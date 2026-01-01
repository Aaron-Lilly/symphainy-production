# Agentic Correlation Pattern Proposal

**Date:** 2025-01-XX  
**Status:** Proposal  
**Goal:** Standardize how all agents report and consume agentic information (platform data + prompts + LLM calls + tool usage + everything else besides core functions)

---

## Executive Summary

Similar to how the **Data Solution Orchestrator** uses `_orchestrate_platform_correlation()` to ensure all platform correlation data (auth, session, workflow, events, telemetry) follows client data through the journey, we should create an **"Agentic Correlation"** pattern in the Agentic Foundation/SDK to ensure all agents (even stateless ones) properly report necessary agentic information.

---

## Current State Analysis

### ✅ What Exists

1. **Platform Data Sidecar Pattern** (Data Solution Orchestrator):
   - `_orchestrate_platform_correlation()` method
   - Orchestrates: Security Guard, Traffic Cop, Conductor, Post Office, Nurse
   - Ensures platform correlation data follows client data through journey

2. **Agent Execution Tracking** (Nurse Service):
   - `record_agent_execution()` SOA API exists
   - Takes: `agent_id`, `agent_name`, `prompt_hash`, `response`, `trace_id`, `execution_metadata`
   - Stores via ObservabilityAbstraction (ArangoDB)

3. **AgentBase Foundation**:
   - Has utilities: `logger`, `telemetry`, `security`, `health`
   - Has access to Smart City services via MCP
   - Has `session_id`, `user_context`, `tenant_context`

### ❌ What's Missing

1. **No Automatic Agent Execution Tracking**:
   - `AgentBase` doesn't automatically call `record_agent_execution()`
   - Agents must manually track execution (inconsistent)

2. **No Agentic Correlation Pattern**:
   - No standardized way to track prompts, LLM calls, tool usage
   - No automatic workflow tracking for agents
   - No automatic event publishing for agent operations
   - No automatic cost/performance tracking

3. **Stateless Agents Don't Track**:
   - Stateless agents (like StatelessHFInferenceAgent) don't track anything
   - No way to observe stateless agent usage

4. **No Agentic Metadata Collection**:
   - Prompts not tracked
   - LLM calls not tracked
   - Tool usage not tracked
   - Cost not tracked
   - Performance not tracked

---

## Proposed Solution: Agentic Correlation Pattern

### Pattern Overview

Create an `_orchestrate_agentic_correlation()` method in `AgentBase` that automatically tracks all agentic information, similar to how `DataSolutionOrchestrator` tracks platform correlation.

### Architecture

```
AgentBase
  ↓ calls
_orchestrate_agentic_correlation()
  ↓ orchestrates
- Security Guard: Validate auth & tenant (if needed)
- Traffic Cop: Manage agent session/state (if stateful)
- Conductor: Track agent workflow steps
- Post Office: Publish agent events
- Nurse: Record agent execution (prompts, LLM calls, tool usage, costs, performance)
```

### Key Principles

1. **Automatic Tracking**: All agents (even stateless) automatically track agentic information
2. **Opt-in Features**: Stateful features (conversation history, iterative execution) are opt-in
3. **Consistent Baseline**: All agents track execution, prompts, LLM calls, tool usage, costs
4. **Platform Integration**: Uses existing platform services (Nurse, Post Office, Conductor, etc.)

---

## Implementation Plan

### Phase 1: Add Agentic Correlation to AgentBase

**File:** `foundations/agentic_foundation/agent_sdk/agent_base.py`

**Add Method:**
```python
async def _orchestrate_agentic_correlation(
    self,
    operation: str,  # "agent_execute", "llm_call", "tool_execute", etc.
    correlation_data: Dict[str, Any],  # Agent-specific data
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Orchestrate agentic correlation data to follow agent execution.
    
    "One Stop Shopping" for all agentic correlation:
    - Security Guard: Validate auth & tenant (if needed)
    - Traffic Cop: Manage agent session/state (if stateful)
    - Conductor: Track agent workflow steps
    - Post Office: Publish agent events
    - Nurse: Record agent execution (prompts, LLM calls, tool usage, costs, performance)
    
    Args:
        operation: Operation name (e.g., "agent_execute", "llm_call", "tool_execute")
        correlation_data: Agent-specific correlation data:
            - For "agent_execute": {prompt, response, model_name, tokens, latency, cost}
            - For "llm_call": {prompt, response, model_name, tokens, latency, cost}
            - For "tool_execute": {tool_name, parameters, result, latency}
        user_context: Optional user context
        
    Returns:
        Enhanced correlation context with all agentic correlation data
    """
    # Get workflow_id (generate if not present)
    workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
    agent_execution_id = f"{self.agent_name}_{int(datetime.now().timestamp())}"
    
    # Discover platform correlation services (lazy-load)
    if not self.security_guard:
        self.security_guard = await self.get_security_guard_api()
    if not self.traffic_cop:
        self.traffic_cop = await self.get_traffic_cop_api()
    if not self.conductor:
        self.conductor = await self.get_conductor_api()
    if not self.post_office:
        self.post_office = await self.get_post_office_api()
    if not self.nurse:
        self.nurse = await self.get_nurse_api()
    
    # Build correlation context
    correlation_context = user_context.copy() if user_context else {}
    correlation_context["workflow_id"] = workflow_id
    correlation_context["agent_execution_id"] = agent_execution_id
    correlation_context["agent_name"] = self.agent_name
    correlation_context["agent_id"] = self.agent_id
    
    # 1. Security Guard: Validate auth & tenant (if needed)
    if self.security_guard and correlation_context.get("user_id"):
        try:
            if correlation_context.get("session_id"):
                auth_result = await self.security_guard.validate_session(
                    session_token=correlation_context.get("session_id"),
                    user_context=correlation_context
                )
                if auth_result and auth_result.get("valid"):
                    correlation_context["auth_validated"] = True
                    correlation_context["tenant_id"] = auth_result.get("tenant_id")
        except Exception as e:
            self.logger.warning(f"⚠️ Auth validation failed: {e}")
    
    # 2. Traffic Cop: Manage agent session/state (if stateful)
    if self.traffic_cop and correlation_context.get("session_id") and self.is_stateful():
        try:
            session_state = await self.traffic_cop.get_session_state(
                session_id=correlation_context.get("session_id"),
                workflow_id=workflow_id
            )
            if session_state:
                correlation_context["session_state"] = session_state
        except Exception as e:
            self.logger.warning(f"⚠️ Session management failed: {e}")
    
    # 3. Conductor: Track agent workflow steps
    if self.conductor:
        try:
            workflow_status = await self.conductor.track_workflow_step(
                workflow_id=workflow_id,
                step_name=f"agent.{self.agent_name}.{operation}",
                status="in_progress",
                user_context=correlation_context
            )
            if workflow_status:
                correlation_context["workflow_tracked"] = True
        except Exception as e:
            self.logger.warning(f"⚠️ Workflow tracking failed: {e}")
    
    # 4. Post Office: Publish agent operation start event
    if self.post_office:
        try:
            await self.post_office.publish_event(
                event_type=f"agent.{self.agent_name}.{operation}.start",
                event_data={
                    "operation": operation,
                    "agent_name": self.agent_name,
                    "agent_id": self.agent_id,
                    "workflow_id": workflow_id,
                    "agent_execution_id": agent_execution_id,
                    **correlation_data
                },
                workflow_id=workflow_id,
                user_context=correlation_context
            )
        except Exception as e:
            self.logger.warning(f"⚠️ Event publishing failed: {e}")
    
    # 5. Nurse: Record agent execution (prompts, LLM calls, tool usage, costs, performance)
    if self.nurse:
        try:
            # Calculate prompt hash
            prompt_hash = self._calculate_prompt_hash(correlation_data.get("prompt", ""))
            
            # Record agent execution
            await self.nurse.record_agent_execution(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                prompt_hash=prompt_hash,
                response=correlation_data.get("response", ""),
                trace_id=workflow_id,
                execution_metadata={
                    "operation": operation,
                    "model_name": correlation_data.get("model_name"),
                    "tokens": correlation_data.get("tokens"),
                    "latency_ms": correlation_data.get("latency_ms"),
                    "cost": correlation_data.get("cost"),
                    "tool_calls": correlation_data.get("tool_calls", []),
                    "tool_results": correlation_data.get("tool_results", []),
                    "agent_execution_id": agent_execution_id
                },
                user_context=correlation_context
            )
        except Exception as e:
            self.logger.warning(f"⚠️ Agent execution tracking failed: {e}")
    
    return correlation_context

async def _record_agentic_correlation_completion(
    self,
    operation: str,
    result: Dict[str, Any],
    correlation_context: Dict[str, Any]
):
    """Record agentic correlation completion for operation."""
    workflow_id = correlation_context.get("workflow_id")
    
    # Conductor: Mark workflow step complete
    if self.conductor and workflow_id:
        try:
            await self.conductor.track_workflow_step(
                workflow_id=workflow_id,
                step_name=f"agent.{self.agent_name}.{operation}",
                status="completed" if result.get("success") else "failed",
                user_context=correlation_context
            )
        except Exception as e:
            self.logger.warning(f"⚠️ Workflow completion tracking failed: {e}")
    
    # Post Office: Publish operation complete event
    if self.post_office and workflow_id:
        try:
            await self.post_office.publish_event(
                event_type=f"agent.{self.agent_name}.{operation}.complete",
                event_data={
                    "operation": operation,
                    "agent_name": self.agent_name,
                    "success": result.get("success", False),
                    "workflow_id": workflow_id,
                    "agent_execution_id": correlation_context.get("agent_execution_id")
                },
                workflow_id=workflow_id,
                user_context=correlation_context
            )
        except Exception as e:
            self.logger.warning(f"⚠️ Event publishing failed: {e}")
    
    # Nurse: Record completion telemetry
    if self.nurse and workflow_id:
        try:
            await self.nurse.record_platform_event(
                event_type="metric",
                event_data={
                    "metric_name": f"agent.{self.agent_name}.{operation}.duration",
                    "value": result.get("duration_ms", 0),
                    "service_name": self.agent_name
                },
                trace_id=workflow_id,
                user_context=correlation_context
            )
        except Exception as e:
            self.logger.warning(f"⚠️ Telemetry recording failed: {e}")

def _calculate_prompt_hash(self, prompt: str) -> str:
    """Calculate hash of prompt for tracking."""
    import hashlib
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]

def is_stateful(self) -> bool:
    """Check if agent is stateful (has conversation history)."""
    # Check if agent has stateful configuration
    return hasattr(self, 'conversation_history') and self.conversation_history is not None
```

### Phase 2: Integrate into Agent Execution Methods

**Update AgentBase methods to automatically call agentic correlation:**

```python
async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Execute agent with automatic agentic correlation tracking."""
    start_time = datetime.now()
    
    try:
        # Orchestrate agentic correlation (start)
        correlation_context = await self._orchestrate_agentic_correlation(
            operation="agent_execute",
            correlation_data={
                "prompt": request.get("prompt", ""),
                "model_name": self.get_model_name(),
                "user_query": request.get("message", "")
            },
            user_context=request.get("user_context")
        )
        
        # Execute agent (existing logic)
        result = await self._execute_agent_logic(request)
        
        # Calculate execution metadata
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Record completion
        await self._record_agentic_correlation_completion(
            operation="agent_execute",
            result={
                "success": result.get("success", True),
                "duration_ms": duration_ms,
                **result
            },
            correlation_context=correlation_context
        )
        
        return result
        
    except Exception as e:
        # Record failure
        await self._record_agentic_correlation_completion(
            operation="agent_execute",
            result={"success": False, "error": str(e)},
            correlation_context=correlation_context if 'correlation_context' in locals() else {}
        )
        raise

async def _call_llm(self, prompt: str, **kwargs) -> Dict[str, Any]:
    """Call LLM with automatic tracking."""
    start_time = datetime.now()
    
    try:
        # Orchestrate agentic correlation (LLM call)
        correlation_context = await self._orchestrate_agentic_correlation(
            operation="llm_call",
            correlation_data={
                "prompt": prompt,
                "model_name": kwargs.get("model_name", self.get_model_name())
            },
            user_context=kwargs.get("user_context")
        )
        
        # Call LLM (existing logic)
        response = await self._call_llm_internal(prompt, **kwargs)
        
        # Calculate LLM metadata
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Record completion with LLM-specific data
        await self._record_agentic_correlation_completion(
            operation="llm_call",
            result={
                "success": True,
                "response": response.get("text", ""),
                "tokens": response.get("tokens", {}),
                "cost": response.get("cost", 0),
                "duration_ms": duration_ms,
                "model_name": kwargs.get("model_name")
            },
            correlation_context=correlation_context
        )
        
        return response
        
    except Exception as e:
        await self._record_agentic_correlation_completion(
            operation="llm_call",
            result={"success": False, "error": str(e)},
            correlation_context=correlation_context if 'correlation_context' in locals() else {}
        )
        raise

async def _execute_tool(self, tool_name: str, parameters: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Execute tool with automatic tracking."""
    start_time = datetime.now()
    
    try:
        # Orchestrate agentic correlation (tool execution)
        correlation_context = await self._orchestrate_agentic_correlation(
            operation="tool_execute",
            correlation_data={
                "tool_name": tool_name,
                "parameters": parameters
            },
            user_context=kwargs.get("user_context")
        )
        
        # Execute tool (existing logic)
        result = await self._execute_tool_internal(tool_name, parameters, **kwargs)
        
        # Calculate tool metadata
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Record completion
        await self._record_agentic_correlation_completion(
            operation="tool_execute",
            result={
                "success": result.get("success", True),
                "tool_name": tool_name,
                "result": result,
                "duration_ms": duration_ms
            },
            correlation_context=correlation_context
        )
        
        return result
        
    except Exception as e:
        await self._record_agentic_correlation_completion(
            operation="tool_execute",
            result={"success": False, "error": str(e), "tool_name": tool_name},
            correlation_context=correlation_context if 'correlation_context' in locals() else {}
        )
        raise
```

### Phase 3: Add Helper Methods for Service Discovery

**Add to AgentBase:**

```python
async def get_security_guard_api(self):
    """Get Security Guard API via MCP."""
    if not hasattr(self, '_security_guard'):
        # Try via MCP client manager
        if self.mcp_client_manager:
            self._security_guard = await self.mcp_client_manager.connect_to_role("security_guard")
    return getattr(self, '_security_guard', None)

async def get_traffic_cop_api(self):
    """Get Traffic Cop API via MCP."""
    if not hasattr(self, '_traffic_cop'):
        if self.mcp_client_manager:
            self._traffic_cop = await self.mcp_client_manager.connect_to_role("traffic_cop")
    return getattr(self, '_traffic_cop', None)

async def get_conductor_api(self):
    """Get Conductor API via MCP."""
    if not hasattr(self, '_conductor'):
        if self.mcp_client_manager:
            self._conductor = await self.mcp_client_manager.connect_to_role("conductor")
    return getattr(self, '_conductor', None)

async def get_post_office_api(self):
    """Get Post Office API via MCP."""
    if not hasattr(self, '_post_office'):
        if self.mcp_client_manager:
            self._post_office = await self.mcp_client_manager.connect_to_role("post_office")
    return getattr(self, '_post_office', None)

async def get_nurse_api(self):
    """Get Nurse API via MCP."""
    if not hasattr(self, '_nurse'):
        if self.mcp_client_manager:
            self._nurse = await self.mcp_client_manager.connect_to_role("nurse")
    return getattr(self, '_nurse', None)
```

---

## Benefits

1. **Automatic Tracking**: All agents automatically track execution, prompts, LLM calls, tool usage, costs
2. **Consistent Baseline**: All agents (even stateless) have consistent observability
3. **Platform Integration**: Uses existing platform services (no new infrastructure)
4. **Opt-in Features**: Stateful features remain opt-in (stateless agents stay lightweight)
5. **Observability**: Full visibility into agent execution, costs, performance
6. **Debugging**: Easy to trace agent execution through workflow, events, telemetry

---

## Migration Path

1. **Phase 1**: Add agentic correlation methods to `AgentBase` (non-breaking)
2. **Phase 2**: Integrate into existing agent execution methods (non-breaking, opt-in)
3. **Phase 3**: Update all agents to use agentic correlation (gradual migration)
4. **Phase 4**: Remove manual tracking code (cleanup)

---

## Success Criteria

1. ✅ All agents automatically track execution via Nurse
2. ✅ All agents publish events via Post Office
3. ✅ All agents track workflow via Conductor
4. ✅ All agents track prompts, LLM calls, tool usage, costs
5. ✅ Stateless agents remain lightweight (no state overhead)
6. ✅ Full observability into agent execution

---

## Next Steps

1. Review this proposal
2. Implement Phase 1 (add agentic correlation methods)
3. Test with existing agents
4. Migrate all agents to use agentic correlation
5. Document agentic correlation pattern in developer guide

