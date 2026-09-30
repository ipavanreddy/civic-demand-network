"""Language / voice endpoints (PRD §37)."""
from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel, Field

from app.models import Language
from app.pipeline import intake, understanding

router = APIRouter(prefix="/api", tags=["language"])


class TranslateBody(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    language: Language


class SpeakBody(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    language: Language


@router.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...), language: Language = Form("hi"),
                         state: str | None = Form(None)) -> dict:
    return understanding.speech_to_text(await audio.read(), audio.content_type or "audio/webm", language, state)


@router.post("/translate")
def translate(body: TranslateBody) -> dict:
    return understanding.translate_to_en(body.text, body.language)


@router.post("/text-to-speech")
def text_to_speech(body: SpeakBody) -> dict:
    return intake.speak(body.text, body.language)
