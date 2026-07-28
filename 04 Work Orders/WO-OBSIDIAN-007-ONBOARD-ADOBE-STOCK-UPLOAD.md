# WORK ORDER — ONBOARD ADOBE STOCK UPLOAD ASSISTANT

Work Order ID: WO-OBSIDIAN-007  
Title: Onboard Adobe Stock Upload Assistant into Project Knowledge Vault  
Status: PLANNED  
Task Classification: EXTERNAL_PROJECT_DISCOVERY_AND_VAULT_UPDATE  
Risk Level: MEDIUM  
Execution Mode: One Repository, One Bounded Seam

Owner: Toto  
Vault Root: `D:\Obsidian\Project-Knowledge-Vault`  
Source Repository: `D:\adobe-stock-upload`

Depends On: WO-OBSIDIAN-006 CLOSED  
Pull Authorization: YES — fast-forward only  
Commit Authorization: YES — one Vault commit after validation  
Push Authorization: NO

---

## 1. Objective

ใช้ `project-read-first` และ `project-context-discovery` ตรวจ Repository truth ของ Adobe Stock Upload Assistant แบบ read-only แล้วอัปเดต Vault ให้บอกได้ชัดว่าโปรเจกต์ทำอะไร มีขั้นตอนเตรียมภาพ/metadata/upload อย่างไร ขอบเขต automation และ human review อยู่ตรงไหน สถานะปัจจุบันคืออะไร และกลับมาทำงานต่อจากจุดใด

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
2. อ่าน root governance/authority files ที่ค้นพบ
3. อ่าน Current Work Order/Task pointer และ active authority
4. อ่าน README หรือ documentation index
5. อ่าน project status, workflow, metadata/category/safety contracts และ validation evidence แบบ targeted
6. Inspect source symbols เฉพาะเมื่อเอกสารไม่เพียงพอ

ห้ามประมวลผลหรืออัปโหลดภาพจริงในงานนี้

---

## 3. Source Repository Boundary

Source Repository และข้อมูลภาพเป็น read-only:

- ห้ามแก้ source/docs/config/Git state
- ห้ามเปิดหรือส่งภาพจริงไป external service
- ห้ามอัปโหลด Adobe Stock
- ห้ามสร้าง/แก้ metadata ของ asset จริง
- ห้าม stage/commit/push
- ห้าม checkout/reset/clean/stash
- ห้ามติดตั้ง dependency
- ห้ามเปิด Secret/Credential/API key/session

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
CURRENT_TASK_OR_WORK_ORDER
PROJECT_PURPOSE
TARGET_USER_AND_WORKFLOW
INPUT_ASSET_BOUNDARY
IMAGE_PREPARATION_FLOW
METADATA_AND_CATEGORY_FLOW
SAFETY_AND_REVIEW_BOUNDARY
UPLOAD_BOUNDARY
CURRENT_STATE
COMPLETED_WORK
OPEN_WORK
KNOWN_RISKS
DO_NOT_REPEAT
REQUIRED_READS
NEXT_RECOMMENDED_ACTION
```

ข้อมูลเรื่องจำนวนภาพ ขนาดขั้นต่ำ provider/model หรือขั้นตอน upload ต้องบันทึกเฉพาะเมื่อมี authority ปัจจุบันรองรับ

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
- purpose/problem/scope
- repository truth
- current task/work order
- workflow and architecture summary
- automation vs human-review boundary
- completed/open work
- risks/do-not-repeat
- Resume Context
- Verification Record พร้อม branch/HEAD/date
- ลิงก์ `[[ARCH-Adobe-Stock-Upload-Overview]]`

---

## 6. Architecture Note

สร้าง `02 Architecture/ARCH-Adobe-Stock-Upload-Overview.md` โดยสรุป:

- Input asset boundary
- Image preparation/quality flow
- Metadata, keyword และ category flow
- Safety/review gates
- Upload boundary และ external-service boundary
- Persistence/configuration boundaries
- Validation strategy
- Known limitations
- Evidence sources
- Last verified HEAD/date
- ลิงก์กลับ `[[Adobe Stock Upload Assistant]]`

ห้ามใส่ Secret, Credential, private asset path ที่ไม่จำเป็น หรือสำเนาภาพ

---

## 7. Stop Conditions

หยุดเมื่อ:

- Path ไม่มีหรือ Git root ไม่ตรง
- Authority/Current Task ขัดแย้ง
- ต้องเปิด/ประมวลผล/อัปโหลด asset จริง
- ต้องเรียก external AI หรือ Adobe service
- ต้องแก้ Source Repository
- ต้องใช้ Secret/Credential หรือ Owner decision
- Serena/CodeGraph mismatch เมื่อจำเป็นต้อง inspect source

---

## 8. Validation

ยืนยัน:

```text
Source repository modified: 0
Images/assets opened or copied: 0
External services called: 0
Uploads performed: 0
Vault files outside allowed scope: 0
Project page required sections: complete
Branch/HEAD/status recorded: yes
Current task/work order recorded: yes or explicitly NONE
Automation/review/upload boundaries grounded: yes
Internal links unresolved: 0 except marked placeholders
Duplicate frontmatter keys: 0
Secrets or private asset data added: 0
Push performed: 0
```

รัน `git diff --check` ใน Vault และตรวจ staged diff ก่อน commit

---

## 9. Definition of Done

1. Source Repository ถูกตรวจแบบ read-only
2. ไม่มีภาพหรือ asset จริงถูกเปิด คัดลอก หรือส่งออก
3. Project Page ตรงกับ Repository truth
4. Resume Context ใช้เริ่มงานใหม่ได้
5. Architecture overview แสดง automation/review/upload boundaries ชัดเจน
6. Dashboard/Project Index สอดคล้องกัน
7. Verification Record มี HEAD และวันที่
8. `CURRENT_WORK_ORDER.md` เปลี่ยนเป็น `CLOSED`
9. Validation ผ่านทั้งหมด
10. Commit หนึ่งครั้ง
11. ไม่มี Push

Commit message:

```text
docs: onboard Adobe Stock Upload context
```

---

## 10. Final Report

```text
WORK_ORDER: WO-OBSIDIAN-007
RESULT: COMPLETED | PARTIAL | BLOCKED

SOURCE_REPOSITORY_ROOT:
SOURCE_BRANCH:
SOURCE_HEAD:
SOURCE_GIT_STATUS:
SOURCE_FILES_MODIFIED:
ASSETS_OPENED_OR_COPIED:
EXTERNAL_SERVICES_CALLED:
UPLOADS_PERFORMED:

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
