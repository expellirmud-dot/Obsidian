# WO-OBSIDIAN-016 — Remove merged agent A/B/C/D worktrees (post-integration cleanup)

## Approved Targets

| # | Worktree Path | Branch | Notes |
|---|---------------|--------|-------|
| 1 | `D:/llm-agents-worktrees/agent-a-protocol` | `feature/agent-a-protocol` | Merged into `integration/wave1-agent-integration` via WO-015 |
| 2 | `D:/llm-agents-worktrees/agent-b-path-policy` | `feature/agent-b-path-policy` | Merged into `integration/wave1-agent-integration` via WO-015 |
| 3 | `D:/llm-agents-worktrees/agent-c-test-replay` | `feature/agent-c-test-replay` | Merged into `integration/wave1-agent-integration` via WO-015 |
| 4 | `D:/llm-agents-worktrees/agent-d-runtime-ledger` | `feature/agent-d-runtime-ledger` | Merged into `integration/wave1-agent-integration` via WO-015 |

## Pre-Flight Conditions (ทุกข้อต้องผ่าน)

ตรวจแต่ละ worktree ก่อนลบ:

### Branch ancestor check
```bash
INTEGRATION="integration/wave1-agent-integration"
for branch in feature/agent-a-protocol feature/agent-b-path-policy \
              feature/agent-c-test-replay feature/agent-d-runtime-ledger; do
    git merge-base --is-ancestor "$branch" "$INTEGRATION"
    echo "exit=$?"
done
```
ต้องได้ exit=0 ทั้ง 4

### Unique commits check
```bash
for branch in feature/agent-a-protocol feature/agent-b-path-policy \
              feature/agent-c-test-replay feature/agent-d-runtime-ledger; do
    git rev-list --left-right --count "$INTEGRATION...$branch"
done
```
ต้องมี unique commits ฝั่ง branch = 0 ทุกรายการ

### Worktree status check
```bash
for wt in agent-a-protocol agent-b-path-policy agent-c-test-replay agent-d-runtime-ledger; do
    git -C "D:/llm-agents-worktrees/$wt" status --short
done
```

- B, C, D ต้อง clean (ไม่มี modified/untracked)
- A ต้องมีเฉพาะ `scratch/` และ `valid_fixtures.json` (classified as REGENERATABLE_SCRATCH per WO-015) — ห้ามมีไฟล์อื่น

### Agent A untracked provenance — Verify per WO-015 decision
```bash
# Confirm untracked files match approved disposable list
git -C "D:/llm-agents-worktrees/agent-a-protocol" status --porcelain | sort
```
Expected output:
```
?? scratch/
?? valid_fixtures.json
```
หากมีไฟล์อื่น → **SKIP** รายการนี้ทันที

## Removal Commands

### B, C, D (clean worktrees — no --force needed)
```bash
for wt in agent-b-path-policy agent-c-test-replay agent-d-runtime-ledger; do
    git worktree remove "D:/llm-agents-worktrees/$wt"
    echo "worktree remove $wt: exit=$?"
done
```

### Agent A (dirty with disposable untracked — requires --force)
```bash
# Verify untracked matches approved list BEFORE --force
git -C "D:/llm-agents-worktrees/agent-a-protocol" status --porcelain
# If only scratch/ and valid_fixtures.json:
git worktree remove --force "D:/llm-agents-worktrees/agent-a-protocol"
echo "worktree remove agent-a-protocol: exit=$?"
```

### Branch deletion (merged into integration branch, must use -d not -D)
```bash
for branch in feature/agent-a-protocol feature/agent-b-path-policy \
              feature/agent-c-test-replay feature/agent-d-runtime-ledger; do
    # Set upstream to integration for git branch -d compatibility
    git branch "$branch" --set-upstream-to=integration/wave1-agent-integration
    git branch -d "$branch"
    echo "branch -d $branch: exit=$?"
done
```

### Prune
```bash
git worktree prune
```

## Constraints

- ห้ามใช้ `git branch -D` (ใช้ `-d` เท่านั้น)
- ห้ามใช้ `git clean`, `reset --hard`, `rm -rf`
- ห้ามลบ remote branches
- ห้ามแตะ baseline `D:\llm-agents`
- ห้ามแตะ `integration/wave1-agent-integration` branch
- ห้ามแตะ `controller/bar-wo-06-controller`
- Baseline status ก่อนและหลังต้องเหมือนเดิม
- Vault commit เฉพาะการปิด WO (ไม่ Push จนกว่าจะตรวจ)

## Disposable Content Classification

จาก WO-015:

| File/Path | Classification | Rationale |
|-----------|:--------------:|-----------|
| `scratch/` (10 files) | **REGENERATABLE_SCRATCH** | Dev debug scripts; not referenced by any tracked code |
| `valid_fixtures.json` (78 lines) | **REGENERATABLE_SCRATCH** | Parser test vectors; not referenced by any test or tracked file (confirmed via `grep -r`) |

## Baseline Protection

- Record `git status` + `git worktree list` BEFORE
- Record `git status` + `git worktree list` AFTER
- Both must be identical except worktree list (4 fewer entries)

## Final Report Template

```
WO-OBSIDIAN-016 — FINAL REPORT
WORKTREES_REMOVED:     (count)
LOCAL_BRANCHES_REMOVED: (count)
REMOTE_BRANCHES:       0 (policy)
ITEMS_SKIPPED:         (count, with reason)
BASELINE_MODIFIED:     YES/NO
REMAINING_WORKTREES:   (list)
REMAINING_RISKS:       (notes)
```

## Execution Verification

### Pre-Flight Results

| Check | agent-a | agent-b | agent-c | agent-d |
|-------|:-------:|:-------:|:-------:|:-------:|
| Ancestor of wave1-agent-integration | ✅ exit=0 | ✅ exit=0 | ✅ exit=0 | ✅ exit=0 |
| Unique commits (branch side) | 0 | 0 | 0 | 0 |
| Status | `scratch/` + `valid_fixtures.json` | ✅ clean | ✅ clean | ✅ clean |

### Removal Commands & Exit Codes

```bash
# B, C, D — clean, no --force
git worktree remove D:/llm-agents-worktrees/agent-b-path-policy    # exit=0
git branch -d feature/agent-b-path-policy                          # exit=0
git worktree remove D:/llm-agents-worktrees/agent-c-test-replay    # exit=0
git branch -d feature/agent-c-test-replay                          # exit=0
git worktree remove D:/llm-agents-worktrees/agent-d-runtime-ledger # exit=0
git branch -d feature/agent-d-runtime-ledger                       # exit=0

# A — disposable untracked (scratch/, valid_fixtures.json), --force
git worktree remove --force D:/llm-agents-worktrees/agent-a-protocol  # exit=0
git branch -d feature/agent-a-protocol                                 # exit=0

# Prune
git worktree prune  # exit=0
```

### Baseline Comparison

| Check | BEFORE | AFTER | Match? |
|-------|--------|-------|:------:|
| git status | 36 entries | 36 entries | ✅ |
| HEAD | 099e516 | 099e516 | ✅ |
| git log -3 | 099e516, ed977c2, 20bdc46 | Same | ✅ |
| Stash | empty | empty | ✅ |
| Baseline branch | integration/wave1-foundation | integration/wave1-foundation | ✅ |

## Final Report

| Field | Value |
|-------|-------|
| **WORKTREES_REMOVED** | 4 — agent-a-protocol, agent-b-path-policy, agent-c-test-replay, agent-d-runtime-ledger |
| **LOCAL_BRANCHES_REMOVED** | 4 — feature/agent-a-protocol, feature/agent-b-path-policy, feature/agent-c-test-replay, feature/agent-d-runtime-ledger |
| **REMOTE_BRANCHES** | 0 (policy: no remote deletion) |
| **ITEMS_SKIPPED** | 0 |
| **BASELINE_MODIFIED** | **NO** — identical before/after |
| **REMAINING_WORKTREES** | 3 — baseline, bar-wo-06-controller (KEEP_ACTIVE), wave1-agent-integration (PRESERVE) |
| **REMAINING_RISKS** | None. All agent branches preserved as commits in integration/wave1-agent-integration. |

### Status: ✅ CLOSED — WO-OBSIDIAN-016
