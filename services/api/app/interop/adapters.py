"""State data adapters (PRD §20-22, §40): state-specific files -> canonical schema.

One generic adapter is driven by a per-state JSON config in `data/adapters/<STATE>.json`
(field mappings, value maps, unit multipliers, category/status maps). Onboarding a new state means
adding a config + raw files, not code.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import h3

from app.models import CATEGORIES, AdminUnit, Indicator, Investment

H3_RESOLUTION = 7


@dataclass
class StateData:
    config: dict
    units: list[AdminUnit] = field(default_factory=list)
    indicators: list[Indicator] = field(default_factory=list)
    investments: list[Investment] = field(default_factory=list)
    raw_unit_sample: dict | None = None
    raw_investment_sample: dict | None = None


def _get(record: dict, path: str) -> Any:
    cur: Any = record
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _read_records(data_dir: Path, spec: dict) -> list[dict]:
    path = data_dir / "sample" / spec["file"]
    if spec["format"] == "csv":
        with path.open(encoding="utf-8") as f:
            return list(csv.DictReader(f))
    doc = json.loads(path.read_text(encoding="utf-8"))
    return doc[spec["records_path"]] if spec.get("records_path") else doc


def _transform(values: list[Any], transform: str, value_maps: dict) -> float | bool | None:
    if any(v is None or v == "" for v in values):
        return None
    if transform == "int":
        return int(float(values[0]))
    if transform == "float":
        return float(values[0])
    if transform == "sum":
        return float(sum(float(v) for v in values))
    if transform == "bool01":
        return str(values[0]).strip() in ("1", "true", "True")
    if transform in value_maps:
        mapped = value_maps[transform].get(str(values[0]).strip())
        if mapped is None:
            raise ValueError(f"unmapped value {values[0]!r} for transform {transform}")
        return mapped
    raise ValueError(f"unknown transform {transform}")


def load_state(config: dict, data_dir: Path) -> StateData:
    state = config["state_code"]
    out = StateData(config=config)
    uspec = config["units"]
    f = uspec["fields"]
    records = _read_records(data_dir, uspec)
    districts_flagged: set[str] = set()
    for rec in records:
        lat, lng = float(_get(rec, f["lat"])), float(_get(rec, f["lng"]))
        unit = AdminUnit(
            lgd_code=str(_get(rec, f["unit_code"])),
            name=str(_get(rec, f["unit_name"])),
            name_local=_get(rec, f["unit_name_local"]) if f.get("unit_name_local") else None,
            level=config["unit_level"],
            state=state,
            district_code=str(_get(rec, f["district_code"])),
            district_name=str(_get(rec, f["district_name"])),
            block_code=str(_get(rec, f["block_code"])),
            block_name=str(_get(rec, f["block_name"])),
            lat=lat,
            lng=lng,
            h3_cell=h3.latlng_to_cell(lat, lng, H3_RESOLUTION),
        )
        out.units.append(unit)
        if out.raw_unit_sample is None:
            out.raw_unit_sample = rec
        for ind in config["indicators"]:
            value = _transform([_get(rec, c) for c in ind["columns"]], ind["transform"], config.get("value_maps", {}))
            if value is None:
                continue
            year = int(_get(rec, ind["year_column"])) if ind.get("year_column") else int(ind["year"])
            level = ind.get("level", config["unit_level"])
            code = unit.district_code if level == "district" else unit.lgd_code
            if level == "district":
                if code in districts_flagged:
                    continue
                districts_flagged.add(code)
            out.indicators.append(Indicator(
                lgd_code=code, indicator_name=ind["canonical"], value=value, year=year,
                geographic_level=level, source=ind["source"], definition=ind.get("definition"),
            ))

    ispec = config.get("investments")
    if ispec:
        fi = ispec["fields"]
        for rec in _read_records(data_dir, ispec):
            raw_cat = str(_get(rec, fi["category"]))
            category = ispec["category_map"].get(raw_cat, "other")
            if category not in CATEGORIES:
                raise ValueError(f"{state}: category map produced unknown category {category}")
            raw_status = str(_get(rec, fi["status"]))
            status = ispec["status_map"].get(raw_status)
            if status is None:
                raise ValueError(f"{state}: unmapped investment status {raw_status!r}")
            title = str(_get(rec, fi["title"]))
            scheme = str(_get(rec, fi["scheme"])) if fi.get("scheme") else title.split(":")[0].strip()
            codes = [c.strip() for c in str(_get(rec, fi["unit_codes"])).split(ispec["list_separator"]) if c.strip()]
            block = str(_get(rec, fi["block_code"])) if fi.get("block_code") else None
            if block is None and codes:
                block = next((u.block_code for u in out.units if u.lgd_code == codes[0]), None)
            out.investments.append(Investment(
                project_id=str(_get(rec, fi["project_id"])),
                scheme=scheme,
                title=title,
                category=category,
                lgd_codes=codes,
                block_code=block,
                status=status,
                sanctioned_amount_inr=float(_get(rec, fi["amount"])) * float(ispec["amount_multiplier"]),
                start_date=str(_get(rec, fi["start_date"])),
                population_covered=round(float(_get(rec, fi["population_covered"])) * float(ispec["population_multiplier"])),
                source=ispec["source"],
            ))
            if out.raw_investment_sample is None:
                out.raw_investment_sample = rec
    return out


def load_all_states(data_dir: Path) -> dict[str, StateData]:
    states = {}
    for cfg_path in sorted((data_dir / "adapters").glob("*.json")):
        config = json.loads(cfg_path.read_text(encoding="utf-8"))
        states[config["state_code"]] = load_state(config, data_dir)
    return states
