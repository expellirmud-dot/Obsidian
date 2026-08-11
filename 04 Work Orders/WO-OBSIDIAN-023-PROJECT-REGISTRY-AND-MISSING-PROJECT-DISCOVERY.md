# WORK ORDER — PROJECT REGISTRY AND MISSING PROJECT DISCOVERY

Work Order ID: WO-OBSIDIAN-023
Title: สร้าง Project Registry และค้นหาโปรเจกต์ที่ยังไม่ได้ถูกนำเข้า Vault
Risk Level: LOW
Task Classification: Documentation / Repository Inventory / Knowledge Base Governance
Execution Mode: Bounded Single Work Order
Owner: Toto
Target Vault: `D:\Obsidian\Project-Knowledge-Vault`
Status: PLANNED

---

## 1. Objective

ทำให้ Project Knowledge Vault มีรายการโปรเจกต์ที่เชื่อถือได้และมองเห็นโปรเจกต์ที่ยังไม่ได้ถูกนำเข้า โดยไม่ถือว่าไฟล์ที่มีอยู่ใน `01 Projects` คือ inventory ทั้งหมดโดยอัตโนมัติ

งานนี้ต้องสร้างกลไก Registry ระดับ Vault ที่แยกอย่างชัดเจนระหว่าง:

- โปรเจกต์ที่นำเข้า Vault แล้ว
- โปรเจกต์ที่ค้นพบแต่ยังไม่ได้นำเข้า
- โปรเจกต์ที่หยุดชั่วคราว
- โปรเจกต์ที่ archived / retired
- โปรเจกต์ที่ยังไม่สามารถยืนยันสถานะได้

เป้าหมายของ WO นี้คือสร้างฐานข้อมูลเชิงเอกสารสำหรับงาน Live Project Wall ในอนาคต ไม่ใช่สร้างระบบ real-time monitoring ในรอบนี้

---

## 2. Repository Authority

Vault repository:

`expellirmud-dot/Obsidian`

Local Vault:

`D:\Obsidian\Project-Knowledge-Vault`

Default branch:

`main`

Authority order:

1. Source repository และไฟล์จริงของแต่ละโปรเจกต์
2. Current Work Order / Current Task Pointer ของ source repository
3. Authority documentation ภายใน source repository
4. Project Registry และ Project Overview ใน Vault
5. Conversation / memory

Vault ห้ามยกระดับข้อมูลที่ยังไม่ได้ตรวจเป็น verified

---

## 3. Mandatory Read First

ก่อนแก้ไฟล์ ให้ปฏิบัติตาม `.agents/skills/project-read-first/SKILL.md` และอ่านอย่างน้อย:

1. `AGENTS.md`
2. `README.md`
3. `00 Dashboard/Project Dashboard.md`
4. `01 Projects/Project Index.md`
5. `04 Work Orders/CURRENT_WORK_ORDER.md`
6. `.agents/skills/project-context-discovery/SKILL.md`
7. Project Overview ที่มีอยู่ทั้งหมดใน `01 Projects`

ต้องผลิต `READ_FIRST_PREFLIGHT` และเริ่มแก้ไฟล์ได้เมื่อ `PREFLIGHT_DECISION: READY` เท่านั้น

---

## 4. Required Outcome

เมื่อ WO นี้เสร็จ ต้องมีผลลัพธ์ขั้นต่ำดังนี้:

### A. Project Registry

สร้างไฟล์:

`01 Projects/Project Registry.md`

Registry ต้องเป็น inventory กลางของโปรเจกต์ที่ Vault รู้จัก และต้องมีอย่างน้อยฟิลด์เชิงแนวคิดต่อไปนี้ต่อหนึ่งโปรเจกต์:

- Project Name
- Repository / Source Location
- Import State
- Lifecycle State
- Verification State
- Last Verified
- Project Note
- Notes / Evidence

ค่าของ `Import State` อย่างน้อยต้องรองรับ:

- `imported`
- `discovered-not-imported`
- `unknown`

ค่าของ `Lifecycle State` อย่างน้อยต้องรองรับ:

- `active`
- `paused`
- `archived`
- `unknown`

ค่าของ `Verification State` อย่างน้อยต้องรองรับ:

- `verified`
- `owner-confirmed`
- `needs-verification`

ห้ามสร้างสถานะจากการคาดเดา

### B. Missing Project Discovery

ตรวจ inventory ของ source repositories / project locations ที่ Owner เข้าถึงได้ และเทียบกับ Project Overview ปัจจุบันใน Vault

ต้องจำแนกผลอย่างน้อยเป็น:

1. Already Imported
2. Discovered — Not Imported
3. Paused / Archived
4. Needs Verification

Source repositories ที่ตรวจต้องเป็น read-only

หากไม่สามารถ enumerate repository ทั้งหมดได้ ให้รายงานข้อจำกัดและเก็บรายการที่พบเป็น `needs-verification` แทนการเดา

### C. Dashboard Integration

ปรับ `00 Dashboard/Project Dashboard.md` ให้มีส่วนที่แสดงอย่างน้อย:

- Imported Projects
- Discovered — Not Imported
- Paused / Archived
- Needs Verification

Dashboard ต้องอ้างอิง Registry เป็น inventory หลัก ไม่ถือว่ารายชื่อ Project Overview ปัจจุบันครบถ้วนโดยปริยาย

### D. Project Index Integration

ปรับ `01 Projects/Project Index.md` ให้เชื่อมไปยัง `Project Registry.md` และอธิบายความแตกต่างระหว่าง:

- Registry = รายการโปรเจกต์ที่ Vault รู้จัก
- Project Overview = เอกสารเชิงบริบทของโปรเจกต์ที่นำเข้าแล้ว

---

## 5. Existing Imported Baseline

จาก Vault ปัจจุบัน มี Project Overview ที่ทราบแล้วอย่างน้อย:

- llm-agents
- STT Typing
- AI Worker Harness
- Utility Disbursement App
- Adobe Stock Upload Assistant

รายการนี้เป็นเพียง baseline ของ Vault ปัจจุบัน ไม่ใช่ข้อพิสูจน์ว่า inventory ทั้งหมดมีเพียง 5 โปรเจกต์

ต้องตรวจ Repo truth ก่อนสรุปสถานะปัจจุบันของแต่ละโปรเจกต์

---

## 6. Hard Boundaries

ห้ามทำสิ่งต่อไปนี้:

1. ห้ามแก้ Source Code ของโปรเจกต์ภายนอก Vault
2. ห้าม commit / push ไปยัง source repositories ภายนอก
3. ห้ามสร้าง Project Overview เต็มรูปแบบให้ทุก discovered project โดยอัตโนมัติใน WO นี้
4. ห้ามทำ Live Project Wall, webhook, polling daemon หรือ background service ใน WO นี้
5. ห้ามติดตั้ง Obsidian Community Plugin
6. ห้ามแก้ `.obsidian/`
7. ห้ามเก็บ Secret, Token, Password, Cookie หรือ Credential
8. ห้ามลบ Project Overview หรือประวัติเดิม
9. ห้ามเปลี่ยน lifecycle state เป็น `active`, `paused`, `archived` จาก inference เพียงอย่างเดียว
10. ห้ามเปลี่ยน `04 Work Orders/CURRENT_WORK_ORDER.md` เว้นแต่ Owner อนุญาตให้ activate WO-OBSIDIAN-023 แยกต่างหาก

---

## 7. Allowed Files

อนุญาตให้แก้เฉพาะไฟล์ต่อไปนี้:

- `01 Projects/Project Registry.md` (new)
- `01 Projects/Project Index.md`
- `00 Dashboard/Project Dashboard.md`
- `04 Work Orders/WO-OBSIDIAN-023-PROJECT-REGISTRY-AND-MISSING-PROJECT-DISCOVERY.md` เฉพาะการอัปเดตสถานะ/หลักฐาน closeout เมื่อจบงาน

หากจำเป็นต้องแก้ไฟล์อื่น ให้ STOP และรายงานเหตุผลก่อน

---

## 8. Discovery Rules

การค้นหาโปรเจกต์ต้องแยก Evidence Classification:

### verified

มีหลักฐานจาก repository / file / command output ในรอบปัจจุบัน

### owner-confirmed

Owner ยืนยันโดยตรง แต่ยังไม่ได้ตรวจ source truth ในรอบนี้

### needs-verification

พบชื่อหรือ path แต่ยังไม่มีหลักฐานเพียงพอ

ห้ามใช้คำว่า verified หากตรวจเพียงข้อมูลใน Vault เดิม

---

## 9. Design Constraint for Future Live Wall

Registry ที่สร้างใน WO นี้ต้องไม่ผูกกับโครงสร้าง source repository แบบเดียวกันทั้งหมด

ต้องรองรับแนวคิดว่าแต่ละโปรเจกต์อาจมี authority files ต่างกัน เช่น:

- `.tasks/CURRENT_TASK.md`
- `WORK_ORDER.md`
- `04 Work Orders/CURRENT_WORK_ORDER.md`
- `AGENTS.md`
- roadmap / readiness docs
- GitHub PR / CI state

Registry ต้องเก็บ identity และ evidence classification โดยไม่บังคับ source repo ให้เปลี่ยนโครงสร้าง

การทำ adapter / normalized runtime state / automatic synchronization เป็นงานอนาคต แยกจาก WO นี้

---

## 10. Validation

ก่อนปิดงาน ต้องตรวจอย่างน้อย:

1. `git status --short`
2. ตรวจว่าแก้เฉพาะ Allowed Files
3. เปิด `Project Registry.md` และตรวจว่าทุก entry มี Import State + Lifecycle State + Verification State
4. ตรวจว่า Dashboard แสดง imported และ not-imported แยกกัน
5. ตรวจว่า Project Index ลิงก์ไป Registry ได้
6. ตรวจว่า Obsidian wikilinks ที่เพิ่มใหม่ resolve ตามชื่อไฟล์จริง
7. ตรวจว่าไม่มี secret หรือข้อมูลส่วนบุคคลที่ไม่จำเป็น
8. ตรวจว่า source repositories ไม่มีการเปลี่ยนแปลงจากงานนี้
9. แสดง diff summary ก่อน commit

---

## 11. Definition of Done

WO-OBSIDIAN-023 ถือว่า DONE เมื่อครบทุกข้อ:

- [ ] Read-first preflight ผ่าน
- [ ] สร้าง `01 Projects/Project Registry.md`
- [ ] Registry แยก imported / discovered-not-imported / paused-archived / needs-verification ได้
- [ ] Inventory ไม่ถือว่า 5 Project Overview เดิมคือรายการทั้งหมดโดยอัตโนมัติ
- [ ] Dashboard อ้างอิง Registry และแสดง missing projects ได้
- [ ] Project Index เชื่อม Registry
- [ ] ไม่มีการแก้ source repository ภายนอก
- [ ] ไม่มี Live Wall automation / webhook / polling ถูกเพิ่มใน WO นี้
- [ ] Validation ผ่าน
- [ ] Diff อยู่ใน Allowed Files เท่านั้น
- [ ] Final report ระบุ verified evidence, unresolved items และข้อเสนอ next step

---

## 12. Commit / Push Policy

Worker สามารถเตรียม diff และ validation ได้ตาม Work Order

ก่อน commit ต้องตรวจว่า working tree ไม่มี unrelated changes

หาก execution environment มี Owner authorization สำหรับ commit อยู่แล้ว ให้ commit ได้หนึ่งครั้งสำหรับ WO นี้โดย stage เฉพาะ Allowed Files

ห้าม push เว้นแต่ Owner อนุญาตอย่างชัดเจนใน execution session นั้น

Suggested commit message:

`docs: add project registry and missing project discovery`

---

## 13. Expected Closeout Report

รายงานปิดงานต้องมี:

- จำนวนโปรเจกต์ที่พบทั้งหมด
- จำนวน `imported`
- จำนวน `discovered-not-imported`
- จำนวน `paused / archived`
- จำนวน `needs-verification`
- รายชื่อ discovered projects ที่ยังไม่ได้ onboard
- ไฟล์ที่แก้
- Validation performed
- Git status
- Remaining risks / unknowns
- Recommended next Work Order

Recommended next step หลัง WO นี้สำเร็จ:

`Import Missing Projects` ก่อนเริ่มงาน `Live Project State / Project Wall Automation`
