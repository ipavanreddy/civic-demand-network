"""AI request understanding (PRD §11, §33, §34.1) + speech/translation front door (PRD §10).

Real mode: Gemini (`generate_structured`) with `ai/prompts/extract_v1.md`, Cloud Speech/Translation.
Demo mode: hand-authored fixtures in `ai/evaluation/fixtures/extraction/`, then a transparent
rule-based extractor. Every output carries provenance (model_name / model_version / prompt_version).
"""
from __future__ import annotations

import json
import logging
import re
import unicodedata
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

from google.genai import types

from app.ai import gemini
from app.config import settings
from app.integrations import google_speech
from app.models import (
    LocationMention,
    Provenance,
    RequestExtraction,
    Transcript,
    Translation,
)
from app.pipeline import taxonomy

log = logging.getLogger(__name__)
FIXTURE_DIR = Path(settings.ai_dir) / "evaluation" / "fixtures" / "extraction"
EXTRACT_PROMPT = ("extract", "v1")
CLARIFY_THRESHOLD = 0.6


def _now() -> datetime:
    return datetime.now(UTC)


def render(template: str, **values: str) -> str:
    for k, v in values.items():
        template = template.replace("{{" + k + "}}", v)
    return template


def normalise(text: str) -> str:
    """Lower-case, NFC, punctuation -> space. Keeps Devanagari/Telugu vowel signs (not \\w in Python)."""
    text = unicodedata.normalize("NFC", text).lower().replace("।", " ").replace("॥", " ")
    return re.sub(r"[^\wऀ-ॿఀ-౿]+", " ", text).strip()


@lru_cache
def fixtures() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(FIXTURE_DIR.glob("*.json"))]


def find_fixture(text: str) -> dict | None:
    key = normalise(text)
    for fx in fixtures():
        if key in (normalise(fx["text_original"]), normalise(fx["text_en"])):
            return fx
    return None


# ------------------------------------------------------------------------------------ speech
def speech_to_text(audio: bytes, content_type: str, language: str, state: str | None = None) -> dict:
    if google_speech.configured():
        try:
            text, lang = google_speech.speech_to_text(audio, content_type, language)
            return {"transcript": text, "language": lang, "mode": "real", "provider": "Cloud Speech-to-Text"}
        except Exception as exc:  # noqa: BLE001
            log.warning("Speech-to-Text failed, trying fallback: %s", exc)
    if gemini.is_configured():
        try:
            prompt = render(gemini.load_prompt("transcribe", "v1"), language=language)
            part = types.Part.from_bytes(data=audio, mime_type=content_type or "audio/webm")
            out, _ = gemini.generate_structured(prompt, Transcript, "transcribe_v1", parts=[part])
            return {"transcript": out.transcript, "language": out.language, "mode": "real",
                    "provider": "Gemini audio transcription"}
        except Exception as exc:  # noqa: BLE001
            log.warning("Gemini transcription failed, using demo transcript: %s", exc)
    candidates = [f for f in fixtures() if f["language"] == language]
    preferred = [f for f in candidates if state and f.get("state") == state and f.get("demo_voice")]
    fx = (preferred or [f for f in candidates if f.get("demo_voice")] or candidates or fixtures())[0]
    return {
        "transcript": fx["text_original"], "language": fx["language"], "mode": "demo",
        "provider": "demo sample transcript",
        "note": "Demo mode: speech services not configured, so the audio was stored but not analysed; "
                "a sample transcript for this language/state is used instead.",
    }


def translate_to_en(text: str, language: str) -> dict:
    if language == "en":
        return {"text_en": text, "mode": "real", "provider": "none (already English)"}
    if google_speech.configured():
        try:
            out, _ = google_speech.translate(text, "en", language)
            return {"text_en": out, "mode": "real", "provider": "Cloud Translation"}
        except Exception as exc:  # noqa: BLE001
            log.warning("Translation API failed, trying fallback: %s", exc)
    if gemini.is_configured():
        try:
            prompt = render(gemini.load_prompt("translate", "v1"), language=language, text=text)
            out, _ = gemini.generate_structured(prompt, Translation, "translate_v1")
            return {"text_en": out.text_en, "mode": "real", "provider": "Gemini translation"}
        except Exception as exc:  # noqa: BLE001
            log.warning("Gemini translation failed: %s", exc)
    fx = find_fixture(text)
    if fx:
        return {"text_en": fx["text_en"], "mode": "demo", "provider": "demo fixture translation"}
    return {"text_en": text, "mode": "demo", "provider": "untranslated",
            "note": "Demo mode: translation not configured; original text kept."}


# ------------------------------------------------------------------------------------ extraction
VULNERABLE = {
    "children": ["children", "child", "kids", "बच्चे", "बच्चों", "పిల్లల", "పిల్లలు"],
    "women": ["women", "औरतों", "महिला", "మహిళలు"],
    "elderly": ["elderly", "old people", "बुजुर्ग", "వృద్ధులు"],
    "pregnant women": ["pregnant", "delivery", "deliveries", "प्रसव", "गर्भवती"],
    "students": ["students", "छात्र", "విద్యార్థులు"],
    "farmers": ["farmers", "crops", "किसान", "రైతులు", "పంటలు"],
    "girls": ["girls", "लड़कियाँ", "लड़कियां"],
    "persons with disabilities": ["disabled", "wheelchair", "दिव्यांग"],
}
SEASONS = {
    "monsoon": ["monsoon", "rain", "flood", "बरसात", "बारिश", "बाढ़", "వర్ష"],
    "summer": ["summer", "गर्मी", "వేసవి"],
}
NEGATIVE = ["no ", "not ", "cannot", "broken", "dry", "dried", "cut off", "overflow", "नहीं", "खराब", "टूट",
            "లేదు", "ఎండిపో", "దొరకడం లేదు"]
CRITICAL = ["died", "death", "accident", "collapsed", "मौत", "हादसा", "మరణ", "ప్రమాదం"]
BENEFICIARY_RE = re.compile(
    r"(\d[\d,]*)\s*(people|persons|families|households|residents|workers|students|office workers|"
    r"परिवार|लोग|కుటుంబాలు|మంది)", re.IGNORECASE)


def _hits(text: str, words: list[str]) -> int:
    return sum(1 for w in words if w.lower() in text)


def _weighted_hits(text: str, words: list[str]) -> int:
    """Longer (more specific) keywords count more, e.g. Telugu 'సాగునీరు' (irrigation) beats 'నీరు' (water)."""
    return sum(len(w) for w in words if w.lower() in text)


def rule_extract(text_original: str, text_en: str, gazetteer: list[tuple[str, str, str]]) -> RequestExtraction:
    """Transparent keyword extractor used only in demo mode. gazetteer: (match_text, canonical, type)."""
    blob = f" {text_original.lower()} {text_en.lower()} "
    best, best_hits, best_sub = "other", 0, "general"
    for cid, cat in taxonomy.categories().items():
        hits, first_sub = 0, None
        for sub, words in cat["sub_keywords"].items():
            h = _weighted_hits(blob, words)
            if h and first_sub is None:
                first_sub = sub
            hits += h
        if hits > best_hits:
            best, best_hits, best_sub = cid, hits, first_sub or "general"
    mentions, seen = [], set()
    for match_text, canonical, typ in gazetteer:
        if match_text.lower() in blob and canonical not in seen:
            seen.add(canonical)
            mentions.append(LocationMention(text=canonical, type=typ))  # type: ignore[arg-type]
    vulnerable = [g for g, words in VULNERABLE.items() if _hits(blob, words)]
    season = next((s for s, words in SEASONS.items() if _hits(blob, words)), None)
    negative = _hits(blob, NEGATIVE) > 0
    if _hits(blob, CRITICAL):
        urgency, reason = "critical", "Mentions risk to life or safety"
    elif negative and (vulnerable or season):
        urgency, reason = "high", "Loss of essential access affecting " + (", ".join(vulnerable) or f"people in {season}")
    elif negative:
        urgency, reason = "medium", "Essential service missing or not working"
    else:
        urgency, reason = "low", "No loss of access described"
    m = BENEFICIARY_RE.search(blob)
    beneficiaries = int(m.group(1).replace(",", "")) if m else None
    confidence = min(0.85, 0.45 + (0.15 if best_hits else 0) + (0.1 if best_hits > 8 else 0) + (0.15 if mentions else 0))
    missing = []
    if not mentions:
        missing.append("location not stated")
    elif not any(mn.type in ("block", "mandal", "district") for mn in mentions):
        missing.append("block/district not stated")
    if best == "other":
        missing.append("type of infrastructure not clear")
    translated = normalise(text_en) != normalise(text_original)
    summary = text_en.strip() if (translated or text_en.isascii()) else (
        f"{taxonomy.label(best)} request (untranslated in demo mode): {text_original.strip()[:140]}")
    return RequestExtraction(
        category=best, sub_category=best_sub, summary_en=summary[:300], location_mentions=mentions,  # type: ignore[arg-type]
        urgency=urgency, urgency_reason=reason, est_beneficiaries=beneficiaries,  # type: ignore[arg-type]
        vulnerable_groups=vulnerable, seasonality=season, sentiment=-0.5 if negative else -0.1,
        confidence=round(confidence, 2), missing_information=missing,
        requires_clarification=confidence < CLARIFY_THRESHOLD or not mentions,
    )


def guard(ex: RequestExtraction, text_original: str, text_en: str) -> RequestExtraction:
    """Post-validation: never keep numbers that are not in the citizen's words; enforce clarification."""
    if ex.est_beneficiaries is not None:
        digits = re.findall(r"\d[\d,]*", f"{text_original} {text_en}")
        if str(ex.est_beneficiaries) not in {d.replace(",", "") for d in digits}:
            ex.est_beneficiaries = None
            ex.missing_information.append("beneficiary count removed: not stated by the citizen")
    if ex.confidence < CLARIFY_THRESHOLD:
        ex.requires_clarification = True
    return ex


def extract(text_original: str, text_en: str, language: str, channel: str, state: str | None,
            district: str | None, gazetteer: list[tuple[str, str, str]]) -> tuple[RequestExtraction, Provenance]:
    prompt_version = "_".join(EXTRACT_PROMPT)
    if gemini.is_configured():
        try:
            prompt = render(
                gemini.load_prompt(*EXTRACT_PROMPT), taxonomy=taxonomy.prompt_listing(), channel=channel,
                language=language, state=state or "unknown", district=district or "unknown",
                text_original=text_original, text_en=text_en,
            )
            ex, prov = gemini.generate_structured(prompt, RequestExtraction, prompt_version)
            return guard(ex, text_original, text_en), Provenance(**prov.model_dump(), mode="real")
        except Exception as exc:  # noqa: BLE001
            log.warning("Gemini extraction failed, falling back to demo extractor: %s", exc)
    fx = find_fixture(text_original) or find_fixture(text_en)
    if fx:
        ex = RequestExtraction(**fx["expected"])
        return guard(ex, text_original, text_en), Provenance(
            model_name="demo-fixture", model_version=fx["id"], prompt_version=prompt_version,
            generated_at=_now(), mode="demo",
            note="Demo mode: hand-authored fixture output (Gemini not configured).")
    ex = rule_extract(text_original, text_en, gazetteer)
    return guard(ex, text_original, text_en), Provenance(
        model_name="demo-rule-extractor", model_version="rules-v1", prompt_version=prompt_version,
        generated_at=_now(), mode="demo",
        note="Demo mode: keyword rules over the fixed taxonomy (Gemini not configured).")
