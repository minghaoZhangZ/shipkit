---
name: product-to-test-flow
description: Use when a normal product requirement needs end-to-end delivery from product discovery through tests, review, release notes, and learning.
---

# Product To Test Flow（渐进式披露架构）

## 核心设计原则

- **按需加载**：只披露当前阶段要做什么，不提前暴露后续阶段细节。
- **状态外置**：阶段状态写入 `<change-dir>/ai/.workflow_state`，不依赖对话上下文记忆。
- **循环收敛**：编码↔验证循环最多 3 轮，第 4 轮强制出口。
- **问题分流**：验证阶段区分 Bug修复（3轮内收敛）和需求变更（回退设计阶段）。

## 工作流入口（始终加载）

收到需求后，执行以下决策树：

```
判断任务类型：
├── 小 bug / 小改动 → 先检查是否满足 minimal 条件（见下方）→ 是 → minimal
│                                                   → 否 → standard
├── 常规产品需求     → profile=standard → 加载 standard-profile
├── 高风险需求       → profile=strict → 加载 strict-profile
└── 不确定           → 问用户要哪个 profile
```

**minimal profile 准入条件（必须同时满足，任一不满足则至少 standard）**：

- 不涉及接口兼容性变化（不改变已有 API 的字段/类型/语义）
- 不涉及数据库 schema 或 migration
- 不涉及权限、鉴权、金额、订单、库存
- 不涉及并发、异步消息、外部集成
- 不新增依赖（pom.xml / build.gradle / package.json 不变）
- 不改变 public API 行为
- 可用一个目标测试或最小复现命令验证
- 改动文件数 ≤ 3

如果无法确定，必须询问用户选择 profile。

**所有 profile 共享的约束**：
- 每个阶段完成后，更新 `<change-dir>/ai/.workflow_state` 文件
- 每轮对话开始时，先读 `.workflow_state` 确认当前阶段
- 阶段间跳转必须经过 Checkpoint 决策，不允许跳过

## 可插拔一致性治理（始终加载）

本工作流默认运行 **Base Flow**，不要求项目配置全局事实库。只有检测到项目根目录存在 `openspec/specs/engineering/engineering.json` 且 `enabled=true` 时，才启用 **Enhanced Flow**。

### Capability Detection

每次创建或恢复 change 时执行：

1. 查找 `<project-root>/openspec/specs/engineering/engineering.json`。
2. 文件不存在、解析失败、`enabled=false` 或 `mode=off` → 使用 Base Flow。
3. `enabled=true` → 读取 `mode` 和 `modules`，启用对应 Enhanced 能力。
4. 将探测结果写入 `.workflow_state`。

默认值（无 manifest 时必须使用）：

```yaml
project_consistency_enabled: false
engineering_manifest: ""
engineering_mode: "off"          # off / advisory / enforced
self_review_mode: "base"         # base / enhanced
metrics_mode: "change_only"      # change_only / project_ledger
sop_mode: "candidate_only"       # candidate_only / registry
consistency_review_required: false
architecture_owner_required: false
self_review_status: "pending"
self_review_issue_count: 0
metrics_recorded: false
```

Enhanced Flow 规则：

- `mode=advisory`：增强检查只记录风险，不阻断归档。
- `mode=enforced`：增强检查作为 review/archive 门禁。
- 未启用 manifest 时，不得强制读取 `openspec/specs/engineering/*`，不得强制生成 `PROJECT_CONSISTENCY_REVIEW.md`，不得强制写 `metrics-ledger.jsonl` 或 `sop-registry.md`。

## 状态文件格式

每进入新阶段或完成一轮循环时，更新 `<change-dir>/ai/.workflow_state`。

**Hook 依赖以下字段做硬拦截，必须保持格式一致**（每行 `key: value`，不含前导空格）：

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
pending_docs: ["09", "10"]
bug_count: 0
known_issues: []
uncovered_req_ids: []
pending_decisions_count: 0
project_consistency_enabled: false
engineering_manifest: ""
engineering_mode: "off"
self_review_mode: "base"
metrics_mode: "change_only"
sop_mode: "candidate_only"
consistency_review_required: false
architecture_owner_required: false
self_review_status: "pending"
self_review_issue_count: 0
metrics_recorded: false
created_at: "2026-05-04T15:00"
updated_at: "2026-05-04T19:00"
```

**Hook 读取的关键字段**：

| 字段 | 取值 | Hook 行为 |
|------|------|-----------|
| `requires_user_confirmation` | `true` / `false` | `true` 时启用门禁检查 |
| `user_confirmed` | `true` / `false` | `false` 时拦截业务代码修改 |
| `checkpoint` | `spec_confirmation` / `plan_confirmation` | 用于拦截消息中的阶段标识 |
| `confirmation_type` | `approve_spec` / `approve_implementation_plan` | 用于拦截消息中的确认类型 |
| `current_phase` | `analysis` / `design` / `plan` / `coding` / `self_review` / `verification` / `review` / `delivery` / `archive` | scope-guard 只在 `coding`/`verification` 阶段激活 |
| `project_consistency_enabled` | `true` / `false` | 是否启用 Enhanced Flow |
| `engineering_mode` | `off` / `advisory` / `enforced` | 控制增强检查是否阻断 |
| `self_review_mode` | `base` / `enhanced` | 控制 self-review checklist 深度 |
| `metrics_mode` | `change_only` / `project_ledger` | 控制是否写项目级 metrics ledger |

**各阶段必须更新的字段**：

| 阶段切换 | 必须设置 |
|---------|---------|
| 进入 analysis | `current_phase=analysis`, `requires_user_confirmation=false`, `user_confirmed=true` |
| analysis 完成，等待确认 | `checkpoint=spec_confirmation`, `requires_user_confirmation=true`, `user_confirmed=false`, `confirmation_type=approve_spec` |
| 用户确认 spec | `user_confirmed=true`, `requires_user_confirmation=false`, `current_phase=design` |
| 进入 plan | `current_phase=plan` |
| plan 完成，等待确认 | `checkpoint=plan_confirmation`, `requires_user_confirmation=true`, `user_confirmed=false`, `confirmation_type=approve_implementation_plan` |
| 用户确认 plan | `user_confirmed=true`, `requires_user_confirmation=false`, `current_phase=coding` |
| 进入 self-review | `current_phase=self_review`, `self_review_status=pending` |
| 进入 verification | `current_phase=verification` |
| 进入 review | `current_phase=review` |
| 进入 delivery | `current_phase=delivery` |
| 归档 | `current_phase=archive` |

## Phase 路由（按 Profile 裁剪）

不同 Profile 加载不同阶段：

| 阶段 | minimal | standard | strict |
|------|---------|----------|--------|
| 需求分析 | 简版 | 完整 | 完整 |
| 产品发现 | 跳过 | 完整 | 完整 |
| 代码库调研 | 跳过 | 完整 | 完整 |
| 后端设计 | 跳过 | 按需 | 完整 |
| 数据契约 | 跳过 | 按需 | 完整 |
| 实施计划 | 简版 | 完整 | 完整 |
| 测试计划 | 简版 | 完整 | 完整 |
| 用户确认 | 跳过 | 强制暂停 | 强制暂停 |
| 编码 | 完整 | 完整 | 完整 |
| 自查 | Base checklist | Base/Enhanced checklist | Base/Enhanced checklist |
| 验证 | 目标测试 | 构建+测试+lint | 构建+测试+lint+安全+DB |
| 审查 | 简版（自检） | 独立Agent审查 | 独立Agent审查 |
| 交付 | RELEASE_NOTE | RELEASE_NOTE+Lessons+Eval | 全部+回滚方案 |
| 归档 | 跳过 | 完整 | 完整 |

---

## Profile 详细阶段定义

以下阶段按需加载。Agent 进入对应阶段时，从以下定义中只读取当前阶段的内容。

---

<!-- PHASE: analysis -->
### Phase: 分析（standard/strict）

1. 写入需求原文到 `00_REQUIREMENT.md`
2. 调用 `product-discovery-analyst` → `01_PRODUCT_DISCOVERY.md`
3. 调用 `product-spec-analyst` → `02_SPEC.md`
4. 验证 `02_SPEC.md` 第 11 节"需求追踪表"完整：每个原始需求片段都有 Req ID，"本次实现"列无未经确认的"否"。
5. 输出 spec 摘要。
6. 如有"待确认问题"（来自 `01_PRODUCT_DISCOVERY.md` 第 9 节或 `02_SPEC.md` 第 9 节），写入 `<change-dir>/ai/PENDING_DECISIONS.md`。

**PENDING_DECISIONS.md 格式**：

```markdown
# Pending Decisions

## DEC-001
- 来源: 02_SPEC.md 第 9 节
- 问题: REQ-004 是否本次实现？
- 影响: 不实现则需从测试计划和实施计划排除
- 状态: pending

## DEC-002
- 来源: 01_PRODUCT_DISCOVERY.md 第 9 节
- 问题: 是否需要支持多租户？
- 影响: 涉及表结构设计和权限模型
- 状态: pending
```

后续阶段（设计、计划、审查）的 Agent 发现新待确认项时，追加到此文件。状态变为 `confirmed` 时更新。

**Checkpoint — 此处必须停止，不得自动继续。**

- 更新 `.workflow_state`：`checkpoint=spec_confirmation`, `requires_user_confirmation=true`, `user_confirmed=false`, `confirmation_type=approve_spec`
- 用 `AskUserQuestion` 询问用户："Spec 是否确认？"
- 选项：确认进入设计 / 需要修改 / 跳过设计直接编码
- 用户选择前，不得调用任何 Agent、不得写入任何设计文档、不得开始编码。
- 即使用户觉得 spec 很完美，也必须等用户确认。
- **用户确认后**，更新 `.workflow_state`：`user_confirmed=true`, `requires_user_confirmation=false`, `current_phase=design`

---

<!-- PHASE: design -->
### Phase: 设计（standard/strict）

1. `search-first` 检查已有能力和依赖
2. `codebase-researcher` → `03_CODEBASE_RESEARCH.md`
3. 涉及后端 → `backend-designer` → `04_BACKEND_DESIGN.md`
4. 涉及前端 → `frontend-designer` → `05_FRONTEND_DESIGN.md`
5. 涉及接口/DB → `data-contract-designer` → `06_DATA_CONTRACT.md`

**Checkpoint**：

1. 设计文档产出完整 → 逐条对照 `02_SPEC.md` 第 11 节 Req ID，检查每个 Req ID 是否有设计覆盖。
2. 有未覆盖项 → 标注到 `.workflow_state` 的 `uncovered_req_ids`，补设计或标记为"已知缺口"后进入计划。
3. 全部覆盖 → 进入计划。
4. 证据不足 → 回到调研。

---

<!-- PHASE: plan -->
### Phase: 计划（standard/strict）

1. `implementation-planner` → `07_IMPLEMENTATION_PLAN.md`
2. `test-planner` → `08_TEST_PLAN.md`
3. 验证覆盖：检查 `.workflow_state` 的 `uncovered_req_ids`，确认 `07_IMPLEMENTATION_PLAN.md` 第 12 节和 `08_TEST_PLAN.md` 第 12 节覆盖了所有 Req ID。

**Checkpoint — 此处必须停止，不得自动继续。**

- 更新 `.workflow_state`：`checkpoint=plan_confirmation`, `requires_user_confirmation=true`, `user_confirmed=false`, `confirmation_type=approve_implementation_plan`
- 用 `AskUserQuestion` 询问用户："实施计划是否确认？"
- 选项：确认开始编码 / 需要修改计划
- 用户选择前，不得修改任何业务代码、不得运行任何构建命令。
- `uncovered_req_ids` 非空时，不得展示"确认开始编码"选项，必须先解决未覆盖项。
- 即使你觉得计划很完善，也必须等用户确认。
- **用户确认后**，更新 `.workflow_state`：`user_confirmed=true`, `requires_user_confirmation=false`, `current_phase=coding`

---

<!-- PHASE: coding -->
### Phase: 编码（所有 profile）

- 只能修改实施计划允许的文件
- Spring Boot 项目按需调用 `springboot-tdd`

**Checkpoint**：代码写完 → 进入 self-review。不得跳过 self-review 直接验证或交付。

---

<!-- PHASE: self-review -->
### Phase: 自查（所有 profile）

编码完成后，进入 `self_review` 阶段，输出 `<change-dir>/ai/10_SELF_REVIEW.md`。

#### Base Self-review（所有项目必须执行）

```markdown
# Self Review

## 1. 模式

- self_review_mode: base / enhanced
- engineering_manifest: <path or empty>

## 2. Req ID 覆盖自查

| Req ID | 代码改动 | 测试覆盖 | 状态 | 证据 |
|--------|----------|----------|------|------|

## 3. 实施计划范围自查

| 文件 | 是否在允许范围 | 说明 |
|------|----------------|------|

## 4. Base Checklist

| Check ID | 检查项 | 结果 | 证据 | 修复记录 |
|----------|--------|------|------|----------|
| SR-BASE-001 | Req ID 均有覆盖或用户确认 | pass/fail |  |  |
| SR-BASE-002 | 改动文件均在计划允许范围 | pass/fail |  |  |
| SR-BASE-003 | 无明显异常处理遗漏（空 catch、吞异常、printStackTrace） | pass/fail |  |  |
| SR-BASE-004 | 测试计划要求均有验证或说明未运行原因 | pass/fail |  |  |
| SR-BASE-005 | 无明显危险模式（硬编码密钥、SQL 拼接用户输入、无分页大列表） | pass/fail |  |  |
| SR-BASE-006 | CHANGE_METRICS.json 已更新 | pass/fail |  |  |

## 5. Enhanced Checklist

仅当 engineering.json 启用时填写；未启用时写 `not enabled`。

## 6. 自查发现问题

## 7. 已修复问题

## 8. 剩余风险
```

#### Enhanced Self-review（仅 manifest 启用时）

当 `project_consistency_enabled=true` 且 `modules.selfReviewRules=true` 时，读取 `openspec/specs/engineering/` 下已存在的规则文件，将其中的检查映射追加到 `10_SELF_REVIEW.md`。如果 `engineering_mode=advisory`，只记录风险；如果 `engineering_mode=enforced`，确定性违反项必须修复或写入 `PENDING_DECISIONS.md` 后才能进入 verification。

#### Metrics

所有 change 都写入或更新 `<change-dir>/ai/CHANGE_METRICS.json`：

```json
{
  "schemaVersion": 1,
  "changeId": "",
  "profile": "minimal|standard|strict",
  "projectConsistencyEnabled": false,
  "engineeringMode": "off|advisory|enforced",
  "counters": {
    "checkpointBlocked": 0,
    "scopeGuardBlocked": 0,
    "dangerousCommandBlocked": 0,
    "selfReviewIssuesFound": 0,
    "selfReviewIssuesFixed": 0,
    "verificationFailedRounds": 0,
    "reviewBlockers": 0,
    "pendingDecisionsCreated": 0,
    "architectureOwnerDecisionsCreated": 0,
    "sopCandidatesCreated": 0
  },
  "signals": []
}
```

**Checkpoint**：Base checklist 全部完成，确定性问题已修复或记录为剩余风险，`CHANGE_METRICS.json` 已更新 → 进入 verification。

---

<!-- PHASE: verification -->
### Phase: 验证（所有 profile）

#### 验证执行

```
运行验证命令 → 读取测试结果 → 判定：
├── 全部通过（0 fail, 0 error）
│   └── → 记录 09_TEST_RESULT.md → Checkpoint → 进审查
│
├── 部分失败 → 对每个失败分类：
│   ├── P0 阻断（编译不过/启动不了/DB连不上）
│   │   └── 必须当轮修掉，否则不计数
│   ├── P1 逻辑 bug（结果和 Spec 不符/计算公式错/NPE）
│   │   └── 修，计入本轮
│   └── P2 兼容/优化（旧版API过期/性能不够/日志缺失）
│       └── 修或记录到 OPEN_ISSUES，不阻断
│
└── 全部失败 → 检查环境/依赖 → 环境问题不计轮次
```

#### 循环收敛机制

```
Round N 结束 → 更新 .workflow_state → 判定下一步：

1. P0/P1 全部清零？
   → 进审查，即使还有 P2 未修（P2 写入 OPEN_ISSUES.md）

2. 还有 P0/P1？
   ├── round < 3 → 回编码阶段继续修
   │   但：同一组件连续 2 轮出问题 → 不是 bug，是设计缺陷
   │   → 回退设计阶段更新 Spec/设计文档
   └── round = 3 → 强制出口
       写 OPEN_ISSUES.md 列出残留 P1
       写 BUGFIX.md 汇总 3 轮修复记录
       进审查
```

#### BUGFIX.md 格式（每轮追加，轻量）

```markdown
## Round 1 (14:30)
- 修: precision 列名 MySQL 保留字冲突 → 改 precision_val, Entity字段同步
- 修: EvalItem 缺 index 字段导致 RAGAS 批量500 → 加 index 字段
- 结果: 158 tests pass, 0 fail
- 剩余: ContextRelevance 偶发返回 None

## Round 2 (15:00)  
- 修: ContextRelevance None → float(None)兜底为0
- 结果: 163 tests pass, 0 fail, 端到端检索+生成全通过
- 剩余: AnswerRelevancy 缺embeddings（design issue，回退设计）
```

不要求格式完美。**目的不是写文档，是在上下文被 bug 淹没时能一眼看到"我修到哪了"。**

#### 设计缺陷识别（"异味检测"）

以下信号出现时，判定为设计问题而非 bug，**不应再循环修复**：

| 信号 | 示例 |
|------|------|
| 同一个类/方法连续 2 轮都在改 | RAGAS app.py 三轮都在改 key 映射 |
| 修复引入了新问题 | 改了 recall 去重 → NDCG 崩了 |
| 修复依赖外部环境变化 | "等 DashScope SDK 更新后就好了" |
| 同样的 fix pattern 重复出现 | 3 个不同地方都缺 null 检查 |

判定为设计问题后 → **回退到设计阶段**更新对应设计文档，不是继续修代码。

#### Checkpoint

全部 P0/P1 清零 或 round=3 → 进审查。minimal profile 可执行简版只读 diff review 后进交付。

---

<!-- PHASE: review -->
### Phase: 审查（standard/strict）

1. 需求覆盖检查：逐条核对 Req ID → 代码改动 → 测试覆盖。有未覆盖项且无用户确认 → 审查结论"不通过"，不得继续。
2. `code-reviewer` → `11_REVIEW_REPORT.md`（旧 change 可保留 `10_REVIEW_REPORT.md`）
3. 按需：`java-reviewer` / `database-reviewer` / `security-reviewer`
4. 阻塞问题 → 修复后回到验证阶段（不计入编码轮次）
5. 非阻塞问题 → 记录到审查报告，不阻断
6. 如果 `project_consistency_enabled=true` 且 `modules.consistencyReview=true`，生成 `<change-dir>/ai/PROJECT_CONSISTENCY_REVIEW.md`：
   - `engineering_mode=advisory`：记录风险，不阻断。
   - `engineering_mode=enforced`：不通过时不得进入归档。

**Checkpoint**：覆盖检查和代码审查均通过 → 进入交付。

---

<!-- PHASE: delivery -->
### Phase: 交付（standard/strict/learning）

1. `12_RELEASE_NOTE.md`（旧 change 可保留 `11_RELEASE_NOTE.md`）
2. 如有遗留问题 → `OPEN_ISSUES.md`
3. `learning-curator` → `13_LESSONS_LEARNED.md` + `14_AGENT_EVAL.md`（旧 change 可保留 `12/13` 编号）
4. Lessons 中必须包含 SOP candidate 小节；Enhanced Flow 启用且 `modules.sopRegistry=true` 时，才更新项目级 `sop-registry.md`。

**Checkpoint**：所有文档产出 → 进入归档。

---

<!-- PHASE: archive -->
### Phase: 归档（standard/strict）

- 调用 `openspec-archive-change`
- 清理 `.workflow_state`（标记 archived）

归档前如果 `consistency_review_required=true`：

- `engineering_mode=advisory`：允许归档，但 release note / lessons 必须记录一致性风险。
- `engineering_mode=enforced`：`PROJECT_CONSISTENCY_REVIEW.md` 未通过不得归档。

---

## minimal Profile（轻量版）

小 bug 和小改动，且满足准入条件（见上方决策树）。

阶段：需求简版 → 简版计划 → 编码 → self-review → 目标验证 → 交付。

必需产出：`00_REQUIREMENT.md`（可一句话）、`07_IMPLEMENTATION_PLAN.md`（简版）、`10_SELF_REVIEW.md`、`CHANGE_METRICS.json`、`12_RELEASE_NOTE.md`（可一段话）。

约束：代码证据（改了什么文件）、验证命令和结果。

**minimal 也需维护 `.workflow_state`**：
- 开始编码前：`current_phase=coding`, `requires_user_confirmation=false`, `user_confirmed=true`
- 进入自查时：`current_phase=self_review`, `self_review_mode=base`
- 进入验证时：`current_phase=verification`
- 完成时：`current_phase=delivery`

## 编码↔验证 循环收敛示例

```
Round 1: 编译通过，158 tests pass, 4 fail → Bug修复 × 2
Round 2: 编译通过，162 tests pass, 0 fail → 全部通过 → 进审查
```

```
Round 1: 编译通过，测试全过，但生成评估分数异常
  → 判定为需求变更（生成评估设计有问题）
  → 回退设计阶段，更新 04_BACKEND_DESIGN.md
  → 重新进入编码
```

```
Round 3: 163 tests pass，但 ContextRelevance 偶发 0
  → 判定为 Bug修复，但 3 轮已满
  → 强制出口，写 OPEN_ISSUES.md："ContextRelevance 批量偶发 0，已加 None→0 兜底"
  → 进审查
```
