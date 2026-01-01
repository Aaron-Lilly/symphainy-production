# Agentic Foundation Refactoring Plan V2 - Option B

**Date:** November 19, 2025  
**Status:** 🚧 **In Progress**  
**Pattern:** Utilities via AgenticFoundationService (Wrapping Pattern)

---

## 📊 Current Status

**Total Methods:** 204  
**Compliant Methods:** 16 (8%)  
**Remaining Violations:** 188

### Violations by Category
- **Error Handling:** 258 violations
- **Telemetry:** 126 violations
- **Security:** 32 violations
- **Tenant:** 40 violations

---

## 🎯 Pattern: "Utilities via AgenticFoundationService" (Option B)

### Rationale

Since infrastructure enablement services are **agent-specific** and will be **coupled with AgenticFoundationService**, we can:

1. **AgenticFoundationService wraps all calls** with utilities (telemetry, error handling, security, tenant)
2. **Infrastructure enablement services** focus on business logic (minimal utilities)
3. **MCPClientManager** gets utilities via mixins (it's in agent_sdk/, used directly by agents)

This approach:
- ✅ Reduces work from 188 methods to ~30-40 methods
- ✅ Maintains reasonable coupling (services are agent-specific anyway)
- ✅ Ensures utilities are consistently applied
- ✅ Makes services easier to maintain

---

## 🏗️ Architecture

### Components to Fix:

1. **Main Foundation Service** (`AgenticFoundationService`)
   - ✅ Some methods already have utilities
   - ⚠️ Need to add utilities to remaining methods
   - ⚠️ Need to wrap infrastructure enablement service calls with utilities
   - ⚠️ Need to integrate infrastructure enablement services

2. **Infrastructure Enablement Services** (`infrastructure_enablement/`)
   - ⚠️ Add basic error handling (minimal)
   - ⚠️ No need for full utility compliance (AgenticFoundationService wraps calls)
   - Services:
     - `ToolRegistryService` - ✅ Already has mixins (can keep or simplify)
     - `ToolDiscoveryService` - ✅ Already has mixins (can keep or simplify)
     - `HealthService` - ⚠️ Add mixins, basic error handling
     - `PolicyService` - ⚠️ Add mixins, basic error handling
     - `SessionService` - ⚠️ Add mixins, basic error handling
     - `AGUIOutputFormatter` - ✅ Already instantiated
     - `AGUISchemaRegistry` - ✅ Already instantiated

3. **MCPClientManager** (`agent_sdk/mcp_client_manager.py`)
   - ⚠️ Add utility mixins (UtilityAccessMixin, PerformanceMonitoringMixin)
   - ⚠️ Replace direct utility access with mixin methods
   - ⚠️ Add utilities to all methods (it's used directly by agents)

4. **Manager Service** (`AgenticManagerService`)
   - ⚠️ Add utilities to all methods
   - Inherits from ManagerServiceBase (has mixins)

5. **SDK Components** (`agent_sdk/`)
   - ✅ No changes needed (base classes get utilities from mixins or DI container)

---

## 🔧 Implementation Steps

### Step 1: Integrate Infrastructure Enablement Services

Add to `AgenticFoundationService._initialize_agentic_services()`:

```python
# Initialize infrastructure enablement services
if self.public_works_foundation:
    # Tool Registry Service
    tool_storage = self.public_works_foundation.get_tool_storage_abstraction()
    self.tool_registry_service = ToolRegistryService(
        tool_storage_abstraction=tool_storage,
        curator_foundation=self.curator_foundation,
        di_container=self.di_container
    )
    
    # Tool Discovery Service
    self.tool_discovery_service = ToolDiscoveryService(
        tool_registry_service=self.tool_registry_service,
        curator_foundation=self.curator_foundation,
        di_container=self.di_container
    )
    
    # Health Service
    health_abstraction = self.public_works_foundation.get_health_abstraction()
    health_composition = self.public_works_foundation.get_health_composition_service()
    self.health_service = HealthService(
        health_abstraction=health_abstraction,
        health_composition_service=health_composition,
        curator_foundation=self.curator_foundation,
        di_container=self.di_container
    )
    
    # Policy Service
    policy_abstraction = self.public_works_foundation.get_policy_abstraction()
    policy_composition = self.public_works_foundation.get_policy_composition_service()
    self.policy_service = PolicyService(
        policy_abstraction=policy_abstraction,
        policy_composition_service=policy_composition,
        curator_foundation=self.curator_foundation,
        di_container=self.di_container
    )
    
    # Session Service
    session_abstraction = self.public_works_foundation.get_session_abstraction()
    session_composition = self.public_works_foundation.get_session_composition_service()
    self.session_service = SessionService(
        session_abstraction=session_abstraction,
        session_composition_service=session_composition,
        curator_foundation=self.curator_foundation,
        di_container=self.di_container
    )
```

### Step 2: Add Wrapper Methods in AgenticFoundationService

For each infrastructure enablement service, add wrapper methods that:
1. Add telemetry tracking
2. Add security/tenant validation
3. Call the service method
4. Add health metrics
5. Handle errors with audit

Example:
```python
async def register_agent_tool(self, tool_definition: ToolDefinition, 
                             agent_id: str = None,
                             user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Register a tool for an agent (wraps ToolRegistryService)."""
    try:
        # Start telemetry tracking
        await self.log_operation_with_telemetry("register_agent_tool_start", success=True, 
                                                details={"tool_name": tool_definition.name, "agent_id": agent_id})
        
        # Security validation
        if user_context:
            security = self.get_security()
            if security:
                if not await security.check_permissions(user_context, "tool_registry", "write"):
                    await self.record_health_metric("register_agent_tool_access_denied", 1.0, {"tool_name": tool_definition.name})
                    await self.log_operation_with_telemetry("register_agent_tool_complete", success=False)
                    return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
        
        # Tenant validation
        tenant_context = self._extract_tenant_context(user_context)
        if tenant_context:
            tenant = self.get_tenant()
            if tenant:
                tenant_id = tenant_context.get("tenant_id")
                if tenant_id:
                    if not await tenant.validate_tenant_access(tenant_id):
                        await self.record_health_metric("register_agent_tool_tenant_denied", 1.0, {"tool_name": tool_definition.name})
                        await self.log_operation_with_telemetry("register_agent_tool_complete", success=False)
                        return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
        
        # Call infrastructure enablement service
        if not self.tool_registry_service:
            return {"success": False, "error": "Tool Registry Service not available"}
        
        result = await self.tool_registry_service.register_tool(
            tool_definition=tool_definition,
            agent_id=agent_id,
            tenant_context=tenant_context
        )
        
        # Record success metric
        await self.record_health_metric("register_agent_tool_success", 1.0, {"tool_name": tool_definition.name})
        
        # End telemetry tracking
        await self.log_operation_with_telemetry("register_agent_tool_complete", success=True, 
                                                details={"tool_name": tool_definition.name})
        
        return result
        
    except Exception as e:
        # Use enhanced error handling with audit
        await self.handle_error_with_audit(e, "register_agent_tool", 
                                          details={"tool_name": tool_definition.name, "agent_id": agent_id})
        raise
```

### Step 3: Fix MCPClientManager

Add utility mixins to MCPClientManager:

```python
from bases.mixins.utility_access_mixin import UtilityAccessMixin
from bases.mixins.performance_monitoring_mixin import PerformanceMonitoringMixin

class MCPClientManager(UtilityAccessMixin, PerformanceMonitoringMixin):
    def __init__(self, foundation_services: DIContainerService,
                 agentic_foundation: 'AgenticFoundationService'):
        # Initialize utility mixins
        self._init_utility_access(foundation_services)
        self._init_performance_monitoring(foundation_services)
        
        # ... rest of initialization
```

Then replace all exception handlers to use `handle_error_with_audit` and add telemetry/health metrics.

### Step 4: Fix Remaining AgenticFoundationService Methods

Add utilities to all methods that don't have them yet.

---

## 📋 Services Status

### ✅ Completed
- `get_tenant_abstraction()` - Added utilities
- `get_mcp_abstraction()` - Added utilities
- `get_llm_abstraction()` - Added utilities
- `get_tool_abstraction()` - Added utilities
- `get_agentic_capabilities()` - Added utilities
- `ToolRegistryService` - Has mixins (can keep or simplify)
- `ToolDiscoveryService` - Has mixins (can keep or simplify)

### 🚧 In Progress
- `AgenticFoundationService` - Need to add wrapper methods and integrate services
- `MCPClientManager` - Need to add mixins and utilities
- Infrastructure enablement services - Need basic mixins

### ⚠️ Pending
- Infrastructure enablement service integration
- Wrapper methods in AgenticFoundationService
- MCPClientManager utilities
- Remaining AgenticFoundationService methods
- AgenticManagerService methods

---

## 🎯 Next Steps

1. **Integrate infrastructure enablement services** into AgenticFoundationService
2. **Add wrapper methods** in AgenticFoundationService for each service
3. **Fix MCPClientManager** - add mixins and utilities
4. **Fix remaining AgenticFoundationService methods**
5. **Fix AgenticManagerService methods**
6. **Validate 100% compliance**

---

## 📝 Pattern Template for Wrapper Methods

```python
async def wrapper_method(self, ..., user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Wrapper method that adds utilities to infrastructure enablement service calls."""
    try:
        # Start telemetry tracking
        await self.log_operation_with_telemetry("wrapper_method_start", success=True, details={...})
        
        # Security validation (if user_context provided)
        if user_context:
            security = self.get_security()
            if security:
                if not await security.check_permissions(user_context, "resource", "action"):
                    await self.record_health_metric("wrapper_method_access_denied", 1.0, {...})
                    await self.log_operation_with_telemetry("wrapper_method_complete", success=False)
                    return {"success": False, "error": "Access denied"}
        
        # Tenant validation (if user_context provided)
        tenant_context = self._extract_tenant_context(user_context)
        if tenant_context:
            tenant = self.get_tenant()
            if tenant:
                tenant_id = tenant_context.get("tenant_id")
                if tenant_id:
                    if not await tenant.validate_tenant_access(tenant_id):
                        await self.record_health_metric("wrapper_method_tenant_denied", 1.0, {...})
                        await self.log_operation_with_telemetry("wrapper_method_complete", success=False)
                        return {"success": False, "error": "Tenant access denied"}
        
        # Call infrastructure enablement service
        if not self.infrastructure_service:
            return {"success": False, "error": "Service not available"}
        
        result = await self.infrastructure_service.method(...)
        
        # Record success metric
        await self.record_health_metric("wrapper_method_success", 1.0, {...})
        
        # End telemetry tracking
        await self.log_operation_with_telemetry("wrapper_method_complete", success=True, details={...})
        
        return result
        
    except Exception as e:
        # Use enhanced error handling with audit
        await self.handle_error_with_audit(e, "wrapper_method", details={...})
        raise
```

---

## ✅ Benefits of Option B

1. **Less Work**: ~30-40 methods vs 188 methods
2. **Consistent Utilities**: All calls go through AgenticFoundationService
3. **Reasonable Coupling**: Services are agent-specific anyway
4. **Easier Maintenance**: Utilities in one place
5. **Clear Pattern**: Wrapper methods are explicit and easy to understand





