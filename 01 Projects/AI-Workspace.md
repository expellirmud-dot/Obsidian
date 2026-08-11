---
type: project
last_reviewed: 2026-08-11
evidence_class: verified
---

# AI-Workspace

## โปรเจกต์นี้คืออะไร

**Workspace ระดับระบบ** (central workspace) สำหรับประสานงาน AI-assisted ข้ามหลายแอป หลายโมเดล หลายโปรเจกต์ — เป็น "home" ระดับบนสุดของกระบวนการ AI ops ไม่ใช่ product app ตัวหนึ่ง

**Evidence:** `README.md` ("Central workspace for coordinating AI-assisted work across multiple applications, models, and product projects"); `AGENTS.md` ("primary workspace ... Do not treat a module directory or product repository as the system root"); `workspace-modules.yaml` (`id: expellirmud-ai-workspace`, `mode: manual-safe`); remote `expellirmud-dot/Expellirmud-AI-Workspace.git`

> ⚠️ **Path correction:** คำสั่งสร้าง draft ระบุ `D:\AI-Workspace` (ไม่มีจริง) ที่อยู่จริงคือ `D:\ai-tools\AI-Workspace` (resolved fresh 2026-08-11)

## ปัญหาที่ต้องการแก้

- ต้องการจุดศูนย์กลางสำหรับจัดการ context, task cards, dispatch instructions, และ reports ข้ามหลายโปรเจกต์โดยไม่ยุ่งกับ product code โดยตรง
- ต้องการ separation of concerns ชัดเจนระหว่าง workspace infra กับ product repositories
- ต้องการ safety model แบบ manual-safe (ห้าม auto-send / auto-invoke / auto-CI)

## เป้าหมายหลัก

- เป็น primary Codex/AI workspace root
- แยก registry module (`ai-ops-registry/`) ออกจาก product code
- กระบวนการ: Owner → Controller → AI-Workspace → Registry Module → Active Project Context → Task Card → Manual Dispatch → Worker → Verifier → Final Gate → Owner Report
- V1 manual-safe: เตรียม context/dispatch เท่านั้น ไม่ auto-execute

## ขอบเขต

**In scope (verified, V1):**
- `workspace-modules.yaml` — workspace + module declarations (schema_version 1.0)
- `ai-ops-registry/` — registry contracts, project profiles, templates, task records, reports, benchmarks, channel-contracts, openapi
- `docs/` (`CONNECTOR_GATEWAY_RUNBOOK.md`)
- `skills/`, `scripts/`, `reports/`, `cache/`, `backups/`
- Product repositories ถูกประกาศเป็น `external_projects` (เช่น `lumina-studio`) — อ่าน/แก้ได้เฉพาะเมื่อมี approved task card

**Out of scope / external (verified):**
- Product repositories เอง (`lumina-studio`, `thai_stt_app`, ฯลฯ) — ไม่อยู่ใน workspace root
- Auto-dispatch / auto-CI / MCP Tasks อัตโนมัติ — ห้ามใน V1 (Deny by default)

## ตำแหน่งไฟล์จริง

- Local (resolved): `D:\ai-tools\AI-Workspace`
- GitHub: `https://github.com/expellirmud-dot/Expellirmud-AI-Workspace.git`
- Exact Git root (2026-08-11): `D:/ai-tools/AI-Workspace`
- Branch: `main` · HEAD: `69340677fb61af3e7d2b7f840363632f3211f5fd` (short `6934067`) · 47 commits
- Git status: pre-existing dirty tracked files (`.serena/project.yml`, `src/App.jsx`) — ไม่เกี่ยวข้องกับ Vault onboarding, อ่าน-only บันทึกไว้
- Last commit: `2026-06-30 feat(workspace): update Gemini CLI dispatch command generation`

## Repository

- Remote: `https://github.com/expellirmud-dot/Expellirmud-AI-Workspace.git`
- Default branch: `main`
- Stack (verified): Node/JS workspace (`package.json`, `vite.config.js`, `src/App.jsx`), YAML module config, `.gemini` / `.antigravitycli` / `.codex` / `.opencode` configs; ai-ops-registry เป็น data/contract layer
- Authority files (verified จาก repo truth 2026-08-11): `README.md`, `AGENTS.md`, `WORKSPACE.md` (Workspace Contract v1), `workspace-modules.yaml`, `CLI_MODEL_CATALOG.md`, `ai-ops-registry/AGENTS.md`, `ai-ops-registry/registry/REGISTRY_CONTRACT.md`, `ai-ops-registry/docs/READ_FIRST_POLICY.md`, `docs/CONNECTOR_GATEWAY_RUNBOOK.md`
- Current work state (source): ไม่มี active work-order pointer ใน repo; git log ล่าสุด = infra/maintenance tasks (task pack composer, registry YAML validation, connector token docs, dashboard workflow) → สถานะ stable / maintenance, ไม่มี active task เปิด

> หมายเหตุ: ไม่มี `Work-Order/CURRENT_WORK_ORDER.md` หรือเทียบเท่า → ไม่มี active WO ให้引用

## สถานะปัจจุบัน

- Source repo อยู่ในสถานะ stable / maintenance (V1 manual-safe ทำงานได้); ไม่มี active work-order tracker
- Evidence class: **verified** (repo truth 2026-08-11)

> หมายเหตุ: ไม่มีการอ้างสถานะ "active task" — สถานะสืบจาก git log + ไม่มี WO pointer

## สิ่งที่ทำเสร็จแล้ว

- Workspace Contract v1 (`WORKSPACE.md`) — architecture + separation of concerns
- `workspace-modules.yaml` — workspace + ai-ops-registry module + external_projects
- `ai-ops-registry/` — registry contracts, project profiles, templates, task records, reports, benchmarks, channel-contracts, openapi
- READ-FIRST policy enforcement (`ai-ops-registry/docs/READ_FIRST_POLICY.md`)
- V1 Safety Rules: manual dispatch only, deny-by-default, registry/product separation
- Connector gateway runbook (`docs/CONNECTOR_GATEWAY_RUNBOOK.md`) + token setup docs
- CLI model catalog + Gemini CLI dispatch command generation
- Dashboard workflow + worker catalog
- Registry YAML shape validation + task pack composer

## งานที่กำลังทำ

- ไม่มี — source ไม่มี active WO; git log สะท้อน maintenance/infra

## งานถัดไป

- รอเจ้าของสั่งงานถัดไป
- หากขยาย: ดู `ai-ops-registry/registry/REGISTRY_CONTRACT.md`, `workspace-modules.yaml`, `docs/CONNECTOR_GATEWAY_RUNBOOK.md`

## สถาปัตยกรรม

สรุปสถาปัตยกรรม (ไม่สร้างแยกต่างหากตาม WO-030 §7):

- **Workspace Root** (`D:\ai-tools\AI-Workspace`): module discovery + system-level instructions
- **Registry Module** (`ai-ops-registry/`): registry contracts, profiles, templates, task records, reports
- **Flow**: Owner → Controller → AI-Workspace → Registry Module → Active Project Context → Task Card → Manual Dispatch → Worker → Verifier → Final Gate → Owner Report
- **External projects**: ประกาศใน `workspace-modules.yaml` (`external_projects`) — เช่น `lumina-studio`; อ่าน/แก้ได้เฉพาะเมื่อ task card อนุมัติ
- **V1 mode**: `manual-safe` — เตรียม context/dispatch เท่านั้น ห้าม auto-send / auto-invoke subagents / auto-CI
- Configs: `.gemini`, `.antigravitycli`, `.codex`, `.opencode` (multi-agent CLI integration)

**Follow-up:** หากต้องการเอกสารสถาปัตยกรรมละเอียด ให้สร้าง `02 Architecture/ARCH-ai-workspace-<topic>.md` ใน WO ภายหลังเมื่อมี evidence พอ

## การตัดสินใจสำคัญ

- **Repository ≠ Project / Tooling ≠ Project**: AI-Workspace เป็น orchestration workspace ไม่ใช่ product app เดี่ยว — บันทึกเพื่อป้องกันเข้าใจผิดเวลา onboard (Vault governance เดียวกัน)
- Manual dispatch only, deny-by-default เมื่อขาด scope
- Registry infra แยกจาก product code ชัดเจน
- ทุก dispatched task ต้องแนบ active-project context snapshot
- External projects ไม่อยู่ใน workspace root — อ่าน/แก้ได้เฉพาะเมื่อ approved task card

## ปัญหาและความเสี่ยง

- Pre-existing dirty tracked files ใน source (`.serena/project.yml`, `src/App.jsx`) — บันทึกเพื่อความโปร่งใส (อ่าน-only)
- ไม่มี active work-order pointer → ไม่มี current-task authority ชัดเจน
- เป็น workspace ระดับระบบ → หากเจ้าของขยายไป auto-dispatch ต้องระวัง safety boundary (V1 ห้าม)
- Path ในคำสั่ง (`D:\AI-Workspace`) ล้าสมัย — ที่จริง `D:\ai-tools\AI-Workspace` (บันทึกใน Registry + Overview แล้ว)
- Lifecycle ปล่อย `unknown` (ไม่ infer)

## บทเรียน

- AI-Workspace เป็น "system-level home" สำหรับ multi-project AI ops — แยกจาก product repos อย่างเด็ดขาด
- READ-FIRST policy + manual-safe mode → ป้องกัน auto-action ที่อันตราย
- `workspace-modules.yaml` เป็น single source of truth สำหรับ module + external project mapping

## Resume Context

- Repo: `D:\ai-tools\AI-Workspace`, branch `main`, HEAD `6934067` (2026-08-11, 47 commits, pre-existing dirty `.serena/project.yml` + `src/App.jsx`)
- Status: stable / maintenance (V1 manual-safe), ไม่มี active task
- Onboarded into Vault ผ่าน WO-OBSIDIAN-030 (2026-08-11) — โปรเจกต์สุดท้ายใน eligible `project + verified` gate
- ตรวจ `git status`, `WORKSPACE.md`, `workspace-modules.yaml`, `ai-ops-registry/` ก่อน resume (repo-truth-first)

## วันที่ตรวจสอบล่าสุด

2026-08-11 (WO-OBSIDIAN-030: repository truth verified, HEAD 6934067)
