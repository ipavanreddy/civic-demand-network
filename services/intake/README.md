# intake

Request intake (text, voice, photo) and confirmation

Starts as a router/module in `services/api/app/` (e.g. `app/intake/`).
Split into its own Cloud Run service here only if it needs separate scaling or runtime.

Implemented in `services/api/` as `app/pipeline/intake.py`, `app/routers/requests.py`.
