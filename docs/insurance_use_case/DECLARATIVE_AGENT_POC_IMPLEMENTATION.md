# Declarative Agent Architecture - Proof of Concept Implementation

## Overview

This document describes the proof-of-concept implementation of the declarative agent architecture. The POC demonstrates how agents can be defined by configuration (role, goal, backstory, tools) rather than hardcoded logic.

## Implementation Status

✅ **Completed:**
- `DeclarativeAgentBase` class created
- Sample configuration file for `UniversalMapperSpecialist`
- Proof-of-concept test script
- Documentation

## Files Created

### 1. DeclarativeAgentBase Class

**Location:** `symphainy-platform/backend/business_enablement/agents/declarative_agent_base.py`

**Key Features:**
- Loads agent configuration from JSON/YAML files
- Builds prompts from configuration + request
- Calls LLM abstraction with prompt
- Executes tools based on LLM decisions
- Provides standard capabilities (telemetry, security, tenant isolation)

**Key Methods:**
- `_load_agent_config()`: Loads configuration from file
- `_build_agent_prompt()`: Builds prompt from config + request
- `process_request()`: Main entry point for request processing
- `_extract_tool_calls_from_llm_response()`: Extracts tool calls from LLM response
- `_execute_tools()`: Executes tools via orchestrator's MCP server

### 2. Sample Configuration File

**Location:** `symphainy-platform/backend/business_enablement/agents/configs/universal_mapper_specialist.yaml`

**Configuration Structure:**
```yaml
agent_name: UniversalMapperSpecialist
role: Schema Mapping Specialist
goal: Create accurate field mappings...
backstory: You are an expert...
instructions:
  - Analyze source and target schemas
  - Use semantic similarity...
allowed_mcp_servers:
  - InsuranceMigrationMCPServer
allowed_tools:
  - map_to_canonical
  - discover_schema
  - validate_mapping
  - get_similar_patterns
capabilities:
  - semantic_analysis
  - pattern_matching
  - field_mapping
llm_config:
  model: gpt-4o-mini
  temperature: 0.3
  max_tokens: 2000
```

### 3. Proof-of-Concept Test Script

**Location:** `scripts/insurance_use_case/test_declarative_agent_poc.py`

**Test Coverage:**
- Configuration file loading
- Agent initialization from configuration
- Orchestrator setup (MCP server access)
- Request processing with LLM abstraction
- Tool execution via MCP server

## Architecture Flow

```
1. Load Configuration (YAML/JSON)
   ↓
2. Initialize DeclarativeAgentBase
   ↓
3. Set Orchestrator (for MCP server access)
   ↓
4. Process Request:
   a. Build prompt from config + request
   b. Call LLM abstraction
   c. Extract tool calls from LLM response
   d. Execute tools via MCP server
   e. Return formatted response
```

## How It Works

### 1. Configuration Loading

The agent loads its configuration from a YAML or JSON file:

```python
agent = DeclarativeAgentBase(
    agent_config_path="configs/universal_mapper_specialist.yaml",
    foundation_services=di_container,
    ...
)
```

### 2. Prompt Building

The agent builds a prompt that includes:
- Agent's role, goal, backstory
- Instructions
- Current request
- Available tools (scoped to this agent)

```python
prompt = f"""You are a {self.role}.
Your goal: {self.goal}
Your backstory: {self.backstory}
...
Available Tools:
{self._format_available_tools()}
...
"""
```

### 3. LLM Reasoning

The LLM abstraction receives the prompt and returns:
- Reasoning about what to do
- Tool calls to execute
- Response to the user

```json
{
    "reasoning": "I need to map the legacy schema...",
    "tool_calls": [
        {
            "tool_name": "map_to_canonical",
            "parameters": {...}
        }
    ],
    "response": "I've analyzed the schemas..."
}
```

### 4. Tool Execution

The agent executes tools via the orchestrator's MCP server:

```python
result = await self._orchestrator.mcp_server.execute_tool(
    tool_name,
    parameters
)
```

### 5. Response Formatting

The agent formats the final response with:
- Reasoning
- Tool results
- Response to user
- Standard metadata (telemetry, security, etc.)

## Key Benefits Demonstrated

1. **Scoped Tools**: Agents only see tools from `allowed_tools` list
2. **Declarative Configuration**: Easy to change agent behavior
3. **LLM Reasoning**: LLM decides what to do (not hardcoded)
4. **Standard Capabilities**: Telemetry, security, tenant isolation in wrapper

## Running the POC

### Prerequisites

1. Python 3.8+
2. Required dependencies (yaml, json, etc.)

### Run Test Script

```bash
cd /home/founders/demoversion/symphainy_source
python scripts/insurance_use_case/test_declarative_agent_poc.py
```

### Expected Output

```
🧪 Testing Declarative Agent Architecture (Proof-of-Concept)
======================================================================
1️⃣ Loading agent configuration...
   ✅ Configuration file found

2️⃣ Initializing Declarative Agent...
   ✅ Agent initialized: UniversalMapperSpecialist
   - Role: Schema Mapping Specialist
   - Goal: Create accurate field mappings...
   - Allowed Tools: map_to_canonical, discover_schema, validate_mapping, get_similar_patterns

3️⃣ Setting orchestrator (for MCP server access)...
   ✅ Orchestrator set
   - Available Tools: 4

4️⃣ Processing test request...
   ✅ Request processed successfully

📊 Results:
   - Success: True
   - Agent: UniversalMapperSpecialist
   - Reasoning: I need to map the legacy schema...
   - Tool Results: 1 tools executed
   - Response: I've analyzed the schemas...

✅ All tests passed!
```

## Next Steps

### Phase 1: Integration with Full Platform

1. **Integrate with Real Dependencies**
   - Connect to real `DIContainerService`
   - Connect to real `AgenticFoundationService`
   - Connect to real `PublicWorksFoundationService`

2. **Test with Real LLM Abstraction**
   - Use actual LLM provider (OpenAI, Anthropic, etc.)
   - Test with real prompts and responses
   - Validate JSON parsing from LLM responses

3. **Test with Real MCP Server**
   - Connect to real orchestrator MCP server
   - Test with real tool execution
   - Validate tool scoping works correctly

### Phase 2: Migrate One Agent

1. **Choose Pilot Agent**
   - `UniversalMapperSpecialist` (recommended)
   - Already has configuration file

2. **Migrate Agent**
   - Replace hardcoded logic with declarative pattern
   - Test thoroughly
   - Compare behavior with original

3. **Validate Results**
   - Ensure same functionality
   - Verify tool scoping works
   - Confirm LLM reasoning is effective

### Phase 3: Enhance LLM Abstraction

1. **Add Agentic Reasoning Support**
   - Enhance `generate_content` to support `agentic_reasoning` content type
   - Add structured response format
   - Improve tool call extraction

2. **Add Tool Descriptions**
   - Include tool schemas in prompts
   - Help LLM understand tool parameters
   - Improve tool selection accuracy

### Phase 4: Migrate Remaining Agents

1. **Create Configuration Files**
   - One config file per agent
   - Define role, goal, backstory, tools

2. **Migrate Agents One by One**
   - Start with simplest agents
   - Test each migration
   - Document learnings

3. **Remove Old Code**
   - Remove hardcoded agent logic
   - Clean up unused methods
   - Update documentation

## Known Limitations (POC)

1. **Mock Dependencies**: Test script uses mocks (expected in POC)
2. **Simple LLM Response Parsing**: May need enhancement for complex responses
3. **Tool Validation**: Basic validation (may need more sophisticated checks)
4. **Error Handling**: Basic error handling (may need enhancement)

## Comparison with Current Approach

### Current Approach (Hardcoded)

```python
class UniversalMapperSpecialist(SpecialistCapabilityAgent):
    async def execute_capability(self, request):
        context = await self._analyze_request_context(request)  # Hardcoded
        service_result = await self._call_enabling_service(...)  # Hardcoded
        enhanced = await self._enhance_with_ai(...)  # Hardcoded
        return enhanced
```

### Declarative Approach (Configuration-Driven)

```yaml
# Configuration file
agent_name: UniversalMapperSpecialist
role: Schema Mapping Specialist
goal: Create accurate mappings...
allowed_tools: [map_to_canonical, discover_schema, ...]
```

```python
# Agent initialization
agent = DeclarativeAgentBase(
    agent_config_path="configs/universal_mapper_specialist.yaml",
    ...
)

# LLM does the reasoning - no hardcoded logic!
result = await agent.process_request(request)
```

## Success Criteria

✅ **POC Complete When:**
- [x] DeclarativeAgentBase class created
- [x] Sample configuration file created
- [x] Test script runs successfully
- [x] Documentation complete

✅ **Phase 1 Complete When:**
- [ ] Integrated with real platform dependencies
- [ ] Tested with real LLM abstraction
- [ ] Tested with real MCP server

✅ **Phase 2 Complete When:**
- [ ] One agent migrated to declarative pattern
- [ ] Migration tested and validated
- [ ] Behavior matches original

✅ **Phase 3 Complete When:**
- [ ] LLM abstraction enhanced for agentic reasoning
- [ ] Tool descriptions included in prompts
- [ ] Tool selection accuracy improved

✅ **Phase 4 Complete When:**
- [ ] All agents migrated to declarative pattern
- [ ] Old hardcoded logic removed
- [ ] Documentation updated

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-19  
**Status:** Proof-of-Concept Complete - Ready for Integration









