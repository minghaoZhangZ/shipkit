---
name: springboot-tdd
description: Use when adding or changing Spring Boot features, endpoints, services, repositories, validation, authorization, or bug fixes that need behavior-first tests.
origin: ECC-adapted
---

# Spring Boot TDD

接入 `test-planner` 和 `<change-dir>/ai/08_TEST_PLAN.md`，把验收标准转成可运行测试。

优先使用场景：复杂业务规则、bug 防回归、权限/金额/订单/库存/状态机、Service/Repository/Controller 行为变化、用户明确要求测试先行。

## Required Inputs

- `<change-dir>/ai/02_SPEC.md`
- `<change-dir>/ai/03_CODEBASE_RESEARCH.md`
- `<change-dir>/ai/07_IMPLEMENTATION_PLAN.md`
- `<change-dir>/ai/08_TEST_PLAN.md`

## Test Selection

Service / Domain：

- 用 JUnit 5 + Mockito。
- 覆盖业务规则、边界条件、异常分支。
- 使用 AssertJ，断言业务结果。

Controller：

- 用 `@WebMvcTest` 或项目现有 Web 测试风格。
- 覆盖状态码、请求校验、响应结构、异常映射、权限。

Repository：

- 用 `@DataJpaTest`。
- 数据库差异敏感时优先 Testcontainers。
- 覆盖唯一约束、分页、排序、查询条件。

Integration：

- 用 `@SpringBootTest` 或项目现有集成测试方式。
- 覆盖跨层流程、事务、幂等、消息或外部接口适配。

## TDD Loop

1. 从 `<change-dir>/ai/08_TEST_PLAN.md` 选择一个用例。
2. 写一个应该失败的测试。
3. 运行测试并确认失败原因正确。
4. 写最小实现。
5. 运行测试确认通过。
6. 重构。
7. 更新 `<change-dir>/ai/09_TEST_RESULT.md`。

## Assertions

- 不接受只有“无异常”的测试。
- 必须断言状态码、字段、状态变化、异常类型或数据库结果。
- 异步逻辑不要用固定 `Thread.sleep`，优先使用项目已有等待工具或 Awaitility。

## Common Mistakes

- 用 `@SpringBootTest` 写所有单元测试。
- Mock 被测对象本身。
- 为了通过测试降低断言质量。
- 只测 happy path。
- 测实现细节而不是业务行为。
