# Additional Risk Found: GOOGLE_APPLICATION_CREDENTIALS Removal

## 🚨 Critical Issue

**File**: `symphainy-platform/foundations/public_works_foundation/public_works_foundation_service.py`  
**Line**: 1582  
**Issue**: Code **removes** `GOOGLE_APPLICATION_CREDENTIALS` if it points to a non-existent file

## Problem

```python
# Line 1575-1582
env_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if env_creds and not os.path.exists(env_creds):
    self.logger.warning(
        f"⚠️ GOOGLE_APPLICATION_CREDENTIALS env var points to non-existent file: {env_creds}. "
        f"Unsetting to allow Application Default Credentials."
    )
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)  # ❌ RISKY: Removes env var
```

**Why This Is Risky**:

1. **Path Resolution Issues**: The file might exist but not be found due to:
   - Relative vs absolute paths
   - Different working directory
   - Path resolution differences

2. **SSH Dependency**: If `GOOGLE_APPLICATION_CREDENTIALS` was set correctly for SSH access, removing it breaks SSH.

3. **Silent Failure**: The code logs a warning but doesn't fail - it just removes the env var and continues.

4. **No Verification**: The code doesn't verify that Application Default Credentials will work after removing the env var.

## Recommended Fix

**Option 1: Don't Remove, Just Warn** (Safest)
```python
env_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if env_creds and not os.path.exists(env_creds):
    self.logger.warning(
        f"⚠️ GOOGLE_APPLICATION_CREDENTIALS env var points to non-existent file: {env_creds}. "
        f"This may cause authentication issues. "
        f"Will attempt to use Application Default Credentials as fallback."
    )
    # DO NOT remove - let GCS client handle fallback
    # The GCS adapter already handles missing credentials gracefully
```

**Option 2: Verify Before Removing** (More Safe)
```python
env_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if env_creds:
    # Try multiple path resolution methods
    resolved_paths = [
        env_creds,  # Original path
        os.path.abspath(env_creds),  # Absolute path
        os.path.expanduser(env_creds),  # Expand ~
    ]
    
    # Check if any resolved path exists
    if not any(os.path.exists(p) for p in resolved_paths):
        # Only remove if we're CERTAIN it doesn't exist
        # AND we have explicit credentials_path to use instead
        if credentials_path and os.path.exists(credentials_path):
            self.logger.warning(
                f"⚠️ GOOGLE_APPLICATION_CREDENTIALS points to non-existent file: {env_creds}. "
                f"Using explicit credentials_path instead: {credentials_path}"
            )
            # Safe to remove since we have explicit credentials
            os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
        else:
            # Don't remove - might be needed for SSH or other GCP tools
            self.logger.warning(
                f"⚠️ GOOGLE_APPLICATION_CREDENTIALS points to non-existent file: {env_creds}. "
                f"Keeping env var (may be needed for SSH/GCP tools). "
                f"GCS adapter will use Application Default Credentials as fallback."
            )
```

**Option 3: Use Test-Specific Credentials** (Best for Tests)
```python
# In test code, use test-specific credential variables
# Don't rely on GOOGLE_APPLICATION_CREDENTIALS at all
gcs_adapter = GCSFileAdapter(
    project_id=project_id,
    bucket_name=bucket_name,
    credentials_path=os.getenv("TEST_GCS_CREDENTIALS") or os.getenv("GCS_CREDENTIALS_PATH")
    # This never touches GOOGLE_APPLICATION_CREDENTIALS
)
```

## Immediate Action Required

1. **Review the code** at line 1582 in `public_works_foundation_service.py`
2. **Decide on fix approach** (Option 1 is safest)
3. **Test thoroughly** to ensure SSH access is not affected
4. **Add to guardrails** to prevent future modifications

## Impact Assessment

**Current Risk Level**: 🟡 **MEDIUM**

- The code only removes the env var if the file doesn't exist
- But path resolution issues could cause false negatives
- Removing the env var could break SSH if it was set correctly

**After Fix**: 🟢 **LOW**

- No modification of critical env vars
- Graceful fallback without removal
- SSH access protected

