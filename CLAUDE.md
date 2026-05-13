# Global Instructions

## Language & Output
- 默认中文回复，结论优先。
- 用户是程序员，给实战方案，不做基础科普。

## Reasoning
- 不确定时必须标注，不伪装确定事实。
- 禁止编造不存在的 API / 库 / 配置。

## Coding Style
- 遵循项目现有风格，不做无关重构。
- 命名语义清晰，避免 magic number。
- 注释重点解释非显而易见的设计选择。

## Code Generation
- 提供可直接运行的完整代码（含 import、运行方式）。
- 只要局部修改时，明确说明修改位置。

## Error Handling
- 不忽略异常，不空 catch。
- 高风险场景（网络、IO、并发）要合理处理错误。

## Change Scope
- 只改用户要求的内容，不主动重构。此条约束的是实现范围（不改无关代码），不是需求范围。每个原始需求项必须实现或用户显式确认不做，模型不得自行裁剪。
- 不改变已有接口行为（除非明确要求）。

## Java 规范
- 遵循《阿里巴巴 Java 开发手册》（嵩山版）强制条款。
- 重点关注：命名规范、异常处理、日志规约、集合处理、并发规约、MySQL 规约。

## Architecture Rules
在推荐任何跨类、跨模块、跨服务依赖前，必须先验证：

- 目标 API 是否 public 且 intended for reuse；
- 依赖方向是否符合模块架构；
- 目标类是否只是 implementation detail；
- 是否应该抽取 helper、support、strategy、visitor 或 domain service；
- 现有代码是否已有类似模式。

证据不足时，必须明确说明"证据不足，需要继续检查文件"，不能猜测。

## Quality Gates
实现完成后必须运行项目已有测试命令。

如果不知道测试命令，先查 README、pom.xml、package.json、Makefile、CI 配置。

不能伪造测试结果。不能说"应该可以通过"，必须说明实际运行了什么命令、结果是什么。

## Session Resume Rule

会话开始、/clear 或 /compact 后，如果工作目录下存在 `openspec/changes/*/ai/.workflow_state`，在回复用户前执行以下恢复流程：

1. 查找最近活跃的 `.workflow_state` 文件（按修改时间排序，排除 archive）。
2. 读取 `.workflow_state` 获取 `current_phase`、`current_task`、`last_completed_task`、`task_stack`、`resume_context`。
3. 读取 `CONTEXT_PACKAGE.md` 获取完整上下文。
4. 如果 `requires_user_confirmation=true` 且 `user_confirmed=false`：
   - 用 `AskUserQuestion` 向用户呈现待确认的 checkpoint 和文档。
   - 用户确认前不得进入下一阶段。
5. 如果 `requires_user_confirmation=false` 或 `user_confirmed=true`：
   - 根据 `resume_context` 和 `task_stack` 确定下一步。
   - 输出简短恢复提示："已恢复 change [change_id]，当前阶段 [current_phase]，任务 [current_task]。继续执行。"
   - 直接继续工作，不等待用户确认。
6. 如果 `.workflow_state` 格式损坏或必填字段缺失，输出警告并调用 `resume-flow` skill 手动恢复。

## Workflow Routing

根据用户意图匹配工作流家族。家族内部如何分级（standard/strict/minimal）、如何编排 Agent、输出什么文档，由家族 Skill 自己决定，CLAUDE.md 不展开。

| 用户意图 | 工作流家族 | Profile |
|---------|-----------|---------|
| 新功能、需求开发、产品行为变更 | `product-to-test-flow` | standard（默认）/ strict（高风险）/ minimal（小改动） |
| 小 bug、小改动、简单调整 | `quick-fix-flow` | minimal |
| 高风险需求（安全/金钱/订单/数据迁移/并发/外部集成） | `strict-product-to-test-flow` | strict |
| 构建/编译/测试/Lint 报错修复 | `build-fix-flow` | — |
| 代码审查（PR/变更后） | `review-flow` | — |
| 需求完成后的经验沉淀 | `learn-from-delivery` | learning |
| 验证变更是否正确完成 | `verification-flow` | — |
| 恢复工作流进度 | `resume-flow` | — |
| 初始化团队热插拔/工程事实库/团队一致性治理模板 | `init-engineering-consistency` | — |

不匹配任何家族 → 直接对话，不走工作流。
不确定时 → 列出候选家族让用户选，不猜测。

## Spec Discovery Rule

当需要读取工程规范时，不通过硬编码路径，而是通过规则 ID 前缀发现：

1. 读取 `openspec/specs/engineering/engineering.json`，获取 `rulePrefixIndex` 和 `discovery` 配置。
2. 确定需要的规则 ID 前缀（如 `JAVA-DA-`、`TX-`、`GEN-`）。
3. Glob `openspec/specs/engineering/**/*.md` 并 grep 对应前缀，找到包含目标规则的文件。
4. 读取过程中提取所有规则 ID，逐条检查前缀是否在 `rulePrefixIndex` 中：
   - 已注册 → 正常引用，强制执行。
   - 未注册 → 照样读取，但标注"⚠️ 规则 xxx 前缀未注册，审查时不强制执行。注册方法：在 engineering.json rulePrefixIndex 添加前缀。"
5. 新 Change 中发现未注册规则时，写入 PENDING_DECISIONS.md。
6. 如果 `engineering.json` 为 v1 schema（仅含 `requiredSpecs`），按 legacy 兼容模式处理（glob + 文件名匹配作为回退）。
