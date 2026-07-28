# WORK ORDER — CREATE PROJECT CONTEXT DISCOVERY SKILL

Work Order ID: WO-OBSIDIAN-003  
Title: Create Project Context Discovery Skill  
Status: ACTIVE  
Task Classification: VAULT_DOCUMENTATION_AND_SKILL_INSTALLATION  
Risk Level: LOW  
Execution Mode: One Bounded Seam

Owner: Toto  
Repository Root: `D:\Obsidian\Project-Knowledge-Vault`  
Branch: `main`

Pull Authorization: YES — `git pull --ff-only origin main`  
Commit Authorization: YES — one commit after validation  
Push Authorization: NO

Depends On: WO-OBSIDIAN-002 CLOSED

---

## 1. Objective

สร้างสกิล `project-context-discovery` เพื่อกำหนดวิธีที่ AI เข้าไปสำรวจโปรเจกต์อื่นอย่างเป็นระบบ โดยรู้ว่าต้องอ่านอะไรตามลำดับ ใช้หลักฐานใด หยุดอ่านเมื่อใด และสรุปข้อมูลกลับเข้า Vault ในรูปแบบมาตรฐาน

งานนี้สร้างสกิลและกฎเท่านั้น ยังไม่สำรวจหรือแก้หน้าโปรเจกต์จริง

---

## 2. Required Read Order

อ่านเต็มก่อนแก้ไฟล์:

1. `AGENTS.md`
2. `.agents/skills/project-read-first/SKILL.md`
3. `README.md`
4. `00 Dashboard/Project Dashboard.md`
5. `04 Work Orders/CURRENT_WORK_ORDER.md`
6. Work Order ฉบับนี้
7. `06 Prompts/Templates/Project Template.md`
8. `06 Prompts/Templates/Resume Context Template.md`

ผลิต `READ_FIRST_PREFLIGHT` และเริ่มแก้ไขได้เฉพาะเมื่อ `PREFLIGHT_DECISION: READY`

---

## 3. Target Structure

สร้าง:

```text
.agents/skills/project-context-discovery/
├── SKILL.md
├── scripts/
│   └── discover-project.ps1
└── references/
    ├── PROJECT_DISCOVERY_READ_ORDER.md
    └── PROJECT_CONTEXT_OUTPUT_CONTRACT.md
```

---

## 4. Skill Purpose

สกิลต้องรองรับการสำรวจแบบอ่านอย่างเดียวในสามระดับ:

### Level 1 — Project Identification

ตรวจ:

- ชื่อโปรเจกต์และ Vault Project Page
- Local path
- Canonical Git root
- Remote repository
- Branch, HEAD, upstream และ Git status
- การมีอยู่ของ Repository และสถานะ dirty/clean

### Level 2 — Authority and Current State

ค้นหาและอ่านตาม authority จริงของแต่ละ Repository:

- `AGENTS.md`, `PROJECT_RULES.md` หรือไฟล์ governance ที่เทียบเท่า
- Current Work Order / Current Task pointer
- README และ documentation index
- Project status, roadmap, architecture และ validation evidence ที่เกี่ยวข้อง
- Stop conditions, forbidden files และ commit/push authority

ห้ามสมมติว่าทุก Repository ใช้ชื่อไฟล์หรือโครงสร้างเหมือนกัน

### Level 3 — Task-Specific Inspection

ใช้เมื่อหลักฐานเอกสารไม่พอ:

- Serena exact-root symbol inspection
- CodeGraph exact-root dependency query
- Targeted source ranges
- อ่านเฉพาะส่วนที่จำเป็นต่อการยืนยัน architecture หรือ current state

ห้ามอ่าน source code ทั้งโปรเจกต์โดยไม่มีเหตุผล

---

## 5. Required Discovery Order

สกิลต้องบังคับลำดับนี้:

1. อ่าน Vault Project Page และ Resume Context
2. Resolve exact repository root
3. ตรวจ Git truth
4. ค้นหา authority files จาก root ก่อน
5. อ่าน Current Work Order / Current Task
6. อ่าน README หรือ documentation index
7. อ่าน status, architecture, roadmap และ validation แบบ targeted
8. ใช้ Serena/CodeGraph เฉพาะเมื่อจำเป็นและต้องตรง exact root
9. Cross-check ข้อสรุปกับไฟล์จริง
10. ผลิต `PROJECT_CONTEXT_DISCOVERY`
11. แยก verified facts, owner-confirmed facts, inference และ unknowns
12. เสนอการอัปเดต Vault โดยไม่แก้ Source Repository

---

## 6. Stop-Reading Rules

หยุดขยายการอ่านเมื่อข้อมูลเพียงพอที่จะตอบครบ:

- โปรเจกต์คืออะไร
- แก้ปัญหาอะไร
- ขอบเขตหลัก
- Repository truth
- Current Work Order และ current state
- Architecture ระดับภาพรวม
- ความเสี่ยงและสิ่งห้ามทำซ้ำ
- Required reads สำหรับรอบถัดไป
- Next recommended action หนึ่งข้อ

ต้องหยุดและรายงานเมื่อ:

- Repository path ไม่ถูกต้องหรือไม่มีอยู่
- Git root ไม่ตรงกับ path ที่บันทึกใน Vault
- Authority files ขัดแย้งกัน
- มี unexpected dirty files ที่ทำให้การสรุป current state ไม่น่าเชื่อถือ
- ต้องใช้ Secret, Credential หรือ external service
- ต้องแก้ Source Repository
- Serena/CodeGraph ไม่ตรง root ในกรณีที่จำเป็นต้อง inspect source code

---

## 7. Evidence Classification

ทุกข้อสรุปต้องระบุที่มาเป็นหนึ่งใน:

```text
VERIFIED_REPOSITORY_FACT
OWNER_CONFIRMED_FACT
SUPPORTED_INFERENCE
NEEDS_VERIFICATION
```

ห้ามเปลี่ยน `needs-verification` เป็น verified จากความจำ แชทเก่า ชื่อไฟล์ หรือ Worker Report เพียงอย่างเดียว

---

## 8. Output Contract

สร้าง contract ที่กำหนด output ขั้นต่ำ:

```text
PROJECT_CONTEXT_DISCOVERY

PROJECT_NAME:
VAULT_PAGE:
REPOSITORY_ROOT:
REMOTE:
BRANCH:
HEAD:
UPSTREAM:
GIT_STATUS:

AUTHORITY_FILES:
CURRENT_WORK_ORDER:
WORK_ORDER_STATUS:
DOCUMENTATION_INDEX:

PROJECT_PURPOSE:
PROBLEM_SOLVED:
IN_SCOPE:
OUT_OF_SCOPE:
ARCHITECTURE_SUMMARY:
CURRENT_STATE:
COMPLETED_WORK:
OPEN_WORK:
KNOWN_RISKS:
DO_NOT_REPEAT:
REQUIRED_READS:

SERENA_STATUS:
CODEGRAPH_STATUS:
SOURCE_SYMBOLS_INSPECTED:

VERIFIED_FACTS:
OWNER_CONFIRMED_FACTS:
SUPPORTED_INFERENCES:
UNVERIFIED_ITEMS:

RECOMMENDED_VAULT_UPDATES:
NEXT_RECOMMENDED_ACTION:
DISCOVERY_DECISION: COMPLETE | PARTIAL | BLOCKED
BLOCK_REASON:
```

---

## 9. discover-project.ps1

สคริปต์ทำหน้าที่ read-only เท่านั้น:

- รับ `-ProjectPath`
- Resolve Git root
- รายงาน current directory, branch, HEAD, upstream, origin และ status
- แสดง top-level files/directories
- ตรวจ candidate authority filenames แบบ case-insensitive
- ไม่อ่าน Secret
- ไม่แก้ไฟล์
- ไม่เปลี่ยน Git state
- ไม่ติดตั้ง dependency
- ไม่ commit/push
- ไม่อ้างว่า Serena/CodeGraph verified

สคริปต์ต้องคืน non-zero exit code เมื่อ path ไม่ใช่ Git repository

---

## 10. AGENTS and README Integration

เพิ่มใน `AGENTS.md` แบบ surgical edit:

- งานสำรวจ Repository ภายนอกต้องใช้ `project-context-discovery`
- Source Repository เป็น read-only เว้นแต่มี Work Order แยกอนุญาต
- Vault update ต้องแยก verified/inference/unknown

เพิ่มใน `README.md`:

- Skill path
- วิธีใช้ก่อน onboard โปรเจกต์ใหม่
- ลิงก์ไป output contract

รักษา Seven Execution Rules และ Four Common AI Failure Modes เดิมทุกข้อ

---

## 11. Allowed Files

```text
.agents/skills/project-context-discovery/SKILL.md
.agents/skills/project-context-discovery/scripts/discover-project.ps1
.agents/skills/project-context-discovery/references/PROJECT_DISCOVERY_READ_ORDER.md
.agents/skills/project-context-discovery/references/PROJECT_CONTEXT_OUTPUT_CONTRACT.md
04 Work Orders/CURRENT_WORK_ORDER.md
04 Work Orders/WO-OBSIDIAN-003-CREATE-PROJECT-CONTEXT-DISCOVERY.md
04 Work Orders/Work Order Index.md
AGENTS.md
README.md
```

---

## 12. Forbidden Actions

ห้าม:

- สำรวจเชิงลึกหรือแก้ Repository โปรเจกต์อื่น
- แก้หน้าใน `01 Projects`
- แก้ Dashboard
- แก้ `.obsidian/`, `IDEA.md` หรือ `.gitignore`
- สร้างข้อมูลสถานะโปรเจกต์จากความจำ
- ใช้ `git add .`
- Push

---

## 13. Validation

ตรวจอย่างน้อย:

```text
Target skill files: 4/4
PowerShell syntax: PASS
Read-only commands only: PASS
Output contract fields: complete
Three discovery levels: present
Stop-reading rules: present
Evidence classes: 4/4
Seven Execution Rules: 7/7 unchanged
Four AI Failure Modes: 4/4 unchanged
Files changed outside scope: 0
Source repositories modified: 0
Secrets added: 0
Push performed: 0
```

รัน:

```powershell
$script = ".agents\skills\project-context-discovery\scripts\discover-project.ps1"
[void][scriptblock]::Create((Get-Content -LiteralPath $script -Raw))
git diff --check
```

---

## 14. Definition of Done

งานสำเร็จเมื่อ:

1. Skill structure ครบ 4 ไฟล์
2. ลำดับการค้นหา authority ไม่ hard-code เฉพาะโปรเจกต์ใด
3. มี three-level discovery และ stop-reading rules
4. Output contract แยก fact/inference/unknown
5. Script เป็น read-only และผ่าน syntax
6. AGENTS/README เชื่อมสกิลแล้ว
7. `CURRENT_WORK_ORDER.md` ยังคงชี้ WO-003 และเปลี่ยนเป็น `CLOSED`
8. Validation ผ่านทั้งหมด
9. Commit หนึ่งครั้ง
10. ไม่มี Push

Commit message:

```text
docs: add project context discovery skill
```

---

## 15. Final Report

```text
WORK_ORDER: WO-OBSIDIAN-003
RESULT: COMPLETED | PARTIAL | BLOCKED

HEAD_BEFORE:
HEAD_AFTER:
COMMIT:

FILES_CREATED:
FILES_UPDATED:
FILES_CHANGED_OUTSIDE_SCOPE:

SKILL_PATH:
POWERSHELL_SYNTAX:
OUTPUT_CONTRACT:
READ_ORDER:
STOP_READING_RULES:
EVIDENCE_CLASSIFICATION:

SOURCE_REPOSITORIES_MODIFIED:
SECRETS_ADDED:
PUSH_PERFORMED:
CURRENT_WORK_ORDER_STATUS:

REMAINING_RISKS:
NEXT_RECOMMENDED_ACTION:
```
