# OpenHands Automation Runbook — Vault Truth Control Plane

Work Order ID: WO-OBSIDIAN-040
Title: WO-OBSIDIAN-040 — OpenHands Automation + End-to-End Validation
Risk Level: MEDIUM (scheduled automation, read-only source repos)
Task Classification: Vault Operational Tooling / Automation
Execution Mode: Bounded Single Work Order
Owner: Toto
Status: CLOSED

> CLOSED — freshness engine + targeted refresh implemented; 73/73 tests PASS;
> 6 end-to-end scenarios A-F proven; Automation A + B designs documented.

## 1. Architecture Implemented

```
┌─────────────────────────────────────────────────────────────────┐
│                   VAULT TRUTH CONTROL PLANE                     │
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐   │
│  │  Discovery   │──▶│  Onboarding  │──▶│  Project State   │   │
│  │  (WO-037)    │   │  (WO-037)    │   │  (v2, WO-036)    │   │
│  └──────┬───────┘   └──────────────┘   └────────┬─────────┘   │
│         │ read-only GitHub API                 │              │
│         ▼                                      ▼              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐   │
│  │  Evidence    │──▶│  Truth       │──▶│  Progress +      │   │
│  │  Collector   │   │  Builder     │   │  Next-Action     │   │
│  │  (WO-038)    │   │  (WO-038)    │   │  Engine (WO-039) │   │
│  └──────────────┘   └──────────────┘   └──────────────────┘   │
│         ▲                                      ▼              │
│         │           ┌──────────────┐    ┌──────────────────┐  │
│         └───────────│  Freshness   │◀───│  Live Project    │  │
│                     │  Engine      │    │  Wall (render)   │  │
│                     │  (WO-040)    │    │                  │  │
│                     └──────────────┘    └──────────────────┘  │
│                                                                 │
│  Automation A (6h): Discovery + Onboarding                     │
│  Automation B (1h): Freshness probe + Targeted Refresh         │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Files Changed (WO-036 → 040)

| File | WO | Purpose |
|------|----|---------|
| `automation/schema/project-state.v2.schema.json` | 036 | v2 schema (identity/execution/freshness/progress) |
| `automation/migrate_state_v2.py` | 036 | idempotent v1→v2 migration |
| `automation/discovery.py` | 037 | read-only GitHub discovery + reconcile + onboard |
| `automation/evidence_collector.py` | 038 | evidence collection (real content) + truth builder |
| `automation/progress_engine.py` | 039 | deterministic progress + next-action |
| `automation/freshness_engine.py` | 040 | freshness probe + targeted refresh + rollback |
| `automation/github_adapter.py` | 036 | updated for v2 nested structure |
| `scripts/render_project_wall.py` | 036 | v2 dashboard with new columns |
| `automation/state/*.yaml` | 036-039 | 11 files migrated to v2 + progress applied |
| `automation/projects.yaml` | 037 | stable repo IDs backfilled |
| `automation/evidence/*.yaml` | 038 | evidence manifests with provenance |
| `tests/conftest.py` | 036 | v2 schema + valid_state_dict |
| `tests/test_migrate_state_v2.py` | 036 | 8 migration tests |
| `tests/test_discovery.py` | 037 | 8 discovery tests |
| `tests/test_evidence_collector.py` | 038 | 8 evidence tests |
| `tests/test_progress_engine.py` | 039 | 10 progress tests |
| `tests/test_freshness_engine.py` | 040 | 28 freshness + e2e tests |

## 3. Automation A — Vault Repository Discovery

**Schedule:** every 6 hours, Asia/Bangkok (`0 */6 * * *`, timezone `Asia/Bangkok`)
**Type:** Prompt Preset (LLM-driven, because onboarding decisions + Project Overview authoring benefit from reasoning)

**Flow:**
```
GitHub repo inventory (read-only)
→ compare registry (stable repo ID)
→ process new / renamed / archived changes
→ auto-onboard eligible repos (needs-verification)
→ validate (schema)
→ render
→ tests
→ publish only if PASS
→ NO-OP if no change (no empty commit)
```

**Prompt:**
```
Run the Vault repository discovery automation:
1. Execute: python3 automation/discovery.py discover
2. Execute: python3 automation/discovery.py reconcile
3. For each new eligible repo, execute: python3 automation/discovery.py onboard --dry-run
   Review the proposed onboarding. If safe, execute without --dry-run.
4. Execute: python3 scripts/render_project_wall.py --validate-all
5. Execute: python3 -m pytest tests/ -q
6. If all PASS and there are Vault changes: git add -A && git commit && git push
   If NO change: do nothing (NO-OP, no empty commit).
7. Report: projects discovered, onboarded, fresh/stale/unknown counts.
Source repositories are READ-ONLY. Only mutate Vault files.
```

## 4. Automation B — Vault Project Truth Refresh

**Schedule:** every 1 hour, Asia/Bangkok (`0 * * * *`, timezone `Asia/Bangkok`)
**Type:** Prompt Preset

**Flow:**
```
Lightweight freshness probe (all projects)
  compare remote_head vs truth_built_from_head
  if equal → FRESH (skip, no deep work)
  if different → STALE → targeted refresh:
    → collect evidence
    → rebuild truth (identity + execution, drift-aware)
    → recompute progress + next-action
    → schema validate
    → if FAIL: restore previous good state, mark refresh_failed
    → if PASS: publish
  if GitHub unreachable → UNKNOWN (never FRESH)
→ render
→ idempotency test (render twice)
→ regression tests
→ publish only if all PASS
→ NO-OP if no change
```

**Prompt:**
```
Run the Vault project truth refresh automation:
1. Execute: python3 automation/freshness_engine.py probe --all
   Review the fresh/stale/unknown summary.
2. Execute: python3 automation/freshness_engine.py refresh --all
   This does targeted refresh of STALE projects only. FRESH projects are skipped.
   REFRESH_FAILED projects keep their previous good state.
3. Execute: python3 scripts/render_project_wall.py --validate-all
4. Execute: python3 scripts/render_project_wall.py  (render twice for idempotency)
5. Execute: python3 -m pytest tests/ -q
6. If all PASS and there are Vault changes: git add -A && git commit && git push
   If NO change: NO-OP (no empty commit).
7. Report: fresh/stale/unknown/refresh_failed counts, projects refreshed.
Source repositories are READ-ONLY. Never publish partial truth.
```

## 5. Freshness Safety Contract (enforced)

| Condition | Status | Action |
|-----------|--------|--------|
| `remote_head == truth_built_from_head` | FRESH | skip (no deep refresh) |
| `remote_head != truth_built_from_head` | STALE | targeted deep refresh |
| GitHub unreachable / head unresolvable | UNKNOWN | never becomes FRESH |
| refresh raises / schema invalid | REFRESH_FAILED | restore previous good state |
| old verified truth | kept | marked stale (not deleted) |

## 6. Tests (73 total, all PASS)

| Suite | Count | Covers |
|-------|-------|--------|
| test_render_project_wall.py | 11 | v2 rendering, dashboard columns |
| test_migrate_state_v2.py | 8 | v1→v2 migration, idempotency |
| test_discovery.py | 8 | discover, idempotent onboard, rename, exclude, no-fabrication |
| test_evidence_collector.py | 8 | content-not-filename, provenance, drift, no-fabrication |
| test_progress_engine.py | 10 | weighted, bounded, unknown, next-action, deterministic, write-path |
| test_freshness_engine.py | 28 | freshness contract, rollback, e2e scenarios A-F |

## 7. End-to-End Scenarios Proven

| Scenario | Description | Result |
|----------|-------------|--------|
| A | Existing fresh project (HEAD unchanged) | FRESH, no deep refresh, no churn ✅ |
| B | Existing project changed (new HEAD) | STALE → targeted refresh → FRESH ✅ |
| C | Brand-new repository | DISCOVERED → onboard → state ✅ |
| D | Ambiguous project (no evidence) | needs-verification, mission unknown ✅ |
| E | Misleading latest work order | Mission=A, Work=B (not rewritten) ✅ |
| F | Progress with/without denominator | evidence-based % / UNKNOWN ✅ |

## 8. Live Probe Results (read-only, against expellirmud-dot)

- fresh: 3 (lumina-studio, citizen_portal, TalkToClibord)
- stale: 3 (Utility-Disbursement-App, lightroom-ai-exposure, AI-Workspace)
- unknown: 5 (thai_stt_app, llm-agents, STT-Typing, AI-Worker-Harness, Adobe-Stock)
- refresh_failed: 0

## 9. Token Scope Limitation (known)

The GITHUB_TOKEN in this environment can access:
- `/repos/{owner}/{repo}` (metadata) ✅
- `/users/{account}/repos` + `/user/repos` (discovery) ✅
- `/repos/{owner}/{repo}/contents/{path}` (file content) ✅

It CANNOT access `/commits`, `/git/trees`, `/branches` (403 "Resource not accessible by integration").
Impact:
- Some repos' remote HEAD cannot be resolved → UNKNOWN (fail-safe, never FRESH)
- Provenance is bound to ref + blob SHAs (commit SHA null, honest)
- The freshness contract holds: UNKNOWN never becomes FRESH

## 10. Proof of No Source-Repository Mutation

All modules use only HTTP GET (read-only):
- `discovery.py`: `ALLOWED_METHOD = "GET"`
- `evidence_collector.py`: `ALLOWED_METHOD = "GET"`
- `freshness_engine.py`: `method="GET"`
- `github_adapter.py`: read-only

No POST/PATCH/PUT/DELETE to any source repository. Only Vault files (`automation/state/`, `automation/evidence/`, `automation/projects.yaml`, rendered dashboard) are mutated.

## 11. Final Acceptance (15 criteria)

1. ✅ Project นี้คืออะไร → `project_identity.purpose`
2. ✅ สร้างขึ้นมาเพื่อแก้ปัญหาอะไร → `project_identity.problem_statement`
3. ✅ เป้าหมายปลายทาง → `project_identity.intended_outcome`
4. ✅ ตอนนี้อยู่ phase ไหน → `current_execution.lifecycle_phase`
5. ✅ สิ่งใดเสร็จแล้ว → `current_execution.last_completed` + progress.completed
6. ✅ สิ่งใดกำลังทำ → `current_execution.current_work`
7. ✅ อ้างอิง repository HEAD ใด → `freshness.truth_built_from_head`
8. ✅ fresh หรือ stale → `freshness.status`
9. ✅ progress ของ roadmap/current goal → `progress.estimate` + `progress.basis`
10. ✅ confidence ของ progress → `progress.confidence`
11. ✅ blocker ปัจจุบัน → `current_execution.blockers`
12. ✅ next authoritative action → `current_execution.next_action`
13. ✅ repository ใหม่เข้า Vault อัตโนมัติ → discovery + onboard (WO-037)
14. ✅ repository ที่เปลี่ยน refresh แบบ targeted → freshness engine (WO-040)
15. ✅ failure ไม่แทนที่ verified truth → rollback + refresh_failed (tested)

## 12. Definition of Done

- [x] freshness engine (probe + targeted refresh + rollback)
- [x] Automation A design (discovery, 6h)
- [x] Automation B design (refresh, 1h)
- [x] 20 required tests + 6 e2e scenarios (73 total, all PASS)
- [x] no source repository mutation (GET only)
- [x] Freshness Safety Contract enforced
- [x] Final acceptance 15/15
