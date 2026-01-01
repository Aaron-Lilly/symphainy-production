#!/usr/bin/env python3
"""
Orchestrator Base Class

Base class for orchestrators (use case coordinators).

Orchestrators compose and coordinate services to deliver use cases.
They are NOT realm services - they orchestrate realm services.

WHAT (Orchestrator Role): I orchestrate multiple services to deliver use cases
HOW (Orchestrator): I compose enabling services, Smart City services, and agents

Architecture:
- Composes RealmServiceBase for Smart City access (delegation, not inheritance)
- Adds orchestrator-specific capabilities (Business Orchestrator, agents, composition)
- Clear separation: orchestrators orchestrate, realm services provide capabilities
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC

from bases.realm_service_base import RealmServiceBase
from bases.startup_policy import StartupPolicy


class OrchestratorBase(ABC):
    """
    Base class for orchestrators (use case coordinators).
    
    Orchestrators compose and coordinate services to deliver use cases.
    They are NOT realm services - they orchestrate realm services.
    
    Key Differences from Realm Services:
    - Realm Services: Provide atomic capabilities (SOA APIs) - "I do one thing well"
    - Orchestrators: Compose services for use cases - "I orchestrate multiple services"
    
    Architecture:
    - Composes RealmServiceBase for Smart City access (delegation)
    - Adds orchestrator-specific capabilities
    - Clear separation: orchestrators orchestrate, realm services provide capabilities
    """
    
    # Startup policy: Orchestrators are LAZY by default (loaded by Managers on-demand)
    startup_policy: StartupPolicy = StartupPolicy.LAZY
    
    def __init__(
        self,
        service_name: str,
        realm_name: str,
        platform_gateway: Any,
        di_container: Any,
        delivery_manager: Any = None,
        business_orchestrator: Any = None  # Legacy - kept for backward compatibility during migration
    ):
        """
        Initialize orchestrator base.
        
        Args:
            service_name: Name of the orchestrator service
            realm_name: Realm name (e.g., "business_enablement")
            platform_gateway: Platform Gateway for infrastructure access
            di_container: DI Container for service discovery
            delivery_manager: Delivery Manager reference (for orchestrator management)
            business_orchestrator: Business Orchestrator reference (legacy - for backward compatibility)
        """
        # Core orchestrator properties
        self.service_name = service_name
        self.realm_name = realm_name
        self.platform_gateway = platform_gateway
        self.di_container = di_container
        # Use delivery_manager if provided, otherwise fall back to business_orchestrator (legacy)
        self.delivery_manager = delivery_manager or business_orchestrator
        # Keep business_orchestrator for backward compatibility during migration
        self.business_orchestrator = business_orchestrator or delivery_manager
        self.orchestrator_name = service_name
        self.start_time = datetime.utcnow()
        self.is_initialized = False
        self.orchestrator_health = "unknown"
        
        # Compose RealmServiceBase for Smart City access (delegation, not inheritance)
        # This gives us access to Smart City services, helper methods, and Curator registration
        # without implying orchestrators ARE realm services
        self._realm_service = RealmServiceBase(
            service_name=service_name,
            realm_name=realm_name,
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Use realm service's logger
        self.logger = self._realm_service.logger
        
        # Agents (lazy initialization via Agentic Foundation factory)
        self._agents: Dict[str, Any] = {}  # Track agents by agent_name
        self.liaison_agent = None  # Legacy - will be removed after migration
        self.processing_agent = None  # Legacy - will be removed after migration
        
        # Enabling services (lazy initialization)
        self._enabling_services = {}
        
        self.logger.info(f"🏗️ {self.orchestrator_name} initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize orchestrator.
        
        Subclasses should override this to:
        1. Call super().initialize()
        2. Initialize composed realm service
        3. Get Smart City services (via delegation)
        4. Initialize agents
        5. Register with Curator
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info(f"🚀 Initializing {self.orchestrator_name}...")
            
            # Initialize composed realm service
            realm_init_result = await self._realm_service.initialize()
            if not realm_init_result:
                self.logger.warning("⚠️ Realm service initialization failed, continuing anyway...")
            
            self.is_initialized = True
            self.orchestrator_health = "healthy"
            
            self.logger.info(f"✅ {self.orchestrator_name} initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.orchestrator_name}: {e}")
            self.orchestrator_health = "unhealthy"
            return False
    
    # ========================================================================
    # DELEGATION TO REALM SERVICE (Smart City Access)
    # ========================================================================
    # These methods delegate to the composed RealmServiceBase instance
    # This gives orchestrators access to Smart City services and helper methods
    # without implying orchestrators ARE realm services
    
    async def get_librarian_api(self) -> Optional[Any]:
        """Delegate to RealmServiceBase for Librarian access."""
        return await self._realm_service.get_librarian_api()
    
    async def get_content_steward_api(self) -> Optional[Any]:
        """Delegate to RealmServiceBase for Content Steward access."""
        return await self._realm_service.get_content_steward_api()
    
    async def get_data_steward_api(self) -> Optional[Any]:
        """Delegate to RealmServiceBase for Data Steward access."""
        return await self._realm_service.get_data_steward_api()
    
    async def get_conductor_api(self) -> Optional[Any]:
        """Delegate to RealmServiceBase for Conductor access."""
        return await self._realm_service.get_conductor_api()
    
    async def get_security_guard_api(self) -> Optional[Any]:
        """Delegate to RealmServiceBase for Security Guard access."""
        return await self._realm_service.get_security_guard_api()
    
    async def get_traffic_cop_api(self) -> Optional[Any]:
        """Delegate to RealmServiceBase for Traffic Cop access."""
        return await self._realm_service.get_traffic_cop_api()
    
    async def get_post_office_api(self) -> Optional[Any]:
        """Delegate to RealmServiceBase for Post Office access."""
        return await self._realm_service.get_post_office_api()
    
    async def get_nurse_api(self) -> Optional[Any]:
        """Delegate to RealmServiceBase for Nurse access."""
        return await self._realm_service.get_nurse_api()
    
    async def get_city_manager_api(self) -> Optional[Any]:
        """Delegate to RealmServiceBase for City Manager access."""
        return await self._realm_service.get_city_manager_api()
    
    async def store_document(self, document_data: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate to RealmServiceBase for document storage."""
        return await self._realm_service.store_document(document_data, metadata)
    
    def _get_config_adapter(self) -> Optional[Any]:
        """
        Get ConfigAdapter from PublicWorksFoundationService.
        
        Returns:
            ConfigAdapter instance if available, None otherwise
        """
        try:
            # Try to get PublicWorksFoundationService from DI Container
            if self.di_container and hasattr(self.di_container, 'get_foundation_service'):
                public_works = self.di_container.get_foundation_service("PublicWorksFoundationService")
                if public_works and hasattr(public_works, 'config_adapter'):
                    return public_works.config_adapter
        except Exception as e:
            # Silently fail - fallback to os.getenv() will be used
            pass
        return None
    
    async def track_data_lineage(
        self,
        source: str,
        destination: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Delegate to RealmServiceBase for data lineage tracking."""
        # RealmServiceBase.track_data_lineage expects a dictionary
        lineage_data = {
            "source": source,
            "destination": destination
        }
        if metadata:
            lineage_data.update(metadata)
        return await self._realm_service.track_data_lineage(lineage_data)
    
    async def register_with_curator(
        self,
        capabilities: List[str],
        soa_apis: List[str],
        mcp_tools: List[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Delegate to RealmServiceBase for Curator registration."""
        return await self._realm_service.register_with_curator(
            capabilities=capabilities,
            soa_apis=soa_apis,
            mcp_tools=mcp_tools or [],
            additional_metadata=additional_metadata
        )
    
    def get_abstraction(self, abstraction_name: str) -> Any:
        """Delegate to RealmServiceBase for infrastructure abstraction access."""
        return self._realm_service.get_abstraction(abstraction_name)
    
    # ========================================================================
    # ORCHESTRATOR-SPECIFIC CAPABILITIES
    # ========================================================================
    
    async def get_enabling_service(self, service_name: str) -> Optional[Any]:
        """
        Get enabling service via Curator discovery.
        
        Args:
            service_name: Name of enabling service (e.g., "FileParserService")
        
        Returns:
            Enabling service instance or None
        """
        # Discover enabling service via Curator (new architecture)
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                service = await curator.get_service(service_name)
                if service:
                    return service
        except Exception as e:
            self.logger.debug(f"Curator discovery failed for {service_name}: {e}")
        
        # Fallback: Try legacy Business Orchestrator pattern (for backward compatibility)
        if self.business_orchestrator:
            discovered_services = getattr(self.business_orchestrator, 'discovered_services', {})
            service = discovered_services.get(service_name)
            if service:
                self.logger.debug(f"Found {service_name} via legacy Business Orchestrator pattern")
                return service
        
        self.logger.warning(f"⚠️ Enabling service {service_name} not available via Curator or legacy pattern")
        return None
    
    async def get_foundation_service(self, service_name: str) -> Optional[Any]:
        """
        Get a foundation service from DI container.
        
        Args:
            service_name: Name of the foundation service
        
        Returns:
            Foundation service instance or None
        """
        try:
            return self.di_container.get_foundation_service(service_name)
        except Exception as e:
            self.logger.debug(f"Foundation service {service_name} not available: {e}")
            return None
    
    async def discover_agent(self, agent_name: str) -> Optional[Any]:
        """
        Discover an agent via Curator.
        
        This method allows orchestrators to discover agents that were
        created by other orchestrators or services.
        
        Args:
            agent_name: Name of the agent to discover
        
        Returns:
            Agent instance or None if not found
        """
        try:
            agentic_foundation = await self.get_foundation_service("AgenticFoundationService")
            if not agentic_foundation:
                self.logger.warning(f"⚠️ Agentic Foundation not available for agent discovery: {agent_name}")
                return None
            
            return await agentic_foundation.get_agent_via_curator(agent_name)
            
        except Exception as e:
            self.logger.error(f"Failed to discover agent {agent_name}: {e}")
            return None
    
    async def discover_agents(
        self,
        agent_type: Optional[str] = None,
        realm_name: Optional[str] = None,
        orchestrator_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Discover agents via Curator.
        
        This method allows orchestrators to discover agents that were
        created by other orchestrators or services.
        
        Args:
            agent_type: Filter by agent type ("liaison", "specialist", "guide", etc.)
            realm_name: Filter by realm name
            orchestrator_name: Filter by orchestrator name
        
        Returns:
            Dictionary with total_agents and agents dict
        """
        try:
            agentic_foundation = await self.get_foundation_service("AgenticFoundationService")
            if not agentic_foundation:
                self.logger.warning("⚠️ Agentic Foundation not available for agent discovery")
                return {"total_agents": 0, "agents": {}}
            
            return await agentic_foundation.discover_agents_via_curator(
                agent_type=agent_type,
                realm_name=realm_name,
                orchestrator_name=orchestrator_name
            )
            
        except Exception as e:
            self.logger.error(f"Failed to discover agents: {e}")
            return {"total_agents": 0, "agents": {}}
    
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
        All agents must use full SDK - no backward compatibility.
        
        Args:
            agent_class: Agent class to instantiate
            agent_name: Name of the agent (for logging and tracking)
            agent_type: Type of agent ("liaison", "specialist", "guide", etc.)
            **kwargs: Additional agent-specific parameters (capabilities, required_roles, etc.)
        
        Returns:
            Initialized agent or None
        """
        try:
            # Check if already initialized (lazy loading)
            if agent_name in self._agents:
                self.logger.debug(f"✅ Agent {agent_name} already initialized (lazy cache)")
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
                self.logger.info(f"✅ {agent_name} initialized (lazy, via Agentic Foundation)")
            else:
                self.logger.error(f"❌ Failed to create {agent_name} via Agentic Foundation")
            
            return agent
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {agent_name}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    async def get_agent(self, agent_name: str) -> Optional[Any]:
        """
        Get an agent by name (lazy-load if needed).
        
        This method provides lazy loading - agents are only created when first accessed.
        
        Args:
            agent_name: Name of the agent
        
        Returns:
            Agent instance or None if not found
        """
        # Check if already initialized
        if agent_name in self._agents:
            return self._agents[agent_name]
        
        # Agent not found - cannot lazy-load without agent_class
        # Callers should use initialize_agent() first
        self.logger.warning(f"⚠️ Agent {agent_name} not found - use initialize_agent() to create it")
        return None
    
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
    
    # ========================================================================
    # HEALTH & METADATA (Orchestrator-specific)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for orchestrator."""
        health = {
            "orchestrator": self.orchestrator_name,
            "status": self.orchestrator_health,
            "is_initialized": self.is_initialized,
            "business_orchestrator_available": self.business_orchestrator is not None,
        }
        
        # Check realm service health
        if hasattr(self._realm_service, 'health_check'):
            realm_health = await self._realm_service.health_check()
            health["realm_service_health"] = realm_health
        
        # Check agents
        if self.liaison_agent:
            health["liaison_agent"] = "available"
        if self.processing_agent:
            health["processing_agent"] = "available"
        
        return health
    
    def get_service_capabilities(self) -> Dict[str, Any]:
        """Get orchestrator capabilities."""
        return {
            "orchestrator_name": self.orchestrator_name,
            "realm": self.realm_name,
            "service_type": "orchestrator",
            "capabilities": ["service_composition", "workflow_orchestration", "agent_management"],
            "enabling_services": list(self._enabling_services.keys()),
            "is_initialized": self.is_initialized,
            "orchestrator_health": self.orchestrator_health
        }
    
    async def shutdown(self) -> bool:
        """Shutdown the orchestrator gracefully."""
        try:
            self.logger.info(f"🛑 Shutting down {self.orchestrator_name}...")
            
            # Shutdown realm service
            if hasattr(self._realm_service, 'shutdown'):
                await self._realm_service.shutdown()
            
            # Orchestrator-specific shutdown
            self.is_initialized = False
            self.orchestrator_health = "shutdown"
            
            self.logger.info(f"✅ {self.orchestrator_name} shutdown successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown {self.orchestrator_name}: {e}")
            return False

