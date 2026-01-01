# MVP Journey Orchestrator Service Investigation

**Date:** 2025-12-04  
**Status:** 🔍 **ROOT CAUSE ANALYSIS IN PROGRESS**

---

## 🎯 **Issue Summary**

**Problem:** Guide Agent endpoints return `503 - MVP Journey Orchestrator not available`

**Root Cause Hypothesis:**
1. MVPJourneyOrchestratorService is not being initialized
2. OR it's initialized but not registered with Curator
3. OR service discovery method mismatch (`get_service` vs `discover_service_by_name`)

---

## 🔍 **Key Findings**

### **Finding 1: Service Discovery Method Mismatch**

**CuratorFoundationService has:**
- ✅ `discover_service_by_name()` - Returns service instance if in cache, metadata if from service discovery
- ❌ `get_service()` - **DOES NOT EXIST**

**BUT:**
- Some code uses `di_container.curator.get_service()` 
- `di_container.curator` might be a different object (not CuratorFoundationService)

**Evidence:**
```python
# solution_composer_service.py line 235
self.mvp_journey_orchestrator = await curator.get_service("MVPJourneyOrchestratorService")

# But CuratorFoundationService doesn't have get_service()!
```

### **Finding 2: Service Registration Pattern**

**How services register:**
1. Services call `register_with_curator()` (from RealmServiceBase)
2. This calls `curator.register_service(service_instance, service_metadata)`
3. Curator stores service in `registered_services[service_name]["service_instance"]`
4. `discover_service_by_name()` checks cache first (line 2442-2447) and returns `service_instance`

**Key Code:**
```python
# curator_foundation_service.py line 2442-2447
if service_name in self.registered_services:
    result = self.registered_services[service_name].get("service_instance")
    return result  # Returns actual service instance!
```

### **Finding 3: MVPJourneyOrchestratorService Registration**

**MVPJourneyOrchestratorService calls `register_with_curator()` in `initialize()`:**
```python
# mvp_journey_orchestrator_service.py line 88
await self.register_with_curator(
    capabilities=[...],
    soa_apis=[...],
    mcp_tools=[...]
)
```

**BUT:** Is it being initialized at all?

---

## 🚨 **Root Cause Hypotheses**

### **Hypothesis 1: Service Not Initialized**
- MVPJourneyOrchestratorService is never created/initialized
- Need to check if it's created in `main.py` or platform startup

### **Hypothesis 2: di_container.curator Doesn't Exist**
- Code uses `di_container.curator.get_service()` 
- But `di_container` might not have `curator` attribute
- Should use `di_container.get_curator_foundation()` or `di_container.get_foundation_service("CuratorFoundationService")`

### **Hypothesis 3: Service Discovery Method Mismatch**
- `discover_service_by_name()` returns metadata from service discovery (Consul/Istio)
- But we need the actual Python service instance
- Service instance is only available if registered in local cache

---

## 🔧 **Investigation Steps**

1. ✅ Check if `di_container.curator` exists
2. ⏳ Check if MVPJourneyOrchestratorService is initialized
3. ⏳ Check if it's registered with Curator
4. ⏳ Check if `discover_service_by_name()` is finding it
5. ⏳ Check if we should use `get_service()` (if it exists) vs `discover_service_by_name()`

---

## 💡 **Potential Solutions**

### **Solution 1: Fix di_container.curator Access**
If `di_container.curator` doesn't exist, we need to:
- Use `di_container.get_curator_foundation()` instead
- OR add `curator` attribute to DI container

### **Solution 2: Ensure Service Initialization**
If service isn't initialized:
- Add initialization in `main.py` or platform startup
- Ensure it's created before JourneyRealmBridge tries to discover it

### **Solution 3: Fix Service Discovery**
If `discover_service_by_name()` isn't finding the service:
- Ensure service is registered in local cache (not just service discovery)
- Check if `registered_services` contains the service

---

## 📋 **Next Steps**

1. Check if `di_container.curator` exists
2. Check if MVPJourneyOrchestratorService is initialized
3. Check if it's registered with Curator
4. Fix service discovery method if needed
5. Test Guide Agent endpoints



