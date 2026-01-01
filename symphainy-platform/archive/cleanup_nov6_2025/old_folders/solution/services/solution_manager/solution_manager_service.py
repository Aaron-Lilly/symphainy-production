#!/usr/bin/env python3
"""
Solution Manager Service - Clean Micro-Modular Rebuild

Clean micro-modular implementation using base/protocol architecture
with proper infrastructure abstractions for solution orchestration.

WHAT (Manager Role): I orchestrate solutions and coordinate journey flow (Solution → Journey)
HOW (Service Implementation): I use ManagerServiceBase with Public Works abstractions + direct library injection
"""

import logging
from typing import Dict, Any, List, Optional

# Import base and protocol
from bases.manager_service_base import ManagerServiceBase, ManagerServiceType, OrchestrationScope, GovernanceLevel
from bases.protocols.manager_service_protocol import ManagerServiceProtocol

# Import micro-modules
from .modules.initialization import Initialization
from .modules.solution_design import SolutionDesign
from .modules.journey_orchestration import JourneyOrchestration
from .modules.capability_composition import CapabilityComposition
from .modules.platform_governance import PlatformGovernance
from .modules.soa_mcp import SoaMcp
from .modules.utilities import Utilities


class SolutionManagerService(ManagerServiceBase, ManagerServiceProtocol):
    """
    Solution Manager Service - Clean Micro-Modular Rebuild
    
    Clean micro-modular implementation using base/protocol architecture
    with proper infrastructure abstractions for solution orchestration.
    
    WHAT (Manager Role): I orchestrate solutions and coordinate journey flow (Solution → Journey)
    HOW (Service Implementation): I use ManagerServiceBase with Public Works abstractions + direct library injection
    """
    
    def __init__(self, di_container: Any, platform_gateway: Any = None):
        """Initialize Solution Manager Service with proper infrastructure mapping."""
        # Get Platform Gateway from DI Container if not provided
        if platform_gateway is None:
            try:
                platform_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
            except:
                pass  # Will be set later if needed
        
        super().__init__(
            service_name="SolutionManagerService",
            realm_name="solution",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Manager-specific initialization
        self.manager_type = ManagerServiceType.SOLUTION_MANAGER
        self.orchestration_scope = OrchestrationScope.CROSS_DIMENSIONAL
        self.governance_level = GovernanceLevel.STRICT  # Changed from HIGH to STRICT
        
        # Infrastructure Abstractions (Public Works - swappable infrastructure for low-level ops)
        self.session_abstraction = None
        self.state_management_abstraction = None
        self.analytics_abstraction = None  # Optional
        
        # Smart City Services (discovered via Curator for business-level operations)
        self.security_guard = None  # Authentication/Authorization
        self.traffic_cop = None  # Session routing, state sync
        self.conductor = None  # Workflow orchestration
        self.post_office = None  # Structured messaging
        
        # Service State
        self.is_infrastructure_connected = False
        
        # SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # Solution Manager specific state
        self.solution_initiators: Dict[str, Any] = {}
        self.platform_governance: Dict[str, Any] = {}
        
        # Capability flags
        self.platform_orchestration_enabled = False
        self.solution_discovery_enabled = False
        self.cross_solution_coordination_enabled = False
        self.platform_governance_enabled = False
        
        # Initialize micro-modules
        self.initialization_module = Initialization(self)
        self.solution_design_module = SolutionDesign(self)
        self.journey_orchestration_module = JourneyOrchestration(self)
        self.capability_composition_module = CapabilityComposition(self)
        self.platform_governance_module = PlatformGovernance(self)
        self.soa_mcp_module = SoaMcp(self)
        self.utilities_module = Utilities(self)
        
        # Initialize state tracking
        self.is_initialized = False
        
        # Logger is initialized in base class
        if hasattr(self, 'logger') and self.logger:
            self.logger.info("✅ Solution Manager Service (Clean Micro-Modular Rebuild) initialized")
    
    async def initialize(self) -> bool:
        """Initialize Solution Manager Service with infrastructure and libraries."""
        try:
            # Logger is initialized in RealmServiceBase parent class
            if hasattr(self, 'logger') and self.logger:
                self.logger.info("🚀 Initializing Solution Manager Service...")
            
            # Initialize infrastructure connections
            await self.initialization_module.initialize_infrastructure_connections()
            
            # Initialize Solution Manager capabilities
            await self.initialization_module.initialize_solution_manager_capabilities()
            
            # Initialize SOA API exposure
            await self.soa_mcp_module.initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self.soa_mcp_module.initialize_mcp_tool_integration()
            
            # Register with Curator
            await self.soa_mcp_module.register_solution_manager_capabilities()
            
            self.is_initialized = True
            
            if hasattr(self, 'logger') and self.logger:
                self.logger.info("✅ Solution Manager Service initialized successfully")
            
            return True
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"❌ Failed to initialize Solution Manager Service: {str(e)}")
                self.logger.error(f"Traceback: {error_details}")
            # Also print for immediate visibility
            print(f"❌ Solution Manager initialization failed: {str(e)}")
            print(f"Traceback: {error_details}")
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown Solution Manager Service gracefully."""
        try:
            if hasattr(self, 'logger') and self.logger:
                self.logger.info("🛑 Shutting down Solution Manager Service...")
            
            # Clear state
            self.solution_initiators.clear()
            self.platform_governance.clear()
            self.soa_apis.clear()
            self.mcp_tools.clear()
            
            self.is_initialized = False
            
            if hasattr(self, 'logger') and self.logger:
                self.logger.info("✅ Solution Manager Service shutdown complete")
            
            return True
            
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"❌ Error during Solution Manager Service shutdown: {str(e)}")
            return False
    
    # ============================================================================
    # SOA API METHODS (Delegated to Modules)
    # ============================================================================
    
    async def design_solution(self, solution_request: Dict[str, Any]) -> Dict[str, Any]:
        """Design a solution based on requirements (SOA API)."""
        return await self.solution_design_module.design_solution(solution_request)
    
    async def compose_capabilities(self, capability_request: Dict[str, Any]) -> Dict[str, Any]:
        """Compose capabilities from multiple sources (SOA API)."""
        return await self.capability_composition_module.compose_capabilities(capability_request)
    
    async def generate_poc(self, poc_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate proof of concept for a solution (SOA API)."""
        return await self.solution_design_module.generate_poc(poc_request)
    
    async def orchestrate_journey(self, journey_context: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate journey via Journey Manager (SOA API - top-down flow)."""
        return await self.journey_orchestration_module.orchestrate_journey(journey_context)
    
    async def discover_solutions(self) -> Dict[str, Any]:
        """Discover available solutions on the platform (SOA API)."""
        return await self.solution_design_module.discover_solutions()
    
    async def get_platform_health(self) -> Dict[str, Any]:
        """Get overall platform health (SOA API)."""
        return await self.platform_governance_module.get_platform_health()
    
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
            "capabilities_enabled": {
                "platform_orchestration": self.platform_orchestration_enabled,
                "solution_discovery": self.solution_discovery_enabled,
                "cross_solution_coordination": self.cross_solution_coordination_enabled,
                "platform_governance": self.platform_governance_enabled
            },
            "infrastructure": self.utilities_module.validate_infrastructure_mapping()
        }


