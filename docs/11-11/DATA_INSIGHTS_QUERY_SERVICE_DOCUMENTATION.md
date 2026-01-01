# Data Insights Query Service Documentation

## Overview

**DataInsightsQueryService** enables natural language querying of analysis results, allowing users to ask questions about their data insights conversationally.

## Architecture

```
User Query ("What are the top 5 revenue drivers?")
    ↓
Frontend: InsightsAPIManager.queryAnalysisResults()
    ↓
Backend API: /api/semantic/insights/query-analysis-results
    ↓
InsightsOrchestrator.query_analysis_results()
    ↓
DataInsightsQueryService.process_query()
    ↓ (rule-based processing)
[Result returned: table/chart/text with explanation]
```

### Service Layer

**Location**: `symphainy-platform/backend/business_enablement/enabling_services/data_insights_query_service/`

**Purpose**: Enabling service for processing NLP queries about data insights

**Integration**: 
- Used by `InsightsOrchestrator` for semantic API method `query_analysis_results()`
- Exposed as MCP tool `query_data_insights` via `InsightsMCPServer`

## Query Processing Approach

### Phase 1: Rule-Based (Current)

The service uses **pattern matching** with 15+ predefined query patterns:

1. **Top/Bottom N**: "What are the top 5 items?"
2. **Chart Requests**: "Show me a chart of revenue"
3. **Trend Analysis**: "What trends are increasing?"
4. **Filtering**: "Show me accounts over 90 days late"
5. **Summarization**: "Summarize the key findings"
6. **Metric Lookup**: "What is the revenue for Q4?"
7. **Comparison**: "Compare Q1 vs Q2"
8. **Recommendations**: "What are the high-priority recommendations?"
9. **AAR Queries**: "Show me lessons learned" (Navy AAR reports)
10. **Count Queries**: "How many accounts are late?"
11. **Average Queries**: "What's the average response time?"

### Phase 2: LLM Fallback (Future)

For queries that don't match patterns (confidence < 0.7), the service can fall back to an LLM for flexible processing.

## Query Patterns

### Pattern Examples

| Pattern Type | Example Query | Response Type |
|-------------|---------------|---------------|
| Top N | "What are the top 3 revenue drivers?" | Table |
| Bottom N | "Show me the bottom 5 performers" | Table |
| Chart | "Create a chart of profit margins" | Chart (Recharts) |
| Summarize | "Give me a summary" | Text |
| Recommendations | "What recommendations do you have?" | Table |
| AAR Lessons | "What lessons were learned?" | Table |
| AAR Risks | "Show me identified risks" | Table |
| AAR Timeline | "Display the timeline" | Table |

## API Integration

### Frontend API Call

```typescript
import { queryAnalysisResults } from '@/lib/api/insights';

const result = await queryAnalysisResults({
  query: "What are the top 5 items?",
  analysis_id: "analysis_123456",
  query_type: "auto"  // or 'table', 'chart', 'summary'
});

// Response
{
  success: true,
  query_id: "query_1699700000_analysis1",
  result: {
    type: "table",  // or 'chart', 'text', 'insight'
    data: {
      columns: ["Name", "Revenue", "Growth"],
      rows: [
        ["Product A", "$1.2M", "15%"],
        ["Product B", "$980K", "8%"],
        // ...
      ]
    },
    explanation: "Here are the top 5 items, sorted by Revenue:",
    confidence: 0.85
  },
  follow_up_suggestions: [
    "Show me the bottom performers",
    "Create a chart of this data",
    "What recommendations do you have?"
  ],
  metadata: {
    intent: "top_n_query",
    confidence: 0.9,
    analysis_id: "analysis_123456",
    processor: "rule_based"
  }
}
```

### Backend API Endpoint

```python
# File: symphainy-platform/backend/experience/api/semantic/insights_pillar_router.py

@insights_router.post("/query-analysis-results")
async def query_analysis_results(request: QueryAnalysisRequest):
    """
    POST /api/semantic/insights/query-analysis-results
    
    Process natural language query about analysis results.
    """
    orchestrator = await get_insights_orchestrator()
    result = await orchestrator.query_analysis_results(
        query=request.query,
        analysis_id=request.analysis_id,
        query_type=request.query_type
    )
    return result
```

## MCP Tool Integration

The service is exposed as an **MCP tool** for agent consumption:

### Tool Registration

```python
# File: symphainy-platform/backend/business_enablement/business_orchestrator/
#       use_cases/mvp/insights_orchestrator/mcp_server/insights_mcp_server.py

self.register_tool(
    name="query_data_insights",
    description="Process natural language query about analysis results. "
                "Ask questions like 'What are the top 3 revenue drivers?' "
                "or 'Show me a chart of profit margins'.",
    handler=self._query_data_insights_tool,
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language query"
            },
            "analysis_id": {
                "type": "string",
                "description": "ID of the analysis to query against"
            },
            "query_type": {
                "type": "string",
                "enum": ["table", "chart", "summary", "auto"],
                "description": "Preferred response type"
            }
        },
        "required": ["query", "analysis_id"]
    }
)
```

### Tool Usage (by agents)

```python
# Hypothetical agent usage
result = await mcp_client.call_tool(
    server="insights_mcp",
    tool="query_data_insights",
    parameters={
        "query": "What were the top 3 items?",
        "analysis_id": "analysis_123456",
        "query_type": "auto"
    }
)
```

## Response Types

### 1. Table Response

Used for: Top N, recommendations, AAR sections, comparisons

```python
{
    "type": "table",
    "data": {
        "columns": ["Column1", "Column2", "Column3"],
        "rows": [
            ["Value1", "Value2", "Value3"],
            ["Value4", "Value5", "Value6"]
        ]
    },
    "explanation": "Here are the results:",
    "confidence": 0.85
}
```

### 2. Chart Response

Used for: Visualization requests, trend analysis

```python
{
    "type": "chart",
    "data": {
        "visualization_id": "query_viz_abc123",
        "chart_type": "bar",  # 'bar' | 'line' | 'pie' | 'area'
        "library": "recharts",
        "title": "Revenue Chart",
        "rationale": "Bar chart showing revenue distribution",
        "chart_data": [
            {"name": "Q1", "value": 100},
            {"name": "Q2", "value": 120},
            {"name": "Q3", "value": 150}
        ],
        "x_axis_key": "name",
        "data_key": "value",
        "colors": ["#3b82f6"]
    },
    "explanation": "I've generated a bar chart showing revenue:",
    "confidence": 0.8
}
```

### 3. Text Response

Used for: Summaries, general questions, errors

```python
{
    "type": "text",
    "data": None,
    "explanation": "Here's the analysis summary: [textual narrative]",
    "confidence": 0.95
}
```

### 4. Insight Response

Used for: Specific insight extraction (future)

```python
{
    "type": "insight",
    "data": {
        "insight_type": "pattern",
        "insight": "Revenue has grown 15% QoQ for 3 consecutive quarters",
        "impact": "high",
        "recommendations": [...]
    },
    "explanation": "I've identified a key pattern in your data:",
    "confidence": 0.88
}
```

## Query Intent Detection

The service uses **regex pattern matching** to detect user intent:

```python
QUERY_PATTERNS = {
    r"(?:top|highest|best)\s+(\d+)\s+(.+)": "top_n_query",
    r"(?:show|create)\s+(?:a\s+)?chart\s+(?:of\s+)?(.+)": "chart_request",
    r"(?:summarize|summary of)\s+(.+)": "summarize_section",
    # ... 15+ patterns total
}
```

### Confidence Scoring

- **High confidence (≥ 0.7)**: Use rule-based processor
- **Low confidence (< 0.7)**: Fall back to LLM (if available)

## Follow-Up Suggestions

The service generates contextual follow-up suggestions based on:

1. **Available data**: If tabular data exists → suggest "top N" queries
2. **Visualizations**: If charts exist → suggest "Show me a chart"
3. **Insights**: If insights exist → suggest "What recommendations?"
4. **AAR analysis**: If AAR exists → suggest AAR-specific queries
5. **Intent**: Based on current query intent

Example:

```python
follow_up_suggestions: [
    "What are the top 5 items?",
    "Show me a chart of the data",
    "What recommendations do you have?"
]
```

## Error Handling

### Analysis Not Found

```python
{
    "success": False,
    "error": "Analysis not found: analysis_123456",
    "timestamp": "2025-11-11T12:00:00Z"
}
```

### Query Processing Failed

```python
{
    "success": False,
    "error": "Query processing failed",
    "error_details": "ValueError: Unable to parse query",
    "timestamp": "2025-11-11T12:00:00Z"
}
```

## Analysis Cache

The service relies on the **orchestrator's analysis cache** to retrieve results:

```python
# In InsightsOrchestrator
self.analysis_cache = {}  # Dict[analysis_id, analysis_result]

# Store after analysis
self.analysis_cache[analysis_id] = analysis_result

# Retrieve for query
cached_analysis = self.analysis_cache.get(analysis_id)
```

### Cache Structure

```python
cached_analysis = {
    "analysis_id": "analysis_123456",
    "summary": {
        "textual": "Narrative summary...",
        "tabular": {
            "columns": [...],
            "rows": [...],
            "summary_stats": {...}
        },
        "visualizations": [...]
    },
    "insights": [...],
    "aar_analysis": {  # Optional, for Navy AAR reports
        "lessons_learned": [...],
        "risks": [...],
        "timeline": [...]
    },
    "metadata": {...}
}
```

## Usage Examples

### Example 1: Top N Query

**User**: "What are the top 3 revenue drivers?"

**Processing**:
1. Matches pattern: `r"(?:top|highest|best)\s+(\d+)\s+(.+)"`
2. Intent: `top_n_query`
3. Entities: `["3", "revenue drivers"]`
4. Handler: `_handle_top_n_query()`
5. Extracts tabular data
6. Sorts by last column (assumes numeric)
7. Returns top 3 rows

**Response**:
```python
{
    "type": "table",
    "data": {
        "columns": ["Category", "Revenue", "Growth"],
        "rows": [
            ["Product A", "$1.2M", "15%"],
            ["Product B", "$980K", "8%"],
            ["Product C", "$850K", "12%"]
        ]
    },
    "explanation": "Here are the top 3 revenue drivers, sorted by Revenue:",
    "confidence": 0.85
}
```

### Example 2: Chart Request

**User**: "Show me a chart of quarterly profit"

**Processing**:
1. Matches pattern: `r"(?:show|create)\s+(?:a\s+)?chart\s+(?:of\s+)?(.+)"`
2. Intent: `chart_request`
3. Entities: `["quarterly profit"]`
4. Handler: `_handle_chart_request()`
5. Checks for existing visualizations
6. Or generates from tabular data
7. Returns Recharts-compatible spec

**Response**:
```python
{
    "type": "chart",
    "data": {
        "chart_type": "bar",
        "library": "recharts",
        "title": "Quarterly Profit Chart",
        "chart_data": [
            {"name": "Q1", "value": 100},
            {"name": "Q2", "value": 120},
            {"name": "Q3", "value": 150},
            {"name": "Q4", "value": 130}
        ],
        "x_axis_key": "name",
        "data_key": "value",
        "colors": ["#3b82f6"]
    },
    "explanation": "I've generated a bar chart showing quarterly profit:",
    "confidence": 0.8
}
```

### Example 3: AAR Query

**User**: "What lessons were learned?"

**Processing**:
1. Matches pattern: `r"(?:what|show me).*lessons"`
2. Intent: `aar_lessons`
3. Handler: `_handle_aar_section("lessons_learned")`
4. Extracts AAR lessons from cache
5. Formats as table

**Response**:
```python
{
    "type": "table",
    "data": {
        "columns": ["Category", "Description", "Importance"],
        "rows": [
            ["Communication", "Improve inter-team comms", "high"],
            ["Planning", "Allocate more buffer time", "medium"],
            ["Resource Mgmt", "Better resource tracking", "high"]
        ]
    },
    "explanation": "Found 3 lessons learned:",
    "confidence": 0.95
}
```

## Testing

### Unit Tests

```python
# File: tests/unit/test_data_insights_query_service.py

import pytest
from backend.business_enablement.enabling_services.data_insights_query_service import DataInsightsQueryService

@pytest.mark.asyncio
async def test_top_n_query():
    """Test top N query processing."""
    service = DataInsightsQueryService()
    
    analysis = {
        "summary": {
            "tabular": {
                "columns": ["Name", "Revenue"],
                "rows": [
                    ["Product A", 1200],
                    ["Product B", 980],
                    ["Product C", 850]
                ]
            }
        }
    }
    
    result = await service.process_query(
        query="What are the top 2 items?",
        analysis_id="test_123",
        cached_analysis=analysis
    )
    
    assert result["success"] == True
    assert result["result"]["type"] == "table"
    assert len(result["result"]["data"]["rows"]) == 2
    assert result["result"]["data"]["rows"][0][0] == "Product A"
```

### Integration Tests

```python
# File: tests/integration/test_insights_query_integration.py

@pytest.mark.asyncio
async def test_query_via_orchestrator():
    """Test query processing via orchestrator."""
    # Create orchestrator
    orchestrator = InsightsOrchestrator(business_orchestrator)
    await orchestrator.initialize()
    
    # Run analysis first
    analysis_result = await orchestrator.analyze_content_for_insights(...)
    analysis_id = analysis_result["analysis_id"]
    
    # Query the analysis
    query_result = await orchestrator.query_analysis_results(
        query="What are the top 5 items?",
        analysis_id=analysis_id
    )
    
    assert query_result["success"] == True
    assert "result" in query_result
```

## Performance

### Rule-Based Processing

- **Latency**: < 100ms (pattern matching + data extraction)
- **Throughput**: > 100 queries/second
- **Cache dependency**: O(1) lookup in analysis cache

### LLM Fallback (Future)

- **Latency**: 1-3 seconds (LLM inference)
- **Throughput**: Depends on LLM endpoint
- **Cost**: Per-query LLM API cost

## Future Enhancements

### Phase 2: LLM Fallback

Add LLM-based processing for complex queries:

```python
service = DataInsightsQueryService(llm_client=llm_client)
```

### Phase 3: Advanced Patterns

- **Time-series queries**: "Show revenue growth over time"
- **Aggregations**: "What's the average profit margin by region?"
- **Multi-step reasoning**: "Compare top performers in Q1 vs Q2"
- **Conversational context**: Remember previous queries in session

### Phase 4: Learning

- **Pattern learning**: Learn new patterns from user queries
- **Intent refinement**: Improve confidence scoring
- **Personalization**: User-specific query preferences

## Troubleshooting

### Issue: Low Confidence Queries

**Symptom**: Many queries falling back to LLM (or general handler)

**Solution**: Add more specific patterns to `QUERY_PATTERNS`

### Issue: Incorrect Intent Detection

**Symptom**: Query matched wrong pattern

**Solution**: Refine regex patterns, add more context

### Issue: Analysis Not Found

**Symptom**: `"Analysis not found: {id}"`

**Solution**: 
1. Check analysis cache
2. Verify analysis was completed
3. Check cache expiration/eviction

### Issue: Empty Table Results

**Symptom**: Table queries return no data

**Solution**:
1. Check tabular data exists in cached analysis
2. Verify column structure matches expectations
3. Check data type compatibility (numeric sorting)

## Summary

**DataInsightsQueryService** provides a powerful, rule-based approach to conversational analytics:

✅ **15+ Query Patterns**: Handles most common data questions  
✅ **3 Response Types**: Table, Chart, Text (+ Insight future)  
✅ **High Performance**: < 100ms latency  
✅ **MCP Integration**: Available to agents via MCP tools  
✅ **Semantic API**: Accessible via `/api/semantic/insights/query-analysis-results`  
✅ **Context-Aware**: Generates relevant follow-up suggestions  
✅ **Extensible**: LLM fallback ready for Phase 2  

This enables users to ask natural language questions about their data insights and receive structured, actionable responses!



