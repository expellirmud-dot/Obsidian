# WORK ORDER — STALENESS AND RE-VERIFICATION POLICY

Work Order ID: WO-OBSIDIAN-010
Title: Define Vault Staleness and Re-verification Policy
Status: ACTIVE
Task Classification: VAULT_POLICY_AND_GOVERNANCE
Risk Level: LOW
Execution Mode: One Policy Seam

Owner: Toto
Vault Root: `D:\Obsidian\Project-Knowledge-Vault`

Depends On: WO-OBSIDIAN-009 CLOSED
Commit Authorization: YES — one Vault commit after validation
Push Authorization: NO

---

## 1. Objective

กำหนดนโยบายว่า Project/Architecture/Resume Context ใดถือว่าสด, ล้าสมัย หรือจำเป็นต้องตรวจ Repository ใหม่ โดยแยก metadata freshness ออกจาก content truth

## 2. Policy Questions

ต้องตอบให้ชัด:

1. อะไรทำให้ข้อมูล stale: HEAD เปลี่ยน, Current Task เปลี่ยน, authority เปลี่ยน, dirty state เปลี่ยน หรือเวลาผ่านไป
2. ข้อมูลประเภทใดตรวจซ้ำทุกครั้ง และประเภทใดใช้ verification เดิมได้
3. เมื่อใดใช้ `VERIFIED_REPOSITORY_FACT`, `OWNER_CONFIRMED_FACT`, `SUPPORTED_INFERENCE`, `NEEDS_VERIFICATION`
4. วิธีระบุ `last_verified_head`, `last_verified_date`, `verification_scope`
5. วิธีแสดง partial verification และ dirty-working-tree observations
6. วิธี re-verify โดยไม่อ่าน Repository กว้างเกินจำเป็น
7. กฎห้ามถือ ModifiedAt/commit date เป็นหลักฐานความสดของเนื้อหาเพียงอย่างเดียว

## 3. Required Read Order

1. `AGENTS.md`
2. `.agents/skills/project-read-first/SKILL.md`
3. `.agents/skills/project-context-discovery/SKILL.md`
4. `04 Work Orders/CURRENT_WORK_ORDER.md`
5. Work Order ฉบับนี้
6. Project pages และ Verification Records ทุกโปรเจกต์
7. ผล WO-009 consistency audit

## 4. Boundaries

- Vault-only
- ห้ามตรวจหรือแก้ Source Repository เว้นแต่ policy example แบบ read-only ที่ไม่ต้องเปิด source code
- ห้ามเปลี่ยน project facts ระหว่างงาน policy
- ห้ามเพิ่ม automation หรือ scripts ใน Work Order นี้
- ห้ามเปิด secrets หรือ external services

## 5. Required Outputs

สร้างหรืออัปเดตเฉพาะ:

```text
03 Decisions/DEC-Vault-Staleness-and-Reverification-Policy.md
03 Decisions/Decision Index.md
00 Dashboard/Project Dashboard.md
04 Work Orders/CURRENT_WORK_ORDER.md
04 Work Orders/WO-OBSIDIAN-010-STALENESS-AND-REVERIFICATION-POLICY.md
04 Work Orders/Work Order Index.md
```

Policy ต้องมี:

- freshness states
- staleness triggers
- minimum re-verification checks
- evidence classification rules
- dirty-worktree handling
- partial verification rules
- update/closeout procedure
- examples อย่างน้อย 3 กรณี

## 6. Validation

```text
Source repositories modified: 0
Policy conflicts with AGENTS/skills: 0
Evidence labels defined: yes
Dirty-working-tree policy defined: yes
Partial verification policy defined: yes
Examples present: at least 3
Internal links unresolved: 0 except marked placeholders
Secrets added: 0
Push performed: 0
```

## 7. Definition of Done

1. Policy ตอบ Policy Questions ครบ
2. Decision record เชื่อมกับ Dashboard และ Index
3. ไม่มีการเปลี่ยน project truth โดยไม่มี evidence
4. `CURRENT_WORK_ORDER.md` เป็น CLOSED
5. Validation ผ่าน
6. Commit หนึ่งครั้ง
7. ไม่มี Push

Commit message:

```text
docs: define Vault re-verification policy
```

## 8. Final Report

```text
WORK_ORDER: WO-OBSIDIAN-010
RESULT: COMPLETED | PARTIAL | BLOCKED
DECISION_FILE:
POLICY_VERSION:
FILES_CHANGED:
FILES_CHANGED_OUTSIDE_SCOPE:
VAULT_COMMIT:
PUSH_PERFORMED:
REMAINING_RISKS:
NEXT_RECOMMENDED_ACTION:
```
