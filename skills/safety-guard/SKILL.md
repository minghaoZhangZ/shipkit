---
name: safety-guard
description: Use when a task may run destructive commands, edit broad file ranges, touch production-like data, perform migrations, or operate autonomously.
---

# Safety Guard

把高风险操作从“提醒”升级成“门禁”。

## Guarded Operations

必须确认或阻止：

- `git reset --hard`
- 丢弃工作区的大范围 checkout
- 递归删除项目目录
- `DROP TABLE` / `DROP DATABASE` / `TRUNCATE TABLE`
- 强制推送
- 跳过 git hooks：`--no-verify`
- 修改 linter、formatter、CI、安全配置来绕过失败
- 数据库不可逆迁移
- 生产表单提交、上传私有文件、删除数据、修改权限、发送消息

## Edit Scope Rule

实现阶段必须遵守 `<change-dir>/ai/07_实施计划.md` 的允许修改范围。

如果需要修改范围外文件：

1. 停止。
2. 说明为什么需要扩大范围。
3. 更新实施计划。
4. 等待用户确认。

## Checkpoint Rule

当 `.workflow_state` 中 `requires_user_confirmation=true` 且 `user_confirmed=false`：

- 只能写 `openspec/changes/*/ai/` 下的 AI 文档。
- 不得修改业务代码。
- 不得运行构建、测试、安装依赖、提交等修改性命令。

## Hook Roadmap

当前已启用：

- `checkpoint-guard.py`：阻止未确认 checkpoint 下的业务代码和构建/测试。
- `scope-guard.py`：阻止 coding/verification 阶段修改计划外文件。
- `dangerous-command-guard.py`：阻止危险命令。

后续可增强：

- Java 轻量质量扫描。
- 测试结果记录检查。
- 项目级 learning observation。
