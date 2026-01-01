# Parsed File Storage and Validation Analysis

**Date:** December 22, 2025  
**Status:** 📋 **ANALYSIS COMPLETE - RECOMMENDATIONS PROVIDED**

---

## 🎯 User Requirements

1. **Structured files should be saved as parquet files** (for performance - avoid huge JSON responses)
2. **Flow should be**: Save parsed output → Call preview function with parsed file → Preview retrieves first 20 rows/columns
3. **Check legacy binary parsing for validation checker** (field value validation based on COBOL constraints)
4. **Suggest validation implementation** if not found (possibly with agents)

---

## 1. ✅ Parquet File Storage

### **Current Status:**

**Found:** Parquet storage logic exists in `content_orchestrator.py` (old version) but **NOT** in `content_analysis_orchestrator.py` (current version).

**Location:** `/home/founders/demoversion/symphainy_source/symphainy-platform/backend/journey/orchestrators/content_journey_orchestrator/content_orchestrator.py`

**Key Methods:**
- `_convert_to_parquet_bytes()` - Converts parsed data to parquet bytes
- `store_parsed_file()` - Stores parquet file via Content Steward

**Current Issue:** `content_analysis_orchestrator.py` (the one we're using) doesn't have this logic.

### **Recommendation:**

**Add parquet storage to `content_analysis_orchestrator.py`:**

```python
async def process_file(...):
    # ... parse file ...
    
    # Save as parquet for structured data
    if parse_result.get("parsing_type") == "structured" and parse_result.get("success"):
        parquet_bytes = await self._convert_to_parquet_bytes(parse_result)
        if parquet_bytes:
            content_steward = await self._get_content_steward()
            store_result = await content_steward.store_parsed_file(
                file_id=file_id,
                parsed_file_data=parquet_bytes,
                format_type="parquet"
            )
            parsed_file_id = store_result.get("parsed_file_id")
    
    # Return summary with parsed_file_id (not full data)
    return {
        "success": True,
        "file_id": file_id,
        "parsed_file_id": parsed_file_id,  # Reference to parquet file
        "parse_result": parse_summary,  # Metadata only
        ...
    }
```

**Implementation Steps:**
1. Copy `_convert_to_parquet_bytes()` from `content_orchestrator.py` to `content_analysis_orchestrator.py`
2. Add parquet storage logic to `process_file()` method
3. Ensure `parsed_file_id` is returned in response

---

## 2. ✅ Preview Function Flow

### **Current Status:**

**Found:** Preview logic exists in legacy code but needs to be updated for parquet-based flow.

**Legacy Pattern:**
- Preview generated during parsing (first 20 rows)
- Preview included in parse response

**Recommended Flow:**
```
1. Parse file → Save as parquet → Return parsed_file_id
2. Frontend calls preview endpoint with parsed_file_id
3. Preview endpoint reads first 20 rows from parquet file
4. Return preview data (small, fast)
```

### **Recommendation:**

**Create/Update Preview Endpoint:**

```python
async def preview_parsed_file(
    self,
    parsed_file_id: str,
    max_rows: int = 20,
    max_columns: int = 20,
    user_id: str = None
) -> Dict[str, Any]:
    """
    Preview parsed file from parquet storage.
    
    Reads first N rows/columns from parquet file for display.
    """
    # 1. Retrieve parquet file from Content Steward
    parsed_file = await self._realm_service.retrieve_document(parsed_file_id)
    
    # 2. Read parquet file (from GCS or local)
    parquet_data = parsed_file.get("file_content") or parsed_file.get("data")
    
    # 3. Load into pandas DataFrame
    import pandas as pd
    import pyarrow.parquet as pq
    from io import BytesIO
    
    df = pd.read_parquet(BytesIO(parquet_data))
    
    # 4. Extract preview (first max_rows rows, first max_columns columns)
    preview_df = df.iloc[:max_rows, :max_columns]
    
    # 5. Convert to JSON-serializable format
    preview_data = {
        "columns": list(preview_df.columns),
        "rows": preview_df.fillna("").astype(str).values.tolist(),
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "preview_rows": len(preview_df),
        "preview_columns": len(preview_df.columns)
    }
    
    return {
        "success": True,
        "parsed_file_id": parsed_file_id,
        "preview": preview_data
    }
```

**Frontend Changes:**
- Add dropdown to select parsed files (from `list_parsed_files` endpoint)
- Call `preview_parsed_file` endpoint when user selects a parsed file
- Display preview grid (20 rows × 20 columns)

---

## 3. ✅ Legacy Validation Checker

### **Found: COBOL Level 88 Validation**

**Location:** `/home/founders/demoversion/symphainy-mvp-backend-final-legacy/backend/utils/extractor_agents/cobol2csv.py`

**What It Does:**
- Extracts COBOL level 88 condition names (allowed values)
- Stores in `level88_values` dictionary
- Adds `mapper` field to field definitions with allowed values
- Example:
  ```cobol
  05 FIELD-NAME PIC X(1).
     88 VALID-VALUES VALUE 'A' 'B' 'C' 'D' 'E' 'F' 'G' 'H' 'I' 'J'.
  ```
  - Field `FIELD-NAME` can only contain A-J
  - If value is 'Q', validation would flag it as invalid

**Code Pattern:**
```python
# Extract level 88 values
level88_values = {}  # Maps field names to allowed values

for line in clean_cobol(lines):
    if line.strip().startswith("88"):
        # Extract parent field name
        # Extract VALUES clause
        # Store allowed values in level88_values[parent_field]

# Add to field definition
if field_name in level88_values:
    element["mapper"] = sorted(list(level88_values[field_name]))
```

**Current Status:** ❌ **NOT IMPLEMENTED** in current `mainframe_processing_adapter.py`

---

## 4. ✅ Validation Implementation Recommendation

### **Option 1: Rule-Based Validation (Recommended for MVP)**

**Implementation:**
1. **Extract Level 88 values during copybook parsing**
2. **Store validation rules in field definitions**
3. **Validate during record parsing**

**Code Structure:**
```python
# In _parse_copybook_from_string()
level88_values = {}  # Extract from copybook

# In _parse_binary_records()
for record in records:
    for field_name, field_value in record.items():
        if field_name in level88_values:
            allowed_values = level88_values[field_name]
            if field_value not in allowed_values:
                validation_errors.append({
                    "field": field_name,
                    "value": field_value,
                    "allowed": allowed_values,
                    "record": record_number
                })
```

**Pros:**
- Fast (rule-based, no AI needed)
- Accurate (based on copybook constraints)
- Can validate during parsing

**Cons:**
- Only works for COBOL level 88 constraints
- Doesn't catch semantic errors (e.g., date ranges)

---

### **Option 2: Agent-Based Validation (For Advanced Cases)**

**When to Use:**
- Semantic validation (e.g., "issue date must be before expiry date")
- Business rule validation (e.g., "policy number format")
- Data quality checks (e.g., "all required fields present")

**Implementation:**
```python
async def validate_parsed_data(
    self,
    parsed_file_id: str,
    validation_rules: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Validate parsed data using agents.
    
    Uses specialist agent to:
    1. Load parsed data (parquet)
    2. Apply validation rules
    3. Generate validation report
    """
    # 1. Get validation agent
    validation_agent = await self._get_validation_agent()
    
    # 2. Load parsed data
    parsed_file = await self._realm_service.retrieve_document(parsed_file_id)
    
    # 3. Create validation task
    validation_task = {
        "parsed_file_id": parsed_file_id,
        "validation_rules": validation_rules or ["level88_constraints", "data_types", "ranges"],
        "data_sample": ...  # First 100 records for validation
    }
    
    # 4. Run validation
    validation_result = await validation_agent.validate(validation_task)
    
    return {
        "success": True,
        "validation_report": validation_result,
        "errors": validation_result.get("errors", []),
        "warnings": validation_result.get("warnings", []),
        "passed": validation_result.get("passed", True)
    }
```

**Agent Responsibilities:**
- Load validation rules from copybook metadata
- Apply rule-based checks (level 88, data types)
- Apply semantic checks (date ranges, business rules)
- Generate validation report

**Pros:**
- Handles complex validation rules
- Can learn from patterns
- Can provide explanations

**Cons:**
- Slower (requires agent processing)
- More complex to implement
- May need training data

---

### **Recommended Hybrid Approach:**

1. **Phase 1: Rule-Based (Immediate)**
   - Extract level 88 values during copybook parsing
   - Validate during record parsing
   - Store validation errors in metadata

2. **Phase 2: Agent-Based (Future)**
   - Add specialist validation agent
   - Handle semantic/business rule validation
   - Generate comprehensive validation reports

---

## 📋 Implementation Priority

### **High Priority:**
1. ✅ Add parquet storage to `content_analysis_orchestrator.py`
2. ✅ Create preview endpoint that reads from parquet
3. ✅ Extract level 88 values during copybook parsing

### **Medium Priority:**
4. ⏳ Add validation during record parsing (rule-based)
5. ⏳ Frontend: Add parsed file dropdown
6. ⏳ Frontend: Update preview to use new endpoint

### **Low Priority:**
7. ⏳ Agent-based validation (Phase 2)
8. ⏳ Advanced semantic validation

---

## 🔍 Next Steps

1. **Review this analysis** - Confirm approach
2. **Implement parquet storage** - Add to `content_analysis_orchestrator.py`
3. **Implement preview endpoint** - Read from parquet
4. **Extract level 88 values** - Add to copybook parsing
5. **Add validation logic** - Validate during parsing

---

**Last Updated:** December 22, 2025  
**Status:** 📋 **READY FOR IMPLEMENTATION**



