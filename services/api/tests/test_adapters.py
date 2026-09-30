import json
import shutil
from pathlib import Path

import pytest

from app.config import settings
from app.interop.adapters import load_all_states, load_state

DATA = Path(settings.data_dir)


@pytest.fixture(scope="module")
def states():
    return load_all_states(DATA)


def test_three_state_configs_load_into_canonical_schema(states):
    assert set(states) == {"BR", "AP", "MH"}
    for sd in states.values():
        assert sd.units and sd.indicators and sd.investments
        assert all(u.h3_cell and u.code_system == "sample-lgd-style" for u in sd.units)
        assert all(i.source and i.year and i.is_sample for i in sd.indicators)


def test_bihar_hindi_values_are_mapped(states):
    br = states["BR"]
    road = {i.lgd_code: i.value for i in br.indicators if i.indicator_name == "all_weather_road_access"}
    assert road["BR.GAY.TEK.SNB"] is False and road["BR.GAY.SHG.RMP"] is True
    inv = {i.project_id: i for i in br.investments}
    assert inv["BR-PMGSY-2025-117"].status == "sanctioned"
    assert inv["BR-PMGSY-2025-117"].category == "roads_bridges"
    assert inv["BR-PMGSY-2025-117"].sanctioned_amount_inr == 185 * 100000
    assert inv["BR-PMGSY-2025-117"].scheme == "PMGSY"
    aspir = [i for i in br.indicators if i.indicator_name == "aspirational_district"]
    assert {i.lgd_code for i in aspir} == {"BR.GAY", "BR.AUR"} and all(i.geographic_level == "district" for i in aspir)


def test_andhra_adapter_sums_sc_st_and_converts_households(states):
    ap = states["AP"]
    dis = {i.lgd_code: i.value for i in ap.indicators if i.indicator_name == "disadvantaged_population_pct"}
    assert dis["AP.ATP.KDG.MDG"] == 18 + 6
    work = next(i for i in ap.investments if i.project_id == "AP-JJM-KDG-0231")
    assert work.population_covered == round(520 * 4.2)
    assert work.status == "ongoing" and work.category == "drinking_water"


def test_maharashtra_urban_adapter(states):
    mh = states["MH"]
    assert all(u.level == "ward" for u in mh.units)
    inv = {i.project_id: i for i in mh.investments}
    assert inv["PMC-PMPML-2026-07"].category == "public_transport"
    assert inv["PMC-PMPML-2026-07"].lgd_codes == ["PMC-W04", "PMC-W22"]
    assert inv["PMC-PMPML-2026-07"].block_code == "MH.PUN.PMC"  # derived from the ward


def test_new_state_is_config_only(tmp_path):
    """Onboarding: a new config + raw files, no code changes (PRD §40)."""
    shutil.copytree(DATA / "sample", tmp_path / "sample")
    cfg = json.loads((DATA / "adapters" / "BR.json").read_text(encoding="utf-8"))
    cfg["state_code"], cfg["name"] = "XX", "Test State"
    sd = load_state(cfg, tmp_path)
    assert sd.units[0].state == "XX" and len(sd.units) == 12


def test_unmapped_status_is_rejected(tmp_path):
    shutil.copytree(DATA / "sample", tmp_path / "sample")
    cfg = json.loads((DATA / "adapters" / "AP.json").read_text(encoding="utf-8"))
    cfg["investments"]["status_map"].pop("Grounded")
    with pytest.raises(ValueError, match="unmapped investment status"):
        load_state(cfg, tmp_path)
