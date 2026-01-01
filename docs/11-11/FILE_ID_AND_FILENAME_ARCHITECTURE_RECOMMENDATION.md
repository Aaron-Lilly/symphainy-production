# File ID and Filename Architecture Recommendation

## Current State Analysis

### The Problem
When a user uploads `userfile.docx`, we need to:
1. **Generate a UUID** for platform/backend use (unique identifier)
2. **Preserve original filename** for user display (dashboard, UI)
3. **Extract file extension** for parsing/insights logic
4. **Track file type** for content pillar tiles and processing patterns

### Current Implementation Issues

#### 1. **Inconsistent Field Naming**
- **Supabase Schema** uses: `uuid`, `ui_name`, `file_type`
- **Content Steward** expects: `ui_name` in metadata
- **Content Orchestrator** passes: `filename` in metadata
- **API Response** returns: `file_id` (which should be `uuid`)

#### 2. **Missing Filename Parsing**
Currently in `content_analysis_orchestrator.py`:
```python
metadata = {
    "filename": filename,  # ❌ Should be "ui_name"
    "file_type": file_type,  # ⚠️ This is MIME type, not extension
    ...
}
```

But Content Steward expects:
```python
"ui_name": metadata.get("ui_name")  # ❌ Gets None because we pass "filename"
```

#### 3. **File Type Confusion**
- `file_type` in metadata is MIME type (e.g., `"application/vnd.openxmlformats-officedocument.wordprocessingml.document"`)
- `file_type` in Supabase schema is extension/type (e.g., `"docx"` or `".docx"`)
- Need to extract extension from filename AND determine content type

#### 4. **File ID Return Value**
- Content Steward returns `uuid` from Supabase
- But API returns `file_id` which might be `None` if mapping is wrong
- Test failure shows: `"file_id": "None"` (string, not actual UUID)

## Recommended Architecture Pattern

### Core Principles

1. **UUID = Platform Identifier**: Always use UUID for backend/platform operations
2. **ui_name = User Display Name**: Preserve original filename for UI
3. **file_extension = Parsing Logic**: Extract extension for processing decisions
4. **content_type = Classification**: Determine structured/unstructured/hybrid
5. **mime_type = Technical Type**: Store MIME type for technical operations

### File Component Structure

```python
class FileComponents:
    """Structured file component representation."""
    
    # User-facing
    original_filename: str          # "userfile.docx"
    ui_name: str                     # "userfile" (for display)
    file_extension: str              # ".docx" (with dot)
    file_extension_clean: str        # "docx" (without dot)
    
    # Platform-facing
    uuid: str                        # "550e8400-e29b-41d4-a716-446655440000"
    file_id: str                     # Alias for uuid (for API compatibility)
    
    # Classification
    mime_type: str                   # "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    content_type: str                 # "unstructured" | "structured" | "hybrid"
    file_type_category: str          # "document" | "spreadsheet" | "binary" | "image" | "pdf" | "text"
    
    # Storage
    gcs_blob_name: str               # "files/{uuid}"
    original_path: str               # "files/{uuid}" (same as blob_name)
```

### Implementation Pattern

#### Step 1: Filename Parsing Utility

```python
def parse_filename(filename: str) -> Dict[str, Any]:
    """
    Parse filename into components.
    
    Args:
        filename: Original filename (e.g., "userfile.docx")
        
    Returns:
        {
            "ui_name": "userfile",
            "file_extension": ".docx",
            "file_extension_clean": "docx",
            "original_filename": "userfile.docx"
        }
    """
    import os
    
    # Split filename and extension
    if '.' in filename:
        name, ext = os.path.splitext(filename)
        return {
            "ui_name": name,
            "file_extension": ext,  # Includes dot: ".docx"
            "file_extension_clean": ext.lstrip('.'),  # Without dot: "docx"
            "original_filename": filename
        }
    else:
        return {
            "ui_name": filename,
            "file_extension": "",
            "file_extension_clean": "",
            "original_filename": filename
        }
```

#### Step 2: Content Type Determination

```python
def determine_content_type(file_extension: str, mime_type: str) -> Dict[str, str]:
    """
    Determine content type and file type category.
    
    Args:
        file_extension: File extension (e.g., ".docx")
        mime_type: MIME type
        
    Returns:
        {
            "content_type": "unstructured" | "structured" | "hybrid",
            "file_type_category": "document" | "spreadsheet" | "binary" | "image" | "pdf" | "text"
        }
    """
    ext_lower = file_extension.lower().lstrip('.')
    
    # Structured data
    structured_exts = ['csv', 'xlsx', 'xls', 'json', 'xml', 'parquet']
    if ext_lower in structured_exts:
        return {
            "content_type": "structured",
            "file_type_category": "spreadsheet" if ext_lower in ['xlsx', 'xls', 'csv'] else "data"
        }
    
    # Unstructured documents
    doc_exts = ['doc', 'docx', 'txt', 'md', 'rtf']
    if ext_lower in doc_exts:
        return {
            "content_type": "unstructured",
            "file_type_category": "document"
        }
    
    # PDFs
    if ext_lower == 'pdf':
        return {
            "content_type": "unstructured",
            "file_type_category": "pdf"
        }
    
    # Images
    image_exts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg']
    if ext_lower in image_exts:
        return {
            "content_type": "unstructured",
            "file_type_category": "image"
        }
    
    # Binary files (with copybooks)
    binary_exts = ['dat', 'bin', 'cpy']
    if ext_lower in binary_exts:
        return {
            "content_type": "structured",
            "file_type_category": "binary"
        }
    
    # Default
    return {
        "content_type": "unstructured",
        "file_type_category": "text"
    }
```

#### Step 3: Updated Content Orchestrator

```python
async def handle_content_upload(
    self,
    file_data: bytes,
    filename: str,  # Original filename: "userfile.docx"
    file_type: str,  # MIME type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    user_id: str = "api_user",
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Handle file upload with proper filename parsing."""
    
    # Step 1: Parse filename
    file_components = parse_filename(filename)
    # Result: {
    #   "ui_name": "userfile",
    #   "file_extension": ".docx",
    #   "file_extension_clean": "docx",
    #   "original_filename": "userfile.docx"
    # }
    
    # Step 2: Determine content type
    content_info = determine_content_type(
        file_components["file_extension"],
        file_type
    )
    # Result: {
    #   "content_type": "unstructured",
    #   "file_type_category": "document"
    # }
    
    # Step 3: Prepare metadata for Content Steward
    metadata = {
        "user_id": user_id,
        "ui_name": file_components["ui_name"],  # ✅ Correct field name
        "file_type": file_components["file_extension_clean"],  # ✅ Extension, not MIME
        "mime_type": file_type,  # ✅ MIME type separately
        "original_filename": file_components["original_filename"],  # ✅ Full original name
        "content_type": content_info["content_type"],  # ✅ For Supabase schema
        "file_type_category": content_info["file_type_category"],  # ✅ For processing logic
        "uploaded_at": datetime.utcnow().isoformat(),
        "size_bytes": len(file_data)
    }
    
    # Step 4: Upload via Content Steward
    upload_result = await content_steward.process_upload(
        file_data, 
        file_type,  # MIME type
        metadata
    )
    
    # Step 5: Return with proper field names
    file_uuid = upload_result.get("uuid")  # ✅ Get UUID from Supabase
    
    return {
        "success": True,
        "file_id": file_uuid,  # ✅ Use UUID as file_id
        "uuid": file_uuid,  # ✅ Also return as uuid for clarity
        "ui_name": file_components["ui_name"],  # ✅ User-friendly name
        "original_filename": file_components["original_filename"],  # ✅ Full original name
        "file_extension": file_components["file_extension"],  # ✅ Extension with dot
        "file_type": file_components["file_extension_clean"],  # ✅ Extension without dot
        "mime_type": file_type,  # ✅ MIME type
        "content_type": content_info["content_type"],  # ✅ Classification
        "size": len(file_data),
        "message": "File uploaded successfully",
        "mode": "gcs_supabase",
        "workflow_id": workflow_id,
        "orchestrator": "ContentAnalysisOrchestrator"
    }
```

#### Step 4: Updated Content Steward File Processing

```python
async def process_upload(
    self, 
    file_data: bytes, 
    content_type: str,  # MIME type
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process uploaded file with proper metadata mapping."""
    
    # Ensure ui_name is set
    if not metadata or "ui_name" not in metadata:
        # Fallback: extract from filename if provided
        filename = metadata.get("filename") if metadata else None
        if filename:
            file_components = parse_filename(filename)
            ui_name = file_components["ui_name"]
        else:
            ui_name = f"file_{uuid.uuid4()}"
    else:
        ui_name = metadata["ui_name"]
    
    # Prepare file record for abstraction layer
    file_record = {
        "user_id": metadata.get("user_id") if metadata else "system",
        "ui_name": ui_name,  # ✅ User-friendly name
        "file_type": metadata.get("file_type") or "unknown",  # ✅ Extension
        "mime_type": content_type,  # ✅ MIME type
        "file_content": file_data,
        "metadata": {
            "original_filename": metadata.get("original_filename"),
            "file_extension": metadata.get("file_extension"),
            "content_type": metadata.get("content_type"),
            "file_type_category": metadata.get("file_type_category"),
            **(metadata.get("metadata", {}) or {})
        },
        "status": "uploaded"
    }
    
    # Create file (generates UUID, stores in GCS + Supabase)
    result = await self.service.file_management_abstraction.create_file(file_record)
    
    # Return with UUID
    return {
        "success": True,
        "uuid": result.get("uuid"),  # ✅ UUID from Supabase
        "file_id": result.get("uuid"),  # ✅ Alias for compatibility
        "ui_name": result.get("ui_name"),
        "file_type": result.get("file_type"),
        "mime_type": result.get("mime_type"),
        "status": result.get("status")
    }
```

## Migration Steps

### Phase 1: Add Utility Functions
1. Create `file_utils.py` with `parse_filename()` and `determine_content_type()`
2. Add to `foundations/public_works_foundation/utilities/`

### Phase 2: Update Content Orchestrator
1. Import utility functions
2. Parse filename in `handle_content_upload()`
3. Map fields correctly to Content Steward
4. Return proper `file_id` (UUID) in response

### Phase 3: Update Content Steward
1. Ensure `ui_name` is always set
2. Map `file_type` correctly (extension, not MIME)
3. Return `uuid` as `file_id` in response

### Phase 4: Update API Responses
1. Ensure all responses use `file_id` = `uuid`
2. Include `ui_name` for display
3. Include `original_filename` for reference
4. Include `file_extension` for parsing logic

### Phase 5: Update Frontend
1. Use `file_id` (UUID) for API calls
2. Use `ui_name` for display
3. Use `file_extension` for file type icons/tiles
4. Use `content_type` for processing decisions

## Benefits

1. **Clear Separation**: UUID for platform, ui_name for users
2. **Proper Parsing**: Extension extracted correctly for processing
3. **Type Classification**: Content type determined for pillar tiles
4. **Consistent Naming**: All layers use same field names
5. **Derivative Support**: Can create derivatives with proper naming (e.g., `{ui_name}_parsed.json`)

## Testing

After implementation, verify:
1. ✅ Upload `userfile.docx` → `file_id` is UUID (not "None")
2. ✅ `ui_name` = "userfile" (for display)
3. ✅ `file_extension` = ".docx" (for parsing)
4. ✅ `content_type` = "unstructured" (for classification)
5. ✅ Derivatives can be created with `{ui_name}_parsed.json`






