"""External integrations. Each one is real when its env var is set and falls back to a clearly
labelled demo mode otherwise. `status()` is the single place the UI reads to show demo badges."""
from __future__ import annotations

from app import runtime_health as health
from app.ai import gemini
from app.config import settings


def status() -> dict:
    g = gemini.is_configured()
    speech_key = bool(settings.google_cloud_api_key)

    def item(real: bool, env: str, demo: str, real_detail: str, key: str = "") -> dict:
        out = {"mode": "real" if real else "demo", "env": env, "detail": real_detail if real else demo}
        last = health.last(key) if (real and key) else None
        if last:
            out["last_call"] = last
            if not last["ok"]:  # configured, but the latest call failed and the demo fallback was used
                out["mode"] = "fallback"
                out["detail"] = f"{real_detail} failing ({last['error']}); using: {demo}"
        return out

    integrations = {
        "gemini": item(g, "GEMINI_API_KEY or GOOGLE_GENAI_USE_VERTEXAI+GOOGLE_CLOUD_PROJECT",
                       "Hand-authored fixtures + rule-based extractor; template evidence briefs",
                       f"Gemini {settings.gemini_model}" + (" via Vertex AI" if settings.google_genai_use_vertexai else ""),
                       "gemini"),
        "embeddings": item(g, "GEMINI_API_KEY or Vertex AI", "Bag-of-words cosine similarity",
                           f"Gemini embeddings {settings.gemini_embedding_model}", "embeddings"),
        "speech_to_text": item(speech_key or g, "GOOGLE_CLOUD_API_KEY (Cloud Speech-to-Text) or Gemini",
                               "Sample transcript per scenario (audio not analysed)",
                               "Cloud Speech-to-Text" if speech_key else "Gemini audio transcription", "speech_to_text"),
        "translation": item(speech_key or g, "GOOGLE_CLOUD_API_KEY (Cloud Translation) or Gemini",
                            "Fixture translations; otherwise original text kept",
                            "Cloud Translation" if speech_key else "Gemini translation", "translation"),
        "text_to_speech": item(speech_key, "GOOGLE_CLOUD_API_KEY (Cloud Text-to-Speech)",
                               "Browser speech synthesis in the citizen app", "Cloud Text-to-Speech", "text_to_speech"),
        "geocoding": item(bool(settings.maps_api_key), "MAPS_API_KEY",
                          "Local sample gazetteer only (exact/fuzzy/pin)", "Google Maps Geocoding API", "geocoding"),
        "bigquery": item(settings.use_bigquery and bool(settings.google_cloud_project),
                         "USE_BIGQUERY=true + GOOGLE_CLOUD_PROJECT",
                         "In-memory store + local JSON file", f"BigQuery dataset {settings.bigquery_dataset} (analytics sink; serving from memory)", "bigquery"),
        "storage": item(bool(settings.gcs_bucket), "GCS_BUCKET", "Local disk (services/api/.data/media)",
                        f"gs://{settings.gcs_bucket}", "storage"),
        "telegram": item(bool(settings.telegram_bot_token), "TELEGRAM_BOT_TOKEN",
                         "Webhook returns the reply in the HTTP response (not delivered)", "Telegram Bot API", "telegram"),
    }
    return {
        "demo_mode": any(v["mode"] != "real" for v in integrations.values()),
        "live_count": sum(v["mode"] == "real" for v in integrations.values()),
        "total_count": len(integrations),
        "integrations": integrations,
    }
