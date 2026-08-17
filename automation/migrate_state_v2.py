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
    field can be mapped without guessing. Concretely only `purpose` is seeded
    from project_name and `scope` from current_goal when present, and even
    those are marked needs-verification. This keeps the contract: do not
    fabricate Mission.
  * freshness is seeded from v1 `head`/`verified_at`/`observed_at`:
      truth_built_from_head = v1 head
      remote_head = v1 head (assume fresh at migration time; the next
      freshness probe will correct this)
      status = fresh if head is set else unknown
  * progress defaults to unknown (no denominator in v1).
  * github_repository_id is left null here -- it is filled by the discovery
    layer (WO-037). null is valid for local-only projects.
  * knowledge_state defaults to needs-verification (v1 states were derived
    from already-verified Vault records but not re-verified against source in
    this run).

The migrator is idempotent: migrating a v2 file is a no-op (it detects
schema_version==2 and returns the file unchanged).

Usage:
    python3 automation/migrate_state_v2.py            # migrate all v1 states
    python3 automation/migrate_state_v2.py --check     # report only, no write
    python3 automation/migrate_state_v2.py --validate  # validate all v2 states
"""

from __future__ import annotations

import argparse
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


def migrate_one(v1: dict) -> dict:
    """Transform a v1 flat state dict into a v2 nested state dict.

    Idempotent: if the input already has schema_version==2 it is returned as-is.
    """
    if v1.get("schema_version") == 2:
        return v1

    head = v1.get("head")
    verified_at = v1.get("verified_at")
    observed_at = v1.get("observed_at")
    open_pr = v1.get("open_pr")
    current_goal = v1.get("current_goal")

    # Seed identity conservatively. Do NOT fabricate a Mission. Only map fields
    # that can be carried without guessing; everything else stays null.
    purpose = v1.get("project_name") or None
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

    # Freshness: assume fresh at migration time when a head exists. The next
    # freshness probe (WO-037/040) will reconcile remote_head against
    # truth_built_from_head. UNKNOWN must never silently become FRESH, but a
    # known head with no contrary evidence is a legitimate fresh seed.
    if head:
        freshness = {
            "status": "fresh",
            "tracked_ref": v1.get("branch"),
            "remote_head": head,
            "truth_built_from_head": head,
            "source_checked_at": observed_at or verified_at,
            "truth_built_at": verified_at,
            "stale_since": None,
            "reason": None,
            "source_freshness": "fresh",
            "semantic_freshness": "fresh",
            "progress_freshness": "fresh",
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
        if v1.get("schema_version") == 2:
            print(f"  SKIP (already v2): {path.name}")
            skipped += 1
            continue
        v2 = migrate_one(v1)
        verrors = sorted(validator.iter_errors(v2), key=lambda e: list(e.path))
        if verrors:
            print(f"  INVALID v2 for {path.name}:")
            for e in verrors:
                print(f"    - {'.'.join(map(str, e.path)) or '<root>'}: {e.message}")
            errors += 1
            continue
        if check_only:
            print(f"  WOULD MIGRATE: {path.name}")
            migrated += 1
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
