# Mainframe/Binary File Parsing Architecture Update Proposal

## Current State

The mainframe processing abstraction (`MainframeProcessingAbstraction`) was built on the old architecture and needs to be updated to work with the new 5-layer architecture.

### Current Issues

1. **Interface Mismatch**: 
   - Old: `parse_cobol_file(binary_path: str, copybook_path: str)` - expects file paths
   - New: `parse_file(request: FileParsingRequest)` - expects bytes and options

2. **Missing File Type Mapping**:
   - `.bin` and `.binary` file types are not mapped in `FileParserService._get_abstraction_name_for_file_type()`

3. **Not Registered in Platform Gateway**:
   - `mainframe_processing` abstraction is not registered in `PlatformGateway.REALM_ABSTRACTION_MAPPINGS`

4. **Copybook Handling**:
   - Copybook comes as a string in `parse_options["copybook"]` but adapter expects a file path

## Proposed Solution

### Phase 1: Update MainframeProcessingAbstraction to Implement FileParsingProtocol

**File**: `symphainy-platform/foundations/public_works_foundation/infrastructure_abstractions/mainframe_processing_abstraction.py`

**Changes**:
1. Add `parse_file()` method that implements `FileParsingProtocol`
2. Handle copybook from `request.options` (can be string or file path)
3. Create temporary files for binary data and copybook (since adapter expects file paths)
4. Convert adapter result to `FileParsingResult` format
5. Keep legacy `parse_cobol_file()` method for backward compatibility

**Implementation Pattern** (following ExcelProcessingAbstraction):
```python
async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
    """
    Parse mainframe binary file using mainframe adapter.
    
    Args:
        request: File parsing request with file_data, filename, and options
        
    Returns:
        FileParsingResult: Parsing result with text, structured data, and metadata
    """
    import tempfile
    import os
    import asyncio
    
    binary_temp_path = None
    copybook_temp_path = None
    
    try:
        # 1. Create temporary file for binary data
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as tmp_binary:
            tmp_binary.write(request.file_data)
            binary_temp_path = tmp_binary.name
        
        # 2. Handle copybook from options
        copybook_data = None
        copybook_path = None
        
        if request.options:
            copybook_data = request.options.get("copybook")  # String
            copybook_path = request.options.get("copybook_path")  # File path
        
        # 3. Create temporary file for copybook if provided as string
        if copybook_data and not copybook_path:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpy', delete=False, encoding='utf-8') as tmp_copybook:
                tmp_copybook.write(copybook_data)
                copybook_temp_path = tmp_copybook.name
                copybook_path = copybook_temp_path
        elif not copybook_path:
            # No copybook provided - return error or try to parse as text
            return FileParsingResult(
                success=False,
                text_content="",
                structured_data=None,
                metadata={},
                error="Copybook required for binary file parsing. Provide 'copybook' (string) or 'copybook_path' (file path) in options.",
                timestamp=datetime.utcnow().isoformat()
            )
        
        # 4. Call adapter with file paths (wrapped in timeout)
        result = await asyncio.wait_for(
            self.mainframe_adapter.parse_cobol_file(binary_temp_path, copybook_path),
            timeout=60.0  # 60 second timeout for mainframe parsing
        )
        
        # 5. Convert adapter result to FileParsingResult
        if not result.get("success"):
            return FileParsingResult(
                success=False,
                text_content="",
                structured_data=None,
                metadata={},
                error=result.get("error", "Unknown error"),
                timestamp=result.get("timestamp", datetime.utcnow().isoformat())
            )
        
        # 6. Convert records to text representation
        records = result.get("records", [])
        text_content = self._records_to_text(records)
        
        # 7. Build structured data
        structured_data = {
            "tables": [{
                "data": records,
                "columns": result.get("columns", []),
                "row_count": len(records)
            }] if records else [],
            "records": records,
            "data": records
        }
        
        # 8. Build metadata
        metadata = {
            "record_count": result.get("record_count", len(records)),
            "column_count": result.get("column_count", 0),
            "columns": result.get("columns", []),
            "abstraction": "mainframe_processing",
            "copybook_provided": True
        }
        
        return FileParsingResult(
            success=True,
            text_content=text_content,
            structured_data=structured_data,
            metadata=metadata,
            error=None,
            timestamp=result.get("timestamp", datetime.utcnow().isoformat())
        )
        
    except asyncio.TimeoutError:
        error_msg = "Mainframe parsing timed out after 60 seconds"
        self.logger.error(f"❌ {error_msg}")
        return FileParsingResult(
            success=False,
            text_content="",
            structured_data=None,
            metadata={},
            error=error_msg,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        self.logger.error(f"❌ Mainframe file parsing failed: {e}")
        return FileParsingResult(
            success=False,
            text_content="",
            structured_data=None,
            metadata={},
            error=str(e),
            timestamp=datetime.utcnow().isoformat()
        )
    finally:
        # Clean up temporary files
        if binary_temp_path and os.path.exists(binary_temp_path):
            try:
                os.unlink(binary_temp_path)
            except Exception:
                pass
        if copybook_temp_path and os.path.exists(copybook_temp_path):
            try:
                os.unlink(copybook_temp_path)
            except Exception:
                pass

def _records_to_text(self, records: List[Dict[str, Any]]) -> str:
    """Convert records to text representation."""
    if not records:
        return ""
    
    # Create a simple text representation
    lines = []
    if records:
        # Header row
        headers = list(records[0].keys())
        lines.append(" | ".join(headers))
        lines.append("-" * (sum(len(str(h)) for h in headers) + len(headers) * 3))
        
        # Data rows
        for record in records:
            values = [str(record.get(key, "")) for key in headers]
            lines.append(" | ".join(values))
    
    return "\n".join(lines)
```

### Phase 2: Add File Type Mapping

**File**: `symphainy-platform/backend/business_enablement/enabling_services/file_parser_service/file_parser_service.py`

**Changes**: Update `_get_abstraction_name_for_file_type()` method:

```python
FILE_TYPE_TO_ABSTRACTION = {
    "xlsx": "excel_processing",
    "xls": "excel_processing",
    "docx": "word_processing",
    "doc": "word_processing",
    "pdf": "pdf_processing",
    "html": "html_processing",
    "htm": "html_processing",
    "png": "image_processing",
    "jpg": "image_processing",
    "jpeg": "image_processing",
    "gif": "image_processing",
    "bmp": "image_processing",
    "tiff": "image_processing",
    "txt": "text_processing",
    "text": "text_processing",
    "csv": "csv_processing",
    "json": "json_processing",
    "bin": "mainframe_processing",      # NEW
    "binary": "mainframe_processing",   # NEW
    "dat": "mainframe_processing",      # NEW (common mainframe extension)
}
```

### Phase 3: Register in Platform Gateway

**File**: `symphainy-platform/platform_infrastructure/infrastructure/platform_gateway.py`

**Changes**: Add `mainframe_processing` to `REALM_ABSTRACTION_MAPPINGS`:

```python
REALM_ABSTRACTION_MAPPINGS = {
    "business_enablement": {
        # ... existing mappings ...
        "mainframe_processing": "mainframe_processing_abstraction",
    },
    # ... other realms ...
}
```

### Phase 4: Ensure MainframeProcessingAbstraction is Created in PublicWorksFoundationService

**File**: `symphainy-platform/foundations/public_works_foundation/public_works_foundation_service.py`

**Verify**: Ensure `mainframe_processing_abstraction` is created and initialized:

```python
# In _create_all_abstractions method
from .infrastructure_abstractions.mainframe_processing_abstraction import MainframeProcessingAbstraction

self.mainframe_processing_abstraction = MainframeProcessingAbstraction(
    mainframe_adapter=self.mainframe_adapter,
    di_container=self.di_container
)
```

## Implementation Steps

1. **Update MainframeProcessingAbstraction**:
   - Add `parse_file()` method implementing `FileParsingProtocol`
   - Add helper method `_records_to_text()`
   - Keep legacy `parse_cobol_file()` for backward compatibility
   - Add proper imports (`tempfile`, `os`, `asyncio`)

2. **Update FileParserService**:
   - Add `.bin`, `.binary`, `.dat` → `mainframe_processing` mapping

3. **Update Platform Gateway**:
   - Register `mainframe_processing` abstraction

4. **Verify PublicWorksFoundationService**:
   - Ensure `mainframe_processing_abstraction` is created

5. **Update Tests**:
   - Test should now pass with the new architecture

## Benefits

1. **Consistency**: Mainframe parsing follows the same pattern as other file types
2. **Swap-ability**: Can swap mainframe adapter without changing service layer
3. **Unified Interface**: All file parsing uses the same `FileParsingProtocol`
4. **Better Error Handling**: Proper timeout protection and error messages
5. **Backward Compatibility**: Legacy `parse_cobol_file()` method still available

## Testing

After implementation, the test `test_parse_binary_with_copybook` should:
- Successfully parse binary files with copybooks
- Return structured data (tables/records)
- Handle errors gracefully
- Clean up temporary files properly

## Notes

- Temporary files are created because the adapter expects file paths
- Copybook can be provided as a string (`copybook`) or file path (`copybook_path`)
- Timeout is set to 60 seconds (mainframe parsing can be slow)
- All temporary files are cleaned up in the `finally` block

