# Abstraction Access Pattern - Architecture Review

**Date**: November 15, 2025  
**Status**: ✅ **Architecture Pattern Documented**

---

## Current Architecture for Abstraction Access

### Four-Tier Access Pattern (for Orchestrators)

Orchestrators should access capabilities in this order:

1. **Enabling Services (Business Enablement Realm)** - First Priority
2. **SOA APIs (Smart City and Other Realms)** - Second Priority
3. **Platform Gateway (Infrastructure Abstractions)** - Third Priority  
4. **Fail Gracefully** - Clear error messages

### Three-Tier Access Pattern (for Enabling Services)

Enabling services should access capabilities in this order:

1. **SOA APIs (Smart City and Other Realms)** - First Priority
2. **Platform Gateway (Infrastructure Abstractions)** - Second Priority  
3. **Fail Gracefully** - Clear error messages

---

## 1. Enabling Services (First Priority - Orchestrators Only)

### Pattern: Check for Enabling Services from Business Enablement Realm

**Orchestrators** coordinate enabling services to deliver use cases. These are discovered via Curator.

**Access Pattern** (Orchestrators):
```python
# ✅ CORRECT: Discover enabling services via Curator
file_parser = await self.get_enabling_service("FileParserService")
data_analyzer = await self.get_enabling_service("DataAnalyzerService")
workflow_manager = await self.get_enabling_service("WorkflowManagerService")

# Use enabling service SOA APIs
parsed_doc = await file_parser.parse_file(file_id)
analysis = await data_analyzer.analyze_data(data_id)
```

**Available Enabling Services** (via `OrchestratorBase.get_enabling_service()`):
- `FileParserService` - File parsing and format conversion
- `DataAnalyzerService` - Data analysis and insights
- `WorkflowManagerService` - Workflow orchestration
- `SOPBuilderService` - SOP creation and management
- `RoadmapGenerationService` - Roadmap generation
- `POCGenerationService` - POC generation
- `MetricsCalculatorService` - KPI calculation
- `VisualizationEngineService` - Visualization generation
- And more...

**Why Enabling Services First?**
- Orchestrators coordinate enabling services (their primary purpose)
- Enabling services provide business logic and use case capabilities
- Discovered via Curator (service registry)
- Most common access pattern for orchestrators

---

## 2. SOA APIs (Second Priority for Orchestrators, First Priority for Enabling Services)

### Pattern: Check for SOA APIs from Smart City and Other Realms

**Smart City Services** expose SOA APIs that wrap infrastructure abstractions with business logic.

**Access Pattern**:
```python
# ✅ CORRECT: Discover Smart City services via convenience methods
librarian = await self.get_librarian_api()
content_steward = await self.get_content_steward_api()
data_steward = await self.get_data_steward_api()

# Use SOA APIs
file_record = await content_steward.get_file(file_id)
metadata = await librarian.get_knowledge_item(item_id)
```

**Available SOA API Methods** (from `RealmServiceBase`):
- `await self.get_librarian_api()` - Librarian service
- `await self.get_content_steward_api()` - Content Steward service
- `await self.get_data_steward_api()` - Data Steward service
- `await self.get_security_guard_api()` - Security Guard service
- `await self.get_post_office_api()` - Post Office service
- `await self.get_conductor_api()` - Conductor service
- `await self.get_traffic_cop_api()` - Traffic Cop service
- `await self.get_nurse_api()` - Nurse service
- `await self.get_city_manager_api()` - City Manager service

**Why SOA APIs First?**
- Encapsulate business logic
- Provide realm-specific validation
- Handle cross-cutting concerns (auth, logging, metrics)
- Enable future service mesh integration

---

## 3. Platform Gateway (Third Priority for Orchestrators, Second Priority for Enabling Services)

### Pattern: Access Infrastructure Abstractions via Platform Gateway

If SOA APIs aren't available or don't provide the needed capability, access infrastructure abstractions directly via Platform Gateway.

**Access Pattern**:
```python
# ✅ CORRECT: Get abstractions through validated Platform Gateway
self.file_management = self.get_abstraction("file_management")
self.content_metadata = self.get_abstraction("content_metadata")
self.llm = self.get_abstraction("llm")
```

**Available Abstractions** (realm-dependent):
- `business_enablement` realm: `file_management`, `content_metadata`, `llm`, `document_intelligence`, `bpmn_processing`, `sop_processing`, `strategic_planning`, `financial_analysis`
- `smart_city` realm: Full access to all abstractions
- `solution` realm: `llm`, `content_metadata`, `file_management`
- `journey` realm: `llm`, `session`, `content_metadata`

**Why Platform Gateway?**
- Validates realm access (governance)
- Provides audit trail
- Enables BYOI (Bring Your Own Infrastructure)
- Single source of truth for access policies

---

## 4. Fail Gracefully (Fourth Priority for Orchestrators, Third Priority for Enabling Services)

### Pattern: Clear Error Messages When Capabilities Unavailable

If neither SOA APIs nor Platform Gateway provide the needed capability, fail gracefully with clear error messages.

**Access Pattern**:
```python
# ✅ CORRECT: Fail gracefully with clear error
librarian = await self.get_librarian_api()
if not librarian:
    raise RuntimeError(
        f"Librarian service required but not available. "
        f"Ensure Smart City services are initialized and registered with Curator."
    )

# Or return structured error response
if not librarian:
    return {
        "success": False,
        "error": "Librarian service not available",
        "error_code": "SERVICE_UNAVAILABLE",
        "message": "Librarian service required but not found. Check Curator registration."
    }
```

---

## Complete Pattern Examples

### Orchestrator Pattern (Four-Tier)

```python
async def process_document(self, file_id: str) -> Dict[str, Any]:
    """
    Process document using four-tier access pattern (orchestrator).
    
    1. Try Enabling Service first (FileParserService)
    2. Try SOA API (Content Steward)
    3. Try Platform Gateway (file_management abstraction)
    4. Fail gracefully with clear error
    """
    # Tier 1: Try Enabling Service first
    file_parser = await self.get_enabling_service("FileParserService")
    if file_parser:
        try:
            parsed_doc = await file_parser.parse_file(file_id)
            if parsed_doc:
                return {"success": True, "data": parsed_doc}
        except Exception as e:
            self.logger.warning(f"FileParserService failed: {e}, trying SOA API")
    
    # Tier 2: Try SOA API
    content_steward = await self.get_content_steward_api()
    if content_steward:
        try:
            file_record = await content_steward.get_file(file_id)
            if file_record:
                return {"success": True, "data": file_record}
        except Exception as e:
            self.logger.warning(f"Content Steward SOA API failed: {e}, trying Platform Gateway")
    
    # Tier 3: Try Platform Gateway
    try:
        file_management = self.get_abstraction("file_management")
        if file_management:
            file_record = await file_management.get_file(file_id)
            if file_record:
                return {"success": True, "data": file_record}
    except Exception as e:
        self.logger.warning(f"Platform Gateway access failed: {e}")
    
    # Tier 4: Fail gracefully
    return {
        "success": False,
        "error": "File retrieval failed",
        "error_code": "FILE_RETRIEVAL_FAILED",
        "message": (
            f"Could not retrieve file {file_id}. "
            f"Tried FileParserService, Content Steward service, and file_management abstraction - all unavailable. "
            f"Check service initialization and Platform Gateway configuration."
        )
    }
```

### Enabling Service Pattern (Three-Tier)

```python
async def process_document(self, file_id: str) -> Dict[str, Any]:
    """
    Process document using three-tier access pattern (enabling service).
    
    1. Try SOA API first (Content Steward)
    2. Try Platform Gateway (file_management abstraction)
    3. Fail gracefully with clear error
    """
    # Tier 1: Try SOA API first
    content_steward = await self.get_content_steward_api()
    if content_steward:
        try:
            file_record = await content_steward.get_file(file_id)
            if file_record:
                return {"success": True, "data": file_record}
        except Exception as e:
            self.logger.warning(f"Content Steward SOA API failed: {e}, trying Platform Gateway")
    
    # Tier 2: Try Platform Gateway
    try:
        file_management = self.get_abstraction("file_management")
        if file_management:
            file_record = await file_management.get_file(file_id)
            if file_record:
                return {"success": True, "data": file_record}
    except Exception as e:
        self.logger.warning(f"Platform Gateway access failed: {e}")
    
    # Tier 3: Fail gracefully
    return {
        "success": False,
        "error": "File retrieval failed",
        "error_code": "FILE_RETRIEVAL_FAILED",
        "message": (
            f"Could not retrieve file {file_id}. "
            f"Content Steward service and file_management abstraction both unavailable. "
            f"Check service initialization and Platform Gateway configuration."
        )
    }
```

---

## Anti-Patterns (Don't Do These)

### ❌ Direct Infrastructure Access (Bypasses SOA APIs)
```python
# ❌ WRONG: Direct infrastructure access
file_management = self.di_container.get_abstraction("file_management")
```

### ❌ Direct Public Works Access (Bypasses Platform Gateway)
```python
# ❌ WRONG: Direct Public Works access
file_management = self.public_works_foundation.get_abstraction("file_management")
```

### ❌ Silent Failures
```python
# ❌ WRONG: Silent failure
if not service:
    return None  # No error message!
```

### ❌ No Fallback Strategy
```python
# ❌ WRONG: No fallback
service = await self.get_librarian_api()
result = await service.get_item(id)  # Fails if service is None
```

---

## Benefits of This Pattern

1. **Encapsulation**: SOA APIs hide infrastructure complexity
2. **Flexibility**: Can use SOA APIs or abstractions depending on needs
3. **Resilience**: Graceful degradation when services unavailable
4. **Observability**: Clear error messages help debugging
5. **Governance**: Platform Gateway enforces access policies
6. **Future-Ready**: Supports service mesh and BYOI patterns

---

## Migration Notes

**Phase 1 Fixes** already implemented this pattern in:
- Insights Orchestrator Workflows: Uses `data_steward.get_file()` and `data_steward.get_asset_metadata()` SOA APIs

**Phase 2** should apply this pattern to:
- All orchestrator methods returning `None`
- All enabling service methods returning `None`
- Any direct infrastructure access that should use SOA APIs first

---

**Status**: ✅ Pattern documented and ready for Phase 2 implementation

