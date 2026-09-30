"""Demand clustering (PRD §13): same category AND same/neighbouring location AND semantic similarity.

Real mode: Gemini embeddings (settings.gemini_embedding_model) for the request vs. each candidate
cluster's summary. Demo mode: bag-of-words cosine. The location/category gate is identical.
"""
from __future__ import annotations

import logging
import math
import re
from collections import Counter

from app.ai import gemini
from app.models import CitizenRequest, DemandCluster
from app.pipeline.location import haversine_km
from app.store import Store

log = logging.getLogger(__name__)
NEIGHBOUR_KM = 10.0
THRESHOLD = {"embedding": 0.8, "bow": 0.45}
STOP = frozenset({
    "a", "an", "the", "of", "in", "on", "at", "to", "for", "from", "and", "or", "is", "are", "was", "were",
    "be", "been", "it", "its", "this", "that", "we", "our", "us", "i", "my", "me", "you", "your", "they",
    "them", "there", "here", "no", "not", "only", "every", "very", "please", "sir", "have", "has", "had",
    "do", "does", "can", "cannot", "with", "by", "as", "into", "about", "over", "near",
})

_embedding_cache: dict[str, list[float]] = {}


def tokens(text: str) -> Counter:
    return Counter(t for t in re.findall(r"[a-z]+", text.lower()) if t not in STOP and len(t) > 2)


def cosine(a: Counter | list[float], b: Counter | list[float]) -> float:
    if isinstance(a, Counter) and isinstance(b, Counter):
        dot = sum(a[k] * b[k] for k in a)
        na, nb = math.sqrt(sum(v * v for v in a.values())), math.sqrt(sum(v * v for v in b.values()))
    else:
        dot = sum(x * y for x, y in zip(a, b))  # type: ignore[arg-type]
        na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))  # type: ignore[union-attr]
    return dot / (na * nb) if na and nb else 0.0


def _profile_text(store: Store, c: DemandCluster) -> str:
    texts = list(dict.fromkeys(r.summary_en for r in store.cluster_requests(c.cluster_id)))[:20]
    return " ".join([c.summary, *texts])


def _similarities(req: CitizenRequest, store: Store, candidates: list[DemandCluster]) -> tuple[dict[str, float], str]:
    if gemini.is_configured() and candidates:
        try:
            missing = [c for c in candidates if c.cluster_id not in _embedding_cache]
            if missing:
                vecs = gemini.embed_texts([c.summary for c in missing])
                _embedding_cache.update({c.cluster_id: v for c, v in zip(missing, vecs)})
            q = gemini.embed_texts([req.summary_en])[0]
            return {c.cluster_id: cosine(q, _embedding_cache[c.cluster_id]) for c in candidates}, "embedding"
        except Exception as exc:  # noqa: BLE001
            log.warning("embedding similarity failed, using bag-of-words: %s", exc)
    q = tokens(f"{req.summary_en} {req.text_en}")
    return {c.cluster_id: cosine(q, tokens(_profile_text(store, c))) for c in candidates}, "bow"


def warm_embeddings(store: Store) -> None:
    """Embed every cluster summary once (called in the background at startup) so the first
    citizen confirmation does not pay the embedding cold start."""
    if not gemini.is_configured():
        return
    try:
        missing = [c for c in store.clusters.values() if c.cluster_id not in _embedding_cache]
        if missing:
            vecs = gemini.embed_texts([c.summary for c in missing])
            _embedding_cache.update({c.cluster_id: v for c, v in zip(missing, vecs)})
    except Exception as exc:  # noqa: BLE001
        log.warning("embedding warm-up failed (will retry on demand): %s", exc)


def assign(req: CitizenRequest, store: Store) -> dict:
    """Join the best matching cluster or start a new one. Returns an explanation dict."""
    unit = store.units.get(req.lgd_unit or "")
    candidates = []
    for c in store.clusters.values():
        if c.state != req.state or c.category != req.category:
            continue
        same_unit = req.lgd_unit in c.lgd_units
        same_block = c.lgd_block == req.lgd_block
        near = unit is not None and any(
            haversine_km(unit.lat, unit.lng, store.units[u].lat, store.units[u].lng) <= NEIGHBOUR_KM
            for u in c.lgd_units if u in store.units)
        if same_unit or same_block or near:
            candidates.append((c, same_unit, same_block, near))
    sims, method = _similarities(req, store, [c for c, *_ in candidates])
    best, best_score = None, -1.0
    for c, same_unit, same_block, near in candidates:
        score = sims[c.cluster_id] + (0.35 if same_unit else 0) + (0.15 if same_block else 0) + (0.1 if near else 0)
        if score > best_score:
            best, best_score = c, score
    if best is not None and best_score >= THRESHOLD[method]:
        store.assign(req, best.cluster_id)
        return {"cluster_id": best.cluster_id, "joined_existing": True, "match_score": round(best_score, 3),
                "similarity_method": method, "candidates_considered": len(candidates)}
    cid = store.new_cluster_id(req.state or "XX")
    store.clusters[cid] = DemandCluster(
        cluster_id=cid, state=req.state or "XX", category=req.category, sub_category=req.sub_category,
        lgd_district=req.lgd_district or "", lgd_block=req.lgd_block or "", lgd_units=[req.lgd_unit] if req.lgd_unit else [],
        summary=req.summary_en, status="Clustered",
    )
    store.members[cid] = []
    store.assign(req, cid)
    return {"cluster_id": cid, "joined_existing": False, "match_score": round(max(best_score, 0), 3),
            "similarity_method": method, "candidates_considered": len(candidates)}
