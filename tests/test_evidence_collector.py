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
            "identity_drift_detected": False, "previous_identity": None, "candidate_identity": None, "candidate_identity_provenance": None},
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
    # WO-OBSIDIAN-041 F1: purpose is derived ONLY from explicit Purpose/Mission
    # text, not from the bare H1 heading. AGENTS.md has a "## Purpose" section
    # followed by a descriptive sentence -> that sentence is the purpose.
    assert new_state["project_identity"]["purpose"] == "Solve orchestration of long-running agents."
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
            "identity_drift_detected": False, "previous_identity": None, "candidate_identity": None, "candidate_identity_provenance": None},
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
            "identity_drift_detected": False, "previous_identity": None, "candidate_identity": None, "candidate_identity_provenance": None},
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

    # Evidence now shows a DIFFERENT mission. WO-OBSIDIAN-041 F1: a bare heading
    # is no longer a purpose, so the candidate mission must come from an EXPLICIT
    # "## Purpose" section to trigger drift detection.
    responses = dict(fake_contents_responses)
    agents_md = "# Completely Different Project\n\n## Purpose\nA data pipeline for streaming analytics.\n"
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
    # F4: the candidate mission + its evidence provenance are recorded.
    assert new_state["project_identity"]["candidate_identity"] == {
        "purpose": "A data pipeline for streaming analytics."}
    prov = new_state["project_identity"]["candidate_identity_provenance"]
    assert prov is not None
    assert prov["path"] == "AGENTS.md"
    assert prov["ref"] == "main"
    assert prov["blob_sha"] == "blob-agents"
    assert prov["observed_at"]


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


# ---------------------------------------------------------------------------
# 9. WO-OBSIDIAN-041 F1: a project title alone is NOT a mission
# ---------------------------------------------------------------------------

def _null_identity():
    return {"purpose": None, "problem_statement": None, "intended_outcome": None,
            "primary_users": None, "success_definition": None, "scope": None, "non_goals": None,
            "identity_drift_detected": False, "previous_identity": None,
            "candidate_identity": None, "candidate_identity_provenance": None}


def _seed_state(tmp_path, monkeypatch, *, purpose=None, knowledge_state="needs-verification"):
    """Write a minimal v2 state file under a tmp STATE_DIR and return its path."""
    state_dir = tmp_path / "state"
    state_dir.mkdir(exist_ok=True)
    monkeypatch.setattr(ev, "STATE_DIR", state_dir)
    state = {
        "schema_version": 2, "project_id": "alpha", "project_name": "Alpha",
        "github_repository_id": 999, "source_path": None,
        "repository": "https://github.com/owner/alpha.git", "branch": "main", "head": "h1",
        "knowledge_state": knowledge_state,
        "project_identity": _null_identity() | ({"purpose": purpose} if purpose else {}),
        "current_execution": {"lifecycle_phase": None, "current_goal": None, "current_work": None,
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
        "last_change": None, "evidence_classification": "unknown", "verified_at": None,
        "adapter_id": "x",
    }
    (state_dir / "alpha.yaml").write_text(yaml.safe_dump(state), encoding="utf-8")
    return state_dir


def _identity_only_responses(agents_md):
    """A fake response set with only an AGENTS.md identity file (no work order)."""
    return {
        "/repos/owner/alpha": (200, {"default_branch": "main"}, {}),
        "/repos/owner/alpha/contents/?ref=main": (200, [
            {"type": "file", "path": "AGENTS.md", "sha": "blob-agents"},
        ], {}),
        "/repos/owner/alpha/contents/AGENTS.md?ref=main": (
            200, {"content": _b64(agents_md), "encoding": "base64", "sha": "blob-agents"}, {}),
    }


def test_project_title_alone_does_not_verify_mission(monkeypatch, tmp_path):
    """A README/AGENTS with only a bare H1 title (no explicit purpose section) must
    NOT be treated as a mission: purpose stays None and knowledge_state is NOT
    promoted to verified (WO-OBSIDIAN-041 F1)."""
    _seed_state(tmp_path, monkeypatch, knowledge_state="needs-verification")
    _patch_gh(monkeypatch, _identity_only_responses("# Thai STT App\n"))

    manifest = ev.collect_evidence_for_project(
        {"project_id": "alpha", "repository": "https://github.com/owner/alpha.git"}, token="fake")
    identity = ev.build_identity_from_evidence(manifest)
    assert identity["purpose"] is None

    res = ev.apply_truth_to_state("alpha", manifest, dry_run=False)
    assert res["applied"] is True
    new_state = yaml.safe_load((ev.STATE_DIR / "alpha.yaml").read_text("utf-8"))
    assert new_state["project_identity"]["purpose"] is None
    # knowledge_state must NOT be promoted to "verified" without a real purpose.
    assert new_state["knowledge_state"] != "verified"


def test_repository_name_alone_does_not_verify_mission(monkeypatch, tmp_path):
    """A repository/project name must never be used as the purpose (F1). Even when
    the only text is the project name repeated, purpose stays None."""
    _seed_state(tmp_path, monkeypatch, knowledge_state="needs-verification")
    # The body text is just the project name -- not an explicit purpose statement.
    _patch_gh(monkeypatch, _identity_only_responses("# alpha\n\nalpha\n"))

    manifest = ev.collect_evidence_for_project(
        {"project_id": "alpha", "repository": "https://github.com/owner/alpha.git"}, token="fake")
    identity = ev.build_identity_from_evidence(manifest)
    assert identity["purpose"] is None
    res = ev.apply_truth_to_state("alpha", manifest, dry_run=False)
    new_state = yaml.safe_load((ev.STATE_DIR / "alpha.yaml").read_text("utf-8"))
    assert new_state["project_identity"]["purpose"] is None
    assert new_state["knowledge_state"] != "verified"


def test_explicit_purpose_text_can_verify_mission(monkeypatch, tmp_path, schema):
    """A README with an explicit "## Purpose" section followed by descriptive text
    yields that text as the purpose and verifies the mission (F1)."""
    _seed_state(tmp_path, monkeypatch, knowledge_state="needs-verification")
    agents_md = "# Thai STT App\n\n## Purpose\nA speech-to-text app for Thai language.\n"
    _patch_gh(monkeypatch, _identity_only_responses(agents_md))

    manifest = ev.collect_evidence_for_project(
        {"project_id": "alpha", "repository": "https://github.com/owner/alpha.git"}, token="fake")
    identity = ev.build_identity_from_evidence(manifest)
    assert identity["purpose"] == "A speech-to-text app for Thai language."

    res = ev.apply_truth_to_state("alpha", manifest, dry_run=False)
    assert res["applied"] is True
    new_state = yaml.safe_load((ev.STATE_DIR / "alpha.yaml").read_text("utf-8"))
    assert new_state["project_identity"]["purpose"] == "A speech-to-text app for Thai language."
    assert new_state["knowledge_state"] == "verified"
    assert list(Draft202012Validator(schema).iter_errors(new_state)) == []


def test_current_work_does_not_become_project_mission(monkeypatch, tmp_path):
    """A work-order file changes current_execution but project_identity.purpose is
    unchanged (Current Work != Mission). Variant: identity evidence has no explicit
    purpose, so purpose must remain None even though a work order is present."""
    _seed_state(tmp_path, monkeypatch, purpose=None, knowledge_state="needs-verification")
    responses = {
        "/repos/owner/alpha": (200, {"default_branch": "main"}, {}),
        "/repos/owner/alpha/contents/?ref=main": (200, [
            {"type": "file", "path": "AGENTS.md", "sha": "blob-agents"},
            {"type": "file", "path": "work_orders/CURRENT_WORK_ORDER.md", "sha": "blob-wo"},
        ], {}),
        "/repos/owner/alpha/contents/AGENTS.md?ref=main": (
            200, {"content": _b64("# Thai STT App\n"), "encoding": "base64", "sha": "blob-agents"}, {}),
        "/repos/owner/alpha/contents/work_orders/CURRENT_WORK_ORDER.md?ref=main": (
            200, {"content": _b64("# WORK ORDER -- X\n\nCurrent work: implement X.\n"),
                  "encoding": "base64", "sha": "blob-wo"}, {}),
    }
    _patch_gh(monkeypatch, responses)

    manifest = ev.collect_evidence_for_project(
        {"project_id": "alpha", "repository": "https://github.com/owner/alpha.git"}, token="fake")
    res = ev.apply_truth_to_state("alpha", manifest, dry_run=False)
    new_state = yaml.safe_load((ev.STATE_DIR / "alpha.yaml").read_text("utf-8"))
    # current_work updated from the work order...
    assert new_state["current_execution"]["current_work"] is not None
    # ...but the mission is NOT seeded from the work order or the bare title.
    assert new_state["project_identity"]["purpose"] is None


# ---------------------------------------------------------------------------
# 10. WO-OBSIDIAN-041 F4: mission drift provenance
# ---------------------------------------------------------------------------

def _seed_verified_state(tmp_path, monkeypatch, purpose):
    """Seed a state with an ESTABLISHED (verified) mission for drift tests."""
    return _seed_state(tmp_path, monkeypatch, purpose=purpose, knowledge_state="verified")


def test_mission_drift_preserves_old_identity(monkeypatch, tmp_path):
    """On drift, the existing purpose is preserved (not overwritten)."""
    _seed_verified_state(tmp_path, monkeypatch, "Mission A")
    agents_md = "# Other\n\n## Purpose\nA completely different streaming pipeline.\n"
    _patch_gh(monkeypatch, _identity_only_responses(agents_md))

    manifest = ev.collect_evidence_for_project(
        {"project_id": "alpha", "repository": "https://github.com/owner/alpha.git"}, token="fake")
    res = ev.apply_truth_to_state("alpha", manifest, dry_run=False)
    assert res["drift"] is True
    new_state = yaml.safe_load((ev.STATE_DIR / "alpha.yaml").read_text("utf-8"))
    assert new_state["project_identity"]["purpose"] == "Mission A"


def test_mission_drift_records_candidate_identity(monkeypatch, tmp_path):
    """On drift, candidate_identity.purpose equals the candidate mission (F4)."""
    _seed_verified_state(tmp_path, monkeypatch, "Mission A")
    candidate = "A completely different streaming pipeline."
    agents_md = f"# Other\n\n## Purpose\n{candidate}\n"
    _patch_gh(monkeypatch, _identity_only_responses(agents_md))

    manifest = ev.collect_evidence_for_project(
        {"project_id": "alpha", "repository": "https://github.com/owner/alpha.git"}, token="fake")
    ev.apply_truth_to_state("alpha", manifest, dry_run=False)
    new_state = yaml.safe_load((ev.STATE_DIR / "alpha.yaml").read_text("utf-8"))
    assert new_state["project_identity"]["candidate_identity"] == {"purpose": candidate}


def test_mission_drift_candidate_has_evidence_provenance(monkeypatch, tmp_path):
    """On drift, candidate_identity_provenance records path/ref/blob_sha/observed_at
    of the evidence item that produced the candidate mission (F4)."""
    _seed_verified_state(tmp_path, monkeypatch, "Mission A")
    agents_md = "# Other\n\n## Purpose\nA different mission entirely.\n"
    _patch_gh(monkeypatch, _identity_only_responses(agents_md))

    manifest = ev.collect_evidence_for_project(
        {"project_id": "alpha", "repository": "https://github.com/owner/alpha.git"}, token="fake")
    ev.apply_truth_to_state("alpha", manifest, dry_run=False)
    new_state = yaml.safe_load((ev.STATE_DIR / "alpha.yaml").read_text("utf-8"))
    prov = new_state["project_identity"]["candidate_identity_provenance"]
    assert prov is not None
    assert prov["path"] == "AGENTS.md"
    assert prov["ref"] == "main"
    assert prov["blob_sha"] == "blob-agents"
    assert prov["observed_at"]  # non-empty ISO timestamp


def test_mission_drift_does_not_silently_overwrite_verified_identity(monkeypatch, tmp_path):
    """On drift, the verified purpose is unchanged AND identity_drift_detected is
    True (the candidate is recorded but NOT applied)."""
    _seed_verified_state(tmp_path, monkeypatch, "Mission A")
    agents_md = "# Other\n\n## Purpose\nA different mission entirely.\n"
    _patch_gh(monkeypatch, _identity_only_responses(agents_md))

    manifest = ev.collect_evidence_for_project(
        {"project_id": "alpha", "repository": "https://github.com/owner/alpha.git"}, token="fake")
    res = ev.apply_truth_to_state("alpha", manifest, dry_run=False)
    new_state = yaml.safe_load((ev.STATE_DIR / "alpha.yaml").read_text("utf-8"))
    assert new_state["project_identity"]["purpose"] == "Mission A"
    assert new_state["project_identity"]["identity_drift_detected"] is True
    assert res["drift"] is True
