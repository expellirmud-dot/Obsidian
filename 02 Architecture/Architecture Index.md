---
type: index
last_reviewed: 2026-07-28
---

# Architecture Index

## โฟลเดอร์นี้ใช้เก็บอะไร

เอกสารสถาปัตยกรรมระดับภาพรวมของแต่ละโปรเจกต์ — โครงสร้างส่วนประกอบ การไหลของข้อมูล และขอบเขตระหว่างระบบ

## สิ่งใดควรเก็บ

- ภาพรวมสถาปัตยกรรมระดับ Component / Boundary
- แผนภาพการไหลของข้อมูลและการควบคุม
- คำอธิบาย Interface ระหว่างระบบ

## สิ่งใดไม่ควรเก็บ

- Source Code จริง (อยู่ใน Repository)
- รายละเอียด Implementation ระดับบรรทัด
- Secret, Credential, Connection String

## รูปแบบการตั้งชื่อไฟล์

`ARCH-<Project>-<Topic>.md`

ตัวอย่าง: `ARCH-llm-agents-Runtime-State-Machine.md`

## เอกสารในหมวดนี้

- [[ARCH-llm-agents-Overview]] — Bounded autonomous L2 worker architecture

กลับไป [[Project Dashboard]]
