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
- `openspec/specs/engineering/10-编码规范/前端编码与交互规范.md`（存在时）

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

- 页面入口、路由、菜单、按钮或弹窗入口
- 用户流程：成功、失败、空、加载、权限、禁用状态
- 组件复用方案
- 表格列、筛选、排序、分页、行操作、批量操作
- 表单字段、校验、提交反馈、取消/返回、未保存风险
- API 调用与状态刷新
- 防重复点击、防抖/节流
- 响应式和浏览器验证路径
- `Req ID 覆盖映射`
- `已读输入`、`引用证据`、`未覆盖项`、`下游依赖`

## 停止条件

- 页面或入口无法定位。
- 组件库、状态管理或 API 调用模式不清。
- 设计要求改变 API、权限、依赖或公共行为但工程规格未覆盖。
- 前端相关 Req ID 未覆盖且无确认排除。
