# Hybrid Parsing Correlation Map: Assessment & Plan

**Date:** January 2025  
**Status:** 🔍 **ASSESSMENT COMPLETE** → 📋 **PLAN READY**

---

## Assessment: Does Correlation Map Exist?

### Current Implementation Analysis

**File:** `content_analysis_orchestrator.py`  
**Method:** `_process_hybrid_semantic()`

**Current Behavior:**
```python
async def _process_hybrid_semantic(self, parse_result, user_context):
    # Process structured component
    structured_result = await self._process_structured_semantic(...)
    
    # Process unstructured component
    unstructured_result = await self._process_unstructured_semantic(...)
    
    return {
        "success": True,
        "structured_result": structured_result,
        "unstructured_result": unstructured_result,
        "data_type": "hybrid"
        # ❌ NO CORRELATION MAP
    }
```

**Storage Behavior:**
```python
elif data_type == "hybrid":
    # Store structured embeddings
    await content_metadata_abstraction.store_semantic_embeddings(...)
    
    # Store unstructured semantic graph
    await content_metadata_abstraction.store_semantic_graph(...)
    
    # ❌ NO CORRELATION MAP STORED
```

### Finding: ❌ **Correlation Map Does NOT Exist**

**What's Missing:**
1. No detailed relationships between structured columns and unstructured entities
2. No correlation map explaining how parsed components relate
3. Only generic `"coexists_with"` relationship (if any)
4. No storage mechanism for correlation map

**Impact:**
- Cannot explain how structured data (tables) relates to unstructured data (text)
- Cannot query "which columns are discussed in which text sections"
- Cannot visualize relationships between structured and unstructured components
- Content Pillar cannot display correlation map

---

## Plan: Add Correlation Map

### Option 1: Add to Enabling Services Refactoring (Recommended)

**Rationale:**
- Enabling services team is already refactoring hybrid parsing
- Correlation map is part of semantic processing logic
- Natural fit for their work

**Assignment:**
- **Team:** Enabling Services Refactoring Team
- **Priority:** High (needed for Content Pillar MVP)
- **Timeline:** Phase 1 (Content + Insights Integration)

### Option 2: Add to DIL Foundation Phase 0

**Rationale:**
- DIL Foundation owns semantic data layer
- Correlation map is semantic metadata
- Could be part of DIL SDK semantic storage

**Assignment:**
- **Team:** DIL Foundation Team
- **Priority:** Medium (can be added later)
- **Timeline:** Phase 0.1 (Foundation Setup)

### Recommendation: **Option 1** (Enabling Services Team)

**Why:**
- Enabling services team is already working on hybrid parsing
- Correlation map generation is part of parsing/semantic processing logic
- Better separation of concerns (parsing logic in enabling services, storage in DIL)

---

## Correlation Map Specification

### Data Structure

```python
correlation_map = {
    "correlation_id": "corr_<uuid>",
    "file_id": "file_123",
    "content_id": "content_456",
    "structured_component_id": "structured_789",
    "unstructured_component_id": "unstructured_012",
    "relationships": [
        {
            "relationship_id": "rel_<uuid>",
            "source_type": "structured_column",  # or "structured_table", "structured_record"
            "source_id": "column:revenue",
            "source_metadata": {
                "column_name": "revenue",
                "table_name": "financial_data",
                "data_type": "numeric",
                "semantic_id": "revenue_metric_v1"
            },
            "target_type": "unstructured_entity",  # or "unstructured_chunk", "unstructured_relationship"
            "target_id": "entity:revenue_discussion",
            "target_metadata": {
                "entity_type": "discussion",
                "chunk_id": "chunk_abc",
                "entity_text": "The revenue discussion in Q4..."
            },
            "relationship_type": "discussed_in",  # or "referenced_by", "explained_in", "calculated_from"
            "confidence": 0.85,  # 0.0 to 1.0
            "evidence": "Column 'revenue' is discussed in text chunk 'chunk_abc'",
            "created_at": "2025-01-15T10:00:00Z"
        }
    ],
    "metadata": {
        "total_relationships": 15,
        "high_confidence_relationships": 12,
        "low_confidence_relationships": 3,
        "generation_method": "semantic_matching",  # or "llm_extraction", "rule_based"
        "generated_at": "2025-01-15T10:00:00Z"
    }
}
```

### Generation Strategy

**Method 1: Semantic Matching (Recommended for MVP)**
- Compare column embeddings with text chunk embeddings
- Find high-similarity matches
- Create relationships for matches above confidence threshold

**Method 2: LLM Extraction (Future Enhancement)**
- Use LLM to extract relationships from text
- Match extracted entities to structured columns
- Create relationships based on LLM output

**Method 3: Rule-Based (Fallback)**
- Use keyword matching
- Use column name matching in text
- Create relationships for matches

### Storage Strategy

**Via DIL SDK:**
```python
# Store correlation map via DIL SDK
await dil.data.store_correlation_map(
    file_id=file_id,
    correlation_map=correlation_map,
    user_context=user_context
)
```

**Storage Location:**
- ArangoDB collection: `correlation_maps`
- Indexed on: `file_id`, `content_id`, `structured_component_id`, `unstructured_component_id`
- Queryable via: `dil.data.query_correlation_map()`

---

## Implementation Requirements for Enabling Services Team

### 1. Update Hybrid Parsing Logic

**File:** `content_analysis_orchestrator.py`  
**Method:** `_process_hybrid_semantic()`

**Changes:**
```python
async def _process_hybrid_semantic(self, parse_result, user_context):
    # Process structured component
    structured_result = await self._process_structured_semantic(...)
    
    # Process unstructured component
    unstructured_result = await self._process_unstructured_semantic(...)
    
    # ✅ NEW: Generate correlation map
    correlation_map = await self._generate_correlation_map(
        structured_result=structured_result,
        unstructured_result=unstructured_result,
        parse_result=parse_result,
        user_context=user_context
    )
    
    return {
        "success": True,
        "structured_result": structured_result,
        "unstructured_result": unstructured_result,
        "correlation_map": correlation_map,  # ✅ NEW
        "data_type": "hybrid"
    }
```

### 2. Add Correlation Map Generation Method

**New Method:** `_generate_correlation_map()`

**Implementation:**
```python
async def _generate_correlation_map(
    self,
    structured_result: Dict[str, Any],
    unstructured_result: Dict[str, Any],
    parse_result: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate correlation map between structured and unstructured components.
    
    Strategy:
    1. Extract column embeddings from structured_result
    2. Extract text chunk embeddings from unstructured_result
    3. Compare embeddings (vector similarity)
    4. Create relationships for high-similarity matches
    5. Return correlation map
    """
    # Implementation details...
    pass
```

### 3. Store Correlation Map via DIL SDK

**Update:** `_store_semantic_via_content_metadata()`

**Changes:**
```python
elif data_type == "hybrid":
    # Store structured embeddings
    # Store unstructured semantic graph
    
    # ✅ NEW: Store correlation map
    if semantic_result.get("correlation_map"):
        await dil.data.store_correlation_map(
            file_id=file_id,
            correlation_map=semantic_result["correlation_map"],
            user_context=user_context
        )
```

### 4. DIL SDK Method (DIL Foundation Team)

**New Method:** `dil.data.store_correlation_map()`

**Implementation:**
```python
async def store_correlation_map(
    self,
    file_id: str,
    correlation_map: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Store correlation map in ArangoDB."""
    # Store in correlation_maps collection
    # Index on file_id, content_id, etc.
    pass
```

---

## Acceptance Criteria

### For Enabling Services Team:
- [ ] `_generate_correlation_map()` method implemented
- [ ] Correlation map generated for hybrid parsing
- [ ] Correlation map included in semantic_result
- [ ] Correlation map stored via DIL SDK
- [ ] Unit tests for correlation map generation
- [ ] Integration tests for hybrid parsing with correlation map

### For DIL Foundation Team:
- [ ] `dil.data.store_correlation_map()` method implemented
- [ ] `dil.data.query_correlation_map()` method implemented
- [ ] ArangoDB collection `correlation_maps` created
- [ ] Indexes created on correlation_maps collection
- [ ] Correlation map queryable via DIL SDK

### For Content Pillar:
- [ ] Correlation map displayed in UI
- [ ] Relationships visualized between structured and unstructured components
- [ ] Users can explore correlations interactively

---

## Timeline

**Phase 1 (Content + Insights Integration):**
- Week 3: Enabling services team implements correlation map generation
- Week 4: DIL Foundation team implements correlation map storage
- Week 4: Content Pillar displays correlation map

---

## Next Steps

1. **Assign to Enabling Services Team** (Option 1 recommended)
2. **Provide correlation map specification** (this document)
3. **Coordinate with DIL Foundation Team** for storage methods
4. **Update Content Pillar** to display correlation map

---

## Conclusion

**Finding:** Correlation map does NOT exist  
**Action:** Add to enabling services refactoring (recommended)  
**Priority:** High (needed for Content Pillar MVP)  
**Timeline:** Phase 1 (Content + Insights Integration)


