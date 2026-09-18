"""矿权日报 Agent：连接 3 个 MCP server，ReAct 编排 + dry-run。"""
from __future__ import annotations

import json
import logging
import sys
from contextlib import AsyncExitStack
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from agent.model import Model
from agent.report import build_report

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "你是矿权日报 Agent。可用工具：search / fetch_article（矿业新闻）、"
    "extract_resources（NI 43-101 储量）、get_price / get_trend（价格行情）。"
    "根据用户问题选择合适的工具收集数据，工具返回 JSON，直接调用即可。"
)

MAX_STEPS = 6

TOPICS: dict[str, tuple[str, str | None, str]] = {
    "锂": ("锂", "https://example.com/pdfs/pilbara-43-101.pdf", "锂"),
    "lithium": ("锂", "https://example.com/pdfs/pilbara-43-101.pdf", "锂"),
    "金": ("金", "https://example.com/pdfs/newmont-redchris-43-101.pdf", "金"),
    "gold": ("金", "https://example.com/pdfs/newmont-redchris-43-101.pdf", "金"),
    "铜": ("铜", None, "铜"),
    "copper": ("铜", None, "铜"),
}
DEFAULT_TOPIC: tuple[str, str | None, str] = (
    "锂",
    "https://example.com/pdfs/pilbara-43-101.pdf",
    "锂",
)


def infer_topic(question: str) -> tuple[str, str | None, str]:
    """从问题推断 (品种, 储量 PDF, 新闻关键词)。"""
    q = question.lower()
    for key, value in TOPICS.items():
        if key in q:
            return value
    return DEFAULT_TOPIC


def _server_params(module: str) -> StdioServerParameters:
    return StdioServerParameters(command=sys.executable, args=["-m", module])


SERVER_SPECS: list[tuple[str, StdioServerParameters]] = [
    ("mining-news", _server_params("servers.mining_news.server")),
    ("mineral-pdf", _server_params("servers.mineral_pdf.server")),
    ("lme-price", _server_params("servers.lme_price.server")),
]


class MiningAgent:
    """连接 MCP server，运行 ReAct 或 dry-run，输出日报。"""

    def __init__(
        self,
        model: Model,
        server_specs: list[tuple[str, StdioServerParameters]] | None = None,
    ) -> None:
        self.model = model
        self.server_specs = server_specs or SERVER_SPECS

    async def run(self, question: str) -> str:
        async with AsyncExitStack() as stack:
            sessions, tools = await self._connect(stack)
            openai_tools = [self._to_openai(spec) for spec in tools.values()]
            if self.model.is_dry_run:
                collected = await self._dry_run(question, sessions, tools)
            else:
                collected = await self._run_with_fallback(
                    question, sessions, tools, openai_tools
                )
        return build_report(question, collected)

    async def _run_with_fallback(
        self,
        question: str,
        sessions: dict[str, ClientSession],
        tools: dict[str, dict[str, Any]],
        openai_tools: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        try:
            return await self._react(question, sessions, tools, openai_tools)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM 调用失败，回退 dry-run：%s", exc)
            return await self._dry_run(question, sessions, tools)

    async def _connect(
        self, stack: AsyncExitStack
    ) -> tuple[dict[str, ClientSession], dict[str, dict[str, Any]]]:
        sessions: dict[str, ClientSession] = {}
        tools: dict[str, dict[str, Any]] = {}
        for name, params in self.server_specs:
            read, write = await stack.enter_async_context(stdio_client(params))
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            sessions[name] = session
            result = await session.list_tools()
            for tool in result.tools:
                tools[tool.name] = {"server": name, "tool": tool}
        return sessions, tools

    @staticmethod
    def _to_openai(spec: dict[str, Any]) -> dict[str, Any]:
        tool = spec["tool"]
        parameters = getattr(tool, "inputSchema", None) or {"type": "object", "properties": {}}
        if hasattr(parameters, "model_dump"):
            parameters = parameters.model_dump()
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": getattr(tool, "description", "") or "",
                "parameters": parameters,
            },
        }

    async def _call_tool(
        self,
        sessions: dict[str, ClientSession],
        tools: dict[str, dict[str, Any]],
        name: str,
        args: dict[str, Any],
    ) -> str:
        if name not in tools:
            return json.dumps({"error": f"未知工具 {name}"}, ensure_ascii=False)
        session = sessions[tools[name]["server"]]
        result = await session.call_tool(name, args)
        return self._extract_text(result)

    @staticmethod
    def _extract_text(result: Any) -> str:
        blocks = getattr(result, "content", None) or []
        texts: list[str] = []
        for block in blocks:
            text = getattr(block, "text", None)
            if text is not None:
                texts.append(text)
        return "\n".join(texts)

    async def _react(
        self,
        question: str,
        sessions: dict[str, ClientSession],
        tools: dict[str, dict[str, Any]],
        openai_tools: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]
        collected: list[dict[str, Any]] = []
        for _ in range(MAX_STEPS):
            resp = await self.model.complete(messages, openai_tools)
            tool_calls = resp.get("tool_calls") or []
            if not tool_calls:
                break
            messages.append(
                {
                    "role": "assistant",
                    "content": resp.get("content") or "",
                    "tool_calls": tool_calls,
                }
            )
            for tc in tool_calls:
                name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"].get("arguments") or "{}")
                except json.JSONDecodeError:
                    args = {}
                text = await self._call_tool(sessions, tools, name, args)
                collected.append({"tool": name, "args": args, "result": text})
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": text})
        return collected

    async def _dry_run(
        self,
        question: str,
        sessions: dict[str, ClientSession],
        tools: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        commodity, pdf_url, keyword = infer_topic(question)
        collected: list[dict[str, Any]] = []

        async def call(name: str, args: dict[str, Any]) -> None:
            text = await self._call_tool(sessions, tools, name, args)
            collected.append({"tool": name, "args": args, "result": text})

        await call("search", {"query": keyword, "days": 30})
        if pdf_url:
            await call("extract_resources", {"pdf_url": pdf_url})
        await call("get_trend", {"commodity": commodity, "days": 30})
        return collected
