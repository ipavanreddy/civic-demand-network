import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import integrations
from app.config import settings
from app.routers import (
    intelligence,
    language,
    recommendations,
    requests,
    states,
    system,
    webhooks,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Load sample data now, and warm Gemini embeddings in the background (real mode only).
    from app.pipeline import clustering
    from app.store import get_store

    store = get_store()
    threading.Thread(target=clustering.warm_embeddings, args=(store,), daemon=True).start()
    yield


app = FastAPI(title=settings.project_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    # e.g. https://.*\.vercel\.app to allow Vercel preview deployments
    allow_origin_regex=settings.cors_origin_regex or None,
    allow_methods=["*"],
    allow_headers=["*"],
)
for r in (requests, language, intelligence, recommendations, states, webhooks, system):
    app.include_router(r.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "project": settings.project_name, "model": settings.gemini_model,
            "demo_mode": integrations.status()["demo_mode"]}
