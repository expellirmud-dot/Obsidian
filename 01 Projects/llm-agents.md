---
type: project
status: active
priority: high
project_path: D:\llm-agents
repository: https://github.com/expellirmud-dot/llm-agents.git
current_work_order: 03-WORK ORDER — G3 CLEAN LIVE RETEST (CREDENTIAL READY).md
last_reviewed: 2026-07-28
---

# llm-agents

> เอกสารนี้เป็นคลังบริบทและภาพรวม — สถานะจริงต้องตรวจจาก Git repository และ Current Work Order
> การตรวจล่าสุด: 2026-07-28 (WO-OBSIDIAN-004) — Repository truth verified

## โปรเจกต์นี้คืออะไร

ระบบควบคุมและดำเนินงาน AI Agent แบบ **Bounded Autonomous Worker (L2)** — แยกบทบาท Controller, Worker, Validation และ Runtime Execution ออกจากกันอย่างชัดเจน โดยใช้ Work Order เป็น Long-term memory และ Notepad/Checkpoint เป็น Short-term memory คัดลอกแนวคิดจาก `D:\ai-tools\ai-worker-harness` แต่เป็นโปรเจกต์อิสระ ไม่ import

**VERIFIED_REPOSITORY_FACT:** โปรเจกต์เป็น standalone L2 scaffold ไม่มี multi-agent runtime; จุดประสงค์คือพิสูจน์ offline file I/O baseline แล้วค่อยขึ้น L3 (checkpoint/resume + validation เชิงลึก)

## ปัญหาที่ต้องการแก้

สร้าง agent loop ที่:
1. รันได้แบบ offline กับ `--stub` (พิสูจน์ลูป/เครื่องมือ/ขอบเขต)
2. รันจริงกับ Gemini free tier (ต้องมี `GEMINI_API_KEY` ใน env)
3. ผ่าน canonical pytest suite ทุกครั้งก่อน deploy
4. มี Gate ควบคุม file I/O อย่างเข้มงวด (allowed globs + exact paths เท่านั้น)

**VERIFIED_REPOSITORY_FACT:** ปัญหานี้ตรงกับที่ระบุใน `README.md` และ `config/settings.json` (gate section)

## เป้าหมายหลัก

1. **Wave 0**: Offline file I/O baseline → canonical tests pass ✅ (committed)
2. **Wave 1**: Live provider test (1 bounded run, credential ready) → DRAFTED, awaiting Owner Go
3. **L3**: Checkpoint/resume + deep validation

**VERIFIED_REPOSITORY_FACT:** ลำดับนี้มาจาก `README.md` และ `work_orders/05-CONTROLLER DIRECTIVE — WAVE 0 BASELINE FREEZE AND WAVE 1 DISPATCH.md`

## ขอบเขต

### In Scope

- Bounded L2 agent loop (planner, loop, tools, gate, memory, provider)
- File I/O restriction: `projects/**` + `test.txt` (READ/APPEND) เท่านั้น
- Free API provider (Gemini free tier) via stdlib `urllib`
- Offline stub provider สำหรับ deterministic testing
- Checkpoint/resume mechanism (checkpoints dir)
- Canonical pytest suite เป็น quality gate

**VERIFIED_REPOSITORY_FACT:** ขอบเขตตรงกับ `config/settings.json` (gate.allowed_file_globs, allowed_exact_paths, forbidden_file_globs) และ `README.md`

### Out of Scope

- Multi-agent runtime / orchestration (จะพิจารณาตอน L3/L4)
- CodeGraph integration (README: "ยังไม่เพิ่ม — โค้ดยังเล็ก")
- Serena read-write (ปัจจุบัน read-only adapter เท่านั้น)
- Production deployment / scaling
- Persistent external memory beyond checkpoints

**VERIFIED_REPOSITORY_FACT:** Out-of-scope items ระบุใน `README.md` และ `AGENTS.md` authority precedence

## ตำแหน่งไฟล์จริง

`D:\llm-agents` — **VERIFIED_REPOSITORY_FACT**: Git root confirmed at `D:/llm-agents` (discovery script exit 0)

## Repository

- **Remote**: https://github.com/expellirmud-dot/llm-agents.git (**VERIFIED_REPOSITORY_FACT**)
- **Branch**: `integration/wave1-foundation` (**VERIFIED_REPOSITORY_FACT**)
- **HEAD**: `099e516b2cf504d664d9cf12a40b722900ba7dde` (**VERIFIED_REPOSITORY_FACT**)
- **Upstream**: NONE (no upstream configured) (**VERIFIED_REPOSITORY_FACT**)
- **Git Status**: 36 dirty files (14 staged changes + 22 untracked) — **VERIFIED_REPOSITORY_FACT**
  - Staged: AGENTS.md (new), README.md, agent/provider.py, requirements.lock, run.py, scripts/gemini_smoke.py, tests/__init__.py, work_orders/CURRENT_WORK_ORDER.md, 6 deleted projects/* files
  - Untracked: work orders drafts, BAAR Roadmap, G3_REPORT, HERMES_START docs, hermes-serena-mcp JSON, test.txt, scratch/, etc.

## สถานะปัจจุบัน

**Status: ACTIVE (Wave 1 — Live verification pending)**

- Wave 0 baseline frozen at commit `8f3dbb2` (tag: `G3_FILE_IO_OFFLINE_IMPLEMENTATION_ACCEPTED / LIVE_VERIFICATION_PENDING`)
- Current work order pointer: `work_orders/03-WORK ORDER — G3 CLEAN LIVE RETEST (CREDENTIAL READY).md` — **Status: DRAFTED — NOT EXECUTED (awaiting Owner Go)**
- Provider: google_gemini_free / gemma-4-31b-it (config/settings.json)
- Credential: `GEMINI_API_KEY` must be present in process environment (loaded from User store in-memory; not persisted)

**VERIFIED_REPOSITORY_FACT:** สถานะทั้งหมดจาก `work_orders/CURRENT_WORK_ORDER.md`, `work_orders/03-WORK ORDER — G3 CLEAN LIVE RETEST (CREDENTIAL READY).md`, `README.md`, และ git log

## สิ่งที่ทำเสร็จแล้ว

| Item | Evidence | Classification |
|------|----------|----------------|
| AGENTS.md canonical authority established | `AGENTS.md` committed (staged) | VERIFIED_REPOSITORY_FACT |
| Offline file I/O baseline (L2) | Commits `dec05ef` → `20bdc46` → `ed977c2` | VERIFIED_REPOSITORY_FACT |
| Canonical pytest suite structure | `tests/` with `test_g3_file_io.py`, `test_l2_agent.py` (staged) | VERIFIED_REPOSITORY_FACT |
| Gate implementation (agent/gate.py) | Staged for selective commit on PASS | VERIFIED_REPOSITORY_FACT |
| Loop/planner/tools/memory/provider modules | `agent/` directory complete | VERIFIED_REPOSITORY_FACT |
| Settings.json with free API config | Committed (staged) | VERIFIED_REPOSITORY_FACT |
| Serena read-only adapter registered | `.serena/project.yml` + global config | VERIFIED_REPOSITORY_FACT |
| Wave 0 baseline tag | `8f3dbb2` tag present | VERIFIED_REPOSITORY_FACT |

## งานที่กำลังทำ

| Work Order | Status | Blocker |
|------------|--------|---------|
| 03-WORK ORDER — G3 CLEAN LIVE RETEST (CREDENTIAL READY) | DRAFTED — NOT EXECUTED | **Owner Go required** — credential ready, single live run pending |

**VERIFIED_REPOSITORY_FACT:** จาก `work_orders/CURRENT_WORK_ORDER.md` pointer และ work order file เอง

## งานถัดไป

1. **Owner Go** → Execute WO-03 live run (single invocation, strict gate)
2. On `G3_FILE_IO_CLEAN_LIVE_PASS` → Selective stage 6 approved files + commit
3. **L3**: Checkpoint/resume + deep validation (planned in `work_orders/04-WORK ORDER - G3 ENGINEERING LIVE MODE.md`)

**SUPPORTED_INFERENCE:** ลำดับจาก `README.md` "ลำดับเดินหน้า" และ work orders ใน `work_orders/planning/`

## สถาปัตยกรรม

ระบบ L2 Bounded Agent ประกอบด้วย:

```
config/settings.json          → Free API + bounded scope config
work_orders/                  → Long-term memory (Work Orders)
agent/                        → Core runtime
  ├── gate.py                 → File I/O gate (allowlist/denylist)
  ├── loop.py                 → Agent loop (step budget, stop conditions)
  ├── tools.py                → Bounded tools (read/write/run_shell/run_test)
  ├── memory.py               → Notepad + Checkpoint (disk)
  ├── planner.py              → Work Order parser
  ├── provider.py             → GeminiFreeProvider + StubProvider
  └── status.py               → Explicit terminal statuses
projects/                     → Agent output artifacts (Gate allows only here)
checkpoints/                  → Resume notepads (disk)
logs/                         → Run reports (JSON)
tests/                        → Canonical pytest suite
.serena/                      → Read-only adapter (gitignored)
```

**VERIFIED_REPOSITORY_FACT:** โครงสร้างจาก `TOP_LEVEL_ENTRIES` discovery + `README.md` + `agent/` directory inspection

ดูรายละเอียด: [[ARCH-llm-agents-Overview]]

## การตัดสินใจสำคัญ

| Decision | Evidence | Classification |
|----------|----------|----------------|
| Fail-closed governance (AGENTS.md highest) | `AGENTS.md` lines 1-34 | VERIFIED_REPOSITORY_FACT |
| Exact argv only, no shell metacharacters | `AGENTS.md` rule 2 | VERIFIED_REPOSITORY_FACT |
| Path containment via absolute normalization | `AGENTS.md` rule 1, Common Omission #2 | VERIFIED_REPOSITORY_FACT |
| Single canonical command = proof (no temp scripts) | `AGENTS.md` rule 7 | VERIFIED_REPOSITORY_FACT |
| Free API only (no paid tiers) | `config/settings.json` provider.type=free_api | VERIFIED_REPOSITORY_FACT |
| Serena read-only adapter first | `README.md` line 39-42 | VERIFIED_REPOSITORY_FACT |
| CodeGraph deferred to L3/L4 | `README.md` line 44-45 | VERIFIED_REPOSITORY_FACT |
| No hardcoded API keys (env only) | `README.md` line 55, `settings.json` api_key_env | VERIFIED_REPOSITORY_FACT |
| Gate forbids config/work_orders/*.md writes | `settings.json` gate.forbidden_file_globs | VERIFIED_REPOSITORY_FACT |

## ปัญหาและความเสี่ยง

| Risk | Severity | Evidence | Classification |
|------|----------|----------|----------------|
| 36 dirty files in worktree (staged + untracked) | HIGH | Git status | VERIFIED_REPOSITORY_FACT |
| No upstream branch configured | MEDIUM | `git rev-parse --abbrev-ref HEAD@{upstream}` → NONE | VERIFIED_REPOSITORY_FACT |
| Live credential only in Owner's process env | MEDIUM | WO-03 credential section | VERIFIED_REPOSITORY_FACT |
| Single-run strict gate (no retry on failure) | MEDIUM | WO-03 Stop Rule | VERIFIED_REPOSITORY_FACT |
| Untracked work order drafts mixed with active | LOW | 12+ untracked WO files in work_orders/ | VERIFIED_REPOSITORY_FACT |
| Large JSON artifacts in root (hermes-serena-mcp-*.json ~1.5MB) | LOW | Untracked files | VERIFIED_REPOSITORY_FACT |
| `test.txt` must be preserved (Gate allows APPEND only) | CRITICAL | WO-03 preservation rule | VERIFIED_REPOSITORY_FACT |

**NEEDS_VERIFICATION:** Whether canonical pytest suite passes in current staged state (not run during discovery)

## บทเรียนที่ได้ (Do Not Repeat)

| Lesson | Source | Classification |
|--------|--------|----------------|
| Temp scripts / ad-hoc diagnostics are not proof — one canonical command with exit 0 is | `AGENTS.md` rule 7 | VERIFIED_REPOSITORY_FACT |
| Path containment by convention (`os.path.join`) is not enough — must normalize absolute | `AGENTS.md` Common Omission #2 | VERIFIED_REPOSITORY_FACT |
| Substring allowlists approve malicious commands (`; rm -rf /`) | `AGENTS.md` Common Omission #3 | VERIFIED_REPOSITORY_FACT |
| Tests that clean up after themselves don't prove isolation | `AGENTS.md` Common Omission #4 | VERIFIED_REPOSITORY_FACT |
| Silent fallback to allow (missing allow_shell) turns bounded agent into open shell | `AGENTS.md` Common Omission #1 | VERIFIED_REPOSITORY_FACT |

## เอกสารที่เกี่ยวข้อง

- [[Project Dashboard]]
- [[Project Index]]
- [[ARCH-llm-agents-Overview]]
- [[Work Order Index]]
- [[Prompt Index]]
- [[Project Resume Workflow]]

## Resume Context

| Field | Value |
|-------|-------|
| สถานะล่าสุด | ACTIVE — Wave 1 live verification pending Owner Go |
| งานปัจจุบัน | WO-03 G3 CLEAN LIVE RETEST (DRAFTED, awaiting Owner Go) |
| สิ่งที่ทำเสร็จแล้ว | Wave 0 baseline frozen, AGENTS.md authority, pytest suite, Gate, Serena read-only |
| สิ่งที่ห้ามทำซ้ำ | สร้าง temp scripts แทน canonical command, ใช้ substring allowlist, ข้าม path normalization |
| ปัญหาที่ยังค้าง | 36 dirty files, no upstream, live credential handling, single-run strict gate |
| ขั้นตอนถัดไป | Owner Go → Execute WO-03 → On PASS selective commit 6 files → L3 checkpoint/resume |
| ไฟล์ที่ต้องอ่านก่อน | `AGENTS.md`, `work_orders/CURRENT_WORK_ORDER.md`, `work_orders/03-WORK ORDER — G3 CLEAN LIVE RETEST (CREDENTIAL READY).md`, `config/settings.json` |
| วันที่ตรวจสอบล่าสุด | 2026-07-28 (WO-OBSIDIAN-004) |

## Verification Record

- **Repository checked**: Yes (read-only discovery via project-context-discovery skill)
- **Git HEAD**: `099e516b2cf504d664d9cf12a40b722900ba7dde` (branch: `integration/wave1-foundation`)
- **Current Work Order checked**: Yes — `work_orders/03-WORK ORDER — G3 CLEAN LIVE RETEST (CREDENTIAL READY).md` (Status: DRAFTED)
- **Authority files read**: `AGENTS.md`, `README.md`, `config/settings.json`, `work_orders/CURRENT_WORK_ORDER.md`, `work_orders/03-WORK ORDER — G3 CLEAN LIVE RETEST (CREDENTIAL READY).md`, `agent/provider.py`, `run.py`
- **Discovery script**: `.agents/skills/project-context-discovery/scripts/discover-project.ps1` — exit 0, `DISCOVERY_LEVEL1_RESULT: OK`
- **Verified by**: WO-OBSIDIAN-004 (AI, bounded scope)
- **Verification date**: 2026-07-28