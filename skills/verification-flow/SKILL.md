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
5. 子 Agent 将结果写入 `09_验证结果.md`（含覆盖率矩阵、命令执行结果、评估结论、缺口清单）。
6. 按 profile 选择深度：
   - minimal：test-planner 覆盖率核对可选，只执行目标测试命令。
   - standard：必须覆盖率核对 + 全量测试。
   - strict：standard + 安全/数据库/回滚相关检查。
7. 前端改动同时使用 `frontend-verification-flow`，浏览器验证结果也写入 `09_验证结果.md`。
8. 处理验证结论：
   - 评估结论"充分"且无 P0/P1 失败 → 进入 Completion Audit（见下方 "Completion Audit" 节）。
   - 评估结论"不充分"或有 P0/P1 失败 → 执行以下步骤后进入修复循环：
     a. 从 `09_验证结果.md` 的 `## N. 修复上下文` 节提取 `<!-- fix_context_start -->` 和 `<!-- fix_context_end -->` 之间的内容。
     b. 将提取内容注入 `.workflow_state` 的 `resume_context` 字段，同时更新 `current_task` 为"修复验证缺口"、`next_action` 为对应 L1/L2 操作。
     c. 进入修复循环（参见 `rules/workflow/verification-loop.md`）。

## Completion Audit（完成审计）

测试通过 ≠ 任务完成。Completion Audit 验证的是"任务是否真的完成了"。

审计由主控 Agent 执行（meta-check，不需要新 Agent）。如果 `.workflow_state` 中 `ralph.enabled=true`，审计为强制执行；否则为标准检查（不阻断但记录缺口）。

**minimal profile 跳过此节**——minimal 不执行全量验证，没有 `02_工程需求规格.md`，审计无输入数据。如果 ralph 触发条件与 minimal 同时满足，先升级到 standard。

### 审计触发条件

以下任一条件满足时，`ralph.enabled` 自动设为 true：
- profile 为 strict
- 用户说"必须完成""不要停""ralph""做完为止"
- 任务涉及安全/金钱/订单/数据迁移/并发/外部集成

### 审计检查清单

#### A. 需求覆盖审计（强制）

- [ ] 逐条读取 `02_工程需求规格.md` 中的 REQ-xxx
- [ ] 每条 REQ 映射到具体的文件/测试/命令行证据（查 `09_验证结果.md` 的覆盖率矩阵）
- [ ] 标记为"本次不实现"的 REQ 是否有用户确认证据
- [ ] 标记未覆盖的 REQ → 写入 `OPEN_ISSUES.md`

#### B. 范围缩减检测（强制）

- [ ] 对比 `07_实施计划.md` 的任务清单 vs 实际 `git diff --stat` 改动
- [ ] 检查是否有"先跳过""TODO""FIXME""HACK""暂时"标记
- [ ] 检查是否有注释掉的代码块（`git diff` 中以 `-//` 或 `-/*` 开头的大段删除不算）
- [ ] 检查是否有计划中的任务被无声跳过（task_stack 中非 completed 但在 diff 中无对应改动）

#### C. TODO 清零（强制）

- [ ] `git diff` 中无新增 TODO/FIXME/HACK（允许已存在的）
- [ ] `task_stack` 全部 completed 或标记为"用户确认不做"
- [ ] `PENDING_DECISIONS.md` 中无阻塞项

#### D. 边界条件覆盖（标准）

- [ ] 检查测试是否覆盖了失败路径（不只是 happy path）
- [ ] 检查 `08_验证计划.md` 中标记的"无法自动化"项是否有手动验证记录
- [ ] 检查空值、边界值、异常输入是否处理

#### E. 去冗余检查（ralph deep 模式，可选）

- [ ] 无未使用的 import
- [ ] 无注释掉的代码块（非文档性注释）
- [ ] 无过度抽象（3 行逻辑包装成 10 行 helper）

### 审计结果处理

- **全部通过** → 更新 `.workflow_state`：`ralph.completion_audit_passed=true`，`ralph.audit_history` 追加 PASSED 记录。进入 review 阶段。
- **有未覆盖 REQ 或范围缩减**：
  - **ralph 模式**（`ralph.enabled=true`）：更新 `.workflow_state`：`ralph.completion_audit_passed=false`，`ralph.iteration += 1`，`ralph.audit_history` 追加 FAILED 记录（含 uncovered_reqs 和 scope_reduction_detected）。
    - 如果 `ralph.iteration <= ralph.max_iterations`：标注缺口，按下方"回到 coding 机制"执行。
    - 如果 `ralph.iteration > ralph.max_iterations`：更新 `.workflow_state` 设 `state=blocked`，写 `PENDING_DECISIONS.md` 记录所有未覆盖 REQ，人工介入。
  - **非 ralph 模式**：记录未覆盖 REQ 到 `OPEN_ISSUES.md`，写风险提示，**不阻断**进入 review。
- **仅边界条件/去冗余未通过** → 记录到 `OPEN_ISSUES.md`，不阻断进入 review。

### 回到 coding 机制

当 Completion Audit 不通过需要回到 coding 时，主控 Agent 执行：

1. 更新 `.workflow_state`：
   - `current_phase=coding`
   - `current_task="修复 Completion Audit 缺口"`
   - `resume_context`：精炼描述具体缺口（"REQ-003 无对应测试证据，REQ-005 在 diff 中无对应改动"）
   - `task_stack`：追加一个修复任务，列出每条未覆盖 REQ 和范围缩减项
2. 在 `OPEN_ISSUES.md` 中记录审计失败的具体项
3. 回到 `product-to-test-flow` 的 coding 阶段，**只补充缺口部分**（不重做已完成的实现）
4. 补充完成后重新走 verification → Completion Audit 完整流程

### Audit History 格式

`.workflow_state` 的 `ralph.audit_history` 数组每项：

```yaml
- iteration: 1
  result: FAILED
  uncovered_reqs: ["REQ-003", "REQ-005"]
  scope_reduction_detected: true
  scope_reduction_detail: "07_实施计划.md 任务 4（异常处理）在 diff 中无对应改动"
  timestamp: "2026-05-14T15:30:00"
```

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
