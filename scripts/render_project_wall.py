#!/usr/bin/env python3
"""Deterministic Live Project Wall renderer.

Reads normalized project-state YAML instances and renders a bounded Markdown
section inside 00 Dashboard/Project Dashboard.md between the markers:

    <!-- LIVE_PROJECT_WALL:START -->
    ...
    <!-- LIVE_PROJECT_WALL:END -->

The renderer modifies ONLY the content between the markers. Content outside
the markers is never altered.

Usage:
    # Render the wall from all enabled pilot state files
    python3 scripts/render_project_wall.py

    # Validate a single state file against the schema
    python3 scripts/render_project_wall.py --validate automation/state/thai_stt_app.yaml

    # Validate all enabled state files
    python3 scripts/render_project_wall.py --validate-all

Idempotency: rendering twice against identical normalized state produces no
additional diff.

Created by WO-OBSIDIAN-031 (Live Project Wall Foundation).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

# Resolve paths relative to the repository root (this script lives in scripts/).
REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "automation" / "schema" / "project-state.schema.json"
PROJECTS_YAML = REPO_ROOT / "automation" / "projects.yaml"
STATE_DIR = REPO_ROOT / "automation" / "state"
DASHBOARD_PATH = REPO_ROOT / "00 Dashboard" / "Project Dashboard.md"

START_MARKER = "<!-- LIVE_PROJECT_WALL:START -->"
END_MARKER = "<!-- LIVE_PROJECT_WALL:END -->"

WALL_COLUMNS = [
    "Project",
    "State",
    "Current Work",
    "CI",
    "PR",
    "Last Change",
    "Next Action",
    "Verified At",
]


def load_schema() -> dict:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_projects_registry() -> dict:
    with open(PROJECTS_YAML, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def enabled_project_ids(registry: dict) -> list[str]:
    return [
        p["project_id"]
        for p in registry.get("projects", [])
        if p.get("enabled_for_wall") is True
    ]


def load_state(project_id: str) -> dict:
    state_path = STATE_DIR / f"{project_id}.yaml"
    with open(state_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_state(state: dict, schema: dict) -> list[str]:
    """Return a list of validation error messages (empty if valid)."""
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(state), key=lambda e: list(e.path))
    return [f"{'.'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]


def cell(value) -> str:
    """Render a state value as a Markdown table cell, preserving unknown/null."""
    if value is None:
        return "null"
    if isinstance(value, str) and value == "":
        return "null"
    if isinstance(value, dict):
        # current_work_authority -> path (kind)
        path = value.get("path")
        kind = value.get("kind")
        if path is None and kind is None:
            return "null"
        path_s = path if path is not None else "null"
        kind_s = kind if kind is not None else "null"
        return f"`{path_s}` ({kind_s})"
    text = str(value)
    # Escape pipe characters for Markdown table cells.
    return text.replace("|", "\\|")


def render_wall(states: list[dict]) -> str:
    """Render the bounded wall section content (without markers)."""
    header = "| " + " | ".join(WALL_COLUMNS) + " |"
    separator = "| " + " | ".join("---" for _ in WALL_COLUMNS) + " |"
    lines = [header, separator]
    for s in states:
        row = [
            cell(s.get("project_name")),
            cell(s.get("project_state")),
            cell(s.get("current_work")),
            cell(s.get("ci_state")),
            cell(s.get("open_pr")),
            cell(s.get("last_change")),
            cell(s.get("next_action")),
            cell(s.get("verified_at")),
        ]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def render_into_dashboard(wall_content: str) -> bool:
    """Replace content between markers in the Dashboard. Return True if changed."""
    original = DASHBOARD_PATH.read_text(encoding="utf-8")
    start_idx = original.find(START_MARKER)
    end_idx = original.find(END_MARKER)
    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        raise SystemExit(
            "ERROR: LIVE_PROJECT_WALL markers not found or malformed in "
            f"{DASHBOARD_PATH}. Expected '{START_MARKER}' and '{END_MARKER}'."
        )
    # Rebuild: prefix + start_marker + content + end_marker + suffix.
    prefix = original[: start_idx + len(START_MARKER)]
    suffix = original[end_idx:]
    new_content = f"{prefix}\n{wall_content}\n{suffix}"
    if new_content == original:
        return False
    DASHBOARD_PATH.write_text(new_content, encoding="utf-8")
    return True


def cmd_validate(path: str) -> int:
    schema = load_schema()
    with open(path, "r", encoding="utf-8") as f:
        state = yaml.safe_load(f)
    errors = validate_state(state, schema)
    if errors:
        print(f"INVALID: {path}")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"VALID: {path}")
    return 0


def cmd_validate_all() -> int:
    schema = load_schema()
    registry = load_projects_registry()
    ids = enabled_project_ids(registry)
    if not ids:
        print("No enabled projects to validate.")
        return 1
    rc = 0
    for pid in ids:
        state = load_state(pid)
        errors = validate_state(state, schema)
        if errors:
            print(f"INVALID: {pid}")
            for e in errors:
                print(f"  - {e}")
            rc = 1
        else:
            print(f"VALID: {pid}")
    return rc


def cmd_render() -> int:
    schema = load_schema()
    registry = load_projects_registry()
    ids = enabled_project_ids(registry)
    if not ids:
        print("No enabled projects to render.")
        return 1
    states = []
    for pid in ids:
        state = load_state(pid)
        errors = validate_state(state, schema)
        if errors:
            print(f"INVALID state for {pid}; aborting render:")
            for e in errors:
                print(f"  - {e}")
            return 1
        states.append(state)
    wall_content = render_wall(states)
    changed = render_into_dashboard(wall_content)
    if changed:
        print(f"Rendered Live Project Wall for {len(states)} pilot(s) — Dashboard updated.")
    else:
        print(f"Rendered Live Project Wall for {len(states)} pilot(s) — no change (idempotent).")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 1:
        return cmd_render()
    if argv[1] == "--validate" and len(argv) == 3:
        return cmd_validate(argv[2])
    if argv[1] == "--validate-all":
        return cmd_validate_all()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
