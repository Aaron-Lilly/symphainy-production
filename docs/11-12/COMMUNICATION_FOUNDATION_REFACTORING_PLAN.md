# Communication Foundation - Refactoring Plan

**Date:** November 19, 2025  
**Status:** Ready for Implementation  
**Current Compliance:** 14% (33/236 methods)

---

## 📊 Current Violations

- **Error Handling:** 322 violations
- **Telemetry:** 88 violations
- **Security:** 8 violations (likely false positives)
- **Tenant:** 12 violations (likely false positives)

---

## 🎯 Strategy

### Priority 1: Foundation Services (Have Utility Access)

These services inherit from `FoundationServiceBase` and have utility access:

1. **MessagingFoundationService** - Add error handling and telemetry
2. **EventBusFoundationService** - Add error handling and telemetry
3. **WebSocketFoundationService** - Add error handling and telemetry

### Priority 2: Abstractions (Need Architecture Review)

**Issue:** Abstractions don't inherit from `FoundationServiceBase`, so they don't have utility access.

**Options:**
1. Make abstractions inherit from a base class with utility access
2. Pass utilities via DI to abstractions
3. Keep abstractions simple and handle utilities at service layer

**Recommendation:** For now, focus on foundation services. Abstractions can be addressed in a separate architectural review.

### Priority 3: Realm Bridges (Have Utility Access)

Realm bridges should inherit from a base that provides utilities. Review and fix.

### Priority 4: Composition Services (Have Utility Access)

Composition services should have utility access. Review and fix.

---

## 🔧 Implementation Pattern for Foundation Services

Since foundation services inherit from `FoundationServiceBase`, they have access to:
- `handle_error_with_audit()`
- `log_operation_with_telemetry()`
- `record_health_metric()`

**Pattern for Foundation Services:**

```python
async def method_name(self, ...):
    """Method description."""
    try:
        # Start telemetry tracking
        await self.log_operation_with_telemetry("method_name_start", success=True)
        
        # Business logic (no security/tenant - abstractions don't need it)
        result = await self._do_work(...)
        
        # Record success metric
        await self.record_health_metric("method_name_success", 1.0, {})
        
        # End telemetry tracking
        await self.log_operation_with_telemetry("method_name_complete", success=True)
        
        return result
        
    except Exception as e:
        # Use enhanced error handling with audit
        await self.handle_error_with_audit(e, "method_name")
        raise  # Re-raise for service layer
```

---

## 📋 Files to Fix (Priority Order)

### 1. MessagingFoundationService
- **File:** `foundation_services/messaging_foundation_service.py`
- **Violations:** Error handling in `send_message()`, `receive_message()`, `realm_message_handler()`
- **Status:** Has utility access ✅

### 2. EventBusFoundationService
- **File:** `foundation_services/event_bus_foundation_service.py`
- **Violations:** Error handling in `publish_event()`, `subscribe_to_event()`, `unsubscribe_from_event()`
- **Status:** Has utility access ✅

### 3. WebSocketFoundationService
- **File:** `foundation_services/websocket_foundation_service.py`
- **Violations:** Error handling in `send_websocket_message()`, `realm_websocket_handler()`
- **Status:** Has utility access ✅

### 4. CommunicationCompositionService
- **File:** `composition_services/communication_composition_service.py`
- **Violations:** Error handling in multiple methods
- **Status:** Needs review for utility access

### 5. SOACompositionService
- **File:** `composition_services/soa_composition_service.py`
- **Violations:** Error handling in multiple methods
- **Status:** Needs review for utility access

---

## ⚠️ Architectural Note

**Abstractions (CommunicationAbstraction, WebSocketAbstraction, SOAClientAbstraction):**
- Don't inherit from `FoundationServiceBase`
- Don't have utility access
- Need architectural decision: Should abstractions have utility access?

**Options:**
1. Make abstractions inherit from a utility-enabled base class
2. Pass utilities via constructor/DI
3. Keep abstractions simple (utilities handled at service layer)

**For now:** Focus on foundation services that have utility access. Abstractions can be addressed separately.

---

## 🎯 Success Criteria

- ✅ Foundation services (Messaging, EventBus, WebSocket) have error handling and telemetry
- ✅ Realm bridges have error handling and telemetry
- ✅ Composition services have error handling and telemetry
- ⚠️ Abstractions: TBD (architectural decision needed)

---

**Estimated Time:** 1-2 days  
**Target Compliance:** 80%+








