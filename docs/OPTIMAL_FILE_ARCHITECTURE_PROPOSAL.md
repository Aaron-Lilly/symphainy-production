# Optimal File Architecture Proposal

## Executive Summary

**Current Problem:** We're over-leveraging `project_files` table just to support the dashboard, creating duplicate entries and complexity.

**Proposed Solution:** Clear separation of concerns with three distinct tables, and a unified dashboard service that queries all three tables to compose the view.

## Core Architectural Principle

**Role = What, Service = How**

Each table has a **clear role (WHAT)**:
- `project_files` → Original uploaded files
- `parsed_data_files` → Parsed file metadata  
- `embedding_files` → Embedding metadata

The dashboard **service (HOW)** queries all three tables and composes a unified view.

## Proposed Architecture

### 1. Table Responsibilities (Clear Separation)

#### `project_files` Table
**Role:** Store ONLY original uploaded files
- **Status:** Always `status="uploaded"` (never "parsed")
- **Content:** Original file binary in GCS + metadata
- **Lineage:** Parent of all derived files
- **No Duplication:** Parsed files are NOT stored here

#### `parsed_data_files` Table  
**Role:** Store parsed file metadata and lineage
- **Content:** Parsed file binary in GCS + metadata
- **Lineage:** `file_id` → links to original `project_files.uuid`
- **UI Name:** Stored in `ui_name` column (e.g., "parsed_Balances")
- **Status:** `status="parsed"` (for filtering/display)
- **No Duplication:** Single source of truth for parsed files

#### `embedding_files` Table
**Role:** Store embedding metadata and lineage
- **Content:** Embedding documents in ArangoDB + metadata
- **Lineage:** 
  - `parsed_file_id` → links to `parsed_data_files.parsed_file_id`
  - `file_id` → links to original `project_files.uuid`
- **UI Name:** Stored in `ui_name` column (e.g., "embeddings_Balances")
- **Status:** `status="embedded"` (for filtering/display)

### 2. Data Flow (Clean Lineage)

```
User Uploads File
  ↓
project_files (status="uploaded", ui_name="Balances")
  ↓
User Parses File
  ↓
parsed_data_files (status="parsed", ui_name="parsed_Balances", file_id→project_files.uuid)
  ↓
User Creates Embeddings
  ↓
embedding_files (status="embedded", ui_name="embeddings_Balances", 
                 parsed_file_id→parsed_data_files.parsed_file_id,
                 file_id→project_files.uuid)
```

### 3. Dashboard Service (Unified Query)

**New Service:** `FileDashboardService` (or method in `ContentStewardService`)

**How It Works:**
```python
async def get_dashboard_files(user_id: str) -> List[Dict[str, Any]]:
    """
    Query all three tables and compose unified file list for dashboard.
    
    Returns unified list with:
    - Original files from project_files
    - Parsed files from parsed_data_files  
    - Embedded files from embedding_files
    """
    files = []
    
    # 1. Get original uploaded files
    uploaded_files = await file_management.list_files(
        user_id=user_id,
        filters={"status": "uploaded", "deleted": False}
    )
    for f in uploaded_files:
        files.append({
            "uuid": f["uuid"],
            "ui_name": f["ui_name"],
            "status": "uploaded",
            "file_type": f["file_type"],
            "size": f["file_size"],
            "created_at": f["created_at"],
            "type": "original"
        })
    
    # 2. Get parsed files
    parsed_files = await content_steward.list_parsed_files(user_id=user_id)
    for pf in parsed_files:
        files.append({
            "uuid": pf["uuid"],  # parsed_data_files.uuid
            "ui_name": pf["ui_name"],  # e.g., "parsed_Balances"
            "status": "parsed",
            "file_type": pf["format_type"],
            "size": pf["file_size"],
            "created_at": pf["parsed_at"],
            "original_file_id": pf["file_id"],  # Link to original
            "type": "parsed"
        })
    
    # 3. Get embedded files
    embedded_files = await content_steward.list_embedding_files(user_id=user_id)
    for ef in embedded_files:
        files.append({
            "uuid": ef["uuid"],  # embedding_files.uuid
            "ui_name": ef["ui_name"],  # e.g., "embeddings_Balances"
            "status": "embedded",
            "file_type": "embeddings",
            "size": ef.get("size", 0),
            "created_at": ef["created_at"],
            "parsed_file_id": ef["parsed_file_id"],  # Link to parsed file
            "original_file_id": ef["file_id"],  # Link to original
            "type": "embedded"
        })
    
    # Sort by created_at (most recent first)
    files.sort(key=lambda x: x["created_at"], reverse=True)
    
    return files
```

### 4. Statistics Service (Unified Counting)

**How It Works:**
```python
async def get_file_statistics(user_id: str) -> Dict[str, Any]:
    """
    Count files from each table separately (no duplication).
    """
    # Count from project_files (only uploaded files)
    uploaded_count = len(await file_management.list_files(
        user_id=user_id,
        filters={"status": "uploaded", "deleted": False}
    ))
    
    # Count from parsed_data_files
    parsed_count = len(await content_steward.list_parsed_files(user_id=user_id))
    
    # Count from embedding_files
    embedded_count = len(await content_steward.list_embedding_files(user_id=user_id))
    
    return {
        "uploaded": uploaded_count,
        "parsed": parsed_count,
        "embedded": embedded_count,
        "total": uploaded_count + parsed_count + embedded_count
    }
```

### 5. Delete (Simple Direct Deletion)

**How It Works:**
```python
async def delete_file(file_uuid: str, file_type: str) -> bool:
    """
    Delete file directly from its table and GCS.
    No cascade - users delete what they want to delete.
    
    Args:
        file_uuid: UUID of file to delete
        file_type: "original", "parsed", or "embedded"
    """
    if file_type == "original":
        # Delete from project_files and GCS
        await file_management.delete_file(file_uuid)
        
    elif file_type == "parsed":
        # Get parsed file metadata to find GCS path
        parsed_file = await content_steward.get_parsed_file(file_uuid)
        if parsed_file:
            gcs_path = parsed_file.get("metadata", {}).get("gcs_path")
            if gcs_path:
                # Delete from GCS
                await gcs_adapter.delete_file(gcs_path)
            
            # Delete from parsed_data_files
            await supabase_adapter.client.table("parsed_data_files").delete().eq("uuid", file_uuid).execute()
        
    elif file_type == "embedded":
        # Get embedding metadata to find ArangoDB documents
        embedding_file = await content_steward.get_embedding_file(file_uuid)
        if embedding_file:
            # Delete embeddings from ArangoDB (if needed)
            # Note: Embeddings might be stored differently, adjust as needed
            
            # Delete from embedding_files
            await supabase_adapter.client.table("embedding_files").delete().eq("uuid", file_uuid).execute()
    
    return True
```

## Benefits of This Architecture

### 1. **Clear Separation of Concerns**
- Each table has a single, clear responsibility
- No duplication or confusion about where data lives
- Easy to understand and maintain

### 2. **Simplified Data Flow**
- Upload → `project_files`
- Parse → `parsed_data_files` (with `file_id` link)
- Embed → `embedding_files` (with `parsed_file_id` and `file_id` links)
- Clear lineage chain

### 3. **Accurate Statistics**
- Count from each table separately
- No double-counting
- Easy to verify correctness

### 4. **Simple Direct Deletion**
- Users delete what they want to delete
- No automatic cascade - gives users control
- Delete from table + GCS/ArangoDB
- Clean and straightforward

### 5. **Flexible Dashboard**
- Can show all files, or filter by type
- Can show lineage relationships
- Can group by original file
- Easy to extend with new file types

### 6. **Performance**
- Each table optimized for its use case
- No unnecessary JOINs
- Can query only what's needed

## Migration Path

### Phase 1: Update `store_parsed_file()`
- Remove creation of entry in `project_files`
- Only create entry in `parsed_data_files`
- Store `ui_name` in `parsed_data_files.ui_name` column

### Phase 2: Create Dashboard Service
- Implement `get_dashboard_files()` method
- Query all three tables
- Compose unified response

### Phase 3: Update Frontend
- Update dashboard to use new unified endpoint
- Handle different file types in UI
- Show lineage relationships

### Phase 4: Cleanup
- Run cleanup script to remove duplicate entries
- Verify statistics are correct
- Test delete cascade

## Schema Changes Needed

### `parsed_data_files` Table
Add columns (if not already present):
- `ui_name TEXT` - For dashboard display
- `user_id TEXT` - For direct queries (currently in metadata JSONB)

### `embedding_files` Table  
Ensure columns exist:
- `ui_name TEXT` - For dashboard display
- `user_id TEXT` - For direct queries
- `parsed_file_id TEXT` - Link to parsed file
- `file_id UUID` - Link to original file

## API Endpoint Changes

### New Endpoint: `/api/v1/content-solution/dashboard/files`
```python
GET /api/v1/content-solution/dashboard/files?user_id={user_id}
Response: {
    "success": True,
    "files": [
        {
            "uuid": "...",
            "ui_name": "Balances",
            "status": "uploaded",
            "type": "original",
            ...
        },
        {
            "uuid": "...",
            "ui_name": "parsed_Balances",
            "status": "parsed",
            "type": "parsed",
            "original_file_id": "...",
            ...
        },
        ...
    ],
    "statistics": {
        "uploaded": 6,
        "parsed": 2,
        "embedded": 0,
        "total": 8
    }
}
```

## Comparison: Current vs. Proposed

| Aspect | Current (Problematic) | Proposed (Optimal) |
|--------|----------------------|-------------------|
| **Parsed Files Storage** | Both `project_files` AND `parsed_data_files` | Only `parsed_data_files` |
| **Dashboard Query** | Single table (`project_files`) | Three tables (unified service) |
| **Statistics** | Risk of double-counting | Accurate (one count per table) |
| **Delete** | Complex (cascade logic) | Simple (direct deletion) |
| **Data Integrity** | Risk of orphaned records | Clean (foreign key relationships) |
| **Complexity** | High (duplication) | Low (clear separation) |

## Conclusion

This architecture:
- ✅ Eliminates duplication
- ✅ Maintains clear separation of concerns
- ✅ Aligns with Role=What, Service=How pattern
- ✅ Simplifies delete cascade
- ✅ Provides accurate statistics
- ✅ Enables flexible dashboard views
- ✅ Reduces complexity and confusion

The key insight: **Don't force data into `project_files` just for the dashboard. Instead, build a dashboard service that queries all relevant tables and composes a unified view.**

