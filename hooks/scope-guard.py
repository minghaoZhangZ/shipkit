#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PreToolUse hook: block edits outside the confirmed implementation plan.

Only active during coding/verification phases. Reads the canonical
07_实施计划.md and falls back to the old 07_IMPLEMENTATION_PLAN.md.
"""

import json
import os
import re
import sys
from pathlib import Path


KNOWN_VERSIONS = {'1.0'}

KNOWN_PHASES = {
    'requirement', 'prd', 'engineering_spec', 'research',
    'backend_design', 'frontend_design', 'contract', 'plan',
    'coding', 'self_review', 'verification', 'review', 'delivery', 'archive',
    # Backward-compatible phases for old changes.
    'analysis', 'design',
}

BOOLEAN_VALUES = {'true', 'false'}
PLAN_FILENAMES = ('07_实施计划.md', '07_IMPLEMENTATION_PLAN.md')


def find_project_root(cwd):
    p = Path(cwd).resolve()
    for parent in [p] + list(p.parents):
        if (parent / '.claude').is_dir() or (parent / 'openspec').is_dir():
            return str(parent)
    return cwd


def find_active_workflow_state(project_root):
    changes_dir = Path(project_root) / 'openspec' / 'changes'
    if not changes_dir.is_dir():
        return None, None

    candidates = []
    for wf_file in changes_dir.glob('*/ai/.workflow_state'):
        if 'archive' in str(wf_file).replace('\\', '/').split('/'):
            continue
        try:
            candidates.append((wf_file.stat().st_mtime, wf_file))
        except OSError:
            continue

    if not candidates:
        return None, None
    candidates.sort(reverse=True)
    wf_file = candidates[0][1]
    return wf_file, str(wf_file.parent.parent)


def parse_workflow_state(file_path):
    state = {}
    try:
        content = Path(file_path).read_text(encoding='utf-8')
    except (IOError, OSError):
        return state

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or line.startswith('- '):
            continue
        if ':' in line:
            key, _, val = line.partition(':')
            state[key.strip()] = val.strip().strip('"').strip("'")
    return state


def validate_workflow_state(state):
    errors = []
    required = ('current_phase', 'requires_user_confirmation', 'user_confirmed')

    if not state:
        return ['workflow state is empty or unreadable']

    version = state.get('schema_version', '')
    if version not in KNOWN_VERSIONS:
        errors.append(
            f'unknown or missing schema_version: {version!r}. '
            f'Known: {sorted(KNOWN_VERSIONS)}. '
            f'Update .workflow_state to current schema or run migrate-workflow-state.py.'
        )

    for key in required:
        if not state.get(key):
            errors.append(f'missing required key: {key}')

    phase = state.get('current_phase', '')
    if phase and phase not in KNOWN_PHASES:
        errors.append(f'invalid current_phase: {phase}')

    for key in ('requires_user_confirmation', 'user_confirmed'):
        value = state.get(key, '')
        if value and value not in BOOLEAN_VALUES:
            errors.append(f'{key} must be true or false: {value}')

    return errors


def is_ai_doc(file_path, project_root):
    normalized = str(Path(file_path).resolve())
    ai_base = str((Path(project_root) / 'openspec' / 'changes').resolve())
    try:
        rel = os.path.relpath(normalized, ai_base)
    except ValueError:
        return False
    parts = rel.replace('\\', '/').split('/')
    return len(parts) >= 3 and parts[1] == 'ai'


def find_plan_path(change_dir):
    ai_dir = Path(change_dir) / 'ai'
    for filename in PLAN_FILENAMES:
        candidate = ai_dir / filename
        if candidate.is_file():
            return str(candidate)
    return str(ai_dir / PLAN_FILENAMES[0])


def parse_allowed_files(plan_path):
    try:
        content = Path(plan_path).read_text(encoding='utf-8')
    except (IOError, OSError):
        return None

    section_patterns = [
        r'###\s*允许修改的文件范围\s*\n(.*?)(?=\n(?:##|###)\s+|\Z)',
        r'###\s*Allowed[^\n]*\n(.*?)(?=\n(?:##|###)\s+|\Z)',
        r'###\s*允许修改的文件[^\n]*\n(.*?)(?=\n(?:##|###)\s+|\Z)',
        # Legacy: old numbered-section format (backward compat)
        r'##\s*7\.\s*允许修改的文件范围\s*\n(.*?)(?=\n##\s*\d+\.|\Z)',
        r'##\s*7\.\s*Allowed[^\n]*\n(.*?)(?=\n##\s*\d+\.|\Z)',
    ]
    section = None
    for pattern in section_patterns:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            section = match.group(1)
            break
    if section is None:
        return None

    allowed = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or line.startswith('|'):
            continue
        line = line.lstrip('-*').strip()
        line = line.strip('`').strip()
        if line and not line.startswith('说明'):
            allowed.append(line)
    return allowed or None


def matches_any_pattern(file_path, patterns, project_root):
    try:
        rel_path = os.path.relpath(str(Path(file_path).resolve()), project_root)
    except ValueError:
        return False
    rel_path = rel_path.replace('\\', '/')

    for raw_pat in patterns:
        pat = raw_pat.replace('\\', '/').strip()
        if not pat or pat in ('无', 'none', 'N/A'):
            continue
        if '*' in pat:
            regex = re.escape(pat)
            regex = regex.replace(r'\*\*', '.*').replace(r'\*', '[^/]*')
            if re.match(regex + r'\Z', rel_path):
                return True
        elif rel_path == pat or rel_path.startswith(pat.rstrip('/') + '/'):
            return True
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    tool_name = data.get('tool_name', '')
    if tool_name not in ('Write', 'Edit', 'MultiEdit'):
        sys.exit(0)

    cwd = data.get('cwd', os.getcwd())
    project_root = find_project_root(cwd)
    wf_file, change_dir = find_active_workflow_state(project_root)
    if wf_file is None:
        sys.exit(0)

    state = parse_workflow_state(wf_file)
    state_errors = validate_workflow_state(state)
    current_phase = state.get('current_phase', '')

    file_path = data.get('tool_input', {}).get('file_path', '')
    if not file_path:
        sys.exit(0)

    if is_ai_doc(file_path, project_root):
        sys.exit(0)

    if state_errors:
        print(
            "\n[ScopeGuard] Active workflow state is malformed; "
            "business-code edits are blocked fail-closed.\n"
            f"  State file: {wf_file}\n"
            f"  File: {file_path}\n"
            f"  Errors: {'; '.join(state_errors)}\n"
            "  Allowed operation: fix files under openspec/changes/*/ai/ including .workflow_state\n",
            file=sys.stderr,
        )
        sys.exit(2)

    if current_phase not in ('coding', 'verification'):
        sys.exit(0)

    plan_path = find_plan_path(change_dir)
    if not os.path.isfile(plan_path):
        print(
            "\n[ScopeGuard] Implementation plan not found.\n"
            f"  Phase: {current_phase}\n"
            f"  File: {file_path}\n"
            f"  Plan path: {plan_path}\n"
            "\n07_实施计划.md is required before editing business code in coding/verification phases.\n",
            file=sys.stderr,
        )
        sys.exit(2)

    allowed = parse_allowed_files(plan_path)
    if allowed is None:
        print(
            "\n[ScopeGuard] Could not parse allowed file scope from plan.\n"
            f"  Phase: {current_phase}\n"
            f"  File: {file_path}\n"
            "\nSection 7 of 07_实施计划.md must list allowed file paths before editing business code.\n",
            file=sys.stderr,
        )
        sys.exit(2)

    if matches_any_pattern(file_path, allowed, project_root):
        sys.exit(0)

    print(
        "\n[ScopeGuard] File not in allowed scope of implementation plan.\n"
        f"  Phase: {current_phase}\n"
        f"  File: {file_path}\n"
        f"  Allowed: {', '.join(allowed[:10])}\n"
        "\nUpdate section 7 of 07_实施计划.md and get user confirmation before editing this file.\n",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == '__main__':
    main()
