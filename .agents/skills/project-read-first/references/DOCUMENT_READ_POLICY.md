# Document Read Policy — Vault Edition

This reference document defines how the project-read-first skill
selects and reads documents during preflight in the Project
Knowledge Vault.

## Mandatory Full Reads

The skill must require complete reads of:

1. `AGENTS.md` — repository-wide execution, safety, and closeout rules
2. `README.md` — Vault usage, structure, and authority boundary
3. `00 Dashboard/Project Dashboard.md` — entry point and project map
4. `04 Work Orders/CURRENT_WORK_ORDER.md` — pointer to the active Work Order
5. The active Work Order file itself (as pointed to by step 4)

These files define authority and scope and must not be
replaced by summaries.

## Targeted Read Policy

The skill must avoid unnecessary broad reads. Use targeted section
reads (offset/limit around the relevant section) as the default.

### Default Targeted Behavior

| Document | Sections to Read |
|---|---|
| `01 Projects/<Project>.md` | Status header, Resume Context, and Verification Record of projects the task touches |
| Category index files (`02 Architecture` … `99 Archive`) | Only when the task changes that category |
| `06 Prompts/Templates/*` | Only when creating a document from that template |
| Source code (SOURCE_REPOSITORY tasks) | Prefer Serena symbol overview, exact symbol reads, CodeGraph dependency queries, and targeted line ranges before full-file reads |

### Escalation Rules

Escalate to a full read when:

1. A safety contract governs the task.
2. The active Work Order requires it.
3. Definitions are distributed across the file.
4. Targeted sections conflict or remain ambiguous.
5. Closeout requires confirming the complete document remains accurate.

### Forbidden Escalations

- Do not read secrets, credentials, or unnecessary personal data.
- Do not read binary files.
- Do not escalate reads beyond what the active Work Order's Required
  Read Order allows.
- Do not copy large amounts of source code into the Vault.

## Priority Rules

When two documents at the same authority level conflict:

1. The active Work Order takes priority.
2. If both are Work Orders at equal level, the more recent commit wins.
3. If still conflicting, stop and report the conflict rather than
   choosing silently.

Authority order for this Vault (from `AGENTS.md`):

1. Git repository and actual project files
2. Current Work Order or Current Task Pointer
3. Authority documents inside the repository
4. Obsidian Project Knowledge Vault
5. Worker Report
6. Conversation and AI memory

## Read Verification

After completing reads, the skill must confirm:

- Each file in the mandatory full-read list was successfully opened
  and non-empty.
- Any targeted reads were scoped to the correct section (no unrelated
  sections absorbed).
- No forbidden documents (secrets, credentials, binaries, personal
  data) were read.
