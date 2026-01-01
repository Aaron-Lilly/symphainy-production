# Frontend FormData Issue Analysis

**Date:** 2025-12-02  
**Status:** 🔍 **INVESTIGATING**

---

## Issue

**Error:** `object of type 'NoneType' has no len()`

**Network Logs Show:**
```
Content-Disposition: form-data; name="file"; filename="telemetry_raw.bin"
Content-Type: application/octet-stream

Content-Disposition: form-data; name="copybook"; filename="telemetry_copybook.cpy"
Content-Type: application/octet-stream

```

**Observation:** The multipart body shows headers but **NO FILE CONTENT** between boundaries. The body appears empty.

**Backend Logs Show:**
- ✅ Request reaches FrontendGatewayService
- ❌ `filename: None` (files not extracted)
- ❌ No router logging visible (handler might not be called)

---

## Root Cause Hypothesis

**Most Likely:** The File objects in the frontend are empty or not properly attached to FormData.

**Possible Causes:**
1. **File objects are null/undefined** when passed to `uploadFile()`
2. **File objects were already read/consumed** before being attached to FormData
3. **Browser issue** with FormData construction
4. **Router handler not being called** (route mismatch?)

---

## Frontend Code Review

### FileUploader.tsx

**File Selection:**
```typescript
const onDrop = useCallback((acceptedFiles: File[]) => {
  const file = acceptedFiles[0];
  setUploadState(prev => ({
    ...prev,
    selectedFile: file,  // ✅ File object stored
    error: null,
    success: false
  }));
}, []);
```

**Upload Handler:**
```typescript
const result = await apiManager.uploadFile(
  uploadState.selectedFile,      // ✅ File object passed
  uploadState.copybookFile || undefined
);
```

### ContentAPIManager.ts

**FormData Construction:**
```typescript
const formData = new FormData();
formData.append('file', file);  // ✅ File object appended

if (copybookFile) {
  formData.append('copybook', copybookFile);  // ✅ Copybook appended
}
```

**Code looks correct!** But the network logs show empty content.

---

## Debugging Steps

### 1. Verify Router Handler is Called ✅

**Added print statements to confirm handler execution:**
```python
print(f"[UNIVERSAL_ROUTER] Handler called: {request.method} /{pillar}/{path}")
logger.info(f"[UNIVERSAL_ROUTER] Handler called: {request.method} /{pillar}/{path}")
```

**Check logs:**
```bash
docker logs symphainy-backend-prod 2>&1 | grep -E "UNIVERSAL_ROUTER|🌐|📋"
```

### 2. Verify File Objects in Frontend

**Add console logging in ContentAPIManager.ts:**
```typescript
async uploadFile(file: File, copybookFile?: File): Promise<UploadResponse> {
  console.log('[ContentAPIManager] uploadFile called');
  console.log('[ContentAPIManager] file:', file);
  console.log('[ContentAPIManager] file.name:', file?.name);
  console.log('[ContentAPIManager] file.size:', file?.size);
  console.log('[ContentAPIManager] file.type:', file?.type);
  
  const formData = new FormData();
  formData.append('file', file);
  console.log('[ContentAPIManager] FormData entries:', Array.from(formData.entries()));
  
  // ... rest of code
}
```

### 3. Check Browser Network Tab

**In browser DevTools:**
- Open Network tab
- Find the upload request
- Check "Payload" tab
- Verify file content is present in FormData

---

## Potential Fixes

### Fix 1: If File Objects Are Null

**Issue:** `uploadState.selectedFile` is null when upload is called

**Fix:** Add validation before upload:
```typescript
if (!uploadState.selectedFile || !(uploadState.selectedFile instanceof File)) {
  setUploadState(prev => ({ ...prev, error: 'Invalid file selected' }));
  return;
}
```

### Fix 2: If Files Are Already Read

**Issue:** File objects were read/consumed before being attached to FormData

**Fix:** Ensure File objects are not read before FormData construction. File objects should be used directly, not read into ArrayBuffer/Blob first.

### Fix 3: If Router Handler Not Called

**Issue:** Route pattern doesn't match `/api/v1/content-pillar/upload-file`

**Fix:** Check route pattern configuration:
```python
# Should be: /api/v1/{pillar}/{path:path}
# Matches: /api/v1/content-pillar/upload-file
# With: pillar="content-pillar", path="upload-file"
```

### Fix 4: If FormData Not Working

**Issue:** Browser FormData API issue

**Fix:** Try alternative approach:
```typescript
// Instead of:
formData.append('file', file);

// Try:
formData.append('file', file, file.name);
```

---

## Next Steps

1. ✅ **Added print statements** to confirm router handler is called
2. ⏳ **Test upload again** and check logs
3. ⏳ **Add frontend console logging** to verify File objects
4. ⏳ **Check browser Network tab** to verify FormData content
5. ⏳ **Apply targeted fix** based on findings

---

## Summary

**Status:** 🔍 **INVESTIGATING**

**Hypothesis:** File objects are empty or not properly attached to FormData in frontend.

**Next:** Test upload with enhanced logging to identify exact issue.






