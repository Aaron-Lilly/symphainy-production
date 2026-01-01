# 🧪 SymphAIny Platform Test Suite

**Updated for New Architecture:** Mixin-based base classes, 5 foundation layers, 9 Smart City services

---

## 📋 Quick Start

### Run All Tests
```bash
cd /home/founders/demoversion/symphainy_source/tests
python3 run_tests.py --all
```

### Run Specific Test Categories
```bash
# Unit tests only (fast)
python3 run_tests.py --unit

# Foundation layer tests
python3 run_tests.py --foundations

# Smart City service tests
python3 run_tests.py --smart-city

# Integration tests
python3 run_tests.py --integration

# End-to-end tests
python3 run_tests.py --e2e
```

### Run Fast Tests Only
```bash
python3 run_tests.py --fast
```

### Run with Coverage
```bash
python3 run_tests.py --all --coverage
```

### Run Only Failed Tests
```bash
python3 run_tests.py --failed
```

---

## 📁 Test Structure

```
tests/
├── conftest.py                    # Pytest configuration & fixtures
├── pytest.ini                     # Pytest settings
├── run_tests.py                   # Test runner script
├── README.md                      # This file
│
├── unit/                          # Unit tests (fast, isolated)
│   ├── foundations/               # Foundation layer unit tests
│   │   ├── test_di_container.py
│   │   ├── test_public_works_foundation.py
│   │   ├── test_curator_foundation.py
│   │   ├── test_communication_foundation.py
│   │   └── test_agentic_foundation.py
│   │
│   ├── smart_city/                # Smart City service unit tests
│   │   ├── test_librarian_service.py
│   │   ├── test_data_steward_service.py
│   │   ├── test_security_guard_service.py
│   │   ├── test_conductor_service.py
│   │   ├── test_post_office_service.py
│   │   ├── test_traffic_cop_service.py
│   │   ├── test_nurse_service.py
│   │   ├── test_content_steward_service.py
│   │   └── test_city_manager_service.py
│   │
│   ├── mcp_servers/               # MCP server unit tests
│   │   └── test_mcp_server_base.py
│   │
│   └── bases/                     # Base class unit tests
│       ├── test_smart_city_role_base.py
│       ├── test_realm_service_base.py
│       └── test_manager_service_base.py
│
├── integration/                   # Integration tests (slower)
│   ├── test_foundation_integration.py
│   ├── test_smart_city_integration.py
│   └── test_mcp_integration.py
│
└── e2e/                          # End-to-end tests (slowest)
    ├── test_platform_startup.py
    └── test_full_workflow.py
```

---

## 🎯 Test Categories (Markers)

### By Test Type
- `unit` - Fast, isolated unit tests
- `integration` - Integration tests (requires multiple components)
- `e2e` - End-to-end tests (requires full platform)

### By Component
- `foundations` - Foundation layer tests
- `smart_city` - Smart City service tests
- `mcp` - MCP server tests
- `bases` - Base class tests

### By Speed
- `fast` - Fast tests (< 1 second)
- `slow` - Slow tests (> 1 second)

### Special
- `security` - Security-related tests
- `performance` - Performance tests

---

## 🔧 Test Fixtures

### DI Container Fixtures
```python
@pytest.fixture
def mock_di_container():
    """Mock DI container for unit tests."""

@pytest.fixture
async def real_di_container():
    """Real DI container for integration tests."""
```

### Foundation Fixtures
```python
@pytest.fixture
def mock_public_works_foundation():
    """Mock Public Works Foundation."""

@pytest.fixture
async def real_public_works_foundation(real_di_container):
    """Real Public Works Foundation."""

# Similar for: communication_foundation, curator_foundation, agentic_foundation
```

### Smart City Service Fixtures
```python
@pytest.fixture
async def librarian_service(mock_di_container):
    """Librarian Service instance."""

# Similar for all 9 Smart City services
```

### Test Data Fixtures
```python
@pytest.fixture
def sample_user_context():
    """Sample user context for testing."""

@pytest.fixture
def sample_file_data():
    """Sample file data for testing."""

@pytest.fixture
def sample_knowledge_item():
    """Sample knowledge item for testing."""
```

---

## 🚀 Running Tests

### Prerequisites

```bash
# Install test dependencies
cd /home/founders/demoversion/symphainy_source/tests
pip install -r requirements.txt

# Or install from platform requirements
cd ../symphainy-platform
pip install -r requirements.txt
```

### Command Line (Direct pytest)

```bash
# All tests
pytest

# Specific test file
pytest unit/foundations/test_di_container.py

# Specific test function
pytest unit/foundations/test_di_container.py::TestDIContainerService::test_di_container_initialization

# By marker
pytest -m "unit"
pytest -m "foundations and fast"
pytest -m "smart_city and not slow"

# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last failed tests only
pytest --lf

# With coverage
pytest --cov=symphainy-platform --cov-report=html
```

### Using Test Runner Script

```bash
# Recommended approach
python3 run_tests.py --all --verbose

# Quick smoke test (fast tests only)
python3 run_tests.py --fast

# After fixing issues (rerun failures)
python3 run_tests.py --failed
```

---

## 📊 Expected Test Results (Current State)

Based on Production Readiness Assessment:

### ✅ Should Pass
- DI Container tests
- Public Works Foundation tests (mostly)
- Librarian Service tests
- Data Steward Service tests
- Content Steward Service tests
- Base class import tests

### ⚠️ Known Issues (Will Fail Until Fixed)
- **Import Error:** Nurse Service (`MetricData` import)
- **Empty Implementations:** Security Guard modules return `{}`
- **MCP TODOs:** MCP base class TODO items
- **Full Startup:** E2E tests (missing configuration)

### 🎯 Fix Priority (from Production Readiness Assessment)
1. Fix `MetricData` import (1 hour)
2. Add `.env.secrets` configuration (1 hour)
3. Complete Security Guard implementations (1-2 days)
4. Complete MCP infrastructure TODOs (1 day)

---

## 🔍 Test Development Guidelines

### Writing Unit Tests

```python
import pytest

pytestmark = [pytest.mark.unit, pytest.mark.fast]

class TestMyService:
    """Test My Service functionality."""
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_di_container):
        """Test service can be initialized."""
        from my_module import MyService
        service = MyService(mock_di_container)
        await service.initialize()
        
        assert service.is_initialized
        assert service.service_health == "healthy"
    
    @pytest.mark.asyncio
    async def test_service_method(self, my_service, sample_data):
        """Test service method."""
        result = await my_service.do_something(sample_data)
        
        assert result is not None
        assert result["status"] == "success"
```

### Writing Integration Tests

```python
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.slow]

class TestServiceIntegration:
    """Test service integration."""
    
    @pytest.mark.asyncio
    async def test_services_interact(self, service_a, service_b):
        """Test services can interact."""
        # Service A calls Service B
        result_a = await service_a.call_service_b(data)
        
        # Service B should have processed it
        result_b = await service_b.get_result()
        
        assert result_a["status"] == "sent"
        assert result_b["status"] == "processed"
```

---

## 🎓 Common Patterns

### Testing Async Methods
```python
@pytest.mark.asyncio
async def test_async_method(self, service):
    result = await service.async_method()
    assert result is not None
```

### Testing Exceptions
```python
def test_raises_error(self, service):
    with pytest.raises(ValueError):
        service.invalid_operation()
```

### Skipping Tests
```python
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature(self):
    pass

# Or conditional skip
@pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
def test_redis_feature(self):
    pass
```

### Parametrized Tests
```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
])
def test_uppercase(self, input, expected):
    assert input.upper() == expected
```

---

## 📈 Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=symphainy-platform --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## 🐛 Debugging Tests

### Run with PDB
```bash
pytest --pdb  # Drop into debugger on failure
pytest --pdb-trace  # Drop into debugger at start
```

### Verbose Output
```bash
pytest -vv  # Very verbose
pytest -s   # Show print statements
pytest --tb=long  # Long traceback format
```

### Specific Test with Output
```bash
pytest -v -s unit/foundations/test_di_container.py::TestDIContainerService::test_di_container_initialization
```

---

## ✅ Pre-Commit Test Strategy

Before committing code:

1. **Quick Smoke Test** (< 30 seconds)
   ```bash
   python3 run_tests.py --fast
   ```

2. **Component Tests** (< 2 minutes)
   ```bash
   python3 run_tests.py --unit --foundations
   ```

3. **Full Unit Test Suite** (< 5 minutes)
   ```bash
   python3 run_tests.py --unit
   ```

Before pushing:

4. **Full Test Suite** (< 15 minutes)
   ```bash
   python3 run_tests.py --all
   ```

---

## 🚦 CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd tests
          python3 run_tests.py --all --coverage
```

---

## 📞 Need Help?

- Check test output for detailed error messages
- Review fixtures in `conftest.py`
- Check Production Readiness Assessment for known issues
- Run `python3 run_tests.py --markers` to see all available markers













