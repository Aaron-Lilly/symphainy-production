# Production Code Patterns Fix Plan - Issues 1, 2, and 4

**Date**: November 13, 2025  
**Status**: Planning Phase  
**Team**: Development Team (Issues 3 & 5 handled separately)

---

## Executive Summary

This plan addresses three production code pattern issues identified during Phase 1 test fixes:

1. **Parameter Naming Inconsistency** (`business_context` vs `context_data`) - 159 occurrences
2. **Required Parameters Without Defaults** (Dataclasses) - ~10-15 dataclasses
3. **Method Naming Inconsistencies** (Legacy method names) - 23+ files

**Estimated Effort**: 3-4 days total  
**Risk Level**: Low-Medium (mostly refactoring, minimal functional changes)  
**Priority**: Medium (improves consistency and developer experience)

---

## Issue 1: Parameter Naming Inconsistency

### Current State Analysis

**Problem**: Two parameter names used for the same concept:
- `business_context` - Used in service layer (RoadmapGenerationService, POCGenerationService)
- `context_data` - Used in orchestrator layer (BusinessOutcomesOrchestrator) and MCP servers

**Evidence** (Actual counts from codebase):
- **`context_data`**: 54 occurrences (needs to be changed)
- **`business_context`**: 227 occurrences (dominant pattern - 81% of usage)
- **Service methods** (enabling services): Use `business_context`
- **Orchestrator methods**: Use `context_data` (inconsistent)
- **MCP Server tools**: Use `context_data` (inconsistent)

**Files Affected**:
1. `backend/business_enablement/enabling_services/roadmap_generation_service/roadmap_generation_service.py` - Uses `business_context`
2. `backend/business_enablement/enabling_services/poc_generation_service/poc_generation_service.py` - Uses `business_context`
3. `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/business_outcomes_orchestrator/business_outcomes_orchestrator.py` - Uses `context_data`
4. `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/business_outcomes_orchestrator/mcp_server/business_outcomes_mcp_server.py` - Uses `context_data`
5. Plus 11 more files with mixed usage

### Decision: Standardize on `business_context`

**Rationale**:
- More descriptive and explicit
- Already used in most service methods (enabling services are the source of truth)
- Clearer intent - explicitly indicates business context
- Better aligns with domain language

### Migration Plan

#### Phase 1.1: Audit and Document (30 min)
1. Create mapping of all occurrences:
   ```bash
   grep -rn "context_data" backend/business_enablement/ > context_data_occurrences.txt
   grep -rn "business_context" backend/business_enablement/ > business_context_occurrences.txt
   ```
2. Categorize by:
   - Function parameters
   - Variable assignments
   - Dictionary keys
   - Comments/documentation

#### Phase 1.2: Update Orchestrator Layer (2-3 hours)
**Files to update**:
- `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/business_outcomes_orchestrator/business_outcomes_orchestrator.py`
  - `generate_strategic_roadmap(context_data)` → `generate_strategic_roadmap(business_context)`
  - `generate_poc_proposal(context_data)` → `generate_poc_proposal(business_context)`
  - `create_comprehensive_strategic_plan(context_data)` → `create_comprehensive_strategic_plan(business_context)`
  - Update internal variable names from `context_data` to `business_context`

#### Phase 1.3: Update MCP Servers (1-2 hours)
**Files to update**:
- `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/business_outcomes_orchestrator/mcp_server/business_outcomes_mcp_server.py`
  - `_generate_strategic_roadmap_tool(context_data)` → `_generate_strategic_roadmap_tool(business_context)`
  - `_generate_poc_proposal_tool(context_data)` → `_generate_poc_proposal_tool(business_context)`
  - `_create_comprehensive_strategic_plan_tool(context_data)` → `_create_comprehensive_strategic_plan_tool(business_context)`
  - Update tool descriptions to use `business_context`

#### Phase 1.4: Update Other Files (2-3 hours)
**Files to review and update**:
- `backend/business_enablement/delivery_manager/delivery_manager_service.py`
- `backend/business_enablement/delivery_manager/modules/business_enablement_orchestration.py`
- `backend/business_enablement/delivery_manager/modules/soa_mcp.py`
- `backend/business_enablement/agents/specialists/*.py`
- Any other files with `context_data` usage

#### Phase 1.5: Update Tests (1-2 hours)
- Update all test files that use `context_data` parameter
- Update test fixtures and mocks
- Run test suite to verify

#### Phase 1.6: Update Documentation (30 min)
- Update API documentation
- Update method docstrings
- Update any architecture docs

**Total Estimated Time**: 7-11 hours (~1-1.5 days)

---

## Issue 2: Required Parameters Without Defaults

### Current State Analysis

**Problem**: Dataclasses with required parameters that could have sensible defaults, especially:
- `timestamp` fields that could default to `datetime.utcnow()`
- `created_at` fields that could default to current time
- `labels`/`metadata` dicts that could default to empty dicts

**Example Found**:
```python
@dataclass
class TelemetryData:
    name: str
    value: float
    type: TelemetryType
    timestamp: datetime  # Required - but could default to now()
    labels: Dict[str, str] = None  # Should use field(default_factory=dict)
    metadata: Dict[str, Any] = None  # Should use field(default_factory=dict)
```

**Location**: `foundations/public_works_foundation/abstraction_contracts/telemetry_protocol.py:31-39`

### Migration Plan

#### Phase 2.1: Audit All Dataclasses (1 hour)
1. Find all dataclasses with required timestamp/created_at fields:
   ```bash
   grep -rn "@dataclass" --include="*.py" | xargs grep -l "timestamp\|created_at\|updated_at"
   ```
2. Review each dataclass to determine:
   - Which parameters truly need to be required
   - Which can have default factories
   - Impact of adding defaults (backward compatibility)

#### Phase 2.2: Update TelemetryData (30 min)
**File**: `foundations/public_works_foundation/abstraction_contracts/telemetry_protocol.py`

**Changes**:
```python
from dataclasses import dataclass, field

@dataclass
class TelemetryData:
    """Telemetry data point."""
    name: str
    value: float
    type: TelemetryType
    timestamp: datetime = field(default_factory=datetime.utcnow)  # Auto-generate
    labels: Dict[str, str] = field(default_factory=dict)  # Fix None default
    metadata: Dict[str, Any] = field(default_factory=dict)  # Fix None default
```

#### Phase 2.3: Update TraceSpan (30 min)
**File**: Same file

**Changes**:
```python
@dataclass
class TraceSpan:
    """Trace span data."""
    name: str
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.utcnow)  # Auto-generate
    end_time: Optional[datetime] = None
    attributes: Dict[str, Any] = field(default_factory=dict)  # Fix None default
    events: List[Dict[str, Any]] = field(default_factory=list)  # Fix None default
```

#### Phase 2.4: Find and Update Other Dataclasses (2-3 hours)
Search for other dataclasses with similar patterns:
- `SessionContext` - Check if `service_id` can be optional
- Any dataclasses with `timestamp`, `created_at`, `updated_at` fields
- Any dataclasses with `Dict` or `List` fields that use `None` instead of `field(default_factory=...)`

**Files to check**:
- `foundations/public_works_foundation/abstraction_contracts/*.py`
- `backend/business_enablement/**/*.py` (if any dataclasses exist)
- Any model files

#### Phase 2.5: Update Tests (1 hour)
- Update tests that manually create timestamps
- Verify backward compatibility (existing code should still work)
- Test that defaults are applied correctly

#### Phase 2.6: Update Usage (1 hour)
- Review code that creates these dataclasses
- Remove unnecessary timestamp creation where defaults are now used
- Keep explicit timestamps where needed for testing/time-travel scenarios

**Total Estimated Time**: 5-6 hours (~1 day)

---

## Issue 4: Method Naming Inconsistencies

### Current State Analysis

**Problem**: Legacy method names still in use instead of protocol-standard names:
- `retrieve_file()` vs `get_file()` (protocol uses `get_file`) - **INCONSISTENCY**
- `create_metadata()` vs `create_file()` - **NOT AN ISSUE** (metadata operations are intentionally different)
- `update_metadata()` vs `update_file()` - **NOT AN ISSUE** (metadata operations are intentionally different)
- `delete_metadata()` vs `delete_file()` - **NOT AN ISSUE** (metadata operations are intentionally different)

**Clarification**: Metadata operations (`create_metadata()`, `update_metadata()`, `delete_metadata()`) are intentionally different from file operations. They enable metadata-only workflows for clients who don't want their data exposed. These should NOT be renamed.

**Evidence** (Actual counts from codebase):
- **Legacy method definitions**: 40 occurrences
- **Protocol** (`file_management_protocol.py`): Defines `get_file()`, `create_file()`, `update_file()`, `delete_file()` (source of truth)
- **Content Steward** (`content_steward_service.py`): Uses `retrieve_file()` (legacy - 1 occurrence)
- **Supabase Metadata Adapter**: Uses `create_metadata()`, `update_metadata()`, `delete_metadata()` (legacy - 3 occurrences)
- **Other adapters**: Various legacy method names

**Files with Legacy Names**:
1. `backend/smart_city/services/content_steward/content_steward_service.py` - `retrieve_file()` → `get_file()`
2. `foundations/public_works_foundation/infrastructure_adapters/supabase_metadata_adapter.py` - `create_metadata()`, `update_metadata()`, `delete_metadata()` 
   - **NOTE**: These are INTENTIONALLY different from file operations (metadata-only operations for clients who don't want data exposed)
   - **Decision**: Keep these names as-is - they're not inconsistencies
3. Plus other adapter files (need to verify if they're file operations or metadata operations)

### Migration Plan

#### Phase 4.1: Audit All Method Names (1 hour)
1. Create mapping of legacy → standard names:
   ```bash
   # Find all legacy method definitions
   grep -rn "def retrieve_file\|def create_metadata\|def update_metadata\|def delete_metadata" --include="*.py"
   ```
2. Document:
   - Which classes implement legacy methods
   - Which classes use standard methods
   - Protocol definitions (source of truth)

#### Phase 4.2: Update Content Steward (1 hour)
**File**: `backend/smart_city/services/content_steward/content_steward_service.py`

**Changes**:
```python
# OLD
async def retrieve_file(self, file_id: str) -> Optional[Dict[str, Any]]:

# NEW
async def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve file via file_management infrastructure (SOA API).
    
    Note: Previously named retrieve_file() - now standardized to get_file().
    """
```

**Also update**:
- Method calls within the class
- Any references in docstrings
- Protocol implementation (if ContentSteward implements a protocol)

#### Phase 4.3: Verify Other Adapters (30 min)
**File**: `foundations/public_works_foundation/infrastructure_adapters/supabase_metadata_adapter.py`

**Decision**: 
- ✅ **CONFIRMED**: `create_metadata()`, `update_metadata()`, `delete_metadata()` are INTENTIONALLY different from file operations
- These enable metadata-only workflows for clients who don't want their data exposed
- **Action**: Keep these names as-is, document the distinction clearly

**Other adapters to check**:
- Review other adapter files to determine if they have file operations that should be renamed
- Distinguish between:
  - File operations → Should use `get_file()`, `create_file()`, etc.
  - Metadata-only operations → Can use `create_metadata()`, `update_metadata()`, etc.

#### Phase 4.4: Add Deprecation Warnings (1 hour)
For backward compatibility during migration:
```python
async def retrieve_file(self, file_id: str) -> Optional[Dict[str, Any]]:
    """
    DEPRECATED: Use get_file() instead.
    This method will be removed in a future version.
    """
    import warnings
    warnings.warn(
        "retrieve_file() is deprecated. Use get_file() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return await self.get_file(file_id)
```

#### Phase 4.5: Update All Callers (2-3 hours)
1. Find all callers of legacy methods:
   ```bash
   grep -rn "\.retrieve_file\|\.create_metadata\|\.update_metadata\|\.delete_metadata" --include="*.py"
   ```
2. Update each caller to use standard method names
3. Update tests

#### Phase 4.6: Remove Deprecated Methods (1 hour)
After migration period (e.g., 1-2 sprints):
- Remove deprecated method implementations
- Update documentation

**Total Estimated Time**: 5-7 hours (~1 day) - Reduced scope (metadata methods are intentional)

---

## Implementation Strategy

### Recommended Order

1. **Issue 2 (Dataclasses)** - Lowest risk, quick wins
   - Start here for momentum
   - Minimal functional impact
   - Easy to test

2. **Issue 4 (Method Names)** - Low risk, reduced scope
   - Well-defined target (protocol names)
   - Can use deprecation warnings for safety
   - Clear migration path
   - **Note**: Metadata methods are intentionally different - not part of this fix

3. **Issue 1 (Parameter Names)** - Medium risk, most occurrences
   - Largest scope (159 occurrences)
   - Requires careful coordination
   - Most impact on API consistency

### Phased Approach

**Week 1: Quick Wins**
- Day 1: Issue 2 (Dataclasses) - Complete
- Day 2: Issue 4 (Method Names) - Complete

**Week 2: Parameter Standardization**
- Day 1-2: Issue 1 (Parameter Names) - Complete
- Day 3: Testing and validation

### Risk Mitigation

1. **Backward Compatibility**:
   - Use deprecation warnings for method renames
   - Keep old parameter names as optional aliases initially
   - Gradual migration with fallbacks

2. **Testing**:
   - Run full test suite after each phase
   - Add integration tests for critical paths
   - Verify no functional regressions

3. **Documentation**:
   - Update API docs immediately
   - Document migration path
   - Add examples of new patterns

---

## Testing Strategy

### For Each Issue

**Issue 1 (Parameter Names)**:
- Test all orchestrator methods with `business_context`
- Test MCP server tools with `business_context`
- Verify service layer still works
- Integration tests for full flow

**Issue 2 (Dataclasses)**:
- Test dataclass creation with defaults
- Test explicit parameter override still works
- Verify backward compatibility
- Test edge cases (None values, etc.)

**Issue 4 (Method Names)**:
- Test new method names work
- Test deprecated methods still work (with warnings)
- Test protocol compliance
- Integration tests for file operations

### Test Checklist

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] No new warnings (except intentional deprecations)
- [ ] API documentation updated
- [ ] Code review completed
- [ ] Performance benchmarks (if applicable)

---

## Success Metrics

### Issue 1: Parameter Naming
- **Before**: 54 `context_data` occurrences (vs 227 `business_context`)
- **After**: 0 `context_data` occurrences (all use `business_context`)
- **Measure**: `grep -rn "context_data" backend/business_enablement/ --include="*.py" | wc -l` = 0

### Issue 2: Required Parameters
- **Before**: ~10-15 dataclasses with required timestamps
- **After**: All have default factories where appropriate
- **Measure**: All dataclasses reviewed and updated (verify with grep for required timestamps)

### Issue 4: Method Naming
- **Before**: 40 legacy method definitions
- **After**: All use protocol-standard names (deprecations allowed during transition)
- **Measure**: `grep -rn "def retrieve_file\|def create_metadata\|def update_metadata\|def delete_metadata" --include="*.py" | wc -l` = 0 (except deprecation wrappers)

---

## Rollback Plan

If issues arise:

1. **Git Revert**: Each phase committed separately for easy rollback
2. **Feature Flags**: Consider feature flags for gradual rollout (if needed)
3. **Deprecation Period**: Keep old names working during transition
4. **Documentation**: Clear migration guide for team

---

## Open Questions

1. ✅ **Issue 4**: `create_metadata()`/`update_metadata()`/`delete_metadata()` are intentionally different - **RESOLVED**
   - These enable metadata-only workflows for clients who don't want their data exposed
   - **Action**: Keep these names, document the distinction

2. **Issue 1**: Should we update protocol definitions to explicitly use `business_context`?
   - **Action**: Review protocols and update if needed

3. **Issue 2**: Are there any dataclasses where explicit timestamps are required for business logic?
   - **Action**: Review each dataclass individually

---

## Next Steps

1. **Review this plan** with team
2. **Answer open questions**
3. **Create tickets** for each phase
4. **Begin with Issue 2** (quickest win)
5. **Track progress** in this document

---

**Last Updated**: November 13, 2025  
**Status**: Ready for Review

