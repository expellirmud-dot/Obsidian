---
type: dashboard
last_reviewed: 2026-08-11
---

# Project Dashboard

> Canonical inventory ของโปรเจกต์ทั้งหมดที่ Vault รู้จักอยู่ที่ [[Project Registry]]
> รายชื่อ Project Overview 5 รายการด้านล่างไม่ใช่ inventory ทั้งหมด (ดู [[Project Registry]])

## Imported Projects

- [[llm-agents]]
- [[STT Typing]]
- [[AI Worker Harness]]
- [[Utility Disbursement App]]
- [[Adobe Stock Upload Assistant]]
- [[thai_stt_app]]
- [[lumina-studio]]
- [[lightroom-ai-exposure]]

## Discovered — Not Imported

พบ **21 repositories** บนดิสก์ที่ยังไม่มี Project Overview ใน Vault (รายการเต็มใน [[Project Registry]])
ตัวอย่าง: `citizen_portal`, `mcp-agentic-framework`, `JAVIS_Nexus`, `.sandbox/*`

> สถานะทั้งหมด = `needs-verification` — ต้อง on-board ทีละโปรเจกต์ก่อนระบุ lifecycle

## Paused / Archived

- [[Utility Disbursement App]] — paused (owner-confirmed 2026-07-29), ย้ายไป `D:\project_backups\utility-disbursement-app`
- อื่น ๆ: ไม่มีหลักฐาน → ดู [[Project Registry]]

## Needs Verification

โปรเจกต์ที่สถานะยังไม่ได้ตรวจสอบจาก Repository จริง:

- 24 discovered-not-imported repos ([[Project Registry]])
- [[Adobe Stock Upload Assistant]] — lifecycle ไม่ได้ประกาศใน prior WO (repo verified แต่ lifecycle = unknown)

## Recently Reviewed

| Project | Last Reviewed |
| ------- | ------------- |
| [[llm-agents]] | 2026-07-28 (WO-OBSIDIAN-004: Repository truth verified, HEAD 099e516) |
| [[STT Typing]] | 2026-07-28 (WO-OBSIDIAN-005: Repository truth verified, HEAD af10254; status: active/superseded-pending-roadmap) |
| [[AI Worker Harness]] | 2026-07-28 (WO-OBSIDIAN-006: Repository truth verified, HEAD 7096991; status: verified, Goal-09 R07 ACTIVE) |
| [[Utility Disbursement App]] | 2026-07-29 (WO-OBSIDIAN-008: Repository truth verified, HEAD 429cb91; status: paused/owner-confirmed) |
| [[Adobe Stock Upload Assistant]] | 2026-07-28 (WO-OBSIDIAN-007: Repository truth verified, HEAD 0e5f9fc; status: verified, no active task) |

## Completed Projects

ยังไม่กำหนด จนกว่าจะมีหลักฐานจาก Owner หรือ Repository

## How to Resume Work

1. เปิดหน้าโปรเจกต์
2. อ่าน Resume Context
3. ตรวจ Repository truth
4. ตรวจ Current Work Order
5. อัปเดตข้อมูลที่ล้าสมัย
6. เริ่มงานตาม Work Order ใหม่

## Indexes

- [[Project Registry]] — canonical inventory (WO-OBSIDIAN-023)
- [[Project Index]]
- [[Architecture Index]]
- [[Decision Index]] — `03 Decisions/DEC-Vault-Staleness-and-Reverification-Policy.md`
- [[Work Order Index]]
- [[Lessons Learned Index]]
- [[Prompt Index]] — `05 Prompts/Prompt Index.md`
- [[Archive Index]]
