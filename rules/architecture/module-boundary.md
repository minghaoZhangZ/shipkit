# Module Boundary Rules

跨模块依赖前必须确认：

- 目标 API 是否 public 且 intended for reuse。
- 依赖方向是否符合当前模块结构。
- 是否已有同类调用。
- 是否应该抽取 helper、strategy、domain service 或 adapter。

如果当前代码库没有明确模式，必须在设计文档中标记为待确认。
