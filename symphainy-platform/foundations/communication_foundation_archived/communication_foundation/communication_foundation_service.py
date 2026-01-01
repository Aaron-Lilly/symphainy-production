#!/usr/bin/env python3
"""
Communication Foundation Service - Unified Communication Infrastructure

Provides unified communication infrastructure for all realms:
- Centralized API Gateway
- SOA Client for inter-realm communication  
- WebSocket infrastructure
- Message queue and event bus

WHAT (Foundation Role): I provide unified communication infrastructure for all realms
HOW (Foundation Implementation): I leverage Public Works abstractions and Curator service discovery
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import foundation base
from bases.foundation_service_base import FoundationServiceBase

# Import Public Works Foundation for infrastructure abstractions
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService

# Import Curator Foundation for service discovery
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService

# Import DI Container for dependency injection
from foundations.di_container.di_container_service import DIContainerService

# Import infrastructure adapters
from .infrastructure_adapters.fastapi_router_manager import FastAPIRouterManager

# Import realm bridges (lazy loading to avoid circular imports)
# from .realm_bridges.solution_bridge import SolutionRealmBridge
# from .realm_bridges.experience_bridge import ExperienceRealmBridge

# Import infrastructure abstractions (to be created)
from .infrastructure_abstractions.communication_abstraction import CommunicationAbstraction
from .infrastructure_abstractions.soa_client_abstraction import SOAClientAbstraction
from .infrastructure_abstractions.websocket_abstraction import WebSocketAbstraction

# Import composition services (to be created)
from .composition_services.communication_composition_service import CommunicationCompositionService
from .composition_services.soa_composition_service import SOACompositionService

# Import infrastructure registry (to be created)
from .infrastructure_registry.communication_registry import CommunicationRegistry

logger = logging.getLogger(__name__)


class CommunicationFoundationService(FoundationServiceBase):
    """
    Communication Foundation Service - Unified Communication Infrastructure
    
    Provides unified communication infrastructure for all realms by leveraging
    existing Public Works abstractions and Curator service discovery.
    
    WHAT (Foundation Role): I provide unified communication infrastructure for all realms
    HOW (Foundation Implementation): I leverage Public Works abstractions and Curator service discovery
    
    Responsibilities:
    - Centralized API Gateway for all API traffic
    - SOA Client for inter-realm communication
    - WebSocket infrastructure for real-time communication
    - Message queue and event bus for asynchronous communication
    - Communication service registry and discovery
    """
    
    def __init__(self, di_container: DIContainerService, 
                 public_works_foundation: PublicWorksFoundationService,
                 curator_foundation: Optional[CuratorFoundationService] = None,
                 security_provider=None,
                 authorization_guard=None,
                 communication_foundation=None):
        """
        Initialize Communication Foundation Service.
        
        Architecture Pattern:
        - Communication Foundation uses Public Works for infrastructure (databases, messaging, etc.)
        - Communication Foundation uses Curator for service discovery and registry
        - Curator is independent and gets its infrastructure from Public Works (not from Communication)
        - If curator_foundation is not provided, it will be obtained from DI Container
        """
        super().__init__(
            service_name="communication_foundation",
            di_container=di_container,
            security_provider=security_provider,
            authorization_guard=authorization_guard
        )
        
        # Store foundation references
        self.public_works_foundation = public_works_foundation
        
        # Get Curator Foundation from DI Container if not provided
        # Curator is initialized by DI Container and is independent of Communication Foundation
        if curator_foundation is None:
            curator_foundation = di_container.get_curator_foundation()
        self.curator_foundation = curator_foundation
        
        self.communication_foundation = communication_foundation
        
        self.logger = logging.getLogger("CommunicationFoundationService")
        
        # Infrastructure adapters
        self.fastapi_router_manager = None
        
        # Foundation services (get from DI Container - not created here)
        self.websocket_foundation = None
        self.messaging_foundation = None
        self.event_bus_foundation = None
        
        # Realm bridges
        self.solution_bridge = None
        self.experience_bridge = None
        self.smart_city_bridge = None
        self.business_enablement_bridge = None
        self.journey_bridge = None
        
        # Infrastructure abstractions
        self.communication_abstraction = None
        self.soa_client_abstraction = None
        self.websocket_abstraction = None
        
        # Composition services
        self.communication_composition_service = None
        self.soa_composition_service = None
        
        # Infrastructure registry
        self.communication_registry = None
        
        # Service state
        self.is_initialized = False
        self.is_running = False
        
        self.logger.info("🏗️ Communication Foundation Service initialized")
    
    async def initialize(self):
        """Initialize Communication Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("initialize_start", success=True)
            
            self.logger.info("🚀 Initializing Communication Foundation Service...")
            
            # Initialize infrastructure adapters
            await self._initialize_infrastructure_adapters()
            
            # Initialize realm bridges
            await self._initialize_realm_bridges()
            
            # Initialize infrastructure abstractions
            await self._initialize_infrastructure_abstractions()
            
            # Initialize composition services
            await self._initialize_composition_services()
            
            # Initialize infrastructure registry
            await self._initialize_infrastructure_registry()
            
            self.is_initialized = True
            self.logger.info("✅ Communication Foundation Service initialized successfully")
            
            # Record success metric
            await self.record_health_metric("initialize_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("initialize_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "initialize")
            self.logger.error(f"❌ Failed to initialize Communication Foundation Service: {e}")
            raise
    
    async def _initialize_infrastructure_adapters(self):
        """Initialize infrastructure foundation services."""
        self.logger.info("🔧 Initializing infrastructure foundation services...")
        
        try:
            # Initialize FastAPI Router Manager (replaces APIGatewayAdapter)
            self.fastapi_router_manager = FastAPIRouterManager()
            await self.fastapi_router_manager.initialize()
            
            # Get Foundation Services from DI Container (not created here)
            try:
                self.websocket_foundation = self.di_container.get_websocket_foundation()
                if self.websocket_foundation and not self.websocket_foundation.is_initialized:
                    await self.websocket_foundation.initialize()
                self.logger.info("✅ WebSocket foundation service obtained")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get WebSocket foundation service: {e}")
                self.websocket_foundation = None
            
            # Get Messaging Foundation Service from DI Container
            try:
                self.messaging_foundation = self.di_container.get_messaging_foundation()
                if self.messaging_foundation and not self.messaging_foundation.is_initialized:
                    await self.messaging_foundation.initialize()
                self.logger.info("✅ Messaging foundation service obtained")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get Messaging foundation service: {e}")
                self.messaging_foundation = None
            
            # Get Event Bus Foundation Service from DI Container
            try:
                self.event_bus_foundation = self.di_container.get_event_bus_foundation()
                if self.event_bus_foundation and not self.event_bus_foundation.is_initialized:
                    await self.event_bus_foundation.initialize()
                self.logger.info("✅ Event Bus foundation service obtained")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get Event Bus foundation service: {e}")
                self.event_bus_foundation = None
            
            self.logger.info("✅ Infrastructure foundation services initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize infrastructure foundation services: {e}")
            raise
    
    async def _initialize_realm_bridges(self):
        """Initialize realm bridges (optional - fails gracefully if services not available)."""
        self.logger.info("🔧 Initializing realm bridges...")
        
        # Initialize bridges as None - will be set if successful
        self.solution_bridge = None
        self.experience_bridge = None
        
        # Try to initialize Solution Bridge
        try:
            # Lazy import to avoid circular imports
            from .realm_bridges.solution_bridge import SolutionRealmBridge
            
            # Initialize Solution Bridge
            self.solution_bridge = SolutionRealmBridge(
                di_container=self.di_container,
                public_works_foundation=self.public_works_foundation,
                curator_foundation=self.curator_foundation
            )
            await self.solution_bridge.initialize()
            
            # Register Solution router with router manager
            solution_router = await self.solution_bridge.get_router()
            await self.fastapi_router_manager.register_realm_router(
                realm="solution",
                router=solution_router,
                metadata={"realm": "solution", "version": "1.0"}
            )
            
            self.logger.info("✅ Solution realm bridge initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️ Solution realm bridge not available (services may not be installed): {e}")
        except Exception as e:
            self.logger.warning(f"⚠️ Solution realm bridge initialization skipped: {e}")
        
        # Try to initialize Experience Foundation Bridge
        try:
            # Lazy import to avoid circular imports
            from .realm_bridges.experience_bridge import ExperienceFoundationBridge
            
            # Initialize Experience Foundation Bridge
            self.experience_foundation_bridge = ExperienceFoundationBridge(
                di_container=self.di_container,
                public_works_foundation=self.public_works_foundation,
                curator_foundation=self.curator_foundation
            )
            await self.experience_foundation_bridge.initialize()
            
            # Register Experience Foundation router with router manager
            experience_router = await self.experience_foundation_bridge.get_router()
            await self.fastapi_router_manager.register_realm_router(
                realm="experience_foundation",  # Updated to reflect Foundation, not Realm
                router=experience_router,
                metadata={"foundation": "experience", "version": "1.0"}
            )
            
            self.logger.info("✅ Experience Foundation bridge initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️ Experience Foundation bridge not available (services may not be installed): {e}")
        except Exception as e:
            self.logger.warning(f"⚠️ Experience Foundation bridge initialization skipped: {e}")
        
        # Try to initialize Smart City Bridge
        try:
            from .realm_bridges.smart_city_bridge import SmartCityRealmBridge
            
            self.smart_city_bridge = SmartCityRealmBridge(
                di_container=self.di_container,
                public_works_foundation=self.public_works_foundation,
                curator_foundation=self.curator_foundation
            )
            await self.smart_city_bridge.initialize()
            
            smart_city_router = await self.smart_city_bridge.get_router()
            await self.fastapi_router_manager.register_realm_router(
                realm="smart_city",
                router=smart_city_router,
                metadata={"realm": "smart_city", "version": "1.0"}
            )
            
            self.logger.info("✅ Smart City realm bridge initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️ Smart City realm bridge not available: {e}")
        except Exception as e:
            self.logger.warning(f"⚠️ Smart City realm bridge initialization skipped: {e}")
        
        # Try to initialize Business Enablement Bridge
        try:
            from .realm_bridges.business_enablement_bridge import BusinessEnablementRealmBridge
            
            self.business_enablement_bridge = BusinessEnablementRealmBridge(
                di_container=self.di_container,
                public_works_foundation=self.public_works_foundation,
                curator_foundation=self.curator_foundation
            )
            await self.business_enablement_bridge.initialize()
            
            be_router = await self.business_enablement_bridge.get_router()
            await self.fastapi_router_manager.register_realm_router(
                realm="business_enablement",
                router=be_router,
                metadata={"realm": "business_enablement", "version": "1.0"}
            )
            
            self.logger.info("✅ Business Enablement realm bridge initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️ Business Enablement realm bridge not available: {e}")
        except Exception as e:
            self.logger.warning(f"⚠️ Business Enablement realm bridge initialization skipped: {e}")
        
        # Try to initialize Journey Bridge
        try:
            from .realm_bridges.journey_bridge import JourneyRealmBridge
            
            self.journey_bridge = JourneyRealmBridge(
                di_container=self.di_container,
                public_works_foundation=self.public_works_foundation,
                curator_foundation=self.curator_foundation
            )
            await self.journey_bridge.initialize()
            
            journey_router = await self.journey_bridge.get_router()
            await self.fastapi_router_manager.register_realm_router(
                realm="journey",
                router=journey_router,
                metadata={"realm": "journey", "version": "1.0"}
            )
            
            self.logger.info("✅ Journey realm bridge initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️ Journey realm bridge not available: {e}")
        except Exception as e:
            self.logger.warning(f"⚠️ Journey realm bridge initialization skipped: {e}")
        
        # Log summary
        bridges_initialized = []
        if self.solution_bridge:
            bridges_initialized.append("solution")
        if self.experience_bridge:
            bridges_initialized.append("experience")
        if self.smart_city_bridge:
            bridges_initialized.append("smart_city")
        if self.business_enablement_bridge:
            bridges_initialized.append("business_enablement")
        if self.journey_bridge:
            bridges_initialized.append("journey")
        
        if bridges_initialized:
            self.logger.info(f"✅ Realm bridges initialized: {', '.join(bridges_initialized)}")
        else:
            self.logger.info("ℹ️ No realm bridges initialized (services may not be available)")
    
    async def _initialize_composition_services(self):
        """Initialize composition services."""
        self.logger.info("🔧 Initializing composition services...")
        
        try:
            # Initialize composition services
            # These would be implemented as needed
            
            self.logger.info("✅ Composition services initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize composition services: {e}")
            raise
    
    async def _initialize_infrastructure_registry(self):
        """Initialize infrastructure registry."""
        self.logger.info("🔧 Initializing infrastructure registry...")
        
        try:
            # Initialize infrastructure registry
            # This would be implemented as needed
            
            self.logger.info("✅ Infrastructure registry initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize infrastructure registry: {e}")
            raise
    
    async def get_unified_router(self):
        """Get the unified router for all realms."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_unified_router_start", success=True)
            
            if not self.fastapi_router_manager:
                raise RuntimeError("FastAPI Router Manager not initialized")
            
            result = self.fastapi_router_manager.get_unified_router()
            
            # Record success metric
            await self.record_health_metric("get_unified_router_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_unified_router_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_unified_router")
            raise
    
    async def shutdown(self):
        """Shutdown Communication Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("shutdown_start", success=True)
            
            self.logger.info("🛑 Shutting down Communication Foundation Service...")
            
            # Shutdown realm bridges
            if self.solution_bridge:
                await self.solution_bridge.shutdown()
            if self.experience_bridge:
                await self.experience_bridge.shutdown()
            if self.smart_city_bridge:
                await self.smart_city_bridge.shutdown()
            if self.business_enablement_bridge:
                await self.business_enablement_bridge.shutdown()
            if self.journey_bridge:
                await self.journey_bridge.shutdown()
            
            # Shutdown infrastructure adapters
            if self.fastapi_router_manager:
                await self.fastapi_router_manager.shutdown()
            
            self.is_initialized = False
            self.is_running = False
            
            self.logger.info("✅ Communication Foundation Service shutdown completed")
            
            # Record success metric
            await self.record_health_metric("shutdown_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("shutdown_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "shutdown")
            self.logger.error(f"❌ Failed to shutdown Communication Foundation Service: {e}")
            raise
    
    async def _initialize_infrastructure_abstractions(self):
        """Initialize infrastructure abstractions."""
        self.logger.info("🔧 Initializing infrastructure abstractions...")
        
        try:
            # Initialize Communication abstraction (if adapters are available)
            # Note: Communication abstraction can be initialized without API Gateway Adapter
            # as it's primarily for inter-realm communication, not external API routing
            if self.websocket_foundation or self.messaging_foundation or self.event_bus_foundation:
                self.communication_abstraction = CommunicationAbstraction(
                    api_gateway_adapter=None,  # No longer using APIGatewayAdapter
                    websocket_foundation=self.websocket_foundation,
                    messaging_foundation=self.messaging_foundation,
                    event_bus_foundation=self.event_bus_foundation
                )
                await self.communication_abstraction.initialize()
            else:
                self.logger.warning("⚠️ Communication adapters not available, skipping communication abstraction")
            
            # Initialize SOA Client abstraction (if communication abstraction is available)
            if self.communication_abstraction:
                self.soa_client_abstraction = SOAClientAbstraction(
                    di_container=self.di_container,
                    curator_foundation=self.curator_foundation,
                    communication_abstraction=self.communication_abstraction
                )
                await self.soa_client_abstraction.initialize()
            else:
                self.logger.warning("⚠️ Communication abstraction not available, skipping SOA Client abstraction")
            
            # Initialize WebSocket abstraction (if communication abstraction is available)
            if self.communication_abstraction:
                self.websocket_abstraction = WebSocketAbstraction(
                    websocket_foundation=self.websocket_foundation,
                    communication_abstraction=self.communication_abstraction
                )
                await self.websocket_abstraction.initialize()
            else:
                self.logger.warning("⚠️ Communication abstraction not available, skipping WebSocket abstraction")
            
            self.logger.info("✅ Infrastructure abstractions initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize infrastructure abstractions: {e}")
            raise
    
    async def _initialize_composition_services(self):
        """Initialize composition services."""
        self.logger.info("🔧 Initializing composition services...")
        
        try:
            # Initialize Communication composition service (if abstractions are available)
            if self.communication_abstraction:
                self.communication_composition_service = CommunicationCompositionService(
                    communication_abstraction=self.communication_abstraction,
                    soa_client_abstraction=self.soa_client_abstraction,
                    websocket_abstraction=self.websocket_abstraction
                )
                await self.communication_composition_service.initialize()
            else:
                self.logger.warning("⚠️ Communication abstraction not available, skipping composition service")
            
            # Initialize SOA composition service (if SOA client abstraction is available)
            if self.soa_client_abstraction:
                self.soa_composition_service = SOACompositionService(
                    soa_client_abstraction=self.soa_client_abstraction,
                    curator_foundation=self.curator_foundation
                )
                await self.soa_composition_service.initialize()
            else:
                self.logger.warning("⚠️ SOA Client abstraction not available, skipping SOA composition service")
            
            self.logger.info("✅ Composition services initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize composition services: {e}")
            raise
    
    async def _initialize_infrastructure_registry(self):
        """Initialize infrastructure registry."""
        self.logger.info("🔧 Initializing infrastructure registry...")
        
        # Initialize Communication registry
        self.communication_registry = CommunicationRegistry(
            communication_abstraction=self.communication_abstraction,
            soa_client_abstraction=self.soa_client_abstraction,
            websocket_abstraction=self.websocket_abstraction
        )
        await self.communication_registry.initialize()
        
        self.logger.info("✅ Infrastructure registry initialized")
    
    async def _register_with_di_container(self):
        """Register Communication Foundation with DI Container."""
        self.logger.info("🔧 Registering with DI Container...")
        
        # Register Communication Foundation service
        self.di_container.register_service(
            service_name="communication_foundation",
            service_instance=self
        )
        
        # Register communication abstractions
        self.di_container.register_service(
            service_name="communication_abstraction",
            service_instance=self.communication_abstraction
        )
        
        self.di_container.register_service(
            service_name="soa_client_abstraction",
            service_instance=self.soa_client_abstraction
        )
        
        self.di_container.register_service(
            service_name="websocket_abstraction",
            service_instance=self.websocket_abstraction
        )
        
        self.logger.info("✅ Registered with DI Container")
    
    async def start(self):
        """Start Communication Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("start_start", success=True)
            
            if not self.is_initialized:
                await self.initialize()
            
            self.logger.info("🚀 Starting Communication Foundation Service...")
            
            # Start infrastructure adapters
            if self.websocket_foundation:
                await self.websocket_foundation.start()
            if self.messaging_foundation:
                await self.messaging_foundation.start()
            if self.event_bus_foundation:
                await self.event_bus_foundation.start()
            
            # Start infrastructure abstractions
            if self.communication_abstraction:
                await self.communication_abstraction.start()
            if self.soa_client_abstraction:
                await self.soa_client_abstraction.start()
            if self.websocket_abstraction:
                await self.websocket_abstraction.start()
            
            # Start composition services
            if self.communication_composition_service:
                await self.communication_composition_service.start()
            if self.soa_composition_service:
                await self.soa_composition_service.start()
            
            # Start infrastructure registry
            if self.communication_registry:
                await self.communication_registry.start()
            
            self.is_running = True
            self.logger.info("✅ Communication Foundation Service started successfully")
            
            # Record success metric
            await self.record_health_metric("start_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("start_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "start")
            self.logger.error(f"❌ Failed to start Communication Foundation Service: {e}")
            raise
    
    async def stop(self):
        """Stop Communication Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("stop_start", success=True)
            
            self.logger.info("🛑 Stopping Communication Foundation Service...")
            
            # Stop infrastructure registry
            if self.communication_registry:
                await self.communication_registry.stop()
            
            # Stop composition services
            if self.soa_composition_service:
                await self.soa_composition_service.stop()
            if self.communication_composition_service:
                await self.communication_composition_service.stop()
            
            # Stop infrastructure abstractions
            if self.websocket_abstraction:
                await self.websocket_abstraction.stop()
            if self.soa_client_abstraction:
                await self.soa_client_abstraction.stop()
            if self.communication_abstraction:
                await self.communication_abstraction.stop()
            
            # Stop infrastructure adapters
            if self.event_bus_foundation:
                await self.event_bus_foundation.stop()
            if self.messaging_foundation:
                await self.messaging_foundation.stop()
            if self.websocket_foundation:
                await self.websocket_foundation.stop()
            
            self.is_running = False
            self.logger.info("✅ Communication Foundation Service stopped successfully")
            
            # Record success metric
            await self.record_health_metric("stop_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("stop_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "stop")
            self.logger.error(f"❌ Failed to stop Communication Foundation Service: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown Communication Foundation Service (duplicate - keeping for compatibility)."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("shutdown_start", success=True)
            
            self.logger.info("🛑 Shutting down Communication Foundation Service...")
            
            # Shutdown all components
            if self.communication_composition_service:
                await self.communication_composition_service.shutdown()
            
            if self.soa_composition_service:
                await self.soa_composition_service.shutdown()
            
            if self.communication_registry:
                await self.communication_registry.shutdown()
            
            # Shutdown infrastructure adapters
            if self.websocket_foundation:
                await self.websocket_foundation.shutdown()
            
            if self.messaging_foundation:
                await self.messaging_foundation.shutdown()
            
            if self.event_bus_foundation:
                await self.event_bus_foundation.shutdown()
            
            self.is_initialized = False
            self.is_running = False
            
            self.logger.info("✅ Communication Foundation Service shutdown complete")
            
            # Record success metric
            await self.record_health_metric("shutdown_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("shutdown_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "shutdown")
            self.logger.error(f"❌ Error during Communication Foundation Service shutdown: {e}")
    
    
    # Public API methods for realms to use
    
    async def get_api_gateway(self):
        """Get API Gateway for external API routing."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_api_gateway_start", success=True)
            
            result = self.communication_abstraction
            
            # Record success metric
            await self.record_health_metric("get_api_gateway_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_api_gateway_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_api_gateway")
            raise
    
    async def get_soa_client(self):
        """Get SOA Client for inter-realm communication."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_soa_client_start", success=True)
            
            result = self.soa_client_abstraction
            
            # Record success metric
            await self.record_health_metric("get_soa_client_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_soa_client_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_soa_client")
            raise
    
    async def get_websocket_manager(self):
        """Get WebSocket manager for real-time communication."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_websocket_manager_start", success=True)
            
            result = self.websocket_abstraction
            
            # Record success metric
            await self.record_health_metric("get_websocket_manager_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_websocket_manager_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_websocket_manager")
            raise
    
    async def get_messaging_service(self):
        """Get messaging service for asynchronous communication."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_messaging_service_start", success=True)
            
            result = self.communication_abstraction
            
            # Record success metric
            await self.record_health_metric("get_messaging_service_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_messaging_service_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_messaging_service")
            raise
    
    async def get_event_bus(self):
        """Get event bus for event-driven communication."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_event_bus_start", success=True)
            
            result = self.communication_abstraction
            
            # Record success metric
            await self.record_health_metric("get_event_bus_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_event_bus_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_event_bus")
            raise
    
    async def register_soa_api(self, service_name: str, api_endpoints: Dict[str, Any], user_context: Dict[str, Any] = None):
        """Register SOA API endpoints with Curator Foundation."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_soa_api_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "soa_api_registry", "write"):
                        await self.record_health_metric("register_soa_api_access_denied", 1.0, {"service_name": service_name})
                        await self.log_operation_with_telemetry("register_soa_api_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_soa_api_tenant_denied", 1.0, {"service_name": service_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("register_soa_api_complete", success=False)
                            return False
            
            if self.curator_foundation:
                await self.curator_foundation.register_soa_api(service_name, api_endpoints)
            
            # Record success metric
            await self.record_health_metric("register_soa_api_success", 1.0, {"service_name": service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_soa_api_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_soa_api")
            self.logger.error(f"❌ Failed to register SOA API {service_name}: {e}")
            return False
    
    async def discover_soa_api(self, service_name: str, user_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Discover SOA API endpoints via Curator Foundation."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("discover_soa_api_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "soa_api_registry", "read"):
                        await self.record_health_metric("discover_soa_api_access_denied", 1.0, {"service_name": service_name})
                        await self.log_operation_with_telemetry("discover_soa_api_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("discover_soa_api_tenant_denied", 1.0, {"service_name": service_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("discover_soa_api_complete", success=False)
                            return None
            
            result = None
            if self.curator_foundation:
                result = await self.curator_foundation.discover_soa_api(service_name)
            
            # Record success metric
            await self.record_health_metric("discover_soa_api_success", 1.0, {"service_name": service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("discover_soa_api_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "discover_soa_api")
            self.logger.error(f"❌ Failed to discover SOA API {service_name}: {e}")
            return None
    
    async def send_message(self, target_realm: str, message_type: str, message_data: Dict[str, Any], user_context: Dict[str, Any] = None):
        """Send message to target realm."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("send_message_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, f"realm_{target_realm}", "write"):
                        await self.record_health_metric("send_message_access_denied", 1.0, {"target_realm": target_realm, "message_type": message_type})
                        await self.log_operation_with_telemetry("send_message_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("send_message_tenant_denied", 1.0, {"target_realm": target_realm, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("send_message_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            result = await self.communication_abstraction.send_message(
                target_realm=target_realm,
                message_type=message_type,
                message_data=message_data
            )
            
            # Record success metric
            await self.record_health_metric("send_message_success", 1.0, {"target_realm": target_realm, "message_type": message_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("send_message_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "send_message")
            self.logger.error(f"❌ Failed to send message to {target_realm}: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    async def publish_event(self, event_type: str, event_data: Dict[str, Any], user_context: Dict[str, Any] = None):
        """Publish event to event bus."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("publish_event_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "event_bus", "write"):
                        await self.record_health_metric("publish_event_access_denied", 1.0, {"event_type": event_type})
                        await self.log_operation_with_telemetry("publish_event_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("publish_event_tenant_denied", 1.0, {"event_type": event_type, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("publish_event_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            result = await self.communication_abstraction.publish_event(
                event_type=event_type,
                event_data=event_data
            )
            
            # Record success metric
            await self.record_health_metric("publish_event_success", 1.0, {"event_type": event_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("publish_event_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "publish_event")
            self.logger.error(f"❌ Failed to publish event {event_type}: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    async def establish_websocket_connection(self, client_id: str, realm: str, user_context: Dict[str, Any] = None):
        """Establish WebSocket connection for real-time communication."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("establish_websocket_connection_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, f"realm_{realm}", "read"):
                        await self.record_health_metric("establish_websocket_connection_access_denied", 1.0, {"client_id": client_id, "realm": realm})
                        await self.log_operation_with_telemetry("establish_websocket_connection_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("establish_websocket_connection_tenant_denied", 1.0, {"client_id": client_id, "realm": realm, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("establish_websocket_connection_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            result = await self.websocket_abstraction.establish_connection(
                client_id=client_id,
                realm=realm
            )
            
            # Record success metric
            await self.record_health_metric("establish_websocket_connection_success", 1.0, {"client_id": client_id, "realm": realm})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("establish_websocket_connection_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "establish_websocket_connection")
            self.logger.error(f"❌ Failed to establish WebSocket connection for {client_id}: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
