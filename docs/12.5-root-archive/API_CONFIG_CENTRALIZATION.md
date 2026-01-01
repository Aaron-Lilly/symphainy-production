# API Configuration Centralization

**Date:** 2025-12-02  
**Status:** ✅ **COMPLETE**

---

## Issue

Multiple API files had hardcoded `localhost:8000` URLs, causing CORS errors when accessing the frontend from a remote IP address.

## Solution

Centralized all API URL configuration to use `lib/config.ts`, which:
- Checks environment variables (`NEXT_PUBLIC_API_BASE` or `NEXT_PUBLIC_BACKEND_URL`)
- Defaults to production backend URL (`http://35.215.64.103:8000`)
- Provides a single source of truth for all API endpoints

## Files Updated

### ✅ Centralized Config
- `lib/config.ts` - Now exports `config.apiUrl` with proper defaults

### ✅ API Files Updated to Use Config
1. **`lib/api/auth.ts`** - Already using `config.apiUrl` ✅
2. **`lib/api/global.ts`** - Already using `config.apiUrl` ✅
3. **`lib/api/insights.ts`** - Updated to use `config.apiUrl`
4. **`lib/api/operations.ts`** - Updated to use `config.apiUrl`
5. **`lib/api/experience.ts`** - Updated to use `config.apiUrl`
6. **`lib/api/experience-adapted.ts`** - Updated to use `config.apiUrl`

### ✅ Files Already Using Config
- `lib/api/content.ts`
- `lib/api/fms.ts`
- `lib/api/fms-insights.ts`
- `lib/api/experience-layer-client.ts`
- `lib/api/unified-client.ts`

### ⚠️ Special Case
- `lib/api/experience-dimension.ts` - Uses port 8007 (different service), left as-is

## Changes Made

### Before:
```typescript
// Each file had its own hardcoded URL
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
```

### After:
```typescript
// All files import and use centralized config
import { config } from "../config";
const API_BASE = config.apiUrl;
const API_URL = config.apiUrl;
```

## Benefits

1. **Single Source of Truth:** All API URLs come from one place
2. **Environment-Aware:** Respects environment variables
3. **Production-Ready:** Defaults to production URL instead of localhost
4. **Maintainable:** Easy to update URL in one place
5. **No Hardcoding:** No more scattered localhost URLs

## Configuration Priority

1. `NEXT_PUBLIC_API_BASE` environment variable (if set)
2. `NEXT_PUBLIC_BACKEND_URL` environment variable (if set)
3. Production backend URL: `http://35.215.64.103:8000` (default)

## Next Steps

1. **Clear browser cache** or hard refresh (Ctrl+Shift+R)
2. **Test login/register** - should work now
3. **Verify:** All API calls should go to `http://35.215.64.103:8000`

## Future Improvements

For production deployment, set environment variables in docker-compose:
```yaml
environment:
  - NEXT_PUBLIC_BACKEND_URL=http://35.215.64.103:8000
```

This allows easy configuration without code changes.






