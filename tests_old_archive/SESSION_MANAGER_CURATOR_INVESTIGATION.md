# Session Manager & Curator Investigation

**Date:** 2025-12-04  
**Status:** 🔍 **INVESTIGATING ROOT CAUSE**

---

## 🎯 **Issue Summary**

**Problem:** Guide Agent endpoint returns `"Session Manager not available"`

**User's Concern:** Session Manager should have been initialized by City Manager on startup (along with all Smart City services), and there might be a silent issue with Curator.

---

## 🔍 **Key Findings**

### **Finding 1: SessionManagerService is NOT a Smart City Service**

**Location:** `foundations/experience_foundation/services/session_manager_service/`

**Realm:** Experience (not Smart City)

**Implication:** City Manager does NOT initialize SessionManagerService. It's an Experience realm service.

---

### **Finding 2: ExperienceFoundationBridge Not Initializing Services**

**Logs Show:**
```
⚠️ Experience Foundation not available - bridge will have limited functionality
```

**Problem:** ExperienceFoundationBridge is not finding/initializing Experience Foundation, so it can't create SessionManagerService.

---

### **Finding 3: Experience Foundation is Initialized (But Bridge Can't Find It)**

**Logs Show:**
```
ExperienceFoundationService.performance_monitoring - INFO - 🏗️ Experience Foundation Service initialized
```

**But:**
```
ExperienceFoundationBridge - WARNING - ⚠️ Experience Foundation not available
```

**Implication:** Experience Foundation exists, but ExperienceFoundationBridge can't access it.

---

## 🚨 **Potential Root Causes**

### **Root Cause 1: Experience Foundation Not in DI Container**

**Hypothesis:** ExperienceFoundationBridge tries to get Experience Foundation from DI Container, but it's not registered.

**Check:** How does ExperienceFoundationBridge get Experience Foundation?

### **Root Cause 2: Curator Registration Issue**

**Hypothesis:** Services are registering with Curator, but:
- Registration is failing silently
- Services aren't being stored in `registered_services` cache
- Discovery is failing because cache is empty

**Check:** Are services actually in Curator's `registered_services` dictionary?

### **Root Cause 3: Service Discovery Not Working**

**Hypothesis:** Curator's `discover_service_by_name()` is:
- Not checking cache correctly
- Not querying service discovery correctly
- Returning None even when services are registered

**Check:** What does `discover_service_by_name()` actually return?

---

## 📋 **Investigation Steps**

1. ✅ Check if SessionManagerService is a Smart City service (NO - it's Experience)
2. ⏳ Check how ExperienceFoundationBridge gets Experience Foundation
3. ⏳ Check if Experience Foundation is in DI Container
4. ⏳ Check if SessionManagerService is being created/initialized
5. ⏳ Check if services are actually in Curator's `registered_services` cache
6. ⏳ Check if `discover_service_by_name()` is working correctly

---

## 💡 **Potential Solutions**

### **Solution 1: Fix ExperienceFoundationBridge**

If Experience Foundation is not accessible:
- Ensure Experience Foundation is initialized before ExperienceFoundationBridge
- Ensure Experience Foundation is registered in DI Container
- Fix ExperienceFoundationBridge to properly access Experience Foundation

### **Solution 2: Lazy-Initialize SessionManagerService in JourneyRealmBridge**

Similar to MVP Journey Orchestrator:
- If SessionManagerService not found, create and initialize it
- Follows the same pattern for non-Smart City realms

### **Solution 3: Fix Curator Registration/Discovery**

If Curator is the issue:
- Ensure services are actually being registered
- Ensure `registered_services` cache is populated
- Fix `discover_service_by_name()` if it's not working

---

## 📝 **Next Steps**

1. Check how ExperienceFoundationBridge accesses Experience Foundation
2. Check if Experience Foundation is in DI Container
3. Check Curator's `registered_services` to see what's actually registered
4. Determine if this is a Curator issue or an Experience Foundation access issue

---

**Status:** Investigating root cause - may be Curator registration/discovery issue or Experience Foundation access issue.



