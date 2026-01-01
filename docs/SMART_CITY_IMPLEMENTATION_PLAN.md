# Smart City Implementation Plan: Bringing the Vision to Life

**Date:** January 2025  
**Status:** 📋 **COMPREHENSIVE IMPLEMENTATION PLAN**  
**Purpose:** Detailed, phase-by-phase plan to implement the "Smart City as Data Plane" vision

---

## Executive Summary

This plan implements the vision where **Smart City IS the Data Intelligence Layer**, with:
- ✅ **Content Metadata** and **Embeddings** separated into distinct abstractions/services
- ✅ **Content Metadata Generated FROM Parsed Files** (simplified approach - no double parsing)
- ✅ **Nurse** enhanced with comprehensive observability (including agentic tracking)
- ✅ **Data Steward, Content Steward, Librarian** properly aligned
- ✅ **DIL SDK** as a client library wrapping Smart City SOA APIs
- ✅ All other necessary updates

**Timeline:** 8-10 weeks  
**Approach:** Phase-by-phase, service-by-service, with testing at each phase

### ⚠️ **IMPORTANT: Business Enablement Service Creation DEFERRED**

**Decision:** Defer creating new Business Enablement services (ContentMetadataExtractionService, EmbeddingService) until Business Enablement realm refactoring.

**Why:**
- ✅ **Avoid technical debt** - New services should follow new Smart City patterns
- ✅ **Holistic approach** - Better to refactor all Business Enablement services together
- ✅ **Use existing services** - StatelessHFInferenceAgent already exists for embeddings
- ✅ **Focus on foundation** - Smart City infrastructure (abstractions, storage) is the foundation

**Temporary Approach (Until Business Enablement Refactoring):**
- ✅ Use existing `StatelessHFInferenceAgent` for embeddings (already exists)
- ✅ Use existing `FileParserService` for parsing (already exists)
- ⚠️ Extract metadata inline in orchestrators (temporary - mark with TODO)
- ✅ Call Librarian SOA APIs to store results

**Phase 1 Focus:** Smart City infrastructure only (abstractions, Librarian storage APIs)

### Architectural Pattern: Business Enablement Does Work, Smart City Stores & Governs

**Consistent Pattern Throughout:**
```
┌─────────────────────────────────────────────────────────────┐
│ BUSINESS ENABLEMENT (DOES the work)                          │
│ - FileParserService → Parses files                          │
│ - ContentMetadataExtractionService → Extracts metadata      │
│ - EmbeddingService → Generates embeddings                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ SMART CITY (STORES and GOVERNS)                              │
│ - Content Steward → Stores parsed files                       │
│ - Librarian → Stores content metadata & embeddings            │
│ - Data Steward → Governs semantic contracts & lineage        │
└─────────────────────────────────────────────────────────────┘
```

**Why This Pattern:**
- ✅ **Consistent**: Same pattern for parsing, metadata extraction, embedding generation
- ✅ **Reusable**: Enabling services can be used by multiple orchestrators
- ✅ **Testable**: Work logic separate from storage logic
- ✅ **Scalable**: Can swap implementations in Business Enablement without affecting Smart City

### Key Simplification: Content Metadata Generation

**Previous Approach (Complex):**
- Parse file → Extract metadata during parsing → Store metadata separately
- Required parsing files twice (once for parsing, once for metadata)

**New Approach (Simple & Architecturally Consistent):**
- Parse file → Store parsed files → **Business Enablement extracts metadata** → **Librarian stores metadata**
- **Structured (Parquet)**: Extract schema from Parquet file
- **Unstructured (JSON chunks)**: Extract chunk metadata from JSON chunks file
- **Hybrid**: Extract schema from Parquet + chunk metadata from JSON + correlation map

**Architectural Pattern (Consistent with Parsing):**
```
FileParserService (Business Enablement) → DOES parsing work
Content Steward (Smart City) → STORES parsed files

ContentMetadataExtractionService (Business Enablement) → DOES metadata extraction work ⚠️ **DEFERRED**
Librarian (Smart City) → STORES content metadata ✅ **Phase 1**

EmbeddingService (Business Enablement) → DOES embedding generation work ⚠️ **DEFERRED**
Librarian (Smart City) → STORES embeddings ✅ **Phase 1**

**Temporary:** Use existing StatelessHFInferenceAgent + inline metadata extraction
```

**Benefits:**
- ✅ No double parsing
- ✅ Metadata comes from source of truth (parsed files)
- ✅ More efficient (reuses stored parsed files)
- ✅ Clearer separation (content metadata = structural, embeddings = semantic)
- ✅ **Architecturally consistent** (Business Enablement = work, Smart City = storage & governance)

---

## Phase 0: Foundation & Preparation (Week 1)

### Goal
Set up infrastructure, clarify boundaries, and prepare for implementation.

---

### Phase 0.1: Infrastructure Abstractions Separation

**Objective:** Separate Content Metadata and Embeddings into distinct abstractions.

#### Step 0.1.1: Create Semantic Data Abstraction

**File:** `foundations/public_works_foundation/infrastructure_abstractions/semantic_data_abstraction.py`

**Purpose:** New abstraction for semantic data (embeddings, semantic graphs) - separate from content metadata.

**Implementation:**
```python
class SemanticDataAbstraction(SemanticDataProtocol):
    """
    Semantic Data Abstraction - Manages semantic data (embeddings, semantic graphs).
    
    WHAT: I manage semantic data storage and retrieval (embeddings, semantic graphs)
    HOW: I use ArangoDB for semantic data storage
    """
    
    def __init__(self, arango_adapter, config_adapter, di_container=None):
        self.arango_adapter = arango_adapter
        self.config_adapter = config_adapter
        self.di_container = di_container
        
        # Semantic data collections
        self.structured_embeddings_collection = "structured_embeddings"
        self.semantic_graph_nodes_collection = "semantic_graph_nodes"
        self.semantic_graph_edges_collection = "semantic_graph_edges"
        self.correlation_maps_collection = "correlation_maps"  # NEW: For hybrid parsing
    
    # ============================================================================
    # EMBEDDING OPERATIONS
    # ============================================================================
    
    async def store_semantic_embeddings(
        self,
        content_id: str,
        file_id: str,
        embeddings: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Store semantic embeddings for structured content."""
        # Move from ContentMetadataAbstraction
        pass
    
    async def get_semantic_embeddings(
        self,
        content_id: str,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get semantic embeddings with filtering."""
        pass
    
    async def query_by_semantic_id(
        self,
        semantic_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query embeddings by semantic ID."""
        pass
    
    async def vector_search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Vector similarity search."""
        pass
    
    # ============================================================================
    # SEMANTIC GRAPH OPERATIONS
    # ============================================================================
    
    async def store_semantic_graph(
        self,
        content_id: str,
        file_id: str,
        semantic_graph: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Store semantic graph for unstructured content."""
        # Move from ContentMetadataAbstraction
        pass
    
    async def get_semantic_graph(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get semantic graph for content."""
        pass
    
    # ============================================================================
    # CORRELATION MAP OPERATIONS (NEW: For hybrid parsing)
    # ============================================================================
    
    async def store_correlation_map(
        self,
        content_id: str,
        file_id: str,
        correlation_map: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Store correlation map linking structured and unstructured data."""
        pass
    
    async def get_correlation_map(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get correlation map for hybrid content."""
        pass
```

**Migration Steps:**
1. Create `SemanticDataAbstraction` class
2. Move embedding methods from `ContentMetadataAbstraction` to `SemanticDataAbstraction`
3. Move semantic graph methods from `ContentMetadataAbstraction` to `SemanticDataAbstraction`
4. Update `ContentMetadataAbstraction` to remove semantic methods
5. Update protocol definitions

---

#### Step 0.1.2: Simplify Content Metadata Abstraction

**File:** `foundations/public_works_foundation/infrastructure_abstractions/content_metadata_abstraction.py`

**Purpose:** Remove semantic fields, keep only structural and parsing metadata.

**Changes:**
```python
# REMOVE these fields from content_metadata:
- entities
- keywords
- topics
- sentiment

# KEEP these fields:
- content_id
- file_id
- content_type
- structure_type
- schema
- columns
- data_types
- row_count
- column_count
- unique_values
- null_counts
- parsing_method
- parsing_confidence
- parsing_errors
- has_embeddings (NEW: flag)
- has_semantic_graph (NEW: flag)
- embedding_count (NEW: count)
- semantic_graph_node_count (NEW: count)
```

**Implementation:**
1. Update `create_content_metadata()` to remove semantic fields
2. Update `update_content_metadata()` to prevent semantic field updates
3. Add flags for semantic data existence
4. Update validation logic

---

#### Step 0.1.3: Update Protocol Definitions

**Files:**
- `foundations/public_works_foundation/abstraction_contracts/content_metadata_protocol.py`
- `foundations/public_works_foundation/abstraction_contracts/semantic_data_protocol.py` (NEW)

**Purpose:** Define clear contracts for each abstraction.

**Content Metadata Protocol:**
```python
class ContentMetadataProtocol(Protocol):
    """Protocol for content metadata operations (structural + parsing)."""
    
    async def create_content_metadata(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create content metadata (structural + parsing info only)."""
        ...
    
    async def get_content_metadata(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content metadata."""
        ...
    
    # NO semantic methods here
```

**Semantic Data Protocol:**
```python
class SemanticDataProtocol(Protocol):
    """Protocol for semantic data operations (embeddings + semantic graphs)."""
    
    async def store_semantic_embeddings(self, ...) -> Dict[str, Any]:
        """Store semantic embeddings."""
        ...
    
    async def get_semantic_embeddings(self, ...) -> List[Dict[str, Any]]:
        """Get semantic embeddings."""
        ...
    
    async def store_semantic_graph(self, ...) -> Dict[str, Any]:
        """Store semantic graph."""
        ...
    
    # All semantic methods here
```

---

### Phase 0.2: ArangoDB Collection Updates

**Objective:** Update ArangoDB collections and indexes for new structure.

#### Step 0.2.1: Update Collection Schema

**File:** `scripts/initialize_arangodb_collections.py`

**Changes:**
1. **content_metadata collection:**
   - Remove semantic fields (entities, keywords, topics, sentiment)
   - Add flags (has_embeddings, has_semantic_graph)
   - Add counts (embedding_count, semantic_graph_node_count)

2. **structured_embeddings collection:**
   - Keep as-is (already correct)
   - Ensure content_id link exists

3. **semantic_graph_nodes collection:**
   - Keep as-is (already correct)
   - Ensure content_id link exists

4. **correlation_maps collection (NEW):**
   - For hybrid parsing correlation maps
   - Fields: content_id, file_id, structured_data_map, unstructured_data_map, correlation_rules

#### Step 0.2.2: Create Migration Script

**File:** `scripts/migrate_content_metadata_schema.py`

**Purpose:** Migrate existing content_metadata documents to remove semantic fields.

**Implementation:**
```python
async def migrate_content_metadata():
    """Remove semantic fields from content_metadata collection."""
    # 1. Query all content_metadata documents
    # 2. Remove entities, keywords, topics, sentiment fields
    # 3. Add has_embeddings, has_semantic_graph flags
    # 4. Update documents
    pass
```

---

### Phase 0.3: Service Boundary Clarification

**Objective:** Clarify RACI for Data Steward, Content Steward, Librarian.

#### Step 0.3.1: Create RACI Document

**File:** `docs/SMART_CITY_SERVICE_RACI.md`

**RACI Matrix:**

| Capability | Content Steward | Librarian | Data Steward |
|-----------|----------------|-----------|--------------|
| **Raw File Storage** | ✅ Responsible | - | - |
| **File Lifecycle** | ✅ Responsible | - | - |
| **File Classification** | ✅ Responsible | - | - |
| **Content Metadata (Structural)** | ✅ Responsible | - | - |
| **Semantic Embeddings** | - | ✅ Responsible | - |
| **Semantic Graph** | - | ✅ Responsible | - |
| **Semantic Search** | - | ✅ Responsible | - |
| **Semantic Contracts** | - | - | ✅ Responsible |
| **Data Governance** | - | - | ✅ Responsible |
| **Lineage Rules** | - | - | ✅ Responsible |
| **Data Policies** | - | - | ✅ Responsible |

---

## Phase 1: Infrastructure & Smart City Storage (Week 2-3)

**Focus:** Smart City infrastructure (abstractions, storage APIs) - NOT Business Enablement services

### Goal
Complete separation of content metadata and embeddings into distinct abstractions and services, following the architectural pattern where Business Enablement does the work and Smart City stores/governs.

### ⚠️ **DEFERRED: Business Enablement Service Creation**

**Decision:** Defer creating new Business Enablement services (ContentMetadataExtractionService, EmbeddingService) until Business Enablement realm refactoring.

**Why:**
- ✅ **Avoid technical debt** - New services should follow new Smart City patterns
- ✅ **Holistic approach** - Better to refactor all Business Enablement services together
- ✅ **Use existing services** - StatelessHFInferenceAgent already exists for embeddings
- ✅ **Focus on infrastructure** - Smart City infrastructure (abstractions, storage) is the foundation

**Temporary Approach (Until Business Enablement Refactoring):**
- ✅ Use existing `StatelessHFInferenceAgent` for embeddings (already exists)
- ✅ Use existing `FileParserService` for parsing (already exists)
- ⚠️ Extract metadata inline in orchestrators (temporary - mark with TODO)
- ✅ Call Librarian SOA APIs to store results

**Phase 1 Focus:** Smart City infrastructure only (abstractions, Librarian storage APIs)

**Future Work (Deferred):**
- See `SMART_CITY_IMPLEMENTATION_PLAN_DEFERRED_WORK.md` for details
- Create `ContentMetadataExtractionService` during Business Enablement refactoring
- Create `EmbeddingService` during Business Enablement refactoring
- Refactor all services to use new Smart City patterns holistically

### Architectural Pattern (Consistent Throughout)

**Pattern:**
```
Business Enablement → DOES the work (processing, extraction, generation)
Smart City → STORES and GOVERNS (storage, lifecycle, governance)
```

**Examples:**
- FileParserService (Business Enablement) → Parses files
- Content Steward (Smart City) → Stores parsed files

- ContentMetadataExtractionService (Business Enablement) → Extracts metadata ⚠️ **DEFERRED**
- Librarian (Smart City) → Stores content metadata ✅ **Phase 1**

- EmbeddingService (Business Enablement) → Generates embeddings ⚠️ **DEFERRED**
- Librarian (Smart City) → Stores embeddings ✅ **Phase 1**

**Temporary (Until Business Enablement Refactoring):**
- Use existing `StatelessHFInferenceAgent` for embeddings
- Extract metadata inline in orchestrators (mark with TODO)
- Call Librarian SOA APIs to store results
```

### Key Insight: Content Metadata Generated FROM Parsed Files

**Simplified Approach:**
Content metadata is **generated FROM parsed files** (not from raw files), after parsing is complete.

**Flow:**
1. **File Upload** → Content Steward (raw file storage in GCS + metadata in Supabase)
2. **File Parsing** → Business Enablement (FileParserService) produces parsed files
3. **Parsed Files Stored** → Content Steward (parsed files in GCS + metadata in Supabase `parsed_data_files` table)
4. **Content Metadata Extracted** → Business Enablement (ContentMetadataExtractionService) reads parsed files and extracts metadata:
   - **Structured (Parquet)**: Extract schema (columns, data types, row count) from Parquet file
   - **Unstructured (JSON chunks)**: Extract chunk metadata (chunk count, word count, character count) from JSON chunks file
   - **Hybrid**: Extract schema from Parquet + chunk metadata from JSON + correlation map reference
5. **Content Metadata Stored** → Librarian stores extracted metadata
6. **Embeddings Generated** → Business Enablement (EmbeddingService) generates embeddings
7. **Embeddings Stored** → Librarian stores generated embeddings

**Why This Is Better:**
- ✅ **Simpler**: No need to parse files twice (once for parsing, once for metadata)
- ✅ **Accurate**: Metadata comes directly from parsed files (source of truth)
- ✅ **Efficient**: Reuses parsed files that are already stored
- ✅ **Clear Separation**: Content metadata = structural info FROM parsed files, Embeddings = semantic meaning (separate)

---

### Phase 1.1: Create Semantic Data Abstraction (Infrastructure)

**Objective:** Create `SemanticDataAbstraction` for storing embeddings and semantic graphs (separate from ContentMetadataAbstraction).

**Focus:** Infrastructure only - Business Enablement service creation is DEFERRED until realm refactoring.

**Key Architectural Pattern (Consistent with Parsing):**
- **Business Enablement** = DOES the work (extraction, generation, processing)
- **Smart City** = STORES and GOVERNS (storage, lifecycle, governance)

**Pattern:**
```
FileParserService (Business Enablement) → DOES parsing
Content Steward (Smart City) → STORES parsed files

ContentMetadataExtractionService (Business Enablement) → DOES metadata extraction
Librarian (Smart City) → STORES content metadata

EmbeddingService (Business Enablement) → DOES embedding generation
Librarian (Smart City) → STORES embeddings
```

**Why This Makes Sense:**
- ✅ **Architecturally consistent** with existing parsing pattern
- ✅ **Clear separation**: Business Enablement = work, Smart City = storage
- ✅ **Reusable**: ContentMetadataExtractionService can be used by multiple orchestrators
- ✅ **Testable**: Extraction logic separate from storage logic

#### Step 1.1.1: Create Semantic Data Abstraction

**File:** `foundations/public_works_foundation/infrastructure_abstractions/semantic_data_abstraction.py` (NEW)

**Purpose:** Infrastructure abstraction for storing semantic data (embeddings, semantic graphs) - separate from content metadata.

**New Approach:** Business Enablement extracts metadata, Librarian stores it.

**Flow:**
1. File uploaded → Content Steward (raw file storage)
2. File parsed → Business Enablement (FileParserService)
3. Parsed files stored → Content Steward (parsed files in GCS + metadata in Supabase `parsed_data_files`)
4. **Content metadata extracted** → Business Enablement (ContentMetadataExtractionService) reads parsed files and extracts metadata
5. **Content metadata stored** → Librarian stores content metadata
6. **Embeddings generated** → Business Enablement (EmbeddingService) generates embeddings
7. **Embeddings stored** → Librarian stores embeddings

**Implementation:**
```python
class SemanticDataAbstraction(SemanticDataProtocol):
    """
    Semantic Data Abstraction - Manages semantic data storage (embeddings, semantic graphs).
    
    WHAT: I manage semantic data storage and retrieval (embeddings, semantic graphs)
    HOW: I use ArangoDB for semantic data storage
    
    Note: This is infrastructure abstraction. Business Enablement services will use this
    via Librarian SOA APIs (not directly).
    """
    
    def __init__(self, arango_adapter, config_adapter, di_container=None):
        self.arango_adapter = arango_adapter
        self.config_adapter = config_adapter
        self.di_container = di_container
        
        # Semantic data collections
        self.structured_embeddings_collection = "structured_embeddings"
        self.semantic_graph_nodes_collection = "semantic_graph_nodes"
        self.semantic_graph_edges_collection = "semantic_graph_edges"
        self.correlation_maps_collection = "correlation_maps"  # NEW: For hybrid parsing
    
    # ============================================================================
    # EMBEDDING OPERATIONS
    # ============================================================================
    
    async def store_semantic_embeddings(
        self,
        content_id: str,
        file_id: str,
        embeddings: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Store semantic embeddings for structured content."""
        # Move from ContentMetadataAbstraction
        pass
    
    async def get_semantic_embeddings(
        self,
        content_id: str,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get semantic embeddings with filtering."""
        pass
    
    async def query_by_semantic_id(
        self,
        semantic_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query embeddings by semantic ID."""
        pass
    
    async def vector_search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Vector similarity search."""
        pass
    
    # ============================================================================
    # SEMANTIC GRAPH OPERATIONS
    # ============================================================================
    
    async def store_semantic_graph(
        self,
        content_id: str,
        file_id: str,
        semantic_graph: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Store semantic graph for unstructured content."""
        # Move from ContentMetadataAbstraction
        pass
    
    async def get_semantic_graph(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get semantic graph for content."""
        pass
    
    # ============================================================================
    # CORRELATION MAP OPERATIONS (NEW: For hybrid parsing)
    # ============================================================================
    
    async def store_correlation_map(
        self,
        content_id: str,
        file_id: str,
        correlation_map: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Store correlation map linking structured and unstructured data."""
        pass
    
    async def get_correlation_map(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get correlation map for hybrid content."""
        pass
```

**Note:** This is infrastructure only. Business Enablement services (ContentMetadataExtractionService, EmbeddingService) will be created later during realm refactoring.
        
        # 2. Generate metadata based on format type
        if format_type == "parquet":
            # Structured: Extract schema from Parquet
            content_metadata = await self._extract_schema_from_parquet(parsed_file_data)
        elif format_type == "json_chunks":
            # Unstructured: Extract chunk metadata from JSON chunks
            content_metadata = await self._extract_metadata_from_json_chunks(parsed_file_data)
        elif format_type == "json_structured":
            # Structured JSON: Extract schema from JSON
            content_metadata = await self._extract_schema_from_json(parsed_file_data)
        else:
            raise ValueError(f"Unsupported format_type: {format_type}")
        
        # 3. Add file linkage
        content_metadata["file_id"] = file_id
        content_metadata["parsed_file_id"] = parsed_file_id
        content_metadata["format_type"] = format_type
        content_metadata["content_type"] = content_type
        
        # 4. Return extracted metadata (NOT stored - that's Librarian's job)
        return {
            "success": True,
            "content_metadata": content_metadata,
            "format_type": format_type,
            "content_type": content_type
        }
    
    async def _extract_schema_from_parquet(
        self,
        parquet_data: bytes
    ) -> Dict[str, Any]:
        """Extract schema from Parquet file."""
        import pyarrow.parquet as pq
        import io
        
        # Read Parquet file
        parquet_file = pq.ParquetFile(io.BytesIO(parquet_data))
        schema = parquet_file.schema
        metadata = parquet_file.metadata
        
        # Extract schema information
        columns = [field.name for field in schema]
        data_types = {field.name: str(field.type) for field in schema}
        
        # Get row count
        row_count = metadata.num_rows
        
        return {
            "content_id": str(uuid.uuid4()),
            "structure_type": "tabular",
            "schema": {
                "columns": columns,
                "data_types": data_types,
                "row_count": row_count,
                "column_count": len(columns)
            },
            "columns": columns,
            "data_types": data_types,
            "row_count": row_count,
            "column_count": len(columns),
            "parsing_method": "parquet",
            "parsing_confidence": 1.0  # Parquet is already structured
        }
    
    async def _extract_metadata_from_json_chunks(
        self,
        json_chunks_data: bytes
    ) -> Dict[str, Any]:
        """Extract metadata from JSON chunks file."""
        import json
        
        # Parse JSON chunks
        chunks_data = json.loads(json_chunks_data.decode('utf-8'))
        chunks = chunks_data.get("chunks", [])
        metadata = chunks_data.get("metadata", {})
        
        # Extract chunk metadata
        total_chunks = len(chunks)
        total_characters = sum(chunk.get("char_count", 0) for chunk in chunks)
        total_words = sum(chunk.get("word_count", 0) for chunk in chunks)
        
        return {
            "content_id": str(uuid.uuid4()),
            "structure_type": "text",
            "schema": {
                "total_chunks": total_chunks,
                "total_characters": total_characters,
                "total_words": total_words,
                "chunk_size": metadata.get("chunk_size", 0)
            },
            "chunk_count": total_chunks,
            "word_count": total_words,
            "line_count": total_chunks,  # Approximate
            "parsing_method": "json_chunks",
            "parsing_confidence": 1.0  # JSON chunks is already parsed
        }
    
    async def _extract_schema_from_json(
        self,
        json_data: bytes
    ) -> Dict[str, Any]:
        """Extract schema from structured JSON file."""
        import json
        
        # Parse JSON
        data = json.loads(json_data.decode('utf-8'))
        
        # Extract schema (assuming array of objects)
        if isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            columns = list(first_item.keys()) if isinstance(first_item, dict) else []
            data_types = {col: type(val).__name__ for col, val in first_item.items()} if isinstance(first_item, dict) else {}
            row_count = len(data)
        else:
            columns = []
            data_types = {}
            row_count = 0
        
        return {
            "content_id": str(uuid.uuid4()),
            "structure_type": "hierarchical",
            "schema": {
                "columns": columns,
                "data_types": data_types,
                "row_count": row_count,
                "column_count": len(columns)
            },
            "columns": columns,
            "data_types": data_types,
            "row_count": row_count,
            "column_count": len(columns),
            "parsing_method": "json_structured",
            "parsing_confidence": 1.0
        }
    
    async def generate_hybrid_content_metadata(
        self,
        file_id: str,
        structured_parsed_file_id: str,
        unstructured_parsed_file_id: str,
        correlation_file_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate content metadata for hybrid files (both structured and unstructured)."""
        # 1. Generate structured metadata from Parquet
        structured_metadata = await self._extract_schema_from_parquet(
            await self.service.file_management_abstraction.get_parsed_file(
                parsed_file_id=structured_parsed_file_id,
                user_context=user_context
            )
        )
        
        # 2. Generate unstructured metadata from JSON chunks
        unstructured_metadata = await self._extract_metadata_from_json_chunks(
            await self.service.file_management_abstraction.get_parsed_file(
                parsed_file_id=unstructured_parsed_file_id,
                user_context=user_context
            )
        )
        
        # 3. Combine into hybrid metadata
        hybrid_metadata = {
            "content_id": str(uuid.uuid4()),
            "file_id": file_id,
            "structure_type": "hybrid",
            "schema": {
                "structured": structured_metadata["schema"],
                "unstructured": unstructured_metadata["schema"],
                "correlation_file_id": correlation_file_id
            },
            "columns": structured_metadata.get("columns", []),
            "data_types": structured_metadata.get("data_types", {}),
            "row_count": structured_metadata.get("row_count", 0),
            "column_count": structured_metadata.get("column_count", 0),
            "chunk_count": unstructured_metadata.get("chunk_count", 0),
            "word_count": unstructured_metadata.get("word_count", 0),
            "parsing_method": "hybrid",
            "parsing_confidence": 1.0
        }
        
        # 4. Return extracted metadata (NOT stored - that's Librarian's job)
        return {
            "success": True,
            "content_metadata": hybrid_metadata,
            "format_type": "hybrid",
            "content_type": "hybrid"
        }
```

---

### Phase 1.2: Update Librarian Service

**Objective:** Librarian owns semantic data operations (embeddings, semantic graphs).

#### Step 1.2.1: Update Librarian Service for Storage

**File:** `backend/smart_city/services/librarian/librarian_service.py`

**Purpose:** Librarian exposes SOA APIs for storing content metadata and embeddings (uses SemanticDataAbstraction and ContentMetadataAbstraction).

**Note:** Business Enablement service creation is DEFERRED. For now, orchestrators will:
- Use existing `StatelessHFInferenceAgent` for embeddings (already exists)
- Extract metadata inline (temporary) until Business Enablement refactoring
- Call Librarian SOA APIs to store results

**Implementation:**
```python
class SemanticData:
    """Semantic data module for Librarian service."""
    
    def __init__(self, service: Any):
        self.service = service
        self.semantic_data_abstraction = None  # SemanticDataAbstraction
    
    async def store_embeddings(
        self,
        content_id: str,
        file_id: str,
        embeddings: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Store semantic embeddings via SemanticDataAbstraction."""
        if not self.semantic_data_abstraction:
            self.semantic_data_abstraction = self.service.get_abstraction("semantic_data")
        
        return await self.semantic_data_abstraction.store_semantic_embeddings(
            content_id=content_id,
            file_id=file_id,
            embeddings=embeddings,
            user_context=user_context
        )
    
    async def query_semantic(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query semantic data (embeddings + semantic graph)."""
        # Use SemanticDataAbstraction
        pass
    
    async def vector_search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Vector similarity search."""
        pass
```

#### Step 1.2.2: Update Librarian Service for Storage

**File:** `backend/smart_city/services/librarian/librarian_service.py`

**Changes:**
1. Add `semantic_data_abstraction` to infrastructure abstractions
2. Add `content_metadata_abstraction` to infrastructure abstractions
3. Initialize `SemanticData` module (for storage)
4. Initialize `ContentMetadataStorage` module (NEW - for storage only, not extraction)
5. Expose semantic data storage SOA APIs
6. Expose content metadata storage SOA APIs (NEW)

**Note:** Librarian STORES content metadata and embeddings, but doesn't GENERATE them (that's Business Enablement's job).

**Implementation:**
```python
class LibrarianService(SmartCityRoleBase, LibrarianServiceProtocol):
    def __init__(self, di_container: Any):
        # ... existing code ...
        
        # Infrastructure Abstractions
        self.knowledge_discovery_abstraction = None  # Meilisearch + Redis Graph + ArangoDB
        self.knowledge_governance_abstraction = None  # Metadata + ArangoDB
        self.semantic_data_abstraction = None  # SemanticDataAbstraction (for storage)
        self.content_metadata_abstraction = None  # ContentMetadataAbstraction (for storage)
        self.messaging_abstraction = None  # Redis for caching
        
        # Initialize modules
        self.semantic_data_module = SemanticData(self)  # Storage module
        self.content_metadata_storage_module = ContentMetadataStorage(self)  # NEW: Storage only
```

---

### Phase 1.3: Update Business Enablement Services

**Objective:** Update orchestrators and enabling services to use correct abstractions.

#### Step 1.3.1: Update ContentAnalysisOrchestrator

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/content_analysis_orchestrator.py`

**Changes:**
1. After parsing, store parsed files via Content Steward
2. Trigger content metadata generation via Content Steward (from parsed files)
3. Use `SemanticDataAbstraction` (via Librarian) for semantic data (embeddings)
4. Update flow to: Parse → Store Parsed Files → Generate Content Metadata → Store Embeddings

**Updated Flow:**
```python
async def parse_and_process_file(self, file_id: str, ...):
    """Parse file and process through pipeline."""
    # 1. Parse file
    parse_result = await self.file_parser_service.parse_file(file_id, ...)
    
    # 2. Store parsed files via Content Steward
    parsed_file_metadata = await self.content_steward.store_parsed_file(
        file_id=file_id,
        parsed_data=parse_result,
        format_type=parse_result["format_type"],  # "parquet", "json_chunks", etc.
        content_type=parse_result["content_type"],  # "structured", "unstructured", "hybrid"
        user_context=user_context
    )
    
    # 3. Extract content metadata FROM parsed files (TEMPORARY: inline until Business Enablement refactoring)
    # TODO: Move to ContentMetadataExtractionService during Business Enablement refactoring
    extracted_metadata = await self._extract_content_metadata_inline(
        parsed_file_id=parsed_file_metadata["parsed_file_id"],
        format_type=parse_result["format_type"],
        content_type=parse_result["content_type"],
        user_context=user_context
    )
    
    # 4. Store content metadata via Librarian (Smart City)
    librarian = self.get_smart_city_api("librarian")
    content_metadata = await librarian.store_content_metadata(
        file_id=file_id,
        parsed_file_id=parsed_file_metadata["parsed_file_id"],
        content_metadata=extracted_metadata,
        user_context=user_context
    )
    
    # 5. Generate embeddings (TEMPORARY: use existing StatelessHFInferenceAgent until Business Enablement refactoring)
    # TODO: Move to EmbeddingService during Business Enablement refactoring
    hf_agent = self._get_stateless_hf_agent()  # Use existing agent
    semantic_result = await self._generate_embeddings_via_hf_agent(
        parse_result=parse_result,
        content_metadata=content_metadata,
        hf_agent=hf_agent,
        user_context=user_context
    )
    
    # 6. Store embeddings via Librarian (Smart City)
    await librarian.store_embeddings(
        content_id=content_metadata["content_id"],
        file_id=file_id,
        embeddings=semantic_result["embeddings"],
        user_context=user_context
    )
    
    # 7. Update content metadata flags (has_embeddings = True) - Librarian owns this
    await librarian.update_content_metadata(
        content_id=content_metadata["content_id"],
        updates={"has_embeddings": True, "embedding_count": len(semantic_result["embeddings"])}
    )
```

**Implementation:**
```python
async def _store_semantic_via_librarian(
    self,
    file_id: str,
    parse_result: Dict[str, Any],
    semantic_result: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Store semantic data via Librarian (not Content Steward)."""
    # 1. Get Librarian service
    librarian = self.get_smart_city_api("librarian")
    
    # 2. Store embeddings via Librarian
    if semantic_result.get("embeddings"):
        await librarian.store_embeddings(
            content_id=file_id,  # Use file_id as content_id
            file_id=file_id,
            embeddings=semantic_result["embeddings"],
            user_context=user_context
        )
    
    # 3. Store semantic graph via Librarian
    if semantic_result.get("semantic_graph"):
        await librarian.store_semantic_graph(
            content_id=file_id,
            file_id=file_id,
            semantic_graph=semantic_result["semantic_graph"],
            user_context=user_context
        )
    
    # 4. Update content metadata flags
    content_metadata = self.get_abstraction("content_metadata")
    await content_metadata.update_content_metadata(file_id, {
        "has_embeddings": bool(semantic_result.get("embeddings")),
        "has_semantic_graph": bool(semantic_result.get("semantic_graph")),
        "embedding_count": len(semantic_result.get("embeddings", [])),
        "semantic_graph_node_count": len(semantic_result.get("semantic_graph", {}).get("nodes", []))
    })
```

---

## Phase 2: Nurse Observability Enhancement (Week 4-5)

### Goal
Enhance Nurse service with comprehensive observability, including agentic tracking.

---

### Phase 2.1: Create Observability Abstraction

**Objective:** Create unified observability abstraction for platform data storage.

#### Step 2.1.1: Create Observability Abstraction

**File:** `foundations/public_works_foundation/infrastructure_abstractions/observability_abstraction.py` (NEW)

**Purpose:** Unified interface for storing observability data (logs, metrics, traces, agent execution).

**Implementation:**
```python
class ObservabilityAbstraction(ObservabilityProtocol):
    """
    Observability Abstraction - Manages platform observability data.
    
    WHAT: I manage platform observability data (logs, metrics, traces, agent execution)
    HOW: I use ArangoDB for platform data storage, OpenTelemetry for collection
    """
    
    def __init__(self, arango_adapter, telemetry_abstraction, config_adapter, di_container=None):
        self.arango_adapter = arango_adapter
        self.telemetry_abstraction = telemetry_abstraction
        self.config_adapter = config_adapter
        self.di_container = di_container
        
        # Platform data collections
        self.platform_logs_collection = "platform_logs"
        self.platform_metrics_collection = "platform_metrics"
        self.platform_traces_collection = "platform_traces"
        self.agent_execution_collection = "agent_execution"  # NEW: Agent tracking
    
    # ============================================================================
    # PLATFORM LOG OPERATIONS
    # ============================================================================
    
    async def record_platform_log(
        self,
        log_level: str,
        message: str,
        service_name: str,
        trace_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record platform log event."""
        log_doc = {
            "_key": str(uuid.uuid4()),
            "log_level": log_level,
            "message": message,
            "service_name": service_name,
            "trace_id": trace_id,
            "tenant_id": user_context.get("tenant_id") if user_context else None,
            "data_classification": "platform",  # Always platform data
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self.arango_adapter.create_document(
            self.platform_logs_collection,
            log_doc
        )
    
    # ============================================================================
    # PLATFORM METRIC OPERATIONS
    # ============================================================================
    
    async def record_platform_metric(
        self,
        metric_name: str,
        metric_value: float,
        service_name: str,
        trace_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record platform metric."""
        # Store in ArangoDB AND send to OpenTelemetry
        pass
    
    # ============================================================================
    # PLATFORM TRACE OPERATIONS
    # ============================================================================
    
    async def record_platform_trace(
        self,
        trace_id: str,
        span_id: str,
        operation_name: str,
        service_name: str,
        duration_ms: float,
        status: str,
        user_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record platform trace."""
        # Store in ArangoDB AND send to OpenTelemetry/Tempo
        pass
    
    # ============================================================================
    # AGENT EXECUTION TRACKING (NEW)
    # ============================================================================
    
    async def record_agent_execution(
        self,
        agent_id: str,
        agent_name: str,
        prompt_hash: str,
        response: str,
        trace_id: Optional[str] = None,
        execution_metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record agent execution for observability."""
        execution_doc = {
            "_key": str(uuid.uuid4()),
            "agent_id": agent_id,
            "agent_name": agent_name,
            "prompt_hash": prompt_hash,
            "response": response,
            "trace_id": trace_id,
            "data_classification": "platform",  # Always platform data
            "execution_metadata": execution_metadata or {},
            "tenant_id": user_context.get("tenant_id") if user_context else None,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self.arango_adapter.create_document(
            self.agent_execution_collection,
            execution_doc
        )
    
    async def get_agent_executions(
        self,
        agent_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query agent executions."""
        pass
    
    # ============================================================================
    # CORRELATION OPERATIONS
    # ============================================================================
    
    async def correlate_trace(
        self,
        trace_id: str,
        correlation_key: str,
        correlation_value: str
    ) -> Dict[str, Any]:
        """Correlate trace with other data."""
        pass
```

---

### Phase 2.2: Update Nurse Service

**Objective:** Nurse uses ObservabilityAbstraction for all observability operations.

#### Step 2.2.1: Add Observability Module to Nurse

**File:** `backend/smart_city/services/nurse/modules/observability.py` (NEW)

**Implementation:**
```python
class Observability:
    """Observability module for Nurse service."""
    
    def __init__(self, service: Any):
        self.service = service
        self.observability_abstraction = None
    
    async def record_platform_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        trace_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record platform event (log, metric, or trace)."""
        if not self.observability_abstraction:
            self.observability_abstraction = self.service.get_abstraction("observability")
        
        if event_type == "log":
            return await self.observability_abstraction.record_platform_log(
                log_level=event_data.get("level", "info"),
                message=event_data.get("message", ""),
                service_name=event_data.get("service_name", "unknown"),
                trace_id=trace_id,
                user_context=user_context,
                metadata=event_data.get("metadata")
            )
        elif event_type == "metric":
            return await self.observability_abstraction.record_platform_metric(
                metric_name=event_data.get("metric_name", ""),
                metric_value=event_data.get("value", 0.0),
                service_name=event_data.get("service_name", "unknown"),
                trace_id=trace_id,
                user_context=user_context,
                metadata=event_data.get("metadata")
            )
        elif event_type == "trace":
            return await self.observability_abstraction.record_platform_trace(
                trace_id=trace_id or event_data.get("trace_id", ""),
                span_id=event_data.get("span_id", ""),
                operation_name=event_data.get("operation_name", ""),
                service_name=event_data.get("service_name", "unknown"),
                duration_ms=event_data.get("duration_ms", 0.0),
                status=event_data.get("status", "ok"),
                user_context=user_context,
                metadata=event_data.get("metadata")
            )
    
    async def record_agent_execution(
        self,
        agent_id: str,
        agent_name: str,
        prompt_hash: str,
        response: str,
        trace_id: Optional[str] = None,
        execution_metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record agent execution."""
        if not self.observability_abstraction:
            self.observability_abstraction = self.service.get_abstraction("observability")
        
        return await self.observability_abstraction.record_agent_execution(
            agent_id=agent_id,
            agent_name=agent_name,
            prompt_hash=prompt_hash,
            response=response,
            trace_id=trace_id,
            execution_metadata=execution_metadata,
            user_context=user_context
        )
    
    async def get_observability_data(
        self,
        data_type: str,  # "logs", "metrics", "traces", "agent_execution"
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query observability data."""
        pass
```

#### Step 2.2.2: Update Nurse Service Initialization

**File:** `backend/smart_city/services/nurse/nurse_service.py`

**Changes:**
1. Add `observability_abstraction` to infrastructure abstractions
2. Initialize `Observability` module
3. Expose observability SOA APIs

**Implementation:**
```python
class NurseService(SmartCityRoleBase, NurseServiceProtocol):
    def __init__(self, di_container: Any):
        # ... existing code ...
        
        # Infrastructure Abstractions
        self.telemetry_abstraction = None  # OpenTelemetry + Tempo
        self.observability_abstraction = None  # NEW: ObservabilityAbstraction
        self.alert_management_abstraction = None
        self.health_abstraction = None
        
        # Initialize modules
        self.observability_module = Observability(self)  # NEW
```

#### Step 2.2.3: Expose Observability SOA APIs

**File:** `backend/smart_city/services/nurse/modules/soa_mcp.py`

**Add SOA APIs:**
```python
async def initialize_soa_api_exposure(self):
    """Initialize SOA API exposure."""
    # ... existing APIs ...
    
    # NEW: Observability APIs
    self.service.soa_apis["record_platform_event"] = {
        "method": self.observability_module.record_platform_event,
        "description": "Record platform event (log, metric, or trace)",
        "parameters": {
            "event_type": "str",  # "log", "metric", "trace"
            "event_data": "Dict[str, Any]",
            "trace_id": "Optional[str]",
            "user_context": "Optional[Dict[str, Any]]"
        }
    }
    
    self.service.soa_apis["record_agent_execution"] = {
        "method": self.observability_module.record_agent_execution,
        "description": "Record agent execution for observability",
        "parameters": {
            "agent_id": "str",
            "agent_name": "str",
            "prompt_hash": "str",
            "response": "str",
            "trace_id": "Optional[str]",
            "execution_metadata": "Optional[Dict[str, Any]]",
            "user_context": "Optional[Dict[str, Any]]"
        }
    }
    
    self.service.soa_apis["get_observability_data"] = {
        "method": self.observability_module.get_observability_data,
        "description": "Query observability data (logs, metrics, traces, agent execution)",
        "parameters": {
            "data_type": "str",  # "logs", "metrics", "traces", "agent_execution"
            "filters": "Optional[Dict[str, Any]]",
            "user_context": "Optional[Dict[str, Any]]"
        }
    }
```

---

### Phase 2.3: Update Agentic Foundation

**Objective:** Agentic Foundation uses Nurse for agent execution tracking.

#### Step 2.3.1: Update Agent Base

**File:** `backend/business_enablement/agents/declarative_agent_base.py`

**Changes:**
1. Track agent execution via Nurse
2. Record prompt hash, response, execution metadata

**Implementation:**
```python
class AgentBase:
    async def execute(self, ...):
        """Execute agent with tracking."""
        # ... existing execution logic ...
        
        # Track execution via Nurse
        nurse = self.get_smart_city_api("nurse")
        if nurse:
            await nurse.record_agent_execution(
                agent_id=self.agent_name,
                agent_name=self.agent_name,
                prompt_hash=prompt_hash,  # Hash of prompt config
                response=response,
                trace_id=trace_id,
                execution_metadata={
                    "model_name": model_name,
                    "inference_time": inference_time,
                    "token_count": token_count,
                    "cost_estimate": cost_estimate
                },
                user_context=user_context
            )
```

---

## Phase 3: Service Alignment (Week 6-7)

### Goal
Align Data Steward, Content Steward, and Librarian with clear boundaries.

---

### Phase 3.1: Content Steward Finalization

**Objective:** Content Steward owns raw data storage, file lifecycle, classification.

#### Step 3.1.1: Update Content Steward SOA APIs

**File:** `backend/smart_city/services/content_steward/modules/soa_mcp.py`

**SOA APIs:**
```python
# File Lifecycle APIs
- upload_file()
- get_file()
- delete_file()
- list_files()
- classify_file()  # data_classification: "client" or "platform"

# Parsed File Storage APIs
- store_parsed_file()  # Store parsed files in GCS + metadata in Supabase
- get_parsed_file()  # Retrieve parsed file data
- list_parsed_files()  # List parsed files for a file_id
```

**NO content metadata APIs** (those belong to Librarian).  
**NO semantic data APIs** (those belong to Librarian).

---

### Phase 3.2: Librarian Finalization

**Objective:** Librarian owns semantic data (embeddings, semantic graphs, semantic search).

#### Step 3.2.1: Update Librarian SOA APIs

**File:** `backend/smart_city/services/librarian/modules/soa_mcp.py`

**SOA APIs:**
```python
# Content Metadata Storage APIs (NEW)
- store_content_metadata()  # Store extracted metadata (from Business Enablement)
- get_content_metadata()
- update_content_metadata()
- get_content_structure()  # Schema, columns, data types

# Semantic Data APIs
- store_embeddings()
- get_embeddings()
- query_by_semantic_id()
- vector_search()
- store_semantic_graph()
- get_semantic_graph()
- store_correlation_map()  # NEW: For hybrid parsing
- get_correlation_map()

# Semantic Search APIs
- search_semantic()  # Unified semantic search
- search_metadata()  # Meilisearch for metadata search
```

---

### Phase 3.3: Data Steward Finalization

**Objective:** Data Steward owns semantic contracts, governance, lineage.

#### Step 3.3.1: Update Data Steward SOA APIs

**File:** `backend/smart_city/services/data_steward/modules/soa_mcp.py`

**SOA APIs:**
```python
# Semantic Contract APIs
- create_semantic_contract()
- get_semantic_contract()
- update_semantic_contract()
- validate_semantic_contract()

# Governance APIs
- create_data_policy()
- get_data_policy()
- enforce_data_policy()

# Lineage APIs
- track_lineage()
- get_lineage()
- query_lineage()
```

**NO file lifecycle APIs** (those belong to Content Steward).  
**NO semantic storage APIs** (those belong to Librarian).

---

## Phase 4: DIL SDK Creation (Week 8)

### Goal
Create DIL SDK as client library wrapping Smart City SOA APIs.

---

### Phase 4.1: Create DIL SDK Structure

**File:** `foundations/data_intelligence_sdk/dil_sdk.py` (NEW)

**Implementation:**
```python
class DILSDK:
    """
    Data Intelligence Layer SDK - Client library for Smart City services.
    
    WHAT: I provide unified interface for data operations
    HOW: I wrap Smart City SOA APIs
    """
    
    def __init__(self, smart_city_services: Dict[str, Any]):
        """Initialize DIL SDK with Smart City services."""
        self.content_steward = smart_city_services.get("content_steward")
        self.librarian = smart_city_services.get("librarian")
        self.data_steward = smart_city_services.get("data_steward")
        self.nurse = smart_city_services.get("nurse")
        # ... other services
    
    # ============================================================================
    # DATA OPERATIONS (Unified Interface)
    # ============================================================================
    
    async def upload_file(
        self,
        file_data: bytes,
        file_name: str,
        file_type: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Upload file via Content Steward."""
        return await self.content_steward.upload_file(
            file_data=file_data,
            file_name=file_name,
            file_type=file_type,
            user_context=user_context
        )
    
    async def store_semantic_embeddings(
        self,
        content_id: str,
        file_id: str,
        embeddings: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Store semantic embeddings via Librarian."""
        return await self.librarian.store_embeddings(
            content_id=content_id,
            file_id=file_id,
            embeddings=embeddings,
            user_context=user_context
        )
    
    async def query_semantic(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query semantic data via Librarian."""
        return await self.librarian.query_semantic(
            query=query,
            filters=filters,
            user_context=user_context
        )
    
    async def create_semantic_contract(
        self,
        contract_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create semantic contract via Data Steward."""
        return await self.data_steward.create_semantic_contract(
            contract_data=contract_data,
            user_context=user_context
        )
    
    # ============================================================================
    # OBSERVABILITY OPERATIONS
    # ============================================================================
    
    async def record_platform_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        trace_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record platform event via Nurse."""
        return await self.nurse.record_platform_event(
            event_type=event_type,
            event_data=event_data,
            trace_id=trace_id,
            user_context=user_context
        )
    
    async def record_agent_execution(
        self,
        agent_id: str,
        agent_name: str,
        prompt_hash: str,
        response: str,
        trace_id: Optional[str] = None,
        execution_metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record agent execution via Nurse."""
        return await self.nurse.record_agent_execution(
            agent_id=agent_id,
            agent_name=agent_name,
            prompt_hash=prompt_hash,
            response=response,
            trace_id=trace_id,
            execution_metadata=execution_metadata,
            user_context=user_context
        )
```

---

### Phase 4.2: Update Business Enablement to Use DIL SDK

**Objective:** Update orchestrators and enabling services to use DIL SDK.

#### Step 4.2.1: Update ContentAnalysisOrchestrator

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/content_analysis_orchestrator.py`

**Changes:**
1. Initialize DIL SDK
2. Use DIL SDK for all data operations

**Implementation:**
```python
class ContentAnalysisOrchestrator(OrchestratorBase):
    def __init__(self, di_container: Any):
        # ... existing code ...
        
        # Initialize DIL SDK
        self.dil_sdk = self._initialize_dil_sdk()
    
    def _initialize_dil_sdk(self) -> DILSDK:
        """Initialize DIL SDK with Smart City services."""
        smart_city_services = {
            "content_steward": self.get_smart_city_api("content_steward"),
            "librarian": self.get_smart_city_api("librarian"),
            "data_steward": self.get_smart_city_api("data_steward"),
            "nurse": self.get_smart_city_api("nurse")
        }
        return DILSDK(smart_city_services)
    
    async def parse_file(self, ...):
        """Parse file using DIL SDK."""
        # Use DIL SDK for all data operations
        file_metadata = await self.dil_sdk.upload_file(...)
        # ... parsing logic ...
        await self.dil_sdk.store_semantic_embeddings(...)
```

---

## Phase 5: Testing & Validation (Week 9-10)

### Goal
Comprehensive testing and validation of all changes.

---

### Phase 5.1: Unit Tests

**Objective:** Test each service and abstraction independently.

**Test Files:**
- `tests/test_semantic_data_abstraction.py`
- `tests/test_content_metadata_abstraction.py`
- `tests/test_observability_abstraction.py`
- `tests/test_librarian_service.py`
- `tests/test_nurse_service.py`
- `tests/test_dil_sdk.py`

---

### Phase 5.2: Integration Tests

**Objective:** Test end-to-end flows.

**Test Scenarios:**
1. File upload → Parse → Embed → Store semantic data
2. Agent execution → Track via Nurse
3. Semantic query → Retrieve via Librarian
4. Platform event → Record via Nurse

---

### Phase 5.3: Migration Validation

**Objective:** Validate content_metadata migration.

**Test:**
1. Verify semantic fields removed
2. Verify flags added
3. Verify embeddings still linked correctly

---

## Summary

### What Changes

1. **Content Metadata & Embeddings Separated:**
   - `ContentMetadataAbstraction` → Structural + parsing only
   - `SemanticDataAbstraction` → Embeddings + semantic graphs (NEW)

2. **Deferred: Business Enablement Service Creation:**
   - ContentMetadataExtractionService → DEFERRED (will create during Business Enablement refactoring)
   - EmbeddingService → DEFERRED (will create during Business Enablement refactoring)
   - **Temporary:** Use existing StatelessHFInferenceAgent for embeddings
   - **Temporary:** Extract metadata inline in orchestrators

3. **Librarian Stores All Content Knowledge:**
   - Content metadata storage (from Business Enablement)
   - Semantic data storage (embeddings, semantic graphs from Business Enablement)
   - Single "content knowledge storage layer"

3. **Content Steward Simplified:**
   - Raw data storage and lifecycle
   - Parsed file storage
   - NO content metadata generation (moved to Librarian)

4. **Nurse Enhanced:**
   - `ObservabilityAbstraction` → Platform data storage (NEW)
   - Agent execution tracking
   - Unified observability interface

5. **Service Alignment:**
   - Content Steward → Raw data, file lifecycle, parsed file storage
   - Business Enablement → **Temporary:** Inline metadata extraction, use existing HF agent for embeddings
   - Librarian → Content metadata storage, semantic data storage, semantic search (STORES and GOVERNS)
   - Data Steward → Semantic contracts, governance

6. **Deferred Work (Business Enablement Refactoring):**
   - Create ContentMetadataExtractionService (following new patterns)
   - Create EmbeddingService (following new patterns)
   - Refactor all Business Enablement services holistically

6. **DIL SDK Created:**
   - Client library wrapping Smart City SOA APIs
   - Unified interface for realms

### Timeline

- **Week 1:** Foundation & Preparation
- **Week 2-3:** Content Metadata & Embeddings Separation
- **Week 4-5:** Nurse Observability Enhancement
- **Week 6-7:** Service Alignment
- **Week 8:** DIL SDK Creation
- **Week 9-10:** Testing & Validation

**Total: 8-10 weeks**

---

## Next Steps

1. **Review this plan**
2. **Start Phase 0** (Foundation & Preparation)
3. **Execute phase-by-phase** with testing at each phase
4. **Update documentation** as we go

**Ready to begin implementation?**

