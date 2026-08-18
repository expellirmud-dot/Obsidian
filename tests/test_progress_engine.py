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


def _manifest_with_roadmap(
    roadmap_content: str,
    *,
    truncated: bool | None = None,
    content_length: int | None = None,
) -> dict:
    """Build a manifest with a single roadmap evidence item.

    ``truncated`` / ``content_length`` mirror the fields the evidence collector
    (WO-OBSIDIAN-041) adds to each evidence item. Pass them explicitly to model
    truncated vs. complete excerpts; omit both to model an old manifest (the
    engine then falls back to the ``len(excerpt) >= 500`` heuristic).
    """
    ev = {
        "path": "ROADMAP.md",
        "category": "roadmap",
        "kind": "roadmap",
        "content_excerpt": roadmap_content,
    }
    if truncated is not None:
        ev["truncated"] = truncated
    if content_length is not None:
        ev["content_length"] = content_length
    return {
        "project_id": "demo",
        "evidence": [ev],
    }


def _state_with_execution(next_action=None, blockers=None) -> dict:
    return {
        "schema_version": 2, "project_id": "demo", "project_name": "Demo",
        "github_repository_id": None, "source_path": None, "repository": None,
        "branch": "main", "head": None, "knowledge_state": "needs-verification",
        "project_identity": {"purpose": None, "problem_statement": None, "intended_outcome": None,
            "primary_users": None, "success_definition": None, "scope": None, "non_goals": None,
            "identity_drift_detected": False, "previous_identity": None, "candidate_identity": None, "candidate_identity_provenance": None},
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
    manifest = _manifest_with_roadmap(roadmap, truncated=False)
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
    manifest = _manifest_with_roadmap(roadmap, truncated=False)
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
    manifest = _manifest_with_roadmap(roadmap, truncated=False)
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

    manifest = _manifest_with_roadmap("- [x] (3) M1\n- [ ] (7) M2\n", truncated=False)
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

    manifest = _manifest_with_roadmap("- [x] M1\n- [ ] M2\n", truncated=False)
    res = pe.apply_progress_to_state("demo", manifest, dry_run=True)
    assert res["applied"] is True
    assert res["dry_run"] is True
    after = (state_dir / "demo.yaml").read_text("utf-8")
    assert before == after


# ---------------------------------------------------------------------------
# 10. WO-OBSIDIAN-041 -- truncation correctness (no false percentages)
# ---------------------------------------------------------------------------

def test_truncated_roadmap_does_not_produce_false_percentage():
    """A truncated roadmap (explicit flag) -> UNKNOWN, never a partial %.

    Regression for the bug where a roadmap whose checklist extended past the
    500-char excerpt cap silently lost later milestones, producing a false
    percentage from a partial denominator.
    """
    # The excerpt shows 2/2 done, but the full roadmap was longer (truncated),
    # so the true denominator is unknown -> must NOT report 100%.
    roadmap = "- [x] M1: Foundation - [x] M2: Tests"
    manifest = _manifest_with_roadmap(roadmap, truncated=True)
    progress = pe.compute_progress(manifest, _state_with_execution())
    assert progress["estimate"] is None
    assert progress["confidence"] == "unknown"
    assert progress["method"] is None
    assert "truncated" in progress["basis"]
    assert "incomplete denominator" in progress["basis"]


def test_truncated_roadmap_via_content_length_does_not_produce_false_percentage():
    """content_length > 500 (full content longer than the cap) -> UNKNOWN."""
    roadmap = "- [x] M1 - [ ] M2"
    manifest = _manifest_with_roadmap(roadmap, content_length=1200)
    progress = pe.compute_progress(manifest, _state_with_execution())
    assert progress["estimate"] is None
    assert progress["confidence"] == "unknown"
    assert progress["method"] is None
    assert "truncated" in progress["basis"]


def test_truncated_roadmap_old_manifest_fallback_does_not_produce_false_percentage():
    """Old manifest (no fields) with an excerpt at the 500-char cap -> UNKNOWN.

    Models a legacy manifest produced before the evidence collector added the
    ``truncated`` / ``content_length`` fields: the engine falls back to the
    ``len(excerpt) >= 500`` heuristic and refuses to fabricate a percentage.
    """
    # 500-char excerpt that looks like 1/2 done but is actually capped.
    roadmap = "- [x] M1 " + "x" * 491
    assert len(roadmap) >= 500
    manifest = _manifest_with_roadmap(roadmap)  # no truncated/content_length
    progress = pe.compute_progress(manifest, _state_with_execution())
    assert progress["estimate"] is None
    assert progress["confidence"] == "unknown"
    assert progress["method"] is None
    assert "truncated" in progress["basis"]


def test_complete_bounded_roadmap_produces_deterministic_percentage():
    """A complete (not truncated) roadmap, 3 milestones / 2 done -> 67%."""
    roadmap = (
        "- [x] M1: Foundation\n"
        "- [x] M2: Tests\n"
        "- [ ] M3: Live run\n"
    )
    manifest = _manifest_with_roadmap(roadmap, truncated=False)
    progress = pe.compute_progress(manifest, _state_with_execution())
    assert progress["method"] == "bounded_milestones"
    assert progress["estimate"] == 67  # round(100 * 2 / 3)
    assert progress["completed"] == 2
    assert progress["remaining"] == 1
    assert progress["confidence"] == "medium"
    # Deterministic: same inputs -> same outputs.
    again = pe.compute_progress(manifest, _state_with_execution())
    assert again == progress


def test_complete_bounded_roadmap_via_content_length_produces_percentage():
    """content_length <= 500 (full content kept) is NOT truncated -> computes."""
    roadmap = "- [x] M1\n- [x] M2\n- [ ] M3\n"
    manifest = _manifest_with_roadmap(roadmap, content_length=len(roadmap))
    progress = pe.compute_progress(manifest, _state_with_execution())
    assert progress["method"] == "bounded_milestones"
    assert progress["estimate"] == 67


def test_missing_denominator_is_unknown():
    """No roadmap evidence at all -> UNKNOWN."""
    manifest = {"evidence": []}
    progress = pe.compute_progress(manifest, _state_with_execution())
    assert progress["estimate"] is None
    assert progress["confidence"] == "unknown"
    assert progress["method"] is None


def test_non_roadmap_evidence_only_is_unknown():
    """Evidence present but none in the roadmap category -> UNKNOWN."""
    manifest = {
        "evidence": [
            {"category": "completed_work", "content_excerpt": "- [x] something", "truncated": False},
            {"category": "identity", "content_excerpt": "# Project", "truncated": False},
        ]
    }
    progress = pe.compute_progress(manifest, _state_with_execution())
    assert progress["estimate"] is None
    assert progress["confidence"] == "unknown"
    assert progress["method"] is None


def test_any_one_truncated_roadmap_item_poisons_the_denominator():
    """If ANY roadmap evidence item is truncated, the whole denominator is suspect."""
    manifest = {
        "evidence": [
            {"path": "ROADMAP.md", "category": "roadmap",
             "content_excerpt": "- [x] M1\n- [ ] M2\n", "truncated": False},
            {"path": "ROADMAP2.md", "category": "roadmap",
             "content_excerpt": "- [x] M3", "truncated": True},
        ]
    }
    progress = pe.compute_progress(manifest, _state_with_execution())
    assert progress["estimate"] is None
    assert progress["confidence"] == "unknown"
    assert "truncated" in progress["basis"]


# ---------------------------------------------------------------------------
# 11. WO-OBSIDIAN-041 -- newline-stripped excerpt parsing (finditer fallback)
# ---------------------------------------------------------------------------

def test_newline_stripped_excerpt_parses_all_milestones():
    """A newline-stripped excerpt with multiple markers parses all milestones.

    The evidence collector flattens content to a single line; the line-anchored
    regex would collapse several milestones into one. The finditer fallback
    recovers them all. The excerpt is NOT truncated, so a percentage is still
    computed from the complete denominator.
    """
    flat = "- [x] M1: Foundation - [x] M2: Tests - [ ] M3: Live run"
    assert "\n" not in flat
    ms = pe.parse_milestones_from_content(flat)
    assert len(ms) == 3
    assert [m["done"] for m in ms] == [True, True, False]
    assert [m["name"] for m in ms] == ["M1: Foundation", "M2: Tests", "M3: Live run"]

    manifest = _manifest_with_roadmap(flat, truncated=False)
    progress = pe.compute_progress(manifest, _state_with_execution())
    assert progress["method"] == "bounded_milestones"
    assert progress["estimate"] == 67  # 2/3
    assert progress["completed"] == 2
    assert progress["remaining"] == 1


def test_newline_stripped_excerpt_with_weights_parses_all_milestones():
    """The finditer fallback also recovers explicit weights from a flat line."""
    flat = "- [x] (3) M1 - [ ] (7) M2"
    ms = pe.parse_milestones_from_content(flat)
    assert len(ms) == 2
    assert [m["weight"] for m in ms] == [3, 7]
    manifest = _manifest_with_roadmap(flat, truncated=False)
    progress = pe.compute_progress(manifest, _state_with_execution())
    assert progress["method"] == "weighted_milestones"
    assert progress["estimate"] == 30  # 3/10


def test_newline_stripped_but_truncated_still_unknown():
    """The finditer fallback parses milestones, but truncation gate -> UNKNOWN.

    Guards the interaction between fix 1 (truncation gate) and fix 2 (finditer
    fallback): even if the parser recovers milestones from a flat excerpt, a
    truncated excerpt must still yield UNKNOWN (incomplete denominator).
    """
    flat = "- [x] M1 - [x] M2 - [ ] M3"
    assert "\n" not in flat
    # Parser recovers all three...
    assert len(pe.parse_milestones_from_content(flat)) == 3
    # ...but truncation wins.
    manifest = _manifest_with_roadmap(flat, truncated=True)
    progress = pe.compute_progress(manifest, _state_with_execution())
    assert progress["estimate"] is None
    assert progress["confidence"] == "unknown"
    assert progress["method"] is None


def test_multiline_excerpt_uses_line_anchored_parse():
    """Multi-line content (has newlines) is unaffected by the finditer path."""
    multi = "- [x] M1: Foundation\n- [ ] M2: Live test\n"
    ms = pe.parse_milestones_from_content(multi)
    assert len(ms) == 2
    assert [m["name"] for m in ms] == ["M1: Foundation", "M2: Live test"]


def test_single_marker_flat_excerpt_parses_one():
    """A flat excerpt with a single marker parses exactly one milestone."""
    flat = "- [x] Only milestone here"
    ms = pe.parse_milestones_from_content(flat)
    assert len(ms) == 1
    assert ms[0]["done"] is True


# ---------------------------------------------------------------------------
# 12. WO-OBSIDIAN-041 -- unsupported methods stay UNKNOWN (no fake impl)
# ---------------------------------------------------------------------------

def test_unsupported_methods_remain_unknown():
    """phase/goal and bounded_work_orders are NOT implemented -> UNKNOWN.

    The engine must not claim support it does not have. With no weighted/bounded
    milestones, compute_progress returns UNKNOWN regardless of phase/goal/WO
    fields present in the state.
    """
    state = _state_with_execution()
    state["current_execution"]["current_goal"] = "Phase 2"
    # No roadmap evidence -> UNKNOWN (no fake phase/goal or WO-set percentage).
    manifest = {"evidence": []}
    progress = pe.compute_progress(manifest, state)
    assert progress["estimate"] is None
    assert progress["confidence"] == "unknown"
    assert progress["method"] is None
    # The supported methods are only weighted_milestones / bounded_milestones.
    assert progress["method"] in (None, "weighted_milestones", "bounded_milestones")
