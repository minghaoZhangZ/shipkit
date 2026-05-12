# Profiles

借鉴 ECC 的 profile 思路，但按个人产品交付流程裁剪。

## minimal

用于小 bug 和小范围修改。重点是快，但不能跳过代码证据、self-review、CHANGE_METRICS 和验证。

## standard

默认产品到测试流程。适合常规需求，需要完整 `<change-dir>/ai` 交接、编码前确认、self-review、验证和审查。

## strict

用于高风险需求。必须增加安全、数据库、回滚、并发和性能检查。

触发条件：

- 权限、登录、鉴权、授权
- 金额、订单、库存、支付
- 数据库迁移或大查询
- 异步消息、重试、幂等
- 外部接口、Webhook、文件上传
- 隐私、密钥、敏感数据

## learning

交付后沉淀经验。Base Flow 产出 SOP candidate；只有项目启用 `openspec/specs/engineering/engineering.json` 时，才写入项目级 `sop-registry.md` 和 `metrics-ledger.jsonl`。项目经验默认项目内生效，重复跨项目出现后再晋升全局。

## optional project consistency

项目级一致性治理是可插拔增强层：

- 未配置 `openspec/specs/engineering/engineering.json`：使用 Base Flow。
- `enabled=true, mode=advisory`：增强检查只记录，不阻断。
- `enabled=true, mode=enforced`：增强检查可作为 review/archive 门禁。
