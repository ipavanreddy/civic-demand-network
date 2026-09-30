#!/usr/bin/env bash
# Deploy services/api to Cloud Run (asia-south1). Secrets come from Secret Manager.
set -euo pipefail
: "${GOOGLE_CLOUD_PROJECT:?set GOOGLE_CLOUD_PROJECT}"
cd "$(dirname "$0")/../../services/api"
# Stage repo-level data/ and ai/ into the build context (removed again on exit).
rm -rf _bundle && mkdir -p _bundle && cp -R ../../data ../../ai _bundle/
trap 'rm -rf _bundle' EXIT
gcloud run deploy civic-demand-network-api \
  --source . \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=asia-south1,USE_BIGQUERY=true \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest,MAPS_API_KEY=maps-api-key:latest,GOOGLE_API_KEY=google-api-key:latest,TELEGRAM_BOT_TOKEN=telegram-bot-token:latest
