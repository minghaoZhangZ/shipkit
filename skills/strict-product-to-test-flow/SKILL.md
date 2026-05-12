---
name: strict-product-to-test-flow
description: Use when a product requirement touches security, permissions, money, orders, inventory, database migrations, concurrency, external integrations, files, webhooks, or sensitive data.
---

# Strict Product To Test Flow

目标：把不可逆风险提前暴露——安全、数据、并发、回滚、审计和验证证据。

## When To Use

- 登录、鉴权、授权、权限模型。
- 金额、订单、库存、支付、退款。
- 数据库迁移、复杂 SQL、大表查询。
- 异步消息、重试、幂等、状态机。
- 外部接口、Webhook、文件上传下载。
- 密钥、token、隐私数据、敏感日志。

## Required Flow

1. 执行 `product-to-test-flow` 的产品、规格、调研、设计、计划、测试计划阶段。
2. 强制补充 `<change-dir>/ai/06_DATA_CONTRACT.md`。
3. `<change-dir>/ai/07_IMPLEMENTATION_PLAN.md` 必须包含：
   - 回滚方案。
   - 灰度或兼容策略。
   - 允许修改文件范围。
   - 不允许修改文件。
   - 停止条件。
4. `<change-dir>/ai/08_TEST_PLAN.md` 必须包含：
   - 权限或安全用例。
   - 幂等和重复提交用例。
   - 异常和回滚用例。
   - 数据边界用例。
5. **编码前强制暂停**：用 `AskUserQuestion` 询问用户确认。用户确认前，不得修改任何业务代码、不得运行任何构建命令。
6. 实现后先执行 `product-to-test-flow` 的 self-review，输出 `<change-dir>/ai/10_SELF_REVIEW.md` 和 `<change-dir>/ai/CHANGE_METRICS.json`。
7. 然后运行 `verification-flow`。
8. 调用 `code-reviewer`。
9. 按需强制调用：
   - Java/Spring：`java-reviewer`
   - 数据库：`database-reviewer`
   - 安全敏感：`security-reviewer`
10. 阻塞问题和高风险问题必须修复后复审。
11. 发布说明必须包含回滚方案和已知风险。

如果项目启用了 `openspec/specs/engineering/engineering.json`：

- `mode=advisory`：项目级一致性风险写入 `PROJECT_CONSISTENCY_REVIEW.md`，不阻断。
- `mode=enforced`：项目级一致性 review 不通过不得归档。
- architecture owner decision 只在 manifest 启用时作为增强门禁；未启用时不得阻断 Base Flow。

## Stop Conditions

遇到以下情况必须停止并请求用户确认：

- 证据不足。
- 需要修改实施计划未允许的文件。
- 需要改变接口兼容性。
- 需要数据库不可逆迁移。
- 安全 reviewer 给出不通过。
- 测试无法运行且没有替代验证方式。
