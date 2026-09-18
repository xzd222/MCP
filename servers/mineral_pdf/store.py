"""mineral-pdf 数据存取：从本地样例数据抽取 NI 43-101 储量。"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).parent / "data" / "resources.json"


@dataclass(frozen=True)
class Resource:
    """一条 NI 43-101 储量记录。"""

    id: str
    project: str
    company: str
    commodity: str
    category: str  # Indicated | Inferred
    source_url: str
    ore_tonnes_mt: float
    grade: float
    grade_unit: str
    metal: float
    metal_unit: str


class ResourceStore:
    """加载本地样例储量数据，按 PDF URL 抽取资源量。"""

    def __init__(self, resources: list[Resource]) -> None:
        self._resources = resources

    @classmethod
    def from_file(cls, path: Path = DATA_FILE) -> ResourceStore:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls([Resource(**item) for item in raw])

    def extract(self, pdf_url: str) -> list[dict[str, Any]]:
        """按 PDF URL 抽取 Indicated/Inferred 储量行；未命中返回空列表。"""
        return [self._to_dict(r) for r in self._resources if r.source_url == pdf_url]

    @staticmethod
    def _to_dict(r: Resource) -> dict[str, Any]:
        return {
            "id": r.id,
            "project": r.project,
            "company": r.company,
            "commodity": r.commodity,
            "category": r.category,
            "ore_tonnes_mt": r.ore_tonnes_mt,
            "grade": r.grade,
            "grade_unit": r.grade_unit,
            "metal": r.metal,
            "metal_unit": r.metal_unit,
        }
