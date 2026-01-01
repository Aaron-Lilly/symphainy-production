# Remaining Test Issues - Recommendations

**Date**: November 13, 2025  
**Status**: 10 tests remaining (156/186 passing = 83.9%)

---

## Executive Summary

After Phase 1 fixes, we have **10 remaining test failures** across 3 categories:

1. **Architectural Issues (3 tests)** - Require understanding of internal adapter creation
2. **Parameter Mismatches (5 tests)** - Simple fixes, just need correct signatures
3. **Test Logic Issues (2 tests)** - Tests checking wrong methods/assertions

**Recommendation**: Fix the 7 simple issues first (parameter mismatches + test logic), then tackle the 3 architectural issues.

---

## Issue Analysis & Recommendations

### Category 1: Architectural Issues (3 tests)

These require understanding how abstractions create adapters internally.

---

#### Issue 1.1: Session Abstraction - Async Mock Issue

**Test**: `test_session_abstraction.py::test_create_session`  
**Error**: `TypeError: object MagicMock can't be used in 'await' expression`

**Root Cause**:
1. `SessionAbstraction` creates `RedisSessionAdapter` internally via `_initialize_adapter()`
2. `RedisSessionAdapter` requires a real `RedisAdapter` with async methods
3. The mock `redis_adapter` is passed, but `RedisSessionAdapter` accesses `self.redis_adapter.client.hset()` which needs to be async
4. The mock's `client` is a `MagicMock`, not an `AsyncMock`

**Code Flow**:
```
SessionAbstraction.__init__()
  → _initialize_adapter() 
    → RedisSessionAdapter(redis_adapter=mock_redis_adapter)
      → self.redis_adapter.client.hset()  # This is MagicMock, not AsyncMock
```

**Recommendations**:

**Option A: Mock the Redis Client Properly (Recommended)**
```python
@pytest.fixture
def mock_redis_adapter(self):
    """Mock Redis adapter with async client."""
    adapter = MagicMock()
    # Create async mock for the client
    async_client = AsyncMock()
    async_client.hset = AsyncMock(return_value=True)
    async_client.hget = AsyncMock(return_value=b'{"session_id": "session_123"}')
    async_client.hgetall = AsyncMock(return_value={b"session_id": b"session_123"})
    async_client.delete = AsyncMock(return_value=True)
    async_client.expire = AsyncMock(return_value=True)
    
    adapter.client = async_client
    adapter.host = "localhost"
    adapter.port = 6379
    adapter.db = 0
    return adapter
```

**Option B: Patch at the Adapter Level**
```python
@patch('foundations.public_works_foundation.infrastructure_adapters.redis_session_adapter.RedisSessionAdapter')
async def test_create_session(self, mock_redis_session_adapter_class, ...):
    # Mock the adapter instance
    mock_adapter_instance = AsyncMock()
    mock_adapter_instance.create_session = AsyncMock(return_value=Session(...))
    mock_redis_session_adapter_class.return_value = mock_adapter_instance
    ...
```

**Option C: Use Real Redis in Tests (Not Recommended)**
- Requires Redis running in test environment
- Slower tests
- Not isolated

**Recommended Path**: **Option A** - Properly mock the Redis client with AsyncMock

**Effort**: 15-20 minutes  
**Priority**: Medium (architectural pattern important for future tests)

---

#### Issue 1.2: LLM Abstraction - Mock Not Being Called

**Test**: `test_llm_abstraction.py::test_generate_response`  
**Error**: `AssertionError: Expected 'generate_response' to have been called once. Called 0 times.`

**Root Cause**:
1. `LLMAbstraction.__init__()` calls `_initialize_adapters()` which creates new adapter instances
2. The test passes a mock, but the abstraction creates its own `OpenAIAdapter()` internally
3. The mock is never used

**Code Flow**:
```
LLMAbstraction.__init__(provider="openai")
  → _initialize_adapters()
    → OpenAIAdapter(**kwargs)  # Creates NEW instance, ignores mock
```

**Recommendations**:

**Option A: Patch the Adapter Class (Recommended)**
```python
@patch('foundations.public_works_foundation.infrastructure_adapters.openai_adapter.OpenAIAdapter')
async def test_generate_response(self, mock_openai_adapter_class, abstraction):
    # Mock the adapter instance
    mock_adapter = AsyncMock()
    mock_adapter.generate_response = AsyncMock(return_value=LLMResponse(...))
    mock_openai_adapter_class.return_value = mock_adapter
    
    # Now the abstraction will use our mock
    result = await abstraction.generate_response(...)
    mock_adapter.generate_response.assert_called_once()
```

**Option B: Pass Adapter via Dependency Injection**
- Modify `LLMAbstraction` to accept adapter instances
- More invasive change
- Better architecture long-term

**Option C: Test at Integration Level**
- Test the abstraction with real adapters
- Not a unit test anymore

**Recommended Path**: **Option A** - Patch the adapter class

**Effort**: 10-15 minutes  
**Priority**: Medium (common pattern for abstractions that create adapters)

---

#### Issue 1.3: Task Management Abstraction - Wrong Method Checked

**Test**: `test_task_management_abstraction.py::test_get_task_status`  
**Error**: `AssertionError: Expected 'get_task_status' to have been called once. Called 0 times.`

**Root Cause**:
1. `TaskManagementAbstraction.get_task_status()` calls `self.celery_adapter.get_task_result()`
2. The test is checking if `get_task_status()` was called on the adapter
3. Should check `get_task_result()` instead

**Code**:
```python
async def get_task_status(self, task_id: str) -> TaskStatus:
    result_data = self.celery_adapter.get_task_result(task_id)  # Calls this
    return self._convert_celery_status(result_data.get("status", "PENDING"))
```

**Recommendation**:

**Fix the Assertion**:
```python
async def test_get_task_status(self, abstraction, mock_celery_adapter):
    """Test abstraction can get task status."""
    result = await abstraction.get_task_status("task_123")
    
    # Check the correct method
    mock_celery_adapter.get_task_result.assert_called_once_with("task_123")
    assert result == TaskStatus.COMPLETED or (hasattr(result, "value") and result.value == "completed")
```

**Effort**: 5 minutes  
**Priority**: High (simple fix)

---

### Category 2: Parameter Mismatches (5 tests)

These are simple fixes - just need to match production method signatures.

---

#### Issue 2.1: Roadmap Generation Service - track_strategic_progress

**Test**: `test_roadmap_generation_service.py::test_track_strategic_progress_soa_api`  
**Error**: `TypeError: RoadmapGenerationService.track_strategic_progress() got an unexpected keyword argument 'roadmap_id'`

**Root Cause**: Test is calling with `roadmap_id`, but method signature is:
```python
async def track_strategic_progress(
    self,
    goals: List[Dict[str, Any]],
    performance_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
```

**Recommendation**:
```python
# Fix the test call
result = await roadmap_service.track_strategic_progress(
    goals=[{"id": "goal_1", "status": "in_progress"}],
    performance_data={}
)
```

**Effort**: 2 minutes  
**Priority**: High (simple fix)

---

#### Issue 2.2: Roadmap Generation Service - analyze_strategic_trends

**Test**: `test_roadmap_generation_service.py::test_analyze_strategic_trends_soa_api`  
**Error**: `TypeError: RoadmapGenerationService.analyze_strategic_trends() got an unexpected keyword argument 'business_context'`

**Root Cause**: Method signature is:
```python
async def analyze_strategic_trends(
    self,
    market_data: Dict[str, Any]
) -> Dict[str, Any]:
```

**Recommendation**:
```python
# Fix the test call
result = await roadmap_service.analyze_strategic_trends(
    market_data={"roadmap_ids": ["roadmap_1", "roadmap_2"]}
)
```

**Effort**: 2 minutes  
**Priority**: High (simple fix)

---

#### Issue 2.3-2.5: POC Generation Service (3 tests)

**Tests**:
- `test_poc_generation_service.py::test_generate_poc_roadmap_soa_api`
- `test_poc_generation_service.py::test_analyze_poc_financials_soa_api`
- `test_poc_generation_service.py::test_calculate_poc_metrics_soa_api`

**Error**: All have `TypeError: got an unexpected keyword argument 'pillar_outputs'`

**Root Cause**: Methods take `business_context`, not `pillar_outputs`

**Method Signatures**:
```python
async def generate_poc_roadmap(
    self,
    business_context: Dict[str, Any],
    poc_type: str = "hybrid"
) -> Dict[str, Any]:

async def analyze_poc_financials(
    self,
    business_context: Dict[str, Any],
    poc_type: str = "hybrid"
) -> Dict[str, Any]:

async def calculate_poc_metrics(
    self,
    business_context: Dict[str, Any],
    poc_type: str = "hybrid"
) -> Dict[str, Any]:
```

**Recommendation**:
```python
# Fix all three test calls
result = await poc_service.generate_poc_roadmap(
    business_context={"pillar_outputs": {...}},
    poc_type="hybrid"
)

result = await poc_service.analyze_poc_financials(
    business_context={"pillar_outputs": {...}},
    poc_type="hybrid"
)

result = await poc_service.calculate_poc_metrics(
    business_context={"pillar_outputs": {...}},
    poc_type="hybrid"
)
```

**Effort**: 5 minutes (all three)  
**Priority**: High (simple fixes)

---

### Category 3: Test Logic Issues (2 tests)

---

#### Issue 3.1: Business Outcomes Orchestrator - track_strategic_progress

**Test**: `test_business_outcomes_orchestrator.py::test_track_strategic_progress`  
**Error**: `TypeError: BusinessOutcomesOrchestrator.track_strategic_progress() got an unexpected keyword argument 'roadmap_id'`

**Root Cause**: We already fixed this, but the fix might not have been applied correctly. The method signature is:
```python
async def track_strategic_progress(
    self,
    goals: List[Dict[str, Any]],
    performance_data: Optional[Dict[str, Any]] = None,
    user_id: str = "anonymous"
) -> Dict[str, Any]:
```

**Recommendation**: Verify the fix was applied correctly:
```python
result = await orchestrator.track_strategic_progress(
    goals=[{"id": "goal_1", "status": "in_progress"}],
    performance_data={}
)
```

**Effort**: 2 minutes  
**Priority**: High (verify fix)

---

## Recommended Action Plan

### Phase 2A: Quick Wins (7 tests - 15 minutes)

**Priority**: Fix these first - they're simple and will boost confidence

1. ✅ **Task Management** - Fix assertion (5 min)
2. ✅ **Roadmap Generation** - Fix 2 parameter mismatches (4 min)
3. ✅ **POC Generation** - Fix 3 parameter mismatches (5 min)
4. ✅ **Business Outcomes** - Verify fix (1 min)

**Expected Result**: 163/186 tests passing (87.6%)

---

### Phase 2B: Architectural Patterns (3 tests - 45 minutes)

**Priority**: Fix these to establish proper testing patterns

1. ✅ **Session Abstraction** - Mock Redis client properly (20 min)
2. ✅ **LLM Abstraction** - Patch adapter class (15 min)
3. ✅ **Verify all patterns** - Document final patterns (10 min)

**Expected Result**: 166/186 tests passing (89.2%)

---

## Implementation Priority

### Immediate (Today)
- [ ] Fix Category 2 issues (5 parameter mismatches) - 10 minutes
- [ ] Fix Category 3 issues (2 test logic) - 5 minutes
- [ ] **Total**: 15 minutes → **163/186 passing (87.6%)**

### Short-term (This Week)
- [ ] Fix Session Abstraction async mock - 20 minutes
- [ ] Fix LLM Abstraction adapter patching - 15 minutes
- [ ] Document final patterns - 10 minutes
- [ ] **Total**: 45 minutes → **166/186 passing (89.2%)**

### Long-term (Architectural Improvements)
- [ ] Consider dependency injection improvements for better testability
- [ ] Create test utilities for common mocking patterns
- [ ] Document adapter creation patterns for future tests

---

## Key Patterns to Document

1. **Mocking Adapters with Internal Clients**
   - When adapters have nested clients (e.g., `redis_adapter.client`), mock the client too
   - Use `AsyncMock` for async methods on nested clients

2. **Patching Adapter Classes**
   - When abstractions create adapters internally, patch the adapter class
   - Use `@patch` decorator at the class level

3. **Checking Internal Method Calls**
   - When testing abstractions, check the methods they actually call
   - Don't assume method names match between abstraction and adapter

---

## Success Metrics

**Current**: 156/186 (83.9%)  
**After Phase 2A**: 163/186 (87.6%) - **+7 tests**  
**After Phase 2B**: 166/186 (89.2%) - **+10 tests total**

**Target**: 90%+ pass rate  
**Gap**: 4-6 tests remaining (likely Phase 2/3 issues)

---

**Last Updated**: November 13, 2025





