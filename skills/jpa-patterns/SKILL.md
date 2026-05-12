---
name: jpa-patterns
description: Use when designing or changing JPA entities, repositories, queries, relationships, migrations, indexes, transactions, pagination, or Hibernate performance behavior.
origin: ECC-adapted
---

# JPA Patterns

接入 `data-contract-designer`、`database-reviewer` 和 `06_接口与数据契约.md`。

## Required Inputs

- `CONTEXT_PACKAGE.md`
- `02_工程需求规格.md`
- `03_代码库调研.md`
- `06_接口与数据契约.md`
- `07_实施计划.md`

统一使用中文 canonical 文档名。

## Entity Rules

- Entity 不直接作为 API Response。
- 字段约束应和数据库约束、DTO 校验保持一致。
- 枚举持久化优先 `EnumType.STRING`。
- 时间字段优先使用项目既有时间类型。
- 金额使用 `BigDecimal`。
- 生产环境不依赖 Hibernate 自动 DDL。

## Relationship Rules

- 集合关系默认 Lazy。
- 谨慎使用 `CascadeType.ALL` 和 `orphanRemoval`。
- `ManyToMany` 优先拆成中间实体，便于扩展审计字段。
- 双向关系要避免 JSON 序列化递归。

## Query Rules

- 大列表必须分页。
- 读模型可用 DTO projection 或接口 projection。
- 复杂查询必须检查 N+1。
- Native SQL 必须参数化。
- 修改查询需要事务边界。

## Transaction Rules

- 事务边界放在 Service 层。
- 只读查询按需使用 `@Transactional(readOnly = true)`。
- 避免在事务中执行慢外部调用。
- 状态机变更要考虑并发写和非法状态转换。

## Index And Migration Rules

写入 `06_接口与数据契约.md` 时必须说明：

- 新增或变更字段。
- 索引设计。
- 唯一约束。
- 外键和删除策略。
- 数据迁移策略。
- 回滚方案。

## Testing

- Repository 测试优先 `@DataJpaTest`。
- 数据库差异敏感时优先 Testcontainers。
- 覆盖唯一约束、分页、排序、边界值、事务回滚。

## Common Mistakes

- `FetchType.EAGER` 用在集合。
- `findAll()` 暴露到接口。
- 缺少分页。
- 事务中调用第三方接口。
- 没有索引就新增高频查询。
- 迁移没有回滚方案。
