# FileParserService Detailed Rebuilding Plan
## Content Pillar Vertical Slice - Phase 1.1

**Date:** December 11, 2025  
**Status:** 📋 Planning Complete  
**Purpose:** Detailed breakdown of what to reuse, refactor, and rebuild in FileParserService

---

## 🎯 **Executive Summary**

This plan provides a detailed breakdown of the FileParserService rebuild, showing:
1. **What to REUSE** - Working code that can be preserved as-is
2. **What to REFACTOR** - Code that needs improvement for better logic flow
3. **What to REBUILD** - Code that needs to leverage the new DIL SDK pattern

**Key Principle:** Preserve all existing functionality (especially binary + copybook) while improving architecture and integrating DIL SDK.

---

## 📊 **Current State Analysis**

### **Current Architecture (Working)**

```
FileParserService (RealmServiceBase)
├── modules/
│   ├── initialization.py ✅ (Smart City discovery, Curator registration)
│   ├── file_retrieval.py ✅ (Content Steward SOA API)
│   ├── file_parsing.py ✅ (Platform Gateway abstractions)
│   └── utilities.py ✅ (Helper methods)
```

### **Current Flow (Working)**

```
1. FileParserService.parse_file(file_id)
   ↓
2. FileRetrieval.retrieve_document(file_id)
   → Content Steward SOA API ✅
   ↓
3. FileParsing.parse_file()
   → Detect file type ✅
   → Get abstraction name ✅
   → Get abstraction via Platform Gateway ✅
   → Parse via abstraction ✅
   → Return parsed result ✅
```

### **Current Capabilities (Working)**

- ✅ File retrieval via Content Steward SOA API
- ✅ File type detection (extension, content_type, metadata)
- ✅ Abstraction mapping (file_type → abstraction_name)
- ✅ Platform Gateway integration
- ✅ All file type support (Excel, PDF, Word, Binary + Copybook, etc.)
- ✅ Security validation (zero-trust)
- ✅ Tenant validation (multi-tenancy)
- ✅ Telemetry tracking
- ✅ Error handling with audit
- ✅ Health metrics
- ✅ Curator registration

### **Current Gaps (Need Fixing)**

- ❌ **No parsing type determination** - Doesn't distinguish structured/unstructured/hybrid/workflow/sop
- ❌ **No parsed file storage** - Parsed files not stored after parsing
- ❌ **No DIL SDK integration** - Doesn't use DIL SDK for Smart City operations
- ❌ **No workflow_id propagation** - Doesn't propagate workflow_id
- ❌ **Complex decision tree** - File type → abstraction mapping is flat, no parsing type layer

---

## 🔄 **Rebuilding Strategy**

### **1. REUSE (Preserve As-Is)**

**These components are working well and can be reused with minimal changes:**

#### **1.1 Service Base Structure**
- ✅ **FileParserService class** - Extends RealmServiceBase correctly
- ✅ **Module-based architecture** - Good separation of concerns
- ✅ **SOA API methods** - Clean API surface

**Location:** `file_parser_service.py` (lines 1-131)

**Action:** Copy to new location, keep structure

---

#### **1.2 Initialization Module**
- ✅ **Smart City service discovery** - Content Steward, Librarian, Data Steward
- ✅ **Platform Gateway verification** - Tests abstraction availability
- ✅ **Curator registration** - Proper capability registration
- ✅ **Error handling** - Good error handling pattern

**Location:** `modules/initialization.py` (lines 1-192)

**Reuse:** ✅ **100%** - Copy as-is, only add DIL SDK initialization

**Changes Needed:**
- Add DIL SDK initialization (after Smart City services discovered)
- Keep everything else the same

```python
# ADD THIS to initialization.py after Smart City services discovered:
from backend.smart_city.sdk.dil_sdk import DILSDK

# In initialize() method, after discovering Smart City services:
smart_city_services = {
    "content_steward": self.service.content_steward,
    "librarian": self.service.librarian,
    "data_steward": self.service.data_steward,
    "nurse": self.service.nurse  # Add nurse if available
}
self.service.dil_sdk = DILSDK(smart_city_services, logger=self.service.logger)
```

---

#### **1.3 File Retrieval Module**
- ✅ **Content Steward SOA API integration** - Works correctly
- ✅ **Fallback to Platform Gateway** - Good fallback pattern
- ✅ **Error handling** - Structured error responses

**Location:** `modules/file_retrieval.py` (lines 1-90)

**Reuse:** ✅ **100%** - Copy as-is, no changes needed

**Why:** File retrieval is working perfectly, no changes needed.

---

#### **1.4 Utilities Module**
- ✅ **File extension extraction** - `get_file_extension()`
- ✅ **Abstraction name mapping** - `get_abstraction_name_for_file_type()`
- ✅ **Supported formats** - `get_supported_formats()`

**Location:** `modules/utilities.py` (lines 1-115)

**Reuse:** ✅ **90%** - Copy most methods, add parsing type helper

**Changes Needed:**
- Keep all existing methods
- Add `get_parsing_type()` method for parsing type determination

```python
# ADD THIS to utilities.py:
def get_parsing_type(
    self,
    file_type: str,
    parse_options: Optional[Dict[str, Any]] = None
) -> str:
    """
    Determine parsing type: structured, unstructured, hybrid, workflow, sop
    
    Rule-based (from frontend file type selection):
    - structured: xlsx, csv, json, bin (binary with copybook)
    - unstructured: pdf, docx, txt
    - hybrid: excel_with_text
    - workflow: json, bpmn, drawio
    - sop: docx, pdf, txt, md
    """
    # Check parse_options for explicit type
    if parse_options and "parsing_type" in parse_options:
        return parse_options["parsing_type"]
    
    # Rule-based determination
    structured_types = ["xlsx", "xls", "csv", "json", "bin", "binary"]
    unstructured_types = ["pdf", "docx", "doc", "txt", "text"]
    hybrid_types = ["excel_with_text"]
    workflow_types = ["bpmn", "drawio"]
    sop_types = ["md"]
    
    if file_type in structured_types:
        return "structured"
    elif file_type in unstructured_types:
        return "unstructured"
    elif file_type in hybrid_types:
        return "hybrid"
    elif file_type in workflow_types or (file_type == "json" and parse_options and parse_options.get("is_workflow")):
        return "workflow"
    elif file_type in sop_types or (file_type in ["docx", "pdf", "txt"] and parse_options and parse_options.get("is_sop")):
        return "sop"
    else:
        return "unstructured"  # Default
```

---

#### **1.5 Security & Tenant Validation**
- ✅ **Security validation** - Zero-trust pattern
- ✅ **Tenant validation** - Multi-tenant support
- ✅ **Error handling** - Proper error responses

**Location:** `modules/file_parsing.py` (lines 55-77)

**Reuse:** ✅ **100%** - Copy security/tenant validation code as-is

---

#### **1.6 Telemetry & Health Metrics**
- ✅ **Telemetry tracking** - Start/complete pattern
- ✅ **Health metrics** - Success/failure tracking
- ✅ **Error audit** - Error handling with audit

**Location:** Throughout `file_parsing.py`

**Reuse:** ✅ **100%** - Keep all telemetry and health metric code

---

### **2. REFACTOR (Improve Logic Flow)**

**These components work but need refactoring for better architecture:**

#### **2.1 File Parsing Module - Parsing Type Determination**

**Current Issue:** No parsing type determination layer

**Current Flow:**
```
File Type → Abstraction Name → Parse
```

**New Flow (Better):**
```
File Type → Parsing Type → File Type → Abstraction Name → Parse
```

**Location:** `modules/file_parsing.py` (lines 20-343)

**Refactor Strategy:**
1. **Add parsing type determination** - Before file type detection
2. **Create parsing orchestrator module** - Routes to appropriate parsing module
3. **Create parsing modules** - Separate modules for each parsing type

**New Structure:**
```
modules/
├── file_parsing.py (REFACTOR - add parsing type determination)
├── parsing_orchestrator.py (NEW - routes to parsing modules)
├── structured_parsing.py (NEW - handles structured data)
├── unstructured_parsing.py (NEW - handles unstructured data)
├── hybrid_parsing.py (NEW - handles hybrid)
├── workflow_parsing.py (NEW - basic text extraction)
└── sop_parsing.py (NEW - basic text extraction)
```

**Refactored Code:**
```python
# In file_parsing.py - REFACTOR parse_file() method:
async def parse_file(...):
    # 1. Retrieve file (REUSE - no changes)
    document = await self.service.file_retrieval_module.retrieve_document(file_id)
    
    # 2. Detect file type (REUSE - no changes)
    file_type = self.service.utilities_module.get_file_extension(filename)
    
    # 3. Determine parsing type (NEW - add this step)
    parsing_type = self.service.utilities_module.get_parsing_type(
        file_type=file_type,
        parse_options=parse_options
    )
    
    # 4. Route to parsing orchestrator (NEW)
    parsing_orchestrator = self.service.parsing_orchestrator_module
    result = await parsing_orchestrator.parse_by_type(
        parsing_type=parsing_type,
        file_data=file_data,
        file_type=file_type,
        filename=filename,
        parse_options=parse_options
    )
    
    # 5. Store parsed file via DIL SDK (NEW - see REBUILD section)
    # ... (covered in REBUILD section)
    
    return result
```

---

#### **2.2 Parsing Orchestrator Module (NEW)**

**Purpose:** Route to appropriate parsing module based on parsing type

**Location:** `modules/parsing_orchestrator.py` (NEW)

**Implementation:**
```python
class ParsingOrchestrator:
    """Routes parsing requests to appropriate parsing module."""
    
    def __init__(self, service_instance):
        self.service = service_instance
        self.structured_parsing = StructuredParsing(self.service)
        self.unstructured_parsing = UnstructuredParsing(self.service)
        self.hybrid_parsing = HybridParsing(self.service)
        self.workflow_parsing = WorkflowParsing(self.service)
        self.sop_parsing = SOPParsing(self.service)
    
    async def parse_by_type(
        self,
        parsing_type: str,
        file_data: bytes,
        file_type: str,
        filename: str,
        parse_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Route to appropriate parsing module."""
        
        if parsing_type == "structured":
            return await self.structured_parsing.parse(file_data, file_type, filename, parse_options)
        elif parsing_type == "unstructured":
            return await self.unstructured_parsing.parse(file_data, file_type, filename, parse_options)
        elif parsing_type == "hybrid":
            return await self.hybrid_parsing.parse(file_data, file_type, filename, parse_options)
        elif parsing_type == "workflow":
            return await self.workflow_parsing.parse(file_data, file_type, filename, parse_options)
        elif parsing_type == "sop":
            return await self.sop_parsing.parse(file_data, file_type, filename, parse_options)
        else:
            raise ValueError(f"Unknown parsing type: {parsing_type}")
```

---

#### **2.3 Structured Parsing Module (NEW)**

**Purpose:** Handle structured data parsing (Excel, CSV, JSON, Binary + Copybook)

**Location:** `modules/structured_parsing.py` (NEW)

**Implementation Strategy:**
- **REUSE** existing abstraction logic from `file_parsing.py`
- **PRESERVE** binary + copybook support (MainframeProcessingAbstraction)
- **IMPROVE** by separating structured parsing logic

**Key Code (Reuse from file_parsing.py lines 149-316):**
```python
class StructuredParsing:
    """Handles structured data parsing."""
    
    async def parse(
        self,
        file_data: bytes,
        file_type: str,
        filename: str,
        parse_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Parse structured file."""
        
        # 1. Get abstraction name (REUSE from utilities)
        abstraction_name = self.service.utilities_module.get_abstraction_name_for_file_type(file_type)
        
        # 2. Get abstraction via Platform Gateway (REUSE)
        file_parser = self.service.platform_gateway.get_abstraction(
            realm_name=self.service.realm_name,
            abstraction_name=abstraction_name
        )
        
        # 3. Create FileParsingRequest (REUSE)
        from foundations.public_works_foundation.abstraction_contracts.file_parsing_protocol import FileParsingRequest
        request = FileParsingRequest(
            file_data=file_data,
            filename=filename,
            options=parse_options  # Includes copybook for binary files
        )
        
        # 4. Parse via abstraction (REUSE)
        result = await file_parser.parse_file(request)
        
        # 5. Convert to structured format (REUSE)
        return {
            "success": result.success,
            "parsing_type": "structured",
            "file_type": file_type,
            "data": result.structured_data,
            "text_content": result.text_content,
            "metadata": result.metadata,
            "tables": result.structured_data.get("tables", []) if result.structured_data else [],
            "records": result.structured_data.get("records", []) if result.structured_data else []
        }
```

**Binary + Copybook Support (PRESERVE):**
- ✅ Copybook handling via `parse_options` (preserved)
- ✅ MainframeProcessingAbstraction integration (preserved)
- ✅ FileParsingRequest with options (preserved)

---

#### **2.4 Unstructured Parsing Module (NEW)**

**Purpose:** Handle unstructured data parsing (PDF, Word, Text)

**Location:** `modules/unstructured_parsing.py` (NEW)

**Implementation Strategy:**
- **REUSE** existing abstraction logic
- **IMPROVE** by separating unstructured parsing logic

**Key Code (Similar to structured, but for unstructured):**
```python
class UnstructuredParsing:
    """Handles unstructured data parsing."""
    
    async def parse(...) -> Dict[str, Any]:
        """Parse unstructured file."""
        # Similar to structured parsing, but returns chunks instead of tables
        return {
            "success": result.success,
            "parsing_type": "unstructured",
            "file_type": file_type,
            "chunks": result.text_content,  # Chunked text
            "metadata": result.metadata
        }
```

---

#### **2.5 Hybrid Parsing Module (NEW)**

**Purpose:** Handle hybrid parsing (structured + unstructured)

**Location:** `modules/hybrid_parsing.py` (NEW)

**Implementation:**
```python
class HybridParsing:
    """Handles hybrid parsing (structured + unstructured)."""
    
    async def parse(...) -> Dict[str, Any]:
        """Parse hybrid file - returns 3 JSON files."""
        
        # 1. Parse structured portion
        structured_result = await self.structured_parsing.parse(...)
        
        # 2. Parse unstructured portion
        unstructured_result = await self.unstructured_parsing.parse(...)
        
        # 3. Create correlation map
        correlation_map = await self._create_correlation_map(
            structured_result,
            unstructured_result
        )
        
        return {
            "success": True,
            "parsing_type": "hybrid",
            "parsed_files": {
                "structured": {
                    "data": structured_result["data"],
                    "format": "json_structured"
                },
                "unstructured": {
                    "data": unstructured_result["chunks"],
                    "format": "json_chunks"
                },
                "correlation_map": {
                    "data": correlation_map,
                    "format": "json"
                }
            }
        }
```

---

#### **2.6 Workflow & SOP Parsing Modules (NEW)**

**Purpose:** Basic text extraction for workflow and SOP files

**Location:** `modules/workflow_parsing.py`, `modules/sop_parsing.py` (NEW)

**Implementation:**
```python
class WorkflowParsing:
    """Handles workflow file parsing (basic text extraction)."""
    
    async def parse(...) -> Dict[str, Any]:
        """Extract basic text from workflow file."""
        # Basic text extraction only (no metadata/embeddings in MVP)
        return {
            "success": True,
            "parsing_type": "workflow",
            "text_content": extracted_text,
            "metadata": {"workflow_type": "basic"}
        }
```

---

### **3. REBUILD (Leverage DIL SDK Pattern)**

**These components need to be rebuilt to use DIL SDK:**

#### **3.1 Parsed File Storage (REBUILD)**

**Current State:** ❌ Parsed files are NOT stored after parsing

**Location:** `modules/file_parsing.py` (after parsing, before return)

**Rebuild Strategy:**
- **ADD** DIL SDK integration for storing parsed files
- **PRESERVE** all existing parsing logic
- **ADD** workflow_id propagation

**New Code (ADD to file_parsing.py after parsing):**
```python
# After parsing completes successfully (in parse_file method):
if result.success:
    # ... existing result conversion ...
    
    # NEW: Store parsed file via DIL SDK
    if self.service.dil_sdk:
        try:
            # Convert parsed data to bytes (JSON format)
            import json
            parsed_data_bytes = json.dumps(parsed_result["data"]).encode('utf-8')
            
            # Determine format_type and content_type
            format_type = "json_structured" if parsing_type == "structured" else "json_chunks"
            content_type = parsing_type  # "structured", "unstructured", "hybrid"
            
            # Store via DIL SDK
            store_result = await self.service.dil_sdk.store_parsed_file(
                file_id=file_id,
                parsed_file_data=parsed_data_bytes,
                format_type=format_type,
                content_type=content_type,
                parse_result=parsed_result,
                workflow_id=user_context.get("workflow_id") if user_context else None,
                user_context=user_context
            )
            
            # Add parsed_file_id to result
            parsed_result["parsed_file_id"] = store_result.get("parsed_file_id")
            
        except Exception as e:
            self.service.logger.warning(f"⚠️ Failed to store parsed file via DIL SDK: {e}")
            # Don't fail parsing if storage fails - log and continue
    
    return parsed_result
```

---

#### **3.2 DIL SDK Initialization (REBUILD)**

**Current State:** ❌ No DIL SDK initialization

**Location:** `modules/initialization.py` (after Smart City services discovered)

**Rebuild Strategy:**
- **ADD** DIL SDK initialization
- **PRESERVE** all existing initialization logic

**New Code (ADD to initialization.py):**
```python
# After discovering Smart City services (line ~34):
from backend.smart_city.sdk.dil_sdk import DILSDK

# In initialize() method, after line 34:
# Initialize DIL SDK
smart_city_services = {
    "content_steward": self.service.content_steward,
    "librarian": self.service.librarian,
    "data_steward": self.service.data_steward,
    "nurse": self.service.nurse if hasattr(self.service, 'nurse') else None
}
self.service.dil_sdk = DILSDK(smart_city_services, logger=self.service.logger)
self.service.logger.info("✅ DIL SDK initialized for FileParserService")
```

---

#### **3.3 Workflow ID Propagation (REBUILD)**

**Current State:** ❌ No workflow_id propagation

**Location:** Throughout `file_parsing.py`

**Rebuild Strategy:**
- **ADD** workflow_id parameter to parse_file method
- **PROPAGATE** workflow_id to DIL SDK calls

**New Code (UPDATE file_parsing.py method signature):**
```python
async def parse_file(
    self,
    file_id: str,
    parse_options: Optional[Dict[str, Any]] = None,
    user_context: Optional[Dict[str, Any]] = None,
    workflow_id: Optional[str] = None  # NEW parameter
) -> Dict[str, Any]:
    """Parse file into structured format (SOA API)."""
    
    # Propagate workflow_id to user_context if provided
    if workflow_id and user_context:
        user_context["workflow_id"] = workflow_id
    elif workflow_id:
        user_context = {"workflow_id": workflow_id}
    
    # ... rest of parsing logic ...
    
    # When storing via DIL SDK:
    store_result = await self.service.dil_sdk.store_parsed_file(
        ...,
        workflow_id=workflow_id,  # Pass workflow_id
        ...
    )
```

---

## 📋 **Implementation Checklist**

### **Phase 1: Reuse (Copy Working Code)**

- [ ] Copy `file_parser_service.py` base structure
- [ ] Copy `modules/initialization.py` (add DIL SDK init)
- [ ] Copy `modules/file_retrieval.py` (no changes)
- [ ] Copy `modules/utilities.py` (add parsing type method)
- [ ] Copy security/tenant validation code
- [ ] Copy telemetry/health metrics code

### **Phase 2: Refactor (Improve Logic Flow)**

- [ ] Create `modules/parsing_orchestrator.py`
- [ ] Create `modules/structured_parsing.py` (reuse abstraction logic)
- [ ] Create `modules/unstructured_parsing.py` (reuse abstraction logic)
- [ ] Create `modules/hybrid_parsing.py` (new logic)
- [ ] Create `modules/workflow_parsing.py` (basic text extraction)
- [ ] Create `modules/sop_parsing.py` (basic text extraction)
- [ ] Refactor `modules/file_parsing.py` to use parsing orchestrator

### **Phase 3: Rebuild (DIL SDK Integration)**

- [ ] Add DIL SDK initialization to `initialization.py`
- [ ] Add parsed file storage to `file_parsing.py` (after parsing)
- [ ] Add workflow_id parameter to `parse_file()` method
- [ ] Propagate workflow_id to DIL SDK calls
- [ ] Test DIL SDK integration

### **Phase 4: Testing**

- [ ] Test all file types (Excel, PDF, Word, Binary + Copybook, etc.)
- [ ] Test parsing type determination
- [ ] Test parsed file storage via DIL SDK
- [ ] Test workflow_id propagation
- [ ] Test error handling
- [ ] Test security/tenant validation
- [ ] Test telemetry/health metrics

---

## 🎯 **Summary**

### **Reuse (90% of code)**
- ✅ Service base structure
- ✅ Initialization module (with DIL SDK addition)
- ✅ File retrieval module
- ✅ Utilities module (with parsing type addition)
- ✅ Security/tenant validation
- ✅ Telemetry/health metrics
- ✅ Abstraction integration logic
- ✅ Binary + copybook support

### **Refactor (10% of code)**
- 🔄 Add parsing type determination layer
- 🔄 Create parsing orchestrator
- 🔄 Create parsing type modules
- 🔄 Improve decision tree flow

### **Rebuild (New code)**
- 🔨 Add DIL SDK initialization
- 🔨 Add parsed file storage via DIL SDK
- 🔨 Add workflow_id propagation

**Total Effort:**
- **Reuse:** ~90% of existing code
- **Refactor:** ~5% of existing code (improve flow)
- **Rebuild:** ~5% new code (DIL SDK integration)

---

**Last Updated:** December 11, 2025  
**Status:** ✅ Plan Complete  
**Next Action:** Begin Phase 1 (Reuse) implementation



