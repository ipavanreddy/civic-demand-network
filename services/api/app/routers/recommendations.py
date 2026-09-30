"""Ranked recommendations, policy-lens weights, evidence briefs and human decisions (PRD §15-17, §37)."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.integrations import bigquery_sink
from app.models import Weights
from app.pipeline import brief as brief_mod
from app.pipeline import fusion, ranking
from app.store import Store, get_store

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


class ScoreBody(BaseModel):
    weights: Weights
    state: str | None = None
    district: str | None = None
    category: str | None = None
    officer: str = "planning-officer-demo"
    reason: str | None = None


class DecisionBody(BaseModel):
    decision: Literal["approve_for_field_verification", "defer", "reject"]
    officer: str = Field("planning-officer-demo", min_length=1)
    note: str | None = None


class BriefBody(BaseModel):
    state: str | None = None
    district: str | None = None
    category: str | None = None


def _ranked(store: Store, weights: Weights, state, district, category) -> dict:
    scored, contexts = ranking.rank(store, weights, state, district, category)
    return {
        "scope": ranking.scope_label(store, state, district, category),
        "weights": weights.model_dump(),
        "default_weights": Weights().model_dump(),
        "formula": "100 × (wD·Demand + wG·Gap + wV·Vulnerability + wT·Trend − wI·Investment) / (wD+wG+wV+wT)",
        "as_of": fusion.as_of(store).isoformat(),
        "items": [ranking.summary_row(store, s, contexts[s.cluster_id]) for s in scored],
    }


@router.get("")
def list_recommendations(state: str | None = None, district: str | None = None, category: str | None = None) -> dict:
    store = get_store()
    return _ranked(store, store.weights, state, district, category)


@router.post("/score")
def rescore(body: ScoreBody) -> dict:
    """Re-rank with new policy weights. Every change of the active weights is recorded (PRD §15)."""
    store = get_store()
    if body.weights != store.weights:
        entry = {
            "at": datetime.now(UTC).isoformat(), "officer": body.officer, "reason": body.reason,
            "from": store.weights.model_dump(), "to": body.weights.model_dump(),
            "scope": ranking.scope_label(store, body.state, body.district, body.category)["label"],
        }
        store.weight_log.append(entry)
        store.weights = body.weights
        bigquery_sink.insert("weight_changes", [entry])
        store.save()
    return _ranked(store, store.weights, body.state, body.district, body.category)


@router.get("/weights-log")
def weights_log() -> list[dict]:
    return list(reversed(get_store().weight_log))


def _find(store: Store, recommendation_id: str, state, district, category):
    cluster_id = recommendation_id.removeprefix("REC-")
    if cluster_id not in store.clusters:
        raise HTTPException(404, "recommendation not found")
    scored, contexts = ranking.rank(store, store.weights, state, district, category)
    s = next((x for x in scored if x.cluster_id == cluster_id), None)
    if s is None:  # outside the requested scope: rank within its own state
        scored, contexts = ranking.rank(store, store.weights, store.clusters[cluster_id].state)
        s = next(x for x in scored if x.cluster_id == cluster_id)
        state, district, category = store.clusters[cluster_id].state, None, None
    return s, contexts[cluster_id], len(scored), ranking.scope_label(store, state, district, category)


@router.get("/{recommendation_id}")
def get_recommendation(recommendation_id: str, state: str | None = None, district: str | None = None,
                       category: str | None = None) -> dict:
    store = get_store()
    s, ctx, total, scope = _find(store, recommendation_id, state, district, category)
    reqs = sorted(store.cluster_requests(s.cluster_id), key=lambda r: r.created_at, reverse=True)
    quotes, seen = [], set()
    for r in reqs:
        if r.text_en not in seen:
            seen.add(r.text_en)
            quotes.append({"language": r.language, "original": r.text_original, "translated_en": r.text_en,
                           "is_synthetic": r.is_synthetic})
    return {
        **ranking.summary_row(store, s, ctx),
        "scope": scope,
        "total_in_scope": total,
        "places": [u.model_dump() for u in ctx["units"]],
        "indicators": ctx["indicator_rows"],
        "investments": ctx["investments"],
        "quotes": quotes[:5],
        "first_seen": store.clusters[s.cluster_id].first_seen,
        "last_seen": store.clusters[s.cluster_id].last_seen,
        "recent_requests_30d": ctx["recent_requests"],
        "brief": store.briefs.get(s.recommendation_id),
        "decision": store.decisions.get(s.recommendation_id),
    }


@router.post("/{recommendation_id}/brief")
def generate_brief(recommendation_id: str, body: BriefBody | None = None) -> dict:
    store = get_store()
    body = body or BriefBody()
    s, ctx, total, scope = _find(store, recommendation_id, body.state, body.district, body.category)
    data = brief_mod.build_input(s, ctx, store, scope, total)
    brief, prov = brief_mod.generate(data)
    grounding = brief_mod.check_grounding(brief, data)
    record = {
        "recommendation_id": s.recommendation_id,
        "cluster_id": s.cluster_id,
        "priority_score": s.priority_score,
        "score_breakdown": [f.model_dump() for f in s.breakdown],
        "weights_used": s.weights_used.model_dump(),
        "evidence_brief": brief.model_dump(),
        "grounding": grounding,
        "generated_at": prov.generated_at.isoformat(),
        "language": "en",
        "model_name": prov.model_name,
        "model_version": prov.model_version,
        "prompt_version": prov.prompt_version,
        "mode": prov.mode,
        "note": prov.note,
        "scope": scope,
        "input": data,
    }
    store.briefs[s.recommendation_id] = record
    bigquery_sink.insert("recommendations", [{k: v for k, v in record.items() if k != "input"}])
    store.save()
    return record


@router.post("/{recommendation_id}/decision")
def decide(recommendation_id: str, body: DecisionBody) -> dict:
    """Human-in-the-loop decision. The platform never approves anything on its own (PRD §35)."""
    store = get_store()
    cluster_id = recommendation_id.removeprefix("REC-")
    if cluster_id not in store.clusters:
        raise HTTPException(404, "recommendation not found")
    record = {"recommendation_id": recommendation_id, **body.model_dump(),
              "decided_at": datetime.now(UTC).isoformat()}
    store.decisions[recommendation_id] = record
    cluster = store.clusters[cluster_id]
    cluster.status = {"approve_for_field_verification": "Recommended", "defer": "Under Review",
                      "reject": "Under Review"}[body.decision]
    bigquery_sink.insert("decisions", [record])
    store.save()
    return {**record, "cluster_status": cluster.status}
