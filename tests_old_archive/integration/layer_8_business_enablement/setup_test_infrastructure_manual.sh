#!/bin/bash
# Manual Test Infrastructure Setup (for environments with limited permissions)
# This version uses existing buckets and creates service accounts if possible

set -e  # Exit on error

echo "🚀 Manual Test Infrastructure Setup"
echo "======================================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "symphainymvp-devbox")
echo -e "${GREEN}✅ Using project: ${PROJECT_ID}${NC}"

# Configuration
EXISTING_BUCKET="symphainy-bucket-2025"  # Use existing bucket
TEST_PREFIX="test/"  # Test files will use this prefix
SERVICE_ACCOUNT_NAME="test-service-account"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
CREDENTIALS_FILE="test-credentials.json"
ENV_FILE=".env.test"

echo ""
echo "📋 Configuration:"
echo "   Existing Bucket: ${EXISTING_BUCKET}"
echo "   Test Prefix: ${TEST_PREFIX}"
echo "   Service Account: ${SERVICE_ACCOUNT_EMAIL}"
echo ""

# Step 1: Verify existing bucket
echo "📦 Step 1: Verifying existing bucket..."
if gsutil ls -b "gs://${EXISTING_BUCKET}" &> /dev/null; then
    echo -e "${GREEN}✅ Bucket ${EXISTING_BUCKET} exists and is accessible${NC}"
else
    echo -e "${RED}❌ Bucket ${EXISTING_BUCKET} not accessible${NC}"
    echo "   Please check bucket name or permissions"
    exit 1
fi

# Step 2: Set Lifecycle Policy (if we have permission)
echo ""
echo "🔄 Step 2: Setting Lifecycle Policy..."
LIFECYCLE_FILE=$(mktemp)
cat > "${LIFECYCLE_FILE}" << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 7,
          "matchesPrefix": ["test/"]
        }
      }
    ]
  }
}
EOF

if gsutil lifecycle set "${LIFECYCLE_FILE}" "gs://${EXISTING_BUCKET}" 2>/dev/null; then
    echo -e "${GREEN}✅ Lifecycle policy set successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Could not set lifecycle policy (may need admin permissions)${NC}"
    echo "   You can set it manually later or ask an admin to set it"
fi
rm "${LIFECYCLE_FILE}"

# Step 3: Try to create service account (may fail if no permission)
echo ""
echo "👤 Step 3: Creating Test Service Account..."
if gcloud iam service-accounts describe "${SERVICE_ACCOUNT_EMAIL}" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Service account ${SERVICE_ACCOUNT_EMAIL} already exists${NC}"
    SKIP_SA_CREATION=true
else
    if gcloud iam service-accounts create "${SERVICE_ACCOUNT_NAME}" \
        --display-name="Test Service Account" \
        --description="Service account for integration tests" \
        --project="${PROJECT_ID}" 2>/dev/null; then
        echo -e "${GREEN}✅ Service account created successfully${NC}"
        SKIP_SA_CREATION=false
    else
        echo -e "${YELLOW}⚠️  Could not create service account (insufficient permissions)${NC}"
        echo "   You can:"
        echo "   1. Ask an admin to create it: test-service-account"
        echo "   2. Use an existing service account"
        echo "   3. Use your current credentials (less secure)"
        SKIP_SA_CREATION=true
        USE_EXISTING_SA=true
    fi
fi

# Step 4: Grant permissions (if service account exists)
if [ "$SKIP_SA_CREATION" = false ] || gcloud iam service-accounts describe "${SERVICE_ACCOUNT_EMAIL}" &> /dev/null; then
    echo ""
    echo "🔐 Step 4: Granting Permissions..."
    if gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/storage.objectAdmin" \
        --condition=None \
        --quiet 2>/dev/null; then
        echo -e "${GREEN}✅ Permissions granted${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not grant permissions (may need admin)${NC}"
        echo "   Ask an admin to grant roles/storage.objectAdmin to: ${SERVICE_ACCOUNT_EMAIL}"
    fi
else
    echo ""
    echo "⏭️  Step 4: Skipping permissions (service account not available)"
fi

# Step 5: Create credentials (if service account exists)
if [ "$SKIP_SA_CREATION" = false ] || gcloud iam service-accounts describe "${SERVICE_ACCOUNT_EMAIL}" &> /dev/null; then
    echo ""
    echo "🔑 Step 5: Creating Service Account Key..."
    if [ -f "${CREDENTIALS_FILE}" ]; then
        echo -e "${YELLOW}⚠️  Credentials file ${CREDENTIALS_FILE} already exists${NC}"
        read -p "   Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "   Skipping key creation"
        else
            if gcloud iam service-accounts keys create "${CREDENTIALS_FILE}" \
                --iam-account="${SERVICE_ACCOUNT_EMAIL}" \
                --project="${PROJECT_ID}" 2>/dev/null; then
                echo -e "${GREEN}✅ Key created: ${CREDENTIALS_FILE}${NC}"
            else
                echo -e "${RED}❌ Failed to create key${NC}"
            fi
        fi
    else
        if gcloud iam service-accounts keys create "${CREDENTIALS_FILE}" \
            --iam-account="${SERVICE_ACCOUNT_EMAIL}" \
            --project="${PROJECT_ID}" 2>/dev/null; then
            echo -e "${GREEN}✅ Key created: ${CREDENTIALS_FILE}${NC}"
        else
            echo -e "${YELLOW}⚠️  Could not create key${NC}"
            echo "   You may need to use existing credentials or ask an admin"
            USE_EXISTING_CREDS=true
        fi
    fi
else
    echo ""
    echo "⏭️  Step 5: Skipping credentials (service account not available)"
    USE_EXISTING_CREDS=true
fi

# Step 6: Create .env.test
echo ""
echo "📝 Step 6: Creating .env.test configuration..."

# Determine credentials path
if [ -f "${CREDENTIALS_FILE}" ]; then
    CREDS_PATH="$(pwd)/${CREDENTIALS_FILE}"
elif [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    CREDS_PATH="$GOOGLE_APPLICATION_CREDENTIALS"
    echo -e "${YELLOW}⚠️  Using existing GOOGLE_APPLICATION_CREDENTIALS${NC}"
else
    CREDS_PATH=""
    echo -e "${YELLOW}⚠️  No credentials file found - you'll need to set this manually${NC}"
fi

cat > "${ENV_FILE}" << EOF
# Test Infrastructure Configuration
# Generated by setup_test_infrastructure_manual.sh

# Enable test infrastructure
TEST_INFRASTRUCTURE_ENABLED=true

# GCS Configuration (using existing bucket)
TEST_GCS_BUCKET=${EXISTING_BUCKET}
${CREDS_PATH:+TEST_GCS_CREDENTIALS=${CREDS_PATH}}
GCS_PROJECT_ID=${PROJECT_ID}
GCS_REGION=us-central1

# Supabase Configuration
# Try to load from env_secrets_for_cursor.md if it exists
SUPABASE_URL=""
SUPABASE_SERVICE_KEY=""
if [ -f "../../../symphainy-platform/env_secrets_for_cursor.md" ]; then
    # Extract Supabase URL (hosted version)
    SUPABASE_URL=$(grep "^SUPABASE_URL=https://" ../../../symphainy-platform/env_secrets_for_cursor.md | head -1 | cut -d'=' -f2)
    # Extract Supabase secret key
    SUPABASE_SERVICE_KEY=$(grep "^SUPABASE_SECRET_KEY=" ../../../symphainy-platform/env_secrets_for_cursor.md | head -1 | cut -d'=' -f2)
fi

# Use extracted values or leave as placeholders
if [ -n "$SUPABASE_URL" ] && [ -n "$SUPABASE_SERVICE_KEY" ]; then
    echo "   Found Supabase credentials from env_secrets_for_cursor.md"
    SUPABASE_CONFIG="SUPABASE_URL=${SUPABASE_URL}
SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
TEST_SUPABASE_URL=${SUPABASE_URL}
TEST_SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}"
else
    SUPABASE_CONFIG="# Supabase Configuration (update with your values)
# TEST_SUPABASE_URL=https://xxx.supabase.co
# TEST_SUPABASE_SERVICE_KEY=your_test_service_key
# Or use existing Supabase config:
# SUPABASE_URL=https://xxx.supabase.co
# SUPABASE_SERVICE_KEY=your_service_key"
fi

# Test Isolation
TEST_TENANT_ID=test_tenant
EOF

echo -e "${GREEN}✅ Configuration file created: ${ENV_FILE}${NC}"

# Summary
echo ""
echo "======================================================================"
echo -e "${GREEN}✅ Manual Setup Complete!${NC}"
echo ""
echo "Summary:"
echo "  📦 Using existing bucket: gs://${EXISTING_BUCKET}"
echo "  📁 Test prefix: ${TEST_PREFIX}"
if [ -f "${CREDENTIALS_FILE}" ]; then
    echo "  🔑 Credentials: ${CREDENTIALS_FILE}"
elif [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "  🔑 Using: GOOGLE_APPLICATION_CREDENTIALS"
else
    echo "  ⚠️  Credentials: Not configured (update .env.test manually)"
fi
echo "  📝 Config: ${ENV_FILE}"
echo ""
echo "Next Steps:"
echo "  1. Update ${ENV_FILE} with Supabase credentials"
if [ "$USE_EXISTING_CREDS" = true ] && [ -z "$CREDS_PATH" ]; then
    echo "  2. Set TEST_GCS_CREDENTIALS in ${ENV_FILE} or GOOGLE_APPLICATION_CREDENTIALS"
fi
echo "  3. Run: python3 verify_test_infrastructure.py"
echo "  4. Run tests: pytest tests/integration/layer_8_business_enablement/ -v"
echo ""
if [ "$USE_EXISTING_SA" = true ] || [ "$USE_EXISTING_CREDS" = true ]; then
    echo -e "${YELLOW}⚠️  Note: Some steps were skipped due to permissions${NC}"
    echo "   The setup will work with existing credentials"
fi
echo "======================================================================"

