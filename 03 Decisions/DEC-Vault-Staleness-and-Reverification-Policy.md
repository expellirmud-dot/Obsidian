---
type: decision
status: accepted
decision_id: DEC-Vault-Staleness-and-Reverification-Policy
date: 2026-07-29
scope: Vault
---

# DEC-Vault-Staleness-and-Reverification-Policy

## บทสรุป

นโยบายนี้กำหนดว่า Project/Architecture/Resume Context ใน Vault ใดถือว่าสด, ล้าสมัย หรือจำเป็นต้องตรวจ Repository ใหม่ โดยแยก metadata freshness ออกจาก content truth และใช้ evidence classification เป็นพื้นฐาน

## ปัจจุบันที่มีผลบังคับ

นโยบายนี้ใช้กับทุกโปรเจกต์ใน Vault จนกว่าจะมี ADR ใหม่supersede ชัดเจน

## นโยบาย freshness

### Freshness states

| State | ความหมาย |
|-------|----------|
| fresh | ข้อมูลตรงกับ repository truth ล่าสุดที่ตรวจแล้ว และไม่มี trigger ใหม่ |
| stale | มี trigger ใหม่ที่ทำให้ต้องตรวจซ้ำ หรือเวลาผ่านไปเกิน threshold |
| partial | ตรวจบางส่วน; ส่วนที่ตรวจแล้ว labeled เป็น verified/owner-confirmed/inference ส่วนที่ยังไม่ตรวจเป็น needs-verification |
| needs-verification | ยังไม่มีหลักฐานในรอบนี้ หรือ trigger ใหม่ปรากฏแต่ยังไม่ตรวจ |

### Staleness triggers

ข้อมูลถือว่า stale เมื่อเกิดอย่างน้อยหนึ่งอย่าง:

1. `HEAD` ของ source repository เปลี่ยนจาก `last_verified_head`
2. `current_work_order` หรือ authority pointer เปลี่ยน
3. dirty working tree เปลี่ยนในลักษณะที่กระทบค่าที่บันทึกไว้ (`worktree_status`, `dirty_details`)
4. ฟีเจอร์/scope ที่มีผลต่อ context เปลี่ยน โดยมีหลักฐานจาก authority ไฟล์
5. เวลาผ่านไปเกิน **30 วัน** ตั้งแต่ `last_verified_date` สำหรับโปรเจกต์ที่มีสถานะ `active`
6. เวลาผ่านไปเกิน **90 วัน** ตั้งแต่ `last_verified_date` สำหรับโปรเจกต์ที่มีสถานะ `paused`/`verified`/`completed` หากมีการ resume

กฎห้าม: **ห้ามถือ `ModifiedAt`/commit date ของไฟล์ใน Vault เป็นหลักฐานความสดของเนื้อหาเพียงอย่างเดียว** ต้องใช้ repository truth + verification record

### Minimum re-verification checks

| สถานะ | Checks ขั้นต่ำเมื่อ fresh → stale |
|--------|--------------------------------|
| active | branch, HEAD, upstream, status, current task pointer, authority file hash หรือ summary ของ authority ไฟล์หลัก |
| paused | branch, HEAD, status, worktree dirty state, current task pointer หรือ NONE |
| verified | branch, HEAD, status, current task pointer หรือ NONE |
| completed | branch, HEAD, status, current task pointer หรือ NONE |
| superseded-pending-roadmap | branch, HEAD, status, active task pointer |

### Evidence classification rules

ใช้ class ตามมาตรฐาน vault:

- `VERIFIED_REPOSITORY_FACT`: ตรวจจาก file content หรือ command output ในรอบนี้
- `OWNER_CONFIRMED_FACT`: 声明โดย Owner โดยตรง ไม่ใช่จาก repo content เพียงอย่างเดียว
- `SUPPORTED_INFERENCE`: Reasoned จาก verified facts; ต้องบอกว่าเป็น inference
- `NEEDS_VERIFICATION`: ยังไม่ตรวจ หรือ trigger ใหม่ปรากฏแต่ยังไม่ตรวจ

### Dirty-worktree handling

- หาก observed `worktree_status: dirty` ให้บันทึก `dirty_details` ให้เฉพาะเจาะจง
- หาก dirty เป็นไฟล์ที่ไม่ได้กระทู้ business logic/context (`dev.db`, build artifact, local config) ให้ถือว่า **dirty-observation only**
- หาก dirty เป็นไฟล์ที่เกี่ยวกับ authority/config/docs ให้ถือว่า **requires re-verification**
- ห้ามใช้สถานะ dirty เป็นเงื่อนไขเดียวในการยกเลิก project state โดยไม่มีหลักฐานอื่น

### Partial verification rules

- partial verification ต้องระบุ:
  - `verification_scope`: ส่วนไหนตรวจแล้ว
  - `unverified_items`: ส่วนไหนยังไม่ตรวจ
  - `observed_limitation`: เหตุผลที่ยังไม่ตรวจ
- ห้ามเปลี่ยน `needs-verification` เป็น `verified` เมื่อยังไม่มี file content/command output ในรอบนั้น
- หาก partial verification อยู่ค้างเกิน threshold ให้กำหนด `re-verification_action`

### Update/closeout procedure

1. อ่าน `Resume Context` และ `Verification Record`
2. ตรวจ `last_verified_head`, `last_verified_date`
3. ตรวจ triggers ว่ามีหรือไม่
4. ทำ minimum checks ตามสถานะ
5. อัปเดต evidence classification ให้ตรงกับรอบนี้
6. ปิด `needs-verification` ได้ก็ต่อเมื่อมี verified/owner-confirmed/inference ที่เพียงพอ
7. ถ้าเปลี่ยน project state ต้องบันทึกว่าใช้ verified หรือ owner-confirmed ที่ใด

## กรณีตัวอย่าง

### กรณี 1: Active project ที่ HEAD เปลี่ยน

โปรเจกต์ `llm-agents` มี `last_verified_head = 099e516`
ผู้ใช้กลับมาทำงานและพบ `HEAD = 099e516` เหมือนเดิม แต่ `current_work_order` เปลี่ยน

- **Trigger**: current_work_order เปลี่ยน
- **Re-verification**: minimum checks = branch, HEAD, status, current task pointer, authority summary
- **Outcome**: ถ้าส่วนที่เปลี่ยนเป็น execution state เท่านั้น และไม่กระทู้ project facts ให้ update `current_work_order` และ verification date

### กรณี 2: Paused project มี tracked modification ใหม่

โปรเจกต์ `Utility Disbursement App` เป็น paused และ `dev.db` เป็น tracked modification

- **Trigger**: dirty working tree เปลี่ยน
- **Re-verification**: minimum checks = HEAD, status, dirty state, current task pointer
- **Outcome**: ถ้า dirty เป็น local artifact เท่านั้น ให้อัปเดต `dirty_details` และ `last_verified_date` แต่ยังคง `paused`

### กรณี 3: Verified project เกิน 90 วัน

โปรเจกต์ `Adobe Stock Upload Assistant` มี `last_verified_date = 2026-07-28` และไม่มี trigger ใหม่

- **Trigger**: เวลาผ่านไปเกิน 90 วัน สำหรับสถานะ paused/verified
- **Re-verification**: minimum checks = branch, HEAD, status, current task pointer
- **Outcome**: ถ้า verified facts ยังคงเป็นอยู่ ให้อัปเดต `last_reviewed` และ verification date; หาก repository truth เปลี่ยน ให้เปรียบเทียบกับ verified facts

## ความเสี่ยง

| ความเสี่ยง | ระดับ | การรับไว้ |
|----------|-------|-----------|
| threshold 30/90 วันไม่ตรงกับ所有 pattern | LOW | ระบุว่าเป็น default policy เปิดให้ปรับตาม evidence |
| dirty state เปลี่ยนบ่อย | MEDIUM | บันทึกเฉพาะเจาะจง และไม่เปลี่ยน project state โดยไม่มีหลักฐาน |
| partial verification ค้างนาน | MEDIUM | กำหนด threshold และ closeout procedure |

## เอกสารที่เกี่ยวข้อง

- [[Project Dashboard]]
- [[Project Index]]
- [[Work Order Index]]
- WO-OBSIDIAN-010
- WO-OBSIDIAN-011

## Verification Record

- Repository checked: read-only discovery via WO-010 policy authoring
- Verified by: AI (WO-OBSIDIAN-010)
- Verification date: 2026-07-29
- Evidence classification: VERIFIED_REPOSITORY_FACT / OWNER_CONFIRMED_FACT / SUPPORTED_INFERENCE / NEEDS_VERIFICATION
