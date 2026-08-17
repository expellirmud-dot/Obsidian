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
    # Only purpose (from project_name) and scope (from current_goal, here null)
    # are seeded; everything else must be null -- no fabrication.
    assert identity["problem_statement"] is None
    assert identity["intended_outcome"] is None
    assert identity["primary_users"] is None
    assert identity["success_definition"] is None
    assert identity["non_goals"] is None
    assert identity["identity_drift_detected"] is False
    assert identity["previous_identity"] is None
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
