#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PreToolUse hook: block business-code edits when user confirmation is pending.

Reads tool call JSON from stdin. Processes Write, Edit, and Bash tools.
Checks .workflow_state to determine if the current phase requires user
confirmation before touching business code.

Exit 0 = allow, Exit 2 = hard block.
"""

import sys
import json
import os
import re
from pathlib import Path


# Bash commands that are ALWAYS safe (read-only) — never block these.
READONLY_COMMANDS = {
    'ls', 'dir', 'cat', 'head', 'tail', 'less', 'more',
    'find', 'grep', 'rg', 'git status', 'git log', 'git diff',
    'git blame', 'git show', 'git stash list', 'git branch',
    'git remote', 'git config', 'echo', 'pwd', 'which', 'where',
    'type', 'env', 'printenv', 'date', 'wc', 'sort', 'uniq',
    'cut', 'tr', 'awk', 'sed', 'xargs', 'tee', 'file', 'stat',
    'du', 'df', 'tree', 'ps', 'top', 'htop',
}

KNOWN_PHASES = {
    'analysis', 'design', 'plan', 'coding', 'self_review',
    'verification', 'review', 'delivery', 'archive',
}

BOOLEAN_VALUES = {'true', 'false'}


def find_project_root(cwd):
    """Find project root by looking for openspec/ or .claude/ directory."""
    p = Path(cwd).resolve()
    for parent in [p] + list(p.parents):
        if (parent / '.claude').is_dir() or (parent / 'openspec').is_dir():
            return str(parent)
    return cwd


def find_active_workflow_state(project_root):
    """Scan openspec/changes/*/ai/.workflow_state, return the most recent
    one that requires confirmation and is unconfirmed."""
    changes_dir = Path(project_root) / 'openspec' / 'changes'
    if not changes_dir.is_dir():
        return None

    candidates = []
    for wf_file in changes_dir.glob('*/ai/.workflow_state'):
        # Skip archived
        if 'archive' in str(wf_file):
            continue
        try:
            mtime = wf_file.stat().st_mtime
            candidates.append((mtime, wf_file))
        except OSError:
            continue

    if not candidates:
        return None

    # Return the most recently modified one
    candidates.sort(reverse=True)
    return candidates[0][1]


def parse_workflow_state(file_path):
    """Parse .workflow_state YAML-like file into a dict.
    Handles simple key: value lines and list items."""
    state = {}
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
    except (IOError, OSError):
        return state

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # key: value
        if ':' in line:
            key, _, val = line.partition(':')
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            state[key] = val
    return state


def validate_workflow_state(state):
    """Return validation errors for fields this hook relies on.

    Keep this intentionally small so older changes are not rejected for missing
    newer, optional workflow fields.
    """
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

    if state.get('requires_user_confirmation') == 'true':
        for key in ('checkpoint', 'confirmation_type'):
            if not state.get(key):
                errors.append(f'missing required key while confirmation pending: {key}')

    return errors


def print_malformed_state_block(wf_file, errors, blocked_target):
    print(
        "\n[CheckpointGuard] Active workflow state is malformed; "
        "business-code operations are blocked fail-closed.\n"
        f"  State file: {wf_file}\n"
        f"  Blocked target: {blocked_target}\n"
        f"  Errors: {'; '.join(errors)}\n"
        "  Allowed operation: fix files under openspec/changes/*/ai/ "
        "including .workflow_state\n",
        file=sys.stderr,
    )


def is_ai_doc(file_path, project_root):
    """Check if file_path is an AI document under openspec/changes/*/ai/."""
    normalized = str(Path(file_path).resolve())
    ai_dir = str((Path(project_root) / 'openspec' / 'changes').resolve())
    try:
        # Must be under openspec/changes/.../ai/
        rel = os.path.relpath(normalized, ai_dir)
        parts = rel.replace('\\', '/').split('/')
        if len(parts) >= 2 and parts[-2] == 'ai':
            return True
    except ValueError:
        pass
    return False


def is_bash_safe(command):
    """Check if a bash command is read-only / safe."""
    cmd_stripped = command.strip()
    # Check exact matches first
    for safe_cmd in READONLY_COMMANDS:
        if cmd_stripped == safe_cmd or cmd_stripped.startswith(safe_cmd + ' '):
            return True
    # Git read-only patterns
    if re.match(r'^git\s+(status|log|diff|blame|show|stash\s+list|branch|remote|config\s+--get)', cmd_stripped):
        return True
    return False


def is_build_or_test_command(command):
    """Check if a bash command looks like a build/test/commit action."""
    patterns = [
        r'\b(mvn|mvnw|gradlew?)\b',          # Java build
        r'\b(npm|pnpm|yarn)\s+(run\s+)?(build|test|lint)',  # Node build/test
        r'\b(npm|pnpm|yarn)\s+install\b',     # Node install
        r'\bgit\s+(add|commit|merge|rebase)', # Git modifying
        r'\bdocker\s+(build|push|run)',       # Docker
        r'\bmake\b',                          # Make
        r'\bgo\s+(build|test|install)',       # Go
        r'\bcargo\s+(build|test)',            # Rust
        r'\bpip\s+install\b',                 # Python install
        r'\bpoetry\s+(install|add|update)',   # Poetry
        r'\buv\s+(pip\s+)?install\b',         # UV install
        r'\.\/\S*(test|build|deploy)',        # Scripts
    ]
    for pat in patterns:
        if re.search(pat, command):
            return True
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    tool_name = data.get('tool_name', '')
    cwd = data.get('cwd', os.getcwd())
    project_root = find_project_root(cwd)

    # Find active workflow state
    wf_file = find_active_workflow_state(project_root)
    if wf_file is None:
        sys.exit(0)  # No active change, allow

    state = parse_workflow_state(wf_file)
    state_errors = validate_workflow_state(state)
    requires_conf = state.get('requires_user_confirmation', 'false')
    user_confirmed = state.get('user_confirmed', 'true')
    confirmation_type = state.get('confirmation_type', '')
    current_phase = state.get('current_phase', '')
    checkpoint = state.get('checkpoint', '')

    if tool_name in ('Write', 'Edit', 'MultiEdit'):
        file_path = data.get('tool_input', {}).get('file_path', '')
        if not file_path:
            sys.exit(0)

        # Always allow writing to AI docs
        if is_ai_doc(file_path, project_root):
            sys.exit(0)

        if state_errors:
            print_malformed_state_block(wf_file, state_errors, file_path)
            sys.exit(2)

        # If no confirmation required or already confirmed, allow
        if requires_conf != 'true' or user_confirmed == 'true':
            sys.exit(0)

        # Block business code edit
        print(
            f"\n[CheckpointGuard] 当前处于 {checkpoint} checkpoint，"
            f"尚未获得用户确认。\n"
            f"  待确认: {confirmation_type}\n"
            f"  被拦截文件: {file_path}\n"
            f"  允许操作: 写入 openspec/changes/*/ai/ 下的文档\n"
            f"  禁止操作: 修改业务代码\n"
            f"\n请先用 AskUserQuestion 向用户确认后再继续。\n",
            file=sys.stderr,
        )
        sys.exit(2)

    elif tool_name == 'Bash':
        command = data.get('tool_input', {}).get('command', '')
        if not command:
            sys.exit(0)

        # Always allow read-only commands
        if is_bash_safe(command):
            sys.exit(0)

        if state_errors:
            print_malformed_state_block(wf_file, state_errors, command)
            sys.exit(2)

        # If no confirmation required or already confirmed, allow
        if requires_conf != 'true' or user_confirmed == 'true':
            sys.exit(0)

        # Block build/test/commit commands
        if is_build_or_test_command(command):
            print(
                f"\n[CheckpointGuard] 当前处于 {checkpoint} checkpoint，"
                f"尚未获得用户确认。\n"
                f"  待确认: {confirmation_type}\n"
                f"  被拦截命令: {command}\n"
                f"  允许: 只读查询命令 (git status, grep, ls, cat 等)\n"
                f"  禁止: 构建/测试/安装依赖/提交等修改性命令\n"
                f"\n请先用 AskUserQuestion 向用户确认后再继续。\n",
                file=sys.stderr,
            )
            sys.exit(2)

        # For other non-readonly, non-build commands — allow (could be
        # research/debugging commands that shouldn't be blocked)

    sys.exit(0)


if __name__ == '__main__':
    main()
