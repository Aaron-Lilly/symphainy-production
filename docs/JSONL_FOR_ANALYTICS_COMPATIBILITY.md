# JSONL for Analytics/Insights Compatibility

**Date:** December 22, 2025  
**Question:** Will analytics/insights pillars work with JSONL, or do we need pandas DataFrames/Parquet?

**Answer:** ✅ **JSONL works perfectly!** Pandas can easily convert JSONL to DataFrames.

---

## ✅ **Key Finding: Insights Services Use Pandas DataFrames**

All insights/analytics services work with **pandas DataFrames**, not raw Parquet files:

```python
# Insights agents expect DataFrames:
- InsightsDataScientistAgent.analyze(df: pd.DataFrame)
- InsightsBusinessAnalystAgent.analyze(df: pd.DataFrame)
- InsightsEDAAgent.analyze(df: pd.DataFrame)
- InsightsDataQualityAgent.analyze(df: pd.DataFrame)
```

---

## 🔄 **JSONL → DataFrame Conversion**

Pandas has **native support** for JSONL:

### **Method 1: Direct JSONL Reading**
```python
import pandas as pd

# Read JSONL directly (pandas 1.2+)
df = pd.read_json('file.jsonl', lines=True)
```

### **Method 2: Manual Conversion (More Control)**
```python
import pandas as pd
import json

# Read JSONL and convert to DataFrame
with open('file.jsonl', 'r') as f:
    records = [json.loads(line) for line in f]
    df = pd.DataFrame(records)
```

### **Method 3: From Bytes (GCS Storage)**
```python
import pandas as pd
import json
import io

# Get JSONL bytes from Content Steward
jsonl_bytes = parsed_file.get("file_data")

# Convert to string and parse
jsonl_content = jsonl_bytes.decode('utf-8')
records = [json.loads(line) for line in jsonl_content.strip().split('\n')]
df = pd.DataFrame(records)
```

---

## 📊 **Current Code Already Supports This**

The existing `parse_parsed_file_to_dataframe()` utility already handles JSON conversion:

```python
# From: backend/content/services/semantic_enrichment_service/modules/utilities.py

def parse_parsed_file_to_dataframe(self, parsed_file: Dict[str, Any]) -> Optional[pd.DataFrame]:
    if "data" in parsed_file:
        data = parsed_file["data"]
        if isinstance(data, list):
            # List of dicts - convert to DataFrame ✅
            return pd.DataFrame(data)
        elif isinstance(data, str):
            # JSON string - parse and convert ✅
            data_dict = json.loads(data)
            if isinstance(data_dict, list):
                return pd.DataFrame(data_dict)
```

**This already works with JSON!** We just need to ensure JSONL is parsed into a list of dicts.

---

## 🎯 **Recommended Implementation**

### **For Insights Services: Add JSONL Support**

```python
# In structured_analysis_workflow.py or data_analyzer.py

async def _load_dataframe_from_parsed_file(
    self,
    parsed_file: Dict[str, Any],
    format_type: str
) -> Optional[pd.DataFrame]:
    """
    Load DataFrame from parsed file (supports multiple formats).
    
    Args:
        parsed_file: Parsed file dict from Content Steward
        format_type: "jsonl", "json_structured", "parquet", etc.
    
    Returns:
        pandas DataFrame or None
    """
    import pandas as pd
    import json
    import io
    
    try:
        file_data = parsed_file.get("file_data") or parsed_file.get("file_content")
        if not file_data:
            return None
        
        if format_type in ["jsonl", "json_structured"]:
            # JSONL: one JSON object per line
            if isinstance(file_data, bytes):
                file_data = file_data.decode('utf-8')
            
            # Parse JSONL lines
            lines = file_data.strip().split('\n')
            records = [json.loads(line) for line in lines if line.strip()]
            
            # Convert to DataFrame
            return pd.DataFrame(records)
            
        elif format_type == "parquet":
            # Parquet: use pandas read_parquet
            if isinstance(file_data, bytes):
                return pd.read_parquet(io.BytesIO(file_data))
            else:
                return pd.read_parquet(file_data)
                
        else:
            # Fallback: try existing parse_parsed_file_to_dataframe
            return self.parse_parsed_file_to_dataframe(parsed_file)
            
    except Exception as e:
        self.logger.error(f"❌ Failed to load DataFrame: {e}")
        return None
```

---

## ✅ **Benefits of JSONL for Analytics**

1. **No Type Issues**: JSONL → DataFrame conversion is straightforward
2. **Flexible Schema**: Each record can have different fields (pandas handles this)
3. **Easy Debugging**: Can inspect with `head`, `tail`, `grep`
4. **Streaming**: Can process large files line-by-line
5. **AI-Friendly**: Already JSON format, perfect for embeddings/chunking

---

## 📋 **Comparison: Parquet vs JSONL for Analytics**

| Aspect | Parquet | JSONL |
|--------|---------|-------|
| **Pandas Support** | ✅ `pd.read_parquet()` | ✅ `pd.read_json(lines=True)` or `pd.DataFrame(list)` |
| **Type Inference** | ❌ Complex (PyArrow issues) | ✅ Simple (JSON-native) |
| **File Size** | ✅ Smaller | ⚠️ Larger (but compressible) |
| **Read Speed** | ✅ Fast | ⚠️ Slower (but acceptable) |
| **AI-Friendly** | ❌ Needs conversion | ✅ Native JSON |
| **Human-Readable** | ❌ Binary | ✅ Text |
| **Schema Flexibility** | ⚠️ Fixed schema | ✅ Flexible schema |

---

## 🎯 **Recommendation**

**Use JSONL as the default format** for structured data storage:

1. ✅ **Works with Analytics**: Pandas can easily convert JSONL to DataFrames
2. ✅ **No Type Issues**: Avoids PyArrow type inference problems
3. ✅ **AI-Friendly**: Native JSON format, perfect for embeddings
4. ✅ **Simple**: Easy to implement and debug
5. ✅ **Flexible**: Handles varying schemas per record

**For Analytics Performance**: If needed, we can add an optional Parquet export for large-scale analytics workloads, but JSONL should be the default.

---

## 🔧 **Migration Path**

1. **Switch storage to JSONL** (simpler, AI-friendly)
2. **Update insights services** to support JSONL loading (add `_load_dataframe_from_parsed_file()`)
3. **Keep Parquet as optional** for performance-critical analytics (if needed)

**Result**: Best of both worlds - simple JSONL for most use cases, optional Parquet for analytics performance.



