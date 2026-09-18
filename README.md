# MCP 矿权日报 Agent

输入一句自然语言，由 3 个 MCP server + 自写 ReAct 编排，输出结构化 Markdown 矿权日报。

日报包含：**新闻摘要 · 储量数据 · 价格走势 · 风险提示 · 引用来源**。

## 架构

```
用户提问
   │
   ▼
Agent client（自写 ReAct，agent/）
   │  MCP 协议（stdio）
   ├── mining-news  →  search / fetch_article
   ├── mineral-pdf  →  extract_resources
   └── lme-price    →  get_price / get_trend
```

## 快速开始

```bash
pip install -e ".[dev]"

# 离线演示（dry-run，无需网络/LLM）
python -m agent --dry-run "生成一份关于 Pilbara 锂矿的今日简报"

# LLM 模式（配置 .env 的 aihubmix key；失败自动回退 dry-run）
python -m agent "生成一份关于 Pilbara 锂矿的今日简报"
```

详见 [RUN.md](RUN.md)（含 Docker 方式）。

## 交付清单

- 3 个 MCP server（mcp 2.x `MCPServer` API）
- 1 个 client 端 Agent 编排（自写 ReAct + dry-run 兜底）
- `mcp-config.json` —— 可直接接 Claude Desktop / Cursor
- `RUN.md` —— 5 分钟跑通，含 docker-compose
- 测试：pytest 25 例 + `ruff` 静态检查

## 工程化

- Python 3.11+，全量类型标注，`ruff` 检查
- git hook：禁 force-push / 禁提交密钥 / 提交前强制 ruff+pytest
- 规则文档（渐进式披露）：`CLAUDE.md` + `.claude/rules/`
