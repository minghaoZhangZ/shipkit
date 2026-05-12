---
name: review-flow
description: Use when staged or unstaged changes need evidence-based review before merge, release, or handoff.
---

你要执行只读审查流程。

## 前置条件

需要有已存在的 `<change-dir>` 且至少有 `02_SPEC.md` 和 `07_IMPLEMENTATION_PLAN.md`。

## 工作流

1. 查看 `git status` 和 `git diff`。
2. 阅读相关 `<change-dir>/ai/` 文档。
3. 调用 `code-reviewer`。
4. 如果涉及 Java/Spring、数据库、安全，可按需调用专项 reviewer。
5. 如果审查发现阻塞或高风险问题，只给修复建议，不直接改代码；交给 resolver 或主控 Agent 处理。
6. 输出或更新 `<change-dir>/ai/11_REVIEW_REPORT.md`（旧 change 可保留 `10_REVIEW_REPORT.md`）。
7. 如果检测到 `openspec/specs/engineering/engineering.json` 且 `enabled=true`、`modules.consistencyReview=true`，生成 `<change-dir>/ai/PROJECT_CONSISTENCY_REVIEW.md`：
   - `mode=advisory`：记录跨 change 一致性风险，不阻断。
   - `mode=enforced`：不通过时审查结论不得为通过。
   - 未启用 manifest：跳过，不得阻断 Base Flow。
8. 更新 `<change-dir>/ai/CHANGE_METRICS.json` 的 `reviewBlockers`、`pendingDecisionsCreated`、`architectureOwnerDecisionsCreated`。

## 审查顺序（先做覆盖，再做质量）

**第一关 — 需求覆盖（机械核对，不过则停）**：

对照 `02_SPEC.md` 需求追踪表的每个 Req ID：
- 在 `git diff` 中是否有对应代码改动
- 在 `08_TEST_PLAN.md` 或实际测试文件中是否有对应测试
- 标记为"本次不实现"的 Req ID 是否有用户确认证据

任何 Req ID 无覆盖且无用户确认 → 审查结论"不通过"，修复后才进入第二关。

**第二关 — 代码质量**：

- 是否违反模块边界。
- 是否依赖 implementation detail。
- 是否缺少异常处理、事务、并发、安全、性能考虑。
- 是否缺少关键测试。
- 如果启用 Enhanced Flow：是否违反项目级工程事实库中的模块边界、领域概念、reusable API、forbidden patterns。

## 禁止事项

- reviewer 不允许修改代码。
- 不允许只给泛泛建议。
- 每个问题必须有文件、位置或证据。
