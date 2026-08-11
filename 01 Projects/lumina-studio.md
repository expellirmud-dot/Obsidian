---
type: project
last_reviewed: 2026-08-11
evidence_class: verified
---

# lumina-studio

## โปรเจกต์นี้คืออะไร

โปรเจกต์เว็บ landing page ระดับพรีเมียมสำหรับช่างภาพ / creative studio — เริ่มต้นเป็น deploy-test landing page และอาจเติบโตเป็น photography portfolio / creative studio website

**Evidence:** `README.md` ("Premium photography landing page project"); `package.json` name=`lumina-studio` v0.1.0 (Next.js + React + TypeScript + Tailwind); `AI_HANDOFF.md` (deployed ไป Vercel); remote `expellirmud-dot/LUMINA-Studio` (verified)

## ปัญหาที่ต้องการแก้

- ต้องมีเว็บไซต์ตัวอย่างพรีเมียมสำหรับแสดงผลงานถ่ายภาพ
- ต้องทดสอบ deploy pipeline (Vercel) ก่อนจะขยายเป็น business website จริง
- แยกขอบเขต Phase 1 (landing page เดียว) ออกจาก feature อนาคต (backend/auth/booking/CMS)

## เป้าหมายหลัก

- Single-page premium photography landing page (Phase 1)
- Deploy ขึ้น production (Vercel) สำเร็จ
- Visual direction = Warm Premium / Quiet Luxury / Human Documentary ("Photography First")

## ขอบเขต

**In scope (verified, Phase 1):**
- Hero / What We Notice / Selected Stories / Moments Between / Behind The Lens / Kind Words / Experience / Final CTA
- Responsive layout, SEO metadata, performance optimization
- Config-driven content (brand, hero image, portfolio, services, navigation, contact, motion) ผ่าน `src/config/`
- Cinematic Hero slideshow + reactive light frame (config/motion controlled)

**Out of scope / locked (verified):**
- Backend, Database, Authentication, Booking, CMS, Admin dashboard, Payment, Client gallery (ห้ามใน Phase 1 ตาม `PROJECT_RULES.md`)
- Hero redesign ถูก FROZEN — ต้อง owner อนุมัติก่อนแก้
- Heavy glassmorphism / WebGL / Three.js / Canvas ใน production ถูกปฏิเสธโดย QA

## ตำแหน่งไฟล์จริง

- Local: `D:\lumina-studio`
- GitHub: `https://github.com/expellirmud-dot/LUMINA-Studio`
- Exact Git root (2026-08-11): `D:/lumina-studio`
- Branch: `main` · HEAD: `e98c9f627c50830c74cf76956abb15770690702d` (short `e98c9f6`) · 93 commits
- Git status: มี tracked dirty file `.serena/project.yml` (pre-existing, ไม่เกี่ยวข้องกับ onboarding, อ่าน-only บันทึกไว้)
- Production URL: `https://lumina-studio-iota-ten.vercel.app` (จาก `AI_HANDOFF.md`)

## Repository

- Remote: `https://github.com/expellirmud-dot/LUMINA-Studio.git`
- Default branch: `main`
- Stack (verified): Next.js 16.2.6, React 19.2.4, TypeScript, Tailwind CSS v4
- Authority files (verified จาก repo truth 2026-08-11): `AGENTS.md`, `PROJECT_RULES.md`, `AI_HANDOFF.md`, `README.md`, `docs/CONTEXT_INDEX.md`, `LUMINA_CONFIG_SYSTEM.md`, `GEMINI.md`, `IDEA.md`
- Task system: `.tasks/` (task packet / report / checkpoint) — active task ล่าสุด `TASK-030` COMPLETE
- Current work state: `AI_HANDOFF.md` → Overall Status **PASSED / READY FOR DEPLOY**; "Await owner's instruction for the next active work slice"

## สถานะปัจจุบัน

- Phase 1 Landing Page ✅ เสร็จ + deployed ไป Vercel production
- Active task: `TASK-030` (Micro Lock Polish) COMPLETE
- Status: PASSED / READY FOR DEPLOY — รอคำสั่งเจ้าของสำหรับงานถัดไป
- Evidence class: **verified** (repo truth 2026-08-11)

> หมายเหตุ: `AI_HANDOFF.md` ระบุ "Phase 2 limited Human Documentary redesign implemented through the existing config system" — ถือเป็นส่วนหนึ่งของ Phase 1 scope ที่อนุญาต (config-driven) ไม่ใช่ Phase 2 ใหม่ตามโครงสร้าง

## สิ่งที่ทำเสร็จแล้ว

- Bootstrap + Next.js + Tailwind initialized
- Deployment ไป Vercel production (`LUMINA-DEPLOYMENT-EXECUTION-001` DEPLOYED)
- Post-deploy verification ผ่าน (production URL ตรงกับ local candidate)
- LUMINA config system (`src/config/`) — แยก content/motion ออกจาก component
- Cinematic Hero slideshow + reactive light frame (config/motion controlled)
- Art Direction Lock (approved/rejected features) — `LUMINA-ART-DIRECTION-LOCK-001`
- Human Documentary redesign ผ่าน config (ไม่เติม backend/DB/dependency)
- Visual audit + browser MCP (Puppeteer) QA tooling
- 47 project skills ภายใต้ `skills/` (source of truth); mirror folders ใน `.gemini/`, `.opencode/`, `.agent/`
- Task scaffolding `.tasks/` (TASK-000..TASK-030+)

## งานที่กำลังทำ

- ไม่มี — `AI_HANDOFF.md` ระบุ Pending: None; Next Task: await owner instruction

## งานถัดไป

- รอเจ้าของสั่งงานถัดไป (ไม่มี active task ในรอบนี้)
- หากขยายนอก Phase 1 ต้องเพิ่มลง `ROADMAP.md` ตาม `PROJECT_RULES.md` scope warning

## สถาปัตยกรรม

สรุปสถาปัตยกรรม (ไม่สร้างแยกต่างหากตาม WO-026 §7):

- Next.js App Router (`app/page.tsx`) + `app/globals.css`
- Config-driven: ทุก content/visual token/motion อยู่ใน `src/config/` (ไม่ hardcode ใน component)
- Client components: Hero slideshow, reactive light frame (120fps viewport parallax, mobile + prefers-reduced-motion fallbacks)
- Agent workflow: `skills/` = source of truth; mirror adapters ใน `.gemini/skills`, `.opencode/skills`, `.agent/skills`
- Task packet system: `.tasks/<TASK-ID>/` (task.md + plan.md + report)
- Authority order (จาก `docs/CONTEXT_INDEX.md`): filesystem > Serena/CodeGraph; read-first = Task Packet → Meta-Rules → AI_HANDOFF

**Follow-up:** หากต้องการเอกสารสถาปัตยกรรมละเอียด ให้สร้าง `02 Architecture/ARCH-lumina-studio-<topic>.md` ใน WO ภายหลังเมื่อมี evidence พอ

## การตัดสินใจสำคัญ

- Phase 1 scope lock — ห้าม backend/auth/booking/CMS (PROJECT_RULES.md)
- Config system แยกออกจาก component — เปลี่ยน content/motion ไม่ต้องแตะ code (LUMINA-CONFIG-SYSTEM-001)
- Art Direction Lock — Photography First; Motion Supports Photography (LUMINA-ART-DIRECTION-LOCK-001)
- Hero FROZEN — ต้อง owner อนุมัติก่อน redesign
- Reject heavy optical overlays / glassmorphism / WebGL / Canvas ใน production
- Filesystem = source of truth เหนือ Serena/CodeGraph

## ปัญหาและความเสี่ยง

- Hero FROZEN → การปรับ hero ต้องรอ owner อนุมัติ (ข้อจำกัดโดยเจตนา)
- Scope creep: หากขอ feature นอก Phase 1 ต้องเข้า ROADMAP ไม่ทำทันที
- Pre-existing dirty file `.serena/project.yml` ใน source repo — ไม่เกี่ยวข้องกับ Vault onboarding (บันทึกเพื่อความโปร่งใส)
- Production depends on Vercel external service — สถานะ deploy อาจเปลี่ยนหากมีการ redeploy

## บทเรียน

- Config-driven content/motion → ปรับแต่ง brand ได้โดยไม่แตะ component
- Art Direction Lock + visual audit → รักษา direction ระหว่างหลาย task
- Task packet system (`.tasks/`) → แต่ละงานมี boundary ชัดเจน เช็คก่อนทำ
- Browser MCP (Puppeteer) สำหรับ visual QA → พิสูจน์ render จริงก่อน claim PASS

## Resume Context

- Repo: `D:\lumina-studio`, branch `main`, HEAD `e98c9f6` (2026-08-11)
- Status: PASSED / READY FOR DEPLOY; รอ owner instruction
- Onboarded into Vault ผ่าน WO-OBSIDIAN-026 (2026-08-11)
- ตรวจ `git status`, `AI_HANDOFF.md`, `PROJECT_RULES.md`, `.tasks/` ก่อน resume (repo-truth-first)

## วันที่ตรวจสอบล่าสุด

2026-08-11 (WO-OBSIDIAN-026: repository truth verified, HEAD e98c9f6)
