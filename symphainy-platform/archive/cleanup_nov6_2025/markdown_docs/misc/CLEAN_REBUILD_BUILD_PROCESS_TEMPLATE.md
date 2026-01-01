# 🏗️ Clean Rebuild Build Process Template

## Overview

This document establishes the **master build process** for clean rebuilds that ensures proper infrastructure mapping from the start, eliminating the need for infrastructure corrections later.

## ✅ **Master Service Versions Established**

The following services are now the **master versions** with proper infrastructure mapping:

### **🔐 Security Guard Service**
- **Master**: `backend/smart_city/services/security_guard/security_guard_service.py`
- **Infrastructure**: Authentication (Supabase + JWT), Authorization (Supabase), Session Management (Redis), Tenant Management (Supabase), Policy Management (Supabase)
- **Status**: ✅ Complete with corrected infrastructure mapping

### **📊 Data Steward Service**
- **Master**: `backend/smart_city/services/data_steward/data_steward_service.py`
- **Infrastructure**: File Management (GCS + Supabase), Metadata Management (Supabase), Content Metadata (ArangoDB)
- **Status**: ✅ Complete with corrected infrastructure mapping

### **📝 Content Steward Service**
- **Master**: `backend/smart_city/services/content_steward/content_steward_service.py`
- **Infrastructure**: Content Processing (In-memory), Metadata Management (In-memory), Format Conversion (In-memory), Data Optimization (In-memory), Content Validation (In-memory), Lineage Tracking (In-memory)
- **Status**: ✅ Complete with proper infrastructure mapping from start

## 📁 **Archived Versions**

All old implementations have been moved to `archive/smart_city_services_old/`:
- `security_guard_service_old.py`
- `security_guard_service_original.py`
- `post_office_service_old.py`

## 🏗️ **Build Process Template**

### **Step 1: Define Infrastructure Mapping**
```python
# Define the correct infrastructure mapping for this service
self.define_infrastructure_mapping({
    "messaging": "Redis",           # Messaging via Redis
    "event_management": "Redis",    # Event management via Redis
    "session_management": "Redis"   # Session management via Redis
})
```

### **Step 2: Initialize Infrastructure Connections**
```python
async def _initialize_infrastructure_connections(self):
    """Initialize connections to proper infrastructure abstractions."""
    try:
        # Get Public Works Foundation
        public_works_foundation = self.get_public_works_foundation()
        if not public_works_foundation:
            raise Exception("Public Works Foundation not available")
        
        # Get each required abstraction
        self.messaging_abstraction = await public_works_foundation.get_abstraction("messaging")
        self.event_management_abstraction = await public_works_foundation.get_abstraction("event_management")
        self.session_management_abstraction = await public_works_foundation.get_abstraction("session_management")
        
        self.is_infrastructure_connected = True
        
    except Exception as e:
        self.logger.error(f"❌ Failed to connect to proper infrastructure: {str(e)}")
        raise e
```

### **Step 3: Implement SOA API Exposure**
```python
async def _initialize_soa_api_exposure(self):
    """Initialize SOA API exposure for Smart City capabilities."""
    self.soa_apis = {
        "service_method": {
            "endpoint": "/api/service/method",
            "method": "POST",
            "description": "Service method description",
            "parameters": ["param1", "param2"]
        }
    }
```

### **Step 4: Implement MCP Tool Integration**
```python
async def _initialize_mcp_tool_integration(self):
    """Initialize MCP tool integration for service operations."""
    self.mcp_tools = {
        "service_tool": {
            "name": "service_tool",
            "description": "Service tool description",
            "parameters": ["param1", "param2"]
        }
    }
```

### **Step 5: Validate Infrastructure Mapping**
```python
async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
    """Validate that proper infrastructure mapping is working correctly."""
    validation_results = {}
    
    # Test each infrastructure connection
    for abstraction_name, expected_infrastructure in self.required_abstractions.items():
        try:
            abstraction = self.infrastructure_connections.get(abstraction_name)
            if abstraction:
                health_result = await abstraction.health_check()
                validation_results[f"{abstraction_name}_{expected_infrastructure.lower()}"] = True
        except Exception as e:
            validation_results[f"{abstraction_name}_{expected_infrastructure.lower()}"] = False
    
    validation_results["overall_status"] = all(validation_results.values())
    return validation_results
```

## 🎯 **Infrastructure Mapping Guidelines**

### **Correct Infrastructure Assignments**

| Service Type | Infrastructure | Database | Use Case |
|--------------|----------------|----------|----------|
| **File Storage** | GCS | Google Cloud Storage | Scalable file storage |
| **File Metadata** | Supabase | PostgreSQL | Structured file metadata |
| **Content Metadata** | ArangoDB | ArangoDB | Graph-based content relationships |
| **Authentication** | Supabase + JWT | PostgreSQL + JWT | User authentication |
| **Authorization** | Supabase | PostgreSQL | Access control |
| **Session Management** | Redis | Redis | Session storage |
| **Tenant Management** | Supabase | PostgreSQL | Multi-tenant data |
| **Policy Management** | Supabase | PostgreSQL | Security policies |
| **Messaging** | Redis | Redis | Inter-service communication |
| **Event Management** | Redis | Redis | Event streaming |

### **❌ Common Mistakes to Avoid**

1. **File Storage in Supabase** → Use GCS instead
2. **Tenant Data in Redis** → Use Supabase instead
3. **Content Metadata in Supabase** → Use ArangoDB instead
4. **Session Data in Supabase** → Use Redis instead

## 🔄 **Service Implementation Pattern**

### **Base Class Structure**
```python
class ServiceName(SmartCityRoleBase, ServiceNameProtocol):
    """Service Name - Clean Rebuild with Proper Infrastructure"""
    
    def __init__(self, di_container: Any):
        super().__init__(
            service_name="ServiceName",
            role_name="service_name",
            di_container=di_container
        )
        
        # Infrastructure Abstractions
        self.abstraction1 = None
        self.abstraction2 = None
        
        # Service State
        self.is_infrastructure_connected = False
        
        # SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
```

### **Initialization Pattern**
```python
async def initialize(self) -> bool:
    try:
        # 1. Initialize infrastructure connections
        await self._initialize_infrastructure_connections()
        
        # 2. Initialize SOA API exposure
        await self._initialize_soa_api_exposure()
        
        # 3. Initialize MCP tool integration
        await self._initialize_mcp_tool_integration()
        
        # 4. Register capabilities
        capabilities = await self._register_service_capabilities()
        await self.register_capability("ServiceName", capabilities)
        
        self.is_initialized = True
        return True
        
    except Exception as e:
        self.logger.error(f"❌ Failed to initialize service: {str(e)}")
        return False
```

## ✅ **Validation Checklist**

Before considering a service complete, ensure:

- [ ] **Infrastructure mapping defined correctly from start**
- [ ] **All required abstractions connected**
- [ ] **SOA API exposure implemented**
- [ ] **MCP tool integration implemented**
- [ ] **Infrastructure validation passes**
- [ ] **All core functionality working**
- [ ] **Service capabilities registered**
- [ ] **Old versions archived**
- [ ] **Master version established**

## 🚀 **Next Steps**

1. **Apply this template to remaining Smart City services**:
   - City Manager
   - Conductor
   - Librarian
   - Nurse
   - Traffic Cop

2. **Use the established master versions as reference**

3. **Archive all old implementations immediately**

4. **Validate infrastructure mapping before deployment**

## 📋 **Benefits of This Approach**

- ✅ **No infrastructure corrections needed**
- ✅ **Proper mapping from the start**
- ✅ **Eliminates technical debt**
- ✅ **Prevents parallel implementations**
- ✅ **Consistent architecture across all services**
- ✅ **Ready for production deployment**

---

**🎉 This build process template ensures clean rebuilds with proper infrastructure mapping from the start, eliminating the need for corrections and establishing a solid foundation for all future service implementations.**
