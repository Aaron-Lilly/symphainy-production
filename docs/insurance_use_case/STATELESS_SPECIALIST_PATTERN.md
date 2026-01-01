# Stateless Specialist Pattern Template

**Date:** 2025-12-05  
**Status:** ✅ **PATTERN ESTABLISHED**

---

## 🎯 Pattern Overview

**Stateless Specialist** pattern for simple, task-focused agents that:
- Don't need conversation history
- Execute in single-pass (no iterative refinement)
- Are fast and lightweight
- Perfect for recommendations, routing, quality checks

**Example:** `RecommendationSpecialist` (generate recommendations from analysis data)

---

## 📋 YAML Configuration Template

```yaml
agent_name: MyStatelessSpecialist
role: Specialist Role
goal: Simple, focused goal that can be achieved in a single pass
backstory: |
  You are an expert in [domain]. You excel at [specific task] and can provide
  quick, accurate results based on input data.

instructions:
  - [Domain-specific instructions]
  - Analyze input data carefully
  - Provide clear, actionable results
  - Use available tools when needed

allowed_mcp_servers:
  - [RelevantMCPServer]

allowed_tools:
  - [tool1]
  - [tool2]

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
stateful: false  # Stateless - no conversation history
max_conversation_history: 10  # Not used if stateful=false

# Execution configuration
iterative_execution: false  # Single-pass execution
max_iterations: 5  # Not used if iterative_execution=false

# Observability configuration
cost_tracking: true  # Track LLM costs

tool_selection_strategy: autonomous
max_tool_calls_per_request: 5
```

---

## 💻 Python Implementation Template

```python
"""
My Stateless Specialist Agent - Declarative Implementation

Migrated to declarative pattern: configuration-driven agent execution
where LLM does the reasoning instead of hardcoded logic.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import logging

from foundations.di_container.di_container_service import DIContainerService
from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
from foundations.agentic_foundation.agent_sdk.mcp_client_manager import MCPClientManager
from foundations.agentic_foundation.agent_sdk.policy_integration import PolicyIntegration
from foundations.agentic_foundation.agent_sdk.tool_composition import ToolComposition
from foundations.agentic_foundation.agent_sdk.agui_output_formatter import AGUIOutputFormatter

from ..declarative_agent_base import DeclarativeAgentBase


class MyStatelessSpecialist(DeclarativeAgentBase):
    """My Stateless Specialist - Declarative Implementation."""
    
    def __init__(self,
                 foundation_services: DIContainerService,
                 agentic_foundation: AgenticFoundationService,
                 mcp_client_manager: MCPClientManager,
                 policy_integration: PolicyIntegration,
                 tool_composition: ToolComposition,
                 agui_formatter: AGUIOutputFormatter,
                 curator_foundation=None,
                 metadata_foundation=None,
                 public_works_foundation=None,
                 logger: Optional[logging.Logger] = None):
        """Initialize with declarative config."""
        config_path = Path(__file__).parent.parent / "configs" / "my_stateless_specialist.yaml"
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
            logger=logger or logging.getLogger("MyStatelessSpecialist")
        )
    
    async def my_domain_method(self, input_data, user_context=None):
        """Domain method - calls process_request()."""
        request = {
            "message": f"Perform task with {input_data}",
            "task": "my_task",
            "data": {"input": input_data},
            "user_context": user_context or {}
        }
        
        # Process request (single-pass execution)
        result = await self.process_request(request)
        
        # Extract and format response
        response = {
            "success": result.get("success"),
            "result": extract_result(result),
            "reasoning": result.get("reasoning", "")
        }
        
        # Preserve Priority 2 metadata
        if "cost_info" in result:
            response["cost_info"] = result["cost_info"]
        if "conversation_history_length" in result:
            response["conversation_history_length"] = result["conversation_history_length"]
        
        return response
```

---

## ✅ When to Use This Pattern

**Use Stateless Specialist When:**
- ✅ Simple, single-step tasks
- ✅ No conversation context needed
- ✅ Fast response time important
- ✅ Cost-sensitive (single LLM call)
- ✅ Examples: Recommendations, routing, quality checks, simple analysis

**Don't Use When:**
- ❌ Need conversation history
- ❌ Multi-step refinement needed
- ❌ Complex iterative workflows
- ❌ Examples: Complex planning, blueprint generation, multi-turn conversations

---

## 📊 Cost Considerations

**Stateless Execution Costs:**
- **Single LLM call per request**
- **Lowest cost pattern**
- **Fastest response time**

**Example:**
- Request: Generate recommendations
- LLM call: 1
- Cost: ~$0.0001-0.0005 per request
- Response time: ~2-5 seconds

---

## 🎯 Success Criteria

**Pattern Working When:**
- ✅ Agent processes requests independently
- ✅ No conversation history maintained
- ✅ Single LLM call per request
- ✅ Fast response time
- ✅ Cost tracking shows single call
- ✅ Response includes cost metadata

---

## 📝 Example: RecommendationSpecialist

**Configuration:**
```yaml
stateful: false
iterative_execution: false
cost_tracking: true
```

**Workflow:**
1. Receive request with analysis data
2. Build prompt with data and context
3. Call LLM (single call)
4. Extract recommendations
5. Return formatted response

**Benefits:**
- ✅ Fast (single LLM call)
- ✅ Low cost
- ✅ Simple and reliable
- ✅ Production-ready

---

## 🚀 Migration Checklist

For migrating a stateless specialist:

- [ ] Create YAML config file
- [ ] Set `stateful: false`
- [ ] Set `iterative_execution: false`
- [ ] Create declarative Python class
- [ ] Implement domain method(s)
- [ ] Preserve Priority 2 metadata
- [ ] Update imports (with fallback)
- [ ] Test functionality
- [ ] Verify cost tracking
- [ ] Document as stateless specialist pattern

---

## 💡 Key Insights

1. **Stateless is simplest** - no conversation history to manage
2. **Single-pass is fastest** - one LLM call per request
3. **Lowest cost** - minimal LLM usage
4. **Perfect for simple tasks** - recommendations, routing, checks
5. **Production-ready** - all Priority 1 & 2 features enabled

---

## 🎉 Pattern Established!

**Stateless Specialist Pattern:**
- ✅ Simple and fast
- ✅ Low cost
- ✅ Production-ready
- ✅ Perfect template for simple specialists

**Use this pattern for:**
- `RoutingDecisionSpecialist`
- `QualityRemediationSpecialist`
- Other simple, single-purpose specialists







