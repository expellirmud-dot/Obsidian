# WO-OBSIDIAN-018 — Close bar-wo-06-controller (controller series)

## Scope

Close the `controller/bar-wo-06-controller` worktree. This is the active controller series with 6 unique commits vs main and 40 commits ahead of `integration/wave1-foundation`.

## Pre-Flight

### Current State
- Branch: `controller/bar-wo-06-controller`
- HEAD: `8e2c854`
- Worktree: `D:/llm-agents-worktrees/bar-wo-06-controller`
- Untracked: `work_orders/active/WO-10/` (retry classification bug fix)
- Unique commits vs main: 40
- Status: dirty (1 untracked directory)

### Authority Check
- `D:\llm-agents\work_orders\CURRENT_WORK_ORDER.md` points to `WO-10`
- `WO-10` is in progress (retry classification)
- bar-wo-06 is the active controller — must close WO-10 first

## Bounded Seams

### Seam 1: WO-10 Retry Classification Validation
- Validate the retry classification fix in `WO-10`
- Run any existing tests for the retry logic
- If validation passes, commit the WO-10 evidence

### Seam 2: Close bar-wo-06-controller
- Archive WO-10 evidence
- Remove worktree (clean or `--force` for disposable untracked)
- Delete local branch `controller/bar-wo-06-controller`
- `git worktree prune`

## Constraints

- Never use `git branch -D` (use `-d` only)
- Never use `git clean`, `reset --hard`, `rm -rf`
- Never delete remote branches
- Never touch baseline `D:\llm-agents` (36 dirty files)
- Never touch `integration/wave1-agent-integration`
- Never touch `integration/wave1-foundation`
- Baseline before/after must be identical
- Vault commit for closeout only
- No push until closeout verified

## Acceptance Gates

- [ ] WO-10 retry classification validated
- [ ] WO-10 evidence committed/archived
- [ ] bar-wo-06-controller worktree removed
- [ ] Branch deleted via `-d`
- [ ] `git worktree prune` clean
- [ ] Baseline unchanged (36 entries)
- [ ] Full suite passes (265 tests)
- [ ] No untracked evidence clogging worktree
- [ ] WO-OBSIDIAN-018 created in Vault
- [ ] Vault commit pushed

## Final Report Template

```
WORK_COMPLETED: ...
COMMITS_CREATED: ...
TEST_RESULTS: ...
FULL_SUITE_RESULT: ...
MERGE_TARGET: N/A (controller series, no merge)
MERGE_RESULT: N/A
WORK_ORDER_STATUS: CLOSED
WORKTREE_STATUS: clean (0 entries)
BRANCH_STATUS: controller/bar-wo-06-controller deleted
BASELINE_STATUS_BEFORE: 36 entries
BASELINE_STATUS_AFTER: 36 entries (identical)
PUSH_STATUS: pending
REMAINING_RISKS: ...
```

### Status: ⏳ PLANNED — Awaiting WO-10 validation
