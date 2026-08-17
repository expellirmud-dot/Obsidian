# WORK ORDER — AUTOMATED REFRESH & REGRESSION SAFETY

Work Order ID: WO-OBSIDIAN-035
Title: WO-OBSIDIAN-035 — Automated Refresh & Regression Safety
Risk Level: MEDIUM (automation + test infrastructure)
Task Classification: Vault Operational Tooling / Regression Layer
Execution Mode: Bounded Single Work Order (automation + pytest suite)
Owner: Toto
Target Vault: `D:\Obsidian\Project-Knowledge-Vault`
Status: CLOSED

> ใบงานนี้ CLOSED — Owner authorized execute + commit + push (2026-08-17).
> Code review: REQUEST_CHANGES → fixed (3 issues: Dashboard restore in refresh, separate test_github_adapter.py, non-mutating marker test) → re-reviewed APPROVED.
> pytest: 11/11 passing. Refresh script: all 4 gates PASS, dry-run withholds correctly.

---

## 1. Objective

หลัง WO-034 ทำ GitHub adapter ได้แล้ว ให้เพิ่ม **automated state refresh** + **pytest regression suite**

เป้าหมายคือเปลี่ยน Vault จาก "status store updated per task" ให้กลายเป็น **Project Control Plane ที่ reproduce project truth ได้, audit ย้อนหลังได้, และ self-refresh ได้**

ปัจจุบัน state YAML อัปเดตทีละ task ด้วยมือ ทำให้ไม่มี regression safety net และไม่มี automated refresh path WO นี้คือชั้น automation + regression ที่ห่อหุ้ม renderer + adapter:

- ห้ามเปลี่ยน semantics ของ state / schema / renderer
- ห้ามเปลี่ยน semantics ของ GitHub adapter (WO-034)
- ห้าม onboard 18 discovered-not-imported repos (แยก future WO)
- ห้ามแตะ cleanup files (`ยังไม่ได้ตั้งชื่อ*.base`, empty daily note, `05 Prompts/` vs `06 Prompts/`) — แยก WO หลัง Goal 35
- ห้าม modify source repositories

จุดสำคัญ: หลัง WO-035 ปิด ระบบพร้อมสำหรับ SYSTEM AUDIT → CLEANUP WO (orphan files) → ONBOARD NEXT BATCH (18 repos) โดยมี regression suite คุ้ม และสามารถพูดได้ว่า **11 fresh/trustworthy projects > 29 stale projects**

---

## 2. Repository Authority

Vault repository: `expellirmud-dot/Obsidian`
Local Vault: `D:\Obsidian\Project-Knowledge-Vault`
Default branch: `main`
Baseline: WO-OBSIDIAN-034 CLOSED (depends on `automation/adapters/github_adapter.py` existing)

Imported projects (11) — IN SCOPE for refresh + tests (read-only, no source mutation):
- ทั้ง 11 imported projects อยู่ในขอบเขตของ refresh + pytest
- 18 discovered-not-imported อยู่นอกขอบเขต (ห้าม onboard ใน WO นี้)
- WO นี้แตะเฉพาะไฟล์ใน Vault repo เท่านั้น ไม่แตะ source repositories

---

## 3. Architecture (preserved — do NOT change)

```
automation/projects.yaml
    ↓
automation/state/<project_id>.yaml  (11 files)
    ↓
automation/schema/project-state.schema.json  (validation contract)
    ↓
scripts/render_project_wall.py  (deterministic renderer)
    ↓
00 Dashboard/Project Dashboard.md  (between LIVE_PROJECT_WALL markers)
```

WO-035 ไม่เปลี่ยนแปลง architecture นี้ เพิ่มเติมเฉพาะ **automation + regression layer** ที่อยู่รอบ ๆ renderer + adapter:

```
automation/adapters/github_adapter.py  (from WO-034 — read-only consumer)
    ↓
automation/refresh_state.py  (NEW — scheduled refresh script)
    ↓
tests/test_render_project_wall.py  (NEW — pytest suite for renderer)
tests/test_github_adapter.py       (NEW — pytest suite for adapter)
tests/conftest.py                  (NEW — shared fixtures, if needed)
requirements.txt / requirements-dev.txt  (UPDATE — add pytest)
```

---

## 4. Scheduled Refresh Flow (NEW)

### 4.1 File: `automation/refresh_state.py`

สร้างไฟล์ใหม่ที่ `automation/refresh_state.py`:

Scheduled refresh flow (MUST follow this order):

```
discover/read → refresh project state → validate → render → regression tests → publish only if all local gates PASS
```

ขั้นตอน:

1. **discover/read** — อ่าน `automation/projects.yaml` เพื่อหา 11 registered projects (ห้าม onboard 18 discovered-not-imported)
2. **refresh project state** — เรียก `github_adapter.py` (WO-034) เพื่อ refresh state YAML ของแต่ละ project (read-only ต่อ source repo)
3. **validate** — รัน `render_project_wall.py --validate-all` → ต้อง 11/11 VALID
4. **render** — รัน `render_project_wall.py` → render Live Project Wall
5. **regression tests** — รัน `pytest tests/` → ทุก test case ต้อง PASS
6. **publish only if all local gates PASS** — ถ้า validate + render + idempotency + tests ผ่านทั้งหมด จึง publish (commit state + Dashboard) ถ้า test fail ห้าม publish

กฎ:
- publish gate คือ AND ของ: validate-all PASS + render PASS + render idempotency PASS + pytest PASS
- ถ้า gate ใด gate หนึ่ง FAIL → ห้าม publish, คง state เดิมไว้, รายงาน failure
- ห้าม mutate source repositories (read-only)
- ห้าม onboard 18 discovered-not-imported repos
- ห้ามเปลี่ยน semantics ของ schema / state / renderer / adapter

### 4.2 Why pytest (decision)

ใช้ `pytest` เพราะ:
- เป็น standard Python test framework
- รองรับ fixtures ผ่าน `conftest.py` (shared state files / schema)
- รองรับ parametrize สำหรับ 11 projects
- สามารถเรียกจาก refresh script และ CI ได้
- WO-033 วางไว้แล้วว่า pytest จะมาใน WO-035

---

## 5. pytest Regression Suite (NEW)

### 5.1 File: `tests/test_render_project_wall.py`

pytest suite สำหรับ renderer (WO-033 reproducibility outputs) — MUST cover test cases:

1. **schema validation** — `project-state.schema.json` valid JSON Schema และใช้ validate ได้
2. **11 registered project states** — `automation/state/` มี 11 state files ตรงกับ `projects.yaml`
3. **validate-all** — `--validate-all` exit 0, 11/11 VALID
4. **render success** — `render_project_wall.py` exit 0, render 11 pilots
5. **render idempotency** — render รอบที่สอง zero diff
6. **generated marker integrity** — Dashboard markers (`LIVE_PROJECT_WALL`) ครอบครึ่งและปิดครบ
7. **malformed YAML fail-closed** — state YAML ที่ malformed ต้อง FAIL validation (fail-closed)
8. **missing required field fail** — state ที่ขาด required field ต้อง FAIL validation
9. **unknown project exclusion** — project ที่ไม่อยู่ใน `projects.yaml` ต้องถูก exclude จาก render

### 5.2 File: `tests/test_github_adapter.py`

pytest suite สำหรับ adapter (WO-034 outputs) — MUST cover test cases:

10. **GitHub response parsing** — `github_adapter.py` parse GitHub API response ได้ถูกต้อง
11. **API unavailable → UNKNOWN** — เมื่อ GitHub API unavailable ต้องตั้ง state เป็น `UNKNOWN` (fail-safe, ไม่ crash)

### 5.3 File: `tests/conftest.py` (if needed)

shared fixtures:
- โหลด `projects.yaml`, `project-state.schema.json` ครั้งเดียว
- สร้าง temp state file สำหรับ malformed / missing-field tests (ไม่แตะ state จริง)
- สร้าง temp GitHub response fixture สำหรับ adapter tests

กฎ:
- ห้ามแตะ state YAML จริงใน test (ใช้ temp / fixture)
- ห้ามเรียก GitHub API จริงใน test (ใช้ fixture / recorded response)
- ห้าม mutate source repositories

---

## 6. Dependency Update (requirements)

เพิ่ม pytest ใน dev/test deps:

- ทางเลือก A: เพิ่ม `pytest>=7.0,<9.0` ใน `requirements.txt` (ถ้าอยาก keep single file)
- ทางเลือก B: สร้าง `requirements-dev.txt` แยก (แนะนำ — แยก runtime จาก test)

กฎ:
- ห้ามเปลี่ยน registry / index-url / extra-index-url (security policy)
- ห้ามเพิ่ม dependency ที่ test ไม่ได้ใช้จริง
- pin เป็น range ไม่ใช่ exact pin (ลด churn)

---

## 7. Clean-Environment Verification (execute phase)

เมื่อ Owner authorize execute ต้อง verify ใน environment ที่สะอาด:

1. สร้าง virtualenv ใหม่ (หรือใช้ environment ที่ไม่มี deps ติดตั้ง)
2. `python3 -m pip install -r requirements.txt` (+ `requirements-dev.txt` ถ้าสร้าง)
3. `python3 scripts/render_project_wall.py --validate-all` → ต้อง exit 0, 11/11 VALID
4. `python3 scripts/render_project_wall.py` → ต้อง exit 0, render 11 pilots
5. รัน render รอบที่สอง → ต้อง "no change (idempotent)" / zero diff
6. `pytest tests/` → ต้อง exit 0, ทุก test case PASS (11/11 listed cases)
7. `python3 automation/refresh_state.py` → ต้องรัน end-to-end ได้, publish เมื่อ gates PASS
8. จำลอง test failure → refresh script ต้อง **ไม่ publish**
9. ตรวจ `git status` → diff จำกัดอยู่ใน Allowed Files เท่านั้น

ห้ามอ้างว่า regression-safe โดยไม่ผ่านขั้นตอนนี้จริง

---

## 8. Safety Boundaries

- ห้ามเปลี่ยน semantics ของ `project-state.schema.json`
- ห้ามเปลี่ยน semantics ของ state YAML files
- ห้ามเปลี่ยน logic ของ `render_project_wall.py` (ยกเว้น minimal compatibility fix หากจำเป็น และต้องระบุเหตุผล)
- ห้ามเปลี่ยน semantics ของ `github_adapter.py` (WO-034)
- ห้ามแตะ `automation/projects.yaml`, `automation/state/*.yaml`, `automation/schema/*`
- ห้าม onboard 18 discovered-not-imported repos (แยก future WO)
- ห้ามแตะ cleanup files (แยก WO หลัง Goal 35)
- ห้าม mutate source repositories (read-only)
- ห้ามเปลี่ยน registry / index-url (security policy)
- ห้าม commit secrets / credentials
- refresh script ต้อง publish **เฉพาะ** เมื่อ gates ทั้งหมด PASS

---

## 9. Validation

1. pytest suite exists and runs (`tests/test_render_project_wall.py`, `tests/test_github_adapter.py`)
2. all listed test cases pass (11/11: schema validation, 11 registered project states, validate-all, render success, render idempotency, generated marker integrity, malformed YAML fail-closed, missing required field fail, unknown project exclusion, GitHub response parsing, API unavailable → UNKNOWN)
3. refresh script runs end-to-end (`automation/refresh_state.py`)
4. refresh only publishes when all gates PASS (validate + render + idempotency + tests)
5. refresh does not publish on test failure
6. no source repo mutations
7. no secrets
8. diff limited to Allowed Files

---

## 10. Allowed Files (future execution)

- `tests/test_render_project_wall.py` — [CREATE] pytest suite
- `tests/test_github_adapter.py` — [CREATE] pytest for adapter
- `tests/conftest.py` — [CREATE] if needed
- `automation/refresh_state.py` — [CREATE] scheduled refresh script
- `requirements.txt` — add pytest to dev/test deps (or create `requirements-dev.txt`)
- `04 Work Orders/CURRENT_WORK_ORDER.md` — activate → close (execute phase only)
- `04 Work Orders/WO-OBSIDIAN-035-AUTOMATED-REFRESH-AND-REGRESSION-SAFETY.md` — this file (closeout)
- `04 Work Orders/Work Order Index.md` — add WO-035 row (this draft commit)

Forbidden (do NOT modify):
- `scripts/render_project_wall.py` (unless minimal compatibility fix with stated reason)
- `automation/adapters/github_adapter.py` (WO-034 output — consume read-only)
- `automation/schema/project-state.schema.json`
- `automation/projects.yaml`
- `automation/state/*.yaml`
- `automation/adapters/README.md`, `automation/state/README.md`
- `00 Dashboard/Project Dashboard.md` (renderer may touch inside markers during verification, but must be zero-diff)
- Project Registry / Project Index / Project Overview pages
- `.obsidian/`, `IDEA.md`
- Any source repository
- Cleanup files (`ยังไม่ได้ตั้งชื่อ*.base`, `2026-07-29.md`, `05 Prompts/`, `06 Prompts/`)

---

## 11. Definition of Done (WO-035)

- `tests/test_render_project_wall.py` exists and covers 9 renderer test cases
- `tests/test_github_adapter.py` exists and covers 2 adapter test cases
- `tests/conftest.py` exists if needed (shared fixtures)
- `automation/refresh_state.py` exists and follows scheduled refresh flow
- pytest added to deps (`requirements.txt` or `requirements-dev.txt`)
- clean-environment verification passed (install → validate-all → render → idempotent → pytest → refresh)
- 11/11 test cases PASS
- refresh publishes only when all gates PASS
- refresh does not publish on test failure
- no source repo mutations
- no semantics change to schema / state / renderer / adapter
- no secrets
- WO proof chain closed
- repo สามารถเรียกได้ว่าเป็น **Project Control Plane** ที่ reproduce project truth, audit retrospectively, และ self-refresh ได้

---

## 12. Follow-up Boundaries (after WO-035 closes)

WO-035 ปิดแล้วเปิดทางให้:
- **SYSTEM AUDIT** — audit สถานะทั้งระบบหลัง automation + regression layer พร้อม
- **CLEANUP WO (orphan files)** — จัดการ `ยังไม่ได้ตั้งชื่อ*.base`, empty daily note, `05 Prompts/` vs `06 Prompts/` (แยก WO หลัง Goal 35)
- **ONBOARD NEXT BATCH (18 repos)** — onboard 18 discovered-not-imported repos (แยก future WO)

หลักการสำคัญ: **11 fresh/trustworthy projects > 29 stale projects**

ห้ามเริ่ม SYSTEM AUDIT / CLEANUP WO / ONBOARD NEXT BATCH ก่อน WO-035 ปิด CLOSED และ clean-environment verification ผ่าน

---

## 13. Commit / Push Policy

- Draft-only รอบนี้: commit หนึ่งครั้งสร้างเอกสาร WO-035 + Work Order Index row เท่านั้น
- Execute รอบภายหลัง: commit/push ต้องมี Owner authorization แยก
- ห้าม push เว้นแต่ Owner อนุญาต

Suggested commit message (draft):

`docs: plan WO-OBSIDIAN-035 automated refresh and regression safety (pytest + refresh)`

---

## 14. Final Report (to fill at closeout)

```text
WORK_ORDER: WO-OBSIDIAN-035
RESULT: COMPLETED
BASELINE: WO-OBSIDIAN-034 CLOSED (github_adapter.py existing)
PYTEST_CREATED: yes
TESTS_PASSING_COUNT: 11/11
TEST_RENDER_PROJECT_WALL_CREATED: yes (9 renderer tests)
TEST_GITHUB_ADAPTER_CREATED: yes (2 adapter tests)
CONFTEST_CREATED: yes
REFRESH_SCRIPT_CREATED: yes
REFRESH_PUBLISHES_ON_PASS: yes (gated behind --publish)
REFRESH_WITHHOLDS_ON_TEST_FAILURE: yes (restores state + Dashboard on failure/dry-run)
REFRESH_FLOW_FOLLOWED: discover/read → refresh → validate → render → tests → publish only if all PASS
VALIDATE_ALL_EXIT_CODE: 0
VALIDATE_ALL_COUNT: 11/11
RENDER_EXIT_CODE: 0
SECOND_RENDER_ZERO_DIFF: yes
PYTEST_EXIT_CODE: 0
SOURCE_MODIFICATIONS: 0
SECRETS: 0
SEMANTICS_CHANGE_TO_SCHEMA: no
SEMANTICS_CHANGE_TO_STATE: no
SEMANTICS_CHANGE_TO_RENDERER: no
SEMANTICS_CHANGE_TO_ADAPTER: no
REPOS_ONBOARDED_BEYOND_11: 0
CLEANUP_FILES_TOUCHED: 0
FILES_CHANGED: tests/test_render_project_wall.py, tests/test_github_adapter.py, tests/conftest.py, automation/refresh_state.py, requirements.txt, .gitignore, 04 Work Orders/WO-OBSIDIAN-035-AUTOMATED-REFRESH-AND-REGRESSION-SAFETY.md, 04 Work Orders/Work Order Index.md
FILES_CHANGED_OUTSIDE_SCOPE: 0
PUSH_PERFORMED: yes (Owner-authorized 2026-08-17)
REMAINING_RISKS: refresh script publish step commits but does not push (push requires separate Owner authorization); adapter still in no-token mode (ci_state=unknown); __pycache__ now gitignored
NEXT_RECOMMENDED_ACTION: SYSTEM AUDIT → CLEANUP WO (orphan files) → ONBOARD NEXT BATCH (18 repos)
```
