# Adapters Utility Update Plan

**Date:** December 20, 2024  
**Status:** 🔄 **IN PROGRESS** - 2/6 adapters complete

---

## Executive Summary

Updating 6 adapters with DI container to use error_handler and telemetry utilities for consistency and better observability.

**Exempt Adapters:**
- ✅ `opentelemetry_health_adapter.py` - **EXEMPT** (provides health monitoring, using telemetry would be circular)

---

## Adapters to Update

### ✅ **Completed (2/6)**

1. ✅ `consul_service_discovery_adapter.py` - **COMPLETE**
   - 10 exception blocks updated with error_handler
   - Success paths updated with telemetry

2. ✅ `opa_policy_adapter.py` - **COMPLETE**
   - 6 exception blocks updated with error_handler
   - Success paths updated with telemetry

### 🔄 **In Progress (4/6)**

3. ⏳ `redis_event_bus_adapter.py` - **IN PROGRESS**
   - 12 exception blocks need error_handler
   - Success paths need telemetry

4. ⏳ `redis_messaging_adapter.py` - **IN PROGRESS**
   - 12 exception blocks need error_handler
   - Success paths need telemetry

5. ⏳ `session_management_adapter.py` - **PENDING**
   - 9 exception blocks need error_handler
   - Success paths need telemetry

6. ⏳ `state_management_adapter.py` - **PENDING**
   - 10 exception blocks need error_handler
   - Success paths need telemetry

---

## Exempt Adapters

### **Foundational Utility Adapters**

These adapters provide foundational utilities and should NOT use utilities to avoid circular dependencies:

1. ✅ `opentelemetry_health_adapter.py`
   - **Rationale:** Provides health monitoring capabilities
   - **Issue:** Using telemetry utility would be circular (telemetry might depend on health)
   - **Pattern:** Use logger only (like utility abstractions)

2. ✅ `telemetry_adapter.py`
   - **Rationale:** Provides telemetry capabilities
   - **Issue:** Using telemetry utility would be circular
   - **Pattern:** Use logger only (like utility abstractions)

---

## Update Pattern

### **Error Handler Pattern**

```python
except Exception as e:
    # Use error handler with telemetry
    error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
    telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
    if error_handler:
        await error_handler.handle_error(e, {
            "operation": "<method_name>",
            "service": self.service_name
        }, telemetry=telemetry)
    else:
        self.logger.error(f"❌ Operation failed: {e}")
    raise  # or return appropriate error response
```

### **Telemetry Pattern**

```python
# Before return statement
telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
if telemetry:
    await telemetry.record_platform_operation_event("<operation_name>", {
        "relevant_context": value,
        "success": True
    })

return result
```

---

## Progress Tracking

- **Total Adapters with DI Container:** 8
- **Exempt (Foundational Utility):** 1 (`opentelemetry_health_adapter`)
- **Exempt (Raw Technology):** 23
- **To Update:** 6
- **Completed:** 2
- **Remaining:** 4

---

**Last Updated:** December 20, 2024









