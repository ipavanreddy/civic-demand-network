"""Tests always run in demo mode (no external calls), whatever keys are in .env."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.store import Store, set_store

for field in ("gemini_api_key", "google_api_key", "maps_api_key", "telegram_bot_token", "gcs_bucket", "google_cloud_project"):
    setattr(settings, field, "")
settings.google_genai_use_vertexai = False
settings.use_bigquery = False
settings.local_state_path = ""


@pytest.fixture
def store() -> Store:
    s = Store(Path(settings.data_dir), "")
    set_store(s)
    return s


@pytest.fixture
def client(store: Store) -> TestClient:
    from app.main import app

    return TestClient(app)


@pytest.fixture(autouse=True)
def _media_to_tmp(tmp_path, monkeypatch):
    from app.integrations import media

    monkeypatch.setattr(media, "LOCAL_DIR", tmp_path / "media")
