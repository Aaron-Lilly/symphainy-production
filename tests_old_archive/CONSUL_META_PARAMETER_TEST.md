# Consul Meta Parameter Support Test

**Date:** 2025-12-04  
**Status:** 🔍 **TESTING**

---

## 🎯 **Question**

Does `python-consul` 1.1.0 support the `meta` parameter in `agent.service.register()`?

**Current Approach:**
- We convert `meta` dict to tags because we assume `python-consul` doesn't support `meta`
- This is inefficient and loses structure
- Consul API v1.21.4 definitely supports `meta` parameter

**Hypothesis:**
- `python-consul` 1.1.0 might support `meta` parameter
- If it does, we should use it directly instead of converting to tags
- This would fix the pickle error (no need to serialize complex objects to strings)

---

## 📋 **Test Results**

**Consul Version:** v1.21.4 (supports `meta` parameter)  
**python-consul Version:** 1.1.0

**Test:** Check if `agent.service.register()` accepts `meta` parameter

---

## 💡 **Expected Fix**

If `python-consul` supports `meta`:
1. Use `meta` parameter directly in `agent.service.register()`
2. Remove tag conversion logic
3. Only send simple string key-value pairs in `meta`
4. This should eliminate pickle errors

---

**Status:** Testing python-consul meta parameter support.



