# Project Context Output Contract

This reference defines the minimum output the
project-context-discovery skill must produce after exploring a
project repository. Every field uses the `FIELD: value` format.

## Contract

```text
PROJECT_CONTEXT_DISCOVERY

PROJECT_NAME:
VAULT_PAGE:
REPOSITORY_ROOT:
REMOTE:
BRANCH:
HEAD:
UPSTREAM:
GIT_STATUS:

AUTHORITY_FILES:
CURRENT_WORK_ORDER:
WORK_ORDER_STATUS:
DOCUMENTATION_INDEX:

PROJECT_PURPOSE:
PROBLEM_SOLVED:
IN_SCOPE:
OUT_OF_SCOPE:
ARCHITECTURE_SUMMARY:
CURRENT_STATE:
COMPLETED_WORK:
OPEN_WORK:
KNOWN_RISKS:
DO_NOT_REPEAT:
REQUIRED_READS:

SERENA_STATUS:
CODEGRAPH_STATUS:
SOURCE_SYMBOLS_INSPECTED:

VERIFIED_FACTS:
OWNER_CONFIRMED_FACTS:
SUPPORTED_INFERENCES:
UNVERIFIED_ITEMS:

RECOMMENDED_VAULT_UPDATES:
NEXT_RECOMMENDED_ACTION:
DISCOVERY_DECISION: COMPLETE | PARTIAL | BLOCKED
BLOCK_REASON:
```

## Field Definitions

| Field | Description |
|---|---|
| `PROJECT_NAME` | Project name as used by the Vault page |
| `VAULT_PAGE` | Path to the page in `01 Projects/` |
| `REPOSITORY_ROOT` | Output of `git rev-parse --show-toplevel` |
| `REMOTE` | Origin URL or `NONE` |
| `BRANCH` | Active branch |
| `HEAD` | Full commit SHA |
| `UPSTREAM` | Upstream ref or `NONE` |
| `GIT_STATUS` | Short status; `clean` if empty |
| `AUTHORITY_FILES` | Governance files found, with paths |
| `CURRENT_WORK_ORDER` | Active Work Order path or `NONE` / `NOT_FOUND` |
| `WORK_ORDER_STATUS` | Status recorded in that Work Order |
| `DOCUMENTATION_INDEX` | Documentation index path or `NONE` |
| `PROJECT_PURPOSE` | What the project is |
| `PROBLEM_SOLVED` | The problem it addresses |
| `IN_SCOPE` / `OUT_OF_SCOPE` | Scope boundary summary |
| `ARCHITECTURE_SUMMARY` | High-level architecture only |
| `CURRENT_STATE` | State supported by repository evidence |
| `COMPLETED_WORK` | Work proven complete by evidence |
| `OPEN_WORK` | Work in progress / planned per authority files |
| `KNOWN_RISKS` | Risks recorded or observed |
| `DO_NOT_REPEAT` | Proven dead ends or forbidden repeats |
| `REQUIRED_READS` | Files the next session must read first |
| `SERENA_STATUS` | `not_required`, `active_verified`, or `not_verified` |
| `CODEGRAPH_STATUS` | `not_required`, `index_verified`, or `not_verified` |
| `SOURCE_SYMBOLS_INSPECTED` | Symbols inspected in Level 3, or `none` |
| `VERIFIED_FACTS` | Conclusions with class `VERIFIED_REPOSITORY_FACT` |
| `OWNER_CONFIRMED_FACTS` | Conclusions with class `OWNER_CONFIRMED_FACT` |
| `SUPPORTED_INFERENCES` | Conclusions with class `SUPPORTED_INFERENCE` |
| `UNVERIFIED_ITEMS` | Items remaining `NEEDS_VERIFICATION` |
| `RECOMMENDED_VAULT_UPDATES` | Proposed edits to Vault pages only |
| `NEXT_RECOMMENDED_ACTION` | Exactly one primary recommendation |
| `DISCOVERY_DECISION` | `COMPLETE`, `PARTIAL`, or `BLOCKED` |
| `BLOCK_REASON` | Empty unless `BLOCKED`; exact reason |

## Decision Semantics

| Decision | Meaning |
|---|---|
| `COMPLETE` | All Stop-Reading questions answered with evidence |
| `PARTIAL` | Some questions unanswered; unknowns listed in `UNVERIFIED_ITEMS` |
| `BLOCKED` | A stop condition was hit; `BLOCK_REASON` required |

## Evidence Classes

Every conclusion in the four evidence sections must belong to exactly
one class:

```text
VERIFIED_REPOSITORY_FACT   — proven by file content or command output this session
OWNER_CONFIRMED_FACT       — stated directly by the Owner
SUPPORTED_INFERENCE        — reasoned from verified facts; marked as inference
NEEDS_VERIFICATION         — recorded but not yet proven
```

`RECOMMENDED_VAULT_UPDATES` must never propose changes to the source
repository — Vault pages only.
