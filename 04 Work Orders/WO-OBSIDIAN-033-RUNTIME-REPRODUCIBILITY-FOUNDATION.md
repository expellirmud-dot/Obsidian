# WORK ORDER — RUNTIME REPRODUCIBILITY FOUNDATION

Work Order ID: WO-OBSIDIAN-033
Title: WO-OBSIDIAN-033 — Runtime Reproducibility Foundation
Risk Level: LOW (dependency manifest + bootstrap docs + clean-environment verification; no semantics change)
Task Classification: Vault Operational Tooling / Reproducibility Layer
Execution Mode: Bounded Single Work Order (foundation-only)
Owner: Toto
Target Vault: `D:\Obsidian\Project-Knowledge-Vault`
Status: PLANNED

> ใบงานนี้เป็น **draft PLANNED เท่านั้น** — ยังไม่ Activate และห้าม execute ในรอบที่สร้างไฟล์นี้
> การ Activate + Execute ต้องรอ Owner สั่งแยกต่างหาก
> Baseline: WO-OBSIDIAN-032 CLOSED (HEAD `7c725e848ec6756f179c82fa698a19dff16c244b`)

---

## 1. Objective

ทำให้ Vault **reproducible จริง** บน fresh clone: โคลนใหม่ → ติดตั้ง dependencies → `validate-all` และ `render` ได้ทันทีโดยไม่ต้องเดา dependencies

ปัจจุบัน `scripts/render_project_wall.py` ใช้ `PyYAML` และ `jsonschema` แต่ไม่มี dependency manifest ใด ๆ ใน repo (ไม่มี `requirements.txt` / `pyproject.toml` / lockfile) ทำให้ fresh clone รันไม่ได้จนกว่าจะติดตั้งเองด้วยมือ นี่คือ dependency ของทุก automation ในอนาคต (WO-034, WO-035) จึงต้องผ่านก่อนเสมอ

WO นี้คือ **foundation-only**:
- ห้ามเปลี่ยน semantics ของ state / schema / renderer
- ห้าม implement GitHub integration (ไว้ WO-034)
- ห้าม implement scheduled refresh / pytest suite (ไว้ WO-035)
- ห้ามแตะ cleanup files (`ยังไม่ได้ตั้งชื่อ*.base`, empty daily note, `05 Prompts/` vs `06 Prompts/`) — แยก WO หลัง Goal 35

จุดสำคัญ: หลัง WO-033 ปิด ต้องสามารถพูดได้ว่า repo **reproducible จริง** ไม่ใช่ "healthy and operational for current manual-governed scope" อีกต่อไป

---

## 2. Repository Authority

Vault repository: `expellirmud-dot/Obsidian`
Local Vault: `D:\Obsidian\Project-Knowledge-Vault`
Default branch: `main`
Baseline: WO-OBSIDIAN-032 CLOSED (HEAD `7c725e848ec6756f179c82fa698a19dff16c244b`)

Imported projects (11) — OUT OF SCOPE (no source repo access in this WO):
- ทั้ง 11 imported projects และ 18 discovered-not-imported อยู่นอกขอบเขต
- WO นี้แตะเฉพาะไฟล์ใน Vault repo เท่านั้น

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

WO-033 ไม่เปลี่ยนแปลง architecture นี้ เพิ่มเติมเฉพาะ **reproducibility layer** ที่อยู่รอบ ๆ renderer:

```
requirements.txt  (NEW — pinned dependency ranges)
README.md        (UPDATE — bootstrap + validation commands)
```

---

## 4. Dependency Manifest (NEW)

### 4.1 File: `requirements.txt`

สร้างไฟล์ใหม่ที่ root ของ repo:

```text
# Runtime dependencies for scripts/render_project_wall.py
# Created by WO-OBSIDIAN-033 (Runtime Reproducibility Foundation).
# Pin ranges, not exact pins, to avoid unnecessary churn; tighten in WO-035 if needed.

PyYAML>=6.0,<7.0
jsonschema>=4.18,<5.0
```

กฎ:
- pin เป็น **range** ไม่ใช่ exact pin (ลด churn; ถ้าจำเป็นค่อย tighten ใน WO-035)
- ห้ามเพิ่ม dependency ที่ renderer ไม่ได้ใช้จริง
- ห้ามเพิ่ม dev/test dependency ในไฟล์นี้ (ไว้ WO-035 เมื่อมี pytest)
- ห้ามเปลี่ยน registry / index-url / extra-index-url (security policy)

### 4.2 Why not `pyproject.toml` (decision)

ใช้ `requirements.txt` เพราะ:
- repo ยังไม่มี Python package structure (ไม่มี `setup.py` / `pyproject.toml` / `src/` layout)
- renderer เป็น single script ไม่ใช่ installable package
- `requirements.txt` เพียงพอและตรงกับสถานการณ์ปัจจุบัน
- ถ้า WO-035 เพิ่ม pytest และต้องการ editable install ค่อยพิจารณา `pyproject.toml`

---

## 5. Bootstrap & Validation Commands (README update)

เพิ่ม section ใน `README.md` ใต้ส่วน Work Order Authority หรือก่อน "วิธีเพิ่มโปรเจกต์ใหม่":

```markdown
## Runtime Setup (Live Project Wall)

สำหรับการรัน `scripts/render_project_wall.py` บน fresh clone:

```bash
# 1. ติดตั้ง dependencies
python3 -m pip install -r requirements.txt

# 2. Validate ทุก state file (ต้อง 11/11 VALID)
python3 scripts/render_project_wall.py --validate-all

# 3. Render Live Project Wall (idempotent — รอบที่สองต้อง zero diff)
python3 scripts/render_project_wall.py

# 4. Validate state file เดียว
python3 scripts/render_project_wall.py --validate automation/state/<project_id>.yaml
```

ต้องการ: Python 3.10+ (ใช้ `from __future__ import annotations` และ `list[str]` hints)
```

กฎ:
- ห้ามลบหรือเปลี่ยนเนื้อหา README เดิม เพิ่ม section ใหม่เท่านั้น
- คำสั่งต้องตรงกับ usage string ใน `render_project_wall.py` จริง

---

## 6. Clean-Environment Verification (execute phase)

เมื่อ Owner authorize execute ต้อง verify ใน environment ที่สะอาด:

1. สร้าง virtualenv ใหม่ (หรือใช้ environment ที่ไม่มี `PyYAML`/`jsonschema` ติดตั้ง)
2. `python3 -m pip install -r requirements.txt`
3. `python3 scripts/render_project_wall.py --validate-all` → ต้อง exit 0, 11/11 VALID
4. `python3 scripts/render_project_wall.py` → ต้อง exit 0, render 11 pilots
5. รัน render รอบที่สอง → ต้อง "no change (idempotent)" / zero diff
6. ตรวจ `git status` → Dashboard ไม่เปลี่ยน (เพราะ idempotent), เฉพาะ `requirements.txt` และ `README.md` เท่านั้นที่ dirty

ห้ามอ้างว่า reproducible โดยไม่ผ่านขั้นตอนนี้จริง

---

## 7. Safety Boundaries

- ห้ามเปลี่ยน semantics ของ `project-state.schema.json`
- ห้ามเปลี่ยน semantics ของ state YAML files
- ห้ามเปลี่ยน logic ของ `render_project_wall.py` (ยกเว้น minimal compatibility fix หากจำเป็น และต้องระบุเหตุผล)
- ห้ามแตะ `automation/projects.yaml`, `automation/state/*.yaml`, `automation/schema/*`
- ห้ามแตะ cleanup files (แยก WO หลัง Goal 35)
- ห้าม implement GitHub integration (WO-034)
- ห้าม implement pytest / scheduled refresh (WO-035)
- ห้ามเปลี่ยน registry / index-url (security policy)
- ห้าม commit secrets / credentials

---

## 8. Validation

1. `requirements.txt` exists at repo root
2. `requirements.txt` contains `PyYAML` and `jsonschema` ranges only (no extras)
3. README bootstrap section present and commands match renderer usage
4. clean-environment install succeeds from `requirements.txt`
5. `--validate-all` exits 0 (11/11 VALID) in clean env
6. render exits 0 in clean env
7. second render zero-diff (idempotent)
8. Dashboard outside markers unchanged
9. no semantics change to schema / state / renderer
10. no secrets
11. diff limited to Allowed Files

---

## 9. Allowed Files (future execution)

- `requirements.txt` — [CREATE]
- `README.md` — add Runtime Setup section only
- `04 Work Orders/CURRENT_WORK_ORDER.md` — activate → close (execute phase only)
- `04 Work Orders/WO-OBSIDIAN-033-RUNTIME-REPRODUCIBILITY-FOUNDATION.md` — this file (closeout)
- `04 Work Orders/Work Order Index.md` — add WO-033 row (this draft commit)

Forbidden (do NOT modify):
- `scripts/render_project_wall.py` (unless minimal compatibility fix with stated reason)
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

## 10. Definition of Done (WO-033)

- `requirements.txt` exists and pins `PyYAML` + `jsonschema` ranges
- README has bootstrap + validation commands matching renderer usage
- clean-environment verification passed (install → validate-all → render → idempotent)
- 11/11 state files VALID in clean env
- render zero-diff on second run in clean env
- no semantics change to schema / state / renderer
- Dashboard outside markers preserved
- no secrets
- WO proof chain closed
- repo สามารถเรียกได้ว่า **reproducible** จริง (ไม่ใช่ "manual-governed scope" อีก)

---

## 11. Follow-up Boundaries (after WO-033 closes)

WO-033 ปิดแล้วเปิดทางให้:
- WO-OBSIDIAN-034 — GitHub Project Truth Integration (read-only PR/CI/HEAD for 11 projects)
- WO-OBSIDIAN-035 — Automated Refresh & Regression Safety (pytest + scheduled refresh)

ห้ามเริ่ม WO-034 ก่อน WO-033 ปิด CLOSED และ clean-environment verification ผ่าน

---

## 12. Commit / Push Policy

- Draft-only รอบนี้: commit หนึ่งครั้งสร้างเอกสาร WO-033 + Work Order Index row เท่านั้น
- Execute รอบภายหลัง: commit/push ต้องมี Owner authorization แยก
- ห้าม push เว้นแต่ Owner อนุญาต

Suggested commit message (draft):

`docs: plan WO-OBSIDIAN-033 runtime reproducibility foundation (requirements.txt + bootstrap)`

---

## 13. Final Report (to fill at closeout)

```text
WORK_ORDER: WO-OBSIDIAN-033
RESULT: <COMPLETED | BLOCKED | PARTIAL>
BASELINE: WO-OBSIDIAN-032 CLOSED (HEAD 7c725e8)
REQUIREMENTS_TXT_CREATED: <yes | no>
README_BOOTSTRAP_SECTION_ADDED: <yes | no>
CLEAN_ENV_INSTALL_OK: <yes | no>
VALIDATE_ALL_EXIT_CODE: <0 | nonzero>
VALIDATE_ALL_COUNT: <11/11 | other>
RENDER_EXIT_CODE: <0 | nonzero>
SECOND_RENDER_ZERO_DIFF: <yes | no>
DASHBOARD_OUTSIDE_MARKERS_UNCHANGED: <yes | no>
SEMANTICS_CHANGE_TO_SCHEMA: <no | yes (reason)>
SEMANTICS_CHANGE_TO_STATE: <no | yes (reason)>
SEMANTICS_CHANGE_TO_RENDERER: <no | yes (reason)>
SOURCE_MODIFICATIONS: 0
SECRETS: 0
FILES_CHANGED: <list>
FILES_CHANGED_OUTSIDE_SCOPE: 0
PUSH_PERFORMED: <yes | no>
REMAINING_RISKS: <list or none>
NEXT_RECOMMENDED_ACTION: WO-OBSIDIAN-034 GitHub Project Truth Integration
```
