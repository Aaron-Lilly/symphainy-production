# LLM Abstraction Review & Enhancement

**Date:** January 15, 2025  
**Purpose:** Review LLM abstraction/adapter for Phase 5 requirements and identify needed enhancements

---

## 🔍 **Current State Analysis**

### **LLM Abstraction Architecture:**

1. **LLMAbstraction** (`foundations/public_works_foundation/infrastructure_abstractions/llm_abstraction.py`)
   - Primary method: `generate_response(request: LLMRequest) -> LLMResponse`
   - Uses `LLMRequest` and `LLMResponse` dataclasses
   - Supports multiple providers (OpenAI, Anthropic, Ollama)
   - Has retry logic, timeout handling, rate limiting
   - ✅ **Well-structured and production-ready**

2. **LLMProtocol** (`foundations/public_works_foundation/abstraction_contracts/llm_protocol.py`)
   - Defines `LLMRequest` and `LLMResponse` dataclasses
   - `LLMRequest`: messages, model, max_tokens, temperature, stream, metadata
   - `LLMResponse`: response_id, model, content, usage, finish_reason, metadata
   - ✅ **Clear contract definition**

3. **AgentBase._call_llm_with_tracking()**
   - Wrapper method for agentic correlation tracking
   - Takes `prompt: str` and `llm_call_func` (async function)
   - Expects function that takes prompt and returns dict/response
   - ✅ **Good pattern for tracking**

### **Issue Identified:**

**Problem:** Agents are calling `llm_abstraction.analyze_text()` which **doesn't exist**.

**Current Agent Code Pattern:**
```python
async def _call_llm(prompt_text, **kwargs):
    llm_abstraction = await self.get_business_abstraction("llm")
    if llm_abstraction:
        return await llm_abstraction.analyze_text(  # ❌ This method doesn't exist!
            text=prompt_text,
            analysis_type="business_insights",
            **kwargs
        )
```

**Correct Pattern:**
```python
from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel

request = LLMRequest(
    messages=[{"role": "user", "content": prompt}],
    model=LLMModel.GPT_4O_MINI
)
response = await llm_abstraction.generate_response(request)
# response.content contains the text
```

---

## 💡 **Recommended Solution: Add Helper Method to AgentBase**

### **Option 1: Add `_call_llm_simple()` Helper Method (Recommended)**

Add a helper method to `AgentBase` that wraps the `LLMRequest`/`LLMResponse` pattern:

**File:** `foundations/agentic_foundation/agent_sdk/agent_base.py`

```python
async def _call_llm_simple(
    self,
    prompt: str,
    system_message: Optional[str] = None,
    model: Optional[LLMModel] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    user_context: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Simple LLM call helper for agents.
    
    Wraps LLMRequest/LLMResponse pattern into a simple interface.
    Uses _call_llm_with_tracking for agentic correlation.
    
    Args:
        prompt: User prompt
        system_message: Optional system message
        model: Optional model (defaults to GPT_4O_MINI)
        max_tokens: Optional max tokens
        temperature: Optional temperature
        user_context: Optional user context
        metadata: Optional metadata
    
    Returns:
        Response text (str)
    """
    from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
    
    # Get LLM abstraction
    llm_abstraction = await self.get_business_abstraction("llm")
    if not llm_abstraction:
        raise ValueError("LLM abstraction not available")
    
    # Build messages
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})
    
    # Create LLM request
    request = LLMRequest(
        messages=messages,
        model=model or LLMModel.GPT_4O_MINI,
        max_tokens=max_tokens,
        temperature=temperature,
        metadata=metadata or {}
    )
    
    # Call LLM with tracking
    async def _call_llm_func(prompt_text, **kwargs):
        response = await llm_abstraction.generate_response(request)
        return {
            "text": response.content,
            "tokens": response.usage,
            "cost": self._estimate_cost(response.usage, model or LLMModel.GPT_4O_MINI),
            "response": response.content
        }
    
    result = await self._call_llm_with_tracking(
        prompt=prompt,
        llm_call_func=_call_llm_func,
        model_name=(model or LLMModel.GPT_4O_MINI).value,
        user_context=user_context,
        metadata=metadata
    )
    
    return result.get("text", result.get("response", ""))
```

### **Option 2: Add to BusinessAbstractionHelper**

Add helper method to `BusinessAbstractionHelper` for LLM calls:

**File:** `foundations/agentic_foundation/agent_sdk/business_abstraction_helper.py`

```python
async def call_llm_simple(
    self,
    prompt: str,
    system_message: Optional[str] = None,
    model: Optional[LLMModel] = None,
    **kwargs
) -> str:
    """Simple LLM call helper."""
    llm_abstraction = await self.get_abstraction("llm")
    if not llm_abstraction:
        raise ValueError("LLM abstraction not available")
    
    # Build LLMRequest and call generate_response
    # Return response.content
```

---

## 🔧 **Required Updates**

### **1. Update Agent Code to Use Correct Pattern**

**Files to Update:**
- `insights_business_analysis_agent.py` - Update `_interpret_eda_results_with_llm()`
- `insights_query_agent.py` - Update `_generate_query_spec_with_llm()`
- `insights_liaison_agent.py` - Update all LLM call methods

**Current (Incorrect):**
```python
return await llm_abstraction.analyze_text(text=prompt_text, ...)
```

**Updated (Correct):**
```python
from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel

request = LLMRequest(
    messages=[{"role": "system", "content": system_message}, {"role": "user", "content": prompt}],
    model=LLMModel.GPT_4O_MINI
)
response = await llm_abstraction.generate_response(request)
return response.content
```

### **2. Add Helper Method to AgentBase (Recommended)**

Add `_call_llm_simple()` method to `AgentBase` to simplify LLM calls for agents.

**Benefits:**
- ✅ Consistent pattern across all agents
- ✅ Automatic agentic correlation tracking
- ✅ Simplified interface (no need to construct LLMRequest manually)
- ✅ Handles LLMResponse extraction automatically

### **3. Update _call_llm_with_tracking to Handle LLMResponse**

The `_call_llm_with_tracking` method expects a dict response, but `generate_response` returns `LLMResponse`. We need to ensure compatibility.

**Current:**
```python
response = await llm_call_func(prompt, **kwargs)
tokens = response.get("tokens", {})  # Expects dict
```

**Should Handle:**
```python
# If LLMResponse, extract to dict
if hasattr(response, 'content'):
    response = {
        "text": response.content,
        "tokens": response.usage,
        "response": response.content
    }
```

---

## ✅ **Assessment: What's Working Well**

1. **LLM Abstraction Structure:**
   - ✅ Clean separation: Protocol → Abstraction → Adapter
   - ✅ Provider switching works correctly
   - ✅ Retry logic and timeout handling
   - ✅ Rate limiting support

2. **LLMRequest/LLMResponse Pattern:**
   - ✅ Well-defined dataclasses
   - ✅ Supports all necessary fields
   - ✅ Type-safe

3. **Agentic Correlation:**
   - ✅ `_call_llm_with_tracking` provides automatic tracking
   - ✅ Integrates with Nurse, Post Office, Conductor

---

## 🚨 **Issues to Fix**

### **Issue 1: Missing `analyze_text()` Method**

**Problem:** Agents call `llm_abstraction.analyze_text()` which doesn't exist.

**Solution:** 
- Add `_call_llm_simple()` helper to `AgentBase`
- Update all agent code to use correct pattern

### **Issue 2: Response Format Mismatch**

**Problem:** `_call_llm_with_tracking` expects dict, but `generate_response` returns `LLMResponse`.

**Solution:**
- Update `_call_llm_with_tracking` to handle both dict and LLMResponse
- Or ensure wrapper functions convert LLMResponse to dict

### **Issue 3: Token/Cost Extraction**

**Problem:** `_call_llm_with_tracking` tries to extract tokens/cost from response, but format may vary.

**Solution:**
- Standardize response format in wrapper functions
- Extract from `LLMResponse.usage` correctly

---

## 📋 **Implementation Plan**

### **Step 1: Add Helper Method to AgentBase**

Add `_call_llm_simple()` method that:
- Takes simple parameters (prompt, system_message, model)
- Constructs LLMRequest internally
- Calls `generate_response()`
- Uses `_call_llm_with_tracking()` for correlation
- Returns response text (str)

### **Step 2: Update Agent Code**

Update all agents to use `_call_llm_simple()`:
- `InsightsBusinessAnalysisAgent._interpret_eda_results_with_llm()`
- `InsightsQueryAgent._generate_query_spec_with_llm()`
- `InsightsLiaisonAgent._understand_user_intent()`
- `InsightsLiaisonAgent._generate_visualization_spec_from_nl()`
- `InsightsLiaisonAgent._extract_filter_criteria()`

### **Step 3: Enhance _call_llm_with_tracking**

Update to handle `LLMResponse` objects:
- Check if response is LLMResponse
- Extract content, usage, etc. correctly
- Convert to dict format for tracking

---

## 🎯 **Recommendation**

**Add `_call_llm_simple()` helper method to AgentBase** to provide a simple, consistent interface for agents to call LLM.

**Benefits:**
- ✅ Simplifies agent code (no need to construct LLMRequest manually)
- ✅ Consistent pattern across all agents
- ✅ Automatic agentic correlation tracking
- ✅ Handles LLMResponse extraction automatically
- ✅ Backward compatible (agents can still use generate_response directly if needed)

**Alternative:** If we want to keep AgentBase minimal, add helper to `BusinessAbstractionHelper` instead.

---

## 📝 **Next Steps**

1. ✅ Review complete
2. ⏸️ Add `_call_llm_simple()` helper method
3. ⏸️ Update agent code to use helper
4. ⏸️ Test with real LLM calls
5. ⏸️ Verify agentic correlation tracking works

