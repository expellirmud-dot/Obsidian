---
name: project-context-discovery
description: >
  Systematically discover another project's context in read-only mode:
  identify the repository, locate its real authority files, read in a
  bounded order with stop-reading rules, classify every conclusion by
  evidence class, and produce a standard PROJECT_CONTEXT_DISCOVERY
  report for updating the Vault without modifying the source repository.
---

# Project Context Discovery Skill

Use this skill when a Vault task requires exploring an external
project repository to record or refresh its context in the Project
Knowledge Vault.

AGENTS.md must be read before loading any repository skill. This
skill runs after `project-read-first` has produced
`PREFLIGHT_DECISION: READY` for the Vault task that invokes it.

All discovery is read-only. The source repository must never be
modified unless a separate Work Order explicitly authorizes it.

## Three Discovery Levels

### Level 1 — Project Identification

Establish identity and repository truth:

- Project name and its Vault Project Page
- Local path recorded in the Vault
- Canonical Git root (`git rev-parse --show-toplevel`)
- Remote repository (`git remote get-url origin`)
- Branch, HEAD, upstream, and Git status
- Repository existence and dirty/clean state

### Level 2 — Authority and Current State

Locate and read the repository's real authority documents:

- `AGENTS.md`, `PROJECT_RULES.md`, or equivalent governance files
- Current Work Order / Current Task pointer
- README and documentation index
- Project status, roadmap, architecture, and relevant validation
  evidence
- Stop conditions, forbidden files, and commit/push authority

Do not assume every repository uses the same filenames or structure.
Search for candidate authority files from the repository root first,
case-insensitively, before descending into subdirectories.

### Level 3 — Task-Specific Inspection

Use only when documentation evidence is insufficient:

- Serena exact-root symbol inspection
- CodeGraph exact-root dependency query
- Targeted source ranges
- Read only the sections needed to confirm architecture or current
  state

Do not read an entire project's source code without a reason. For
Level 3, Serena and CodeGraph must be verified against the exact
Git root of the source repository per
`project-read-first/references/SERENA_CODEGRAPH_PROTOCOL.md` — the
Vault root must never substitute for the source root.

## Required Discovery Order

1. Read the Vault Project Page and its Resume Context
2. Resolve the exact repository root
3. Verify Git truth (branch, HEAD, upstream, origin, status)
4. Search for authority files from the root first
5. Read the Current Work Order / Current Task pointer
6. Read README or the documentation index
7. Read status, architecture, roadmap, and validation targeted
8. Use Serena/CodeGraph only when needed, and only at the exact root
9. Cross-check conclusions against actual files
10. Produce `PROJECT_CONTEXT_DISCOVERY`
11. Separate verified facts, owner-confirmed facts, inferences, and
    unknowns
12. Propose Vault updates without modifying the source repository

## Stop-Reading Rules

Stop expanding reads once the information answers all of:

- What the project is
- What problem it solves
- Its main scope
- Repository truth
- Current Work Order and current state
- High-level architecture
- Risks and do-not-repeat items
- Required reads for the next session
- One next recommended action

Stop and report (`DISCOVERY_DECISION: BLOCKED`) when:

- The repository path is wrong or does not exist
- The Git root does not match the path recorded in the Vault
- Authority files conflict with each other
- Unexpected dirty files make the current-state summary unreliable
- The task would require secrets, credentials, or external services
- The task would require modifying the source repository
- Serena/CodeGraph cannot be verified for the exact root when source
  inspection is necessary

## Evidence Classification

Every conclusion must cite its origin as exactly one of:

```text
VERIFIED_REPOSITORY_FACT
OWNER_CONFIRMED_FACT
SUPPORTED_INFERENCE
NEEDS_VERIFICATION
```

Never upgrade `needs-verification` to verified based on memory, old
chats, filenames alone, or a Worker Report alone. Only actual file
content and command output verified this session count as
`VERIFIED_REPOSITORY_FACT`.

## Output

Produce the `PROJECT_CONTEXT_DISCOVERY` report defined in
`references/PROJECT_CONTEXT_OUTPUT_CONTRACT.md`. The report ends with
exactly one `DISCOVERY_DECISION: COMPLETE | PARTIAL | BLOCKED` and
one `BLOCK_REASON`.

## Helper Script

`scripts/discover-project.ps1 -ProjectPath <path>` performs the
read-only Level 1 checks and authority-file candidate scan. It never
modifies files or Git state and never claims Serena/CodeGraph
verification.

## Safety Rules

- Read-only: never modify the source repository
- Do not read secrets or credentials
- Do not read binaries or unnecessary personal data
- Do not install dependencies
- Do not commit or push in the source repository
- Do not copy large amounts of source code into the Vault
- Conversation, AI memory, Worker reports, Serena memory, and
  CodeGraph results are supplementary context and never override
  repository files
