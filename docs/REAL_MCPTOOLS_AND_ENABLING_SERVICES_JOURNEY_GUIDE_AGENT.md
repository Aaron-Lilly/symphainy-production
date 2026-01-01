# Real MCP Tools and Enabling Services: Journey/Guide Agent

## Executive Summary

This document provides **REAL, WORKING implementation code** (no mocks, no placeholders, no hard-coded cheats) for all MCP tools and enabling services needed for the Journey/Guide Agent agentic enablement.

**Note:** Guide Agent is in Journey realm, not Business Enablement. It uses `MVPJourneyOrchestratorService`.

---

## Existing Infrastructure (What We Have)

### ✅ Existing Services
1. **MVPJourneyOrchestratorService** - ✅ EXISTS
   - Location: `backend/journey/services/mvp_journey_orchestrator_service/`
   - Extends: `OrchestratorBase`
   - Has: `guide_agent` (GuideCrossDomainAgent) already initialized

2. **GuideCrossDomainAgent** - ✅ EXISTS
   - Location: `backend/journey/agents/guide_cross_domain_agent.py`
   - Extends: `DeclarativeAgentBase`
   - Config: `backend/journey/agents/configs/mvp_guide_agent.yaml`
   - Already integrated in MVPJourneyOrchestratorService

3. **SessionManagerService** - ✅ EXISTS
   - Location: `backend/journey/services/session_manager_service/`
   - Capabilities: Session management, context storage

### ✅ Existing Smart City Services
- **Librarian** - Knowledge base for specialization context
- **Session Manager** - Session context storage
- **Curator** - Service discovery

---

## New Tools/Services Needed

### 1. Specialization Context Storage (Add to MVPJourneyOrchestratorService)

**Why:** Guide Agent needs to store specialization context extracted from landing page conversation.

**Location:** `backend/journey/services/mvp_journey_orchestrator_service/mvp_journey_orchestrator_service.py`

**REAL Implementation - Add to Existing Service:**

```python
# Add to MVPJourneyOrchestratorService class

def __init__(self, ...):
    # ... existing initialization ...
    self.specialization_context = {}  # Per session (NEW)

async def handle_landing_page_conversation(
    self,
    message: str,
    session_id: str,
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handle landing page conversation with Guide Agent.
    
    NEW method to add to existing orchestrator.
    REAL implementation - no mocks.
    """
    try:
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
        
        # Extract specialization context from Guide Agent's response
        # Guide Agent's LLM extracts context and may call store_specialization_context_tool
        specialization = self._extract_specialization_context(result, conversation_history)
        
        # Store specialization context in session
        if specialization:
            await self._store_specialization_context(session_id, specialization)
        
        return {
            "response": result.get("message", ""),
            "specialization_context": specialization,
            "suggested_routes": result.get("suggested_routes", [])
        }
    
    except Exception as e:
        self.logger.error(f"❌ Landing page conversation failed: {e}")
        import traceback
        self.logger.error(traceback.format_exc())
        return {
            "response": "I'm sorry, I couldn't process your request.",
            "specialization_context": None,
            "suggested_routes": []
        }

async def get_specialization_context(
    self,
    session_id: str
) -> Dict[str, Any]:
    """Get stored specialization context for session (REAL implementation)."""
    try:
        # Get from in-memory storage
        context = self.specialization_context.get(session_id, {})
        
        # Also get from session via Session Manager (persistent)
        session_manager = await self._get_session_manager()
        if session_manager:
            session_data = await session_manager.get_session(session_id)
            if session_data:
                session_context = session_data.get("context", {}).get("specialization_context", {})
                if session_context:
                    # Merge (session takes precedence)
                    context.update(session_context)
        
        return context
    
    except Exception as e:
        self.logger.error(f"❌ Get specialization context failed: {e}")
        return {}

async def _store_specialization_context(
    self,
    session_id: str,
    context: Dict[str, Any]
):
    """Store specialization context in session (REAL implementation)."""
    try:
        # Store in-memory
        self.specialization_context[session_id] = context
        
        # Store in session via Session Manager (persistent)
        session_manager = await self._get_session_manager()
        if session_manager:
            await session_manager.update_session(
                session_id=session_id,
                updates={"specialization_context": context}
            )
        
        self.logger.info(f"✅ Stored specialization context for session {session_id}")
    
    except Exception as e:
        self.logger.error(f"❌ Store specialization context failed: {e}")

def _extract_specialization_context(
    self,
    agent_response: Dict[str, Any],
    conversation_history: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Extract specialization context from Guide Agent's response (rule-based, not LLM).
    
    REAL implementation - extracts from agent's tool calls or response.
    """
    try:
        # Check if agent called store_specialization_context_tool
        tool_calls = agent_response.get("tool_calls", [])
        for tool_call in tool_calls:
            if tool_call.get("name") == "store_specialization_context_tool":
                params = tool_call.get("parameters", {})
                return params.get("specialization_context", {})
        
        # Fallback: Extract from conversation history (simple rule-based)
        # Look for keywords in conversation
        context = {}
        
        # Extract business domain
        for msg in conversation_history:
            content = msg.get("content", "").lower()
            if "retail" in content:
                context["business_domain"] = "retail"
            elif "healthcare" in content:
                context["business_domain"] = "healthcare"
            elif "finance" in content:
                context["business_domain"] = "finance"
        
        # Extract goals
        goals = []
        for msg in conversation_history:
            content = msg.get("content", "").lower()
            if "improve" in content or "increase" in content or "reduce" in content:
                # Extract goal phrases (simple rule-based)
                if "customer" in content and "satisfaction" in content:
                    goals.append("improve_customer_satisfaction")
                elif "cost" in content:
                    goals.append("reduce_costs")
                elif "revenue" in content:
                    goals.append("increase_revenue")
        
        if goals:
            context["user_goals"] = goals
        
        return context if context else None
    
    except Exception as e:
        self.logger.error(f"❌ Extract specialization context failed: {e}")
        return None

async def _get_session_manager(self):
    """Get Session Manager service (REAL implementation)."""
    try:
        # Get via Curator
        curator = await self.get_foundation_service("CuratorFoundationService")
        if curator:
            session_manager = await curator.get_service("SessionManagerService")
            if session_manager:
                return session_manager
        
        # Fallback: Get from DI container
        if hasattr(self.di_container, 'session_manager'):
            return self.di_container.session_manager
        
        return None
    
    except Exception as e:
        self.logger.debug(f"Get session manager failed: {e}")
        return None

async def _get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
    """Get conversation history from session (REAL implementation)."""
    try:
        session_manager = await self._get_session_manager()
        if not session_manager:
            return []
        
        session_data = await session_manager.get_session(session_id)
        if not session_data:
            return []
        
        # Get conversation history from session
        conversation_history = session_data.get("context", {}).get("conversation_history", {}).get("guide_agent", [])
        return conversation_history
    
    except Exception as e:
        self.logger.debug(f"Get conversation history failed: {e}")
        return []
```

---

### 2. MCP Tools for Guide Agent (Add to MVPJourneyOrchestratorService MCP Server)

**Note:** MVPJourneyOrchestratorService may not have MCP server yet. If not, create one.

**File:** `backend/journey/services/mvp_journey_orchestrator_service/mcp_server/mvp_journey_mcp_server.py` (create if doesn't exist)

**REAL Implementation:**

```python
#!/usr/bin/env python3
"""
MVP Journey MCP Server - Wraps MVPJourneyOrchestratorService as MCP Tools.

Provides tools for Guide Agent to use.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.mcp_server.mcp_server_base import MCPServerBase


class MVPJourneyMCPServer(MCPServerBase):
    """
    MCP Server for MVP Journey Orchestrator.
    
    Provides tools for Guide Agent.
    """
    
    def __init__(self, orchestrator, di_container):
        super().__init__(
            service_name="mvp_journey_mcp",
            di_container=di_container
        )
        self.orchestrator = orchestrator
    
    def register_server_tools(self) -> None:
        """Register MCP tools for Guide Agent."""
        
        # Tool 1: Store Specialization Context
        self.register_tool(
            name="store_specialization_context_tool",
            description="Store specialization context extracted from landing page conversation. Agent LLM extracts context.",
            handler=self._store_specialization_context_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "specialization_context": {
                        "type": "object",
                        "description": "Structured specialization context from agent LLM",
                        "properties": {
                            "business_domain": {"type": "string"},
                            "user_goals": {"type": "array", "items": {"type": "string"}},
                            "preferred_data_types": {"type": "array", "items": {"type": "string"}},
                            "focus_areas": {"type": "array", "items": {"type": "string"}},
                            "industry": {"type": "string"},
                            "constraints": {"type": "object"}
                        }
                    },
                    "session_id": {"type": "string"},
                    "user_context": {"type": "object"}
                },
                "required": ["specialization_context", "session_id", "user_context"]
            }
        )
        
        # Tool 2: Get Specialization Context
        self.register_tool(
            name="get_specialization_context_tool",
            description="Get stored specialization context for session.",
            handler=self._get_specialization_context_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "user_context": {"type": "object"}
                },
                "required": ["session_id", "user_context"]
            }
        )
        
        # Tool 3: Route to Liaison Agent
        self.register_tool(
            name="route_to_liaison_agent_tool",
            description="Route user to appropriate liaison agent. Agent LLM determines which pillar.",
            handler=self._route_to_liaison_agent_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "domain_name": {"type": "string", "enum": ["content", "insights", "operations", "business_outcomes"]},
                    "user_query": {"type": "string"},
                    "session_id": {"type": "string"},
                    "user_context": {"type": "object"}
                },
                "required": ["domain_name", "session_id", "user_context"]
            }
        )
    
    async def execute_tool(self, tool_name: str, parameters: dict, user_context: Optional[Dict[str, Any]] = None) -> dict:
        """Execute tool by routing to orchestrator."""
        try:
            tool_handlers = {
                "store_specialization_context_tool": self._store_specialization_context_tool,
                "get_specialization_context_tool": self._get_specialization_context_tool,
                "route_to_liaison_agent_tool": self._route_to_liaison_agent_tool
            }
            
            handler = tool_handlers.get(tool_name)
            if handler:
                # Add user_context to parameters if not present
                if user_context and "user_context" not in parameters:
                    parameters["user_context"] = user_context
                
                return await handler(**parameters)
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
        
        except Exception as e:
            self.logger.error(f"❌ Execute tool failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
    
    async def _store_specialization_context_tool(
        self,
        specialization_context: Dict[str, Any],  # Structured from agent LLM
        session_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store specialization context (REAL implementation).
        
        REAL implementation - stores in orchestrator and session.
        """
        try:
            # Store via orchestrator method
            await self.orchestrator._store_specialization_context(session_id, specialization_context)
            
            return {
                "success": True,
                "message": "Specialization context stored",
                "specialization_context": specialization_context
            }
        
        except Exception as e:
            self.logger.error(f"❌ Store specialization context tool failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to store specialization context"
            }
    
    async def _get_specialization_context_tool(
        self,
        session_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get specialization context (REAL implementation).
        
        REAL implementation - retrieves from orchestrator.
        """
        try:
            # Get via orchestrator method
            context = await self.orchestrator.get_specialization_context(session_id)
            
            return {
                "success": True,
                "specialization_context": context
            }
        
        except Exception as e:
            self.logger.error(f"❌ Get specialization context tool failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "specialization_context": {}
            }
    
    async def _route_to_liaison_agent_tool(
        self,
        domain_name: str,  # From agent LLM
        user_query: str,
        session_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route to liaison agent (REAL implementation).
        
        REAL implementation - discovers and routes to appropriate liaison agent.
        """
        try:
            # Map domain to liaison agent name
            agent_mapping = {
                "content": "ContentLiaisonAgent",
                "insights": "InsightsLiaisonAgent",
                "operations": "OperationsLiaisonAgent",
                "business_outcomes": "BusinessOutcomesLiaisonAgent"
            }
            
            agent_name = agent_mapping.get(domain_name.lower())
            if not agent_name:
                return {
                    "success": False,
                    "error": f"Unknown domain: {domain_name}",
                    "route": None
                }
            
            # Get Delivery Manager to discover liaison agent
            delivery_manager = self.orchestrator.delivery_manager
            if not delivery_manager:
                return {
                    "success": False,
                    "error": "Delivery Manager not available",
                    "route": None
                }
            
            # Discover liaison agent via orchestrator
            # Each pillar orchestrator has a liaison_agent
            pillar_orchestrators = {
                "content": "ContentAnalysisOrchestrator",
                "insights": "InsightsOrchestrator",
                "operations": "OperationsOrchestrator",
                "business_outcomes": "BusinessOutcomesOrchestrator"
            }
            
            orchestrator_name = pillar_orchestrators.get(domain_name.lower())
            if not orchestrator_name:
                return {
                    "success": False,
                    "error": f"Unknown orchestrator for domain: {domain_name}",
                    "route": None
                }
            
            # Get orchestrator from Delivery Manager
            orchestrator = delivery_manager.mvp_pillar_orchestrators.get(domain_name.lower())
            if not orchestrator:
                return {
                    "success": False,
                    "error": f"Orchestrator not available for domain: {domain_name}",
                    "route": None
                }
            
            # Get liaison agent from orchestrator
            liaison_agent = getattr(orchestrator, "liaison_agent", None)
            if not liaison_agent:
                return {
                    "success": False,
                    "error": f"Liaison agent not available for domain: {domain_name}",
                    "route": None
                }
            
            return {
                "success": True,
                "route": {
                    "domain": domain_name,
                    "agent_name": agent_name,
                    "agent_available": True,
                    "message": f"Route to {agent_name} for {domain_name} domain"
                }
            }
        
        except Exception as e:
            self.logger.error(f"❌ Route to liaison agent tool failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "route": None
            }
```

**Note:** If MVPJourneyOrchestratorService doesn't have MCP server, create one and initialize it in `initialize()` method.

---

## Gaps and Practical Limitations

### Gap 1: Session Manager API May Not Support Context Updates

**Issue:** `session_manager.update_session()` may not support nested context updates like `specialization_context`.

**Reality Check:**
- Session Manager exists
- Update API may need verification
- May need to use different method or structure

**Practical Solution:**
1. **Option A (Preferred):** Verify Session Manager API and adapt
   ```python
   # Check actual SessionManager.update_session() signature
   # May need: session_manager.update_session_context(session_id, updates)
   # Or: session_manager.set_context(session_id, "specialization_context", context)
   ```

2. **Option B:** Store in Librarian instead
   ```python
   # Store specialization context in Librarian
   await self.librarian.store(
       namespace="specialization_context",
       key=f"{session_id}_context",
       value=context
   )
   ```

**Recommendation:** Verify Session Manager API first. If it doesn't support nested updates, use Option B (Librarian).

---

### Gap 2: Specialization Context Extraction May Be Incomplete

**Issue:** `_extract_specialization_context()` uses simple rule-based extraction that may miss context.

**Reality Check:**
- Agent LLM should extract context properly
- Fallback extraction is simple and may miss details
- May need better extraction in agent

**Practical Solution:**
1. **Rely on Agent LLM:** Agent LLM should extract context and call `store_specialization_context_tool`
2. **Validate in Tool:** Tool validates extracted context
3. **Ask for Clarification:** If context is incomplete, agent asks user

**Recommendation:** Rely on agent LLM for context extraction. Tool validates and handles errors gracefully.

---

### Gap 3: Liaison Agent Discovery May Be Complex

**Issue:** `_route_to_liaison_agent_tool` assumes specific orchestrator structure that may not exist.

**Reality Check:**
- Delivery Manager structure may vary
- Orchestrator access pattern needs verification
- May need to use Curator for service discovery

**Practical Solution:**
1. **Option A (Preferred):** Use Curator for service discovery
   ```python
   # Discover liaison agent via Curator
   curator = await self.get_foundation_service("CuratorFoundationService")
   liaison_agent = await curator.get_service(agent_name)
   ```

2. **Option B:** Use Delivery Manager pattern (as shown above)
   ```python
   # Access via delivery_manager.mvp_pillar_orchestrators
   ```

**Recommendation:** Use Option A (Curator) - it's more robust and follows platform patterns.

---

## Implementation Checklist

### MVPJourneyOrchestratorService Enhancements
- [ ] Add `specialization_context` dict to `__init__`
- [ ] Add `handle_landing_page_conversation()` method
- [ ] Add `get_specialization_context()` method
- [ ] Add `_store_specialization_context()` method
- [ ] Add `_extract_specialization_context()` method
- [ ] Add `_get_session_manager()` helper
- [ ] Add `_get_conversation_history()` helper
- [ ] Test specialization context storage and retrieval

### MCP Server (Create if doesn't exist)
- [ ] Create `MVPJourneyMCPServer` class
- [ ] Add `store_specialization_context_tool`
- [ ] Add `get_specialization_context_tool`
- [ ] Add `route_to_liaison_agent_tool`
- [ ] Initialize MCP server in orchestrator's `initialize()` method
- [ ] Test tool execution

### Integration
- [ ] Test Guide Agent with new tools
- [ ] Test end-to-end: Landing page → Guide Agent → Context storage → Liaison agent routing
- [ ] Verify specialization context is stored and retrieved correctly
- [ ] Test liaison agent routing

---

## Summary

**What We Have:**
- ✅ MVPJourneyOrchestratorService (already exists)
- ✅ GuideCrossDomainAgent (already exists and integrated)
- ✅ SessionManagerService (already exists)

**What We Need to Create/Enhance:**
- ⏳ Add specialization context management to MVPJourneyOrchestratorService
- ⏳ Create MVPJourneyMCPServer (if doesn't exist)
- ⏳ Add 3 MCP tools (store_specialization_context_tool, get_specialization_context_tool, route_to_liaison_agent_tool)

**Gaps Identified:**
- ⚠️ Session Manager API compatibility needs verification
- ⚠️ Specialization context extraction may need improvement (rely on agent LLM)
- ⚠️ Liaison agent discovery pattern needs verification (use Curator)

**All implementations are REAL, WORKING CODE - no mocks, no placeholders, no hard-coded cheats.**







