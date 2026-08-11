# WORK ORDER — ONBOARD LIGHTROOM-AI-EXPOSURE

Work Order ID: WO-OBSIDIAN-027
Title: WO-OBSIDIAN-027 — Onboard lightroom-ai-exposure
Risk Level: LOW
Task Classification: Documentation / Project Onboarding / Knowledge Base Governance
Execution Mode: Bounded Single Work Order
Owner: Toto
Target Vault: `D:\Obsidian\Project-Knowledge-Vault`
Status: PLANNED

> ใบงานนี้เป็น **draft PLANNED เท่านั้น** — ยังไม่ Activate และห้าม execute ในรอบที่สร้างไฟล์นี้
> การ Activate + Execute ต้องรอ Owner สั่งแยกต่างหาก

---

## 1. Objective

Onboard โปรเจกต์ `lightroom-ai-exposure` ที่ผ่าน recommendation gate จาก WO-OBSIDIAN-024 (Triage Class = `project`, Evidence = `verified`) เข้าสู่ Project Knowledge Vault เป็นโปรเจกต์เดียวที่ bounded หนึ่งงาน โดยใช้ repository truth ปัจจุบัน และรักษาโมเดล authority ของ Vault

ลำดับ onboarding ทีละโปรเจกต์: `thai_stt_app` (WO-025 ✅) → `lumina-studio` (WO-026 ✅) → **`lightroom-ai-exposure` (WO-027)** → `citizen_portal` → `TalkToClibord` → `AI-Workspace`

---

## 2. Repository Authority

Vault repository: `expellirmud-dot/Obsidian`
Local Vault: `D:\Obsidian\Project-Knowledge-Vault`
Default branch: `main`

Source repository (READ-ONLY ในรอบ execute):
- Local: `D:\lightroom-ai-exposure`
- GitHub: `expellirmud-dot/Lightroom-AI-Workflow-` (remote จาก WO-024 evidence: `expellirmud-dot/Lightroom-AI-Workflow-.git`, branch `main`, 96 commits)

Authority order:

1. Source repository (`D:\lightroom-ai-exposure`) และไฟล์จริง
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

`01 Projects/lightroom-ai-exposure.md`

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
- เพิ่มแถว `[[lightroom-ai-exposure]]` ในตาราง (พร้อม Description / Local Path / Status / Last Verified)
- ลิงก์กลับ `[[Project Dashboard]]`

### 6.3 Project Dashboard
- ย้าย `lightroom-ai-exposure` จากหมวด **Discovered — Not Imported** ไป **Imported Projects**
- ห้ามออกแบบ dashboard ใหม่ — แก้เฉพาะจุดที่ต้องย้าย

---

## 7. Architecture Handling

ห้ามสร้าง Architecture document ใหม่อัตโนมัติ เว้นแต่กฎ/template ของ Vault ต้องการ และมี source evidence เพียงพอ
หากสถาปัตยกรรมอยู่นอกขอบเขต:
- สรุปสถาปัตยกรรมแบบย่อใน Project Overview
- บันทึกเป็น follow-up (ไม่สร้างไฟล์ ARCH- ในรอบนี้)

---

## 8. Hard Boundaries

1. ห้ามแก้ Source Code ของ `D:\lightroom-ai-exposure`
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
13. ห้ามเปลี่ยน `04 Work Orders/CURRENT_WORK_ORDER.md` เว้นแต่ Owner อนุญาตให้ activate WO-027 แยกต่างหาก
14. ห้ามแก้ `01 Projects/STT Typing.md` (pre-existing CRLF artifact — out-of-scope)
15. ห้ามแก้ owner notes (untracked: `2026-08-11.md`, `ยังไม่ได้ตั้งชื่อ.canvas`)

---

## 9. Allowed Files (future execution)

อนุญาตให้แก้เฉพาะ:

- `01 Projects/lightroom-ai-exposure.md` (new — Project Overview)
- `01 Projects/Project Registry.md` (import transition + refresh evidence)
- `01 Projects/Project Index.md` (เพิ่มแถว)
- `00 Dashboard/Project Dashboard.md` (ย้ายเข้า Imported Projects)
- `04 Work Orders/CURRENT_WORK_ORDER.md` (เปิด pointer → WO-027 ACTIVE, ปิด → CLOSED ให้ครบ proof chain)
- `04 Work Orders/WO-OBSIDIAN-027-ONBOARD-LIGHTROOM-AI-EXPOSURE.md` เฉพาะการอัปเดตสถานะ/หลักฐาน closeout เมื่อจบงาน

หากจำเป็นต้องแก้ไฟล์อื่น ให้ STOP และรายงานเหตุผลก่อน

---

## 10. Validation (future execution)

ก่อนปิดงาน ต้องตรวจอย่างน้อย:

1. exact source repo path/root ถูก resolve (`D:\lightroom-ai-exposure`, `git rev-parse --show-toplevel`)
2. source git status / branch / HEAD ถูกจับได้ (`git status --short`, `git branch --show-current`, `git rev-parse HEAD`)
3. source authority files ถูกระบุจาก repo จริง (ไม่ใช่เดา)
4. Project Overview มีครบทุกหัวข้อที่ AGENTS.md กำหนด
5. ไม่มีการอ้างสถานะปัจจุบันที่ไม่มีหลักฐาน
6. Registry import transition ถูกต้อง (`discovered-not-imported` → `imported`)
7. Dashboard ไม่แสดง `lightroom-ai-exposure` ใน Discovered — Not Imported อีกต่อไป
8. wikilinks ทั้งหมด resolve ตามชื่อไฟล์จริง
9. source repo ไม่มีการเปลี่ยนแปลง (READ-ONLY enforced)
10. diff แตะเฉพาะ Allowed Files
11. pre-existing `STT Typing.md` CRLF artifact ยังคง out-of-scope (ไม่ถูก stage/commit)
12. owner notes ยังคง untouched
13. แสดง diff summary ก่อน commit

---

## 11. Definition of Done (future execution)

WO-OBSIDIAN-027 ถือว่า DONE เมื่อครบทุกข้อ:

- [ ] Read-first preflight ผ่าน (`READY`)
- [ ] มี Project Overview เดียวที่ verified สำหรับ `lightroom-ai-exposure`
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
- **สำหรับการสร้างใบงาน (draft) นี้:** commit ได้หนึ่งครั้งเพื่อสร้างเอกสาร WO-027 เท่านั้น stage เฉพาะไฟล์ WO-027
- **สำหรับการ execute onboarding ในอนาคต:** commit/push ต้องมี Owner authorization แยกในรอบนั้น
- ห้าม push เว้นแต่ Owner อนุญาตชัดเจน

Suggested commit message (draft creation):

`docs: add WO-OBSIDIAN-027 onboard lightroom-ai-exposure (planned)`

---

## 13. Expected Closeout Report (future execution)

- Source repo path + HEAD + branch + status
- Authority files ที่พบ
- รายชื่อไฟล์ที่แก้
- Validation performed
- Git status (รวม owner notes + STT Typing.md artifact)
- Evidence classification summary
- Remaining risks / unknowns
- Recommended next Work Order (onboard `citizen_portal`)
