"""Priority Score (PRD §15): transparent, deterministic, weight-configurable.

  score = 100 * (wD*Demand + wG*Gap + wV*Vulnerability + wT*Trend - wI*InvestmentCoverage) / (wD+wG+wV+wT)

- Demand: recency-weighted unique citizens per 10k population (half-life 45 days), divided by the
  maximum in the selected geography (so the top cluster in scope = 1). Repeat submissions by the same
  citizen count once.
- Trend: share of the last-60-day requests that arrived in the last 30 days, divided by the maximum in scope.
- Gap, Vulnerability, Investment coverage: population-weighted 0-1 shares from the fused indicators.
  A missing gap indicator uses a neutral 0.5 and is flagged.
The result is clamped to 0-100. Gemini never changes this number.
"""
from __future__ import annotations

from app.models import FactorScore, ScoredCluster, Weights

LABELS = {
    "demand": "Demand intensity",
    "infra_gap": "Infrastructure gap",
    "vulnerability": "Vulnerability",
    "trend": "Demand trend",
    "investment": "Existing investment coverage",
}


def band(score: float) -> str:
    return "High" if score >= 70 else "Medium" if score >= 45 else "Low"


def score_contexts(contexts: list[dict], weights: Weights) -> list[ScoredCluster]:
    if not contexts:
        return []
    max_demand = max(c["demand_raw"] for c in contexts) or 1.0
    max_trend = max(c["trend_raw"] for c in contexts) or 1.0
    positive = weights.demand + weights.infra_gap + weights.vulnerability + weights.trend
    scored = []
    for ctx in contexts:
        cl = ctx["cluster"]
        d = ctx["demand_raw"] / max_demand
        t = ctx["trend_raw"] / max_trend
        g = ctx["gap"] if ctx["gap"] is not None else 0.5
        v = ctx["vulnerability"] if ctx["vulnerability"] is not None else 0.5
        i = ctx["coverage"]
        indicator_sources = sorted({r["source"] for r in ctx["indicator_rows"]})
        gap_sources = sorted({r["source"] for r in ctx["indicator_rows"] if r["indicator_name"] == ctx["gap_indicator"]})
        vp = ctx["vulnerability_parts"]
        factors = [
            ("demand", ctx["demand_raw"], d, weights.demand,
             f"{ctx['recency_weighted_citizens']:.1f} recency-weighted unique citizens per {ctx['population']:,} people "
             f"= {ctx['demand_raw']:.1f} per 10k; {d:.2f} of the highest in scope", ["Citizen requests"]),
            ("infra_gap", ctx["gap"], g, weights.infra_gap,
             (f"Gap from '{ctx['gap_indicator']}' (population-weighted) = {g:.2f}" if ctx["gap"] is not None
              else "No category gap indicator available: neutral 0.5 used (flagged as missing data)"), gap_sources),
            ("vulnerability", ctx["vulnerability"], v, weights.vulnerability,
             "Composite of " + ", ".join(
                 f"{k.replace('_', ' ')}={val:.2f}" if val is not None else f"{k.replace('_', ' ')}=missing"
                 for k, val in vp.items()), indicator_sources),
            ("trend", ctx["trend_raw"], t, weights.trend,
             f"{ctx['recent_requests']} requests in the last 30 days vs {ctx['prior_requests']} in the 30 days before; "
             f"{t:.2f} of the fastest-growing in scope", ["Citizen requests"]),
            ("investment", ctx["coverage"], i, weights.investment,
             f"{ctx['population_covered']:,} of {ctx['population']:,} people covered by sanctioned/ongoing/completed "
             f"projects = {i:.2f} (subtracted)", sorted({inv["source"] for inv in ctx["investments"]})),
        ]
        breakdown = []
        total = 0.0
        for key, raw, norm, w, why, src in factors:
            sign = -1 if key == "investment" else 1
            contribution = (100 * sign * w * norm / positive) if positive else 0.0
            total += contribution
            breakdown.append(FactorScore(
                factor=key, label=LABELS[key], raw=None if raw is None else round(float(raw), 4),
                normalised=round(norm, 4), weight=w, contribution=round(contribution, 2), explanation=why, sources=src,
            ))
        score = round(max(0.0, min(100.0, total)), 1)
        scored.append(ScoredCluster(
            recommendation_id=f"REC-{cl.cluster_id}", cluster_id=cl.cluster_id, rank=0, priority_score=score,
            band=band(score), breakdown=breakdown, weights_used=weights,  # type: ignore[arg-type]
        ))
    scored.sort(key=lambda s: (-s.priority_score, s.cluster_id))
    for n, s in enumerate(scored, 1):
        s.rank = n
    return scored
