#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PreToolUse hook: block business-code work while a workflow checkpoint waits.

Reads tool call JSON from stdin. It allows AI document edits under
openspec/changes/*/ while a confirmation is pending, but blocks business-code
edits and build/test/commit style commands until the checkpoint is confirmed.
"""

import json
import os
import re
import sys
from pathlib import Path


READONLY_COMMANDS = {
    'ls', 'dir', 'cat', 'head', 'tail', 'less', 'more',
    'find', 'grep', 'rg', 'git status', 'git log', 'git diff',
    'git blame', 'git show', 'git stash list', 'git branch',
    'git remote', 'git config', 'echo', 'pwd', 'which', 'where',
    'type', 'env', 'printenv', 'date', 'wc', 'sort', 'uniq',
    'cut', 'tr', 'awk', 'sed', 'xargs', 'tee', 'file', 'stat',
    'du', 'df', 'tree', 'ps', 'top', 'htop', 'Get-ChildItem',
    'Get-Content', 'Select-String',
}

KNOWN_VERSIONS = {'1.0'}

KNOWN_PHASES = {
    'requirement', 'prd', 'engineering_spec', 'research',
    'backend_design', 'frontend_design', 'contract', 'plan',
    'coding', 'self_review', 'verification', 'review', 'delivery', 'archive',
    # Backward-compatible phases for old changes.
    'analysis', 'design',
}

KNOWN_CONFIRMATION_TYPES = {
    'approve_prd',
    'approve_engineering_spec',
    'approve_backend_design',
    'approve_frontend_design',
    'approve_contract',
    'approve_implementation_plan',
    # Backward-compatible value.
    'approve_spec',
}

KNOWN_STATES = {'active', 'blocked', 'failed', 'finished'}

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
        return None

    candidates = []
    for wf_file in changes_dir.glob('*/.workflow_state'):
        if 'archive' in str(wf_file).replace('\\', '/').split('/'):
            continue
        try:
            candidates.append((wf_file.stat().st_mtime, wf_file))
        except OSError:
            continue

    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


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

    if state.get('requires_user_confirmation') == 'true':
        for key in ('checkpoint', 'confirmation_type', 'confirmation_role', 'confirmation_docs'):
            if not state.get(key):
                errors.append(f'missing required key while confirmation pending: {key}')
        ctype = state.get('confirmation_type', '')
        if ctype and ctype not in KNOWN_CONFIRMATION_TYPES:
            errors.append(f'invalid confirmation_type: {ctype}')

    # Validate lifecycle state.
    lifecycle_state = state.get('state', 'active')
    if lifecycle_state and lifecycle_state not in KNOWN_STATES:
        errors.append(f'invalid state: {lifecycle_state}. Known: {sorted(KNOWN_STATES)}')

    # Non-blocking: resume_context should be present for context recovery
    if not state.get('resume_context', ''):
        print(
            "[CheckpointGuard] Warning: resume_context is empty. "
            "Context recovery after /clear may be incomplete.",
            file=sys.stderr,
        )

    return errors


def print_malformed_state_block(wf_file, errors, blocked_target):
    print(
        "\n[CheckpointGuard] Active workflow state is malformed; "
        "business-code operations are blocked fail-closed.\n"
        f"  State file: {wf_file}\n"
        f"  Blocked target: {blocked_target}\n"
        f"  Errors: {'; '.join(errors)}\n"
        "  Allowed operation: fix files under openspec/changes/*/ "
        "including .workflow_state\n",
        file=sys.stderr,
    )


def is_ai_doc(file_path, project_root):
    normalized = str(Path(file_path).resolve())
    ai_base = str((Path(project_root) / 'openspec' / 'changes').resolve())
    try:
        rel = os.path.relpath(normalized, ai_base)
    except ValueError:
        return False
    parts = rel.replace('\\', '/').split('/')
    # rel should be like "<change-id>/<filename>"
    return len(parts) >= 2


def is_bash_safe(command):
    cmd = command.strip()
    for safe_cmd in READONLY_COMMANDS:
        if cmd == safe_cmd or cmd.startswith(safe_cmd + ' '):
            return True
    if re.match(r'^git\s+(status|log|diff|blame|show|stash\s+list|branch|remote|config\s+--get)\b', cmd):
        return True
    return False


def is_build_or_test_command(command):
    patterns = [
        r'\b(mvn|mvnw|gradlew?)\b',
        r'\b(npm|pnpm|yarn)\s+(run\s+)?(build|test|lint|typecheck)\b',
        r'\b(npm|pnpm|yarn)\s+install\b',
        r'\bgit\s+(add|commit|merge|rebase)\b',
        r'\bdocker\s+(build|push|run)\b',
        r'\bmake\b',
        r'\bgo\s+(build|test|install)\b',
        r'\bcargo\s+(build|test)\b',
        r'\bpip\s+install\b',
        r'\bpoetry\s+(install|add|update)\b',
        r'\buv\s+(pip\s+)?install\b',
        r'\.\/\S*(test|build|deploy)\b',
    ]
    return any(re.search(pattern, command, re.IGNORECASE) for pattern in patterns)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    tool_name = data.get('tool_name', '')
    cwd = data.get('cwd', os.getcwd())
    project_root = find_project_root(cwd)
    wf_file = find_active_workflow_state(project_root)
    if wf_file is None:
        sys.exit(0)

    state = parse_workflow_state(wf_file)
    state_errors = validate_workflow_state(state)
    requires_conf = state.get('requires_user_confirmation', 'false')
    user_confirmed = state.get('user_confirmed', 'true')
    checkpoint = state.get('checkpoint', '')
    confirmation_type = state.get('confirmation_type', '')
    confirmation_role = state.get('confirmation_role', '')
    confirmation_docs = state.get('confirmation_docs', '')

    if tool_name in ('Write', 'Edit', 'MultiEdit'):
        file_path = data.get('tool_input', {}).get('file_path', '')
        if not file_path:
            sys.exit(0)

        if is_ai_doc(file_path, project_root):
            sys.exit(0)

        if state_errors:
            print_malformed_state_block(wf_file, state_errors, file_path)
            sys.exit(2)

        lifecycle_state = state.get('state', 'active')
        if lifecycle_state == 'blocked':
            print(
                f"\n[CheckpointGuard] 当前 change 已被阻塞 (state: blocked)。\n"
                f"  Change: {state.get('change_id', 'unknown')}\n"
                f"  被拦截文件: {file_path}\n"
                "  允许操作: 写入 openspec/changes/*/ 下的 AI 文档。\n"
                "  禁止操作: 修改业务代码。\n"
                "\n请先处理 PENDING_DECISIONS.md 中的阻塞项后再继续。\n",
                file=sys.stderr,
            )
            sys.exit(2)

        if lifecycle_state == 'failed':
            print(
                f"\n[CheckpointGuard] 当前 change 已放弃 (state: failed)。\n"
                f"  Change: {state.get('change_id', 'unknown')}\n"
                "  此 change 不可恢复。如需继续，请创建新 change。\n",
                file=sys.stderr,
            )
            sys.exit(2)

        if requires_conf != 'true' or user_confirmed == 'true':
            sys.exit(0)

        print(
            f"\n[CheckpointGuard] 当前处于 {checkpoint} checkpoint，尚未获得用户确认。\n"
            f"  待确认: {confirmation_type}\n"
            f"  确认角色: {confirmation_role}\n"
            f"  确认文档: {confirmation_docs}\n"
            f"  被拦截文件: {file_path}\n"
            "  允许操作: 写入 openspec/changes/*/ 下的 AI 文档。\n"
            "  禁止操作: 修改业务代码。\n"
            "\n请先用 AskUserQuestion 向用户确认后再继续。\n",
            file=sys.stderr,
        )
        sys.exit(2)

    if tool_name == 'Bash':
        command = data.get('tool_input', {}).get('command', '')
        if not command:
            sys.exit(0)

        if is_bash_safe(command):
            sys.exit(0)

        if state_errors:
            print_malformed_state_block(wf_file, state_errors, command)
            sys.exit(2)

        if requires_conf != 'true' or user_confirmed == 'true':
            sys.exit(0)

        if is_build_or_test_command(command):
            print(
                f"\n[CheckpointGuard] 当前处于 {checkpoint} checkpoint，尚未获得用户确认。\n"
                f"  待确认: {confirmation_type}\n"
                f"  确认角色: {confirmation_role}\n"
                f"  确认文档: {confirmation_docs}\n"
                f"  被拦截命令: {command}\n"
                "  允许: 只读查询命令。\n"
                "  禁止: 构建/测试/安装依赖/提交等修改性命令。\n"
                "\n请先用 AskUserQuestion 向用户确认后再继续。\n",
                file=sys.stderr,
            )
            sys.exit(2)

    sys.exit(0)


if __name__ == '__main__':
    main()
