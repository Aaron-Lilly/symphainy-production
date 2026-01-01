#!/usr/bin/env python3
"""
Content Manager Service - Clean Micro-Modular Rebuild

Clean micro-modular implementation using base/protocol architecture
with proper infrastructure abstractions for content orchestration.

WHAT (Manager Role): I orchestrate content processing and coordinate content flow (Content → Business Enablement)
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


class ContentManagerService(ManagerServiceBase, ManagerServiceProtocol):
    """
    Content Manager Service - Clean Micro-Modular Rebuild
    
    Clean micro-modular implementation using base/protocol architecture
    with proper infrastructure abstractions for content orchestration.
    
    WHAT (Manager Role): I orchestrate content processing and coordinate content flow (Content → Business Enablement)
    HOW (Service Implementation): I use ManagerServiceBase with Public Works abstractions + direct library injection
    """
    
    def __init__(self, di_container: Any, platform_gateway: Any = None):
        """Initialize Content Manager Service with proper infrastructure mapping."""
        # Get Platform Gateway from DI Container if not provided
        if platform_gateway is None:
            try:
                platform_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
            except:
                pass  # Will be set later if needed
        
        super().__init__(
            service_name="ContentManagerService",
            realm_name="content",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Manager-specific initialization
        self.manager_type = ManagerServiceType.CONTENT_MANAGER
        self.orchestration_scope = OrchestrationScope.REALM_ONLY
        self.governance_level = GovernanceLevel.MODERATE
        
        # Infrastructure Abstractions (Public Works - swappable infrastructure for low-level ops)
        self.file_management = None
        self.content_metadata = None
        
        # Smart City Services (discovered via Curator for business-level operations)
        self.librarian = None  # Content metadata management
        self.content_steward = None  # Content operations
        self.data_steward = None  # Data operations
        
        # Service State
        self.is_infrastructure_connected = False
        
        # SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # Content Manager specific state
        self.content_orchestrator = None
        
        # Initialize micro-modules
        self.initialization_module = Initialization(self)
        self.soa_mcp_module = SoaMcp(self)
        self.utilities_module = Utilities(self)
        
        # Initialize state tracking
        self.is_initialized = False
        
        # Logger is initialized in base class
        if hasattr(self, 'logger') and self.logger:
            self.logger.info("✅ Content Manager Service (Clean Micro-Modular Rebuild) initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize Content Manager Service with infrastructure and libraries.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "content_manager_initialize_start",
            success=True
        )
        
        try:
            if hasattr(self, 'logger') and self.logger:
                self.logger.info("🚀 Initializing Content Manager Service...")
            
            # Initialize infrastructure connections
            await self.initialization_module.initialize_infrastructure_connections()
            
            # Initialize Content Manager capabilities
            await self.initialization_module.initialize_content_manager_capabilities()
            
            # Discover Content realm services via Curator
            await self.initialization_module.discover_content_realm_services()
            
            # Initialize SOA API exposure
            await self.soa_mcp_module.initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self.soa_mcp_module.initialize_mcp_tool_integration()
            
            # Register with Curator (Phase 2 pattern)
            await self.soa_mcp_module.register_content_manager_capabilities()
            
            self.is_initialized = True
            
            # Record health metric
            await self.record_health_metric(
                "content_manager_initialized",
                1.0,
                {"service": self.service_name, "orchestrator_available": self.content_orchestrator is not None}
            )
            
            # Record completion
            await self.log_operation_with_telemetry(
                "content_manager_initialize_complete",
                success=True,
                details={
                    "service": self.service_name,
                    "orchestrator_available": self.content_orchestrator is not None
                }
            )
            
            if hasattr(self, 'logger') and self.logger:
                self.logger.info("✅ Content Manager Service initialized successfully")
            
            return True
            
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"❌ Failed to initialize Content Manager Service: {str(e)}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Record failure
            await self.log_operation_with_telemetry(
                "content_manager_initialize_failed",
                success=False,
                details={"error": str(e)}
            )
            
            return False
    
    async def get_content_orchestrator(self) -> Optional[Any]:
        """
        Get Content Orchestrator via Curator discovery.
        
        Returns:
            ContentAnalysisOrchestrator instance or None if not available
        """
        if self.content_orchestrator:
            return self.content_orchestrator
        
        # Try to discover via Curator
        curator = self.get_curator()
        if curator:
            orchestrator = await curator.discover_service_by_name("ContentAnalysisOrchestrator")
            if orchestrator:
                self.content_orchestrator = orchestrator
                return orchestrator
        
        return None
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get Content Manager service capabilities."""
        return self.utilities_module.get_service_capabilities()

