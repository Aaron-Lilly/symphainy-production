# Production Fixes Required - Action Plan

**Date:** December 2024  
**Target:** GCE VM Deployment (35.215.64.103:3000)  
**Priority:** Fix before CTO demo

---

## 🔴 **Priority 1: Critical Fixes (Must Do Before Deployment)**

### **Fix 1: Frontend Standalone Build Configuration**

**Issue:** Dockerfile expects `.next/standalone` but Next.js not configured for standalone output.

**File:** `symphainy-frontend/next.config.js`

**Current:**
```javascript
const nextConfig = {
  typescript: { ... },
  eslint: { ... },
  async rewrites() { ... },
  webpack: (config, { isServer }) => { ... }
}
```

**Required:**
```javascript
const nextConfig = {
  output: 'standalone',  // ADD THIS LINE
  typescript: { ... },
  eslint: { ... },
  async rewrites() { ... },
  webpack: (config, { isServer }) => { ... }
}
```

**Action:** Add `output: 'standalone'` to `next.config.js`

---

### **Fix 2: CORS Configuration for Production**

**Issue:** CORS allows all origins in development, but production config has placeholder.

**Files:**
1. `symphainy-platform/main.py` (line ~1021)
2. `symphainy-platform/config/production.env` (line 46)

**Current:**
```python
# main.py
cors_origins = os.getenv("CORS_ORIGINS", "*")
```

```bash
# config/production.env
API_CORS_ORIGINS=https://your-domain.com,https://app.your-domain.com
```

**Required:**
```bash
# config/production.env
API_CORS_ORIGINS=http://35.215.64.103:3000,http://localhost:3000
```

**Action:** Update `config/production.env` with actual production URL

---

### **Fix 3: Frontend Backend URL Configuration**

**Issue:** Some frontend files have hardcoded backend URL fallback.

**Files:**
- `symphainy-frontend/shared/services/operations/core.ts` (line 19)
- `symphainy-frontend/shared/services/operations/workflow-generation.ts` (line 10)

**Current:**
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://35.215.64.103:8000";
```

**Required:** Keep as-is (fallback is correct), but ensure `NEXT_PUBLIC_API_URL` is set in production.

**Action:** Document that `NEXT_PUBLIC_API_URL=http://35.215.64.103:8000` must be set in production.

---

### **Fix 4: Create CI/CD Pipeline**

**Issue:** No automated deployment pipeline exists.

**Required:** Create `.github/workflows/deploy-production.yml`

**Action:** Create GitHub Actions workflow (see template below)

---

## 🟡 **Priority 2: Important Fixes (Should Do)**

### **Fix 5: Environment Variable Documentation**

**Issue:** No `.env.production.example` file for frontend.

**Action:** Create `symphainy-frontend/.env.production.example` with:
```bash
NEXT_PUBLIC_BACKEND_URL=http://35.215.64.103:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

---

### **Fix 6: Security Headers Middleware**

**Issue:** No explicit security headers configured.

**Action:** Add security headers middleware to `main.py`:
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

---

## 📋 **Implementation Steps**

### **Step 1: Fix Frontend Configuration (5 minutes)**
1. Add `output: 'standalone'` to `next.config.js`
2. Test build: `cd symphainy-frontend && npm run build`
3. Verify `.next/standalone` directory exists

### **Step 2: Fix CORS Configuration (2 minutes)**
1. Update `symphainy-platform/config/production.env`:
   ```bash
   API_CORS_ORIGINS=http://35.215.64.103:3000,http://localhost:3000
   ```
2. Verify `main.py` reads from `CORS_ORIGINS` env var

### **Step 3: Create CI/CD Pipeline (15 minutes)**
1. Create `.github/workflows/deploy-production.yml`
2. Configure SSH key in GitHub Secrets
3. Test deployment workflow

### **Step 4: Document Environment Variables (10 minutes)**
1. Create `.env.production.example` for frontend
2. Document backend `.env.secrets` requirements
3. Create deployment guide

---

## 🚀 **CI/CD Pipeline Template**

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:  # Allow manual trigger

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Deploy to GCE VM
        uses: appleboy/ssh-action@master
        with:
          host: 35.215.64.103
          username: founders
          key: ${{ secrets.GCE_SSH_KEY }}
          script: |
            cd /home/founders/demoversion/symphainy_source
            git pull origin main
            ./scripts/vm-staging-deploy.sh
      
      - name: Health Check
        uses: appleboy/ssh-action@master
        with:
          host: 35.215.64.103
          username: founders
          key: ${{ secrets.GCE_SSH_KEY }}
          script: |
            sleep 30
            curl -f http://localhost:8000/health || exit 1
            curl -f http://localhost:3000 || exit 1
```

---

## ✅ **Quick Fix Checklist**

- [ ] Fix frontend standalone build (`next.config.js`)
- [ ] Fix CORS configuration (`config/production.env`)
- [ ] Create CI/CD pipeline (`.github/workflows/deploy-production.yml`)
- [ ] Create `.env.production.example` for frontend
- [ ] Document secret deployment process
- [ ] Test deployment script locally
- [ ] Verify firewall rules allow ports 3000 and 8000
- [ ] Deploy and test CTO demo scenarios

---

**Estimated Time:** 1-2 hours for all critical fixes

**Last Updated:** December 2024


