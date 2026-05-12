---
name: build-fix-flow
description: Use when build, compile, lint, typecheck, dependency, static analysis, or test execution errors need focused repair.
---

# Build Fix Flow

只修复明确失败，修完必须用同一命令验证。

## Flow

1. 记录原始失败命令和关键错误。
2. 判断技术栈：
   - Java / Maven / Gradle / Spring：优先调用 `java-build-resolver`。
   - 其他技术栈：调用 `build-error-resolver`。
3. Resolver 只能做最小修复。
4. Resolver 必须重新运行失败命令。
5. 将命令和结果写入 `<change-dir>/ai/09_TEST_RESULT.md`。
6. 如果修复修改了业务代码，调用 `code-reviewer`。

## Limits

- 不禁用测试、lint、Checkstyle、SpotBugs、安全规则。
- 不扩大重构。
- 不修改实施计划禁止的文件。
- 连续 3 次失败必须停止并报告。

## Output

```text
Build Status: SUCCESS / FAILED
Original Command:
Verification Command:
Files Modified:
Remaining Errors:
```
