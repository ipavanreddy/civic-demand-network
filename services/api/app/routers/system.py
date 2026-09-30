"""System status (demo-mode badges), taxonomy and demo reset."""
from __future__ import annotations

from fastapi import APIRouter

from app import integrations
from app.config import settings
from app.pipeline import taxonomy, understanding
from app.store import get_store

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/system/status")
def system_status() -> dict:
    store = get_store()
    st = integrations.status()
    synthetic = sum(1 for r in store.requests.values() if r.is_synthetic)
    return {
        **st,
        "sample_data": True,
        "synthetic_requests": synthetic,
        "live_requests": len(store.requests) - synthetic,
        "data_notice": store.manifest["notice"],
        "dataset_version": store.manifest["dataset_version"],
        "datasets": store.manifest["datasets"],
        "gemini_model": settings.gemini_model,
    }


@router.get("/taxonomy")
def get_taxonomy() -> dict:
    return taxonomy.taxonomy()


@router.post("/system/reset")
def reset_demo() -> dict:
    """Drop runtime changes (new requests, decisions, weight changes) and reload the sample data."""
    store = get_store()
    store.reset(load_runtime=False)
    store.save()
    return {"ok": True, "requests": len(store.requests), "clusters": len(store.clusters)}


@router.get("/demo/scenarios")
def demo_scenarios() -> list[dict]:
    """PRD §43 scenarios (from ai/evaluation/fixtures) for one-click demo input in the citizen app."""
    return [{k: fx.get(k) for k in ("id", "scenario", "state", "district", "language", "channel", "text_original", "text_en")}
            for fx in understanding.fixtures() if fx.get("scenario") != "eval"]
