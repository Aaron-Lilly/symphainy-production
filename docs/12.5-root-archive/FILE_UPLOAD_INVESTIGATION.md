# File Upload Investigation

**Date:** 2025-12-02  
**Status:** 🔍 **INVESTIGATING**

---

## Issue

User reports "object of type 'NoneType' has no len()" error when uploading binary files with copybook. Suspects there might be a mismatch in how files are being handled.

---

## Current Flow

### Frontend (`ContentAPIManager.ts`)

```typescript
const formData = new FormData();
formData.append('file', file);              // Main file
if (copybookFile) {
  formData.append('copybook', copybookFile); // Copybook file
}
```

**Field Names:**
- Main file: `'file'`
- Copybook: `'copybook'`

### Backend Router (`universal_pillar_router.py`)

**Extraction:**
```python
form_data = await request.form()
for key, value in form_data.items():
    if isinstance(value, UploadFile):
        file_content = await value.read()
        files[key] = {
            "filename": value.filename,
            "content": file_content,
            "content_type": value.content_type
        }
```

**Mapping to params:**
```python
if key == "file":
    request_payload["params"]["file_data"] = file_info["content"]
    request_payload["params"]["filename"] = file_info["filename"]
    request_payload["params"]["content_type"] = file_info["content_type"]
elif key == "copybook":
    request_payload["params"]["copybook_data"] = file_info["content"]
    request_payload["params"]["copybook_filename"] = file_info["filename"]
```

### FrontendGatewayService

**Extraction:**
```python
file_data=params.get("file_data"),      # Can be None!
filename=params.get("filename"),
content_type=params.get("content_type"),
copybook_data=params.get("copybook_data"),
copybook_filename=params.get("copybook_filename")
```

---

## Potential Issues

### 1. Field Name Mismatch ❓

**Hypothesis:** Frontend might be using a different field name than expected.

**Check:**
- Frontend uses `'file'` - should match
- Router expects `key == "file"` - should match
- But what if the form field name is different?

### 2. File Not Extracted ❓

**Hypothesis:** File might not be extracted correctly from multipart form.

**Possible Causes:**
- Form data parsing fails silently
- File content is empty
- File is read but becomes None somehow

### 3. Multiple Files Confusion ❓

**Hypothesis:** When both files are uploaded, there might be confusion about which is which.

**Check:**
- Are both files being extracted?
- Is the main file being overwritten by copybook?
- Is the order of extraction causing issues?

---

## Debugging Added

### Enhanced Logging in Router ✅

1. **File Extraction Logging:**
   - Log each file extracted with key, filename, and size
   - Warn if file content is empty
   - Validate filename is not None

2. **File Mapping Logging:**
   - Log all file keys found
   - Log when main file is added to params
   - Log when copybook is added to params
   - Warn about unknown file keys
   - Error if main file is missing

3. **Validation:**
   - Check if main file exists before routing
   - Return clear error if main file is missing

---

## Next Steps

### 1. Test Upload

**Action:** Try uploading a binary file with copybook again.

**Expected Logs:**
```
📎 Extracted file: key='file', filename='telemetry_raw.bin', size=1597 bytes
📎 Extracted file: key='copybook', filename='telemetry_copybook.cpy', size=XXX bytes
📦 Files extracted: ['file', 'copybook']
✅ Main file added to params: filename='telemetry_raw.bin', size=1597 bytes
✅ Copybook file added to params: filename='telemetry_copybook.cpy', size=XXX bytes
```

**If Main File Missing:**
```
❌ Main file ('file') not found in form data! Available keys: ['copybook']
```

### 2. Check Frontend FormData

**Action:** Verify frontend is using correct field names.

**Check:**
- `ContentAPIManager.ts` line 78: `formData.append('file', file)`
- Should match router expectation: `key == "file"`

### 3. Check Browser Network Tab

**Action:** Inspect the actual request being sent.

**Check:**
- FormData field names in browser DevTools
- File sizes match expectations
- Content-Type header is `multipart/form-data`

---

## Potential Fixes

### Fix 1: Case-Insensitive Key Matching

If field names have case issues:
```python
if key.lower() == "file":
    # ...
```

### Fix 2: Support Multiple Field Names

If frontend uses different names:
```python
# Support both 'file' and 'upload' or other variations
if key in ["file", "upload", "file_data"]:
    # ...
```

### Fix 3: Better Error Messages

Already added - will show which keys are available if main file is missing.

---

## Summary

**Status:** 🔍 **INVESTIGATING**

**Added:**
- ✅ Enhanced logging in router
- ✅ Validation for main file presence
- ✅ Clear error messages

**Next:**
- Test upload and check logs
- Verify field names match
- Check browser network tab






