# Running Tests - Quick Start Guide

**For:** Test execution team  
**Purpose:** Guide for running and updating tests in parallel with CI/CD integration

---

## 🚀 Quick Start

### Prerequisites
```bash
# Install test dependencies
cd /home/founders/demoversion/symphainy_source/tests
pip3 install -r requirements.txt
```

### Environment Setup
```bash
# Set up test environment
export TEST_USE_REAL_INFRASTRUCTURE=true
export TEST_API_URL=http://localhost  # Or your test API URL
export TEST_SUPABASE_URL=your_test_supabase_url
export TEST_SUPABASE_ANON_KEY=your_test_supabase_anon_key
```

---

## 📋 Running Tests

### Run All Tests
```bash
cd /home/founders/demoversion/symphainy_source/tests
pytest tests/ -v
```

### Run by Category
```bash
# Unit tests (fast)
pytest tests/unit/ -v -m unit

# Integration tests (medium)
pytest tests/integration/ -v -m integration

# E2E tests (slow)
pytest tests/e2e/ -v -m e2e
```

### Run Specific Test Files
```bash
# Platform startup tests
pytest tests/e2e/production/smoke_tests/test_platform_startup_e2e.py -v

# Content pillar tests
pytest tests/e2e/production/pillar_validation/test_content_pillar_e2e.py -v

# Cross-pillar workflow tests
pytest tests/e2e/production/cross_pillar/test_complete_user_journey_e2e.py -v
```

### Run with Markers
```bash
# Critical tests only
pytest tests/ -v -m critical

# Fast tests only
pytest tests/ -v -m fast

# Production readiness tests
pytest tests/ -v -m production_readiness
```

---

## 🔧 Test Configuration

### Using Real Infrastructure (Default)
```bash
export TEST_USE_REAL_INFRASTRUCTURE=true
pytest tests/ -v
```

### Using Mocks (Faster, No API Costs)
```bash
export TEST_USE_REAL_INFRASTRUCTURE=false
pytest tests/ -v
```

### Test Environment Variables
See `config/test_config.py` for all available configuration options.

---

## 📝 Updating Tests

### Test File Structure
```
tests/
├── unit/              # Unit tests (fast, isolated)
├── integration/       # Integration tests (service interactions)
├── e2e/              # E2E tests (full platform)
├── config/           # Test configuration
├── utils/            # Test utilities
└── fixtures/         # Test fixtures
```

### Adding New Tests
1. **Choose the right category:**
   - Unit tests: Fast, isolated, mocked dependencies
   - Integration tests: Service interactions, real infrastructure
   - E2E tests: Full platform, complete user journeys

2. **Follow existing patterns:**
   - Use `@pytest.mark.asyncio` for async tests
   - Use `skip_if_missing_real_infrastructure()` for infrastructure-dependent tests
   - Use appropriate markers (`@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`)

3. **Example test structure:**
```python
import pytest
from utils.real_infrastructure_helpers import skip_if_missing_real_infrastructure

@pytest.mark.e2e
@pytest.mark.critical
class TestMyFeature:
    @pytest.mark.asyncio
    async def test_my_feature(self, api_base_url, session_token):
        skip_if_missing_real_infrastructure(["supabase"])
        # Test implementation
        assert True
```

### Fixing Failing Tests
1. **Identify the issue:**
   - Check test output for error messages
   - Verify environment variables are set correctly
   - Check if infrastructure is available

2. **Update test:**
   - Fix test logic if incorrect
   - Update assertions if API responses changed
   - Add proper error handling

3. **Document changes:**
   - Add comments explaining fixes
   - Update test documentation if needed

---

## 🐛 Troubleshooting

### Import Errors
```bash
# Ensure pytest.ini pythonpath is correct
# Run from tests directory
cd /home/founders/demoversion/symphainy_source/tests
pytest tests/ -v
```

### Infrastructure Not Available
```bash
# Tests will skip gracefully if infrastructure unavailable
# Check TEST_USE_REAL_INFRASTRUCTURE environment variable
export TEST_USE_REAL_INFRASTRUCTURE=false  # Use mocks instead
```

### Authentication Issues
```bash
# Ensure Supabase credentials are set
export TEST_SUPABASE_URL=your_url
export TEST_SUPABASE_ANON_KEY=your_key
```

---

## 📊 Test Results

### Viewing Test Results
```bash
# Verbose output
pytest tests/ -v

# With coverage
pytest tests/ --cov --cov-report=html

# HTML report
pytest tests/ --html=report.html
```

### Test Markers Reference
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - E2E tests
- `@pytest.mark.critical` - Critical tests
- `@pytest.mark.slow` - Slow tests
- `@pytest.mark.production_readiness` - Production readiness tests

---

## 🔄 Integration with CI/CD

**Note:** CI/CD integration is being developed in parallel. Test updates will be automatically integrated into CI/CD pipeline once complete.

**Process:**
1. Run tests locally
2. Update tests as needed
3. Commit test updates
4. CI/CD will automatically run updated tests

---

## 📚 Additional Resources

- **Test Strategy:** `docs/TESTING_STRATEGY_OVERHAUL_PLAN.md`
- **Test Configuration:** `tests/config/test_config.py`
- **Test Utilities:** `tests/utils/`
- **Real Infrastructure Helpers:** `tests/utils/real_infrastructure_helpers.py`

---

**Last Updated:** January 2025  
**For Questions:** See test documentation or contact development team



