# Insights Pillar Backend - Quick Reference

**Status:** ✅ Production-Ready  
**Phase:** 1A & 2A Complete  
**Next:** Phase 3 - Frontend Implementation

---

## 🚀 Quick Start

### **Testing the API**

```bash
# Start backend server
cd symphainy-platform/backend
python3 main.py

# API available at: http://localhost:8000
```

### **Example Request**

```bash
# Analyze structured content
curl -X POST http://localhost:8000/api/insights-pillar/analyze-content-for-insights \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "file",
    "file_id": "test_file_123",
    "content_type": "structured",
    "analysis_options": {
      "include_visualizations": true,
      "include_tabular_summary": true
    }
  }'
```

---

## 📂 File Locations

### **Orchestrator** (`insights_orchestrator.py`)
```
symphainy-platform/backend/business_enablement/
  business_orchestrator/use_cases/mvp/insights_orchestrator/
    ├─ insights_orchestrator.py          (Enhanced orchestrator)
    └─ workflows/
       ├─ structured_analysis_workflow.py
       ├─ unstructured_analysis_workflow.py
       └─ hybrid_analysis_workflow.py
```

### **Semantic API** (`insights_pillar_router.py`)
```
symphainy-platform/backend/experience/api/semantic/
  └─ insights_pillar_router.py           (9 endpoints)
```

### **Registration** (`main_api.py`)
```
symphainy-platform/backend/experience/api/
  └─ main_api.py                         (Already registered)
```

---

## 🎯 Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/insights-pillar/analyze-content-for-insights` | POST | Main analysis |
| `/api/insights-pillar/query-analysis-results` | POST | NLP queries |
| `/api/insights-pillar/get-available-content-metadata` | GET | List metadata |
| `/api/insights-pillar/validate-content-metadata-for-insights` | POST | Validate metadata |
| `/api/insights-pillar/get-analysis-results/{id}` | GET | Retrieve analysis |
| `/api/insights-pillar/list-user-analyses` | GET | Analysis history |
| `/api/insights-pillar/health` | GET | Health check |

---

## 🔧 Key Methods

### **Orchestrator Methods**

```python
# Main analysis method
await insights_orchestrator.analyze_content_for_insights(
    source_type="file",  # or "content_metadata"
    file_id="abc123",
    content_type="structured",  # or "unstructured" or "hybrid"
    analysis_options={
        "include_visualizations": True,
        "include_tabular_summary": True,
        "aar_specific_analysis": False
    }
)

# NLP query method
await insights_orchestrator.query_analysis_results(
    query="Show me accounts over 90 days late",
    analysis_id="analysis_123"
)

# Retrieve cached results
await insights_orchestrator.get_analysis_results("analysis_123")

# List analyses
await insights_orchestrator.list_user_analyses(limit=20, offset=0)
```

---

## 📊 Response Structure

### **Analysis Response**

```json
{
  "success": true,
  "analysis_id": "analysis_1731331200_abc12345",
  "summary": {
    "textual": "Business narrative summary...",
    "tabular": {
      "columns": ["Metric", "Value"],
      "rows": [["Total Records", 100], ["Average", 42.5]],
      "summary_stats": {
        "mean": {"Value": 42.5},
        "total_rows": 100
      }
    },
    "visualizations": [
      {
        "visualization_id": "viz_001",
        "chart_type": "bar",
        "vega_lite_spec": {...},
        "rationale": "Bar chart shows distribution..."
      }
    ]
  },
  "insights": [
    {
      "insight_id": "insight_abc",
      "type": "trend",
      "description": "Key finding...",
      "confidence": 0.85,
      "recommendations": ["Recommendation 1"]
    }
  ],
  "aar_analysis": {  // Optional (when aar_specific_analysis=true)
    "lessons_learned": [...],
    "risks": [...],
    "recommendations": [...],
    "timeline": [...]
  },
  "metadata": {
    "content_type": "structured",
    "analysis_timestamp": "2025-11-11T12:00:00Z",
    "source_info": {
      "type": "file",
      "id": "abc123"
    }
  }
}
```

---

## ⚙️ Configuration

### **Accessing the Orchestrator**

```python
# From semantic router
business_orchestrator = get_business_orchestrator()
insights_orchestrator = business_orchestrator.insights_orchestrator

# From business orchestrator
insights_orchestrator = self.business_orchestrator.insights_orchestrator
```

### **Accessing Enabling Services**

```python
# Services are accessed via business_orchestrator
data_analyzer = self.business_orchestrator.data_analyzer_service
visualization_engine = self.business_orchestrator.visualization_engine_service
metrics_calculator = self.business_orchestrator.metrics_calculator_service
```

---

## 🔍 Troubleshooting

### **Common Issues**

**Issue:** "Insights orchestrator not available"
- **Solution:** Ensure `insights_orchestrator` is initialized in `business_orchestrator`

**Issue:** "Analysis not found"
- **Solution:** Analysis ID may have expired from cache (in-memory only)

**Issue:** "Service not available"
- **Solution:** Check enabling service initialization in business_orchestrator

### **Logging**

```python
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # For detailed logs
```

---

## 📝 TODO Items

### **Items with Placeholder Implementations**

1. **NLP Query Processing** (`query-analysis-results`)
   - Location: `insights_orchestrator.py:query_analysis_results()`
   - TODO: Implement actual natural language understanding

2. **ArangoDB Integration** (`get-available-content-metadata`)
   - Location: `insights_pillar_router.py:get_available_content_metadata()`
   - TODO: Query ArangoDB via Public Works abstractions

3. **Validation Logic** (`validate-content-metadata-for-insights`)
   - Location: `insights_pillar_router.py:validate_content_metadata_for_insights()`
   - TODO: Implement quality assessment

4. **Report Generation** (`export-analysis-report`)
   - Location: `insights_pillar_router.py:export_analysis_report()`
   - TODO: Implement PDF/DOCX/CSV generation

5. **Data Retrieval** (workflows)
   - Location: All workflow `_get_data()` methods
   - TODO: Implement actual DataSteward/Librarian calls

6. **Service Integration** (workflows)
   - Location: All workflow analysis methods
   - TODO: Connect to actual InsightsGeneratorService, APGProcessorService

---

## 🎯 Frontend Integration Guide

### **Step 1: Install API Client**

```typescript
// lib/api/insightsPillarApi.ts
export async function analyzeContentForInsights(request: AnalyzeContentRequest) {
  const response = await api.post(
    '/api/insights-pillar/analyze-content-for-insights',
    request
  );
  return response.data;
}
```

### **Step 2: Call from Component**

```typescript
const handleAnalyze = async () => {
  const result = await analyzeContentForInsights({
    source_type: 'file',
    file_id: selectedFileId,
    content_type: 'structured',
    analysis_options: {
      include_visualizations: true,
      include_tabular_summary: true
    }
  });
  
  // Display 3-way summary
  setAnalysisResult(result);
};
```

### **Step 3: Render Results**

```typescript
<InsightsSummaryDisplay
  textual={result.summary.textual}
  tabular={result.summary.tabular}
  visualizations={result.summary.visualizations}
/>
```

---

## 📚 Documentation

- `API_CONTRACT_INSIGHTS_PILLAR.md` - Complete API specification
- `PHASE_1A_2A_IMPLEMENTATION_COMPLETE.md` - Implementation summary
- `INSIGHTS_PILLAR_REFACTORING_PLAN.md` - Target UX specification
- `INSIGHTS_PILLAR_INTEGRATED_REFACTORING_PLAN.md` - Overall plan

---

## ✅ Ready for Phase 3!

**Backend is complete and functional. Frontend development can begin immediately!** 🚀



