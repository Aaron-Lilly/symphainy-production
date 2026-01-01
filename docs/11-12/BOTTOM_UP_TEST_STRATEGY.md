# Bottom-Up Test Strategy - Catch Issues Early

**Goal**: Test each layer in isolation, catch issues where they occur, prevent production code issues

**Principle**: Test from the bottom up - if foundations work, everything else is easier to debug

---

## 🎯 Test Pyramid (Bottom-Up)

```
                    /\
                   /  \  E2E (5%) - Full system, slow
                  /____\
                 /      \  Integration (15%) - Multiple components
                /________\
               /          \  Unit (80%) - Single component, fast
              /____________\
```

**Key**: 80% fast unit tests, 15% integration, 5% E2E

---

## 📊 Layer-by-Layer Testing Strategy

### Layer 0: Infrastructure Adapters (Foundation)

**Test**: Each adapter in isolation
**Goal**: Verify adapters work correctly before anything uses them

**Test Structure**:
```
tests/unit/infrastructure_adapters/
├── test_supabase_file_management_adapter.py
├── test_redis_adapter.py
├── test_arangodb_adapter.py
├── test_opentelemetry_health_adapter.py
└── test_telemetry_adapter.py
```

**Test Pattern**:
```python
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.infrastructure
class TestSupabaseFileManagementAdapter:
    """Test Supabase File Management Adapter in isolation."""
    
    @pytest.mark.asyncio
    async def test_adapter_initializes(self, mock_supabase_client):
        """Test adapter initializes correctly."""
        adapter = SupabaseFileManagementAdapter(mock_supabase_client)
        await adapter.initialize()
        assert adapter.is_initialized
    
    @pytest.mark.asyncio
    async def test_adapter_stores_file(self, adapter, sample_file):
        """Test adapter can store a file."""
        result = await adapter.store_file(sample_file)
        assert result["success"] is True
        assert "file_id" in result
    
    @pytest.mark.asyncio
    async def test_adapter_retrieves_file(self, adapter, stored_file_id):
        """Test adapter can retrieve a file."""
        result = await adapter.retrieve_file(stored_file_id)
        assert result["success"] is True
        assert "content" in result
```

**Validation**: Check for mocks, TODOs, placeholders in adapter code

---

### Layer 1: Public Works Foundation

**Test**: Foundation services in isolation
**Goal**: Verify foundations work before Smart City uses them

**Test Structure**:
```
tests/unit/foundations/
├── test_di_container.py              # ✅ Exists
├── test_public_works_foundation.py   # ✅ Exists
├── test_curator_foundation.py
├── test_communication_foundation.py
└── test_agentic_foundation.py
```

**Test Pattern**:
```python
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.foundations
class TestPublicWorksFoundation:
    """Test Public Works Foundation in isolation."""
    
    @pytest.mark.asyncio
    async def test_foundation_initializes(self, mock_di_container):
        """Test foundation initializes correctly."""
        foundation = PublicWorksFoundationService(mock_di_container)
        await foundation.initialize()
        assert foundation.is_initialized
    
    @pytest.mark.asyncio
    async def test_foundation_provides_file_management(self, foundation):
        """Test foundation provides file management abstraction."""
        file_mgmt = await foundation.get_file_management_abstraction()
        assert file_mgmt is not None
        assert hasattr(file_mgmt, 'store_file')
        assert hasattr(file_mgmt, 'retrieve_file')
```

**Validation**: Check for mocks, TODOs, placeholders in foundation code

---

### Layer 2: Smart City Services

**Test**: Each Smart City service in isolation
**Goal**: Verify services work before Business Enablement uses them

**Test Structure**:
```
tests/unit/smart_city/
├── test_librarian_service.py         # ✅ Exists
├── test_data_steward_service.py
├── test_security_guard_service.py     # ✅ Exists
├── test_conductor_service.py
├── test_post_office_service.py
├── test_traffic_cop_service.py
├── test_nurse_service.py
├── test_content_steward_service.py
└── test_city_manager_service.py
```

**Test Pattern**:
```python
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.smart_city
class TestLibrarianService:
    """Test Librarian Service in isolation."""
    
    @pytest.mark.asyncio
    async def test_service_initializes(self, mock_di_container):
        """Test service initializes correctly."""
        service = LibrarianService(mock_di_container)
        await service.initialize()
        assert service.is_initialized
    
    @pytest.mark.asyncio
    async def test_store_document_soa_api(self, librarian_service, sample_document):
        """Test store_document SOA API works."""
        result = await librarian_service.store_document(
            document_data=sample_document,
            metadata={}
        )
        assert result["success"] is True
        assert "document_id" in result
    
    @pytest.mark.asyncio
    async def test_search_knowledge_soa_api(self, librarian_service):
        """Test search_knowledge SOA API works."""
        result = await librarian_service.search_knowledge(
            query="test query",
            filters={}
        )
        assert isinstance(result, dict)
        assert "results" in result or "documents" in result
```

**Validation**: Check for mocks, TODOs, placeholders in service code

---

### Layer 3: Enabling Services

**Test**: Each enabling service in isolation
**Goal**: Verify services work before orchestrators use them

**Test Structure**:
```
tests/unit/enabling_services/
├── test_file_parser_service.py
├── test_format_composer_service.py
├── test_data_analyzer_service.py
├── test_metrics_calculator_service.py
├── test_visualization_engine_service.py
├── test_roadmap_generation_service.py
├── test_poc_generation_service.py
└── ...
```

**Test Pattern**:
```python
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.enabling_services
class TestFileParserService:
    """Test File Parser Service in isolation."""
    
    @pytest.mark.asyncio
    async def test_service_initializes(self, mock_di_container):
        """Test service initializes correctly."""
        service = FileParserService(mock_di_container)
        await service.initialize()
        assert service.is_initialized
    
    @pytest.mark.asyncio
    async def test_parse_file_soa_api(self, file_parser_service, sample_file_id):
        """Test parse_file SOA API works."""
        result = await file_parser_service.parse_file(
            file_id=sample_file_id,
            parse_options={}
        )
        assert result["success"] is True
        assert "parsed_content" in result
    
    @pytest.mark.asyncio
    async def test_detect_file_type_soa_api(self, file_parser_service, sample_file_id):
        """Test detect_file_type SOA API works."""
        result = await file_parser_service.detect_file_type(file_id=sample_file_id)
        assert result["success"] is True
        assert "file_type" in result
```

**Validation**: Check for mocks, TODOs, placeholders in service code

---

### Layer 4: Orchestrators

**Test**: Each orchestrator in isolation
**Goal**: Verify orchestrators compose services correctly

**Test Structure**:
```
tests/unit/orchestrators/
├── test_content_analysis_orchestrator.py
├── test_insights_orchestrator.py
├── test_operations_orchestrator.py
└── test_business_outcomes_orchestrator.py
```

**Test Pattern**:
```python
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.orchestrators
class TestContentAnalysisOrchestrator:
    """Test Content Analysis Orchestrator in isolation."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initializes(self, mock_di_container):
        """Test orchestrator initializes correctly."""
        orchestrator = ContentAnalysisOrchestrator(mock_di_container)
        await orchestrator.initialize()
        assert orchestrator.is_initialized
        assert hasattr(orchestrator, 'mcp_server')  # Verify MCP server initialized
    
    @pytest.mark.asyncio
    async def test_orchestrator_composes_services(self, orchestrator, mock_enabling_services):
        """Test orchestrator composes enabling services correctly."""
        result = await orchestrator.parse_file("test_123")
        # Verify orchestrator called enabling service
        mock_enabling_services['file_parser'].parse_file.assert_called_once()
```

**Validation**: Check for mocks, TODOs, placeholders in orchestrator code

---

### Layer 5: MCP Servers

**Test**: Each MCP server in isolation
**Goal**: Verify MCP servers expose tools correctly

**Test Structure**:
```
tests/unit/mcp_servers/
├── test_content_analysis_mcp_server.py
├── test_insights_mcp_server.py
├── test_operations_mcp_server.py
└── test_business_outcomes_mcp_server.py
```

**Test Pattern**:
```python
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.mcp
class TestContentAnalysisMCPServer:
    """Test Content Analysis MCP Server in isolation."""
    
    @pytest.mark.asyncio
    async def test_mcp_server_initializes(self, mock_orchestrator, mock_di_container):
        """Test MCP server initializes correctly."""
        mcp_server = ContentAnalysisMCPServer(mock_orchestrator, mock_di_container)
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

**Validation**: Check for mocks, TODOs, placeholders in MCP server code

---

### Layer 6: Agents

**Test**: Each agent in isolation
**Goal**: Verify agents use MCP tools correctly

**Test Structure**:
```
tests/unit/agents/
├── test_content_processing_agent.py
├── test_insights_specialist_agent.py
├── test_operations_specialist_agent.py
└── test_business_outcomes_specialist_agent.py
```

**Test Pattern**:
```python
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.agents
class TestInsightsSpecialistAgent:
    """Test Insights Specialist Agent in isolation."""
    
    @pytest.mark.asyncio
    async def test_agent_uses_mcp_tools(self, insights_agent, mock_orchestrator):
        """Test agent uses MCP tools, not direct orchestrator calls."""
        mock_mcp_server = MagicMock()
        mock_mcp_server.execute_tool = AsyncMock(return_value={"success": True})
        mock_orchestrator.mcp_server = mock_mcp_server
        
        insights_agent.set_orchestrator(mock_orchestrator)
        
        result = await insights_agent.generate_grounded_insights("resource_123")
        
        # Verify MCP tool was called
        assert mock_mcp_server.execute_tool.called
        # Verify NO direct orchestrator call
        assert not hasattr(mock_orchestrator, 'generate_grounded_insights') or \
               not mock_orchestrator.generate_grounded_insights.called
```

**Validation**: Check for mocks, TODOs, placeholders in agent code

---

## 🔍 Production Code Validation

### Automated Validation Script

**Create**: `tests/scripts/validate_production_code.py`

**Purpose**: Check for mocks, TODOs, placeholders, hardcoded cheats in production code

**Checks**:
1. No `mock`, `Mock`, `MagicMock` in production code
2. No `TODO`, `FIXME`, `XXX` comments
3. No `pass` statements (empty implementations)
4. No hardcoded test values
5. No `# HACK`, `# CHEAT`, `# TEMP` comments

**Usage**:
```bash
python3 tests/scripts/validate_production_code.py
```

---

## 📋 Implementation Plan

### Phase 1: Create Validation Script (1 hour)

**File**: `tests/scripts/validate_production_code.py`

**Features**:
- Scan production code for anti-patterns
- Report violations with file/line numbers
- Exit with error code if violations found
- Can be run in CI/CD

### Phase 2: Create Layer 0 Tests (2 hours)

**Create**: `tests/unit/infrastructure_adapters/`

**Tests**:
- One test file per adapter
- Test initialization
- Test core operations
- Test error handling

### Phase 3: Enhance Layer 1 Tests (2 hours)

**Enhance**: `tests/unit/foundations/`

**Add**:
- Test each foundation service in isolation
- Test foundation provides abstractions
- Test foundation initialization

### Phase 4: Enhance Layer 2 Tests (4 hours)

**Enhance**: `tests/unit/smart_city/`

**Add**:
- Test each Smart City service in isolation
- Test SOA APIs
- Test service initialization

### Phase 5: Create Layer 3 Tests (4 hours)

**Create**: `tests/unit/enabling_services/`

**Tests**:
- One test file per enabling service
- Test SOA APIs
- Test service composition

### Phase 6: Enhance Layer 4 Tests (2 hours)

**Enhance**: `tests/unit/orchestrators/`

**Add**:
- Test orchestrator initialization
- Test MCP server initialization
- Test orchestrator composes services

### Phase 7: Create Layer 5 Tests (2 hours)

**Create**: `tests/unit/mcp_servers/`

**Tests**:
- Test MCP server initialization
- Test tool registration
- Test tool execution routes to orchestrator

### Phase 8: Enhance Layer 6 Tests (2 hours)

**Enhance**: `tests/unit/agents/`

**Add**:
- Test agent uses MCP tools
- Test agent doesn't call orchestrator directly
- Test agent initialization

---

## 🛠️ Test Template Generator

**Create**: `tests/scripts/generate_test_template.py`

**Purpose**: Generate test file templates for each layer

**Usage**:
```bash
python3 tests/scripts/generate_test_template.py \
    --layer infrastructure_adapters \
    --component SupabaseFileManagementAdapter \
    --output tests/unit/infrastructure_adapters/test_supabase_file_management_adapter.py
```

---

## 📊 Test Execution Order

### Recommended Execution Order

1. **Infrastructure Adapters** (Layer 0)
   - If these fail, everything else will fail
   - Fast, isolated tests

2. **Foundations** (Layer 1)
   - Depends on adapters
   - Fast, isolated tests

3. **Smart City Services** (Layer 2)
   - Depends on foundations
   - Fast, isolated tests

4. **Enabling Services** (Layer 3)
   - Depends on Smart City
   - Fast, isolated tests

5. **Orchestrators** (Layer 4)
   - Depends on enabling services
   - Fast, isolated tests

6. **MCP Servers** (Layer 5)
   - Depends on orchestrators
   - Fast, isolated tests

7. **Agents** (Layer 6)
   - Depends on MCP servers
   - Fast, isolated tests

8. **Integration Tests** (Layer 7)
   - Multiple components
   - Medium speed

9. **E2E Tests** (Layer 8)
   - Full system
   - Slow, run last

### Test Runner Enhancement

**Update**: `tests/run_tests.py`

**Add**: Layer-by-layer execution

```bash
python3 run_tests.py --layer 0  # Infrastructure adapters
python3 run_tests.py --layer 1  # Foundations
python3 run_tests.py --layer 2  # Smart City
python3 run_tests.py --layer 3  # Enabling services
python3 run_tests.py --layer 4  # Orchestrators
python3 run_tests.py --layer 5  # MCP servers
python3 run_tests.py --layer 6  # Agents
python3 run_tests.py --layers 0-6  # All layers in order
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

## 📝 Next Steps

1. **Create validation script** (prevents production code issues)
2. **Create Layer 0 tests** (infrastructure adapters)
3. **Enhance existing tests** (add layer-by-layer structure)
4. **Create missing tests** (MCP servers, agents)
5. **Update test runner** (layer-by-layer execution)

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

## 🚀 Quick Start

### Step 1: Create Validation Script

```bash
python3 tests/scripts/validate_production_code.py
```

### Step 2: Run Layer 0 Tests

```bash
pytest tests/unit/infrastructure_adapters/ -v
```

### Step 3: Fix Any Issues

- Read error messages
- Fix at the layer where issue occurs
- Re-run that layer's tests

### Step 4: Move to Next Layer

- Only proceed if current layer passes
- Test next layer in isolation
- Repeat

---

## 📚 Test Examples

See `tests/unit/` for examples of each layer's test patterns.

