---
name: init-engineering-consistency
description: Use when the user explicitly asks to initialize the team hot-plug governance capability, project-level consistency governance, engineering facts, engineering consensus, or openspec/specs/engineering templates for the current project.
---

# Init Engineering Consistency

## Purpose

Initialize the optional project-level team engineering standards scaffold in the current project.

This skill only creates templates. It must not enter product delivery, analyze a new requirement, modify business code, or enable enforced governance by default.

## Trigger

Use this skill only when the user explicitly asks for one of these intents:

- "我要走团队热插拔功能"
- "初始化团队一致性治理"
- "初始化工程事实库"
- "初始化团队规范"
- "初始化代码规范"
- "创建 openspec/specs/engineering"
- "启用 project-level consistency governance 模板"

Do not run this skill implicitly during normal product-to-test-flow.

## Hard Rules

1. Create files only under the target project root.
2. Never create `openspec/specs/engineering` under `~/.claude`, `.claude`, `.codex`, or another global configuration directory.
3. Do not overwrite existing files. If a file already exists, report it as skipped.
4. Default manifest must be safe:
   - `enabled: false`
   - `mode: advisory`
   - `status: draft`
5. Stop after scaffolding and verification. Do not continue into delivery workflow.

## Project Root Detection

Determine the target project root before writing:

1. Prefer the current working directory if it looks like a project root.
2. Otherwise walk upward until a directory contains one of:
   - `.git`
   - `pom.xml`
   - `build.gradle`
   - `package.json`
   - `openspec`
   - `README.md`
3. If the detected path is a global AI config directory such as `.claude` or `.codex`, stop and ask the user to provide or switch to the project root.

## Files To Create

Create this directory:

```text
<project-root>/openspec/specs/engineering/
```

Create these files if missing:

```text
engineering.json
00-总则/行为准则.md
00-总则/需求澄清与上下文规则.md
10-编码规范/Java后端编码规范.md
10-编码规范/Spring事务与并发规范.md
10-编码规范/SQL与数据库规范.md
10-编码规范/前端编码与交互规范.md
10-编码规范/API契约与DTO-VO规范.md
10-编码规范/通用空值与equals规范.md
20-架构规范/分层架构规范.md
20-架构规范/模块边界规范.md
20-架构规范/依赖方向规范.md
20-架构规范/领域概念与命名规范.md
20-架构规范/可复用能力规范.md
30-质量与验证/单元测试规范.md
30-质量与验证/验证命令与测试证据规范.md
30-质量与验证/代码审查清单.md
30-质量与验证/禁止模式清单.md
40-交付流程/需求拆解规范.md
40-交付流程/实施计划规范.md
40-交付流程/变更范围控制规范.md
40-交付流程/发布与回滚规范.md
50-经验沉淀/SOP注册表.md
50-经验沉淀/问题复盘规范.md
50-经验沉淀/指标台账.jsonl
```

Use templates from:

```text
<claude-home>/templates/engineering/
```

Preferred execution:

```powershell
py <claude-home>\scripts\init-engineering-consistency.py --target <project-root>
```

For a dry run:

```powershell
py <claude-home>\scripts\init-engineering-consistency.py --target <project-root> --dry-run
```

If Python is unavailable, create equivalent files manually with the same names and sections described below.

## Template Semantics

### engineering.json

The manifest is the only activation switch for Enhanced Flow.

- `enabled=false`: normal Base Flow. The workflow must not require engineering specs.
- `enabled=true`: Enhanced Flow can read project-level facts.
- `mode=advisory`: record consistency risks but do not block archive.
- `mode=enforced`: deterministic violations can block review/archive.
- `status=draft`: facts are not approved yet; keep `enabled=false` unless the team has completed consensus.

### 中文分层目录

The scaffold is organized by how agents use the standards:

- `00-总则`: agent behavior, clarification, context rules.
- `10-编码规范`: concrete backend, frontend, SQL, API, null-safety coding standards.
- `20-架构规范`: layering, module boundaries, dependency direction, domain concepts, reusable APIs.
- `30-质量与验证`: unit tests, command evidence, review checklist, forbidden patterns.
- `40-交付流程`: requirement breakdown, implementation plan, scope control, release and rollback.
- `50-经验沉淀`: SOP registry, retrospective rules, metrics ledger.

Each markdown file is a team-editable consensus artifact. The scaffold should contain headings and examples, not final project decisions.

### 指标台账.jsonl

Initialize with a schema record only. Runtime metrics are appended later by delivery workflows when Enhanced Flow is enabled.

## Verification

After scaffolding:

1. List created files and skipped existing files.
2. Validate `engineering.json` as JSON when Python or another JSON parser is available.
3. Confirm the manifest defaults are safe:
   - `enabled=false`
   - `mode=advisory`
   - `status=draft`
4. Report the exact project path initialized.

## Final Response

Keep the final response short:

- initialized path
- created files count
- skipped files count
- reminder that Enhanced Flow is not active until the team edits `engineering.json` and sets `enabled=true`
