#!/usr/bin/env bash
# Deploy ClaimGuard AI to Cloud Run (builds from source with Cloud Build - no local Docker needed).
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project)}"
REGION="${REGION:-us-central1}"
SERVICE="claimguard-ai"

echo "Deploying $SERVICE to project $PROJECT_ID ($REGION)"

gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com aiplatform.googleapis.com --project "$PROJECT_ID"

# Let the default compute service account (used by Cloud Run) call Vertex AI.
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user" --condition=None >/dev/null

gcloud run deploy "$SERVICE" \
  --source . \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --allow-unauthenticated \
  --memory 1Gi \
  --min-instances 1 \
  --max-instances 3 \
  --timeout 120 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$REGION,GEMINI_MODEL=${GEMINI_MODEL:-gemini-2.5-flash}"

gcloud run services describe "$SERVICE" --project "$PROJECT_ID" --region "$REGION" --format='value(status.url)'
