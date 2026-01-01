# Platform Developer Quick Reference
## Cheat Sheet for Common Patterns

**Date:** December 20, 2025  
**Status:** 📋 **Quick Reference**  
**Purpose:** Quick lookup for common development patterns

> **📝 Amendment Notice:** See `PLATFORM_DEVELOPER_GUIDE_AMENDMENT_2025.md` for recent updates including:
> - Agentic Correlation Tracking patterns
> - Platform Data Sidecar Pattern
> - MVP Pillars as Realm Demonstrations
> - Three Client Data Journeys

---

## 🚀 **Base Class Selection**

| Service Type | Base Class | When to Use |
|-------------|------------|-------------|
| Foundation Service | `FoundationServiceBase` | Creating a new foundation (Public Works, Curator, etc.) |
| Realm Service | `RealmServiceBase` | Creating a service in Business Enablement, Experience, Journey, Solution realms |
| Smart City Service | `SmartCityRoleBase` | Creating a Smart City service (Librarian, Security Guard, etc.) |
| Orchestrator | `OrchestratorBase` | Creating an orchestrator (Content, Insights, Operations, etc.) |
| Manager | `ManagerServiceBase` | Creating a manager (Solution, Journey, Delivery) |

---

## 🔧 **Common Access Patterns**

### Get Utilities
```python
config = self.get_utility("config")
health = self.get_health()
telemetry = self.get_telemetry()
error_handler = self.get_error_handler()
```

### Get Infrastructure
```python
file_mgmt = self.get_abstraction("file_management")
content_metadata = self.get_abstraction("content_metadata")
semantic_data = self.get_abstraction("semantic_data")
```

### Get Smart City Services
```python
librarian = await self.get_librarian_api()
content_steward = await self.get_content_steward_api()
data_steward = await self.get_data_steward_api()
security_guard = await self.get_security_guard_api()
traffic_cop = await self.get_traffic_cop_api()
conductor = await self.get_conductor_api()
post_office = await self.get_post_office_api()
nurse = await self.get_nurse_api()
city_manager = await self.get_city_manager_api()
```

### Get Foundation Services
```python
curator = di_container.get_foundation_service("CuratorFoundationService")
public_works = di_container.get_foundation_service("PublicWorksFoundationService")
agentic = di_container.get_foundation_service("AgenticFoundationService")
```

### Get Enabling Services
```python
service = await self.get_enabling_service("ServiceName")
```

---

## 🔐 **Security Patterns**

### Get Security Context
```python
tenant_id = self.get_tenant_id()
user_id = self.get_user_id()
context = self.get_security_context()
```

### Validate Access
```python
if not self.validate_access("file", "read"):
    raise PermissionError("Access denied")
```

### Multi-Tenancy
```python
tenant_id = self.get_tenant_id()
query = {
    "tenant_id": tenant_id,
    "data_classification": "client"
}
```

---

## 📝 **Service Registration**

### Standard Registration
```python
await self.register_with_curator(
    capabilities=[{
        "name": "capability_name",
        "protocol": "IProtocol",
        "description": "Description",
        "semantic_mapping": {
            "domain_capability": "domain.capability",
            "semantic_api": "/api/v1/endpoint"
        },
        "contracts": {
            "soa_api": {
                "api_name": "method_name",
                "endpoint": "/api/v1/endpoint",
                "method": "POST"
            },
            "mcp_tool": {
                "tool_name": "tool_name",
                "tool_definition": {...}
            }
        }
    }],
    soa_apis=["method1", "method2"],
    mcp_tools=["tool1", "tool2"]
)
```

---

## 🤖 **Agent Patterns**

### Create Agent
```python
agent = await self.initialize_agent(
    MyAgent,
    "MyAgent",
    agent_type="liaison",  # or "specialist", "guide"
    capabilities=["capability1"],
    required_roles=["role1"]
)
```

### Agent Base Class
```python
class MyAgent(AgentBase):
    def __init__(self, ...):
        super().__init__(
            agent_name="MyAgent",
            capabilities=["capability1"],
            required_roles=["role1"],
            agui_schema=self._create_agui_schema(),
            ...
        )
    
    async def process(self, request, user_context):
        llm_client = self.get_llm_client()
        mcp_tools = self.get_mcp_tools()
        result = await self.call_mcp_tool("tool_name", params, user_context)
        return self.generate_agui_response(result)
```

---

## 📊 **Telemetry & Monitoring**

### Track Operations
```python
await self.log_operation_with_telemetry(
    "operation_start",
    success=True
)

try:
    result = await self._do_work()
    await self.log_operation_with_telemetry(
        "operation_complete",
        success=True,
        details={"result_count": len(result)}
    )
except Exception as e:
    await self.log_operation_with_telemetry(
        "operation_complete",
        success=False,
        details={"error": str(e)}
    )
    raise
```

### Error Handling
```python
try:
    result = await self._do_work()
except Exception as e:
    await self.handle_error_with_audit(e, "operation_name")
    raise
```

---

## 🔄 **Service Discovery (Four-Tier Pattern)**

```python
# Tier 1: Enabling Service (via Curator)
service = await self.get_enabling_service("ServiceName")

# Tier 2: Direct import (fallback)
if not service:
    from backend.path import ServiceName
    service = ServiceName(...)
    await service.initialize()

# Tier 3: SOA API (if available)
if not service:
    result = await self.call_soa_api("ServiceName", "method", params)

# Tier 4: Return None (calling code handles)
if not service:
    return None
```

---

## 🏗️ **Service Template**

```python
class MyService(RealmServiceBase):
    def __init__(self, service_name, realm_name, platform_gateway, di_container):
        super().__init__(service_name, realm_name, platform_gateway, di_container)
    
    async def initialize(self):
        await super().initialize()
        
        # Get Smart City services
        self.librarian = await self.get_librarian_api()
        
        # Get infrastructure
        self.file_mgmt = self.get_abstraction("file_management")
        
        # Register with Curator
        await self.register_with_curator(
            capabilities=[...],
            soa_apis=["method1", "method2"],
            mcp_tools=["tool1", "tool2"]
        )
    
    async def my_soa_api(self, param1, param2, user_context=None):
        """Clear, atomic SOA API method."""
        tenant_id = self.get_tenant_id()
        await self.log_operation_with_telemetry("my_soa_api_start", success=True)
        
        try:
            result = await self.librarian.store_document(...)
            await self.log_operation_with_telemetry("my_soa_api_complete", success=True)
            return {"success": True, "result": result}
        except Exception as e:
            await self.log_operation_with_telemetry("my_soa_api_complete", success=False)
            await self.handle_error_with_audit(e, "my_soa_api")
            raise
```

---

## 🎯 **Orchestrator Template**

```python
class MyOrchestrator(OrchestratorBase):
    def __init__(self, service_name, realm_name, platform_gateway, di_container, delivery_manager):
        super().__init__(service_name, realm_name, platform_gateway, di_container, delivery_manager)
    
    async def initialize(self):
        await super().initialize()
        
        # Get enabling services
        self.enabling_service = await self.get_enabling_service("MyEnablingService")
        
        # Get Smart City services
        self.librarian = await self.get_librarian_api()
        
        # Initialize agents
        self.agent = await self.initialize_agent(
            MyAgent,
            "MyAgent",
            agent_type="liaison"
        )
        
        # Register with Curator
        await self.register_with_curator(...)
```

---

## ✅ **DO's and DON'Ts**

### ✅ DO's
- ✅ Use correct base class
- ✅ Initialize with DI Container
- ✅ Register with Curator
- ✅ Use helper methods for Smart City services
- ✅ Use Platform Gateway for infrastructure
- ✅ Validate security context
- ✅ Track telemetry
- ✅ Handle errors with audit
- ✅ Follow 350-line limit
- ✅ Use semantic data layer
- ✅ Use Agentic Foundation SDK (not CrewAI)
- ✅ Use JWKS local token validation

### ❌ DON'Ts
- ❌ Direct Public Works access
- ❌ Direct Communication Foundation access
- ❌ Custom storage implementations
- ❌ Custom validation logic
- ❌ Hard-coded values
- ❌ LLM in services (only in agents)
- ❌ CrewAI patterns
- ❌ Direct database access
- ❌ Bypass security validation
- ❌ Skip Curator registration
- ❌ Ignore multi-tenancy
- ❌ Access parsed data directly

---

**Last Updated:** December 20, 2025  
**Status:** 📋 **Quick Reference**


