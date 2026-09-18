# 代码规范

## 语言与工具
- Python 3.11+，类型标注全覆盖（文件头 `from __future__ import annotations`）
- 静态检查/格式用 `ruff`（line-length=100），提交前 `ruff check`
- 包管理 `uv`（无则 pip），依赖写进 `pyproject.toml`，锁定版本

## MCP server 结构（3 个一致）
每个 server 一个目录 `servers/<name>/`：
- `server.py`：用 `mcp` 官方 SDK，`@server.list_tools()` 注册 + `@server.call_tool()` 分发
- 工具函数必须：类型标注 + docstring（含参数/返回说明）
- 数据源与工具逻辑分离，样例数据放 `servers/<name>/data/`

## 通用约束
- 函数单一职责，超 40 行考虑拆分
- 不写死魔法值，抽成常量/配置
- 用 `logging`，禁止 `print` 调试残留
- 命名：函数/变量 `snake_case`，类 `PascalCase`，常量 `UPPER_SNAKE`
