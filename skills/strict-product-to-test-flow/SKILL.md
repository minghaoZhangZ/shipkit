---
name: strict-product-to-test-flow
description: Use when a product requirement touches security, permissions, money, orders, inventory, database migrations, concurrency, external integrations, files, webhooks, or sensitive data.
---

# Strict Product To Test Flow

strict 是高风险流程，目标是在编码前暴露不可逆风险、兼容风险、安全风险、数据风险和验证缺口。

## 触发条件

- 登录、鉴权、授权、权限模型。
- 金额、订单、库存、支付、退款。
- 数据库迁移、复杂 SQL、大表查询。
- 并发、异步消息、重试、幂等、状态机。
- 外部接口、webhook、文件上传下载。
- 密钥、token、隐私数据、敏感日志。
- 不可逆操作或生产数据风险。

## 必须执行

1. 执行 `product-to-test-flow` 的角色化路由。
2. 强制产出 `02_工程需求规格.md`。
3. 强制产出 `06_接口与数据契约.md`。
4. `07_实施计划.md` 必须包含回滚方案、灰度/兼容策略、允许/禁止修改文件、停止条件。
5. `08_验证计划.md` 必须包含安全/权限、幂等/重复提交、异常/回滚、数据边界用例。
6. 编码前必须通过 `engineering_spec_confirmation`、`contract_confirmation`、`plan_confirmation`。
7. 设计或实现涉及前端时，必须通过 `frontend_design_confirmation`。
8. 设计或实现涉及后端时，必须通过 `backend_design_confirmation`。
9. **每个阶段调用子 Agent 后，必须检查输出是否包含 Pre-mortem 校验通过标记**（参见 `rules/workflow/premortem-validation.md`）。校验失败不得进入下一阶段。
10. 实现后，验证阶段由 test-planner 验证模式独立执行（覆盖率核对 + 测试执行 + 评估），产出 `09_验证结果.md`。更新 `CHANGE_METRICS.json`。
11. 编码阶段每次修改业务代码前必须更新 `resume_context`，确保 `/clear` 后能从最近的 safe point 恢复。
12. 然后运行 `verification-flow`。
13. 按需强制调用 `java-reviewer`、`database-reviewer`、`security-reviewer`、`frontend-ux-reviewer`。

## Stop Conditions

遇到以下情况必须停止并请求用户确认：

- 证据不足。
- 需要修改 `07_实施计划.md` 未允许的文件。
- 需要改变接口兼容性。
- 需要数据库不可逆迁移。
- 安全 reviewer 不通过。
- 测试无法运行且没有替代验证方式。
- `PENDING_DECISIONS.md` 存在 pending 项。

## Enhanced Flow

如果项目启用 `openspec/specs/engineering/engineering.json`：

- `mode=advisory`：记录风险，不阻断。
- `mode=enforced`：项目一致性 review 不通过不得归档。
- architecture owner decision 只在 manifest 启用时作为增强门禁。
