# Stateful Conversational Pattern Template

**Date:** 2025-12-05  
**Status:** ✅ **PATTERN ESTABLISHED**

---

## 🎯 Pattern Overview

**Stateful Conversational** pattern for agents that need:
- Conversation history for contextual responses
- Multi-turn conversations within a session
- Remembering previous interactions
- Personalized, contextual guidance

**Example:** `InsuranceLiaisonAgent` (conversational guidance for insurance migration)

---

## 📋 YAML Configuration Template

```yaml
agent_name: MyConversationalAgent
role: Conversational Agent Role
goal: Provide conversational guidance and assistance
backstory: |
  You are an expert [domain] assistant. You help users understand and navigate
  [domain] processes. You maintain conversation context to provide personalized,
  contextual guidance.

instructions:
  - Maintain conversation context to provide personalized guidance
  - Understand user intent and respond appropriately
  - Remember previous conversation context when relevant
  - Provide clear, actionable next steps
  - Use available tools to help users accomplish their goals
  - Suggest appropriate actions based on user intent

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
stateful: true  # Stateful - maintains conversation history
max_conversation_history: 20  # Keep last N messages for context

# Execution configuration
iterative_execution: false  # Single-pass - conversational responses don't need iterative refinement
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
My Conversational Agent - Declarative Implementation

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


class MyConversationalAgent(DeclarativeAgentBase):
    """My Conversational Agent - Declarative Implementation."""
    
    def __init__(self, ...):
        """Initialize with declarative config."""
        config_path = Path(__file__).parent.parent / "configs" / "my_conversational_agent.yaml"
        super().__init__(
            agent_config_path=str(config_path),
            ...
        )
    
    async def handle_user_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle conversational user request.
        
        Args:
            request: User request containing:
                - message: User message
                - user_context: User context
                - session_id: Optional session ID
                - conversation_history: Optional conversation history
        
        Returns:
            Response with guidance and actions
        """
        # Build request for declarative agent
        declarative_request = {
            "message": request.get("message", ""),
            "task": "conversation",
            "data": {
                "session_id": request.get("session_id", "default")
            },
            "user_context": request.get("user_context", {}),
            "session_id": request.get("session_id", "default")
        }
        
        # Include conversation history if provided
        if "conversation_history" in request:
            declarative_request["conversation_history"] = request["conversation_history"]
        
        # Process request (conversation history handled automatically if stateful)
        result = await self.process_request(declarative_request)
        
        # Format response
        response = {
            "message": result.get("response", ""),
            "intent": extract_intent(result),
            "suggested_actions": extract_actions(result)
        }
        
        # Preserve Priority 2 metadata
        if "cost_info" in result:
            response["cost_info"] = result["cost_info"]
        if "conversation_history_length" in result:
            response["conversation_history_length"] = result["conversation_history_length"]
        
        return response
```

---

## 🔄 Conversation History Flow

### **How It Works:**

1. **First Message:**
   - User: "How do I ingest legacy data?"
   - Agent: [Provides guidance]
   - History: [User message, Agent response]

2. **Second Message (with context):**
   - User: "What format should I use?"
   - Agent: [Uses conversation history to know user is asking about ingestion]
   - History: [Previous messages + new messages]

3. **Context-Aware Responses:**
   - Agent remembers what was discussed
   - Provides contextual follow-up guidance
   - Suggests relevant next steps

---

## ✅ When to Use This Pattern

**Use Stateful Conversational When:**
- ✅ Conversational interface needed
- ✅ Context-dependent responses
- ✅ Multi-turn conversations
- ✅ Remembering previous interactions
- ✅ Examples: Chatbots, assistants, liaison agents, guide agents

**Don't Use When:**
- ❌ Simple, single-step tasks
- ❌ No conversation context needed
- ❌ Stateless task execution
- ❌ Examples: Simple routing, basic recommendations

---

## 📊 Cost Considerations

**Stateful Execution Costs:**
- **Single LLM call per request** (same as stateless)
- **Slightly more tokens** (conversation history included)
- **Cost increase:** ~10-20% (due to history tokens)

**Example:**
- Request 1: ~100 tokens
- Request 2 (with history): ~150 tokens (50 tokens history)
- Request 3 (with history): ~200 tokens (100 tokens history)

**Mitigation:**
- ✅ Max conversation history limit (prevents unbounded growth)
- ✅ Cost tracking enabled
- ✅ History truncation

---

## 🎯 Success Criteria

**Pattern Working When:**
- ✅ Agent maintains conversation history
- ✅ Responses reference previous context
- ✅ History length tracked in response
- ✅ History automatically truncated
- ✅ Context-aware suggestions provided

---

## 📝 Example: InsuranceLiaisonAgent

**Configuration:**
```yaml
stateful: true
max_conversation_history: 20
iterative_execution: false
cost_tracking: true
```

**Workflow:**
1. User: "How do I ingest data?"
2. Agent: [Provides guidance, stores in history]
3. User: "What format?"
4. Agent: [Uses history to know context, provides format guidance]
5. User: "Can you help me start?"
6. Agent: [Uses full history, provides step-by-step guidance]

**Benefits:**
- ✅ Contextual responses
- ✅ Personalized guidance
- ✅ Better user experience
- ✅ Natural conversation flow

---

## 🚀 Migration Checklist

For migrating a conversational agent:

- [ ] Create YAML config file
- [ ] Set `stateful: true`
- [ ] Set `max_conversation_history: 20` (or appropriate)
- [ ] Set `iterative_execution: false` (unless needed)
- [ ] Create declarative Python class
- [ ] Implement `handle_user_request()` or similar
- [ ] Include session_id support
- [ ] Preserve Priority 2 metadata
- [ ] Update imports (with fallback)
- [ ] Test conversation history
- [ ] Verify cost tracking
- [ ] Document as stateful conversational pattern

---

## 💡 Key Insights

1. **Stateful enables context** - Agent remembers conversation
2. **History limit prevents bloat** - Automatic truncation
3. **Slightly higher cost** - But better user experience
4. **Perfect for chatbots** - Natural conversation flow
5. **Production-ready** - All Priority 1 & 2 features enabled

---

## 🎉 Pattern Established!

**Stateful Conversational Pattern:**
- ✅ Conversation history maintained
- ✅ Context-aware responses
- ✅ Personalized guidance
- ✅ Production-ready

**Use this pattern for:**
- Guide agents (cross-domain navigation)
- Liaison agents (domain-specific conversation)
- Chatbots and assistants
- Any conversational interface







