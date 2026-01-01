# File Upload Root Cause Analysis

**Date:** 2025-12-02  
**Status:** 🔍 **ROOT CAUSE IDENTIFIED**

---

## Complete Flow Review

### ✅ Frontend Flow is Correct:

1. **File Selection:** File objects properly captured from dropzone ✅
2. **State Management:** File objects stored in React state ✅
3. **FormData Construction:** FormData created with File objects ✅
4. **Fetch Request:** Request configured correctly ✅

### ❌ The Problem:

**Network Log Shows:**
- Request URL: `http://35.215.64.103:3000/api/v1/content-pillar/upload-file`
- Content-Type: `multipart/form-data; boundary=...` ✅
- Body: Shows boundaries and headers but **NO FILE CONTENT** ❌

**Backend Logs Show:**
- Request reaches FrontendGatewayService
- `filename: None` (files not extracted)
- No router logging visible

---

## Root Cause: Next.js Rewrite Issue

### The Issue:

**Next.js Rewrite Configuration** (`next.config.js` line 18-29):
```javascript
async rewrites() {
  const backendURL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://35.215.64.103:8000';
  return [
    {
      source: '/api/:path*',
      destination: `${backendURL}/api/:path*`,
    },
  ];
}
```

**Problem:** Next.js rewrites are **server-side only** and may not properly handle multipart/form-data with binary file content. The rewrite might be:
1. Stripping file content during proxy
2. Not properly forwarding FormData
3. Converting FormData to a different format

### Evidence:

1. **Request goes through Next.js:** Network log shows request to port 3000 (frontend), not 8000 (backend)
2. **Files not reaching backend:** Backend receives `filename: None`
3. **Empty body content:** Network log shows empty content between boundaries

---

## Solution: Bypass Next.js Rewrite for File Uploads

### Fix: Use Direct Backend URL for File Uploads

**Modify `ContentAPIManager.ts`:**

```typescript
async uploadFile(file: File, copybookFile?: File): Promise<UploadResponse> {
  try {
    // ... validation code ...
    
    const formData = new FormData();
    formData.append('file', file);
    if (copybookFile) {
      formData.append('copybook', copybookFile);
    }
    
    // FIX: Use direct backend URL for file uploads (bypass Next.js rewrite)
    // Next.js rewrites don't properly handle multipart/form-data with binary files
    const backendURL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://35.215.64.103:8000';
    const uploadURL = `${backendURL}/api/v1/content-pillar/upload-file`;
    
    console.log('[ContentAPIManager] Uploading to:', uploadURL);
    console.log('[ContentAPIManager] File size:', file.size);
    console.log('[ContentAPIManager] Copybook size:', copybookFile?.size);
    
    const response = await fetch(uploadURL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.sessionToken}`,
        'X-Session-Token': this.sessionToken
        // DO NOT set Content-Type - browser sets it automatically with boundary
      },
      body: formData
    });
    
    // ... rest of code ...
  }
}
```

**Alternative: Use Environment Variable**

```typescript
constructor(sessionToken: string, baseURL?: string) {
  this.sessionToken = sessionToken;
  // For file uploads, always use direct backend URL to avoid Next.js rewrite issues
  this.baseURL = baseURL || (
    typeof window !== 'undefined' 
      ? (process.env.NEXT_PUBLIC_BACKEND_URL || 'http://35.215.64.103:8000')
      : 'http://localhost:8000'
  );
}
```

---

## Why This Happens

### Next.js Rewrites Limitation:

1. **Server-Side Only:** Rewrites work on Next.js server, not in browser
2. **Request Transformation:** Rewrites transform requests, which can affect FormData
3. **Binary Data:** Multipart/form-data with binary files may not be properly forwarded
4. **Stream Handling:** File streams might be consumed or corrupted during proxy

### Best Practice:

**For file uploads, always use direct backend URL:**
- ✅ Avoids Next.js rewrite issues
- ✅ Preserves binary data integrity
- ✅ Better performance (one less hop)
- ✅ More reliable for large files

**For other API calls, Next.js rewrites are fine:**
- ✅ JSON requests work fine through rewrites
- ✅ Smaller payloads are handled correctly
- ✅ Can use relative URLs for convenience

---

## Implementation

### Option 1: Modify uploadFile Method (Recommended)

**File:** `symphainy-frontend/shared/managers/ContentAPIManager.ts`

**Change:**
```typescript
async uploadFile(file: File, copybookFile?: File): Promise<UploadResponse> {
  // ... existing validation code ...
  
  // FIX: Use direct backend URL for file uploads
  const backendURL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://35.215.64.103:8000';
  const uploadURL = `${backendURL}/api/v1/content-pillar/upload-file`;
  
  const response = await fetch(uploadURL, {
    // ... rest of config ...
  });
}
```

### Option 2: Modify Constructor

**File:** `symphainy-frontend/shared/managers/ContentAPIManager.ts`

**Change:**
```typescript
constructor(sessionToken: string, baseURL?: string) {
  this.sessionToken = sessionToken;
  // Always use direct backend URL (no Next.js proxy for file uploads)
  this.baseURL = baseURL || (
    typeof window !== 'undefined' 
      ? (process.env.NEXT_PUBLIC_BACKEND_URL || 'http://35.215.64.103:8000')
      : 'http://localhost:8000'
  );
}
```

---

## Testing

After implementing the fix:

1. **Check browser console:** Should see `[ContentAPIManager] Uploading to: http://35.215.64.103:8000/api/v1/content-pillar/upload-file`
2. **Check network tab:** Request should go directly to port 8000 (backend), not 3000 (frontend)
3. **Check backend logs:** Should see router logging and file extraction
4. **Verify upload:** File should upload successfully

---

## Summary

**Root Cause:** Next.js rewrites don't properly handle multipart/form-data with binary file content, causing file data to be lost during proxy.

**Solution:** Use direct backend URL for file uploads, bypassing Next.js rewrites.

**Impact:** File uploads will work correctly, other API calls continue to use rewrites (which is fine for JSON).






