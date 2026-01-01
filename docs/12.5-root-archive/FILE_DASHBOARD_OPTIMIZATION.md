# File Dashboard Optimization - Reducing Excessive API Calls

**Date:** 2025-12-01  
**Issue:** FileDashboard and FileSelector components were calling `listFiles()` too frequently, causing rate limiting issues.

## Root Cause Analysis

### Problems Found

1. **FileDashboard useEffect dependency issue:**
   - `useEffect` was calling `loadFiles()` every time `isAuthenticated` changed
   - Should only load once on mount

2. **FileSelector useEffect dependency issue:**
   - `useEffect` depended on both `isAuthenticated` AND `loadFiles`
   - Since `loadFiles` is a `useCallback` that depends on `guideSessionToken`, `getPillarState`, `setPillarState`, it gets recreated whenever these change
   - This caused the useEffect to run multiple times unnecessarily

3. **Multiple components calling listFiles:**
   - `FileDashboard` (main page component)
   - `FileSelector` (used in `ParsePreview` and `MetadataExtractor`)
   - Result: **3+ API calls on every page load**

4. **No deduplication:**
   - Each component independently called `listFiles()` without checking if data was already loaded
   - Even though they update global state, they don't check if it's already populated

## Solution Implemented

### Changes Made

1. **Added `useRef` to track if files have been loaded:**
   - Prevents multiple calls even if dependencies change
   - Resets when user logs out (allows reload on next login)

2. **Updated useEffect dependencies:**
   - Removed `loadFiles` from dependency array (prevents re-runs when callback is recreated)
   - Only depends on `isAuthenticated` (for login/logout handling)

3. **Added guard to prevent duplicate loads:**
   - `hasLoadedRef.current` ensures `loadFiles()` is only called once per mount
   - Components still check global state first (from previous useEffect)

### Files Modified

1. **`app/pillars/content/components/FileDashboard.tsx`**
   - Added `useRef` import
   - Added `hasLoadedRef` to track load state
   - Updated useEffect to only load once on mount

2. **`app/pillars/content/components/FileSelector.tsx`**
   - Added `useRef` import
   - Added `hasLoadedRef` to track load state
   - Updated useEffect to only load once on mount
   - Removed `loadFiles` from dependency array

## Expected Behavior After Fix

### Before:
- Page load: 3+ calls to `listFiles()` (FileDashboard + 2x FileSelector)
- Every auth state change: Additional calls
- Every global state update: Additional calls (via loadFiles recreation)

### After:
- Page load: 1 call to `listFiles()` (first component to mount)
- Subsequent components: Use global state (no API call)
- Manual refresh: 1 call (when user clicks refresh button)
- Auth state changes: No additional calls (unless user logs out and back in)

## Testing Recommendations

1. **Monitor network tab:**
   - Open browser DevTools → Network tab
   - Filter by `list-uploaded-files`
   - Load the content pillar page
   - Should see only 1 API call (not 3+)

2. **Test refresh button:**
   - Click the refresh button in FileDashboard
   - Should see 1 additional API call

3. **Test multiple components:**
   - Navigate between ParsePreview and MetadataExtractor
   - Should NOT see additional API calls (they use global state)

4. **Test logout/login:**
   - Log out and log back in
   - Should see 1 API call on login (ref resets)

## Additional Optimizations (Future)

1. **Shared data fetching hook:**
   - Create a `useFileList` hook that both components can use
   - Ensures only one component actually fetches data
   - Others just subscribe to the same data

2. **Request deduplication:**
   - If multiple components request data simultaneously, deduplicate requests
   - Use a shared promise/cache

3. **Stale-while-revalidate:**
   - Show cached data immediately
   - Refresh in background if data is stale






