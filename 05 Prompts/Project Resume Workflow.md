---
type: workflow
title: Project Resume Workflow
last_reviewed: 2026-07-29
---

# Project Resume Workflow

Workflow มาตรฐานสำหรับกลับมาทำงานแต่ละโปรเจกต์จาก Vault โดยไม่ใช้ข้อมูลล้าสมัย ไม่ข้าม authority และไม่แก้ Source Repository ก่อน readiness gate ผ่าน

## Scope

- ใช้กับทุกโปรเจกต์ใน Vault
- ใช้กับทุก session ที่ resume โปรเจกต์จาก Vault
- ไม่ใช่ instruction สำหรับแก้ source code โดยตรง

## 1. Resume Checklist

ใช้ steps นี้เสมอเมื่อกลับมาทำงาน:

1. **เลือก Project page** — เปิด `01 Projects/<Project>.md`
2. **อ่าน Resume Context และ Verification Record** — ตรวจ `last_verified_head`, `last_verified_date`, `verification_scope`
3. **ตรวจ staleness** — ใช้ policy จาก `03 Decisions/DEC-Vault-Staleness-and-Reverification-Policy.md`
4. **Resolve exact Source Git root** — รัน `git rev-parse --show-toplevel` จาก source path
5. **ตรวจ branch, HEAD, upstream, status** — รันคำสั่ง git truth จาก exact root
6. **ตรวจ authority pointer** — ตรวจ current task/work order pointer ใน source repo
7. **ตัดสิน re-verification ระดับ** — ใช้ decision tree ข้างล่าง
8. **สร้าง bounded Work Order ใหม่** — ถ้าจำเป็น; ใช้ template ข้างล่าง
9. **ตรวจ Serena/CodeGraph** — เฉพาะเมื่อจะ inspect source code; ต้องตรง exact root
10. **Validation, explicit staging, single-task commit, push authorization** — ตาม workflow template
11. **Closeout และอัปเดต Vault** — เมื่อ repository truth เปลี่ยน

## 2. Readiness Gate

Workflow เริ่มได้เมื่อ:

- Vault preflight ผ่าน (`PREFLIGHT_DECISION: READY`)
- Work Order ใหม่ valid และ approved
- Source repository truth ตรวจแล้ว
- Serena/CodeGraph ตรง exact root ถ้าจำเป็น

หยุดทันทีเมื่อ:

- repository path ไม่ตรงกับ Vault record
- authority files ขัดแย้ง
- dirty state ทำให้ current-state summary ไม่ไว้ใจได้
- ต้องแก้ source repository ก่อน readiness gate ผ่าน
- ต้องการ secret/credential/Owner decision ที่ยังไม่มี
- Serena/CodeGraph mismatch เมื่อจำเป็นต้อง inspect source code

## 3. Staleness / Re-verification Decision Tree

```
อ่าน Resume Context
    │
    ▼
ตรวจ last_verified_head == current HEAD?
    │
    ├─ no → ต้องตรวจ branch/HEAD/upstream/status + current task pointer
    │
    ▼
ตรวจ last_verified_date เกิน threshold ตามสถานะ?
    │
    ├─ active >30 วัน → ตรวจ minimum checks
    ├─ paused/verified/completed >90 วัน → ตรวจ minimum checks
    │
    ▼
ตรวจ triggers: HEAD/current_task/authority/dirty_state/scope เปลี่ยน?
    │
    ├─ yes → ตรวจ minimum checks ตามสถานะ
    │
    ▼
ตรวจ Dirty state เปลี่ยนแปลง?
    │
    ├─ dirty เป็น local artifact เท่านั้น → dirty-observation only
    ├─ dirty กระทู้ authority/config/docs → requires re-verification
    │
    ▼
อัปเดต evidence classification:
- VERIFIED_REPOSITORY_FACT: ตรวจจาก file content/command output ในรอบนี้
- OWNER_CONFIRMED_FACT: 声明โดย Owner
- SUPPORTED_INFERENCE: reasoned จาก verified facts
- NEEDS_VERIFICATION: ยังไม่ตรวจ หรือ trigger ใหม่แต่ยังไม่ตรวจ
```

## 4. Source Read-Only Preflight

ก่อนแก้ source repository ใด ๆ:

1. รัน `git rev-parse --show-toplevel` เพื่อยืนยัน exact root
2. รัน `git status --short` เพื่อดู tracked/untracked
3. ตรวจว่าไม่มี tracked modifications ที่ไม่เกี่ยวข้อง
4. ตรวจว่าไม่มี untracked files ที่เสี่ยงเป็น secret/credential
5. ตรวจ authority pointer ปัจจุบัน
6. ถ้าเจอ stop condition → ห้ามแก้ source และรายงานต่อ Controller/Owner

## 5. Bounded Work Order Bootstrap Template

```markdown
# WORK ORDER — < título >
Work Order ID: WO-<project>-<number>-<title>
Title: <title>
Status: PLANNED
Task Classification: <classification>
Risk Level: <level>
Execution Mode: <mode>
Owner: <owner>
Vault Root: <vault root>
Source Repository: <source path>
Depends On: <dependencies>
Commit Authorization: YES/NO
Push Authorization: YES/NO

## Objective
< jedno paragraph >

## Required Read Order
1. Vault authority
2. Active Work Order
3. Project page + Resume Context
4. Source authority files
5. Targeted source inspection (เฉพาะเมื่อ필요)

## Boundaries
- Vault-only / Source read-only / ...
- ห้าม...

## Required Outputs
- Allowed files only

## Validation
< explicit checklist >

## Definition of Done
1. ...
2. ...
3. ...

Commit message: <message>
```

## 6. Stop-Condition Template

```markdown
STOP CONDITION
- Trigger: ...
- Evidence: ...
- Action: stop and report to Controller/Owner
- Next: ...
```

## 7. Final Report Template

```text
WORK_ORDER: <id>
RESULT: COMPLETED | PARTIAL | BLOCKED
SOURCE_REPOSITORY_ROOT:
SOURCE_BRANCH:
SOURCE_HEAD:
SOURCE_GIT_STATUS:
SOURCE_FILES_MODIFIED:
RUNTIME_ACTIONS_PERFORMED:
VAULT_COMMIT:
FILES_CHANGED_OUTSIDE_SCOPE:
DISCOVERY_DECISION:
UNVERIFIED_ITEMS:
PUSH_PERFORMED:
REMAINING_RISKS:
NEXT_RECOMMENDED_ACTION:
```

## 8. Examples

### Example 1: Resume llm-agents (active, dirty worktree)

**Context:** Project page บอกว่า active, Wave 1 pending, last verified 2026-07-28
**Staleness check:**
- HEAD: `099e516` เหมือนเดิม
- current_work_order เปลี่ยนจาก baseline
- worktree: 36 dirty files
- last_verified_date < 30 วัน
**Decision:** partial re-verification
- minimum checks: branch, HEAD, upstream, status, current task pointer, authority summary
- dirty state เป็น local artifacts และ reports → dirty-observation only
**Work Order:** bounded live run under WO-03, explicit staging, single commit

### Example 2: Resume STT Typing (superseded-pending-roadmap)

**Context:** Project page บอกว่า active/superseded-pending-roadmap, last verified 2026-07-28
**Staleness check:**
- HEAD: `af10254` เหมือนเดิม
- current task: SUPERSEDED-PENDING-ROADMAP
- no active executable task
- worktree: 1 modified + 4 untracked
**Decision:** no re-verification needed for resume unless roadmap changes
- minimum checks: branch, HEAD, status
**Work Order:** None until Owner approves new roadmap; Vault updated only

### Example 3: Resume Utility Disbursement App (paused)

**Context:** Project page บอกว่า paused/owner-confirmed, last verified 2026-07-29
**Staleness check:**
- HEAD: `429cb91` เหมือนเดิม
- current_work_order: NONE
- worktree: `dev.db` modified
- last_verified_date < 30 วัน
- Owner confirmed paused 2026-07-28
**Decision:** no re-verification needed unless resume
- minimum checks: branch, HEAD, status, dirty state
**Work Order:** ถ้า Owner resume → bounded onboarding/workflow WO; else maintain paused state

## 9. Controller / Worker Responsibilities

| Role | Responsibility |
|------|----------------|
| Controller | Approve resume, validate Work Order, review evidence, authorize commit/push |
| Worker | Execute bounded inspection/re-verification, write reports, run validation |
| Reviewer | Check scope compliance, evidence, commit readiness |
| Owner | Final approval, explicit push authorization |

## 10. Evidence Sources

- `04 Work Orders/WO-OBSIDIAN-010-STALENESS-AND-REVERIFICATION-POLICY.md`
- `03 Decisions/DEC-Vault-Staleness-and-Reverification-Policy.md`
- `AGENTS.md`
- `.agents/skills/project-read-first/SKILL.md`
- `.agents/skills/project-context-discovery/SKILL.md`

## 11. Verification Record

- Verified by: AI (WO-OBSIDIAN-011)
- Verification date: 2026-07-29
- Evidence classification: VERIFIED_REPOSITORY_FACT / OWNER_CONFIRMED_FACT / SUPPORTED_INFERENCE / NEEDS_VERIFICATION
