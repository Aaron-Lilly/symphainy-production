# GCS Credentials Architecture - Clear Separation

## 🎯 The Problem

We have **two distinct sets of GCS credentials** that serve different purposes:

1. **SSH/VM Credentials** (`GOOGLE_APPLICATION_CREDENTIALS`)
   - Used for SSH access to GCP VMs
   - Used by `gcloud` CLI and other GCP tools
   - **MUST NEVER be modified or replaced**

2. **Bucket Credentials** (for GCS file storage)
   - Used specifically for accessing GCS buckets to store client files
   - Should be **completely separate** from SSH credentials
   - Should be passed explicitly to GCS adapter

**The Issue**: Current code uses `GOOGLE_APPLICATION_CREDENTIALS` as a fallback for bucket credentials, which creates confusion and risk.

---

## ✅ The Solution: Clear Separation

### **Architectural Principle**

**SSH/VM Credentials** and **Bucket Credentials** are **completely separate concerns**:
- SSH credentials = Infrastructure access (VM, gcloud, etc.)
- Bucket credentials = Application data access (GCS buckets)

They should **never** be mixed or used as fallbacks for each other.

---

## 🔧 Implementation Pattern

### **1. SSH/VM Credentials** (Infrastructure)

**Environment Variable**: `GOOGLE_APPLICATION_CREDENTIALS`

**Purpose**:
- SSH access to GCP VMs
- `gcloud` CLI commands
- Other GCP tool authentication

**Rules**:
- ✅ **NEVER modified** by application code
- ✅ **NEVER used** as fallback for bucket credentials
- ✅ **NEVER removed** by application code
- ✅ Set once at VM/SSH session level

**Usage**:
```python
# ❌ FORBIDDEN - Never modify
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path

# ✅ ALLOWED - Read-only access (for logging/debugging only)
ssh_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
```

---

### **2. Bucket Credentials** (Application Data)

**Environment Variable**: `GCS_CREDENTIALS_PATH`

**Purpose**:
- Accessing GCS buckets for client file storage
- Application-specific GCS operations

**Rules**:
- ✅ **ONLY** use `GCS_CREDENTIALS_PATH` (never `GOOGLE_APPLICATION_CREDENTIALS`)
- ✅ Pass explicitly to GCS adapter
- ✅ If not set, use Application Default Credentials (which may use compute service account on GCP VM)
- ✅ **NEVER** fallback to `GOOGLE_APPLICATION_CREDENTIALS`

**Usage**:
```python
# ✅ CORRECT - Use GCS_CREDENTIALS_PATH explicitly
bucket_creds = os.getenv("GCS_CREDENTIALS_PATH")

gcs_adapter = GCSFileAdapter(
    project_id=project_id,
    bucket_name=bucket_name,
    credentials_path=bucket_creds  # Explicit bucket credentials
)

# ❌ WRONG - Never use GOOGLE_APPLICATION_CREDENTIALS as fallback
bucket_creds = os.getenv("GCS_CREDENTIALS_PATH") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
```

---

## 📋 Configuration Pattern

### **Environment Variables**

```bash
# SSH/VM Credentials (Infrastructure)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/ssh-vm-credentials.json

# Bucket Credentials (Application Data)
GCS_CREDENTIALS_PATH=/path/to/bucket-credentials.json
GCS_PROJECT_ID=your-project-id
GCS_BUCKET_NAME=your-bucket-name
```

**Key Point**: These are **two different files** with **two different purposes**.

---

## 🔧 Code Changes Required

### **1. Update ConfigAdapter** 🔴 **CRITICAL**

**File**: `config_adapter.py`

**Current (Problematic)**:
```python
def get_gcs_credentials_path(self) -> Optional[str]:
    return (
        self.get("GCS_CREDENTIALS_PATH") or
        self.get("GOOGLE_APPLICATION_CREDENTIALS")  # ❌ WRONG: Mixes concerns
    )
```

**Fixed (Clear Separation)**:
```python
def get_gcs_credentials_path(self) -> Optional[str]:
    """
    Raw GCS bucket credentials path retrieval - no business logic.
    
    CRITICAL: This is ONLY for bucket credentials (application data).
    It does NOT use GOOGLE_APPLICATION_CREDENTIALS as fallback, as that
    is for SSH/VM access (infrastructure) and must remain separate.
    
    If GCS_CREDENTIALS_PATH is not set, returns None, which allows
    GCS adapter to use Application Default Credentials (compute service
    account on GCP VM, or GOOGLE_APPLICATION_CREDENTIALS if set - but
    we don't modify it).
    """
    return self.get("GCS_CREDENTIALS_PATH")  # ✅ ONLY bucket credentials
```

---

### **2. Update PublicWorksFoundationService** 🔴 **CRITICAL**

**File**: `public_works_foundation_service.py`

**Current (Problematic)**:
- Checks `GOOGLE_APPLICATION_CREDENTIALS` and warns if file doesn't exist
- Could cause confusion about which credentials are being used

**Fixed (Clear Separation)**:
```python
# Get bucket credentials (ONLY from GCS_CREDENTIALS_PATH)
credentials_path = gcs_config.get("credentials_path")  # This is GCS_CREDENTIALS_PATH

# DO NOT check or modify GOOGLE_APPLICATION_CREDENTIALS
# It's for SSH/VM access, not bucket access

if credentials_path:
    if not os.path.exists(credentials_path):
        self.logger.warning(
            f"⚠️ GCS bucket credentials file not found: {credentials_path}. "
            f"Falling back to Application Default Credentials. "
            f"Set GCS_CREDENTIALS_PATH to use explicit bucket credentials."
        )
        credentials_path = None  # Use Application Default Credentials

# Create GCS adapter with explicit bucket credentials
self.gcs_adapter = GCSFileAdapter(
    project_id=gcs_config.get("project_id"),
    bucket_name=gcs_config["bucket_name"],
    credentials_path=credentials_path  # Explicit bucket credentials (or None for ADC)
)
```

---

### **3. Update GCSFileAdapter Documentation** 🟠 **IMPORTANT**

**File**: `gcs_file_adapter.py`

**Add Clear Documentation**:
```python
class GCSFileAdapter:
    """
    Raw GCS client wrapper for file operations - no business logic.
    
    CREDENTIALS ARCHITECTURE:
    - credentials_path: Explicit bucket credentials (from GCS_CREDENTIALS_PATH)
      Used ONLY for bucket operations (application data).
    - If credentials_path is None: Uses Application Default Credentials
      (compute service account on GCP VM, or GOOGLE_APPLICATION_CREDENTIALS
      if set - but we never modify GOOGLE_APPLICATION_CREDENTIALS).
    
    CRITICAL: This adapter NEVER modifies GOOGLE_APPLICATION_CREDENTIALS,
    which is reserved for SSH/VM access (infrastructure).
    """
```

---

## 📝 Configuration Examples

### **Production (GCP VM)**

```bash
# SSH/VM Credentials (set at VM level, never modified by app)
GOOGLE_APPLICATION_CREDENTIALS=/etc/gcp/ssh-vm-credentials.json

# Bucket Credentials (set in application config)
GCS_CREDENTIALS_PATH=/etc/gcp/bucket-credentials.json
GCS_PROJECT_ID=my-project-id
GCS_BUCKET_NAME=my-bucket-name
```

**On GCP VM**: If `GCS_CREDENTIALS_PATH` is not set, GCS adapter will use the compute service account (which has bucket access), without touching `GOOGLE_APPLICATION_CREDENTIALS`.

---

### **Development (Local)**

```bash
# SSH/VM Credentials (for SSH access to dev VM)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/ssh-vm-credentials.json

# Bucket Credentials (for local testing)
GCS_CREDENTIALS_PATH=/path/to/bucket-credentials.json
GCS_PROJECT_ID=my-project-id
GCS_BUCKET_NAME=my-bucket-name
```

---

### **Testing**

```bash
# SSH/VM Credentials (for SSH access - never modified)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/ssh-vm-credentials.json

# Test Bucket Credentials (test-specific, never touches SSH creds)
TEST_GCS_CREDENTIALS=/path/to/test-bucket-credentials.json
# OR
GCS_CREDENTIALS_PATH=/path/to/test-bucket-credentials.json
```

---

## 🛡️ Guardrails

### **Code Review Checklist**

- [ ] No code modifies `GOOGLE_APPLICATION_CREDENTIALS`
- [ ] No code uses `GOOGLE_APPLICATION_CREDENTIALS` as fallback for bucket credentials
- [ ] All GCS operations use `GCS_CREDENTIALS_PATH` explicitly
- [ ] Clear documentation explains credential separation

### **Test Checklist**

- [ ] Tests use `TEST_GCS_CREDENTIALS` or `GCS_CREDENTIALS_PATH` (not `GOOGLE_APPLICATION_CREDENTIALS`)
- [ ] Protection fixtures verify `GOOGLE_APPLICATION_CREDENTIALS` is never modified
- [ ] Tests can run with different bucket credentials without affecting SSH

---

## ✅ Benefits

1. **Clear Separation**: SSH credentials and bucket credentials are distinct
2. **No Confusion**: Clear which credentials are used for what purpose
3. **SSH Protection**: `GOOGLE_APPLICATION_CREDENTIALS` is never modified
4. **Flexibility**: Can use different credentials for buckets vs SSH
5. **Safety**: Protection fixtures prevent accidental mixing

---

## 🔍 Verification

### **Check Current Configuration**

```bash
# Check SSH/VM credentials (should be set for SSH access)
echo "SSH/VM Credentials: $GOOGLE_APPLICATION_CREDENTIALS"

# Check bucket credentials (should be separate)
echo "Bucket Credentials: $GCS_CREDENTIALS_PATH"

# Verify they're different files
if [ "$GOOGLE_APPLICATION_CREDENTIALS" = "$GCS_CREDENTIALS_PATH" ]; then
    echo "⚠️ WARNING: SSH and bucket credentials are the same file!"
    echo "This is not recommended - use separate credentials for security."
fi
```

---

## 📚 Summary

**The Rule**: 
- `GOOGLE_APPLICATION_CREDENTIALS` = SSH/VM access (infrastructure) - **NEVER modified**
- `GCS_CREDENTIALS_PATH` = Bucket access (application data) - **Explicit and separate**

**The Pattern**:
- Always use `GCS_CREDENTIALS_PATH` for bucket operations
- Never use `GOOGLE_APPLICATION_CREDENTIALS` as fallback for bucket credentials
- If `GCS_CREDENTIALS_PATH` is not set, use Application Default Credentials (which may use compute service account on GCP VM)

**The Result**:
- Clear separation of concerns
- SSH access always protected
- Bucket operations use explicit credentials
- No confusion about which credentials are used

