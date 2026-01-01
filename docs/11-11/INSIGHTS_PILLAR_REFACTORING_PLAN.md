# Insights Pillar Refactoring Plan

## 🎯 Vision Summary

Transform the Insights Pillar into a clean, two-section layout that provides unified insights presentation regardless of data type, with enhanced NLP query capabilities through the Insights Liaison Agent.

---

## 📊 Current State Analysis

### **Frontend Structure:**
- **Two separate pages**: `/pillars/insights` (basic) and `/pillars/insight` (VARK/APG toggle)
- **VARK Flow**: Learning-style optimized interface with business summary + learning style selector
- **APG Flow**: After Action Report processing for Navy use case
- **Insights Liaison Agent**: Currently rendered inline (should be in side panel)

### **Backend Structure:**
- **InsightsPillarService**: Main service orchestrator (1,088+ lines)
- **Micro-modules**: Data Analyzer, Visualization Engine, APG Mode Processor, Insights Generator, Metrics Calculator
- **Agents**: Insights Liaison Agent, Insights Analysis Agent, APG Analysis Agent
- **MCP Server**: Tools for analysis, visualization, APG processing

### **Key Issues:**
1. **UI Complexity**: VARK/APG toggle creates confusion - should be content-type driven
2. **Duplicate Pages**: Two different insights pages with overlapping functionality
3. **Agent Placement**: Insights Liaison Agent rendered inline instead of side panel
4. **Inconsistent Data Flow**: VARK expects structured, APG expects unstructured, but no clear separation
5. **Metadata Integration**: No clear path to use extracted metadata instead of file selection

---

## ✨ Enhancement Opportunities

### **1. Unified Insights Display Pattern**
**Current**: Different layouts for VARK vs APG  
**Enhanced**: Consistent 3-way summary display for both:
- **Textual Summary** (Business Analysis): Always shown, explains insights in narrative form
- **Tabular Summary**: Shown when data is structured/numeric (with expandable detail levels)
- **Visual Summary**: Charts/graphs when applicable (with rationale for each visualization)

**Benefit**: Users get familiar interface regardless of data type, reducing cognitive load

### **2. Smart Metadata Integration**
**Current**: File selection only  
**Enhanced**: 
- Show "Use Extracted Metadata" option when metadata is available from Content Pillar
- Allow users to run analysis on metadata without re-uploading
- Show metadata preview before analysis

**Benefit**: Faster workflow, reduces redundant processing

### **3. Enhanced NLP Query Capabilities**
**Current**: Basic liaison agent with keyword matching  
**Enhanced**:
- **Query Understanding**: Parse natural language queries like "show me accounts over 90 days late"
- **Dynamic Table Generation**: Generate tables on-demand based on queries
- **Context-Aware Responses**: Agent understands current analysis context
- **Query History**: Show previous queries and results

**Example Queries**:
- "I see we have a lot of accounts that are more than 90 days late. Can you show me a table with all of those accounts?"
- "What's the correlation between customer satisfaction and revenue?"
- "Show me a chart of sales trends over the last quarter"
- "Which products have the highest return rates?"

**Benefit**: True conversational analytics, making data exploration intuitive

### **4. Content-Type Driven Routing**
**Current**: User manually selects VARK or APG mode  
**Enhanced**: 
- Automatically route to Structured Data Insights for structured/hybrid files
- Automatically route to Unstructured Data Insights for unstructured files
- Show both sections side-by-side when hybrid content is analyzed
- Clear visual indicators of which section is active

**Benefit**: Eliminates mode confusion, makes workflow intuitive

### **5. Navy AAR Specialization**
**Current**: APG mode handles unstructured data generically  
**Enhanced**:
- **AAR-Specific Analysis**: Pattern recognition for after-action reports
- **Lessons Learned Extraction**: Structured extraction of key learnings
- **Risk Assessment**: Identify and categorize risks from reports
- **Exercise Planning Insights**: Generate actionable recommendations for future exercises
- **Timeline Analysis**: Extract and visualize temporal patterns

**Benefit**: Domain-specific value for Navy use case while maintaining general unstructured analysis

---

## 🏗️ Implementation Approach

### **Phase 1: Frontend Restructure (2-3 days)**

#### **1.1 Create Unified Insights Page**
**File**: `app/pillars/insights/page.tsx`

**Structure**:
```tsx
<div className="flex-grow space-y-6">
  {/* Header */}
  <Header />
  
  {/* Section 1: Insights from Structured Data */}
  <StructuredDataInsightsSection 
    onFileSelect={handleStructuredFileSelect}
    onMetadataSelect={handleStructuredMetadataSelect}
    analysisResult={structuredAnalysisResult}
  />
  
  {/* Section 2: Insights from Unstructured Data */}
  <UnstructuredDataInsightsSection
    onFileSelect={handleUnstructuredFileSelect}
    onMetadataSelect={handleUnstructuredMetadataSelect}
    analysisResult={unstructuredAnalysisResult}
  />
</div>
```

**Key Components**:
- `StructuredDataInsightsSection.tsx`: File/metadata selection + 3-way summary display
- `UnstructuredDataInsightsSection.tsx`: File/metadata selection + 3-way summary + AAR analysis
- `InsightsSummaryDisplay.tsx`: Reusable component for textual/tabular/visual summaries
- Remove: VARK/APG toggle, separate pages

#### **1.2 Create Reusable Summary Display Component**
**File**: `components/insights/InsightsSummaryDisplay.tsx`

**Features**:
- **Tabbed Interface**: Text | Table | Charts
- **Textual Tab**: Business analysis narrative (always available)
- **Tabular Tab**: Data grid with sorting, filtering, export (when data available)
- **Visual Tab**: Chart gallery with Vega-Lite rendering (when applicable)
- **Empty States**: Helpful messages when data isn't available

#### **1.3 Move Insights Liaison Agent to Side Panel**
- Remove inline `<InsightsLiaisonAgent />` component
- Keep `useEffect` that configures agent for side panel (like Content Pillar)
- Agent accessible via "Switch to Specialist" button

#### **1.4 File/Metadata Selection Component**
**File**: `components/insights/InsightsFileSelector.tsx`

**Features**:
- Dropdown for file selection (filtered by content type)
- "Use Extracted Metadata" button (when metadata available)
- Metadata preview before analysis
- Clear indication of selected source

---

### **Phase 2: Backend API Enhancements (2-3 days)**

#### **2.1 Unified Analysis Endpoint**
**Endpoint**: `POST /api/insights-pillar/analyze`

**Request**:
```typescript
interface AnalysisRequest {
  source_type: 'file' | 'metadata';
  file_id?: string;
  metadata_id?: string;
  content_type: 'structured' | 'unstructured' | 'hybrid';
  analysis_options?: {
    include_visualizations?: boolean;
    include_tabular_summary?: boolean;
    aar_specific_analysis?: boolean; // For Navy use case
  };
}
```

**Response**:
```typescript
interface AnalysisResponse {
  success: boolean;
  analysis_id: string;
  summary: {
    textual: string; // Business analysis narrative
    tabular?: {
      columns: string[];
      rows: any[][];
      summary_stats?: Record<string, any>;
    };
    visualizations?: Array<{
      chart_type: string;
      vega_lite_spec: any;
      rationale: string;
    }>;
  };
  insights: Array<{
    type: string;
    description: string;
    confidence: number;
    recommendations?: string[];
  }>;
  metadata: {
    content_type: string;
    analysis_timestamp: string;
    processing_time_ms: number;
  };
}
```

#### **2.2 Enhanced NLP Query Endpoint**
**Endpoint**: `POST /api/insights-pillar/query`

**Request**:
```typescript
interface QueryRequest {
  query: string; // Natural language query
  analysis_id: string; // Context from current analysis
  query_type?: 'table' | 'chart' | 'summary' | 'insight';
}
```

**Response**:
```typescript
interface QueryResponse {
  success: boolean;
  result: {
    type: 'table' | 'chart' | 'text' | 'insight';
    data?: any; // Table data or chart spec
    explanation: string; // What the query found
  };
  follow_up_suggestions?: string[]; // Related queries user might want
}
```

#### **2.3 Metadata Integration**
- Add endpoint to fetch available metadata from Content Pillar
- Add metadata validation to ensure it's suitable for analysis
- Support metadata-based analysis without file re-processing

---

### **Phase 3: Insights Liaison Agent Enhancement (2-3 days)**

#### **3.1 Query Understanding**
- Implement natural language parsing for data queries
- Map queries to analysis operations (filter, aggregate, correlate, etc.)
- Context awareness: understand current analysis state

#### **3.2 Dynamic Response Generation**
- Generate tables on-demand based on queries
- Create charts dynamically from query results
- Provide explanations of what was found

#### **3.3 Query Examples & Suggestions**
- Show example queries when user opens chat
- Suggest follow-up queries based on current analysis
- Maintain query history for reference

---

### **Phase 4: Navy AAR Specialization (1-2 days)**

#### **4.1 AAR-Specific Analysis Module**
**File**: `backend/.../insights_pillar/micro_modules/aar_analyzer.py`

**Capabilities**:
- Extract lessons learned from AAR text
- Identify risk factors and categorize them
- Generate exercise planning recommendations
- Timeline extraction and visualization

#### **4.2 AAR Analysis UI**
- Special section in Unstructured Data Insights
- Showcase AAR-specific insights (lessons learned, risks, recommendations)
- Export AAR analysis report

---

## 📋 Implementation Checklist

### **Frontend**
- [ ] Create unified `insights/page.tsx` with two sections
- [ ] Build `StructuredDataInsightsSection` component
- [ ] Build `UnstructuredDataInsightsSection` component
- [ ] Create reusable `InsightsSummaryDisplay` component
- [ ] Build `InsightsFileSelector` with metadata option
- [ ] Remove VARK/APG toggle and separate pages
- [ ] Move Insights Liaison Agent to side panel
- [ ] Add query interface in side panel chat
- [ ] Implement 3-way summary display (text/table/charts)

### **Backend**
- [ ] Create unified analysis endpoint
- [ ] Add metadata-based analysis support
- [ ] Enhance NLP query endpoint
- [ ] Implement query understanding logic
- [ ] Add dynamic table/chart generation
- [ ] Create AAR-specific analysis module
- [ ] Update Insights Liaison Agent with query capabilities

### **Integration**
- [ ] Connect frontend to new backend endpoints
- [ ] Integrate Insights Liaison Agent with query system
- [ ] Test file-based analysis flow
- [ ] Test metadata-based analysis flow
- [ ] Test NLP query capabilities
- [ ] Test AAR-specific analysis

---

## 🎨 UI/UX Enhancements

### **Visual Hierarchy**
- Clear section headers: "Insights from Structured Data" | "Insights from Unstructured Data"
- Visual indicators showing which section is active
- Consistent card layout matching Content Pillar style

### **Progressive Disclosure**
- Show file/metadata selection first
- Display summary tabs after analysis completes
- Expandable detail levels in tabular view
- Chart gallery with thumbnails

### **Feedback & Loading States**
- Clear loading indicators during analysis
- Progress updates for long-running analyses
- Error states with helpful recovery suggestions
- Success confirmations with next-step suggestions

---

## 🔄 Migration Strategy

1. **Keep existing pages** during development (no breaking changes)
2. **Build new unified page** alongside existing
3. **Test thoroughly** with both structured and unstructured data
4. **Gradual rollout**: Feature flag to switch between old/new
5. **Remove old pages** once new page is validated

---

## 📊 Success Metrics

- **User Clarity**: Users understand which section to use (structured vs unstructured)
- **Workflow Speed**: Metadata-based analysis reduces time-to-insights
- **Query Effectiveness**: Users successfully query data via NLP
- **AAR Value**: Navy users extract actionable insights from AARs
- **Consistency**: Unified interface reduces learning curve

---

## 🚀 Next Steps

1. **Review this plan** and provide feedback
2. **Prioritize phases** based on business needs
3. **Start with Phase 1** (Frontend Restructure) for immediate UX improvement
4. **Iterate** based on user feedback

