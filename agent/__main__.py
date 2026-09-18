"""矿权日报 Agent 命令行入口。

用法：python -m agent "生成一份关于 Pilbara 锂矿的今日简报"
"""
from __future__ import annotations

import asyncio
import os
import sys

from dotenv import load_dotenv

from agent.agent import MiningAgent
from agent.model import DryRunModel, OpenAIModel


def _build_model() -> DryRunModel | OpenAIModel:
    api_key = os.getenv("AIHUBMIX_API_KEY", "").strip()
    if api_key and api_key != "your_api_key_here":
        base_url = os.getenv("AIHUBMIX_BASE_URL", "https://aihubmix.com/v1")
        model = os.getenv("AIHUBMIX_MODEL", "gpt-4o-free")
        return OpenAIModel(api_key=api_key, base_url=base_url, model=model)
    return DryRunModel()


def _parse_args() -> tuple[str, bool]:
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    rest = [a for a in args if a != "--dry-run"]
    question = rest[0] if rest else "生成一份关于 Pilbara 锂矿的今日简报"
    return question, dry_run


async def _main() -> None:
    question, dry_run = _parse_args()
    model = DryRunModel() if dry_run else _build_model()
    agent = MiningAgent(model)
    print(await agent.run(question))


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(_main())
