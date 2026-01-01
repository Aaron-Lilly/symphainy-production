# LogRecord exc_info Conflict Fix

**Date:** 2025-12-01  
**Issue:** "Attempt to overwrite 'exc_info' in LogRecord" error when uploading files

## Root Cause

The error occurs when:
1. An exception happens during file upload
2. The logger tries to log the exception (Python automatically sets `exc_info` on the LogRecord)
3. The `TraceContextFormatter` tries to modify the LogRecord by adding `trace_id`, `request_id`, `user_id`
4. This creates a conflict because `exc_info` is a protected attribute that cannot be overwritten once set

## Solution

### Changes Made

1. **TraceContextFormatter (`utilities/logging/trace_context_formatter.py`):**
   - Added check for `exc_info` before modifying LogRecord
   - If `exc_info` is present, format the message manually instead of modifying the record
   - This prevents the "Attempt to overwrite 'exc_info'" error

2. **FrontendGatewayService (`foundations/experience_foundation/services/frontend_gateway_service/frontend_gateway_service.py`):**
   - Updated error handler to explicitly set `exc_info=False` when logging upload errors
   - This prevents Python from automatically setting `exc_info` on the LogRecord

## Technical Details

### Why This Happens

Python's logging system has special handling for exceptions:
- When you call `logger.error()` with an exception in the context, Python automatically sets `exc_info` on the LogRecord
- `exc_info` is a protected attribute (like `__dict__`) that cannot be modified once set
- Our `TraceContextFormatter` was trying to modify the record AFTER `exc_info` was set, causing the conflict

### The Fix

1. **Detect exc_info presence:** Check if `exc_info` or `exc_text` is already set on the record
2. **Skip record modification:** If `exc_info` is present, don't try to set attributes on the record
3. **Manual formatting:** Format the message manually to include trace context without modifying the record
4. **Explicit exc_info=False:** In error handlers, explicitly set `exc_info=False` to prevent automatic exception info capture

## Testing

After the fix:
1. Try uploading a file
2. Should no longer see "Attempt to overwrite 'exc_info' in LogRecord" error
3. Error messages should still include trace context information
4. Exception details should still be logged (just not via exc_info)

## Files Modified

1. `utilities/logging/trace_context_formatter.py` - Added exc_info detection and manual formatting
2. `foundations/experience_foundation/services/frontend_gateway_service/frontend_gateway_service.py` - Set exc_info=False in error handler






