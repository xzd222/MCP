"""mining-news MCP server 测试。"""
from __future__ import annotations

import json
from datetime import date

import pytest

from servers.mining_news.server import fetch_article, search
from servers.mining_news.store import NewsStore

TODAY = date(2026, 9, 18)


@pytest.fixture()
def store() -> NewsStore:
    return NewsStore.from_file()


def test_search_matches_keyword(store: NewsStore) -> None:
    results = store.search("锂", days=30, today=TODAY)
    assert results, "应命中锂相关新闻"
    assert all("锂" in (r["title"] + r["summary"] + r["body"]) for r in results)


def test_search_respects_days_window(store: NewsStore) -> None:
    within = store.search("金", days=30, today=TODAY)
    recent = store.search("金", days=7, today=TODAY)
    assert within and not recent, "金矿新闻应只出现在较宽时间窗"


def test_search_multi_keyword_all_match(store: NewsStore) -> None:
    results = store.search("Pilbara 锂", days=30, today=TODAY)
    assert results
    assert all("pilbara" in r["title"].lower() for r in results)


def test_fetch_article_roundtrip(store: NewsStore) -> None:
    url = store.search("Pilbara", days=30, today=TODAY)[0]["url"]
    article = store.fetch(url)
    assert article is not None
    assert article["url"] == url
    assert article["body"]


def test_fetch_missing_url_returns_none(store: NewsStore) -> None:
    assert store.fetch("https://example.com/nonexistent") is None


def test_tool_functions_return_json() -> None:
    assert isinstance(json.loads(search("锂", days=30)), list)
    assert isinstance(json.loads(fetch_article("https://example.com/news/pilbara-output")), dict)
