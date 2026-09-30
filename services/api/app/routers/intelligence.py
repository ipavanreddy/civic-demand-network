"""Clusters, hotspots and analytics (PRD §37 "Clusters & Intelligence", §17)."""
from __future__ import annotations

from collections import Counter

import h3
from fastapi import APIRouter, HTTPException

from app.pipeline import fusion, ranking, taxonomy
from app.store import Store, get_store

router = APIRouter(prefix="/api", tags=["intelligence"])


def _in_scope(store: Store, r, state, district, category) -> bool:
    return ((not state or r.state == state) and (not district or r.lgd_district == district)
            and (not category or r.category == category) and r.cluster_id is not None)


@router.get("/clusters")
def list_clusters(state: str | None = None, district: str | None = None, category: str | None = None) -> list[dict]:
    store = get_store()
    scored, contexts = ranking.rank(store, store.weights, state, district, category)
    return [ranking.summary_row(store, s, contexts[s.cluster_id]) for s in scored]


@router.get("/clusters/{cluster_id}")
def get_cluster(cluster_id: str) -> dict:
    store = get_store()
    c = store.clusters.get(cluster_id)
    if not c:
        raise HTTPException(404, "cluster not found")
    ctx = fusion.cluster_context(c, store)
    reqs = sorted(store.cluster_requests(cluster_id), key=lambda r: r.created_at, reverse=True)
    return {
        **c.model_dump(mode="json"),
        "category_label": taxonomy.label(c.category),
        "places": [u.model_dump() for u in ctx["units"]],
        "population": ctx["population"],
        "recent_requests": [
            {k: r.model_dump(mode="json")[k] for k in ("request_id", "language", "text_original", "text_en", "channel",
                                                       "created_at", "is_synthetic", "lgd_unit")}
            for r in reqs[:10]
        ],
        "languages": Counter(r.language for r in reqs),
        "channels": Counter(r.channel for r in reqs),
    }


@router.get("/hotspots")
def hotspots(state: str | None = None, district: str | None = None, category: str | None = None) -> dict:
    store = get_store()
    cells: dict[str, dict] = {}
    for r in store.requests.values():
        if not r.h3_cell or not _in_scope(store, r, state, district, category):
            continue
        cell = cells.setdefault(r.h3_cell, {"citizens": set(), "categories": Counter(), "clusters": set(), "count": 0})
        cell["count"] += 1
        cell["citizens"].add(r.citizen_id)
        cell["categories"][r.category] += 1
        cell["clusters"].add(r.cluster_id)
    scored, _ = ranking.rank(store, store.weights, state, district, category)
    score_by_cluster = {s.cluster_id: s.priority_score for s in scored}
    out = []
    for cell_id, v in cells.items():
        lat, lng = h3.cell_to_latlng(cell_id)
        top = v["categories"].most_common(1)[0][0]
        out.append({
            "h3_cell": cell_id, "lat": lat, "lng": lng,
            "boundary": [list(p) for p in h3.cell_to_boundary(cell_id)],
            "request_count": v["count"], "unique_citizens": len(v["citizens"]),
            "top_category": top, "top_category_label": taxonomy.label(top),
            "cluster_ids": sorted(v["clusters"]),
            "max_priority_score": max((score_by_cluster.get(c, 0) for c in v["clusters"]), default=0),
        })
    out.sort(key=lambda x: -x["request_count"])
    return {"resolution": 7, "cells": out, "scope": ranking.scope_label(store, state, district, category)}


def analytics(store: Store, state: str | None = None, district: str | None = None) -> dict:
    reqs = [r for r in store.requests.values() if _in_scope(store, r, state, district, None)]
    clusters = store.filter_clusters(state, district)
    districts: dict[str, dict] = {}
    for r in reqs:
        u = store.units.get(r.lgd_unit or "")
        d = districts.setdefault(r.lgd_district or "?", {
            "code": r.lgd_district, "name": u.district_name if u else r.lgd_district, "state": r.state, "requests": 0})
        d["requests"] += 1
    live = [r for r in store.requests.values() if not r.is_synthetic]
    last = max((r.created_at for r in reqs), default=None)
    return {
        "scope": ranking.scope_label(store, state, district, None),
        "requests": len(reqs),
        "unique_citizens": len({r.citizen_id for r in reqs}),
        "clusters": len(clusters),
        "top_categories": [{"category": c, "label": taxonomy.label(c), "requests": n}
                           for c, n in Counter(r.category for r in reqs).most_common()],
        "by_district": sorted(districts.values(), key=lambda d: -d["requests"]),
        "languages": Counter(r.language for r in reqs),
        "channels": Counter(r.channel for r in reqs),
        "synthetic_share": round(sum(r.is_synthetic for r in reqs) / len(reqs), 3) if reqs else 0,
        "freshness": {
            "citizen_requests_last_received": last.isoformat() if last else None,
            "last_live_request": max((r.created_at for r in live), default=None),
            "scoring_as_of": fusion.as_of(store).isoformat(),
            "indicator_years": sorted({i.year for rows in store.indicators.values() for i in rows}),
        },
        "investments_in_scope": sum(1 for i in store.investments if any(
            (u := store.units.get(code)) and (not state or u.state == state) and (not district or u.district_code == district)
            for code in i.lgd_codes)),
        "weights": store.weights.model_dump(),
    }


@router.get("/analytics")
def get_analytics(state: str | None = None, district: str | None = None) -> dict:
    return analytics(get_store(), state, district)
