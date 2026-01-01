# Rate Limiting Fix for File Dashboard Connection Reset

**Date:** 2025-12-01  
**Issue:** `ERR_CONNECTION_RESET` when accessing `/api/v1/content-pillar/list-uploaded-files`

## Root Cause

The backend was returning **429 Too Many Requests** due to aggressive rate limiting:
- Default rate limit: **100 requests per hour** (too low for file listing)
- All requests from the same IP were grouped together
- The `FileDashboard` component calls `listFiles()` on mount and auth changes
- Multiple rapid requests quickly hit the rate limit

## Solution

Updated the rate limiting middleware (`fastapi_rate_limiting_middleware.py`) to:

1. **Exclude read-only endpoints** from rate limiting:
   - `/api/v1/content-pillar/list-uploaded-files` (file listing)
   - `/api/v1/content-pillar/get-file-details` (file details)

2. **Increase default rate limit** from 100 to 1000 requests per hour

3. **Better logging** to show excluded paths

## Changes Made

### File: `utilities/api_routing/middleware/fastapi_rate_limiting_middleware.py`

1. Added `excluded_paths` list for read-only endpoints
2. Updated `dispatch()` to skip rate limiting for excluded paths
3. Increased default rate limit from 100 to 1000 requests/hour
4. Enhanced logging to show excluded paths count

## Testing

After restarting the backend:
- ✅ Endpoint `/api/v1/content-pillar/list-uploaded-files` should no longer return 429
- ✅ File dashboard should load without connection reset errors
- ✅ Other endpoints still protected by rate limiting

## Next Steps

1. Monitor backend logs for rate limiting warnings
2. Test file dashboard in browser to confirm fix
3. Consider adding request deduplication/caching in frontend for additional optimization






