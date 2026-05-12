---
name: product-to-test-flow
description: Use when a normal product requirement needs end-to-end delivery from product discovery through tests, review, release notes, and learning.
---

# Product To Test Flow

本流程只做路由和门禁，不承载具体模板细节。阶段细节由专项 skill 和 agent 负责，主控 Agent 负责最终编码实现。

## 核心原则

- **角色化确认**：产品确认 PRD，技术确认工程规格，前端确认交互，后端确认架构，前后端确认契约，负责人确认开工。
- **渐进式披露**：当前阶段只加载当前阶段的 skill、agent、输入包和规范。
- **上下文不丢失**：每阶段开始前更新 `CONTEXT_PACKAGE.md`，每阶段输出必须有 Req ID 覆盖映射。
- **AI 文档先行**：所有 checkpoint 未确认前，只能写 `openspec/changes/*/ai/` 下的 AI 文档，不得修改业务代码。
- **主控实现**：designer/reviewer/planner 只产出文档或审查意见；业务代码由主控 Agent 按 `07_实施计划.md` 执行。

## 文档标准

新流程必须写中文 canonical 文档名。旧 change（2026-05-15 前创建）可能使用英文旧名，读取时兼容但新输出一律使用中文名。

| 阶段 | 新文档 | 旧兼容名 |
|---|---|---|
| 原始需求 | `00_原始需求.md` | `00_REQUIREMENT.md` |
| 产品需求 | `01_PRD产品需求.md` | `01_PRODUCT_DISCOVERY.md` |
| 工程规格 | `02_工程需求规格.md` | `02_SPEC.md` |
| 代码调研 | `03_代码库调研.md` | `03_CODEBASE_RESEARCH.md` |
| 后端方案 | `04_后端方案说明.md` | `04_BACKEND_DESIGN.md` |
| 前端方案 | `05_前端方案说明.md` | `05_FRONTEND_DESIGN.md` |
| 接口契约 | `06_接口与数据契约.md` | `06_DATA_CONTRACT.md` |
| 实施计划 | `07_实施计划.md` | `07_IMPLEMENTATION_PLAN.md` |
| 验证计划 | `08_验证计划.md` | `08_TEST_PLAN.md` |
| 验证结果 | `09_验证结果.md` | `09_TEST_RESULT.md` |
| 自查报告 | `10_自查报告.md`（已废弃，新 change 不产出） | `10_SELF_REVIEW.md` |
| 审查报告 | `11_审查报告.md` | `11_REVIEW_REPORT.md` |
| 发布说明 | `12_发布说明.md` | `12_RELEASE_NOTE.md` |
| 经验沉淀 | `13_经验沉淀.md` | `13_LESSONS_LEARNED.md` |
| Agent 评估 | `14_Agent评估.md` | `14_AGENT_EVAL.md` |

每个阶段输出必须包含：

- `已读输入`
- `引用证据`
- `Req ID 覆盖映射`
- `未覆盖项`
- `下游依赖`

不确定项写入 `PENDING_DECISIONS.md`。存在 pending 决策时，不得进入编码。

## Profile 路由

### minimal

用于小 bug、小 UI 修复、窄范围重构、单个失败测试修复。minimal 不强制 PRD/设计 checkpoint。

必须同时满足：

- 不改接口契约、数据库、权限、事务/并发、外部系统。
- 不涉及安全、金钱、订单、库存、迁移、敏感数据。
- 不涉及前后端同时改。
- 产品语义清楚。
- 预计改动文件不超过 3 个。
- 可用一个目标测试或最小复现路径验证。

任一条件不满足，升级 standard 或 strict。

### standard

普通产品需求默认使用 standard。按需执行前端、后端、契约阶段。

### strict

涉及安全、金钱、订单、库存、数据库迁移、并发、外部集成、文件、webhook、敏感数据、不可逆操作时使用 strict。strict 必须执行契约、回滚、安全/DB/验证证据门禁。

## `.workflow_state` 标准

```yaml
schema_version: "1.0"
change_id: "<change-id>"
profile: standard
current_phase: prd
# --- task 级跟踪字段 ---
current_task: "输出用户角色与业务流程"
last_completed_task: "输出背景与目标"
next_action: "调用 product-discovery-analyst 继续写 01_PRD产品需求.md 的业务流程部分"
task_stack:
  - id: "1"
    description: "背景与目标"
    status: completed
  - id: "2"
    description: "用户角色与业务流程"
    status: in_progress
  - id: "3"
    description: "功能范围与非目标"
    status: pending
  - id: "4"
    description: "验收标准与异常/边界场景"
    status: pending
  - id: "5"
    description: "Req ID 覆盖映射与下游依赖"
    status: pending
phase_history:
  - phase: requirement
    completed_at: "2026-05-12T10:30"
    output: "00_原始需求.md"
resume_context: |
  正在执行 prd 阶段的 01_PRD产品需求.md。
  已完成背景与目标，正在编写用户角色与业务流程。
  上次调用 product-discovery-analyst 时，要求基于 00_原始需求.md 中用户场景展开。
  下一步：完成业务流程后进入功能范围与非目标。
# --- checkpoint 字段 ---
checkpoint: prd_confirmation
requires_user_confirmation: true
user_confirmed: false
confirmation_type: approve_prd
confirmation_role: product_owner
confirmation_docs: ["01_PRD产品需求.md"]
confirmed_checkpoints: []
required_checkpoints:
  - prd_confirmation
  - engineering_spec_confirmation
  - plan_confirmation
# --- 元信息 ---
affected_areas: ["backend", "frontend", "contract"]
context_package: "CONTEXT_PACKAGE.md"
trace_matrix_status: pending
round: 0
max_rounds: 3
pending_decisions_count: 0
project_consistency_enabled: false
engineering_manifest: ""
engineering_mode: "off"
verification_mode: "independent"
metrics_mode: "change_only"
sop_mode: "candidate_only"
consistency_review_required: false
architecture_owner_required: false
verification_status: "pending"
verification_issue_count: 0
metrics_recorded: false
created_at: "2026-05-12T00:00"
updated_at: "2026-05-12T00:00"
```

## Checkpoint

| checkpoint | confirmation_type | role | docs | 解锁 |
|---|---|---|---|---|
| `prd_confirmation` | `approve_prd` | 产品/业务负责人 | `01_PRD产品需求.md` | 工程规格 |
| `engineering_spec_confirmation` | `approve_engineering_spec` | 技术负责人 | `02_工程需求规格.md` | 代码调研和设计 |
| `backend_design_confirmation` | `approve_backend_design` | 后端负责人 | `04_后端方案说明.md` | 后端实施任务/契约 |
| `frontend_design_confirmation` | `approve_frontend_design` | 前端负责人/产品可参与 | `05_前端方案说明.md` | 前端实施任务/契约 |
| `contract_confirmation` | `approve_contract` | 前端+后端负责人 | `06_接口与数据契约.md` | 实施计划 |
| `plan_confirmation` | `approve_implementation_plan` | 研发负责人 | `07_实施计划.md`, `08_验证计划.md` | 编码、构建、测试 |

每个 checkpoint 必须：

1. 更新 `.workflow_state`：`requires_user_confirmation=true`, `user_confirmed=false`。
2. 用 `AskUserQuestion` 请求对应角色确认。
3. 用户确认前不得进入下一阶段，不得修改业务代码。
4. 用户确认后写入 `confirmed_checkpoints`，并将 `requires_user_confirmation=false`, `user_confirmed=true`。

## Context Package

每个阶段开始前更新 `<change-dir>/ai/CONTEXT_PACKAGE.md`：

```markdown
# Context Package

## Change 基本信息
- change_id:
- profile:
- current_phase:
- checkpoint:
- affected_areas:

## 全局必读
- 00_原始需求.md
- 01_PRD产品需求.md
- 02_工程需求规格.md
- 03_代码库调研.md

## 当前阶段必读

## Input Manifest

当前阶段子 Agent 启动前必须逐项验证以下文件存在且满足最小内容判据。
本表必须与"当前阶段必读"一致——不允许必读但未列入 manifest。

| 文件 | 必需性 | 最小内容判据 |
|------|--------|-------------|

## 项目规范必读

## 当前阶段目标

## 输出合同
- 输出文件:
- 必须包含章节:
- 必须覆盖 Req ID:
- 不确定项写入:

## 停止条件
```

子代理第一步必须读取 `CONTEXT_PACKAGE.md` 并执行 `rules/workflow/premortem-validation.md` 规定的输入完整性校验。校验不通过时停止并记录到 `PENDING_DECISIONS.md`，不得产出设计文档。

## Task 状态更新规则

主控 Agent 必须在以下时机更新 `.workflow_state` 的 task 字段：

1. **进入新阶段时**：初始化 `task_stack`（将该阶段所有子任务列出，第一个标记 `in_progress`，其余 `pending`），更新 `current_task`。
2. **完成一个子任务时**：更新 `last_completed_task`（刚完成的）、`current_task`（下一个）、`task_stack`（完成项标记 `completed`，下一项标记 `in_progress`）、`next_action`、`resume_context`、`updated_at`。
3. **调用子 Agent 前**：更新 `next_action` 和 `resume_context`，确保子 Agent 返回后能从 `resume_context` 继续。子 Agent 调用完成后立即更新 `current_task` 进度。
4. **阶段结束时**：清空 `task_stack`（所有项 `completed`），将阶段信息追加到 `phase_history`（含 `phase`、`completed_at`、`output`），清空 `current_task` 为下一阶段做准备。
5. **遇到阻塞时**：更新 `resume_context` 记录阻塞原因和下一步，写入 `PENDING_DECISIONS.md`。

更新粒度：每个子任务完成后更新一次（而非每个 tool call）。

`resume_context` 约束：≤200 tokens，精炼且可执行。内容必须包含：当前在做什么、已做到哪一步、下一步具体操作、上次调用的 Agent 和关键上下文。

## 阶段路由

### requirement

1. 创建 change workspace。
2. 将用户原始需求写入 `00_原始需求.md`。
3. 判断 profile；不确定时让用户选择。
4. 更新 `.workflow_state`：`current_phase=requirement`，`current_task="创建 change workspace"`，`last_completed_task=""`，`task_stack` 初始化为单任务。

### prd

1. 使用 `prd-check-flow`。
2. 更新 `CONTEXT_PACKAGE.md`，填写 Input Manifest：
   - `00_原始需求.md`: required，文件存在且非空
3. 初始化 `task_stack`：
   - "背景与目标"
   - "用户角色与业务流程"
   - "功能范围与非目标"
   - "验收标准与异常/边界场景"
   - "Req ID 覆盖映射与下游依赖"
   第一项标记 `in_progress`。
4. 更新 `current_task`，调用 `product-discovery-analyst` 产出 `01_PRD产品需求.md`。
4. 每完成一个子任务更新 `current_task`、`last_completed_task`、`task_stack`、`next_action`、`resume_context`。
5. 触发 `prd_confirmation`。

### engineering_spec

1. 使用 `engineering-spec-flow`。
2. 更新 `CONTEXT_PACKAGE.md`，填写 Input Manifest：
   - `00_原始需求.md`: required，文件存在且非空
   - `01_PRD产品需求.md`: required，第 8 节"业务流程"和第 10 节"验收标准"非空
3. 初始化 `task_stack`：
   - "本次实现范围与不实现范围"
   - "功能需求与权限规则"
   - "数据规则与异常边界场景"
   - "验收标准"
   - "Req ID 分配与覆盖映射"
   第一项标记 `in_progress`。
4. 更新 `current_task`，调用 `product-spec-analyst` 产出 `02_工程需求规格.md`。
4. 每完成一个子任务更新 task 跟踪字段。
5. 触发 `engineering_spec_confirmation`。

### research

1. 更新 `CONTEXT_PACKAGE.md`，填写 Input Manifest：
   - `02_工程需求规格.md`: required，第 5 节"功能需求"非空，至少 1 个 REQ-xxx
2. 初始化 `task_stack`：
   - "定位相似模块与可复用 API"
   - "分析模块边界与依赖方向"
   - "输出 search-first 结论（adopt/wrap/build/defer）"
   第一项标记 `in_progress`。
3. 更新 `current_task`，调用 `codebase-researcher` 产出 `03_代码库调研.md`。
4. 每完成一个子任务更新 task 跟踪字段。
5. 证据不足时回到工程规格或写入 `PENDING_DECISIONS.md`。

### backend_design

当 `affected_areas` 包含 `backend`、`database`、`integration`、`security` 时执行：

1. 使用 `backend-design-check-flow`。
2. 更新 `CONTEXT_PACKAGE.md`，填写 Input Manifest：
   - `02_工程需求规格.md`: required，第 5 节非空，至少 1 个 REQ-xxx
   - `03_代码库调研.md`: required，第 1 节"涉及模块"非空
   - `openspec/specs/engineering/10-编码规范/Java后端编码规范.md`: conditional（文件存在则 required）
   - `openspec/specs/engineering/10-编码规范/Spring事务与并发规范.md`: conditional（文件存在则 required）
   - `openspec/specs/engineering/10-编码规范/SQL与数据库规范.md`: conditional（文件存在则 required）
3. 初始化 `task_stack`：
   - "模块依赖与边界分析"
   - "Controller/Service/Repository 边界设计"
   - "DTO/VO/Entity 关系与事务边界"
   - "锁、并发、幂等策略"
   - "SQL、索引、批量查询策略"
   - "外部接口调用位置"
   - "异常、日志、审计设计"
   - "后端任务拆分与 Req ID 覆盖"
   第一项标记 `in_progress`。
4. 更新 `current_task`，调用 `backend-designer` 产出 `04_后端方案说明.md`。
4. 按需调用 `java-reviewer`、`database-reviewer`、`security-reviewer` 做设计期审查。
5. 每完成一个子任务更新 task 跟踪字段。
6. 触发 `backend_design_confirmation`。

### frontend_design

当前端页面、组件、路由、表单、表格、交互、样式、权限展示或浏览器行为受影响时执行：

1. 使用 `frontend-design-check-flow`。
2. 更新 `CONTEXT_PACKAGE.md`，填写 Input Manifest：
   - `01_PRD产品需求.md`: required，第 8 节"业务流程"非空
   - `02_工程需求规格.md`: required，第 5 节非空，至少 1 个 REQ-xxx
   - `03_代码库调研.md`: required，涉及前端模块的证据非空
   - `openspec/specs/engineering/10-编码规范/前端编码与交互规范.md`: conditional（文件存在则 required）
3. 初始化 `task_stack`：
   - "页面入口、路由、菜单定位"
   - "用户流程与各状态设计（成功/失败/空/加载/权限）"
   - "组件复用方案"
   - "表格/表单完整状态设计"
   - "API 调用与状态刷新策略"
   - "响应式与浏览器验证路径"
   - "Req ID 覆盖映射"
   第一项标记 `in_progress`。
4. 更新 `current_task`，调用 `frontend-product-design` 和 `frontend-designer` 产出 `05_前端方案说明.md`。
4. 调用 `frontend-ux-reviewer` 做设计期审查。
5. 每完成一个子任务更新 task 跟踪字段。
6. 触发 `frontend_design_confirmation`。

### contract

当前后端、前端、API、DTO/VO、事件、数据库字段、错误码、枚举、权限失败行为任一受影响时执行：

1. 使用 `contract-check-flow`。
2. 更新 `CONTEXT_PACKAGE.md`，填写 Input Manifest：
   - `02_工程需求规格.md`: required，第 5 节非空
   - `03_代码库调研.md`: required，第 1 节非空
   - `04_后端方案说明.md`: conditional（affected_areas 含 backend 则 required）
   - `05_前端方案说明.md`: conditional（affected_areas 含 frontend 则 required）
3. 初始化 `task_stack`：
   - "API 路径与方法定义"
   - "请求 DTO 与响应 VO 字段"
   - "枚举值、错误码、权限失败行为"
   - "分页、排序、过滤规则"
   - "幂等、兼容与版本演进策略"
   - "数据库/事件契约（如适用）"
   - "Req ID 覆盖映射"
   第一项标记 `in_progress`。
4. 更新 `current_task`，调用 `data-contract-designer` 产出 `06_接口与数据契约.md`。
4. 每完成一个子任务更新 task 跟踪字段。
5. 触发 `contract_confirmation`。

### plan

1. 使用 `implementation-plan-check-flow`。
2. 更新 `CONTEXT_PACKAGE.md`，填写 Input Manifest：
   - `02_工程需求规格.md`: required，第 5 节非空且 Req ID 列表完整
   - `03_代码库调研.md`: required，第 1 节非空
   - `04_后端方案说明.md`: conditional（affected_areas 含 backend 则 required）
   - `05_前端方案说明.md`: conditional（affected_areas 含 frontend 则 required）
   - `06_接口与数据契约.md`: conditional（affected_areas 含 contract 或 strict profile 则 required）
   - `PENDING_DECISIONS.md`: conditional（如 pending_decisions_count > 0 则 required，检查无 pending 项）
3. 初始化 `task_stack`：
   - "总体策略与任务拆分"
   - "后端任务规划"
   - "前端任务规划"
   - "数据与契约任务规划"
   - "允许/不允许修改文件范围"
   - "验证计划（单元/集成/API/前端/E2E）"
   - "Req ID 覆盖校验"
   第一项标记 `in_progress`。
4. 更新 `current_task`，调用 `implementation-planner` 产出 `07_实施计划.md`。
4. 调用 `test-planner` 产出 `08_验证计划.md`。
5. 每完成一个子任务更新 task 跟踪字段。
6. 触发 `plan_confirmation`。

### coding

1. 主控 Agent 读取 `CONTEXT_PACKAGE.md`、`02_工程需求规格.md`、设计文档、契约、实施计划、验证计划。
2. 根据 `07_实施计划.md` 的任务拆分初始化 `task_stack`，每个实施任务拆为"写测试 → 写实现 → 验证通过"三个子任务。
3. **测试先行（强制）**：对每个实施任务，先从 `08_验证计划.md` 的测试用例表找到对应的测试用例，按以下 TDD 循环执行：
   - 先写测试代码（Java 后端参考 `springboot-tdd` 规范：断言必须验证业务结果而不仅是"无异常"；前端写组件测试或浏览器验证用例）
   - 运行新增测试，确认因功能缺失而失败（red phase）
   - 写最小业务实现
   - 运行测试，确认通过（green phase）
   - 循环直到当前任务关联的所有测试用例覆盖完毕
4. 只修改 `07_实施计划.md` 允许的文件。
5. **每次修改业务代码前**更新 `resume_context`（当前在改什么文件、为什么、下一步），确保 `/clear` 后能从最近 safe point 恢复。
6. 每完成一个实施任务（含其所有 TDD 子任务）更新 `current_task`、`last_completed_task`、`task_stack`、`next_action`、`resume_context`。
7. designer/reviewer/planner 不直接改业务代码。主控 Agent 不自己跑测试验证——测试验证在下一个阶段由独立子 Agent 完成。

### verification

验证阶段由独立子 Agent（test-planner 验证执行模式）全权负责。主控 Agent 不跑测试、不判断测试结果。

1. 使用 `verification-flow`。
2. 更新 `CONTEXT_PACKAGE.md`，`current_phase=verification`，填写 Input Manifest：
   - `02_工程需求规格.md`: required
   - `08_验证计划.md`: required
   - `07_实施计划.md`: required
3. 初始化 `task_stack`：
   - "调用 test-planner 独立验证（覆盖率核对 + 测试执行 + 评估）"
   - "处理验证结果（通过 / 修复 / 阻塞）"
   - "前端浏览器验证（条件，由 frontend-verification-flow 执行）"
   第一项标记 `in_progress`。
4. 调用 `test-planner`（验证执行模式），由其独立完成覆盖率核对、测试执行和充分性评估，产出 `09_验证结果.md`。
5. 子 Agent 返回后检查 Pre-mortem 校验通过标记；失败则补全输入重新调用。
6. 前端改动同时调用 `frontend-verification-flow`，浏览器验证结果写入 `09_验证结果.md`。
7. 评估结论为"充分"且无 P0/P1 失败 → 进入 review。
8. 评估结论为"不充分"或有 P0/P1 失败 → 进入修复循环（参见 `rules/workflow/verification-loop.md`）：
   - L1 构建/基础设施错误 → `build-error-resolver` → 重新调用 test-planner 验证
   - L2 断言失败/覆盖缺口（首次）→ 主控修复 → **重新调用 test-planner 验证**（主控不自己跑测试）
   - L3 同组件连续两次失败 → `code-reviewer` 诊断，主控不得继续修
   - L4 连续三次失败 → 写 PENDING_DECISIONS，标记 blocked，人工介入
9. 每完成一个子任务更新 task 跟踪字段。

### review

审查阶段由独立 reviewer agent 执行。主控 Agent 负责调用和汇总。

1. 使用 `review-flow`。
2. 更新 `CONTEXT_PACKAGE.md`，`current_phase=review`，填写 Input Manifest：
   - `02_工程需求规格.md`: required
   - `07_实施计划.md`: required
   - `08_验证计划.md`: required
   - `09_验证结果.md`: required
   - `openspec/specs/engineering/30-质量与验证/禁止模式清单.md`: conditional（文件存在则 required）
   - `openspec/specs/engineering/30-质量与验证/代码审查清单.md`: conditional（文件存在则 required）
   - `openspec/specs/engineering/20-架构规范/模块边界规范.md`: conditional（文件存在则 required）
3. 初始化 `task_stack`：
   - "需求覆盖审查"
   - "范围与证据审查"
   - "代码质量审查（含反模式逐条对照 FORBID-xxx）"
   - "测试设计审查（对照 AC 检查测试计划覆盖完整性）"
   - "交叉引用检查（对比 2-3 个相似现有实现）"
   - "专项审查（按需：Java/安全/数据库/前端）"
   第一项标记 `in_progress`。
4. 调用 `code-reviewer`（实现后模式），返回后检查 Pre-mortem 校验通过标记。
5. 按需调用专项 reviewer：`java-reviewer`、`database-reviewer`、`security-reviewer`、`frontend-ux-reviewer`。每个返回后检查 Pre-mortem 校验通过标记。
6. 汇总审查结论到 `11_审查报告.md`。
7. 审查不通过 → 主控修复 → 重新走 verification → review（不跳过任何步骤）。
8. 审查通过 → 进入 delivery。
9. 每完成一个子任务更新 task 跟踪字段。

### delivery

1. 初始化 `task_stack`：
   - "更新 CHANGE_METRICS.json"
   - "发布说明"
   - "经验沉淀（standard/strict）"
   - "Agent 评估（standard/strict）"
   第一项标记 `in_progress`。
2. 更新 `CHANGE_METRICS.json`（从原 self_review 阶段迁入，记录本轮 change 的指标数据）。
3. 产出 `12_发布说明.md`。
4. standard/strict 产出 `13_经验沉淀.md` 和 `14_Agent评估.md`。
5. 每完成一个子任务更新 task 跟踪字段。
6. 所有 task 完成后，追加 `delivery` 到 `phase_history`。

**注意**：`10_自查报告.md` 不再作为独立文档产出。原 self_review 的机械检查（Req ID 覆盖核对）由 test-planner 验证模式的覆盖率核对步骤承担，判断性检查（异常处理、危险模式）由 review 阶段的独立 reviewer 承担。

### archive

使用 `openspec-archive-change`。存在未确认问题、审查不通过、验证无证据、阻塞问题未修复时不得归档。

## minimal 流程

minimal 只执行：

```text
00_原始需求.md
→ 03_代码库调研.md（轻量）
→ 07_实施计划.md
→ 08_验证计划.md（按需）
→ coding（测试先行，TDD 循环）
→ 09_验证结果.md（test-planner 轻量模式）
→ 12_发布说明.md
```

minimal 不强制人工 checkpoint，但必须维护 `.workflow_state`、`CONTEXT_PACKAGE.md`、`CHANGE_METRICS.json` 和允许文件范围。minimal 下 test-planner 验证模式覆盖率核对可选，测试执行只跑目标测试。不强制 review 阶段。轻量 diff 自查由主控 Agent 直接对比变更和需求。

## Enhanced Flow

如果项目存在 `openspec/specs/engineering/engineering.json` 且 `enabled=true`：

- `mode=advisory`：记录风险，不阻断归档。
- `mode=enforced`：确定性违反项、项目一致性 review 失败、未处理 owner decision 均阻断进入下一门禁。
- 未启用 manifest 时，不得强制读取工程事实库，不得生成阻断性一致性结论。
