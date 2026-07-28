---
type: architecture
project: Utility Disbursement App
last_reviewed: 2026-07-29
---

# Architecture Overview: Utility Disbursement App

> สรุปจาก repository `D:\project_backups\utility-disbursement-app` HEAD `429cb91`

## ภาพรวมสถาปัตยกรรม

Utility Disbursement App เป็น standalone Thai municipal utility disbursement app บน Next.js App Router สำหรับเตรียมเอกสารเบิกจ่ายค่าสาธารณูปโภค โดยแบ่งเป็น intake/OCR, review, readiness validation, memo preview, dashboard, และ e-LAAS manual copy helper

## Execution/Deployment Boundary

- Next.js 16 App Router บน local/dev environment
- Prisma + SQLite เป็น current datasource
- ไม่มี production deployment architecture ที่ตรวจแล้วใน repo
- ไม่มี confirmed cloud storage/backend architecture; local storage adapter เป็น V1 implementation

## App / API Boundary

- `src/app/page.tsx` เป็น dashboard/operations console
- `src/app/disbursements/page.tsx` เป็น workbench
- `src/app/print/page.tsx` เป็น print/output path
- API routes ครอบคลุม drafts, budget-master, dashboard summary, e-LAAS, print-package, uploads, ledger, ai-verifier

## UI / Service Boundary

- Components แยกเป็น intake, review, validation, dashboard, e-LAAS preview/print
- Readiness และ tax rules เป็น shared lib boundaries
- Human review เป็น enforced boundary ก่อน memo/output

## Data / Model Boundary

VERIFIED_REPOSITORY_FACT จาก `prisma/schema.prisma`:
- `BudgetMaster`: fiscal year, expense type, budget code/name, amounts
- `UploadedBill`: bill metadata, extraction status, storage linkage, fiscal year
- `DisbursementDraft`: memo fields, readiness JSON, status, link to uploaded bill
- `AuditLedger`: event/operator/amount/metadata/hash evidence

SUPPORTED_INFERENCE:
- readiness, tax, fiscal-year, memo, print, e-LAAS และ storage adapter เป็น service boundaries สำคัญ แต่ไม่ได้ include schema/prisma path ทั้งหมดในโฮสต์นี้

## Key Decisions

- Electricity exempt from withholding tax; other utilities apply 1%
- Human review required before document generation
- Browser print/Save as PDF เป็น default PDF path จนกว่าจะมีอนุมัติ true PDF generation
- e-LAAS เป็น manual-safety copy helper ONLY
- SQLite เป็น datasource ปัจจุบัน
- budget/fiscal-year logic ใช้ Thai municipal fiscal year

## External Boundary

- e-LAAS ยังไม่ integrate กับ外部 submission ระบบจริงอย่างเป็นทางการ
- ไม่มี confirmed external ledger sync/budget API ที่ตรวจแล้วใน repo

## Evidence Sources

- `D:\project_backups\utility-disbursement-app\AGENTS.md`
- `D:\project_backups\utility-disbursement-app\PROJECT_RULES.md`
- `D:\project_backups\utility-disbursement-app\README.md`
- `D:\project_backups\utility-disbursement-app\package.json`
- `D:\project_backups\utility-disbursement-app\prisma\schema.prisma`
- `D:\project_backups\utility-disbursement-app\.tasks\TASK-014\status.md`
- `D:\project_backups\utility-disbursement-app\.tasks\TASK-015\status.md`
- `D:\project_backups\utility-disbursement-app\.tasks\TASK-016\status.md`
- `D:\project_backups\utility-disbursement-app\.tasks\TASK-017\status.md`
- `D:\project_backups\utility-disbursement-app\.tasks\TASK-018\status.md`
- `D:\project_backups\utility-disbursement-app\src\app\page.tsx`
- `D:\project_backups\utility-disbursement-app\src\app\disbursements\page.tsx`
- `D:\project_backups\utility-disbursement-app\src\app\layout.tsx`
- `D:\project_backups\utility-disbursement-app\src\components\AppShell.tsx`
- `D:\project_backups\utility-disbursement-app\src\lib\readinessValidator.ts`
- `D:\project_backups\utility-disbursement-app\src\lib\taxRules.ts`

## Last Verified

- **HEAD:** `429cb91f5a4a6d5b64a14fac6e0136f59649e95d`
- **Date:** 2026-07-29
- **By:** WO-OBSIDIAN-008
- **Evidence Classification:** VERIFIED_REPOSITORY_FACT / SUPPORTED_INFERENCE / NEEDS_VERIFICATION

กลับไป [[Utility Disbursement App]]
