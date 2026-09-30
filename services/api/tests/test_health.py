from fastapi.testclient import TestClient

from app.main import app


def test_health():
    res = TestClient(app).get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_badge_reports_fallback_when_a_configured_integration_fails(client, monkeypatch):
    from app import runtime_health
    from app.config import settings

    runtime_health.reset()
    monkeypatch.setattr(settings, "maps_api_key", "test-key")
    assert client.get("/api/system/status").json()["integrations"]["geocoding"]["mode"] == "real"
    runtime_health.record("geocoding", False, "REQUEST_DENIED")
    geo = client.get("/api/system/status").json()["integrations"]["geocoding"]
    assert geo["mode"] == "fallback" and "REQUEST_DENIED" in geo["detail"]
    runtime_health.record("geocoding", True)
    assert client.get("/api/system/status").json()["integrations"]["geocoding"]["mode"] == "real"
    runtime_health.reset()
