#!/usr/bin/env python3
"""Deterministic progress + next-action engine (WO-OBSIDIAN-039).

Computes progress from EVIDENCE only -- never from LLM impression. Priority:
  1. explicit weighted roadmap milestones
  2. explicit phases/goals with completion status
  3. bounded work-order set belonging to the current goal
  4. insufficient denominator -> UNKNOWN

Derives the next authoritative action from:
  1. explicit Current WO/Task
  2. roadmap dependency
  3. open blocker resolution
  4. next planned milestone
If no evidence -> next_action: unknown (never invented).

The engine reads the evidence manifest (WO-038) and the v2 state, and writes
the computed `progress` block + `current_execution.next_action` back into the
state file. It is deterministic: identical inputs produce identical outputs.

Safety:
  * READ-ONLY w.r.t. source repositories (it only reads Vault files).
  * Never fabricates a percentage. Missing denominator -> estimate=null,
    confidence=unknown.
  * The basis string explains exactly how the numbers were derived.

Usage:
    python3 automation/progress_engine.py compute --project thai_stt_app
    python3 automation/progress_engine.py compute --all
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_YAML = REPO_ROOT / "automation" / "projects.yaml"
STATE_DIR = REPO_ROOT / "automation" / "state"
EVIDENCE_DIR = REPO_ROOT / "automation" / "evidence"
SCHEMA_PATH = REPO_ROOT / "automation" / "schema" / "project-state.v2.schema.json"


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_schema() -> dict:
    import json
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Roadmap / milestone parsing from evidence content
# ---------------------------------------------------------------------------

# Match milestone/phase lines like:
#   - [x] M1: Foundation          (completed, weight 1)
#   - [ ] M2: Live test           (not completed, weight 1)
#   - [x] (2) Phase A             (completed, weight 2)
#   ## Phase 1 — Foundation (DONE)
MILESTONE_RE = re.compile(
    r"^\s*[-*]?\s*\[(?P<done>[xX ])\]\s*(?:\((?P<weight>\d+)\)\s*)?(?P<name>.+)$"
)


def parse_milestones_from_content(content: str) -> list[dict]:
    """Parse weighted milestone lines from markdown content.

    Returns a list of {name, done (bool), weight (int)}.
    """
    milestones: list[dict] = []
    for line in content.splitlines():
        m = MILESTONE_RE.match(line)
        if not m:
            continue
        done = m.group("done").strip().lower() == "x"
        weight = int(m.group("weight")) if m.group("weight") else 1
        name = m.group("name").strip().strip("*_`").strip()
        if not name:
            continue
        milestones.append({"name": name, "done": done, "weight": weight})
    return milestones


def collect_roadmap_evidence(manifest: dict) -> list[dict]:
    """Return roadmap-category evidence items (with content_excerpt)."""
    return [e for e in manifest.get("evidence", []) if e.get("category") == "roadmap"]


def collect_completed_evidence(manifest: dict) -> list[dict]:
    return [e for e in manifest.get("evidence", []) if e.get("category") == "completed_work"]


# ---------------------------------------------------------------------------
# Progress computation (deterministic)
# ---------------------------------------------------------------------------

def compute_weighted_progress(milestones: list[dict]) -> dict | None:
    """Method 1: weighted milestones. Returns a progress block or None.

    estimate = round(100 * sum(weight_i for done) / sum(all weights))
    range = estimate +/- 0 (deterministic when weights explicit); we widen to
    +/- 5 at medium confidence to reflect that milestone granularity is coarse.
    """
    if not milestones:
        return None
    total_weight = sum(m["weight"] for m in milestones)
    if total_weight <= 0:
        return None
    done_weight = sum(m["weight"] for m in milestones if m["done"])
    estimate = round(100 * done_weight / total_weight)
    completed = sum(1 for m in milestones if m["done"])
    remaining = sum(1 for m in milestones if not m["done"])
    active = 0  # milestone-level: no "active" concept unless marked
    return {
        "scope": "current_roadmap",
        "method": "weighted_milestones",
        "estimate": estimate,
        "range_min": max(0, estimate - 5),
        "range_max": min(100, estimate + 5),
        "confidence": "medium",
        "completed": completed,
        "active": active,
        "remaining": remaining,
        "basis": (
            f"weighted milestones: {done_weight}/{total_weight} weight units "
            f"completed ({completed}/{len(milestones)} milestones)"
        ),
    }


def compute_bounded_milestones(milestones: list[dict]) -> dict | None:
    """Method 2: unweighted bounded milestones (equal weight)."""
    if not milestones:
        return None
    n = len(milestones)
    done = sum(1 for m in milestones if m["done"])
    estimate = round(100 * done / n)
    return {
        "scope": "current_roadmap",
        "method": "bounded_milestones",
        "estimate": estimate,
        "range_min": max(0, estimate - 5),
        "range_max": min(100, estimate + 5),
        "confidence": "medium",
        "completed": done,
        "active": 0,
        "remaining": n - done,
        "basis": f"bounded milestones: {done}/{n} milestones completed (equal weight)",
    }


def compute_unknown_progress(reason: str = "no denominator (roadmap/milestone evidence not found)") -> dict:
    """Method 4: insufficient denominator -> UNKNOWN."""
    return {
        "scope": None,
        "method": None,
        "estimate": None,
        "range_min": None,
        "range_max": None,
        "confidence": "unknown",
        "completed": None,
        "active": None,
        "remaining": None,
        "basis": reason,
    }


def compute_progress(manifest: dict, state: dict) -> dict:
    """Compute the progress block deterministically from evidence + state.

    Priority:
      1. weighted roadmap milestones (explicit weights)
      2. bounded milestones (equal weight)
      3. (work-order set: not enough structure in evidence to bound reliably)
      4. UNKNOWN
    """
    roadmap_ev = collect_roadmap_evidence(manifest)
    all_milestones: list[dict] = []
    has_explicit_weights = False
    for ev in roadmap_ev:
        ms = parse_milestones_from_content(ev.get("content_excerpt", ""))
        if ms:
            if any(m["weight"] != 1 for m in ms):
                has_explicit_weights = True
            all_milestones.extend(ms)

    if all_milestones and has_explicit_weights:
        return compute_weighted_progress(all_milestones)
    if all_milestones:
        return compute_bounded_milestones(all_milestones)
    return compute_unknown_progress()


# ---------------------------------------------------------------------------
# Next-action derivation (from explicit authority only)
# ---------------------------------------------------------------------------

def derive_next_action(manifest: dict, state: dict) -> str | None:
    """Derive the next authoritative action. Never invents.

    Priority:
      1. explicit existing next_action (from current_execution, verified authority)
      2. open blocker resolution
      3. first incomplete roadmap milestone
    If no evidence -> None (unknown).
    """
    execution = state.get("current_execution") or {}

    # 1. If there is an explicit current work + a stated next_action already
    #    verified, keep it (it came from authority).
    existing_next = execution.get("next_action")
    if existing_next and existing_next.strip().lower() not in ("unknown", "null", ""):
        return existing_next

    # 2. Open blocker resolution.
    blockers = execution.get("blockers")
    if blockers and blockers.strip().lower() not in ("unknown", "null", ""):
        return f"Resolve blocker: {blockers}"

    # 3. Roadmap dependency: first incomplete milestone.
    roadmap_ev = collect_roadmap_evidence(manifest)
    for ev in roadmap_ev:
        ms = parse_milestones_from_content(ev.get("content_excerpt", ""))
        for m in ms:
            if not m["done"]:
                src = ev.get("path") or "roadmap"
                return f"Next milestone: {m['name']} (from {src})"

    # No evidence -> unknown (never invent).
    return None


# ---------------------------------------------------------------------------
# Apply to state
# ---------------------------------------------------------------------------

def apply_progress_to_state(project_id: str, manifest: dict | None, dry_run: bool = False) -> dict:
    """Compute progress + next_action and write into the v2 state file."""
    state_path = STATE_DIR / f"{project_id}.yaml"
    if not state_path.exists():
        return {"project_id": project_id, "applied": False, "reason": "state_not_found"}
    original_text = state_path.read_text(encoding="utf-8")
    state = yaml.safe_load(original_text)
    if not isinstance(state, dict):
        return {"project_id": project_id, "applied": False, "reason": "state_not_dict"}

    if manifest is None:
        manifest = {"evidence": []}

    progress = compute_progress(manifest, state)
    next_action = derive_next_action(manifest, state)

    state["progress"] = progress
    execution = state.get("current_execution") or {}
    execution["next_action"] = next_action
    state["current_execution"] = execution

    # Validate before writing.
    import json
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(state))
    if errors:
        return {
            "project_id": project_id,
            "applied": False,
            "reason": "schema_invalid",
            "errors": [e.message for e in errors],
        }

    if dry_run:
        return {
            "project_id": project_id,
            "applied": True,
            "dry_run": True,
            "estimate": progress["estimate"],
            "method": progress["method"],
            "confidence": progress["confidence"],
            "next_action": next_action,
        }

    header_lines = [ln for ln in original_text.splitlines() if ln.startswith("#") or ln.strip() == ""]
    while header_lines and header_lines[-1].strip() == "":
        header_lines.pop()
    body = yaml.safe_dump(state, sort_keys=False, default_flow_style=False, allow_unicode=True, width=1000)
    state_path.write_text("\n".join(header_lines) + "\n" + body, encoding="utf-8")
    return {
        "project_id": project_id,
        "applied": True,
        "dry_run": False,
        "estimate": progress["estimate"],
        "method": progress["method"],
        "confidence": progress["confidence"],
        "next_action": next_action,
    }


def load_manifest(project_id: str) -> dict | None:
    path = EVIDENCE_DIR / f"{project_id}.yaml"
    if not path.exists():
        return None
    return load_yaml(path)


def cmd_compute(project_id: str | None, all_projects: bool, dry_run: bool) -> int:
    print(f"WO-OBSIDIAN-039 -- Progress + Next Action Engine ({'DRY-RUN' if dry_run else 'APPLY'})")
    print("=" * 70)
    registry = load_yaml(PROJECTS_YAML)
    ids = [p["project_id"] for p in registry.get("projects", [])]
    if project_id:
        ids = [i for i in ids if i == project_id]
    elif all_projects:
        pass
    if not ids:
        print("no projects")
        return 1
    for pid in ids:
        manifest = load_manifest(pid)
        res = apply_progress_to_state(pid, manifest, dry_run=dry_run)
        if res.get("applied"):
            est = res.get("estimate")
            est_s = "UNKNOWN" if est is None else f"{est}%"
            print(f"  {pid}: progress={est_s} method={res.get('method')} "
                  f"confidence={res.get('confidence')} next_action={res.get('next_action')}")
        else:
            print(f"  {pid}: not applied ({res.get('reason')})")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Progress + next-action engine (WO-039)")
    sub = parser.add_subparsers(dest="cmd")
    p_c = sub.add_parser("compute", help="compute progress + next action")
    p_c.add_argument("--project", help="single project_id")
    p_c.add_argument("--all", action="store_true", help="all registered projects")
    p_c.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv[1:])
    if args.cmd == "compute":
        return cmd_compute(args.project, args.all, args.dry_run)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
