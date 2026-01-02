# Optimal File Architecture Implementation Plan

## Overview

This plan implements the optimal file architecture where:
- `project_files` → Only original uploaded files
- `parsed_data_files` → Only parsed files
- `embedding_files` → Only embeddings
- Dashboard service queries all three tables
- Simple direct deletion (no cascade)

## Implementation Steps

### Phase 1: Update `store_parsed_file()` - Remove `project_files` Entry

**File:** `symphainy-platform/backend/smart_city/services/content_steward/modules/parsed_file_processing.py`

**Changes:**
1. Remove creation of entry in `project_files` table
2. Only create entry in `parsed_data_files` table
3. Store parsed file binary in GCS
4. Store `ui_name` in `parsed_data_files.ui_name` column

**Code:**
```python
async def store_parsed_file(...):
    # Store parsed file binary in GCS
    parsed_file_id = str(uuid.uuid4())
    gcs_path = f"parsed_data/{parsed_file_id}.{format_type}"
    
    # Upload to GCS
    await gcs_adapter.upload_file(gcs_path, parsed_file_data, ...)
    
    # Create entry ONLY in parsed_data_files (NOT in project_files)
    parsed_file_metadata = {
        "file_id": file_id,  # Link to original
        "parsed_file_id": parsed_file_id,
        "ui_name": f"parsed_{original_ui_name}",  # Store in column
        "user_id": user_id,  # Store in column (if schema has it)
        "format_type": format_type,
        "content_type": content_type,
        "status": "parsed",
        "metadata": {
            "gcs_path": gcs_path,
            "gcs_file_id": parsed_file_id
        },
        ...
    }
    
    # Insert into parsed_data_files only
    await supabase_adapter.client.table("parsed_data_files").insert(parsed_file_metadata).execute()
```

### Phase 2: Create Dashboard Service Method

**File:** `symphainy-platform/backend/smart_city/services/content_steward/content_steward_service.py`

**New Method:**
```python
async def get_dashboard_files(
    self,
    user_id: str,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get unified file list for dashboard from all three tables.
    
    Returns:
        Dict with files list and statistics
    """
    files = []
    
    # 1. Get original uploaded files from project_files
    uploaded_files = await self.file_management_abstraction.list_files(
        user_id=user_id,
        filters={"status": "uploaded", "deleted": False}
    )
    for f in uploaded_files:
        files.append({
            "uuid": f["uuid"],
            "ui_name": f["ui_name"],
            "status": "uploaded",
            "file_type": f["file_type"],
            "size": f.get("file_size", 0),
            "created_at": f.get("created_at", ""),
            "type": "original"
        })
    
    # 2. Get parsed files from parsed_data_files
    parsed_files = await self.list_parsed_files(user_id=user_id, user_context=user_context)
    for pf in parsed_files:
        files.append({
            "uuid": pf["uuid"],  # parsed_data_files.uuid
            "ui_name": pf.get("ui_name", f"parsed_{pf.get('parsed_file_id', '')}"),
            "status": "parsed",
            "file_type": pf.get("format_type", ""),
            "size": pf.get("file_size", 0),
            "created_at": pf.get("parsed_at", pf.get("created_at", "")),
            "original_file_id": pf.get("file_id"),  # Link to original
            "type": "parsed"
        })
    
    # 3. Get embedded files from embedding_files
    embedded_files = await self.list_embedding_files(user_id=user_id, user_context=user_context)
    for ef in embedded_files:
        files.append({
            "uuid": ef["uuid"],  # embedding_files.uuid
            "ui_name": ef.get("ui_name", f"embeddings_{ef.get('parsed_file_id', '')}"),
            "status": "embedded",
            "file_type": "embeddings",
            "size": ef.get("size", 0),
            "created_at": ef.get("created_at", ""),
            "parsed_file_id": ef.get("parsed_file_id"),  # Link to parsed file
            "original_file_id": ef.get("file_id"),  # Link to original
            "type": "embedded"
        })
    
    # Sort by created_at (most recent first)
    files.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Calculate statistics
    statistics = {
        "uploaded": len([f for f in files if f["type"] == "original"]),
        "parsed": len([f for f in files if f["type"] == "parsed"]),
        "embedded": len([f for f in files if f["type"] == "embedded"]),
        "total": len(files)
    }
    
    return {
        "success": True,
        "files": files,
        "statistics": statistics
    }
```

### Phase 3: Create Delete Method with File Type

**File:** `symphainy-platform/backend/smart_city/services/content_steward/content_steward_service.py`

**New Method:**
```python
async def delete_file_by_type(
    self,
    file_uuid: str,
    file_type: str,  # "original", "parsed", or "embedded"
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Delete file directly from its table and storage.
    No cascade - users delete what they want to delete.
    
    Args:
        file_uuid: UUID of file to delete
        file_type: "original", "parsed", or "embedded"
    """
    try:
        if file_type == "original":
            # Delete from project_files and GCS
            result = await self.file_management_abstraction.delete_file(file_uuid)
            return {
                "success": result,
                "file_uuid": file_uuid,
                "file_type": file_type,
                "message": "Original file deleted"
            }
            
        elif file_type == "parsed":
            # Get parsed file metadata to find GCS path
            parsed_file = await self.get_parsed_file(file_uuid, user_context)
            if not parsed_file:
                return {
                    "success": False,
                    "error": f"Parsed file not found: {file_uuid}"
                }
            
            # Delete from GCS
            gcs_path = parsed_file.get("metadata", {}).get("gcs_path")
            if gcs_path:
                gcs_adapter = self.file_management_abstraction.gcs_adapter
                if gcs_adapter:
                    await gcs_adapter.delete_file(gcs_path)
            
            # Delete from parsed_data_files
            supabase_adapter = self.file_management_abstraction.supabase_adapter
            supabase_adapter.client.table("parsed_data_files").delete().eq("uuid", file_uuid).execute()
            
            return {
                "success": True,
                "file_uuid": file_uuid,
                "file_type": file_type,
                "message": "Parsed file deleted"
            }
            
        elif file_type == "embedded":
            # Get embedding metadata
            embedding_file = await self.get_embedding_file(file_uuid, user_context)
            if not embedding_file:
                return {
                    "success": False,
                    "error": f"Embedding file not found: {file_uuid}"
                }
            
            # Delete embeddings from ArangoDB (if needed)
            # Note: Implementation depends on how embeddings are stored
            
            # Delete from embedding_files
            supabase_adapter = self.file_management_abstraction.supabase_adapter
            supabase_adapter.client.table("embedding_files").delete().eq("uuid", file_uuid).execute()
            
            return {
                "success": True,
                "file_uuid": file_uuid,
                "file_type": file_type,
                "message": "Embedding file deleted"
            }
        else:
            return {
                "success": False,
                "error": f"Invalid file_type: {file_type}. Must be 'original', 'parsed', or 'embedded'"
            }
            
    except Exception as e:
        self.logger.error(f"❌ Failed to delete file {file_uuid} (type: {file_type}): {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

### Phase 4: Update API Endpoint

**File:** Create new endpoint or update existing in Content Solution Orchestrator

**New Endpoint:** `/api/v1/content-solution/dashboard/files`

```python
@router.get("/dashboard/files")
async def get_dashboard_files(
    user_id: str = Query(...),
    # ... auth headers ...
):
    """Get unified file list for dashboard."""
    content_steward = await get_content_steward_api()
    result = await content_steward.get_dashboard_files(user_id=user_id)
    return result

@router.delete("/dashboard/files/{file_uuid}")
async def delete_dashboard_file(
    file_uuid: str,
    file_type: str = Query(..., description="File type: original, parsed, or embedded"),
    # ... auth headers ...
):
    """Delete file from dashboard."""
    content_steward = await get_content_steward_api()
    result = await content_steward.delete_file_by_type(
        file_uuid=file_uuid,
        file_type=file_type
    )
    return result
```

### Phase 5: Update Frontend

**File:** Frontend dashboard component

**Changes:**
1. Update API call to use new `/dashboard/files` endpoint
2. Handle `type` field in file objects
3. Update delete to pass `file_type` parameter
4. Display file type in UI (optional)

## Migration Checklist

- [ ] Phase 1: Update `store_parsed_file()` - Remove `project_files` entry creation
- [ ] Phase 2: Create `get_dashboard_files()` method
- [ ] Phase 3: Create `delete_file_by_type()` method
- [ ] Phase 4: Create/update API endpoints
- [ ] Phase 5: Update frontend dashboard
- [ ] Test: Upload → Parse → View dashboard → Delete
- [ ] Test: Statistics accuracy
- [ ] Run cleanup script to remove old duplicate entries

## Benefits After Implementation

1. ✅ No duplication - each file type in one table
2. ✅ Simple deletion - direct delete, no cascade logic
3. ✅ Accurate statistics - count each table separately
4. ✅ Clear architecture - aligns with Role=What, Service=How
5. ✅ User control - users delete what they want
6. ✅ Easy to maintain - clear separation of concerns


