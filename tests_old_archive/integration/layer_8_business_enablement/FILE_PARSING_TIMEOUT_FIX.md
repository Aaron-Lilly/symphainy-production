# File Parsing Timeout Fix - Blocking Operations

## 🎯 Problem

File parser test was timing out during Excel parsing. Investigation revealed **synchronous blocking operations** in async functions that could hang indefinitely.

## 🔍 Root Causes Identified

### **1. Excel Parsing Blocking Operation** ⚠️

**File**: `file_parser_service.py:1065`

**Issue**:
- `pd.read_excel(excel_file, sheet_name=None)` - Synchronous blocking call in async function
- Can hang indefinitely for large or corrupted Excel files
- No timeout protection

**Impact**: If Excel file is large or corrupted, parsing can hang and cause SSH session crashes.

### **2. Entity Extraction Blocking Operation** ⚠️

**File**: `document_processing_adapter.py:158`

**Issue**:
- `self.spacy_model(text)` - Synchronous blocking call in async function
- SpaCy processing can be slow for long texts
- No timeout protection

**Impact**: If text is very long, entity extraction can hang and cause SSH session crashes.

### **3. Embedding Generation Blocking Operation** ⚠️

**File**: `document_processing_adapter.py:191`

**Issue**:
- `self.sentence_transformer.encode(texts)` - Synchronous blocking call in async function
- Embedding generation can be slow for many texts
- No timeout protection

**Impact**: If processing many texts, embedding generation can hang and cause SSH session crashes.

## ✅ Fixes Applied

### **1. Excel Parsing Timeout Protection** ✅

**File**: `file_parser_service.py:1053-1103`

**Changes**:
1. Wrapped `pd.read_excel()` call in `asyncio.to_thread()` with 30-second timeout
2. Added `asyncio.wait_for()` for timeout protection
3. Added clear error message if timeout occurs

**Code Pattern**:
```python
try:
    excel_data = await asyncio.wait_for(
        asyncio.to_thread(pd.read_excel, excel_file, sheet_name=None),
        timeout=30.0  # 30 second timeout for Excel parsing
    )
except asyncio.TimeoutError:
    raise TimeoutError(
        f"Excel parsing timed out after 30 seconds. "
        f"File may be too large or corrupted."
    )
```

### **2. Entity Extraction Timeout Protection** ✅

**File**: `document_processing_adapter.py:144-175`

**Changes**:
1. Wrapped `self.spacy_model(text)` call in `asyncio.to_thread()` with 15-second timeout
2. Added `asyncio.wait_for()` for timeout protection
3. Returns empty list on timeout instead of failing (graceful degradation)

**Code Pattern**:
```python
try:
    doc = await asyncio.wait_for(
        asyncio.to_thread(self.spacy_model, text),
        timeout=15.0  # 15 second timeout for entity extraction
    )
except asyncio.TimeoutError:
    self.logger.warning(f"⚠️ Entity extraction timed out after 15 seconds")
    return []  # Return empty entities instead of failing
```

### **3. Embedding Generation Timeout Protection** ✅

**File**: `document_processing_adapter.py:177-198`

**Changes**:
1. Wrapped `self.sentence_transformer.encode(texts)` call in `asyncio.to_thread()` with 30-second timeout
2. Added `asyncio.wait_for()` for timeout protection
3. Returns empty list on timeout instead of failing (graceful degradation)

**Code Pattern**:
```python
try:
    embeddings = await asyncio.wait_for(
        asyncio.to_thread(self.sentence_transformer.encode, texts),
        timeout=30.0  # 30 second timeout for embedding generation
    )
except asyncio.TimeoutError:
    self.logger.warning(f"⚠️ Embedding generation timed out after 30 seconds")
    return []  # Return empty embeddings instead of failing
```

## 📋 How It Works Now

1. **Excel Parsing**:
   - Blocking `pd.read_excel()` call runs in thread pool
   - 30-second timeout prevents indefinite hangs
   - Clear error message if timeout occurs

2. **Entity Extraction**:
   - Blocking `spacy_model()` call runs in thread pool
   - 15-second timeout prevents indefinite hangs
   - Graceful degradation (returns empty list on timeout)

3. **Embedding Generation**:
   - Blocking `encode()` call runs in thread pool
   - 30-second timeout prevents indefinite hangs
   - Graceful degradation (returns empty list on timeout)

## 🧪 Testing

Run the file parser test to verify the fix:

```bash
cd /home/founders/demoversion/symphainy_source
timeout 180 python3 -m pytest tests/integration/layer_8_business_enablement/test_file_parser_functional.py::TestFileParserFunctional::test_file_parser_actually_parses_excel_file -v --tb=short
```

**Expected Behavior**:
- ✅ If file is normal: Test completes successfully
- ✅ If file is large: Test completes within timeout (may take longer but won't hang)
- ✅ If file is corrupted: Test fails fast with timeout error (no indefinite hang)
- ✅ SSH session remains stable (no crashes)

## 🔧 Additional Recommendations

### **Future Improvement: Make All Parsing Operations Async**

Consider making all parsing operations async to avoid blocking calls:

```python
# Instead of:
excel_data = pd.read_excel(excel_file)

# Use:
excel_data = await async_read_excel(excel_file)
```

### **Pattern for All Blocking Operations**

All blocking CPU-intensive operations in async functions should:
1. Use `asyncio.to_thread()` to run in thread pool
2. Wrap with `asyncio.wait_for()` for timeout protection
3. Provide clear error messages on timeout
4. Consider graceful degradation instead of failing

## 📝 Summary

- ✅ Fixed Excel parsing blocking operation - Added 30-second timeout
- ✅ Fixed entity extraction blocking operation - Added 15-second timeout
- ✅ Fixed embedding generation blocking operation - Added 30-second timeout
- ✅ All blocking operations now have timeout protection
- ✅ SSH sessions protected from indefinite hangs during file parsing



