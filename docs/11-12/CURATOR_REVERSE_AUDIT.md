# Curator Foundation Reverse Audit

**Date**: December 2024  
**Status**: 🔍 Audit Complete - Usage Patterns Identified

---

## Executive Summary

Performed reverse audit to understand how realms and foundations actually use Curator Foundation. Found **multiple registration paths** with different formats, revealing validation misalignment.

### Key Findings

- ✅ **SOA API Registration**: Separate registry (`register_soa_api()`) - working correctly
- ✅ **MCP Tool Registration**: Separate registry (`register_mcp_tool()`) - working correctly  
- ⚠️ **Service Registration**: Two paths with format conversion - validation happens after conversion
- ⚠️ **Capability Registration**: Called both directly and indirectly - format mismatch
- ❌ **Validation Timing**: Validates converted format, not input format

---

## Registration Paths Analysis

### 1. Service Registration (via City Manager)

**Path**: `CityManagerService` → `register_service()` → `_validate_service_metadata()` → `capability_registry.register_capability()`

**Location**: `backend/smart_city/services/city_manager/modules/realm_orchestration.py:208`

**What Gets Registered**:
```python
await curator.register_service(
    service_instance=service_instance,
    service_metadata={
        "service_name": curator_service_name,  # e.g., "Nurse", "TrafficCop"
        "service_type": "smart_city",           # Always "smart_city"
        "realm": "smart_city",                  # Always "smart_city"
        "capabilities": getattr(service_instance, "capabilities", []),  # List of strings
        "startup_policy": "lazy"
    }
)
```

**What Happens Inside `register_service()`**:
```python
# Line 310-321: Converts string capabilities to dict format
capabilities = service_metadata.get("capabilities", [])
for capability_name in capabilities:
    capability_dict = {
        "name": capability_name,
        "interface": f"I{service_name}",      # ADDED by curator
        "service_type": service_metadata.get("service_type", "unknown"),
        "endpoints": [],                       # ADDED by curator (empty)
        "tools": []                            # ADDED by curator (empty)
    }
    await self.capability_registry.register_capability(service_name, capability_dict)
```

**Issue**: 
- Comment says "REQUIRED fields: interface, endpoints, tools (validated by _validate_capability_structure)"
- But these fields are **added by curator**, not provided by services
- Validation happens **after** conversion, so it validates the converted format, not the input

---

### 2. SOA API Registration (Direct from Services)

**Path**: `Service.soa_mcp.register_capabilities()` → `curator_foundation.register_soa_api()`

**Location**: `backend/smart_city/services/*/modules/soa_mcp.py`

**What Gets Registered**:
```python
# From Nurse Service (typical pattern)
for api_name, api_config in self.service.soa_apis.items():
    endpoint = api_config.get("endpoint", f"/api/v1/nurse/{api_name}")
    handler = getattr(self.service, api_name, None)
    metadata = {
        "method": api_config.get("method", "POST"),
        "description": api_config.get("description", f"Nurse {api_name} API")
    }
    await curator_foundation.register_soa_api(
        service_name=self.service.service_name,
        api_name=api_name,
        endpoint=endpoint,
        handler=handler,
        metadata=metadata
    )
```

**Storage**: `curator_foundation_service.soa_api_registry` (dict keyed by `f"{service_name}.{api_name}"`)

**Status**: ✅ **Working correctly** - separate registry, no validation issues

---

### 3. MCP Tool Registration (Direct from Services)

**Path**: `Service.soa_mcp.register_capabilities()` → `curator_foundation.register_mcp_tool()`

**Location**: `backend/smart_city/services/*/modules/soa_mcp.py`

**What Gets Registered**:
```python
# From Nurse Service (typical pattern)
for tool_name, tool_config in self.service.mcp_tools.items():
    handler = getattr(self, f"_mcp_{tool_name}", None)
    tool_definition = {
        "name": tool_config.get("name", tool_name),
        "description": tool_config.get("description", f"Nurse {tool_name} tool"),
        "endpoint": f"/mcp/{tool_name}",
        "handler": handler
    }
    metadata = {
        "service_name": self.service.service_name,
        "tool_name": tool_name
    }
    await curator_foundation.register_mcp_tool(
        tool_name=tool_name,
        tool_definition=tool_definition,
        metadata=metadata
    )
```

**Storage**: `curator_foundation_service.mcp_tool_registry` (dict keyed by `tool_name`)

**Status**: ✅ **Working correctly** - separate registry, no validation issues

---

### 4. Capability Registration (Direct from Services)

**Path**: `Service.register_capability()` → `curator_foundation.register_capability()`

**Location**: Various services call this directly (e.g., `ContentStewardService`, `SecurityGuardService`)

**What Gets Registered**:
```python
# From Content Steward Service
capabilities = await self.soa_mcp_module.register_content_steward_capabilities()
await self.register_capability("ContentStewardService", capabilities)
```

**What `capabilities` Contains** (from `utilities.get_service_capabilities()`):
```python
{
    "service_name": "content_steward",
    "service_type": "content_processing",  # NOT "smart_city"
    "realm": "smart_city",
    "capabilities": ["content_processing", "policy_enforcement", ...],  # List of strings
    "detailed_capabilities": {...},  # Dict with nested structures
    "soa_api_exposure": {"apis": [...], "endpoints": [...]},
    "mcp_server_integration": {"tools": [...], ...},
    "infrastructure": {...},
    "access_pattern": "api_via_smart_city_gateway",
    "version": "3.0"
}
```

**Issue**: 
- Services call `register_capability()` with full service metadata dict
- But `register_capability()` expects a capability dict (not service metadata)
- This is a **different method** than what `register_service()` calls internally

---

## Registry Inventory

### Registries in Curator Foundation

| Registry | Method | Storage | Purpose | Status |
|----------|--------|---------|---------|--------|
| **Service Registry** | `register_service()` | `registered_services` dict | Service instances + metadata | ⚠️ Format conversion issue |
| **Capability Registry** | `register_capability()` | `capability_registry` service | Capability definitions | ⚠️ Validation mismatch |
| **SOA API Registry** | `register_soa_api()` | `soa_api_registry` dict | SOA API endpoints | ✅ Working |
| **MCP Tool Registry** | `register_mcp_tool()` | `mcp_tool_registry` dict | MCP tool definitions | ✅ Working |
| **Agent Capability Registry** | `register_agent_capabilities()` | `agent_capabilities` dict | Agent capabilities | ✅ Working |

### Other Registries (Not in Curator)

| Registry | Location | Purpose | Should Go Through Curator? |
|----------|----------|---------|---------------------------|
| **Communication Registry** | `communication_foundation/infrastructure_registry/communication_registry.py` | Communication channels | ❓ Unknown |
| **Service Discovery Registry** | `public_works_foundation/infrastructure_registry/service_discovery_registry.py` | Consul/Istio/Linkerd | ✅ Already integrated |
| **Specialization Registry** | `agentic_foundation/specialization_registry.py` | Agent specializations | ✅ Used by Curator |
| **AGUI Schema Registry** | `agentic_foundation/agui_schema_registry.py` | AGUI schemas | ✅ Used by Curator |
| **Tool Registry** | `agentic_foundation/infrastructure_enablement/tool_registry_service.py` | Tool definitions | ❓ Unknown |

---

## Registration Flow Analysis

### Current Flow (City Manager Path)

```
CityManagerService
  └─> register_service(service_instance, service_metadata)
       ├─> _validate_service_metadata(service_metadata)  # Validates input format
       ├─> Convert capabilities: ["cap1", "cap2"] → [{"name": "cap1", "interface": "...", ...}]
       └─> capability_registry.register_capability(service_name, capability_dict)
            └─> _validate_capability_structure(capability_dict)  # Validates converted format
```

**Problem**: Validation happens on converted format, not input format.

### Current Flow (Direct Service Path)

```
Service.soa_mcp.register_capabilities()
  ├─> register_soa_api()  # ✅ Separate registry
  ├─> register_mcp_tool()  # ✅ Separate registry
  └─> register_capability()  # ⚠️ Different method signature
       └─> ??? (Need to check what this actually does)
```

**Problem**: `register_capability()` is called with service metadata dict, but expects capability dict.

---

## Actual Service Reporting Formats

### Format 1: City Manager Registration (via `register_service()`)

```python
{
    "service_name": "Nurse",
    "service_type": "smart_city",  # Always "smart_city"
    "realm": "smart_city",          # Always "smart_city"
    "capabilities": ["health_monitoring", "telemetry_collection"],  # List of strings
    "startup_policy": "lazy"
}
```

### Format 2: Direct Service Capability Reporting (via `get_service_capabilities()`)

```python
{
    "service_name": "NurseService",
    "service_type": "health_monitor",  # Actual service type
    "realm": "smart_city",
    "capabilities": ["health_monitoring", "telemetry_collection"],  # List of strings
    "infrastructure_connections": {...},
    "soa_apis": 5,  # Count
    "mcp_tools": 3  # Count
}
```

### Format 3: Content Steward Detailed Format

```python
{
    "service_name": "content_steward",
    "service_type": "content_processing",
    "realm": "smart_city",
    "capabilities": ["content_processing", "policy_enforcement", ...],  # List of strings
    "detailed_capabilities": {  # Dict with nested structures
        "content_processing": {...},
        "format_conversion": {...},
        ...
    },
    "soa_api_exposure": {
        "apis": [...],
        "endpoints": [...]
    },
    "mcp_server_integration": {
        "tools": [...],
        "server_enabled": True
    },
    "infrastructure": {...},
    "access_pattern": "api_via_smart_city_gateway",
    "version": "3.0"
}
```

### Format 4: Librarian Dict Format

```python
{
    "service_name": "LibrarianService",
    "role_name": "librarian",
    "capabilities": {  # Dict structure (not list)
        "knowledge_management": {...},
        "search": {...},
        "content_organization": {...}
    },
    "soa_apis": 4,
    "mcp_tools": 2
}
```

---

## Validation Issues Identified

### Issue 1: Validation Happens After Format Conversion

**Location**: `curator_foundation_service.py:310-321`

**Problem**:
- `register_service()` converts string capabilities to dict format
- Comment says fields are "REQUIRED" but they're actually **added by curator**
- `_validate_capability_structure()` validates the **converted** format, not the **input** format
- Services provide string capabilities, but validation expects dict with `interface`, `endpoints`, `tools`

**Impact**: 
- Validation is checking the wrong thing
- Services can't provide the "required" fields because curator adds them

### Issue 2: Service Metadata Validation Too Strict

**Location**: `curator_foundation_service.py:376-405` (already updated, but need to verify)

**Problem**:
- Was restricting `service_type` to 4 values: `["smart_city", "business_enablement", "experience", "agentic"]`
- But services use: `"content_processing"`, `"health_monitor"`, `"security"`, etc.
- These are **service categories**, not **realm types**

**Status**: ✅ **Already fixed** in recent update

### Issue 3: Capability Structure Validation Too Strict

**Location**: `capability_registry_service.py:_validate_capability_structure()`

**Problem**:
- Was requiring `interface`, `endpoints`, `tools`
- But curator adds these fields during `register_service()`
- Services don't provide them

**Status**: ✅ **Already fixed** - now flexible

### Issue 4: Method Signature Mismatch

**Problem**:
- Services call `self.register_capability("ContentStewardService", capabilities)` 
- `PlatformCapabilitiesMixin.register_capability()` expects: `(capability_name: str, capability_data: Dict[str, Any])`
- But services pass: `(service_name: str, service_metadata: Dict[str, Any])`
- This is a **signature mismatch** - service name is not capability name, service metadata is not capability data

**Location**: 
- `bases/mixins/platform_capabilities_mixin.py:235`
- `backend/smart_city/services/content_steward/content_steward_service.py:101`
- `backend/smart_city/services/security_guard/security_guard_service.py:162`

**Impact**: 
- Services are registering service metadata as if it were a capability
- This may work if the capability registry accepts flexible formats, but it's semantically incorrect

**Action Required**: ⚠️ **Clarify intent** - Should services register capabilities or service metadata?

---

## Recommendations

### 1. Fix Validation Timing

**Current**: Validates converted format  
**Should**: Validate input format, then convert

**Change**:
```python
# Validate input format FIRST
validation_result = await self._validate_service_metadata(service_metadata)
if not validation_result["valid"]:
    return {"success": False, "error": f"Invalid service metadata: {validation_result['errors']}"}

# THEN convert format
capabilities = service_metadata.get("capabilities", [])
for capability_name in capabilities:
    capability_dict = {
        "name": capability_name,
        "interface": f"I{service_name}",  # Added by curator
        "endpoints": [],  # Added by curator
        "tools": []  # Added by curator
    }
    # No need to validate converted format - we control it
    await self.capability_registry.register_capability(service_name, capability_dict)
```

### 2. Clarify Registration Methods

**Issue**: Multiple methods with similar names:
- `register_service()` - registers service instance
- `register_capability()` - registers capability (called internally and directly)
- `register_soa_api()` - registers SOA API
- `register_mcp_tool()` - registers MCP tool

**Recommendation**: 
- Document which method to use when
- Consider renaming `register_capability()` to `_register_capability()` if it's internal-only
- Or create separate public methods: `register_service_capabilities()` vs `register_capability_definition()`

### 3. Standardize Service Metadata Format

**Current**: Multiple formats (City Manager vs Direct Service vs Detailed)

**Recommendation**:
- Accept all formats (flexible validation)
- Normalize internally to standard format
- Document expected formats

### 4. Separate SOA/MCP Registration from Capability Registration

**Current**: Services call `register_capabilities()` which does:
1. Register SOA APIs
2. Register MCP tools
3. Return capabilities dict

**Recommendation**:
- Keep SOA/MCP registration separate (already working)
- Make capability registration optional or separate
- Clarify what "register capabilities" means

---

## Questions for Review

1. **Should `register_capability()` be public or internal?**
   - Currently called both internally (by `register_service()`) and directly (by services)
   - Should services call it directly, or only through `register_service()`?

2. **What is the relationship between `register_service()` and `register_capability()`?**
   - `register_service()` calls `register_capability()` internally
   - But services also call `register_capability()` directly
   - Are these the same thing or different?

3. **Should SOA APIs and MCP tools be part of capability registration?**
   - Currently registered separately
   - Should they be included in capability definitions?

4. **What registries should go through Curator?**
   - Communication Registry?
   - Tool Registry?
   - Others?

---

## Next Steps

1. ✅ **Review this audit** - Confirm findings
2. ⚠️ **Investigate `register_capability()` method signature** - Check what it actually expects
3. ⚠️ **Fix validation timing** - Validate input format, not converted format
4. ⚠️ **Clarify registration methods** - Document which method to use when
5. ⚠️ **Test with actual services** - Verify all registration paths work

---

**Last Updated**: December 2024

