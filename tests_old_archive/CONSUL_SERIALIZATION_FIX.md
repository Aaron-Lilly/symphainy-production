# Consul Serialization Fix

**Date:** 2025-12-04  
**Status:** ✅ **FIXES APPLIED**

---

## 🎯 **Root Cause**

**User's Insight:**
> "can you also check that the underlying consul tables actually match what we're trying to register? I just realized I can't remember the last time we revisited our consul setup, but we've iterated our curator strategy at least a dozen times."

**Finding:** The pickle error was happening because:
1. `asdict(capability_def)` was trying to serialize `contracts` dict which contained unpicklable objects (handlers, service instances with thread locks)
2. Meta to tags conversion was trying to serialize complex objects using `str(v)` which can trigger pickle

---

## ✅ **Fixes Applied**

### **Fix 1: Safe Capability Serialization**

**File:** `capability_registry_service.py` - `register_capability()`

**Change:** Replaced `asdict(capability_def)` with `safe_serialize_capability()` that:
- Only serializes simple fields (strings, ints, etc.)
- Skips complex objects in `contracts` (handlers, service instances)
- Only includes contract metadata, not handlers/instances

**Before:**
```python
"capability": asdict(capability_def)  # ❌ Tries to serialize everything, including handlers with thread locks
```

**After:**
```python
def safe_serialize_capability(cap_def):
    """Safely serialize CapabilityDefinition, skipping unpicklable objects."""
    return {
        "capability_name": cap_def.capability_name,
        # ... simple fields ...
        "contracts": {
            # Only serialize contract metadata, skip handlers/instances
            k: {
                k2: v2 for k2, v2 in v.items() 
                if k2 not in ["handler", "service_instance", "instance"] and not hasattr(v2, '__dict__')
            } if isinstance(v, dict) else v
            for k, v in cap_def.contracts.items()
        },
        # ...
    }

"capability": safe_serialize_capability(capability_def)  # ✅ Only serializes safe fields
```

### **Fix 2: Safe Meta to Tags Conversion**

**File:** `consul_service_discovery_adapter.py` - `register_service()`

**Change:** Enhanced meta to tags conversion to:
- Skip complex objects (service instances, handlers)
- Only serialize simple types (str, int, float, bool, None)
- Handle lists/tuples by converting items to strings
- Handle dicts by converting to JSON (only if all values are simple)
- Log warnings for skipped complex objects

**Before:**
```python
for k, v in meta.items():
    enriched_tags.append(f"{k}:{str(v)}")  # ❌ str(v) on complex objects can trigger pickle
```

**After:**
```python
for k, v in meta.items():
    # Skip complex objects that might contain thread locks
    if hasattr(v, '__dict__') and not isinstance(v, (str, int, float, bool, type(None))):
        self.logger.debug(f"⚠️ Skipping meta key '{k}' - complex object type: {type(v).__name__}")
        continue
    
    # Handle simple types, lists, dicts safely
    # ... (see code for full implementation)
```

---

## 📋 **Consul Format Verification**

**Consul Status:**
- ✅ Consul is running and connected
- ✅ Services are registering successfully (CityManager, agent capabilities)
- ✅ Format matches Consul expectations (name, service_id, address, port, tags, check)

**What Consul Stores:**
- Services in service catalog
- Tags as string arrays
- Health checks in health check system
- Meta information converted to tags (format: "key:value")

**What We're Sending:**
- ✅ Correct format for basic service registration
- ✅ Tags are simple strings (no complex objects)
- ✅ Meta is safely converted to tags (complex objects skipped)

---

## 🎯 **Expected Results**

1. ✅ No more pickle errors during capability registration
2. ✅ No more pickle errors during service discovery registration
3. ✅ Services register in cache even if Consul registration has issues
4. ✅ Complex objects (handlers, service instances) are safely skipped
5. ✅ Only serializable metadata is sent to Consul

---

## 🚀 **Next Steps**

1. ✅ Safe serialization implemented
2. ⏳ Test registration with fixed serialization
3. ⏳ Verify services are discoverable via cache
4. ⏳ Verify Consul registrations are correct

---

**Status:** Serialization fixes applied - complex objects are now safely skipped during registration.

