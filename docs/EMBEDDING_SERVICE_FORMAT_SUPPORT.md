# EmbeddingService Format Support

**Date:** December 29, 2025  
**Status:** ✅ **COMPLETE**

---

## 🎯 **Overview**

EmbeddingService now supports all parsing output formats and content types used by the File Parser Service.

---

## 📋 **Supported Format Types**

### **1. `jsonl` (JSON Lines)**
- **Used for:** Structured data (default format)
- **Structure:** One JSON object per line
- **Example:**
  ```
  {"column1": "value1", "column2": 123}
  {"column1": "value2", "column2": 456}
  ```
- **Processing:** Parse line-by-line, convert to DataFrame for tabular embeddings

### **2. `json_structured` (Structured JSON)**
- **Used for:** Structured data in hybrid files, single JSON objects/arrays
- **Structure:** Single JSON object or array of objects
- **Example:**
  ```json
  [
    {"column1": "value1", "column2": 123},
    {"column1": "value2", "column2": 456}
  ]
  ```
- **Processing:** Parse as single JSON, convert to DataFrame for tabular embeddings

### **3. `json_chunks` (Text Chunks)**
- **Used for:** Unstructured content (text chunks)
- **Structure:** Array of text chunk objects
- **Example:**
  ```json
  [
    {"text": "Chunk 1 content...", "metadata": {...}},
    {"text": "Chunk 2 content...", "metadata": {...}}
  ]
  ```
- **Processing:** Extract text from chunks, create document-based embeddings (not tabular)

### **4. `parquet` (Legacy)**
- **Used for:** Legacy structured data (backward compatibility)
- **Structure:** Binary Parquet format
- **Processing:** Read with pandas, convert to DataFrame for tabular embeddings

---

## 📊 **Content Type Handling**

### **Structured Content (`content_type: "structured"`)**
- **Format Types:** `jsonl`, `json_structured`, `parquet`
- **Embedding Strategy:** Column-based embeddings
  - Metadata embeddings (column name + data type)
  - Meaning embeddings (semantic meaning)
  - Sample embeddings (representative values)
- **Data Structure:** Tabular (DataFrame)

### **Unstructured Content (`content_type: "unstructured"`)**
- **Format Types:** `json_chunks`
- **Embedding Strategy:** Document-based embeddings
  - Chunk embeddings (text content of each chunk)
  - Metadata embeddings (chunk metadata)
- **Data Structure:** Array of text chunks

### **Hybrid Content (`content_type: "hybrid"`)**
- **Format Types:** Multiple files (structured + unstructured)
- **Embedding Strategy:** 
  - Structured part: Column-based embeddings
  - Unstructured part: Document-based embeddings
- **Note:** Currently handled as separate parsed files (future: correlation support)

---

## 🔧 **Implementation Details**

### **Format Detection**
```python
format_type = parsed_file_result.get("format_type", "parquet").lower()
content_type = parsed_file_result.get("content_type", "structured").lower()
```

### **Format-Specific Processing**

#### **JSONL (`jsonl`)**
```python
# Parse line-by-line
lines = file_content.strip().split('\n')
records = [json.loads(line) for line in lines if line.strip()]
df = pd.DataFrame(records)
```

#### **JSON Structured (`json_structured`)**
```python
# Parse as single JSON
data = json.loads(file_content)
if isinstance(data, list):
    df = pd.DataFrame(data)
elif isinstance(data, dict):
    # Single object - convert to DataFrame with one row
    df = pd.DataFrame([data])
```

#### **JSON Chunks (`json_chunks`)**
```python
# Parse as array of chunks
chunks = json.loads(file_content)
if isinstance(chunks, list):
    # Extract text from chunks
    texts = [chunk.get("text", "") if isinstance(chunk, dict) else str(chunk) for chunk in chunks]
    # Process as unstructured content (not tabular)
```

#### **Parquet (`parquet`)**
```python
# Read binary format
parquet_buffer = io.BytesIO(file_content)
df = pd.read_parquet(parquet_buffer)
```

---

## ✅ **Validation**

All format types are validated:
- ✅ Format type detection from `parsed_file_result`
- ✅ Content type detection for appropriate embedding strategy
- ✅ Error handling for unsupported formats
- ✅ Logging for format-specific processing

---

## 🚀 **Future Enhancements**

1. **Hybrid File Correlation:** Support for correlating structured and unstructured embeddings
2. **Workflow/SOP Support:** Special handling for workflow and SOP content types
3. **Format Conversion:** Optional conversion between formats for analytics

---

## 📝 **Migration Notes**

- ✅ Legacy Parquet files still supported
- ✅ New files default to JSONL for structured data
- ✅ Unstructured files use JSON chunks format
- ✅ Hybrid files create separate embeddings for each part








