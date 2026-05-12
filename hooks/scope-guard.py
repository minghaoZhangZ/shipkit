#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PreToolUse hook: block edits to files outside the implementation plan scope.

Only active during coding/verification phases. Reads 07_IMPLEMENTATION_PLAN.md
to determine allowed file ranges.

Exit 0 = allow, Exit 2 = hard block.
"""

import sys
import json
import os
import re
from pathlib import Path


KNOWN_PHASES = {
    'analysis', 'design', 'plan', 'coding', 'self_review',
    'verification', 'review', 'delivery', 'archive',
}

BOOLEAN_VALUES = {'true', 'false'}


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
        if 'archive' in str(wf_file):
            continue
        try:
            mtime = wf_file.stat().st_mtime
            candidates.append((mtime, wf_file))
        except OSError:
            continue

    if not candidates:
        return None, None

    candidates.sort(reverse=True)
    change_dir = candidates[0][1].parent.parent
    return candidates[0][1], str(change_dir)


def parse_workflow_state(file_path):
    state = {}
    try:
        with open(file_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' in line:
                    key, _, val = line.partition(':')
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    state[key] = val
    except (IOError, OSError):
        pass
    return state


def validate_workflow_state(state):
    """Return validation errors for fields this hook relies on."""
    errors = []
    required = ('current_phase', 'requires_user_confirmation', 'user_confirmed')

    if not state:
        return ['workflow state is empty or unreadable']

    for key in required:
        if key not in state or state[key] == '':
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
        parts = rel.replace('\\', '/').split('/')
        if len(parts) >= 2 and parts[-2] == 'ai':
            return True
    except ValueError:
        pass
    return False


def parse_allowed_files(plan_path):
    try:
        with open(plan_path, encoding='utf-8') as f:
            content = f.read()
    except (IOError, OSError):
        return None

    # Match section 7 header in either Chinese or English
    m = re.search(
        r'##\s*7\.\s*(?:Allowed|Allow|Scope|允许修改的文件范围)\s*\n(.*?)(?=\n##\s*\d+\.|\Z)',
        content, re.DOTALL
    )
    if not m:
        return None

    section = m.group(1)
    allowed = []
    for line in section.splitlines():
        line = line.strip().lstrip('-').strip()
        if line and not line.startswith('#'):
            allowed.append(line)

    return allowed if allowed else None


def matches_any_pattern(file_path, patterns, project_root):
    rel_path = None
    try:
        rel_path = os.path.relpath(str(Path(file_path).resolve()), project_root)
    except ValueError:
        return False

    for pat in patterns:
        if '*' in pat:
            regex = re.escape(pat).replace(r'\*\*', '___DOUBLE_STAR___')
            regex = regex.replace(r'\*', '[^/]*')
            regex = regex.replace('___DOUBLE_STAR___', '.*')
            if re.match(regex, rel_path):
                return True
        elif rel_path.startswith(pat.rstrip('/')):
            return True
        elif rel_path == pat:
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
            "  Allowed operation: fix files under openspec/changes/*/ai/ "
            "including .workflow_state\n",
            file=sys.stderr,
        )
        sys.exit(2)

    if current_phase not in ('coding', 'verification'):
        sys.exit(0)

    plan_path = os.path.join(change_dir, 'ai', '07_IMPLEMENTATION_PLAN.md')
    if not os.path.isfile(plan_path):
        print(
            "\n[ScopeGuard] Implementation plan not found.\n"
            f"  Phase: {current_phase}\n"
            f"  File: {file_path}\n"
            f"  Plan path: {plan_path}\n"
            "\n07_IMPLEMENTATION_PLAN.md is required before editing business "
            "code in coding/verification phases.\n",
            file=sys.stderr,
        )
        sys.exit(2)

    allowed = parse_allowed_files(plan_path)
    if allowed is None:
        print(
            "\n[ScopeGuard] Could not parse allowed file scope from plan.\n"
            f"  Phase: {current_phase}\n"
            f"  File: {file_path}\n"
            "\nSection 7 of 07_IMPLEMENTATION_PLAN.md must list allowed "
            "file paths before editing business code.\n",
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
        "\nUpdate section 7 of 07_IMPLEMENTATION_PLAN.md "
        "and get user confirmation before editing this file.\n",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == '__main__':
    main()
