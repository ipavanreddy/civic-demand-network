#!/usr/bin/env bash
# Deploy JanVaani services to Cloud Run (public, asia-south1). The frontends are on Vercel
# (see infrastructure/vercel/README.md), so the only Cloud Run target is the API.
#
#   CORS_ORIGINS="https://<citizen>.vercel.app,https://<officer>.vercel.app" \
#   CORS_ORIGIN_REGEX='https://.*\.vercel\.app' \
#     infrastructure/cloud-run/deploy.sh api
#
# The image is built by Cloud Build from the repo root (cloudbuild.yaml + services/api/Dockerfile)
# and pushed to Artifact Registry. Secrets come from Secret Manager and never enter the repo/image:
#   MAPS_API_KEY <- maps-api-key, GOOGLE_CLOUD_API_KEY <- google-api-key
#   GEMINI_API_KEY <- gemini-api-key (attached only if that secret exists AND GEMINI_BACKEND=api-key)
# Gemini runs on Vertex AI through the service account by default (GOOGLE_GENAI_USE_VERTEXAI=true,
# location "global"). Do NOT set GOOGLE_API_KEY on the service: google-genai would treat it as a
# Gemini key and bypass Vertex AI.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

PROJECT="${GOOGLE_CLOUD_PROJECT:-spontom-build-with-ai}"
REGION="${REGION:-asia-south1}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-hackathon-dev@spontom-build-with-ai.iam.gserviceaccount.com}"
AR_REPO="${AR_REPO:-cloud-run-source-deploy}"
BIGQUERY_DATASET="${BIGQUERY_DATASET:-civic_demand_network}"
GCS_BUCKET="${GCS_BUCKET:-spontom-build-with-ai-media}"
GEMINI_MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"
GEMINI_EMBEDDING_MODEL="${GEMINI_EMBEDDING_MODEL:-gemini-embedding-001}"
GEMINI_LOCATION="${GEMINI_LOCATION:-global}"   # asia-south1 returned 429s for Gemini
GEMINI_BACKEND="${GEMINI_BACKEND:-vertex}"      # vertex | api-key
USE_BIGQUERY="${USE_BIGQUERY:-true}"
CORS_ORIGINS="${CORS_ORIGINS:-}"
CORS_ORIGIN_REGEX="${CORS_ORIGIN_REGEX:-}"
# The serving store is in memory (BigQuery is a write-only sink), so a single instance keeps the
# citizen -> officer loop consistent. MIN_INSTANCES=1 avoids cold starts during judging.
MIN_INSTANCES="${MIN_INSTANCES:-0}"
MAX_INSTANCES="${MAX_INSTANCES:-1}"

API=civic-demand-network-api
TARGETS=("$@")
[ ${#TARGETS[@]} -eq 0 ] && TARGETS=(api)

gc() { gcloud --project "$PROJECT" --quiet "$@"; }
yq() { printf "'%s'" "${1//\'/\'\'}"; }  # YAML single-quoted scalar (keeps regex backslashes)

REGISTRY="$REGION-docker.pkg.dev/$PROJECT/$AR_REPO"
TAG="$(git rev-parse --short HEAD)$(git diff --quiet HEAD -- services ai data || echo -dirty)-$(date +%Y%m%d%H%M%S)"

deploy_api() {
  if [ -z "$CORS_ORIGINS" ]; then
    echo "CORS_ORIGINS is required, e.g. CORS_ORIGINS=https://janvaani-citizen.vercel.app,https://janvaani-officer.vercel.app" >&2
    exit 2
  fi
  local image="$REGISTRY/$API:$TAG" envfile secrets vertex
  gc artifacts repositories describe "$AR_REPO" --location "$REGION" >/dev/null
  gc builds submit "$ROOT" --region "$REGION" --config infrastructure/cloud-run/cloudbuild.yaml \
    --substitutions "_DOCKERFILE=services/api/Dockerfile,_IMAGE=$image"

  vertex=true
  secrets="MAPS_API_KEY=maps-api-key:latest,GOOGLE_CLOUD_API_KEY=google-api-key:latest"
  if [ "$GEMINI_BACKEND" = api-key ]; then
    gc secrets describe gemini-api-key >/dev/null  # fails loudly if the secret does not exist yet
    secrets="$secrets,GEMINI_API_KEY=gemini-api-key:latest"
    vertex=false
  fi

  envfile="$(mktemp)"
  trap 'rm -f "$envfile"' RETURN
  cat >"$envfile" <<YAML
GOOGLE_CLOUD_PROJECT: $(yq "$PROJECT")
GOOGLE_GENAI_USE_VERTEXAI: $(yq "$vertex")
GOOGLE_CLOUD_LOCATION: $(yq "$GEMINI_LOCATION")
GEMINI_MODEL: $(yq "$GEMINI_MODEL")
GEMINI_EMBEDDING_MODEL: $(yq "$GEMINI_EMBEDDING_MODEL")
GEMINI_THINKING_BUDGET: '0'
USE_BIGQUERY: $(yq "$USE_BIGQUERY")
BIGQUERY_DATASET: $(yq "$BIGQUERY_DATASET")
GCS_BUCKET: $(yq "$GCS_BUCKET")
CORS_ORIGINS: $(yq "$CORS_ORIGINS")
CORS_ORIGIN_REGEX: $(yq "$CORS_ORIGIN_REGEX")
YAML

  # --update-* would keep stale variables (e.g. an old GOOGLE_API_KEY); --env-vars-file and
  # --set-secrets replace the full set.
  gc run deploy "$API" --image "$image" \
    --service-account="$SERVICE_ACCOUNT" --allow-unauthenticated --region="$REGION" \
    --env-vars-file "$envfile" --set-secrets "$secrets" \
    --memory 1Gi --cpu 1 --timeout 120 --concurrency 40 \
    --min-instances "$MIN_INSTANCES" --max-instances "$MAX_INSTANCES" \
    --labels app=civic-demand-network,component=api

  local url
  url="$(gc run services describe "$API" --region "$REGION" --format='value(status.url)')"
  echo
  echo "API: $url  (health: $url/health, docs: $url/docs)"
  curl -fsS "$url/health" && echo
  curl -fsS "$url/api/system/status" | python3 -c 'import json,sys; d=json.load(sys.stdin); [print(f"  {k:15} {v[\"mode\"]:8} {v[\"detail\"]}") for k,v in d["integrations"].items()]' || true
}

for t in "${TARGETS[@]}"; do
  case "$t" in
    api) deploy_api ;;
    *) echo "unknown target: $t (only 'api' runs on Cloud Run; frontends deploy to Vercel)" >&2; exit 2 ;;
  esac
done
