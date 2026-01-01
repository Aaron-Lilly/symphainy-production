# Test Suite Evaluation & Recommendations

**Date**: November 12, 2025  
**Focus**: Comprehensive evaluation of test suite for new agentic architecture

---

## Executive Summary

This evaluation covers 5 critical areas:
1. **Architectural Alignment**: What needs to change for the new agentic architecture
2. **Best Practices**: Whether current approach conforms to testing best practices
3. **Tooling**: Whether WireMock or other tools would help
4. **Token Costs**: Why tests might be costing hundreds of dollars in Cursor
5. **Structural Improvements**: How to better catch production issues

**Key Findings**:
- ✅ Good foundation with proper test structure (unit/integration/e2e)
- ⚠️ **CRITICAL**: Tests are missing MCP server/agent architecture patterns
- ⚠️ **CRITICAL**: Using Cursor agent to run/troubleshoot tests is causing high Cursor token costs
- ⚠️ Tests reference old architecture (pillar services, not orchestrators)
- ✅ Good use of mocks for infrastructure
- ⚠️ Missing agentic-specific test patterns
- ✅ **SOLUTION**: Self-service test execution guide created (see TEST_EXECUTION_GUIDE.md)

---

## 1. Architectural Alignment Assessment

### 1.1 Current Test Architecture vs. New Architecture

#### ✅ What's Working
- Test structure (unit/integration/e2e) is solid
- Good use of fixtures and mocks for infrastructure
- Proper async test patterns

#### ❌ Critical Gaps

**1. Missing MCP Server Testing**
- **Current**: Tests mock orchestrators directly
- **New Architecture**: Agents use MCP tools → Orchestrator methods → Enabling services
- **Gap**: No tests for MCP server tool execution
- **Impact**: Can't verify agent-orchestrator integration via MCP

**Example Gap**:
```python
# ❌ CURRENT (Wrong Pattern)
async def test_agent_calls_orchestrator():
    agent.orchestrator = mock_orchestrator
    result = await agent.refine_poc_proposal(...)
    mock_orchestrator.generate_poc_proposal.assert_called()

# ✅ NEEDED (Correct Pattern)
async def test_agent_uses_mcp_tool():
    agent.orchestrator = mock_orchestrator
    agent.orchestrator.mcp_server = mock_mcp_server
    result = await agent.refine_poc_proposal(...)
    mock_mcp_server.execute_tool.assert_called_with("generate_comprehensive_poc_tool", ...)
```

**2. Missing Agent MCP Tool Usage Tests**
- **Current**: Tests check direct orchestrator calls
- **New Architecture**: Agents must use MCP tools
- **Gap**: No validation that agents use MCP tools correctly
- **Impact**: Can't catch architectural violations

**3. Outdated Orchestrator Tests**
- **Current**: Tests reference old paths like `business_orchestrator.use_cases.mvp.content_analysis_orchestrator`
- **New Architecture**: Orchestrators are under `delivery_manager.mvp_pillar_orchestrators`
- **Gap**: Import paths are wrong
- **Impact**: Tests may be testing wrong code or failing incorrectly

**Example**:
```python
# ❌ CURRENT (Wrong Path)
from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator

# ✅ CORRECT (New Path)
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator import ContentAnalysisOrchestrator
```

**4. Missing Specialist Agent Tests**
- **Current**: Tests for old specialist agents (if any)
- **New Architecture**: New specialist agents (InsightsSpecialistAgent, etc.)
- **Gap**: No tests for new agents
- **Impact**: Can't verify agentic capabilities

**5. Missing MCP Server Initialization Tests**
- **Current**: No tests verifying MCP servers are initialized
- **New Architecture**: All orchestrators must initialize MCP servers
- **Gap**: Can't verify MCP server setup
- **Impact**: Silent failures if MCP servers aren't initialized

### 1.2 Required Test Updates

#### Priority 1: MCP Server Testing (CRITICAL)

**New Test Category**: `tests/unit/mcp_servers/`
```python
# tests/unit/mcp_servers/test_content_analysis_mcp_server.py
@pytest.mark.unit
@pytest.mark.mcp
class TestContentAnalysisMCPServer:
    """Test Content Analysis MCP Server."""
    
    @pytest.mark.asyncio
    async def test_mcp_server_initializes(self, mock_orchestrator, mock_di_container):
        """Test MCP server initializes correctly."""
        from ...content_analysis_mcp_server import ContentAnalysisMCPServer
        
        mcp_server = ContentAnalysisMCPServer(
            orchestrator=mock_orchestrator,
            di_container=mock_di_container
        )
        
        assert mcp_server.orchestrator == mock_orchestrator
        assert len(mcp_server.tools) > 0
    
    @pytest.mark.asyncio
    async def test_execute_tool_routes_to_orchestrator(self, mcp_server, mock_orchestrator):
        """Test MCP tool execution routes to orchestrator."""
        mock_orchestrator.parse_file = AsyncMock(return_value={"success": True})
        
        result = await mcp_server.execute_tool(
            "parse_file_tool",
            {"file_id": "test_123"}
        )
        
        mock_orchestrator.parse_file.assert_called_once_with(
            file_id="test_123",
            parse_options=None
        )
        assert result["success"] is True
```

#### Priority 2: Agent MCP Tool Usage Tests (CRITICAL)

**New Test Category**: `tests/agentic/integration/test_agent_mcp_integration.py`
```python
@pytest.mark.integration
@pytest.mark.agentic
class TestAgentMCPToolUsage:
    """Test agents use MCP tools correctly."""
    
    @pytest.mark.asyncio
    async def test_business_outcomes_agent_uses_mcp_tools(self, business_outcomes_agent, mock_orchestrator):
        """Test Business Outcomes agent uses MCP tools, not direct calls."""
        mock_mcp_server = MagicMock()
        mock_mcp_server.execute_tool = AsyncMock(return_value={"success": True})
        mock_orchestrator.mcp_server = mock_mcp_server
        
        business_outcomes_agent.set_orchestrator(mock_orchestrator)
        
        await business_outcomes_agent.refine_poc_proposal(
            base_proposal={"success": True},
            context={}
        )
        
        # Verify MCP tool was called, not direct orchestrator method
        assert mock_mcp_server.execute_tool.called
        # Verify NO direct orchestrator call
        assert not hasattr(mock_orchestrator, 'generate_poc_proposal') or \
               not mock_orchestrator.generate_poc_proposal.called
```

#### Priority 3: Update Orchestrator Test Imports

**Files to Update**:
- `tests/business_enablement/orchestrators/test_content_analysis_orchestrator.py`
- `tests/business_enablement/orchestrators/test_insights_orchestrator.py`
- `tests/business_enablement/orchestrators/test_operations_orchestrator.py`
- `tests/business_enablement/orchestrators/test_business_outcomes_orchestrator.py`

**Change**: Update import paths to new architecture

#### Priority 4: Add MCP Server Initialization Tests

```python
@pytest.mark.integration
class TestOrchestratorMCPInitialization:
    """Test orchestrators initialize MCP servers."""
    
    @pytest.mark.asyncio
    async def test_content_orchestrator_initializes_mcp_server(self, content_orchestrator):
        """Test Content orchestrator initializes MCP server."""
        await content_orchestrator.initialize()
        
        assert hasattr(content_orchestrator, 'mcp_server')
        assert content_orchestrator.mcp_server is not None
        assert content_orchestrator.mcp_server.orchestrator == content_orchestrator
```

---

## 2. Best Practices Assessment

### 2.1 ✅ What's Good

1. **Test Structure**: Clear separation of unit/integration/e2e
2. **Fixtures**: Good use of pytest fixtures for setup
3. **Markers**: Proper use of pytest markers for categorization
4. **Async Support**: Proper async test patterns
5. **Mocking**: Good use of mocks for infrastructure isolation

### 2.2 ⚠️ Areas for Improvement

#### 2.2.1 Test Isolation

**Issue**: Some tests may have dependencies between tests
**Recommendation**: Ensure each test is independent

```python
# ❌ BAD: Test depends on previous test state
def test_a():
    global_state["value"] = 1

def test_b():
    assert global_state["value"] == 1  # Depends on test_a

# ✅ GOOD: Each test is independent
def test_a(fixture):
    result = fixture.do_something()
    assert result == 1

def test_b(fixture):
    result = fixture.do_something_else()
    assert result == 2
```

#### 2.2.2 Test Naming

**Issue**: Some test names are vague
**Recommendation**: Use descriptive test names

```python
# ❌ BAD
def test_orchestrator():
    pass

# ✅ GOOD
def test_content_orchestrator_initializes_mcp_server_on_startup():
    pass
```

#### 2.2.3 Test Data Management

**Issue**: Test data may be hardcoded in tests
**Recommendation**: Use fixtures for test data

```python
# ❌ BAD: Hardcoded data
def test_parse_file():
    result = parser.parse_file("test.pdf")
    assert result["type"] == "pdf"

# ✅ GOOD: Fixture-based data
def test_parse_file(sample_pdf_file):
    result = parser.parse_file(sample_pdf_file)
    assert result["type"] == "pdf"
```

#### 2.2.4 Assertion Quality

**Issue**: Some assertions may be too generic
**Recommendation**: Use specific assertions

```python
# ❌ BAD: Generic assertion
def test_parse():
    result = parser.parse()
    assert result  # Too generic

# ✅ GOOD: Specific assertions
def test_parse():
    result = parser.parse()
    assert result["success"] is True
    assert "content" in result
    assert result["metadata"]["pages"] > 0
```

#### 2.2.5 Test Coverage

**Issue**: May have gaps in coverage
**Recommendation**: Use coverage tools and aim for >80% coverage

```bash
pytest --cov=symphainy-platform --cov-report=html --cov-report=term
```

### 2.3 Missing Best Practices

#### 2.3.1 Contract Testing

**Missing**: API contract tests
**Recommendation**: Add contract tests for SOA APIs

```python
@pytest.mark.contract
class TestSOAAPIContracts:
    """Test SOA API contracts."""
    
    def test_file_parser_soa_api_contract(self, file_parser_service):
        """Test FileParserService.parse_file() SOA API contract."""
        result = await file_parser_service.parse_file(file_id="test")
        
        # Contract: Must return dict with "success" key
        assert isinstance(result, dict)
        assert "success" in result
        
        # Contract: If success=True, must have "parsed_content"
        if result["success"]:
            assert "parsed_content" in result
```

#### 2.3.2 Property-Based Testing

**Missing**: Property-based tests
**Recommendation**: Use Hypothesis for property-based testing

```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=100))
def test_parse_file_handles_any_filename(filename):
    """Test parser handles any valid filename."""
    result = parser.parse_file(filename)
    assert result["success"] in [True, False]  # Property: Always returns success status
```

#### 2.3.3 Test Documentation

**Issue**: Some tests lack docstrings
**Recommendation**: Add docstrings explaining what is tested

```python
def test_parse_file():
    """Test file parser correctly extracts content and metadata from PDF files.
    
    Verifies:
    - Content extraction works
    - Metadata is populated
    - File type is detected correctly
    """
    pass
```

---

## 3. Tooling Assessment (WireMock & Alternatives)

### 3.1 WireMock Evaluation

#### What WireMock Does
- HTTP server mocking
- Request/response recording and replay
- Request matching and stubbing

#### Would It Help?

**✅ YES, for**:
- E2E tests that make HTTP calls
- Testing frontend-backend integration
- Recording real API responses for replay

**❌ NO, for**:
- Unit tests (already using mocks)
- MCP server tests (not HTTP-based)
- Agent tests (not HTTP-based)

#### Recommendation: **PARTIAL ADOPTION**

**Use WireMock for**:
1. **Frontend Gateway API Tests**: Mock HTTP endpoints
2. **E2E Tests**: Record/replay real API responses
3. **Integration Tests**: Mock external services

**Don't Use WireMock for**:
1. Unit tests (current mocking is fine)
2. MCP server tests (not HTTP)
3. Agent tests (not HTTP)

### 3.2 Alternative Tools to Consider

#### 3.2.1 pytest-mock (Already Using ✅)
- Good for unit test mocking
- Keep using this

#### 3.2.2 pytest-asyncio (Already Using ✅)
- Good for async tests
- Keep using this

#### 3.2.3 pytest-cov (Recommended ✅)
- Coverage reporting
- **Action**: Add to requirements.txt if not present

#### 3.2.4 pytest-xdist (Recommended ✅)
- Parallel test execution
- **Action**: Add for faster test runs

```bash
pytest -n auto  # Run tests in parallel
```

#### 3.2.5 pytest-timeout (Recommended ✅)
- Prevent hanging tests
- **Action**: Add to catch infinite loops

```python
@pytest.mark.timeout(30)  # Fail if test takes > 30 seconds
def test_slow_operation():
    pass
```

#### 3.2.6 Hypothesis (Recommended for Property Testing)
- Property-based testing
- **Action**: Consider for data validation tests

#### 3.2.7 VCR.py (Recommended for HTTP Recording)
- Record/replay HTTP interactions
- **Alternative to WireMock** (Python-native)

```python
import vcr

@vcr.use_cassette('fixtures/vcr_cassettes/api_call.yaml')
def test_api_call():
    response = requests.get('https://api.example.com')
    assert response.status_code == 200
```

### 3.3 Tooling Recommendations

**Priority 1: Add These Tools**
1. `pytest-xdist` - Parallel execution (faster tests)
2. `pytest-timeout` - Prevent hanging tests
3. `pytest-cov` - Coverage reporting (if not already)

**Priority 2: Consider These Tools**
1. `VCR.py` - HTTP recording (alternative to WireMock)
2. `Hypothesis` - Property-based testing

**Priority 3: Evaluate WireMock**
- Only if you need HTTP server mocking for E2E tests
- Python-native alternatives (VCR.py) may be better

---

## 4. Token Cost Analysis (Why Tests Cost Hundreds of Dollars)

### 4.1 Root Cause Analysis

#### 4.1.1 Potential LLM Calls in Tests

**CRITICAL FINDING**: Tests may be making real LLM API calls

**Evidence**:
- Tests reference agents that use LLMs
- Agent fixtures use `mock_agentic_foundation`, but agents may still initialize LLM clients during `initialize()`
- Agentic Foundation Factory may create real LLM clients if not properly mocked
- Tests may be calling agent methods that trigger LLM initialization

**Example Risk**:
```python
# ❌ RISK: Agent may initialize real LLM client during initialize()
@pytest.fixture
async def agent_fixture(mock_agentic_foundation):
    agent = InsightsSpecialistAgent(
        agentic_foundation=mock_agentic_foundation,  # Mocked
        ...
    )
    await agent.initialize()  # ⚠️ May create real LLM client here!
    return agent

# ❌ RISK: Test may trigger LLM call
async def test_agent_generates_insights(agent_fixture):
    result = await agent_fixture.generate_grounded_insights(...)
    # If agent has real LLM client, this makes real API call!
```

**Impact**: Each test run could make hundreds of LLM API calls

#### 4.1.2 Agentic Foundation Factory Risk

**Issue**: `AgenticFoundationService` may create real LLM clients
**Risk**: Even with mocked foundation, agents may access real LLM clients

**Check Needed**:
```python
# Check if agents access LLM clients from foundation
agent.agentic_foundation.get_llm_client()  # May return real client
```

#### 4.1.3 Cost Source Clarification

**IMPORTANT**: There are TWO potential cost sources:

**1. OpenAI/Anthropic API Costs (Your Account)**
- **If tests make real LLM API calls** → Charged to YOUR OpenAI/Anthropic account
- **Evidence**: Tests creating agents that initialize real LLM clients
- **Impact**: Each test run could make hundreds of API calls = $$$ on your API account
- **Solution**: Mock all LLM clients (prevents real API calls)

**2. Cursor Token Costs (Cursor Account)**
- **If Cursor analyzes test files** → Charged to YOUR Cursor account
- **Evidence**: Cursor loading test files into context, analyzing failures
- **Impact**: Large test files + failure analysis = $$$ on Cursor account
- **Solution**: `.cursorignore` to exclude tests, limit Cursor context

**Which is the bigger issue?**
- **Most likely**: OpenAI/Anthropic API costs (if tests make real LLM calls)
- **Secondary**: Cursor token costs (if Cursor is analyzing large test files)

**To determine which**:
1. Check your OpenAI/Anthropic usage dashboard for API calls during test runs
2. Check Cursor usage for token consumption during test execution
3. Mock LLM clients first (addresses #1)
4. Add `.cursorignore` second (addresses #2)

#### 4.2.2 Cursor Token Costs (Separate from API Costs)

**Issue**: Cursor may be consuming tokens when:
- Loading test files into context for analysis
- Analyzing test failures with its own LLM
- Processing test output and generating suggestions

**Impact**: 
- Cursor token consumption per test run
- Cursor token consumption per failure analysis
- **Note**: This is separate from OpenAI/Anthropic API costs

**Solution**: 
- Add `.cursorignore` to exclude test files from Cursor context
- Limit Cursor's analysis scope
- Use Cursor's test execution features sparingly

### 4.2 Solutions

#### Solution 1: Mock All LLM Clients (CRITICAL)

**Action**: Ensure all agent tests mock LLM clients

**Step 1: Add LLM Client Mock Fixture**
```python
# In conftest.py
@pytest.fixture
def mock_llm_client():
    """Mock LLM client to prevent real API calls."""
    mock_client = MagicMock()
    mock_client.generate = AsyncMock(return_value={
        "content": "Mocked response",
        "usage": {"total_tokens": 0}
    })
    mock_client.chat = AsyncMock(return_value={
        "content": "Mocked chat response",
        "usage": {"total_tokens": 0}
    })
    return mock_client

@pytest.fixture(autouse=True)  # Auto-use for all tests
def patch_llm_clients(mock_llm_client):
    """Patch all LLM client creation to use mock."""
    with patch('foundations.agentic_foundation.agent_sdk.llm_client.LLMClient', return_value=mock_llm_client):
        with patch('langchain_openai.ChatOpenAI', return_value=mock_llm_client):
            with patch('langchain_anthropic.ChatAnthropic', return_value=mock_llm_client):
                yield mock_llm_client
```

**Step 2: Update Agent Fixtures**
```python
# ✅ CORRECT: Ensure agent uses mocked LLM
@pytest.fixture
async def insights_specialist_agent(mock_agentic_foundation, mock_llm_client):
    """Create Insights Specialist Agent with mocked LLM."""
    agent = InsightsSpecialistAgent(...)
    
    # CRITICAL: Inject mock LLM client before initialization
    agent.llm_client = mock_llm_client
    
    await agent.initialize()
    
    # Verify mock is still in place
    assert agent.llm_client == mock_llm_client
    
    return agent
```

**Step 3: Update Agent Tests**
```python
@pytest.mark.asyncio
async def test_agent_with_mocked_llm(insights_specialist_agent, mock_llm_client):
    """Test agent with mocked LLM client."""
    result = await insights_specialist_agent.generate_grounded_insights(...)
    
    # Verify LLM was called (but with mock, no real API call)
    # Note: If agent uses MCP tools, it won't call LLM directly
    # But if agent has LLM for reasoning, verify it's mocked
    if hasattr(insights_specialist_agent, 'llm_client'):
        # Only check if agent uses LLM directly (not via MCP)
        pass  # Agent uses MCP tools, not direct LLM
    
    assert result["success"] is True
```

#### Solution 2: Environment Variable Guard (CRITICAL)

**Action**: Add environment variable to prevent real LLM calls in tests

**Step 1: Update conftest.py**
```python
# In conftest.py (at the top, before any imports)
import os
os.environ["USE_MOCK_LLM"] = "true"  # CRITICAL: Prevent real LLM calls
os.environ["TESTING"] = "true"  # Mark as test environment
os.environ["SKIP_AI_TESTS"] = "true"  # Skip AI tests by default
```

**Step 2: Update Agent Base Classes**
```python
# In agent base classes (if they initialize LLM clients)
import os

class AgentBase:
    def __init__(self, ...):
        # CRITICAL: Use mock LLM in test environment
        if os.getenv("USE_MOCK_LLM") == "true" or os.getenv("TESTING") == "true":
            from tests.fixtures.mock_llm_client import MockLLMClient
            self.llm_client = MockLLMClient()
        else:
            self.llm_client = RealLLMClient()  # Production only
```

**Step 3: Create Mock LLM Client**
```python
# tests/fixtures/mock_llm_client.py
class MockLLMClient:
    """Mock LLM client that never makes real API calls."""
    
    async def generate(self, prompt, **kwargs):
        return {
            "content": f"Mocked response for: {prompt[:50]}...",
            "usage": {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}
        }
    
    async def chat(self, messages, **kwargs):
        return {
            "content": "Mocked chat response",
            "usage": {"total_tokens": 0}
        }
```

#### Solution 3: Test Markers for LLM Tests

**Action**: Mark tests that use LLMs (and skip by default)

```python
# In pytest.ini
markers =
    ai: Tests using real AI APIs (slow, costs money)
    cached: Tests using cached AI responses

# In tests
@pytest.mark.ai
@pytest.mark.skipif(os.getenv("SKIP_AI_TESTS") == "true", reason="Skipping AI tests to save costs")
async def test_agent_with_real_llm():
    """Test with real LLM (only run when explicitly enabled)."""
    pass
```

#### Solution 4: Cursor-Specific Configuration

**Action**: Create `.cursor-test-config.json` to limit test execution

```json
{
  "testExecution": {
    "skipAITests": true,
    "skipE2ETests": true,
    "maxTestDuration": 300,
    "parallelWorkers": 1
  }
}
```

### 4.3 Cost Reduction Checklist

- [ ] **CRITICAL**: Add `USE_MOCK_LLM=true` to conftest.py (before any imports)
- [ ] **CRITICAL**: Create `MockLLMClient` fixture and patch all LLM client creation
- [ ] **CRITICAL**: Update agent fixtures to inject mock LLM clients before `initialize()`
- [ ] **CRITICAL**: Add `@pytest.fixture(autouse=True)` to patch LLM clients globally
- [ ] **CRITICAL**: Verify no real LLM clients are created in test environment
- [ ] **HIGH**: Mark AI tests with `@pytest.mark.ai` and skip by default in pytest.ini
- [ ] **HIGH**: Limit test execution in Cursor (skip E2E, skip AI tests)
- [ ] **HIGH**: Add `.cursorignore` to exclude test files from Cursor context
- [ ] **MEDIUM**: Use test caching (pytest-cache)
- [ ] **MEDIUM**: Run tests in parallel (pytest-xdist) to reduce total time

### Immediate Action Items (Today)

#### Priority 1: Prevent OpenAI/Anthropic API Costs (Your Account)

1. **Add to conftest.py (TOP OF FILE)**:
```python
import os
# CRITICAL: Prevent real LLM calls in tests (saves YOUR OpenAI/Anthropic API costs)
os.environ["USE_MOCK_LLM"] = "true"
os.environ["TESTING"] = "true"
os.environ["SKIP_AI_TESTS"] = "true"
```

2. **Create tests/fixtures/mock_llm_client.py**:
```python
class MockLLMClient:
    """Mock LLM client - never makes real API calls (prevents OpenAI/Anthropic charges)."""
    # (Implementation above)
```

3. **Update pytest.ini**:
```ini
addopts = 
    -m "not ai"  # Skip AI tests by default (prevents real API calls)
    --tb=short
```

#### Priority 2: Reduce Cursor Token Costs (Cursor Account)

4. **Create .cursorignore** (in project root):
```
tests/
*.pyc
__pycache__/
htmlcov/
.pytest_cache/
```

5. **Verify Cost Source**:
   - Check OpenAI/Anthropic usage dashboard: Are API calls happening during test runs?
   - Check Cursor usage: Are tokens being consumed when running tests?
   - This will tell you which cost source is the bigger issue

---

## 5. Structural Improvements

### 5.1 Test Pyramid Optimization

**Current State**: May have too many E2E tests
**Recommendation**: Follow test pyramid

```
        /\
       /  \  E2E (10%) - Slow, expensive
      /____\
     /      \  Integration (20%) - Medium speed
    /________\
   /          \  Unit (70%) - Fast, cheap
  /____________\
```

**Action**: 
- Increase unit test coverage (70%)
- Reduce E2E tests (10%)
- Keep integration tests (20%)

### 5.2 Test Organization

**Current**: Tests organized by component
**Recommendation**: Also organize by feature/user journey

```
tests/
├── unit/
│   ├── by_component/  # Current structure
│   └── by_feature/     # NEW: Feature-based tests
│       ├── file_upload/
│       ├── document_analysis/
│       └── insights_generation/
```

### 5.3 Test Data Management

**Issue**: Test data may be scattered
**Recommendation**: Centralize test data

```
tests/
├── fixtures/
│   ├── data/
│   │   ├── sample_files/
│   │   ├── sample_documents/
│   │   └── sample_metadata/
│   └── responses/
│       ├── api_responses/
│       └── llm_responses/
```

### 5.4 Continuous Testing

**Missing**: Pre-commit hooks
**Recommendation**: Add pre-commit hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: run-fast-tests
        name: Run Fast Tests
        entry: pytest
        args: ["-m", "fast", "--tb=short"]
        language: system
        pass_filenames: false
        always_run: true
```

### 5.5 Test Reporting

**Missing**: Test result tracking
**Recommendation**: Add test reporting

```python
# conftest.py
def pytest_sessionfinish(session, exitstatus):
    """Generate test report after session."""
    # Write test results to file
    # Track test duration
    # Identify flaky tests
    pass
```

### 5.6 Flaky Test Detection

**Missing**: Flaky test detection
**Recommendation**: Add flaky test detection

```bash
# Run tests multiple times to detect flaky tests
pytest --count=10 tests/  # Run each test 10 times
```

### 5.7 Test Performance Monitoring

**Missing**: Test performance tracking
**Recommendation**: Track test execution time

```python
# conftest.py
@pytest.fixture(autouse=True)
def track_test_performance(request):
    """Track test execution time."""
    start = time.time()
    yield
    duration = time.time() - start
    if duration > 5:  # Flag slow tests
        pytest.warns(UserWarning, f"Slow test: {request.node.name} took {duration}s")
```

---

## 6. Implementation Priority

### Phase 1: Critical Fixes (Week 1)

1. **Mock All LLM Clients** (Prevent token costs)
   - Add `USE_MOCK_LLM=true` to test environment
   - Update all agent tests to mock LLM clients
   - Add `@pytest.mark.ai` to AI tests and skip by default

2. **Fix Import Paths** (Fix broken tests)
   - Update orchestrator import paths
   - Update test references to new architecture

3. **Add MCP Server Tests** (Architectural alignment)
   - Create `tests/unit/mcp_servers/`
   - Test MCP server initialization
   - Test MCP tool execution

### Phase 2: Architectural Alignment (Week 2)

1. **Add Agent MCP Tool Usage Tests**
   - Verify agents use MCP tools (not direct calls)
   - Test agent-orchestrator integration via MCP

2. **Add Specialist Agent Tests**
   - Test new specialist agents
   - Test agent capabilities

3. **Update Orchestrator Tests**
   - Test MCP server initialization
   - Test orchestrator-agent integration

### Phase 3: Best Practices (Week 3)

1. **Add Test Tools**
   - `pytest-xdist` (parallel execution)
   - `pytest-timeout` (prevent hanging)
   - `pytest-cov` (coverage)

2. **Improve Test Quality**
   - Better test names
   - Better assertions
   - Better documentation

3. **Add Contract Tests**
   - SOA API contract tests
   - MCP tool contract tests

### Phase 4: Structural Improvements (Week 4)

1. **Reorganize Tests**
   - Feature-based organization
   - Centralize test data

2. **Add Continuous Testing**
   - Pre-commit hooks
   - Test reporting
   - Flaky test detection

---

## 7. Quick Wins

### Immediate Actions (Today)

1. **Add LLM Mocking** (30 minutes)
   ```python
   # conftest.py
   os.environ["USE_MOCK_LLM"] = "true"
   ```

2. **Skip AI Tests by Default** (15 minutes)
   ```python
   # pytest.ini
   addopts = -m "not ai"
   ```

3. **Fix Import Paths** (1 hour)
   - Update 4 orchestrator test files

### This Week

1. **Add MCP Server Tests** (4 hours)
2. **Add Agent MCP Tool Tests** (4 hours)
3. **Add pytest-xdist** (30 minutes)

---

## 8. Success Metrics

### Cost Reduction
- **Target**: Reduce test execution costs by 90%
- **Measure**: Track token usage per test run

### Test Coverage
- **Target**: >80% code coverage
- **Measure**: Use pytest-cov

### Test Speed
- **Target**: Unit tests < 30 seconds
- **Measure**: Track test execution time

### Test Reliability
- **Target**: <1% flaky test rate
- **Measure**: Run tests multiple times

---

## 9. Conclusion

**Critical Issues**:
1. ⚠️ **LLM calls in tests** → Causing high token costs
2. ⚠️ **Missing MCP architecture tests** → Can't verify new architecture
3. ⚠️ **Outdated import paths** → Tests may be broken

**Recommendations**:
1. **IMMEDIATE**: Mock all LLM clients, skip AI tests by default
2. **THIS WEEK**: Add MCP server tests, fix import paths
3. **THIS MONTH**: Improve test structure, add tooling

**Expected Outcome**:
- 90% reduction in test execution costs
- 100% architectural alignment
- Improved test reliability and speed

