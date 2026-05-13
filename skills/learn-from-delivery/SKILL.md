---
name: learn-from-delivery
description: Use when a feature, bugfix, review, or release is finished and reusable delivery lessons or promotion candidates should be extracted.
---

# Learn From Delivery

用于交付后的经验沉淀。读取本次 change 文档、metrics 和审查结果，输出可复用经验、SOP candidate 和 Agent 评估。

## Flow

1. 阅读 `<change-dir>/ai/` 文档，使用中文 canonical 名。旧 change（2026-05-15 前创建）可能使用英文旧名，读取时兼容但新输出必须用中文名。
2. 读取 `CHANGE_METRICS.json`；不存在时说明原因，不得伪造指标。
3. 总结产品、架构、实现、测试、审查中的有效模式。
4. 识别重复问题和低质量 Agent 输出。
5. 输出 `13_经验沉淀.md`。
6. 输出 `14_Agent评估.md`。
7. 在 lessons 中产出 SOP candidate 小节。
8. 如果启用 `openspec/specs/engineering/engineering.json` 且 `modules.learningGovernance=true`，读取 `engineering.json` metrics.ledgerFile 指定的指标台账并按重复信号更新 SOP 注册表。
9. 更新 `<change-dir>/metadata.json` 状态为 `done`。

## 晋升标准

- 单 change 首次出现：记录到 lessons。
- 同类 signal 跨 change 出现 2 次：SOP candidate。
- 同类 signal 跨 change 出现 3 次：建议做成 skill。
- 同类确定性 signal 跨 change 出现 3 次：建议做成 hook。
- 跨项目重复出现：建议加入全局 rules。

没有启用 Enhanced Flow 时，不写项目级 SOP 注册表，只在 lessons 保留 candidate。

## 输出要求

每条经验必须包含：

- 触发场景
- 解决方式
- 证据来源
- 下次如何复用
- 是否建议晋升
- 关联 metrics signal
