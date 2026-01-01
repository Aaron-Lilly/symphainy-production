# Security Guard Lazy Instantiation Pattern

**Date:** December 2024  
**Status:** ✅ **PATTERN DOCUMENTED**

---

## 🎯 Question

**Is the City Manager logic in `backend/api/__init__.py` how we "lazy instantiate" Security Guard?**

**Answer: YES - but it's only part of the pattern!**

---

## 📊 How Lazy Instantiation Works

### **Two-Part Pattern:**

1. **`backend/api/__init__.py` (Lines 54-65):**
   - Sets City Manager in auth router (provides bootstrap capability)
   - This is the **setup phase** - makes City Manager available for lazy instantiation

2. **`backend/api/auth_router.py` (Lines 52-109):**
   - `get_security_guard()` function performs the **actual lazy instantiation**
   - Uses City Manager (set in `__init__.py`) to bootstrap Security Guard if needed

---

## 🔍 Complete Flow

### **Step 1: Setup (in `__init__.py`)**

```python
# Set City Manager in auth router
# Auth router needs City Manager to discover Security Guard (fallback if Curator unavailable)
try:
    city_manager = platform_orchestrator.managers.get("city_manager")
    if city_manager:
        set_city_manager(city_manager)  # Stores in global _city_manager variable
        logger.info("✅ City Manager set in auth router")
```

**What this does:**
- Makes City Manager available to `auth_router.py`
- Stores it in global `_city_manager` variable
- Enables bootstrap capability for Security Guard

---

### **Step 2: Lazy Instantiation (in `auth_router.py`)**

```python
async def get_security_guard():
    """
    Get Security Guard service instance via proper service discovery.
    
    Security Guard is a Smart City service, discoverable via:
    1. Curator Foundation (primary - service discovery)
    2. City Manager (fallback - Smart City realm manager)
    """
    global _security_guard_instance, _city_manager
    
    # Use cached instance if available
    if _security_guard_instance:
        return _security_guard_instance
    
    # 1. Try Curator Foundation (primary - service discovery)
    try:
        curator = Curator()
        security_guard = await curator.get_service("SecurityGuardService")
        if security_guard:
            _security_guard_instance = security_guard
            return security_guard
    except Exception as e:
        logger.debug(f"Curator lookup failed: {e}")
    
    # 2. Try City Manager (fallback - Smart City realm manager)
    if _city_manager:  # ← Uses City Manager set in __init__.py
        try:
            # Check if Security Guard is already in City Manager's registry
            if hasattr(_city_manager, 'smart_city_services'):
                service_info = _city_manager.smart_city_services.get("security_guard")
                if service_info and service_info.get("instance"):
                    security_guard = service_info["instance"]
                    _security_guard_instance = security_guard
                    return security_guard
            
            # ⭐ BOOTSTRAP: Initialize Security Guard via City Manager if needed
            if hasattr(_city_manager, 'realm_orchestration_module'):
                result = await _city_manager.realm_orchestration_module.orchestrate_realm_startup(
                    services=["security_guard"]  # ← Lazy instantiation happens here!
                )
                if result and result.get("success"):
                    service_info = _city_manager.smart_city_services.get("security_guard")
                    if service_info and service_info.get("instance"):
                        security_guard = service_info["instance"]
                        _security_guard_instance = security_guard
                        logger.info("✅ Security Guard bootstrapped via City Manager")
                        return security_guard
        except Exception as e:
            logger.debug(f"City Manager lookup failed: {e}")
    
    logger.error("❌ Security Guard service not available")
    return None
```

**What this does:**
- First checks cached instance (fast path)
- Tries Curator Foundation (primary discovery method)
- **Falls back to City Manager** (set in `__init__.py`)
- **Bootstraps Security Guard** via `orchestrate_realm_startup()` if not already initialized
- Caches the instance for future requests

---

## ✅ Why This Pattern Works

### **1. Lazy Initialization:**
- Security Guard is **not initialized** during platform startup
- It's only initialized **when first needed** (first auth request)
- Reduces startup time

### **2. Bootstrap Capability:**
- City Manager can **orchestrate realm startup** for Smart City services
- `orchestrate_realm_startup(services=["security_guard"])` initializes Security Guard on-demand
- City Manager prevents double instantiation (checks if already initialized)

### **3. Fallback Chain:**
```
1. Cached instance (fastest)
   ↓ (if not cached)
2. Curator Foundation (primary discovery)
   ↓ (if not found)
3. City Manager (fallback bootstrap)
   ↓ (if City Manager available)
4. Bootstrap Security Guard via orchestrate_realm_startup()
```

---

## 🎯 Key Points

1. **`__init__.py` provides the capability:**
   - Sets City Manager in auth router
   - Makes bootstrap possible
   - Non-blocking (won't fail startup if City Manager unavailable)

2. **`auth_router.py` performs the lazy instantiation:**
   - `get_security_guard()` is called on first auth request
   - Uses City Manager (set in `__init__.py`) to bootstrap if needed
   - Caches instance for subsequent requests

3. **This is proper lazy hydration:**
   - Service not initialized until needed
   - Bootstrap happens on-demand
   - No double instantiation (City Manager checks first)

---

## 📍 Files Involved

1. **`backend/api/__init__.py` (Lines 54-65):**
   - Sets City Manager in auth router
   - Provides bootstrap capability

2. **`backend/api/auth_router.py` (Lines 52-109):**
   - `get_security_guard()` function
   - Performs actual lazy instantiation
   - Uses City Manager to bootstrap if needed

---

## 🔍 Example Flow

**First Auth Request:**
```
1. User calls POST /api/auth/login
2. auth_router.py calls get_security_guard()
3. No cached instance → Try Curator → Not found
4. Try City Manager (set in __init__.py) → Available
5. Check City Manager registry → Security Guard not initialized
6. Call orchestrate_realm_startup(services=["security_guard"])
7. Security Guard initializes
8. Cache instance in _security_guard_instance
9. Return Security Guard
10. Process login request
```

**Subsequent Auth Requests:**
```
1. User calls POST /api/auth/login
2. auth_router.py calls get_security_guard()
3. Cached instance exists → Return immediately (fast path)
4. Process login request
```

---

## ✅ Conclusion

**Yes, the City Manager logic in `__init__.py` is part of the lazy instantiation pattern!**

- **`__init__.py`**: Sets up City Manager (provides bootstrap capability)
- **`auth_router.py`**: Uses City Manager to bootstrap Security Guard on-demand

This is the **proper lazy hydration pattern** - services initialize when needed, not during platform startup.

---

**Last Updated:** December 2024  
**Status:** Pattern Documented




