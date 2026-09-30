# localization

Speech-to-Text, Text-to-Speech, Translation

Starts as a router/module in `services/api/app/` (e.g. `app/localization/`).
Split into its own Cloud Run service here only if it needs separate scaling or runtime.

Implemented in `services/api/` as `app/integrations/google_speech.py`, `app/pipeline/messages.py`, `app/routers/language.py`.
