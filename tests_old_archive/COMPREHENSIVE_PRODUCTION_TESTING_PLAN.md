# Comprehensive Production Testing Plan

**Date:** December 3, 2024  
**Status:** 🚧 **IN PROGRESS**

---

## 🎯 Overview

This plan addresses all 4 points raised:
1. ✅ Test file parsing for ALL file types
2. ✅ Fix preview/metadata tests to use PARSED files (not original uploaded files)
3. ✅ Update existing functional tests to use semantic endpoints and real HTTP
4. ✅ Create production tests for other pillars (Insights, Operations, Business Outcomes)

---

## 📋 Point 1: Test All File Types

### Supported File Types (from FileParserService)
- **Structured:** CSV, Excel (xlsx, xls), JSON, XML, YAML, Parquet
- **Unstructured:** PDF, DOCX, DOC, TXT, MD, RTF, HTML
- **Images:** JPG, JPEG, PNG, GIF, BMP, SVG, TIFF
- **Binary:** BIN, DAT (with COBOL copybook)
- **COBOL:** CBL, COB

### Test File Types to Create
```python
FILE_TYPE_TESTS = [
    ("csv", b"name,value\ntest1,100", "text/csv"),
    ("xlsx", <excel_bytes>, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    ("pdf", <pdf_bytes>, "application/pdf"),
    ("docx", <docx_bytes>, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ("txt", b"Plain text content", "text/plain"),
    ("json", b'{"key": "value"}', "application/json"),
    ("png", <image_bytes>, "image/png"),
    ("bin", <binary_bytes>, "application/octet-stream"),  # With copybook
]
```

### Test Structure
```python
@pytest.mark.parametrize("file_type,content,mime_type", FILE_TYPE_TESTS)
async def test_file_parsing_all_types(file_type, content, mime_type, production_client):
    """Test parsing for all supported file types."""
    # 1. Upload file
    # 2. Parse file
    # 3. Verify parsing succeeded
    # 4. Verify parsed data structure
```

---

## 📋 Point 2: Use Parsed Files for Preview/Metadata

### Current Issue
- Tests use original uploaded file (status: `Uploaded`)
- Frontend uses `showOnlyParsed={true}` for MetadataExtractor
- Frontend uses `filterStatus={[FileStatus.Uploaded]}` for ParsePreview (files to parse)

### Fix Required
1. **File Preview Test:**
   - Upload file → Parse file → Get file details (preview)
   - Verify file status is `Parsed` before preview
   - Verify preview shows parsed content

2. **Metadata Extraction Test:**
   - Upload file → Parse file → Extract metadata
   - Verify file status is `Parsed` before metadata extraction
   - Verify metadata includes parsed file information

### Frontend Behavior (Confirmed)
- `FileSelector` has `showOnlyParsed={true}` prop
- Filters for `FileStatus.Parsed` or `metadata.parsed === true`
- `MetadataExtractor` uses `showOnlyParsed={true}`
- `ParsePreview` uses `filterStatus={[FileStatus.Uploaded]}` (files to parse)

### Test Flow
```python
# Correct flow for preview/metadata:
1. Upload file (status: Uploaded)
2. Parse file (status: Parsed)
3. Get file details (preview) - should show parsed content
4. Extract metadata - should use parsed file
```

---

## 📋 Point 3: Update Existing Functional Tests

### File: `test_content_pillar_functional.py`
**Current Issues:**
- Uses old endpoints: `/api/mvp/content/upload`, `/api/mvp/content/parse/{file_id}`
- Uses session tokens (old auth)
- Tests CSV, Binary, Excel, PDF, DOCX parsing

**Updates Needed:**
1. Replace endpoints:
   - `/api/mvp/content/upload` → `/api/v1/content-pillar/upload-file`
   - `/api/mvp/content/parse/{file_id}` → `/api/v1/content-pillar/process-file/{file_id}`
2. Use `production_client` fixture (automatic auth)
3. Keep all file type tests (CSV, Binary, Excel, PDF, DOCX)
4. Add more file types (JSON, TXT, images)
5. Verify parsed data structure and content

---

## 📋 Point 4: Other Pillars - Start Fresh or Reuse?

### Decision: **START FRESH** ✅

**Reasoning:**
1. **Content Pillar Approach:** We created new production tests (`test_content_pillar_capabilities.py`) rather than updating old tests
2. **Legacy Tests Use Mocks:** Most existing tests use mocks, not real HTTP
3. **Semantic Endpoints:** New tests should use semantic endpoints (`/api/v1/{pillar}-pillar/*`)
4. **Production Focus:** Goal is to test actual production functionality, not legacy patterns

### Pillar Capabilities to Test

#### **Insights Pillar**
**Endpoints:**
- `POST /api/v1/insights-pillar/analyze-content-for-insights`
- `GET /api/v1/insights-pillar/get-analysis-results/{analysis_id}`
- `GET /api/v1/insights-pillar/get-visualizations/{analysis_id}`

**Capabilities:**
1. Analyze content for insights (structured data)
2. Analyze content for insights (unstructured data)
3. Get analysis results
4. Get visualizations
5. Query analysis results (NLP)

**Test File:** `test_insights_pillar_capabilities.py`

#### **Operations Pillar**
**Endpoints:**
- `POST /api/v1/operations-pillar/create-standard-operating-procedure`
- `POST /api/v1/operations-pillar/create-workflow`
- `POST /api/v1/operations-pillar/convert-sop-to-workflow`
- `POST /api/v1/operations-pillar/convert-workflow-to-sop`
- `GET /api/v1/operations-pillar/list-standard-operating-procedures`
- `GET /api/v1/operations-pillar/list-workflows`

**Capabilities:**
1. Create SOP from file
2. Create workflow from file
3. Convert SOP to workflow
4. Convert workflow to SOP
5. List SOPs
6. List workflows

**Test File:** `test_operations_pillar_capabilities.py`

#### **Business Outcomes Pillar**
**Endpoints:**
- `POST /api/v1/business-outcomes-pillar/generate-strategic-roadmap`
- `POST /api/v1/business-outcomes-pillar/generate-proof-of-concept-proposal`
- `GET /api/v1/business-outcomes-pillar/get-pillar-summaries`
- `GET /api/v1/business-outcomes-pillar/get-journey-visualization`

**Capabilities:**
1. Generate strategic roadmap
2. Generate POC proposal
3. Get pillar summaries
4. Get journey visualization

**Test File:** `test_business_outcomes_pillar_capabilities.py`

---

## 🚀 Implementation Plan

### Phase 1: Content Pillar (Current)
1. ✅ Create `test_content_pillar_capabilities.py` (DONE)
2. ⏳ Add all file type tests (CSV, Excel, PDF, DOCX, binary, images, JSON, TXT)
3. ⏳ Fix preview/metadata tests to use parsed files
4. ⏳ Update `test_content_pillar_functional.py` to use semantic endpoints

### Phase 2: Insights Pillar
1. ⏳ Create `test_insights_pillar_capabilities.py`
2. ⏳ Test structured data analysis
3. ⏳ Test unstructured data analysis
4. ⏳ Test analysis results retrieval
5. ⏳ Test visualizations

### Phase 3: Operations Pillar
1. ⏳ Create `test_operations_pillar_capabilities.py`
2. ⏳ Test SOP creation
3. ⏳ Test workflow creation
4. ⏳ Test SOP ↔ Workflow conversion
5. ⏳ Test listing capabilities

### Phase 4: Business Outcomes Pillar
1. ⏳ Create `test_business_outcomes_pillar_capabilities.py`
2. ⏳ Test roadmap generation
3. ⏳ Test POC proposal generation
4. ⏳ Test pillar summaries
5. ⏳ Test journey visualization

---

## 📊 Test Coverage Matrix

| Pillar | Capability | Endpoint Exists | Actually Works | Data Correct |
|--------|------------|----------------|----------------|--------------|
| **Content** | File Upload | ✅ | ✅ | ✅ |
| **Content** | File Dashboard | ✅ | ✅ | ✅ |
| **Content** | File Parsing (CSV) | ✅ | ✅ | ⏳ |
| **Content** | File Parsing (All Types) | ✅ | ⏳ | ⏳ |
| **Content** | File Preview (Parsed) | ✅ | ⏳ | ⏳ |
| **Content** | Metadata Extraction (Parsed) | ✅ | ⏳ | ⏳ |
| **Insights** | Analyze Content | ✅ | ⏳ | ⏳ |
| **Insights** | Get Analysis Results | ✅ | ⏳ | ⏳ |
| **Insights** | Get Visualizations | ✅ | ⏳ | ⏳ |
| **Operations** | Create SOP | ✅ | ⏳ | ⏳ |
| **Operations** | Create Workflow | ✅ | ⏳ | ⏳ |
| **Operations** | Convert SOP↔Workflow | ✅ | ⏳ | ⏳ |
| **Business Outcomes** | Generate Roadmap | ✅ | ⏳ | ⏳ |
| **Business Outcomes** | Generate POC | ✅ | ⏳ | ⏳ |

---

## 🎯 Summary

**Approach:**
- ✅ Start fresh for all pillars (like Content Pillar)
- ✅ Use semantic endpoints (`/api/v1/{pillar}-pillar/*`)
- ✅ Use `production_client` fixture (real HTTP, auth, rate limiting)
- ✅ Test actual functionality, not just endpoint existence
- ✅ Follow same pattern as `test_content_pillar_capabilities.py`

**Next Steps:**
1. Fix Content Pillar tests (all file types, parsed files for preview/metadata)
2. Update `test_content_pillar_functional.py` to use semantic endpoints
3. Create Insights Pillar tests
4. Create Operations Pillar tests
5. Create Business Outcomes Pillar tests



