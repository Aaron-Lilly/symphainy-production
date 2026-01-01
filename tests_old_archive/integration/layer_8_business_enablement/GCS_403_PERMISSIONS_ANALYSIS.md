# GCS 403 Permissions Issue - Analysis

## Issue

**Error**: `403 Forbidden: Provided scope(s) are not authorized`

This error occurs when uploading files to GCS, indicating the service account credentials don't have the required permissions/scopes.

## Root Cause Analysis

### 1. Credentials File Location
- **Expected Path** (from env_secrets_for_cursor.md): `backend/symphainymvp-devbox-40d941571d46.json`
- **Actual Path**: `symphainy-platform/backend/symphainymvp-devbox-40d941571d46.json`
- **Issue**: Relative path not resolved correctly when running from different directories (e.g., tests/)

### 2. Service Account Details
- **Service Account**: `409769699232-compute@developer.gserviceaccount.com`
- **Type**: Compute Engine default service account
- **Project**: `symphainymvp-devbox`

### 3. Permissions Issue
The 403 error "Provided scope(s) are not authorized" suggests:
- The service account may not have the right IAM roles for GCS bucket access
- The service account may not have the right OAuth scopes
- The bucket IAM policy may not grant access to this service account

## Fixes Applied

### Fix 1: Path Resolution
**File**: `gcs_file_adapter.py`

Added path resolution logic to handle relative paths:
- Resolves relative paths relative to project root (where `symphainy-platform/` exists)
- Falls back to current working directory if project root not found
- Handles cases when running from `tests/`, `symphainy-platform/`, or project root

### Fix 2: Path Resolution in Public Works Foundation
**File**: `public_works_foundation_service.py`

Added similar path resolution before passing to GCS adapter to ensure credentials are found.

## Required GCS Permissions

The service account needs these IAM roles for GCS bucket operations:
- `roles/storage.objectCreator` - To upload files
- `roles/storage.objectViewer` - To read files
- `roles/storage.objectAdmin` - For full object management (optional)

Or the bucket IAM policy needs to grant these permissions to the service account.

## Required OAuth Scopes

The service account credentials need these scopes:
- `https://www.googleapis.com/auth/cloud-platform` (full access)
- OR `https://www.googleapis.com/auth/devstorage.full_control` (GCS full control)
- OR `https://www.googleapis.com/auth/devstorage.read_write` (GCS read/write)

## Verification Steps

1. **Check Service Account IAM Roles**:
   ```bash
   gcloud projects get-iam-policy symphainymvp-devbox \
     --flatten="bindings[].members" \
     --filter="bindings.members:409769699232-compute@developer.gserviceaccount.com"
   ```

2. **Check Bucket IAM Policy**:
   ```bash
   gsutil iam get gs://symphainy-bucket-2025
   ```

3. **Verify Credentials File Scopes**:
   ```python
   import json
   creds = json.load(open('symphainy-platform/backend/symphainymvp-devbox-40d941571d46.json'))
   print('Scopes:', creds.get('scopes', 'Not specified (uses default)'))
   ```

4. **Test Upload with Explicit Credentials**:
   ```python
   from google.cloud import storage
   client = storage.Client.from_service_account_json(
       'symphainy-platform/backend/symphainymvp-devbox-40d941571d46.json',
       project='symphainymvp-devbox'
   )
   bucket = client.bucket('symphainy-bucket-2025')
   blob = bucket.blob('test.txt')
   blob.upload_from_string('test content', content_type='text/plain')
   ```

## Next Steps

1. **Verify Path Resolution Works**: Run tests to ensure credentials file is found
2. **Check IAM Permissions**: Verify service account has required GCS roles
3. **Check Bucket IAM**: Verify bucket grants access to service account
4. **If Still Failing**: May need to create a dedicated service account with explicit GCS permissions (separate from compute service account)

## Important Notes

- **NEVER modify GOOGLE_APPLICATION_CREDENTIALS** - This is for SSH/VM access
- **Use GCS_CREDENTIALS_PATH** - This is for bucket access (separate concern)
- **Path Resolution** - Now handles relative paths correctly
- **Service Account Separation** - Consider using a dedicated GCS service account instead of compute service account


