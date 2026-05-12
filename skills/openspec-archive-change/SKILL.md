---
name: openspec-archive-change
description: Use when a requirement, bugfix, refactor, security fix, data migration, or test task is complete and its OpenSpec change should be archived.
---

# OpenSpec Archive Change

## Required Before Archive

归档前必须确认：

- `<change-dir>/ai/09_TEST_RESULT.md` 已记录真实验证命令。
- 新流程 change：`<change-dir>/ai/10_SELF_REVIEW.md` 已完成；旧 change 可说明不适用。
- 新流程 change：`<change-dir>/ai/11_REVIEW_REPORT.md` 已完成；旧 change 可保留 `10_REVIEW_REPORT.md`。
- 新流程 change：`<change-dir>/ai/12_RELEASE_NOTE.md` 已完成；旧 change 可保留 `11_RELEASE_NOTE.md`。
- 新流程 change：`<change-dir>/ai/13_LESSONS_LEARNED.md` 已完成；旧 change 可保留 `12_LESSONS_LEARNED.md`。
- `<change-dir>/ai/CHANGE_METRICS.json` 已完成；旧 change 可说明不适用。
- `metadata.json` 状态已更新为 `done`。

## Flow

1. 阅读 change 的 proposal、design、tasks 和 ai 文档。
2. 判断哪些内容应合并到 `openspec/specs/`：
   - 产品长期规则。
   - API 契约。
   - 数据库事实。
   - 测试策略。
   - 架构边界。
3. 更新对应 specs。
4. 如果检测到 `openspec/specs/engineering/engineering.json` 且 `enabled=true`：
   - `modules.consistencyReview=true` 时，检查 `<change-dir>/ai/PROJECT_CONSISTENCY_REVIEW.md`。
   - `mode=advisory`：允许归档，但归档记录中保留风险。
   - `mode=enforced`：一致性 review 不通过或缺失时不得归档。
   - `modules.metricsLedger=true` 时，将 `CHANGE_METRICS.json` 归纳追加到 `openspec/specs/engineering/metrics-ledger.jsonl`。
   - `modules.sopRegistry=true` 时，确认 SOP candidate 已按规则处理。
5. 未启用 engineering manifest 时，跳过 Enhanced Flow，不得阻断 Base Flow。
6. 将目录移动到：

```text
openspec/changes/archive/<change-id>
```

7. 将归档后 `metadata.json` 状态更新为 `archived`。

## Do Not Archive If

- 测试未运行且无理由。
- 审查结论不通过。
- 阻塞问题未修复。
- 需求仍有未确认问题。
- 长期 specs 需要更新但尚未更新。
- `engineering.json` 为 `enabled=true` 且 `mode=enforced` 时，项目一致性 review 未通过。
