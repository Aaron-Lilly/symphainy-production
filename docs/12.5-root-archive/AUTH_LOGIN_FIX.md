# Auth/Login Fix - Production Backend URL

**Date:** 2025-12-02  
**Status:** ✅ **FIXED**

---

## Issue

After clearing browser cache, users couldn't login or register. Error:
```
Access to fetch at 'http://localhost:8000/api/auth/login' from origin 'http://35.215.64.103:3000' 
has been blocked by CORS policy: The request client is not a secure context and the resource 
is in more-private address space `loopback`.
```

## Root Cause

The frontend config (`lib/config.ts`) was defaulting to `http://localhost:8000` when `NEXT_PUBLIC_API_BASE` or `NEXT_PUBLIC_BACKEND_URL` environment variables were not set.

**Problem:**
- Frontend is accessed from remote IP: `http://35.215.64.103:3000`
- Backend API calls were going to: `http://localhost:8000`
- Browsers block requests from public IPs to localhost for security (private network access)

## Fix Applied

**Updated `lib/config.ts`:**

```typescript
// Before:
apiUrl: API_BASE || "http://localhost:8000",

// After:
apiUrl: API_BASE || "http://35.215.64.103:8000",
```

**Also checks both environment variables:**
```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_BACKEND_URL;
```

## Affected Endpoints

This fix applies to all API calls that use `config.apiUrl`:
- ✅ `/api/auth/login` - Login
- ✅ `/api/auth/register` - Registration
- ✅ `/api/global/session` - Global session
- ✅ All other API calls using the config

## Rebuild

✅ Rebuilt frontend container with `--no-cache`  
✅ Restarted frontend container

## Next Steps

1. **Clear browser cache** or do hard refresh (Ctrl+Shift+R)
2. **Try login/register again** - should work now
3. **Verify:** Requests should go to `http://35.215.64.103:8000` instead of `localhost:8000`

---

**Note:** For production deployment, set `NEXT_PUBLIC_BACKEND_URL` environment variable in docker-compose or deployment config to avoid hardcoding.






