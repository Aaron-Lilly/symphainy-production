# Parallel Components Analysis

## Overview
Found 5 components with "New" suffix indicating parallel implementations:
1. `FileUploaderNew.tsx`
2. `FileDashboardNew.tsx`
3. `ParsePreviewNew.tsx`
4. `MetadataExtractorNew.tsx`
5. `InsightsDashboardNew.tsx`

## Current Usage
**Content Pillar Page** (`app/pillars/content/page.tsx`) uses:
- ✅ `FileUploaderNew`
- ✅ `FileDashboardNew`
- ✅ `ParsePreviewNew`
- ✅ `MetadataExtractorNew`

**Insights Pillar Page** (`app/pillars/insights/page.tsx`) uses:
- ✅ `InsightsDashboardNew`

---

## 1. FileUploader Component

### Versions Found:
1. **`FileUploaderNew.tsx`** (296 lines) - Currently used in page.tsx
2. **`app/pillars/content/components/FileUploader/`** (modular architecture)
   - `index.tsx` - Barrel export
   - `core.tsx` - Main component
   - `hooks.ts` - Custom hooks
   - `types.ts` - TypeScript types
   - `utils.ts` - Utilities
3. **`components/content/FileUploader.tsx`** (385 lines) - Standalone component

### Comparison:

| Feature | FileUploaderNew | FileUploader/ (modular) | components/content/FileUploader |
|---------|----------------|-------------------------|--------------------------------|
| **API Integration** | ❌ TODO comment | ❓ Unknown (needs hooks review) | ✅ Uses `uploadAndProcessFile()` |
| **State Management** | Basic useState | Custom hook (`useFileUploader`) | ✅ Global session state |
| **File Types** | Simple (pdf, docx, csv, txt, xlsx) | Uses FILE_TYPE_OPTIONS | ✅ Full enum (Structured, Image, PDF, Mainframe, SopWorkflow) |
| **Copybook Support** | ❌ No | ✅ Yes (for Mainframe) | ✅ Yes |
| **Pillar State Updates** | ❌ No | ❓ Unknown | ✅ Yes (data, parsing, operations) |
| **Workflow Tracking** | ❌ No | ❓ Unknown | ✅ Yes (workflow_id) |
| **Authentication** | ✅ useAuth() | ❓ Unknown | ✅ useGlobalSession() |
| **Semantic Test IDs** | ❌ No | ❓ Unknown | ❌ No |
| **Architecture** | Monolithic | ✅ Modular | Monolithic |

### Recommendation:
**Keep: `FileUploader/` (modular architecture)** ✅ BEST VERSION
- ✅ Has API integration via `UnifiedFileAPI.uploadFile()` and `uploadAndProcessFile()`
- ✅ Modular architecture (core, hooks, types, utils)
- ✅ Updates pillar states correctly
- ✅ Supports all file types including Mainframe with copybook
- ✅ Tracks workflow IDs
- ✅ Uses `useGlobalSession()` for state management
- ✅ Proper error handling and validation

**Also Keep: `components/content/FileUploader.tsx`** (as reference/fallback)
- Has real API integration
- Updates pillar states correctly
- Supports all file types including Mainframe with copybook
- Tracks workflow IDs

**Archive:**
- `FileUploaderNew.tsx` (incomplete, has TODOs, mock responses)

---

## 2. FileDashboard Component

### Versions Found:
1. **`FileDashboardNew.tsx`** (363 lines) - Currently used in page.tsx
2. **`app/pillars/content/components/FileDashboard/`** (modular architecture)
   - `index.tsx` - Barrel export
   - `core.tsx` - Main component
   - `components.tsx` - Sub-components
   - `hooks.ts` - Custom hooks
   - `types.ts` - TypeScript types
   - `utils.ts` - Utilities
3. **`components/content/FileDashboard.tsx`** - Standalone component

### Comparison:

| Feature | FileDashboardNew | FileDashboard/ (modular) | components/content/FileDashboard |
|---------|------------------|--------------------------|----------------------------------|
| **API Integration** | ❌ TODO comments | ❓ Unknown | ❓ Unknown |
| **File Listing** | ❌ Mock response | ❓ Unknown | ❓ Unknown |
| **File Actions** | ❌ TODO comments | ❓ Unknown | ❓ Unknown |
| **State Management** | Basic useState | Custom hook | ❓ Unknown |
| **Architecture** | Monolithic | ✅ Modular | Monolithic |

### Recommendation:
**Keep: `FileDashboard/` (modular architecture)** ✅ BEST VERSION
- ✅ Has API integration via `UnifiedFileAPI.listFiles()` and `UnifiedFileAPI.deleteFile()`
- ✅ Modular architecture (core, hooks, types, utils, components)
- ✅ Uses `useGlobalSession()` for state management
- ✅ Proper error handling with fallback to mock data
- ✅ Has semantic test ID (`data-testid="files-dashboard"`)

**Also Keep: `components/content/FileDashboard.tsx`** (as reference/fallback)
- Has API integration via `listFiles()` from `@/lib/api/fms`
- Uses global session state management
- Has mock data fallback

**Archive:**
- `FileDashboardNew.tsx` (incomplete, has TODOs, mock responses only)

---

## 3. ParsePreview Component

### Versions Found:
1. **`ParsePreviewNew.tsx`** - Currently used in page.tsx
2. **`app/pillars/content/components/ParsePreview/`** (modular architecture)
3. **`components/content/ParsePreview.tsx`** - Standalone component

### Recommendation:
**Keep: `ParsePreview/` (modular architecture)** ✅ BEST VERSION
- ✅ Has API integration via `UnifiedFileAPI.parseFile()`
- ✅ Modular architecture (core, hooks, types, utils, components)
- ✅ Uses `useGlobalSession()` for state management
- ✅ Combines files from all pillar states
- ✅ Proper error handling and validation

**Also Keep: `components/content/ParsePreview.tsx`** (as reference/fallback)
- Has API integration via `parseFile()` from `@/lib/api/fms`
- Uses global session state management
- Has comprehensive tabbed interface (StructuredDataTab, TextDataTab, SOPWorkflowTab, etc.)

**Archive:**
- `ParsePreviewNew.tsx` (incomplete, has TODOs, mock responses only)

---

## 4. MetadataExtractor Component

### Versions Found:
1. **`MetadataExtractorNew.tsx`** - Currently used in page.tsx
2. **`components/content/MetadataExtraction.tsx`** - Different name, may be related

### Recommendation:
**Keep: `components/content/MetadataExtraction.tsx`** ✅ BEST VERSION
- ✅ Uses semantic API endpoint `/api/content-pillar/list-uploaded-files`
- ✅ Uses semantic API endpoint `/api/content-pillar/get-file-details/${fileId}`
- ✅ Comprehensive metadata extraction (data summary, semantic summary, categorization)
- ✅ Proper error handling

**Archive:**
- `MetadataExtractorNew.tsx` (incomplete, has TODOs, mock responses only)

---

## 5. InsightsDashboard Component

### Versions Found:
1. **`InsightsDashboardNew.tsx`** - Currently used in page.tsx
2. No other versions found

### Recommendation:
**Keep: `InsightsDashboardNew.tsx`** (only version)
- Rename to `InsightsDashboard.tsx`

---

## Action Plan

### Phase 1: Review All Versions ✅ COMPLETE
1. ✅ Compare FileUploader versions
2. ✅ Review FileDashboard versions
3. ✅ Review ParsePreview versions
4. ✅ Review MetadataExtractor versions
5. ✅ InsightsDashboard (only one version)

### Phase 2: Determine Best Versions ✅ COMPLETE
**Decisions Made:**
- **FileUploader**: Keep `FileUploader/` (modular) - BEST
- **FileDashboard**: Keep `FileDashboard/` (modular) - BEST
- **ParsePreview**: Keep `ParsePreview/` (modular) - BEST
- **MetadataExtractor**: Keep `components/content/MetadataExtraction.tsx` - BEST
- **InsightsDashboard**: Keep `InsightsDashboardNew.tsx` (only version) - Rename to `InsightsDashboard.tsx`

### Phase 3: Archive and Rename
1. **Archive to `archive/parallel-components/`:**
   - `FileUploaderNew.tsx`
   - `FileDashboardNew.tsx`
   - `ParsePreviewNew.tsx`
   - `MetadataExtractorNew.tsx`

2. **Rename:**
   - `InsightsDashboardNew.tsx` → `InsightsDashboard.tsx`

3. **Update imports in `page.tsx` files:**
   - `app/pillars/content/page.tsx`: Update to use modular versions
   - `app/pillars/insights/page.tsx`: Update to use `InsightsDashboard`

### Phase 4: Add Semantic Test IDs
- Add `data-testid` attributes to the chosen components
- Ensure E2E tests can find them

---

## Final Recommendations Summary

| Component | Keep | Archive | Notes |
|-----------|------|---------|-------|
| **FileUploader** | `FileUploader/` (modular) | `FileUploaderNew.tsx` | Modular has API integration |
| **FileDashboard** | `FileDashboard/` (modular) | `FileDashboardNew.tsx` | Modular has API integration |
| **ParsePreview** | `ParsePreview/` (modular) | `ParsePreviewNew.tsx` | Modular has API integration |
| **MetadataExtractor** | `components/content/MetadataExtraction.tsx` | `MetadataExtractorNew.tsx` | Uses semantic APIs |
| **InsightsDashboard** | `InsightsDashboardNew.tsx` → Rename | None | Only version, rename it |

---

## Next Steps
1. ✅ Review all components (DONE)
2. ⏳ Archive old versions to `archive/parallel-components/`
3. ⏳ Update `app/pillars/content/page.tsx` to use modular versions
4. ⏳ Rename `InsightsDashboardNew.tsx` to `InsightsDashboard.tsx`
5. ⏳ Update `app/pillars/insights/page.tsx` import
6. ⏳ Add semantic test IDs to chosen components
7. ⏳ Review and validate E2E refactoring (frontend and backend)
8. ⏳ Design test to validate semantic API system
9. ⏳ Update E2E test to reflect new component flow

