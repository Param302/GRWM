#!/bin/bash

# GRWM Backend - GCP Cloud Run Deployment Script
# This script builds and deploys the backend to Google Cloud Run

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="grwm-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   GRWM Backend - Cloud Run Deployment     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Error: GCP_PROJECT_ID environment variable is not set${NC}"
    echo -e "${YELLOW}   Set it with: export GCP_PROJECT_ID=your-project-id${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Configuration:${NC}"
echo -e "   Project ID: ${GREEN}${PROJECT_ID}${NC}"
echo -e "   Region: ${GREEN}${REGION}${NC}"
echo -e "   Service Name: ${GREEN}${SERVICE_NAME}${NC}"
echo -e "   Image: ${GREEN}${IMAGE_NAME}${NC}"
echo ""

# Check if user is logged in
echo -e "${BLUE}🔐 Checking authentication...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1 > /dev/null 2>&1; then
    echo -e "${RED}❌ Not authenticated with gcloud${NC}"
    echo -e "${YELLOW}   Run: gcloud auth login${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Authenticated${NC}"
echo ""

# Set active project
echo -e "${BLUE}🎯 Setting active project...${NC}"
gcloud config set project ${PROJECT_ID}
echo ""

# Enable required APIs
echo -e "${BLUE}🔌 Enabling required APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com
echo -e "${GREEN}✅ APIs enabled${NC}"
echo ""

# Build Docker image using Cloud Build (recommended for production)
echo -e "${BLUE}🏗️  Building Docker image with Cloud Build...${NC}"
gcloud builds submit --tag ${IMAGE_NAME}:latest
echo -e "${GREEN}✅ Image built successfully${NC}"
echo ""

# Check if secrets exist (GitHub PAT and Google API Keys)
echo -e "${BLUE}🔑 Checking secrets...${NC}"

# Check GitHub PAT (REQUIRED)
if ! gcloud secrets describe github-pat --project=${PROJECT_ID} > /dev/null 2>&1; then
    echo -e "${RED}❌ Secret 'github-pat' not found (REQUIRED)${NC}"
    echo -e "${YELLOW}   Create it with:${NC}"
    echo -e "${YELLOW}   echo -n 'your-github-token' | gcloud secrets create github-pat --data-file=-${NC}"
    echo ""
    echo -e "${RED}Deployment cancelled - GitHub PAT required${NC}"
    exit 1
else
    echo -e "${GREEN}   ✅ Found github-pat${NC}"
fi

# Check for API keys and build secrets configuration
echo -e "${BLUE}   Checking Google API keys...${NC}"
SECRETS_CONFIG="GITHUB_PAT=github-pat:latest"
KEY_COUNT=0

# Check key 1
if gcloud secrets describe google-api-key-1 --project=${PROJECT_ID} > /dev/null 2>&1; then
    SECRETS_CONFIG="${SECRETS_CONFIG},GOOGLE_API_KEY_1=google-api-key-1:latest"
    KEY_COUNT=$((KEY_COUNT + 1))
    echo -e "${GREEN}   ✅ Found google-api-key-1${NC}"
fi

# Check key 2
if gcloud secrets describe google-api-key-2 --project=${PROJECT_ID} > /dev/null 2>&1; then
    SECRETS_CONFIG="${SECRETS_CONFIG},GOOGLE_API_KEY_2=google-api-key-2:latest"
    KEY_COUNT=$((KEY_COUNT + 1))
    echo -e "${GREEN}   ✅ Found google-api-key-2${NC}"
fi

# Check key 3
if gcloud secrets describe google-api-key-3 --project=${PROJECT_ID} > /dev/null 2>&1; then
    SECRETS_CONFIG="${SECRETS_CONFIG},GOOGLE_API_KEY_3=google-api-key-3:latest"
    KEY_COUNT=$((KEY_COUNT + 1))
    echo -e "${GREEN}   ✅ Found google-api-key-3${NC}"
fi

if [ $KEY_COUNT -eq 0 ]; then
    echo -e "${RED}❌ No Google API keys found!${NC}"
    echo -e "${YELLOW}   Create at least one key:${NC}"
    echo -e "${YELLOW}   echo -n 'your-api-key' | gcloud secrets create google-api-key-1 --data-file=-${NC}"
    echo ""
    echo -e "${RED}Deployment cancelled - secrets required${NC}"
    exit 1
else
    echo -e "${GREEN}✅ API key rotation enabled with ${KEY_COUNT} key(s)${NC}"
fi
echo ""

# Grant Cloud Run service account access to secrets
echo -e "${BLUE}🔐 Granting secret access permissions...${NC}"

# Get project number for service account
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo -e "${BLUE}   Service Account: ${SERVICE_ACCOUNT}${NC}"

# Grant access to GitHub PAT
echo -e "${BLUE}   Granting access to github-pat...${NC}"
gcloud secrets add-iam-policy-binding github-pat \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" \
    --project=${PROJECT_ID} > /dev/null 2>&1

# Grant access to API keys
if gcloud secrets describe google-api-key-1 --project=${PROJECT_ID} > /dev/null 2>&1; then
    echo -e "${BLUE}   Granting access to google-api-key-1...${NC}"
    gcloud secrets add-iam-policy-binding google-api-key-1 \
        --member="serviceAccount:${SERVICE_ACCOUNT}" \
        --role="roles/secretmanager.secretAccessor" \
        --project=${PROJECT_ID} > /dev/null 2>&1
fi

if gcloud secrets describe google-api-key-2 --project=${PROJECT_ID} > /dev/null 2>&1; then
    echo -e "${BLUE}   Granting access to google-api-key-2...${NC}"
    gcloud secrets add-iam-policy-binding google-api-key-2 \
        --member="serviceAccount:${SERVICE_ACCOUNT}" \
        --role="roles/secretmanager.secretAccessor" \
        --project=${PROJECT_ID} > /dev/null 2>&1
fi

if gcloud secrets describe google-api-key-3 --project=${PROJECT_ID} > /dev/null 2>&1; then
    echo -e "${BLUE}   Granting access to google-api-key-3...${NC}"
    gcloud secrets add-iam-policy-binding google-api-key-3 \
        --member="serviceAccount:${SERVICE_ACCOUNT}" \
        --role="roles/secretmanager.secretAccessor" \
        --project=${PROJECT_ID} > /dev/null 2>&1
fi

echo -e "${GREEN}✅ Permissions granted${NC}"
echo ""

# Deploy to Cloud Run
echo -e "${BLUE}🚀 Deploying to Cloud Run...${NC}"
echo -e "${BLUE}   Using ${KEY_COUNT} API key(s) for rotation${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --cpu 2 \
    --memory 2Gi \
    --timeout 300 \
    --concurrency 80 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars "ENVIRONMENT=production" \
    --set-secrets "${SECRETS_CONFIG}" \
    --execution-environment gen2 \
    --no-cpu-throttling

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
echo -e "${BLUE}🌐 Service URL:${NC}"
echo -e "   ${GREEN}${SERVICE_URL}${NC}"
echo ""

# Test health endpoint
echo -e "${BLUE}🏥 Testing health endpoint...${NC}"
if curl -s "${SERVICE_URL}/api/health" > /dev/null; then
    echo -e "${GREEN}✅ Service is healthy!${NC}"
else
    echo -e "${YELLOW}⚠️  Health check failed (service might still be starting)${NC}"
fi
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   🎉 Deployment Successful!                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📝 Next steps:${NC}"
echo -e "   1. Update frontend env: ${YELLOW}NEXT_PUBLIC_API_URL=${SERVICE_URL}${NC}"
echo -e "   2. Add service URL to CORS in api.py if needed"
echo -e "   3. Monitor logs: ${YELLOW}gcloud run logs tail ${SERVICE_NAME} --region ${REGION}${NC}"
echo ""
