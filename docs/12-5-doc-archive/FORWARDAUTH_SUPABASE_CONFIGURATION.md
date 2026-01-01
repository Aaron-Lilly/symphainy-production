# ForwardAuth Supabase Configuration

**Date:** December 2024  
**Status:** 🔧 **CONFIGURATION REQUIRED**

---

## 🎯 Problem

Traefik ForwardAuth middleware requires Supabase credentials to validate JWT tokens. The backend's `/api/auth/validate-token` endpoint needs:
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous/public key

These environment variables are currently missing, causing 503 "Configuration error" responses.

---

## ✅ Solution

Add Supabase environment variables to the backend service in `docker-compose.yml`:

```yaml
backend:
  environment:
    # ... existing env vars ...
    # Supabase Configuration (REQUIRED for ForwardAuth)
    - SUPABASE_URL=${SUPABASE_URL:-}
    - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY:-}
```

---

## 📋 Configuration Steps

### **Step 1: Get Supabase Credentials**

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Navigate to **Settings** → **API**
4. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_ANON_KEY`

### **Step 2: Set Environment Variables**

**Option A: Docker Compose .env file (Recommended)**

Create or update `.env` file in the project root:

```bash
# .env (in project root, not committed to git)
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Option B: Export in Shell**

```bash
export SUPABASE_URL=https://your-project-ref.supabase.co
export SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
docker-compose up -d
```

**Option C: Direct in docker-compose.yml (Not Recommended for Production)**

```yaml
environment:
  - SUPABASE_URL=https://your-project-ref.supabase.co
  - SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🔍 How ForwardAuth Works

1. **Client Request:**
   ```
   GET /api/v1/content-pillar/list-uploaded-files
   Headers: Authorization: Bearer <jwt_token>
   ```

2. **Traefik Intercepts:**
   - Applies `supabase-auth` middleware
   - Makes internal request to: `http://backend:8000/api/auth/validate-token`
   - Sends only headers (Authorization), NOT body

3. **Backend Validates:**
   - `/api/auth/validate-token` endpoint receives request
   - Extracts JWT token from Authorization header
   - Calls Supabase API: `{SUPABASE_URL}/auth/v1/user`
   - Validates token with Supabase
   - Returns 200 OK with user context headers (X-User-Id, X-Tenant-Id, etc.)

4. **Traefik Forwards:**
   - If validation succeeds (200 OK):
     - Adds user context headers to original request
     - Forwards request to backend service
   - If validation fails (401 Unauthorized):
     - Returns 401 to client
     - Request never reaches backend

---

## ✅ Verification

After configuring, verify ForwardAuth works:

```bash
# 1. Restart backend to pick up new env vars
docker-compose restart backend

# 2. Check backend logs for ForwardAuth errors
docker-compose logs backend | grep -i "ForwardAuth\|Supabase"

# 3. Test with a request
curl -H "Authorization: Bearer <token>" \
     http://35.215.64.103/api/v1/content-pillar/list-uploaded-files
```

**Expected:** 200 OK (not 503)

---

## 🔒 Security Notes

- **SUPABASE_ANON_KEY** is safe to expose in client-side code (it's the "anon" key)
- **SUPABASE_SERVICE_KEY** should NOT be used for ForwardAuth (it has admin permissions)
- ForwardAuth only validates tokens, doesn't perform admin operations
- The anon key is designed for client-side authentication validation

---

## 📝 Next Steps

1. ✅ Add env vars to docker-compose.yml (done)
2. ⏳ Set SUPABASE_URL and SUPABASE_ANON_KEY values
3. ⏳ Restart backend service
4. ⏳ Test ForwardAuth endpoint
5. ⏳ Re-run functional tests


