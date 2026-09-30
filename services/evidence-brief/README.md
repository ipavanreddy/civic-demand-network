# evidence-brief

Gemini evidence briefs for ranked recommendations

Starts as a router/module in `services/api/app/` (e.g. `app/evidence_brief/`).
Split into its own Cloud Run service here only if it needs separate scaling or runtime.

Implemented in `services/api/` as `app/pipeline/brief.py` (prompt `ai/prompts/evidence_brief_v1.md`).
