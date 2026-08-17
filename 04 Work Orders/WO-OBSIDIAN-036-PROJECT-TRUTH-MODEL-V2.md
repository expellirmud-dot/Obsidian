# WORK ORDER — PROJECT TRUTH MODEL v2 + FRESHNESS CONTRACT

Work Order ID: WO-OBSIDIAN-036
Title: WO-OBSIDIAN-036 — Project Truth Model v2 + Freshness Contract
Risk Level: MEDIUM (schema migration + renderer/adapter upgrade)
Task Classification: Vault Operational Tooling / Truth Layer
Execution Mode: Bounded Single Work Order
Owner: Toto
Target Vault: `D:\Obsidian\Project-Knowledge-Vault`
Status: CLOSED

> CLOSED — v2 schema + backward-safe migration implemented; 11/11 states migrated and VALID;
> renderer + adapter upgraded to v2; 19/19 tests PASS; refresh 4 gates PASS.

## 1. Objective

ออกแบบ normalized state รุ่นใหม่ (v2) ที่แยก:
- `project_identity` (Mission ที่ stable — ห้าม rewrite เมื่อ Work Order เปลี่ยน)
- `current_execution` (current goal/work — เปลี่ยนได้ตาม Work Order)
- `freshness` (source/semantic/progress freshness contract)
- `progress` (deterministic, evidence-constrained)

เพิ่ม stable `github_repository_id` (รองรับ repository rename) และ schema migration แบบ backward-safe.

## 2. Critical Semantic Rule

ห้ามถือว่า Current Work Order ล่าสุดคือเป้าหมายแท้จริงของ Project v2 แยก identity ออกจาก execution
ทางโครงสร้าง ถ้าหลักฐานไม่พอ → `unknown` / `needs-verification` ห้ามเดา

## 3. Implemented

- `automation/schema/project-state.v2.schema.json` — v2 schema (identity/execution/freshness/progress/github blocks; github_repository_id nullable; knowledge_state; identity_drift_detected/previous_identity)
- `automation/migrate_state_v2.py` — backward-safe migrator (idempotent, drops no data, does not fabricate Mission; identity defaults to null)
- `automation/state/*.yaml` — 11 states migrated to v2, all VALID
- `scripts/render_project_wall.py` — upgraded to v2; new wall columns (Mission, Phase, Current Goal, Current Work, Progress, Confidence, Freshness, Vault HEAD, Remote HEAD, Last Truth Refresh, Next Action, Blocker); stale marked explicitly
- `automation/github_adapter.py` — upgraded to v2 (writes github block + freshness.remote_head/source_checked_at; does NOT change freshness.status)
- `automation/state/README.md` — v2 documentation
- `tests/test_migrate_state_v2.py` — 8 new tests
- `tests/conftest.py`, `tests/test_render_project_wall.py` — updated for v2

## 4. Freshness Contract

- `remote_head != truth_built_from_head` → stale
- GitHub unreachable → unknown (UNKNOWN never becomes FRESH)
- refresh failed → refresh_failed (known-good truth preserved)
- adapter records remote_head + source_checked_at only; status reconciled by freshness engine (WO-037/040)

## 5. Validation

- `python3 automation/migrate_state_v2.py --validate` → 11/11 VALID
- `python3 scripts/render_project_wall.py --validate-all` → 11/11 VALID
- `python3 scripts/render_project_wall.py` → rendered; second render zero diff (idempotent)
- `python3 -m pytest tests/` → 19/19 PASS
- `python3 automation/refresh_state.py` → 4 gates PASS (dry-run)

## 6. Safety

- ไม่แก้ source repositories (read-only)
- v1 schema retained for history; v2 is active contract
- ไม่ fabricate Mission (identity defaults null; knowledge_state=needs-verification)
- ไม่ commit secrets

## 7. Definition of Done

- [x] v2 schema separates identity/execution/freshness/progress
- [x] github_repository_id added (nullable)
- [x] backward-safe migration (idempotent, no data loss)
- [x] 11 states migrated and VALID
- [x] renderer + adapter upgraded to v2
- [x] freshness contract encoded (unknown never fresh)
- [x] mission not rewritten on work-order change (test)
- [x] 19/19 tests PASS
- [x] refresh 4 gates PASS
