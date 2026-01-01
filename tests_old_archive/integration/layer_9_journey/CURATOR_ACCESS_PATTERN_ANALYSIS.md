# Curator Access Pattern Analysis

**Date:** December 2024  
**Status:** 🔍 **Root Cause Analysis Complete**

---

## 🎯 ISSUE IDENTIFIED

**Problem:** Journey services are calling `curator.get_service()` which **does not exist** on Curator Foundation Service.

**Correct Method:** Curator Foundation Service provides `discover_service_by_name()` for service discovery.

---

## 📊 ACTUAL CURATOR METHODS

### **Service Discovery:**
- ✅ `discover_service_by_name(service_name: str)` - **CORRECT** method for discovering services
- ❌ `get_service(service_name: str)` - **DOES NOT EXIST**

### **Agent Discovery:**
- ✅ `get_agent(agent_name: str)` - For discovering agents specifically

---

## 🔍 CODEBASE ANALYSIS

### **✅ CORRECT USAGE:**

1. **Journey Manager** (`journey_manager/modules/initialization.py`):
   ```python
   service_info = await curator.discover_service_by_name(service_name)
   ```

2. **MCP Client Manager** (`agent_sdk/mcp_client_manager.py`):
   ```python
   mcp_server = await self.curator_foundation.discover_service_by_name("SmartCityMCPServer")
   ```

### **❌ INCORRECT USAGE (BUGS):**

1. **Session Journey Orchestrator** (`session_journey_orchestrator_service.py`):
   ```python
   self.frontend_gateway = await curator.get_service("FrontendGatewayService")  # ❌ BUG
   ```

2. **Structured Journey Orchestrator** (`structured_journey_orchestrator_service.py`):
   ```python
   self.frontend_gateway = await curator.get_service("FrontendGatewayService")  # ❌ BUG
   ```

3. **MVP Journey Orchestrator** (`mvp_journey_orchestrator_service.py`):
   ```python
   self.session_orchestrator = await curator.get_service("SessionJourneyOrchestratorService")  # ❌ BUG
   ```

4. **Saga Journey Orchestrator** (`saga_journey_orchestrator_service.py`):
   ```python
   self.structured_orchestrator = await curator.get_service("StructuredJourneyOrchestratorService")  # ❌ BUG
   ```

5. **Journey Analytics Service** (`journey_analytics_service.py`):
   ```python
   self.user_experience = await curator.get_service("UserExperienceService")  # ❌ BUG
   ```

6. **Journey Milestone Tracker** (`journey_milestone_tracker_service.py`):
   ```python
   self.session_manager = await curator.get_service("SessionManagerService")  # ❌ BUG
   ```

---

## 🔧 FIXES REQUIRED

### **Standard Access Pattern:**

All Journey services should use:
```python
curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
if curator:
    service = await curator.discover_service_by_name("ServiceName")
```

**OR** via DI container:
```python
curator = self.di_container.get_foundation_service("CuratorFoundationService")
if curator:
    service = await curator.discover_service_by_name("ServiceName")
```

---

## 📋 FILES TO FIX

1. `backend/journey/services/session_journey_orchestrator_service/session_journey_orchestrator_service.py`
2. `backend/journey/services/structured_journey_orchestrator_service/structured_journey_orchestrator_service.py`
3. `backend/journey/services/mvp_journey_orchestrator_service/mvp_journey_orchestrator_service.py`
4. `backend/journey/services/saga_journey_orchestrator_service/saga_journey_orchestrator_service.py`
5. `backend/journey/services/journey_analytics_service/journey_analytics_service.py`
6. `backend/journey/services/journey_milestone_tracker_service/journey_milestone_tracker_service.py`

---

## ✅ VALIDATION

After fixes, tests should validate:
- ✅ Journey services can discover services via `discover_service_by_name()`
- ✅ Services are correctly discovered and accessible
- ✅ Error handling works when services are not available

---

**Next Steps:**
1. Fix all Journey services to use `discover_service_by_name()`
2. Update tests to validate correct pattern
3. Document standard access pattern for future development



