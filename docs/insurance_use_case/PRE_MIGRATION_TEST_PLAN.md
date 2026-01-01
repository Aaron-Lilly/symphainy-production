# Pre-Migration Test Plan - 4 Declarative Agents

**Date:** 2025-12-06  
**Status:** ⏳ **READY FOR TESTING**

---

## 🎯 Objective

Verify that all 4 declarative agents are production-ready after the flat structure migration before proceeding with migrating the remaining agents.

---

## 📋 Test Scripts

### **1. Stateless Specialist Pattern**
**Test Script:** `scripts/insurance_use_case/test_stateless_specialist_pattern.py`  
**Agent:** `RecommendationSpecialist`  
**Pattern:** Stateless (no conversation history, single-pass execution)

**Tests:**
- ✅ Agent initialization and config verification
- ✅ Simple recommendation request
- ✅ Stateless behavior verification (no conversation history)
- ✅ Cost tracking verification
- ✅ Independent request (stateless)

**Expected Results:**
- Agent initializes successfully
- Config loads correctly (`stateful: false`, `iterative_execution: false`)
- Recommendations generated successfully
- No conversation history maintained
- Cost tracking working

---

### **2. Iterative Specialist Pattern**
**Test Script:** `scripts/insurance_use_case/test_iterative_specialist_pattern.py`  
**Agent:** `UniversalMapperSpecialist`  
**Pattern:** Iterative (stateless, but uses iterative execution with tool feedback loops)

**Tests:**
- ✅ Agent initialization and config verification
- ✅ Simple mapping request
- ✅ Iterative execution verification
- ✅ Stateless behavior (no conversation history, but iterative)
- ✅ Cost tracking

**Expected Results:**
- Agent initializes successfully
- Config loads correctly (`stateful: false`, `iterative_execution: true`)
- Mappings generated successfully
- Iterative execution working (multiple LLM calls)
- Cost tracking shows iteration costs

---

### **3. Stateful Conversational Pattern**
**Test Script:** `scripts/insurance_use_case/test_stateful_conversational_pattern.py`  
**Agent:** `InsuranceLiaisonAgent`  
**Pattern:** Stateful Conversational (maintains conversation history, single-pass)

**Tests:**
- ✅ Agent initialization and config verification
- ✅ Simple conversational request
- ✅ Stateful behavior (conversation history)
- ✅ Multi-turn conversation
- ✅ Cost tracking

**Expected Results:**
- Agent initializes successfully
- Config loads correctly (`stateful: true`, `iterative_execution: false`)
- Conversational responses generated
- Conversation history maintained across requests
- History grows with each interaction
- Cost tracking working

---

### **4. Guide Agent Pattern**
**Test Script:** `scripts/insurance_use_case/test_guide_agent_pattern.py`  
**Agent:** `GuideCrossDomainAgent`  
**Pattern:** Guide Agent (stateful, cross-domain navigation)

**Tests:**
- ✅ Agent initialization and config verification
- ✅ Simple cross-domain request
- ✅ Cross-domain intent understanding
- ✅ Stateful behavior (conversation history)
- ✅ Cost tracking

**Expected Results:**
- Agent initializes successfully
- Config loads correctly (`stateful: true`, `iterative_execution: false`)
- Solution configuration loaded (MVP domains)
- Cross-domain navigation working
- Conversation history maintained
- Cost tracking working

---

## 🔧 Test Configuration

**Environment:** PRODUCTION (`http://35.215.64.103`)  
**LLM Model:** `gpt-4o-mini` (cheapest model)  
**Cost Controls:** Enabled (max $1.00 per test)  
**Response Caching:** Enabled  
**Traefik:** Optional in test mode

---

## ✅ Success Criteria

All tests must pass:
- ✅ All 4 agents initialize successfully
- ✅ All configs load correctly
- ✅ All agents respond to requests
- ✅ Pattern-specific features work (stateful, iterative, stateless)
- ✅ Cost tracking working
- ✅ No import errors
- ✅ No runtime errors

---

## 🚀 Test Execution Order

1. **Stateless Specialist** (easiest - single LLM call)
2. **Iterative Specialist** (moderate - multiple LLM calls)
3. **Stateful Conversational** (moderate - conversation history)
4. **Guide Agent** (most complex - cross-domain navigation)

---

## 📊 Expected Test Results Summary

| Agent | Pattern | Tests | Expected Pass Rate |
|-------|---------|-------|-------------------|
| `RecommendationSpecialist` | Stateless | 4 | 100% |
| `UniversalMapperSpecialist` | Iterative | 5 | 100% |
| `InsuranceLiaisonAgent` | Stateful | 5 | 100% |
| `GuideCrossDomainAgent` | Guide | 5 | 100% |

**Total:** 19 tests, 100% pass rate expected

---

## 🎯 Next Steps After Testing

1. ✅ **If all tests pass:** Proceed with migrating remaining agents
2. ❌ **If any tests fail:** Fix issues before proceeding
3. 📝 **Document results:** Update this document with test results

---

## 📝 Notes

- All test scripts have been updated with new import paths (flat structure)
- Tests use production environment to ensure fixes actually work
- Cost controls prevent budget overruns during testing
- Response caching reduces API costs







