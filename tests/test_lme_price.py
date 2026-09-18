"""lme-price MCP server 测试。"""
from __future__ import annotations

import json
from datetime import date

import pytest

from servers.lme_price.server import get_price, get_trend
from servers.lme_price.store import PriceStore

TODAY = date(2026, 9, 18)


@pytest.fixture()
def store() -> PriceStore:
    return PriceStore.from_file()


def test_get_price_by_chinese_name(store: PriceStore) -> None:
    result = store.get_price("锂", "2026-09-17")
    assert result is not None
    assert result["price"] > 0


def test_get_price_by_symbol(store: PriceStore) -> None:
    result = store.get_price("lithium", "2026-09-17")
    assert result is not None
    assert result["unit"] == "USD/t"


def test_get_price_missing_date_returns_none(store: PriceStore) -> None:
    assert store.get_price("锂", "1999-01-01") is None


def test_get_trend_respects_days(store: PriceStore) -> None:
    trend = store.get_trend("铜", days=7, today=TODAY)
    assert len(trend) == 7


def test_get_trend_sorted_ascending(store: PriceStore) -> None:
    trend = store.get_trend("lithium", days=30, today=TODAY)
    dates = [p["date"] for p in trend]
    assert dates == sorted(dates)


def test_tool_functions_return_json() -> None:
    assert isinstance(json.loads(get_price("锂", "2026-09-17")), dict)
    assert isinstance(json.loads(get_trend("锂", days=7)), list)
