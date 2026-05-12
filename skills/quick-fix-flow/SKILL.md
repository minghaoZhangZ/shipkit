---
name: quick-fix-flow
description: Use when a small bug, narrow refactor, simple API adjustment, small UI fix, or focused failing test needs a lightweight workflow.
---

你要执行小需求或小 bug 修复流程。

适用范围：

- 小 bug
- 简单接口调整
- 简单文案或样式修复
- 小范围重构
- 明确失败测试修复

## 前置条件

如果还没有 `<change-dir>`，先调用 `openspec-new-change` 创建工作区。

## 工作流

1. 简述问题和预期结果，写入 `<change-dir>/ai/00_REQUIREMENT.md`。
2. 创建/更新 `<change-dir>/ai/.workflow_state`：
   ```yaml
   change_id: "<change-id>"
   profile: minimal
   current_phase: plan
   requires_user_confirmation: false
   user_confirmed: true
   project_consistency_enabled: false
   engineering_manifest: ""
   engineering_mode: "off"
   self_review_mode: "base"
   metrics_mode: "change_only"
   sop_mode: "candidate_only"
   consistency_review_required: false
   architecture_owner_required: false
   ```
3. 调用或执行只读代码库调研，输出到 `<change-dir>/ai/03_CODEBASE_RESEARCH.md`。
4. 生成简版实施计划，输出到 `<change-dir>/ai/07_IMPLEMENTATION_PLAN.md`。
5. 如涉及测试，更新 `<change-dir>/ai/08_TEST_PLAN.md`。
6. 在 `07_IMPLEMENTATION_PLAN.md` 中保留“顺带重构受控出口”；minimal 默认空出口，除非用户明确确认。
7. **进入编码前**更新 `.workflow_state`：`current_phase=coding`
8. 只修改实施计划允许的文件。
9. 编码完成后进入 self-review，更新 `.workflow_state`：`current_phase=self_review`, `self_review_mode=base`。
10. 输出 `<change-dir>/ai/10_SELF_REVIEW.md`，至少检查 Req ID 覆盖、实施计划范围、异常处理、测试缺口、明显危险模式。
11. 输出或更新 `<change-dir>/ai/CHANGE_METRICS.json`，记录 self-review 问题数、验证失败轮次、review 阻塞数等 per-change 指标。
12. 执行 `verification-flow` 的 minimal 深度验证。更新 `.workflow_state`：`current_phase=verification`
13. 更新 `<change-dir>/ai/09_TEST_RESULT.md`。
14. 执行只读 diff review（自检，不调独立 Agent）。
15. 需要时更新 `<change-dir>/ai/12_RELEASE_NOTE.md`（旧 change 可保留 `11_RELEASE_NOTE.md`）。
16. 更新 `.workflow_state`：`current_phase=delivery`

## 下一步

调用 `openspec-archive-change` 归档本次 change。

## 禁止事项

- 不要因为是小需求就跳过代码证据。
- 不要因为是小需求就跳过 self-review 和 CHANGE_METRICS。
- 不要改无关文件。
- 不要扩大重构范围。
