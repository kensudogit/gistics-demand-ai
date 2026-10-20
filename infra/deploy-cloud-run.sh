#!/usr/bin/env bash
set -euo pipefail
: "${GCP_PROJECT:?Set GCP_PROJECT}"
: "${GCP_REGION:=asia-northeast1}"
# Authenticated Cloud Run. IAM must be configured separately. Do not claim deploy success without running this.
gcloud run deploy logistics-ai-api \
  --source ../backend \
  --project "$GCP_PROJECT" \
  --region "$GCP_REGION" \
  --no-allow-unauthenticated
