# JanVaani: Multilingual Citizen Development Request Platform

Build with AI (Google) hackathon, Track 1. Full spec: [docs/PRD.md](docs/PRD.md).

## Core journey (build this first; PRD §57)

```text
Request (text/voice)
 ↓
Gemini Extraction
 ↓
Location Resolution
 ↓
Clustering
 ↓
Data Fusion + Priority Score
 ↓
Evidence Brief
```

**Headline score:** Priority Score (Demand 30 · Infra gap 30 · Vulnerability 20 · Trend 10 · − Investment coverage 10)
**Users:** Citizen (`apps/citizen-web`) · Planning Officer (`apps/officer-dashboard`)
**Languages:** English, Hindi, Telugu
**Demo states:** Bihar (bridge/roads), Andhra Pradesh (drinking water), Maharashtra urban ward (transport)

## Stack

Next.js + TypeScript + Tailwind + shadcn/ui (pnpm workspace) · FastAPI on Cloud Run (uv, Python 3.12) ·
Gemini API / Vertex AI · BigQuery · Firebase · Cloud Storage · Google Maps Platform ·
Speech-to-Text / Text-to-Speech / Translation · region `asia-south1`.

## Run the demo (no keys needed)

```bash
pnpm install
(cd services/api && uv sync)
for a in apps/*; do [ -f $a/.env.local ] || cp $a/.env.example $a/.env.local; done
[ -f .env ] || cp .env.example .env       # keys optional; empty = demo mode

pnpm dev:api                 # http://localhost:8010  (OpenAPI docs at /docs)
pnpm dev:citizen-web         # http://localhost:3010  Citizen app (EN / हिन्दी / తెలుగు)
pnpm dev:officer-dashboard   # http://localhost:3011  Planning Officer dashboard
```

Without keys everything runs in **demo mode**: both apps show an amber *"Demo mode · sample data"*
badge (click it to see which integration is real vs demo), and every AI output is labelled with its
`model_name` (e.g. `demo-fixture`, `demo-rule-extractor`, `demo-template`).

`POST /api/system/reset` drops runtime changes (new requests, decisions, weight changes) kept in
`services/api/.data/runtime_state.json` (git-ignored).

### 5-minute demo script (PRD §44)

1. **Citizen app → Demo scenarios → "A · BR · हिन्दी"** (or *Speak* → record/upload any audio: in demo
   mode the audio is stored and the Hindi sample transcript is used). Send.
   Shows transcription, English translation, extracted category / urgency / vulnerable groups,
   location resolved to a sample LGD code + H3 cell, and a Hindi confirmation (▶ *Play* speaks it).
2. **Confirm** → the request joins the existing Sonbarsa bridge cluster (147 requests, unique
   citizens, representative quotes). Try **"A-clarify"** for the ambiguous *Rampur* clarification flow.
3. **Officer dashboard** → India → Bihar → Gaya: hotspot map (H3 hexagons + cluster circles), KPIs,
   data freshness, ranked recommendations with factor bars.
4. **Policy lens**: move *Vulnerability* up → *Apply & re-rank* → arrows show rank changes; the change
   is logged (audit list under the sliders).
5. **Generate evidence brief**: demand evidence, cited data evidence, investments, uncertainties, next
   step, plus a *number check* proving every number exists in the input data. Then a **human
   decision** (approve for field verification / defer / reject); the citizen's status (*Check status*)
   changes to *Recommended / अनुशंसित*.
6. **Interoperability tab**: switch Bihar ↔ Andhra Pradesh ↔ Maharashtra to see raw state records →
   adapter config → the same canonical schema. Scenario **B** (Telugu, drinking water) and **C**
   (English, Pune transport) run through the identical pipeline.

Telegram (demo): `curl -X POST localhost:8010/api/webhooks/messaging -H 'content-type: application/json'
-d '{"message":{"chat":{"id":1},"text":"<request text>"}}'` returns the reply the bot would send.

## Turning on real integrations

Each integration sits behind one adapter; setting its env var is the only step needed.

| Env var (repo-root `.env` unless noted) | Switches on | Adapter | Demo-mode fallback |
|---|---|---|---|
| `GEMINI_API_KEY` (or `GOOGLE_GENAI_USE_VERTEXAI=true` + `GOOGLE_CLOUD_PROJECT` + ADC) | Gemini request extraction (`ai/prompts/extract_v1.md`), evidence briefs (`evidence_brief_v1.md`), embeddings for clustering, audio transcription / translation fallback | `app/ai/gemini.py` | Hand-authored fixtures (`ai/evaluation/fixtures/`), keyword rule extractor, template brief, bag-of-words similarity |
| `GEMINI_MODEL`, `GEMINI_EMBEDDING_MODEL` | Model IDs (never hard-coded) | `app/config.py` | – |
| `GOOGLE_API_KEY` | Cloud Speech-to-Text, Translation, Text-to-Speech (REST) | `app/integrations/google_speech.py` | Gemini (if configured), else sample transcript / fixture translation / browser speech synthesis |
| `MAPS_API_KEY` | Google Geocoding for unmatched place names | `app/integrations/maps.py` | Local gazetteer (exact / fuzzy / pin) |
| `NEXT_PUBLIC_MAPS_API_KEY` (`apps/officer-dashboard/.env.local`) | Google Maps hotspot map | `components/map-google.tsx` | Leaflet + OpenStreetMap tiles |
| `USE_BIGQUERY=true` + `GOOGLE_CLOUD_PROJECT` (+ ADC) | Streams requests, assignments, briefs, weight changes, decisions to BigQuery (`infrastructure/bigquery/schema.sql`) | `app/integrations/bigquery_sink.py` | In-memory store + local JSON file |
| `GCS_BUCKET` | Voice notes stored in Cloud Storage | `app/integrations/media.py` | `services/api/.data/media/` |
| `TELEGRAM_BOT_TOKEN` | Telegram replies + voice-note download (`setWebhook` to `/api/webhooks/messaging`) | `app/integrations/telegram.py` | Reply returned in the HTTP response |

Firebase (citizen auth / realtime status) is not wired yet (see *Known gaps*).

## How it works

```text
text / voice ─► Speech-to-Text ─► Translation (original kept) ─► Gemini extraction (schema-validated,
numbers not stated by the citizen are dropped) ─► location resolution (sample LGD code + H3 res-7,
clarification if ambiguous) ─► citizen confirms / corrects ─► clustering (same category + same /
neighbouring place + semantic similarity) ─► data fusion (demographics, infra gap, investment; each
value with source + year) ─► deterministic Priority Score ─► Gemini evidence brief from structured
data only ─► number-grounding check ─► human decision ─► citizen status
```

**Priority Score** (`services/api/app/pipeline/scoring.py`):
`100 × (wD·Demand + wG·Gap + wV·Vulnerability + wT·Trend − wI·Investment) / (wD+wG+wV+wT)`, defaults
30/30/20/10/10. Demand = recency-weighted *unique* citizens per 10k population (repeat submissions do
not inflate it), normalised to the top cluster in the selected geography; Trend = last 30 days vs the
30 before, normalised in scope; Gap / Vulnerability / Investment coverage are population-weighted 0–1
shares. A missing gap indicator uses a neutral 0.5 and is flagged in the breakdown and the brief.

**Interoperability**: `data/adapters/{BR,AP,MH}.json` map three differently shaped state files
(Hindi-transliterated CSV, nested JSON with SC/ST split and households, urban ward CSV with slum share)
into the canonical schema (`data/schemas/*.json`). A new state = new config + raw files, no code.

## Data

`python3 data/transformations/generate_sample.py` regenerates all synthetic sample data
deterministically (fixed seed, no AI). See `data/sample/manifest.json` for source / timestamp /
version / scope / synthetic flags. JSON Schemas: `cd services/api && uv run python -m app.export_schemas`.

## Checks

```bash
pnpm test:api   # pytest: scoring, adapters, location, extraction guards, grounding, API, demo journey
pnpm lint
pnpm build
```

## Known gaps

- Firebase auth, officer authentication/RBAC and WhatsApp are not implemented; the two roles are
  separate apps without login.
- Photo upload, impact view and demand forecasting (PRD Priority 4) are not built.
- The in-memory store is the serving layer; BigQuery is a write-only sink (no BigQuery vector search yet).
- Real Gemini / Speech / Maps paths are implemented but untested without keys; `tests/test_understanding.py`
  has a live Gemini check that runs only when `GEMINI_API_KEY` is set.
- All figures are synthetic; LGD codes are sample codes.

## Layout

| Path | Purpose |
|---|---|
| `apps/citizen-web/` | Citizen app |
| `apps/officer-dashboard/` | Planning Officer dashboard |
| `services/api/` | FastAPI gateway: `app/pipeline/` (intake, understanding, location, clustering, fusion, scoring, brief), `app/routers/`, `app/interop/` (state adapters), `app/integrations/` (Google / Telegram adapters) |
| `services/intake/` | Request intake (text, voice, photo) and confirmation |
| `services/messaging-bot/` | Telegram bot webhook (Node.js allowed here) |
| `services/understanding/` | Gemini request extraction to schema-validated JSON |
| `services/location/` | Free-text location → LGD code resolution (Maps Geocoding) |
| `services/clustering-scoring/` | Demand clustering (embeddings) and Priority Score |
| `services/evidence-brief/` | Gemini evidence briefs for ranked recommendations |
| `services/localization/` | Speech-to-Text, Text-to-Speech, Translation |
| `ai/` | Prompts, JSON schemas, models, evaluation |
| `data/` | Canonical schema, state adapters, sample data |
| `infrastructure/` | Cloud Run, BigQuery, Firebase config |
| `docs/` | PRD and architecture notes |
