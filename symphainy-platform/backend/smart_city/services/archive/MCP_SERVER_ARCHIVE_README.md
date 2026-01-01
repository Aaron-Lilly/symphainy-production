# Archived Individual MCP Servers

**Date:** 2025-01-15  
**Reason:** Replaced by unified Smart City MCP Server  
**New Location:** `backend/smart_city/mcp_server/smart_city_mcp_server.py`

---

## 📋 Overview

Individual MCP servers for each Smart City service have been **archived** and replaced by a unified Smart City MCP Server.

### **Before (8 Individual MCP Servers):**
```
backend/smart_city/services/
├── city_manager/mcp_server/city_manager_mcp_server.py       (port 8007)
├── conductor/mcp_server/conductor_mcp_server.py              (port 8003)
├── content_steward/mcp_server/ (if existed)
├── data_steward/mcp_server/data_steward_mcp_server.py       (port 8002)
├── librarian/mcp_server/librarian_mcp_server.py              (port 8001)
├── nurse/mcp_server/nurse_mcp_server.py                      (port 8006)
├── post_office/mcp_server/post_office_mcp_server.py         (port 8004)
├── security_guard/mcp_server/security_guard_mcp_server.py   (port 8005)
└── traffic_cop/mcp_server/traffic_cop_mcp_server.py        (port 8008)
```

### **After (1 Unified MCP Server):**
```
backend/smart_city/
└── mcp_server/
    ├── __init__.py
    └── smart_city_mcp_server.py                              (port 8000)
```

---

## 🔄 Migration Guide

### **Tool Naming Changes:**

**OLD Pattern (Individual Servers):**
```python
# Each service had its own endpoint
await mcp_client.call_tool(
    endpoint="http://localhost:8001",  # Librarian
    tool="upload_file",
    params={...}
)
```

**NEW Pattern (Unified Server):**
```python
# All services use unified endpoint with namespaced tools
await mcp_client.call_tool(
    endpoint="http://localhost:8000/mcp",  # Unified
    tool="librarian_upload_file",  # Namespaced!
    params={...}
)
```

### **Tool Name Mapping:**

All tools are now **namespaced by role**:

| Old Tool Name | New Tool Name |
|--------------|---------------|
| `upload_file` (Librarian) | `librarian_upload_file` |
| `validate_schema` (Data Steward) | `data_steward_validate_schema` |
| `authenticate_user` (Security Guard) | `security_guard_authenticate_user` |
| `execute_workflow` (Conductor) | `conductor_execute_workflow` |
| `send_message` (Post Office) | `post_office_send_message` |
| `manage_session` (Traffic Cop) | `traffic_cop_manage_session` |
| `collect_telemetry` (Nurse) | `nurse_collect_telemetry` |
| `bootstrap_platform` (City Manager) | `city_manager_bootstrap_platform` |

**Pattern:** `{role}_{tool_name}`

---

## 📦 Archived Locations

All individual MCP servers have been archived to:

```
backend/smart_city/services/{service}/archive/mcp_server_YYYYMMDD/
```

**Archived Services:**
- `city_manager/archive/mcp_server_20250115/`
- `conductor/archive/mcp_server_20250115/`
- `data_steward/archive/mcp_server_20250115/`
- `librarian/archive/mcp_server_20250115/`
- `nurse/archive/mcp_server_20250115/`
- `post_office/archive/mcp_server_20250115/`
- `security_guard/archive/mcp_server_20250115/`
- `traffic_cop/archive/mcp_server_20250115/`

---

## ✅ Benefits of Unified Server

### **Operational:**
- ✅ **1 process** instead of 8 (87.5% reduction)
- ✅ **1 port** instead of 8 (simpler configuration)
- ✅ **Single health check** endpoint
- ✅ **Easier debugging** (single point of control)
- ✅ **Reduced resource footprint**

### **Agent:**
- ✅ **1 connection** instead of 8 (simpler client)
- ✅ **Clear tool naming** (`{role}_{tool_name}`)
- ✅ **Easier tool discovery** (all Smart City tools in one place)
- ✅ **Reduced connection overhead**

### **Platform:**
- ✅ **Aligns with "Smart City as orchestrator" vision**
- ✅ **City Manager can centrally manage tool exposure**
- ✅ **Single governance point** for Smart City MCP
- ✅ **Enables Agentic IDP** (agents managing agents via MCP)

---

## 🔗 Related Files

- **Unified MCP Server:** `backend/smart_city/mcp_server/smart_city_mcp_server.py`
- **MCP Server Base:** `bases/mcp_server_base.py` (refactored for multi-service)
- **MCP Client Manager:** `foundations/agentic_foundation/agent_sdk/mcp_client_manager.py` (updated for unified endpoint)
- **Refactoring Plan:** `SMART_CITY_UNIFIED_MCP_REFACTORING_PLAN.md`

---

## 📝 Notes

- Archived MCP servers are kept for **reference only**
- They are **no longer used** in the platform
- All tools are now exposed via the unified server
- Tool names are automatically namespaced by role
- No breaking changes for agents (MCPClientManager handles translation)

---

**Status:** ✅ **Archived - Replaced by Unified Smart City MCP Server**






