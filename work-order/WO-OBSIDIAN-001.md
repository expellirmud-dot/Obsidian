````markdown
# WORK ORDER — OBSIDIAN PROJECT KNOWLEDGE VAULT INITIAL SETUP

Work Order ID: WO-OBSIDIAN-001
Title: เตรียมโครงสร้างคลังความรู้และชุดหน้าโปรเจกต์เริ่มต้น
Risk Level: LOW
Task Classification: Documentation / Knowledge Base Setup
Execution Mode: Bounded Single Work Order
Owner: Toto
Target Vault: D:\Obsidian\Project-Knowledge-Vault

---
## Repository Authority

Local Vault:
`D:\Obsidian\Project-Knowledge-Vault`

GitHub Repository:
`expellirmud-dot/Project-Knowledge-Vault`

Default Branch:
`main`

Execution policy:

- ทำงานเฉพาะภายใน Local Vault
- ตรวจ Git status ก่อนเริ่ม
- สร้างและตรวจสอบไฟล์ตาม Work Order
- Stage เฉพาะไฟล์ของ WO-OBSIDIAN-001
- Commit ได้หนึ่งครั้งเมื่อ Validation ผ่าน
- ห้าม Push จนกว่า Owner จะตรวจรายงานและอนุญาต
## 1. Objective

จัดเตรียม Obsidian Vault ให้เป็นคลังความรู้กลางสำหรับเก็บข้อมูลโปรเจกต์ทั้งหมด เพื่อให้มนุษย์และ AI สามารถกลับมาอ่านบริบทเดิมและทำงานต่อได้ โดยไม่ต้องพึ่งความจำหรือประวัติแชทเพียงอย่างเดียว

Vault นี้มีหน้าที่เก็บ:

- ภาพรวมของแต่ละโปรเจกต์
- จุดประสงค์และขอบเขต
- ตำแหน่ง Source Code และ Repository
- สถาปัตยกรรมระดับภาพรวม
- การตัดสินใจสำคัญ
- บทเรียนและปัญหาที่เคยพบ
- Resume Context สำหรับเริ่มแชทหรือเริ่มงานรอบใหม่
- ลิงก์ไปยัง Work Order และเอกสารที่เกี่ยวข้อง

Vault นี้ไม่ใช่แหล่งความจริงของ Source Code หรือสถานะ Runtime

ลำดับแหล่งความจริง:

1. Git repository และไฟล์จริงในโปรเจกต์
2. Current Work Order ของโปรเจกต์
3. Obsidian Project Knowledge Vault
4. Conversation หรือความจำของ AI

---

## 2. Hard Boundaries

AI ต้องปฏิบัติตามข้อจำกัดต่อไปนี้:

1. ทำงานเฉพาะภายใน:

   `D:\Obsidian\Project-Knowledge-Vault`

2. ห้ามแก้ Source Code ในโปรเจกต์ภายนอก Vault

3. ห้ามแก้หรือลบไฟล์ใน:

   - `D:\llm-agents`
   - `D:\stt_typing`
   - `D:\ai-tools\ai-worker-harness`
   - `D:\utility-disbursement-app`
   - `D:\adobe-stock-upload`

4. ห้ามติดตั้ง Community Plugin

5. ห้ามแก้ `.obsidian` เว้นแต่ Work Order ระบุไว้โดยตรง

6. ห้ามย้าย เปลี่ยนชื่อ หรือลบโน้ตเดิมที่ผู้ใช้สร้างไว้

7. ห้ามสร้างข้อมูลสถานะโปรเจกต์จากการคาดเดา

8. ข้อมูลที่ยังไม่ได้ตรวจสอบต้องใช้สถานะ:

   `needs-verification`

9. ห้ามคัดลอก Source Code จำนวนมากเข้ามาใน Vault

10. ห้าม Commit หรือ Push เว้นแต่ Vault เป็น Git repository อยู่แล้วและ Owner อนุญาตไว้ชัดเจน

---

## 3. Read First

ก่อนแก้ไข ให้ตรวจสอบตามลำดับ:

1. ยืนยันว่า Vault path มีอยู่จริง
2. แสดงรายการไฟล์และโฟลเดอร์ระดับบนสุดของ Vault
3. อ่าน `AGENTS.md` หากมีอยู่แล้ว
4. อ่าน `README.md` หากมีอยู่แล้ว
5. อ่าน `00 Dashboard/Project Dashboard.md` หากมีอยู่แล้ว
6. ตรวจหาไฟล์ชื่อเดียวกับไฟล์ที่จะสร้าง
7. ป้องกันการเขียนทับข้อมูลเดิม

หากพบไฟล์เดิม:

- ให้แก้เฉพาะส่วนที่เกี่ยวข้อง
- รักษาข้อมูลของผู้ใช้
- ห้ามแทนที่ไฟล์ทั้งฉบับโดยไม่จำเป็น
- รายงานความขัดแย้งก่อนดำเนินการ หากไม่สามารถรวมข้อมูลอย่างปลอดภัยได้

---

## 4. Required Directory Structure

สร้างเฉพาะโฟลเดอร์ที่ยังไม่มี:

```text
Project-Knowledge-Vault
│
├── AGENTS.md
├── README.md
│
├── 00 Dashboard
│   └── Project Dashboard.md
│
├── 01 Projects
│   ├── Project Index.md
│   ├── llm-agents.md
│   ├── STT Typing.md
│   ├── AI Worker Harness.md
│   ├── Utility Disbursement App.md
│   └── Adobe Stock Upload Assistant.md
│
├── 02 Architecture
│   └── Architecture Index.md
│
├── 03 Decisions
│   └── Decision Index.md
│
├── 04 Work Orders
│   └── Work Order Index.md
│
├── 05 Lessons Learned
│   └── Lessons Learned Index.md
│
├── 06 Prompts
│   ├── Prompt Index.md
│   └── Templates
│       ├── Project Template.md
│       ├── Decision Template.md
│       ├── Lesson Learned Template.md
│       └── Resume Context Template.md
│
├── 07 Attachments
│
└── 99 Archive
    └── Archive Index.md
````

ห้ามสร้างไฟล์ว่างโดยไม่มีหัวข้อหรือคำอธิบายหน้าที่ของไฟล์

---

## 5. AGENTS.md Requirements

สร้างไฟล์:

`AGENTS.md`

ไฟล์นี้เป็นกฎระดับ Vault และเป็นไฟล์แรกที่ AI ต้องอ่านก่อนทำงานใน Vault

เนื้อหาต้องมีหัวข้อต่อไปนี้:

```markdown
# AGENTS.md

## Purpose

Obsidian Vault นี้เป็นคลังความรู้กลางของโปรเจกต์ ใช้เก็บภาพรวม บริบท การตัดสินใจ บทเรียน และข้อมูลสำหรับกลับมาทำงานต่อ

Vault ไม่ใช่แหล่งความจริงแทน Git repository หรือ Current Work Order

## Authority Order

เมื่อข้อมูลขัดแย้งกัน ให้ยึดตามลำดับ:

1. Git repository และไฟล์จริงของโปรเจกต์
2. Current Work Order หรือ Current Task Pointer
3. เอกสาร Authority ภายใน Repository
4. Obsidian Project Knowledge Vault
5. Worker Report
6. Conversation และความจำของ AI

## Mandatory Read First

ก่อนแก้ไขข้อมูลโปรเจกต์ใด ให้ AI อ่าน:

1. `AGENTS.md`
2. `README.md`
3. `00 Dashboard/Project Dashboard.md`
4. หน้า Project Overview ที่เกี่ยวข้อง
5. Resume Context ของโปรเจกต์
6. เอกสารที่ถูกลิงก์ว่าเป็น Authority
7. Current Work Order จาก Repository จริง เมื่อเข้าถึงได้

---

# Seven Execution Rules

## 1. Task Classification

ระบุประเภทงานก่อนเริ่ม เช่น Documentation, Research, Planning, Code Change, Validation หรือ Destructive Operation

ระดับความเสี่ยงและวิธีตรวจสอบต้องเหมาะกับประเภทงาน

## 2. Define Done First

กำหนด Definition of Done ก่อนแก้ไขไฟล์

ห้ามเริ่มงานโดยไม่มีเงื่อนไขว่างานสำเร็จเมื่อใด

## 3. Parallel Evidence Gathering

รวบรวมหลักฐานจากแหล่งที่เกี่ยวข้องก่อนตัดสินใจ

สามารถตรวจหลายแหล่งพร้อมกันได้ แต่ต้องไม่แก้หลายขอบเขตพร้อมกันโดยไม่มีเหตุผล

## 4. Single Recommendation

เมื่อมีข้อมูลเพียงพอ ให้เลือกข้อเสนอหลักเพียงข้อเดียว

ห้ามโยนตัวเลือกจำนวนมากกลับให้ Owner ตัดสินใจแทน ในกรณีที่ AI สามารถตัดสินใจภายในขอบเขตได้เอง

## 5. Surgical Change

แก้เฉพาะสิ่งที่จำเป็นต่อเป้าหมาย

ห้ามปรับโครงสร้าง ขยายขอบเขต หรือแก้ไฟล์ที่ไม่เกี่ยวข้องโดยพลการ

## 6. Verify by Execution

ห้ามสรุปว่างานสำเร็จจากการอ่านข้อความหรือ Worker Report เพียงอย่างเดียว

ต้องตรวจไฟล์จริง ลิงก์จริง โครงสร้างจริง หรือรัน Validation ที่เกี่ยวข้อง

## 7. Outcome-First Reporting

รายงานผลลัพธ์ก่อนรายละเอียดกระบวนการ

รายงานว่าทำสำเร็จหรือไม่ หลักฐานคืออะไร มีข้อจำกัดหรือความเสี่ยงใดเหลืออยู่ และขั้นตอนถัดไปคืออะไร

---

# Four Common AI Failure Modes

## 1. Memory Over Repository Truth

AI มักเชื่อความจำ บริบทเก่า หรือบทสนทนา มากกว่าไฟล์จริง

กฎบังคับ:

> Repo truth มาก่อนความจำเสมอ

## 2. Treating Worker Reports as Final Evidence

AI มักถือว่า Worker บอกว่าเสร็จแล้ว เท่ากับงานเสร็จจริง

กฎบังคับ:

> Worker Report เป็นข้อมูลประกอบ ไม่ใช่หลักฐานสุดท้าย  
> Controller หรือผู้ตรวจต้องตรวจไฟล์และผล Validation ด้วยตนเอง

## 3. Leaving the Proof Chain Open

AI มักแก้ไฟล์แล้วจบ โดยไม่ตรวจว่าหลักฐานครบหรือสถานะถูกปิดจริงหรือไม่

กฎบังคับ:

> งานที่เสร็จต้องปิด Proof Chain ตั้งแต่ Input → Change → Validation → Evidence → Final Status

## 4. Unauthorized Scope Expansion

AI มักเห็นสิ่งอื่นที่ปรับปรุงได้แล้วขยายงานเอง

กฎบังคับ:

> ห้ามขยายขอบเขตเอง  
> สิ่งที่อยู่นอก Work Order ให้บันทึกเป็นข้อเสนอหรือ Follow-up เท่านั้น

---

## Project Knowledge Rules

1. ทุกโปรเจกต์ต้องมีหน้า Project Overview
2. ทุกหน้าโปรเจกต์ต้องมีวันที่ตรวจสอบล่าสุด
3. ข้อมูลสถานะที่ไม่ได้ตรวจจาก Repository ต้องระบุ `needs-verification`
4. ห้ามเขียนสถานะปัจจุบันจากความจำของ AI
5. ห้ามเก็บ Secret, Token, Password หรือ Credential
6. Source Code ต้องอยู่ใน Repository เดิม
7. Vault เก็บเฉพาะ Summary, Decisions, Context, Links และ Lessons
8. เมื่อเปลี่ยนชื่อโน้ต ต้องรักษาลิงก์ภายใน
9. ห้ามลบประวัติการตัดสินใจเพียงเพราะมีการตัดสินใจใหม่
10. เอกสารเก่าให้ย้ายไป `99 Archive` โดยไม่ลบหลักฐานเดิม

## Required Project Page Sections

ทุกหน้า Project Overview ต้องมี:

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

## Safety

ห้ามบันทึก:

- Password
- API Key
- Access Token
- Session Cookie
- Private Credential
- ข้อมูลส่วนบุคคลที่ไม่จำเป็น
- Source Code จำนวนมากที่ซ้ำกับ Repository
```

---

## 6. README.md Requirements

สร้าง `README.md` เพื่ออธิบายการใช้ Vault โดยต้องมี:

* Vault นี้ใช้ทำอะไร
* ความแตกต่างระหว่าง Vault กับ Git repository
* โครงสร้างโฟลเดอร์
* วิธีเพิ่มโปรเจกต์ใหม่
* วิธีอัปเดต Resume Context
* วิธีเริ่มงานรอบใหม่
* วิธีจัดเก็บเอกสารเก่า
* คำเตือนเรื่อง Secret และข้อมูลส่วนบุคคล

ต้องมีข้อความนี้:

```markdown
> Obsidian เป็นแหล่งความรู้และบริบทระยะยาว  
> Git repository และ Current Work Order เป็นแหล่งความจริงของงาน
```

---

## 7. Project Dashboard Requirements

สร้าง:

`00 Dashboard/Project Dashboard.md`

ต้องประกอบด้วย:

```markdown
---
type: dashboard
last_reviewed: YYYY-MM-DD
---

# Project Dashboard

## Active Projects

- [[llm-agents]]
- [[STT Typing]]
- [[AI Worker Harness]]
- [[Utility Disbursement App]]
- [[Adobe Stock Upload Assistant]]

## Needs Verification

แสดงรายการโปรเจกต์ที่สถานะยังไม่ได้ตรวจสอบจาก Repository จริง

## Recently Reviewed

แสดงชื่อโปรเจกต์และวันที่ตรวจสอบล่าสุด

## Paused Projects

ยังไม่กำหนด จนกว่าจะมีหลักฐานจาก Owner หรือ Repository

## Completed Projects

ยังไม่กำหนด จนกว่าจะมีหลักฐานจาก Owner หรือ Repository

## How to Resume Work

1. เปิดหน้าโปรเจกต์
2. อ่าน Resume Context
3. ตรวจ Repository truth
4. ตรวจ Current Work Order
5. อัปเดตข้อมูลที่ล้าสมัย
6. เริ่มงานตาม Work Order ใหม่
```

ห้ามระบุว่าโปรเจกต์ใด Active, Paused หรือ Completed จากการคาดเดา

รายชื่อด้านบนหมายถึง “โปรเจกต์ที่อยู่ในคลัง” ไม่ใช่การยืนยันสถานะ Runtime

---

## 8. Project Index Requirements

สร้าง:

`01 Projects/Project Index.md`

เนื้อหาต้องมีตาราง:

| Project | Description | Local Path | Status | Last Verified |
| ------- | ----------- | ---------- | ------ | ------------- |

เพิ่มโปรเจกต์เริ่มต้น:

1. llm-agents
2. STT Typing
3. AI Worker Harness
4. Utility Disbursement App
5. Adobe Stock Upload Assistant

กำหนดสถานะเริ่มต้นทั้งหมดเป็น:

`needs-verification`

ยกเว้นมีหลักฐานจาก Repository จริงที่ตรวจสอบในรอบนี้

---

## 9. Initial Project Pages

สร้างหน้าโปรเจกต์ทั้งห้าจาก `Project Template.md`

### 9.1 llm-agents

Known local path:

`D:\llm-agents`

คำอธิบายเริ่มต้น:

ระบบสำหรับควบคุมและดำเนินงาน AI Agent โดยแยกบทบาท Controller, Worker, Validation และ Runtime Execution ออกจากกัน

### 9.2 STT Typing

Known local path:

`D:\stt_typing`

คำอธิบายเริ่มต้น:

ระบบช่วยพิมพ์ข้อความและสั่งงานด้วยเสียง โดยเน้น Offline-First, Focus Guard และการควบคุม Runtime อย่างปลอดภัย

### 9.3 AI Worker Harness

Known local path:

`D:\ai-tools\ai-worker-harness`

คำอธิบายเริ่มต้น:

ระบบ Harness สำหรับออก Work Order ควบคุม AI Worker ตรวจ Validation และเก็บหลักฐานการทำงาน

### 9.4 Utility Disbursement App

Known local path:

`D:\utility-disbursement-app`

คำอธิบายเริ่มต้น:

ระบบช่วยจัดการเอกสารและกระบวนการเบิกจ่ายค่าสาธารณูปโภค

### 9.5 Adobe Stock Upload Assistant

Known local path:

`D:\adobe-stock-upload`

คำอธิบายเริ่มต้น:

ระบบช่วยเตรียมภาพ Metadata หมวดหมู่ และกระบวนการอัปโหลดผลงานไปยัง Adobe Stock

สำหรับทุกโปรเจกต์:

* อย่าสรุปสถานะปัจจุบันจากคำอธิบายข้างต้น
* ใช้ `status: needs-verification`
* ใช้ `last_reviewed:` เป็นวันที่ดำเนินงาน
* ช่อง Repository ที่ยังไม่ยืนยันให้เว้นว่าง
* ช่อง Current Work Order ให้ระบุว่า `Not verified`
* ห้ามสแกนหรืออ่าน Source Code เชิงลึกใน Work Order นี้
* อนุญาตให้ตรวจเพียงว่า Local Path มีอยู่หรือไม่

---

## 10. Project Template

สร้าง:

`06 Prompts/Templates/Project Template.md`

เนื้อหา:

```markdown
---
type: project
status: needs-verification
priority: unassigned
project_path:
repository:
current_work_order:
last_reviewed:
---

# Project Name

> เอกสารนี้เป็นคลังบริบทและภาพรวม  
> สถานะจริงต้องตรวจจาก Git repository และ Current Work Order

## โปรเจกต์นี้คืออะไร

## ปัญหาที่ต้องการแก้

## เป้าหมายหลัก

## ขอบเขต

### In Scope

### Out of Scope

## ตำแหน่งไฟล์จริง

## Repository

## สถานะปัจจุบัน

Status: needs-verification

## สิ่งที่ทำเสร็จแล้ว

ยังไม่ได้ตรวจสอบ

## งานที่กำลังทำ

ยังไม่ได้ตรวจสอบ

## งานถัดไป

ยังไม่ได้กำหนดจาก Repository truth

## สถาปัตยกรรม

## การตัดสินใจสำคัญ

## ปัญหาและความเสี่ยง

## บทเรียนที่ได้

## เอกสารที่เกี่ยวข้อง

## Resume Context

สถานะล่าสุด: needs-verification  
งานปัจจุบัน: Not verified  
สิ่งที่ทำเสร็จแล้ว: Not verified  
สิ่งที่ห้ามทำซ้ำ: Not verified  
ปัญหาที่ยังค้าง: Not verified  
ขั้นตอนถัดไป: Verify repository truth  
ไฟล์ที่ต้องอ่านก่อน: Not verified  
วันที่ตรวจสอบล่าสุด:  

## Verification Record

- Repository checked:
- Git HEAD:
- Current Work Order checked:
- Verified by:
- Verification date:
```

---

## 11. Other Templates

### Decision Template

ต้องมี:

* Decision ID
* วันที่
* โปรเจกต์
* สถานะ
* บริบท
* ตัวเลือกที่พิจารณา
* การตัดสินใจ
* เหตุผล
* ผลกระทบ
* หลักฐาน
* วันที่ทบทวนครั้งถัดไป

### Lesson Learned Template

ต้องมี:

* เหตุการณ์
* สิ่งที่คาดไว้
* สิ่งที่เกิดขึ้นจริง
* สาเหตุ
* ผลกระทบ
* บทเรียน
* การป้องกันการเกิดซ้ำ
* หลักฐานที่เกี่ยวข้อง

### Resume Context Template

ต้องมี:

* Project
* Last verified date
* Repository path
* Git branch และ HEAD
* Current Work Order
* Completed work
* Current state
* Open risks
* Do not repeat
* Required reads
* Recommended next action
* Verification status

---

## 12. Index Files

สร้าง Index สำหรับ:

* Architecture
* Decisions
* Work Orders
* Lessons Learned
* Prompts
* Archive

แต่ละ Index ต้องอธิบาย:

* โฟลเดอร์นี้ใช้เก็บอะไร
* สิ่งใดควรเก็บ
* สิ่งใดไม่ควรเก็บ
* รูปแบบการตั้งชื่อไฟล์
* ลิงก์กลับไป `[[Project Dashboard]]`

---

## 13. Naming Rules

ใช้กฎต่อไปนี้:

```text
Project page:
<Project Name>.md

Architecture:
ARCH-<Project>-<Topic>.md

Decision:
ADR-<Project>-<Number>-<Title>.md

Work Order:
WO-<Project>-<Number>-<Title>.md

Lesson Learned:
LESSON-<Project>-<Number>-<Title>.md

Archive:
เก็บชื่อเดิมและเพิ่มวันที่เมื่อจำเป็น
```

ใช้ชื่อที่มนุษย์อ่านเข้าใจได้

ห้ามใช้ชื่อทั่วไป เช่น:

* `note.md`
* `new.md`
* `temp.md`
* `document.md`

---

## 14. Link Requirements

ตรวจให้แน่ใจว่า:

1. Dashboard ลิงก์ไปยังทุกหน้าโปรเจกต์

2. ทุกหน้าโปรเจกต์ลิงก์กลับไป `[[Project Dashboard]]`

3. ทุก Index ลิงก์กลับไป Dashboard

4. ลิงก์ภายในใช้รูปแบบ Obsidian:

   `[[Note Name]]`

5. ไม่มีลิงก์ไปยังโน้ตที่ไม่มีอยู่ ยกเว้นระบุว่าเป็น Placeholder อย่างชัดเจน

---

## 15. Definition of Done

งานสำเร็จเมื่อ:

1. โครงสร้างโฟลเดอร์ครบตาม Work Order
2. มี `AGENTS.md` และกฎครบถ้วน
3. Seven Execution Rules ครบทั้ง 7 ข้อ
4. Four Common AI Failure Modes ครบทั้ง 4 ข้อ
5. มี `README.md`
6. มี Project Dashboard
7. มี Project Index
8. มีหน้าโปรเจกต์เริ่มต้นครบ 5 โปรเจกต์
9. มี Template ครบ 4 แบบ
10. มี Index ของแต่ละหมวด
11. ไม่มีการเขียนทับข้อมูลเดิมโดยไม่จำเป็น
12. ไม่มี Secret หรือ Credential
13. ไม่มี Source Code ถูกคัดลอกเข้ามา
14. ลิงก์ภายในชี้ไปยังไฟล์ที่มีอยู่
15. ทุกสถานะที่ยังไม่ตรวจสอบใช้ `needs-verification`
16. ไม่ได้ติดตั้ง Plugin
17. ไม่ได้แก้ไข Source Repository ภายนอก Vault

---

## 16. Validation

หลังดำเนินงาน ให้ตรวจสอบอย่างน้อย:

### Structure Validation

* แสดงรายการ Directory Tree ของ Vault
* ยืนยันไฟล์ที่สร้างใหม่
* ยืนยันไฟล์เดิมที่แก้ไข
* ยืนยันว่าไม่มีไฟล์ภายนอก Vault ถูกแก้

### Content Validation

ค้นหาใน `AGENTS.md` และยืนยันว่ามี:

* Task Classification
* Define Done First
* Parallel Evidence Gathering
* Single Recommendation
* Surgical Change
* Verify by Execution
* Outcome-First Reporting
* Memory Over Repository Truth
* Treating Worker Reports as Final Evidence
* Leaving the Proof Chain Open
* Unauthorized Scope Expansion

### Link Validation

ตรวจ `[[...]]` ทุกลิงก์ในไฟล์ที่สร้าง และรายงาน:

* Total internal links
* Resolved links
* Unresolved links

Unresolved links ที่ไม่ได้ระบุว่าเป็น Placeholder ต้องเท่ากับศูนย์

### Safety Validation

ยืนยัน:

* Files changed outside Vault: 0
* Community plugins installed: 0
* Secrets added: 0
* Source files copied: 0

---

## 17. Stop Conditions

หยุดและรายงาน Owner ทันทีเมื่อ:

1. Vault path ไม่มีอยู่จริง
2. ไม่มีสิทธิ์เขียนไฟล์
3. พบ `AGENTS.md` เดิมที่มีกฎขัดแย้ง
4. พบโครงสร้างเดิมที่อาจเสียหายจากการรวม
5. ต้องลบหรือเปลี่ยนชื่อไฟล์เดิม
6. พบ Secret หรือ Credential ในไฟล์ที่จะต้องแก้
7. งานจำเป็นต้องออกนอก Vault
8. ไม่สามารถรักษาข้อมูลเดิมไว้ได้
9. พบความไม่แน่นอนที่อาจทำให้ข้อมูลโปรเจกต์ผิดจาก Repository truth

ห้ามใช้ Stop Condition กับเรื่องเล็กน้อยที่สามารถแก้ได้อย่างปลอดภัยภายใน Work Order

---

## 18. Final Report Format

รายงานผลตามรูปแบบนี้:

```text
WORK_ORDER: WO-OBSIDIAN-001
RESULT: COMPLETED | BLOCKED | PARTIAL

VAULT_PATH:
FILES_CREATED:
FILES_UPDATED:
FILES_DELETED:
DIRECTORIES_CREATED:

PROJECT_PAGES_CREATED:
TEMPLATES_CREATED:
INDEX_FILES_CREATED:

SEVEN_EXECUTION_RULES_PRESENT: YES | NO
FOUR_AI_FAILURE_MODES_PRESENT: YES | NO

TOTAL_INTERNAL_LINKS:
RESOLVED_LINKS:
UNRESOLVED_LINKS:

FILES_CHANGED_OUTSIDE_VAULT:
PLUGINS_INSTALLED:
SECRETS_ADDED:
SOURCE_FILES_COPIED:

VALIDATION:
REMAINING_RISKS:
NEXT_RECOMMENDED_ACTION:
```

ห้ามรายงานเพียงว่า “เสร็จแล้ว”

ต้องแนบรายการไฟล์และผล Validation ที่ตรวจจากไฟล์จริง

```

Work Order นี้ให้ AI สร้างเฉพาะ **ฐานโครงสร้างกับหน้าโปรเจกต์เริ่มต้น** ก่อน โดยยังไม่อ่านโค้ดเชิงลึกหรือแต่งสถานะปัจจุบันขึ้นเอง หลังจากชุดนี้ผ่าน Validation แล้ว ค่อยออก Work Order ถัดไปให้ตรวจ Repository truth และเติมรายละเอียดทีละโปรเจกต์ครับเจ้านาย
```
