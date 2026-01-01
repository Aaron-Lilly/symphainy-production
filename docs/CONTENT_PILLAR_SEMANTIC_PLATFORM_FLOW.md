# Content Pillar: Evolution to Semantic Platform Flow (MVP/Demo)

## Executive Summary

This document outlines the **fundamental evolution** of the Content Pillar to align with the semantic platform architecture. The key shift: **parsing is just the first step** - semantic processing (embeddings for structured, semantic graph for unstructured) is the real value.

**MVP/Demo Note:** Validation UI is deferred. We display results read-only and voice over that validation will be available once customers start paying.

---

## New Flow Architecture

### Common Steps (1-5): All Data Types

```
1. User sees all files
   ↓
2. User uploads new file (or selects existing)
   ↓
3. User selects file for parsing
   ↓
4. Platform parses file → parquet/JSON (or simpler formats for embedding agents)
   ↓
5. Platform displays parsed output (read-only display for demo)
   ↓
   [BIFURCATION: Structured vs Unstructured]
```

### Structured Data Path (S6-S8)

```
S6. Platform processes parsed outputs to create 3 embeddings
    - Column metadata embedding
    - Semantic meaning embedding  
    - Sample values embedding
    - Saved in Arango via abstraction
    
S7. Platform displays semantic extraction layer (read-only for demo)
    - Column metadata
    - Semantic meaning (from Column Meaning Agent)
    - Candidate semantic IDs (from Semantic Matching Agent)
    - [Voice over: "Users can validate/correct these mappings"]
    
S8. Insights pillar uses Arango embeddings for analytics
    - Or uses parsed outputs directly
    - Semantic layer enables cross-file reasoning
```

### Unstructured Data Path (U6-U8)

```
U6. Platform processes parsed outputs
    - NLP extraction → normalized entities & relationships
    - Creates semantic graph (nodes = entities, edges = relationships)
    - Saved in Arango via abstraction
    - Instead of structured flow (columns → metadata → semantic ID)
    
U7. Platform displays semantic graph (read-only for demo)
    - Entities extracted
    - Relationships inferred
    - Semantic IDs assigned (from Semantic Matching Agent)
    - [Voice over: "Users can validate/correct the graph"]
    
U8. Insights (and other upstream orchestrators/workflows) use Arango
    - Or use parsed outputs directly
    - Semantic graph enables relationship reasoning
```

---

## Current State vs. New State

### Current State (What We Have)

**Content Pillar:**
- Parse file → returns parquet/JSON
- Maybe some basic metadata extraction
- **End of flow** (or basic analysis)

**Issues:**
- No semantic processing
- No embeddings
- No semantic graph
- Insights uses parsed files directly (no semantic layer)

### New State (What We Need)

**Content Pillar:**
- Parse file → returns parquet/JSON (or simpler formats)
- **Then:** Semantic processing (structured or unstructured)
- **Then:** Store in Arango (embeddings or semantic graph)
- **Then:** Display for viewing (read-only for MVP)
- **Then:** Available for Insights/upstream use

**Benefits:**
- Semantic layer enables cross-file reasoning
- Embeddings enable similarity matching
- Semantic graph enables relationship reasoning
- Arango becomes the semantic data store

---

## Implementation Changes Required

### 1. Update ContentAnalysisOrchestrator Flow

**Current Flow:**
```python
async def parse_file(self, file_id: str, ...):
    # Parse file
    result = await file_parser.parse_file(file_id, ...)
    # Return parsed result
    return result
```

**New Flow:**
```python
async def parse_file(self, file_id: str, ...):
    # Step 1: Parse file
    parse_result = await file_parser.parse_file(file_id, ...)
    
    # Step 2: Detect data type (structured vs unstructured)
    data_type = await self._detect_data_type(parse_result)
    
    # Step 3: Route to semantic processing
    if data_type == "structured":
        semantic_result = await self._process_structured_semantic(parse_result, ...)
    elif data_type == "unstructured":
        semantic_result = await self._process_unstructured_semantic(parse_result, ...)
    
    # Step 4: Store in Arango
    await self._store_in_arango(semantic_result, data_type, ...)
    
    # Step 5: Return for display (read-only for MVP)
    return {
        "parse_result": parse_result,
        "semantic_result": semantic_result,
        "data_type": data_type,
        "display_mode": "read_only"  # MVP: no validation UI
    }
```

### 2. Create Structured Semantic Processing

**New Method in ContentAnalysisOrchestrator:**

```python
async def _process_structured_semantic(
    self,
    parse_result: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process structured data to create embeddings and semantic layer.
    
    Flow:
    1. Profile columns → Profiling Agent
    2. Infer meanings → Column Meaning Agent → HF Inference Agent
    3. Match to semantic IDs → Semantic Matching Agent → HF Inference Agent
    4. Create embeddings → HF Inference Agent
    5. Store in Arango
    """
    try:
        # Step 1: Profile columns (deterministic)
        profiling_agent = await self.get_agent("ProfilingAgent")
        column_docs = await profiling_agent.profile_columns(
            parsed_data=parse_result,
            user_context=user_context
        )
        
        # Step 2: Infer column meanings (uses HF Inference Agent)
        column_meaning_agent = await self.get_agent("ColumnMeaningAgent")
        column_meanings = await column_meaning_agent.infer_column_meanings(
            column_docs=column_docs,
            user_context=user_context
        )
        
        # Step 3: Match to semantic IDs (uses HF Inference Agent)
        semantic_matching_agent = await self.get_agent("SemanticMatchingAgent")
        semantic_matches = await semantic_matching_agent.match_to_semantic_ids(
            column_meanings=column_meanings,
            user_context=user_context
        )
        
        # Step 4: Create embeddings (uses HF Inference Agent)
        hf_inference_agent = await self.get_agent("StatelessHFInferenceAgent")
        
        embeddings = []
        for match in semantic_matches:
            column_name = match.get("column_name")
            meaning = match.get("meaning")
            semantic_id = match.get("top_candidate", {}).get("semantic_id")
            
            # Create 3 embeddings
            # 1. Column metadata embedding
            metadata_embedding = await hf_inference_agent.generate_embedding(
                text=f"{column_name} {meaning}",
                user_context=user_context
            )
            
            # 2. Semantic meaning embedding
            meaning_embedding = await hf_inference_agent.generate_embedding(
                text=meaning,
                user_context=user_context
            )
            
            # 3. Sample values embedding (if available)
            sample_values = match.get("sample_values", [])
            if sample_values:
                samples_text = " ".join(str(v) for v in sample_values[:10])
                samples_embedding = await hf_inference_agent.generate_embedding(
                    text=samples_text,
                    user_context=user_context
                )
            else:
                samples_embedding = None
            
            embeddings.append({
                "column_name": column_name,
                "semantic_id": semantic_id,
                "metadata_embedding": metadata_embedding.get("embedding"),
                "meaning_embedding": meaning_embedding.get("embedding"),
                "samples_embedding": samples_embedding.get("embedding") if samples_embedding else None
            })
        
        # Step 5: Store in Arango via abstraction
        arango_result = await self._store_embeddings_in_arango(
            file_id=parse_result.get("file_id"),
            embeddings=embeddings,
            column_docs=column_docs,
            semantic_matches=semantic_matches,
            user_context=user_context
        )
        
        return {
            "success": True,
            "column_docs": column_docs,
            "column_meanings": column_meanings,
            "semantic_matches": semantic_matches,
            "embeddings": embeddings,
            "arango_storage": arango_result
        }
    
    except Exception as e:
        self.logger.error(f"❌ Structured semantic processing failed: {e}")
        import traceback
        self.logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }
```

### 3. Create Unstructured Semantic Processing

**New Method in ContentAnalysisOrchestrator:**

```python
async def _process_unstructured_semantic(
    self,
    parse_result: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process unstructured data to create semantic graph.
    
    Flow:
    1. NLP extraction → NLP Extraction Agent
    2. Normalize entities & relationships → Normalization Agent
    3. Create semantic graph → Semantic Graph Agent
    4. Match to semantic IDs → Semantic Matching Agent → HF Inference Agent
    5. Store in Arango
    """
    try:
        # Step 1: NLP extraction (uses LLM/NER models)
        nlp_extraction_agent = await self.get_agent("NLPExtractionAgent")
        extracted_entities = await nlp_extraction_agent.extract_entities(
            text_content=parse_result.get("text_content", ""),
            user_context=user_context
        )
        
        # Step 2: Extract relationships (uses LLM)
        relationship_agent = await self.get_agent("RelationshipExtractionAgent")
        relationships = await relationship_agent.extract_relationships(
            entities=extracted_entities,
            text_content=parse_result.get("text_content", ""),
            user_context=user_context
        )
        
        # Step 3: Normalize entities & relationships
        normalization_agent = await self.get_agent("EntityNormalizationAgent")
        normalized_entities = await normalization_agent.normalize_entities(
            entities=extracted_entities,
            user_context=user_context
        )
        
        # Step 4: Match to semantic IDs (uses HF Inference Agent)
        semantic_matching_agent = await self.get_agent("SemanticMatchingAgent")
        
        semantic_graph_nodes = []
        for entity in normalized_entities:
            # Generate embedding for entity
            hf_inference_agent = await self.get_agent("StatelessHFInferenceAgent")
            entity_embedding = await hf_inference_agent.generate_embedding(
                text=entity.get("text", ""),
                user_context=user_context
            )
            
            # Find semantic ID candidates
            candidates = await semantic_matching_agent.find_semantic_id_candidates(
                column_meaning=entity.get("text", ""),
                embedding=entity_embedding.get("embedding"),
                user_context=user_context
            )
            
            semantic_graph_nodes.append({
                "entity_id": entity.get("entity_id"),
                "entity_text": entity.get("text"),
                "entity_type": entity.get("type"),
                "semantic_id": candidates.get("candidates", [{}])[0].get("semantic_id") if candidates.get("candidates") else None,
                "embedding": entity_embedding.get("embedding"),
                "confidence": candidates.get("candidates", [{}])[0].get("confidence", 0.0) if candidates.get("candidates") else 0.0
            })
        
        # Step 5: Create semantic graph edges (relationships)
        semantic_graph_edges = []
        for relationship in relationships:
            semantic_graph_edges.append({
                "source_entity_id": relationship.get("source_entity_id"),
                "target_entity_id": relationship.get("target_entity_id"),
                "relationship_type": relationship.get("type"),
                "confidence": relationship.get("confidence", 0.0)
            })
        
        # Step 6: Store in Arango via abstraction
        arango_result = await self._store_semantic_graph_in_arango(
            file_id=parse_result.get("file_id"),
            nodes=semantic_graph_nodes,
            edges=semantic_graph_edges,
            user_context=user_context
        )
        
        return {
            "success": True,
            "extracted_entities": extracted_entities,
            "relationships": relationships,
            "normalized_entities": normalized_entities,
            "semantic_graph": {
                "nodes": semantic_graph_nodes,
                "edges": semantic_graph_edges
            },
            "arango_storage": arango_result
        }
    
    except Exception as e:
        self.logger.error(f"❌ Unstructured semantic processing failed: {e}")
        import traceback
        self.logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }
```

### 4. Create Arango Storage Methods

**New Methods in ContentAnalysisOrchestrator:**

```python
async def _store_embeddings_in_arango(
    self,
    file_id: str,
    embeddings: List[Dict[str, Any]],
    column_docs: List[Dict[str, Any]],
    semantic_matches: List[Dict[str, Any]],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Store structured data embeddings in Arango via abstraction.
    
    REAL implementation - uses Arango abstraction.
    """
    try:
        # Get Arango abstraction
        arango_adapter = await self.get_abstraction("ArangoAdapter")
        if not arango_adapter:
            return {
                "success": False,
                "error": "Arango adapter not available"
            }
        
        # Store embeddings in Arango
        # Collection: structured_embeddings
        # Document structure:
        # {
        #   "_key": f"{file_id}_{column_name}",
        #   "file_id": file_id,
        #   "column_name": column_name,
        #   "semantic_id": semantic_id,
        #   "metadata_embedding": [...],
        #   "meaning_embedding": [...],
        #   "samples_embedding": [...],
        #   "column_doc": {...},
        #   "semantic_match": {...},
        #   "tenant_id": user_context.get("tenant_id"),
        #   "created_at": datetime.utcnow().isoformat()
        # }
        
        stored_docs = []
        for embedding_data in embeddings:
            doc = {
                "_key": f"{file_id}_{embedding_data['column_name']}",
                "file_id": file_id,
                "column_name": embedding_data["column_name"],
                "semantic_id": embedding_data.get("semantic_id"),
                "metadata_embedding": embedding_data.get("metadata_embedding"),
                "meaning_embedding": embedding_data.get("meaning_embedding"),
                "samples_embedding": embedding_data.get("samples_embedding"),
                "tenant_id": user_context.get("tenant_id") if user_context else None,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in Arango (REAL implementation)
            result = await arango_adapter.store_document(
                collection="structured_embeddings",
                document=doc
            )
            
            if result.get("success"):
                stored_docs.append(doc)
        
        return {
            "success": True,
            "stored_count": len(stored_docs),
            "collection": "structured_embeddings"
        }
    
    except Exception as e:
        self.logger.error(f"❌ Store embeddings in Arango failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def _store_semantic_graph_in_arango(
    self,
    file_id: str,
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Store unstructured data semantic graph in Arango via abstraction.
    
    REAL implementation - uses Arango abstraction.
    """
    try:
        # Get Arango abstraction
        arango_adapter = await self.get_abstraction("ArangoAdapter")
        if not arango_adapter:
            return {
                "success": False,
                "error": "Arango adapter not available"
            }
        
        # Store nodes in Arango
        # Collection: semantic_graph_nodes
        stored_nodes = []
        for node in nodes:
            doc = {
                "_key": f"{file_id}_{node['entity_id']}",
                "file_id": file_id,
                "entity_id": node.get("entity_id"),
                "entity_text": node.get("entity_text"),
                "entity_type": node.get("entity_type"),
                "semantic_id": node.get("semantic_id"),
                "embedding": node.get("embedding"),
                "confidence": node.get("confidence"),
                "tenant_id": user_context.get("tenant_id") if user_context else None,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = await arango_adapter.store_document(
                collection="semantic_graph_nodes",
                document=doc
            )
            
            if result.get("success"):
                stored_nodes.append(doc)
        
        # Store edges in Arango
        # Collection: semantic_graph_edges
        stored_edges = []
        for edge in edges:
            doc = {
                "_key": f"{file_id}_{edge['source_entity_id']}_{edge['target_entity_id']}",
                "file_id": file_id,
                "source_entity_id": edge.get("source_entity_id"),
                "target_entity_id": edge.get("target_entity_id"),
                "relationship_type": edge.get("relationship_type"),
                "confidence": edge.get("confidence"),
                "tenant_id": user_context.get("tenant_id") if user_context else None,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = await arango_adapter.store_document(
                collection="semantic_graph_edges",
                document=doc
            )
            
            if result.get("success"):
                stored_edges.append(doc)
        
        return {
            "success": True,
            "stored_nodes_count": len(stored_nodes),
            "stored_edges_count": len(stored_edges),
            "collections": ["semantic_graph_nodes", "semantic_graph_edges"]
        }
    
    except Exception as e:
        self.logger.error(f"❌ Store semantic graph in Arango failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

### 5. Update Parsing Output Format

**Current:** Returns parquet/JSON (complex formats)

**New:** May need simpler formats for embedding agents (JSON, Pandas dataframe, etc.)

**Consideration:** Embedding agents may need specific input formats. We should:
1. Keep current formats (parquet/JSON) for backward compatibility
2. Add option to return simpler formats for embedding agents
3. Document which formats embedding agents accept

---

## New Agents Required

### For Structured Path

1. **ProfilingAgent** (deterministic)
   - Profiles columns from parsed data
   - Generates ColumnDocs (structure + examples + stats)

2. **ColumnMeaningAgent** (uses HF Inference Agent)
   - Infers semantic meaning of columns
   - Calls Stateless HF Inference Agent via MCP tools

3. **SemanticMatchingAgent** (uses HF Inference Agent)
   - Matches columns to semantic IDs
   - Uses embedding comparison via HF Inference Agent

### For Unstructured Path

1. **NLPExtractionAgent** (uses LLM/NER models)
   - Extracts entities from text
   - Uses LLM or NER models

2. **RelationshipExtractionAgent** (uses LLM)
   - Extracts relationships between entities
   - Uses LLM for relationship inference

3. **EntityNormalizationAgent** (uses HF Inference Agent)
   - Normalizes entities to standard forms
   - Uses HF Inference Agent for semantic matching

4. **SemanticGraphAgent** (orchestrates graph creation)
   - Creates semantic graph from entities and relationships
   - Coordinates with Semantic Matching Agent

---

## Integration with Insights Pillar

### Current: Insights Uses Parsed Files

```python
# Insights queries parsed files directly
parsed_data = await content_orchestrator.get_file_details(file_id)
# Analyze parsed data
insights = await insights_orchestrator.analyze_data(parsed_data)
```

### New: Insights Uses Arango (Semantic Layer)

**Structured Data:**
```python
# Insights queries Arango for embeddings
arango_adapter = await self.get_abstraction("ArangoAdapter")
embeddings = await arango_adapter.query(
    collection="structured_embeddings",
    filters={"file_id": file_id}
)

# Use embeddings for similarity matching, cross-file reasoning
similar_columns = await self._find_similar_columns(embeddings)
insights = await self._analyze_with_semantic_context(embeddings, similar_columns)
```

**Unstructured Data:**
```python
# Insights queries Arango for semantic graph
arango_adapter = await self.get_abstraction("ArangoAdapter")
graph = await arango_adapter.query_graph(
    nodes_collection="semantic_graph_nodes",
    edges_collection="semantic_graph_edges",
    filters={"file_id": file_id}
)

# Use graph for relationship reasoning, entity analysis
insights = await self._analyze_with_graph_context(graph)
```

---

## UI/UX Changes Required (MVP: Read-Only Display)

### Step 5: Display Parsed Output (Read-Only)

**Existing UI Component:** `ParsePreview.tsx` (already exists)

**Enhancement:** 
- Show parsed data preview (already works)
- Add note: "Parsed data validated" (for demo voice over)
- No actual validation UI needed for MVP

### Step S7: Display Semantic Extraction Layer (Read-Only)

**New UI Component:** `SemanticExtractionLayerDisplay.tsx`

**Features (Read-Only for MVP):**
- Show column metadata
- Show semantic meaning (from Column Meaning Agent)
- Show candidate semantic IDs (from Semantic Matching Agent)
- Display embeddings info (count, dimensions)
- **No edit/validation UI** (voice over: "Users can validate/correct these mappings")

**Display Format:**
```tsx
<div className="semantic-extraction-layer">
  <h3>Semantic Extraction Layer</h3>
  {columns.map(column => (
    <div key={column.name}>
      <div>Column: {column.name}</div>
      <div>Semantic Meaning: {column.meaning}</div>
      <div>Semantic ID: {column.semantic_id}</div>
      <div>Confidence: {column.confidence}</div>
      {/* Read-only display */}
    </div>
  ))}
  <div className="demo-note">
    [Voice over: "Users can validate and correct these mappings"]
  </div>
</div>
```

### Step U7: Display Semantic Graph (Read-Only)

**New UI Component:** `SemanticGraphDisplay.tsx`

**Features (Read-Only for MVP):**
- Show semantic graph visualization (nodes + edges)
- Show entities (nodes) with semantic IDs
- Show relationships (edges) with types
- Display confidence scores
- **No edit/validation UI** (voice over: "Users can validate/correct the graph")

**Display Format:**
```tsx
<div className="semantic-graph">
  <h3>Semantic Graph</h3>
  <GraphVisualization 
    nodes={semantic_graph.nodes}
    edges={semantic_graph.edges}
    readOnly={true}  // MVP: no editing
  />
  <div className="demo-note">
    [Voice over: "Users can validate and correct the graph"]
  </div>
</div>
```

---

## Implementation Checklist

### Phase 1: Core Flow Changes
- [ ] Update `parse_file()` to detect data type
- [ ] Add `_detect_data_type()` method
- [ ] Add `_process_structured_semantic()` method
- [ ] Add `_process_unstructured_semantic()` method
- [ ] Add `_store_embeddings_in_arango()` method
- [ ] Add `_store_semantic_graph_in_arango()` method
- [ ] Test end-to-end flow

### Phase 2: Agent Integration
- [ ] Create ProfilingAgent (deterministic)
- [ ] Create ColumnMeaningAgent (uses HF Inference Agent)
- [ ] Create SemanticMatchingAgent (uses HF Inference Agent)
- [ ] Create NLPExtractionAgent (uses LLM/NER)
- [ ] Create RelationshipExtractionAgent (uses LLM)
- [ ] Create EntityNormalizationAgent (uses HF Inference Agent)
- [ ] Test agent → agent flow

### Phase 3: Arango Integration
- [ ] Create ArangoAdapter abstraction (if doesn't exist)
- [ ] Implement `store_document()` method
- [ ] Implement `query()` method
- [ ] Implement `query_graph()` method
- [ ] Test Arango storage and retrieval

### Phase 4: Insights Integration
- [ ] Update InsightsOrchestrator to query Arango
- [ ] Add `_find_similar_columns()` method (using embeddings)
- [ ] Add `_analyze_with_semantic_context()` method
- [ ] Add `_analyze_with_graph_context()` method
- [ ] Test Insights with Arango data

### Phase 5: UI/UX (Read-Only Display for MVP)
- [ ] Enhance existing ParsePreview component (add semantic layer display)
- [ ] Create SemanticExtractionLayerDisplay component (read-only)
- [ ] Create SemanticGraphDisplay component (read-only)
- [ ] Add demo voice-over notes
- [ ] Test display flows

**Note:** Validation UI components deferred to post-MVP (when customers start paying)

---

## Key Principles

1. **Parsing is Step 1, Not the End:** Semantic processing is the real value
2. **Bifurcation by Data Type:** Structured vs unstructured get different treatment
3. **Arango is the Semantic Store:** All semantic data goes to Arango
4. **Display for Demo:** Read-only display with voice-over for validation (MVP)
5. **Insights Uses Arango:** Not just parsed files, but semantic layer
6. **Real Implementation:** No mocks, no placeholders, real Arango storage

---

## MVP Simplifications

### What We're NOT Building (Deferred to Post-MVP)

1. **Validation UI Components:**
   - Accept/reject semantic ID buttons
   - Edit semantic meaning inputs
   - Create new semantic ID forms
   - HITL review workflows

2. **Interactive Graph Editing:**
   - Add/remove entity nodes
   - Add/remove relationship edges
   - Edit entity properties
   - Edit relationship types

3. **Validation State Management:**
   - Track validation status
   - Store user corrections
   - Update semantic layer based on corrections

### What We ARE Building (MVP)

1. **Semantic Processing:**
   - Full semantic inference pipeline
   - Embedding generation
   - Semantic graph creation
   - Arango storage

2. **Read-Only Display:**
   - Show parsed output
   - Show semantic extraction layer
   - Show semantic graph
   - Display confidence scores

3. **Voice-Over Notes:**
   - Document what validation will look like
   - Prepare demo script
   - Highlight value proposition

---

## Summary

**Evolution:**
- **Before:** Parse → Return → Done
- **After:** Parse → Semantic Processing → Arango Storage → Display → Available for Insights

**Key Changes:**
1. Add semantic processing after parsing
2. Store in Arango (embeddings or semantic graph)
3. Display for viewing (read-only for MVP)
4. Insights uses Arango, not just parsed files

**MVP Simplification:**
- No validation UI (deferred to post-MVP)
- Read-only display with voice-over
- Full semantic processing still happens
- Arango storage still happens

**This is a much cleaner and better aligned version that enables the semantic platform vision while keeping MVP scope manageable.**

