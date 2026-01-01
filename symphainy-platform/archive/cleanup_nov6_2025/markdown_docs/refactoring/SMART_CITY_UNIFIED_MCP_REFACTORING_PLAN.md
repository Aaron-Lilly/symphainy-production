# 🎯 Smart City Unified MCP Server Refactoring Plan

**Goal:** Consolidate 8 individual MCP servers into 1 unified Smart City MCP Server  
**Timeline:** Week 3-4 (5 days)  
**Risk Level:** Medium (backward-compatible changes)

---

## ✅ RECOMMENDATION REVIEW

I **fully agree** with the Unified Smart City MCP Server recommendation. The benefits are clear:

### **Operational Benefits:**
- ✅ 1 process instead of 8 (87.5% reduction in processes)
- ✅ 1 port instead of 8 (simpler deployment & configuration)
- ✅ Single health check endpoint
- ✅ Easier debugging (single point of control)
- ✅ Reduced resource footprint

### **Agent Benefits:**
- ✅ 1 connection instead of 8 (simpler client code)
- ✅ Clear tool naming (`{role}_{tool_name}`)
- ✅ Easier tool discovery (all Smart City tools in one place)
- ✅ Reduced connection overhead

### **Platform Benefits:**
- ✅ Aligns with "Smart City as orchestrator" vision
- ✅ City Manager can centrally manage tool exposure
- ✅ Single governance point for Smart City MCP
- ✅ Enables Agentic IDP (agents managing agents via MCP)

---

## 📊 CURRENT STATE ANALYSIS

### **Existing MCP Servers (8 Individual):**

```
backend/smart_city/services/
├── city_manager/mcp_server/city_manager_mcp_server.py        (port 8007)
├── conductor/mcp_server/conductor_mcp_server.py              (port 8003)
├── content_steward/mcp_server/ (if exists)
├── data_steward/mcp_server/data_steward_mcp_server.py       (port 8002)
├── librarian/mcp_server/librarian_mcp_server.py              (port 8001)
├── nurse/mcp_server/nurse_mcp_server.py                       (port 8006)
├── post_office/mcp_server/post_office_mcp_server.py         (port 8004)
├── security_guard/mcp_server/security_guard_mcp_server.py   (port 8005)
└── traffic_cop/mcp_server/traffic_cop_mcp_server.py        (port 8008)
```

### **MCPClientManager Current Configuration:**

```python
# From agentic_foundation/agent_sdk/mcp_client_manager.py
self.role_mappings = {
    "librarian": "http://localhost:8001",
    "data_steward": "http://localhost:8002", 
    "conductor": "http://localhost:8003",
    "post_office": "http://localhost:8004",
    "security_guard": "http://localhost:8005",
    "nurse": "http://localhost:8006",
    "city_manager": "http://localhost:8007",
    "traffic_cop": "http://localhost:8008"
}
```

### **Service Tool Definitions:**

Each service has `modules/soa_mcp.py` with `mcp_tools` dictionary:
- Tool definitions (name, description, input_schema)
- Used for SOA API exposure and MCP tool registration

---

## 🎯 TARGET STATE

### **Unified Smart City MCP Server:**

```
backend/smart_city/
└── mcp_server/
    ├── __init__.py
    └── smart_city_mcp_server.py          (NEW - unified server)
```

### **Single Endpoint:**

```python
# Unified endpoint for all Smart City tools
smart_city_endpoint = "http://localhost:8000/mcp"
```

### **Tool Naming Pattern:**

```
All tools namespaced by role:
├─ librarian_upload_file
├─ librarian_search_documents
├─ librarian_get_metadata
├─ data_steward_validate_schema
├─ data_steward_record_lineage
├─ security_guard_authenticate_user
├─ security_guard_authorize_action
├─ conductor_execute_workflow
├─ post_office_send_message
├─ traffic_cop_manage_session
├─ nurse_collect_telemetry
├─ city_manager_bootstrap_platform
└─ content_steward_process_upload
```

---

## 🔧 REFACTORING PLAN

### **Phase 1: Enhance MCPServerBase (Day 1-2)**

**Goal:** Refactor MCPServerBase for multi-service pattern (clean break - no backward compatibility)

#### **1.1 Update MCPServerBase:**

```python
# bases/mcp_server_base.py

class MCPServerBase(ABC):
    """MCP Server Base - optimized for multi-service unified servers."""
    
    def __init__(self, server_name: str, di_container,
                 security_provider=None, authorization_guard=None):
        # ... existing initialization ...
        
        # Multi-service support (core architecture)
        self.registered_services: Dict[str, Any] = {}
        self.service_tool_prefixes: Dict[str, str] = {}
        self.tool_routing: Dict[str, str] = {}  # tool_name -> service_name
        
        # ... rest of initialization ...
    
    async def register_service(self, service_name: str, service_instance: Any, tool_prefix: Optional[str] = None):
        """
        Register a service with multi-service MCP server.
        
        Args:
            service_name: Name of the service (e.g., "librarian", "data_steward")
            service_instance: The service instance
            tool_prefix: Optional prefix for tools (defaults to service_name)
        """
        prefix = tool_prefix or service_name
        self.registered_services[service_name] = service_instance
        self.service_tool_prefixes[service_name] = prefix
        
        # Register tools from service's mcp_tools
        if hasattr(service_instance, 'mcp_tools') and service_instance.mcp_tools:
            for tool_name, tool_def in service_instance.mcp_tools.items():
                namespaced_tool_name = f"{prefix}_{tool_name}"
                await self.register_tool({
                    "name": namespaced_tool_name,
                    "description": tool_def.get("description", ""),
                    "input_schema": tool_def.get("input_schema", {}),
                    "handler": self._create_tool_handler(service_name, tool_name)
                })
                self.tool_routing[namespaced_tool_name] = service_name
    
    def _create_tool_handler(self, service_name: str, tool_name: str) -> Callable:
        """Create a handler function that routes to the appropriate service."""
        async def handler(parameters: Dict[str, Any]) -> Dict[str, Any]:
            service = self.registered_services.get(service_name)
            if not service:
                return {"success": False, "error": f"Service {service_name} not registered"}
            
            # Route to service method (standardize naming)
            method_name = tool_name  # or map tool_name to service method
            
            if hasattr(service, method_name):
                method = getattr(service, method_name)
                if callable(method):
                    return await method(parameters)
            
            return {"success": False, "error": f"Tool {tool_name} not found in service {service_name}"}
        
        return handler
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool - routes to appropriate service.
        
        Args:
            tool_name: Tool name (namespaced: {role}_{tool_name})
            parameters: Tool parameters
            
        Returns:
            Execution result
        """
        # Route to appropriate service
        service_name = self.tool_routing.get(tool_name)
        if service_name:
            service = self.registered_services.get(service_name)
            if service:
                # Extract original tool name (remove prefix)
                prefix = self.service_tool_prefixes.get(service_name, "")
                original_tool_name = tool_name.replace(f"{prefix}_", "", 1)
                
                # Call service method
                return await self._execute_service_tool(service_name, original_tool_name, parameters)
        
        return {"success": False, "error": f"Tool {tool_name} not found"}
```

#### **1.2 Testing:**
- ✅ Test multi-service registration
- ✅ Test tool routing
- ✅ Test error handling
- ✅ Verify clean multi-service architecture

---

### **Phase 2: Create Unified Smart City MCP Server (Day 3-4)**

**Goal:** Create the unified MCP server that registers all Smart City services

#### **2.1 Create Unified MCP Server:**

```python
# backend/smart_city/mcp_server/smart_city_mcp_server.py

from typing import Dict, Any
from bases.mcp_server_base import MCPServerBase


class SmartCityMCPServer(MCPServerBase):
    """
    Unified MCP Server for Smart City Realm
    
    Provides single MCP endpoint for all Smart City services:
    - Librarian (knowledge management)
    - Data Steward (data governance)
    - Content Steward (content management)
    - Security Guard (authentication/authorization)
    - Conductor (workflow orchestration)
    - Post Office (messaging)
    - Traffic Cop (session/state management)
    - Nurse (health monitoring)
    - City Manager (platform governance)
    """
    
    def __init__(self, di_container):
        super().__init__(
            server_name="smart_city_mcp",
            di_container=di_container
        )
        
        self.logger.info("🏛️ Smart City Unified MCP Server initialized")
    
    async def initialize(self):
        """Initialize unified MCP server and register all Smart City services."""
        try:
            self.logger.info("🔧 Registering Smart City services with unified MCP server...")
            
            # Get all Smart City services from DI Container
            services_to_register = [
                ("librarian", "LibrarianService"),
                ("data_steward", "DataStewardService"),
                ("content_steward", "ContentStewardService"),
                ("security_guard", "SecurityGuardService"),
                ("conductor", "ConductorService"),
                ("post_office", "PostOfficeService"),
                ("traffic_cop", "TrafficCopService"),
                ("nurse", "NurseService"),
                ("city_manager", "CityManagerService")
            ]
            
            registered_count = 0
            
            for role_name, service_class_name in services_to_register:
                try:
                    # Get service from DI Container
                    service = self.di_container.get_service(service_class_name)
                    
                    if service:
                        # Register service with MCP server
                        await self.register_service(
                            service_name=role_name,
                            service_instance=service,
                            tool_prefix=role_name  # Use role name as tool prefix
                        )
                        registered_count += 1
                        self.logger.info(f"✅ Registered {role_name} service")
                    else:
                        self.logger.warning(f"⚠️ Service {service_class_name} not found in DI Container")
                
                except Exception as e:
                    self.logger.error(f"❌ Failed to register {role_name} service: {e}")
                    continue
            
            self.logger.info(f"✅ Smart City Unified MCP Server initialized with {registered_count} services")
            self.is_initialized = True
            self.service_health = "healthy"
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Smart City Unified MCP Server: {e}")
            self.service_health = "unhealthy"
            return False
    
    async def shutdown(self):
        """Shutdown unified MCP server."""
        try:
            self.logger.info("🛑 Shutting down Smart City Unified MCP Server...")
            self.is_initialized = False
            self.service_health = "shutdown"
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown Smart City Unified MCP Server: {e}")
            return False
    
    async def get_server_capabilities(self) -> Dict[str, Any]:
        """Get unified MCP server capabilities."""
        base_capabilities = await super().get_server_capabilities()
        
        return {
            **base_capabilities,
            "server_type": "unified",
            "registered_services": list(self.registered_services.keys()),
            "total_tools": len(self.exposed_tools),
            "tool_naming_pattern": "{role}_{tool_name}"
        }
```

#### **2.2 Update Tool Handler:**

The unified server needs to route tool calls to the appropriate service. We need to ensure services expose their methods correctly.

**Option A:** Services expose MCP tools via their `soa_mcp.py` modules (already have `mcp_tools` dictionaries)

**Option B:** Services implement a standard `execute_mcp_tool(tool_name, parameters)` method

**Recommendation:** Use Option A (existing pattern) and enhance `register_service()` to extract tools from `service.mcp_tools` or `service.soa_mcp_module.mcp_tools`.

#### **2.3 Testing:**
- ✅ Verify all 9 services register successfully
- ✅ Test tool execution routing
- ✅ Verify tool naming (`{role}_{tool_name}`)
- ✅ Test error handling (unknown tool, service unavailable)

---

### **Phase 3: Update MCPClientManager (Day 5)**

**Goal:** Update MCPClientManager to use single endpoint instead of 8

#### **3.1 Update MCPClientManager:**

```python
# foundations/agentic_foundation/agent_sdk/mcp_client_manager.py

class MCPClientManager:
    """Manages MCP connections to Smart City roles with multi-tenant awareness."""
    
    def __init__(self, foundation_services: DIContainerService,
                 agentic_foundation: 'AgenticFoundationService'):
        # ... existing initialization ...
        
        # Unified Smart City MCP endpoint (NEW)
        self.smart_city_endpoint = "http://localhost:8000/mcp"
        
        # Legacy role mappings (DEPRECATED - for backward compatibility during migration)
        self.role_mappings = {
            "librarian": self.smart_city_endpoint,
            "data_steward": self.smart_city_endpoint,
            "conductor": self.smart_city_endpoint,
            "post_office": self.smart_city_endpoint,
            "security_guard": self.smart_city_endpoint,
            "nurse": self.smart_city_endpoint,
            "city_manager": self.smart_city_endpoint,
            "traffic_cop": self.smart_city_endpoint
        }
        
        # Active connection to unified server
        self.smart_city_connection = None
    
    async def connect_to_smart_city(self) -> bool:
        """Connect to unified Smart City MCP server."""
        try:
            self.logger.info(f"🔗 Connecting to unified Smart City MCP server: {self.smart_city_endpoint}")
            
            # Create MCP client connection
            # (Implementation depends on MCP client library)
            self.smart_city_connection = await self._create_mcp_client(self.smart_city_endpoint)
            
            self.logger.info("✅ Connected to unified Smart City MCP server")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to Smart City MCP server: {e}")
            return False
    
    async def call_tool(self, role: str, tool: str, params: Dict[str, Any], tenant_id: str = None) -> Dict[str, Any]:
        """
        Call MCP tool via unified server.
        
        Args:
            role: Role name (e.g., "librarian", "data_steward")
            tool: Tool name (without role prefix)
            params: Tool parameters
            tenant_id: Optional tenant ID for multi-tenant operations
            
        Returns:
            Tool execution result
        """
        try:
            # Ensure connection to unified server
            if not self.smart_city_connection:
                await self.connect_to_smart_city()
            
            # Construct namespaced tool name
            namespaced_tool = f"{role}_{tool}"
            
            # Call tool via unified server
            result = await self.smart_city_connection.call_tool(
                tool_name=namespaced_tool,
                parameters=params,
                tenant_context={"tenant_id": tenant_id} if tenant_id else None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to call tool {role}/{tool}: {e}")
            return {"success": False, "error": str(e)}
```

#### **3.2 Update Agent Base:**

Agents using `MCPClientManager` will automatically use the unified endpoint. No changes needed to agent code (backward compatible).

#### **3.3 Testing:**
- ✅ Test connection to unified server
- ✅ Test tool calls with namespaced tools
- ✅ Verify backward compatibility
- ✅ Test multi-tenant operations

---

### **Phase 4: Archive Individual MCP Servers (Day 5)**

**Goal:** Archive individual MCP servers to eliminate technical debt

#### **4.1 Archive Individual MCP Servers:**

```bash
# Create archive directory structure
mkdir -p backend/smart_city/services/{service_name}/archive/mcp_server

# Archive individual MCP servers
for service in city_manager conductor content_steward data_steward librarian nurse post_office security_guard traffic_cop; do
    if [ -d "backend/smart_city/services/$service/mcp_server" ]; then
        mv "backend/smart_city/services/$service/mcp_server" \
           "backend/smart_city/services/$service/archive/mcp_server_$(date +%Y%m%d)"
        echo "✅ Archived $service/mcp_server"
    fi
done
```

#### **4.2 Create Archive Documentation:**

```markdown
# Archived Individual MCP Servers

**Date:** 2025-01-XX
**Reason:** Replaced by unified Smart City MCP Server
**New Location:** `backend/smart_city/mcp_server/smart_city_mcp_server.py`

Individual MCP servers have been replaced by a unified Smart City MCP Server.
All tools are now available via single endpoint with namespaced tool names.

**Migration Guide:**
- Old: `http://localhost:8001` → `tool="upload_file"`
- New: `http://localhost:8000/mcp` → `tool="librarian_upload_file"`
```

#### **4.3 Update Documentation:**
- Update developer guide
- Update architecture diagrams
- Document unified pattern
- Create migration guide

---

### **Phase 5: Integration & Testing (Day 5)**

**Goal:** End-to-end testing and validation

#### **5.1 Integration Testing:**

```python
# tests/integration/test_unified_smart_city_mcp.py

async def test_unified_mcp_server_registration():
    """Test that all Smart City services register with unified MCP server."""
    # ... test implementation ...

async def test_tool_routing():
    """Test that tools are correctly routed to appropriate services."""
    # ... test implementation ...

async def test_namespaced_tool_names():
    """Test that all tools are correctly namespaced."""
    # ... test implementation ...

async def test_mcp_client_manager():
    """Test MCPClientManager with unified endpoint."""
    # ... test implementation ...
```

#### **5.2 Validation Checklist:**

- ✅ All 9 services register successfully
- ✅ All tools accessible via namespaced names
- ✅ Tool routing works correctly
- ✅ MCPClientManager uses single endpoint
- ✅ Agents can call tools via unified server
- ✅ Multi-tenant operations work
- ✅ Error handling works (unknown tool, service unavailable)
- ✅ Health checks work
- ✅ Individual MCP servers archived
- ✅ Documentation updated

---

## 📋 IMPLEMENTATION CHECKLIST

### **Day 1-2: Enhance MCPServerBase**
- [ ] Refactor `MCPServerBase` for multi-service pattern (clean break)
- [ ] Add `registered_services` dictionary
- [ ] Add `service_tool_prefixes` dictionary
- [ ] Add `tool_routing` dictionary
- [ ] Implement `register_service()` method
- [ ] Implement `_create_tool_handler()` method
- [ ] Refactor `execute_tool()` for multi-service routing only
- [ ] Add unit tests for multi-service support

### **Day 3-4: Create Unified Smart City MCP Server**
- [ ] Create `backend/smart_city/mcp_server/` directory
- [ ] Create `smart_city_mcp_server.py`
- [ ] Implement `SmartCityMCPServer` class
- [ ] Implement service registration logic
- [ ] Extract tools from service `mcp_tools` or `soa_mcp_module.mcp_tools`
- [ ] Implement tool routing
- [ ] Add error handling
- [ ] Add health check
- [ ] Add integration tests

### **Day 5: Update MCPClientManager & Archive**
- [ ] Update `MCPClientManager` to use unified endpoint
- [ ] Update `call_tool()` to construct namespaced tool names
- [ ] Add `connect_to_smart_city()` method
- [ ] Verify backward compatibility
- [ ] Archive individual MCP servers
- [ ] Create archive documentation
- [ ] Update main documentation
- [ ] Run end-to-end integration tests

---

## ⚠️ RISKS & MITIGATION

### **Risk 1: Service Tool Extraction**
**Risk:** Services may expose tools differently (some via `mcp_tools`, some via methods)  
**Mitigation:**
- Standardize on extracting from `service.mcp_tools` or `service.soa_mcp_module.mcp_tools`
- If not available, fall back to service method introspection
- Create adapter pattern if needed

### **Risk 2: Tool Name Conflicts**
**Risk:** Two services might have tools with the same name  
**Mitigation:**
- Namespacing prevents conflicts (`{role}_{tool_name}`)
- Validate tool names during registration
- Warn on conflicts

### **Risk 3: Service Initialization Order**
**Risk:** Services might not be initialized when MCP server registers them  
**Mitigation:**
- Register services after they're initialized
- Add health checks to verify service availability
- Implement lazy loading if needed

### **Risk 4: Breaking Changes**
**Risk:** Breaking changes for existing agents  
**Mitigation:**
- Charter is "break and fix" - clean refactor
- Update all dependent code in same sprint
- Clear migration path via tool namespacing

---

## ✅ SUCCESS CRITERIA

1. ✅ All 9 Smart City services register with unified MCP server
2. ✅ All tools accessible via namespaced names (`{role}_{tool_name}`)
3. ✅ MCPClientManager uses single endpoint
4. ✅ Tool routing works correctly
5. ✅ No breaking changes to agent code
6. ✅ Individual MCP servers archived
7. ✅ Documentation updated
8. ✅ Integration tests pass
9. ✅ Performance acceptable (< 200ms response time)

---

## 🚀 POST-REFACTORING BENEFITS

After refactoring:
- **1 process** instead of 8 (87.5% reduction)
- **1 port** instead of 8 (simpler configuration)
- **1 connection** for agents (reduced overhead)
- **Clear tool naming** (`{role}_{tool_name}`)
- **Centralized governance** (City Manager manages tool exposure)
- **Easier debugging** (single point of control)
- **Reduced technical debt** (archived individual servers)

---

## 📝 NOTES

- Other realms (Business Enablement, Experience, Journey, Solution) keep 1:1 MCP server pattern
- Unified pattern is **specific to Smart City** (platform orchestrator)
- Backward compatibility maintained during migration
- Tool namespacing ensures no conflicts
- City Manager can manage tool exposure centrally

---

**Status:** Ready for implementation  
**Approval:** Pending CTO review

