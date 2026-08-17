# Project Knowledge Vault

> Obsidian เป็นแหล่งความรู้และบริบทระยะยาว
> Git repository และ Current Work Order เป็นแหล่งความจริงของงาน

## Vault นี้ใช้ทำอะไร

Vault นี้เป็นคลังความรู้กลางสำหรับเก็บข้อมูลโปรเจกต์ทั้งหมด เพื่อให้มนุษย์และ AI สามารถกลับมาอ่านบริบทเดิมและทำงานต่อได้ โดยไม่ต้องพึ่งความจำหรือประวัติแชทเพียงอย่างเดียว

เก็บ: ภาพรวมโปรเจกต์ / จุดประสงค์และขอบเขต / ตำแหน่ง Source Code / สถาปัตยกรรมระดับภาพรวม / การตัดสินใจสำคัญ / บทเรียน / Resume Context / ลิงก์ไปยัง Work Order

## ความแตกต่างระหว่าง Vault กับ Git Repository

| | Vault | Git Repository |
|---|---|---|
| หน้าที่ | บริบท ความรู้ สรุป การตัดสินใจ | Source Code และสถานะจริงของงาน |
| ความจริง | อาจล้าสมัยได้ ต้องระบุ `needs-verification` | แหล่งความจริงลำดับที่ 1 |
| การอัปเดต | สรุปหลังงานเสร็จ / รอบทบทวน | ทุก commit |

ลำดับแหล่งความจริง: 1) Git repository และไฟล์จริง 2) Current Work Order 3) Vault นี้ 4) Conversation / ความจำ AI

## โครงสร้างโฟลเดอร์

```text
Project-Knowledge-Vault
├── AGENTS.md                  กฎระดับ Vault — AI ต้องอ่านก่อนทำงาน
├── README.md                  ไฟล์นี้
├── .agents                    Repository skills (.agents/skills/project-read-first/SKILL.md)
├── 00 Dashboard               ภาพรวมและทางเข้าหลัก
├── 01 Projects                หน้า Project Overview ของแต่ละโปรเจกต์
├── 02 Architecture            เอกสารสถาปัตยกรรม (ARCH-<Project>-<Topic>.md)
├── 03 Decisions               บันทึกการตัดสินใจ (ADR-<Project>-<Number>-<Title>.md)
├── 04 Work Orders             Work Order authority (CURRENT_WORK_ORDER.md + WO-*.md)
├── 05 Lessons Learned         บทเรียน (LESSON-<Project>-<Number>-<Title>.md)
├── 06 Prompts                 Prompt และ Templates
├── 07 Attachments             ไฟล์แนบ รูปภาพ
└── 99 Archive                 เอกสารเก่าที่เลิกใช้ (เก็บหลักฐานเดิม ไม่ลบ)
```

## Work Order Authority

- Current Work Order pointer: `04 Work Orders/CURRENT_WORK_ORDER.md`
- Work Order ใหม่ทั้งหมดต้องอยู่ใน `04 Work Orders`
- `work-order/WO-OBSIDIAN-001.md` เป็น legacy historical location — เก็บไว้เพื่อรักษาประวัติ Git ไม่ย้าย ไม่แก้
- Skill เริ่มงาน: `.agents/skills/project-read-first/SKILL.md` — ทุกงานต้องผ่าน READ_FIRST_PREFLIGHT ก่อนแก้ไฟล์
- Skill สำรวจโปรเจกต์: `.agents/skills/project-context-discovery/SKILL.md` — ใช้ก่อน onboard หรืออัปเดตบริบทโปรเจกต์ภายนอกเข้า Vault (read-only ต่อ Source Repository; output ตาม `.agents/skills/project-context-discovery/references/PROJECT_CONTEXT_OUTPUT_CONTRACT.md`)

## Runtime Setup (Live Project Wall)

สำหรับการรัน `scripts/render_project_wall.py` บน fresh clone:

```bash
# 1. ติดตั้ง dependencies
python3 -m pip install -r requirements.txt

# 2. Validate ทุก state file (ต้อง 11/11 VALID)
python3 scripts/render_project_wall.py --validate-all

# 3. Render Live Project Wall (idempotent — รอบที่สองต้อง zero diff)
python3 scripts/render_project_wall.py

# 4. Validate state file เดียว
python3 scripts/render_project_wall.py --validate automation/state/<project_id>.yaml
```

ต้องการ: Python 3.10+ (ใช้ `from __future__ import annotations` และ `list[str]` hints)

## วิธีเพิ่มโปรเจกต์ใหม่

1. คัดลอก `06 Prompts/Templates/Project Template.md` ไปไว้ที่ `01 Projects/<Project Name>.md`
2. กรอกข้อมูลที่ยืนยันได้จริง — ส่วนที่ยังไม่ตรวจให้ใช้ `needs-verification`
3. เพิ่มแถวใน `01 Projects/Project Index.md`
4. เพิ่มลิงก์ใน `00 Dashboard/Project Dashboard.md`

## วิธีอัปเดต Resume Context

1. เปิดหน้าโปรเจกต์ใน `01 Projects`
2. ตรวจ Repository truth (git status, branch, HEAD) และ Current Work Order
3. อัปเดตหัวข้อ Resume Context และ `last_reviewed:` เป็นวันที่ตรวจจริง
4. บันทึก Verification Record (HEAD, ผู้ตรวจ, วันที่)

## วิธีเริ่มงานรอบใหม่

1. เปิด `00 Dashboard/Project Dashboard.md`
2. เปิดหน้าโปรเจกต์ที่จะทำ อ่าน Resume Context
3. ตรวจ Repository truth และ Current Work Order จริง
4. อัปเดตข้อมูลที่ล้าสมัยใน Vault
5. เริ่มงานตาม Work Order ใหม่

## วิธีจัดเก็บเอกสารเก่า

- ย้ายเอกสารที่เลิกใช้ไป `99 Archive` โดยเก็บชื่อเดิม เพิ่มวันที่เมื่อจำเป็น
- ห้ามลบประวัติการตัดสินใจ — ADR ที่ถูกแทนที่ให้ระบุสถานะ Superseded และลิงก์ไป ADR ใหม่

## คำเตือน: Secret และข้อมูลส่วนบุคคล

ห้ามบันทึกใน Vault นี้เด็ดขาด:

- Password, API Key, Access Token, Session Cookie, Private Credential
- ข้อมูลส่วนบุคคลที่ไม่จำเป็น
- Source Code จำนวนมากที่ซ้ำกับ Repository

ดูกฎฉบับเต็มที่ [[AGENTS]] และเริ่มต้นที่ [[Project Dashboard]]
