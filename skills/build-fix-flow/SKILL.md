---
name: build-fix-flow
description: Use when build, compile, lint, typecheck, dependency, static analysis, or test execution errors need focused repair.
---

# Build Fix Flow

只修复明确失败，修完必须用同一命令验证，并把结果写入 `09_验证结果.md`。

## Flow

1. 记录原始失败命令和关键错误。
2. 判断技术栈：
   - Java / Maven / Gradle / Spring：优先调用 `java-build-resolver`。
   - 其他技术栈：调用 `build-error-resolver`。
   Resolver 返回后检查其输出是否包含 Pre-mortem 校验通过标记；缺少失败命令信息时补全并重新调用。
3. Resolver 只能做最小修复，且必须遵守 `07_实施计划.md` 的允许文件范围。
4. Resolver 必须重新运行失败命令。
5. 将命令、退出码和结果写入 `09_验证结果.md`。
6. 如果修复修改了业务代码，调用 `code-reviewer`。

## Limits

- 不要通过删除测试、关闭 lint、关闭 Checkstyle、关闭 SpotBugs、修改安全配置来绕过失败。
- 不扩大重构范围。
- 不修改 `07_实施计划.md` 禁止的文件。
- 连续 3 次失败必须停止并报告。

## Output

```text
Build Status: SUCCESS / FAILED
Original Command:
Verification Command:
Files Modified:
Remaining Errors:
```
