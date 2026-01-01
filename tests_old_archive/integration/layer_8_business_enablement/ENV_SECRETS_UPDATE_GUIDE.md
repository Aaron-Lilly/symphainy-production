# .env.secrets Update Guide - GCS Credentials Migration

## 🎯 What to Update

### **DO NOT CHANGE** ❌

1. **`GOOGLE_APPLICATION_CREDENTIALS`** - **KEEP AS-IS**
   - **Purpose**: SSH/VM access (infrastructure)
   - **Why**: This is critical for SSH access to GCP VMs
   - **Action**: Do not modify or remove

2. **`GOOGLE_API_KEY`** - **KEEP AS-IS**
   - **Purpose**: Google AI API (document intelligence)
   - **Why**: This is for Google AI services, not GCS
   - **Action**: Do not modify

### **ADD NEW** ✅

3. **`GCS_CREDENTIALS_JSON`** - **ADD THIS**
   - **Purpose**: GCS bucket access (application data)
   - **Pattern**: Supabase-style (JSON string in environment variable)
   - **Action**: Add this new variable

### **REMOVE OLD** 🗑️

4. **`GCS_CREDENTIALS_PATH`** - **REMOVE THIS** (if present)
   - **Why**: No longer needed - we use JSON credentials now
   - **Action**: Remove this line

---

## 📋 Update Steps

### **Option 1: Use Helper Script** (Recommended)

```bash
cd /home/founders/demoversion/symphainy_source
./tests/integration/layer_8_business_enablement/update_gcs_credentials.sh
```

This script will:
- ✅ Read credentials from `backend/symphainymvp-devbox-40d941571d46.json`
- ✅ Convert to JSON string
- ✅ Add `GCS_CREDENTIALS_JSON` to `.env.secrets`
- ✅ Remove old `GCS_CREDENTIALS_PATH` (if present)
- ✅ Create backup of `.env.secrets`
- ✅ Keep `GOOGLE_APPLICATION_CREDENTIALS` and `GOOGLE_API_KEY` unchanged

### **Option 2: Manual Update**

1. **Read credentials file and convert to JSON**:
   ```bash
   cd /home/founders/demoversion/symphainy_source/symphainy-platform
   cat backend/symphainymvp-devbox-40d941571d46.json | python3 -c "import json, sys; print(json.dumps(json.load(sys.stdin), separators=(',', ':')))"
   ```

2. **Add to `.env.secrets`**:
   ```bash
   # Remove old GCS_CREDENTIALS_PATH line (if present)
   # Add new line:
   GCS_CREDENTIALS_JSON='{"type":"service_account","project_id":"symphainymvp-devbox",...}'
   ```

---

## 📝 Example .env.secrets Section

### **Before** (Old)
```bash
# GOOGLE CLOUD SERVICES
GOOGLE_API_KEY=AIzaSyC1GRzqFlAkHP8lteKfAglxin1MO0LWbmQ

# GCS Configuration
GCS_PROJECT_ID=symphainymvp-devbox
GCS_BUCKET_NAME=symphainy-bucket-2025
GCS_CREDENTIALS_PATH=backend/symphainymvp-devbox-40d941571d46.json

# CRITICAL: DO NOT SET GOOGLE_APPLICATION_CREDENTIALS HERE
# (It's set at VM/SSH level for infrastructure access)
```

### **After** (New)
```bash
# GOOGLE CLOUD SERVICES
GOOGLE_API_KEY=AIzaSyC1GRzqFlAkHP8lteKfAglxin1MO0LWbmQ

# GCS Configuration (Supabase Pattern)
GCS_PROJECT_ID=symphainymvp-devbox
GCS_BUCKET_NAME=symphainy-bucket-2025
# GCS Credentials (Supabase pattern - JSON string, no file paths!)
# CRITICAL: This is for bucket access (application data)
# DO NOT use GOOGLE_APPLICATION_CREDENTIALS (that's for SSH/VM access)
GCS_CREDENTIALS_JSON='{"type":"service_account","project_id":"symphainymvp-devbox","private_key_id":"40d941571d46",...}'

# CRITICAL: DO NOT SET GOOGLE_APPLICATION_CREDENTIALS HERE
# (It's set at VM/SSH level for infrastructure access)
```

---

## ✅ Verification

After updating, test that it works:

```bash
cd /home/founders/demoversion/symphainy_source
python3 tests/integration/layer_8_business_enablement/test_gcs_json_credentials_simple.py
```

Expected output:
```
✅ GCS adapter initialized successfully
✅ Successfully accessed GCS!
✅ ALL TESTS PASSED - GCS JSON credentials work correctly!
```

---

## 🛡️ Safety Checklist

Before updating:
- [ ] Backup `.env.secrets` (script does this automatically)
- [ ] Verify `GOOGLE_APPLICATION_CREDENTIALS` is NOT in `.env.secrets` (should be set at VM/SSH level)
- [ ] Verify `GOOGLE_API_KEY` exists (for Google AI API)

After updating:
- [ ] Verify `GCS_CREDENTIALS_JSON` is set
- [ ] Verify `GCS_CREDENTIALS_PATH` is removed (if it was there)
- [ ] Test GCS access works
- [ ] Verify SSH access still works (should be unaffected)

---

## 🎯 Summary

**What to Update**:
- ✅ **ADD**: `GCS_CREDENTIALS_JSON` (new, Supabase pattern)
- 🗑️ **REMOVE**: `GCS_CREDENTIALS_PATH` (old, no longer needed)

**What to Keep**:
- ✅ **KEEP**: `GOOGLE_APPLICATION_CREDENTIALS` (SSH/VM access - set at VM level, not in .env.secrets)
- ✅ **KEEP**: `GOOGLE_API_KEY` (Google AI API)

**Result**: 
- ✅ Simpler configuration (no file paths)
- ✅ No path resolution needed
- ✅ No SSH/GCE concerns
- ✅ Consistent with Supabase pattern







