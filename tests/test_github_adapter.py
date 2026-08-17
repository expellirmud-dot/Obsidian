"""WO-OBSIDIAN-035 regression suite for the GitHub adapter.

Covers automation/github_adapter.py. Two test cases:

  10. test_github_response_parsing
  11. test_api_unavailable_returns_unknown

No real GitHub API calls are made; tests use dict fixtures from conftest.py
and monkeypatch the adapter's github_request function.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# 10. GitHub response parsing
# ---------------------------------------------------------------------------

def test_github_response_parsing(
    adapter_module,
    sample_repo_api_response,
    sample_commit_api_response,
    sample_prs_api_response,
    sample_status_api_response,
    sample_check_runs_api_response,
    monkeypatch,
):
    """The adapter correctly parses sample GitHub API responses (no real HTTP)."""
    calls: list[str] = []

    def fake_github_request(path, token):
        calls.append(path)
        if path.startswith("/repos/") and path.endswith("/commits/be7bd07760cc6c426927a2aec9e0cbce8c2ddf60/status"):
            return 200, sample_status_api_response, {}
        if "/check-runs" in path:
            return 200, sample_check_runs_api_response, {}
        if path.endswith("/pulls?state=open&per_page=100"):
            return 200, sample_prs_api_response, {}
        if "/commits/main" in path:
            return 200, sample_commit_api_response, {}
        # /repos/{owner}/{repo}
        return 200, sample_repo_api_response, {}

    monkeypatch.setattr(adapter_module, "github_request", fake_github_request)

    owner, repo = "expellirmud-dot", "thai_stt_app"

    head = adapter_module.fetch_repo_head(owner, repo, token="fake-token")
    assert head["head_sha"] == "be7bd07760cc6c426927a2aec9e0cbce8c2ddf60"
    assert head["last_change"] == "2026-08-09"
    assert head["default_branch"] == "main"

    prs = adapter_module.fetch_open_prs(owner, repo, token="fake-token")
    assert prs["open_pr_count"] == 2
    assert prs["open_pr"] == 42  # first PR number

    ci = adapter_module.fetch_ci_state(
        owner, repo, head["head_sha"], token="fake-token"
    )
    assert ci["ci_state"] == "success", f"expected success, got {ci}"

    # parse_owner_repo must extract (owner, repo) from a real-style URL.
    assert adapter_module.parse_owner_repo(
        "https://github.com/expellirmud-dot/thai_stt_app.git"
    ) == ("expellirmud-dot", "thai_stt_app")
    assert adapter_module.parse_owner_repo("") is None
    assert adapter_module.parse_owner_repo("not-a-url") is None


# ---------------------------------------------------------------------------
# 11. API unavailable -> ci_state=unknown (not failure)
# ---------------------------------------------------------------------------

def test_api_unavailable_returns_unknown(adapter_module, monkeypatch):
    """When the API/token is unavailable, ci_state=unknown (never failure)."""
    # Simulate total network failure (github_request returns -1).
    def fake_github_request(path, token):
        return -1, None, {"_error": "simulated network failure"}

    monkeypatch.setattr(adapter_module, "github_request", fake_github_request)

    head = adapter_module.fetch_repo_head("owner", "repo", token=None)
    assert head.get("error") == "github_api_unavailable"

    # With no head_sha, ci_state must be unknown (fail-safe), never failure.
    ci = adapter_module.fetch_ci_state("owner", "repo", "", token=None)
    assert ci["ci_state"] == "unknown", (
        f"API unavailable must yield unknown, got {ci}"
    )

    # Even with a head_sha but all endpoints unavailable -> unknown.
    ci2 = adapter_module.fetch_ci_state(
        "owner", "repo", "some-sha", token=None
    )
    assert ci2["ci_state"] == "unknown", f"got {ci2}"

    # Rate-limited (403 with remaining=0) must also be unknown, not failure.
    def fake_rate_limited(path, token):
        return 403, None, {"X-RateLimit-Remaining": "0"}

    monkeypatch.setattr(adapter_module, "github_request", fake_rate_limited)
    head_rl = adapter_module.fetch_repo_head("owner", "repo", token="t")
    assert head_rl.get("error") == "rate_limited"
    ci_rl = adapter_module.fetch_ci_state("owner", "repo", "sha", token="t")
    assert ci_rl["ci_state"] == "unknown"
