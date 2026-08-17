# WORK ORDER — PROGRESS + NEXT ACTION ENGINE

Work Order ID: WO-OBSIDIAN-039
Title: WO-OBSIDIAN-039 — Progress + Next Action Engine
Risk Level: MEDIUM (deterministic progress computation)
Task Classification: Vault Operational Tooling / Progress Layer
Execution Mode: Bounded Single Work Order
Owner: Toto
Target Vault: `D:\Obsidian\Project-Knowledge-Vault`
Status: CLOSED

> CLOSED — deterministic evidence-constrained progress engine implemented;
> weighted milestones / bounded milestones / UNKNOWN; next-action from explicit authority;
> 43/43 tests PASS.

## 1. Objective

สร้าง deterministic/evidence-constrained progress engine ที่:
- คำนวณ progress จาก evidence เท่านั้น (ไม่ใช่ LLM impression)
- Priority: weighted roadmap milestones → bounded milestones → bounded work-order set → UNKNOWN
- ห้าม LLM สร้าง percentage จาก impression ("ดูเหมือน 80%")
- ถ้ามี evidence พอ: output estimate, range, confidence, calculation_method, evidence_basis
- ถ้าไม่มี denominator: UNKNOWN

## 2. Next Action

Derive จาก:
1. explicit Current WO/Task
2. roadmap dependency (first incomplete milestone)
3. open blocker resolution
4. next planned milestone
ถ้าไม่มี evidence: `next_action: unknown` (ห้าม invent งานใหม่)

## 3. Implemented

- `automation/progress_engine.py` — parse_milestones_from_content() / compute_weighted_progress() / compute_bounded_milestones() / compute_unknown_progress() / derive_next_action() / apply_progress_to_state() / CLI
- `tests/test_progress_engine.py` — 8 tests

## 4. Determinism

Identical inputs produce identical outputs (tested). The basis string explains exactly how numbers were derived (e.g. "weighted milestones: 4/10 weight units completed (2/3 milestones)").

## 5. Validation

- `python3 automation/progress_engine.py compute --all` → all 11 projects computed (UNKNOWN where no roadmap evidence; next_action from authority where present)
- `python3 scripts/render_project_wall.py --validate-all` → 11/11 VALID
- `python3 -m pytest tests/` → 43/43 PASS

## 6. Definition of Done

- [x] weighted milestone progress (explicit weights)
- [x] bounded milestone progress (equal weight)
- [x] missing denominator -> UNKNOWN
- [x] next action from explicit authority
- [x] no authority -> next_action unknown (None)
- [x] next action from blocker
- [x] next action from first incomplete milestone
- [x] deterministic (identical inputs -> identical outputs)
- [x] no LLM impression / no fabrication
- [x] 43/43 tests PASS
