# Orchestrator Declarative Pattern Migration Analysis

**Date:** 2025-12-05  
**Question:** Should we update orchestrators to use `process_request()` directly instead of maintaining backward compatibility with domain-specific methods?

## Current State

### Agent Method Calls in Orchestrators:
1. **InsuranceMigrationOrchestrator**:
   - `universal_mapper.suggest_mappings()` - 1 call
   - `universal_mapper.learn_from_mappings()` - 1 call
   - `routing_decision_agent.decide_routing()` - 1 call

**Total:** Only 3 direct agent method calls across all orchestrators

### Current Pattern:
```python
# Orchestrator calls domain-specific method
suggestions_result = await universal_mapper.suggest_mappings(
    source_schema=source_schema,
    target_schema_name=canonical_model_name,
    user_context=user_context
)

# Agent method wraps process_request() and extracts results
async def suggest_mappings(self, ...):
    request = {
        "message": f"Suggest mappings from source schema to {target_schema_name}",
        "task": "suggest_mappings",
        "data": {...},
        "user_context": user_context
    }
    result = await self.process_request(request)
    # Extract and format results
    return {"success": True, "suggestions": [...], ...}
```

## Option 1: Update Orchestrators to Use `process_request()` Directly

### Implementation:
```python
# Orchestrator calls process_request() directly
suggestions_result = await universal_mapper.process_request({
    "message": f"Suggest mappings from source schema to {canonical_model_name}",
    "task": "suggest_mappings",
    "data": {
        "source_schema": source_schema,
        "target_schema_name": canonical_model_name,
        "client_id": client_id
    },
    "user_context": user_context
})

# Orchestrator extracts results
if suggestions_result.get("success"):
    tool_results = suggestions_result.get("tool_results", {})
    if "map_to_canonical" in tool_results:
        mapping_result = tool_results["map_to_canonical"]
        # Extract suggestions...
        ai_mapping_suggestions = [...]
```

### Pros:
- ✅ **More Declarative**: Orchestrators use the core declarative pattern
- ✅ **Less Agent Code**: No domain-specific methods needed in agent classes
- ✅ **More Flexible**: Orchestrators can pass any request structure
- ✅ **Consistent**: All agent interactions use the same pattern

### Cons:
- ❌ **Lose Type Safety**: No typed method signatures (IDE autocomplete)
- ❌ **Result Extraction in Orchestrators**: Domain-specific extraction logic moves to orchestrators
- ❌ **Less Encapsulation**: Orchestrators need to know about tool result structure
- ❌ **More Orchestrator Code**: Each orchestrator needs extraction logic
- ❌ **Duplication**: Multiple orchestrators might need similar extraction logic

## Option 2: Keep Domain Methods (Current Approach)

### Pros:
- ✅ **Type Safety**: Typed method signatures with IDE support
- ✅ **Encapsulation**: Result extraction stays in agent (where it belongs)
- ✅ **Less Orchestrator Code**: Orchestrators just call methods, don't extract results
- ✅ **Single Responsibility**: Agent handles its own result formatting
- ✅ **Reusability**: Multiple orchestrators can use the same agent methods

### Cons:
- ❌ **More Agent Code**: Each agent needs domain-specific methods
- ❌ **Less "Pure" Declarative**: Still have Python code wrapping the declarative core

## Option 3: Hybrid - Thin Typed Wrappers

### Implementation:
Keep domain methods but make them even thinner - just typed wrappers:
```python
async def suggest_mappings(self, ...) -> Dict[str, Any]:
    """Typed wrapper around process_request() for suggest_mappings task."""
    result = await self.process_request({
        "message": f"Suggest mappings from source schema to {target_schema_name}",
        "task": "suggest_mappings",
        "data": {...},
        "user_context": user_context
    })
    return self._extract_suggestions(result)  # Extraction logic in agent
```

### Pros:
- ✅ **Type Safety**: Typed method signatures
- ✅ **Encapsulation**: Result extraction in agent
- ✅ **Minimal Code**: Methods are just thin wrappers
- ✅ **Best of Both**: Declarative core + typed interface

### Cons:
- ❌ **Still Need Some Python Code**: But it's minimal

## Recommendation: **Option 3 (Hybrid - Thin Typed Wrappers)**

### Key Insight: This Isn't "Backwards Compatibility" - It's Architectural Alignment

The domain-specific methods aren't a legacy pattern we're maintaining for backwards compatibility. **They're the correct architectural pattern** that matches what orchestrators should expect, regardless of whether we had old code or not.

### Rationale:

1. **Result Extraction Belongs in Agent**: The extraction logic is domain-specific and knows how to parse tool results. Orchestrators shouldn't need to know about `map_to_canonical` tool results. This is proper encapsulation.

2. **Type Safety is Valuable**: IDE autocomplete and type checking catch errors at development time, not runtime. This is a fundamental benefit of typed interfaces.

3. **Minimal Code**: The domain methods are already thin wrappers (~100 lines total for all 4 methods). Making them even thinner doesn't add much overhead.

4. **Encapsulation**: The agent is responsible for its own result formatting. This is good separation of concerns - orchestrators shouldn't know about agent internals.

5. **Reusability**: If multiple orchestrators need mapping suggestions, they all use the same method. If we move extraction to orchestrators, we'd duplicate it.

6. **Orchestrator Expectations**: Orchestrators expect typed, domain-specific interfaces. This is the right pattern, not a legacy one.

### Implementation Strategy:

1. **Keep domain methods** but make them even thinner:
   - Move request building to a helper method
   - Move result extraction to helper methods
   - Domain methods become 5-10 line wrappers

2. **Add to YAML config** (optional enhancement):
   ```yaml
   interface_methods:
     suggest_mappings:
       description: "Suggest mappings from source to target schema"
       request_template: "Suggest mappings from {source_schema} to {target_schema_name}"
       result_extraction:
         from_tool: "map_to_canonical"
         format: "suggestions"
   ```
   This could auto-generate the thin wrapper methods (future enhancement).

3. **Document the pattern**: Make it clear that domain methods are thin typed wrappers around `process_request()`.

## Alternative: If We Want Pure Declarative

If we really want orchestrators to use `process_request()` directly, we should:

1. **Move result extraction to YAML config** (complex but possible):
   ```yaml
   result_extractors:
     suggest_mappings:
       source: "tool_results.map_to_canonical"
       transform: |
         mappings = source.get("mappings", [])
         return {
           "suggestions": [{
             "source_field": m.get("source"),
             "target_field": m.get("target"),
             ...
           } for m in mappings],
           ...
         }
   ```

2. **Add helper method to agent**:
   ```python
   async def extract_result(self, task: str, result: dict) -> dict:
       """Extract formatted result based on YAML config."""
       extractor = self.agent_config.get("result_extractors", {}).get(task)
       if extractor:
           # Execute extractor logic
           return self._execute_extractor(extractor, result)
       return result
   ```

3. **Orchestrator calls**:
   ```python
   result = await universal_mapper.process_request({...})
   formatted = await universal_mapper.extract_result("suggest_mappings", result)
   ```

But this adds complexity and loses type safety.

## Conclusion

**Recommendation: Keep domain methods (Option 3 - Thin Typed Wrappers)**

### Architectural Alignment, Not Backwards Compatibility

The domain methods aren't about maintaining old code - **they're the architecturally correct pattern** for how orchestrators should interact with agents:

1. **Orchestrators expect typed, domain-specific interfaces** - This is the right pattern regardless of implementation details
2. **Agents encapsulate their result formatting** - Orchestrators shouldn't know about tool result structures
3. **Type safety is fundamental** - Not a nice-to-have, but a core requirement for maintainable code

### The Declarative Architecture

The "declarative" part is:
- **Core**: `process_request()` method + YAML config (agent behavior)
- **Interface**: Typed domain methods (orchestrator interaction)

This is a **layered architecture**:
- **Inner layer (declarative)**: YAML config + `process_request()` - defines what the agent does
- **Outer layer (typed interface)**: Domain methods - defines how orchestrators use the agent

Both layers are necessary and architecturally aligned. The domain methods aren't legacy code - they're the correct interface layer.

### Future Enhancements

If we want to reduce boilerplate, we could:
1. Auto-generate domain methods from YAML config (future enhancement)
2. Move result extraction logic to YAML config (adds complexity)
3. But **always keep the typed interface** - that's the architectural requirement

The current approach is the right balance between declarative configuration and architectural correctness.

