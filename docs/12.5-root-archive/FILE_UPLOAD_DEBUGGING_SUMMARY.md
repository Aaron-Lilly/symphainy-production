# File Upload Debugging Summary

**Date:** 2025-12-02  
**Status:** 🔍 **DEBUGGING ENABLED**

---

## Issue

User experiencing "object of type 'NoneType' has no len()" error when uploading binary files with copybook. Suspects field name mismatch or file handling issue.

---

## Investigation Findings

### Frontend Implementation ✅

**Component:** `FileUploader.tsx` (used on content pillar page)

**Manager:** `ContentAPIManager.uploadFile()`

**Field Names:**
```typescript
formData.append('file', file);              // Main file
formData.append('copybook', copybookFile);   // Copybook file
```

**API Endpoint:** `/api/v1/content-pillar/upload-file`

### Backend Expectations ✅

**Router:** `universal_pillar_router.py`

**Expected Field Names:**
- Main file: `'file'` ✅ (matches frontend)
- Copybook: `'copybook'` ✅ (matches frontend)

**Mapping:**
```python
if key == "file":
    params["file_data"] = file_info["content"]
    params["filename"] = file_info["filename"]
    params["content_type"] = file_info["content_type"]
elif key == "copybook":
    params["copybook_data"] = file_info["content"]
    params["copybook_filename"] = file_info["filename"]
```

**Field names match!** ✅

---

## Enhanced Logging Added

### 1. File Extraction Logging ✅

**Location:** `universal_pillar_router.py` (lines 121-129)

**Logs:**
- Each file extracted with key, filename, and size
- Warning if file content is empty
- Validation that filename is not None

**Example Output:**
```
📎 Extracted file: key='file', filename='telemetry_raw.bin', size=1597 bytes
📎 Extracted file: key='copybook', filename='telemetry_copybook.cpy', size=234 bytes
```

### 2. File Mapping Logging ✅

**Location:** `universal_pillar_router.py` (lines 166-189)

**Logs:**
- All file keys found: `📦 Files extracted: ['file', 'copybook']`
- When main file is added: `✅ Main file added to params: filename='...', size=... bytes`
- When copybook is added: `✅ Copybook file added to params: filename='...', size=... bytes`
- Warning for unknown file keys
- **Error if main file is missing** with available keys

**Example Output:**
```
📦 Files extracted: ['file', 'copybook']
✅ Main file added to params: filename='telemetry_raw.bin', size=1597 bytes
✅ Copybook file added to params: filename='telemetry_copybook.cpy', size=234 bytes
```

**If Main File Missing:**
```
❌ Main file ('file') not found in form data! Available keys: ['copybook']
```

### 3. Validation Added ✅

**Location:** `universal_pillar_router.py` (lines 189-196)

**Checks:**
- Validates main file exists before routing
- Returns clear error with available keys if missing
- Prevents NoneType errors downstream

---

## Next Steps

### 1. Test Upload Again

**Action:** Try uploading a binary file with copybook.

**What to Check:**
1. **Backend Logs:**
   ```bash
   docker logs symphainy-backend-prod --tail 50 | grep -E "📎|📦|✅|❌|file"
   ```

2. **Expected Logs (Success):**
   ```
   📎 Extracted file: key='file', filename='telemetry_raw.bin', size=1597 bytes
   📎 Extracted file: key='copybook', filename='telemetry_copybook.cpy', size=234 bytes
   📦 Files extracted: ['file', 'copybook']
   ✅ Main file added to params: filename='telemetry_raw.bin', size=1597 bytes
   ✅ Copybook file added to params: filename='telemetry_copybook.cpy', size=234 bytes
   📤 Content Pillar: Upload file request: telemetry_raw.bin (1597 bytes)
   ```

3. **If Error:**
   ```
   ❌ Main file ('file') not found in form data! Available keys: [...]
   ```
   This will tell us what keys are actually being sent.

### 2. Check Browser Network Tab

**Action:** Open browser DevTools → Network tab → Upload file → Inspect request.

**What to Check:**
1. **Request URL:** Should be `/api/v1/content-pillar/upload-file`
2. **Content-Type:** Should be `multipart/form-data`
3. **Form Data:**
   - Should see `file: [File object]`
   - Should see `copybook: [File object]`
   - Check if field names match exactly

### 3. Verify File Sizes

**Action:** Check if file sizes in logs match what's shown in UI.

**From Screenshot:**
- Binary file: "1.56 KB" (should be ~1597 bytes)
- Copybook: Size not shown, but should be logged

---

## Potential Issues & Fixes

### Issue 1: Field Name Case Sensitivity

**If logs show:** `Available keys: ['File', 'Copybook']` (capitalized)

**Fix:** Make key matching case-insensitive:
```python
if key.lower() == "file":
    # ...
```

### Issue 2: Different Field Names

**If logs show:** `Available keys: ['upload', 'copybook_file']` (different names)

**Fix:** Support multiple field name variations:
```python
if key in ["file", "upload", "file_data"]:
    # ...
```

### Issue 3: File Not in FormData

**If logs show:** `Available keys: []` (no files)

**Fix:** Check frontend FormData construction - might need to verify file is actually added.

### Issue 4: File Content Empty

**If logs show:** `⚠️ File 'file' has no content`

**Fix:** Check if file is being read correctly - might be a FastAPI UploadFile issue.

---

## Summary

**Status:** 🔍 **DEBUGGING ENABLED**

**Changes:**
- ✅ Enhanced logging in router
- ✅ Validation for main file presence
- ✅ Clear error messages with available keys
- ✅ File extraction logging

**Field Names:** ✅ Match (frontend uses 'file'/'copybook', backend expects 'file'/'copybook')

**Next:** Test upload and check logs to see what's actually happening.






