# OrchestratorBase Class Proposal

## Problem Statement

Currently, orchestrators have inconsistent patterns:
- **ContentAnalysisOrchestrator**: Plain class (no base class) ❌
- **InsightsOrchestrator**: Extends `RealmServiceBase` ✅
- **OperationsOrchestrator**: Extends `RealmServiceBase` ✅
- **BusinessOutcomesOrchestrator**: Extends `RealmServiceBase` ✅

**Issue**: `RealmServiceBase` is designed for **realm services** (atomic capabilities), not **orchestrators** (service composition).

## Key Differences: Realm Services vs Orchestrators

### Realm Services (Content Steward, Librarian, etc.)
- **Purpose**: Provide atomic capabilities (SOA APIs)
- **Pattern**: "I do one thing well"
- **Examples**: `parse_file()`, `store_document()`, `calculate_metrics()`
- **Access**: Direct infrastructure abstractions, Smart City services

### Orchestrators (ContentAnalysis, Insights, Operations, etc.)
- **Purpose**: Compose and coordinate services for use cases
- **Pattern**: "I orchestrate multiple services to deliver a use case"
- **Examples**: `handle_content_upload()` → delegates to FileParser, Content Steward, etc.
- **Access**: 
  - Business Orchestrator (for enabling services)
  - Smart City services (via Curator)
  - Infrastructure abstractions (via Platform Gateway)
  - Agents (liaison agents, processing agents)

## Orchestrator Requirements

Based on analysis of existing orchestrators, they need:

1. **Business Orchestrator Reference** (for enabling services)
2. **Smart City Access** (via RealmServiceBase)
3. **Infrastructure Access** (via RealmServiceBase)
4. **Agent Initialization** (liaison agents, processing agents)
5. **Service Composition Helpers** (coordinate multiple services)
6. **Use Case Orchestration Patterns** (standardized workflows)
7. **Curator Registration** (make orchestrators discoverable)

## Proposed Solution: OrchestratorBase

Create a new base class that:
- **Extends RealmServiceBase** (to get Smart City access, infrastructure, etc.)
- **Adds orchestrator-specific capabilities** (Business Orchestrator reference, agent helpers, composition patterns)

### Architecture

```
OrchestratorBase(RealmServiceBase)
├── Inherits from RealmServiceBase:
│   ├── Smart City access (Librarian, Content Steward, etc.)
│   ├── Infrastructure abstractions (via Platform Gateway)
│   ├── Curator registration
│   ├── Health monitoring
│   └── Security, performance, etc.
├── Orchestrator-specific:
│   ├── Business Orchestrator reference
│   ├── Agent initialization helpers
│   ├── Service composition helpers
│   └── Use case orchestration patterns
```

### Implementation

```python
from bases.realm_service_base import RealmServiceBase
from typing import Dict, Any, Optional, List

class OrchestratorBase(RealmServiceBase):
    """
    Base class for all orchestrators (use case coordinators).
    
    Orchestrators compose and coordinate services to deliver use cases.
    They differ from realm services in that they:
    - Compose multiple services (not provide atomic capabilities)
    - Coordinate workflows across services
    - Manage use case-specific orchestration logic
    - Initialize and manage agents (liaison, processing, etc.)
    
    Architecture:
    - Extends RealmServiceBase for Smart City access and infrastructure
    - Adds Business Orchestrator reference for enabling services
    - Provides orchestrator-specific helpers and patterns
    """
    
    def __init__(
        self,
        service_name: str,
        realm_name: str,
        platform_gateway: Any,
        di_container: Any,
        business_orchestrator: Any
    ):
        """
        Initialize orchestrator base.
        
        Args:
            service_name: Name of the orchestrator service
            realm_name: Realm name (e.g., "business_enablement")
            platform_gateway: Platform Gateway for infrastructure access
            di_container: DI Container for service discovery
            business_orchestrator: Business Orchestrator reference (for enabling services)
        """
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        self.business_orchestrator = business_orchestrator
        self.orchestrator_name = service_name
        
        # Agents (initialized in initialize())
        self.liaison_agent = None
        self.processing_agent = None
        
        # Enabling services (lazy initialization)
        self._enabling_services = {}
    
    async def initialize(self) -> bool:
        """
        Initialize orchestrator.
        
        Subclasses should override this to:
        1. Call super().initialize()
        2. Get Smart City services
        3. Initialize agents
        4. Register with Curator
        """
        await super().initialize()
        return True
    
    # ========================================================================
    # ORCHESTRATOR-SPECIFIC HELPERS
    # ========================================================================
    
    async def get_enabling_service(self, service_name: str) -> Optional[Any]:
        """
        Get enabling service from Business Orchestrator.
        
        Args:
            service_name: Name of enabling service (e.g., "FileParserService")
        
        Returns:
            Enabling service instance or None
        """
        if not self.business_orchestrator:
            self.logger.warning(f"⚠️ Business Orchestrator not available for {service_name}")
            return None
        
        # Get from Business Orchestrator's discovered services
        discovered_services = getattr(self.business_orchestrator, 'discovered_services', {})
        return discovered_services.get(service_name)
    
    async def compose_services(
        self,
        service_names: List[str],
        operation: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Compose multiple services to perform an operation.
        
        Args:
            service_names: List of service names to compose
            operation: Operation to perform
            **kwargs: Operation parameters
        
        Returns:
            Composition result
        """
        services = []
        for service_name in service_names:
            service = await self.get_enabling_service(service_name)
            if service:
                services.append(service)
            else:
                self.logger.warning(f"⚠️ Service {service_name} not available")
        
        if not services:
            return {
                "success": False,
                "error": f"No services available for composition: {service_names}"
            }
        
        # Delegate to Business Orchestrator for composition
        if hasattr(self.business_orchestrator, 'compose_services'):
            return await self.business_orchestrator.compose_services(
                services=services,
                operation=operation,
                **kwargs
            )
        
        return {
            "success": False,
            "error": "Service composition not available"
        }
    
    async def initialize_agent(
        self,
        agent_class: type,
        agent_name: str,
        **kwargs
    ) -> Optional[Any]:
        """
        Initialize an agent for the orchestrator.
        
        Args:
            agent_class: Agent class to instantiate
            agent_name: Name of the agent (for logging)
            **kwargs: Agent initialization parameters
        
        Returns:
            Initialized agent or None
        """
        try:
            if not self.di_container:
                self.logger.warning(f"⚠️ DI Container not available for {agent_name}")
                return None
            
            agent = agent_class(di_container=self.di_container, **kwargs)
            if hasattr(agent, 'initialize'):
                await agent.initialize()
            
            self.logger.info(f"✅ {agent_name} initialized")
            return agent
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {agent_name}: {e}")
            return None
    
    # ========================================================================
    # USE CASE ORCHESTRATION PATTERNS
    # ========================================================================
    
    async def orchestrate_workflow(
        self,
        workflow_steps: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate a multi-step workflow.
        
        Args:
            workflow_steps: List of workflow steps (each with 'service', 'operation', 'params')
            context: Workflow context (shared across steps)
        
        Returns:
            Workflow result
        """
        context = context or {}
        results = []
        
        for step in workflow_steps:
            service_name = step.get('service')
            operation = step.get('operation')
            params = step.get('params', {})
            
            service = await self.get_enabling_service(service_name)
            if not service:
                return {
                    "success": False,
                    "error": f"Service {service_name} not available",
                    "completed_steps": len(results)
                }
            
            # Execute step
            if hasattr(service, operation):
                result = await getattr(service, operation)(**params, **context)
                results.append(result)
                context.update(result.get('context', {}))
            else:
                return {
                    "success": False,
                    "error": f"Operation {operation} not available on {service_name}",
                    "completed_steps": len(results)
                }
        
        return {
            "success": True,
            "results": results,
            "context": context
        }
```

## Migration Path

### Step 1: Create OrchestratorBase
- Create `bases/orchestrator_base.py`
- Implement base class with orchestrator-specific helpers
- Add to `bases/__init__.py`

### Step 2: Update ContentAnalysisOrchestrator
- Change from plain class to `OrchestratorBase`
- Update `__init__` to match base class signature
- Update `initialize()` to call `super().initialize()`
- Use orchestrator-specific helpers

### Step 3: Update Other Orchestrators (Optional)
- InsightsOrchestrator, OperationsOrchestrator, etc. can migrate to `OrchestratorBase`
- Or keep extending `RealmServiceBase` if they don't need orchestrator-specific features

### Step 4: Update BusinessOrchestratorService
- Update initialization code to use new base class
- Ensure proper parameter passing

## Benefits

1. **Consistency**: All orchestrators follow the same pattern
2. **Reusability**: Orchestrator-specific helpers available to all
3. **Maintainability**: Changes to orchestrator patterns in one place
4. **Clarity**: Clear distinction between realm services and orchestrators
5. **Extensibility**: Easy to add new orchestrator-specific capabilities

## Questions to Consider

1. **Should all orchestrators use OrchestratorBase?**
   - Yes: Consistent pattern, easier maintenance
   - No: Some orchestrators might not need orchestrator-specific features

2. **Should OrchestratorBase extend RealmServiceBase?**
   - Yes: Orchestrators need Smart City access and infrastructure
   - Alternative: Compose RealmServiceBase instead of extending?

3. **What orchestrator-specific features are needed?**
   - Business Orchestrator reference ✅
   - Agent initialization helpers ✅
   - Service composition helpers ✅
   - Workflow orchestration patterns ✅
   - Others?

## Recommendation

**Create OrchestratorBase** that extends `RealmServiceBase` and adds orchestrator-specific capabilities. This provides:
- Consistency across all orchestrators
- Clear architectural distinction
- Reusable orchestrator patterns
- Easy migration path






