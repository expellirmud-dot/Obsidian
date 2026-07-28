---
type: index
last_reviewed: 2026-07-28
---

# Work Order Index

## โฟลเดอร์นี้ใช้เก็บอะไร

สำเนาหรือลิงก์อ้างอิง Work Order ของแต่ละโปรเจกต์ เพื่อให้ตามรอยได้ว่างานใดถูกสั่งด้วยขอบเขตใด

หมายเหตุ: Work Order ของ Vault นี้อยู่ใน `04 Work Orders` ส่วน Work Order ของ Source Repository อื่นยังคงมี authority อยู่ใน Repository ของโปรเจกต์นั้น

## สิ่งใดควรเก็บ

- Work Order ของ Vault พร้อมขอบเขตและผลลัพธ์
- สำเนาหรือลิงก์อ้างอิง Work Order ของโปรเจกต์อื่น
- สถานะการปิดงาน (`COMPLETED`, `BLOCKED`, `PARTIAL`)

## สิ่งใดไม่ควรเก็บ

- Work Order ฉบับแก้ไขที่ขัดแย้งกับ Authority ใน Source Repository
- Secret หรือ Credential ที่ฝังอยู่ในคำสั่งงาน

## รูปแบบการตั้งชื่อไฟล์

`WO-<Project>-<Number>-<Title>.md`

ตัวอย่าง: `WO-OBSIDIAN-003-CREATE-PROJECT-CONTEXT-DISCOVERY.md`

## Current Work Order

- [[CURRENT_WORK_ORDER]]
- **CLOSED:** [[WO-OBSIDIAN-005-ONBOARD-STT-TYPING]]
- **CLOSED:** [[WO-OBSIDIAN-006-ONBOARD-AI-WORKER-HARNESS]] — งานถัดไป: [[WO-OBSIDIAN-007-ONBOARD-ADOBE-STOCK-UPLOAD]] (PLANNED — NEXT)

## Planned Sequence

| Order | Work Order | Purpose | Status |
|---|---|---|---|
| 003 | [[WO-OBSIDIAN-003-CREATE-PROJECT-CONTEXT-DISCOVERY]] | สร้างสกิลค้นหา authority และบริบทจาก Repository อื่น | CLOSED |
| 004 | [[WO-OBSIDIAN-004-ONBOARD-LLM-AGENTS]] | ตรวจและบันทึกบริบท llm-agents | CLOSED |
| 005 | [[WO-OBSIDIAN-005-ONBOARD-STT-TYPING]] | ตรวจและบันทึกบริบท STT Typing | **CLOSED** |
|| 006 | [[WO-OBSIDIAN-006-ONBOARD-AI-WORKER-HARNESS]] | ตรวจและบันทึกบริบท AI Worker Harness | **CLOSED** |
|| 007 | [[WO-OBSIDIAN-007-ONBOARD-ADOBE-STOCK-UPLOAD]] | ตรวจและบันทึกบริบท Adobe Stock Upload Assistant | PLANNED — NEXT |

ลำดับนี้เป็น sequential gate: ห้ามเริ่มงานถัดไปก่อนงานก่อนหน้าปิด `CLOSED` และ Validation ผ่าน

## Closed Work Orders

- [[WO-OBSIDIAN-005-ONBOARD-STT-TYPING]] — CLOSED
- [[WO-OBSIDIAN-006-ONBOARD-AI-WORKER-HARNESS]] — CLOSED
- [[WO-OBSIDIAN-004-ONBOARD-LLM-AGENTS]] — CLOSED
- [[WO-OBSIDIAN-003-CREATE-PROJECT-CONTEXT-DISCOVERY]] — CLOSED
- [[WO-OBSIDIAN-002-INSTALL-PROJECT-READ-FIRST]] — CLOSED

## Closed Legacy Work Orders

- `work-order/WO-OBSIDIAN-001.md` — COMPLETED
  - เก็บไว้ที่เส้นทางเดิมเพื่อรักษาประวัติ Git
  - Work Order ใหม่ทั้งหมดใช้ `04 Work Orders`

กลับไป [[Project Dashboard]]
