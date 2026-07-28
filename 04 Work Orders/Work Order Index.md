---
type: index
last_reviewed: 2026-07-28
---

# Work Order Index

## โฟลเดอร์นี้ใช้เก็บอะไร

สำเนาหรือลิงก์อ้างอิง Work Order ของแต่ละโปรเจกต์ เพื่อให้ตามรอยได้ว่างานใดถูกสั่งด้วยขอบเขตใด

หมายเหตุ: Work Order ตัวจริง (Authority) อยู่ใน Repository ของโปรเจกต์นั้น — Vault เก็บเพื่ออ้างอิงเท่านั้น

## สิ่งใดควรเก็บ

- สำเนา Work Order ที่ปิดแล้ว พร้อมผลลัพธ์สรุป
- ลิงก์ไปยัง Work Order Authority ใน Repository จริง
- สถานะการปิดงาน (COMPLETED / BLOCKED / PARTIAL)

## สิ่งใดไม่ควรเก็บ

- Work Order ฉบับแก้ไขที่ขัดแย้งกับ Authority ใน Repository
- Secret หรือ Credential ที่ฝังอยู่ในคำสั่งงาน

## รูปแบบการตั้งชื่อไฟล์

`WO-<Project>-<Number>-<Title>.md`

ตัวอย่าง: `WO-OBSIDIAN-001-Initial-Setup.md`

## เอกสารในหมวดนี้

- Work Order ปัจจุบันของ Vault นี้: `work-order/WO-OBSIDIAN-001.md` (ที่ root ของ repo)

กลับไป [[Project Dashboard]]
