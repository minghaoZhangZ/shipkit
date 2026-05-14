---
name: resume-flow
description: Use when session context is lost (/clear, /compact, new session) and workflow progress needs to be recovered from .workflow_state.
---

# Resume Flow

从 `.workflow_state` 和 `CONTEXT_PACKAGE.md` 恢复工作流进度。

## 触发场景

- 会话开始且存在活跃的 `.workflow_state`
- 用户执行 `/clear` 或 `/compact` 后
- 用户明确要求恢复进度

## 恢复步骤

### Step 1: 定位 change

1. 搜索 `openspec/changes/*/ai/.workflow_state`，排除 archive。
2. 按修改时间排序，取最新。
3. 确定 `<change-dir>`。

### Step 2: 读取状态

1. 解析 `.workflow_state`。
2. 读取 `<change-dir>/ai/CONTEXT_PACKAGE.md`。
3. 列出 `<change-dir>/ai/` 下已有文档。

### Step 3: 状态验证

**首先检查 `state` 字段**：

- `state=active` → 正常恢复，继续后续步骤。
- `state=blocked` → 输出"此 change 已被阻塞"，列出 PENDING_DECISIONS.md 中的阻塞项，提示用户处理。**不自动继续工作**，等待用户解除阻塞或将 `state` 改回 `active`。
- `state=failed` → 输出"此 change 已放弃，不可恢复"，建议创建新 change。
- `state=finished` → 输出"此 change 已完成"，建议归档。
- 无 `state` 字段 → 视为 `active`（向后兼容）。

**一致性检查**：
- `.workflow_state` 中的 `current_phase` 与已有 AI 文档是否匹配。
- `task_stack` 中的 `completed` 任务是否有对应产出。
- `phase_history` 是否与已有文档一致。
- 如果发现不一致：记录到恢复报告，以 `.workflow_state` 为准。

### Step 4: 检查 pending 决策

1. 读取 `<change-dir>/ai/PENDING_DECISIONS.md`（如存在）。
2. 如果有 pending 项且 `pending_decisions_count > 0`：提示用户先处理。

### Step 5: 检查 checkpoint

1. 如果 `requires_user_confirmation=true` 且 `user_confirmed=false`：
   - 输出当前 checkpoint 信息。
   - 用 `AskUserQuestion` 请求确认。
   - 确认后更新 `.workflow_state`。
2. 如果所有 required checkpoints 已确认：直接进入 Step 6。

### Step 6: 输出恢复摘要

```markdown
# 工作流恢复

- Change: <change-id>
- Profile: <profile>
- 当前阶段: <current_phase>
- 当前任务: <current_task>
- 已完成: <last_completed_task>
- 下一步: <next_action>
- 待完成任务:
  - [ ] task-1
  - [ ] task-2
- 已确认 checkpoint: <confirmed_checkpoints>
- 待确认 checkpoint: <未确认的>
- 已产出文档: <已有文档列表>
- 缺失文档: <应有但缺失的>
- Pending 决策: <数量>
```

### Step 7: 继续工作

根据 `resume_context` 和 `next_action` 直接继续执行，不再等待用户确认（除非有 pending checkpoint）。

## 边界情况

### 多个活跃 change

如果存在多个非归档的 `.workflow_state`：
1. 列出所有活跃 change 的 `change_id`、`current_phase`、`updated_at`。
2. 让用户选择要恢复哪个。
3. 默认选最近更新的。

### 状态文件损坏

1. 输出损坏的具体字段。
2. 尝试从 `CONTEXT_PACKAGE.md` 和已有 AI 文档推断当前阶段。
3. 提示用户手动确认。

### 无活跃 change

静默退出，不干扰正常对话。

### minimal profile

minimal 的 task_stack 可以更简单（3-5 个 task），不强制 phase_history。

### 旧 change 兼容

如果 `.workflow_state` 缺少 `schema_version` 字段或其值不在已知版本列表中（当前仅 `1.0`），Hook 会 fail-closed 阻断业务操作。此时需运行 `migrate-workflow-state.py` 将旧 state 升级到当前版本，或手动补齐 `schema_version: "1.0"` 及 Hook 所需的必填字段。

如果 `.workflow_state` 已有 `schema_version: "1.0"` 但缺少 `task_stack`、`resume_context`、`phase_history` 等任务级跟踪字段：
1. 降级为仅从 `CONTEXT_PACKAGE.md` 和已有 AI 文档推断当前进度。
2. 输出降级提示："旧版 .workflow_state 缺少 task 级跟踪字段，已从已有文档推断当前进度。"
3. 建议用户确认当前阶段和下一步。
