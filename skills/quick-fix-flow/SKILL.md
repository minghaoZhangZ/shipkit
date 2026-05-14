---
name: quick-fix-flow
description: Use when a small bug, narrow refactor, simple API adjustment, small UI fix, or focused failing test needs a lightweight workflow.
---

# Quick Fix Flow

用于 minimal profile。它不强制 PRD/设计 checkpoint，但仍必须保留代码证据、允许文件范围、自查、验证和 metrics。

## 准入条件

必须同时满足：

- 不改接口契约、数据库、权限、事务/并发、外部系统。
- 不涉及安全、金钱、订单、库存、迁移、敏感数据、不可逆操作。
- 不涉及前后端同时改。
- 产品语义清楚。
- 预计改动文件不超过 3 个。
- 可用一个目标测试或最小复现路径验证。
- 如改动需要新增测试用例，应升级到 standard（minimal 不新增测试基础设施）。

任一不满足，升级 `product-to-test-flow` 的 standard 或 strict。

## 流程

1. 写入 `<change-dir>/ai/00_原始需求.md`。
2. 创建/更新 `.workflow_state`：

```yaml
schema_version: “1.0”
change_id: “<change-id>”
profile: minimal
current_phase: plan
state: active
current_task: “”
last_completed_task: “”
next_action: “”
task_stack: []
resume_context: “”
requires_user_confirmation: false
user_confirmed: true
checkpoint: “”
confirmed_checkpoints: []
required_checkpoints: []
affected_areas: []
context_package: “CONTEXT_PACKAGE.md”
trace_matrix_status: lightweight
```

3. 更新 `CONTEXT_PACKAGE.md`，声明 minimal、输入、输出合同、停止条件；填写 Input Manifest（minimal 判据可放宽：文件存在即为通过）。
4. 执行只读代码库调研，调用 `codebase-researcher` 输出 `03_代码库调研.md`。返回后检查 Pre-mortem 校验通过标记。
5. 初始化 `task_stack`（3-5 项），输出轻量 `07_实施计划.md`，必须包含第 7 节”允许修改的文件范围”。
6. 按需输出 `08_验证计划.md`；小 UI bug 必须记录页面、组件、复现路径、视口和预期结果。
7. 更新 `.workflow_state`：`current_phase=coding`，`current_task` 为第一个实施任务，`next_action` 为具体操作。
8. 主控 Agent 只修改计划允许的文件，每完成一个 task 更新 `current_task`、`last_completed_task`、`next_action`、`resume_context`。如有测试用例，优先写测试再写实现。
9. 调用 `test-planner` 验证模式（minimal profile：覆盖率核对可选，采用渐进策略执行测试——先目标类、再相关类、必要时才全量；前端改动同时执行 `frontend-verification-flow`），产出 `09_验证结果.md`。
10. 执行轻量只读 diff review，由主控 Agent 直接对比变更和需求（不强制调用独立 reviewer）。
11. 更新 `CHANGE_METRICS.json`。
12. 输出 `12_发布说明.md`，更新 `.workflow_state`：`current_phase=delivery`。

**注意**：minimal 不再产出 `10_自查报告.md`。

## 禁止事项

- 不要因为 minimal 就跳过代码证据。
- 不要跳过 `CHANGE_METRICS.json`。
- 不要修改计划外文件。
- 不要扩大顺带重构范围。
- UI 修复不能只凭肉眼判断完成，必须记录浏览器验证路径或无法运行原因。
- 主控 Agent 不自己跑测试判断”通过了”——必须由 test-planner 验证模式执行并记录。
