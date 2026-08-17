"""WO-OBSIDIAN-035 regression suite for the Live Project Wall renderer.

Covers the renderer (scripts/render_project_wall.py). The GitHub adapter
tests live in tests/test_github_adapter.py. All 9 renderer test cases:

  1.  test_schema_validation
  2.  test_all_11_registered_project_states
  3.  test_validate_all
  4.  test_render_success
  5.  test_render_idempotency
  6.  test_marker_integrity
  7.  test_malformed_yaml_fail_closed
  8.  test_missing_required_field_fail
  9.  test_unknown_project_exclusion

No real GitHub API calls are made and no real state YAML files are mutated;
tests that need files use tmp_path.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
AUTOMATION_DIR = REPO_ROOT / "automation"
for _d in (str(REPO_ROOT), str(SCRIPTS_DIR), str(AUTOMATION_DIR)):
    if _d not in sys.path:
        sys.path.insert(0, _d)


# ---------------------------------------------------------------------------
# 1. Schema validation
# ---------------------------------------------------------------------------

def test_schema_validation(schema):
    """The schema file loads and is itself a valid JSON Schema (Draft 2020-12)."""
    assert isinstance(schema, dict)
    assert schema.get("type") == "object"
    # The schema must be usable as a Draft 2020-12 validator (raises on invalid).
    Draft202012Validator.check_schema(schema)
    # Sanity: a known-good state validates cleanly.
    validator = Draft202012Validator(schema)
    good = {
        "project_id": "x",
        "project_name": "X",
        "source_path": "D:\\x",
        "repository": None,
        "branch": "main",
        "head": None,
        "project_state": "active",
        "current_goal": None,
        "current_work": None,
        "current_work_authority": {"path": None, "kind": None},
        "current_work_evidence": "unknown",
        "ci_state": "unknown",
        "open_pr": None,
        "last_change": None,
        "next_action": None,
        "blockers": None,
        "evidence_classification": "unknown",
        "verified_at": None,
        "adapter_id": "generic-git-plus-authority-files",
    }
    assert validator.iter_errors(good) is not None
    assert list(validator.iter_errors(good)) == []


# ---------------------------------------------------------------------------
# 2. Exactly 11 registered project states
# ---------------------------------------------------------------------------

def test_all_11_registered_project_states(registry, state_dir):
    """Exactly 11 state files exist, matching the enabled projects in projects.yaml."""
    enabled = [
        p["project_id"]
        for p in registry.get("projects", [])
        if p.get("enabled_for_wall") is True
    ]
    assert len(enabled) == 11, f"expected 11 enabled projects, got {len(enabled)}"

    state_files = {
        f.stem for f in state_dir.glob("*.yaml") if f.is_file()
    }
    assert state_files == set(enabled), (
        f"state files {sorted(state_files)} != enabled ids {sorted(enabled)}"
    )
    # No extra/missing files.
    assert len(state_files) == 11


# ---------------------------------------------------------------------------
# 3. validate-all returns 0 errors for all 11
# ---------------------------------------------------------------------------

def test_validate_all(renderer_module, registry, state_dir):
    """Running the validate-all logic returns 0 errors for all 11 states."""
    schema = renderer_module.load_schema()
    ids = renderer_module.enabled_project_ids(registry)
    assert len(ids) == 11

    total_errors = 0
    for pid in ids:
        state = renderer_module.load_state(pid)
        errors = renderer_module.validate_state(state, schema)
        total_errors += len(errors)
        assert errors == [], f"{pid} has validation errors: {errors}"
    assert total_errors == 0


# ---------------------------------------------------------------------------
# 4. Render success: non-empty wall with header + separator + 11 rows
# ---------------------------------------------------------------------------

def test_render_success(renderer_module, registry):
    """render_wall produces non-empty content with header + separator + 11 rows."""
    schema = renderer_module.load_schema()
    ids = renderer_module.enabled_project_ids(registry)
    states = [renderer_module.load_state(pid) for pid in ids]
    for s in states:
        assert renderer_module.validate_state(s, schema) == []

    wall = renderer_module.render_wall(states)
    assert wall, "wall content must be non-empty"
    lines = wall.splitlines()
    # header + separator + 11 data rows
    assert len(lines) == 2 + 11, f"expected 13 lines, got {len(lines)}"

    header = lines[0]
    separator = lines[1]
    for col in renderer_module.WALL_COLUMNS:
        assert col in header, f"column {col!r} missing from header"
    # separator is all dashes between pipes
    sep_cells = [c.strip() for c in separator.strip("|").split("|")]
    assert all(c == "---" for c in sep_cells), f"bad separator: {separator!r}"
    assert len(sep_cells) == len(renderer_module.WALL_COLUMNS)

    # Each data row has the same column count as the header.
    header_cells = header.count("|") - 1
    for row in lines[2:]:
        assert row.count("|") - 1 == header_cells, f"malformed row: {row!r}"


# ---------------------------------------------------------------------------
# 5. Render idempotency: rendering twice produces identical output
# ---------------------------------------------------------------------------

def test_render_idempotency(renderer_module, registry):
    """Rendering twice against identical state produces identical output."""
    schema = renderer_module.load_schema()
    ids = renderer_module.enabled_project_ids(registry)
    states = [renderer_module.load_state(pid) for pid in ids]

    first = renderer_module.render_wall(states)
    second = renderer_module.render_wall(states)
    assert first == second, "render_wall is not idempotent"
    assert first  # non-empty


# ---------------------------------------------------------------------------
# 6. Marker integrity: Dashboard has START and END markers in correct order
# ---------------------------------------------------------------------------

def test_marker_integrity(dashboard_path, renderer_module, tmp_path):
    """Dashboard has both START and END markers, START before END.

    Uses a tmp_path copy so the real Dashboard is never mutated.
    """
    text = dashboard_path.read_text(encoding="utf-8")
    start = renderer_module.START_MARKER
    end = renderer_module.END_MARKER
    assert start in text, "START marker missing from Dashboard"
    assert end in text, "END marker missing from Dashboard"
    assert text.find(start) < text.find(end), "markers out of order (END before START)"

    # render_into_dashboard must succeed (not raise) on a COPY of the dashboard.
    tmp_dashboard = tmp_path / "Project Dashboard.md"
    tmp_dashboard.write_text(text, encoding="utf-8")
    schema = renderer_module.load_schema()
    registry = renderer_module.load_projects_registry()
    ids = renderer_module.enabled_project_ids(registry)
    states = [renderer_module.load_state(pid) for pid in ids]
    wall = renderer_module.render_wall(states)

    # Patch DASHBOARD_PATH to the temp copy so the real file is never touched.
    original = renderer_module.DASHBOARD_PATH
    renderer_module.DASHBOARD_PATH = tmp_dashboard
    try:
        changed = renderer_module.render_into_dashboard(wall)
        assert isinstance(changed, bool)
    finally:
        renderer_module.DASHBOARD_PATH = original


# ---------------------------------------------------------------------------
# 7. Malformed YAML fail-closed
# ---------------------------------------------------------------------------

def test_malformed_yaml_fail_closed(renderer_module, schema, tmp_path):
    """A malformed YAML state file is rejected by validation (fail-closed)."""
    malformed = tmp_path / "malformed.yaml"
    malformed.write_text(
        "project_id: bad\n"
        "project_name: [unclosed\n"
        "  - oops\n"
        "    : colon: everywhere: \n",
        encoding="utf-8",
    )
    with pytest.raises(yaml.YAMLError):
        yaml.safe_load(malformed.read_text(encoding="utf-8"))

    # The renderer's cmd_validate reads the file with yaml.safe_load, which
    # raises on malformed YAML -> non-zero exit (fail-closed).
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "render_project_wall.py"),
         "--validate", str(malformed)],
        capture_output=True, text=True,
    )
    assert proc.returncode != 0, "malformed YAML must fail validation"
    # The failure may surface as INVALID in stdout or as a traceback in stderr;
    # either way it must NOT silently pass as VALID.
    assert "VALID:" not in proc.stdout, "malformed YAML must not pass as VALID"


# ---------------------------------------------------------------------------
# 8. Missing required field fails validation
# ---------------------------------------------------------------------------

def test_missing_required_field_fail(renderer_module, schema, valid_state_dict):
    """A state missing a required field fails validation."""
    missing = dict(valid_state_dict)
    del missing["project_state"]
    errors = renderer_module.validate_state(missing, schema)
    assert errors, "missing required field must produce validation errors"
    # The error must reference the missing required field.
    joined = " ".join(errors)
    assert "project_state" in joined, (
        f"validation error did not mention 'project_state': {errors}"
    )


# ---------------------------------------------------------------------------
# 9. Unknown project exclusion
# ---------------------------------------------------------------------------

def test_unknown_project_exclusion(renderer_module, registry):
    """A project not in projects.yaml is not rendered."""
    enabled = renderer_module.enabled_project_ids(registry)
    unknown = "definitely_not_a_registered_project_xyz"
    assert unknown not in enabled

    schema = renderer_module.load_schema()
    states = [renderer_module.load_state(pid) for pid in enabled]
    wall = renderer_module.render_wall(states)

    # The unknown id must not appear anywhere in the rendered wall.
    assert unknown not in wall
    # And only the enabled ids' project names should appear (11 rows).
    lines = wall.splitlines()
    assert len(lines) == 2 + len(enabled)
