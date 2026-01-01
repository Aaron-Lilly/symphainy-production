# Structured Data Format Recommendation

**Date:** December 22, 2025  
**Goal:** Simple, Flexible, AI-Friendly storage for parsed structured data

---

## 🎯 **Recommendation: JSONL (JSON Lines)**

**JSONL** is the best choice for your goals:
- ✅ **Simple**: Just JSON objects, one per line. No complex type inference.
- ✅ **Flexible**: Handles any structure, nested data, varying schemas per record
- ✅ **AI-Friendly**: LLMs work excellently with JSON, easy to chunk for embeddings
- ✅ **No Type Issues**: Everything is JSON-native, no PyArrow/Pandas type conversion problems
- ✅ **Easy to Preview**: Read first N lines for preview, no need to load entire file
- ✅ **Streaming-Friendly**: Process line-by-line for large files
- ✅ **Human-Readable**: Can inspect with `head`, `tail`, `grep`, etc.

---

## 📊 **Format Comparison**

| Format | Simple | Flexible | AI-Friendly | Type Issues | File Size | Analytics |
|--------|--------|---------|-------------|-------------|-----------|-----------|
| **JSONL** ⭐ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅ None | Medium | Good |
| **Parquet** | ❌ Complex | ⚠️ Schema required | ⚠️ Needs conversion | ❌ Type inference issues | ✅ Small | ✅✅ Excellent |
| **JSON** (single file) | ✅✅ | ✅✅✅ | ✅✅✅ | ✅ None | Large | Poor |
| **CSV** | ✅✅✅ | ❌ No nesting | ⚠️ Limited | ⚠️ Type loss | Small | Good |

---

## 🔄 **Current vs. Recommended**

### **Current: Parquet**
```python
# Issues we're experiencing:
- PyArrow type inference failures (object columns)
- Requires pandas/pyarrow dependencies
- Complex type conversion logic needed
- Not directly AI-friendly (needs conversion to JSON)
```

### **Recommended: JSONL**
```python
# Benefits:
- No type inference needed (everything is JSON)
- Simple conversion: json.dumps() per record
- Directly AI-friendly (already JSON)
- Easy to preview (read first N lines)
- Streaming-friendly (process line-by-line)
```

---

## 💡 **Implementation Strategy**

### **1. Update `_convert_to_parquet_bytes()` → `_convert_to_jsonl_bytes()`**

```python
async def _convert_to_jsonl_bytes(self, parse_result: Dict[str, Any]) -> Optional[bytes]:
    """
    Convert parsed data to JSONL (JSON Lines) format.
    One JSON object per line, newline-delimited.
    
    Simple, flexible, AI-friendly format.
    """
    try:
        import json
        
        # Extract records (same logic as before)
        records = []
        if "tables" in parse_result and isinstance(parse_result["tables"], list):
            for table in parse_result["tables"]:
                if isinstance(table, list):
                    records.extend(table)
                elif isinstance(table, dict):
                    records.append(table)
        if "records" in parse_result:
            records.extend(parse_result["records"])
        if "data" in parse_result:
            data = parse_result["data"]
            if isinstance(data, list):
                records.extend(data)
            elif isinstance(data, dict):
                records.append(data)
        
        if not records:
            self.logger.warning("⚠️ No structured data found - cannot convert to JSONL")
            return None
        
        # Convert to JSONL: one JSON object per line
        jsonl_lines = []
        for record in records:
            # Convert to native Python types (handles numpy types automatically)
            json_line = json.dumps(record, default=str)  # default=str handles numpy types
            jsonl_lines.append(json_line)
        
        # Join with newlines and encode to bytes
        jsonl_content = '\n'.join(jsonl_lines)
        jsonl_bytes = jsonl_content.encode('utf-8')
        
        self.logger.info(f"✅ Converted to JSONL: {len(records)} records, {len(jsonl_bytes)} bytes")
        return jsonl_bytes
        
    except Exception as e:
        self.logger.error(f"❌ Failed to convert to JSONL bytes: {e}", exc_info=True)
        return None
```

### **2. Update Preview Method**

```python
async def preview_parsed_file(
    self,
    parsed_file_id: str,
    max_rows: int = 20,
    max_columns: int = 20,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Preview parsed file from JSONL storage.
    Reads first N lines and extracts first M columns.
    """
    try:
        # Get parsed file from Content Steward
        parsed_file = await content_steward.get_parsed_file(parsed_file_id)
        if not parsed_file:
            return {"success": False, "error": "Parsed file not found"}
        
        # Extract JSONL data
        jsonl_data = parsed_file.get("file_data") or parsed_file.get("file_content")
        if not jsonl_data:
            return {"success": False, "error": "Parsed file has no data"}
        
        # Convert to string if bytes
        if isinstance(jsonl_data, bytes):
            jsonl_data = jsonl_data.decode('utf-8')
        
        # Parse JSONL (one JSON object per line)
        import json
        lines = jsonl_data.strip().split('\n')
        records = [json.loads(line) for line in lines[:max_rows]]
        
        # Extract columns (from first record)
        if records:
            all_columns = list(records[0].keys())
            columns = all_columns[:max_columns]
            
            # Build preview grid
            preview_rows = []
            for record in records:
                row = [str(record.get(col, '')) for col in columns]
                preview_rows.append(row)
            
            return {
                "success": True,
                "parsed_file_id": parsed_file_id,
                "preview": {
                    "columns": columns,
                    "rows": preview_rows,
                    "total_rows": len(lines),
                    "total_columns": len(all_columns),
                    "preview_rows": len(preview_rows),
                    "preview_columns": len(columns)
                }
            }
        else:
            return {"success": False, "error": "No records found"}
            
    except Exception as e:
        self.logger.error(f"❌ Preview parsed file failed: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
```

---

## 🚀 **Migration Path**

### **Option 1: Switch to JSONL (Recommended)**
1. Replace `_convert_to_parquet_bytes()` with `_convert_to_jsonl_bytes()`
2. Update `format_type` from `"parquet"` to `"jsonl"` or `"json_structured"`
3. Update preview method to read JSONL
4. Keep Parquet support for backward compatibility (if needed)

### **Option 2: Support Both Formats**
- Use JSONL as default (simple, AI-friendly)
- Keep Parquet as optional for analytics workloads
- Let user choose format based on use case

---

## ✅ **Benefits for Your Use Case**

1. **No More Type Issues**: JSON handles everything natively
2. **AI-Friendly**: LLMs can directly process JSONL for embeddings/chunking
3. **Simple Preview**: Just read first N lines, no complex parsing
4. **Flexible Schema**: Each record can have different fields
5. **Easy Debugging**: Can inspect with `head`, `tail`, `grep`
6. **Streaming**: Process large files line-by-line without loading entire file

---

## 📝 **Example JSONL Output**

```
{"BF-ISSUE-SYSTEM":"MP","BF-KEY":"12345","BF-COMPANY-CODE":"ABC",...}
{"BF-ISSUE-SYSTEM":"MP","BF-KEY":"12346","BF-COMPANY-CODE":"ABC",...}
{"BF-ISSUE-SYSTEM":"MP","BF-KEY":"12347","BF-COMPANY-CODE":"ABC",...}
```

**Simple, readable, AI-friendly!**

---

**Recommendation:** Switch to JSONL for structured data storage. It aligns perfectly with your goals of simplicity, flexibility, and AI-friendliness.



