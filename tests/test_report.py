"""日报渲染测试。"""
from __future__ import annotations

import json
from typing import Any

from agent.report import build_report


def _news() -> list[dict[str, Any]]:
    return [
        {
            "title": "Pilbara 产量创新高",
            "source": "mining.com",
            "published_at": "2026-09-17",
            "summary": "产量增长",
            "url": "https://example.com/a",
        }
    ]


def _resources() -> list[dict[str, Any]]:
    return [
        {"category": "Indicated", "ore_tonnes_mt": 142.5, "grade": 1.25,
         "grade_unit": "% Li2O", "metal": 4.45, "metal_unit": "Mt LCE"},
        {"category": "Inferred", "ore_tonnes_mt": 78.3, "grade": 1.12,
         "grade_unit": "% Li2O", "metal": 2.2, "metal_unit": "Mt LCE"},
    ]


def _trend() -> list[dict[str, Any]]:
    return [
        {"date": "2026-09-16", "price": 100, "unit": "USD/t"},
        {"date": "2026-09-17", "price": 110, "unit": "USD/t"},
    ]


def _collected(news=None, resources=None, trend=None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if news:
        out.append({"tool": "search", "args": {}, "result": json.dumps(news, ensure_ascii=False)})
    if resources:
        out.append({"tool": "extract_resources", "args": {},
                    "result": json.dumps(resources, ensure_ascii=False)})
    if trend:
        out.append(
            {"tool": "get_trend", "args": {}, "result": json.dumps(trend, ensure_ascii=False)}
        )
    return out


def test_report_has_all_sections() -> None:
    report = build_report("Pilbara 锂矿", _collected(_news(), _resources(), _trend()))
    for section in ("## 新闻摘要", "## 储量数据", "## 价格走势", "## 风险提示", "## 引用来源"):
        assert section in report


def test_report_handles_empty() -> None:
    report = build_report("某话题", [])
    assert "# 矿权日报" in report
    assert "暂无" in report


def test_report_computes_risk() -> None:
    report = build_report("锂", _collected(trend=_trend()))
    assert "上涨" in report


def test_report_skips_error_entries() -> None:
    collected = [{"tool": "get_price", "args": {}, "result": json.dumps({"error": "未找到"})}]
    report = build_report("锂", collected)
    assert "暂无走势数据" in report
