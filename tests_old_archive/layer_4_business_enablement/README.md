# Business Enablement Test Suite

Comprehensive test suite for Business Enablement realm components.

## Test Structure

```
layer_4_business_enablement/
├── compliance/              # Validator tests (DI, Utility, Foundation)
├── initialization/          # Component initialization tests
├── functionality/           # Component functionality tests (mock AI)
│   ├── enabling_services/  # 15+ enabling services
│   ├── orchestrators/      # 4 orchestrators
│   ├── agents/             # 9+ agents
│   └── mcp_servers/        # 5 MCP servers
├── integration/            # Integration tests (real infrastructure, mock AI)
├── ai_integration/         # AI integration tests (real AI APIs) ⭐
└── e2e_mvp_demo/          # End-to-end MVP/CTO Demo tests ⭐
```

## Test Phases

### Phase 0: Foundation Setup ✅
- Test directory structure
- Basic fixtures
- AI configuration
- Test data helpers

### Phase 1: Compliance & Initialization
- Run validators
- Create initialization tests
- Verify infrastructure connections

### Phase 2: Component Functionality
- Test enabling services
- Test orchestrators
- Test agents
- Test MCP servers
- Use mock AI responses

### Phase 3: Integration Tests
- Test service-to-service communication
- Test orchestrator-to-service communication
- Test agent-to-MCP communication
- Use real infrastructure, mock AI

### Phase 4: AI Integration Tests ⭐
- Test agent LLM calls with real APIs
- Test agent decision-making
- Test multi-agent coordination
- Use real AI APIs (gpt-4o-mini)

### Phase 5: E2E MVP/CTO Demo Tests ⭐
- Test complete MVP/CTO Demo scenarios
- Verify business value
- Performance validation

## Running Tests

### Run all Business Enablement tests
```bash
pytest tests/layer_4_business_enablement/ -v
```

### Run specific phase
```bash
# Phase 1: Compliance & Initialization
pytest tests/layer_4_business_enablement/compliance/ tests/layer_4_business_enablement/initialization/ -v

# Phase 2: Component Functionality
pytest tests/layer_4_business_enablement/functionality/ -v

# Phase 3: Integration Tests
pytest tests/layer_4_business_enablement/integration/ -v

# Phase 4: AI Integration Tests (requires AI_ENABLED=true)
AI_ENABLED=true pytest tests/layer_4_business_enablement/ai_integration/ -v

# Phase 5: E2E MVP/CTO Demo Tests (requires AI_ENABLED=true)
AI_ENABLED=true pytest tests/layer_4_business_enablement/e2e_mvp_demo/ -v
```

## Configuration

### AI Configuration
Set environment variables for AI integration tests:

```bash
export AI_ENABLED=true
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini
export OPENAI_MAX_TOKENS=500
export AI_CACHE_ENABLED=true
```

### Infrastructure
Ensure Docker Compose services are running:

```bash
docker-compose -f tests/docker-compose.test.yml up -d
```

## Fixtures

Fixtures are available in `tests/fixtures/business_enablement_fixtures.py`:
- Mock services (enabling services, orchestrators, agents, MCP servers)
- Real services (for integration tests)
- DI Container and Platform Gateway fixtures

## Test Data

Test datasets are available in `tests/fixtures/test_datasets.py`:
- Sample documents (PDF, DOCX, HTML, text)
- Sample data files (CSV, JSON)
- Sample workflows
- Sample business scenarios

## AI Mock Responses

Mock AI responses are available in `tests/fixtures/ai_mock_responses.py`:
- Content analysis responses
- Insights generation responses
- Operations optimization responses
- Multi-agent coordination responses

Use these for Phase 2 and Phase 3 tests (no real API calls).

## Status

- ✅ Phase 0: Foundation Setup - Complete
- ⏳ Phase 1: Compliance & Initialization - In Progress
- ⏳ Phase 2: Component Functionality - Pending
- ⏳ Phase 3: Integration Tests - Pending
- ⏳ Phase 4: AI Integration Tests - Pending
- ⏳ Phase 5: E2E MVP/CTO Demo Tests - Pending

