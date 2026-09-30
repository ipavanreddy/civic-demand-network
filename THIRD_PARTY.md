# Third-party datasets, models and libraries

Every reused dataset, model and library must be cited here (hackathon rule).

| Name | Type | Licence | Source URL | Used for |
|---|---|---|---|---|
| Next.js 16 | Library | MIT | https://nextjs.org | Frontends (citizen app, officer dashboard) |
| React / React DOM 19 | Library | MIT | https://react.dev | UI runtime |
| shadcn/ui (components + CLI) | Library | MIT | https://ui.shadcn.com | UI components |
| Base UI | Library | MIT | https://base-ui.com | Primitives under shadcn/ui |
| class-variance-authority, cn, tw-animate-css | Library | MIT / Apache-2.0 | https://cva.style · https://www.npmjs.com/package/cn · https://github.com/Wombosvideo/tw-animate-css | Component variants, class names, animations |
| next-themes, sonner | Library | MIT | https://github.com/pacocoursey/next-themes · https://sonner.emilkowal.ski | Theme handling, toasts |
| lucide-react | Library | ISC | https://lucide.dev | Icons |
| Tailwind CSS 4 | Library | MIT | https://tailwindcss.com | Styling |
| Geist / Geist Mono (via `next/font/google`) | Font | SIL OFL 1.1 | https://vercel.com/font | UI typeface (Latin); Devanagari / Telugu use system fonts |
| TypeScript, ESLint, eslint-config-next | Library (dev) | Apache-2.0 / MIT | https://www.typescriptlang.org · https://eslint.org | Type checking, linting |
| Leaflet | Library | BSD-2-Clause | https://leafletjs.com | Hotspot map when no Google Maps key is set or the key is rejected |
| OpenStreetMap tiles | Map data / tiles | ODbL (data), tile usage policy | https://www.openstreetmap.org/copyright · https://operations.osmfoundation.org/policies/tiles/ | Fallback base map (attribution shown on the map; light demo use only) |
| Google Maps JavaScript API | Service / map tiles | Google Maps Platform ToS | https://developers.google.com/maps/documentation/javascript | Hotspot map when `NEXT_PUBLIC_MAPS_API_KEY` is set |
| Google Maps Geocoding API | Service | Google Maps Platform ToS | https://developers.google.com/maps/documentation/geocoding | Location resolution fallback (`MAPS_API_KEY`) |
| FastAPI (with Starlette) | Library | MIT / BSD-3-Clause | https://fastapi.tiangolo.com | API |
| Pydantic / pydantic-settings | Library | MIT | https://docs.pydantic.dev | Canonical schema, structured-output schemas, config |
| python-multipart | Library | Apache-2.0 | https://github.com/Kludex/python-multipart | Voice-note uploads |
| Google Gen AI SDK (`google-genai`) | Library | Apache-2.0 | https://github.com/googleapis/python-genai | Gemini calls on Vertex AI (extraction, transcription/translation fallback, briefs, embeddings) |
| Gemini 2.5 Flash (`gemini-2.5-flash`, set by `GEMINI_MODEL`) | Model | Google Cloud / Gemini API ToS | https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash | Request understanding, evidence briefs |
| Gemini Embedding (`gemini-embedding-001`, set by `GEMINI_EMBEDDING_MODEL`) | Model | Google Cloud ToS | https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings | Semantic similarity for demand clustering |
| Vertex AI | Service | Google Cloud ToS | https://cloud.google.com/vertex-ai | Serves Gemini through the service account (location `global`) |
| Cloud Speech-to-Text / Cloud Translation / Cloud Text-to-Speech | Service | Google Cloud ToS | https://cloud.google.com/speech-to-text · https://cloud.google.com/translate · https://cloud.google.com/text-to-speech | Voice + multilingual pipeline (`GOOGLE_CLOUD_API_KEY`) |
| BigQuery | Service | Google Cloud ToS | https://cloud.google.com/bigquery | Analytics sink for requests, cluster assignments, briefs, weight changes, decisions |
| Cloud Storage | Service | Google Cloud ToS | https://cloud.google.com/storage | Voice notes |
| Cloud Run, Cloud Build, Artifact Registry, Secret Manager | Service | Google Cloud ToS | https://cloud.google.com/run | API hosting, image build, secrets |
| Vercel | Service | Vercel ToS | https://vercel.com | Frontend hosting |
| google-cloud-bigquery, google-cloud-storage, firebase-admin | Library | Apache-2.0 | https://github.com/googleapis/python-bigquery · https://github.com/googleapis/python-storage · https://github.com/firebase/firebase-admin-python | BigQuery sink, media storage (firebase-admin: dependency for the planned auth, not used yet) |
| h3 (h3-py) | Library | Apache-2.0 | https://github.com/uber/h3-py | H3 hexagonal cells for hotspots |
| httpx | Library | BSD-3-Clause | https://www.python-httpx.org | REST calls to Google APIs / Telegram |
| uvicorn | Library | BSD-3-Clause | https://www.uvicorn.org | ASGI server |
| uv | Tool | MIT / Apache-2.0 | https://docs.astral.sh/uv | Python packaging (also in the API image) |
| python:3.12-slim | Container base image | PSF / Debian licences | https://hub.docker.com/_/python | API image |
| pytest, ruff | Library (dev) | MIT | https://pytest.org · https://docs.astral.sh/ruff | Tests, linting |
| python-pptx | Library (docs tooling) | MIT | https://github.com/scanny/python-pptx | Generates the pitch deck (`docs/pitch/build_deck.py`) |
| Playwright | Tool (dev, not committed) | Apache-2.0 | https://playwright.dev | Local screenshots / smoke checks of the UI |
| Telegram Bot API | Service | Telegram ToS | https://core.telegram.org/bots/api | Messaging-bot channel (`TELEGRAM_BOT_TOKEN`) |

## Data

All data under `data/sample/` is **synthetic sample data** generated by
`data/transformations/generate_sample.py` (standard library, fixed seed, no AI). It is *modelled on*
the structure of the public sources below but contains **no values copied from them**; administrative
codes are LGD-style sample codes, not official LGD codes.

| Modelled on | Publisher | URL |
|---|---|---|
| Local Government Directory (LGD) codes | Ministry of Panchayati Raj | https://lgdirectory.gov.in |
| Census of India 2011 Primary Census Abstract | Office of the Registrar General & Census Commissioner | https://censusindia.gov.in |
| Aspirational Districts Programme list | NITI Aayog | https://www.niti.gov.in/aspirational-districts-programme |
| Jal Jeevan Mission / Har Ghar Nal Jal MIS | Ministry of Jal Shakti / Govt. of Bihar | https://ejalshakti.gov.in |
| PMGSY road works | Ministry of Rural Development | https://omms.nic.in |
| H3 geospatial index (method) | Uber / H3 project | https://h3geo.org |

Place names (villages, mandals, wards) are real Indian place names used only as labels; populations,
indicators, investments and citizen requests attached to them are fictional.
