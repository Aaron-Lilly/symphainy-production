# Document Processing Refactoring Plan

**Date**: November 14, 2025  
**Status**: Planning

---

## Goal

Refactor document processing to use abstractions with adapters, enabling future swap-ability to hosted solutions (Kreuzberg, HuggingFace, Cobrix).

---

## Current State

- **FileParserService**: Uses libraries directly (pdfplumber, python-docx, beautifulsoup, etc.)
- **Format-Specific Adapters**: Exist but unused (beautifulsoup_html_adapter, python_docx_adapter, pdfplumber_table_extractor, pytesseract_ocr_adapter, opencv_image_processor, pypdf2_text_extractor, cobol_processing_adapter)
- **DocumentProcessingAdapter**: Exists but focused on NLP (SpaCy, SentenceTransformers)
- **DocumentIntelligenceAbstraction**: Exists but only uses DocumentProcessingAdapter

---

## Target Architecture

### Layer 0: Format-Specific Adapters (Raw Technology)
- `BeautifulSoupHTMLAdapter` - HTML parsing
- `PythonDocxAdapter` - Word document parsing
- `PdfplumberTableExtractor` - PDF table extraction
- `Pypdf2TextExtractor` - PDF text extraction
- `PyTesseractOCRAdapter` - OCR text extraction
- `OpenCVImageProcessor` - Image enhancement
- `CobolProcessingAdapter` - COBOL file processing
- `DocumentProcessingAdapter` - NLP tasks (entity extraction, embeddings, similarity)

### Layer 1: Document Intelligence Abstraction
- Coordinates format-specific adapters based on file type
- Routes parsing to appropriate adapter
- Uses DocumentProcessingAdapter for NLP tasks
- Provides unified interface for document processing

### Layer 2: Business Enablement Services
- `FileParserService` uses `DocumentIntelligenceAbstraction` (via Platform Gateway)
- No direct library access

---

## Implementation Steps

### Step 1: Refactor DocumentIntelligenceAbstraction
- Accept multiple format-specific adapters via dependency injection
- Route parsing to appropriate adapter based on file type
- Keep DocumentProcessingAdapter for NLP tasks

### Step 2: Update Public Works Foundation
- Create all format-specific adapters in `_create_all_adapters()`
- Create DocumentIntelligenceAbstraction with injected adapters
- Register with appropriate registry

### Step 3: Expose via Platform Gateway
- Add DocumentIntelligenceAbstraction to Platform Gateway
- Make available to Business Enablement realm

### Step 4: Refactor FileParserService
- Replace direct library calls with DocumentIntelligenceAbstraction calls
- Use Platform Gateway to access DocumentIntelligenceAbstraction

---

## Benefits

1. **Swap-ability**: Can swap local libraries for hosted solutions (Kreuzberg, HuggingFace, etc.)
2. **Consistency**: Matches architectural pattern (adapters → abstractions → services)
3. **Testability**: Easier to mock/test document processing
4. **Future-ready**: Prepared for hosted solutions

---

**Status**: Ready for implementation




