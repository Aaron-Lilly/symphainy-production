# Business Enablement Agent Refactoring Template

**Date:** December 2024  
**Status:** 📋 **REFACTORING TEMPLATE**

---

## Overview

This template provides the enhanced pattern for refactoring Business Enablement agents to align with:
- ✅ New Agentic Foundation factory pattern (factory owns registration)
- ✅ Standardized utility usage (via AgentBase utility methods)
- ✅ Phase 2 Curator registration (via factory)
- ✅ Consistent capabilities pattern
- ✅ Full utility integration (telemetry, health, security, tenant)

---

## Enhanced Agent Pattern Template

### 1. Agent Class Structure

```python
#!/usr/bin/env python3
"""
[Agent Name] - [Description]

[WHAT (Business Enablement Role): Description]
[HOW (Agent Type): Description]
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from utilities import UserContext
from backend.business_enablement.protocols.business_specialist_agent_protocol import (
    BusinessSpecialistAgentBase,
    SpecialistCapability
)
# OR for liaison agents:
# from foundations.agentic_foundation.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
# OR for guide agents:
# from foundations.agentic_foundation.agent_sdk.global_guide_agent import GlobalGuideAgent


class [AgentName](BusinessSpecialistAgentBase):
    """
    [Agent Name] - [Description]
    
    [Detailed description of agent capabilities and purpose]
    
    Uses full Agentic SDK via Agentic Foundation factory.
    """
    
    def __init__(
        self,
        agent_name: str,
        business_domain: str,
        capabilities: List[str],  # REQUIRED - factory validates this
        required_roles: List[str],
        agui_schema: Any,
        foundation_services: Any,
        agentic_foundation: Any,
        public_works_foundation: Any,
        mcp_client_manager: Any,
        policy_integration: Any,
        tool_composition: Any,
        agui_formatter: Any,
        curator_foundation: Any = None,
        metadata_foundation: Any = None,
        **kwargs
    ):
        """
        Initialize [Agent Name] with full SDK dependencies.
        
        This agent is created via Agentic Foundation factory - all dependencies
        are provided by the factory.
        
        Args:
            agent_name: Name of the agent
            business_domain: Business domain (realm)
            capabilities: List of agent capabilities (REQUIRED - factory validates)
            required_roles: List of required Smart City roles
            agui_schema: AGUI schema for structured output
            foundation_services: DI container service
            agentic_foundation: Agentic foundation service
            public_works_foundation: Public works foundation service
            mcp_client_manager: MCP client manager
            policy_integration: Policy integration service
            tool_composition: Tool composition service
            agui_formatter: AGUI output formatter
            curator_foundation: Optional curator foundation
            metadata_foundation: Optional metadata foundation
            **kwargs: Additional agent-specific parameters
        """
        super().__init__(
            agent_name=agent_name,
            business_domain=business_domain,
            capabilities=capabilities,  # REQUIRED - set in __init__
            required_roles=required_roles,
            agui_schema=agui_schema,
            foundation_services=foundation_services,
            public_works_foundation=public_works_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            curator_foundation=curator_foundation,
            metadata_foundation=metadata_foundation,
            specialist_capability=kwargs.get("specialist_capability", SpecialistCapability.[CAPABILITY_TYPE]),
            **{k: v for k, v in kwargs.items() if k != "specialist_capability"}
        )
        
        # Agent-specific properties
        self.service_name = agent_name
        
        # Orchestrator reference (set by orchestrator for MCP tool access)
        self.orchestrator = None
        self.[domain]_orchestrator = None  # Domain-specific alias
        
        # Agent-specific state
        self.[agent_specific_state] = {}
    
    async def initialize(self):
        """
        Initialize [Agent Name].
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        
        Note: Factory handles Curator registration (Agentic Foundation owns agent registry).
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("initialize_start", success=True)
            
            # Call parent initialize
            await super().initialize()
            
            # Agent-specific initialization logic
            # ... initialization code ...
            
            # Discover orchestrator via Curator (optional, agent can work independently)
            if self.curator_foundation:
                try:
                    registered_services = await self.curator_foundation.get_registered_services()
                    services_dict = registered_services.get("services", {})
                    if "[OrchestratorServiceName]" in services_dict:
                        service_info = services_dict["[OrchestratorServiceName]"]
                        self.orchestrator = service_info.get("service_instance")
                        self.logger.info("✅ Discovered [OrchestratorServiceName]")
                except Exception as e:
                    self.logger.warning(f"⚠️ [OrchestratorServiceName] not available: {e}")
            
            # REMOVED: Self-registration with Curator
            # Factory handles registration (Agentic Foundation owns agent registry)
            
            self.is_initialized = True
            
            # Record health metric (success)
            await self.record_health_metric("initialized", 1.0, {
                "agent_name": self.service_name
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("initialize_complete", success=True)
            
            self.logger.info(f"✅ {self.service_name} initialization complete")
            return True
        
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "initialize", {
                "agent_name": self.service_name
            })
            
            # Record health metric (failure)
            await self.record_health_metric("initialization_failed", 1.0, {
                "agent_name": self.service_name,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("initialize_complete", success=False, {
                "error": str(e)
            })
            
            self.is_initialized = False
            return False
    
    def set_orchestrator(self, orchestrator):
        """Set orchestrator reference for MCP server access."""
        self.orchestrator = orchestrator
        self.[domain]_orchestrator = orchestrator  # Domain-specific alias
        self.logger.info("✅ Orchestrator reference set for MCP tool access")
    
    async def [user_facing_method](
        self,
        [method_params],
        user_context: UserContext
    ) -> Dict[str, Any]:
        """
        [Method description]
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        
        Args:
            [method_params]: Method parameters
            user_context: User context for authorization and tenant validation
            
        Returns:
            Method result
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("[method_name]_start", success=True, {
                "[param_name]": [param_value]
            })
            
            # Security validation (zero-trust: secure by design)
            if user_context and self.security:
                try:
                    # Convert UserContext to dict for security check
                    user_context_dict = {
                        "user_id": getattr(user_context, "user_id", None),
                        "tenant_id": getattr(user_context, "tenant_id", None),
                        "roles": getattr(user_context, "roles", [])
                    }
                    if not await self.security.check_permissions(user_context_dict, "[resource]", "[action]"):
                        # Record health metric (access denied)
                        await self.record_health_metric("[method_name]_access_denied", 1.0, {
                            "[param_name]": [param_value]
                        })
                        # End telemetry tracking
                        await self.log_operation_with_telemetry("[method_name]_complete", success=False, {
                            "status": "access_denied"
                        })
                        raise PermissionError("Access denied: insufficient permissions")
                except PermissionError:
                    raise
                except Exception:
                    pass  # Security check is optional
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant_id = getattr(user_context, "tenant_id", None)
                if tenant_id and hasattr(self, "public_works_foundation"):
                    try:
                        tenant_service = self.public_works_foundation.get_tenant_service()
                        if tenant_service and not await tenant_service.validate_tenant_access(tenant_id):
                            # Record health metric (tenant denied)
                            await self.record_health_metric("[method_name]_tenant_denied", 1.0, {
                                "[param_name]": [param_value],
                                "tenant_id": tenant_id
                            })
                            # End telemetry tracking
                            await self.log_operation_with_telemetry("[method_name]_complete", success=False, {
                                "status": "tenant_denied"
                            })
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
                    except PermissionError:
                        raise
                    except Exception:
                        pass  # Tenant validation is optional
            
            # Business logic
            # ... method implementation ...
            result = ...
            
            # Record health metric (success)
            await self.record_health_metric("[method_name]_success", 1.0, {
                "[param_name]": [param_value]
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("[method_name]_complete", success=True)
            
            return {
                "success": True,
                "message": "[Success message]",
                "result": result
            }
            
        except PermissionError:
            raise  # Re-raise permission errors
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "[method_name]", {
                "[param_name]": [param_value]
            })
            
            # Record health metric (failure)
            await self.record_health_metric("[method_name]_error", 1.0, {
                "[param_name]": [param_value],
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("[method_name]_complete", success=False, {
                "error": str(e)
            })
            
            return {
                "success": False,
                "message": f"[Method] failed: {str(e)}",
                "error_details": {"error": str(e)}
            }
```

---

## Key Patterns

### 1. Capabilities (REQUIRED)

```python
# In __init__:
self.capabilities = capabilities  # Set by parent class, but ensure it's set

# Factory validates capabilities are provided (fail fast)
# Agents must provide capabilities when created via factory
```

### 2. Utility Methods (Use AgentBase Methods)

```python
# Use AgentBase utility methods (not manual utility access):
await self.log_operation_with_telemetry("operation_name", success=True, details={})
await self.record_health_metric("metric_name", 1.0, metadata={})
await self.handle_error_with_audit(error, "operation_name", details={})

# These methods are available on all agents via AgentBase
```

### 3. Security & Tenant Validation

```python
# Security validation (zero-trust)
if user_context and self.security:
    user_context_dict = {
        "user_id": getattr(user_context, "user_id", None),
        "tenant_id": getattr(user_context, "tenant_id", None),
        "roles": getattr(user_context, "roles", [])
    }
    if not await self.security.check_permissions(user_context_dict, "resource", "action"):
        raise PermissionError("Access denied")

# Tenant validation (multi-tenancy)
if user_context:
    tenant_id = getattr(user_context, "tenant_id", None)
    if tenant_id and hasattr(self, "public_works_foundation"):
        tenant_service = self.public_works_foundation.get_tenant_service()
        if tenant_service and not await tenant_service.validate_tenant_access(tenant_id):
            raise PermissionError(f"Tenant access denied: {tenant_id}")
```

### 4. No Self-Registration

```python
# ❌ DO NOT call register_with_curator() in initialize()
# ❌ DO NOT have register_with_curator() method
# ✅ Factory handles all registration via Phase 2 pattern
```

### 5. Factory Pattern Compliance

```python
# ✅ All agents created via factory:
agent = await agentic_foundation.create_agent(
    agent_class=AgentClass,
    agent_name="AgentName",
    agent_type="specialist",  # or "liaison", "guide"
    realm_name="business_enablement",
    di_container=di_container,
    orchestrator=orchestrator,  # Optional
    capabilities=["capability1", "capability2"],  # REQUIRED
    required_roles=["librarian"],
    ...
)

# ❌ DO NOT create agents directly:
# agent = AgentClass(...)  # WRONG!
```

---

## Refactoring Checklist

For each agent:

### Base Class
- [ ] Extends appropriate base (`BusinessSpecialistAgentBase`, `DimensionLiaisonAgent`, `GlobalGuideAgent`)
- [ ] Inherits from `AgentBase` via base class

### Initialization
- [ ] `self.capabilities` set in `__init__` (via parent class)
- [ ] All factory dependencies provided via `__init__`
- [ ] No self-registration in `initialize()`
- [ ] Uses `log_operation_with_telemetry()` for telemetry
- [ ] Uses `record_health_metric()` for health metrics
- [ ] Uses `handle_error_with_audit()` for error handling

### Utility Usage
- [ ] Telemetry tracking in user-facing methods (via `log_operation_with_telemetry()`)
- [ ] Health metrics recording (via `record_health_metric()`)
- [ ] Security validation (zero-trust)
- [ ] Tenant validation (multi-tenancy)
- [ ] Error handling with audit logging (via `handle_error_with_audit()`)

### User Context
- [ ] `user_context` parameter in all user-facing methods
- [ ] Security validation using `user_context`
- [ ] Tenant validation using `user_context`
- [ ] UserContext converted to dict for security checks

### Factory Compliance
- [ ] Created via factory (not direct instantiation)
- [ ] Capabilities provided to factory
- [ ] Factory handles registration

### Registration
- [ ] No `register_with_curator()` calls
- [ ] No `register_with_curator()` methods
- [ ] Factory handles all registration

---

## Migration Steps

1. **Update Base Class**: Ensure agent extends appropriate base class
2. **Update `__init__`**: Ensure capabilities are set (via parent)
3. **Update `initialize()`**: 
   - Remove any `register_with_curator()` calls
   - Add utility method calls (`log_operation_with_telemetry`, `record_health_metric`, `handle_error_with_audit`)
4. **Update User-Facing Methods**:
   - Add `user_context` parameter
   - Add security validation
   - Add tenant validation
   - Add utility method calls
   - Update error handling to use `handle_error_with_audit()`
5. **Verify Factory Usage**: Ensure agent is created via factory
6. **Test**: Verify agent works with factory and utilities

---

## Example: Before vs After

### Before (Old Pattern)

```python
async def initialize(self):
    await super().initialize()
    if self.curator_foundation:
        await self.register_with_curator()  # ❌ Self-registration
    self.is_initialized = True

async def process_data(self, data: Dict[str, Any]):  # ❌ No user_context
    try:
        # Manual utility access
        if self.telemetry:
            await self.telemetry.collect_metric({...})  # ❌ Manual access
        result = ...
        return result
    except Exception as e:
        self.logger.error(f"Error: {e}")  # ❌ No audit logging
        return {"error": str(e)}
```

### After (Enhanced Pattern)

```python
async def initialize(self):
    try:
        await self.log_operation_with_telemetry("initialize_start", success=True)
        await super().initialize()
        # ✅ No self-registration - factory handles it
        self.is_initialized = True
        await self.record_health_metric("initialized", 1.0, {})
        await self.log_operation_with_telemetry("initialize_complete", success=True)
        return True
    except Exception as e:
        await self.handle_error_with_audit(e, "initialize")
        return False

async def process_data(
    self,
    data: Dict[str, Any],
    user_context: UserContext  # ✅ User context
) -> Dict[str, Any]:
    try:
        await self.log_operation_with_telemetry("process_data_start", success=True)
        
        # ✅ Security validation
        if user_context and self.security:
            user_context_dict = {...}
            if not await self.security.check_permissions(user_context_dict, "data", "process"):
                raise PermissionError("Access denied")
        
        # ✅ Tenant validation
        if user_context:
            tenant_id = getattr(user_context, "tenant_id", None)
            if tenant_id and hasattr(self, "public_works_foundation"):
                tenant_service = self.public_works_foundation.get_tenant_service()
                if tenant_service and not await tenant_service.validate_tenant_access(tenant_id):
                    raise PermissionError(f"Tenant access denied: {tenant_id}")
        
        result = ...
        
        await self.record_health_metric("process_data_success", 1.0, {})
        await self.log_operation_with_telemetry("process_data_complete", success=True)
        return {"success": True, "result": result}
    except PermissionError:
        raise
    except Exception as e:
        await self.handle_error_with_audit(e, "process_data")  # ✅ Audit logging
        await self.record_health_metric("process_data_error", 1.0, {"error": str(e)})
        return {"success": False, "error": str(e)}
```

---

## Notes

- **AgentBase Utility Methods**: All agents now have access to `log_operation_with_telemetry()`, `record_health_metric()`, and `handle_error_with_audit()` via AgentBase
- **Factory Registration**: Factory handles all registration using Phase 2 pattern - agents should never self-register
- **Capabilities**: Factory validates capabilities are provided (fail fast) - all agents must provide capabilities
- **User Context**: All user-facing methods must accept `user_context` parameter for security and tenant validation
- **Error Handling**: Use `handle_error_with_audit()` for consistent error handling and audit logging

---

**Status:** 📋 **REFACTORING TEMPLATE**  
**Last Updated:** December 2024



