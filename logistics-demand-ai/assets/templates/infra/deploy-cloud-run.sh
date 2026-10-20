#!/usr/bin/env bash
set -euo pipefail
: "${GCP_PROJECT:?Set GCP_PROJECT}"
: "${GCP_REGION:=asia-northeast1}"
# 認証が必要なCloud Runサービスとしてデプロイ（権限設定は別途）。
gcloud run deploy logistics-ai-api \
  --source ../backend \
  --project "$GCP_PROJECT" \
  --region "$GCP_REGION" \
  --no-allow-unauthenticated
