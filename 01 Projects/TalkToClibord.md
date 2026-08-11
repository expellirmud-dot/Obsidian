---
type: project
last_reviewed: 2026-08-11
evidence_class: verified
---

# TalkToClibord

## โปรเจกต์นี้คืออะไร

เดสก์ทอป AI assistant ส่วนตัว (ชื่อใน repo คือ "J.A.V.I.S" / "Vision") — แอป Python + Tkinter GUI ที่คุยกับผู้ใช้ด้วยภาษาไทย เรียก Gemini API เพื่อตอบคำถาม/สั่งงาน มี memory (chat_history + MemoryVault), TTS ด้วย pygame, และคลิปบอร์ด/ไฟล์ service

**Evidence:** `README.md` ("# J.A.V.I.S"); `JAVIS.md` (project persistent memory — Architecture + Sprint Status); remote `expellirmud-dot/TalkToClibord.git`; HEAD `40b565e`

> หมายเหตุ: repo ชื่อ `TalkToClibord` แต่เอกสารภายในเรียก "J.A.V.I.S"/"Vision" — ใช้ชื่อ repo เป็นหลักสำหรับ Vault Overview ตาม convention

## ปัญหาที่ต้องการแก้

- ต้องการ assistant บนเดสก์ทอปที่คุยภาษาไทยได้ และเข้าถึงคลิปบอร์ด/ไฟล์/บริบท本地ได้
- ต้องการความจำข้ามเซสชัน (chat history + persistent memory vault)
- ต้องการ TTS เพื่อตอบเสียง และ interface แบบ GUI

## เป้าหมายหลัก

- Tkinter GUI frontend (`newVision.py` ตาม JAVIS.md)
- Python backend modules (`vision_*.py`) — engine, hand service, interface, context builder/compactor, dependency graph
- Gemini API เป็น AI service (`vision_ai_service.py`, `miniGeminiWeb.py`)
- Persistent memory: `chat_history.json` + MemoryVault
- TTS ด้วย `pygame.mixer`
- Thai language support ตลอดทั้งระบบ
- Expense tracking (ExpenseTracker V2.0, in-memory cache) — ฟีเจอร์รอง

## ขอบเขต

**In scope (verified, จาก JAVIS.md + src tree):**
- Frontend: Tkinter GUI
- Backend: `src/core/vision_*.py` (engine, hand_service, interfaces variants, context_builder, context_compactor, context_recovery, dependency_detective, dependency_graph, live_service, persistent_memory) + `src/api/` (vision_ai_service, vision_api_manager) + `src/config/` (models, pricing, prompts, settings)
- AI Service: Gemini API
- Memory: chat_history.json, MemoryVault
- Audio: pygame.mixer (TTS)
- Config: vision_config.py
- Expense tracking (ExpenseTracker V2.0)
- Docs: `docs/` (config_compatibility, optional_dependency_audit, requirements_coverage_audit, stabilization_baseline, ui_module_audit)

**Out of scope / unknown (verified):**
- ไม่พบ AGENTS.md / work-order pointer ใน source → ไม่มี current-task authority ชัดเจน
- หลายไฟล์ `.bat` / `.spec` / `.rar` / `backup/` / `buggy_file.py` / `outbox_fixed.py.bak` ดูเหมือน artifact/snapshot ไม่ใช่ core — บันทึกไว้ ไม่นำมาสรุปเป็นสถาปัตยกรรมหลัก

## ตำแหน่งไฟล์จริง

- Local (resolved): `D:\TalkToClibord`
- GitHub: `https://github.com/expellirmud-dot/TalkToClibord.git`
- Exact Git root (2026-08-11): `D:/TalkToClibord`
- Branch: `main` · HEAD: `40b565e6c1dc34c6efa3640d79e2ada9083e74b0` (short `40b565e`) · 41 commits
- Git status: **pre-existing dirty tracked files** (`docs/requirements_coverage_audit.md`, `outbox_fixed.py`, `src/config/models.py`, `src/config/settings.py`, `src/core/red_file.py`, `src/core/vision_context_builder.py`, `src/core/vision_dependency_graph.py`, `src/core/vision_engine.py`, `src/core/vision_hand_service.py`, `src/core/vision_interface.py`, `src/core/vision_persistent_memory.py`) + untracked (`JAVIS.md`, `*.bat`, `*.spec`, `data/config/`, ฯลฯ) — ไม่เกี่ยวข้องกับ Vault onboarding, อ่าน-only บันทึกไว้
- Last commit: `2026-05-13 Merge pull request #21 ... optional dependency audit`

## Repository

- Remote: `https://github.com/expellirmud-dot/TalkToClibord.git`
- Default branch: `main`
- Stack (verified): Python (Tkinter GUI), Gemini API, pygame (TTS), MemoryVault/chat_history; requirements in `requirements.txt` + `requirements-optional.txt`
- Authority files (verified จาก repo truth 2026-08-11): `README.md` (J.A.V.I.S overview + dependency/CI notes), `JAVIS.md` (project persistent memory — architecture + sprint status; ไฟล์ untracked แต่เป็น primary project doc), `docs/*` audit docs, `vision_config.py`, `src/` tree
- Current work state (source): ไม่มี AGENTS.md / work-order pointer; `JAVIS.md` Sprint Status = "Test Sprint" (updated 2026-04-18); git log ล่าสุดคือ optional-dependency audit tasks (TASK O/P) + merge PR #21 (2026-05-13) → สถานะ active development / test phase, ไม่มี active task tracker ชัดเจน

> หมายเหตุ: ไม่มี `Work-Order/CURRENT_WORK_ORDER.md` หรือเทียบเท่า → ไม่มี active WO ให้引用

## สถานะปัจจุบัน

- Source repo อยู่ในสถานะ active development / test phase ("Test Sprint" ตาม JAVIS.md) — แต่ไม่มี work-order tracker ชัดเจน
- Evidence class: **verified** (repo truth 2026-08-11)

> หมายเหตุ: ไม่มีการอ้างสถานะ "active task" ที่อิงจาก tracker — สถานะสืบจาก JAVIS.md + git log

## สิ่งที่ทำเสร็จแล้ว

- โครงสร้าง Python + Tkinter GUI frontend
- `vision_*.py` backend modules (engine, hand service, interfaces, context builder/compactor/recovery, dependency detective/graph, live service, persistent memory)
- Gemini API integration (`vision_ai_service.py`, `miniGeminiWeb.py`)
- Persistent memory (chat_history.json + MemoryVault)
- pygame TTS
- Thai language support ตลอดระบบ
- ExpenseTracker V2.0 (in-memory cache)
- Optional dependency audit (TASK O/P) + lazy import (TASK P) — รองรับ minimal environment
- docs audit ชุด: config compatibility, optional dependency, requirements coverage, stabilization baseline, ui module audit

## งานที่กำลังทำ

- ตาม `JAVIS.md`: "Test Sprint" / "Test Focus" (updated 2026-04-18) — ไม่มี active task tracker ชัดเจน
- git history สะท้อน optional-dependency audit + stabilization เป็นงานล่าสุด

## งานถัดไป

- รอเจ้าของสั่งงานถัดไป
- หากขยาย: ดู `docs/stabilization_baseline.md`, `docs/ui_module_audit.md`, `JAVIS.md` สำหรับทิศทางถัดไป

## สถาปัตยกรรม

สรุปสถาปัตยกรรม (ไม่สร้างแยกต่างหากตาม WO-029 §7):

- Frontend: Tkinter GUI (`newVision.py` ตาม JAVIS.md)
- Backend: Python modules `src/core/vision_*.py`:
  - `vision_engine.py` — core engine
  - `vision_hand_service.py` — hand/service layer
  - `vision_interface*.py` — หลาย variants (base, corrected, file_preview, memory, optimized, tpm, tpm_correct, tpm_fixed, updated) — variants บันทึกไว้ ไม่สรุปเป็นสถาปัตยกรรมเดียว
  - `vision_context_builder.py` / `vision_context_compactor.py` / `vision_context_recovery.py` — context management
  - `vision_dependency_detective.py` / `vision_dependency_graph.py` — dependency analysis
  - `vision_live_service.py` / `vision_persistent_memory.py` — service + memory
- AI: `src/api/vision_ai_service.py` (Gemini), `vision_api_manager.py`, `src/core/miniGeminiWeb.py`
- Config: `src/config/` (models, pricing, prompts, settings) + `vision_config.py`
- Memory: `chat_history.json` + MemoryVault
- Audio: `pygame.mixer` (TTS)
- Key decisions (JAVIS.md): simple truncation for memory summarization (deterministic cache hit), static instructions in RAM, identity-based instruction override (INSTR_VISION_ULTIMATE), expense tracking with in-memory cache
- Patterns: `sys_log` logging, Thai support, thread-safe locks, try-except

**Follow-up:** หากต้องการเอกสารสถาปัตยกรรมละเอียด ให้สร้าง `02 Architecture/ARCH-talktoclibord-<topic>.md` ใน WO ภายหลังเมื่อมี evidence พอ

## การตัดสินใจสำคัญ

- Identity-based instruction override (INSTR_VISION_ULTIMATE for VISION) — คอนฟิกเอกลักษณ์ assistant
- Memory summarization ใช้ simple truncation (deterministic สำหรับ cache hit)
- Static instructions โหลดเข้า RAM เพื่อ optimize context
- Expense tracking ด้วย in-memory cache (ExpenseTracker V2.0)
- Optional dependency lazy import — รองรับ minimal/CI environment (TASK O/P)
- Thai language support เป็น first-class ตลอดระบบ

## ปัญหาและความเสี่ยง

- ไม่มี AGENTS.md / work-order pointer → ไม่มี current-task authority ชัดเจน
- Source มี pre-existing dirty tracked files + หลาย untracked artifacts (`*.bat`, `*.spec`, `*.rar`, `backup/`, `buggy_file.py`) — บันทึกไว้ ไม่นำมาสรุปสถาปัตยกรรมหลัก (อาจมี debt/experimental)
- `JAVIS.md` เป็น untracked file — เป็น primary project doc แต่ไม่เข้า version control (risk: หายหากไม่ backup)
- หลาย `vision_interface*.py` variants — บ่งชี้การทดลอง/refactor ที่อาจยังไม่ merge (technical debt)
- Lifecycle ปล่อย `unknown` (ห้าม infer)

## บทเรียน

- Project ภายในเรียก "J.A.V.I.S"/"Vision" แต่ repo ชื่อ `TalkToClibord` — ใช้ชื่อ repo ใน Vault Overview (convention)
- `JAVIS.md` เป็น persistent-memory doc ที่มีสถาปัตยกรรม + sprint status ครบ — ใช้เป็น primary authority แทน README
- Optional-dependency lazy import → รันได้ใน minimal/CI  environment (หลักฐานจาก TASK O/P)

## Resume Context

- Repo: `D:\TalkToClibord`, branch `main`, HEAD `40b565e` (2026-08-11, 41 commits, มี pre-existing dirty + untracked artifacts)
- Status: active dev / "Test Sprint" (JAVIS.md), ไม่มี active task tracker
- Onboarded into Vault ผ่าน WO-OBSIDIAN-029 (2026-08-11)
- ตรวจ `git status`, `JAVIS.md`, `README.md`, `docs/`, `src/` ก่อน resume (repo-truth-first)

## วันที่ตรวจสอบล่าสุด

2026-08-11 (WO-OBSIDIAN-029: repository truth verified, HEAD 40b565e)
