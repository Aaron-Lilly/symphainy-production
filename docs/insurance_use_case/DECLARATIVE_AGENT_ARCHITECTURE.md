# Declarative Agent Architecture Design

## Executive Summary

This document proposes a shift from hardcoded agent logic to a **declarative, configuration-driven agent pattern** similar to CrewAI's JSON "script" approach. Instead of agents having hardcoded methods that call LLM abstraction, agents become **declarative configurations** that the LLM abstraction uses to "do its thing" (chat, generate content, analyze text, etc.).

**Key Innovation:** The LLM abstraction receives a **prompt** that includes:
- What the agent should do (role, goal, backstory)
- Which MCP Servers/Tools it can use (scoped to prevent overwhelming)
- The current request/context

The **base class wrapper** provides standard capabilities (telemetry, security, tenant isolation, etc.) without hardcoding business logic.

---

## Table of Contents

1. [Current Approach vs. Proposed Approach](#current-approach-vs-proposed-approach)
2. [Architecture Design](#architecture-design)
3. [Agent Configuration Schema](#agent-configuration-schema)
4. [Implementation Pattern](#implementation-pattern)
5. [Code Examples](#code-examples)
6. [Migration Strategy](#migration-strategy)
7. [Benefits](#benefits)

---

## Current Approach vs. Proposed Approach

### Current Approach (Hardcoded Logic)

```python
class SpecialistCapabilityAgent:
    async def execute_capability(self, request):
        # 1. Hardcoded: Analyze context
        context_analysis = await self._analyze_request_context(request)
        
        # 2. Hardcoded: Gather requirements
        if context_analysis.get('needs_clarification'):
            clarification = await self._gather_requirements(request, context_analysis)
        
        # 3. Hardcoded: Call service
        service_result = await self._call_enabling_service(request, context_analysis)
        
        # 4. Hardcoded: Enhance with AI
        enhanced_result = await self._enhance_with_ai(service_result, request, context_analysis)
        
        # 5. Hardcoded: Personalize
        personalized_result = await self._personalize_output(enhanced_result, request)
        
        return personalized_result
```

**Problems:**
- Hardcoded logic flow (not flexible)
- Each agent needs custom methods
- Difficult to configure or change behavior
- LLM calls scattered throughout code

### Proposed Approach (Declarative Configuration)

```python
# Agent Configuration (JSON/YAML)
{
    "agent_name": "UniversalMapperSpecialist",
    "role": "Schema Mapping Specialist",
    "goal": "Create accurate field mappings between legacy schemas and canonical models",
    "backstory": "Expert in schema mapping, data transformation, and semantic analysis",
    "allowed_mcp_servers": ["InsuranceMigrationMCPServer"],
    "allowed_tools": ["map_to_canonical", "discover_schema", "validate_mapping"],
    "capabilities": ["semantic_analysis", "pattern_matching", "field_mapping"]
}

# Agent Execution (Base Class)
class DeclarativeAgentBase:
    async def process_request(self, request):
        # 1. Build prompt from configuration
        prompt = self._build_agent_prompt(request)
        
        # 2. Call LLM abstraction with prompt
        llm_response = await self.llm_abstraction.generate_content(
            prompt=prompt,
            content_type="agentic_reasoning",
            available_tools=self._get_available_tools(),
            user_context=request.get('user_context', {})
        )
        
        # 3. Execute tools that LLM decided to use
        tool_results = await self._execute_tools_from_llm_response(llm_response)
        
        # 4. Return results (with telemetry, security, etc. handled by wrapper)
        return self._format_response(llm_response, tool_results)
```

**Benefits:**
- Declarative configuration (easy to change)
- LLM does the reasoning (not hardcoded)
- Scoped tools (agents only see relevant tools)
- Standard capabilities in wrapper (telemetry, security, etc.)

---

## Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Declarative Agent Base                     │
│  (Provides: Telemetry, Security, Tenant Isolation, etc.)     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Uses
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Agent Configuration (JSON/YAML)                │
│  - role, goal, backstory                                     │
│  - allowed_mcp_servers                                       │
│  - allowed_tools                                             │
│  - capabilities                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Builds Prompt
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM Abstraction                           │
│  - Receives: Agent config + Request + Available Tools       │
│  - Returns: Reasoning + Tool Calls to Execute               │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Executes
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Tool Execution (Scoped)                   │
│  - Only tools from allowed_mcp_servers                      │
│  - Only tools from allowed_tools list                      │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

1. **DeclarativeAgentBase (Wrapper)**
   - Provides standard capabilities (telemetry, security, tenant isolation)
   - Loads agent configuration
   - Builds prompts from configuration
   - Executes tools based on LLM decisions
   - Formats responses

2. **Agent Configuration (JSON/YAML)**
   - Defines agent's role, goal, backstory
   - Scopes MCP servers and tools
   - Defines capabilities

3. **LLM Abstraction**
   - Receives agent config + request + available tools
   - Does the reasoning (decides what to do, which tools to use)
   - Returns structured response with tool calls

4. **MCP Tool Execution**
   - Executes only scoped tools
   - Validates tool access
   - Returns results

---

## Agent Configuration Schema

### Configuration File Format (JSON)

```json
{
    "agent_name": "UniversalMapperSpecialist",
    "role": "Schema Mapping Specialist",
    "goal": "Create accurate field mappings between legacy schemas and canonical models with high confidence scores",
    "backstory": "You are an expert in schema mapping, data transformation, and semantic analysis. You have deep knowledge of insurance domain models and can identify semantic relationships between fields even when names differ.",
    "instructions": [
        "Analyze source and target schemas carefully",
        "Use semantic similarity to match fields",
        "Validate mappings before returning results",
        "Provide confidence scores for each mapping"
    ],
    "allowed_mcp_servers": [
        "InsuranceMigrationMCPServer"
    ],
    "allowed_tools": [
        "map_to_canonical",
        "discover_schema",
        "validate_mapping",
        "get_similar_patterns"
    ],
    "capabilities": [
        "semantic_analysis",
        "pattern_matching",
        "field_mapping",
        "confidence_scoring"
    ],
    "llm_config": {
        "model": "gpt-4",
        "temperature": 0.3,
        "max_tokens": 2000
    },
    "tool_selection_strategy": "autonomous",  // or "guided", "restricted"
    "max_tool_calls_per_request": 5
}
```

### Configuration File Format (YAML)

```yaml
agent_name: UniversalMapperSpecialist
role: Schema Mapping Specialist
goal: Create accurate field mappings between legacy schemas and canonical models with high confidence scores
backstory: |
  You are an expert in schema mapping, data transformation, and semantic analysis.
  You have deep knowledge of insurance domain models and can identify semantic
  relationships between fields even when names differ.

instructions:
  - Analyze source and target schemas carefully
  - Use semantic similarity to match fields
  - Validate mappings before returning results
  - Provide confidence scores for each mapping

allowed_mcp_servers:
  - InsuranceMigrationMCPServer

allowed_tools:
  - map_to_canonical
  - discover_schema
  - validate_mapping
  - get_similar_patterns

capabilities:
  - semantic_analysis
  - pattern_matching
  - field_mapping
  - confidence_scoring

llm_config:
  model: gpt-4
  temperature: 0.3
  max_tokens: 2000

tool_selection_strategy: autonomous  # or "guided", "restricted"
max_tool_calls_per_request: 5
```

### Configuration Schema Validation

```python
AGENT_CONFIG_SCHEMA = {
    "type": "object",
    "required": ["agent_name", "role", "goal", "backstory"],
    "properties": {
        "agent_name": {"type": "string"},
        "role": {"type": "string"},
        "goal": {"type": "string"},
        "backstory": {"type": "string"},
        "instructions": {
            "type": "array",
            "items": {"type": "string"}
        },
        "allowed_mcp_servers": {
            "type": "array",
            "items": {"type": "string"}
        },
        "allowed_tools": {
            "type": "array",
            "items": {"type": "string"}
        },
        "capabilities": {
            "type": "array",
            "items": {"type": "string"}
        },
        "llm_config": {
            "type": "object",
            "properties": {
                "model": {"type": "string"},
                "temperature": {"type": "number"},
                "max_tokens": {"type": "integer"}
            }
        },
        "tool_selection_strategy": {
            "type": "string",
            "enum": ["autonomous", "guided", "restricted"]
        },
        "max_tool_calls_per_request": {"type": "integer"}
    }
}
```

---

## Implementation Pattern

### Base Class: `DeclarativeAgentBase`

```python
class DeclarativeAgentBase(AgentBase):
    """
    Declarative Agent Base - Configuration-driven agent execution.
    
    Agents are defined by configuration (role, goal, backstory, tools),
    and the LLM abstraction does the reasoning about what to do.
    """
    
    def __init__(self,
                 agent_config_path: str,  # Path to JSON/YAML config
                 foundation_services: DIContainerService,
                 agentic_foundation: AgenticFoundationService,
                 mcp_client_manager: MCPClientManager,
                 policy_integration: PolicyIntegration,
                 tool_composition: ToolComposition,
                 agui_formatter: AGUIOutputFormatter,
                 curator_foundation=None,
                 **kwargs):
        """
        Initialize declarative agent from configuration.
        
        Args:
            agent_config_path: Path to agent configuration file (JSON/YAML)
            ... (other standard AgentBase parameters)
        """
        # Load agent configuration
        self.agent_config = self._load_agent_config(agent_config_path)
        
        # Validate configuration
        self._validate_agent_config(self.agent_config)
        
        # Initialize base class with agent name from config
        super().__init__(
            agent_name=self.agent_config["agent_name"],
            capabilities=self.agent_config.get("capabilities", []),
            required_roles=[],  # Not needed for declarative agents
            agui_schema=self._build_agui_schema_from_config(),
            foundation_services=foundation_services,
            agentic_foundation=agentic_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            curator_foundation=curator_foundation,
            **kwargs
        )
        
        # Store configuration
        self.role = self.agent_config["role"]
        self.goal = self.agent_config["goal"]
        self.backstory = self.agent_config["backstory"]
        self.instructions = self.agent_config.get("instructions", [])
        self.allowed_mcp_servers = self.agent_config.get("allowed_mcp_servers", [])
        self.allowed_tools = self.agent_config.get("allowed_tools", [])
        self.llm_config = self.agent_config.get("llm_config", {})
        self.tool_selection_strategy = self.agent_config.get("tool_selection_strategy", "autonomous")
        self.max_tool_calls = self.agent_config.get("max_tool_calls_per_request", 10)
        
        # Orchestrator reference (set by orchestrator for MCP server access)
        self._orchestrator = None
        
        # Available tools cache (scoped to allowed tools)
        self._available_tools_cache = None
        
        self.logger.info(f"✅ Declarative agent '{self.agent_name}' initialized from config")
    
    def _load_agent_config(self, config_path: str) -> Dict[str, Any]:
        """Load agent configuration from JSON or YAML file."""
        import json
        import yaml
        from pathlib import Path
        
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Agent configuration file not found: {config_path}")
        
        with open(path, 'r') as f:
            if path.suffix == '.yaml' or path.suffix == '.yml':
                return yaml.safe_load(f)
            else:
                return json.load(f)
    
    def _validate_agent_config(self, config: Dict[str, Any]):
        """Validate agent configuration against schema."""
        # Use JSON schema validation
        import jsonschema
        try:
            jsonschema.validate(instance=config, schema=AGENT_CONFIG_SCHEMA)
        except jsonschema.ValidationError as e:
            raise ValueError(f"Invalid agent configuration: {e.message}")
    
    def set_orchestrator(self, orchestrator):
        """Set orchestrator reference (called by orchestrator during initialization)."""
        self._orchestrator = orchestrator
        
        # Validate orchestrator has MCP server
        if not hasattr(orchestrator, 'mcp_server') or orchestrator.mcp_server is None:
            raise ValueError("Orchestrator must have MCP server for agent tool access")
        
        # Cache available tools (scoped to allowed tools)
        self._available_tools_cache = self._get_scoped_tools()
        
        self.logger.info(f"✅ Orchestrator set for {self.agent_name} (MCP server available)")
    
    def _get_scoped_tools(self) -> List[Dict[str, Any]]:
        """
        Get available tools scoped to this agent's allowed tools.
        
        This prevents agents from seeing tools they shouldn't use.
        """
        if self._orchestrator is None:
            return []
        
        # Get all tools from orchestrator's MCP server
        all_tools = self._orchestrator.mcp_server.list_tools()
        
        # Filter to only allowed tools
        scoped_tools = [
            tool for tool in all_tools
            if tool["name"] in self.allowed_tools
        ]
        
        return scoped_tools
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process request using declarative agent pattern.
        
        Pattern:
        1. Build prompt from agent configuration + request
        2. Call LLM abstraction with prompt + available tools
        3. LLM decides what to do and which tools to use
        4. Execute tools that LLM decided to use
        5. Return results (with telemetry, security handled by wrapper)
        """
        try:
            # Start telemetry tracking (standard capability)
            await self.log_operation_with_telemetry("process_request_start", success=True)
            
            # Security validation (standard capability)
            user_context = request.get('user_context', {})
            if user_context and self.security:
                if not await self.security.check_permissions(user_context, "agent", "execute"):
                    raise PermissionError("Access denied")
            
            # Tenant validation (standard capability)
            if user_context:
                tenant_id = user_context.get("tenant_id")
                if tenant_id and not await self._validate_tenant_access(tenant_id):
                    raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            # Build prompt from agent configuration
            prompt = self._build_agent_prompt(request)
            
            # Get available tools (scoped to this agent)
            available_tools = self._get_available_tools()
            
            # Call LLM abstraction with prompt + tools
            llm_response = await self.llm_abstraction.generate_content(
                prompt=prompt,
                content_type="agentic_reasoning",
                available_tools=available_tools,
                user_context=user_context,
                llm_config=self.llm_config
            )
            
            # Extract tool calls from LLM response
            tool_calls = self._extract_tool_calls_from_llm_response(llm_response)
            
            # Execute tools (with validation)
            tool_results = await self._execute_tools(tool_calls, request)
            
            # Format response
            response = self._format_response(llm_response, tool_results, request)
            
            # End telemetry tracking (standard capability)
            await self.log_operation_with_telemetry("process_request_complete", success=True)
            
            return response
            
        except PermissionError:
            raise
        except Exception as e:
            await self.handle_error_with_audit(e, "process_request")
            raise
    
    def _build_agent_prompt(self, request: Dict[str, Any]) -> str:
        """
        Build prompt from agent configuration + request.
        
        This is where the "script" is created for the LLM.
        """
        prompt = f"""You are a {self.role}.

Your goal: {self.goal}

Your backstory: {self.backstory}

Instructions:
{chr(10).join(f"- {instruction}" for instruction in self.instructions)}

Current Request:
{request.get('message', request.get('task', 'No request provided'))}

Context:
{json.dumps(request.get('data', {}), indent=2)}

Available Tools:
{self._format_available_tools()}

Your task is to:
1. Understand the request
2. Decide which tools to use (if any)
3. Execute the tools
4. Provide a response

Respond in JSON format with:
{{
    "reasoning": "Your reasoning about what to do",
    "tool_calls": [
        {{"tool_name": "tool1", "parameters": {{...}}}},
        {{"tool_name": "tool2", "parameters": {{...}}}}
    ],
    "response": "Your response to the user"
}}
"""
        return prompt
    
    def _format_available_tools(self) -> str:
        """Format available tools for prompt."""
        if not self._available_tools_cache:
            return "No tools available"
        
        tool_descriptions = []
        for tool in self._available_tools_cache:
            tool_descriptions.append(
                f"- {tool['name']}: {tool.get('description', 'No description')}"
            )
        
        return "\n".join(tool_descriptions)
    
    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools (scoped to this agent)."""
        if self._available_tools_cache is None:
            self._available_tools_cache = self._get_scoped_tools()
        return self._available_tools_cache
    
    def _extract_tool_calls_from_llm_response(self, llm_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract tool calls from LLM response.
        
        LLM response should be in format:
        {
            "reasoning": "...",
            "tool_calls": [
                {"tool_name": "tool1", "parameters": {...}},
                {"tool_name": "tool2", "parameters": {...}}
            ],
            "response": "..."
        }
        """
        # Parse LLM response (could be JSON string or dict)
        if isinstance(llm_response, str):
            import json
            llm_response = json.loads(llm_response)
        
        tool_calls = llm_response.get("tool_calls", [])
        
        # Validate tool calls are in allowed tools
        validated_tool_calls = []
        for tool_call in tool_calls:
            tool_name = tool_call.get("tool_name")
            if tool_name in self.allowed_tools:
                validated_tool_calls.append(tool_call)
            else:
                self.logger.warning(
                    f"⚠️ Tool '{tool_name}' not in allowed tools. Skipping."
                )
        
        # Limit tool calls per request
        if len(validated_tool_calls) > self.max_tool_calls:
            self.logger.warning(
                f"⚠️ Too many tool calls ({len(validated_tool_calls)} > {self.max_tool_calls}). "
                f"Limiting to {self.max_tool_calls}."
            )
            validated_tool_calls = validated_tool_calls[:self.max_tool_calls]
        
        return validated_tool_calls
    
    async def _execute_tools(self, tool_calls: List[Dict[str, Any]], request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tools that LLM decided to use.
        
        Args:
            tool_calls: List of tool calls from LLM
            request: Original request
            
        Returns:
            Aggregated tool results
        """
        if not tool_calls:
            return {}
        
        if self._orchestrator is None:
            raise ValueError("Orchestrator not set. Cannot execute tools.")
        
        tool_results = {}
        for tool_call in tool_calls:
            tool_name = tool_call.get("tool_name")
            parameters = tool_call.get("parameters", {})
            
            try:
                # Execute tool via orchestrator's MCP server
                result = await self._orchestrator.mcp_server.execute_tool(
                    tool_name,
                    {**parameters, "user_context": request.get("user_context", {})}
                )
                
                tool_results[tool_name] = result
                
            except Exception as e:
                self.logger.error(f"❌ Tool execution failed for '{tool_name}': {e}")
                tool_results[tool_name] = {"success": False, "error": str(e)}
        
        return tool_results
    
    def _format_response(self, llm_response: Dict[str, Any], tool_results: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
        """Format final response."""
        return {
            "success": True,
            "agent_name": self.agent_name,
            "role": self.role,
            "reasoning": llm_response.get("reasoning", ""),
            "tool_results": tool_results,
            "response": llm_response.get("response", ""),
            "timestamp": datetime.now().isoformat()
        }
```

---

## Code Examples

### Example 1: Universal Mapper Specialist (Declarative)

**Configuration File:** `agents/universal_mapper_specialist.yaml`

```yaml
agent_name: UniversalMapperSpecialist
role: Schema Mapping Specialist
goal: Create accurate field mappings between legacy schemas and canonical models
backstory: |
  You are an expert in schema mapping and data transformation. You understand
  semantic relationships between fields and can identify mappings even when
  field names differ.

instructions:
  - Analyze source and target schemas
  - Use semantic similarity to match fields
  - Validate mappings before returning
  - Provide confidence scores

allowed_mcp_servers:
  - InsuranceMigrationMCPServer

allowed_tools:
  - map_to_canonical
  - discover_schema
  - validate_mapping
  - get_similar_patterns

capabilities:
  - semantic_analysis
  - pattern_matching
  - field_mapping
```

**Usage:**

```python
# Initialize agent from configuration
agent = DeclarativeAgentBase(
    agent_config_path="agents/universal_mapper_specialist.yaml",
    foundation_services=di_container,
    agentic_foundation=agentic_foundation,
    mcp_client_manager=mcp_client_manager,
    policy_integration=policy_integration,
    tool_composition=tool_composition,
    agui_formatter=agui_formatter
)

# Set orchestrator (gives agent access to MCP server)
agent.set_orchestrator(insurance_migration_orchestrator)

# Process request (LLM does the reasoning)
result = await agent.process_request({
    "message": "Map legacy policy schema to canonical model",
    "data": {
        "source_schema": {...},
        "target_schema": {...}
    },
    "user_context": {...}
})
```

### Example 2: Quality Remediation Specialist (Declarative)

**Configuration File:** `agents/quality_remediation_specialist.yaml`

```yaml
agent_name: QualityRemediationSpecialist
role: Data Quality Remediation Specialist
goal: Identify and remediate data quality issues in legacy data
backstory: |
  You are an expert in data quality analysis and remediation. You can identify
  issues like missing values, format inconsistencies, and data integrity problems.

instructions:
  - Analyze data quality issues
  - Prioritize issues by severity
  - Suggest remediation strategies
  - Validate fixes

allowed_mcp_servers:
  - InsuranceMigrationMCPServer

allowed_tools:
  - analyze_data_quality
  - remediate_quality_issues
  - validate_remediation

capabilities:
  - quality_analysis
  - issue_prioritization
  - remediation_strategy
```

### Example 3: Comparison with Current Approach

**Current Approach (Hardcoded):**

```python
class UniversalMapperSpecialist(SpecialistCapabilityAgent):
    async def _calculate_semantic_similarity(self, source_field, target_field):
        # Hardcoded logic
        if source_field.lower() == target_field.lower():
            return 1.0
        # ... more hardcoded logic
```

**Declarative Approach:**

```yaml
# Configuration defines what agent does
agent_name: UniversalMapperSpecialist
role: Schema Mapping Specialist
goal: Create accurate field mappings
# LLM does the reasoning - no hardcoded logic needed!
```

---

## Migration Strategy

### Phase 1: Create Declarative Base Class

1. Create `DeclarativeAgentBase` class
2. Implement configuration loading and validation
3. Implement prompt building from configuration
4. Implement tool scoping and execution

### Phase 2: Migrate One Agent (Pilot)

1. Choose one agent (e.g., `UniversalMapperSpecialist`)
2. Create configuration file for that agent
3. Migrate agent to use `DeclarativeAgentBase`
4. Test thoroughly

### Phase 3: Migrate Remaining Agents

1. Create configuration files for all agents
2. Migrate agents one by one
3. Test each migration
4. Remove old hardcoded logic

### Phase 4: Enhance LLM Abstraction

1. Enhance LLM abstraction to support "agentic_reasoning" content type
2. Add tool call extraction from LLM responses
3. Add structured response format

---

## Benefits

### 1. **Flexibility**
- Easy to change agent behavior (just update config)
- No code changes needed for new capabilities
- Configuration-driven = easier to maintain

### 2. **Scoped Tools**
- Agents only see tools they should use
- Prevents overwhelming agents with irrelevant tools
- Better security (principle of least privilege)

### 3. **Centralized Reasoning**
- LLM does the reasoning (not hardcoded)
- More intelligent decision-making
- Easier to improve (just improve LLM prompts)

### 4. **Standard Capabilities**
- Telemetry, security, tenant isolation in wrapper
- No need to implement in each agent
- Consistent behavior across all agents

### 5. **Easier Testing**
- Test configuration files (not code)
- Mock LLM responses for testing
- Easier to validate agent behavior

### 6. **Better Alignment with Headless Architecture**
- Configuration = "head" (swappable)
- Base class = "body" (consistent)
- LLM abstraction = "brain" (intelligent)

---

## Next Steps

1. **Review this design** with the team
2. **Create proof-of-concept** with one agent
3. **Enhance LLM abstraction** to support agentic reasoning
4. **Migrate agents** one by one
5. **Update documentation** and examples

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-19  
**Status:** Design Proposal - Ready for Review









