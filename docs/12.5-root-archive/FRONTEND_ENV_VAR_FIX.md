# Frontend Environment Variable Fix

**Date:** 2025-12-02  
**Status:** ✅ **FIXED - REBUILT**

---

## Problem

The frontend container was using `NEXT_PUBLIC_API_URL=http://backend:8000` which is a Docker internal hostname. This was baked into the JavaScript bundle at build time, causing the browser to try to access `http://localhost:8000` (which gets blocked by CORS).

**Error in console:**
```
Access to fetch at 'http://localhost:8000/api/global/session' from origin 'http://35.215.64.103:3000' has been blocked by CORS policy
```

---

## Root Cause

1. `docker-compose.prod.yml` had `NEXT_PUBLIC_API_URL=http://backend:8000`
2. Next.js bakes `NEXT_PUBLIC_*` environment variables into the JavaScript bundle at **build time**
3. The browser can't access `backend:8000` (Docker internal hostname)
4. Browser falls back to `localhost:8000` which is blocked by CORS

---

## Fix Applied

### 1. Updated `docker-compose.prod.yml`
Changed:
```yaml
environment:
  - NEXT_PUBLIC_API_URL=http://backend:8000  # ❌ Docker internal hostname
```

To:
```yaml
environment:
  - NEXT_PUBLIC_BACKEND_URL=http://35.215.64.103:8000  # ✅ Production IP
  - NEXT_PUBLIC_API_BASE=http://35.215.64.103:8000     # ✅ Production IP
```

### 2. Rebuilt Frontend Container
- Rebuilt with `--no-cache` to ensure new environment variables are baked in
- Restarted container with new image

---

## How It Works Now

1. **Build Time:** Next.js reads `NEXT_PUBLIC_BACKEND_URL` and `NEXT_PUBLIC_API_BASE` from environment
2. **Config File:** `lib/config.ts` uses these variables:
   ```typescript
   const API_BASE = process.env.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_BACKEND_URL;
   export const config = {
     apiUrl: API_BASE || "http://35.215.64.103:8000", // Fallback to production IP
   };
   ```
3. **Runtime:** All API calls use `config.apiUrl` which is now `http://35.215.64.103:8000`

---

## Testing

1. **Clear browser cache** or hard refresh (Ctrl+Shift+R / Cmd+Shift+R)
2. **Check network tab** - all API calls should go to `http://35.215.64.103:8000`
3. **Test login** - should work now without CORS errors

---

## Environment Variables Reference

| Variable | Purpose | Value |
|----------|---------|-------|
| `NEXT_PUBLIC_BACKEND_URL` | Backend API URL | `http://35.215.64.103:8000` |
| `NEXT_PUBLIC_API_BASE` | API base URL (alias) | `http://35.215.64.103:8000` |
| `NODE_ENV` | Environment mode | `production` |

**Note:** `NEXT_PUBLIC_*` variables are baked into the bundle at build time. To change them, you must rebuild the container.

---

**Status:** ✅ Frontend rebuilt with correct environment variables. Ready for testing!






