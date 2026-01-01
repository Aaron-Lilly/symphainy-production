# CapabilityDefinition Review and Evolution Proposal

## Current State Analysis

### Current CapabilityDefinition Structure

```python
@dataclass
class CapabilityDefinition:
    service_name: str
    interface_name: str  # ❌ MISLEADING: Comment says "Protocol name" but field name suggests interface
    endpoints: List[str]  # ⚠️ AMBIGUOUS: Which contract do these belong to?
    tools: List[str]  # ⚠️ AMBIGUOUS: Which contract do these belong to?
    description: str
    realm: str
    version: str = "1.0.0"
    registered_at: str = None
    semantic_mapping: Optional[Dict[str, Any]] = None
    contracts: Optional[Dict[str, Any]] = None
```

### Issues Identified

1. **`interface_name` is misleading**
   - Field name suggests "interface" but we use **Protocols**, not interfaces
   - Comment says "Protocol name (e.g., "IFileParser")" but that's wrong
   - Should be actual Protocol class name like `NurseServiceProtocol`, not `INurseService`

2. **`endpoints` and `tools` are ambiguous**
   - These are separate fields, but they should be part of `contracts`
   - A capability can have multiple contracts (SOA API, REST API, MCP tool)
   - Each contract has its own endpoints/tools
   - Current structure doesn't clearly show which contract owns which endpoints/tools

3. **Missing `capability_name`**
   - What uniquely identifies this capability?
   - Services can have multiple capabilities (e.g., "health_monitoring", "telemetry_collection")
   - Currently inferred from description or other fields

4. **Structure doesn't reflect architecture**
   - Architecture uses: **Protocols** (not interfaces), **Contracts** (multiple invocation methods)
   - Current structure mixes concepts (endpoints/tools separate from contracts)

---

## Architecture Alignment

### What is a Capability?

From the architecture:
- **Capability**: Something a service can do (e.g., "parse_file", "monitor_health")
- **Protocol**: The contract that defines HOW the capability is invoked (e.g., `NurseServiceProtocol`)
- **Contract**: A specific way to invoke the capability (SOA API, REST API, MCP tool)
- **Semantic Mapping**: How the capability maps to domain/user-facing concepts

### Capability Registration Pattern

From `RealmServiceBase.register_with_curator()`:
```python
capabilities=[
    {
        "name": "file_parsing",  # ✅ Capability name
        "protocol": "IFileParser",  # ❌ Should be "FileParserProtocol" or protocol class name
        "description": "Parse files into structured formats",
        "semantic_mapping": {
            "domain_capability": "content.upload_file",
            "semantic_api": "/api/v1/content-pillar/upload-file"
        },
        "contracts": {
            "soa_api": {...},
            "rest_api": {...},
            "mcp_tool": {...}
        }
    }
]
```

---

## Proposed Evolution

### Option A: Refactor Current Structure (Recommended)

**Key Changes:**
1. Rename `interface_name` → `protocol_name` (with clear documentation)
2. Remove `endpoints` and `tools` as separate fields (move to contracts)
3. Add `capability_name` field
4. Make `contracts` required (not optional) - a capability must have at least one contract
5. Clarify that `protocol_name` should be the actual Protocol class name

**New Structure:**
```python
@dataclass
class CapabilityDefinition:
    """
    Definition of a service capability.
    
    A capability is something a service can do, defined by:
    - A unique name (capability_name)
    - A protocol that defines the contract (protocol_name)
    - One or more contracts (ways to invoke the capability)
    - Semantic mapping (how it maps to domain/user concepts)
    """
    # Core identification
    capability_name: str  # ✅ NEW: Unique identifier (e.g., "file_parsing", "health_monitoring")
    service_name: str  # Which service provides this capability
    protocol_name: str  # ✅ RENAMED: Protocol class name (e.g., "NurseServiceProtocol")
    
    # Description
    description: str
    realm: str  # Which realm this capability belongs to
    
    # Contracts (REQUIRED - capability must have at least one way to invoke it)
    contracts: Dict[str, Any]  # ✅ REQUIRED: At least one contract (soa_api, rest_api, mcp_tool)
    # Each contract can have:
    #   - "soa_api": {api_name, endpoint, method, handler, metadata}
    #   - "rest_api": {endpoint, method, handler, metadata}
    #   - "mcp_tool": {tool_name, tool_definition, metadata}
    
    # Semantic mapping (optional but recommended)
    semantic_mapping: Optional[Dict[str, Any]] = None
    # Structure:
    #   {
    #       "domain_capability": "content.upload_file",  # Domain concept
    #       "semantic_api": "/api/v1/content-pillar/upload-file",  # User-facing API
    #       "user_journey": "upload_document_for_analysis"  # User journey step
    #   }
    
    # Versioning and metadata
    version: str = "1.0.0"
    registered_at: str = None
    
    # REMOVED: endpoints, tools (now part of contracts)
    # REMOVED: interface_name (renamed to protocol_name)
```

**Benefits:**
- ✅ Clear separation: capability name, protocol, contracts
- ✅ Contracts are required (capability must be invokable)
- ✅ Endpoints/tools are part of contracts (where they belong)
- ✅ Protocol name is clear (actual Protocol class name)
- ✅ Semantic mapping is optional but structured

**Migration Path:**
- Update all existing code to use `protocol_name` instead of `interface_name`
- Extract `capability_name` from description or generate from service_name + contract
- Move endpoints/tools into contracts
- Make contracts required

---

### Option B: More Explicit Structure

**Alternative with explicit contract types:**
```python
@dataclass
class SOAAPIContract:
    api_name: str
    endpoint: str
    method: str
    handler: Any
    metadata: Dict[str, Any]

@dataclass
class RESTAPIContract:
    endpoint: str
    method: str
    handler: Any
    metadata: Dict[str, Any]

@dataclass
class MCPToolContract:
    tool_name: str
    tool_definition: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class CapabilityDefinition:
    capability_name: str
    service_name: str
    protocol_name: str  # Protocol class name
    description: str
    realm: str
    
    # Contracts (at least one required)
    soa_api: Optional[SOAAPIContract] = None
    rest_api: Optional[RESTAPIContract] = None
    mcp_tool: Optional[MCPToolContract] = None
    
    semantic_mapping: Optional[Dict[str, Any]] = None
    version: str = "1.0.0"
    registered_at: str = None
```

**Benefits:**
- ✅ Type-safe contracts
- ✅ Clear structure
- ✅ Validation at dataclass level

**Drawbacks:**
- ⚠️ More complex migration
- ⚠️ Less flexible (can't add new contract types easily)

---

## Recommendation

**Recommend Option A** (refactored current structure) because:
1. ✅ Minimal breaking changes
2. ✅ Clear and flexible
3. ✅ Aligns with architecture (Protocols, not interfaces)
4. ✅ Contracts are required (capability must be invokable)
5. ✅ Easy migration path

**Key Principles:**
1. **Protocols, not interfaces** - Use actual Protocol class names
2. **Contracts are required** - A capability must have at least one way to invoke it
3. **Capability name is explicit** - Not inferred from other fields
4. **Endpoints/tools belong to contracts** - Not separate fields

---

## Migration Steps

1. **Update CapabilityDefinition model**
   - Rename `interface_name` → `protocol_name`
   - Add `capability_name` field
   - Remove `endpoints` and `tools` fields
   - Make `contracts` required (not Optional)

2. **Update all registration code**
   - Use protocol class names (e.g., `NurseServiceProtocol`)
   - Extract/generate capability names
   - Move endpoints/tools into contracts

3. **Update validation**
   - Ensure contracts is not empty
   - Validate protocol_name is a valid Protocol class name
   - Validate capability_name is unique per service

4. **Update documentation**
   - Clarify Protocols vs interfaces
   - Document contract structure
   - Provide examples

---

## Questions for Review

1. **Should `capability_name` be required?** (Recommend: YES)
2. **Should `contracts` be required?** (Recommend: YES - capability must be invokable)
3. **Should we validate `protocol_name` exists?** (Recommend: YES - check Protocol registry)
4. **How should we handle backward compatibility?** (Recommend: Migration script + deprecation period)







