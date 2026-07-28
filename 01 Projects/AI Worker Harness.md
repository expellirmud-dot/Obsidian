---
type: project
status: verified
priority: medium
project_path: D:\ai-tools\ai-worker-harness
repository: https://github.com/expellirmud-dot/ai-worker-harness.git
current_work_order: WO-G9-R07-TASK-CLASS-EVALUATION-ROBUSTNESS (Goal-09, R07 live campaign)
last_reviewed: 2026-07-28
---

# AI Worker Harness

> สถานะจริงตรวจจาก Repository Commit 7096991 (2026-07-28 ตาม WO-OBSIDIAN-006)
> แหล่ง truth: AGENTS.md, README.md, work-order/CURRENT_WORK_ORDER.md, docs/HARNESS_CURRENT_STATUS.md, docs/GOAL_EXECUTION_CONTRACT.md, docs/DOCS_INDEX.md

## โปรเจกต์นี้คืออะไร

Bounded, evidence-driven control plane สำหรับรันและประเมิน CLI coding Workers ภายใต้ Work Orders ที่ชัดเจน — แยกบทบาท Controller, CLI Worker, Harness Worker, Harness Runtime

## ปัญหาที่ต้องการแก้

- ต้องการระบบออกคำสั่งงาน (Work Order) ที่ตรวจสอบขอบเขตได้
- ต้องการแยก Controller (วางแผน/ตรวจสอบ) กับ Worker (ปฏิบัติ) อย่างชัดเจน
- ต้องการหลักฐานการทำงาน (evidence) ที่ตรวจสอบได้ ไม่ใช่แค่รายงานสรุป
- ต้องการรันและประเมิน AI Worker ภายใต้ budget, route policy, และ acceptance criteria ที่กำหนด
- ต้องการแยก Goal completion ออกจาก readiness — evaluation failure ไม่ใช่ implementation defect

## เป้าหมายหลัก

1. ระบบ Work Order lifecycle: validate → activate → execute → closeout
2. Controller/Worker role separation: Controller เลือก seam, ตรวจ evidence, commit; Worker implement ภายใต้ขอบเขต
3. Evidence-driven evaluation: deterministic evidence, per-case records, terminal status classification
4. Route/provider policy: config/models.json + config/route_selection_policy.json
5. Campaign/Goal completion: finite evidence plan → COMPLETE_READY / COMPLETE_NOT_READY / COMPLETE_INCONCLUSIVE

## ขอบเขต

### In Scope

- Work Order creation, validation, activation, and closeout
- Controller/CLI Worker/Harness Worker/Harness Runtime role separation
- ToolGate enforcement for runtime safety
- Per-case evidence collection and settlement
- Route selection and provider policy
- Bounded corrective passes for implementation defects only
- Exception-driven reporting

### Out of Scope

- Production-default autonomous operation (currently `NOT_READY`)
- OpenHands as edit-capable production backend (read-only bridge currently)
- Real OS/window automation
- External API/service calls outside configured provider routes
- Credential/secret management
- Multi-repository orchestration

## ตำแหน่งไฟล์จริง

`D:\ai-tools\ai-worker-harness`

## Repository

https://github.com/expellirmud-dot/ai-worker-harness.git
Remote branch inspected: `origin/main`

## สถานะปัจจุบัน

VERIFIED_REPOSITORY_FACT — ตรวจสอบแล้ว 2026-07-28:

- Branch: main
- HEAD: 7096991892cead77a40c0178c57c9589839b1518
- Git Status: 1 modified (work-order/templates/CONTROLLER_SESSION_BOOTSTRAP.md), 3 untracked (.benchmark-sandbox/r07-runs/, work-order/Goal-10.md, work-order/HARNESS_GOAL09_CONTROLLER_HANDOFF.md)
- Active Goal: Goal-09 — Runtime Observability, Information Sufficiency, and Model Evaluation
- Active Work Order: WO-G9-R07-TASK-CLASS-EVALUATION-ROBUSTNESS (R07 live campaign, ACTIVE)
- Shell/Python: D:\ai-tools\ai-worker-harness\.venv\Scripts\python.exe
- Full suite: no fresh result for current HEAD (historical: 962 passed at fd69aa1)
- Goal-09 R07: ACTIVE — 10 task classes, sentinel batch TC-01+TC-07, route google-gemma-main
- Goal-10: inactive — not part of current authority

VERIFIED_REPOSITORY_FACT:
- Git Status: 1 modified (work-order/templates/CONTROLLER_SESSION_BOOTSTRAP.md), 3 untracked (.benchmark-sandbox/r07-runs/, work-order/Goal-10.md, work-order/HARNESS_GOAL09_CONTROLLER_HANDOFF.md)

SUPPORTED_INFERENCE:
- ไฟล์ที่ modified/untracked ดูเกี่ยวข้องกับ Goal-09/R07 campaign แต่ provenance ไม่ได้รับการยืนยันจาก repository fact

EXECUTION_WARNING:
- ต้อง reconcile provenance และ authority ของ dirty files ก่อนใช้เป็นฐานรันงานต่อ

## สิ่งที่ทำเสร็จแล้ว

- Canonical AGENTS.md defining roles, safety, repository operation
- README.md with execution model and entry points
- docs/HARNESS_CURRENT_STATUS.md — single owner of current verified state
- docs/GOAL_EXECUTION_CONTRACT.md — Goal continuation, completion, campaign budgets
- docs/DOCS_INDEX.md — document routing map
- work-order/CURRENT_WORK_ORDER.md — active pointer mechanism
- work-order/Goal-09.md — R07 evaluator roadmap
- R07 offline acceptance: 13 deterministic gates PASS (READY_FOR_LIVE_R07 at a0f9814)
- R07 evaluator hardening: offline architecture, process supervision, atomic per-case evidence
- Historical Goal-01 through Goal-08 closed with recorded outputs
- OpenHands read-only bridge (optional, not production default)
- Canonical validation commands defined

## งานที่กำลังทำ

Goal-09 R07 live campaign (WO-G9-R07-TASK-CLASS-EVALUATION-ROBUSTNESS):
1. Validate fresh route health for google-gemma-main (primary)
2. Run sentinel batch TC-01 + TC-07
3. If sentinel passes, run remaining TC-02–06, 08–10
4. Close R07 with observed result
5. Execute R08 from available evidence
6. Issue final Goal-09 disposition (COMPLETE_READY / COMPLETE_NOT_READY / COMPLETE_INCONCLUSIVE)

## สถาปัตยกรรม

ดู [[ARCH-AI-Worker-Harness-Overview]]

## การตัดสินใจสำคัญ

- Controller owns Goal/seam, architecture, evidence review, commit — ไม่ใช่ Worker
- Completed ≠ ready: finite evidence plan can end COMPLETE_NOT_READY หรือ COMPLETE_INCONCLUSIVE
- Evaluation outcome ≠ implementation defect — ห้าม patch evaluation failure toward PASS
- Two-commit lifecycle: (1) Work Order + pointer, (2) implementation/evidence + pointer closeout
- Goal authority persists across seams, commits, and session changes
- Exception-driven reporting — routine activation/validation/closeout ไม่ต้องรายงาน

## ปัญหาและความเสี่ยง

- No fresh complete-suite result for current HEAD
- Goal-09 has not produced task-class qualification matrix or final readiness decision
- R07 live attempts 1–2 closed INCONCLUSIVE/NOT_SCOREABLE (evidence loss, process settlement failure)
- R06 remains non-scoreable
- Worktree dirty: 1 modified + 3 untracked — ต้องตรวจก่อน execute งานใด
- Production-default autonomous operation remains NOT_READY
- Route health must be validated fresh per run (historical PASS does not qualify)
- Provider mixing inside one task is forbidden
- OpenHands read-only bridge exists but is not production-capable

## Resume Context

### Read-First Order (Next Session)

1. AGENTS.md — role/safety authority
2. work-order/CURRENT_WORK_ORDER.md — active pointer
3. docs/HARNESS_CURRENT_STATUS.md — current verified state
4. docs/GOAL_EXECUTION_CONTRACT.md — Goal completion/rules
5. docs/DOCS_INDEX.md — document routing
6. Active Goal (work-order/Goal-09.md) + active Work Order
7. README.md, AI_WORKER_HARNESS_OPERATION_GUIDE.md, .agents/skills/ai-worker-harness/SKILL.md

### Identity

- Active Path: D:\ai-tools\ai-worker-harness
- Python: .venv\Scripts\python.exe
- Shell: Harness Runtime (ToolGate + process isolation)
- Active Goal: Goal-09 (R07 live campaign)
- Tools: opencode, gemini (CLI Workers); Codex (Controller path — NEEDS_VERIFICATION: routing policy เปลี่ยนง่าย)

### Active State

- Current Work Order: WO-G9-R07-TASK-CLASS-EVALUATION-ROBUSTNESS (ACTIVE)
- Git HEAD: 7096991892cead77a40c0178c57c9589839b1518
- Worktree: 1 modified + 3 untracked
- Suite: no fresh result for current HEAD
- Next major action: execute R07 sentinel batch (TC-01 + TC-07)

### Safety

- ห้ามแก้ source, tests, configuration, หรือ Git state ของ ai-worker-harness
- ห้าม dispatch Worker/Provider หรือรัน live evaluation จาก Vault context
- ห้ามติดตั้ง dependency
- ห้าม commit/push ใน Source Repository
- ห้ามใช้ internal subagent แทน CLI Worker
- Real OS/window actions ต้อง Owner approval

## วันที่ตรวจสอบล่าสุด

2026-07-28 (WO-OBSIDIAN-006)

## Verification Record

- Repository checked: Yes (WO-OBSIDIAN-006)
- Git branch: main
- Git HEAD: 7096991892cead77a40c0178c57c9589839b1518
- Git Status: 1 modified, 3 untracked
- Current Work Order checked: Yes (WO-G9-R07-TASK-CLASS-EVALUATION-ROBUSTNESS, ACTIVE)
- Runtime/provider dispatched: No
- Repository files modified: 0
- Evidence Sources: AGENTS.md, README.md, work-order/CURRENT_WORK_ORDER.md, docs/HARNESS_CURRENT_STATUS.md, docs/GOAL_EXECUTION_CONTRACT.md, docs/DOCS_INDEX.md
- Verified by: WO-OBSIDIAN-006 (AI)
- Verification date: 2026-07-28

## เอกสารที่เกี่ยวข้อง

- [[Project Dashboard]]
- [[Project Index]]
- [[ARCH-AI-Worker-Harness-Overview]]
- [[Work Order Index]]
- [[Prompt Index]]
- [[Project Resume Workflow]]
