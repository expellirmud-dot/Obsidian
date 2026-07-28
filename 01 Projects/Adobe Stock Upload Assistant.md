---
type: project
status: verified
priority: low
project_path: D:\adobe-stock-upload
repository: local-only — no remote configured
current_work_order: TASK-ADOBE-STOCK-SAFETY-TERMS-CORE-001 (completed — no active executable task)
last_reviewed: 2026-07-28
---

# Adobe Stock Upload Assistant

> สถานะจริงตรวจจาก Repository Commit 0e5f9fc (2026-07-28 ตาม WO-OBSIDIAN-007)
> แหล่ง truth: AGENTS.md, PROJECT_RULES.md, README.md, docs/workflow/*

## โปรเจกต์นี้คืออะไร

ระบบช่วยเตรียมภาพ Metadata หมวดหมู่ และกระบวนการอัปโหลดผลงานไปยัง Adobe Stock — Owner เป็นผู้ยืนยันและกด Submit เองเสมอ

## ปัญหาที่ต้องการแก้

- การอัปโหลดภาพจำนวนมากไปยัง Adobe Stock ต้องการ metadata, categories, keywords ที่ถูกต้อง
- ต้องการระบบตรวจสอบภาพ (dimensions, format, color mode) ก่อนอัปโหลด
- ต้องการ task-based governance: Controller → Worker → Reviewer → Owner approval
- ต้องรักษาหลักการ No Auto-Submit: AI ห้ามกด Submit หรือเรียก Adobe Stock API จริง

## เป้าหมายหลัก

1. ระบบจัดการ metadata และคำแนะนำหมวดหมู่/คำค้น
2. Preflight validation (image inspection, PASS/HOLD/REJECT report)
3. Task packet governance (task.md, plan.md, implementation-order.md, status.md, qa-checklist.md, worker-handoff.md, final-report.md)
4. Execution levels L0–L5 สำหรับแบ่งระดับความเสี่ยง
5. No Auto-Submit — final submission เป็น Owner/manual เท่านั้น

## ขอบเขต

### In Scope

- Image inspection (dimensions, format, color mode, file size)
- Metadata preparation (title, keywords, category recommendations)
- PASS / HOLD / REJECT_LOCAL report generation
- Task packet lifecycle (bootstrap, prep, gather, analyze, triage, execute, review, close)
- Explicit git add only (no `git add .`)
- Owner/manual final submission

### Out of Scope

- Auto-submit to Adobe Stock
- Browser automation for submission (ยกเว้น L3+ task ที่ระบุชัด)
- Adobe Stock API credentials/secrets
- Account settings, contributor profile, payment/tax configuration (L4+, Owner only)
- Editing `tools\stock_preflight.py`, `src\adobe_stock_upload\*`, หรือ `tests\*` เว้นแต่ task ระบุชัด

## ตำแหน่งไฟล์จริง

`D:\adobe-stock-upload`

## Repository

No remote configured — local-only Git repository

## สถานะปัจจุบัน

VERIFIED_REPOSITORY_FACT — ตรวจสอบแล้ว 2026-07-28:

- Branch: main
- HEAD: 0e5f9fc53f58592ca9e5e3c37bb2b0ef1ced977a
- Remote: none (local-only Git)
- Git Status: 1 modified (.tasks/TASK-ADOBE-STOCK-SAFETY-TERMS-CORE-001/status.md — task marked completed), 3 untracked (.continue/, .serena/, .tasks/_proposed_next/)
- Active Task: TASK-ADOBE-STOCK-SAFETY-TERMS-CORE-001 — STATUS: completed
- No active executable task
- Python: D:\adobe-stock-upload\_venv\Scripts\python.exe
- Skill source: D:\adobe-stock-upload\ai\skills\read-first-adobe-stock\SKILL.md

## สิ่งที่ทำเสร็จแล้ว

- AGENTS.md — agent behavior guidelines
- PROJECT_RULES.md — core project rules
- README.md — project overview
- docs/workflow/ADOBE_STOCK_WORKFLOW_STANDARDS.md — workflow standards, execution levels L0–L5
- docs/workflow/LOOP_CONTRACT.md — AI execution loop contract
- docs/workflow/TASK_PACKET_POLICY.md — task packet structure
- docs/workflow/VALIDATION_AND_COMMIT_GATE.md — validation/commit gate policy
- .tasks/CURRENT_TASK.md — active task pointer
- Task packets: TASK-ADOBE-STOCK-BOOTSTRAP-GOVERNANCE-001, METADATA-CATEGORY-CORE-001, PREFLIGHT-CORE-001, SAFETY-TERMS-CORE-001 (completed), SKILL-PACK-SYNC-001, WORKFLOW-STANDARDS-SYNC-001
- .tasks/_template/ — reusable task packet templates

## งานที่กำลังทำ

ไม่มี active executable task — TASK-ADOBE-STOCK-SAFETY-TERMS-CORE-001 completed แล้ว งานถัดไปรอ Owner กำหนด

## สถาปัตยกรรม

ดู [[ARCH-Adobe-Stock-Upload-Overview]]

## การตัดสินใจสำคัญ

- **No Auto-Submit**: AI ห้ามกด Submit หรือเรียก Adobe Stock API — Owner/manual only
- **Execution Levels L0–L5**: ควบคุมขอบเขตตามความเสี่ยง
- **Explicit Git Add Only**: ห้าม `git add .` หรือ `git add -A` โดยไม่มี Owner approval
- **Controller/Worker/Reviewer**: แยกบทบาทแม้ agent เดียวทำได้ตามลำดับ
- **No Remote**: Repository นี้ยังไม่มี remote — ต้อง backup ก่อน data loss

## ปัญหาและความเสี่ยง

- **No remote configured**: local-only Git — เสี่ยง data loss ถ้า drive เสีย
- **Worktree dirty**: 1 modified + 3 untracked — ควรตรวจก่อน execute งานใด
- **No active executable task**: งานทั้งหมด completed — รอ Owner กำหนดงานถัดไป
- **Task governance complexity**: task packet มี 7 ไฟล์ต่อ 1 task — overhead สูงสำหรับงานเล็ก

## Resume Context

### Read-First Order (Next Session)

1. `ai\skills\read-first-adobe-stock\SKILL.md`
2. `PROJECT_RULES.md`
3. `AGENTS.md`
4. `docs\workflow\ADOBE_STOCK_WORKFLOW_STANDARDS.md`
5. `docs\workflow\LOOP_CONTRACT.md`
6. `docs\workflow\TASK_PACKET_POLICY.md`
7. `docs\workflow\VALIDATION_AND_COMMIT_GATE.md`
8. `.tasks\CURRENT_TASK.md`
9. Active task's `task.md`

### Identity

- Active Path: `D:\adobe-stock-upload`
- Python: `_venv\Scripts\python.exe`
- Skill source: `ai\skills\`
- Execution model: Controller → Worker → Reviewer → Owner approval

### Active State

- Current Task: TASK-ADOBE-STOCK-SAFETY-TERMS-CORE-001 (completed)
- Git HEAD: 0e5f9fc53f58592ca9e5e3c37bb2b0ef1ced977a
- Remote: none (local-only)
- Worktree: 1 modified + 3 untracked
- Next action: Owner กำหนด task ถัดไป หรือตั้ง remote

### Safety

- ห้าม auto-submit หรือเรียก Adobe Stock API
- ห้าม edit `tools\stock_preflight.py`, `src\adobe_stock_upload\*`, `tests\*` เว้นแต่ task ระบุ
- ห้ามใช้ dot-prefixed skill/venv path
- ห้าม `git add .` หรือ `git add -A` — ใช้ explicit `git add <file>` เท่านั้น
- ห้ามเปิด browser automation โดยไม่มี L3+ task
- ห้ามติดตั้ง dependency
- Real Adobe Stock submission ต้อง Owner/manual only

## วันที่ตรวจสอบล่าสุด

2026-07-28 (WO-OBSIDIAN-007)

## Verification Record

- Repository checked: Yes (WO-OBSIDIAN-007)
- Git branch: main
- Git HEAD: 0e5f9fc53f58592ca9e5e3c37bb2b0ef1ced977a
- Git Status: 1 modified, 3 untracked
- Current Task checked: Yes (TASK-ADOBE-STOCK-SAFETY-TERMS-CORE-001 — completed)
- No active executable task
- Repository files modified: 0
- Evidence Sources: AGENTS.md, PROJECT_RULES.md, README.md, docs/workflow/ADOBE_STOCK_WORKFLOW_STANDARDS.md, .tasks/CURRENT_TASK.md
- Verified by: WO-OBSIDIAN-007 (AI)
- Verification date: 2026-07-28

## เอกสารที่เกี่ยวข้อง

- [[Project Dashboard]]
- [[Project Index]]
- [[ARCH-Adobe-Stock-Upload-Overview]]
- [[Work Order Index]]
