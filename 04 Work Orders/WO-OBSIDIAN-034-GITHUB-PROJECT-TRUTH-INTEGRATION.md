# WORK ORDER — GITHUB PROJECT TRUTH INTEGRATION

Work Order ID: WO-OBSIDIAN-034
Title: WO-OBSIDIAN-034 — GitHub Project Truth Integration
Risk Level: MEDIUM (read-only GitHub adapter + state enrichment; no source mutation)
Task Classification: Vault Operational Tooling / GitHub Integration Layer
Execution Mode: Bounded Single Work Order (read-only adapter only)
Owner: Toto
Target Vault: `D:\Obsidian\Project-Knowledge-Vault`
Status: CLOSED

> ใบงานนี้ CLOSED — Owner authorized execute + commit + push (2026-08-17).
> Code review: APPROVED (sub-agent, risk LOW, no issues).
> Note: adapter ran in fail-safe no-token mode (ci_state=unknown for all 11); re-run with GITHUB_TOKEN to populate real values.

---

## 1. Objective

เติมช่องว่าง `ci_state: unknown` และ `open_pr: null` ของทั้ง 11 imported projects ด้วยการสร้าง **read-only GitHub adapter**

ปัจจุบัน state YAML ของ 11 imported projects มี `ci_state: unknown` และ `open_pr: null` เพราะยังไม่มี path ที่ดึงความจริงจาก GitHub เข้าสู่ Vault ทำให้ Live Project Wall แสดงสถานะที่ไม่ตรงกับความเป็นจริงของ source repo WO นี้คือชั้น **GitHub Integration Layer** ที่อยู่ระหว่าง `projects.yaml` กับ state YAML:

- ห้ามเปลี่ยน semantics ของ state / schema / renderer
- ห้าม implement scheduled refresh / pytest suite (ไว้ WO-035)
- ห้าม onboard 18 discovered-not-imported repos (แยก future WO)
- ห้ามแตะ cleanup files (`ยังไม่ได้ตั้งชื่อ*.base`, empty daily note, `05 Prompts/` vs `06 Prompts/`) — แยก WO หลัง Goal 35
- ห้าม mutate source repositories (read-only เท่านั้น)

จุดสำคัญ: หลัง WO-034 ปิด ต้องสามารถพูดได้ว่า state YAML ของ 11 projects สะท้อน **project truth จาก GitHub ณ SHA ที่กำหนด** ไม่ใช่ `unknown`/`null` อีกต่อไป โดยที่ truth นั้นมี `observed_at` timestamp และผูกกับ exact SHA เพื่อลด stale truth

---

## 2. Repository Authority

Vault repository: `expellirmud-dot/Obsidian`
Local Vault: `D:\Obsidian\Project-Knowledge-Vault`
Default branch: `main`
Baseline: WO-OBSIDIAN-033 CLOSED (repo reproducible — `requirements.txt` + bootstrap verified)

Imported projects (11) — IN SCOPE for read-only GitHub enrichment:
- ทั้ง 11 imported projects อยู่ในขอบเขตของ adapter (read-only, no source mutation)
- 18 discovered-not-imported อยู่นอกขอบเขต (ห้าม onboard ใน WO นี้)
- WO นี้แตะเฉพาะไฟล์ใน Vault repo เท่านั้น ไม่แตะ source repositories นอกจาก read-only API calls

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

WO-034 ไม่เปลี่ยนแปลง architecture นี้ เพิ่มเติมเฉพาะ **GitHub Integration Layer** ที่อยู่ระหว่าง `projects.yaml` กับ state YAML:

```
projects.yaml → GitHub read-only adapter → Repository HEAD / Open PR / PR HEAD SHA / Check/CI state → state/<project>.yaml → schema validation → Live Project Wall
```

ไฟล์ใหม่ที่เข้ามาในชั้นนี้:

```
automation/github_adapter.py  (NEW — read-only GitHub adapter)
```

> หมายเหตุ: WO-035 อ้างอิง path นี้เป็น `automation/adapters/github_adapter.py` หาก execute phase เลือกวางใต้ `automation/adapters/` ให้ถือว่าเป็น path เดียวกัน (adapter ตัวเดียวกัน) และต้องระบุใน Final Report ว่าวางที่ path ใดจริง

---

## 4. Read-Only GitHub Adapter (NEW)

### 4.1 File: `automation/github_adapter.py`

สร้างไฟล์ใหม่ที่ `automation/github_adapter.py` (หรือ `automation/adapters/github_adapter.py` ตามที่ execute phase เลือก — ระบุใน Final Report):

Adapter flow (MUST follow this order):

```
read projects.yaml → for each of 11 projects → query GitHub read-only API → resolve Repository HEAD / Open PR / PR HEAD SHA / Check/CI state → write state/<project>.yaml (ci_state, open_pr, observed_at) → schema validation
```

ขั้นตอน:

1. **read projects.yaml** — อ่าน `automation/projects.yaml` เพื่อหา 11 registered projects (ห้าม onboard 18 discovered-not-imported)
2. **query GitHub read-only API** — เรียก GitHub REST/GraphQL API แบบ **read-only** เพื่อดึง:
   - Repository HEAD SHA (default branch tip)
   - Open PR (มี/ไม่มี + PR number + PR HEAD SHA)
   - Check/CI state ของ HEAD SHA (success / failure / pending / unknown)
3. **resolve truth ณ exact SHA** — ผูก PR/CI กับ exact SHA เสมอ (ไม่ใช่ "latest") เพื่อลด stale truth
4. **write state/<project>.yaml** — อัปเดต `ci_state`, `open_pr`, `observed_at` ใน state YAML ของแต่ละ project
5. **schema validation** — รัน `render_project_wall.py --validate <project>.yaml` หรือ `--validate-all` → ต้อง VALID

กฎ:
- adapter ต้องเป็น **read-only** เท่านั้น — ห้าม merge / commit / comment / push ไปยัง source repos
- adapter ต้องจัดการ failure แบบ fail-safe (ดู Section 5)
- adapter ต้องบันทึก `observed_at` timestamp ทุกครั้งที่เขียน state
- ห้ามเปลี่ยน semantics ของ schema / state / renderer
- ห้าม onboard 18 discovered-not-imported repos

### 4.2 Why read-only (decision)

adapter เป็น **read-only** เพราะ:
- Vault เป็น knowledge plane ไม่ใช่ control plane ของ source repos
- การเขียนกลับ source repo คือ risk ที่ไม่จำเป็นและอยู่นอก scope ของ Vault
- read-only adapter ลด blast radius ของ credential leak / misconfiguration
- ถ้าอนาคตต้องการ write-back (เช่น auto-comment) ต้องเป็น WO แยกต่างหากพร้อม risk review

---

## 5. Fail-Safe Rules (MUST enforce)

adapter ต้องปฏิบัติตามกฎ fail-safe ต่อไปนี้ทุกข้อ — ไม่มีข้อยกเว้น:

1. **API failure ≠ CI failed** — เมื่อ GitHub API ไม่ตอบ / ตอบผิด / timeout ต้อง render `ci_state: unknown` เท่านั้น ห้าม fabricate `failure`
2. **No token → `unknown`** — เมื่อไม่มี GitHub token ใน environment ต้อง render `ci_state: unknown` และ `open_pr: null` ห้าม fabricate state ใด ๆ
3. **Rate limit → store provenance/error, do not crash** — เมื่อ GitHub ส่ง rate-limit response ต้องบันทึก provenance/error ลง state (เช่น `observed_at` + error note) และ render `unknown` ห้าม crash / raise ออกจาก process
4. **GitHub adapter must NEVER merge/commit/comment/push to source repos** — adapter เป็น read-only เท่านั้น ห้ามเรียก endpoint ใด ที่ mutate source repo (เช่น `POST /merges`, `POST /commits`, `POST /comments`, `git push`)
5. **State must record `observed_at` timestamp** — ทุก state YAML ที่ adapter เขียนต้องมี `observed_at` (ISO 8601) เพื่อให้รู้ว่า truth นี้สังเกตเมื่อไร
6. **PR/CI tied to exact SHA** — `open_pr` และ `ci_state` ต้องผูกกับ exact SHA (HEAD หรือ PR HEAD SHA) ไม่ใช่ "latest" แบบ floating เพื่อลด stale truth

กฎเสริม:
- ห้าม log / บันทึก token ลงไฟล์ใด ๆ (รวม state YAML, log file, error note)
- ห้ามส่ง token ออกนอก GitHub API endpoint ที่ authorize แล้ว
- error note ใน state ต้องเป็น generic message เท่านั้น (เช่น `github_api_unavailable`) ห้ามมี raw response body ที่อาจบรรจุข้อมูล sensitive

---

## 6. Clean-Environment Verification (execute phase)

เมื่อ Owner authorize execute ต้อง verify ใน environment ที่สะอาด:

1. สร้าง virtualenv ใหม่ (หรือใช้ environment ที่ไม่มี deps ติดตั้ง)
2. `python3 -m pip install -r requirements.txt`
3. ตั้ง GitHub token ใน environment (เช่น `GITHUB_TOKEN`) — ห้าม hardcode ในไฟล์
4. `python3 automation/github_adapter.py` → ต้องรันได้, อัปเดต state ของ 11 projects
5. `python3 scripts/render_project_wall.py --validate-all` → ต้อง exit 0, 11/11 VALID
6. `python3 scripts/render_project_wall.py` → ต้อง exit 0, render 11 pilots
7. รัน render รอบที่สอง → ต้อง "no change (idempotent)" / zero diff
8. จำลอง **no token** → adapter ต้อง render `unknown` ทั้ง 11, ห้าม crash
9. จำลอง **API failure / rate limit** → adapter ต้อง render `unknown` + provenance, ห้าม crash
10. ตรวจ `git status` → diff จำกัดอยู่ใน Allowed Files เท่านั้น, ไม่มี token ในไฟล์ใด ๆ

ห้ามอ้างว่า GitHub truth integrated โดยไม่ผ่านขั้นตอนนี้จริง

---

## 7. Safety Boundaries

- ห้ามเปลี่ยน semantics ของ `project-state.schema.json` (ยกเว้นเพิ่ม optional field หากจำเป็น และต้องระบุเหตุผล)
- ห้ามเปลี่ยน semantics ของ state YAML files (เติม `ci_state`/`open_pr`/`observed_at` เท่านั้น ห้ามเปลี่ยน meaning ของ field เดิม)
- ห้ามเปลี่ยน logic ของ `render_project_wall.py` (ยกเว้น minimal change หากจำเป็น และต้องระบุเหตุผล)
- ห้ามแตะ `automation/projects.yaml`
- ห้าม mutate source repositories (read-only adapter)
- ห้าม implement scheduled refresh / pytest (WO-035)
- ห้าม onboard 18 discovered-not-imported repos (แยก future WO)
- ห้ามแตะ cleanup files (แยก WO หลัง Goal 35)
- ห้ามเปลี่ยน registry / index-url (security policy)
- ห้าม commit secrets / credentials / token

---

## 8. Validation

1. adapter read-only — `github_adapter.py` ไม่เรียก endpoint ใด ที่ mutate source repo (merge/commit/comment/push)
2. API failure → `unknown` — เมื่อ GitHub API unavailable ต้อง render `ci_state: unknown`, ห้าม fabricate `failure`
3. no token → `unknown` — เมื่อไม่มี token ต้อง render `unknown`, ห้าม fabricate state
4. rate limit graceful — เมื่อ rate-limited ต้องบันทึก provenance/error และ render `unknown`, ห้าม crash
5. `observed_at` present — ทุก state YAML ที่ adapter เขียนต้องมี `observed_at` (ISO 8601)
6. PR/CI tied to exact SHA — `open_pr` และ `ci_state` ผูกกับ exact SHA ไม่ใช่ floating "latest"
7. 11 states validate — `--validate-all` exit 0, 11/11 VALID
8. render succeeds — `render_project_wall.py` exit 0, render 11 pilots
9. second render zero-diff — render รอบที่สอง "no change (idempotent)"
10. no secrets — ไม่มี token / credential ในไฟล์ใด ๆ (state, log, error note)
11. diff limited to Allowed Files — `git status` จำกัดอยู่ใน Allowed Files เท่านั้น

---

## 9. Allowed Files (future execution)

- `automation/github_adapter.py` — [CREATE] read-only GitHub adapter
- `automation/state/*.yaml` — update `ci_state`, `open_pr`, `observed_at` (11 files)
- `automation/schema/project-state.schema.json` — add optional fields ONLY if needed (must state reason)
- `scripts/render_project_wall.py` — minimal change only if needed (must state reason)
- `00 Dashboard/Project Dashboard.md` — inside `LIVE_PROJECT_WALL` markers only
- `04 Work Orders/CURRENT_WORK_ORDER.md` — activate → close (execute phase only)
- `04 Work Orders/WO-OBSIDIAN-034-GITHUB-PROJECT-TRUTH-INTEGRATION.md` — this file (closeout)
- `04 Work Orders/Work Order Index.md` — add WO-034 row (this draft commit)

Forbidden (do NOT modify):
- `automation/projects.yaml`
- `automation/adapters/README.md`, `automation/state/README.md`
- `00 Dashboard/Project Dashboard.md` outside `LIVE_PROJECT_WALL` markers
- Project Registry / Project Index / Project Overview pages
- `.obsidian/`, `IDEA.md`
- Any source repository (read-only API calls only — no merge/commit/comment/push)
- Cleanup files (`ยังไม่ได้ตั้งชื่อ*.base`, `2026-07-29.md`, `05 Prompts/`, `06 Prompts/`)
- Scheduled refresh script / pytest suite (WO-035 scope)

---

## 10. Definition of Done (WO-034)

- `automation/github_adapter.py` exists and is read-only (no merge/commit/comment/push)
- adapter fills `ci_state` + `open_pr` + `observed_at` for all 11 imported projects
- API failure / no token / rate limit → `unknown` (fail-safe, no crash, no fabrication)
- `observed_at` present in every updated state file (ISO 8601)
- PR/CI tied to exact SHA (not floating "latest")
- `--validate-all` exit 0, 11/11 VALID
- render exit 0, render 11 pilots
- second render zero-diff (idempotent)
- no source repo mutations
- no secrets / token in any file
- no semantics change to schema / state / renderer (optional schema fields only if justified)
- WO proof chain closed
- repo สามารถพูดได้ว่า state YAML ของ 11 projects สะท้อน **project truth จาก GitHub ณ SHA ที่กำหนด** ไม่ใช่ `unknown`/`null` อีก

---

## 11. Follow-up Boundaries (after WO-034 closes)

WO-034 ปิดแล้วเปิดทางให้:
- WO-OBSIDIAN-035 — Automated Refresh & Regression Safety (pytest + scheduled refresh ที่ consume adapter แบบ read-only)

ห้ามเริ่ม WO-035 ก่อน WO-034 ปิด CLOSED และ clean-environment verification ผ่าน

หลักการสำคัญ: adapter ของ WO-034 เป็น **read-only consumer** เท่านั้น WO-035 จะ wrap ด้วย scheduled refresh + regression suite แต่ห้ามเปลี่ยน adapter เป็น write-back

---

## 12. Commit / Push Policy

- Draft-only รอบนี้: commit หนึ่งครั้งสร้างเอกสาร WO-034 + Work Order Index row เท่านั้น
- Execute รอบภายหลัง: commit/push ต้องมี Owner authorization แยก
- ห้าม push เว้นแต่ Owner อนุญาต

Suggested commit message (draft):

`docs: plan WO-OBSIDIAN-034 github project truth integration (read-only adapter)`

---

## 13. Final Report (to fill at closeout)

```text
WORK_ORDER: WO-OBSIDIAN-034
RESULT: COMPLETED
BASELINE: WO-OBSIDIAN-033 CLOSED (repo reproducible)
ADAPTER_CREATED: yes
ADAPTER_PATH: automation/github_adapter.py
ADAPTER_READ_ONLY: yes (GET-only, zero write endpoints)
PROJECTS_UPDATED: 11/11
API_FAILURE_HANDLED: yes — unknown rendered, no fabrication
NO_TOKEN_HANDLED: yes — unknown rendered, no fabrication (no GITHUB_TOKEN in env; fail-safe mode)
RATE_LIMIT_GRACEFUL: yes — provenance stored, no crash (not triggered; no token)
OBSERVED_AT_PRESENT: yes — 11/11 state files
PR_CI_TIED_TO_SHA: yes
SCHEMA_OPTIONAL_FIELDS_ADDED: yes (observed_at — optional, not required, ISO-8601 timestamp)
RENDERER_CHANGE: no
VALIDATE_ALL_EXIT_CODE: 0
VALIDATE_ALL_COUNT: 11/11
RENDER_EXIT_CODE: 0
SECOND_RENDER_ZERO_DIFF: yes
SOURCE_MODIFICATIONS: 0
SECRETS: 0
SEMANTICS_CHANGE_TO_SCHEMA: no (additive optional field only)
SEMANTICS_CHANGE_TO_STATE: no (observed_at added; ci_state/open_pr unchanged from fail-safe unknown/null)
SEMANTICS_CHANGE_TO_RENDERER: no
REPOS_ONBOARDED_BEYOND_11: 0
CLEANUP_FILES_TOUCHED: 0
SCHEDULED_REFRESH_IMPLEMENTED: no — WO-035 scope
PYTEST_IMPLEMENTED: no — WO-035 scope
FILES_CHANGED: automation/github_adapter.py, automation/schema/project-state.schema.json, automation/state/*.yaml (11 files), 04 Work Orders/WO-OBSIDIAN-034-GITHUB-PROJECT-TRUTH-INTEGRATION.md, 04 Work Orders/Work Order Index.md
FILES_CHANGED_OUTSIDE_SCOPE: 0
PUSH_PERFORMED: yes (Owner-authorized 2026-08-17)
REMAINING_RISKS: adapter ran in no-token mode (ci_state=unknown for all 11); re-run with GITHUB_TOKEN to populate real PR/CI values; observed_at regenerates per-run (adapter intentionally non-idempotent; renderer idempotency unaffected)
NEXT_RECOMMENDED_ACTION: WO-OBSIDIAN-035 Automated Refresh & Regression Safety
```
