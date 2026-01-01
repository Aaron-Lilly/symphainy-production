#!/usr/bin/env python3
"""
Experience Manager Service - Clean Micro-Modular Rebuild

Clean micro-modular implementation using base/protocol architecture
with proper infrastructure abstractions for experience orchestration.

WHAT (Manager Role): I orchestrate experiences and coordinate delivery flow (Experience → Delivery)
HOW (Service Implementation): I use ManagerServiceBase with Public Works abstractions + direct library injection
"""

import logging
from typing import Dict, Any, Optional

# Import base and protocol
from bases.manager_service_base import ManagerServiceBase, ManagerServiceType, OrchestrationScope, GovernanceLevel
from bases.protocols.manager_service_protocol import ManagerServiceProtocol

# Import micro-modules
from .modules.initialization import Initialization
from .modules.experience_coordination import ExperienceCoordination
from .modules.delivery_orchestration import DeliveryOrchestration
from .modules.soa_mcp import SoaMcp
from .modules.utilities import Utilities


class ExperienceManagerService(ManagerServiceBase, ManagerServiceProtocol):
    """
    Experience Manager Service - Clean Micro-Modular Rebuild
    
    Clean micro-modular implementation using base/protocol architecture
    with proper infrastructure abstractions for experience orchestration.
    
    WHAT (Manager Role): I orchestrate experiences and coordinate delivery flow (Experience → Delivery)
    HOW (Service Implementation): I use ManagerServiceBase with Public Works abstractions + direct library injection
    """
    
    def __init__(self, di_container: Any, platform_gateway: Any = None):
        """Initialize Experience Manager Service with proper infrastructure mapping."""
        # Get Platform Gateway from DI Container if not provided
        if platform_gateway is None:
            try:
                platform_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
            except:
                pass  # Will be set later if needed
        
        super().__init__(
            service_name="ExperienceManagerService",
            realm_name="experience",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Manager-specific initialization
        self.manager_type = ManagerServiceType.EXPERIENCE_MANAGER
        self.orchestration_scope = OrchestrationScope.CROSS_DIMENSIONAL
        self.governance_level = GovernanceLevel.MODERATE
        
        # Infrastructure Abstractions (Public Works - swappable infrastructure for low-level ops)
        self.session_abstraction = None
        self.state_management_abstraction = None
        
        # Smart City Services (discovered via Curator for business-level operations)
        self.security_guard = None  # Authentication/Authorization
        self.traffic_cop = None  # Session routing, UI state sync
        self.post_office = None  # Real-time messaging
        
        # Service State
        self.is_infrastructure_connected = False
        
        # SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # Experience Manager specific state
        self.experience_services: Dict[str, Any] = {}
        self.gateway_services: Dict[str, Any] = {}
        
        # Initialize micro-modules
        self.initialization_module = Initialization(self)
        self.experience_coordination_module = ExperienceCoordination(self)
        self.delivery_orchestration_module = DeliveryOrchestration(self)
        self.soa_mcp_module = SoaMcp(self)
        self.utilities_module = Utilities(self)
        
        # Logger is initialized in base class
        if hasattr(self, 'logger') and self.logger:
            self.logger.info("✅ Experience Manager Service (Clean Micro-Modular Rebuild) initialized")
    
    async def initialize(self) -> bool:
        """Initialize Experience Manager Service with infrastructure and libraries."""
        try:
            if hasattr(self, "logger") and self.logger:
                self.logger.info("🚀 Initializing Experience Manager Service...")
            
            # Initialize infrastructure connections
            await self.initialization_module.initialize_infrastructure_connections()
            
            # Initialize Experience Manager capabilities
            await self.initialization_module.initialize_experience_manager_capabilities()
            
            # Discover Experience realm services via Curator
            await self.initialization_module.discover_experience_realm_services()
            
            # Initialize SOA API exposure
            await self.soa_mcp_module.initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self.soa_mcp_module.initialize_mcp_tool_integration()
            
            # Register with Curator
            await self.soa_mcp_module.register_experience_manager_capabilities()
            
            self.is_initialized = True
            
            if hasattr(self, "logger") and self.logger:
                self.logger.info("✅ Experience Manager Service initialized successfully")
            
            return True
            
        except Exception as e:
            if hasattr(self, "logger") and self.logger:
                self.logger.error(f"❌ Failed to initialize Experience Manager Service: {str(e)}")
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown Experience Manager Service gracefully."""
        try:
            if hasattr(self, "logger") and self.logger:
                self.logger.info("🛑 Shutting down Experience Manager Service...")
            
            # Clear state
            self.experience_services.clear()
            self.gateway_services.clear()
            self.soa_apis.clear()
            self.mcp_tools.clear()
            
            self.is_initialized = False
            
            if hasattr(self, "logger") and self.logger:
                self.logger.info("✅ Experience Manager Service shutdown complete")
            
            return True
            
        except Exception as e:
            if hasattr(self, "logger") and self.logger:
                self.logger.error(f"❌ Error during Experience Manager Service shutdown: {str(e)}")
            return False
    
    # ============================================================================
    # SOA API METHODS (Delegated to Modules)
    # ============================================================================
    
    async def coordinate_experience(self, experience_request: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate experience services for user interactions (SOA API)."""
        return await self.experience_coordination_module.coordinate_experience(experience_request)
    
    async def expose_apis(self, api_request: Dict[str, Any]) -> Dict[str, Any]:
        """Expose APIs for frontend and external systems (SOA API)."""
        return await self.experience_coordination_module.expose_apis(api_request)
    
    async def manage_sessions(self, session_request: Dict[str, Any]) -> Dict[str, Any]:
        """Manage user sessions (SOA API)."""
        return await self.experience_coordination_module.manage_sessions(session_request)
    
    async def orchestrate_delivery(self, delivery_context: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate delivery via Delivery Manager (SOA API - top-down flow)."""
        return await self.delivery_orchestration_module.orchestrate_delivery(delivery_context)
    
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
            "experience_services": len(self.experience_services),
            "infrastructure": self.utilities_module.validate_infrastructure_mapping()
        }
    
    async def get_business_orchestrator(self) -> Optional[Any]:
        """
        Get Business Orchestrator via Delivery Manager.
        
        This method is used by micro-modules (like FrontendRouterModule) to access
        Business Orchestrator for routing to pillar orchestrators.
        """
        try:
            # Get Delivery Manager (which contains Business Orchestrator)
            delivery_manager = await self.get_manager("delivery_manager")
            if not delivery_manager:
                if hasattr(self, 'logger') and self.logger:
                    self.logger.warning("⚠️ Delivery Manager not available - cannot get Business Orchestrator")
                return None
            
            # Get Business Orchestrator from Delivery Manager
            if hasattr(delivery_manager, 'get_business_orchestrator'):
                business_orchestrator = await delivery_manager.get_business_orchestrator()
                if business_orchestrator:
                    if hasattr(self, 'logger') and self.logger:
                        self.logger.debug("✅ Retrieved Business Orchestrator from Delivery Manager")
                    return business_orchestrator
            
            # Fallback: Check if stored directly
            if hasattr(delivery_manager, 'business_orchestrator') and delivery_manager.business_orchestrator:
                if hasattr(self, 'logger') and self.logger:
                    self.logger.debug("✅ Retrieved Business Orchestrator from Delivery Manager (direct)")
                return delivery_manager.business_orchestrator
            
            return None
            
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"❌ Failed to get Business Orchestrator: {e}")
            return None


