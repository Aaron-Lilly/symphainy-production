# Feature Testing Process Guide

**Last Updated:** December 1, 2025  
**Version:** 2.0 (Post-Phase 1-4 Improvements)

---

## Overview

This guide explains how to add tests for new features in the SymphAIny platform. Following this process ensures your features are properly tested and integrated into the CI/CD pipeline.

---

## Testing Pyramid

```
        /\
       /  \      E2E Tests (Few, Critical)
      /____\     - Full user journeys
     /      \    - Critical business flows
    /________\   Integration Tests (Some)
   /          \  - Component interactions
  /____________\ Unit Tests (Many)
                - Individual functions
                - Fast, isolated
```

**Principle:** Many fast unit tests, some integration tests, few critical E2E tests.

---

## Step-by-Step: Adding Tests for a New Feature

### Step 1: Write Unit Tests (First!)

**When:** As you write the feature code

**Location:** `tests/unit/`

**Example:**
```python
# tests/unit/backend/test_new_feature.py
import pytest
from symphainy_platform.backend.new_feature import NewFeatureService

def test_new_feature_initialization():
    """Test that new feature initializes correctly."""
    service = NewFeatureService()
    assert service is not None
    assert service.status == "ready"

def test_new_feature_process_data():
    """Test data processing logic."""
    service = NewFeatureService()
    result = service.process_data({"key": "value"})
    assert result["processed"] is True
    assert "key" in result
```

**Best Practices:**
- ✅ Test one thing per test
- ✅ Use descriptive test names
- ✅ Test edge cases (empty input, None, etc.)
- ✅ Aim for 100% coverage of your feature code
- ✅ Keep tests fast (< 1 second each)

**Run Locally:**
```bash
cd tests
pytest unit/backend/test_new_feature.py -v
```

---

### Step 2: Write Integration Tests

**When:** After unit tests pass

**Location:** `tests/integration/`

**Example:**
```python
# tests/integration/test_new_feature_integration.py
import pytest
from symphainy_platform.backend.new_feature import NewFeatureService
from symphainy_platform.backend.database import DatabaseService

@pytest.mark.asyncio
async def test_new_feature_with_database():
    """Test new feature integrates with database."""
    db = DatabaseService()
    feature = NewFeatureService(db)
    
    result = await feature.save_data({"key": "value"})
    assert result["saved"] is True
    
    retrieved = await db.get_data(result["id"])
    assert retrieved["key"] == "value"
```

**Best Practices:**
- ✅ Test interactions between components
- ✅ Use real infrastructure (Redis, ArangoDB) when needed
- ✅ Clean up test data after tests
- ✅ Test error handling and edge cases

**Run Locally:**
```bash
# Start infrastructure
docker-compose -f tests/docker-compose.test.yml up -d

# Run integration tests
cd tests
pytest integration/test_new_feature_integration.py -v

# Cleanup
docker-compose -f tests/docker-compose.test.yml down
```

---

### Step 3: Write E2E Tests (If Critical)

**When:** For critical user-facing features

**Location:** `tests/e2e/`

**Example:**
```python
# tests/e2e/test_new_feature_e2e.py
import pytest
import httpx
import os

TEST_BACKEND_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
TEST_FRONTEND_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")

@pytest.mark.asyncio
@pytest.mark.e2e
async def test_new_feature_user_journey():
    """Test complete user journey for new feature."""
    async with httpx.AsyncClient() as client:
        # 1. User accesses feature
        response = await client.get(f"{TEST_FRONTEND_URL}/new-feature")
        assert response.status_code == 200
        
        # 2. User submits data
        response = await client.post(
            f"{TEST_BACKEND_URL}/api/v1/new-feature/process",
            json={"data": "test"}
        )
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        
        # 3. User views results
        response = await client.get(
            f"{TEST_BACKEND_URL}/api/v1/new-feature/results/{result['id']}"
        )
        assert response.status_code == 200
```

**Best Practices:**
- ✅ Only write E2E tests for critical user journeys
- ✅ Test complete workflows, not individual steps
- ✅ Use realistic test data
- ✅ Test error scenarios
- ✅ Keep E2E tests fast (< 5 minutes each)

**Run Locally:**
```bash
# Start full environment
docker-compose -f docker-compose.test.yml up -d

# Run E2E tests
cd tests
TEST_BACKEND_URL=http://localhost:8001 TEST_FRONTEND_URL=http://localhost:3001 \
pytest e2e/test_new_feature_e2e.py -v

# Cleanup
docker-compose -f docker-compose.test.yml down
```

---

### Step 4: Add to CI/CD Pipeline

**When:** After all tests pass locally

**Location:** `.github/workflows/ci-cd-pipeline.yml`

**Unit Tests:** Automatically discovered (no changes needed)

**Integration Tests:** Automatically discovered (no changes needed)

**E2E Tests:** Add to critical tests if needed:
```yaml
- name: Run critical E2E tests
  run: |
    pytest e2e/test_complete_cto_demo_journey.py \
           e2e/test_new_feature_e2e.py \  # Add your test here
           -v -s --timeout=300
```

---

## Test Types by Feature Type

### Backend API Endpoint

**Tests Needed:**
1. ✅ Unit tests for business logic
2. ✅ Integration tests with database
3. ✅ E2E tests for API endpoints (if critical)

**Example Structure:**
```
tests/
├── unit/
│   └── backend/
│       └── test_new_api_endpoint.py
├── integration/
│   └── test_new_api_integration.py
└── e2e/
    └── test_new_api_e2e.py
```

---

### Frontend Component

**Tests Needed:**
1. ✅ Unit tests for component logic
2. ✅ Integration tests with hooks/context
3. ✅ E2E tests for user interactions (if critical)

**Example Structure:**
```
symphainy-frontend/
├── src/
│   └── components/
│       └── NewFeature/
│           ├── NewFeature.tsx
│           └── NewFeature.test.tsx  # Unit tests
└── tests/
    └── integration/
        └── NewFeature.integration.test.tsx
```

---

### Agent/Orchestrator

**Tests Needed:**
1. ✅ Unit tests for agent logic
2. ✅ Integration tests with MCP tools
3. ✅ E2E tests for agent interactions (if critical)

**Example Structure:**
```
tests/
├── unit/
│   └── agents/
│       └── test_new_agent.py
├── integration/
│   └── agents/
│       └── test_new_agent_integration.py
└── e2e/
    └── agents/
        └── test_new_agent_e2e.py
```

---

## Test Coverage Requirements

### Minimum Coverage

- **Unit Tests:** 80%+ coverage for new code
- **Integration Tests:** Cover all critical paths
- **E2E Tests:** Cover critical user journeys

### Checking Coverage

```bash
# Backend coverage
cd tests
pytest unit/ -v --cov=../symphainy-platform --cov-report=html
open htmlcov/index.html

# Frontend coverage
cd symphainy-frontend
npm test -- --coverage
open coverage/lcov-report/index.html
```

---

## Test Markers

Use pytest markers to organize tests:

```python
@pytest.mark.unit
def test_unit_function():
    """Unit test."""
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_integration_with_database():
    """Integration test."""
    pass

@pytest.mark.e2e
@pytest.mark.critical
def test_critical_user_journey():
    """Critical E2E test."""
    pass
```

**Run by Marker:**
```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
pytest -m e2e           # Run only E2E tests
pytest -m critical      # Run only critical tests
```

---

## Best Practices

### 1. Test-Driven Development (TDD)

**Process:**
1. Write failing test
2. Write minimal code to pass
3. Refactor
4. Repeat

**Benefits:**
- ✅ Better test coverage
- ✅ Clearer requirements
- ✅ Fewer bugs

### 2. Test Isolation

**Each test should:**
- ✅ Be independent (no shared state)
- ✅ Clean up after itself
- ✅ Not depend on other tests
- ✅ Be repeatable

### 3. Test Data Management

**Use fixtures:**
```python
@pytest.fixture
def sample_data():
    """Provide test data."""
    return {"key": "value"}

def test_with_fixture(sample_data):
    """Use fixture data."""
    assert sample_data["key"] == "value"
```

### 4. Mock External Services

**Mock external APIs:**
```python
from unittest.mock import Mock, patch

@patch('external_service.api_call')
def test_with_mock(mock_api):
    """Test with mocked external service."""
    mock_api.return_value = {"status": "success"}
    result = my_function()
    assert result["status"] == "success"
```

### 5. Test Error Cases

**Don't just test happy path:**
```python
def test_error_handling():
    """Test error scenarios."""
    with pytest.raises(ValueError):
        process_invalid_data(None)
    
    with pytest.raises(KeyError):
        process_missing_key({})
```

---

## CI/CD Integration

### Automatic Test Discovery

The CI/CD pipeline automatically:
- ✅ Discovers all tests in `tests/unit/`
- ✅ Discovers all tests in `tests/integration/`
- ✅ Runs E2E tests from `tests/e2e/`

### Test Execution Order

1. **Unit Tests** (~5 minutes)
2. **Integration Tests** (~5 minutes)
3. **E2E Tests** (~10-30 minutes)

### Coverage Requirements

- ✅ Backend: >= 80% coverage
- ✅ Frontend: >= 80% coverage
- ✅ Deployment blocked if coverage below threshold

---

## Troubleshooting

### Tests Failing Locally But Pass in CI

**Check:**
- Environment variables
- Test data dependencies
- Infrastructure services

**Fix:**
```bash
# Use same environment as CI
export TEST_BACKEND_URL=http://localhost:8000
export TEST_FRONTEND_URL=http://localhost:3000

# Start infrastructure
docker-compose -f tests/docker-compose.test.yml up -d
```

### Tests Too Slow

**Optimize:**
- Use mocks for slow operations
- Run tests in parallel
- Use test markers to skip slow tests

```bash
# Run fast tests only
pytest -m "not slow" -v
```

### Coverage Below Threshold

**Improve:**
- Add tests for uncovered code
- Remove dead code
- Review coverage report

```bash
# Generate coverage report
pytest --cov=../symphainy-platform --cov-report=html
open htmlcov/index.html
```

---

## Summary

**Process:**
1. ✅ Write unit tests first (TDD)
2. ✅ Write integration tests
3. ✅ Write E2E tests (if critical)
4. ✅ Ensure >= 80% coverage
5. ✅ All tests pass locally
6. ✅ Push to trigger CI/CD

**Result:**
- ✅ High-quality code
- ✅ Confident deployments
- ✅ Fewer production bugs

---

**Questions?** Contact the testing team or refer to the CI/CD how-to guide.


