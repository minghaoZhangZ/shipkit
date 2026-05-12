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
| 初始化团队热插拔/工程事实库/团队一致性治理模板 | `init-engineering-consistency` | — |

不匹配任何家族 → 直接对话，不走工作流。
不确定时 → 列出候选家族让用户选，不猜测。
