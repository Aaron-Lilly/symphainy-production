# Docker Rebuild Checklist - JWKS Implementation

**Date:** December 2024  
**Purpose:** Ensure nothing is lost when rebuilding Docker containers

---

## ✅ Code Changes (All in Repository)

All code changes are in the repository and will be included in the rebuild:

1. **New File:** `supabase_jwks_adapter.py`
   - Location: `symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/supabase_jwks_adapter.py`
   - Status: ✅ In repository

2. **Modified Files:**
   - `supabase_adapter.py` - Added ES256 support and `validate_token_local()`
   - `auth_abstraction.py` - Updated to use local verification
   - `supabase_jwks_adapter.py` - URL normalization

3. **Dependencies:**
   - No new Python packages needed (uses existing `cryptography`, `jwt`, `httpx`)

---

## ⚠️ Environment Variables (Need to Verify)

### **New Environment Variables Added:**

1. **`SUPABASE_JWKS_URL`**
   - Location: `.env.secrets` file
   - Example: `https://eocztpcvzcdqgygxlnqg.supabase.co/auth/v1/.well-known/jwks.json`

2. **`SUPABASE_JWT_ISSUER`**
   - Location: `.env.secrets` file
   - Example: `https://eocztpcvzcdqgygxlnqg.supabase.co/auth/v1`

### **How They're Loaded:**

The application loads `.env.secrets` in `main.py`:
```python
load_dotenv('.env.secrets')
```

### **Docker Build Process:**

The Dockerfile does:
```dockerfile
COPY . .
```

This means:
- ✅ If `.env.secrets` exists in the build context, it will be copied into the image
- ⚠️ If `.env.secrets` is in `.gitignore` (which it should be), it won't be in the image unless:
  - It's manually copied into the build context before building
  - It's mounted as a volume at runtime
  - The env vars are passed directly in docker-compose

### **Current docker-compose.prod.yml:**

**Issue:** The new env vars are NOT in the `environment:` section, and `.env.secrets` is NOT mounted as a volume.

**Options:**

1. **Option A: Add to docker-compose (Recommended)**
   ```yaml
   environment:
     - SUPABASE_JWKS_URL=${SUPABASE_JWKS_URL}
     - SUPABASE_JWT_ISSUER=${SUPABASE_JWT_ISSUER}
   ```

2. **Option B: Mount .env.secrets as volume**
   ```yaml
   volumes:
     - ./symphainy-platform/.env.secrets:/app/.env.secrets:ro
   ```

3. **Option C: Copy .env.secrets into build context**
   - Ensure `.env.secrets` exists in `symphainy-platform/` before building
   - It will be copied into the image with `COPY . .`

---

## 📋 Pre-Rebuild Checklist

### **Before Rebuilding:**

1. ✅ **Verify code is committed:**
   ```bash
   git status
   # Should show all JWKS-related files as committed
   ```

2. ⚠️ **Verify .env.secrets has new vars:**
   ```bash
   grep -E "SUPABASE_JWKS_URL|SUPABASE_JWT_ISSUER" symphainy-platform/.env.secrets
   ```

3. ⚠️ **Decide on env var strategy:**
   - Option A: Add to docker-compose (recommended for production)
   - Option B: Mount as volume (good for development)
   - Option C: Copy into image (if .env.secrets is in build context)

4. ✅ **Verify new file exists:**
   ```bash
   ls -la symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/supabase_jwks_adapter.py
   ```

---

## 🔧 Recommended Fix

**Add environment variables to docker-compose.prod.yml:**

```yaml
backend:
  environment:
    # ... existing vars ...
    - SUPABASE_JWKS_URL=${SUPABASE_JWKS_URL}
    - SUPABASE_JWT_ISSUER=${SUPABASE_JWT_ISSUER}
```

**Then set them in your shell before building:**
```bash
export SUPABASE_JWKS_URL="https://eocztpcvzcdqgygxlnqg.supabase.co/auth/v1/.well-known/jwks.json"
export SUPABASE_JWT_ISSUER="https://eocztpcvzcdqgygxlnqg.supabase.co/auth/v1"
docker-compose -f docker-compose.prod.yml up --build
```

---

## ✅ What Will Be Preserved

- ✅ All code changes (in repository)
- ✅ All modified files (in repository)
- ✅ Dockerfile changes (if any)
- ✅ docker-compose changes (if any)

## ⚠️ What Needs Attention

- ⚠️ Environment variables in `.env.secrets` (need to ensure they're available)
- ⚠️ Any runtime state (expected to be lost)

---

## 🧹 Disk Space Management

### **Important: Clean Build Cache After Each Build**

Multiple Docker image rebuilds can create overlay2 layers that accumulate. Docker may report ~7GB, but actual disk usage can be 75GB+.

**Solution:** Run this after each build:
```bash
docker builder prune -af
```

**Automated Script:**
We've created `scripts/docker-build-clean.sh` that builds and cleans automatically:
```bash
./scripts/docker-build-clean.sh
```

Or manually:
```bash
docker-compose -f docker-compose.prod.yml build
docker builder prune -af
```

---

## 🎯 Summary

**Code:** ✅ All safe (in repository)  
**Config:** ⚠️ Need to ensure env vars are available (either in .env.secrets in build context, or passed via docker-compose)  
**Disk Space:** ⚠️ Run `docker builder prune -af` after each build to prevent accumulation

