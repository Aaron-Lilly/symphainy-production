# Insights Pillar Implementation Plan
## Bringing the Vision to Life with Semantic Data Layer Security

**Date:** December 20, 2025 (Updated: January 15, 2025)  
**Status:** 🚀 **Implementation Plan**  
**Strategy:** Semantic-First, Agentic Forward, Security Boundary Maintained  
**Architecture:** Showcase Use Case with Proper Enabling Services

**Note:** This plan was updated to use OpenAI LLM instead of HuggingFace models for query generation and visualization spec generation. See `PHASE_5_HF_MODELS_ANALYSIS_AND_RECOMMENDATIONS.md` for the detailed analysis and rationale.

---

## 🎯 **Executive Summary**

This plan implements the Insights Pillar vision while maintaining the semantic data layer security boundary. The insights pillar serves as a showcase/use case demonstrating analytics capabilities built on semantic data. The plan uses OpenAI LLM (already integrated) for query generation and visualization spec generation, providing a simpler and more flexible architecture than specialized HF models.

**Key Principles:**
1. **Semantic Data Layer is Security Boundary** - Platform only uses semantic data, never raw parsed data
2. **Structured Data:** EDA Analysis Tools → OpenAI LLM interpretation (deterministic results)
3. **Unstructured Data:** Direct embedding review with OpenAI LLM
4. **Visualization:** AGUI-compliant components (not raw code)
5. **OpenAI LLM for Query & Visualization Spec Generation:** Use existing OpenAI integration (simpler, more flexible)
6. **Agentic Foundation SDK:** Use custom agentic foundation (CrewAI already removed)
7. **InsightsLiaisonAgent:** Conversational interface with full websocket integration for E2E functionality

---

## 🏗️ **Architecture Overview**

```
User Query → InsightsOrchestrator
  ↓
Get Data Solution Orchestrator (via Curator)
  ↓
orchestrate_data_expose() (exposes semantic embeddings)
  ↓
Determine data type (structured/unstructured)
  ↓
┌─────────────────────────────────────────────────────────┐
│ STRUCTURED DATA PATH                                     │
├─────────────────────────────────────────────────────────┤
│ Business Analysis Agent (OpenAI LLM)                      │
│   ↓ calls EDA Analysis Tools (DataAnalyzerService)      │
│   ↓ gets deterministic results                           │
│   ↓ interprets with OpenAI LLM                          │
│   ↓ generates consistent business narrative              │
└─────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────┐
│ UNSTRUCTURED DATA PATH                                   │
├─────────────────────────────────────────────────────────┤
│ Business Analysis Agent (OpenAI LLM)                      │
│   ↓ reviews semantic embeddings directly                 │
│   ↓ generates business narrative                        │
└─────────────────────────────────────────────────────────┘
  ↓
If query needs specific data not in embeddings:
  ↓
Semantic Enrichment Gateway
  ↓ requests enrichment (not raw data)
  ↓ enrichment service creates new embeddings
  ↓ adds to semantic layer
  ↓ platform queries enriched semantic layer via Data Solution
  ↓
Visualization Request → Visualization Engine Service (AGUI components)
  ↓ generates
AGUI-compliant visualization components
  ↓
Frontend renders via AGUI schema
```

**Key Architectural Pattern:**
- ✅ **Data Solution Orchestrator** - Same pattern as Content Pillar
- ✅ **orchestrate_data_expose()** - Primary pathway for semantic data access
- ✅ **No direct semantic data access** - All access via Data Solution Orchestrator
- ✅ **Platform correlation** - Auth, session, workflow, events, telemetry

---

## 📋 **Phase 1: Build Proper DataAnalyzerService with EDA Tools** (Week 1, Days 1-3)

### **1.1 Goal**

Rebuild DataAnalyzerService to expose EDA (Exploratory Data Analysis) tools that agents can call. The service should:
- Work with semantic embeddings (schema/metadata)
- Provide deterministic EDA results
- Support structured data analysis
- Be callable via MCP tools

### **1.2 Current State Analysis**

**Issues:**
- DataAnalyzerService exists but may not have proper EDA tools
- No clear separation between EDA tools and business analysis
- May not work with semantic data layer

**Required:**
- EDA tools that work with semantic embeddings
- Deterministic results (same input = same output)
- MCP tool exposure for agents

### **1.3 Implementation**

**File:** `backend/business_enablement/enabling_services/data_analyzer_service/data_analyzer_service.py`

**Key Methods to Add/Update:**

```python
class DataAnalyzerService(RealmServiceBase):
    """
    Data Analyzer Service - Exposes EDA tools for agents.
    
    WHAT: Provides exploratory data analysis tools
    HOW: Works with semantic embeddings, provides deterministic results
    """
    
    async def run_eda_analysis(
        self,
        content_id: str,
        analysis_types: List[str],  # ["statistics", "correlations", "distributions", "missing_values"]
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run EDA analysis on structured data using semantic embeddings.
        
        Flow:
        1. Get semantic embeddings (schema/metadata) from Librarian
        2. Extract schema information from embeddings
        3. Run EDA analysis tools (deterministic)
        4. Return structured results
        
        Args:
            content_id: Content metadata ID
            analysis_types: List of analysis types to run
            user_context: Optional user context
            
        Returns:
            Dict with EDA results (deterministic - same input = same output)
        """
        try:
            # Step 1: Get semantic embeddings (schema/metadata)
            embeddings = await self.librarian.get_embeddings(
                content_id=content_id,
                filters={"embedding_type": "schema"},  # Get schema embeddings
                user_context=user_context
            )
            
            if not embeddings:
                return {
                    "success": False,
                    "error": "No schema embeddings found for content_id",
                    "content_id": content_id
                }
            
            # Step 2: Extract schema information from embeddings
            schema_info = self._extract_schema_from_embeddings(embeddings)
            
            # Step 3: Run EDA analysis tools (deterministic)
            eda_results = {}
            
            if "statistics" in analysis_types:
                eda_results["statistics"] = await self._calculate_statistics(schema_info)
            
            if "correlations" in analysis_types:
                eda_results["correlations"] = await self._calculate_correlations(schema_info)
            
            if "distributions" in analysis_types:
                eda_results["distributions"] = await self._calculate_distributions(schema_info)
            
            if "missing_values" in analysis_types:
                eda_results["missing_values"] = await self._analyze_missing_values(schema_info)
            
            # Step 4: Return structured results (deterministic)
            return {
                "success": True,
                "content_id": content_id,
                "analysis_types": analysis_types,
                "eda_results": eda_results,
                "schema_info": schema_info  # Include schema for context
            }
            
        except Exception as e:
            self.logger.error(f"❌ EDA analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content_id": content_id
            }
    
    def _extract_schema_from_embeddings(
        self,
        embeddings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract schema information from semantic embeddings.
        
        Schema embeddings contain:
        - column_name
        - data_type
        - sample_values (from representative sampling)
        - metadata (statistics, constraints, etc.)
        """
        schema = {
            "columns": [],
            "data_types": {},
            "sample_values": {},
            "metadata": {}
        }
        
        for emb in embeddings:
            column_name = emb.get("column_name")
            if not column_name:
                continue
            
            schema["columns"].append(column_name)
            schema["data_types"][column_name] = emb.get("data_type", "unknown")
            schema["sample_values"][column_name] = emb.get("sample_values", [])
            schema["metadata"][column_name] = emb.get("metadata", {})
        
        return schema
    
    async def _calculate_statistics(
        self,
        schema_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate descriptive statistics from schema embeddings.
        
        Uses metadata from embeddings (which includes statistics from representative sampling).
        """
        statistics = {}
        
        for column_name in schema_info["columns"]:
            metadata = schema_info["metadata"].get(column_name, {})
            data_type = schema_info["data_types"].get(column_name, "unknown")
            
            if data_type in ["int", "float", "number"]:
                # Numerical statistics
                statistics[column_name] = {
                    "type": "numerical",
                    "mean": metadata.get("mean"),
                    "median": metadata.get("median"),
                    "std": metadata.get("std"),
                    "min": metadata.get("min"),
                    "max": metadata.get("max"),
                    "count": metadata.get("count"),
                    "null_count": metadata.get("null_count", 0)
                }
            elif data_type in ["string", "text", "object"]:
                # Categorical statistics
                statistics[column_name] = {
                    "type": "categorical",
                    "unique_count": metadata.get("unique_count"),
                    "most_common": metadata.get("most_common", []),
                    "count": metadata.get("count"),
                    "null_count": metadata.get("null_count", 0)
                }
            else:
                # Unknown type
                statistics[column_name] = {
                    "type": "unknown",
                    "count": metadata.get("count"),
                    "null_count": metadata.get("null_count", 0)
                }
        
        return statistics
    
    async def _calculate_correlations(
        self,
        schema_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate correlations between numerical columns.
        
        Uses correlation metadata from embeddings if available.
        """
        numerical_columns = [
            col for col in schema_info["columns"]
            if schema_info["data_types"].get(col) in ["int", "float", "number"]
        ]
        
        if len(numerical_columns) < 2:
            return {
                "message": "Insufficient numerical columns for correlation analysis",
                "numerical_columns": numerical_columns
            }
        
        # Extract correlation metadata from embeddings
        correlations = {}
        
        for col1 in numerical_columns:
            metadata1 = schema_info["metadata"].get(col1, {})
            correlations[col1] = {}
            
            for col2 in numerical_columns:
                if col1 == col2:
                    correlations[col1][col2] = 1.0
                else:
                    # Get correlation from metadata if available
                    correlation_metadata = metadata1.get("correlations", {})
                    correlations[col1][col2] = correlation_metadata.get(col2, 0.0)
        
        return {
            "numerical_columns": numerical_columns,
            "correlation_matrix": correlations
        }
    
    async def _calculate_distributions(
        self,
        schema_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate distribution information from schema embeddings.
        
        Uses sample values and metadata from embeddings.
        """
        distributions = {}
        
        for column_name in schema_info["columns"]:
            metadata = schema_info["metadata"].get(column_name, {})
            data_type = schema_info["data_types"].get(column_name, "unknown")
            sample_values = schema_info["sample_values"].get(column_name, [])
            
            if data_type in ["int", "float", "number"]:
                # Numerical distribution
                distributions[column_name] = {
                    "type": "numerical",
                    "skewness": metadata.get("skewness"),
                    "kurtosis": metadata.get("kurtosis"),
                    "quartiles": {
                        "q1": metadata.get("q1"),
                        "q2": metadata.get("q2"),  # median
                        "q3": metadata.get("q3")
                    },
                    "sample_values": sample_values[:10]  # First 10 samples
                }
            elif data_type in ["string", "text", "object"]:
                # Categorical distribution
                distributions[column_name] = {
                    "type": "categorical",
                    "value_counts": metadata.get("value_counts", {}),
                    "sample_values": sample_values[:10]
                }
            else:
                distributions[column_name] = {
                    "type": "unknown",
                    "sample_values": sample_values[:10]
                }
        
        return distributions
    
    async def _analyze_missing_values(
        self,
        schema_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze missing values from schema embeddings.
        
        Uses metadata from embeddings.
        """
        missing_analysis = {}
        
        for column_name in schema_info["columns"]:
            metadata = schema_info["metadata"].get(column_name, {})
            
            total_count = metadata.get("count", 0)
            null_count = metadata.get("null_count", 0)
            missing_percentage = (null_count / total_count * 100) if total_count > 0 else 0
            
            missing_analysis[column_name] = {
                "total_count": total_count,
                "null_count": null_count,
                "missing_percentage": round(missing_percentage, 2),
                "has_missing": null_count > 0
            }
        
        return missing_analysis
```

### **1.4 MCP Tool Exposure**

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/mcp_server/insights_mcp_server.py`

**Add MCP Tool:**

```python
def _register_eda_analysis_tool(self):
    """Register EDA analysis tool for agents."""
    self.register_tool(
        name="run_eda_analysis_tool",
        description="Run exploratory data analysis (EDA) on structured data. Returns deterministic results that can be interpreted by LLM.",
        input_schema={
            "type": "object",
            "properties": {
                "content_id": {
                    "type": "string",
                    "description": "Content metadata ID"
                },
                "analysis_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["statistics", "correlations", "distributions", "missing_values"]
                    },
                    "description": "List of analysis types to run"
                }
            },
            "required": ["content_id", "analysis_types"]
        },
        handler=self._handle_eda_analysis_tool
    )

async def _handle_eda_analysis_tool(
    self,
    parameters: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Handle EDA analysis tool call."""
    try:
        data_analyzer = await self.orchestrator._get_data_analyzer_service()
        if not data_analyzer:
            return {
                "success": False,
                "error": "Data Analyzer Service not available"
            }
        
        result = await data_analyzer.run_eda_analysis(
            content_id=parameters.get("content_id"),
            analysis_types=parameters.get("analysis_types", []),
            user_context=user_context
        )
        
        return result
        
    except Exception as e:
        self.logger.error(f"❌ EDA analysis tool failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

### **1.5 Deliverables**

- [ ] DataAnalyzerService updated with EDA tools
- [ ] `run_eda_analysis()` method implemented
- [ ] Schema extraction from embeddings
- [ ] Statistics calculation
- [ ] Correlations calculation
- [ ] Distributions calculation
- [ ] Missing values analysis
- [ ] MCP tool registered
- [ ] Unit tests for EDA tools
- [ ] Integration tests with semantic embeddings

---

## 📋 **Phase 2: Build Proper VisualizationEngineService with AGUI Components** (Week 1, Days 4-5)

### **2.1 Goal**

Rebuild VisualizationEngineService to generate AGUI-compliant visualization components instead of raw matplotlib/plotly code. The service should:
- Generate AGUI schema-compliant components
- Work with semantic embeddings
- Support visualization composition
- Be callable via MCP tools

### **2.2 Current State Analysis**

**Issues:**
- VisualizationEngineService may generate raw code (matplotlib/plotly)
- Not integrated with AGUI
- May not work with semantic data layer

**Required:**
- AGUI-compliant component generation
- Integration with AGUI schema registry
- Visualization composition support

### **2.3 Implementation**

**File:** `backend/business_enablement/enabling_services/visualization_engine_service/visualization_engine_service.py`

**Key Methods to Add/Update:**

```python
class VisualizationEngineService(RealmServiceBase):
    """
    Visualization Engine Service - Generates AGUI-compliant visualization components.
    
    WHAT: Provides visualization generation capabilities
    HOW: Generates AGUI schema-compliant components (not raw code)
    """
    
    def __init__(self, ...):
        super().__init__(...)
        # Get AGUI schema registry
        self.agui_schema_registry = None  # Will be initialized
        self.visualization_composition = None  # Will be initialized
    
    async def create_agui_visualization(
        self,
        content_id: str,
        visualization_type: str,  # "chart", "dashboard", "table", etc.
        visualization_spec: Dict[str, Any],  # What to visualize
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create AGUI-compliant visualization component.
        
        Flow:
        1. Get semantic embeddings (data to visualize)
        2. Generate AGUI component based on visualization_spec
        3. Return AGUI schema-compliant component
        
        Args:
            content_id: Content metadata ID
            visualization_type: Type of visualization ("chart", "dashboard", "table")
            visualization_spec: Specification of what to visualize
            user_context: Optional user context
            
        Returns:
            Dict with AGUI-compliant component
        """
        try:
            # Step 1: Get semantic embeddings (data to visualize)
            embeddings = await self.librarian.get_embeddings(
                content_id=content_id,
                filters=visualization_spec.get("filters", {}),
                user_context=user_context
            )
            
            if not embeddings:
                return {
                    "success": False,
                    "error": "No embeddings found for visualization",
                    "content_id": content_id
                }
            
            # Step 2: Generate AGUI component based on visualization_spec
            if visualization_type == "chart":
                component = await self._create_chart_component(embeddings, visualization_spec)
            elif visualization_type == "dashboard":
                component = await self._create_dashboard_component(embeddings, visualization_spec)
            elif visualization_type == "table":
                component = await self._create_table_component(embeddings, visualization_spec)
            else:
                return {
                    "success": False,
                    "error": f"Unknown visualization type: {visualization_type}"
                }
            
            # Step 3: Return AGUI schema-compliant component
            return {
                "success": True,
                "content_id": content_id,
                "visualization_type": visualization_type,
                "component": component,  # AGUI-compliant component
                "agui_schema": self._get_agui_schema_for_type(visualization_type)
            }
            
        except Exception as e:
            self.logger.error(f"❌ AGUI visualization creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content_id": content_id
            }
    
    async def _create_chart_component(
        self,
        embeddings: List[Dict[str, Any]],
        visualization_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create AGUI chart component.
        
        AGUI chart component structure:
        {
            "type": "chart",
            "chart_type": "bar" | "line" | "scatter" | "histogram" | etc.,
            "data": [...],
            "config": {...},
            "metadata": {...}
        }
        """
        chart_type = visualization_spec.get("chart_type", "bar")
        x_axis = visualization_spec.get("x_axis")
        y_axis = visualization_spec.get("y_axis")
        
        # Extract data from embeddings
        data = self._extract_data_from_embeddings(embeddings, x_axis, y_axis)
        
        # Create AGUI chart component
        component = {
            "type": "chart",
            "chart_type": chart_type,
            "data": data,
            "config": {
                "x_axis": x_axis,
                "y_axis": y_axis,
                "title": visualization_spec.get("title", "Chart"),
                "labels": visualization_spec.get("labels", {})
            },
            "metadata": {
                "content_id": visualization_spec.get("content_id"),
                "created_at": datetime.now().isoformat()
            }
        }
        
        return component
    
    async def _create_dashboard_component(
        self,
        embeddings: List[Dict[str, Any]],
        visualization_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create AGUI dashboard component.
        
        AGUI dashboard component structure:
        {
            "type": "dashboard",
            "components": [...],  # Array of chart/table components
            "layout": {...},
            "metadata": {...}
        }
        """
        components = visualization_spec.get("components", [])
        
        # Create individual components
        dashboard_components = []
        for comp_spec in components:
            if comp_spec.get("type") == "chart":
                comp = await self._create_chart_component(embeddings, comp_spec)
            elif comp_spec.get("type") == "table":
                comp = await self._create_table_component(embeddings, comp_spec)
            else:
                continue
            
            dashboard_components.append(comp)
        
        # Create AGUI dashboard component
        component = {
            "type": "dashboard",
            "components": dashboard_components,
            "layout": visualization_spec.get("layout", {
                "grid": "auto",
                "columns": 2
            }),
            "metadata": {
                "content_id": visualization_spec.get("content_id"),
                "created_at": datetime.now().isoformat()
            }
        }
        
        return component
    
    async def _create_table_component(
        self,
        embeddings: List[Dict[str, Any]],
        visualization_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create AGUI table component.
        
        AGUI table component structure:
        {
            "type": "table",
            "columns": [...],
            "rows": [...],
            "config": {...},
            "metadata": {...}
        }
        """
        # Extract table data from embeddings
        columns = visualization_spec.get("columns", [])
        rows = self._extract_table_data_from_embeddings(embeddings, columns)
        
        # Create AGUI table component
        component = {
            "type": "table",
            "columns": columns,
            "rows": rows,
            "config": {
                "sortable": visualization_spec.get("sortable", True),
                "filterable": visualization_spec.get("filterable", True),
                "pageable": visualization_spec.get("pageable", True)
            },
            "metadata": {
                "content_id": visualization_spec.get("content_id"),
                "created_at": datetime.now().isoformat()
            }
        }
        
        return component
    
    def _extract_data_from_embeddings(
        self,
        embeddings: List[Dict[str, Any]],
        x_axis: Optional[str],
        y_axis: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Extract chart data from embeddings."""
        data = []
        
        for emb in embeddings:
            row = {}
            if x_axis:
                row[x_axis] = emb.get(x_axis) or emb.get("column_name")
            if y_axis:
                row[y_axis] = emb.get(y_axis) or emb.get("value")
            if row:
                data.append(row)
        
        return data
    
    def _extract_table_data_from_embeddings(
        self,
        embeddings: List[Dict[str, Any]],
        columns: List[str]
    ) -> List[Dict[str, Any]]:
        """Extract table data from embeddings."""
        rows = []
        
        for emb in embeddings:
            row = {}
            for col in columns:
                row[col] = emb.get(col) or emb.get("column_name")
            if row:
                rows.append(row)
        
        return rows
    
    def _get_agui_schema_for_type(self, visualization_type: str) -> Dict[str, Any]:
        """Get AGUI schema for visualization type."""
        # Get from AGUI schema registry
        if not self.agui_schema_registry:
            # Fallback schema
            return {
                "type": visualization_type,
                "schema_version": "1.0"
            }
        
        return self.agui_schema_registry.get_schema_for_type(visualization_type)
```

### **2.4 MCP Tool Exposure**

**Add MCP Tool:**

```python
def _register_create_agui_visualization_tool(self):
    """Register AGUI visualization creation tool for agents."""
    self.register_tool(
        name="create_agui_visualization_tool",
        description="Create AGUI-compliant visualization component (chart, dashboard, or table). Returns AGUI schema-compliant component, not raw code.",
        input_schema={
            "type": "object",
            "properties": {
                "content_id": {
                    "type": "string",
                    "description": "Content metadata ID"
                },
                "visualization_type": {
                    "type": "string",
                    "enum": ["chart", "dashboard", "table"],
                    "description": "Type of visualization to create"
                },
                "visualization_spec": {
                    "type": "object",
                    "description": "Specification of what to visualize"
                }
            },
            "required": ["content_id", "visualization_type", "visualization_spec"]
        },
        handler=self._handle_create_agui_visualization_tool
    )

async def _handle_create_agui_visualization_tool(
    self,
    parameters: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Handle AGUI visualization creation tool call."""
    try:
        visualization_engine = await self.orchestrator._get_visualization_engine_service()
        if not visualization_engine:
            return {
                "success": False,
                "error": "Visualization Engine Service not available"
            }
        
        result = await visualization_engine.create_agui_visualization(
            content_id=parameters.get("content_id"),
            visualization_type=parameters.get("visualization_type"),
            visualization_spec=parameters.get("visualization_spec", {}),
            user_context=user_context
        )
        
        return result
        
    except Exception as e:
        self.logger.error(f"❌ AGUI visualization tool failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

### **2.5 Deliverables**

- [ ] VisualizationEngineService updated for AGUI components
- [ ] `create_agui_visualization()` method implemented
- [ ] Chart component generation
- [ ] Dashboard component generation
- [ ] Table component generation
- [ ] AGUI schema integration
- [ ] MCP tool registered
- [ ] Unit tests for AGUI components
- [ ] Integration tests with semantic embeddings

---

## 📋 **Phase 3: Create Insights Business Analysis Agent** (Week 2, Days 1-2)

### **3.1 Goal**

Create InsightsBusinessAnalysisAgent that:
- Uses OpenAI LLM (not HF) for business analysis
- Calls EDA tools for structured data
- Reviews embeddings directly for unstructured data
- Uses Agentic Foundation SDK (not CrewAI)

### **3.2 Implementation**

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/agents/insights_business_analysis_agent.py`

```python
from foundations.agentic_foundation.agent_sdk.agent_base import AgentBase
from foundations.agentic_foundation.agui_schema_registry import AGUISchema
from typing import Dict, Any, List, Optional

class InsightsBusinessAnalysisAgent(AgentBase):
    """
    Business Analysis Agent for Insights Pillar.
    
    Uses OpenAI LLM (not HF) for business analysis.
    For structured data: Uses EDA tools, then interprets with OpenAI LLM.
    For unstructured data: Reviews embeddings directly with OpenAI LLM.
    """
    
    def __init__(self, ...):
        super().__init__(
            agent_name="InsightsBusinessAnalysisAgent",
            capabilities=["business_analysis", "eda_interpretation", "embedding_review"],
            required_roles=["librarian", "data_steward"],
            agui_schema=self._create_agui_schema(),
            ...
        )
        # Get LLM client from Agentic Foundation
        self.llm_client = self.get_llm_client()
        self.mcp_tools = self.get_mcp_tools()
    
    async def analyze_structured_data(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze structured data using EDA tools + LLM interpretation.
        
        Pattern:
        1. Get semantic embeddings (schema/metadata)
        2. Run EDA analysis tools (deterministic)
        3. LLM interprets EDA results (consistent - same EDA = same interpretation)
        """
        try:
            # Step 1: Get semantic embeddings for schema
            librarian = await self.get_smart_city_service("LibrarianService")
            embeddings = await librarian.get_embeddings(
                content_id=content_id,
                filters={"embedding_type": "schema"},
                user_context=user_context
            )
            
            if not embeddings:
                return {
                    "success": False,
                    "error": "No schema embeddings found",
                    "content_id": content_id
                }
            
            # Step 2: Run EDA analysis tools (via MCP tool)
            eda_results = await self.call_mcp_tool(
                "run_eda_analysis_tool",
                {
                    "content_id": content_id,
                    "analysis_types": ["statistics", "correlations", "distributions", "missing_values"]
                },
                user_context=user_context
            )
            
            if not eda_results.get("success"):
                return {
                    "success": False,
                    "error": "EDA analysis failed",
                    "eda_error": eda_results.get("error")
                }
            
            # Step 3: LLM interprets EDA results (OpenAI, not HF)
            interpretation = await self.llm_client.generate_analysis(
                prompt=self._build_interpretation_prompt(eda_results, embeddings),
                user_context=user_context
            )
            
            return {
                "success": True,
                "content_id": content_id,
                "eda_results": eda_results.get("eda_results"),  # Deterministic
                "interpretation": interpretation,  # Consistent (same EDA = same interpretation)
                "embeddings_used": [emb.get("_key") for emb in embeddings]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Structured data analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content_id": content_id
            }
    
    async def analyze_unstructured_data(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze unstructured data by reviewing embeddings directly.
        
        Pattern:
        1. Get semantic embeddings (chunk embeddings)
        2. LLM reviews embeddings directly
        3. Generates business narrative
        """
        try:
            # Get chunk embeddings
            librarian = await self.get_smart_city_service("LibrarianService")
            embeddings = await librarian.get_embeddings(
                content_id=content_id,
                filters={"embedding_type": "chunk"},
                user_context=user_context
            )
            
            if not embeddings:
                return {
                    "success": False,
                    "error": "No chunk embeddings found",
                    "content_id": content_id
                }
            
            # LLM reviews embeddings directly
            analysis = await self.llm_client.generate_analysis(
                prompt=self._build_unstructured_prompt(embeddings),
                user_context=user_context
            )
            
            return {
                "success": True,
                "content_id": content_id,
                "analysis": analysis,
                "embeddings_reviewed": [emb.get("_key") for emb in embeddings]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Unstructured data analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content_id": content_id
            }
    
    def _build_interpretation_prompt(
        self,
        eda_results: Dict[str, Any],
        embeddings: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for LLM to interpret EDA results."""
        prompt = f"""
        You are a business analyst reviewing exploratory data analysis (EDA) results.
        
        EDA Results:
        {json.dumps(eda_results, indent=2)}
        
        Schema Information:
        {json.dumps([emb.get("column_name") for emb in embeddings], indent=2)}
        
        Please provide:
        1. Key insights from the data
        2. Business implications
        3. Recommendations
        4. Potential issues or concerns
        
        Be specific and reference the EDA results in your analysis.
        """
        return prompt
    
    def _build_unstructured_prompt(
        self,
        embeddings: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for LLM to review unstructured embeddings."""
        # Extract text from embeddings
        texts = [emb.get("text") or emb.get("content") for emb in embeddings if emb.get("text") or emb.get("content")]
        
        prompt = f"""
        You are a business analyst reviewing unstructured content.
        
        Content Chunks:
        {json.dumps(texts[:10], indent=2)}  # First 10 chunks
        
        Please provide:
        1. Key themes and topics
        2. Business insights
        3. Recommendations
        4. Summary
        
        Be specific and reference the content in your analysis.
        """
        return prompt
    
    def _create_agui_schema(self) -> AGUISchema:
        """Create AGUI schema for business analysis agent."""
        # Use standard insights liaison schema
        from foundations.agentic_foundation.agui_schema_helpers import create_insights_liaison_agui_schema
        return create_insights_liaison_agui_schema()
```

### **3.3 Deliverables**

- [ ] InsightsBusinessAnalysisAgent created
- [ ] Uses Agentic Foundation SDK (not CrewAI)
- [ ] `analyze_structured_data()` method
- [ ] `analyze_unstructured_data()` method
- [ ] EDA tool integration
- [ ] OpenAI LLM integration
- [ ] Unit tests
- [ ] Integration tests

---

## 📋 **Phase 4: Create Semantic Enrichment Gateway** (Week 2, Days 3-4)

### **4.1 Goal**

Create SemanticEnrichmentGateway that maintains security boundary while enabling semantic enrichment when embeddings don't have enough information.

### **4.2 Implementation**

**File:** `backend/business_enablement/enabling_services/semantic_enrichment_gateway/semantic_enrichment_gateway.py`

```python
class SemanticEnrichmentGateway(RealmServiceBase):
    """
    Semantic Enrichment Gateway - Maintains security boundary.
    
    WHAT: Enables semantic enrichment without exposing parsed data
    HOW: Requests enrichment, enrichment service creates new embeddings, adds to semantic layer
    """
    
    async def enrich_semantic_layer(
        self,
        content_id: str,
        enrichment_request: Dict[str, Any],  # What semantic info is needed
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Request semantic enrichment without exposing parsed data.
        
        Flow:
        1. Platform identifies what semantic info is missing
        2. Requests enrichment (describes what's needed, not raw data)
        3. Enrichment service (runs in secure boundary) processes parsed data
        4. Creates new embeddings with requested semantic info
        5. Adds to semantic layer
        6. Returns new embedding IDs (not raw data)
        """
        try:
            # Step 1: Validate request (what semantic info is needed)
            enrichment_type = enrichment_request.get("type")  # "column_values", "statistics", etc.
            
            if not enrichment_type:
                return {
                    "success": False,
                    "error": "Enrichment type is required"
                }
            
            # Step 2: Request enrichment from secure service
            # This service runs in secure boundary and can access parsed data
            enrichment_service = await self._get_enrichment_service()
            
            if not enrichment_service:
                return {
                    "success": False,
                    "error": "Enrichment service not available"
                }
            
            # Step 3: Enrichment service processes parsed data and creates embeddings
            new_embeddings = await enrichment_service.create_enrichment_embeddings(
                content_id=content_id,
                enrichment_type=enrichment_type,
                filters=enrichment_request.get("filters"),  # Which columns/rows needed
                user_context=user_context
            )
            
            if not new_embeddings:
                return {
                    "success": False,
                    "error": "Enrichment failed to create embeddings"
                }
            
            # Step 4: Store new embeddings in semantic layer
            librarian = await self.get_librarian_api()
            content_metadata = await librarian.get_content_metadata(content_id, user_context)
            file_id = content_metadata.get("file_id")
            
            store_result = await librarian.store_embeddings(
                content_id=content_id,
                file_id=file_id,
                embeddings=new_embeddings,  # New semantic data, not raw parsed data
                user_context=user_context
            )
            
            if not store_result.get("success"):
                return {
                    "success": False,
                    "error": "Failed to store enriched embeddings"
                }
            
            # Step 5: Return embedding IDs (platform can query these)
            return {
                "success": True,
                "embedding_ids": [emb.get("_key") for emb in new_embeddings],
                "enrichment_type": enrichment_type,
                "count": len(new_embeddings)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Semantic enrichment failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_enrichment_service(self):
        """Get enrichment service (runs in secure boundary)."""
        # This service can access parsed data
        # It's a separate service that runs in secure boundary
        # For now, return None (will be implemented separately)
        return None
```

### **4.3 Enrichment Service (Secure Boundary)**

**File:** `backend/business_enablement/enabling_services/semantic_enrichment_service/semantic_enrichment_service.py`

```python
class SemanticEnrichmentService(RealmServiceBase):
    """
    Semantic Enrichment Service - Runs in secure boundary.
    
    This service CAN access parsed data to create new embeddings.
    It's the only service that crosses the security boundary.
    """
    
    async def create_enrichment_embeddings(
        self,
        content_id: str,
        enrichment_type: str,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Create new embeddings from parsed data.
        
        This is the ONLY place where parsed data is accessed.
        New embeddings are created and returned (not raw data).
        """
        try:
            # Step 1: Get parsed data (ONLY place this happens)
            content_steward = await self.get_content_steward_api()
            content_metadata = await self.librarian.get_content_metadata(content_id, user_context)
            parsed_file_id = content_metadata.get("parsed_file_id")
            
            if not parsed_file_id:
                return []
            
            # Get parsed file
            parsed_file = await content_steward.get_file(parsed_file_id, user_context)
            if not parsed_file:
                return []
            
            # Step 2: Process parsed data based on enrichment type
            if enrichment_type == "column_values":
                new_embeddings = await self._create_column_value_embeddings(
                    parsed_file, filters, user_context
                )
            elif enrichment_type == "statistics":
                new_embeddings = await self._create_statistics_embeddings(
                    parsed_file, filters, user_context
                )
            else:
                return []
            
            # Step 3: Return new embeddings (not raw data)
            return new_embeddings
            
        except Exception as e:
            self.logger.error(f"❌ Enrichment embedding creation failed: {e}")
            return []
    
    async def _create_column_value_embeddings(
        self,
        parsed_file: Dict[str, Any],
        filters: Optional[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create embeddings for specific column values."""
        # Process parsed file and create embeddings
        # This is where we'd use HF inference agent if needed
        # For now, return empty list (implementation detail)
        return []
    
    async def _create_statistics_embeddings(
        self,
        parsed_file: Dict[str, Any],
        filters: Optional[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create embeddings for statistics."""
        # Process parsed file and create embeddings
        # This is where we'd use HF inference agent if needed
        # For now, return empty list (implementation detail)
        return []
```

### **4.4 Deliverables**

- [ ] SemanticEnrichmentGateway created
- [ ] `enrich_semantic_layer()` method
- [ ] Security boundary maintained
- [ ] SemanticEnrichmentService created (secure boundary)
- [ ] Enrichment embedding creation
- [ ] Unit tests
- [ ] Security boundary validation tests

---

## 📋 **Phase 5: Query Generation Agent + InsightsLiaisonAgent Enhancement** (Week 2, Days 5-6)

### **5.1 Goal**

Create query generation agent using OpenAI LLM and enhance InsightsLiaisonAgent with:
- Conversational drill-down capabilities
- Full websocket integration for E2E functionality
- Natural language query processing
- Integration with InsightsOrchestrator and enabling services

### **5.2 Architecture Decision: OpenAI LLM vs HF Models**

**Decision:** Use OpenAI LLM instead of HF models for:
- ✅ Simpler architecture (no HF infrastructure needed)
- ✅ Already integrated (uses existing LLM abstraction)
- ✅ More flexible and context-aware
- ✅ No table size limits (works with schema metadata)
- ✅ Maintains security boundary (works with semantic embeddings)

**HF Models Deferred:** Can be added later if needed for offline/private deployments or cost-sensitive scenarios.

### **5.3 Implementation**

#### **5.3.1 Create InsightsQueryAgent (OpenAI-based)**

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/agents/insights_query_agent.py`

```python
class InsightsQueryAgent(AgentBase):
    """
    Query Generation Agent - Uses OpenAI LLM for query generation.
    
    Only used when semantic search isn't sufficient.
    Generates query specs (not raw SQL/Pandas code) based on schema metadata.
    """
    
    async def generate_query_from_nl(
        self,
        natural_language_query: str,
        content_id: str,
        schema_metadata: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate SQL/Pandas query from natural language using OpenAI LLM.
        
        Flow:
        1. Get schema metadata from embeddings
        2. Use OpenAI LLM to generate query spec
        3. Return query spec (not raw code)
        
        Args:
            natural_language_query: User's natural language query
            content_id: Content ID for context
            schema_metadata: Schema metadata from embeddings
            user_context: User context for security/tenant validation
        
        Returns:
            Query spec dictionary with:
            - query_type: "sql" | "pandas" | "semantic_search"
            - query_spec: Query specification
            - confidence: Confidence score
        """
        # Use OpenAI LLM (via get_business_abstraction("llm"))
        # Generate query based on schema metadata
        # Return query spec
        pass
```

#### **5.3.2 Enhance InsightsLiaisonAgent**

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/agents/insights_liaison_agent.py`

**Key Enhancements:**

1. **Conversational Drill-Down:**
   - Handle follow-up questions (e.g., "I see 3 customers 90+ days late. Which ones are they?")
   - Maintain conversation context
   - Extract intent and entities from queries
   - Route to appropriate services/orchestrators

2. **Natural Language Query Processing:**
   - Use OpenAI LLM to understand user intent
   - Generate visualization specs from NL requests
   - Call InsightsQueryAgent when semantic search isn't sufficient
   - Integrate with InsightsOrchestrator for analysis

3. **Integration with Enabling Services:**
   - Call DataAnalyzerService via MCP tools
   - Call VisualizationEngineService for visualizations
   - Call InsightsOrchestrator for analysis workflows
   - Use SemanticEnrichmentGateway when needed

**Enhanced Methods:**

```python
async def process_conversation(
    self,
    query: str,
    conversation_id: str,
    user_context: UserContext
) -> Dict[str, Any]:
    """
    Process conversational query with drill-down support.
    
    Handles:
    - Initial analysis requests
    - Follow-up drill-down questions
    - Visualization requests
    - Comparison queries
    - Trend analysis
    """
    # Use OpenAI LLM to understand intent
    # Route to appropriate service/orchestrator
    # Return structured response with AGUI components
    pass

async def handle_drill_down_query(
    self,
    query: str,
    previous_analysis: Dict[str, Any],
    user_context: UserContext
) -> Dict[str, Any]:
    """
    Handle drill-down queries (e.g., "which ones are they?").
    
    Extracts entities from previous analysis and query,
    then queries specific records via Data Solution Orchestrator.
    """
    # Extract entities from query and previous analysis
    # Generate filter criteria
    # Query via Data Solution Orchestrator
    # Return specific records
    pass

async def generate_visualization_from_nl(
    self,
    query: str,
    content_id: str,
    user_context: UserContext
) -> Dict[str, Any]:
    """
    Generate visualization from natural language query.
    
    Flow:
    1. Use OpenAI LLM to interpret query and generate visualization spec
    2. Pass spec to VisualizationEngineService
    3. Service generates AGUI component deterministically
    """
    # Use OpenAI LLM to generate visualization spec
    # Call VisualizationEngineService
    # Return AGUI component
    pass
```

#### **5.3.3 Create Unified Agent WebSocket SDK (Experience Foundation)**

**File:** `foundations/experience_foundation/sdk/unified_agent_websocket_sdk.py` (NEW)

```python
class UnifiedAgentWebSocketSDK:
    """
    Unified Agent WebSocket SDK - Experience Foundation
    
    Provides unified websocket endpoint for all agents (Guide + Liaison).
    Single connection per user, routes messages to appropriate agent.
    
    WHAT (Experience SDK): I provide unified agent websocket for user-facing communication
    HOW (SDK Implementation): I compose Experience WebSocketSDK + Agentic Foundation for routing
    """
    
    async def handle_agent_message(
        self,
        websocket: WebSocket,
        message: Dict[str, Any],
        session_token: str
    ) -> Dict[str, Any]:
        """
        Handle agent message with routing.
        
        Routes to appropriate agent based on message.agent_type and message.pillar.
        """
        agent_type = message.get("agent_type", "guide")
        pillar = message.get("pillar")
        user_message = message.get("message", "")
        conversation_id = message.get("conversation_id")
        
        # Route to agent via Agentic Foundation
        if agent_type == "guide":
            agent = await self._get_guide_agent()
            response = await agent.handle_user_message(user_message, session_token)
        elif agent_type == "liaison":
            if not pillar:
                return {"type": "error", "message": "pillar is required for liaison agent"}
            agent = await self._get_liaison_agent(pillar)
            user_context = await self._create_user_context(session_token)
            response = await agent.process_user_query(
                query=user_message,
                conversation_id=conversation_id or f"{pillar}_{session_token}",
                user_context=user_context
            )
        else:
            return {"type": "error", "message": f"Unknown agent_type: {agent_type}"}
        
        # Add routing metadata
        response["agent_type"] = agent_type
        if pillar:
            response["pillar"] = pillar
        
        return response
```

**File:** `foundations/experience_foundation/experience_foundation_service.py` (update)

```python
# Add unified agent websocket SDK
self._unified_agent_websocket_sdk: Optional[UnifiedAgentWebSocketSDK] = None

async def get_unified_agent_websocket_sdk(self) -> Optional[UnifiedAgentWebSocketSDK]:
    """Get Unified Agent WebSocket SDK instance."""
    if not self._unified_agent_websocket_sdk:
        self._unified_agent_websocket_sdk = UnifiedAgentWebSocketSDK(self)
        await self._unified_agent_websocket_sdk.initialize()
    return self._unified_agent_websocket_sdk
```

#### **5.3.4 Create Unified WebSocket Endpoint**

**File:** `backend/api/websocket_router.py` (update - add unified endpoint)

```python
@router.websocket("/api/ws/agent")
async def unified_agent_websocket(websocket: WebSocket, session_token: str = Query(None)):
    """
    Unified Agent WebSocket endpoint.
    
    Handles all agent communications (Guide + Liaison) via message routing.
    Single connection per user, routes messages to appropriate agent.
    
    Uses Experience Foundation UnifiedAgentWebSocketSDK.
    """
    await websocket.accept()
    logger.info(f"🔌 Unified Agent WebSocket connection accepted (session_token: {session_token})")
    
    try:
        # Get Experience Foundation
        experience_foundation = await get_experience_foundation()
        if not experience_foundation:
            await websocket.close(code=4001, reason="Experience Foundation not available")
            return
        
        unified_sdk = await experience_foundation.get_unified_agent_websocket_sdk()
        if not unified_sdk:
            await websocket.close(code=4002, reason="Unified Agent WebSocket SDK not available")
            return
        
        # Message loop
        try:
            while True:
                message_data = await websocket.receive_json()
                
                # Handle message via unified SDK
                response = await unified_sdk.handle_agent_message(
                    websocket=websocket,
                    message=message_data,
                    session_token=session_token or "anonymous"
                )
                
                # Send response
                await websocket.send_json(response)
                
        except WebSocketDisconnect:
            logger.info(f"🔌 Unified Agent WebSocket disconnected")
        except Exception as e:
            logger.error(f"❌ Error in Unified Agent WebSocket: {e}")
            await websocket.send_json({
                "type": "error",
                "message": f"Internal error: {str(e)}"
            })
    except Exception as e:
        logger.error(f"❌ Unified Agent WebSocket setup failed: {e}")
        await websocket.close(code=4003, reason=f"Setup failed: {str(e)}")
```

**Note:** Keep existing endpoints (`/api/ws/guide`, `/api/ws/liaison/{pillar}`) for backward compatibility during migration.

#### **5.3.5 Frontend Integration**

**Frontend Updates Required:**

1. **Create Unified WebSocket Hook:**
   - **File:** `frontend/shared/hooks/useUnifiedAgentChat.ts` (NEW)
   - Single websocket connection to `/api/ws/agent`
   - Manages active agent state (guide vs liaison + pillar)
   - Handles conversation context per agent
   - Supports agent switching without reconnection

2. **Update Insights Pillar UI:**
   - Use `useUnifiedAgentChat` hook
   - Set active agent to `{type: "liaison", pillar: "insights"}` when in Insights pillar
   - Display agent responses with AGUI components
   - Support visualization rendering from agent responses
   - Handle drill-down query flow

3. **Message Format:**
   ```typescript
   interface AgentMessage {
     agent_type: "guide" | "liaison";
     pillar?: "content" | "insights" | "operations" | "business_outcomes";
     message: string;
     conversation_id?: string;
   }
   
   interface AgentResponse {
     agent_type: "guide" | "liaison";
     pillar?: string;
     message: string;
     conversation_id: string;
     type: "message" | "error" | "visualization" | "analysis" | "drill_down";
     data?: any;  // AGUI components, analysis results, etc.
     visualization?: any;  // AGUI visualization component
   }
   ```

### **5.4 Use Cases (from MVP Description)**

Based on `MVP_Description_For_Business_and_Technical_Readiness.md`:

1. **Initial Analysis:**
   - User: "Analyze my customer data"
   - Agent: Calls InsightsOrchestrator → Returns business analysis + visualization

2. **Drill-Down Queries:**
   - User: "I see I have a lot of customers who are more than 90 days late. Can you show me who those customers are?"
   - Agent: Extracts filter criteria → Queries via Data Solution Orchestrator → Returns specific records

3. **Visualization Requests:**
   - User: "Show me a chart of revenue by region"
   - Agent: Generates visualization spec → Calls VisualizationEngineService → Returns AGUI chart component

4. **Follow-Up Questions:**
   - User: "What's the trend in customer satisfaction?"
   - Agent: Maintains context → Calls DataAnalyzerService for trend analysis → Returns trend visualization

### **5.5 Deliverables**

- [ ] InsightsQueryAgent created (OpenAI-based)
- [ ] InsightsLiaisonAgent enhanced with:
  - [ ] Conversational drill-down capabilities
  - [ ] Natural language query processing
  - [ ] Integration with InsightsOrchestrator
  - [ ] Integration with enabling services (via MCP)
- [ ] Unified Agent WebSocket SDK created (Experience Foundation):
  - [ ] `UnifiedAgentWebSocketSDK` in Experience Foundation SDK
  - [ ] Agent routing logic (Guide + Liaison)
  - [ ] Session management integration
  - [ ] Conversation context management
- [ ] Unified WebSocket endpoint created (`/api/ws/agent`):
  - [ ] Uses Experience Foundation Unified SDK
  - [ ] Routes messages to appropriate agents
  - [ ] Handles Guide and Liaison agents
- [ ] Frontend integration:
  - [ ] `useUnifiedAgentChat` hook created
  - [ ] Insights pillar UI connected to unified endpoint
  - [ ] Agent switching logic
  - [ ] AGUI component rendering
  - [ ] Conversation history management
- [ ] Unit tests for agents
- [ ] Integration tests for unified websocket E2E flow
- [ ] Documentation updated

---

## 📋 **Phase 6: Update InsightsOrchestrator** (Week 3, Days 1-2)

### **6.1 Goal**

Update InsightsOrchestrator to:
- Use Data Solution Orchestrator (same pattern as Content Pillar)
- Use semantic data layer via `orchestrate_data_expose()` (not raw parsed data)
- Integrate with new agents
- Use Semantic Enrichment Gateway when needed
- Verify no CrewAI usage

### **6.2 Key Architectural Change**

**CRITICAL:** Insights Pillar must use Data Solution Orchestrator (same pattern as Content Pillar).

**Before (Direct Access):**
```python
# ❌ Direct semantic data access (bypasses Data Solution Orchestrator)
embeddings = await self.librarian.get_embeddings(...)
```

**After (Data Solution Orchestrator):**
```python
# ✅ Use Data Solution Orchestrator (same pattern as Content)
data_solution = await self._get_data_solution_orchestrator()
expose_result = await data_solution.orchestrate_data_expose(
    file_id=file_id,
    parsed_file_id=parsed_file_id,
    user_context=user_context
)
embeddings = expose_result.get("embeddings", [])
```

### **6.3 Implementation**

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/insights_orchestrator.py`

**Key Updates:**

#### **6.3.1 Add Data Solution Orchestrator Helper**

```python
async def _get_data_solution_orchestrator(self):
    """
    Get Data Solution Orchestrator Service via Curator discovery.
    
    Same pattern as ContentOrchestrator.
    This is the ONLY way to access data operations in the platform.
    
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

#### **6.3.2 Update analyze_content_for_insights()**

```python
async def analyze_content_for_insights(
    self,
    content_id: str,
    user_query: Optional[str] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze content using semantic data layer with Data Solution Orchestrator.
    
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
        
        # Step 2: Get content metadata to extract file_id
        librarian = await self.get_librarian_api()
        content_metadata = await librarian.get_content_metadata(content_id, user_context)
        file_id = content_metadata.get("file_id")
        parsed_file_id = content_metadata.get("parsed_file_id")
        
        # Step 3: Expose semantic data via Data Solution Orchestrator (PRIMARY PATHWAY)
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
            # Use Business Analysis Agent with EDA tools
            analysis_result = await business_agent.analyze_structured_data(
                content_id=content_id,
                user_context=user_context
            )
        else:
            # Use Business Analysis Agent with direct embedding review
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
                # Re-analyze with enriched embeddings if needed
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

#### **6.3.3 Add Helper Methods**

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

### **6.3 Deliverables**

- [ ] InsightsOrchestrator updated
- [ ] Semantic data layer integration
- [ ] Agent integration
- [ ] Semantic Enrichment Gateway integration
- [ ] No CrewAI usage verified
- [ ] Unit tests
- [ ] Integration tests

---

## 📋 **Phase 7: Verify No CrewAI Usage** (Week 3, Day 3)

### **7.1 Goal**

Verify that no CrewAI references exist in the codebase and ensure all agents use Agentic Foundation SDK.

**Note:** CrewAI was already removed in previous cycles. This phase is a verification step to ensure no CrewAI patterns or dependencies were accidentally introduced.

### **7.2 Tasks**

- [ ] Search codebase for any CrewAI imports or references
- [ ] Verify all agent classes extend `AgentBase` (not CrewAI classes)
- [ ] Verify all agent initialization uses Agentic Foundation SDK
- [ ] Verify no CrewAI patterns in agent code
- [ ] Update tests to ensure no CrewAI dependencies
- [ ] Document verification results

---

## 📋 **Phase 8: Testing & Validation** (Week 3, Days 4-5)

### **8.1 Goal**

Comprehensive testing of all components.

### **8.2 Test Coverage**

- [ ] Unit tests for DataAnalyzerService EDA tools
- [ ] Unit tests for VisualizationEngineService AGUI components
- [ ] Unit tests for InsightsBusinessAnalysisAgent
- [ ] Unit tests for SemanticEnrichmentGateway
- [ ] Unit tests for InsightsQueryAgent
- [ ] Unit tests for InsightsLiaisonAgent enhancements
- [ ] Integration tests for websocket E2E flow
- [ ] Integration tests with semantic embeddings
- [ ] Security boundary validation tests
- [ ] End-to-end workflow tests
- [ ] Performance tests

---

## ✅ **Success Criteria**

### **Phase 1 Success:**
- [ ] DataAnalyzerService exposes EDA tools
- [ ] EDA tools work with semantic embeddings
- [ ] Deterministic results (same input = same output)
- [ ] MCP tool registered and working

### **Phase 2 Success:**
- [ ] VisualizationEngineService generates AGUI components
- [ ] AGUI components are schema-compliant
- [ ] MCP tool registered and working

### **Phase 3 Success:**
- [ ] InsightsBusinessAnalysisAgent created
- [ ] Uses Agentic Foundation SDK (not CrewAI)
- [ ] Structured data analysis works
- [ ] Unstructured data analysis works

### **Phase 4 Success:**
- [ ] SemanticEnrichmentGateway created
- [ ] Security boundary maintained
- [ ] Enrichment works without exposing parsed data

### **Phase 5 Success:**
- [ ] InsightsQueryAgent created (OpenAI-based)
- [ ] InsightsLiaisonAgent enhanced with:
  - [ ] Conversational drill-down capabilities
  - [ ] Natural language query processing
  - [ ] Integration with InsightsOrchestrator
  - [ ] Integration with enabling services
- [ ] Unified Agent WebSocket SDK created (Experience Foundation):
  - [ ] SDK handles Guide and Liaison agent routing
  - [ ] Session management integrated
  - [ ] Conversation context managed
- [ ] Unified WebSocket endpoint created (`/api/ws/agent`):
  - [ ] Single endpoint for all agents
  - [ ] Message routing works correctly
  - [ ] Agent switching without reconnection
- [ ] Frontend integration complete:
  - [ ] Unified websocket hook created
  - [ ] Insights pillar UI connected
  - [ ] Agent switching works
  - [ ] AGUI component rendering works
- [ ] E2E websocket flow tested:
  - [ ] Guide agent communication
  - [ ] Insights liaison agent communication
  - [ ] Agent switching during conversation
  - [ ] Conversation history persistence
- [ ] Query generation works (when semantic search insufficient)
- [ ] Visualization spec generation works

### **Phase 6 Success:**
- [ ] InsightsOrchestrator updated
- [ ] Semantic data layer integration working
- [ ] All agents integrated
- [ ] No CrewAI usage verified

### **Phase 7 Success:**
- [ ] No CrewAI references found in codebase
- [ ] All agents verified to use Agentic Foundation SDK
- [ ] Verification documented

### **Phase 8 Success:**
- [ ] All tests passing
- [ ] Security boundary validated
- [ ] End-to-end workflow working

---

## 📊 **Timeline Summary**

| Phase | Duration | Focus |
|-------|----------|-------|
| **Phase 1** | Week 1, Days 1-3 | DataAnalyzerService EDA Tools |
| **Phase 2** | Week 1, Days 4-5 | VisualizationEngineService AGUI |
| **Phase 3** | Week 2, Days 1-2 | Business Analysis Agent |
| **Phase 4** | Week 2, Days 3-4 | Semantic Enrichment Gateway |
| **Phase 5** | Week 2, Days 5-6 | Query Agent + InsightsLiaisonAgent + WebSocket |
| **Phase 6** | Week 3, Days 1-2 | InsightsOrchestrator Update |
| **Phase 7** | Week 3, Day 3 | Verify No CrewAI Usage |
| **Phase 8** | Week 3, Days 4-5 | Testing & Validation |

**Total:** 3 weeks to complete implementation

---

## 🎯 **Key Principles**

1. **Semantic Data Layer is Security Boundary** - Platform only uses semantic data
2. **Structured Data:** EDA Tools → OpenAI LLM (deterministic)
3. **Unstructured Data:** Direct embedding review with OpenAI LLM
4. **Visualization:** AGUI components (not raw code)
5. **OpenAI LLM for Query & Visualization Spec Generation** - Use existing integration (simpler, more flexible)
6. **Agentic Foundation SDK** - Use custom foundation (CrewAI already removed)
7. **InsightsLiaisonAgent** - Conversational interface with full websocket integration
8. **Showcase Use Case** - Insights pillar demonstrates capabilities

---

**Last Updated:** December 20, 2025  
**Status:** 🚀 **Implementation Plan Ready**  
**Next Action:** Begin Phase 1 - Build DataAnalyzerService EDA Tools

