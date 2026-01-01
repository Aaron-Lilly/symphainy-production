# Test Infrastructure Setup Guide

## Quick Start

### Step 1: Create Test GCS Bucket

```bash
# Create test bucket (if it doesn't exist)
gsutil mb -p your-project-id -l us-central1 gs://symphainy-bucket-2025-test

# Set lifecycle policy for auto-cleanup (delete files older than 7 days)
cat > lifecycle.json << EOF
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

gsutil lifecycle set lifecycle.json gs://symphainy-bucket-2025-test
```

### Step 2: Create Test Service Account

```bash
# Create service account for tests
gcloud iam service-accounts create test-service-account \
    --display-name="Test Service Account" \
    --description="Service account for integration tests"

# Grant permissions
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:test-service-account@your-project-id.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Create and download key
gcloud iam service-accounts keys create test-credentials.json \
    --iam-account=test-service-account@your-project-id.iam.gserviceaccount.com
```

### Step 3: Configure Supabase Test Isolation

**Option A: Use Test Tenant (Recommended)**
- Use existing `project_files` table
- Filter by `tenant_id = 'test_tenant'`
- Auto-cleanup: Delete records with `tenant_id = 'test_tenant'` older than 7 days

**Option B: Create Test Table**
```sql
-- Create test table (if needed)
CREATE TABLE project_files_test (
    -- Same schema as project_files
    uuid TEXT PRIMARY KEY,
    user_id TEXT,
    tenant_id TEXT DEFAULT 'test_tenant',
    ui_name TEXT,
    file_type TEXT,
    -- ... other fields
);
```

### Step 4: Set Environment Variables

Create `.env.test` file:

```bash
# Test Infrastructure Configuration
TEST_INFRASTRUCTURE_ENABLED=true

# GCS Configuration
TEST_GCS_BUCKET=symphainy-bucket-2025-test
TEST_GCS_CREDENTIALS=/path/to/test-credentials.json
# OR use default credentials
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/test-credentials.json

# Supabase Configuration
TEST_SUPABASE_URL=https://xxx.supabase.co
TEST_SUPABASE_SERVICE_KEY=your_test_service_key
# OR use existing Supabase config
# SUPABASE_URL=https://xxx.supabase.co
# SUPABASE_SERVICE_KEY=your_service_key

# Test Isolation
TEST_TENANT_ID=test_tenant
```

### Step 5: Load Environment in Tests

```python
# In conftest.py or test setup
import os
from dotenv import load_dotenv

# Load test environment
load_dotenv('.env.test')
```

---

## Test Isolation Strategy

### GCS Isolation

**Prefix-Based Isolation (Recommended)**
- All test files: `test/YYYYMMDD_HHMMSS_filename.ext`
- Lifecycle policy: Auto-delete after 7 days
- Easy to identify and clean up

**Implementation:**
```python
test_file_path = f"test/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
```

### Supabase Isolation

**Tenant-Based Isolation (Recommended)**
- All test records: `tenant_id = 'test_tenant'`
- Easy to query and clean up
- Uses existing table structure

**Implementation:**
```python
file_metadata = {
    "tenant_id": "test_tenant",
    "user_id": "test_user",
    # ... other fields
}
```

---

## Cleanup Strategies

### Automatic Cleanup (Recommended)

**GCS Lifecycle Policy:**
```json
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
```

**Supabase Cleanup Job:**
```sql
-- Run daily cleanup job
DELETE FROM project_files 
WHERE tenant_id = 'test_tenant' 
  AND created_at < NOW() - INTERVAL '7 days';
```

### Manual Cleanup

```bash
# Clean up GCS test files
gsutil -m rm gs://symphainy-bucket-2025-test/test/**

# Clean up Supabase test records
psql -c "DELETE FROM project_files WHERE tenant_id = 'test_tenant';"
```

---

## Running Tests

### With Real Infrastructure

```bash
# Set environment variable
export TEST_INFRASTRUCTURE_ENABLED=true

# Run tests
pytest tests/integration/layer_8_business_enablement/ -v
```

### Without Infrastructure (Skip Tests)

```bash
# Don't set TEST_INFRASTRUCTURE_ENABLED (or set to false)
pytest tests/integration/layer_8_business_enablement/ -v
# Tests will skip gracefully
```

---

## Verification

### Check GCS Bucket

```bash
# List test files
gsutil ls gs://symphainy-bucket-2025-test/test/

# Check lifecycle policy
gsutil lifecycle get gs://symphainy-bucket-2025-test
```

### Check Supabase

```sql
-- Count test records
SELECT COUNT(*) FROM project_files WHERE tenant_id = 'test_tenant';

-- List test records
SELECT uuid, ui_name, created_at 
FROM project_files 
WHERE tenant_id = 'test_tenant' 
ORDER BY created_at DESC 
LIMIT 10;
```

---

## Cost Considerations

### GCS Costs
- Storage: ~$0.02/GB/month
- Operations: ~$0.05 per 10,000 operations
- **Test bucket with 7-day lifecycle: Minimal cost**

### Supabase Costs
- Storage: Included in plan
- Operations: Included in plan
- **Test tenant isolation: No additional cost**

---

## Security Considerations

1. **Separate Service Account**: Use dedicated test service account (not production)
2. **Limited Permissions**: Only grant necessary permissions (Storage Object Admin)
3. **Test Credentials**: Store test credentials securely (not in repo)
4. **Tenant Isolation**: Ensure test tenant cannot access production data

---

## Troubleshooting

### GCS Authentication Error

```bash
# Verify credentials
gcloud auth activate-service-account --key-file=test-credentials.json

# Test access
gsutil ls gs://symphainy-bucket-2025-test/
```

### Supabase Connection Error

```bash
# Verify URL and key
curl -H "apikey: YOUR_SERVICE_KEY" https://xxx.supabase.co/rest/v1/
```

### Test Files Not Cleaning Up

```bash
# Check lifecycle policy
gsutil lifecycle get gs://symphainy-bucket-2025-test

# Manual cleanup
gsutil -m rm gs://symphainy-bucket-2025-test/test/**
```

---

## Next Steps

1. ✅ Set up test GCS bucket
2. ✅ Create test service account
3. ✅ Configure Supabase test isolation
4. ✅ Set environment variables
5. ✅ Update test fixtures to use test infrastructure
6. ✅ Verify tests work with real infrastructure
7. ✅ Set up automatic cleanup (lifecycle policies)

