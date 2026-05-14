---
name: openspec-new-change
description: Use when starting a new requirement, feature, bugfix, refactor, security fix, data migration, performance task, or test task that needs an OpenSpec change workspace.
---

# OpenSpec New Change

## Change ID

格式：

```text
<yyyy-mm-dd>-<type>-<domain>-<中文动作>
```

示例：

```text
2026-05-12-feature-order-增加库存锁定校验
2026-05-12-bugfix-ui-修复列表重复提交
```

## Flow

1. 根据需求生成 `<change-id>`。
2. 确保 OpenSpec 基础目录存在：

```text
openspec/changes/archive
openspec/specs
openspec/_templates/change
openspec/_templates/ai
```

3. 创建 change 目录：

```text
openspec/changes/<change-id>/ai
openspec/changes/<change-id>/specs
```

4. 创建或更新 `metadata.json`：

```json
{
  "id": "<change-id>",
  "title": "<需求标题>",
  "type": "<type>",
  "domain": "<domain>",
  "action": "<中文动作>",
  "status": "draft",
  "createdAt": "YYYY-MM-DD",
  "profile": "minimal|standard|strict",
  "owner": "minghao"
}
```

5. 将原始需求写入 `<change-dir>/ai/00_原始需求.md`。
6. 初始化 `<change-dir>/ai/CONTEXT_PACKAGE.md`。
7. 初始化 `<change-dir>/ai/.workflow_state`，使用以下完整 schema（新字段初始化为空）。所有 AI 文档统一使用中文 canonical 名。

```yaml
schema_version: "1.0"
change_id: "<change-id>"
profile: minimal
current_phase: requirement
state: active
current_task: ""
last_completed_task: ""
next_action: ""
task_stack: []
phase_history: []
resume_context: ""
checkpoint: ""
requires_user_confirmation: false
user_confirmed: true
confirmation_type: ""
confirmation_role: ""
confirmation_docs: []
confirmed_checkpoints: []
required_checkpoints: []
affected_areas: []
context_package: "CONTEXT_PACKAGE.md"
trace_matrix_status: pending
round: 0
max_rounds: 3
pending_decisions_count: 0
project_consistency_enabled: false
engineering_manifest: ""
engineering_mode: "off"
verification_mode: "independent"
metrics_mode: "change_only"
sop_mode: "candidate_only"
consistency_review_required: false
architecture_owner_required: false
verification_status: "pending"
verification_issue_count: 0
metrics_recorded: false
created_at: "<YYYY-MM-DD>"
updated_at: "<YYYY-MM-DD>"
```

## 下一步

- 常规需求：调用 `product-to-test-flow`
- 高风险需求：调用 `strict-product-to-test-flow`
- 小修复：调用 `quick-fix-flow`

## Type Values

```text
feature
bugfix
hotfix
refactor
techdebt
perf
security
data
docs
test
```

## Status Values

```text
draft
planning
approved
implementing
verifying
reviewing
done
archived
```
