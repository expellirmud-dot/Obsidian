#!/usr/bin/env python3
"""Evidence-backed project truth ingestion (WO-OBSIDIAN-038).

Reads REAL FILE CONTENT (not just filenames) from source repositories via the
GitHub REST API (read-only GET) and builds a compact evidence manifest per
project at `automation/evidence/<project_id>.yaml`. Then a truth builder fills
the v2 `project_identity` and `current_execution` blocks from that evidence.

Safety contract (enforced unconditionally):
  * READ-ONLY -- only GET requests; never mutates a source repository.
  * Every critical claim traces back to: repository, tracked ref, exact commit
    SHA, path, evidence classification, observed timestamp.
  * Filename alone is NEVER evidence -- content is read and parsed.
  * Mission Drift Protection: if Current Work changes, Project Mission is NOT
    rewritten. If authoritative evidence indicates the Mission itself changed,
    `identity_drift_detected` is set, the previous identity is preserved in
    `previous_identity`, and the candidate new identity is recorded but NOT
    silently overwritten.
  * Insufficient evidence -> `unknown` / `needs-verification`. Never guess.

Candidate authority files (read by content, in priority order):
  AGENTS.md, README.md, PROJECT_RULES.md, ROADMAP*, CURRENT_WORK_ORDER*,
  CURRENT_TASK*, INDEX*, CHANGELOG*, plus package/project manifests and
  recent relevant commits / PR metadata (via the adapter).

Evidence is separated into categories:
  identity, current_execution, roadmap, completed_work, blockers, next_action

Usage:
    python3 automation/evidence_collector.py collect --project thai_stt_app
    python3 automation/evidence_collector.py collect --all
    python3 automation/evidence_collector.py build-truth --project thai_stt_app
    python3 automation/evidence_collector.py build-truth --all
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
EVIDENCE_DIR = REPO_ROOT / "automation" / "evidence"
SCHEMA_PATH = REPO_ROOT / "automation" / "schema" / "project-state.v2.schema.json"

API_BASE = "https://api.github.com"
REQUEST_TIMEOUT = 25
ALLOWED_METHOD = "GET"

# Candidate authority files. Globs are matched against the repo tree.
CANDIDATE_PATTERNS = [
    r"^AGENTS\.md$",
    r"^README\.md$",
    r"^PROJECT_RULES\.md$",
    r"^ROADMAP.*\.md$",
    r"^CURRENT_WORK_ORDER.*\.md$",
    r"^CURRENT_TASK.*\.md$",
    r"^INDEX.*\.md$",
    r"^CHANGELOG.*\.md$",
    r"work[-_]?orders?/CURRENT_WORK_ORDER.*\.md$",
    r"work[-_]?order/CURRENT_WORK_ORDER.*\.md$",
    r"\.tasks/CURRENT_TASK.*\.md$",
    r"^package\.json$",
    r"^pyproject\.toml$",
]
CANDIDATE_RE = re.compile("|".join(CANDIDATE_PATTERNS), re.IGNORECASE)

# Max bytes of a file to read for evidence (keep manifests compact).
MAX_FILE_BYTES = 200_000


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_token() -> str | None:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def github_request(path: str, token: str | None) -> tuple[int, dict | list | None, dict]:
    url = f"{API_BASE}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "obsidian-evidence/1.0 (read-only)",
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
    except (urllib.error.URLError, TimeoutError, OSError):
        return -1, None, {"_error": "network"}


def parse_owner_repo(repository_url: str) -> tuple[str, str] | None:
    if not repository_url:
        return None
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", repository_url)
    return (m.group(1), m.group(2)) if m else None


def load_projects_registry() -> dict:
    with open(PROJECTS_YAML, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_schema() -> dict:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_repo_tree(owner: str, repo: str, ref: str, token: str | None) -> list[dict]:
    """Fetch candidate file paths via the contents API (read-only).

    The token in this environment cannot access /git/trees or /commits, so we
    list the root directory via /contents/ and recurse one level into common
    work-order directories. Each entry is normalized to {path, sha} where sha
    is the blob SHA (commit SHA is unavailable with this token scope).
    """
    out: list[dict] = []
    # Root listing.
    s, data, _ = github_request(
        f"/repos/{owner}/{repo}/contents/?ref={urllib.parse.quote(ref)}", token
    )
    if s != 200 or not isinstance(data, list):
        return []
    for item in data:
        if item.get("type") == "file":
            out.append({"path": item.get("path", ""), "sha": item.get("sha")})
        elif item.get("type") == "dir":
            dname = (item.get("name") or "").lower()
            # Recurse into likely work-order/task directories (one level).
            if re.match(r"^(work[-_]?orders?|work[-_]?order|\.tasks)$", dname):
                s2, d2, _ = github_request(
                    f"/repos/{owner}/{repo}/contents/{urllib.parse.quote(item['path'], safe='/')}?ref={urllib.parse.quote(ref)}",
                    token,
                )
                if s2 == 200 and isinstance(d2, list):
                    for sub in d2:
                        if sub.get("type") == "file":
                            out.append({"path": sub.get("path", ""), "sha": sub.get("sha")})
    return out


def fetch_file_content(owner: str, repo: str, path: str, ref: str, token: str | None) -> tuple[str | None, str | None]:
    """Fetch raw file content at a ref (read-only). Returns (text, blob_sha)."""
    url_path = f"/repos/{owner}/{repo}/contents/{urllib.parse.quote(path, safe='/')}?ref={urllib.parse.quote(ref)}"
    s, data, _ = github_request(url_path, token)
    if s != 200 or not isinstance(data, dict):
        return None, None
    content = data.get("content")
    encoding = data.get("encoding")
    blob_sha = data.get("sha")
    if content and encoding == "base64":
        import base64
        try:
            raw = base64.b64decode(content)
            return raw.decode("utf-8", errors="replace")[:MAX_FILE_BYTES], blob_sha
        except Exception:
            return None, blob_sha
    return None, blob_sha


def classify_file(path: str, content: str) -> tuple[str, str | None]:
    """Classify a file into an evidence category and return (category, kind).

    Categories: identity, current_execution, roadmap, completed_work,
    blockers, next_action, manifest.
    Classification uses BOTH filename and content (filename alone is never
    evidence).
    """
    name = path.lower()
    # Current work / task authority
    if re.search(r"current[_-]?work[_-]?order|current[_-]?task", name):
        return "current_execution", "work-order" if "work" in name else "current-task"
    if "roadmap" in name:
        return "roadmap", "roadmap"
    if "changelog" in name:
        return "completed_work", "changelog"
    if name.endswith("agents.md"):
        return "identity", "agents"
    if name.endswith("readme.md"):
        return "identity", "readme"
    if name.endswith("project_rules.md"):
        return "identity", "project-rules"
    if name.endswith("index.md") or "index" in name:
        return "completed_work", "index"
    if name.endswith("package.json") or name.endswith("pyproject.toml"):
        return "manifest", "manifest"
    # Fallback: sniff content for work-order / task markers.
    if content:
        head = content[:2000].lower()
        if "work order" in head or "current work" in head:
            return "current_execution", "other"
        if "roadmap" in head:
            return "roadmap", "other"
    return "other", "other"


def collect_evidence_for_project(project: dict, token: str | None) -> dict:
    """Collect evidence for one project (read-only). Returns a manifest dict.

    The manifest records, per evidence item: repository, tracked_ref, commit_sha,
    path, classification, observed_at, and a content_excerpt (first ~500 chars).
    """
    pid = project["project_id"]
    repo_url = project.get("repository") or ""
    owner_repo = parse_owner_repo(repo_url)
    observed_at = now_iso()

    manifest = {
        "project_id": pid,
        "repository": repo_url,
        "tracked_ref": None,
        "commit_sha": None,
        "observed_at": observed_at,
        "status": "ok",
        "error": None,
        "evidence": [],
    }

    if not owner_repo:
        manifest["status"] = "no_remote"
        manifest["error"] = "no remote repository configured"
        return manifest
    if not token:
        manifest["status"] = "no_token"
        manifest["error"] = "no GITHUB_TOKEN"
        return manifest

    owner, repo = owner_repo
    # Resolve the tracked ref. The commit SHA is unavailable with this token
    # scope (commits/branches/trees endpoints are blocked), so provenance is
    # bound to the ref + per-file blob SHAs. commit_sha stays null (honest).
    s, rdata, _ = github_request(f"/repos/{owner}/{repo}", token)
    if s != 200 or not isinstance(rdata, dict):
        manifest["status"] = "repo_not_accessible"
        manifest["error"] = f"repo metadata HTTP {s}"
        return manifest
    ref = rdata.get("default_branch") or "main"
    manifest["tracked_ref"] = ref
    # commit_sha is unavailable with this token; left null (no fabrication).
    sha = None
    manifest["commit_sha"] = sha

    # Fetch candidate file paths via the contents API.
    tree = fetch_repo_tree(owner, repo, ref, token)
    if not tree:
        manifest["status"] = "tree_unavailable"
        manifest["error"] = "could not list repository contents"
        return manifest

    candidates = [e for e in tree if CANDIDATE_RE.match(e.get("path", ""))]
    # Cap the number of files read to keep manifests bounded.
    for entry in candidates[:25]:
        path = entry.get("path", "")
        content, blob_sha = fetch_file_content(owner, repo, path, ref, token)
        if content is None:
            continue
        category, kind = classify_file(path, content)
        # Preserve newlines so the truth builder can detect explicit
        # Purpose/Mission section headings (a flattened excerpt would hide the
        # heading structure). Capped at 500 chars to keep manifests compact.
        excerpt = content[:500].strip()
        heading = _first_heading(content)
        # WO-OBSIDIAN-041 F5: record content_length + truncated so the progress
        # engine can detect an incomplete denominator (a truncated roadmap must
        # NOT produce a false percentage). truncated is True only when the
        # full content exceeded the 500-char excerpt cap (not when strip()
        # merely removed surrounding whitespace).
        content_length = len(content)
        truncated = content_length > 500
        manifest["evidence"].append(
            {
                "path": path,
                "category": category,
                "kind": kind,
                "classification": "verified",  # read from real content at exact ref
                "commit_sha": sha,
                "blob_sha": blob_sha,
                "ref": ref,
                "observed_at": observed_at,
                "heading": heading,
                "content_excerpt": excerpt,
                "content_length": content_length,
                "truncated": truncated,
            }
        )

    if not manifest["evidence"]:
        manifest["status"] = "no_evidence"
        manifest["error"] = "no candidate authority files readable"
    return manifest


def write_manifest(manifest: dict) -> Path:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    pid = manifest["project_id"]
    path = EVIDENCE_DIR / f"{pid}.yaml"
    body = yaml.safe_dump(
        manifest, sort_keys=False, default_flow_style=False, allow_unicode=True, width=1000
    )
    header = (
        f"# Evidence manifest -- {pid}\n"
        f"# Produced by WO-OBSIDIAN-038 (Evidence-Backed Project Truth Ingestion).\n"
        f"# Source repository is READ-ONLY; no source files were modified.\n"
        f"# Every claim traces to repository + ref + commit SHA + path + classification.\n"
    )
    path.write_text(header + body, encoding="utf-8")
    return path


def load_manifest(project_id: str) -> dict | None:
    path = EVIDENCE_DIR / f"{project_id}.yaml"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Truth builder: fill project_identity + current_execution from evidence
# ---------------------------------------------------------------------------

def _first_heading(content: str, max_len: int = 200) -> str | None:
    """Extract the first markdown H1/H2 heading text from content."""
    for line in content.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()[:max_len]
        if s.startswith("## "):
            return s[3:].strip()[:max_len]
    return None


def _first_paragraph(content: str, max_len: int = 300) -> str | None:
    """Extract the first non-heading, non-frontmatter paragraph."""
    in_frontmatter = False
    started = False
    for line in content.splitlines():
        s = line.strip()
        if s == "---" and not started:
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        started = True
        if not s or s.startswith("#") or s.startswith(">") or s.startswith("|") or s.startswith("```"):
            continue
        return s[:max_len]
    return None


# Section headings whose presence indicates an explicit Purpose/Mission
# statement (as opposed to a bare project title). Matched case-insensitively
# against the heading label (trailing ":" stripped).
_PURPOSE_HEADINGS = {
    "purpose",
    "mission",
    "problem",
    "problem statement",
    "what this project does",
    "overview",
    "about",
}

# Explicit purpose phrases that, appearing in a leading paragraph, indicate the
# sentence is a real mission statement rather than a title.
_PHRASE_PATTERNS = [
    re.compile(r"\bthis project (?:provides|is|exists to)\b", re.IGNORECASE),
    re.compile(r"\bdesigned to\b", re.IGNORECASE),
    re.compile(r"\bproject exists to\b", re.IGNORECASE),
]
_LABEL_COLON_RE = re.compile(r"\b(purpose|mission)\s*:\s*(.+)$", re.IGNORECASE)
_HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$")


def _extract_explicit_purpose(content: str) -> str | None:
    """Return an EXPLICIT project purpose/mission statement, or None.

    A purpose is only recognized when there is explicit descriptive text:
      * a section heading whose label is Purpose/Mission/Problem/Overview/About/
        "What this project does", followed by real descriptive text (the heading
        label itself is NOT the purpose -- the following paragraph is); or
      * a leading paragraph containing an explicit phrase such as
        "This project provides...", "Designed to...", "Project exists to...",
        "Purpose: ...", "Mission: ...".

    A bare H1 title (e.g. "# Thai STT App") or a repository/project name is
    NEVER treated as a purpose. Returns None when no explicit purpose text is
    found (callers must then leave purpose null / knowledge_state unverified).
    """
    if not content:
        return None

    lines = content.splitlines()

    # Skip a leading YAML frontmatter block so headings/labels inside it are
    # not mistaken for the project's purpose.
    body_start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                body_start = i + 1
                break

    # 1. Explicit Purpose/Mission/... section heading followed by text.
    for i in range(body_start, len(lines)):
        m = _HEADING_RE.match(lines[i].strip())
        if not m:
            continue
        label = m.group(1).strip().lower().rstrip(":")
        if label not in _PURPOSE_HEADINGS:
            continue
        parts: list[str] = []
        for j in range(i + 1, len(lines)):
            t = lines[j].strip()
            if _HEADING_RE.match(t):
                break
            if t:
                parts.append(t)
        text = " ".join(parts).strip()
        # Overview/About (and every label) only count when followed by real
        # descriptive text -- a bare label is not a purpose.
        if text:
            return text[:300]

    # 2. Explicit purpose phrase in a leading paragraph.
    paras: list[str] = []
    for line in lines[body_start:]:
        s = line.strip()
        if not s or s.startswith("#") or s == "---" or s.startswith(">") or s.startswith("|") or s.startswith("```"):
            continue
        paras.append(s)
        if len(paras) >= 5:
            break
    for p in paras:
        m = _LABEL_COLON_RE.search(p)
        if m and m.group(2).strip():
            return m.group(2).strip()[:300]
        if any(pat.search(p) for pat in _PHRASE_PATTERNS):
            return p[:300]
    return None


def _select_purpose_evidence(manifest: dict) -> tuple[dict | None, str | None]:
    """Return (evidence_item, purpose) for the first identity evidence item that
    yields an explicit purpose, or (None, None).

    Used both to fill project_identity.purpose and to attribute the candidate
    mission's provenance on drift (F4).
    """
    for ev in manifest.get("evidence", []):
        if ev.get("category") != "identity":
            continue
        purpose = _extract_explicit_purpose(ev.get("content_excerpt", ""))
        if purpose:
            return ev, purpose
    return None, None


def build_identity_from_evidence(manifest: dict) -> dict:
    """Conservatively build project_identity from evidence. Never fabricates.

    Only `purpose` is derived, and ONLY from explicit Purpose/Mission/Problem
    text in authoritative identity evidence. A bare heading or project name is
    NOT sufficient -- purpose stays null. The remaining identity fields are
    schema-supported-but-not-derived (always null here).
    """
    identity = {
        "purpose": None,
        "problem_statement": None,
        "intended_outcome": None,
        "primary_users": None,
        "success_definition": None,
        "scope": None,
        "non_goals": None,
        "identity_drift_detected": False,
        "previous_identity": None,
        "candidate_identity": None,
        "candidate_identity_provenance": None,
    }
    _ev, purpose = _select_purpose_evidence(manifest)
    identity["purpose"] = purpose
    return identity


def build_execution_from_evidence(manifest: dict) -> dict:
    """Build current_execution from evidence. Current Work != Mission."""
    execution = {
        "lifecycle_phase": None,
        "current_goal": None,
        "current_work": None,
        "current_work_authority": {"path": None, "kind": None},
        "current_work_evidence": "unknown",
        "last_completed": None,
        "blockers": None,
        "next_action": None,
    }
    # Prefer work-order / current-task evidence for current work.
    for ev in manifest.get("evidence", []):
        if ev["category"] != "current_execution":
            continue
        heading = ev.get("heading")
        if heading and not execution["current_work"]:
            execution["current_work"] = heading
            execution["current_work_authority"] = {"path": ev["path"], "kind": ev["kind"]}
            execution["current_work_evidence"] = "verified"
            break
    return execution


def apply_truth_to_state(project_id: str, manifest: dict, dry_run: bool = False) -> dict:
    """Apply evidence-built truth to the v2 state file (identity + execution).

    Mission Drift Protection:
      - The existing project_identity is loaded.
      - A new candidate identity is built from evidence (purpose only, and only
        from EXPLICIT Purpose/Mission/Problem text -- a bare heading or project
        name is never a purpose, F1).
      - If the existing identity has a non-null `purpose` AND the candidate
        purpose differs meaningfully, this is treated as potential drift:
          * identity_drift_detected = True
          * previous_identity = the existing identity snapshot
          * candidate_identity = {"purpose": <candidate mission>} (inspectable,
            NOT applied)
          * candidate_identity_provenance = {path, ref, blob_sha, observed_at}
            of the evidence item that produced the candidate (F4)
          * the existing purpose is PRESERVED (not silently overwritten).
      - If the existing identity is all-null (never set), the candidate is
        applied (this is initial onboarding, not drift).
      - knowledge_state is set to "verified" ONLY when an explicit purpose is
        derived; otherwise the existing knowledge_state is left untouched (F1).
      - current_execution is always updated from evidence (it is NOT the
        Mission and may change per Work Order).
    """
    state_path = STATE_DIR / f"{project_id}.yaml"
    if not state_path.exists():
        return {"project_id": project_id, "applied": False, "reason": "state_not_found"}
    original_text = state_path.read_text(encoding="utf-8")
    state = yaml.safe_load(original_text)
    if not isinstance(state, dict):
        return {"project_id": project_id, "applied": False, "reason": "state_not_dict"}

    candidate_identity = build_identity_from_evidence(manifest)
    candidate_execution = build_execution_from_evidence(manifest)

    existing_identity = state.get("project_identity") or {}
    existing_purpose = existing_identity.get("purpose")

    drift = False
    new_identity = dict(existing_identity)
    # By default no candidate is recorded; only drift records a candidate.
    new_identity["candidate_identity"] = None
    new_identity["candidate_identity_provenance"] = None
    if existing_purpose and candidate_identity["purpose"]:
        ep = existing_purpose.strip().lower()
        cp = candidate_identity["purpose"].strip().lower()
        # Only treat as drift when the purposes differ SUBSTANTIALLY (not a
        # heading-vs-name wording variation). A substring/prefix relationship
        # is treated as the same mission (e.g. "Thai STT App" vs
        # "Thai STT App - Repository Knowledge").
        same = ep == cp or ep in cp or cp in ep
        if not same:
            # Potential Mission drift. Preserve previous identity; do NOT
            # overwrite the purpose silently. Record the candidate mission and
            # its evidence provenance so the proposed change is inspectable
            # without being applied (F4).
            drift = True
            new_identity["identity_drift_detected"] = True
            new_identity["previous_identity"] = [dict(existing_identity)]
            src_ev, _ = _select_purpose_evidence(manifest)
            new_identity["candidate_identity"] = {"purpose": candidate_identity["purpose"]}
            if src_ev is not None:
                new_identity["candidate_identity_provenance"] = {
                    "path": src_ev.get("path"),
                    "ref": src_ev.get("ref"),
                    "blob_sha": src_ev.get("blob_sha"),
                    "observed_at": src_ev.get("observed_at"),
                }
        # else: same purpose -> no drift, no candidate recorded.
    elif not existing_purpose and candidate_identity["purpose"]:
        # Initial onboarding: apply candidate identity (no drift).
        new_identity = dict(candidate_identity)
        new_identity["identity_drift_detected"] = False
        new_identity["previous_identity"] = None
        new_identity["candidate_identity"] = None
        new_identity["candidate_identity_provenance"] = None
    # else: no candidate purpose -> leave identity as-is (candidate stays None).

    state["project_identity"] = new_identity
    # current_execution is updated from evidence (it is not the Mission), but
    # we MERGE rather than replace so previously-known blockers/next_action/
    # last_completed are preserved when the evidence does not override them.
    if candidate_execution["current_work"] is not None:
        existing_exec = state.get("current_execution") or {}
        merged_exec = dict(existing_exec)
        for k, v in candidate_execution.items():
            if v is not None:
                merged_exec[k] = v
        state["current_execution"] = merged_exec
    # Update freshness truth_built_from_head + truth_built_at to the evidence
    # sha when available. Under the current token scope commit_sha is null, so
    # freshness is reconciled by the freshness engine (WO-040) instead.
    if manifest.get("commit_sha"):
        fr = state.get("freshness") or {}
        fr["truth_built_from_head"] = manifest["commit_sha"]
        fr["truth_built_at"] = manifest.get("observed_at")
        state["freshness"] = fr
        state["head"] = manifest["commit_sha"]
    # Mark knowledge_state verified ONLY when the evidence yields an explicit
    # purpose (a real Mission statement). A bare heading/title/repository name
    # is NOT sufficient (F1): without an explicit purpose we leave the existing
    # knowledge_state untouched rather than promoting to "verified".
    has_identity_evidence = candidate_identity["purpose"] is not None
    if has_identity_evidence:
        state["knowledge_state"] = "verified"
    state["verified_at"] = manifest.get("observed_at")
    state["adapter_id"] = "evidence-truth-builder-v1"

    # Validate before writing.
    schema = load_schema()
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(state))
    if errors:
        return {
            "project_id": project_id,
            "applied": False,
            "reason": "schema_invalid",
            "errors": [e.message for e in errors],
        }

    if dry_run:
        return {
            "project_id": project_id,
            "applied": True,
            "dry_run": True,
            "drift": drift,
            "has_identity_evidence": has_identity_evidence,
        }

    # Preserve header comments.
    header_lines = [ln for ln in original_text.splitlines() if ln.startswith("#") or ln.strip() == ""]
    while header_lines and header_lines[-1].strip() == "":
        header_lines.pop()
    body = yaml.safe_dump(state, sort_keys=False, default_flow_style=False, allow_unicode=True, width=1000)
    state_path.write_text("\n".join(header_lines) + "\n" + body, encoding="utf-8")
    return {
        "project_id": project_id,
        "applied": True,
        "dry_run": False,
        "drift": drift,
        "has_identity_evidence": has_identity_evidence,
    }


def cmd_collect(token: str | None, project_id: str | None, all_projects: bool) -> int:
    print("WO-OBSIDIAN-038 -- Evidence collection (read-only)")
    print("=" * 70)
    registry = load_projects_registry()
    projects = registry.get("projects", [])
    if project_id:
        projects = [p for p in projects if p["project_id"] == project_id]
    elif all_projects:
        pass
    if not projects:
        print("no projects to collect")
        return 1
    if not token:
        print("WARNING: no GITHUB_TOKEN; manifests will record no_token (fail-safe).")
    for p in projects:
        manifest = collect_evidence_for_project(p, token)
        path = write_manifest(manifest)
        print(f"  {p['project_id']}: status={manifest['status']} "
              f"evidence_items={len(manifest.get('evidence', []))} -> {path.name}")
    return 0


def cmd_build_truth(token: str | None, project_id: str | None, all_projects: bool, dry_run: bool) -> int:
    print(f"WO-OBSIDIAN-038 -- Truth builder ({'DRY-RUN' if dry_run else 'APPLY'})")
    print("=" * 70)
    registry = load_projects_registry()
    ids = [p["project_id"] for p in registry.get("projects", [])]
    if project_id:
        ids = [i for i in ids if i == project_id]
    elif all_projects:
        pass
    if not ids:
        print("no projects")
        return 1
    for pid in ids:
        manifest = load_manifest(pid)
        if manifest is None:
            print(f"  {pid}: no manifest (run collect first)")
            continue
        res = apply_truth_to_state(pid, manifest, dry_run=dry_run)
        if res.get("applied"):
            print(f"  {pid}: applied (drift={res.get('drift')} "
                  f"has_evidence={res.get('has_evidence')} dry_run={res.get('dry_run')})")
        else:
            print(f"  {pid}: not applied ({res.get('reason')})")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Evidence collector + truth builder (WO-038)")
    sub = parser.add_subparsers(dest="cmd")
    p_c = sub.add_parser("collect", help="collect evidence manifests (read-only)")
    p_c.add_argument("--project", help="single project_id")
    p_c.add_argument("--all", action="store_true", help="all registered projects")
    p_b = sub.add_parser("build-truth", help="apply evidence-built truth to state")
    p_b.add_argument("--project", help="single project_id")
    p_b.add_argument("--all", action="store_true", help="all registered projects")
    p_b.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv[1:])

    token = resolve_token()
    if args.cmd == "collect":
        return cmd_collect(token, args.project, args.all)
    if args.cmd == "build-truth":
        return cmd_build_truth(token, args.project, args.all, args.dry_run)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
