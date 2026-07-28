---
type: architecture
project: STT Typing
last_reviewed: 2026-07-28
---

# Architecture Overview: STT Typing

> สรุปจาก Repository `D:\stt_typing` HEAD `af10254`

## ภาพรวมสถาปัตยกรรม

STT Typing เป็นระบบ Speech-to-Text Typing Assistant สำหรับ Windows Desktop แบบ Offline-First โดยมีสถาปัตยกรรมแบบ Component-Based ภายใน `app/` และใช้ Tkinter เป็น Runtime Shell

## Composition / Runtime Entry Points

```text
main.py                    ← Entry point (official, เรียก STT_auto_paste.main())
  └─ STT_auto_paste.py     ← Runtime orchestrator (ยัง active, legacy root)
       ├─ app/audio/       ← Microphone capture + VAD
       ├─ app/recognition/ ← ASR (Whisper local / Google)
       ├─ app/commands/    ← Command routing + pipeline
       ├─ app/paste/       ← Clipboard + typing
       ├─ app/ui/          ← Tkinter HUD
       ├─ app/windows/     ← Window focus/switching
       ├─ app/hud/         ← Future HUD (PySide6/QML sidecar)
       └─ app/orchestrators/ ← Orchestrator extractions (partial)
```

## Audio → Recognition → Command/Typing → Output Flow

```
Microphone
    ↓
Audio Capture (app/audio/) — Fast listening, VAD segmentation
    ↓
Queueing (app/queueing/) — Audio chunk flow management
    ↓
Recognition (app/recognition/) — Whisper small (local) / Google ASR
    ↓
Intent Resolution → Command Pipeline (app/commands/)
    ├── Dictation → Focus Guard → TypingActionExecutor → Output
    └── Command   → Safety Dispatcher → Confirmation (if risky) → Action
    ↓
Feedback → HUD (app/ui/ Tkinter / app/hud/ Future PySide6)
```

## Major Modules / Components

| Module | Path | Purpose |
|--------|------|---------|
| Audio | `app/audio/` | Mic capture, VAD segmentation, audio queue |
| Recognition | `app/recognition/` | ASR backend: Whisper local + Google |
| Commands | `app/commands/` | Command catalog, router, pipeline, executor, safety |
| Paste | `app/paste/` | Clipboard management, text insertion |
| Windows | `app/windows/` | Window focus detection and switching |
| UI | `app/ui/` | Tkinter HUD (current runtime) |
| HUD | `app/hud/` | Future PySide6/QML sidecar (dev only) |
| Orchestrators | `app/orchestrators/` | Partial extraction (paths, startup) |
| Confirmation | `app/confirmation/` | Confirmation layer for risky actions |
| Correction | `app/correction/` | Dictionary-based text correction |
| Events | `app/events/` | Event routing |
| Feedback | `app/feedback/` | Feedback producer/sink protocols |
| Logging | `app/logging/` | System logging |
| Threading | `app/threading/` | Thread lifecycle management |

## Feature Flags and Safety Boundaries

| Variable | Default | Effect |
|----------|---------|--------|
| `STT_PIPELINE_ENABLED` | disabled | Enable command execution pipeline |
| `STT_REAL_TYPING_ENABLED` | disabled | (Alpha) Enable real OS typing |
| `STT_FORCE_TKINTER` | disabled | Force Tk fallback, skip Future HUD |
| `STT_ENABLE_FUTURE_HUD` | enabled | Enable Future HUD (PySide6/QML sidecar) |

### Safety Mechanisms

- **Focus Guard**: วางข้อความเฉพาะเมื่อ focus อยู่ใน text input
- **Confirmation Layer**: คำสั่งเสี่ยงต้องยืนยันก่อน execute
- **Safety Dispatcher**: Risk classification และ action allowlist
- **Undo/Recovery Pipeline**: ย้อนกลับ action ล่าสุด
- **Real Action Allowlist Policy**: กำหนด action ที่อนุญาตให้ทำจริง
- **Manual-Safe Boundary**: Real OS/window actions ต้อง Owner approval
- **FakeActionSink**: Test sink สำหรับ offline validation

## External/Local Service Boundaries

| Service | Type | Usage |
|---------|------|-------|
| Whisper small | Local | Default ASR (offline) |
| Google Speech API | Cloud | Optional ASR backend |
| PyAudio | Local | Mic capture |
| pyautogui | Local | OS typing / automation |
| uiautomation | Local | Window focus/control |
| PySide6 | Local | Future HUD (dev, not production) |
| SpeechRecognition | Local | ASR abstraction layer |

> **Evidence source**: `requirements.txt` at HEAD af10254. `sounddevice` และ `pywinauto` ไม่ได้อยู่ใน requirements.txt จริง — แก้จากข้อมูลเก่า

## Validation Strategy

- **pytest** (~205+ tests documented at HEAD af10254) — unit + integration
- **tools/smoke_test_commands.py** (44/44) — headless smoke harness
- **tools/audit_context_budget.ps1** — context preflight gate
- **windows-ui-review-runtime** — controlled UI capture harness
- **Manual runtime smoke**: `tools/manual_runtime_smoke.py --manual-runtime` (placeholder)
- **Task packet validation**: git diff, status, check, scope compliance

## Known Limitations / Risks

- **No active executable task** — งานถูกระงับรอ roadmap ใหม่
- **Production Qt shell ยังไม่พร้อมใช้งาน** — Tkinter ต้อง continue support (current runtime)
- **Real typing alpha** — flag-gated ยังต้อง Owner pilot evidence
- **Worktree dirty** — `.serena/project.yml` modified
- **ASR backend mode routing** — มี design แต่ยังไม่ได้ implement ครบ
- **Orchestrator extraction** — ยัง partial (`STT_auto_paste.py` ยัง active shell)
- **Intent Router** — design only, ยังไม่ได้ implement

## Evidence Sources

- `D:\stt_typing\README.md`
- `D:\stt_typing\AGENTS.md`
- `D:\stt_typing\PROJECT_RULES.md`
- `D:\stt_typing\PRODUCT.md`
- `D:\stt_typing\DESIGN.md`
- `D:\stt_typing\main.py`
- `D:\stt_typing\.tasks\CURRENT_TASK.md`
- `D:\stt_typing\docs\STT_PROJECT_CURRENT_STATE.md`
- `D:\stt_typing\docs\LOOP_CONTRACT.md`

## Last Verified

- **HEAD:** `af10254774766425b735e63632eb9a11f9056002`
- **Date:** 2026-07-28
- **By:** WO-OBSIDIAN-005
- **Evidence Classification:** VERIFIED_REPOSITORY_FACT (ยกเว้นที่ระบุ)

กลับไป [[STT Typing]]
