# Complex Iterative Specialist Pattern Template

**Date:** 2025-12-05  
**Status:** ✅ **PATTERN ESTABLISHED**

---

## 🎯 Pattern Overview

**Complex Iterative Specialist** pattern for agents that need:
- Multi-step workflows with refinement
- Tool feedback loops
- Iterative validation and improvement
- Complex reasoning across multiple iterations

**Example:** `UniversalMapperSpecialist` (mapping suggestions → validation → refinement → final validation)

---

## 📋 YAML Configuration Template

```yaml
agent_name: MyComplexSpecialist
role: Complex Specialist Role
goal: Complex specialist goal that requires iterative refinement
backstory: |
  You are an expert in [domain]. You excel at complex multi-step tasks
  that require careful analysis, validation, and iterative refinement.

instructions:
  - [Domain-specific instructions]
  - If using iterative execution, refine results across iterations
  - Use tool results from previous iterations to improve suggestions
  - Validate in early iterations, refine in later iterations
  - Stop iterating when results are complete and validated

allowed_mcp_servers:
  - [RelevantMCPServer]

allowed_tools:
  - [tool1]
  - [tool2]
  - [tool3]

capabilities:
  - [capability1]
  - [capability2]

llm_config:
  model: gpt-4o-mini
  temperature: 0.3
  max_tokens: 2000
  timeout: 120
  retry:
    enabled: true
    max_attempts: 3
    base_delay: 2.0
  rate_limiting:
    enabled: true
    capacity: 100
    refill_rate: 10

# Agent pattern configuration
stateful: false  # Stateless (no conversation history needed for task-focused agents)
max_conversation_history: 10  # Not used if stateful=false

# Execution configuration
iterative_execution: true  # Enable iterative refinement
max_iterations: 5  # Allow multiple iterations for complex workflows

# Observability configuration
cost_tracking: true  # Track LLM costs

tool_selection_strategy: autonomous
max_tool_calls_per_request: 5
```

---

## 🔄 Iterative Execution Flow

### **How It Works:**

1. **Iteration 1:** Initial analysis and tool execution
   - LLM analyzes request
   - Executes initial tools
   - Gets first results

2. **Iteration 2-N:** Refinement based on previous results
   - LLM reviews previous iteration results
   - Decides if more tools needed
   - Refines approach based on feedback
   - Executes additional tools if needed

3. **Final Iteration:** Complete and validated
   - LLM determines work is complete
   - Returns final results
   - No more tool calls needed

### **Example: Mapping Workflow**

**Iteration 1:**
- Analyze source and target schemas
- Generate initial mapping suggestions
- Execute `map_to_canonical_tool`

**Iteration 2:**
- Review mapping suggestions from iteration 1
- Validate suggestions
- Execute `validate_mapping_tool`
- Identify issues

**Iteration 3:**
- Review validation results
- Refine mappings based on validation
- Execute `map_to_canonical_tool` with refinements

**Iteration 4:**
- Final validation
- Confirm completeness
- Return final results

---

## 💻 Python Implementation Template

```python
class MyComplexSpecialist(DeclarativeAgentBase):
    """My Complex Specialist - Declarative Implementation."""
    
    def __init__(self, ...):
        """Initialize with declarative config."""
        config_path = Path(__file__).parent.parent / "configs" / "my_complex_specialist.yaml"
        super().__init__(
            agent_config_path=str(config_path),
            foundation_services=foundation_services,
            agentic_foundation=agentic_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            curator_foundation=curator_foundation,
            metadata_foundation=metadata_foundation,
            public_works_foundation=public_works_foundation,
            logger=logger
        )
    
    async def my_complex_task(self, input_data, user_context=None):
        """Complex task with iterative refinement."""
        request = {
            "message": f"Perform complex task with {input_data}",
            "task": "my_complex_task",
            "data": {"input": input_data},
            "user_context": user_context or {}
        }
        
        # Process request (iterative execution handled automatically)
        result = await self.process_request(request)
        
        # Extract results from iterations
        tool_results = result.get("tool_results", {})
        iterations = tool_results.get("iterations", [])
        
        # Format response
        response = {
            "success": result.get("success"),
            "result": extract_result_from_iterations(iterations),
            "iterations_used": len(iterations),
            "reasoning": result.get("reasoning", "")
        }
        
        # Preserve Priority 2 metadata
        if "cost_info" in result:
            response["cost_info"] = result["cost_info"]
        
        return response
```

---

## ✅ When to Use This Pattern

**Use Complex Iterative Specialist When:**
- ✅ Task requires multiple steps
- ✅ Results need validation and refinement
- ✅ Tool feedback improves results
- ✅ Complex reasoning across iterations
- ✅ Examples: Mapping, planning, blueprint generation, roadmap creation

**Don't Use When:**
- ❌ Simple, single-step tasks
- ❌ No validation/refinement needed
- ❌ Cost-sensitive (iterative = more LLM calls)
- ❌ Examples: Simple routing, basic recommendations

---

## 📊 Cost Considerations

**Iterative Execution Costs:**
- **Single-pass:** 1 LLM call per request
- **Iterative (3 iterations):** 3 LLM calls per request
- **Cost multiplier:** ~3x (but better results)

**Mitigation:**
- ✅ Cost tracking enabled
- ✅ Cost controls in tests
- ✅ Agent can stop early (no more tools needed)
- ✅ Max iterations limit (prevents runaway costs)

---

## 🎯 Success Criteria

**Pattern Working When:**
- ✅ Agent uses multiple iterations for complex tasks
- ✅ Results improve across iterations
- ✅ Agent stops when complete (no unnecessary iterations)
- ✅ Cost tracking shows iteration costs
- ✅ Response includes iteration metadata

---

## 📝 Example: UniversalMapperSpecialist

**Configuration:**
```yaml
iterative_execution: true
max_iterations: 5
```

**Workflow:**
1. **Iteration 1:** Suggest initial mappings
2. **Iteration 2:** Validate mappings
3. **Iteration 3:** Refine based on validation
4. **Iteration 4:** Final validation
5. **Done:** Return final mappings

**Benefits:**
- ✅ Better mapping quality
- ✅ Thorough validation
- ✅ Iterative refinement
- ✅ Production-ready pattern

---

## 🚀 Next Steps

1. ✅ **Pattern Established:** UniversalMapperSpecialist updated
2. ⏳ **Use as Template:** Reference for other complex specialists
3. ⏳ **Migrate Phase 1:** Stateless specialist, Stateful guide/liaison
4. ⏳ **Proceed with Remaining:** Use established patterns

---

## 💡 Key Insights

1. **Iterative execution is powerful** for complex tasks
2. **Cost controls are essential** (3x cost multiplier)
3. **Agent can stop early** (no unnecessary iterations)
4. **Better results** justify the cost for complex tasks
5. **Pattern is reusable** for other complex specialists







