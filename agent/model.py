"""LLM 模型抽象：OpenAI 兼容实现 + dry-run 兜底。"""
from __future__ import annotations

from typing import Any


class Model:
    """LLM 模型接口。"""

    is_dry_run: bool = False

    async def complete(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]
    ) -> dict[str, Any]:
        raise NotImplementedError


class DryRunModel(Model):
    """无 LLM 的演示模式，不发起任何模型调用。"""

    is_dry_run = True

    async def complete(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]
    ) -> dict[str, Any]:
        return {"content": "", "tool_calls": []}


class OpenAIModel(Model):
    """OpenAI 兼容模型（aihubmix 免费模型）。"""

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=15.0)
        self._model = model

    async def complete(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]
    ) -> dict[str, Any]:
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            tools=tools or None,
            temperature=0.3,
        )
        msg = resp.choices[0].message
        tool_calls = [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments or "{}"},
            }
            for tc in (msg.tool_calls or [])
        ]
        return {"content": msg.content or "", "tool_calls": tool_calls}
