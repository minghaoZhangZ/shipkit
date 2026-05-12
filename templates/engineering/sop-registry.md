# SOP 注册表

## 1. 目的

沉淀从多次交付证据中晋升出来的可复用 SOP。此文件属于 Enhanced Flow，只有当 `engineering.json` 启用 `sopRegistry` 时才应被工作流更新。

## 2. 晋升规则

默认晋升信号：

- 同一场景至少出现在 3 条 SOP candidate 中。
- 候选项来自至少 2 个不同 change。
- 相关证据出现在 self-review 问题、review 阻塞项、verification 失败轮次等 metrics 中。
- 架构 / 领域 / 质量 Owner 确认该 SOP 具备复用价值。

## 3. SOP 索引

| SOP ID | 场景 | 状态 | 来源 Change | Owner | 最后更新 |
|--------|------|------|-------------|-------|----------|
| SOP-001 | TODO | draft / active / deprecated | TODO | TODO | TODO |

## 4. SOP 模板

```markdown
## SOP-XXX: TODO

- 触发条件: TODO
- 前置检查:
  - [ ] TODO
- 执行步骤:
  1. TODO
- 验证方式:
  - TODO
- 度量信号:
  - TODO
- 来源 Change:
  - TODO
- Owner:
  - TODO
- 状态:
  - draft
```
