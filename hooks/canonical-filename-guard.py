#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PreToolUse hook: block AI doc writes with non-canonical filenames.

Only checks Markdown and JSON files under openspec/changes/<id>/ai/.
Canonical names per product-to-test-flow document standard.
"""

import json
import os
import re
import sys
from pathlib import Path

# Canonical document names for openspec/changes/<id>/ai/.
CANONICAL_NAMES = {
    # Core AI documents (Chinese canonical names).
    "00_原始需求.md",
    "01_PRD产品需求.md",
    "02_工程需求规格.md",
    "03_代码库调研.md",
    "04_后端方案说明.md",
    "05_前端方案说明.md",
    "06_接口与数据契约.md",
    "07_实施计划.md",
    "08_验证计划.md",
    "09_验证结果.md",
    "10_自查报告.md",       # deprecated but recognized
    "11_审查报告.md",
    "12_发布说明.md",
    "13_经验沉淀.md",
    "14_Agent评估.md",
    # Meta files.
    "CONTEXT_PACKAGE.md",
    "PENDING_DECISIONS.md",
    "CHANGE_METRICS.json",
    "OPEN_ISSUES.md",
    "COMPLETION_AUDIT.md",
    ".workflow_state",
    # Legacy English names — allowed for reading, blocked for new writes.
    # Listed here so the error message can suggest the canonical alternative.
}

LEGACY_TO_CANONICAL = {
    "00_REQUIREMENT.md":         "00_原始需求.md",
    "01_PRODUCT_DISCOVERY.md":   "01_PRD产品需求.md",
    "02_SPEC.md":                "02_工程需求规格.md",
    "03_CODEBASE_RESEARCH.md":   "03_代码库调研.md",
    "04_BACKEND_DESIGN.md":      "04_后端方案说明.md",
    "05_FRONTEND_DESIGN.md":     "05_前端方案说明.md",
    "06_DATA_CONTRACT.md":       "06_接口与数据契约.md",
    "07_IMPLEMENTATION_PLAN.md": "07_实施计划.md",
    "08_TEST_PLAN.md":           "08_验证计划.md",
    "09_TEST_RESULT.md":         "09_验证结果.md",
    "10_SELF_REVIEW.md":         "10_自查报告.md",
    "10_REVIEW_REPORT.md":       "11_审查报告.md",
    "11_REVIEW_REPORT.md":       "11_审查报告.md",
    "11_RELEASE_NOTE.md":        "12_发布说明.md",
    "12_LESSONS_LEARNED.md":     "13_经验沉淀.md",
    "13_AGENT_EVAL.md":          "14_Agent评估.md",
    "09_WORKFLOW_SUMMARY.md":    None,  # no canonical equivalent
    "BUGFIX.md":                 "OPEN_ISSUES.md",
}


def find_project_root(cwd: str) -> str:
    p = Path(cwd).resolve()
    for parent in [p] + list(p.parents):
        if (parent / ".claude").is_dir() or (parent / "openspec").is_dir():
            return str(parent)
    return cwd


def is_ai_subdir(file_path: str, project_root: str) -> bool:
    """Check if the file is under openspec/changes/<id>/ai/."""
    normalized = str(Path(file_path).resolve())
    ai_base = str((Path(project_root) / "openspec" / "changes").resolve())
    try:
        rel = os.path.relpath(normalized, ai_base)
    except ValueError:
        return False
    parts = rel.replace("\\", "/").split("/")
    # rel should be like "<change-id>/ai/<filename>"
    return len(parts) >= 3 and parts[1] == "ai"


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, IOError):
        return 0

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        return 0

    cwd = data.get("cwd", os.getcwd())
    project_root = find_project_root(cwd)
    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        return 0

    if not is_ai_subdir(file_path, project_root):
        return 0

    filename = os.path.basename(file_path)

    # Allow non-md, non-json files (e.g., images, scripts).
    if not (filename.endswith(".md") or filename.endswith(".json")):
        return 0

    if filename in CANONICAL_NAMES:
        return 0

    suggestion = ""
    if filename in LEGACY_TO_CANONICAL:
        canonical = LEGACY_TO_CANONICAL[filename]
        if canonical:
            suggestion = f" 请使用 canonical 名: {canonical}"
        else:
            suggestion = " 该文件名无对应 canonical 名，请使用当前文档标准中的文件名。"
    else:
        suggestion = (
            " 文件名不在 canonical 白名单中。"
            " 如需新增文档类型，请先更新 product-to-test-flow 中的文档标准。"
        )

    print(
        "\n[CanonicalFilenameGuard] 非 canonical 文件名被拦截。\n"
        f"  文件: {file_path}\n"
        f"  文件名: {filename}\n"
        f"{suggestion}\n"
        "\nCanonical 文件名列表参见 product-to-test-flow SKILL.md 文档标准节。\n",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
