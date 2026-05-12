---
name: springboot-verification
description: Use when verifying Spring Boot changes before completion, review, release notes, PR, or after build/test/security-sensitive modifications.
origin: ECC-adapted
---

# Spring Boot Verification

`verification-flow` 的 Spring Boot 深度实现，结果写入 `<change-dir>/ai/09_TEST_RESULT.md`。

## Command Discovery

优先按项目已有方式运行：

1. `README`
2. CI 配置
3. `mvnw` / `pom.xml`
4. `gradlew` / `build.gradle`
5. Makefile

不要凭空指定项目没有的插件命令。

## Minimal Verification

用于小改动：

```bash
./mvnw test
mvn test
./gradlew test
```

也可以运行更窄的测试，但必须说明原因。

## Standard Verification

用于常规需求：

```bash
./mvnw verify
mvn verify
./gradlew check
```

如项目配置了静态检查，运行：

```bash
./mvnw checkstyle:check
./mvnw spotbugs:check
./mvnw pmd:check
```

## Strict Verification

用于权限、金额、订单、数据库、安全、并发、外部接口：

- standard verification。
- 安全敏感代码搜索。
- 数据库迁移检查。
- 幂等和并发相关测试。
- 回滚方案检查。

常用只读扫描：

```bash
grep -rn "System\\.out\\.print" src/main --include="*.java"
grep -rn "printStackTrace" src/main --include="*.java"
grep -rn "e\\.getMessage()" src/main --include="*.java"
grep -rn "allowedOrigins.*\\*" src/main --include="*.java"
```

## Result Format

写入 `<change-dir>/ai/09_TEST_RESULT.md`：

```text
## Spring Boot Verification

Profile: minimal / standard / strict

Commands:
- <command>

Exit Codes:
- <command>: <code>

Result:
- PASS / FAIL

Failures:
- ...

Skipped:
- ...

Remaining Risk:
- ...
```

## Stop Rules

- 构建失败：进入 `build-fix-flow`。
- 测试失败：先看失败原因，不要改测试绕过。
- 缺少测试命令：记录查找路径和未找到原因。
- 安全或数据库检查失败：进入 strict review。
