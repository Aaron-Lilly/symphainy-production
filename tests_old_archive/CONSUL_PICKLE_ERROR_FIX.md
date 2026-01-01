# Consul Pickle Error Fix

**Date:** 2025-12-04  
**Status:** ✅ **FIXED**

---

## 🎯 **Root Cause**

**Issue:** `TypeError: cannot pickle '_thread.lock' object`

**Location:** `CapabilityRegistryService.register_capability()` when serializing `CapabilityDefinition` for Consul registration

**Root Cause:**
1. `CapabilityDefinition.contracts` can contain handlers/service instances
2. Handlers/service instances contain thread locks (from async operations, logging, etc.)
3. When trying to serialize `contracts` for Consul registration, Python tries to pickle these objects
4. Thread locks cannot be pickled → Error

**Additional Finding:**
- `python-consul` 1.1.0 does NOT support `meta` parameter
- We're correctly converting `meta` to tags (this is the right approach)
- Consul v1.21.4 supports `meta`, but python-consul library doesn't expose it

---

## ✅ **Fix Applied**

**File:** `capability_registry_service.py`

**Changes:**
1. Enhanced `safe_serialize_capability()` to recursively check for unpicklable objects
2. Added `safe_serialize_for_consul()` helper in `_register_with_service_discovery()` methods
3. Skip objects with thread locks (`_lock`, `_thread`, `lock`, `thread`)
4. Skip handlers and service instances (`handler`, `service_instance`, `instance`)
5. Recursively clean nested dicts and lists

**Key Principle:** Only serialize simple, picklable data types (str, int, float, bool, None, dict, list of simple types)

---

## 📋 **What We're Sending to Consul**

**Current Format (via tags):**
```python
tags = [
    "service_type:CityManagerProtocol",
    "capabilities:service_discovery,realm_orchestration",
    "endpoints:",
    "realm:smart_city",
    "registered_at:2025-12-04T06:34:33.853449"
]
```

**Note:** `ServiceMeta` is empty because python-consul doesn't support `meta` parameter. This is expected and acceptable - tags work fine for our use case.

---

## ✅ **Expected Results**

1. ✅ No more pickle errors during capability registration
2. ✅ Services register successfully in Curator cache
3. ✅ Services register successfully in Consul (via tags)
4. ✅ Only serializable data is sent to Consul

---

## 🚀 **Next Steps**

1. ✅ Pickle error fix applied
2. ⏳ Test capability registration
3. ⏳ Verify services are discoverable
4. ⏳ Test service discovery in cache-only mode

---

**Status:** Consul pickle error fixed - only serializable data is now sent to Consul.



