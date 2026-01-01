# GCS Credentials Pattern Improvement - Use Supabase Pattern

## 🎯 Problem

**GCS adapter uses file paths** for credentials, which:
- ❌ Requires path resolution (complex, error-prone)
- ❌ Creates SSH/GCE protection concerns
- ❌ Different from Supabase pattern (inconsistent)
- ❌ Harder to manage in containerized environments

**Supabase adapter uses direct credentials** (keys/URLs), which:
- ✅ Simple and straightforward
- ✅ No path resolution needed
- ✅ Works well in containers
- ✅ Consistent with other adapters

## ✅ Solution: Use Supabase Pattern for GCS

**Store credentials as JSON string in environment variable** (like Supabase keys), not file paths.

### **Google Cloud Storage Support**

GCS Python client supports credentials in multiple ways:
1. ✅ **File path** (current): `storage.Client.from_service_account_json(path)`
2. ✅ **Credentials object** (better): `storage.Client(credentials=creds)`
3. ✅ **Service account info dict** (best): `Credentials.from_service_account_info(dict)`

We can use option 3 - pass credentials as JSON string, parse to dict, create credentials object.

---

## 📋 Implementation

### **1. Environment Variables**

**Current** (file path):
```bash
GCS_CREDENTIALS_PATH=/path/to/credentials.json
```

**New** (JSON string - preferred):
```bash
GCS_CREDENTIALS_JSON='{"type":"service_account","project_id":"...","private_key_id":"...","private_key":"...","client_email":"...","client_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_x509_cert_url":"..."}'
```

**Backward Compatibility**:
- Support both `GCS_CREDENTIALS_JSON` (preferred) and `GCS_CREDENTIALS_PATH` (fallback)
- If both are set, `GCS_CREDENTIALS_JSON` takes precedence

### **2. ConfigAdapter**

```python
def get_gcs_credentials_json(self) -> Optional[str]:
    """Get GCS credentials as JSON string (preferred method)."""
    return self.get("GCS_CREDENTIALS_JSON")

def get_gcs_credentials_path(self) -> Optional[str]:
    """Get GCS credentials file path (fallback for backward compatibility)."""
    return self.get("GCS_CREDENTIALS_PATH")
```

### **3. InfrastructureConfig**

```python
def _get_gcs_config(self) -> Dict[str, Any]:
    """Get GCS configuration - supports both JSON and file path."""
    project_id = self.config_adapter.get_gcs_project_id()
    bucket_name = self.config_adapter.get_gcs_bucket_name() or "symphainy-platform-files"
    
    # Prefer JSON credentials (Supabase pattern)
    credentials_json = self.config_adapter.get_gcs_credentials_json()
    credentials_path = None
    
    if credentials_json:
        # Use JSON credentials (no path resolution needed!)
        self.logger.info("✅ Using GCS credentials from GCS_CREDENTIALS_JSON")
    else:
        # Fallback to file path (backward compatibility)
        credentials_path = self.config_adapter.get_gcs_credentials_path()
        if credentials_path:
            # Resolve path (only if using file path)
            resolved_path = ensure_absolute_path(credentials_path)
            credentials_path = str(resolved_path)
            self._verify_not_ssh_credentials(credentials_path, "GCS")
            self.logger.info("✅ Using GCS credentials from GCS_CREDENTIALS_PATH")
    
    return {
        "project_id": project_id,
        "bucket_name": bucket_name,
        "credentials_json": credentials_json,  # New: JSON string
        "credentials_path": credentials_path   # Fallback: File path
    }
```

### **4. GCSFileAdapter**

```python
def __init__(self, project_id: str, bucket_name: str, 
             credentials_json: str = None, credentials_path: str = None):
    """
    Initialize GCS adapter with credentials.
    
    Args:
        project_id: GCP project ID
        bucket_name: GCS bucket name
        credentials_json: Service account credentials as JSON string (preferred)
        credentials_path: Path to credentials file (fallback)
    """
    from google.oauth2 import service_account
    from google.cloud import storage
    import json
    
    self.project_id = project_id
    self.bucket_name = bucket_name
    
    # Prefer JSON credentials (Supabase pattern)
    if credentials_json:
        try:
            # Parse JSON string to dict
            creds_dict = json.loads(credentials_json)
            
            # Create credentials object from dict
            credentials = service_account.Credentials.from_service_account_info(
                creds_dict
            )
            
            # Create client with credentials object
            self._client = storage.Client(
                project=project_id,
                credentials=credentials
            )
            logger.info("✅ GCS client initialized with JSON credentials (Supabase pattern)")
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"❌ Failed to parse GCS credentials JSON: {e}")
            raise ValueError(f"Invalid GCS credentials JSON: {e}")
    
    # Fallback to file path (backward compatibility)
    elif credentials_path:
        if not os.path.exists(credentials_path):
            logger.warning(f"⚠️ Credentials file not found: {credentials_path}")
            credentials_path = None
        else:
            self._client = storage.Client.from_service_account_json(
                credentials_path, 
                project=project_id
            )
            logger.info("✅ GCS client initialized with file path credentials")
    
    # No explicit credentials - use Application Default Credentials
    if not hasattr(self, '_client') or self._client is None:
        self._client = storage.Client(project=project_id)
        logger.info("✅ GCS client initialized with Application Default Credentials")
    
    self._bucket = self._client.bucket(bucket_name)
```

---

## ✅ Benefits

### **1. Eliminates Path Resolution**
- ✅ No file paths = no path resolution needed
- ✅ No complex project root detection
- ✅ No SSH/GCE protection concerns
- ✅ Simpler code

### **2. Consistent with Supabase**
- ✅ Same pattern: credentials in environment variable
- ✅ No file paths
- ✅ Works well in containers
- ✅ Easier to manage

### **3. Better Security**
- ✅ Credentials can be stored in secret managers (as JSON strings)
- ✅ No file system access needed
- ✅ Works in read-only file systems
- ✅ Easier to rotate credentials

### **4. Container-Friendly**
- ✅ No need to mount credential files
- ✅ Credentials in environment variables (standard practice)
- ✅ Works with Kubernetes secrets
- ✅ Works with Docker secrets

### **5. Backward Compatible**
- ✅ Still supports `GCS_CREDENTIALS_PATH` (file path)
- ✅ Prefers `GCS_CREDENTIALS_JSON` (new method)
- ✅ Gradual migration path

---

## 🔄 Migration Path

### **Phase 1: Add Support** (Current)
- ✅ Add `GCS_CREDENTIALS_JSON` support
- ✅ Keep `GCS_CREDENTIALS_PATH` for backward compatibility
- ✅ Prefer JSON if both are set

### **Phase 2: Update Documentation**
- ✅ Document new `GCS_CREDENTIALS_JSON` method
- ✅ Recommend JSON over file paths
- ✅ Update examples

### **Phase 3: Migrate** (Optional)
- ⚠️ Update `.env.secrets` to use `GCS_CREDENTIALS_JSON`
- ⚠️ Remove `GCS_CREDENTIALS_PATH` (or keep as fallback)

---

## 📊 Comparison

### **Before (File Path)**
```python
# Environment
GCS_CREDENTIALS_PATH=/path/to/credentials.json

# Code
credentials_path = config.get("GCS_CREDENTIALS_PATH")
resolved_path = ensure_absolute_path(credentials_path)  # Complex!
verify_not_ssh_credentials(resolved_path)  # Protection needed
client = storage.Client.from_service_account_json(resolved_path)
```

**Issues**:
- ❌ Path resolution complexity
- ❌ SSH/GCE protection concerns
- ❌ File system dependencies
- ❌ Harder in containers

### **After (JSON String)**
```python
# Environment
GCS_CREDENTIALS_JSON='{"type":"service_account",...}'

# Code
credentials_json = config.get("GCS_CREDENTIALS_JSON")
creds_dict = json.loads(credentials_json)  # Simple!
credentials = Credentials.from_service_account_info(creds_dict)
client = storage.Client(credentials=credentials)
```

**Benefits**:
- ✅ No path resolution
- ✅ No SSH/GCE concerns
- ✅ No file system dependencies
- ✅ Works great in containers

---

## 🎯 Recommendation

**Implement JSON credentials support** (Supabase pattern):
1. ✅ Add `GCS_CREDENTIALS_JSON` support
2. ✅ Keep `GCS_CREDENTIALS_PATH` for backward compatibility
3. ✅ Prefer JSON if both are set
4. ✅ Document new method
5. ✅ Gradually migrate to JSON

**This eliminates**:
- ❌ Path resolution complexity
- ❌ SSH/GCE protection concerns
- ❌ File system dependencies
- ❌ Inconsistency with Supabase pattern

---

## ✅ Summary

**Problem**: GCS uses file paths (different from Supabase, complex, error-prone)
**Solution**: Use JSON credentials in environment variable (same as Supabase)
**Result**: Simpler, more secure, container-friendly, consistent with other adapters







