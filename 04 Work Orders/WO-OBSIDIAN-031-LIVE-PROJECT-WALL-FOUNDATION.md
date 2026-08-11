# WORK ORDER — LIVE PROJECT WALL FOUNDATION

Work Order ID: WO-OBSIDIAN-031
Title: WO-OBSIDIAN-031 — Live Project Wall Foundation
Risk Level: MEDIUM (foundation design, no runtime yet)
Task Classification: Vault Operational Tooling / Knowledge Layer
Execution Mode: Bounded Single Work Order (foundation-only)
Owner: Toto
Target Vault: `D:\Obsidian\Project-Knowledge-Vault`
Status: PLANNED

> ใบงานนี้เป็น **draft PLANNED เท่านั้น** — ยังไม่ Activate และห้าม execute ในรอบที่สร้างไฟล์นี้
> การ Activate + Execute ต้องรอ Owner สั่งแยกต่างหาก

---

## 1. Objective

สร้าง **foundation** สำหรับ Live Project Wall ที่แสดงสถานะปัจจุบันของ 11 imported projects โดยไม่บังคับให้ source repositories มีโครงสร้างภายในเหมือนกัน

WO นี้คือ **foundation-only**:
- ห้าม implement real-time webhook / polling daemon / background service / Obsidian plugin / automatic GitHub sync ตอนนี้

จุดสำคัญ: พิสูจน์ก่อนว่า `thai_stt_app` และ `lumina-studio` (โครงสร้าง repo ต่างกัน) สามารถถูกแปลงเป็น normalized state กลางเดียวกัน และ render Wall แบบ deterministic ได้ ถ้าสองตัวนี้ผ่าน ค่อยขยายไปอีก 9 โปรเจกต์

---

## 2. Repository Authority

Vault repository: `expellirmud-dot/Obsidian`
Local Vault: `D:\Obsidian\Project-Knowledge-Vault`
Default branch: `main`

Imported projects (11) — OUT OF SCOPE: 18 discovered-not-imported:
- `llm-agents`, `STT Typing`, `AI Worker Harness`, `Utility Disbursement App`, `Adobe Stock Upload Assistant`, `thai_stt_app`, `lumina-studio`, `lightroom-ai-exposure`, `citizen_portal`, `TalkToClibord`, `AI-Workspace`
- Discovered-not-imported (18): tooling-infrastructure ×6, sandbox-experiment ×6, backup-archive-candidate ×2, duplicate-superseded-candidate ×1, unknown ×3 — **NOT eligible** ใน WO นี้

---

## 3. Architecture (normalized state layer)

```
Source Repository
    ↓
Project Adapter / Evidence Reader
    ↓
Normalized Project State
    ↓
Project Wall Renderer
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
- GitHub PR / CI state

ห้ามบังคับ source repos ต้องใช้ layout เดียวกัน

---

## 4. Normalized Project-State Schema

Canonical representation: **YAML** (เครื่องอ่านง่าย, deterministic, ไม่พึ่ง parser ซับซ้อน)
ไฟล์: `automation/state/<project_id>.yaml` (อนุมัติในรอบ execute)

### 4.1 YAML state vs JSON Schema (rule)

> Normalized state instances are YAML.
> JSON Schema is used only as the validation contract because YAML is compatible with the JSON data model.
> Do not switch normalized project-state files from YAML to JSON.

- normalized state instances remain **YAML**
- state files remain `automation/state/<project_id>.yaml`
- `automation/schema/project-state.schema.json` is the **validation contract only**
- JSON Schema does not mean state instances become JSON — the schema validates the YAML data model, it does not dictate the on-disk instance format

Required fields (ไม่มีค่าให้ใส่ `null` / `"unknown"` / `"needs-verification"` — ห้ามเดา):

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
  path: <string | null>          # where the current-work claim came from
  kind: <work-order | current-task | handoff | roadmap | readme | other | null>
current_work_evidence: <verified | owner-confirmed | inference | unknown>   # how strongly the claim is supported
ci_state: <success | failure | pending | unknown | null>
open_pr: <pr-number | null>
last_change: <iso-date | null>
next_action: <string | null>
blockers: <string | null>
evidence_classification: <verified | owner-confirmed | inference | unknown>
verified_at: <iso-date | null>
adapter_id: <string>
```

### 4.2 Authority source vs evidence confidence (rule)

`current_work_authority` and `current_work_evidence` are **separate concerns** and must not be conflated:

- **`current_work_authority`** answers: *"Where did this current-work state come from?"*
  - `path`: the source file/path the claim was read from (or `null` if none)
  - `kind`: the type of authority document (`work-order` | `current-task` | `handoff` | `roadmap` | `readme` | `other` | `null`)
- **`current_work_evidence`** answers: *"How strongly is this claim supported?"*
  - `verified` | `owner-confirmed` | `inference` | `unknown`
- **`evidence_classification`** (kept separately) is the overall evidence confidence for the normalized state record as a whole.

The previous ambiguous scalar `current_work_authority: <verified | owner-confirmed | inference | unknown>` is **replaced** by the `current_work_authority` (path/kind) + `current_work_evidence` (confidence) pair above.

---

## 5. Evidence Classification (explicit)

- `verified` — หลักฐานจาก repo / file / command output
- `owner-confirmed` — Owner ยืนยันโดยตรง
- `inference` — สันนิษฐานจากบริบท (ต้องระบุ)
- `unknown` / `needs-verification` — ไม่มีหลักฐาน

---

## 6. Project Adapter Concept

แต่ละ imported project อาจมี evidence mapping ของตน

### 6.1 `automation/projects.yaml` registration scope (rule)

`automation/projects.yaml` is the registry of adapters and must register **all 11 imported projects**. Only `thai_stt_app` and `lumina-studio` receive executable evidence mappings/adapters in WO-031; the other 9 remain registered but disabled for the Wall pilot. The 18 discovered-not-imported repositories must **not** appear as eligible Wall projects.

Canonical per-project fields:

```yaml
projects:
  - project_id: thai_stt_app
    enabled_for_wall: true
    pilot_status: adapted
    adapter_id: generic-git-plus-authority-files
    # ... evidence mapping ...
  - project_id: lumina-studio
    enabled_for_wall: true
    pilot_status: adapted
    adapter_id: generic-git-plus-authority-files
    # ... evidence mapping ...
  # remaining 9 imported projects: registered, not adapted for the pilot
  - project_id: llm-agents
    enabled_for_wall: false
    pilot_status: not-yet-adapted
  # ... 8 more with enabled_for_wall: false, pilot_status: not-yet-adapted ...
```

- `enabled_for_wall: false` + `pilot_status: not-yet-adapted` for the 9 non-pilot imported projects
- no discovered-not-imported repository may be registered as Wall-eligible

### 6.2 Adapter evidence mapping (concept)

Conceptual config (YAML) for an adapted pilot:

```yaml
project: thai_stt_app
adapter_id: generic-git-plus-authority-files
authority_candidates:
  - AGENTS.md
  - WORK_ORDER.md
  - README.md
github:
  prs: true
  ci: true
```

WO นี้เลือก **YAML** เป็น canonical representation เดียว (adapter + state)

---

## 7. Two Data Concepts

**A. Snapshot** — current known project state (normalized state file)
**B. Event** — meaningful change (commit, PR opened/merged, CI changed, WO activated/closed, state changed)

WO นี้กำหนด contract เท่านั้น — ห้าม implement persistent event ingestion นอกเสียจาก minimal proof ที่จำเป็น

---

## 8. Preserve Existing Vault Model

ห้ามแทนที่: Project Registry, Project Overview, Recently Reviewed / verification history, Work Orders
Live Project Wall = operational view เพิ่มเติม ไม่ใช่การแทนที่ความรู้ที่ verified

---

## 9. Wall Sections (conceptual)

```
LIVE PROJECT WALL
- Project | State | Current Work | CI | PR | Last Change | Next Action | Verified At

RECENTLY REVIEWED
- audit / verification info คงเดิมแยกต่างหาก
```

---

## 10. Deterministic Rendering Rule

AI/evidence reader อาจตีความ source state แต่ Markdown rendering ต้อง deterministic จาก normalized state
ห้ามให้ AI agent เขียนใหม่ทั้ง Dashboard

---

## 11. Safety Boundaries

- Source repos READ-ONLY
- ไม่แก้ source repo
- ไม่ onboard โปรเจกต์เพิ่ม
- ไม่ infer lifecycle
- ไม่มี secrets/credentials
- ไม่แก้ `.obsidian`
- ไม่มี Community Plugin
- ไม่มี webhook / polling daemon / scheduled automation / background process
- ไม่มี CI workflow implementation ตอนนี้
- ไม่มี external service deployment

---

## 12. Expected Implementation Scope (future execution)

Allowed artifacts (WO ตัดสินใจ path ก่อน execute):
- `automation/projects.yaml` — project registry of adapters
- `automation/schema/project-state.schema.json` — JSON schema สำหรับ normalized state (validation contract only; state instances remain YAML)
- `automation/adapters/README.md` — adapter contract
- `automation/state/README.md` — state contract
- `automation/state/thai_stt_app.yaml` — pilot normalized state (YAML)
- `automation/state/lumina-studio.yaml` — pilot normalized state (YAML)
- `scripts/render_project_wall.py` — deterministic renderer
- bounded Wall section ใน `00 Dashboard/Project Dashboard.md` (within markers)

ห้ามสร้างไฟล์เหล่านี้ในรอบ draft-only นี้

---

## 13. Foundation Proof (2 pilot projects)

ใช้ `thai_stt_app` + `lumina-studio` เท่านั้น
อีก 9 imported projects คงการลงทะเบียน แต่ไม่ต้องมี adapter เต็มรูปใน WO-031

Pilot normalized state files (required execution artifacts):
- `automation/state/thai_stt_app.yaml`
- `automation/state/lumina-studio.yaml`

---

## 14. Pilot Acceptance Criteria

สำหรับทั้งสอง pilot:
- identify repo path
- resolve adapter/evidence sources
- produce normalized state
- render bounded Live Project Wall section
- preserve existing Dashboard content outside generated section
- handle unknown fields โดยไม่เดา

---

## 15. Idempotency

Renderer รันสองครั้งกับ normalized state เดียวกันต้องไม่เกิด diff เพิ่ม

---

## 16. Generated-Section Boundary

Dashboard ใช้ markers ชัดเจน:

```markdown
<!-- LIVE_PROJECT_WALL:START -->
...
<!-- LIVE_PROJECT_WALL:END -->
```

Renderer แก้ได้เฉพาะเนื้อหาใน markers เท่านั้น

---

## 17. Validation (future execution)

1. schema validation ผ่าน (JSON schema validates YAML state instances; state files remain YAML)
2. ทั้งสอง pilot normalize สำเร็จ (`automation/state/thai_stt_app.yaml`, `automation/state/lumina-studio.yaml`)
3. unknown values คง `unknown` (ไม่เดา)
4. generated Wall ไม่มี discovered-not-imported repos
5. มีได้แค่ 11 imported projects ตาม registry; only 2 enabled/adapted for the pilot
6. deterministic second render → clean diff
7. Dashboard content นอก markers ไม่เปลี่ยน
8. source repos ไม่เปลี่ยน
9. ไม่มี secrets
10. diff จำกัดเฉพาะ Allowed Files (รวม `automation/state/thai_stt_app.yaml`, `automation/state/lumina-studio.yaml`)
11. existing CRLF artifacts (`STT Typing.md`, `Work Order Index.md`) คง out-of-scope
12. owner notes คง untouched

---

## 18. Definition of Done (WO-031)

- normalized state contract มีอยู่
- adapter contract มีอยู่
- deterministic renderer มีอยู่
- pilot ทำงานสำหรับ `thai_stt_app` + `lumina-studio`
- bounded Live Project Wall render ถูกต้อง
- ไม่มี real-time automation ถูก implement
- proof chain ปิด

---

## 19. Follow-up Boundaries (after WO-031 closes)

ห้าม implement ใน WO-031:
- expand adapters ไปอีก 9 imported projects
- GitHub PR/CI integration
- scheduled polling
- event history
- webhook/event-driven sync

---

## 20. Allowed Files (future execution)

- `automation/projects.yaml`
- `automation/schema/project-state.schema.json`
- `automation/adapters/README.md`
- `automation/state/README.md`
- `automation/state/thai_stt_app.yaml`
- `automation/state/lumina-studio.yaml`
- `scripts/render_project_wall.py`
- `00 Dashboard/Project Dashboard.md` (เฉพาะภายใน LIVE_PROJECT_WALL markers)
- `04 Work Orders/CURRENT_WORK_ORDER.md` (activate → close)
- `04 Work Orders/WO-OBSIDIAN-031-LIVE-PROJECT-WALL-FOUNDATION.md` (closeout)

ห้ามแก้ Project Registry / Project Overview ในรอบนี้ เว้นจำเป็นต้องอ้างอิง

---

## 21. Commit / Push Policy

- Draft-only รอบนี้: commit หนึ่งครั้งสร้างเอกสาร WO-031 เท่านั้น (stage เฉพาะไฟล์ WO-031)
- Execute รอบภายหลัง: commit/push ต้องมี Owner authorization แยก
- ห้าม push เว้นแต่ Owner อนุญาต

Suggested commit message (draft):

`docs: add WO-OBSIDIAN-031 live project wall foundation (planned)`
