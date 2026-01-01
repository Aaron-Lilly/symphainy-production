# Agentic Foundation and Agent Testing Strategy V2

**Date:** 2025-11-29  
**Purpose:** Define testing approach for Agentic Foundation and agents  
**Critical Focus:** Verify agents can USE Smart City services and utilities (not just instantiate)

---

## 🎯 **CRITICAL REQUIREMENT: Integration Testing**

**The Agentic Foundation replaces CrewAI** - agents MUST be able to:
1. ✅ **Access Smart City services via MCP tools** - This is fundamental
2. ✅ **Access Business Enablement orchestrators via MCP tools** - This is fundamental
3. ✅ **Use utilities from Public Works Foundation** - This is fundamental
4. ✅ **Execute tools and get results** - This is fundamental

**If these don't work, we don't have an Agentic Foundation - we just have class instantiation.**

---

## 🎯 Recommended Approach: **Integration-First Testing Strategy**

### **Phase 1: Integration Verification (Foundation & Platform Access)**
**Goal:** Verify agents can actually USE the platform infrastructure

**Why Integration First:**
- ✅ **Catches breaking issues early** - Before spending money on API calls
- ✅ **Verifies platform integration** - Agents must work with Smart City and utilities
- ✅ **Validates architecture** - Ensures the foundation actually works
- ✅ **Prevents wasted effort** - Don't test LLM if agents can't use tools

**What to Test (Integration Points):**
1. ✅ **MCP Tool Discovery** - Can agents discover Smart City MCP tools?
2. ✅ **MCP Tool Discovery (Business Enablement)** - Can agents discover Business Enablement MCP tools?
3. ✅ **MCP Tool Execution (Smart City)** - Can agents execute Smart City tools and get results?
4. ✅ **MCP Tool Execution (Business Enablement)** - Can agents execute Business Enablement tools and get results?
5. ✅ **Utility Access** - Can agents access Public Works utilities?
6. ✅ **Smart City Service Access** - Can agents connect to Smart City services?
7. ✅ **Business Enablement Service Access** - Can agents access Business Enablement orchestrators?
8. ✅ **Tool Composition** - Can agents chain tools together?
9. ✅ **Error Handling** - Do agents handle failures gracefully?
10. ✅ **Agent Initialization** - Do agents initialize with all dependencies?
11. ✅ **Agent Protocols** - Do protocols route correctly (with mocked LLM)?

**Mock Strategy:**
- ✅ **Mock LLM responses** - Use mocked LLM to avoid API costs
- ❌ **DO NOT mock MCP tools** - Test real MCP tool execution
- ❌ **DO NOT mock utilities** - Test real utility access
- ✅ **Use full infrastructure** - Test with Smart City services

---

### **Phase 2: Real API Testing (LLM Integration Verification)**
**Goal:** Verify actual LLM integration works end-to-end

**Why Real API Second:**
- ✅ **Verify LLM integration** - After we know infrastructure works
- ✅ **Test real responses** - Verify agents can handle actual LLM outputs
- ✅ **Performance testing** - Measure real API latency
- ✅ **Cost estimation** - Understand actual API usage

**What to Test with Real APIs:**
1. ✅ LLM provider configuration
2. ✅ Agent conversation processing with real LLM
3. ✅ Agent guidance generation with real LLM
4. ✅ Tool calling orchestration with real LLM
5. ✅ Response quality and formatting

---

## 📋 Detailed Testing Plan

### **Phase 1: Integration Verification (Critical First)**

#### **1.1 MCP Tool Discovery Tests**
```python
# Test that agents can discover Smart City MCP tools
- Agent can discover tools via MCP Client Manager
- Tools are properly namespaced (role_tool_name)
- Tool discovery uses Curator for service discovery
- Tools are available for execution
```

#### **1.2 MCP Tool Execution Tests (Smart City)**
```python
# Test that agents can execute Smart City MCP tools and get results
- Agent can execute librarian tools (e.g., store_document)
- Agent can execute data_steward tools (e.g., validate_schema)
- Agent can execute content_steward tools (e.g., upload_file)
- Tool execution returns results (not errors)
- Tool execution handles errors gracefully
```

#### **1.2b MCP Tool Execution Tests (Business Enablement)**
```python
# Test that agents can execute Business Enablement MCP tools and get results
- Agent can execute content_analysis_mcp_server tools (e.g., analyze_document_tool)
- Agent can execute insights_mcp_server tools (e.g., generate_insights_tool)
- Agent can execute operations_mcp_server tools (e.g., create_sop_tool)
- Agent can execute business_outcomes_mcp_server tools (e.g., generate_roadmap_tool)
- Tool execution returns results (not errors)
- Tool execution handles errors gracefully
```

#### **1.3 Utility Access Tests**
```python
# Test that agents can access Public Works utilities
- Agent can access LLM abstraction via BusinessAbstractionHelper
- Agent can access file management abstraction
- Agent can access other utilities
- Utility access is properly cached
```

#### **1.4 Smart City Service Integration Tests**
```python
# Test that agents can connect to Smart City services
- Agent can connect to Smart City MCP server
- Agent can discover available services
- Agent can get service health status
- Agent handles service unavailability gracefully
```

#### **1.5 Tool Composition Tests**
```python
# Test that agents can chain tools together
- Agent can compose multiple tools
- Tool chaining works correctly
- Tool results are passed between tools
- Tool composition handles errors
```

#### **1.6 Agent Initialization Tests**
```python
# Test agent initialization with full dependencies
- Agent initializes with MCP Client Manager
- Agent initializes with BusinessAbstractionHelper
- Agent initializes with all required dependencies
- Agent handles missing optional dependencies gracefully
```

#### **1.7 Agent Protocol Tests (Mocked LLM)**
```python
# Test agent protocols with mocked LLM but real infrastructure
- ConversationRequest processing (mocked LLM, real MCP)
- CapabilityGuidanceRequest processing (mocked LLM, real utilities)
- Tool execution patterns (mocked LLM, real MCP tools)
- Error handling and fallbacks
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
# Test actual LLM conversations with real infrastructure
- Simple conversation queries (real LLM, real MCP)
- Complex multi-turn conversations
- Context preservation
- Response quality validation
```

#### **2.3 Real Guidance Tests**
```python
# Test actual LLM guidance generation
- Capability guidance requests (real LLM, real utilities)
- Step-by-step guidance
- Alternative approaches
- Prerequisites and dependencies
```

#### **2.4 Real Tool Execution Tests**
```python
# Test actual tool calling with LLM
- Tool selection by LLM (real LLM decides which tool)
- Tool parameter extraction
- Tool execution orchestration (real LLM, real MCP)
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

### **Mock Strategy (Updated)**

#### **Mock LLM Only (Recommended)**
```python
# Mock the LLM client/provider at the Agentic Foundation level
# This allows testing all agent logic without real API calls
# BUT: Use real MCP tools and utilities

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

# BUT: Use real MCP Client Manager
# BUT: Use real Smart City services
# BUT: Use real utilities
```

#### **DO NOT Mock:**
- ❌ MCP Client Manager
- ❌ Smart City MCP Server
- ❌ Smart City Services
- ❌ Public Works utilities
- ❌ Tool execution

#### **DO Mock:**
- ✅ LLM API calls (to avoid costs)
- ✅ LLM responses (for predictable testing)

---

### **Test Infrastructure**

#### **Use Full Infrastructure Fixture**
```python
# Use smart_city_infrastructure fixture (not minimal)
# This ensures we test with real Smart City services

@pytest.fixture
async def agent_with_full_infrastructure(smart_city_infrastructure):
    """Agent with full infrastructure for integration testing."""
    # Initialize Agentic Foundation
    # Create agent
    # Agent should have access to:
    # - Smart City services via MCP
    # - Public Works utilities
    # - All platform infrastructure
    return agent
```

#### **Test Requirements:**
- ✅ Smart City services must be initialized
- ✅ MCP servers must be available
- ✅ Utilities must be accessible
- ✅ If services unavailable, tests should fail with clear error (not skip)

---

## 📊 Test Organization

### **Test File Structure (Updated)**
```
tests/integration/layer_8_business_enablement/
├── test_agentic_foundation.py          # Phase 1: Foundation tests (real infrastructure)
├── test_agent_mcp_integration.py      # Phase 1: MCP tool discovery and execution (REAL)
├── test_agent_utility_access.py        # Phase 1: Utility access tests (REAL)
├── test_agent_smart_city_integration.py  # Phase 1: Smart City integration (REAL)
├── test_agent_tool_composition.py      # Phase 1: Tool chaining (REAL)
├── test_agent_initialization.py       # Phase 1: Agent creation (real infrastructure)
├── test_agent_protocols_mocked.py      # Phase 1: Protocol tests (mocked LLM, real infrastructure)
├── test_agent_orchestrator_integration.py  # Phase 1: Orchestrator integration (real infrastructure)
├── test_agent_conversation_real.py     # Phase 2: Real conversation tests
├── test_agent_guidance_real.py         # Phase 2: Real guidance tests
└── test_agent_end_to_end_real.py       # Phase 2: End-to-end workflows
```

---

## ✅ Recommended Testing Order

### **Step 1: Infrastructure Integration Tests (CRITICAL)**
1. Test MCP tool discovery (real Smart City services)
2. Test MCP tool execution (real tool calls)
3. Test utility access (real Public Works utilities)
4. Test Smart City service connection (real services)

### **Step 2: Agent Initialization Tests (Real Infrastructure)**
1. Test agent initialization with full dependencies
2. Test agent can access MCP Client Manager
3. Test agent can access BusinessAbstractionHelper
4. Test agent handles missing optional dependencies

### **Step 3: Tool Composition Tests (Real Infrastructure)**
1. Test tool chaining (real MCP tools)
2. Test tool result passing
3. Test error handling in tool chains

### **Step 4: Agent Protocol Tests (Mocked LLM, Real Infrastructure)**
1. Test conversation processing (mocked LLM, real MCP)
2. Test guidance generation (mocked LLM, real utilities)
3. Test tool execution patterns (mocked LLM, real tools)

### **Step 5: Real API Tests (After Phase 1 Passes)**
1. Test LLM provider configuration
2. Test real conversation processing
3. Test real guidance generation
4. Test real tool execution with LLM
5. Test end-to-end workflows

---

## 🎯 Success Criteria

### **Phase 1 (Integration) - Must Pass Before Phase 2:**
- ✅ Agents can discover MCP tools from Smart City services
- ✅ Agents can execute MCP tools and get results
- ✅ Agents can access utilities from Public Works Foundation
- ✅ Agents can connect to Smart City services
- ✅ Tool composition works (tools can be chained)
- ✅ Error handling works for infrastructure failures
- ✅ Agent initialization works with full infrastructure
- ✅ Agent protocols work (with mocked LLM, real infrastructure)

### **Phase 2 (Real API) - Production Readiness:**
- ✅ All real API tests pass
- ✅ LLM integration works correctly
- ✅ Response quality is acceptable
- ✅ Error handling works for API failures
- ✅ Performance is acceptable

---

## 💡 Key Principle

**"Test What Matters"**

We're not testing that we can create agent objects - we're testing that agents can:
1. **USE Smart City services** via MCP tools
2. **USE utilities** from Public Works Foundation
3. **EXECUTE tools** and get results
4. **WORK with the platform** infrastructure

If agents can't do these things, we don't have an Agentic Foundation - we just have class instantiation.

---

## 🚀 Next Steps

1. ⏳ **Revise Phase 1 tests** to focus on integration points
2. ⏳ **Use full infrastructure** (smart_city_infrastructure fixture)
3. ⏳ **Test real MCP tool execution** (not mocked)
4. ⏳ **Test real utility access** (not mocked)
5. ⏳ **Mock only LLM** (to avoid API costs)
6. ⏳ **Run Phase 1 tests** and fix any integration issues
7. ⏳ **Once Phase 1 passes**, proceed to Phase 2 (real API tests)

---

## 🔍 Critical Test Scenarios

### **Scenario 1: Agent Uses Smart City Tool (Librarian)**
```python
# Agent should be able to:
1. Discover librarian tools via MCP
2. Execute librarian_store_document tool
3. Get real result from Librarian service
4. Handle errors if Librarian unavailable
```

### **Scenario 1b: Agent Uses Business Enablement Tool (Content Analysis)**
```python
# Agent should be able to:
1. Discover content_analysis_mcp_server tools
2. Execute analyze_document_tool
3. Get real result from Content Analysis Orchestrator
4. Handle errors if orchestrator unavailable
```

### **Scenario 2: Agent Uses Data Steward Tool**
```python
# Agent should be able to:
1. Discover data_steward tools via MCP
2. Execute data_steward_validate_schema tool
3. Get real result from Data Steward service
4. Handle errors if Data Steward unavailable
```

### **Scenario 3: Agent Uses Utility**
```python
# Agent should be able to:
1. Access LLM abstraction via BusinessAbstractionHelper
2. Use file management abstraction
3. Use other Public Works utilities
4. Handle errors if utilities unavailable
```

### **Scenario 4: Agent Chains Tools (Smart City)**
```python
# Agent should be able to:
1. Execute librarian_store_document
2. Use result to execute data_steward_validate_schema
3. Chain multiple tools together
4. Handle errors in tool chain
```

### **Scenario 4b: Agent Chains Tools (Cross-Domain)**
```python
# Agent should be able to:
1. Execute Smart City tool (librarian_store_document)
2. Use result to execute Business Enablement tool (content_analysis_analyze_document)
3. Chain tools across Smart City and Business Enablement
4. Handle errors in cross-domain tool chain
```

---

## ⚠️ **Critical: If Tests Fail**

If integration tests fail, it means:
- ❌ Agents can't use Smart City services → **Breaking issue**
- ❌ Agents can't use utilities → **Breaking issue**
- ❌ MCP integration doesn't work → **Breaking issue**

**These must be fixed before proceeding to Phase 2 (real API tests).**

---

## 📝 Summary

**Phase 1 Focus:**
- ✅ **Integration verification** - Can agents USE the platform?
- ✅ **Real infrastructure** - Test with Smart City services AND Business Enablement orchestrators
- ✅ **Real MCP tools** - Test actual tool execution (Smart City AND Business Enablement)
- ✅ **Real utilities** - Test actual utility access
- ✅ **Mocked LLM** - Avoid API costs during development

**Phase 2 Focus:**
- ✅ **LLM integration** - After we know infrastructure works
- ✅ **Real API calls** - Verify LLM integration
- ✅ **Production readiness** - Final verification

