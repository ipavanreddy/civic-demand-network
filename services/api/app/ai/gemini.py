"""Gemini orchestration: structured context in, schema-validated JSON out, versioned."""
import logging
import os
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

from google import genai
from google.genai import types
from pydantic import BaseModel

from app import runtime_health
from app.config import settings

log = logging.getLogger(__name__)
PROMPTS_DIR = Path(settings.ai_dir) / "prompts"


class AIProvenance(BaseModel):
    model_name: str
    model_version: str
    prompt_version: str
    generated_at: datetime


def is_configured() -> bool:
    """True when real Gemini calls are possible (API key, or Vertex AI with a project)."""
    if settings.google_genai_use_vertexai:
        return bool(settings.google_cloud_project)
    return bool(settings.gemini_api_key)


@lru_cache
def client() -> genai.Client:
    if settings.google_genai_use_vertexai:
        # google-genai treats a GOOGLE_API_KEY env var as a Gemini key, which overrides Vertex AI
        # (service-account) auth. Cloud APIs use GOOGLE_CLOUD_API_KEY instead; drop any stray one.
        if os.environ.pop("GOOGLE_API_KEY", None):
            log.warning("GOOGLE_API_KEY ignored: Gemini runs via Vertex AI (use GOOGLE_CLOUD_API_KEY for Cloud APIs)")
        return genai.Client(
            vertexai=True,
            project=settings.google_cloud_project,
            location=settings.google_cloud_location,
        )
    return genai.Client(api_key=settings.gemini_api_key)


def load_prompt(name: str, version: str) -> str:
    """Load ai/prompts/{name}_{version}.md."""
    return (PROMPTS_DIR / f"{name}_{version}.md").read_text()


def generate_structured[T: BaseModel](
    prompt: str,
    schema: type[T],
    prompt_version: str,
    parts: list[types.Part] | None = None,
) -> tuple[T, AIProvenance]:
    """Call Gemini with a response schema and return the validated object plus provenance."""
    try:
        response = client().models.generate_content(
            model=settings.gemini_model,
            contents=[prompt, *(parts or [])],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                thinking_config=(types.ThinkingConfig(thinking_budget=settings.gemini_thinking_budget)
                                 if settings.gemini_thinking_budget is not None else None),
            ),
        )
        result = schema.model_validate_json(response.text)
    except Exception as exc:
        runtime_health.record("gemini", False, exc)
        raise
    runtime_health.record("gemini", True)
    provenance = AIProvenance(
        model_name=settings.gemini_model,
        model_version=response.model_version or settings.gemini_model,
        prompt_version=prompt_version,
        generated_at=datetime.now(UTC),
    )
    return result, provenance


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts with the configured Gemini embedding model (settings.gemini_embedding_model)."""
    try:
        result = client().models.embed_content(model=settings.gemini_embedding_model, contents=texts)
    except Exception as exc:
        runtime_health.record("embeddings", False, exc)
        raise
    runtime_health.record("embeddings", True)
    return [list(e.values or []) for e in (result.embeddings or [])]
