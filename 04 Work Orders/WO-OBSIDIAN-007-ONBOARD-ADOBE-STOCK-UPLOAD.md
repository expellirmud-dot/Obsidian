# WORK ORDER — ONBOARD ADOBE STOCK UPLOAD ASSISTANT

Work Order ID: WO-OBSIDIAN-007
Title: Onboard Adobe Stock Upload Assistant into Project Knowledge Vault
Status: COMPLETED
Task Classification: EXTERNAL_PROJECT_DISCOVERY_AND_VAULT_UPDATE  
Risk Level: MEDIUM  
Execution Mode: One Repository, One Bounded Seam

Owner: Toto  
Vault Root: `D:\Obsidian\Project-Knowledge-Vault`  
Source Repository: `D:\adobe-stock-upload`

Depends On: WO-OBSIDIAN-006 CLOSED  
Pull Authorization: NO — no remote configured
Commit Authorization: YES — one Vault commit after validation  
Push Authorization: YES — combined with WO-OBSIDIAN-006

---

## 1. Objective

ใช้ `project-read-first` และ `project-context-discovery` ตรวจ Repository truth ของ Adobe Stock Upload Assistant แบบ read-only แล้วอัปเดต Vault ให้สะท้อนหน้าที่ปัจจุบันของ Assistant, safety/execution-level boundaries, task packet governance, risks และ resume context

---

## 2. Required Read Order

### Vault

1. `AGENTS.md`
2. `.agents/skills/project-read-first/SKILL.md`
3. `.agents/skills/project-context-discovery/SKILL.md`
4. `04 Work Orders/CURRENT_WORK_ORDER.md`
5. Work Order ฉบับนี้
6. `01 Projects/Adobe Stock Upload Assistant.md`
7. `01 Projects/Project Index.md`
8. `00 Dashboard/Project Dashboard.md`

### Source Repository

1. Resolve exact Git root จาก `D:\adobe-stock-upload`
2. อ่าน root authority/governance files ที่ค้นพบ
3. อ่าน Current Task pointer และ active authority
4. อ่าน README และ workflow standards
5. อ่าน execution levels, safety boundaries, task packet policy
6. Inspect source symbols เฉพาะเมื่อเอกสารไม่เพียงพอ

---

## 3. Source Repository Boundary

Source Repository เป็น read-only:

- ห้ามแก้ task packet, source, tests, configuration หรือ Git state
- ห้ามรัน browser automation
- ห้าม stage/commit/push ใน Source Repository
- ห้าม checkout/reset/clean/stash
- ห้ามติดตั้ง dependency
- ห้ามเปิด Adobe Stock API หรือ browser automation

หากต้อง inspect source code ให้ Serena และ CodeGraph ตรง exact Git root ก่อน

---

## 4. Required Evidence

รวบรวม:

```text
REPOSITORY_ROOT
REMOTE
BRANCH
HEAD
UPSTREAM
GIT_STATUS
AUTHORITY_FILES
CURRENT_TASK
CURRENT_STATUS
PROJECT_PURPOSE
EXECUTION_LEVEL_BOUNDARIES
WORKFLOW_SAFETY_RULES
TASK_PACKET_GOVERNANCE
COMPLETED_WORK
OPEN_WORK
KNOWN_RISKS
DO_NOT_REPEAT
REQUIRED_READS
NEXT_RECOMMENDED_ACTION
```

ทุกข้อสรุปต้องระบุ:

- `VERIFIED_REPOSITORY_FACT`
- `OWNER_CONFIRMED_FACT`
- `SUPPORTED_INFERENCE`
- `NEEDS_VERIFICATION`

---

## 5. Vault Updates

แก้หรือสร้างเฉพาะ:

```text
01 Projects/Adobe Stock Upload Assistant.md
01 Projects/Project Index.md
00 Dashboard/Project Dashboard.md
02 Architecture/ARCH-Adobe-Stock-Upload-Overview.md
02 Architecture/Architecture Index.md
04 Work Orders/CURRENT_WORK_ORDER.md
04 Work Orders/WO-OBSIDIAN-007-ONBOARD-ADOBE-STOCK-UPLOAD.md
04 Work Orders/Work Order Index.md
```

หน้า Project ต้องอัปเดต:

- verified frontmatter
- purpose/problem/scope/prerequisites
- repository truth
- current task
- execution level safety summary
- task packet governance summary
- completed/open work
- risks/do-not-repeat
- Resume Context
- Verification Record พร้อม branch/HEAD/date
- ลิงก์ `[[ARCH-Adobe-Stock-Upload-Overview]]`

---

## 6. Architecture Note

สร้าง `02 Architecture/ARCH-Adobe-Stock-Upload-Overview.md` โดยสรุป:

- Controller/Worker/Reviewer/Owner roles
- Execution model และ execution levels L0–L5
- Task packet structure
- Safety/No-Auto-Submit boundaries
- Known limitations
- Evidence sources
- Last verified HEAD/date
- ลิงก์กลับ `[[Adobe Stock Upload Assistant]]`

---

## 7. Stop Conditions

หยุดเมื่อ:

- Path ไม่มีหรือ Git root ไม่ตรง
- Authority files ขัดแย้ง
- Worktree state ทำให้แยก current/historical truth ไม่ได้
- ต้องรัน browser automation หรือ Adobe Stock API
- ต้องแก้ Source Repository
- ต้องใช้ Secret/Credential หรือ Owner decision
- Serena/CodeGraph mismatch เมื่อจำเป็นต้อง inspect source

---

## 8. Validation

ยืนยัน:

```text
Source repository modified: 0
Browser/API actions invoked: 0
Vault files outside allowed scope: 0
Project page required sections: complete
Branch/HEAD/status recorded: yes
Current task recorded: yes or explicitly NONE
Architecture claims grounded: yes
Internal links unresolved: 0 except marked placeholders
Duplicate frontmatter keys: 0
Secrets added: 0
Push performed: 0 (combined with WO-006 per Owner authorization)
```

รัน `git diff --check` ใน Vault และตรวจ staged diff ก่อน commit

---

## 9. Definition of Done

1. Source Repository ถูกตรวจแบบ read-only
2. Adobe Stock Project Page ตรงกับ current repository authority
3. Resume Context ใช้เริ่มงานใหม่ได้
4. Execution levels L0–L5 และ No-Auto-Submit boundary ชัดเจน
5. Dashboard/Project Index สอดคล้องกัน
6. Verification Record มี HEAD และวันที่
7. `CURRENT_WORK_ORDER.md` เปลี่ยนเป็น `CLOSED`
8. Validation ผ่านทั้งหมด
9. Commit หนึ่งครั้ง
10. Push ตาม Owner authorization

Commit message:

```text
docs: onboard Adobe Stock Upload Assistant context
```

---

## 10. Final Report

```text
WORK_ORDER: WO-OBSIDIAN-007
RESULT: COMPLETED

SOURCE_REPOSITORY_ROOT: D:\adobe-stock-upload
SOURCE_BRANCH: main
SOURCE_HEAD: 0e5f9fc53f58592ca9e5e3c37bb2b0ef1ced977a
SOURCE_GIT_STATUS: 1 modified (.tasks/TASK-ADOBE-STOCK-SAFETY-TERMS-CORE-001/status.md), 3 untracked (.continue/, .serena/, .tasks/_proposed_next/)
SOURCE_FILES_MODIFIED: 0
BROWSER_OR_API_ACTIONS_INVOKED: 0

VAULT_HEAD_BEFORE: 90b1fd3
VAULT_HEAD_AFTER: <commit-sha>
VAULT_COMMIT: <commit-sha>
VAULT_FILES_CREATED: 02 Architecture/ARCH-Adobe-Stock-Upload-Overview.md, 04 Work Orders/WO-OBSIDIAN-007-ONBOARD-ADOBE-STOCK-UPLOAD.md
VAULT_FILES_UPDATED: 01 Projects/Adobe Stock Upload Assistant.md, 01 Projects/Project Index.md, 00 Dashboard/Project Dashboard.md, 02 Architecture/Architecture Index.md, 04 Work Orders/CURRENT_WORK_ORDER.md, 04 Work Orders/Work Order Index.md
FILES_CHANGED_OUTSIDE_SCOPE: 0

AUTHORITY_FILES_READ: AGENTS.md, PROJECT_RULES.md, README.md, docs/workflow/ADOBE_STOCK_WORKFLOW_STANDARDS.md, .tasks/CURRENT_TASK.md
CURRENT_TASK: TASK-ADOBE-STOCK-SAFETY-TERMS-CORE-001 (completed)
DISCOVERY_DECISION: COMPLETE
VERIFICATION_STATUS: VERIFIED_REPOSITORY_FACT — branch/HEAD/status/authority ยืนยันจาก source truth
UNVERIFIED_ITEMS: Internal implementation details, Adobe Stock API interaction patterns (no source inspection needed)

SECRETS_ADDED: 0
PUSH_PERFORMED: Combined with WO-006 (Owner authorized)
REMAINING_RISKS: No remote configured (local-only Git); no active executable task; worktree dirty
NEXT_RECOMMENDED_ACTION: กำหนดงานถัดไปสำหรับ Adobe Stock Upload Assistant หรือตั้ง remote backup
```
