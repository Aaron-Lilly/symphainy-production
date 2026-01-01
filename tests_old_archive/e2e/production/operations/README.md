# Operations Pillar E2E Tests

## Overview

Comprehensive end-to-end tests for the Operations Pillar using production platform containers and real LLM calls.

## Test Scenarios

### 1. Health Check
- **Test**: `test_operations_pillar_health`
- **Validates**: Operations Solution Orchestrator is accessible
- **Duration**: < 1 minute

### 2. SOP → Workflow Conversion
- **Test**: `test_workflow_from_sop_conversion`
- **Validates**:
  - SOP document can be converted to workflow diagram
  - Workflow structure is valid (nodes, edges)
  - Conversion uses real LLM calls
- **Duration**: ~5 minutes

### 3. Workflow → SOP Conversion
- **Test**: `test_sop_from_workflow_conversion`
- **Validates**:
  - Workflow diagram can be converted to SOP document
  - SOP structure is valid (title, sections, steps)
  - Conversion uses real LLM calls
- **Duration**: ~5 minutes

### 4. Workflow Visualization
- **Test**: `test_workflow_visualization`
- **Validates**:
  - Workflow can be visualized
  - Visualization data is properly formatted
- **Duration**: ~5 minutes

### 5. SOP Visualization
- **Test**: `test_sop_visualization`
- **Validates**:
  - SOP can be visualized
  - Visualization data is properly formatted
- **Duration**: ~5 minutes

### 6. Coexistence Analysis
- **Test**: `test_coexistence_analysis`
- **Validates**:
  - Can analyze human-AI coexistence
  - Generates optimized blueprint
  - Blueprint has proper structure
- **Duration**: ~10 minutes

### 7. Interactive SOP Creation
- **Test**: `test_interactive_sop_creation`
- **Validates**:
  - Can start interactive SOP creation session
  - Can chat to build SOP
  - Can publish final SOP
- **Duration**: ~10 minutes

### 8. AI-Optimized Blueprint Generation
- **Test**: `test_ai_optimized_blueprint`
- **Validates**:
  - Can generate optimized blueprint from available documents
  - Blueprint includes AI recommendations
  - Blueprint structure is valid
- **Duration**: ~10 minutes

### 9. Complete Operations Journey
- **Test**: `test_complete_operations_journey`
- **Validates**: End-to-end operations pillar journey:
  1. Create SOP
  2. Convert SOP to workflow
  3. Convert workflow back to SOP
  4. Visualize workflow
  5. Analyze coexistence
- **Duration**: ~15 minutes

## Running the Tests

### Prerequisites

1. **Production containers must be running**
   ```bash
   # Verify backend is accessible
   curl http://localhost:8000/api/health
   ```

2. **Environment variables** (optional):
   ```bash
   export TEST_BACKEND_URL=http://localhost:8000
   export TEST_FRONTEND_URL=http://localhost:3000
   ```

### Run All Tests

```bash
# From project root
pytest tests/e2e/production/operations/ -v
```

### Run Specific Test

```bash
# Run single test
pytest tests/e2e/production/operations/test_operations_pillar_e2e.py::TestOperationsPillarE2E::test_workflow_from_sop_conversion -v

# Run with markers
pytest tests/e2e/production/operations/ -v -m operations
```

### Run with Timeout

```bash
# Increase timeout for slow LLM calls
pytest tests/e2e/production/operations/ -v --timeout=600
```

## Test Architecture

### Endpoints Tested

All tests use the new **Solution Orchestrator** endpoints:

- `POST /api/v1/operations-solution/workflow-from-sop`
- `POST /api/v1/operations-solution/sop-from-workflow`
- `POST /api/v1/operations-solution/workflow-visualization`
- `POST /api/v1/operations-solution/sop-visualization`
- `POST /api/v1/operations-solution/coexistence-analysis`
- `POST /api/v1/operations-solution/interactive-sop/start`
- `POST /api/v1/operations-solution/interactive-sop/chat`
- `POST /api/v1/operations-solution/interactive-sop/publish`
- `POST /api/v1/operations-solution/ai-optimized-blueprint`

### Request Flow

```
Test → HTTP Client → Universal Pillar Router
  ↓
FrontendGatewayService
  ↓
OperationsSolutionOrchestratorService (Solution Realm)
  ↓
OperationsJourneyOrchestrator (Journey Realm)
  ↓
Operations Realm Services / Agents
```

### Platform Correlation

All requests include:
- `X-Session-Token`: Session authentication
- `X-User-Id`: User identification
- `user_context`: Full user context for platform correlation

## Validation Criteria

### SOP Structure Validation
- ✅ Has `title` or `sections` or `steps` or `content`
- ✅ Content is not empty
- ✅ Structure is valid JSON/dict

### Workflow Structure Validation
- ✅ Has `nodes` or `tasks` or `steps` or `elements`
- ✅ Structure is valid JSON/dict
- ✅ Contains workflow elements

### Blueprint Validation
- ✅ Has `blueprint` or `deliverable.blueprint`
- ✅ Blueprint is not None
- ✅ Contains optimization recommendations

## Expected Results

### Success Criteria
- ✅ All endpoints return `200` or `201` status codes
- ✅ Response contains expected data structures
- ✅ LLM calls complete successfully (no timeouts)
- ✅ Platform correlation data is preserved

### Failure Scenarios
- ❌ `404`: Endpoint not found (routing issue)
- ❌ `500`: Server error (check logs)
- ❌ `Timeout`: LLM call took too long (increase timeout)
- ❌ `401/403`: Authentication issue (check session token)

## Debugging

### Enable Verbose Logging

```bash
pytest tests/e2e/production/operations/ -v -s --log-cli-level=INFO
```

### Check Response Details

Tests log response data (first 500 chars) for debugging:
```python
logger.info(f"✅ Response: {json.dumps(result, indent=2)[:500]}")
```

### Common Issues

1. **Backend not accessible**
   - Check containers are running: `docker ps`
   - Verify health endpoint: `curl http://localhost:8000/api/health`

2. **Session token issues**
   - Check `test_session` fixture is working
   - Verify session creation endpoint is accessible

3. **LLM timeouts**
   - Increase timeout: `--timeout=600`
   - Check LLM service is running
   - Verify API keys are configured

4. **Endpoint not found (404)**
   - Verify FrontendGatewayService routing
   - Check OperationsSolutionOrchestratorService is registered with Curator
   - Verify endpoint path matches `handle_request` routing

## Integration with CTO Demo Scenarios

These tests validate the operations pillar capabilities used in the 3 CTO demo scenarios:

1. **Autonomous Vehicle Testing (Defense T&E)**
   - Uses: SOP generation, workflow creation, coexistence analysis

2. **Life Insurance Underwriting**
   - Uses: Workflow creation, SOP generation, blueprint optimization

3. **Data Mash Coexistence/Migration**
   - Uses: Coexistence analysis, AI-optimized blueprint, workflow conversion

## Next Steps

1. ✅ All core capabilities tested
2. ⏳ Add performance benchmarks
3. ⏳ Add load testing
4. ⏳ Add integration with Content Pillar (file upload)
5. ⏳ Add integration with Insights Pillar (analysis results)





