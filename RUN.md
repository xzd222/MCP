# 运行指南（5 分钟跑通）

## 方式一：本地 Python（推荐）

### 1. 准备环境
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -e ".[dev]"
```

### 2.（可选）配置 LLM
```bash
cp .env.example .env
# 编辑 .env，填入 AIHUBMIX_API_KEY
```
不配置 key 也能跑 —— 会自动进入 dry-run 模式（无需网络、无需 LLM）。

### 3. 生成日报
```bash
# dry-run（离线可用，最快）
python -m agent --dry-run "生成一份关于 Pilbara 锂矿的今日简报"

# LLM 模式（需能连 aihubmix，失败自动回退 dry-run）
python -m agent "生成一份关于 Pilbara 锂矿的今日简报"
```

### 4. 跑测试与静态检查
```bash
ruff check . && pytest
```

## 方式二：Docker
```bash
docker compose run --rm agent
```

## 接入 Claude Desktop / Cursor
把 `mcp-config.json` 的 `mcpServers` 内容合并进 Claude Desktop 配置（或 Cursor 的 MCP 配置），即可让 Claude/Cursor 直接调用 3 个 server 的工具。

## 三个 MCP server
| server | 工具 | 启动模块 |
|---|---|---|
| mining-news | `search` / `fetch_article` | `servers.mining_news.server` |
| mineral-pdf | `extract_resources` | `servers.mineral_pdf.server` |
| lme-price | `get_price` / `get_trend` | `servers.lme_price.server` |

## 项目结构
```
servers/  三个 MCP server（各自 store.py + server.py + data/）
agent/    ReAct 编排（model.py + report.py + agent.py + __main__.py）
tests/    pytest 测试
```
