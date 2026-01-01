# File Upload Comprehensive Debugging

**Date:** 2025-12-02  
**Status:** 🔍 **COMPREHENSIVE LOGGING ENABLED**

---

## Issue Analysis

**Error:** `object of type 'NoneType' has no len()`

**Network Logs Show:**
- ✅ Request sent to `/api/v1/content-pillar/upload-file`
- ✅ Content-Type: `multipart/form-data`
- ✅ Field names: `file` and `copybook` (correct)
- ⚠️ Body appears empty in string representation (normal for binary, but need to verify)

**Backend Logs:**
- ❌ No file extraction logs visible
- ✅ Request received (200 OK)
- ⚠️ `file_data` is None when reaching handler

---

## Root Cause Hypothesis

**Most Likely:** Files are being sent, but FastAPI's `request.form()` isn't extracting them properly, OR the files are being read but the content is empty/None.

**Possible Causes:**
1. **FastAPI UploadFile Issue:** Files might not be properly parsed from multipart form
2. **File Reading Issue:** `value.read()` might return None or empty bytes
3. **Form Data Parsing Issue:** `request.form()` might not be finding the files
4. **Content-Type Issue:** Multipart boundary might not be parsed correctly

---

## Enhanced Logging Added

### 1. Request Entry Logging ✅

**Location:** Start of `universal_pillar_handler`

**Logs:**
```
🌐 Request: POST /content-pillar/upload-file, Content-Type: multipart/form-data; boundary=...
```

### 2. Form Data Parsing Logging ✅

**Location:** Before and after `request.form()`

**Logs:**
```
📋 Parsing multipart/form-data...
📋 Form data keys: ['file', 'copybook', ...]
```

### 3. Field Processing Logging ✅

**Location:** For each form field

**Logs:**
```
🔍 Processing form field: key='file', type=UploadFile
```

### 4. File Extraction Logging ✅

**Location:** When UploadFile is detected

**Logs:**
```
📎 Extracted file: key='file', filename='telemetry_raw.bin', size=1597 bytes
```

### 5. File Mapping Logging ✅

**Location:** When files are added to params

**Logs:**
```
📦 Files extracted: ['file', 'copybook']
✅ Main file added to params: filename='...', size=... bytes
```

---

## Next Test

**Action:** Try uploading again and check logs:

```bash
docker logs symphainy-backend-prod --tail 100 | grep -E "🌐|📋|🔍|📎|📦|✅|❌|file"
```

**Expected Output (Success):**
```
🌐 Request: POST /content-pillar/upload-file, Content-Type: multipart/form-data; boundary=...
📋 Parsing multipart/form-data...
📋 Form data keys: ['file', 'copybook']
🔍 Processing form field: key='file', type=UploadFile
📎 Extracted file: key='file', filename='telemetry_raw.bin', size=1597 bytes
🔍 Processing form field: key='copybook', type=UploadFile
📎 Extracted file: key='copybook', filename='telemetry_copybook.cpy', size=234 bytes
📦 Files extracted: ['file', 'copybook']
✅ Main file added to params: filename='telemetry_raw.bin', size=1597 bytes
✅ Copybook file added to params: filename='telemetry_copybook.cpy', size=234 bytes
```

**If Files Not Found:**
```
📋 Form data keys: []  # Empty!
```

**If Files Found But Not UploadFile:**
```
🔍 Processing form field: key='file', type=str  # Wrong type!
```

**If Files Empty:**
```
⚠️ File 'file' has no content (filename: telemetry_raw.bin)
```

---

## Potential Fixes Based on Findings

### Fix 1: If Form Data Keys Empty

**Issue:** `request.form()` returns empty dict

**Possible Causes:**
- Content-Type header issue
- FastAPI multipart parsing issue
- Request body not being read correctly

**Fix:** Check if we need to use `request.form()` differently or if there's a FastAPI version issue.

### Fix 2: If Files Are Not UploadFile Type

**Issue:** Files are strings or other types

**Possible Causes:**
- FormData encoding issue
- FastAPI parsing issue

**Fix:** Handle different types or fix FormData construction.

### Fix 3: If File Content Is Empty

**Issue:** `value.read()` returns empty bytes

**Possible Causes:**
- File already read elsewhere
- File stream issue
- FastAPI UploadFile issue

**Fix:** Check if file needs to be read differently or if there's a stream position issue.

---

## Summary

**Status:** 🔍 **COMPREHENSIVE LOGGING ENABLED**

**What We'll Learn:**
- ✅ If form data is being parsed
- ✅ What keys are found
- ✅ What types the values are
- ✅ If files are being extracted
- ✅ If file content is empty

**Next:** Test upload and check logs to identify exact issue.






