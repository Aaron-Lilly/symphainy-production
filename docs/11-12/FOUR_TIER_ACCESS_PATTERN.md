# Four-Tier Access Pattern - Updated Architecture

**Date**: November 15, 2025  
**Status**: ✅ **Pattern Updated for Orchestrators**

---

## Architecture Update

After review, we identified that **orchestrators primarily coordinate enabling services** from the business_enablement realm. This requires a **four-tier access pattern** for orchestrators.

---

## Four-Tier Access Pattern (Orchestrators)

### Tier 1: Enabling Services (Business Enablement Realm)
**Priority**: First  
**Method**: `await self.get_enabling_service("ServiceName")`  
**Via**: Curator discovery

**Why First?**
- Orchestrators coordinate enabling services (their primary purpose)
- Most common access pattern for orchestrators
- Enabling services provide business logic and use case capabilities

**Examples**:
- `FileParserService` - File parsing
- `DataAnalyzerService` - Data analysis
- `WorkflowManagerService` - Workflow orchestration
- `SOPBuilderService` - SOP creation
- `RoadmapGenerationService` - Roadmap generation

### Tier 2: SOA APIs (Smart City and Other Realms)
**Priority**: Second  
**Method**: `await self.get_*_api()` (e.g., `get_content_steward_api()`)  
**Via**: Curator discovery

**Why Second?**
- Smart City services provide infrastructure-level capabilities
- Encapsulate business logic and validation
- Used when enabling services don't provide the capability

**Examples**:
- `content_steward.get_file()` - File retrieval
- `librarian.get_knowledge_item()` - Metadata retrieval
- `conductor.execute_workflow()` - Workflow execution

### Tier 3: Platform Gateway (Infrastructure Abstractions)
**Priority**: Third  
**Method**: `self.get_abstraction("abstraction_name")`  
**Via**: Platform Gateway validation

**Why Third?**
- Direct infrastructure access (bypasses business logic)
- Used when SOA APIs don't provide the capability
- Requires realm access validation

**Examples**:
- `file_management.get_file()` - Direct file access
- `content_metadata.get_content_metadata()` - Direct metadata access
- `llm.generate_text()` - Direct LLM access

### Tier 4: Fail Gracefully
**Priority**: Fourth  
**Action**: Return structured error or raise exception

**Why Last?**
- Clear error messages help debugging
- Prevents silent failures
- Enables observability

---

## Three-Tier Access Pattern (Enabling Services)

Enabling services use a **three-tier pattern** (they don't call other enabling services):

1. **SOA APIs** (Smart City services)
2. **Platform Gateway** (infrastructure abstractions)
3. **Fail Gracefully**

---

## Complete Example: Orchestrator

```python
async def analyze_document(self, file_id: str) -> Dict[str, Any]:
    """
    Analyze document using four-tier access pattern.
    """
    # Tier 1: Try Enabling Service first
    data_analyzer = await self.get_enabling_service("DataAnalyzerService")
    if data_analyzer:
        try:
            analysis = await data_analyzer.analyze_data(file_id)
            if analysis:
                return {"success": True, "data": analysis}
        except Exception as e:
            self.logger.warning(f"DataAnalyzerService failed: {e}, trying SOA API")
    
    # Tier 2: Try SOA API
    content_steward = await self.get_content_steward_api()
    if content_steward:
        try:
            file_record = await content_steward.get_file(file_id)
            if file_record:
                # Basic analysis using file content
                return {"success": True, "data": {"basic_analysis": file_record}}
        except Exception as e:
            self.logger.warning(f"Content Steward failed: {e}, trying Platform Gateway")
    
    # Tier 3: Try Platform Gateway
    try:
        file_management = self.get_abstraction("file_management")
        if file_management:
            file_record = await file_management.get_file(file_id)
            if file_record:
                return {"success": True, "data": {"file": file_record}}
    except Exception as e:
        self.logger.warning(f"Platform Gateway failed: {e}")
    
    # Tier 4: Fail gracefully
    return {
        "success": False,
        "error": "Document analysis failed",
        "error_code": "ANALYSIS_FAILED",
        "message": (
            f"Could not analyze document {file_id}. "
            f"Tried DataAnalyzerService, Content Steward, and file_management - all unavailable."
        )
    }
```

---

## Service-Specific Patterns

### File Parsing (Orchestrator)
1. `FileParserService.parse_file()` (enabling service)
2. `content_steward.get_file()` (SOA API)
3. `file_management.get_file()` (Platform Gateway)
4. Fail gracefully

### Data Analysis (Orchestrator)
1. `DataAnalyzerService.analyze_data()` (enabling service)
2. Platform Gateway (if needed)
3. Fail gracefully

### Workflow Execution (Orchestrator)
1. `WorkflowManagerService.execute_workflow()` (enabling service)
2. `conductor.execute_workflow()` (SOA API)
3. Fail gracefully

### LLM Operations (Orchestrator)
1. Platform Gateway `llm` abstraction (no enabling service or SOA API)
2. Fail gracefully

---

## Benefits

1. **Correct Layering**: Orchestrators coordinate enabling services first
2. **Resilience**: Multiple fallback options
3. **Observability**: Clear error messages at each tier
4. **Flexibility**: Can use enabling services, SOA APIs, or abstractions
5. **Consistency**: Same pattern across all orchestrators

---

**Status**: ✅ Pattern updated and ready for Phase 2 implementation
