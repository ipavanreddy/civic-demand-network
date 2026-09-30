"""Location resolution (PRD §12): mentions -> sample LGD-style unit + H3 cell.

Order: pin -> exact name match (Latin or local script) -> fuzzy match -> Maps geocoding (if
MAPS_API_KEY) -> unresolved. Ambiguous names produce one clarification question.
"""
from __future__ import annotations

import difflib
import math

from app.integrations import maps
from app.models import AdminUnit, LocationMention, LocationResolution
from app.pipeline import messages
from app.pipeline.understanding import normalise

PIN_RADIUS_KM = 10.0
GEOCODE_RADIUS_KM = 15.0


def haversine_km(a_lat: float, a_lng: float, b_lat: float, b_lng: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp, dl = p2 - p1, math.radians(b_lng - a_lng)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def _resolved(u: AdminUnit, method: str, confidence: float) -> LocationResolution:
    return LocationResolution(
        resolved=True, lgd_state=u.state, lgd_district=u.district_code, lgd_block=u.block_code,
        lgd_unit=u.lgd_code, unit_name=u.name, block_name=u.block_name, district_name=u.district_name,
        h3_cell=u.h3_cell, lat=u.lat, lng=u.lng, method=method, confidence=round(confidence, 2),  # type: ignore[arg-type]
    )


def _scope(units: list[AdminUnit], state: str | None, district: str | None) -> list[AdminUnit]:
    scoped = [u for u in units if not state or u.state == state]
    if district:
        d = normalise(district)
        narrowed = [u for u in scoped if u.district_code == district or normalise(u.district_name) == d]
        scoped = narrowed or scoped
    return scoped


def gazetteer(units: list[AdminUnit]) -> list[tuple[str, str, str]]:
    """(text to look for, canonical Latin name, mention type) for the demo rule extractor."""
    out: list[tuple[str, str, str]] = []
    for u in units:
        out.append((u.name, u.name, "ward" if u.level == "ward" else "village"))
        if u.name_local:
            out.append((u.name_local, u.name, "ward" if u.level == "ward" else "village"))
    for block in {u.block_name for u in units}:
        out.append((block, block, "block"))
    return out


def _nearest(units: list[AdminUnit], lat: float, lng: float, radius: float) -> AdminUnit | None:
    best = min(units, key=lambda u: haversine_km(lat, lng, u.lat, u.lng), default=None)
    if best and haversine_km(lat, lng, best.lat, best.lng) <= radius:
        return best
    return None


def resolve(mentions: list[LocationMention], text: str, units: list[AdminUnit], language: str,
            state: str | None = None, district: str | None = None, pin: tuple[float, float] | None = None,
            state_name: str | None = None) -> LocationResolution:
    scoped = _scope(units, state, district)
    if pin:
        u = _nearest(scoped, pin[0], pin[1], PIN_RADIUS_KM)
        if u:
            return _resolved(u, "pin", 0.95)

    names = [m.text for m in mentions]
    blob = normalise(text)
    block_hints = {u.block_code for u in scoped
                   if normalise(u.block_name) in {normalise(n) for n in names} or f" {normalise(u.block_name)} " in f" {blob} "}

    def exact(name: str) -> list[AdminUnit]:
        n = normalise(name)
        return [u for u in scoped if n in (normalise(u.name), normalise(u.name_local or ""))]

    place_mentions = [m for m in mentions if m.type not in ("block", "mandal", "district")]
    candidates: list[AdminUnit] = []
    ambiguous_name = None
    for m in place_mentions:
        hits = exact(m.text)
        if block_hints:
            hits = [u for u in hits if u.block_code in block_hints] or hits
        if len(hits) == 1:
            return _resolved(hits[0], "exact_match", 0.9)
        if len(hits) > 1:
            candidates, ambiguous_name = hits, m.text
            break

    if not candidates:  # names written in the text but not returned as mentions (e.g. local script)
        found = [u for u in scoped if f" {normalise(u.name)} " in f" {blob} "
                 or (u.name_local and normalise(u.name_local) in blob)]
        by_name: dict[str, list[AdminUnit]] = {}
        for u in found:
            by_name.setdefault(u.name, []).append(u)
        for name, hits in by_name.items():
            if block_hints:
                hits = [u for u in hits if u.block_code in block_hints] or hits
            if len(hits) == 1:
                return _resolved(hits[0], "exact_match", 0.85)
            candidates, ambiguous_name = hits, name
            break

    if candidates and ambiguous_name:
        options = [{"lgd_code": u.lgd_code, "label": f"{u.name} ({u.block_name}, {u.district_name})"} for u in candidates]
        q = messages.render("ambiguous", language, name=ambiguous_name,
                            options=" / ".join(f"{u.block_name}" for u in candidates))
        return LocationResolution(resolved=False, method="ambiguous", confidence=0.4, candidates=options,
                                  clarification_question=q)

    latin = {u.name: u for u in scoped}
    for m in place_mentions:
        close = difflib.get_close_matches(m.text, list(latin), n=1, cutoff=0.8)
        if close:
            ratio = difflib.SequenceMatcher(None, m.text.lower(), close[0].lower()).ratio()
            return _resolved(latin[close[0]], "fuzzy_match", 0.85 * ratio)

    if maps.configured() and place_mentions:
        district_name = scoped[0].district_name if district and scoped else ""
        for m in place_mentions:
            addr = ", ".join(x for x in [m.text, district_name, state_name or "", "India"] if x)
            loc = maps.geocode(addr)
            if loc:
                u = _nearest(scoped, loc[0], loc[1], GEOCODE_RADIUS_KM)
                if u:
                    return _resolved(u, "geocoded", 0.7)

    return LocationResolution(resolved=False, method="unresolved", confidence=0.0,
                              clarification_question=messages.render("unresolved", language))


def resolve_code(code: str, units: dict[str, AdminUnit]) -> LocationResolution | None:
    u = units.get(code)
    return _resolved(u, "clarified", 1.0) if u else None
