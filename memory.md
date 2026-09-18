# 项目记忆（上下文摘要）

> 每完成一个 task 更新一次；压缩上下文时仅保留最近 3 轮完整对话。

## 概览
- 题目 #2：MCP 矿权日报 Agent
- 仓库：git@github.com:xzd222/MCP.git（push 走 SSH）
- 栈：Python 3.13 · mcp 2.2.0 · openai 3.15.0 · pytest · ruff · python-dotenv

## 已确认决策
- 编排：自写 ReAct（非 LangGraph）
- LLM：aihubmix `gpt-4o-free`（base_url=https://aihubmix.com/v1），失败自动回退 dry-run
- 结构：servers/（3 MCP server）+ agent/（编排）+ tests/

## 进度
- [x] 1 骨架 + venv + git + hook
- [x] 2 mining-news（search / fetch_article）
- [x] 3 mineral-pdf（extract_resources）
- [x] 4 lme-price（get_price / get_trend）
- [x] 5 ReAct agent（含 LLM 失败回退，25 测试绿）
- [ ] 6 mcp-config.json + RUN.md + docker-compose
- [ ] 7 README
- [ ] 8 全量检查 + 推送

## 注意
- 本机连不上 GitHub(HTTPS) 与 aihubmix，push 用 SSH，演示用 `--dry-run`
- hook（.claude/settings.json）需 /hooks 或重启才生效
- key 在 .env（gitignore）；面试资料 docx/md 不提交
