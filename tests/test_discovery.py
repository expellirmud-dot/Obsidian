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


# ---------------------------------------------------------------------------
# F6 -- Atomic / repairable onboarding (WO-OBSIDIAN-041)
# ---------------------------------------------------------------------------

def _setup_workspace(monkeypatch, tmp_path):
    """Point discovery file paths at a tmp workspace and return the dirs."""
    state_dir = tmp_path / "state"
    projects_dir = tmp_path / "projects"
    projects_yaml = tmp_path / "projects.yaml"
    state_dir.mkdir()
    projects_dir.mkdir()
    projects_yaml.write_text(
        yaml.safe_dump({"registry_version": 1, "projects": []}), encoding="utf-8"
    )
    monkeypatch.setattr(disc, "STATE_DIR", state_dir)
    monkeypatch.setattr(disc, "PROJECTS_DIR", projects_dir)
    monkeypatch.setattr(disc, "PROJECTS_YAML", projects_yaml)
    monkeypatch.setattr(
        disc, "fetch_repo_head_sha",
        lambda o, r, t: {"default_branch": "main", "head_sha": "abc", "last_change": "2026-08-10"},
    )
    return state_dir, projects_dir, projects_yaml


def _brand_new_repo():
    return {
        "id": 1002, "name": "brand-new-repo",
        "full_name": "expellirmud-dot/brand-new-repo",
        "default_branch": "main",
        "html_url": "https://github.com/expellirmud-dot/brand-new-repo",
    }


def test_onboarding_failure_does_not_leave_partial_registration(monkeypatch, tmp_path):
    """A crash after the state write but before the registry append is repaired
    on rerun: the missing registry entry + overview are appended without
    creating a duplicate."""
    state_dir, projects_dir, projects_yaml = _setup_workspace(monkeypatch, tmp_path)
    repo = _brand_new_repo()

    # First call: succeed fully, then simulate a partial state by removing the
    # registry entry and overview (as if onboarding crashed after the state write).
    disc.onboard_project(repo, token="fake", dry_run=False)
    assert (state_dir / "brand-new-repo.yaml").exists()

    # Simulate the crash: registry entry + overview gone, state file remains.
    projects_yaml.write_text(
        yaml.safe_dump({"registry_version": 1, "projects": []}), encoding="utf-8"
    )
    for md in projects_dir.glob("*.md"):
        md.unlink()

    # Rerun must repair (append registry + write overview), not duplicate.
    res = disc.onboard_project(repo, token="fake", dry_run=False)
    assert res["created"] is False
    assert res["reason"] == "repaired"
    assert res["repaired_registry"] is True
    assert res["repaired_overview"] is True

    reg = yaml.safe_load(projects_yaml.read_text("utf-8"))
    brand_entries = [p for p in reg["projects"] if p["project_id"] == "brand-new-repo"]
    assert len(brand_entries) == 1  # no duplicate
    assert brand_entries[0]["github_repository_id"] == 1002
    assert any("needs-verification" in p.read_text("utf-8") for p in projects_dir.glob("*.md"))


def test_onboarding_rerun_repairs_incomplete_state(monkeypatch, tmp_path):
    """State file exists, no registry entry, no overview -> rerun repairs both
    and the registry ends with exactly one entry."""
    state_dir, projects_dir, projects_yaml = _setup_workspace(monkeypatch, tmp_path)
    repo = _brand_new_repo()

    # Seed ONLY a state file (no registry entry, no overview).
    state = disc._default_state_v2(
        "brand-new-repo", "Brand New Repo", 1002,
        "https://github.com/expellirmud-dot/brand-new-repo.git",
        "main", "abc", "2026-08-10", disc.now_iso(),
    )
    (state_dir / "brand-new-repo.yaml").write_text(
        yaml.safe_dump(state, sort_keys=False), encoding="utf-8"
    )

    res = disc.onboard_project(repo, token="fake", dry_run=False)
    assert res["created"] is False
    assert res["reason"] == "repaired"

    reg = yaml.safe_load(projects_yaml.read_text("utf-8"))
    assert len(reg["projects"]) == 1
    assert reg["projects"][0]["project_id"] == "brand-new-repo"
    assert (projects_dir / "Brand New Repo.md").exists()


def test_onboarding_is_idempotent_after_success(monkeypatch, tmp_path):
    """After a successful onboarding, a second call returns already_onboarded
    with no duplicate registry entry and no duplicate overview."""
    state_dir, projects_dir, projects_yaml = _setup_workspace(monkeypatch, tmp_path)
    repo = _brand_new_repo()

    r1 = disc.onboard_project(repo, token="fake", dry_run=False)
    assert r1["created"] is True

    overview_count_before = len(list(projects_dir.glob("*.md")))

    r2 = disc.onboard_project(repo, token="fake", dry_run=False)
    assert r2["created"] is False
    assert r2["reason"] == "already_onboarded"

    reg = yaml.safe_load(projects_yaml.read_text("utf-8"))
    brand_entries = [p for p in reg["projects"] if p["project_id"] == "brand-new-repo"]
    assert len(brand_entries) == 1
    assert len(list(projects_dir.glob("*.md"))) == overview_count_before  # no dup overview


def test_onboarding_never_duplicates_project_by_stable_repo_id(monkeypatch, tmp_path):
    """Onboarding a repo, then re-onboarding with the SAME stable id but a
    DIFFERENT name, does not create a duplicate registry entry (matched by
    stable github_repository_id)."""
    state_dir, projects_dir, projects_yaml = _setup_workspace(monkeypatch, tmp_path)

    repo_a = {
        "id": 3001, "name": "alpha-repo", "full_name": "owner/alpha-repo",
        "default_branch": "main", "html_url": "https://github.com/owner/alpha-repo",
    }
    repo_b = {
        "id": 3001, "name": "renamed-repo", "full_name": "owner/renamed-repo",
        "default_branch": "main", "html_url": "https://github.com/owner/renamed-repo",
    }

    disc.onboard_project(repo_a, token="fake", dry_run=False)
    res = disc.onboard_project(repo_b, token="fake", dry_run=False)

    # Matched by stable id 3001 -> not a new project; repaired (no duplicate).
    assert res["created"] is False
    reg = yaml.safe_load(projects_yaml.read_text("utf-8"))
    rid_entries = [p for p in reg["projects"] if p.get("github_repository_id") == 3001]
    assert len(rid_entries) == 1  # exactly one entry for the stable id


def test_onboarding_validates_state_before_any_write(monkeypatch, tmp_path):
    """Schema-invalid state is never written: no state file, no registry entry,
    no overview."""
    state_dir, projects_dir, projects_yaml = _setup_workspace(monkeypatch, tmp_path)
    repo = _brand_new_repo()

    # Force schema validation to fail by making the produced state invalid.
    real_default_state = disc._default_state_v2

    def bad_state(*args, **kwargs):
        s = real_default_state(*args, **kwargs)
        s["schema_version"] = 999  # invalid -> schema rejects
        return s

    monkeypatch.setattr(disc, "_default_state_v2", bad_state)

    res = disc.onboard_project(repo, token="fake", dry_run=False)
    assert res["created"] is False
    assert res["reason"] == "schema_invalid"

    # Nothing was written.
    assert not (state_dir / "brand-new-repo.yaml").exists()
    reg = yaml.safe_load(projects_yaml.read_text("utf-8"))
    assert reg["projects"] == []
    assert list(projects_dir.glob("*.md")) == []


# ---------------------------------------------------------------------------
# F8 -- Dry-run must be strictly read-only (WO-OBSIDIAN-041)
# ---------------------------------------------------------------------------

def _seed_state_file(state_dir, project_id="brand-new-repo", project_name="Brand New Repo",
                     rid=1002, repository="https://github.com/expellirmud-dot/brand-new-repo.git"):
    """Write a minimal valid state file and return its path."""
    state = disc._default_state_v2(
        project_id, project_name, rid, repository,
        "main", "abc", "2026-08-10", disc.now_iso(),
    )
    path = state_dir / f"{project_id}.yaml"
    path.write_text(yaml.safe_dump(state, sort_keys=False), encoding="utf-8")
    return path


def _seed_registry_entry(projects_yaml, project_id="brand-new-repo",
                         project_name="Brand New Repo", rid=1002,
                         repository="https://github.com/expellirmud-dot/brand-new-repo.git"):
    """Append a single registry entry to projects.yaml."""
    reg = yaml.safe_load(projects_yaml.read_text("utf-8")) or {"projects": []}
    reg.setdefault("projects", []).append({
        "project_id": project_id, "project_name": project_name,
        "repository": repository, "github_repository_id": rid,
        "enabled_for_wall": True,
    })
    projects_yaml.write_text(yaml.safe_dump(reg), encoding="utf-8")


def _seed_overview(projects_dir, project_name="Brand New Repo"):
    """Write a minimal overview file and return its path."""
    path = projects_dir / f"{project_name}.md"
    path.write_text("---\ntype: project-overview\n---\n# seeded\n", encoding="utf-8")
    return path


def test_dry_run_new_onboarding_no_writes(monkeypatch, tmp_path):
    """dry_run=True with nothing existing -> ZERO writes (byte-for-byte)."""
    state_dir, projects_dir, projects_yaml = _setup_workspace(monkeypatch, tmp_path)
    repo = _brand_new_repo()

    state_before = None
    projects_yaml_before = projects_yaml.read_bytes()
    projects_dir_before = sorted(p.read_bytes() for p in projects_dir.glob("*.md"))

    res = disc.onboard_project(repo, token="fake", dry_run=True)
    assert res["dry_run"] is True

    # No state file written.
    assert not (state_dir / "brand-new-repo.yaml").exists()
    # Registry byte-for-byte unchanged.
    assert projects_yaml.read_bytes() == projects_yaml_before
    # No overview written.
    assert sorted(p.read_bytes() for p in projects_dir.glob("*.md")) == projects_dir_before


def test_dry_run_state_only_partial_no_writes(monkeypatch, tmp_path):
    """Seed state file only; dry_run=True -> state unchanged, no registry/overview."""
    state_dir, projects_dir, projects_yaml = _setup_workspace(monkeypatch, tmp_path)
    repo = _brand_new_repo()

    state_path = _seed_state_file(state_dir)
    state_before = state_path.read_bytes()
    projects_yaml_before = projects_yaml.read_bytes()
    projects_dir_before = sorted(p.read_bytes() for p in projects_dir.glob("*.md"))

    res = disc.onboard_project(repo, token="fake", dry_run=True)
    assert res["dry_run"] is True
    assert res["reason"] == "proposed_repair"
    assert res["proposed_repairs"]["state"] is False
    assert res["proposed_repairs"]["registry"] is True
    assert res["proposed_repairs"]["overview"] is True

    # Byte-for-byte unchanged.
    assert state_path.read_bytes() == state_before
    assert projects_yaml.read_bytes() == projects_yaml_before
    assert sorted(p.read_bytes() for p in projects_dir.glob("*.md")) == projects_dir_before


def test_dry_run_registry_only_partial_no_writes(monkeypatch, tmp_path):
    """Seed registry entry only; dry_run=True -> registry unchanged, no state/overview."""
    state_dir, projects_dir, projects_yaml = _setup_workspace(monkeypatch, tmp_path)
    repo = _brand_new_repo()

    _seed_registry_entry(projects_yaml)
    projects_yaml_before = projects_yaml.read_bytes()
    projects_dir_before = sorted(p.read_bytes() for p in projects_dir.glob("*.md"))

    res = disc.onboard_project(repo, token="fake", dry_run=True)
    assert res["dry_run"] is True
    assert res["reason"] == "proposed_repair"
    assert res["proposed_repairs"]["state"] is True
    assert res["proposed_repairs"]["registry"] is False
    assert res["proposed_repairs"]["overview"] is True

    # Byte-for-byte unchanged.
    assert not (state_dir / "brand-new-repo.yaml").exists()
    assert projects_yaml.read_bytes() == projects_yaml_before
    assert sorted(p.read_bytes() for p in projects_dir.glob("*.md")) == projects_dir_before


def test_dry_run_overview_only_partial_no_writes(monkeypatch, tmp_path):
    """Seed overview only; dry_run=True -> overview unchanged, no state/registry."""
    state_dir, projects_dir, projects_yaml = _setup_workspace(monkeypatch, tmp_path)
    repo = _brand_new_repo()

    overview_path = _seed_overview(projects_dir)
    overview_before = overview_path.read_bytes()
    projects_yaml_before = projects_yaml.read_bytes()

    res = disc.onboard_project(repo, token="fake", dry_run=True)
    assert res["dry_run"] is True
    assert res["reason"] == "proposed_repair"
    assert res["proposed_repairs"]["state"] is True
    assert res["proposed_repairs"]["registry"] is True
    assert res["proposed_repairs"]["overview"] is False

    # Byte-for-byte unchanged.
    assert not (state_dir / "brand-new-repo.yaml").exists()
    assert projects_yaml.read_bytes() == projects_yaml_before
    assert overview_path.read_bytes() == overview_before


def test_dry_run_mixed_partial_no_writes(monkeypatch, tmp_path):
    """Seed state + registry (no overview); dry_run=True -> all unchanged."""
    state_dir, projects_dir, projects_yaml = _setup_workspace(monkeypatch, tmp_path)
    repo = _brand_new_repo()

    state_path = _seed_state_file(state_dir)
    _seed_registry_entry(projects_yaml)
    state_before = state_path.read_bytes()
    projects_yaml_before = projects_yaml.read_bytes()
    projects_dir_before = sorted(p.read_bytes() for p in projects_dir.glob("*.md"))

    res = disc.onboard_project(repo, token="fake", dry_run=True)
    assert res["dry_run"] is True
    assert res["reason"] == "proposed_repair"
    assert res["proposed_repairs"]["state"] is False
    assert res["proposed_repairs"]["registry"] is False
    assert res["proposed_repairs"]["overview"] is True

    # Byte-for-byte unchanged.
    assert state_path.read_bytes() == state_before
    assert projects_yaml.read_bytes() == projects_yaml_before
    assert sorted(p.read_bytes() for p in projects_dir.glob("*.md")) == projects_dir_before


# ---------------------------------------------------------------------------
# F9 -- Complete partial-onboarding repair (WO-OBSIDIAN-041)
# ---------------------------------------------------------------------------

def test_repair_registry_only_writes_state_and_overview(monkeypatch, tmp_path):
    """Registry entry exists, no state, no overview -> repair writes state + overview;
    registry has exactly one entry."""
    state_dir, projects_dir, projects_yaml = _setup_workspace(monkeypatch, tmp_path)
    repo = _brand_new_repo()

    _seed_registry_entry(projects_yaml)

    res = disc.onboard_project(repo, token="fake", dry_run=False)
    assert res["created"] is False
    assert res["reason"] == "repaired"
    assert res["repaired_state"] is True
    assert res["repaired_registry"] is False
    assert res["repaired_overview"] is True

    # State written.
    assert (state_dir / "brand-new-repo.yaml").exists()
    # Overview written.
    assert (projects_dir / "Brand New Repo.md").exists()
    # Registry has exactly one entry (no duplicate).
    reg = yaml.safe_load(projects_yaml.read_text("utf-8"))
    brand_entries = [p for p in reg["projects"] if p["project_id"] == "brand-new-repo"]
    assert len(brand_entries) == 1


def test_repair_registry_and_overview_state_missing(monkeypatch, tmp_path):
    """Registry + overview exist, state missing -> repair writes state. All three exist."""
    state_dir, projects_dir, projects_yaml = _setup_workspace(monkeypatch, tmp_path)
    repo = _brand_new_repo()

    _seed_registry_entry(projects_yaml)
    _seed_overview(projects_dir)

    res = disc.onboard_project(repo, token="fake", dry_run=False)
    assert res["created"] is False
    assert res["reason"] == "repaired"
    assert res["repaired_state"] is True
    assert res["repaired_registry"] is False
    assert res["repaired_overview"] is False

    # All three now exist.
    assert (state_dir / "brand-new-repo.yaml").exists()
    assert (projects_dir / "Brand New Repo.md").exists()
    reg = yaml.safe_load(projects_yaml.read_text("utf-8"))
    brand_entries = [p for p in reg["projects"] if p["project_id"] == "brand-new-repo"]
    assert len(brand_entries) == 1


def test_repair_state_and_registry_overview_missing(monkeypatch, tmp_path):
    """State + registry exist, overview missing -> repair writes overview."""
    state_dir, projects_dir, projects_yaml = _setup_workspace(monkeypatch, tmp_path)
    repo = _brand_new_repo()

    _seed_state_file(state_dir)
    _seed_registry_entry(projects_yaml)

    res = disc.onboard_project(repo, token="fake", dry_run=False)
    assert res["created"] is False
    assert res["reason"] == "repaired"
    assert res["repaired_state"] is False
    assert res["repaired_registry"] is False
    assert res["repaired_overview"] is True

    assert (projects_dir / "Brand New Repo.md").exists()
    reg = yaml.safe_load(projects_yaml.read_text("utf-8"))
    brand_entries = [p for p in reg["projects"] if p["project_id"] == "brand-new-repo"]
    assert len(brand_entries) == 1


def test_repair_state_and_overview_registry_missing(monkeypatch, tmp_path):
    """State + overview exist, registry missing -> repair appends registry."""
    state_dir, projects_dir, projects_yaml = _setup_workspace(monkeypatch, tmp_path)
    repo = _brand_new_repo()

    _seed_state_file(state_dir)
    _seed_overview(projects_dir)

    res = disc.onboard_project(repo, token="fake", dry_run=False)
    assert res["created"] is False
    assert res["reason"] == "repaired"
    assert res["repaired_state"] is False
    assert res["repaired_registry"] is True
    assert res["repaired_overview"] is False

    reg = yaml.safe_load(projects_yaml.read_text("utf-8"))
    brand_entries = [p for p in reg["projects"] if p["project_id"] == "brand-new-repo"]
    assert len(brand_entries) == 1


def test_never_already_onboarded_while_state_missing(monkeypatch, tmp_path):
    """Registry + overview exist but NO state -> must NOT return already_onboarded;
    it must repair (write state) or fail closed."""
    state_dir, projects_dir, projects_yaml = _setup_workspace(monkeypatch, tmp_path)
    repo = _brand_new_repo()

    _seed_registry_entry(projects_yaml)
    _seed_overview(projects_dir)

    res = disc.onboard_project(repo, token="fake", dry_run=False)
    assert res.get("reason") != "already_onboarded"
    # It repaired (wrote the missing state).
    assert res["reason"] == "repaired"
    assert res["repaired_state"] is True
    assert (state_dir / "brand-new-repo.yaml").exists()
