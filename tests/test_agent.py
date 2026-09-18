"""Agent 编排测试。"""
from __future__ import annotations

import asyncio
from typing import Any

from agent.agent import MiningAgent, infer_topic
from agent.model import DryRunModel, Model

QUESTION = "生成一份关于 Pilbara 锂矿的今日简报"


class _FailingModel(Model):
    async def complete(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]
    ) -> dict[str, Any]:
        raise RuntimeError("模拟 LLM 失败")


def test_infer_topic_lithium() -> None:
    assert infer_topic("Pilbara 锂矿")[0] == "锂"


def test_infer_topic_defaults_to_lithium() -> None:
    commodity, _, _ = infer_topic("随便说点啥")
    assert commodity == "锂"


def test_dry_run_end_to_end() -> None:
    report = asyncio.run(_run(DryRunModel()))
    _assert_report(report)


def test_llm_failure_falls_back_to_dry_run() -> None:
    report = asyncio.run(_run(_FailingModel()))
    _assert_report(report)


def _assert_report(report: str) -> None:
    for section in ("# 矿权日报", "## 新闻摘要", "## 储量数据", "## 价格走势", "## 引用来源"):
        assert section in report
    assert "锂" in report


async def _run(model: Model) -> str:
    agent = MiningAgent(model)
    return await agent.run(QUESTION)
