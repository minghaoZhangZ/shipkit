---
name: openspec-archive-change
description: Use when a requirement, bugfix, refactor, security fix, data migration, or test task is complete and its OpenSpec change should be archived.
---

# OpenSpec Archive Change

## 归档前必须确认

- `09_验证结果.md` 已记录真实验证命令。
- 新流程 change 已完成验证（`09_验证结果.md` 含 test-planner 独立评估结论）。
- 新流程 change 已完成 `11_审查报告.md`。
- 新流程 change 已完成 `12_发布说明.md`。
- standard/strict change 已完成 `13_经验沉淀.md`。
- `CHANGE_METRICS.json` 已完成。
- `metadata.json` 状态已更新为 `done`。
- `PENDING_DECISIONS.md` 无 pending 项。
- `.workflow_state` 中 required checkpoints 均已确认。

## Flow

1. 阅读 proposal、design、tasks、AI 文档和 `CONTEXT_PACKAGE.md`。
2. 判断哪些内容应合并到 `openspec/specs/`：产品长期规则、API 契约、数据库事实、测试策略、架构边界。
3. 更新对应 specs。
4. 如果检测到 `openspec/specs/engineering/engineering.json` 且 `enabled=true`：
   - `modules.architectureRules=true` 或 `modules.qualityVerification=true` 时，检查 `PROJECT_CONSISTENCY_REVIEW.md`。
   - `mode=advisory`：允许归档，但归档记录中保留风险。
   - `mode=enforced`：一致性 review 不通过或缺失时不得归档。
   - `modules.learningGovernance=true` 时，将 `CHANGE_METRICS.json` 归纳追加到 `engineering.json` metrics.ledgerFile 指定的指标台账。
   - `modules.learningGovernance=true` 时，确认 SOP candidate 已按规则处理。
5. 未启用 engineering manifest 时，跳过 Enhanced Flow，不得阻断 Base Flow。
6. 将目录移动到 `openspec/changes/archive/<change-id>`。
7. 将归档后 `metadata.json` 状态更新为 `archived`。

## Do Not Archive If

- 测试未运行且无理由。
- 审查结论不通过。
- 阻塞问题未修复。
- 需求仍有未确认问题。
- required checkpoints 未全部确认。
- 长期 specs 需要更新但尚未更新。
- `engineering.json` 为 `enabled=true` 且 `mode=enforced` 时，项目一致性 review 未通过。
