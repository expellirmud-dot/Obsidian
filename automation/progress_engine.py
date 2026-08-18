#!/usr/bin/env python3
"""Deterministic progress + next-action engine (WO-OBSIDIAN-039).

Computes progress from EVIDENCE only -- never from LLM impression. Priority:
  1. explicit weighted roadmap milestones (explicit weights)
  2. bounded milestones (equal weight)
  3. UNSUPPORTED -> UNKNOWN (do not claim support that does not exist):
       * phase/goal progress: NOT IMPLEMENTED
       * bounded work-order set: NOT IMPLEMENTED (no reliable structure in
         evidence to bound the denominator)
  4. insufficient / incomplete denominator -> UNKNOWN

Truncation safety (WO-OBSIDIAN-041): the evidence collector caps
`content_excerpt` at 500 chars and strips newlines. A roadmap whose checklist
extends past that cap yields an INCOMPLETE denominator, so a percentage derived
from the excerpt would be false (later milestones silently lost). Before
computing a percentage, compute_progress checks every roadmap evidence item for
truncation (the `truncated` flag / `content_length` added by the evidence
collector, with a `len(excerpt) >= 500` fallback for old manifests). If any
roadmap evidence is truncated -> UNKNOWN, never a fabricated percentage.

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
  * Never fabricates a percentage. Missing/incomplete denominator ->
    estimate=null, confidence=unknown.
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

# Non-line-anchored variant for newline-stripped excerpts: the evidence
# collector flattens content to a single line, so the line-anchored regex
# above would collapse several milestones into one (greedy name) or miss
# them. This variant finds each `[x]`/`[ ]` marker in place; the name is
# lazy and bounded by a lookahead to the next marker (or end of string).
MILESTONE_RE_FLAT = re.compile(
    r"\[(?P<done>[xX ])\]\s*(?:\((?P<weight>\d+)\)\s*)?"
    r"(?P<name>.+?)(?=\s*[-*]?\s*\[[xX ]\]|$)"
)

# A single milestone checkbox marker, used to count markers regardless of
# whether the line structure is intact.
_MARKER_RE = re.compile(r"\[[xX ]\]")


def _milestone_from_match(m: re.Match) -> dict | None:
    done = m.group("done").strip().lower() == "x"
    weight = int(m.group("weight")) if m.group("weight") else 1
    name = m.group("name").strip().strip("*_`-").strip()
    if not name:
        return None
    return {"name": name, "done": done, "weight": weight}


def parse_milestones_from_content(content: str) -> list[dict]:
    """Parse weighted milestone lines from markdown content.

    Returns a list of {name, done (bool), weight (int)}.

    Handles two shapes of content:
      * multi-line checklists (line-anchored regex over splitlines());
      * newline-stripped excerpts (a single long line with several
        ``[x]``/``[ ]`` markers), via a finditer fallback. The fallback only
        triggers when the content has no newlines but contains multiple
        markers, so normal multi-line content is unaffected.

    NOTE: this parser does NOT decide whether the excerpt was truncated -- that
    is the caller's responsibility (see ``is_evidence_truncated`` /
    ``compute_progress``). A truncated excerpt may still parse here, but
    ``compute_progress`` gates on truncation and returns UNKNOWN.
    """
    if not content:
        return []
    milestones: list[dict] = []
    for line in content.splitlines():
        m = MILESTONE_RE.match(line)
        if not m:
            continue
        ms = _milestone_from_match(m)
        if ms:
            milestones.append(ms)

    # Fallback for newline-stripped excerpts: one long line, many markers.
    has_newlines = "\n" in content
    marker_count = len(_MARKER_RE.findall(content))
    if not has_newlines and marker_count > 1:
        flat: list[dict] = []
        for m in MILESTONE_RE_FLAT.finditer(content):
            ms = _milestone_from_match(m)
            if ms:
                flat.append(ms)
        # Only adopt the flat parse if it recovers at least as many milestones
        # (it should recover all markers when the line was flattened).
        if len(flat) >= len(milestones):
            milestones = flat
    return milestones


def collect_roadmap_evidence(manifest: dict) -> list[dict]:
    """Return roadmap-category evidence items (with content_excerpt)."""
    return [e for e in manifest.get("evidence", []) if e.get("category") == "roadmap"]


def collect_completed_evidence(manifest: dict) -> list[dict]:
    return [e for e in manifest.get("evidence", []) if e.get("category") == "completed_work"]


# Evidence-collector excerpt cap (see evidence_collector.py). Excerpts at or
# past this cap are treated as truncated when no explicit signal is present.
_EXCERPT_CAP = 500


def is_evidence_truncated(ev: dict) -> bool:
    """Decide whether an evidence item's content_excerpt is incomplete.

    Reads the ``truncated`` (bool) and ``content_length`` (int, full content
    length before truncation) fields defensively -- they are added by the
    evidence collector (WO-OBSIDIAN-041) and may be absent in old manifests.

    Resolution order:
      1. explicit ``truncated`` flag (if present);
      2. ``content_length`` (if present): truncated when the full content was
         longer than the kept excerpt, or longer than the 500-char cap;
      3. fallback for old manifests: truncated when the excerpt itself is at
         least as long as the 500-char cap (i.e. it likely hit the cap).
    """
    if "truncated" in ev:
        return bool(ev.get("truncated"))
    content_length = ev.get("content_length")
    if isinstance(content_length, int):
        excerpt = ev.get("content_excerpt") or ""
        return content_length > len(excerpt) or content_length > _EXCERPT_CAP
    excerpt = ev.get("content_excerpt") or ""
    return len(excerpt) >= _EXCERPT_CAP


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
      3. UNSUPPORTED -> UNKNOWN:
           * phase/goal progress: NOT IMPLEMENTED
           * bounded work-order set: NOT IMPLEMENTED (no reliable structure in
             evidence to bound the denominator)
      4. UNKNOWN

    Truncation gate (WO-OBSIDIAN-041): before computing a percentage, every
    roadmap evidence item is checked for truncation. If ANY roadmap evidence is
    truncated, the denominator is INCOMPLETE and a percentage would be false --
    so UNKNOWN is returned regardless of what the parser recovered.
    """
    roadmap_ev = collect_roadmap_evidence(manifest)

    # Truncation gate: an incomplete denominator must never yield a percentage.
    for ev in roadmap_ev:
        if is_evidence_truncated(ev):
            return compute_unknown_progress(
                reason="roadmap evidence truncated (incomplete denominator; "
                "cannot compute a reliable percentage)"
            )

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
