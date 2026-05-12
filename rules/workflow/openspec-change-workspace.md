# OpenSpec Change Workspace Rules

每个需求必须有独立 change 目录。

## Change ID

格式：`<yyyy-mm-dd>-<type>-<domain>-<中文动作>`

示例：`2026-04-30-feature-recommend-增加推荐理由`

## Directory

当前需求目录称为 `<change-dir>`：`openspec/changes/<change-id>`

AI 阶段文档统一写入 `<change-dir>/ai/`。新流程包含 `10_SELF_REVIEW.md`、`CHANGE_METRICS.json`，并将 review / release / lessons / eval 文档顺延到 11-14；旧 change 可保留 00 到 13 的历史编号。

模板来源：`openspec/_templates/change/` 和 `openspec/_templates/ai/`
模板缺失时：Agent 直接创建文件，不从模板复制。首次使用会自动 bootstrap openspec 目录结构。

## Archive

完成后归档到：`openspec/changes/archive/<change-id>`

归档前必须：更新测试结果、完成审查报告、写发布说明、写经验沉淀、判断是否需要更新 `openspec/specs/`。

项目级一致性治理可选：

- 只有存在 `openspec/specs/engineering/engineering.json` 且 `enabled=true` 时，才读取 `openspec/specs/engineering/`。
- 未启用时不得阻断 Base Flow。
- `mode=advisory` 只记录风险，`mode=enforced` 可作为归档门禁。
