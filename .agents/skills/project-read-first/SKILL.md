---
name: project-read-first
description: >
  Establish repository truth before any modification by resolving the
  exact Git root, classifying the task, verifying Serena and CodeGraph
  only when source code is involved, reading mandatory Vault authority
  documents, and producing a bounded preflight decision before any
  file modification.
---

# Project Read-First Skill — Vault Edition

Use this skill at the start of every task in this repository to
establish exact project truth before reading implementation files or
making changes.

AGENTS.md must be read before loading any repository skill.

## 1. Resolve Git Repository Root

Run:

```powershell
git rev-parse --show-toplevel
```

The repository root is the canonical project root for all subsequent
steps. Do not assume or hard-code the root from a previous session.

## 2. Verify Repository State

From the canonical Git root, capture:

- Current directory (`pwd`)
- Active branch (`git branch --show-current`)
- HEAD commit (`git rev-parse HEAD`)
- Upstream branch (`git rev-parse --abbrev-ref HEAD@{upstream}` if
  one exists)
- Origin URL (`git remote get-url origin`)
- Git status (`git status --short`)

Expected pre-existing owner artifacts in this Vault (untracked, must
be preserved, never staged, never modified):

```text
.obsidian/
IDEA.md
```

Separate expected dirty files from unexpected dirty files. Expected
files are the owner artifacts above plus files explicitly listed as
Allowed Files by the active Work Order. If unexpected tracked
modifications or unexpected untracked files exist, stop and report
`BLOCKED_DIRTY_WORKTREE`.

## 3. Classify the Task

### VAULT_DOCUMENTATION

Markdown, Dashboard, Index, Template, Project Overview, or Resume
Context work inside the Vault:

```text
SERENA_PROJECT: not_required
SERENA_STATUS: not_required
CODEGRAPH_PROJECT: not_required
CODEGRAPH_STATUS: not_required
CODEGRAPH_SYNC: not_required
```

For documentation-only Vault tasks, Serena and CodeGraph are
not required. They become mandatory only when the task reads,
analyzes, or modifies source code. Serena and CodeGraph must not
block documentation-only tasks.

### SOURCE_REPOSITORY

Tasks that read, analyze, or modify source code:

- Resolve the exact Git root of the actual source repository.
- Serena must match that exact Git root.
- CodeGraph must match that exact Git root.
- The Vault root must never substitute for a source repository root.
- If tool verification is impossible, the task must block.

## 4. Activate Serena for the Exact Repository Root (SOURCE_REPOSITORY only)

Activate Serena using the canonical Git root:

```python
mcp__serena__activate_project(
    project="<canonical-git-root>"
)
```

Then verify Serena is active:

```python
config = mcp__serena__get_current_config()
```

Confirm the active project path matches the canonical Git root from
step 1. If it does not match, use the correct project name from
`config.projects` or pass the absolute root path to `activate_project`.

Reject a parent, sibling, historical, or previously active project.
Finding a Serena executable on PATH is not verification.

## 5. Verify CodeGraph Is Indexed for the Same Root (SOURCE_REPOSITORY only)

Run CodeGraph diagnostics or an introspection query to confirm the
indexed path equals the canonical Git root and that the index is
recent enough for the current task.

The existence of an index directory on disk is not verification.
If CodeGraph cannot be verified for the exact root, the terminal
preflight decision must be `BLOCKED_CODEGRAPH`.

## 6. Read Mandatory Authority Documents (Full Read)

Read these documents completely before any other task work:

1. `AGENTS.md`
2. `README.md`
3. `00 Dashboard/Project Dashboard.md`
4. `04 Work Orders/CURRENT_WORK_ORDER.md`
5. The active Work Order referenced by `CURRENT_WORK_ORDER.md`

These files define authority and scope. Do not replace them with
summaries.

## 7. Read Targeted Documents (Conditional)

Based on the active Work Order's scope, read additional documents
only as needed. Prefer targeted section reads over full-file reads.

Default targeted behavior:

- Project Overview pages in `01 Projects/` — read status header,
  Resume Context, and Verification Record for the projects the task
  touches.
- Index files (`02 Architecture` … `99 Archive`) — read only when the
  task changes that category.
- Source code — prefer Serena symbol overview, exact symbol reads,
  CodeGraph dependency queries, and targeted line ranges before full
  file reads.

Escalate to a full read when:

- A safety contract governs the task.
- The active Work Order requires it.
- Definitions are distributed across the file.
- Targeted sections conflict or remain ambiguous.
- Closeout requires confirming the complete document remains accurate.

## 8. Produce Preflight Report

Output a deterministic preflight report using the exact shape defined
in `references/PREFLIGHT_OUTPUT_CONTRACT.md`. Every field uses the
`FIELD: value` format. The report contains exactly one
`READ_FIRST_PREFLIGHT` header, one `PREFLIGHT_DECISION`, and one
`BLOCK_REASON`.

## 9. Terminal Preflight Decisions

The skill must produce exactly one of:

| Decision | Meaning |
|---|---|
| `READY` | All checks passed; implementation may begin |
| `BLOCKED_DIRTY_WORKTREE` | Unexpected dirty or untracked files exist |
| `BLOCKED_PROJECT_MISMATCH` | Serena or CodeGraph project does not match Git root |
| `BLOCKED_SERENA` | Serena cannot be activated or verified for the exact root |
| `BLOCKED_CODEGRAPH` | CodeGraph cannot be verified for the exact root |
| `BLOCKED_MISSING_AUTHORITY` | Mandatory authority document is missing |
| `BLOCKED_SCOPE_CONFLICT` | Active Work Order scope is ambiguous |
| `BLOCKED_OWNER_DECISION` | Action requires owner authority |

Implementation may begin only after `READY`.

Only these eight values are valid terminal decisions. Generic status
words (for example PASS, SUCCESS, or AVAILABLE) must never be used as
a terminal decision.

## Safety Rules

- Do not read secrets or credentials.
- Do not modify any repository outside the active Work Order.
- Do not read binary files or unnecessary personal data.
- Do not call external AI services during preflight.
- Do not install dependencies during preflight.
- Do not modify Git state during preflight.
- Do not commit or push during preflight.
- Do not edit files during preflight; only read.

## Authority Rule

Conversation, AI memory, Worker reports, Serena memory, and
CodeGraph results are supplementary context and never override
repository files.

## Read-First Invocation Rule

Every task must invoke this skill before implementation begins.
The active Work Order's Required Read Order section defines the
mandatory read set; this skill defines the verification that those
reads completed correctly.
