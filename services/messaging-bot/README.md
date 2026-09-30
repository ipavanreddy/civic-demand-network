# messaging-bot

Telegram bot webhook (Node.js allowed here)

Starts as a router/module in `services/api/app/` (e.g. `app/messaging_bot/`).
Split into its own Cloud Run service here only if it needs separate scaling or runtime.

Implemented in `services/api/` as `app/routers/webhooks.py`, `app/integrations/telegram.py`.
