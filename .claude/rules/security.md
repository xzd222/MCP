# 安全与注意事项

## 密钥（最高优先级）
- API key 只写 `.env`（已 gitignore），代码/文档/日志禁止 `sk-` 明文
- 运行前 `cp .env.example .env` 再填 key；仓库只提交 `.env.example`（占位无真值）

## aihubmix 免费模型
- `base_url=https://aihubmix.com/v1`，模型带 `-free` 后缀（如 `gpt-4o-free`）
- 有 RPM + 每日 token 上限；Agent 必须保留 **dry-run 模式**（无 key/限流时用假模型跑通）

## 其他注意事项
- 不提交真实 PDF / 大体积样例文件（放 `data/` 并 gitignore，或给下载链接）
- MCP server 默认不联网；真实抓取作为可选开关，默认关
- 提交前自查：`git diff --cached` 扫一遍，确认无密钥/大文件
