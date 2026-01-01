# Declarative Agent Production Gaps - Implementation Plan

**Date:** 2025-12-05  
**Status:** 📋 **PLANNING**

---

## Strategic Framework Alignment

### Platform Architecture Principles

1. **Support Both Stateful and Stateless Patterns**
   - Stateful: Full `AgentBase` with conversation history, session management
   - Stateless: Lightweight declarative agents for simple operations
   - Agents choose their pattern based on needs

2. **Consistent Baseline (Always Present)**
   - Audit logging (security)
   - Telemetry tracking (observability)
   - Error handling (resilience)
   - Multi-tenancy support (isolation)

3. **Optional Capabilities (Opt-In)**
   - Retry logic (configurable)
   - Timeout handling (configurable)
   - Rate limiting (configurable)
   - Conversation history (stateful only)
   - Tool result feedback loops (iterative execution)
   - Cost tracking (observability)

4. **No Over-Burdening**
   - Unlike CrewAI, don't force all agents to have all capabilities
   - Make features configurable via YAML config
   - Lightweight defaults for stateless agents
   - Full capabilities for stateful agents

---

## Implementation Strategy

### Layer 1: Infrastructure Layer (LLM Abstraction)

**Location:** `foundations/public_works_foundation/infrastructure_abstractions/llm_abstraction.py`

**Responsibility:** Provide retry, timeout, and rate limiting at the infrastructure level (shared by all LLM consumers)

**Changes:**
- Add retry logic with exponential backoff
- Add timeout handling
- Add rate limiting (token bucket or sliding window)
- Make all configurable via environment/config

**Benefits:**
- All LLM consumers benefit (agents, services, etc.)
- Consistent behavior across platform
- Centralized configuration

---

### Layer 2: Agent SDK Layer (AgentBase)

**Location:** `foundations/agentic_foundation/agent_sdk/agent_base.py`

**Responsibility:** Provide optional agent capabilities that agents can opt into

**Changes:**
- Add optional conversation history management (stateful pattern)
- Add optional iterative execution (tool feedback loops)
- Add optional cost tracking
- Keep baseline capabilities (audit, telemetry, error handling)

**Benefits:**
- Agents choose what they need
- Stateless agents stay lightweight
- Stateful agents get full capabilities

---

### Layer 3: Declarative Agent Layer (DeclarativeAgentBase)

**Location:** `backend/business_enablement/agents/declarative_agent_base.py`

**Responsibility:** Configuration-driven agent with optional production capabilities

**Changes:**
- Add configuration options for retry, timeout, rate limiting
- Add configuration for stateful vs stateless pattern
- Add configuration for iterative execution
- Improve JSON parsing robustness
- Add cost tracking integration

**Benefits:**
- YAML-driven configuration
- Easy to enable/disable features
- Consistent with declarative pattern

---

## Detailed Implementation Plan

### Priority 1: Critical Production Gaps (Must Fix)

#### 1.1 LLM Retry Logic with Exponential Backoff

**Location:** `foundations/public_works_foundation/infrastructure_abstractions/llm_abstraction.py`

**Implementation:**
```python
class LLMAbstraction:
    async def generate_response(
        self, 
        request: LLMRequest,
        retry_config: Optional[RetryConfig] = None
    ) -> LLMResponse:
        """
        Generate LLM response with retry logic.
        
        Args:
            request: LLM request
            retry_config: Optional retry configuration (uses defaults if not provided)
        """
        retry_config = retry_config or self._get_default_retry_config()
        
        for attempt in range(retry_config.max_attempts):
            try:
                response = await self._call_llm_provider(request)
                return response
            except (RateLimitError, TimeoutError, ConnectionError) as e:
                if attempt < retry_config.max_attempts - 1:
                    delay = retry_config.base_delay * (2 ** attempt)  # Exponential backoff
                    await asyncio.sleep(delay)
                    continue
                raise
            except (ValueError, AuthenticationError) as e:
                # Non-retryable errors
                raise
```

**Configuration:**
```yaml
# In agent YAML config
llm_config:
  model: "gpt-4o-mini"
  max_tokens: 2000
  temperature: 0.3
  retry:
    enabled: true
    max_attempts: 3
    base_delay: 2.0  # seconds
    retryable_errors: ["rate_limit", "timeout", "connection"]
```

**Benefits:**
- Handles transient failures gracefully
- Configurable per agent
- Exponential backoff prevents API hammering

---

#### 1.2 Timeout Handling

**Location:** `foundations/public_works_foundation/infrastructure_abstractions/llm_abstraction.py`

**Implementation:**
```python
class LLMAbstraction:
    async def generate_response(
        self,
        request: LLMRequest,
        timeout: Optional[float] = None
    ) -> LLMResponse:
        """
        Generate LLM response with timeout.
        
        Args:
            request: LLM request
            timeout: Optional timeout in seconds (uses config default if not provided)
        """
        timeout = timeout or self._get_default_timeout()
        
        try:
            response = await asyncio.wait_for(
                self._call_llm_provider(request),
                timeout=timeout
            )
            return response
        except asyncio.TimeoutError:
            raise TimeoutError(f"LLM request timed out after {timeout}s")
```

**Configuration:**
```yaml
# In agent YAML config
llm_config:
  timeout: 120  # seconds
```

**Benefits:**
- Prevents hanging requests
- Configurable per agent
- Resource protection

---

#### 1.3 Rate Limiting

**Location:** `foundations/public_works_foundation/infrastructure_abstractions/llm_rate_limiting_abstraction.py`

**Implementation:**
```python
class LLMRateLimitingAbstraction:
    def __init__(self, config: Dict[str, Any]):
        self.rate_limiter = TokenBucket(
            capacity=config.get("rate_limit_capacity", 100),
            refill_rate=config.get("rate_limit_refill_rate", 10)  # per second
        )
    
    async def acquire(self, tokens: int = 1) -> bool:
        """Acquire tokens for LLM request."""
        return await self.rate_limiter.acquire(tokens)
```

**Integration:**
```python
# In LLMAbstraction.generate_response()
if self.rate_limiting_enabled:
    await self.rate_limiter.acquire()
    response = await self._call_llm_provider(request)
```

**Configuration:**
```yaml
# In agent YAML config
llm_config:
  rate_limiting:
    enabled: true
    capacity: 100
    refill_rate: 10  # tokens per second
```

**Benefits:**
- Prevents API rate limit violations
- Configurable per agent
- Protects against cost spikes

---

#### 1.4 Robust JSON Parsing

**Location:** `backend/business_enablement/agents/declarative_agent_base.py`

**Implementation:**
```python
def _parse_llm_response_json(self, content: str) -> Dict[str, Any]:
    """
    Parse LLM response JSON with multiple fallback strategies.
    
    Strategies:
    1. Direct JSON parsing
    2. Extract JSON from markdown code blocks
    3. Extract JSON from text (regex with validation)
    4. Fallback to structured text response
    """
    # Strategy 1: Direct JSON parsing
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Extract from markdown code blocks
    import re
    json_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_block_match:
        try:
            return json.loads(json_block_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Strategy 3: Extract JSON from text (with validation)
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group())
            # Validate structure
            if self._validate_json_structure(parsed):
                return parsed
        except json.JSONDecodeError:
            pass
    
    # Strategy 4: Fallback to structured text response
    return {
        "reasoning": content,
        "tool_calls": [],
        "response": content
    }
```

**Benefits:**
- Handles various LLM response formats
- Multiple fallback strategies
- Validates JSON structure

---

### Priority 2: Important Production Features (Should Fix)

#### 2.1 Multi-Turn Conversation Support (Stateful Pattern)

**Location:** `backend/business_enablement/agents/declarative_agent_base.py`

**Implementation:**
```python
class DeclarativeAgentBase(AgentBase):
    def __init__(self, ...):
        # ... existing init ...
        
        # Conversation state (optional, for stateful agents)
        self.conversation_history: List[Dict[str, Any]] = []
        self.max_conversation_history = self.agent_config.get("max_conversation_history", 10)
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process request with optional conversation history."""
        # Add conversation history to request if stateful
        if self.agent_config.get("stateful", False):
            request["conversation_history"] = self.conversation_history[-self.max_conversation_history:]
        
        # Process request
        response = await self._process_with_llm(request)
        
        # Update conversation history if stateful
        if self.agent_config.get("stateful", False):
            self.conversation_history.append({
                "role": "user",
                "content": request.get("message", ""),
                "timestamp": datetime.now().isoformat()
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": response.get("response", ""),
                "timestamp": datetime.now().isoformat()
            })
        
        return response
    
    def _build_agent_prompt(self, request: Dict[str, Any]) -> str:
        """Build prompt with conversation history if stateful."""
        prompt = f"""You are a {self.role}..."""
        
        # Add conversation history if stateful
        if self.agent_config.get("stateful", False):
            conversation_history = request.get("conversation_history", [])
            if conversation_history:
                prompt += "\n\nConversation History:\n"
                for msg in conversation_history:
                    prompt += f"{msg['role']}: {msg['content']}\n"
        
        return prompt
```

**Configuration:**
```yaml
# In agent YAML config
agent_name: "UniversalMapperSpecialist"
stateful: true  # Enable conversation history
max_conversation_history: 10  # Keep last 10 messages
```

**Benefits:**
- Optional feature (stateless agents don't pay cost)
- Configurable per agent
- Maintains context across requests

---

#### 2.2 Tool Result Feedback Loops (Iterative Execution)

**Location:** `backend/business_enablement/agents/declarative_agent_base.py`

**Implementation:**
```python
async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Process request with optional iterative execution."""
    max_iterations = self.agent_config.get("max_iterations", 1)
    enable_iterative = self.agent_config.get("iterative_execution", False)
    
    if not enable_iterative:
        # Single-pass execution (current behavior)
        return await self._process_single_pass(request)
    
    # Iterative execution (plan → execute → evaluate → replan)
    tool_results_history = []
    for iteration in range(max_iterations):
        # Build prompt with tool results from previous iterations
        prompt = self._build_agent_prompt(request, tool_results_history)
        
        # Get LLM response
        llm_response = await self._call_llm_with_retry(prompt)
        tool_calls = self._extract_tool_calls_from_llm_response(llm_response)
        
        if not tool_calls:
            # Agent is done
            break
        
        # Execute tools
        tool_results = await self._execute_tools(tool_calls, request)
        tool_results_history.append({
            "iteration": iteration,
            "tool_calls": tool_calls,
            "tool_results": tool_results
        })
    
    return self._format_response(llm_response, tool_results_history, request)
```

**Configuration:**
```yaml
# In agent YAML config
iterative_execution: true  # Enable iterative execution
max_iterations: 5  # Maximum iterations
```

**Benefits:**
- Optional feature (simple agents stay simple)
- Enables sophisticated reasoning
- Configurable per agent

---

#### 2.3 Cost Tracking

**Location:** `backend/business_enablement/agents/declarative_agent_base.py`

**Implementation:**
```python
async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Process request with cost tracking."""
    # ... existing code ...
    
    llm_response = await self.llm_abstraction.generate_response(llm_request)
    
    # Track costs if enabled
    if self.agent_config.get("cost_tracking", True):
        cost = self._calculate_llm_cost(llm_response)
        await self._record_cost_metric(cost, request)
    
    # ... rest of processing ...
```

**Cost Calculation:**
```python
def _calculate_llm_cost(self, llm_response: LLMResponse) -> float:
    """Calculate LLM cost based on token usage and model pricing."""
    model = llm_response.model
    prompt_tokens = llm_response.usage.prompt_tokens
    completion_tokens = llm_response.usage.completion_tokens
    
    # Get model pricing from config
    pricing = self._get_model_pricing(model)
    cost = (prompt_tokens * pricing["prompt_cost_per_1k"] / 1000) + \
           (completion_tokens * pricing["completion_cost_per_1k"] / 1000)
    
    return cost
```

**Configuration:**
```yaml
# In agent YAML config
cost_tracking: true  # Enable cost tracking
```

**Benefits:**
- Visibility into LLM costs
- Optional feature
- Telemetry integration

---

## SDK Updates

### AgentBase Enhancements

**Location:** `foundations/agentic_foundation/agent_sdk/agent_base.py`

**Changes:**
1. Add optional conversation history management methods
2. Add optional cost tracking methods
3. Keep baseline capabilities (audit, telemetry, error handling)

**New Methods:**
```python
class AgentBase(ABC, TenantProtocol):
    # Optional: Conversation history (stateful pattern)
    async def add_to_conversation_history(self, role: str, content: str):
        """Add message to conversation history (stateful agents only)."""
        if hasattr(self, 'conversation_history'):
            self.conversation_history.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
    
    # Optional: Cost tracking
    async def track_llm_cost(self, cost: float, operation: str):
        """Track LLM cost (if cost tracking enabled)."""
        if self.agent_config.get("cost_tracking", False):
            await self.telemetry.record_metric(
                f"agent.{self.agent_name}.cost.{operation}",
                cost,
                {"model": self.llm_config.get("model")}
            )
```

---

## Configuration Schema

### Agent YAML Configuration

```yaml
agent_name: "UniversalMapperSpecialist"
role: "Mapping Specialist"
goal: "Suggest and validate mappings"
backstory: "..."

# LLM Configuration
llm_config:
  model: "gpt-4o-mini"
  max_tokens: 2000
  temperature: 0.3
  timeout: 120  # seconds
  retry:
    enabled: true
    max_attempts: 3
    base_delay: 2.0
  rate_limiting:
    enabled: true
    capacity: 100
    refill_rate: 10

# Agent Pattern Configuration
stateful: false  # true for stateful, false for stateless
max_conversation_history: 10  # Only used if stateful=true

# Execution Configuration
iterative_execution: false  # true for iterative, false for single-pass
max_iterations: 5  # Only used if iterative_execution=true

# Observability Configuration
cost_tracking: true  # Track LLM costs

# Tool Configuration
allowed_tools: ["map_to_canonical_tool", "validate_mapping"]
max_tool_calls_per_request: 10
```

---

## Migration Strategy

### Phase 1: Infrastructure Layer (Week 1)

1. ✅ Add retry logic to LLM abstraction
2. ✅ Add timeout handling to LLM abstraction
3. ✅ Add rate limiting to LLM abstraction
4. ✅ Update configuration loading

**Testing:**
- Unit tests for retry logic
- Unit tests for timeout handling
- Unit tests for rate limiting

---

### Phase 2: Agent SDK Layer (Week 1-2)

1. ✅ Add optional conversation history to AgentBase
2. ✅ Add optional cost tracking to AgentBase
3. ✅ Update DeclarativeAgentBase to use infrastructure retry/timeout/rate limiting
4. ✅ Improve JSON parsing in DeclarativeAgentBase

**Testing:**
- Integration tests for conversation history
- Integration tests for cost tracking
- Integration tests for improved JSON parsing

---

### Phase 3: Declarative Agent Features (Week 2)

1. ✅ Add iterative execution to DeclarativeAgentBase
2. ✅ Add stateful pattern support to DeclarativeAgentBase
3. ✅ Update YAML configuration schema
4. ✅ Update comprehensive tests

**Testing:**
- Integration tests for iterative execution
- Integration tests for stateful pattern
- End-to-end tests for full workflow

---

### Phase 4: Production Validation (Week 3)

1. ✅ Run production pilot with 1-2 agents
2. ✅ Monitor retry/timeout/rate limiting behavior
3. ✅ Monitor cost tracking
4. ✅ Gather production metrics
5. ✅ Fix issues based on production learnings

---

## Testing Strategy

### Unit Tests

**Location:** `tests/unit/foundations/public_works_foundation/infrastructure_abstractions/`

1. Test retry logic with various error types
2. Test timeout handling
3. Test rate limiting behavior
4. Test JSON parsing with various formats

---

### Integration Tests

**Location:** `tests/integration/backend/business_enablement/agents/`

1. Test declarative agent with retry/timeout/rate limiting
2. Test stateful vs stateless patterns
3. Test iterative execution
4. Test cost tracking

---

### End-to-End Tests

**Location:** `scripts/insurance_use_case/`

1. Test full workflow with production gaps fixed
2. Test concurrent requests
3. Test production load scenarios

---

## Success Criteria

### Priority 1 (Must Have)

- ✅ Retry logic handles transient failures (429, timeouts, connection errors)
- ✅ Timeout prevents hanging requests
- ✅ Rate limiting prevents API violations
- ✅ JSON parsing handles various LLM response formats

**Confidence Level:** 🟢 **8.5/10 - Production Ready**

---

### Priority 2 (Should Have)

- ✅ Stateful agents maintain conversation history
- ✅ Iterative execution enables sophisticated reasoning
- ✅ Cost tracking provides visibility

**Confidence Level:** 🟢 **9.0/10 - Production Ready**

---

## Configuration Examples

### Stateless Agent (Lightweight)

```yaml
agent_name: "SimpleMapper"
stateful: false
iterative_execution: false
cost_tracking: true  # Still track costs for observability
llm_config:
  retry:
    enabled: true
  timeout: 60
```

### Stateful Agent (Full Capabilities)

```yaml
agent_name: "ConversationalMapper"
stateful: true
max_conversation_history: 20
iterative_execution: true
max_iterations: 5
cost_tracking: true
llm_config:
  retry:
    enabled: true
  timeout: 120
```

---

## Conclusion

This implementation plan:

1. ✅ **Respects Platform Architecture** - Supports both stateful and stateless patterns
2. ✅ **No Over-Burdening** - Features are optional and configurable
3. ✅ **Consistent Baseline** - Audit, telemetry, error handling always present
4. ✅ **Infrastructure First** - Retry/timeout/rate limiting at infrastructure layer
5. ✅ **Agent Choice** - Agents choose what they need via YAML config

**After Priority 1 fixes, confidence level:** 🟢 **8.5/10 - Production Ready**

