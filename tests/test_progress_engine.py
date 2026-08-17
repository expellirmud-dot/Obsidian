"""WO-OBSIDIAN-039 regression suite for the progress + next-action engine.

Covers automation/progress_engine.py. No real GitHub API calls; tests use
in-memory manifests and tmp_path for state writes.

Required test cases:
  1. test_weighted_progress_calculation
  2. test_unweighted_bounded_milestones
  3. test_missing_denominator_progress_unknown
  4. test_next_action_from_explicit_authority
  5. test_no_authority_next_action_unknown
  6. test_next_action_from_blocker
  7. test_next_action_from_first_incomplete_milestone
  8. test_progress_engine_is_deterministic
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

import progress_engine as pe  # noqa: E402


def _manifest_with_roadmap(roadmap_content: str) -> dict:
    return {
        "project_id": "demo",
        "evidence": [
            {
                "path": "ROADMAP.md",
                "category": "roadmap",
                "kind": "roadmap",
                "content_excerpt": roadmap_content,
            }
        ],
    }


def _state_with_execution(next_action=None, blockers=None) -> dict:
    return {
        "schema_version": 2, "project_id": "demo", "project_name": "Demo",
        "github_repository_id": None, "source_path": None, "repository": None,
        "branch": "main", "head": None, "knowledge_state": "needs-verification",
        "project_identity": {"purpose": None, "problem_statement": None, "intended_outcome": None,
            "primary_users": None, "success_definition": None, "scope": None, "non_goals": None,
            "identity_drift_detected": False, "previous_identity": None},
        "current_execution": {"lifecycle_phase": "active", "current_goal": None, "current_work": None,
            "current_work_authority": {"path": None, "kind": None}, "current_work_evidence": "unknown",
            "last_completed": None, "blockers": blockers, "next_action": next_action},
        "freshness": {"status": "unknown", "tracked_ref": "main", "remote_head": None,
            "truth_built_from_head": None, "source_checked_at": None, "truth_built_at": None,
            "stale_since": None, "reason": None, "source_freshness": "unknown",
            "semantic_freshness": "unknown", "progress_freshness": "unknown"},
        "progress": {"scope": None, "method": None, "estimate": None, "range_min": None,
            "range_max": None, "confidence": "unknown", "completed": None, "active": None,
            "remaining": None, "basis": None},
        "github": {"ci_state": "unknown", "open_pr": None, "open_pr_count": None, "observed_at": None},
        "last_change": None, "evidence_classification": "unknown", "verified_at": None,
        "adapter_id": "x",
    }


# ---------------------------------------------------------------------------
# 1. Weighted progress calculation
# ---------------------------------------------------------------------------

def test_weighted_progress_calculation():
    """Explicit weights produce a weighted estimate from milestone evidence."""
    roadmap = (
        "- [x] (3) M1: Foundation\n"
        "- [x] (1) M2: Tests\n"
        "- [ ] (6) M3: Live run\n"
    )
    manifest = _manifest_with_roadmap(roadmap)
    progress = pe.compute_progress(manifest, _state_with_execution())
    assert progress["method"] == "weighted_milestones"
    # done weight = 3+1 = 4; total = 3+1+6 = 10 -> 40%
    assert progress["estimate"] == 40
    assert progress["range_min"] == 35
    assert progress["range_max"] == 45
    assert progress["confidence"] == "medium"
    assert progress["completed"] == 2
    assert progress["remaining"] == 1
    assert "4/10 weight units" in progress["basis"]


# ---------------------------------------------------------------------------
# 2. Unweighted bounded milestones
# ---------------------------------------------------------------------------

def test_unweighted_bounded_milestones():
    """Milestones without explicit weights use equal-weight bounded method."""
    roadmap = (
        "- [x] M1: Foundation\n"
        "- [x] M2: Tests\n"
        "- [x] M3: Docs\n"
        "- [ ] M4: Live run\n"
    )
    manifest = _manifest_with_roadmap(roadmap)
    progress = pe.compute_progress(manifest, _state_with_execution())
    assert progress["method"] == "bounded_milestones"
    # 3/4 = 75%
    assert progress["estimate"] == 75
    assert progress["completed"] == 3
    assert progress["remaining"] == 1
    assert "3/4 milestones" in progress["basis"]


# ---------------------------------------------------------------------------
# 3. Missing denominator -> progress UNKNOWN
# ---------------------------------------------------------------------------

def test_missing_denominator_progress_unknown():
    """No roadmap/milestone evidence -> estimate=null, confidence=unknown."""
    manifest = {"evidence": []}
    progress = pe.compute_progress(manifest, _state_with_execution())
    assert progress["estimate"] is None
    assert progress["range_min"] is None
    assert progress["range_max"] is None
    assert progress["confidence"] == "unknown"
    assert progress["method"] is None
    assert "denominator" in progress["basis"]


# ---------------------------------------------------------------------------
# 4. Next action from explicit authority
# ---------------------------------------------------------------------------

def test_next_action_from_explicit_authority():
    """An existing verified next_action from authority is preserved."""
    state = _state_with_execution(next_action="Execute WO-03 live run")
    manifest = {"evidence": []}
    na = pe.derive_next_action(manifest, state)
    assert na == "Execute WO-03 live run"


# ---------------------------------------------------------------------------
# 5. No authority -> next_action unknown (None)
# ---------------------------------------------------------------------------

def test_no_authority_next_action_unknown():
    """With no authority, no blocker, and no roadmap -> next_action is None (unknown)."""
    state = _state_with_execution(next_action=None, blockers=None)
    manifest = {"evidence": []}
    na = pe.derive_next_action(manifest, state)
    assert na is None


# ---------------------------------------------------------------------------
# 6. Next action from blocker
# ---------------------------------------------------------------------------

def test_next_action_from_blocker():
    """When there is no explicit next_action but a blocker exists, resolve it."""
    state = _state_with_execution(next_action=None, blockers="Owner Go required")
    manifest = {"evidence": []}
    na = pe.derive_next_action(manifest, state)
    assert na is not None
    assert "Owner Go required" in na
    assert na.startswith("Resolve blocker:")


# ---------------------------------------------------------------------------
# 7. Next action from first incomplete milestone
# ---------------------------------------------------------------------------

def test_next_action_from_first_incomplete_milestone():
    """With no next_action/blocker, the first incomplete milestone is the next action."""
    roadmap = (
        "- [x] M1: Foundation\n"
        "- [ ] M2: Live test\n"
        "- [ ] M3: Ship\n"
    )
    manifest = _manifest_with_roadmap(roadmap)
    state = _state_with_execution(next_action=None, blockers=None)
    na = pe.derive_next_action(manifest, state)
    assert na is not None
    assert "M2: Live test" in na
    assert "ROADMAP.md" in na


# ---------------------------------------------------------------------------
# 8. Progress engine is deterministic
# ---------------------------------------------------------------------------

def test_progress_engine_is_deterministic():
    """Identical inputs produce identical progress + next_action outputs."""
    roadmap = "- [x] (2) A\n- [ ] (3) B\n"
    manifest = _manifest_with_roadmap(roadmap)
    state = _state_with_execution()
    p1 = pe.compute_progress(manifest, state)
    p2 = pe.compute_progress(manifest, state)
    assert p1 == p2
    # 2/5 = 40%
    assert p1["estimate"] == 40


# ---------------------------------------------------------------------------
# 9. Write path: apply_progress_to_state round-trip + schema rejection
# ---------------------------------------------------------------------------

def test_apply_progress_writes_state_and_validates(monkeypatch, tmp_path, schema):
    """apply_progress_to_state writes a schema-valid state with the progress block."""
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    monkeypatch.setattr(pe, "STATE_DIR", state_dir)
    state = _state_with_execution(next_action="Execute WO-03")
    (state_dir / "demo.yaml").write_text(yaml.safe_dump(state), encoding="utf-8")

    manifest = _manifest_with_roadmap("- [x] (3) M1\n- [ ] (7) M2\n")
    res = pe.apply_progress_to_state("demo", manifest, dry_run=False)
    assert res["applied"] is True
    assert res["estimate"] == 30  # 3/10
    assert res["method"] == "weighted_milestones"

    new_state = yaml.safe_load((state_dir / "demo.yaml").read_text("utf-8"))
    assert new_state["progress"]["estimate"] == 30
    assert new_state["current_execution"]["next_action"] == "Execute WO-03"
    assert list(Draft202012Validator(schema).iter_errors(new_state)) == []


def test_apply_progress_dry_run_does_not_write(monkeypatch, tmp_path):
    """Dry-run does not modify the state file."""
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    monkeypatch.setattr(pe, "STATE_DIR", state_dir)
    state = _state_with_execution()
    (state_dir / "demo.yaml").write_text(yaml.safe_dump(state), encoding="utf-8")
    before = (state_dir / "demo.yaml").read_text("utf-8")

    manifest = _manifest_with_roadmap("- [x] M1\n- [ ] M2\n")
    res = pe.apply_progress_to_state("demo", manifest, dry_run=True)
    assert res["applied"] is True
    assert res["dry_run"] is True
    after = (state_dir / "demo.yaml").read_text("utf-8")
    assert before == after
