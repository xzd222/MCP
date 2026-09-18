# Git 规范

## 分支
- 禁止直接提交 `main`/`master`（hook 强制；允许首次初始提交）
- 工作都在 `git checkout -b feature/xxx`，最后合并/PR 回 main

## 提交信息（Conventional Commits）
```
type(scope): subject
```
- type：feat / fix / refactor / test / docs / chore / build
- subject ≤ 72 字符，中英文任选但保持一致

## 硬性禁止（hook 强制拦截）
- `git push --force` / `-f` / `--force-with-lease`
- 提交 `.env`、`id_rsa`、`*.pem` 等密钥文件
- 提交含 `sk-` 明文的内容
- 暂存了 `.py` 改动但 `ruff check` 或 `pytest` 未通过时 commit

## 忽略清单
`.gitignore` 至少含：`.env`、`.venv/`、`__pycache__/`、`*.pyc`、`.pytest_cache/`、`.ruff_cache/`、`dist/`
