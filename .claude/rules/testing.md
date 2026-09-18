# 测试规范

- 框架 `pytest`，测试放 `tests/`，命名 `test_*.py`
- 每个 MCP 工具至少 1 条用例；Agent 编排至少 1 条 dry-run 用例
- dry-run 模式必须有测试（无 key 也能跑）
- 提交前 `pytest -q` 全绿（hook 强制）

## 用例设计原则
- 覆盖：正常路径 + 边界（空输入/异常参数）+ 失败回退
- 测试不得依赖外部网络/真实 API key（用 mock/fixture）
