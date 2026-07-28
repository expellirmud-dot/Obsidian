# WORK ORDER — ONBOARD AI WORKER HARNESS

Work Order ID: WO-OBSIDIAN-006  
Title: Onboard AI Worker Harness into Project Knowledge Vault  
Status: COMPLETED
Task Classification: EXTERNAL_PROJECT_DISCOVERY_AND_VAULT_UPDATE  
Risk Level: MEDIUM  
Execution Mode: One Repository, One Bounded Seam

Owner: Toto  
Vault Root: `D:\Obsidian\Project-Knowledge-Vault`  
Source Repository: `D:\ai-tools\ai-worker-harness`

Depends On: WO-OBSIDIAN-005 CLOSED  
Pull Authorization: YES — fast-forward only  
Commit Authorization: YES — one Vault commit after validation  
Push Authorization: NO

---

## 1. Objective

ใช้ `project-read-first` และ `project-context-discovery` ตรวจ Repository truth ของ AI Worker Harness แบบ read-only แล้วอัปเดต Vault ให้สะท้อนหน้าที่จริงของ Harness, authority/control flow, Work Order lifecycle, validation/evidence boundaries, current roadmap state, risks และ resume context

---

## 2. Required Read Order

### Vault

1. `AGENTS.md`
2. `.agents/skills/project-read-first/SKILL.md`
3. `.agents/skills/project-context-discovery/SKILL.md`
4. `04 Work Orders/CURRENT_WORK_ORDER.md`
5. Work Order ฉบับนี้
6. `01 Projects/AI Worker Harness.md`
7. `01 Projects/Project Index.md`
8. `00 Dashboard/Project Dashboard.md`

### Source Repository

1. Resolve exact Git root จาก `D:\ai-tools\ai-worker-harness`
2. อ่าน root governance/authority files ที่ค้นพบ
3. อ่าน Current Work Order/Goal pointer และ active authority
4. อ่าน README หรือ documentation index
5. อ่าน roadmap/status, controller/worker contracts, validation/evidence และ runtime boundaries แบบ targeted
6. Inspect source symbols เฉพาะเมื่อเอกสารไม่เพียงพอ

ห้ามใช้รายงานการทดลองเก่าหรือชื่อ Goal เป็นหลักฐาน current state โดยไม่ตรวจ Git truth

---

## 3. Source Repository Boundary

Source Repository เป็น read-only:

- ห้ามแก้ Work Order, Goal, source, tests, configuration หรือ Git state
- ห้าม dispatch Worker/Provider
- ห้ามรัน live evaluation
- ห้าม stage/commit/push
- ห้าม checkout/reset/clean/stash
- ห้ามติดตั้ง dependency
- ห้ามเปิด Secret/Credential

หากต้อง inspect source code ให้ Serena และ CodeGraph ตรง exact Git root ก่อน

---

## 4. Required Evidence

รวบรวม:

```text
REPOSITORY_ROOT
REMOTE
BRANCH
HEAD
UPSTREAM
GIT_STATUS
AUTHORITY_FILES
CURRENT_GOAL_OR_WORK_ORDER
CURRENT_STATUS
PROJECT_PURPOSE
CONTROL_PLANE_BOUNDARIES
CONTROLLER_WORKER_BOUNDARY
WORK_ORDER_LIFECYCLE
VALIDATION_AND_EVIDENCE_FLOW
RUNTIME_PROVIDER_BOUNDARY
CURRENT_ROADMAP_SEAM
COMPLETED_WORK
OPEN_WORK
KNOWN_RISKS
DO_NOT_REPEAT
REQUIRED_READS
NEXT_RECOMMENDED_ACTION
```

ต้องแยกผลการทดลองเป็น:

- completed/scored evidence
- inconclusive/not-scoreable evidence
- current authority
- historical evidence

ทุกข้อสรุปต้องระบุ:

- `VERIFIED_REPOSITORY_FACT`
- `OWNER_CONFIRMED_FACT`
- `SUPPORTED_INFERENCE`
- `NEEDS_VERIFICATION`

---

## 5. Vault Updates

แก้หรือสร้างเฉพาะ:

```text
01 Projects/AI Worker Harness.md
01 Projects/Project Index.md
00 Dashboard/Project Dashboard.md
02 Architecture/ARCH-AI-Worker-Harness-Overview.md
02 Architecture/Architecture Index.md
04 Work Orders/CURRENT_WORK_ORDER.md
04 Work Orders/WO-OBSIDIAN-006-ONBOARD-AI-WORKER-HARNESS.md
04 Work Orders/Work Order Index.md
```

หน้า Project ต้องอัปเดต:

- verified frontmatter
- purpose/problem/scope
- repository truth
- current Goal/Work Order
- architecture/control boundary summary
- validation/evidence lifecycle
- completed/open work
- risks/do-not-repeat
- Resume Context
- Verification Record พร้อม branch/HEAD/date
- ลิงก์ `[[ARCH-AI-Worker-Harness-Overview]]`

---

## 6. Architecture Note

สร้าง `02 Architecture/ARCH-AI-Worker-Harness-Overview.md` โดยสรุป:

- Owner/Controller/Worker roles
- Development control plane และ runtime execution plane ตาม repo truth
- Work Order dispatch and closeout flow
- Provider/tool boundary
- Validation, evidence และ terminal status flow
- Retry/loop/process-settlement boundaries หากเป็น current architecture
- Safety/authority boundaries
- Known limitations
- Evidence sources
- Last verified HEAD/date
- ลิงก์กลับ `[[AI Worker Harness]]`

ห้ามนำ historical proposal มาเขียนเป็น implemented architecture

---

## 7. Stop Conditions

หยุดเมื่อ:

- Path ไม่มีหรือ Git root ไม่ตรง
- Goal/Work Order pointer หรือ authority ขัดแย้ง
- Worktree state ทำให้แยก current/historical truth ไม่ได้
- ต้อง dispatch Worker หรือรัน live provider
- ต้องแก้ Source Repository
- ต้องใช้ Secret/Credential หรือ Owner decision
- Serena/CodeGraph mismatch เมื่อจำเป็นต้อง inspect source

---

## 8. Validation

ยืนยัน:

```text
Source repository modified: 0
Workers/providers dispatched: 0
Live evaluations run: 0
Vault files outside allowed scope: 0
Project page required sections: complete
Branch/HEAD/status recorded: yes
Current Goal/Work Order recorded: yes or explicitly NONE
Historical vs current evidence separated: yes
Architecture claims grounded: yes
Internal links unresolved: 0 except marked placeholders
Duplicate frontmatter keys: 0
Secrets added: 0
Push performed: 0
```

รัน `git diff --check` ใน Vault และตรวจ staged diff ก่อน commit

---

## 9. Definition of Done

1. Source Repository ถูกตรวจแบบ read-only
2. Harness Project Page ตรงกับ current repository authority
3. Resume Context ใช้เริ่มงานใหม่ได้
4. Architecture overview แยก control/runtime/evidence boundaries ชัดเจน
5. Historical และ current state ไม่ปะปนกัน
6. Dashboard/Project Index สอดคล้องกัน
7. Verification Record มี HEAD และวันที่
8. `CURRENT_WORK_ORDER.md` เปลี่ยนเป็น `CLOSED`
9. Validation ผ่านทั้งหมด
10. Commit หนึ่งครั้ง
11. ไม่มี Push

Commit message:

```text
docs: onboard AI Worker Harness context
```

---

## 10. Final Report

```text
WORK_ORDER: WO-OBSIDIAN-006
RESULT: COMPLETED

SOURCE_REPOSITORY_ROOT: D:\ai-tools\ai-worker-harness
SOURCE_BRANCH: main
SOURCE_HEAD: 7096991892cead77a40c0178c57c9589839b1518
SOURCE_GIT_STATUS: 1 modified (work-order/templates/CONTROLLER_SESSION_BOOTSTRAP.md), 3 untracked (.benchmark-sandbox/r07-runs/, work-order/Goal-10.md, work-order/HARNESS_GOAL09_CONTROLLER_HANDOFF.md)
SOURCE_FILES_MODIFIED: 0
WORKERS_OR_PROVIDERS_DISPATCHED: 0

VAULT_HEAD_BEFORE: 98c796b5a3003066def9c4b857f495228b90340f
VAULT_HEAD_AFTER: <commit-sha>
VAULT_COMMIT: <commit-sha>
VAULT_FILES_CREATED: 02 Architecture/ARCH-AI-Worker-Harness-Overview.md
VAULT_FILES_UPDATED: 01 Projects/AI Worker Harness.md, 01 Projects/Project Index.md, 00 Dashboard/Project Dashboard.md, 02 Architecture/Architecture Index.md, 04 Work Orders/CURRENT_WORK_ORDER.md, 04 Work Orders/WO-OBSIDIAN-006-ONBOARD-AI-WORKER-HARNESS.md, 04 Work Orders/Work Order Index.md
FILES_CHANGED_OUTSIDE_SCOPE: 0

AUTHORITY_FILES_READ: AGENTS.md, README.md, work-order/CURRENT_WORK_ORDER.md, docs/HARNESS_CURRENT_STATUS.md, docs/GOAL_EXECUTION_CONTRACT.md, docs/DOCS_INDEX.md, work-order/Goal-09.md (harnes repo)
CURRENT_GOAL_OR_WORK_ORDER: Goal-09, WO-G9-R07-TASK-CLASS-EVALUATION-ROBUSTNESS (ACTIVE)
DISCOVERY_DECISION: COMPLETE
VERIFICATION_STATUS: VERIFIED_REPOSITORY_FACT — branch/HEAD/status/authority ยืนยันจาก source truth
UNVERIFIED_ITEMS: รายละเอียด route policy, model routing, internal implementation details (not inspected per WO scope)

SECRETS_ADDED: 0
PUSH_PERFORMED: 0
REMAINING_RISKS: Source repo worktree dirty (active campaign context); no fresh full-suite for HEAD 7096991; Vault needs periodic re-verification
NEXT_RECOMMENDED_ACTION: WO-OBSIDIAN-007 — Onboard Adobe Stock Upload Assistant
```
