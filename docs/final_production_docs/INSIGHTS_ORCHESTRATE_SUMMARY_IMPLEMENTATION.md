# Insights orchestrate_summary Implementation

**Date:** January 2025  
**Status:** ✅ **IMPLEMENTED**  
**Purpose:** Implement `orchestrate_summary()` method in InsightsJourneyOrchestrator to select the best output

---

## ✅ Implementation Complete

### Method: `orchestrate_summary()`
**File:** `symphainy-platform/backend/journey/orchestrators/insights_journey_orchestrator/insights_journey_orchestrator.py`

**Purpose:** Select the most appropriate and interesting output from available analyses for a given session.

---

## 🎯 Selection Priority

The method selects outputs based on priority (most actionable/interesting first):

1. **Data Mappings** (Highest Priority)
   - Most actionable output
   - Shows transformation logic
   - Demonstrates data integration capabilities

2. **AAR (After Action Review)**
   - Comprehensive insights
   - Narrative format
   - Strategic value

3. **Structured Insights**
   - Data-driven
   - Charts, trends, metrics
   - Quantitative analysis

4. **Unstructured Insights** (Lowest Priority)
   - Narrative summaries
   - Key findings
   - Qualitative analysis

---

## 🔍 Implementation Details

### Query Strategy

The method queries available outputs from two sources:

1. **Librarian Service**
   - Queries content by session_id
   - Categorizes content by type (mapping, AAR, structured, unstructured)
   - Extracts analysis results from content metadata

2. **ContentSteward Service**
   - Queries files with analysis results
   - Checks file metadata for analysis results
   - Extracts mapping rules, AAR reports, structured/unstructured analysis results

### Selection Logic

1. Query both Librarian and ContentSteward for available outputs
2. Categorize outputs by type:
   - `data_mapping`: Mapping rules, transformation logic
   - `aar`: After Action Review reports
   - `structured_insights`: EDA, VARK, business summary results
   - `unstructured_insights`: Unstructured analysis results
3. Select the first available output based on priority order
4. Return selected output with metadata

---

## 📊 Return Structure

### Success Case
```json
{
  "success": true,
  "output_type": "data_mapping",
  "output": {
    "type": "data_mapping",
    "file_id": "...",
    "mapping_rules": [...],
    "analysis_results": {...}
  },
  "summary": {
    // Same as output (alias for compatibility)
  },
  "metadata": {
    "session_id": "...",
    "selected_at": "2026-01-01T00:00:00Z",
    "available_types": ["data_mapping", "structured_insights"],
    "priority_order": ["data_mapping", "aar", "structured_insights", "unstructured_insights"]
  }
}
```

### No Outputs Available
```json
{
  "success": false,
  "error": "No analysis outputs available for this session",
  "output_type": null,
  "output": null,
  "summary": {},
  "metadata": {
    "session_id": "...",
    "selected_at": "2026-01-01T00:00:00Z",
    "available_types": [],
    "priority_order": ["data_mapping", "aar", "structured_insights", "unstructured_insights"]
  }
}
```

---

## 🔧 Integration with Insights Pillar Summary

The `orchestrate_insights_pillar_summary()` method in `InsightsSolutionOrchestratorService` now calls this method:

```python
if hasattr(self.insights_journey_orchestrator, 'orchestrate_summary'):
    summary_result = await self.insights_journey_orchestrator.orchestrate_summary(
        session_id=session_id,
        user_context=enhanced_user_context
    )
    if summary_result and summary_result.get("success"):
        selected_output = summary_result.get("summary") or summary_result.get("output")
```

---

## 🚀 Future Enhancements

### 1. Enhanced Query Methods
**Current:** Uses placeholder methods (`query_content_by_session`, `list_files_with_analyses`)

**Enhancement:** Implement actual query methods in Librarian and ContentSteward services:
- `LibrarianService.query_content_by_session(session_id, user_context)`
- `ContentStewardService.list_files_with_analyses(session_id, user_context)`

### 2. Caching
**Enhancement:** Cache selected outputs to avoid re-querying on every summary request

### 3. Scoring System
**Enhancement:** Instead of simple priority order, use a scoring system that considers:
- Recency (prefer newer analyses)
- Completeness (prefer complete analyses)
- User preferences (if available)
- Analysis quality scores

### 4. Multiple Outputs
**Enhancement:** Return top N outputs instead of just the best one, allowing frontend to showcase multiple insights

---

## ✅ Success Criteria

- ✅ Method implemented in `InsightsJourneyOrchestrator`
- ✅ Priority-based selection logic
- ✅ Queries both Librarian and ContentSteward
- ✅ Returns structured output with metadata
- ✅ Integrated with `orchestrate_insights_pillar_summary()`
- ⏸️ Query methods in Librarian/ContentSteward may need implementation (currently placeholders)

---

## 📝 Notes

- The method uses placeholder API calls (`query_content_by_session`, `list_files_with_analyses`) that may need to be implemented in the actual services
- The method gracefully handles missing services and returns appropriate error messages
- The selection logic is deterministic (always selects the same output for the same inputs)
- The method logs selection decisions for debugging

---

**Last Updated:** January 2025  
**Status:** ✅ **IMPLEMENTED - READY FOR TESTING**



