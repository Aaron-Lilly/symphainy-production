# Unified File Metadata Pattern

## Overview

This document describes the standardized metadata pattern across all three file metadata tables in the SymphAIny platform:
- `project_files` (uploaded files)
- `parsed_data_files` (parsed files)
- `embedding_files` (embedding files)

## Standardized Schema Fields

All three tables now include these common fields for unified query patterns:

### Core Identifiers
- `uuid` / `parsed_file_id` / `uuid` - Primary key
- `file_id` - Link to original uploaded file (from `project_files`)
- `user_id` - User who owns/created the file (enables direct queries without JOINs)
- `tenant_id` - Tenant for multi-tenant security

### UI Display
- `ui_name` - **UI-friendly display name** (e.g., "Balances", "parsed_Balances", "Embeddings: Balances")
  - Enables direct display in dropdowns and lists
  - No need to JOIN with other tables or fetch from GCS
  - Consistent naming pattern across all file types

### Data Classification
- `data_classification` - 'platform' or 'client'
- `tenant_id` - Required for client data, NULL for platform data

### Status & Processing
- `status` - Current status (uploaded/parsed/embedded, processing, completed, failed)
- `processing_status` - Processing pipeline status
- `created_at` / `parsed_at` / `created_at` - Timestamp

## Benefits

### 1. Simplified Queries
**Before (required JOINs):**
```sql
SELECT p.*, pf.ui_name 
FROM parsed_data_files p
JOIN project_files pf ON p.file_id = pf.uuid
WHERE p.user_id = 'user123';
```

**After (direct query):**
```sql
SELECT * FROM parsed_data_files
WHERE user_id = 'user123';
-- ui_name is already in the table!
```

### 2. Faster Performance
- No JOINs needed for basic file listings
- Direct index lookups on `user_id` and `ui_name`
- Reduced database load

### 3. Consistent Frontend Patterns
All three file types can be queried and displayed using the same pattern:
```typescript
// Uploaded files
const uploadedFiles = await listFiles(userId);
// Returns: [{ id, ui_name, file_id, ... }]

// Parsed files
const parsedFiles = await listParsedFiles(userId);
// Returns: [{ parsed_file_id, ui_name, file_id, ... }]

// Embedding files
const embeddingFiles = await listEmbeddingFiles(userId);
// Returns: [{ embedding_file_id, ui_name, file_id, parsed_file_id, ... }]
```

### 4. Easier Data Mash Integration
The Data Mash UI can now:
- Query parsed files directly by `user_id` and get `ui_name` immediately
- Match parsed files to embedding files by `parsed_file_id`
- Display all file types with consistent naming

## Migration Path

### Phase 1: Add `ui_name` to `parsed_data_files` ✅
- Migration script: `add_ui_name_to_parsed_data_files.sql`
- Backfills existing records from metadata or constructs from `parsed_file_id`

### Phase 2: Update Creation Code ✅
- `parsed_file_processing.py` now stores `ui_name` when creating parsed files
- Format: `f"parsed_{original_file.get('ui_name', file_id)}"`

### Phase 3: Simplify Query Code ✅
- `list_parsed_files()` now uses `ui_name` directly from table
- Removed JOINs and GCS lookups for name retrieval

### Phase 4: Update Data Mash (Next)
- Update Data Mash to use `list-parsed-files-with-embeddings` endpoint
- Use `ui_name` directly from parsed files
- Match by `parsed_file_id` instead of `file_id`

## Data Lineage Pattern

The unified pattern maintains clear lineage:

```
project_files (ui_name: "Balances")
    ↓ file_id
parsed_data_files (ui_name: "parsed_Balances", file_id: <original>)
    ↓ parsed_file_id
embedding_files (ui_name: "Embeddings: Balances", parsed_file_id: <parsed>, file_id: <original>)
```

Each level:
- Links to parent via `file_id` or `parsed_file_id`
- Has its own `ui_name` for direct display
- Can be queried independently by `user_id`

## Best Practices

1. **Always store `ui_name`** when creating file records
2. **Use `ui_name` directly** from tables (don't JOIN unless necessary)
3. **Maintain naming consistency**: 
   - Original: `"Balances"`
   - Parsed: `"parsed_Balances"`
   - Embeddings: `"Embeddings: Balances"`
4. **Query by `user_id` first** for performance (indexed field)
5. **Use `parsed_file_id` for matching** between parsed and embedding files

## Future Enhancements

1. Add `ui_name` to other derived file types (if any)
2. Create unified query functions that work across all three tables
3. Add full-text search on `ui_name` for better file discovery
4. Standardize metadata JSONB structure across all tables




