# Alibaba Java Style

Java 代码默认遵循阿里巴巴 Java 开发规范，并优先服从项目已有规范。

## 核心规则

- 类名 UpperCamelCase，方法名/参数名/成员变量 lowerCamelCase，常量 UPPER_SNAKE_CASE。
- 禁止魔法值，必须抽取有语义的常量。
- 禁止空 `catch`、`printStackTrace`、生产代码 `System.out.println`。
- 集合返回值不返回 `null`，返回空集合。
- 金额计算使用 `BigDecimal`，禁止使用浮点数。

## Spring 要求

- 优先构造器注入，避免字段注入。
- Controller 保持薄层，不写复杂业务逻辑。
- 事务放在 Service 层，查询方法按需使用 `@Transactional(readOnly = true)`。
- API 入参使用 Bean Validation，不直接向前端返回 JPA Entity。
