---
name: backend-design-check-flow
description: Use when backend APIs, services, transactions, SQL, integrations, permissions, concurrency, or data consistency require design review before implementation.
---

# Backend Design Check Flow

目标：生成可审查的 `04_后端方案说明.md`，并在后端实施任务生成或编码前获得后端确认。

## 输入

必读：

- `CONTEXT_PACKAGE.md`
- `02_工程需求规格.md`
- `03_代码库调研.md`
- 工程规范（通过 `engineering.json` rulePrefixIndex 发现，glob `openspec/specs/engineering/**/*.md` + grep 前缀）：
  - JAVA-DA-/JAVA-CQ-/JAVA-CFG- 前缀（Java 编码与数据访问）
  - TX- 前缀（Spring 事务与并发）
  - DB-IDX-/DB-QRY-/DB-SAFE-/DB-DEPLOY- 前缀（SQL 与数据库）

按需读取架构规范（MOD-API-/MOD-PRIVATE-/DEP-/ARCH-LAYER-/API-REUSE- 前缀）和相关源码。

## 执行

1. 确认 `engineering_spec_confirmation` 已通过；minimal 可跳过但仍要有代码证据。
2. 更新 `CONTEXT_PACKAGE.md`，`current_phase=backend_design`，填写 Input Manifest。
3. 调用 `backend-designer` 输出 `04_后端方案说明.md`。
4. Agent 返回后检查其输出"已读输入"节是否包含 Pre-mortem 校验通过标记；校验失败时补全输入并重新调用，不得跳过。
5. 设计期 review：
   - Java/Spring 改动：调用 `java-reviewer`。
   - SQL、索引、迁移、表结构：调用 `database-reviewer`。
   - 权限、敏感数据、外部输入：调用 `security-reviewer`。
5. 阻塞问题写入 `PENDING_DECISIONS.md` 或修订后端方案。
6. 设置 checkpoint：

```yaml
checkpoint: backend_design_confirmation
requires_user_confirmation: true
user_confirmed: false
confirmation_type: approve_backend_design
confirmation_role: backend_owner
confirmation_docs: ["04_后端方案说明.md"]
```

## 输出合同

`04_后端方案说明.md` 必须包含：

**概览区：** TL;DR、设计目标、涉及模块与依赖方向、关键决策
**正文区：** Controller / Service / Repository / Mapper 边界、DTO / VO / Entity 关系、事务边界和小事务说明、锁/并发/幂等策略、SQL/索引/批量查询策略、外部接口调用位置及事务外处理、异常/日志/审计、复用现有代码的证据、后端任务拆分
**附录区：** Req ID 覆盖映射、已读输入、引用证据、未覆盖项、下游依赖

## 停止条件

- 缺少代码库证据。
- 需要跨模块/public API 依赖但证据不足。
- 事务、并发、外部接口、SQL 风险无法判断。
- 后端相关 Req ID 未覆盖且无确认排除。
