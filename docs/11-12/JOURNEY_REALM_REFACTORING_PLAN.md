# Journey Realm - Comprehensive Refactoring Plan

**Date:** December 2024  
**Status:** 📋 **REFACTORING PLAN**  
**Goal:** Refactor all Journey realm services to use utility patterns and Phase 2 Curator registration

---

## 🎯 Overview

The Journey realm orchestrates multi-step user journeys by composing Experience services. This plan outlines the refactoring of all Journey realm components to align with the enhanced patterns established in Business Enablement.

---

## 📊 Journey Realm Structure

### Service Types

1. **Manager Service** (1 service)
   - `JourneyManagerService` - Coordinates all journey orchestrators

2. **Orchestrator Services** (3 services)
   - `StructuredJourneyOrchestratorService` - Linear, guided flows
   - `SessionJourneyOrchestratorService` - Free-form, user-driven navigation
   - `MVPJourneyOrchestratorService` - MVP-specific 4-pillar navigation

3. **Enabling Services** (2 services)
   - `JourneyAnalyticsService` - Journey metrics and optimization
   - `JourneyMilestoneTrackerService` - Milestone tracking and progress

4. **MCP Server** (1 module)
   - `journey_manager/modules/soa_mcp.py` - SOA/MCP integration

**Total Components:** 7

---

## 🔍 Current State Analysis

### ✅ What's Already Good

1. **Base Classes:**
   - All services extend appropriate base classes (`RealmServiceBase` or `ManagerServiceBase`)
   - Proper inheritance hierarchy

2. **Service Discovery:**
   - Services discover Experience services via Curator
   - Smart City services accessed via base class methods

3. **Micro-Modular Architecture:**
   - Journey Manager uses micro-modules (similar to Delivery Manager)
   - Good separation of concerns

### ❌ What Needs Refactoring

1. **Utility Usage Pattern:**
   - ❌ Missing `log_operation_with_telemetry()` calls
   - ❌ Missing `record_health_metric()` calls
   - ❌ Missing `handle_error_with_audit()` calls
   - ❌ No security/tenant validation in user-facing methods

2. **Curator Registration:**
   - ❌ Using old-style `register_with_curator()` with simple lists
   - ❌ Missing Phase 2 `CapabilityDefinition` structure
   - ❌ Missing SOA API contracts
   - ❌ Missing semantic mappings

3. **User Context:**
   - ❌ No `user_context` parameters in user-facing methods
   - ❌ No security/tenant validation

4. **Error Handling:**
   - ❌ Basic try/except without audit logging
   - ❌ No structured error handling pattern

---

## 📋 Refactoring Plan by Component

### 1. Journey Manager Service

**File:** `backend/journey/services/journey_manager/journey_manager_service.py`

**Service Type:** Manager Service (extends `ManagerServiceBase`)

**Current State:**
- ✅ Extends `ManagerServiceBase`
- ✅ Uses micro-modules
- ❌ Missing utility methods in `initialize()`
- ❌ Missing Phase 2 Curator registration
- ❌ Missing `user_context` in user-facing methods

**Refactoring Tasks:**

1. **Update `initialize()` method:**
   ```python
   async def initialize(self) -> bool:
       # Start telemetry tracking
       await self.log_operation_with_telemetry("journey_manager_initialize_start", success=True)
       
       try:
           # ... initialization logic ...
           
           # Record health metric
           await self.record_health_metric("journey_manager_initialized", 1.0, {})
           
           # End telemetry tracking
           await self.log_operation_with_telemetry("journey_manager_initialize_complete", success=True)
           return True
       except Exception as e:
           await self.handle_error_with_audit(e, "journey_manager_initialize")
           await self.log_operation_with_telemetry("journey_manager_initialize_complete", success=False)
           return False
   ```

2. **Update SOA/MCP module (`modules/soa_mcp.py`):**
   - Replace old `register_service()` with Phase 2 `register_with_curator()`
   - Use `CapabilityDefinition` structure with contracts
   - Include SOA API contracts with handler references
   - Include MCP tool contracts
   - Include semantic mappings

3. **Add `user_context` to user-facing methods:**
   - `design_journey(journey_request, user_context)`
   - `create_roadmap(roadmap_request, user_context)`
   - `track_milestones(tracking_request, user_context)`
   - `orchestrate_experience(experience_context, user_context)`

4. **Update module methods:**
   - Add utility methods to `journey_design.py`
   - Add utility methods to `experience_orchestration.py`
   - Add utility methods to `roadmap_management.py`

**Reference:** `backend/business_enablement/delivery_manager/delivery_manager_service.py`

---

### 2. Structured Journey Orchestrator Service

**File:** `backend/journey/services/structured_journey_orchestrator_service/structured_journey_orchestrator_service.py`

**Service Type:** Orchestrator Service (extends `RealmServiceBase`)

**Current State:**
- ✅ Extends `RealmServiceBase`
- ✅ Discovers Experience services via Curator
- ❌ Old-style Curator registration (simple lists)
- ❌ Missing utility methods
- ❌ Missing `user_context` parameters

**Refactoring Tasks:**

1. **Update `initialize()` method:**
   - Add `log_operation_with_telemetry()` for start/complete
   - Add `record_health_metric()` for success
   - Add `handle_error_with_audit()` for errors

2. **Update Curator registration to Phase 2:**
   ```python
   await self.register_with_curator(
       capabilities=[
           {
               "name": "journey_orchestration",
               "protocol": "StructuredJourneyOrchestratorProtocol",
               "description": "Design and execute structured journeys",
               "contracts": {
                   "soa_api": {
                       "api_name": "design_journey",
                       "endpoint": "/api/v1/journey/structured/design",
                       "method": "POST",
                       "handler": self.design_journey,
                       "metadata": {
                           "description": "Design a structured journey",
                           "parameters": ["journey_type", "requirements", "user_context"]
                       }
                   }
               },
               "semantic_mapping": {
                   "domain_capability": "journey.design_structured",
                   "semantic_api": "/api/v1/journey/structured/design",
                   "user_journey": "design_structured_journey"
               }
           },
           # ... more capabilities
       ],
       soa_apis=["design_journey", "execute_journey", ...],
       mcp_tools=[]
   )
   ```

3. **Add `user_context` to all SOA API methods:**
   - `design_journey(journey_type, requirements, user_context)`
   - `get_journey_template(template_name, user_context)`
   - `customize_journey(journey_id, customizations, user_context)`
   - `execute_journey(journey_id, user_id, context, user_context)`
   - `advance_journey_step(journey_id, user_id, step_result, user_context)`
   - `get_journey_status(journey_id, user_id, user_context)`
   - `pause_journey(journey_id, user_id, user_context)`
   - `resume_journey(journey_id, user_id, user_context)`
   - `cancel_journey(journey_id, user_id, user_context)`
   - `get_available_journey_types(user_context)`

4. **Add utility methods to each SOA API method:**
   - Security validation
   - Tenant validation
   - Telemetry tracking (start/complete)
   - Health metrics
   - Error handling with audit

**Reference:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/insights_orchestrator.py`

---

### 3. Session Journey Orchestrator Service

**File:** `backend/journey/services/session_journey_orchestrator_service/session_journey_orchestrator_service.py`

**Service Type:** Orchestrator Service (extends `RealmServiceBase`)

**Current State:**
- ✅ Extends `RealmServiceBase`
- ✅ Free-form navigation pattern
- ❌ Old-style Curator registration
- ❌ Missing utility methods
- ❌ Missing `user_context` parameters

**Refactoring Tasks:**

1. **Same as Structured Journey Orchestrator:**
   - Update `initialize()` with utility methods
   - Update Curator registration to Phase 2
   - Add `user_context` to all SOA API methods
   - Add utility methods to each SOA API method

2. **SOA API methods to update:**
   - `start_session_journey(journey_type, user_id, context, user_context)`
   - `navigate_to_area(journey_id, area_name, user_context)`
   - `update_area_state(journey_id, area_name, state, user_context)`
   - `check_area_completion(journey_id, area_name, user_context)`
   - `get_session_progress(journey_id, user_context)`
   - `get_navigation_history(journey_id, user_context)`
   - `reset_area(journey_id, area_name, user_context)`
   - `complete_session_journey(journey_id, user_context)`
   - `get_session_status(journey_id, user_context)`
   - `get_available_areas(journey_id, user_context)`

**Reference:** Same as Structured Journey Orchestrator

---

### 4. MVP Journey Orchestrator Service

**File:** `backend/journey/services/mvp_journey_orchestrator_service/mvp_journey_orchestrator_service.py`

**Service Type:** Orchestrator Service (extends `RealmServiceBase`)

**Current State:**
- ✅ Extends `RealmServiceBase`
- ✅ Composes Session Journey Orchestrator
- ✅ Pre-configured for 4 MVP pillars
- ❌ Old-style Curator registration
- ❌ Missing utility methods
- ❌ Missing `user_context` parameters

**Refactoring Tasks:**

1. **Same pattern as other orchestrators:**
   - Update `initialize()` with utility methods
   - Update Curator registration to Phase 2
   - Add `user_context` to all SOA API methods
   - Add utility methods to each SOA API method

2. **SOA API methods to update:**
   - `start_mvp_journey(user_id, context, user_context)`
   - `navigate_to_pillar(journey_id, pillar_name, user_context)`
   - `update_pillar_progress(journey_id, pillar_name, progress, user_context)`
   - `get_recommended_next_pillar(journey_id, user_context)`
   - `check_mvp_completion(journey_id, user_context)`
   - `get_mvp_status(journey_id, user_context)`
   - `get_pillar_progress(journey_id, pillar_name, user_context)`
   - `get_mvp_summary(journey_id, user_context)`

**Reference:** Same as Structured Journey Orchestrator

---

### 5. Journey Analytics Service

**File:** `backend/journey/services/journey_analytics_service/journey_analytics_service.py`

**Service Type:** Enabling Service (extends `RealmServiceBase`)

**Current State:**
- ✅ Extends `RealmServiceBase`
- ✅ Discovers Experience services via Curator
- ❌ Old-style Curator registration
- ❌ Missing utility methods
- ❌ Missing `user_context` parameters

**Refactoring Tasks:**

1. **Update `initialize()` method:**
   - Add utility methods (same pattern as orchestrators)

2. **Update Curator registration to Phase 2:**
   - Use `CapabilityDefinition` structure
   - Include SOA API contracts

3. **Add `user_context` to all SOA API methods:**
   - `calculate_journey_metrics(journey_id, user_context)`
   - `get_completion_rate(journey_id, user_context)`
   - `get_average_duration(journey_id, user_context)`
   - `identify_drop_off_points(journey_id, user_context)`
   - `analyze_journey_performance(journey_id, user_context)`
   - `get_optimization_recommendations(journey_id, user_context)`
   - `compare_journeys(journey_ids, user_context)`
   - `get_journey_benchmarks(journey_type, user_context)`

4. **Add utility methods to each SOA API method:**
   - Security validation
   - Tenant validation
   - Telemetry tracking
   - Health metrics
   - Error handling

**Reference:** `backend/business_enablement/enabling_services/data_analyzer_service/data_analyzer_service.py`

---

### 6. Journey Milestone Tracker Service

**File:** `backend/journey/services/journey_milestone_tracker_service/journey_milestone_tracker_service.py`

**Service Type:** Enabling Service (extends `RealmServiceBase`)

**Current State:**
- ✅ Extends `RealmServiceBase`
- ✅ Tracks journey milestones
- ❌ Old-style Curator registration
- ❌ Missing utility methods
- ❌ Missing `user_context` parameters

**Refactoring Tasks:**

1. **Same pattern as Journey Analytics Service:**
   - Update `initialize()` with utility methods
   - Update Curator registration to Phase 2
   - Add `user_context` to all SOA API methods
   - Add utility methods to each SOA API method

2. **SOA API methods to update:**
   - `track_milestone(journey_id, milestone_id, status, user_context)`
   - `get_milestone_status(journey_id, milestone_id, user_context)`
   - `get_journey_milestones(journey_id, user_context)`
   - `update_milestone_progress(journey_id, milestone_id, progress, user_context)`
   - `get_milestone_history(journey_id, milestone_id, user_context)`
   - `reset_milestone(journey_id, milestone_id, user_context)`
   - `get_completed_milestones(journey_id, user_context)`
   - `get_pending_milestones(journey_id, user_context)`

**Reference:** Same as Journey Analytics Service

---

### 7. Journey Manager MCP Server

**File:** `backend/journey/services/journey_manager/modules/soa_mcp.py`

**Current State:**
- ✅ Defines SOA APIs and MCP tools
- ❌ Old-style `register_service()` pattern
- ❌ Missing Phase 2 `CapabilityDefinition` structure

**Refactoring Tasks:**

1. **Update `register_journey_manager_capabilities()` method:**
   - Replace `curator.register_service()` with `self.service.register_with_curator()`
   - Use Phase 2 `CapabilityDefinition` structure
   - Include SOA API contracts with handler references
   - Include MCP tool contracts
   - Include semantic mappings

**Reference:** `backend/business_enablement/delivery_manager/modules/soa_mcp.py`

---

## 🎯 Refactoring Pattern Summary

### Utility Usage Pattern (All Services)

```python
# In initialize():
await self.log_operation_with_telemetry("service_initialize_start", success=True)
try:
    # ... initialization logic ...
    await self.record_health_metric("service_initialized", 1.0, {})
    await self.log_operation_with_telemetry("service_initialize_complete", success=True)
    return True
except Exception as e:
    await self.handle_error_with_audit(e, "service_initialize")
    await self.log_operation_with_telemetry("service_initialize_complete", success=False)
    return False

# In user-facing methods:
async def my_method(self, param1, user_context: Optional[Dict[str, Any]] = None):
    # Start telemetry tracking
    await self.log_operation_with_telemetry("my_method_start", success=True)
    
    # Security and Tenant Validation
    if user_context:
        if not await self.security.check_permissions(user_context, "my_method", "execute"):
            await self.handle_error_with_audit(ValueError("Permission denied"), "my_method")
            await self.record_health_metric("my_method_access_denied", 1.0, {})
            await self.log_operation_with_telemetry("my_method_complete", success=False)
            return {"success": False, "error": "Permission denied"}
        
        tenant_id = user_context.get("tenant_id")
        if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
            await self.handle_error_with_audit(ValueError("Tenant access denied"), "my_method")
            await self.record_health_metric("my_method_tenant_denied", 1.0, {})
            await self.log_operation_with_telemetry("my_method_complete", success=False)
            return {"success": False, "error": "Tenant access denied"}
    
    try:
        # Business logic
        result = ...
        
        # Record health metric (success)
        await self.record_health_metric("my_method_success", 1.0, {})
        
        # End telemetry tracking
        await self.log_operation_with_telemetry("my_method_complete", success=True)
        return result
    except Exception as e:
        # Error handling with audit
        await self.handle_error_with_audit(e, "my_method")
        
        # Record health metric (failure)
        await self.record_health_metric("my_method_failed", 1.0, {"error": type(e).__name__})
        
        # End telemetry tracking with failure
        await self.log_operation_with_telemetry("my_method_complete", success=False, details={"error": str(e)})
        raise
```

### Phase 2 Curator Registration

```python
await self.register_with_curator(
    capabilities=[
        {
            "name": "capability_name",
            "protocol": "ServiceProtocol",
            "description": "Description of capability",
            "contracts": {
                "soa_api": {
                    "api_name": "method_name",
                    "endpoint": "/api/v1/journey/...",
                    "method": "POST",
                    "handler": self.method_name,
                    "metadata": {
                        "description": "Description",
                        "parameters": ["param1", "param2", "user_context"]
                    }
                },
                "mcp_tool": {  # Optional
                    "tool_name": "method_name_tool",
                    "tool_definition": {
                        "name": "method_name_tool",
                        "description": "Description",
                        "input_schema": {...}
                    }
                }
            },
            "semantic_mapping": {
                "domain_capability": "journey.capability_name",
                "semantic_api": "/api/v1/journey/...",
                "user_journey": "capability_name"
            }
        }
    ],
    soa_apis=["method1", "method2", ...],
    mcp_tools=["tool1", "tool2", ...]  # Optional
)
```

---

## 📊 Progress Tracking

| Component | Type | Status | Priority |
|-----------|------|--------|----------|
| Journey Manager Service | Manager | ⏳ Pending | High |
| Structured Journey Orchestrator | Orchestrator | ⏳ Pending | High |
| Session Journey Orchestrator | Orchestrator | ⏳ Pending | High |
| MVP Journey Orchestrator | Orchestrator | ⏳ Pending | High |
| Journey Analytics Service | Enabling | ⏳ Pending | Medium |
| Journey Milestone Tracker | Enabling | ⏳ Pending | Medium |
| Journey Manager MCP Server | MCP | ⏳ Pending | Medium |
| **TOTAL** | **7** | **0/7** | **0%** |

---

## 🚀 Recommended Order

1. **Enabling Services** (2 services)
   - Journey Analytics Service
   - Journey Milestone Tracker Service
   - **Why:** Similar to Business Enablement enabling services, quick to complete

2. **Orchestrator Services** (3 services)
   - Structured Journey Orchestrator
   - Session Journey Orchestrator
   - MVP Journey Orchestrator
   - **Why:** Similar pattern, can be done in parallel

3. **Journey Manager Service** (1 service)
   - Journey Manager Service
   - **Why:** Coordinates orchestrators, should be done after orchestrators

4. **MCP Server** (1 module)
   - Journey Manager MCP Server
   - **Why:** Depends on Journey Manager Service

---

## ✅ Success Criteria

### For Each Component:

1. ✅ Full utility usage (telemetry, error handling, security, tenant, health)
2. ✅ Phase 2 Curator registration with `CapabilityDefinition` structure
3. ✅ `user_context` parameter in all user-facing methods
4. ✅ Security and tenant validation in all user-facing methods
5. ✅ Functional equivalence (services still work)
6. ✅ Tests passing

### End-to-End:

1. ✅ All Journey realm services refactored
2. ✅ All services registered with Curator (Phase 2)
3. ✅ All services use utilities consistently
4. ✅ Platform integration works
5. ✅ Tests passing

---

## 📝 Notes

- **Reference Implementations:**
  - Manager Service: `backend/business_enablement/delivery_manager/delivery_manager_service.py`
  - Orchestrator Services: `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/insights_orchestrator.py`
  - Enabling Services: `backend/business_enablement/enabling_services/data_analyzer_service/data_analyzer_service.py`
  - MCP Server: `backend/business_enablement/delivery_manager/modules/soa_mcp.py`

- **Pattern Consistency:** Follow the same patterns established in Business Enablement realm

- **Testing:** Create tests similar to Business Enablement tests

---

**Status:** 📋 **REFACTORING PLAN**  
**Progress:** 0/7 components complete (0%)  
**Remaining:** 7 components (100%)



