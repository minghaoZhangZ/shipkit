#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migrate .workflow_state to schema_version 1.0.

Usage:
  python migrate-workflow-state.py <project-root>
  python migrate-workflow-state.py <project-root> --dry-run
  python migrate-workflow-state.py <project-root> --change <change-id>

Reads openspec/changes/<change-id>/ai/.workflow_state (non-archive),
detects missing fields relative to the 1.0 schema, and writes back
the migrated state.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Canonical schema 1.0 fields with their default values.
CANONICAL_DEFAULTS: Dict[str, Any] = {
    "schema_version": "1.0",
    "change_id": "",
    "profile": "standard",
    "current_phase": "coding",
    "state": "active",
    "current_task": "",
    "last_completed_task": "",
    "next_action": "",
    "task_stack": [],
    "phase_history": [],
    "resume_context": "",
    "checkpoint": "",
    "requires_user_confirmation": "false",
    "user_confirmed": "true",
    "confirmation_type": "",
    "confirmation_role": "",
    "confirmation_docs": "",
    "confirmed_checkpoints": "",
    "required_checkpoints": "",
    "affected_areas": "",
    "context_package": "CONTEXT_PACKAGE.md",
    "trace_matrix_status": "pending",
    "round": "0",
    "max_rounds": "3",
    "pending_decisions_count": "0",
    "project_consistency_enabled": "false",
    "engineering_manifest": "",
    "engineering_mode": "off",
    "verification_mode": "independent",
    "metrics_mode": "change_only",
    "sop_mode": "candidate_only",
    "consistency_review_required": "false",
    "architecture_owner_required": "false",
    "verification_status": "pending",
    "verification_issue_count": "0",
    "metrics_recorded": "false",
    "created_at": "",
    "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
}

# Ordered output keys to match the canonical template.
OUTPUT_ORDER = list(CANONICAL_DEFAULTS.keys())

# Legacy mappings: old keys → canonical keys.
LEGACY_KEY_MAP = {
    "bug_count": None,          # dropped; superseded by verification_issue_count
    "known_issues": None,       # dropped; superseded by verification agent output
    "pending_docs": None,       # dropped; superseded by task_stack
    "uncovered_req_ids": None,  # dropped; superseded by verification agent output
    "self_review_status": "verification_status",
    "self_review_issue_count": "verification_issue_count",
    "self_review_mode": None,   # dropped
}


def parse_workflow_state(file_path: Path) -> Tuple[Dict[str, str], List[str]]:
    """Parse a YAML-line-format .workflow_state file.

    Returns (state_dict, raw_lines_for_reconstruction).
    """
    state: Dict[str, str] = {}
    raw_lines: List[str] = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except (IOError, OSError) as exc:
        return {}, [f"cannot read file: {exc}"]

    for line in content.splitlines():
        raw_lines.append(line)
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if ':' in stripped:
            key, _, val = stripped.partition(':')
            state[key.strip()] = val.strip().strip('"').strip("'")
    return state, raw_lines


def build_migrated_state(old_state: Dict[str, str]) -> Dict[str, str]:
    """Build a new state dict by merging old values into canonical defaults."""
    new_state = dict(CANONICAL_DEFAULTS)

    for key, value in old_state.items():
        if key in LEGACY_KEY_MAP:
            canonical = LEGACY_KEY_MAP[key]
            if canonical is not None and canonical in CANONICAL_DEFAULTS:
                new_state[canonical] = value
            # else: dropped key, skip
        elif key in CANONICAL_DEFAULTS:
            new_state[key] = value
        # else: unknown key, skip (don't carry forward noise)

    # If created_at is empty, infer from file mtime or use today.
    if not new_state.get("created_at", ""):
        new_state["created_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    # If change_id is empty, try to infer from path.
    # This is handled by the caller before calling this function.

    return new_state


def format_yaml_lines(state: Dict[str, str]) -> str:
    """Format a state dict as YAML-line-format text."""
    lines = []
    for key in OUTPUT_ORDER:
        raw_value = state.get(key, CANONICAL_DEFAULTS.get(key, ""))
        str_value = str(raw_value)
        # Values that look like lists leave as-is (already YAML format).
        if str_value.startswith("[") or str_value.startswith("- "):
            lines.append(f"{key}: {str_value}")
        elif str_value in ("true", "false") or str_value.isdigit() or not str_value:
            lines.append(f"{key}: {str_value}")
        else:
            lines.append(f'{key}: "{str_value}"')
    return "\n".join(lines) + "\n"


def find_workflow_states(project_root: Path, change_id: Optional[str] = None) -> List[Path]:
    """Find .workflow_state files in non-archive changes."""
    changes_dir = project_root / "openspec" / "changes"
    if not changes_dir.is_dir():
        return []

    results = []
    for wf_file in changes_dir.glob("*/ai/.workflow_state"):
        path_str = str(wf_file).replace("\\", "/")
        if "/archive/" in path_str:
            continue
        if change_id:
            parent_change = wf_file.parent.parent.name
            if parent_change != change_id:
                continue
        results.append(wf_file)
    results.sort()
    return results


def migrate_file(wf_file: Path, dry_run: bool) -> Dict[str, Any]:
    """Migrate a single .workflow_state file.

    Returns a report dict with keys: file, status, missing_fields, added_fields, errors.
    """
    report: Dict[str, Any] = {
        "file": str(wf_file),
        "status": "ok",
        "missing_fields": [],
        "added_fields": [],
        "dropped_keys": [],
        "errors": [],
    }

    old_state, parse_errors = parse_workflow_state(wf_file)
    if parse_errors:
        report["status"] = "parse_error"
        report["errors"] = parse_errors
        return report

    # Check if already at current version.
    if old_state.get("schema_version") == "1.0":
        # Still check for any missing required fields.
        missing = [k for k in CANONICAL_DEFAULTS if k not in old_state]
        if not missing:
            report["status"] = "current"
            return report
        report["missing_fields"] = missing

    # Track what's being added and dropped.
    for key in CANONICAL_DEFAULTS:
        if key not in old_state:
            report["added_fields"].append(key)

    for key in old_state:
        if key in LEGACY_KEY_MAP:
            report["dropped_keys"].append(key)
        elif key not in CANONICAL_DEFAULTS:
            report["dropped_keys"].append(key)

    # Infer change_id from directory name if missing.
    if not old_state.get("change_id", ""):
        old_state["change_id"] = wf_file.parent.parent.name

    new_state = build_migrated_state(old_state)

    if dry_run:
        report["status"] = "would_migrate"
        return report

    new_content = format_yaml_lines(new_state)
    backup_path = wf_file.with_suffix(".workflow_state.bak")
    try:
        wf_file.rename(backup_path)
        wf_file.write_text(new_content, encoding="utf-8")
        report["backup"] = str(backup_path)
    except (IOError, OSError) as exc:
        report["status"] = "write_error"
        report["errors"].append(str(exc))
        return report

    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate .workflow_state files to schema version 1.0"
    )
    parser.add_argument("project_root", help="Path to the project root directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    parser.add_argument("--change", metavar="CHANGE_ID", help="Migrate only a specific change")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not project_root.is_dir():
        print(f"Error: project root not found: {project_root}", file=sys.stderr)
        return 1

    wf_files = find_workflow_states(project_root, args.change)
    if not wf_files:
        print("No active .workflow_state files found. Nothing to migrate.")
        return 0

    total = len(wf_files)
    ok = 0
    errors = 0

    for wf_file in wf_files:
        report = migrate_file(wf_file, args.dry_run)
        status = report["status"]
        change_name = wf_file.parent.parent.name

        if status == "current":
            print(f"  [SKIP] {change_name} — already schema_version 1.0")
            ok += 1
        elif status == "would_migrate":
            print(f"  [DRY-RUN] {change_name} — would add {len(report['added_fields'])} fields, drop {len(report['dropped_keys'])} keys")
            ok += 1
        elif status == "ok":
            print(f"  [OK] {change_name} — migrated ({len(report['added_fields'])} fields added, {len(report['dropped_keys'])} dropped)")
            ok += 1
        else:
            print(f"  [ERROR] {change_name} — {report['status']}: {'; '.join(report.get('errors', ['unknown']))}")
            errors += 1

    print(f"\nDone: {total} file(s), {ok} ok, {errors} error(s)")
    if args.dry_run and wf_files:
        print("Dry run — no files were modified. Remove --dry-run to apply.")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
