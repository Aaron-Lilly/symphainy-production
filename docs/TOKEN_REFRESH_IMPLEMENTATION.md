# Token Refresh Implementation Summary

## Overview
Implemented comprehensive token refresh and expiration handling across the platform to fix the "Token expired" issue that was causing content pillar failures.

## Architecture Confirmation
✅ **Frontend routing is correct**: All API managers use `/api/v1/{pillar-name}/` endpoints which route through the **Universal Pillar Router** → **FrontendGatewayService** → **Journey Orchestrators**. This maintains proper realm boundaries and does NOT create anti-patterns.

## Backend Changes

### 1. Auth Router (`backend/api/auth_router.py`)
- ✅ Added `refresh_token` field to `AuthResponse` model
- ✅ Added `RefreshTokenRequest` model
- ✅ Added `/api/auth/refresh` endpoint that:
  - Accepts `refresh_token`
  - Uses `AuthAbstraction.refresh_token()` (delegates to Supabase)
  - Returns new `access_token` and `refresh_token`

### 2. Security Guard (`backend/smart_city/services/security_guard/modules/authentication.py`)
- ✅ Updated `authenticate_user()` to extract and return `refresh_token` from Supabase

## Frontend Changes

### 1. Auth API (`lib/api/auth.ts`)
- ✅ Updated `AuthResponse` interface to include `refresh_token`
- ✅ Store `refresh_token` in localStorage on login/register
- ✅ Added `refreshAccessToken()` function

### 2. Token Refresh Utility (`lib/utils/tokenRefresh.ts`) - NEW FILE
- ✅ `authenticatedFetch()`: Wraps fetch with automatic token refresh
  - **Proactive refresh**: Checks if token is expired/expiring before making request
  - **Reactive refresh**: Automatically refreshes on 401 errors
  - **Retry logic**: Retries original request after successful refresh
  - **Redirect on failure**: Redirects to login if refresh fails
- ✅ `isTokenExpired()`: Checks JWT expiration (with buffer)
- ✅ `refreshTokenIfNeeded()`: Proactively refreshes before expiration
- ✅ Handles FormData correctly (doesn't set Content-Type header)

### 3. API Managers Updated
- ✅ **ContentAPIManager**: All 12 fetch calls updated
- ✅ **OperationsAPIManager**: All 11 fetch calls updated
- ⏳ **InsightsAPIManager**: Needs update (3 fetch calls)
- ⏳ **BusinessOutcomesAPIManager**: Needs update (4 fetch calls)
- ⏳ **SessionAPIManager**: Needs update (3 fetch calls)
- ⏳ **GuideAgentAPIManager**: Needs update (3 fetch calls)
- ⏳ **LiaisonAgentsAPIManager**: Needs update (2 fetch calls)

## Pattern for Remaining Managers

Each API manager should:
1. Add `authenticatedFetch()` helper method (same as ContentAPIManager)
2. Replace all `fetch()` calls with `this.authenticatedFetch()`
3. Remove `'Authorization': \`Bearer ${this.sessionToken}\`` from headers (authenticatedFetch adds it)
4. Add `method: 'GET'` or `method: 'POST'` explicitly

## How It Works

1. **On Login**: Frontend receives and stores both `access_token` and `refresh_token`
2. **On API Calls**: 
   - `authenticatedFetch()` checks if token is expired/expiring
   - If expired: Proactively refreshes token before making request
   - Makes request with current/refreshed token
   - If 401 error: Attempts token refresh and retries request
   - If refresh fails: Redirects to login page
3. **Token Expiration**: Proactively refreshes 60 seconds before expiration (configurable)

## Testing Checklist

- [ ] Log in and verify `refresh_token` is stored in localStorage
- [ ] Wait for token to expire (or manually expire it)
- [ ] Navigate to content pillar → Should automatically refresh token
- [ ] Make API calls → Should work seamlessly with refreshed token
- [ ] If refresh fails → Should redirect to login page
- [ ] Test with all pillars (content, operations, insights, etc.)

## Next Steps

1. Update remaining API managers (Insights, BusinessOutcomes, Session, GuideAgent, LiaisonAgents)
2. Test end-to-end token refresh flow
3. Monitor logs for token refresh activity
4. Consider adding token refresh metrics/observability




