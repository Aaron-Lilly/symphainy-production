# Declarative Agent: YAML vs Python Class Analysis

**Date:** 2025-12-05  
**Question:** Do we need both YAML config and Python class (like CrewAI), or can we make it more dynamic?

## Current Implementation

### What We Have:
1. **YAML Config File** (`universal_mapper_specialist.yaml`):
   - Defines agent behavior (role, goal, backstory, instructions)
   - Lists allowed MCP servers and tools
   - Configures LLM settings
   - Declarative "script" for the agent

2. **Python Class** (`UniversalMapperSpecialist`):
   - Inherits from `DeclarativeAgentBase`
   - Loads YAML config in `__init__`
   - Provides domain-specific methods: `suggest_mappings()`, `validate_mappings()`, `learn_from_mappings()`, `learn_from_correction()`
   - These methods wrap `process_request()` and extract/format results

### Why We Need Both:

#### 1. **Orchestrator Interface Requirements**
The orchestrator calls domain-specific methods directly:
```python
suggestions_result = await universal_mapper.suggest_mappings(
    source_schema=source_schema,
    target_schema_name=canonical_model_name,
    user_context=user_context
)
```

These methods provide:
- **Type safety**: IDE autocomplete, type checking
- **Stable interface**: Orchestrators don't need to know about `process_request()`
- **Result extraction**: Parse LLM response and format for orchestrator consumption
- **Architectural alignment**: This is the correct pattern for orchestrator-agent interaction (not just backwards compatibility)

#### 2. **Result Extraction & Formatting**
The Python class methods extract structured data from the LLM response:
```python
# Extract suggestions from tool results
if "map_to_canonical" in tool_results:
    mapping_result = tool_results["map_to_canonical"]
    # Convert to suggestions format
    suggestions = [...]
    return {
        "success": True,
        "suggestions": suggestions,
        "total_suggestions": len(suggestions),
        "highest_confidence": max([...])
    }
```

This extraction logic is domain-specific and can't be in the YAML config.

#### 3. **Integration with Platform**
- The Python class integrates with `AgentBase` (telemetry, security, etc.)
- It sets up orchestrator references for MCP tool access
- It provides AGUI schema registration
- It handles initialization with foundation services

## Comparison with CrewAI

### CrewAI Pattern:
- **JSON/YAML**: Defines agent behavior (role, goal, backstory, tools)
- **Python Class**: Wraps the config and provides framework integration

### Our Pattern (Similar):
- **YAML**: Defines agent behavior (role, goal, backstory, tools, LLM config)
- **Python Class**: Wraps the config, provides domain-specific methods, and integrates with platform

### Key Difference:
CrewAI agents are typically used via a `Crew` that orchestrates them. Our agents are called directly by orchestrators with domain-specific methods.

## Could We Make It More Dynamic?

### Option 1: Pure YAML (No Python Class)
**Problem:** Orchestrators need to call domain-specific methods. We'd need to:
- Change orchestrators to call `process_request()` directly
- Move result extraction logic somewhere (where?)
- Lose type safety and IDE support
- Break backward compatibility

**Verdict:** ❌ Not practical - too much refactoring, loses benefits

### Option 2: Auto-Generate Python Class from YAML
**Approach:** Generate Python class methods from YAML config
```yaml
# In YAML
interface_methods:
  suggest_mappings:
    request_template: "Suggest mappings from {source_schema} to {target_schema_name}"
    result_extraction:
      from_tool: "map_to_canonical"
      format: "suggestions"
```

**Problem:**
- Result extraction logic is complex and domain-specific
- Each agent has different extraction needs
- Would make YAML configs very verbose
- Still need Python class for initialization/integration

**Verdict:** ⚠️ Possible but adds complexity, may not be worth it

### Option 3: Thin Python Wrapper (Current Approach - OPTIMAL)
**Approach:** Keep Python class minimal - just:
1. Load config
2. Provide domain-specific method stubs
3. Extract/format results

**Benefits:**
- ✅ Type safety
- ✅ IDE support
- ✅ Stable orchestrator interface
- ✅ Domain-specific result extraction
- ✅ Platform integration
- ✅ Minimal boilerplate

**Current Implementation:**
- Python class is already quite thin (~450 lines)
- Most logic is in `DeclarativeAgentBase` (reusable)
- Domain methods are just wrappers around `process_request()`

**Verdict:** ✅ This is the right approach

## Why Our Tests Didn't Catch This

Our tests:
- ✅ Tested the declarative agent base directly
- ✅ Tested the `UniversalMapperSpecialist` class
- ✅ Tested `process_request()` with real LLM calls
- ❌ **Didn't test** if orchestrators could use agents without Python classes

**What We Should Test:**
- Orchestrator integration (calling `suggest_mappings()` etc.)
- Result extraction and formatting
- Backward compatibility with existing orchestrator code

## Recommendation

**Keep the current approach (YAML + Python class):**

1. **YAML Config**: Defines agent behavior (what it does) - **Declarative core**
2. **Python Class**: Provides typed interface (how orchestrators use it) - **Architectural requirement**

This is similar to CrewAI but with domain-specific methods for orchestrator integration.

**The Python class is necessary because:**
- Orchestrators need stable, typed interfaces (architectural requirement, not backwards compatibility)
- Result extraction is domain-specific and belongs in the agent (encapsulation)
- Platform integration requires Python classes
- Type safety and IDE support are fundamental, not optional

**We could make it thinner by:**
- Moving more common logic to `DeclarativeAgentBase`
- Using decorators or mixins for common patterns
- But the domain-specific methods are still needed (architectural requirement)

## Conclusion

**Yes, we need both** (like CrewAI), but for different reasons:
- **CrewAI**: Python class for framework integration
- **Us**: Python class for orchestrator interface + result extraction

**Key Insight**: The domain methods aren't about "backwards compatibility" - they're the **architecturally correct pattern** for how orchestrators should interact with agents. Orchestrators expect typed, domain-specific interfaces regardless of the underlying implementation.

This is a **layered architecture**:
- **Inner layer (declarative)**: YAML config + `process_request()` - defines what the agent does
- **Outer layer (typed interface)**: Domain methods - defines how orchestrators use the agent

Both layers are necessary and architecturally aligned.

Our tests didn't catch this because we tested the agent in isolation, not how orchestrators use it. We should add orchestrator integration tests to validate the full workflow.

