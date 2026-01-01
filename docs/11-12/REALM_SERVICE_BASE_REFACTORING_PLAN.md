# RealmServiceBase Refactoring Plan

## Overview
Complete refactoring of `RealmServiceBase` to fix incorrect Smart City service method calls and architectural issues.

## Issues to Fix

### 1. ✅ `search_documents()` → `search_knowledge()` (18 usages)
**Current:** `librarian.search_documents(query)`  
**Fix:** `librarian.search_knowledge(query, filters=None)`  
**Impact:** Simple rename, update callers

### 2. ✅ `classify_content()` → Remove (0 usages)
**Current:** `content_steward.classify_content(content, type)`  
**Fix:** Remove method entirely  
**Impact:** None (unused)

### 3. ✅ `enrich_metadata()` → Remove (0 usages)
**Current:** `content_steward.enrich_metadata(content_id, type)`  
**Fix:** Remove method entirely  
**Impact:** None (unused)

### 4. ✅ `validate_data()` → `validate_schema()` (18 usages)
**Current:** `data_steward.validate_data(data, validation_rules)`  
**Fix:** `data_steward.validate_schema(schema_data)`  
**Impact:** Need to convert parameters to schema_data dict structure

### 5. ✅ `transform_data()` → Remove (17 usages)
**Current:** `data_steward.transform_data(data, transformation_rules)`  
**Fix:** Remove method entirely  
**Impact:** Fix recursive call bug in TransformationEngineService

### 6. ✅ `track_data_lineage()` → `record_lineage()` (37 usages)
**Current:** `data_steward.track_lineage(source, destination, transformation)`  
**Fix:** `data_steward.record_lineage(lineage_data)`  
**Impact:** Convert parameters to lineage_data dict structure

## Implementation Steps

### Phase 1: Fix RealmServiceBase Methods
1. Update `search_documents()` → `search_knowledge()`
2. Remove `classify_content()`
3. Remove `enrich_metadata()`
4. Update `validate_data()` → `validate_schema()` with parameter conversion
5. Remove `transform_data()`
6. Update `track_data_lineage()` → `record_lineage()` with parameter conversion

### Phase 2: Fix TransformationEngineService
1. Fix recursive call bug (line 118)
2. Create `_perform_transformation()` helper method
3. Update to use internal helpers

### Phase 3: Update Callers
1. Search for all usages of each method
2. Update callers to match new signatures
3. Test to ensure no regressions

## Risk Assessment
- **High Risk:** `track_data_lineage()` (37 usages) - most critical
- **Medium Risk:** `validate_data()` (18 usages), `search_documents()` (18 usages)
- **Low Risk:** `transform_data()` (17 usages, but self-contained), `classify_content()` (0), `enrich_metadata()` (0)

## Testing Strategy
1. Run existing tests to establish baseline
2. Fix methods one at a time
3. Update callers incrementally
4. Run tests after each change
5. Verify no regressions






