# WO-OBSIDIAN-043 — Restore Evidence-backed Automated Refresh

Status: ACTIVE
Owner: Toto
Started: 2026-10-11T03:29:15+07:00 (observed, Asia/Bangkok)
Classification: VAULT_OPERATIONAL_TOOLING / SOURCE_REPOSITORY
Root: D:\Obsidian\_nexus_work\WO-043 (isolated clean clone)
Repository: https://github.com/expellirmud-dot/Obsidian.git
Baseline: 1fa1ed18e1c900e130262a86af9d65fabc6ddda9

## Goal
Restore trustworthy automated Project Wall updates using the existing OpenHands/GitHub publisher. Fix explicit-purpose evidence extraction; never infer progress or mission from a commit, title or current task.

## Baseline / verified evidence
- 2026-10-10: OpenHands created three daily truth-refresh commits; Github Vault Validation passed.
- Owner's original Vault is dirty and must remain read-only.
- In isolated clone: Python 3.12 pytest 148 PASS, schema validation 22 PASS.
- STT Typing live GitHub evidence: manifest OK, five authority files, but no explicit mission extracted from truncated 500-character content excerpts.
- Serena exact-root health PASS after process-local PATH correction; CodeGraph exact-root index PASS.

## Allowed files
- automation/evidence_collector.py
- automation/freshness_engine.py (only if a validated defect requires)
- automation/refresh_state.py (only if validated integration requires)
- tests/test_evidence_collector.py
- tests/test_freshness_engine.py and tests/test_refresh_state.py (as needed)
- 04 Work Orders/WO-OBSIDIAN-043-RESTORE-AUTOMATED-TRUTH-REFRESH.md
- 04 Work Orders/CURRENT_WORK_ORDER.md
- 04 Work Orders/Work Order Index.md

## Forbidden
- Mutate, stash, reset, clean or pull original owner Vault; modify any source project.
- Fabricate purpose, promote stale truth to fresh without evidence, rewrite historical closed WOs.
- Duplicate OpenHands scheduler; alter global shared tools or install credentials.
- Push, merge or cleanup unless all candidate-current safety gates pass.

## Steps
- [x] Verify Git baseline, original dirty files, worktree and correct remote.
- [x] Verify existing OpenHands commits/CI and reproduce missing STT semantic evidence.
- [x] Serena and CodeGraph exact-root gates PASS.
- [x] Baseline tests 148 PASS and state schema 22 PASS.
- [x] Implement bounded full-authority explicit-purpose extraction, Thai purpose headings and regression tests.
- [x] Validate Python 3.12: 151 tests PASS, 22/22 states VALID, renderer twice zero diff. Live GitHub evidence: STT manifest OK with no explicit mission (remains stale); online-job-factory verified explicit mission and dry-run FRESH (no mutation).
- [ ] Commit, push PR, review, CI and merge only after gate checks.
- [ ] Verify remote/publisher continuity, reconcile WO, safe cleanup, final report.

## Acceptance
Explicit mission in real authority must be extractable even when after byte 500; manifest stays bounded and source provenance is retained. Non-explicit documents remain UNKNOWN/STALE. CI and correct branch/HEAD verification are mandatory. Do not claim scheduler end-to-end verified without seeing a subsequent real run.

## Final Report
Pending.
