# Agentic Overhaul Implementation Plan

## Executive Summary

This document provides a detailed, step-by-step implementation plan to overhaul all agents (23 total) to remove anti-patterns and implement fully AI-enabled functionality. The plan includes code examples, SDK/base class updates to prevent future anti-patterns, and validation mechanisms.

**Goal:** Transform all agents from placeholder/mock implementations to fully AI-enabled agents that use real LLM calls, MCP tools, and proper reasoning.

---

## Table of Contents

1. [Anti-Pattern Categories](#anti-pattern-categories)
2. [SDK/Base Class Updates](#sdkbase-class-updates)
3. [Phase-by-Phase Implementation](#phase-by-phase-implementation)
4. [Code Examples](#code-examples)
5. [Validation & Testing](#validation--testing)
6. [Prevention Mechanisms](#prevention-mechanisms)

---

## Anti-Pattern Categories

### Category 1: LLM Placeholders
**Problem:** Agents use placeholder comments instead of actual LLM calls.

**Example:**
```python
# Placeholder - would use LLM
# Placeholder for AI enhancement - would use LLM
```

**Fix:** Use `self.llm_abstraction.generate_content()` or `self.llm_abstraction.analyze_text()`.

### Category 2: Mock LLM Fallbacks
**Problem:** Agents check for LLM service availability and fall back to mock responses.

**Example:**
```python
if hasattr(self, 'llm_composition_service') and self.llm_composition_service:
    insights = await self.llm_composition_service.generate_insights(...)
else:
    # Mock LLM insights generation
    insights = {"mock": "data"}
```

**Fix:** Remove fallbacks. Fail fast if LLM is unavailable.

### Category 3: Direct Service Access
**Problem:** Agents discover and store direct references to enabling services.

**Example:**
```python
self.enabling_service = await self.curator_foundation.get_service(self.enabling_service_name)
result = await self.enabling_service.map_to_canonical(...)
```

**Fix:** Use MCP tools via orchestrator's MCP server.

### Category 4: Bypassed MCP Tool Execution
**Problem:** Agents have commented-out MCP tool calls with placeholder responses.

**Example:**
```python
# Call service (placeholder - would use MCP tools)
# result = await self.execute_role_tool(...)
# Placeholder response
return {"success": True, "service_result": "Service executed successfully"}
```

**Fix:** Execute MCP tools via `self.orchestrator.mcp_server.execute_tool()` or `self.tool_composition.execute_tool_chain()`.

---

## SDK/Base Class Updates

### Update 1: Add Validation to `AgentBase`

**File:** `foundations/agentic_foundation/agent_sdk/agent_base.py`

**Purpose:** Prevent agents from storing direct service references and enforce MCP tool usage.

**Code:**

```python
class AgentBase(ABC, TenantProtocol):
    """
    Base class for all agents with anti-pattern prevention.
    """
    
    def __init__(self, ...):
        super().__init__(...)
        
        # Anti-pattern prevention: Track service access patterns
        self._service_access_log = []
        self._mcp_tool_usage_log = []
        
        # Orchestrator reference (set by orchestrator, not discovered)
        self._orchestrator = None
        self._orchestrator_set_via_setter = False
        
        # Prevent direct service storage
        self._direct_service_references = {}
    
    def set_orchestrator(self, orchestrator):
        """
        Set orchestrator reference (called by orchestrator during initialization).
        
        This is the ONLY way agents should get orchestrator access.
        """
        if self._orchestrator is not None:
            self.logger.warning(
                f"⚠️ Orchestrator already set for {self.agent_name}. "
                f"Overwriting with new orchestrator."
            )
        
        self._orchestrator = orchestrator
        self._orchestrator_set_via_setter = True
        
        # Validate orchestrator has MCP server
        if not hasattr(orchestrator, 'mcp_server') or orchestrator.mcp_server is None:
            self.logger.error(
                f"❌ Orchestrator {orchestrator.__class__.__name__} does not have MCP server. "
                f"Agents require MCP server access for tool execution."
            )
            raise ValueError("Orchestrator must have MCP server for agent tool access")
        
        self.logger.info(f"✅ Orchestrator set for {self.agent_name} (MCP server available)")
    
    @property
    def orchestrator(self):
        """Get orchestrator reference (read-only)."""
        if self._orchestrator is None:
            self.logger.warning(
                f"⚠️ Orchestrator not set for {self.agent_name}. "
                f"Call orchestrator.set_orchestrator(agent) during orchestrator initialization."
            )
        return self._orchestrator
    
    def _validate_no_direct_service_access(self, service_name: str):
        """
        Validate that agent is not storing direct service references.
        
        This method should be called during agent initialization to detect anti-patterns.
        """
        if service_name in self._direct_service_references:
            self.logger.error(
                f"❌ ANTI-PATTERN DETECTED: Agent {self.agent_name} is storing direct "
                f"reference to service '{service_name}'. Agents must use MCP tools instead."
            )
            raise ValueError(
                f"Direct service access anti-pattern detected. "
                f"Use MCP tools via orchestrator.mcp_server instead."
            )
    
    async def execute_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute MCP tool via orchestrator's MCP server.
        
        This is the PRIMARY method for agents to interact with services.
        
        Args:
            tool_name: Name of MCP tool to execute
            parameters: Tool parameters
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If orchestrator or MCP server not available
        """
        if self._orchestrator is None:
            raise ValueError(
                f"Orchestrator not set for {self.agent_name}. "
                f"Cannot execute MCP tool '{tool_name}'. "
                f"Ensure orchestrator calls set_orchestrator(agent) during initialization."
            )
        
        if not hasattr(self._orchestrator, 'mcp_server') or self._orchestrator.mcp_server is None:
            raise ValueError(
                f"Orchestrator {self._orchestrator.__class__.__name__} does not have MCP server. "
                f"Cannot execute MCP tool '{tool_name}'."
            )
        
        # Log MCP tool usage
        self._mcp_tool_usage_log.append({
            "tool_name": tool_name,
            "timestamp": datetime.now().isoformat(),
            "parameters": parameters
        })
        
        try:
            # Execute tool via orchestrator's MCP server
            result = await self._orchestrator.mcp_server.execute_tool(tool_name, parameters)
            
            self.logger.info(f"✅ Executed MCP tool '{tool_name}' via orchestrator")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to execute MCP tool '{tool_name}': {e}")
            raise
    
    async def execute_mcp_tool_chain(self, tool_chain: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a chain of MCP tools using tool composition.
        
        Args:
            tool_chain: List of tool definitions with format:
                [
                    {"tool_name": "tool1", "parameters": {...}},
                    {"tool_name": "tool2", "parameters": {...}}
                ]
                
        Returns:
            Aggregated execution results
        """
        if not self.tool_composition:
            raise ValueError(
                f"Tool composition not available for {self.agent_name}. "
                f"Cannot execute tool chain."
            )
        
        # Log tool chain usage
        self._mcp_tool_usage_log.append({
            "tool_chain": [t.get("tool_name") for t in tool_chain],
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            result = await self.tool_composition.compose_tools(tool_chain, self.tenant_context)
            self.logger.info(f"✅ Executed tool chain with {len(tool_chain)} tools")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to execute tool chain: {e}")
            raise
    
    def validate_llm_usage(self, method_name: str):
        """
        Validate that agent is using LLM abstraction, not placeholders.
        
        This should be called at the start of methods that should use LLM.
        """
        if self.llm_abstraction is None:
            self.logger.error(
                f"❌ LLM abstraction not available for {self.agent_name}. "
                f"Method '{method_name}' requires LLM but llm_abstraction is None. "
                f"Ensure PublicWorksFoundation is initialized and provides LLM abstraction."
            )
            raise ValueError(
                f"LLM abstraction required for {method_name} but not available. "
                f"Fail fast - no fallbacks allowed."
            )
```

### Update 2: Add Validation to `LightweightLLMAgent`

**File:** `foundations/agentic_foundation/agent_sdk/lightweight_llm_agent.py`

**Purpose:** Ensure LLM abstraction is always available and fail fast if not.

**Code:**

```python
class LightweightLLMAgent(AgentBase):
    """
    Lightweight LLM Agent with anti-pattern prevention.
    """
    
    def __init__(self, ...):
        super().__init__(...)
        
        # Initialize LLM abstraction (REQUIRED - no fallbacks)
        if self.public_works_foundation:
            self.llm_abstraction = self.public_works_foundation.get_abstraction("llm")
            
            if self.llm_abstraction is None:
                self.logger.error(
                    f"❌ LLM abstraction not available from PublicWorksFoundation. "
                    f"Agent {self.agent_name} requires LLM but abstraction is None."
                )
                raise ValueError(
                    "LLM abstraction required but not available. "
                    "Ensure PublicWorksFoundation provides 'llm' abstraction."
                )
        else:
            self.logger.error(
                f"❌ PublicWorksFoundation not available for {self.agent_name}. "
                f"LLM agents require PublicWorksFoundation for LLM abstraction."
            )
            raise ValueError(
                "PublicWorksFoundation required for LightweightLLMAgent. "
                "No fallbacks allowed - fail fast."
            )
        
        self.logger.info(f"✅ LLM abstraction initialized for {self.agent_name}")
    
    def _generate_content(self, prompt: str, content_type: str = "text", **kwargs) -> Dict[str, Any]:
        """
        Generate content using LLM abstraction (NO FALLBACKS).
        
        Args:
            prompt: Prompt for content generation
            content_type: Type of content to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated content
            
        Raises:
            ValueError: If LLM abstraction not available (fail fast)
        """
        # Validate LLM is available (fail fast)
        if self.llm_abstraction is None:
            raise ValueError(
                f"LLM abstraction not available for {self.agent_name}. "
                f"Cannot generate content. No fallbacks allowed."
            )
        
        self._log_operation('generate', {'prompt_length': len(prompt), 'content_type': content_type})
        
        try:
            # Use LLM business abstraction (REAL CALL - no placeholders)
            result = self.llm_abstraction.generate_content(
                prompt=prompt,
                content_type=content_type,
                **kwargs
            )
            
            self._update_usage_stats(result)
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Content generation failed: {e}")
            # Fail fast - no fallback to mock data
            raise
```

### Update 3: Add Validation Helper to `SpecialistCapabilityAgent`

**File:** `backend/business_enablement/agents/specialist_capability_agent.py`

**Purpose:** Remove service discovery and enforce MCP tool usage.

**Code:**

```python
class SpecialistCapabilityAgent(DimensionSpecialistAgent):
    """
    Platform-level base class with anti-pattern prevention.
    """
    
    def __init__(self, ...):
        super().__init__(...)
        
        # REMOVED: self.enabling_service = None
        # REMOVED: self.enabling_service_name (keep for config, but don't discover service)
        
        # MCP tools for this capability (from config)
        self.capability_mcp_tools = capability_config.get('mcp_tools', [])
        
        # Orchestrator reference (set by orchestrator, not discovered)
        self._orchestrator = None
    
    async def initialize(self):
        """
        Initialize specialist agent (NO SERVICE DISCOVERY).
        
        Agents should NOT discover enabling services directly.
        They should use MCP tools via orchestrator's MCP server.
        """
        try:
            await self.log_operation_with_telemetry("initialize_start", success=True, details={
                "agent_name": self.agent_name,
                "capability_name": self.capability_name
            })
            
            # Call parent initialize
            await super().initialize()
            
            # REMOVED: Service discovery anti-pattern
            # if self.enabling_service_name and self.curator_foundation:
            #     self.enabling_service = await self.curator_foundation.get_service(...)
            
            # Validate orchestrator is set (should be set by orchestrator during its init)
            if self._orchestrator is None:
                self.logger.warning(
                    f"⚠️ Orchestrator not set for {self.agent_name}. "
                    f"MCP tools will not be available until orchestrator.set_orchestrator(agent) is called."
                )
            else:
                # Validate MCP server is available
                if not hasattr(self._orchestrator, 'mcp_server') or self._orchestrator.mcp_server is None:
                    self.logger.error(
                        f"❌ Orchestrator {self._orchestrator.__class__.__name__} does not have MCP server. "
                        f"Agent {self.agent_name} requires MCP server for tool execution."
                    )
                else:
                    self.logger.info(
                        f"✅ Orchestrator and MCP server available for {self.agent_name}. "
                        f"Available MCP tools: {self.capability_mcp_tools}"
                    )
            
            self.is_initialized = True
            
            await self.record_health_metric("initialized", 1.0, {
                "agent_name": self.agent_name,
                "capability_name": self.capability_name
            })
            
            await self.log_operation_with_telemetry("initialize_complete", success=True, details={
                "agent_name": self.agent_name,
                "capability_name": self.capability_name
            })
            
            return True
            
        except Exception as e:
            await self.handle_error_with_audit(e, "initialize", details={
                "agent_name": self.agent_name,
                "capability_name": self.capability_name
            })
            raise
    
    async def _call_enabling_service(self,
                                    request: Dict[str, Any],
                                    context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call enabling service via MCP tools (NOT DIRECT SERVICE ACCESS).
        
        This method uses MCP tools exposed by orchestrator's MCP server.
        
        Args:
            request: User request
            context_analysis: Context analysis
            
        Returns:
            Service results from MCP tool execution
        """
        # Validate orchestrator and MCP server are available
        if self._orchestrator is None:
            raise ValueError(
                f"Orchestrator not set for {self.agent_name}. "
                f"Cannot call enabling service via MCP tools. "
                f"Ensure orchestrator calls set_orchestrator(agent) during initialization."
            )
        
        if not hasattr(self._orchestrator, 'mcp_server') or self._orchestrator.mcp_server is None:
            raise ValueError(
                f"Orchestrator {self._orchestrator.__class__.__name__} does not have MCP server. "
                f"Cannot call enabling service via MCP tools."
            )
        
        # Determine which MCP tool to use (from config)
        if not self.capability_mcp_tools:
            raise ValueError(
                f"No MCP tools configured for capability '{self.capability_name}'. "
                f"Add 'mcp_tools' to capability_config."
            )
        
        # Use first MCP tool (or implement tool selection logic)
        tool_name = self.capability_mcp_tools[0]
        
        # Prepare tool parameters
        tool_parameters = {
            "task": request.get('task'),
            "data": request.get('data'),
            "parameters": request.get('parameters', {}),
            "user_context": request.get('user_context'),
            "context_analysis": context_analysis
        }
        
        try:
            # Execute MCP tool via orchestrator's MCP server (REAL CALL - no placeholders)
            result = await self.execute_mcp_tool(tool_name, tool_parameters)
            
            self.logger.info(f"✅ Called enabling service via MCP tool '{tool_name}'")
            return {
                "success": True,
                "service_result": result,
                "raw_output": result
            }
            
        except Exception as e:
            self.logger.error(f"❌ MCP tool execution failed: {e}")
            # Fail fast - no fallback
            raise
    
    async def _enhance_with_ai(self,
                              service_result: Dict[str, Any],
                              request: Dict[str, Any],
                              context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance service results with AI reasoning (REAL LLM CALL - no placeholders).
        
        Args:
            service_result: Results from enabling service
            request: Original request
            context_analysis: Context analysis
            
        Returns:
            AI-enhanced results
        """
        # Validate LLM is available (fail fast)
        if self.llm_abstraction is None:
            raise ValueError(
                f"LLM abstraction not available for {self.agent_name}. "
                f"Cannot enhance results with AI. No fallbacks allowed."
            )
        
        self.logger.info("🧠 Enhancing results with AI reasoning...")
        
        # Build prompt for AI enhancement
        enhancement_prompt = f"""
Analyze the following service result and provide AI-powered insights:

Service Result: {service_result}
Original Request: {request}
Context Analysis: {context_analysis}

Provide:
1. AI-powered interpretation of the results
2. Patterns detected in the data
3. Recommendations based on the analysis
4. Confidence score (0-1)
"""
        
        try:
            # Use LLM abstraction (REAL CALL - no placeholders)
            ai_response = await self.llm_abstraction.generate_content(
                prompt=enhancement_prompt,
                content_type="analysis",
                user_context=request.get('user_context', {})
            )
            
            # Parse AI response
            enhanced = {
                "original_result": service_result,
                "ai_insights": ai_response.get("content", ""),
                "patterns_detected": ai_response.get("patterns", []),
                "recommendations": ai_response.get("recommendations", []),
                "confidence": ai_response.get("confidence", 0.85)
            }
            
            return enhanced
            
        except Exception as e:
            self.logger.error(f"❌ AI enhancement failed: {e}")
            # Fail fast - no fallback
            raise
    
    async def _gather_requirements(self,
                                  request: Dict[str, Any],
                                  context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gather additional requirements using conversational AI (REAL LLM CALL - no placeholders).
        
        This will require ConversationalAIService (Phase 1.3).
        For now, use LLM abstraction directly.
        
        Args:
            request: User request
            context_analysis: Context analysis
            
        Returns:
            Clarification information
        """
        # Validate LLM is available (fail fast)
        if self.llm_abstraction is None:
            raise ValueError(
                f"LLM abstraction not available for {self.agent_name}. "
                f"Cannot gather requirements. No fallbacks allowed."
            )
        
        self.logger.info("📋 Gathering additional requirements...")
        
        # Build prompt for requirements gathering
        requirements_prompt = f"""
Analyze the following user request and determine if additional information is needed:

User Request: {request}
Context Analysis: {context_analysis}

Determine:
1. Is clarification needed? (yes/no)
2. What additional information is required?
3. What questions should be asked to gather this information?

Respond in JSON format with keys: clarification_needed, required_information, questions.
"""
        
        try:
            # Use LLM abstraction (REAL CALL - no placeholders)
            ai_response = await self.llm_abstraction.generate_content(
                prompt=requirements_prompt,
                content_type="structured",
                user_context=request.get('user_context', {})
            )
            
            # Parse AI response
            requirements_gathered = {
                "requirements_gathered": True,
                "clarification_needed": ai_response.get("clarification_needed", False),
                "additional_context": ai_response.get("required_information", {}),
                "questions": ai_response.get("questions", [])
            }
            
            return requirements_gathered
            
        except Exception as e:
            self.logger.error(f"❌ Requirements gathering failed: {e}")
            # Fail fast - no fallback
            raise
```

### Update 4: Add Validation Helper to `LiaisonDomainAgent`

**File:** `backend/business_enablement/agents/liaison_domain_agent.py`

**Purpose:** Remove orchestrator discovery and enforce MCP tool usage.

**Code:**

```python
class LiaisonDomainAgent(DimensionLiaisonAgent):
    """
    Platform-level base class with anti-pattern prevention.
    """
    
    def __init__(self, ...):
        super().__init__(...)
        
        # REMOVED: self.orchestrator = None (discovered via Curator)
        # Orchestrator reference (set by orchestrator, not discovered)
        self._orchestrator = None
    
    async def initialize(self):
        """
        Initialize liaison agent (NO ORCHESTRATOR DISCOVERY).
        
        Agents should NOT discover orchestrators directly.
        They should use MCP tools via orchestrator's MCP server.
        """
        try:
            await self.log_operation_with_telemetry("initialize_start", success=True, details={
                "agent_name": self.agent_name,
                "domain_name": self.domain_name
            })
            
            # Call parent initialize
            await super().initialize()
            
            # REMOVED: Orchestrator discovery anti-pattern
            # if self.orchestrator_name and self.curator_foundation:
            #     self.orchestrator = await self.curator_foundation.get_service(...)
            
            # Validate orchestrator is set (should be set by orchestrator during its init)
            if self._orchestrator is None:
                self.logger.warning(
                    f"⚠️ Orchestrator not set for {self.agent_name}. "
                    f"MCP tools will not be available until orchestrator.set_orchestrator(agent) is called."
                )
            else:
                # Validate MCP server is available
                if not hasattr(self._orchestrator, 'mcp_server') or self._orchestrator.mcp_server is None:
                    self.logger.error(
                        f"❌ Orchestrator {self._orchestrator.__class__.__name__} does not have MCP server. "
                        f"Agent {self.agent_name} requires MCP server for tool execution."
                    )
                else:
                    self.logger.info(
                        f"✅ Orchestrator and MCP server available for {self.agent_name}. "
                        f"Available MCP tools: {self.domain_mcp_tools}"
                    )
            
            self.is_initialized = True
            
            await self.record_health_metric("initialized", 1.0, {
                "agent_name": self.agent_name,
                "domain_name": self.domain_name
            })
            
            await self.log_operation_with_telemetry("initialize_complete", success=True, details={
                "agent_name": self.agent_name,
                "domain_name": self.domain_name
            })
            
            return True
            
        except Exception as e:
            await self.handle_error_with_audit(e, "initialize", details={
                "agent_name": self.agent_name,
                "domain_name": self.domain_name
            })
            raise
    
    async def _handle_with_mcp_tools(self, 
                                    request: Dict[str, Any],
                                    intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle request directly using MCP tools (REAL MCP TOOL EXECUTION - no placeholders).
        
        Args:
            request: User request
            intent_analysis: Intent analysis
            
        Returns:
            Response from MCP tool execution
        """
        # Validate orchestrator and MCP server are available
        if self._orchestrator is None:
            raise ValueError(
                f"Orchestrator not set for {self.agent_name}. "
                f"Cannot execute MCP tools. "
                f"Ensure orchestrator calls set_orchestrator(agent) during initialization."
            )
        
        if not hasattr(self._orchestrator, 'mcp_server') or self._orchestrator.mcp_server is None:
            raise ValueError(
                f"Orchestrator {self._orchestrator.__class__.__name__} does not have MCP server. "
                f"Cannot execute MCP tools."
            )
        
        intent = intent_analysis.get('intent')
        action = intent_analysis.get('action')
        
        # Determine which MCP tool to use based on intent/action
        tool_name = self._map_intent_to_mcp_tool(intent, action)
        
        if not tool_name:
            raise ValueError(
                f"No MCP tool mapped for intent '{intent}' and action '{action}'. "
                f"Add mapping to domain_config['intent_to_tool_mapping']."
            )
        
        # Prepare tool parameters
        tool_parameters = {
            "intent": intent,
            "action": action,
            "user_context": request.get('user_context', {}),
            "parameters": request.get('parameters', {}),
            "intent_analysis": intent_analysis
        }
        
        try:
            # Execute MCP tool via orchestrator's MCP server (REAL CALL - no placeholders)
            result = await self.execute_mcp_tool(tool_name, tool_parameters)
            
            self.logger.info(f"✅ Executed MCP tool '{tool_name}' for intent '{intent}'")
            
            return {
                "success": True,
                "response_type": "mcp_tool_execution",
                "intent": intent,
                "response": result.get("response", f"I've processed your {intent} request."),
                "results": result
            }
            
        except Exception as e:
            self.logger.error(f"❌ MCP tool execution failed: {e}")
            # Fail fast - no fallback
            raise
    
    def _map_intent_to_mcp_tool(self, intent: str, action: str) -> Optional[str]:
        """
        Map intent/action to MCP tool name.
        
        Args:
            intent: Detected intent
            action: Detected action
            
        Returns:
            MCP tool name or None if no mapping found
        """
        # Get mapping from domain config
        intent_mapping = self.domain_config.get('intent_to_tool_mapping', {})
        
        # Try intent first
        if intent in intent_mapping:
            return intent_mapping[intent]
        
        # Try action
        if action in intent_mapping:
            return intent_mapping[action]
        
        # Try combined
        combined_key = f"{intent}_{action}"
        if combined_key in intent_mapping:
            return intent_mapping[combined_key]
        
        return None
```

---

## Phase-by-Phase Implementation

### Phase 1: Foundation Layer (Week 1)

#### 1.1 Fix `SpecialistCapabilityAgent` Base Class

**Tasks:**
1. Remove `self.enabling_service` and service discovery from `initialize()`
2. Replace `_enhance_with_ai()` placeholder with `self.llm_abstraction.generate_content()`
3. Replace `_call_enabling_service()` placeholder with `self.execute_mcp_tool()`
4. Replace `_gather_requirements()` placeholder with LLM-based conversational AI
5. Remove fallbacks from `_classify_task()` and `_assess_complexity()`

**Code Changes:**
- See "Update 3" above for complete implementation

**Testing:**
```python
# Test that service discovery is removed
agent = SpecialistCapabilityAgent(...)
await agent.initialize()
assert agent.enabling_service is None  # Should not exist
assert agent._orchestrator is not None  # Should be set by orchestrator

# Test that MCP tool execution works
result = await agent._call_enabling_service(request, context)
assert result["success"] == True
assert "service_result" in result

# Test that LLM enhancement works
enhanced = await agent._enhance_with_ai(service_result, request, context)
assert "ai_insights" in enhanced
assert "confidence" in enhanced
```

#### 1.2 Fix `LiaisonDomainAgent` Base Class

**Tasks:**
1. Remove `self.orchestrator` discovery from `initialize()`
2. Replace `_handle_with_mcp_tools()` placeholder with `self.execute_mcp_tool()`
3. Add `_map_intent_to_mcp_tool()` helper method

**Code Changes:**
- See "Update 4" above for complete implementation

**Testing:**
```python
# Test that orchestrator discovery is removed
agent = LiaisonDomainAgent(...)
await agent.initialize()
assert agent.orchestrator is None  # Should not exist (old pattern)
assert agent._orchestrator is not None  # Should be set by orchestrator

# Test that MCP tool execution works
result = await agent._handle_with_mcp_tools(request, intent_analysis)
assert result["success"] == True
assert result["response_type"] == "mcp_tool_execution"
```

#### 1.3 Create `ConversationalAIService`

**Purpose:** Provide conversational AI capabilities for requirements gathering.

**File:** `backend/business_enablement/enabling_services/conversational_ai_service/conversational_ai_service.py`

**Code:**

```python
class ConversationalAIService:
    """
    Conversational AI Service for requirements gathering and dialogue.
    """
    
    def __init__(self, public_works_foundation, logger):
        self.public_works_foundation = public_works_foundation
        self.logger = logger
        
        # Get LLM abstraction
        self.llm_abstraction = public_works_foundation.get_abstraction("llm")
        if self.llm_abstraction is None:
            raise ValueError("LLM abstraction required for ConversationalAIService")
    
    async def gather_requirements(self,
                                 user_request: Dict[str, Any],
                                 context: Dict[str, Any],
                                 conversation_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Gather requirements through conversational AI.
        
        Args:
            user_request: User's request
            context: Current context
            conversation_history: Previous conversation turns
            
        Returns:
            Requirements gathering result with clarification questions
        """
        # Build conversational prompt
        prompt = self._build_requirements_prompt(user_request, context, conversation_history)
        
        # Use LLM abstraction
        response = await self.llm_abstraction.generate_content(
            prompt=prompt,
            content_type="conversational",
            user_context=context.get('user_context', {})
        )
        
        return {
            "clarification_needed": response.get("clarification_needed", False),
            "questions": response.get("questions", []),
            "required_information": response.get("required_information", {}),
            "conversation_response": response.get("content", "")
        }
    
    def _build_requirements_prompt(self, user_request, context, conversation_history):
        """Build prompt for requirements gathering."""
        # Implementation details...
        pass
```

#### 1.4 Create `LLMCompositionService`

**Purpose:** Provide advanced LLM composition for complex reasoning.

**File:** `backend/business_enablement/enabling_services/llm_composition_service/llm_composition_service.py`

**Code:**

```python
class LLMCompositionService:
    """
    LLM Composition Service for complex reasoning and multi-step LLM operations.
    """
    
    def __init__(self, public_works_foundation, logger):
        self.public_works_foundation = public_works_foundation
        self.logger = logger
        
        # Get LLM abstraction
        self.llm_abstraction = public_works_foundation.get_abstraction("llm")
        if self.llm_abstraction is None:
            raise ValueError("LLM abstraction required for LLMCompositionService")
    
    async def generate_insights(self,
                               data: Dict[str, Any],
                               user_context: Dict[str, Any],
                               session_id: str) -> Dict[str, Any]:
        """
        Generate AI-powered insights from data.
        
        Args:
            data: Data to analyze
            user_context: User context
            session_id: Session identifier
            
        Returns:
            Generated insights
        """
        # Build insight generation prompt
        prompt = self._build_insight_prompt(data, user_context)
        
        # Use LLM abstraction (REAL CALL - no fallbacks)
        response = await self.llm_abstraction.generate_content(
            prompt=prompt,
            content_type="insights",
            user_context=user_context
        )
        
        return {
            "insights": response.get("insights", []),
            "patterns": response.get("patterns", []),
            "recommendations": response.get("recommendations", []),
            "confidence": response.get("confidence", 0.85)
        }
    
    def _build_insight_prompt(self, data, user_context):
        """Build prompt for insight generation."""
        # Implementation details...
        pass
```

### Phase 2: Insurance Use Case Agents (Week 2)

#### 2.1 Fix Insurance Specialist Agents

**Agents to Fix:**
1. `UniversalMapperSpecialist`
2. `QualityRemediationSpecialist`
3. `RoutingDecisionSpecialist`
4. `WavePlanningSpecialist`
5. `ChangeImpactAssessmentSpecialist`
6. `CoexistenceStrategySpecialist`
7. `SagaWALManagementSpecialist`

**Pattern for Each:**
1. Remove any LLM placeholders
2. Replace with `self.llm_abstraction.generate_content()` or `self.llm_abstraction.analyze_text()`
3. Replace MCP tool placeholders with `self.execute_mcp_tool()`
4. Remove all fallbacks

**Example Fix for `UniversalMapperSpecialist`:**

```python
# BEFORE (Anti-pattern):
def _calculate_semantic_similarity(self, source_field: str, target_field: str) -> float:
    """Calculate semantic similarity between field names."""
    # Placeholder - would use NLP/embeddings in production
    source_lower = source_field.lower()
    target_lower = target_field.lower()
    if source_lower == target_lower:
        return 1.0
    # ... simple string matching

# AFTER (Correct pattern):
async def _calculate_semantic_similarity(self, source_field: str, target_field: str) -> float:
    """Calculate semantic similarity between field names using LLM."""
    # Validate LLM is available (fail fast)
    if self.llm_abstraction is None:
        raise ValueError("LLM abstraction required for semantic similarity calculation")
    
    # Build prompt for semantic similarity
    prompt = f"""
Calculate the semantic similarity between these two field names on a scale of 0.0 to 1.0:

Source Field: {source_field}
Target Field: {target_field}

Consider:
- Semantic meaning
- Common abbreviations
- Domain-specific terminology

Respond with ONLY a float between 0.0 and 1.0.
"""
    
    try:
        # Use LLM abstraction (REAL CALL - no placeholders)
        response = await self.llm_abstraction.generate_content(
            prompt=prompt,
            content_type="numeric",
            user_context=self.tenant_context
        )
        
        # Parse similarity score
        similarity = float(response.get("content", "0.5"))
        return max(0.0, min(1.0, similarity))  # Clamp to [0.0, 1.0]
        
    except Exception as e:
        self.logger.error(f"❌ Semantic similarity calculation failed: {e}")
        raise
```

### Phase 3: MVP Agents (Week 3)

#### 3.1 Fix MVP Specialist Agents

**Agents to Fix:**
1. `InsightsAnalysisAgent` (remove mock LLM fallbacks)
2. `OperationsSpecialistAgent` (remove fallback blueprints)
3. `BusinessAnalysisSpecialist` (remove LLM placeholders)
4. `RecommendationSpecialist` (remove LLM placeholders)

**Pattern for Each:**
1. Remove `if hasattr(self, 'llm_service') else mock_fallback` patterns
2. Replace with direct `self.llm_abstraction` calls
3. Fail fast if LLM unavailable

**Example Fix for `InsightsAnalysisAgent`:**

```python
# BEFORE (Anti-pattern):
async def _generate_llm_insights(self, insights_data, user_context, session_id):
    if hasattr(self, 'llm_composition_service') and self.llm_composition_service:
        insights = await self.llm_composition_service.generate_insights(...)
    else:
        # Mock LLM insights generation
        insights = {"mock": "data"}

# AFTER (Correct pattern):
async def _generate_llm_insights(self, insights_data, user_context, session_id):
    # Validate LLM is available (fail fast)
    if self.llm_abstraction is None:
        raise ValueError("LLM abstraction required for insight generation")
    
    # Use LLM composition service if available, otherwise use LLM abstraction directly
    if hasattr(self, 'llm_composition_service') and self.llm_composition_service:
        insights = await self.llm_composition_service.generate_insights(
            insights_data, user_context, session_id
        )
    else:
        # Use LLM abstraction directly (REAL CALL - no fallbacks)
        prompt = self._build_insight_prompt(insights_data, user_context)
        response = await self.llm_abstraction.generate_content(
            prompt=prompt,
            content_type="insights",
            user_context=user_context
        )
        insights = {
            "insights": response.get("insights", []),
            "patterns": response.get("patterns", []),
            "recommendations": response.get("recommendations", [])
        }
    
    return insights
```

### Phase 4: MCP Tool Integration (Week 4)

#### 4.1 Ensure All Orchestrators Set Agents

**Pattern:**
```python
# In orchestrator.initialize():
if self.specialist_agent and hasattr(self.specialist_agent, 'set_orchestrator'):
    self.specialist_agent.set_orchestrator(self)  # Give agent access to MCP server

if self.liaison_agent and hasattr(self.liaison_agent, 'set_orchestrator'):
    self.liaison_agent.set_orchestrator(self)  # Give agent access to MCP server
```

#### 4.2 Validate MCP Tool Names in Config

**Add validation:**
```python
# In agent.initialize():
if self.capability_mcp_tools:
    # Validate tools exist in orchestrator's MCP server
    available_tools = self._orchestrator.mcp_server.list_tools()
    for tool_name in self.capability_mcp_tools:
        if tool_name not in available_tools:
            self.logger.error(
                f"❌ MCP tool '{tool_name}' not found in orchestrator's MCP server. "
                f"Available tools: {available_tools}"
            )
            raise ValueError(f"MCP tool '{tool_name}' not available")
```

### Phase 5: Testing & Validation (Week 5)

#### 5.1 Create Anti-Pattern Detection Tests

**File:** `scripts/insurance_use_case/test_agentic_anti_patterns.py`

**Code:**

```python
async def test_no_service_discovery():
    """Test that agents do not discover services directly."""
    agent = SpecialistCapabilityAgent(...)
    await agent.initialize()
    
    # Should not have enabling_service
    assert not hasattr(agent, 'enabling_service') or agent.enabling_service is None
    
    # Should not have discovered service via Curator
    assert agent._service_access_log == []

async def test_no_llm_fallbacks():
    """Test that agents fail fast if LLM unavailable."""
    # Create agent without LLM abstraction
    agent = SpecialistCapabilityAgent(...)
    agent.llm_abstraction = None
    
    # Should raise error, not return mock data
    with pytest.raises(ValueError, match="LLM abstraction required"):
        await agent._enhance_with_ai(service_result, request, context)

async def test_mcp_tool_execution():
    """Test that agents use MCP tools, not direct service calls."""
    agent = SpecialistCapabilityAgent(...)
    agent.set_orchestrator(mock_orchestrator)
    
    # Should execute MCP tool
    result = await agent._call_enabling_service(request, context)
    
    # Verify MCP tool was called
    assert mock_orchestrator.mcp_server.execute_tool.called
    assert result["success"] == True
```

---

## Prevention Mechanisms

### 1. Code Review Checklist

Add to PR template:

```markdown
## Agent Code Review Checklist

- [ ] Agent does NOT discover services via Curator
- [ ] Agent does NOT store `self.enabling_service` or `self.orchestrator` (discovered)
- [ ] Agent uses `self.execute_mcp_tool()` for service interactions
- [ ] Agent uses `self.llm_abstraction` for LLM calls (no placeholders)
- [ ] Agent fails fast if LLM unavailable (no fallbacks)
- [ ] Agent has `set_orchestrator()` called by orchestrator during init
- [ ] All LLM calls are real (no "Placeholder - would use LLM" comments)
- [ ] All MCP tool calls are real (no "Placeholder - would use MCP tools" comments)
```

### 2. Linter Rules

**File:** `.pylintrc` or `ruff.toml`

```toml
[tool.ruff.lint]
# Detect placeholder comments
select = ["PLR", "PLW"]

[tool.ruff.lint.per-file-ignores]
# Allow in test files
"**/test_*.py" = ["PLR0913"]
```

**Custom Rule (if using custom linter):**
```python
# Detect placeholder comments in agent files
def check_no_placeholders(node):
    """Check for placeholder comments in agent methods."""
    for comment in node.comments:
        if "placeholder" in comment.lower() and "would use" in comment.lower():
            yield (
                node.lineno,
                f"Placeholder detected: {comment}. Use real implementation."
            )
```

### 3. Runtime Validation

**Add to agent initialization:**
```python
def _validate_no_anti_patterns(self):
    """Validate agent does not have anti-patterns."""
    # Check for direct service references
    if hasattr(self, 'enabling_service') and self.enabling_service is not None:
        raise ValueError(
            f"ANTI-PATTERN: Agent {self.agent_name} has direct service reference. "
            f"Use MCP tools instead."
        )
    
    # Check for placeholder methods
    import inspect
    for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
        source = inspect.getsource(method)
        if "placeholder" in source.lower() and "would use" in source.lower():
            self.logger.warning(
                f"⚠️ Potential placeholder in {self.agent_name}.{name}"
            )
```

---

## Success Criteria

### Phase 1 Complete When:
- [ ] `SpecialistCapabilityAgent` has no service discovery
- [ ] `LiaisonDomainAgent` has no orchestrator discovery
- [ ] All LLM placeholders replaced with real calls
- [ ] All MCP tool placeholders replaced with real execution
- [ ] `ConversationalAIService` created and tested
- [ ] `LLMCompositionService` created and tested

### Phase 2 Complete When:
- [ ] All 7 Insurance specialist agents use real LLM calls
- [ ] All 7 Insurance specialist agents use real MCP tools
- [ ] No fallbacks or placeholders remain

### Phase 3 Complete When:
- [ ] All 4 MVP specialist agents use real LLM calls
- [ ] All mock LLM fallbacks removed

### Phase 4 Complete When:
- [ ] All orchestrators set agents via `set_orchestrator()`
- [ ] All MCP tool names validated in config
- [ ] All agents can execute MCP tools successfully

### Phase 5 Complete When:
- [ ] All anti-pattern detection tests pass
- [ ] All agents tested with real LLM calls
- [ ] All agents tested with real MCP tool execution
- [ ] Code review checklist added to PR template
- [ ] Linter rules configured

---

## Next Steps

1. **Start with Phase 1.1:** Update `AgentBase` with validation methods
2. **Then Phase 1.2:** Fix `SpecialistCapabilityAgent` base class
3. **Then Phase 1.3:** Fix `LiaisonDomainAgent` base class
4. **Then Phase 1.4:** Create `ConversationalAIService` and `LLMCompositionService`
5. **Then Phase 2:** Fix all Insurance Use Case agents
6. **Then Phase 3:** Fix all MVP agents
7. **Then Phase 4:** Ensure MCP tool integration
8. **Finally Phase 5:** Testing and validation

---

## Appendix: Code Examples Summary

### Example 1: Real LLM Call (No Placeholder)

```python
# ✅ CORRECT
async def _enhance_with_ai(self, service_result, request, context):
    if self.llm_abstraction is None:
        raise ValueError("LLM abstraction required")
    
    prompt = f"Analyze: {service_result}"
    response = await self.llm_abstraction.generate_content(
        prompt=prompt,
        content_type="analysis"
    )
    return {"ai_insights": response.get("content")}

# ❌ WRONG
async def _enhance_with_ai(self, service_result, request, context):
    # Placeholder - would use LLM
    return {"ai_insights": "AI-powered interpretation"}
```

### Example 2: Real MCP Tool Execution (No Placeholder)

```python
# ✅ CORRECT
async def _call_enabling_service(self, request, context):
    if self._orchestrator is None:
        raise ValueError("Orchestrator not set")
    
    tool_name = self.capability_mcp_tools[0]
    result = await self.execute_mcp_tool(tool_name, {
        "task": request.get('task'),
        "data": request.get('data')
    })
    return {"service_result": result}

# ❌ WRONG
async def _call_enabling_service(self, request, context):
    # Call service (placeholder - would use MCP tools)
    return {"service_result": "Service executed successfully"}
```

### Example 3: No Service Discovery (Use MCP Tools)

```python
# ✅ CORRECT
async def initialize(self):
    await super().initialize()
    # Orchestrator will call set_orchestrator(agent) during its init
    # No service discovery needed

# ❌ WRONG
async def initialize(self):
    await super().initialize()
    self.enabling_service = await self.curator_foundation.get_service(...)
```

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-19  
**Status:** Ready for Implementation

