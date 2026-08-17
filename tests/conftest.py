"""Shared pytest fixtures for the WO-OBSIDIAN-035 regression suite.

Fixtures here load the real registry/schema once and provide sample GitHub
API response payloads (dicts) for adapter tests. No real HTTP calls are made
and no real state YAML files are mutated.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

# Make the repo root importable so tests can import the renderer/adapter
# modules directly (they live in scripts/ and automation/).
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# The renderer lives in scripts/ and the adapter in automation/. Add their
# parent directories to sys.path so they import as top-level modules.
SCRIPTS_DIR = REPO_ROOT / "scripts"
AUTOMATION_DIR = REPO_ROOT / "automation"
for _d in (SCRIPTS_DIR, AUTOMATION_DIR):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def schema_path(repo_root) -> Path:
    return repo_root / "automation" / "schema" / "project-state.schema.json"


@pytest.fixture(scope="session")
def schema(schema_path) -> dict:
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def projects_yaml_path(repo_root) -> Path:
    return repo_root / "automation" / "projects.yaml"


@pytest.fixture(scope="session")
def registry(projects_yaml_path) -> dict:
    with open(projects_yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def state_dir(repo_root) -> Path:
    return repo_root / "automation" / "state"


@pytest.fixture(scope="session")
def dashboard_path(repo_root) -> Path:
    return repo_root / "00 Dashboard" / "Project Dashboard.md"


@pytest.fixture(scope="session")
def renderer_module():
    import render_project_wall as rpw  # noqa: WPS433
    return rpw


@pytest.fixture(scope="session")
def adapter_module():
    import github_adapter as gha  # noqa: WPS433
    return gha


@pytest.fixture
def sample_repo_api_response() -> dict:
    """Sample GET /repos/{owner}/{repo} response (dict fixture, no HTTP)."""
    return {
        "id": 123456789,
        "name": "thai_stt_app",
        "full_name": "expellirmud-dot/thai_stt_app",
        "default_branch": "main",
        "html_url": "https://github.com/expellirmud-dot/thai_stt_app",
        "private": False,
    }


@pytest.fixture
def sample_commit_api_response() -> dict:
    """Sample GET /repos/{owner}/{repo}/commits/{branch} response."""
    return {
        "sha": "be7bd07760cc6c426927a2aec9e0cbce8c2ddf60",
        "commit": {
            "committer": {
                "name": "Toto",
                "email": "toto@example.com",
                "date": "2026-08-09T10:11:12Z",
            },
        },
    }


@pytest.fixture
def sample_prs_api_response() -> list:
    """Sample GET /repos/{owner}/{repo}/pulls?state=open response (list)."""
    return [
        {"number": 42, "title": "Fix audio pipeline", "state": "open"},
        {"number": 43, "title": "Add tests", "state": "open"},
    ]


@pytest.fixture
def sample_status_api_response() -> dict:
    """Sample GET /repos/{owner}/{repo}/commits/{sha}/status response."""
    return {
        "state": "success",
        "statuses": [
            {"state": "success", "context": "ci/audio"},
        ],
        "sha": "be7bd07760cc6c426927a2aec9e0cbce8c2ddf60",
    }


@pytest.fixture
def sample_check_runs_api_response() -> dict:
    """Sample GET /repos/{owner}/{repo}/commits/{sha}/check-runs response."""
    return {
        "total_count": 2,
        "check_runs": [
            {"name": "build", "status": "completed", "conclusion": "success"},
            {"name": "lint", "status": "completed", "conclusion": "success"},
        ],
    }


@pytest.fixture
def valid_state_dict() -> dict:
    """A minimal-but-complete state instance that satisfies the schema."""
    return {
        "project_id": "thai_stt_app",
        "project_name": "Thai STT App",
        "source_path": "D:\\thai_stt_app",
        "repository": "https://github.com/expellirmud-dot/thai_stt_app.git",
        "branch": "main",
        "head": "be7bd07760cc6c426927a2aec9e0cbce8c2ddf60",
        "project_state": "active",
        "current_goal": "WO-Skill-Audit",
        "current_work": "audit and install skills",
        "current_work_authority": {"path": "work-order/WO-Skill-Audit/work-order.md", "kind": "work-order"},
        "current_work_evidence": "verified",
        "ci_state": "unknown",
        "open_pr": None,
        "last_change": "2026-08-09",
        "next_action": "Complete WO-Skill-Audit",
        "blockers": None,
        "evidence_classification": "verified",
        "verified_at": "2026-08-12T04:33:00Z",
        "adapter_id": "generic-git-plus-authority-files",
    }
