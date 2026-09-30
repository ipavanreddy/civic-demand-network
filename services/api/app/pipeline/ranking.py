"""Scope -> fused contexts -> deterministic ranking. Shared by the recommendations/cluster routers."""
from __future__ import annotations

from app.models import ScoredCluster, Weights
from app.pipeline import fusion, scoring, taxonomy
from app.store import Store


def scope_label(store: Store, state: str | None, district: str | None, category: str | None) -> dict:
    label = "All India"
    if state and state in store.states:
        label = store.states[state].config["name"]
    if district:
        name = next((u.district_name for u in store.units.values() if u.district_code == district), district)
        label = f"{name}, {label}" if state else name
    if category:
        label += f" · {taxonomy.label(category)}"
    return {"state": state, "district": district, "category": category, "label": label}


def rank(store: Store, weights: Weights, state: str | None = None, district: str | None = None,
         category: str | None = None) -> tuple[list[ScoredCluster], dict[str, dict]]:
    clusters = store.filter_clusters(state, district, category)
    now = fusion.as_of(store)
    contexts = {c.cluster_id: fusion.cluster_context(c, store, now) for c in clusters}
    scored = scoring.score_contexts(list(contexts.values()), weights)
    if weights != Weights():
        default_rank = {s.cluster_id: s.rank for s in scoring.score_contexts(list(contexts.values()), Weights())}
    else:
        default_rank = {s.cluster_id: s.rank for s in scored}
    for s in scored:
        s.default_rank = default_rank[s.cluster_id]
    return scored, contexts


def summary_row(store: Store, s: ScoredCluster, ctx: dict) -> dict:
    c = ctx["cluster"]
    units = ctx["units"]
    return {
        **s.model_dump(mode="json"),
        "title": f"{taxonomy.label(c.category)} – {', '.join(u.name for u in units)}",
        "category": c.category,
        "category_label": taxonomy.label(c.category),
        "sub_category": c.sub_category,
        "summary": c.summary,
        "state": c.state,
        "state_name": store.states[c.state].config["name"] if c.state in store.states else c.state,
        "district": units[0].district_name if units else c.lgd_district,
        "block": units[0].block_name if units else c.lgd_block,
        "places": [u.name for u in units],
        "lat": sum(u.lat for u in units) / len(units) if units else None,
        "lng": sum(u.lng for u in units) / len(units) if units else None,
        "request_count": c.request_count,
        "unique_citizens": c.unique_citizens,
        "population": ctx["population"],
        "status": c.status,
        "is_synthetic": c.is_synthetic,
        "decision": store.decisions.get(s.recommendation_id),
        "has_brief": s.recommendation_id in store.briefs,
    }
