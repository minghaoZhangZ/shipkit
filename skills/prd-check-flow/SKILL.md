---
name: prd-check-flow
description: Use when a product or business requirement needs a product-readable PRD before engineering specification or implementation planning.
---

# PRD Check Flow

目标：生成只面向产品/业务的 `01_PRD产品需求.md`，并在进入工程规格前获得产品确认。

## 输入

必读：

- `<change-dir>/ai/00_原始需求.md`。
- `<change-dir>/ai/CONTEXT_PACKAGE.md`。

不得要求产品阅读代码、类名、SQL、接口实现、组件路径或测试命令。

## 执行

1. 更新 `CONTEXT_PACKAGE.md`，`current_phase=prd`，填写 Input Manifest（参见 `rules/workflow/premortem-validation.md`）。
2. 调用 `product-discovery-analyst`。
3. Agent 返回后检查其输出"已读输入"节是否包含 Pre-mortem 校验通过标记；校验失败时补全输入并重新调用，不得跳过。
4. 输出 `<change-dir>/ai/01_PRD产品需求.md`。
4. 将业务歧义写入 `PENDING_DECISIONS.md`。
5. 设置 checkpoint：

```yaml
checkpoint: prd_confirmation
requires_user_confirmation: true
user_confirmed: false
confirmation_type: approve_prd
confirmation_role: product_owner
confirmation_docs: ["01_PRD产品需求.md"]
```

6. 用 `AskUserQuestion` 请求产品/业务确认。

## 输出合同

`01_PRD产品需求.md` 必须包含：

**概览区：** TL;DR、业务目标与成功指标、关键决策、涉及角色
**正文区：** 背景、用户角色与场景、业务流程（含 Mermaid 中文流程图）、功能范围、非目标、页面或业务入口、验收标准、异常/边界场景、待产品确认问题
**附录区：** Req ID 覆盖映射、已读输入、引用证据、未覆盖项、下游依赖

## 停止条件

- 产品目标不清。
- 用户角色或业务入口不清。
- 验收标准无法用业务语言表达。
- 需要把原始需求拆分但用户未确认取舍。

停止时只写 `PENDING_DECISIONS.md` 和 AI 文档，不得进入工程规格。
