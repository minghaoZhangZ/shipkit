# ShipKit

从产品想法到代码交付的 AI 工程工作流——内置工程规范、代码审查、安全门禁，让 AI 编程按你的规则来。

## 概述

ShipKit 是一套 Claude Code 配置体系，四层架构让 AI 从需求分析到交付归档全流程可控：

- **约束层**（rules/ + CLAUDE.md）—— 工程规范固化，人先对齐再让 AI 执行
- **编排层**（skills/ + profiles/）—— 按风险等级自动匹配工作流（minimal / standard / strict）
- **执行层**（agents/）—— 16 个专项 Agent，各司其职
- **门禁层**（hooks/）—— 危险命令阻断、阶段确认、范围控制，硬拦截

之后在任何目录打开 Claude Code，直接说需求，AI 自动按流程走：需求分析 → 设计 → 计划 → 编码 → 自查 → 验证 → 审查 → 交付 → 归档。

## 前置条件

- Claude Code CLI（终端输入 `claude` 能启动）
- CCSwitch 配置好 API 连接
- Python 3（`py -3 --version` 正常输出）

Python 下载：[python.org](https://www.python.org/downloads/)（勾选 "Add Python to PATH" 和 "Install Python Launcher"）

## 安装

```bash
git clone <your-repo-url> shipkit
cd shipkit
claude
```

在 Claude Code 中输入：**按 SETUP.md 执行安装**

等待 AI 完成安装和验证，看到安装报告即完成。

## 安装完成后

在任何目录打开 Claude Code，工作流自动生效。

**试一下**：输入"帮我修复一个单词拼写错误"，观察 AI 是否走 quick-fix-flow 流程。

## 更新

```bash
cd shipkit
git pull
claude
```

输入：**重新执行 SETUP.md 安装**（安装前会自动备份已有配置）

## 常见问题

**Q: 怎么知道安装成功了？**
AI 会输出安装报告。或检查 `%USERPROFILE%\.claude\` 下是否有 rules/skills/agents 等目录。

**Q: 会影响已有配置吗？**
会备份 `settings.json` 再合并，CCSwitch 的 API 配置不受影响。
