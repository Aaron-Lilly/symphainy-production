#!/usr/bin/env python3
"""
Orchestrator Protocol

Clean protocol definition for orchestrator services - contracts only, no implementations.
Aligned with new architecture (Delivery Manager, Curator-based discovery, Experience Foundation).

WHAT (Orchestrator Role): I define the contract for all orchestrator services
HOW (Orchestrator Protocol): I provide type-safe contracts for service composition and orchestration
"""

from typing import Protocol, Dict, Any, Optional, List, runtime_checkable
from datetime import datetime


@runtime_checkable
class OrchestratorProtocol(Protocol):
    """
    Protocol for Orchestrator Services.
    
    Orchestrators compose and coordinate services to deliver use cases.
    They are NOT realm services - they orchestrate realm services.
    
    Architecture:
    - Managed by Delivery Manager (not Business Orchestrator)
    - Discover enabling services via Curator
    - Use Platform Gateway for infrastructure access
    - Use Agentic Foundation for agent creation
    """
    
    # Core Properties
    service_name: str
    realm_name: str
    platform_gateway: Any  # PlatformInfrastructureGateway
    di_container: Any  # DIContainerService
    delivery_manager: Any  # DeliveryManagerService (replaces business_orchestrator)
    orchestrator_name: str
    start_time: datetime
    is_initialized: bool
    orchestrator_health: str
    
    # Lifecycle Methods
    async def initialize(self) -> bool:
        """Initialize the orchestrator service."""
        ...
    
    async def shutdown(self) -> bool:
        """Shutdown the orchestrator service gracefully."""
        ...
    
    # Health and Monitoring
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status."""
        ...
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities and metadata."""
        ...
    
    # Infrastructure Access (via Platform Gateway)
    def get_abstraction(self, abstraction_name: str) -> Any:
        """Get infrastructure abstraction through Platform Gateway."""
        ...
    
    # Foundation Service Access
    async def get_foundation_service(self, service_name: str) -> Optional[Any]:
        """
        Get a foundation service from DI container.
        
        Args:
            service_name: Name of the foundation service
        
        Returns:
            Foundation service instance or None
        """
        ...
    
    # Enabling Service Discovery (via Curator)
    async def get_enabling_service(self, service_name: str) -> Optional[Any]:
        """
        Get enabling service via Curator discovery.
        
        Args:
            service_name: Name of enabling service (e.g., "FileParserService")
        
        Returns:
            Enabling service instance or None
        """
        ...
    
    # Agent Management (via Agentic Foundation)
    async def initialize_agent(
        self,
        agent_class: type,
        agent_name: str,
        agent_type: str = "liaison",
        **kwargs
    ) -> Optional[Any]:
        """
        Initialize an agent using Agentic Foundation factory.
        
        Args:
            agent_class: Agent class to instantiate
            agent_name: Name of the agent
            agent_type: Type of agent ("liaison", "specialist", "guide", etc.)
            **kwargs: Additional agent-specific parameters
        
        Returns:
            Initialized agent or None
        """
        ...
    
    async def get_agent(self, agent_name: str) -> Optional[Any]:
        """
        Get an agent by name (lazy-load if needed).
        
        Args:
            agent_name: Name of the agent
        
        Returns:
            Agent instance or None if not found
        """
        ...
    
    async def discover_agent(self, agent_name: str) -> Optional[Any]:
        """
        Discover an agent via Curator.
        
        Args:
            agent_name: Name of the agent to discover
        
        Returns:
            Agent instance or None if not found
        """
        ...
    
    async def discover_agents(
        self,
        agent_type: Optional[str] = None,
        realm_name: Optional[str] = None,
        orchestrator_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Discover agents via Curator.
        
        Args:
            agent_type: Filter by agent type
            realm_name: Filter by realm name
            orchestrator_name: Filter by orchestrator name
        
        Returns:
            Dictionary with total_agents and agents dict
        """
        ...
    
    # Workflow Orchestration
    async def orchestrate_workflow(
        self,
        workflow_steps: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate a multi-step workflow.
        
        Args:
            workflow_steps: List of workflow steps
            context: Workflow context
        
        Returns:
            Workflow result
        """
        ...
    
    # Curator Registration
    async def register_with_curator(self, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register orchestrator with Curator for service discovery.
        
        Args:
            metadata: Additional metadata for registration
        
        Returns:
            True if registration successful
        """
        ...
    
    # Configuration and Metadata
    def get_configuration(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        ...
    
    def get_service_metadata(self) -> Dict[str, Any]:
        """Get service metadata and information."""
        ...








