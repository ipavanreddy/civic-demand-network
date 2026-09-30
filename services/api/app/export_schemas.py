"""Write JSON Schemas for AI outputs (ai/schemas/) and canonical entities (data/schemas/).

Run: cd services/api && uv run python -m app.export_schemas   (tests fail if these files are stale)
"""
from __future__ import annotations

import json
from pathlib import Path

from app.config import REPO_ROOT
from app.models import (
    AdminUnit,
    CitizenRequest,
    DemandCluster,
    EvidenceBrief,
    Indicator,
    Investment,
    RequestExtraction,
    ScoredCluster,
    Transcript,
    Translation,
)

AI = {"request_extraction.v1.json": RequestExtraction, "evidence_brief.v1.json": EvidenceBrief,
      "transcript.v1.json": Transcript, "translation.v1.json": Translation}
CANONICAL = {"request.json": CitizenRequest, "demand_cluster.json": DemandCluster, "indicator.json": Indicator,
             "investment.json": Investment, "admin_unit.json": AdminUnit, "recommendation.json": ScoredCluster}


def rendered() -> dict[Path, str]:
    out = {}
    for name, model in AI.items():
        out[REPO_ROOT / "ai" / "schemas" / name] = json.dumps(model.model_json_schema(), indent=2, ensure_ascii=False) + "\n"
    for name, model in CANONICAL.items():
        out[REPO_ROOT / "data" / "schemas" / name] = json.dumps(model.model_json_schema(), indent=2, ensure_ascii=False) + "\n"
    return out


if __name__ == "__main__":
    for path, text in rendered().items():
        path.write_text(text, encoding="utf-8")
        print("wrote", path.relative_to(REPO_ROOT))
