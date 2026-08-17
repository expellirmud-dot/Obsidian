#!/usr/bin/env python3
"""Read-only GitHub adapter for the Live Project Wall.

Fills `ci_state`, `open_pr`, and `observed_at` in
`automation/state/<project_id>.yaml` for every project registered in
`automation/projects.yaml` by querying the GitHub REST API (read-only).

Created by WO-OBSIDIAN-034 (GitHub Project Truth Integration).

Safety contract (enforced unconditionally):
  * READ-ONLY -- never calls any endpoint that mutates a source repository
    (no merge / commit / comment / push). Only GET requests are issued.
  * API failure / timeout / HTTP error -> `ci_state: unknown`
    (NEVER fabricate `failure`).
  * No GITHUB_TOKEN -> `ci_state: unknown`, `open_pr: null`, warn and continue.
  * Rate limit (HTTP 403/429) -> log, set `unknown`, continue (no crash).
  * PR / CI truth is tied to the exact HEAD SHA (never floating "latest").
  * `observed_at` (ISO-8601) is recorded in every updated state file.
  * The token is never logged, written to a file, or sent anywhere except
    the authorized api.github.com endpoints.

Usage:
    python3 automation/github_adapter.py
"""

from __future__ import annotations

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

# Resolve paths relative to the repository root (this file lives in automation/).
REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_YAML = REPO_ROOT / "automation" / "projects.yaml"
STATE_DIR = REPO_ROOT / "automation" / "state"
SCHEMA_PATH = REPO_ROOT / "automation" / "schema" / "project-state.schema.json"

API_BASE = "https://api.github.com"
REQUEST_TIMEOUT = 20  # seconds

# Only GET is permitted -- read-only adapter. This allowlist is a defensive
# guard: any non-GET method would be a contract violation.
ALLOWED_METHOD = "GET"


def now_iso() -> str:
    """Current UTC time as an ISO-8601 string with seconds and 'Z' suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_projects_registry() -> list[dict]:
    with open(PROJECTS_YAML, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [p for p in data.get("projects", []) if p.get("enabled_for_wall") is True]


def load_schema() -> dict:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_token() -> str | None:
    """Return the GitHub token from the environment, or None.

    Accepts GITHUB_TOKEN (primary) or GH_TOKEN (fallback). Never logs the value.
    """
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def parse_owner_repo(repository_url: str) -> tuple[str, str] | None:
    """Extract (owner, repo) from a GitHub URL. Returns None if not parseable."""
    if not repository_url:
        return None
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", repository_url)
    if not m:
        return None
    return m.group(1), m.group(2)


def github_request(path: str, token: str | None) -> tuple[int, dict | list | None, dict]:
    """Issue a read-only GET to api.github.com. Returns (status, json, headers).

    Only GET is ever used -- this adapter is strictly read-only.
    """
    url = f"{API_BASE}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "obsidian-github-adapter/1.0 (read-only)",
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


def is_rate_limited(status: int, headers: dict) -> bool:
    if status == 429:
        return True
    if status == 403:
        remaining = headers.get("X-RateLimit-Remaining") or headers.get(
            "x-ratelimit-remaining"
        )
        if remaining is not None and str(remaining) == "0":
            return True
        reset = headers.get("X-RateLimit-Reset") or headers.get("x-ratelimit-reset")
        if reset is not None:
            return True
    return False


def fetch_repo_head(owner: str, repo: str, token: str | None) -> dict:
    """Fetch the default-branch HEAD commit. Never raises."""
    status, data, headers = github_request(f"/repos/{owner}/{repo}", token)
    if status == -1:
        return {"error": "github_api_unavailable"}
    if status == 404:
        return {"error": "repo_not_accessible"}
    if is_rate_limited(status, headers):
        return {"error": "rate_limited"}
    if status != 200 or not isinstance(data, dict):
        return {"error": "github_api_unavailable"}

    default_branch = data.get("default_branch") or "main"
    s2, cdata, h2 = github_request(
        f"/repos/{owner}/{repo}/commits/{urllib.parse.quote(default_branch)}", token
    )
    if s2 == -1:
        return {"error": "github_api_unavailable", "default_branch": default_branch}
    if is_rate_limited(s2, h2):
        return {"error": "rate_limited", "default_branch": default_branch}
    if s2 == 404:
        return {"error": "head_not_found", "default_branch": default_branch}
    if s2 != 200 or not isinstance(cdata, dict):
        return {"error": "github_api_unavailable", "default_branch": default_branch}

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
    return {
        "default_branch": default_branch,
        "head_sha": sha,
        "last_change": last_change,
    }


def fetch_open_prs(owner: str, repo: str, token: str | None) -> dict:
    """Fetch open PRs (read-only). Never raises."""
    status, data, headers = github_request(
        f"/repos/{owner}/{repo}/pulls?state=open&per_page=100", token
    )
    if status == -1:
        return {"error": "github_api_unavailable"}
    if is_rate_limited(status, headers):
        return {"error": "rate_limited"}
    if status == 404:
        return {"error": "repo_not_accessible"}
    if status != 200 or not isinstance(data, list):
        return {"error": "github_api_unavailable"}
    open_pr_count = len(data)
    open_pr = data[0].get("number") if data else None
    return {"open_pr": open_pr, "open_pr_count": open_pr_count}


def fetch_ci_state(owner: str, repo: str, head_sha: str, token: str | None) -> dict:
    """Resolve CI/check state for the EXACT head_sha (read-only).

    The result is tied to head_sha so it never reflects a floating "latest".
    """
    if not head_sha:
        return {"ci_state": "unknown", "error": "no_head_sha"}

    s1, d1, h1 = github_request(
        f"/repos/{owner}/{repo}/commits/{urllib.parse.quote(head_sha)}/status", token
    )
    s2, d2, h2 = github_request(
        f"/repos/{owner}/{repo}/commits/{urllib.parse.quote(head_sha)}/check-runs"
        "?per_page=100",
        token,
    )

    rate_limited = is_rate_limited(s1, h1) or is_rate_limited(s2, h2)
    if rate_limited:
        return {"ci_state": "unknown", "error": "rate_limited"}
    if s1 == -1 and s2 == -1:
        return {"ci_state": "unknown", "error": "github_api_unavailable"}
    if s1 == 404 and s2 == 404:
        return {"ci_state": "unknown", "error": "repo_not_accessible"}

    states: list[str] = []
    if s1 == 200 and isinstance(d1, dict):
        combined = d1.get("state")
        if combined in ("success", "failure", "pending"):
            states.append(combined)
    if s2 == 200 and isinstance(d2, dict):
        for run in d2.get("check_runs", []) or []:
            st = run.get("conclusion") or run.get("status")
            if st in ("success", "failure", "pending"):
                states.append(st)
            elif st == "neutral":
                states.append("success")
            elif st in ("timed_out", "cancelled", "action_required"):
                states.append("failure")

    if not states:
        return {"ci_state": "unknown"}
    if "failure" in states:
        return {"ci_state": "failure"}
    if "pending" in states:
        return {"ci_state": "pending"}
    return {"ci_state": "success"}


def yaml_scalar(value) -> str:
    """Render a Python value as a YAML scalar fragment for inline replacement."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    s = str(value)
    # Quote ISO-8601 timestamps/dates so PyYAML does not auto-parse them
    # into datetime/date objects (which would violate the string schema).
    if re.match(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?.*)?$", s):
        return '"' + s.replace('"', '\\"') + '"'
    if s == "" or re.match(r"^[\s#:{}\[\],&*!|>'\"%@`]", s) or "://" in s or ": " in s:
        return '"' + s.replace('"', '\\"') + '"'
    return s

def update_state_file(project_id: str, updates: dict) -> bool:
    """Surgically update a state YAML file with the given field values.

    Only the lines for keys present in `updates` are rewritten; an
    `observed_at` line is added/replaced. All other lines (including header
    comments) are preserved verbatim to keep the diff minimal.
    """
    state_path = STATE_DIR / f"{project_id}.yaml"
    original_lines = state_path.read_text(encoding="utf-8").splitlines(keepends=True)

    key_re = re.compile(r"^(\s*)([A-Za-z0-9_]+):\s*(.*)$")
    updated_lines = list(original_lines)
    touched_keys: set[str] = set()
    insert_idx: int | None = None

    for i, line in enumerate(updated_lines):
        m = key_re.match(line.rstrip("\n"))
        if not m:
            continue
        indent, key, _rest = m.group(1), m.group(2), m.group(3)
        if indent != "":
            continue
        if key in updates:
            new_val = updates[key]
            updated_lines[i] = f"{key}: {new_val}\n"
            touched_keys.add(key)
        if key == "adapter_id":
            insert_idx = i + 1

    if "observed_at" in updates and "observed_at" not in touched_keys:
        val = updates["observed_at"]
        new_line = f"observed_at: {val}\n"
        if insert_idx is not None:
            updated_lines.insert(insert_idx, new_line)
        else:
            updated_lines.append(new_line)

    new_text = "".join(updated_lines)
    if new_text == "".join(original_lines):
        return False
    state_path.write_text(new_text, encoding="utf-8")
    return True


def validate_all_states(schema: dict, project_ids: list[str]) -> tuple[int, int]:
    """Validate every state file. Returns (exit_code, valid_count)."""
    validator = Draft202012Validator(schema)
    rc = 0
    valid = 0
    for pid in project_ids:
        state_path = STATE_DIR / f"{pid}.yaml"
        with open(state_path, "r", encoding="utf-8") as f:
            state = yaml.safe_load(f)
        errors = sorted(validator.iter_errors(state), key=lambda e: list(e.path))
        if errors:
            print(f"  INVALID: {pid}")
            for e in errors:
                print(f"    - {'.'.join(map(str, e.path)) or '<root>'}: {e.message}")
            rc = 1
        else:
            print(f"  VALID: {pid}")
            valid += 1
    return rc, valid


def main() -> int:
    print("WO-OBSIDIAN-034 -- GitHub Project Truth Integration (read-only adapter)")
    print("=" * 70)

    token = resolve_token()
    if not token:
        print(
            "WARNING: No GITHUB_TOKEN (or GH_TOKEN) in environment. "
            "All projects will be rendered ci_state=unknown, open_pr=null "
            "(fail-safe, no fabrication)."
        )

    projects = load_projects_registry()
    print(f"Registered enabled projects: {len(projects)}")

    observed_at = now_iso()
    summary: list[dict] = []

    for p in projects:
        pid = p["project_id"]
        repo_url = p.get("repository") or ""
        owner_repo = parse_owner_repo(repo_url) if repo_url else None

        ci_state = "unknown"
        open_pr = None
        last_change = None
        head_sha = None
        note = None

        if not repo_url:
            note = "no_remote"
        elif owner_repo is None:
            note = "unparseable_remote"
        elif not token:
            note = "no_token"
        else:
            owner, repo = owner_repo
            head = fetch_repo_head(owner, repo, token)
            if "error" in head:
                note = head["error"]
            else:
                head_sha = head.get("head_sha")
                last_change = head.get("last_change")
                ci = fetch_ci_state(owner, repo, head_sha, token) if head_sha else {
                    "ci_state": "unknown",
                    "error": "no_head_sha",
                }
                ci_state = ci.get("ci_state", "unknown")
                if "error" in ci:
                    note = ci["error"]
                prs = fetch_open_prs(owner, repo, token)
                if "error" in prs:
                    open_pr = None
                    if note is None:
                        note = prs["error"]
                else:
                    open_pr = prs.get("open_pr")

        updates = {
            "ci_state": yaml_scalar(ci_state),
            "open_pr": yaml_scalar(open_pr),
            "observed_at": yaml_scalar(observed_at),
        }
        if last_change:
            updates["last_change"] = yaml_scalar(last_change)

        changed = update_state_file(pid, updates)
        summary.append(
            {
                "project_id": pid,
                "ci_state": ci_state,
                "open_pr": open_pr,
                "observed_at": observed_at,
                "note": note,
                "changed": changed,
            }
        )

    print("\n--- Adapter summary ---")
    print(f"{'project_id':<32} {'ci_state':<10} {'open_pr':<10} {'observed_at'}")
    print("-" * 70)
    for s in summary:
        pr = "null" if s["open_pr"] is None else str(s["open_pr"])
        print(
            f"{s['project_id']:<32} {s['ci_state']:<10} {pr:<10} {s['observed_at']}"
        )
    notes = [s for s in summary if s["note"]]
    if notes:
        print("\nNotes (fail-safe provenance, generic only):")
        for s in notes:
            print(f"  - {s['project_id']}: {s['note']}")

    print("\n--- Schema validation ---")
    schema = load_schema()
    rc, valid = validate_all_states(schema, [p["project_id"] for p in projects])
    print(f"Validation: {valid}/{len(projects)} VALID (exit code {rc})")

    print("\nRead-only contract: only GET requests issued; no merge/commit/comment/push.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
