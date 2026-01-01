#!/usr/bin/env python3
"""
Journey Manager Service - Clean Micro-Modular Rebuild

Clean micro-modular implementation using base/protocol architecture
with proper infrastructure abstractions for journey orchestration.

WHAT (Manager Role): I orchestrate journeys and coordinate experience flow (Journey → Experience)
HOW (Service Implementation): I use ManagerServiceBase with Public Works abstractions + direct library injection
"""

import logging
from typing import Dict, Any, Optional

# Import base and protocol
from bases.manager_service_base import ManagerServiceBase, ManagerServiceType, OrchestrationScope, GovernanceLevel
from bases.protocols.manager_service_protocol import ManagerServiceProtocol

# Import micro-modules
from .modules.initialization import Initialization
from .modules.journey_design import JourneyDesign
from .modules.experience_orchestration import ExperienceOrchestration
from .modules.roadmap_management import RoadmapManagement
from .modules.soa_mcp import SoaMcp
from .modules.utilities import Utilities


class JourneyManagerService(ManagerServiceBase, ManagerServiceProtocol):
    """
    Journey Manager Service - Clean Micro-Modular Rebuild
    
    Clean micro-modular implementation using base/protocol architecture
    with proper infrastructure abstractions for journey orchestration.
    
    WHAT (Manager Role): I orchestrate journeys and coordinate experience flow (Journey → Experience)
    HOW (Service Implementation): I use ManagerServiceBase with Public Works abstractions + direct library injection
    """
    
    def __init__(self, di_container: Any, platform_gateway: Any = None):
        """Initialize Journey Manager Service with proper infrastructure mapping."""
        # Get Platform Gateway from DI Container if not provided
        if platform_gateway is None:
            try:
                platform_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
            except:
                pass  # Will be set later if needed
        
        super().__init__(
            service_name="JourneyManagerService",
            realm_name="journey",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Manager-specific initialization
        self.manager_type = ManagerServiceType.JOURNEY_MANAGER
        self.orchestration_scope = OrchestrationScope.CROSS_DIMENSIONAL
        self.governance_level = GovernanceLevel.MODERATE
        
        # Infrastructure Abstractions (Public Works - swappable infrastructure for low-level ops)
        self.session_abstraction = None
        self.state_management_abstraction = None
        
        # Smart City Services (discovered via Curator for business-level operations)
        self.traffic_cop = None  # Session routing, state sync
        self.conductor = None  # Workflow orchestration
        self.post_office = None  # Structured messaging
        
        # Service State
        self.is_infrastructure_connected = False
        
        # SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # Journey Manager specific state
        self.journey_services: Dict[str, Any] = {}
        self.journey_templates: Dict[str, Any] = {}
        self.active_journeys: Dict[str, Any] = {}
        
        # Initialize micro-modules
        self.initialization_module = Initialization(self)
        self.journey_design_module = JourneyDesign(self)
        self.experience_orchestration_module = ExperienceOrchestration(self)
        self.roadmap_management_module = RoadmapManagement(self)
        self.soa_mcp_module = SoaMcp(self)
        self.utilities_module = Utilities(self)
        
        # Initialize state tracking
        self.is_initialized = False
        
        # Logger is initialized in base class
        if hasattr(self, 'logger') and self.logger:
            self.logger.info("✅ Journey Manager Service (Clean Micro-Modular Rebuild) initialized")
    
    async def initialize(self) -> bool:
        """Initialize Journey Manager Service with infrastructure and libraries."""
        try:
            if hasattr(self, 'logger') and self.logger:
                self.logger.info("🚀 Initializing Journey Manager Service...")
            
            # Initialize infrastructure connections
            await self.initialization_module.initialize_infrastructure_connections()
            
            # Initialize Journey Manager capabilities
            await self.initialization_module.initialize_journey_manager_capabilities()
            
            # Initialize SOA API exposure
            await self.soa_mcp_module.initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self.soa_mcp_module.initialize_mcp_tool_integration()
            
            # Register with Curator
            await self.soa_mcp_module.register_journey_manager_capabilities()
            
            self.is_initialized = True
            
            if hasattr(self, 'logger') and self.logger:
                self.logger.info("✅ Journey Manager Service initialized successfully")
            
            return True
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"❌ Failed to initialize Journey Manager Service: {str(e)}")
                self.logger.error(f"Traceback: {error_details}")
            # Also print for immediate visibility
            print(f"❌ Journey Manager initialization failed: {str(e)}")
            print(f"Traceback: {error_details}")
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown Journey Manager Service gracefully."""
        try:
            if self.logger:
                self.logger.info("🛑 Shutting down Journey Manager Service...")
            
            # Clear state
            self.journey_services.clear()
            self.journey_templates.clear()
            self.active_journeys.clear()
            self.soa_apis.clear()
            self.mcp_tools.clear()
            
            self.is_initialized = False
            
            if self.logger:
                self.logger.info("✅ Journey Manager Service shutdown complete")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error during Journey Manager Service shutdown: {str(e)}")
            return False
    
    # ============================================================================
    # SOA API METHODS (Delegated to Modules)
    # ============================================================================
    
    async def design_journey(self, journey_request: Dict[str, Any]) -> Dict[str, Any]:
        """Design a journey based on requirements (SOA API)."""
        return await self.journey_design_module.design_journey(journey_request)
    
    async def create_roadmap(self, roadmap_request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a roadmap for a journey (SOA API)."""
        return await self.roadmap_management_module.create_roadmap(roadmap_request)
    
    async def track_milestones(self, tracking_request: Dict[str, Any]) -> Dict[str, Any]:
        """Track milestones for a journey (SOA API)."""
        return await self.roadmap_management_module.track_milestones(tracking_request)
    
    async def orchestrate_experience(self, experience_context: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate experience via Experience Manager (SOA API - top-down flow)."""
        return await self.experience_orchestration_module.orchestrate_experience(experience_context)
    
    # ============================================================================
    # PROTOCOL COMPLIANCE METHODS
    # ============================================================================
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (ManagerServiceProtocol)."""
        return self.utilities_module.get_service_capabilities()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check (ManagerServiceProtocol)."""
        return {
            "service_name": self.service_name,
            "status": "healthy" if self.is_initialized else "unhealthy",
            "is_infrastructure_connected": self.is_infrastructure_connected,
            "active_journeys": len(self.active_journeys),
            "infrastructure": self.utilities_module.validate_infrastructure_mapping()
        }


