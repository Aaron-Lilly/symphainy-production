# Startup Warnings and Issues - Remediation Plan

**Date:** 2025-11-13  
**Status:** Platform starts successfully, but several warnings/issues need attention  
**Priority:** Medium (non-blocking, but should be addressed for production readiness)

---

## Summary

The platform now starts successfully! ✅ City Manager imports correctly, and all foundations initialize. However, there are several warnings and errors that should be addressed to ensure full functionality and clean logs.

---

## Issues Identified

### 🔴 **Critical Issues** (May affect functionality)

#### 1. **Experience Realm Import Error**
- **Location:** `main.py` line 354
- **Error:** `No module named 'backend.experience'`
- **Impact:** MVP API routers not registered
- **Root Cause:** Code still trying to import Experience as a realm, but it's now a Foundation
- **Priority:** High (affects API routing)

#### 2. **MCP Client Manager - Curator Method Missing**
- **Location:** `foundations/agentic_foundation/agent_sdk/mcp_client_manager.py`
- **Error:** `'CuratorFoundationService' object has no attribute 'get_service'`
- **Impact:** MCP endpoint discovery fails, falls back to config
- **Root Cause:** Method name mismatch - should be `discover_service` or similar
- **Priority:** High (affects MCP functionality)

---

### 🟡 **Medium Priority Issues** (Functionality works but needs cleanup)

#### 3. **Telemetry Reporting - Incorrect Method Call**
- **Location:** `bases/mixins/performance_monitoring_mixin.py:124`
- **Error:** `'TelemetryReportingUtility' object has no attribute 'record_event'`
- **Impact:** Telemetry events not recorded (metrics still work)
- **Frequency:** Appears ~10 times during startup
- **Root Cause:** Code is calling `record_event()` which doesn't exist. `TelemetryReportingUtility` has the correct method for sending telemetry information, but it's NOT `record_event`.
- **Available Methods in TelemetryReportingUtility:**
  - `record_metric()` - async, for metrics
  - `log_health_metrics()` - async, for health data
  - `log_anomaly()` - async, for anomalies
- **Priority:** Medium (affects observability)

#### 4. **WebSocket Adapter Initialization**
- **Location:** `foundations/communication_foundation/infrastructure_adapters/websocket_adapter.py`
- **Error:** `'PublicWorksFoundationService' object has no attribute 'get_websocket_adapter'`
- **Impact:** WebSocket functionality not available
- **Root Cause:** Method doesn't exist on PublicWorksFoundationService
- **Priority:** Medium (affects real-time features)

#### 5. **Messaging Adapter Initialization**
- **Location:** `foundations/communication_foundation/infrastructure_adapters/messaging_adapter.py`
- **Error:** `'MessagingAbstraction' object has no attribute 'initialize'`
- **Impact:** Messaging functionality not available
- **Root Cause:** Abstraction doesn't have `initialize()` method
- **Priority:** Medium (affects messaging features)

#### 6. **Event Bus Adapter Initialization**
- **Location:** `foundations/communication_foundation/infrastructure_adapters/event_bus_adapter.py`
- **Error:** `'EventManagementAbstraction' object has no attribute 'initialize'`
- **Impact:** Event bus functionality not available
- **Root Cause:** Abstraction doesn't have `initialize()` method
- **Priority:** Medium (affects event-driven features)

---

### 🟢 **Low Priority Issues** (Non-critical, cleanup items)

#### 7. **Agent Specialization Management**
- **Location:** `foundations/curator_foundation/micro_services/agent_specialization_management_service.py`
- **Error:** `Failed to load specializations from registry: 'list' object has no attribute 'items'`
- **Impact:** Specializations may not load correctly
- **Root Cause:** Data structure mismatch (expecting dict, getting list)
- **Priority:** Low (affects agent specialization features)

#### 8. **AGUI Schema Documentation**
- **Location:** `foundations/curator_foundation/micro_services/agui_schema_documentation_service.py`
- **Error:** `'AGUISchemaRegistry' object has no attribute 'get_all_schemas'`
- **Impact:** AGUI schema documentation not generated
- **Root Cause:** Method name mismatch or missing implementation
- **Priority:** Low (affects documentation generation)

#### 9. **Telemetry Metric Recording (Async)**
- **Location:** `bases/mixins/performance_monitoring_mixin.py:131`
- **Warning:** `RuntimeWarning: coroutine 'TelemetryReportingUtility.record_metric' was never awaited`
- **Impact:** Metrics may not be recorded correctly
- **Root Cause:** Async method called without `await`
- **Priority:** Low (affects metrics collection)

---

## Remediation Plan

### Phase 1: Critical Fixes (Do First)

#### Fix 1.1: Remove Experience Realm Import
**File:** `main.py` (around line 354)  
**Action:**
- Find code that tries to import `backend.experience`
- Remove or update to use Experience Foundation instead
- Ensure MVP API routers are registered via Experience Foundation SDK

**Steps:**
1. Search for `backend.experience` import in `main.py`
2. Replace with Experience Foundation SDK usage
3. Update router registration logic

---

#### Fix 1.2: Fix MCP Client Manager Curator Method
**File:** `foundations/agentic_foundation/agent_sdk/mcp_client_manager.py`  
**Action:**
- Check what method CuratorFoundationService actually has for service discovery
- Update `mcp_client_manager.py` to use correct method name
- Options: `discover_service()`, `get_service()`, `find_service()`, etc.

**Steps:**
1. Check `CuratorFoundationService` for service discovery methods
2. Update `MCPClientManager.initialize()` to use correct method
3. Test MCP endpoint discovery

---

### Phase 2: Medium Priority Fixes

#### Fix 2.1: Fix Telemetry Event Recording - Use Correct Method ✅ COMPLETED
**File:** `bases/mixins/performance_monitoring_mixin.py:121`  
**Status:** ✅ FIXED

**Solution:**
- `TelemetryReportingUtility` does NOT have `record_event()` method
- Updated `record_telemetry_event()` to use:
  - `log_anomaly()` for error events (when event_name contains "error")
  - `record_metric()` for operation events (with value=1.0 and event data as tags)
- Made `record_telemetry_event()` async to match `TelemetryReportingUtility` methods
- Updated all callers to use `await`:
  - `handle_error_with_audit()` - now uses `await`
  - `log_operation_with_telemetry()` - now uses `await`
- Also updated `record_telemetry_metric()` to be async and use correct `tags` parameter
- Updated `track_performance()` to be async
- Updated callers in `curator_foundation_service.py` to use `await`
- Updated `public_works_foundation_service.py` sync method to handle async gracefully

**Files Changed:**
- `bases/mixins/performance_monitoring_mixin.py` - Main fix
- `foundations/curator_foundation/curator_foundation_service.py` - Updated callers
- `foundations/public_works_foundation/public_works_foundation_service.py` - Updated sync caller

---

#### Fix 2.2: Fix WebSocket Adapter Initialization
**File:** `foundations/communication_foundation/infrastructure_adapters/websocket_adapter.py`  
**Action:**
- Check if `PublicWorksFoundationService` has WebSocket abstraction access
- Update adapter to get WebSocket abstraction via Platform Gateway or direct access
- Ensure proper initialization pattern

**Steps:**
1. Check how WebSocket abstraction is accessed in Public Works Foundation
2. Update `WebSocketAdapter.__init__()` to use correct access pattern
3. Test WebSocket initialization

---

#### Fix 2.3: Fix Messaging Adapter Initialization
**File:** `foundations/communication_foundation/infrastructure_adapters/messaging_adapter.py`  
**Action:**
- Check if `MessagingAbstraction` needs initialization
- If not, remove `initialize()` call
- If yes, add `initialize()` method to abstraction

**Steps:**
1. Check `MessagingAbstraction` class definition
2. Either add `initialize()` method or remove call
3. Test messaging functionality

---

#### Fix 2.4: Fix Event Bus Adapter Initialization
**File:** `foundations/communication_foundation/infrastructure_adapters/event_bus_adapter.py`  
**Action:**
- Check if `EventManagementAbstraction` needs initialization
- If not, remove `initialize()` call
- If yes, add `initialize()` method to abstraction

**Steps:**
1. Check `EventManagementAbstraction` class definition
2. Either add `initialize()` method or remove call
3. Test event bus functionality

---

### Phase 3: Low Priority Cleanup

#### Fix 3.1: Fix Agent Specialization Data Structure
**File:** `foundations/curator_foundation/micro_services/agent_specialization_management_service.py`  
**Action:**
- Check what data structure specialization registry returns
- Update code to handle both list and dict formats
- Add proper type checking/validation

**Steps:**
1. Check specialization registry return type
2. Update code to handle correct data structure
3. Add type validation

---

#### Fix 3.2: Add `get_all_schemas` Method to AGUISchemaRegistry
**File:** `foundations/agentic_foundation/agent_sdk/agui_schema_registry.py` (or wherever it's defined)  
**Action:**
- Add `get_all_schemas()` method to `AGUISchemaRegistry`
- Or update caller to use correct method name
- Ensure method returns expected format

**Steps:**
1. Find `AGUISchemaRegistry` class
2. Check if method exists with different name
3. Add missing method or update caller

---

#### Fix 3.3: Fix Async Telemetry Metric Recording
**File:** `bases/mixins/performance_monitoring_mixin.py:131`  
**Action:**
- Check if `record_metric` is async
- If yes, add `await` keyword
- If no, ensure method is synchronous

**Steps:**
1. Check `TelemetryReportingUtility.record_metric()` signature
2. Add `await` if async, or make method sync
3. Update all callers if needed

---

## Testing Plan

After each fix:
1. **Startup Test:** Verify platform starts without errors
2. **Functionality Test:** Test the specific feature that was broken
3. **Log Review:** Ensure no new warnings appear

### Full Test Suite (After All Fixes):
1. ✅ Platform startup completes successfully
2. ✅ All foundations initialize without errors
3. ✅ City Manager initializes correctly
4. ✅ MCP endpoint discovery works
5. ✅ Telemetry events are recorded
6. ✅ WebSocket/Messaging/EventBus adapters initialize
7. ✅ No warnings in startup logs (except expected ones)

---

## Notes

- **Platform Status:** ✅ **OPERATIONAL** - All critical functionality works
- **These issues are non-blocking** for basic platform operation
- **Priority order:** Critical → Medium → Low
- **Estimated time:** 
  - Phase 1: 1-2 hours
  - Phase 2: 2-3 hours  
  - Phase 3: 1-2 hours
  - **Total: 4-7 hours**

---

## Success Criteria

✅ Platform starts cleanly with no errors  
✅ All adapters initialize successfully  
✅ Telemetry/metrics work correctly  
✅ MCP discovery works via Curator  
✅ Clean startup logs (only expected warnings)

---

**Created:** 2025-11-13  
**Last Updated:** 2025-11-13

