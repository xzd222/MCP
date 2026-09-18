"""日报 Markdown 渲染（纯函数，便于测试）。"""
from __future__ import annotations

import json
from typing import Any


def build_report(question: str, collected: list[dict[str, Any]]) -> str:
    """根据收集到的工具结果渲染 Markdown 日报。"""
    news = _collect(collected, "search")
    resources = _collect(collected, "extract_resources")
    trend = _collect(collected, "get_trend")
    price = _collect(collected, "get_price")

    parts: list[str] = [f"# 矿权日报：{question}", ""]
    parts += _news_section(news)
    parts += _resource_section(resources)
    parts += _trend_section(trend, price)
    parts += _risk_section(trend)
    parts += _source_section(news)
    return "\n".join(parts)


def _collect(collected: list[dict[str, Any]], tool: str) -> list[dict[str, Any]]:
    """汇总指定工具的结果（解析 JSON，跳过 error 条目）。"""
    out: list[dict[str, Any]] = []
    for item in collected:
        if item.get("tool") != tool:
            continue
        try:
            data = json.loads(item["result"])
        except (json.JSONDecodeError, TypeError, KeyError):
            continue
        if isinstance(data, list):
            out.extend(d for d in data if isinstance(d, dict))
        elif isinstance(data, dict) and "error" not in data:
            out.append(data)
    return out


def _news_section(news: list[dict[str, Any]]) -> list[str]:
    lines = ["## 新闻摘要", ""]
    if not news:
        lines.append("- 暂无相关新闻。")
    for article in news[:5]:
        title = article.get("title", "无标题")
        source = article.get("source", "")
        date = article.get("published_at", "")
        summary = article.get("summary", "")
        lines.append(f"- **{title}**（{source} · {date}）：{summary}")
    lines.append("")
    return lines


def _resource_section(resources: list[dict[str, Any]]) -> list[str]:
    lines = ["## 储量数据", ""]
    if not resources:
        lines.append("- 暂无储量数据。")
        lines.append("")
        return lines
    lines.append("| 类别 | 矿石量(Mt) | 品位 | 金属量 |")
    lines.append("|---|---|---|---|")
    for r in resources:
        lines.append(
            f"| {r.get('category', '')} | {r.get('ore_tonnes_mt', '')} | "
            f"{r.get('grade', '')} {r.get('grade_unit', '')} | "
            f"{r.get('metal', '')} {r.get('metal_unit', '')} |"
        )
    lines.append("")
    return lines


def _trend_section(trend: list[dict[str, Any]], price: list[dict[str, Any]]) -> list[str]:
    lines = ["## 价格走势", ""]
    if price:
        point = price[0]
        lines.append(
            f"- 最新价格（{point.get('date', '')}）："
            f"{point.get('price', '')} {point.get('unit', '')}"
        )
        lines.append("")
    if not trend:
        lines.append("- 暂无走势数据。")
        lines.append("")
        return lines
    lines.append("| 日期 | 价格 |")
    lines.append("|---|---|")
    for point in trend:
        lines.append(
            f"| {point.get('date', '')} | "
            f"{point.get('price', '')} {point.get('unit', '')} |"
        )
    lines.append("")
    return lines


def _risk_section(trend: list[dict[str, Any]]) -> list[str]:
    lines = ["## 风险提示", ""]
    if len(trend) >= 2:
        first = float(trend[0].get("price", 0))
        last = float(trend[-1].get("price", 0))
        pct = (last - first) / first * 100 if first else 0.0
        direction = "上涨" if pct >= 0 else "下跌"
        lines.append(f"- 价格近 {len(trend)} 天{direction} {abs(pct):.1f}%，需关注波动风险。")
    else:
        lines.append("- 暂无足够价格数据用于风险评估。")
    lines.append("- 以上数据来自样例数据源，仅供演示，不构成投资建议。")
    lines.append("")
    return lines


def _source_section(news: list[dict[str, Any]]) -> list[str]:
    lines = ["## 引用来源", ""]
    seen: set[str] = set()
    for article in news:
        url = article.get("url", "")
        if url and url not in seen:
            seen.add(url)
            lines.append(f"- [{article.get('title', '链接')}]({url})")
    if not seen:
        lines.append("- 无")
    lines.append("")
    return lines
