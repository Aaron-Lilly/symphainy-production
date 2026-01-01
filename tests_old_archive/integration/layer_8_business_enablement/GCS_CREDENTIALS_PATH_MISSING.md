# GCS_CREDENTIALS_PATH Missing from .env.secrets

## Issue Found

**Problem**: `GCS_CREDENTIALS_PATH` is **not set** in `.env.secrets` file.

**Impact**: Platform falls back to Application Default Credentials (compute service account), which causes 403 errors when trying to upload files.

## Current State

### What's in .env.secrets:
- ✅ `GCS_PROJECT_ID=symphainymvp-devbox`
- ✅ `GCS_BUCKET_NAME=symphainy-bucket-2025`
- ❌ `GCS_CREDENTIALS_PATH` - **MISSING**

### What Should Be Added:
```
GCS_CREDENTIALS_PATH=backend/symphainymvp-devbox-40d941571d46.json
```

Or the absolute path:
```
GCS_CREDENTIALS_PATH=symphainy-platform/backend/symphainymvp-devbox-40d941571d46.json
```

## Why This Matters

1. **Without GCS_CREDENTIALS_PATH**: Platform uses Application Default Credentials
   - On GCP VM: Uses compute service account (may have scope limitations)
   - Locally: May not have credentials configured
   - Result: 403 "Provided scope(s) are not authorized"

2. **With GCS_CREDENTIALS_PATH**: Platform uses explicit service account credentials
   - Uses the credentials file directly
   - Has proper scopes and permissions
   - Result: Uploads work correctly (as verified by test script)

## Verification

The verification script (`verify_gcs_permissions.py`) worked because it:
- Used the credentials file path directly
- Didn't rely on `.env.secrets` configuration

The functional test failed because:
- Platform loads config from `.env.secrets`
- `GCS_CREDENTIALS_PATH` is missing
- Falls back to Application Default Credentials
- Gets 403 error

## Solution

**Add to `.env.secrets`**:
```bash
GCS_CREDENTIALS_PATH=backend/symphainymvp-devbox-40d941571d46.json
```

The path resolution fix we made will handle the relative path correctly, resolving it to:
`symphainy-platform/backend/symphainymvp-devbox-40d941571d46.json`

## Note

The credentials file exists and has correct permissions (verified by test script).
The path resolution logic is working correctly.
The only missing piece is the `GCS_CREDENTIALS_PATH` entry in `.env.secrets`.


