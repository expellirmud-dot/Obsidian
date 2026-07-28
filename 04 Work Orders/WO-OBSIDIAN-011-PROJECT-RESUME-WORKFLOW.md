# WORK ORDER — PROJECT RESUME WORKFLOW

Work Order ID: WO-OBSIDIAN-011
Title: Define Project Resume Workflow
Status: PLANNED
Task Classification: VAULT_WORKFLOW_AND_RESUME_CONTROL
Risk Level: MEDIUM
Execution Mode: One Workflow Seam

Owner: Toto
Vault Root: `D:\Obsidian\Project-Knowledge-Vault`

Depends On: WO-OBSIDIAN-010 CLOSED
Commit Authorization: YES — one Vault commit after validation
Push Authorization: NO

---

## 1. Objective

กำหนด workflow มาตรฐานสำหรับกลับมาทำงานแต่ละโปรเจกต์จาก Vault โดยไม่ใช้ข้อมูลล้าสมัย ไม่ข้าม authority และไม่แก้ Source Repository ก่อน readiness gate ผ่าน

## 2. Resume Workflow Requirements

Workflow ต้องครอบคลุม:

1. เลือก Project page
2. อ่าน Resume Context และ Verification Record
3. ตรวจ staleness ตาม policy จาก WO-010
4. Resolve exact Source Git root
5. ตรวจ branch, HEAD, upstream, status และ authority pointer
6. ตัดสินว่า re-verification ระดับใดจำเป็น
7. ตรวจ Serena/CodeGraph exact root เมื่อจะ inspect source code
8. สร้าง bounded Work Order ใหม่
9. แยก Controller/Worker responsibilities
10. Validation, explicit staging, single-task commit และ push authorization
11. Stop Conditions และ Owner decision points
12. Closeout และอัปเดต Vault เมื่อ repository truth เปลี่ยน

## 3. Required Read Order

1. `AGENTS.md`
2. `.agents/skills/project-read-first/SKILL.md`
3. `.agents/skills/project-context-discovery/SKILL.md`
4. Decision จาก WO-010
5. `04 Work Orders/CURRENT_WORK_ORDER.md`
6. Work Order ฉบับนี้
7. Resume Context ของทุก Project page
8. ตัวอย่าง Work Orders 004–008

## 4. Boundaries

- Vault-only; ห้าม dispatch Worker หรือแก้ Source Repository
- ห้ามรัน runtime/provider/external service
- ห้ามสร้าง project-specific implementation plan ที่เกิน workflow template
- ห้ามฝัง model/provider ที่เปลี่ยนง่ายเป็น authority ถาวร
- ห้ามเปิด secrets

## 5. Required Outputs

สร้างหรืออัปเดตเฉพาะ:

```text
05 Prompts/Project Resume Workflow.md
05 Prompts/Prompt Index.md
00 Dashboard/Project Dashboard.md
01 Projects/*.md
04 Work Orders/CURRENT_WORK_ORDER.md
04 Work Orders/WO-OBSIDIAN-011-PROJECT-RESUME-WORKFLOW.md
04 Work Orders/Work Order Index.md
```

Workflow artifact ต้องมี:

- universal resume checklist
- readiness gate
- staleness/re-verification decision tree
- source read-only preflight
- bounded Work Order bootstrap template
- stop-condition template
- final report template
- examples สำหรับอย่างน้อย 3 โปรเจกต์

Project pages แก้ได้เฉพาะเพื่อเพิ่มลิงก์ workflow หรือทำให้ Resume Context ใช้ schema เดียวกัน ห้ามเปลี่ยน project facts

## 6. Validation

```text
Source repositories modified: 0
Workflow conflicts with AGENTS/skills/policy: 0
Readiness gate present: yes
Stop conditions present: yes
Controller/Worker boundaries present: yes
Explicit staging and push authorization present: yes
Project facts changed without evidence: 0
Internal links unresolved: 0 except marked placeholders
Secrets added: 0
Push performed: 0
```

## 7. Definition of Done

1. Resume workflow ใช้ได้กับทุกโปรเจกต์ใน Vault
2. เชื่อมกับ policy WO-010 และ skills ปัจจุบัน
3. มี reusable checklist/templates ครบ
4. Project pages เชื่อม workflow โดยไม่เปลี่ยน facts
5. `CURRENT_WORK_ORDER.md` เป็น CLOSED
6. Validation ผ่าน
7. Commit หนึ่งครั้ง
8. ไม่มี Push

Commit message:

```text
docs: add project resume workflow
```

## 8. Final Report

```text
WORK_ORDER: WO-OBSIDIAN-011
RESULT: COMPLETED | PARTIAL | BLOCKED
WORKFLOW_FILE:
PROJECT_PAGES_LINKED:
FILES_CHANGED:
FILES_CHANGED_OUTSIDE_SCOPE:
VAULT_COMMIT:
PUSH_PERFORMED:
REMAINING_RISKS:
NEXT_RECOMMENDED_ACTION:
```
