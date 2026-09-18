"""mineral-pdf MCP server 测试。"""
from __future__ import annotations

import json

import pytest

from servers.mineral_pdf.server import extract_resources
from servers.mineral_pdf.store import ResourceStore

PILBARA_URL = "https://example.com/pdfs/pilbara-43-101.pdf"


@pytest.fixture()
def store() -> ResourceStore:
    return ResourceStore.from_file()


def test_extract_returns_indicated_and_inferred(store: ResourceStore) -> None:
    categories = {r["category"] for r in store.extract(PILBARA_URL)}
    assert categories == {"Indicated", "Inferred"}


def test_extract_has_required_fields(store: ResourceStore) -> None:
    row = store.extract(PILBARA_URL)[0]
    for key in ("ore_tonnes_mt", "grade", "grade_unit", "metal", "metal_unit"):
        assert key in row


def test_extract_missing_url_returns_empty(store: ResourceStore) -> None:
    assert store.extract("https://example.com/pdfs/unknown.pdf") == []


def test_tool_returns_json() -> None:
    rows = json.loads(extract_resources(PILBARA_URL))
    assert isinstance(rows, list)
    assert len(rows) >= 2
