# Pillar Refactoring Plan - Workflow/SOP/Financial Adapters

**Date**: November 14, 2025  
**Status**: Planning

---

## Overview

Refactor Insights, Operations, and Business Outcomes pillars to use infrastructure abstractions instead of direct library access.

---

## Current State

### Abstractions Already Exist ✅
1. **`BPMNProcessingAbstraction`** - Uses `BPMNProcessingAdapter`
2. **`SOPProcessingAbstraction`** - Uses `SOPParsingAdapter`
3. **`SOPEnhancementAbstraction`** - Uses `SOPEnhancementAdapter`
4. **`StrategicPlanningAbstraction`** - Uses `StandardStrategicPlanningAdapter` + `HuggingFaceStrategicPlanningAdapter`
5. **`FinancialAnalysisAbstraction`** - Uses `StandardFinancialAdapter` + `HuggingFaceFinancialAdapter`

### Issues
- ❌ Abstractions are NOT created in `PublicWorksFoundationService`
- ❌ Abstractions are NOT exposed via Platform Gateway
- ❌ Services use direct library access or business logic instead of abstractions

---

## Target State

### Operations Pillar
- **`WorkflowManagerService`** → Use `WorkflowOrchestrationAbstraction` (already exists) + `BPMNProcessingAbstraction`
- **`WorkflowConversionService`** → Use `BPMNProcessingAbstraction` + `SOPProcessingAbstraction`

### Insights Pillar
- **`SOPBuilderService`** → Use `SOPProcessingAbstraction` + `SOPEnhancementAbstraction`
- **`CoexistenceAnalysisService`** → Use `SOPProcessingAbstraction` (if applicable)

### Business Outcomes Pillar
- **`RoadmapGenerationService`** → Use `StrategicPlanningAbstraction` (already references it but needs proper integration)
- **`POCGenerationService`** → Use `FinancialAnalysisAbstraction` + `StrategicPlanningAbstraction`
- **`BusinessOutcomesOrchestrator`** → Use `FinancialAnalysisAbstraction` + `StrategicPlanningAbstraction`

---

## Implementation Steps

### Phase 1: Create Abstractions in Public Works Foundation

1. **Add adapter creation** to `PublicWorksFoundationService._create_all_adapters()`:
   - `BPMNProcessingAdapter`
   - `SOPParsingAdapter`
   - `SOPEnhancementAdapter`
   - `StandardStrategicPlanningAdapter`
   - `StandardFinancialAdapter`
   - `HuggingFaceStrategicPlanningAdapter` (from `future_abstractions/`)
   - `HuggingFaceFinancialAdapter` (from `future_abstractions/`)

2. **Add abstraction creation** to `PublicWorksFoundationService._create_all_abstractions()`:
   - `BPMNProcessingAbstraction`
   - `SOPProcessingAbstraction`
   - `SOPEnhancementAbstraction`
   - `StrategicPlanningAbstraction`
   - `FinancialAnalysisAbstraction`

3. **Expose via Platform Gateway**:
   - Add to `REALM_ABSTRACTION_MAPPINGS` for `business_enablement` realm:
     - `bpmn_processing`
     - `sop_processing`
     - `sop_enhancement`
     - `strategic_planning`
     - `financial_analysis`

### Phase 2: Refactor Services

#### Operations Pillar
1. **`WorkflowManagerService`**:
   - Get `WorkflowOrchestrationAbstraction` and `BPMNProcessingAbstraction` via Platform Gateway
   - Replace direct workflow logic with abstraction calls

2. **`WorkflowConversionService`**:
   - Get `BPMNProcessingAbstraction` and `SOPProcessingAbstraction` via Platform Gateway
   - Replace direct BPMN/SOP parsing with abstraction calls

#### Insights Pillar
3. **`SOPBuilderService`**:
   - Get `SOPProcessingAbstraction` and `SOPEnhancementAbstraction` via Platform Gateway
   - Replace direct SOP logic with abstraction calls

#### Business Outcomes Pillar
4. **`RoadmapGenerationService`**:
   - Get `StrategicPlanningAbstraction` via Platform Gateway (already references it)
   - Replace fallback logic with required abstraction

5. **`POCGenerationService`**:
   - Get `FinancialAnalysisAbstraction` and `StrategicPlanningAbstraction` via Platform Gateway
   - Replace direct financial calculations with abstraction calls

6. **`BusinessOutcomesOrchestrator`**:
   - Get `FinancialAnalysisAbstraction` and `StrategicPlanningAbstraction` via Platform Gateway
   - Replace direct financial/strategic logic with abstraction calls

---

## Benefits

1. **Swap-ability**: Can swap local libraries for hosted solutions (e.g., HuggingFace, Camunda Cloud)
2. **Consistency**: All pillars use the same architectural pattern
3. **Testability**: Abstractions can be easily mocked for testing
4. **Future-proof**: Ready for Option C (everything as a service) deployment

---

## Next Steps

1. Start with Phase 1: Create abstractions in Public Works Foundation
2. Then Phase 2: Refactor services one pillar at a time

