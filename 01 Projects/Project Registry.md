---
type: registry
last_reviewed: 2026-08-11
---

# Project Registry

> Inventory กลางของโปรเจกต์ที่ Vault รู้จัก (canonical inventory)
> สร้างโดย WO-OBSIDIAN-023 (2026-08-11); triage ต่อ 24 discovered โดย WO-OBSIDIAN-024 (2026-08-11)
> Dashboard และ Project Index อ้างอิง Registry นี้เป็นแหล่งรายการหลัก
> ห้ามถือว่ารายชื่อ Project Overview 5 รายการคือ inventory ทั้งหมดโดยปริยาย

## มุมมองสรุป (Summary)

| Import State | Count |
| ------------ | ----- |
| imported | 6 |
| discovered-not-imported | 23 |
| unknown | 0 |
| **รวม repos ที่พบ** | **29** |

| Lifecycle State | Count |
| --------------- | ----- |
| active | 3 |
| paused | 1 |
| archived | 0 |
| unknown | 25 |

| Verification State | Count |
| ------------------ | ----- |
| verified | 5 (imported) + 22 (discovered) = 27 |
| owner-confirmed | 1 (imported) |
| needs-verification | 3 (discovered: Automation, JAVIS_Nexus, office_council_keeper) |

## Triage Summary (WO-OBSIDIAN-024, 2026-08-11, read-only)

24 discovered repos ถูก triage ตาม taxonomy ใน WO-024 §5:

| Triage Class | Count | Evidence |
| ------------ | ----- | -------- |
| project | 6 | verified (owner GitHub repos, มี commit + remote เป็น expellirmud-dot/*) |
| tooling-infrastructure | 6 | verified (framework/mirror/skill kit) |
| sandbox-experiment | 6 | verified (fork ของ `D:\llm-agents`, remote = `D:/llm-agents`) |
| backup-archive-candidate | 2 | verified (อยู่ใต้ `project_backups/`) |
| duplicate-superseded-candidate | 1 | verified (อยู่ใต้ `project_backups/`, remote ซ้ำ `utility_automation_v2`) |
| unknown | 3 | needs-verification (0 commits on all branches, ไม่มี remote/README) |
| **รวม** | **24** | reconcile = 24, missing = 0 |

**Post-Triage Onboarding Gate (WO-024 §13):**
- Automatically eligible (onboard ได้พิจารณา): `project` + `verified` = 5 repos (เหลือหลังจาก onboard `thai_stt_app`)
  - `AI-Workspace`, `lightroom-ai-exposure`, `citizen_portal`, `lumina-studio`, `TalkToClibord`
- Conditionally eligible: `tooling-infrastructure` + `verified` = 6 repos — ต้อง Owner ยืนยันว่ามี lifecycle เป็นอิสระจึงติดตามได้
- ไม่ผ่าน gate โดยอัตโนมัติ: `sandbox-experiment` (6), `backup-archive-candidate` (2), `duplicate-superseded-candidate` (1), `unknown` (3) = 12 repos
- Triage Class ไม่กำหนด Lifecycle State (ห้าม infer)

## Legend

- **Import**: `IMP` = imported · `DIS` = discovered-not-imported · `UNK` = unknown
- **Lifecycle**: `ACT` = active · `PAU` = paused · `ARC` = archived · `UNK` = unknown
- **Verify**: `VER` = verified · `OWC` = owner-confirmed · `NEE` = needs-verification
- **Triage Class**: `PRJ` = project · `SBX` = sandbox-experiment · `TLG` = tooling-infrastructure · `BAK` = backup-archive-candidate · `DUP` = duplicate-superseded-candidate · `UNK` = unknown

## Registry Table

| Project | Repository / Source Location | Import | Lifecycle | Verify | Triage Class | Triage Evidence | Project Note | Notes / Evidence |
| ------- | ---------------------------- | ------ | --------- | ------ | ------------ | --------------- | ------------ | ---------------- |
| llm-agents | `D:\llm-agents` | IMP | ACT | VER | — (imported) | imported project (WO-023), outside triage scope | AI agent control/operations system | repo-exists verified 2026-08-11 |
| STT Typing | `D:\stt_typing` | IMP | ACT | VER | — (imported) | imported project (WO-023), outside triage scope | offline-first voice typing / command | repo-exists verified 2026-08-11 |
| AI Worker Harness | `D:\ai-tools\ai-worker-harness` | IMP | ACT | VER | — (imported) | imported project (WO-023), outside triage scope | evidence-driven work-order control plane | repo-exists verified 2026-08-11 |
| Utility Disbursement App | `D:\project_backups\utility-disbursement-app` | IMP | PAU | OWC | — (imported) | imported project (WO-023), outside triage scope | utility bill disbursement process | owner-confirmed paused 2026-07-29 |
| Adobe Stock Upload Assistant | `D:\adobe-stock-upload` | IMP | UNK | VER | — (imported) | imported project (WO-023), outside triage scope | Adobe Stock metadata/upload prep | repo verified; lifecycle ไม่ได้ประกาศใน prior WO → UNK |
| .sandbox/01-longcat | `D:\.sandbox\01-longcat` | DIS | UNK | VER | SBX | fork ของ `D:\llm-agents` (remote=`D:/llm-agents`), README "LLM Agents — Bounded Autonomous Worker", 264 commits, branch `benchmark/run` | sandbox model repo | benchmark experiment — ไม่ใช่โปรเจกต์อิสระ |
| .sandbox/02-deepseek-v4 | `D:\.sandbox\02-deepseek-v4` | DIS | UNK | VER | SBX | fork ของ `D:\llm-agents` (remote=`D:/llm-agents`), 264 commits, branch `benchmark/run` | sandbox model repo | benchmark experiment |
| .sandbox/03-nemotron-ultra | `D:\.sandbox\03-nemotron-ultra` | DIS | UNK | VER | SBX | fork ของ `D:\llm-agents` (remote=`D:/llm-agents`), 264 commits, branch `benchmark/run` | sandbox model repo | benchmark experiment |
| .sandbox/04-step-3.7 | `D:\.sandbox\04-step-3.7` | DIS | UNK | VER | SBX | fork ของ `D:\llm-agents` (remote=`D:/llm-agents`), 264 commits, branch `benchmark/run` | sandbox model repo | benchmark experiment |
| .sandbox/05-mimo-v2.5 | `D:\.sandbox\05-mimo-v2.5` | DIS | UNK | VER | SBX | fork ของ `D:\llm-agents` (remote=`D:/llm-agents`), 264 commits, branch `benchmark/run` | sandbox model repo | benchmark experiment |
| .sandbox/06-north-mini | `D:\.sandbox\06-north-mini` | DIS | UNK | VER | SBX | fork ของ `D:\llm-agents` (remote=`D:/llm-agents`), 264 commits, branch `benchmark/run` | sandbox model repo | benchmark experiment |
| ai-tools-kit | `D:\ai-tools\ai-tools-kit` | DIS | UNK | VER | TLG | README "AI Tools Kit"; skills/scripts; 4 commits; ไม่มี remote | AI tools kit | tooling-infrastructure (owner kit) |
| AI-Workspace | `D:\ai-tools\AI-Workspace` | DIS | UNK | VER | PRJ | README "Expellirmud AI-Workspace"; remote `expellirmud-dot/Expellirmud-AI-Workspace`; 47 commits | AI workspace | **project** (owner GitHub) — ผ่าน onboarding gate |
| computer-use-preview | `D:\ai-tools\computer-use-preview` | DIS | UNK | VER | TLG | README "Computer Use Preview"; remote `google-gemini/computer-use-preview` (third-party); 25 commits | computer-use tool | tooling-infrastructure (third-party mirror) |
| gridgeist | `D:\ai-tools\gridgeist` | DIS | UNK | VER | TLG | README "Gridgeist"; remote `ohmiler/gridgeist` (third-party); 22 commits | unknown tool | tooling-infrastructure (third-party mirror) |
| lightroom-ai-exposure | `D:\ai-tools\lightroom-ai-exposure` | DIS | UNK | VER | PRJ | README "Lightroom AI Exposure Assist"; remote `expellirmud-dot/Lightroom-AI-Workflow-.git`; 96 commits | Lightroom AI exposure | **project** (owner GitHub) — อาจเกี่ยวข้องกับ LR workflow |
| Automation | `D:\Automation` | DIS | UNK | NEE | UNK | 0 commits on all branches; ไม่มี remote; ไม่มี README (มี .rar + โค้ด) | automation scripts | หลักฐานไม่พอ — unverifiable |
| citizen_portal | `D:\citizen_portal` | DIS | UNK | VER | PRJ | README Next.js; remote `expellirmud-dot/citizen-portal`; 37 commits; AGENTS.md/CLAUDE.md | citizen portal | **project** (owner GitHub) — ผ่าน onboarding gate |
| JAVIS_Nexus | `D:\JAVIS_Nexus` | DIS | UNK | NEE | UNK | 0 commits on all branches; ไม่มี remote; ไม่มี README (มี async_engine.py ฯลฯ) | JAVIS Nexus | หลักฐานไม่พอ — unverifiable |
| lumina-studio | `D:\lumina-studio` | DIS | UNK | VER | PRJ | README "LUMINA Studio"; remote `expellirmud-dot/LUMINA-Studio`; 93 commits | lumina studio | **project** (owner GitHub) — ผ่าน onboarding gate |
| mcp-agentic-framework | `D:\mcp-agentic-framework` | DIS | UNK | VER | TLG | README "MCP Agentic Framework"; remote `Piotr1215/mcp-agentic-framework` (third-party); 38 commits | MCP agentic framework | tooling-infrastructure (third-party mirror) |
| office_council_keeper | `D:\office_council_keeper` | DIS | UNK | NEE | UNK | 0 commits on all branches; ไม่มี remote; README หัวข้อ "AI Tools Kit" (คัดลอก); agents/skills | office council keeper | หลักฐานไม่พอ — unverifiable |
| Utility Automation2 | `D:\project_backups\Utility Automation2` | DIS | UNK | VER | BAK | อยู่ใต้ `project_backups/`; README "Utility Automation V2"; remote `expellirmud-dot/utility_automation_v2`; 16 commits | utility automation backup | backup-archive-candidate |
| utility_automation_v2 | `D:\project_backups\utility_automation_v2` | DIS | UNK | VER | BAK | อยู่ใต้ `project_backups/`; README "Utility Automation V2"; remote `expellirmud-dot/utility_automation_v2`; 144 commits | utility automation backup | backup-archive-candidate (canonical copy candidate) |
| utility_automation_v2_light | `D:\project_backups\utility_automation_v2_light` | DIS | UNK | VER | DUP | อยู่ใต้ `project_backups/`; README "Utility Automation V2"; remote `expellirmud-dot/utility_automation_v2`; 172 commits | utility automation backup variant | duplicate-superseded-candidate (remote ซ้ำ) |
| stt-openhands-batch-draft | `D:\stt-openhands-batch-draft` | DIS | UNK | VER | TLG | node project: `package.json` + `work-order/` + `templates`; 2 commits; ไม่มี remote | STT OpenHands batch draft | tooling-infrastructure (draft scaffold) — อาจเกี่ยวข้องกับ STT Typing |
| TalkToClibord | `D:\TalkToClibord` | DIS | UNK | VER | PRJ | README "J.A.V.I.S"; remote `expellirmud-dot/TalkToClibord`; 41 commits | clipboard tool | **project** (owner GitHub) — ผ่าน onboarding gate |
| thai_stt_app | `D:\thai_stt_app` | IMP | UNK | VER | PRJ | AGENTS.md + pyproject; remote `expellirmud-dot/thai_stt_app`; HEAD `be7bd07`, 71 commits; WO-Skill-Audit IN_PROGRESS (2026-08-11) | Thai STT desktop app | **project** (owner GitHub) — onboarded via WO-025 (2026-08-11); Lifecycle UNK (ห้าม infer) |
| codegraph | `D:\tools\codegraph` | DIS | UNK | VER | TLG | README; remote `colbymchenry/codegraph` (third-party); 307 commits | codegraph tooling | tooling-infrastructure (third-party mirror) |

## Discovery Methodology & Limitations

**Method (read-only, 2026-08-11):**
- `find /d -maxdepth 3 -type d -name .git` → 31 git roots (รวม Vault + D:\ root)
- `find /c/Users/Expellirmud -maxdepth 3 -type d -name .git` → 2 (tooling config)
- Triage evidence: read per-repo README/AGENTS, `ls` root, `git branch/HEAD/rev-list/remote` (local `cd` + `git`, ไม่ใช้ `git -C /d/...` ซึ่ง fail ใน env นี้)
- ไม่มีการแก้ไข source repository ใดๆ

**Excluded from inventory (not projects):** `D:\` root `.git`, `D:\Obsidian\Project-Knowledge-Vault` (Vault เอง)

**Limitations:**
- การสำรวจจำกัดที่ `D:\`, `C:\Users\Expellirmud` ความลึก ≤ 3 ระดับ; repo ที่ฝังลึกกว่าหรือยังไม่ clone ไม่อยู่ในขอบเขต
- `Automation`, `JAVIS_Nexus`, `office_council_keeper` มี 0 commits ทุก branch → จำแนก `unknown`/`needs-verification` ไม่สามารถสรุป purpose
- ความสัมพันธ์ (เช่น `stt-openhands-batch-draft`→STT, `lightroom-ai-exposure`→LR) เป็น inference จากชื่อ/README ไม่ใช่ข้อพิสูจน์ lifecycle
- sandbox 6 ตัว remote ชี้ `D:/llm-agents` (local path) → เป็น fork/benchmark ของ imported `llm-agents` ไม่ใช่โปรเจกต์ใหม่
- `codegraph`, `computer-use-preview`, `gridgeist`, `mcp-agentic-framework` remote ชี้ third-party → เป็น mirror/tooling ไม่ใช่โปรเจกต์ของ Owner

## Recommended Next Step

 on-board `Import Missing Projects` — เริ่มจาก 6 `project`+`verified` ที่ผ่าน gate (AI-Workspace, lightroom-ai-exposure, citizen_portal, lumina-studio, TalkToClibord, thai_stt_app) ก่อนเริ่ม `Live Project State / Project Wall Automation`
