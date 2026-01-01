# Comprehensive Declarative Agent Testing Plan

## Overview

This document outlines the comprehensive testing strategy for the declarative `UniversalMapperSpecialist` agent. The goal is to validate that the new declarative pattern is **bulletproof** before migrating remaining agents and updating the Agentic SDK.

## Test Script

**Location:** `scripts/insurance_use_case/test_universal_mapper_declarative_comprehensive.py`

## Test Coverage

### Phase 1: Platform Setup
- ✅ DI Container initialization
- ✅ Public Works Foundation initialization
- ✅ Curator Foundation initialization
- ✅ Agentic Foundation initialization
- ✅ LLM abstraction availability check

### Phase 2: Orchestrator Setup
- ✅ Insurance Migration Orchestrator initialization
- ✅ MCP Server initialization

### Phase 3: Agent Tests (13 Comprehensive Tests)

#### Test 1: Agent Initialization (Real Dependencies)
**Purpose:** Validate agent can be initialized with real platform dependencies.

**Validations:**
- Agent class loads correctly
- Configuration file loads
- Agent name matches config
- Role, goal, backstory set from config
- Allowed tools configured
- LLM abstraction available

#### Test 2: Orchestrator Integration
**Purpose:** Validate agent can be set on orchestrator and access MCP server.

**Validations:**
- `set_orchestrator()` works
- Orchestrator reference stored
- MCP server accessible
- Available tools scoped correctly

#### Test 3: LLM Abstraction Validation
**Purpose:** Test that LLM abstraction is available and can make real API calls.

**Validations:**
- LLM abstraction available
- Can make real API call
- Response received
- Response has content

**Note:** This test will be skipped if LLM API keys are not configured.

#### Test 4: Prompt Building
**Purpose:** Test that agent builds correct prompts from configuration.

**Validations:**
- Prompt includes agent role
- Prompt includes agent goal
- Prompt includes available tools
- Prompt includes user message
- Tools are listed in prompt

#### Test 5: suggest_mappings() with Real LLM
**Purpose:** Test `suggest_mappings()` method with real LLM calls.

**Validations:**
- Method executes successfully
- Result has correct structure
- Suggestions returned
- Confidence scores present
- Reasoning included

**Note:** This test requires LLM API keys.

#### Test 6: learn_from_mappings() with Real LLM
**Purpose:** Test `learn_from_mappings()` method with real LLM calls.

**Validations:**
- Method executes successfully
- Pattern ID generated
- Patterns learned count correct
- Confidence score present

**Note:** This test requires LLM API keys.

#### Test 7: validate_mappings() with Real LLM
**Purpose:** Test `validate_mappings()` method with real LLM calls.

**Validations:**
- Method executes successfully
- Validation result returned
- `is_valid` field present
- Confidence score present
- Recommendations included

**Note:** This test requires LLM API keys.

#### Test 8: learn_from_correction() with Real LLM
**Purpose:** Test `learn_from_correction()` method with real LLM calls.

**Validations:**
- Method executes successfully
- Correction learned flag set
- Pattern ID generated
- Reasoning included

**Note:** This test requires LLM API keys.

#### Test 9: MCP Tool Execution
**Purpose:** Test that agent can execute MCP tools via orchestrator.

**Validations:**
- Tool execution works
- Tool result returned
- Tool calls can be extracted from LLM response
- Tool validation works

#### Test 10: Error Handling
**Purpose:** Test error handling in various scenarios.

**Validations:**
- Invalid requests handled gracefully
- Invalid tools filtered out
- Tool call limits enforced
- Error messages appropriate

#### Test 11: Tool Scoping
**Purpose:** Test that agent only sees allowed tools (scoping works).

**Validations:**
- Scoped tools match allowed tools
- All allowed tools visible (if in MCP server)
- No unauthorized tools visible
- Scoping logic works correctly

#### Test 12: Full Workflow Integration
**Purpose:** Test a full workflow: suggest → validate → learn.

**Validations:**
- Workflow executes end-to-end
- Suggestions generated
- Validation performed
- Learning successful
- All steps connected

**Note:** This test requires LLM API keys.

#### Test 13: Performance and Resource Usage
**Purpose:** Test agent performance and resource usage.

**Validations:**
- Prompt building is fast (< 1s)
- Tool extraction is fast (< 1s)
- No performance regressions
- Resource usage acceptable

## Expected Results

### With LLM API Keys Configured
- **Total Tests:** 13
- **Expected Passed:** 13
- **Expected Skipped:** 0
- **Expected Failed:** 0

### Without LLM API Keys Configured
- **Total Tests:** 13
- **Expected Passed:** ~6-7 (non-LLM tests)
- **Expected Skipped:** ~6-7 (LLM-dependent tests)
- **Expected Failed:** 0

## Running the Tests

### Prerequisites
1. Platform dependencies available
2. (Optional) LLM API keys configured for full testing

### Command
```bash
cd /home/founders/demoversion/symphainy_source
python3 scripts/insurance_use_case/test_universal_mapper_declarative_comprehensive.py
```

### Expected Output
- Detailed logging for each test
- Test results summary
- Success rate percentage
- List of any failures

## Success Criteria

The declarative agent is considered **bulletproof** when:

1. ✅ All structural tests pass (100%)
2. ✅ All integration tests pass (with real dependencies)
3. ✅ All LLM tests pass (with API keys configured)
4. ✅ All interface methods work correctly
5. ✅ Error handling works as expected
6. ✅ Tool scoping works correctly
7. ✅ Performance is acceptable
8. ✅ Full workflow executes successfully

## Next Steps After Testing

Once all tests pass:

1. **Migrate Remaining Agents**
   - Apply declarative pattern to all other agents
   - Use `UniversalMapperSpecialist` as the template

2. **Update Agentic SDK**
   - Document declarative pattern
   - Update base classes if needed
   - Add validation to prevent anti-patterns

3. **Production Deployment**
   - Deploy declarative agents
   - Monitor performance
   - Collect feedback

## Known Limitations

1. **LLM API Keys:** Some tests require LLM API keys to be configured
2. **Platform Dependencies:** Tests require full platform context
3. **MCP Server:** Tests require orchestrator MCP server to be initialized

## Troubleshooting

### LLM Tests Skipped
- **Cause:** LLM API keys not configured
- **Solution:** Configure `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in `.env.secrets`

### Platform Initialization Fails
- **Cause:** Missing dependencies or configuration
- **Solution:** Check platform configuration and dependencies

### MCP Server Not Available
- **Cause:** Orchestrator not initialized correctly
- **Solution:** Check orchestrator initialization and MCP server setup

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-19  
**Status:** Ready for Testing









