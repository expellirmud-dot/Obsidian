# WO-OBSIDIAN-014 — Reconcile and remove eh-03r-mainline-attestation

## Target

- Worktree: `D:/d/llm-agents-worktrees/eh-03r-mainline-attestation`
- Branch: `controller/eh-03r-re-attestation` (HEAD `b9b4c56`)

## Pre-Flight: WO-06.2 Provenance Review

| Check | eh-03r (untracked) | bar-wo-06 (tracked) | Verdict |
|-------|:------------------:|:-------------------:|:-------:|
| `work-order.json` | ✅ exists (identical) | ✅ committed | **DUPLICATE_OF_TRACKED** |
| `controller-order.md` | ❌ missing | ✅ committed | n/a |
| `worker-handoff.md` | ❌ missing | ✅ committed | n/a |
| Content match | 100% identical | — | Exact copy |

**Decision:** eh-03r's `work_orders/active/WO-06.2/work-order.json` is a **DUPLICATE_OF_TRACKED** — no unique evidence.

## Branch Relationship

- `controller/eh-03r-re-attestation` is an **ancestor** of `controller/bar-wo-06-controller` (exit=0)
- Commit `b9b4c56` is PRESERVED_IN_BAR_BRANCH (confirmed via `git branch --contains`)
- Unique commits vs bar-wo-06: `5 0` (eh-03r has 0 unique)
- Code: **SUPERSEDED** by bar-wo-06-controller

## Execution

```bash
# Worktree remove (--force for disposable untracked WO-06.2 duplicate)
git worktree remove --force "D:/d/llm-agents-worktrees/eh-03r-mainline-attestation"  # exit=0

# Branch delete (commit preserved in bar-wo-06-controller)
git branch controller/eh-03r-re-attestation --set-upstream-to=controller/bar-wo-06-controller
git branch -d controller/eh-03r-re-attestation  # exit=0

# Prune
git worktree prune  # exit=0
```

## Final Report

| Field | Value |
|-------|-------|
| **RESULT** | SUCCESS — reconciled + removed |
| **WORKTREE REMOVED** | eh-03r-mainline-attestation |
| **BRANCH REMOVED** | controller/eh-03r-re-attestation (b9b4c56 preserved in bar-wo-06) |
| **REMOTE BRANCHES** | 0 (no remote deletion) |
| **BASELINE** | NOT modified |
| **EVIDENCE** | WO-06.2 = DUPLICATE_OF_TRACKED, code = SUPERSEDED |

### Status: ✅ CLOSED — WO-OBSIDIAN-014
