# WORK ORDER — ONBOARD LUMINA-STUDIO

Work Order ID: WO-OBSIDIAN-026
Title: WO-OBSIDIAN-026 — Onboard lumina-studio
Risk Level: LOW
Task Classification: Documentation / Project Onboarding / Knowledge Base Governance
Execution Mode: Bounded Single Work Order
Owner: Toto
Target Vault: `D:\Obsidian\Project-Knowledge-Vault`
Status: CLOSED

> ใบงานนี้ถูก Activate + Execute เรียบร้อยแล้ว (2026-08-11) — ดู §14 Closeout Status
> การ Activate ได้รับ Owner authorization ชัดเจน

---

## 1. Objective

Onboard โปรเจกต์ `lumina-studio` ที่ผ่าน recommendation gate จาก WO-OBSIDIAN-024 (Triage Class = `project`, Evidence = `verified`) เข้าสู่ Project Knowledge Vault เป็นโปรเจกต์เดียวที่ bounded หนึ่งงาน โดยใช้ repository truth ปัจจุบัน และรักษาโมเดล authority ของ Vault

ลำดับ onboarding ทีละโปรเจกต์: `thai_stt_app` (WO-025 ✅) → **`lumina-studio` (WO-026)** → `lightroom-ai-exposure` → `citizen_portal` → `TalkToClibord` → `AI-Workspace`

---

## 2. Repository Authority

Vault repository: `expellirmud-dot/Obsidian`
Local Vault: `D:\Obsidian\Project-Knowledge-Vault`
Default branch: `main`

Source repository (READ-ONLY ในรอบ execute):
- Local: `D:\lumina-studio`
- GitHub: `expellirmud-dot/LUMINA-Studio` (remote จาก WO-024 evidence: `expellirmud-dot/LUMINA-Studio`, branch `main`, 93 commits)

Authority order:

1. Source repository (`D:\lumina-studio`) และไฟล์จริง
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
8. Source repo authority files ที่พบจาก repo truth จริง (เช่น `AGENTS.md`, `README*`, `WORK_ORDER.md`, `INDEX.md`)
9. Source repo git truth: `branch`, `HEAD`, `status`
10. Current task / work-order authority ของ source repo (ถ้ามี)

ต้องผลิต `READ_FIRST_PREFLIGHT` และเริ่มแก้ไฟล์ได้เมื่อ `PREFLIGHT_DECISION: READY` เท่านั้น

---

## 4. Required Future Outcome

สร้าง Project Overview:

`01 Projects/lumina-studio.md`

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
- เพิ่มแถว `[[lumina-studio]]` ในตาราง (พร้อม Description / Local Path / Status / Last Verified)
- ลิงก์กลับ `[[Project Dashboard]]`

### 6.3 Project Dashboard
- ย้าย `lumina-studio` จากหมวด **Discovered — Not Imported** ไป **Imported Projects**
- ห้ามออกแบบ dashboard ใหม่ — แก้เฉพาะจุดที่ต้องย้าย

---

## 7. Architecture Handling

ห้ามสร้าง Architecture document ใหม่อัตโนมัติ เว้นแต่กฎ/template ของ Vault ต้องการ และมี source evidence เพียงพอ
หากสถาปัตยกรรมอยู่นอกขอบเขต:
- สรุปสถาปัตยกรรมแบบย่อใน Project Overview
- บันทึกเป็น follow-up (ไม่สร้างไฟล์ ARCH- ในรอบนี้)

---

## 8. Hard Boundaries

1. ห้ามแก้ Source Code ของ `D:\lumina-studio`
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
13. ห้ามเปลี่ยน `04 Work Orders/CURRENT_WORK_ORDER.md` เว้นแต่ Owner อนุญาตให้ activate WO-026 แยกต่างหาก

---

## 9. Allowed Files (future execution)

อนุญาตให้แก้เฉพาะ:

- `01 Projects/lumina-studio.md` (new — Project Overview)
- `01 Projects/Project Registry.md` (import transition + refresh evidence)
- `01 Projects/Project Index.md` (เพิ่มแถว)
- `00 Dashboard/Project Dashboard.md` (ย้ายเข้า Imported Projects)
- `04 Work Orders/CURRENT_WORK_ORDER.md` (เปิด pointer → WO-026 ACTIVE, ปิด → CLOSED ให้ครบ proof chain)
- `04 Work Orders/WO-OBSIDIAN-026-ONBOARD-LUMINA-STUDIO.md` เฉพาะการอัปเดตสถานะ/หลักฐาน closeout เมื่อจบงาน

หากจำเป็นต้องแก้ไฟล์อื่น ให้ STOP และรายงานเหตุผลก่อน

---

## 10. Validation (future execution)

ก่อนปิดงาน ต้องตรวจอย่างน้อย:

1. exact source repo path/root ถูก resolve (`D:\lumina-studio`, `git rev-parse --show-toplevel`)
2. source git status / branch / HEAD ถูกจับได้ (`git status --short`, `git branch --show-current`, `git rev-parse HEAD`)
3. authority files ถูกระบุจาก repo จริง (ไม่ใช่เดา)
4. Project Overview มีครบทุกหัวข้อที่ AGENTS.md กำหนด
5. ไม่มีการอ้างสถานะปัจจุบันที่ไม่มีหลักฐาน
6. Registry import transition ถูกต้อง (`discovered-not-imported` → `imported`)
7. Dashboard ไม่แสดง `lumina-studio` ใน Discovered — Not Imported อีกต่อไป
8. wikilinks ทั้งหมด resolve ตามชื่อไฟล์จริง
9. source repo ไม่มีการเปลี่ยนแปลง (READ-ONLY enforced)
10. diff แตะเฉพาะ Allowed Files
11. owner notes (untracked) ยังคง untouched
12. แสดง diff summary ก่อน commit

---

## 11. Definition of Done (future execution)

WO-OBSIDIAN-026 ถือว่า DONE เมื่อครบทุกข้อ:

- [ ] Read-first preflight ผ่าน (`READY`)
- [ ] มี Project Overview เดียวที่ verified สำหรับ `lumina-studio`
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
- ก่อน commit ต้องตรวจว่า working tree ไม่มี unrelated changes
- **สำหรับการสร้างใบงาน (draft) นี้:** commit ได้หนึ่งครั้งเพื่อสร้างเอกสาร WO-026 เท่านั้น stage เฉพาะไฟล์ WO-026
- **สำหรับการ execute onboarding ในอนาคต:** commit/push ต้องมี Owner authorization แยกในรอบนั้น
- ห้าม push เว้นแต่ Owner อนุญาตชัดเจน

Suggested commit message (draft creation):

`docs: add WO-OBSIDIAN-026 onboard lumina-studio (planned)`

---

## 13. Expected Closeout Report (future execution)

- Source repo path + HEAD + branch + status
- Authority files ที่พบ
- รายชื่อไฟล์ที่แก้
- Validation performed
- Git status (รวม owner notes)
- Evidence classification summary
- Remaining risks / unknowns
- Recommended next Work Order (onboard `lightroom-ai-exposure`)

---

## 14. Closeout Status (updated 2026-08-11)

- **Status:** CLOSED — committed (owner-authorized bounded commit; NO push)
- **Preflight:** `PREFLIGHT_DECISION: READY` (VAULT_DOCUMENTATION)
- **Source repo:** READ-ONLY — ไม่มีการแก้ไข `D:\lumina-studio` (pre-existing dirty `.serena/project.yml` คงเดิม บันทึกเพื่อความโปร่งใส)

### Source repo truth (fresh, 2026-08-11)
- Path/root: `D:\lumina-studio` (`git rev-parse --show-toplevel`)
- Branch: `main`
- HEAD: `e98c9f627c50830c74cf76956abb15770690702d` (short `e98c9f6`)
- Commits: 93
- Status: tracked dirty `.serena/project.yml` (pre-existing, not caused by this WO)
- Remote: `https://github.com/expellirmud-dot/LUMINA-Studio.git`
- Authority files (actual): `AGENTS.md`, `PROJECT_RULES.md`, `AI_HANDOFF.md`, `README.md`, `docs/CONTEXT_INDEX.md`, `LUMINA_CONFIG_SYSTEM.md`, `GEMINI.md`, `IDEA.md`
- Current work state: `AI_HANDOFF.md` → Overall Status **PASSED / READY FOR DEPLOY**; active task `TASK-030` COMPLETE; "Await owner's instruction"
- Production URL: `https://lumina-studio-iota-ten.vercel.app`

### Files changed (Allowed Files only)
- `01 Projects/lumina-studio.md` (new — Project Overview)
- `01 Projects/Project Registry.md` (DIS→IMP, evidence refresh)
- `01 Projects/Project Index.md` (แถวใหม่)
- `00 Dashboard/Project Dashboard.md` (ย้ายเข้า Imported Projects)
- `04 Work Orders/CURRENT_WORK_ORDER.md` (pointer → WO-026 CLOSED)
- `04 Work Orders/WO-OBSIDIAN-026-ONBOARD-LUMINA-STUDIO.md` (closeout)

### Validation results (WO §10)
1. ✅ exact source root resolved
2. ✅ git status/branch/HEAD captured
3. ✅ authority files identified from actual repo
4. ✅ Project Overview มีครบทุกหัวข้อ AGENTS.md
5. ✅ ไม่มี unsupported current-status claims (lifecycle = UNK, ไม่ infer)
6. ✅ Registry import transition ถูกต้อง (DIS→IMP)
7. ✅ Dashboard ไม่แสดง lumina-studio ใน Discovered — Not Imported อีกต่อไป
8. ✅ wikilinks ทั้งหมด resolve ([[lumina-studio]], [[Project Registry]], [[Project Index]], [[Project Dashboard]])
9. ✅ source repo unchanged (นอกเหนือจาก pre-existing dirty `.serena/project.yml`)
10. ✅ diff เฉพาะ Allowed Files
11. ✅ owner notes ยังคง untouched
12. ✅ diff summary ก่อน commit

### Evidence classification
- verified: repo truth 2026-08-11 (structure, HEAD, status, authority files, deploy status, task state)
- needs-verification: ไม่มีประเด็นค้างในรอบนี้ (production URL ระบุใน AI_HANDOFF.md = verified)

### Unresolved / needs-verification
- Pre-existing dirty `.serena/project.yml` ใน source repo — ไม่เกี่ยวข้องกับ Vault onboarding (บันทึก)
- Hero FROZEN — การปรับ hero ต้อง owner อนุมัติ (ข้อจำกัดโดยเจตนา จาก PROJECT_RULES.md)
- Lifecycle state เจตนาปล่อย `unknown` (ไม่ infer)
- หากขยายนอก Phase 1 ต้องเข้า ROADMAP.md

### Recommended next Work Order
`WO-OBSIDIAN-027 — Onboard lightroom-ai-exposure` (ตามลำดับที่ Owner กำหนด)
