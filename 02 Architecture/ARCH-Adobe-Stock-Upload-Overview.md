---
type: architecture
project: Adobe Stock Upload Assistant
last_reviewed: 2026-07-28
---

# Architecture Overview: Adobe Stock Upload Assistant

> สรุปจาก Repository `D:\adobe-stock-upload` HEAD `0e5f9fc`

## ภาพรวมสถาปัตยกรรม

ระบบช่วยเตรียมภาพ Metadata หมวดหมู่ และกระบวนการอัปโหลดผลงานไปยัง Adobe Stock โดย Owner เป็นผู้ยืนยันและกด Submit เองเสมอ (No Auto-Submit)

## Core Roles

| Role | Responsibility |
|------|---------------|
| **Controller** | กำหนด scope, task packet, validation gates, commit readiness, execution level |
| **Worker** | Execute approved task packet, follow allowed/forbidden files, run validation |
| **Reviewer** | Verify scope compliance, validation evidence, commit readiness |
| **Owner** | Final approval, explicit git add, manual Adobe Stock submission |

Agent เดียวสามารถทำ Controller+Worker+Reviewer ตามลำดับได้ แต่ต้อง fulfill แต่ละบทบาท distinct

## Execution Model

```
Owner defines goal
→ Controller validates scope & creates task packet
→ Worker executes bounded implementation
→ Worker runs validation
→ Reviewer checks evidence & compliance
→ Owner approves & performs explicit git add
→ Manual Adobe Stock submission (Owner)
```

## Execution Levels

| Level | Name | Permitted Actions |
|-------|------|-------------------|
| L0 | Read-Only Review / Audit | Read files, inspect logs, review reports. No writes. |
| L1 | Docs / Governance / Config | Edit documentation, governance, config. No code/runtime. |
| L2 | Local Deterministic Code / Tests | Python modules, CLI tools, tests. No external services. |
| L3 | Browser / Upload Workflow Support | Metadata prep, image inspect, reports. No Submit. |
| L4 | Policy / Account / Submission-Risk | Account settings. Requires Owner approval. |
| L5 | External Submit / Account / Payment / Tax / Credential | **Stop-only.** Owner must perform manually. |

## Project Structure

```text
D:\adobe-stock-upload
├── AGENTS.md                 Agent behavior guidelines
├── PROJECT_RULES.md          Core project rules
├── README.md                 Project overview
├── .gitignore
├── _venv/                    Python virtual environment
├── ai/                       AI skills (ai/skills/read-first-adobe-stock/)
├── config/                   Configuration
├── docs/
│   ├── adobe-stock/          Adobe Stock-specific docs
│   ├── architecture/         Architecture docs
│   ├── testing/              Testing docs
│   └── workflow/             Workflow standards, loop contract, task policy
├── .tasks/                   Task packets + template
│   ├── CURRENT_TASK.md       Active task pointer
│   └── TASK-*/               Individual task packet folders
├── src/                      Source code
├── tests/                    Test files
├── tools/                    CLI tools
├── input/                    Input directory (gitignored)
├── logs/                     Logs (gitignored)
├── metadata/                 Metadata (gitignored)
├── ready/                    Ready for review (gitignored)
├── hold/                     Hold (gitignored)
├── rejected_local/           Rejected (gitignored)
└── _proposed_next/           Proposed future tasks
```

## Task Packet Structure

แต่ละ task มี 7 ไฟล์ใน `.tasks/TASK-<NAME>-<NNN>/`:

| File | Purpose |
|------|---------|
| `task.md` | Task definition and scope |
| `plan.md` | Implementation plan |
| `implementation-order.md` | Ordered implementation steps |
| `status.md` | Current status and checklist |
| `qa-checklist.md` | Quality assurance checklist |
| `worker-handoff.md` | Context for handoff between sessions |
| `final-report.md` | Summary and evidence |

## Safety Mechanisms

- **No Auto-Submit**: AI ห้ามกด Submit หรือเรียก Adobe Stock API — Owner/manual only
- **Explicit Git Add Only**: ห้าม `git add .` หรือ `git add -A` โดยไม่มี Owner approval
- **Execution Levels**: ควบคุมว่าอะไรทำได้/ไม่ได้ตาม L0–L5
- **Skill Source Lock**: ใช้ `ai/skills/` เท่านั้น — ห้ามใช้ dot-prefixed path
- **Forbidden Files**: `tools/stock_preflight.py`, `src/adobe_stock_upload/*`, `tests/*` ห้าม edit เว้นแต่ task ระบุ
- **Task Packet Governance**: 7 ไฟล์ต่อ task เพื่อบังคับ scope และ evidence

## Known Limitations

- No remote configured — local-only Git เสี่ยง data loss
- No active executable task (all completed)
- Worktree: 1 modified + 3 untracked — ต้องตรวจก่อน execute งานใด
- Task packet overhead: 7 ไฟล์ต่อ task อาจมากเกินไปสำหรับงานเล็ก
- No production Adobe Stock API integration (by design — Owner/manual submit)

## Evidence Sources

- `D:\adobe-stock-upload\AGENTS.md`
- `D:\adobe-stock-upload\PROJECT_RULES.md`
- `D:\adobe-stock-upload\README.md`
- `D:\adobe-stock-upload\docs\workflow\ADOBE_STOCK_WORKFLOW_STANDARDS.md`
- `D:\adobe-stock-upload\docs\workflow\LOOP_CONTRACT.md`
- `D:\adobe-stock-upload\docs\workflow\TASK_PACKET_POLICY.md`
- `D:\adobe-stock-upload\docs\workflow\VALIDATION_AND_COMMIT_GATE.md`
- `D:\adobe-stock-upload\.tasks\CURRENT_TASK.md`
- `D:\adobe-stock-upload\.tasks\TASK-ADOBE-STOCK-SAFETY-TERMS-CORE-001\status.md`

## Last Verified

- **HEAD:** `0e5f9fc53f58592ca9e5e3c37bb2b0ef1ced977a`
- **Date:** 2026-07-28
- **By:** WO-OBSIDIAN-007
- **Evidence Classification:** VERIFIED_REPOSITORY_FACT (ยกเว้นที่ระบุ)

กลับไป [[Adobe Stock Upload Assistant]]
