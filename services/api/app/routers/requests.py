"""Citizen request endpoints (PRD §37: POST /api/requests, GET /api/requests/:id, POST .../confirm)."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.integrations import media
from app.models import Language
from app.pipeline import intake, understanding
from app.store import get_store

router = APIRouter(prefix="/api/requests", tags=["requests"])


class CreateRequest(BaseModel):
    text: str = Field(min_length=3, max_length=2000)
    language: Language = "en"
    channel: str = "web"
    citizen_ref: str | None = Field(None, description="Demo profile / phone number; stored only as a salted hash")
    state: str | None = None
    district: str | None = None
    lat: float | None = None
    lng: float | None = None


class ConfirmRequest(BaseModel):
    category: str | None = None
    lgd_code: str | None = None
    location_text: str | None = None


@router.post("")
def create_request(body: CreateRequest) -> dict:
    pin = (body.lat, body.lng) if body.lat is not None and body.lng is not None else None
    return intake.create(get_store(), text=body.text, language=body.language, channel=body.channel,
                         citizen_ref=body.citizen_ref, state=body.state, district=body.district, pin=pin)


@router.post("/voice")
async def create_voice_request(
    audio: UploadFile = File(...),
    language: Language = Form("hi"),
    state: str | None = Form(None),
    district: str | None = Form(None),
    citizen_ref: str | None = Form(None),
) -> dict:
    data = await audio.read()
    if not data:
        raise HTTPException(400, "empty audio")
    content_type = audio.content_type or "audio/webm"
    ext = (audio.filename or "voice.webm").rsplit(".", 1)[-1][:5]
    audio_url = media.save(f"{uuid.uuid4().hex}.{ext}", data, content_type)
    speech = understanding.speech_to_text(data, content_type, language, state)
    if not speech["transcript"]:
        raise HTTPException(422, "no speech recognised")
    return intake.create(get_store(), text=speech["transcript"], language=speech["language"], channel="voice",
                         citizen_ref=citizen_ref, state=state, district=district, audio_url=audio_url, speech=speech)


@router.get("/{request_id}")
def get_request(request_id: str) -> dict:
    store = get_store()
    req = store.requests.get(request_id)
    if not req:
        raise HTTPException(404, "request not found")
    return intake.view(store, req)


@router.post("/{request_id}/confirm")
def confirm_request(request_id: str, body: ConfirmRequest | None = None) -> dict:
    store = get_store()
    if request_id not in store.requests:
        raise HTTPException(404, "request not found")
    body = body or ConfirmRequest()
    try:
        return intake.confirm(store, request_id, body.category, body.lgd_code, body.location_text)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
