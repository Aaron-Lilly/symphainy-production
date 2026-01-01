# Troubleshooting Test Infrastructure Setup

## Common Errors and Solutions

### Error: "AccessDeniedException: 403 Provided scope(s) are not authorized"

**Problem:** Your gcloud credentials don't have permission to create GCS buckets.

**Solution Options:**

#### Option 1: Request Permissions (Recommended)
Ask your GCP admin to grant you one of these roles:
- `roles/storage.admin` (full storage access)
- `roles/storage.objectAdmin` (can create buckets and manage objects)
- `roles/iam.serviceAccountAdmin` (can create service accounts)

#### Option 2: Use Existing Bucket
If you can't create buckets, use an existing bucket:

```bash
# Edit setup_test_infrastructure.sh and change:
TEST_BUCKET_NAME="symphainy-bucket-2025-test"
# To an existing bucket you have access to:
TEST_BUCKET_NAME="your-existing-bucket"
```

#### Option 3: Use Service Account with Permissions
If you have a service account with permissions:

```bash
# Activate service account
gcloud auth activate-service-account SERVICE_ACCOUNT_EMAIL --key-file=KEY_FILE.json

# Then run setup script
bash tests/integration/layer_8_business_enablement/setup_test_infrastructure.sh
```

#### Option 4: Manual Setup (Skip Bucket Creation)
If you can't create buckets, manually set up what you can:

1. **Skip bucket creation** - Use existing bucket or ask admin to create it
2. **Create service account manually:**
   ```bash
   gcloud iam service-accounts create test-service-account \
       --display-name="Test Service Account" \
       --project=symphainymvp-devbox
   ```
3. **Grant permissions:**
   ```bash
   gcloud projects add-iam-policy-binding symphainymvp-devbox \
       --member="serviceAccount:test-service-account@symphainymvp-devbox.iam.gserviceaccount.com" \
       --role="roles/storage.objectAdmin"
   ```
4. **Create key:**
   ```bash
   gcloud iam service-accounts keys create test-credentials.json \
       --iam-account=test-service-account@symphainymvp-devbox.iam.gserviceaccount.com
   ```
5. **Create .env.test manually:**
   ```bash
   cat > .env.test << EOF
   TEST_INFRASTRUCTURE_ENABLED=true
   TEST_GCS_BUCKET=your-existing-bucket-name
   TEST_GCS_CREDENTIALS=$(pwd)/test-credentials.json
   GCS_PROJECT_ID=symphainymvp-devbox
   TEST_SUPABASE_URL=your_supabase_url
   TEST_SUPABASE_SERVICE_KEY=your_service_key
   TEST_TENANT_ID=test_tenant
   EOF
   ```

---

### Error: "Bucket already exists"

**Solution:** The script will detect this and continue. No action needed.

---

### Error: "Service account already exists"

**Solution:** The script will detect this and continue. No action needed.

---

### Error: "gcloud: command not found"

**Solution:** Install Google Cloud SDK:
```bash
# Follow: https://cloud.google.com/sdk/docs/install
```

---

### Error: "No default project set"

**Solution:** Set your project:
```bash
gcloud config set project symphainymvp-devbox
```

---

### Error: "Permission denied" when running script

**Solution:** Make script executable:
```bash
chmod +x tests/integration/layer_8_business_enablement/setup_test_infrastructure.sh
```

Or run with bash:
```bash
bash tests/integration/layer_8_business_enablement/setup_test_infrastructure.sh
```

---

## Checking Your Permissions

### Check Current Project
```bash
gcloud config get-value project
```

### Check Current Account
```bash
gcloud auth list
```

### Check Your Roles
```bash
gcloud projects get-iam-policy symphainymvp-devbox \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:$(gcloud config get-value account)"
```

### Test Bucket Creation Permission
```bash
# Try creating a test bucket (will fail if no permission)
gsutil mb -p symphainymvp-devbox -l us-central1 gs://test-bucket-permission-check
gsutil rb gs://test-bucket-permission-check  # Clean up if it worked
```

---

## Workaround: Use Existing Infrastructure

If you can't create new resources, you can use existing infrastructure:

### Use Existing GCS Bucket

1. **Find an existing bucket you have access to:**
   ```bash
   gsutil ls
   ```

2. **Update .env.test:**
   ```bash
   TEST_GCS_BUCKET=your-existing-bucket-name
   ```

3. **Ensure bucket has lifecycle policy for test/ prefix:**
   ```bash
   # Create lifecycle.json
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
   
   # Apply to existing bucket
   gsutil lifecycle set lifecycle.json gs://your-existing-bucket-name
   ```

### Use Existing Service Account

If you have an existing service account with storage permissions:

1. **List service accounts:**
   ```bash
   gcloud iam service-accounts list
   ```

2. **Create key for existing account:**
   ```bash
   gcloud iam service-accounts keys create test-credentials.json \
       --iam-account=EXISTING_ACCOUNT@symphainymvp-devbox.iam.gserviceaccount.com
   ```

3. **Update .env.test:**
   ```bash
   TEST_GCS_CREDENTIALS=/path/to/test-credentials.json
   ```

---

## Next Steps After Fixing Permissions

Once you have the right permissions:

1. **Re-run setup script:**
   ```bash
   bash tests/integration/layer_8_business_enablement/setup_test_infrastructure.sh
   ```

2. **Or continue manually:**
   - Follow the manual setup steps above
   - Update `.env.test` with your configuration
   - Run `verify_test_infrastructure.py` to check setup

---

## Getting Help

If you're stuck:
1. Check your GCP project permissions
2. Contact your GCP admin for bucket creation permissions
3. Use existing infrastructure if available
4. Check `INFRASTRUCTURE_SETUP_GUIDE.md` for detailed instructions

