# Project Adapter Registry

> Canonical registry of adapters for the Live Project Wall.
> Created by WO-OBSIDIAN-031 (Live Project Wall Foundation).
> Source of truth for which imported projects are registered, enabled, and adapted.

## Rule (registration scope)

`automation/projects.yaml` registers **all 11 imported projects** from the Project Registry.

- WO-OBSIDIAN-031 adapted the first two pilots (`thai_stt_app`, `lumina-studio`).
- WO-OBSIDIAN-032 expanded adapter coverage to the remaining 9 imported projects; all 11 are now `enabled_for_wall: true` / `pilot_status: adapted`.
- The 18 discovered-not-imported repositories are **not** registered here and must **never** appear as Wall-eligible.

## Adapter contract

Each adapted project maps source-repository evidence to normalized state via an adapter:

- `adapter_id` — identifies the adapter implementation (e.g. `generic-git-plus-authority-files`)
- `authority_candidates` — ordered list of authority files to read for current-work state
- `github.prs` / `github.ci` — whether PR/CI evidence is mapped (WO-OBSIDIAN-034 integrated the read-only GitHub adapter `automation/github_adapter.py`; CI/PR render as `unknown`/`null` until the adapter is re-run with `GITHUB_TOKEN`)

## Adapter: `generic-git-plus-authority-files`

A generic adapter that resolves project state from:

- git branch / HEAD / status / remote (read-only)
- authority files present in the source repo (e.g. `AGENTS.md`, `WORK_ORDER.md`, `AI_HANDOFF.md`, `PROJECT_RULES.md`, `README.md`)
- `.tasks/` task packets and `work-order/` work orders where present

The adapter does **not** mutate the source repository. It reads truth and emits a normalized YAML state instance under `automation/state/<project_id>.yaml`.

## Authority vs evidence (do not conflate)

- `current_work_authority` (path + kind) answers: *where did this current-work claim come from?*
- `current_work_evidence` answers: *how strongly is this claim supported?*
- `evidence_classification` is the overall record confidence, kept separate.

See `automation/state/README.md` for the normalized-state contract and `automation/schema/project-state.schema.json` for the validation contract.

## Adapter coverage (WO-031 + WO-032)

| project_id | status | WO |
|-----------|--------|----|
| thai_stt_app | adapted | WO-031 |
| lumina-studio | adapted | WO-031 |
| llm-agents | adapted | WO-032 |
| STT-Typing | adapted | WO-032 |
| AI-Worker-Harness | adapted | WO-032 |
| Utility-Disbursement-App | adapted | WO-032 |
| Adobe-Stock-Upload-Assistant | adapted | WO-032 |
| lightroom-ai-exposure | adapted | WO-032 |
| citizen_portal | adapted | WO-032 |
| TalkToClibord | adapted | WO-032 |
| AI-Workspace | adapted | WO-032 |

All 11 imported projects are adapter-covered and rendered on the Live Project Wall.
