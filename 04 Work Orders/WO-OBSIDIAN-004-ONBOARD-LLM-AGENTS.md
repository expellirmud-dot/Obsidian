# WORK ORDER — ONBOARD LLM-AGENTS

Work Order ID: WO-OBSIDIAN-004  
Title: Onboard llm-agents into Project Knowledge Vault  
Status: CLOSED  
Task Classification: EXTERNAL_PROJECT_DISCOVERY_AND_VAULT_UPDATE  
Risk Level: MEDIUM  
Execution Mode: One Repository, One Bounded Seam

Owner: Toto  
Vault Root: `D:\Obsidian\Project-Knowledge-Vault`  
Source Repository: `D:\llm-agents`

Depends On: WO-OBSIDIAN-003 CLOSED  
Pull Authorization: YES — fast-forward only  
Commit Authorization: YES — one Vault commit after validation  
Push Authorization: NO

---

## 1. Objective

ใช้ `project-read-first` และ `project-context-discovery` ตรวจ Repository truth ของ `llm-agents` แบบ read-only แล้วอัปเดต Vault ให้สามารถกลับมาทำงานต่อได้โดยไม่ต้องอ่านโปรเจกต์ใหม่ทั้งหมด

ต้องยืนยันจุดประสงค์ ขอบเขต authority, branch/HEAD/status, Current Work Order, architecture ระดับภาพรวม, current state, risks, required reads และ next action จากหลักฐานจริง

---

## 2. Required Read Order

### Vault

1. `AGENTS.md`
2. `.agents/skills/project-read-first/SKILL.md`
3. `.agents/skills/project-context-discovery/SKILL.md`
4. `04 Work Orders/CURRENT_WORK_ORDER.md`
5. Work Order ฉบับนี้
6. `01 Projects/llm-agents.md`
7. `01 Projects/Project Index.md`
8. `00 Dashboard/Project Dashboard.md`

### Source Repository

1. Resolve exact Git root จาก `D:\llm-agents`
2. อ่าน root authority files ที่ค้นพบ
3. อ่าน Current Work Order / Current Task pointer ที่เป็น authority
4. อ่าน README หรือ documentation index
5. อ่าน status, roadmap, architecture และ validation แบบ targeted
6. Inspect source symbols เฉพาะเมื่อเอกสารไม่เพียงพอ

ห้าม hard-code ชื่อไฟล์ authority นอกเหนือจากการค้นหา candidate files

---

## 3. Source Repository Boundary

Source Repository เป็น read-only:

- ห้ามแก้ไฟล์
- ห้าม stage/commit/push
- ห้าม checkout/reset/clean/stash
- ห้ามติดตั้ง dependency
- ห้ามรันคำสั่ง destructive หรือ runtime ที่เปลี่ยน state
- ห้ามเปิด Secret/Credential

หากต้อง inspect source code ให้ Serena และ CodeGraph ตรง exact Git root ก่อน

---

## 4. Required Evidence

รวบรวมและบันทึก:

```text
REPOSITORY_ROOT
REMOTE
BRANCH
HEAD
UPSTREAM
GIT_STATUS
AUTHORITY_FILES
CURRENT_WORK_ORDER
WORK_ORDER_STATUS
DOCUMENTATION_INDEX
PROJECT_PURPOSE
PROBLEM_SOLVED
IN_SCOPE
OUT_OF_SCOPE
ARCHITECTURE_SUMMARY
CURRENT_STATE
COMPLETED_WORK
OPEN_WORK
KNOWN_RISKS
DO_NOT_REPEAT
REQUIRED_READS
NEXT_RECOMMENDED_ACTION
```

ทุกข้อสรุปต้องแยกเป็น:

- `VERIFIED_REPOSITORY_FACT`
- `OWNER_CONFIRMED_FACT`
- `SUPPORTED_INFERENCE`
- `NEEDS_VERIFICATION`

---

## 5. Vault Updates

แก้หรือสร้างเฉพาะ:

```text
01 Projects/llm-agents.md
01 Projects/Project Index.md
00 Dashboard/Project Dashboard.md
02 Architecture/ARCH-llm-agents-Overview.md
02 Architecture/Architecture Index.md
04 Work Orders/CURRENT_WORK_ORDER.md
04 Work Orders/WO-OBSIDIAN-004-ONBOARD-LLM-AGENTS.md
04 Work Orders/Work Order Index.md
```

หน้า Project ต้องอัปเดต:

- frontmatter status/path/repository/current_work_order/last_reviewed
- project purpose และ problem solved
- verified scope
- repository truth
- current state
- completed/open work
- architecture summary พร้อมลิงก์ `[[ARCH-llm-agents-Overview]]`
- risks และ do-not-repeat
- Resume Context
- Verification Record พร้อม branch/HEAD/date

ห้ามลบข้อมูลเดิมที่ยังมีประโยชน์ ให้แก้ contradiction และรักษาประวัติที่จำเป็น

---

## 6. Architecture Note

สร้าง `02 Architecture/ARCH-llm-agents-Overview.md` เป็น summary ไม่ใช่สำเนา source code โดยมี:

- System purpose
- Major planes/components
- Authority and control boundaries
- Main execution flow
- Persistence/state boundaries
- Safety/validation boundaries
- Known limitations
- Evidence sources
- Last verified HEAD/date
- ลิงก์กลับ `[[llm-agents]]`

ข้อที่ยังยืนยันไม่ได้ต้องระบุ `needs-verification`

---

## 7. Stop Conditions

หยุดและรายงานเมื่อ:

- Path ไม่มีหรือไม่ใช่ Git repository
- Vault path กับ Git root ขัดแย้งกัน
- Authority documents ขัดแย้งจนสรุปไม่ได้
- Current Work Order ไม่ชัดเจน
- Source worktree มี state ที่ทำให้ current status สรุปไม่ได้อย่างปลอดภัย
- ต้องแก้ Source Repository
- ต้องใช้ Owner decision, Secret หรือ Credential
- Serena/CodeGraph mismatch เมื่อจำเป็นต้อง inspect source

---

## 8. Validation

ยืนยัน:

```text
Source repository modified: 0
Vault files outside allowed scope: 0
Project page required sections: complete
Repository root/branch/HEAD recorded: yes
Current Work Order recorded: yes or explicitly NONE
Architecture evidence citations/paths: present
Verified/inference/unknown separation: present
Internal links unresolved: 0 except marked placeholders
Duplicate frontmatter keys: 0
Secrets added: 0
Push performed: 0
```

รัน `git diff --check` ใน Vault และตรวจ diff ทั้งหมดก่อน commit

---

## 9. Definition of Done

1. Source Repository ถูกตรวจแบบ read-only
2. หน้า `llm-agents` ไม่เหลือข้อมูลเดิมที่ขัดกับหลักฐาน
3. Resume Context พร้อมใช้เริ่มแชทใหม่
4. Architecture overview เชื่อมกับ Project Page และ Index
5. Dashboard/Project Index สอดคล้องกัน
6. Verification Record มี HEAD และวันที่
7. `CURRENT_WORK_ORDER.md` เปลี่ยนเป็น `CLOSED`
8. Validation ผ่านทั้งหมด
9. Commit หนึ่งครั้ง
10. ไม่มี Push

Commit message:

```text
docs: onboard llm-agents project context
```

---

## 10. Final Report

```text
WORK_ORDER: WO-OBSIDIAN-004
RESULT: COMPLETED | PARTIAL | BLOCKED

SOURCE_REPOSITORY_ROOT:
SOURCE_BRANCH:
SOURCE_HEAD:
SOURCE_GIT_STATUS:
SOURCE_FILES_MODIFIED:

VAULT_HEAD_BEFORE:
VAULT_HEAD_AFTER:
VAULT_COMMIT:
VAULT_FILES_CREATED:
VAULT_FILES_UPDATED:
FILES_CHANGED_OUTSIDE_SCOPE:

AUTHORITY_FILES_READ:
CURRENT_WORK_ORDER:
DISCOVERY_DECISION:
VERIFICATION_STATUS:
UNVERIFIED_ITEMS:

SECRETS_ADDED:
PUSH_PERFORMED:
REMAINING_RISKS:
NEXT_RECOMMENDED_ACTION:
```
