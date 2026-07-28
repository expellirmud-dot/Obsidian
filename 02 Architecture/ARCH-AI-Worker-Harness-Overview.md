---
type: architecture
project: AI Worker Harness
last_reviewed: 2026-07-28
---

# Architecture Overview: AI Worker Harness

> สรุปจาก Repository `D:\ai-tools\ai-worker-harness` HEAD `7096991`

## ภาพรวมสถาปัตยกรรม

AI Worker Harness เป็น control plane แบบ bounded evidence-driven สำหรับรัน CLI coding Workers ภายใต้ Work Orders ที่ชัดเจน สถาปัตยกรรมแยกเป็น 4 บทบาทหลัก และใช้ Work Order lifecycle เป็นกลไกควบคุมการทำงาน

## Core Roles

### Controller
- Owns Goal/seam selection, architecture decisions, route selection
- Validates and activates Work Orders
- Reviews evidence and issues final disposition
- Stages and commits (only the two-commit lifecycle)
- Does NOT implement under Worker scope

### CLI Worker — Implementation Assistant
- Performs bounded exploration, implementation, validation, evidence collection
- Never selects Goal, expands scope, or makes material architecture decisions
- Never stages, commits, or pushes
- Assigned by Controller via Work Order

### Harness Worker — Evaluation Subject
- Runtime/provider-backed product evaluated by the Harness
- Runs only through canonical Harness entry point under Work Order
- May propose actions/terminal status but cannot own scope/authority/verdict

### Harness Runtime
- Tool registration and ToolGate enforcement
- Path/security boundaries, budgets, process isolation
- Event/audit collection and terminal-state translation
- Does not choose target architecture or widen scope

## Execution Model

```
Owner Goal authority
→ Controller selects one bounded seam
→ validated Work Order + active pointer
→ CLI Worker or Controller implements
→ Harness Worker evaluated when declared
→ deterministic evidence + Controller review
→ implementation/evidence + pointer closeout
→ next seam or final Goal disposition
```

## Work Order Lifecycle

1. **Audit** live state and select one bounded seam
2. **Generate & validate** complete Work Order before activation
3. **Commit** Work Order + active pointer (commit 1)
4. **Execute, validate, review**
5. **Commit** implementation/evidence + STATUS:NONE closeout (commit 2)
6. **Re-audit** and continue from active Goal

Two-commit lifecycle: 1) Work Order + pointer; 2) implementation/evidence + pointer closeout.

## Controller ↔ Worker Boundary

| Aspect | Controller | CLI Worker |
|--------|-----------|------------|
| Goal/Seam selection | ✅ Owns | ❌ Never |
| Architecture decisions | ✅ Owns | ❌ Never |
| Scope expansion | ✅ Authorizes | ❌ Never |
| Implementation | May delegate | ✅ Bounded scope |
| Evidence review | ✅ Owns | Collects only |
| Staging/Commit | ✅ Owns | ❌ Never |
| Route selection | ✅ Owns | Receives only |
| Final disposition | ✅ Issues | Proposes only |

## Provider / Route Boundary

- **config/models.json** owns route inventory
- **config/route_selection_policy.json** owns ranking and eligibility
- Current primary: `google-gemma-main`
- Fallback: `google-gemma-fallback`
- Provider mixing inside one task: FORBIDDEN
- Fresh route health required per important/costly run
- Historical PASS/connectivity does NOT qualify current task

## Validation and Evidence Flow

### Canonical Commands

```
.venv\Scripts\python.exe -m pytest .\tests -q -p no:cacheprovider --tb=short
.venv\Scripts\python.exe scripts\run_sandbox_validation.py
.venv\Scripts\python.exe scripts\show_routes.py
```

### Finding Classification

- **IMPLEMENTATION_DEFECT** — one corrective pass allowed within same root cause
- **EVALUATION_OUTCOME** — record and continue; do NOT patch toward PASS
- **TRANSIENT_ROUTE_FAILURE** — retry only when explicitly permitted
- **EVIDENCE_PIPELINE_FAILURE** — stop campaign; corrective pass if budget remains
- **MATERIAL_ARCHITECTURE_GAP** — close phase as not ready/inconclusive
- **OUT_OF_SCOPE_ADJACENT_DEFECT** — record without fixing

### Goal Completion (≠ Readiness)

| Disposition | Meaning |
|------------|---------|
| COMPLETE_READY | Evidence supports declared readiness gate |
| COMPLETE_NOT_READY | Evidence plan complete; readiness not established |
| COMPLETE_INCONCLUSIVE | Required conclusion cannot be drawn |
| BLOCKED_OWNER_DECISION | New authority required |

## Safety Mechanisms

- **ToolGate**: enforces allowed tool set per role/Work Order
- **Path/Security Boundaries**: restricts file system access
- **Budget Enforcement**: turns, tool calls, provider calls, retries, wall time
- **Process Isolation**: separates Harness Worker runtime from Controller
- **Event/Audit Collection**: terminal-state translation and settlement
- **Forbidden Actions**: no stage/commit/push by Worker, no provider mixing, no secret access

## Documentation Architecture

| Document | Owner of |
|----------|----------|
| AGENTS.md | Roles, safety, repository authority |
| docs/GOAL_EXECUTION_CONTRACT.md | Goal continuation and completion |
| docs/HARNESS_CURRENT_STATUS.md | Current verified state |
| docs/DOCS_INDEX.md | Document routing |
| work-order/CURRENT_WORK_ORDER.md | Active Work Order identity |
| work-order/Goal-*.md | Goal-specific scope and evidence plan |
| config/models.json | Route inventory |
| config/route_selection_policy.json | Route ranking and eligibility |

## Known Limitations

- No fresh complete-suite result for current HEAD (7096991)
- Goal-09 has not produced final readiness decision or task-class qualification matrix
- R07 live attempts 1–2 closed INCONCLUSIVE (evidence loss, settlement failure)
- R06 remains non-scoreable
- Production-default autonomous operation remains NOT_READY
- OpenHands bridge is read-only and optional (not production backend)
- Worktree: 1 modified + 3 untracked — must audit before execution

## Evidence Sources

- `D:\ai-tools\ai-worker-harness\AGENTS.md`
- `D:\ai-tools\ai-worker-harness\README.md`
- `D:\ai-tools\ai-worker-harness\work-order\CURRENT_WORK_ORDER.md`
- `D:\ai-tools\ai-worker-harness\docs\HARNESS_CURRENT_STATUS.md`
- `D:\ai-tools\ai-worker-harness\docs\GOAL_EXECUTION_CONTRACT.md`
- `D:\ai-tools\ai-worker-harness\docs\DOCS_INDEX.md`
- `D:\ai-tools\ai-worker-harness\work-order\Goal-09.md`

## Last Verified

- **HEAD:** `7096991892cead77a40c0178c57c9589839b1518`
- **Date:** 2026-07-28
- **By:** WO-OBSIDIAN-006
- **Evidence Classification:** VERIFIED_REPOSITORY_FACT (ยกเว้นที่ระบุ)

กลับไป [[AI Worker Harness]]
