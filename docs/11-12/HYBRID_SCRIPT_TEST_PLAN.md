# Hybrid Script Test Plan

## Current Status
The hybrid script has been created but needs refinement. The exception handler update logic is complex and needs testing.

## Recommendation: Manual Test First

Given the complexity of exception handler parsing, let's:

1. **Test on 2-3 files manually first** to validate the pattern
2. **Then refine the script** based on what we learn
3. **Then use the script** for the remaining files

## Test Files Selected
1. `analytics_abstraction.py` - 6 async methods, 4 exception handlers
2. `auth_abstraction.py` - 7 async methods
3. `authorization_abstraction.py` - 7 async methods

## Manual Update Pattern (for testing)

### Step 1: Update Constructor
- Add `di_container=None` parameter
- Add `self.di_container = di_container`
- Add `self.service_name = "<service_name>_abstraction"`
- Get logger from DI container
- Update logger.info message

### Step 2: Update Exception Handlers
For each `except Exception as e:` block:
- Add utility retrieval code before existing logger.error
- Update logger to self.logger
- Add error_handler.handle_error call

### Step 3: Add Telemetry (Manual)
- Review each success path
- Add telemetry.record_platform_operation_event before return

## After Manual Test
Once we've manually updated 2-3 files and validated the pattern:
1. Refine the script based on real examples
2. Test script on the same files (should show no changes needed)
3. Then use script for remaining files












