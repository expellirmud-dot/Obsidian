# WORK ORDER — TRUTH CONTROL PLANE CORRECTNESS HARDENING

Work Order ID: WO-OBSIDIAN-041
Title: WO-OBSIDIAN-041 — Truth Control Plane Correctness Hardening
Risk Level: MEDIUM (corrective hardening of WO-036–040 truth layer; no source repo mutation)
Task Classification: Vault Operational Tooling / Truth Layer Correctness
Execution Mode: Bounded Single Work Order (MANDATORY PARALLEL MULTI-AGENT)
Owner: Toto
Target Vault: `D:\Obsidian\Project-Knowledge-Vault`
Status: CLOSED

> CLOSED — corrective hardening of the Truth Control Plane built in WO-036–040.
> Principle: CORRECTNESS > FEATURE COUNT. UNKNOWN is better than fabricated truth.
> No claim is preserved merely because a prior Work Order marked it PASS.
>
> All 14 findings (F1–F14) accepted across 4 independent review rounds.
> Final independent owner review: PASS. Ready for merge.

## 1. Objective

ทำ corrective hardening ของ Truth Control Plane ที่สร้างใน WO-036–040 ให้:

PROJECT TRUTH, FRESHNESS, MISSION, PROGRESS, ONBOARDING, ACCEPTANCE CLAIMS
ตรงกับ implementation และ evidence จริง

หลักสำคัญ:
- CORRECTNESS > FEATURE COUNT
- UNKNOWN ดีกว่า fabricated truth
- ห้ามรักษา claim เดิมไว้เพียงเพราะ Work Order ก่อนหน้าระบุว่า PASS

## 2. Baseline (verified against origin/main)

- origin/main SHA: `26caeaefca03aa61f030c5c6d277b9616332c1c9` (merge of PR #2)
- PR #1 (fix/health-check-issues-2026-08-15): merged
- PR #2 (feat: integrate WO-036–040 truth control plane): merged
- Working tree: clean
- Branch: `wo-041-truth-correctness-hardening` (from origin/main)
- Baseline tests: 73 passed
- Baseline schema validation: 11/11 VALID
- Baseline renderer validation: 11/11 VALID

## 3. Mandatory Findings to Resolve (7)

### F1 — PROJECT NAME != PROJECT MISSION (P1)

Project Name, Repository Name, Document Heading, Current Goal, Latest Work Order
แต่ละอย่างเพียงอย่างเดียวห้ามทำให้ `knowledge_state = verified` หรือถือเป็น semantic Mission.

`purpose` ต้องมี meaningful evidence จริง (explicit Purpose/Mission/Problem text).
หาก evidence ไม่พอ → `purpose = null`, `knowledge_state = needs-verification`
(หรือ preserve previous verified truth ตาม context).

Root cause (preliminary, to be confirmed by audit):
- `evidence_collector.py` build_identity_from_evidence ใช้ `heading or para` เป็น purpose
  โดย heading คือ first H1/H2 (เช่น "# Thai STT App" → "Thai STT App")
- `has_identity_evidence` เช็คแค่ `category == "identity" and heading` → verified
- `migrate_state_v2.py` seed `purpose = project_name`

Required tests:
- test_project_title_alone_does_not_verify_mission
- test_repository_name_alone_does_not_verify_mission
- test_explicit_purpose_text_can_verify_mission
- test_current_work_does_not_become_project_mission

### F2 — FALSE FRESHNESS / PARTIAL TRUTH (P1)

ห้าม: remote_head known + evidence unavailable = FRESH.
ต้องแยก source_freshness / semantic_freshness / progress_freshness.
Aggregate FRESH ต้องไม่เกิดเมื่อ semantic evidence rebuild ไม่สำเร็จ.

Root cause (preliminary):
- `freshness_engine.py` deep-refresh path ตั้ง semantic_freshness/progress_freshness = "fresh"
  เมื่อ remote_head available โดยไม่ตรวจ manifest status / identity evidence
- `classify_freshness` model แค่ source freshness ไม่ model semantic freshness

Required tests:
- test_remote_head_known_but_evidence_unavailable_not_fresh
- test_no_evidence_does_not_publish_fresh_semantic_truth
- test_failed_semantic_refresh_preserves_previous_verified_identity
- test_unknown_semantic_freshness_prevents_aggregate_fresh
- test_refresh_failure_never_publishes_partial_truth

### F3 — ACCEPTANCE OVERCLAIM (P1)

ตรวจ WO-036–040 ทุก claim. การมี field ใน schema != extractor รองรับ.
เลือก: A. implement evidence-backed + tests หรือ B. downgrade เป็น unsupported/unknown.

Root cause (preliminary):
- WO-038 claims identity filled from evidence แต่ build_identity กรอกแค่ `purpose`
  (6 ฟิลด์เป็น null เสมอ: problem_statement, intended_outcome, primary_users,
   success_definition, scope, non_goals) → schema-supported-but-not-derived
- WO-039 claims "bounded work-order set" เป็น method 3 แต่ไม่ implement

### F4 — MISSION DRIFT PROVENANCE (P2)

เมื่อ authoritative evidence บ่งชี้ Mission ใหม่ ต้องเก็บ:
OLD VERIFIED IDENTITY, CANDIDATE NEW IDENTITY, EVIDENCE PROVENANCE ของ candidate
และห้าม overwrite old identity อัตโนมัติ.

Root cause (preliminary):
- `evidence_collector.py` drift path เก็บแค่ previous_identity (old) ไม่เก็บ candidate
  หรือ provenance ของ candidate → ตรวจ candidate mission ไม่ได้

Required tests:
- test_mission_drift_preserves_old_identity
- test_mission_drift_records_candidate_identity
- test_mission_drift_candidate_has_evidence_provenance
- test_mission_drift_does_not_silently_overwrite_verified_identity

### F5 — PROGRESS CORRECTNESS (P2)

Progress ห้ามมาจาก LLM impression. รองรับ method ไหนจริงให้ระบุให้ตรง:
weighted milestones, bounded milestones, phase goals, bounded work orders.
แต่ละ method: IMPLEMENTED + TESTED หรือ UNSUPPORTED → UNKNOWN.
ตรวจ content truncation. ห้ามใช้ partial roadmap checklist เป็น denominator ทั้งหมด.

Root cause (preliminary):
- `progress_engine.py` parse milestones จาก content_excerpt (500 chars truncated)
  → partial roadmap → false percentage
- phase/goal และ bounded work-order methods ไม่ implement แต่ WO-039 claim

Required tests:
- test_truncated_roadmap_does_not_produce_false_percentage
- test_complete_bounded_roadmap_produces_deterministic_percentage
- test_missing_denominator_is_unknown

### F6 — ATOMIC / REPAIRABLE ONBOARDING (P2)

ป้องกัน: write state → projects.yaml fail → overview fail → partial project เหลือ.
Onboarding ต้อง: no duplicate, no silent partial, repairable rerun,
schema valid before publication, stable repo ID aware.

Root cause (preliminary):
- `discovery.py` onboard_project เขียน state → projects.yaml → overview ตามลำดับ
  ไม่มี staging/transaction/rollback; crash กลางทาง → partial registration
- rerun เจอ state_exists → return ไม่ repair registry

Required tests:
- test_onboarding_failure_does_not_leave_partial_registration
- test_onboarding_rerun_repairs_incomplete_state
- test_onboarding_is_idempotent_after_success
- test_onboarding_never_duplicates_project_by_stable_repo_id

### F7 — AUTOMATION GIT SAFETY

แก้ Automation A/B ถ้ามี `git add .` / `git add -A` ให้เป็น explicit staging.
Flow: git status → identify exact changed paths → git diff → validation →
stage explicit paths → inspect staged diff → commit. ห้าม stage unrelated.

Root cause (preliminary):
- WO-040 Automation A prompt: `git add -A && git commit && git push`
- WO-040 Automation B prompt: `git add -A && git commit && git push`

## 4. Execution Mode — MANDATORY PARALLEL MULTI-AGENT

Main Agent = Controller / Integrator. ห้ามทำทุก finding เองแบบ sequential.

### Wave 1 — Parallel Read-Only Audit (5 agents: A, B, C, D, E)
### Wave 1 Reconciliation (Main Agent)
### Wave 2 — Parallel Implementation (Implementer A, B, C, D, E)
### Wave 3 — Main Agent Integration (shared files only)
### Wave 4 — Parallel Independent Review (3 reviewers)
### Review Reconciliation
### Final Acceptance + Delivery

### Shared-file ownership (Main Agent only)
- automation/schema/project-state.v2.schema.json
- automation/migrate_state_v2.py
- automation/state/*.yaml, automation/evidence/*.yaml
- WO-036–040 + WO-041 + Work Order Index
- automation/state/README.md

### Sub-agent rules
- ห้าม commit/push/merge/change branch/force push
- ห้ามแก้ไฟล์นอก ownership
- ห้ามปิด WO / ประกาศ final PASS
- Report: FILES_INSPECTED, FILES_CHANGED, FINDINGS, TESTS_ADDED, TESTS_EXECUTED, UNRESOLVED, RISKS

## 5. Validation Gate

- `python3 automation/migrate_state_v2.py --validate` → ทุก state VALID
- `python3 scripts/render_project_wall.py --validate-all` → ทุก state VALID
- `python3 scripts/render_project_wall.py` → render; second render zero semantic diff
- `python3 -m pytest tests/ -q` → FAILED = 0 (report actual count; อย่า hard-code 73)
- `git diff --check` / `git status` / `git diff` → scope check

## 6. Final Acceptance

WO-041 CLOSED ได้ต่อเมื่อ (see FINAL ACCEPTANCE checklist in task prompt):
ทุกข้อผ่าน รวม independent reviewers resolved.

## 7. Closeout Reconciliation

ตาราง: | Finding | Before | Fix | Test Evidence | Reviewer | Final |
ต้องมี F1–F7; expected findings=7, resolved=7, unresolved=0.

## 8. Delivery

- Commit: `fix: harden project truth correctness (WO-041)`
- Push: `wo-041-truth-correctness-hardening`
- PR เข้า main (DO NOT MERGE)
- PR body: root causes, 7 findings reconciliation, sub-agent evidence, files changed,
  schema impact, validation commands, actual test count, renderer/idempotency,
  known limitations, branch HEAD SHA, origin/main baseline SHA, reviewer results

## 9. Forbidden

git add . / git add -A / git clean / git reset --hard / force push / history rewrite /
merge PR / แก้ source repositories / เปลี่ยน Mission จาก inference / สร้าง progress % จาก impression /
ซ่อน UNKNOWN / เปลี่ยน failed evidence เป็น VERIFIED/FRESH / เพิ่ม secret / แก้ unrelated files /
ให้ Sub-agent commit/push

## 10. Stop Conditions

baseline dirty โดยไม่รู้ที่มา / origin/main reconciliation มีปัญหา / schema migration data loss risk /
verified Mission อาจถูก overwrite โดยไม่มี evidence / correction ต้อง mutate source repo /
tests fail โดย root cause ยังไม่ทราบ / diff หลุด scope / parallel sub-agent unavailable /
unresolved P1 correctness finding / secret ปรากฏ / ต้อง force push

หาก STOP: ห้าม commit/push partial solution; รายงาน evidence + blocker ตามจริง

## 11. Closeout Reconciliation

| Finding | Before | Fix | Test Evidence | Reviewer | Final |
|---------|--------|-----|---------------|----------|-------|
| F1 Mission Verification | heading/project_name → purpose + verified | `_extract_explicit_purpose` requires explicit Purpose/Mission/Problem text; `knowledge_state=verified` requires `purpose is not None`; migrator no longer seeds purpose from project_name | 4 tests (test_evidence_collector) + 1 refresh-path regression (test_freshness_engine) | R1b PASS | RESOLVED |
| F2 Freshness Publication | remote_head known → all gates fresh | `semantic_freshness_for`/`progress_freshness_for` gate on manifest status; `_aggregate_freshness` requires all 3 gates fresh; publication gate rolls back on manifest ≠ ok | 6 tests (test_freshness_engine) | R2 PASS | RESOLVED |
| F3 Acceptance Overclaim | "fills identity from evidence"; bounded work-orders supported | WO-036/038/039 banners + DoD corrected; 6 fields marked schema-supported-but-not-derived; bounded work-orders + phase/goal marked UNSUPPORTED | Doc corrections (WO-036/038/039/040, state README, Work Order Index) | R3 PASS | RESOLVED |
| F4 Mission Drift Provenance | candidate discarded; no provenance; no reset | `candidate_identity` + `candidate_identity_provenance` (path/ref/blob_sha/observed_at) recorded on drift; reset to None each cycle; old identity preserved | 4 tests (test_evidence_collector) + 2 refresh-path regression (test_freshness_engine) | R1b PASS | RESOLVED |
| F5 Progress Correctness | truncated roadmap → false % | truncation gate (`content_length > 500` → UNKNOWN); finditer fallback for newline-stripped excerpts; unsupported methods stay UNKNOWN | 14 tests (test_progress_engine) | R3 PASS | RESOLVED |
| F6 Atomic Onboarding | sequential writes; `'w'` mode; state-only idempotency | `_atomic_write_registry` (temp+os.replace); completeness-aware idempotency (state+registry+overview); `_repair_onboarding`; stable-repo-id duplicate prevention | 5 tests (test_discovery) | R2 PASS | RESOLVED |
| F7 Git Automation Safety | `git add -A` in Automation A/B | explicit path staging flow; `git add .`/`git add -A` forbidden; Git Safety section added | WO-040 doc corrections | R3 PASS | RESOLVED |

Expected findings: 7
Resolved: 7
Unresolved: 0

## 12. Final Acceptance

- [x] Project title alone cannot verify Mission
- [x] repository name alone cannot verify Mission
- [x] Current Work cannot become Project Mission
- [x] knowledge_state=verified requires semantic evidence
- [x] failed evidence refresh cannot produce semantic FRESH
- [x] aggregate FRESH requires required freshness gates
- [x] known-good identity survives failed refresh
- [x] mission drift preserves old identity
- [x] candidate mission + provenance inspectable
- [x] incomplete denominator cannot generate percentage
- [x] unsupported progress methods become UNKNOWN
- [x] onboarding cannot silently leave broken partial registration
- [x] rerun can repair interrupted onboarding
- [x] successful onboarding is idempotent
- [x] no broad git staging in Automation A/B
- [x] WO-036–040 claims match implementation
- [x] schema validation PASS (11/11 VALID)
- [x] renderer validation PASS
- [x] render idempotency PASS (zero diff on second render)
- [x] full tests PASS (109 passed, 0 failed)
- [x] diff-check PASS
- [x] no source repository mutation
- [x] no secrets
- [x] no out-of-scope changes
- [x] all independent reviewers resolved

## 13. Delivery

- Branch: `wo-041-truth-correctness-hardening`
- Branch HEAD SHA: `17b813c14be03c1777cd082811a547f50ab57b73`
- origin/main baseline SHA: `26caeaefca03aa61f030c5c6d277b9616332c1c9`
- PR: #3 (https://github.com/expellirmud-dot/Obsidian/pull/3)
- Commit: `fix: harden project truth correctness (WO-041)`
- DO NOT MERGE — awaiting independent owner review

## 14. Sub-Agent Execution Evidence

Wave 1 — Parallel Read-Only Audit (5 agents):
- Agent A (Mission/Identity/Evidence): confirmed F1/F4 root causes
- Agent B (Freshness/Publication): confirmed F2 root cause
- Agent C (Progress): confirmed F5 root cause + truncation
- Agent D (Discovery/Onboarding): confirmed F6 root cause
- Agent E (Governance/Claims): confirmed F3/F7 overclaims

Wave 2 — Parallel Implementation (5 agents):
- Implementer A: F1 + identity-F3 + F4 in evidence_collector.py (8 new tests)
- Implementer B: F2 in freshness_engine.py (6 new tests)
- Implementer C: F5 in progress_engine.py (14 new tests)
- Implementer D: F6 in discovery.py (5 new tests)
- Implementer E: F3/F7 documentation patch proposals (applied by Main Agent)

Wave 4 — Parallel Independent Review (3 agents):
- Reviewer 1 (Semantic Correctness): found 2 bugs → FIXED + 3 regression tests → Re-review PASS
- Reviewer 2 (Failure/Safety): PASS
- Reviewer 3 (Acceptance/Diff): PASS

## 15. Validation Results

- Schema: 11/11 VALID
- Renderer: all VALID
- Render idempotency: PASS (zero diff on second render)
- Tests: 146 passed, 0 failed (baseline 73; +36 Round 1; +20 Round 2; +11 Round 3; +6 Round 4)
- diff-check: clean
- No source repository mutation (GET-only)
- No secrets
- No out-of-scope changes

## 16. Closeout (Round 4 — Final)

Final HEAD SHA: `82329f07518c0c0c97010a05bd750e60db3a3e91`
origin/main baseline SHA: `26caeaefca03aa61f030c5c6d277b9616332c1c9`
PR: #3 (https://github.com/expellirmud-dot/Obsidian/pull/3)

### Cumulative Findings Reconciliation (F1–F14)

| Finding | Round | Before | Fix | Final |
|---------|-------|--------|-----|-------|
| F1 Mission Verification | 1 | heading/project_name → purpose + verified | `_extract_explicit_purpose` requires explicit Purpose/Mission/Problem text | ACCEPTED |
| F2 Freshness Publication | 1 | remote_head known → all gates fresh | sub-gates gate on manifest status; aggregate requires all 3 fresh | ACCEPTED |
| F3 Acceptance Overclaim | 1 | "fills identity from evidence" | WO-036/038/039 corrected; 6 fields schema-supported-but-not-derived | ACCEPTED |
| F4 Mission Drift Provenance | 1 | candidate discarded; no provenance | `candidate_identity` + provenance recorded; old identity preserved | ACCEPTED |
| F5 Progress Correctness | 1 | truncated roadmap → false % | truncation gate; finditer fallback; unsupported methods UNKNOWN | ACCEPTED |
| F6 Atomic Onboarding | 1 | sequential writes; `'w'` mode | `_atomic_write_registry`; completeness-aware idempotency | ACCEPTED |
| F7 Git Automation Safety | 1 | `git add -A` in Automation A/B | explicit path staging; forbidden in docs | ACCEPTED |
| F8 Dry-Run Read-Only | 2 | wrote before dry_run gate | `dry_run` param; ZERO writes in every state | ACCEPTED |
| F9 Complete Partial Repair | 2 | state file never repaired | repairs missing state; completeness requires all 3 | ACCEPTED |
| F10 Progress Value ≠ Freshness | 2 | `estimate==null` → stale | "fresh" when manifest ok regardless of estimate | ACCEPTED |
| F11 Backward-Safe v2 Migration | 2 | v2 states skipped | `_upgrade_v2_shape` adds candidate fields; no longer skips v2 | ACCEPTED |
| F12 State Validity | 3 | `state_path.exists()` treated as complete | `_load_validated_state` loads + validates; invalid state rebuilt | ACCEPTED |
| F13 Migration Freshness Fabrication | 3 | v1 head → all freshness = "fresh" | all freshness = "unknown" for migrated v1 states | ACCEPTED |
| F14 Repair Transaction Safety | 4 | no rollback on later write failure | pre-repair snapshots + `_rollback()` + explicit `repair_failed` | ACCEPTED |

Expected findings: 14
Resolved: 14
Unresolved: 0

### Final Independent Owner Review

```
WO-OBSIDIAN-041
HEAD: 82329f07518c0c0c97010a05bd750e60db3a3e91

F1–F14: ACCEPTED
OPEN CORRECTNESS FINDINGS: 0

INDEPENDENT REVIEW: PASS
READY FOR CLOSEOUT: YES
READY FOR MERGE: YES
```

### Known Limitations (accepted as non-blocking)

1. Legacy manifests without `truncated`/`content_length` → progress UNKNOWN (safe default)
2. 6 identity fields remain schema-supported-but-not-derived (future WO)
3. bounded work-order set + phase/goal progress marked UNSUPPORTED (return UNKNOWN)
4. Repair-on-rename edge case (narrow, not reachable via normal flow)
5. Non-blocking: schema `progress_freshness` enum includes "stale" though no code produces it (harmless over-permissiveness; preserved for forward-compatibility)
6. Non-blocking: if the state write itself fails mid-write (disk full, first write), `repaired_state` stays False and rollback skips the state file — failure occurs before publish of registry/overview; retry re-enters via invalid-state repair; not a fail-open of the Project Truth Control Plane
7. Evidence limitation: no GitHub Actions workflow run at this HEAD; `146 passed` is from OpenHands/local execution, not GitHub CI reproduced by the owner. Not a blocker under the current workflow.

Status: CLOSED (final independent owner review PASS; ready for merge)
