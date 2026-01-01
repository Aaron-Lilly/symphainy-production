# Content Pillar E2E Implementation Plan: Semantic Platform Flow

## Executive Summary

This document provides a detailed implementation plan for evolving the Content Pillar to support the new semantic platform flow: Parse → Semantic Processing → Arango Storage → Display → Insights Integration.

**MVP Scope:** Read-only display (validation UI deferred to post-MVP)

---

## Phase 1: Backend Core Flow Changes

### 1.1 Update ContentAnalysisOrchestrator.parse_file()

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/content_analysis_orchestrator.py`

**Changes:**

```python
async def parse_file(
    self,
    file_id: str,
    parse_options: Optional[Dict[str, Any]] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Parse file and process semantically (NEW FLOW).
    
    Flow:
    1. Parse file → parquet/JSON
    2. Detect data type (structured vs unstructured)
    3. Process semantically (embeddings or graph)
    4. Store in Arango
    5. Return for display
    """
    # ... existing security/tenant validation ...
    
    # Step 1: Parse file (existing)
    parse_result = await file_parser.parse_file(file_id, parse_options, user_context)
    
    if not parse_result.get("success"):
        return parse_result
    
    # Step 2: Detect data type
    data_type = await self._detect_data_type(parse_result)
    
    # Step 3: Process semantically
    semantic_result = None
    if data_type == "structured":
        semantic_result = await self._process_structured_semantic(
            parse_result, user_context
        )
    elif data_type == "unstructured":
        semantic_result = await self._process_unstructured_semantic(
            parse_result, user_context
        )
    
    # Step 4: Store in Arango (if semantic processing succeeded)
    if semantic_result and semantic_result.get("success"):
        await self._store_semantic_data_in_arango(
            file_id=file_id,
            semantic_result=semantic_result,
            data_type=data_type,
            user_context=user_context
        )
    
    # Step 5: Return for display
    return {
        "success": True,
        "parse_result": parse_result,
        "semantic_result": semantic_result,
        "data_type": data_type,
        "display_mode": "read_only"  # MVP: no validation UI
    }
```

### 1.2 Add Data Type Detection

**New Method:**

```python
async def _detect_data_type(
    self,
    parse_result: Dict[str, Any]
) -> str:
    """
    Detect if data is structured or unstructured.
    
    Rule-based detection:
    - Has tables/records → structured
    - Has text_content only → unstructured
    - Has both → check ratio
    """
    tables = parse_result.get("tables", [])
    records = parse_result.get("records", [])
    text_content = parse_result.get("text_content", "")
    
    # If has structured data, likely structured
    if tables or records:
        return "structured"
    
    # If only text, likely unstructured
    if text_content and not tables and not records:
        return "unstructured"
    
    # Default to structured if ambiguous
    return "structured"
```

### 1.3 Add Structured Semantic Processing

**New Method:**

```python
async def _process_structured_semantic(
    self,
    parse_result: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process structured data: Profile → Meaning → Matching → Embeddings.
    
    Uses:
    - ProfilingAgent (deterministic)
    - ColumnMeaningAgent → StatelessHFInferenceAgent
    - SemanticMatchingAgent → StatelessHFInferenceAgent
    """
    try:
        # Step 1: Profile columns
        profiling_agent = await self.get_agent("ProfilingAgent")
        column_docs = await profiling_agent.profile_columns(
            parsed_data=parse_result,
            user_context=user_context
        )
        
        # Step 2: Infer meanings
        column_meaning_agent = await self.get_agent("ColumnMeaningAgent")
        column_meanings = await column_meaning_agent.infer_column_meanings(
            column_docs=column_docs,
            user_context=user_context
        )
        
        # Step 3: Match to semantic IDs
        semantic_matching_agent = await self.get_agent("SemanticMatchingAgent")
        semantic_matches = await semantic_matching_agent.match_to_semantic_ids(
            column_meanings=column_meanings,
            user_context=user_context
        )
        
        # Step 4: Create 3 embeddings per column
        hf_inference_agent = await self.get_agent("StatelessHFInferenceAgent")
        embeddings = []
        
        for match in semantic_matches.get("matches", []):
            column_name = match.get("column_name")
            meaning = match.get("meaning")
            
            # Get embeddings via MCP tool
            metadata_embedding = await self._call_hf_inference_tool(
                "generate_embedding_tool",
                {"text": f"{column_name} {meaning}"},
                user_context
            )
            
            meaning_embedding = await self._call_hf_inference_tool(
                "generate_embedding_tool",
                {"text": meaning},
                user_context
            )
            
            # Sample values embedding (if available)
            samples_embedding = None
            sample_values = match.get("sample_values", [])
            if sample_values:
                samples_text = " ".join(str(v) for v in sample_values[:10])
                samples_embedding = await self._call_hf_inference_tool(
                    "generate_embedding_tool",
                    {"text": samples_text},
                    user_context
                )
            
            embeddings.append({
                "column_name": column_name,
                "semantic_id": match.get("top_candidate", {}).get("semantic_id"),
                "metadata_embedding": metadata_embedding.get("embedding"),
                "meaning_embedding": meaning_embedding.get("embedding"),
                "samples_embedding": samples_embedding.get("embedding") if samples_embedding else None
            })
        
        return {
            "success": True,
            "column_docs": column_docs,
            "column_meanings": column_meanings,
            "semantic_matches": semantic_matches,
            "embeddings": embeddings
        }
    
    except Exception as e:
        self.logger.error(f"❌ Structured semantic processing failed: {e}")
        return {"success": False, "error": str(e)}
```

### 1.4 Add Unstructured Semantic Processing

**New Method:**

```python
async def _process_unstructured_semantic(
    self,
    parse_result: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process unstructured data: NLP → Relationships → Graph.
    
    Uses:
    - NLPExtractionAgent (LLM/NER)
    - RelationshipExtractionAgent (LLM)
    - EntityNormalizationAgent
    - SemanticMatchingAgent → StatelessHFInferenceAgent
    """
    try:
        text_content = parse_result.get("text_content", "")
        
        # Step 1: Extract entities
        nlp_agent = await self.get_agent("NLPExtractionAgent")
        entities = await nlp_agent.extract_entities(
            text_content=text_content,
            user_context=user_context
        )
        
        # Step 2: Extract relationships
        relationship_agent = await self.get_agent("RelationshipExtractionAgent")
        relationships = await relationship_agent.extract_relationships(
            entities=entities,
            text_content=text_content,
            user_context=user_context
        )
        
        # Step 3: Normalize entities
        normalization_agent = await self.get_agent("EntityNormalizationAgent")
        normalized_entities = await normalization_agent.normalize_entities(
            entities=entities,
            user_context=user_context
        )
        
        # Step 4: Match to semantic IDs and create graph
        semantic_matching_agent = await self.get_agent("SemanticMatchingAgent")
        hf_inference_agent = await self.get_agent("StatelessHFInferenceAgent")
        
        nodes = []
        for entity in normalized_entities:
            # Generate embedding
            embedding_result = await self._call_hf_inference_tool(
                "generate_embedding_tool",
                {"text": entity.get("text", "")},
                user_context
            )
            
            # Find semantic ID candidates
            candidates_result = await self._call_hf_inference_tool(
                "find_semantic_id_candidates_tool",
                {
                    "column_meaning": entity.get("text", ""),
                    "embedding": embedding_result.get("embedding")
                },
                user_context
            )
            
            nodes.append({
                "entity_id": entity.get("entity_id"),
                "entity_text": entity.get("text"),
                "entity_type": entity.get("type"),
                "semantic_id": candidates_result.get("candidates", [{}])[0].get("semantic_id") if candidates_result.get("candidates") else None,
                "embedding": embedding_result.get("embedding"),
                "confidence": candidates_result.get("candidates", [{}])[0].get("confidence", 0.0) if candidates_result.get("candidates") else 0.0
            })
        
        # Create edges
        edges = []
        for rel in relationships:
            edges.append({
                "source_entity_id": rel.get("source_entity_id"),
                "target_entity_id": rel.get("target_entity_id"),
                "relationship_type": rel.get("type"),
                "confidence": rel.get("confidence", 0.0)
            })
        
        return {
            "success": True,
            "semantic_graph": {
                "nodes": nodes,
                "edges": edges
            }
        }
    
    except Exception as e:
        self.logger.error(f"❌ Unstructured semantic processing failed: {e}")
        return {"success": False, "error": str(e)}
```

### 1.5 Add Arango Storage

**New Method:**

```python
async def _store_semantic_data_in_arango(
    self,
    file_id: str,
    semantic_result: Dict[str, Any],
    data_type: str,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Store semantic data in Arango via abstraction."""
    try:
        arango_adapter = await self.get_abstraction("ArangoAdapter")
        if not arango_adapter:
            return {"success": False, "error": "Arango adapter not available"}
        
        if data_type == "structured":
            # Store embeddings
            for emb in semantic_result.get("embeddings", []):
                doc = {
                    "_key": f"{file_id}_{emb['column_name']}",
                    "file_id": file_id,
                    "column_name": emb["column_name"],
                    "semantic_id": emb.get("semantic_id"),
                    "metadata_embedding": emb.get("metadata_embedding"),
                    "meaning_embedding": emb.get("meaning_embedding"),
                    "samples_embedding": emb.get("samples_embedding"),
                    "tenant_id": user_context.get("tenant_id") if user_context else None,
                    "created_at": datetime.utcnow().isoformat()
                }
                await arango_adapter.create_document("structured_embeddings", doc)
        
        elif data_type == "unstructured":
            # Store graph nodes
            for node in semantic_result.get("semantic_graph", {}).get("nodes", []):
                doc = {
                    "_key": f"{file_id}_{node['entity_id']}",
                    "file_id": file_id,
                    **node,
                    "tenant_id": user_context.get("tenant_id") if user_context else None,
                    "created_at": datetime.utcnow().isoformat()
                }
                await arango_adapter.create_document("semantic_graph_nodes", doc)
            
            # Store graph edges
            for edge in semantic_result.get("semantic_graph", {}).get("edges", []):
                doc = {
                    "_key": f"{file_id}_{edge['source_entity_id']}_{edge['target_entity_id']}",
                    "file_id": file_id,
                    **edge,
                    "tenant_id": user_context.get("tenant_id") if user_context else None,
                    "created_at": datetime.utcnow().isoformat()
                }
                await arango_adapter.create_document("semantic_graph_edges", doc)
        
        return {"success": True}
    
    except Exception as e:
        self.logger.error(f"❌ Arango storage failed: {e}")
        return {"success": False, "error": str(e)}
```

### 1.6 Helper: Call HF Inference Tool

**New Method:**

```python
async def _call_hf_inference_tool(
    self,
    tool_name: str,
    parameters: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Call HF Inference Agent via MCP tool."""
    try:
        # Get Semantic Inference Orchestrator's MCP server
        # (We'll create this orchestrator in Phase 2)
        # For now, get HF Inference Agent directly
        hf_agent = await self.get_agent("StatelessHFInferenceAgent")
        if not hf_agent:
            return {"success": False, "error": "HF Inference Agent not available"}
        
        # Call agent method directly (or via MCP tool if available)
        if tool_name == "generate_embedding_tool":
            return await hf_agent.generate_embedding(
                text=parameters.get("text"),
                user_context=user_context
            )
        elif tool_name == "find_semantic_id_candidates_tool":
            return await hf_agent.find_semantic_id_candidates(
                column_meaning=parameters.get("column_meaning"),
                embedding=parameters.get("embedding"),
                user_context=user_context
            )
        
        return {"success": False, "error": f"Unknown tool: {tool_name}"}
    
    except Exception as e:
        self.logger.error(f"❌ HF inference tool call failed: {e}")
        return {"success": False, "error": str(e)}
```

---

## Phase 2: Create New Agents

### 2.1 StatelessHFInferenceAgent

**File:** `backend/business_enablement/agents/stateless_hf_inference_agent.py`

**Configuration:** `backend/business_enablement/agents/configs/stateless_hf_inference_agent.yaml`

**Recommended HF Models:**
- **Semantic Meaning:** `sentence-transformers/all-MiniLM-L6-v2` (embeddings)
- **Text Embeddings:** `sentence-transformers/all-mpnet-base-v2` (higher quality)
- **NER/Entity Extraction:** `dslim/bert-base-NER` (for NLP extraction)

**Implementation:**

```python
class StatelessHFInferenceAgent(DeclarativeAgentBase):
    """Stateless HF Inference Agent - wraps HuggingFace model endpoints."""
    
    def __init__(self, ...):
        super().__init__(...)
        self.hf_endpoint = None  # From config
        self.hf_api_key = None   # From environment
    
    async def generate_embedding(
        self,
        text: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate embedding using HF model."""
        # Get HuggingFace adapter
        hf_adapter = await self.get_abstraction("HuggingFaceAdapter")
        if not hf_adapter:
            raise ValueError("HuggingFace adapter not available")
        
        # Call HF endpoint
        response = await hf_adapter.inference(
            endpoint="embeddings",
            model="sentence-transformers/all-mpnet-base-v2",
            text=text
        )
        
        return {
            "embedding": response.get("embedding"),
            "model": "all-mpnet-base-v2",
            "dimension": len(response.get("embedding", []))
        }
    
    async def infer_column_meaning(
        self,
        column_metadata: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Infer semantic meaning of column."""
        # Build prompt
        prompt = f"Column name: {column_metadata.get('name')}\n"
        prompt += f"Type: {column_metadata.get('type')}\n"
        prompt += f"Samples: {column_metadata.get('samples', [])[:5]}\n"
        prompt += "What is the semantic meaning of this column?"
        
        # Call HF model (or LLM for meaning inference)
        # For MVP, could use LLM abstraction instead
        # HF models are better for embeddings, LLM for meaning
        
        return {
            "meaning": "inferred meaning",  # From LLM or HF model
            "confidence": 0.85
        }
```

### 2.2 ProfilingAgent

**File:** `backend/business_enablement/agents/profiling_agent.py`

**Purpose:** Deterministic column profiling (no LLM)

**Implementation:**

```python
class ProfilingAgent(DeclarativeAgentBase):
    """Profiling Agent - generates ColumnDocs (deterministic)."""
    
    async def profile_columns(
        self,
        parsed_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Profile columns from parsed data."""
        tables = parsed_data.get("tables", [])
        records = parsed_data.get("records", [])
        
        column_docs = []
        
        # Extract columns from tables or records
        if tables:
            for table in tables:
                columns = table.get("columns", [])
                for col in columns:
                    column_docs.append({
                        "name": col.get("name"),
                        "type": col.get("type"),
                        "position": col.get("position"),
                        "samples": col.get("samples", [])[:10],
                        "stats": {
                            "null_count": col.get("null_count", 0),
                            "unique_count": col.get("unique_count", 0),
                            "min": col.get("min"),
                            "max": col.get("max")
                        }
                    })
        
        return {
            "success": True,
            "column_docs": column_docs
        }
```

### 2.3 ColumnMeaningAgent

**File:** `backend/business_enablement/agents/column_meaning_agent.py`

**Uses:** StatelessHFInferenceAgent (via MCP tools)

### 2.4 SemanticMatchingAgent

**File:** `backend/business_enablement/agents/semantic_matching_agent.py`

**Uses:** StatelessHFInferenceAgent (via MCP tools)

### 2.5 NLPExtractionAgent

**File:** `backend/business_enablement/agents/nlp_extraction_agent.py`

**Uses:** LLM or NER models for entity extraction

### 2.6 RelationshipExtractionAgent

**File:** `backend/business_enablement/agents/relationship_extraction_agent.py`

**Uses:** LLM for relationship inference

### 2.7 EntityNormalizationAgent

**File:** `backend/business_enablement/agents/entity_normalization_agent.py`

**Uses:** StatelessHFInferenceAgent for semantic matching

---

## Phase 3: Create Arango Abstraction

### 3.1 Create ArangoAdapter Abstraction

**File:** `foundations/public_works_foundation/infrastructure_abstractions/arango_abstraction.py`

**Purpose:** Expose ArangoDBAdapter via Platform Gateway

**Implementation:**

```python
class ArangoAbstraction:
    """Arango abstraction - exposes ArangoDBAdapter."""
    
    def __init__(self, arango_adapter: ArangoDBAdapter):
        self.adapter = arango_adapter
    
    async def store_document(
        self,
        collection: str,
        document: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store document in Arango."""
        result = await self.adapter.create_document(collection, document)
        return {"success": True, "result": result}
    
    async def query(
        self,
        collection: str,
        filters: Dict[str, Any] = None,
        limit: int = None
    ) -> Dict[str, Any]:
        """Query documents."""
        results = await self.adapter.find_documents(
            collection, filters, limit=limit
        )
        return {"success": True, "results": results}
```

### 3.2 Register in Public Works Foundation

**File:** `foundations/public_works_foundation/public_works_foundation_service.py`

**Changes:**

```python
# In _create_all_abstractions()
from .infrastructure_abstractions.arango_abstraction import ArangoAbstraction

arango_abstraction = ArangoAbstraction(self.arango_adapter)
self.abstractions["ArangoAdapter"] = arango_abstraction
```

### 3.3 Register in Platform Gateway

**File:** `foundations/platform_gateway/platform_gateway_service.py`

**Changes:**

```python
# Add to REALM_ABSTRACTION_MAPPINGS
"business_enablement": {
    # ... existing mappings ...
    "ArangoAdapter": "arango_adapter"
}
```

---

## Phase 4: Create HuggingFace Adapter

### 4.1 Create HuggingFaceAdapter

**File:** `foundations/public_works_foundation/infrastructure_adapters/huggingface_adapter.py`

**Implementation:**

```python
class HuggingFaceAdapter:
    """HuggingFace model endpoint adapter."""
    
    def __init__(self, endpoint_url: str, api_key: str):
        self.endpoint_url = endpoint_url
        self.api_key = api_key
    
    async def inference(
        self,
        endpoint: str,  # "embeddings", "inference"
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Call HF model endpoint."""
        import httpx
        
        url = f"{self.endpoint_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        payload = {
            "model": model,
            **kwargs
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
```

### 4.2 Register in Public Works Foundation

**Similar to ArangoAdapter registration**

---

## Phase 5: Frontend Changes

### 5.1 Update ParsePreview Component

**File:** `frontend/components/content/ParsePreview.tsx`

**Changes:**

```tsx
// Add semantic layer display after parsing
{parseResult && parseResult.semantic_result && (
  <div className="mt-6">
    {parseResult.data_type === "structured" ? (
      <SemanticExtractionLayerDisplay 
        data={parseResult.semantic_result}
        readOnly={true}  // MVP: no validation
      />
    ) : (
      <SemanticGraphDisplay 
        data={parseResult.semantic_result.semantic_graph}
        readOnly={true}  // MVP: no validation
      />
    )}
  </div>
)}
```

### 5.2 Create SemanticExtractionLayerDisplay Component

**File:** `frontend/components/content/SemanticExtractionLayerDisplay.tsx`

**Implementation:**

```tsx
export default function SemanticExtractionLayerDisplay({ data, readOnly }) {
  return (
    <div className="semantic-extraction-layer">
      <h3>Semantic Extraction Layer</h3>
      {data.column_meanings?.map(column => (
        <div key={column.column_name} className="column-info">
          <div>Column: {column.column_name}</div>
          <div>Meaning: {column.meaning}</div>
          <div>Semantic ID: {column.semantic_id}</div>
          <div>Confidence: {column.confidence}</div>
        </div>
      ))}
      {readOnly && (
        <div className="demo-note">
          [Voice over: "Users can validate and correct these mappings"]
        </div>
      )}
    </div>
  );
}
```

### 5.3 Create SemanticGraphDisplay Component

**File:** `frontend/components/content/SemanticGraphDisplay.tsx`

**Implementation:**

```tsx
export default function SemanticGraphDisplay({ data, readOnly }) {
  return (
    <div className="semantic-graph">
      <h3>Semantic Graph</h3>
      <GraphVisualization 
        nodes={data.nodes}
        edges={data.edges}
        readOnly={readOnly}
      />
      {readOnly && (
        <div className="demo-note">
          [Voice over: "Users can validate and correct the graph"]
        </div>
      )}
    </div>
  );
}
```

---

## Phase 6: Parsing Adapter Output Format Changes

### 6.1 Ensure Simple Format Support

**Current:** Parsers return parquet/JSON (complex)

**Action:** Ensure parsers can also return simpler formats for embedding agents:
- JSON (simple dict/list)
- Pandas DataFrame (for structured)
- Plain text (for unstructured)

**File:** `backend/business_enablement/enabling_services/file_parser_service/file_parser_service.py`

**Changes:**

```python
async def parse_file(
    self,
    file_id: str,
    parse_options: Optional[Dict[str, Any]] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    # ... existing parsing ...
    
    # Ensure we return simple formats for embedding agents
    result = {
        "success": True,
        "file_id": file_id,
        "file_type": file_type,
        "text_content": result.text_content,  # For unstructured
        "tables": result.structured_data.get("tables", []),  # For structured
        "records": result.structured_data.get("records", []),  # For structured
        # ... existing fields ...
    }
    
    return result
```

**No major changes needed** - current format already supports both structured and unstructured.

---

## Phase 7: New Enabling Services

### 7.1 EmbeddingExtractionService (Optional)

**Purpose:** Pure service for embedding extraction (if we want to separate from agents)

**Decision:** Not needed - StatelessHFInferenceAgent handles this

### 7.2 SemanticGraphService (Optional)

**Purpose:** Pure service for graph operations

**Decision:** Not needed - agents handle graph creation, Arango stores it

---

## Implementation Checklist

### Backend
- [ ] Update `ContentAnalysisOrchestrator.parse_file()`
- [ ] Add `_detect_data_type()` method
- [ ] Add `_process_structured_semantic()` method
- [ ] Add `_process_unstructured_semantic()` method
- [ ] Add `_store_semantic_data_in_arango()` method
- [ ] Add `_call_hf_inference_tool()` helper
- [ ] Create StatelessHFInferenceAgent
- [ ] Create ProfilingAgent
- [ ] Create ColumnMeaningAgent
- [ ] Create SemanticMatchingAgent
- [ ] Create NLPExtractionAgent
- [ ] Create RelationshipExtractionAgent
- [ ] Create EntityNormalizationAgent
- [ ] Create ArangoAbstraction
- [ ] Register ArangoAbstraction in Public Works Foundation
- [ ] Register ArangoAbstraction in Platform Gateway
- [ ] Create HuggingFaceAdapter
- [ ] Register HuggingFaceAdapter in Public Works Foundation

### Frontend
- [ ] Update ParsePreview component
- [ ] Create SemanticExtractionLayerDisplay component
- [ ] Create SemanticGraphDisplay component
- [ ] Add demo voice-over notes

### Testing
- [ ] Test structured flow end-to-end
- [ ] Test unstructured flow end-to-end
- [ ] Test Arango storage
- [ ] Test frontend display

---

## HuggingFace Model Recommendations

### For Embeddings
- **Primary:** `sentence-transformers/all-mpnet-base-v2` (768-dim, high quality)
- **Fallback:** `sentence-transformers/all-MiniLM-L6-v2` (384-dim, faster)

### For Semantic Meaning Inference
- **Use LLM abstraction** (GPT-4, Claude, etc.) - HF models are better for embeddings, LLMs for meaning

### For NER/Entity Extraction
- **Primary:** `dslim/bert-base-NER` (for English)
- **Alternative:** `dbmdz/bert-large-cased-finetuned-conll03-english`

### For Relationship Extraction
- **Use LLM abstraction** - relationship extraction requires reasoning

---

## Summary

**Key Changes:**
1. Update `parse_file()` to add semantic processing
2. Create 7 new agents (HF Inference + 6 semantic agents)
3. Create ArangoAbstraction for storage
4. Create HuggingFaceAdapter for model calls
5. Update frontend to display semantic layer (read-only)

**No parsing adapter changes needed** - current format supports both structured and unstructured.

