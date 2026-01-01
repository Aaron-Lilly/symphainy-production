# Insights Pillar Plan Evolution Analysis
## Comparing Current Plan to Updated Full Vision

**Date:** December 20, 2025  
**Status:** 📋 **Analysis & Evolution Plan**  
**Purpose:** Identify what needs to evolve in Insights Pillar plan to align with full vision

---

## 🎯 **Executive Summary**

The current Insights Pillar implementation plan is **90% aligned** with the updated vision. Key evolution needed:
1. **Data Solution Orchestrator Integration** - Use same pattern as Content Pillar
2. **Semantic Data Access Pattern** - Use `orchestrate_data_expose()` instead of direct access
3. **Dependencies** - ✅ All required dependencies already in `pyproject.toml`

---

## ✅ **What's Already Aligned**

### **1. Enabling Services** ✅
- ✅ DataAnalyzerService with EDA tools (Phase 1)
- ✅ VisualizationEngineService with AGUI components (Phase 2)
- ✅ SemanticEnrichmentGateway (Phase 4)
- ✅ All use semantic data layer (not raw parsed data)

### **2. Agents** ✅
- ✅ InsightsBusinessAnalysisAgent (Phase 3)
- ✅ Specialized HF Agents (Phase 5)
- ✅ All use Agentic Foundation SDK (not CrewAI)

### **3. Architecture Principles** ✅
- ✅ Semantic data layer security boundary
- ✅ Deterministic EDA tools
- ✅ AGUI-compliant visualizations
- ✅ OpenAI LLM for business analysis

### **4. Dependencies** ✅ **ALL PRESENT**
- ✅ `pandas = "^2.0.0"` - Data manipulation
- ✅ `scipy = "^1.11.0"` - Statistical analysis
- ✅ `numpy = "^1.24.0"` - Numerical operations
- ✅ `matplotlib = "^3.7.0"` - Static visualizations
- ✅ `plotly = "^6.5.0"` - Interactive visualizations
- ✅ `seaborn = "^0.12.0"` - Statistical visualizations

**No additional dependencies needed!** ✅

---

## 🔄 **What Needs to Evolve**

### **1. Data Solution Orchestrator Integration** 🔄 **CRITICAL UPDATE**

#### **Current Plan (Phase 6):**
```python
# Current plan shows direct semantic data access
embeddings = await self.librarian.get_embeddings(...)
```

#### **Updated Vision (Should Match Content Pattern):**
```python
# Should use Data Solution Orchestrator (same pattern as Content)
data_solution = await self.get_data_solution_orchestrator()
expose_result = await data_solution.orchestrate_data_expose(
    file_id=file_id,
    parsed_file_id=parsed_file_id,
    user_context=user_context
)
embeddings = expose_result.get("embeddings", [])
```

**Why This Matters:**
- ✅ Consistent pattern with Content Pillar
- ✅ Platform correlation (auth, session, workflow, events, telemetry)
- ✅ Proper architectural layering
- ✅ workflow_id propagation

---

### **2. InsightsOrchestrator Method Updates** 🔄 **NEEDS UPDATE**

#### **Current Implementation:**
```python
async def analyze_content_for_insights(
    self,
    source_type: str,
    file_id: Optional[str] = None,
    content_metadata_id: Optional[str] = None,
    content_type: str = "structured",
    analysis_options: Optional[Dict[str, Any]] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    # Currently uses workflows directly
    if content_type == "structured":
        result = await self.structured_workflow.execute(...)
```

#### **Updated Implementation (Should Use Data Solution):**
```python
async def analyze_content_for_insights(
    self,
    content_id: str,  # Simplified - use content_id
    user_query: Optional[str] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze content using semantic data layer with Data Solution Orchestrator.
    
    REAL IMPLEMENTATION:
    1. Get Data Solution Orchestrator (same pattern as Content)
    2. Expose semantic data via orchestrate_data_expose()
    3. Analyze with business analysis agent
    4. Generate visualizations
    5. Request enrichment if needed
    """
    # Step 1: Get Data Solution Orchestrator (same pattern as Content)
    data_solution = await self._get_data_solution_orchestrator()
    
    # Step 2: Expose semantic data (not raw parsed data)
    expose_result = await data_solution.orchestrate_data_expose(
        file_id=file_id,  # Extract from content_id if needed
        parsed_file_id=parsed_file_id,
        user_context=user_context
    )
    
    embeddings = expose_result.get("embeddings", [])
    
    # Step 3: Determine data type
    data_type = self._determine_data_type(embeddings)
    
    # Step 4: Analyze based on data type
    if data_type == "structured":
        business_agent = await self.get_agent("InsightsBusinessAnalysisAgent")
        analysis_result = await business_agent.analyze_structured_data(
            content_id=content_id,
            user_context=user_context
        )
    else:
        business_agent = await self.get_agent("InsightsBusinessAnalysisAgent")
        analysis_result = await business_agent.analyze_unstructured_data(
            content_id=content_id,
            user_context=user_context
        )
    
    # Step 5: If enrichment needed, request via SemanticEnrichmentGateway
    if user_query and self._needs_enrichment(user_query, embeddings):
        enrichment_gateway = await self._get_semantic_enrichment_gateway()
        enrichment_result = await enrichment_gateway.enrich_semantic_layer(
            content_id=content_id,
            enrichment_request=self._build_enrichment_request(user_query),
            user_context=user_context
        )
    
    # Step 6: Generate visualization if requested
    if user_query and self._needs_visualization(user_query):
        viz_engine = await self._get_visualization_engine_service()
        viz_component = await viz_engine.create_agui_visualization(
            content_id=content_id,
            visualization_type="chart",
            visualization_spec=analysis_result.get("eda_results", {}),
            user_context=user_context
        )
        analysis_result["visualization"] = viz_component
    
    return analysis_result
```

---

### **3. Helper Method: Get Data Solution Orchestrator** 🆕 **NEW**

#### **Add to InsightsOrchestrator:**
```python
async def _get_data_solution_orchestrator(self):
    """
    Get Data Solution Orchestrator Service via Curator discovery.
    
    This is the ONLY way to access data operations in the platform.
    Hard fails if Data Solution Orchestrator is not available.
    
    Returns:
        DataSolutionOrchestratorService instance
    
    Raises:
        ValueError: If Data Solution Orchestrator Service is not available
    """
    try:
        # Discover via Curator (Solution realm service)
        curator = await self.get_foundation_service("CuratorFoundationService")
        if not curator:
            raise ValueError("Curator not available - cannot discover Data Solution Orchestrator Service")
        
        data_solution_service = await curator.get_service("DataSolutionOrchestratorService")
        if not data_solution_service:
            raise ValueError("Data Solution Orchestrator Service not available - must be registered in Solution realm")
        
        return data_solution_service
    except Exception as e:
        self.logger.error(f"❌ Failed to get Data Solution Orchestrator Service: {e}")
        raise ValueError(f"Data Solution Orchestrator Service not available: {e}")
```

**Note:** This is the same pattern used in ContentOrchestrator (line 159-185 in content_orchestrator.py).

---

### **4. Remove Direct Semantic Data Access** 🔄 **CLEANUP**

#### **Current Plan Issues:**
- Direct `librarian.get_embeddings()` calls
- Direct semantic data abstraction access
- Bypasses Data Solution Orchestrator

#### **Updated Pattern:**
- ✅ Use Data Solution Orchestrator for all semantic data access
- ✅ Use `orchestrate_data_expose()` method
- ✅ Maintain proper architectural layering

---

## 📋 **Updated Phase 6: InsightsOrchestrator Updates**

### **6.1 Key Changes**

**Before:**
```python
# Direct semantic data access
embeddings = await self.librarian.get_embeddings(...)
```

**After:**
```python
# Use Data Solution Orchestrator (same pattern as Content)
data_solution = await self._get_data_solution_orchestrator()
expose_result = await data_solution.orchestrate_data_expose(
    file_id=file_id,
    parsed_file_id=parsed_file_id,
    user_context=user_context
)
embeddings = expose_result.get("embeddings", [])
```

### **6.2 Updated Method Signature**

**Current:**
```python
async def analyze_content_for_insights(
    self,
    source_type: str,
    file_id: Optional[str] = None,
    content_metadata_id: Optional[str] = None,
    content_type: str = "structured",
    analysis_options: Optional[Dict[str, Any]] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
```

**Updated (Simplified):**
```python
async def analyze_content_for_insights(
    self,
    content_id: str,  # Primary identifier
    user_query: Optional[str] = None,  # Natural language query
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze content for insights using semantic data layer.
    
    Uses Data Solution Orchestrator (same pattern as Content Pillar).
    """
```

### **6.3 Updated Flow**

```
InsightsOrchestrator.analyze_content_for_insights()
  ↓
Get Data Solution Orchestrator (via Curator)
  ↓
orchestrate_data_expose() (exposes semantic embeddings)
  ↓
Determine data type (structured/unstructured)
  ↓
InsightsBusinessAnalysisAgent.analyze_structured_data() OR
InsightsBusinessAnalysisAgent.analyze_unstructured_data()
  ↓
If enrichment needed:
  SemanticEnrichmentGateway.enrich_semantic_layer()
  ↓
If visualization needed:
  VisualizationEngineService.create_agui_visualization()
  ↓
Return analysis result
```

---

## 📊 **Dependency Analysis**

### **Current Dependencies in pyproject.toml** ✅

**All Required Dependencies Present:**
```toml
# Financial Analysis Libraries (Required for Business Outcomes Pillar)
pandas = "^2.0.0"          # ✅ Data manipulation for EDA
scipy = "^1.11.0"          # ✅ Statistical analysis for EDA
matplotlib = "^3.7.0"      # ✅ Static visualizations
seaborn = "^0.12.0"        # ✅ Statistical visualizations

# Already present:
numpy = "^1.24.0"          # ✅ Numerical operations (line 79)
plotly = "^6.5.0"          # ✅ Interactive visualizations (line 101)
```

**No Additional Dependencies Needed!** ✅

---

## 🔍 **Current Implementation Gaps**

### **Gap 1: Data Solution Orchestrator Integration** ❌

**Current State:**
- InsightsOrchestrator does NOT use Data Solution Orchestrator
- Uses workflows directly
- No `_get_data_solution_orchestrator()` method

**Required:**
- Add `_get_data_solution_orchestrator()` method (same as ContentOrchestrator)
- Update `analyze_content_for_insights()` to use Data Solution Orchestrator
- Use `orchestrate_data_expose()` for semantic data access

---

### **Gap 2: Semantic Data Access Pattern** ❌

**Current State:**
- Direct `librarian.get_embeddings()` calls in workflows
- Direct semantic data abstraction access
- Bypasses Data Solution Orchestrator

**Required:**
- Remove direct semantic data access
- Use Data Solution Orchestrator for all semantic data
- Maintain proper architectural layering

---

### **Gap 3: Method Signature Simplification** ⚠️

**Current State:**
- Complex method signature with `source_type`, `file_id`, `content_metadata_id`, `content_type`
- Multiple workflow paths

**Required:**
- Simplify to `content_id` (primary identifier)
- Use Data Solution Orchestrator to handle file/content_metadata mapping
- Let Data Solution Orchestrator determine data type

---

## 📝 **Updated Phase 6 Implementation**

### **6.1 Add Data Solution Orchestrator Helper**

```python
async def _get_data_solution_orchestrator(self):
    """
    Get Data Solution Orchestrator Service via Curator discovery.
    
    Same pattern as ContentOrchestrator.
    """
    try:
        # Discover via Curator (Solution realm service)
        curator = await self.get_foundation_service("CuratorFoundationService")
        if not curator:
            raise ValueError("Curator not available")
        
        data_solution_service = await curator.get_service("DataSolutionOrchestratorService")
        if not data_solution_service:
            raise ValueError("Data Solution Orchestrator Service not available")
        
        return data_solution_service
    except Exception as e:
        self.logger.error(f"❌ Failed to get Data Solution Orchestrator Service: {e}")
        raise ValueError(f"Data Solution Orchestrator Service not available: {e}")
```

---

### **6.2 Update analyze_content_for_insights()**

```python
async def analyze_content_for_insights(
    self,
    content_id: str,
    user_query: Optional[str] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze content for insights using semantic data layer.
    
    Uses Data Solution Orchestrator (same pattern as Content Pillar).
    
    REAL IMPLEMENTATION:
    1. Get Data Solution Orchestrator
    2. Expose semantic data via orchestrate_data_expose()
    3. Analyze with business analysis agent
    4. Generate visualizations
    5. Request enrichment if needed
    """
    # Start telemetry tracking
    await self._realm_service.log_operation_with_telemetry(
        "analyze_content_for_insights_start",
        success=True,
        details={"content_id": content_id}
    )
    
    try:
        # Step 1: Get Data Solution Orchestrator (same pattern as Content)
        data_solution = await self._get_data_solution_orchestrator()
        
        # Step 2: Extract file_id from content_id (if needed)
        # Content metadata should have file_id reference
        librarian = await self.get_librarian_api()
        content_metadata = await librarian.get_content_metadata(content_id, user_context)
        file_id = content_metadata.get("file_id")
        parsed_file_id = content_metadata.get("parsed_file_id")
        
        # Step 3: Expose semantic data (not raw parsed data)
        expose_result = await data_solution.orchestrate_data_expose(
            file_id=file_id,
            parsed_file_id=parsed_file_id,
            user_context=user_context
        )
        
        if not expose_result.get("success"):
            return {
                "success": False,
                "error": "Failed to expose semantic data",
                "details": expose_result.get("error")
            }
        
        embeddings = expose_result.get("embeddings", [])
        
        if not embeddings:
            return {
                "success": False,
                "error": "No semantic embeddings found",
                "content_id": content_id
            }
        
        # Step 4: Determine data type from embeddings
        data_type = self._determine_data_type(embeddings)
        
        # Step 5: Analyze based on data type
        business_agent = await self.get_agent("InsightsBusinessAnalysisAgent")
        
        if data_type == "structured":
            analysis_result = await business_agent.analyze_structured_data(
                content_id=content_id,
                user_context=user_context
            )
        else:
            analysis_result = await business_agent.analyze_unstructured_data(
                content_id=content_id,
                user_context=user_context
            )
        
        # Step 6: If query needs specific data not in embeddings, request enrichment
        if user_query and self._needs_enrichment(user_query, embeddings):
            enrichment_gateway = await self._get_semantic_enrichment_gateway()
            enrichment_result = await enrichment_gateway.enrich_semantic_layer(
                content_id=content_id,
                enrichment_request=self._build_enrichment_request(user_query),
                user_context=user_context
            )
            
            if enrichment_result.get("success"):
                # Re-query with enriched embeddings
                expose_result = await data_solution.orchestrate_data_expose(
                    file_id=file_id,
                    parsed_file_id=parsed_file_id,
                    user_context=user_context
                )
                embeddings = expose_result.get("embeddings", [])
                # Re-analyze with enriched embeddings
                # ...
        
        # Step 7: Generate visualization if requested
        if user_query and self._needs_visualization(user_query):
            viz_engine = await self._get_visualization_engine_service()
            viz_component = await viz_engine.create_agui_visualization(
                content_id=content_id,
                visualization_type="chart",
                visualization_spec=analysis_result.get("eda_results", {}),
                user_context=user_context
            )
            analysis_result["visualization"] = viz_component
        
        # Record success
        await self._realm_service.record_health_metric(
            "analyze_content_for_insights_success",
            1.0,
            {"content_id": content_id, "data_type": data_type}
        )
        
        await self._realm_service.log_operation_with_telemetry(
            "analyze_content_for_insights_complete",
            success=True,
            details={"content_id": content_id, "data_type": data_type}
        )
        
        return analysis_result
        
    except Exception as e:
        await self._realm_service.handle_error_with_audit(e, "analyze_content_for_insights")
        await self._realm_service.record_health_metric(
            "analyze_content_for_insights_failed",
            1.0,
            {"content_id": content_id, "error": type(e).__name__}
        )
        await self._realm_service.log_operation_with_telemetry(
            "analyze_content_for_insights_complete",
            success=False,
            details={"content_id": content_id, "error": str(e)}
        )
        raise
```

---

### **6.3 Helper Methods**

```python
def _determine_data_type(self, embeddings: List[Dict[str, Any]]) -> str:
    """
    Determine data type from embeddings.
    
    REAL IMPLEMENTATION:
    - Check embedding_type field
    - Check schema embeddings presence
    - Default to "structured" if schema found
    """
    # Check for schema embeddings
    schema_embeddings = [e for e in embeddings if e.get("embedding_type") == "schema"]
    if schema_embeddings:
        return "structured"
    
    # Check for chunk embeddings
    chunk_embeddings = [e for e in embeddings if e.get("embedding_type") == "chunk"]
    if chunk_embeddings:
        return "unstructured"
    
    # Default
    return "structured"

def _needs_enrichment(self, user_query: str, embeddings: List[Dict[str, Any]]) -> bool:
    """
    Determine if enrichment is needed based on query and available embeddings.
    
    REAL IMPLEMENTATION:
    - Use LLM to analyze query requirements
    - Check if embeddings have required information
    - Return True if enrichment needed
    """
    # Simple heuristic for now (can be enhanced with LLM)
    query_lower = user_query.lower()
    
    # Check for specific data requests
    if any(keyword in query_lower for keyword in ["specific", "exact", "detailed", "all values"]):
        return True
    
    # Check if embeddings have enough information
    # (This would be more sophisticated in real implementation)
    return False

def _build_enrichment_request(self, user_query: str) -> Dict[str, Any]:
    """
    Build enrichment request from user query.
    
    REAL IMPLEMENTATION:
    - Use LLM to extract what semantic info is needed
    - Return enrichment request structure
    """
    return {
        "type": "column_values",  # or "statistics", etc.
        "query": user_query,
        "filters": {}  # Which columns/rows needed
    }

def _needs_visualization(self, user_query: str) -> bool:
    """
    Determine if visualization is needed based on query.
    
    REAL IMPLEMENTATION:
    - Check for visualization keywords
    - Return True if visualization needed
    """
    query_lower = user_query.lower()
    viz_keywords = ["show", "display", "chart", "graph", "plot", "visualize", "visualization"]
    return any(keyword in query_lower for keyword in viz_keywords)
```

---

## 📋 **Updated Plan Summary**

### **What Stays the Same** ✅
- Phase 1: DataAnalyzerService (EDA tools)
- Phase 2: VisualizationEngineService (AGUI components)
- Phase 3: InsightsBusinessAnalysisAgent
- Phase 4: SemanticEnrichmentGateway
- Phase 5: Specialized HF Agents
- Phase 7: Verify No CrewAI Usage
- Phase 8: Testing & Validation

### **What Evolves** 🔄
- **Phase 6:** Update InsightsOrchestrator to use Data Solution Orchestrator
  - Add `_get_data_solution_orchestrator()` method
  - Update `analyze_content_for_insights()` to use Data Solution Orchestrator
  - Remove direct semantic data access
  - Simplify method signature

### **Dependencies** ✅
- **No changes needed** - All required dependencies already in `pyproject.toml`

---

## ✅ **Action Items**

### **Update INSIGHTS_PILLAR_HF_IMPLEMENTATION_PLAN.md**

1. **Phase 6 Updates:**
   - [ ] Add `_get_data_solution_orchestrator()` method documentation
   - [ ] Update `analyze_content_for_insights()` to use Data Solution Orchestrator
   - [ ] Remove direct semantic data access patterns
   - [ ] Add helper methods (`_determine_data_type`, `_needs_enrichment`, etc.)

2. **Architecture Section Updates:**
   - [ ] Update flow diagram to show Data Solution Orchestrator
   - [ ] Show `orchestrate_data_expose()` usage
   - [ ] Align with Content Pillar pattern

3. **Code Examples Updates:**
   - [ ] Update all code examples to use Data Solution Orchestrator
   - [ ] Remove direct `librarian.get_embeddings()` calls
   - [ ] Show proper architectural layering

---

## 🎯 **Key Takeaways**

1. **Current plan is 90% aligned** - Only Phase 6 needs updates
2. **Dependencies are complete** - No additional packages needed
3. **Main evolution:** Use Data Solution Orchestrator (same pattern as Content)
4. **Architectural consistency:** Insights follows same pattern as Content Pillar

---

**Last Updated:** December 20, 2025  
**Status:** 📋 **Analysis Complete**  
**Next Action:** Update INSIGHTS_PILLAR_HF_IMPLEMENTATION_PLAN.md Phase 6


