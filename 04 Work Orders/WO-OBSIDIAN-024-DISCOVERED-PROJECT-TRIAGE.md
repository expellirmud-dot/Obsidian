# WORK ORDER — DISCOVERED PROJECT TRIAGE

Work Order ID: WO-OBSIDIAN-024
Title: WO-OBSIDIAN-024 — Discovered Project Triage
Risk Level: LOW
Task Classification: Documentation / Repository Inventory / Knowledge Base Governance
Execution Mode: Bounded Single Work Order
Owner: Toto
Target Vault: `D:\Obsidian\Project-Knowledge-Vault`
Status: PLANNED

> ใบงานนี้เป็น **draft PLANNED เท่านั้น** — ยังไม่ Activate และห้าม execute ในรอบที่สร้างไฟล์นี้
> การ Activate + Execute ต้องรอ Owner สั่งแยกต่างหาก

---

## 1. Objective

Triage รายการ **24 discovered-not-imported repositories** จาก WO-OBSIDIAN-023 โดยใช้หลักฐานจาก repository แบบ read-only เพื่อให้ Vault แยกได้ว่าอะไรคือโปรเจกต์จริง อะไรคือ sandbox / tooling / backup-duplicate / archive candidate หรือยังสรุปไม่ได้ **ก่อน** จะทำ onboarding หรือ Live Project Wall

หลักการถาวรที่ WO นี้ต้องสถาปนา:

> **Repository ≠ Project.** การมี `.git` ไม่ได้แปลว่าเป็นโปรเจกต์ที่ควรอยู่บน Project Wall

WO นี้เป็นการ **classify-only** ไม่ใช่ onboarding และไม่ใช่ automation

---

## 2. Repository Authority

Vault repository: `expellirmud-dot/Obsidian`
Local Vault: `D:\Obsidian\Project-Knowledge-Vault`
Default branch: `main`

Authority order:

1. Source repository และไฟล์จริงของแต่ละ repo ที่ตรวจ
2. Current Work Order / Current Task Pointer ของ source repo
3. Authority documentation ภายใน source repo
4. Project Registry ใน Vault
5. Conversation / memory

Vault ห้ามยกระดับข้อมูลที่ยังไม่ได้ตรวจเป็น verified

---

## 3. Mandatory Read First

ก่อนแก้ไฟล์ ให้ปฏิบัติตาม `.agents/skills/project-read-first/SKILL.md` และอ่านอย่างน้อย:

1. `AGENTS.md`
2. `README.md`
3. `00 Dashboard/Project Dashboard.md`
4. `01 Projects/Project Registry.md`
5. `01 Projects/Project Index.md`
6. `04 Work Orders/CURRENT_WORK_ORDER.md`
7. `04 Work Orders/WO-OBSIDIAN-023-PROJECT-REGISTRY-AND-MISSING-PROJECT-DISCOVERY.md`
8. `.agents/skills/project-context-discovery/SKILL.md`

ต้องผลิต `READ_FIRST_PREFLIGHT` และเริ่มแก้ไฟล์ได้เมื่อ `PREFLIGHT_DECISION: READY` เท่านั้น

---

## 4. Scope of Triage

ตรวจเฉพาะ 24 repositories ที่ Registry จำแนกเป็น `discovered-not-imported` (Import = DIS):

```text
.sandbox/01-longcat
.sandbox/02-deepseek-v4
.sandbox/03-nemotron-ultra
.sandbox/04-step-3.7
.sandbox/05-mimo-v2.5
.sandbox/06-north-mini
ai-tools-kit
AI-Workspace
computer-use-preview
gridgeist
lightroom-ai-exposure
Automation
citizen_portal
JAVIS_Nexus
lumina-studio
mcp-agentic-framework
office_council_keeper
Utility Automation2
utility_automation_v2
utility_automation_v2_light
stt-openhands-batch-draft
TalkToClibord
thai_stt_app
codegraph
```

รายการอ้างอิงจาก Registry — หากไม่ตรงกับ Registry ตอน execute ให้ยึด Registry เป็นแหล่ง แล้วรายงานส่วนต่าง

Repository ทั้งหมดนี้ต้องถูกตรวจแบบ **READ-ONLY**

---

## 5. Triage Taxonomy (bounded)

`Triage Class` ต้องเป็นค่าใดค่าหนึ่งต่อไปนี้เท่านั้น:

- `project` — โปรเจกต์จริงที่ควรพิจารณา onboard
- `sandbox-experiment` — scratch / spike / model trial / throwaway
- `tooling-infrastructure` — เครื่องมือ / infra / library ที่ support งานอื่น ไม่ใช่ product
- `duplicate-superseded-candidate` — น่าจะซ้ำหรือถูกแทนที่ด้วย repo อื่น (candidate — ต้องมีหลักฐานชี้ target)
- `backup-archive-candidate` — สำเนา/สำรอง หรืออยู่ใน backup location
- `unknown` — หลักฐานไม่พอสรุป

คำว่า `candidate` มีความหมาย: เป็นข้อสงสัยที่มีหลักฐานรองรับ **ไม่ใช่** ข้อสรุปสุดท้ายของ lifecycle

---

## 6. Evidence Rules (บังคับ)

### 6.1 ชื่อไม่พอ

> Repository name เพียงอย่างเดียว **ไม่ถือเป็นหลักฐานเพียงพอ** สำหรับ final classification

ทุก final Triage Class ต้องอ้างหลักฐานจริงอย่างน้อยหนึ่งชิ้นจากแหล่งใน §6.2 ถ้าไม่มี ให้เป็น `unknown`

### 6.2 Evidence Sources (read-only)

- Repository root file listing
- `README*`, `AGENTS*`, project metadata / docs
- Current Work Order / current task pointer ภายใน repo (ถ้ามี)
- `git branch`, `git rev-parse HEAD`, recent commit history (`git log --oneline -n`)
- `git remote get-url origin` (remote URL — ห้ามเก็บ token/credential)
- Package/project manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, ฯลฯ)
- Archive/backup location (เช่นอยู่ใต้ `project_backups/`)
- Explicit owner-confirmed evidence

### 6.3 Evidence Classification ≠ Triage Class

สองมิตินี้แยกกันเด็ดขาด ต้องบันทึกทั้งคู่:

- **Triage Class** — repo คืออะไร (§5)
- **Evidence Classification** — เชื่อได้แค่ไหน:
  - `verified` — มีหลักฐานจาก file/command output ในรอบ execute
  - `owner-confirmed` — Owner ยืนยันตรง แต่ยังไม่ตรวจ source ในรอบนี้
  - `needs-verification` — ยังไม่มีหลักฐานพอ

ห้ามใช้ `verified` หากตรวจเพียงข้อมูลใน Vault เดิม

### 6.4 ห้ามอนุมาน lifecycle จาก Triage Class

Triage Class ไม่แปลงเป็น Lifecycle State อัตโนมัติ ตัวอย่างที่ห้าม:

- `tooling-infrastructure` **ไม่** เท่ากับ `archived`
- `duplicate-superseded-candidate` **ไม่** กลายเป็น `superseded` โดยไม่มีหลักฐาน
- `backup-archive-candidate` **ไม่** เท่ากับ `archived` lifecycle

Lifecycle State ใน Registry ของ discovered repos ยังคง `unknown` เว้นแต่มีหลักฐาน/owner ยืนยันแยก

---

## 7. Required Outcome (future execution)

การเปลี่ยนแปลง Vault หลักที่ตั้งใจในรอบ execute:

เพิ่ม **Triage Class + Triage Evidence (สั้น กระชับ)** ลงใน `01 Projects/Project Registry.md` สำหรับ 24 discovered entries

รูปแบบที่แนะนำ: เพิ่มคอลัมน์/ฟิลด์ `Triage Class` และ `Triage Evidence` (หรือ section เสริมใน Registry) โดยไม่ทำลายโครงสร้าง/entry เดิม และไม่แตะ 5 imported entries

ห้ามในรอบ execute:

- ห้ามสร้าง Project Overview ให้ discovered repo (no onboarding)
- ห้ามเปลี่ยน Import State ของ discovered repos เป็น `imported`
- ห้ามเปลี่ยน Lifecycle State จาก Triage Class เพียงอย่างเดียว

---

## 8. Hard Boundaries

1. ห้ามแก้ Source Code ของ repository ภายนอกใด ๆ
2. ห้าม commit / push ไปยัง source repositories ภายนอก
3. Source repositories ทั้งหมดเป็น READ-ONLY
4. ห้าม onboard / สร้าง Project Overview ใน WO-024
5. ห้ามทำ Live Project Wall
6. ห้ามทำ webhook, polling, daemon, background service
7. ห้ามติดตั้ง Obsidian Community Plugin หรือ automation ใด ๆ
8. ห้ามแก้ `.obsidian/`
9. ห้ามเก็บ Secret, Token, Password, Cookie, Credential (รวมถึงใน remote URL)
10. ห้ามลบ Project Overview / Registry entry / ประวัติเดิม
11. ห้ามจัดหมวด imported project ใหม่ (5 imported ต้องคงเดิม)
12. ห้ามแก้ `04 Work Orders/CURRENT_WORK_ORDER.md` เว้นแต่ Owner อนุญาตให้ activate WO-024 แยกต่างหาก

---

## 9. Allowed Files (future execution)

อนุญาตให้แก้เฉพาะ:

- `04 Work Orders/CURRENT_WORK_ORDER.md` (เปิด pointer → WO-024 ACTIVE และปิด → CLOSED ให้ครบ proof chain)
- `01 Projects/Project Registry.md` (เพิ่ม Triage Class + Triage Evidence ให้ 24 discovered entries)
- `04 Work Orders/WO-OBSIDIAN-024-DISCOVERED-PROJECT-TRIAGE.md` เฉพาะการอัปเดตสถานะ/หลักฐาน closeout เมื่อจบงาน

การแก้ `00 Dashboard/Project Dashboard.md` หรือ `01 Projects/Project Index.md` **ไม่อยู่ในขอบเขต WO-024** เว้นแต่ Owner ขยาย scope ชัดเจน

หากจำเป็นต้องแก้ไฟล์อื่น ให้ STOP และรายงานเหตุผลก่อน

---

## 10. Validation (future execution)

ก่อนปิดงาน ต้องตรวจอย่างน้อย:

1. `git status --short`
2. ตรวจว่าแก้เฉพาะ Allowed Files
3. ครบทั้ง **24 discovered entries** ถูกพิจารณา (นับได้ = 24)
4. ไม่มี imported project ใดถูกจัดหมวดใหม่ (5 imported คงเดิม — Import/Lifecycle/Verify ไม่เปลี่ยน)
5. ทุก final classification มี Triage Evidence อ้างอิงจริง
6. เคสที่หลักฐานไม่พอ = `unknown` และ Evidence Classification = `needs-verification`
7. Triage Class ทุกค่าอยู่ใน taxonomy §5 เท่านั้น
8. ไม่มี lifecycle ถูกเปลี่ยนจาก Triage Class เพียงอย่างเดียว
9. ไม่มี secret / credential (รวม remote URL)
10. source repositories ไม่มีการเปลี่ยนแปลงจากงานนี้
11. แสดง diff summary ก่อน commit

---

## 11. Definition of Done (future execution)

WO-OBSIDIAN-024 ถือว่า DONE เมื่อครบทุกข้อ:

- [ ] Read-first preflight ผ่าน (`READY`)
- [ ] ทั้ง 24 discovered repos ได้ Triage Class + Triage Evidence
- [ ] ทุก final Triage Class มีหลักฐานจริง (ไม่มีการสรุปจากชื่อล้วน)
- [ ] เคสหลักฐานไม่พอ = `unknown` / `needs-verification`
- [ ] Triage Class และ Evidence Classification ถูกบันทึกแยกกัน
- [ ] ไม่มี lifecycle เปลี่ยนจาก Triage Class เพียงอย่างเดียว
- [ ] 5 imported projects ไม่ถูกจัดหมวดใหม่
- [ ] ไม่มีการแก้ source repository ภายนอก
- [ ] ไม่มี onboarding / Live Wall / automation ถูกเพิ่ม
- [ ] Diff อยู่ใน Allowed Files เท่านั้น
- [ ] Validation ผ่าน
- [ ] Closeout report มี counts + recommendation gate

---

## 12. Closeout Output Counts

รายงานปิดงานต้องระบุจำนวนต่อ Triage Class:

- `project`
- `sandbox-experiment`
- `tooling-infrastructure`
- `duplicate-superseded-candidate`
- `backup-archive-candidate`
- `unknown`

รวมต้องเท่ากับ 24 (reconcile: sum(classes) = 24, missing = 0)

---

## 13. Post-Triage Onboarding Gate

หลัง triage เสร็จ:

Automatically eligible for onboarding consideration:
- `project` + `verified`
- `project` + `owner-confirmed`

Conditionally eligible:
- `tooling-infrastructure` + `verified` / `owner-confirmed`
  only when Owner confirms that the repository is an independently managed project
  worth tracking in the Project Knowledge Vault / Project Wall.

Not eligible without further evidence:
- `sandbox-experiment`
- `duplicate-superseded-candidate`
- `backup-archive-candidate`
- `unknown`

Triage Class must not automatically determine Lifecycle State.

recommendation gate นี้เป็นข้อเสนอ ไม่ใช่การเปลี่ยนสถานะ lifecycle

> กฎสำคัญที่รักษาไว้: `Repository ≠ Project`
> แต่ไม่กลายเป็น `Tooling ≠ Project` — tooling ที่ Owner ยืนยันว่ามี lifecycle เป็นอิสระยังคงเป็นโปรเจกต์ที่ติดตามได้

---

## 14. Commit / Push Policy

- Worker เตรียม diff + validation ตาม WO
- ก่อน commit ต้องตรวจว่า working tree ไม่มี unrelated changes
- **สำหรับการสร้างใบงาน (draft) นี้:** commit ได้หนึ่งครั้งเพื่อสร้างเอกสาร WO-024 เท่านั้น stage เฉพาะไฟล์ WO-024
- **สำหรับการ execute triage ในอนาคต:** commit/push ต้องมี Owner authorization แยกในรอบนั้น
- ห้าม push เว้นแต่ Owner อนุญาตชัดเจน

Suggested commit message (draft creation):

`docs: add WO-OBSIDIAN-024 discovered project triage (planned)`

---

## 15. Expected Closeout Report (future execution)

- counts ต่อ Triage Class (§12) + reconcile = 24
- รายชื่อ repos ที่ผ่าน recommendation gate (`project` + verified/owner-confirmed)
- รายชื่อ repos ที่ยัง `unknown` / `needs-verification`
- ไฟล์ที่แก้
- Validation performed
- Git status
- Remaining risks / unknowns
- Recommended next Work Order

Recommended next step หลัง WO-024 สำเร็จ:

`Import Missing Projects` เฉพาะ repos ที่ผ่าน recommendation gate ก่อนเริ่มงาน `Live Project State / Project Wall Automation`
