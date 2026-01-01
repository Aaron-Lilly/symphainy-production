# Infrastructure Abstractions - Batch Processing Plan

**Date:** December 20, 2024  
**Status:** 📋 **READY FOR BATCH PROCESSING**

---

## Progress Summary

### **Completed: 2/47 abstractions** ✅

1. ✅ **file_management_abstraction.py** - COMPLETE
   - Constructor updated with `di_container`
   - All 14 async methods updated with error handling and telemetry
   - Foundation service updated

2. ✅ **content_metadata_abstraction.py** - COMPLETE
   - Constructor updated with `di_container`
   - All 19 async methods updated with error handling and telemetry
   - Foundation service updated

### **Remaining: 45/47 abstractions**

---

## Pattern Confirmed

The pattern is now fully established and tested on 2 complete files:

1. **Constructor**: Add `di_container=None`, `service_name`, logger from DI container
2. **Success Path**: Add telemetry before return
3. **Error Path**: Add error handler with telemetry in exception blocks
4. **No Security/Tenant**: Validation stays at composition service level

---

## Batch Processing Strategy

### **Approach: Small Batches with Review**

Given the complexity and need for careful changes:

1. **Use helper script for analysis** - Shows what needs updating
2. **Process 2-3 files at a time** - Small batches for review
3. **Manual updates** - Use script as guide, apply changes manually
4. **Verify each batch** - Run lints and tests before proceeding

### **Helper Script Usage**

```bash
# Analyze a file
python3 scripts/update_abstraction_utilities.py <file> 

# Shows:
# - Has DI Container: Yes/No
# - Async Methods: count
# - Methods needing updates: list
```

---

## Next Batch Recommendations

### **Batch 1: Similar Abstractions (3 files)**
- `content_analysis_abstraction.py` - Similar to content_metadata
- `content_insights_abstraction.py` - Similar pattern
- `content_schema_abstraction.py` - Similar pattern

### **Batch 2: LLM-Related (3 files)**
- `llm_abstraction.py` - Core LLM operations
- `llm_caching_abstraction.py` - Caching operations
- `llm_rate_limiting_abstraction.py` - Rate limiting

### **Batch 3: Document Processing (3 files)**
- `document_intelligence_abstraction.py`
- `text_extraction_abstraction.py`
- `table_extraction_abstraction.py`

### **Continue in batches of 2-3 files...**

---

## Files Already with DI Container (Skip)

These 7 files already have DI container support:
- ✅ `policy_abstraction.py`
- ✅ `tool_storage_abstraction.py`
- ✅ `telemetry_abstraction.py`
- ✅ `health_abstraction.py`
- ✅ `alert_management_abstraction.py`
- ✅ `session_abstraction.py`
- ✅ `service_discovery_abstraction.py`

**Note**: Still need to verify these have error handling and telemetry in all methods.

---

## Estimated Remaining Work

- **45 abstractions** × ~10 methods each = ~450 method updates
- **With careful batching**: ~15-20 hours
- **Foundation service updates**: ~2 hours
- **Total**: ~17-22 hours

---

## Next Steps

1. ✅ Pattern established (2 files complete)
2. ⏭️ Process Batch 1 (3 similar abstractions)
3. ⏭️ Review and verify Batch 1
4. ⏭️ Continue with remaining batches
5. ⏭️ Update foundation service for each batch

---

**Status:** 📋 **READY FOR BATCH PROCESSING**












