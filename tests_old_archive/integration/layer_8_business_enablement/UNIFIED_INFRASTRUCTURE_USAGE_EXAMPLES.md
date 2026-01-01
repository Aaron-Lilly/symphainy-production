# Unified Infrastructure Usage Examples

## 🎯 Purpose

This document provides examples of how to use the new unified infrastructure fixtures and helpers in tests.

---

## 📋 Available Fixtures

### **1. `infrastructure_storage`**

Provides unified access to file storage infrastructure.

**Returns**:
```python
{
    "file_storage": ContentSteward (preferred) or FileManagementAbstraction,
    "metadata_storage": SupabaseAdapter,
    "type": "content_steward" or "file_management_abstraction"
}
```

### **2. `infrastructure_database`**

Provides unified access to database infrastructure.

**Returns**:
```python
{
    "arangodb": ArangoDBAdapter,
    "redis": RedisAdapter
}
```

### **3. `infrastructure_ai`**

Provides unified access to AI infrastructure.

**Returns**:
```python
{
    "llm": LLMAbstraction,
    "document_intelligence": DocumentIntelligenceAbstraction
}
```

---

## 📚 Usage Examples

### **Example 1: File Storage with Unified Fixture**

**Before** (Complex):
```python
@pytest.mark.asyncio
async def test_store_file(smart_city_infrastructure):
    infra = smart_city_infrastructure
    
    # Get Content Steward
    content_steward = infra["smart_city_services"].get("content_steward")
    if not content_steward:
        # Fallback to FileManagementAbstraction
        file_abstraction = infra["public_works_foundation"].get_file_management_abstraction()
        if not file_abstraction:
            pytest.fail("Storage not available")
        storage = file_abstraction
    else:
        storage = content_steward
    
    # Store file
    helper = ContentStewardHelper(storage, user_context)
    file_id = await helper.store_file(file_data, filename)
```

**After** (Simple):
```python
@pytest.mark.asyncio
async def test_store_file(infrastructure_storage, user_context):
    """Store file using unified storage fixture."""
    storage = infrastructure_storage["file_storage"]
    
    helper = ContentStewardHelper(storage, user_context)
    file_id = await helper.store_file(file_data, filename)
    
    # Cleanup
    await helper.cleanup()
```

**Benefits**:
- ✅ Single fixture, no complex fallback logic
- ✅ Automatic selection of best storage option
- ✅ Clear and simple

---

### **Example 2: Database Operations**

**Before** (Complex):
```python
@pytest.mark.asyncio
async def test_database_operations(smart_city_infrastructure):
    infra = smart_city_infrastructure
    pwf = infra["public_works_foundation"]
    
    arangodb = pwf.arango_adapter
    redis = pwf.redis_adapter
    
    # Use adapters
    await arangodb.create_document("test_collection", {"key": "value"})
    await redis.set("test_key", "test_value")
```

**After** (Simple):
```python
@pytest.mark.asyncio
async def test_database_operations(infrastructure_database):
    """Test database operations using unified fixture."""
    db = infrastructure_database
    
    # Use adapters
    await db["arangodb"].create_document("test_collection", {"key": "value"})
    await db["redis"].set("test_key", "test_value")
```

**Benefits**:
- ✅ Single fixture for all databases
- ✅ Consistent access pattern
- ✅ Easy to use

---

### **Example 3: AI Operations**

**Before** (Complex):
```python
@pytest.mark.asyncio
async def test_ai_operations(smart_city_infrastructure):
    infra = smart_city_infrastructure
    pwf = infra["public_works_foundation"]
    
    llm = pwf.get_llm_abstraction()
    doc_intel = pwf.get_document_intelligence_abstraction()
    
    # Use AI services
    result = await llm.generate_text("Hello")
    doc_result = await doc_intel.process_document(file_id)
```

**After** (Simple):
```python
@pytest.mark.asyncio
async def test_ai_operations(infrastructure_ai):
    """Test AI operations using unified fixture."""
    ai = infrastructure_ai
    
    # Use AI services
    result = await ai["llm"].generate_text("Hello")
    doc_result = await ai["document_intelligence"].process_document(file_id)
```

**Benefits**:
- ✅ Single fixture for all AI services
- ✅ Consistent access pattern
- ✅ Easy to use

---

### **Example 4: Enhanced ContentStewardHelper**

**Before** (Basic):
```python
helper = ContentStewardHelper(content_steward, user_context)
file_id = await helper.store_file(file_data, filename)
if not file_id:
    pytest.fail("Failed to store file")
```

**After** (Enhanced):
```python
helper = ContentStewardHelper(storage, user_context)

# Raises ValueError if fails (better error handling)
file_id = await helper.store_file(file_data, filename)

# Get file with validation
file_record = await helper.get_file(file_id)

# Cleanup (automatic tracking)
await helper.cleanup()
```

**Benefits**:
- ✅ Better error handling (raises exceptions)
- ✅ Automatic cleanup tracking
- ✅ Supports both Content Steward and FileManagementAbstraction
- ✅ Consistent API

---

### **Example 5: Complete Test with All Fixtures**

```python
@pytest.mark.asyncio
async def test_complete_workflow(
    infrastructure_storage,
    infrastructure_database,
    infrastructure_ai,
    user_context
):
    """Complete test using all unified fixtures."""
    
    # Storage operations
    storage = infrastructure_storage["file_storage"]
    helper = ContentStewardHelper(storage, user_context)
    
    file_id = await helper.store_file(b"test content", "test.txt")
    file_record = await helper.get_file(file_id)
    
    # Database operations
    db = infrastructure_database
    await db["redis"].set("test_key", "test_value")
    await db["arangodb"].create_document("test_collection", {"key": "value"})
    
    # AI operations
    ai = infrastructure_ai
    if ai["llm"]:
        result = await ai["llm"].generate_text("Hello")
    
    # Cleanup
    await helper.cleanup()
```

---

## ✅ Benefits Summary

### **For Tests**
- ✅ **Simpler**: Single fixtures, no complex setup
- ✅ **Faster**: Less boilerplate, faster test execution
- ✅ **Clearer**: Consistent patterns, easier to understand
- ✅ **More Reliable**: Automatic fallback chains, better error handling

### **For Development**
- ✅ **Easier**: No need to understand all infrastructure layers
- ✅ **Faster**: Less time setting up tests
- ✅ **Clearer**: Consistent patterns across all tests

### **For Maintenance**
- ✅ **Easier**: Unified patterns, easier to update
- ✅ **Clearer**: Consistent code, easier to debug
- ✅ **More Reliable**: Unified error handling, better error messages

---

## 🔒 Safeguards

All fixtures and helpers:
- ✅ **Preserve infrastructure swapping**: Adapters still use dependency injection
- ✅ **Protect SSH credentials**: Never touch `GOOGLE_APPLICATION_CREDENTIALS`
- ✅ **Use existing infrastructure**: Leverage existing Public Works Foundation initialization

---

## 📖 Migration Guide

### **Step 1: Update Test Signature**

**Before**:
```python
async def test_example(smart_city_infrastructure):
```

**After**:
```python
async def test_example(infrastructure_storage, user_context):
```

### **Step 2: Use Unified Fixture**

**Before**:
```python
infra = smart_city_infrastructure
content_steward = infra["smart_city_services"].get("content_steward")
```

**After**:
```python
storage = infrastructure_storage["file_storage"]
```

### **Step 3: Use Enhanced Helper**

**Before**:
```python
helper = ContentStewardHelper(content_steward, user_context)
file_id = await helper.store_file(file_data, filename)
if not file_id:
    pytest.fail("Failed")
```

**After**:
```python
helper = ContentStewardHelper(storage, user_context)
file_id = await helper.store_file(file_data, filename)  # Raises if fails
await helper.cleanup()  # Automatic cleanup
```

---

## 🎯 Next Steps

1. ✅ Update existing tests to use unified fixtures
2. ✅ Use enhanced helpers for better error handling
3. ✅ Add cleanup calls to all tests
4. ✅ Document any test-specific patterns

