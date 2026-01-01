# Insights Pillar: Integrated Three-Dimensional Refactoring Plan

**Date:** November 11, 2025 (Updated)  
**Status:** 🎯 **READY TO EXECUTE** (Frontend-First Approach)

---

## 🎯 Executive Summary

Transform the Insights Pillar through three coordinated dimensions:

1. **Architecture**: Convert from Business Enablement Pillar → Platform Enabler (move MVP logic to orchestrator)
2. **Semantic APIs**: Adopt consistent semantic API pattern (like Content Pillar)
3. **Frontend UX**: Streamline to unified two-section layout

**Strategic Approach:** Frontend-First (define target UX, then build backend to serve it)  
**Pattern:** Follow Content Pillar refactoring pattern  
**Timeline:** 6-8 days (phased execution)  
**Risk:** Low (incremental, tested at each phase)

**Recent Update (Nov 11):**
- ✅ **Agentic Foundation Cleanup Complete** - All business services moved to `enabling_services/`
- ✅ **Architecture Clarified** - Pure layer separation confirmed
- 📋 **API Contract Defined** - See `API_CONTRACT_INSIGHTS_PILLAR.md`
- 🎨 **Target UX Defined** - See `INSIGHTS_PILLAR_REFACTORING_PLAN.md`

---

## 📊 Current State Analysis

### **Backend Architecture**

```
❌ BEFORE (Current):
backend/business_enablement/pillars/insights_pillar/
  └─ InsightsPillarService (1,088+ lines)
     ├─ MVP-specific logic MIXED with enabling capabilities
     ├─ micro_modules/ (DataAnalyzer, VisualizationEngine, APGModeProcessor, etc.)
     ├─ agents/ (InsightsLiaisonAgent, InsightsAnalysisAgent)
     └─ mcp_server/ (InsightsPillarMCPServer)

backend/business_enablement/business_orchestrator/use_cases/mvp/
  └─ insights_orchestrator/ (INCOMPLETE - only 57 lines)
     └─ InsightsOrchestrator (STUB)
```

### **API Layer**

```
❌ BEFORE (Current):
POST /api/mvp/insights/analyze  # Non-semantic, unclear purpose
GET  /api/mvp/insights/health   # Non-semantic
```

### **Frontend Structure**

```
❌ BEFORE (Current):
app/pillars/insights/page.tsx        # Basic insights page
app/pillars/insight/page.tsx         # VARK/APG toggle page (DUPLICATE!)
  ├─ VARKFlow component
  ├─ APGFlow component
  ├─ VARK/APG mode toggle (CONFUSING)
  └─ Insights Liaison Agent rendered inline (WRONG PLACEMENT)
```

---

## ✅ Target State (After Refactoring)

### **Architecture: Platform Enabler Pattern**

```
✅ AFTER (Target):

# InsightsPillar = Pure Enabling Service
backend/business_enablement/pillars/insights_pillar/
  └─ InsightsPillarService (ENABLING CAPABILITIES ONLY)
     ├─ micro_modules/ (core capabilities, no MVP logic)
     │  ├─ data_analyzer.py          # Generic data analysis
     │  ├─ visualization_engine.py   # Chart/visualization generation
     │  ├─ insights_generator.py     # Generic insights extraction
     │  ├─ metrics_calculator.py     # Statistical calculations
     │  └─ unstructured_analyzer.py  # Text/AAR analysis
     ├─ agents/ (enabling agents)
     │  ├─ insights_liaison_agent.py
     │  └─ insights_analysis_agent.py
     └─ mcp_server/ (capability tools)

# InsightsOrchestrator = MVP-Specific Logic
backend/business_enablement/business_orchestrator/use_cases/mvp/
  └─ insights_orchestrator/
     └─ InsightsOrchestrator (MVP ORCHESTRATION)
        ├─ Structured data analysis workflow
        ├─ Unstructured data analysis workflow
        ├─ VARK-style presentation logic
        ├─ Navy AAR processing workflow
        └─ Uses InsightsPillar enabling services
```

### **Semantic APIs: Clear User Journey**

```
✅ AFTER (Semantic):

# Semantic Insights Router
backend/experience/api/semantic/insights_pillar_router.py

POST /api/insights-pillar/analyze-content-for-insights
  Body: {
    source_type: 'file' | 'metadata',
    file_id?: string,
    content_type: 'structured' | 'unstructured' | 'hybrid',
    analysis_options?: {...}
  }

POST /api/insights-pillar/query-analysis-results
  Body: {
    query: "Show me accounts over 90 days late",
    analysis_id: string,
    query_type?: 'table' | 'chart' | 'summary'
  }

GET  /api/insights-pillar/get-analysis-results/{analysis_id}
GET  /api/insights-pillar/get-visualizations/{analysis_id}
GET  /api/insights-pillar/list-available-analyses
GET  /api/insights-pillar/health
```

### **Frontend UX: Unified Two-Section Layout**

```
✅ AFTER (Streamlined):

app/pillars/insights/page.tsx  # SINGLE unified page
  ├─ Header
  ├─ Section 1: Insights from Structured Data
  │  ├─ File/Metadata Selector
  │  ├─ Analysis Trigger
  │  └─ InsightsSummaryDisplay (Text | Table | Charts tabs)
  │
  └─ Section 2: Insights from Unstructured Data
     ├─ File/Metadata Selector
     ├─ Analysis Trigger (includes AAR-specific options)
     └─ InsightsSummaryDisplay (Text | Table | Charts tabs)
        └─ Navy AAR special section (when applicable)

# Side Panel (not inline)
Insights Liaison Agent (NLP query interface)
```

---

## 📋 Phase 0: Target State Definition (COMPLETE ✅)

**Status:** Complete (Nov 11, 2025)

### **Purpose**
Define the target frontend UX, API contracts, and backend architecture BEFORE implementation begins. This ensures we build toward a clear vision and avoid rework.

### **Deliverables**

#### ✅ **1. Target Frontend UX**
**Document:** `INSIGHTS_PILLAR_REFACTORING_PLAN.md`

**Key Decisions:**
- **Unified Two-Section Layout**: Structured Data Insights + Unstructured Data Insights
- **3-Way Summary Display**: Text | Table | Charts (consistent across both sections)
- **Navy AAR Analysis**: Expandable section below 3-way summary (not separate mode)
- **Agent Placement**: Side panel (not inline)
- **Metadata Integration**: "Use Extracted Metadata" option from Content Pillar (ArangoDB)
- **NLP Query Interface**: Conversational analytics through Insights Liaison Agent

**Target User Experience:**
```
┌─────────────────────────────────────────────────────────────┐
│  Insights Pillar                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Section 1: Insights from Structured Data               │
│  ├─ [Select File ▼] or [Use Extracted Metadata 🔒]        │
│  ├─ [Analyze Content] ──────────────────────────►          │
│  └─ Results:                                                │
│     ┌─────────────────────────────────────────┐            │
│     │ [Text] [Table] [Charts]                 │            │
│     │ • Business narrative summary            │            │
│     │ • Interactive data table                │            │
│     │ • Vega-Lite visualizations              │            │
│     └─────────────────────────────────────────┘            │
│                                                             │
│  📄 Section 2: Insights from Unstructured Data             │
│  ├─ [Select File ▼] or [Use Extracted Metadata 🔒]        │
│  ├─ [Analyze Content] [✓ Navy AAR Mode]                   │
│  └─ Results:                                                │
│     ┌─────────────────────────────────────────┐            │
│     │ [Text] [Table] [Charts]                 │            │
│     │ • Business narrative summary            │            │
│     │ • Extracted tables                      │            │
│     │ • Semantic visualizations               │            │
│     └─────────────────────────────────────────┘            │
│     ┌─────────────────────────────────────────┐            │
│     │ ▼ Navy AAR Analysis (Expandable)        │            │
│     │ • Lessons Learned                        │            │
│     │ • Risk Assessment                        │            │
│     │ • Recommendations                        │            │
│     │ • Timeline Visualization                 │            │
│     └─────────────────────────────────────────┘            │
│                                                             │
└─────────────────────────────────────────────────────────────┘

[Side Panel]
💬 Insights Liaison Agent
   "Show me all accounts over 90 days late"
   → Generates table dynamically
```

#### ✅ **2. API Contract**
**Document:** `API_CONTRACT_INSIGHTS_PILLAR.md`

**Core Endpoints:**
1. `POST /api/insights-pillar/analyze-content-for-insights`
   - Supports `source_type: 'file' | 'content_metadata'`
   - Returns 3-way summary (text/table/charts)
   - Optional AAR-specific analysis

2. `POST /api/insights-pillar/query-analysis-results`
   - NLP queries on analysis results
   - Dynamic table/chart generation

3. `GET /api/insights-pillar/get-available-content-metadata`
   - Query ArangoDB for Content Pillar metadata
   - "Data doesn't leave your walls" UX

4. `POST /api/insights-pillar/validate-content-metadata-for-insights`
   - Check if metadata is suitable for analysis

5. `GET /api/insights-pillar/get-analysis-results/{analysis_id}`
6. `GET /api/insights-pillar/get-analysis-visualizations/{analysis_id}`
7. `GET /api/insights-pillar/list-user-analyses`
8. `POST /api/insights-pillar/export-analysis-report`
9. `GET /api/insights-pillar/health`

**Key Design Decisions:**
- ✅ Semantic endpoint naming (descriptive, not terse)
- ✅ Content metadata from ArangoDB (query via Public Works abstractions)
- ✅ 3-way summary structure (always textual, conditional tabular/visualizations)
- ✅ AAR analysis as nested object (not separate endpoint)

#### ✅ **3. Backend Architecture (Corrected)**
**Document:** `AGENTIC_FOUNDATION_CLEANUP_COMPLETE.md`

**Layer Clarifications:**
- ✅ **Agentic Foundation**: Pure agent SDK infrastructure (MCP Server, Claude Desktop, Anthropic API)
- ✅ **Enabling Services**: Business services that enable capabilities (moved from `agentic_foundation/`)
  - `data_analyzer_service/`
  - `visualization_engine_service/`
  - `metrics_calculator_service/`
  - `insights_generator_service/` (moved)
  - `apg_processor_service/` (moved)
  - `insights_orchestrator_service/` (moved)

**Cleanup Actions Completed:**
- ✅ Deleted 3 duplicate services (1,979 lines)
- ✅ Moved 3 services to `enabling_services/` (1,701 lines)
- ✅ Updated imports in 2 files

**Service Placement:**
```
✅ CORRECTED ARCHITECTURE:

backend/business_enablement/enabling_services/
  ├─ data_analyzer_service/              # Data analysis
  ├─ visualization_engine_service/       # Chart generation
  ├─ metrics_calculator_service/         # Statistical calculations
  ├─ insights_generator_service/         # Insights extraction
  ├─ apg_processor_service/              # APG/AAR processing
  └─ insights_orchestrator_service/      # Workflow orchestration
  
backend/business_enablement/pillars/insights_pillar/
  └─ insights_pillar_composition_service.py  # Pillar composition
  
backend/business_enablement/business_orchestrator/use_cases/mvp/
  └─ insights_orchestrator/                   # MVP orchestrator (to be enhanced)
```

### **Phase 0 Outcomes**

✅ **Clear Target State Defined**
- Frontend UX is well-specified (components, layout, interactions)
- API contract is comprehensive (all endpoints defined)
- Backend architecture is clarified (correct layer placement)

✅ **Architecture Simplified**
- No more confusion about `agentic_foundation/` scope
- Business services correctly located in `enabling_services/`
- Ready for orchestrator pattern implementation

✅ **Frontend-First Strategy Validated**
- Building backend to serve defined UX (not reverse)
- API contract aligns with user workflows
- Reduces rework and guesswork

**Next Steps:** Proceed to Phase 1 & 2 implementation with confidence! 🚀

---

## 🏗️ Three-Dimensional Implementation Plan

### **DIMENSION 1: Architecture Refactoring**

#### **Phase 1A: Create MVP Insights Orchestrator (2 days)**

**Goal:** Create/enhance MVP Insights Orchestrator that uses enabling services

**Status Update (Nov 11):** ✅ Enabling services already correctly placed in `enabling_services/` (cleanup complete)

**Files to Create/Enhance:**
```
backend/business_enablement/business_orchestrator/use_cases/mvp/insights_orchestrator/
  ├─ insights_orchestrator.py           # Main MVP orchestrator (ENHANCE EXISTING)
  ├─ workflows/
  │  ├─ structured_analysis_workflow.py # VARK-style workflow
  │  ├─ unstructured_analysis_workflow.py # APG/AAR workflow
  │  └─ hybrid_analysis_workflow.py     # Combined workflow
  └─ mcp_server/
     └─ insights_orchestrator_mcp_server.py  # MVP-specific tools
```

**Enabling Services Used (Already in Place):**
```
✅ backend/business_enablement/enabling_services/
  ├─ data_analyzer_service/              # Data analysis
  ├─ visualization_engine_service/       # Chart generation  
  ├─ metrics_calculator_service/         # Statistical calculations
  ├─ insights_generator_service/         # Insights extraction
  ├─ apg_processor_service/              # APG/AAR processing
  └─ insights_orchestrator_service/      # Workflow orchestration (rename to avoid confusion?)
```

**InsightsOrchestrator Structure:**
```python
class InsightsOrchestrator(OrchestratorBase):
    """
    Insights Orchestrator for MVP use case.
    
    WHAT: Orchestrates MVP insights analysis workflows
    HOW: Delegates to enabling services (via Curator or direct access)
    
    Workflows:
    - Structured data analysis (VARK-style presentation)
    - Unstructured data analysis (APG/AAR processing)
    - Hybrid analysis (both)
    - NLP query processing
    """
    
    def __init__(self, business_orchestrator):
        super().__init__(
            service_name="InsightsOrchestratorService",
            realm_name=business_orchestrator.realm_name,
            platform_gateway=business_orchestrator.platform_gateway,
            di_container=business_orchestrator.di_container,
            business_orchestrator=business_orchestrator
        )
        
        # Access enabling services (via Curator or DI Container)
        # TODO: Migrate from direct imports to Curator-based discovery
        self.data_analyzer = None           # DataAnalyzerService
        self.visualization_engine = None    # VisualizationEngineService
        self.metrics_calculator = None      # MetricsCalculatorService
        self.insights_generator = None      # InsightsDataService
        self.apg_processor = None           # APGProcessingService
        
        # Smart City services
        self.data_steward = None            # Data access
        self.librarian = None               # Metadata management
        
    async def analyze_structured_content(
        self, 
        source_type: str,
        file_id: Optional[str] = None,
        metadata_id: Optional[str] = None,
        analysis_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        MVP workflow for structured data analysis.
        
        Workflow:
        1. Get data from DataSteward (file or metadata)
        2. Analyze data using InsightsPillar.data_analyzer
        3. Generate visualizations using InsightsPillar.visualization_engine
        4. Calculate metrics using InsightsPillar.metrics_calculator
        5. Generate insights summary using InsightsPillar.insights_generator
        6. Format for VARK-style presentation
        """
        pass
        
    async def analyze_unstructured_content(
        self,
        source_type: str,
        file_id: Optional[str] = None,
        text_content: Optional[str] = None,
        aar_specific: bool = False
    ) -> Dict[str, Any]:
        """
        MVP workflow for unstructured data analysis.
        
        Workflow:
        1. Get text content from DataSteward
        2. Analyze text using InsightsPillar.unstructured_analyzer
        3. Extract themes/patterns using InsightsPillar.insights_generator
        4. Generate narrative summary
        5. If AAR: extract lessons learned, risks, recommendations
        6. Format for APG-style presentation
        """
        pass
        
    async def query_analysis(
        self,
        query: str,
        analysis_id: str,
        query_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        MVP workflow for NLP queries on analysis results.
        
        Workflow:
        1. Parse natural language query
        2. Map to data operations (filter, aggregate, correlate)
        3. Execute query on cached analysis data
        4. Generate table/chart/summary based on query_type
        5. Provide explanation and follow-up suggestions
        """
        pass
```

**Migration Strategy:**
1. Keep current InsightsPillarService running
2. Build InsightsOrchestrator with NEW workflows
3. Test orchestrator workflows thoroughly
4. Update semantic API router to use orchestrator
5. Verify old endpoints still work (for rollback)

**Acceptance Criteria:**
- ✅ InsightsOrchestrator handles structured analysis workflow
- ✅ InsightsOrchestrator handles unstructured analysis workflow
- ✅ InsightsOrchestrator delegates to InsightsPillar services
- ✅ InsightsPillar refactored to pure enabling capabilities
- ✅ All tests pass

---

#### **Phase 1B: Refactor InsightsPillar to Pure Enabler (1 day)**

**Goal:** Remove MVP-specific logic from InsightsPillarService

**Files to Modify:**
```
backend/business_enablement/pillars/insights_pillar/
  └─ insights_pillar_service.py  # REMOVE MVP logic, keep capabilities
     ├─ analyze_data() → generic, no VARK/APG logic
     ├─ generate_visualizations() → generic
     ├─ calculate_metrics() → generic
     └─ extract_insights() → generic
```

**Refactoring Tasks:**
1. **Remove MVP-specific methods** (move to orchestrator):
   - VARK-style formatting
   - APG-specific processing
   - MVP workflow logic

2. **Keep enabling capabilities**:
   - Data analysis (generic)
   - Visualization generation (generic)
   - Metrics calculation (generic)
   - Insights extraction (generic)
   - Text analysis (generic)

3. **Add new micro-module** (if needed):
   ```python
   # micro_modules/unstructured_analyzer.py
   class UnstructuredAnalyzerModule:
       """Generic unstructured text analysis capabilities."""
       
       async def analyze_text(self, text: str, options: Dict) -> Dict:
           """Analyze unstructured text for themes, patterns, sentiment."""
           pass
           
       async def extract_entities(self, text: str) -> List[str]:
           """Extract named entities from text."""
           pass
           
       async def identify_themes(self, text: str) -> List[Dict]:
           """Identify key themes and topics."""
           pass
   ```

**Acceptance Criteria:**
- ✅ InsightsPillarService has NO MVP-specific logic
- ✅ All capabilities are generic and reusable
- ✅ Micro-modules are pure capability providers
- ✅ InsightsOrchestrator successfully uses refactored pillar

---

### **DIMENSION 2: Semantic API Migration**

#### **Phase 2A: Build Semantic Insights API (2 days)**

**Goal:** Create semantic API router following Content Pillar pattern

**Status Update (Nov 11):** ✅ API Contract defined - see `API_CONTRACT_INSIGHTS_PILLAR.md`

**Files to Create:**
```
backend/experience/api/semantic/insights_pillar_router.py
```

**API Contract Reference:**
See `API_CONTRACT_INSIGHTS_PILLAR.md` for complete endpoint specifications.

**Semantic Endpoints (Summary):**
```python
#!/usr/bin/env python3
"""
Semantic Insights Pillar Router

User-focused semantic API endpoints for insights pillar operations.
Uses semantic naming that aligns with user journeys and mental models.

Core Endpoints:
- POST /api/insights-pillar/analyze-content-for-insights
- POST /api/insights-pillar/query-analysis-results
- GET  /api/insights-pillar/get-available-content-metadata  # ArangoDB integration
- POST /api/insights-pillar/validate-content-metadata-for-insights
- GET  /api/insights-pillar/get-analysis-results/{analysis_id}
- GET  /api/insights-pillar/get-analysis-visualizations/{analysis_id}
- GET  /api/insights-pillar/list-user-analyses
- POST /api/insights-pillar/export-analysis-report
- GET  /api/insights-pillar/health

Key Features:
- Descriptive semantic naming (not terse abbreviations)
- Content metadata from ArangoDB (query via Public Works abstractions)
- 3-way summary structure (text/table/charts)
- AAR analysis as nested object (expandable section in UI)
- NLP query support for conversational analytics
"""

from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/insights-pillar", tags=["Insights Pillar"])

# Request/Response Models
class AnalyzeContentRequest(BaseModel):
    """Request model for content analysis."""
    source_type: str  # 'file' | 'metadata'
    file_id: Optional[str] = None
    metadata_id: Optional[str] = None
    content_type: str  # 'structured' | 'unstructured' | 'hybrid'
    analysis_options: Optional[Dict[str, Any]] = None

class AnalyzeContentResponse(BaseModel):
    """Semantic response model for content analysis."""
    success: bool
    analysis_id: str
    summary: Dict[str, Any]  # textual, tabular, visualizations
    insights: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class QueryAnalysisRequest(BaseModel):
    """Request model for NLP queries."""
    query: str  # Natural language query
    analysis_id: str
    query_type: Optional[str] = None  # 'table' | 'chart' | 'summary'

class QueryAnalysisResponse(BaseModel):
    """Response model for query results."""
    success: bool
    result: Dict[str, Any]  # type, data, explanation
    follow_up_suggestions: Optional[List[str]] = None

# Endpoints
@router.post("/analyze-content-for-insights", response_model=AnalyzeContentResponse)
async def analyze_content_for_insights(
    request: AnalyzeContentRequest,
    session_token: Optional[str] = Header(None, alias="X-Session-Token")
):
    """
    Analyze content (structured or unstructured) and generate insights.
    
    This semantic endpoint analyzes data files or metadata to extract
    business insights, generate visualizations, and provide recommendations.
    
    Supports:
    - Structured data (CSV, Excel) → VARK-style analysis with tables/charts
    - Unstructured data (text, AAR) → APG-style analysis with narrative
    - Hybrid data → Combined analysis
    - Metadata analysis → Use extracted metadata from Content Pillar
    """
    try:
        logger.info(f"📊 Semantic analyze-content-for-insights request: {request.content_type}")
        
        # Get insights orchestrator
        insights_orchestrator = await get_insights_orchestrator()
        
        # Route based on content type
        if request.content_type == 'structured':
            result = await insights_orchestrator.analyze_structured_content(
                source_type=request.source_type,
                file_id=request.file_id,
                metadata_id=request.metadata_id,
                analysis_options=request.analysis_options or {}
            )
        elif request.content_type == 'unstructured':
            aar_specific = request.analysis_options.get('aar_specific_analysis', False) if request.analysis_options else False
            result = await insights_orchestrator.analyze_unstructured_content(
                source_type=request.source_type,
                file_id=request.file_id,
                aar_specific=aar_specific
            )
        elif request.content_type == 'hybrid':
            result = await insights_orchestrator.analyze_hybrid_content(
                source_type=request.source_type,
                file_id=request.file_id,
                metadata_id=request.metadata_id,
                analysis_options=request.analysis_options or {}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content_type: {request.content_type}"
            )
        
        return AnalyzeContentResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/query-analysis-results", response_model=QueryAnalysisResponse)
async def query_analysis_results(
    request: QueryAnalysisRequest,
    session_token: Optional[str] = Header(None, alias="X-Session-Token")
):
    """
    Query analysis results using natural language.
    
    This semantic endpoint enables conversational analytics by allowing
    users to ask questions about their analysis results in natural language.
    
    Example queries:
    - "Show me accounts over 90 days late"
    - "What's the correlation between satisfaction and revenue?"
    - "Create a chart of sales trends"
    """
    try:
        logger.info(f"🔍 Semantic query-analysis-results: '{request.query}'")
        
        insights_orchestrator = await get_insights_orchestrator()
        
        result = await insights_orchestrator.query_analysis(
            query=request.query,
            analysis_id=request.analysis_id,
            query_type=request.query_type
        )
        
        return QueryAnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Query failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )

@router.get("/get-analysis-results/{analysis_id}")
async def get_analysis_results(
    analysis_id: str,
    session_token: Optional[str] = Header(None, alias="X-Session-Token")
):
    """Get complete analysis results by ID."""
    try:
        insights_orchestrator = await get_insights_orchestrator()
        result = await insights_orchestrator.get_analysis_results(analysis_id)
        return {"success": True, **result}
    except Exception as e:
        logger.error(f"❌ Failed to get analysis results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis results: {str(e)}"
        )

@router.get("/get-visualizations/{analysis_id}")
async def get_visualizations(
    analysis_id: str,
    session_token: Optional[str] = Header(None, alias="X-Session-Token")
):
    """Get visualizations for an analysis."""
    try:
        insights_orchestrator = await get_insights_orchestrator()
        result = await insights_orchestrator.get_visualizations(analysis_id)
        return {"success": True, **result}
    except Exception as e:
        logger.error(f"❌ Failed to get visualizations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get visualizations: {str(e)}"
        )

@router.get("/list-available-analyses")
async def list_available_analyses(
    session_token: Optional[str] = Header(None, alias="X-Session-Token")
):
    """List all available analyses for the current session."""
    try:
        insights_orchestrator = await get_insights_orchestrator()
        result = await insights_orchestrator.list_available_analyses()
        return {"success": True, **result}
    except Exception as e:
        logger.error(f"❌ Failed to list analyses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list analyses: {str(e)}"
        )

@router.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "insights-pillar",
        "timestamp": datetime.utcnow().isoformat()
    }

# Helper functions
async def get_insights_orchestrator():
    """Get InsightsOrchestrator from platform orchestrator."""
    from mvp_insights_router import get_business_orchestrator
    business_orchestrator = await get_business_orchestrator()
    if not business_orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Insights orchestrator not available"
        )
    return business_orchestrator.insights_orchestrator
```

**Register Router:**
```python
# backend/experience/api/main_api.py
from api.semantic.insights_pillar_router import router as insights_semantic_router

app.include_router(insights_semantic_router)
```

**Acceptance Criteria:**
- ✅ All semantic endpoints implemented
- ✅ Request/response models match CLEAN_SEMANTIC_MIGRATION_PLAN
- ✅ Endpoints route to InsightsOrchestrator
- ✅ Old endpoints still work (parallel operation)
- ✅ API documentation generated

---

#### **Phase 2B: Remove Legacy Insights API (1 day)**

**Goal:** Clean up old non-semantic endpoints

**Files to Delete:**
```
backend/experience/api/mvp_insights_router.py  # DELETE after migration
```

**Files to Modify:**
```
backend/experience/api/main_api.py  # Remove old router registration
```

**Migration Checklist:**
1. ✅ Frontend fully migrated to semantic APIs
2. ✅ All tests use semantic APIs
3. ✅ No references to old endpoints
4. ✅ Documentation updated

---

### **DIMENSION 3: Frontend UX Streamlining**

#### **Phase 3A: Create Unified Insights Page (2 days)**

**Goal:** Replace duplicate pages with single two-section layout

**Files to Create:**
```
app/pillars/insights/page.tsx  # NEW unified page
components/insights/
  ├─ StructuredDataInsightsSection.tsx
  ├─ UnstructuredDataInsightsSection.tsx
  ├─ InsightsSummaryDisplay.tsx  # Reusable Text|Table|Charts display
  └─ InsightsFileSelector.tsx    # File/metadata selector
```

**Unified Insights Page Structure:**
```tsx
// app/pillars/insights/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { Header } from '@/components/layout/Header';
import { StructuredDataInsightsSection } from '@/components/insights/StructuredDataInsightsSection';
import { UnstructuredDataInsightsSection } from '@/components/insights/UnstructuredDataInsightsSection';
import { useLiaisonAgent } from '@/shared/hooks/useLiaisonAgent';

export default function InsightsPillarPage() {
  const [structuredAnalysis, setStructuredAnalysis] = useState(null);
  const [unstructuredAnalysis, setUnstructuredAnalysis] = useState(null);
  
  // Configure Insights Liaison Agent for side panel
  const { configureLiaisonAgent } = useLiaisonAgent();
  
  useEffect(() => {
    configureLiaisonAgent({
      type: 'insights',
      capabilities: [
        'Query analysis results',
        'Generate tables on-demand',
        'Create visualizations',
        'Explain insights',
        'Suggest follow-up analyses'
      ],
      exampleQueries: [
        "Show me accounts over 90 days late",
        "What's the correlation between satisfaction and revenue?",
        "Create a chart of sales trends over the last quarter"
      ]
    });
  }, []);
  
  return (
    <div className="flex-grow space-y-6 p-6">
      <Header 
        title="Insights Pillar"
        description="Extract insights from your data - structured or unstructured"
      />
      
      {/* Section 1: Structured Data Insights */}
      <StructuredDataInsightsSection
        onAnalysisComplete={setStructuredAnalysis}
        analysis={structuredAnalysis}
      />
      
      {/* Section 2: Unstructured Data Insights */}
      <UnstructuredDataInsightsSection
        onAnalysisComplete={setUnstructuredAnalysis}
        analysis={unstructuredAnalysis}
      />
    </div>
  );
}
```

**StructuredDataInsightsSection Component:**
```tsx
// components/insights/StructuredDataInsightsSection.tsx
import { useState } from 'react';
import { InsightsFileSelector } from './InsightsFileSelector';
import { InsightsSummaryDisplay } from './InsightsSummaryDisplay';
import { analyzeContentForInsights } from '@/lib/api/insightsPillarApi';

export function StructuredDataInsightsSection({ onAnalysisComplete, analysis }) {
  const [loading, setLoading] = useState(false);
  const [selectedSource, setSelectedSource] = useState(null);
  
  const handleAnalyze = async () => {
    if (!selectedSource) return;
    
    setLoading(true);
    try {
      const result = await analyzeContentForInsights({
        source_type: selectedSource.type, // 'file' or 'metadata'
        file_id: selectedSource.file_id,
        metadata_id: selectedSource.metadata_id,
        content_type: 'structured',
        analysis_options: {
          include_visualizations: true,
          include_tabular_summary: true
        }
      });
      
      onAnalysisComplete(result);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="card space-y-4">
      <div className="card-header">
        <h2 className="text-xl font-semibold">Insights from Structured Data</h2>
        <p className="text-sm text-gray-600">
          Analyze CSV, Excel, or structured data with tables, charts, and metrics
        </p>
      </div>
      
      <div className="card-body space-y-4">
        {/* File/Metadata Selector */}
        <InsightsFileSelector
          contentType="structured"
          onSelect={setSelectedSource}
          selectedSource={selectedSource}
        />
        
        {/* Analyze Button */}
        <button
          onClick={handleAnalyze}
          disabled={!selectedSource || loading}
          className="btn-primary"
        >
          {loading ? 'Analyzing...' : 'Analyze for Insights'}
        </button>
        
        {/* Summary Display (appears after analysis) */}
        {analysis && (
          <InsightsSummaryDisplay
            analysis={analysis}
            contentType="structured"
          />
        )}
      </div>
    </div>
  );
}
```

**InsightsSummaryDisplay Component (Reusable):**
```tsx
// components/insights/InsightsSummaryDisplay.tsx
import { useState } from 'react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';

export function InsightsSummaryDisplay({ analysis, contentType }) {
  const [activeTab, setActiveTab] = useState('text');
  
  return (
    <div className="border rounded-lg p-4">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="text">📝 Textual Summary</TabsTrigger>
          {analysis.summary.tabular && (
            <TabsTrigger value="table">📊 Tabular Summary</TabsTrigger>
          )}
          {analysis.summary.visualizations && (
            <TabsTrigger value="charts">📈 Visual Summary</TabsTrigger>
          )}
        </TabsList>
        
        {/* Text Tab (always available) */}
        <TabsContent value="text" className="prose max-w-none">
          <div className="bg-blue-50 p-4 rounded">
            <h3 className="text-lg font-semibold mb-2">Business Analysis</h3>
            <p>{analysis.summary.textual}</p>
          </div>
          
          {/* Key Insights */}
          {analysis.insights && analysis.insights.length > 0 && (
            <div className="mt-4">
              <h4 className="font-semibold mb-2">Key Insights:</h4>
              <ul className="space-y-2">
                {analysis.insights.map((insight, idx) => (
                  <li key={idx} className="bg-yellow-50 p-3 rounded">
                    <span className="font-medium">{insight.type}:</span> {insight.description}
                    {insight.recommendations && (
                      <div className="mt-2 text-sm text-gray-700">
                        💡 {insight.recommendations.join(', ')}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </TabsContent>
        
        {/* Table Tab (if available) */}
        {analysis.summary.tabular && (
          <TabsContent value="table">
            <DataTable
              columns={analysis.summary.tabular.columns}
              rows={analysis.summary.tabular.rows}
              summaryStats={analysis.summary.tabular.summary_stats}
            />
          </TabsContent>
        )}
        
        {/* Charts Tab (if available) */}
        {analysis.summary.visualizations && (
          <TabsContent value="charts">
            <ChartGallery
              visualizations={analysis.summary.visualizations}
            />
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
}
```

**Acceptance Criteria:**
- ✅ Single unified insights page created
- ✅ Two clear sections (structured/unstructured)
- ✅ Reusable InsightsSummaryDisplay component
- ✅ File/metadata selector working
- ✅ Insights Liaison Agent in side panel (not inline)
- ✅ Clean, intuitive UI

---

#### **Phase 3B: Remove Duplicate Pages & Components (1 day)**

**Goal:** Delete old VARK/APG pages and components

**Files to Delete:**
```
app/pillars/insight/page.tsx               # DELETE (duplicate page)
components/insights/VARKFlow.tsx          # DELETE
components/insights/APGFlow.tsx           # DELETE
components/insights/VARKAPGToggle.tsx     # DELETE
components/insights/InlineInsightsAgent.tsx  # DELETE (now in side panel)
```

**Cleanup Checklist:**
1. ✅ Remove old page routes
2. ✅ Remove old component imports
3. ✅ Update navigation links
4. ✅ Remove VARK/APG toggle logic
5. ✅ Test unified page thoroughly

---

#### **Phase 3C: Enhance Insights Liaison Agent with NLP Queries (2 days)**

**Goal:** Enable conversational analytics through side panel agent

**Files to Modify:**
```
symphainy-frontend/lib/api/insightsPillarApi.ts  # Add query endpoint
components/chat/LiaisonAgentPanel.tsx            # Add query interface
```

**Enhanced API Client:**
```typescript
// lib/api/insightsPillarApi.ts
export async function queryAnalysisResults(request: {
  query: string;
  analysis_id: string;
  query_type?: 'table' | 'chart' | 'summary';
}): Promise<QueryAnalysisResponse> {
  const response = await api.post(
    '/api/insights-pillar/query-analysis-results',
    request
  );
  return response.data;
}
```

**Query Interface in Side Panel:**
```tsx
// In LiaisonAgentPanel.tsx (when agent type is 'insights')
const handleQuerySubmit = async (query: string) => {
  if (!currentAnalysisId) {
    return "Please run an analysis first before querying results.";
  }
  
  const result = await queryAnalysisResults({
    query,
    analysis_id: currentAnalysisId
  });
  
  // Display result based on type
  if (result.result.type === 'table') {
    return <DataTable data={result.result.data} />;
  } else if (result.result.type === 'chart') {
    return <ChartDisplay spec={result.result.data} />;
  } else {
    return result.result.explanation;
  }
};
```

**Acceptance Criteria:**
- ✅ NLP query endpoint integrated
- ✅ Query interface in side panel
- ✅ Dynamic table/chart generation
- ✅ Follow-up query suggestions
- ✅ Query history maintained

---

## 📋 Integrated Timeline & Dependencies

### **Week 1: Architecture + Semantic APIs**
```
Day 1-2: Phase 1A - Create MVP Insights Orchestrator
  ↓ Depends on: Nothing (can start immediately)
  ↓ Blocks: Phase 2A

Day 3: Phase 1B - Refactor InsightsPillar to Pure Enabler
  ↓ Depends on: Phase 1A complete
  ↓ Blocks: Phase 2A

Day 4-5: Phase 2A - Build Semantic Insights API
  ↓ Depends on: Phase 1A, 1B complete
  ↓ Blocks: Phase 3A

✅ Milestone: Backend refactoring complete, semantic APIs ready
```

### **Week 2: Frontend UX + Cleanup**
```
Day 6-7: Phase 3A - Create Unified Insights Page
  ↓ Depends on: Phase 2A complete
  ↓ Blocks: Phase 3B

Day 8: Phase 3B - Remove Duplicate Pages
  ↓ Depends on: Phase 3A complete, tested, and validated
  ↓ Blocks: None

Day 8-9: Phase 3C - Enhance Liaison Agent with NLP Queries
  ↓ Depends on: Phase 2A (query endpoint), Phase 3A (side panel)
  ↓ Blocks: None

Day 10: Phase 2B - Remove Legacy Insights API
  ↓ Depends on: ALL frontend migration complete
  ↓ Blocks: None

✅ Milestone: Full refactoring complete, legacy code removed
```

**Total: 8-10 days**

---

## 🎯 Success Metrics

### **Architecture**
- ✅ InsightsPillar is pure enabling service (no MVP logic)
- ✅ InsightsOrchestrator handles all MVP workflows
- ✅ Clear separation of concerns (Role=What, Service=How)
- ✅ Orchestrator successfully composes enabling services

### **Semantic APIs**
- ✅ All endpoints follow semantic naming convention
- ✅ API aligns with user journey (analyze → query → visualize)
- ✅ Request/response models are clear and documented
- ✅ Consistent with Content Pillar API pattern

### **Frontend UX**
- ✅ Single unified insights page (no duplicates)
- ✅ Clear two-section layout (structured/unstructured)
- ✅ Reusable InsightsSummaryDisplay component
- ✅ Insights Liaison Agent in side panel
- ✅ NLP query interface working
- ✅ User journey is intuitive and streamlined

### **Quality**
- ✅ All tests pass
- ✅ E2E CTO demo journey works
- ✅ No breaking changes to functionality
- ✅ Performance equivalent or better
- ✅ Documentation updated

---

## 🔄 Rollback Strategy

### **Phase 1 (Architecture):**
- Keep old InsightsPillarService running in parallel
- Orchestrator is additive, doesn't break existing code
- Can revert by not using orchestrator

### **Phase 2 (Semantic APIs):**
- Old API endpoints remain during development
- Frontend can continue using old endpoints
- Can revert by not registering new router

### **Phase 3 (Frontend UX):**
- Keep old pages during development
- Use feature flag or route prefix
- Can revert by restoring old pages

**Git Strategy:**
```bash
# Separate commits for each phase
git commit -m "Phase 1A: Create MVP Insights Orchestrator"
git commit -m "Phase 1B: Refactor InsightsPillar to pure enabler"
git commit -m "Phase 2A: Build semantic insights API"
git commit -m "Phase 3A: Create unified insights page"
git commit -m "Phase 3B: Remove duplicate pages"
git commit -m "Phase 3C: Enhance liaison agent with NLP"
git commit -m "Phase 2B: Remove legacy insights API"

# Easy rollback to any phase
git revert <commit-hash>
```

---

## 🚀 Getting Started

### **Pre-Flight Checklist:**
1. ✅ Review this plan with team
2. ✅ Content Pillar refactoring complete (reference pattern)
3. ✅ Test environment ready
4. ✅ Feature branch created (`insights-pillar-refactoring`)
5. ✅ Backup current state (git commit/push)

### **Recommended Start:**
**Begin with Phase 1A: Create MVP Insights Orchestrator**

This provides:
- Immediate architectural improvement
- Clear separation of concerns
- Foundation for semantic APIs
- No risk to existing functionality

---

## 📚 Reference Documentation

**Patterns to Follow:**
- Content Pillar refactoring (architecture pattern)
- `CLEAN_SEMANTIC_MIGRATION_PLAN.md` (API pattern)
- `INSIGHTS_PILLAR_REFACTORING_PLAN.md` (UX pattern)

**Key Files to Review:**
- `content_analysis_orchestrator.py` (orchestrator pattern)
- `semantic/content_pillar_router.py` (semantic API pattern)
- `app/pillars/content/page.tsx` (frontend UX pattern)

---

## ✅ Final Recommendation

**Status:** ✅ Phase 0 COMPLETE - Ready for Implementation  
**Start Date:** Ready to begin Phase 1 & 2 immediately  
**Execution:** Sequential phases with testing at each step  
**Risk Level:** Low (incremental, tested, reversible)  
**Expected Outcome:** Clean, maintainable, semantic Insights Pillar

### **Phase 0 Achievements (Nov 11, 2025)**

✅ **Target UX Defined** (`INSIGHTS_PILLAR_REFACTORING_PLAN.md`)
- Unified two-section layout (Structured + Unstructured)
- 3-way summary display (Text | Table | Charts)
- Navy AAR as expandable section
- Agent in side panel with NLP queries
- "Use Extracted Metadata" integration

✅ **API Contract Defined** (`API_CONTRACT_INSIGHTS_PILLAR.md`)
- 9 semantic endpoints with complete specifications
- ArangoDB integration for content metadata
- 3-way summary response structure
- NLP query support
- Descriptive naming conventions

✅ **Architecture Clarified** (`AGENTIC_FOUNDATION_CLEANUP_COMPLETE.md`)
- Enabling services correctly placed
- Agentic Foundation purified (SDK only)
- 3,680 lines cleaned up
- Import paths updated

### **Ready to Execute:**

🎯 **This plan integrates all three dimensions into a coordinated refactoring that follows proven patterns from your Content Pillar transformation.**

**Frontend-First Approach:**
- We know WHAT we're building (target UX defined)
- We know HOW to serve it (API contract defined)
- We know WHERE everything goes (architecture clarified)

**No More Guesswork - Just Execution!**

Would you like me to proceed with **Phase 1A: Create MVP Insights Orchestrator** and **Phase 2A: Build Semantic API**?

