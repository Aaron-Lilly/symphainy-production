# Realm Architecture Migration Plan
## Migrating Operations and Business Outcomes to Solution → Journey → Realm Pattern

**Date:** January 2025  
**Status:** 📋 **PLANNING**  
**Goal:** Migrate Operations and Business Outcomes pillars to the new Solution → Journey → Realm architectural pattern (following Insights Pillar migration)

---

## 🎯 Executive Summary

This plan outlines the migration of **Operations Pillar** and **Business Outcomes Pillar** to the new architectural pattern established by the Insights Pillar migration. The pattern ensures:

- **Solution Realm:** Business outcomes orchestration (entry point)
- **Journey Realm:** Operations orchestration (workflow management)
- **Realm Services:** Core capabilities (enabling services)

**Key Principle:** Follow the Insights Pillar migration pattern exactly, ensuring consistency across all pillars.

---

## 📊 Current State Analysis

### Operations Pillar

**Current Location:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/operations_orchestrator/`

**Current Structure:**
- `OperationsOrchestrator` extends `OrchestratorBase`
- Uses enabling services: `WorkflowConversionService`, `CoexistenceAnalysisService`, `SOPBuilderService`
- Has Journey Orchestrator integration for artifact creation

**Current API Surface:**
- `/api/v1/operations-pillar/*` (routed via FrontendGatewayService)

### Business Outcomes Pillar

**Current Location:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/business_outcomes_orchestrator/`

**Current Structure:**
- `BusinessOutcomesOrchestrator` extends `OrchestratorBase`
- Uses enabling services: `MetricsCalculatorService`, `ReportGeneratorService`, `RoadmapGenerationService`
- Has MCP Server for agentic tools

**Current API Surface:**
- `/api/v1/business-outcomes-pillar/*` (routed via FrontendGatewayService)

---

## 🏗️ Target Architecture

### Solution → Journey → Realm Pattern

Following the Insights Pillar pattern:

```
Frontend
  ↓
FrontendGatewayService (Experience Foundation)
  ↓ routes to
OperationsSolutionOrchestratorService (Solution Realm)
  ↓ orchestrates platform correlation
  ↓ delegates to
OperationsJourneyOrchestrator (Journey Realm)
  ↓ composes realm services:
  ├─ WorkflowConversionService (Journey Realm)
  ├─ CoexistenceAnalysisService (Journey Realm)
  └─ SOPBuilderService (Journey Realm)
```

```
Frontend
  ↓
FrontendGatewayService (Experience Foundation)
  ↓ routes to
BusinessOutcomesSolutionOrchestratorService (Solution Realm)
  ↓ orchestrates platform correlation
  ↓ delegates to
BusinessOutcomesJourneyOrchestrator (Journey Realm)
  ↓ composes realm services:
  ├─ MetricsCalculatorService (Business Enablement Realm)
  ├─ ReportGeneratorService (Business Enablement Realm)
  └─ RoadmapGenerationService (Business Enablement Realm)
```

---

## 📋 Migration Plan

### Phase 1: Operations Pillar Migration

#### Step 1.1: Create OperationsSolutionOrchestratorService

**Location:** `backend/solution/services/operations_solution_orchestrator_service/`

**Responsibilities:**
- Orchestrate platform correlation (workflow_id, lineage, telemetry)
- Route requests to OperationsJourneyOrchestrator
- Handle HTTP requests via `handle_request()`

**Methods:**
- `orchestrate_operations_workflow()` - Main orchestration method
- `handle_request()` - HTTP routing
- `_orchestrate_platform_correlation()` - Platform correlation
- `_record_platform_correlation_completion()` - Record completion

#### Step 1.2: Create OperationsJourneyOrchestrator

**Location:** `backend/journey/orchestrators/operations_journey_orchestrator/`

**Responsibilities:**
- Execute operations workflows
- Compose realm services (WorkflowConversionService, etc.)
- Track data lineage

**Methods:**
- `execute_workflow_conversion_workflow()` - Workflow conversion
- `execute_coexistence_analysis_workflow()` - Coexistence analysis
- `execute_sop_builder_workflow()` - SOP building
- Lazy initialization methods for realm services

#### Step 1.3: Migrate Workflows

**Location:** `backend/journey/orchestrators/operations_journey_orchestrator/workflows/`

**Workflows to Migrate:**
- `WorkflowConversionWorkflow`
- `CoexistenceAnalysisWorkflow`
- `SOPBuilderWorkflow`

#### Step 1.4: Update FrontendGatewayService

**Changes:**
- Add `operations-solution` pillar mapping
- Route `/api/v1/operations-solution/*` to `OperationsSolutionOrchestratorService`
- Remove backward compatibility with `operations-pillar` (after migration complete)

#### Step 1.5: Update Frontend Service

**File:** `symphainy-frontend/shared/services/operations/core.ts`

**Changes:**
- Update `API_BASE` to `/api/v1/operations-solution`
- Update method signatures to match new API structure

### Phase 2: Business Outcomes Pillar Migration

#### Step 2.1: Create BusinessOutcomesSolutionOrchestratorService

**Location:** `backend/solution/services/business_outcomes_solution_orchestrator_service/`

**Responsibilities:**
- Orchestrate platform correlation
- Route requests to BusinessOutcomesJourneyOrchestrator
- Handle HTTP requests via `handle_request()`

**Methods:**
- `orchestrate_business_outcomes_analysis()` - Main orchestration
- `orchestrate_roadmap_generation()` - Roadmap generation
- `orchestrate_poc_proposal()` - POC proposal generation
- `handle_request()` - HTTP routing

#### Step 2.2: Create BusinessOutcomesJourneyOrchestrator

**Location:** `backend/journey/orchestrators/business_outcomes_journey_orchestrator/`

**Responsibilities:**
- Execute business outcomes workflows
- Compose realm services (MetricsCalculatorService, etc.)
- Track data lineage

**Methods:**
- `execute_metrics_calculation_workflow()` - Metrics calculation
- `execute_report_generation_workflow()` - Report generation
- `execute_roadmap_generation_workflow()` - Roadmap generation
- Lazy initialization methods for realm services

#### Step 2.3: Migrate Workflows

**Location:** `backend/journey/orchestrators/business_outcomes_journey_orchestrator/workflows/`

**Workflows to Migrate:**
- `MetricsCalculationWorkflow`
- `ReportGenerationWorkflow`
- `RoadmapGenerationWorkflow`
- `POCProposalWorkflow`

#### Step 2.4: Update FrontendGatewayService

**Changes:**
- Add `business-outcomes-solution` pillar mapping
- Route `/api/v1/business-outcomes-solution/*` to `BusinessOutcomesSolutionOrchestratorService`
- Remove backward compatibility with `business-outcomes-pillar` (after migration complete)

#### Step 2.5: Update Frontend Service

**File:** `symphainy-frontend/shared/services/business-outcomes/core.ts`

**Changes:**
- Update `API_BASE` to `/api/v1/business-outcomes-solution`
- Update method signatures to match new API structure

### Phase 3: Testing and Validation

#### Step 3.1: Unit Tests

**Files:**
- `tests/unit/solution/test_operations_solution_orchestrator.py`
- `tests/unit/solution/test_business_outcomes_solution_orchestrator.py`
- `tests/unit/journey/test_operations_journey_orchestrator.py`
- `tests/unit/journey/test_business_outcomes_journey_orchestrator.py`

#### Step 3.2: Integration Tests

**Files:**
- `tests/integration/operations/test_operations_architectural_flow.py`
- `tests/integration/business_outcomes/test_business_outcomes_architectural_flow.py`

#### Step 3.3: E2E Tests

**Files:**
- `tests/e2e/operations/test_operations_architectural_e2e.py`
- `tests/e2e/business_outcomes/test_business_outcomes_architectural_e2e.py`

### Phase 4: Backward Compatibility Removal

**After all tests pass:**
- Remove `operations-pillar` routes from FrontendGatewayService
- Remove `business-outcomes-pillar` routes from FrontendGatewayService
- Remove legacy orchestrator initialization
- Update documentation

---

## 🔄 Migration Checklist

### Operations Pillar
- [ ] Create `OperationsSolutionOrchestratorService`
- [ ] Create `OperationsJourneyOrchestrator`
- [ ] Migrate workflows to Journey Orchestrator
- [ ] Update FrontendGatewayService routing
- [ ] Update frontend service layer
- [ ] Create unit tests
- [ ] Create integration tests
- [ ] Create E2E tests
- [ ] Remove backward compatibility

### Business Outcomes Pillar
- [ ] Create `BusinessOutcomesSolutionOrchestratorService`
- [ ] Create `BusinessOutcomesJourneyOrchestrator`
- [ ] Migrate workflows to Journey Orchestrator
- [ ] Update FrontendGatewayService routing
- [ ] Update frontend service layer
- [ ] Create unit tests
- [ ] Create integration tests
- [ ] Create E2E tests
- [ ] Remove backward compatibility

---

## 📚 Reference: Insights Pillar Migration

The Insights Pillar migration serves as the reference implementation:

**Files:**
- `backend/solution/services/insights_solution_orchestrator_service/insights_solution_orchestrator_service.py`
- `backend/journey/orchestrators/insights_journey_orchestrator/insights_journey_orchestrator.py`
- `backend/journey/orchestrators/insights_journey_orchestrator/workflows/`

**Documentation:**
- [DATA_SOLUTION_ORCHESTRATOR_REALM_INTEGRATION_PLAN.md](./DATA_SOLUTION_ORCHESTRATOR_REALM_INTEGRATION_PLAN.md)
- [PHASE_4_DATA_MASH_IMPLEMENTATION_SUMMARY.md](./PHASE_4_DATA_MASH_IMPLEMENTATION_SUMMARY.md)

---

## ⚠️ Important Considerations

### 1. Platform Correlation
- All operations must include platform correlation (workflow_id, lineage, telemetry)
- Use `_orchestrate_platform_correlation()` and `_record_platform_correlation_completion()`

### 2. Service Discovery
- Use four-tier access pattern for service discovery
- Lazy initialization for realm services
- Fallback to direct initialization if Curator discovery fails

### 3. Error Handling
- Use `handle_error_with_audit()` for all errors
- Include `workflow_id` in error responses
- Maintain error audit trail

### 4. Data Lineage
- Track data lineage for all operations
- Use `track_data_lineage()` from Smart City services
- Include lineage in platform correlation

---

**Last Updated:** January 2025











