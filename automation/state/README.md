# Normalized Project State (v2 — Project Truth Control Plane)

> Contract for normalized project-state v2 instances consumed by the Live
> Project Wall renderer. Created by WO-OBSIDIAN-031; upgraded to v2 by
> WO-OBSIDIAN-036 (Project Truth Model v2 + Freshness Contract).

## Critical semantic rule

> **Current Work Order is NOT the Project Mission.** v2 separates
> `project_identity` (stable Mission) from `current_execution` (current
> goal/work). A Work Order change touches `current_execution` only; the
> Mission is never rewritten automatically. When authoritative evidence
> indicates the Mission itself changed, `identity_drift_detected` is set, the
> previous identity is preserved in `previous_identity`, and the candidate new
> identity + its evidence provenance are recorded in `candidate_identity` /
> `candidate_identity_provenance` (never silently overwritten).

> **WO-OBSIDIAN-041 hardening (F1):** A bare project title, repository name,
> or document heading is NOT sufficient to verify the Mission.
> `knowledge_state=verified` requires an explicit Purpose/Mission/Problem
> statement read from real file content. Insufficient evidence →
> `purpose=null`, `knowledge_state=needs-verification` (never fabricated).

## Format rule

> Normalized state instances are **YAML**.
> JSON Schema (`automation/schema/project-state.v2.schema.json`) is used only
> as the validation contract because YAML is compatible with the JSON data
> model. Do not switch normalized project-state files from YAML to JSON.

- State files live at `automation/state/<project_id>.yaml`.
- The v1 schema (`project-state.schema.json`) is retained for history only;
  the active contract is v2.

## Top-level blocks

| Block | Purpose |
| --- | --- |
| `project_identity` | Stable Mission: purpose (derived from explicit Purpose/Mission/Problem text only), problem_statement, intended_outcome, primary_users, success_definition, scope, non_goals (schema-supported-but-not-derived), identity_drift_detected, previous_identity, candidate_identity, candidate_identity_provenance |
| `current_execution` | Current truth: lifecycle_phase, current_goal, current_work, current_work_authority, current_work_evidence, last_completed, blockers, next_action |
| `freshness` | Freshness contract: status, tracked_ref, remote_head, truth_built_from_head, source_checked_at, truth_built_at, stale_since, reason, source_freshness, semantic_freshness, progress_freshness |
| `progress` | Deterministic progress: scope, method, estimate, range_min, range_max, confidence, completed, active, remaining, basis |
| `github` | Live GitHub truth: ci_state, open_pr, open_pr_count, observed_at |

Plus scalar fields: `schema_version`, `project_id`, `project_name`,
`github_repository_id` (stable across rename), `source_path` (nullable for
GitHub-only projects), `repository`, `branch`, `head`, `knowledge_state`,
`last_change`, `evidence_classification`, `verified_at`, `adapter_id`.

## Freshness safety contract

- `remote_head != truth_built_from_head` → `stale`
- GitHub unreachable → `unknown` (UNKNOWN must never become FRESH)
- refresh failed → `refresh_failed` (known-good truth preserved with stale marker)
- old verified truth is kept when a new refresh fails

## Migration (backward-safe)

`automation/migrate_state_v2.py` transforms v1 flat state → v2 nested state.
It is idempotent (v2 input is returned unchanged) and drops no data. Identity
fields default to `null` (unknown) — the Mission is never fabricated.

```bash
python3 automation/migrate_state_v2.py            # migrate all v1 states
python3 automation/migrate_state_v2.py --check     # report only
python3 automation/migrate_state_v2.py --validate  # validate all v2 states
```

## Validation

```bash
python3 scripts/render_project_wall.py --validate automation/state/<project_id>.yaml
python3 scripts/render_project_wall.py --validate-all
```

## Scope

All 11 imported projects have valid v2 state and appear on the Live Project
Wall. `github_repository_id` is null until filled by the discovery layer
(WO-OBSIDIAN-037).
