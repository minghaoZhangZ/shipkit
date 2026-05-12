---
name: openspec-new-change
description: Use when starting a new requirement, feature, bugfix, refactor, security fix, data migration, performance task, or test task that needs an OpenSpec change workspace.
---

# OpenSpec New Change

## Change ID

格式：

```text
<yyyy-mm-dd>-<type>-<domain>-<中文动作>
```

示例：

```text
2026-04-30-feature-recommend-增加推荐理由
2026-04-30-bugfix-order-修复状态并发
```

## Flow

1. 根据需求生成 `<change-id>`。
2. 确保 OpenSpec 基础目录存在（老项目自动 bootstrap）：

```bash
# 项目根目录下执行
mkdir -p openspec/changes/archive
mkdir -p openspec/specs
mkdir -p openspec/_templates/change
mkdir -p openspec/_templates/ai
# 模板不存在时自动创建最小 metadata.json
test -f openspec/_templates/change/metadata.json || cat > openspec/_templates/change/metadata.json << 'TMPL'
{
  "id": "",
  "title": "",
  "type": "feature",
  "domain": "",
  "action": "",
  "status": "draft",
  "createdAt": "",
  "profile": "standard",
  "owner": ""
}
TMPL
```

3. 创建 change 目录：

```text
mkdir -p openspec/changes/<change-id>/ai
mkdir -p openspec/changes/<change-id>/specs
```

4. 复制模板（模板缺失时跳过，Agent 直接写文件）：

4. 更新 `metadata.json`：

```json
{
  "id": "<change-id>",
  "title": "<需求标题>",
  "type": "<type>",
  "domain": "<domain>",
  "action": "<中文动作>",
  "status": "draft",
  "createdAt": "YYYY-MM-DD",
  "profile": "minimal|standard|strict",
  "owner": "minghao"
}
```

5. 将原始需求写入 `<change-dir>/ai/00_REQUIREMENT.md`。

## 下一步

根据需求类型选择 flow：

- 常规需求：调用 `product-to-test-flow`
- 高风险需求：调用 `strict-product-to-test-flow`
- 小修复：调用 `quick-fix-flow`

## Type Values

```text
feature
bugfix
hotfix
refactor
techdebt
perf
security
data
docs
test
```

## Status Values

```text
draft
planning
approved
implementing
verifying
reviewing
done
archived
```
