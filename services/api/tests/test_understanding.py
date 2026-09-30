import json

import pytest

from app.config import settings
from app.models import LocationMention, RequestExtraction
from app.pipeline import location, understanding


def test_fixture_is_used_in_demo_mode_with_provenance(store):
    fx = understanding.fixtures()[0]
    ex, prov = understanding.extract(fx["text_original"], fx["text_en"], fx["language"], "web", fx["state"], None, [])
    assert ex.category == fx["expected"]["category"]
    assert prov.mode == "demo" and prov.model_name == "demo-fixture" and prov.prompt_version == "extract_v1"


@pytest.mark.parametrize("text,lang,category", [
    ("The handpump in Kothi is broken and there is no drinking water", "en", "drinking_water"),
    ("खैरा के पास नदी पर पुल नहीं है", "hi", "roads_bridges"),
    ("కణేకల్ లో రైతులకు సాగునీరు లేదు", "te", "irrigation"),
    ("Need a bus stop near Wagholi society", "en", "public_transport"),
    ("Open drain overflowing in Kondhwa", "en", "sanitation"),
])
def test_rule_extractor_uses_fixed_taxonomy(store, text, lang, category):
    gaz = location.gazetteer(list(store.units.values()))
    ex, prov = understanding.extract(text, text, lang, "web", None, None, gaz)
    assert ex.category == category
    assert prov.model_name == "demo-rule-extractor"
    assert ex.location_mentions  # every example names a known place


def test_guard_removes_numbers_not_stated_by_citizen():
    ex = RequestExtraction(
        category="drinking_water", sub_category="x", summary_en="s", location_mentions=[], urgency="high",
        urgency_reason="r", est_beneficiaries=500, vulnerable_groups=[], seasonality=None, sentiment=-0.5,
        confidence=0.9, missing_information=[], requires_clarification=False)
    out = understanding.guard(ex, "No water in our village", "No water in our village")
    assert out.est_beneficiaries is None and any("removed" in m for m in out.missing_information)


def test_low_confidence_requires_clarification(store):
    ex, _ = understanding.extract("please help us", "please help us", "en", "web", None, None, [])
    assert ex.requires_clarification


def test_demo_translation_and_transcript():
    fx = next(f for f in understanding.fixtures() if f["language"] == "te")
    tr = understanding.translate_to_en(fx["text_original"], "te")
    assert tr["text_en"] == fx["text_en"] and tr["mode"] == "demo"
    st = understanding.speech_to_text(b"fake-audio", "audio/webm", "te", "AP")
    assert st["mode"] == "demo" and st["language"] == "te" and st["transcript"]


@pytest.mark.skipif(not settings.gemini_api_key, reason="live Gemini evaluation needs GEMINI_API_KEY")
def test_live_gemini_matches_fixtures():  # pragma: no cover - only with a key
    for fx in understanding.fixtures():
        ex, prov = understanding.extract(fx["text_original"], fx["text_en"], fx["language"], "web", fx["state"], None, [])
        assert ex.category == fx["expected"]["category"], json.dumps(fx["id"])
        assert prov.mode == "real"


def test_location_resolution(store):
    units = list(store.units.values())
    r = location.resolve([LocationMention(text="सोनबरसा", type="village")], "", units, "hi", "BR")
    assert r.resolved and r.lgd_unit == "BR.GAY.TEK.SNB" and r.method == "exact_match" and r.h3_cell
    amb = location.resolve([LocationMention(text="Rampur", type="village")], "", units, "hi", "BR", "BR.GAY")
    assert not amb.resolved and amb.method == "ambiguous" and len(amb.candidates) == 2
    assert "प्रखंड" in amb.clarification_question
    hinted = location.resolve([LocationMention(text="Rampur", type="village")], "Rampur, Imamganj", units, "en", "BR")
    assert hinted.lgd_unit == "BR.GAY.IMG.RMP"
    fuzzy = location.resolve([LocationMention(text="Sonbarsaa", type="village")], "", units, "en", "BR")
    assert fuzzy.method == "fuzzy_match" and fuzzy.lgd_unit == "BR.GAY.TEK.SNB"
    pin = location.resolve([], "", units, "en", "AP", pin=(14.60, 77.08))
    assert pin.method == "pin" and pin.lgd_unit == "AP.ATP.KDG.MDG"
    none = location.resolve([LocationMention(text="Atlantis", type="village")], "", units, "te", "AP")
    assert none.method == "unresolved" and none.clarification_question
