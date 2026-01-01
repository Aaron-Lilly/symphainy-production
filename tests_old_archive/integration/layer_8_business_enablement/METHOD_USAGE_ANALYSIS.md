# Method Usage Analysis: extract_entities, calculate_document_similarity, generate_document_embeddings

## Summary

**All three methods appear to be historical artifacts with minimal/no active usage.**

## 1. extract_entities() in process_document()

### Location
- `DocumentIntelligenceAbstraction.process_document()` line 423
- Called automatically during file parsing

### Active Usage
✅ **ACTIVELY USED** (but unnecessarily)
- Called automatically in `process_document()` for every file parse
- Entities are included in `DocumentProcessingResult`
- `FileParserService` passes entities through in response (lines 600-607)
- **BUT**: FileParserService doesn't actually USE entities - just includes them

### Indirect Usage
- `DataAnalyzerService.extract_entities()` - but this delegates to Content Steward's `enrich_content_metadata()` with `enrichment_type="extract_entities"`, NOT directly to the abstraction
- `ContentAnalysisOrchestrator.extract_entities()` - delegates to `DataAnalyzerService.extract_entities()`, NOT directly to the abstraction

### Conclusion
- **Can be removed from `process_document()`** - entities are generated but not actively used
- FileParserService doesn't need entities for file parsing
- If entities are needed, they should be extracted separately via an agentic service

---

## 2. calculate_document_similarity()

### Location
- `DocumentIntelligenceAbstraction.calculate_document_similarity()` line 479
- `DocumentIntelligenceCompositionService.compare_documents_for_agent()` line 262

### Active Usage
❌ **NOT ACTIVELY USED**

**Only called in:**
- `DocumentIntelligenceCompositionService.compare_documents_for_agent()` (line 262)

**But:**
- `DocumentIntelligenceCompositionService` is **NOT instantiated** in `PublicWorksFoundationService`
- No `get_document_intelligence_composition_service()` method exists
- No references to `document_intelligence_composition_service` in the codebase
- The composition service file exists but appears to be **dead code**

### Conclusion
- **Historical artifact - can be removed**
- Composition service that wraps it is not used
- No active callers found

---

## 3. generate_document_embeddings()

### Location
- `DocumentIntelligenceAbstraction.generate_document_embeddings()` line 509
- `DocumentIntelligenceCompositionService.generate_document_embeddings_for_agent()` line 327

### Active Usage
❌ **NOT ACTIVELY USED**

**Only called in:**
- `DocumentIntelligenceCompositionService.generate_document_embeddings_for_agent()` (line 327)

**But:**
- `DocumentIntelligenceCompositionService` is **NOT instantiated** in `PublicWorksFoundationService`
- No `get_document_intelligence_composition_service()` method exists
- No references to `document_intelligence_composition_service` in the codebase
- The composition service file exists but appears to be **dead code**

### Conclusion
- **Historical artifact - can be removed**
- Composition service that wraps it is not used
- No active callers found

---

## 4. extract_document_entities() (separate method)

### Location
- `DocumentIntelligenceAbstraction.extract_document_entities()` line 530
- Called by `DocumentIntelligenceCompositionService.extract_entities_for_agent()` line 391

### Active Usage
❌ **NOT ACTIVELY USED**

**Only called in:**
- `DocumentIntelligenceCompositionService.extract_entities_for_agent()` (line 391)

**But:**
- `DocumentIntelligenceCompositionService` is **NOT instantiated**
- This is a separate method from the one called in `process_document()`
- Appears to be **dead code**

### Conclusion
- **Historical artifact - can be removed**
- Not actively used

---

## DocumentIntelligenceCompositionService Status

### File Exists
- `/foundations/public_works_foundation/composition_services/document_intelligence_composition_service.py`

### But:
- ❌ **NOT instantiated** in `PublicWorksFoundationService._create_all_composition_services()`
- ❌ **NO** `get_document_intelligence_composition_service()` method
- ❌ **NO** references to it anywhere in the codebase
- ❌ **NO** imports of it (except in its own file)

### Methods in Composition Service:
1. `process_agent_document()` - wraps `process_document()`
2. `compare_documents_for_agent()` - wraps `calculate_document_similarity()` ❌
3. `generate_document_embeddings_for_agent()` - wraps `generate_document_embeddings()` ❌
4. `extract_entities_for_agent()` - wraps `extract_document_entities()` ❌

**All appear to be dead code.**

---

## Recommendations

### Safe to Remove Immediately

1. ✅ **`calculate_document_similarity()`** - No active usage
2. ✅ **`generate_document_embeddings()`** - No active usage
3. ✅ **`extract_document_entities()`** (separate method) - No active usage
4. ✅ **`DocumentIntelligenceCompositionService`** - Entire file is dead code

### Requires Careful Removal

1. ⚠️ **`extract_entities()` in `process_document()`** - Currently called automatically
   - **Action**: Remove from `process_document()` but keep the adapter method
   - **Impact**: FileParserService will no longer receive entities (but it doesn't use them anyway)
   - **Migration**: If entities are needed, create a separate `EntityExtractionService`

### What to Keep

1. ✅ **`DocumentProcessingAdapter.extract_entities()`** - Keep the adapter method
   - Can be used by future agentic services
   - Just remove the automatic call in `process_document()`

2. ✅ **`DocumentProcessingAdapter.generate_embeddings()`** - Keep the adapter method
   - Can be used by future analytics services
   - Just remove the abstraction wrapper

3. ✅ **`DocumentProcessingAdapter.calculate_similarity()`** - Keep the adapter method
   - Can be used by future analytics services
   - Just remove the abstraction wrapper

---

## Removal Plan

### Phase 1: Remove Dead Code (Zero Risk)
1. Delete `DocumentIntelligenceCompositionService` file
2. Remove `calculate_document_similarity()` from `DocumentIntelligenceAbstraction`
3. Remove `generate_document_embeddings()` from `DocumentIntelligenceAbstraction`
4. Remove `extract_document_entities()` from `DocumentIntelligenceAbstraction`
5. Remove these methods from `DocumentIntelligenceProtocol`

### Phase 2: Remove Automatic Entity Extraction (Low Risk)
1. Remove `extract_entities()` call from `process_document()` (line 423)
2. Remove entities from `DocumentProcessingResult` in `process_document()`
3. Update `FileParserService` to not include entities in response
4. Update `DocumentProcessingResult` dataclass to make entities optional (already is)

### Phase 3: Clean Up Protocol (Low Risk)
1. Remove unused methods from `DocumentIntelligenceProtocol`
2. Keep adapter methods in `DocumentProcessingAdapter` for future use

---

## Impact Assessment

### Breaking Changes
- **None** for `calculate_document_similarity()` - not used
- **None** for `generate_document_embeddings()` - not used
- **None** for `extract_document_entities()` - not used
- **Minor** for removing entities from `process_document()`:
  - FileParserService will no longer include entities in response
  - But FileParserService doesn't use entities anyway
  - If entities are needed, they should be extracted via a separate service

### Benefits
- Cleaner architecture
- Removes dead code
- Removes inappropriate NLP from infrastructure
- Makes it clear that file parsing != entity extraction

