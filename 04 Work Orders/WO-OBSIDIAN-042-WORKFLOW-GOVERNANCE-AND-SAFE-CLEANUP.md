# WO-OBSIDIAN-042 — Workflow Governance & Safe Recovery
Work Order ID: WO-OBSIDIAN-042
Status: IN_PROGRESS
Owner: Toto
Start: 2026-10-09 (Asia/Bangkok; precise start reported in task conversation)
Task Classification: VAULT_DOCUMENTATION
Risk Level: MEDIUM
Execution Mode: isolated clean clone; bounded single-writer; independent read-only reviews
Repository: expellirmud-dot/Obsidian
Baseline HEAD: 54cb8a8fac8b9ac7098ec37e1a3e57744d3eec4e
Execution Root: D:\Obsidian\_nexus_work\WO-042
Original Vault Root: D:\Obsidian\Project-Knowledge-Vault

## Objective
Codify workflow-first Nexus controller governance and safe Git/PR/deploy/cleanup gates. Reconcile local-versus-remote evidence while preserving all pre-existing owner files. Reuse existing Project Resume Workflow and README/AGENTS authority rather than create duplicate knowledge maps.

## Required Read Order
AGENTS.md; .agents/skills/project-read-first/SKILL.md; README.md; 00 Dashboard/Project Dashboard.md; 04 Work Orders/CURRENT_WORK_ORDER.md; WO-041; 05 Prompts/Project Resume Workflow.md; D:\tools\TOOLS.md and applicable continuity/kernel contracts.

## Preflight and authority
READ_FIRST_PREFLIGHT: READY for isolated clean clone on correct remote HEAD, with no unexpected dirty files at initiation. Original local Vault separately BLOCKED_DIRTY_WORKTREE and strictly read-only; no change to shared D:\tools, global registries, or other source repos. New WO explicitly authorized by Owner on 2026-10-09.

## Allowed Files
- 04 Work Orders/WO-OBSIDIAN-042-WORKFLOW-GOVERNANCE-AND-SAFE-CLEANUP.md
- 04 Work Orders/CURRENT_WORK_ORDER.md
- 04 Work Orders/Work Order Index.md
- 05 Prompts/Project Resume Workflow.md
- AGENTS.md (brief pointer only if essential)
- README.md (brief pointer only if essential)

## Forbidden
- Original dirty Vault mutation/stash/reset/clean/pull
- Untracked owner artifacts and nested system_prompts_leaks repo
- Source repositories, secrets, credentials, shared D:\tools
- Unrelated Dashboard, YAML states, automation code, policy changes
- New deploy target or new external commitments
- Cleanup without confirmed merged target, path provenance and clean disposable worktree

## Checklist
- [x] Verify remote, local divergence, owner dirty files, isolation baseline
- [x] Read mandatory authority and prior workflow
- [ ] Update existing canonical Project Resume Workflow with Nexus governance
- [ ] Review scope, markdown references, diff and risk-based validation
- [ ] Commit, push, open PR, review and merge if gates permit
- [ ] Verify target HEAD and safe cleanup, then final report / closeout

## Worker Routing
Readers/reviewers may run in parallel on evidence and document review. Exactly one writer for this worktree; controller validates. Model/provider routing from live inventory; no silent paid API fallback. No CLI worker needed for deterministic markdown edits unless a verified safe model is available.

## Validation
Git diff --check; changed files only Allowed Files; all referenced canonical paths exist or are explicitly optional; no credential content; Work Order pointer and index consistent; no change to original local files; no duplicate policy owner; GitHub PR and required checks only when applicable.

## Done
Verified intended governance in canonical workflow, Work Order closed with true evidence, PR merged on actual remote main if enabled, cleanup gate evaluated, original owner data untouched. If any required gate fails, report BLOCKED/PARTIAL rather than claim completion.
