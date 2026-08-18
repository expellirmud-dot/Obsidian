# WORK ORDER — EVIDENCE-BACKED PROJECT TRUTH INGESTION

Work Order ID: WO-OBSIDIAN-038
Title: WO-OBSIDIAN-038 — Evidence-Backed Project Truth Ingestion
Risk Level: MEDIUM (read-only evidence collection + truth builder)
Task Classification: Vault Operational Tooling / Truth Ingestion Layer
Execution Mode: Bounded Single Work Order
Owner: Toto
Target Vault: `D:\Obsidian\Project-Knowledge-Vault`
Status: CLOSED

> CLOSED — evidence collector reads real file content via GitHub contents API;
> evidence manifests with provenance (ref + blob_sha + path + classification);
> truth builder fills `purpose` (explicit Purpose/Mission/Problem text only) + execution;
> 6 identity fields (problem_statement, intended_outcome, primary_users,
> success_definition, scope, non_goals) are schema-supported-but-not-derived;
> Mission Drift Protection (candidate identity + provenance recorded, not overwritten);
> 35/35 tests PASS (WO-038 baseline).
>
> WO-OBSIDIAN-041 HARDENING: a bare project title/heading/repository name no
> longer verifies the Mission (F1). knowledge_state=verified now requires an
> explicit purpose. Mission drift records candidate_identity +
> candidate_identity_provenance (F4). See WO-OBSIDIAN-041.

## 1. Objective

สร้าง evidence collector / truth builder ที่:
- อ่าน repository ตาม availability และ authority (read-only)
- ห้ามใช้ filename อย่างเดียวเป็น evidence — ต้องอ่าน content จริง
- สร้าง compact evidence manifest ต่อ project (`automation/evidence/<project_id>.yaml`)
- ทุก critical claim trace กลับได้: repository, tracked ref, commit/blob SHA, path, classification, observed timestamp
- แยก evidence สำหรับ identity / current_execution / roadmap / completed_work / blockers / next_action

## 2. Mission Drift Protection

- ถ้า Current Work เปลี่ยน → ห้ามเปลี่ยน Project Mission โดยอัตโนมัติ
- ถ้าหลักฐาน authoritative บ่งชี้ว่า Mission เปลี่ยนจริง:
  - preserve previous identity
  - mark `identity_drift_detected: true`
  - record candidate new identity in `previous_identity`
  - ไม่ silently overwrite historical mission

## 3. Implemented

- `automation/evidence_collector.py` — collect_evidence_for_project() / build_identity_from_evidence() / build_execution_from_evidence() / apply_truth_to_state() / CLI
- `automation/evidence/<project_id>.yaml` — compact evidence manifests with provenance
- `tests/test_evidence_collector.py` — 8 tests

## 4. Token Scope Reality

The GITHUB_TOKEN in this environment can access:
- `/repos/{owner}/{repo}` (metadata)
- `/users/{account}/repos` + `/user/repos` (discovery)
- `/repos/{owner}/{repo}/contents/{path}` (file content + directory listing)

It CANNOT access `/commits`, `/git/trees`, `/branches` (returns 403 "Resource not accessible by integration").
Therefore:
- Provenance is bound to the tracked ref + per-file blob SHAs (commit SHA unavailable, left null — honest, no fabrication)
- The freshness engine (WO-040) reconciles via discovery's remote_head (also null with this token → UNKNOWN, fail-safe)

## 5. Validation

- `python3 automation/evidence_collector.py collect --project thai_stt_app` → status=ok, 4 evidence items (AGENTS.md, CHANGELOG.md, INDEX.md, pyproject.toml) with real content excerpts + blob SHAs
- `python3 automation/evidence_collector.py build-truth --project thai_stt_app` → applied, drift=False, knowledge_state=verified
- `python3 scripts/render_project_wall.py --validate-all` → 11/11 VALID
- `python3 -m pytest tests/` → 35/35 PASS

## 6. Definition of Done

- [x] evidence collector reads real file content (not filename alone)
- [x] evidence manifests with provenance (ref + blob_sha + path + classification + observed_at)
- [x] truth builder fills `purpose` (explicit text only) + execution; 6 identity fields schema-supported-but-not-derived (WO-041 F1/F3)
- [x] Mission Drift Protection (preserve previous identity, flag drift, no silent overwrite)
- [x] Mission drift records candidate_identity + candidate_identity_provenance (WO-041 F4)
- [x] current work change does NOT rewrite mission (test)
- [x] insufficient evidence → unknown (no fabrication)
- [x] API unavailable → fail-safe (no fabrication)
- [x] 35/35 tests PASS
- [x] no source repo mutation
