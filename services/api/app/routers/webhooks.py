"""Messaging bot webhook (PRD §9, §37: POST /api/webhooks/messaging). Telegram update format.

Set the webhook with: https://api.telegram.org/bot<TOKEN>/setWebhook?url=<API_URL>/api/webhooks/messaging
Commands: /state BR|AP|MH  (set the citizen's state), /status REQ-XXXXXX.
"""
from __future__ import annotations

import re

from fastapi import APIRouter

from app.integrations import telegram
from app.pipeline import intake, understanding
from app.store import get_store

router = APIRouter(prefix="/api/webhooks", tags=["messaging"])
STATE_BY_LANGUAGE = {"hi": "BR", "te": "AP", "en": "MH"}


def detect_language(text: str) -> str:
    if re.search(r"[ఀ-౿]", text):
        return "te"
    if re.search(r"[ऀ-ॿ]", text):
        return "hi"
    return "en"


def _reply(chat_id, text: str, result: dict | None = None) -> dict:
    delivered = telegram.send_message(chat_id, text)
    return {"ok": True, "reply": text, "delivered": delivered,
            "mode": "real" if telegram.configured() else "demo", "result": result}


@router.post("/messaging")
def messaging_webhook(update: dict) -> dict:
    store = get_store()
    msg = update.get("message") or update.get("edited_message") or {}
    chat_id = (msg.get("chat") or {}).get("id")
    if chat_id is None:
        return {"ok": True, "ignored": True}
    chat = store.telegram_chats.setdefault(str(chat_id), {})
    text = (msg.get("text") or "").strip()

    if text.startswith("/start"):
        return _reply(chat_id, "JanVaani: send your development request by text or voice note (English / हिन्दी / తెలుగు). "
                               "Set your state with /state BR, /state AP or /state MH.")
    if text.startswith("/state"):
        code = text.split(maxsplit=1)[1].strip().upper() if len(text.split()) > 1 else ""
        if code not in store.states:
            return _reply(chat_id, f"Unknown state. Choose one of: {', '.join(store.states)}")
        chat["state"] = code
        return _reply(chat_id, f"State set to {store.states[code].config['name']}.")
    if text.startswith("/status"):
        rid = text.split(maxsplit=1)[1].strip() if len(text.split()) > 1 else chat.get("last_request", "")
        req = store.requests.get(rid)
        if not req:
            return _reply(chat_id, "Request not found.")
        v = intake.view(store, req)
        return _reply(chat_id, v["message"]["text"], v)

    citizen_ref = f"telegram:{chat_id}"
    if chat.get("pending") and text:
        # the previous message needed clarification: treat this text as the location answer
        v = intake.confirm(store, chat.pop("pending"), location_text=text)
    elif msg.get("voice"):
        lang = chat.get("language", "hi")
        audio = telegram.download_file(msg["voice"]["file_id"]) or b""
        speech = understanding.speech_to_text(audio, msg["voice"].get("mime_type", "audio/ogg"), lang, chat.get("state"))
        v = intake.create(store, text=speech["transcript"], language=speech["language"], channel="telegram",
                          citizen_ref=citizen_ref, state=chat.get("state"), speech=speech, auto_confirm=True)
    elif text:
        lang = detect_language(text)
        chat["language"] = lang
        state = chat.get("state") or STATE_BY_LANGUAGE[lang]
        v = intake.create(store, text=text, language=lang, channel="telegram", citizen_ref=citizen_ref,
                          state=state, auto_confirm=True)
    else:
        return _reply(chat_id, "Please send text or a voice note.")
    rid = v["request"]["request_id"]
    chat["last_request"] = rid
    if v["needs_clarification"]:
        chat["pending"] = rid
    return _reply(chat_id, f"{v['message']['text']} ({rid})", v)
