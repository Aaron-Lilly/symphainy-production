# GCP Admin Checklist - Fix GCS Write Permissions

## 🔍 What to Check

### Step 1: Identify the Service Account

**Service Account Email:** `409769699232-compute@developer.gserviceaccount.com`  
**Project:** `symphainymvp-devbox`  
**Bucket:** `symphainy-bucket-2025`

### Step 2: Check Current Permissions

#### Option A: Using GCP Console (Web UI)

1. **Go to IAM & Admin:**
   - Navigate to: https://console.cloud.google.com/iam-admin/iam?project=symphainymvp-devbox
   - Or: GCP Console → IAM & Admin → IAM

2. **Find the Service Account:**
   - Search for: `409769699232-compute@developer.gserviceaccount.com`
   - Or look for: `Compute Engine default service account`

3. **Check Roles:**
   - Look at the "Roles" column for this service account
   - Check if it has any of these:
     - `Storage Object Admin` (roles/storage.objectAdmin)
     - `Storage Admin` (roles/storage.admin)
     - `Storage Object Creator` (roles/storage.objectCreator)
     - `Storage Object Viewer` (roles/storage.objectViewer)

#### Option B: Using gcloud CLI

```bash
# Check IAM policy for the project
gcloud projects get-iam-policy symphainymvp-devbox \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:serviceAccount:409769699232-compute@developer.gserviceaccount.com"

# Check bucket-level permissions
gsutil iam get gs://symphainy-bucket-2025
```

### Step 3: Check Bucket-Level Permissions

1. **Go to Cloud Storage:**
   - Navigate to: https://console.cloud.google.com/storage/browser?project=symphainymvp-devbox
   - Or: GCP Console → Cloud Storage → Buckets

2. **Select the Bucket:**
   - Click on: `symphainy-bucket-2025`

3. **Check Permissions:**
   - Click on "Permissions" tab
   - Look for: `409769699232-compute@developer.gserviceaccount.com`
   - Check what role it has (if any)

## 🔧 How to Fix

### Option 1: Grant Project-Level Permissions (Recommended)

**Using GCP Console:**

1. Go to: https://console.cloud.google.com/iam-admin/iam?project=symphainymvp-devbox
2. Click "Grant Access" (or "Edit" if service account already exists)
3. In "New principals", enter: `409769699232-compute@developer.gserviceaccount.com`
4. Select role: **Storage Object Admin** (or **Storage Admin** for full access)
5. Click "Save"

**Using gcloud CLI:**

```bash
# Grant Storage Object Admin role (recommended - can read/write objects)
gcloud projects add-iam-policy-binding symphainymvp-devbox \
    --member="serviceAccount:409769699232-compute@developer.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# OR grant Storage Admin (full access - can manage buckets too)
gcloud projects add-iam-policy-binding symphainymvp-devbox \
    --member="serviceAccount:409769699232-compute@developer.gserviceaccount.com" \
    --role="roles/storage.admin"
```

### Option 2: Grant Bucket-Level Permissions (More Restrictive)

**Using GCP Console:**

1. Go to: https://console.cloud.google.com/storage/browser/symphainy-bucket-2025?project=symphainymvp-devbox
2. Click on the bucket: `symphainy-bucket-2025`
3. Click "Permissions" tab
4. Click "Grant Access"
5. In "New principals", enter: `409769699232-compute@developer.gserviceaccount.com`
6. Select role: **Storage Object Admin**
7. Click "Save"

**Using gsutil CLI:**

```bash
# Grant Storage Object Admin to specific bucket
gsutil iam ch serviceAccount:409769699232-compute@developer.gserviceaccount.com:roles/storage.objectAdmin gs://symphainy-bucket-2025
```

### Option 3: Use a Different Service Account (If You Can't Modify Compute Service Account)

If you can't modify the compute service account permissions, you can:

1. **Create a new service account:**
   ```bash
   gcloud iam service-accounts create test-storage-sa \
       --display-name="Test Storage Service Account" \
       --project=symphainymvp-devbox
   ```

2. **Grant it permissions:**
   ```bash
   gcloud projects add-iam-policy-binding symphainymvp-devbox \
       --member="serviceAccount:test-storage-sa@symphainymvp-devbox.iam.gserviceaccount.com" \
       --role="roles/storage.objectAdmin"
   ```

3. **Create a key:**
   ```bash
   gcloud iam service-accounts keys create test-storage-key.json \
       --iam-account=test-storage-sa@symphainymvp-devbox.iam.gserviceaccount.com
   ```

4. **Update `.env.test`:**
   ```bash
   TEST_GCS_CREDENTIALS=/path/to/test-storage-key.json
   GCS_CREDENTIALS_PATH=/path/to/test-storage-key.json
   ```

## ✅ Verify the Fix

After granting permissions, verify it works:

```bash
cd /home/founders/demoversion/symphainy_source

# Test direct upload
python3 -c "
from google.cloud import storage
from pathlib import Path
import json

key_file = Path('symphainy-platform/backend/symphainymvp-devbox-40d941571d46.json')
with open(key_file) as f:
    key_data = json.load(f)

client = storage.Client.from_service_account_json(str(key_file), project=key_data['project_id'])
bucket = client.bucket('symphainy-bucket-2025')
blob = bucket.blob('test/verify_permissions.txt')

try:
    blob.upload_from_string(b'Permission test')
    print('✅ Upload successful - permissions are correct!')
    blob.delete()
    print('✅ Delete successful!')
except Exception as e:
    print(f'❌ Still failing: {e}')
"
```

## 🎯 Recommended Approach

**For Testing:** Use **Option 1** (Project-level Storage Object Admin) - this is the simplest and most common approach.

**For Production:** Consider **Option 2** (Bucket-level) for better security isolation, or **Option 3** (Dedicated service account) for better separation of concerns.

## 📋 Quick Reference

- **Service Account:** `409769699232-compute@developer.gserviceaccount.com`
- **Project:** `symphainymvp-devbox`
- **Bucket:** `symphainy-bucket-2025`
- **Required Role:** `roles/storage.objectAdmin` (minimum) or `roles/storage.admin` (full access)
- **GCP Console IAM:** https://console.cloud.google.com/iam-admin/iam?project=symphainymvp-devbox
- **GCP Console Storage:** https://console.cloud.google.com/storage/browser?project=symphainymvp-devbox

