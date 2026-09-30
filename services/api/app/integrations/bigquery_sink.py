"""BigQuery sink (USE_BIGQUERY=true + GOOGLE_CLOUD_PROJECT). Streams canonical rows to the tables
defined in `infrastructure/bigquery/schema.sql`. In demo mode this is a no-op and the in-memory
store + local JSON file are the source of truth. Failures are logged, never raised (PRD §39)."""
from __future__ import annotations

import json
import logging
from functools import lru_cache

from app import runtime_health
from app.config import settings

log = logging.getLogger(__name__)


# Columns typed JSON in infrastructure/bigquery/schema.sql. The streaming API expects these as
# JSON-encoded strings, not nested objects (nested objects are only accepted for RECORD columns).
JSON_COLUMNS = {
    "recommendations": {"score_breakdown", "weights_used", "evidence_brief", "grounding", "scope"},
    "weight_changes": {"from", "to"},
}


def configured() -> bool:
    return settings.use_bigquery and bool(settings.google_cloud_project)


@lru_cache
def _client():
    from google.cloud import bigquery

    return bigquery.Client(project=settings.google_cloud_project)


def insert(table: str, rows: list[dict]) -> bool:
    if not configured() or not rows:
        return False
    table_id = f"{settings.google_cloud_project}.{settings.bigquery_dataset}.{table}"
    try:
        # round-trip through JSON so datetimes/lists serialise the same way as the API responses
        payload = json.loads(json.dumps(rows, default=str))
        json_cols = JSON_COLUMNS.get(table, set())
        for row in payload:
            for col in json_cols & row.keys():
                if row[col] is not None:
                    row[col] = json.dumps(row[col], ensure_ascii=False)
        errors = _client().insert_rows_json(table_id, payload)
        if errors:
            log.warning("BigQuery insert errors for %s: %s", table_id, errors)
            runtime_health.record("bigquery", False, f"{table}: {errors}")
            return False
        runtime_health.record("bigquery", True)
        return True
    except Exception as exc:  # noqa: BLE001
        log.warning("BigQuery insert failed for %s: %s", table_id, exc)
        runtime_health.record("bigquery", False, exc)
        return False
