"""Initialize optional project-level engineering consistency templates.

This script is intentionally conservative:
- It refuses to write under global AI config directories such as .claude/.codex.
- It creates missing files only and never overwrites existing project content.
- The default manifest keeps Enhanced Flow disabled until the team opts in.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


MARKERS = (".git", "pom.xml", "build.gradle", "package.json", "openspec", "README.md")
GLOBAL_CONFIG_NAMES = {".claude", ".codex"}
TEMPLATE_FILES = (
    "engineering.json",
    "00-总则/行为准则.md",
    "00-总则/需求澄清与上下文规则.md",
    "10-编码规范/Java后端编码规范.md",
    "10-编码规范/Spring事务与并发规范.md",
    "10-编码规范/SQL与数据库规范.md",
    "10-编码规范/前端编码与交互规范.md",
    "10-编码规范/API契约与DTO-VO规范.md",
    "10-编码规范/通用空值与equals规范.md",
    "20-架构规范/分层架构规范.md",
    "20-架构规范/模块边界规范.md",
    "20-架构规范/依赖方向规范.md",
    "20-架构规范/领域概念与命名规范.md",
    "20-架构规范/可复用能力规范.md",
    "30-质量与验证/单元测试规范.md",
    "30-质量与验证/验证命令与测试证据规范.md",
    "30-质量与验证/代码审查清单.md",
    "30-质量与验证/禁止模式清单.md",
    "40-交付流程/需求拆解规范.md",
    "40-交付流程/实施计划规范.md",
    "40-交付流程/变更范围控制规范.md",
    "40-交付流程/发布与回滚规范.md",
    "50-经验沉淀/SOP注册表.md",
    "50-经验沉淀/问题复盘规范.md",
    "50-经验沉淀/指标台账.jsonl",
)


def is_global_config_path(path: Path) -> bool:
    return any(part.lower() in GLOBAL_CONFIG_NAMES for part in path.resolve().parts)


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if any((candidate / marker).exists() for marker in MARKERS):
            return candidate

    return current


def validate_manifest(path: Path) -> list[str]:
    errors: list[str] = []
    data = json.loads(path.read_text(encoding="utf-8"))

    expected = {
        "enabled": False,
        "mode": "advisory",
        "status": "draft",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            errors.append(f"engineering.json default {key!r} should be {value!r}")

    return errors


def initialize(target: Path, dry_run: bool = False) -> dict[str, object]:
    script_path = Path(__file__).resolve()
    claude_home = script_path.parents[1]
    template_dir = claude_home / "templates" / "engineering"
    project_root = find_project_root(target)

    if is_global_config_path(project_root):
        raise RuntimeError(
            f"Refusing to initialize engineering facts under global config path: {project_root}"
        )

    missing_templates = [name for name in TEMPLATE_FILES if not (template_dir / name).exists()]
    if missing_templates:
        raise RuntimeError(f"Missing template files: {', '.join(missing_templates)}")

    destination = project_root / "openspec" / "specs" / "engineering"
    created: list[str] = []
    skipped: list[str] = []

    if not dry_run:
        destination.mkdir(parents=True, exist_ok=True)

    for name in TEMPLATE_FILES:
        source = template_dir / name
        target_file = destination / name
        if target_file.exists():
            skipped.append(str(target_file))
            continue
        created.append(str(target_file))
        if not dry_run:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target_file)

    manifest_errors: list[str] = []
    manifest_path = destination / "engineering.json"
    if dry_run:
        manifest_errors = validate_manifest(template_dir / "engineering.json")
    elif manifest_path.exists():
        manifest_errors = validate_manifest(manifest_path)

    return {
        "projectRoot": str(project_root),
        "engineeringDir": str(destination),
        "created": created,
        "skipped": skipped,
        "dryRun": dry_run,
        "manifestErrors": manifest_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create openspec/specs/engineering templates for a project."
    )
    parser.add_argument(
        "--target",
        default=".",
        help="Project directory or subdirectory. Defaults to current working directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be created without writing files.",
    )
    args = parser.parse_args()

    try:
        result = initialize(Path(args.target), dry_run=args.dry_run)
    except Exception as exc:  # noqa: BLE001 - CLI should surface concise failures.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
