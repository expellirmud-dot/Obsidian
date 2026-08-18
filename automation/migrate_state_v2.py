#!/usr/bin/env python3
"""Backward-safe schema migration: v1 flat state -> v2 nested state.

WO-OBSIDIAN-036 (Project Truth Model v2 + Freshness Contract).

The v1 schema is a flat object. The v2 schema separates:
  * project_identity   (stable Mission -- never rewritten on Work Order change)
  * current_execution   (current goal/work -- may change per Work Order)
  * freshness          (source/semantic/progress freshness contract)
  * progress           (deterministic, evidence-constrained)

Migration rules (backward-safe):
  * Every v1 field is preserved -- no data is dropped.
  * v1 `project_state` -> current_execution.lifecycle_phase.
  * v1 `current_goal`/`current_work`/`current_work_authority`/`current_work_evidence`
    -> current_execution.* (same values).
  * v1 `next_action`/`blockers` -> current_execution.* (same values).
  * v1 `ci_state`/`open_pr`/`observed_at` -> github.* (open_pr_count defaults to
    1 when open_pr is set, else null).
  * project_identity is seeded from v1 `project_state`/`current_goal` as a
    *placeholder* with knowledge_state=needs-verification -- the Mission is NOT
    fabricated; every identity field defaults to null (unknown) unless a v1
    field can be mapped without guessing. Concretely `purpose` is NOT seeded
    (stays null -- a project name is not a Mission, WO-OBSIDIAN-041 F1);
    `scope` is seeded from current_goal as a needs-verification placeholder.
    This keeps the contract: do not fabricate Mission.
  * freshness is seeded from v1 `head`/`verified_at`/`observed_at`:
      truth_built_from_head = v1 head (preserved for reference)
      remote_head = v1 head (preserved for reference)
      status = unknown (legacy migration does NOT perform evidence refresh;
      the freshness probe establishes FRESH from current evidence)
  * progress defaults to unknown (no denominator in v1).
  * github_repository_id is left null here -- it is filled by the discovery
    layer (WO-037). null is valid for local-only projects.
  * knowledge_state defaults to needs-verification (v1 states were derived
    from already-verified Vault records but not re-verified against source in
    this run).

The migrator is idempotent: migrating a v2 file upgrades it in-place to the
current v2 shape (missing required project_identity fields added as null,
WO-OBSIDIAN-041 F11). No data is lost; a v2 file that is already current is
returned unchanged.

Usage:
    python3 automation/migrate_state_v2.py            # migrate all v1 states
    python3 automation/migrate_state_v2.py --check     # report only, no write
    python3 automation/migrate_state_v2.py --validate  # validate all v2 states
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = REPO_ROOT / "automation" / "state"
V2_SCHEMA_PATH = REPO_ROOT / "automation" / "schema" / "project-state.v2.schema.json"


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_schema() -> dict:
    with open(V2_SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _upgrade_v2_shape(v2: dict) -> dict:
    """Upgrade an old v2 state to the current v2 shape by adding any missing
    required project_identity fields as null. Does NOT lose existing data.
    Idempotent (WO-OBSIDIAN-041 F11).

    Pre-WO-041 v2 states lack candidate_identity / candidate_identity_provenance,
    which the schema now requires. This adds them as null when missing; existing
    values (e.g. a candidate_identity recorded by a prior drift detection) are
    preserved.
    """
    identity = v2.get("project_identity")
    if not isinstance(identity, dict):
        # Shouldn't happen for a valid v2 state, but be safe: do not touch it.
        return v2
    if "candidate_identity" not in identity:
        identity["candidate_identity"] = None
    if "candidate_identity_provenance" not in identity:
        identity["candidate_identity_provenance"] = None
    v2["project_identity"] = identity
    return v2


def migrate_one(v1: dict) -> dict:
    """Transform a v1 flat state dict into a v2 nested state dict.

    Idempotent: if the input already has schema_version==2, it is upgraded
    in-place to the current v2 shape (missing required project_identity
    fields added as null). This handles pre-WO-041 v2 states that lack
    candidate_identity / candidate_identity_provenance (WO-OBSIDIAN-041 F11).
    """
    if v1.get("schema_version") == 2:
        return _upgrade_v2_shape(v1)

    head = v1.get("head")
    verified_at = v1.get("verified_at")
    observed_at = v1.get("observed_at")
    open_pr = v1.get("open_pr")
    current_goal = v1.get("current_goal")

    # Seed identity conservatively. Do NOT fabricate a Mission. A project name
    # or heading is NOT a purpose (WO-OBSIDIAN-041 F1). Only an explicit
    # Purpose/Mission/Problem statement would justify a non-null purpose, and
    # the migrator has no content evidence -- so purpose stays null here. The
    # evidence collector (WO-038) fills purpose later from real file content
    # using explicit-purpose detection. scope is seeded from current_goal only
    # as a needs-verification placeholder (it is execution scope, not Mission).
    purpose = None
    scope = current_goal or None
    identity = {
        "purpose": purpose,
        "problem_statement": None,
        "intended_outcome": None,
        "primary_users": None,
        "success_definition": None,
        "scope": scope,
        "non_goals": None,
        "identity_drift_detected": False,
        "previous_identity": None,
        "candidate_identity": None,
        "candidate_identity_provenance": None,
    }

    current_execution = {
        "lifecycle_phase": v1.get("project_state"),
        "current_goal": current_goal,
        "current_work": v1.get("current_work"),
        "current_work_authority": v1.get("current_work_authority")
        or {"path": None, "kind": None},
        "current_work_evidence": v1.get("current_work_evidence") or "unknown",
        "last_completed": None,
        "blockers": v1.get("blockers"),
        "next_action": v1.get("next_action"),
    }

    # Freshness: legacy migration is a DATA TRANSFORM, not an evidence
    # refresh. A stored v1 HEAD does NOT prove current semantic/progress
    # truth -- the migrated state still has knowledge_state=
    # needs-verification, purpose=null, progress.estimate=null and
    # progress.confidence=unknown. Therefore ALL freshness fields must be
    # "unknown" (WO-OBSIDIAN-041 F13). The stored head is preserved in
    # remote_head / truth_built_from_head for reference only -- that is data
    # preservation, NOT a freshness claim. The freshness probe (WO-037/040)
    # establishes FRESH from current evidence. UNKNOWN must never silently
    # become FRESH.
    if head:
        freshness = {
            "status": "unknown",
            "tracked_ref": v1.get("branch"),
            "remote_head": head,
            "truth_built_from_head": head,
            "source_checked_at": observed_at or verified_at,
            "truth_built_at": verified_at,
            "stale_since": None,
            "reason": "legacy state migrated; freshness requires source re-verification",
            "source_freshness": "unknown",
            "semantic_freshness": "unknown",
            "progress_freshness": "unknown",
        }
    else:
        freshness = {
            "status": "unknown",
            "tracked_ref": v1.get("branch"),
            "remote_head": None,
            "truth_built_from_head": None,
            "source_checked_at": observed_at or verified_at,
            "truth_built_at": verified_at,
            "stale_since": None,
            "reason": "no head sha in v1 state",
            "source_freshness": "unknown",
            "semantic_freshness": "unknown",
            "progress_freshness": "unknown",
        }

    progress = {
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

    github = {
        "ci_state": v1.get("ci_state") or "unknown",
        "open_pr": open_pr,
        # v1 did not track open_pr_count; leave null (unknown) rather than
        # fabricate a count. The adapter (WO-034/v2) fills the real count.
        "open_pr_count": None,
        "observed_at": observed_at,
    }

    v2 = {
        "schema_version": 2,
        "project_id": v1.get("project_id"),
        "project_name": v1.get("project_name"),
        "github_repository_id": None,
        "source_path": v1.get("source_path"),
        "repository": v1.get("repository"),
        "branch": v1.get("branch"),
        "head": head,
        "knowledge_state": "needs-verification",
        "project_identity": identity,
        "current_execution": current_execution,
        "freshness": freshness,
        "progress": progress,
        "github": github,
        "last_change": v1.get("last_change"),
        "evidence_classification": v1.get("evidence_classification") or "unknown",
        "verified_at": verified_at,
        "adapter_id": v1.get("adapter_id") or "generic-git-plus-authority-files",
    }
    return v2


def render_v2_yaml(v2: dict, original_text: str) -> str:
    """Render a v2 state as YAML, preserving the original header comment block.

    The original v1 files begin with a `#`-comment header. We keep every
    leading comment line up to the first non-comment, non-blank line, then
    append a v2 marker comment and the YAML body.
    """
    header_lines: list[str] = []
    for line in original_text.splitlines():
        if line.startswith("#") or line.strip() == "":
            header_lines.append(line)
        else:
            break
    # Drop trailing blank lines from the captured header.
    while header_lines and header_lines[-1].strip() == "":
        header_lines.pop()
    body = yaml.safe_dump(
        v2,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
        width=1000,
    )
    marker = "# --- v2 (WO-OBSIDIAN-036): identity/execution/freshness/progress separated ---"
    return "\n".join(header_lines) + "\n" + marker + "\n" + body


def migrate_all(check_only: bool = False) -> tuple[int, int, int]:
    """Migrate every state file. Returns (migrated, skipped, errors)."""
    schema = load_schema()
    validator = Draft202012Validator(schema)
    migrated = 0
    skipped = 0
    errors = 0
    for path in sorted(STATE_DIR.glob("*.yaml")):
        if not path.is_file():
            continue
        original_text = path.read_text(encoding="utf-8")
        v1 = load_yaml(path)
        if not isinstance(v1, dict):
            print(f"  SKIP (not a dict): {path.name}")
            errors += 1
            continue
        # WO-OBSIDIAN-041 F11: do NOT skip schema_version==2 states. Old v2
        # states may lack the now-required candidate_identity /
        # candidate_identity_provenance fields; migrate_one upgrades them
        # in-place. v1 states flow through the normal v1->v2 path.
        #
        # Snapshot the original dict before migration: migrate_one mutates v2
        # states in place during the shape upgrade, so we compare against the
        # snapshot to decide whether anything actually changed.
        original_snapshot = copy.deepcopy(v1) if v1.get("schema_version") == 2 else None
        v2 = migrate_one(v1)
        verrors = sorted(validator.iter_errors(v2), key=lambda e: list(e.path))
        if verrors:
            print(f"  INVALID v2 for {path.name}:")
            for e in verrors:
                print(f"    - {'.'.join(map(str, e.path)) or '<root>'}: {e.message}")
            errors += 1
            continue
        # A v2 state that was already current (shape upgrade was a no-op) is
        # not rewritten. v1->v2 migrations always change the dict, so they are
        # written.
        already_current = original_snapshot is not None and v2 == original_snapshot
        if check_only:
            if already_current:
                print(f"  SKIP (already current v2): {path.name}")
                skipped += 1
            else:
                print(f"  WOULD MIGRATE: {path.name}")
                migrated += 1
            continue
        if already_current:
            print(f"  SKIP (already current v2): {path.name}")
            skipped += 1
            continue
        new_text = render_v2_yaml(v2, original_text)
        path.write_text(new_text, encoding="utf-8")
        print(f"  MIGRATED: {path.name}")
        migrated += 1
    return migrated, skipped, errors


def validate_all() -> int:
    schema = load_schema()
    validator = Draft202012Validator(schema)
    rc = 0
    valid = 0
    total = 0
    for path in sorted(STATE_DIR.glob("*.yaml")):
        if not path.is_file():
            continue
        total += 1
        state = load_yaml(path)
        errors = sorted(validator.iter_errors(state), key=lambda e: list(e.path))
        if errors:
            print(f"  INVALID: {path.name}")
            for e in errors:
                print(f"    - {'.'.join(map(str, e.path)) or '<root>'}: {e.message}")
            rc = 1
        else:
            print(f"  VALID: {path.name}")
            valid += 1
    print(f"Validation: {valid}/{total} VALID (exit code {rc})")
    return rc


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Migrate v1 state -> v2 (WO-036)")
    parser.add_argument("--check", action="store_true", help="report only, do not write")
    parser.add_argument("--validate", action="store_true", help="validate all v2 states")
    args = parser.parse_args(argv[1:])

    print("WO-OBSIDIAN-036 -- Project Truth Model v2 migration")
    print("=" * 70)
    if args.validate:
        return validate_all()
    migrated, skipped, errors = migrate_all(check_only=args.check)
    print("-" * 70)
    print(f"migrated={migrated} skipped={skipped} errors={errors}")
    if errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
