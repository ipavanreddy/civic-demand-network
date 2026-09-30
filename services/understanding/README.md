# understanding

Gemini request extraction to schema-validated JSON

Starts as a router/module in `services/api/app/` (e.g. `app/understanding/`).
Split into its own Cloud Run service here only if it needs separate scaling or runtime.

Implemented in `services/api/` as `app/pipeline/understanding.py` (prompt `ai/prompts/extract_v1.md`).
