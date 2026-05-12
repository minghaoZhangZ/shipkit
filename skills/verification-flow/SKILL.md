---
name: verification-flow
description: Use when about to claim work is complete, write release notes, finish review, or verify significant implementation changes.
---

# Verification Flow

核心原则：没有真实命令输出，就不能声称完成、通过或修复。结果写入 `<change-dir>/ai/09_TEST_RESULT.md`。

验证前必须确认：

- 新流程 change 已完成 `<change-dir>/ai/10_SELF_REVIEW.md`。
- `<change-dir>/ai/CHANGE_METRICS.json` 已存在或将在本阶段更新。
- 旧 change 没有 self-review 文档时，不强制补历史文档，但必须在测试结果中说明。

## Flow

1. 识别项目验证命令：
   - README
   - `pom.xml`
   - `build.gradle`
   - `package.json`
   - Makefile
   - CI 配置
2. 按风险选择验证深度：
   - minimal：相关单测或最小复现命令。
   - standard：构建 + 测试 + lint/typecheck。
   - strict：standard + 安全/数据库/回滚相关检查。
3. 运行命令。
4. 阅读完整输出和退出码。
5. 更新 `<change-dir>/ai/09_TEST_RESULT.md`。
6. 更新 `<change-dir>/ai/CHANGE_METRICS.json` 的 `verificationFailedRounds` 和相关 signals；没有工程事实库时只写 per-change metrics。
7. 如果失败，进入 `build-fix-flow` 或停止报告。
8. 只有验证证据支持时，才允许说“通过”。

## Java / Spring Common Commands

```bash
./mvnw test
mvn test
./mvnw verify
mvn verify
./gradlew test
./gradlew check
```

## Report Template

写入 `<change-dir>/ai/09_TEST_RESULT.md`：

```text
## 实际运行命令

## 退出码

## 通过结果

## 失败结果

## 未运行项及原因

## 剩余风险
```

## Red Flags

- “应该可以通过”
- “看起来没问题”
- “之前跑过”
- “只改了文档不用验证”
- “测试太慢所以跳过”

出现这些想法时，必须回到命令证据。
