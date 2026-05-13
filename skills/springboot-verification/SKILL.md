---
name: springboot-verification
description: Use when verifying Spring Boot changes before completion, review, release notes, PR, or after build/test/security-sensitive modifications.
origin: ECC-adapted
---

# Spring Boot Verification

`verification-flow` 的 Spring Boot 深度实现，结果写入 `09_验证结果.md`。

## Command Discovery

优先按项目已有方式运行：

1. README
2. CI 配置
3. `mvnw` / `pom.xml`
4. `gradlew` / `build.gradle`
5. Makefile

不要凭空指定项目没有的插件命令。

## Minimal Verification

用于小改动，采用渐进策略：

1. 先运行目标测试类：

```bash
mvn -Dtest=ChangedClassNameTest test
```

2. 如涉及相关类，扩展运行：

```bash
mvn -Dtest=ChangedTest,RelatedTest test
```

3. 仅当改动影响共享逻辑（工具类、基础 Service、AOP 切面）时，才运行全量：

```bash
mvn test
```

必须记录实际运行命令、退出码和关键输出。只跑第一步就声称通过时，需说明为什么其他类不需要跑。

## Standard Verification

用于常规需求：

```bash
./mvnw verify
mvn verify
./gradlew check
```

如果项目配置了静态检查，运行实际存在的 checkstyle、spotbugs 或 pmd 命令。

## Strict Verification

用于权限、金额、订单、数据库、安全、并发、外部接口：

- standard verification。
- 安全敏感代码搜索。
- 数据库迁移检查。
- 幂等和并发相关测试。
- 回滚方案检查。

## Result Format

写入 `09_验证结果.md`：

```markdown
## Spring Boot Verification

Profile: minimal / standard / strict

Commands:

Exit Codes:

Result:

Failures:

Skipped:

Remaining Risk:
```

## Stop Rules

- 构建失败：进入 `build-fix-flow`。
- 测试失败：先看失败原因，不要改测试绕过。
- 缺少测试命令：记录查找路径和未找到原因。
- 安全或数据库检查失败：进入 strict review。
