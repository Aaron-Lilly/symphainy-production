# SSH Access Issue Fix

## Problem Identified

The recent changes to Layer 8 Business Enablement test infrastructure are modifying the **global** `GOOGLE_APPLICATION_CREDENTIALS` environment variable, which affects all GCP authentication including SSH access to the VM.

### Root Causes

1. **Test Code (`test_file_parser_core.py` lines 45-57)**: Modifies `GOOGLE_APPLICATION_CREDENTIALS` globally
2. **GCS Adapter (`gcs_file_adapter.py` line 84)**: Sets `GOOGLE_APPLICATION_CREDENTIALS` when initializing

### Why This Breaks SSH

- `GOOGLE_APPLICATION_CREDENTIALS` is used by **all** GCP tools and services for authentication
- When this variable is set to an invalid path or wrong credentials, it breaks:
  - SSH access to GCP VMs
  - gcloud CLI commands
  - Any GCP service authentication

## Solution

We need to:
1. **Stop modifying `GOOGLE_APPLICATION_CREDENTIALS` globally**
2. **Pass credentials directly** to GCS client without setting environment variable
3. **Use test-specific credential variables** that don't affect global GCP auth

## Fixes Applied

1. ✅ **Updated `gcs_file_adapter.py`**: Removed global modification of `GOOGLE_APPLICATION_CREDENTIALS`. Now passes credentials directly via `from_service_account_json()` which doesn't require the environment variable.

2. ✅ **Updated `test_file_parser_core.py`**: Removed `GOOGLE_APPLICATION_CREDENTIALS` from the list of variables being modified. Now only modifies test-specific variables (`GCS_CREDENTIALS_PATH`, `TEST_GCS_CREDENTIALS`).

## How It Works Now

- **GCS Adapter**: Uses `storage.Client.from_service_account_json(credentials_path, project=project_id)` which reads credentials directly from the file without needing the environment variable.

- **Test Code**: Only modifies test-specific credential variables, leaving `GOOGLE_APPLICATION_CREDENTIALS` untouched for SSH and other GCP tools.

- **Config Adapter**: Still checks `GOOGLE_APPLICATION_CREDENTIALS` as a fallback, but it won't be modified by our code.

## Verification Steps

After fix, verify:
1. **SSH access to GCP VM**: Try connecting via SSH - it should work normally
2. **Tests still work**: Run tests to ensure they still function with test credentials
3. **Production GCP services**: Verify other GCP services are unaffected

## If SSH Still Doesn't Work

If SSH access is still broken after this fix, check:

1. **Current value of `GOOGLE_APPLICATION_CREDENTIALS`**:
   ```bash
   echo $GOOGLE_APPLICATION_CREDENTIALS
   ```

2. **If it's set to an invalid path**, unset it:
   ```bash
   unset GOOGLE_APPLICATION_CREDENTIALS
   ```

3. **Or set it to the correct credentials file**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/correct/credentials.json
   ```

4. **Verify credentials file exists and is valid**:
   ```bash
   test -f "$GOOGLE_APPLICATION_CREDENTIALS" && echo "File exists" || echo "File missing"
   ```

