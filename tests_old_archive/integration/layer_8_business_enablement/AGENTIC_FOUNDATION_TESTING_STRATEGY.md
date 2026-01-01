# Agentic Foundation and Agent Testing Strategy

**Date:** 2025-11-29  
**Purpose:** Define testing approach for Agentic Foundation and agents

---

## 🎯 Recommended Approach: **Phased Testing Strategy**

### **Phase 1: Mock Testing (Foundation & Code Verification)**
**Goal:** Verify foundation, code structure, agent initialization, and tool calling patterns work correctly

**Why Mock First:**
- ✅ **Faster iteration** - No API latency or rate limits
- ✅ **Cost-effective** - No API costs during development
- ✅ **Reliable** - No network issues or API downtime
- ✅ **Predictable** - Can test edge cases and error handling
- ✅ **Easier debugging** - Isolate foundation/code issues from API issues
- ✅ **Comprehensive coverage** - Test all code paths without API constraints

**What to Test with Mocks:**
1. ✅ Agentic Foundation initialization
2. ✅ Agent factory and creation
3. ✅ Agent initialization via orchestrators
4. ✅ Agent protocol setup (conversation, guidance, tool calling)
5. ✅ MCP tool registration and discovery
6. ✅ Tool execution patterns (without actual LLM calls)
7. ✅ Error handling and graceful degradation
8. ✅ Agent lifecycle management
9. ✅ Multi-tenancy and security integration
10. ✅ Agent-to-orchestrator communication

---

### **Phase 2: Real API Testing (Integration Verification)**
**Goal:** Verify actual LLM integration works end-to-end

**Why Real API Second:**
- ✅ **Verify integration** - Ensure LLM providers are correctly configured
- ✅ **Test real responses** - Verify agents can handle actual LLM outputs
- ✅ **Performance testing** - Measure real API latency and response times
- ✅ **Cost estimation** - Understand actual API usage and costs
- ✅ **Production readiness** - Final verification before deployment

**What to Test with Real APIs:**
1. ✅ LLM provider configuration (OpenAI, Anthropic, etc.)
2. ✅ Agent conversation processing with real LLM
3. ✅ Agent guidance generation with real LLM
4. ✅ Tool calling and orchestration with real LLM
5. ✅ Response quality and formatting
6. ✅ Error handling for API failures
7. ✅ Rate limiting and retry logic
8. ✅ Token usage and cost tracking

---

## 📋 Detailed Testing Plan

### **Phase 1: Mock Testing (Recommended First)**

#### **1.1 Agentic Foundation Tests**
```python
# Test Agentic Foundation initialization
- Foundation service initialization
- Agent factory setup
- Agent registry and tracking
- Foundation health checks
```

#### **1.2 Agent Creation Tests**
```python
# Test agent creation via factory
- Agent creation with valid parameters
- Agent creation with invalid parameters
- Agent creation error handling
- Agent lifecycle management
```

#### **1.3 Agent Initialization Tests**
```python
# Test agent initialization via orchestrators
- Liaison agent initialization
- Specialist agent initialization
- Agent protocol setup
- MCP client manager setup
- Policy integration setup
```

#### **1.4 Agent Protocol Tests (Mocked LLM)**
```python
# Test agent protocols with mocked LLM responses
- ConversationRequest processing (mocked)
- CapabilityGuidanceRequest processing (mocked)
- Tool execution patterns (mocked)
- Error handling and fallbacks
```

#### **1.5 MCP Tool Integration Tests**
```python
# Test MCP tool registration and discovery
- Tool registration via MCP server
- Tool discovery by agents
- Tool execution patterns
- Tool composition and chaining
```

#### **1.6 Orchestrator-Agent Integration Tests**
```python
# Test orchestrator-agent communication
- Agent access via orchestrator
- Agent tool calling via orchestrator methods
- Agent response handling
- Agent error propagation
```

---

### **Phase 2: Real API Testing (After Phase 1 Passes)**

#### **2.1 LLM Provider Configuration Tests**
```python
# Test LLM provider setup
- OpenAI configuration
- Anthropic configuration (if used)
- API key validation
- Provider selection logic
```

#### **2.2 Real Conversation Tests**
```python
# Test actual LLM conversations
- Simple conversation queries
- Complex multi-turn conversations
- Context preservation
- Response quality validation
```

#### **2.3 Real Guidance Tests**
```python
# Test actual LLM guidance generation
- Capability guidance requests
- Step-by-step guidance
- Alternative approaches
- Prerequisites and dependencies
```

#### **2.4 Real Tool Execution Tests**
```python
# Test actual tool calling with LLM
- Tool selection by LLM
- Tool parameter extraction
- Tool execution orchestration
- Tool result interpretation
```

#### **2.5 End-to-End Agent Workflows**
```python
# Test complete agent workflows
- User query → Agent processing → Tool execution → Response
- Multi-agent collaboration
- Agent-to-agent communication
- Complex use case scenarios
```

---

## 🔧 Implementation Approach

### **Mock Strategy**

#### **Option 1: Mock LLM Client (Recommended)**
```python
# Mock the LLM client/provider at the Agentic Foundation level
# This allows testing all agent logic without real API calls

class MockLLMClient:
    async def chat_completion(self, messages, **kwargs):
        # Return predictable responses for testing
        return {
            "choices": [{
                "message": {
                    "content": "Mocked response for testing",
                    "role": "assistant"
                }
            }]
        }
```

#### **Option 2: Mock Agent Protocol**
```python
# Mock the agent protocol layer
# This allows testing orchestrator-agent integration without LLM

class MockAgentProtocol:
    async def process_conversation(self, request):
        return ConversationResponse(
            success=True,
            message="Mocked conversation response",
            ...
        )
```

#### **Option 3: Environment-Based Toggle**
```python
# Use environment variable to toggle between mock and real
USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "true").lower() == "true"

if USE_MOCK_LLM:
    llm_client = MockLLMClient()
else:
    llm_client = RealLLMClient(api_key=...)
```

---

### **Real API Strategy**

#### **Configuration**
```python
# Use environment variables for API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Skip tests if API keys not configured
if not OPENAI_API_KEY:
    pytest.skip("OpenAI API key not configured")
```

#### **Test Isolation**
```python
# Mark real API tests separately
@pytest.mark.real_api
@pytest.mark.slow
async def test_agent_conversation_real_llm():
    # Test with real LLM
    ...
```

#### **Cost Management**
```python
# Use cheaper models for testing
TEST_MODEL = "gpt-3.5-turbo"  # Instead of gpt-4
TEST_MAX_TOKENS = 100  # Limit token usage
```

---

## 📊 Test Organization

### **Test File Structure**
```
tests/integration/layer_8_business_enablement/
├── test_agentic_utilities.py           # ✅ Phase 1: Mock LLM adapter and utilities
├── test_agentic_foundation.py          # ✅ Phase 1: Foundation tests (mocked)
├── test_agent_initialization.py        # ✅ Phase 1: Agent creation tests (mocked)
├── test_agent_business_helper.py       # ✅ Phase 1: BusinessAbstractionHelper tests (mocked)
├── test_agent_protocols_mocked.py      # ✅ Phase 1: Protocol tests (mocked)
├── test_agent_mcp_integration.py       # ✅ Phase 1: MCP tool tests (mocked)
├── test_agent_orchestrator_integration.py  # ✅ Phase 1: Orchestrator integration (mocked)
├── test_agent_conversation_real.py     # ⏳ Phase 2: Real conversation tests
├── test_agent_guidance_real.py          # ⏳ Phase 2: Real guidance tests
└── test_agent_end_to_end_real.py       # ⏳ Phase 2: End-to-end workflows
```

**Status:**
- ✅ Phase 1 test suite **COMPLETE** (7 test files, ~50+ test cases)
- ⏳ Phase 2 test suite **PENDING** (to be created after Phase 1 passes)

---

## ✅ Recommended Testing Order

### **Step 1: Foundation Tests (Mocked)**
1. Test Agentic Foundation initialization
2. Test agent factory and creation
3. Test agent registry and tracking

### **Step 2: Agent Initialization Tests (Mocked)**
1. Test agent initialization via orchestrators
2. Test agent protocol setup
3. Test MCP client manager setup

### **Step 3: Agent Protocol Tests (Mocked)**
1. Test conversation processing (mocked responses)
2. Test guidance generation (mocked responses)
3. Test tool execution patterns (mocked)

### **Step 4: Integration Tests (Mocked)**
1. Test orchestrator-agent communication
2. Test MCP tool registration and discovery
3. Test agent-to-agent communication

### **Step 5: Real API Tests (After Phase 1 Passes)**
1. Test LLM provider configuration
2. Test real conversation processing
3. Test real guidance generation
4. Test real tool execution
5. Test end-to-end workflows

---

## 🎯 Success Criteria

### **Phase 1 (Mocked) - Must Pass Before Phase 2:**
- ✅ All foundation tests pass
- ✅ All agent initialization tests pass
- ✅ All protocol tests pass (with mocks)
- ✅ All integration tests pass
- ✅ No code-level bugs or issues

### **Phase 2 (Real API) - Production Readiness:**
- ✅ All real API tests pass
- ✅ LLM integration works correctly
- ✅ Response quality is acceptable
- ✅ Error handling works for API failures
- ✅ Performance is acceptable

---

## 💡 Recommendation

**Start with Phase 1 (Mocked Testing)** because:

1. **Faster Development** - Can iterate quickly without API delays
2. **Cost-Effective** - No API costs during development
3. **Comprehensive Coverage** - Can test all code paths
4. **Easier Debugging** - Isolate foundation/code issues
5. **Reliable Tests** - No flaky tests due to network/API issues

**Then move to Phase 2 (Real API Testing)** once Phase 1 passes, to:
1. Verify actual LLM integration
2. Test real response quality
3. Validate production readiness

This phased approach ensures we catch foundation/code issues early (cheap, fast) before investing in real API testing (slower, costs money).

---

## 🚀 Next Steps

1. ✅ **COMPLETED:** Create Phase 1 test suite (mocked)
   - ✅ `test_agentic_utilities.py` - Mock LLM adapter and test utilities
   - ✅ `test_agentic_foundation.py` - Foundation initialization tests
   - ✅ `test_agent_initialization.py` - Agent creation and factory tests
   - ✅ `test_agent_business_helper.py` - BusinessAbstractionHelper integration tests
   - ✅ `test_agent_protocols_mocked.py` - Protocol tests with mocked LLM
   - ✅ `test_agent_mcp_integration.py` - MCP tool discovery and execution tests
   - ✅ `test_agent_orchestrator_integration.py` - Orchestrator-agent communication tests

2. ⏳ **NEXT:** Run Phase 1 tests and fix any issues
   ```bash
   # Run all Phase 1 tests
   pytest tests/integration/layer_8_business_enablement/test_agentic_*.py \
          tests/integration/layer_8_business_enablement/test_agent_*.py \
          -v --tb=short
   ```

3. ⏳ **FUTURE:** Once Phase 1 passes, create Phase 2 test suite (real API)
   - `test_agent_conversation_real.py` - Real conversation tests
   - `test_agent_guidance_real.py` - Real guidance tests
   - `test_agent_end_to_end_real.py` - End-to-end workflows

4. ⏳ **FUTURE:** Run Phase 2 tests and validate production readiness

