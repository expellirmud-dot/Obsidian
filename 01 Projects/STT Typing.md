---
type: project
status: active
priority: medium
project_path: D:\stt_typing
repository: https://github.com/expellirmud-dot/stt_typing.git
current_work_order: TASK-STT-LEGACY-TK-CLEANUP-067 (SUPERSEDED-PENDING-ROADMAP — no active executable task)
last_reviewed: 2026-07-28
---

# STT Typing

> สถานะจริงตรวจจาก Repository Commit af10254 (2026-07-28 ตาม WO-OBSIDIAN-005)

## โปรเจกต์นี้คืออะไร

ระบบช่วยพิมพ์ข้อความและสั่งงานด้วยเสียง (Speech-to-Text Typing Helper) สำหรับ Windows Desktop ภาษาไทย โดยเน้น Offline-First, Focus Guard, และการควบคุม Runtime อย่างปลอดภัย

## ปัญหาที่ต้องการแก้

- พิมพ์ข้อความภาษาไทยด้วยเสียง โดยทำงานแบบ Offline (local model Whisper small)
- ควบคุม Windows desktop (เปิด/ปิดโปรแกรม, สลับหน้าต่าง) ด้วยเสียง
- ต้องปลอดภัย: มี Focus Guard, Confirmation Layer, Safety Dispatcher
- ต้องมี HUD แสดงสถานะตลอดเวลา แบบไม่บดบังงานหลัก

## เป้าหมายหลัก

สร้างระบบ Speech-to-Text Typing Assistant ที่:

1. รับเสียงเร็ว ไม่สะดุด
2. แยก Dictation กับ Command ได้ชัดเจน
3. วางข้อความผ่าน Focus Guard เท่านั้น
4. มี HUD (Tkinter) แสดงสถานะ
5. มี safety layer: confirmation, undo, risk classification
6. ทำงาน Offline-First (Whisper local)

## ขอบเขต

### In Scope

- Windows Desktop เท่านั้น
- ภาษาไทย (primary), รองรับอังกฤษ
- ใช้ local Whisper model (small) เป็น default ASR
- มี Google ASR backend เป็นทางเลือก
- Tkinter runtime shell (production)
- Future HUD (PySide6/QML) เป็น dev/sidecar
- Command Pipeline (260 commands ใน catalog)
- Focus Guard สำหรับวางข้อความ
- Confirmation Layer สำหรับคำสั่งเสี่ยง
- Undo/Recovery

### Out of Scope

- ระบบปฏิบัติการอื่น (macOS/Linux)
- การรับเสียง/พิมพ์จริงในโหมด automated โดยไม่มี Owner อยู่ (manual-safe)
- Production Qt shell — ยังไม่มี (อยู่ระหว่างออกแบบ)
- External ASR service integration ที่ต้องใช้ Internet public API

## ตำแหน่งไฟล์จริง

D:\stt_typing

## Repository

https://github.com/expellirmud-dot/stt_typing.git (origin/main)

## สถานะปัจจุบัน

VERIFIED_REPOSITORY_FACT — ตรวจสอบแล้ว 2026-07-28:

- Branch: main
- HEAD: af10254774766425b735e63632eb9a11f9056002
- Git Status: 1 modified (.serena/project.yml), 4 untracked (.tasks/ proposals)
- Active Task: TASK-STT-LEGACY-TK-CLEANUP-067 — SUPERSEDED-PENDING-ROADMAP (ไม่สามารถ execute ได้)
- Blocker: STAGE_11_PRODUCTION_QT_ARCHITECTURE_INCOMPLETE
- Shell: Tkinter (STTWindow, root.mainloop()) — active production
- Future HUD: PySide6/QML — dev/sidecar, disable via STT_ENABLE_FUTURE_HUD=0
- Python Runtime: D:\stt_typing\venv312\Scripts\python.exe
- Test Suite: pytest (~205+ tests) + smoke test harness

## สิ่งที่ทำเสร็จแล้ว

- Audio Capture / Fast Listening Core
- VAD Segmentation with baseline proof
- Correction dictionaries (common_terms, ai_workflow_terms, window_commands, app_commands)
- Command catalog (260 commands)
- CatalogCommandRouter (63 tests)
- ActionDispatcher + FakeActionSink (55 tests)
- TypingActionExecutor + MemoryTextInsertSink (51 tests)
- CommandExecutionPipeline (70 tests)
- Pipeline runtime integration (default-off, flag-gated)
- Safe typing live alpha (flag-gated, STT_REAL_TYPING_ENABLED=1)
- Pipeline undo recovery alpha
- Focus Guard
- Confirmation Layer
- Real Action Allowlist Policy
- Orchestrator extraction (paths.py, startup.py) — partial
- HUD snapshot bridge
- Smoke test harness (44/44)
- Multiple Tk cleanup task packets preserved as evidence
- DESIGN.md (design system for dark HUD/UI)
- PRODUCT.md (product vision — 10 jigsaw pieces)
- Extensive documentation suite (~70+ docs in docs/)

## งานที่กำลังทำ

ไม่มี active executable task — งานทั้งหมดถูก suspend/routed ไปยัง GOAL-STT-PRODUCTION-QT-APPLICATION-COMPLETION roadmap

## งานถัดไป

ตาม Roadmap 2569-07-19: Production Qt shell completion (STAGE 11)

## สถาปัตยกรรม

ดู [[ARCH-STT-Typing-Overview]]

### ภาพรวมคร่าว

- main.py → STT_auto_paste.py (runtime orchestrator)
- โมดูลหลักใน app/: audio, recognition, commands, paste, windows, ui, orchestration
- Runtime shell: Tkinter (STTWindow)
- Future HUD: PySide6/QML (sidecar mode)
- ASR: Whisper small (local) + Google ASR backend (optional)
- VAD: Silero VAD-based segmentation
- Command Pipeline: flag-gated (STT_PIPELINE_ENABLED=1)
- Real typing: flag-gated (STT_REAL_TYPING_ENABLED=1) — alpha

## การตัดสินใจสำคัญ

- Tkinter ยังคงเป็น production shell — Qt production ยังไม่พร้อม
- Future HUD เป็น dev/sidecar ไม่ใช่ production Qt shell
- Codex GPT-5.4/5.5 เป็น default Controller path
- OpenCode CLI (DeepSeek) = default L1-2 worker, AGY CLI (Gemini) = L3+
- .agents\skills = project skill source of truth
- Project authority: Owner instruction > Task Packet > PROJECT_RULES.md > docs/LOOP_CONTRACT.md > context budget docs > routing docs > skills
- CLI WORKER != SUBAGENT — ห้ามใช้ internal subagent แทน CLI Worker

## ปัญหาและความเสี่ยง

- SUPERSEDED-PENDING-ROADMAP: ไม่มี executable task ปัจจุบัน — งานถูกระงับรอ roadmap ใหม่
- STAGE_11 Qt incomplete: Production Qt shell ยังไม่พร้อม — Tkinter ต้อง support ต่อไป
- Dirty worktree: .serena/project.yml ถูกแก้ไข, .tasks/ มี untracked proposals
- Real typing alpha: ยังเป็น flag-gated alpha — ต้อง Owner pilot evidence ก่อน enable
- Workflow complexity: ระบบ governance ซับซ้อนมาก
- ความขัดแย้งของ Vault data: ข้อมูล Vault เดิมเป็น needs-verification — ต้องอัปเดตให้ตรง repo truth

## บทเรียนที่ได้

- ระบบ governance ที่ซับซ้อนช่วยป้องกัน scope creep แต่เพิ่ม overhead ในการ onboarding
- การแยก Controller/Worker ช่วยให้ audit ได้ชัดเจน
- Task packet system ช่วยให้แต่ละ task มี evidence ครบ
- Single Work Order path (bounded L2-3 seam) มีประโยชน์สำหรับ engineering seam เล็ก

## Resume Context

### Read-First Order (Next Session)

1. AGENTS.md, PROJECT_RULES.md
2. .tasks/CURRENT_TASK.md — ตรวจ current packet state
3. docs/STT_PROJECT_CURRENT_STATE.md
4. docs/LOOP_CONTRACT.md
5. docs/STT_OPENCODE_CLI_MODEL_ROUTING.md
6. Task-specific packet ตาม CURRENT_TASK.md

### Identity

- Active Path: D:\stt_typing
- Python: venv312\Scripts\python.exe
- Shell: Tkinter production, Future HUD (PySide6/QML) sidecar
- ASR: Whisper small local + Google ASR optional
- Tools: opencode, gemini, agy (CLI workers); Codex GPT-5.4/5.5 (Controller)
- Serena/CodeGraph: project root = D:\stt_typing

### Active State

- Current Task: TASK-STT-LEGACY-TK-CLEANUP-067 → SUPERSEDED-PENDING-ROADMAP
- Git HEAD: af10254774766425b735e63632eb9a11f9056002
- Worktree: 1 modified + 4 untracked
- Test baseline: ~205 pytest + 44 smoke
- Next major goal: Production Qt shell completion

### Safety

- ห้าม modify STT recognition, VAD, ASR, paste, command runtime
- ห้ามเปิด mic, real typing, clipboard automation
- ห้ามติดตั้ง dependency
- ห้าม commit/push ใน Source Repository
- ห้ามใช้ internal subagent แทน CLI Worker
- Real OS/window actions ต้อง Owner approval

## วันที่ตรวจสอบล่าสุด

2026-07-28 (WO-OBSIDIAN-005)

## Verification Record

- Repository checked: Yes (WO-OBSIDIAN-005)
- Git branch: main
- Git HEAD: af10254774766425b735e63632eb9a11f9056002
- Git Status: 1 modified (.serena/project.yml), 4 untracked
- Current Work Order checked: Yes (SUPERSEDED-PENDING-ROADMAP)
- Runtime/audio invoked: No
- Repository files modified: 0
- Verified by: WO-OBSIDIAN-005 (AI)
- Verification date: 2026-07-28

## เอกสารที่เกี่ยวข้อง

- [[Project Dashboard]]
- [[Project Index]]
- [[ARCH-STT-Typing-Overview]]
- [[Work Order Index]]
