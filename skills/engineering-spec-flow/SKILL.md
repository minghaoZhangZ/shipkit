---
name: engineering-spec-flow
description: Use when a confirmed PRD must be converted into engineering requirements, Req IDs, acceptance criteria, and traceability before design.
---

# Engineering Spec Flow

目标：把产品可读 PRD 转成研发可执行的 `02_工程需求规格.md`，并在代码调研和技术设计前获得技术确认。

## 输入

必读：

- `CONTEXT_PACKAGE.md`
- `00_原始需求.md`
- `01_PRD产品需求.md`

统一使用中文 canonical 文档名。

## 执行

1. 确认 `prd_confirmation` 已在 `confirmed_checkpoints` 中；minimal 可跳过。
2. 更新 `CONTEXT_PACKAGE.md`，`current_phase=engineering_spec`，填写 Input Manifest。
3. 调用 `product-spec-analyst`。
4. Agent 返回后检查其输出"已读输入"节是否包含 Pre-mortem 校验通过标记；校验失败时补全输入并重新调用，不得跳过。
5. 输出 `02_工程需求规格.md`。
5. 如果存在工程歧义，写入 `PENDING_DECISIONS.md`。
6. 设置 checkpoint：

```yaml
checkpoint: engineering_spec_confirmation
requires_user_confirmation: true
user_confirmed: false
confirmation_type: approve_engineering_spec
confirmation_role: tech_lead
confirmation_docs: ["02_工程需求规格.md"]
```

7. 用 `AskUserQuestion` 请求技术负责人确认。

## 输出合同

`02_工程需求规格.md` 必须包含：

**概览区：** TL;DR、本次实现范围、关键决策、涉及模块
**正文区：** 背景与目标、本次不实现范围及确认依据、功能需求（含 REQ-xxx 标记）、权限规则、数据规则、异常与边界场景、验收标准
**附录区：** Req ID 覆盖映射、已读输入、引用证据、未覆盖项、下游依赖

Req ID 格式统一为 `REQ-001`、`REQ-002`。

## 停止条件

- PRD 未确认。
- 原始需求片段无法映射到 Req ID。
- “本次不实现”没有用户或产品确认证据。
- 关键权限、数据、异常规则不清。
