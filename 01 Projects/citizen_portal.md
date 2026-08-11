---
type: project
last_reviewed: 2026-08-11
evidence_class: verified
---

# citizen_portal

## โปรเจกต์นี้คืออะไร

ระบบบริหารจัดการคำร้องออนไลน์ (Citizen Request Management) สำหรับเทศบาลตำบลด่านทับตะโก — รูปแบบเป็น **research prototype** (ไม่ใช่ระบบ production เต็มรูปแบบในขณะนี้) ที่ให้ประชาชนยื่นคำร้อง/ติดตามสถานะ เจ้าหน้าที่จัดการคิว/อัปเดตสถานะ ผู้ดูแลดูแดชบอร์ดพื้นฐาน

**Evidence:** `PROJECT_RULES.md` (Goal + MVP scope); `repo_memory/citizen_portal_memory.md` ("research prototype first, production optional later"); `package.json` name=`citizen-app` v0.1.0; `README.md` (generic Next.js boilerplate — ไม่ใช่แหล่งอธิบายโปรเจกต์ที่มีบริบท); remote `expellirmud-dot/citizen-portal.git` (verified)

## ปัญหาที่ต้องการแก้

- เทศบาลต้องการรับคำร้องจากประชาชนแบบออนไลน์ แทนกระดาษ/หน้างาน
- ประชาชนต้องการติดตามสถานะคำร้องได้เอง
- เจ้าหน้าที่ต้องการคิวงานและประวัติสถานะที่ชัดเจน
- ผู้ดูแลต้องการสถิติพื้นฐาน

## เป้าหมายหลัก

- MVP: ประชาชนยื่นคำร้อง + แนบรูป + ได้เลขติดตาม + ดูสถานะ
- เจ้าหน้าที่: login → ดูคิว → อัปเดตสถานะ + โน้ตผล
- ผู้ดูแล: แดชบอร์ดสถิติพื้นฐาน
- Explicit non-goals: AI classification, chatbot, mobile, microservices, realtime socket, predictive analytics

## ขอบเขต

**In scope (verified, MVP prototype):**
- Next.js 16 App Router + TypeScript + Tailwind + shadcn/ui
- Prisma ORM (PostgreSQL adapter + better-sqlite3 adapter) — อัปเดตล่าสุดไป Supabase Postgres (TASK storage `eace8c3`)
- Auth.js (NextAuth v4) สำหรับ login บทบาท citizen/staff/admin
- Image uploads ย้ายไป Supabase storage (`f8ae9fb` ชุดก่อนหน้า: `a4cb027` feat(storage))
- Workflow: citizen submit → tracking number → staff update → status history
- Admin dashboard basic stats
- Docs: `docs/` (API_SPEC, BUILD_PLAN, DATA_MODEL, MVP_SCOPE, SYSTEM_DIAGRAMS, TEST_CASES, UI_SITEMAP, WORKFLOW, presentation assets)

**Out of scope / non-goals (verified, PROJECT_RULES.md):**
- AI image classification, chatbot, mobile app, microservices, realtime socket, predictive analytics
- Production enterprise municipal system (ปัจจุบันคือ research prototype)

## ตำแหน่งไฟล์จริง

- Local (resolved): `D:\citizen_portal`
- GitHub: `https://github.com/expellirmud-dot/citizen-portal.git`
- Exact Git root (2026-08-11): `D:/citizen_portal`
- Branch: `main` · HEAD: `f8ae9fb428641da6101cab3ff76b1e5d20e43203` (short `f8ae9fb`) · 37 commits
- Git status: clean (no dirty tracked files ณ 2026-08-11)
- Last commit: `2026-06-24 chore: ignore Vercel local config`

## Repository

- Remote: `https://github.com/expellirmud-dot/citizen-portal.git`
- Default branch: `main`
- Stack (verified): Next.js 16.2.6 + React 19.2.4 + TypeScript, Tailwind, shadcn/ui, Prisma 7.8 (PostgreSQL + better-sqlite3 adapters), Supabase (DB + storage), Auth.js/NextAuth 4, bcryptjs
- Authority files (verified จาก repo truth 2026-08-11): `PROJECT_RULES.md` (primary), `CLAUDE.md` (`@AGENTS.md`), `AGENTS.md` (nextjs-agent-rules stub), `README.md` (generic boilerplate), `docs/*` (API_SPEC, BUILD_PLAN, DATA_MODEL, MVP_SCOPE, SYSTEM_DIAGRAMS, TEST_CASES, UI_SITEMAP, WORKFLOW), `repo_memory/citizen_portal_memory.md`, `prisma/` schema
- Current work state (source): ไม่มี active work-order pointer ใน repo; git log ล่าสุดคือ cleanup/config (Vercel local config ignore) วันที่ 2026-06-24 — สะท้อนสถานะ prototype ที่พัก/เสร็จ MVP แล้ว ไม่มี task เปิดอยู่

> หมายเหตุ: ไม่มี `Work-Order/CURRENT_WORK_ORDER.md` หรือเทียบเท่าใน source → ไม่มี active WO ให้引用

## สถานะปัจจุบัน

- Source repo อยู่ในสถานะ research prototype ที่ MVP flows ทำงานได้ (ตาม `repo_memory`) และไม่มี active task เปิดอยู่
- Evidence class: **verified** (repo truth 2026-08-11)

> หมายเหตุ: ไม่มีการอ้างสถานะ "active task" — git log + ไม่มี WO pointer สะท้อน prototype ที่พักหลังจบ MVP

## สิ่งที่ทำเสร็จแล้ว

- โครงสร้าง Next.js + TypeScript + Tailwind + shadcn/ui (`PROJECT_RULES.md` architecture constraints)
- Prisma + PostgreSQL/Supabase config (`eace8c3` Configure Prisma for Supabase Postgres demo)
- Auth.js login สำหรับ citizen/staff/admin (`PROJECT_RULES.md` + `repo_memory` core flows)
- Citizen flow: ยื่นคำร้อง + แนบรูป + ได้เลขติดตาม + ติดตามสถานะ
- Staff flow: ดูคิว + อัปเดตสถานะ + โน้ตผล + ประวัติสถานะ
- Admin: แดชบอร์ดสถิติพื้นฐาน
- Image uploads ย้ายไป Supabase storage (`a4cb027`)
- เอกสารครบชุด: API spec, data model, workflow, test cases, UI sitemap, system diagrams, presentation
- Demonstration screenshots (demo-01..05) + presentation assets
- Vercel local config ignore (`f8ae9fb`)

## งานที่กำลังทำ

- ไม่มี — ไม่มี active task/WO ใน source; prototype อยู่สถานะพักหลังจบ MVP

## งานถัดไป

- รอเจ้าของสั่งงานถัดไป (production track หรือ feature เพิ่ม)
- หากขยาย: ดู `docs/MVP_SCOPE.md` / `BUILD_PLAN.md` สำหรับทิศทางถัดไป
- Explicit non-goals ห้ามขยายเข้าไปโดยไม่มี owner authorization (AI/chatbot/mobile/realtime ฯลฯ)

## สถาปัตยกรรม

สรุปสถาปัตยกรรม (ไม่สร้างแยกต่างหากตาม WO-028 §7):

- Next.js 16 App Router (App Router, `src/app`, `src/lib`)
- TypeScript + Tailwind + shadcn/ui
- Data: Prisma ORM → PostgreSQL (Supabase) + better-sqlite3 adapter (local demo)
- Auth: Auth.js (NextAuth v4) — roles: citizen / staff / admin
- Storage: Supabase storage สำหรับรูปคำร้อง (เปลี่ยนจาก local วันที่ `a4cb027`)
- มี `middleware.ts` (route guard), `prisma/` schema, `docs/` เป็น canonical documentation
- Engineering rules (PROJECT_RULES.md): no over-engineering, database-first, UI follows workflow

**Follow-up:** หากต้องการเอกสารสถาปัตยกรรมละเอียด ให้สร้าง `02 Architecture/ARCH-citizen-portal-<topic>.md` ใน WO ภายหลังเมื่อมี evidence พอ

## การตัดสินใจสำคัญ

- Research prototype first — ไม่ใช่ production enterprise ระบบ ณ ตอนนี้ (`repo_memory`)
- Explicit non-goals ที่ชัดเจน (AI/chatbot/mobile/realtime ฯลฯ) — ห้ามอนุมานขยาย
- Storage ย้ายไป Supabase (centralized) แทน local filesystem
- Auth roles แยก citizen/staff/admin ชัดเจน
- Next.js 16 มี breaking changes — `AGENTS.md` เตือนให้อ่าน `node_modules/next/dist/docs/` ก่อนเขียนโค้ด (relevant ถ้ามี future dev)

## ปัญหาและความเสี่ยง

- สถานะเป็น research prototype — หากจะเอาไป production จริงต้องมี governance/security เพิ่ม (ไม่อยู่ใน MVP)
- `AGENTS.md` เป็นเพียง nextjs-agent-rules stub — ไม่มี project convention ลึกในไฟล์นั้น (อาศัย `PROJECT_RULES.md` + `docs/`)
- `README.md` คือ Next.js boilerplate ทั่วไป — ไม่สะท้อนบริบทโปรเจกต์ (ใช้ `PROJECT_RULES.md` เป็น primary authority)
- ไม่มี active WO pointer ใน source → ไม่มี current-task authority ชัดเจน
- Lifecycle ปล่อย `unknown` (ห้าม infer)

## บทเรียน

- Primary authority สำหรับโปรเจกต์นี้คือ `PROJECT_RULES.md` + `docs/` + `repo_memory/` ไม่ใช่ `README.md` (boilerplate) หรือ `AGENTS.md` (stub)
- Research-prototype mindset → แยก clearly จาก production scope
- Explicit non-goals ป้องกัน scope creep (AI/chatbot/mobile/realtime)

## Resume Context

- Repo: `D:\citizen_portal`, branch `main`, HEAD `f8ae9fb` (2026-08-11, 37 commits, clean)
- Status: research prototype, MVP flows ทำงานได้, ไม่มี active task
- Onboarded into Vault ผ่าน WO-OBSIDIAN-028 (2026-08-11)
- ตรวจ `git status`, `docs/`, `PROJECT_RULES.md`, `repo_memory/` ก่อน resume (repo-truth-first)

## วันที่ตรวจสอบล่าสุด

2026-08-11 (WO-OBSIDIAN-028: repository truth verified, HEAD f8ae9fb)
