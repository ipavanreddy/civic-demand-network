"""External integrations. Each one is real when its env var is set and falls back to a clearly
labelled demo mode otherwise. `status()` is the single place the UI reads to show demo badges."""
from __future__ import annotations

from app.ai import gemini
from app.config import settings


def status() -> dict:
    g = gemini.is_configured()
    speech_key = bool(settings.google_api_key)

    def item(real: bool, env: str, demo: str, real_detail: str) -> dict:
        return {"mode": "real" if real else "demo", "env": env, "detail": real_detail if real else demo}

    integrations = {
        "gemini": item(g, "GEMINI_API_KEY or GOOGLE_GENAI_USE_VERTEXAI+GOOGLE_CLOUD_PROJECT",
                       "Hand-authored fixtures + rule-based extractor; template evidence briefs",
                       f"Gemini {settings.gemini_model}"),
        "embeddings": item(g, "GEMINI_API_KEY", "Bag-of-words cosine similarity",
                           f"Gemini embeddings {settings.gemini_embedding_model}"),
        "speech_to_text": item(speech_key or g, "GOOGLE_API_KEY (Cloud Speech-to-Text) or Gemini",
                               "Sample transcript per scenario (audio not analysed)",
                               "Cloud Speech-to-Text" if speech_key else "Gemini audio transcription"),
        "translation": item(speech_key or g, "GOOGLE_API_KEY (Cloud Translation) or Gemini",
                            "Fixture translations; otherwise original text kept",
                            "Cloud Translation" if speech_key else "Gemini translation"),
        "text_to_speech": item(speech_key, "GOOGLE_API_KEY (Cloud Text-to-Speech)",
                               "Browser speech synthesis in the citizen app", "Cloud Text-to-Speech"),
        "geocoding": item(bool(settings.maps_api_key), "MAPS_API_KEY",
                          "Local sample gazetteer only (exact/fuzzy/pin)", "Google Maps Geocoding API"),
        "bigquery": item(settings.use_bigquery and bool(settings.google_cloud_project),
                         "USE_BIGQUERY=true + GOOGLE_CLOUD_PROJECT",
                         "In-memory store + local JSON file", f"BigQuery dataset {settings.bigquery_dataset}"),
        "storage": item(bool(settings.gcs_bucket), "GCS_BUCKET", "Local disk (services/api/.data/media)",
                        f"gs://{settings.gcs_bucket}"),
        "telegram": item(bool(settings.telegram_bot_token), "TELEGRAM_BOT_TOKEN",
                         "Webhook returns the reply in the HTTP response (not delivered)", "Telegram Bot API"),
    }
    return {
        "demo_mode": any(v["mode"] == "demo" for v in integrations.values()),
        "integrations": integrations,
    }
