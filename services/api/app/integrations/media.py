"""Audio/photo storage: Cloud Storage when GCS_BUCKET is set, local disk otherwise (demo mode)."""
from __future__ import annotations

import logging
from pathlib import Path

from app.config import REPO_ROOT, settings

log = logging.getLogger(__name__)
LOCAL_DIR = REPO_ROOT / "services" / "api" / ".data" / "media"


def save(name: str, data: bytes, content_type: str) -> str:
    if settings.gcs_bucket:
        try:
            from google.cloud import storage

            blob = storage.Client().bucket(settings.gcs_bucket).blob(f"requests/{name}")
            blob.upload_from_string(data, content_type=content_type)
            return f"gs://{settings.gcs_bucket}/requests/{name}"
        except Exception as exc:  # noqa: BLE001
            log.warning("GCS upload failed, storing locally: %s", exc)
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    path: Path = LOCAL_DIR / name
    path.write_bytes(data)
    try:
        return f"local://{path.relative_to(REPO_ROOT)}"
    except ValueError:
        return f"local://{path}"
