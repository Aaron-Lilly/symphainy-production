# Data Lineage and Traceability Strategic Analysis

## Executive Summary

This document evaluates the current data lineage/traceability implementation and proposes a strategic refactoring to simplify the flow, improve UI usability, and make the platform's capabilities more intuitive.

## Current Flow Analysis

### 1. File Upload Flow ✅
**Current Implementation:**
- User uploads file → Supabase `project_files` table (metadata)
- File stored in GCS (binary data)
- Metadata includes: `uuid`, `user_id`, `tenant_id`, `ui_name`, `file_type`, `status`, etc.
- **Lineage**: Direct link via `uuid` (file_id)

**Status**: ✅ **Working well**

### 2. Parsed File Flow ⚠️
**Current Implementation:**
- Parsed files stored in GCS via `file_management_abstraction.create_file()`
- Gets new UUID (parsed_file_id) in `project_files` table
- Metadata stored in `parsed_data_files` table with:
  - `file_id` → links to original file
  - `parsed_file_id` → GCS file UUID
  - `ui_name` → `"parsed_{original_file_name}"` (UI-friendly name)
- File link created in `file_links` table (parent → child)

**Issues:**
1. Parsed files appear in `project_files` but with `status="parsed"`, which can confuse dashboard statistics
2. Dashboard only queries `project_files` table, so it counts parsed files as "uploaded" files
3. Two separate storage locations: `project_files` (for GCS file) and `parsed_data_files` (for metadata)

**Status**: ⚠️ **Functional but confusing**

### 3. Embedding Flow ❌
**Current Implementation:**
- Embeddings stored in ArangoDB `structured_embeddings` collection
- Each embedding document has:
  - `file_id` → original file UUID
  - `parsed_file_id` → parsed file UUID (if available)
  - `content_id` → content metadata ID
  - `column_name` or `chunk_index` → identifier
  - **NO UI-friendly name**
- Frontend tries to match embeddings to parsed files by `parsed_file_id` or `file_id`

**Issues:**
1. **No UI-friendly name** for embeddings → can't display them directly in UI
2. Frontend must query parsed files, then query embeddings, then match them → complex
3. Embeddings are stored as individual documents (one per column/chunk), not grouped by "embedding file"
4. Dashboard can't count embeddings as a separate category

**Status**: ❌ **Not UI-friendly**

## Root Cause Analysis

### Problem 1: Dashboard Statistics
**Root Cause**: Dashboard only queries `project_files` table and filters by `status`. Parsed files are stored as separate records in `project_files` with `status="parsed"`, but the dashboard logic doesn't distinguish between:
- Original uploaded files (status="uploaded")
- Parsed file records (status="parsed" but are derived files)

**Impact**: Shows "8 uploaded files" instead of "6 uploaded, 2 parsed"

### Problem 2: Embedding Display
**Root Cause**: Embeddings don't have a UI-friendly name or a "file-like" representation. They're stored as individual documents in ArangoDB, not as a cohesive "embedding file" that can be displayed in dropdowns.

**Impact**: Frontend must do complex matching logic to link embeddings back to parsed files, and even then can't display them as a first-class file type.

### Problem 3: Data Lineage Complexity
**Root Cause**: Three separate storage systems:
- `project_files` (Supabase) → original files
- `parsed_data_files` (Supabase) → parsed file metadata
- `structured_embeddings` (ArangoDB) → embeddings

Each has different query patterns, making it hard to build unified dashboards and file selectors.

## Proposed Solution: Unified File-Like Representation

### Core Principle
**Treat embeddings as first-class "files" with UI-friendly names**, similar to how parsed files are handled.

### Architecture Changes

#### 1. Embedding File Metadata (New)
**Create a new table or extend existing schema:**

```sql
-- Option A: New table (recommended for clarity)
CREATE TABLE embedding_files (
  uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  parsed_file_id TEXT NOT NULL,           -- Links to parsed file
  file_id TEXT NOT NULL,                  -- Links to original file
  user_id TEXT NOT NULL,
  tenant_id TEXT,
  ui_name TEXT NOT NULL,                  -- UI-friendly name (e.g., "Embeddings: sales_data.csv")
  content_id TEXT,                        -- Content metadata ID
  embeddings_count INTEGER DEFAULT 0,      -- Number of embeddings in this "file"
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  metadata JSONB                          -- Additional metadata
);

-- Option B: Extend parsed_data_files (simpler, but mixes concerns)
-- Add columns to parsed_data_files:
--   has_embeddings BOOLEAN DEFAULT FALSE,
--   embeddings_file_id UUID,
--   embeddings_count INTEGER DEFAULT 0
```

**Recommendation**: **Option A** (new table) for clarity and separation of concerns.

#### 2. Embedding Storage Pattern
**When creating embeddings:**
1. Create an "embedding file" record in `embedding_files` table with:
   - `ui_name` = `"Embeddings: {original_file_name}"`
   - `parsed_file_id` = parsed file UUID
   - `file_id` = original file UUID
   - `embeddings_count` = number of embeddings created
2. Store embeddings in ArangoDB with:
   - `embedding_file_id` = UUID from `embedding_files` table (NEW)
   - `parsed_file_id` = parsed file UUID (existing)
   - `file_id` = original file UUID (existing)

#### 3. Unified Query Pattern
**For dashboards and file selectors:**
```python
# Query all file types in one place
files = {
    "uploaded": query_project_files(user_id, status="uploaded"),
    "parsed": query_parsed_data_files(user_id),  # Already has UI-friendly names
    "embeddings": query_embedding_files(user_id)  # NEW: Direct query with UI-friendly names
}
```

### Implementation Plan

#### Phase 1: Create Embedding Files Table
1. Create `embedding_files` table in Supabase
2. Add migration script
3. Update schema documentation

#### Phase 2: Update Embedding Creation Flow
1. Modify `EmbeddingService.create_embeddings()` to:
   - Create `embedding_files` record BEFORE storing embeddings
   - Set `ui_name` based on original file name
   - Store `embedding_file_id` in each embedding document
2. Update `SemanticDataAbstraction.store_semantic_embeddings()` to accept `embedding_file_id`
3. Update `EmbeddingCreation.create_representative_embeddings()` to create embedding file record

#### Phase 3: Update Query Endpoints
1. Create `list_embedding_files(user_id)` endpoint
2. Update `list_parsed_files_with_embeddings()` to use `embedding_files` table
3. Simplify matching logic (no more complex joins)

#### Phase 4: Update Dashboard
1. Query `embedding_files` table separately
2. Display embeddings as a separate category
3. Show statistics: "X uploaded, Y parsed, Z embedded"

#### Phase 5: Update Frontend
1. Add "Embedding Files" to file selectors
2. Display embeddings directly (no matching logic needed)
3. Update dashboard to show embedding statistics

## Benefits

### 1. Simplified UI Logic
- **Before**: Frontend queries parsed files → queries embeddings → matches by `parsed_file_id` → displays
- **After**: Frontend queries `embedding_files` → displays directly (like parsed files)

### 2. Better Dashboard Statistics
- **Before**: "8 uploaded files" (includes parsed files)
- **After**: "6 uploaded, 2 parsed, 2 embedded" (clear separation)

### 3. Consistent File Representation
- All file types (uploaded, parsed, embedded) have:
  - UI-friendly name
  - Direct query endpoint
  - Consistent metadata structure

### 4. Improved Data Lineage
- Clear lineage chain:
  - Original file (`project_files`) → `file_id`
  - Parsed file (`parsed_data_files`) → `parsed_file_id`, `file_id`
  - Embedding file (`embedding_files`) → `embedding_file_id`, `parsed_file_id`, `file_id`
  - Embeddings (ArangoDB) → `embedding_file_id`, `parsed_file_id`, `file_id`

## Migration Strategy

### Backward Compatibility
1. **Existing embeddings**: Create `embedding_files` records retroactively by:
   - Querying ArangoDB for all embeddings
   - Grouping by `parsed_file_id` or `file_id`
   - Creating `embedding_files` records with appropriate `ui_name`
   - Updating embedding documents with `embedding_file_id`

2. **Gradual rollout**: 
   - New embeddings use new flow
   - Old embeddings continue to work (with fallback matching)
   - Migration script runs in background

## Alternative: Simpler Approach (If New Table Is Too Much)

If creating a new table is too complex, we can:

1. **Extend `parsed_data_files` table:**
   - Add `has_embeddings BOOLEAN`
   - Add `embeddings_count INTEGER`
   - Add `embeddings_created_at TIMESTAMPTZ`
   - Use existing `ui_name` from parsed file (e.g., "Parsed: sales_data.csv")

2. **Update embedding creation:**
   - When embeddings are created, update `parsed_data_files` record
   - Set `has_embeddings = TRUE`
   - Set `embeddings_count = X`

3. **Update frontend:**
   - Query `parsed_data_files` with `has_embeddings = TRUE`
   - Display as "Embeddings: {parsed_file_name}"

**Trade-off**: Simpler implementation, but mixes parsed file metadata with embedding metadata.

## Recommendation

**Recommend Option A (new `embedding_files` table)** because:
1. Clear separation of concerns
2. Embeddings are a distinct "file type" in the platform
3. Easier to extend in the future (e.g., embedding versions, multiple embedding sets per parsed file)
4. Consistent with how parsed files are handled (separate table)

## Next Steps

1. **Review and approve** this strategic approach
2. **Create implementation plan** with specific tasks
3. **Implement Phase 1** (table creation)
4. **Test with existing data** (migration script)
5. **Roll out incrementally** (new embeddings first, then migrate old)

## Questions for Discussion

1. Should embeddings be a separate "file type" or an attribute of parsed files?
2. Do we need to support multiple embedding sets per parsed file (e.g., different models)?
3. Should embedding files be deletable independently, or cascade from parsed file deletion?
4. Do we need embedding file versions (if embeddings are regenerated)?

