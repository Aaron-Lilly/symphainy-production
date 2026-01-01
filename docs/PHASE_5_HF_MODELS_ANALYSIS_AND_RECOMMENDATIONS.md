# Phase 5: HF Models Analysis & Recommendations

**Date:** January 15, 2025  
**Status:** 🔍 **Architectural Review & Recommendations**  
**Goal:** Determine if HF models are needed or if better alternatives exist

---

## 🎯 **Executive Summary**

After reviewing Phase 5 and the current architecture, **HF models may not be necessary** for most use cases. We can achieve the same goals using:
1. **OpenAI LLM** (already integrated) for query generation and visualization spec generation
2. **VisualizationEngineService** (already built) for deterministic AGUI component generation
3. **Semantic search + enrichment** as primary pathway

**Recommendation:** Use OpenAI LLM as primary approach, with HF models as optional fallback for specialized cases.

---

## 📊 **Current Architecture Assessment**

### **What We Already Have:**

1. **Semantic Search** (ArangoDB vector search)
   - Vector similarity search on embeddings
   - Can find relevant data semantically
   - Primary pathway for queries

2. **EDA Tools** (DataAnalyzerService)
   - Deterministic analysis (statistics, correlations, distributions)
   - Works with semantic embeddings
   - Provides structured results

3. **VisualizationEngineService**
   - Generates AGUI components deterministically
   - Uses plotly/matplotlib for data generation
   - Already produces structured AGUI schema-compliant components
   - **Does NOT need code generation** - it's deterministic

4. **OpenAI LLM Integration**
   - Already integrated via LLM abstraction
   - Can generate SQL/Pandas code
   - Can interpret natural language
   - Large context window (128k tokens)
   - No table size limits (works with schema/metadata)

5. **Semantic Enrichment Gateway**
   - Can request additional semantic data when needed
   - Maintains security boundary

---

## 🤔 **Phase 5 Use Cases Analysis**

### **Use Case 1: Queries That Semantic Search Can't Address**

**Problem:** User asks a question that requires specific data not found via semantic search.

**Current Plan:** Use HF text-to-SQL model (sqlcoder-7b or tapas).

**Alternative Approach:**
1. **Try semantic search first** (via vector search on embeddings)
2. **If insufficient, use OpenAI LLM** to:
   - Analyze the query
   - Generate SQL/Pandas query based on schema metadata from embeddings
   - Execute query (if we have query execution capability)
3. **If still insufficient, request enrichment** via SemanticEnrichmentGateway
4. **Re-query with enriched embeddings**

**Why OpenAI LLM is Better:**
- ✅ Already integrated (no new infrastructure)
- ✅ More flexible (can handle various query types)
- ✅ Large context window (can include full schema)
- ✅ No table size limits (works with metadata, not full tables)
- ✅ Can generate both SQL and Pandas
- ✅ Better at understanding business context

**When HF Might Be Needed:**
- ❌ Only if we need specialized SQL generation that OpenAI can't handle
- ❌ Only if we want to run models locally (privacy/offline requirements)
- ❌ Only if cost is a concern (HF models are free to run)

### **Use Case 2: Visualization Generation**

**Problem:** User requests a visualization (e.g., "Show me a bar chart of revenue by region").

**Current Plan:** Use HF code generation model (starcoder2-7b) to generate matplotlib/plotly code.

**Reality Check:**
- ✅ **VisualizationEngineService already exists** and generates AGUI components
- ✅ It's **deterministic** (same input = same output)
- ✅ It works with **semantic embeddings** (not raw data)
- ✅ It produces **AGUI schema-compliant components** (not raw code)

**Better Approach:**
1. **Use OpenAI LLM** to interpret user's visualization request
2. **Generate visualization spec** (chart_type, x_axis, y_axis, title, etc.)
3. **Pass spec to VisualizationEngineService**
4. **Service generates AGUI component deterministically**

**Why This is Better:**
- ✅ No code generation needed (VisualizationEngineService handles it)
- ✅ More secure (no code execution)
- ✅ More consistent (deterministic results)
- ✅ AGUI-compliant (structured components)
- ✅ Works with semantic data (security boundary maintained)

**HF Not Needed Because:**
- VisualizationEngineService already generates visualizations
- We don't need code generation - we need spec generation
- OpenAI LLM can interpret NL and generate specs

---

## 🔍 **Model Comparison: sqlcoder-7b vs tapas**

### **defog/sqlcoder-7b**

**Strengths:**
- ✅ Purpose-built for SQL generation
- ✅ Good performance on SQL queries
- ✅ Can handle complex queries
- ✅ No table size limits (works with schema)

**Limitations:**
- ❌ SQL-specific (doesn't handle Pandas well)
- ❌ Requires schema/metadata (not full tables)
- ❌ May need fine-tuning for our specific schemas
- ❌ Requires HF infrastructure setup

**Best For:**
- Database-backed queries
- Complex SQL generation
- When we have well-defined schemas

### **google/tapas-large-finetuned-wtq**

**Strengths:**
- ✅ Table-based question answering
- ✅ Can answer questions directly over tables
- ✅ Good for CSV/Excel-like data

**Limitations:**
- ❌ **Table size limits** (typically 512 tokens for table content)
- ❌ Requires full table data (not just schema)
- ❌ Would break security boundary (needs raw parsed data)
- ❌ Not ideal for SQL generation
- ❌ May not scale to large datasets

**Best For:**
- Small-medium tables (< 512 tokens)
- Direct table QA (not query generation)
- When table data is available

### **OpenAI GPT-4/GPT-4o**

**Strengths:**
- ✅ Already integrated
- ✅ Large context window (128k tokens)
- ✅ Can generate both SQL and Pandas
- ✅ Works with schema/metadata (no table size limits)
- ✅ Better at understanding business context
- ✅ More flexible (handles various query types)

**Limitations:**
- ❌ API costs (but reasonable for our use case)
- ❌ Requires internet connection
- ❌ Not specialized for SQL (but good enough)

**Best For:**
- Our use case (semantic data layer, schema-based queries)
- Flexible query generation
- Business context understanding

---

## 💡 **Recommended Approach**

### **Primary Pathway: OpenAI LLM + Existing Services**

```
User Query
  ↓
1. Try Semantic Search (vector search on embeddings)
  ↓ (if insufficient)
2. Use OpenAI LLM to:
   - Analyze query
   - Generate query spec (SQL/Pandas) based on schema metadata
   - Or generate visualization spec
  ↓
3. Execute via:
   - Query execution service (if we build one)
   - Or VisualizationEngineService (for visualizations)
  ↓ (if still insufficient)
4. Request enrichment via SemanticEnrichmentGateway
  ↓
5. Re-query with enriched embeddings
```

### **For Query Generation:**

**Create: `InsightsQueryAgent` (not HF-specific)**

```python
class InsightsQueryAgent(AgentBase):
    """
    Query Generation Agent - Uses OpenAI LLM for query generation.
    
    Only used when semantic search isn't sufficient.
    """
    
    async def generate_query(
        self,
        natural_language_query: str,
        schema_metadata: Dict[str, Any],  # From embeddings
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate SQL/Pandas query using OpenAI LLM.
        
        Flow:
        1. Get schema metadata from embeddings
        2. Use OpenAI LLM to generate query
        3. Return query spec (not raw code)
        """
        # Use OpenAI LLM (already integrated)
        # Generate query based on schema
        # Return query spec
```

**Why Not HF:**
- OpenAI LLM is already integrated
- More flexible and context-aware
- No table size limits
- Works with schema metadata (security boundary maintained)

### **For Visualization Generation:**

**Use: `VisualizationEngineService` + OpenAI LLM for spec generation**

```python
# In InsightsOrchestrator or Business Analysis Agent
async def generate_visualization_from_query(
    self,
    user_query: str,
    content_id: str,
    embeddings: List[Dict[str, Any]],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate visualization from natural language query.
    
    Flow:
    1. Use OpenAI LLM to interpret query and generate visualization spec
    2. Pass spec to VisualizationEngineService
    3. Service generates AGUI component deterministically
    """
    # Step 1: Use OpenAI LLM to generate visualization spec
    llm_abstraction = await self.get_business_abstraction("llm")
    spec = await llm_abstraction.generate_response(
        LLMRequest(
            messages=[
                {"role": "system", "content": "You are a visualization spec generator..."},
                {"role": "user", "content": f"Generate visualization spec for: {user_query}\n\nSchema: {schema_from_embeddings}"}
            ]
        )
    )
    
    # Step 2: Parse spec and call VisualizationEngineService
    viz_engine = await self._get_visualization_engine_service()
    component = await viz_engine.create_agui_visualization(
        content_id=content_id,
        visualization_type=spec.get("type", "chart"),
        visualization_spec=spec,
        user_context=user_context
    )
    
    return component
```

**Why Not HF:**
- VisualizationEngineService already generates visualizations
- We need spec generation, not code generation
- OpenAI LLM can interpret NL and generate specs
- More secure (no code execution)

---

## 🎯 **Revised Phase 5 Recommendation**

### **Option A: Skip HF Models (Recommended)**

**Create:**
1. **InsightsQueryAgent** - Uses OpenAI LLM for query generation
2. **Enhanced VisualizationEngineService integration** - Use OpenAI LLM for spec generation

**Benefits:**
- ✅ Simpler architecture (no HF infrastructure)
- ✅ Uses existing OpenAI integration
- ✅ More flexible and context-aware
- ✅ No table size limits
- ✅ Maintains security boundary
- ✅ Faster to implement

**Trade-offs:**
- ❌ API costs (but reasonable)
- ❌ Requires internet (but we already have this)

### **Option B: HF Models as Optional Fallback**

**Create:**
1. **InsightsQueryAgent** - Primary: OpenAI LLM, Fallback: HF sqlcoder-7b
2. **Keep VisualizationEngineService** - Use OpenAI LLM for spec generation (no HF needed)

**When to Use HF:**
- Offline/private deployments
- Cost-sensitive scenarios
- Specialized SQL generation needs

**Implementation:**
- Use StatelessHFInferenceAgent pattern
- Only call HF if OpenAI fails or is unavailable
- Handle table size limits for tapas (chunk tables if needed)

---

## 📋 **Specific Recommendations**

### **1. Query Generation**

**Recommendation:** Use OpenAI LLM (GPT-4o) for query generation.

**Implementation:**
- Create `InsightsQueryAgent` that uses OpenAI LLM
- Generate queries based on schema metadata from embeddings
- Return query specs (not raw SQL/Pandas code)
- Execute queries via query execution service (if we build one)

**Skip HF Unless:**
- We need offline/private deployment
- Cost is a major concern
- We need specialized SQL generation

### **2. Visualization Generation**

**Recommendation:** Use OpenAI LLM for spec generation + VisualizationEngineService for component generation.

**Implementation:**
- Use OpenAI LLM to interpret user query
- Generate visualization spec (chart_type, x_axis, y_axis, etc.)
- Pass spec to VisualizationEngineService
- Service generates AGUI component deterministically

**Skip HF Completely:**
- VisualizationEngineService already handles visualization generation
- We don't need code generation
- OpenAI LLM can generate specs

### **3. If We Do Use HF Models**

**For Query Generation:**
- **Use sqlcoder-7b** (not tapas)
  - Works with schema (not full tables)
  - No table size limits
  - Better for SQL generation
  - Maintains security boundary

**For Visualization:**
- **Don't use HF** - VisualizationEngineService is sufficient

**Table Size Limits (if using tapas):**
- TAPAS typically handles ~512 tokens of table content
- Would need to chunk large tables
- Would break security boundary (needs raw parsed data)
- **Not recommended for our architecture**

---

## 🔄 **Updated Phase 5 Implementation**

### **Phase 5A: Query Generation Agent (OpenAI-based)**

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/agents/insights_query_agent.py`

```python
class InsightsQueryAgent(AgentBase):
    """
    Query Generation Agent - Uses OpenAI LLM for query generation.
    
    Only used when semantic search isn't sufficient.
    """
    
    async def generate_query_from_nl(
        self,
        natural_language_query: str,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate SQL/Pandas query from natural language.
        
        Flow:
        1. Get schema metadata from embeddings
        2. Use OpenAI LLM to generate query
        3. Return query spec
        """
        # Get schema from embeddings
        # Use OpenAI LLM to generate query
        # Return query spec
```

### **Phase 5B: Enhanced Visualization Integration**

**Update:** `InsightsOrchestrator` or `InsightsBusinessAnalysisAgent`

```python
async def generate_visualization_from_nl(
    self,
    user_query: str,
    content_id: str,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate visualization from natural language query.
    
    Uses OpenAI LLM for spec generation + VisualizationEngineService for component generation.
    """
    # Use OpenAI LLM to generate visualization spec
    # Call VisualizationEngineService
    # Return AGUI component
```

---

## ✅ **Final Recommendation**

**Skip HF Models for MVP** and use:
1. **OpenAI LLM** for query generation and visualization spec generation
2. **VisualizationEngineService** for deterministic AGUI component generation
3. **Semantic search + enrichment** as primary pathway

**Reasons:**
- ✅ Simpler architecture
- ✅ Uses existing infrastructure
- ✅ More flexible and context-aware
- ✅ No table size limits
- ✅ Maintains security boundary
- ✅ Faster to implement

**Consider HF Later If:**
- We need offline/private deployments
- Cost becomes a major concern
- We need specialized capabilities OpenAI can't provide

---

## 📝 **Action Items**

1. ✅ Update Phase 5 plan to use OpenAI LLM instead of HF
2. ✅ Create InsightsQueryAgent (OpenAI-based)
3. ✅ Enhance visualization integration (OpenAI spec generation)
4. ⏸️ Defer HF models to future phase (if needed)

