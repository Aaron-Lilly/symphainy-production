# Testing Execution Plan - Bottom-Up Approach

**Date**: November 15, 2025  
**Status**: All Phases Complete - Ready for Full Testing  
**Approach**: Bottom-Up (Layer 1 → Layer 10)

---

## Testing Strategy

Start with **Layer 1** (foundation) and work up to **Layer 10** (deployment). This ensures:
1. ✅ Foundation is solid before building on it
2. ✅ Issues are caught early (fail fast)
3. ✅ Each layer validates the previous layer
4. ✅ Critical tests run after foundation is validated

---

## Execution Order

### Phase A: Foundation Validation (Layers 1-2)

**Goal**: Ensure infrastructure and abstractions work correctly

#### Layer 1: Adapter Infrastructure Tests ⭐ START HERE

**Time**: 30-45 minutes  
**Priority**: HIGH (Foundation)

```bash
# 1. Start test infrastructure
docker-compose -f tests/docker-compose.test.yml up -d

# 2. Run Layer 1 tests
pytest tests/integration/infrastructure_adapters/test_redis_adapter_real.py -v
pytest tests/integration/infrastructure_adapters/test_arangodb_adapter_real.py -v
pytest tests/integration/infrastructure_adapters/test_meilisearch_adapter_real.py -v

# 3. Run all Layer 1 tests
pytest tests/integration/infrastructure_adapters/ -v
```

**What We're Validating**:
- ✅ Redis adapter connects to real Redis
- ✅ ArangoDB adapter connects to real ArangoDB
- ✅ Meilisearch adapter connects to real Meilisearch
- ✅ Adapter versions match requirements.txt
- ✅ All adapter operations work with real infrastructure

**Success Criteria**: All Layer 1 tests pass

---

#### Layer 2: Abstraction Exposure Tests

**Time**: 30-45 minutes  
**Priority**: HIGH (Foundation)

```bash
# Run Layer 2 tests
pytest tests/integration/foundations/test_smart_city_abstraction_access.py -v
pytest tests/integration/platform_gateway/test_realm_abstraction_access.py -v
pytest tests/integration/platform_gateway/test_abstraction_composition.py -v
```

**What We're Validating**:
- ✅ Smart City has direct access to abstractions
- ✅ Other realms access abstractions via Platform Gateway
- ✅ Platform Gateway validates realm access correctly
- ✅ Abstractions are created by Public Works Foundation

**Success Criteria**: All Layer 2 tests pass

---

### Phase B: Production Readiness Validation (Layers 7-9)

**Goal**: Ensure production readiness fixes are in place

#### Layer 7: Access Pattern Tests ⚠️ CRITICAL

**Time**: 45-60 minutes  
**Priority**: CRITICAL (Production Readiness)

```bash
# Run Layer 7 tests
pytest tests/integration/orchestrators/test_orchestrator_access_patterns.py -v
pytest tests/integration/enabling_services/test_enabling_service_access_patterns.py -v
```

**What We're Validating**:
- ✅ Orchestrators use four-tier access pattern
- ✅ Enabling services use three-tier access pattern
- ✅ No methods return None silently
- ✅ All failures return structured errors

**Success Criteria**: All Layer 7 tests pass

---

#### Layer 8: No Placeholder Tests ⚠️ CRITICAL

**Time**: 30-45 minutes  
**Priority**: CRITICAL (Production Readiness)

```bash
# Run Layer 8 tests
pytest tests/integration/production_readiness/test_no_placeholders.py -v
pytest tests/integration/production_readiness/test_no_placeholder_tokens.py -v
pytest tests/integration/production_readiness/test_real_quality_scores.py -v
```

**What We're Validating**:
- ✅ No placeholder text in orchestrator responses
- ✅ No placeholder tokens in authentication
- ✅ No placeholder quality scores
- ✅ All data is real or properly error-handled

**Success Criteria**: All Layer 8 tests pass

---

#### Layer 9: Graceful Failure Tests

**Time**: 30-45 minutes  
**Priority**: HIGH (Production Readiness)

```bash
# Run Layer 9 tests
pytest tests/integration/production_readiness/test_graceful_failures.py -v
pytest tests/integration/production_readiness/test_error_code_consistency.py -v
```

**What We're Validating**:
- ✅ Services fail gracefully (no crashes)
- ✅ Error messages are clear and actionable
- ✅ Error codes are consistent

**Success Criteria**: All Layer 9 tests pass

---

### Phase C: Service & Orchestrator Validation (Layers 3-4)

**Goal**: Ensure services and orchestrators work correctly

#### Layer 3: Enabling Service Tests

**Time**: 60-90 minutes  
**Priority**: MEDIUM

```bash
# Run Layer 3 tests (as they're created)
pytest tests/unit/enabling_services/ -v
```

**What We're Validating**:
- ✅ All enabling services work in isolation
- ✅ Services use correct abstractions
- ✅ Services use correct Smart City services

**Success Criteria**: All Layer 3 tests pass

---

#### Layer 4: Orchestrator Output Tests ⚠️ CRITICAL

**Time**: 60-90 minutes  
**Priority**: CRITICAL (CTO Demo Readiness)

```bash
# Run Layer 4 tests
pytest tests/integration/orchestrators/test_business_outcomes_roadmap_output.py -v
pytest tests/integration/orchestrators/test_business_outcomes_poc_output.py -v
```

**What We're Validating**:
- ✅ Roadmap output is impressive (> 500 words, context-specific)
- ✅ POC proposal output is impressive (> 800 words, includes financial analysis)
- ✅ All required sections are present
- ✅ Pillar outputs are integrated

**Success Criteria**: All Layer 4 tests pass

---

### Phase D: End-to-End Validation (Layers 5-6, 10)

**Goal**: Validate complete system works end-to-end

#### Layer 5: CTO Demo Scenarios ⚠️ CRITICAL

**Time**: 90-120 minutes  
**Priority**: CRITICAL (CTO Demo Readiness)

```bash
# Run Layer 5 tests
pytest tests/integration/demo_scenarios/ -v
```

**What We're Validating**:
- ✅ All 3 CTO demo scenarios work end-to-end
- ✅ Outputs are impressive (not generic)
- ✅ All MVP requirements are met

**Success Criteria**: All Layer 5 tests pass

---

#### Layer 6: MVP Requirements Tests

**Time**: 60-90 minutes  
**Priority**: MEDIUM

```bash
# Run Layer 6 tests
pytest tests/integration/mvp_requirements/ -v
```

**What We're Validating**:
- ✅ All MVP requirements are met
- ✅ All UI elements work
- ✅ All agents respond correctly

**Success Criteria**: All Layer 6 tests pass

---

#### Layer 10: EC2 Deployment Tests

**Time**: 30-45 minutes  
**Priority**: MEDIUM

```bash
# Run Layer 10 tests
pytest tests/integration/deployment/ -v
```

**What We're Validating**:
- ✅ Frontend accessible from outside EC2
- ✅ Backend API accessible from frontend
- ✅ Configuration supports Option C migration

**Success Criteria**: All Layer 10 tests pass

---

## Quick Start Commands

### Full Test Suite (Bottom-Up)

```bash
# 1. Start infrastructure
docker-compose -f tests/docker-compose.test.yml up -d

# 2. Run all tests in order
pytest tests/integration/infrastructure_adapters/ -v  # Layer 1
pytest tests/integration/foundations/ tests/integration/platform_gateway/ -v  # Layer 2
pytest tests/integration/orchestrators/test_orchestrator_access_patterns.py tests/integration/enabling_services/test_enabling_service_access_patterns.py -v  # Layer 7
pytest tests/integration/production_readiness/ -v  # Layers 8-9
pytest tests/integration/orchestrators/test_business_outcomes_*.py -v  # Layer 4
pytest tests/integration/deployment/ -v  # Layer 10
```

### Critical Tests Only

```bash
# Run only critical tests
pytest tests/integration/orchestrators/test_orchestrator_access_patterns.py -v  # Layer 7
pytest tests/integration/production_readiness/test_no_placeholders.py tests/integration/production_readiness/test_no_placeholder_tokens.py -v  # Layer 8
pytest tests/integration/orchestrators/test_business_outcomes_roadmap_output.py tests/integration/orchestrators/test_business_outcomes_poc_output.py -v  # Layer 4
```

---

## Expected Timeline

- **Layer 1**: 30-45 minutes
- **Layer 2**: 30-45 minutes
- **Layer 7**: 45-60 minutes
- **Layer 8**: 30-45 minutes
- **Layer 9**: 30-45 minutes
- **Layer 3**: 60-90 minutes
- **Layer 4**: 60-90 minutes
- **Layer 5**: 90-120 minutes
- **Layer 6**: 60-90 minutes
- **Layer 10**: 30-45 minutes

**Total Estimated Time**: 6-9 hours (can be parallelized)

---

## Success Criteria

### Foundation (Layers 1-2)
- ✅ All infrastructure adapters work with real infrastructure
- ✅ All abstractions are correctly exposed

### Production Readiness (Layers 7-9)
- ✅ All access patterns are correct
- ✅ No placeholder data exists
- ✅ All failures are graceful

### Functionality (Layers 3-4)
- ✅ All enabling services work
- ✅ Orchestrator outputs are impressive

### End-to-End (Layers 5-6, 10)
- ✅ All CTO demo scenarios work
- ✅ All MVP requirements are met
- ✅ Deployment configuration is correct

---

## Troubleshooting

### Infrastructure Not Available
```bash
# Start test infrastructure
docker-compose -f tests/docker-compose.test.yml up -d

# Check container health
docker-compose -f tests/docker-compose.test.yml ps
```

### Import Errors
```bash
# Ensure you're in project root
cd /home/founders/demoversion/symphainy_source

# Check Python path
python3 -c "import sys; print(sys.path)"
```

### Test Failures
1. Check which layer failed
2. Review error messages
3. Fix issues in that layer before proceeding
4. Re-run tests for that layer

---

**Ready to start! Begin with Layer 1 tests.**
