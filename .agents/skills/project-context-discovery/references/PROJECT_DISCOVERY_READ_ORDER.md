# Project Discovery Read Order

This reference defines the bounded read order the
project-context-discovery skill must follow when exploring an
external project repository. All reads are read-only.

## Phase 0 — Vault Context (before touching the repository)

| Step | Read | Purpose |
|---|---|---|
| 0.1 | `01 Projects/<Project>.md` (Vault page) | Recorded path, status, Resume Context, prior risks |
| 0.2 | Vault page Verification Record | What was verified before, and when |

## Phase 1 — Repository Identification (Level 1)

| Step | Command / Read | Purpose |
|---|---|---|
| 1.1 | Confirm local path exists | Path truth |
| 1.2 | `git rev-parse --show-toplevel` | Canonical Git root |
| 1.3 | `git branch --show-current`, `git rev-parse HEAD` | Branch + HEAD |
| 1.4 | `git rev-parse --abbrev-ref HEAD@{upstream}` | Upstream |
| 1.5 | `git remote get-url origin` | Remote |
| 1.6 | `git status --short` | Dirty/clean state |
| 1.7 | Top-level file/directory listing | Structure overview |

If 1.1 or 1.2 fails, or the Git root does not match the Vault page,
stop with `DISCOVERY_DECISION: BLOCKED`.

## Phase 2 — Authority Discovery (Level 2)

Search from the repository root first, case-insensitively. Candidate
authority filenames (non-exhaustive — never assume one layout):

```text
AGENTS.md
PROJECT_RULES.md
CLAUDE.md
CONTRIBUTING.md
GOVERNANCE.md
CURRENT_WORK_ORDER.md (any casing/location)
work-order/ | work_orders/ | Work-Order/ (directories)
docs/INDEX.md | docs/README.md
README.md
```

Read order within Phase 2:

1. Governance files found at root (`AGENTS.md`, `PROJECT_RULES.md`, …)
2. Current Work Order / Current Task pointer, then the active Work
   Order it references
3. README or documentation index
4. Status / roadmap / architecture / validation evidence — targeted
   sections only

Record for each authority file: path, whether read fully or targeted,
and what authority it claims (scope, forbidden files, commit/push
rules, stop conditions).

## Phase 3 — Task-Specific Inspection (Level 3, conditional)

Enter only when Phase 2 evidence cannot answer a required question.

1. Verify Serena against the source repository's exact Git root
2. Verify CodeGraph against the same exact root
3. Prefer symbol overview → exact symbol reads → targeted line ranges
4. Record every inspected symbol in `SOURCE_SYMBOLS_INSPECTED`

If verification for the exact root fails, stop with
`DISCOVERY_DECISION: BLOCKED` rather than inspecting unverified.

## Escalation and Stop

- Apply the Stop-Reading Rules from `SKILL.md` after every phase.
- Escalate to a full-file read only when targeted sections conflict,
  definitions are distributed, or a safety contract governs the task.
- Never read secrets, credentials, binaries, or bulk personal data.

## Forbidden

- Modifying anything in the source repository
- Assuming filenames or structure from another project
- Treating file existence as evidence of content
- Copying large source files into the Vault
