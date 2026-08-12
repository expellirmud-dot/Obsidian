# WORK ORDER — EXPAND PROJECT WALL ADAPTERS

Work Order ID: WO-OBSIDIAN-032
Title: WO-OBSIDIAN-032 — Expand Project Wall Adapters (9 remaining imported projects)
Risk Level: MEDIUM (adapter expansion, no runtime/automation added)
Task Classification: Vault Operational Tooling / Knowledge Layer
Execution Mode: Bounded Single Work Order (expand-only)
Owner: Toto
Target Vault: `D:\Obsidian\Project-Knowledge-Vault`
Status: CLOSED

> ใบงานนี้ CLOSED — Owner authorized execute + commit + push (2026-08-12).

---

## 22. Final Report

```text
WORK_ORDER: WO-OBSIDIAN-032
RESULT: COMPLETED
BASELINE: WO-OBSIDIAN-031 CLOSED (HEAD 60f108b)
PROJECTS_ADAPTED: 9 (llm-agents, STT-Typing, AI-Worker-Harness, Utility-Disbursement-App, Adobe-Stock-Upload-Assistant, lightroom-ai-exposure, citizen_portal, TalkToClibord, AI-Workspace)
TOTAL_PROJECTS_ON_WALL: 11
SCHEMA_VALID: yes (11/11)
RENDERER_EXIT_CODE: 0
SECOND_RENDER_ZERO_DIFF: yes
DASHBOARD_OUTSIDE_MARKERS_UNCHANGED: yes
SOURCE_MODIFICATIONS: 0
SECRETS: 0
CI_PR_INTEGRATION: none (unknown/null for all)
DISCOVERED_NOT_IMPORTED_REPRESENTED: 0
FILES_CHANGED: automation/projects.yaml, automation/state/llm-agents.yaml, automation/state/STT-Typing.yaml, automation/state/AI-Worker-Harness.yaml, automation/state/Utility-Disbursement-App.yaml, automation/state/Adobe-Stock-Upload-Assistant.yaml, automation/state/lightroom-ai-exposure.yaml, automation/state/citizen_portal.yaml, automation/state/TalkToClibord.yaml, automation/state/AI-Workspace.yaml, automation/adapters/README.md, automation/state/README.md, 00 Dashboard/Project Dashboard.md, 04 Work Orders/WO-OBSIDIAN-032-EXPAND-PROJECT-WALL-ADAPTERS.md, 04 Work Orders/Work Order Index.md, 04 Work Orders/CURRENT_WORK_ORDER.md
FILES_CHANGED_OUTSIDE_SCOPE: 0
PUSH_PERFORMED: yes (Owner-authorized 2026-08-12)
REMAINING_RISKS: source repos not directly accessible in execution environment — normalized state derived from already-verified Vault records (WO-004..008, WO-025..030); CI/PR remain unknown; TalkToClibord current_work_evidence=inference (JAVIS.md sprint status not a formal WO)
NEXT_RECOMMENDED_ACTION: WO-033 GitHub PR/CI integration or scheduled project-state refresh
```

---

## 1. Objective

ขยาย Live Project Wall adapter coverage จาก 2 pilot projects (`thai_stt_app`, `lumina-studio`) ไปยัง imported projects ที่เหลืออีก 9 ตัว โดยรักษา normalized-state contract และ deterministic rendering architecture ที่ WO-031 สร้างไว้

WO นี้คือ **expand-only**:
- ห้าม implement real-time webhook / polling daemon / background service / Obsidian plugin / automatic GitHub sync / GitHub PR/CI integration ตอนนี้
- ห้าม redesign schema, adapter contract, หรือ renderer

จุดสำคัญ: พิสูจน์ว่า 9 imported projects ที่เหลือ (โครงสร้าง repo ต่างกัน) สามารถถูกแปลงเป็น normalized state กลางเดียวกัน และ render Wall แบบ deterministic ได้ โดยใช้ schema/adapter/renderer เดิมจาก WO-031

---

## 2. Repository Authority

Vault repository: `expellirmud-dot/Obsidian`
Local Vault: `D:\Obsidian\Project-Knowledge-Vault`
Default branch: `main`
Baseline: WO-OBSIDIAN-031 CLOSED (HEAD `60f108b7117a91d4242931dc68b2c1829a5be2b3`)

Imported projects (11) — OUT OF SCOPE: 18 discovered-not-imported:
- Already adapted (WO-031): `thai_stt_app`, `lumina-studio`
- To adapt (WO-032): `llm-agents`, `STT-Typing`, `AI-Worker-Harness`, `Utility-Disbursement-App`, `Adobe-Stock-Upload-Assistant`, `lightroom-ai-exposure`, `citizen_portal`, `TalkToClibord`, `AI-Workspace`
- Discovered-not-imported (18): **NOT eligible** ใน WO นี้

---

## 3. Architecture (preserved from WO-031 — do NOT replace)

```
Source Repository
    ↓
Project Adapter / Evidence Reader
    ↓
Normalized Project State YAML
    ↓
Deterministic Project Wall Renderer
    ↓
00 Dashboard/Project Dashboard.md
```

Design MUST support repositories with different authority structures:
- `.tasks/CURRENT_TASK.md`
- `WORK_ORDER.md`
- `Work-Order/CURRENT_WORK_ORDER.md`
- `04 Work Orders/CURRENT_WORK_ORDER.md`
- `AGENTS.md`
- `PROJECT_RULES.md`
- roadmap / readiness / handoff docs
- git branch / HEAD / status
- GitHub PR / CI state (declared but NOT integrated in WO-032)

ห้ามบังคับ source repos ต้องใช้ layout เดียวกัน

---

## 4. Reuse WO-031 Schema (do NOT create a second schema)

Normalized state instances remain **YAML** at `automation/state/<project_id>.yaml`.
Validation contract remains `automation/schema/project-state.schema.json` (unchanged from WO-031).

Required fields (same as WO-031 — ห้ามเดา; ใส่ `null` / `unknown` / `needs-verification` เมื่อไม่มีหลักฐาน):

```yaml
project_id: <string>
project_name: <string>
source_path: <abs path>
repository: <remote url or null>
branch: <string or null>
head: <sha or null>
project_state: <verified-string | unknown>
current_goal: <string | null>
current_work: <string | null>
current_work_authority:
  path: <string | null>
  kind: <work-order | current-task | handoff | roadmap | readme | other | null>
current_work_evidence: <verified | owner-confirmed | inference | unknown>
ci_state: <success | failure | pending | unknown | null>
open_pr: <pr-number | null>
last_change: <iso-date | null>
next_action: <string | null>
blockers: <string | null>
evidence_classification: <verified | owner-confirmed | inference | unknown>
verified_at: <iso-date | null>
adapter_id: <string>
```

หาก field เพิ่มเติมจำเป็นจริง ๆ สำหรับ project ใด:
- พิสูจน์ว่า schema เดิม represent ไม่ได้
- เลือก backward-compatible optional extension
- บันทึกเหตุผล
- ห้าม redesign schema โดยพลการ

---

## 5. Reuse Adapter Contract from WO-031

Adapter: `generic-git-plus-authority-files` (เดิมจาก WO-031)

Adapter evidence may include:
- `CURRENT_TASK.md`, `CURRENT_WORK_ORDER.md`, `WORK_ORDER.md`
- `AGENTS.md`, `PROJECT_RULES.md`
- handoff/readiness/roadmap docs
- repo-specific authority docs
- git branch, HEAD, status, log

Historical/archive paths explicitly declared non-authoritative MUST NOT be used as `current_work_authority`.

ตัวอย่าง: `.tasks/` ที่ระบุ "Historical reference only; never execution authority" ต้องไม่กลายเป็น current-work authority

---

## 6. Repository-Change != Project-State-Change (invariant)

A commit, cleanup, refactor, asset move, dependency cleanup, repository-size reduction, or maintenance change:

- MAY update `head`
- MAY update `last_change`
- MAY update `current_work` if supported by authoritative evidence

but MUST NOT automatically change:
- `project_state`
- `lifecycle`
- `current_goal`
- `blockers`

Never infer project lifecycle merely from Git activity.

---

## 7. Resolve Every Source Repository Fresh

สำหรับแต่ละ project ใน 9 ตัว บันทึก:
- exact local git root
- branch
- HEAD
- status
- remote
- authority files
- current-work authority
- current-work evidence classification

Source repos are STRICTLY READ-ONLY.
Do not trust stale source paths from Vault when git/filesystem truth contradicts them.

> หมายเหตุ execution: source repos (`D:\*` Windows paths) อาจไม่สามารถเข้าถึงได้โดยตรงใน execution environment; ในกรณีนั้น normalized state มาจาก already-verified Vault records (Project Overview pages + Project Registry) ที่ verified ใน WO onboarding ก่อนหน้า ต้องระบุ evidence source ชัดเจน

---

## 8. Handle Dirty Repositories Safely

Pre-existing dirty/untracked source state:
- record it
- preserve it
- do not clean/reset/stash/edit it
- do not treat it as caused by WO-032

---

## 9. projects.yaml

Update the existing `automation/projects.yaml`:
- all 11 imported projects remain registered
- all 11 should be adapter-covered if validation succeeds
- `enabled_for_wall: true` only after that project's normalization succeeds
- `pilot_status` transitions from `not-yet-adapted` to `adapted`

Do not add discovered-not-imported repos.

---

## 10. Normalized YAML State Files (9 remaining projects)

Expected new state files:

```text
automation/state/llm-agents.yaml
automation/state/STT-Typing.yaml
automation/state/AI-Worker-Harness.yaml
automation/state/Utility-Disbursement-App.yaml
automation/state/Adobe-Stock-Upload-Assistant.yaml
automation/state/lightroom-ai-exposure.yaml
automation/state/citizen_portal.yaml
automation/state/TalkToClibord.yaml
automation/state/AI-Workspace.yaml
```

Use the existing `project_id` convention from `automation/projects.yaml` (exact IDs: `llm-agents`, `STT-Typing`, `AI-Worker-Harness`, `Utility-Disbursement-App`, `Adobe-Stock-Upload-Assistant`, `lightroom-ai-exposure`, `citizen_portal`, `TalkToClibord`, `AI-Workspace`).

---

## 11. Unknown Handling

If evidence does not establish a field: `null` / `unknown` / `needs-verification`.

Do NOT fabricate: project state, active task, next action, blockers, CI status, PR status, lifecycle.

---

## 12. CI and PR Remain Outside Integration Scope

Do NOT implement GitHub API/CLI integration in WO-032.
For projects without verified CI/PR state: render `unknown`/`null`.

---

## 13. Renderer Remains Deterministic

Do NOT redesign renderer unless a minimal compatibility change is required for additional adapters.
Renderer may modify only content inside `<!-- LIVE_PROJECT_WALL:START -->` ... `<!-- LIVE_PROJECT_WALL:END -->`.
Dashboard content outside markers is immutable in this WO.

---

## 14. Wall Target After Successful Execution

- All 11 imported projects rendered
- No discovered-not-imported project rendered
- Columns remain compatible with WO-031: Project | State | Current Work | CI | PR | Last Change | Next Action | Verified At

---

## 15. Idempotency Requirement

After all 11 normalized states are generated:
- render Wall
- capture result
- render again with identical state
- second render must produce zero additional diff

---

## 16. Safety Boundaries

- source repos READ-ONLY
- no project onboarding
- no Registry reclassification
- no lifecycle inference
- no `.obsidian` changes
- no Community Plugin
- no webhook / polling / daemon / background service
- no CI workflow implementation
- no external deployment
- no GitHub PR/CI integration
- no event-history implementation
- no unrelated cleanup

---

## 17. Validation

1. current WO-031 schema still valid
2. every normalized YAML validates against schema (11 total)
3. 11 projects registered
4. 11 imported projects represented
5. exactly 0 discovered-not-imported repos represented
6. `current_work_authority` path/kind valid or null
7. evidence classification explicit
8. historical/non-authoritative paths rejected as current authority
9. unknown fields remain unknown/null
10. dirty source repos unchanged from preflight
11. clean source repos remain clean
12. renderer succeeds for all projects
13. second render zero-diff
14. Dashboard outside markers unchanged
15. no source modifications
16. no secrets
17. diff limited to Allowed Files

---

## 18. Allowed Files (future execution)

- `automation/projects.yaml` — update 9 projects to enabled/adapted
- `automation/state/llm-agents.yaml` — [CREATE]
- `automation/state/STT-Typing.yaml` — [CREATE]
- `automation/state/AI-Worker-Harness.yaml` — [CREATE]
- `automation/state/Utility-Disbursement-App.yaml` — [CREATE]
- `automation/state/Adobe-Stock-Upload-Assistant.yaml` — [CREATE]
- `automation/state/lightroom-ai-exposure.yaml` — [CREATE]
- `automation/state/citizen_portal.yaml` — [CREATE]
- `automation/state/TalkToClibord.yaml` — [CREATE]
- `automation/state/AI-Workspace.yaml` — [CREATE]
- `automation/adapters/README.md` — update coverage table (if needed)
- `automation/state/README.md` — update file table (if needed)
- `scripts/render_project_wall.py` — minimal compatibility change only if required
- `00 Dashboard/Project Dashboard.md` — inside LIVE_PROJECT_WALL markers only
- `04 Work Orders/CURRENT_WORK_ORDER.md` — activate → close
- `04 Work Orders/WO-OBSIDIAN-032-EXPAND-PROJECT-WALL-ADAPTERS.md` — this file (closeout)
- `04 Work Orders/Work Order Index.md` — add WO-032 row

Forbidden (do NOT modify):
- `automation/schema/project-state.schema.json` (reuse WO-031 schema as-is)
- Project Registry / Project Index / Project Overview pages
- `.obsidian/`
- Any source repository
- `scripts/staleness-check.py`, `scripts/staleness-registry.yml`

---

## 19. Definition of Done (WO-032)

- all 11 imported projects have adapter registration
- all 11 have valid normalized state
- all 11 appear on Live Project Wall
- heterogeneous authority layouts handled correctly
- no unsupported claims introduced
- historical/archive evidence excluded from execution authority
- renderer deterministic/idempotent
- Dashboard outside markers preserved
- source repos unchanged
- no real-time synchronization implemented
- WO proof chain closed

---

## 20. Follow-up Candidates — OUT OF SCOPE

After WO-032 only:
- GitHub PR/CI integration
- scheduled project-state refresh / polling
- event/change history
- webhook/event-driven synchronization
- stale-state detection/TTL for wall state
- adapter health monitoring

---

## 21. Commit / Push Policy

- Draft-only รอบนี้: commit หนึ่งครั้งสร้างเอกสาร WO-032 เท่านั้น (stage เฉพาะไฟล์ WO-032)
- Execute รอบภายหลัง: commit/push ต้องมี Owner authorization แยก
- ห้าม push เว้นแต่ Owner อนุญาต

Suggested commit message (draft):

`docs: plan WO-OBSIDIAN-032 expand project wall adapters (9 remaining projects)`
