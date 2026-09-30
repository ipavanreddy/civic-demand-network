"""Request intake orchestration (PRD §8, §9, §32): text -> translation -> Gemini extraction ->
schema validation -> location resolution -> confirmation (citizen's language) -> clustering."""
from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import UTC, datetime

from app.config import settings
from app.integrations import google_speech
from app.models import CATEGORIES, CitizenRequest, LocationMention, LocationResolution
from app.pipeline import clustering, location, messages, understanding
from app.store import Store

log = logging.getLogger(__name__)


def citizen_id(ref: str | None) -> str:
    ref = ref or f"anon-{uuid.uuid4()}"
    return "CIT-" + hashlib.sha256(f"{settings.citizen_id_salt}:{ref}".encode()).hexdigest()[:10]


def speak(text: str, language: str) -> dict:
    if google_speech.configured():
        try:
            return {"mode": "real", "provider": "Cloud Text-to-Speech",
                    "audio_base64": google_speech.text_to_speech(text, language), "mime": "audio/mpeg"}
        except Exception as exc:  # noqa: BLE001
            log.warning("TTS failed, browser fallback: %s", exc)
    return {"mode": "demo", "provider": "browser speech synthesis", "audio_base64": None, "mime": None}


def _place_label(store: Store, req: CitizenRequest, language: str) -> str:
    u = store.units.get(req.lgd_unit or "")
    if not u:
        return "?"
    return u.name_local if language != "en" and u.name_local else u.name


def view(store: Store, req: CitizenRequest) -> dict:
    """Citizen-facing view of a request (used by POST/GET/confirm responses)."""
    extra = store.extras.get(req.request_id, {})
    cluster = store.clusters.get(req.cluster_id or "")
    status = cluster.status if cluster and cluster.status != "Clustered" else req.status
    cluster_view = None
    if cluster:
        quotes = list(dict.fromkeys(r.text_en for r in store.cluster_requests(cluster.cluster_id)))[:3]
        cluster_view = {**cluster.model_dump(mode="json"), "representative_quotes": quotes,
                        **extra.get("clustering", {})}
    lang = req.language
    if req.status == "Needs Clarification":
        message = extra.get("clarification_question") or messages.render("low_confidence", lang)
    elif cluster:
        key = "clustered" if extra.get("clustering", {}).get("joined_existing", True) else "new_cluster"
        message = messages.render(key, lang, id=req.request_id, n=cluster.request_count - 1 or 1,
                                  unique=cluster.unique_citizens, status=status)
    else:
        message = messages.render("confirm", lang, category=req.category, place=_place_label(store, req, lang),
                                  id=req.request_id)
    demo_parts = [k for k in ("translation", "provenance", "speech") if (extra.get(k) or {}).get("mode") == "demo"]
    return {
        "request": req.model_dump(mode="json"),
        "status": status,
        "status_label": messages.status_label(status, lang),
        "extraction": extra.get("extraction"),
        "provenance": extra.get("provenance"),
        "translation": extra.get("translation"),
        "speech": extra.get("speech"),
        "location": extra.get("location"),
        "needs_clarification": req.status == "Needs Clarification",
        "clarification_question": extra.get("clarification_question") if req.status == "Needs Clarification" else None,
        "message": {"language": lang, "text": message},
        "cluster": cluster_view,
        "demo_mode": bool(demo_parts) or req.is_synthetic,
        "demo_components": demo_parts,
    }


def _apply_location(req: CitizenRequest, loc: LocationResolution) -> None:
    if loc.resolved:
        req.state = loc.lgd_state
        req.lgd_district, req.lgd_block, req.lgd_unit = loc.lgd_district, loc.lgd_block, loc.lgd_unit
        req.h3_cell = loc.h3_cell
    req.resolution_method = loc.method
    req.resolution_confidence = loc.confidence


def create(store: Store, *, text: str, language: str, channel: str = "web", citizen_ref: str | None = None,
           state: str | None = None, district: str | None = None, pin: tuple[float, float] | None = None,
           audio_url: str | None = None, speech: dict | None = None, auto_confirm: bool = False) -> dict:
    translation = understanding.translate_to_en(text, language)
    units = list(store.units.values())
    scoped = [u for u in units if not state or u.state == state]
    state_name = store.states[state].config["name"] if state in store.states else None
    ex, prov = understanding.extract(text, translation["text_en"], language, channel, state, district,
                                     location.gazetteer(scoped))
    loc = location.resolve(ex.location_mentions, f"{text} {translation['text_en']}", units, language,
                           state, district, pin, state_name)
    req = CitizenRequest(
        request_id=f"REQ-{uuid.uuid4().hex[:6].upper()}",
        citizen_id=citizen_id(citizen_ref), channel=channel, language=language, text_original=text,
        text_en=translation["text_en"], audio_url=audio_url, category=ex.category, sub_category=ex.sub_category,
        summary_en=ex.summary_en, urgency=ex.urgency, urgency_reason=ex.urgency_reason,
        est_beneficiaries=ex.est_beneficiaries, vulnerable_groups=ex.vulnerable_groups, seasonality=ex.seasonality,
        sentiment=ex.sentiment, confidence=ex.confidence, missing_information=ex.missing_information,
        state=state, created_at=datetime.now(UTC), model_name=prov.model_name,
        model_version=prov.model_version, prompt_version=prov.prompt_version,
    )
    _apply_location(req, loc)
    needs = (not loc.resolved) or ex.requires_clarification
    req.status = "Needs Clarification" if needs else "Understood"
    question = loc.clarification_question or ex.clarification_question or (
        messages.render("low_confidence", language) if needs else None)
    store.extras[req.request_id] = {
        "extraction": ex.model_dump(), "provenance": prov.model_dump(mode="json"), "translation": translation,
        "speech": speech, "location": loc.model_dump(), "clarification_question": question,
    }
    store.add_request(req)
    if auto_confirm and not needs:
        return confirm(store, req.request_id)
    out = view(store, req)
    out["message"]["speech"] = speak(out["message"]["text"], language)
    return out


def confirm(store: Store, request_id: str, category: str | None = None, lgd_code: str | None = None,
            location_text: str | None = None) -> dict:
    req = store.requests[request_id]
    extra = store.extras.setdefault(request_id, {})
    if category:
        if category not in CATEGORIES:
            raise ValueError(f"unknown category {category}")
        req.category = category
        extra.setdefault("corrections", {})["category"] = category
    loc = None
    if lgd_code:
        loc = location.resolve_code(lgd_code, store.units)
        if loc is None:
            raise ValueError(f"unknown location code {lgd_code}")
    elif location_text:
        loc = location.resolve([LocationMention(text=location_text, type="other")], location_text,
                               list(store.units.values()), req.language, req.state)
    if loc is not None:
        _apply_location(req, loc)
        extra["location"] = loc.model_dump()
        extra.setdefault("corrections", {})["location"] = lgd_code or location_text
        if not loc.resolved:
            req.status = "Needs Clarification"
            extra["clarification_question"] = loc.clarification_question
            store.save()
            return view(store, req)
    if not req.lgd_unit:
        req.status = "Needs Clarification"
        store.save()
        return view(store, req)
    if req.cluster_id is None:
        extra["clustering"] = clustering.assign(req, store)
    out = view(store, req)
    out["message"]["speech"] = speak(out["message"]["text"], req.language)
    return out
