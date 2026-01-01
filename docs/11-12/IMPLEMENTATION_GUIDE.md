# Bottom-Up Test Strategy - Implementation Guide

**Quick Start**: Get your test suite overhauled in 8 phases

---

## 🎯 What We're Building

A **bottom-up, layer-by-layer** test strategy that:
- ✅ Catches issues at the layer where they occur
- ✅ Tests each component in isolation
- ✅ Validates production code (no mocks, TODOs, placeholders)
- ✅ Reduces Cursor token costs (less troubleshooting needed)

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Validate Production Code

```bash
cd tests
python3 scripts/validate_production_code.py
```

**What it does**: Scans for mocks, TODOs, placeholders, hardcoded values

**Fix any violations** before proceeding.

### Step 2: Run Tests Layer-by-Layer

```bash
# Run Layer 0 (Infrastructure Adapters)
python3 run_tests.py --layer 0

# Run Layers 0-3 (Foundation layers)
python3 run_tests.py --layers 0-3

# Run all layers in order
python3 run_tests.py --all --validate
```

**What it does**: Tests each layer in isolation, stops on first failure

---

## 📋 Implementation Phases

### Phase 1: Validation Script ✅ DONE

**File**: `tests/scripts/validate_production_code.py`

**Status**: ✅ Created and ready to use

**Usage**:
```bash
python3 tests/scripts/validate_production_code.py
```

**What it checks**:
- ❌ No mocks in production code
- ❌ No TODOs/FIXMEs
- ❌ No empty implementations (`pass`)
- ❌ No hardcoded test values

---

### Phase 2: Test Runner Enhancement ✅ DONE

**File**: `tests/run_tests.py`

**Status**: ✅ Enhanced with layer-by-layer execution

**New Features**:
- `--layer N`: Run specific layer (0-8)
- `--layers 0-6`: Run range of layers
- `--validate`: Validate production code before testing
- `--all`: Run all layers in order (bottom-up)

**Usage**:
```bash
# Run Layer 0 only
python3 run_tests.py --layer 0

# Run Layers 0-3
python3 run_tests.py --layers 0-3

# Run all with validation
python3 run_tests.py --all --validate
```

---

### Phase 3: Create Layer 0 Tests (Infrastructure Adapters)

**Goal**: Test each adapter in isolation

**Create**: `tests/unit/infrastructure_adapters/`

**Test Files Needed**:
- `test_supabase_file_management_adapter.py`
- `test_redis_adapter.py`
- `test_arangodb_adapter.py`
- `test_opentelemetry_health_adapter.py`
- `test_telemetry_adapter.py`

**Template Generator**:
```bash
python3 tests/scripts/generate_test_template.py \
    --layer infrastructure_adapters \
    --component SupabaseFileManagementAdapter \
    --output tests/unit/infrastructure_adapters/test_supabase_file_management_adapter.py
```

**Test Pattern**:
- Test initialization
- Test core operations
- Test error handling
- Fast (< 1 second per test)

---

### Phase 4: Enhance Layer 1 Tests (Foundations)

**Goal**: Test foundation services in isolation

**Enhance**: `tests/unit/foundations/`

**Test Files to Add/Enhance**:
- `test_curator_foundation.py`
- `test_communication_foundation.py`
- `test_agentic_foundation.py`

**Test Pattern**:
- Test foundation initializes
- Test foundation provides abstractions
- Test foundation services work

---

### Phase 5: Enhance Layer 2 Tests (Smart City Services)

**Goal**: Test Smart City services in isolation

**Enhance**: `tests/unit/smart_city/`

**Test Files to Add/Enhance**:
- `test_data_steward_service.py`
- `test_conductor_service.py`
- `test_post_office_service.py`
- `test_traffic_cop_service.py`
- `test_nurse_service.py`
- `test_content_steward_service.py`
- `test_city_manager_service.py`

**Test Pattern**:
- Test service initializes
- Test SOA APIs work
- Test service composes dependencies

---

### Phase 6: Create Layer 3 Tests (Enabling Services)

**Goal**: Test enabling services in isolation

**Create**: `tests/unit/enabling_services/`

**Test Files Needed**:
- `test_file_parser_service.py`
- `test_format_composer_service.py`
- `test_data_analyzer_service.py`
- `test_metrics_calculator_service.py`
- `test_visualization_engine_service.py`
- `test_roadmap_generation_service.py`
- `test_poc_generation_service.py`

**Template Generator**:
```bash
python3 tests/scripts/generate_test_template.py \
    --layer enabling_services \
    --component FileParserService \
    --output tests/unit/enabling_services/test_file_parser_service.py
```

**Test Pattern**:
- Test service initializes
- Test SOA APIs work
- Test service uses Smart City services correctly

---

### Phase 7: Enhance Layer 4-6 Tests (Orchestrators, MCP Servers, Agents)

**Goal**: Test orchestrators, MCP servers, and agents in isolation

**Enhance**:
- `tests/unit/orchestrators/`
- `tests/unit/mcp_servers/`
- `tests/unit/agents/`

**Test Pattern**:
- Test component initializes
- Test component uses dependencies correctly
- Test component exposes expected APIs

---

### Phase 8: Add Test Markers

**Goal**: Mark all tests with appropriate markers

**Markers Needed**:
- `@pytest.mark.unit`
- `@pytest.mark.fast`
- `@pytest.mark.infrastructure` (Layer 0)
- `@pytest.mark.foundations` (Layer 1)
- `@pytest.mark.smart_city` (Layer 2)
- `@pytest.mark.enabling_services` (Layer 3)
- `@pytest.mark.orchestrators` (Layer 4)
- `@pytest.mark.mcp` (Layer 5)
- `@pytest.mark.agents` (Layer 6)
- `@pytest.mark.integration` (Layer 7)
- `@pytest.mark.e2e` (Layer 8)

**Add to `pytest.ini`**:
```ini
markers =
    unit: Unit tests
    fast: Fast tests (< 1 second)
    infrastructure: Infrastructure adapter tests
    foundations: Foundation service tests
    smart_city: Smart City service tests
    enabling_services: Enabling service tests
    orchestrators: Orchestrator tests
    mcp: MCP server tests
    agents: Agent tests
    integration: Integration tests
    e2e: End-to-end tests
```

---

## 🛠️ Tools Created

### 1. Production Code Validator ✅

**File**: `tests/scripts/validate_production_code.py`

**Usage**:
```bash
python3 tests/scripts/validate_production_code.py
```

**What it does**:
- Scans production code for anti-patterns
- Reports violations with file/line numbers
- Exits with error code if violations found

### 2. Test Template Generator ✅

**File**: `tests/scripts/generate_test_template.py`

**Usage**:
```bash
python3 tests/scripts/generate_test_template.py \
    --layer infrastructure_adapters \
    --component SupabaseFileManagementAdapter \
    --output tests/unit/infrastructure_adapters/test_supabase_file_management_adapter.py
```

**What it does**:
- Generates test file templates
- Supports multiple layers
- Includes fixtures and test patterns

### 3. Enhanced Test Runner ✅

**File**: `tests/run_tests.py`

**New Features**:
- Layer-by-layer execution
- Production code validation
- Bottom-up test execution

---

## 📊 Test Execution Examples

### Run Single Layer

```bash
# Test infrastructure adapters only
python3 run_tests.py --layer 0

# Test foundations only
python3 run_tests.py --layer 1
```

### Run Layer Range

```bash
# Test foundation layers (0-3)
python3 run_tests.py --layers 0-3

# Test specific layers
python3 run_tests.py --layers 0,1,2
```

### Run All with Validation

```bash
# Validate production code, then run all layers
python3 run_tests.py --all --validate
```

### Run Fast Tests Only

```bash
# Run only fast tests (< 1 second)
python3 run_tests.py --fast
```

---

## ✅ Validation Checklist

### For Each Test File

- [ ] Tests one component in isolation
- [ ] Tests initialization
- [ ] Tests core operations
- [ ] Tests error handling
- [ ] Fast (< 1 second per test)
- [ ] No dependencies on other layers (use mocks)
- [ ] Clear test names
- [ ] Test documentation
- [ ] Appropriate markers (`@pytest.mark.unit`, `@pytest.mark.fast`, layer marker)

### For Each Production File

- [ ] No mocks in production code
- [ ] No TODOs/FIXMEs
- [ ] No empty implementations (`pass`)
- [ ] No hardcoded test values
- [ ] No HACK/CHEAT comments

---

## 🎯 Success Criteria

### Test Coverage

- **Layer 0**: 100% adapter coverage
- **Layer 1**: 100% foundation coverage
- **Layer 2**: 100% Smart City service coverage
- **Layer 3**: 100% enabling service coverage
- **Layer 4**: 100% orchestrator coverage
- **Layer 5**: 100% MCP server coverage
- **Layer 6**: 100% agent coverage

### Test Speed

- **Layer 0-6**: All tests < 1 second each
- **Total unit tests**: < 5 minutes
- **Integration tests**: < 10 minutes
- **E2E tests**: < 15 minutes

### Issue Detection

- **Issues caught at layer where they occur**: 90%+
- **Issues caught in unit tests**: 80%+
- **Issues caught in integration tests**: 15%+
- **Issues caught in E2E tests**: 5%+

---

## 💡 Benefits

### Immediate Benefits

1. **Faster feedback**: Issues caught in < 1 second
2. **Easier debugging**: Know exactly which layer failed
3. **Better isolation**: Test one thing at a time
4. **Prevent production issues**: Validation catches mocks/TODOs

### Long-Term Benefits

1. **Reduced Cursor costs**: Less troubleshooting needed
2. **Faster development**: Catch issues before they compound
3. **Better code quality**: Validation prevents bad patterns
4. **Easier onboarding**: Clear test structure

---

## 🚀 Next Steps

1. **Run validation script** (5 minutes)
   ```bash
   python3 tests/scripts/validate_production_code.py
   ```

2. **Fix any violations** (varies)

3. **Start with Layer 0** (2 hours)
   - Create infrastructure adapter tests
   - Test one adapter at a time

4. **Move to next layer** (repeat)
   - Only proceed if current layer passes
   - Test next layer in isolation

5. **Add markers** (1 hour)
   - Mark all tests with appropriate markers
   - Update `pytest.ini`

---

## 📚 Documentation

- **Strategy**: `docs/11-12/BOTTOM_UP_TEST_STRATEGY.md`
- **Execution Guide**: `docs/11-12/TEST_EXECUTION_GUIDE.md`
- **Test Suite Evaluation**: `docs/11-12/TEST_SUITE_EVALUATION.md`

---

## 🆘 Troubleshooting

### Tests Fail at Layer 0

**Issue**: Infrastructure adapters failing

**Solution**:
1. Read error message
2. Check adapter initialization
3. Verify adapter dependencies
4. Fix at Layer 0 (don't move to Layer 1)

### Validation Fails

**Issue**: Production code has violations

**Solution**:
1. Review violations
2. Fix mocks/TODOs/placeholders
3. Re-run validation
4. Proceed only when validation passes

### Tests Too Slow

**Issue**: Tests taking > 1 second

**Solution**:
1. Check for real API calls (should be mocked)
2. Check for real database calls (should be mocked)
3. Optimize test setup/teardown
4. Use fixtures efficiently

---

## 📝 Summary

**Key Principle**: Test from the bottom up, catch issues where they occur

**Workflow**:
1. Validate production code
2. Run Layer 0 tests
3. Fix any failures
4. Move to next layer
5. Repeat

**Result**: Faster feedback, easier debugging, reduced Cursor costs

