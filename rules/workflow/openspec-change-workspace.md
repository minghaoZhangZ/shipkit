# OpenSpec Change Workspace Rules

每个需求必须有独立 change 目录。

## Change ID

格式：`<yyyy-mm-dd>-<type>-<domain>-<中文动作>`

示例：`2026-04-30-feature-recommend-增加推荐理由`

## Directory

当前需求目录称为 `<change-dir>`：`openspec/changes/<change-id>`

AI 阶段文档统一写入 `<change-dir>/`。新流程不再产出 `10_自查报告.md`（已废弃），其机械检查并入 verification 阶段、判断性检查并入 review 阶段。文档编号 09/11/12/13/14 保留，10 跳号。旧 change 可保留原有 00 到 14 的历史编号。

模板来源：`openspec/_templates/change/` 和 `openspec/_templates/`
模板缺失时：Agent 直接创建文件，不从模板复制。首次使用会自动 bootstrap openspec 目录结构。

## Archive

完成后归档到：`openspec/changes/archive/<change-id>`

归档前必须：更新测试结果、完成审查报告、写发布说明、写经验沉淀、判断是否需要更新 `openspec/specs/`。

项目级一致性治理可选：

- 只有存在 `openspec/specs/engineering/engineering.json` 且 `enabled=true` 时，才读取 `openspec/specs/engineering/`。
- `schemaVersion >= 2` 的 `engineering.json` 使用 `rulePrefixIndex` 进行规则发现；v1 `requiredSpecs` 视为 legacy 兼容模式。
- 未启用时不得阻断 Base Flow。
- `mode=advisory` 只记录风险，`mode=enforced` 可作为归档门禁。
