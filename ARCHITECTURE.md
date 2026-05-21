# Claude Workflow Architecture

This directory defines a Claude Code workflow system with role-based checkpoints, skills, agents, rules, and hooks.

## Main Shape

`CLAUDE.md` routes user intent to one of four workflow families, selected by risk profile:

| Intent | Workflow | Profile |
|--------|----------|---------|
| New feature, product behavior change | `product-to-test-flow` | standard / strict |
| Small bug, narrow fix (≤3 files, no contract change) | `quick-fix-flow` | minimal |
| Security, money, orders, migration, concurrency, external integration | `strict-product-to-test-flow` | strict |
| Build/lint/test error repair | `build-fix-flow` | — |
| Code review (PR/post-change) | `review-flow` | — |
| Delivery learning extraction | `learn-from-delivery` | learning |

## Change Workspace

`openspec-new-change` creates the change directory:

```
openspec/changes/<change-id>/
openspec/changes/<change-id>/specs/
```

`<change-id>` format: `<yyyy-mm-dd>-<type>-<domain>-<中文动作>`

Initial files: `00_原始需求.md`, `CONTEXT_PACKAGE.md`, `.workflow_state`, `metadata.json`.

## Canonical AI Documents

All new changes use Chinese canonical names. English legacy names are blocked for new writes by `canonical-filename-guard.py`.

| Purpose | File | Status |
|---|---|---|
| Raw requirement | `00_原始需求.md` | active |
| Product PRD | `01_PRD产品需求.md` | active |
| Engineering spec | `02_工程需求规格.md` | active |
| Codebase research | `03_代码库调研.md` | active |
| Backend design | `04_后端方案说明.md` | active |
| Frontend design | `05_前端方案说明.md` | active |
| API/data contract | `06_接口与数据契约.md` | active |
| Implementation plan | `07_实施计划.md` | active |
| Verification plan | `08_验证计划.md` | active |
| Verification result | `09_验证结果.md` | active |
| Review report | `11_审查报告.md` | active |
| Release note | `12_发布说明.md` | active |
| Lessons learned | `13_经验沉淀.md` | active |
| Agent evaluation | `14_Agent评估.md` | active |

Meta files (sibling to numbered docs): `CONTEXT_PACKAGE.md`, `PENDING_DECISIONS.md`, `CHANGE_METRICS.json`, `OPEN_ISSUES.md`, `COMPLETION_AUDIT.md`, `.workflow_state`.

`10_自查报告.md` is deprecated — coverage checking moved to test-planner verification mode, judgment checks moved to review phase.

## `.workflow_state` Schema

Versioned with `schema_version: "1.0"`. The `checkpoint-guard.py` and `scope-guard.py` hooks fail-closed on unknown or missing versions. Old states must be migrated with `scripts/migrate-workflow-state.py`.

Key fields: `schema_version`, `change_id`, `profile`, `current_phase`, `current_task`, `task_stack`, `phase_history`, `resume_context`, `checkpoint`, `requires_user_confirmation`, `user_confirmed`, `confirmed_checkpoints`, `required_checkpoints`.

## Role Checkpoints

| Checkpoint | Role | Document |
|---|---|---|
| `prd_confirmation` | Product / business owner | `01_PRD产品需求.md` |
| `engineering_spec_confirmation` | Tech lead | `02_工程需求规格.md` |
| `backend_design_confirmation` | Backend owner | `04_后端方案说明.md` |
| `frontend_design_confirmation` | Frontend owner | `05_前端方案说明.md` |
| `contract_confirmation` | Frontend + backend owners | `06_接口与数据契约.md` |
| `plan_confirmation` | Engineering owner | `07_实施计划.md`, `08_验证计划.md` |

Standard/strict profiles enforce all applicable checkpoints before coding. Minimal skips checkpoints.

Checkpoint enforcement: `checkpoint-guard.py` blocks business-code edits and build/test commands while a checkpoint is pending. Only AI docs under `openspec/changes/*/` may be written.

## Phase Routing (product-to-test-flow)

```
requirement → prd → engineering_spec → research →
backend_design → frontend_design → contract → plan →
coding → verification → completion_audit → review → delivery → archive
```

Each phase delegates to a phase skill, which calls a specialist agent to produce the canonical document. The main agent implements code during the coding phase — designers and reviewers do not modify business code.

**Verification phase**: test-planner agent runs independently in verification mode. The main agent must not run tests or interpret test output. A hard stop in `verification-flow` requires `09_验证结果.md` to contain the test-planner evaluation conclusion marker.

**Completion Audit phase** (`completion-audit-flow`): An independent gate between verification and review. It audits whether the task is truly complete — not just that tests pass. Checks REQ coverage, scope reduction, TODO zero-clear, and boundary conditions. In ralph mode, a failed audit routes back to coding without starting review; in non-ralph mode, gaps are recorded as OPEN_ISSUES but don't block review.

## Ralph Persistence Completion Loop

The ralph mode (`ralph.enabled=true` in `.workflow_state`) is an enhanced verification mode. Core philosophy: "Don't stop until done. Every iteration must have fresh evidence."

### Trigger conditions

- Profile is `strict` (auto-enable)
- User says "必须完成" / "不要停" / "ralph" / "做完为止"
- Task involves security, money, orders, data migration, concurrency, or external integration

### Key behaviors

| Dimension | Non-ralph | Ralph mode |
|-----------|-----------|------------|
| Completion Audit | Light check, non-blocking | Enforced, fail → back to coding |
| Architect Review Tier floor | STANDARD | DEEP |
| L3 failure handling | code-reviewer → human decision | code-reviewer → auto-loop |
| Max iterations | None | 10 (hard stop) |
| TODO/FIXME check | Optional | Mandatory zero-clear |
| Scope reduction detection | None | Per-item plan vs. actual diff |

### State fields

```yaml
ralph:
  enabled: false
  iteration: 0
  max_iterations: 10
  completion_audit_passed: false
  architect_tier: STANDARD
  context_snapshot_path: ""
  audit_history: []
```

## Context Package

Each phase updates `CONTEXT_PACKAGE.md`. Subagents must read it first. It declares: current phase, required inputs, project rules, stage goal, output contract, and stop conditions.

## Context Recovery

`resume-flow` recovers workflow progress after `/clear`, `/compact`, or a new session. Reads `.workflow_state` and `CONTEXT_PACKAGE.md`, validates consistency, presents a recovery summary, and resumes from the last checkpoint.

## Hooks (PreToolUse)

Executed in order on every tool call:

| # | Hook | Matcher | Purpose |
|---|------|---------|---------|
| 1 | `canonical-filename-guard.py` | Write\|Edit\|MultiEdit | Blocks non-canonical filenames under `openspec/changes/*/` |
| 2 | `dangerous-command-guard.py` | Bash | Blocks destructive commands (rm -rf, force push, DROP TABLE, etc.) |
| 3 | `checkpoint-guard.py` | Write\|Edit\|MultiEdit\|Bash | Blocks business code edits and build/test when checkpoint is pending; blocks when state=blocked/failed |
| 4 | `scope-guard.py` | Write\|Edit\|MultiEdit | Blocks edits outside `07_实施计划.md` section 7 during coding/verification |
| 5 | `engine-guard.py` | Write\|Edit\|MultiEdit | Blocks unregistered rule ID prefixes when writing engineering spec files |

## Agents

**Specialist agents** produce documents or reports only (never modify business code):
- `product-discovery-analyst` → PRD
- `product-spec-analyst` → engineering spec
- `codebase-researcher` → codebase research
- `backend-designer` → backend design
- `frontend-designer` → frontend design
- `data-contract-designer` → contract
- `implementation-planner` → implementation plan
- `test-planner` → verification plan (plan mode) / verification execution (verify mode)
- `code-reviewer` → review report
- `java-reviewer`, `database-reviewer`, `security-reviewer`, `frontend-ux-reviewer` → design/review phase audits

**Resolver agents** fix specific failures within allowed file scope:
- `java-build-resolver` / `build-error-resolver` → build/test failures

**Main agent** implements business code during the coding phase, following `07_实施计划.md`.
