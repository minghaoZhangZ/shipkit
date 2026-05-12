---
name: search-first
description: Use when adding new functionality, abstractions, libraries, tools, integrations, algorithms, or infrastructure that might already exist.
---

# Search First

先查已有能力，再决定 adopt、wrap、build 或 defer。

## Flow

1. 明确要解决的问题。
2. 先查当前代码库：
   - 相似模块
   - 工具类
   - 现有依赖
   - 测试样例
3. 再查项目依赖和官方能力。
4. 必要时查成熟开源方案、MCP、skill 或内部规范。
5. 输出决策：
   - `adopt`：直接采用。
   - `wrap`：薄封装复用。
   - `build`：自研，并说明原因。
   - `defer`：证据不足。

## Output

建议写入 `<change-dir>/ai/03_CODEBASE_RESEARCH.md`：

```text
## Search-first 结论

### 问题定义
### 已有项目能力
### 可复用依赖或工具
### 外部成熟方案
### 决策：adopt / wrap / build / defer
### 证据
```

## Common Mistakes

- 没查代码库就写 helper。
- 为一个小功能引入巨大依赖。
- 明明已有项目模式却自造一套。
- 外部方案没有许可证、维护状态或兼容性判断。
