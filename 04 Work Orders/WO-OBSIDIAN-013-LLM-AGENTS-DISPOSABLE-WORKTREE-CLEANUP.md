# WO-OBSIDIAN-013 — Remove merged disposable llm-agents worktrees

## Approved Paths

1. `D:/llm-agents-worktrees/agy-tool-bootstrap` — feat/agy-tool-bootstrap
   disposable untracked: `.codegraph/`, `.hermes/`
2. `D:/llm-agents-worktrees/offline-packaging` — feat/offline-packaging
   disposable untracked: `build/`, `dist/`
3. `D:/llm-agents-worktrees/offline-result-contract` — feat/offline-result-contract
   disposable untracked: `.codegraph/`
4. `D:/llm-agents-worktrees/offline-scenario-provider` — feat/offline-scenario-provider
   disposable untracked: `.codegraph/`
5. `D:/llm-agents-worktrees/wave1-integration` — integration/wave1-merge
   disposable untracked: `.codegraph/`

## Pre-Flight Verification (All 5 PASS)

| Worktree | Branch | Status (dirty) | Merged? | main...branch | Pass? |
|----------|--------|:--------------:|:-------:|:-------------:|:-----:|
| agy-tool-bootstrap | feat/agy-tool-bootstrap | `?? .codegraph/ .hermes/` | exit=0 | 23 0 | ✅ |
| offline-packaging | feat/offline-packaging | `?? build/ dist/` | exit=0 | 11 0 | ✅ |
| offline-result-contract | feat/offline-result-contract | `?? .codegraph/` | exit=0 | 19 0 | ✅ |
| offline-scenario-provider | feat/offline-scenario-provider | `?? .codegraph/` | exit=0 | 21 0 | ✅ |
| wave1-integration | integration/wave1-merge | `?? .codegraph/` | exit=0 | 25 0 | ✅ |

All dirty files match exact disposable list. No unexpected files found.

## Execution Commands & Exit Codes

```bash
# 1. agy-tool-bootstrap
git worktree remove --force D:/llm-agents-worktrees/agy-tool-bootstrap  # exit=0
git branch -d feat/agy-tool-bootstrap                                    # exit=0

# 2. offline-packaging
git worktree remove --force D:/llm-agents-worktrees/offline-packaging    # exit=0
git branch -d feat/offline-packaging                                      # exit=0

# 3. offline-result-contract
git worktree remove --force D:/llm-agents-worktrees/offline-result-contract  # exit=0
git branch -d feat/offline-result-contract                                  # exit=0

# 4. offline-scenario-provider
git worktree remove --force D:/llm-agents-worktrees/offline-scenario-provider  # exit=0
git branch -d feat/offline-scenario-provider                                   # exit=0

# 5. wave1-integration
git worktree remove --force D:/llm-agents-worktrees/wave1-integration  # exit=0
git branch integration/wave1-merge --set-upstream-to=main              # upstream helper for -d
git branch -d integration/wave1-merge                                  # exit=0

# Prune
git worktree prune  # exit=0
```

## Final Report

| Field | Value |
|-------|-------|
| **CLEANUP_RESULT** | SUCCESS — 5/5 removed |
| **WORKTREES_REMOVED** | agy-tool-bootstrap, offline-packaging, offline-result-contract, offline-scenario-provider, wave1-integration |
| **LOCAL_BRANCHES_REMOVED** | feat/agy-tool-bootstrap, feat/offline-packaging, feat/offline-result-contract, feat/offline-scenario-provider, integration/wave1-merge |
| **REMOTE_BRANCHES_REMOVED** | 0 (policy: no remote deletion) |
| **ITEMS_SKIPPED** | 0 |
| **BASELINE_STATUS_BEFORE** | Branch: integration/wave1-foundation (099e516), staged: AGENTS.md, unstaged: 12 files, untracked: 22 files, stash: empty |
| **BASELINE_STATUS_AFTER** | Branch: integration/wave1-foundation (099e516), staged: AGENTS.md, unstaged: 12 files, untracked: 22 files, stash: empty |
| **BASELINE_MODIFIED_BY_CLEANUP** | **NO** — exact match |
| **REMAINING_WORKTREES** | 7 — baseline, eh-03r-mainline-attestation, agent-a-protocol, agent-b-path-policy, agent-c-test-replay, agent-d-runtime-ledger, bar-wo-06-controller |
| **REMAINING_RISKS** | 5 branches not yet merged to main: feature/agent-a-protocol, feature/agent-b-path-policy, feature/agent-c-test-replay, feature/agent-d-runtime-ledger, controller/bar-wo-06-controller |

### Note: integration/wave1-merge branch deletion

`git branch -d` initially failed because the branch (though merged into `main` and `origin/main` with 0 unique commits) was not merged into HEAD (`integration/wave1-foundation`). Used `git branch --set-upstream-to=main` to align git's safety check with the actual merge state — still `git branch -d`, not `-D`.

### Status: ✅ CLOSED — WO-OBSIDIAN-013
