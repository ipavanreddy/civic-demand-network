"""Cloud Speech-to-Text, Translation and Text-to-Speech via REST (API key in GOOGLE_API_KEY).

These are thin adapters: callers check `configured()` and fall back to Gemini or demo mode.
"""
from __future__ import annotations

import base64

import httpx

from app.config import settings

BCP47 = {"en": "en-IN", "hi": "hi-IN", "te": "te-IN"}
TIMEOUT = 30.0


def configured() -> bool:
    return bool(settings.google_api_key)


def _encoding(content_type: str) -> dict:
    ct = (content_type or "").lower()
    if "webm" in ct:
        return {"encoding": "WEBM_OPUS", "sampleRateHertz": 48000}
    if "ogg" in ct:
        return {"encoding": "OGG_OPUS", "sampleRateHertz": 48000}
    if "mpeg" in ct or "mp3" in ct:
        return {"encoding": "MP3", "sampleRateHertz": 16000}
    if "flac" in ct:
        return {"encoding": "FLAC"}
    return {}  # WAV/LINEAR16: header is read by the API


def speech_to_text(audio: bytes, content_type: str, language: str) -> tuple[str, str]:
    """Return (transcript, language). Uses v1p1beta1 for MP3 support and alternative languages."""
    primary = BCP47.get(language, "hi-IN")
    body = {
        "config": {
            "languageCode": primary,
            "alternativeLanguageCodes": [c for c in BCP47.values() if c != primary],
            "enableAutomaticPunctuation": True,
            **_encoding(content_type),
        },
        "audio": {"content": base64.b64encode(audio).decode()},
    }
    res = httpx.post(
        "https://speech.googleapis.com/v1p1beta1/speech:recognize",
        params={"key": settings.google_api_key}, json=body, timeout=TIMEOUT,
    )
    res.raise_for_status()
    results = res.json().get("results", [])
    transcript = " ".join(r["alternatives"][0]["transcript"] for r in results if r.get("alternatives"))
    detected = results[0].get("languageCode", primary) if results else primary
    lang = next((k for k, v in BCP47.items() if v.lower() == detected.lower()), language)
    return transcript.strip(), lang


def translate(text: str, target: str = "en", source: str | None = None) -> tuple[str, str]:
    """Return (translated_text, detected_source_language)."""
    body = {"q": text, "target": target, "format": "text"}
    if source:
        body["source"] = source
    res = httpx.post(
        "https://translation.googleapis.com/language/translate/v2",
        params={"key": settings.google_api_key}, json=body, timeout=TIMEOUT,
    )
    res.raise_for_status()
    t = res.json()["data"]["translations"][0]
    return t["translatedText"], t.get("detectedSourceLanguage", source or "")


def text_to_speech(text: str, language: str) -> str:
    """Return base64 MP3 audio."""
    body = {
        "input": {"text": text},
        "voice": {"languageCode": BCP47.get(language, "en-IN")},
        "audioConfig": {"audioEncoding": "MP3"},
    }
    res = httpx.post(
        "https://texttospeech.googleapis.com/v1/text:synthesize",
        params={"key": settings.google_api_key}, json=body, timeout=TIMEOUT,
    )
    res.raise_for_status()
    return res.json()["audioContent"]
