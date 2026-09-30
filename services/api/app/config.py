from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")

    project_name: str = "civic-demand-network"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-flash-latest"
    gemini_embedding_model: str = "gemini-embedding-001"
    google_genai_use_vertexai: bool = False
    google_cloud_project: str = ""
    google_cloud_location: str = "asia-south1"
    # API key for Cloud Speech-to-Text, Translation and Text-to-Speech REST APIs
    google_api_key: str = ""
    use_bigquery: bool = False
    bigquery_dataset: str = "civic_demand_network"
    gcs_bucket: str = ""
    firebase_project_id: str = ""
    maps_api_key: str = ""
    telegram_bot_token: str = ""
    cors_origins: str = "http://localhost:3010,http://localhost:3011"
    # Salt for pseudonymous citizen IDs (hashed phone / chat IDs)
    citizen_id_salt: str = "janvaani-demo-salt"
    # Local JSON file for runtime state in demo mode ("" disables persistence)
    local_state_path: str = str(REPO_ROOT / "services" / "api" / ".data" / "runtime_state.json")
    data_dir: str = str(REPO_ROOT / "data")
    ai_dir: str = str(REPO_ROOT / "ai")


settings = Settings()
