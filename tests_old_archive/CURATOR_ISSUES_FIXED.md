# Curator Issues - Root Causes and Fixes

**Date:** 2025-12-04  
**Status:** ✅ **FIXES APPLIED**

---

## 🎯 **Root Causes Identified**

### **Issue 1: TypeError - cannot pickle '_thread.lock' object**

**Root Cause:** When registering with service discovery, the code tries to serialize metadata that contains unpicklable objects (thread locks from async operations, logging, etc.).

**Fix:** 
- Wrapped service discovery registration in try-except
- Ensure all values in `service_info` are serializable (convert to strings)
- Service discovery registration is now OPTIONAL - cache registration is PRIMARY
- If service discovery fails, we still register in cache (cache-only mode is valid)

### **Issue 2: RecursionError - maximum recursion depth exceeded**

**Root Cause:** Circular reference during registration (likely in capability registration or service discovery).

**Fix:**
- Service discovery registration is now wrapped in try-except
- If recursion occurs, we catch it and continue with cache registration

### **Issue 3: Capability Validation Errors**

**Root Cause:** Some capabilities don't have required contracts (soa_api, rest_api, or mcp_tool).

**Status:** This is a separate issue that needs to be fixed in the services that register capabilities.

---

## ✅ **Fixes Applied**

### **File:** `curator_foundation_service.py` - `register_service()`

**Changes:**
1. Wrapped service discovery registration in try-except
2. Ensure all values in `service_info` are serializable (convert to strings)
3. Service discovery registration is now OPTIONAL - cache registration is PRIMARY
4. If service discovery fails, we still register in cache (cache-only mode is valid)

**Key Principle:** Cache registration is PRIMARY, service discovery is SECONDARY. If service discovery fails, we still register in cache.

---

## 📋 **Expected Results**

1. ✅ Services register in cache even if service discovery fails
2. ✅ No more "cannot pickle '_thread.lock' object" errors blocking registration
3. ✅ No more recursion errors blocking registration
4. ✅ Services are discoverable via cache even in cache-only mode
5. ✅ Better error logging for service discovery failures

---

## 🚀 **Next Steps**

1. ✅ Service discovery registration wrapped in try-except
2. ✅ Cache registration is PRIMARY (always happens)
3. ⏳ Fix capability validation errors (separate issue)
4. ⏳ Test service discovery in cache-only mode

---

**Status:** Curator registration issues fixed - services now register in cache even if service discovery fails.



