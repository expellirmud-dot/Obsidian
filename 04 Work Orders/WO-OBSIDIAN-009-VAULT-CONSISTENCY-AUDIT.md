# WORK ORDER — VAULT CONSISTENCY AUDIT

Work Order ID: WO-OBSIDIAN-009
Title: Audit Project Knowledge Vault Consistency
Status: PLANNED
Task Classification: VAULT_GOVERNANCE_AND_CONSISTENCY_AUDIT
Risk Level: MEDIUM
Execution Mode: One Vault, One Bounded Audit

Owner: Toto
Vault Root: `D:\Obsidian\Project-Knowledge-Vault`

Depends On: WO-OBSIDIAN-008 CLOSED
Commit Authorization: YES — one Vault commit after validation
Push Authorization: NO

---

## 1. Objective

ตรวจความสอดคล้องของ Vault ทั้งระบบหลัง onboarding โปรเจกต์ โดยไม่แก้ Source Repository ใด ๆ

## 2. Audit Scope

ตรวจเฉพาะ:

- frontmatter schema และ key ซ้ำ
- project lifecycle / execution state terminology
- repository path และ path escaping
- internal links / orphaned links
- CURRENT_WORK_ORDER และ Work Order Index
- evidence labels และ verification records
- Resume Context / Required Reads / Next Action
- Dashboard, Project Index และ Architecture Index consistency
- stale or contradictory statements ระหว่าง Vault pages

## 3. Required Read Order

1. `AGENTS.md`
2. `.agents/skills/project-read-first/SKILL.md`
3. `04 Work Orders/CURRENT_WORK_ORDER.md`
4. Work Order ฉบับนี้
5. Dashboard และ Indexes ทั้งหมด
6. Project pages และ Architecture overviews ทุกโปรเจกต์
7. Work Orders 003–008

## 4. Boundaries

- Vault-only; ห้ามแก้ Source Repository
- ห้าม pull/checkout/reset/clean/stash
- ห้ามรัน runtime, provider หรือ external service
- ห้ามเปิด secrets
- ใช้ surgical edits เท่านั้น
- ห้ามเปลี่ยน factual project state โดยไม่มี evidence

## 5. Required Outputs

```text
AUDIT_INVENTORY
SCHEMA_FINDINGS
LINK_FINDINGS
PATH_FINDINGS
STATUS_TERMINOLOGY_FINDINGS
EVIDENCE_CLASSIFICATION_FINDINGS
STALE_OR_CONTRADICTORY_FINDINGS
FILES_REQUIRING_REMEDIATION
NO_CHANGE_ITEMS
REMAINING_UNVERIFIED_ITEMS
```

## 6. Allowed Files

```text
00 Dashboard/Project Dashboard.md
01 Projects/*.md
02 Architecture/*.md
04 Work Orders/CURRENT_WORK_ORDER.md
04 Work Orders/WO-OBSIDIAN-009-VAULT-CONSISTENCY-AUDIT.md
04 Work Orders/Work Order Index.md
```

ห้ามแก้ไฟล์อื่นโดยไม่มี Stop Condition + Owner decision

## 7. Validation

```text
Source repositories modified: 0
Vault files outside allowed scope: 0
Broken internal links: 0 except marked placeholders
Duplicate frontmatter keys: 0
Path escaping defects: 0
Contradictory lifecycle/execution states: 0 or explicitly qualified
Evidence labels consistent: yes
CURRENT_WORK_ORDER consistent: yes
Secrets added: 0
Push performed: 0
```

รัน `git diff --check` และตรวจ staged diff แบบ explicit

## 8. Definition of Done

1. Audit inventory ครบ
2. Findings ถูกแก้แบบ surgical หรือบันทึกเป็น NEEDS_VERIFICATION
3. Dashboard/Indexes/Project pages สอดคล้องกัน
4. `CURRENT_WORK_ORDER.md` เป็น CLOSED
5. Validation ผ่าน
6. Commit หนึ่งครั้ง
7. ไม่มี Push

Commit message:

```text
docs: audit Vault consistency
```

## 9. Final Report

```text
WORK_ORDER: WO-OBSIDIAN-009
RESULT: COMPLETED | PARTIAL | BLOCKED
FILES_AUDITED:
FILES_CHANGED:
BROKEN_LINKS_FIXED:
SCHEMA_ISSUES_FIXED:
CONTRADICTIONS_QUALIFIED:
FILES_CHANGED_OUTSIDE_SCOPE:
VAULT_COMMIT:
PUSH_PERFORMED:
REMAINING_RISKS:
NEXT_RECOMMENDED_ACTION:
```
