# Quick Start: Test Infrastructure Setup

## 🚀 Fast Setup (5 minutes)

### Step 1: Run Setup Script

```bash
cd tests/integration/layer_8_business_enablement
./setup_test_infrastructure.sh
```

This will:
- ✅ Create GCS test bucket: `symphainy-bucket-2025-test`
- ✅ Set lifecycle policy (auto-delete after 7 days)
- ✅ Create test service account
- ✅ Generate credentials file
- ✅ Create `.env.test` configuration

### Step 2: Configure Supabase

Edit `.env.test` and add your Supabase credentials:

```bash
# Update these values:
TEST_SUPABASE_URL=https://xxx.supabase.co
TEST_SUPABASE_SERVICE_KEY=your_service_key
```

Or use existing Supabase config:
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
```

### Step 3: Set Up Supabase Test Isolation

Run the SQL script in your Supabase SQL editor:

```bash
# Copy the SQL from setup_supabase_test_isolation.sql
# Paste into Supabase SQL Editor and run
```

Or manually:
- Use `tenant_id = 'test_tenant'` for all test records
- Create cleanup function (optional)

### Step 4: Verify Setup

```bash
python3 verify_test_infrastructure.py
```

### Step 5: Run Tests

```bash
# From project root
export TEST_INFRASTRUCTURE_ENABLED=true
pytest tests/integration/layer_8_business_enablement/ -v
```

---

## 📋 Manual Setup (if script doesn't work)

### GCS Setup

```bash
# 1. Create bucket
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://symphainy-bucket-2025-test

# 2. Set lifecycle policy
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [{
      "action": {"type": "Delete"},
      "condition": {
        "age": 7,
        "matchesPrefix": ["test/"]
      }
    }]
  }
}
EOF
gsutil lifecycle set lifecycle.json gs://symphainy-bucket-2025-test

# 3. Create service account
gcloud iam service-accounts create test-service-account \
    --display-name="Test Service Account"

# 4. Grant permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:test-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# 5. Create key
gcloud iam service-accounts keys create test-credentials.json \
    --iam-account=test-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### Supabase Setup

1. Go to Supabase Dashboard → SQL Editor
2. Run `setup_supabase_test_isolation.sql`
3. Or manually use `tenant_id = 'test_tenant'` for test records

### Configuration

Create `.env.test`:

```bash
TEST_INFRASTRUCTURE_ENABLED=true
TEST_GCS_BUCKET=symphainy-bucket-2025-test
TEST_GCS_CREDENTIALS=/path/to/test-credentials.json
TEST_SUPABASE_URL=https://xxx.supabase.co
TEST_SUPABASE_SERVICE_KEY=your_service_key
TEST_TENANT_ID=test_tenant
```

---

## ✅ Verification Checklist

- [ ] GCS bucket exists: `gs://symphainy-bucket-2025-test`
- [ ] Lifecycle policy set (auto-delete after 7 days)
- [ ] Service account created
- [ ] Credentials file exists: `test-credentials.json`
- [ ] `.env.test` configured with Supabase credentials
- [ ] Supabase test isolation set up
- [ ] `verify_test_infrastructure.py` passes

---

## 🔒 Security Notes

1. **Never commit credentials!**
   ```bash
   # Add to .gitignore
   echo "test-credentials.json" >> .gitignore
   echo ".env.test" >> .gitignore
   ```

2. **Use separate service account** (not production credentials)

3. **Test tenant isolation** (separate from production data)

---

## 🐛 Troubleshooting

### GCS Authentication Error
```bash
# Verify credentials
gcloud auth activate-service-account --key-file=test-credentials.json
gsutil ls gs://symphainy-bucket-2025-test/
```

### Supabase Connection Error
```bash
# Verify URL and key
curl -H "apikey: YOUR_SERVICE_KEY" https://xxx.supabase.co/rest/v1/
```

### Tests Still Skipping
```bash
# Check environment variable
echo $TEST_INFRASTRUCTURE_ENABLED

# Load .env.test
export $(cat .env.test | xargs)
```

---

## 📚 More Information

- **Full Guide**: `INFRASTRUCTURE_SETUP_GUIDE.md`
- **Strategy**: `INFRASTRUCTURE_TESTING_STRATEGY.md`
- **Root Cause Analysis**: `ROOT_CAUSE_ANALYSIS.md`

