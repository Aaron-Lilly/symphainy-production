# Test Update Process - Parallel Work Stream

**For:** Test execution team  
**Purpose:** Process for updating tests while CI/CD integration proceeds in parallel

---

## 🎯 Overview

This document outlines the process for running and updating tests in parallel with CI/CD integration work.

**Key Points:**
- Tests are ready to run
- CI/CD integration is independent
- Test updates can be made in parallel
- Changes will be integrated automatically

---

## 📋 Test Execution Workflow

### 1. Initial Test Run
```bash
cd /home/founders/demoversion/symphainy_source/tests

# Run all tests to establish baseline
pytest tests/ -v --tb=short > test_results_baseline.txt

# Review results
cat test_results_baseline.txt
```

### 2. Identify Issues
- **Failing tests:** Note which tests fail and why
- **Skipped tests:** Note which tests skip (infrastructure unavailable)
- **Slow tests:** Note tests that take too long
- **Missing tests:** Note gaps in coverage

### 3. Update Tests
- **Fix failing tests:** Update test logic, assertions, or infrastructure setup
- **Add missing tests:** Create tests for uncovered functionality
- **Optimize slow tests:** Improve test performance
- **Document changes:** Add comments explaining updates

### 4. Re-run Tests
```bash
# Run updated tests
pytest tests/ -v --tb=short > test_results_updated.txt

# Compare with baseline
diff test_results_baseline.txt test_results_updated.txt
```

---

## 🔄 Integration Process

### Test Updates → CI/CD Integration

**Automatic Integration:**
- Test updates are committed to the same repository
- CI/CD pipeline will automatically pick up test changes
- No manual integration needed

**Process:**
1. **Test team commits updates:**
   ```bash
   git add tests/
   git commit -m "Update tests: fix failing tests, add missing coverage"
   git push
   ```

2. **CI/CD automatically runs updated tests:**
   - CI pipeline triggers on commit
   - Runs all tests (unit, integration, E2E)
   - Reports results

3. **Results available:**
   - CI/CD dashboard shows test results
   - Test team can see CI/CD results
   - Both teams coordinate on fixes

---

## 📝 Test Update Guidelines

### What to Update

✅ **DO Update:**
- Test logic that's incorrect
- Assertions that don't match API responses
- Test data that's outdated
- Missing test coverage
- Slow or flaky tests

❌ **DON'T Update:**
- Test infrastructure (pytest.ini, conftest.py) - coordinate with CI/CD team
- Test markers - coordinate with CI/CD team
- Test configuration structure - coordinate with CI/CD team

### Update Patterns

**Fixing Failing Tests:**
```python
# Before (failing)
async def test_my_feature(self, api_base_url):
    response = await client.get(f"{api_base_url}/api/endpoint")
    assert response.json()["status"] == "success"  # Fails if status is "ok"

# After (fixed)
async def test_my_feature(self, api_base_url):
    response = await client.get(f"{api_base_url}/api/endpoint")
    assert response.json()["status"] in ["success", "ok"]  # More flexible
```

**Adding Missing Tests:**
```python
@pytest.mark.e2e
@pytest.mark.critical
class TestNewFeature:
    @pytest.mark.asyncio
    async def test_new_feature(self, api_base_url, session_token):
        skip_if_missing_real_infrastructure(["supabase"])
        # Test implementation
        assert True
```

**Optimizing Slow Tests:**
```python
# Add timeout marker
@pytest.mark.timeout_30  # 30 second timeout
async def test_slow_feature(self, api_base_url):
    # Test implementation
    pass
```

---

## 🗂️ File Organization

### Test Files Structure
```
tests/
├── unit/                    # Unit tests
│   ├── foundations/         # Foundation layer tests
│   ├── smart_city/          # Smart City service tests
│   └── ...
├── integration/             # Integration tests
│   ├── service_discovery/   # Service discovery tests
│   ├── cross_realm/        # Cross-realm tests
│   ├── saga/               # Saga integration tests
│   ├── wal/                # WAL integration tests
│   └── pillar/             # Pillar integration tests
├── e2e/                    # E2E tests
│   └── production/
│       ├── smoke_tests/    # Platform startup tests
│       ├── pillar_validation/  # Pillar validation tests
│       ├── cross_pillar/   # Cross-pillar workflow tests
│       └── production_readiness/  # Production readiness tests
├── config/                 # Test configuration
├── utils/                  # Test utilities
└── fixtures/               # Test fixtures
```

### Where to Add Tests

- **New unit tests:** Add to `tests/unit/` in appropriate subdirectory
- **New integration tests:** Add to `tests/integration/` in appropriate subdirectory
- **New E2E tests:** Add to `tests/e2e/production/` in appropriate subdirectory

---

## 🔍 Test Quality Checklist

Before committing test updates, verify:

- [ ] Tests follow existing patterns
- [ ] Tests use appropriate markers
- [ ] Tests have proper error handling
- [ ] Tests skip gracefully if infrastructure unavailable
- [ ] Tests are well-documented
- [ ] Tests pass locally
- [ ] Tests are not flaky

---

## 📊 Progress Tracking

### Test Execution Status
Track test execution progress:
- Total tests: ~200+
- Passing tests: ___
- Failing tests: ___
- Skipped tests: ___

### Test Update Status
Track test update progress:
- Tests fixed: ___
- Tests added: ___
- Tests optimized: ___

### CI/CD Integration Status
- CI/CD team working on: Pipeline integration
- Test updates will be: Automatically integrated
- Coordination needed: None (automatic)

---

## 🤝 Coordination

### With CI/CD Team
- **No blocking dependencies:** Test updates don't block CI/CD work
- **Automatic integration:** Test changes automatically picked up
- **Communication:** Use commit messages to document changes

### Commit Messages
Use clear commit messages:
```bash
# Good commit messages
git commit -m "Fix: Update content pillar test assertions to match API response"
git commit -m "Add: E2E test for new feature X"
git commit -m "Optimize: Reduce timeout for slow integration test"

# Avoid
git commit -m "Update tests"  # Too vague
```

---

## 📚 Resources

- **Test Documentation:** `tests/README.md`
- **Running Tests:** `tests/RUNNING_TESTS.md`
- **Test Strategy:** `docs/TESTING_STRATEGY_OVERHAUL_PLAN.md`
- **Test Configuration:** `tests/config/test_config.py`

---

**Last Updated:** January 2025  
**Status:** Ready for parallel work




