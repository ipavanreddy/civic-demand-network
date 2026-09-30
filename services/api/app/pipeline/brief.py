"""Evidence briefs (PRD §16, §33, §34.2) + number-grounding validation (PRD §32, FR-08).

Real mode: Gemini with `ai/prompts/evidence_brief_v1.md`, given ONLY the structured input below.
Demo mode: a deterministic template over the same input. Both are checked so that every number in
the brief exists in the input data.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime

from app.ai import gemini
from app.models import DataEvidence, EvidenceBrief, Provenance, ScoredCluster
from app.pipeline import taxonomy
from app.pipeline.understanding import render
from app.store import Store

log = logging.getLogger(__name__)
PROMPT = ("evidence_brief", "v1")
NUM_RE = re.compile(r"(?<![\w.])\d+(?:,\d{2,3})*(?:\.\d+)?")

RELEVANT = ("population", "disadvantaged_population_pct", "literacy_rate_pct", "aspirational_district")
NEXT_STEP = {
    "roads_bridges": "Field verification by the block engineer to confirm the crossing/alignment, then a DPR proposal under the relevant road/bridge scheme.",
    "drinking_water": "Field verification of source and supply status by the RWS/PHED engineer; check whether the existing water-supply work covers the affected habitations.",
    "public_transport": "Route and ridership check with the transport undertaking; pilot schedule change or feeder route for review.",
    "sanitation": "Site inspection by the ward engineer; check drain capacity against the ongoing works.",
}


def build_input(sc: ScoredCluster, ctx: dict, store: Store, scope: dict, total_in_scope: int) -> dict:
    c = ctx["cluster"]
    reqs = sorted(store.cluster_requests(c.cluster_id), key=lambda r: r.created_at, reverse=True)
    quotes, seen = [], set()
    for r in reqs:
        if r.text_en not in seen:
            seen.add(r.text_en)
            quotes.append({"language": r.language, "original": r.text_original, "translated_en": r.text_en})
        if len(quotes) == 3:
            break
    units = ctx["units"]
    return {
        "scope": scope,
        "ranking": {"rank": sc.rank, "of": total_in_scope, "priority_score": sc.priority_score, "score_scale_max": 100,
                    "band": sc.band,
                    "weights_percent": sc.weights_used.model_dump()},
        "score_breakdown": [{"factor": f.label, "normalised": f.normalised, "weight": f.weight,
                             "contribution": f.contribution, "explanation": f.explanation} for f in sc.breakdown],
        "cluster": {
            "cluster_id": c.cluster_id,
            "category": c.category,
            "category_label": taxonomy.label(c.category),
            "gap_indicator": ctx["gap_indicator"],
            "sub_category": c.sub_category,
            "summary": c.summary,
            "places": [u.name for u in units],
            "places_count": len(units),
            "block": units[0].block_name if units else None,
            "district": units[0].district_name if units else None,
            "state": store.states[c.state].config["name"] if c.state in store.states else c.state,
            "request_count": c.request_count,
            "unique_citizens": c.unique_citizens,
            "first_seen": c.first_seen.date().isoformat() if c.first_seen else None,
            "last_seen": c.last_seen.date().isoformat() if c.last_seen else None,
            "days_span": (c.last_seen - c.first_seen).days if c.first_seen and c.last_seen else None,
            "trend_window_days": 30,
            "requests_last_30_days": ctx["recent_requests"],
            "population": ctx["population"],
            "population_covered": ctx["population_covered"] or None,
            "synthetic_requests": any(r.is_synthetic for r in reqs),
            "representative_quotes": quotes,
        },
        "indicators": [{"place": r["unit"], "field": r["indicator_name"], "value": r["value"], "year": r["year"],
                        "level": r["geographic_level"], "source": r["source"], "is_sample": r["is_sample"]}
                       for r in ctx["indicator_rows"]],
        "investments": [{"project_id": i["project_id"], "scheme": i["scheme"], "title": i["title"],
                         "status": i["status"], "amount_lakh_inr": round(i["sanctioned_amount_inr"] / 100000, 1),
                         "start_date": i["start_date"], "population_covered": i["population_covered"],
                         "covers_cluster_area": i["covers_cluster_area"], "source": i["source"], "is_sample": i["is_sample"]}
                        for i in ctx["investments"]],
        "data_as_of": ctx["as_of"].date().isoformat(),
    }


# ------------------------------------------------------------------------------ grounding
def _allowed_numbers(obj) -> set[float]:
    out: set[float] = set()

    def add(v: float) -> None:
        for x in (v, round(v), round(v, 1), round(v, 2)):
            out.add(float(x))
        if 0 < abs(v) <= 1:
            for x in (v * 100, round(v * 100), round(v * 100, 1)):
                out.add(float(x))

    def walk(o) -> None:
        if isinstance(o, bool) or o is None:
            return
        if isinstance(o, (int, float)):
            add(float(o))
        elif isinstance(o, str):
            for m in NUM_RE.findall(o):
                add(float(m.replace(",", "")))
            for m in re.findall(r"\d+", o):  # dates, IDs
                add(float(m))
        elif isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(obj)
    return out


def brief_numbers(brief: EvidenceBrief) -> list[str]:
    texts = [brief.title, brief.summary, *brief.demand_evidence, *brief.investment_context, *brief.uncertainties,
             brief.next_step, brief.beneficiaries_basis]
    for d in brief.data_evidence:
        texts += [d.claim, d.value, d.year]
    found = [m for t in texts for m in NUM_RE.findall(t or "")]
    if brief.estimated_beneficiaries is not None:
        found.append(str(brief.estimated_beneficiaries))
    return found


def check_grounding(brief: EvidenceBrief, data: dict) -> dict:
    allowed = _allowed_numbers(data)
    ungrounded = []
    for n in brief_numbers(brief):
        v = float(n.replace(",", ""))
        if not any(abs(v - a) <= 1e-6 or (abs(a) >= 1 and abs(v - a) / abs(a) < 0.005) for a in allowed):
            ungrounded.append(n)
    return {"ok": not ungrounded, "numbers_checked": len(brief_numbers(brief)), "ungrounded_numbers": ungrounded}


# ------------------------------------------------------------------------------ generation
def _fmt(v) -> str:
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return f"{v:,}" if isinstance(v, int) else str(v)


def template_brief(data: dict) -> EvidenceBrief:
    c, rk = data["cluster"], data["ranking"]
    places = ", ".join(c["places"])
    title = f"{c['category_label']} ({(c['sub_category'] or '').replace('_', ' ')}) – {places}, {c['district']} ({c['state']})"
    demand = [
        f"{_fmt(c['request_count'])} requests from {_fmt(c['unique_citizens'])} unique citizens across "
        f"{c['places_count']} place(s) between {c['first_seen']} and {c['last_seen']}"
        + (" (synthetic sample requests)." if c["synthetic_requests"] else "."),
        f"{_fmt(c['requests_last_30_days'])} of these arrived in the last 30 days.",
        *[f"\"{q['translated_en']}\" (original in {q['language']})" for q in c["representative_quotes"]],
    ]
    evidence = [
        DataEvidence(
            claim=f"{ind['place']}: {ind['field'].replace('_', ' ')} = {_fmt(ind['value'])}"
                  + (" (sample)" if ind["is_sample"] else ""),
            field=ind["field"], value=_fmt(ind["value"]), source=ind["source"], year=str(ind["year"]))
        for ind in data["indicators"]
        if ind["field"] in (*RELEVANT, c["gap_indicator"])
    ]
    inv_lines = [
        f"{i['project_id']} {i['title']} ({i['scheme']}): {i['status']}, {_fmt(i['amount_lakh_inr'])} lakh INR, "
        f"covers {_fmt(i['population_covered'])} people"
        + ("" if i["covers_cluster_area"] else " (same block/area, but not these places)")
        + (" [sample data]" if i["is_sample"] else "")
        for i in data["investments"]
    ] or [f"No sanctioned, ongoing or completed {c['category_label'].lower()} project recorded for these places (sample investment dataset)."]
    uncertainties = []
    if any(ind["is_sample"] for ind in data["indicators"]):
        uncertainties.append("Indicator and investment values are SAMPLE / SYNTHETIC data for the demo, not official statistics.")
    if any(ind["year"] == 2011 for ind in data["indicators"]):
        uncertainties.append("Population and demographic baselines are from Census 2011 and may be outdated.")
    for f in data["score_breakdown"]:
        if "missing" in f["explanation"]:
            uncertainties.append(f"{f['factor']}: {f['explanation']}.")
    uncertainties.append("Exact site and scope are not verified on the ground; citizen reports are self-reported.")
    beneficiaries = c["population"] if c["population"] else None
    return EvidenceBrief(
        title=title,
        summary=f"Priority Score {rk['priority_score']} / 100 ({rk['band']}), rank {rk['rank']} of {rk['of']} in the selected scope. {c['summary']}",
        demand_evidence=demand,
        data_evidence=evidence,
        investment_context=inv_lines,
        estimated_beneficiaries=beneficiaries,
        beneficiaries_basis="Total population of the places in this cluster (Census 2011 sample values)" if beneficiaries else "Not available",
        uncertainties=uncertainties,
        next_step=NEXT_STEP.get(c["category"], "Field verification by the responsible line department before any proposal is prepared."),
        confidence=0.7,
    )


def generate(data: dict) -> tuple[EvidenceBrief, Provenance]:
    prompt_version = "_".join(PROMPT)
    if gemini.is_configured():
        try:
            prompt = render(gemini.load_prompt(*PROMPT),
                            input_json=json.dumps(data, ensure_ascii=False, indent=1, default=str))
            brief, prov = gemini.generate_structured(prompt, EvidenceBrief, prompt_version)
            return brief, Provenance(**prov.model_dump(), mode="real")
        except Exception as exc:  # noqa: BLE001
            log.warning("Gemini brief failed, using template: %s", exc)
    return template_brief(data), Provenance(
        model_name="demo-template", model_version="template-v1", prompt_version=prompt_version,
        generated_at=datetime.now(UTC), mode="demo",
        note="Demo mode: deterministic template over the same structured input (Gemini not configured).")
