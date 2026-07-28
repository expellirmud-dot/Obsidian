# Preflight Output Contract — Vault Edition

This reference document defines the exact output shape the
project-read-first skill must produce.

## Contract

The skill must produce exactly this shape. Every field uses the
`FIELD: value` format. `READ_FIRST_PREFLIGHT`, `PREFLIGHT_DECISION`,
and `BLOCK_REASON` each appear exactly once.

```text
READ_FIRST_PREFLIGHT

REPOSITORY_ROOT:
CURRENT_DIRECTORY:
BRANCH:
HEAD:
UPSTREAM:
ORIGIN:
GIT_STATUS:
EXPECTED_DIRTY_FILES:
UNEXPECTED_DIRTY_FILES:

TASK_CLASSIFICATION:
ACTIVE_WORK_ORDER:
WORK_ORDER_STATUS:
ALLOWED_FILES:
FORBIDDEN_FILES:

SERENA_PROJECT:
SERENA_STATUS:
CODEGRAPH_PROJECT:
CODEGRAPH_STATUS:
CODEGRAPH_SYNC:

FULL_DOCUMENTS_READ:
TARGETED_DOCUMENTS_READ:
SOURCE_SYMBOLS_INSPECTED:

EXPECTED_CHANGE:
REQUIRED_VALIDATION:
DOCUMENTATION_IMPACT:
COMMIT_AUTHORIZATION:

PREFLIGHT_DECISION: <one of the eight decision values>

BLOCK_REASON: <empty if READY, otherwise exact reason>
```

## Field Definitions

| Field | Description |
|---|---|
| `REPOSITORY_ROOT` | Output of `git rev-parse --show-toplevel` |
| `CURRENT_DIRECTORY` | Working directory at skill start |
| `BRANCH` | Active branch name |
| `HEAD` | Full commit SHA of HEAD |
| `UPSTREAM` | Upstream branch reference |
| `ORIGIN` | Origin remote URL |
| `GIT_STATUS` | Output of `git status --short` |
| `EXPECTED_DIRTY_FILES` | Dirty/untracked paths that are owner artifacts or Allowed Files |
| `UNEXPECTED_DIRTY_FILES` | Dirty/untracked paths outside the expected list |
| `TASK_CLASSIFICATION` | `VAULT_DOCUMENTATION` or `SOURCE_REPOSITORY` |
| `ACTIVE_WORK_ORDER` | Path to active Work Order or NONE |
| `WORK_ORDER_STATUS` | STATUS field from the Work Order |
| `ALLOWED_FILES` | Count of files in the Work Order Allowed Files list |
| `FORBIDDEN_FILES` | Count of paths in the Work Order Forbidden Files/Actions list |
| `SERENA_PROJECT` | Exact root verified, or `not_required` for VAULT_DOCUMENTATION |
| `SERENA_STATUS` | `active_verified`, `not_verified`, or `not_required` |
| `CODEGRAPH_PROJECT` | Indexed path verified, or `not_required` for VAULT_DOCUMENTATION |
| `CODEGRAPH_STATUS` | `index_verified`, `not_verified`, or `not_required` |
| `CODEGRAPH_SYNC` | `yes`, `no`, or `not_required` |
| `FULL_DOCUMENTS_READ` | List of files fully read |
| `TARGETED_DOCUMENTS_READ` | List of files read with targeted sections |
| `SOURCE_SYMBOLS_INSPECTED` | List of symbols inspected via Serena/CodeGraph |
| `EXPECTED_CHANGE` | Brief description of what the task will do |
| `REQUIRED_VALIDATION` | Validation commands from Work Order |
| `DOCUMENTATION_IMPACT` | `yes` or `no`, list of docs affected |
| `COMMIT_AUTHORIZATION` | `yes` if Work Order authorizes commit, `no` |
| `PREFLIGHT_DECISION` | One of the 8 decision values |
| `BLOCK_REASON` | Empty if READY, otherwise the exact blocking condition |

## Verification Semantics

- `SERENA_STATUS: active_verified` requires confirmation that the
  active Serena project equals the canonical Git root. The presence
  of a Serena executable on PATH is never sufficient.
- `CODEGRAPH_STATUS: index_verified` requires confirmation that the
  indexed path equals the canonical Git root and the index is current.
  The presence of an index directory on disk is never sufficient.
- For `TASK_CLASSIFICATION: VAULT_DOCUMENTATION`, all five Serena and
  CodeGraph fields are `not_required` and must not block the task.

## Decision Value Reference

Only these eight values are valid terminal decisions:

| Decision | Meaning |
|---|---|
| `READY` | All preflight checks passed; implementation may begin |
| `BLOCKED_DIRTY_WORKTREE` | Unexpected dirty or untracked files |
| `BLOCKED_PROJECT_MISMATCH` | Serena/CodeGraph project does not match Git root |
| `BLOCKED_SERENA` | Serena cannot be activated or verified |
| `BLOCKED_CODEGRAPH` | CodeGraph cannot be verified |
| `BLOCKED_MISSING_AUTHORITY` | Mandatory authority document is missing |
| `BLOCKED_SCOPE_CONFLICT` | Active Work Order scope is ambiguous |
| `BLOCKED_OWNER_DECISION` | Action requires owner authorization |

Generic status words (for example PASS or SUCCESS) must never be
used as a terminal decision.
