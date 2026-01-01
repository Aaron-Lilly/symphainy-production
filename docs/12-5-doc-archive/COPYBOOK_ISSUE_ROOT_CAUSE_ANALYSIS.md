# Copybook Issue - Root Cause Analysis

**Date:** December 4, 2024  
**Status:** 🔍 **Investigation In Progress**

---

## 🎯 **Issue Summary**

The binary copybook test is correctly failing because copybook parsing requires a valid copybook, but the copybook parameter isn't reaching the MainframeProcessingAbstraction.

**Error Message:**
```
"Copybook required. Provide 'copybook' (string or bytes) in options."
```

**Test Request:**
```json
POST /api/v1/content-pillar/process-file/{file_id}
{
    "action": "parse",
    "options": {
        "copybook": copybook_content,
        "file_type": "binary"
    }
}
```

---

## 🔍 **Code Flow Analysis**

### Request Flow
1. **Test** → Sends: `{"action": "parse", "options": {"copybook": "...", "file_type": "binary"}}`
2. **universal_pillar_router** → Extracts JSON body → `body = await request.json()` → puts in `request_payload["params"] = body`
3. **FrontendGatewayService.route_frontend_request** → Receives `request` with `params` containing JSON body
4. **FrontendGatewayService._route_via_discovery** → Extracts `request_data = request.get("params", {}).copy()` → should have `options`
5. **APIRoutingUtility.route_request** → Creates `RequestContext(body=request_data)` → passes to handler
6. **Adapter Handler** → Receives `request_body` (which is `request_context.body`) → should extract `options`
7. **handle_process_file_request** → Receives `processing_options` → should contain `copybook`
8. **ContentAnalysisOrchestrator.process_file** → Receives `processing_options` → becomes `parse_options`
9. **ContentAnalysisOrchestrator.parse_file** → Receives `parse_options` → should contain `copybook`
10. **FileParserService.parse_file** → Receives `parse_options` → creates `FileParsingRequest(options=parse_options)`
11. **MainframeProcessingAbstraction.parse_file** → Checks: `request.options.get("copybook")` → **NOT FOUND**

### Issue Location
The copybook is being passed correctly through steps 1-5, but `request.options` in step 11 is empty or doesn't contain the copybook.

---

## 🔧 **Key Findings**

### 1. Legacy Architecture Difference
**Legacy Backend (`symphainy-mvp-backend-final-legacy`):**
- Copybook was uploaded as a **separate file** (`copybook: Optional[UploadFile] = File(None)`)
- Stored separately in GCS with its own UUID
- Retrieved from file metadata during parsing: `copybook_url = file_record.get("copybook_path")`
- Passed to parsing function as a file path

**Current Architecture:**
- Copybook is passed as a **string in JSON body** (`options: {"copybook": "..."}`)
- Expected to be in `request.options` when reaching `MainframeProcessingAbstraction`
- But it's not making it through the abstraction layers

### 2. Adapter Handler Issue
**Location:** `frontend_gateway_service.py` line 1288-1305

**Problem:** The adapter handler was looking for `processing_options` in `request_body`, but the JSON body has `options`.

**Fix Applied:** Updated adapter to extract `options` from `request_body`:
```python
processing_options = request_body.get("options") or request_body.get("processing_options")
```

**Status:** Fix applied, but copybook still not reaching parser.

### 3. Debug Logging Issue
**Problem:** Debug logs with `🔍🔍🔍` aren't appearing in logs, even though:
- Code is being executed (request is processed)
- Logger is configured correctly
- Log level is WARNING (should definitely show)

**Possible Causes:**
- Logger name mismatch
- Log filtering
- Code path not being executed

---

## 🎯 **Next Steps**

### 1. Verify Request Body Structure
Add logging to see what's actually in `request_body` when it reaches the adapter:
- Check if `options` is in `request_body`
- Check if `request_body` has the JSON body at all
- Verify `request_data` construction in `_route_via_discovery`

### 2. Check FileParsingRequest Construction
Verify that `FileParsingRequest(options=parse_options)` is correctly preserving the `copybook`:
- Check if `parse_options` has `copybook` when creating `FileParsingRequest`
- Verify `request.options` in `MainframeProcessingAbstraction`

### 3. Alternative Approach
Consider if we should follow the legacy pattern:
- Upload copybook as a separate file
- Store it separately
- Retrieve it from metadata during parsing
- Pass it as a file path to the adapter

---

## 📝 **Code References**

- **Legacy Upload:** `symphainy-mvp-backend-final-legacy/backend/routes/fms.py:33-92`
- **Legacy Parsing:** `symphainy-mvp-backend-final-legacy/backend/utils/parsing.py:15-30`
- **Current Adapter:** `frontend_gateway_service.py:1288-1305`
- **Current Abstraction:** `mainframe_processing_abstraction.py:97-140`
- **Current Adapter (Mainframe):** `mainframe_processing_adapter.py:141-184`

---

## ✅ **Fixes Applied**

1. ✅ Updated adapter to extract `options` from `request_body` (line 1294)
2. ✅ Added debug logging (not appearing in logs - needs investigation)
3. ✅ Added logging in `handle_process_file_request` (not appearing - needs investigation)

---

## 🔄 **Status**

- **Root Cause:** Copybook in `options` JSON body not reaching `MainframeProcessingAbstraction`
- **Fix Status:** Partial - adapter updated, but copybook still not reaching parser
- **Next Action:** Verify request body structure and FileParsingRequest construction


