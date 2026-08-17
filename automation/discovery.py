#!/usr/bin/env python3
"""Read-only GitHub repository discovery + safe auto-onboarding (WO-OBSIDIAN-037).

Reads the GitHub REST API (GET only) to inventory repositories owned by a
target account, compares them against the Vault project registry using the
STABLE numeric `github_repository_id` (not the name, so renames are detected),
and safely onboards eligible new repositories.

Safety contract (enforced unconditionally):
  * READ-ONLY -- only GET requests; never mutates a source repository.
  * Default inclusion/exclusion policy:
      - EXCLUDE archived repositories
      - EXCLUDE forks
      - EXCLUDE an explicit denylist (e.g. the Vault repo itself)
      - EXCLUDE repositories that cannot be read (inaccessible) -- never guess
  * Onboarding is idempotent: re-running never creates a duplicate project.
    Matching is by stable github_repository_id first, then by repository URL.
  * When evidence is insufficient to identify a project's Mission, the project
    is onboarded with knowledge_state=needs-verification and identity fields
    set to null (unknown). The Mission is NEVER fabricated.
  * GitHub unreachable -> discovery reports UNKNOWN for every repo; no
    onboarding happens (fail-safe).

Discovery flow (per the WO-037 contract):
    DISCOVERED
    -> evidence scan (read repo metadata + candidate authority files)
    -> identity extraction (conservative; null when insufficient)
    -> normalized state (v2)
    -> Project Overview (markdown)
    -> Project Registry (append)
    -> projects.yaml (append, enabled_for_wall)
    -> Dashboard (rendered by the renderer)

This module provides:
  * discover_repos()        -- inventory + classify (new/renamed/archived/inaccessible)
  * reconcile_registry()   -- compare discovery vs registry by stable id
  * onboard_project()      -- create state + registry + overview for one repo
  * main()                  -- CLI: discover / reconcile / onboard / list

Usage:
    python3 automation/discovery.py discover      # inventory GitHub (read-only)
    python3 automation/discovery.py reconcile     # compare vs registry
    python3 automation/discovery.py onboard --dry-run   # propose onboarding
    python3 automation/discovery.py onboard        # onboard eligible new repos
"""

from __future__ import annotations

import argparse
import json
import os
import re
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
SCHEMA_PATH = REPO_ROOT / "automation" / "schema" / "project-state.v2.schema.json"
REGISTRY_MD = REPO_ROOT / "01 Projects" / "Project Registry.md"
PROJECTS_DIR = REPO_ROOT / "01 Projects"
DASHBOARD = REPO_ROOT / "00 Dashboard" / "Project Dashboard.md"

API_BASE = "https://api.github.com"
REQUEST_TIMEOUT = 20
ALLOWED_METHOD = "GET"

# Default policy: exclude archived, forks, and an explicit denylist.
# The Vault repo itself (Obsidian) is denied because it is the knowledge
# layer, not a tracked source project.
DEFAULT_DENYLIST_NAMES = {"Obsidian"}
DEFAULT_EXCLUDE_ARCHIVED = True
DEFAULT_EXCLUDE_FORKS = True


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_token() -> str | None:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def github_request(path: str, token: str | None) -> tuple[int, dict | list | None, dict]:
    """Read-only GET to api.github.com. Returns (status, json, headers)."""
    url = f"{API_BASE}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "obsidian-discovery/1.0 (read-only)",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method=ALLOWED_METHOD)
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            data = json.loads(body) if body else None
            return resp.status, data, dict(resp.headers)
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        data = None
        try:
            data = json.loads(body) if body else None
        except Exception:
            data = None
        return e.code, data, dict(e.headers) if hasattr(e, "headers") else {}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return -1, None, {"_error": str(e)}


def parse_owner_repo(repository_url: str) -> tuple[str, str] | None:
    if not repository_url:
        return None
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", repository_url)
    if not m:
        return None
    return m.group(1), m.group(2)


def load_projects_registry() -> dict:
    with open(PROJECTS_YAML, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_schema() -> dict:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def registry_index(registry: dict) -> dict:
    """Build a lookup index of the registry by stable id and by URL/name."""
    by_id: dict[int, dict] = {}
    by_url: dict[str, dict] = {}
    by_name: dict[str, dict] = {}
    for p in registry.get("projects", []):
        if p.get("github_repository_id") is not None:
            by_id[p["github_repository_id"]] = p
        url = (p.get("repository") or "").lower()
        if url:
            by_url[url] = p
        nm = (p.get("repository") or "")
        m = parse_owner_repo(nm)
        if m:
            by_name[m[1].lower()] = p
    return {"by_id": by_id, "by_url": by_url, "by_name": by_name}


def discover_repos(
    account: str = "expellirmud-dot",
    token: str | None = None,
    exclude_archived: bool = DEFAULT_EXCLUDE_ARCHIVED,
    exclude_forks: bool = DEFAULT_EXCLUDE_FORKS,
    denylist: set[str] | None = None,
) -> dict:
    """Inventory repositories for an account (read-only). Returns a report.

    The report has:
      * repos: list of repo dicts (id, name, full_name, archived, fork,
        default_branch, private, pushed_at, html_url)
      * status: 'ok' | 'unavailable' | 'no_token'
      * error: reason when unavailable
    Excluded repos (archived/fork/denylist) are still returned but flagged
    `excluded=True` with an `exclusion_reason` so callers can audit policy.
    """
    denylist = denylist if denylist is not None else set(DEFAULT_DENYLIST_NAMES)
    if not token:
        return {"status": "no_token", "repos": [], "error": "no GITHUB_TOKEN"}

    # Use the authenticated owner endpoint so private repos are included.
    # Fall back to the public /users/{account}/repos endpoint if needed.
    repos: list[dict] = []
    for page in (1, 2, 3):
        path = f"/user/repos?affiliation=owner&per_page=100&page={page}"
        status, data, _ = github_request(path, token)
        if status == -1:
            return {"status": "unavailable", "repos": [], "error": "github_api_unavailable"}
        if status == 401 or status == 403:
            # Token may lack scope for /user/repos; fall back to public endpoint.
            break
        if status != 200 or not isinstance(data, list):
            break
        if not data:
            break
        repos.extend(data)
    # Filter to only the target account's owned repos (affiliation=owner can
    # include orgs the user owns). Keep only full_name starting with account.
    repos = [r for r in repos if str(r.get("full_name", "")).startswith(f"{account}/")]

    if not repos:
        # Fallback: public endpoint.
        for page in (1, 2, 3):
            path = f"/users/{account}/repos?per_page=100&page={page}&type=owner"
            status, data, _ = github_request(path, token)
            if status == -1:
                return {"status": "unavailable", "repos": [], "error": "github_api_unavailable"}
            if status != 200 or not isinstance(data, list):
                break
            if not data:
                break
            repos.extend(data)
        repos = [r for r in repos if str(r.get("full_name", "")).startswith(f"{account}/")]

    out: list[dict] = []
    for r in repos:
        excluded = False
        reason = None
        if exclude_archived and r.get("archived"):
            excluded = True
            reason = "archived"
        elif exclude_forks and r.get("fork"):
            excluded = True
            reason = "fork"
        elif r.get("name") in denylist:
            excluded = True
            reason = "denylist"
        out.append(
            {
                "id": r.get("id"),
                "name": r.get("name"),
                "full_name": r.get("full_name"),
                "archived": bool(r.get("archived")),
                "fork": bool(r.get("fork")),
                "default_branch": r.get("default_branch"),
                "private": bool(r.get("private")),
                "pushed_at": r.get("pushed_at"),
                "html_url": r.get("html_url"),
                "excluded": excluded,
                "exclusion_reason": reason,
            }
        )
    return {"status": "ok", "repos": out, "error": None}


def reconcile_registry(discovery: dict, registry: dict) -> dict:
    """Compare discovery vs registry by stable id. Classify each repo.

    Returns a report with:
      * new: repos not in registry (eligible candidates)
      * renamed: repos whose stable id IS in registry but whose name differs
      * known: repos whose stable id and name match the registry
      * archived_in_registry: registry entries whose remote is now archived
      * inaccessible: registry entries whose remote could not be read
    """
    idx = registry_index(registry)
    by_id = idx["by_id"]
    by_name = idx["by_name"]

    new: list[dict] = []
    renamed: list[dict] = []
    known: list[dict] = []
    discovered_ids: set[int] = set()
    matched_registry_ids: set[str] = set()

    for r in discovery.get("repos", []):
        rid = r.get("id")
        if rid is not None:
            discovered_ids.add(rid)
        reg = by_id.get(rid) if rid is not None else None
        if reg is None:
            # Try name match (repo may be registered by URL/name without id).
            reg = by_name.get((r.get("name") or "").lower())
        if reg is None:
            if not r.get("excluded"):
                new.append(r)
            continue
        matched_registry_ids.add(reg.get("project_id"))
        # Found in registry by id (or name). Check rename.
        reg_repo_url = reg.get("repository") or ""
        m = parse_owner_repo(reg_repo_url)
        reg_name = (m[1] if m else "").lower()
        if reg_name and reg_name != (r.get("name") or "").lower():
            renamed.append({"discovered": r, "registered": reg})
        else:
            known.append({"discovered": r, "registered": reg})

    # Detect registry entries whose remote was not in discovery (archived/
    # inaccessible/renamed-away). A registry entry matched by name above is
    # NOT inaccessible. Local-only projects (no remote) are skipped.
    # When we can read a tracked repo's metadata and it is archived, classify
    # it as archived_in_registry rather than inaccessible.
    archived_in_registry: list[dict] = []
    inaccessible: list[dict] = []
    # Build a set of discovered ids that were archived (so a tracked repo
    # present in discovery but archived is reported as archived, not known).
    discovered_archived_ids = {
        r.get("id") for r in discovery.get("repos", []) if r.get("archived")
    }
    for p in registry.get("projects", []):
        url = p.get("repository") or ""
        if not url:
            continue  # local-only project (e.g. Adobe Stock) -- not inaccessible
        if p.get("project_id") in matched_registry_ids:
            # Matched in discovery. If the discovered repo is archived, flag it.
            rid = p.get("github_repository_id")
            if rid in discovered_archived_ids:
                archived_in_registry.append(p)
            continue  # otherwise matched -> not inaccessible
        rid = p.get("github_repository_id")
        if rid in discovered_ids:
            continue  # seen in discovery (matched by id)
        # Not seen: could be archived, renamed, or inaccessible.
        inaccessible.append(p)

    return {
        "new": new,
        "renamed": renamed,
        "known": known,
        "archived_in_registry": archived_in_registry,
        "inaccessible": inaccessible,
    }


def _slug(project_name: str) -> str:
    """Make a filesystem-safe project_id from a repo name."""
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", project_name or "unknown")
    s = re.sub(r"-+", "-", s).strip("-_.")
    return s or "unknown"


def _default_state_v2(
    project_id: str,
    project_name: str,
    github_repository_id: int | None,
    repository: str,
    default_branch: str | None,
    head_sha: str | None,
    last_change: str | None,
    observed_at: str,
) -> dict:
    """Build a conservative v2 state for a newly onboarded project.

    Identity fields default to null (unknown) -- the Mission is NOT
    fabricated. knowledge_state=needs-verification. The evidence collector
    (WO-038) fills identity later from real file content.
    """
    return {
        "schema_version": 2,
        "project_id": project_id,
        "project_name": project_name,
        "github_repository_id": github_repository_id,
        "source_path": None,  # GitHub-only project; no local path required
        "repository": repository,
        "branch": default_branch,
        "head": head_sha,
        "knowledge_state": "needs-verification",
        "project_identity": {
            "purpose": None,
            "problem_statement": None,
            "intended_outcome": None,
            "primary_users": None,
            "success_definition": None,
            "scope": None,
            "non_goals": None,
            "identity_drift_detected": False,
            "previous_identity": None,
        },
        "current_execution": {
            "lifecycle_phase": None,
            "current_goal": None,
            "current_work": None,
            "current_work_authority": {"path": None, "kind": None},
            "current_work_evidence": "unknown",
            "last_completed": None,
            "blockers": None,
            "next_action": None,
        },
        "freshness": {
            "status": "fresh" if head_sha else "unknown",
            "tracked_ref": default_branch,
            "remote_head": head_sha,
            "truth_built_from_head": head_sha,
            "source_checked_at": observed_at,
            "truth_built_at": observed_at if head_sha else None,
            "stale_since": None,
            "reason": None if head_sha else "no head sha resolved at onboarding",
            "source_freshness": "fresh" if head_sha else "unknown",
            "semantic_freshness": "fresh" if head_sha else "unknown",
            "progress_freshness": "fresh" if head_sha else "unknown",
        },
        "progress": {
            "scope": None,
            "method": None,
            "estimate": None,
            "range_min": None,
            "range_max": None,
            "confidence": "unknown",
            "completed": None,
            "active": None,
            "remaining": None,
            "basis": None,
        },
        "github": {
            "ci_state": "unknown",
            "open_pr": None,
            "open_pr_count": None,
            "observed_at": observed_at,
        },
        "last_change": last_change,
        "evidence_classification": "unknown",
        "verified_at": observed_at,
        "adapter_id": "discovery-onboard-v1",
    }


def fetch_repo_head_sha(owner: str, repo: str, token: str | None) -> dict:
    """Fetch the default-branch HEAD sha + last_change for a repo (read-only)."""
    s, data, _ = github_request(f"/repos/{owner}/{repo}", token)
    if s != 200 or not isinstance(data, dict):
        return {"error": "repo_not_accessible"}
    default_branch = data.get("default_branch") or "main"
    s2, cdata, _ = github_request(
        f"/repos/{owner}/{repo}/commits/{urllib.parse.quote(default_branch)}", token
    )
    if s2 != 200 or not isinstance(cdata, dict):
        return {"error": "head_not_found", "default_branch": default_branch}
    sha = cdata.get("sha")
    commit = cdata.get("commit") or {}
    date_raw = (commit.get("commit") or {}).get("committer", {}).get("date") or \
        commit.get("committer", {}).get("date")
    last_change = None
    if date_raw:
        try:
            last_change = datetime.fromisoformat(
                date_raw.replace("Z", "+00:00")
            ).strftime("%Y-%m-%d")
        except ValueError:
            last_change = date_raw[:10]
    return {"default_branch": default_branch, "head_sha": sha, "last_change": last_change}


def onboard_project(
    repo: dict,
    token: str | None,
    dry_run: bool = True,
) -> dict:
    """Onboard a single discovered repo into the Vault (idempotent).

    Creates:
      * automation/state/<project_id>.yaml (v2 state, needs-verification)
      * appends to automation/projects.yaml (enabled_for_wall: true)
      * 01 Projects/<project_name>.md (Project Overview stub)

    Returns a report dict with project_id, created (bool), and path.
    Idempotent: if the project_id already exists, returns created=False.
    """
    name = repo.get("name") or "unknown"
    rid = repo.get("id")
    full = repo.get("full_name") or f"expellirmud-dot/{name}"
    html_url = repo.get("html_url") or f"https://github.com/{full}"
    repository = f"{html_url}.git" if html_url else None
    project_id = _slug(name)
    project_name = name.replace("-", " ").replace("_", " ").title() or name

    state_path = STATE_DIR / f"{project_id}.yaml"
    overview_path = PROJECTS_DIR / f"{project_name}.md"
    if state_path.exists():
        return {"project_id": project_id, "created": False, "reason": "state_exists"}

    # Resolve head sha (read-only). Failure -> unknown freshness, not a crash.
    owner_repo = parse_owner_repo(repository) if repository else None
    head_info = {"error": "no_remote"}
    if owner_repo and token:
        head_info = fetch_repo_head_sha(owner_repo[0], owner_repo[1], token)
    head_sha = head_info.get("head_sha") if "error" not in head_info else None
    default_branch = head_info.get("default_branch") or repo.get("default_branch")
    last_change = head_info.get("last_change")
    observed_at = now_iso()

    state = _default_state_v2(
        project_id, project_name, rid, repository, default_branch,
        head_sha, last_change, observed_at,
    )

    # Validate before writing.
    schema = load_schema()
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(state))
    if errors:
        return {
            "project_id": project_id,
            "created": False,
            "reason": "schema_invalid",
            "errors": [e.message for e in errors],
        }

    overview = _overview_stub(project_id, project_name, repository, rid, observed_at)

    if dry_run:
        return {
            "project_id": project_id,
            "project_name": project_name,
            "created": True,
            "dry_run": True,
            "state_path": str(state_path),
            "overview_path": str(overview_path),
            "head_sha": head_sha,
            "knowledge_state": "needs-verification",
        }

    # Write state file.
    header = (
        f"# Normalized project state (v2) -- {project_id}\n"
        f"# Onboarded by WO-OBSIDIAN-037 (Repository Discovery + Safe Auto-Onboarding).\n"
        f"# Source repository is READ-ONLY; no source files were modified.\n"
        f"# knowledge_state=needs-verification: Mission not yet verified against source evidence.\n"
    )
    body = yaml.safe_dump(
        state, sort_keys=False, default_flow_style=False, allow_unicode=True, width=1000
    )
    state_path.write_text(header + body, encoding="utf-8")

    # Append to projects.yaml.
    registry = load_projects_registry()
    entry = {
        "project_id": project_id,
        "project_name": project_name,
        "source_path": None,
        "repository": repository,
        "github_repository_id": rid,
        "enabled_for_wall": True,
        "pilot_status": "discovered",
        "adapter_id": "discovery-onboard-v1",
        "authority_candidates": ["AGENTS.md", "README.md", "PROJECT_RULES.md"],
    }
    registry.setdefault("projects", []).append(entry)
    with open(PROJECTS_YAML, "w", encoding="utf-8") as f:
        f.write(
            yaml.safe_dump(
                registry, sort_keys=False, default_flow_style=False,
                allow_unicode=True, width=1000,
            )
        )

    # Write Project Overview stub.
    overview_path.write_text(overview, encoding="utf-8")

    return {
        "project_id": project_id,
        "project_name": project_name,
        "created": True,
        "dry_run": False,
        "state_path": str(state_path),
        "overview_path": str(overview_path),
        "head_sha": head_sha,
        "knowledge_state": "needs-verification",
    }


def _overview_stub(
    project_id: str, project_name: str, repository: str,
    github_repository_id: int | None, observed_at: str,
) -> str:
    return f"""---
type: project-overview
last_reviewed: {observed_at[:10]}
---

# {project_name}

> Onboarded by WO-OBSIDIAN-037 (Repository Discovery + Safe Auto-Onboarding).
> knowledge_state: **needs-verification** -- Project Mission not yet verified against source evidence.

## โปรเจกต์นี้คืออะไร

unknown -- ยังไม่มีหลักฐานเพียงพอระบุ Mission จาก source repository

## ปัญหาที่ต้องการแก้

unknown

## เป้าหมายหลัก

unknown

## ขอบเขต

unknown

## ตำแหน่งไฟล์จริง

GitHub-only project (no local source_path required).

## Repository

- URL: {repository or 'null'}
- github_repository_id: {github_repository_id}

## สถานะปัจจุบัน

needs-verification -- ต้อง verify กับ source evidence (WO-OBSIDIAN-038)

## สิ่งที่ทำเสร็จแล้ว

unknown

## งานที่กำลังทำ

unknown

## งานถัดไป

Verify Project Mission against source repository evidence (WO-OBSIDIAN-038).

## สถาปัตยกรรม

unknown

## การตัดสินใจสำคัญ

- Onboarded automatically by discovery layer with knowledge_state=needs-verification (no Mission fabrication).

## Resume Context

อ่าน `automation/state/{project_id}.yaml` สำหรับ normalized state

## วันที่ตรวจสอบล่าสุด

{observed_at[:10]}
"""


def cmd_discover(token: str | None) -> int:
    print("WO-OBSIDIAN-037 -- Repository Discovery (read-only)")
    print("=" * 70)
    if not token:
        print("WARNING: no GITHUB_TOKEN; discovery unavailable (fail-safe).")
        return 0
    report = discover_repos(token=token)
    if report["status"] != "ok":
        print(f"discovery status: {report['status']} ({report['error']})")
        return 1
    repos = report["repos"]
    print(f"discovered {len(repos)} repositories")
    eligible = [r for r in repos if not r.get("excluded")]
    excluded = [r for r in repos if r.get("excluded")]
    print(f"eligible (not excluded): {len(eligible)}")
    print(f"excluded: {len(excluded)}")
    print("\n--- all repos ---")
    print(f"{'id':<14} {'name':<32} {'archived':<9} {'fork':<6} {'excluded':<9} reason")
    for r in sorted(repos, key=lambda x: x.get("name") or ""):
        print(
            f"{str(r.get('id')):<14} {(r.get('name') or ''):<32} "
            f"{str(r.get('archived')):<9} {str(r.get('fork')):<6} "
            f"{str(r.get('excluded')):<9} {r.get('exclusion_reason') or ''}"
        )
    return 0


def cmd_reconcile(token: str | None) -> int:
    print("WO-OBSIDIAN-037 -- Reconcile discovery vs registry (by stable id)")
    print("=" * 70)
    registry = load_projects_registry()
    if not token:
        print("WARNING: no GITHUB_TOKEN; cannot probe GitHub. Reporting registry only.")
        # Still report registry entries missing github_repository_id.
        missing_id = [p for p in registry.get("projects", []) if p.get("github_repository_id") is None and (p.get("repository"))]
        print(f"registry entries with a remote but no github_repository_id: {len(missing_id)}")
        for p in missing_id:
            print(f"  - {p['project_id']}: {p.get('repository')}")
        return 0
    discovery = discover_repos(token=token)
    if discovery["status"] != "ok":
        print(f"discovery unavailable: {discovery['error']}")
        return 1
    rec = reconcile_registry(discovery, registry)
    print(f"new (eligible, not in registry): {len(rec['new'])}")
    for r in rec["new"]:
        print(f"  + {r.get('name')} (id={r.get('id')})")
    print(f"renamed (stable id in registry, name differs): {len(rec['renamed'])}")
    for r in rec["renamed"]:
        print(
            f"  ~ {r['discovered'].get('name')} (id={r['discovered'].get('id')}) "
            f"<- registered as {r['registered'].get('project_id')}"
        )
    print(f"known (id+name match): {len(rec['known'])}")
    print(f"inaccessible (in registry, not seen in discovery): {len(rec['inaccessible'])}")
    for p in rec["inaccessible"]:
        print(f"  ? {p.get('project_id')}: {p.get('repository')}")
    return 0


def cmd_onboard(token: str | None, dry_run: bool) -> int:
    mode = "DRY-RUN" if dry_run else "ONBOARD"
    print(f"WO-OBSIDIAN-037 -- Safe Auto-Onboarding ({mode})")
    print("=" * 70)
    if not token:
        print("WARNING: no GITHUB_TOKEN; cannot discover. No onboarding.")
        return 0
    registry = load_projects_registry()
    discovery = discover_repos(token=token)
    if discovery["status"] != "ok":
        print(f"discovery unavailable: {discovery['error']}")
        return 1
    rec = reconcile_registry(discovery, registry)
    new = rec["new"]
    print(f"eligible new repos to onboard: {len(new)}")
    if not new:
        print("NO-OP: no new eligible repos. (No empty commit.)")
        return 0
    results = []
    for r in new:
        res = onboard_project(r, token, dry_run=dry_run)
        results.append(res)
        if res.get("created"):
            print(f"  + {res['project_id']} (head={res.get('head_sha')}) "
                  f"knowledge_state={res.get('knowledge_state')}")
        else:
            print(f"  = {res['project_id']} skipped ({res.get('reason')})")
    created = [r for r in results if r.get("created")]
    print(f"\nonboarded: {len(created)} (dry_run={dry_run})")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Repository discovery + onboarding (WO-037)")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("discover", help="inventory GitHub (read-only)")
    sub.add_parser("reconcile", help="compare discovery vs registry by stable id")
    p_on = sub.add_parser("onboard", help="onboard eligible new repos")
    p_on.add_argument("--dry-run", action="store_true", help="propose only, do not write")
    args = parser.parse_args(argv[1:])

    token = resolve_token()
    if args.cmd == "discover":
        return cmd_discover(token)
    if args.cmd == "reconcile":
        return cmd_reconcile(token)
    if args.cmd == "onboard":
        return cmd_onboard(token, dry_run=args.dry_run)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
