"""lme-price 数据存取：从本地样例数据查询矿产品价格与走势。"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).parent / "data" / "prices.json"


@dataclass(frozen=True)
class PricePoint:
    """单个日期的价格点。"""

    date: str  # ISO 日期 YYYY-MM-DD
    price: float


@dataclass(frozen=True)
class Commodity:
    """一种矿产品的价格序列。"""

    commodity: str  # 英文符号
    name: str  # 中文名
    unit: str
    series: tuple[PricePoint, ...]


class PriceStore:
    """加载本地样例价格，支持按品种/日期查询与走势。"""

    def __init__(self, commodities: list[Commodity]) -> None:
        self._index: dict[str, Commodity] = {}
        for c in commodities:
            self._index[c.commodity.lower()] = c
            self._index[c.name.lower()] = c

    @classmethod
    def from_file(cls, path: Path = DATA_FILE) -> PriceStore:
        raw = json.loads(path.read_text(encoding="utf-8"))
        commodities = [
            Commodity(
                commodity=item["commodity"],
                name=item["name"],
                unit=item["unit"],
                series=tuple(PricePoint(**p) for p in item["series"]),
            )
            for item in raw
        ]
        return cls(commodities)

    def _resolve(self, key: str) -> Commodity | None:
        return self._index.get(key.strip().lower())

    def get_price(self, commodity: str, on: str) -> dict[str, Any] | None:
        """查询某品种在指定日期的价格；未命中返回 None。"""
        c = self._resolve(commodity)
        if c is None:
            return None
        for p in c.series:
            if p.date == on:
                return {"commodity": c.name, "date": p.date, "price": p.price, "unit": c.unit}
        return None

    def get_trend(self, commodity: str, days: int, today: date | None = None) -> list[dict[str, Any]]:
        """查询某品种近 N 天的价格走势（按日期升序）；未命中返回空列表。"""
        c = self._resolve(commodity)
        if c is None:
            return []
        today = today or date.today()
        cutoff = today - timedelta(days=days)
        points = [p for p in c.series if p.date >= cutoff.isoformat()]
        points.sort(key=lambda p: p.date)
        return [
            {"commodity": c.name, "date": p.date, "price": p.price, "unit": c.unit}
            for p in points
        ]
