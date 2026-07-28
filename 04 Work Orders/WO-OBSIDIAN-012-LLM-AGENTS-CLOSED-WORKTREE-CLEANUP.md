ดำเนินการ Cleanup รอบที่ 1 สำหรับ llm-agents เฉพาะรายการที่ Owner อนุมัติ:

1. D:/llm-agents-worktrees/agy-pre-dispatch-governance
   branch: feat/agy-pre-dispatch-governance

2. D:/llm-agents-worktrees/offline-desktop-app
   branch: feat/offline-desktop-app

3. D:/llm-agents-worktrees/offline-job-queue
   branch: feat/offline-job-queue

4. D:/llm-agents-worktrees/offline-wts-integration
   branch: feat/offline-wts-integration

Repository:
D:/llm-agents

ข้อบังคับ:
- ห้ามแตะ baseline D:/llm-agents
- ห้ามแก้ ลบ stage commit หรือ push ไฟล์ใน baseline
- ตรวจ worktree แต่ละรายการใหม่ก่อนลบ
- ต้อง clean จริง
- branch ต้อง merged into main จริง
- ต้องไม่มี unique commits
- หาก state ต่างจาก Inventory ให้ SKIP รายการนั้นทันที
- ห้ามใช้ git clean
- ห้ามใช้ reset --hard
- ห้ามใช้ rm -rf
- ห้ามลบ remote branches
- ลบทีละรายการด้วย git worktree remove
- หลัง remove สำเร็จจึงลบ local branch ด้วย git branch -d
- ห้ามใช้ -D
- รัน git worktree prune หลังลบครบ
- ตรวจ baseline status ก่อนและหลัง ต้องเหมือนเดิมทุกประการ

ลำดับ:
1. บันทึก BASELINE_STATUS_BEFORE
2. ตรวจ git worktree list --porcelain
3. ตรวจ git status ของแต่ละ worktree
4. ตรวจ git merge-base --is-ancestor <branch> main
5. ตรวจ git rev-list --left-right --count main...<branch>
6. ลบ worktree ทีละรายการ
7. ลบ local branch ด้วย -d
8. git worktree prune
9. บันทึก BASELINE_STATUS_AFTER
10. รายงาน exact commands และ exit codes

## Final Report

| Field | Value |
|-------|-------|
| **CLEANUP_RESULT** | SUCCESS — 4/4 removed |
| **WORKTREES_REMOVED** | 1. `D:/llm-agents-worktrees/agy-pre-dispatch-governance` — feat/agy-pre-dispatch-governance<br>2. `D:/llm-agents-worktrees/offline-desktop-app` — feat/offline-desktop-app<br>3. `D:/llm-agents-worktrees/offline-job-queue` — feat/offline-job-queue<br>4. `D:/llm-agents-worktrees/offline-wts-integration` — feat/offline-wts-integration |
| **LOCAL_BRANCHES_REMOVED** | feat/agy-pre-dispatch-governance, feat/offline-desktop-app, feat/offline-job-queue, feat/offline-wts-integration |
| **REMOTE_BRANCHES_REMOVED** | 0 (policy: no remote deletion) |
| **ITEMS_SKIPPED** | 0 — all 4 passed pre-flight checks |
| **BASELINE_STATUS_BEFORE** | Branch: integration/wave1-foundation (099e516), staged: AGENTS.md, unstaged: 12 files, untracked: 22 files, stash: empty |
| **BASELINE_STATUS_AFTER** | Branch: integration/wave1-foundation (099e516), staged: AGENTS.md, unstaged: 12 files, untracked: 22 files, stash: empty |
| **BASELINE_MODIFIED_BY_CLEANUP** | **NO** — exact match on all checks |
| **REMAINING_WORKTREES** | 10 — eh-03r-mainline-attestation, agent-a-protocol, agent-b-path-policy, agent-c-test-replay, agent-d-runtime-ledger, agy-tool-bootstrap, bar-wo-06-controller, offline-packaging, offline-result-contract, offline-scenario-provider, wave1-integration |
| **REMAINING_RISKS** | None for this batch. REMAINING WORKTREES NOT IN SCOPE of WO-OBSIDIAN-012. |

### Verification Commands & Exit Codes

```bash
# 1. agy-pre-dispatch-governance
git worktree remove D:/llm-agents-worktrees/agy-pre-dispatch-governance  # exit=0
git branch -d feat/agy-pre-dispatch-governance                            # exit=0

# 2. offline-desktop-app
git worktree remove D:/llm-agents-worktrees/offline-desktop-app          # exit=0
git branch -d feat/offline-desktop-app                                    # exit=0

# 3. offline-job-queue
git worktree remove D:/llm-agents-worktrees/offline-job-queue            # exit=0
git branch -d feat/offline-job-queue                                      # exit=0

# 4. offline-wts-integration
git worktree remove D:/llm-agents-worktrees/offline-wts-integration      # exit=0
git branch -d feat/offline-wts-integration                                # exit=0

# Prune
git worktree prune                                                        # exit=0
```

### Status: ✅ CLOSED — WO-OBSIDIAN-012