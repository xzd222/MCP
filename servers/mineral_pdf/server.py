"""mineral-pdf MCP server：NI 43-101 储量抽取。

以 stdio 方式运行：python -m servers.mineral_pdf.server
"""
from __future__ import annotations

import json

from mcp.server.mcpserver import MCPServer

from servers.mineral_pdf.store import ResourceStore

mcp = MCPServer("mineral-pdf")
store = ResourceStore.from_file()


@mcp.tool()
def extract_resources(pdf_url: str) -> str:
    """从 NI 43-101 报告 PDF 抽取 Indicated/Inferred 储量。

    Args:
        pdf_url: 报告 PDF 的链接。

    Returns:
        JSON 字符串：储量行列表（矿石量 Mt、品位、金属量）；未命中返回空列表。
    """
    return json.dumps(store.extract(pdf_url), ensure_ascii=False)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
