# Setup Workaround for Limited Permissions

## Current Situation

You're running on a GCP Compute Engine VM with a compute service account that has limited permissions. The setup script can't create new buckets or service accounts, but we can work around this!

## ✅ What We've Done

1. **Created manual setup script** - Uses existing bucket instead of creating new one
2. **Updated configuration** - Uses `symphainy-bucket-2025` (your existing bucket)
3. **Application Default Credentials** - Uses compute service account credentials automatically

## 🔧 Current Configuration

Your `.env.test` file should have:
```bash
TEST_INFRASTRUCTURE_ENABLED=true
TEST_GCS_BUCKET=symphainy-bucket-2025
GCS_PROJECT_ID=symphainymvp-devbox
# Credentials: Using application default credentials (compute service account)
```

## 📋 Remaining Steps

### Step 1: Add Supabase Credentials

Edit `.env.test` and add your Supabase credentials:

```bash
# Option A: Test-specific Supabase
TEST_SUPABASE_URL=https://xxx.supabase.co
TEST_SUPABASE_SERVICE_KEY=your_test_service_key

# Option B: Use existing Supabase config
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
```

### Step 2: Verify Setup

```bash
cd tests/integration/layer_8_business_enablement
python3 verify_test_infrastructure.py
```

### Step 3: Test File Operations

The compute service account should be able to:
- ✅ Read/write files in `gs://symphainy-bucket-2025`
- ✅ Use `test/` prefix for test files
- ❌ Create new buckets (not needed - using existing)
- ❌ Create service accounts (not needed - using compute account)

### Step 4: Run Tests

```bash
export TEST_INFRASTRUCTURE_ENABLED=true
pytest tests/integration/layer_8_business_enablement/ -v
```

## 🔒 Security Notes

**Using Compute Service Account:**
- ✅ Works for testing
- ✅ No additional credentials needed
- ⚠️  Less isolated than dedicated test service account
- ⚠️  Uses same credentials as VM

**For Production Testing:**
- Consider asking admin to create dedicated test service account
- Or use existing service account with test bucket

## 🎯 What Works Now

- ✅ GCS file storage (using existing bucket)
- ✅ Test file isolation (using `test/` prefix)
- ✅ Application default credentials
- ⏳ Supabase (needs credentials)

## 🎯 What Needs Admin Help

If you want better isolation:

1. **Ask admin to create test bucket:**
   ```bash
   gsutil mb -p symphainymvp-devbox -l us-central1 gs://symphainy-bucket-2025-test
   ```

2. **Ask admin to create test service account:**
   ```bash
   gcloud iam service-accounts create test-service-account \
       --display-name="Test Service Account" \
       --project=symphainymvp-devbox
   ```

3. **Ask admin to grant permissions:**
   ```bash
   gcloud projects add-iam-policy-binding symphainymvp-devbox \
       --member="serviceAccount:test-service-account@symphainymvp-devbox.iam.gserviceaccount.com" \
       --role="roles/storage.objectAdmin"
   ```

But for now, **the current setup will work** with the existing bucket and compute service account!

