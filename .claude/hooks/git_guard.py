#!/usr/bin/env python3
"""Git 提交/推送保护（Claude Code PreToolUse hook）。

规则：
  1. 禁止 push --force / -f / --force-with-lease
  2. 分支保护：默认关闭（solo 直接提交 main；团队协作再启用，见 2a）
  3. 禁止暂存疑似密钥文件（.env、id_rsa、*.pem 等，或内容含 sk- 明文）
  4. 暂存了 .py 改动时，commit 前强制 ruff check + pytest（未安装则跳过）

stdin 接收 hook 输入 JSON；拒绝时输出 permissionDecision=deny 并 exit 0。
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

SECRET_NAMES = ("id_rsa", "id_dsa", "id_ecdsa", "id_ed25519")
SECRET_SUFFIXES = (".pem", ".p12", ".pfx", ".key")

# 强制 UTF-8 输出，避免 Windows 控制台 GBK 编码导致 hook 解析出乱码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _emit_deny(reason: str) -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(payload, ensure_ascii=False))
    sys.exit(0)


def _run(cmd: list[str], cwd: str):
    """返回 (CompletedProcess|None, hint)；命令不存在时返回 (None, hint)。"""
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=90), None
    except FileNotFoundError:
        return None, f"`{cmd[0]}` 未安装"
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def _venv_tool(cwd: str, tool: str, *args: str) -> list[str]:
    """构造 venv 内工具的命令行（Windows: .venv/Scripts/，POSIX: .venv/bin/）。"""
    subdir = "Scripts" if os.name == "nt" else "bin"
    ext = ".exe" if os.name == "nt" else ""
    return [os.path.join(cwd, ".venv", subdir, tool + ext), *args]


def main() -> None:
    try:
        data = json.loads(sys.stdin.read())
    except Exception:  # noqa: BLE001
        return

    command = ((data.get("tool_input") or {}).get("command") or "").strip()
    cwd = data.get("cwd") or "."

    if not command.lower().startswith("git"):
        return

    parts = command.split()

    # 1) 禁止 force push
    if len(parts) >= 2 and parts[1] == "push":
        if any(t in ("--force", "-f", "--force-with-lease") for t in parts):
            _emit_deny("禁止 force push。请用普通 push，或与团队确认后走 rebase 流程。")

    # 2) 仅对 git commit 做密钥/质量校验
    if len(parts) < 2 or parts[1] != "commit":
        return

    # 2a) 分支保护：solo 项目默认关闭。团队协作时取消下方注释即可禁止直接提交 main/master。
    # proc, _ = _run(["git", "rev-parse", "--verify", "HEAD"], cwd)
    # if proc is not None and proc.returncode == 0:
    #     proc2, _ = _run(["git", "branch", "--show-current"], cwd)
    #     branch = (proc2.stdout or "").strip() if proc2 else ""
    #     if branch in ("main", "master"):
    #         _emit_deny(f"禁止直接提交到 `{branch}`。请先 `git checkout -b feature/xxx`。")

    # 2b) 密钥文件/明文扫描（只看已暂存内容）
    proc, _ = _run(["git", "diff", "--cached", "--name-only", "-z"], cwd)
    staged = [f for f in (proc.stdout or "").split("\x00") if f] if proc else []
    for f in staged:
        base = os.path.basename(f)
        if base == ".env.example":
            continue  # 模板文件，允许提交
        if base.endswith(".env") or base in SECRET_NAMES or base.endswith(SECRET_SUFFIXES):
            _emit_deny(f"疑似密钥文件 `{f}` 被暂存，禁止提交。请加入 .gitignore。")
        try:
            with open(os.path.join(cwd, f), encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
        except OSError:
            continue
        if re.search(r"sk-[A-Za-z0-9]{16,}", content):
            _emit_deny(f"`{f}` 含疑似 API key 明文（sk-...），禁止提交。请改用 .env 注入。")

    # 2c) 提交前质量门禁（仅当暂存了 .py 改动；工具未安装则跳过不拦截）
    if any(f.endswith(".py") for f in staged):
        failures: list[str] = []
        proc, _ = _run(_venv_tool(cwd, "ruff", "check", "."), cwd)
        if proc is not None and proc.returncode != 0:
            out = ((proc.stdout or "") + (proc.stderr or ""))[:2000]
            failures.append(f"ruff check 未通过：\n{out}")
        proc, _ = _run(_venv_tool(cwd, "python", "-m", "pytest", "-q"), cwd)
        if proc is not None and proc.returncode != 0:
            out = ((proc.stdout or "") + (proc.stderr or ""))[:2000]
            failures.append(f"pytest 未通过：\n{out}")
        if failures:
            _emit_deny("提交被质量门禁拦截：\n" + "\n\n".join(failures))


if __name__ == "__main__":
    main()
