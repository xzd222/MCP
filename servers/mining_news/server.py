"""mining-news MCP server：新闻搜索与正文抓取。

以 stdio 方式运行：python -m servers.mining_news.server
"""
from __future__ import annotations

import json

from mcp.server.mcpserver import MCPServer

from servers.mining_news.store import NewsStore

mcp = MCPServer("mining-news")
store = NewsStore.from_file()


@mcp.tool()
def search(query: str, days: int = 30) -> str:
    """按关键词搜索近 N 天矿业新闻。

    Args:
        query: 关键词，空格分隔多个词（全部命中才返回）。
        days: 回溯天数，默认 30。

    Returns:
        JSON 字符串：命中的新闻列表，按日期倒序。
    """
    return json.dumps(store.search(query, days), ensure_ascii=False)


@mcp.tool()
def fetch_article(url: str) -> str:
    """按 URL 抓取新闻正文。

    Args:
        url: 新闻链接。

    Returns:
        JSON 字符串：文章完整字段；未命中返回 error 字段。
    """
    article = store.fetch(url)
    if article is None:
        return json.dumps({"error": "未找到该 URL 对应的文章"}, ensure_ascii=False)
    return json.dumps(article, ensure_ascii=False)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
