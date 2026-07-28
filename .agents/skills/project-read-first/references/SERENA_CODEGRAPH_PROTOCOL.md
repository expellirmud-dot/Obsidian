# Serena and CodeGraph Protocol — Vault Edition

This reference document defines the exact protocol for activating,
verifying, and using Serena and CodeGraph during the project-read-first
preflight.

## When This Protocol Applies

| Task Classification | Serena / CodeGraph |
|---|---|
| `VAULT_DOCUMENTATION` | `not_required` — must not block the task |
| `SOURCE_REPOSITORY` | Mandatory — exact-root verification required |

Markdown, Dashboard, Index, Template, Project Overview, and Resume
Context work inside the Vault is `VAULT_DOCUMENTATION`. Tasks that
read, analyze, or modify source code are `SOURCE_REPOSITORY`.

For `SOURCE_REPOSITORY` tasks, resolve the exact Git root of the
actual source repository. The Vault root must never substitute for a
source repository root.

## Serena Protocol

### Activation

The canonical project root must be resolved first using `git rev-parse
--show-toplevel`. Serena is then activated using that exact path:

```python
mcp__serena__activate_project(
    project="<canonical-git-root>"
)
```

### Verification

After activation, verify Serena reports the correct project:

```python
config = mcp__serena__get_current_config()
# assert active project == canonical_git_root
```

### Rules

1. The project path used with `activate_project` must equal the canonical
   Git root. Do not use a parent, sibling, historical, or previously
   active project.
2. If `activate_project` fails or reports a mismatched project, stop with
   `BLOCKED_PROJECT_MISMATCH`.
3. If Serena is not installed or cannot be verified, stop with
   `BLOCKED_SERENA`.
4. Finding a Serena executable on PATH is not verification. Only a
   confirmed active project equal to the canonical Git root counts.
5. Symbol extraction via Serena only applies to code files in active
   languages. Markdown docs (README, AGENTS.md, Work Orders) must be
   read with `read_file` directly — do not route them through Serena
   symbol tools.
6. Serena memory is supplementary context only. Do not treat it as
   authority over Git files.

### Common Failure Modes

| Symptom | Cause | Resolution |
|---|---|---|
| Serena returns no symbols for a file | File not in active languages | Use `read_file` directly for docs |
| `activate_project` fails with unknown project | Project not registered | Check global `serena_config.yml` or use path directly |
| Tool calls timeout | Serena process not responding | Restart Serena MCP connection |

## CodeGraph Protocol

### Verification

1. Confirm the indexed repository path equals the canonical Git root.
2. Confirm the index exists and is recent (compared to file
   modification times).
3. If the index is stale (files modified after last index run),
   synchronize:
   ```bash
   codegraph init --path <canonical-git-root>
   ```
4. Use CodeGraph for dependency queries, caller/callee analysis, and
   architecture impact assessments.

### Rules

1. The indexed path must equal the canonical Git root. Do not index a
   parent directory that encompasses unrelated repositories.
2. The existence of an index directory on disk is not verification.
   Only a confirmed indexed path equal to the canonical Git root counts.
3. Cross-check material CodeGraph results against repository source
   truth. CodeGraph provides hints, not proof.
4. If CodeGraph cannot be verified for the exact root, the terminal
   preflight decision must be `BLOCKED_CODEGRAPH`.

### Common Failure Modes

| Symptom | Cause | Resolution |
|---|---|---|
| CodeGraph returns [] for a file | Index missing or stale | Re-run `codegraph init` |
| Symbol not found | File not in indexed languages or symbol name wrong | Verify file extension and symbol name |
| Index corruption | Partial index from interrupted run | Delete `.codegraph/` and re-index |

## Combined Protocol

For `SOURCE_REPOSITORY` tasks, both Serena and CodeGraph must be
verified before implementation begins. The preflight produces one
terminal decision:

- `READY` — both verified, mandatory documents read
- `BLOCKED_SERENA` — Serena failed verification
- `BLOCKED_CODEGRAPH` — CodeGraph failed verification
- `BLOCKED_PROJECT_MISMATCH` — either tool shows a wrong project root

For `VAULT_DOCUMENTATION` tasks, both tools are `not_required` and the
decision is computed from repository state and authority documents
only.

Do not proceed to implementation if a required verification blocks.

## Authority Rule

Conversation, AI memory, Worker reports, Serena memory, and
CodeGraph results are supplementary context and never override
repository files.
