"""WO-OBSIDIAN-040 regression suite: freshness engine + end-to-end scenarios.

Covers automation/freshness_engine.py and the end-to-end refresh pipeline.
No real GitHub API calls; tests monkeypatch github_request and use tmp_path.

Required test cases (20):
  1.  test_repo_discovered_new
  2.  test_discovery_idempotent_no_duplicate
  3.  test_repo_rename_uses_stable_id
  4.  test_excluded_repo_not_onboarded
  5.  test_missing_evidence_no_fabrication
  6.  test_head_unchanged_is_fresh
  7.  test_head_changed_is_stale
  8.  test_api_unavailable_is_unknown
  9.  test_failed_refresh_preserves_known_good_state
  10. test_current_wo_change_does_not_rewrite_mission
  11. test_identity_drift_detection
  12. test_weighted_progress_calculation
  13. test_unweighted_bounded_milestones
  14. test_missing_denominator_progress_unknown
  15. test_next_action_from_explicit_authority
  16. test_no_authority_next_action_unknown
  17. test_semantic_refresh_idempotency
  18. test_dashboard_marks_stale_correctly
  19. test_full_refresh_pass_publishes
  20. test_any_gate_fail_prevents_partial_publish

End-to-end scenarios A-F are covered by the integration tests at the end.
"""

from __future__ import annotations

import base64
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

import freshness_engine as fe  # noqa: E402
import discovery as disc  # noqa: E402
import evidence_collector as ev  # noqa: E402
import progress_engine as pe  # noqa: E402


def _b64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def _v2_state(pid="demo", purpose=None, truth_head=None, remote_head=None,
              next_action=None, blockers=None, status="unknown") -> dict:
    return {
        "schema_version": 2, "project_id": pid, "project_name": pid,
        "github_repository_id": None, "source_path": None,
        "repository": f"https://github.com/owner/{pid}.git", "branch": "main", "head": truth_head,
        "knowledge_state": "verified" if purpose else "needs-verification",
        "project_identity": {"purpose": purpose, "problem_statement": None, "intended_outcome": None,
            "primary_users": None, "success_definition": None, "scope": None, "non_goals": None,
            "identity_drift_detected": False, "previous_identity": None,
            "candidate_identity": None, "candidate_identity_provenance": None},
        "current_execution": {"lifecycle_phase": "active", "current_goal": None, "current_work": None,
            "current_work_authority": {"path": None, "kind": None}, "current_work_evidence": "unknown",
            "last_completed": None, "blockers": blockers, "next_action": next_action},
        "freshness": {"status": status, "tracked_ref": "main", "remote_head": remote_head,
            "truth_built_from_head": truth_head, "source_checked_at": None, "truth_built_at": None,
            "stale_since": None, "reason": None, "source_freshness": status,
            "semantic_freshness": status, "progress_freshness": status},
        "progress": {"scope": None, "method": None, "estimate": None, "range_min": None,
            "range_max": None, "confidence": "unknown", "completed": None, "active": None,
            "remaining": None, "basis": None},
        "github": {"ci_state": "unknown", "open_pr": None, "open_pr_count": None, "observed_at": None},
        "last_change": None, "evidence_classification": "verified", "verified_at": None,
        "adapter_id": "x",
    }


def _seed_state(tmp_path: Path, pid: str, state: dict) -> Path:
    state_dir = tmp_path / "state"
    state_dir.mkdir(exist_ok=True)
    p = state_dir / f"{pid}.yaml"
    p.write_text(yaml.safe_dump(state), encoding="utf-8")
    return p


def _patch_fe_github(monkeypatch, responses):
    def fake(path, token):
        # Return empty for page>=2 to avoid duplicate accumulation (checked
        # FIRST, before any key matching).
        if "page=2" in path or "page=3" in path:
            return 200, [], {}
        # Strip query string for matching.
        path_no_q = path.split("?")[0]
        if path in responses:
            return responses[path]
        if path_no_q in responses:
            return responses[path_no_q]
        # Prefix match for listing endpoints.
        for key, val in responses.items():
            if path_no_q == key or path_no_q.endswith(key) or key in path:
                return val
        return 404, None, {}
    monkeypatch.setattr(fe, "github_request", fake)


# ===========================================================================
# Freshness classification tests (6-8, 18)
# ===========================================================================

def test_head_unchanged_is_fresh():
    """HEAD unchanged -> FRESH."""
    status, reason = fe.classify_freshness("abc123", "abc123", accessible=True)
    assert status == "fresh"
    assert reason is None


def test_head_changed_is_stale():
    """remote_head != truth_built_from_head -> STALE."""
    status, reason = fe.classify_freshness("abc123", "def456", accessible=True)
    assert status == "stale"
    assert "changed" in reason


def test_api_unavailable_is_unknown():
    """GitHub inaccessible -> UNKNOWN (never FRESH)."""
    status, reason = fe.classify_freshness("abc123", None, accessible=False)
    assert status == "unknown"
    # UNKNOWN must never be FRESH.
    assert status != "fresh"


def test_unknown_never_becomes_fresh():
    """When remote_head is None (token scope), status is unknown, not fresh."""
    status, _ = fe.classify_freshness("abc123", None, accessible=True)
    assert status == "unknown"


def test_no_truth_head_is_stale():
    """No truth_built_from_head -> stale (needs first build)."""
    status, _ = fe.classify_freshness(None, "abc123", accessible=True)
    assert status == "stale"


# ===========================================================================
# Failed refresh preserves known-good state (9, 20)
# ===========================================================================

def test_failed_refresh_preserves_known_good_state(monkeypatch, tmp_path):
    """If refresh fails, the previous good state is restored and status=refresh_failed."""
    monkeypatch.setattr(fe, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(fe, "PROJECTS_YAML", tmp_path / "projects.yaml")
    monkeypatch.setattr(fe, "EVIDENCE_DIR", tmp_path / "evidence")
    (tmp_path / "state").mkdir()
    (tmp_path / "evidence").mkdir()
    (tmp_path / "projects.yaml").write_text(
        yaml.safe_dump({"projects": [{"project_id": "demo",
            "repository": "https://github.com/owner/demo.git"}]}), encoding="utf-8")

    original = _v2_state(pid="demo", purpose="Mission A", truth_head="h1",
                         remote_head="h1", status="fresh")
    _seed_state(tmp_path, "demo", original)

    # Probe says STALE (head changed), but evidence collection will raise.
    responses = {
        "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
        "/repos/owner/demo/commits/main": (200, {"sha": "h2"}, {}),
    }
    _patch_fe_github(monkeypatch, responses)
    # Force evidence collection to raise.
    monkeypatch.setattr(ev, "collect_evidence_for_project",
                        lambda p, t: (_ for _ in ()).throw(RuntimeError("boom")))

    res = fe.refresh_project({"project_id": "demo",
        "repository": "https://github.com/owner/demo.git"}, token="fake", dry_run=False)
    assert res["status"] == "refresh_failed"
    assert res["restored"] is True
    assert res["published"] is False
    # The original good state is preserved.
    state = yaml.safe_load((tmp_path / "state" / "demo.yaml").read_text("utf-8"))
    assert state["project_identity"]["purpose"] == "Mission A"
    assert state["freshness"]["status"] == "refresh_failed"


def test_any_gate_fail_prevents_partial_publish(monkeypatch, tmp_path):
    """A schema-validation failure prevents publishing partial truth.

    Under F2 the publication gate requires manifest status=="ok" before any
    schema validation runs, so the evidence must succeed first; the broken
    schema then forces refresh_failed with rollback.
    """
    monkeypatch.setattr(fe, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(fe, "PROJECTS_YAML", tmp_path / "projects.yaml")
    monkeypatch.setattr(fe, "EVIDENCE_DIR", tmp_path / "evidence")
    (tmp_path / "state").mkdir()
    (tmp_path / "evidence").mkdir()
    (tmp_path / "projects.yaml").write_text(
        yaml.safe_dump({"projects": [{"project_id": "demo",
            "repository": "https://github.com/owner/demo.git"}]}), encoding="utf-8")
    original = _v2_state(pid="demo", purpose="Mission A", truth_head="h1", status="fresh")
    _seed_state(tmp_path, "demo", original)

    agents_md = "## Mission\n\nMission A\n"
    roadmap_md = "# Roadmap\n\n- [x] (3) M1\n- [ ] (7) M2\n"
    responses = {
        "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
        "/repos/owner/demo/commits/main": (200, {"sha": "h2"}, {}),
        "/repos/owner/demo/contents/?ref=main": (200, [
            {"type": "file", "path": "AGENTS.md", "sha": "blob-a"},
            {"type": "file", "path": "ROADMAP.md", "sha": "blob-r"},
        ], {}),
        "/repos/owner/demo/contents/AGENTS.md?ref=main": (
            200, {"content": _b64(agents_md), "encoding": "base64", "sha": "blob-a"}, {}),
        "/repos/owner/demo/contents/ROADMAP.md?ref=main": (
            200, {"content": _b64(roadmap_md), "encoding": "base64", "sha": "blob-r"}, {}),
    }
    _patch_fe_github(monkeypatch, responses)
    monkeypatch.setattr(ev, "github_request", fe.github_request)
    # Make schema validation fail by returning a broken schema.
    monkeypatch.setattr(fe, "load_schema", lambda: {"type": "string"})  # state is dict -> invalid

    res = fe.refresh_project({"project_id": "demo",
        "repository": "https://github.com/owner/demo.git"}, token="fake", dry_run=False)
    assert res["published"] is False
    assert res["status"] == "refresh_failed"
    assert res.get("restored") is True
    # Original verified identity preserved (not nulled).
    state = yaml.safe_load((tmp_path / "state" / "demo.yaml").read_text("utf-8"))
    assert state["project_identity"]["purpose"] == "Mission A"
    assert state["freshness"]["status"] == "refresh_failed"
    assert state["freshness"]["semantic_freshness"] == "refresh_failed"
    assert state["freshness"]["progress_freshness"] == "refresh_failed"


# ===========================================================================
# Full refresh PASS publishes (19)
# ===========================================================================

def test_full_refresh_pass_publishes(monkeypatch, tmp_path):
    """A successful stale refresh publishes a FRESH state with rebuilt truth."""
    monkeypatch.setattr(fe, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(fe, "PROJECTS_YAML", tmp_path / "projects.yaml")
    monkeypatch.setattr(fe, "EVIDENCE_DIR", tmp_path / "evidence")
    (tmp_path / "state").mkdir()
    (tmp_path / "evidence").mkdir()
    (tmp_path / "projects.yaml").write_text(
        yaml.safe_dump({"projects": [{"project_id": "demo",
            "repository": "https://github.com/owner/demo.git"}]}), encoding="utf-8")
    original = _v2_state(pid="demo", purpose="Mission A", truth_head="h1", status="fresh")
    _seed_state(tmp_path, "demo", original)

    agents_md = "## Mission\n\nMission A\n"
    roadmap_md = "# Roadmap\n\n- [x] (3) M1\n- [ ] (7) M2\n"
    responses = {
        "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
        "/repos/owner/demo/commits/main": (200, {"sha": "h2"}, {}),
        "/repos/owner/demo/contents/?ref=main": (200, [
            {"type": "file", "path": "AGENTS.md", "sha": "blob-a"},
            {"type": "file", "path": "ROADMAP.md", "sha": "blob-r"},
        ], {}),
        "/repos/owner/demo/contents/AGENTS.md?ref=main": (
            200, {"content": _b64(agents_md), "encoding": "base64", "sha": "blob-a"}, {}),
        "/repos/owner/demo/contents/ROADMAP.md?ref=main": (
            200, {"content": _b64(roadmap_md), "encoding": "base64", "sha": "blob-r"}, {}),
    }
    _patch_fe_github(monkeypatch, responses)
    # evidence_collector uses its own github_request; patch it too.
    monkeypatch.setattr(ev, "github_request", fe.github_request)

    res = fe.refresh_project({"project_id": "demo",
        "repository": "https://github.com/owner/demo.git"}, token="fake", dry_run=False)
    assert res["published"] is True
    assert res["deep_refresh"] is True
    assert res["status"] == "fresh"
    state = yaml.safe_load((tmp_path / "state" / "demo.yaml").read_text("utf-8"))
    assert state["freshness"]["status"] == "fresh"
    assert state["freshness"]["truth_built_from_head"] == "h2"
    assert state["freshness"]["remote_head"] == "h2"
    assert state["freshness"]["source_freshness"] == "fresh"
    assert state["freshness"]["semantic_freshness"] == "fresh"
    assert state["freshness"]["progress_freshness"] == "fresh"
    # Mission preserved (same mission).
    assert state["project_identity"]["purpose"] == "Mission A"
    assert state["project_identity"]["identity_drift_detected"] is False


# ===========================================================================
# Semantic refresh idempotency (17)
# ===========================================================================

def test_semantic_refresh_idempotency(monkeypatch, tmp_path):
    """Running refresh twice on a FRESH project does not duplicate or churn."""
    monkeypatch.setattr(fe, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(fe, "PROJECTS_YAML", tmp_path / "projects.yaml")
    monkeypatch.setattr(fe, "EVIDENCE_DIR", tmp_path / "evidence")
    (tmp_path / "state").mkdir()
    (tmp_path / "evidence").mkdir()
    (tmp_path / "projects.yaml").write_text(
        yaml.safe_dump({"projects": [{"project_id": "demo",
            "repository": "https://github.com/owner/demo.git"}]}), encoding="utf-8")
    original = _v2_state(pid="demo", purpose="Mission A", truth_head="h1", status="fresh")
    _seed_state(tmp_path, "demo", original)

    responses = {
        "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
        "/repos/owner/demo/commits/main": (200, {"sha": "h1"}, {}),  # unchanged
    }
    _patch_fe_github(monkeypatch, responses)

    r1 = fe.refresh_project({"project_id": "demo",
        "repository": "https://github.com/owner/demo.git"}, token="fake", dry_run=False)
    r2 = fe.refresh_project({"project_id": "demo",
        "repository": "https://github.com/owner/demo.git"}, token="fake", dry_run=False)
    assert r1["status"] == "fresh"
    assert r1["deep_refresh"] is False
    assert r2["status"] == "fresh"
    assert r2["deep_refresh"] is False
    # State is stable.
    state = yaml.safe_load((tmp_path / "state" / "demo.yaml").read_text("utf-8"))
    assert state["freshness"]["status"] == "fresh"
    assert state["project_identity"]["purpose"] == "Mission A"


# ===========================================================================
# Dashboard marks stale correctly (18)
# ===========================================================================

def test_dashboard_marks_stale_correctly():
    """The freshness status string for a stale project is clearly STALE."""
    status, reason = fe.classify_freshness("h1", "h2", accessible=True)
    assert status == "stale"
    assert "HEAD changed" in reason


# ===========================================================================
# Discovery tests (1-4) -- re-affirmed via freshness module imports
# ===========================================================================

def test_repo_discovered_new(monkeypatch):
    """A repo not in the registry is classified as new by discovery."""
    sample = [{"id": 2001, "name": "newrepo", "full_name": "owner/newrepo",
               "archived": False, "fork": False, "default_branch": "main",
               "html_url": "https://github.com/owner/newrepo"}]
    _patch_fe_github(monkeypatch, {"/user/repos": (200, sample, {}), "/users/owner/repos": (200, sample, {})})
    monkeypatch.setattr(disc, "github_request", fe.github_request)
    discovery = disc.discover_repos(account="owner", token="fake")
    rec = disc.reconcile_registry(discovery, {"projects": []})
    assert len(rec["new"]) == 1
    assert rec["new"][0]["name"] == "newrepo"


def test_discovery_idempotent_no_duplicate(monkeypatch, tmp_path):
    """Onboarding twice does not create a duplicate (match by stable id)."""
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
                        lambda o, r, t: {"default_branch": "main", "head_sha": "h1", "last_change": "x"})
    repo = {"id": 2001, "name": "newrepo", "full_name": "owner/newrepo",
            "default_branch": "main", "html_url": "https://github.com/owner/newrepo"}
    r1 = disc.onboard_project(repo, token="fake", dry_run=False)
    r2 = disc.onboard_project(repo, token="fake", dry_run=False)
    assert r1["created"] is True
    assert r2["created"] is False  # idempotent


def test_repo_rename_uses_stable_id(monkeypatch):
    """A repo whose stable id is in the registry but name changed is 'renamed'."""
    sample = [{"id": 2001, "name": "new_name", "full_name": "owner/new_name",
               "archived": False, "fork": False, "default_branch": "main",
               "html_url": "https://github.com/owner/new_name"}]
    _patch_fe_github(monkeypatch, {"/user/repos": (200, sample, {}), "/users/owner/repos": (200, sample, {})})
    monkeypatch.setattr(disc, "github_request", fe.github_request)
    registry = {"projects": [{"project_id": "old-name", "project_name": "Old",
        "repository": "https://github.com/owner/old-name.git",
        "github_repository_id": 2001, "enabled_for_wall": True}]}
    discovery = disc.discover_repos(account="owner", token="fake")
    rec = disc.reconcile_registry(discovery, registry)
    assert len(rec["renamed"]) == 1
    assert len(rec["new"]) == 0


def test_excluded_repo_not_onboarded(monkeypatch):
    """Archived + fork + denylist repos are excluded from new."""
    sample = [
        {"id": 1, "name": "archived", "full_name": "owner/archived", "archived": True,
         "fork": False, "default_branch": "main", "html_url": "https://github.com/owner/archived"},
        {"id": 2, "name": "forked", "full_name": "owner/forked", "archived": False,
         "fork": True, "default_branch": "main", "html_url": "https://github.com/owner/forked"},
        {"id": 3, "name": "Obsidian", "full_name": "owner/Obsidian", "archived": False,
         "fork": False, "default_branch": "main", "html_url": "https://github.com/owner/Obsidian"},
    ]
    _patch_fe_github(monkeypatch, {"/user/repos": (200, sample, {}), "/users/owner/repos": (200, sample, {})})
    monkeypatch.setattr(disc, "github_request", fe.github_request)
    discovery = disc.discover_repos(account="owner", token="fake")
    eligible = [r for r in discovery["repos"] if not r["excluded"]]
    excluded = [r for r in discovery["repos"] if r["excluded"]]
    assert len(excluded) == 3
    assert len(eligible) == 0


# ===========================================================================
# Missing evidence / no fabrication (5)
# ===========================================================================

def test_missing_evidence_no_fabrication(monkeypatch):
    """No readable content -> identity null, knowledge_state needs-verification."""
    responses = {
        "/repos/owner/empty": (200, {"default_branch": "main"}, {}),
        "/repos/owner/empty/contents/?ref=main": (200, [
            {"type": "file", "path": "src/main.py", "sha": "x"},
        ], {}),
    }
    _patch_fe_github(monkeypatch, responses)
    monkeypatch.setattr(ev, "github_request", fe.github_request)
    manifest = ev.collect_evidence_for_project(
        {"project_id": "empty", "repository": "https://github.com/owner/empty.git"}, token="fake")
    assert manifest["status"] == "no_evidence"
    identity = ev.build_identity_from_evidence(manifest)
    assert identity["purpose"] is None


# ===========================================================================
# Mission drift / current-work-change (10, 11)
# ===========================================================================

def test_current_wo_change_does_not_rewrite_mission(monkeypatch, tmp_path):
    """Changing the work-order updates current_work but NOT the mission."""
    monkeypatch.setattr(ev, "STATE_DIR", tmp_path / "state")
    (tmp_path / "state").mkdir()
    state = _v2_state(pid="demo", purpose="Mission A", truth_head="h1", status="fresh")
    state["current_execution"]["current_work"] = "WO-1 doing A"
    _seed_state(tmp_path, "demo", state)

    agents_md = "# Mission A\n\nA platform.\n"
    wo_md = "# WORK ORDER -- Feature B\n\nCurrent work: implement B.\n"
    responses = {
        "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
        "/repos/owner/demo/contents/?ref=main": (200, [
            {"type": "file", "path": "AGENTS.md", "sha": "a"},
            {"type": "dir", "name": "work_orders", "path": "work_orders"},
        ], {}),
        "/repos/owner/demo/contents/work_orders?ref=main": (200, [
            {"type": "file", "path": "work_orders/CURRENT_WORK_ORDER.md", "sha": "w"},
        ], {}),
        "/repos/owner/demo/contents/AGENTS.md?ref=main": (
            200, {"content": _b64(agents_md), "encoding": "base64", "sha": "a"}, {}),
        "/repos/owner/demo/contents/work_orders/CURRENT_WORK_ORDER.md?ref=main": (
            200, {"content": _b64(wo_md), "encoding": "base64", "sha": "w"}, {}),
    }
    _patch_fe_github(monkeypatch, responses)
    monkeypatch.setattr(ev, "github_request", fe.github_request)
    manifest = ev.collect_evidence_for_project(
        {"project_id": "demo", "repository": "https://github.com/owner/demo.git"}, token="fake")
    res = ev.apply_truth_to_state("demo", manifest, dry_run=False)
    assert res["drift"] is False
    new_state = yaml.safe_load((tmp_path / "state" / "demo.yaml").read_text("utf-8"))
    assert new_state["project_identity"]["purpose"] == "Mission A"
    assert "Feature B" in (new_state["current_execution"]["current_work"] or "")


def test_identity_drift_detection(monkeypatch, tmp_path):
    """A genuinely different mission triggers drift detection + preservation.

    Under F1 a bare heading/paragraph is NOT a purpose, so the candidate mission
    must come from an EXPLICIT Purpose/Mission label for drift to be meaningful.
    """
    monkeypatch.setattr(ev, "STATE_DIR", tmp_path / "state")
    (tmp_path / "state").mkdir()
    state = _v2_state(pid="demo", purpose="Mission A", truth_head="h1", status="fresh")
    _seed_state(tmp_path, "demo", state)

    agents_md = "## Purpose\n\nNow a data pipeline.\n"
    responses = {
        "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
        "/repos/owner/demo/contents/?ref=main": (200, [
            {"type": "file", "path": "AGENTS.md", "sha": "a"},
        ], {}),
        "/repos/owner/demo/contents/AGENTS.md?ref=main": (
            200, {"content": _b64(agents_md), "encoding": "base64", "sha": "a"}, {}),
    }
    _patch_fe_github(monkeypatch, responses)
    monkeypatch.setattr(ev, "github_request", fe.github_request)
    manifest = ev.collect_evidence_for_project(
        {"project_id": "demo", "repository": "https://github.com/owner/demo.git"}, token="fake")
    res = ev.apply_truth_to_state("demo", manifest, dry_run=False)
    assert res["drift"] is True
    new_state = yaml.safe_load((tmp_path / "state" / "demo.yaml").read_text("utf-8"))
    assert new_state["project_identity"]["purpose"] == "Mission A"  # preserved
    assert new_state["project_identity"]["identity_drift_detected"] is True
    assert new_state["project_identity"]["previous_identity"][0]["purpose"] == "Mission A"


def test_refresh_bare_heading_does_not_verify_mission(monkeypatch, tmp_path):
    """F1 regression (Reviewer 1 Finding 1): the refresh path must NOT set
    knowledge_state=verified when the only identity evidence is a bare heading
    (no explicit Purpose/Mission text). The refresh path previously duplicated
    the truth logic and used `e.heading` instead of `purpose is not None`."""
    monkeypatch.setattr(fe, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(fe, "PROJECTS_YAML", tmp_path / "projects.yaml")
    monkeypatch.setattr(fe, "EVIDENCE_DIR", tmp_path / "evidence")
    (tmp_path / "state").mkdir()
    (tmp_path / "evidence").mkdir()
    (tmp_path / "projects.yaml").write_text(
        yaml.safe_dump({"projects": [{"project_id": "demo",
            "repository": "https://github.com/owner/demo.git"}]}), encoding="utf-8")
    # Existing state: needs-verification, no purpose.
    original = _v2_state(pid="demo", purpose=None, truth_head="h1", status="stale")
    _seed_state(tmp_path, "demo", original)

    # AGENTS.md with ONLY a bare heading (no explicit Purpose section).
    agents_md = "# Thai STT App\n\nSome intro text.\n"
    responses = {
        "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
        "/repos/owner/demo/commits/main": (200, {"sha": "h2"}, {}),
        "/repos/owner/demo/contents/?ref=main": (200, [
            {"type": "file", "path": "AGENTS.md", "sha": "blob-a"},
        ], {}),
        "/repos/owner/demo/contents/AGENTS.md?ref=main": (
            200, {"content": _b64(agents_md), "encoding": "base64", "sha": "blob-a"}, {}),
    }
    _patch_fe_github(monkeypatch, responses)
    monkeypatch.setattr(ev, "github_request", fe.github_request)

    res = fe.refresh_project({"project_id": "demo",
        "repository": "https://github.com/owner/demo.git"}, token="fake", dry_run=False)
    new_state = yaml.safe_load((tmp_path / "state" / "demo.yaml").read_text("utf-8"))
    # A bare heading must NOT verify the mission.
    assert new_state["project_identity"]["purpose"] is None
    assert new_state["knowledge_state"] != "verified"


def test_refresh_drift_records_candidate_identity_and_provenance(monkeypatch, tmp_path):
    """F4 regression (Reviewer 1 Finding 2): the refresh path must record
    candidate_identity + candidate_identity_provenance on drift, not just
    previous_identity."""
    monkeypatch.setattr(fe, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(fe, "PROJECTS_YAML", tmp_path / "projects.yaml")
    monkeypatch.setattr(fe, "EVIDENCE_DIR", tmp_path / "evidence")
    (tmp_path / "state").mkdir()
    (tmp_path / "evidence").mkdir()
    (tmp_path / "projects.yaml").write_text(
        yaml.safe_dump({"projects": [{"project_id": "demo",
            "repository": "https://github.com/owner/demo.git"}]}), encoding="utf-8")
    original = _v2_state(pid="demo", purpose="Mission A", truth_head="h1", status="stale")
    _seed_state(tmp_path, "demo", original)

    agents_md = "## Purpose\n\nNow a data pipeline for streaming analytics.\n"
    responses = {
        "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
        "/repos/owner/demo/commits/main": (200, {"sha": "h2"}, {}),
        "/repos/owner/demo/contents/?ref=main": (200, [
            {"type": "file", "path": "AGENTS.md", "sha": "blob-a"},
        ], {}),
        "/repos/owner/demo/contents/AGENTS.md?ref=main": (
            200, {"content": _b64(agents_md), "encoding": "base64", "sha": "blob-a"}, {}),
    }
    _patch_fe_github(monkeypatch, responses)
    monkeypatch.setattr(ev, "github_request", fe.github_request)

    res = fe.refresh_project({"project_id": "demo",
        "repository": "https://github.com/owner/demo.git"}, token="fake", dry_run=False)
    new_state = yaml.safe_load((tmp_path / "state" / "demo.yaml").read_text("utf-8"))
    ident = new_state["project_identity"]
    # Old purpose preserved.
    assert ident["purpose"] == "Mission A"
    assert ident["identity_drift_detected"] is True
    # Candidate + provenance recorded (F4).
    assert ident["candidate_identity"] is not None
    assert ident["candidate_identity"]["purpose"] is not None
    assert "data pipeline" in ident["candidate_identity"]["purpose"].lower()
    assert ident["candidate_identity_provenance"] is not None
    assert ident["candidate_identity_provenance"]["path"] == "AGENTS.md"


def test_refresh_no_drift_clears_candidate_identity(monkeypatch, tmp_path):
    """F4 regression: when a prior drift is resolved (mission now matches),
    the refresh path must clear stale candidate_identity/candidate_identity_provenance."""
    monkeypatch.setattr(fe, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(fe, "PROJECTS_YAML", tmp_path / "projects.yaml")
    monkeypatch.setattr(fe, "EVIDENCE_DIR", tmp_path / "evidence")
    (tmp_path / "state").mkdir()
    (tmp_path / "evidence").mkdir()
    (tmp_path / "projects.yaml").write_text(
        yaml.safe_dump({"projects": [{"project_id": "demo",
            "repository": "https://github.com/owner/demo.git"}]}), encoding="utf-8")
    # Existing state has a STALE candidate from a prior drift cycle.
    state = _v2_state(pid="demo", purpose="Mission A", truth_head="h1", status="stale")
    state["project_identity"]["candidate_identity"] = {"purpose": "stale candidate"}
    state["project_identity"]["candidate_identity_provenance"] = {"path": "old.md"}
    _seed_state(tmp_path, "demo", state)

    # New evidence matches the existing mission (no drift).
    agents_md = "## Purpose\n\nMission A\n"
    responses = {
        "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
        "/repos/owner/demo/commits/main": (200, {"sha": "h2"}, {}),
        "/repos/owner/demo/contents/?ref=main": (200, [
            {"type": "file", "path": "AGENTS.md", "sha": "blob-a"},
        ], {}),
        "/repos/owner/demo/contents/AGENTS.md?ref=main": (
            200, {"content": _b64(agents_md), "encoding": "base64", "sha": "blob-a"}, {}),
    }
    _patch_fe_github(monkeypatch, responses)
    monkeypatch.setattr(ev, "github_request", fe.github_request)

    fe.refresh_project({"project_id": "demo",
        "repository": "https://github.com/owner/demo.git"}, token="fake", dry_run=False)
    new_state = yaml.safe_load((tmp_path / "state" / "demo.yaml").read_text("utf-8"))
    ident = new_state["project_identity"]
    assert ident["identity_drift_detected"] is False
    # Stale candidate cleared.
    assert ident["candidate_identity"] is None
    assert ident["candidate_identity_provenance"] is None


# ===========================================================================
# Progress + next-action (12-16)
# ===========================================================================

def test_weighted_progress_calculation_fe():
    roadmap = "- [x] (3) M1\n- [ ] (7) M2\n"
    manifest = {"evidence": [{"category": "roadmap", "content_excerpt": roadmap}]}
    p = pe.compute_progress(manifest, _v2_state())
    assert p["method"] == "weighted_milestones"
    assert p["estimate"] == 30


def test_unweighted_bounded_milestones_fe():
    roadmap = "- [x] M1\n- [x] M2\n- [ ] M3\n"
    manifest = {"evidence": [{"category": "roadmap", "content_excerpt": roadmap}]}
    p = pe.compute_progress(manifest, _v2_state())
    assert p["method"] == "bounded_milestones"
    assert p["estimate"] == 67


def test_missing_denominator_progress_unknown_fe():
    p = pe.compute_progress({"evidence": []}, _v2_state())
    assert p["estimate"] is None
    assert p["confidence"] == "unknown"


def test_next_action_from_explicit_authority_fe():
    state = _v2_state(next_action="Execute WO-03")
    na = pe.derive_next_action({"evidence": []}, state)
    assert na == "Execute WO-03"


def test_no_authority_next_action_unknown_fe():
    na = pe.derive_next_action({"evidence": []}, _v2_state())
    assert na is None


# ===========================================================================
# End-to-end scenarios A-F
# ===========================================================================

class TestEndToEndScenarios:
    """The six required end-to-end proof scenarios."""

    def _setup(self, monkeypatch, tmp_path):
        monkeypatch.setattr(fe, "STATE_DIR", tmp_path / "state")
        monkeypatch.setattr(fe, "PROJECTS_YAML", tmp_path / "projects.yaml")
        monkeypatch.setattr(fe, "EVIDENCE_DIR", tmp_path / "evidence")
        monkeypatch.setattr(ev, "STATE_DIR", tmp_path / "state")
        monkeypatch.setattr(ev, "EVIDENCE_DIR", tmp_path / "evidence")
        (tmp_path / "state").mkdir()
        (tmp_path / "evidence").mkdir()
        (tmp_path / "projects.yaml").write_text(
            yaml.safe_dump({"projects": [{"project_id": "demo",
                "repository": "https://github.com/owner/demo.git"}]}), encoding="utf-8")

    def test_scenario_a_existing_fresh_project(self, monkeypatch, tmp_path):
        """Scenario A: HEAD unchanged -> FRESH, no deep refresh, no churn."""
        self._setup(monkeypatch, tmp_path)
        original = _v2_state(pid="demo", purpose="Mission A", truth_head="h1", status="fresh")
        _seed_state(tmp_path, "demo", original)
        responses = {
            "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
            "/repos/owner/demo/commits/main": (200, {"sha": "h1"}, {}),  # unchanged
        }
        _patch_fe_github(monkeypatch, responses)
        monkeypatch.setattr(ev, "github_request", fe.github_request)
        res = fe.refresh_project({"project_id": "demo",
            "repository": "https://github.com/owner/demo.git"}, token="fake", dry_run=False)
        assert res["status"] == "fresh"
        assert res["deep_refresh"] is False
        assert res["published"] is True

    def test_scenario_b_existing_project_changed(self, monkeypatch, tmp_path):
        """Scenario B: remote HEAD new -> STALE -> targeted refresh -> FRESH.

        Under F2, FRESH requires all three sub-gates fresh, so the evidence
        must include an explicit purpose (matching the existing mission) and
        a roadmap with milestones.
        """
        self._setup(monkeypatch, tmp_path)
        original = _v2_state(pid="demo", purpose="Mission A", truth_head="h1", status="fresh")
        _seed_state(tmp_path, "demo", original)
        agents_md = "## Mission\n\nMission A\n"
        roadmap_md = "# Roadmap\n\n- [x] (3) M1\n- [ ] (7) M2\n"
        responses = {
            "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
            "/repos/owner/demo/commits/main": (200, {"sha": "h2"}, {}),  # changed
            "/repos/owner/demo/contents/?ref=main": (200, [
                {"type": "file", "path": "AGENTS.md", "sha": "a"},
                {"type": "file", "path": "ROADMAP.md", "sha": "r"},
            ], {}),
            "/repos/owner/demo/contents/AGENTS.md?ref=main": (
                200, {"content": _b64(agents_md), "encoding": "base64", "sha": "a"}, {}),
            "/repos/owner/demo/contents/ROADMAP.md?ref=main": (
                200, {"content": _b64(roadmap_md), "encoding": "base64", "sha": "r"}, {}),
        }
        _patch_fe_github(monkeypatch, responses)
        monkeypatch.setattr(ev, "github_request", fe.github_request)
        res = fe.refresh_project({"project_id": "demo",
            "repository": "https://github.com/owner/demo.git"}, token="fake", dry_run=False)
        assert res["deep_refresh"] is True
        assert res["status"] == "fresh"
        assert res["published"] is True
        state = yaml.safe_load((tmp_path / "state" / "demo.yaml").read_text("utf-8"))
        assert state["freshness"]["truth_built_from_head"] == "h2"
        assert state["freshness"]["semantic_freshness"] == "fresh"
        assert state["freshness"]["progress_freshness"] == "fresh"

    def test_scenario_c_brand_new_repository(self, monkeypatch, tmp_path):
        """Scenario C: repo not in registry -> DISCOVERED -> onboard -> state + overview."""
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
                            lambda o, r, t: {"default_branch": "main", "head_sha": "h1", "last_change": "x"})
        repo = {"id": 3001, "name": "brand-new", "full_name": "owner/brand-new",
                "default_branch": "main", "html_url": "https://github.com/owner/brand-new"}
        res = disc.onboard_project(repo, token="fake", dry_run=False)
        assert res["created"] is True
        assert res["knowledge_state"] == "needs-verification"
        # State file exists.
        assert (state_dir / "brand-new.yaml").exists()
        # No source repo mutation (onboarding only writes Vault files).

    def test_scenario_d_ambiguous_project(self, monkeypatch, tmp_path):
        """Scenario D: no evidence for Mission -> needs-verification, mission unknown."""
        self._setup(monkeypatch, tmp_path)
        responses = {
            "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
            "/repos/owner/demo/contents/?ref=main": (200, [
                {"type": "file", "path": "src/main.py", "sha": "x"}], {}),
        }
        _patch_fe_github(monkeypatch, responses)
        monkeypatch.setattr(ev, "github_request", fe.github_request)
        manifest = ev.collect_evidence_for_project(
            {"project_id": "demo", "repository": "https://github.com/owner/demo.git"}, token="fake")
        assert manifest["status"] == "no_evidence"
        identity = ev.build_identity_from_evidence(manifest)
        assert identity["purpose"] is None  # mission unknown, not fabricated

    def test_scenario_e_misleading_latest_work_order(self, monkeypatch, tmp_path):
        """Scenario E: Mission=A, latest WO=feature B -> Mission stays A, Work=B."""
        monkeypatch.setattr(ev, "STATE_DIR", tmp_path / "state")
        (tmp_path / "state").mkdir()
        state = _v2_state(pid="demo", purpose="Mission A", truth_head="h1", status="fresh")
        _seed_state(tmp_path, "demo", state)
        agents_md = "# Mission A\n\nA platform.\n"
        wo_md = "# WORK ORDER -- Feature B\n\nCurrent work: implement B.\n"
        responses = {
            "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
            "/repos/owner/demo/contents/?ref=main": (200, [
                {"type": "file", "path": "AGENTS.md", "sha": "a"},
                {"type": "dir", "name": "work_orders", "path": "work_orders"}], {}),
            "/repos/owner/demo/contents/work_orders?ref=main": (200, [
                {"type": "file", "path": "work_orders/CURRENT_WORK_ORDER.md", "sha": "w"}], {}),
            "/repos/owner/demo/contents/AGENTS.md?ref=main": (
                200, {"content": _b64(agents_md), "encoding": "base64", "sha": "a"}, {}),
            "/repos/owner/demo/contents/work_orders/CURRENT_WORK_ORDER.md?ref=main": (
                200, {"content": _b64(wo_md), "encoding": "base64", "sha": "w"}, {}),
        }
        _patch_fe_github(monkeypatch, responses)
        monkeypatch.setattr(ev, "github_request", fe.github_request)
        manifest = ev.collect_evidence_for_project(
            {"project_id": "demo", "repository": "https://github.com/owner/demo.git"}, token="fake")
        res = ev.apply_truth_to_state("demo", manifest, dry_run=False)
        assert res["drift"] is False
        new_state = yaml.safe_load((tmp_path / "state" / "demo.yaml").read_text("utf-8"))
        # Mission = A (NOT B).
        assert new_state["project_identity"]["purpose"] == "Mission A"
        # Current work = B.
        assert "Feature B" in (new_state["current_execution"]["current_work"] or "")

    def test_scenario_f_progress(self):
        """Scenario F: roadmap with denominator -> evidence-based %; without -> UNKNOWN."""
        # With denominator.
        roadmap = "- [x] (2) M1\n- [ ] (8) M2\n"
        manifest = {"evidence": [{"category": "roadmap", "content_excerpt": roadmap}]}
        p = pe.compute_progress(manifest, _v2_state())
        assert p["estimate"] == 20  # 2/10
        assert p["method"] == "weighted_milestones"
        # Without denominator.
        p2 = pe.compute_progress({"evidence": []}, _v2_state())
        assert p2["estimate"] is None
        assert p2["confidence"] == "unknown"


# ===========================================================================
# WO-OBSIDIAN-041 / F2: False Freshness / Partial Truth (P1)
# ===========================================================================

def test_remote_head_known_but_evidence_unavailable_not_fresh(monkeypatch, tmp_path):
    """remote_head known but manifest status="no_evidence" -> NOT fresh.

    The OLD bug set all sub-gates "fresh" whenever remote_head was known,
    fabricating fresh semantic truth even when evidence collection failed.
    """
    monkeypatch.setattr(fe, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(fe, "PROJECTS_YAML", tmp_path / "projects.yaml")
    monkeypatch.setattr(fe, "EVIDENCE_DIR", tmp_path / "evidence")
    (tmp_path / "state").mkdir()
    (tmp_path / "evidence").mkdir()
    (tmp_path / "projects.yaml").write_text(
        yaml.safe_dump({"projects": [{"project_id": "demo",
            "repository": "https://github.com/owner/demo.git"}]}), encoding="utf-8")
    original = _v2_state(pid="demo", purpose="Mission A", truth_head="h1", status="fresh")
    _seed_state(tmp_path, "demo", original)

    # remote HEAD known (h2) but contents are non-authoritative -> no_evidence.
    responses = {
        "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
        "/repos/owner/demo/commits/main": (200, {"sha": "h2"}, {}),
        "/repos/owner/demo/contents/?ref=main": (200, [
            {"type": "file", "path": "src/main.py", "sha": "x"}], {}),
    }
    _patch_fe_github(monkeypatch, responses)
    monkeypatch.setattr(ev, "github_request", fe.github_request)

    res = fe.refresh_project({"project_id": "demo",
        "repository": "https://github.com/owner/demo.git"}, token="fake", dry_run=False)
    assert res["published"] is False
    assert res["status"] != "fresh"
    state = yaml.safe_load((tmp_path / "state" / "demo.yaml").read_text("utf-8"))
    assert state["freshness"]["semantic_freshness"] != "fresh"
    assert state["freshness"]["status"] != "fresh"


def test_no_evidence_does_not_publish_fresh_semantic_truth(monkeypatch, tmp_path):
    """manifest status="no_evidence" -> semantic_freshness="unknown", not fresh."""
    monkeypatch.setattr(fe, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(fe, "PROJECTS_YAML", tmp_path / "projects.yaml")
    monkeypatch.setattr(fe, "EVIDENCE_DIR", tmp_path / "evidence")
    (tmp_path / "state").mkdir()
    (tmp_path / "evidence").mkdir()
    (tmp_path / "projects.yaml").write_text(
        yaml.safe_dump({"projects": [{"project_id": "demo",
            "repository": "https://github.com/owner/demo.git"}]}), encoding="utf-8")
    original = _v2_state(pid="demo", purpose="Mission A", truth_head="h1", status="fresh")
    _seed_state(tmp_path, "demo", original)

    responses = {
        "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
        "/repos/owner/demo/commits/main": (200, {"sha": "h2"}, {}),
        "/repos/owner/demo/contents/?ref=main": (200, [
            {"type": "file", "path": "src/main.py", "sha": "x"}], {}),
    }
    _patch_fe_github(monkeypatch, responses)
    monkeypatch.setattr(ev, "github_request", fe.github_request)

    res = fe.refresh_project({"project_id": "demo",
        "repository": "https://github.com/owner/demo.git"}, token="fake", dry_run=False)
    assert res["published"] is False
    state = yaml.safe_load((tmp_path / "state" / "demo.yaml").read_text("utf-8"))
    assert state["freshness"]["semantic_freshness"] == "unknown"
    assert state["freshness"]["progress_freshness"] == "unknown"
    assert state["freshness"]["status"] == "unknown"


def test_failed_semantic_refresh_preserves_previous_verified_identity(monkeypatch, tmp_path):
    """Existing verified purpose preserved when refresh fails (evidence unavailable)."""
    monkeypatch.setattr(fe, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(fe, "PROJECTS_YAML", tmp_path / "projects.yaml")
    monkeypatch.setattr(fe, "EVIDENCE_DIR", tmp_path / "evidence")
    (tmp_path / "state").mkdir()
    (tmp_path / "evidence").mkdir()
    (tmp_path / "projects.yaml").write_text(
        yaml.safe_dump({"projects": [{"project_id": "demo",
            "repository": "https://github.com/owner/demo.git"}]}), encoding="utf-8")
    original = _v2_state(pid="demo", purpose="Mission A", truth_head="h1", status="fresh")
    _seed_state(tmp_path, "demo", original)

    responses = {
        "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
        "/repos/owner/demo/commits/main": (200, {"sha": "h2"}, {}),
        "/repos/owner/demo/contents/?ref=main": (200, [
            {"type": "file", "path": "src/main.py", "sha": "x"}], {}),
    }
    _patch_fe_github(monkeypatch, responses)
    monkeypatch.setattr(ev, "github_request", fe.github_request)

    fe.refresh_project({"project_id": "demo",
        "repository": "https://github.com/owner/demo.git"}, token="fake", dry_run=False)
    state = yaml.safe_load((tmp_path / "state" / "demo.yaml").read_text("utf-8"))
    # Previous verified identity preserved (not nulled).
    assert state["project_identity"]["purpose"] == "Mission A"
    # truth_built_from_head unchanged (not overwritten with remote_head or null).
    assert state["freshness"]["truth_built_from_head"] == "h1"


def test_unknown_semantic_freshness_prevents_aggregate_fresh():
    """source_freshness="fresh" but semantic_freshness="unknown" -> aggregate="unknown"."""
    assert fe._aggregate_freshness("fresh", "unknown", "fresh") == "unknown"
    assert fe._aggregate_freshness("fresh", "unknown", "stale") == "unknown"
    assert fe._aggregate_freshness("fresh", "unknown", "unknown") == "unknown"


def test_refresh_failure_never_publishes_partial_truth(monkeypatch, tmp_path):
    """Exception during refresh -> published=False, original restored, refresh_failed."""
    monkeypatch.setattr(fe, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(fe, "PROJECTS_YAML", tmp_path / "projects.yaml")
    monkeypatch.setattr(fe, "EVIDENCE_DIR", tmp_path / "evidence")
    (tmp_path / "state").mkdir()
    (tmp_path / "evidence").mkdir()
    (tmp_path / "projects.yaml").write_text(
        yaml.safe_dump({"projects": [{"project_id": "demo",
            "repository": "https://github.com/owner/demo.git"}]}), encoding="utf-8")
    original = _v2_state(pid="demo", purpose="Mission A", truth_head="h1", status="fresh")
    _seed_state(tmp_path, "demo", original)

    responses = {
        "/repos/owner/demo": (200, {"default_branch": "main"}, {}),
        "/repos/owner/demo/commits/main": (200, {"sha": "h2"}, {}),
        "/repos/owner/demo/contents/?ref=main": (200, [
            {"type": "file", "path": "AGENTS.md", "sha": "a"}], {}),
        "/repos/owner/demo/contents/AGENTS.md?ref=main": (
            200, {"content": _b64("## Mission\n\nMission A\n"),
                  "encoding": "base64", "sha": "a"}, {}),
    }
    _patch_fe_github(monkeypatch, responses)
    monkeypatch.setattr(ev, "github_request", fe.github_request)
    # Force an exception mid-refresh by breaking the progress engine import.
    import progress_engine as _pe
    monkeypatch.setattr(_pe, "compute_progress",
                        lambda manifest, state: (_ for _ in ()).throw(RuntimeError("boom")))

    res = fe.refresh_project({"project_id": "demo",
        "repository": "https://github.com/owner/demo.git"}, token="fake", dry_run=False)
    assert res["published"] is False
    assert res["status"] == "refresh_failed"
    assert res.get("restored") is True
    state = yaml.safe_load((tmp_path / "state" / "demo.yaml").read_text("utf-8"))
    # Original verified identity preserved.
    assert state["project_identity"]["purpose"] == "Mission A"
    assert state["freshness"]["status"] == "refresh_failed"


def test_aggregate_fresh_requires_all_three_gates_fresh():
    """All three fresh -> aggregate="fresh"; any one not fresh -> aggregate != "fresh"."""
    assert fe._aggregate_freshness("fresh", "fresh", "fresh") == "fresh"
    for combo in [
        ("stale", "fresh", "fresh"),
        ("fresh", "stale", "fresh"),
        ("fresh", "fresh", "stale"),
        ("unknown", "fresh", "fresh"),
        ("fresh", "unknown", "fresh"),
        ("fresh", "fresh", "unknown"),
        ("refresh_failed", "fresh", "fresh"),
        ("fresh", "refresh_failed", "fresh"),
        ("fresh", "fresh", "refresh_failed"),
    ]:
        assert fe._aggregate_freshness(*combo) != "fresh", combo


# ===========================================================================
# WO-OBSIDIAN-041 / F10: Progress VALUE != Progress FRESHNESS (P2)
# ===========================================================================

def test_progress_freshness_fresh_when_manifest_ok_even_with_null_estimate():
    """manifest status="ok" + estimate=None + confidence="unknown" -> "fresh".

    Progress FRESHNESS describes whether the computation was rebuilt from
    current evidence, NOT whether a percentage exists. A null estimate with
    confidence="unknown" is a FRESH computation (no denominator available),
    not stale. No percentage is fabricated.
    """
    manifest = {"status": "ok"}
    progress = {"estimate": None, "confidence": "unknown"}
    assert fe.progress_freshness_for(manifest, progress) == "fresh"
    # Sanity: the progress VALUE stays null (no fabrication).
    assert progress["estimate"] is None
    assert progress["confidence"] == "unknown"


def test_progress_freshness_unknown_when_manifest_not_ok():
    """manifest status="no_evidence" -> progress_freshness="unknown"."""
    manifest = {"status": "no_evidence"}
    progress = {"estimate": None, "confidence": "unknown"}
    assert fe.progress_freshness_for(manifest, progress) == "unknown"


def test_progress_freshness_fresh_with_valid_estimate():
    """manifest status="ok" + estimate=67 -> progress_freshness="fresh"."""
    manifest = {"status": "ok"}
    progress = {"estimate": 67, "confidence": "high"}
    assert fe.progress_freshness_for(manifest, progress) == "fresh"


def test_aggregate_fresh_with_null_progress_estimate():
    """A project with current evidence but no roadmap is FRESH (not stale).

    source="fresh", semantic="fresh", progress="fresh" (manifest ok, estimate
    null) -> aggregate="fresh". The progress VALUE being null doesn't make the
    project stale -- it means progress is genuinely unknown (no roadmap), but
    the freshness (evidence currency) is fresh.
    """
    assert fe._aggregate_freshness("fresh", "fresh", "fresh") == "fresh"
    # Confirm the underlying progress_freshness contract that produces this.
    manifest = {"status": "ok"}
    progress = {"estimate": None, "confidence": "unknown"}
    assert fe.progress_freshness_for(manifest, progress) == "fresh"


def test_aggregate_not_fresh_when_progress_unknown():
    """source="fresh", semantic="fresh", progress="unknown" -> aggregate="unknown".

    When the manifest is not ok, progress_freshness="unknown" and the
    aggregate cannot be "fresh" (unknown takes precedence).
    """
    assert fe._aggregate_freshness("fresh", "fresh", "unknown") == "unknown"
    # Confirm the underlying progress_freshness contract that produces this.
    manifest = {"status": "no_evidence"}
    progress = {"estimate": None, "confidence": "unknown"}
    assert fe.progress_freshness_for(manifest, progress) == "unknown"


# ===========================================================================
# Local-only (no remote) refresh regression (health-check 2026-08-19)
# ===========================================================================

def test_probe_local_only_includes_checked_at(monkeypatch, tmp_path):
    """probe_project's no-remote early return must include checked_at.

    The return previously omitted checked_at/default_branch, while
    refresh_project reads probe["checked_at"] unconditionally -> permanent
    refresh_failed (KeyError: 'checked_at') for every local-only project
    (observed on Adobe-Stock-Upload-Assistant).
    """
    monkeypatch.setattr(fe, "STATE_DIR", tmp_path / "state")
    (tmp_path / "state").mkdir()
    _seed_state(tmp_path, "localproj", _v2_state(pid="localproj"))

    probe = fe.probe_project({"project_id": "localproj", "repository": ""},
                             token=None)
    assert probe["status"] == "unknown"
    assert probe["reason"] == "no remote repository"
    assert probe["checked_at"]
    assert probe["remote_head"] is None
    assert probe["default_branch"] is None


def test_refresh_local_only_no_keyerror(monkeypatch, tmp_path):
    """Local-only refresh must fail gracefully (evidence unavailable /
    unknown), never crash with KeyError -> refresh_failed."""
    monkeypatch.setattr(fe, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(fe, "PROJECTS_YAML", tmp_path / "projects.yaml")
    monkeypatch.setattr(fe, "EVIDENCE_DIR", tmp_path / "evidence")
    (tmp_path / "state").mkdir()
    (tmp_path / "evidence").mkdir()
    (tmp_path / "projects.yaml").write_text(
        yaml.safe_dump({"projects": [{"project_id": "localproj",
                                      "repository": ""}]}),
        encoding="utf-8")
    _seed_state(tmp_path, "localproj", _v2_state(pid="localproj"))

    res = fe.refresh_project({"project_id": "localproj", "repository": ""},
                             token=None, dry_run=False)
    assert res["status"] != "refresh_failed"
    assert "KeyError" not in str(res)
    # The original state content must be preserved (no partial truth written).
    state = yaml.safe_load((tmp_path / "state" / "localproj.yaml").read_text("utf-8"))
    assert state["project_id"] == "localproj"
