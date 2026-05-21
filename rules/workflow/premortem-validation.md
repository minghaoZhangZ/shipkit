# Pre-mortem Validation Protocol

子 Agent 在开始任何产出性工作前，必须执行输入完整性校验。校验不通过时，禁止产出设计文档。

## Input Manifest 格式

CONTEXT_PACKAGE.md 的 `## Input Manifest` 节使用以下结构：

| 文件路径 | 必需性 | 最小内容判据 |
|---------|--------|-------------|
| 02_工程需求规格.md | required | "功能需求"节存在且至少含 1 个 REQ-xxx 标记 |
| 03_代码库调研.md | required | "涉及模块"节存在且非空 |

必需性取值：
- `required`：缺少则阻断，不得产出设计文档。
- `conditional`：需检查 affected_areas 或上下文判断是否需要；需要时同 required 处理。
- `optional`：缺少不阻断，但在输出"已读输入"中标注未读及原因。

## Agent 校验步骤

1. 读取 `<change-dir>/CONTEXT_PACKAGE.md`，定位 `## Input Manifest` 节。
2. 对每一行 `required` 文件：Read 该文件，验证最小内容判据是否通过。
3. 对每一行 `conditional` 文件：根据 `<change-dir>/.workflow_state` 中的 `affected_areas` 和当前阶段上下文判断是否需要。需要则同 `required` 处理；不需要则在输出中标注跳过。
4. 校验完成后，在输出文档的"已读输入"节写入结构化校验结果。

## 校验失败协议

任一 `required` 文件缺失或判据不通过时：

1. 写入 `<change-dir>/PENDING_DECISIONS.md`（追加模式）：
   ```
   ## [Pre-mortem] 输入完整性校验失败 — <yyyy-mm-dd HH:MM>

   | 文件 | 必需性 | 状态 | 详情 |
   |------|--------|------|------|
   | <path> | required | MISSING / EMPTY / INCOMPLETE | <具体判据不通过细节> |

   阻塞原因: 缺少 required 输入，无法产出可靠的设计文档。
   建议操作: 主控 Agent 检查 CONTEXT_PACKAGE.md 的 Input Manifest 是否完整，补全缺失文件后重新调用本 Agent。
   ```

2. **停止当前 Agent**，不产出任何设计文档。
3. 向主控返回：校验失败的文件清单和原因。

## 校验通过格式

校验通过后，在输出文档"已读输入"节使用以下格式，放在文件列表之前：

```
## 已读输入

### Pre-mortem 校验结果

| 文件 | 行数/大小 | 关键内容判据 | 校验结果 |
|------|----------|-------------|---------|
| 02_工程需求规格.md | 287 行 | Req ID 数量: 5 | PASS |
| 03_代码库调研.md | 156 行 | 涉及模块 ≥ 1 | PASS |
| 04_后端方案说明.md | N/A | affected_areas 不含 backend，跳过 | SKIP |

### 已读文件
- ...
```

## 主控 Agent 职责

1. 每个阶段开始前，更新 CONTEXT_PACKAGE.md 时**必须填写 `## Input Manifest` 节**。
2. Input Manifest 的内容必须与 `## 当前阶段必读` 一致——不允许"必读但未列入 manifest"。
3. 调用子 Agent 后，检查子 Agent 返回结果的"已读输入"节是否包含 Pre-mortem 校验结果。
4. 如果子 Agent 报告校验失败：补全缺失文件，修复 CONTEXT_PACKAGE.md 的 Input Manifest，重新调用子 Agent，不得跳过。
5. 如果子 Agent 输出中**没有** Pre-mortem 校验结果：视为校验未执行，主控 Agent 必须追问子 Agent 或在 `PENDING_DECISIONS.md` 中记录风险。

## 常见失败原因及修复

| 失败原因 | 修复方式 |
|---------|---------|
| 文件不存在（MISSING） | 主控 Agent 检查该阶段是否应已产出该文件；如应产出但未产出，回溯上一阶段 |
| 文件存在但关键节为空（EMPTY） | 主控 Agent 检查文件内容是否被截断或写入不完整 |
| 判据不通过（INCOMPLETE） | 主控 Agent 检查判据是否合理；判据合理则补全文件内容 |
| Input Manifest 节缺失 | 主控 Agent 未填写，需补全 CONTEXT_PACKAGE.md |

## 与现有流程的集成

- pre-mortem 校验是**编码前防御**，checkpoint 确认是**编码后确认**，两者互补不替代。
- minimal profile 的 Agent 同样执行校验，判据可适当放宽（参见各 Agent 定义中的 minimal 判据）。
- 校验失败写入 PENDING_DECISIONS.md 后，主控 Agent 在下一轮调用前必须清空对应的 pre-mortem 阻塞项。
