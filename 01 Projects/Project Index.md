---
type: index
last_reviewed: 2026-07-29
---

# Project Index

ตารางรวมโปรเจกต์ทั้งหมดในคลังความรู้ — สถานะจริงต้องตรวจจาก Git repository และ Current Work Order

> **Registry vs Project Overview:** [[Project Registry]] คือรายการโปรเจกต์ที่ Vault รู้จักทั้งหมด (รวม `discovered-not-imported`); ตารางด้านล่างนี้ครอบคลุมเฉพาะโปรเจกต์ที่นำเข้าแล้ว (`imported`) ที่มี Project Overview เต็มรูปแบบ สำหรับ discovered projects ทั้งหมด ดูที่ [[Project Registry]]

| Project | Description | Local Path | Status | Last Verified |
| ------- | ----------- | ---------- | ------ | ------------- |
| [[llm-agents]] | ระบบควบคุมและดำเนินงาน AI Agent แยกบทบาท Controller, Worker, Validation และ Runtime Execution | `D:\llm-agents` | **active** (Wave 1 live verification pending) | 2026-07-28 (WO-OBSIDIAN-004: Repository truth verified, HEAD 099e516) |
| [[STT Typing]] | ระบบช่วยพิมพ์ข้อความและสั่งงานด้วยเสียง Offline-First, Focus Guard | `D:\stt_typing` | **active** (superseded-pending-roadmap) | 2026-07-28 (WO-OBSIDIAN-005: Repository truth verified, HEAD af10254) |
| [[AI Worker Harness]] | ระบบ control plane สำหรับออก Work Order ควบคุม CLI Worker ตรวจ Validation และเก็บหลักฐาน แบบ evidence-driven | `D:\ai-tools\ai-worker-harness` | **verified** (Goal-09 R07 ACTIVE) | 2026-07-28 (WO-OBSIDIAN-006: Repository truth verified, HEAD 7096991) |
| [[Utility Disbursement App]] | ระบบจัดการเอกสารและกระบวนการเบิกจ่ายค่าสาธารณูปโภค | `D:\project_backups\utility-disbursement-app` | **paused** (Owner-confirmed paused; full repo onboarding completed; worktree dirty: `dev.db` modified) | 2026-07-29 (WO-OBSIDIAN-008: Repository truth verified, HEAD 429cb91) |
| [[Adobe Stock Upload Assistant]] | ระบบช่วยเตรียมภาพ Metadata หมวดหมู่ และกระบวนการอัปโหลดไป Adobe Stock — Owner/manual submit | `D:\adobe-stock-upload` | **verified** (no active task) | 2026-07-28 (WO-OBSIDIAN-007: Repository truth verified, HEAD 0e5f9fc) |

หมายเหตุ: `Last Verified` ในแต่ละรอบขึ้นอยู่กับขอบเขตของ Work Order นั้น

กลับไป [[Project Dashboard]]
