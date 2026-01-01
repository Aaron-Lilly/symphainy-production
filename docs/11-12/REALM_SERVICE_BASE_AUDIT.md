# RealmServiceBase Audit Report

## Summary
Audit of `RealmServiceBase` to identify incorrect Smart City service method calls, similar to the Librarian `store_document` issue that was fixed.

## Issues Found

### 1. ❌ `search_documents()` - Librarian Service
**Location:** Line 532  
**Current Call:**
```python
return await librarian.search_documents(query)
```

**Actual Librarian Method:**
```python
async def search_knowledge(self, query: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]
```

**Fix:** Change to `search_knowledge(query, filters=None)`

---

### 2. ❌ `classify_content()` - Content Steward Service
**Location:** Line 557  
**Current Call:**
```python
return await content_steward.classify_content(content, classification_type)
```

**Actual Content Steward Methods:**
- `validate_content(content_data: bytes, content_type: str) -> bool`
- `get_quality_metrics(asset_id: str) -> Dict[str, Any]`
- `get_asset_metadata(asset_id: str) -> Dict[str, Any]`

**Fix:** Remove this method or replace with appropriate Content Steward method. Content Steward doesn't have a `classify_content` method.

---

### 3. ❌ `enrich_metadata()` - Content Steward Service
**Location:** Line 578  
**Current Call:**
```python
return await content_steward.enrich_metadata(content_id, enrichment_type)
```

**Actual Content Steward Methods:**
- `get_asset_metadata(asset_id: str) -> Dict[str, Any]`
- `get_lineage(asset_id: str) -> Dict[str, Any]`

**Fix:** Replace with `get_asset_metadata(content_id)` or remove if not needed.

---

### 4. ❌ `validate_data()` - Data Steward Service
**Location:** Line 603  
**Current Call:**
```python
return await data_steward.validate_data(data, validation_rules)
```

**Actual Data Steward Method:**
```python
async def validate_schema(self, schema_data: Dict[str, Any]) -> bool
```

**Fix:** Change to `validate_schema()` with proper data structure, or create a wrapper that converts `(data, rules)` to `schema_data`.

---

### 5. ❌ `transform_data()` - Data Steward Service
**Location:** Line 624  
**Current Call:**
```python
return await data_steward.transform_data(data, transformation_rules)
```

**Actual Data Steward Methods:**
- No `transform_data` method exists
- Available: `create_content_policy()`, `record_lineage()`, `validate_schema()`, `get_quality_metrics()`, `enforce_compliance()`

**Fix:** Remove this method or create it in Data Steward if transformation is needed.

---

### 6. ❌ `track_lineage()` - Data Steward Service
**Location:** Line 647  
**Current Call:**
```python
return await data_steward.track_lineage(source, destination, transformation)
```

**Actual Data Steward Method:**
```python
async def record_lineage(self, lineage_data: Dict[str, Any]) -> str
```

**Expected `lineage_data` structure:**
```python
{
    "asset_id": str,
    "parent_assets": List[str],  # optional
    "child_assets": List[str],    # optional
    "transformation": Dict[str, Any],  # optional
    # ... other metadata
}
```

**Fix:** Change to `record_lineage()` and convert parameters to proper `lineage_data` dict structure.

---

## Architecture Notes

### Service Responsibilities:
- **Content Steward**: File/document storage, content processing, metadata extraction, quality metrics
- **Data Steward**: Data governance, policy management, lineage tracking, schema validation, compliance
- **Librarian**: Knowledge management, semantic search, content cataloging (NOT document storage)

### Correct Patterns:
✅ `store_document()` → Content Steward `process_upload()`  
✅ `retrieve_document()` → Content Steward `get_file()`  
✅ `search_knowledge()` → Librarian `search_knowledge()`  
✅ `record_lineage()` → Data Steward `record_lineage()`  

---

## Fix Priority

1. **High Priority** (Breaking):
   - `track_lineage()` → `record_lineage()` (used by many services)
   - `search_documents()` → `search_knowledge()` (if used)

2. **Medium Priority** (May cause errors):
   - `validate_data()` → `validate_schema()` (if used)
   - `enrich_metadata()` → `get_asset_metadata()` (if used)

3. **Low Priority** (May not be used):
   - `classify_content()` → Remove or replace
   - `transform_data()` → Remove or create in Data Steward

---

## Next Steps

1. Fix all 6 issues in `RealmServiceBase`
2. Search codebase for usages of these methods
3. Update all callers if method signatures change
4. Test to ensure no regressions






