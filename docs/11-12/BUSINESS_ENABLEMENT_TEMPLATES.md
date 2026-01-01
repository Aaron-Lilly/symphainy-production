# Business Enablement Realm: Service Type Templates

## Overview

This document provides templates for refactoring each service type in the business_enablement realm to use:
1. **Full utility pattern** (telemetry, security, tenant validation, error handling, health metrics)
2. **Curator Phase 2 registration pattern** (new `CapabilityDefinition` with `contracts`)

---

## Template 1: Enabling Service (RealmServiceBase)

### Service Structure
```python
from bases.realm_service_base import RealmServiceBase
from backend.business_enablement.protocols.service_protocol import ServiceProtocol

class EnablingService(RealmServiceBase, ServiceProtocol):
    """Enabling service template."""
    
    async def initialize(self) -> bool:
        """Initialize service with utilities."""
        await self.log_operation_with_telemetry("service_initialize_start", success=True)
        try:
            # ... initialization logic ...
            
            # Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[...],  # See Curator Registration section
                soa_apis=["method1", "method2"],
                mcp_tools=[]  # Enabling services don't have MCP tools
            )
            
            await self.record_health_metric("service_initialized", 1.0, {"service": self.service_name})
            await self.log_operation_with_telemetry("service_initialize_complete", success=True)
            return True
        except Exception as e:
            await self.handle_error_with_audit(e, "service_initialize")
            await self.log_operation_with_telemetry("service_initialize_complete", success=False, details={"error": str(e)})
            return False
    
    async def service_method(self, params, user_context: Optional[Dict[str, Any]] = None):
        """Service method with full utility usage."""
        await self.log_operation_with_telemetry("service_method_start", success=True, details={"params": params})
        try:
            # Security validation
            if user_context:
                security = self.get_security()
                if security and not await security.check_permissions(user_context, "resource", "action"):
                    await self.record_health_metric("service_method_access_denied", 1.0, {"resource": "resource"})
                    await self.log_operation_with_telemetry("service_method_complete", success=False)
                    raise PermissionError("Access denied")
            
            # Tenant validation
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id and not await tenant.validate_tenant_access(tenant_id):
                        await self.record_health_metric("service_method_tenant_denied", 1.0, {"tenant_id": tenant_id})
                        await self.log_operation_with_telemetry("service_method_complete", success=False)
                        raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            # ... business logic ...
            
            await self.record_health_metric("service_method_success", 1.0, {...})
            await self.log_operation_with_telemetry("service_method_complete", success=True, details={...})
            return result
        except Exception as e:
            await self.handle_error_with_audit(e, "service_method")
            await self.log_operation_with_telemetry("service_method_complete", success=False, details={"error": str(e)})
            raise
```

### Module Structure
```python
class ServiceModule:
    """Module for enabling service."""
    
    def __init__(self, service: Any):
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def module_method(self, params, user_context: Optional[Dict[str, Any]] = None):
        """Module method with full utility usage."""
        await self.service.log_operation_with_telemetry("module_method_start", success=True, details={...})
        try:
            # Security validation
            if user_context:
                security = self.service.get_security()
                if security and not await security.check_permissions(user_context, "resource", "action"):
                    await self.service.record_health_metric("module_method_access_denied", 1.0, {...})
                    await self.service.log_operation_with_telemetry("module_method_complete", success=False)
                    raise PermissionError("Access denied")
            
            # Tenant validation
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id and not await tenant.validate_tenant_access(tenant_id):
                        await self.service.record_health_metric("module_method_tenant_denied", 1.0, {"tenant_id": tenant_id})
                        await self.service.log_operation_with_telemetry("module_method_complete", success=False)
                        raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            # ... business logic ...
            
            await self.service.record_health_metric("module_method_success", 1.0, {...})
            await self.service.log_operation_with_telemetry("module_method_complete", success=True, details={...})
            return result
        except Exception as e:
            await self.service.handle_error_with_audit(e, "module_method")
            await self.service.log_operation_with_telemetry("module_method_complete", success=False, details={"error": str(e)})
            raise
```

### Curator Registration (Phase 2 Pattern)
```python
await self.register_with_curator(
    capabilities=[
        {
            "name": "capability_name",
            "protocol": "ServiceProtocol",
            "description": "What this capability does",
            "contracts": {
                "soa_api": {
                    "api_name": "method_name",
                    "endpoint": "/api/v1/service/method",
                    "method": "POST",
                    "handler": self.method_name,
                    "metadata": {
                        "description": "Method description",
                        "parameters": [...]
                    }
                }
            },
            "semantic_mapping": {
                "domain_capability": "domain.concept",
                "semantic_api": "/api/v1/pillar/endpoint",
                "user_journey": "user_journey_step"
            }
        }
    ],
    soa_apis=["method1", "method2"],
    mcp_tools=[]  # Enabling services don't have MCP tools
)
```

---

## Template 2: Orchestrator (OrchestratorBase)

### Service Structure
```python
from bases.orchestrator_base import OrchestratorBase
from backend.business_enablement.protocols.orchestrator_protocol import OrchestratorProtocol

class UseCaseOrchestrator(OrchestratorBase, OrchestratorProtocol):
    """Orchestrator template."""
    
    async def initialize(self) -> bool:
        """Initialize orchestrator with utilities."""
        await self.log_operation_with_telemetry("orchestrator_initialize_start", success=True)
        try:
            # ... initialization logic ...
            
            # Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[...],  # See Curator Registration section
                soa_apis=["orchestrate", "get_status"],
                mcp_tools=["use_case_tool1", "use_case_tool2"]
            )
            
            await self.record_health_metric("orchestrator_initialized", 1.0, {"orchestrator": self.service_name})
            await self.log_operation_with_telemetry("orchestrator_initialize_complete", success=True)
            return True
        except Exception as e:
            await self.handle_error_with_audit(e, "orchestrator_initialize")
            await self.log_operation_with_telemetry("orchestrator_initialize_complete", success=False, details={"error": str(e)})
            return False
    
    async def orchestrate(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None):
        """Orchestrate use case with full utility usage."""
        await self.log_operation_with_telemetry("orchestrate_start", success=True, details={"request": request})
        try:
            # Security validation
            if user_context:
                security = self.get_security()
                if security and not await security.check_permissions(user_context, "orchestration", "execute"):
                    await self.record_health_metric("orchestrate_access_denied", 1.0, {...})
                    await self.log_operation_with_telemetry("orchestrate_complete", success=False)
                    raise PermissionError("Access denied")
            
            # Tenant validation
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id and not await tenant.validate_tenant_access(tenant_id):
                        await self.record_health_metric("orchestrate_tenant_denied", 1.0, {"tenant_id": tenant_id})
                        await self.log_operation_with_telemetry("orchestrate_complete", success=False)
                        raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            # ... orchestration logic ...
            
            await self.record_health_metric("orchestrate_success", 1.0, {...})
            await self.log_operation_with_telemetry("orchestrate_complete", success=True, details={...})
            return result
        except Exception as e:
            await self.handle_error_with_audit(e, "orchestrate")
            await self.log_operation_with_telemetry("orchestrate_complete", success=False, details={"error": str(e)})
            raise
```

### Curator Registration (Phase 2 Pattern)
```python
await self.register_with_curator(
    capabilities=[
        {
            "name": "orchestrate_use_case",
            "protocol": "OrchestratorProtocol",
            "description": "Orchestrates use case execution",
            "contracts": {
                "soa_api": {
                    "api_name": "orchestrate",
                    "endpoint": "/api/v1/orchestrator/orchestrate",
                    "method": "POST",
                    "handler": self.orchestrate
                },
                "mcp_tool": {
                    "tool_name": "use_case_tool",
                    "tool_definition": {
                        "name": "use_case_tool",
                        "description": "Execute use case",
                        "input_schema": {...}
                    }
                }
            },
            "semantic_mapping": {
                "domain_capability": "use_case.execute",
                "semantic_api": "/api/v1/pillar/execute",
                "user_journey": "execute_use_case"
            }
        }
    ],
    soa_apis=["orchestrate", "get_status"],
    mcp_tools=["use_case_tool1", "use_case_tool2"]
)
```

---

## Template 3: Manager Service (ManagerServiceBase)

### Service Structure
```python
from bases.manager_service_base import ManagerServiceBase
from backend.business_enablement.protocols.manager_service_protocol import ManagerServiceProtocol

class ManagerService(ManagerServiceBase, ManagerServiceProtocol):
    """Manager service template."""
    
    async def initialize(self) -> bool:
        """Initialize manager service with utilities."""
        await self.log_operation_with_telemetry("manager_initialize_start", success=True)
        try:
            # ... initialization logic ...
            
            # Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[...],  # See Curator Registration section
                soa_apis=["coordinate", "get_status"],
                mcp_tools=["coordination_tool1", "coordination_tool2"]
            )
            
            await self.record_health_metric("manager_initialized", 1.0, {"manager": self.service_name})
            await self.log_operation_with_telemetry("manager_initialize_complete", success=True)
            return True
        except Exception as e:
            await self.handle_error_with_audit(e, "manager_initialize")
            await self.log_operation_with_telemetry("manager_initialize_complete", success=False, details={"error": str(e)})
            return False
    
    async def coordinate(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None):
        """Coordinate orchestrators with full utility usage."""
        await self.log_operation_with_telemetry("coordinate_start", success=True, details={"request": request})
        try:
            # Security validation
            if user_context:
                security = self.get_security()
                if security and not await security.check_permissions(user_context, "coordination", "execute"):
                    await self.record_health_metric("coordinate_access_denied", 1.0, {...})
                    await self.log_operation_with_telemetry("coordinate_complete", success=False)
                    raise PermissionError("Access denied")
            
            # Tenant validation
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id and not await tenant.validate_tenant_access(tenant_id):
                        await self.record_health_metric("coordinate_tenant_denied", 1.0, {"tenant_id": tenant_id})
                        await self.log_operation_with_telemetry("coordinate_complete", success=False)
                        raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            # ... coordination logic ...
            
            await self.record_health_metric("coordinate_success", 1.0, {...})
            await self.log_operation_with_telemetry("coordinate_complete", success=True, details={...})
            return result
        except Exception as e:
            await self.handle_error_with_audit(e, "coordinate")
            await self.log_operation_with_telemetry("coordinate_complete", success=False, details={"error": str(e)})
            raise
```

### Curator Registration (Phase 2 Pattern)
```python
await self.register_with_curator(
    capabilities=[
        {
            "name": "coordinate_orchestrators",
            "protocol": "ManagerServiceProtocol",
            "description": "Coordinates orchestrators",
            "contracts": {
                "soa_api": {
                    "api_name": "coordinate",
                    "endpoint": "/api/v1/manager/coordinate",
                    "method": "POST",
                    "handler": self.coordinate
                },
                "mcp_tool": {
                    "tool_name": "coordination_tool",
                    "tool_definition": {...}
                }
            },
            "semantic_mapping": {
                "domain_capability": "coordination.execute",
                "semantic_api": "/api/v1/manager/coordinate"
            }
        }
    ],
    soa_apis=["coordinate", "get_status"],
    mcp_tools=["coordination_tool1", "coordination_tool2"]
)
```

---

## Template 4: Agent (AgentBase)

### Agent Structure
```python
from bases.agent_base import AgentBase
from backend.business_enablement.protocols.agent_protocol import AgentProtocol

class SpecialistAgent(AgentBase, AgentProtocol):
    """Agent template."""
    
    async def initialize(self) -> bool:
        """Initialize agent with utilities."""
        await self.log_operation_with_telemetry("agent_initialize_start", success=True)
        try:
            # ... initialization logic ...
            
            # Register with Curator (new register_agent pattern)
            curator = self.get_curator()
            if curator:
                await curator.register_agent(
                    agent_id=self.agent_id,
                    agent_name=self.agent_name,
                    characteristics={
                        "capabilities": self.capabilities,
                        "pillar": self.pillar,
                        "specialization": self.specialization,
                        "required_roles": self.required_roles,
                        "agui_schema": self.agui_schema
                    },
                    contracts={
                        "mcp_tools": self.mcp_tools,
                        "agent_api": self.agent_api
                    },
                    user_context=None  # Internal registration
                )
            
            await self.record_health_metric("agent_initialized", 1.0, {"agent": self.agent_name})
            await self.log_operation_with_telemetry("agent_initialize_complete", success=True)
            return True
        except Exception as e:
            await self.handle_error_with_audit(e, "agent_initialize")
            await self.log_operation_with_telemetry("agent_initialize_complete", success=False, details={"error": str(e)})
            return False
    
    async def execute(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None):
        """Execute agent task with full utility usage."""
        await self.log_operation_with_telemetry("agent_execute_start", success=True, details={"request": request})
        try:
            # Security validation
            if user_context:
                security = self.get_security()
                if security and not await security.check_permissions(user_context, "agent", "execute"):
                    await self.record_health_metric("agent_execute_access_denied", 1.0, {...})
                    await self.log_operation_with_telemetry("agent_execute_complete", success=False)
                    raise PermissionError("Access denied")
            
            # Tenant validation
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id and not await tenant.validate_tenant_access(tenant_id):
                        await self.record_health_metric("agent_execute_tenant_denied", 1.0, {"tenant_id": tenant_id})
                        await self.log_operation_with_telemetry("agent_execute_complete", success=False)
                        raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            # ... agent logic ...
            
            await self.record_health_metric("agent_execute_success", 1.0, {...})
            await self.log_operation_with_telemetry("agent_execute_complete", success=True, details={...})
            return result
        except Exception as e:
            await self.handle_error_with_audit(e, "agent_execute")
            await self.log_operation_with_telemetry("agent_execute_complete", success=False, details={"error": str(e)})
            raise
```

### Curator Registration (New Pattern)
```python
curator = self.get_curator()
if curator:
    await curator.register_agent(
        agent_id=self.agent_id,
        agent_name=self.agent_name,
        characteristics={
            "capabilities": ["capability1", "capability2"],
            "pillar": "content",
            "specialization": "content_analysis",
            "required_roles": ["analyst", "reviewer"],
            "agui_schema": {
                "input_fields": [...],
                "output_fields": [...]
            }
        },
        contracts={
            "mcp_tools": [
                {
                    "tool_name": "agent_tool",
                    "tool_definition": {
                        "name": "agent_tool",
                        "description": "Agent tool description",
                        "input_schema": {...}
                    }
                }
            ],
            "agent_api": {
                "execute": self.execute,
                "get_status": self.get_status
            }
        },
        user_context=None  # Internal registration
    )
```

---

## Template 5: MCP Server (MCPServerBase)

### MCP Server Structure
```python
from bases.mcp_server_base import MCPServerBase

class UseCaseMCPServer(MCPServerBase):
    """MCP Server template."""
    
    def __init__(self, orchestrator, di_container):
        """Initialize MCP server."""
        super().__init__(
            server_name="use_case_mcp_server",
            di_container=di_container,
            server_type="single_service"  # 1:1 for orchestrators
        )
        self.orchestrator = orchestrator
        self._register_tools()
    
    def _register_tools(self):
        """Register MCP tools (tools are registered via orchestrator's Curator registration)."""
        # Tools are registered when orchestrator registers capabilities
        # MCP server just routes tool execution to orchestrator methods
        pass
    
    async def execute_tool(self, tool_name: str, parameters: dict, user_context: Optional[Dict[str, Any]] = None):
        """Execute MCP tool with full utility usage."""
        await self.log_operation_with_telemetry("mcp_execute_tool_start", success=True, details={"tool": tool_name})
        try:
            # Security validation
            if user_context:
                security = self.get_security()
                if security and not await security.check_permissions(user_context, "mcp_tool", "execute"):
                    await self.record_health_metric("mcp_execute_tool_access_denied", 1.0, {"tool": tool_name})
                    await self.log_operation_with_telemetry("mcp_execute_tool_complete", success=False)
                    raise PermissionError("Access denied")
            
            # Tenant validation
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id and not await tenant.validate_tenant_access(tenant_id):
                        await self.record_health_metric("mcp_execute_tool_tenant_denied", 1.0, {"tool": tool_name, "tenant_id": tenant_id})
                        await self.log_operation_with_telemetry("mcp_execute_tool_complete", success=False)
                        raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            # Route to orchestrator method
            result = await self.orchestrator.execute_tool(tool_name, parameters, user_context)
            
            await self.record_health_metric("mcp_execute_tool_success", 1.0, {"tool": tool_name})
            await self.log_operation_with_telemetry("mcp_execute_tool_complete", success=True, details={"tool": tool_name})
            return result
        except Exception as e:
            await self.handle_error_with_audit(e, "mcp_execute_tool")
            await self.log_operation_with_telemetry("mcp_execute_tool_complete", success=False, details={"tool": tool_name, "error": str(e)})
            raise
```

**Note**: MCP Servers don't register directly with Curator. Tools are registered when the orchestrator/service registers capabilities with MCP tool contracts.

---

## Common Patterns

### Utility Usage Checklist
- ✅ Telemetry: `log_operation_with_telemetry()` (start/complete pattern)
- ✅ Security: `get_security().check_permissions()` (zero-trust validation)
- ✅ Tenant: `get_tenant().validate_tenant_access()` (multi-tenancy)
- ✅ Error Handling: `handle_error_with_audit()` (all exceptions)
- ✅ Health Metrics: `record_health_metric()` (success/failure tracking)
- ✅ Logging: `self.logger` (via DI Container)

### Curator Registration Checklist
- ✅ Use `CapabilityDefinition` structure (via `register_with_curator()`)
- ✅ Include `capability_name`, `protocol_name`, `contracts` (required)
- ✅ Include `semantic_mapping` (for user-facing capabilities)
- ✅ Register `soa_api` contracts for SOA APIs
- ✅ Register `mcp_tool` contracts for MCP tools
- ✅ Register `rest_api` contracts for REST endpoints (if applicable)

### Migration Checklist
- ✅ Replace old `register_with_curator()` dict format with new structure
- ✅ Add utility usage to all methods (service-level and module-level)
- ✅ Add security and tenant validation to user-facing methods
- ✅ Add telemetry tracking (start/complete pattern)
- ✅ Add error handling with audit
- ✅ Add health metrics recording
- ✅ Test utility usage
- ✅ Test Curator registration and discovery





