# Verification Loop Rules

没有真实命令输出，就不能声称完成、通过或修复。

## Required Evidence

- 实际运行命令、退出码、关键输出。
- 失败项、未运行项及原因、剩余风险。
- 新流程 change 还必须有 self-review 记录和 CHANGE_METRICS；旧 change 缺失时说明不适用。

## Depth

- minimal：目标测试或最小复现命令。
- standard：构建 + 测试 + lint/typecheck。
- strict：standard + 安全、数据库、回滚相关检查。

## Forbidden Claims

- 应该可以通过、看起来没问题、之前跑过、只改一点不用测。
- self-review 还没跑但声称可以验证/交付。
