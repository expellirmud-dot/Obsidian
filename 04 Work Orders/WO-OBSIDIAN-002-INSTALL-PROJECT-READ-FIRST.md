# WORK ORDER — INSTALL PROJECT READ-FIRST SKILL

Work Order ID: WO-OBSIDIAN-002  
Title: Pull Latest, Reconcile Work Order Authority, and Install Project Read-First  
Status: CLOSED
Task Classification: VAULT_DOCUMENTATION_AND_SKILL_INSTALLATION  
Risk Level: LOW  
Execution Mode: One Bounded Seam  

Owner: Toto  
Repository Root: `D:\Obsidian\Project-Knowledge-Vault`  
Remote: `https://github.com/expellirmud-dot/Project-Knowledge-Vault.git`  
Branch: `main`

Pull Authorization: YES — fast-forward only  
Commit Authorization: YES — one commit after all validation passes  
Push Authorization: NO

Expected remote HEAD when this Work Order was issued:

`baa1ae55986d94ce8cefd49510fdf47d147a5ba6`

The fetched `origin/main` at execution time remains the source of truth.

---

## 1. Objective

ดำเนินงานหนึ่ง bounded seam ประกอบด้วย:

1. ตรวจ Local repository และ Pull `origin/main` แบบ fast-forward เท่านั้น
2. ทำให้ Work Order authority ของ Vault มีเส้นทางที่ชัดเจน
3. สร้าง `CURRENT_WORK_ORDER.md`
4. ติดตั้งและปรับสกิล `project-read-first` สำหรับ Obsidian Vault
5. เชื่อมกฎเรียกใช้สกิลเข้ากับ `AGENTS.md`
6. แก้ชื่อหัวข้อ Dashboard ที่ทำให้สถานะ Active/Paused สับสน
7. ตรวจโครงสร้าง เนื้อหา สัญญา output และขอบเขตงาน
8. Commit หนึ่งครั้งเมื่อ Validation ผ่าน
9. ห้าม Push

---

## 2. Source and Target

Source skill — read only:

`D:\ai-tools\lightroom-ai-exposure\.agents\skills\project-read-first`

Target skill:

`D:\Obsidian\Project-Knowledge-Vault\.agents\skills\project-read-first`

Expected source files:

- `SKILL.md`
- `scripts/preflight.ps1`
- `references/DOCUMENT_READ_POLICY.md`
- `references/PREFLIGHT_OUTPUT_CONTRACT.md`
- `references/SERENA_CODEGRAPH_PROTOCOL.md`

ห้ามแก้ไฟล์ใดใน Source repository

---

## 3. Pull and Baseline Reconciliation

ทำส่วนนี้ก่อนอ่านหรือแก้ไฟล์งาน

```powershell
Set-Location "D:\Obsidian\Project-Knowledge-Vault"

$root = git rev-parse --show-toplevel
$branch = git branch --show-current
$headBefore = git rev-parse HEAD
$origin = git remote get-url origin
$statusBefore = git status --short

$root
$branch
$headBefore
$origin
$statusBefore
```

ต้องยืนยัน:

```text
REPOSITORY_ROOT: D:\Obsidian\Project-Knowledge-Vault
BRANCH: main
ORIGIN: https://github.com/expellirmud-dot/Project-Knowledge-Vault.git
```

ไฟล์ untracked เดิมที่ Owner อนุญาตให้คงอยู่ได้:

```text
.obsidian/
IDEA.md
```

ไฟล์ทั้งสองเป็น Owner artifacts:

- ห้ามแก้
- ห้ามลบ
- ห้าม Stage
- ห้ามเพิ่มเข้า `.gitignore` ใน Work Order นี้

หากพบ tracked modification หรือ untracked file อื่นนอกเหนือจากสองรายการนี้:

```text
PREFLIGHT_DECISION: BLOCKED_DIRTY_WORKTREE
```

ห้าม Reset, Clean, Stash หรือ Checkout ทับข้อมูล

### Fetch and Pull

```powershell
git fetch origin

git rev-list --left-right --count HEAD...origin/main
git log -1 --format="%H %s" HEAD
git log -1 --format="%H %s" origin/main
```

อนุญาตให้ Pull เฉพาะเมื่อ Local branch ไม่ได้ ahead และไม่ diverged:

```powershell
git pull --ff-only origin main
```

หลัง Pull:

```powershell
git rev-parse HEAD
git rev-parse origin/main
git status --short
```

เงื่อนไขผ่าน:

```text
HEAD == origin/main
Pull method == fast-forward or already up to date
Owner artifacts preserved
Unexpected dirty files == 0
```

หาก branch diverged, local ahead หรือ Pull ต้อง merge:

```text
PREFLIGHT_DECISION: BLOCKED_OWNER_DECISION
```

ห้ามใช้ `git pull` แบบ merge และห้าม force

---

## 4. Mandatory Read Order

อ่านเต็มก่อนแก้ไฟล์:

1. `AGENTS.md`
2. `README.md`
3. `00 Dashboard/Project Dashboard.md`
4. `04 Work Orders/Work Order Index.md`
5. `work-order/WO-OBSIDIAN-001.md`
6. Source `.agents/skills/project-read-first/SKILL.md`
7. Source `references/DOCUMENT_READ_POLICY.md`
8. Source `references/PREFLIGHT_OUTPUT_CONTRACT.md`
9. Source `references/SERENA_CODEGRAPH_PROTOCOL.md`
10. Source `scripts/preflight.ps1`

ตรวจสอบว่าไฟล์ไม่ว่างและไม่มีความขัดแย้งที่แก้ไม่ได้อย่างปลอดภัย

---

## 5. Work Order Authority Reconciliation

เส้นทางมาตรฐานใหม่ของ Vault:

```text
04 Work Orders/CURRENT_WORK_ORDER.md
04 Work Orders/WO-OBSIDIAN-002-INSTALL-PROJECT-READ-FIRST.md
```

ไฟล์เดิม:

```text
work-order/WO-OBSIDIAN-001.md
```

ให้ถือเป็น Legacy Closed Work Order และรักษาไว้ ห้ามย้าย ห้ามลบ และห้ามแก้ในงานนี้

อัปเดต `04 Work Orders/Work Order Index.md` ให้ระบุชัดเจน:

```markdown
## Current Work Order

- [[CURRENT_WORK_ORDER]]
- [[WO-OBSIDIAN-002-INSTALL-PROJECT-READ-FIRST]]

## Closed Legacy Work Orders

- `work-order/WO-OBSIDIAN-001.md` — COMPLETED
  - เก็บไว้ที่เส้นทางเดิมเพื่อรักษาประวัติ Git
  - Work Order ใหม่ทั้งหมดใช้ `04 Work Orders`
```

---

## 6. CURRENT_WORK_ORDER.md

สร้าง:

`04 Work Orders/CURRENT_WORK_ORDER.md`

เนื้อหาเริ่มงาน:

```markdown
# Current Work Order

WORK_ORDER: `04 Work Orders/WO-OBSIDIAN-002-INSTALL-PROJECT-READ-FIRST.md`
STATUS: ACTIVE
TASK_CLASSIFICATION: VAULT_DOCUMENTATION_AND_SKILL_INSTALLATION
OWNER: Toto

## Authority

ไฟล์นี้เป็น pointer ของงานปัจจุบันสำหรับ Project Knowledge Vault

## Allowed Scope

ดู Allowed Files และ Forbidden Actions ใน Active Work Order
```

เมื่อดำเนินงานและ Validation ผ่านครบแล้ว เปลี่ยนเฉพาะ:

```text
STATUS: CLOSED
```

ต้องรักษา pointer ไปยัง WO-002 ไว้ ห้ามเปลี่ยนเป็น NONE และห้ามลบไฟล์

---

## 7. Install Target Structure

สร้าง:

```text
.agents/
└── skills/
    └── project-read-first/
        ├── SKILL.md
        ├── scripts/
        │   └── preflight.ps1
        └── references/
            ├── DOCUMENT_READ_POLICY.md
            ├── PREFLIGHT_OUTPUT_CONTRACT.md
            └── SERENA_CODEGRAPH_PROTOCOL.md
```

สกิลเป้าหมายต้องเป็น Vault Edition ไม่ใช่การคัดลอกต้นฉบับแบบไม่แก้ไข

---

## 8. Vault Authority Mapping

Mandatory full reads สำหรับงานใน Vault:

1. `AGENTS.md`
2. `README.md`
3. `00 Dashboard/Project Dashboard.md`
4. `04 Work Orders/CURRENT_WORK_ORDER.md`
5. Active Work Order ที่ pointer อ้างถึง

ห้ามบังคับเส้นทางเฉพาะ Lightroom ต่อไปนี้:

```text
docs/INDEX.md
Work-Order/CURRENT_WORK_ORDER.md
docs/PROJECT_STATUS.md
docs/CAPABILITY_MATRIX.md
docs/VALIDATION_REGISTER.md
```

---

## 9. Task Classification Behavior

### VAULT_DOCUMENTATION

งาน Markdown, Dashboard, Index, Template, Project Overview หรือ Resume Context ภายใน Vault:

```text
SERENA_PROJECT: not_required
SERENA_STATUS: not_required
CODEGRAPH_PROJECT: not_required
CODEGRAPH_STATUS: not_required
CODEGRAPH_SYNC: not_required
```

Serena และ CodeGraph ต้องไม่บล็อกงานประเภทนี้

### SOURCE_REPOSITORY

งานที่อ่าน วิเคราะห์ หรือแก้ Source Code:

- Resolve exact Git root ของ Source repository จริง
- Serena ต้องตรงกับ exact Git root
- CodeGraph ต้องตรงกับ exact Git root
- Vault root ห้ามใช้แทน Source repository root
- หากตรวจเครื่องมือไม่ได้ต้อง Block
- Serena memory และ CodeGraph เป็นข้อมูลประกอบ ไม่ใช่ Authority เหนือไฟล์จริง

---

## 10. Required SKILL.md Changes

ปรับตัวอย่าง Serena จาก hard-coded path:

```python
mcp__serena__activate_project(
    project="D:\\ai-tools\\lightroom-ai-exposure"
)
```

เป็น:

```python
mcp__serena__activate_project(
    project="<canonical-git-root>"
)
```

ลบกฎเฉพาะ Lightroom:

- Lightroom catalogs
- Preview caches
- Photographs
- RAW files
- XMP sidecars

แทนด้วยกฎทั่วไป:

- ห้ามอ่าน Secret หรือ Credential
- ห้ามแก้ Repository ภายนอก Active Work Order
- ห้ามอ่าน Binary หรือข้อมูลส่วนบุคคลที่ไม่จำเป็น
- ห้ามเรียก External AI Service ระหว่าง preflight
- ห้ามติดตั้ง Dependency ระหว่าง preflight
- ห้ามแก้ Git state ระหว่าง preflight
- ห้าม Commit หรือ Push ระหว่าง preflight

เพิ่มกฎ:

```text
AGENTS.md must be read before loading any repository skill.

For documentation-only Vault tasks, Serena and CodeGraph are
not required. They become mandatory only when the task reads,
analyzes, or modifies source code.

Conversation, AI memory, Worker reports, Serena memory, and
CodeGraph results are supplementary context and never override
repository files.
```

---

## 11. Fix preflight.ps1

สคริปต์ต้อง:

1. แสดง `READ_FIRST_PREFLIGHT` หนึ่งครั้ง
2. ใช้รูปแบบ `FIELD: value`
3. แสดง `PREFLIGHT_DECISION` หนึ่งครั้ง
4. แสดง `BLOCK_REASON:` หนึ่งครั้ง
5. ไม่รายงาน Serena verified จากการพบ executable
6. ไม่รายงาน CodeGraph verified จากการพบ directory
7. แยก expected dirty files กับ unexpected dirty files
8. ไม่แก้ไฟล์หรือ Git state
9. ไม่ Pull, Commit หรือ Push ภายใน preflight script
10. รองรับ `VAULT_DOCUMENTATION` เป็น `not_required`

Terminal decision อนุญาตเฉพาะ:

```text
READY
BLOCKED_DIRTY_WORKTREE
BLOCKED_PROJECT_MISMATCH
BLOCKED_SERENA
BLOCKED_CODEGRAPH
BLOCKED_MISSING_AUTHORITY
BLOCKED_SCOPE_CONFLICT
BLOCKED_OWNER_DECISION
```

ห้ามใช้:

```text
GIT_READY
PASS
SUCCESS
AVAILABLE
```

เป็น terminal decision

---

## 12. AGENTS.md Integration

เพิ่มส่วนนี้แบบ surgical edit โดยรักษากฎ 7 ข้อและ 4 Failure Modes เดิมทุกข้อ:

```markdown
## Mandatory Project Read-First

ก่อนแก้ไขไฟล์ทุกงาน AI ต้องอ่านและปฏิบัติตาม:

`.agents/skills/project-read-first/SKILL.md`

ลำดับเริ่มงาน:

1. อ่าน `AGENTS.md`
2. โหลด `project-read-first`
3. Resolve exact Git root
4. อ่าน `04 Work Orders/CURRENT_WORK_ORDER.md`
5. อ่าน Active Work Order
6. ตรวจ Allowed Files และ Forbidden Actions
7. ผลิต `READ_FIRST_PREFLIGHT`
8. เริ่มแก้ไขได้เฉพาะเมื่อ `PREFLIGHT_DECISION: READY`

สำหรับงาน Markdown-only ภายใน Vault:
Serena และ CodeGraph เป็น `not_required`

สำหรับงาน Source Code:
Serena และ CodeGraph ต้องตรงกับ exact Git root ของ Source Repository
```

ห้ามแก้ถ้อยคำหรือจำนวนของ Seven Execution Rules และ Four Common AI Failure Modes เดิม

---

## 13. Dashboard Correction

ใน:

`00 Dashboard/Project Dashboard.md`

เปลี่ยนหัวข้อ:

```markdown
## Active Projects
```

เป็น:

```markdown
## Projects in Vault
```

รักษารายชื่อทั้งห้าไว้ เพราะส่วนนี้หมายถึงสารบัญโปรเจกต์ ไม่ใช่สถานะ

รักษา `Utility Disbursement App` ไว้เฉพาะใน `Paused Projects` สำหรับการแสดงสถานะจริง

---

## 14. README Integration

อัปเดต README แบบ surgical edit:

- ระบุ Current Work Order path:
  `04 Work Orders/CURRENT_WORK_ORDER.md`
- ระบุ Skill path:
  `.agents/skills/project-read-first/SKILL.md`
- ระบุว่า `work-order/WO-OBSIDIAN-001.md` เป็น legacy historical location
- Work Order ใหม่ทั้งหมดต้องอยู่ใน `04 Work Orders`

ห้ามเปลี่ยนหลัก Authority Order เดิม

---

## 15. Allowed Files

อนุญาตให้สร้างหรือแก้เฉพาะ:

```text
.agents/skills/project-read-first/SKILL.md
.agents/skills/project-read-first/scripts/preflight.ps1
.agents/skills/project-read-first/references/DOCUMENT_READ_POLICY.md
.agents/skills/project-read-first/references/PREFLIGHT_OUTPUT_CONTRACT.md
.agents/skills/project-read-first/references/SERENA_CODEGRAPH_PROTOCOL.md
04 Work Orders/CURRENT_WORK_ORDER.md
04 Work Orders/WO-OBSIDIAN-002-INSTALL-PROJECT-READ-FIRST.md
04 Work Orders/Work Order Index.md
00 Dashboard/Project Dashboard.md
AGENTS.md
README.md
```

---

## 16. Forbidden Actions

ห้าม:

- แก้ Source skill repository
- แก้ `work-order/WO-OBSIDIAN-001.md`
- แก้หน้า Project Overview ทั้งห้า
- แก้ `01 Projects/Project Index.md`
- แก้ `.gitignore`
- แก้ `.obsidian/`
- แก้ `IDEA.md`
- ติดตั้ง Plugin
- สร้าง Serena หรือ CodeGraph evidence ปลอม
- ใช้ `git add .`
- ใช้ `git reset --hard`
- ใช้ `git clean`
- ใช้ Force Push
- Merge branch
- Commit ก่อน Validation
- Push

---

## 17. Validation

### Repository

```powershell
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git rev-parse origin/main
git status --short
git diff --check
```

### Structure

```powershell
Get-ChildItem `
  ".agents\skills\project-read-first" `
  -Recurse |
  Select-Object FullName
```

### PowerShell Syntax

```powershell
$script = ".agents\skills\project-read-first\scripts\preflight.ps1"
$content = Get-Content -LiteralPath $script -Raw
[void][scriptblock]::Create($content)
"POWERSHELL_SYNTAX_OK"
```

### Source-Specific Leakage

ค้นหาภายใน Target skill:

```text
D:\ai-tools\lightroom-ai-exposure
Lightroom catalog
Preview cache
RAW file
XMP sidecar
GIT_READY
```

Expected occurrences:

```text
Hard-coded Lightroom root: 0
Lightroom-specific rules: 0
GIT_READY terminal decision: 0
```

### Output Contract

ยืนยันจากการรันสคริปต์:

```text
READ_FIRST_PREFLIGHT occurrences: 1
PREFLIGHT_DECISION occurrences: 1
BLOCK_REASON occurrences: 1
Unknown terminal decisions: 0
FIELD=value format occurrences: 0
```

### Governance

ยืนยัน:

```text
Seven Execution Rules: 7/7 unchanged
Four AI Failure Modes: 4/4 unchanged
CURRENT_WORK_ORDER exists: YES
CURRENT_WORK_ORDER target exists: YES
Work Order Index links current authority: YES
Dashboard misleading Active heading: 0
```

### Scope and Safety

```text
Files changed outside Allowed Files: 0
Files deleted: 0
External repositories modified: 0
Plugins installed: 0
Secrets added: 0
Owner artifacts modified: 0
Push performed: 0
```

---

## 18. Definition of Done

งานสำเร็จเมื่อ:

1. Pull แบบ fast-forward หรือ Already up to date
2. Local HEAD ตรงกับ `origin/main` ก่อนเริ่มแก้
3. สกิลติดตั้งครบห้าไฟล์
4. ไม่มี Lightroom-specific path หรือ policy เหลือ
5. Markdown-only ไม่ถูกบล็อกด้วย Serena/CodeGraph
6. Source-code task ยังบังคับ exact-root verification
7. `preflight.ps1` ผ่าน syntax และ output contract
8. `CURRENT_WORK_ORDER.md` ถูกสร้าง
9. Work Order authority ใช้ `04 Work Orders`
10. Legacy WO-001 ถูกเก็บไว้โดยไม่แก้
11. Dashboard ไม่เรียกสารบัญรวมว่า Active Projects
12. Seven Rules และ Four Failure Modes ไม่เปลี่ยน
13. ไม่มีไฟล์นอก scope ถูกแก้
14. Validation ผ่านครบ
15. `CURRENT_WORK_ORDER` เปลี่ยนเป็น CLOSED
16. Commit หนึ่งครั้ง
17. ไม่มี Push

---

## 19. Stage and Commit

Stage แบบ explicit เท่านั้น:

```powershell
git add -- `
  ".agents/skills/project-read-first/SKILL.md" `
  ".agents/skills/project-read-first/scripts/preflight.ps1" `
  ".agents/skills/project-read-first/references/DOCUMENT_READ_POLICY.md" `
  ".agents/skills/project-read-first/references/PREFLIGHT_OUTPUT_CONTRACT.md" `
  ".agents/skills/project-read-first/references/SERENA_CODEGRAPH_PROTOCOL.md" `
  "04 Work Orders/CURRENT_WORK_ORDER.md" `
  "04 Work Orders/WO-OBSIDIAN-002-INSTALL-PROJECT-READ-FIRST.md" `
  "04 Work Orders/Work Order Index.md" `
  "00 Dashboard/Project Dashboard.md" `
  "AGENTS.md" `
  "README.md"

git diff --cached --check
git diff --cached --stat
git diff --cached
```

ตรวจว่า staged paths ตรง Allowed Files ก่อน Commit:

```powershell
git commit -m "docs: install project read-first skill"
```

ห้าม Push

---

## 20. Final Report

```text
WORK_ORDER: WO-OBSIDIAN-002
RESULT: COMPLETED | BLOCKED | PARTIAL

REPOSITORY_ROOT:
BRANCH:
HEAD_BEFORE_PULL:
REMOTE_HEAD:
PULL_RESULT:
HEAD_AFTER_PULL:

HEAD_BEFORE_COMMIT:
HEAD_AFTER_COMMIT:
COMMIT:

PREEXISTING_OWNER_ARTIFACTS:
UNEXPECTED_DIRTY_FILES:

FILES_CREATED:
FILES_UPDATED:
FILES_DELETED:
FILES_CHANGED_OUTSIDE_SCOPE:

SKILL_PATH:
POWERSHELL_SYNTAX:
OUTPUT_CONTRACT:
TERMINAL_DECISIONS:
LIGHTROOM_SPECIFIC_LEAKAGE:

SEVEN_EXECUTION_RULES:
FOUR_AI_FAILURE_MODES:
CURRENT_WORK_ORDER_STATUS:
WORK_ORDER_AUTHORITY_RECONCILED:
DASHBOARD_STATUS_LABEL_RECONCILED:

EXTERNAL_REPOSITORIES_MODIFIED:
PLUGINS_INSTALLED:
SECRETS_ADDED:
PUSH_PERFORMED:

REMAINING_RISKS:
NEXT_RECOMMENDED_ACTION:
```

ห้ามรายงาน `COMPLETED` หากไม่มี commit SHA หรือ Validation ข้อใดข้อหนึ่งยังไม่ผ่าน
