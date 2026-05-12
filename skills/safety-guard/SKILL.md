---
name: safety-guard
description: Use when a task may run destructive commands, edit broad file ranges, touch production-like data, perform migrations, or operate autonomously.
---

# Safety Guard

把高风险操作从”提醒”升级成”门禁”。

## Guarded Operations

必须确认或阻止：

- `git reset --hard`
- 丢弃工作区的大范围 checkout
- 递归删除项目目录
- `DROP TABLE` / `DROP DATABASE`
- 强制推送
- 跳过 git hooks：`--no-verify`
- 修改 linter、formatter、CI、安全配置来绕过失败
- 数据库不可逆迁移

## Edit Scope Rule

实现阶段必须遵守 `<change-dir>/ai/07_IMPLEMENTATION_PLAN.md` 的允许修改范围。

如果需要修改范围外文件：

1. 停止。
2. 说明为什么需要扩大范围。
3. 更新实施计划。
4. 等待用户确认。

## Hook Roadmap

第一阶段：

- 等待通知 beep。

第二阶段：

- 阻止危险命令。
- Java 轻量质量扫描。
- 检查测试结果是否记录。

第三阶段：

- 项目级 learning observation。
- profile-aware quality gate。
