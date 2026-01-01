# Parsed File Storage Architecture Analysis

## Current Problem

**Root Cause:** `store_parsed_file()` stores parsed files incorrectly:
1. Creates a new file in `project_files` table via `create_file()` → gets UUID `72fd0dd0-...`
2. Generates separate `parsed_file_id = "parsed_{uuid}"` 
3. Stores metadata in `parsed_data_files` with the generated ID, NOT the actual GCS file UUID
4. **Result:** File exists in `project_files` but `parsed_data_files` has wrong ID → lookups fail

## Architecture Decision: Where Should Parsed Files Be Stored?

### Option A: Supabase + GCS (Current Intended Approach) ✅ **RECOMMENDED**

**Storage:**
- **Binary Data:** GCS (via `file_management_abstraction`)
- **Metadata:** Supabase `parsed_data_files` table
- **Semantic Data:** ArangoDB (embeddings only, not raw parsed data)

**Rationale:**
1. **"Leaving Client Data at the Door":**
   - Client data (files, parsed files) stays in GCS/Supabase with strict tenant isolation
   - Only semantic representations (embeddings) go to ArangoDB for cross-client intelligence
   - Maintains clear boundary: client data vs. platform intelligence

2. **Technical Fit:**
   - GCS handles large binary files efficiently (JSONL, Parquet)
   - Supabase provides fast metadata queries with tenant isolation
   - ArangoDB is optimized for graph/embeddings, not large binary blobs

3. **Data Mash Vision Alignment:**
   - Infrastructure Layer (GCS/Supabase) = Client data storage
   - Semantic Layer (ArangoDB) = Platform intelligence (embeddings only)
   - Clear separation enables cross-client learning without data leakage

**Implementation:**
- Store parsed file binary in GCS (via `file_management_abstraction.create_file()`)
- Store metadata in `parsed_data_files` table with:
  - `parsed_file_id` = **ACTUAL GCS file UUID** (not a generated string)
  - `file_id` = Original file UUID (link to source)
  - `gcs_file_id` = Same as `parsed_file_id` (for clarity)

### Option B: ArangoDB Only ❌ **NOT RECOMMENDED**

**Storage:**
- Binary data + metadata in ArangoDB

**Why Not:**
- ArangoDB is not designed for large binary files (JSONL, Parquet)
- Would require base64 encoding → inefficient storage
- Breaks existing file storage patterns
- Doesn't align with "infrastructure layer" separation

### Option C: Hybrid (Metadata in ArangoDB, Binary in GCS) ⚠️ **POSSIBLE BUT COMPLEX**

**Storage:**
- Binary in GCS
- Metadata in ArangoDB `parsed_data` collection

**Why Not:**
- Duplicates metadata storage (Supabase + ArangoDB)
- Adds complexity without clear benefit
- Supabase already provides tenant isolation and fast queries

## Recommended Fix

### 1. Fix `store_parsed_file()` to Use Actual GCS UUID

**Current (WRONG):**
```python
parsed_file_id = f"parsed_{uuid.uuid4()}"  # Generated ID
gcs_result = await self.service.file_management_abstraction.create_file(parsed_file_record)
parsed_file_gcs_id = gcs_result.get("uuid")  # Actual GCS UUID (different!)
```

**Should Be:**
```python
# Store in GCS first
gcs_result = await self.service.file_management_abstraction.create_file(parsed_file_record)
parsed_file_gcs_id = gcs_result.get("uuid")  # Actual GCS UUID
parsed_file_id = parsed_file_gcs_id  # Use actual UUID, not generated one

# Then store metadata with correct ID
parsed_file_metadata = {
    "file_id": file_id,
    "parsed_file_id": parsed_file_gcs_id,  # Use actual GCS UUID
    "gcs_file_id": parsed_file_gcs_id,  # Same value
    ...
}
```

### 2. Update Discovery Logic

**Current:** Falls back to searching `project_files` by name pattern

**Should Be:** 
- Primary: Query `parsed_data_files` by `file_id` (original file)
- If not found, check if original file has `status = "parsed"` and `metadata.is_parsed_file = true`
- Use the actual file UUID from `project_files` as `parsed_file_id`

### 3. Impact on Preview Discovery

**Current Flow:**
1. List parsed files → queries `parsed_data_files` by `file_id`
2. Falls back to `project_files` with name pattern
3. Preview fails because `parsed_file_id` doesn't match GCS UUID

**Fixed Flow:**
1. List parsed files → queries `parsed_data_files` by `file_id` → returns `parsed_file_id` = actual GCS UUID
2. Preview uses `parsed_file_id` → finds file in GCS directly
3. No fallback needed

## Data Mash Vision: "Leaving Client Data at the Door"

**Principle:** Client data stays in infrastructure layer, only semantic intelligence crosses the boundary.

**Storage Map:**
```
┌─────────────────────────────────────────────────────────┐
│ INFRASTRUCTURE LAYER (Client Data - Tenant Isolated)   │
│                                                         │
│ • Original Files: GCS + Supabase project_files         │
│ • Parsed Files: GCS + Supabase parsed_data_files       │
│ • Both have tenant_id + data_classification="client"   │
└─────────────────────────────────────────────────────────┘
                          ↓ (semantic processing)
┌─────────────────────────────────────────────────────────┐
│ SEMANTIC LAYER (Platform Intelligence - Cross-Client) │
│                                                         │
│ • Embeddings: ArangoDB (semantic_embeddings)           │
│ • Semantic Graphs: ArangoDB (semantic_graphs)          │
│ • NO raw client data, only semantic representations     │
└─────────────────────────────────────────────────────────┘
```

**Key Points:**
- Client data (files, parsed files) = Infrastructure layer (GCS/Supabase)
- Platform intelligence (embeddings) = Semantic layer (ArangoDB)
- Clear boundary enables cross-client learning without data leakage
- Tenant isolation maintained at infrastructure layer

## Conclusion

**Recommendation:** **Option A (Supabase + GCS)** - Fix the implementation to use actual GCS UUIDs

**Next Steps:**
1. Fix `store_parsed_file()` to use actual GCS UUID as `parsed_file_id`
2. Update `list_parsed_files()` to correctly link `parsed_data_files` entries
3. Remove fallback name-pattern search (shouldn't be needed once IDs are correct)
4. Update preview logic to use correct `parsed_file_id` from `parsed_data_files`

