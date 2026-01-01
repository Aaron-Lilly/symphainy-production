# Immediate Action Items - Production Readiness

**Date:** December 2024  
**Purpose:** Quick reference for critical fixes needed before production deployment

---

## 🔴 **Critical Issues Found During Deployment**

### **1. GCS Configuration Missing in Production** ⚠️ **BLOCKING**

**Problem:**
- `GCS_PROJECT_ID` and `GCS_BUCKET_NAME` only in `config/development.env`
- Not in `config/production.env`
- Backend fails to start because GCS adapter can't initialize

**Current State:**
- ✅ `GCS_PROJECT_ID=symphainymvp-devbox` in `config/development.env`
- ✅ `GCS_BUCKET_NAME=symphainy-bucket-2025` in `config/development.env`
- ✅ `GCS_CREDENTIALS_JSON` in `.env.secrets` (with "type", "project_id", "private_key_id")

**Action Required:**
```bash
# Add to config/production.env:
GCS_PROJECT_ID=symphainymvp-devbox  # Or your production project ID
GCS_BUCKET_NAME=symphainy-bucket-2025  # Or your production bucket
```

**Files to Update:**
- `symphainy-platform/config/production.env`

---

### **2. Docker Network Isolation** ⚠️ **BLOCKING**

**Problem:**
- Infrastructure services: `symphainy-platform_smart_city_net`
- Application services: `symphainy_source_symphainy-network`
- Services can't communicate across networks

**Current State:**
- ✅ Infrastructure compose: `smart_city_net` network
- ⚠️ Application compose: `symphainy-network` network
- ⚠️ Backend now connected to both (workaround)

**Action Required:**
- **Option A (Recommended):** Use single network for everything
  - Update `docker-compose.prod.yml` to use `smart_city_net` as external network
  - Remove `symphainy-network` creation
  - Connect all services to `smart_city_net`

- **Option B:** Keep separate networks but ensure proper connectivity
  - Document network architecture
  - Ensure all services that need to communicate are on same network

**Files to Update:**
- `docker-compose.prod.yml`
- `symphainy-platform/docker-compose.infrastructure.yml` (if needed)

---

### **3. Test Files in Production Build** ⚠️ **BLOCKING**

**Problem:**
- Test files (`TestUtils.tsx`, `__tests__/`) being compiled in production
- TypeScript errors in test files break build
- Currently using workaround (`ignoreBuildErrors: true`)

**Action Required:**
```bash
# Update symphainy-frontend/.dockerignore:
__tests__/
**/*.test.ts
**/*.test.tsx
**/*.spec.ts
**/*.spec.tsx
shared/testing/
tests/

# Update symphainy-frontend/tsconfig.json:
"exclude": [
  "node_modules",
  "archive/**/*",
  "**/*.test.ts",
  "**/*.test.tsx",
  "**/__tests__/**/*",
  "**/testing/**/*"
]

# Update symphainy-frontend/next.config.js:
# Remove ignoreBuildErrors: true after proper exclusion
```

**Files to Update:**
- `symphainy-frontend/.dockerignore`
- `symphainy-frontend/tsconfig.json`
- `symphainy-frontend/next.config.js`

---

### **4. Poetry Lock File Out of Sync** ⚠️ **BLOCKING**

**Problem:**
- `poetry.lock` doesn't match `pyproject.toml` after adding `gotrue`
- Build fails or uses workaround

**Action Required:**
```bash
# On local machine (with Poetry installed):
cd symphainy-platform
poetry lock
git add poetry.lock
git commit -m "Update poetry.lock with gotrue dependency"
git push origin main

# Then remove workaround from Dockerfile:
# Remove: (poetry lock || true) &&
```

**Files to Update:**
- `symphainy-platform/poetry.lock` (regenerate)
- `symphainy-platform/Dockerfile` (remove workaround)

---

### **5. Build Context Cleanup** ⚠️ **HIGH PRIORITY**

**Problem:**
- Documentation, tests, scripts included in Docker build context
- Larger builds, slower deployments, potential security issues

**Action Required:**

**Backend `.dockerignore`:**
```bash
# Create/update symphainy-platform/.dockerignore:
docs/
tests/
*.md
archive/
scripts/
.git/
.github/
.vscode/
.idea/
*.swp
*.swo
.env.local
.env.development
config/development.env
htmlcov/
coverage.xml
.pytest_cache/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
```

**Frontend `.dockerignore` (already exists, verify):**
```bash
# Verify symphainy-frontend/.dockerignore excludes:
__tests__/
tests/
docs/
*.md
archive/
scripts/
.git/
.github/
.env.local
.env.development
```

**Files to Create/Update:**
- `symphainy-platform/.dockerignore` (create if doesn't exist)
- `symphainy-frontend/.dockerignore` (verify and update)

---

### **6. Poetry on VM** ℹ️ **INFORMATIONAL**

**Problem:**
- Poetry command not found when trying to run on VM
- Confusion about when Poetry is needed

**Clarification:**
- Poetry is **only needed inside Docker containers** for building
- Not needed on VM itself (Docker handles it)
- If you want to run Poetry on VM for local development, install it separately

**Action Required:**
- [ ] Document that Poetry runs in Docker, not needed on VM
- [ ] OR install Poetry on VM if needed: `curl -sSL https://install.python-poetry.org | python3 -`
- [ ] Update deployment documentation

---

## 📋 **Quick Fix Checklist**

### **Before Next Deployment Attempt:**

- [ ] **GCS Config:** Add `GCS_PROJECT_ID` and `GCS_BUCKET_NAME` to `config/production.env`
- [ ] **Network:** Standardize on single Docker network
- [ ] **Test Files:** Properly exclude from builds (remove workarounds)
- [ ] **Poetry Lock:** Regenerate and commit `poetry.lock`
- [ ] **Build Context:** Create/update `.dockerignore` files
- [ ] **Dependencies:** Verify all imports have corresponding dependencies
- [ ] **Config Validation:** Create script to validate all required config exists
- [ ] **Local Testing:** Test production Docker builds locally first

---

## 🧪 **Pre-Deployment Validation Script**

Create a script to validate before deployment:

```bash
#!/bin/bash
# scripts/validate-production-readiness.sh

echo "🔍 Validating Production Readiness..."

# Check GCS config
if ! grep -q "GCS_PROJECT_ID" symphainy-platform/config/production.env; then
    echo "❌ GCS_PROJECT_ID missing in production.env"
    exit 1
fi

# Check network config
# ... add more checks

echo "✅ All checks passed!"
```

---

## 📊 **Summary of Issues by Category**

| Category | Issues Found | Critical | High | Medium |
|----------|-------------|----------|------|--------|
| Build & Compilation | 4 | 3 | 1 | 0 |
| Code Organization | 3 | 1 | 2 | 0 |
| Configuration | 3 | 1 | 2 | 0 |
| Docker & Infrastructure | 3 | 1 | 1 | 1 |
| Dependencies | 3 | 2 | 1 | 0 |
| Service Initialization | 3 | 1 | 2 | 0 |
| Documentation | 2 | 0 | 2 | 0 |
| Testing & Validation | 2 | 0 | 2 | 0 |
| **TOTAL** | **23** | **9** | **13** | **1** |

---

## 🎯 **Recommended Approach**

1. **Stop current deployment attempt**
2. **Fix all CRITICAL issues** (GCS, Network, Test Files, Dependencies)
3. **Test builds locally** before deploying
4. **Create validation script** to catch issues early
5. **Then attempt deployment again**

---

**Next Steps:** Review checklist, prioritize fixes, and work through them systematically.

