---
type: index
last_reviewed: 2026-07-28
---

# Decision Index

## โฟลเดอร์นี้ใช้เก็บอะไร

บันทึกการตัดสินใจสำคัญ (Architecture Decision Records) ของแต่ละโปรเจกต์ พร้อมบริบท เหตุผล และหลักฐาน

## สิ่งใดควรเก็บ

- การตัดสินใจเชิงสถาปัตยกรรมหรือกระบวนการที่มีผลระยะยาว
- บริบท ตัวเลือกที่พิจารณา เหตุผล และผลกระทบ
- สถานะการตัดสินใจ (proposed / accepted / superseded / rejected)

## สิ่งใดไม่ควรเก็บ

- การตัดสินใจเล็กน้อยที่ไม่มีผลระยะยาว
- Secret หรือ Credential
- ห้ามลบ ADR เดิมเมื่อมีการตัดสินใจใหม่ — ให้ mark เป็น superseded และลิงก์ไป ADR ใหม่

## รูปแบบการตั้งชื่อไฟล์

`ADR-<Project>-<Number>-<Title>.md`

ตัวอย่าง: `ADR-llm-agents-001-Runtime-State-Machine-Freeze.md`

ใช้ [[Decision Template]] เป็นแบบฟอร์ม

## เอกสารในหมวดนี้

ยังไม่มี — จะเพิ่มเมื่อมีการตัดสินใจที่บันทึกอย่างเป็นทางการ

กลับไป [[Project Dashboard]]
