# Public Works Layers Update Analysis

## Summary

After implementing the bytes-based file parsing pattern, we need to update a few additional layers to maintain consistency.

## ✅ Already Correct (No Updates Needed)

### 1. FileParsingProtocol ✅
- Already uses bytes: `FileParsingRequest(file_data: bytes, ...)`
- All new abstractions implement this protocol
- **Status**: No changes needed

### 2. Composition Services ✅
- `FileManagementCompositionService` - Works with file storage, not parsing
- `DocumentIntelligenceCompositionService` - Uses archived `DocumentIntelligenceAbstraction` (separate concern)
- Other composition services don't use file parsing
- **Status**: No changes needed

### 3. Registries ✅
- File parsing abstractions are accessed via Platform Gateway, not registries
- Registries handle discovery/health, not direct access
- **Status**: No changes needed

## ⚠️ Needs Updates

### 1. CobolProcessingProtocol (ARCHIVE)

**Current State:**
- Still defines `parse_cobol_file(binary_path: str, copybook_path: str)` with file paths
- Mainframe adapter no longer uses this protocol (uses `parse_file()` with bytes instead)

**Action Required:**
- Archive the protocol (comment with ARCHIVED note)
- Document that mainframe processing now uses `FileParsingProtocol` instead

**Reason:**
- Mainframe adapter now implements bytes-based `parse_file()` method
- The old protocol is no longer used
- Keep for reference but mark as archived

### 2. Platform Gateway (ADD mainframe_processing)

**Current State:**
- Lists new file parsing abstractions: `excel_processing`, `csv_processing`, `pdf_processing`, etc.
- **Missing**: `mainframe_processing`

**Action Required:**
- Add `"mainframe_processing"` to `business_enablement` realm abstractions list

**Reason:**
- FileParserService needs access to mainframe_processing abstraction
- Currently missing from Platform Gateway mappings

### 3. TextExtractionAbstraction & TableExtractionAbstraction (OPTIONAL)

**Current State:**
- Still have methods that use file paths
- Also have bytes support (`extract_text_from_bytes`, `extract_tables_from_bytes`)
- These are separate from the new file parsing abstractions

**Action Required:**
- **Optional**: These might be legacy or for different use cases
- If they're still used, consider updating to prefer bytes methods
- If they're legacy, consider archiving them

**Note:** These seem to be different abstractions (text/table extraction from documents) vs. the new file parsing abstractions (parse entire files). They might serve different purposes.

## Implementation Plan

### Priority 1: Platform Gateway (Required)
- Add `"mainframe_processing"` to business_enablement abstractions

### Priority 2: Archive CobolProcessingProtocol (Cleanup)
- Comment out with ARCHIVED note
- Document that mainframe now uses FileParsingProtocol

### Priority 3: Review Text/Table Extraction Abstractions (Optional)
- Determine if they're still needed
- If yes, update to prefer bytes methods
- If no, archive them

## Files to Update

1. `platform_infrastructure/infrastructure/platform_gateway.py`
   - Add `"mainframe_processing"` to business_enablement abstractions

2. `foundations/public_works_foundation/abstraction_contracts/cobol_processing_protocol.py`
   - Archive with ARCHIVED comment
   - Add note about using FileParsingProtocol instead

3. (Optional) `foundations/public_works_foundation/infrastructure_abstractions/text_extraction_abstraction.py`
   - Review and potentially update

4. (Optional) `foundations/public_works_foundation/infrastructure_abstractions/table_extraction_abstraction.py`
   - Review and potentially update

