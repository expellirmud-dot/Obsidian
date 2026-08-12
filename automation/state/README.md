# Normalized Project State

> Contract for normalized project-state instances consumed by the Live Project Wall renderer.
> Created by WO-OBSIDIAN-031 (Live Project Wall Foundation).

## Format rule

> Normalized state instances are **YAML**.
> JSON Schema (`automation/schema/project-state.schema.json`) is used only as the validation contract because YAML is compatible with the JSON data model.
> Do not switch normalized project-state files from YAML to JSON.

- State files live at `automation/state/<project_id>.yaml`.
- The JSON Schema validates the YAML data model; it does **not** dictate that instances become JSON on disk.

## Required fields

Every state instance must include all fields below. Values that cannot be verified must remain explicit `null` / `unknown` / `needs-verification` — **never guess**.

| Field | Type | Meaning |
| --- | --- | --- |
| `project_id` | string | Stable id matching the Project Registry |
| `project_name` | string | Human-readable name |
| `source_path` | string | Absolute local path of the source repo |
| `repository` | string \| null | Remote URL or null |
| `branch` | string \| null | Active branch or null |
| `head` | string \| null | HEAD commit SHA or null |
| `project_state` | string | Verified state string or `unknown` |
| `current_goal` | string \| null | Current goal or null |
| `current_work` | string \| null | Current work or null |
| `current_work_authority.path` | string \| null | Where the current-work claim came from |
| `current_work_authority.kind` | enum \| null | `work-order` \| `current-task` \| `handoff` \| `roadmap` \| `readme` \| `other` \| null |
| `current_work_evidence` | enum | `verified` \| `owner-confirmed` \| `inference` \| `unknown` |
| `ci_state` | enum \| null | `success` \| `failure` \| `pending` \| `unknown` \| null |
| `open_pr` | integer \| null | PR number or null |
| `last_change` | iso-date \| null | Last commit date or null |
| `next_action` | string \| null | Next action or null |
| `blockers` | string \| null | Blockers or null |
| `evidence_classification` | enum | Overall record confidence |
| `verified_at` | iso-date \| null | When this state was verified |
| `adapter_id` | string | Adapter that produced this state |

## Authority vs evidence (rule)

`current_work_authority` and `current_work_evidence` are **separate concerns**:

- **`current_work_authority`** answers *"Where did this current-work state come from?"* — `path` (source file) + `kind` (document type).
- **`current_work_evidence`** answers *"How strongly is this claim supported?"* — `verified` \| `owner-confirmed` \| `inference` \| `unknown`.
- **`evidence_classification`** is the overall evidence confidence for the record, kept separately.

The previous ambiguous scalar `current_work_authority: <verified | owner-confirmed | inference | unknown>` is **replaced** by the authority (path/kind) + evidence (confidence) pair.

## Validation

Validate a state instance against the schema:

```bash
python3 scripts/render_project_wall.py --validate automation/state/<project_id>.yaml
```

## Pilot scope (WO-031)

Only two state instances are produced in WO-031:

- `automation/state/thai_stt_app.yaml`
- `automation/state/lumina-studio.yaml`

The other 9 imported projects are registered in `automation/projects.yaml` but are `enabled_for_wall: false` / `pilot_status: not-yet-adapted` and have no state instance in this WO.
