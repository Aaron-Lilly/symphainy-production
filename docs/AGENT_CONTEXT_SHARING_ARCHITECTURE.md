# Agent Context Sharing Architecture

## Executive Summary

This document explains how agents get and share conversational context and analytics to enable the declarative agent + conversational analytics vision. It provides code examples for context management, context sharing between agents, and how services receive structured parameters from agents.

## Architecture Overview

### Context Flow

```
User Message
    ↓
Agent (LLM Reasoning)
    ↓
Extract Context / Generate Structured Params
    ↓
MCP Tool (Stateless)
    ↓
Service (Pure Data Processing)
    ↓
Response with Data
    ↓
Agent (Format Response)
    ↓
User
```

### Context Types

1. **Conversation Context**: Message history, current topic, user intent
2. **Specialization Context**: User goals, business domain, preferences
3. **Analytics Context**: Analysis results, query history, drill-down paths
4. **Session Context**: Session state, pillar progress, journey state

## Context Storage and Retrieval

### 1. Session-Based Context Storage

**Service:** `SessionManagerService` (already exists)

**Storage Structure:**

```python
# Session document structure
session_document = {
    "session_id": "session_123",
    "user_id": "user_456",
    "tenant_id": "tenant_789",
    "conversation_history": {
        "guide_agent": [
            {"role": "user", "content": "...", "timestamp": "..."},
            {"role": "assistant", "content": "...", "timestamp": "..."}
        ],
        "content_liaison": [...],
        "insights_liaison": [...]
    },
    "specialization_context": {
        "user_goals": "...",
        "business_domain": "...",
        "preferred_data_types": [...]
    },
    "analytics_context": {
        "current_analysis_id": "...",
        "query_history": [...],
        "drill_down_paths": [...]
    },
    "pillar_context": {
        "content": {
            "uploaded_files": [...],
            "current_file_id": "..."
        },
        "insights": {
            "current_analysis_id": "...",
            "last_query": "..."
        }
    }
}
```

### 2. Agent Context Retrieval (UPDATED - Simplified Pattern)

**✅ CORRECT Pattern:** Context is passed in `request` dict, not retrieved manually in agents

**Example: Content Liaison Agent (Corrected)**

```python
# backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/
#   content_analysis_orchestrator/agents/content_liaison_agent.py

class ContentLiaisonAgent(DeclarativeAgentBase):
    async def handle_user_query(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle user query with context passed in request dict.
        
        Base class handles conversation history automatically if stateful: true.
        Context should be passed in request dict, not retrieved manually.
        """
        # Context is already in request dict:
        # - conversation_history: Optional (base class manages if stateful)
        # - specialization_context: Optional (from Journey Orchestrator)
        # - pillar_context: Optional (from session)
        
        # Base class handles conversation history if stateful: true
        # Base class injects context into prompts automatically
        result = await self.process_request(request)
        
        # Format response
        return {
            "type": "liaison_response",
            "message": result.get("response", ""),
            "intent": self._extract_intent(result)
        }
```

**Context Building (In Orchestrator or Frontend):**

```python
# In orchestrator or frontend, before calling agent
async def build_request_with_context(
    self,
    user_message: str,
    session_id: str,
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Build request with all context."""
    
    # 1. Get conversation history from session (if needed for non-stateful agents)
    # Note: If stateful: true, base class handles this automatically
    conversation_history = await session_manager.get_conversation_history(
        session_id, 
        agent_type="content_liaison"
    )
    
    # 2. Get specialization context from MVPJourneyOrchestratorService
    mvp_orchestrator = await curator.discover_service_by_name("MVPJourneyOrchestratorService")
    specialization_context = await mvp_orchestrator.get_specialization_context(session_id)
    
    # 3. Get pillar-specific context from session
    session_data = await session_manager.get_session(session_id)
    pillar_context = session_data.get("pillar_context", {}).get("content", {})
    
    # 4. Build request with all context
    request = {
        "message": user_message,
        "session_id": session_id,
        "user_context": user_context,
        "conversation_history": conversation_history,  # Base class manages if stateful
        "specialization_context": specialization_context,  # From Journey Orchestrator
        "pillar_context": pillar_context  # From session
    }
    
    return request

# Call agent with context in request
request = await build_request_with_context(message, session_id, user_context)
response = await content_liaison_agent.handle_user_query(request)
```

**❌ WRONG Pattern (from old plans):**
```python
# Don't retrieve context manually in agent
conversation_history = await self._get_conversation_history(session_id)
specialization_context = await self._get_specialization_context(session_id)
# Base class handles conversation history if stateful: true
# Context should be passed in request dict
```

## Context Injection into LLM Prompts (UPDATED - Automatic)

### Declarative Agent Base Context Building

**File:** `backend/business_enablement/agents/declarative_agent_base.py`

**Method:** `_build_agent_prompt()`

**✅ CORRECT Pattern:** Base class automatically injects context from `request` dict

```python
def _build_agent_prompt(
    self,
    request: Dict[str, Any]
) -> str:
    """
    Build prompt for LLM with all context from request dict.
    
    This method is called by process_request() to build the full prompt
    that includes role, goal, backstory, instructions, conversation history,
    and additional context.
    """
    prompt_parts = []
    user_message = request.get("message", "")
    
    # 1. Agent identity (from YAML config)
    prompt_parts.append(f"Role: {self.agent_config.get('role', '')}")
    prompt_parts.append(f"Goal: {self.agent_config.get('goal', '')}")
    prompt_parts.append(f"Backstory: {self.agent_config.get('backstory', '')}")
    
    # 2. Instructions (from YAML config)
    instructions = self.agent_config.get('instructions', [])
    prompt_parts.append("Instructions:")
    for instruction in instructions:
        prompt_parts.append(f"- {instruction}")
    
    # 3. Specialization context (from request dict, if available)
    specialization_context = request.get("specialization_context")
    if specialization_context:
        prompt_parts.append("\nUser Specialization Context:")
        prompt_parts.append(f"- Business Domain: {specialization_context.get('business_domain', 'N/A')}")
        prompt_parts.append(f"- User Goals: {specialization_context.get('user_goals', 'N/A')}")
        prompt_parts.append(f"- Preferred Data Types: {', '.join(specialization_context.get('preferred_data_types', []))}")
        prompt_parts.append(f"- Focus Areas: {', '.join(specialization_context.get('focus_areas', []))}")
        prompt_parts.append("\nPlease personalize your responses based on this context.")
        prompt_parts.append("Prioritize tools and recommendations that align with the user's goals and domain.")
    
    # 4. Pillar context (from request dict, if available)
    pillar_context = request.get("pillar_context")
    if pillar_context:
        prompt_parts.append("\nCurrent Pillar Context:")
        for key, value in pillar_context.items():
            if value:
                prompt_parts.append(f"- {key}: {value}")
    
    # 5. Conversation history (automatically managed if stateful: true)
    conversation_history = request.get("conversation_history", [])
    if conversation_history:
        prompt_parts.append("\nConversation History:")
        # Base class handles truncation to max_conversation_history
        for msg in conversation_history[-self.max_conversation_history:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt_parts.append(f"{role.capitalize()}: {content}")
    
    # 6. Learned patterns (from knowledge base, if available) - NEW Enhancement
    learned_patterns = request.get("learned_patterns", [])
    if learned_patterns:
        prompt_parts.append("\nLearned Patterns (from previous interactions):")
        for pattern in learned_patterns:
            prompt_parts.append(f"- {pattern.get('description')}")
        prompt_parts.append("Use these patterns to provide more accurate and personalized responses.")
    
    # 7. Available tools
    prompt_parts.append("\nAvailable Tools:")
    for tool in self.available_tools:
        prompt_parts.append(f"- {tool['name']}: {tool['description']}")
    
    # 8. Current user message
    prompt_parts.append(f"\nUser Message: {user_message}")
    
    # 9. Instructions for response
    prompt_parts.append("\nPlease respond to the user's message, using tools if necessary.")
    prompt_parts.append("Maintain conversation context and provide helpful, personalized guidance.")
    
    return "\n".join(prompt_parts)
```

**Key Points:**
- Context is extracted from `request` dict, not retrieved manually
- Base class handles conversation history automatically if `stateful: true`
- Specialization context is injected into prompt automatically
- Pillar context is injected into prompt automatically
- Learned patterns can be injected (enhancement opportunity)

## Agent → Service: Structured Parameter Passing

### Example: Insights Liaison Agent → DataDrillDownService

**Agent Side (Insights Liaison Agent):**

```python
# backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/
#   insights_orchestrator/agents/insights_liaison_agent.py

class InsightsLiaisonAgent(DeclarativeAgentBase):
    async def process_user_query(
        self,
        query: str,
        analysis_id: str,
        conversation_id: str,
        user_context: UserContext
    ) -> Dict[str, Any]:
        """Process drill-down query."""
        
        # Get conversation history
        conversation_history = await self._get_conversation_history(conversation_id)
        
        # Get cached analysis for context
        cached_analysis = await self._get_cached_analysis(analysis_id)
        
        # Build request
        request = {
            "message": query,
            "analysis_id": analysis_id,
            "cached_analysis": cached_analysis,
            "conversation_history": conversation_history,
            "user_context": user_context
        }
        
        # LLM reasoning extracts intent and entities
        result = await self.process_request(request)
        
        # The LLM response includes tool calls with structured parameters
        # Example tool call from LLM:
        # {
        #   "name": "drill_down_into_data_tool",
        #   "parameters": {
        #     "filter_criteria": {
        #       "field": "days_overdue",
        #       "operator": ">=",
        #       "value": 90
        #     },
        #     "data_source": "customer_data",
        #     "max_results": 100
        #   }
        # }
        
        return result
```

**MCP Tool (Insights MCP Server):**

```python
# backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/
#   insights_orchestrator/mcp_server/insights_mcp_server.py

@mcp_tool
async def drill_down_into_data_tool(
    filter_criteria: Dict[str, Any],  # Structured from agent LLM
    insight_summary: str,
    data_source: str,
    max_results: int = 100,
    user_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Drill down into specific data records.
    
    Agent's LLM extracts filter_criteria from user query and calls this tool.
    """
    # Get Data Drill-Down Service
    service = await orchestrator.get_enabling_service("DataDrillDownService")
    if not service:
        return {"success": False, "error": "Data Drill-Down Service not available"}
    
    # Call service with structured parameters (NO LLM in service)
    result = await service.get_filtered_records(
        filter_criteria=filter_criteria,  # Already structured by agent LLM
        data_source=data_source,
        max_results=max_results,
        user_context=user_context
    )
    
    return result
```

**Service Side (DataDrillDownService):**

```python
# backend/business_enablement/enabling_services/data_drill_down_service/
#   data_drill_down_service.py

class DataDrillDownService(RealmServiceBase):
    """
    Pure data processing service - NO LLM.
    Agents handle all LLM reasoning and extract structured parameters.
    """
    
    async def get_filtered_records(
        self,
        filter_criteria: Dict[str, Any],  # Structured from agent LLM
        data_source: str,
        max_results: int = 100,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get filtered records from data source.
        
        Args:
            filter_criteria: {
                "field": "days_overdue",
                "operator": ">=",
                "value": 90
            }
            data_source: Source identifier
            max_results: Maximum number of results
            user_context: User context for security/tenant validation
        
        Returns:
            Filtered records with details
        """
        # Pure data processing - no LLM
        
        # 1. Validate filter criteria structure
        if not self._validate_filter_criteria(filter_criteria):
            return {
                "success": False,
                "error": "Invalid filter criteria structure"
            }
        
        # 2. Get data from Data Steward
        data_steward = await self.get_data_steward_api()
        if not data_steward:
            return {
                "success": False,
                "error": "Data Steward not available"
            }
        
        # 3. Query data with filter
        # Convert filter_criteria to query format
        query = self._build_query(filter_criteria, data_source)
        
        # 4. Execute query
        records = await data_steward.query_data(
            query=query,
            limit=max_results,
            user_context=user_context
        )
        
        # 5. Format results
        return {
            "success": True,
            "records": records,
            "count": len(records),
            "filter_applied": filter_criteria
        }
    
    def _validate_filter_criteria(self, criteria: Dict[str, Any]) -> bool:
        """Validate filter criteria structure."""
        required_fields = ["field", "operator", "value"]
        return all(field in criteria for field in required_fields)
    
    def _build_query(self, filter_criteria: Dict[str, Any], data_source: str) -> Dict[str, Any]:
        """Build query from filter criteria."""
        return {
            "source": data_source,
            "filters": [filter_criteria],
            "select": "*"  # Get all fields
        }
```

## Specialization Context Sharing (UPDATED - Use Existing MVPJourneyOrchestratorService)

### Landing Page → MVPJourneyOrchestratorService → Liaison Agents

**Step 1: Landing Page Conversation (UPDATED)**

```python
# MVPJourneyOrchestratorService handles landing page conversation
# Add this method to existing MVPJourneyOrchestratorService

async def handle_landing_page_conversation(
    self,
    message: str,
    session_id: str,
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Handle landing page conversation with Guide Agent."""
    
    # Get conversation history from session (if needed)
    # Note: If stateful: true, base class handles this automatically
    conversation_history = await self._get_conversation_history(session_id)
    
    # Process with Guide Agent (already exists: self.guide_agent)
    request = {
        "message": message,
        "session_id": session_id,
        "user_context": user_context,
        "conversation_history": conversation_history,  # Base class manages if stateful
        "conversation_stage": "landing_page"
    }
    
    result = await self.guide_agent.handle_user_request(request)
    
    # Guide Agent's LLM extracts specialization context
    # The LLM response includes a tool call:
    # {
    #   "name": "store_specialization_context_tool",
    #   "parameters": {
    #     "specialization_context": {
    #       "user_goals": "Improve customer satisfaction",
    #       "business_domain": "retail",
    #       "industry": "retail",
    #       "preferred_data_types": ["customer_feedback", "support_tickets"],
    #       "focus_areas": ["customer_experience", "response_time"]
    #     }
    #   }
    # }
    
    # Tool call is executed, context is stored
    if result.get("tool_calls"):
        for tool_call in result["tool_calls"]:
            if tool_call["name"] == "store_specialization_context_tool":
                await self._store_specialization_context(
                    session_id,
                    tool_call["parameters"]["specialization_context"]
                )
    
    return result
```

**Step 2: Store Specialization Context**

```python
async def _store_specialization_context(
    self,
    session_id: str,
    context: Dict[str, Any]
):
    """Store specialization context in session."""
    # Store in orchestrator's local dict
    self.specialization_context[session_id] = context
    
    # Also store in session via Session Manager
    session_manager = await self._get_session_manager()
    if session_manager:
        await session_manager.update_session(
            session_id=session_id,
            updates={
                "specialization_context": context
            }
        )
```

**Step 3: Share with Liaison Agents (UPDATED - Simplified)**

**✅ CORRECT Pattern:** Pass context in `request` dict, don't retrieve in agent

```python
# In orchestrator or frontend, when calling liaison agent
async def call_liaison_agent_with_context(
    self,
    liaison_agent: DeclarativeAgentBase,
    user_message: str,
    session_id: str,
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Call liaison agent with all context in request dict."""
    
    # Get specialization context from MVPJourneyOrchestratorService
    mvp_orchestrator = await curator.discover_service_by_name("MVPJourneyOrchestratorService")
    specialization_context = await mvp_orchestrator.get_specialization_context(session_id)
    
    # Get pillar context from session
    session_data = await session_manager.get_session(session_id)
    pillar_context = session_data.get("pillar_context", {}).get("content", {})
    
    # Build request with all context
    request = {
        "message": user_message,
        "session_id": session_id,
        "user_context": user_context,
        "specialization_context": specialization_context,  # From MVPJourneyOrchestratorService
        "pillar_context": pillar_context  # From session
        # conversation_history: Base class manages if stateful: true
    }
    
    # Agent receives context in request, base class injects into prompt
    return await liaison_agent.handle_user_query(request)
```

**❌ WRONG Pattern (from old plans):**
```python
# Don't retrieve context in agent
specialization_context = await self._get_specialization_context(session_id)
# Pass in request dict instead
```

**Step 4: Apply Specialization to Agent Behavior (Automatic)**

**✅ CORRECT Pattern:** Base class automatically injects context into prompts

```python
# In DeclarativeAgentBase._build_agent_prompt()
# Context is automatically extracted from request dict and injected into prompt
# No manual application needed - base class handles it

# Specialization context is injected automatically if present in request:
if specialization_context:
    prompt_parts.append("\nUser Specialization Context:")
    prompt_parts.append(f"- Business Domain: {specialization_context.get('business_domain')}")
    prompt_parts.append(f"- Goals: {specialization_context.get('user_goals')}")
    prompt_parts.append(f"- Focus Areas: {', '.join(specialization_context.get('focus_areas', []))}")
    prompt_parts.append("\nPlease personalize your responses based on this context.")
    prompt_parts.append("Prioritize tools and recommendations that align with the user's goals and domain.")
```

**No manual application needed - base class handles context injection automatically!**

## Analytics Context Sharing

### Insights Pillar: Query → Drill-Down Flow

**Step 1: User Asks Initial Question**

```python
# Insights Liaison Agent
async def process_user_query(
    self,
    query: str,  # "What are my top customers?"
    analysis_id: str,
    conversation_id: str,
    user_context: UserContext
) -> Dict[str, Any]:
    # Get conversation history
    conversation_history = await self._get_conversation_history(conversation_id)
    
    # Get cached analysis
    cached_analysis = await self._get_cached_analysis(analysis_id)
    
    request = {
        "message": query,
        "analysis_id": analysis_id,
        "cached_analysis": cached_analysis,
        "conversation_history": conversation_history
    }
    
    # LLM extracts: intent="top_n_query", entities={"metric": "customers", "n": 5}
    result = await self.process_request(request)
    
    # Agent calls: query_data_insights_tool(query_params, ...)
    # Returns: "Your top 5 customers are: Acme Corp ($50K), Beta Inc ($45K), ..."
    
    # Store query in analytics context
    await self._store_analytics_query(conversation_id, {
        "query": query,
        "intent": "top_n_query",
        "result_summary": "5 customers identified"
    })
    
    return result
```

**Step 2: User Asks Follow-Up (Drill-Down)**

```python
# User: "Which ones are they?"
async def process_user_query(
    self,
    query: str,  # "Which ones are they?"
    analysis_id: str,
    conversation_id: str,
    user_context: UserContext
) -> Dict[str, Any]:
    # Get conversation history (includes previous query and response)
    conversation_history = await self._get_conversation_history(conversation_id)
    
    # Get analytics context (previous query results)
    analytics_context = await self._get_analytics_context(conversation_id)
    
    request = {
        "message": query,
        "analysis_id": analysis_id,
        "conversation_history": conversation_history,  # Contains "top 5 customers" context
        "analytics_context": analytics_context  # Previous query: top_n_query
    }
    
    # LLM reasoning:
    # - Understands "which ones" refers to previous "top 5 customers"
    # - Extracts: intent="drill_down", entities={"reference": "previous_query", "filter": "top_5_customers"}
    # - Calls: drill_down_into_data_tool(filter_criteria, ...)
    
    result = await self.process_request(request)
    
    return result
```

**Step 3: Analytics Context Storage**

```python
async def _store_analytics_query(
    self,
    conversation_id: str,
    query_info: Dict[str, Any]
):
    """Store analytics query in session."""
    session_manager = await self._get_session_manager()
    if session_manager:
        # Get current analytics context
        session_data = await session_manager.get_session(conversation_id)
        analytics_context = session_data.get("analytics_context", {})
        
        # Add query to history
        query_history = analytics_context.get("query_history", [])
        query_history.append(query_info)
        
        # Update analytics context
        analytics_context["query_history"] = query_history
        analytics_context["last_query"] = query_info
        
        # Store back in session
        await session_manager.update_session(
            session_id=conversation_id,
            updates={"analytics_context": analytics_context}
        )
```

## Context Passing to Services

### Example: Data Insights Query Service

**Agent Side:**

```python
# Insights Liaison Agent's LLM extracts structured params
# LLM response includes:
{
    "tool_calls": [{
        "name": "query_data_insights_tool",
        "parameters": {
            "query_params": {
                "intent": "drill_down",
                "entities": {
                    "metric": "customers",
                    "filter": {
                        "field": "days_overdue",
                        "operator": ">=",
                        "value": 90
                    }
                },
                "query_type": "filter"
            },
            "analysis_id": "analysis_123"
        }
    }]
}
```

**MCP Tool:**

```python
@mcp_tool
async def query_data_insights_tool(
    query_params: Dict[str, Any],  # Structured from agent LLM
    analysis_id: str,
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Query data insights with structured parameters."""
    # Get Data Insights Query Service
    service = orchestrator.data_insights_query_service
    
    # Get cached analysis
    cached_analysis = orchestrator.analysis_cache.get(analysis_id)
    
    # Call service with structured params (NO LLM in service)
    result = await service.process_query(
        query_params=query_params,  # Already structured
        analysis_id=analysis_id,
        cached_analysis=cached_analysis,
        user_context=user_context
    )
    
    return result
```

**Service Side:**

```python
# Data Insights Query Service (NO LLM)
async def process_query(
    self,
    query_params: Dict[str, Any],  # Structured from agent LLM
    analysis_id: str,
    cached_analysis: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process query with structured parameters.
    
    Args:
        query_params: {
            "intent": "drill_down",
            "entities": {
                "metric": "customers",
                "filter": {"field": "days_overdue", "operator": ">=", "value": 90}
            },
            "query_type": "filter"
        }
    """
    # Pure data processing - no LLM
    
    intent = query_params.get("intent")
    entities = query_params.get("entities", {})
    
    # Route to appropriate handler (rule-based)
    if intent == "drill_down":
        return self._execute_drill_down(entities, cached_analysis)
    elif intent == "filter":
        return self._execute_filter(entities, cached_analysis)
    elif intent == "top_n_query":
        return self._execute_top_n(entities, cached_analysis)
    # ... etc
    
    return {"success": False, "error": "Unknown intent"}
```

## Dynamic Specialization Assignment

### Landing Page → Agent Configuration

**Step 1: Capture Specialization in Landing Page**

```python
# Journey Orchestrator - Landing Page Conversation
async def handle_landing_page_conversation(...):
    # Guide Agent conversation extracts specialization
    result = await self.guide_agent.process_request(request)
    
    # Extract specialization context from LLM response
    specialization = self._extract_specialization_from_response(result)
    
    # Store in session
    await self._store_specialization_context(session_id, specialization)
    
    return {
        "response": result.get("response"),
        "specialization_context": specialization
    }
```

**Step 2: Share with Liaison Agents**

```python
# When liaison agent processes first query
async def process_user_query(self, query: str, session_id: str, ...):
    # Get specialization context
    specialization = await self._get_specialization_context(session_id)
    
    # Apply to agent's context
    if specialization:
        # Update agent's understanding
        self.user_domain = specialization.get("business_domain")
        self.user_goals = specialization.get("user_goals")
        
        # Context is injected into LLM prompt
        # Agent's responses will be personalized
    
    # Process query with specialization context
    request = {
        "message": query,
        "specialization_context": specialization,
        ...
    }
    
    return await self.process_request(request)
```

**Step 3: Agent Uses Specialization in Responses**

```python
# Agent's LLM prompt includes specialization context
# Example prompt:
"""
Role: Content Management Assistant
Goal: Help users manage, parse, and understand their content files

User Context:
- Business Domain: retail
- Goals: Improve customer satisfaction
- Preferred Data Types: customer_feedback, support_tickets
- Focus Areas: customer_experience, response_time

Conversation History:
User: "I want to upload my customer feedback data"
Assistant: [Previous response]

User Message: "What format should I use?"

Please respond based on the user's context. Since they're working with
customer feedback for satisfaction improvement, recommend formats that
support sentiment analysis and trend tracking.
"""

# Agent's LLM will generate personalized response:
# "For customer feedback analysis focused on satisfaction improvement,
#  I recommend using JSON structured format. This will allow you to
#  analyze sentiment trends and identify key themes in your feedback data.
#  Would you like me to help you convert your data to this format?"
```

## Code Examples Summary (UPDATED - Correct Patterns)

### 1. Build Request with Context (In Orchestrator or Frontend)

**✅ CORRECT Pattern:**
```python
# In orchestrator or frontend, before calling agent
async def build_request_with_context(
    user_message: str,
    session_id: str,
    user_context: Dict[str, Any],
    mvp_orchestrator: MVPJourneyOrchestratorService,
    session_manager: SessionManager
) -> Dict[str, Any]:
    """Build request with all context."""
    
    # Get specialization context from MVPJourneyOrchestratorService
    specialization_context = await mvp_orchestrator.get_specialization_context(session_id)
    
    # Get pillar context from session
    session_data = await session_manager.get_session(session_id)
    pillar_context = session_data.get("pillar_context", {}).get("content", {})
    
    # Build request with all context
    request = {
        "message": user_message,
        "session_id": session_id,
        "user_context": user_context,
        "specialization_context": specialization_context,  # From Journey Orchestrator
        "pillar_context": pillar_context  # From session
        # conversation_history: Base class manages if stateful: true
    }
    
    return request
```

**❌ WRONG Pattern (from old plans):**
```python
# Don't retrieve context in agent
conversation_history = await self._get_conversation_history(session_id)
# Pass in request dict instead
```

### 2. Agent Extracts Structured Params

```python
# LLM reasoning in process_request() extracts:
{
    "intent": "drill_down",
    "entities": {
        "metric": "customers",
        "filter": {"field": "days_overdue", "operator": ">=", "value": 90}
    }
}

# Agent calls tool with structured params
await tool.call({
    "filter_criteria": entities["filter"],
    "data_source": "customer_data"
})
```

### 3. Service Receives Structured Params

```python
# Service receives structured params (NO LLM)
async def get_filtered_records(
    self,
    filter_criteria: Dict[str, Any],  # Already structured
    data_source: str,
    ...
) -> Dict[str, Any]:
    # Pure data processing
    query = self._build_query(filter_criteria)
    records = await data_steward.query_data(query)
    return {"success": True, "records": records}
```

### 4. Context Sharing Between Agents (UPDATED - Simplified)

**✅ CORRECT Pattern:**
```python
# MVPJourneyOrchestratorService stores specialization
await mvp_orchestrator._store_specialization_context(session_id, context)

# When calling liaison agent, pass context in request dict
specialization = await mvp_orchestrator.get_specialization_context(session_id)

request = {
    "message": user_message,
    "specialization_context": specialization,  # Pass in request dict
    # ... other context
}

# Agent receives context, base class injects into prompt automatically
response = await liaison_agent.handle_user_query(request)
```

**❌ WRONG Pattern (from old plans):**
```python
# Don't retrieve in agent
specialization = await journey_orchestrator.get_specialization_context(session_id)
# Pass in request dict instead
```

## Best Practices (UPDATED)

1. **Pass Context in Request Dict**: Don't retrieve context manually in agents - pass in `request` dict
2. **Let Base Class Handle Conversation History**: If `stateful: true`, base class manages conversation history automatically
3. **Store Context Updates**: When context changes, update session immediately
4. **Validate Structured Params**: Services should validate params from agents
5. **Handle Missing Context**: Gracefully handle cases where context isn't available
6. **Context Boundaries**: Keep context focused and relevant
7. **Performance**: Cache context retrieval when possible (in orchestrator/frontend)
8. **Privacy**: Respect tenant isolation in context sharing
9. **Use Existing Orchestrators**: Use `MVPJourneyOrchestratorService` for specialization context, don't create new ones
10. **Automatic Context Injection**: Base class automatically injects context into prompts - no manual application needed

## Conclusion (UPDATED)

This architecture enables:
1. **Natural Language Interaction**: Agents understand context from conversations
2. **Personalized Responses**: Specialization context personalizes all interactions
3. **Progressive Exploration**: Analytics context enables drill-down queries
4. **Service Purity**: Services receive structured params, no LLM needed
5. **Context Persistence**: All context stored in session, shared across agents
6. **Simplified Context Management**: Context passed in `request` dict, base class handles conversation history
7. **Automatic Context Injection**: Base class automatically injects context into prompts

**Key Principles:**
- **Agents extract and structure, Services process and return data**
- **Context passed in `request` dict, not retrieved manually**
- **Base class handles conversation history automatically if `stateful: true`**
- **Use existing `MVPJourneyOrchestratorService` for specialization context**

**Enhancement Opportunities:**
- Agent-to-Agent Collaboration (agents call other agents as tools)
- Agent Learning (store patterns in knowledge base)
- Cross-Pillar Collaboration (agents work together)
- See `AGENTIC_PLATFORM_ENHANCEMENT_OPPORTUNITIES.md` for details


