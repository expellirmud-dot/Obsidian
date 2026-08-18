# OpenHands Automation Runbook вҖ” Vault Truth Control Plane

Work Order ID: WO-OBSIDIAN-040
Title: WO-OBSIDIAN-040 вҖ” OpenHands Automation + End-to-End Validation
Risk Level: MEDIUM (scheduled automation, read-only source repos)
Task Classification: Vault Operational Tooling / Automation
Execution Mode: Bounded Single Work Order
Owner: Toto
Status: CLOSED

> CLOSED вҖ” freshness engine + targeted refresh implemented; 73/73 tests PASS;
> 6 end-to-end scenarios A-F proven; Automation A + B designs documented.

## 1. Architecture Implemented

```
в”Ңв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”җ
в”Ӯ                   VAULT TRUTH CONTROL PLANE                     в”Ӯ
в”Ӯ                                                                 в”Ӯ
в”Ӯ  в”Ңв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”җ   в”Ңв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”җ   в”Ңв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”җ   в”Ӯ
в”Ӯ  в”Ӯ  Discovery   в”Ӯв”Җв”Җв–¶в”Ӯ  Onboarding  в”Ӯв”Җв”Җв–¶в”Ӯ  Project State   в”Ӯ   в”Ӯ
в”Ӯ  в”Ӯ  (WO-037)    в”Ӯ   в”Ӯ  (WO-037)    в”Ӯ   в”Ӯ  (v2, WO-036)    в”Ӯ   в”Ӯ
в”Ӯ  в””в”Җв”Җв”Җв”Җв”Җв”Җв”¬в”Җв”Җв”Җв”Җв”Җв”Җв”Җв”ҳ   в””в”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”ҳ   в””в”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”¬в”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”ҳ   в”Ӯ
в”Ӯ         в”Ӯ read-only GitHub API                 в”Ӯ              в”Ӯ
в”Ӯ         в–ј                                      в–ј              в”Ӯ
в”Ӯ  в”Ңв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”җ   в”Ңв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”җ   в”Ңв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”җ   в”Ӯ
в”Ӯ  в”Ӯ  Evidence    в”Ӯв”Җв”Җв–¶в”Ӯ  Truth       в”Ӯв”Җв”Җв–¶в”Ӯ  Progress +      в”Ӯ   в”Ӯ
в”Ӯ  в”Ӯ  Collector   в”Ӯ   в”Ӯ  Builder     в”Ӯ   в”Ӯ  Next-Action     в”Ӯ   в”Ӯ
в”Ӯ  в”Ӯ  (WO-038)    в”Ӯ   в”Ӯ  (WO-038)    в”Ӯ   в”Ӯ  Engine (WO-039) в”Ӯ   в”Ӯ
в”Ӯ  в””в”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”ҳ   в””в”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”ҳ   в””в”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”ҳ   в”Ӯ
в”Ӯ         в–І                                      в–ј              в”Ӯ
в”Ӯ         в”Ӯ           в”Ңв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”җ    в”Ңв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”җ  в”Ӯ
в”Ӯ         в””в”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Ӯ  Freshness   в”Ӯв—Җв”Җв”Җв”Җв”Ӯ  Live Project    в”Ӯ  в”Ӯ
в”Ӯ                     в”Ӯ  Engine      в”Ӯ    в”Ӯ  Wall (render)   в”Ӯ  в”Ӯ
в”Ӯ                     в”Ӯ  (WO-040)    в”Ӯ    в”Ӯ                  в”Ӯ  в”Ӯ
в”Ӯ                     в””в”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”ҳ    в””в”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”ҳ  в”Ӯ
в”Ӯ                                                                 в”Ӯ
в”Ӯ  Automation A (6h): Discovery + Onboarding                     в”Ӯ
в”Ӯ  Automation B (1h): Freshness probe + Targeted Refresh         в”Ӯ
в””в”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”ҳ
```

## 2. Files Changed (WO-036 вҶ’ 040)

| File | WO | Purpose |
|------|----|---------|
| `automation/schema/project-state.v2.schema.json` | 036 | v2 schema (identity/execution/freshness/progress) |
| `automation/migrate_state_v2.py` | 036 | idempotent v1вҶ’v2 migration |
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

## 3. Automation A вҖ” Vault Repository Discovery

**Schedule:** every 6 hours, Asia/Bangkok (`0 */6 * * *`, timezone `Asia/Bangkok`)
**Type:** Prompt Preset (LLM-driven, because onboarding decisions + Project Overview authoring benefit from reasoning)

**Flow:**
```
GitHub repo inventory (read-only)
вҶ’ compare registry (stable repo ID)
вҶ’ process new / renamed / archived changes
вҶ’ auto-onboard eligible repos (needs-verification)
вҶ’ validate (schema)
вҶ’ render
вҶ’ tests
вҶ’ publish only if PASS
вҶ’ NO-OP if no change (no empty commit)
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
6. If all PASS and there are Vault changes, use EXPLICIT staging (WO-041 F7):
   git status
   → identify exact changed Vault paths (automation/state/, automation/evidence/,
     automation/projects.yaml, 00 Dashboard/, 01 Projects/, 04 Work Orders/)
   → git diff <each changed path>
   → git add <explicit paths>  (NEVER `git add .` or `git add -A`)
   → git diff --cached  (inspect staged diff)
   → git commit && git push
   If NO change: do nothing (NO-OP, no empty commit).
7. Report: projects discovered, onboarded, fresh/stale/unknown counts.
Source repositories are READ-ONLY. Only mutate Vault files.
```

## 4. Automation B вҖ” Vault Project Truth Refresh

**Schedule:** every 1 hour, Asia/Bangkok (`0 * * * *`, timezone `Asia/Bangkok`)
**Type:** Prompt Preset

**Flow:**
```
Lightweight freshness probe (all projects)
  compare remote_head vs truth_built_from_head
  if equal вҶ’ FRESH (skip, no deep work)
  if different вҶ’ STALE вҶ’ targeted refresh:
    вҶ’ collect evidence
    вҶ’ rebuild truth (identity + execution, drift-aware)
    вҶ’ recompute progress + next-action
    вҶ’ schema validate
    вҶ’ if FAIL: restore previous good state, mark refresh_failed
    вҶ’ if PASS: publish
  if GitHub unreachable вҶ’ UNKNOWN (never FRESH)
вҶ’ render
вҶ’ idempotency test (render twice)
вҶ’ regression tests
вҶ’ publish only if all PASS
вҶ’ NO-OP if no change
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
6. If all PASS and there are Vault changes, use EXPLICIT staging (WO-041 F7):
   git status
   → identify exact changed Vault paths (automation/state/, automation/evidence/,
     automation/projects.yaml, 00 Dashboard/, 01 Projects/, 04 Work Orders/)
   → git diff <each changed path>
   → git add <explicit paths>  (NEVER `git add .` or `git add -A`)
   → git diff --cached  (inspect staged diff)
   → git commit && git push
   If NO change: NO-OP (no empty commit).
7. Report: fresh/stale/unknown/refresh_failed counts, projects refreshed.
Source repositories are READ-ONLY. Never publish partial truth.
```

## 3b. Git Safety (WO-041 F7)

Automation A/B use **EXPLICIT path staging only**. `git add .` and `git add -A`
are **FORBIDDEN** — they stage stray files (`.base`, `.pytest_cache/`, untitled
notes) into automated commits. The required flow is:

```
git status
→ identify exact changed Vault paths
→ git diff <each path>
→ validation (schema + renderer + tests already run above)
→ git add <explicit paths>  (NEVER git add . / git add -A)
→ git diff --cached  (inspect staged diff)
→ git commit
→ git push
```

## 3c. Freshness Safety Contract Hardening (WO-041 F2)

WO-041 corrected the false-freshness bug: aggregate `status="fresh"` now
requires ALL THREE sub-gates (source_freshness, semantic_freshness,
progress_freshness) to be fresh. A known remote HEAD with unavailable evidence
no longer produces semantic FRESH. Evidence-collection failure (manifest
status != "ok") → semantic_freshness/progress_freshness = "unknown" →
aggregate = "unknown" (never FRESH). Failed refresh preserves the previous
verified identity + truth_built_from_head (rollback).

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
| test_migrate_state_v2.py | 8 | v1вҶ’v2 migration, idempotency |
| test_discovery.py | 8 | discover, idempotent onboard, rename, exclude, no-fabrication |
| test_evidence_collector.py | 8 | content-not-filename, provenance, drift, no-fabrication |
| test_progress_engine.py | 10 | weighted, bounded, unknown, next-action, deterministic, write-path |
| test_freshness_engine.py | 28 | freshness contract, rollback, e2e scenarios A-F |

## 7. End-to-End Scenarios Proven

| Scenario | Description | Result |
|----------|-------------|--------|
| A | Existing fresh project (HEAD unchanged) | FRESH, no deep refresh, no churn вң… |
| B | Existing project changed (new HEAD) | STALE вҶ’ targeted refresh вҶ’ FRESH вң… |
| C | Brand-new repository | DISCOVERED вҶ’ onboard вҶ’ state вң… |
| D | Ambiguous project (no evidence) | needs-verification, mission unknown вң… |
| E | Misleading latest work order | Mission=A, Work=B (not rewritten) вң… |
| F | Progress with/without denominator | evidence-based % / UNKNOWN вң… |

## 8. Live Probe Results (read-only, against expellirmud-dot)

- fresh: 3 (lumina-studio, citizen_portal, TalkToClibord)
- stale: 3 (Utility-Disbursement-App, lightroom-ai-exposure, AI-Workspace)
- unknown: 5 (thai_stt_app, llm-agents, STT-Typing, AI-Worker-Harness, Adobe-Stock)
- refresh_failed: 0

## 9. Token Scope Limitation (known)

The GITHUB_TOKEN in this environment can access:
- `/repos/{owner}/{repo}` (metadata) вң…
- `/users/{account}/repos` + `/user/repos` (discovery) вң…
- `/repos/{owner}/{repo}/contents/{path}` (file content) вң…

It CANNOT access `/commits`, `/git/trees`, `/branches` (403 "Resource not accessible by integration").
Impact:
- Some repos' remote HEAD cannot be resolved вҶ’ UNKNOWN (fail-safe, never FRESH)
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

1. вң… Project аёҷаёөа№үаё„аё·аёӯаёӯаё°а№„аёЈ вҶ’ `project_identity.purpose`
2. вң… аёӘаёЈа№үаёІаёҮаёӮаё¶а№үаёҷаёЎаёІа№Җаёһаё·а№Ҳаёӯа№ҒаёҒа№үаёӣаёұаёҚаё«аёІаёӯаё°а№„аёЈ вҶ’ `project_identity.problem_statement`
3. вң… а№Җаёӣа№үаёІаё«аёЎаёІаёўаёӣаёҘаёІаёўаё—аёІаёҮ вҶ’ `project_identity.intended_outcome`
4. вң… аё•аёӯаёҷаёҷаёөа№үаёӯаёўаё№а№Ҳ phase а№„аё«аёҷ вҶ’ `current_execution.lifecycle_phase`
5. вң… аёӘаёҙа№ҲаёҮа№ғаё”а№ҖаёӘаёЈа№ҮаёҲа№ҒаёҘа№үаё§ вҶ’ `current_execution.last_completed` + progress.completed
6. вң… аёӘаёҙа№ҲаёҮа№ғаё”аёҒаёіаёҘаёұаёҮаё—аёі вҶ’ `current_execution.current_work`
7. вң… аёӯа№үаёІаёҮаёӯаёҙаёҮ repository HEAD а№ғаё” вҶ’ `freshness.truth_built_from_head`
8. вң… fresh аё«аёЈаё·аёӯ stale вҶ’ `freshness.status`
9. вң… progress аёӮаёӯаёҮ roadmap/current goal вҶ’ `progress.estimate` + `progress.basis`
10. вң… confidence аёӮаёӯаёҮ progress вҶ’ `progress.confidence`
11. вң… blocker аёӣаёұаёҲаёҲаёёаёҡаёұаёҷ вҶ’ `current_execution.blockers`
12. вң… next authoritative action вҶ’ `current_execution.next_action`
13. вң… repository а№ғаё«аёЎа№Ҳа№ҖаёӮа№үаёІ Vault аёӯаёұаё•а№ӮаёҷаёЎаёұаё•аёҙ вҶ’ discovery + onboard (WO-037)
14. вң… repository аё—аёөа№Ҳа№ҖаёӣаёҘаёөа№Ҳаёўаёҷ refresh а№Ғаёҡаёҡ targeted вҶ’ freshness engine (WO-040)
15. вң… failure а№„аёЎа№Ҳа№Ғаё—аёҷаё—аёөа№Ҳ verified truth вҶ’ rollback + refresh_failed (tested)

## 12. Definition of Done

- [x] freshness engine (probe + targeted refresh + rollback)
- [x] Automation A design (discovery, 6h)
- [x] Automation B design (refresh, 1h)
- [x] 20 required tests + 6 e2e scenarios (73 total, all PASS)
- [x] no source repository mutation (GET only)
- [x] Freshness Safety Contract enforced
- [x] Final acceptance 15/15
