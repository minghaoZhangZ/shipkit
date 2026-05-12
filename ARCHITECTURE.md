# Claude Code 个人工作方式 —— 体系说明文档

> 文档生成日期：2026-05-09

---

## 一、设计理念

核心思路：**先把团队的工程共识沉淀为显式规则，再把规则固化为 AI 可执行的约束和门禁**。

分两步走：

1. **规则层**（rules/）—— 将工程规范写成结构化文档，覆盖架构、工程、安全、审查、工作流等 6 个域。这是"人跟人先对齐"。
2. **约束层**（hooks/ + profiles/ + skills/）—— 将规则转化为 AI 的行为边界：什么时候该暂停让用户确认、什么文件不能改、什么命令不能执行。这是"让 AI 按人的规则来"。

顺序不能反——人自己都没共识的东西，写成 AI Rule 就是废纸。

---

## 二、总体架构

```
┌──────────────────────────────────────────────────────────────┐
│                      CLAUDE.md（Always Loaded）               │
│  语言/推理/编码风格/变更范围/Java规范/质量门禁/工作流路由表      │
└──────────────────────────┬───────────────────────────────────┘
                           │ 路由到对应 Skill
    ┌──────────────────────┼──────────────────────────┐
    ▼                      ▼                          ▼
┌──────────┐    ┌──────────────────┐    ┌─────────────────────┐
│ profiles/│    │    skills/        │    │     agents/         │
│ 定义什么  │───▶│   工作流编排       │───▶│   专项能力执行        │
│ 阶段+谁  │    │   (编排层)         │    │   (执行层)           │
└──────────┘    └────────┬─────────┘    └─────────────────────┘
                         │ 读写
                         ▼
              ┌─────────────────────┐
              │ .workflow_state     │  ← 状态外置，跨对话保持
              │ CHANGE_METRICS.json │  ← per-change 指标
              │ <change-dir>/ai/    │  ← 阶段文档
              └────────┬────────────┘
                       │ 被读取
                       ▼
              ┌─────────────────────┐
              │     hooks/           │  ← PreToolUse 硬拦截
              │ 危险命令 / 门禁 / 范围 │     (settings.json 注册)
              └─────────────────────┘
```

**四层结构**：

- **约束层**（rules/ + CLAUDE.md）：描述"应该怎么做"，always loaded
- **编排层**（profiles/ + skills/）：描述"按什么流程做"，按需加载
- **执行层**（agents/）：描述"具体谁来做"，按需调用
- **门禁层**（hooks/）：描述"什么绝对不能做"，每次工具调用前硬检查

---

## 三、目录结构与职责

```
~/.claude/
├── CLAUDE.md                    # Always 规则 + 工作流路由表
├── settings.json                # 环境变量 + Hook 注册
├── settings.local.json          # 权限白名单
│
├── rules/                       # [约束层] 工程规范（13 个文件，6 个域）
│   ├── architecture/            # 架构规则
│   │   ├── evidence-gate.md     #   证据门禁：不猜测 API/架构意图
│   │   └── module-boundary.md   #   模块边界：跨模块依赖前必须检查的事项
│   ├── engineering/             # 工程规则
│   │   ├── alibaba-java-style.md#   阿里 Java 规范（命名/异常/日志/集合/并发）
│   │   └── testing-quality.md   #   测试质量：断言业务结果，不伪造测试
│   ├── learning/                # 学习规则
│   │   └── project-scoped-learning.md  # 经验先项目内沉淀，跨项目重复才晋升
│   ├── product/                 # 产品规则
│   │   └── acceptance-criteria.md     # 验收标准可验证、覆盖成功和失败路径
│   ├── review/                  # 审查规则
│   │   └── diff-review.md       #   审查先列问题再总结，每个问题需严重级别+位置+修复方向
│   ├── security/                # 安全规则
│   │   └── security-review.md   #   涉及登录/鉴权/支付/文件/密钥时必须安全审查
│   ├── workflow/                # 工作流规则
│   │   ├── agent-permissions.md #   Agent 权限模型（Analyst/Designer/Reviewer/Resolver/Builder）
│   │   ├── openspec-change-workspace.md  # Change 目录规范
│   │   ├── profiles.md          #   Profile 分层定义（minimal/standard/strict/learning）
│   │   └── verification-loop.md #   验证循环：没有真实命令输出就不能声称通过
│   └── spring-core.md           # Spring 综合规范（API/事务/异常/测试/JPA Entity/Query/Migration）
│
├── profiles/                    # [编排层] Profile 定义
│   ├── profiles.json            # 每个 profile 的 requiredSkills/Agents/qualityGate
│   └── README.md                # Profile 使用说明 + Enhanced Flow 触发条件
│
├── skills/                      # [编排层] 工作流 Skill（17 个）
│   ├── product-to-test-flow/    # 核心：标准产品交付流程（standard/strict）
│   ├── strict-product-to-test-flow/ # 高风险需求专用（安全/金钱/数据/并发）
│   ├── quick-fix-flow/          # 小 bug / 小改动轻量流程（minimal）
│   ├── build-fix-flow/          # 构建/编译/测试报错修复
│   ├── review-flow/             # 代码审查（先做需求覆盖，再做代码质量）
│   ├── verification-flow/       # 验证（没有命令输出就不能声称通过）
│   ├── learn-from-delivery/     # 经验沉淀（lessons + agent eval + 晋升建议）
│   ├── openspec-new-change/     # 创建 change 工作区
│   ├── openspec-archive-change/ # 归档 change
│   ├── init-engineering-consistency/ # 初始化项目工程事实库（模板脚手架）
│   ├── jpa-patterns/            # JPA Entity/Repository/Query/Migration 模式
│   ├── springboot-patterns/     # Spring Boot API/Service/Validation/Transaction
│   ├── springboot-tdd/          # Spring Boot 测试驱动开发
│   ├── springboot-verification/ # Spring Boot 变更验证
│   ├── safety-guard/            # 安全守护（高风险操作前提示确认）
│   ├── search-first/            # 新增能力前先检查是否已有现成方案
│   └── writing-skills/          # 编写和验证 Skill
│
├── agents/                      # [执行层] 专项 Agent（16 个）
│   ├── product-discovery-analyst.md  # 产品发现（用户目标/痛点/场景）
│   ├── product-spec-analyst.md       # 需求规格（验收标准/需求追踪表）
│   ├── codebase-researcher.md        # 代码库调研（模块边界/现有模式/风险）
│   ├── backend-designer.md           # 后端设计（API/Service/领域模型）
│   ├── frontend-designer.md          # 前端设计（页面/组件/路由/状态）
│   ├── data-contract-designer.md     # 数据契约（DTO/Schema/迁移/兼容性）
│   ├── implementation-planner.md     # 实施计划（文件范围/步骤/停止条件）
│   ├── test-planner.md               # 测试计划（测试范围/风险分级/覆盖矩阵）
│   ├── code-reviewer.md              # 代码审查（覆盖/架构/安全/性能/测试）
│   ├── database-reviewer.md          # 数据库审查（SQL/Schema/索引/迁移/事务）
│   ├── security-reviewer.md          # 安全审查（注入/越权/SSRF/密钥泄露）
│   ├── java-reviewer.md              # Java 专项审查
│   ├── java-build-resolver.md        # Java 构建/编译/测试报错修复
│   ├── build-error-resolver.md       # 通用构建/编译/依赖报错修复
│   ├── learning-curator.md           # 经验沉淀与晋升建议
│   └── test-planner.md               # (同 implementation-planner.md 一起工作)
│
├── hooks/                       # [门禁层] PreToolUse 硬拦截
│   ├── dangerous-command-guard.py  # 危险命令阻断（20+ 模式：rm -rf/force push/DROP TABLE/curl|sh...）
│   ├── checkpoint-guard.py         # 阶段门禁（用户未确认时拦截业务代码编辑和构建命令）
│   ├── scope-guard.py              # 范围门禁（coding/verification 阶段拦截计划外文件修改）
│   └── README.md                   # Hook 设计文档 + Roadmap（Phase 2/3 规划）
│
├── templates/                   # 模板（仅用于初始化，内容由团队填写）
│   └── engineering/             # 项目工程事实库模板
│       ├── engineering.json         # 清单开关（enabled/mode/status）
│       ├── architecture-principles.md  # 架构原则
│       ├── dependency-rules.md         # 依赖规则
│       ├── domain-concepts.md          # 领域概念
│       ├── module-boundaries.md        # 模块边界与 public API
│       ├── reusable-apis.md            # 可复用 API
│       ├── forbidden-patterns.md       # 禁止模式
│       └── sop-registry.md             # SOP 注册表
│
└── scripts/
    └── init-engineering-consistency.py  # 一键初始化项目 openspec/specs/engineering/
```

---

## 四、核心机制详解

### 4.1 Profile 分层体系

4 个 Profile，按风险等级逐级增强。定义在 `profiles/profiles.json`：

| Profile | 适用场景 | requiredSkills | requiredAgents | qualityGate |
|---------|---------|----------------|----------------|-------------|
| **minimal** | 小 bug、≤3 文件、不改 API/DB/权限/依赖 | openspec-new-change, quick-fix-flow, verification-flow | codebase-researcher, code-reviewer | Base self-review + CHANGE_METRICS + 目标测试 |
| **standard** | 常规产品需求（默认） | openspec-new-change, product-to-test-flow, verification-flow, learn-from-delivery, openspec-archive-change | product-discovery-analyst, product-spec-analyst, codebase-researcher, implementation-planner, test-planner, code-reviewer, learning-curator | 实施计划和测试计划编码前确认；self-review + 验证证据 after coding |
| **strict** | 安全/金钱/订单/迁移/并发/外部集成 | strict-product-to-test-flow + 同 standard | codebase-researcher, data-contract-designer, test-planner, code-reviewer, database-reviewer, security-reviewer | standard + 回滚方案 + 安全审查 + 数据库审查 |
| **learning** | 交付后经验沉淀 | learn-from-delivery, openspec-archive-change | learning-curator | 每条 lesson 含触发场景/证据/复用路径/晋升建议 |

**minimal 准入条件**（任一不满足则至少 standard）：
- 不涉及接口兼容性变化
- 不涉及数据库 schema 或 migration
- 不涉及权限、鉴权、金额、订单、库存
- 不涉及并发、异步消息、外部集成
- 不新增依赖
- 不改 public API 行为
- 改动文件数 ≤ 3

### 4.2 工作流状态机

`product-to-test-flow` 定义完整状态机，状态写入 `<change-dir>/ai/.workflow_state` 文件（跨对话保持）：

```
analysis → design → plan → coding → self_review → verification → review → delivery → archive
    ↑                                                    │                    │
    └──────────────── 回退（设计缺陷）────────────────────┘                    │
                         ↑                                                    │
                         └──────── 编码↔验证循环（max 3 rounds）──────────────┘
```

**关键设计决策**：

- **状态外置**：不依赖对话上下文记忆。每轮对话开始时先读 `.workflow_state` 确定当前阶段。
- **两个强制确认点**：`spec_confirmation`（需求确认）和 `plan_confirmation`（计划确认），必须用 `AskUserQuestion` 获得用户明确同意后才能继续。未确认前，Hook 会硬拦截业务代码的编辑和构建命令。
- **循环收敛**：编码↔验证循环最多 3 轮。超过 3 轮强制出口，不允许无限修 bug。
- **异味检测**：同一文件连续 2 轮出问题 → 判定为设计缺陷而非 bug → 回退设计阶段，不继续编码。
- **问题分流**：验证阶段区分 P0（编译/启动）、P1（逻辑错误）、P2（兼容/优化）。P0/P1 必须清零，P2 可记录到 OPEN_ISSUES 不阻断。

### 4.3 三级 Hook 门禁

所有 Hook 通过 `settings.json` 的 `PreToolUse` 注册，在工具调用**之前**执行。退出码 `exit 0` = 放行，`exit 2` = 硬阻断（stderr 反馈给 Claude 自我纠正）。

| Hook | 触发工具 | 阻断条件 | 特点 |
|------|---------|---------|------|
| `dangerous-command-guard` | Bash | 匹配 20+ 危险模式 | 全阶段生效，管物理安全 |
| `checkpoint-guard` | Write / Edit / Bash | `.workflow_state` 中 `requires_user_confirmation=true` 且 `user_confirmed=false` | 管流程合规，但始终允许写 AI 文档 |
| `scope-guard` | Write / Edit | `current_phase` 为 coding/verification 时，文件不在实施计划允许范围 | 管范围控制，只在编码和验证阶段激活 |

**状态格式校验**：`checkpoint-guard` 和 `scope-guard` 在读 `.workflow_state` 后会校验必需字段（`current_phase`, `requires_user_confirmation`, `user_confirmed`）是否完整且合法。格式错误时 fail-closed（exit 2），不会静默放行。

**设计原则**：
- Hook 只做确定性检查（模式匹配、字段比对），不做判断型分析。
- 判断型发现（代码质量、设计问题）走 Agent 审查路径，不放到 Hook 里。
- 脚本纯标准库，无外部依赖，执行耗时 < 50ms。

### 4.4 可插拔一致性治理（Base Flow + Enhanced Flow）

**Base Flow**（默认）：不依赖任何项目级配置。任何项目、任何仓库都能直接工作。

**Enhanced Flow**（可选增强）：当项目根目录存在 `openspec/specs/engineering/engineering.json` 且 `enabled=true` 时自动激活。

```
检测逻辑：
  openspec/specs/engineering/engineering.json 存在?
  ├─ 否 → Base Flow（约束层只有 rules/ 和 hooks/）
  └─ 是 → 读 mode 字段
          ├─ mode=advisory → 增强检查记录风险，不阻断
          └─ mode=enforced → 确定性违反可阻断 review/archive
```

Enhanced Flow 影响的范围：
- **self-review**：在 Base Checklist 6 项之上，追加项目工程事实库中的检查规则
- **review**：生成 `PROJECT_CONSISTENCY_REVIEW.md`，检查是否违反 forbidden-patterns、module-boundaries 等
- **archive**：enforced 模式下，一致性 review 不通过不能归档
- **metrics**：per-change metrics 追加到项目级 `metrics-ledger.jsonl`
- **SOP**：跨 change 重复出现 3 次以上的模式可注册到 `sop-registry.md`

**初始化**：由用户显式调用 `init-engineering-consistency` skill，将 `templates/engineering/` 下的模板拷贝到项目 `openspec/specs/engineering/`。模板是脚手架（占位符），具体内容由团队达成共识后人工填写。默认 `enabled=false, mode=advisory, status=draft`，保证初始化后不会意外激活。

### 4.5 Per-Change 指标采集

每个 change 目录维护 `CHANGE_METRICS.json`，记录本次变更的关键指标：

```json
{
  "counters": {
    "checkpointBlocked": 0,        // checkpoint-guard 拦截次数
    "scopeGuardBlocked": 0,        // scope-guard 拦截次数
    "dangerousCommandBlocked": 0,  // 危险命令拦截次数
    "selfReviewIssuesFound": 0,    // 自查发现的问题数
    "selfReviewIssuesFixed": 0,    // 自查已修复数
    "verificationFailedRounds": 0, // 验证失败轮次
    "reviewBlockers": 0,           // 审查阻塞项数
    "pendingDecisionsCreated": 0,  // 待确认决策数
    "sopCandidatesCreated": 0      // SOP 候选数
  }
}
```

用途：
- 个人复盘时快速了解该 change 的"摩擦力"（阻塞次数多 → 流程或需求可能有问题）
- Enhanced Flow 启用时，归档阶段追加到项目级 `metrics-ledger.jsonl`，用于后续 SOP 晋升信号

---

## 五、数据流全景

```
用户发起需求
    │
    ▼
CLAUDE.md（判断意图 → 匹配 Profile）
    │
    ├─ 新需求 → openspec-new-change（创建 change 目录 + .workflow_state）
    │              │
    │              ▼
    │         product-to-test-flow（按 profile 执行阶段）
    │              │
    │              ├─ Phase: analysis  → product-discovery-analyst / product-spec-analyst
    │              ├─ Phase: design    → search-first / codebase-researcher / backend-designer ...
    │              ├─ Phase: plan      → implementation-planner / test-planner
    │              │     │
    │              │     └─ checkpoint (plan_confirmation) → AskUserQuestion → 用户确认
    │              │                                          │
    │              │                        ┌─ Hook: checkpoint-guard 检查 user_confirmed
    │              │                        │
    │              ├─ Phase: coding ────────┤
    │              │                        ├─ Hook: scope-guard 检查 Section 7 允许范围
    │              │                        └─ Hook: dangerous-command-guard 检查危险命令
    │              │     │
    │              ├─ Phase: self_review → 10_SELF_REVIEW.md + CHANGE_METRICS.json
    │              │     │
    │              ├─ Phase: verification → 运行测试命令 → 09_TEST_RESULT.md
    │              │     │                    │
    │              │     │                    ├─ 全通过 → 进 review
    │              │     │                    ├─ 部分失败 → round+1（max 3）
    │              │     │                    └─ 同文件连续 2 轮 → 回退 design
    │              │     │
    │              ├─ Phase: review → code-reviewer (+ java/database/security reviewer)
    │              │     │
    │              ├─ Phase: delivery → release note + lessons + agent eval
    │              │     │
    │              └─ Phase: archive → openspec-archive-change
    │
    ├─ 小 bug → quick-fix-flow（简版 minimal）
    ├─ 高风险 → strict-product-to-test-flow
    ├─ 构建错误 → build-fix-flow
    ├─ 审查 → review-flow
    └─ 验证 → verification-flow
```

---

## 六、状态文件规范

### .workflow_state

位于 `<change-dir>/ai/.workflow_state`，是 Hook 和 Skill 之间的状态接口。格式：每行 `key: value`。

```yaml
change_id: "2026-05-04-feature-rag-eval-xxx"
profile: standard
current_phase: plan
checkpoint: plan_confirmation
requires_user_confirmation: true
user_confirmed: false
confirmation_type: "approve_implementation_plan"
round: 0
max_rounds: 3
project_consistency_enabled: false
engineering_manifest: ""
engineering_mode: "off"
self_review_mode: "base"
metrics_mode: "change_only"
sop_mode: "candidate_only"
```

**Hook 读取的关键字段**：

| 字段 | 读取者 | 行为 |
|------|--------|------|
| `current_phase` | checkpoint-guard, scope-guard | 决定哪个门禁激活 |
| `requires_user_confirmation` | checkpoint-guard | `true` 时启用确认检查 |
| `user_confirmed` | checkpoint-guard | `false` 时拦截业务代码 + 构建命令 |
| `checkpoint` | checkpoint-guard | 用于错误消息中的阶段标识 |
| `confirmation_type` | checkpoint-guard | 用于错误消息中的确认类型 |
| 格式不合法（缺失/错误） | checkpoint-guard, scope-guard | fail-closed → exit 2 |

**各阶段切换时 Skill 必须更新的字段**：见 `product-to-test-flow/SKILL.md` "各阶段必须更新的字段"表。

### 阶段文档编号

新流程 change 使用 00-14 编号：

| 编号 | 文件 | 产出阶段 |
|------|------|---------|
| 00 | REQUIREMENT.md | analysis |
| 01 | PRODUCT_DISCOVERY.md | analysis |
| 02 | SPEC.md | analysis |
| 03 | CODEBASE_RESEARCH.md | design |
| 04 | BACKEND_DESIGN.md | design |
| 05 | FRONTEND_DESIGN.md | design |
| 06 | DATA_CONTRACT.md | design |
| 07 | IMPLEMENTATION_PLAN.md | plan |
| 08 | TEST_PLAN.md | plan |
| 09 | TEST_RESULT.md | verification |
| 10 | SELF_REVIEW.md | self_review |
| 11 | REVIEW_REPORT.md | review |
| 12 | RELEASE_NOTE.md | delivery |
| N/A | CHANGE_METRICS.json | self_review + 各阶段更新 |
| 13 | LESSONS_LEARNED.md | delivery |
| 14 | AGENT_EVAL.md | delivery |

（旧 change 可能保留旧编号，如 10_REVIEW_REPORT.md、11_RELEASE_NOTE.md、12_LESSONS_LEARNED.md、13_AGENT_EVAL.md）

---

## 七、关键设计选择

### 为什么 Hook 用 Python 脚本而不是配置文件

这 3 个 Hook 需要逻辑判断（正则匹配危险命令、解析 `.workflow_state`、解析实施计划 Section 7、glob 匹配文件路径），纯声明式配置表达能力不够。标准库实现，无 pip 依赖，Windows/macOS/Linux 都能跑。

### 为什么状态放文件里而不是依赖对话上下文

对话上下文会压缩、会丢失、模型切换后不存在。文件是 single source of truth，Hook（Python 进程）和 Skill（AI 模型）都能读。

### 为什么 Enhanced Flow 默认关闭

`engineering.json` 默认 `enabled=false`。这意味着没有团队共识的项目不会因为"缺了某个配置文件"而被阻断。Base Flow 的约束层（rules/ + hooks/）已经提供了足够的个人级保护。

### 为什么编码↔验证循环限制 3 轮

无限制循环意味着同一个 bug 可以反复修、反复引入新问题，对话上下文被 bug 淹没。3 轮是经验值——如果 3 轮还修不好，大概率不是 bug 而是设计问题。

---

## 八、当前状态与后续方向

### 已就绪

- [x] 6 域 13 个 rules 文件（约束层）
- [x] 4 个 profile 定义（minimal / standard / strict / learning）
- [x] 核心 product-to-test-flow 完整状态机（9 个阶段 + 2 个强制确认点）
- [x] 3 个 PreToolUse Hook（含 fail-closed 状态校验）
- [x] 16 个专项 Agent
- [x] Base Flow + 可插拔 Enhanced Flow
- [x] Per-change metrics 采集
- [x] 编码↔验证循环收敛（round ≤ 3 + 异味检测）
- [x] PENDING_DECISIONS 追踪机制

### 后续方向

| 优先级 | 事项 | 触发条件 |
|--------|------|---------|
| 中 | 在一个真实项目上跑通 Enhanced Flow 端到端 | 下一个新项目启动 |
| 中 | Phase 2 Hook（java-light-quality-gate, test-result-check） | 按 hooks/README.md Roadmap |
| 低 | 项目级 metrics 汇总脚本 | Enhanced Flow 跑了 10+ 个 change |
| 低 | 多模型对抗审查 | 团队扩展到 3 人以上 |
