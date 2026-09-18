# 任务清单

> 顺序执行，每完成一项再进下一项；每项含「写代码 + 写测试 + 通过检查」。

## 工作流约定（每个 task 完成后）
1. `ruff check` + `pytest` 全绿
2. 提交并推送一次（中文备注，走 SSH）
3. `TaskUpdate` 更新任务状态
4. 上下文压缩：进度摘要写入 memory，仅保留最近 3 轮完整对话

- [x] 1. 项目骨架：`pyproject.toml` + `.gitignore` + `git init` + `.env.example`
- [x] 2. `servers/mining_news`（search / fetch_article）+ 测试
- [x] 3. `servers/mineral_pdf`（extract_resources）+ 测试
- [x] 4. `servers/lme_price`（get_price / get_trend）+ 测试
- [ ] 5. `agent/` ReAct 编排（含 dry-run）+ 测试
- [ ] 6. `mcp-config.json` + `RUN.md` + `docker-compose.yml`
- [ ] 7. `README.md`（架构图 + 5 分钟跑通说明）
- [ ] 8. 全量 `ruff check` + `pytest` 通过，推 GitHub
