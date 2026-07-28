---
type: architecture
project: llm-agents
topic: Overview
last_verified_head: 099e516b2cf504d664d9cf12a40b722900ba7dde
last_verified_date: 2026-07-28
verification_record: WO-OBSIDIAN-004
---

# ARCH-llm-agents-Overview — Bounded Autonomous L2 Worker Architecture

> Architecture summary derived from repository truth (WO-OBSIDIAN-004 verification).
> Links back to project page: [[llm-agents]]
> Part of Architecture Index: [[Architecture Index]]

---

## System Purpose

Standalone **L2 Bounded Autonomous Worker** scaffold that proves:
1. Offline file I/O baseline (deterministic stub provider)
2. Single live provider invocation (Gemini free tier) under strict Gate
3. Canonical pytest suite as quality gate before any live run

Goal: Minimal L2 loop (planner → loop → tools → gate → memory → provider) that can resume from disk checkpoints. No multi-agent runtime, no orchestration layer.

**Evidence:** `README.md` "ลำดับเดินหน้า", `config/settings.json`, `AGENTS.md` authority precedence

---

## Major Planes / Components

| Plane | Component | Responsibility | Evidence |
|-------|-----------|----------------|----------|
| **Config** | `config/settings.json` | Single source of truth: provider, agent limits, tool allowlists, gate rules, memory, logging | VERIFIED_REPOSITORY_FACT (committed/staged) |
| **Long-term Memory** | `work_orders/` | Work Orders = active directives; `CURRENT_WORK_ORDER.md` pointer | VERIFIED_REPOSITORY_FACT |
| **Runtime Core** | `agent/` | Planner, Loop, Tools, Gate, Memory, Provider, Status | VERIFIED_REPOSITORY_FACT (TOP_LEVEL_ENTRIES) |
| **Agent Output** | `projects/` | Only directory Gate allows writes to (glob: `projects/**`) | VERIFIED_REPOSITORY_FACT (gate.allowed_file_globs) |
| **Resume/State** | `checkpoints/` | Notepad persistence across restarts | VERIFIED_REPOSITORY_FACT (memory.checkpoint_dir) |
| **Reports** | `logs/` | JSON run reports (run_id, goal, steps, last_status, results) | VERIFIED_REPOSITORY_FACT (logging.report_dir) |
| **Validation** | `tests/` | Canonical pytest suite (test_g3_file_io.py, test_l2_agent.py) | VERIFIED_REPOSITORY_FACT (staged) |
| **Dev Assistant** | `.serena/` | Read-only adapter (excluded write/shell tools) | VERIFIED_REPOSITORY_FACT |

---

## Authority and Control Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                      AGENTS.md (Canonical)                   │
│  1. AGENTS.md  2. TASK/WORK_ORDER  3. README  4. tests/CI   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    config/settings.json                      │
│  Gate: allowed_file_globs=[projects/**]                      │
│  Gate: allowed_exact_paths={test.txt: [READ, APPEND]}        │
│  Gate: forbidden_file_globs=[config/**, work_orders/**, *.md]│
└─────────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │   Planner   │   │    Loop     │   │   Tools     │
   │ (parse WO)  │   │ (step budget│   │ (read/write/│
   │             │   │  stop cond) │   │  shell/test)│
   └─────────────┘   └─────────────┘   └─────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
   ┌─────────────────────────────────────────────────┐
   │                      Gate                        │
   │  Every file/shell/test op → allow/deny + audit   │
   └─────────────────────────────────────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │  Notepad    │   │ Checkpoint  │   │  Provider   │
   │ (short-term)│   │ (disk resume) │   │ (Gemini/Stub)│
   └─────────────┘   └─────────────┘   └─────────────┘
```

**Key Boundaries:**
- **File I/O**: Only `projects/**` + `test.txt` (READ/APPEND) — all else denied
- **Shell**: Allowlist only (`pytest`, `python -m`, `dir`, `echo`) — no arbitrary commands
- **Network**: Only via `GeminiFreeProvider` to `generativelanguage.googleapis.com` with `GEMINI_API_KEY` from env
- **Code changes**: Forbidden during live run (Commit Gate LOCKED until `G3_FILE_IO_CLEAN_LIVE_PASS`)

**Evidence:** `config/settings.json` (gate, tools, provider sections), `AGENTS.md` rules 1-7, WO-03 "Commit Gate: LOCKED"

---

## Main Execution Flow

```text
python run.py [--stub] [--work-order PATH] [--settings PATH]
       │
       ▼
load_settings() → config/settings.json
       │
       ▼
load_work_order() → follows CURRENT_WORK_ORDER.md pointer if needed
       │
       ▼
parse_work_order() → Plan (goal + steps)
       │
       ▼
Gate(settings) → enforces allowlists/denylists
Tools(ROOT, gate) → bounded ops (read/write/run_shell/run_test under Gate)
Notepad() + Checkpoint(checkpoints/) → short-term + disk resume
Provider: StubProvider (--stub) OR GeminiFreeProvider (live, needs GEMINI_API_KEY)
       │
       ▼
run(plan, provider, tools, notepad, checkpoint, run_id, max_steps)
       │
       ├─► Step 1..max_steps: provider.complete(system, user) → tool calls → Gate → results
       │
       ├─► Stop conditions: max_steps, no_progress_3_steps, validation_passed
       │
       ▼
Terminal Status: TASK_DONE | BUDGET_EXHAUSTED | VALIDATION_FAILED | BLOCKED_ACTION | PROVIDER_ERROR | MALFORMED_RESPONSE
       │
       ▼
Write JSON report → logs/run_<run_id>.json
Exit code: 0 if TASK_DONE else 1
```

**Evidence:** `run.py` main(), `agent/loop.py` (run function), `agent/status.py` (Status enum), `agent/provider.py` (complete() contract)

---

## Persistence / State Boundaries

| State Type | Location | Lifetime | Scope |
|------------|----------|----------|-------|
| **Work Order** | `work_orders/*.md` | Persistent (git) | Long-term directive |
| **Current WO Pointer** | `work_orders/CURRENT_WORK_ORDER.md` | Persistent (git) | Active directive |
| **Settings** | `config/settings.json` | Persistent (git) | Runtime config |
| **Agent Output** | `projects/**` | Persistent (git, gated) | Work products |
| **Checkpoints** | `checkpoints/` | Persistent (gitignored) | Resume across restarts |
| **Run Reports** | `logs/run_*.json` | Persistent (gitignored) | Audit trail |
| **Notepad** | In-memory (per run) | Ephemeral | Step scratchpad |
| **Provider Credentials** | Process env (`GEMINI_API_KEY`) | Ephemeral (in-memory only) | Never persisted |

**Evidence:** `config/settings.json` (memory, logging), `agent/memory.py` (Notepad, Checkpoint), `run.py` (report writing), WO-03 "Credential masking: report booleans only"

---

## Safety / Validation Boundaries

| Boundary | Mechanism | Fail Behavior |
|----------|-----------|---------------|
| **File I/O** | `Gate.allow_file_op()` + glob/exact match | `BLOCKED_ACTION` status, op denied |
| **Shell** | `Gate.allow_shell()` + exact argv allowlist | `BLOCKED_ACTION` status |
| **Test** | `Gate.allow_test()` + pytest command | `BLOCKED_ACTION` status |
| **Step Budget** | `max_steps` (default 40) + `step_budget_per_run` | `BUDGET_EXHAUSTED` status |
| **Progress** | `no_progress_for_3_steps` detection | `VALIDATION_FAILED` status |
| **Commit Gate** | WO-03: LOCKED until `G3_FILE_IO_CLEAN_LIVE_PASS` | No git add/commit/push allowed |
| **Credential** | Env var only, masked in error messages | Never logged, never written to disk |

**Evidence:** `agent/gate.py` (allow_file_op, allow_shell, allow_test), `config/settings.json` (gate.stop_conditions), `AGENTS.md` rules 1-7, WO-03 sections 1, 5, 7

---

## Known Limitations

1. **No upstream branch** — `NO UPSTREAM` configured; all work on `integration/wave1-foundation` local branch
2. **36 dirty files** — Work order drafts, reports, JSON dumps, scratch files untracked
3. **6 deleted `projects/*` files** — Staged deletions from baseline freeze (Wave 0)
4. **No CodeGraph** — Explicitly deferred per `README.md` ("โค้ดยังเล็ก, ประโยชน์น้อยกว่าภาระ")
5. **Serena read-only** — Write tools excluded; cannot bypass Gate
6. **Single live run design** — WO-03: "Invocation Count = 1 | Retry = 0. Strict Single Run"
7. **No secret persistence** — `GEMINI_API_KEY` only in process env, loaded from User store at runtime

**Evidence:** Discovery script output, `git status`, `README.md`, WO-03

---

## Evidence Sources

| Source | Type | Verified At |
|--------|------|-------------|
| `AGENTS.md` | Authority file (canonical) | 2026-07-28 HEAD `099e516` |
| `config/settings.json` | Runtime config (staged) | 2026-07-28 HEAD `099e516` |
| `README.md` | Project documentation (modified) | 2026-07-28 HEAD `099e516` |
| `work_orders/CURRENT_WORK_ORDER.md` | Active WO pointer (modified) | 2026-07-28 HEAD `099e516` |
| `work_orders/03-WORK ORDER — G3 CLEAN LIVE RETEST (CREDENTIAL READY).md` | Current WO (untracked) | 2026-07-28 filesystem |
| `run.py` / `agent/*.py` | Source code (staged/modified) | 2026-07-28 HEAD `099e516` |
| Discovery script (`discover-project.ps1`) | Level 1 repo facts | 2026-07-28 exit 0 |

---

## Links

- Project page: [[llm-agents]]
- Architecture Index: [[Architecture Index]]
- Project Dashboard: [[Project Dashboard]]

---

**Last Verified:** 2026-07-28 (WO-OBSIDIAN-004) — Repository HEAD `099e516b2cf504d664d9cf12a40b722900ba7dde` on branch `integration/wave1-foundation`
**Verification Record:** WO-OBSIDIAN-004
**Evidence Classification:** All facts marked `VERIFIED_REPOSITORY_FACT` unless noted `SUPPORTED_INFERENCE`