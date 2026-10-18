# WO-OBSIDIAN-044 — Current and Recurring Project Truth

Work Order ID: WO-OBSIDIAN-044
Title: Current and Recurring Project Truth
Owner: Toto (delegated decision authority to Hermes Controller)
Task Classification: VAULT_OPERATIONAL_TOOLING / SOURCE_REPOSITORY
Risk Level: MEDIUM
Execution Mode: Goal-loop engineering; sequential bounded goals; read-only source repositories
Status: ACTIVE
Root: `D:\Obsidian\Project-Knowledge-Vault`
Baseline HEAD: `bf2ad318e53509e03ffd1084ab744af3fcbd0ef4`

## Objective

Make Vault project information current from live repository evidence and ensure the existing automated refresh keeps updating that information as projects advance. Preserve uncertainty when evidence is unavailable or ambiguous.

## Authority and boundaries

- Owner delegated project decisions and repository management to Hermes Controller, except genuine stop decisions requiring Owner input.
- Source repositories are read-only. No source repo edits, commits, pushes, deploys, credentials changes, or destructive cleanup.
- Do not delete or modify pre-existing owner notes or unrelated local artifacts.
- Do not fabricate mission, progress, lifecycle, or project state. Keep unavailable facts `UNKNOWN` / `needs-verification`.
- No push. Local commit only if validation passes and exact scope is staged.

## Allowed Files

- `04 Work Orders/WO-OBSIDIAN-044-CURRENT-AND-RECURRING-PROJECT-TRUTH.md`
- `04 Work Orders/CURRENT_WORK_ORDER.md`
- `04 Work Orders/Work Order Index.md`
- `automation/refresh_state.py`
- `tests/test_refresh_state.py`
- `automation/evidence_collector.py` (only if required by verified defect)
- `tests/test_evidence_collector.py` (only if required by verified defect)
- `00 Dashboard/Project Dashboard.md` (generated refresh output only)
- `automation/evidence/*.yaml` (collector output only)
- `automation/state/*.yaml` (truth pipeline output only)

## Forbidden Actions

- Modify any source repository or shared `D:\tools` file.
- Stage/commit owner artifacts, unrelated files, or files outside Allowed Files.
- Push, merge, publish externally, or run destructive cleanup.
- Promote unsupported evidence to verified or broaden mission extraction heuristics without inspecting candidate evidence and adding a negative regression test.
- Claim recurring schedule is operational without observing a real scheduled execution.

## Goal loop and outcomes

### Goal 1 — Repair preflight classification: COMPLETE

- Left `2026-08-11.md` and `2026-08-15.md` as pre-existing empty untracked owner notes; neither entered staged scope.
- Seven Project Overview `M` statuses were EOL artifacts: `git -c core.autocrlf=false diff --name-only` showed no content changes.
- Produced READY scope after creating this bounded WO. No cleanup or source repo mutation.

### Goal 2 — Verify the live update mechanism: COMPLETE

- Live GitHub API collection and truth build ran for all 23 registered projects; refreshed manifests and normalized state.
- Local publication commit `bd9643d4357c88d5a86ad815fccfa7583729e57c` refreshed 46 evidence/state YAML files; Dashboard renderer reported no change.
- Post-refresh state count: `verified=10`, `needs-verification=13`.
- Evidence unavailable for 4 projects: `Adobe-Stock-Upload-Assistant: no_remote`, `Jamie-Phone: no_evidence`, `agentic-framework-mcp` and `Nexus-Control-Center: tree_unavailable`.
- Dry-run and publish gates: validate-all PASS, renderer PASS, idempotency PASS, pytest `159 passed`.
- Remote `main` contains repeated `chore(vault): daily project truth refresh` commits on Oct 14–18, 2026. Latest inspected pre-run commit `55a76ed...` had Validation run `39085633692` success. Remote `bf2ad31` Validation run `39148432724` also success.
- `.github/workflows/validation.yml` is push/PR validation only and defines no schedule. Observed daily publisher is external; its configuration/trigger owner was not directly inspected. Current scheduler configuration remains UNKNOWN.

### Goal 3 — Repair verified pipeline defects: NOT REQUIRED

No defect reproduced. Existing refresh chain calls GitHub adapter, `collect --all`, `build-truth --all`, four gates, and optional `--publish`. No pipeline code changes made.

### Goal 4 — Reconcile and close: COMPLETE

Refresh commit is local and not pushed. This governance closeout updates WO, pointer, and Index only. Source repositories and shared tools were not modified.

## Validation

- `GITHUB_TOKEN="$(gh auth token)" uv run --no-project --with "pytest>=7,<9" --with "PyYAML>=6,<7" --with "jsonschema>=4.18,<5" --python 3.12 python automation/refresh_state.py` — PASS; all 4 gates PASS; `159 passed`.
- Same command with `--publish` — PASS; local refresh commit created; no push.
- `gh run view 39148432724 --repo expellirmud-dot/Obsidian --json headSha,conclusion,event,createdAt,workflowName,jobs` — remote head `bf2ad318...`, conclusion `success`.
- Default Python is 3.14.7 and lacks pytest; commands used isolated Python 3.12.9 environment from `uv`.
- No source repository changes; no credential values printed; owner notes preserved.

## Residual risk / next action

- 13 projects remain `needs-verification`; do not promote without explicit mission evidence.
- Scheduler configuration lives outside this repository. Remote history proves repeated publisher activity through 2026-10-18, not current scheduler configuration or a run after this local refresh. Inspect external scheduler only in a separately bounded follow-up if current scheduler ownership/continuity must be proven.
- Local `main` is ahead of `origin/main` by two commits (`bd9643d` refresh, then this closeout). Push not authorized/performed.

## Closeout

Status: CLOSED
Closed: 2026-10-19 (Asia/Bangkok)
Closeout commit: recorded after validation.
