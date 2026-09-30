# JanVaani: submission pack

Build with AI (Google) hackathon · Track 1 · repo https://github.com/ipavanreddy/civic-demand-network

## Product description (2–3 lines)

> **JanVaani** lets any citizen tell the government what their village or ward needs, by voice, text
> or chat in Hindi, Telugu or English. Gemini on Vertex AI understands each request, maps it to an
> LGD location and groups it with similar requests, and planning officers get a transparent Priority
> Score and a number-checked evidence brief that fuses citizen demand with demographic,
> infrastructure-gap and investment data. One set of state adapters makes Bihar, Andhra Pradesh and
> Maharashtra run on the same platform.

## Live URLs

| Component | URL |
|---|---|
| Citizen app | *to be filled by lead* (Vercel) |
| Planning Officer dashboard | *to be filled by lead* (Vercel) |
| API | https://civic-demand-network-api-847963771142.asia-south1.run.app (`/docs`, `/api/system/status`) |

Before recording: open both apps once (Cloud Run may cold-start), click the header badge and check
it reads *Live AI · 8/9 integrations* with no **fallback** rows, and call
`POST /api/system/reset` (from `/docs`) so the demo starts from clean sample data.

## Demo video script (≈ 4:50, PRD §44)

Screen: browser with two tabs, the citizen app on a phone-width window (≈ 430 px) and the officer
dashboard full width. Narration in English; the citizen speaks Hindi.

| Time | Scene (screen) | Action | Narration (voice-over) |
|---|---|---|---|
| 0:00–0:30 | **Hook.** Citizen app, language *हिन्दी* selected, state Bihar, district Gaya. | Slowly scroll the header; hover the green *Live AI* badge and open it to show the live Google services. | "Meet a parent in a village near Gaya. Every monsoon the river cuts the village off and the children miss school. Thousands of requests like hers arrive every year in many languages, through many channels, and are never added up. JanVaani changes that." |
| 0:30–1:10 | **Voice request.** Citizen app → *बोलें* tab. | Record (or upload) a Hindi voice note: *"सोनबरसा गाँव में नदी पर पुल नहीं है। बरसात में बच्चे स्कूल नहीं जा पाते।"* Wait for the result card. Point at: transcript, English translation, category *Roads & bridges*, urgency *high*, vulnerable group *children*, location *Sonbarsa → LGD code + H3 cell*, confidence. Press ▶ to play the Hindi confirmation. | "She just speaks. Cloud Speech-to-Text transcribes the Hindi, Cloud Translation keeps her words and adds English, and Gemini 2.5 Flash returns schema-validated JSON: category from a fixed taxonomy, urgency, who is affected, and how confident it is. Gemini may not invent numbers or places. The village is resolved to an LGD code and an H3 cell, and she hears the confirmation in Hindi from Cloud Text-to-Speech." |
| 1:10–1:50 | **Demand cluster.** Same card. | Click *हाँ, यह सही है* (confirm). Show "joined a demand group": request count, unique citizens, representative quotes. Optionally: *Chat bot* tab, send the same text, show the bot reply. | "When she confirms, Gemini embeddings compare her request with nearby demand. She is not alone: she joins a cluster of about 150 requests from more than 130 unique citizens. Repeat messages from one person never inflate the count. The same pipeline also runs behind our Telegram bot." |
| 1:50–2:30 | **Data fusion + Priority Score.** Officer dashboard → state *Bihar* → district *Gaya*. | Select the top recommendation *Roads & Bridges – Sonbarsa…*; show the factor bars and the score (≈ 86/100). In *Policy lens (weights)* raise *Vulnerability* to 40 %, click *Apply & re-rank*, point at the rank-change arrows and the *Weight change log (audit)*. | "The planning officer sees citizen demand fused with Census demographics, an infrastructure-gap indicator and existing investments, each with its source and year. The Priority Score is a transparent formula, not a black box. Officers can change the policy weights; the ranking updates instantly and every change is logged." |
| 2:30–3:10 | **Evidence brief.** Recommendation detail. | Click *Generate evidence brief*. Scroll: *Citizen demand evidence*, *Data evidence* (with sources), *Existing investment*, *Uncertainties*, next step, the green *number check*. Click *Approve for field verification*. | "Gemini now writes an evidence brief, but only from the structured data we give it. An automatic check proves that every number in the brief exists in the input. Uncertainties are explicit. The decision stays with a human: the officer approves it for field verification." |
| 3:10–3:40 | **Hotspot map + closing the loop.** Dashboard *All India* → Bihar → Gaya; then the citizen tab. | Show the hotspot map zooming from national to district (H3 hexagons, cluster circles). Switch to the citizen app → *स्थिति जाँचें* with her request ID: status *अनुशंसित* (Recommended). | "From the national view down to one district, officers see where demand is concentrated. And the loop closes: the parent checks her request and sees, in Hindi, that it has been recommended." |
| 3:40–4:20 | **Interoperability.** Dashboard *Interoperability* tab; citizen app scenario **B · AP · తెలుగు**. | Switch Bihar → Andhra Pradesh → Maharashtra: raw state record → adapter mapping → the same canonical record. In the citizen app send scenario B (Telugu, drinking water, Anantapur) and show it land in the AP cluster. | "Every state keeps its own data formats: Hindi-transliterated CSVs in Bihar, nested JSON with separate SC and ST columns in Andhra Pradesh, ward tables in Pune. A small adapter config maps each into one canonical schema. Onboarding a new state is configuration, not code. A Telugu drinking-water request from Anantapur runs through exactly the same AI and APIs." |
| 4:20–4:50 | **Scale & deployment.** Architecture diagram from the README / pitch slide. | Show the diagram and the badge list of Google services. | "JanVaani runs on Google Cloud: Gemini and embeddings on Vertex AI, Speech-to-Text, Translation and Text-to-Speech, Maps, BigQuery, Cloud Storage and Cloud Run in Mumbai. One request, one village, one district, one state, many states: a national citizen-demand intelligence network, and a pattern any BRICS country can adopt with its own admin codes and languages." |

Fallback if the live voice step is slow: use the demo chip *A · BR · हिन्दी* (same text) and say
"typed or spoken, the pipeline is the same".

## Evaluation alignment (PRD §55)

| Criterion | Weight | Evidence in the prototype |
|---|---|---|
| AI / technical execution | 25 % | Gemini 2.5 Flash on Vertex AI with schema-validated JSON and versioned prompts; Gemini embeddings for clustering; Speech-to-Text / Translation / Text-to-Speech; number-grounding check; deterministic score; per-integration live / demo / fallback status; `app.eval_extraction` live evaluation |
| Problem-solution fit | 20 % | One citizen journey from voice note to officer decision and back to the citizen's status |
| Depth & reach across India | 20 % | Three languages, three channels (web text, voice, chat bot / Telegram), three states with different data shapes behind one canonical schema |
| Deployability & scalability | 20 % | Cloud Run API image, Vercel frontends, Secret Manager, BigQuery sink, config-only state onboarding, `deploy.sh` |
| Impact | 15 % | Per-capita unique-citizen demand, vulnerability weighting, investment-coverage subtraction: spending follows measured need |

Live extraction evaluation (2026-09-30, `uv run python -m app.eval_extraction 40`, gemini-2.5-flash,
prompt `extract_v1`, 1.5 s between calls): **100 % category accuracy on 39 live calls** (14 EN /
16 HI / 9 TE: 5 golden fixtures + template-labelled synthetic requests), 5/5 urgency on the golden
set, 0 invented beneficiary counts and 0 places not present in the text. 6 of 45 calls still hit
Vertex AI `429 RESOURCE_EXHAUSTED` on the shared project quota after retries and fell back to the
labelled demo extractor (a first run without pacing: 34/45 live, also 100 %). The synthetic requests are template text, so this is a sanity check, not a
field accuracy figure.

## Definition of Done (PRD §56)

| Item | Status | Notes |
|---|---|---|
| **Citizen experience** | | |
| Submit a request by text | Done | Citizen app *Type* tab; `POST /api/requests` |
| Submit a request by voice | Done | *Speak* tab (record or upload) → Cloud Storage + Cloud Speech-to-Text |
| Submit through the messaging bot | Partly done | Telegram webhook works and the citizen app *Chat bot* tab uses it live; delivery on Telegram itself needs `TELEGRAM_BOT_TOKEN` (not provided) |
| Confirmation in the citizen's language | Done | EN / HI / TE text + Cloud Text-to-Speech audio |
| Citizen can correct or confirm the AI's understanding | Done | Confirm, correct category / place, clarification for ambiguous names |
| **AI experience** | | |
| Gemini extracts structured request data | Done | gemini-2.5-flash via Vertex AI, schema-validated, provenance stored |
| Location resolves to an LGD code | Done | Sample LGD-style codes + H3 res-7; Maps Geocoding fallback |
| Requests cluster into demand clusters | Done | Gemini embeddings + same category / area rules |
| Priority Score with breakdown | Done | Five factors, weights, points, sources |
| Gemini grounded evidence brief | Done | Structured input only + automated number check |
| Confidence / uncertainty displayed | Done | Extraction confidence, location confidence, brief uncertainties |
| **Language & voice** | | |
| English / Hindi / Telugu | Done | UI, confirmations, speech, translation |
| At least one complete voice interaction | Done | Voice note → transcript → confirmation audio (verified live 2026-09-30) |
| **Planning Officer** | | |
| Dashboard exists | Done | `apps/officer-dashboard` |
| Hotspot map visible | Done | Google Maps (Leaflet fallback if the browser key rejects the domain) |
| Ranked recommendations visible | Done | |
| Weights can be adjusted | Done | Policy lens + audit log (streamed to BigQuery) |
| Data sources and freshness visible | Done | Data freshness KPI, per-value source + year, sample-data notice |
| **Interoperability** | | |
| Canonical schema documented | Done | `data/schemas/*.json`, `ai/schemas/*.json` |
| At least two state configurations | Done | Bihar, Andhra Pradesh, Maharashtra |
| State data maps to the common schema | Done | `data/adapters/*.json` + Interoperability tab |
| Shared AI / API services on the common structure | Done | Same pipeline for all three states (tests cover it) |
| **Deployment & submission** | | |
| Prototype publicly deployed | Pending lead | API image and `deploy.sh` verified locally with Docker; lead runs the Cloud Run and Vercel deploys and fills in the URLs |
| Source code on GitHub | Done | Public repo |
| README with setup and architecture | Done | `README.md` (mermaid diagram, integration map, env vars, onboarding) |
| Demo data available and labelled | Done | `data/sample/manifest.json`, "synthetic" flags in data, API and UI |
| 3–5 minute demo video prepared | Not done | Script above; recording needs the live URLs |
| 10–12 slide pitch deck prepared | Done | [`docs/pitch/JanVaani_Spontom_Pitch.pptx`](pitch/JanVaani_Spontom_Pitch.pptx) (13 slides incl. 2 reference slides; PDF: [`JanVaani_Spontom_Pitch.pdf`](pitch/JanVaani_Spontom_Pitch.pdf); generated by `docs/pitch/build-deck.js`) |
| 2–3 line product description | Done | Top of this file |

Not in scope for the MVP (PRD Priority 4 / known gaps): Firebase auth and officer RBAC (Firebase not
provisioned), WhatsApp, photo evidence, impact view, demand forecasting.
