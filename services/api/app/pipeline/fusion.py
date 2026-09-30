"""Data fusion (PRD §14): join each demand cluster with demographics, infrastructure gap and
investment data from the canonical store. Every value keeps its source, year and level."""
from __future__ import annotations

from datetime import datetime, timedelta

from app.models import DemandCluster, Indicator
from app.pipeline import taxonomy
from app.store import Store

HALF_LIFE_DAYS = 45
TREND_WINDOW_DAYS = 30
# How much of a project's covered population counts as "already addressed" (PRD §15).
STATUS_WEIGHT = {"proposed": 0.25, "sanctioned": 1.0, "ongoing": 1.0, "completed": 0.5}
VULNERABILITY_PARTS = {"disadvantaged_population_pct": 0.4, "literacy_gap": 0.3, "aspirational_district": 0.3}


def as_of(store: Store) -> datetime:
    """Data-relative 'now' (latest request), so the synthetic history scores the same on any day."""
    return max(r.created_at for r in store.requests.values())


def unit_gap(ind: Indicator | None, spec: dict | None) -> float | None:
    if ind is None or spec is None:
        return None
    v = ind.value
    if spec["kind"] == "bool_good":
        return 0.0 if bool(v) else 1.0
    if spec["kind"] == "pct_good":
        return max(0.0, min(1.0, 1 - float(v) / 100))
    if spec["kind"] == "distance_bad":
        return max(0.0, min(1.0, float(v) / float(spec.get("full_gap_at", 15))))
    return None


def _ind(store: Store, code: str, name: str) -> Indicator | None:
    return next((i for i in store.unit_indicators(code) if i.indicator_name == name), None)


def _weighted(pairs: list[tuple[float, int]]) -> float | None:
    total = sum(p for _, p in pairs)
    return sum(v * p for v, p in pairs) / total if pairs and total else None


def cluster_context(c: DemandCluster, store: Store, now: datetime | None = None) -> dict:
    now = now or as_of(store)
    units = [store.units[u] for u in c.lgd_units if u in store.units]
    pops = {u.lgd_code: int(_ind(store, u.lgd_code, "population").value) if _ind(store, u.lgd_code, "population") else 0
            for u in units}
    population = sum(pops.values())
    cat = taxonomy.categories().get(c.category, {})
    gap_spec = cat.get("gap_indicator")

    rows: list[dict] = []
    gap_pairs, dis_pairs, lit_pairs = [], [], []
    for u in units:
        for ind in store.unit_indicators(u.lgd_code):
            rows.append({"unit": u.name, **ind.model_dump()})
        g = unit_gap(_ind(store, u.lgd_code, gap_spec["name"]) if gap_spec else None, gap_spec)
        if g is not None:
            gap_pairs.append((g, pops[u.lgd_code]))
        d = _ind(store, u.lgd_code, "disadvantaged_population_pct")
        if d is not None:
            dis_pairs.append((float(d.value) / 100, pops[u.lgd_code]))
        lit = _ind(store, u.lgd_code, "literacy_rate_pct")
        if lit is not None:
            lit_pairs.append((1 - float(lit.value) / 100, pops[u.lgd_code]))
    district_flags = [i for i in store.unit_indicators(c.lgd_district) if i.indicator_name == "aspirational_district"]
    rows.extend({"unit": units[0].district_name if units else c.lgd_district, **i.model_dump()} for i in district_flags)

    vuln_parts = {
        "disadvantaged_population_pct": _weighted(dis_pairs),
        "literacy_gap": _weighted(lit_pairs),
        "aspirational_district": (1.0 if district_flags[0].value else 0.0) if district_flags else None,
    }
    present = {k: v for k, v in vuln_parts.items() if v is not None}
    vulnerability = (sum(VULNERABILITY_PARTS[k] * v for k, v in present.items()) / sum(VULNERABILITY_PARTS[k] for k in present)
                     if present else None)

    unit_codes = {u.lgd_code for u in units}
    investments, covered = [], 0.0
    for inv in store.investments:
        if inv.category != c.category:
            continue
        overlap = unit_codes & set(inv.lgd_codes)
        if not overlap and inv.block_code != c.lgd_block:
            continue
        covers = bool(overlap)
        if covers:
            overlap_pop = sum(pops.get(code, 0) for code in overlap)
            covered += STATUS_WEIGHT[inv.status] * min(inv.population_covered, overlap_pop)
        investments.append({**inv.model_dump(), "covers_cluster_area": covers})
    coverage = min(1.0, covered / population) if population else 0.0

    reqs = store.cluster_requests(c.cluster_id)
    latest: dict[str, datetime] = {}
    for r in reqs:
        latest[r.citizen_id] = max(latest.get(r.citizen_id, r.created_at), r.created_at)
    recency_weighted = sum(0.5 ** (max(0.0, (now - t).total_seconds() / 86400) / HALF_LIFE_DAYS) for t in latest.values())
    recent = sum(1 for r in reqs if now - r.created_at <= timedelta(days=TREND_WINDOW_DAYS))
    prior = sum(1 for r in reqs if timedelta(days=TREND_WINDOW_DAYS) < now - r.created_at <= timedelta(days=2 * TREND_WINDOW_DAYS))

    return {
        "cluster": c,
        "units": units,
        "population": population,
        "indicator_rows": rows,
        "gap": _weighted(gap_pairs),
        "gap_indicator": gap_spec["name"] if gap_spec else None,
        "vulnerability": vulnerability,
        "vulnerability_parts": vuln_parts,
        "investments": investments,
        "coverage": coverage,
        "population_covered": int(covered),
        "demand_raw": (recency_weighted / population * 10000) if population else 0.0,
        "recency_weighted_citizens": recency_weighted,
        "recent_requests": recent,
        "prior_requests": prior,
        "trend_raw": recent / (recent + prior) if (recent + prior) else 0.5,
        "as_of": now,
    }
