# State Model

> ShipKit 工作流状态管理权威定义。单用户单主控模型，不涉及多 session 并发。

---

## 一、状态文件

| 文件 | 路径 | 用途 |
|------|------|------|
| `.workflow_state` | `openspec/changes/<change-id>/.workflow_state` | 工作流运行时状态（Hook 校验、resume 恢复） |
| `metadata.json` | `openspec/changes/<change-id>/metadata.json` | Change 元信息（展示用，不参与 Hook 校验） |

**.workflow_state 格式**：YAML 行解析（每行 `key: value`）。Hook 按行读取，不解析嵌套 YAML 结构。

---

## 二、字段字典

### A. 标识与路由

| 字段 | 类型 | 默认 | 合法值 | 初始化 | 更新时机 | 读者 |
|------|------|------|--------|--------|---------|------|
| `schema_version` | str | `"1.0"` | `"1.0"` | openspec-new-change | — | hooks, migrate |
| `change_id` | str | `""` | `yyyy-mm-dd-type-domain-动作` | openspec-new-change | — | hooks, resume-flow |
| `profile` | enum | `minimal` | `minimal` / `standard` / `strict` / `learning` | openspec-new-change | requirement 阶段判断 | hooks, skills |
| `current_phase` | enum | `requirement` | 见 §三 Phase 列表 | openspec-new-change | 每阶段开始 | hooks, resume-flow, test-planner |

### B. 生命周期

| 字段 | 类型 | 默认 | 合法值 | 初始化 | 更新时机 | 读者 |
|------|------|------|--------|--------|---------|------|
| `state` | enum | `active` | `active` / `blocked` / `failed` / `finished` | openspec-new-change | 触发条件时（见 §四 终态） | checkpoint-guard, resume-flow |

### C. Task 级跟踪

| 字段 | 类型 | 默认 | 合法值 | 初始化 | 更新时机 | 读者 |
|------|------|------|--------|--------|---------|------|
| `current_task` | str | `""` | 当前子任务描述 | openspec-new-change | 每子任务切换 | resume-flow |
| `last_completed_task` | str | `""` | 上一个完成的子任务 | — | 每子任务完成 | resume-flow |
| `next_action` | str | `""` | 下一步操作描述 | — | 每子任务切换 | resume-flow |
| `task_stack` | list | `[]` | `[{id, description, status}]` | 每阶段开始 | 每子任务完成 | resume-flow |
| `phase_history` | list | `[]` | `[{phase, completed_at, output}]` | — | 每阶段结束 | resume-flow |
| `resume_context` | str | `""` | ≤200 tokens 精炼描述 | — | 每子任务切换、调子 Agent 前 | resume-flow |

### D. Checkpoint 确认

| 字段 | 类型 | 默认 | 合法值 | 初始化 | 更新时机 | 读者 |
|------|------|------|--------|--------|---------|------|
| `checkpoint` | enum | `""` | `prd_confirmation` / `engineering_spec_confirmation` / `backend_design_confirmation` / `frontend_design_confirmation` / `contract_confirmation` / `plan_confirmation` | — | 每 checkpoint 到达 | checkpoint-guard |
| `requires_user_confirmation` | bool | `false` | `true` / `false` | openspec-new-change | checkpoint 触发时设 true，确认后设 false | checkpoint-guard |
| `user_confirmed` | bool | `true` | `true` / `false` | openspec-new-change | 用户确认后设 true | checkpoint-guard |
| `confirmation_type` | enum | `""` | `approve_prd` / `approve_engineering_spec` / `approve_backend_design` / `approve_frontend_design` / `approve_contract` / `approve_implementation_plan` | — | checkpoint 触发时 | checkpoint-guard |
| `confirmation_role` | str | `""` | 角色描述 | — | checkpoint 触发时 | checkpoint-guard |
| `confirmation_docs` | list | `[]` | 待确认文档列表 | — | checkpoint 触发时 | checkpoint-guard |
| `confirmed_checkpoints` | list | `[]` | 已确认 checkpoint 列表 | — | 用户确认后追加 | checkpoint-guard, skills |
| `required_checkpoints` | list | `[]` | 必确认 checkpoint 列表 | requirement 阶段 | — | checkpoint-guard, skills |

### E. 元信息

| 字段 | 类型 | 默认 | 合法值 | 初始化 | 更新时机 | 读者 |
|------|------|------|--------|--------|---------|------|
| `affected_areas` | list | `[]` | `backend` / `frontend` / `contract` / `database` / `security` / `file` / `integration` | openspec-new-change | requirement 阶段 | skills |
| `context_package` | str | `"CONTEXT_PACKAGE.md"` | 文件名 | openspec-new-change | — | skills, agents |
| `trace_matrix_status` | enum | `pending` | `pending` / `in_progress` / `complete` | openspec-new-change | engineering_spec 阶段 | skills |
| `pending_decisions_count` | int | `0` | ≥0 | openspec-new-change | PENDING_DECISIONS 变更时 | skills |
| `round` | int | `0` | ≥0 | openspec-new-change | （当前未使用，保留向后兼容） | — |
| `max_rounds` | int | `3` | 正整数 | openspec-new-change | — | skills |

### F. 工程一致性（可选增强层）

| 字段 | 类型 | 默认 | 合法值 | 初始化 | 更新时机 | 读者 |
|------|------|------|--------|--------|---------|------|
| `project_consistency_enabled` | bool | `false` | `true` / `false` | openspec-new-change | — | skills |
| `engineering_manifest` | str | `""` | 文件路径 | openspec-new-change | — | skills |
| `engineering_mode` | enum | `off` | `off` / `advisory` / `enforced` | openspec-new-change | — | skills |
| `verification_mode` | str | `"independent"` | `"independent"` | openspec-new-change | — | skills |
| `metrics_mode` | str | `"change_only"` | `"change_only"` | openspec-new-change | — | skills |
| `sop_mode` | str | `"candidate_only"` | `"candidate_only"` | openspec-new-change | — | skills |
| `consistency_review_required` | bool | `false` | `true` / `false` | openspec-new-change | — | skills |
| `architecture_owner_required` | bool | `false` | `true` / `false` | openspec-new-change | — | skills |

### G. 验证状态

| 字段 | 类型 | 默认 | 合法值 | 初始化 | 更新时机 | 读者 |
|------|------|------|--------|--------|---------|------|
| `verification_status` | enum | `pending` | `pending` / `passed` / `failed` | openspec-new-change | verification 阶段结束后 | skills |
| `verification_issue_count` | int | `0` | ≥0 | openspec-new-change | verification 阶段结束后 | skills |
| `metrics_recorded` | bool | `false` | `true` / `false` | openspec-new-change | delivery 阶段 | skills |
| `created_at` | str | `""` | ISO datetime | openspec-new-change | — | skills |
| `updated_at` | str | `""` | ISO datetime | openspec-new-change | 每次写 state 时 | resume-flow |

### H. Ralph 持久化完成循环

| 字段 | 类型 | 默认 | 合法值 | 初始化 | 更新时机 | 读者 |
|------|------|------|--------|--------|---------|------|
| `ralph.enabled` | bool | `false` | `true` / `false` | requirement | requirement 阶段 | verification-flow, review-flow |
| `ralph.iteration` | int | `0` | 0..max_iterations | requirement | Completion Audit 失败时 | verification-flow |
| `ralph.max_iterations` | int | `10` | 正整数 | requirement | — | verification-flow |
| `ralph.completion_audit_passed` | bool | `false` | `true` / `false` | requirement | Completion Audit 结束时 | verification-flow |
| `ralph.architect_tier` | enum | `STANDARD` | `STANDARD` / `DEEP` / `THOROUGH` | requirement | review-flow | review-flow |
| `ralph.audit_history` | list | `[]` | `[{iteration, result, uncovered_reqs, ...}]` | requirement | Completion Audit 结束时 | verification-flow |

> **行解析器说明**：Hook 按行解析 `key: value`。ralph 块的 YAML 嵌套被解析为独立 key（`ralph:` → val=""、`enabled:` → val="false" 等）。这些 key 不在 Hook 的 required 集合中，不触发校验错误。写 ralph 字段时注意不与现有 key 冲突。

---

## 三、Phase 列表与转换

### 合法 phase 值

```
requirement → prd → engineering_spec → research
→ backend_design ──→ contract → plan → coding
→ frontend_design ──┘
→ verification → review → delivery → archive
```

- `self_review`：已废弃，保留向后兼容
- `analysis` / `design`：旧 change 兼容名

### 完整转换表

每条转换格式：`from_phase → to_phase`，标注触发者和方向。

#### 正向转换（9 条）

| # | 转换 | 触发者 | 何时 |
|---|------|--------|------|
| 1 | `requirement` → `prd` | product-to-test-flow | 创建 change 后 |
| 2 | `prd` → `engineering_spec` | product-to-test-flow | prd_confirmation 后 |
| 3 | `engineering_spec` → `research` | product-to-test-flow | engineering_spec_confirmation 后 |
| 4 | `research` → `backend_design` / `frontend_design` | product-to-test-flow | research 完成后 |
| 5 | `backend_design` / `frontend_design` → `contract` | product-to-test-flow | 设计确认后 |
| 6 | `contract` → `plan` | product-to-test-flow | contract_confirmation 后 |
| 7 | `plan` → `coding` | product-to-test-flow | plan_confirmation 后 |
| 8 | `coding` → `verification` | product-to-test-flow | 编码完成后 |
| 9 | `verification` → `review` | verification-flow | Completion Audit 通过后 |
| 10 | `review` → `delivery` | product-to-test-flow | 审查通过后 |
| 11 | `delivery` → `archive` | openspec-archive-change | 交付完成后 |

#### 反向转换（3 条，ralph 引入）

| # | 转换 | 触发者 | 何时 |
|---|------|--------|------|
| R1 | `verification` → `coding` | verification-flow | Completion Audit 不通过（ralph 模式） |
| R2 | `verification` → `plan` | verification-flow | L3 code-reviewer 诊断"设计问题"（ralph 模式） |
| R3 | `review` → `coding` | product-to-test-flow | 审查不通过，主控修复 |

#### minimal 简化路径（quick-fix-flow）

| # | 转换 | 触发者 |
|---|------|--------|
| M1 | `plan` → `coding` | quick-fix-flow |
| M2 | `coding` → `verification` | quick-fix-flow |
| M3 | `verification` → `delivery` | quick-fix-flow |

### 转换规则

- Hook 不硬校验转换合法性（仅校验 phase 在 KNOWN_PHASES 集合中）
- 非法转换由 skill 指令和 checkpoint guard 间接阻止（如未确认 plan 无法进入 coding）
- 反向转换 R1/R2/R3 依赖 Agent 正确执行 skill 指令

---

## 四、生命周期终态

```
                    ┌──→ active ──→ finished（正常归档）
                    │
state: active ──────┤
（正常流转）        │
                    ├──→ blocked（阻塞）
                    │      │
                    │      ├── L4 连续三次失败
                    │      ├── ralph.iteration > ralph.max_iterations
                    │      ├── 安全 reviewer 不通过
                    │      └── 用户手动暂停
                    │      │
                    │      └──→ active（人工解除阻塞，继续流转）
                    │
                    └──→ failed（手动放弃，不可恢复）
```

### 终态行为

| state | checkpoint-guard | scope-guard | resume-flow |
|-------|:---:|:---:|------|
| `active` | 正常校验 | 正常校验 | 正常恢复 |
| `blocked` | **阻断业务编辑**（仅允许 AI 文档写入） | 不激活 | 提示"此 change 已阻塞"，不自动继续 |
| `failed` | **阻断一切编辑** | 不激活 | 提示"此 change 已放弃" |
| `finished` | 正常校验 | 不激活 | 提示"此 change 已完成"，建议归档 |

---

## 五、状态文件权威层级

ShipKit 单用户单主控模型，不涉及多 session 并发。层级简单：

```
.active .workflow_state（每个 change 独立）
  │
  └── Hook 读取时：<change-dir>/.workflow_state（唯一来源）
  │
  └── resume-flow 恢复时：按 updated_at 排序，取最新非归档 change
```

无 session scope / root scope 的区别，无 explicit session 覆盖逻辑。

---

## 六、与新功能集成指南

当向 ShipKit 添加新特性（如 autopilot）需要新增状态字段时：

1. 确定字段归属分组（A-H），在对应分组追加
2. 更新 `openspec-new-change/SKILL.md` 初始化模板（含默认值）
3. 更新 `product-to-test-flow/SKILL.md` 完整 schema
4. 更新 `migrate-workflow-state.py` CANONICAL_DEFAULTS
5. 如果字段需要 Hook 校验，更新对应 Hook
6. 在此文档字段字典中追加行，转换表中追加转换
