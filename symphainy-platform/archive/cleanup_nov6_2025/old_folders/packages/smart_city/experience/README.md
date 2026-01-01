# Experience MCP Server Package

## 🎯 **Architecture Overview**

The Experience MCP Server Package is the **connective tissue** between frontend and backend, orchestrating user experience across the Smart City platform.

## 🏗️ **Package Structure**

### **Experience Manager MCP Package** (Orchestrator)
```
experience/
├── roles/
│   └── experience_manager_role.py          # Experience Manager Role
├── services/
│   └── experience_service.py               # Experience Service
└── integrations/
    └── experience_mcp.py                   # Experience MCP Server
```

### **3 Sub-MCP Server Packages**

#### **1. Ambassador MCP Server Package**
```
experience/ambassador_mcp/
├── roles/
│   └── ambassador_role.py                  # Ambassador Role (Agentic Communication)
├── services/
│   └── ambassador_service.py               # Ambassador Service
└── integrations/
    └── ambassador_mcp.py                   # Ambassador MCP Server
```

#### **2. Frontend MCP Server Package**
```
experience/frontend_mcp/
├── roles/
│   └── frontend_role.py                    # Frontend Role (UI Integration)
├── services/
│   └── frontend_service.py                 # Frontend Service
└── integrations/
    └── frontend_mcp.py                     # Frontend MCP Server
```

#### **3. Guide Agent MCP Server Package**
```
experience/guide_agent_mcp/
├── roles/
│   └── guide_agent_role.py                 # Guide Agent Role (User Guidance)
├── services/
│   └── guide_agent_service.py              # Guide Agent Service
└── integrations/
    └── guide_agent_mcp.py                  # Guide Agent MCP Server
```

## 🎯 **Key Components**

### **Experience Manager** (Orchestration)
- **Role**: Defines WHAT user experience capabilities are needed
- **Service**: Implements HOW to orchestrate the experience
- **MCP Server**: Connects frontend to backend via MCP

### **Ambassador** (Agentic Communication)
- **Role**: Defines WHAT agentic communication capabilities are needed
- **Service**: Implements HOW to use Post Office for agent communication
- **MCP Server**: Provides agentic communication infrastructure

### **Frontend** (UI Integration)
- **Role**: Defines WHAT frontend integration capabilities are needed
- **Service**: Implements HOW to integrate with symphainy-frontend
- **MCP Server**: Provides frontend-backend communication

### **Guide Agent** (User Guidance)
- **Role**: Defines WHAT user guidance capabilities are needed
- **Service**: Implements HOW to guide users through their journey
- **MCP Server**: Provides user guidance and journey planning

## 🔗 **Integration Points**

### **Frontend Integration**
- **symphainy-frontend** ↔ **Frontend MCP Server** ↔ **Experience Manager MCP**

### **Backend Integration**
- **Experience Manager MCP** ↔ **Delivery Manager MCP** ↔ **3 Pillars**

### **Agent Coordination**
- **Experience Manager MCP** ↔ **Ambassador MCP** ↔ **Guide Agent MCP**

## 🚀 **Implementation Status**

### **✅ Scaffolded**
- Experience Manager Role
- Experience Service
- Experience MCP Server
- Ambassador Role (Experience Layer)
- Frontend Role (Experience Layer)
- Guide Agent Role (Experience Layer)

### **🔄 Next Steps**
1. **Create Services** for Ambassador, Frontend, Guide Agent
2. **Create MCP Servers** for each sub-package
3. **Implement Business Logic** for each component
4. **Connect to symphainy-frontend**
5. **Test End-to-End Flow**

## 📋 **Usage**

### **Start Experience Manager MCP Server**
```python
from backend.packages.smart_city.experience.integrations.experience_mcp import ExperienceMCP

# Initialize and start the MCP server
experience_mcp = ExperienceMCP()
experience_mcp.start_server()
```

### **Call Experience Manager Tools**
```python
# Orchestrate user experience
result = experience_mcp.call_tool("orchestrate_user_experience", {
    "user_id": "user123",
    "journey_type": "poc_discovery"
})

# Coordinate frontend integration
result = experience_mcp.call_tool("coordinate_frontend_integration", {
    "frontend_request": "load_dashboard",
    "user_context": {"pillar": "content"}
})
```

## 🎯 **Architecture Benefits**

1. **Clean Separation**: Frontend and backend concerns are clearly separated
2. **MCP Integration**: Standard MCP protocol for all communication
3. **Modular Design**: Each component can be developed and tested independently
4. **Scalable**: Easy to add new experience components
5. **Maintainable**: Clear role/service separation with MCP integration

## 🔧 **Development Notes**

- **Scaffolded**: All components are scaffolded and ready for business logic implementation
- **MCP Compliant**: All components follow MCP protocol standards
- **Micro-Modular**: Each file is under 350 lines for maintainability
- **Testable**: Clear interfaces for unit and integration testing

