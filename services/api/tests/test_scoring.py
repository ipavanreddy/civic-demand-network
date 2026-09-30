from datetime import timedelta

import pytest

from app.models import CitizenRequest, DemandCluster, Weights
from app.pipeline import fusion, ranking, scoring


def ctx(cid: str, demand=1.0, gap=1.0, vuln=0.5, trend=0.5, coverage=0.0) -> dict:
    return {
        "cluster": DemandCluster(cluster_id=cid, state="BR", category="roads_bridges", lgd_district="d",
                                 lgd_block="b", lgd_units=[], summary="s"),
        "demand_raw": demand, "trend_raw": trend, "gap": gap, "vulnerability": vuln, "coverage": coverage,
        "indicator_rows": [], "gap_indicator": "all_weather_road_access",
        "vulnerability_parts": {"disadvantaged_population_pct": vuln, "literacy_gap": None, "aspirational_district": None},
        "recency_weighted_citizens": 10.0, "population": 1000, "recent_requests": 5, "prior_requests": 5,
        "population_covered": 0, "investments": [],
    }


def test_default_weights_match_prd():
    w = Weights()
    assert (w.demand, w.infra_gap, w.vulnerability, w.trend, w.investment) == (30, 30, 20, 10, 10)


def test_formula_is_transparent_and_normalised_within_scope():
    [top, low] = scoring.score_contexts([ctx("A", demand=10), ctx("B", demand=5)], Weights())
    assert top.cluster_id == "A" and top.rank == 1
    d = {f.factor: f for f in top.breakdown}
    assert d["demand"].normalised == 1.0  # max in scope
    expected = 100 * (30 * 1 + 30 * 1 + 20 * 0.5 + 10 * 1) / 90
    assert top.priority_score == pytest.approx(round(expected, 1))
    assert sum(f.contribution for f in top.breakdown) == pytest.approx(top.priority_score, abs=0.1)
    assert {f.factor: f for f in low.breakdown}["demand"].normalised == 0.5


def test_investment_coverage_is_subtracted():
    [a] = scoring.score_contexts([ctx("A", coverage=0.0)], Weights())
    [b] = scoring.score_contexts([ctx("A", coverage=1.0)], Weights())
    assert b.priority_score == pytest.approx(a.priority_score - 100 * 10 / 90, abs=0.1)
    assert {f.factor: f for f in b.breakdown}["investment"].contribution < 0


def test_missing_gap_uses_neutral_value_and_is_flagged():
    [s] = scoring.score_contexts([ctx("A", gap=None)], Weights())
    gap = {f.factor: f for f in s.breakdown}["infra_gap"]
    assert gap.normalised == 0.5 and "missing" in gap.explanation


def test_score_is_clamped_and_banded():
    [s] = scoring.score_contexts([ctx("A", demand=1, gap=0, vuln=0, trend=0.0001, coverage=1)], Weights())
    assert s.priority_score >= 0
    assert scoring.band(70) == "High" and scoring.band(45) == "Medium" and scoring.band(44.9) == "Low"


def test_changing_weights_reranks():
    contexts = [ctx("DEMAND", demand=10, vuln=0.1), ctx("VULN", demand=3, vuln=1.0)]
    default = scoring.score_contexts(contexts, Weights())
    lens = scoring.score_contexts(contexts, Weights(demand=5, vulnerability=60))
    assert default[0].cluster_id == "DEMAND"
    assert lens[0].cluster_id == "VULN"


def test_real_data_ranking_and_default_rank(store):
    w = Weights(demand=10, infra_gap=10, vulnerability=70, trend=0, investment=10)
    scored, _ = ranking.rank(store, w)
    assert all(s.default_rank is not None for s in scored)
    assert any(s.rank != s.default_rank for s in scored)


def test_repeat_submissions_do_not_inflate_demand(store):
    c = store.clusters["CL-BR-0001"]
    before = fusion.cluster_context(c, store)
    count, unique = c.request_count, c.unique_citizens
    first = store.cluster_requests("CL-BR-0001")[0]
    latest = max(r.created_at for r in store.cluster_requests("CL-BR-0001") if r.citizen_id == first.citizen_id)
    dup = CitizenRequest(**{**first.model_dump(), "request_id": "DUP-1", "created_at": latest})
    store.requests[dup.request_id] = dup
    store.assign(dup, "CL-BR-0001")
    after = fusion.cluster_context(c, store, before["as_of"])
    assert c.request_count == count + 1
    assert c.unique_citizens == unique
    assert after["demand_raw"] == pytest.approx(before["demand_raw"])


def test_trend_uses_30_day_windows(store):
    c = store.clusters["CL-BR-0001"]
    ctx_ = fusion.cluster_context(c, store)
    now = ctx_["as_of"]
    reqs = store.cluster_requests("CL-BR-0001")
    assert ctx_["recent_requests"] == sum(1 for r in reqs if now - r.created_at <= timedelta(days=30))
    assert 0 <= ctx_["trend_raw"] <= 1
