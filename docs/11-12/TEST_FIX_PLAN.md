# Test Fix Plan - Tomorrow's Attack Strategy

**Date**: November 13, 2025  
**Current Status**: 64.5% pass rate (120/186 tests passing)

---

## 📊 Current Status Summary

### ✅ What's Working (100% Pass Rate)
- **Platform Gateway** (18/18 tests) - Perfect! ✅
- **GCS File Adapter** (5/5 tests)
- **Supabase Metadata Adapter** (5/5 tests)
- **Redis State Adapter** (5/5 tests)
- **Redis Graph Adapter** (2/2 tests)
- **OpenTelemetry Adapter** (3/3 tests)
- **Tempo Adapter** (5/5 tests)
- **Auth Abstraction** (3/3 tests)
- **Messaging Abstraction** (3/3 tests)
- **Event Management Abstraction** (3/3 tests)
- **Cache Abstraction** (4/4 tests)
- **Knowledge Discovery Abstraction** (2/2 tests)
- **Content Schema Abstraction** (3/3 tests)
- **Content Insights Abstraction** (3/3 tests)
- **File Parser Service** (8/8 tests)
- **Format Composer Service** (7/7 tests)
- **Content Analysis Orchestrator** (7/7 tests)

### ⚠️ What Needs Fixing

**Critical Issues (0% pass rate):**
- **MCP Servers** (0/10 tests) - Abstract class instantiation
- **Agents** (0/5 tests) - Abstract class instantiation

**High Priority (Partial failures):**
- **Infrastructure Adapters** (32/55 tests) - 58% pass rate
- **Orchestrators** (14/21 tests) - 67% pass rate
- **Enabling Services** (27/35 tests) - 77% pass rate

---

## 🎯 Attack Plan (Prioritized)

### Phase 1: Quick Wins (30-60 minutes)
**Goal**: Fix simple type errors and parameter mismatches

#### 1.1 Fix Type Errors in Abstractions (6 failures)
- ✅ **File Management Abstraction** - Fix async/await on MagicMock
- ✅ **Session Abstraction** - Fix SessionContext parameter mismatch
- ✅ **Telemetry Abstraction** - Fix TelemetryData missing required parameter
- ✅ **Task Management Abstraction** - Fix TaskStatus subscriptable issue
- ✅ **LLM Abstraction** - Fix LLMRequest parameter mismatch

**Estimated Time**: 30 minutes  
**Impact**: +6 tests passing

#### 1.2 Fix Type Errors in Enabling Services (8 failures)
- ✅ **Data Analyzer Service** - Fix `detect_domain()` and `assess_complexity()` parameter mismatches
- ✅ **Roadmap Generation Service** - Fix `create_comprehensive_strategic_plan()` parameter mismatch
- ✅ **POC Generation Service** - Fix `generate_poc_roadmap()` parameter mismatch

**Estimated Time**: 30 minutes  
**Impact**: +8 tests passing

#### 1.3 Fix Type Errors in Orchestrators (7 failures)
- ✅ **Business Outcomes Orchestrator** - Fix parameter mismatches
- ✅ **Insights Orchestrator** - Fix `analyze_content_for_insights()` parameter mismatch
- ✅ **Operations Orchestrator** - Fix `generate_workflow_from_sop()` parameter mismatch and missing attribute

**Estimated Time**: 30 minutes  
**Impact**: +7 tests passing

**Phase 1 Total**: ~90 minutes, +21 tests passing → **~75% pass rate**

---

### Phase 2: Abstract Class Issues (60-90 minutes)
**Goal**: Fix MCP Server and Agent abstract class instantiation

#### 2.1 Fix MCP Server Tests (4 failures)
**Issue**: `Can't instantiate abstract class XMCPServer`

**Root Cause**: MCP Servers likely inherit from abstract base classes that require specific implementations.

**Solution**:
1. Check actual MCP Server base classes
2. Mock the abstract methods properly
3. Use `unittest.mock.patch` to mock abstract base class requirements
4. Or create concrete test implementations

**Files to Fix**:
- `test_business_outcomes_mcp_server.py`
- `test_content_analysis_mcp_server.py`
- `test_insights_mcp_server.py`
- `test_operations_mcp_server.py`

**Estimated Time**: 60 minutes  
**Impact**: +10 tests passing

#### 2.2 Fix Agent Tests (4 failures)
**Issue**: `Can't instantiate abstract class XSpecialistAgent`

**Root Cause**: Similar to MCP Servers - agents inherit from abstract base classes.

**Solution**:
1. Check actual Agent base classes
2. Mock abstract methods
3. Use proper test fixtures that provide required dependencies

**Files to Fix**:
- `test_business_outcomes_specialist_agent.py`
- `test_insights_specialist_agent.py`
- `test_content_processing_agent.py`
- `test_operations_specialist_agent.py`

**Estimated Time**: 30 minutes  
**Impact**: +5 tests passing

**Phase 2 Total**: ~90 minutes, +15 tests passing → **~85% pass rate**

---

### Phase 3: Infrastructure Adapter Issues (90-120 minutes)
**Goal**: Fix remaining adapter test failures

#### 3.1 Fix Import Errors (3 failures)
- ✅ **Supabase Adapter** - Fix import errors
- ✅ **ArangoDB Adapter** - Fix import errors
- ✅ **Meilisearch Knowledge Adapter** - Fix import errors

**Estimated Time**: 30 minutes  
**Impact**: +10 tests passing

#### 3.2 Fix Type/Attribute Errors (5 failures)
- ✅ **Supabase File Management Adapter** - Fix type/attribute errors (6 failures)
- ✅ **Redis Adapter** - Fix type/attribute errors (6 failures)
- ✅ **Redis Session Adapter** - Fix SessionContext parameter issues (2 failures)
- ✅ **Redis Event Bus Adapter** - Fix initialization/attribute errors (1 failure)
- ✅ **Celery Adapter** - Fix async/await and attribute errors (2 failures)

**Estimated Time**: 60 minutes  
**Impact**: +17 tests passing

**Phase 3 Total**: ~90 minutes, +27 tests passing → **~95% pass rate**

---

## 📋 Detailed Fix Checklist

### Phase 1: Quick Wins

#### File Management Abstraction
- [ ] Fix `MagicMock` async/await issue in `test_create_file`
- [ ] Fix `MagicMock` async/await issue in `test_retrieve_file`

#### Session Abstraction
- [ ] Fix `SessionContext.__init__()` parameter mismatch
- [ ] Check actual SessionContext signature

#### Telemetry Abstraction
- [ ] Fix `TelemetryData.__init__()` missing required parameter
- [ ] Check actual TelemetryData signature

#### Task Management Abstraction
- [ ] Fix `TaskStatus` subscriptable issue
- [ ] Check if TaskStatus is an Enum


#### Data Analyzer Service
- [ ] Fix `detect_domain()` parameter mismatch
- [ ] Fix `assess_complexity()` parameter mismatch

#### Roadmap Generation Service
- [ ] Fix `create_comprehensive_strategic_plan()` parameter mismatch

#### POC Generation Service
- [ ] Fix `generate_poc_roadmap()` parameter mismatch

#### Orchestrators
- [ ] Fix Business Outcomes Orchestrator parameter mismatches
- [ ] Fix Insights Orchestrator `analyze_content_for_insights()` parameter
- [ ] Fix Operations Orchestrator `generate_workflow_from_sop()` parameter and missing attribute

---

### Phase 2: Abstract Classes

#### MCP Servers
- [ ] Check MCP Server base class structure
- [ ] Create proper mocks for abstract methods
- [ ] Fix Business Outcomes MCP Server
- [ ] Fix Content Analysis MCP Server
- [ ] Fix Insights MCP Server
- [ ] Fix Operations MCP Server

#### Agents
- [ ] Check Agent base class structure
- [ ] Create proper mocks for abstract methods
- [ ] Fix Business Outcomes Specialist Agent
- [ ] Fix Insights Specialist Agent
- [ ] Fix Content Processing Agent
- [ ] Fix Operations Specialist Agent

---

### Phase 3: Infrastructure Adapters

#### Import Errors
- [ ] Fix Supabase Adapter imports
- [ ] Fix ArangoDB Adapter imports
- [ ] Fix Meilisearch Knowledge Adapter imports

#### Type/Attribute Errors
- [ ] Fix Supabase File Management Adapter (6 failures)
- [ ] Fix Redis Adapter (6 failures)
- [ ] Fix Redis Session Adapter (2 failures)
- [ ] Fix Redis Event Bus Adapter (1 failure)
- [ ] Fix Celery Adapter (2 failures)

---

## 🎯 Success Metrics

### Target Goals
- **Phase 1 Complete**: 75% pass rate (141/186 tests)
- **Phase 2 Complete**: 85% pass rate (156/186 tests)
- **Phase 3 Complete**: 95% pass rate (177/186 tests)

### Time Estimates
- **Phase 1**: 90 minutes
- **Phase 2**: 90 minutes
- **Phase 3**: 90 minutes
- **Total**: ~4.5 hours

---

## 🔍 Investigation Needed

Before starting, investigate:

1. **Abstract Base Classes**
   - Check actual MCP Server base classes
   - Check actual Agent base classes
   - Understand what methods need to be implemented/mocked

2. **Protocol/Interface Signatures**
   - Check actual SessionContext signature
   - Check actual TelemetryData signature
   - Check actual LLMRequest signature
   - Check actual TaskStatus type

3. **Import Paths**
   - Verify all import paths are correct
   - Check if any modules moved or were renamed

---

## 💡 Quick Reference

### Common Fix Patterns

#### Fix Parameter Mismatches
```python
# Check actual method signature
# Update test to match actual signature
```

#### Fix Abstract Class Instantiation
```python
# Option 1: Mock abstract methods
@patch.object(AbstractBaseClass, 'abstract_method', return_value=mock_value)

# Option 2: Create concrete test class
class TestConcreteClass(AbstractBaseClass):
    def abstract_method(self):
        return mock_value
```

#### Fix Async/Await Issues
```python
# Use AsyncMock instead of MagicMock for async methods
from unittest.mock import AsyncMock
mock_method = AsyncMock(return_value=value)
```

#### Fix Import Errors
```python
# Check actual module paths
# Use relative imports if needed
# Verify __init__.py files exist
```

---

## 🚀 Execution Order

1. **Start with Phase 1** - Quick wins boost morale and show progress
2. **Move to Phase 2** - Abstract classes are blocking all MCP/Agent tests
3. **Finish with Phase 3** - Infrastructure adapters are less critical but important

---

## 📝 Notes

- Most failures are **type/parameter mismatches** - easy fixes
- Abstract class issues are **systematic** - fix pattern once, apply to all
- Import errors are **isolated** - fix one at a time
- **Platform Gateway is perfect** - use as reference for patterns

---

**Good luck tomorrow!** 🎯

