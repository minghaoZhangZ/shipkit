---
name: frontend-design-check-flow
description: Use when frontend pages, routes, forms, tables, components, interactions, permissions, responsive behavior, or browser verification need design review before implementation.
---

# Frontend Design Check Flow

目标：生成可审查的 `05_前端方案说明.md`，并在前端实施任务生成或编码前获得前端确认。

## 输入

必读：

- `CONTEXT_PACKAGE.md`
- `01_PRD产品需求.md`
- `02_工程需求规格.md`
- `03_代码库调研.md`
- 工程规范（通过 `engineering.json` rulePrefixIndex 发现，glob `engineering/**/*.md` + grep 前缀）：FE- 前缀（前端编码与交互）

按需读取现有路由、菜单、组件、状态管理、API 调用和样式约定。

## 执行

1. 确认 `engineering_spec_confirmation` 已通过；minimal UI bug 可跳过但必须有复现路径。
2. 更新 `CONTEXT_PACKAGE.md`，`current_phase=frontend_design`，填写 Input Manifest。
3. 使用 `frontend-product-design` 明确页面、组件、状态、交互、浏览器验证点。
4. 调用 `frontend-designer` 输出 `05_前端方案说明.md`。返回后检查 Pre-mortem 校验通过标记；失败则补全输入重新调用。
5. 调用 `frontend-ux-reviewer` 做设计期审查，只写审查意见，不改代码。
6. 阻塞问题写入 `PENDING_DECISIONS.md` 或修订前端方案。
7. 设置 checkpoint：

```yaml
checkpoint: frontend_design_confirmation
requires_user_confirmation: true
user_confirmed: false
confirmation_type: approve_frontend_design
confirmation_role: frontend_owner
confirmation_docs: ["05_前端方案说明.md"]
```

## 输出合同

`05_前端方案说明.md` 必须包含：

**概览区：** TL;DR、页面目标、涉及模块、关键决策
**正文区：** 路由与入口、用户流程（成功/失败/空/加载/权限/禁用状态）、组件拆分与复用、状态管理、接口调用、表格/筛选与分页、表单校验与提交反馈、防重复点击与交互保护、响应式与浏览器验证点
**附录区：** Req ID 覆盖映射、已读输入、引用证据、未覆盖项、下游依赖

## 停止条件

- 页面或入口无法定位。
- 组件库、状态管理或 API 调用模式不清。
- 设计要求改变 API、权限、依赖或公共行为但工程规格未覆盖。
- 前端相关 Req ID 未覆盖且无确认排除。
