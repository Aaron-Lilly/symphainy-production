# Embedding-Based Preview Strategy
## Generating Previews from Semantic Embeddings

**Date:** December 14, 2025  
**Status:** 🎯 **Strategic Plan**  
**Goal:** Use embeddings (not raw parsed data) for frontend previews

---

## 🎯 **Overview**

**Question:** Can we generate a preview of parsed files from embeddings?

**Answer:** **Yes, but we need to store metadata alongside embeddings** (not just the embedding vectors).

**Key Insight:** Embeddings are vector representations - we can't "reverse" them to get original data. But we can store the necessary metadata (column names, types, sample values, semantic meanings) alongside embeddings to reconstruct a "semantic preview."

---

## 📊 **What Embeddings Currently Store**

Based on `semantic_data_abstraction.py` and `CONTENT_PILLAR_SEMANTIC_PLATFORM_FLOW.md`:

### **Structured Data Embeddings:**
```python
{
    "column_name": "customer_id",           # ✅ Stored as text
    "semantic_id": "sem_123",                # ✅ Stored as text
    "metadata_embedding": [0.1, 0.2, ...],   # Vector (can't reverse)
    "meaning_embedding": [0.3, 0.4, ...],   # Vector (can't reverse)
    "samples_embedding": [0.5, 0.6, ...]     # Vector (can't reverse)
}
```

### **What We Can Reconstruct:**
- ✅ **Column names** - Stored directly in embedding document
- ✅ **Semantic IDs** - Stored directly, can look up semantic model recommendations
- ❌ **Sample values** - Only embedded (vector), not stored as text
- ❌ **Semantic meanings** - Only embedded (vector), not stored as text
- ❌ **Data types** - Not stored in embedding document

---

## 🔍 **What We Need for Preview**

### **1. Parsed File Preview:**
- Column names
- Data types
- Sample values (first 10-20 rows)
- Row count
- Column count
- Structure info (table layout)

### **2. Semantic Data Model Preview:**
- Column names → Semantic meanings
- Column names → Semantic IDs
- Semantic model recommendations (from semantic_id matches)
- Confidence scores
- Validation status (if HITL validation exists)

---

## ✅ **Solution: Store Metadata Alongside Embeddings**

### **Enhanced Embedding Storage:**

```python
{
    # Embeddings (vectors)
    "metadata_embedding": [0.1, 0.2, ...],
    "meaning_embedding": [0.3, 0.4, ...],
    "samples_embedding": [0.5, 0.6, ...],
    
    # Metadata (text - for preview reconstruction)
    "column_name": "customer_id",                    # ✅ Already stored
    "data_type": "string",                           # ✅ NEW: Store data type
    "semantic_id": "sem_123",                        # ✅ Already stored
    "semantic_meaning": "Customer unique identifier", # ✅ NEW: Store meaning as text
    "sample_values": ["CUST001", "CUST002", ...],    # ✅ NEW: Store samples as text
    "row_count": 1000,                               # ✅ NEW: Store row count
    "column_position": 0,                            # ✅ NEW: Store column order
    
    # Semantic model info
    "semantic_model_recommendation": {               # ✅ NEW: Store recommendation
        "semantic_id": "sem_123",
        "confidence": 0.95,
        "meaning": "Customer unique identifier",
        "examples": ["CUST001", "CUST002"]
    }
}
```

### **Storage Location:**
- **ArangoDB:** Embeddings + metadata stored together in `structured_embeddings` collection
- **Librarian:** Content metadata (schema, structure) stored separately
- **Both:** Can be queried together for complete preview

---

## 🎨 **Preview Generation Strategy**

### **Option 1: Query Embeddings + Metadata (Recommended)**

```python
async def get_preview_from_embeddings(
    self,
    content_id: str,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate preview from embeddings + metadata.
    
    Flow:
    1. Query embeddings from ArangoDB (includes metadata)
    2. Query content metadata from Librarian (structure info)
    3. Combine to create preview
    4. Return preview (no raw parsed data needed)
    """
    # 1. Get embeddings (includes column_name, semantic_id, sample_values, etc.)
    embeddings = await self.semantic_data.get_semantic_embeddings(
        content_id=content_id,
        user_context=user_context
    )
    
    # 2. Get content metadata (structure, row_count, column_count)
    content_metadata = await self.librarian.get_content_metadata(
        content_id=content_id,
        user_context=user_context
    )
    
    # 3. Build preview from metadata (not raw data)
    preview = {
        "columns": [
            {
                "name": emb["column_name"],
                "data_type": emb.get("data_type", "unknown"),
                "semantic_meaning": emb.get("semantic_meaning", ""),
                "semantic_id": emb.get("semantic_id"),
                "sample_values": emb.get("sample_values", [])[:10],  # First 10 samples
                "position": emb.get("column_position", 0)
            }
            for emb in embeddings
        ],
        "structure": {
            "row_count": content_metadata.get("row_count", 0),
            "column_count": len(embeddings),
            "table_count": content_metadata.get("table_count", 1)
        },
        "semantic_model": {
            "recommendations": [
                {
                    "column_name": emb["column_name"],
                    "semantic_id": emb.get("semantic_id"),
                    "confidence": emb.get("semantic_model_recommendation", {}).get("confidence", 0.0),
                    "meaning": emb.get("semantic_meaning", "")
                }
                for emb in embeddings
            ]
        }
    }
    
    return preview
```

### **Option 2: Store Preview in Librarian (Alternative)**

Store a pre-computed preview in Librarian's content metadata:

```python
# When creating embeddings, also store preview
preview = {
    "columns": [...],
    "structure": {...},
    "semantic_model": {...}
}

await self.librarian.store_content_metadata(
    content_id=content_id,
    content_metadata={
        ...existing_metadata...,
        "preview": preview  # ✅ Store preview alongside metadata
    }
)
```

**Pros:**
- Faster retrieval (no need to query embeddings)
- Single source of truth

**Cons:**
- Duplicates data (also in embeddings)
- Need to keep in sync

---

## 🚀 **Implementation Plan**

### **Phase 1: Immediate Fix (Current)**
- ✅ Update `ContentOrchestrator.process_file()` to return metadata only
- ✅ Add note that full data is stored as parquet
- ✅ Test all parsing types (CSV, JSON, XLSX, Binary, Hybrid, TXT, PDF)

### **Phase 2: Enhanced Embedding Storage**
- [ ] Update `EmbeddingService` to store metadata alongside embeddings:
  - `data_type` (from parsed file metadata)
  - `semantic_meaning` (as text, not just embedding)
  - `sample_values` (as text array, not just embedding)
  - `row_count`, `column_position` (structure info)
  - `semantic_model_recommendation` (recommendation object)
- [ ] Update `SemanticDataAbstraction.store_semantic_embeddings()` to accept and store metadata
- [ ] Update embedding creation flow to extract and store metadata

### **Phase 3: Preview Generation Service**
- [ ] Create `PreviewService` (or method in `ContentOrchestrator`):
  - `get_preview_from_embeddings(content_id)` - Query embeddings + metadata
  - `get_semantic_model_preview(content_id)` - Query semantic recommendations
- [ ] Return preview structure (columns, structure, semantic_model)

### **Phase 4: Frontend Integration**
- [ ] Update `ParsePreview.tsx` to call preview endpoint (not parse endpoint)
- [ ] Display:
  - Column structure (from embeddings metadata)
  - Sample values (from embeddings metadata)
  - Semantic model recommendations (from semantic_id matches)
- [ ] Remove dependency on full parsed data in API response

### **Phase 5: Re-evaluate Parsing APIs**
- [ ] After frontend uses embeddings, determine what parsing APIs actually need to return
- [ ] Likely: Only metadata (already implemented in Phase 1)
- [ ] Remove any remaining full data returns

---

## 📋 **Updated Data Flow**

### **Current Flow (After Phase 1 Fix):**
```
1. Parse File
   ↓
2. Store Parsed Data (Parquet in GCS)
   ↓
3. Return Metadata Only (API Response)
   ↓
4. Frontend Displays Metadata (Limited Preview)
```

### **Target Flow (After Phase 4):**
```
1. Parse File
   ↓
2. Store Parsed Data (Parquet in GCS)
   ↓
3. Create Embeddings + Store Metadata
   ↓
4. Return Metadata Only (API Response) - for parsing tests
   ↓
5. Frontend Calls Preview Endpoint
   ↓
6. Preview Service Queries Embeddings + Metadata
   ↓
7. Frontend Displays Full Preview (from embeddings, not raw data)
```

---

## ✅ **Benefits of This Approach**

1. **Security:**
   - No raw client data in API responses
   - Only semantic representations exposed

2. **Performance:**
   - Previews generated from indexed metadata (fast)
   - No need to read large parquet files

3. **Alignment with Data Mash Vision:**
   - Uses semantic layer (embeddings) for display
   - Semantic model recommendations visible
   - Supports cross-client reasoning

4. **Flexibility:**
   - Can enhance previews without changing parsing
   - Can add semantic insights to preview
   - Can show recommendations from global semantic store

---

## 🔗 **Related Documents**

- `docs/DATA_FLOW_AFTER_METADATA_ONLY_FIX.md` - Current API response changes
- `docs/CONTENT_PILLAR_SEMANTIC_PLATFORM_FLOW.md` - Semantic platform flow
- `docs/UNIFIED_DATA_SOLUTION_IMPLEMENTATION_PLAN_V1.md` - Unified implementation plan
- `docs/DATA_FORMAT_CONVERSION_STRATEGY.md` - Format conversion strategy

---

## 📝 **Summary**

**Answer to User's Question:**
> "Could we generate a preview of the parsed file from the embeddings?"

**Yes, but we need to:**
1. Store metadata alongside embeddings (data types, sample values as text, semantic meanings as text)
2. Query embeddings + metadata to reconstruct preview
3. Create a preview endpoint that uses embeddings (not raw parsed data)

**User's Plan Makes Perfect Sense:**
1. ✅ Implement immediate fix (metadata only) - parsing tests pass
2. ✅ Validate parsing works for all file types
3. ✅ Proceed with embeddings
4. ✅ Update frontend to use embeddings for preview
5. ✅ Re-evaluate parsing APIs (likely only need metadata)

**This aligns perfectly with:**
- Data Mash vision (semantic layer)
- Security (no raw data in API)
- Performance (indexed metadata queries)
- Extensibility (can enhance previews without changing parsing)


