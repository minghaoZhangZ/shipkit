---
name: completion-audit-flow
description: Use after verification passes, before review. Audits whether the task is truly complete — checks REQ coverage, scope reduction, TODO zero-clear, and boundary conditions.
---

# Completion Audit Flow

独立的完成审计 gate。在 test-planner 验证通过后、code-reviewer 启动前执行。

核心问题："测试通过了，但东西真的做完了吗？"

## 前提条件

- verification 阶段已完成，`09_验证结果.md` 存在且含 test-planner 评估结论标记。
- **minimal profile 跳过本阶段**——minimal 不产出 `02_工程需求规格.md`，审计无输入数据。

## 执行方式

审计由主控 Agent 执行（meta-check，不需要新 Agent）。审计必须**对照文档逐条执行**，不得凭记忆判断。如果 `.workflow_state` 中 `ralph.enabled=true`，审计为强制执行；否则为标准检查（只查不阻断）。

## 输入

读取 `<change-dir>/CONTEXT_PACKAGE.md`，验证以下输入存在且满足最小内容判据：

| 文件 | 必需性 | 最小内容判据 |
|------|--------|-------------|
| `02_工程需求规格.md` | required | "验收标准"节存在且至少含 1 个 REQ-xxx 标记 |
| `07_实施计划.md` | required | "允许修改的文件范围"节存在且非空 |
| `08_验证计划.md` | required | "单元测试用例"节存在且非空 |
| `09_验证结果.md` | required | 含 test-planner 评估结论标记（"评估结论: 充分" 或 "评估结论: 不充分"） |
| `.workflow_state` | required | 含 ralph 字段 |

## 审计步骤

### A. 需求覆盖审计（强制）

- 从 `02_工程需求规格.md` 提取所有 REQ-xxx 编号。
- 从 `09_验证结果.md` 的覆盖率矩阵查找每条 REQ 的对应行。
- 每条 REQ 必须映射到具体的测试证据（覆盖率矩阵中状态为"已实现"）。
- 标记为"本次不实现"的 REQ 是否有用户确认证据（在 `02_工程需求规格.md` 或 `PENDING_DECISIONS.md` 中）。
- 未覆盖的 REQ → 记录到审计结果。

### B. 范围缩减检测（强制）

- 从 `07_实施计划.md` 提取任务清单。
- 执行 `git diff --stat origin/master...HEAD`（或 `git diff --stat HEAD~1`）。
- 逐任务对比：计划中的任务是否有对应文件改动？
- 检查是否有"先跳过""TODO""FIXME""HACK""暂时"标记。
- 检查是否有注释掉的代码块（`git diff` 中以 `-//` 或 `-/*` 开头的大段删除不算）。
- 被无声跳过的任务 → 记录到审计结果。

### C. TODO 清零（强制）

- 执行 `git diff`，扫描所有新增行（以 `+` 开头）。
- 含 TODO / FIXME / HACK 关键字 → 记录到审计结果。
- 已存在的 TODO（`git diff` 中以空格开头）不算。

### D. 边界条件覆盖（标准）

- 检查测试是否覆盖失败路径（不只是 happy path）。
- 检查 `08_验证计划.md` "无法自动化项与人工验证"节是否有手动验证记录。
- 检查空值、边界值、异常输入是否有对应用例。

### E. 去冗余检查（ralph deep 模式，可选）

- 未使用的 import（仅 ralph deep 模式检查）。
- 注释掉的代码块（非文档性注释）。
- 过度抽象（3 行逻辑包装成 10 行 helper）。

## 审计结果处理

### 全部通过（A/B/C 全绿）

- 更新 `.workflow_state`：`ralph.completion_audit_passed=true`。
- `ralph.audit_history` 追加 PASSED 记录。
- 返回 PASS，进入 review。

### 有未覆盖 REQ 或范围缩减（A/B 不过）

**ralph 模式**（`ralph.enabled=true`）：

- 更新 `.workflow_state`：
  - `ralph.completion_audit_passed=false`
  - `ralph.iteration += 1`
  - `current_phase=coding`
  - `current_task="修复 Completion Audit 缺口"`
  - `resume_context`：精炼描述具体缺口（如"REQ-003 无对应测试证据，REQ-005 在 diff 中无对应改动"）
  - `task_stack` 追加修复任务，列出每条未覆盖 REQ 和范围缩减项
  - `ralph.audit_history` 追加 FAILED 记录（含 `uncovered_reqs`、`scope_reduction_detected`、`scope_reduction_detail`、`timestamp`）
- 在 `OPEN_ISSUES.md` 记录审计失败项。
- 返回 FAIL，主控 Agent 回到 coding 阶段**只补充缺口**（不重做已完成实现）。
- 补充完成后重新走 verification → audit 完整流程。
- 如果 `ralph.iteration > ralph.max_iterations`：更新 `.workflow_state` 设 `state=blocked`，写 `PENDING_DECISIONS.md`，强制停止，人工介入。

**非 ralph 模式**：

- 记录未覆盖 REQ 到 `OPEN_ISSUES.md`。
- 写风险提示。
- 返回 WARN，**不阻断**进入 review。

### 仅边界条件/去冗余未通过（仅 D/E 不过）

- 记录到 `OPEN_ISSUES.md`。
- 不阻断进入 review（无论 ralph 模式）。

## 输出

审计结果写入 `<change-dir>/COMPLETION_AUDIT.md`：

```markdown
# Completion Audit 结果

## 审计执行信息
- 执行时间
- 审计轮次 (ralph.iteration)
- Ralph 模式: 是 / 否

## A. 需求覆盖审计
| REQ ID | 覆盖率矩阵状态 | 测试证据 | 结论 |
|--------|-------------|---------|------|

## B. 范围缩减检测
| 计划任务 | git diff 状态 | 结论 |
|---------|-------------|------|

## C. TODO 清零
| 文件 | 行内容 | 结论 |
|------|--------|------|

## D. 边界条件

## E. 去冗余

## 审计结论
- 结果: PASS / FAIL / WARN
- 未覆盖 REQ: [...]
- 范围缩减: 有 / 无
- 回 coding 指令: (仅 FAIL 时)
```

## Audit History 格式

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

## Red Flags

- "应该都做了吧"
- "我记得每个 REQ 都有对应测试"
- "不读文档了，凭记忆判断"
- 跳过 git diff 直接说"看起来没缩减范围"

出现这些想法时，必须回到真实审计流程：打开每份文档、运行 git diff、逐条对照。
