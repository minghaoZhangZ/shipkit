# 安装指令

你正在执行 Claude Code 团队工作流的安装。严格按顺序执行以下步骤，每步完成后报告结果，遇到阻塞立即停止。

---

## 0. 前置检查

执行以下检查，任一失败则终止并报告：

1. 当前目录下存在 `CLAUDE.md`、`rules/`、`skills/`、`agents/`、`hooks/` → 确认
2. `settings.shared.json` 存在 → 确认
3. 执行 `py -3 --version` → 确认 Python 3 可用

---

## 1. 确定安装目标

目标为用户 home 下的 `.claude` 目录。先确认路径：

```powershell
echo $env:USERPROFILE
```

记下输出，后续操作的目标目录为 `<USERPROFILE>\.claude\`。

如果该目录不存在则创建。

---

## 2. 备份已有配置

如果 `<USERPROFILE>\.claude\settings.json` 存在：

1. 生成备份文件名：`settings.json.backup.YYYYMMDD-HHmmss`（使用当前时间戳）
2. 将 `settings.json` 复制到同目录下的备份文件
3. 备份完成后报告

如果 settings.json 不存在（全新安装），跳过备份并说明。

---

## 3. 复制文件

需要将以下内容从当前目录复制到 `<USERPROFILE>\.claude\`。

**逐一执行，不批量**。每完成一项报告一行。

| 源 | 目标目录 | 方式 |
|---|---|---|
| `CLAUDE.md` | `~/.claude/` | 单文件覆盖 |
| `ARCHITECTURE.md` | `~/.claude/` | 单文件覆盖 |
| `rules\` 整个目录 | `~/.claude/rules\` | 目录覆盖 |
| `profiles\` 整个目录 | `~/.claude/profiles\` | 目录覆盖 |
| `skills\` 整个目录 | `~/.claude/skills\` | 目录覆盖 |
| `agents\` 整个目录 | `~/.claude/agents\` | 目录覆盖 |
| `hooks\` 整个目录 | `~/.claude/hooks\` | 目录覆盖 |
| `templates\` 整个目录 | `~/.claude/templates\` | 目录覆盖 |
| `scripts\` 整个目录 | `~/.claude/scripts\` | 目录覆盖 |
| `commands\` 整个目录 | `~/.claude/commands\` | 目录覆盖 |

使用 PowerShell 的 `Copy-Item -Recurse -Force` 完成复制。

---

## 4. 合并 settings.json

**这是最关键的一步。** 目标：把公用 hook/plugin 配置注入到用户已有设置中，保留其 API 配置。

1. 读取 `<USERPROFILE>\.claude\settings.json`（如果不存在，当空对象 `{}` 处理）
2. 读取当前目录 `settings.shared.json`
3. 合并逻辑：
   - 保留已有 settings.json 中的 **全部字段**（尤其是 `env`——API 配置）
   - 将 `settings.shared.json` 中的以下字段**覆盖或新增**：`enabledPlugins`、`extraKnownMarketplaces`、`effortLevel`、`hooks`、`autoUpdatesChannel`
   - `env` 字段完全不动，不增不减不改
4. 将合并后的结果写入 `<USERPROFILE>\.claude\settings.json`

---

## 5. 验证安装

逐项检查并报告每项状态：

1. `<USERPROFILE>\.claude\CLAUDE.md` → 存在/缺失
2. `<USERPROFILE>\.claude\rules\` 下 .md 文件数 → 应有 15 个
3. `<USERPROFILE>\.claude\profiles\` → 应有 profiles.json + README.md
4. `<USERPROFILE>\.claude\skills\` 下子目录数 → 应有 29 个
5. `<USERPROFILE>\.claude\agents\` 下 .md 文件数 → 应有 16 个
6. `<USERPROFILE>\.claude\hooks\` 下 .py 文件数 → 应有 4 个
7. `<USERPROFILE>\.claude\settings.json` 包含 `env` 字段 → 有/无（API 配置完好/被破坏）
8. `<USERPROFILE>\.claude\settings.json` 包含 `hooks.PreToolUse` → 有/无（Hook 已注册/未注册）
9. 执行 `py -3 -c "import sys; print('ok')"` → 能输出 ok

---

## 6. 输出安装报告

```
========================================
  Claude Code 工作流安装报告
========================================
安装目标: <实际的 USERPROFILE\.claude\ 路径>
Python: OK / 不可用
备份: <备份文件名 或 不需要>
文件完整性: OK / 缺失 (列出缺失项)
settings.json: 已合并 / 已创建
API 配置: 完好 / 缺失
Hook 注册: 已完成 / 未完成
========================================
状态: 安装成功 / 部分失败
========================================
```

如果失败：列出具体缺失项和手工修复步骤。
如果成功：告知用户安装完毕，今后在任何目录打开 Claude Code 工作流自动生效。建议试一个简单需求验证，比如"帮我修复个拼写错误"。

---

## 禁止事项

- 不要修改 `<USERPROFILE>\.claude\settings.json` 中的 `env` 字段
- 不要删除用户已有的任何非同名文件
- 不要跳过验证步骤
- 安装过程中不要修改当前工作目录下的任何文件
