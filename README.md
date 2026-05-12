# ShipKit
<img width="1254" height="1254" alt="舰桥" src="https://github.com/user-attachments/assets/e2931431-8e3c-40f6-a133-f6bd82d624d5" />

从产品想法到代码交付的 AI 工程工作流——把团队规范固化到 Claude Code 配置中，让 AI 按你的规则走完全流程。

---

## 快速开始

在新电脑上刚装好 Claude Code？三步接入这套工作流：

### 前置条件

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) — 终端输入 `claude` 能启动
- Python 3 — `python3 --version`（或 `py -3 --version` on Windows）正常输出

### 1. 克隆仓库

```bash
git clone https://github.com/<your-username>/shipkit.git
cd shipkit
```

### 2. 让 AI 执行安装

```bash
claude
```

在 Claude Code 中输入：

```
按 SETUP.md 执行安装
```

AI 会按 SETUP.md 中的指令自动完成以下操作：

| 步骤 | 说明 |
|------|------|
| 前置检查 | 验证 CLAUDE.md、rules/、settings.shared.json 等文件存在，Python 可用 |
| 备份 | 备份已有 `~/.claude/settings.json`（不覆盖 API 配置） |
| 复制文件 | 将 rules/、skills/、agents/、hooks/、profiles/、templates/、scripts/、commands/ 等同步到 `~/.claude/` |
| 合并配置 | 将 hooks、plugins 注入 settings.json，保留你的 API key 和 env 配置不动 |
| 验证 | 检查文件完整性、settings.json 配置正确性、Python 可用性 |
| 输出报告 | 打印安装状态和各项检查结果 |

**关键保障**：安装过程不会修改你的 API 配置（`env` 字段完全不动），不会删除已有文件（只覆盖同名文件）。

### 3. 验证安装

在任何目录打开 Claude Code，输入一个简单需求试试：

```
帮我修复一个单词拼写错误
```

观察 AI 是否自动走 quick-fix-flow（你会看到它创建 openspec changes 目录、执行代码调研等流程）。

也可以直接检查 `~/.claude/` 目录下是否存在 rules/、skills/、agents/、hooks/ 等目录。

---

## 这是什么

ShipKit 是一套 Claude Code 配置体系，用**四层架构**把工程规范固化到 AI 的行为中：

```
┌──────────────────────────────────────────────────┐
│                   约束层                          │
│  CLAUDE.md + rules/  工程规范与行为准则              │
│  "AI 应该怎么做" —— 编码风格、架构边界、安全规则        │
├──────────────────────────────────────────────────┤
│                   编排层                          │
│  skills/ + profiles/  按风险自动路由工作流            │
│  "AI 走哪个流程" —— 需求分析→设计→计划→编码→验证→审查  │
├──────────────────────────────────────────────────┤
│                   执行层                          │
│  agents/  16 个专项 Agent，各司其职                  │
│  "谁来做" —— Designer 做设计、Reviewer 做审查          │
├──────────────────────────────────────────────────┤
│                   门禁层                          │
│  hooks/  4 个 PreToolUse Hook，硬拦截              │
│  "什么不能做" —— 危险命令阻断、Checkpoint 强制确认       │
└──────────────────────────────────────────────────┘
```

核心原则：

- **角色化确认** — 产品确认 PRD，技术确认工程规格，前后端确认契约，负责人确认开工
- **AI 文档先行** — 所有 checkpoint 未确认前，只能写设计文档，不能改业务代码
- **独立验证** — 实现者不跑测试，由独立 Agent 执行验证并出具结论
- **证据驱动** — 每个架构建议、设计决策都必须有代码或文档证据

---

## 架构总览

### 文件结构

```
shipkit/
├── CLAUDE.md                  # 全局指令：语言、规范、工作流路由表
├── ARCHITECTURE.md            # 架构说明（给你的，不是给 AI 的）
├── SETUP.md                   # AI 执行的安装脚本（人可读）
├── settings.shared.json       # 公用配置（hooks、plugins），安装时合并
│
├── rules/                     # 约束层：工程规范（被 CLAUDE.md 加载）
│   ├── spring-core.md         #   Spring Boot 核心规范
│   ├── frontend/              #   前端 UI/UX 质量规范
│   ├── security/              #   安全审查规范
│   ├── architecture/          #   架构证据门、模块边界
│   ├── engineering/           #   测试质量、阿里巴巴 Java 规范
│   ├── product/               #   验收标准规范
│   ├── review/                #   Diff 审查规范
│   ├── workflow/              #   工作流核心规则（profiles、verification-loop、checkpoint 等）
│   └── learning/              #   项目经验沉淀规则
│
├── skills/                    # 编排层：29 个技能，每个对应一个工作流阶段或子流程
│   ├── product-to-test-flow/  #   标准产品需求全流程（主流程）
│   ├── quick-fix-flow/        #   小 bug、窄改动轻量流程
│   ├── strict-product-to-test-flow/  # 高风险需求严格流程
│   ├── build-fix-flow/        #   构建/编译/测试报错修复
│   ├── review-flow/           #   代码审查流程
│   ├── verification-flow/     #   独立验证流程
│   ├── learn-from-delivery/   #   交付后经验沉淀
│   ├── resume-flow/           #   会话中断后恢复工作流
│   ├── prd-check-flow/        #   PRD 产出与确认
│   ├── engineering-spec-flow/ #   工程需求规格产出
│   ├── backend-design-check-flow/  # 后端方案设计检查
│   ├── frontend-design-check-flow/ # 前端方案设计检查
│   ├── contract-check-flow/   #   接口与数据契约检查
│   ├── implementation-plan-check-flow/ # 实施计划检查
│   ├── init-engineering-consistency/  # 初始化项目工程一致性模板
│   ├── openspec-new-change/   #   创建 change workspace
│   ├── openspec-archive-change/ #  归档 change
│   ├── springboot-patterns/   #   Spring Boot 模式指导
│   ├── springboot-tdd/        #   Spring Boot TDD 测试写法
│   ├── jpa-patterns/          #   JPA 模式指导
│   ├── search-first/          #   搜索优先（避免重复造轮子）
│   ├── safety-guard/          #   安全操作守卫
│   ├── frontend-product-design/ # 前端产品设计
│   ├── frontend-verification-flow/ # 前端浏览器验证
│   ├── copy-polish-zh/        #   中文文案润色
│   ├── pdf/                   #   PDF 处理
│   ├── remotion-best-practices/ # Remotion 视频最佳实践
│   └── writing-skills/        #   编写 Skill 指南
│
├── agents/                    # 执行层：16 个专项 Agent 定义
│   ├── product-discovery-analyst.md  # 产品发现分析（产出 PRD）
│   ├── product-spec-analyst.md       # 工程需求规格分析
│   ├── codebase-researcher.md        # 代码库调研
│   ├── backend-designer.md           # 后端方案设计
│   ├── frontend-designer.md          # 前端方案设计
│   ├── data-contract-designer.md     # 接口与数据契约设计
│   ├── implementation-planner.md     # 实施计划制定
│   ├── test-planner.md               # 验证计划 + 独立验证执行
│   ├── code-reviewer.md              # 通用代码审查
│   ├── java-reviewer.md              # Java 专项审查
│   ├── database-reviewer.md          # 数据库专项审查
│   ├── security-reviewer.md          # 安全专项审查
│   ├── frontend-ux-reviewer.md       # 前端 UX 专项审查
│   ├── java-build-resolver.md        # Java 构建错误修复
│   ├── build-error-resolver.md       # 通用构建错误修复
│   └── learning-curator.md           # 经验沉淀与评估
│
├── hooks/                     # 门禁层：4 个 Python Hook，硬拦截
│   ├── dangerous-command-guard.py    # 危险命令阻断（rm -rf, force push, DROP TABLE...）
│   ├── checkpoint-guard.py           # Checkpoint 未确认时阻断业务代码修改
│   ├── scope-guard.py                # 编码阶段阻断计划外文件修改
│   └── canonical-filename-guard.py   # 非标准文档名阻断
│
├── profiles/                  # Profile 定义：minimal / standard / strict / learning
│   └── profiles.json
│
├── templates/                 # 可选：项目级工程一致性模板
│   └── engineering/
│
├── scripts/                   # 辅助脚本
│   ├── init-engineering-consistency.py  # 初始化项目工程模板
│   ├── migrate-workflow-state.py        # .workflow_state 版本迁移
│   └── validate-role-checkpoint-flow.py # 角色 checkpoint 流程校验
│
└── commands/                  # Claude Code 斜杠命令
    └── cast.md                # /cast 命令：发布 CodeCast 会话
```

---

## 工作流家族

CLAUDE.md 根据用户意图自动路由到对应工作流：

| 用户意图 | 工作流 | Profile | 适用场景 |
|---------|--------|---------|---------|
| 新功能、需求开发 | `product-to-test-flow` | standard | 普通产品需求，有前端/后端/契约变更 |
| 高风险需求 | `strict-product-to-test-flow` | strict | 安全、金钱、订单、迁移、并发、外部集成 |
| 小 bug、窄改动 | `quick-fix-flow` | minimal | 单个拼写错误、小 UI 修复、≤3 文件改动 |
| 构建/测试报错 | `build-fix-flow` | — | 编译失败、lint 报错、测试框架错误 |
| 代码审查 | `review-flow` | — | PR 审查、变更后审查 |
| 验证变更 | `verification-flow` | — | 独立验证实现是否正确 |
| 经验沉淀 | `learn-from-delivery` | learning | 需求完成后提取可复用经验 |
| 恢复进度 | `resume-flow` | — | /clear 或新会话后恢复中断的工作流 |

**你不需手动选择工作流**。直接在 Claude Code 中说需求，AI 根据 CLAUDE.md 的路由表自动匹配。

### quick-fix-flow 的准入条件

只做最小改动的轻量流程，但必须同时满足：

- 不改接口契约、数据库、权限、事务/并发、外部系统
- 不涉及安全、金钱、订单、库存、迁移、敏感数据
- 不涉及前后端同时改
- 产品语义清楚
- 预计改动文件 ≤ 3 个
- 可用一个目标测试验证

任一条件不满足，自动升级到 standard 或 strict。

---

## 工作流详解：product-to-test-flow

这是默认的标准全流程，也是 strict 和 minimal 的基座：

```
requirement ──→ prd ──→ engineering_spec ──→ research
                                                  │
            ┌─────────────────────────────────────┤
            ↓                                     ↓
   backend_design                        frontend_design
            │                                     │
            └──────────→ contract ←───────────────┘
                              │
                              ↓
                           plan ──→ coding ──→ verification ──→ review ──→ delivery ──→ archive
```

### 阶段总览

| 阶段 | 产出文档 | 执行者 | Checkpoint |
|------|---------|--------|------------|
| requirement | `00_原始需求.md` | 主控 Agent | — |
| prd | `01_PRD产品需求.md` | product-discovery-analyst | prd_confirmation（产品负责人） |
| engineering_spec | `02_工程需求规格.md` | product-spec-analyst | engineering_spec_confirmation（技术负责人） |
| research | `03_代码库调研.md` | codebase-researcher | — |
| backend_design | `04_后端方案说明.md` | backend-designer | backend_design_confirmation（后端负责人） |
| frontend_design | `05_前端方案说明.md` | frontend-designer | frontend_design_confirmation（前端负责人） |
| contract | `06_接口与数据契约.md` | data-contract-designer | contract_confirmation（前后端负责人） |
| plan | `07_实施计划.md` + `08_验证计划.md` | implementation-planner + test-planner | plan_confirmation（研发负责人） |
| coding | 业务代码 + 测试代码 | 主控 Agent（TDD 循环） | — |
| verification | `09_验证结果.md` | test-planner（独立验证模式） | — |
| review | `11_审查报告.md` | code-reviewer + 专项 reviewer | — |
| delivery | `12_发布说明.md` + `13_经验沉淀.md` + `14_Agent评估.md` + metrics | 主控 Agent + learning-curator | — |
| archive | 归档到 `openspec/changes/archive/` | openspec-archive-change | — |

> `10_自查报告.md` 已废弃。原来的机械检查交由 test-planner 验证模式的覆盖率核对步骤承担，判断性检查交由 review 阶段的独立 reviewer 承担。

### Checkpoint 机制

编码前有 6 个可能的确认点，standard 默认启用其中 3 个（prd、engineering_spec、plan），其余按 `affected_areas` 动态启用：

```
prd_confirmation ──→ engineering_spec_confirmation ──→ [backend_design_confirmation]
                                                              │
                              plan_confirmation ←── [contract_confirmation] ←── [frontend_design_confirmation]
```

每个 checkpoint 的流程：

1. 对应文档产出完成
2. `.workflow_state` 标记 `requires_user_confirmation=true`
3. AI 用 `AskUserQuestion` 请求对应角色确认
4. **确认前**：checkpoint-guard hook 拦截所有业务代码修改和构建/测试命令，只允许写入 `openspec/changes/*/ai/` 下的 AI 文档
5. **确认后**：解锁下一阶段

### 编码阶段：TDD 循环

编码阶段由主控 Agent 执行，必须遵循测试先行：

1. 从 `08_验证计划.md` 找到对应测试用例
2. 先写测试代码 → 运行确认失败（red）
3. 写最小业务实现 → 运行确认通过（green）
4. 循环直到当前任务所有测试覆盖

scope-guard hook 在编码和验证阶段持续拦截 `07_实施计划.md` 第 7 节"允许修改的文件范围"之外的文件编辑。

### 验证阶段：独立执行

**验证由独立 Agent（test-planner 验证模式）执行，主控 Agent 不跑测试、不判断测试结果。** 验证完成后 `verification-flow` 做硬停止检查——`09_验证结果.md` 必须包含 test-planner 的独立评估结论标记，否则不得进入 review。

修复循环分级（详见 `rules/workflow/verification-loop.md`）：

| 级别 | 失败类型 | 执行者 |
|------|---------|--------|
| L1 | 构建/编译/基础设施错误 | build-error-resolver |
| L2 | 断言失败/覆盖缺口（首次） | 主控 Agent 修复 → 重新调用 test-planner 验证 |
| L3 | 同组件连续两次失败 | code-reviewer 诊断，主控不得继续修 |
| L4 | 连续三次失败 | 强制停止，写 PENDING_DECISIONS，人工介入 |

---

## Profile 分级

| 维度 | minimal | standard | strict |
|------|---------|----------|--------|
| 适用场景 | 小 bug、窄改动 | 普通产品需求 | 安全、金钱、数据迁移等 |
| Checkpoint | 无（自动确认） | prd + engineering_spec + plan | engineering_spec + contract + plan |
| 设计文档 | 不强制 | 按需（backend/frontend/contract） | 强制 engineering_spec + contract |
| 验证深度 | 目标测试命令 | 覆盖率核对 + 全量测试 | +安全/数据库/回滚检查 |
| 审查 | 主控自查 diff | 独立 reviewer | 独立 reviewer + 专项审查 |
| 经验沉淀 | 不强制 | 必须 | 必须 |
| 准入条件 | ≤3 文件、不改契约/DB/权限 | 默认 | 安全/金钱/订单/迁移/并发/外部集成 |

**自动升级规则**：minimal 在执行中检测到权限变更、事务改动、外部集成、DB 变更、API 契约变更、前后端同时改动、产品语义不清、或预计超 3 个文件时，自动升级到 standard。涉及安全/金钱/订单/库存/迁移/敏感数据时升级到 strict。

---

## Agent 体系

16 个 Agent 按职责分为四类：

### Designer（只做设计，不改业务代码）

| Agent | 产出 |
|-------|------|
| product-discovery-analyst | `01_PRD产品需求.md` |
| product-spec-analyst | `02_工程需求规格.md` |
| codebase-researcher | `03_代码库调研.md` |
| backend-designer | `04_后端方案说明.md` |
| frontend-designer | `05_前端方案说明.md` |
| data-contract-designer | `06_接口与数据契约.md` |
| implementation-planner | `07_实施计划.md` |
| test-planner | `08_验证计划.md` + `09_验证结果.md`（验证模式） |

### Reviewer（只做审查，不改业务代码）

| Agent | 审查范围 |
|-------|---------|
| code-reviewer | 通用代码审查（需求覆盖、范围、质量） |
| java-reviewer | Java/Spring Boot 专项 |
| database-reviewer | SQL、索引、迁移回滚 |
| security-reviewer | 认证、授权、注入、敏感数据 |
| frontend-ux-reviewer | 前端交互、状态、响应式 |

### Resolver（修复明确的错误）

| Agent | 修复范围 |
|-------|---------|
| java-build-resolver | Java/Maven/Gradle 编译和测试错误 |
| build-error-resolver | 通用构建/lint/typecheck 错误 |

### Curator（经验管理）

| Agent | 职责 |
|-------|------|
| learning-curator | 交付后提取可复用经验，评估 Agent 表现，推荐晋升候选 |

### 如何调整 Agent

每个 Agent 定义文件在 `agents/<name>.md`，包含以下可调整部分：

```markdown
---
name: code-reviewer
description: ...          # Agent 用途描述
tools: Read, Grep, Glob, Bash, Write  # 允许使用的工具集
model: sonnet             # 运行模型：sonnet / opus / haiku
---

你是只读审查 Agent...      # 系统提示词
```

调整方式：

- **换模型**：修改 `model:` 字段（sonnet → opus 获得更强推理，或 haiku 降低成本）
- **加权限**：修改 `tools:` 字段（加上 `Edit` 让 Agent 能写代码，加上 `Bash` 能执行命令）
- **改行为**：直接编辑提示词内容，调整审查重点、输出格式等
- **加新 Agent**：复制现有 Agent 文件，修改 name/description/tools/model 和提示词即可
- **禁用 Agent**：从 `profiles/profiles.json` 对应 profile 的 `requiredAgents` 中移除，或直接删除 agent 文件

Agent 按需调用，不会自动全部加载。每个 profile 的 `profiles.json` 中定义了该 profile 的必需 Agent 和可选 Agent。

---

## Hooks 门禁系统

4 个 PreToolUse Hook，在每次工具调用前执行，返回 exit 2 则硬拦截：

### 1. dangerous-command-guard.py

拦截以下危险命令（任何阶段）：

- `rm -rf`、`git reset --hard`、`git push --force`、`git clean -f`
- `DROP TABLE`、`DROP DATABASE`、`TRUNCATE TABLE`
- `curl | sh`、`wget | sh`
- `--no-verify`（跳过 git hooks）
- Windows 下的 `Remove-Item -Recurse -Force`、`format`、`diskpart`

被拦截时，工具调用不执行，AI 收到错误说明并自我修正。

### 2. checkpoint-guard.py

当 `.workflow_state` 中 `requires_user_confirmation=true` 且 `user_confirmed=false` 时：
- **拦截**业务代码的 Write/Edit 操作、构建/测试/提交类 Bash 命令
- **允许**只读查询命令、`openspec/changes/*/ai/` 下的文档写入
- `.workflow_state` 格式损坏时 fail-closed（拦截所有业务代码操作）

### 3. scope-guard.py

编码和验证阶段（`current_phase=coding|verification`）：
- 读取 `07_实施计划.md` 第 7 节"允许修改的文件范围"
- 拦截范围外的文件编辑
- 实施计划缺失或无法解析时 fail-closed

### 4. canonical-filename-guard.py

拦截在 `openspec/changes/*/ai/` 下创建非标准文件名的文档：
- 只允许中文 canonical 名（如 `01_PRD产品需求.md`），不允许英文旧名（如 `01_PRODUCT_DISCOVERY.md`）
- 只检查 .md 和 .json 文件，不影响图片、脚本等其他文件
- 白名单中的 meta 文件（CONTEXT_PACKAGE.md、.workflow_state 等）放行

---

## Change Workspace

每个需求在项目中有一个独立的 change 目录：

```
项目根目录/
└── openspec/
    └── changes/
        └── 2026-05-13-feature-recommend-增加推荐理由/
            ├── ai/                          # AI 产出的所有文档
            │   ├── .workflow_state          # 工作流状态机（阶段、task、checkpoint）
            │   ├── CONTEXT_PACKAGE.md       # 上下文包（每阶段更新，子 Agent 入口）
            │   ├── CHANGE_METRICS.json      # 变更指标
            │   ├── PENDING_DECISIONS.md     # 待决策项
            │   ├── 00_原始需求.md
            │   ├── 01_PRD产品需求.md
            │   ├── ...                      # 02-14 号文档
            │   └── 14_Agent评估.md
            └── specs/                       # 规格产物
```

**上下文恢复**：会话 `/clear` 或新会话后，CLAUDE.md 的 Session Resume Rule 自动查找最近的 `.workflow_state` 并恢复工作进度。

---

## 项目一致性治理（可选）

ShipKit 提供可选的"团队工程一致性"增强层，默认未启用。

### 启用方式

在项目根目录执行：

```
初始化团队工程一致性模板
```

AI 调用 `init-engineering-consistency` skill，将 `templates/engineering/` 复制到 `openspec/specs/engineering/`，并创建 `engineering.json`。初始化后 `enabled=false`，团队需要：

1. 填写 `project.name`、`project.description`
2. 填写各 `ownerRoles`
3. 审批后将 `enabled` 设为 `true`
4. 按需将 `mode` 从 `advisory` 改为 `enforced`

### 两种模式

| 模式 | 行为 |
|------|------|
| `advisory` | 增强检查只记录风险，不阻断流程 |
| `enforced` | 确定性违反项、一致性 review 失败、未处理的 owner decision 均可阻断归档 |

未启用时，hooks 只执行 Base Flow 安全门禁，不强制读取工程事实库。

---

## 前置条件

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)（终端输入 `claude` 能启动）
- Python 3（`python3 --version` 正常输出，仅用于 hooks）

Python 下载：[python.org](https://www.python.org/downloads/)

---

## 安装

```bash
git clone https://github.com/<your-username>/shipkit.git
cd shipkit
claude
```

在 Claude Code 中输入：

```
按 SETUP.md 执行安装
```

AI 自动完成备份、复制、合并、验证全部步骤。

## 安装完成后

在任何目录打开 Claude Code，工作流自动生效。

**试一下**：输入"帮我修复一个单词拼写错误"，观察 AI 是否走 quick-fix-flow 流程。

---

## 更新

```bash
cd shipkit
git pull
claude
```

输入：

```
重新执行 SETUP.md 安装
```

安装前会自动备份已有配置，API 配置不受影响。

---

## 自定义

### 添加自己的 rule

在 `rules/` 下新建 `.md` 文件（如 `rules/my-team-rules.md`），安装时会同步到 `~/.claude/rules/`。CLAUDE.md 会自动加载 rules/ 目录下的所有文件。

### 调整 profile

编辑 `profiles/profiles.json`，修改各 profile 的 `requiredSkills`、`requiredAgents`、`checkpoints`、`qualityGate`、升级条件等。

### 禁用某个 skill 或 agent

从 `profiles.json` 对应 profile 的列表中移除即可。不影响其他 profile。

### 项目级规范（不跟仓库走）

如果你的团队想定义项目特定的工程规范而不修改 ShipKit 仓库本身，启用项目一致性治理（见上文），所有项目级规范写入 `openspec/specs/engineering/`。

---

## 常见问题

**Q: 怎么知道安装成功了？**
AI 会输出安装报告，逐项列出检查结果。或手动检查 `~/.claude/` 下是否有 rules/、skills/、agents/、hooks/ 等目录，以及 `~/.claude/settings.json` 是否包含 `hooks.PreToolUse`。

**Q: 会影响我已有的 API 配置吗？**
不会。`settings.shared.json` 合并时 `env` 字段完全不动，你的 API key、CCSwitch 配置等不受影响。

**Q: 安装后所有项目都走这套流程吗？**
只有工作目录下存在 `openspec/` 或有 `.claude/` 的项目才会触发完整工作流。其他目录下 Claude Code 照常工作，但全局 rules 和 agents 依然可用。

**Q: 怎么临时跳过某个 checkpoint？**
在 `.workflow_state` 中将对应 checkpoint 手动加入 `confirmed_checkpoints`，或将 `requires_user_confirmation` 设为 `false`。不建议在生产需求中跳过。

**Q: 能不能只用部分功能？**
可以。你可以只复制 rules/（要规范不要流程），或只复制 hooks/（要门禁不要流程），或只复制 agents/（要专项 Agent 不要流程）。SETUP.md 的安装是全量的，但你也可以手动选择复制的目录。

**Q: 怎么卸载？**
删除 `~/.claude/` 下对应的文件即可。如果之前有备份的 `settings.json`，恢复备份文件。
