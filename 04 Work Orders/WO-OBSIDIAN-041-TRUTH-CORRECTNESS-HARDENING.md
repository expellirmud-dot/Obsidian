# WORK ORDER — TRUTH CONTROL PLANE CORRECTNESS HARDENING

Work Order ID: WO-OBSIDIAN-041
Title: WO-OBSIDIAN-041 — Truth Control Plane Correctness Hardening
Risk Level: MEDIUM (corrective hardening of WO-036–040 truth layer; no source repo mutation)
Task Classification: Vault Operational Tooling / Truth Layer Correctness
Execution Mode: Bounded Single Work Order (MANDATORY PARALLEL MULTI-AGENT)
Owner: Toto
Target Vault: `D:\Obsidian\Project-Knowledge-Vault`
Status: ACTIVE

> ACTIVE — corrective hardening of the Truth Control Plane built in WO-036–040.
> Principle: CORRECTNESS > FEATURE COUNT. UNKNOWN is better than fabricated truth.
> No claim is preserved merely because a prior Work Order marked it PASS.

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
