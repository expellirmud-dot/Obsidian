# WORK ORDER — REPOSITORY DISCOVERY + SAFE AUTO-ONBOARDING

Work Order ID: WO-OBSIDIAN-037
Title: WO-OBSIDIAN-037 — Repository Discovery + Safe Auto-Onboarding
Risk Level: MEDIUM (read-only GitHub discovery + onboarding)
Task Classification: Vault Operational Tooling / Discovery Layer
Execution Mode: Bounded Single Work Order
Owner: Toto
Target Vault: `D:\Obsidian\Project-Knowledge-Vault`
Status: CLOSED

> CLOSED — discovery layer implemented; 10 registered repos backfilled with stable github_repository_id;
> reconcile: 10 known, 0 renamed, 0 inaccessible, 7 new eligible (Obsidian excluded by denylist);
> 27/27 tests PASS.

## 1. Objective

สร้าง discovery layer ที่อ่าน GitHub แบบ READ-ONLY เพื่อ:
- ตรวจพบ repository/project ที่สร้างใหม่
- เปรียบเทียบ GitHub repositories กับ Vault registry โดยใช้ stable repository ID (ไม่ใช่ชื่อ)
- ตรวจ: new / renamed / archived / inaccessible
- onboard project ใหม่เข้า Vault โดยอัตโนมัติ (idempotent)

## 2. Safety Contract

- READ-ONLY (GET only); ไม่ mutate source repositories
- Default policy: EXCLUDE archived, forks, denylist (Vault repo itself)
- ห้าม onboard repo ที่ไม่มี permission เพียงพอโดยเดาข้อมูล
- หลักฐานไม่พอ → onboard เป็น `knowledge_state: needs-verification` (ไม่ fabricate mission)
- Idempotent: รันซ้ำไม่สร้าง duplicate (match by stable id ก่อน, แล้ว by URL/name)

## 3. Implemented

- `automation/discovery.py` — discover_repos() / reconcile_registry() / onboard_project() / CLI
- backfilled `github_repository_id` into 10 state files + projects.yaml (Adobe Stock: no remote, skipped)
- `tests/test_discovery.py` — 8 tests (discovery, idempotency, rename by stable id, exclusion, no-fabrication, api-unavailable, v2 state, registry+overview)

## 4. Live Reconcile Result (read-only, against expellirmud-dot)

- known (id+name match): 10
- renamed: 0
- inaccessible: 0
- new eligible: 7 (agentic-framework-mcp, ai-ops-registry, ai-pr-review-controller, ai-pr-review-sandbox, Jamie-Phone, SR-400-Virtual-Tuning-Lab, utility_automation_v2)
- excluded: 1 (Obsidian — denylist, the Vault itself)

## 5. Validation

- `python3 automation/discovery.py discover` → 18 repos, 17 eligible, 1 excluded
- `python3 automation/discovery.py reconcile` → 10 known, 7 new, 0 inaccessible
- `python3 automation/discovery.py onboard --dry-run` → 7 proposed (needs-verification)
- `python3 scripts/render_project_wall.py --validate-all` → 11/11 VALID
- `python3 -m pytest tests/` → 27/27 PASS

## 6. Definition of Done

- [x] discovery reads GitHub read-only (GET only)
- [x] compare via stable github_repository_id (rename-safe)
- [x] detect new/renamed/archived/inaccessible
- [x] inclusion/exclusion policy (archived+forks+denylist)
- [x] idempotent onboarding (no duplicates)
- [x] missing evidence → needs-verification (no mission fabrication)
- [x] 27/27 tests PASS
- [x] no source repo mutation
