#!/usr/bin/env python3
"""Freshness engine + targeted truth refresh (WO-OBSIDIAN-040).

Implements the Freshness Safety Contract:

    remote_head != truth_built_from_head  -> STALE
    GitHub unreachable / no head          -> UNKNOWN
    UNKNOWN                               -> never becomes FRESH
    refresh failed                        -> REFRESH_FAILED
    old verified truth                    -> kept, but marked stale

The refresh is TARGETED: only projects whose HEAD changed get a deep rebuild
(evidence -> truth -> progress -> next-action). Projects whose HEAD is
unchanged are FRESH and skipped (no deep AI analysis, no unnecessary commit).

On refresh failure, the previous good state is RESTORED and freshness.status
is set to refresh_failed with a reason. Partial truth is never published.

Safety:
  * READ-ONLY w.r.t. source repositories (only GitHub GET).
  * Only Vault-generated/knowledge files are mutated.
  * No source repository mutation.

Usage:
    python3 automation/freshness_engine.py probe --all
    python3 automation/freshness_engine.py refresh --all
    python3 automation/freshness_engine.py refresh --project thai_stt_app
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_YAML = REPO_ROOT / "automation" / "projects.yaml"
STATE_DIR = REPO_ROOT / "automation" / "state"
EVIDENCE_DIR = REPO_ROOT / "automation" / "evidence"
SCHEMA_PATH = REPO_ROOT / "automation" / "schema" / "project-state.v2.schema.json"

API_BASE = "https://api.github.com"
REQUEST_TIMEOUT = 25


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_token() -> str | None:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def github_request(path: str, token: str | None) -> tuple[int, dict | list | None, dict]:
    url = f"{API_BASE}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "obsidian-freshness/1.0 (read-only)",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            data = json.loads(body) if body else None
            return resp.status, data, dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, None, {}
    except (urllib.error.URLError, TimeoutError, OSError):
        return -1, None, {"_error": "network"}


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_schema() -> dict:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_owner_repo(repository_url: str) -> tuple[str, str] | None:
    if not repository_url:
        return None
    import re
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", repository_url)
    return (m.group(1), m.group(2)) if m else None


def fetch_remote_head(owner: str, repo: str, token: str | None) -> dict:
    """Fetch the remote HEAD sha for the default branch.

    Returns {"head_sha": str|None, "default_branch": str, "checked_at": str,
    "accessible": bool}. Under the current token scope the commits/branches
    endpoints are blocked, so head_sha may be None (UNKNOWN) -- never FRESH
    by default.
    """
    checked_at = now_iso()
    s, data, _ = github_request(f"/repos/{owner}/{repo}", token)
    if s != 200 or not isinstance(data, dict):
        return {"head_sha": None, "default_branch": None, "checked_at": checked_at,
                "accessible": False, "error": f"repo metadata HTTP {s}"}
    branch = data.get("default_branch") or "main"
    # Try the commits endpoint (may be blocked by token scope).
    s2, cdata, _ = github_request(
        f"/repos/{owner}/{repo}/commits/{urllib.parse.quote(branch)}", token)
    if s2 == 200 and isinstance(cdata, dict):
        return {"head_sha": cdata.get("sha"), "default_branch": branch,
                "checked_at": checked_at, "accessible": True, "error": None}
    # Commits endpoint blocked/unavailable -> head unknown (NOT fresh).
    return {"head_sha": None, "default_branch": branch, "checked_at": checked_at,
            "accessible": True, "error": f"head HTTP {s2} (token scope)"}


# ---------------------------------------------------------------------------
# Freshness classification
# ---------------------------------------------------------------------------

def classify_freshness(truth_built_from_head: str | None, remote_head: str | None,
                       accessible: bool) -> tuple[str, str | None]:
    """Classify SOURCE-level freshness per the safety contract.

    This models only the source HEAD vs. the HEAD the semantic truth was built
    from. It does NOT model semantic/progress freshness (those are gated on
    evidence-collection + identity-rebuild + progress-compute success).

    Returns (status, reason).
    """
    if not accessible:
        return "unknown", "GitHub repo not accessible"
    if remote_head is None:
        # Could not resolve head (token scope / network) -> UNKNOWN, never FRESH.
        return "unknown", "remote head could not be resolved"
    if truth_built_from_head is None:
        # No truth built yet -> stale (needs first build).
        return "stale", "no truth_built_from_head recorded"
    if remote_head != truth_built_from_head:
        return "stale", "remote HEAD changed after last semantic truth build"
    return "fresh", None


def semantic_freshness_for(manifest: dict, candidate_purpose: str | None,
                           existing_purpose: str | None,
                           has_identity_evidence: bool) -> str:
    """Classify SEMANTIC freshness from the evidence manifest + identity rebuild.

    "fresh" ONLY when ALL of:
      * manifest["status"] == "ok" (evidence collection succeeded)
      * identity was rebuilt successfully: candidate purpose is non-null (new
        evidence) OR existing verified identity is preserved (existing purpose
        non-null)
      * has_identity_evidence is true
    Otherwise:
      * "stale" if manifest ok but identity rebuild incomplete
      * "unknown" if manifest status is no_evidence/no_token/repo_not_accessible/
        tree_unavailable/no_remote
      * "refresh_failed" on schema-invalid/exception (caller sets this)
    """
    status = manifest.get("status") if isinstance(manifest, dict) else None
    if status == "ok":
        identity_ok = bool(candidate_purpose) or bool(existing_purpose)
        if identity_ok and has_identity_evidence:
            return "fresh"
        return "stale"
    if status in ("no_evidence", "no_token", "repo_not_accessible",
                  "tree_unavailable", "no_remote"):
        return "unknown"
    # Unknown manifest status or manifest missing -> treat as unknown (safe).
    return "unknown"


def progress_freshness_for(manifest: dict, progress: dict) -> str:
    """Classify PROGRESS freshness from the manifest + computed progress.

    Progress FRESHNESS describes whether the progress computation was rebuilt
    from current evidence -- NOT whether a trustworthy percentage exists
    (that is the progress VALUE, i.e. progress.estimate). A null estimate with
    confidence="unknown" means "we freshly computed progress from current
    evidence, and the result is: no denominator available" -- that is still a
    FRESH computation, just with an unknown value.

    compute_progress never throws (it returns UNKNOWN on failure), so a
    manifest status of "ok" implies the computation ran from current evidence.

      * manifest["status"] != "ok" -> "unknown" (evidence not current)
      * manifest["status"] == "ok" -> "fresh" (computation ran from current
        evidence, regardless of estimate value)
    There is no "stale" case for progress: progress is either
    fresh-from-current-evidence or unknown.
    """
    status = manifest.get("status") if isinstance(manifest, dict) else None
    if status != "ok":
        return "unknown"
    return "fresh"


def _aggregate_freshness(source_f: str, semantic_f: str, progress_f: str) -> str:
    """Aggregate the three sub-gates into a single freshness status.

    Precedence (most severe first):
      * "refresh_failed" if any sub-gate is refresh_failed
      * "unknown" if any sub-gate is unknown
      * "stale" if any sub-gate is stale
      * "fresh" ONLY if all three sub-gates are fresh
    """
    gates = (source_f, semantic_f, progress_f)
    if any(g == "refresh_failed" for g in gates):
        return "refresh_failed"
    if any(g == "unknown" for g in gates):
        return "unknown"
    if any(g == "stale" for g in gates):
        return "stale"
    if all(g == "fresh" for g in gates):
        return "fresh"
    # Defensive: any unexpected value -> unknown (never fresh).
    return "unknown"


def probe_project(project: dict, token: str | None) -> dict:
    """Lightweight freshness probe for one project. Does NOT rebuild truth."""
    pid = project["project_id"]
    state_path = STATE_DIR / f"{pid}.yaml"
    if not state_path.exists():
        return {"project_id": pid, "status": "unknown", "reason": "state_not_found"}
    state = load_yaml(state_path)
    repo_url = project.get("repository") or ""
    owner_repo = parse_owner_repo(repo_url)
    if not owner_repo:
        # Local-only project (no remote) -> freshness unknown (cannot compare).
        # checked_at/default_branch must be present: refresh_project reads
        # probe["checked_at"] unconditionally (KeyError otherwise).
        return {"project_id": pid, "status": "unknown", "reason": "no remote repository",
                "remote_head": None, "default_branch": None, "checked_at": now_iso()}
    owner, repo = owner_repo
    head_info = fetch_remote_head(owner, repo, token)
    fr = state.get("freshness") or {}
    truth_head = fr.get("truth_built_from_head")
    status, reason = classify_freshness(truth_head, head_info["head_sha"],
                                        head_info["accessible"])
    return {
        "project_id": pid,
        "status": status,
        "reason": reason,
        "remote_head": head_info["head_sha"],
        "truth_built_from_head": truth_head,
        "default_branch": head_info["default_branch"],
        "checked_at": head_info["checked_at"],
    }


def probe_all(token: str | None) -> list[dict]:
    registry = load_yaml(PROJECTS_YAML)
    return [probe_project(p, token) for p in registry.get("projects", [])]


# ---------------------------------------------------------------------------
# Targeted refresh (with rollback on failure)
# ---------------------------------------------------------------------------

def _write_state(state_path: Path, state: dict, original_text: str) -> None:
    header_lines = [ln for ln in original_text.splitlines()
                    if ln.startswith("#") or ln.strip() == ""]
    while header_lines and header_lines[-1].strip() == "":
        header_lines.pop()
    body = yaml.safe_dump(state, sort_keys=False, default_flow_style=False,
                          allow_unicode=True, width=1000)
    state_path.write_text("\n".join(header_lines) + "\n" + body, encoding="utf-8")


def _validate_state(state: dict) -> list[str]:
    schema = load_schema()
    return [e.message for e in Draft202012Validator(schema).iter_errors(state)]


def refresh_project(project: dict, token: str | None, dry_run: bool = False) -> dict:
    """Targeted refresh for one project.

    Flow:
      probe -> if FRESH, skip (no deep work).
      if STALE/UNKNOWN:
        backup original state
        -> collect evidence
        -> rebuild truth (identity + execution, drift-aware)
        -> recompute progress + next-action
        -> update freshness (truth_built_from_head, truth_built_at)
        -> schema validate
        -> if any step FAILS: restore backup, set refresh_failed
        -> publish only if all PASS
    """
    pid = project["project_id"]
    state_path = STATE_DIR / f"{pid}.yaml"
    if not state_path.exists():
        return {"project_id": pid, "published": False, "reason": "state_not_found"}

    original_text = state_path.read_text(encoding="utf-8")
    original_state = yaml.safe_load(original_text)

    # 1. Probe.
    probe = probe_project(project, token)
    status = probe["status"]

    if status == "fresh":
        # No deep refresh. Update source_checked_at only (lightweight).
        # Re-assert sub-gates from EXISTING state: source is fresh, but the
        # aggregate must NOT be fresh unless the existing semantic/progress
        # sub-gates are also fresh (Freshness Safety Contract, F2).
        state = dict(original_state)
        fr = dict(state.get("freshness") or {})
        fr["source_checked_at"] = probe["checked_at"]
        fr["remote_head"] = probe["remote_head"]
        fr["reason"] = None
        fr["stale_since"] = None
        fr["source_freshness"] = "fresh"
        existing_semantic = fr.get("semantic_freshness") or "unknown"
        existing_progress = fr.get("progress_freshness") or "unknown"
        fr["semantic_freshness"] = existing_semantic
        fr["progress_freshness"] = existing_progress
        fr["status"] = _aggregate_freshness("fresh", existing_semantic, existing_progress)
        state["freshness"] = fr
        # Validate before writing (consistent with deep-refresh path).
        errors = _validate_state(state)
        if errors:
            if not dry_run:
                state_path.write_text(original_text, encoding="utf-8")
            failed_state = yaml.safe_load(original_text)
            ffr = failed_state.get("freshness") or {}
            ffr["status"] = "refresh_failed"
            ffr["reason"] = f"schema invalid (fresh path): {errors[:2]}"
            failed_state["freshness"] = ffr
            if not dry_run:
                _write_state(state_path, failed_state, original_text)
            return {"project_id": pid, "published": False, "status": "refresh_failed",
                    "reason": "schema invalid (fresh path)", "restored": True}
        if not dry_run:
            _write_state(state_path, state, original_text)
        return {"project_id": pid, "published": not dry_run,
                "status": fr["status"], "deep_refresh": False,
                "reason": "HEAD unchanged"}

    # 2. STALE or UNKNOWN -> attempt deep refresh.
    # Import the truth builder + progress engine lazily (guard against
    # duplicate sys.path entries on repeated calls).
    for _p in (str(REPO_ROOT), str(REPO_ROOT / "automation")):
        if _p not in sys.path:
            sys.path.insert(0, _p)
    import evidence_collector as ev
    import progress_engine as pe

    try:
        # Backup is the original_text (already captured).
        # 2a. Collect evidence.
        manifest = ev.collect_evidence_for_project(project, token)
        # 2b. Build a working copy of the state.
        working = yaml.safe_load(original_text)  # fresh deep copy
        # 2c. Apply truth (identity + execution, drift-aware). We reuse the
        # evidence_collector's builder functions directly (single source of
        # truth for drift logic) rather than duplicating it.
        candidate_identity = ev.build_identity_from_evidence(manifest)
        candidate_execution = ev.build_execution_from_evidence(manifest)
        existing_identity = working.get("project_identity") or {}
        existing_purpose = existing_identity.get("purpose")
        new_identity = dict(existing_identity)
        # Reset drift fields each cycle (a prior drift may have been resolved).
        new_identity["identity_drift_detected"] = False
        new_identity["previous_identity"] = None
        new_identity["candidate_identity"] = None
        new_identity["candidate_identity_provenance"] = None
        drift = False
        if existing_purpose and candidate_identity["purpose"]:
            ep = existing_purpose.strip().lower()
            cp = candidate_identity["purpose"].strip().lower()
            same = ep == cp or ep in cp or cp in ep
            if not same:
                # Mission drift: preserve old identity, record candidate +
                # provenance (F4). Do NOT overwrite the existing purpose.
                drift = True
                new_identity["identity_drift_detected"] = True
                new_identity["previous_identity"] = [dict(existing_identity)]
                new_identity["candidate_identity"] = {"purpose": candidate_identity["purpose"]}
                cand_ev, _ = ev._select_purpose_evidence(manifest)
                if cand_ev is not None:
                    new_identity["candidate_identity_provenance"] = {
                        "path": cand_ev.get("path"),
                        "ref": cand_ev.get("ref"),
                        "blob_sha": cand_ev.get("blob_sha"),
                        "observed_at": cand_ev.get("observed_at"),
                    }
        elif not existing_purpose and candidate_identity["purpose"]:
            new_identity = dict(candidate_identity)
            new_identity["identity_drift_detected"] = False
            new_identity["previous_identity"] = None
            new_identity["candidate_identity"] = None
            new_identity["candidate_identity_provenance"] = None
        working["project_identity"] = new_identity
        if candidate_execution["current_work"] is not None:
            existing_exec = working.get("current_execution") or {}
            merged_exec = dict(existing_exec)
            for k, v in candidate_execution.items():
                if v is not None:
                    merged_exec[k] = v
            working["current_execution"] = merged_exec
        # F1: knowledge_state=verified requires an explicit purpose (not just
        # any heading). A bare project title/heading must NOT verify the Mission.
        has_identity_evidence = candidate_identity["purpose"] is not None
        if has_identity_evidence:
            working["knowledge_state"] = "verified"
        working["verified_at"] = manifest.get("observed_at")
        working["adapter_id"] = "freshness-refresh-v1"

        # 2d. Recompute progress + next-action.
        progress = pe.compute_progress(manifest, working)
        next_action = pe.derive_next_action(manifest, working)
        working["progress"] = progress
        exec_block = working.get("current_execution") or {}
        exec_block["next_action"] = next_action
        working["current_execution"] = exec_block

        # 2e. Compute the three sub-gates (F2: False Freshness / Partial Truth).
        remote_head = probe.get("remote_head")
        accessible = probe.get("status") != "unknown" or remote_head is not None
        # Source freshness is derived from classify_freshness (source-level).
        source_f, _ = classify_freshness(
            (working.get("freshness") or {}).get("truth_built_from_head"),
            remote_head, accessible)
        # If the remote head is known, source is fresh relative to the rebuilt
        # truth (we bind truth_built_from_head to it below); otherwise classify
        # already returned unknown/stale.
        if remote_head:
            source_f = "fresh"
        semantic_f = semantic_freshness_for(
            manifest, candidate_identity["purpose"], existing_purpose,
            has_identity_evidence)
        progress_f = progress_freshness_for(manifest, progress)
        aggregate = _aggregate_freshness(source_f, semantic_f, progress_f)

        # 2f. Publication gate (F2): if evidence collection did not succeed,
        # do NOT publish the rebuilt truth as fresh. Roll back to the original
        # state, preserving the previous verified identity + truth_built_from_head.
        if manifest.get("status") != "ok":
            if not dry_run:
                state_path.write_text(original_text, encoding="utf-8")
            failed_state = yaml.safe_load(original_text)
            ffr = dict(failed_state.get("freshness") or {})
            ffr["source_checked_at"] = probe["checked_at"]
            ffr["remote_head"] = remote_head
            ffr["tracked_ref"] = probe.get("default_branch") or ffr.get("tracked_ref")
            # Preserve previous verified identity + truth_built_from_head
            # (do NOT overwrite with null or with remote_head).
            ffr["source_freshness"] = source_f
            ffr["semantic_freshness"] = "unknown"
            ffr["progress_freshness"] = "unknown"
            ffr["status"] = "unknown"
            ffr["reason"] = f"evidence unavailable: manifest status={manifest.get('status')}"
            failed_state["freshness"] = ffr
            if not dry_run:
                _write_state(state_path, failed_state, original_text)
            return {"project_id": pid, "published": False, "status": "unknown",
                    "deep_refresh": True, "restored": True,
                    "reason": f"evidence unavailable: manifest status={manifest.get('status')}",
                    "manifest_status": manifest.get("status")}

        # 2g. Evidence OK -> bind truth to remote head (if known) and publish
        # the aggregate status. Aggregate is fresh ONLY if all three sub-gates
        # are fresh.
        fr = working.get("freshness") or {}
        fr["source_checked_at"] = probe["checked_at"]
        fr["remote_head"] = remote_head
        fr["tracked_ref"] = probe.get("default_branch") or fr.get("tracked_ref")
        if remote_head:
            fr["truth_built_from_head"] = remote_head
            fr["truth_built_at"] = now_iso()
            working["head"] = remote_head
        fr["source_freshness"] = source_f
        fr["semantic_freshness"] = semantic_f
        fr["progress_freshness"] = progress_f
        fr["status"] = aggregate
        fr["reason"] = None if aggregate == "fresh" else (
            f"sub-gates: source={source_f} semantic={semantic_f} progress={progress_f}")
        fr["stale_since"] = None if aggregate == "fresh" else fr.get("stale_since")
        working["freshness"] = fr

        # 2h. Schema validate.
        errors = _validate_state(working)
        if errors:
            # Restore original; mark refresh_failed. Preserve the original
            # verified identity (do NOT null it).
            if not dry_run:
                state_path.write_text(original_text, encoding="utf-8")
            failed_state = yaml.safe_load(original_text)
            ffr = dict(failed_state.get("freshness") or {})
            ffr["status"] = "refresh_failed"
            ffr["reason"] = f"schema invalid: {errors[:2]}"
            ffr["source_checked_at"] = probe["checked_at"]
            ffr["source_freshness"] = source_f
            ffr["semantic_freshness"] = "refresh_failed"
            ffr["progress_freshness"] = "refresh_failed"
            failed_state["freshness"] = ffr
            if not dry_run:
                _write_state(state_path, failed_state, original_text)
            return {"project_id": pid, "published": False, "status": "refresh_failed",
                    "reason": f"schema invalid", "errors": errors[:3], "restored": True}

        # 2i. Publish (only if all PASS).
        if not dry_run:
            _write_state(state_path, working, original_text)
        return {
            "project_id": pid,
            "published": not dry_run,
            "status": working["freshness"]["status"],
            "deep_refresh": True,
            "drift": drift,
            "evidence_items": len(manifest.get("evidence", [])),
            "progress_estimate": progress["estimate"],
            "next_action": next_action,
        }
    except Exception as exc:  # noqa: BLE001
        # Restore original good state; mark refresh_failed. Preserve the
        # original verified identity (do NOT null it).
        if not dry_run:
            state_path.write_text(original_text, encoding="utf-8")
        try:
            failed_state = yaml.safe_load(original_text)
            ffr = dict(failed_state.get("freshness") or {})
            ffr["status"] = "refresh_failed"
            ffr["reason"] = f"exception: {type(exc).__name__}: {exc}"[:200]
            ffr["source_checked_at"] = now_iso()
            ffr["source_freshness"] = ffr.get("source_freshness") or "unknown"
            ffr["semantic_freshness"] = "refresh_failed"
            ffr["progress_freshness"] = "refresh_failed"
            failed_state["freshness"] = ffr
            if not dry_run:
                _write_state(state_path, failed_state, original_text)
        except Exception:
            pass
        return {"project_id": pid, "published": False, "status": "refresh_failed",
                "reason": f"exception: {type(exc).__name__}", "restored": True}


def refresh_all(token: str | None, dry_run: bool = False) -> list[dict]:
    registry = load_yaml(PROJECTS_YAML)
    return [refresh_project(p, token, dry_run=dry_run) for p in registry.get("projects", [])]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_probe(token: str | None, project_id: str | None, all_projects: bool) -> int:
    print("WO-OBSIDIAN-040 -- Freshness probe (lightweight, read-only)")
    print("=" * 70)
    if project_id:
        registry = load_yaml(PROJECTS_YAML)
        proj = next((p for p in registry.get("projects", []) if p["project_id"] == project_id), None)
        if not proj:
            print(f"unknown project: {project_id}")
            return 1
        res = [probe_project(proj, token)]
    else:
        res = probe_all(token)
    counts = {"fresh": 0, "stale": 0, "unknown": 0, "refresh_failed": 0}
    for r in res:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        rh = r.get("remote_head")
        th = r.get("truth_built_from_head")
        print(f"  {r['project_id']}: {r['status'].upper()} "
              f"(remote={rh or 'n/a'} truth={th or 'n/a'}) {r.get('reason') or ''}")
    print(f"\nSummary: fresh={counts['fresh']} stale={counts['stale']} "
          f"unknown={counts['unknown']} refresh_failed={counts['refresh_failed']}")
    return 0


def cmd_refresh(token: str | None, project_id: str | None, all_projects: bool, dry_run: bool) -> int:
    print(f"WO-OBSIDIAN-040 -- Targeted truth refresh ({'DRY-RUN' if dry_run else 'APPLY'})")
    print("=" * 70)
    if project_id:
        registry = load_yaml(PROJECTS_YAML)
        proj = next((p for p in registry.get("projects", []) if p["project_id"] == project_id), None)
        if not proj:
            print(f"unknown project: {project_id}")
            return 1
        res = [refresh_project(proj, token, dry_run=dry_run)]
    else:
        res = refresh_all(token, dry_run=dry_run)
    published = sum(1 for r in res if r.get("published"))
    deep = sum(1 for r in res if r.get("deep_refresh"))
    failed = sum(1 for r in res if r.get("status") == "refresh_failed")
    for r in res:
        print(f"  {r['project_id']}: status={r.get('status')} "
              f"deep={r.get('deep_refresh')} published={r.get('published')} "
              f"reason={r.get('reason') or ''}")
    print(f"\nSummary: published={published} deep_refreshes={deep} failed={failed}")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Freshness engine (WO-040)")
    sub = parser.add_subparsers(dest="cmd")
    p_p = sub.add_parser("probe", help="lightweight freshness probe")
    p_p.add_argument("--project", help="single project_id")
    p_p.add_argument("--all", action="store_true")
    p_r = sub.add_parser("refresh", help="targeted truth refresh")
    p_r.add_argument("--project", help="single project_id")
    p_r.add_argument("--all", action="store_true")
    p_r.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv[1:])
    token = resolve_token()
    if args.cmd == "probe":
        return cmd_probe(token, args.project, args.all)
    if args.cmd == "refresh":
        return cmd_refresh(token, args.project, args.all, args.dry_run)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
