# Fix GCS Permissions for Compute Service Account

## Problem

The compute service account (`409769699232-compute@developer.gserviceaccount.com`) doesn't have permission to write to GCS bucket `symphainy-bucket-2025`.

**Error:** `403 Provided scope(s) are not authorized`

## Solutions

### Option 1: Grant Storage Permissions to Compute Service Account (Recommended)

Ask your GCP admin to grant the compute service account storage write permissions:

```bash
# Grant Storage Object Admin role
gcloud projects add-iam-policy-binding symphainymvp-devbox \
    --member="serviceAccount:409769699232-compute@developer.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Or grant Storage Admin (full access)
gcloud projects add-iam-policy-binding symphainymvp-devbox \
    --member="serviceAccount:409769699232-compute@developer.gserviceaccount.com" \
    --role="roles/storage.admin"
```

### Option 2: Use Service Account Key File

If you have a service account key file with permissions:

1. **Find or create service account with permissions:**
   ```bash
   # List service accounts
   gcloud iam service-accounts list
   ```

2. **Use existing key file:**
   ```bash
   # Check if key file exists
   ls -la backend/symphainymvp-devbox-40d941571d46.json
   ```

3. **Update .env.test:**
   ```bash
   TEST_GCS_CREDENTIALS=/path/to/symphainymvp-devbox-40d941571d46.json
   ```

### Option 3: Update VM Service Account Scopes

If you have access to update the VM, you can add storage scopes:

```bash
# Stop VM
gcloud compute instances stop INSTANCE_NAME --zone=ZONE

# Update service account scopes
gcloud compute instances set-service-account INSTANCE_NAME \
    --zone=ZONE \
    --service-account=409769699232-compute@developer.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/cloud-platform

# Start VM
gcloud compute instances start INSTANCE_NAME --zone=ZONE
```

**Note:** This requires VM admin access and will restart the VM.

### Option 4: Use Different Authentication

If you have user credentials with permissions:

```bash
# Authenticate as user
gcloud auth login

# Set application default credentials
gcloud auth application-default login

# Then tests will use your user credentials
```

---

## Quick Check: What Permissions Do We Have?

```bash
# Check current service account
curl -s "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email" -H "Metadata-Flavor: Google"

# Test GCS read access
gsutil ls gs://symphainy-bucket-2025/

# Test GCS write access (will fail if no permission)
echo "test" | gsutil cp - gs://symphainy-bucket-2025/test/permission-test.txt
gsutil rm gs://symphainy-bucket-2025/test/permission-test.txt
```

---

## Recommended Action

**For immediate testing:**
1. Ask GCP admin to grant `roles/storage.objectAdmin` to compute service account
2. Or use service account key file if available

**For long-term:**
- Create dedicated test service account with limited permissions
- Use that for testing instead of compute service account

---

## After Fixing Permissions

Once permissions are granted:

1. **Verify:**
   ```bash
   echo "test" | gsutil cp - gs://symphainy-bucket-2025/test/permission-test.txt
   gsutil rm gs://symphainy-bucket-2025/test/permission-test.txt
   ```

2. **Run tests:**
   ```bash
   export TEST_INFRASTRUCTURE_ENABLED=true
   pytest tests/integration/layer_8_business_enablement/ -v
   ```

