# Phase 6 Frontend Integration - Evaluation & Updated Plan

**Date:** January 2025  
**Status:** 📋 **EVALUATION COMPLETE**  
**Context:** Post-Insights Pillar Refactoring

---

## 🎯 Executive Summary

After the holistic refactoring of the Insights Pillar, we need to update Phase 6 to ensure:
1. **All existing components** use the new architecture
2. **New data mapping UI** integrates properly
3. **Consistent API usage** across all components
4. **Proper UI representation** of the Solution → Journey → Realm pattern

---

## 📊 Current State Analysis

### ✅ What's Already Updated

1. **Frontend Service Layer** (`shared/services/insights/core.ts`)
   - ✅ Updated to use `/api/v1/insights-solution/*` endpoints
   - ✅ Removed legacy methods
   - ✅ New methods: `getEDAAnalysis()`, `getBusinessAnalysis()`, `getUnstructuredAnalysis()`, `getVARKAnalysis()`
   - ⚠️ **Missing:** Data mapping methods

2. **Insights Page Structure** (`app/pillars/insights/page.tsx`)
   - ✅ Two-section layout (Structured + Unstructured)
   - ✅ Uses new component structure
   - ⚠️ **Missing:** Data Mapping section

3. **Component Structure**
   - ✅ `StructuredDataInsightsSection.tsx` - Exists
   - ✅ `UnstructuredDataInsightsSection.tsx` - Exists
   - ✅ `InsightsDashboard.tsx` - Exists (may need updates)
   - ❌ **Missing:** Data Mapping components

### ⚠️ What Needs Updates

1. **Existing Components Using Old API**
   - Need to audit all components for legacy API calls
   - Update to use new `InsightsService` methods
   - Ensure all use `insights-solution` endpoints

2. **Missing Data Mapping UI**
   - No data mapping section in Insights page
   - No file selection for source/target
   - No mapping results display
   - No quality dashboard
   - No cleanup actions UI

3. **API Method Gaps**
   - Missing data mapping methods in `InsightsService`
   - Missing visualization methods (may need updates)
   - Missing export methods

---

## 🔍 Detailed Component Analysis

### 1. Insights Service (`shared/services/insights/core.ts`)

**Current State:**
- ✅ Uses `/api/v1/insights-solution` base URL
- ✅ Has `getEDAAnalysis()`, `getBusinessAnalysis()`, `getUnstructuredAnalysis()`, `getVARKAnalysis()`
- ⚠️ Has `getVisualizationAnalysis()` but may need update
- ❌ **Missing:** Data mapping methods

**Required Updates:**
```typescript
// Add to InsightsService class:

/**
 * Execute data mapping operation
 * @param sourceFileId - Source file identifier
 * @param targetFileId - Target file identifier  
 * @param mappingOptions - Mapping configuration
 * @param sessionToken - Optional session token
 */
async executeDataMapping(
  sourceFileId: string,
  targetFileId: string,
  mappingOptions?: {
    mapping_type?: "auto" | "unstructured_to_structured" | "structured_to_structured";
    quality_validation?: boolean;
    min_confidence?: number;
    include_citations?: boolean;
  },
  sessionToken?: string
): Promise<DataMappingResponse> {
  const res = await fetch(`${API_BASE}/mapping`, {
    method: "POST",
    headers: getAuthHeaders(this.token, sessionToken),
    body: JSON.stringify({
      source_file_id: sourceFileId,
      target_file_id: targetFileId,
      mapping_options: mappingOptions || {},
    }),
  });
  
  if (!res.ok) {
    throw new Error(`Failed to execute data mapping: ${res.status} ${res.statusText}`);
  }
  
  return await res.json();
}

/**
 * Get mapping results
 * @param mappingId - Mapping operation identifier
 * @param sessionToken - Optional session token
 */
async getMappingResults(
  mappingId: string,
  sessionToken?: string
): Promise<DataMappingResultsResponse> {
  const res = await fetch(`${API_BASE}/mapping/${mappingId}`, {
    method: "GET",
    headers: getAuthHeaders(this.token, sessionToken),
  });
  
  if (!res.ok) {
    throw new Error(`Failed to get mapping results: ${res.status} ${res.statusText}`);
  }
  
  return await res.json();
}

/**
 * Export mapping results
 * @param mappingId - Mapping operation identifier
 * @param outputFormat - Output format (excel, json, csv)
 * @param sessionToken - Optional session token
 */
async exportMappingResults(
  mappingId: string,
  outputFormat: "excel" | "json" | "csv" = "excel",
  sessionToken?: string
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/mapping/${mappingId}/export`, {
    method: "POST",
    headers: getAuthHeaders(this.token, sessionToken),
    body: JSON.stringify({
      output_format: outputFormat,
    }),
  });
  
  if (!res.ok) {
    throw new Error(`Failed to export mapping results: ${res.status} ${res.statusText}`);
  }
  
  return await res.blob();
}
```

**Type Definitions Needed:**
```typescript
// Add to shared/services/insights/types.ts

export interface DataMappingResponse {
  success: boolean;
  mapping_id: string;
  workflow_id: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  message?: string;
  error?: string;
}

export interface DataMappingResultsResponse {
  success: boolean;
  mapping_id: string;
  workflow_id: string;
  mapping_results: {
    mapped_records: any[];
    mapping_rules: MappingRule[];
    confidence_scores: Record<string, number>;
    citations: Record<string, Citation[]>;
  };
  quality_report?: QualityReport;  // For structured→structured
  cleanup_actions?: CleanupAction[];  // For structured→structured
  metadata: {
    source_file_id: string;
    target_file_id: string;
    mapping_type: string;
    record_count: number;
    created_at: string;
    completed_at?: string;
  };
}

export interface MappingRule {
  source_field: string;
  target_field: string;
  confidence: number;
  extraction_method: "llm" | "regex" | "semantic";
  transformation?: string;
}

export interface Citation {
  field: string;
  source: string;
  location: string;
  confidence: number;
}

export interface QualityReport {
  overall_score: number;
  pass_rate: number;
  completeness: number;
  accuracy: number;
  record_count: number;
  quality_issues: QualityIssue[];
  metrics: {
    total_records: number;
    passed_records: number;
    failed_records: number;
    records_with_issues: number;
  };
}

export interface QualityIssue {
  record_id: string;
  field: string;
  issue_type: "missing" | "invalid_type" | "invalid_format" | "out_of_range";
  severity: "high" | "medium" | "low";
  message: string;
  suggested_fix?: string;
}

export interface CleanupAction {
  action_id: string;
  priority: "high" | "medium" | "low";
  action_type: "fix_missing" | "fix_format" | "fix_type" | "transform";
  description: string;
  affected_records: number;
  example_fix: string;
  suggested_transformation?: string;
}
```

---

### 2. Insights Page (`app/pillars/insights/page.tsx`)

**Current State:**
- ✅ Two-section layout (Structured + Unstructured)
- ❌ **Missing:** Data Mapping section

**Required Updates:**
```typescript
// Add third section to Insights page:

{/* Section 3: Data Mapping */}
<Card>
  <CardHeader>
    <CardTitle>Data Mapping</CardTitle>
    <CardDescription>
      Map data from source files to target data models. Supports both unstructured-to-structured 
      (e.g., license PDF to Excel) and structured-to-structured (e.g., legacy policy records to new model) 
      with quality validation and cleanup actions.
    </CardDescription>
  </CardHeader>
  <CardContent>
    <DataMappingSection 
      onMappingComplete={handleMappingComplete}
    />
  </CardContent>
</Card>
```

---

### 3. New Components Required

#### 3.1 Data Mapping Section Component
**File:** `app/pillars/insights/components/DataMappingSection.tsx`

**Features:**
- File selection (source + target)
- Mapping type selection (auto, unstructured→structured, structured→structured)
- Mapping options configuration
- Execute mapping button
- Progress indicator
- Results display

**Structure:**
```typescript
export function DataMappingSection({ onMappingComplete }: Props) {
  // State management
  // File selection UI
  // Mapping options UI
  // Execute mapping
  // Display results
}
```

#### 3.2 Mapping Results Display Component
**File:** `app/pillars/insights/components/MappingResultsDisplay.tsx`

**Features:**
- Mapping rules table (source → target with confidence)
- Sample mapped records preview
- Citations display
- Export buttons

**Tabs:**
- Overview
- Mapping Rules
- Sample Data
- Citations

#### 3.3 Quality Dashboard Component
**File:** `app/pillars/insights/components/QualityDashboard.tsx`

**Features:**
- Quality score visualization (gauge/chart)
- Quality metrics (pass rate, completeness, accuracy)
- Quality issues list
- Record-level drill-down
- Filtering and sorting

**Sections:**
- Quality Overview (metrics cards)
- Quality Issues Table
- Record Details Panel

#### 3.4 Cleanup Actions Panel Component
**File:** `app/pillars/insights/components/CleanupActionsPanel.tsx`

**Features:**
- Cleanup actions list (prioritized)
- Action details (description, affected records, example fix)
- Export cleanup report button
- Filter by priority/type

**Structure:**
- Actions grouped by priority
- Expandable action cards
- Example fixes display
- Export functionality

---

### 4. Existing Components to Audit & Update

#### 4.1 StructuredDataInsightsSection.tsx
**Check:**
- ⚠️ Uses `@/lib/api/insights` - **NEEDS AUDIT**
- ⚠️ Uses `analyzeContentForInsights()` function - may be legacy
- ⚠️ May need to migrate to `InsightsService.getEDAAnalysis()`
- ⚠️ May need to verify error handling for new architecture

**Action:** **CRITICAL** - Audit `lib/api/insights.ts` and update to use new architecture

#### 4.1a lib/api/insights.ts (API Layer)
**Check:**
- ⚠️ This is a separate API layer that may be using legacy endpoints
- ⚠️ May need complete rewrite to use `InsightsService`
- ⚠️ Or update to use `/api/v1/insights-solution/*` endpoints

**Action:** **CRITICAL** - Audit and update this file first

#### 4.2 UnstructuredDataInsightsSection.tsx
**Check:**
- ✅ Uses `InsightsService.getUnstructuredAnalysis()` or similar new methods
- ✅ Uses `/api/v1/insights-solution/analyze` endpoint
- ⚠️ May need to verify error handling for new architecture

**Action:** Review and verify API usage

#### 4.3 InsightsDashboard.tsx
**Check:**
- ⚠️ Uses `InsightsService.getBusinessAnalysis()` - verify it's updated
- ⚠️ May have legacy API calls
- ⚠️ May need workflow_id display

**Action:** Audit and update if needed

#### 4.4 InsightsFileSelector.tsx
**Check:**
- ✅ File selection component
- ⚠️ May need to support selecting two files (source + target) for mapping

**Action:** Review and potentially extend for dual file selection

---

## 📋 Updated Phase 6 Implementation Plan

### Phase 6.0: Critical API Migration (Week 11, Day 1) ⚠️ **URGENT**

**Tasks:**
1. **CRITICAL:** Update `lib/api/insights.ts` to use `/api/v1/insights-solution/*` endpoints
   - Update `analyzeContentForInsights()` to use `/api/v1/insights-solution/analyze`
   - Update all other functions to use new endpoints
   - OR deprecate this file and migrate components to `InsightsService`
2. Test that existing components still work
3. Fix any breaking changes

**Deliverables:**
- Updated `lib/api/insights.ts` OR migration plan
- Verified existing components work
- Migration documentation

**Priority:** **CRITICAL** - Must be done first, before any new component work

---

### Phase 6.1: Service Layer Updates (Week 11, Days 2-3)

**Tasks:**
1. ✅ Add data mapping methods to `InsightsService`
2. ✅ Add type definitions for data mapping
3. ✅ Update visualization methods if needed
4. ✅ Add export methods
5. ✅ Test service methods

**Deliverables:**
- Updated `shared/services/insights/core.ts`
- Updated `shared/services/insights/types.ts`
- Service method tests

---

### Phase 6.2: Data Mapping Core Components (Week 11, Days 3-5)

**Tasks:**
1. Create `DataMappingSection.tsx`
   - File selection (source + target)
   - Mapping type selection
   - Options configuration
   - Execute mapping
   - Progress indicator

2. Create `MappingResultsDisplay.tsx`
   - Mapping rules table
   - Sample data preview
   - Citations display
   - Export buttons

**Deliverables:**
- `app/pillars/insights/components/DataMappingSection.tsx`
- `app/pillars/insights/components/MappingResultsDisplay.tsx`
- Component tests

---

### Phase 6.3: Quality & Cleanup Components (Week 12, Days 1-3)

**Tasks:**
1. Create `QualityDashboard.tsx`
   - Quality metrics visualization
   - Quality issues table
   - Record-level drill-down

2. Create `CleanupActionsPanel.tsx`
   - Cleanup actions list
   - Priority indicators
   - Export functionality

**Deliverables:**
- `app/pillars/insights/components/QualityDashboard.tsx`
- `app/pillars/insights/components/CleanupActionsPanel.tsx`
- Component tests

---

### Phase 6.4: Integration & Updates (Week 12, Days 4-5)

**Tasks:**
1. Update Insights page to include Data Mapping section
2. Audit existing components for API usage
3. Update any components using legacy APIs
4. Add workflow_id display where appropriate
5. Integration testing

**Deliverables:**
- Updated `app/pillars/insights/page.tsx`
- Updated existing components (if needed)
- Integration tests
- E2E tests

---

### Phase 6.5: Polish & Documentation (Week 12, Day 5)

**Tasks:**
1. UI/UX polish
2. Error handling improvements
3. Loading states
4. Documentation updates
5. User guide

**Deliverables:**
- Polished UI
- Updated documentation
- User guide

---

## 🎨 UI/UX Design Considerations

### Data Mapping Section Layout

```
┌─────────────────────────────────────────────────┐
│ Data Mapping                                    │
├─────────────────────────────────────────────────┤
│                                                 │
│ Source File: [Select File ▼]                   │
│ Target File: [Select File ▼]                   │
│                                                 │
│ Mapping Type: ○ Auto  ○ Unstructured→Structured │
│                ○ Structured→Structured           │
│                                                 │
│ Options:                                        │
│ ☑ Quality Validation (for structured→structured)│
│ Min Confidence: [0.8] ━━━━━━━━━━━━━━━━━━━━━━━ │
│ ☑ Include Citations                            │
│                                                 │
│ [Execute Mapping]                               │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Mapping Results Layout

```
┌─────────────────────────────────────────────────┐
│ Mapping Results                                 │
├─────────────────────────────────────────────────┤
│ [Overview] [Mapping Rules] [Sample Data] [Citations] │
│                                                 │
│ Overview:                                       │
│ • Mapped Records: 1,234                        │
│ • Average Confidence: 0.87                     │
│ • Mapping Rules: 15                             │
│                                                 │
│ [Export Excel] [Export JSON] [Export CSV]      │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Quality Dashboard Layout

```
┌─────────────────────────────────────────────────┐
│ Quality Dashboard                               │
├─────────────────────────────────────────────────┤
│                                                 │
│ Quality Score: [Gauge Chart] 0.85              │
│                                                 │
│ Metrics:                                        │
│ Pass Rate: 85%  │  Completeness: 92%           │
│ Accuracy: 88%   │  Records: 1,234              │
│                                                 │
│ Quality Issues:                                 │
│ [Table with filtering]                          │
│ • Record 123: Missing field "expiration_date"   │
│ • Record 456: Invalid format "license_number"   │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## ✅ Success Criteria

### Functional
- ✅ Users can select source and target files
- ✅ Users can execute data mapping
- ✅ Mapping results are displayed correctly
- ✅ Quality dashboard shows metrics and issues
- ✅ Cleanup actions are displayed and exportable
- ✅ All exports work correctly

### Technical
- ✅ All components use new `InsightsService` methods
- ✅ All API calls use `/api/v1/insights-solution/*` endpoints
- ✅ Workflow IDs are displayed where appropriate
- ✅ Error handling is consistent
- ✅ Loading states are clear

### UX
- ✅ Intuitive file selection
- ✅ Clear progress indicators
- ✅ Easy-to-understand results
- ✅ Actionable cleanup actions
- ✅ Smooth export process

---

## 🚨 CRITICAL FINDINGS

### ⚠️ CRITICAL: Legacy API Layer Still Active

**File:** `lib/api/insights.ts`

**Issue:**
- This file contains functions that use **OLD `/api/insights-pillar/*` endpoints**
- These endpoints have been **REMOVED** in the backend refactoring
- Functions like `analyzeContentForInsights()` call `/api/insights-pillar/analyze-content-for-insights` which **NO LONGER EXISTS**
- This will cause **ALL existing insights components to fail**

**Affected Functions:**
- `analyzeContentForInsights()` - Line 502: `/api/insights-pillar/analyze-content-for-insights` ❌
- `queryAnalysisResults()` - Line 521: `/api/insights-pillar/query-analysis-results` ❌
- `getAvailableContentMetadata()` - Line 549: `/api/insights-pillar/get-available-content-metadata` ❌
- `validateContentMetadataForInsights()` - Line 567: `/api/insights-pillar/validate-content-metadata-for-insights` ❌
- `getAnalysisResults()` - Line 586: `/api/insights-pillar/get-analysis-results/{id}` ❌
- `getAnalysisVisualizations()` - Line 608: `/api/insights-pillar/get-analysis-visualizations/{id}` ❌
- `listUserAnalyses()` - Line 633: `/api/insights-pillar/list-user-analyses` ❌
- `exportAnalysisReport()` - Line 654: `/api/insights-pillar/export-analysis-report` ❌
- `checkInsightsPillarHealth()` - Line 673: `/api/insights-pillar/health` ❌

**Also Using Legacy Endpoints:**
- `getEDAAnalysis()` - Line 117: `/api/insights/analysis/eda` ❌
- `getVisualizationAnalysis()` - Line 139: `/api/insights/analysis/visualization` ❌
- `getBusinessAnalysis()` - Line 183: `/api/insights/analysis/business-analysis` ❌
- And many more...

**Required Action:**
1. **IMMEDIATE:** Update `lib/api/insights.ts` to use `/api/v1/insights-solution/*` endpoints
2. **OR:** Migrate all components to use `InsightsService` from `shared/services/insights/core.ts`
3. **PRIORITY:** This must be done BEFORE Phase 6.2 (component creation)

**Migration Strategy:**
- Option A: Update `lib/api/insights.ts` functions to call new endpoints
- Option B: Deprecate `lib/api/insights.ts` and migrate components to `InsightsService`
- **Recommendation:** Option B (use `InsightsService` as single source of truth)

---

## 🚨 Risks & Mitigations

### Risk 1: Existing Components Using Legacy APIs ⚠️ **CRITICAL**
**Status:** **CONFIRMED** - `lib/api/insights.ts` uses removed endpoints  
**Mitigation:** 
1. **IMMEDIATE:** Update `lib/api/insights.ts` OR migrate components to `InsightsService`
2. Comprehensive audit before Phase 6.4
3. Update all at once to avoid breaking changes

### Risk 2: Complex Quality Dashboard UI
**Mitigation:** Start with simple metrics, add complexity iteratively

### Risk 3: Large File Handling
**Mitigation:** Implement pagination, lazy loading, progress indicators

### Risk 4: Export Performance
**Mitigation:** Use streaming exports, show progress, handle errors gracefully

---

## 📝 Dependencies

### Backend
- ✅ Data mapping API endpoints working
- ✅ Quality validation working
- ✅ Cleanup actions generation working
- ✅ Export functionality working

### Frontend
- ✅ InsightsService updated
- ✅ Type definitions complete
- ✅ UI component library available
- ✅ File selection components available

---

## 🎯 Next Steps

1. **Review this evaluation** with team
2. **Prioritize components** (can start with core mapping, add quality later)
3. **Create detailed component specs** for each new component
4. **Begin Phase 6.1** (Service layer updates)
5. **Iterate** based on feedback

---

**Status:** 📋 **READY FOR IMPLEMENTATION**  
**Estimated Duration:** 2 weeks (10 working days)  
**Priority:** HIGH - Required for data mapping MVP

