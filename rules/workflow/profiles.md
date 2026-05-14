# Profile Rules

## minimal

用于小 bug 和小改动。必须有：问题复述、代码证据、简版计划、base self-review、CHANGE_METRICS、目标验证命令。

## standard

用于常规产品需求。必须有：产品发现、需求规格、代码库调研、设计文档、实施计划、测试计划、编码前确认、self-review、验证证据。

## strict

用于高风险需求。必须额外有：安全审查、数据库审查、回滚方案、兼容性策略、幂等和并发测试、self-review、真实验证记录。

## learning

用于交付后。必须输出：Lessons learned、Agent eval、SOP candidate、晋升建议。

## optional project consistency

项目级一致性治理是可选增强层：

- 无 `openspec/specs/engineering/engineering.json`：使用 Base Flow，不阻断。
- `enabled=true, mode=advisory`：增强检查只记录风险。
- `enabled=true, mode=enforced`：增强检查可作为 review/archive 门禁。

## ralph 持久化完成循环

ralph 模式是 verification-flow 的增强模式，核心理念："不完成不停止。每次迭代必须有 fresh evidence。"

### 触发条件

以下任一条件满足时，`.workflow_state` 的 `ralph.enabled` 自动设为 true：

1. profile 为 **strict**（自动启用）
2. 用户使用触发词："必须完成"、"不要停"、"ralph"、"做完为止"、"不完成不停止"
3. affected_areas 包含：安全、金钱、订单、数据迁移、并发、外部集成
4. 手动设置 `.workflow_state` 中 `ralph.enabled=true`

### ralph 模式行为变化

| 维度 | 非 ralph | ralph 模式 |
|------|---------|-----------|
| Completion Audit | 轻量检查，不阻断 | 强制执行，不通过 → 回到 coding |
| Architect Review Tier floor | STANDARD | DEEP（小改动也要深度审查） |
| L3 失败处理 | code-reviewer 诊断 → 人工介入 | code-reviewer 诊断 → 自动回路（回 design/coding/修正测试） |
| max_iterations | 无 | 10（超出后强制停止） |
| TODO/FIXME 检查 | 不强制 | 强制清零 |
| 范围缩减检测 | 无 | 逐条对比 plan vs 实际改动 |

### ralph 不适用于 minimal profile

minimal 不执行全量验证和审查，completion audit 在其中意义有限。如果 ralph 触发条件与 minimal 同时满足，升级到 standard。
