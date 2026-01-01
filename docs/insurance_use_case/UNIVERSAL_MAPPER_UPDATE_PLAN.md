# UniversalMapperSpecialist Update Plan

**Date:** 2025-12-05  
**Status:** 📋 **PLAN READY**

---

## 🎯 Goal

Update `UniversalMapperSpecialist` to optimally use the new declarative pattern features, establishing it as the **complex specialist pattern template**.

---

## 📊 Current State Analysis

### **Current Configuration:**
```yaml
stateful: false
iterative_execution: false
cost_tracking: true
```

### **Current Domain Methods:**
1. `suggest_mappings()` - Suggests mappings
2. `learn_from_mappings()` - Learns patterns
3. `validate_mappings()` - Validates mappings
4. `learn_from_correction()` - Learns from corrections

### **Complexity Analysis:**

**`suggest_mappings()`:**
- **Current:** Single-pass (stateless, no iterative)
- **Could Benefit From:** Iterative execution for complex scenarios
  - Iteration 1: Initial mapping suggestions
  - Iteration 2: Validate suggestions
  - Iteration 3: Refine based on validation
  - Iteration 4: Final validation

**`validate_mappings()`:**
- **Current:** Single-pass validation
- **Could Benefit From:** Iterative execution for thorough validation
  - Iteration 1: Basic validation
  - Iteration 2: Pattern validation
  - Iteration 3: Completeness check
  - Iteration 4: Correctness verification

**`learn_from_mappings()` & `learn_from_correction()`:**
- **Current:** Single-pass learning
- **Recommendation:** Keep stateless (learning is typically one-shot)

---

## ✅ Recommended Updates

### **Option 1: Enable Iterative Execution (Recommended)**

**Update YAML:**
```yaml
# Execution configuration
iterative_execution: true  # Enable for complex mapping workflows
max_iterations: 5  # Allow multiple iterations for refinement
```

**Benefits:**
- ✅ Complex mapping scenarios can refine suggestions
- ✅ Validation can be thorough (multiple passes)
- ✅ Establishes iterative specialist pattern
- ✅ Better results for complex schemas

**Use Cases:**
- Complex schema mappings with many fields
- Mappings requiring validation and refinement
- Multi-step mapping workflows

---

### **Option 2: Keep Current (Simpler)**

**Keep YAML:**
```yaml
# Execution configuration
iterative_execution: false  # Keep simple for now
max_iterations: 5
```

**Benefits:**
- ✅ Simpler, faster
- ✅ Lower cost (fewer LLM calls)
- ✅ Good enough for most cases

**Use Cases:**
- Simple schema mappings
- Quick suggestions
- Low-complexity scenarios

---

## 🎯 Recommendation: **Option 1 (Enable Iterative)**

**Why:**
1. **Complex Specialist Template:** Establishes pattern for other complex specialists
2. **Better Results:** Iterative refinement improves mapping quality
3. **Production Ready:** We have cost controls, so iterative is safe
4. **Quick Win:** Just update YAML config (1-2 hours)

**Implementation:**
1. Update YAML config: `iterative_execution: true`
2. Update instructions to guide LLM on iterative refinement
3. Test with complex mapping scenarios
4. Document as "complex iterative specialist" pattern

---

## 📝 Update Checklist

### **1. YAML Configuration Update**
- [ ] Set `iterative_execution: true`
- [ ] Set `max_iterations: 5`
- [ ] Update instructions to mention iterative refinement
- [ ] Keep `stateful: false` (stateless is appropriate)

### **2. Instructions Update**
Add to YAML instructions:
```yaml
instructions:
  - Analyze source and target schemas carefully
  - Use semantic similarity to match fields
  - Leverage pattern learning from previous mappings when available
  - Validate mappings before returning results
  - Provide confidence scores for each mapping
  - Consider ACORD standards when relevant
  - If using iterative execution, refine mappings across iterations
  - Use tool results from previous iterations to improve suggestions
```

### **3. Testing**
- [ ] Test `suggest_mappings()` with iterative execution
- [ ] Test `validate_mappings()` with iterative execution
- [ ] Verify cost tracking works with iterations
- [ ] Verify response includes iteration metadata

### **4. Documentation**
- [ ] Document as "complex iterative specialist" pattern
- [ ] Update migration strategy with this pattern
- [ ] Create template for other complex specialists

---

## 🚀 Implementation Steps

1. **Update YAML Config** (5 minutes)
   - Change `iterative_execution: false` → `true`
   - Update instructions

2. **Test Iterative Execution** (30 minutes)
   - Run comprehensive tests
   - Verify iterations work correctly
   - Check cost tracking

3. **Document Pattern** (30 minutes)
   - Document as complex iterative specialist template
   - Update migration strategy

4. **Verify Production Readiness** (15 minutes)
   - Check all Priority 1 & 2 features
   - Verify cost controls
   - Run full test suite

**Total Time:** ~1.5 hours

---

## 📋 Pattern Template (After Update)

**Complex Iterative Specialist Pattern:**
```yaml
agent_name: MyComplexSpecialist
role: Complex Specialist Role
goal: Complex specialist goal
backstory: Complex specialist backstory

# Agent pattern configuration
stateful: false  # Stateless (no conversation history needed)
iterative_execution: true  # Enable iterative refinement
max_iterations: 5  # Allow multiple iterations

# Observability
cost_tracking: true  # Track costs

# LLM config with retry/timeout
llm_config:
  model: gpt-4o-mini
  temperature: 0.3
  max_tokens: 2000
  timeout: 120
  retry:
    enabled: true
    max_attempts: 3
    base_delay: 2.0
```

---

## ✅ Success Criteria

**Update Complete When:**
- ✅ YAML config updated with `iterative_execution: true`
- ✅ Instructions updated for iterative refinement
- ✅ Tests passing (100%)
- ✅ Cost tracking verified for iterations
- ✅ Pattern documented as template
- ✅ Production ready

---

## 🎉 Next Steps After Update

1. **Use as Template:** Reference for other complex specialists
2. **Migrate Phase 1:** Stateless specialist, Stateful guide/liaison
3. **Proceed with Remaining:** Use established patterns

---

## 💡 Key Insight

**UniversalMapperSpecialist is perfect for iterative execution because:**
- Mapping suggestions can be refined
- Validation can be thorough (multiple passes)
- Complex schemas benefit from iterative refinement
- Establishes pattern for other complex specialists

**This update gives us:**
- ✅ Quick win (1-2 hours)
- ✅ Complex specialist pattern template
- ✅ Better mapping results
- ✅ Production-ready example







