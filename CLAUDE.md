# 项目开发规则

**项目**：MCP 矿权日报 Agent（面试题 #2）
**约束**：24h 内上传 GitHub · 全程 Claude Code 编写 · 工程化规范

## 已确认决策（勿再讨论）
- 编排：自写 ReAct（非 LangGraph）
- LLM：aihubmix 免费模型，OpenAI 兼容 `base_url=https://aihubmix.com/v1`；必须保留 dry-run（无 key 可跑通）
- 目录：`servers/`(3 个 MCP server) · `agent/`(编排) · `tests/` · `mcp-config.json` · `RUN.md` · `docker-compose.yml`

## 硬性规则（违反即重做）
1. 密钥不入库：API key 只写 `.env`（已 gitignore），代码/文档/日志禁止出现 `sk-` 明文。
2. 提交前过 `ruff check` + `pytest`（由 hook 强制）。
3. 禁止 `push --force`、禁止直接提交 `main`/`master`（由 hook 强制）。
4. 每个模块带测试；函数/工具带类型标注 + docstring。

## 渐进式披露（按需读取，别全读）
| 场景 | 读 |
|---|---|
| 写代码 | `.claude/rules/code.md` |
| git 操作 | `.claude/rules/git.md` |
| 写/跑测试 | `.claude/rules/testing.md` |
| 密钥/限流/注意事项 | `.claude/rules/security.md` |
| 任务清单 | `.claude/rules/tasks.md` |
