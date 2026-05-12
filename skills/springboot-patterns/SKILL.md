---
name: springboot-patterns
description: Use when designing or implementing Java Spring Boot backend APIs, services, repositories, validation, transactions, exceptions, logging, caching, async jobs, or integration flows.
origin: ECC-adapted
---

# Spring Boot Patterns

不能替代代码库调研；只能在 `03_代码库调研.md` 有证据后，用来约束 Spring Boot 设计和实现。

## Required Inputs

- `CONTEXT_PACKAGE.md`
- `02_工程需求规格.md`
- `03_代码库调研.md`
- `04_后端方案说明.md`
- `07_实施计划.md`

统一使用中文 canonical 文档名。

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

Repository / Mapper：

- 只处理数据访问。
- 复杂查询必须说明索引、分页、投影和 N+1 风险。
- 修改查询必须有事务边界。

DTO / VO：

- Request DTO 负责输入契约和校验。
- Response VO 负责输出契约。
- 不暴露 Entity 内部结构。

## API Design

- 大列表接口必须分页。
- 对外 API 字段变更必须进入 `06_接口与数据契约.md`。
- 权限、校验、异常返回必须和契约一致。

## Exception And Logging

- 优先使用全局异常处理。
- 不吞异常，不空 catch。
- 禁止生产代码 `System.out.println` 和 `printStackTrace`。
- 日志保留排查上下文，但脱敏 token、密码、手机号、身份证等敏感信息。

## Transactions

- 小事务原则。
- 避免事务中执行慢外部调用。
- 锁生命周期必须包含事务生命周期。
- 需要锁包住事务时，优先使用 `TransactionTemplate` 手动控制。

## Output Integration

- 设计阶段写入 `04_后端方案说明.md` 和 `06_接口与数据契约.md`。
- 实现阶段遵守 `07_实施计划.md`。
- 验证阶段记录到 `09_验证结果.md`。

## Common Mistakes

- Controller 里写业务逻辑。
- Service 返回 `null`。
- 直接返回 Entity。
- 无分页返回 `List<T>`。
- 事务包住外部 HTTP 调用。
- 异常直接 `e.getMessage()` 返回前端。
