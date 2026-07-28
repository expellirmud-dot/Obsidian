# WORK ORDER — ONBOARD STT TYPING

Work Order ID: WO-OBSIDIAN-005
Title: Onboard STT Typing into Project Knowledge Vault
Status: COMPLETED
Task Classification: EXTERNAL_PROJECT_DISCOVERY_AND_VAULT_UPDATE
Risk Level: MEDIUM
Execution Mode: One Repository, One Bounded Seam

Owner: Toto
Vault Root: `D:\Obsidian\Project-Knowledge-Vault`
Source Repository: `D:\stt_typing`

Depends On: WO-OBSIDIAN-004 CLOSED
Pull Authorization: YES — fast-forward only
Commit Authorization: YES — one Vault commit after validation
Push Authorization: NO

---

## 1. Objective

ใช้ `project-read-first` และ `project-context-discovery` ตรวจ Repository truth ของ STT Typing แบบ read-only แล้วสร้างบริบทระยะยาวที่ยืนยันได้สำหรับการกลับมาพัฒนาต่อ

ต้องครอบคลุม project purpose, runtime boundary, authority, branch/HEAD/status, Current Work Order, architecture ระดับภาพรวม, feature flags/safety guards ที่ยังเป็น authority, current state, risks, required reads และ next action

---

## 2. Required Read Order

### Vault

1. `AGENTS.md`
2. `.agents/skills/project-read-first/SKILL.md`
3. `.agents/skills/project-context-discovery/SKILL.md`
4. `04 Work Orders/CURRENT_WORK_ORDER.md`
5. Work Order ฉบับนี้
6. `01 Projects/STT Typing.md`
7. `01 Projects/Project Index.md`
8. `00 Dashboard/Project Dashboard.md`

### Source Repository

1. Resolve exact Git root จาก `D:\stt_typing`
2. อ่าน root authority/governance files ที่ค้นพบ
3. อ่าน Current Task/Work Order pointer และ active authority
4. อ่าน README หรือ documentation index
5. อ่าน project status, architecture, runtime/safety contracts และ validation evidence แบบ targeted
6. Inspect source symbols เฉพาะเมื่อเอกสารไม่เพียงพอ

ห้ามถือข้อมูลจากแชทหรือ Vault เดิมว่าเป็น current truth โดยไม่ตรวจ Repository

---

## 3. Source Repository Boundary

Source Repository เป็น read-only:

- ห้ามแก้ source, docs, task pointer หรือ Git state
- ห้าม stage/commit/push
- ห้าม checkout/reset/clean/stash
- ห้ามเปิด microphone, real typing, clipboard automation หรือ external ASR service
- ห้ามเปิด Secret/Credential
- ห้ามติดตั้ง dependency

หากต้อง inspect source code ให้ Serena และ CodeGraph ตรง exact Git root ก่อน

---

## 4. Required Evidence

รวบรวมและบันทึก:

```text
REPOSITORY_ROOT
REMOTE
BRANCH
HEAD
UPSTREAM
GIT_STATUS
AUTHORITY_FILES
CURRENT_TASK_OR_WORK_ORDER
WORK_ORDER_STATUS
DOCUMENTATION_INDEX
PROJECT_PURPOSE
RUNTIME_ENTRY_POINTS
MAJOR_COMPONENTS
FEATURE_FLAGS
SAFETY_GUARDS
CURRENT_STATE
COMPLETED_WORK
OPEN_WORK
KNOWN_RISKS
DO_NOT_REPEAT
REQUIRED_READS
NEXT_RECOMMENDED_ACTION
```

ข้อมูล VAD, ASR route, feature flag, focus guard, test counts หรือ runtime state ต้องบันทึกเฉพาะเมื่อยังได้รับการยืนยันจาก authority ปัจจุบัน

ทุกข้อสรุปต้องแยกเป็น:

- `VERIFIED_REPOSITORY_FACT`
- `OWNER_CONFIRMED_FACT`
- `SUPPORTED_INFERENCE`
- `NEEDS_VERIFICATION`

---

## 5. Vault Updates

แก้หรือสร้างเฉพาะ:

```text
01 Projects/STT Typing.md
01 Projects/Project Index.md
00 Dashboard/Project Dashboard.md
02 Architecture/ARCH-STT-Typing-Overview.md
02 Architecture/Architecture Index.md
04 Work Orders/CURRENT_WORK_ORDER.md
04 Work Orders/WO-OBSIDIAN-005-ONBOARD-STT-TYPING.md
04 Work Orders/Work Order Index.md
```

หน้า Project ต้องมี:

- verified frontmatter
- purpose/problem/scope
- repository truth
- current task/work order
- runtime architecture summary
- safety and capability boundaries
- completed/open work
- risks/do-not-repeat
- Resume Context
- Verification Record พร้อม branch/HEAD/date
- ลิงก์ `[[ARCH-STT-Typing-Overview]]`

---

## 6. Architecture Note

สร้าง `02 Architecture/ARCH-STT-Typing-Overview.md` โดยสรุป:

- Composition/runtime entry points
- Audio → recognition → command/typing → output flow
- Major modules/orchestrators ตาม repo truth
- Feature flags และ safety boundaries
- External/local service boundaries
- Validation strategy
- Known limitations/risks
- Evidence sources
- Last verified HEAD/date
- ลิงก์กลับ `[[STT Typing]]`

ห้ามคัดลอก source code จำนวนมาก

---

## 7. Stop Conditions

หยุดเมื่อ:

- Path ไม่มีหรือ Git root ไม่ตรง
- Authority หรือ Current Task ขัดแย้ง
- Unexpected dirty state ทำให้ current state สรุปไม่ได้
- ต้องรัน real typing/audio/external service
- ต้องแก้ Source Repository
- ต้องใช้ Secret/Credential หรือ Owner decision
- Serena/CodeGraph mismatch เมื่อจำเป็นต้อง inspect source

---

## 8. Validation

ยืนยัน:

```text
Source repository modified: 0
Runtime/audio/external service invoked: 0
Vault files outside allowed scope: 0
Project page required sections: complete
Branch/HEAD/status recorded: yes
Current task/work order recorded: yes or explicitly NONE
Safety claims grounded in authority: yes
Architecture evidence paths: present
Verified/inference/unknown separation: present
Internal links unresolved: 0 except marked placeholders
Duplicate frontmatter keys: 0
Secrets added: 0
Push performed: 0
```

รัน `git diff --check` ใน Vault และตรวจ staged diff ก่อน commit

---

## 9. Definition of Done

1. Source Repository ถูกตรวจแบบ read-only
2. STT Project Page สอดคล้องกับ Repository truth
3. Resume Context ใช้เริ่มงานใหม่ได้
4. Architecture overview แสดง runtime/safety boundaries โดยไม่เดา
5. Dashboard/Project Index สอดคล้องกัน
6. Verification Record มี HEAD และวันที่
7. `CURRENT_WORK_ORDER.md` เปลี่ยนเป็น `CLOSED`
8. Validation ผ่านทั้งหมด
9. Commit หนึ่งครั้ง
10. ไม่มี Push

Commit message:

```text
docs: onboard STT Typing project context
```

---

## 10. Final Report

```text
WORK_ORDER: WO-OBSIDIAN-005
RESULT: COMPLETED | PARTIAL | BLOCKED

SOURCE_REPOSITORY_ROOT:
SOURCE_BRANCH:
SOURCE_HEAD:
SOURCE_GIT_STATUS:
SOURCE_FILES_MODIFIED:
RUNTIME_ACTIONS_PERFORMED:

VAULT_HEAD_BEFORE:
VAULT_HEAD_AFTER:
VAULT_COMMIT:
VAULT_FILES_CREATED:
VAULT_FILES_UPDATED:
FILES_CHANGED_OUTSIDE_SCOPE:

AUTHORITY_FILES_READ:
CURRENT_TASK_OR_WORK_ORDER:
DISCOVERY_DECISION:
VERIFICATION_STATUS:
UNVERIFIED_ITEMS:

SECRETS_ADDED:
PUSH_PERFORMED:
REMAINING_RISKS:
NEXT_RECOMMENDED_ACTION:
```
