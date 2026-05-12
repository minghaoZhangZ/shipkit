---
name: learn-from-delivery
description: Use when a feature, bugfix, review, or release is finished and reusable delivery lessons or promotion candidates should be extracted.
---

你要执行交付后经验沉淀流程。

## 工作流

1. 阅读本次 `<change-dir>/ai/` 文档。
2. 读取 `<change-dir>/ai/CHANGE_METRICS.json`；如果不存在，说明原因并按现有文档推断，但不得伪造指标。
3. 总结产品、架构、实现、测试、审查中的有效模式。
4. 识别重复问题和低质量 Agent 输出。
5. 输出 `<change-dir>/ai/13_LESSONS_LEARNED.md`（旧 change 可保留 `12_LESSONS_LEARNED.md`）。
6. 输出 `<change-dir>/ai/14_AGENT_EVAL.md`（旧 change 可保留 `13_AGENT_EVAL.md`）。
7. 在 lessons 中产出 SOP candidate 小节。
8. 如果检测到 `openspec/specs/engineering/engineering.json` 且 `enabled=true`、`modules.sopRegistry=true`，读取 `metrics-ledger.jsonl` 并按重复信号更新 `sop-registry.md`；未启用时只保留 candidate，不强制注册。
9. 更新 `<change-dir>/metadata.json` 状态为 `done`。

## 下一步

调用 `openspec-archive-change` 归档本次 change。

## 晋升标准（Base / Enhanced）

- 单 change 首次出现：记录到 lessons。
- 同类 signal 跨 change 出现 2 次：SOP candidate。
- 同类 signal 跨 change 出现 3 次：建议做成 skill。
- 同类确定性 signal 跨 change 出现 3 次：建议做成 hook。
- 跨项目重复出现：建议加入全局 rules。

没有启用 Enhanced Flow 时，不写项目级 `sop-registry.md`，只在 lessons 中保留 SOP candidate。

## 输出要求

每条经验必须包含：

- 触发场景
- 解决方式
- 证据来源
- 下次如何复用
- 是否建议晋升
- 关联 metrics signal（eventType / eventKey / count）
