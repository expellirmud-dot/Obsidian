"""WO-OBSIDIAN-037 regression suite for repository discovery + onboarding.

Covers automation/discovery.py. No real GitHub API calls are made; tests
monkeypatch github_request and use tmp_path for any file writes.

Required test cases mapped here:
  1. test_discover_new_repository
  2. test_discovery_idempotent_no_duplicate
  3. test_rename_detected_by_stable_id
  4. test_excluded_repo_not_onboarded (archived + fork + denylist)
  5. test_missing_evidence_does_not_fabricate_mission
  6. test_api_unavailable_discovery_unknown
  7. test_onboard_writes_v2_state_needs_verification
  8. test_onboard_appends_registry_and_overview
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
AUTOMATION_DIR = REPO_ROOT / "automation"
for _d in (str(REPO_ROOT), str(AUTOMATION_DIR)):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import discovery as disc  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures: sample GitHub repo payloads (dicts, no HTTP)
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_repos():
    return [
        {"id": 1001, "name": "thai_stt_app", "full_name": "expellirmud-dot/thai_stt_app",
         "archived": False, "fork": False, "default_branch": "main",
         "private": False, "pushed_at": "2026-08-09", "html_url": "https://github.com/expellirmud-dot/thai_stt_app"},
        {"id": 1002, "name": "brand-new-repo", "full_name": "expellirmud-dot/brand-new-repo",
         "archived": False, "fork": False, "default_branch": "main",
         "private": False, "pushed_at": "2026-08-10", "html_url": "https://github.com/expellirmud-dot/brand-new-repo"},
        {"id": 1003, "name": "archived-old", "full_name": "expellirmud-dot/archived-old",
         "archived": True, "fork": False, "default_branch": "main",
         "private": False, "pushed_at": "2025-01-01", "html_url": "https://github.com/expellirmud-dot/archived-old"},
        {"id": 1004, "name": "forked-repo", "full_name": "expellirmud-dot/forked-repo",
         "archived": False, "fork": True, "default_branch": "main",
         "private": False, "pushed_at": "2026-07-01", "html_url": "https://github.com/expellirmud-dot/forked-repo"},
        {"id": 1005, "name": "Obsidian", "full_name": "expellirmud-dot/Obsidian",
         "archived": False, "fork": False, "default_branch": "main",
         "private": False, "pushed_at": "2026-08-17", "html_url": "https://github.com/expellirmud-dot/Obsidian"},
    ]


@pytest.fixture
def registry_with_thai():
    """A registry that already contains thai_stt_app (by stable id)."""
    return {
        "registry_version": 1,
        "projects": [
            {
                "project_id": "thai_stt_app",
                "project_name": "Thai STT App",
                "source_path": "D:\\thai_stt_app",
                "repository": "https://github.com/expellirmud-dot/thai_stt_app.git",
                "github_repository_id": 1001,
                "enabled_for_wall": True,
            },
        ],
    }


def _patch_github_request(monkeypatch, module, repos_payload, status=200):
    """Make module.github_request return the given repo list for the FIRST
    /user/repos or /users/ page, and an empty list for subsequent pages so
    pagination does not accumulate duplicates.
    """
    calls: list[str] = []

    def fake(path, token):
        if path.startswith("/user/repos") or path.startswith("/users/"):
            calls.append(path)
            # First call returns the payload; later pages return empty.
            page_match = "page=" in path
            if page_match and calls.count(path) > 1:
                return status, [], {}
            # Return payload only on the first page; empty for page>=2.
            if "page=2" in path or "page=3" in path:
                return status, [], {}
            return status, repos_payload, {}
        return 404, None, {}

    monkeypatch.setattr(module, "github_request", fake)


# ---------------------------------------------------------------------------
# 1. Discover new repository
# ---------------------------------------------------------------------------

def test_discover_new_repository(sample_repos, monkeypatch):
    """A repo not in the registry is classified as new (eligible)."""
    _patch_github_request(monkeypatch, disc, sample_repos)
    discovery = disc.discover_repos(token="fake")
    assert discovery["status"] == "ok"
    names = [r["name"] for r in discovery["repos"]]
    assert "brand-new-repo" in names

    registry = {"projects": []}
    rec = disc.reconcile_registry(discovery, registry)
    new_names = [r["name"] for r in rec["new"]]
    assert "brand-new-repo" in new_names


# ---------------------------------------------------------------------------
# 2. Discovery idempotent -- no duplicate
# ---------------------------------------------------------------------------

def test_discovery_idempotent_no_duplicate(sample_repos, registry_with_thai, monkeypatch, tmp_path):
    """Onboarding the same repo twice does not create a duplicate project."""
    _patch_github_request(monkeypatch, disc, sample_repos)
    # Point file paths at a tmp workspace so we don't touch the real Vault.
    monkeypatch.setattr(disc, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(disc, "PROJECTS_DIR", tmp_path / "projects")
    monkeypatch.setattr(disc, "PROJECTS_YAML", tmp_path / "projects.yaml")
    (tmp_path / "state").mkdir()
    (tmp_path / "projects").mkdir()
    # Seed a registry with brand-new-repo already present (simulating a prior run).
    registry = {
        "projects": registry_with_thai["projects"] + [
            {"project_id": "brand-new-repo", "project_name": "Brand New Repo",
             "repository": "https://github.com/expellirmud-dot/brand-new-repo.git",
             "github_repository_id": 1002, "enabled_for_wall": True},
        ]
    }
    monkeypatch.setattr(disc, "load_projects_registry", lambda: registry)
    discovery = disc.discover_repos(token="fake")
    rec = disc.reconcile_registry(discovery, registry)
    # brand-new-repo is already registered -> not in `new`.
    new_names = [r["name"] for r in rec["new"]]
    assert "brand-new-repo" not in new_names
    assert rec["known"], "thai_stt_app should be known"

    # Onboarding the (empty) new set is a NO-OP.
    assert rec["new"] == []


# ---------------------------------------------------------------------------
# 3. Rename detected by stable id
# ---------------------------------------------------------------------------

def test_rename_detected_by_stable_id(sample_repos, monkeypatch):
    """A repo whose stable id is in the registry but whose name changed is 'renamed'."""
    _patch_github_request(monkeypatch, disc, sample_repos)
    # Registry knows id 1001 but under a DIFFERENT name (old name).
    registry = {
        "projects": [
            {"project_id": "thai-stt-old-name", "project_name": "Thai STT Old",
             "repository": "https://github.com/expellirmud-dot/thai-stt-old-name.git",
             "github_repository_id": 1001, "enabled_for_wall": True},
        ]
    }
    discovery = disc.discover_repos(token="fake")
    rec = disc.reconcile_registry(discovery, registry)
    assert len(rec["renamed"]) == 1
    assert rec["renamed"][0]["discovered"]["name"] == "thai_stt_app"
    assert rec["renamed"][0]["registered"]["project_id"] == "thai-stt-old-name"
    # It must NOT also appear as new (it was matched by stable id).
    new_names = [r["name"] for r in rec["new"]]
    assert "thai_stt_app" not in new_names


# ---------------------------------------------------------------------------
# 4. Excluded repo not onboarded (archived + fork + denylist)
# ---------------------------------------------------------------------------

def test_excluded_repo_not_onboarded(sample_repos, monkeypatch):
    """Archived, fork, and denylisted repos are excluded and not in `new`."""
    _patch_github_request(monkeypatch, disc, sample_repos)
    discovery = disc.discover_repos(token="fake")
    by_name = {r["name"]: r for r in discovery["repos"]}
    assert by_name["archived-old"]["excluded"] is True
    assert by_name["archived-old"]["exclusion_reason"] == "archived"
    assert by_name["forked-repo"]["excluded"] is True
    assert by_name["forked-repo"]["exclusion_reason"] == "fork"
    assert by_name["Obsidian"]["excluded"] is True
    assert by_name["Obsidian"]["exclusion_reason"] == "denylist"

    rec = disc.reconcile_registry(discovery, {"projects": []})
    new_names = [r["name"] for r in rec["new"]]
    assert "archived-old" not in new_names
    assert "forked-repo" not in new_names
    assert "Obsidian" not in new_names


# ---------------------------------------------------------------------------
# 5. Missing evidence does not fabricate a mission
# ---------------------------------------------------------------------------

def test_missing_evidence_does_not_fabricate_mission(sample_repos, monkeypatch, tmp_path):
    """Onboarding a repo with no readable content yields identity=null (unknown)."""
    _patch_github_request(monkeypatch, disc, sample_repos)
    state_dir = tmp_path / "state"
    projects_dir = tmp_path / "projects"
    projects_yaml = tmp_path / "projects.yaml"
    state_dir.mkdir()
    projects_dir.mkdir()
    projects_yaml.write_text(yaml.safe_dump({"registry_version": 1, "projects": []}), encoding="utf-8")
    monkeypatch.setattr(disc, "STATE_DIR", state_dir)
    monkeypatch.setattr(disc, "PROJECTS_DIR", projects_dir)
    monkeypatch.setattr(disc, "PROJECTS_YAML", projects_yaml)
    # Make head fetch fail so we exercise the no-evidence path.
    def fake_head(owner, repo, token):
        return {"error": "head_not_found", "default_branch": "main"}
    monkeypatch.setattr(disc, "fetch_repo_head_sha", fake_head)

    repo = {"id": 1002, "name": "brand-new-repo",
            "full_name": "expellirmud-dot/brand-new-repo",
            "default_branch": "main", "html_url": "https://github.com/expellirmud-dot/brand-new-repo"}
    res = disc.onboard_project(repo, token="fake", dry_run=False)
    assert res["created"] is True
    assert res["knowledge_state"] == "needs-verification"

    state = yaml.safe_load((state_dir / "brand-new-repo.yaml").read_text("utf-8"))
    identity = state["project_identity"]
    # Every identity field must be null -- no fabrication.
    for f in ("purpose", "problem_statement", "intended_outcome", "primary_users",
              "success_definition", "scope", "non_goals"):
        assert identity[f] is None, f"{f} must be null, got {identity[f]!r}"
    assert identity["identity_drift_detected"] is False
    assert state["knowledge_state"] == "needs-verification"
    # Freshness must be unknown (no head), never fresh.
    assert state["freshness"]["status"] == "unknown"


# ---------------------------------------------------------------------------
# 6. API unavailable -> discovery unknown (no onboarding)
# ---------------------------------------------------------------------------

def test_api_unavailable_discovery_unknown(monkeypatch):
    """When GitHub is unreachable, discovery reports unavailable (fail-safe)."""
    def fake(path, token):
        return -1, None, {"_error": "network"}
    monkeypatch.setattr(disc, "github_request", fake)
    discovery = disc.discover_repos(token="fake")
    assert discovery["status"] == "unavailable"
    assert discovery["repos"] == []

    # No token -> no_token (also fail-safe, no onboarding).
    discovery2 = disc.discover_repos(token=None)
    assert discovery2["status"] == "no_token"


# ---------------------------------------------------------------------------
# 7. Onboard writes a v2 state with needs-verification
# ---------------------------------------------------------------------------

def test_onboard_writes_v2_state_needs_verification(sample_repos, monkeypatch, tmp_path, schema):
    """The onboarded state file validates against the v2 schema and is needs-verification."""
    _patch_github_request(monkeypatch, disc, sample_repos)
    state_dir = tmp_path / "state"
    projects_dir = tmp_path / "projects"
    projects_yaml = tmp_path / "projects.yaml"
    state_dir.mkdir()
    projects_dir.mkdir()
    projects_yaml.write_text(yaml.safe_dump({"registry_version": 1, "projects": []}), encoding="utf-8")
    monkeypatch.setattr(disc, "STATE_DIR", state_dir)
    monkeypatch.setattr(disc, "PROJECTS_DIR", projects_dir)
    monkeypatch.setattr(disc, "PROJECTS_YAML", projects_yaml)
    monkeypatch.setattr(disc, "fetch_repo_head_sha",
                        lambda o, r, t: {"default_branch": "main", "head_sha": "abc123", "last_change": "2026-08-10"})

    repo = {"id": 1002, "name": "brand-new-repo",
            "full_name": "expellirmud-dot/brand-new-repo",
            "default_branch": "main", "html_url": "https://github.com/expellirmud-dot/brand-new-repo"}
    res = disc.onboard_project(repo, token="fake", dry_run=False)
    assert res["created"] is True

    state = yaml.safe_load((state_dir / "brand-new-repo.yaml").read_text("utf-8"))
    validator = Draft202012Validator(schema)
    assert list(validator.iter_errors(state)) == [], "onboarded state must validate against v2 schema"
    assert state["schema_version"] == 2
    assert state["github_repository_id"] == 1002
    assert state["knowledge_state"] == "needs-verification"
    assert state["freshness"]["status"] == "fresh"
    assert state["freshness"]["truth_built_from_head"] == "abc123"


# ---------------------------------------------------------------------------
# 8. Onboard appends registry + writes Project Overview
# ---------------------------------------------------------------------------

def test_onboard_appends_registry_and_overview(sample_repos, monkeypatch, tmp_path):
    """Onboarding appends to projects.yaml and writes a Project Overview stub."""
    _patch_github_request(monkeypatch, disc, sample_repos)
    state_dir = tmp_path / "state"
    projects_dir = tmp_path / "projects"
    projects_yaml = tmp_path / "projects.yaml"
    state_dir.mkdir()
    projects_dir.mkdir()
    # Seed an existing registry.
    seed = {"registry_version": 1, "projects": [
        {"project_id": "thai_stt_app", "project_name": "Thai STT App",
         "repository": "https://github.com/expellirmud-dot/thai_stt_app.git",
         "github_repository_id": 1001, "enabled_for_wall": True},
    ]}
    projects_yaml.write_text(yaml.safe_dump(seed), encoding="utf-8")
    monkeypatch.setattr(disc, "STATE_DIR", state_dir)
    monkeypatch.setattr(disc, "PROJECTS_DIR", projects_dir)
    monkeypatch.setattr(disc, "PROJECTS_YAML", projects_yaml)
    monkeypatch.setattr(disc, "fetch_repo_head_sha",
                        lambda o, r, t: {"default_branch": "main", "head_sha": "abc", "last_change": "2026-08-10"})

    repo = {"id": 1002, "name": "brand-new-repo",
            "full_name": "expellirmud-dot/brand-new-repo",
            "default_branch": "main", "html_url": "https://github.com/expellirmud-dot/brand-new-repo"}
    disc.onboard_project(repo, token="fake", dry_run=False)

    reg = yaml.safe_load(projects_yaml.read_text("utf-8"))
    ids = [p["project_id"] for p in reg["projects"]]
    assert "brand-new-repo" in ids
    assert "thai_stt_app" in ids  # original preserved
    assert len(reg["projects"]) == 2

    # Project Overview stub exists and mentions needs-verification.
    overviews = list(projects_dir.glob("*.md"))
    assert any("needs-verification" in p.read_text("utf-8") for p in overviews)
