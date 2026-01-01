# Insurance Agents Testing Guide

**Date:** December 2024  
**Status:** ✅ **TESTING FRAMEWORK CREATED**

---

## 🎯 Overview

This guide describes effective ways to test the Insurance Use Case agents:
1. **Insurance Liaison Agent** - Conversational guidance
2. **Universal Mapper Specialist Agent** - Pattern learning and AI-assisted mapping

---

## 📋 Testing Approaches

### **1. Simple Direct Testing (Recommended)**

**File:** `scripts/test_insurance_agents_simple.py`

**Approach:** Test agent methods directly without full initialization.

**Benefits:**
- ✅ Fast execution
- ✅ No complex mocking required
- ✅ Tests core agent logic
- ✅ Easy to maintain

**Usage:**
```bash
python3 scripts/test_insurance_agents_simple.py
```

**What It Tests:**
- Liaison Agent guidance methods (8 methods)
- Mapper Agent pattern learning
- Mapper Agent validation logic
- Mapper Agent correction learning
- Semantic similarity calculation
- Type compatibility checks

---

### **2. Integration Testing (Full Mock)**

**File:** `tests/integration/insurance_use_case/phase2_agents/test_insurance_agents.py`

**Approach:** Full agent initialization with mocked dependencies.

**Benefits:**
- ✅ Tests full agent lifecycle
- ✅ Tests agent initialization
- ✅ Tests agent integration patterns

**Challenges:**
- ⚠️ Requires complex mocking
- ⚠️ More setup required
- ⚠️ Slower execution

**Status:** ⏳ **IN PROGRESS** (needs mock improvements)

---

## 🧪 Test Coverage

### **Insurance Liaison Agent**

**Tested Methods:**
- ✅ `_get_ingestion_guidance()` - Data ingestion guidance
- ✅ `_get_mapping_guidance()` - Canonical mapping guidance
- ✅ `_get_routing_guidance()` - Policy routing guidance
- ✅ `_get_wave_guidance()` - Wave planning guidance
- ✅ `_get_tracking_guidance()` - Policy tracking guidance
- ✅ `_get_validation_guidance()` - Validation guidance
- ✅ `_get_rollback_guidance()` - Rollback guidance
- ✅ `_get_general_guidance()` - General migration guidance
- ✅ `_get_suggested_actions()` - Suggested actions generation

**Test Results:** ✅ **ALL PASSING**

---

### **Universal Mapper Specialist Agent**

**Tested Methods:**
- ✅ `_calculate_semantic_similarity()` - Field name similarity
- ✅ `_extract_mapping_patterns()` - Pattern extraction
- ✅ `_get_field_type()` - Field type retrieval
- ✅ `_validate_completeness()` - Mapping completeness
- ✅ `_validate_correctness()` - Mapping correctness
- ✅ `_are_types_compatible()` - Type compatibility
- ✅ `_extract_correction_pattern()` - Correction pattern extraction
- ✅ `_classify_correction_type()` - Correction classification

**Test Results:** ✅ **ALL PASSING**

---

## 🚀 Running Tests

### **Quick Test (Recommended):**
```bash
cd /home/founders/demoversion/symphainy_source
python3 scripts/test_insurance_agents_simple.py
```

### **Full Integration Tests:**
```bash
cd /home/founders/demoversion/symphainy_source
python3 -m pytest tests/integration/insurance_use_case/phase2_agents/test_insurance_agents.py -v
```

### **Individual Test Suites:**
```bash
# Test liaison agent guidance
python3 -c "
import asyncio
import sys
sys.path.insert(0, 'symphainy-platform')
from scripts.test_insurance_agents_simple import test_liaison_agent_guidance
asyncio.run(test_liaison_agent_guidance())
"

# Test mapper agent pattern learning
python3 -c "
import asyncio
import sys
sys.path.insert(0, 'symphainy-platform')
from scripts.test_insurance_agents_simple import test_mapper_agent_pattern_learning
asyncio.run(test_mapper_agent_pattern_learning())
"
```

---

## 📊 Test Results

### **Current Status:**
- ✅ **Simple Direct Tests:** ALL PASSING (4/4 test suites)
- ⏳ **Integration Tests:** IN PROGRESS (needs mock improvements)

### **Test Coverage:**
- **Liaison Agent:** 9/9 methods tested
- **Mapper Agent:** 8/8 core methods tested
- **Total:** 17/17 methods tested

---

## 💡 Testing Best Practices

### **1. Test Core Logic First**
Start with simple direct tests that verify core agent logic without complex dependencies.

### **2. Mock External Dependencies**
Use mocks for:
- Librarian (knowledge base)
- Canonical Model Service
- Schema Mapper Service
- MCP Client Manager

### **3. Test Error Handling**
Ensure agents handle errors gracefully:
- Missing dependencies
- Invalid input
- Service failures

### **4. Test Edge Cases**
Test:
- Empty schemas
- Missing fields
- Type mismatches
- Invalid mappings

---

## 🔄 Continuous Testing

### **Pre-Commit:**
Run simple tests before committing:
```bash
python3 scripts/test_insurance_agents_simple.py
```

### **CI/CD:**
Run full test suite:
```bash
pytest tests/integration/insurance_use_case/phase2_agents/ -v
```

---

## 📝 Adding New Tests

### **For New Agent Methods:**

1. **Add to Simple Test:**
```python
# In scripts/test_insurance_agents_simple.py
async def test_new_method():
    agent = AgentClass.__new__(AgentClass)
    agent.logger = None
    
    result = agent._new_method()
    assert result is not None
    print_result("New Method", True)
```

2. **Add to Integration Test:**
```python
# In tests/integration/insurance_use_case/phase2_agents/test_insurance_agents.py
@pytest.mark.asyncio
async def test_new_method(self, agent):
    result = await agent.new_method(...)
    assert result["success"] is True
```

---

## 🎯 Next Steps

1. ✅ **Complete Simple Tests** - DONE
2. ⏳ **Improve Integration Test Mocks** - IN PROGRESS
3. ⏳ **Add End-to-End Tests** - PENDING
4. ⏳ **Add Performance Tests** - PENDING

---

**Last Updated:** December 2024  
**Status:** ✅ **TESTING FRAMEWORK OPERATIONAL**











