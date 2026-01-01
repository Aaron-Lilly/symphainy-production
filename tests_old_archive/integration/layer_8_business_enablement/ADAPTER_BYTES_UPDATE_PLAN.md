# Adapter Bytes Update Plan

## Goal

**Pass bytes directly to all abstractions/adapters** - no paths, no temp files, no documents.

## Current State Analysis

### ✅ Already Working with Bytes (No Changes Needed)

1. **Excel Adapter** - `parse_file(file_data: bytes, filename: str)`
2. **CSV Adapter** - `parse_file(file_data: bytes, filename: str)`
3. **JSON Adapter** - `parse_file(file_data: bytes, filename: str)`
4. **Text Adapter** - `parse_file(file_data: bytes, filename: str)`
5. **HTML Adapter** - Likely works with bytes (need to verify)

### ⚠️ Need Updates (Currently Use Temp Files)

1. **PDF Abstraction** - Creates temp files, should use `extract_tables_from_bytes()` / `extract_text_from_bytes()`
2. **Word Abstraction** - Likely creates temp files (need to verify)
3. **Image Abstraction** - Likely creates temp files (need to verify)

### 🔴 Needs Complete Update (Mainframe)

1. **Mainframe Adapter** - Currently requires file paths, needs to accept bytes for both binary and copybook

## Update Plan

### Phase 1: Update Abstractions to Use Bytes (Remove Temp Files)

#### 1.1 PDF Abstraction

**Current** (creates temp files):
```python
# Creates temp file
tmp_path = await asyncio.to_thread(_create_temp_file)
result = await self.pdfplumber_adapter.extract_tables_from_file(tmp_path)
```

**Updated** (uses bytes directly):
```python
# Use bytes directly
result = await self.pdfplumber_adapter.extract_tables_from_bytes(request.file_data)
```

**Changes**:
- Remove temp file creation
- Call `extract_tables_from_bytes()` instead of `extract_tables_from_file()`
- Call `extract_text_from_bytes()` instead of `extract_text_from_file()`
- Remove temp file cleanup

#### 1.2 Word Abstraction

**Check**: Does it create temp files? If yes, update to use bytes.

**If python-docx supports BytesIO**:
```python
# Use bytes directly
result = await self.word_adapter.parse_file_from_bytes(request.file_data, request.filename)
```

**If python-docx requires file path**:
- Check if we can use `io.BytesIO` with python-docx
- If not, this is a library limitation (document it)

#### 1.3 Image Abstraction

**Check**: Does it create temp files? If yes, update to use bytes.

**If OpenCV/PIL support BytesIO**:
```python
# Use bytes directly
result = await self.image_adapter.process_image_from_bytes(request.file_data)
```

### Phase 2: Update Mainframe Adapter

#### 2.1 Mainframe Adapter - Accept Bytes

**Current** (requires file paths):
```python
async def parse_cobol_file(self, binary_path: str, copybook_path: str) -> Dict[str, Any]:
    # Reads from file paths
    with open(binary_path, 'rb') as f:
        binary_data = f.read()
    with open(copybook_path, 'r') as f:
        copybook_content = f.read()
```

**Updated** (accepts bytes):
```python
async def parse_file(self, file_data: bytes, filename: str, copybook_data: bytes = None) -> Dict[str, Any]:
    """
    Parse mainframe binary file from bytes using copybook definitions.
    
    Args:
        file_data: Binary file content as bytes
        filename: Original filename (for logging)
        copybook_data: Copybook content as bytes (required for parsing)
        
    Returns:
        Dict[str, Any]: A dictionary containing parsed data, tables, and metadata.
    """
    if not copybook_data:
        return {
            "success": False,
            "error": "Copybook data required",
            ...
        }
    
    # Parse copybook from bytes
    copybook_content = copybook_data.decode('utf-8')
    field_definitions = await self._parse_copybook_from_string(copybook_content)
    
    # Parse binary records
    records = await self._parse_binary_records(file_data, field_definitions)
    
    # Convert to standard format
    text_content = self._records_to_text(records)
    tables = [{
        "data": records,
        "columns": list(records[0].keys()) if records else [],
        "row_count": len(records)
    }] if records else []
    
    return {
        "success": True,
        "text": text_content,
        "tables": tables,
        "records": records,
        "data": records,
        "metadata": {
            "file_type": "mainframe",
            "record_count": len(records),
            "column_count": len(records[0].keys()) if records else 0,
            "columns": list(records[0].keys()) if records else [],
            "filename": filename
        },
        "timestamp": datetime.utcnow().isoformat()
    }
```

#### 2.2 Update `_parse_copybook()` Method

**Current** (reads from file):
```python
async def _parse_copybook(self, copybook_path: str) -> List[Dict[str, Any]]:
    with open(copybook_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # Parse...
```

**Updated** (reads from string):
```python
async def _parse_copybook_from_string(self, copybook_content: str) -> List[Dict[str, Any]]:
    """Parse copybook from string content."""
    import io
    copybook_file = io.StringIO(copybook_content)
    
    for line_num, line in enumerate(copybook_file, 1):
        # Parse... (same logic, just from StringIO instead of file)
```

#### 2.3 Add Helper Method

```python
def _records_to_text(self, records: List[Dict[str, Any]]) -> str:
    """Convert records to text representation."""
    if not records:
        return ""
    
    # Create text representation
    text_lines = []
    for record in records:
        record_str = ", ".join(f"{k}: {v}" for k, v in record.items())
        text_lines.append(record_str)
    
    return "\n".join(text_lines)
```

#### 2.4 Remove Legacy Method

**No backward compatibility needed** - we're breaking and fixing to avoid bad patterns.

**Action:** Remove `parse_cobol_file()` method entirely. All callers should use `parse_file()` with bytes.

### Phase 3: Update Mainframe Abstraction

#### 3.1 Mainframe Abstraction - Extract Copybook from Options

**Current** (doesn't exist or uses file paths):
```python
# Need to create/update
```

**Updated** (extracts copybook from options):
```python
async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
    """Parse mainframe binary file using mainframe adapter."""
    # Get copybook from options
    copybook_data = None
    if request.options:
        copybook = request.options.get("copybook")  # String or bytes
        if copybook:
            if isinstance(copybook, str):
                copybook_data = copybook.encode('utf-8')
            elif isinstance(copybook, bytes):
                copybook_data = copybook
            else:
                return FileParsingResult(
                    success=False,
                    text_content="",
                    structured_data=None,
                    metadata={},
                    error="Copybook must be string or bytes. Provide 'copybook' in options.",
                    timestamp=datetime.utcnow().isoformat()
                )
    
    if not copybook_data:
        return FileParsingResult(
            success=False,
            text_content="",
            structured_data=None,
            metadata={},
            error="Copybook required. Provide 'copybook' (string or bytes) in options.",
            timestamp=datetime.utcnow().isoformat()
        )
    
    # Call adapter (simple!)
    result = await asyncio.wait_for(
        self.mainframe_adapter.parse_file(
            request.file_data,
            request.filename,
            copybook_data
        ),
        timeout=60.0
    )
    
    # Convert to FileParsingResult
    if not result.get("success"):
        return FileParsingResult(
            success=False,
            text_content="",
            structured_data=None,
            metadata={},
            error=result.get("error", "Unknown error"),
            timestamp=result.get("timestamp", datetime.utcnow().isoformat())
        )
    
    return FileParsingResult(
        success=True,
        text_content=result.get("text", ""),
        structured_data={
            "tables": result.get("tables", []),
            "records": result.get("records", []),
            "data": result.get("data", [])
        },
        metadata=result.get("metadata", {}),
        error=None,
        timestamp=result.get("timestamp", datetime.utcnow().isoformat())
    )
```

### Phase 4: Update FileParserService

#### 4.1 Add Mainframe File Type Mapping

```python
def _get_abstraction_name_for_file_type(self, file_type: str) -> Optional[str]:
    """Map file extension to abstraction name."""
    mapping = {
        "xlsx": "excel_processing",
        "xls": "excel_processing",
        "csv": "csv_processing",
        "json": "json_processing",
        "txt": "text_processing",
        "text": "text_processing",
        "pdf": "pdf_processing",
        "docx": "word_processing",
        "doc": "word_processing",
        "html": "html_processing",
        "htm": "html_processing",
        "jpg": "image_processing",
        "jpeg": "image_processing",
        "png": "image_processing",
        "gif": "image_processing",
        "bin": "mainframe_processing",      # NEW
        "binary": "mainframe_processing",   # NEW
        "dat": "mainframe_processing",      # NEW
    }
    return mapping.get(file_type.lower())
```

#### 4.2 Handle Copybook for Mainframe Files

```python
# In parse_file method, when abstraction_name == "mainframe_processing":
if abstraction_name == "mainframe_processing":
    # Check if copybook is provided in parse_options
    if not parse_options or "copybook" not in parse_options:
        # Try to find copybook file in same location
        # Or return error asking for copybook
        return {
            "success": False,
            "error": "Copybook required for mainframe files. Provide 'copybook' in parse_options.",
            ...
        }
```

## Implementation Order

1. **Phase 1**: Update PDF/Word/Image abstractions to use bytes (remove temp files)
2. **Phase 2**: Update Mainframe adapter to accept bytes (remove legacy `parse_cobol_file()` method)
3. **Phase 3**: Update Mainframe abstraction to extract copybook from options
4. **Phase 4**: Update FileParserService to map mainframe file types
5. **Phase 5**: Update any callers of legacy `parse_cobol_file()` to use new `parse_file()` method

## Testing Strategy

1. Test each adapter with bytes directly
2. Test abstractions with FileParsingRequest
3. Test FileParserService end-to-end
4. Test mainframe parsing with binary + copybook bytes

## Benefits

1. **No temp files** - Everything in memory
2. **Consistent pattern** - All adapters work the same way
3. **Better performance** - No disk I/O
4. **Simpler code** - No file cleanup needed
5. **Easier testing** - Just pass bytes, no file setup

