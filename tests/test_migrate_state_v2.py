"""WO-OBSIDIAN-036 regression suite for the v2 schema + migration.

Covers automation/migrate_state_v2.py and the v2 schema contract. No real
state YAML files are mutated; tests that need files use tmp_path.

Test cases:
  1. test_v2_schema_separates_identity_execution_freshness_progress
  2. test_migration_preserves_v1_data
  3. test_migration_is_idempotent
  4. test_migration_does_not_fabricate_mission
  5. test_mission_not_rewritten_when_work_order_changes
  6. test_freshness_contract_unknown_never_becomes_fresh
  7. test_github_repository_id_allows_null_for_local_only
  8. test_progress_supports_unknown
  9. test_pre_wo041_v2_state_upgraded_with_new_fields        (WO-041 F11)
  10. test_idempotent_v2_shape_upgrade                        (WO-041 F11)
  11. test_migrate_all_upgrades_old_v2_states                 (WO-041 F11)
  12. test_migrate_all_skips_already_current_v2               (WO-041 F11)
  13. test_v2_shape_upgrade_preserves_existing_data           (WO-041 F11)
"""

from __future__ import annotations

import copy
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

import migrate_state_v2 as mig  # noqa: E402


# ---------------------------------------------------------------------------
# 1. v2 schema separates identity / execution / freshness / progress
# ---------------------------------------------------------------------------

def test_v2_schema_separates_identity_execution_freshness_progress(schema):
    """The v2 schema requires the four separated top-level blocks."""
    required = schema["required"]
    for block in (
        "project_identity",
        "current_execution",
        "freshness",
        "progress",
    ):
        assert block in required, f"{block} must be a required top-level block"
    # identity sub-fields
    for f in (
        "purpose",
        "problem_statement",
        "intended_outcome",
        "primary_users",
        "success_definition",
        "scope",
        "non_goals",
        "identity_drift_detected",
        "previous_identity",
        "candidate_identity",
        "candidate_identity_provenance",
    ):
        assert f in schema["properties"]["project_identity"]["properties"], (
            f"project_identity missing {f}"
        )
    # freshness sub-fields incl. the three split freshness dimensions
    for f in (
        "status",
        "tracked_ref",
        "remote_head",
        "truth_built_from_head",
        "source_checked_at",
        "truth_built_at",
        "stale_since",
        "reason",
        "source_freshness",
        "semantic_freshness",
        "progress_freshness",
    ):
        assert f in schema["properties"]["freshness"]["properties"], (
            f"freshness missing {f}"
        )
    # github_repository_id is present and nullable (survives rename)
    gid = schema["properties"]["github_repository_id"]
    assert "integer" in gid["type"] and "null" in gid["type"]


# ---------------------------------------------------------------------------
# 2. Migration preserves v1 data (no data dropped)
# ---------------------------------------------------------------------------

def test_migration_preserves_v1_data():
    """Every v1 field is carried into v2; no data is dropped."""
    v1 = {
        "project_id": "demo",
        "project_name": "Demo",
        "source_path": "D:\\demo",
        "repository": "https://github.com/expellirmud-dot/demo.git",
        "branch": "main",
        "head": "abc1234567890",
        "project_state": "active",
        "current_goal": "Ship v1",
        "current_work": "writing tests",
        "current_work_authority": {"path": "WO-1.md", "kind": "work-order"},
        "current_work_evidence": "verified",
        "ci_state": "success",
        "open_pr": 7,
        "last_change": "2026-08-10",
        "next_action": "merge",
        "blockers": "none",
        "evidence_classification": "verified",
        "verified_at": "2026-08-10T00:00:00Z",
        "adapter_id": "generic-git-plus-authority-files",
        "observed_at": "2026-08-17T00:00:00Z",
    }
    v2 = mig.migrate_one(v1)
    assert v2["schema_version"] == 2
    assert v2["project_id"] == "demo"
    assert v2["project_name"] == "Demo"
    assert v2["repository"] == v1["repository"]
    assert v2["branch"] == "main"
    assert v2["head"] == "abc1234567890"
    # project_state -> lifecycle_phase
    assert v2["current_execution"]["lifecycle_phase"] == "active"
    assert v2["current_execution"]["current_goal"] == "Ship v1"
    assert v2["current_execution"]["current_work"] == "writing tests"
    assert v2["current_execution"]["current_work_authority"] == {"path": "WO-1.md", "kind": "work-order"}
    assert v2["current_execution"]["current_work_evidence"] == "verified"
    assert v2["current_execution"]["next_action"] == "merge"
    assert v2["current_execution"]["blockers"] == "none"
    # github block
    assert v2["github"]["ci_state"] == "success"
    assert v2["github"]["open_pr"] == 7
    assert v2["github"]["observed_at"] == "2026-08-17T00:00:00Z"
    assert v2["last_change"] == "2026-08-10"
    assert v2["verified_at"] == "2026-08-10T00:00:00Z"


# ---------------------------------------------------------------------------
# 3. Migration is idempotent
# ---------------------------------------------------------------------------

def test_migration_is_idempotent():
    """Migrating an already-v2 state returns it unchanged."""
    v1 = {
        "project_id": "demo",
        "project_name": "Demo",
        "source_path": "D:\\demo",
        "repository": None,
        "branch": "main",
        "head": None,
        "project_state": "active",
        "current_goal": None,
        "current_work": None,
        "current_work_authority": {"path": None, "kind": None},
        "current_work_evidence": "unknown",
        "ci_state": "unknown",
        "open_pr": None,
        "last_change": None,
        "next_action": None,
        "blockers": None,
        "evidence_classification": "unknown",
        "verified_at": None,
        "adapter_id": "generic-git-plus-authority-files",
    }
    v2 = mig.migrate_one(v1)
    v2_again = mig.migrate_one(v2)
    assert v2_again is v2  # returned as-is (schema_version==2 short-circuit)


# ---------------------------------------------------------------------------
# 4. Migration does not fabricate a Mission
# ---------------------------------------------------------------------------

def test_migration_does_not_fabricate_mission():
    """When v1 has no identity evidence, identity fields stay null (unknown)."""
    v1 = {
        "project_id": "demo",
        "project_name": "Demo",
        "source_path": "D:\\demo",
        "repository": None,
        "branch": "main",
        "head": None,
        "project_state": "active",
        "current_goal": None,
        "current_work": None,
        "current_work_authority": {"path": None, "kind": None},
        "current_work_evidence": "unknown",
        "ci_state": "unknown",
        "open_pr": None,
        "last_change": None,
        "next_action": None,
        "blockers": None,
        "evidence_classification": "unknown",
        "verified_at": None,
        "adapter_id": "generic-git-plus-authority-files",
    }
    v2 = mig.migrate_one(v1)
    identity = v2["project_identity"]
    # WO-OBSIDIAN-041 F1: purpose is NO LONGER seeded from project_name (a name
    # is not a Mission). All identity fields must be null -- no fabrication.
    # scope is seeded from current_goal (execution scope, not Mission).
    assert identity["purpose"] is None
    assert identity["problem_statement"] is None
    assert identity["intended_outcome"] is None
    assert identity["primary_users"] is None
    assert identity["success_definition"] is None
    assert identity["non_goals"] is None
    assert identity["identity_drift_detected"] is False
    assert identity["previous_identity"] is None
    assert identity["candidate_identity"] is None
    assert identity["candidate_identity_provenance"] is None
    # knowledge_state must be needs-verification, not verified-by-guess.
    assert v2["knowledge_state"] == "needs-verification"


# ---------------------------------------------------------------------------
# 5. Mission is NOT rewritten when a Work Order changes (semantic separation)
# ---------------------------------------------------------------------------

def test_mission_not_rewritten_when_work_order_changes():
    """Changing current_work/current_goal must not alter project_identity.

    This encodes the critical semantic rule: Current Work Order != Project
    Mission. The v2 structure keeps them in separate blocks so a Work Order
    change touches current_execution only.
    """
    v1 = {
        "project_id": "demo",
        "project_name": "Demo Platform",
        "source_path": "D:\\demo",
        "repository": None,
        "branch": "main",
        "head": "aaa",
        "project_state": "active",
        "current_goal": "Mission A",
        "current_work": "WO-1 doing A",
        "current_work_authority": {"path": "WO-1.md", "kind": "work-order"},
        "current_work_evidence": "verified",
        "ci_state": "unknown",
        "open_pr": None,
        "last_change": None,
        "next_action": "finish A",
        "blockers": None,
        "evidence_classification": "verified",
        "verified_at": "2026-08-10T00:00:00Z",
        "adapter_id": "generic-git-plus-authority-files",
    }
    v2 = mig.migrate_one(v1)
    identity_before = dict(v2["project_identity"])

    # Simulate a NEW Work Order that changes the work entirely (feature B).
    v2["current_execution"]["current_goal"] = "Feature B"
    v2["current_execution"]["current_work"] = "WO-2 doing B"
    v2["current_execution"]["current_work_authority"] = {"path": "WO-2.md", "kind": "work-order"}

    # The identity block must be untouched by the Work Order change.
    assert v2["project_identity"] == identity_before
    # And specifically the purpose/mission did not become "Feature B".
    assert v2["project_identity"]["purpose"] != "Feature B"


# ---------------------------------------------------------------------------
# 6. Freshness contract: UNKNOWN must never silently become FRESH
# ---------------------------------------------------------------------------

def test_freshness_contract_unknown_never_becomes_fresh():
    """A v1 state with no head migrates to freshness.status=unknown, not fresh."""
    v1 = {
        "project_id": "demo",
        "project_name": "Demo",
        "source_path": "D:\\demo",
        "repository": None,
        "branch": "main",
        "head": None,  # no head -> unknown
        "project_state": "active",
        "current_goal": None,
        "current_work": None,
        "current_work_authority": {"path": None, "kind": None},
        "current_work_evidence": "unknown",
        "ci_state": "unknown",
        "open_pr": None,
        "last_change": None,
        "next_action": None,
        "blockers": None,
        "evidence_classification": "unknown",
        "verified_at": None,
        "adapter_id": "generic-git-plus-authority-files",
    }
    v2 = mig.migrate_one(v1)
    fr = v2["freshness"]
    assert fr["status"] == "unknown"
    assert fr["remote_head"] is None
    assert fr["truth_built_from_head"] is None
    assert fr["source_freshness"] == "unknown"
    # The contract: unknown must NOT be fresh.
    assert fr["status"] != "fresh"


# ---------------------------------------------------------------------------
# 7. github_repository_id allows null for local-only projects
# ---------------------------------------------------------------------------

def test_github_repository_id_allows_null_for_local_only(schema, valid_state_dict):
    """A local-only project (no remote) validates with github_repository_id=null."""
    validator = Draft202012Validator(schema)
    state = dict(valid_state_dict)
    state["github_repository_id"] = None
    state["repository"] = None
    assert list(validator.iter_errors(state)) == []


# ---------------------------------------------------------------------------
# 8. progress supports unknown (no denominator)
# ---------------------------------------------------------------------------

def test_progress_supports_unknown(schema, valid_state_dict):
    """A progress block with all-unknown values validates (no denominator)."""
    validator = Draft202012Validator(schema)
    state = dict(valid_state_dict)
    state["progress"] = {
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
    }
    assert list(validator.iter_errors(state)) == []


# ---------------------------------------------------------------------------
# 9-13. WO-OBSIDIAN-041 F11: backward-safe v2 shape upgrade
# ---------------------------------------------------------------------------

def _pre_wo041_v2_state() -> dict:
    """A valid pre-WO-041 v2 state: schema_version=2 but project_identity
    LACKS candidate_identity / candidate_identity_provenance (the fields the
    WO-041 schema now requires)."""
    state = {
        "schema_version": 2,
        "project_id": "demo",
        "project_name": "Demo",
        "github_repository_id": None,
        "source_path": "D:\\demo",
        "repository": "https://github.com/expellirmud-dot/demo.git",
        "branch": "main",
        "head": "abc1234567890",
        "knowledge_state": "needs-verification",
        "project_identity": {
            "purpose": "Mission A",
            "problem_statement": "Solve X",
            "intended_outcome": "Outcome Y",
            "primary_users": "users",
            "success_definition": "def",
            "scope": "scope A",
            "non_goals": "ng",
            "identity_drift_detected": False,
            "previous_identity": None,
            # NOTE: candidate_identity / candidate_identity_provenance absent
        },
        "current_execution": {
            "lifecycle_phase": "active",
            "current_goal": "Ship v1",
            "current_work": "writing tests",
            "current_work_authority": {"path": "WO-1.md", "kind": "work-order"},
            "current_work_evidence": "verified",
            "last_completed": None,
            "blockers": None,
            "next_action": "merge",
        },
        "freshness": {
            "status": "fresh",
            "tracked_ref": "main",
            "remote_head": "abc1234567890",
            "truth_built_from_head": "abc1234567890",
            "source_checked_at": "2026-08-10T00:00:00Z",
            "truth_built_at": "2026-08-10T00:00:00Z",
            "stale_since": None,
            "reason": None,
            "source_freshness": "fresh",
            "semantic_freshness": "fresh",
            "progress_freshness": "fresh",
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
            "ci_state": "success",
            "open_pr": 7,
            "open_pr_count": None,
            "observed_at": "2026-08-10T00:00:00Z",
        },
        "last_change": "2026-08-10",
        "evidence_classification": "verified",
        "verified_at": "2026-08-10T00:00:00Z",
        "adapter_id": "generic-git-plus-authority-files",
    }
    return state


def test_pre_wo041_v2_state_upgraded_with_new_fields(schema):
    """A pre-WO-041 v2 state (missing candidate_* fields) is upgraded in-place
    by migrate_one and then validates against the current schema."""
    validator = Draft202012Validator(schema)
    state = _pre_wo041_v2_state()
    # Sanity: the pre-WO-041 state must FAIL the current schema (missing
    # required fields) before the upgrade.
    pre_errors = list(validator.iter_errors(state))
    assert pre_errors, "pre-WO-041 v2 state should fail current schema before upgrade"

    upgraded = mig.migrate_one(copy.deepcopy(state))

    assert upgraded["schema_version"] == 2
    identity = upgraded["project_identity"]
    assert "candidate_identity" in identity
    assert identity["candidate_identity"] is None
    assert "candidate_identity_provenance" in identity
    assert identity["candidate_identity_provenance"] is None
    # Existing data preserved.
    assert identity["purpose"] == "Mission A"
    assert identity["problem_statement"] == "Solve X"
    assert identity["scope"] == "scope A"
    assert upgraded["project_id"] == "demo"
    assert upgraded["current_execution"]["current_goal"] == "Ship v1"
    assert upgraded["github"]["open_pr"] == 7
    # The upgraded state must now pass the current schema.
    assert list(validator.iter_errors(upgraded)) == []


def test_idempotent_v2_shape_upgrade(schema):
    """Running migrate_one on an already-upgraded v2 state is a no-op."""
    validator = Draft202012Validator(schema)
    state = _pre_wo041_v2_state()
    upgraded_once = mig.migrate_one(copy.deepcopy(state))
    upgraded_twice = mig.migrate_one(copy.deepcopy(upgraded_once))
    assert upgraded_twice == upgraded_once
    assert upgraded_twice["project_identity"]["candidate_identity"] is None
    assert upgraded_twice["project_identity"]["candidate_identity_provenance"] is None
    assert list(validator.iter_errors(upgraded_twice)) == []


def test_migrate_all_upgrades_old_v2_states(schema, tmp_path, monkeypatch):
    """migrate_all upgrades an old v2 state file on disk and the result is
    valid against the current schema."""
    # Point STATE_DIR at a temp dir with a single old v2 state file.
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    old_state = _pre_wo041_v2_state()
    state_path = state_dir / "demo.yaml"
    state_path.write_text(yaml.safe_dump(old_state, sort_keys=False), encoding="utf-8")

    monkeypatch.setattr(mig, "STATE_DIR", state_dir)

    migrated, skipped, errors = mig.migrate_all(check_only=False)
    assert errors == 0
    assert migrated == 1
    assert skipped == 0

    # The file on disk now has the candidate fields and validates.
    written = yaml.safe_load(state_path.read_text(encoding="utf-8"))
    identity = written["project_identity"]
    assert "candidate_identity" in identity
    assert identity["candidate_identity"] is None
    assert "candidate_identity_provenance" in identity
    assert identity["candidate_identity_provenance"] is None
    validator = Draft202012Validator(schema)
    assert list(validator.iter_errors(written)) == []


def test_migrate_all_skips_already_current_v2(schema, valid_state_dict, tmp_path, monkeypatch):
    """A v2 state that already has the candidate fields is NOT rewritten."""
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    state_path = state_dir / "current.yaml"
    # valid_state_dict already has candidate_identity / candidate_identity_provenance.
    original_text = yaml.safe_dump(valid_state_dict, sort_keys=False)
    state_path.write_text(original_text, encoding="utf-8")

    monkeypatch.setattr(mig, "STATE_DIR", state_dir)

    migrated, skipped, errors = mig.migrate_all(check_only=False)
    assert errors == 0
    assert migrated == 0
    assert skipped == 1
    # File unchanged on disk.
    assert state_path.read_text(encoding="utf-8") == original_text


def test_v2_shape_upgrade_preserves_existing_data(schema):
    """A v2 state that already has a non-null candidate_identity (from a prior
    drift detection) must NOT have it overwritten by the shape upgrade."""
    validator = Draft202012Validator(schema)
    state = _pre_wo041_v2_state()
    # Simulate a prior drift detection that recorded a candidate identity.
    state["project_identity"]["candidate_identity"] = {"purpose": "candidate"}
    state["project_identity"]["candidate_identity_provenance"] = {
        "path": "README.md",
        "ref": "main",
        "blob_sha": "deadbeef",
        "observed_at": "2026-08-10T00:00:00Z",
    }
    state["project_identity"]["identity_drift_detected"] = True

    upgraded = mig.migrate_one(copy.deepcopy(state))

    identity = upgraded["project_identity"]
    # Existing candidate values preserved -- NOT overwritten with null.
    assert identity["candidate_identity"] == {"purpose": "candidate"}
    assert identity["candidate_identity_provenance"]["path"] == "README.md"
    assert identity["identity_drift_detected"] is True
    # Other existing data preserved.
    assert identity["purpose"] == "Mission A"
    assert identity["scope"] == "scope A"
    # Validates against the current schema.
    assert list(validator.iter_errors(upgraded)) == []


# ---------------------------------------------------------------------------
# WO-OBSIDIAN-041 F13: legacy migration must NOT fabricate freshness.
# Migration is a data transform, not an evidence refresh. A stored v1 HEAD
# does not prove current semantic/progress truth, so ALL freshness fields
# must be "unknown" after migration. The stored head is preserved in
# remote_head / truth_built_from_head for reference only (data preservation,
# not a freshness claim). The freshness probe establishes FRESH from current
# evidence.
# ---------------------------------------------------------------------------

def _v1_with_head() -> dict:
    """A v1 flat state with a non-null head (the F13 regression input)."""
    return {
        "project_id": "demo",
        "project_name": "Demo",
        "source_path": "D:\\demo",
        "repository": "https://github.com/expellirmud-dot/demo.git",
        "branch": "main",
        "head": "abc1234567890",
        "project_state": "active",
        "current_goal": "Ship v1",
        "current_work": "writing tests",
        "current_work_authority": {"path": "WO-1.md", "kind": "work-order"},
        "current_work_evidence": "verified",
        "ci_state": "success",
        "open_pr": 7,
        "last_change": "2026-08-10",
        "next_action": "merge",
        "blockers": "none",
        "evidence_classification": "verified",
        "verified_at": "2026-08-10T00:00:00Z",
        "adapter_id": "generic-git-plus-authority-files",
        "observed_at": "2026-08-17T00:00:00Z",
    }


def test_v1_with_head_does_not_fabricate_freshness(schema):
    """A v1 state with a non-null head must NOT migrate to freshness=fresh.

    Legacy migration is a data transform, not an evidence refresh. The
    migrated state still has knowledge_state=needs-verification, purpose=null,
    progress.estimate=null and progress.confidence=unknown -- so it cannot
    claim semantic/progress FRESH. All freshness fields must be "unknown".
    The stored head is preserved in remote_head / truth_built_from_head for
    reference only. The result must pass the current schema.
    """
    validator = Draft202012Validator(schema)
    v2 = mig.migrate_one(_v1_with_head())

    # Identity / knowledge / progress are conservative (no fabrication).
    assert v2["project_identity"]["purpose"] is None
    assert v2["knowledge_state"] == "needs-verification"
    assert v2["progress"]["estimate"] is None
    assert v2["progress"]["confidence"] == "unknown"

    fr = v2["freshness"]
    # Freshness status and all sub-gates must NOT be "fresh".
    assert fr["status"] != "fresh"
    assert fr["status"] == "unknown"
    assert fr["semantic_freshness"] != "fresh"
    assert fr["semantic_freshness"] == "unknown"
    assert fr["progress_freshness"] != "fresh"
    assert fr["progress_freshness"] == "unknown"
    assert fr["source_freshness"] != "fresh"
    assert fr["source_freshness"] == "unknown"

    # The stored head is preserved for reference (data preservation, not a
    # freshness claim).
    assert fr["remote_head"] == "abc1234567890"
    assert fr["truth_built_from_head"] == "abc1234567890"

    # The migrated state must pass the current schema.
    assert list(validator.iter_errors(v2)) == []


def test_v1_without_head_unknown_freshness(schema):
    """A v1 state with head=None migrates to all-unknown freshness (existing
    behavior, kept as a regression guard)."""
    validator = Draft202012Validator(schema)
    v1 = _v1_with_head()
    v1["head"] = None
    v2 = mig.migrate_one(v1)
    fr = v2["freshness"]
    assert fr["status"] == "unknown"
    assert fr["source_freshness"] == "unknown"
    assert fr["semantic_freshness"] == "unknown"
    assert fr["progress_freshness"] == "unknown"
    assert fr["remote_head"] is None
    assert fr["truth_built_from_head"] is None
    assert list(validator.iter_errors(v2)) == []


def test_migration_reason_documents_reverification():
    """The freshness.reason for a head-present v1 migration must mention
    re-verification (it documents that freshness requires source
    re-verification, not a fabricated fresh claim)."""
    v2 = mig.migrate_one(_v1_with_head())
    reason = v2["freshness"]["reason"]
    assert reason is not None
    assert "re-verification" in reason or "re-verify" in reason
    # The reason must not claim a fresh STATUS (it documents that freshness
    # requires re-verification). "freshness" (the field name) is fine; the
    # standalone status word "fresh" as a claim is not.
    assert "fresh" not in reason.replace("freshness", "")


def test_migrated_state_passes_schema(schema):
    """A migrated v1 state (with head) passes the current v2 schema."""
    validator = Draft202012Validator(schema)
    v2 = mig.migrate_one(_v1_with_head())
    assert list(validator.iter_errors(v2)) == []
