# Platform-Wide Patterns and Lessons Learned

**Date**: November 15, 2025  
**Purpose**: Identify patterns and lessons learned from yesterday's `RealmServiceBase` refactoring that should be applied more broadly across the platform.

---

## Executive Summary

Yesterday's work revealed **critical architectural patterns** that need to be enforced platform-wide:

1. ✅ **RealmServiceBase Usage**: All realm services must properly inherit and use `RealmServiceBase`
2. ✅ **Smart City Service Delegation**: Services must delegate to Smart City services, not reinvent functionality
3. ✅ **Public Works Abstraction Access**: Services must use `get_abstraction()` via Platform Gateway, not direct library imports
4. ✅ **Method Signature Alignment**: All service method calls must match actual Smart City service signatures
5. ✅ **Architectural Separation of Concerns**: Clear boundaries between Smart City services (Content Steward, Data Steward, Librarian)

---

## Pattern 1: RealmServiceBase Usage ✅

### ✅ Current Status: GOOD
- **51 services** inherit from `RealmServiceBase` (verified via grep)
- All enabling services in `business_enablement` properly inherit
- All solution, journey, and experience services properly inherit

### ✅ Correct Pattern (from `RealmServiceBase` docs):
```python
class MyService(RealmServiceBase):
    async def initialize(self):
        await super().initialize()
        
        # Get abstractions via Platform Gateway
        self.file_management = self.get_abstraction("file_management")
        
        # Discover Smart City services via Curator
        self.librarian = await self.get_librarian_api()
        self.content_steward = await self.get_content_steward_api()
        
        # Register with Curator
        await self.register_with_curator(...)
```

### ❌ Anti-Patterns to Avoid:
1. **Direct DI Container Access**:
   ```python
   # ❌ WRONG
   self.file_mgmt = self.di_container.get_abstraction("file_management")
   
   # ✅ CORRECT
   self.file_mgmt = self.get_abstraction("file_management")
   ```

2. **Direct Communication Foundation**:
   ```python
   # ❌ WRONG
   await self.communication_foundation.send_message(...)
   
   # ✅ CORRECT
   post_office = await self.get_post_office_api()
   await post_office.send_message(...)
   ```

### 🔍 Verification Needed:
- [ ] Check all services for direct `di_container.get_abstraction()` calls
- [ ] Check all services for direct `communication_foundation` access
- [ ] Verify all services call `super().initialize()` in their `initialize()` method

---

## Pattern 2: Smart City Service Delegation ✅

### ✅ Lesson Learned from Yesterday:
**Services must delegate to Smart City services, not reinvent functionality.**

### ✅ Correct Delegation Pattern:
```python
# ✅ CORRECT: Use RealmServiceBase helper methods
result = await self.store_document(document_data, metadata)
validated = await self.validate_data_quality(schema_data)
lineage_id = await self.track_data_lineage(lineage_data)
search_results = await self.search_documents(query, filters)
```

### ❌ Anti-Patterns (Custom Implementations):
```python
# ❌ WRONG: Custom storage
with open(f"/tmp/{file}", "w") as f:
    f.write(data)

# ❌ WRONG: Custom validation
if not data.get("required_field"):
    raise Error(...)

# ❌ WRONG: Custom search
results = [doc for doc in all_docs if query in doc.text]
```

### 🔍 Verification Needed:
- [ ] Search for `open()` calls in realm services (custom file I/O)
- [ ] Search for custom validation logic (if/else checks instead of `validate_data_quality`)
- [ ] Search for custom search implementations (list comprehensions, etc.)
- [ ] Verify all services use `RealmServiceBase` helper methods for:
  - Document storage → `store_document()`
  - Document retrieval → `retrieve_document()`
  - Document search → `search_documents()`
  - Data validation → `validate_data_quality()`
  - Lineage tracking → `track_data_lineage()`

---

## Pattern 3: Public Works Abstraction Access ✅

### ✅ Current Status: GOOD
- **No direct library imports** found in `business_enablement` services (verified via grep)
- Services use `self.get_abstraction()` pattern correctly
- Platform Gateway properly validates realm access

### ✅ Correct Pattern:
```python
# ✅ CORRECT: Get abstractions via Platform Gateway
self.analytics = self.get_abstraction("analytics")
self.file_management = self.get_abstraction("file_management")
self.llm = self.get_abstraction("llm")
```

### ❌ Anti-Patterns:
```python
# ❌ WRONG: Direct library imports
import redis
import httpx
import boto3
import meilisearch

# ❌ WRONG: Direct adapter instantiation
self.redis = RedisAdapter(...)
self.meilisearch = MeilisearchClient(...)
```

### 🔍 Verification Needed:
- [ ] Search for direct library imports in realm services:
  - `import redis`
  - `import httpx`
  - `import boto3`
  - `import meilisearch`
  - `import arangodb`
  - `import pymongo`
  - `import psycopg2`
  - `import sqlalchemy`
- [ ] Verify all infrastructure access goes through abstractions
- [ ] Check that abstractions are properly exposed via Platform Gateway

---

## Pattern 4: Method Signature Alignment ✅

### ✅ Lesson Learned from Yesterday:
**All service method calls must match actual Smart City service signatures.**

### ✅ Fixed Patterns (from Yesterday):
1. **`search_documents()`**:
   - **Before**: `search_documents(query: Dict[str, Any])`
   - **After**: `search_documents(query: str, filters: Optional[Dict] = None)`
   - **Calls**: `librarian.search_knowledge(query, filters)`

2. **`validate_data_quality()`**:
   - **Before**: `validate_data_quality(data: Any, validation_rules: Dict) -> Dict`
   - **After**: `validate_data_quality(schema_data: Dict[str, Any]) -> bool`
   - **Calls**: `data_steward.validate_schema(schema_data)`

3. **`track_data_lineage()`**:
   - **Before**: `track_data_lineage(source: str, destination: str, transformation: Dict) -> bool`
   - **After**: `track_data_lineage(lineage_data: Dict[str, Any]) -> str`
   - **Calls**: `data_steward.record_lineage(lineage_data)`

4. **`store_document()`**:
   - **Before**: `librarian.store_document()` ❌
   - **After**: `content_steward.process_upload()` ✅

### 🔍 Verification Needed:
- [ ] Audit all Smart City service method signatures
- [ ] Verify all `RealmServiceBase` helper methods match Smart City signatures
- [ ] Check for any remaining incorrect method calls:
  - `librarian.store_document()` → Should be `content_steward.process_upload()`
  - `librarian.search_documents()` → Should be `librarian.search_knowledge()`
  - `data_steward.validate_data()` → Should be `data_steward.validate_schema()`
  - `data_steward.track_lineage()` → Should be `data_steward.record_lineage()`
  - `data_steward.transform_data()` → Should be removed (TransformationEngineService owns it)

---

## Pattern 5: Architectural Separation of Concerns ✅

### ✅ Service Responsibilities (Now Correct):
- **Content Steward**: File/document storage, content processing, metadata extraction
- **Data Steward**: Data governance, policy management, lineage tracking, schema validation
- **Librarian**: Knowledge management, semantic search, content cataloging (NOT document storage)
- **TransformationEngineService**: Owns transformation logic (business logic, not governance)

### ✅ Method Delegation (Now Correct):
- `store_document()` → Content Steward `process_upload()`
- `retrieve_document()` → Content Steward `get_file()`
- `search_documents()` → Librarian `search_knowledge()`
- `validate_data_quality()` → Data Steward `validate_schema()`
- `track_data_lineage()` → Data Steward `record_lineage()`
- `transform_data()` → REMOVED (TransformationEngineService owns it)

### 🔍 Verification Needed:
- [ ] Audit all Smart City services to ensure they don't overlap responsibilities
- [ ] Verify Content Steward doesn't do knowledge search (Librarian's job)
- [ ] Verify Data Steward doesn't do data transformation (TransformationEngineService's job)
- [ ] Verify Librarian doesn't do document storage (Content Steward's job)

---

## Pattern 6: Public Works Foundation Creation Pattern ✅

### ✅ Critical Pattern (Established November 14, 2025):
**"Public Works Foundation creates everything; registries expose"**

This is the **foundational architectural pattern** for all infrastructure:

1. **Public Works Foundation creates** all adapters and abstractions
2. **Registries expose** (register and provide discovery) - they do NOT create
3. **Abstractions consume** adapters via dependency injection (constructor injection)
4. **Adapters encapsulate** infrastructure clients (no `.client` access)
5. **Platform Gateway validates** realm access
6. **Realms access** via `get_abstraction()`

### ✅ Correct Flow:
```
Public Works Foundation Service
    ↓ (_create_all_adapters())
Infrastructure Adapter (Layer 0)
    ↓ (injected into abstraction)
Infrastructure Abstraction (Layer 1)
    ↓ (_create_all_abstractions())
    ↓ (_initialize_and_register_abstractions())
Registry (exposure/discovery only)
    ↓ (exposed via Platform Gateway)
Realm Services (via get_abstraction())
```

### ✅ Correct Implementation Pattern:
```python
# ✅ CORRECT: Public Works Foundation creates everything
class PublicWorksFoundationService:
    async def _create_all_adapters(self):
        # Create all adapters
        self.consul_adapter = ConsulServiceDiscoveryAdapter(...)
        self.redis_adapter = RedisAdapter(...)
        # ... all adapters created here
    
    async def _create_all_abstractions(self):
        # Create abstractions with DI
        self.service_discovery_abstraction = ServiceDiscoveryAbstraction(
            adapter=self.consul_adapter  # Dependency injection
        )
        # ... all abstractions created here
    
    async def _initialize_and_register_abstractions(self):
        # Initialize registries (exposure-only)
        self.service_discovery_registry = ServiceDiscoveryRegistry()
        # Register abstractions
        self.service_discovery_registry.register_abstraction(
            "service_discovery", 
            self.service_discovery_abstraction
        )
```

### ✅ Registry Pattern (Exposure-Only):
```python
# ✅ CORRECT: Registry only exposes, doesn't create
class ServiceDiscoveryRegistry:
    def __init__(self):
        self.abstraction = None  # Will be registered, not created
    
    def register_abstraction(self, name: str, abstraction):
        """Register abstraction created by Public Works Foundation."""
        self.abstraction = abstraction
        self.is_ready = True
```

### ❌ Anti-Patterns:
1. **Registries creating adapters/abstractions** → Violates single source of truth
   ```python
   # ❌ WRONG: Registry creating adapter
   class ServiceDiscoveryRegistry:
       async def build_infrastructure(self):
           self.adapter = ConsulServiceDiscoveryAdapter(...)  # ❌
   ```
2. **Abstractions creating adapters internally** → Hard to test, tight coupling
   ```python
   # ❌ WRONG: Abstraction creating adapter
   class ServiceDiscoveryAbstraction:
       def __init__(self):
           self.adapter = ConsulServiceDiscoveryAdapter(...)  # ❌
   ```
3. **Adapter.client pattern** → Nested mocking complexity, breaks encapsulation
   ```python
   # ❌ WRONG: Direct client access
   result = self.adapter.client.some_method()  # ❌
   
   # ✅ CORRECT: Wrapper method
   result = self.adapter.some_method()  # ✅
   ```
4. **Direct adapter instantiation in services** → Bypasses Platform Gateway
   ```python
   # ❌ WRONG: Service creating adapter
   self.redis = RedisAdapter(...)  # ❌
   
   # ✅ CORRECT: Get via Platform Gateway
   self.cache = self.get_abstraction("cache")  # ✅
   ```

### 🔍 Verification Needed:
- [ ] Verify all adapters are created in `PublicWorksFoundationService._create_all_adapters()`
- [ ] Verify all abstractions are created in `PublicWorksFoundationService._create_all_abstractions()`
- [ ] Verify all registries are exposure-only (no `build_infrastructure()` or adapter creation)
- [ ] Verify all abstractions receive adapters via constructor injection (not internal creation)
- [ ] Verify all abstractions are registered with registries in `_initialize_and_register_abstractions()`
- [ ] Check for any registries that still create adapters/abstractions internally

---

## Pattern 7: Platform Gateway Exposure ✅

### ✅ Current Status: GOOD
- Platform Gateway properly validates realm access
- Abstractions are exposed via `REALM_ABSTRACTION_MAPPINGS`
- Services use `get_abstraction()` correctly

### ✅ Realm Abstraction Mappings:
```python
REALM_ABSTRACTION_MAPPINGS = {
    "smart_city": {
        "abstractions": [
            "session", "state", "auth", "authorization", "tenant",
            "file_management", "content_metadata", "content_schema", 
            "content_insights", "llm", "mcp", "policy", "messaging", "cache",
            "event_management", "api_gateway", "websocket", "event_bus"
        ],
        "byoi_support": True
    },
    "business_enablement": {
        "abstractions": [
            "content_metadata", "content_schema", "content_insights", 
            "file_management", "llm", "document_intelligence",
            "bpmn_processing", "sop_processing", "sop_enhancement",
            "strategic_planning", "financial_analysis"
        ],
        "byoi_support": False
    },
    # ... other realms
}
```

### 🔍 Verification Needed:
- [ ] Verify all abstractions used by realm services are in `REALM_ABSTRACTION_MAPPINGS`
- [ ] Check for any services requesting abstractions not in their realm's allowed list
- [ ] Verify Smart City services have full access (as intended)
- [ ] Verify other realms have appropriate limited access

---

## Pattern 8: Protocol Migration Pattern ✅

### ✅ Critical Pattern (Established November 13-14, 2025):
**Use `typing.Protocol` instead of `abc.ABC` for all abstraction contracts**

### ✅ Correct Pattern:
```python
# ✅ CORRECT: Use typing.Protocol
from typing import Protocol

class LLMProtocol(Protocol):
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response from LLM."""
        ...  # Protocol methods use ... not pass
```

### ❌ Anti-Pattern:
```python
# ❌ WRONG: Using abc.ABC
from abc import ABC, abstractmethod

class LLMProtocol(ABC):
    @abstractmethod
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        pass
```

### ✅ Benefits of Protocol:
1. **Structural typing** - No explicit inheritance required
2. **Duck typing** - Any class with matching methods implements the protocol
3. **Pythonic** - More aligned with Python's philosophy
4. **Type checking** - Works with mypy and other type checkers
5. **Flexibility** - Easier to evolve and extend

### 🔍 Verification Needed:
- [ ] Verify all protocol files use `typing.Protocol` (not `abc.ABC`)
- [ ] Search for remaining `from abc import ABC, abstractmethod` in protocol files
- [ ] Verify all protocol methods use `...` (not `pass`)
- [ ] Check for any explicit inheritance from protocols (not needed, but not wrong)

---

## Pattern 9: Adapter Encapsulation Pattern ✅

### ✅ Critical Pattern (Established November 14, 2025):
**Adapters must encapsulate raw clients - no direct `.client` access**

### ✅ Correct Pattern:
```python
# ✅ CORRECT: Encapsulated adapter
class RedisAdapter:
    def __init__(self, host: str, port: int):
        self._client = redis.Redis(host=host, port=port)  # Private
    
    def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        return self._client.get(key)  # Use private client
    
    def set(self, key: str, value: str) -> bool:
        """Set value in Redis."""
        return self._client.set(key, value)
```

### ❌ Anti-Patterns:
```python
# ❌ WRONG: Exposing client directly
class RedisAdapter:
    def __init__(self, host: str, port: int):
        self.client = redis.Redis(host=host, port=port)  # ❌ Public
    
    # External code does: adapter.client.get(key)  # ❌ Breaks encapsulation
```

```python
# ❌ WRONG: Nested client access
class SomeAbstraction:
    def __init__(self, adapter: RedisAdapter):
        self.adapter = adapter
    
    def get_value(self, key: str):
        return self.adapter.client.get(key)  # ❌ Direct client access
```

### ✅ Benefits:
1. **Encapsulation** - Raw client details hidden
2. **Testability** - Easy to mock adapter methods
3. **Swappability** - Can swap adapters without breaking abstractions
4. **Consistency** - All infrastructure access through well-defined methods

### 🔍 Verification Needed:
- [ ] Verify all adapters use `self._client` (private) instead of `self.client` (public)
- [ ] Search for `.client` access in abstractions and services
- [ ] Verify all adapter methods are wrapper methods (not direct client passthrough)
- [ ] Check for any backward-compatibility aliases (`self.client = self._client`) that should be removed

---

## Pattern 10: Service Discovery Registry Pattern ✅

### ✅ Special Case Pattern (Refactored November 14, 2025):
**ServiceDiscoveryRegistry was a special case that violated the pattern - now fixed**

### ✅ Lesson Learned:
Even "special cases" must follow the architectural pattern. The comment "Service Discovery Registry is a special case - it still creates adapters because Consul is self-hosted" was **incorrect**. All registries must be exposure-only.

### ✅ Before (Anti-Pattern):
```python
# ❌ WRONG: Registry creating adapter
class ServiceDiscoveryRegistry:
    async def build_infrastructure(self, config):
        self.adapter = await self._build_consul_adapter(config)  # ❌
        self.abstraction = ServiceDiscoveryAbstraction(self.adapter)  # ❌
```

### ✅ After (Correct Pattern):
```python
# ✅ CORRECT: Public Works Foundation creates, registry exposes
# In PublicWorksFoundationService:
async def _create_all_adapters(self):
    self.consul_service_discovery_adapter = ConsulServiceDiscoveryAdapter(...)

async def _create_all_abstractions(self):
    self.service_discovery_abstraction = ServiceDiscoveryAbstraction(
        adapter=self.consul_service_discovery_adapter  # DI
    )

async def _initialize_and_register_abstractions(self):
    self.service_discovery_registry = ServiceDiscoveryRegistry()
    self.service_discovery_registry.register_abstraction(
        "service_discovery", 
        self.service_discovery_abstraction
    )
```

### ✅ Key Insight:
**No exceptions to the pattern** - even if infrastructure is "self-hosted" vs "managed service", the pattern remains the same. The difference is in **where** the adapter is created (Public Works Foundation), not **how** it's exposed (via registry).

### 🔍 Verification Needed:
- [ ] Verify ServiceDiscoveryRegistry is now exposure-only
- [ ] Check for any other "special case" registries that might violate the pattern
- [ ] Verify all registries follow the same pattern (no exceptions)

---

## Pattern 11: SOA API Pattern ✅

### ✅ Correct Pattern:
```python
# ✅ CORRECT: Define clear, atomic SOA APIs
async def parse_file(self, file_path: str, format: str) -> ParsedDocument:
    '''Parse file into structured format (SOA API).'''
    # Complete implementation using Smart City services
    librarian = await self.get_librarian_api()
    content_steward = await self.get_content_steward_api()
    # ... orchestrate and return result
```

### ✅ Service Registration:
```python
await self.register_with_curator(
    capabilities=["file_parsing", "format_conversion"],
    soa_apis=["parse_file", "detect_file_type"],
    mcp_tools=["parse_file_tool", "detect_file_type_tool"]
)
```

### 🔍 Verification Needed:
- [ ] Verify all services register their SOA APIs with Curator
- [ ] Verify SOA APIs are atomic and focused (3-5 per service)
- [ ] Verify MCP tools wrap SOA APIs (for realm services that expose MCP)

---

## Comprehensive Audit Checklist

### Phase 1: RealmServiceBase Usage
- [ ] Search for `self.di_container.get_abstraction()` (should be `self.get_abstraction()`)
- [ ] Search for `self.communication_foundation` direct access (should use Smart City services)
- [ ] Verify all services call `super().initialize()`
- [ ] Verify all services inherit from `RealmServiceBase` (not `RealmBase` or other bases)

### Phase 2: Smart City Service Delegation
- [ ] Search for `open()` calls (custom file I/O)
- [ ] Search for custom validation logic (if/else checks)
- [ ] Search for custom search implementations
- [ ] Verify services use `RealmServiceBase` helper methods

### Phase 3: Public Works Abstraction Access
- [ ] Search for direct library imports (`import redis`, `import httpx`, etc.)
- [ ] Search for direct adapter instantiation
- [ ] Verify all infrastructure access goes through abstractions

### Phase 4: Method Signature Alignment
- [ ] Audit all Smart City service method signatures
- [ ] Verify all `RealmServiceBase` helper methods match Smart City signatures
- [ ] Check for incorrect method calls (e.g., `librarian.store_document()`)

### Phase 5: Architectural Separation of Concerns
- [ ] Audit Smart City services for overlapping responsibilities
- [ ] Verify Content Steward doesn't do knowledge search
- [ ] Verify Data Steward doesn't do data transformation
- [ ] Verify Librarian doesn't do document storage

### Phase 6: Public Works Foundation Patterns
- [ ] Verify all adapters are created in `PublicWorksFoundationService._create_all_adapters()`
- [ ] Verify all abstractions are created in `PublicWorksFoundationService._create_all_abstractions()`
- [ ] Verify all registries are exposure-only (no adapter/abstraction creation)
- [ ] Verify all abstractions receive adapters via constructor injection
- [ ] Verify all abstractions are registered with registries
- [ ] Check for any registries that still create adapters/abstractions internally

### Phase 7: Protocol Migration
- [ ] Verify all protocol files use `typing.Protocol` (not `abc.ABC`)
- [ ] Search for remaining `from abc import ABC, abstractmethod` in protocol files
- [ ] Verify all protocol methods use `...` (not `pass`)

### Phase 8: Adapter Encapsulation
- [ ] Verify all adapters use `self._client` (private) instead of `self.client` (public)
- [ ] Search for `.client` access in abstractions and services
- [ ] Verify all adapter methods are wrapper methods
- [ ] Check for backward-compatibility aliases that should be removed

### Phase 9: Platform Gateway Exposure
- [ ] Verify all abstractions are in `REALM_ABSTRACTION_MAPPINGS`
- [ ] Check for services requesting unauthorized abstractions
- [ ] Verify realm access is properly validated

### Phase 10: Service Discovery Registry Pattern
- [ ] Verify ServiceDiscoveryRegistry is exposure-only
- [ ] Check for any other "special case" registries that violate the pattern
- [ ] Verify all registries follow the same pattern (no exceptions)

### Phase 11: SOA API Pattern
- [ ] Verify all services register SOA APIs with Curator
- [ ] Verify SOA APIs are atomic and focused
- [ ] Verify MCP tools wrap SOA APIs (where applicable)

---

## Priority Actions

### 🔴 High Priority (Architectural Issues):
1. **Audit all services for direct `di_container.get_abstraction()` calls**
2. **Audit all services for direct library imports**
3. **Audit all Smart City service method signatures**
4. **Verify all services use `RealmServiceBase` helper methods**

### 🟡 Medium Priority (Pattern Compliance):
1. **Verify all registries are exposure-only (no adapter/abstraction creation)**
2. **Verify all protocol files use `typing.Protocol` (not `abc.ABC`)**
3. **Verify all adapters encapsulate clients (no `.client` access)**
4. **Verify all abstractions are exposed via Platform Gateway**
5. **Verify all services register SOA APIs with Curator**
6. **Check for custom implementations (file I/O, validation, search)**

### 🟢 Low Priority (Documentation/Verification):
1. **Document all Smart City service responsibilities**
2. **Create audit scripts to verify patterns**
3. **Update service templates with correct patterns**

---

## Next Steps

1. **Create audit scripts** to automatically detect anti-patterns
2. **Run comprehensive audit** across all realm services
3. **Fix identified issues** using break-and-fix approach (as yesterday)
4. **Update service templates** with correct patterns
5. **Document patterns** in architecture documentation

---

## References

- `docs/11-12/REALM_SERVICE_BASE_AUDIT.md` - Original audit findings
- `docs/11-12/BREAK_AND_FIX_COMPLETE.md` - Refactoring completion
- `docs/11-12/STANDARDIZED_ABSTRACTION_ADAPTER_PATTERN.md` - Abstraction patterns
- `docs/11-12/REGISTRY_REFACTORING_PATTERN.md` - Registry refactoring pattern
- `docs/11-12/COMPLETE_ARCHITECTURAL_CHANGES.md` - Complete architectural changes
- `docs/11-12/SERVICE_DISCOVERY_REGISTRY_REFACTORING_COMPLETE.md` - ServiceDiscoveryRegistry refactoring
- `docs/11-12/CLIENT_ACCESS_REMOVAL_COMPLETE.md` - Adapter encapsulation pattern
- `docs/11-12/PROTOCOL_MIGRATION_COMPLETE.md` - Protocol migration completion
- `bases/realm_service_base.py` - Base class with pattern documentation
- `platform_infrastructure/infrastructure/platform_gateway.py` - Platform Gateway implementation
- `foundations/public_works_foundation/public_works_foundation_service.py` - Public Works Foundation implementation

---

## Summary of New Patterns (November 14, 2025)

1. **Pattern 6 (Updated)**: Public Works Foundation Creation Pattern - "Public Works Foundation creates everything; registries expose"
2. **Pattern 8 (New)**: Protocol Migration Pattern - Use `typing.Protocol` instead of `abc.ABC`
3. **Pattern 9 (New)**: Adapter Encapsulation Pattern - No direct `.client` access
4. **Pattern 10 (New)**: Service Discovery Registry Pattern - No exceptions to the architectural pattern

---

**Last Updated**: November 15, 2025

