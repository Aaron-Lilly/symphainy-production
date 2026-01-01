# Remaining Test Failures - Summary and Plan

**Date**: November 14, 2025  
**Status**: 48 Failed, 38 Errors (86 total issues)  
**Passing**: 247/349 (71%)

---

## Executive Summary

After completing 7 strategic test fixes, we have **86 remaining test issues** categorized into 5 main problem areas. This plan prioritizes fixes by impact and root cause.

---

## Failure Categories

### Category 1: Signature Issues (22 errors) 🔴 **HIGH PRIORITY**

**Issue**: `TypeError: non-default argument 'health_status' follows default argument`

**Affected Tests**:
- All agent tests (4 tests)
- All foundation comprehensive tests (12 tests)
- Orchestrator initialization tests (6 tests)

**Root Cause**: A base class or fixture has a method signature with `health_status` as a required parameter after optional parameters, which violates Python syntax.

**Impact**: Blocks all agent and foundation tests

**Fix Strategy**:
1. Find the base class/fixture with the problematic signature
2. Reorder parameters: required params before optional params
3. Or make `health_status` optional with a default value

**Files to Check**:
- Base classes for agents/orchestrators
- Foundation service base classes
- Test fixtures that create these services

---

### Category 2: Module Import Errors (13+ errors) 🔴 **HIGH PRIORITY**

**Issue**: `ModuleNotFoundError: No module named 'foundations.public_works_foundation.i...'`

**Affected Tests**:
- LLM abstraction tests (2 tests)
- Session abstraction tests (2 tests)
- Telemetry abstraction tests (2 tests)
- Meilisearch adapter tests (3 tests)
- OpenTelemetry adapter tests (2 tests)
- Content processing agent (1 test - different: `backend.protocols`)

**Root Cause**: Test fixtures or mocks are trying to import modules that:
1. Were archived/moved
2. Don't exist
3. Have incorrect paths

**Impact**: Blocks infrastructure abstraction and adapter tests

**Fix Strategy**:
1. Review `mock_infrastructure_patcher.py` for missing patches
2. Check if modules were archived (like `arango_content_metadata_adapter`)
3. Update test fixtures to handle missing modules gracefully
4. Fix import paths in test files

**Files to Check**:
- `tests/fixtures/mock_infrastructure_patcher.py`
- Test files with direct imports of infrastructure modules
- `__init__.py` files in infrastructure_adapters

---

### Category 3: Parameter Mismatches (8+ failures) 🟡 **MEDIUM PRIORITY**

**Sub-category 3a: MCP Server Tool Registration (4 failures)**
- **Issue**: `TypeError: MCPServerBase.register_tool() got an unexpected keyword argument`
- **Affected**: MCP server tests
- **Fix**: Update test calls to match actual `register_tool()` signature

**Sub-category 3b: Security Guard Service (3 failures)**
- **Issue**: `TypeError: SecurityGuardService.authenticate_user() got an unexpected keyword argument`
- **Issue**: `TypeError: SecurityGuardService.authorize_action() got an unexpected keyword argument`
- **Issue**: `AttributeError: 'SecurityGuardService' object has no attribute 'create_session'`
- **Fix**: Update tests to match actual service method signatures

**Sub-category 3c: Session Context (1 failure)**
- **Issue**: `TypeError: SessionContext.__init__() got an unexpected keyword argument 'user_id'`
- **Fix**: Update test to match actual `SessionContext` constructor

**Sub-category 3d: Redis Adapter (1 failure)**
- **Issue**: `TypeError: MockRedisAdapter.set() got an unexpected keyword argument 'ttl'`
- **Fix**: Update mock or test to handle `ttl` parameter correctly

---

### Category 4: Missing Attributes/Methods (10+ failures) 🟡 **MEDIUM PRIORITY**

**Sub-category 4a: Mock Adapters (5 failures)**
- **Issue**: `AttributeError: 'MockArangoDBAdapter' object has no attribute 'db'`
- **Issue**: `AttributeError: 'MockArangoDBAdapter' object has no attribute 'create_document'`
- **Affected**: ArangoDB adapter tests
- **Fix**: Update `MockArangoDBAdapter` in `mock_infrastructure_adapters.py` to include missing methods

**Sub-category 4b: Celery Adapter (1 failure)**
- **Issue**: `AttributeError: 'CeleryAdapter' object has no attribute 'get_task_status'`
- **Fix**: Check if method was renamed or removed, update test accordingly

**Sub-category 4c: Telemetry Abstraction (1 failure)**
- **Issue**: `AttributeError: <module 'foundations.public_works_foundation.infrastructure...`
- **Fix**: Check import path and module structure

**Sub-category 4d: Security Guard Modules (3 failures)**
- **Issue**: `assert False` - modules returning empty dicts
- **Fix**: Complete implementation or update test expectations

---

### Category 5: Test Logic/Assertion Issues (15+ failures) 🟢 **LOW PRIORITY**

**Sub-category 5a: Data Analyzer Service (4 failures)**
- **Issue**: `AssertionError: assert 'domain' in {...}`
- **Root Cause**: Service response structure changed, tests expect `domain` field
- **Fix**: Update tests to match actual service response structure

**Sub-category 5b: File Parser Service (1 failure)**
- **Issue**: `assert None is not None` - Content Steward not returning expected data
- **Fix**: Check mock setup or service implementation

**Sub-category 5c: ArangoDB Adapter (1 failure)**
- **Issue**: `assert None is not None` - Document not found
- **Fix**: Check mock adapter implementation

**Sub-category 5d: Abstract Class Instantiation (2 failures)**
- **Issue**: `TypeError: Can't instantiate abstract class OperationsMCPServer with abstract methods`
- **Issue**: `TypeError: Can't instantiate abstract class ContentAnalysisMCPServer with abstract methods`
- **Fix**: Tests trying to instantiate abstract classes - need to use concrete implementations or mocks

**Sub-category 5e: Other Assertions (7+ failures)**
- Various `assert False`, `assert None is not None`, etc.
- **Fix**: Review test logic and update assertions

---

## Prioritized Action Plan

### Phase 1: Critical Blockers (High Priority) 🔴

**Goal**: Unblock the most tests with minimal effort

#### 1.1 Fix Signature Issue (22 errors)
- **Effort**: Medium
- **Impact**: Unblocks 22 tests
- **Steps**:
  1. Search for `health_status` parameter in base classes
  2. Find method signature with required param after optional
  3. Reorder parameters or add default value
  4. Verify fix with agent/foundation tests

#### 1.2 Fix Module Import Errors (13+ errors)
- **Effort**: Low-Medium
- **Impact**: Unblocks 13+ tests
- **Steps**:
  1. Review `mock_infrastructure_patcher.py` for missing patches
  2. Add try/except blocks for archived modules (like we did for `arango_content_metadata_adapter`)
  3. Fix `backend.protocols` import in content processing agent test
  4. Verify fix with infrastructure abstraction tests

**Expected Result**: ~35 tests unblocked

---

### Phase 2: Parameter Mismatches (Medium Priority) 🟡

**Goal**: Fix tests that have wrong method signatures

#### 2.1 Fix MCP Server Tests (4 failures)
- **Effort**: Low
- **Steps**: Update test calls to match `register_tool()` signature

#### 2.2 Fix Security Guard Service Tests (3 failures)
- **Effort**: Medium
- **Steps**: 
  1. Check actual `SecurityGuardService` method signatures
  2. Update tests to match
  3. Add missing `create_session` method if needed

#### 2.3 Fix Other Parameter Issues (2 failures)
- **Effort**: Low
- **Steps**: Update SessionContext and Redis adapter test calls

**Expected Result**: ~9 tests fixed

---

### Phase 3: Mock Adapter Updates (Medium Priority) 🟡

**Goal**: Complete mock adapter implementations

#### 3.1 Fix MockArangoDBAdapter (5 failures)
- **Effort**: Low
- **Steps**: Add missing methods (`db`, `create_document`, `update_document`, `delete_document`)

#### 3.2 Fix Other Mock Issues (2 failures)
- **Effort**: Low
- **Steps**: Fix Celery adapter and telemetry abstraction mocks

**Expected Result**: ~7 tests fixed

---

### Phase 4: Test Logic Updates (Low Priority) 🟢

**Goal**: Update tests to match actual service behavior

#### 4.1 Fix Data Analyzer Tests (4 failures)
- **Effort**: Low
- **Steps**: Update assertions to match actual response structure

#### 4.2 Fix Abstract Class Tests (2 failures)
- **Effort**: Low
- **Steps**: Use concrete implementations or proper mocks

#### 4.3 Fix Other Assertions (9+ failures)
- **Effort**: Low-Medium
- **Steps**: Review and update test logic

**Expected Result**: ~15 tests fixed

---

## Implementation Strategy

### Approach
1. **Root Cause Focus**: Fix underlying issues, not symptoms
2. **Batch Similar Fixes**: Group related failures together
3. **Verify After Each Phase**: Run tests to confirm progress
4. **Document Patterns**: Note common issues for future prevention

### Testing Strategy
- Run tests after each phase to verify progress
- Focus on unblocking tests first (errors), then fixing failures
- Prioritize tests that block other tests

---

## Success Metrics

**Current State**:
- Passing: 247/349 (71%)
- Failed: 48 (14%)
- Errors: 38 (11%)
- Skipped: 16 (4%)

**Target State** (After Phase 1-2):
- Passing: 280+/349 (80%+)
- Failed: 30- (9%-)
- Errors: 5- (1%-)

**Ideal State** (After All Phases):
- Passing: 320+/349 (92%+)
- Failed: 10- (3%-)
- Errors: 0 (0%)

---

## Next Steps

1. **Start with Phase 1.1**: Fix signature issue (biggest blocker)
2. **Then Phase 1.2**: Fix import errors (quick wins)
3. **Verify Progress**: Run full test suite
4. **Continue with Phase 2**: Parameter mismatches
5. **Iterate**: Continue through remaining phases

---

## Notes

- Some failures may be due to incomplete implementations (e.g., Security Guard modules)
- Abstract class tests may need architectural decisions (use mocks vs concrete classes)
- Test logic issues may indicate service behavior changes that need documentation

---

**Last Updated**: November 14, 2025

