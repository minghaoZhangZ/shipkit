---
name: springboot-patterns
description: Use when designing or implementing Java Spring Boot backend APIs, services, repositories, validation, transactions, exceptions, logging, caching, async jobs, or integration flows.
origin: ECC-adapted
---

# Spring Boot Patterns

不能替代代码库调研；只能在 `<change-dir>/ai/03_CODEBASE_RESEARCH.md` 有证据后，用来约束 Spring Boot 设计和实现。

## Required Inputs

- `<change-dir>/ai/02_SPEC.md`
- `<change-dir>/ai/03_CODEBASE_RESEARCH.md`
- `<change-dir>/ai/04_BACKEND_DESIGN.md`
- `<change-dir>/ai/07_IMPLEMENTATION_PLAN.md`

## Layer Rules

Controller：

- 只处理 HTTP 协议、参数校验、响应码和 DTO 转换。
- 不写复杂业务逻辑。
- 入参使用 `@Valid` 和 Bean Validation。
- 不直接返回 JPA Entity。

Service：

- 承载业务流程、事务边界、权限校验和领域规则。
- 写操作使用 `@Transactional`。
- 只读查询按需使用 `@Transactional(readOnly = true)`。
- 外部接口调用不要放在长事务中。

Repository：

- 只处理数据访问。
- 复杂查询必须说明索引、分页、投影和 N+1 风险。
- 修改查询必须有事务边界和 `@Modifying`。

DTO：

- Request DTO 负责输入契约和校验。
- Response DTO 负责输出契约。
- 不暴露 Entity 内部结构。

## API Design

- 创建成功返回 `201 Created`。
- 查询不存在返回 `404`，不要用 `200 + null`。
- 校验失败返回 `400`。
- 权限不足返回 `403`。
- 未认证返回 `401`。
- 大列表接口必须分页。
- 对外 API 字段变更必须进入 `<change-dir>/ai/06_DATA_CONTRACT.md`。

## Exception Handling

- 优先使用全局异常处理。
- 业务异常映射为明确错误码或错误消息。
- 不把堆栈、SQL、路径、内部类名暴露给客户端。
- 日志保留排查上下文，但脱敏 token、密码、手机号、身份证等敏感信息。

## Logging

- 使用 SLF4J 参数化日志。
- 禁止生产代码 `System.out.println` 和 `printStackTrace`。
- 关键业务操作记录业务 ID、用户 ID、状态变化和结果。
- 不记录敏感原文。

## Async And Jobs

- 异步任务必须考虑线程池边界、重试、幂等和失败告警。
- 定时任务避免长时间阻塞调度线程。
- 消息消费必须考虑重复消费和死信处理。

## Cache

- 缓存必须有失效策略。
- 写操作必须考虑缓存一致性。
- 缓存 key 必须稳定且避免敏感信息。

## Output Integration

设计阶段写入：

- `<change-dir>/ai/04_BACKEND_DESIGN.md`
- `<change-dir>/ai/06_DATA_CONTRACT.md`

实现阶段遵守：

- `<change-dir>/ai/07_IMPLEMENTATION_PLAN.md`

验证阶段记录：

- `<change-dir>/ai/09_TEST_RESULT.md`

## Common Mistakes

- Controller 里写业务逻辑。
- Service 返回 `null`。
- 直接返回 Entity。
- 无分页返回 `List<T>`。
- 事务包住外部 HTTP 调用。
- 异常直接 `e.getMessage()` 返回前端。
