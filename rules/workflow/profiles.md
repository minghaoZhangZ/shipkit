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
