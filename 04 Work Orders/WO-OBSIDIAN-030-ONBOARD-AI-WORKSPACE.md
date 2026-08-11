# WORK ORDER — ONBOARD AI-WORKSPACE

Work Order ID: WO-OBSIDIAN-030
Title: WO-OBSIDIAN-030 — Onboard AI-Workspace
Risk Level: LOW
Task Classification: Documentation / Project Onboarding / Knowledge Base Governance
Execution Mode: Bounded Single Work Order
Owner: Toto
Target Vault: `D:\Obsidian\Project-Knowledge-Vault`
Status: CLOSED

> ใบงานนี้ถูก Activate + Execute เรียบร้อยแล้ว (2026-08-11) — ดู §14 Closeout Status
> การ Activate ได้รับ Owner authorization ชัดเจน
> หมายเหตุ: คำสั่งระบุ source `D:\AI-Workspace` ไม่มีจริง — resolved จริงคือ `D:\ai-tools\AI-Workspace` (ตาม WO-024 + git truth)

---

## 1. Objective

Onboard โปรเจกต์ `AI-Workspace` ที่ผ่าน recommendation gate จาก WO-OBSIDIAN-024 (Triage Class = `project`, Evidence = `verified`) เข้าสู่ Project Knowledge Vault เป็นโปรเจกต์เดียวที่ bounded หนึ่งงาน โดยใช้ repository truth ปัจจุบัน และรักษาโมเดล authority ของ Vault

ลำดับ onboarding ทีละโปรเจกต์: `thai_stt_app` (WO-025 ✅) → `lumina-studio` (WO-026 ✅) → `lightroom-ai-exposure` (WO-027 ✅) → `citizen_portal` (WO-028 ✅) → `TalkToClibord` (WO-029 ✅) → **`AI-Workspace` (WO-030)** — โปรเจกต์สุดท้ายใน eligible gate

---

## 2. Repository Authority

Vault repository: `expellirmud-dot/Obsidian`
Local Vault: `D:\Obsidian\Project-Knowledge-Vault`
Default branch: `main`

Source repository (READ-ONLY ในรอบ execute):
- Target path (จากคำสั่งสร้าง draft): `D:\AI-Workspace`
- WO-024 draft evidence (อาจล้าสมัย): `D:\ai-tools\AI-Workspace`, remote `expellirmud-dot/Expellirmud-AI-Workspace`, branch `main`, 47 commits
- ⚠️ **Path discrepancy:** draft ระบุ `D:\AI-Workspace` แต่ WO-024 ระบุ `D:\ai-tools\AI-Workspace` — ในรอบ execute ต้อง resolve จาก `git rev-parse --show-toplevel` จริง และรายงาน path ที่ถูกต้อง (บันทึกไว้เพื่อไม่ให้เดาผิด)

Authority order:

1. Source repository (`D:\AI-Workspace` หรือ path จริงที่ resolve ได้) และไฟล์จริง
2. Current Work Order / Current Task pointer ของ source repo (ถ้ามี)
3. Authority documentation ภายใน source repo (`AGENTS.md`, `README*`, docs)
4. Project Registry และ Project Overview ใน Vault
5. Conversation / memory

Vault ห้ามยกระดับข้อมูลที่ยังไม่ได้ตรวจเป็น verified

---

## 3. Mandatory Read First (future execution)

ก่อนแก้ไฟล์ ให้ปฏิบัติตาม `.agents/skills/project-read-first/SKILL.md` และอ่านอย่างน้อย:

1. `AGENTS.md` (Vault)
2. `README.md` (Vault)
3. `.agents/skills/project-read-first/SKILL.md`
4. `.agents/skills/project-context-discovery/SKILL.md`
5. `01 Projects/Project Registry.md`
6. `01 Projects/Project Index.md`
7. `00 Dashboard/Project Dashboard.md`
8. Source repo authority files ที่พบจาก repo truth จริง (เช่น `AGENTS.md`, `README*`, `CLAUDE.md`, `WORK_ORDER.md`, `INDEX.md`)
9. Source repo git truth: `branch`, `HEAD`, `status`
10. Current task / work-order authority ของ source repo (ถ้ามี)

ต้องผลิต `READ_FIRST_PREFLIGHT` และเริ่มแก้ไฟล์ได้เมื่อ `PREFLIGHT_DECISION: READY` เท่านั้น

---

## 4. Required Future Outcome

สร้าง Project Overview:

`01 Projects/AI-Workspace.md`

Project Overview ต้องครอบคลุมหัวข้อที่ AGENTS.md กำหนด (Required Project Page Sections) และมีเฉพาะข้อมูลที่รองรับด้วยหลักฐาน:
- โปรเจกต์นี้คืออะไร
- ปัญหาที่ต้องการแก้
- เป้าหมายหลัก
- ขอบเขต
- ตำแหน่งไฟล์จริง
- Repository
- สถานะปัจจุบัน
- สิ่งที่ทำเสร็จแล้ว
- งานที่กำลังทำ
- งานถัดไป
- สถาปัตยกรรม
- การตัดสินใจสำคัญ
- ปัญหาและความเสี่ยง
- บทเรียน
- Resume Context
- วันที่ตรวจสอบล่าสุด

---

## 5. Evidence Classification

ทุกข้อสรุปต้องติดป้ายแหล่งที่มาเป็นหนึ่งใน:

- `verified` — หลักฐานจาก repo / file / command output ในรอบ execute
- `owner-confirmed` — Owner ยืนยันโดยตรง แต่ยังไม่ตรวจ source ในรอบนี้
- `inference` — สันนิษฐานจากบริบท/ชื่อ/โครงสร้าง (ต้องระบุชัด)
- `unknown` / `needs-verification` — พบชื่อ/ทาง แต่หลักฐานไม่พอ

ห้ามเลื่อน `inference` เป็น `verified` โดยไม่มีหลักฐานจริงในรอบนั้น

---

## 6. Registry / Index / Dashboard Updates (future execution)

### 6.1 Project Registry
- `Import State`: `discovered-not-imported` → `imported` **เฉพาะหลังจากมี evidence การ execute จริง** (ห้ามเปลี่ยนในรอบ PLANNED)
- รับรอง/รีเฟรช verification evidence จากรอบ execute จริง
- `Triage Class` คง `project` เว้นแต่ repo truth ขัดแย้ง
- ห้ามอนุมาน lifecycle โดยไม่มีหลักฐาน (Lifecycle State คง `unknown` เว้นมี proof)

### 6.2 Project Index
- เพิ่มแถว `[[AI-Workspace]]` ในตาราง (พร้อม Description / Local Path / Status / Last Verified)
- ลิงก์กลับ `[[Project Dashboard]]`

### 6.3 Project Dashboard
- ย้าย `AI-Workspace` จากหมวด **Discovered — Not Imported** ไป **Imported Projects**
- ห้ามออกแบบ dashboard ใหม่ — แก้เฉพาะจุดที่ต้องย้าย

---

## 7. Architecture Handling

ห้ามสร้าง Architecture document ใหม่อัตโนมัติ เว้นแต่กฎ/template ของ Vault ต้องการ และมี source evidence เพียงพอ
หากสถาปัตยกรรมอยู่นอกขอบเขต:
- สรุปสถาปัตยกรรมแบบย่อใน Project Overview
- บันทึกเป็น follow-up (ไม่สร้างไฟล์ ARCH- ในรอบนี้)

---

## 8. Hard Boundaries

1. ห้ามแก้ Source Code ของ source repo
2. ห้าม commit / push ไปยัง source repository
3. Source repository ต้องเป็น READ-ONLY
4. ห้ามคัดลอก source code ยกเว้น identifier / ตัวอย่างขั้นต่ำที่จำเป็นสำหรับบริบท
5. ห้ามทำซ้ำ implementation details จาก repo
6. ห้ามแก้ `.obsidian/`
7. ห้ามติดตั้ง plugin / Obsidian Community Plugin
8. ห้ามทำ Live Project Wall
9. ห้ามทำ automation / webhook / polling / daemon
10. ห้ามแก้ Project Overview อื่นที่ไม่เกี่ยวข้อง
11. ห้ามเก็บ Secret / Token / Password / Cookie / Credential (รวมใน remote URL)
12. ห้ามลบ Project Overview / Registry entry / ประวัติเดิม
13. ห้ามเปลี่ยน `04 Work Orders/CURRENT_WORK_ORDER.md` เว้นแต่ Owner อนุญาตให้ activate WO-030 แยกต่างหาก
14. ห้ามแก้ `01 Projects/STT Typing.md` (pre-existing CRLF artifact — out-of-scope)
15. ห้ามแก้ `04 Work Orders/Work Order Index.md` (pre-existing CRLF artifact — out-of-scope)
16. ห้ามแก้ owner notes (untracked: `2026-08-11.md`, canvas files)

---

## 9. Allowed Files (future execution)

อนุญาตให้แก้เฉพาะ:

- `01 Projects/AI-Workspace.md` (new — Project Overview)
- `01 Projects/Project Registry.md` (import transition + refresh evidence)
- `01 Projects/Project Index.md` (เพิ่มแถว)
- `00 Dashboard/Project Dashboard.md` (ย้ายเข้า Imported Projects)
- `04 Work Orders/CURRENT_WORK_ORDER.md` (เปิด pointer → WO-030 ACTIVE, ปิด → CLOSED ให้ครบ proof chain)
- `04 Work Orders/WO-OBSIDIAN-030-ONBOARD-AI-WORKSPACE.md` เฉพาะการอัปเดตสถานะ/หลักฐาน closeout เมื่อจบงาน

หากจำเป็นต้องแก้ไฟล์อื่น ให้ STOP และรายงานเหตุผลก่อน

---

## 10. Validation (future execution)

ก่อนปิดงาน ต้องตรวจอย่างน้อย:

1. exact source repo path/root ถูก resolve (`git rev-parse --show-toplevel` — ต้องยืนยัน `D:\AI-Workspace` vs `D:\ai-tools\AI-Workspace`)
2. source git status / branch / HEAD ถูกจับได้ (`git status --short`, `git branch --show-current`, `git rev-parse HEAD`)
3. source authority files ถูกระบุจาก repo จริง (ไม่ใช่เดา)
4. Project Overview มีครบทุกหัวข้อที่ AGENTS.md กำหนด
5. ไม่มีการอ้างสถานะปัจจุบันที่ไม่มีหลักฐาน
6. Registry import transition ถูกต้อง (`discovered-not-imported` → `imported`)
7. Dashboard ไม่แสดง `AI-Workspace` ใน Discovered — Not Imported อีกต่อไป
8. wikilinks ทั้งหมด resolve ตามชื่อไฟล์จริง
9. source repo ไม่มีการเปลี่ยนแปลง (READ-ONLY enforced)
10. diff แตะเฉพาะ Allowed Files
11. pre-existing CRLF artifacts (`STT Typing.md`, `Work Order Index.md`) ยังคง out-of-scope (ไม่ถูก stage/commit)
12. owner notes ยังคง untouched
13. แสดง diff summary ก่อน commit

---

## 11. Definition of Done (future execution)

WO-OBSIDIAN-030 ถือว่า DONE เมื่อครบทุกข้อ:

- [ ] Read-first preflight ผ่าน (`READY`)
- [ ] มี Project Overview เดียวที่ verified สำหรับ `AI-Workspace`
- [ ] Registry ทำเครื่องหมาย `imported`
- [ ] Project Index และ Dashboard สอดคล้องกัน
- [ ] Proof chain ปิด (Activate → Execute → Close → Commit)
- [ ] Source repo ไม่เปลี่ยน
- [ ] ไม่มีการแก้ source repository / .obsidian / plugin / automation
- [ ] Validation ผ่าน
- [ ] Diff อยู่ใน Allowed Files เท่านั้น

---

## 12. Commit / Push Policy

- Worker เตรียม diff + validation ตาม WO
- ก่อน commit ต้องตรวจว่า working tree ไม่มี unrelated changes (เฉพาะ Allowed Files ที่ stage)
- **สำหรับการสร้างใบงาน (draft) นี้:** commit ได้หนึ่งครั้งเพื่อสร้างเอกสาร WO-030 เท่านั้น stage เฉพาะไฟล์ WO-030
- **สำหรับการ execute onboarding ในอนาคต:** commit/push ต้องมี Owner authorization แยกในรอบนั้น
- ห้าม push เว้นแต่ Owner อนุญาตชัดเจน

Suggested commit message (draft creation):

`docs: add WO-OBSIDIAN-030 onboard AI-Workspace (planned)`

---

## 13. Expected Closeout Report (future execution)

- Source repo path + HEAD + branch + status
- Authority files ที่พบ
- รายชื่อไฟล์ที่แก้
- Validation performed
- Git status (รวม owner notes + CRLF artifacts)
- Evidence classification summary
- Remaining risks / unknowns
- หมายเหตุ: นี่คือ WO สุดท้ายใน eligible `project + verified` gate — ภายหลังปิด WO-030 ให้รายงานสถานะ remaining repos ที่รอเจ้าของตัดสิน (tooling-infrastructure 6 ตัว + sandbox/backup/dup/unknown)

---

## 14. Closeout Status (updated 2026-08-11)

- **Status:** CLOSED — committed (owner-authorized bounded commit; NO push)
- **Preflight:** `PREFLIGHT_DECISION: READY` (VAULT_DOCUMENTATION)
- **Source repo:** READ-ONLY — ไม่มีการแก้ไข `D:\ai-tools\AI-Workspace` (pre-existing dirty tracked `.serena/project.yml` + `src/App.jsx` คงเดิม บันทึกเพื่อความโปร่งใส)
- **Path correction:** คำสั่งสร้าง draft ระบุ `D:\AI-Workspace` (ไม่มีจริง) → resolved จริง `D:\ai-tools\AI-Workspace` (git truth + WO-024 evidence) — บันทึกใน Overview + Registry เพื่อไม่ให้เดาผิด

### Source repo truth (fresh, 2026-08-11)
- Resolved path/root: `D:\ai-tools\AI-Workspace` (`git rev-parse --show-toplevel`)
- Branch: `main`
- HEAD: `69340677fb61af3e7d2b7f840363632f3211f5fd` (short `6934067`)
- Commits: 47
- Status: **pre-existing dirty tracked files** (`.serena/project.yml`, `src/App.jsx`) — not caused by this WO
- Remote: `https://github.com/expellirmud-dot/Expellirmud-AI-Workspace.git`
- Authority files (actual): `README.md`, `AGENTS.md`, `WORKSPACE.md` (Workspace Contract v1), `workspace-modules.yaml`, `CLI_MODEL_CATALOG.md`, `ai-ops-registry/AGENTS.md`, `ai-ops-registry/registry/REGISTRY_CONTRACT.md`, `ai-ops-registry/docs/READ_FIRST_POLICY.md`, `docs/CONNECTOR_GATEWAY_RUNBOOK.md`
- Current work state: ไม่มี AGENTS/work-order pointer ใน source; git log ล่าสุด = maintenance/infra tasks (task pack composer, registry YAML validation, connector token docs, dashboard workflow) + last commit 2026-06-30 → stable / maintenance, ไม่มี active task tracker ชัดเจน

### Files changed (Allowed Files only)
- `01 Projects/AI-Workspace.md` (new — Project Overview)
- `01 Projects/Project Registry.md` (DIS→IMP, evidence refresh, counts 11 imported / 18 discovered)
- `01 Projects/Project Index.md` (แถวใหม่)
- `00 Dashboard/Project Dashboard.md` (ย้ายเข้า Imported Projects)
- `04 Work Orders/CURRENT_WORK_ORDER.md` (pointer → WO-030 CLOSED)
- `04 Work Orders/WO-OBSIDIAN-030-ONBOARD-AI-WORKSPACE.md` (closeout)

### Validation results (WO §10)
1. ✅ exact source root resolved (คำสั่ง `D:\AI-Workspace` ไม่มี → จริง `D:\ai-tools\AI-Workspace` ตาม git truth)
2. ✅ git status/branch/HEAD captured (main, 6934067, dirty pre-existing)
3. ✅ authority files identified from actual repo (README/AGENTS/WORKSPACE/workspace-modules/ai-ops-registry — ไม่ใช้เดาสันนิษฐาน)
4. ✅ Project Overview มีครบทุกหัวข้อ AGENTS.md
5. ✅ ไม่มี unsupported current-status claims (lifecycle = UNK, ไม่ infer; source ไม่มี active WO → ไม่อ้าง active task)
6. ✅ Registry import transition ถูกต้อง (DIS→IMP)
7. ✅ Dashboard ไม่แสดง AI-Workspace ใน Discovered — Not Imported อีกต่อไป
8. ✅ wikilinks ทั้งหมด resolve ([[AI-Workspace]], [[Project Registry]], [[Project Index]], [[Project Dashboard]])
9. ✅ source repo unchanged (READ-ONLY enforced; pre-existing dirty คงเดิม)
10. ✅ diff เฉพาะ Allowed Files
11. ✅ pre-existing CRLF artifacts (`STT Typing.md`, `Work Order Index.md`) ยังคง out-of-scope (ไม่ถูก stage)
12. ✅ owner notes + canvas/base files ยังคง untouched
13. ✅ diff summary ก่อน commit

### Remaining Registry categories/counts (หลังปิด WO-030 — โปรเจกต์สุดท้ายใน eligible `project + verified` gate)
- **Imported (IMP): 11** — `llm-agents`, `STT Typing`, `AI Worker Harness`, `Utility Disbursement App`, `Adobe Stock Upload Assistant`, `thai_stt_app`, `lumina-studio`, `lightroom-ai-exposure`, `citizen_portal`, `TalkToClibord`, `AI-Workspace`
- **Discovered-not-imported (DIS): 18** แบ่งตาม Triage Class:
  - `tooling-infrastructure` (TLG): 6 — ต้อง Owner ยืนยัน lifecycle อิสระก่อนติดตาม (conditionally eligible)
  - `sandbox-experiment` (SBX): 6 — ไม่ผ่าน gate อัตโนมัติ
  - `backup-archive-candidate` (BAK): 2
  - `duplicate-superseded-candidate` (DUP): 1
  - `unknown` (UNK): 3 — needs-verification (`Automation`, `JAVIS_Nexus`, `office_council_keeper`)
- **unknown (UNK import): 0**
- **รวม repos ที่พบ: 29** (reconcile = 29, missing = 0)
- **Automatically eligible gate:** 0 เหลือ (onboard ครบ `project + verified` 6 ตัวแล้ว)

### Evidence classification
- verified: repo truth 2026-08-11 (structure, HEAD, status, authority files, source work state)
- needs-verification: ไม่มีประเด็นค้างในรอบนี้

### Unresolved / needs-verification
- Source ไม่มี AGENTS.md / work-order pointer → ไม่มี current-task authority ชัดเจน (สถานะสืบจาก git log)
- Source มี pre-existing dirty tracked files (`.serena/project.yml`, `src/App.jsx`) — บันทึก ไม่นำมาสรุปสถาปัตยกรรมหลัก
- ชื่อ `AI-Workspace` คือ orchestration workspace ไม่ใช่ product app เดี่ยว — บันทึกเพื่อป้องกันเข้าใจผิด (Vault governance "Repository ≠ Project / Tooling ≠ Project")
- Path ในคำสั่ง (`D:\AI-Workspace`) ล้าสมัย — ที่จริง `D:\ai-tools\AI-Workspace` (บันทึกใน Registry + Overview)
- Lifecycle เจตนาปล่อย `unknown` (ไม่ infer)

### Recommended next (beyond this gate)
Remaining DIS 18 ตัวรอเจ้าของตัดสิน:
- `tooling-infrastructure` ×6 → หากเจ้าของยืนยันว่ามี lifecycle อิสระ จึงติดตาม/ onboard ได้
- `sandbox-experiment` ×6, `backup-archive-candidate` ×2, `duplicate-superseded-candidate` ×1, `unknown` ×3 → ไม่ผ่าน gate โดยอัตโนมัติ ต้องเจ้าของสั่ง explicitly
