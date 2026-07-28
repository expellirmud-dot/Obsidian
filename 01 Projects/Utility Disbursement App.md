---
type: project
status: paused
priority: unassigned
project_path: D:\project_backups\utility-disbursement-app
repository:
  local: D:\project_backups\utility-disbursement-app
  canonical_root: D:\project_backups\utility-disbursement-app
  origin: https://github.com/expellirmud-dot/utility-disbursement-app.git
  branch: main
  head: 429cb91f5a4a6d5b64a14fac6e0136f59649e95d
  upstream: origin/main
  worktree_status: dirty
  dirty_details: dev.db modified
current_work_order: NONE
last_reviewed: 2026-07-29
---

# Utility Disbursement App

> คลังบริบทโปรเจกต์ — อ้างอิงจาก source repository แบบ read-only

## โปรเจกต์นี้คืออะไร

ระบบช่วยเจ้าหน้าที่เทศบาลจัดเตรียมเอกสารเบิกจ่ายค่าสาธารณูปโภค โดยอ่านบิล เลือก/แก้ไขข้อมูล คำนวณภาษีหัก ณ ที่จ่าย และเตรียมข้อมูลสำหรับ e-LAAS

## ปัญหาที่ต้องการแก้

เจ้าหน้าที่ต้องอ่านบิล จัดทำบันทึกข้อความ และเตรียมรายละเอียดเบิกจ่ายด้วยตนเอง ทำให้ช้าและเสี่ยงพลาด尤其是在ส่วนคำนวณภาษี งบประมาณ และความสมบูรณ์ของเอกสาร

## เป้าหมายหลัก

- เพิ่มประสิทธิภาพการเตรียมเอกสารเบิกจ่ายค่าสาธารณูปโภค
- คำนวณภาษีหัก ณ ที่จ่ายและยอดสุทธิได้ถูกต้องตาม business rule
- บังคับให้มีการตรวจสอบอย่างมีหลักฐานก่อนสร้างบันทึกข้อความหรือคัดลอกไป e-LAAS
- เตรียมข้อมูลสำหรับ e-LAAS แบบ manual-safe ที่ไม่ส่งอัตโนมัติ

## ขอบเขต

### In Scope

- รับอัปโหลดบิลและเตรียม OCR/mock extraction
- แก้ไข/ตรวจสอบข้อมูลบิลโดยผู้ใช้
- คำนวณภาษีหัก ณ ที่จ่ายและยอดสุทธิ
- ตรวจสอบ budget/fiscal year และ readiness gate
- สร้าง preview บันทึกข้อความและ dashboard สำหรับติดตาม
- เตรียมข้อมูล e-LAAS ในรูปแบบ copy-helper แบบ manual submit

### Out of Scope

- การส่ง e-LAAS อัตโนมัติ
- ระบบล็อกอิน/บทบาทซับซ้อน
- บริหารฐานข้อมูลหนัก หรือ production-scale cloud storage
- นำ governance/runtime ระบบเดิมกลับมาใช้

## ตำแหน่งไฟล์จริง

`D:\project_backups\utility-disbursement-app`

## Repository

VERIFIED_REPOSITORY_FACT:
- origin: https://github.com/expellirmud-dot/utility-disbursement-app.git
- canonical root: D:\project_backups\utility-disbursement-app
- branch/HEAD/upstream/status ตรวจแล้วด้วย command output

## สถานะปัจจุบัน

Status: paused — Owner ยืนยันว่ายังไม่พัฒนาต่อชั่วคราวและย้ายไปเก็บใน backup path
OWNER_CONFIRMED_FACT:
- paused หมายถึงหยุดพัฒนาชั่วคราว ไม่ใช่ abandoned / completed / production-ready
- ยังไม่มี proof ที่ source repo สั่งให้หยุดอย่างเป็นทางการ โดยสแตนซ์ปัจจุบันมีข้อมูลงานค้างและสถานะ task status อ้างอิงไว้แล้ว

Repository facts:
- branch: main
- HEAD: 429cb91f5a4a6d5b64a14fac6e0136f59649e95d
- upstream: origin/main
- worktree: dev.db มีการแก้ไขเป็น tracked modification
- current repository task pointer: NONE

## สิ่งที่ทำเสร็จแล้ว

VERIFIED_REPOSITORY_FACT / SUPPORTED_INFERENCE จาก authority และ task status:
- TASK 013 Non-PDF Readiness Foundation:
  - 013-A memo hardening
  - 013-B fiscal year/budget validation
  - 013-C readiness gate
  - 013-E evidence persistence
  - 013-F tax consistency
  - 013-QA final validation
- TASK 014 Business Dashboard:
  - 014-A dashboard scope foundation
  - 014-B summary cards
  - 014-C draft status list
  - 014-D blockers/missing fields view
  - 014-E evidence readiness view
  - 014-F dashboard polish
  - 014-QA final validation
- TASK 015 PDF/Print Output Scope:
  - 015-A readiness/output contract
  - 015-B print layout hardening
  - 015-C readiness-gated print controls
  - 015-D PDF generation decision point
  - 015-E evidence/officer review copy
  - 015-QA final validation
- TASK 016 e-LAAS Copy Helper Refinement:
  - 016-A field contract
  - 016-B copy helper UI
  - 016-C readiness-gated copy controls
  - 016-D copy format and audit notes
  - 016-E manual safety guardrails
  - 016-QA final validation
- TASK 017 File Upload/Storage Foundation:
  - 017-A minimal scope
  - 017-B storage decision
  - 017-C local storage adapter
  - 017-D draft file reference link
  - 017-E storage safety guardrails
  - 017-QA final validation
- TASK 018 Pilot/QA:
  - 018-A/B manual pilot
  - 018-C automated smoke script
  - 018-D pilot evidence
  - 018-E pilot gap closure
  - 018-QA final
- Validation ที่อ้างอิงใน repo:
  - `npm run lint`: pass with baseline isolated-tool warnings
  - `npm run build`: pass
  - `node scripts/pilot-smoke-check.mjs`: pass

## งานที่กำลังทำ

TASK 013 status: IN_PROGRESS
TASK 017 status: IN_PROGRESS
หมายเหตุ: เป็นสถานะของ task packet ภายใน repo ที่ระบุ subtask คุ้มครองรายการใหญ่แล้ว; ไม่ใช่ runtime กำลังทำงานจริงบนระบบที่ pause อยู่

## งานถัดไป

SUPPORTED_INFERENCE จาก docs/legacy-memory:
- TASK 019 extraction pipeline modernization/next-stage work
- TASK 015-note: true PDF generation ยังต้องได้รับการอนุมัติ dependency/architecture อย่างชัดเจนก่อนทำต่อ
- จริงจัง wiederaufnahme: ตรวจ branch/HEAD/งานค้าง + readiness ว่าสามารถกลับพัฒนาต่อได้ใน path ปัจจุบันหรือไม่

## สถาปัตยกรรม

SUPPORTED_INFERENCE:
- Framework: Next.js 16 App Router + React + TypeScript + Tailwind
- UI boundaries: AppShell, Dashboard, Disbursement Workbench, Bill Intake, Memo Preview, e-LAAS Prepare
- API boundaries: drafts, budget master, dashboard summary, e-LAAS dry-run/manual-reference/write-prototype, print package, uploads, ledger, ai-verifier
- Data/persistence boundaries:
  - Prisma schema ตรวจแล้ว: BudgetMaster, UploadedBill, DisbursementDraft, AuditLedger
  - sqlite datasource
  - local storage adapter สำหรับไฟล์อัปโหลด
- Business rule boundaries:
  - ค่าไฟฟ้าไม่หักภาษี ณ ที่จ่าย
  - อื่น ๆ หัก 1%
  - ต้องผ่าน human review ก่อน memo/output
  - Thai fiscal year เป็น Oct-Sep B.E.
- Explicit non-goals:
  - ไม่ส่ง e-LAAS อัตโนมัติ
  - ไม่เก็บ password/credential
  - ไม่นำ ai_runtime/governance เดิมกลับมา

## การตัดสินใจสำคัญ

- ใช้ Next.js App Router + Tailwind แทนระบบ governance เก่า
- เก็บเฉพาะ metadata ของ uploaded bill; binary ไม่อยู่ใน schema
- SQLite เป็น datasource ปัจจุบัน
- PDF/print ใช้ browser print/save as PDF เป็น default จนกว่าจะมีอนุมัติ true PDF generation
- e-LAAS เป็น copy-helper/manual-safety ONLY
- TASK 014-A ทำเป็น planning/scope foundation และใช้ read-only dashboard pattern

## ปัญหาและความเสี่ยง

- dev.db เป็น tracked modification ปัจจุบัน สาเหตุและผลกระทบยังไม่ตรวจลึก
- ยังไม่มี production persistence/ledger sync ที่ตรวจครบ
- ข้อมูล budget ใกล้เคียง static-seed
- หากกลับพัฒนาต่อ ควรเพิ่ม validation รายละเอียดเกี่ยวกับ branch policy/upstream และ working tree ก่อน commit ใด
- Roadmap เก่าอาจไม่ตรงกับ task packet ปัจจุบัน; ใช้ task packet เป็น source of truth มากกว่าบันทึกย้อนหลัง

## บทเรียนที่ได้

- บันทึกโปรเจกต์เป็น Vault ควรแยก:
  - verified repo fact
  - owner-confirmed fact
  - supported inference
  - needs-verification
- โฟลเดอร์ backup ไม่ใช่ production path; กลับมาทำงานต่อควรย้ายกลับ working path ปกติและเช็ค repo policy ใหม่
- task packet (.tasks/) เป็น authoritative ที่ดีกว่า legacy product reports

## เอกสารที่เกี่ยวข้อง

- [[Project Dashboard]]
- [[Project Index]]
- [[ARCH-Utility-Disbursement-App-Overview]]
- source repo docs:
  - `AGENTS.md`
  - `CLAUDE.md`
  - `PROJECT_RULES.md`
  - `README.md`
  - `docs/NEW_PROJECT_BRIEF.md`
  - `docs/legacy-memory/ROADMAP_CURRENT.md`
  - `.tasks/TASK-*/status.md`

## Resume Context

สถานะล่าสุด: paused
เหตุผล/หลักฐาน: owner-confirmed 2026-07-28; repo ย้ายมาเก็บที่ backup path
Repo truth ล่าสุด: branch main, HEAD 429cb91, upstream origin/main, worktree dev.db มี tracked modification
งานที่กำลังทำตาม task packet: TASK 013 IN_PROGRESS, TASK 017 IN_PROGRESS
สิ่งที่ทำเสร็จแล้ว: TASK 013/014/015/016/017/018 มี subtask และ QA ที่อ้างอิงแล้วเสร็จ
สิ่งที่ห้ามทำซ้ำ: ระงับ e-LAAS auto-submit, ไม่นำ old ai_runtime กลับมา, ไม่เพิ่ม auth/backend หนักก่อนที่มีหลักฐานอนุมัติ
ปัญหาที่ยังค้าง: dev.db dirty state ยังไม่ทราบสาเหตุ, true PDF generation ยังไม่ได้รับการอนุมัติ, budget sync จริงยังไม่ตรวจ
ขั้นตอนถัดไป:
1. ตรวจสาเหตุ tracked modification ของ dev.db ก่อนกลับพัฒนา
2. ยืนยันว่า path/policy การทำงานต่อเป็น production path หรือ backup path
3. หากกลับพัฒนา เริ่มด้วย task packet ปัจจุบันและตรวจ branch policy ใหม่
ไฟล์ที่ต้องอ่านก่อน: AGENTS.md, PROJECT_RULES.md, docs/NEW_PROJECT_BRIEF.md, active `.tasks/TASK-XXX/status.md`
วันที่ตรวจสอบล่าสุด: 2026-07-29

## Verification Record

- Repository checked: full read-only discovery; source repo unmodified
- Git HEAD: 429cb91f5a4a6d5b64a14fac6e0136f59649e95d
- Current Work Order checked: NONE in repo
- Verified by: AI discovery + owner statement 2026-07-28 + repo evidence 2026-07-29
- Verification date: 2026-07-29
- Evidence classification: VERIFIED_REPOSITORY_FACT / OWNER_CONFIRMED_FACT / SUPPORTED_INFERENCE / NEEDS_VERIFICATION
