---
name: contract-check-flow
description: Use when frontend-backend API contracts, DTO/VO fields, enums, errors, null rules, permissions, pagination, events, or database contracts must be aligned before implementation.
---

# Contract Check Flow

目标：生成 `06_接口与数据契约.md`，让前端和后端在实施计划前确认同一份合同。

## 输入

必读：

- `CONTEXT_PACKAGE.md`
- `02_工程需求规格.md`
- `04_后端方案说明.md`（后端受影响时）
- `05_前端方案说明.md`（前端受影响时）
- `03_代码库调研.md`

## 执行

1. 确认 required design checkpoint 已通过。
2. 更新 `CONTEXT_PACKAGE.md`，`current_phase=contract`，填写 Input Manifest。
3. 调用 `data-contract-designer` 输出 `06_接口与数据契约.md`。返回后检查 Pre-mortem 校验通过标记；失败则补全输入重新调用。
4. 检查前后端字段、枚举、错误码、空值、权限失败行为是否一致。
5. 设置 checkpoint：

```yaml
checkpoint: contract_confirmation
requires_user_confirmation: true
user_confirmed: false
confirmation_type: approve_contract
confirmation_role: frontend_backend_owners
confirmation_docs: ["06_接口与数据契约.md"]
```

## 输出合同

`06_接口与数据契约.md` 必须包含：

- 契约范围
- API 路径和方法
- 请求 DTO
- 响应 VO
- 字段含义、类型、是否可空、默认值
- 枚举值和状态流转
- 错误码和异常返回
- 权限失败行为
- 分页、排序、过滤规则
- 幂等、兼容和版本演进策略
- 数据库/事件契约（如适用）
- 回滚和灰度风险（strict 必填）
- `Req ID 覆盖映射`
- `已读输入`、`引用证据`、`未覆盖项`、`下游依赖`

## 停止条件

- 前后端字段不一致。
- 错误码、枚举、空值或权限失败行为不清。
- 兼容性或幂等风险无法判断。
- 契约相关 Req ID 未覆盖且无确认排除。
