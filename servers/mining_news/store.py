"""mining-news 数据存取：从本地样例数据搜索与抓取正文。

数据源与工具逻辑分离，便于独立测试。
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).parent / "data" / "news.json"


@dataclass(frozen=True)
class Article:
    """一条新闻的完整字段。"""

    id: str
    title: str
    url: str
    source: str
    published_at: str  # ISO 日期 YYYY-MM-DD
    summary: str
    body: str


class NewsStore:
    """加载本地样例新闻，提供搜索与正文抓取。"""

    def __init__(self, articles: list[Article]) -> None:
        self._articles = {a.url: a for a in articles}

    @classmethod
    def from_file(cls, path: Path = DATA_FILE) -> NewsStore:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls([Article(**item) for item in raw])

    def search(self, query: str, days: int, today: date | None = None) -> list[dict[str, Any]]:
        """按关键词搜索近 N 天新闻；关键词空格分隔、全部命中才返回。"""
        today = today or date.today()
        cutoff = today - timedelta(days=days)
        keywords = [k for k in query.lower().split() if k]

        results: list[dict[str, Any]] = []
        for article in self._articles.values():
            if article.published_at < cutoff.isoformat():
                continue
            text = f"{article.title} {article.summary} {article.body}".lower()
            if not keywords or all(k in text for k in keywords):
                results.append(self._to_dict(article))

        results.sort(key=lambda item: item["published_at"], reverse=True)
        return results

    def fetch(self, url: str) -> dict[str, Any] | None:
        """按 URL 抓取正文；未命中返回 None。"""
        article = self._articles.get(url)
        return self._to_dict(article) if article else None

    @staticmethod
    def _to_dict(article: Article) -> dict[str, Any]:
        return {
            "id": article.id,
            "title": article.title,
            "url": article.url,
            "source": article.source,
            "published_at": article.published_at,
            "summary": article.summary,
            "body": article.body,
        }
