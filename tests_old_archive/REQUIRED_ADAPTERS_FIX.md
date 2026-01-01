# Required Infrastructure Fix - PyTesseractOCRAdapter and OpenCVImageProcessor

**Date**: November 15, 2025  
**Decision**: These adapters are **REQUIRED**, not optional

---

## Analysis

### Why They Are Required

1. **DocumentIntelligenceAbstraction is Required**
   - `FileParserService` requires `DocumentIntelligenceAbstraction` via Platform Gateway
   - It's not optional - the service will fail if the abstraction is not available
   - See: `FileParserService.initialize()` raises RuntimeError if abstraction is None

2. **Platform Supports Image Files**
   - Platform supports image files (PNG, JPG, JPEG, GIF, BMP, TIFF) as unstructured documents
   - These are part of the platform's core file type support
   - See: Platform Gateway exposes `document_intelligence` to `business_enablement` realm

3. **PyTesseractOCRAdapter is Required for Image OCR**
   - `DocumentIntelligenceAbstraction` uses `pytesseract_adapter` for OCR on image files
   - Without it, images cannot be processed (no text extraction)
   - See: `_build_file_type_mapping()` maps image extensions to `pytesseract_adapter`

4. **OpenCVImageProcessor is Required for Image Enhancement**
   - Used for image enhancement before OCR (improves OCR quality)
   - Part of the image processing pipeline

### Layer 2 Testing Purpose

**Layer 2 validates that everything the platform needs is available/accessible**
- If these adapters are optional, we're not validating that the platform can actually process image files
- For testing purposes, we should ensure all required capabilities are available
- The platform should fail gracefully (clear errors) but still fail if required components are missing

---

## Fix Applied

**Reverted**: Made PyTesseractOCRAdapter and OpenCVImageProcessor **REQUIRED** again
- They will fail gracefully with clear error messages if dependencies are missing
- But they will still fail (not set to None)
- This ensures the platform can actually process image files when initialized

---

## Result

✅ **PyTesseractOCRAdapter and OpenCVImageProcessor are now REQUIRED**
✅ **Platform will fail gracefully but still fail if these dependencies are missing**
✅ **Layer 2 tests will validate that image processing capabilities are available**

---

**Last Updated**: November 15, 2025
