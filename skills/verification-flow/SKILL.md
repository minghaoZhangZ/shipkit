---
name: verification-flow
description: Use when about to claim work is complete, write release notes, finish review, or verify significant implementation changes.
---

# Verification Flow

核心原则：验证由独立子 Agent 执行。实现者（主控 Agent）不跑测试、不判断测试结果。没有真实命令输出，就不能声称完成、通过或修复。

## 前提条件

- coding 阶段所有实施任务已完成（task_stack 全部为 completed）。
- `07_实施计划.md` 的允许文件范围已存在。
- `08_验证计划.md` 已列出命令、用例和无法自动化项。

注意：不再要求 `10_自查报告.md`（该文档已废弃）。

## 主控 Agent 角色

本阶段主控 Agent 的唯一职责是：准备上下文 → 调用 `test-planner`（验证执行模式）→ 接收结论 → 决定下一步。

主控 Agent 不运行测试命令，不解读测试输出。

## Flow

1. 更新 `CONTEXT_PACKAGE.md`，`current_phase=verification`，填写 Input Manifest（02/07/08）。
2. 调用 `test-planner`（验证执行模式）。该 agent 独立完成：
   - 覆盖率核对（测试计划 vs 实际测试代码）
   - 测试执行（运行验证命令）
   - 充分性评估（验收标准覆盖判断）
3. **硬停止检查**：验证 `test-planner` 确实被调用且产出了独立评估结论：
   - `09_验证结果.md` 必须存在。
   - 文件内容必须包含 `test-planner` 的评估结论标记（"评估结论: 充分" 或 "评估结论: 不充分"）。
   - 如果文件不存在或缺少评估结论标记 → **停止**。不得自行运行测试、不得自行判断测试结果、不得跳过此检查。重新调用 `test-planner`。
4. 子 Agent 返回后，检查输出是否包含 Pre-mortem 校验通过标记；校验失败则补全输入重新调用。
4. 子 Agent 返回后，检查输出是否包含 Pre-mortem 校验通过标记；校验失败则补全输入重新调用。
5. 子 Agent 将结果写入 `09_验证结果.md`（含覆盖率矩阵、命令执行结果、评估结论、缺口清单）。
6. 按 profile 选择深度：
   - minimal：test-planner 覆盖率核对可选，只执行目标测试命令。
   - standard：必须覆盖率核对 + 全量测试。
   - strict：standard + 安全/数据库/回滚相关检查。
7. 前端改动同时使用 `frontend-verification-flow`，浏览器验证结果也写入 `09_验证结果.md`。
8. 处理验证结论：
   - 评估结论"充分"且无 P0/P1 失败 → 进入 review 阶段。
   - 评估结论"不充分"或有 P0/P1 失败 → 进入修复循环（参见 `rules/workflow/verification-loop.md`）。

## 修复循环提醒

- 每一次修复后，必须重新调用 `test-planner` 验证模式重新执行完整三步。主控 Agent 永远不自己跑测试验证。
- L3（同组件连续两次失败）时主控 Agent 不得继续修复，切换为 `code-reviewer` 诊断。
- L4（连续三次失败）时强制停止，写 PENDING_DECISIONS，人工介入。

## Frontend Verification

如果改动涉及前端页面、组件、样式、交互、路由、权限展示、表单、表格或浏览器运行时：

1. 使用 `frontend-verification-flow`。
2. 读取 `05_前端方案说明.md` 和 `08_验证计划.md`。
3. 运行实际存在的前端命令。
4. 使用 Playwright MCP 做浏览器 smoke / acceptance 验证；`bb-browser` 仅作探索或 fallback。
5. 在 `09_验证结果.md` 记录 URL、视口、操作、预期、实际、控制台错误、未验证项和原因。

前端浏览器验证与 test-planner 的验证执行可并行，但必须在 review 阶段之前完成。

## Red Flags

- "应该可以通过"
- "看起来没问题"
- "之前跑过"
- "只改了文档不用验证"
- "测试太慢所以跳过"
- 主控 Agent 自己跑测试并声称"通过了"

出现这些想法时，必须回到真实验证流程：由独立子 Agent 跑测试，用真实命令输出说话。
