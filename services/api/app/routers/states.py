"""State configurations + interoperability view (PRD §20-22, §37 "State / Analytics", §40)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.routers.intelligence import analytics
from app.store import get_store

router = APIRouter(prefix="/api", tags=["states"])


def _summary(sd) -> dict:
    cfg = sd.config
    districts = {}
    for u in sd.units:
        districts.setdefault(u.district_code, {"code": u.district_code, "name": u.district_name, "blocks": set()})
        districts[u.district_code]["blocks"].add(u.block_name)
    return {
        "state_code": cfg["state_code"], "lgd_state_code": cfg["lgd_state_code"], "name": cfg["name"],
        "name_local": cfg["name_local"], "languages": cfg["languages"], "default_language": cfg["default_language"],
        "focus_categories": cfg["focus_categories"], "unit_level": cfg["unit_level"],
        "level_labels": cfg["level_labels"], "channels": cfg["channels"], "map_center": cfg["map_center"],
        "districts": [{**d, "blocks": sorted(d["blocks"])} for d in districts.values()],
        "units": len(sd.units), "indicators": len(sd.indicators), "investments": len(sd.investments),
        "adapter_config": f"data/adapters/{cfg['state_code']}.json",
        "is_sample": True,
    }


@router.get("/states")
def list_states() -> list[dict]:
    return [_summary(sd) for sd in get_store().states.values()]


@router.get("/states/{state_id}")
def get_state(state_id: str) -> dict:
    sd = get_store().states.get(state_id.upper())
    if not sd:
        raise HTTPException(404, "state not configured")
    return {**_summary(sd), "adapter": sd.config}


@router.get("/states/{state_id}/analytics")
def state_analytics(state_id: str, district: str | None = None) -> dict:
    store = get_store()
    if state_id.upper() not in store.states:
        raise HTTPException(404, "state not configured")
    return analytics(store, state_id.upper(), district)


@router.get("/states/{state_id}/interop")
def interop_example(state_id: str) -> dict:
    """Show one raw state record next to the canonical records the adapter produced from it."""
    store = get_store()
    sd = store.states.get(state_id.upper())
    if not sd:
        raise HTTPException(404, "state not configured")
    unit = sd.units[0]
    inv = sd.investments[0] if sd.investments else None
    req = next((r for r in store.requests.values() if r.state == sd.config["state_code"]), None)
    return {
        "state": sd.config["state_code"],
        "raw_unit_record": sd.raw_unit_sample,
        "canonical_unit": unit.model_dump(),
        "canonical_indicators": [i.model_dump() for i in store.unit_indicators(unit.lgd_code)],
        "raw_investment_record": sd.raw_investment_sample,
        "canonical_investment": inv.model_dump() if inv else None,
        "canonical_request_example": req.model_dump(mode="json") if req else None,
        "field_mapping": sd.config["units"]["fields"],
        "indicator_mapping": [{k: v for k, v in i.items() if k in ("canonical", "columns", "transform", "source")}
                              for i in sd.config["indicators"]],
    }


@router.get("/districts/{district_id}/indicators")
def district_indicators(district_id: str) -> dict:
    store = get_store()
    units = [u for u in store.units.values() if u.district_code == district_id]
    if not units:
        raise HTTPException(404, "district not found")
    rows = [{"unit": u.name, "block": u.block_name, **i.model_dump()}
            for u in units for i in store.unit_indicators(u.lgd_code)]
    rows += [{"unit": units[0].district_name, "block": None, **i.model_dump()} for i in store.unit_indicators(district_id)]
    return {"district": district_id, "name": units[0].district_name, "state": units[0].state, "indicators": rows}
