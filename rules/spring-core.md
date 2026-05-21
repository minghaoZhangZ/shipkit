# Spring Core Rules

## API Design

- Controller 只处理 HTTP 协议、参数校验、状态码和 DTO 转换，不写复杂业务逻辑。
- 入参使用 Bean Validation，不直接返回 JPA Entity。
- 状态码：创建 201、查询 200、参数错误 400、未认证 401、无权限 403、不存在 404、冲突 409。
- 大列表必须分页，错误响应统一格式。
- 除非用户确认，不做破坏性接口变更。

## Transaction

- 事务边界放在 Service 层，写操作使用 `@Transactional`，只读查询使用 `@Transactional(readOnly = true)`。
- 避免在事务中调用外部 HTTP、RPC、消息发送或慢 IO。
- 状态变更必须检查当前状态是否合法，幂等键必须在状态变更前检查。
- 高并发写必须考虑唯一约束、乐观锁、悲观锁或业务锁。

## Exception & Logging

- 使用统一异常处理机制，业务异常要有明确语义。
- 使用 SLF4J 参数化日志，禁止 `System.out.println` 和 `printStackTrace`。
- 日志应包含业务定位信息，不记录密码、token、密钥等敏感信息。
- 不得向客户端暴露堆栈信息、SQL 原文、内部文件路径、内部类名、密钥或敏感配置。

## Testing

- Service/Domain：JUnit 5 + Mockito，覆盖业务规则。
- Controller：MockMvc 或项目现有 Web 测试，覆盖状态码和响应结构。
- Repository：`@DataJpaTest`，数据库差异敏感时使用 Testcontainers。
- 必须断言业务结果、状态码、字段、异常类型或数据库结果，不接受只验证"没有异常"的测试。
- 不用 `@SpringBootTest` 写所有单元测试，优先使用轻量测试切片。

## JPA Entity

- Entity 不直接作为 API Response，金额使用 `BigDecimal`，枚举持久化优先 `EnumType.STRING`。
- 集合关系默认 Lazy，谨慎使用 `CascadeType.ALL` 和 `orphanRemoval`。
- `ManyToMany` 优先拆中间实体，双向关系必须避免 JSON 序列化递归。

## JPA Query

- 大列表必须分页，高频查询必须评估索引。
- Native SQL 必须参数化，修改查询必须有事务边界。
- 复杂查询必须检查 N+1 风险。

## JPA Migration

数据库变更必须写入 `<change-dir>/06_DATA_CONTRACT.md`：字段变更、索引、约束、迁移脚本、回滚方案、兼容性影响。
