"""Telegram Bot API adapter (TELEGRAM_BOT_TOKEN). Without a token, replies are returned to the
caller instead of being delivered (demo mode)."""
from __future__ import annotations

import logging

import httpx

from app.config import settings

log = logging.getLogger(__name__)


def configured() -> bool:
    return bool(settings.telegram_bot_token)


def _url(method: str) -> str:
    return f"https://api.telegram.org/bot{settings.telegram_bot_token}/{method}"


def send_message(chat_id: int | str, text: str) -> bool:
    if not configured():
        return False
    try:
        httpx.post(_url("sendMessage"), json={"chat_id": chat_id, "text": text}, timeout=10.0).raise_for_status()
        return True
    except httpx.HTTPError as exc:
        log.warning("telegram sendMessage failed: %s", exc)
        return False


def download_file(file_id: str) -> bytes | None:
    if not configured():
        return None
    try:
        info = httpx.get(_url("getFile"), params={"file_id": file_id}, timeout=10.0).json()
        path = info["result"]["file_path"]
        res = httpx.get(f"https://api.telegram.org/file/bot{settings.telegram_bot_token}/{path}", timeout=30.0)
        res.raise_for_status()
        return res.content
    except (httpx.HTTPError, KeyError) as exc:
        log.warning("telegram file download failed: %s", exc)
        return None
