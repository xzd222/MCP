"""lme-price MCP server：矿产品价格行情。

以 stdio 方式运行：python -m servers.lme_price.server
"""
from __future__ import annotations

import json

from mcp.server.mcpserver import MCPServer

from servers.lme_price.store import PriceStore

mcp = MCPServer("lme-price")
store = PriceStore.from_file()


@mcp.tool()
def get_price(commodity: str, date: str) -> str:
    """查询某矿产品在指定日期的价格。

    Args:
        commodity: 品种，支持中文（如「锂」「铜」）或英文符号（如 lithium、copper）。
        date: 日期，格式 YYYY-MM-DD。

    Returns:
        JSON 字符串：价格对象；未命中返回 error 字段。
    """
    result = store.get_price(commodity, date)
    if result is None:
        return json.dumps({"error": f"未找到 {commodity} 在 {date} 的价格"}, ensure_ascii=False)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def get_trend(commodity: str, days: int = 30) -> str:
    """查询某矿产品近 N 天价格走势。

    Args:
        commodity: 品种，支持中文或英文符号。
        days: 回溯天数，默认 30。

    Returns:
        JSON 字符串：价格点列表，按日期升序。
    """
    return json.dumps(store.get_trend(commodity, days), ensure_ascii=False)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
