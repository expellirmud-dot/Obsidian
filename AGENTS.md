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
