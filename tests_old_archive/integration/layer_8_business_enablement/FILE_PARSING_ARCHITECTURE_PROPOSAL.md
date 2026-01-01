# File Parsing Architecture Proposal

## Current State Analysis

### Current Flow (Backwards from FileParserService)

```
FileParserService.parse_file(file_id)
  ↓
DocumentIntelligenceAbstraction.process_document(request)
  ↓
  ├─→ Routes to format-specific adapters (beautifulsoup, python_docx, pdfplumber, etc.)
  ├─→ Calls extract_entities() ← NLP (inappropriate)
  ├─→ Calls chunk_text() ← Infrastructure (appropriate)
  └─→ Returns DocumentProcessingResult with chunks + entities
```

### Problems with Current Architecture

1. **DocumentIntelligenceAbstraction is doing too much**:
   - File parsing (infrastructure) ✅
   - NLP entity extraction (agentic) ❌
   - Text chunking (infrastructure) ✅
   - Document similarity (analytics) ❌
   - Embeddings (analytics) ❌

2. **Missing Excel Adapter**:
   - Excel files (.xlsx, .xls) are NOT in `_file_type_mapping`
   - FileParserService has its own `_parse_excel()` method
   - This duplicates logic and prevents swap-ability

3. **Duplication**:
   - FileParserService has `_parse_by_type()` with format-specific parsers
   - DocumentIntelligenceAbstraction routes to adapters
   - Same logic in two places

4. **No Swap-Ability**:
   - Can't swap to Kreuzberg, Cobrix, HuggingFace without major refactoring
   - Adapters are embedded in DocumentIntelligenceAbstraction
   - No clear abstraction layer per file type

## Proposed Architecture

### 5-Layer Pattern for File Parsing

```
Layer 1: Adapters (Raw Technology)
├── excel_processing_adapter.py (pandas/openpyxl)
├── word_processing_adapter.py (python-docx) ✅ exists
├── pdf_processing_adapter.py (pdfplumber/pypdf2) ✅ exists
├── html_processing_adapter.py (beautifulsoup) ✅ exists
├── image_processing_adapter.py (pytesseract/opencv) ✅ exists
├── mainframe_processing_adapter.py (COBOL) ✅ exists (rename from cobol)
├── text_processing_adapter.py (plain text)
├── csv_processing_adapter.py (pandas)
└── json_processing_adapter.py (json)

Layer 2: Abstractions (Swap-Ability)
├── excel_processing_abstraction.py
├── word_processing_abstraction.py
├── pdf_processing_abstraction.py
├── html_processing_abstraction.py
├── image_processing_abstraction.py
├── mainframe_processing_abstraction.py
├── text_processing_abstraction.py
├── csv_processing_abstraction.py
└── json_processing_abstraction.py

Layer 3: Composition Services (Optional - for complex workflows)
└── file_parsing_composition_service.py (if needed)

Layer 4: Registries (Exposure/Discovery)
└── file_parsing_registry.py (exposes all file parsing abstractions)

Layer 5: Platform Gateway (Realm Access)
└── platform_gateway.get_abstraction("excel_processing")
```

## Proposed File Structure

### Adapters (Layer 1) - One Per File Type

```
infrastructure_adapters/
├── excel_processing_adapter.py (NEW - extract from FileParserService._parse_excel)
├── word_processing_adapter.py (RENAME from python_docx_adapter.py)
├── pdf_processing_adapter.py (CONSOLIDATE pdfplumber + pypdf2)
├── html_processing_adapter.py (RENAME from beautifulsoup_html_adapter.py)
├── image_processing_adapter.py (CONSOLIDATE pytesseract + opencv)
├── mainframe_processing_adapter.py (RENAME from cobol_processing_adapter.py)
├── text_processing_adapter.py (NEW - simple text parsing)
├── csv_processing_adapter.py (NEW - extract from FileParserService._parse_csv)
└── json_processing_adapter.py (NEW - extract from FileParserService._parse_json)
```

### Abstractions (Layer 2) - One Per File Type

```
infrastructure_abstractions/
├── excel_processing_abstraction.py (NEW)
├── word_processing_abstraction.py (NEW)
├── pdf_processing_abstraction.py (NEW)
├── html_processing_abstraction.py (NEW)
├── image_processing_abstraction.py (NEW)
├── mainframe_processing_abstraction.py (EXISTS - cobol_processing_abstraction.py)
├── text_processing_abstraction.py (NEW)
├── csv_processing_abstraction.py (NEW)
└── json_processing_abstraction.py (NEW)
```

### Abstraction Contracts (Protocols)

```
abstraction_contracts/
└── file_parsing_protocol.py (NEW - common interface for all file parsers)
```

## Abstraction Protocol Design

### Common Interface for All File Parsers

```python
from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class FileParsingRequest:
    """Request for file parsing."""
    file_data: bytes
    filename: str
    options: Optional[Dict[str, Any]] = None

@dataclass
class FileParsingResult:
    """Result from file parsing."""
    success: bool
    text_content: str
    structured_data: Optional[Any] = None  # Tables, records, etc.
    metadata: Dict[str, Any] = None
    error: Optional[str] = None

class FileParsingProtocol(Protocol):
    """Protocol for file parsing abstractions."""
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """Parse file and return structured result."""
        ...
    
    async def extract_text(self, file_data: bytes, filename: str) -> str:
        """Extract plain text from file."""
        ...
    
    async def extract_metadata(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Extract metadata from file."""
        ...
```

## Proposed Flow (New Architecture)

### FileParserService.parse_file()

```python
async def parse_file(self, file_id: str, parse_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    # 1. Retrieve file
    document = await self.retrieve_document(file_id)
    file_data = document.get("file_content")
    filename = document.get("ui_name") or file_id
    
    # 2. Detect file type
    file_type = self._get_file_extension(filename) or self._infer_from_content_type(document)
    
    # 3. Get appropriate abstraction via Platform Gateway
    abstraction_name = self._get_abstraction_name_for_file_type(file_type)
    # e.g., "excel_processing", "pdf_processing", "word_processing"
    
    file_parser = self.platform_gateway.get_abstraction(
        realm_name=self.realm_name,
        abstraction_name=abstraction_name
    )
    
    if not file_parser:
        # Fallback to direct parsing (for unsupported types)
        return await self._parse_by_type(file_data, file_type, parse_options)
    
    # 4. Parse via abstraction
    request = FileParsingRequest(
        file_data=file_data,
        filename=filename,
        options=parse_options
    )
    
    result = await file_parser.parse_file(request)
    
    # 5. Return standardized format
    return {
        "success": result.success,
        "file_id": file_id,
        "file_type": file_type,
        "content": result.text_content,
        "structure": result.structured_data,
        "metadata": result.metadata
    }
```

## Implementation Plan

### Phase 1: Create Missing Adapters

1. **Create `excel_processing_adapter.py`**
   - Extract logic from `FileParserService._parse_excel()`
   - Use pandas/openpyxl
   - Return structured data (tables, sheets)

2. **Create `csv_processing_adapter.py`**
   - Extract logic from `FileParserService._parse_csv()`
   - Use pandas/csv module

3. **Create `json_processing_adapter.py`**
   - Extract logic from `FileParserService._parse_json()`
   - Use json module

4. **Create `text_processing_adapter.py`**
   - Simple text parsing (decode bytes to string)
   - Handle encoding detection

5. **Rename `cobol_processing_adapter.py` → `mainframe_processing_adapter.py`**

### Phase 2: Create Abstractions (One Per File Type)

1. **Create `excel_processing_abstraction.py`**
   ```python
   class ExcelProcessingAbstraction(FileParsingProtocol):
       def __init__(self, excel_adapter, di_container=None):
           self.excel_adapter = excel_adapter
       
       async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
           # Wrap adapter call with timeout protection
           # Handle errors gracefully
           # Return standardized result
   ```

2. **Create similar abstractions for each file type**

3. **Create `file_parsing_protocol.py`** with common interface

### Phase 3: Update PublicWorksFoundationService

1. **Create all adapters** (already done for most)
2. **Create all abstractions** (new)
3. **Register abstractions with Platform Gateway**
   ```python
   # In _create_all_abstractions()
   self.excel_processing_abstraction = ExcelProcessingAbstraction(
       excel_adapter=self.excel_adapter,
       di_container=self.di_container
   )
   
   # Register with Platform Gateway
   self.platform_gateway.register_abstraction(
       realm_name="business_enablement",
       abstraction_name="excel_processing",
       abstraction=self.excel_processing_abstraction
   )
   ```

### Phase 4: Update FileParserService

1. **Remove `_parse_by_type()` and format-specific parsers**
2. **Update `parse_file()` to use abstractions via Platform Gateway**
3. **Remove dependency on DocumentIntelligenceAbstraction for parsing**
4. **Keep DocumentIntelligenceAbstraction only for text chunking (if needed)**

### Phase 5: Clean Up DocumentIntelligenceAbstraction

1. **Remove file parsing logic** (moved to individual abstractions)
2. **Remove NLP entity extraction** (move to agentic service)
3. **Remove document similarity** (move to analytics service)
4. **Remove embeddings** (move to analytics service)
5. **Keep only text chunking** (if still needed, or move to separate abstraction)

## Swap-Ability Example

### Current (Hard to Swap)
```python
# Adapter is embedded in abstraction
DocumentIntelligenceAbstraction(
    excel_adapter=ExcelAdapter()  # Can't swap easily
)
```

### Proposed (Easy to Swap)
```python
# Adapter can be swapped at initialization
ExcelProcessingAbstraction(
    excel_adapter=KreuzbergExcelAdapter()  # Swap to Kreuzberg
    # OR
    excel_adapter=HuggingFaceExcelAdapter()  # Swap to HuggingFace
    # OR
    excel_adapter=PandasExcelAdapter()  # Current implementation
)
```

## File Type to Abstraction Mapping

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
    "cbl": "mainframe_processing",
    "cob": "mainframe_processing",
    "bin": "mainframe_processing",
    "txt": "text_processing",
    "csv": "csv_processing",
    "json": "json_processing"
}
```

## Benefits

1. **Clear Separation**: Each file type has its own adapter + abstraction
2. **Swap-Ability**: Easy to swap adapters (Kreuzberg, Cobrix, HuggingFace)
3. **No Duplication**: Single source of truth per file type
4. **Clean Architecture**: Follows 5-layer pattern consistently
5. **Testability**: Each abstraction can be tested independently
6. **Maintainability**: Changes to one file type don't affect others

## Migration Path

1. **Create new adapters** (don't break existing code)
2. **Create new abstractions** (don't break existing code)
3. **Register with Platform Gateway** (additive)
4. **Update FileParserService** to use new abstractions
5. **Remove old code** from DocumentIntelligenceAbstraction
6. **Remove duplicate code** from FileParserService

## Complete Flow Example

### Current Flow (Problematic)
```
FileParserService.parse_file(file_id)
  ↓
DocumentIntelligenceAbstraction.process_document(request)
  ↓
  ├─→ Routes to adapters (beautifulsoup, python_docx, pdfplumber)
  ├─→ Calls extract_entities() ← NLP (WRONG LAYER)
  └─→ Returns DocumentProcessingResult
```

### Proposed Flow (Clean)
```
FileParserService.parse_file(file_id)
  ↓
1. Detect file type (xlsx, pdf, docx, etc.)
  ↓
2. Map file type to abstraction name
   "xlsx" → "excel_processing"
   "pdf" → "pdf_processing"
   "docx" → "word_processing"
  ↓
3. Get abstraction via Platform Gateway
   platform_gateway.get_abstraction(
       realm_name="business_enablement",
       abstraction_name="excel_processing"
   )
  ↓
4. Platform Gateway validates realm access
   (checks REALM_ABSTRACTION_MAPPINGS)
  ↓
5. Platform Gateway calls PublicWorksFoundationService.get_abstraction("excel_processing")
  ↓
6. PublicWorksFoundationService returns ExcelProcessingAbstraction
  ↓
7. ExcelProcessingAbstraction.parse_file(request)
  ↓
8. ExcelProcessingAbstraction wraps ExcelProcessingAdapter
   (with timeout protection, error handling)
  ↓
9. ExcelProcessingAdapter uses pandas/openpyxl
  ↓
10. Return standardized FileParsingResult
```

## Platform Gateway Registration

### Step 1: Add Abstractions to REALM_ABSTRACTION_MAPPINGS

```python
# In platform_gateway.py
REALM_ABSTRACTION_MAPPINGS = {
    "business_enablement": {
        "abstractions": [
            # ... existing abstractions ...
            "excel_processing",      # NEW
            "word_processing",        # NEW
            "pdf_processing",        # NEW
            "html_processing",        # NEW
            "image_processing",      # NEW
            "mainframe_processing",  # NEW (renamed from cobol)
            "text_processing",       # NEW
            "csv_processing",        # NEW
            "json_processing"        # NEW
        ]
    }
}
```

### Step 2: Add to PublicWorksFoundationService.get_abstraction()

```python
# In public_works_foundation_service.py
def get_abstraction(self, name: str) -> Any:
    abstraction_map = {
        # ... existing mappings ...
        "excel_processing": self.excel_processing_abstraction,
        "word_processing": self.word_processing_abstraction,
        "pdf_processing": self.pdf_processing_abstraction,
        "html_processing": self.html_processing_abstraction,
        "image_processing": self.image_processing_abstraction,
        "mainframe_processing": self.mainframe_processing_abstraction,
        "text_processing": self.text_processing_abstraction,
        "csv_processing": self.csv_processing_abstraction,
        "json_processing": self.json_processing_abstraction
    }
    return abstraction_map.get(name)
```

## Swap-Ability Example: Excel Processing

### Current Implementation (Pandas)
```python
# excel_processing_adapter.py
class ExcelProcessingAdapter:
    async def parse_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        import pandas as pd
        excel_file = io.BytesIO(file_data)
        excel_data = pd.read_excel(excel_file, sheet_name=None)
        # ... return structured data
```

### Swap to Kreuzberg (Future)
```python
# excel_processing_adapter.py (swapped implementation)
class ExcelProcessingAdapter:
    def __init__(self):
        from kreuzberg import KreuzbergExcelParser
        self.parser = KreuzbergExcelParser(api_key=os.getenv("KREUZBERG_API_KEY"))
    
    async def parse_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        result = await self.parser.parse(file_data)
        # ... return structured data
```

### Swap to HuggingFace (Future)
```python
# excel_processing_adapter.py (swapped implementation)
class ExcelProcessingAdapter:
    def __init__(self):
        from transformers import AutoModelForTableQuestionAnswering
        self.model = AutoModelForTableQuestionAnswering.from_pretrained("google/tapas-base")
    
    async def parse_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        # Use HuggingFace model for parsing
        # ... return structured data
```

**No changes needed to:**
- `ExcelProcessingAbstraction` (still wraps adapter)
- `FileParserService` (still calls abstraction via Platform Gateway)
- Platform Gateway (still routes to abstraction)

## Questions to Resolve

1. **Text Chunking**: Should this be a separate abstraction or part of each file parser?
   - Recommendation: Separate `text_chunking_abstraction.py` (it's a post-processing step)

2. **DocumentIntelligenceAbstraction**: What should it become?
   - Option A: Delete it entirely (parsing moved to individual abstractions)
   - Option B: Keep only for text chunking (rename to `TextChunkingAbstraction`)
   - Recommendation: Option B, then eventually Option A

3. **Excel Adapter**: Should it handle both .xlsx and .xls?
   - Recommendation: Yes, one adapter for both (pandas handles both)

4. **Error Handling**: How should unsupported file types be handled?
   - Recommendation: Return error result, don't crash

5. **File Type Detection**: Where should it live?
   - Option A: In FileParserService (current)
   - Option B: In a separate `file_type_detection_abstraction.py`
   - Recommendation: Option A (it's a simple utility function)

