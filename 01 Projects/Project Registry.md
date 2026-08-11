---
type: registry
last_reviewed: 2026-08-11
---

# Project Registry

> Inventory กลางของโปรเจกต์ที่ Vault รู้จัก (canonical inventory)
> สร้างโดย WO-OBSIDIAN-023 (2026-08-11)
> Dashboard และ Project Index อ้างอิง Registry นี้เป็นแหล่งรายการหลัก
> ห้ามถือว่ารายชื่อ Project Overview 5 รายการคือ inventory ทั้งหมดโดยปริยาย

## มุมมองสรุป (Summary)

| Import State | Count |
| ------------ | ----- |
| imported | 5 |
| discovered-not-imported | 24 |
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
| verified | 4 |
| owner-confirmed | 1 |
| needs-verification | 24 |

หมายเหตุสรุป:
- `active` = 3 (llm-agents, STT Typing, AI Worker Harness — ประกาศใน prior WO)
- `paused` = 1 (Utility Disbursement App — owner-confirmed)
- `unknown` lifecycle = 25 (Adobe Stock ไม่ได้ประกาศ lifecycle ใน prior WO + 24 discovered)
- `verified` = 4 (5 imported ยกเว้น Utility ที่เป็น owner-confirmed)
- `needs-verification` = 24 discovered (พบว่าเป็น git repo แต่ purpose/lifecycle/ownership ยังไม่ตรวจ)

## Legend

- **Import**: `IMP` = imported · `DIS` = discovered-not-imported · `UNK` = unknown
- **Lifecycle**: `ACT` = active · `PAU` = paused · `ARC` = archived · `UNK` = unknown
- **Verify**: `VER` = verified · `OWC` = owner-confirmed · `NEE` = needs-verification

## Registry Table

| Project | Repository / Source Location | Import | Lifecycle | Verify | Last Verified | Project Note | Notes / Evidence |
| ------- | ---------------------------- | ------ | --------- | ------ | ------------- | ------------ | ---------------- |
| llm-agents | `D:\llm-agents` | IMP | ACT | VER | 2026-07-28 (WO-004 HEAD 099e516) | AI agent control/operations system | repo-exists verified 2026-08-11 (`git`); prior WO verification record |
| STT Typing | `D:\stt_typing` | IMP | ACT | VER | 2026-07-28 (WO-005 HEAD af10254) | offline-first voice typing / command | repo-exists verified 2026-08-11 |
| AI Worker Harness | `D:\ai-tools\ai-worker-harness` | IMP | ACT | VER | 2026-07-28 (WO-006 HEAD 7096991) | evidence-driven work-order control plane | repo-exists verified 2026-08-11 |
| Utility Disbursement App | `D:\project_backups\utility-disbursement-app` | IMP | PAU | OWC | 2026-07-29 (WO-008 HEAD 429cb91) | utility bill disbursement process | owner-confirmed paused 2026-07-29; repo-exists 2026-08-11 |
| Adobe Stock Upload Assistant | `D:\adobe-stock-upload` | IMP | UNK | VER | 2026-07-28 (WO-007 HEAD 0e5f9fc) | Adobe Stock metadata/upload prep | repo-exists verified 2026-08-11; lifecycle ไม่ได้ประกาศใน prior WO → UNK |
| .sandbox/01-longcat | `D:\.sandbox\01-longcat` | DIS | UNK | NEE | 2026-08-11 (repo scan) | sandbox model repo (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |
| .sandbox/02-deepseek-v4 | `D:\.sandbox\02-deepseek-v4` | DIS | UNK | NEE | 2026-08-11 (repo scan) | sandbox model repo (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |
| .sandbox/03-nemotron-ultra | `D:\.sandbox\03-nemotron-ultra` | DIS | UNK | NEE | 2026-08-11 (repo scan) | sandbox model repo (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |
| .sandbox/04-step-3.7 | `D:\.sandbox\04-step-3.7` | DIS | UNK | NEE | 2026-08-11 (repo scan) | sandbox model repo (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |
| .sandbox/05-mimo-v2.5 | `D:\.sandbox\05-mimo-v2.5` | DIS | UNK | NEE | 2026-08-11 (repo scan) | sandbox model repo (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |
| .sandbox/06-north-mini | `D:\.sandbox\06-north-mini` | DIS | UNK | NEE | 2026-08-11 (repo scan) | sandbox model repo (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |
| ai-tools-kit | `D:\ai-tools\ai-tools-kit` | DIS | UNK | NEE | 2026-08-11 (repo scan) | AI tools kit (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |
| AI-Workspace | `D:\ai-tools\AI-Workspace` | DIS | UNK | NEE | 2026-08-11 (repo scan) | AI workspace (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |
| computer-use-preview | `D:\ai-tools\computer-use-preview` | DIS | UNK | NEE | 2026-08-11 (repo scan) | computer-use preview (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |
| gridgeist | `D:\ai-tools\gridgeist` | DIS | UNK | NEE | 2026-08-11 (repo scan) | unknown (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |
| lightroom-ai-exposure | `D:\ai-tools\lightroom-ai-exposure` | DIS | UNK | NEE | 2026-08-11 (repo scan) | Lightroom AI exposure (name-based) | git repo confirmed 2026-08-11; possible relation to LR workflow (inference) |
| Automation | `D:\Automation` | DIS | UNK | NEE | 2026-08-11 (repo scan) | automation scripts (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |
| citizen_portal | `D:\citizen_portal` | DIS | UNK | NEE | 2026-08-11 (repo scan) | citizen portal (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |
| JAVIS_Nexus | `D:\JAVIS_Nexus` | DIS | UNK | NEE | 2026-08-11 (repo scan) | JAVIS Nexus (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |
| lumina-studio | `D:\lumina-studio` | DIS | UNK | NEE | 2026-08-11 (repo scan) | lumina studio (name-based) | git repo confirmed 2026-08-11; possible relation to lumina-photo-harvest (inference) |
| mcp-agentic-framework | `D:\mcp-agentic-framework` | DIS | UNK | NEE | 2026-08-11 (repo scan) | MCP agentic framework (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |
| office_council_keeper | `D:\office_council_keeper` | DIS | UNK | NEE | 2026-08-11 (repo scan) | office council keeper (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |
| Utility Automation2 | `D:\project_backups\Utility Automation2` | DIS | UNK | NEE | 2026-08-11 (repo scan) | utility automation backup (name-based) | git repo confirmed 2026-08-11; possible relation to Utility Disbursement App (inference) |
| utility_automation_v2 | `D:\project_backups\utility_automation_v2` | DIS | UNK | NEE | 2026-08-11 (repo scan) | utility automation backup (name-based) | git repo confirmed 2026-08-11; possible relation to Utility Disbursement App (inference) |
| utility_automation_v2_light | `D:\project_backups\utility_automation_v2_light` | DIS | UNK | NEE | 2026-08-11 (repo scan) | utility automation backup (name-based) | git repo confirmed 2026-08-11; possible relation to Utility Disbursement App (inference) |
| stt-openhands-batch-draft | `D:\stt-openhands-batch-draft` | DIS | UNK | NEE | 2026-08-11 (repo scan) | STT OpenHands batch draft (name-based) | git repo confirmed 2026-08-11; possible relation to STT Typing (inference) |
| TalkToClibord | `D:\TalkToClibord` | DIS | UNK | NEE | 2026-08-11 (repo scan) | clipboard tool (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |
| thai_stt_app | `D:\thai_stt_app` | DIS | UNK | NEE | 2026-08-11 (repo scan) | Thai STT desktop app (name-based) | git repo confirmed 2026-08-11; possible relation to STT Typing (inference) |
| codegraph | `D:\tools\codegraph` | DIS | UNK | NEE | 2026-08-11 (repo scan) | codegraph tooling repo (name-based) | git repo confirmed 2026-08-11; purpose/owner NEE |

## Discovery Methodology & Limitations

**Method (read-only, 2026-08-11):**
- `find /d -maxdepth 3 -type d -name .git` → 31 git roots
- `find /c/Users/Expellirmud -maxdepth 3 -type d -name .git` → 2 (`.agents`, `.codex/memories`) — เป็น tooling config ไม่ใช่โปรเจกต์
- 5 imported repos ตรวจยืนยัน `.git` ครบ
- ไม่มีการแก้ไข source repository ใดๆ

**Excluded from inventory (not projects):**
- `D:\` root `.git` — artifact ของดิสก์ root ไม่ใช่โปรเจกต์
- `D:\Obsidian\Project-Knowledge-Vault` — คือ Vault/Registry host เอง

**Limitations:**
- การสำรวจจำกัดที่พาธที่เมานท์อยู่ภายในเครื่อง (`D:\`, `C:\Users\Expellirmud`) ที่ความลึก ≤ 3 ระดับ
- Repository ที่ฝังลึกกว่าหรือ remote ที่ยังไม่ได้ clone มาอยู่本地 ไม่อยู่ในขอบเขตนี้
- Backup / fork / scratch repos อาจนับเกินหรือขาดได้
- purpose / lifecycle / ownership ของ discovered repos ยัง **ไม่ได้ตรวจ** — ต้อง owner ยืนยันหรือ inspect source ก่อนระบุ lifecycle
- ความสัมพันธ์ที่ใส่เครื่องหมาย "inference" คือการสันนิษฐานจากชื่อเท่านั้น ไม่ใช่ข้อพิสูจน์

## Recommended Next Step

 on-board `Import Missing Projects` ทีละโปรเจกต์ (เริ่มจาก discovered-not-imported) ก่อนเริ่มงาน `Live Project State / Project Wall Automation`
