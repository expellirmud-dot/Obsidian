# WORK ORDER — ONBOARD UTILITY DISBURSEMENT APP

Work Order ID: WO-OBSIDIAN-008
Title: Onboard Utility Disbursement App into Project Knowledge Vault
Status: CLOSED
Task Classification: EXTERNAL_PROJECT_DISCOVERY_AND_VAULT_UPDATE
Risk Level: MEDIUM
Execution Mode: One Repository, One Bounded Seam

Owner: Toto
Vault Root: `D:\Obsidian\Project-Knowledge-Vault`
Source Repository: `D:\project_backups\utility-disbursement-app`

Depends On: WO-OBSIDIAN-007 CLOSED
Pull Authorization: YES — fast-forward only when remote exists
Commit Authorization: YES — one Vault commit after validation
Push Authorization: NO

---

## 1. Objective

ใช้ `project-read-first` และ `project-context-discovery` ตรวจ Repository truth ของ Utility Disbursement App แบบ read-only แล้วเปลี่ยนสถานะจาก partially verified เป็นบริบทที่แยกชัดระหว่าง `OWNER_CONFIRMED_FACT`, `VERIFIED_REPOSITORY_FACT`, `SUPPORTED_INFERENCE` และ `NEEDS_VERIFICATION`

สถานะ `paused` ต้องไม่ถูกตีความว่า abandoned, completed หรือ production-ready

## 2. Required Read Order

### Vault

1. `AGENTS.md`
2. `.agents/skills/project-read-first/SKILL.md`
3. `.agents/skills/project-context-discovery/SKILL.md`
4. `04 Work Orders/CURRENT_WORK_ORDER.md`
5. Work Order ฉบับนี้
6. `01 Projects/Utility Disbursement App.md`
7. `01 Projects/Project Index.md`
8. `00 Dashboard/Project Dashboard.md`

### Source Repository

1. Resolve exact Git root จาก source path
2. ตรวจ remote, branch, HEAD, upstream และ status
3. อ่าน authority/governance files ที่ค้นพบ
4. อ่าน Current Task/Work Order pointer หรือยืนยันว่าไม่มี
5. อ่าน README/documentation index และ architecture/status docs แบบ targeted
6. Inspect source symbols เฉพาะเมื่อเอกสารไม่เพียงพอ และต้องใช้ Serena/CodeGraph ตรง exact root

## 3. Source Repository Boundary

Source Repository เป็น read-only:

- ห้ามแก้ source, docs, task pointer, configuration หรือ Git state
- ห้าม stage/commit/push/checkout/reset/clean/stash
- ห้ามรัน application, database migration, browser automation หรือ external service
- ห้ามเปิด Secret/Credential
- ห้ามติดตั้ง dependency

## 4. Required Evidence

```text
REPOSITORY_ROOT
REMOTE
BRANCH
HEAD
UPSTREAM
GIT_STATUS
AUTHORITY_FILES
CURRENT_TASK_OR_WORK_ORDER
PROJECT_PURPOSE
RUNTIME_ENTRY_POINTS
MAJOR_COMPONENTS
DATA_AND_EXTERNAL_BOUNDARIES
CURRENT_STATE
OWNER_CONFIRMED_PAUSED_STATE
COMPLETED_WORK
OPEN_WORK
KNOWN_RISKS
DO_NOT_REPEAT
REQUIRED_READS
NEXT_RECOMMENDED_ACTION
```

## 5. Vault Updates

แก้หรือสร้างเฉพาะ:

```text
01 Projects/Utility Disbursement App.md
01 Projects/Project Index.md
00 Dashboard/Project Dashboard.md
02 Architecture/ARCH-Utility-Disbursement-App-Overview.md
02 Architecture/Architecture Index.md
04 Work Orders/CURRENT_WORK_ORDER.md
04 Work Orders/WO-OBSIDIAN-008-ONBOARD-UTILITY-DISBURSEMENT-APP.md
04 Work Orders/Work Order Index.md
```

## 6. Stop Conditions

หยุดเมื่อ path/Git root ไม่ตรง, authority ขัดแย้ง, dirty state ทำให้แยก current truth ไม่ได้, ต้องรันระบบจริง, ต้องแก้ Source Repository, ต้องใช้ Secret/Owner decision หรือ Serena/CodeGraph mismatch

## 7. Validation

```text
Source repository modified: 0
Runtime/database/external service invoked: 0
Vault files outside allowed scope: 0
Owner-confirmed paused state separated from repository facts: yes
Branch/HEAD/status recorded: yes
Current task recorded: yes or explicitly NONE
Internal links unresolved: 0 except marked placeholders
Duplicate frontmatter keys: 0
Secrets added: 0
Push performed: 0
```

รัน `git diff --check` และตรวจ staged paths ก่อน commit

## 8. Definition of Done

1. Source Repository ถูกตรวจแบบ read-only
2. Project page และ architecture overview grounded ตามหลักฐาน
3. สถานะ paused แยกจาก execution/completion state
4. Resume Context ใช้เริ่มงานใหม่ได้
5. Dashboard/Indexes สอดคล้องกัน
6. `CURRENT_WORK_ORDER.md` เปลี่ยนเป็น CLOSED
7. Validation ผ่านทั้งหมด
8. Commit หนึ่งครั้ง
9. ไม่มี Push

Commit message:

```text
docs: onboard Utility Disbursement App context
```

## 9. Final Report

```text
WORK_ORDER: WO-OBSIDIAN-008
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
