# WO-OBSIDIAN-015 — Merge Agent A/B/C/D into clean integration worktree

## Approved Approach

Merge 4 Wave 1 agent feature branches into a new clean integration worktree, preserving each branch's provenance with `--no-ff`. Cannot merge into baseline `D:\llm-agents` (dirty worktree — 36 status entries).

## Integration Worktree

- Path: `D:/llm-agents-worktrees/wave1-agent-integration`
- Branch: `integration/wave1-agent-integration`
- Base: `integration/wave1-foundation` (099e516)
- Created: `git worktree add D:/llm-agents-worktrees/wave1-agent-integration -b integration/wave1-agent-integration integration/wave1-foundation`

## Merge Order & Results

### 1. feature/agent-b-path-policy (path-policy)
- Commits: `a9e51d4 Implement PathPolicy and Capabilities`
- Files: agent/path_policy.py, agent/capabilities.py, tests/test_path_policy.py, tests/test_capabilities.py
- Merge: `--no-ff` → commit `fd1155f`
- Tests: **6 passed**
- Status: ✅ clean

### 2. feature/agent-c-test-replay (replay)
- Commit: `1fb608c test: add replay infrastructure and scenarios`
- Files: tests/conftest.py, tests/fixtures/runtime_scenarios/agent_a.json, test_provider_replay.py, test_runtime_scenarios.py
- Merge: `--no-ff` → commit `0702e7d`
- Tests: **7 passed** (cumulative)
- Status: ✅ clean

### 3. feature/agent-d-runtime-ledger (runtime)
- Commit: `87d5f10 feat: Add Runtime and Evidence infrastructure`
- Files: agent/event_log.py, agent/run_context.py, scripts/preflight.py, scripts/run_certification_live.py, scripts/run_engineering_live.py, tests/test_event_log.py, tests/test_run_context.py
- Merge: `--no-ff` → commit `c6e7eb9`
- Tests: **12 passed** (cumulative)
- Status: ✅ clean

### 4. feature/agent-a-protocol (protocol — merged last)
- Commit: `9017c2e feat(agent): extract typed protocol contract`
- Files: agent/protocol.py, tests/test_protocol.py, 71 fixture JSON files
- Note: 51 add/add conflicts on fixture files (base `099e516` already had fixture corpus)
- Conflict resolution: kept THEIRS (integration base) for all fixture files, accepted agent-a's unique files (`protocol.py`, `test_protocol.py`)
- Merge: `--no-ff` (with conflict resolution) → commit `6fb56e7`
- Tests: **104 passed** (cumulative — ALL tests)
- Status: ✅ clean

## Final Architecture Check

| Check | Result |
|-------|:------:|
| `py_compile` all agent files | ✅ PASS (5 modules) |
| Import all agent modules | ✅ ALL IMPORTS OK |
| Full pytest suite | ✅ **104 passed in 3.00s** |
| `git diff --check` | ✅ No whitespace errors |
| Integration worktree status | ✅ Clean |

## Provenance: Agent A Untracked Files

| File | Content | Classification |
|------|---------|:--------------:|
| `scratch/` (10 files) | Debug/diagnostic scripts from development | **REGENERATABLE_SCRATCH** |
| `valid_fixtures.json` (78 lines) | Hand-curated parser test vectors, NOT referenced by any tracked code | **REGENERATABLE_SCRATCH** |

No VALUABLE_EVIDENCE found. Both are development artifacts safe to discard upon worktree removal.

## Future State

| Branch | Fate |
|--------|:----:|
| `feature/agent-a-protocol` | Merged into `integration/wave1-agent-integration` |
| `feature/agent-b-path-policy` | Merged into `integration/wave1-agent-integration` |
| `feature/agent-c-test-replay` | Merged into `integration/wave1-agent-integration` |
| `feature/agent-d-runtime-ledger` | Merged into `integration/wave1-agent-integration` |
| `controller/bar-wo-06-controller` | **KEEP_ACTIVE** — separate controller series |

## Baseline

- `D:\llm-agents` (baseline) — NOT modified
- `integration/wave1-foundation` — NOT modified
- Remote branches — NOT deleted

### Status: ✅ CLOSED — WO-OBSIDIAN-015
