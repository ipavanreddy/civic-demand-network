"""Category taxonomy loaded from ai/taxonomy/categories.json."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.config import settings

TAXONOMY_PATH = Path(settings.ai_dir) / "taxonomy" / "categories.json"


@lru_cache
def taxonomy() -> dict:
    return json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))


@lru_cache
def categories() -> dict[str, dict]:
    return {c["id"]: c for c in taxonomy()["categories"]}


def label(category: str, language: str = "en") -> str:
    c = categories().get(category) or categories()["other"]
    return c["label"].get(language) or c["label"]["en"]


def prompt_listing() -> str:
    return "\n".join(
        f"- {c['id']}: {c['label']['en']} (e.g. {', '.join(c['sub_keywords']) or 'anything else'})"
        for c in taxonomy()["categories"]
    )
