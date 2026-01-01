# Platform-Wide Patterns Audit - Fix Plan

**Date**: November 15, 2025  
**Status**: 🚧 Ready for Implementation

---

## Executive Summary

**Total Findings**: 45 (32 errors, 13 warnings)

The audit identified violations of architectural patterns across the platform. This document provides a prioritized plan to fix all issues.

---

## Findings Summary

| Pattern | Errors | Warnings | Total | Priority |
|---------|--------|----------|-------|----------|
| RealmServiceBase Usage | 14 | 0 | 14 | 🔴 High |
| Method Signature Alignment | 10 | 0 | 10 | 🔴 High |
| Public Works Abstraction Access | 7 | 0 | 7 | 🔴 High |
| Smart City Service Delegation | 0 | 13 | 13 | 🟡 Medium |
| Adapter Encapsulation | 1 | 0 | 1 | 🔴 High |

---

## Phase 1: Critical Errors (High Priority) 🔴

### 1.1 RealmServiceBase Usage - Direct Communication Foundation Access (14 errors)

**Files Affected**:
- `symphainy-platform/bases/realm_base.py` (6 errors)
- `symphainy-platform/bases/realm_service_base_old.py` (2 errors)
- `symphainy-platform/bases/realm_service_base.py` (4 errors)
- `symphainy-platform/bases/mixins/communication_mixin.py` (2 errors)

**Issues**:
- Direct `self.communication_foundation` access
- Should use Smart City services via `RealmServiceBase` helper methods

**Fix Strategy**:
1. **realm_base.py**: This is a base class - needs careful refactoring
   - Replace `self.communication_foundation.soa_client_abstraction` → Use `await self.get_post_office_api()`
   - Replace `self.communication_foundation.curator_foundation` → Use `await self.get_curator_api()`
   - Replace `self.communication_foundation.communication_abstraction` → Use appropriate Smart City service

2. **realm_service_base_old.py**: Archive or update
   - **Decision needed**: Is this file still used? If not, move to archive
   - If used, apply same fixes as realm_base.py

3. **realm_service_base.py**: Update to use helper methods
   - Replace direct communication_foundation access with helper methods

4. **communication_mixin.py**: Update mixin to use RealmServiceBase methods
   - Replace direct access with helper methods

**Estimated Effort**: 4-6 hours

---

### 1.2 Method Signature Alignment (10 errors)

**Files Affected**:
- `operations_orchestrator.py` (1 error - active)
- `legacy_orchestrators/operations_orchestrator.py` (2 errors - archive)
- `coexistence_analysis_service.py` (2 errors)
- `sop_builder_service.py` (3 errors)
- `workflow_conversion_service.py` (2 errors)

**Issues**:
- Using `librarian.store_document()` instead of `content_steward.process_upload()`

**Fix Strategy**:
1. **Active Files** (Priority):
   - `operations_orchestrator.py`: Replace `librarian.store_document()` → `content_steward.process_upload()`
   - `coexistence_analysis_service.py`: Replace all incorrect calls
   - `sop_builder_service.py`: Replace all incorrect calls
   - `workflow_conversion_service.py`: Replace all incorrect calls

2. **Archive Files** (Low Priority):
   - `legacy_orchestrators/operations_orchestrator.py`: Move to archive or fix if still referenced

**Code Pattern**:
```python
# ❌ BEFORE
await self.librarian.store_document(document_data)

# ✅ AFTER
content_steward = await self.get_content_steward_api()
await content_steward.process_upload(document_data)
```

**Estimated Effort**: 2-3 hours

---

### 1.3 Public Works Abstraction Access - Direct Adapter Instantiation (7 errors)

**Files Affected**:
- `file_management_registry.py` (1 error)
- `insights_analytics_composition_service.py` (2 errors)
- `communication_foundation_service.py` (2 errors)
- `websocket_adapter.py` (1 error)
- `pytesseract_ocr_adapter.py` (1 error - likely false positive)

**Issues**:
- Direct adapter instantiation instead of using abstractions via Platform Gateway
- Registries/composition services creating adapters

**Fix Strategy**:
1. **file_management_registry.py**:
   - **Check**: This might be the old registry file (we have `file_management_registry_gcs.py`)
   - If old, archive it
   - If active, remove adapter creation - should be exposure-only

2. **insights_analytics_composition_service.py**:
   - Remove adapter instantiation
   - Receive abstractions via dependency injection (from Public Works Foundation)

3. **communication_foundation_service.py**:
   - This is a foundation service - needs special handling
   - **Decision needed**: Should Communication Foundation create its own adapters, or use Public Works Foundation?
   - If using Public Works, inject abstractions instead of creating adapters

4. **websocket_adapter.py**:
   - If this is an adapter file creating another adapter, refactor to use dependency injection

5. **pytesseract_ocr_adapter.py**:
   - **Likely false positive** - adapters can import libraries
   - Verify: If it's creating another adapter internally, fix it

**Estimated Effort**: 3-4 hours

---

### 1.4 Adapter Encapsulation - Direct .client Access (1 error)

**Files Affected**:
- `di_container_service.py` (1 error)

**Issue**:
- Direct `.client` access instead of using adapter wrapper methods

**Fix Strategy**:
1. **di_container_service.py**:
   - Find the line with `.client` access
   - Replace with appropriate adapter wrapper method
   - If no wrapper method exists, add one to the adapter

**Code Pattern**:
```python
# ❌ BEFORE
result = self.adapter.client.some_method()

# ✅ AFTER
result = self.adapter.some_method()  # Use wrapper method
```

**Estimated Effort**: 30 minutes

---

## Phase 2: Warnings (Medium Priority) 🟡

### 2.1 Smart City Service Delegation - Custom File I/O (13 warnings)

**Files Affected**:
- `file_parser_service.py` (3 warnings)
- Archive files (10 warnings)

**Issues**:
- Using `open()` for file I/O instead of delegating to Smart City services

**Fix Strategy**:
1. **Active Files** (Priority):
   - `file_parser_service.py`: Replace `open()` calls with `RealmServiceBase.store_document()` or `content_steward.process_upload()`
   - **Note**: Some `open()` calls might be for temporary files - verify context

2. **Archive Files** (Low Priority):
   - Archive files can be left as-is or fixed if they're still referenced

**Code Pattern**:
```python
# ❌ BEFORE
with open(file_path, 'w') as f:
    f.write(data)

# ✅ AFTER
await self.store_document(data, metadata)
# OR
content_steward = await self.get_content_steward_api()
await content_steward.process_upload(file_data, metadata)
```

**Estimated Effort**: 2-3 hours

---

## Implementation Plan

### Step 1: Quick Wins (30 minutes)
- [ ] Fix adapter encapsulation issue in `di_container_service.py`

### Step 2: Method Signature Alignment (2-3 hours)
- [ ] Fix `operations_orchestrator.py`
- [ ] Fix `coexistence_analysis_service.py`
- [ ] Fix `sop_builder_service.py`
- [ ] Fix `workflow_conversion_service.py`
- [ ] Verify archive files (decide: fix or archive)

### Step 3: Public Works Abstraction Access (3-4 hours)
- [ ] **Archive `file_management_registry.py`** (old registry - violates pattern)
  - Move to archive directory
  - Verify no active references
- [ ] Fix `insights_analytics_composition_service.py`
- [ ] Fix `communication_foundation_service.py` (use Public Works Foundation)
- [ ] Fix `websocket_adapter.py`
- [ ] Verify `pytesseract_ocr_adapter.py` (likely false positive)

### Step 4: RealmServiceBase Usage (4-6 hours)
- [ ] Fix `realm_base.py` (careful - base class)
- [ ] Fix `realm_service_base.py`
- [ ] Fix `communication_mixin.py`
- [ ] **Archive `realm_service_base_old.py`** and update any references
  - Move to archive directory
  - Search for imports/references and update to use `realm_service_base.py`

### Step 5: Smart City Service Delegation (2-3 hours)
- [ ] Fix `file_parser_service.py` (verify context of open() calls)
- [ ] Review archive files (low priority)

---

## Architectural Decisions ✅ (RESOLVED)

1. **Communication Foundation Service**: ✅ **DECIDED**
   - **Decision**: Use Public Works Foundation for consistency
   - **Action**: Refactor `communication_foundation_service.py` to receive abstractions via dependency injection from Public Works Foundation

2. **realm_service_base_old.py**: ✅ **DECIDED**
   - **Decision**: Archive it and update any references to use `realm_service_base.py` instead
   - **Action**: 
     - Move `realm_service_base_old.py` to archive
     - Search for any imports/references and update them

3. **file_management_registry.py**: ✅ **DECIDED**
   - **Decision**: Archive the old `file_management_registry.py` (Supabase-only)
   - **Rationale**: 
     - `file_management_registry_gcs.py` is the correct registry (exposure-only, follows pattern)
     - `FileManagementAbstraction` already coordinates BOTH:
       - GCS adapter for file storage
       - Supabase adapter for file metadata (source of truth)
     - The abstraction handles the coordination - no need for separate registries
   - **Action**: Archive `file_management_registry.py` (it violates the pattern by creating adapters)

4. **Archive Files**: ✅ **DECIDED**
   - **Decision**: Leave archive files as-is unless they're still referenced
   - **Action**: If referenced, determine appropriate current reference or consider restoring/fixing

---

## Risk Assessment

### Low Risk
- Adapter encapsulation fix (single file, isolated)
- Method signature alignment (straightforward replacements)

### Medium Risk
- Public Works abstraction access (may require architectural decisions)
- Smart City service delegation (need to verify context of open() calls)

### High Risk
- RealmServiceBase usage (base classes - changes affect many services)
  - **Mitigation**: Test thoroughly, update tests first

---

## Testing Strategy

1. **Unit Tests**: Update tests for each file before fixing
2. **Integration Tests**: Run integration tests after each phase
3. **Smoke Tests**: Quick verification after each fix
4. **Regression Tests**: Full test suite after all fixes

---

## Success Criteria

- [ ] All 32 errors fixed
- [ ] All 13 warnings addressed (fixed or documented as acceptable)
- [ ] All tests passing
- [ ] No regressions introduced
- [ ] Architectural patterns consistently applied

---

## Estimated Total Effort

- **Phase 1 (Critical Errors)**: 10-14 hours
- **Phase 2 (Warnings)**: 2-3 hours
- **Testing & Verification**: 4-6 hours
- **Total**: 16-23 hours

---

## Next Steps

1. **Review this plan** with the team
2. **Make architectural decisions** (Communication Foundation, archive files)
3. **Start with Quick Wins** (Step 1)
4. **Proceed phase by phase** with testing at each step
5. **Document any deviations** from the plan

---

**Last Updated**: November 15, 2025

