# Smart City Fixes Test Design

**Date:** December 11, 2025  
**Purpose:** Test design document for validating the 7 Smart City fixes and DIL SDK integration pattern

---

## Test Strategy

Since we haven't made changes to other realms (Business Enablement), we need to carefully design tests that:
1. **Test what we can test** - Smart City fixes that don't require Business Enablement changes
2. **Validate integration patterns** - DIL SDK usage patterns that will be used by Business Enablement
3. **Verify code paths exist** - Ensure workflow orchestration and event publishing code paths are present
4. **Test in isolation** - Test Smart City services independently without requiring orchestrator changes

---

## Test Coverage

### ✅ Fix 1: file_id Standardization + Original Filename Tracking
**Test:** `test_fix1_file_id_standardization()`
- Upload file via Content Steward
- Verify `file_id` is primary field in response
- Verify `original_filename` is tracked
- Verify `ui_name` is present
- Verify `uuid` is present for backward compatibility

**Expected Results:**
- Response includes `file_id` as primary field
- Response includes `original_filename` matching input
- Response includes `ui_name` for UI display

---

### ✅ Fix 5: Data Classification During Upload
**Test:** `test_fix5_data_classification()`
- Upload file with `tenant_id` (should be "client")
- Upload file without `tenant_id` (should be "platform")
- Verify `data_classification` is set automatically

**Expected Results:**
- Files with `tenant_id` are classified as "client"
- Files without `tenant_id` are classified as "platform"
- `data_classification` is always present in response

---

### ✅ Fix 6: Tenant Validation Enforcement
**Test:** `test_fix6_tenant_validation()`
- Upload file with valid tenant access
- Verify tenant validation code path exists
- Note: Full invalid tenant test would require mocking Security Guard

**Expected Results:**
- Valid tenant upload succeeds
- Tenant validation code path is executed

---

### ✅ Fix 2: Workflow Orchestration (Conductor Integration)
**Test:** `test_fix2_workflow_orchestration()`
- Upload file with `workflow_id` parameter
- Verify `workflow_id` is accepted
- Note: Full workflow state verification would require Conductor service

**Expected Results:**
- `workflow_id` parameter is accepted
- Workflow orchestration code path exists

---

### ✅ Fix 3: Event Publishing (Post Office Integration)
**Test:** `test_fix3_event_publishing()`
- Upload file (should trigger event publishing)
- Verify event publishing code path exists
- Note: Full event verification would require Post Office service and event subscription

**Expected Results:**
- Event publishing code path exists
- `file_uploaded` event should be published

---

### ✅ Fix 7: API Response Format Consistency
**Test:** `test_fix7_api_response_format()`
- Upload file via Content Steward
- Verify standardized response format:
  ```python
  {
      "success": bool,
      "data": { ... },
      "metadata": { ... }
  }
  ```

**Expected Results:**
- Response includes `success` field
- Response includes `data` field with actual response data
- Response includes `metadata` field with additional metadata

---

### ✅ Fix 4: Data Path Bootstrap Pattern
**Test:** `test_fix4_data_path_bootstrap()`
- Initialize City Manager
- Verify `data_path_bootstrap_module` exists
- Call `bootstrap_data_paths()`
- Verify validators are registered
- Verify Smart City services are validated

**Expected Results:**
- `data_path_bootstrap_module` exists
- `bootstrap_data_paths()` executes successfully
- Validators are registered
- Smart City services are validated

---

### ✅ DIL SDK Integration Pattern
**Test:** `test_dil_sdk_integration()`
- Initialize DIL SDK with Smart City services
- Test `upload_file()` via DIL SDK
- Test `get_file()` via DIL SDK
- Test `record_platform_event()` via DIL SDK

**Expected Results:**
- DIL SDK initializes successfully
- DIL SDK methods work correctly
- DIL SDK provides unified interface to Smart City services

---

### ✅ Complete Lifecycle Pattern
**Test:** `test_complete_lifecycle_pattern()`
- Simulate complete lifecycle from DIL SDK integration example:
  1. Upload file via DIL SDK
  2. Record platform event via DIL SDK
  3. Track lineage via DIL SDK

**Expected Results:**
- Complete lifecycle pattern works
- All steps execute successfully
- Pattern matches DIL SDK integration example

---

## Test Limitations

### What We Can't Test (Yet)
1. **Full Workflow Orchestration** - Requires Conductor service to be running and workflow state to be queryable
2. **Full Event Publishing** - Requires Post Office service to be running and event subscription mechanism
3. **Business Enablement Integration** - Requires Business Enablement orchestrators to be updated to use DIL SDK
4. **End-to-End Data Flow** - Requires all components (parse, metadata extraction, embeddings) to be implemented

### What We Can Test
1. ✅ **Code Paths Exist** - Verify workflow orchestration and event publishing code paths are present
2. ✅ **Parameter Acceptance** - Verify `workflow_id` parameter is accepted
3. ✅ **Response Formats** - Verify standardized response formats
4. ✅ **DIL SDK Pattern** - Verify DIL SDK can be initialized and used
5. ✅ **Data Classification** - Verify automatic data classification
6. ✅ **Tenant Validation** - Verify tenant validation code path exists
7. ✅ **file_id Standardization** - Verify file_id is primary field

---

## Test Execution

### Prerequisites
- Public Works Foundation initialized
- Curator Foundation initialized
- Smart City services initialized
- ArangoDB available (for some tests)
- Supabase available (for file storage)

### Running Tests
```bash
cd /home/founders/demoversion/symphainy_source
python3 scripts/test_smart_city_fixes_and_dil_sdk.py
```

### Expected Output
- Each test should print its name and status
- Tests should verify code paths exist and parameters are accepted
- Tests should not fail due to missing Business Enablement changes

---

## Next Steps

Once Business Enablement is updated:
1. **Add Full Workflow Tests** - Test actual workflow state updates via Conductor
2. **Add Full Event Tests** - Test actual event publishing and subscription via Post Office
3. **Add End-to-End Tests** - Test complete data lifecycle from upload to embeddings
4. **Add Integration Tests** - Test Business Enablement orchestrators using DIL SDK

---

## Test Results Interpretation

### ✅ Pass
- Code path exists
- Parameter is accepted
- Response format is correct
- DIL SDK works

### ⚠️ Partial Pass
- Code path exists but full functionality requires additional services
- Parameter is accepted but full verification requires integration

### ❌ Fail
- Code path missing
- Parameter not accepted
- Response format incorrect
- DIL SDK initialization fails

---

## Summary

This test suite validates that:
1. ✅ All 7 Smart City fixes are implemented
2. ✅ Code paths exist for workflow orchestration and event publishing
3. ✅ DIL SDK can be initialized and used
4. ✅ Response formats are standardized
5. ✅ Data classification and tenant validation work

The tests are designed to work **without** requiring Business Enablement changes, focusing on what we can validate now while establishing the patterns that Business Enablement will use.



