# Business Enablement Violations Fix Plan

## Violation Summary

**Total Active Code Violations**: 65
- **Utility Violations**: 59 (logging imports and calls)
- **Foundation Import Violations**: 3 (protocol/contract imports)
- **Smart City Import Violations**: 0 (all in archive)
- **DI Container Violations**: 3

## Fix Strategy

### Phase 1: Utility Logging Violations (59 violations)
**Pattern**: Replace `import logging` and `logging.getLogger()` with DI Container access

**Files Affected**:
- Delivery Manager modules (3 files)
- MVP Pillar Orchestrator agents (multiple files)
- Enabling services (multiple files)
- Agent classes (multiple files)

**Fix Approach**:
1. Remove `import logging` statements
2. Replace `logging.getLogger()` with `self.service.di_container.get_logger()` or `self.di_container.get_logger()`
3. Update module-level logger initialization to use DI Container

### Phase 2: Foundation Import Violations (3 violations)
**Files**:
1. `file_parser_service.py:224` - `DocumentProcessingRequest` protocol import
2. `workflow_manager_service.py:22` - Workflow protocol imports
3. `content_analysis_orchestrator.py:413` - `file_utils` import

**Analysis Needed**:
- Protocol/contract imports: Are these runtime or type hints?
- `file_utils` import: Should be replaced with Platform Gateway or Smart City SOA API

**Fix Approach**:
1. Check if protocol imports can be moved to TYPE_CHECKING blocks
2. Replace `file_utils` import with appropriate abstraction access
3. If protocols are runtime, consider moving to shared location

### Phase 3: DI Container Violations (3 violations)
**Need to identify specific violations**

## Implementation Order

1. ✅ **Analyze violations** - DONE
2. **Fix utility logging** - Create script similar to Smart City fix
3. **Fix foundation imports** - Manual fixes (need architectural decisions)
4. **Fix DI Container violations** - Manual fixes
5. **Re-run validator** - Verify all fixes
6. **Strategize test suite** - After violations fixed

