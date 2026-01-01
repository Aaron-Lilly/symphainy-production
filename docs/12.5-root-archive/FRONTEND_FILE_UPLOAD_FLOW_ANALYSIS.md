# Frontend File Upload Flow - Complete Analysis

**Date:** 2025-12-02  
**Status:** ✅ **COMPLETE FLOW REVIEWED**

---

## Complete File Upload Flow

### Step 1: File Selection (FileUploader.tsx)

**Component:** `FileUploader`  
**Location:** `app/pillars/content/components/FileUploader.tsx`

**Process:**
1. User drops file or clicks to select
2. `react-dropzone` calls `onDrop` callback (line 122-132)
3. Receives `acceptedFiles: File[]` from dropzone
4. Takes first file: `const file = acceptedFiles[0]`
5. Stores in React state: `setUploadState(prev => ({ ...prev, selectedFile: file }))`

**State Storage:**
```typescript
interface UploadState {
  selectedFile: File | null;  // ✅ File object stored here
  copybookFile: File | null;  // ✅ Copybook File object stored here
  // ... other state
}
```

**✅ Status:** File objects are properly stored in React state.

---

### Step 2: Copybook Selection (FileUploader.tsx)

**Process:**
1. User selects copybook file via `<input type="file">` (line 515-522)
2. `handleCopybookChange` callback (line 194-198)
3. Receives `e.target.files[0]` from input
4. Stores in state: `setUploadState(prev => ({ ...prev, copybookFile: e.target.files![0] }))`

**✅ Status:** Copybook File object is properly stored in React state.

---

### Step 3: Upload Button Click (FileUploader.tsx)

**Handler:** `handleUpload` (line 201-336)

**Process:**
1. Validates `uploadState.selectedFile` exists (line 203)
2. Validates copybook if required (line 209)
3. Sets uploading state (line 214)
4. Gets session token (line 217)
5. Creates `ContentAPIManager` instance (line 218)
6. **Calls `apiManager.uploadFile()`** (line 221-224):
   ```typescript
   const result = await apiManager.uploadFile(
     uploadState.selectedFile,      // ✅ File object from state
     uploadState.copybookFile || undefined  // ✅ Copybook File object or undefined
   );
   ```

**✅ Status:** File objects are correctly passed to API manager.

---

### Step 4: FormData Construction (ContentAPIManager.ts)

**Method:** `uploadFile` (line 75-161)

**Process:**
1. **Validates File objects** (line 87-90):
   ```typescript
   if (!file || !(file instanceof File)) {
     throw new Error('Invalid file: file must be a File object');
   }
   ```

2. **Creates FormData** (line 92):
   ```typescript
   const formData = new FormData();
   ```

3. **Appends main file** (line 93):
   ```typescript
   formData.append('file', file);
   ```

4. **Appends copybook if present** (line 96-102):
   ```typescript
   if (copybookFile) {
     if (!(copybookFile instanceof File)) {
       throw new Error('Invalid copybook file');
     }
     formData.append('copybook', copybookFile);
   }
   ```

**✅ Status:** FormData is correctly constructed with File objects.

---

### Step 5: Fetch Request (ContentAPIManager.ts)

**Request Configuration:**
```typescript
const response = await fetch(`${this.baseURL}/api/v1/content-pillar/upload-file`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${this.sessionToken}`,
    'X-Session-Token': this.sessionToken
    // ✅ NO Content-Type header - browser sets it automatically with boundary
  },
  body: formData  // ✅ FormData object
});
```

**Base URL:**
- Constructor (line 41-45): `baseURL || (typeof window !== 'undefined' ? '' : 'http://localhost:8000')`
- If `baseURL` not provided and in browser: uses empty string (relative URL)
- This relies on Next.js rewrites/proxy

**✅ Status:** Fetch request is correctly configured.

---

## Critical Observations

### ✅ What's Working Correctly:

1. **File Selection:** File objects are properly captured from dropzone
2. **State Management:** File objects are stored in React state correctly
3. **File Passing:** File objects are passed to API manager correctly
4. **FormData Construction:** FormData is created and files are appended correctly
5. **Headers:** Content-Type is NOT manually set (correct - browser sets it)
6. **Request:** Fetch is called with FormData as body

### ⚠️ Potential Issues:

#### Issue 1: Base URL Configuration

**Observation:**
- `baseURL` defaults to empty string in browser
- This relies on Next.js rewrites/proxy to forward requests
- If rewrites not configured, request might fail or be modified

**Check:** Next.js `next.config.js` for rewrites/proxy configuration

#### Issue 2: File Object Validity

**Observation:**
- File objects are stored in React state
- State updates are async - could file be cleared before upload?
- Check if `uploadState.selectedFile` is still valid when `handleUpload` is called

**Verification:** The code checks `uploadState.selectedFile` exists (line 203), but doesn't verify it's still a File instance.

#### Issue 3: FormData Serialization

**Observation:**
- Network logs show empty file content between boundaries
- This suggests FormData might not be serializing File objects correctly
- Could be a browser issue or FormData API issue

**Check:** Browser DevTools Network tab - verify FormData payload

#### Issue 4: Next.js Proxy/Rewrite

**Observation:**
- If using relative URL (`baseURL = ''`), Next.js must proxy to backend
- Proxy might strip or modify FormData
- Check Next.js configuration

---

## Network Log Analysis

**From User's Network Log:**
```javascript
fetch("http://35.215.64.103:3000/api/v1/content-pillar/upload-file", {
  "headers": {
    "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryFBd8UeannLHAxek1",
    // ... other headers
  },
  "body": "------WebKitFormBoundaryFBd8UeannLHAxek1\r\nContent-Disposition: form-data; name=\"file\"; filename=\"telemetry_raw.bin\"\r\nContent-Type: application/octet-stream\r\n\r\n\r\n------WebKitFormBoundaryFBd8UeannLHAxek1\r\nContent-Disposition: form-data; name=\"copybook\"; filename=\"telemetry_copybook.cpy\"\r\nContent-Type: application/octet-stream\r\n\r\n\r\n------WebKitFormBoundaryFBd8UeannLHAxek1--\r\n"
});
```

**Critical Finding:**
- ✅ Headers are correct (Content-Type with boundary)
- ✅ Boundary markers are present
- ✅ Field names are correct (`file` and `copybook`)
- ✅ Filenames are present
- ❌ **FILE CONTENT IS MISSING** - empty between boundaries (`\r\n\r\n`)

**This indicates:** File objects are being serialized to FormData, but the actual file content (binary data) is not being included.

---

## Root Cause Hypothesis

**Most Likely:** File objects are being read/consumed or corrupted before being appended to FormData.

**Possible Causes:**
1. **File objects are empty** - size is 0
2. **File objects were already read** - stream position at end
3. **Browser FormData bug** - FormData not serializing File objects correctly
4. **Next.js proxy issue** - Proxy stripping file content
5. **File objects are not actual File instances** - might be Blob or other type

---

## Recommended Fixes

### Fix 1: Verify File Objects Before Upload

**Add to `handleUpload` in FileUploader.tsx:**
```typescript
// Before calling apiManager.uploadFile
console.log('Selected file:', uploadState.selectedFile);
console.log('File size:', uploadState.selectedFile?.size);
console.log('File type:', uploadState.selectedFile?.type);
console.log('Is File instance:', uploadState.selectedFile instanceof File);

if (!uploadState.selectedFile || uploadState.selectedFile.size === 0) {
  setUploadState(prev => ({ ...prev, error: 'Invalid file: file is empty' }));
  return;
}
```

### Fix 2: Verify FormData Before Send

**Already added in ContentAPIManager.ts** (line 104-110):
```typescript
console.log('[ContentAPIManager] FormData entries:', Array.from(formData.entries()));
```

**Check browser console for this output.**

### Fix 3: Use Absolute URL

**Modify ContentAPIManager constructor:**
```typescript
constructor(sessionToken: string, baseURL?: string) {
  this.sessionToken = sessionToken;
  // Use absolute URL instead of relying on Next.js proxy
  this.baseURL = baseURL || (typeof window !== 'undefined' 
    ? 'http://35.215.64.103:8000'  // Direct backend URL
    : 'http://localhost:8000');
}
```

### Fix 4: Check Next.js Configuration

**Verify `next.config.js` has correct rewrites/proxy:**
```javascript
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://35.215.64.103:8000/api/:path*',
    },
  ];
}
```

---

## Next Steps

1. ✅ **Review complete flow** - DONE
2. ⏳ **Check browser console** - Look for `[ContentAPIManager]` logs
3. ⏳ **Check Next.js config** - Verify rewrites/proxy
4. ⏳ **Test with absolute URL** - Bypass Next.js proxy
5. ⏳ **Verify File objects** - Check size and type before upload

---

## Summary

**Status:** ✅ **FLOW REVIEWED - ISSUE IDENTIFIED**

**Finding:** File objects are correctly handled through the flow, but **file content is missing in the network request body**.

**Root Cause:** File content is not being serialized into FormData, likely due to:
- File objects being empty/corrupted
- Browser FormData serialization issue
- Next.js proxy stripping content

**Next:** Check browser console logs and Next.js configuration.






