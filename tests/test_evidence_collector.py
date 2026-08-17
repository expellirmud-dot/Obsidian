"""WO-OBSIDIAN-038 regression suite for evidence-backed truth ingestion.

Covers automation/evidence_collector.py. No real GitHub API calls are made;
tests monkeypatch github_request and use tmp_path for file writes.

Required test cases:
  1. test_evidence_reads_real_content_not_filename
  2. test_evidence_manifest_has_provenance
  3. test_truth_builder_fills_identity_from_evidence
  4. test_current_work_change_does_not_rewrite_mission
  5. test_mission_drift_detection_preserves_previous_identity
  6. test_insufficient_evidence_yields_unknown
  7. test_api_unavailable_no_fabrication
  8. test_classify_file_uses_content
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

import evidence_collector as ev  # noqa: E402


def _b64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


@pytest.fixture
def fake_contents_responses():
    """Simulated GitHub contents API responses for a repo with AGENTS.md + a
    work-order file. Keys are URL path fragments.
    """
    agents_md = (
        "# Project Alpha\n\n"
        "Project Alpha is a multi-agent execution platform.\n"
        "## Purpose\nSolve orchestration of long-running agents.\n"
    )
    wo_md = (
        "# WORK ORDER -- Feature B\n\n"
        "Current work: implement feature B this sprint.\n"
    )
    return {
        # repo metadata
        "/repos/owner/alpha": (200, {"default_branch": "main", "full_name": "owner/alpha"}, {}),
        # root listing
        "/repos/owner/alpha/contents/?ref=main": (200, [
            {"type": "file", "path": "AGENTS.md", "sha": "blob-agents"},
            {"type": "file", "path": "README.md", "sha": "blob-readme"},
            {"type": "dir", "name": "work_orders", "path": "work_orders"},
        ], {}),
        # work_orders dir listing
        "/repos/owner/alpha/contents/work_orders?ref=main": (200, [
            {"type": "file", "path": "work_orders/CURRENT_WORK_ORDER.md", "sha": "blob-wo"},
        ], {}),
        # file contents
        "/repos/owner/alpha/contents/AGENTS.md?ref=main": (
            200, {"content": _b64(agents_md), "encoding": "base64", "sha": "blob-agents"}, {}
        ),
        "/repos/owner/alpha/contents/work_orders/CURRENT_WORK_ORDER.md?ref=main": (
            200, {"content": _b64(wo_md), "encoding": "base64", "sha": "blob-wo"}, {}
        ),
        # README missing
        "/repos/owner/alpha/contents/README.md?ref=main": (404, None, {}),
    }


def _patch_gh(monkeypatch, responses):
    def fake(path, token):
        # Exact match first.
        if path in responses:
            return responses[path]
        # Then longest-key suffix match (avoid short keys shadowing longer paths).
        best = None
        best_len = -1
        for key, val in responses.items():
            if path.endswith(key) and len(key) > best_len:
                best = val
                best_len = len(key)
        if best is not None:
            return best
        return 404, None, {}
    monkeypatch.setattr(ev, "github_request", fake)


# ---------------------------------------------------------------------------
# 1. Evidence reads real content, not just filename
# ---------------------------------------------------------------------------

def test_evidence_reads_real_content_not_filename(monkeypatch, fake_contents_responses):
    """The collector reads file CONTENT and records an excerpt, not just names."""
    _patch_gh(monkeypatch, fake_contents_responses)
    project = {
        "project_id": "alpha",
        "repository": "https://github.com/owner/alpha.git",
    }
    manifest = ev.collect_evidence_for_project(project, token="fake")
    assert manifest["status"] == "ok"
    paths = [e["path"] for e in manifest["evidence"]]
    assert "AGENTS.md" in paths
    agents_ev = [e for e in manifest["evidence"] if e["path"] == "AGENTS.md"][0]
    # The excerpt must contain real content, not just the filename.
    assert "multi-agent execution platform" in agents_ev["content_excerpt"]
    assert agents_ev["category"] == "identity"


# ---------------------------------------------------------------------------
# 2. Evidence manifest has provenance
# ---------------------------------------------------------------------------

def test_evidence_manifest_has_provenance(monkeypatch, fake_contents_responses, tmp_path):
    """Every evidence item traces to repository, ref, blob_sha, path, classification, observed_at."""
    _patch_gh(monkeypatch, fake_contents_responses)
    monkeypatch.setattr(ev, "EVIDENCE_DIR", tmp_path / "evidence")
    project = {"project_id": "alpha", "repository": "https://github.com/owner/alpha.git"}
    manifest = ev.collect_evidence_for_project(project, token="fake")
    path = ev.write_manifest(manifest)
    loaded = yaml.safe_load(path.read_text("utf-8"))
    assert loaded["repository"] == "https://github.com/owner/alpha.git"
    assert loaded["tracked_ref"] == "main"
    assert loaded["observed_at"]
    for e in loaded["evidence"]:
        assert e["path"]
        assert e["ref"] == "main"
        assert e["blob_sha"]
        assert e["classification"] == "verified"
        assert e["observed_at"]
        assert e["category"] in ("identity", "current_execution", "roadmap",
                                 "completed_work", "blockers", "next_action", "manifest", "other")


# ---------------------------------------------------------------------------
# 3. Truth builder fills identity from evidence
# ---------------------------------------------------------------------------

def test_truth_builder_fills_identity_from_evidence(monkeypatch, fake_contents_responses, tmp_path, schema):
    """A state with null identity gets its purpose filled from AGENTS.md evidence."""
    _patch_gh(monkeypatch, fake_contents_responses)
    state_dir = tmp_path / "state"
    evidence_dir = tmp_path / "evidence"
    state_dir.mkdir()
    evidence_dir.mkdir()
    monkeypatch.setattr(ev, "STATE_DIR", state_dir)
    monkeypatch.setattr(ev, "EVIDENCE_DIR", evidence_dir)

    # Seed a v2 state with all-null identity (never set).
    state = {
        "schema_version": 2, "project_id": "alpha", "project_name": "Alpha",
        "github_repository_id": 999, "source_path": None,
        "repository": "https://github.com/owner/alpha.git", "branch": "main", "head": None,
        "knowledge_state": "needs-verification",
        "project_identity": {"purpose": None, "problem_statement": None, "intended_outcome": None,
            "primary_users": None, "success_definition": None, "scope": None, "non_goals": None,
            "identity_drift_detected": False, "previous_identity": None},
        "current_execution": {"lifecycle_phase": None, "current_goal": None, "current_work": None,
            "current_work_authority": {"path": None, "kind": None}, "current_work_evidence": "unknown",
            "last_completed": None, "blockers": None, "next_action": None},
        "freshness": {"status": "unknown", "tracked_ref": "main", "remote_head": None,
            "truth_built_from_head": None, "source_checked_at": None, "truth_built_at": None,
            "stale_since": None, "reason": None, "source_freshness": "unknown",
            "semantic_freshness": "unknown", "progress_freshness": "unknown"},
        "progress": {"scope": None, "method": None, "estimate": None, "range_min": None,
            "range_max": None, "confidence": "unknown", "completed": None, "active": None,
            "remaining": None, "basis": None},
        "github": {"ci_state": "unknown", "open_pr": None, "open_pr_count": None, "observed_at": None},
        "last_change": None, "evidence_classification": "unknown", "verified_at": None,
        "adapter_id": "discovery-onboard-v1",
    }
    (state_dir / "alpha.yaml").write_text(yaml.safe_dump(state), encoding="utf-8")

    manifest = ev.collect_evidence_for_project(
        {"project_id": "alpha", "repository": "https://github.com/owner/alpha.git"}, token="fake")
    res = ev.apply_truth_to_state("alpha", manifest, dry_run=False)
    assert res["applied"] is True
    assert res["drift"] is False  # initial onboarding, not drift

    new_state = yaml.safe_load((state_dir / "alpha.yaml").read_text("utf-8"))
    # Identity purpose filled from AGENTS.md heading.
    assert new_state["project_identity"]["purpose"] == "Project Alpha"
    assert new_state["project_identity"]["identity_drift_detected"] is False
    # current_execution filled from the work-order file.
    assert new_state["current_execution"]["current_work"] is not None
    assert new_state["current_execution"]["current_work_authority"]["kind"] == "work-order"
    assert new_state["knowledge_state"] == "verified"
    # Validate against v2 schema.
    assert list(Draft202012Validator(schema).iter_errors(new_state)) == []


# ---------------------------------------------------------------------------
# 4. Current Work change does NOT rewrite Mission
# ---------------------------------------------------------------------------

def test_current_work_change_does_not_rewrite_mission(monkeypatch, fake_contents_responses, tmp_path):
    """Changing the work-order content updates current_execution but NOT project_identity."""
    _patch_gh(monkeypatch, fake_contents_responses)
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    monkeypatch.setattr(ev, "STATE_DIR", state_dir)

    # Seed a state with an ESTABLISHED mission.
    state = {
        "schema_version": 2, "project_id": "alpha", "project_name": "Alpha",
        "github_repository_id": 999, "source_path": None,
        "repository": "https://github.com/owner/alpha.git", "branch": "main", "head": "h1",
        "knowledge_state": "verified",
        "project_identity": {"purpose": "Mission A", "problem_statement": None, "intended_outcome": None,
            "primary_users": None, "success_definition": None, "scope": None, "non_goals": None,
            "identity_drift_detected": False, "previous_identity": None},
        "current_execution": {"lifecycle_phase": "active", "current_goal": "Mission A",
            "current_work": "WO-1 doing A", "current_work_authority": {"path": "WO-1.md", "kind": "work-order"},
            "current_work_evidence": "verified", "last_completed": None, "blockers": None, "next_action": None},
        "freshness": {"status": "fresh", "tracked_ref": "main", "remote_head": "h1",
            "truth_built_from_head": "h1", "source_checked_at": "x", "truth_built_at": "x",
            "stale_since": None, "reason": None, "source_freshness": "fresh",
            "semantic_freshness": "fresh", "progress_freshness": "fresh"},
        "progress": {"scope": None, "method": None, "estimate": None, "range_min": None,
            "range_max": None, "confidence": "unknown", "completed": None, "active": None,
            "remaining": None, "basis": None},
        "github": {"ci_state": "unknown", "open_pr": None, "open_pr_count": None, "observed_at": None},
        "last_change": None, "evidence_classification": "verified", "verified_at": "x",
        "adapter_id": "x",
    }
    (state_dir / "alpha.yaml").write_text(yaml.safe_dump(state), encoding="utf-8")

    # Evidence now describes Feature B (a NEW work order) but the AGENTS.md
    # heading is still "Project Alpha" (same mission as "Mission A"? no --
    # "Mission A" vs "Project Alpha" differ substantially -> drift).
    # To test the "work change does not rewrite mission" rule cleanly, make
    # the AGENTS heading match the existing purpose so NO drift, and only the
    # work-order changes.
    responses = dict(fake_contents_responses)
    agents_md = "# Mission A\n\nProject Alpha is a multi-agent platform.\n"
    responses["/repos/owner/alpha/contents/AGENTS.md?ref=main"] = (
        200, {"content": _b64(agents_md), "encoding": "base64", "sha": "blob-agents"}, {})
    wo_md = "# WORK ORDER -- Feature B\n\nCurrent work: implement feature B.\n"
    responses["/repos/owner/alpha/contents/work_orders/CURRENT_WORK_ORDER.md?ref=main"] = (
        200, {"content": _b64(wo_md), "encoding": "base64", "sha": "blob-wo"}, {})
    _patch_gh(monkeypatch, responses)

    manifest = ev.collect_evidence_for_project(
        {"project_id": "alpha", "repository": "https://github.com/owner/alpha.git"}, token="fake")
    res = ev.apply_truth_to_state("alpha", manifest, dry_run=False)
    assert res["applied"] is True
    assert res["drift"] is False  # mission unchanged

    new_state = yaml.safe_load((state_dir / "alpha.yaml").read_text("utf-8"))
    # Mission preserved.
    assert new_state["project_identity"]["purpose"] == "Mission A"
    assert new_state["project_identity"]["identity_drift_detected"] is False
    # Current work updated to Feature B.
    assert "Feature B" in (new_state["current_execution"]["current_work"] or "")
    assert new_state["current_execution"]["current_work_authority"]["kind"] == "work-order"


# ---------------------------------------------------------------------------
# 5. Mission drift detection preserves previous identity
# ---------------------------------------------------------------------------

def test_mission_drift_detection_preserves_previous_identity(monkeypatch, fake_contents_responses, tmp_path):
    """When evidence indicates a genuinely different Mission, drift is flagged
    and the previous identity is preserved (not overwritten)."""
    _patch_gh(monkeypatch, fake_contents_responses)
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    monkeypatch.setattr(ev, "STATE_DIR", state_dir)

    state = {
        "schema_version": 2, "project_id": "alpha", "project_name": "Alpha",
        "github_repository_id": 999, "source_path": None,
        "repository": "https://github.com/owner/alpha.git", "branch": "main", "head": "h1",
        "knowledge_state": "verified",
        "project_identity": {"purpose": "Mission A", "problem_statement": None, "intended_outcome": None,
            "primary_users": None, "success_definition": None, "scope": None, "non_goals": None,
            "identity_drift_detected": False, "previous_identity": None},
        "current_execution": {"lifecycle_phase": "active", "current_goal": None, "current_work": None,
            "current_work_authority": {"path": None, "kind": None}, "current_work_evidence": "unknown",
            "last_completed": None, "blockers": None, "next_action": None},
        "freshness": {"status": "fresh", "tracked_ref": "main", "remote_head": "h1",
            "truth_built_from_head": "h1", "source_checked_at": "x", "truth_built_at": "x",
            "stale_since": None, "reason": None, "source_freshness": "fresh",
            "semantic_freshness": "fresh", "progress_freshness": "fresh"},
        "progress": {"scope": None, "method": None, "estimate": None, "range_min": None,
            "range_max": None, "confidence": "unknown", "completed": None, "active": None,
            "remaining": None, "basis": None},
        "github": {"ci_state": "unknown", "open_pr": None, "open_pr_count": None, "observed_at": None},
        "last_change": None, "evidence_classification": "verified", "verified_at": "x",
        "adapter_id": "x",
    }
    (state_dir / "alpha.yaml").write_text(yaml.safe_dump(state), encoding="utf-8")

    # Evidence now shows a DIFFERENT mission ("Completely Different Project").
    responses = dict(fake_contents_responses)
    agents_md = "# Completely Different Project\n\nNow a data pipeline.\n"
    responses["/repos/owner/alpha/contents/AGENTS.md?ref=main"] = (
        200, {"content": _b64(agents_md), "encoding": "base64", "sha": "blob-agents"}, {})
    _patch_gh(monkeypatch, responses)

    manifest = ev.collect_evidence_for_project(
        {"project_id": "alpha", "repository": "https://github.com/owner/alpha.git"}, token="fake")
    res = ev.apply_truth_to_state("alpha", manifest, dry_run=False)
    assert res["applied"] is True
    assert res["drift"] is True

    new_state = yaml.safe_load((state_dir / "alpha.yaml").read_text("utf-8"))
    # The existing purpose is PRESERVED (not overwritten with the new mission).
    assert new_state["project_identity"]["purpose"] == "Mission A"
    assert new_state["project_identity"]["identity_drift_detected"] is True
    # The previous identity snapshot is recorded.
    prev = new_state["project_identity"]["previous_identity"]
    assert isinstance(prev, list) and len(prev) == 1
    assert prev[0]["purpose"] == "Mission A"


# ---------------------------------------------------------------------------
# 6. Insufficient evidence yields unknown
# ---------------------------------------------------------------------------

def test_insufficient_evidence_yields_unknown(monkeypatch, tmp_path):
    """A repo with no readable authority files yields no evidence and unknown identity."""
    responses = {
        "/repos/owner/empty": (200, {"default_branch": "main"}, {}),
        "/repos/owner/empty/contents/?ref=main": (200, [
            {"type": "file", "path": "src/main.py", "sha": "x"},
        ], {}),
    }
    _patch_gh(monkeypatch, responses)
    project = {"project_id": "empty", "repository": "https://github.com/owner/empty.git"}
    manifest = ev.collect_evidence_for_project(project, token="fake")
    assert manifest["status"] == "no_evidence"
    assert manifest["evidence"] == []
    identity = ev.build_identity_from_evidence(manifest)
    # All identity fields remain null.
    assert identity["purpose"] is None
    assert identity["problem_statement"] is None


# ---------------------------------------------------------------------------
# 7. API unavailable -> no fabrication
# ---------------------------------------------------------------------------

def test_api_unavailable_no_fabrication(monkeypatch):
    """When GitHub is unreachable, the manifest records the failure and no evidence is fabricated."""
    def fake(path, token):
        return -1, None, {"_error": "network"}
    monkeypatch.setattr(ev, "github_request", fake)
    project = {"project_id": "alpha", "repository": "https://github.com/owner/alpha.git"}
    manifest = ev.collect_evidence_for_project(project, token="fake")
    assert manifest["status"] == "repo_not_accessible"
    assert manifest["evidence"] == []
    # No token -> no_token (fail-safe).
    manifest2 = ev.collect_evidence_for_project(project, token=None)
    assert manifest2["status"] == "no_token"


# ---------------------------------------------------------------------------
# 8. classify_file uses content (not filename alone)
# ---------------------------------------------------------------------------

def test_classify_file_uses_content():
    """A file with a generic name but work-order content is classified by content."""
    cat, kind = ev.classify_file("notes.md", "# WORK ORDER -- X\n\nCurrent work: do X.\n")
    assert cat == "current_execution"
    # A README with roadmap content falls through to identity by name.
    cat2, kind2 = ev.classify_file("README.md", "# Project\n\nA project.\n")
    assert cat2 == "identity"
    # AGENTS.md by name.
    cat3, kind3 = ev.classify_file("AGENTS.md", "whatever")
    assert cat3 == "identity" and kind3 == "agents"
