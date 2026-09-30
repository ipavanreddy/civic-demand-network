"""Google Maps Geocoding adapter (MAPS_API_KEY). Returns None when not configured or no result."""
from __future__ import annotations

import logging

import httpx

from app import runtime_health
from app.config import settings

log = logging.getLogger(__name__)


def configured() -> bool:
    return bool(settings.maps_api_key)


def geocode(address: str) -> tuple[float, float] | None:
    if not configured():
        return None
    try:
        res = httpx.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": address, "region": "in", "key": settings.maps_api_key},
            timeout=10.0,
        )
        res.raise_for_status()
        results = res.json().get("results", [])
        status = res.json().get("status")
        if status not in ("OK", "ZERO_RESULTS"):  # e.g. REQUEST_DENIED for a restricted key
            raise httpx.HTTPError(f"Geocoding status {status}: {res.json().get('error_message', '')}")
    except httpx.HTTPError as exc:  # external failure must not block intake
        log.warning("geocoding failed: %s", exc)
        runtime_health.record("geocoding", False, exc)
        return None
    runtime_health.record("geocoding", True)
    if not results:
        return None
    loc = results[0]["geometry"]["location"]
    return float(loc["lat"]), float(loc["lng"])
