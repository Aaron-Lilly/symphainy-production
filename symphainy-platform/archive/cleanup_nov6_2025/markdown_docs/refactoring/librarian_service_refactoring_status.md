# Librarian Service Refactoring Status

## Current Situation

### Old Version:
- File: `librarian_service.py` (907 lines)
- Uses `RealmServiceBase` + `ILibrarian` interface
- Has all core functionality but needs refactoring

### What We Need to Do:
1. Create new `librarian_service.py` using `SmartCityRoleBase`
2. Remove `ILibrarian` interface inheritance (use `LibrarianProtocol` instead)
3. Preserve all core functionality:
   - `store_knowledge()` - Store knowledge items
   - `search_knowledge()` - Search knowledge base
   - `get_metadata()` - Get metadata
   - `update_metadata()` - Update metadata
   - `get_semantic_relationships()` - Get semantic relationships
4. Add strategic orchestration capabilities
5. Archive old version

### Core Functionality to Preserve:
From lines 243-560 of old service:
- `_store_knowledge()` - Internal storage logic (with validation, ID generation)
- `_search_knowledge()` - Search with semantic capabilities
- `_get_metadata()` - Metadata retrieval with tenant access control
- `_update_metadata()` - Metadata updates with version tracking
- `_get_semantic_relationships()` - Semantic relationship discovery
- `get_knowledge_item()` - Get complete knowledge item
- `delete_knowledge_item()` - Delete knowledge items
- `get_knowledge_statistics()` - Get knowledge base statistics
- `_store_knowledge_item()` - Internal storage with index updates
- Sample knowledge initialization

### New Capabilities to Add:
From `LibrarianProtocol`:
- `orchestrate_knowledge_discovery()` - Strategic knowledge discovery patterns
- `orchestrate_semantic_enrichment()` - Semantic enrichment orchestration
- `orchestrate_metadata_governance()` - Metadata governance policies
- `orchestrate_knowledge_graph()` - Knowledge graph construction
- `orchestrate_search_optimization()` - Search optimization patterns
- `orchestrate_metadata_enrichment_pipeline()` - Batch metadata enrichment
- `orchestrate_knowledge_curation()` - Knowledge curation patterns

## Recommendation

Due to the complexity (900+ lines) and the need to preserve ALL functionality, I recommend:

1. **Rename old file**: `librarian_service.py` → `librarian_service_old.py`
2. **Create new file**: `librarian_service.py` with new structure
3. **Copy and adapt** all core functionality (preserve everything)
4. **Add** strategic orchestration capabilities
5. **Test** to ensure nothing breaks

Given the size and complexity, this is a **substantial refactoring** that should be done carefully to avoid breaking existing functionality.

## Next Steps

**Option 1**: Proceed with full refactoring now (this will be a large change)
**Option 2**: Move on to smaller services first (Nurse, Data Steward, Content Steward)
**Option 3**: Provide a detailed plan for refactoring this service step-by-step

What would you prefer?

