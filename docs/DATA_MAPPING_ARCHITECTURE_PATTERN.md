# Data Mapping Architecture Pattern - Solution → Journey → Realm Services

**Date:** January 2025  
**Status:** ✅ **Architecture Pattern Document**  
**Purpose:** Document the correct architectural pattern for Insights data mapping following Content Pillar pattern

---

## 🎯 Architectural Pattern

Following the **Content Pillar pattern**, the Insights data mapping system follows this structure:

```
Solution Realm → Journey Realm → Insights Realm Services
```

---

## 📊 Layer Breakdown

### 1. Solution Realm (Entry Point)

**Component:** `InsightsSolutionOrchestratorService`

**Location:** `backend/solution/services/insights_solution_orchestrator_service/`

**Responsibilities:**
- Entry point for insights operations
- Platform correlation (workflow_id, lineage, telemetry)
- Orchestrates platform services (Security Guard, Traffic Cop, Conductor, Post Office, Nurse)
- Routes to Insights Journey Orchestrator

**Pattern:** Similar to `DataSolutionOrchestratorService` but for insights operations

**Example:**
```python
class InsightsSolutionOrchestratorService(OrchestratorBase):
    """
    Insights Solution Orchestrator - Entry point for insights operations.
    
    Pattern: Similar to DataSolutionOrchestratorService
    """
    
    async def orchestrate_insights_mapping(
        self,
        source_file_id: str,
        target_file_id: str,
        mapping_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate data mapping with full platform correlation.
        
        Flow:
        1. Orchestrate platform correlation
        2. Route to Insights Journey Orchestrator
        3. Record completion in platform correlation
        """
        # Platform correlation
        correlation_context = await self._orchestrate_platform_correlation(
            operation="insights_mapping",
            user_context=user_context
        )
        
        # Route to Journey Orchestrator
        insights_journey = await self._discover_insights_journey_orchestrator()
        result = await insights_journey.execute_data_mapping_workflow(
            source_file_id=source_file_id,
            target_file_id=target_file_id,
            mapping_options=mapping_options,
            user_context=correlation_context
        )
        
        # Record completion
        await self._record_platform_correlation_completion(
            operation="insights_mapping",
            result=result,
            correlation_context=correlation_context
        )
        
        return result
```

---

### 2. Journey Realm (Workflows)

**Component:** `InsightsJourneyOrchestratorService`

**Location:** `backend/journey/orchestrators/insights_journey_orchestrator/`

**Responsibilities:**
- Orchestrates insights workflows (data mapping, analysis, etc.)
- Composes Insights Realm Services
- Manages workflow state and transitions
- Routes to appropriate services based on operation type

**Key Workflow:** Data Mapping Workflow

**Location:** `backend/journey/orchestrators/insights_journey_orchestrator/workflows/data_mapping_workflow.py`

**Responsibilities:**
- Orchestrate end-to-end mapping process
- Handle both use cases (unstructured→structured, structured→structured)
- Coordinate agents and services
- Track lineage and citations
- Generate quality reports

**Example:**
```python
class DataMappingWorkflow:
    """
    Data Mapping Workflow - Orchestrates data mapping process.
    
    Located in Journey Realm, composes Insights Realm Services.
    """
    
    async def execute(
        self,
        source_file_id: str,
        target_file_id: str,
        mapping_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute data mapping workflow.
        
        Composes:
        - Insights Realm Services (Field Extraction, Data Quality, Data Transformation)
        - Insights Realm Agents (Schema Extraction, Semantic Matching, Data Quality)
        """
        # Get Insights Realm Services
        field_extraction_service = await self._get_insights_realm_service("FieldExtractionService")
        data_quality_service = await self._get_insights_realm_service("DataQualityValidationService")
        data_transformation_service = await self._get_insights_realm_service("DataTransformationService")
        
        # Get Insights Realm Agents
        data_mapping_agent = await self._get_insights_realm_agent("DataMappingAgent")
        data_quality_agent = await self._get_insights_realm_agent("DataQualityAgent")
        
        # Execute workflow...
        pass
```

---

### 3. Insights Realm (Services & Agents)

**Services Location:** `backend/insights/services/`

**Agents Location:** `backend/insights/agents/`

**Services:**
1. **Field Extraction Service** (`field_extraction_service/`)
   - Extract fields from unstructured sources
   - LLM + regex patterns

2. **Data Quality Validation Service** (`data_quality_validation_service/`)
   - Record-level validation
   - Quality issue identification
   - Cleanup action generation

3. **Data Transformation Service** (`data_transformation_service/`)
   - Apply mapping rules
   - Transform data formats
   - Generate output files

**Agents:**
1. **Data Mapping Agent** (`data_mapping_agent.py`)
   - Schema extraction
   - Semantic matching
   - Mapping rule generation

2. **Data Quality Agent** (`data_quality_agent.py`)
   - Quality issue analysis
   - Cleanup action generation
   - Transformation suggestions

---

## 🔄 Complete Flow

```
Frontend Request
  ↓
FrontendGatewayService (Experience Realm)
  ↓
Insights Solution Orchestrator (Solution Realm)
  ├─ Platform correlation (auth, session, workflow, events, telemetry)
  └─ Routes to
      ↓
Insights Journey Orchestrator (Journey Realm)
  ├─ Data Mapping Workflow
  └─ Composes
      ↓
Insights Realm Services & Agents
  ├─ Field Extraction Service
  ├─ Data Quality Validation Service
  ├─ Data Transformation Service
  ├─ Data Mapping Agent
  └─ Data Quality Agent
```

---

## 📋 Key Differences from Original Design

### Original Design (Incorrect)
- Data Mapping Orchestrator in Insights Pillar
- Services in Business Enablement realm
- No Solution/Journey layer separation

### Corrected Design (Following Content Pattern)
- ✅ Insights Solution Orchestrator in Solution Realm
- ✅ Insights Journey Orchestrator in Journey Realm
- ✅ Data Mapping Workflow in Journey Realm
- ✅ Services in Insights Realm
- ✅ Agents in Insights Realm

---

## ✅ Benefits of This Pattern

1. **Consistency** - Matches Content Pillar pattern
2. **Platform Correlation** - Solution layer handles platform correlation
3. **Workflow Management** - Journey layer manages workflows
4. **Service Isolation** - Realm services are isolated and reusable
5. **Clear Separation** - Each layer has clear responsibilities

---

## 🚀 Implementation Order

1. **Phase 1:** Insights Solution Orchestrator (Solution Realm)
2. **Phase 2:** Insights Journey Orchestrator + Data Mapping Workflow (Journey Realm)
3. **Phase 3:** Insights Realm Services (Field Extraction, Data Quality, Data Transformation)
4. **Phase 4:** Insights Realm Agents (Data Mapping Agent, Data Quality Agent)
5. **Phase 5:** Integration and Testing

---

**Status:** ✅ Architecture Pattern Documented  
**Next:** Update implementation plan to follow this pattern












