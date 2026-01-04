#!/usr/bin/env python3
"""
Insights Manager Service - Clean Micro-Modular Rebuild

Clean micro-modular implementation using base/protocol architecture
with proper infrastructure abstractions for insights orchestration.

WHAT (Manager Role): I orchestrate insights generation and coordinate insights flow (Insights → Business Enablement)
HOW (Service Implementation): I use ManagerServiceBase with Public Works abstractions + direct library injection
"""

import logging
from typing import Dict, Any, Optional

# Import base and protocol
from bases.manager_service_base import ManagerServiceBase, ManagerServiceType, OrchestrationScope, GovernanceLevel
from bases.protocols.manager_service_protocol import ManagerServiceProtocol

# Import micro-modules
from .modules.initialization import Initialization
from .modules.utilities import Utilities
from .modules.soa_mcp import SoaMcp


class InsightsManagerService(ManagerServiceBase, ManagerServiceProtocol):
    """
    Insights Manager Service - Clean Micro-Modular Rebuild
    
    Clean micro-modular implementation using base/protocol architecture
    with proper infrastructure abstractions for insights orchestration.
    
    WHAT (Manager Role): I orchestrate insights generation and coordinate insights flow (Insights → Business Enablement)
    HOW (Service Implementation): I use ManagerServiceBase with Public Works abstractions + direct library injection
    """
    
    def __init__(self, di_container: Any, platform_gateway: Any = None):
        """Initialize Insights Manager Service with proper infrastructure mapping."""
        # Get Platform Gateway from DI Container if not provided
        if platform_gateway is None:
            try:
                platform_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
            except:
                pass  # Will be set later if needed
        
        super().__init__(
            service_name="InsightsManagerService",
            realm_name="insights",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Manager-specific initialization
        self.manager_type = ManagerServiceType.INSIGHTS_MANAGER
        self.orchestration_scope = OrchestrationScope.REALM_ONLY
        self.governance_level = GovernanceLevel.MODERATE
        
        # Infrastructure Abstractions (Public Works - swappable infrastructure for low-level ops)
        self.file_management = None
        self.content_metadata = None
        
        # Smart City Services (discovered via Curator for business-level operations)
        self.librarian = None  # Content metadata management
        self.data_steward = None  # Data operations
        self.data_steward = None  # Content operations
        
        # Service State
        self.is_infrastructure_connected = False
        
        # SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # Insights Manager specific state
        self.insights_orchestrator = None
        
        # Initialize micro-modules
        self.initialization_module = Initialization(self)
        self.soa_mcp_module = SoaMcp(self)
        self.utilities_module = Utilities(self)
        
        # Initialize state tracking
        self.is_initialized = False
        
        # Logger is initialized in base class
        if hasattr(self, 'logger') and self.logger:
            self.logger.info("✅ Insights Manager Service (Clean Micro-Modular Rebuild) initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize Insights Manager Service with infrastructure and libraries.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "insights_manager_initialize_start",
            success=True
        )
        
        try:
            if hasattr(self, 'logger') and self.logger:
                self.logger.info("🚀 Initializing Insights Manager Service...")
            
            # Initialize infrastructure connections
            await self.initialization_module.initialize_infrastructure_connections()
            
            # Initialize Insights Manager capabilities
            await self.initialization_module.initialize_insights_manager_capabilities()
            
            # Discover Insights realm services via Curator
            await self.initialization_module.discover_insights_realm_services()
            
            # Initialize SOA API exposure
            await self.soa_mcp_module.initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self.soa_mcp_module.initialize_mcp_tool_integration()
            
            # Register with Curator (Phase 2 pattern)
            await self.soa_mcp_module.register_insights_manager_capabilities()
            
            self.is_initialized = True
            
            # Record health metric
            await self.record_health_metric(
                "insights_manager_initialized",
                1.0,
                {"service": self.service_name, "orchestrator_available": self.insights_orchestrator is not None}
            )
            
            # Record completion
            await self.log_operation_with_telemetry(
                "insights_manager_initialize_complete",
                success=True,
                details={
                    "service": self.service_name,
                    "orchestrator_available": self.insights_orchestrator is not None
                }
            )
            
            if hasattr(self, 'logger') and self.logger:
                self.logger.info("✅ Insights Manager Service initialized successfully")
            
            return True
            
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"❌ Failed to initialize Insights Manager Service: {str(e)}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Record failure
            await self.log_operation_with_telemetry(
                "insights_manager_initialize_failed",
                success=False,
                details={"error": str(e)}
            )
            
            return False
    
    async def get_insights_orchestrator(self) -> Optional[Any]:
        """
        Get Insights Orchestrator via Curator discovery.
        
        Returns:
            InsightsOrchestrator instance or None if not available
        """
        if self.insights_orchestrator:
            return self.insights_orchestrator
        
        # Try to discover via Curator
        curator = self.get_curator()
        if curator:
            orchestrator = await curator.discover_service_by_name("InsightsOrchestrator")
            if orchestrator:
                self.insights_orchestrator = orchestrator
                return orchestrator
        
        return None
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get Insights Manager service capabilities."""
        return self.utilities_module.get_service_capabilities()

