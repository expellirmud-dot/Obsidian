#!/usr/bin/env python3
"""Scheduled state refresh for the Live Project Wall (WO-OBSIDIAN-035).

Orchestrates the full refresh flow and only publishes when ALL local gates
PASS:

    discover/read -> refresh project state -> validate -> render
        -> regression tests -> publish only if all local gates PASS

Gates (publish requires AND of all):
  1. validate-all  : `render_project_wall.py --validate-all` exit 0 (11/11 VALID)
  2. render        : `render_project_wall.py` exit 0
  3. idempotency   : a second render produces zero diff
  4. regression    : `pytest tests/` exit 0

If any gate FAILS the script prints an error and exits non-zero WITHOUT
publishing (no commit, no Dashboard mutation beyond the idempotent render).

The GitHub adapter (automation/github_adapter.py) is read-only and never
mutates source repositories. When GITHUB_TOKEN is absent the adapter sets
ci_state=unknown for every project (fail-safe) and the rest of the flow
still runs.

Publishing is gated behind an explicit `--publish` flag. Without it the
script runs every gate in dry-run mode and reports what it WOULD publish.
This keeps the default invocation safe (no commits) while still exercising
the full pipeline.

Usage:
    python3 automation/refresh_state.py            # dry-run (no publish)
    python3 automation/refresh_state.py --publish  # publish only if all PASS
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Resolve paths relative to the repository root (this file lives in automation/).
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
AUTOMATION_DIR = REPO_ROOT / "automation"
TESTS_DIR = REPO_ROOT / "tests"
STATE_DIR = AUTOMATION_DIR / "state"
RENDERER = SCRIPTS_DIR / "render_project_wall.py"
ADAPTER = AUTOMATION_DIR / "github_adapter.py"
DASHBOARD = REPO_ROOT / "00 Dashboard" / "Project Dashboard.md"


def snapshot_state() -> dict[Path, bytes]:
    """Capture the current bytes of every state YAML file + the Dashboard.

    The refresh flow mutates state files (the adapter updates ci_state/open_pr/
    observed_at) and the Dashboard (the renderer writes between markers). To
    honor 'publish only if all gates PASS', those mutations are discarded
    unless we actually publish. This snapshot lets us restore the working
    tree (state + Dashboard) when dry-running or when a gate fails.
    """
    snapshot: dict[Path, bytes] = {
        p: p.read_bytes() for p in STATE_DIR.glob("*.yaml") if p.is_file()
    }
    if DASHBOARD.exists():
        snapshot[DASHBOARD] = DASHBOARD.read_bytes()
    return snapshot


def restore_state(snapshot: dict[Path, bytes]) -> None:
    """Restore every state YAML file and the Dashboard to snapshot bytes."""
    for path, data in snapshot.items():
        if path.read_bytes() != data:
            path.write_bytes(data)


def run(cmd: list[str], label: str) -> subprocess.CompletedProcess:
    """Run a command, streaming output, returning the CompletedProcess."""
    print(f"\n=== GATE: {label} ===")
    print("$ " + " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return proc


def gate_validate_all() -> tuple[bool, str]:
    """Gate 1: validate-all must exit 0 (11/11 VALID)."""
    proc = run(
        [sys.executable, str(RENDERER), "--validate-all"],
        "validate-all (schema validation for all enabled states)",
    )
    ok = proc.returncode == 0
    return ok, f"exit code {proc.returncode}"


def gate_render() -> tuple[bool, str]:
    """Gate 2: render must exit 0."""
    proc = run(
        [sys.executable, str(RENDERER)],
        "render (Live Project Wall)",
    )
    ok = proc.returncode == 0
    return ok, f"exit code {proc.returncode}"


def gate_idempotency() -> tuple[bool, str]:
    """Gate 3: a second render must produce zero diff (idempotent).

    Captures the Dashboard hash before and after a second render invocation.
    """
    import hashlib

    if not DASHBOARD.exists():
        return False, "Dashboard file not found"
    before = hashlib.sha256(DASHBOARD.read_bytes()).hexdigest()
    proc = run([sys.executable, str(RENDERER)], "render (idempotency re-render)")
    if proc.returncode != 0:
        return False, f"second render exit code {proc.returncode}"
    after = hashlib.sha256(DASHBOARD.read_bytes()).hexdigest()
    ok = before == after
    return ok, "zero diff" if ok else "Dashboard changed on re-render (not idempotent)"


def gate_regression() -> tuple[bool, str]:
    """Gate 4: pytest tests/ must exit 0."""
    proc = run(
        [sys.executable, "-m", "pytest", str(TESTS_DIR), "-v"],
        "regression tests (pytest tests/)",
    )
    ok = proc.returncode == 0
    return ok, f"exit code {proc.returncode}"


def refresh_project_state() -> tuple[bool, str]:
    """Run the read-only GitHub adapter to refresh state.

    This is NOT a publish gate by itself -- it refreshes ci_state/open_pr/
    observed_at in the state YAML files. When no token is present the adapter
    sets ci_state=unknown for every project (fail-safe) and exits 0 as long as
    schema validation passes. A non-zero exit here aborts before the gates.
    """
    proc = run(
        [sys.executable, str(ADAPTER)],
        "refresh project state (read-only GitHub adapter)",
    )
    ok = proc.returncode == 0
    return ok, f"exit code {proc.returncode}"


def publish() -> bool:
    """Publish the refreshed state + Dashboard.

    In this implementation publishing means staging the state directory and
    the Dashboard and committing them with git. The script never pushes
    (push requires separate Owner authorization per the WO commit policy).

    Returns True if a commit was created, False if there was nothing to commit.
    """
    print("\n=== PUBLISH ===")
    # Stage state YAMLs and the Dashboard only (no source repos, no secrets).
    stage_cmd = ["git", "add", "automation/state/", "00 Dashboard/Project Dashboard.md"]
    subprocess.run(stage_cmd, cwd=str(REPO_ROOT))
    # Only commit if there is something staged.
    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(REPO_ROOT),
    )
    if diff.returncode == 0:
        print("Nothing to publish (no staged changes).")
        return False
    msg = (
        "chore: WO-OBSIDIAN-035 automated state refresh "
        "(validate + render + idempotency + pytest PASS)"
    )
    subprocess.run(["git", "commit", "-m", msg], cwd=str(REPO_ROOT))
    print("Published: committed refreshed state + Dashboard (not pushed).")
    return True


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Scheduled state refresh (WO-035)")
    parser.add_argument(
        "--publish",
        action="store_true",
        help="publish (commit state + Dashboard) only if all gates PASS; "
        "without this flag the script runs in dry-run mode",
    )
    args = parser.parse_args(argv[1:])

    print("WO-OBSIDIAN-035 -- Automated Refresh & Regression Safety")
    print("=" * 70)
    print(f"repo root: {REPO_ROOT}")
    print(f"mode: {'PUBLISH' if args.publish else 'DRY-RUN (no commit)'}")

    # Snapshot state files so we can discard adapter mutations unless we
    # actually publish (publish only if all gates PASS).
    state_snapshot = snapshot_state()

    # Flow: discover/read -> refresh -> validate -> render -> tests -> publish
    # discover/read is implicit in the adapter/renderer (they read projects.yaml).

    # refresh project state (read-only adapter). Failure here aborts early.
    refresh_ok, refresh_msg = refresh_project_state()
    if not refresh_ok:
        print(f"\n[FAIL] refresh project state: {refresh_msg}")
        print("Aborting before gates: adapter returned non-zero. NOT publishing.")
        restore_state(state_snapshot)
        return 2

    gates: list[tuple[str, bool, str]] = []

    g1_ok, g1_msg = gate_validate_all()
    gates.append(("validate-all", g1_ok, g1_msg))

    g2_ok, g2_msg = gate_render()
    gates.append(("render", g2_ok, g2_msg))

    g3_ok, g3_msg = gate_idempotency()
    gates.append(("idempotency", g3_ok, g3_msg))

    g4_ok, g4_msg = gate_regression()
    gates.append(("regression-tests", g4_ok, g4_msg))

    print("\n" + "=" * 70)
    print("GATE SUMMARY")
    print("-" * 70)
    all_pass = True
    for name, ok, msg in gates:
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_pass = False
        print(f"  {name:<20} {status:<6} ({msg})")
    print("-" * 70)

    if not all_pass:
        print("\n[FAIL] One or more gates FAILED. NOT publishing (state preserved).")
        restore_state(state_snapshot)
        return 1

    print("\n[PASS] All gates PASS.")
    if args.publish:
        publish()
        print("\nRefresh complete: published (committed, not pushed).")
    else:
        # Dry-run: discard the adapter's state mutations so the working tree
        # stays clean (publish only happens with --publish).
        restore_state(state_snapshot)
        print(
            "\nRefresh complete: dry-run (no --publish). State mutations discarded; "
            "re-run with --publish to commit state + Dashboard."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
