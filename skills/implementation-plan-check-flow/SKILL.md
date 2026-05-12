---
name: implementation-plan-check-flow
description: Use when confirmed requirements, designs, and contracts need a scoped implementation plan and verification plan before coding.
---

# Implementation Plan Check Flow

目标：生成 `07_实施计划.md` 和 `08_验证计划.md`，并获得开工确认。这里不再评审方案，只确认能否安全开工。

## 输入

必读：

- `CONTEXT_PACKAGE.md`
- `02_工程需求规格.md`
- `03_代码库调研.md`
- 已确认的 `04_后端方案说明.md`（如适用）
- 已确认的 `05_前端方案说明.md`（如适用）
- 已确认的 `06_接口与数据契约.md`（如适用）

## 执行

1. 检查 `required_checkpoints` 均在 `confirmed_checkpoints` 中。
2. 检查 `PENDING_DECISIONS.md` 无 pending 项。
3. 更新 `CONTEXT_PACKAGE.md`，`current_phase=plan`，填写 Input Manifest。
4. 调用 `implementation-planner` 输出 `07_实施计划.md`。返回后检查 Pre-mortem 校验通过标记；失败则补全输入重新调用。
5. 调用 `test-planner` 输出 `08_验证计划.md`。返回后检查 Pre-mortem 校验通过标记；失败则补全输入重新调用。
6. 校验 Req ID 在计划和验证中均有覆盖。
7. 设置 checkpoint：

```yaml
checkpoint: plan_confirmation
requires_user_confirmation: true
user_confirmed: false
confirmation_type: approve_implementation_plan
confirmation_role: engineering_owner
confirmation_docs: ["07_实施计划.md", "08_验证计划.md"]
```

8. 用 `AskUserQuestion` 请求研发负责人确认。

## 输出合同

`07_实施计划.md` 必须包含：

- 总体策略
- 任务拆分
- 后端任务
- 前端任务
- 数据与契约任务
- 测试任务
- 允许修改文件范围
- 不允许修改文件
- 依赖关系
- 停止条件
- 顺带重构受控出口
- `Req ID 覆盖映射`
- `已读输入`、`引用证据`、`未覆盖项`、`下游依赖`

`08_验证计划.md` 必须包含：

- 验证范围
- 已发现的测试命令
- 单元、集成、API、前端、E2E、回归用例
- 浏览器验证路径（前端受影响时）
- 无法自动化项和人工验证步骤
- `Req ID 覆盖映射`

## 停止条件

- 必需 checkpoint 未确认。
- 存在 pending 决策。
- Req ID 在实施或验证中未覆盖。
- 允许修改文件范围缺失。
- 测试无法运行且没有替代验证方式。
