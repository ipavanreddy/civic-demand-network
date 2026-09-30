import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")

    project_name: str = "civic-demand-network"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-001"
    # Gemini 2.5 thinking budget in tokens for structured calls; 0 = off (fast; the tasks are
    # schema-constrained extraction/summarisation), -1 = dynamic.
    gemini_thinking_budget: int | None = 0
    google_genai_use_vertexai: bool = False
    google_cloud_project: str = ""
    # Vertex AI location for Gemini. "global" avoids regional 429s; data services stay in asia-south1.
    google_cloud_location: str = "global"
    # Service-account JSON for local dev (Cloud Run uses its attached service account)
    google_application_credentials: str = ""
    # API key for Cloud Speech-to-Text, Translation and Text-to-Speech REST APIs
    google_cloud_api_key: str = ""
    use_bigquery: bool = False
    bigquery_dataset: str = "civic_demand_network"
    gcs_bucket: str = ""
    firebase_project_id: str = ""
    maps_api_key: str = ""
    telegram_bot_token: str = ""
    cors_origins: str = "http://localhost:3010,http://localhost:3011"
    # Optional regex for extra allowed origins, e.g. https://.*\.vercel\.app (Vercel previews)
    cors_origin_regex: str = ""
    # Salt for pseudonymous citizen IDs (hashed phone / chat IDs)
    citizen_id_salt: str = "janvaani-demo-salt"
    # Local JSON file for runtime state in demo mode ("" disables persistence)
    local_state_path: str = str(REPO_ROOT / "services" / "api" / ".data" / "runtime_state.json")
    data_dir: str = str(REPO_ROOT / "data")
    ai_dir: str = str(REPO_ROOT / "ai")


settings = Settings()

# Google client libraries (BigQuery, Cloud Storage, Vertex AI) read ADC from the process environment,
# but pydantic-settings only reads .env into `settings`. Export the key path so local dev uses the
# service account from .env; on Cloud Run the variable is unset and the attached SA is used.
if settings.google_application_credentials and "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials
