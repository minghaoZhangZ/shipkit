#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PreToolUse hook: validate rule ID prefixes when writing engineering spec files.

Only checks .md files under openspec/specs/engineering/.
Extracts rule IDs (e.g. JAVA-DA-001, GEN-002) and validates each prefix
against engineering.json rulePrefixIndex.
"""

import json
import os
import re
import sys
from pathlib import Path

# Matches rule IDs like: JAVA-DA-001, GEN-002, DB-IDX-005, ARCH-LAYER-001, FORBID-SEC-001
# Pattern: UPPER(-UPPER)*-\d+  e.g. JAVA-DA-001 → prefix "JAVA-DA-"
RULE_ID_PATTERN = re.compile(r'\b([A-Z]+(?:-[A-Z]+)*-\d+)\b')


def find_project_root(cwd):
    p = Path(cwd).resolve()
    for parent in [p] + list(p.parents):
        if (parent / '.claude').is_dir() or (parent / 'openspec').is_dir():
            return str(parent)
    return cwd


def is_engineering_spec(file_path, project_root):
    """Check if file is under openspec/specs/engineering/."""
    normalized = str(Path(file_path).resolve())
    eng_base = str((Path(project_root) / 'openspec' / 'specs' / 'engineering').resolve())
    try:
        rel = os.path.relpath(normalized, eng_base)
    except ValueError:
        return False
    return not rel.startswith('..') and not os.path.isabs(rel)


def load_rule_prefix_index(project_root):
    """Load rulePrefixIndex from engineering.json. Returns empty dict on failure."""
    manifest_path = Path(project_root) / 'openspec' / 'specs' / 'engineering' / 'engineering.json'
    try:
        data = json.loads(manifest_path.read_text(encoding='utf-8'))
    except (IOError, OSError, json.JSONDecodeError):
        return {}

    # v2 schema
    if data.get('schemaVersion', 0) >= 2:
        return data.get('rulePrefixIndex', {})

    # v1 legacy: derive from requiredSpecs paths (best-effort)
    required = data.get('requiredSpecs', [])
    prefix_map = {}
    legacy_prefix_map = {
        '行为准则.md': 'GEN-',
        '需求澄清与上下文规则.md': 'CTX-',
        'Java后端编码规范.md': 'JAVA-',
        'Spring事务与并发规范.md': 'TX-',
        'SQL与数据库规范.md': 'DB-',
        '前端编码与交互规范.md': 'FE-',
        'API契约与DTO-VO规范.md': 'API-',
        'Redis与缓存规范.md': 'CACHE-',
        '通用空值与equals规范.md': 'NPE-',
        '分层架构规范.md': 'ARCH-LAYER-',
        '模块边界规范.md': 'MOD-',
        '依赖方向规范.md': 'DEP-',
        '领域概念与命名规范.md': 'DOMAIN-',
        '可复用能力规范.md': 'API-REUSE-',
        '单元测试规范.md': 'TEST-',
        '验证命令与测试证据规范.md': 'VERIFY-',
        '代码审查清单.md': 'REVIEW-',
        '禁止模式清单.md': 'FORBID-',
        '需求拆解规范.md': 'REQ-',
        '实施计划规范.md': 'PLAN-',
        '变更范围控制规范.md': 'SCOPE-',
        '发布与回滚规范.md': 'DEPLOY-',
        'SOP注册表.md': 'SOP-',
        '问题复盘规范.md': 'RETRO-',
    }
    for path in required:
        filename = os.path.basename(path)
        prefix = legacy_prefix_map.get(filename, '')
        if prefix:
            prefix_map[prefix] = {
                'category': 'legacy',
                'owner': 'unknown',
                'status': 'active'
            }
    return prefix_map


def extract_rule_ids_from_content(content):
    """Extract all rule IDs like JAVA-DA-001 from content."""
    return RULE_ID_PATTERN.findall(content)


def extract_prefix(rule_id):
    """Extract prefix from rule ID.
    GEN-001 → 'GEN-'
    JAVA-DA-001 → 'JAVA-DA-'
    DB-IDX-005 → 'DB-IDX-'
    ARCH-LAYER-001 → 'ARCH-LAYER-'
    """
    match = re.match(r'^([A-Z]+(?:-[A-Z]+)*)-\d+$', rule_id)
    if not match:
        return rule_id
    prefix = match.group(1)
    return prefix + '-'


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
    file_path = data.get('tool_input', {}).get('file_path', '')
    if not file_path:
        sys.exit(0)

    if not is_engineering_spec(file_path, project_root):
        sys.exit(0)

    filename = os.path.basename(file_path)
    if not filename.endswith('.md'):
        sys.exit(0)

    # Read the content being written
    content = data.get('tool_input', {}).get('content', '')
    if not content:
        # For Edit, try new_string
        content = data.get('tool_input', {}).get('new_string', '')
    if not content:
        # Can't validate — allow (conservative)
        sys.exit(0)

    rule_ids = extract_rule_ids_from_content(content)
    if not rule_ids:
        sys.exit(0)

    prefix_index = load_rule_prefix_index(project_root)
    unregistered = []
    for rid in rule_ids:
        prefix = extract_prefix(rid)
        if prefix not in prefix_index:
            unregistered.append((rid, prefix))

    if not unregistered:
        sys.exit(0)

    # Format error message
    prefix_list = sorted(set(p[1] for p in unregistered))
    rule_list = sorted(set(p[0] for p in unregistered))

    lines = [
        "\n[EngineGuard] 未注册的规则 ID 前缀被拦截。",
        f"  文件: {file_path}",
        f"  未注册规则: {', '.join(rule_list)}",
        f"  未注册前缀: {', '.join(prefix_list)}",
        "",
        "  修复方式 (任选其一):",
    ]
    for prefix in prefix_list:
        lines.append(
            f'    在 engineering.json rulePrefixIndex 中添加: '
            f'"{prefix}": {{"category": "...", "owner": "...", "status": "active"}}'
        )
    lines.append("")
    lines.append("  engineering.json 位置: openspec/specs/engineering/engineering.json")
    lines.append("  如需新增跨项目通用前缀，建议先与架构 Owner 确认。")
    lines.append("")

    print('\n'.join(lines), file=sys.stderr)
    sys.exit(2)


if __name__ == '__main__':
    main()
