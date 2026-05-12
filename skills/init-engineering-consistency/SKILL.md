---
name: init-engineering-consistency
description: Use when the user explicitly asks to initialize the team hot-plug governance capability, project-level consistency governance, engineering facts, engineering consensus, or openspec/specs/engineering templates for the current project.
---

# Init Engineering Consistency

## Purpose

Initialize the optional project-level consistency governance scaffold in the current project.

This skill only creates templates. It must not enter product delivery, analyze a new requirement, modify business code, or enable enforced governance by default.

## Trigger

Use this skill only when the user explicitly asks for one of these intents:

- "我要走团队热插拔功能"
- "初始化团队一致性治理"
- "初始化工程事实库"
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
architecture-principles.md
dependency-rules.md
domain-concepts.md
module-boundaries.md
reusable-apis.md
forbidden-patterns.md
sop-registry.md
metrics-ledger.jsonl
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

### Markdown Files

Each markdown file is a team-editable consensus artifact. The scaffold should contain headings and examples, not final project decisions.

### metrics-ledger.jsonl

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
