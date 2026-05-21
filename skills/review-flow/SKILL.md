---
name: review-flow
description: Use when staged or unstaged changes need evidence-based review before merge, release, or handoff.
---

# Review Flow

执行只读审查流程。reviewer 不允许修改代码。

## 前置条件

需要有 `<change-dir>`，并至少存在：

- `02_工程需求规格.md`
- `07_实施计划.md`
- `08_验证计划.md`
- `09_验证结果.md`

统一使用中文 canonical 文档名。

## Architect Review Tier（架构审查分级）

审查深度由变更规模自动决定。在开始审查前，先执行 `git diff --stat origin/master...HEAD`（或 `git diff --stat HEAD~1` 如果在 master 上）计算：

| 变更规模 | Tier | 审查重点 |
|---------|------|---------|
| ≤3 文件, 净增 ≤100 行 | **STANDARD** | 代码正确性、规范合规、测试覆盖（五关）。Java 项目保留 java-reviewer。 |
| 4-20 文件 | **DEEP** | + 架构一致性、依赖方向、事务边界（五关 + 架构专项） |
| >20 文件 或 安全/DB/并发变更 或 **strict profile** | **THOROUGH** | + 安全审查、DB 审查、回滚方案（全六关 + 全部专项 reviewer） |

**ralph 模式 floor**：如果 `.workflow_state` 中 `ralph.enabled=true`，最小审查级别为 **DEEP**（即使是小改动）。**strict profile 始终为 THOROUGH**（不受 floor 影响，是固定要求）。

Tier 决定后写入 `11_审查报告.md` 的审查总览中。

## 工作流

1. 检查 `.workflow_state` 中 `ralph.enabled` 是否为 true。如是，审查 floor 为 DEEP。
2. 计算变更规模（`git diff --stat`），结合 ralph floor 确定 Architect Review Tier。
3. 查看 `git status` 和 `git diff`，或等价的变更证据。
4. 阅读相关 `<change-dir>/` 文档和 `CONTEXT_PACKAGE.md`。
5. 主控 Agent 在调用 reviewer 前，确认 CONTEXT_PACKAGE.md 的 Input Manifest 已包含工程规范（通过 engineering.json rulePrefixIndex 发现）：
   - FORBID- 前缀（禁止模式）
   - REVIEW-/REV-SUP- 前缀（代码审查清单）
   - MOD-API-/MOD-PRIVATE- 前缀（模块边界）
6. 按 Tier 调用 reviewer：
   - **STANDARD**：调用 `code-reviewer`。对于 Java 项目，仍调用 `java-reviewer`（基础质量底线）。不强制调用 database-reviewer / security-reviewer / frontend-ux-reviewer。
   - **DEEP**：调用 `code-reviewer` + 按 affected_areas 调用对应专项 reviewer（Java → java-reviewer，DB → database-reviewer，security → security-reviewer，frontend → frontend-ux-reviewer）。**此行为等同于改前的标准审查深度。**
   - **THOROUGH**：调用 `code-reviewer` + 全部专项 reviewer（java-reviewer, database-reviewer, security-reviewer, frontend-ux-reviewer），无论 affected_areas 是否涉及。
   每个 reviewer 返回后检查 Pre-mortem 校验通过标记；失败则补全输入重新调用。
7. 如果发现阻塞或高风险问题，只给修复建议，交给主控 Agent 或 resolver 处理。
8. 输出或更新 `11_审查报告.md`。
9. 如果启用工程事实库且 `modules.architectureRules=true` 或 `modules.qualityVerification=true`，生成 `PROJECT_CONSISTENCY_REVIEW.md`。
10. 更新 `CHANGE_METRICS.json` 的 `reviewBlockers`、`pendingDecisionsCreated`、`architectureOwnerDecisionsCreated`。

## 审查顺序

**第一关：需求覆盖** `[STANDARD]`

对照 `02_工程需求规格.md` 的每个 Req ID：

- 是否有对应设计。
- 是否有对应实施任务。
- 是否有对应验证计划和验证证据。
- 标记为本次不实现的 Req ID 是否有用户确认证据。

任何 Req ID 无覆盖且无用户确认，审查结论必须为”不通过”。

**第二关：范围和证据** `[STANDARD]`

- 改动是否都在 `07_实施计划.md` 允许范围。
- 是否存在 pending 决策。
- 是否存在未确认 checkpoint。
- 验证结果是否是真实命令输出（非主控 Agent 自己跑的结果）。

**第三关：反模式对照** `[STANDARD]`

如果 `禁止模式清单.md` 存在，逐条对照 FORBID-xxx 规则检查 diff。每个违反项标记严重级别和证据。

**第四关：交叉引用** `[DEEP 起]`

从 `03_代码库调研.md` 第 1-3 节提取 2-3 个相似现有实现作为参考基线，对比变更是否遵循现有模式。不一致且无合理原因的标记为 P1。

STANDARD tier 可跳过此关，直接在审查报告中注明”STANDARD tier，跳过交叉引用”。

**第五关：测试设计审查** `[STANDARD]`

对照 `02_工程需求规格.md` 中每个 AC 的 Given/When/Then，检查 `08_验证计划.md` 的测试用例是否覆盖了 Then 中所有可观测结果。边界条件是否至少有一个对应测试用例。标记缺失的测试场景为 P1。

**第六关：代码质量** `[DEEP 起]`

- 是否违反模块边界。
- 是否依赖 implementation detail。
- 是否缺少异常处理、事务、并发、安全、性能考虑。
- 是否缺少关键测试。
- 前端改动是否符合 `rules/frontend/ui-ux-quality.md`，并具备浏览器验证证据。

STANDARD tier 只检查：命名规范、异常不空 catch、无 printStackTrace、无 System.out.println。

## 输出

`11_审查报告.md` 采用评审规范 REVIEW- 前缀文件的第 4 节"审查输出格式"定义的统一输出格式。

必须包含：

- 总览表（Critical / Major / Minor / Nit 分布）
- ⚠️ 问题（按严重级别排列，每条含编号、文件、问题、影响、建议、规则引用）
- ✅ 通过的检查项
- 总体评估（通过 / 不通过 / 有条件通过，有 Critical 项自动不通过）

此外保留：
- Req ID 覆盖映射
- 已读输入
- 引用证据
- 未覆盖项
- 下游依赖
