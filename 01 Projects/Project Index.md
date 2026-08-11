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
| [[thai_stt_app]] | Thai Speech-to-Text desktop app (Silero VAD + Groq Whisper + PySide6 UI + Desktop Capture/OCR) | `D:\thai_stt_app` | **verified** (onboarded WO-OBSIDIAN-025; HEAD be7bd07; WO-Skill-Audit IN_PROGRESS) | 2026-08-11 (WO-OBSIDIAN-025: Repository truth verified, HEAD be7bd07) |
| [[lumina-studio]] | Premium photography landing page (Next.js + React + TS + Tailwind), Phase 1, deployed Vercel | `D:\lumina-studio` | **verified** (onboarded WO-OBSIDIAN-026; HEAD e98c9f6; status PASSED/READY FOR DEPLOY) | 2026-08-11 (WO-OBSIDIAN-026: Repository truth verified, HEAD e98c9f6) |
| [[lightroom-ai-exposure]] | Windows-first Lightroom Classic exposure assistant (Python lr-ai-exposure, MVP adjusts only crs:Exposure2012, dry_run default) | `D:\ai-tools\lightroom-ai-exposure` | **verified** (onboarded WO-OBSIDIAN-027; HEAD 243c405; source stable/complete after WO-028) | 2026-08-11 (WO-OBSIDIAN-027: Repository truth verified, HEAD 243c405) |
| [[citizen_portal]] | Online citizen-request management system for ด่านทับตะโก municipality (Next.js 16 + Prisma + Supabase + Auth.js), research prototype, MVP flows working | `D:\citizen_portal` | **verified** (onboarded WO-OBSIDIAN-028; HEAD f8ae9fb; research prototype, no active task) | 2026-08-11 (WO-OBSIDIAN-028: Repository truth verified, HEAD f8ae9fb) |
| [[TalkToClibord]] | J.A.V.I.S desktop AI assistant (Python Tkinter GUI + vision_*.py backend + Gemini API + MemoryVault + pygame TTS, Thai-language), active dev / Test Sprint | `D:\TalkToClibord` | **verified** (onboarded WO-OBSIDIAN-029; HEAD 40b565e; pre-existing dirty + untracked artifacts) | 2026-08-11 (WO-OBSIDIAN-029: Repository truth verified, HEAD 40b565e) |
| [[AI-Workspace]] | System-level AI ops workspace (multi-app/multi-model/multi-project orchestration, manual-safe V1, ai-ops-registry) | `D:\ai-tools\AI-Workspace` | **verified** (onboarded WO-OBSIDIAN-030; HEAD 6934067; pre-existing dirty .serena/project.yml + src/App.jsx) | 2026-08-11 (WO-OBSIDIAN-030: Repository truth verified, HEAD 6934067) |

หมายเหตุ: `Last Verified` ในแต่ละรอบขึ้นอยู่กับขอบเขตของ Work Order นั้น

กลับไป [[Project Dashboard]]
