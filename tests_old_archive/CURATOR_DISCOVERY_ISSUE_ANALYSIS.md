# Curator Discovery Issue Analysis

**Date:** 2025-12-04  
**Status:** 🔍 **INVESTIGATING**

---

## 🎯 **Problem Summary**

**User's Concern:**
> "let's investigate the curator issue. I feel like this has shown up in enough places that there might be an issue there."

**Evidence:**
- Multiple "cache-only mode" warnings
- Services not being discovered even though they register
- `discover_service_by_name()` returning None
- Services discovered from service discovery have `service_instance: None`

---

## 🔍 **Key Findings**

### **Finding 1: Service Discovery Not Available**

**Logs Show:**
```
⚠️ Service discovery not available for MVPJourneyOrchestratorService, cache-only mode
⚠️ Service discovery not available for SessionManagerService, cache-only mode
⚠️ Service discovery not available, using local cache only for CityManager
```

**Implication:** Service discovery (Consul) is not available, so Curator falls back to cache-only mode.

### **Finding 2: Services Are Registering**

**Logs Show:**
```
✅ register_service_start completed successfully
✅ register_service_complete completed successfully
✅ Registered service {service_name} with Curator Foundation (service discovery + cache)
```

**But:**
```
⚠️ Failed to register MVPJourneyOrchestratorService with Curator
```

**Implication:** Some services are registering successfully, but others are failing.

### **Finding 3: discover_service_by_name Logic**

**Code Analysis:**
1. Checks cache first: `if service_name in self.registered_services:`
2. Returns `service_instance` from cache: `result = self.registered_services[service_name].get("service_instance")`
3. If not in cache, queries service discovery
4. If found in service discovery, stores in cache with `service_instance: None` (line 2465)

**Problem:** When service discovery is not available, services discovered from service discovery won't have instances!

---

## 🚨 **Root Causes**

### **Root Cause 1: Service Discovery Not Available**

**Issue:** Consul/service discovery is not configured or not running.

**Impact:**
- Services can't register with Consul
- Services fall back to cache-only mode
- Services discovered from service discovery have `service_instance: None`

### **Root Cause 2: Service Instance Not Stored**

**Issue:** When services are discovered from service discovery (not cache), the code stores:
```python
self.registered_services[service_name] = {
    "service_instance": None,  # Not available from service discovery
    "metadata": service_info
}
```

**Impact:** Even if service is in cache, `service_instance` is None, so discovery returns None.

### **Root Cause 3: Registration Failures**

**Issue:** Some services are failing to register with Curator.

**Evidence:**
```
⚠️ Failed to register MVPJourneyOrchestratorService with Curator
```

**Need to investigate:** Why is registration failing?

---

## 📋 **Investigation Steps**

1. ⏳ Check why service discovery is not available
2. ⏳ Check why some services fail to register
3. ⏳ Check if services are actually in cache
4. ⏳ Check if `service_instance` is None in cache
5. ⏳ Check if `discover_service_by_name` is checking cache correctly

---

## 💡 **Diagnostic Approach**

### **Step 1: Check Curator Cache Contents**

Add diagnostic logging to see what's actually in cache:
```python
# In discover_service_by_name
self.logger.info(f"🔍 Curator cache contents: {list(self.registered_services.keys())}")
self.logger.info(f"🔍 Looking for: {service_name}")
if service_name in self.registered_services:
    cache_entry = self.registered_services[service_name]
    self.logger.info(f"🔍 Cache entry: {cache_entry.keys()}")
    self.logger.info(f"🔍 service_instance type: {type(cache_entry.get('service_instance'))}")
    self.logger.info(f"🔍 service_instance is None: {cache_entry.get('service_instance') is None}")
```

### **Step 2: Check Registration Success**

Add diagnostic logging to see if registration succeeds:
```python
# In register_with_curator
result = await curator.register_service(...)
self.logger.info(f"🔍 Registration result: {result}")
if not result.get("success"):
    self.logger.error(f"❌ Registration failed: {result.get('error')}")
```

### **Step 3: Check Service Discovery Availability**

Add diagnostic logging to see if service discovery is available:
```python
# In CuratorFoundationService
if self.service_discovery:
    self.logger.info("✅ Service discovery is available")
else:
    self.logger.warning("⚠️ Service discovery is NOT available - cache-only mode")
```

---

## 🎯 **Key Questions**

1. **Is service discovery configured?** (Check Consul connection)
2. **Are services actually in cache?** (Check `registered_services` dictionary)
3. **Is `service_instance` None in cache?** (Check cache entries)
4. **Why are some registrations failing?** (Check registration errors)
5. **Is `discover_service_by_name` checking cache correctly?** (Check logic)

---

## 📝 **Next Steps**

1. Add diagnostic logging to check Curator cache
2. Check why service discovery is not available
3. Check why some services fail to register
4. Fix the `service_instance: None` issue when discovered from service discovery

---

**Status:** Investigating - multiple potential issues identified.



