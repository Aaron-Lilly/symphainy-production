# Agentic Foundation Refactoring Plan - UPDATED

## Overview

Refactor Agentic Foundation to own agent registry/factory and integrate with Curator using Phase 2 patterns, ensuring consistent agent creation, capabilities handling, and registration patterns.

## Current State Issues

### 1. Inconsistent Capabilities Pattern
- **Problem**: Some agents use `self.capabilities` attribute, others implement `get_agent_capabilities()` method
- **Impact**: Factory can't reliably extract capabilities
- **Solution**: Standardize on `self.capabilities` attribute (set in `__init__`), make `get_agent_capabilities()` return `self.capabilities` by default

### 2. Double Registration
- **Problem**: `agent.initialize()` calls `register_with_curator()` AND factory calls `_register_agent_with_curator()`
- **Impact**: Duplicate registrations, inconsistent patterns
- **Solution**: Remove registration from `agent.initialize()`, factory owns registration

### 3. Wrong Registration Pattern
- **Problem**: Factory uses old `register_service()` pattern instead of Phase 2 `register_agent()`
- **Impact**: Inconsistent with Phase 2 architecture
- **Solution**: Use `register_agent()` with `characteristics`/`contracts` format

### 4. Agent Self-Registration
- **Problem**: Agents can self-register via `register_with_curator()` method
- **Impact**: Bypasses factory, creates inconsistency
- **Solution**: Remove agent self-registration methods entirely

### 5. Agents Bypassing Factory
- **Problem**: Some agents are created directly (e.g., `mvp_liaison_agents.py`, `mvp_guide_agent.py`)
- **Impact**: Bypasses factory, no registration, inconsistent patterns
- **Solution**: Refactor to use factory

### 6. Missing Capabilities Validation
- **Problem**: Factory doesn't validate that capabilities are provided
- **Impact**: Agents can be created without capabilities
- **Solution**: Add fail-fast validation in factory

## Target State

### Agentic Foundation Owns Agent Registry/Factory
- **Factory** (`create_agent()`):
  - Validates capabilities are provided (fail fast)
  - Creates agent instance
  - Initializes agent (without registration)
  - Registers with Curator using Phase 2 `register_agent()` pattern
  - Uses standardized capabilities extraction
- **Agents**:
  - Focus on business logic only
  - No self-registration methods
  - Standardized capabilities pattern (`self.capabilities` attribute)
  - All created via factory (no direct instantiation)

## How Services Access Agents

### Current Pattern (Correct)
- **Direct Python Method Calls**: Services/orchestrators call agent methods directly
  - Example: `self.specialist_agent.process_query(query_text, session_token)`
  - Agents are Python objects, not REST services
  - Orchestrators store agents in `self._agents` dict
  - Agents have orchestrator reference via `set_orchestrator()`

### Agent Discovery
- **Via Curator**: Services can discover agents via `curator.discover_agents()` or `curator.get_agent()`
- **Via Factory**: Agentic Foundation maintains factory cache for fast access
- **Via Orchestrator**: Orchestrators own their agents and provide direct access

### Agent API Contract
- **Not REST APIs**: Agents don't expose REST endpoints
- **Python Interface**: Agent API contract documents the agent's Python methods/interface
- **Registration**: Agent API contract registered in `contracts["agent_api"]` for discovery and documentation

## What Agents Should Register with Curator

### Characteristics (What the Agent IS)
1. **Agent Capabilities** - What the agent can do (business capabilities, not MCP tools)
   - Example: `["conversation", "guidance", "analysis_support"]`
   - Required: Yes (validated in factory)

2. **Realm** - Which realm the agent belongs to
   - Example: `"business_enablement"`, `"smart_city"`, `"solution"`, `"journey"`
   - Required: Yes (always present, cross-realm organizational unit)

3. **Agent Specialization** - Optional user-driven customization
   - Example: `"testing_expert"`, `"claims_specialist"`, `"content_processing"`
   - Required: No (optional customization)
   - Stored in: `specialization_config.get("specialization")`

4. **Required Roles** - Smart City roles the agent needs
   - Example: `["librarian", "data_steward"]`
   - Required: No (can be empty list)

5. **AGUI Schema** - Schema for UI generation
   - Required: Yes (agents must have AGUI schema)

### Contracts (How Services Access the Agent)
1. **Agent API Contract** - Documents the agent's Python interface
   - **Not REST endpoints** - Agents are Python objects, not REST services
   - **Python Methods** - Documents available methods (for discovery/documentation)
   - **Access Pattern**: Direct Python method calls
   - Structure:
     ```python
     {
         "agent_api": {
             "service_name": agent_name,
             "realm": realm_name,
             "agent_type": agent_type,
             "orchestrator": orchestrator.service_name if orchestrator else None,
             "agent_id": agent_id,
             "access_pattern": "direct_python_method_calls",
             "interface": "python_object"  # Not REST API
         }
     }
     ```

### What Agents Should NOT Register
- **MCP Tools** - Agents USE MCP tools (via `mcp_client_manager`), they don't expose them
- **REST Endpoints** - Agents don't expose REST APIs
- **SOA APIs** - Agents use services, they don't provide them

## Implementation Plan

### Phase 0: Standardize Capabilities Pattern

**File:** `foundations/agentic_foundation/agent_sdk/agent_base.py`

**Action:** Make `get_agent_capabilities()` return `self.capabilities` by default

```python
async def get_agent_capabilities(self) -> List[str]:
    """
    Get list of agent capabilities.
    
    Default implementation returns self.capabilities attribute.
    Agents can override if they need dynamic capability discovery.
    
    Returns:
        List of capability names
    """
    return self.capabilities if self.capabilities else []
```

**Rationale:**
- Standardizes on `self.capabilities` attribute (set in `__init__`)
- Agents can still override if needed for dynamic capabilities
- Factory can reliably extract capabilities

**Files to Update:**
- `agent_base.py` - Update default implementation
- Review all agent implementations - ensure they set `self.capabilities` in `__init__`
- Remove any custom `get_agent_capabilities()` implementations that just return `self.capabilities`

### Phase 1: Remove Registration from agent.initialize()

**File:** `foundations/agentic_foundation/agent_sdk/agent_base.py`

**Action:** Remove registration call from `initialize()` method

**Current Code (lines 213-215):**
```python
# Register with Curator Foundation if available
if self.curator_foundation:
    await self.register_with_curator(user_context, tenant_context)
```

**New Code:**
```python
# Registration handled by factory (Agentic Foundation owns agent registry)
# Removed: await self.register_with_curator(user_context, tenant_context)
```

**Rationale:**
- Factory owns registration (foundation ownership pattern)
- Prevents double registration
- Aligns with Experience Foundation pattern

### Phase 2: Add Capabilities Validation to Factory

**File:** `foundations/agentic_foundation/agentic_foundation_service.py`

**Action:** Add fail-fast validation in `create_agent()` method

**Location:** After agent creation, before initialization

```python
# Validate capabilities are provided (fail fast)
if not kwargs.get("capabilities"):
    error_msg = f"Agent {agent_name} created without capabilities - capabilities are required"
    self.logger.error(f"❌ {error_msg}")
    await self.record_health_metric("create_agent_missing_capabilities", 1.0, {"agent_name": agent_name})
    await self.log_operation_with_telemetry("create_agent_complete", success=False)
    raise ValueError(error_msg)
```

**Rationale:**
- Ensures all agents have capabilities
- Fail fast - catch issues early
- Prevents agents from being created without capabilities

### Phase 3: Refactor Factory Registration Method

**File:** `foundations/agentic_foundation/agentic_foundation_service.py`

**Current Method:** Uses old `register_service()` pattern

**New Method:**
```python
async def _register_agent_with_curator(
    self,
    agent: Any,
    agent_name: str,
    agent_type: str,
    realm_name: str,
    orchestrator: Optional[Any] = None
) -> bool:
    """
    Register agent with Curator using Phase 2 register_agent() pattern.
    
    Agentic Foundation owns agent registration (similar to Experience Foundation owning routes).
    Agents register their capabilities, specialization, and metadata - NOT MCP tools.
    
    Args:
        agent: Agent instance
        agent_name: Agent name
        agent_type: Agent type ("liaison", "specialist", "guide", etc.)
        realm_name: Realm name
        orchestrator: Optional orchestrator reference
    
    Returns:
        True if registration successful, False otherwise
    """
    try:
        curator = self.di_container.get_foundation_service("CuratorFoundationService")
        if not curator:
            self.logger.warning(f"⚠️ Curator not available - cannot register {agent_name}")
            return False
        
        # Extract agent capabilities (standardized pattern)
        capabilities = []
        if hasattr(agent, 'capabilities') and agent.capabilities:
            capabilities = agent.capabilities
        elif hasattr(agent, 'get_agent_capabilities'):
            try:
                capabilities = await agent.get_agent_capabilities()
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get capabilities from {agent_name}: {e}")
                capabilities = []
        
        # If still empty, try specialization_config
        if not capabilities and hasattr(agent, 'specialization_config'):
            capabilities = agent.specialization_config.get("capabilities", [])
        
        # Validate capabilities were found
        if not capabilities:
            self.logger.error(f"❌ Agent {agent_name} has no capabilities - cannot register")
            return False
        
        # Extract specialization config
        specialization_config = {}
        if hasattr(agent, 'specialization_config') and agent.specialization_config:
            specialization_config = agent.specialization_config
        else:
            # Build from agent attributes if available
            specialization_config = {
                "specialization": getattr(agent, 'specialization_name', None) or getattr(agent, 'specialization', None),
                "required_roles": getattr(agent, 'required_roles', []),
                "agui_schema": getattr(agent, 'agui_schema', {}).schema_name if hasattr(getattr(agent, 'agui_schema', None), 'schema_name') else None
            }
        
        # Build characteristics (agent metadata - what the agent IS)
        characteristics = {
            "capabilities": capabilities,  # What the agent CAN do
            "realm": realm_name,  # Which realm (cross-realm organizational unit)
            "specialization": specialization_config.get("specialization"),  # Optional user-driven customization
            "required_roles": specialization_config.get("required_roles", []),
            "agui_schema": specialization_config.get("agui_schema") or (agent.agui_schema.schema_name if hasattr(agent, 'agui_schema') and agent.agui_schema else None)
        }
        
        # Build contracts (agent API - how services can access the agent)
        # NOTE: Agents are Python objects, not REST services
        # Services access agents via direct Python method calls
        contracts = {
            "agent_api": {
                "service_name": agent_name,
                "realm": realm_name,
                "agent_type": agent_type,
                "orchestrator": orchestrator.service_name if orchestrator else None,
                "agent_id": getattr(agent, 'agent_id', agent_name),
                "access_pattern": "direct_python_method_calls",
                "interface": "python_object"  # Not REST API
            }
            # NOTE: MCP tools are NOT registered here - agents USE MCP tools, they don't expose them
            # MCP servers expose tools, agents consume them via mcp_client_manager
        }
        
        # Register with Curator using Phase 2 pattern
        success = await curator.register_agent(
            agent_id=getattr(agent, 'agent_id', agent_name),
            agent_name=agent_name,
            characteristics=characteristics,
            contracts=contracts,
            user_context=None  # Internal registration (no user context)
        )
        
        if success:
            self.logger.info(f"   📝 Agent {agent_name} registered with Curator (Phase 2)")
            return True
        else:
            self.logger.warning(f"   ⚠️ Agent {agent_name} Curator registration failed")
            return False
        
    except Exception as e:
        self.logger.error(f"❌ Failed to register agent {agent_name} with Curator: {e}")
        import traceback
        self.logger.debug(f"Traceback: {traceback.format_exc()}")
        return False
```

**Key Changes:**
- Uses Phase 2 `register_agent()` pattern
- Standardized capabilities extraction (attribute first, then method, then specialization_config)
- Validates capabilities are found before registration
- Removes MCP tools from registration (agents use them, don't expose them)
- Removes pillar from registration (legacy concept, replaced with realm)
- Registers agent capabilities, realm, specialization (optional), and metadata
- Documents agent API as Python interface (not REST API)

### Phase 4: Remove Agent Self-Registration

**File:** `foundations/agentic_foundation/agent_sdk/agent_base.py`

**Action:** Remove `register_with_curator()` method entirely

**Rationale:**
- Factory handles registration (foundation ownership)
- Prevents duplication and inconsistency
- Aligns with Experience Foundation pattern
- No production deployment = can break and fix

**Files to Check:**
- Verify no agents call `register_with_curator()` externally
- Remove method from `agent_base.py`
- Update any tests that mock this method

### Phase 5: Fix Agents Bypassing Factory

**Files to Fix:**
1. `backend/business_enablement/agents/mvp_liaison_agents.py`
2. `backend/business_enablement/agents/mvp_guide_agent.py`

**Action:** Refactor to use Agentic Foundation factory

**Current Pattern (mvp_liaison_agents.py):**
```python
agent = LiaisonDomainAgent(
    domain_name=domain_name,
    domain_config=config,
    foundation_services=foundation_services,
    agentic_foundation=agentic_foundation,
    # ... all dependencies manually passed
)
await agent.initialize()
```

**New Pattern:**
```python
# Use Agentic Foundation factory
agent = await agentic_foundation.create_agent(
    agent_class=LiaisonDomainAgent,
    agent_name=f"{domain_name.replace('_', ' ').title()} Liaison",
    agent_type="liaison",
    realm_name="business_enablement",
    di_container=foundation_services,
    orchestrator=None,  # Or pass orchestrator if available
    capabilities=config.get('capabilities', []),
    required_roles=[config.get('orchestrator', '')],
    # Pass domain-specific config via kwargs
    domain_name=domain_name,
    domain_config=config
)
```

**Rationale:**
- All agents must go through factory
- Ensures consistent registration
- Factory handles all dependencies

### Phase 6: Audit All Agent Implementations

**Action:** Verify all agents:
1. Set `self.capabilities` in `__init__` (or receive via factory kwargs)
2. Don't bypass factory
3. Don't call `register_with_curator()` directly

**Files to Audit:**
- All agent files in `backend/business_enablement/agents/`
- All agent files in orchestrator subdirectories
- All agent base classes

**Checklist:**
- [ ] All agents set `self.capabilities` in `__init__`
- [ ] All agents created via factory (no direct instantiation)
- [ ] No agents call `register_with_curator()` directly
- [ ] All agents receive capabilities via factory kwargs

### Phase 7: Testing

**Test Cases:**
1. **Factory Registration:**
   - Verify `create_agent()` registers agent with Curator using Phase 2 pattern
   - Verify `characteristics` and `contracts` are correctly formatted
   - Verify agent appears in Curator registry
   - Verify capabilities are correctly extracted

2. **Capabilities Validation:**
   - Verify factory fails fast if capabilities not provided
   - Verify factory validates capabilities are found before registration
   - Verify all agents have capabilities set

3. **No Double Registration:**
   - Verify `agent.initialize()` does NOT call registration
   - Verify factory registration is the only path
   - Verify no duplicate registrations in Curator

4. **Capabilities Standardization:**
   - Verify all agents have `self.capabilities` set
   - Verify `get_agent_capabilities()` returns `self.capabilities` by default
   - Verify factory can extract capabilities reliably

5. **Factory Usage:**
   - Verify all agents created via factory
   - Verify no agents bypass factory
   - Verify agents that previously bypassed factory now use factory

6. **Discovery:**
   - Verify agents can be discovered via Curator
   - Verify factory cache still works for performance
   - Verify agent metadata is correct

## Benefits

1. **Foundation Ownership:** Agentic Foundation owns agent lifecycle (like Experience Foundation owns routes)
2. **Consistency:** Single registration path (no duplication)
3. **Phase 2 Alignment:** Uses new `register_agent()` pattern with `characteristics`/`contracts`
4. **Agent Focus:** Agents focus on business logic, not registration mechanics
5. **Standardized Patterns:** Consistent capabilities pattern across all agents
6. **Fail Fast:** Capabilities validation prevents issues early
7. **Architectural Alignment:** Same pattern across foundations (Experience → routes, Agentic → agents)

## Migration Notes

- **Break and Fix:** Remove agent self-registration immediately (no backward compatibility needed)
- **Factory Registration:** Update factory to use Phase 2 pattern
- **Capabilities:** Standardize on `self.capabilities` attribute pattern
- **Factory Usage:** All agents must go through factory
- **Testing:** Verify all agents are registered via factory (not self-registration)

## Dependencies

- **Curator Foundation:** Must have `register_agent()` method (already implemented)
- **Agent Base:** Must remove `register_with_curator()` method
- **All Agents:** Must be created via factory (fix agents that bypass)
- **All Agents:** Must set `capabilities` in `__init__` (verify and fix if needed)

## Timeline

- **Phase 0:** Standardize capabilities pattern (1 hour)
- **Phase 1:** Remove registration from `agent.initialize()` (30 minutes)
- **Phase 2:** Add capabilities validation to factory (30 minutes)
- **Phase 3:** Refactor factory registration method (1-2 hours)
- **Phase 4:** Remove agent self-registration (30 minutes)
- **Phase 5:** Fix agents bypassing factory (1-2 hours)
- **Phase 6:** Audit all agent implementations (1-2 hours)
- **Phase 7:** Testing (1-2 hours)

**Total:** ~6-9 hours
