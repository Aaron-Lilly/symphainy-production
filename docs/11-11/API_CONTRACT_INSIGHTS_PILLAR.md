# Insights Pillar API Contract
**Target UX-Driven Design**

## 🎯 Overview

This API contract defines the semantic endpoints that serve the Insights Pillar frontend UX. All endpoints follow semantic naming conventions for clarity, troubleshooting, and extensibility.

---

## 📋 Core Endpoints

### 1. Analyze Content for Insights
**Purpose**: Primary analysis workflow - generate insights from file or metadata

**Endpoint**: `POST /api/insights-pillar/analyze-content-for-insights`

**Request**:
```typescript
{
  source_type: 'file' | 'content_metadata',  // 'content_metadata' = from ArangoDB
  file_id?: string,                          // Required if source_type = 'file'
  content_metadata_id?: string,              // Required if source_type = 'content_metadata'
  content_type: 'structured' | 'unstructured' | 'hybrid',
  analysis_options?: {
    include_visualizations?: boolean,        // Default: true
    include_tabular_summary?: boolean,       // Default: true
    aar_specific_analysis?: boolean          // Navy use case, Default: false
  }
}
```

**Response**:
```typescript
{
  success: boolean,
  analysis_id: string,
  
  // 3-Way Summary Display (Target UX)
  summary: {
    textual: string,              // ALWAYS present - business narrative
    tabular?: {                   // When applicable (structured/hybrid data)
      columns: string[],
      rows: any[][],
      summary_stats?: {
        mean?: Record<string, number>,
        median?: Record<string, number>,
        std_dev?: Record<string, number>,
        total_rows: number,
        total_columns: number
      }
    },
    visualizations?: Array<{      // When applicable
      visualization_id: string,
      chart_type: 'bar' | 'line' | 'pie' | 'area' | 'heatmap' | 'scatter',  // Recharts types
      library: 'recharts' | 'nivo',  // Which chart library to use
      title?: string,
      rationale: string,           // Why this visualization is useful
      chart_data: Array<{[key: string]: any}>,  // Recharts-format data
      x_axis_key?: string,         // X-axis field name (e.g., 'name', 'date')
      data_key?: string,           // Primary series field (e.g., 'value', 'Revenue')
      colors?: string[]            // Optional color palette
    }>
  },
  
  // Extracted Insights
  insights: Array<{
    insight_id: string,
    type: 'trend' | 'anomaly' | 'correlation' | 'distribution' | 'comparison',
    description: string,
    confidence: number,            // 0.0 - 1.0
    recommendations?: string[],
    supporting_data?: any
  }>,
  
  // Navy AAR Analysis (expandable section below 3-way summary)
  aar_analysis?: {
    lessons_learned: Array<{
      lesson_id: string,
      category: 'tactical' | 'strategic' | 'operational' | 'logistical',
      description: string,
      importance: 'high' | 'medium' | 'low',
      actionable_steps?: string[]
    }>,
    risks: Array<{
      risk_id: string,
      category: 'personnel' | 'equipment' | 'environmental' | 'operational',
      description: string,
      severity: 'critical' | 'high' | 'medium' | 'low',
      mitigation_strategies?: string[]
    }>,
    recommendations: Array<{
      recommendation_id: string,
      area: 'training' | 'equipment' | 'procedures' | 'planning',
      recommendation: string,
      priority: 'high' | 'medium' | 'low',
      estimated_impact: string
    }>,
    timeline?: Array<{
      timestamp: string,
      event: string,
      event_type: 'milestone' | 'incident' | 'decision' | 'outcome'
    }>
  },
  
  // Metadata
  metadata: {
    content_type: 'structured' | 'unstructured' | 'hybrid',
    analysis_timestamp: string,
    processing_time_ms: number,
    source_info: {
      type: 'file' | 'content_metadata',
      id: string,
      name?: string,
      tenant_id?: string
    }
  }
}
```

---

### 2. Query Analysis Results
**Purpose**: Conversational analytics - NLP queries on analysis results

**Endpoint**: `POST /api/insights-pillar/query-analysis-results`

**Request**:
```typescript
{
  query: string,                              // Natural language query
  analysis_id: string,                        // Context from current analysis
  query_type?: 'table' | 'chart' | 'summary' // Hint for response format
}
```

**Response**:
```typescript
{
  success: boolean,
  query_id: string,
  result: {
    type: 'table' | 'chart' | 'text' | 'insight',
    data?: any,                    // Table data or Recharts chart spec
    explanation: string,           // What the query found
    confidence?: number            // How confident the system is in the result
  },
  follow_up_suggestions?: string[] // Related queries user might want
}
```

**Example Queries**:
- "Show me all accounts that are more than 90 days late"
- "What's the correlation between customer satisfaction and revenue?"
- "Create a chart showing sales trends over the last quarter"
- "Which products have the highest return rates?"

---

### 3. Get Available Content Metadata
**Purpose**: Fetch metadata stored in ArangoDB from Content Pillar

**Endpoint**: `GET /api/insights-pillar/get-available-content-metadata`

**Query Parameters**:
- `tenant_id`: string (optional, filters by tenant)
- `content_type`: 'structured' | 'unstructured' (optional, filters by type)
- `limit`: number (optional, default: 50)
- `offset`: number (optional, default: 0)

**Response**:
```typescript
{
  success: boolean,
  content_metadata_items: Array<{
    content_metadata_id: string,     // ArangoDB _key
    file_id: string,
    tenant_id: string,
    
    // File Info
    file_metadata: {
      file_name: string,
      file_type: string,
      file_size: number,
      creation_date: string,
      modification_date: string
    },
    
    // Content Info
    content_metadata: {
      title: string,
      author: string,
      subject: string,
      keywords: string[],
      language: string,
      word_count: number
    },
    
    // Semantic Info
    semantic_metadata: {
      topics: string[],
      entities: string[],
      sentiment: string,
      categories: string[],
      tags: string[]
    },
    
    // Enhanced Librarian Analysis
    librarian_analysis?: {
      categorization?: any,
      quality_assessment?: any,
      semantic_insights?: any
    },
    
    extraction_timestamp: string,
    
    // Preview for UI
    preview: {
      text_sample?: string,          // First 500 chars
      table_sample?: any,            // First 5 rows if structured
      entity_count?: number,
      topic_count?: number
    }
  }>,
  
  // Pagination
  pagination: {
    total_count: number,
    limit: number,
    offset: number,
    has_more: boolean
  }
}
```

---

### 4. Validate Content Metadata
**Purpose**: Check if metadata is suitable for insights analysis

**Endpoint**: `POST /api/insights-pillar/validate-content-metadata-for-insights`

**Request**:
```typescript
{
  content_metadata_id: string
}
```

**Response**:
```typescript
{
  success: boolean,
  valid: boolean,
  content_type: 'structured' | 'unstructured' | 'hybrid',
  
  // Auto-detected analysis capabilities
  suggested_analysis_options: {
    include_visualizations: boolean,
    include_tabular_summary: boolean,
    aar_specific_analysis: boolean
  },
  
  // Quality checks
  validation_details: {
    has_sufficient_content: boolean,
    has_structured_data: boolean,
    has_entities: boolean,
    has_semantic_metadata: boolean,
    quality_score: number              // 0.0 - 1.0
  },
  
  validation_notes?: string[]          // Human-readable notes
}
```

---

### 5. Get Analysis Results (Retrieve)
**Purpose**: Retrieve cached analysis results

**Endpoint**: `GET /api/insights-pillar/get-analysis-results/{analysis_id}`

**Response**:
```typescript
{
  success: boolean,
  analysis: {
    // Same structure as "Analyze Content for Insights" response
  }
}
```

---

### 6. Get Analysis Visualizations
**Purpose**: Retrieve visualizations for a specific analysis

**Endpoint**: `GET /api/insights-pillar/get-analysis-visualizations/{analysis_id}`

**Query Parameters**:
- `chart_type`: 'bar' | 'line' | 'pie' | 'area' | 'heatmap' | 'scatter' (optional)

**Response**:
```typescript
{
  success: boolean,
  visualizations: Array<{
    visualization_id: string,
    chart_type: 'bar' | 'line' | 'pie' | 'area' | 'heatmap' | 'scatter',
    library: 'recharts' | 'nivo',
    title?: string,
    rationale: string,
    chart_data: Array<{[key: string]: any}>,  // Recharts-format data
    x_axis_key?: string,
    data_key?: string,
    colors?: string[],
    thumbnail_url?: string           // Optional pre-rendered thumbnail
  }>
}
```

---

### 7. List User's Analyses
**Purpose**: Show user's analysis history for session context

**Endpoint**: `GET /api/insights-pillar/list-user-analyses`

**Query Parameters**:
- `limit`: number (optional, default: 20)
- `offset`: number (optional, default: 0)
- `content_type`: 'structured' | 'unstructured' (optional filter)

**Response**:
```typescript
{
  success: boolean,
  analyses: Array<{
    analysis_id: string,
    content_type: 'structured' | 'unstructured' | 'hybrid',
    source_info: {
      type: 'file' | 'content_metadata',
      name: string
    },
    analyzed_at: string,
    summary_preview: string,         // First 200 chars of textual summary
    insight_count: number,
    has_visualizations: boolean
  }>,
  pagination: {
    total_count: number,
    limit: number,
    offset: number,
    has_more: boolean
  }
}
```

---

### 8. Get Pillar Summary
**Purpose**: Get Insights Pillar summary for Business Outcomes page

This endpoint returns the 3-way summary (textual, tabular, visualizations) from the most recent or specified analysis. It's designed to be consumed by the Business Outcomes pillar to display insights on their dashboard.

**Endpoint**: `GET /api/insights-pillar/pillar-summary?analysis_id={optional}`

**Query Parameters**:
- `analysis_id` (optional): Specific analysis ID. If omitted, returns most recent analysis.

**Response**:
```typescript
{
  success: boolean,
  pillar: 'insights',
  summary: {
    textual: string,              // Business narrative (e.g., "Q4 revenue analysis shows...")
    tabular: {                    // Data table with key findings
      columns: string[],
      rows: any[][],
      summary_stats?: {
        total_rows: number,
        key_metrics: {...}
      }
    },
    visualizations: Array<{       // Charts in Recharts/Nivo format
      visualization_id: string,
      chart_type: 'bar' | 'line' | 'pie' | 'area' | 'heatmap' | 'scatter',
      library: 'recharts' | 'nivo',
      title?: string,
      rationale: string,
      chart_data: Array<{[key: string]: any}>,
      x_axis_key?: string,
      data_key?: string,
      colors?: string[]
    }>
  },
  source_analysis_id: string,
  generated_at: string
}
```

**Note**: Report generation (PDF/DOCX/etc.) is handled by the Business Outcomes pillar, which aggregates summaries from all pillars.

---

### 9. Health Check
**Purpose**: Service health monitoring

**Endpoint**: `GET /api/insights-pillar/health`

**Response**:
```typescript
{
  status: 'healthy' | 'degraded' | 'unhealthy',
  service: 'insights-pillar',
  timestamp: string,
  dependencies: {
    arango_db: 'healthy' | 'unhealthy',
    enabling_services: {
      data_analyzer: 'healthy' | 'unhealthy',
      visualization_engine: 'healthy' | 'unhealthy',
      metrics_calculator: 'healthy' | 'unhealthy',
      insights_generator: 'healthy' | 'unhealthy',
      apg_processor: 'healthy' | 'unhealthy'
    }
  }
}
```

---

## 🔄 Integration with Content Pillar

### ArangoDB Query Pattern

The Insights Pillar will query ArangoDB for content metadata using this pattern:

```python
# Query ArangoDB for available content metadata
content_metadata_abstraction = curator.get_service("ContentMetadataAbstraction")

# Get metadata by tenant
metadata_items = await content_metadata_abstraction.query_content_metadata({
    "tenant_id": user_context.tenant_id,
    "content_type": "structured"  # or "unstructured"
})

# Get specific metadata item
metadata_item = await content_metadata_abstraction.get_content_metadata_by_id(
    content_metadata_id
)
```

### Metadata Schema in ArangoDB

```json
{
  "_key": "content_metadata_12345",
  "_rev": "...",
  "file_id": "file_abc123",
  "tenant_id": "tenant_xyz789",
  
  "file_metadata": {
    "file_id": "file_abc123",
    "file_name": "Q4_Sales_Report.csv",
    "file_type": "csv",
    "file_size": 51200,
    "creation_date": "2025-11-01T10:30:00Z",
    "modification_date": "2025-11-01T10:30:00Z",
    "mime_type": "text/csv",
    "encoding": "utf-8"
  },
  
  "content_metadata": {
    "title": "Q4 Sales Report",
    "author": "Sales Team",
    "subject": "Quarterly sales analysis",
    "keywords": ["sales", "Q4", "revenue", "analysis"],
    "language": "en",
    "word_count": 1500,
    "character_count": 51200,
    "line_count": 200
  },
  
  "semantic_metadata": {
    "topics": ["sales", "revenue", "quarterly_report"],
    "entities": ["Q4", "Sales Team", "Revenue"],
    "sentiment": "neutral",
    "categories": ["business_report", "financial_data"],
    "tags": ["csv", "sales", "quarterly", "structured"],
    "confidence": 0.92,
    "language_detected": "en"
  },
  
  "librarian_analysis": {
    "categorization": {
      "content_type": "structured",
      "domain": "financial"
    },
    "quality_assessment": {
      "completeness": 0.95,
      "consistency": 0.88,
      "accuracy": 0.90
    },
    "semantic_insights": {
      "key_themes": ["quarterly_performance", "revenue_growth"],
      "recommended_analyses": ["trend_analysis", "comparison"]
    }
  },
  
  "extraction_timestamp": "2025-11-01T10:35:00Z"
}
```

---

## 🎨 Frontend Integration Notes

### Data Flow for Metadata-Based Analysis

1. **User opens Insights Pillar**
   - Frontend calls `GET /api/insights-pillar/get-available-content-metadata`
   - Displays list of available metadata items

2. **User selects metadata item**
   - Frontend calls `POST /api/insights-pillar/validate-content-metadata-for-insights`
   - Displays preview and suggested analysis options

3. **User initiates analysis**
   - Frontend calls `POST /api/insights-pillar/analyze-content-for-insights` with `source_type: 'content_metadata'`
   - Backend queries ArangoDB for full metadata
   - Backend runs analysis using metadata (no file re-processing)
   - Returns 3-way summary (text, table, charts)

4. **User asks NLP query**
   - Frontend calls `POST /api/insights-pillar/query-analysis-results`
   - Agent returns table/chart/text dynamically

### "Data Doesn't Leave Your Walls" UX

```typescript
// Frontend component
const InsightsFileSelector = () => {
  const [useMetadata, setUseMetadata] = useState(true);
  
  return (
    <div>
      <Toggle 
        label="Use Extracted Metadata (Data stays secure)"
        checked={useMetadata}
        onChange={setUseMetadata}
      />
      
      {useMetadata ? (
        <MetadataSelector 
          onSelect={handleMetadataSelect}
          previewEnabled={true}
        />
      ) : (
        <FileUploadSelector 
          onUpload={handleFileUpload}
        />
      )}
    </div>
  );
};
```

---

## 📊 Success Criteria

- ✅ All endpoints use semantic naming
- ✅ Content metadata from ArangoDB can be queried and used for analysis
- ✅ 3-way summary (text/table/charts) is always returned
- ✅ AAR analysis is expandable section (not separate mode)
- ✅ NLP queries generate dynamic responses
- ✅ Frontend can show "data doesn't leave your walls" UX
- ✅ API is extensible for future analysis types

---

## 🚀 Implementation Priority

1. **Phase 1**: Core analysis endpoint + ArangoDB integration
2. **Phase 2**: Metadata endpoints + validation
3. **Phase 3**: NLP query endpoint
4. **Phase 4**: Export + history endpoints

