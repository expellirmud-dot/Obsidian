---
type: project
last_reviewed: 2026-08-11
evidence_class: verified
---

# lightroom-ai-exposure

## โปรเจกต์นี้คืออะไร

Windows-first Lightroom Classic exposure assistant — ช่วยปรับความสม่ำเสมอของการรับแสง (exposure) ให้ชุดภาพถ่าย โดยใช้ vision model ตัดสินใจทีละภาพ แล้วเขียนการเปลี่ยนแค่ `crs:Exposure2012` ลง XMP sidecar (โหมด default = `dry_run`, ต้องเจ้าของอนุมัติถึงจะเขียนจริง)

**Evidence:** `README.md` ("Windows-first Lightroom Classic exposure assistant"); `pyproject.toml` name=`lr-ai-exposure` v0.1.0; `AGENTS.md` (Project Mission); remote `expellirmud-dot/Lightroom-AI-Workflow-.git` (verified)

> ⚠️ **Path correction:** WO-024 draft ระบุ source path เป็น `D:\lightroom-ai-exposure` แต่จริงๆ ไม่มี ที่อยู่จริงคือ `D:\ai-tools\lightroom-ai-exposure` (resolved fresh 2026-08-11) — ใช้ที่หลังในเอกสารนี้

## ปัญหาที่ต้องการแก้

- ผู้ใช้เลือกชุดภาพใน Lightroom Classic แล้วต้องการความสม่ำเสมอของ exposure โดยไม่แตะโทนสี/white balance/อื่นๆ
- ต้องการความช่วยเหลือจาก AI โดยไม่เสี่ยงทำลาย RAW / catalog / XMP เดิม
- ต้องมี safety boundary ที่เข้มงวด (backup ก่อนเขียน, เขียนได้แค่ Exposure2012)

## เป้าหมายหลัก

- Pipeline: preview → manifest → AI judge → validate/clamp → XMP backup → write `crs:Exposure2012` → result report
- Default `dry_run` — ไม่เขียนจริงจนกว่าเจ้าของจะอนุมัติ
- MVP ปรับได้แค่ exposure (ไม่แตะพารามิเตอร์อื่น)

## ขอบเขต

**In scope (verified, MVP + WO-001..WO-028):**
- Python CLI package `src/lr_ai_exposure/` (job, manifest, AI judge, exposure judgment, batch consistency, XMP read/backup/safe-write, apply transaction)
- Lightroom Classic plug-in shell (`lightroom-plugin/AIExposureAssist.lrplugin/`) — Plug-in Extras command
- Preview export + manifest handoff, preview validation
- Vision provider integration (Google GenAI), manual batch provider, transactional XMP apply
- Cache-based preview extractor (WO-015..WO-020) + end-to-end cache→Lightroom pilot
- Safety: XMP backup ก่อนทุก real write, เขียนผ่าน temp file + atomic replace

**Out of scope / forbidden (verified, AGENTS.md Non-Negotiable Boundaries):**
- ห้ามแก้ RAW/NEF/JPEG originals, `.lrcat*` catalog, `.lrdata`
- ห้ามแก้ EXIF capture fields, White Balance, Contrast, Highlights, Shadows, Crop, Masks, Keywords, Rating, Label, Sharpening, Noise Reduction
- ห้าม automate final export ใน MVP
- ห้ามเก็บ API key/secrets ใน tracked files

## ตำแหน่งไฟล์จริง

- Local (resolved): `D:\ai-tools\lightroom-ai-exposure`
- GitHub: `https://github.com/expellirmud-dot/Lightroom-AI-Workflow-.git`
- Exact Git root (2026-08-11): `D:/ai-tools/lightroom-ai-exposure`
- Branch: `main` · HEAD: `243c405e46aa36116e377cfa8cb062ed37fdb44a` (short `243c405`) · 96 commits
- Git status: มี pre-existing dirty tracked files (`config/settings.json`, `src/lr_ai_exposure/bridge.py`, `handoff.py`, `main.py`) — ไม่เกี่ยวข้องกับ Vault onboarding, อ่าน-only บันทึกไว้
- Last commit: `2026-07-29 docs: close WO-028 after successful real Lightroom certification`

## Repository

- Remote: `https://github.com/expellirmud-dot/Lightroom-AI-Workflow-.git`
- Default branch: `main`
- Stack (verified): Python ≥3.11, `google-genai`, `pillow`, `pydantic`; pytest; Lightroom Classic plug-in (Lua)
- Authority files (verified จาก repo truth 2026-08-11): `AGENTS.md`, `README.md`, `docs/INDEX.md`, `docs/ARCHITECTURE.md`, `docs/XMP_SAFETY.md`, `docs/AI_JUDGE_CONTRACT.md`, `docs/CAPABILITY_MATRIX.md`, `docs/PROJECT_STATUS.md`, `docs/VALIDATION_REGISTER.md`, `docs/DECISIONS.md`, `Work-Order/CURRENT_WORK_ORDER.md`
- Current work state (source): `Work-Order/CURRENT_WORK_ORDER.md` → STATUS: NONE; no active WO; LATEST_COMPLETED = WO-028 (hotfix, real-runtime certification done)

> หมายเหนtic: Source repo มี WO series ของตัวเอง (WO-001..WO-028) — ตัวเลขซ้ำกับ Vault WO แต่ต่างบริบทกัน (Vault WO-OBSIDIAN-027 ≠ source WO-027)

## สถานะปัจจุบัน

- Source repo อยู่ในสถะนะ stable / complete หลังปิด WO-028 (real-runtime certification สำเร็จ)
- ไม่มี active work order ในรอบนี้
- Evidence class: **verified** (repo truth 2026-08-11)

> หมายเหตุ: ไม่มีการอ้างสถานะ "active task" — source ระบุ STATUS: NONE ชัดเจน

## สิ่งที่ทำเสร็จแล้ว

- Project scaffold + documentation governance (WO-001/002)
- Project traceability registers (CAPABILITY_MATRIX, VALIDATION_REGISTER, PROJECT_STATUS) (WO-003)
- Lightroom plugin bridge + skeleton (WO-004/006)
- Job + manifest foundation (WO-005)
- Preview export + manifest handoff + preview validation (WO-007/008)
- AI decision contract + mock judge (WO-009)
- Exposure judgment + batch consistency + image relevance/quality triage (WO-010.x)
- XMP read + backup + safe write `crs:Exposure2012` (WO-011)
- End-to-end dry-run integration (WO-012)
- Lightroom live pilot + .lrdatacache extraction (WO-013/014)
- Cache preview identity mapping + read-only cache extractor + cache job handoff (WO-015/016/017)
- Single-pass AI triage + exposure (WO-018)
- XMP exposure apply pilot (WO-019)
- End-to-end cache→Lightroom pilot (WO-020)
- Vision provider integration (WO-021)
- Canonical runtime integration repair (WO-022)
- Manual batch provider evidence contract (WO-023)
- Reproducible CLI certification (WO-024)
- Transactional XMP apply pilot (WO-025)
- WO-028 hotfix + real-runtime certification (latest)

## งานที่กำลังทำ

- ไม่มี — source `STATUS: NONE`, no active WO

## งานถัดไป

- รอเจ้าของสั่งงานถัดไป (source ปิด WO-028 แล้ว)
- หากขยาย: ดู `Work-Order/ROADMAP-WO-015-TO-WO-020.md` สำหรับทิศทางถัดไป

## สถาปัตยกรรม

สรุปสถาปัตยกรรม (ไม่สร้างแยกต่างหากตาม WO-027 §7):

- src-layout Python package `lr_ai_exposure`:
  - `main.py` (CLI entry, `--check-config`, dry_run default)
  - `job.py` + manifest handoff (`handoff.py`, `bridge.py`)
  - `ai_judge.py` / `judge.py` (vision provider integration, schema-validated, untrusted output)
  - `exposure_judgment.py` + `batch_consistency.py` (หนึ่ง decision ต่อภาพ, clamp `delta_ev`)
  - `xmp.py` + `apply.py` + `apply_transaction.py` (read/backup/safe-write `crs:Exposure2012`, atomic temp-file replace)
  - `cache_extractor.py` / `cache_probe.py` (read-only preview-cache extraction)
  - `image_triage.py` / `quality_safety.py` (relevance/quality)
- Lightroom plug-in (`lightroom-plugin/AIExposureAssist.lrplugin/`, Lua) — Plug-in Extras command
- Safety: XMP backup ก่อนทุก real write; เขียนผ่าน temp + atomic replace; failed write ทิ้ง XMP เดิมไว้
- Docs as authority: `docs/INDEX.md` คือ canonical doc index; authority order = Active WO > AGENTS.md > XMP_SAFETY > ARCHITECTURE > tests > impl > README

**Follow-up:** หากต้องการเอกสารสถาปัตยกรรมละเอียด ให้สร้าง `02 Architecture/ARCH-lightroom-ai-exposure-<topic>.md` ใน WO ภายหลังเมื่อมี evidence พอ

## การตัดสินใจสำคัญ

- MVP ปรับได้แค่ `crs:Exposure2012` — พารามิเตอร์อื่นถูกห้ามเด็ดขาด (AGENTS.md Non-Negotiable Boundaries)
- Default `dry_run` — ต้อง owner อนุมัติถึงจะ real-write
- AI output = untrusted input → ต้อง schema validate + clamp + low-confidence ไม่ถูก apply อัตโนมัติ
- XMP backup ก่อนทุก real write + atomic temp-file replace
- Vision provider ผ่าน `google-genai` (Gemini); manual batch provider สำหรับ evidence contract
- ห้ามเก็บ secrets ใน tracked files
- Status-truth rules: capability status ต้องไม่เกินระดับที่ evidence พิสูจน์ได้ (IMPLEMENTED ≤ TESTED ≤ INTEGRATED ≤ LIVE_VERIFIED)

## ปัญหาและความเสี่ยง

- Pre-existing dirty tracked files ใน source (`config/settings.json`, `bridge.py`, `handoff.py`, `main.py`) — บันทึกเพื่อความโปร่งใส (อ่าน-only)
- Real-write ต้องเจ้าของอนุมัติ + credentials (Google GenAI API key) — ห้ามทำโดยไม่มี authorization
- Safety boundary เข้มงวด: หาก XMP parse ไม่ได้ต้อง STOP image นั้น ไม่เดา
- Source WO numbering (WO-001..028) ซ้ำกับ Vault WO — ต้องแยกบริบทเวลาอ้างอิง
- Path ใน Vault Registry/WO-024 draft (`D:\lightroom-ai-exposure`) ล้าสมัย — ที่จริงคือ `D:\ai-tools\lightroom-ai-exposure`

## บทเรียน

- Strict safety boundary (backup + atomic write + dry_run default) → ป้องกันทำลาย RAW/catalog
- Vision output = untrusted → validate/clamp ก่อนเขียน
- Capability status-truth rules → ห้ามอ้างสถานะสูงกว่าที่ evidence พิสูจน์
- Documentation governance (docs/INDEX.md canonical) → ป้องกัน doc กลายเป็น authority โดยไม่ตั้งใจ

## Resume Context

- Repo: `D:\ai-tools\lightroom-ai-exposure`, branch `main`, HEAD `243c405` (2026-08-11)
- Status: stable/complete (ปิด WO-028), no active WO
- Onboarded into Vault ผ่าน WO-OBSIDIAN-027 (2026-08-11)
- ตรวจ `git status`, `Work-Order/CURRENT_WORK_ORDER.md`, `docs/PROJECT_STATUS.md` ก่อน resume (repo-truth-first)

## วันที่ตรวจสอบล่าสุด

2026-08-11 (WO-OBSIDIAN-027: repository truth verified, HEAD 243c405)
