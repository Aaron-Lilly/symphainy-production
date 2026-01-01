# Phase 7: Unify Agent Initialization - Proposal

## Current State Analysis

### Architecture Layers

1. **Agentic Foundation (Foundation Layer - EAGER)**
   - `AgenticFoundationService`: Provides agentic SDK and capabilities
   - `agent_sdk/`: Base classes and utilities (AgentBase, MCPClientManager, PolicyIntegration, etc.)
   - Agent types: DimensionLiaisonAgent, DimensionSpecialistAgent, GlobalGuideAgent, etc.
   - Initialized at platform startup

2. **Realm Agents (Realm Layer - LAZY)**
   - Business Enablement: ContentLiaisonAgent, ContentProcessingAgent, etc.
   - Other realms: Future agents (Journey, Solution, Experience)
   - Currently initialized via `OrchestratorBase.initialize_agent()`
   - Take `di_container` as parameter

### Current Issues

1. **Inconsistent Access Pattern**
   - Agents access Agentic Foundation indirectly (via di_container)
   - No unified way to get Agentic Foundation capabilities
   - Agents don't consistently use Agentic SDK components

2. **Manual Initialization**
   - Each orchestrator manually initializes its agents
   - No centralized agent lifecycle management
   - Agents initialized even if not used

3. **No Agent Registry**
   - Agents not registered with Curator
   - No service discovery for agents
   - No health monitoring for agents

## Proposed Solution

### 1. Unified Agent Initialization Pattern

**Add to OrchestratorBase:**
```python
async def initialize_agent(
    self,
    agent_class: type,
    agent_name: str,
    agent_type: str = "liaison",  # "liaison", "specialist", "guide", etc.
    **kwargs
) -> Optional[Any]:
    """
    Initialize an agent using Agentic Foundation SDK.
    
    This method:
    1. Gets Agentic Foundation from DI container
    2. Uses appropriate Agentic SDK base class
    3. Initializes agent with proper dependencies
    4. Registers agent with Curator
    5. Returns initialized agent
    """
```

**Benefits:**
- Consistent agent initialization across all realms
- Automatic Agentic Foundation access
- Proper SDK component usage
- Curator registration

### 2. Agentic Foundation Access Pattern

**Add to RealmServiceBase:**
```python
async def get_agentic_foundation_api(self) -> Optional[Any]:
    """Get Agentic Foundation service for agent capabilities."""
    return await self.get_foundation_service("AgenticFoundationService")
```

**Benefits:**
- Unified access to Agentic Foundation
- Available to all realm services
- Lazy initialization (Foundation is EAGER, but access is lazy)

### 3. Agent Registry Pattern

**Add agent registration to OrchestratorBase.initialize_agent():**
```python
# Register agent with Curator
await self.register_agent_with_curator(
    agent=agent,
    agent_name=agent_name,
    agent_type=agent_type,
    orchestrator=self
)
```

**Benefits:**
- Service discovery for agents
- Health monitoring
- Agent dashboard integration

### 4. Agent Lifecycle Management

**Add to OrchestratorBase:**
```python
self._agents: Dict[str, Any] = {}  # Track initialized agents

async def get_agent(self, agent_name: str) -> Optional[Any]:
    """Get an agent (lazy-load if needed)."""
    if agent_name in self._agents:
        return self._agents[agent_name]
    # Lazy-load agent if needed
    ...
```

**Benefits:**
- Lazy agent initialization
- Agent reuse
- Lifecycle tracking

## Implementation Plan

### Phase 7.1: Add Agentic Foundation Access
- Add `get_agentic_foundation_api()` to RealmServiceBase
- Update OrchestratorBase to use Agentic Foundation

### Phase 7.2: Enhance OrchestratorBase.initialize_agent()
- Get Agentic Foundation
- Use appropriate Agentic SDK base class
- Register agent with Curator
- Track agents in `_agents` dict

### Phase 7.3: Add Agent Registry
- Create `register_agent_with_curator()` method
- Register agents with metadata (agent_type, orchestrator, capabilities)

### Phase 7.4: Update Existing Agents
- Update ContentLiaisonAgent, ContentProcessingAgent, etc.
- Use unified initialization pattern
- Remove manual initialization code

### Phase 7.5: Add Agent Lazy Loading
- Implement `get_agent()` method in OrchestratorBase
- Lazy-load agents on first access
- Update orchestrators to use lazy loading

## Current Agent Initialization Mismatch

**Problem Identified:**
- `BusinessLiaisonAgentBase` requires many dependencies (agentic_foundation, mcp_client_manager, policy_integration, etc.)
- Current agents (ContentLiaisonAgent, etc.) only take `di_container` and `utility_foundation`
- `OrchestratorBase.initialize_agent()` only passes `di_container`
- This creates a mismatch that needs to be resolved

## Recommended Solution: Agent Factory Pattern

### Approach: Agent Factory in Agentic Foundation

**Agent Factory belongs in Agentic Foundation because:**
1. Agentic Foundation is the source of truth for agent capabilities
2. It has all required dependencies (mcp_client_manager, policy_integration, etc.)
3. It's more reusable across different contexts (orchestrators, managers, services)
4. It aligns with foundation's role as provider of agentic capabilities
5. Better separation of concerns (foundation provides, realm services consume)

**Agent Factory responsibilities:**
1. Create agents with full SDK dependencies
2. Initialize agents properly
3. Register agents with Curator
4. Track agent lifecycle
5. Provide lazy-loading support

### Implementation Details

**Agent Factory in AgenticFoundationService:**
```python
async def create_agent(
    self,
    agent_class: type,
    agent_name: str,
    agent_type: str,  # "liaison", "specialist", "guide", etc.
    realm_name: str,
    di_container: Any,
    orchestrator: Optional[Any] = None,  # Optional orchestrator reference
    **kwargs
) -> Optional[Any]:
    """
    Create and initialize an agent using full Agentic SDK.
    
    This is the unified agent factory - all agents must use this.
    No backward compatibility - all agents must use full SDK.
    
    Args:
        agent_class: Agent class to instantiate
        agent_name: Unique name for the agent
        agent_type: Type of agent ("liaison", "specialist", "guide", etc.)
        realm_name: Realm name (e.g., "business_enablement")
        di_container: DI container for foundation services
        orchestrator: Optional orchestrator that owns this agent
        **kwargs: Additional agent-specific parameters
    
    Returns:
        Initialized agent or None if creation failed
    """
    try:
        # Get all required dependencies
        public_works = di_container.get_foundation_service("PublicWorksFoundationService")
        curator = di_container.get_foundation_service("CuratorFoundationService")
        
        # Get Agentic Foundation components
        mcp_client_manager = self.mcp_client_manager
        policy_integration = self.policy_integration
        tool_composition = self.tool_composition
        agui_formatter = self.agui_formatter
        
        # Create AGUI schema (can be simplified for now)
        from foundations.agentic_foundation.agui_schema_registry import AGUISchema
        agui_schema = AGUISchema(components=[], layout="default")
        
        # Create agent with all dependencies
        agent = agent_class(
            agent_name=agent_name,
            business_domain=realm_name,
            capabilities=kwargs.get("capabilities", []),
            required_roles=kwargs.get("required_roles", []),
            agui_schema=agui_schema,
            foundation_services=di_container,
            agentic_foundation=self,
            public_works_foundation=public_works,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            curator_foundation=curator,
            **kwargs
        )
        
        # Initialize agent
        if hasattr(agent, 'initialize'):
            await agent.initialize()
        
        # Register with Curator
        await self._register_agent_with_curator(
            agent=agent,
            agent_name=agent_name,
            agent_type=agent_type,
            realm_name=realm_name,
            orchestrator=orchestrator
        )
        
        return agent
        
    except Exception as e:
        self.logger.error(f"❌ Failed to create agent {agent_name}: {e}")
        import traceback
        self.logger.error(f"Traceback: {traceback.format_exc()}")
        return None
```

**Simplified OrchestratorBase.initialize_agent():**
```python
async def initialize_agent(
    self,
    agent_class: type,
    agent_name: str,
    agent_type: str = "liaison",  # "liaison", "specialist", "guide", etc.
    **kwargs
) -> Optional[Any]:
    """
    Initialize an agent using Agentic Foundation factory (lazy loading).
    
    This method delegates to Agentic Foundation's agent factory.
    Agents are lazy-loaded (only created when first accessed).
    """
    try:
        # Check if already initialized
        if agent_name in self._agents:
            return self._agents[agent_name]
        
        # Get Agentic Foundation
        agentic_foundation = await self.get_foundation_service("AgenticFoundationService")
        if not agentic_foundation:
            self.logger.error(f"❌ Agentic Foundation not available - cannot create {agent_name}")
            return None
        
        # Create agent via Agentic Foundation factory
        agent = await agentic_foundation.create_agent(
            agent_class=agent_class,
            agent_name=agent_name,
            agent_type=agent_type,
            realm_name=self.realm_name,
            di_container=self.di_container,
            orchestrator=self,
            **kwargs
        )
        
        if agent:
            self._agents[agent_name] = agent
            self.logger.info(f"✅ {agent_name} initialized (lazy)")
        
        return agent
        
    except Exception as e:
        self.logger.error(f"❌ Failed to initialize {agent_name}: {e}")
        return None
```

## Migration Strategy (All at Once, No Backward Compatibility)

### Phase 7.1: Add Agent Factory to Agentic Foundation
- Add `create_agent()` method to `AgenticFoundationService`
- Add `_register_agent_with_curator()` helper method
- Add agent tracking in Agentic Foundation

### Phase 7.2: Update OrchestratorBase.initialize_agent()
- Simplify to delegate to Agentic Foundation factory
- Add `_agents` dict for lazy loading
- Remove legacy initialization code

### Phase 7.3: Add Agent Lazy Loading
- Implement `get_agent()` method in OrchestratorBase
- Lazy-load agents on first access
- Update orchestrators to use lazy loading

### Phase 7.4: Update All Existing Agents
- Update all agents to use full SDK initialization
- Remove legacy `__init__` patterns
- Update all orchestrators to use new pattern
- Test all agents

### Phase 7.5: Add Agent Discovery via Curator
- Ensure all agents registered with Curator
- Add agent discovery methods
- Update agent access patterns

## Decisions Made

1. **Migration Timeline**: ✅ All at once (no gradual migration)
2. **Backward Compatibility**: ✅ None (clean break)
3. **Agent Lifecycle**: ✅ Lazy (on first use)
4. **Agent Discovery**: ✅ Via Curator
5. **Agent SDK Usage**: ✅ All agents use full SDK (lightweight patterns available in SDK)

## Final Architecture

**Agent Factory Location**: ✅ Agentic Foundation (not OrchestratorBase)

**Benefits:**
- ✅ Clean separation of concerns (foundation provides, realm services consume)
- ✅ Reusable across all contexts (orchestrators, managers, services)
- ✅ Source of truth for agent initialization
- ✅ All LLM usage through SDK for proper governance and visibility
- ✅ Lazy loading (aligned with platform vision)
- ✅ Service discovery via Curator
- ✅ Extensibility for future realms

