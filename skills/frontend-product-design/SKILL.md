---
name: frontend-product-design
description: Use when a product requirement changes frontend pages, components, routes, forms, tables, dashboards, navigation, visual states, responsive behavior, or user interactions in business systems.
---

# Frontend Product Design

Use this skill inside `frontend-design-check-flow`. Write the result to `05_前端方案说明.md`; old changes may be read from `05_FRONTEND_DESIGN.md`.

## Core Principle

Design business frontend changes as usable product surfaces, not decorative pages. Favor clarity, scanability, permission-aware behavior, stable interaction states, and reuse of the project's existing component system.

## Required Inputs

- `CONTEXT_PACKAGE.md`
- `01_PRD产品需求.md`
- `02_工程需求规格.md`
- `03_代码库调研.md`
- Existing UI code evidence when available.

If evidence is insufficient, stop and write: `证据不足，需要继续调研。`

## Output Structure

Write `05_前端方案说明.md` 包含以下三区：

**概览区：**
1. TL;DR — 页面目标、涉及模块、关键决策
2. 页面与入口 — route/menu/button/modal/drawer entry points

**正文区：**
3. 用户流程 — success/failure/empty/loading/permission states
4. 组件方案 — reuse existing components first
5. 数据与状态 — API data, local state, form state, validation
6. 交互与反馈 — loading/disabled/error/toast/dialog
7. 响应式与可访问性 — desktop/mobile, keyboard/focus
8. 验证点 — browser paths, viewport sizes, key operations

**附录区：**
9. Req ID 覆盖映射
10. 已读输入、引用证据、未覆盖项、下游依赖

## Design Rules

- Follow existing visual language, component libraries, icons, spacing, and route patterns.
- For management/admin systems, prefer dense but readable layouts over hero/marketing composition.
- Tables must define columns, filters, sorting, pagination, row actions, bulk actions, empty state, and permission behavior when applicable.
- Forms must define labels, required rules, submit feedback, validation timing, cancel/back behavior, unsaved-change risk, and error placement.
- Destructive or irreversible actions require confirmation and recoverability notes.
- Do not introduce new dependencies, fonts, icon libraries, animation libraries, or design systems unless `07_实施计划.md` explicitly allows them.
- Do not claim usability improvements without observable acceptance criteria.

## Stop Conditions

- The required page/route cannot be located.
- The intended component library or state pattern is unclear.
- A design requires changing API contracts, permissions, dependencies, or public behavior not covered by `02_工程需求规格.md`.
- A Req ID has no frontend design coverage and no user-confirmed exclusion.
