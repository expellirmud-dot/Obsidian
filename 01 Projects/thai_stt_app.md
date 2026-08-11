---
type: project
last_reviewed: 2026-08-11
evidence_class: verified
---

# thai_stt_app

## โปรเจกต์นี้คืออะไร

โปรเจกต์桌面 application สำหรับ Thai Speech-to-Text บน Windows — รับเสียงจากไมโครโฟน ส่งผ่าน Voice Activity Detection (Silero VAD) แล้ว transcribe ด้วย STT engine (Google Web Speech / Groq Whisper) พร้อมระบบ corrector สำหรับแก้คำไทยที่เกิดจาก STT ผิดพลาด และระบบ voice command

**Evidence:** `pyproject.toml` name=`thai-stt` v0.2.0, description="Thai Speech-to-Text app with Silero VAD and Groq Whisper"; `AGENTS.md`, `INDEX.md` (สถานะปัจจุบัน); remote `expellirmud-dot/thai_stt_app` (verified)

## ปัญหาที่ต้องการแก้

- พิมพ์ข้อความภาษาไทยด้วยเสียงได้เร็วขึ้นโดยไม่ต้องพิมพ์มือ
- STT ภาษาไทยมักออกคำผิด (especially ชื่อเฉพาะ/คำอังกฤษในประโยคไทย) → ต้อง corrector
- UI เดิม (Tkinter) มีข้อจำกัด thread-safety → migrate เป็น PySide6

## เป้าหมายหลัก

- Real-time Thai STT จากไมโครโฟน พร้อม clipboard auto-paste
- Swap STT engine ระหว่าง Google / Groq Whisper ได้ runtime
- Voice commands (toggle listening, clear text, engine switch)
- Desktop Capture & OCR (Goal-09) — แคปหน้าจอ + ถอดข้อความภาษาไทยจากภาพ

## ขอบเขต

**In scope (verified):**
- `src/thai_stt/` modular package (config, corrector, vad, stt_engines, commands, audio_controller, qt_ui, messages, app)
- PySide6 UI (migrated จาก Tkinter ผ่าน WO-UI-01..06)
- Liquid Glass visual redesign (WO-UI-07A/B/C) + Futuristic Icon system (WO-UI-08D)
- Desktop Capture & OCR chain (Goal-09: WO-CAP-09A/B, WO-OCR-09C, WO-OCR-09F)

**Out of scope / needs-verification:**
- WO-UI-08E (Final Compact Liquid Glass) — สถานะ DRAFT
- WO-OCR-09D (Real Thai OCR Provider) — สถานะ DRAFT
- Windows desktop pixel-level visual sign-off ของ glass/OCR — pending (offscreen Qt ใช้เป็นหลักฐานชั่วคราว)

## ตำแหน่งไฟล์จริง

- Local: `D:\thai_stt_app`
- GitHub: `https://github.com/expellirmud-dot/thai_stt_app`
- Exact Git root (2026-08-11): `D:/thai_stt_app`
- Branch: `main` · HEAD: `be7bd07760cc6c426927a2aec9e0cbce8c2ddf60` (short `be7bd07`) · 71 commits
- Git status: clean ยกเว้น untracked `.hermes/` (Hermes agent artifacts — ไม่แตะ)

## Repository

- Remote: `https://github.com/expellirmud-dot/thai_stt_app.git`
- Default branch: `main`
- Authority files (verified จาก repo truth 2026-08-11): `AGENTS.md` (operating rules + 7 decision rules), `INDEX.md` (doc index + progress), `WORK_ORDER.md` (work-order index → `work-order/`), `CHANGELOG.md`, `pyproject.toml`
- Current task/work-order state: `WO-Skill-Audit` = IN_PROGRESS; `WO-UI-08E`, `WO-OCR-09D` = DRAFT (จาก `WORK_ORDER.md`)

## สถานะปัจจุบัน

- Phase A–I (modular refactor) ✅ เสร็จ
- UI migration Tkinter→PySide6 (WO-UI-01..06) ✅ เสร็จ
- Liquid Glass redesign (WO-UI-07A/B/C) ✅ เสร็จ
- Futuristic Icon & Visual Polish (WO-UI-08D) ✅ เสร็จ
- Desktop Capture & OCR (Goal-09: 09A/B/09C/09F) ✅ เสร็จ; 09D DRAFT
- Active work: `WO-Skill-Audit` (IN_PROGRESS)
- Evidence class: **verified** (repo truth 2026-08-11)

> หมายเหตุความขัดแย้ง: `INDEX.md` ระบุ test counts ต่างกันระหว่างหัวข้อ (276 passed/1 skipped) กับเนื้อหา (203 tests) — จำนวน test ที่แน่ชัด = `needs-verification` ไม่นำมาอ้างเป็นสถานะที่แน่นอน

## สิ่งที่ทำเสร็จแล้ว

- Modular package refactor (`src/thai_stt/`, ~203 tests ตาม INDEX body)
- STT engine strategy (Google + Groq Whisper, `create_engines()` factory)
- `OptimizedCorrector` (regex 14 + exact map 15) สำหรับแก้คำไทย
- `SileroVAD` class (lazy load, BytesIO, numpy RMS pre-filter)
- `AudioController` lock-based thread-safe state
- `VoiceCommandHandler` callback-based (UI-decoupled)
- PySide6 UI migration + Liquid Glass + vector icon system
- Desktop capture/region/OCR + Cloud OCR benchmark (Gemini 3.1 Flash Lite = PRIMARY_CLOUD_OCR)

## งานที่กำลังทำ

- `WO-Skill-Audit` — IN_PROGRESS (ตรวจสอบ/แก้/ติดตั้ง skills)
- `WO-UI-08E` — DRAFT (Final Compact Liquid Glass)
- `WO-OCR-09D` — DRAFT (Real Thai OCR Provider, Windows-local first + Tesseract fallback)

## งานถัดไป

- ปิด `WO-Skill-Audit`
- ตัดสินใจ `WO-UI-08E` / `WO-OCR-09D` (หาก Owner อนุมัติ)
- Windows desktop runtime smoke test สำหรับ Capture/OCR (pending per INDEX)

## สถาปัตยกรรม

สรุปสถาปัตยกรรม (ไม่สร้างแยกต่างหากตาม WO-025 §7):

- Layered modular package ใต้ `src/thai_stt/`
- `app.py` = composition root (wire UI ↔ AudioController ↔ VoiceCommandHandler)
- Audio pipeline: mic → `audio_queue` → `_listen_loop` → VAD pre-filter → STT engine → corrector → clipboard/command
- Thread-safety: `threading.Lock` state (ไม่ใช้ `tk.StringVar` reads จาก thread); Qt dispatch ผ่าน `QTimer` poll (100ms) + GUI-thread assertion
- UI: PySide6 `qt_ui.py` (frameless/topmost/draggable), GlassTheme tokens แยกจาก behavioral UIConfig
- Module decoupling: `messages.py` (UIMessage enum) แยกจาก UI; `commands.py` callback-based ไม่แตะ GUI

**Follow-up:** หากต้องการเอกสารสถาปัตยกรรมละเอียด ให้สร้าง `02 Architecture/ARCH-thai_stt_app-<topic>.md` ใน WO ภายหลังเมื่อมี evidence พอ

## การตัดสินใจสำคัญ

- `src/` layout (PEP 621) — กัน import shadowing (2026-08-07)
- STTEngine ABC + `create_engines()` factory — swap engine runtime ได้ (2026-08-07)
- `AudioController` lock-based state แทน `tk.StringVar` — thread-safe (2026-08-07)
- Tkinter → PySide6 migration ทีละขั้น (WO-UI-01..06) — Qt signal/slot มarshal ข้าม thread ได้ (2026-08-08)
- `blockSignals(True)` รอบ programmatic set — ป้องกัน double-fire callback (WO-UI-05)
- Liquid Glass ไม่ใช้ `QGraphicsBlurEffect` — translucent surface + border + gradient (WO-UI-07)
- Vector icon system แทน emoji primary icon (WO-UI-08D)

## ปัญหาและความเสี่ยง

- Offscreen Qt ไม่ composite QSS translucency เหมือน compositor จริง → ต้อง Windows desktop render สำหรับ pixel-level sign-off (ข้อจำกัดทราบแล้ว)
- Capture harness เดิมอ้างอิง `ui.py` (Tkinter) ที่ลบแล้ว → ต้องอัปเดตก่อนใช้งานจริง
- Groq Whisper ต้อง API key (engine พร้อมเฉพาะเมื่อมี key; `create_engines()` เพิ่ม groq ถ้ามี)
- Test count inconsistency ใน `INDEX.md` → ต้องนับจริงก่อนอ้างสถานะ

## บทเรียน

- Migration แบบ chain (WO-UI-01..07) + behavioral parity tests → ลด regression
- Separate visual tokens (GlassTheme) จาก behavioral config → ปรับ UI โดยไม่แตะ logic
- Decouple UI จาก domain modules ผ่าน callbacks/enums → test ได้โดยไม่มี GUI framework

## Resume Context

- Repo: `D:\thai_stt_app`, branch `main`, HEAD `be7bd07` (2026-08-11)
- Active: `WO-Skill-Audit` (IN_PROGRESS); `WO-UI-08E`, `WO-OCR-09D` (DRAFT)
- Onboarded into Vault ผ่าน WO-OBSIDIAN-025 (2026-08-11)
- ตรวจ `git status`, `WORK_ORDER.md`, `INDEX.md` ก่อน resume (repo-truth-first)

## วันที่ตรวจสอบล่าสุด

2026-08-11 (WO-OBSIDIAN-025: repository truth verified, HEAD be7bd07)
