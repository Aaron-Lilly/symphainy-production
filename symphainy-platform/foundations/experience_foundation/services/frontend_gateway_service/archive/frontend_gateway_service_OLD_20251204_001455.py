#!/usr/bin/env python3
"""
REST API Gateway Service (via Experience Foundation SDK)

Routes REST API requests to Business Enablement orchestrators.
This is the REST API experience implementation - any client can consume these APIs.

symphainy-frontend is one client consuming these REST APIs (MVP implementation).
Other clients (mobile, CLI, API clients) can consume the same REST APIs.

WHAT: Routes REST API requests to Business Enablement orchestrators
HOW: Discovers orchestrators via Curator, uses APIRoutingUtility for route execution, integrates with Curator for route discovery
"""

import os
import sys
import uuid
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../'))

from bases.realm_service_base import RealmServiceBase


class APIEndpointType(Enum):
    """Types of API endpoints."""
    REST = "rest"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"


class FrontendGatewayService(RealmServiceBase):
    """
    REST API Gateway Service (via Experience Foundation SDK)
    
    Routes REST API requests to Business Enablement orchestrators.
    This is the REST API experience implementation - any client can consume these APIs.
    
    symphainy-frontend is one client consuming these REST APIs (MVP implementation).
    Other clients (mobile, CLI, API clients) can consume the same REST APIs.
    
    WHAT: Routes REST API requests to Business Enablement orchestrators
    HOW: Discovers orchestrators via Curator, uses APIRoutingUtility for route execution, integrates with Curator for route discovery
    
    Composes:
    - ContentAnalysisOrchestrator → /api/v1/content-pillar/*
    - InsightsOrchestrator → /api/v1/insights-pillar/*
    - OperationsOrchestrator → /api/v1/operations-pillar/*
    - BusinessOutcomesOrchestrator → /api/v1/business-outcomes-pillar/*
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Frontend Gateway Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.librarian = None
        self.security_guard = None
        self.traffic_cop = None
        
        # Business Enablement orchestrators (discovered via Curator)
        self.content_orchestrator = None
        self.insights_orchestrator = None
        self.operations_orchestrator = None
        self.data_operations_orchestrator = None
        self.business_outcomes_orchestrator = None
        
        # Orchestrators dictionary (for dictionary-style access)
        self.orchestrators: Dict[str, Any] = {}
        
        # Chat Service (discovered via Curator)
        self.chat_service = None
        
        # API registry
        self.registered_apis: Dict[str, Dict[str, Any]] = {}
        
        # Supported endpoint types
        self.supported_types = [t.value for t in APIEndpointType]
        
        # Get APIRoutingUtility for route execution (will be initialized in initialize())
        self.api_router = None
        
        # ⭐ NEW: Feature flag for discovered routing (parallel implementation)
        # When False: Use existing hardcoded routing (current behavior)
        # When True: Use route discovery from Curator (new behavior)
        try:
            from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager
            from utilities.path_utils import get_project_root
            project_root = get_project_root()
            config = UnifiedConfigurationManager(
                service_name="frontend_gateway",
                config_root=str(project_root)
            )
            self.use_discovered_routing = config.get("routing.use_discovered_routing", False)
            self.routing_monitoring_enabled = config.get("routing.monitoring.enabled", True)
        except Exception as e:
            # Fallback if config not available
            self.use_discovered_routing = False
            self.routing_monitoring_enabled = False
            self.logger.warning(f"⚠️ Failed to load routing config: {e}, using defaults")
        
        # Route registry for discovered routes (new approach)
        self.discovered_routes: Dict[str, Dict[str, Any]] = {}
        
        # ⭐ NEW: Routing metrics for monitoring (Phase 4)
        self.routing_metrics: Dict[str, Any] = {
            "old_routing": {
                "requests": 0,
                "successes": 0,
                "errors": 0,
                "total_time_ms": 0.0,
                "avg_time_ms": 0.0
            },
            "new_routing": {
                "requests": 0,
                "successes": 0,
                "errors": 0,
                "total_time_ms": 0.0,
                "avg_time_ms": 0.0,
                "fallbacks": 0
            },
            "last_reset": datetime.utcnow().isoformat()
        }
    
    async def _ensure_city_manager_available(self):
        """
        Ensure City Manager is available (lazy bootstrap if needed).
        
        City Manager is the bootstrap pattern to activate realm services.
        Frontend Gateway needs City Manager to access Smart City services.
        If City Manager isn't available, we bootstrap it here.
        """
        try:
            # Check if City Manager is already available
            city_manager = None
            
            # Try DI container first
            try:
                city_manager = self.di_container.get_foundation_service("CityManagerService")
            except Exception:
                pass
            
            # Try Curator registry
            if not city_manager:
                try:
                    curator = self.di_container.get_foundation_service("CuratorFoundationService")
                    if curator:
                        city_manager_registration = curator.registered_services.get("CityManager")
                        if city_manager_registration:
                            city_manager = city_manager_registration.get("service_instance")
                except Exception:
                    pass
            
            # If City Manager is available, we're done
            if city_manager:
                self.logger.info("✅ City Manager already available")
                return
            
            # City Manager not available - bootstrap it
            self.logger.info("🔧 City Manager not available - bootstrapping...")
            
            # Import City Manager Service
            try:
                from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
            except ImportError as e:
                self.logger.error(f"❌ Failed to import City Manager Service: {e}")
                raise ValueError("City Manager Service not available and cannot be imported")
            
            # Create and initialize City Manager
            city_manager = CityManagerService(di_container=self.di_container)
            await city_manager.initialize()
            
            # Register with DI container
            self.di_container.service_registry["CityManagerService"] = city_manager
            # Note: foundation_services may not exist on all DI container implementations
            if hasattr(self.di_container, 'foundation_services'):
                self.di_container.foundation_services["CityManagerService"] = city_manager
            
            # Register with Curator
            try:
                curator = self.di_container.get_foundation_service("CuratorFoundationService")
                if curator:
                    result = await curator.register_service(
                        service_instance=city_manager,
                        service_metadata={
                            "service_name": "CityManager",
                            "service_type": "smart_city",
                            "realm": "smart_city",
                            "capabilities": ["service_discovery", "realm_orchestration", "manager_hierarchy"],
                            "startup_policy": "eager"
                        }
                    )
                    if result.get("success"):
                        self.logger.info("✅ City Manager registered with Curator")
                    else:
                        self.logger.warning(f"⚠️ City Manager Curator registration failed: {result.get('error')}")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to register City Manager with Curator: {e}")
            
            self.logger.info("✅ City Manager bootstrapped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to bootstrap City Manager: {e}")
            raise ValueError(f"City Manager bootstrap failed: {e}")
    
    async def initialize(self) -> bool:
        """Initialize Frontend Gateway Service."""
        await super().initialize()
        
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("frontend_gateway_initialize_start", success=True)
            
            # 0. Ensure City Manager is available (lazy bootstrap if needed)
            await self._ensure_city_manager_available()
            
            # 1. Get Smart City services
            self.librarian = await self.get_librarian_api()
            self.security_guard = await self.get_security_guard_api()
            self.traffic_cop = await self.get_traffic_cop_api()
            
            # 2. Get APIRoutingUtility from DI container (for route execution and Curator registration)
            try:
                self.api_router = self.di_container.get_api_router()
                if self.api_router:
                    self.logger.info("✅ APIRoutingUtility connected for route execution")
                    # Initialize APIRoutingUtility if not already initialized
                    if hasattr(self.api_router, 'initialize') and not hasattr(self.api_router, '_initialized'):
                        await self.api_router.initialize()
                        self.api_router._initialized = True
                else:
                    self.logger.warning("⚠️ APIRoutingUtility not available - will use fallback routing")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get APIRoutingUtility: {e}")
            
            # ⭐ NEW: Register routes with Curator (Phase 2: Route Registration)
            await self._register_routes_with_curator()
            
            # ⭐ NEW: Discover routes from Curator if new routing is enabled
            if self.use_discovered_routing:
                await self._discover_routes_from_curator()
            
            # 3. Discover Business Enablement orchestrators via Curator
            await self._discover_orchestrators()
            
            # 4. Register routes via APIRoutingUtility (routes tracked in Curator)
            if self.api_router:
                await self._register_orchestrator_routes()
            
            # 5. Expose frontend APIs
            await self._expose_frontend_apis()
            
            # 6. Register with Curator
            await self.register_with_curator(
                capabilities=["frontend_api_gateway", "request_routing", "api_transformation", "chat_routing"],
                soa_apis=[
                    "expose_frontend_api", "route_frontend_request", "get_frontend_apis",
                    "handle_document_analysis_request", "handle_insights_request",
                    "handle_operations_request", "handle_data_operations_request",
                    "handle_guide_chat_request", "handle_liaison_chat_request",
                    "handle_create_conversation_request", "handle_conversation_history_request",
                    "register_api_endpoint", "validate_api_request", "transform_for_frontend"
                ],
                mcp_tools=[],  # Experience services provide SOA APIs, not MCP tools
                additional_metadata={
                    "layer": "experience",
                    "api_gateway": True,
                    "composes": "business_enablement_orchestrators",
                    "chat_enabled": True
                }
            )
            
            self.logger.info("✅ Frontend Gateway Service initialized successfully")
            
            # Record health metric
            await self.record_health_metric("frontend_gateway_initialized", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("frontend_gateway_initialize_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "frontend_gateway_initialize")
            self.logger.error(f"❌ Frontend Gateway Service initialization failed: {e}")
            await self.log_operation_with_telemetry("frontend_gateway_initialize_complete", success=False)
            return False
    
    async def _discover_orchestrators(self):
        """Discover Business Enablement orchestrators via Delivery Manager."""
        try:
            # Try multiple ways to get Delivery Manager
            delivery_manager = None
            
            # Method 1: Try getting it through City Manager (preferred - triggers bootstrap if needed)
            try:
                city_manager = await self._ensure_city_manager_available()
                if city_manager and hasattr(city_manager, 'get_manager'):
                    delivery_manager = await city_manager.get_manager("delivery_manager")
                    if delivery_manager:
                        self.logger.info("✅ Retrieved Delivery Manager via City Manager")
            except Exception as e:
                self.logger.debug(f"Could not get Delivery Manager via City Manager: {e}")
            
            # Method 2: Try DI container service registry (fallback)
            if not delivery_manager:
                delivery_manager = self.di_container.service_registry.get("DeliveryManagerService")
                if delivery_manager:
                    self.logger.info("✅ Retrieved Delivery Manager via service registry")
            
            # Method 3: Try foundation service (fallback)
            if not delivery_manager:
                try:
                    delivery_manager = self.di_container.get_foundation_service("DeliveryManagerService")
                    if delivery_manager:
                        self.logger.info("✅ Retrieved Delivery Manager via foundation service")
                except Exception as e:
                    self.logger.debug(f"Could not get Delivery Manager via foundation service: {e}")
            
            if delivery_manager and hasattr(delivery_manager, 'mvp_pillar_orchestrators'):
                self.logger.info("✅ Found DeliveryManagerService, discovering MVP pillar orchestrators...")
                
                # Get orchestrators from Delivery Manager's mvp_pillar_orchestrators dict
                # Note: keys are "content_analysis", not "content"
                if "content_analysis" in delivery_manager.mvp_pillar_orchestrators:
                    self.content_orchestrator = delivery_manager.mvp_pillar_orchestrators["content_analysis"]
                    self.logger.info("✅ Discovered ContentAnalysisOrchestrator from Delivery Manager")
                else:
                    self.logger.warning("⚠️ ContentAnalysisOrchestrator not in mvp_pillar_orchestrators")
                    self.logger.warning(f"   Available keys: {list(delivery_manager.mvp_pillar_orchestrators.keys())}")
                
                if "insights" in delivery_manager.mvp_pillar_orchestrators:
                    self.insights_orchestrator = delivery_manager.mvp_pillar_orchestrators["insights"]
                    self.logger.info("✅ Discovered InsightsOrchestrator from Delivery Manager")
                else:
                    self.logger.warning("⚠️ InsightsOrchestrator not in mvp_pillar_orchestrators")
                
                if "operations" in delivery_manager.mvp_pillar_orchestrators:
                    self.operations_orchestrator = delivery_manager.mvp_pillar_orchestrators["operations"]
                    self.logger.info("✅ Discovered OperationsOrchestrator from Delivery Manager")
                else:
                    self.logger.warning("⚠️ OperationsOrchestrator not in mvp_pillar_orchestrators")
                
                if "business_outcomes" in delivery_manager.mvp_pillar_orchestrators:
                    self.business_outcomes_orchestrator = delivery_manager.mvp_pillar_orchestrators["business_outcomes"]
                    self.logger.info("✅ Discovered BusinessOutcomesOrchestrator from Delivery Manager")
                else:
                    self.logger.warning("⚠️ BusinessOutcomesOrchestrator not in mvp_pillar_orchestrators")
                
                self.logger.info(f"✅ Available MVP pillar orchestrators: {list(delivery_manager.mvp_pillar_orchestrators.keys())}")
                
                # Populate orchestrators dictionary for dictionary-style access
                if self.content_orchestrator:
                    self.orchestrators["ContentAnalysisOrchestrator"] = self.content_orchestrator
                if self.insights_orchestrator:
                    self.orchestrators["InsightsOrchestrator"] = self.insights_orchestrator
                if self.operations_orchestrator:
                    self.orchestrators["OperationsOrchestrator"] = self.operations_orchestrator
                if self.data_operations_orchestrator:
                    self.orchestrators["DataOperationsOrchestrator"] = self.data_operations_orchestrator
                if self.business_outcomes_orchestrator:
                    self.orchestrators["BusinessOutcomesOrchestrator"] = self.business_outcomes_orchestrator
                
                self.logger.info(f"✅ Orchestrators registered: {list(self.orchestrators.keys())}")
            else:
                self.logger.warning("⚠️ DeliveryManagerService not available or missing mvp_pillar_orchestrators")
                self.logger.warning(f"   DI container has: {list(self.di_container.service_registry.keys())}")
                
                # Discover Chat Service
                try:
                    self.chat_service = await curator.get_service("ChatService")
                    self.logger.info("✅ Discovered ChatService")
                except Exception:
                    self.logger.warning("⚠️ ChatService not yet available")
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "discover_orchestrators")
            self.logger.error(f"❌ Orchestrator discovery failed: {e}")
    
    async def _register_orchestrator_routes(self):
        """Register orchestrator routes via APIRoutingUtility (routes tracked in Curator)."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_orchestrator_routes_start", success=True)
            
            if not self.api_router:
                self.logger.warning("⚠️ APIRoutingUtility not available - skipping route registration")
                await self.log_operation_with_telemetry("register_orchestrator_routes_complete", success=False)
                return
            
            from utilities.api_routing.api_routing_utility import HTTPMethod
            
            # Route mappings for each orchestrator
            route_mappings = {
                "content_analysis": {
                    "pillar": "content-pillar",
                    "orchestrator": self.content_orchestrator,
                    "routes": [
                        {"path": "/api/v1/content-pillar/list-uploaded-files", "method": "GET"},
                        {"path": "/api/v1/content-pillar/upload-file", "method": "POST"},
                        {"path": "/api/v1/content-pillar/process-file/{file_id}", "method": "POST"},
                    ]
                },
                "insights": {
                    "pillar": "insights-pillar",
                    "orchestrator": self.insights_orchestrator,
                    "routes": [
                        {"path": "/api/v1/insights-pillar/analyze-content-for-insights", "method": "POST"},
                    ]
                },
                "operations": {
                    "pillar": "operations-pillar",
                    "orchestrator": self.operations_orchestrator,
                    "routes": [
                        {"path": "/api/v1/operations-pillar/convert-sop-to-workflow", "method": "POST"},
                        {"path": "/api/v1/operations-pillar/convert-workflow-to-sop", "method": "POST"},
                    ]
                },
                "business_outcomes": {
                    "pillar": "business-outcomes-pillar",
                    "orchestrator": self.business_outcomes_orchestrator,
                    "routes": [
                        {"path": "/api/v1/business-outcomes-pillar/generate-strategic-roadmap", "method": "POST"},
                        {"path": "/api/v1/business-outcomes-pillar/generate-proof-of-concept-proposal", "method": "POST"},
                    ]
                }
            }
            
            registered_count = 0
            for orchestrator_key, mapping in route_mappings.items():
                orchestrator = mapping["orchestrator"]
                if not orchestrator:
                    self.logger.debug(f"⚠️ {orchestrator_key} orchestrator not available - skipping route registration")
                    continue
                
                for route in mapping["routes"]:
                    try:
                        # Create route handler that delegates to route_frontend_request()
                        # Use closure to capture route_path and route_method
                        route_path = route["path"]
                        route_method = route["method"]
                        
                        async def create_handler(route_path_inner, route_method_inner):
                            async def handler(request_context):
                                # Convert request_context to route_frontend_request format
                                return await self.route_frontend_request({
                                    "endpoint": route_path_inner,
                                    "method": request_context.method if hasattr(request_context, 'method') else route_method_inner,
                                    "params": request_context.body if hasattr(request_context, 'body') else {},
                                    "headers": request_context.headers if hasattr(request_context, 'headers') else {},
                                    "user_id": request_context.user_id if hasattr(request_context, 'user_id') else None,
                                    "session_token": request_context.session_token if hasattr(request_context, 'session_token') else None,
                                    "query_params": request_context.query_params if hasattr(request_context, 'query_params') else {}
                                })
                            return handler
                        
                        handler = await create_handler(route_path, route_method)
                        
                        await self.api_router.register_route(
                            method=HTTPMethod[route["method"]],
                            path=route["path"],
                            handler=handler,
                            pillar=mapping["pillar"],
                            realm="business_enablement",
                            description=f"REST API route for {orchestrator_key} orchestrator",
                            version="v1"
                        )
                        # APIRoutingUtility automatically registers in Curator
                        registered_count += 1
                        self.logger.debug(f"✅ Registered route: {route['method']} {route['path']}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to register route {route['path']}: {e}")
            
            if registered_count > 0:
                self.logger.info(f"✅ Registered {registered_count} orchestrator routes via APIRoutingUtility (tracked in Curator)")
                # Record health metric
                await self.record_health_metric("orchestrator_routes_registered", float(registered_count), {"service": self.service_name})
            else:
                self.logger.warning("⚠️ No routes registered - orchestrators may not be available")
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_orchestrator_routes_complete", success=(registered_count > 0))
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_orchestrator_routes")
            self.logger.error(f"❌ Failed to register orchestrator routes: {e}")
            await self.log_operation_with_telemetry("register_orchestrator_routes_complete", success=False)
            import traceback
            self.logger.debug(traceback.format_exc())
    
    async def _expose_frontend_apis(self):
        """Expose frontend APIs for discovered orchestrators."""
        # Register API endpoints
        if self.content_orchestrator:
            await self.register_api_endpoint("/api/documents/analyze", self.handle_document_analysis_request)
        
        if self.insights_orchestrator:
            await self.register_api_endpoint("/api/insights/generate", self.handle_insights_request)
        
        if self.operations_orchestrator:
            await self.register_api_endpoint("/api/operations/optimize", self.handle_operations_request)
        
        if self.data_operations_orchestrator:
            await self.register_api_endpoint("/api/data/transform", self.handle_data_operations_request)
        
        # Register chat endpoints
        if self.chat_service:
            await self.register_api_endpoint("/api/chat/guide", self.handle_guide_chat_request)
            await self.register_api_endpoint("/api/chat/liaison", self.handle_liaison_chat_request)
            await self.register_api_endpoint("/api/chat/conversation/create", self.handle_create_conversation_request)
            await self.register_api_endpoint("/api/chat/conversation/history", self.handle_conversation_history_request)
    
    # ========================================================================
    # SOA APIs (Frontend Gateway)
    # ========================================================================
    
    async def expose_frontend_api(
        self,
        api_name: str,
        endpoint: str,
        handler: Callable
    ) -> bool:
        """
        Expose a frontend API endpoint (SOA API).
        
        Args:
            api_name: Name of the API
            endpoint: API endpoint path
            handler: Handler function for the API
        
        Returns:
            bool: True if API exposed successfully
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("expose_frontend_api_start", success=True, metadata={"api_name": api_name, "endpoint": endpoint})
            
            self.registered_apis[endpoint] = {
                "api_name": api_name,
                "handler": handler,
                "exposed_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"✅ Exposed frontend API: {api_name} at {endpoint}")
            
            # Record health metric
            await self.record_health_metric("frontend_api_exposed", 1.0, {"api_name": api_name, "endpoint": endpoint})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("expose_frontend_api_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "expose_frontend_api")
            self.logger.error(f"❌ Expose frontend API failed: {e}")
            await self.log_operation_with_telemetry("expose_frontend_api_complete", success=False)
            return False
    
    # ============================================================================
    # ⭐ NEW: Route Registration and Discovery (Parallel Implementation)
    # ============================================================================
    
    async def _register_routes_with_curator(self):
        """
        Register all FrontendGatewayService routes with Curator (Phase 2: Route Registration).
        
        This method registers all routes that FrontendGatewayService handles,
        making them discoverable for the new routing approach.
        
        Routes are registered in Curator's RouteRegistryService endpoint registry.
        """
        try:
            self.logger.info("📋 Registering routes with Curator...")
            
            # Get Curator (use get_curator from base class)
            curator = self.get_curator()
            if not curator:
                self.logger.warning("⚠️ Curator not available - cannot register routes")
                return
            
            # Get RouteRegistryService
            route_registry = None
            try:
                # Try to get RouteRegistryService from Curator
                if hasattr(curator, 'get_service'):
                    route_registry = curator.get_service("RouteRegistryService")
                elif hasattr(curator, 'route_registry_service'):
                    route_registry = curator.route_registry_service
                else:
                    # Try direct access
                    route_registry = getattr(curator, 'route_registry', None)
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get RouteRegistryService: {e}")
            
            if not route_registry:
                self.logger.warning("⚠️ RouteRegistryService not available - routes will not be registered")
                return
            
            # Define all routes handled by FrontendGatewayService
            # Starting with Content and Insights pillars (most used)
            routes_to_register = [
                # Content Pillar Routes
                {
                    "route_id": "content_upload_file",
                    "path": "/api/v1/content-pillar/upload-file",
                    "method": "POST",
                    "pillar": "content-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "file_upload",
                    "handler": "handle_upload_file_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Upload file for content analysis",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "content_process_file",
                    "path": "/api/v1/content-pillar/process-file/{file_id}",
                    "method": "POST",
                    "pillar": "content-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "file_processing",
                    "handler": "handle_process_file_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Process uploaded file",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "content_list_files",
                    "path": "/api/v1/content-pillar/list-uploaded-files",
                    "method": "GET",
                    "pillar": "content-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "file_listing",
                    "handler": "handle_list_uploaded_files_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "List uploaded files",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "content_get_file_details",
                    "path": "/api/v1/content-pillar/get-file-details/{file_id}",
                    "method": "GET",
                    "pillar": "content-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "file_details",
                    "handler": "handle_get_file_details_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Get file details",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "content_health",
                    "path": "/api/v1/content-pillar/health",
                    "method": "GET",
                    "pillar": "content-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "health_check",
                    "handler": "handle_content_pillar_health_check_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Content pillar health check",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                # Insights Pillar Routes
                {
                    "route_id": "insights_analyze_content",
                    "path": "/api/v1/insights-pillar/analyze-content",
                    "method": "POST",
                    "pillar": "insights-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "content_analysis",
                    "handler": "handle_analyze_content_for_insights_semantic_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Analyze content for insights",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "insights_query_analysis",
                    "path": "/api/v1/insights-pillar/query-analysis",
                    "method": "POST",
                    "pillar": "insights-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "query_analysis",
                    "handler": "handle_query_insights_analysis_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Query insights analysis",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "insights_available_metadata",
                    "path": "/api/v1/insights-pillar/available-content-metadata",
                    "method": "GET",
                    "pillar": "insights-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "metadata_listing",
                    "handler": "handle_get_available_content_metadata_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Get available content metadata",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "insights_validate_metadata",
                    "path": "/api/v1/insights-pillar/validate-content-metadata",
                    "method": "POST",
                    "pillar": "insights-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "metadata_validation",
                    "handler": "handle_validate_content_metadata_for_insights_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Validate content metadata",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "insights_analysis_results",
                    "path": "/api/v1/insights-pillar/analysis-results/{analysis_id}",
                    "method": "GET",
                    "pillar": "insights-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "analysis_results",
                    "handler": "handle_get_insights_analysis_results_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Get insights analysis results",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "insights_analysis_visualizations",
                    "path": "/api/v1/insights-pillar/analysis-visualizations/{analysis_id}",
                    "method": "GET",
                    "pillar": "insights-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "analysis_visualizations",
                    "handler": "handle_get_insights_analysis_visualizations_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Get insights analysis visualizations",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "insights_user_analyses",
                    "path": "/api/v1/insights-pillar/user-analyses",
                    "method": "GET",
                    "pillar": "insights-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "user_analyses",
                    "handler": "handle_list_user_insights_analyses_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "List user insights analyses",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "insights_health",
                    "path": "/api/v1/insights-pillar/health",
                    "method": "GET",
                    "pillar": "insights-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "health_check",
                    "handler": "handle_insights_pillar_health_check_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Insights pillar health check",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                # Operations Pillar Routes (key routes - can add more later)
                {
                    "route_id": "operations_health",
                    "path": "/api/v1/operations-pillar/health",
                    "method": "GET",
                    "pillar": "operations-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "health_check",
                    "handler": "handle_operations_pillar_health_check_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Operations pillar health check",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                # Business Outcomes Pillar Routes (key routes - can add more later)
                {
                    "route_id": "business_outcomes_health",
                    "path": "/api/v1/business-outcomes-pillar/health",
                    "method": "GET",
                    "pillar": "business-outcomes-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "health_check",
                    "handler": "handle_business_outcomes_health_check_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Business Outcomes pillar health check",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                }
            ]
            
            # Register each route
            routes_registered = 0
            for route_metadata in routes_to_register:
                try:
                    # Verify handler exists
                    handler_name = route_metadata.get("handler")
                    if not hasattr(self, handler_name):
                        self.logger.warning(f"⚠️ Handler method not found: {handler_name}, skipping route")
                        continue
                    
                    # Register route with RouteRegistryService
                    success = await route_registry.register_route(
                        route_metadata=route_metadata,
                        user_context=None  # System registration, no user context needed
                    )
                    
                    if success:
                        routes_registered += 1
                        self.logger.debug(f"✅ Route registered: {route_metadata['path']}")
                    else:
                        self.logger.warning(f"⚠️ Failed to register route: {route_metadata['path']}")
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Error registering route {route_metadata.get('path')}: {e}")
            
            self.logger.info(f"✅ Registered {routes_registered}/{len(routes_to_register)} routes with Curator")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Route registration failed: {e}, routes will not be discoverable")
            import traceback
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
    
    async def _discover_routes_from_curator(self):
        """
        Discover routes from Curator's RouteRegistryService (new approach).
        
        This method discovers routes that were registered by services during initialization.
        Routes are tracked in Curator's endpoint registry for discovery.
        """
        try:
            self.logger.info("🔍 Discovering routes from Curator...")
            
            # Get Curator (use get_curator from base class)
            curator = self.get_curator()
            if not curator:
                self.logger.warning("⚠️ Curator not available - cannot discover routes")
                return
            
            # Get RouteRegistryService from Curator
            route_registry = None
            try:
                if hasattr(curator, 'route_registry'):
                    route_registry = curator.route_registry
                elif hasattr(curator, 'route_registry_service'):
                    route_registry = curator.route_registry_service
                elif hasattr(curator, 'get_service'):
                    route_registry = curator.get_service("RouteRegistryService")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get RouteRegistryService: {e}")
            
            if not route_registry:
                self.logger.warning("⚠️ RouteRegistryService not available - cannot discover routes")
                return
            
            # Discover routes (RouteRegistryService.discover_routes doesn't take status parameter)
            try:
                routes = await route_registry.discover_routes()
            except Exception as e:
                self.logger.warning(f"⚠️ Route discovery failed: {e}")
                return
            
            if not routes:
                self.logger.info("ℹ️ No routes discovered from Curator (routes may not be registered yet)")
                return
            
            # Build route registry in APIRoutingUtility
            routes_registered = 0
            for route in routes:
                # Only register routes that have FrontendGatewayService as handler_service
                handler_service = route.get("handler_service")
                if handler_service != "FrontendGatewayService":
                    continue
                
                handler_name = route.get("handler")
                if not handler_name:
                    continue
                
                # Get handler method from this service
                handler = getattr(self, handler_name, None)
                if not handler:
                    self.logger.warning(f"⚠️ Handler method not found: {handler_name}")
                    continue
                
                # Register route with APIRoutingUtility
                if self.api_router:
                    try:
                        from utilities.api_routing.api_routing_utility import HTTPMethod, RequestContext
                        
                        # Create adapter wrapper that converts APIRoutingUtility's handler signature
                        # APIRoutingUtility calls: handler(request_context.body, request_context.user_context)
                        # Our handlers have different signatures, so we need to adapt
                        def create_adapter(original_handler, handler_name: str):
                            """Create adapter function."""
                            async def adapter_handler(request_body: Dict[str, Any], user_context: Any):
                                """Adapter that converts APIRoutingUtility signature to our handler signature."""
                                # Extract user_id from user_context
                                user_id = user_context.user_id if user_context and hasattr(user_context, 'user_id') else "anonymous"
                                
                                # Call original handler with extracted parameters based on handler name
                                try:
                                    if handler_name == "handle_upload_file_request":
                                        return await original_handler(
                                            file_data=request_body.get("file_data"),
                                            filename=request_body.get("filename"),
                                            content_type=request_body.get("content_type"),
                                            user_id=user_id,
                                            session_id=request_body.get("session_id"),
                                            copybook_data=request_body.get("copybook_data"),
                                            copybook_filename=request_body.get("copybook_filename")
                                        )
                                    elif handler_name == "handle_content_pillar_health_check_request":
                                        return await original_handler()
                                    elif handler_name == "handle_insights_pillar_health_check_request":
                                        return await original_handler()
                                    elif handler_name == "handle_operations_pillar_health_check_request":
                                        return await original_handler()
                                    elif handler_name == "handle_business_outcomes_health_check_request":
                                        return await original_handler()
                                    elif handler_name == "handle_list_uploaded_files_request":
                                        return await original_handler(user_id=user_id)
                                    elif handler_name == "handle_get_file_details_request":
                                        # Extract file_id from path (stored in request_body by _route_via_discovery)
                                        file_id = request_body.get("file_id")
                                        return await original_handler(file_id=file_id, user_id=user_id)
                                    elif handler_name == "handle_process_file_request":
                                        file_id = request_body.get("file_id")
                                        return await original_handler(
                                            file_id=file_id,
                                            user_id=user_id,
                                            copybook_file_id=request_body.get("copybook_file_id"),
                                            processing_options=request_body.get("processing_options")
                                        )
                                    elif handler_name == "handle_analyze_content_for_insights_semantic_request":
                                        return await original_handler(
                                            source_type=request_body.get("source_type", "file"),
                                            file_id=request_body.get("file_id"),
                                            content_metadata_id=request_body.get("content_metadata_id"),
                                            content_type=request_body.get("content_type", "structured"),
                                            analysis_options=request_body.get("analysis_options")
                                        )
                                    elif handler_name == "handle_query_insights_analysis_request":
                                        return await original_handler(
                                            analysis_id=request_body.get("analysis_id"),
                                            query=request_body.get("query"),
                                            user_id=user_id
                                        )
                                    elif handler_name == "handle_get_available_content_metadata_request":
                                        return await original_handler(user_id=user_id)
                                    elif handler_name == "handle_validate_content_metadata_for_insights_request":
                                        return await original_handler(
                                            metadata_id=request_body.get("metadata_id"),
                                            user_id=user_id
                                        )
                                    elif handler_name == "handle_get_insights_analysis_results_request":
                                        analysis_id = request_body.get("analysis_id")
                                        return await original_handler(analysis_id=analysis_id, user_id=user_id)
                                    elif handler_name == "handle_get_insights_analysis_visualizations_request":
                                        analysis_id = request_body.get("analysis_id")
                                        return await original_handler(analysis_id=analysis_id, user_id=user_id)
                                    elif handler_name == "handle_list_user_insights_analyses_request":
                                        return await original_handler(user_id=user_id)
                                    else:
                                        # Generic handler - pass request_body as kwargs
                                        return await original_handler(**request_body, user_id=user_id)
                                except Exception as e:
                                    self.logger.error(f"❌ Handler adapter failed for {handler_name}: {e}")
                                    raise
                            
                            return adapter_handler
                        
                        adapter = create_adapter(handler, handler_name)
                        
                        await self.api_router.register_route(
                            method=HTTPMethod[route["method"]],
                            path=route["path"],
                            handler=adapter,
                            pillar=route.get("pillar", ""),
                            realm=route.get("realm", ""),
                            description=route.get("description", ""),
                            version=route.get("version", "1.0")
                        )
                        
                        # Store in discovered routes registry
                        route_key = f"{route['method']}:{route['path']}"
                        self.discovered_routes[route_key] = route
                        routes_registered += 1
                        
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to register route {route['path']}: {e}")
            
            self.logger.info(f"✅ Discovered and registered {routes_registered} routes from Curator")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Route discovery failed: {e}, will use hardcoded routing as fallback")
            import traceback
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
    
    async def _route_via_discovery(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route request using discovered routes from Curator (new approach).
        
        This method uses APIRoutingUtility to find and execute routes that were
        discovered from Curator's RouteRegistryService.
        
        Args:
            request: Frontend request data
            
        Returns:
            Frontend-ready response
        """
        try:
            endpoint = request.get("endpoint", "")
            method = request.get("method", "POST")
            
            if not self.api_router:
                return {"success": False, "error": "APIRoutingUtility not available"}
            
            # Use APIRoutingUtility's route_request method which handles route matching internally
            from utilities.api_routing.api_routing_utility import HTTPMethod, UserContext
            
            # Convert method string to HTTPMethod enum
            try:
                http_method = HTTPMethod[method.upper()]
            except KeyError:
                return {"success": False, "error": f"Invalid HTTP method: {method}"}
            
            # Build user context (UserContext requires email, full_name, permissions)
            user_id = request.get("user_id") or request.get("params", {}).get("user_id", "anonymous")
            user_context = UserContext(
                user_id=user_id,
                email=request.get("params", {}).get("email", f"{user_id}@example.com"),
                full_name=request.get("params", {}).get("full_name", user_id),
                session_id=request.get("params", {}).get("session_id", ""),
                permissions=request.get("params", {}).get("permissions", []),
                tenant_id=request.get("params", {}).get("tenant_id")
            )
            
            # Execute route with middleware via APIRoutingUtility
            # route_request() handles route matching internally via _find_matching_route()
            # Note: We need to extract path parameters from endpoint for handlers that need them
            request_data = request.get("params", {}).copy()
            
            # Extract path parameters (e.g., /api/v1/content-pillar/process-file/{file_id})
            # Store in request_data so adapter can access them
            path_parts = endpoint.strip("/").split("/")
            if len(path_parts) >= 5:  # /api/v1/pillar/path/{id}
                # Try to extract ID from path (last part after the action)
                action_part = path_parts[-2] if len(path_parts) > 4 else None
                id_part = path_parts[-1] if len(path_parts) > 4 else None
                
                # Map common patterns
                if "file" in action_part or "file" in (path_parts[-2] if len(path_parts) > 3 else ""):
                    if id_part and id_part not in ["health", "list-uploaded-files", "upload-file"]:
                        request_data["file_id"] = id_part
                elif "analysis" in action_part:
                    if id_part and id_part not in ["results", "visualizations"]:
                        request_data["analysis_id"] = id_part
            
            response_context = await self.api_router.route_request(
                method=http_method,
                path=endpoint,
                request_data=request_data,
                user_context=user_context,
                headers=request.get("headers", {}),
                query_params=request.get("query_params", {})
            )
            
            # Check if route was found (404 means route not found)
            if response_context.status_code == 404:
                return {
                    "success": False,
                    "error": "Route not found",
                    "endpoint": endpoint,
                    "routing_method": "discovered"
                }
            
            # Return response body
            return response_context.body
            
        except Exception as e:
            self.logger.error(f"❌ Discovered routing failed: {e}", exc_info=True)
            return {"success": False, "error": str(e), "routing_method": "discovered"}
    
    async def _route_via_hardcoded(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route request using hardcoded if/elif chains (existing approach).
        
        This is the current routing implementation that will be replaced
        once discovered routing is validated.
        
        Args:
            request: Frontend request data
            
        Returns:
            Frontend-ready response
        """
        # This method contains the existing hardcoded routing logic
        # We'll keep the existing route_frontend_request logic here
        # For now, we'll call the existing implementation
        # (The existing route_frontend_request will be refactored to call this)
        pass  # Placeholder - existing logic will be moved here
    
    async def route_frontend_request(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Universal request router - routes requests to pillar-specific handlers (SOA API).
        
        Called by all protocol adapters (REST, GraphQL, WebSocket, gRPC).
        Parses endpoint to determine pillar and path, then routes to appropriate handler.
        
        Args:
            request: Frontend request data
                - endpoint: "/api/{pillar}/{path}" 
                - method: "GET" | "POST" | "PUT" | "DELETE"
                - params: Request parameters/body
                - headers: Optional headers
                - query_params: Optional query parameters
                - user_id: Optional user identifier
        
        Returns:
            Frontend-ready response
        """
        try:
            # Start telemetry tracking
            endpoint = request.get("endpoint", "")
            method = request.get("method", "POST")
            await self.log_operation_with_telemetry("route_frontend_request_start", success=True, metadata={"endpoint": endpoint, "method": method})
            
            # ⭐ NEW: Feature flag check - try new routing first if enabled
            if self.use_discovered_routing:
                start_time = datetime.utcnow()
                try:
                    result = await self._route_via_discovery(request)
                    elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                    
                    # Track metrics for new routing
                    if self.routing_monitoring_enabled:
                        self.routing_metrics["new_routing"]["requests"] += 1
                        self.routing_metrics["new_routing"]["total_time_ms"] += elapsed_ms
                        if result.get("success") is not False and result.get("error") != "Route not found":
                            self.routing_metrics["new_routing"]["successes"] += 1
                        else:
                            self.routing_metrics["new_routing"]["errors"] += 1
                            self.routing_metrics["new_routing"]["fallbacks"] += 1
                        # Update average
                        if self.routing_metrics["new_routing"]["requests"] > 0:
                            self.routing_metrics["new_routing"]["avg_time_ms"] = (
                                self.routing_metrics["new_routing"]["total_time_ms"] / 
                                self.routing_metrics["new_routing"]["requests"]
                            )
                    
                    # If routing succeeded (not a "route not found" error), return result
                    if result.get("success") is not False or result.get("error") != "Route not found":
                        if self.routing_monitoring_enabled:
                            self.logger.debug(f"✅ New routing: {endpoint} ({elapsed_ms:.2f}ms)")
                        return result
                    # Otherwise, fall through to hardcoded routing as fallback
                    self.logger.debug(f"Route not found via discovery for {endpoint}, falling back to hardcoded routing")
                except Exception as e:
                    elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                    if self.routing_monitoring_enabled:
                        self.routing_metrics["new_routing"]["requests"] += 1
                        self.routing_metrics["new_routing"]["errors"] += 1
                        self.routing_metrics["new_routing"]["fallbacks"] += 1
                        self.routing_metrics["new_routing"]["total_time_ms"] += elapsed_ms
                    self.logger.warning(f"⚠️ Discovered routing failed for {endpoint}: {e}, falling back to hardcoded routing")
                    # Fall through to hardcoded routing as fallback
            
            # Existing hardcoded routing (fallback or when feature flag is False)
            start_time_old = datetime.utcnow()
            
            params = request.get("params", {})
            headers = request.get("headers", {})
            query_params = request.get("query_params", {})
            
            # Extract authentication token from Authorization header
            auth_token = None
            auth_header = headers.get("Authorization") or headers.get("authorization")
            if auth_header:
                # Support "Bearer <token>" format
                if auth_header.startswith("Bearer "):
                    auth_token = auth_header[7:].strip()
                else:
                    # Also support token without "Bearer " prefix
                    auth_token = auth_header.strip()
            
            # Extract user_id from headers/params (fallback for backward compatibility)
            user_id = request.get("user_id") or params.get("user_id", "anonymous")
            
            # If we have a token, try to validate it and get the actual user context
            if auth_token:
                try:
                    # Try to get AuthAbstraction from Public Works Foundation to validate token
                    public_works_foundation = self.di_container.get_foundation_service("PublicWorksFoundationService")
                    if public_works_foundation:
                        auth_abstraction = public_works_foundation.get_auth_abstraction()
                        if auth_abstraction:
                            # Validate token using AuthAbstraction
                            security_context = await auth_abstraction.validate_token(auth_token)
                            if security_context and security_context.user_id:
                                user_id = security_context.user_id
                                self.logger.info(f"✅ Authenticated user from token: {user_id} (origin: {security_context.origin})")
                            else:
                                self.logger.warning(f"⚠️ Token validation returned anonymous context")
                        else:
                            self.logger.warning(f"⚠️ AuthAbstraction not available, using provided user_id: {user_id}")
                    else:
                        self.logger.warning(f"⚠️ PublicWorksFoundationService not available, using provided user_id: {user_id}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to validate token: {e}, using provided user_id: {user_id}")
            
            self.logger.info(f"🌐 Routing {method} {endpoint} for user: {user_id}")
            
            # Parse endpoint: /api/v1/{pillar}/{path} or /api/{pillar}/{path} (backward compatibility)
            parts = endpoint.strip("/").split("/")
            if len(parts) < 3 or parts[0] != "api":
                return {
                    "success": False,
                    "error": "Invalid Endpoint",
                    "message": f"Endpoint must be /api/v1/{{pillar}}/{{path}} or /api/{{pillar}}/{{path}}, got: {endpoint}"
                }
            
            # Check if version is present (v1, v2, etc.)
            version = None
            pillar_index = 1
            if len(parts) >= 4 and parts[1].startswith("v") and parts[1][1:].isdigit():
                # Versioned endpoint: /api/v1/{pillar}/{path}
                version = parts[1]  # v1, v2, v3, etc.
                pillar_index = 2
            
            pillar = parts[pillar_index]  # content-pillar, insights-pillar, operations-pillar, business-outcomes-pillar
            path_parts = parts[pillar_index + 1:]  # remaining path
            path = "/".join(path_parts)
            
            # Normalize pillar name (remove -pillar suffix if present, for backward compatibility)
            # But also support full pillar names: content-pillar, insights-pillar, etc.
            pillar_normalized = pillar.replace("-pillar", "") if pillar.endswith("-pillar") else pillar
            
            self.logger.info(f"📍 Version: {version}, Pillar: {pillar} (normalized: {pillar_normalized}), Path: {path}")
            
            # Zero-Trust Authorization via Security Guard
            # "Secure by design, open by policy" - CTO requirement
            # DEMO MODE: Allow anonymous access to API endpoints for demo purposes
            # TODO: Remove this for production - require proper authentication
            demo_mode = True  # Set to False for production
            
            if self.security_guard and not (demo_mode and endpoint.startswith("/api/")):
                try:
                    auth_result = await self.security_guard.authorize_action({
                        "user_id": user_id,
                        "action": method,
                        "resource": endpoint,
                        "tenant_id": params.get("tenant_id", "default"),
                        "context": {
                            "pillar": pillar,
                            "path": path,
                            "headers": headers,
                            "token": auth_token  # Pass token to Security Guard for validation
                        }
                    })
                    
                    if not auth_result.get("success", False):
                        self.logger.warning(f"🛡️ Authorization denied: {user_id} -> {method} {endpoint}")
                        return {
                            "success": False,
                            "error": "Unauthorized",
                            "message": f"Access denied: {auth_result.get('message', 'Insufficient permissions')}"
                        }
                    
                    self.logger.info(f"✅ Authorization granted: {user_id} -> {method} {endpoint}")
                except Exception as e:
                    self.logger.error(f"❌ Authorization check failed: {e}")
                    # Fail closed (deny on error) for zero-trust
                    return {
                        "success": False,
                        "error": "Authorization Error",
                        "message": "Unable to verify authorization"
                    }
            elif demo_mode and endpoint.startswith("/api/"):
                self.logger.info(f"✅ Authorization granted (demo mode - anonymous API access): {user_id} -> {method} {endpoint}")
            else:
                # Security Guard not available - log warning but allow for MVP
                # TODO: Make Security Guard required for production deployment
                self.logger.warning(f"⚠️ Security Guard not available - request allowed without authorization check")
                self.logger.warning(f"   This is acceptable for MVP but MUST be fixed for production")
            
            # Route to pillar-specific handlers
            result = None
            
            # ================================================================
            # CONTENT PILLAR ROUTING
            # ================================================================
            if pillar == "content-pillar" or pillar_normalized == "content":
                if path == "upload-file" and method == "POST":
                    # Extract file data from params (will be added by universal router)
                    result = await self.handle_upload_file_request(
                        file_data=params.get("file_data"),
                        filename=params.get("filename"),
                        content_type=params.get("content_type"),
                        user_id=user_id,
                        session_id=params.get("session_id"),
                        copybook_data=params.get("copybook_data"),
                        copybook_filename=params.get("copybook_filename")
                    )
                
                elif path.startswith("process-file/") and method == "POST":
                    file_id = path.split("/")[1]
                    result = await self.handle_process_file_request(
                        file_id=file_id,
                        user_id=user_id,
                        copybook_file_id=params.get("copybook_file_id"),
                        processing_options=params.get("processing_options")
                    )
                
                elif path == "list-uploaded-files" and method == "GET":
                    result = await self.handle_list_uploaded_files_request(
                        user_id=user_id
                    )
                
                elif path.startswith("get-file-details/") and method == "GET":
                    file_id = path.split("/")[1]
                    result = await self.handle_get_file_details_request(
                        file_id=file_id,
                        user_id=user_id
                    )
                
                elif path == "health" and method == "GET":
                    result = await self.handle_content_pillar_health_check_request()
                
                else:
                    result = {
                        "success": False,
                        "error": "Not Found",
                        "message": f"Content Pillar endpoint not found: {path}"
                    }
            
            # ================================================================
            # INSIGHTS PILLAR ROUTING
            # ================================================================
            elif pillar == "insights-pillar" or pillar_normalized == "insights":
                if path == "analyze-content" and method == "POST":
                    # Map request parameters to semantic API handler signature
                    # Handler expects: source_type, file_id, content_metadata_id, content_type, analysis_options
                    result = await self.handle_analyze_content_for_insights_semantic_request(
                        source_type=params.get("source_type", "file"),  # 'file' or 'content_metadata'
                        file_id=params.get("file_id"),  # Required if source_type='file'
                        content_metadata_id=params.get("content_metadata_id"),  # Required if source_type='content_metadata'
                        content_type=params.get("content_type", "structured"),  # 'structured', 'unstructured', or 'hybrid'
                        analysis_options=params.get("analysis_options")  # Optional configuration dict
                    )
                
                elif path == "query-analysis" and method == "POST":
                    result = await self.handle_query_insights_analysis_request(
                        analysis_id=params.get("analysis_id"),
                        query=params.get("query"),
                        user_id=user_id
                    )
                
                elif path == "available-content-metadata" and method == "GET":
                    result = await self.handle_get_available_content_metadata_request(
                        user_id=user_id
                    )
                
                elif path == "validate-content-metadata" and method == "POST":
                    result = await self.handle_validate_content_metadata_for_insights_request(
                        metadata_id=params.get("metadata_id"),
                        user_id=user_id
                    )
                
                elif path.startswith("analysis-results/") and method == "GET":
                    analysis_id = path.split("/")[1]
                    result = await self.handle_get_insights_analysis_results_request(
                        analysis_id=analysis_id,
                        user_id=user_id
                    )
                
                elif path.startswith("analysis-visualizations/") and method == "GET":
                    analysis_id = path.split("/")[1]
                    result = await self.handle_get_insights_analysis_visualizations_request(
                        analysis_id=analysis_id,
                        user_id=user_id
                    )
                
                elif path == "user-analyses" and method == "GET":
                    result = await self.handle_list_user_insights_analyses_request(
                        user_id=user_id
                    )
                
                elif path == "pillar-summary" and method == "GET":
                    result = await self.handle_get_insights_pillar_summary_request(
                        analysis_id=params.get("analysis_id"),
                        user_id=user_id
                    )
                
                elif path == "health" and method == "GET":
                    result = await self.handle_insights_pillar_health_check_request()
                
                else:
                    result = {
                        "success": False,
                        "error": "Not Found",
                        "message": f"Insights Pillar endpoint not found: {path}"
                    }
            
            # ================================================================
            # OPERATIONS PILLAR ROUTING
            # ================================================================
            elif pillar == "operations-pillar" or pillar_normalized == "operations":
                # Session Management
                if path == "session/elements" and method == "GET":
                    result = await self.handle_get_session_elements_request(
                        session_token=params.get("session_token") or query_params.get("session_token")
                    )
                
                elif path == "session/elements" and method == "DELETE":
                    result = await self.handle_clear_session_elements_request(
                        session_token=params.get("session_token") or query_params.get("session_token")
                    )
                
                # Process Blueprint (support both hyphen and underscore formats)
                elif path in ["generate-workflow-from-sop", "generate_workflow_from_sop"] and method == "POST":
                    # Extract sop_content from either direct params or workflow_data
                    sop_content = params.get("sop_content")
                    if not sop_content and "workflow_data" in params:
                        sop_content = params["workflow_data"].get("sop_content")
                    
                    result = await self.handle_generate_workflow_from_sop_request(
                        session_token=params.get("session_token"),
                        sop_file_uuid=params.get("sop_file_uuid"),
                        sop_content=sop_content
                    )
                
                elif path in ["generate-sop-from-workflow", "generate_sop_from_workflow"] and method == "POST":
                    # Extract workflow_content from multiple possible locations
                    workflow_content = params.get("workflow_content")
                    if not workflow_content and "workflow_data" in params:
                        workflow_content = params["workflow_data"].get("workflow_content")
                    if not workflow_content and "sop_data" in params:
                        workflow_content = params["sop_data"].get("workflow")
                    
                    result = await self.handle_generate_sop_from_workflow_request(
                        session_token=params.get("session_token"),
                        workflow_file_uuid=params.get("workflow_file_uuid"),
                        workflow_content=workflow_content
                    )
                
                elif path == "files/analyze" and method == "GET":
                    result = await self.handle_analyze_file_request(
                        session_token=query_params.get("session_token"),
                        input_file_uuid=query_params.get("input_file_uuid"),
                        output_type=query_params.get("output_type")
                    )
                
                # Coexistence Analysis
                elif path == "files/coexistence" and method == "GET":
                    result = await self.handle_analyze_coexistence_files_request(
                        session_token=query_params.get("session_token")
                    )
                
                elif path == "coexistence/analyze" and method == "POST":
                    result = await self.handle_analyze_coexistence_content_request(
                        session_token=params.get("session_token"),
                        sop_content=params.get("sop_content"),
                        workflow_content=params.get("workflow_content")
                    )
                
                # Wizard Mode
                elif path == "wizard/start" and method == "POST":
                    result = await self.handle_start_wizard_request()
                
                elif path == "wizard/chat" and method == "POST":
                    result = await self.handle_wizard_chat_request(
                        session_token=params.get("session_token"),
                        user_message=params.get("user_message")
                    )
                
                elif path == "wizard/publish" and method == "POST":
                    result = await self.handle_wizard_publish_request(
                        session_token=params.get("session_token")
                    )
                
                # Blueprint Management
                elif path == "blueprint/save" and method == "POST":
                    result = await self.handle_save_blueprint_request(
                        blueprint=params.get("blueprint"),
                        user_id=params.get("user_id")
                    )
                
                # Liaison Agent (Conversational)
                elif path == "query" and method == "POST":
                    result = await self.handle_process_operations_query_request(
                        session_id=params.get("session_id"),
                        query=params.get("query"),
                        file_url=params.get("file_url"),
                        context=params.get("context")
                    )
                
                elif path == "conversation" and method == "POST":
                    result = await self.handle_process_operations_conversation_request(
                        session_id=params.get("session_id"),
                        message=params.get("message"),
                        context=params.get("context")
                    )
                
                elif path.startswith("session/") and path.endswith("/context") and method == "GET":
                    session_id = path.split("/")[1]
                    result = await self.handle_get_operations_conversation_context_request(
                        session_id=session_id
                    )
                
                elif path == "intent/analyze" and method == "POST":
                    result = await self.handle_analyze_operations_intent_request(
                        query=params.get("query")
                    )
                
                # Semantic API Endpoints (NEW)
                elif path == "create-standard-operating-procedure" and method == "POST":
                    result = await self.handle_create_standard_operating_procedure_request(
                        sop_content=params.get("sop_content"),
                        description=params.get("description"),
                        sop_type=params.get("sop_type"),
                        file_ids=params.get("file_ids"),
                        options=params.get("options"),
                        user_id=user_id,
                        session_token=params.get("session_token")
                    )
                
                elif path == "list-standard-operating-procedures" and method == "GET":
                    result = await self.handle_list_standard_operating_procedures_request(
                        user_id=user_id,
                        sop_type=query_params.get("sop_type")
                    )
                
                elif path == "create-workflow" and method == "POST":
                    result = await self.handle_create_workflow_request(
                        workflow_data=params.get("workflow_data"),
                        workflow=params.get("workflow"),
                        name=params.get("name"),
                        description=params.get("description"),
                        sop_id=params.get("sop_id"),
                        options=params.get("options"),
                        user_id=user_id,
                        session_token=params.get("session_token")
                    )
                
                elif path == "list-workflows" and method == "GET":
                    result = await self.handle_list_workflows_request(
                        user_id=user_id
                    )
                
                elif path == "convert-sop-to-workflow" and method == "POST":
                    result = await self.handle_convert_sop_to_workflow_request(
                        sop_id=params.get("sop_id"),
                        sop_file_uuid=params.get("sop_file_uuid"),
                        sop_content=params.get("sop_content"),
                        conversion_type=params.get("conversion_type"),
                        options=params.get("options"),
                        user_id=user_id,
                        session_token=params.get("session_token")
                    )
                
                elif path == "convert-workflow-to-sop" and method == "POST":
                    result = await self.handle_convert_workflow_to_sop_request(
                        workflow_id=params.get("workflow_id"),
                        workflow_file_uuid=params.get("workflow_file_uuid"),
                        workflow=params.get("workflow"),
                        workflow_content=params.get("workflow_content"),
                        conversion_type=params.get("conversion_type"),
                        options=params.get("options"),
                        user_id=user_id,
                        session_token=params.get("session_token")
                    )
                
                # Health Check
                elif path == "health" and method == "GET":
                    result = await self.handle_operations_pillar_health_check_request()
                
                else:
                    result = {
                        "success": False,
                        "error": "Not Found",
                        "message": f"Operations Pillar endpoint not found: {path}"
                    }
            
            # ================================================================
            # BUSINESS OUTCOMES PILLAR ROUTING
            # ================================================================
            elif pillar == "business-outcomes-pillar" or pillar in ["business-outcomes", "business_outcomes"] or pillar_normalized == "business-outcomes":
                # Route to BusinessOutcomesOrchestrator semantic APIs
                if not self.business_outcomes_orchestrator:
                    result = {
                        "success": False,
                        "error": "Service Unavailable",
                        "message": "Business Outcomes Orchestrator is not available. Please try again later."
                    }
                else:
                    # Route to semantic API methods (support both hyphen and underscore formats)
                    if path in ["generate-strategic-roadmap", "generate_strategic_roadmap"] and method == "POST":
                        # Extract pillar_outputs from either direct params or context_data
                        context_data = params.get("context_data", {})
                        pillar_outputs = params.get("pillar_outputs") or context_data.get("pillar_outputs", {})
                        roadmap_options = params.get("roadmap_options") or context_data.get("roadmap_options", {})
                        
                        result = await self.handle_generate_strategic_roadmap_request(
                            pillar_outputs=pillar_outputs,
                            roadmap_options=roadmap_options,
                            user_id=user_id
                        )
                    
                    elif path in ["generate-proof-of-concept-proposal", "generate_proof_of_concept_proposal"] and method == "POST":
                        result = await self.handle_generate_poc_proposal_request(
                            pillar_outputs=params.get("pillar_outputs", {}),
                            proposal_options=params.get("proposal_options", {}),
                            user_id=user_id
                        )
                    
                    elif path in ["get-pillar-summaries", "get_pillar_summaries"] and method == "GET":
                        result = await self.handle_get_pillar_summaries_request(
                            session_id=query_params.get("session_id") or params.get("session_id"),
                            user_id=user_id
                        )
                    
                    elif path in ["get-journey-visualization", "get_journey_visualization"] and method == "GET":
                        result = await self.handle_get_journey_visualization_request(
                            session_id=query_params.get("session_id") or params.get("session_id"),
                            user_id=user_id
                        )
                    
                    elif path == "health" and method == "GET":
                        result = await self.handle_business_outcomes_health_check_request()
                    
                    else:
                        result = {
                            "success": False,
                            "error": "Not Found",
                            "message": f"Business Outcomes Pillar endpoint not found: {path}"
                        }
            
            # ================================================================
            # SESSION PILLAR ROUTING (NEW)
            # ================================================================
            elif pillar == "session" or pillar_normalized == "session":
                if path == "create-user-session" and method == "POST":
                    result = await self.handle_create_user_session_request(
                        user_id=user_id,
                        session_type=params.get("session_type", "mvp"),
                        context=params.get("context")
                    )
                
                elif path.startswith("get-session-details/") and method == "GET":
                    session_id = path.split("/")[1]
                    result = await self.handle_get_session_details_request(
                        session_id=session_id,
                        user_id=user_id
                    )
                
                elif path.startswith("get-session-state/") and method == "GET":
                    session_id = path.split("/")[1]
                    result = await self.handle_get_session_state_request(
                        session_id=session_id,
                        user_id=user_id
                    )
                
                elif path == "health" and method == "GET":
                    result = await self.handle_session_pillar_health_check_request()
                
                else:
                    result = {
                        "success": False,
                        "error": "Not Found",
                        "message": f"Session Pillar endpoint not found: {path}"
                    }
            
            # ================================================================
            # LIAISON AGENTS PILLAR ROUTING (NEW)
            # ================================================================
            elif pillar == "liaison-agents" or pillar_normalized == "liaison-agents":
                if path == "send-message-to-pillar-agent" and method == "POST":
                    result = await self.handle_send_message_to_pillar_agent_request(
                        message=params.get("message"),
                        pillar=params.get("pillar"),
                        session_id=params.get("session_id"),
                        conversation_id=params.get("conversation_id"),
                        user_id=user_id,
                        session_token=params.get("session_token")
                    )
                
                elif path.startswith("get-pillar-conversation-history/") and method == "GET":
                    # Path format: get-pillar-conversation-history/{session_id}/{pillar}
                    path_parts = path.split("/")
                    if len(path_parts) >= 3:
                        session_id = path_parts[1]
                        pillar = path_parts[2]
                        result = await self.handle_get_pillar_conversation_history_request(
                            session_id=session_id,
                            pillar=pillar,
                            user_id=user_id
                        )
                    else:
                        result = {
                            "success": False,
                            "error": "Invalid Path",
                            "message": "Path must be: get-pillar-conversation-history/{session_id}/{pillar}"
                        }
                
                elif path == "health" and method == "GET":
                    result = await self.handle_liaison_agents_pillar_health_check_request()
                
                else:
                    result = {
                        "success": False,
                        "error": "Not Found",
                        "message": f"Liaison Agents Pillar endpoint not found: {path}"
                    }
            
            # ================================================================
            # UNKNOWN PILLAR
            # ================================================================
            else:
                result = {
                    "success": False,
                    "error": "Not Found",
                    "message": f"Unknown pillar: {pillar}"
                }
            
            # Transform for frontend (if result exists)
            if result:
                frontend_response = await self.transform_for_frontend(result)
                
                # Log request via Librarian
                try:
                    await self.store_document(
                        document_data={
                            "request": request,
                            "response": frontend_response,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        metadata={
                            "type": "api_request_log",
                            "endpoint": endpoint,
                            "method": method,
                            "pillar": pillar,
                            "path": path
                        }
                    )
                except Exception as log_error:
                    self.logger.warning(f"⚠️  Failed to log request: {log_error}")
                
                # Record health metric
                await self.record_health_metric("route_frontend_request_success", 1.0, {"endpoint": endpoint, "pillar": pillar})
                
                # ⭐ NEW: Track metrics for old routing (Phase 4)
                if self.routing_monitoring_enabled:
                    elapsed_ms = (datetime.utcnow() - start_time_old).total_seconds() * 1000
                    self.routing_metrics["old_routing"]["requests"] += 1
                    self.routing_metrics["old_routing"]["total_time_ms"] += elapsed_ms
                    if frontend_response.get("success") is not False:
                        self.routing_metrics["old_routing"]["successes"] += 1
                    else:
                        self.routing_metrics["old_routing"]["errors"] += 1
                    # Update average
                    if self.routing_metrics["old_routing"]["requests"] > 0:
                        self.routing_metrics["old_routing"]["avg_time_ms"] = (
                            self.routing_metrics["old_routing"]["total_time_ms"] / 
                            self.routing_metrics["old_routing"]["requests"]
                        )
                    self.logger.debug(f"📊 Old routing: {endpoint} ({elapsed_ms:.2f}ms)")
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("route_frontend_request_complete", success=True)
                
                return frontend_response
            
            # No handler found
            await self.record_health_metric("route_frontend_request_no_handler", 1.0, {"endpoint": endpoint})
            
            # Track metrics for old routing (error case)
            if self.routing_monitoring_enabled:
                elapsed_ms = (datetime.utcnow() - start_time_old).total_seconds() * 1000
                self.routing_metrics["old_routing"]["requests"] += 1
                self.routing_metrics["old_routing"]["errors"] += 1
                self.routing_metrics["old_routing"]["total_time_ms"] += elapsed_ms
            
            await self.log_operation_with_telemetry("route_frontend_request_complete", success=False)
            
            return {
                "success": False,
                "error": "No Handler",
                "message": f"No handler found for: {endpoint}"
            }
            
        except Exception as e:
            # Track metrics for old routing (exception case)
            if self.routing_monitoring_enabled:
                elapsed_ms = (datetime.utcnow() - start_time_old).total_seconds() * 1000
                self.routing_metrics["old_routing"]["requests"] += 1
                self.routing_metrics["old_routing"]["errors"] += 1
                self.routing_metrics["old_routing"]["total_time_ms"] += elapsed_ms
            
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "route_frontend_request")
            self.logger.error(f"❌ Route frontend request failed: {e}")
            await self.log_operation_with_telemetry("route_frontend_request_complete", success=False)
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": "Internal Server Error",
                "message": str(e)
            }
    
    async def get_frontend_apis(self) -> Dict[str, Any]:
        """
        Get all exposed frontend APIs (SOA API).
        
        Returns:
            Dictionary of exposed APIs
        """
        return {
            "success": True,
            "apis": {
                endpoint: {
                    "api_name": info["api_name"],
                    "exposed_at": info["exposed_at"]
                }
                for endpoint, info in self.registered_apis.items()
            },
            "total_apis": len(self.registered_apis)
        }
    
    # ========================================================================
    # REQUEST HANDLERS (Compose Business Enablement Orchestrators)
    # ========================================================================
    
    async def handle_document_analysis_request(
        self,
        document_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle document analysis request (Frontend API → ContentAnalysisOrchestrator).
        
        Args:
            document_id: ID of document to analyze
            options: Optional analysis options
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.content_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Content analysis service not available"
                }
            
            # Call Business Enablement orchestrator
            result = await self.content_orchestrator.analyze_document(document_id)
            
            self.logger.info(f"✅ Document analysis complete: {document_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Document analysis request failed: {e}")
            return {
                "success": False,
                "error": "Analysis Failed",
                "message": str(e)
            }
    
    async def handle_insights_request(
        self,
        data_id: str,
        insight_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Handle insights generation request (Frontend API → InsightsOrchestrator).
        
        Args:
            data_id: ID of data to analyze
            insight_types: Optional list of insight types to generate
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights service not available"
                }
            
            # Call Business Enablement orchestrator
            result = await self.insights_orchestrator.generate_insights(
                data_id=data_id,
                insight_types=insight_types or []
            )
            
            self.logger.info(f"✅ Insights generated: {data_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Insights request failed: {e}")
            return {
                "success": False,
                "error": "Insights Failed",
                "message": str(e)
            }
    
    async def handle_operations_request(
        self,
        process_id: str,
        operation_type: str
    ) -> Dict[str, Any]:
        """
        Handle operations request (Frontend API → OperationsOrchestrator).
        
        Args:
            process_id: ID of process to optimize
            operation_type: Type of operation (optimize, build_sop, etc.)
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.operations_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Operations service not available"
                }
            
            # Call Business Enablement orchestrator
            result = await self.operations_orchestrator.execute(
                request={
                    "action": operation_type,
                    "params": {"process_id": process_id}
                }
            )
            
            self.logger.info(f"✅ Operation complete: {operation_type} on {process_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Operations request failed: {e}")
            return {
                "success": False,
                "error": "Operation Failed",
                "message": str(e)
            }
    
    async def handle_data_operations_request(
        self,
        data_id: str,
        operation_type: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle data operations request (Frontend API → DataOperationsOrchestrator).
        
        Args:
            data_id: ID of data to process
            operation_type: Type of operation (transform, validate, reconcile)
            options: Optional operation options
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.data_operations_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Data operations service not available"
                }
            
            # Call Business Enablement orchestrator
            result = await self.data_operations_orchestrator.execute(
                request={
                    "action": operation_type,
                    "params": {"data_id": data_id, **( options or {})}
                }
            )
            
            self.logger.info(f"✅ Data operation complete: {operation_type} on {data_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Data operations request failed: {e}")
            return {
                "success": False,
                "error": "Data Operation Failed",
                "message": str(e)
            }
    
    # ========================================================================
    # CHAT HANDLERS (Frontend API → ChatService)
    # ========================================================================
    
    async def handle_guide_chat_request(
        self,
        message: str,
        conversation_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Handle guide chat request (Frontend API → ChatService → GuideAgent).
        
        Implements: MVP requirement for Guide Agent in persistent chat panel.
        
        Args:
            message: User's message
            conversation_id: Conversation ID
            user_id: User ID
        
        Returns:
            Frontend-ready chat response
        """
        try:
            if not self.chat_service:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Chat service not available"
                }
            
            # Send message to Guide Agent via ChatService
            result = await self.chat_service.send_message_to_guide(
                message=message,
                conversation_id=conversation_id,
                user_id=user_id
            )
            
            self.logger.info(f"✅ Guide chat message sent: {conversation_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Guide chat request failed: {e}")
            return {
                "success": False,
                "error": "Chat Failed",
                "message": str(e)
            }
    
    async def handle_liaison_chat_request(
        self,
        message: str,
        pillar: str,
        conversation_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Handle liaison chat request (Frontend API → ChatService → Liaison Agent).
        
        Implements: MVP requirement for pillar-specific liaison agents in chat panel.
        
        Args:
            message: User's message
            pillar: Pillar name (content, insights, operations, business_outcomes)
            conversation_id: Conversation ID
            user_id: User ID
        
        Returns:
            Frontend-ready chat response
        """
        try:
            if not self.chat_service:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Chat service not available"
                }
            
            # Send message to Liaison Agent via ChatService
            result = await self.chat_service.send_message_to_liaison(
                message=message,
                pillar=pillar,
                conversation_id=conversation_id,
                user_id=user_id
            )
            
            self.logger.info(f"✅ Liaison chat message sent: {pillar} - {conversation_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Liaison chat request failed: {e}")
            return {
                "success": False,
                "error": "Chat Failed",
                "message": str(e)
            }
    
    async def handle_create_conversation_request(
        self,
        user_id: str,
        initial_agent: str = "guide"
    ) -> Dict[str, Any]:
        """
        Handle create conversation request (Frontend API → ChatService).
        
        Args:
            user_id: User ID
            initial_agent: Initial agent (guide, content, insights, operations, business_outcomes)
        
        Returns:
            New conversation details
        """
        try:
            if not self.chat_service:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Chat service not available"
                }
            
            result = await self.chat_service.create_conversation(
                user_id=user_id,
                initial_agent=initial_agent
            )
            
            self.logger.info(f"✅ Conversation created: {result.get('conversation_id')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Create conversation request failed: {e}")
            return {
                "success": False,
                "error": "Conversation Creation Failed",
                "message": str(e)
            }
    
    async def handle_conversation_history_request(
        self,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Handle conversation history request (Frontend API → ChatService).
        
        Args:
            conversation_id: Conversation ID
        
        Returns:
            Conversation history
        """
        try:
            if not self.chat_service:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Chat service not available"
                }
            
            result = await self.chat_service.get_conversation_history(
                conversation_id=conversation_id
            )
            
            self.logger.info(f"✅ Conversation history retrieved: {conversation_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Conversation history request failed: {e}")
            return {
                "success": False,
                "error": "History Retrieval Failed",
                "message": str(e)
            }
    
    # ========================================================================
    # INSIGHTS PILLAR SEMANTIC API HANDLERS
    # ========================================================================
    
    async def handle_analyze_content_for_insights_semantic_request(
        self,
        source_type: str,
        file_id: Optional[str] = None,
        content_metadata_id: Optional[str] = None,
        content_type: str = "structured",
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle analyze content for insights request (Frontend API → InsightsOrchestrator).
        Semantic API: Primary analysis endpoint matching semantic router signature.
        
        Args:
            source_type: 'file' or 'content_metadata'
            file_id: File identifier (if source_type='file')
            content_metadata_id: Content metadata ID (if source_type='content_metadata')
            content_type: 'structured', 'unstructured', or 'hybrid'
            analysis_options: Optional configuration
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            # Call Business Enablement orchestrator (domain capability)
            result = await self.insights_orchestrator.analyze_content_for_insights(
                source_type=source_type,
                file_id=file_id,
                content_metadata_id=content_metadata_id,
                content_type=content_type,
                analysis_options=analysis_options
            )
            
            self.logger.info(f"✅ Content analyzed for insights: source_type={source_type}, content_type={content_type}")
            
            # Transform for frontend (REST layer)
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Analyze content for insights failed: {e}")
            return {
                "success": False,
                "error": "Analysis Failed",
                "message": str(e)
            }
    
    async def handle_analyze_content_for_insights_request(
        self,
        content_metadata_ids: List[str],
        analysis_type: str = "auto",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle analyze content request (Frontend API → InsightsOrchestrator).
        Semantic API: Analyze content metadata for insights.
        
        Args:
            content_metadata_ids: List of content metadata IDs to analyze
            analysis_type: Type of analysis (auto, structured, unstructured, hybrid)
            user_id: Optional user ID
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            # Call Business Enablement orchestrator (domain capability)
            result = await self.insights_orchestrator.analyze_content(
                content_metadata_ids=content_metadata_ids,
                analysis_type=analysis_type,
                user_id=user_id
            )
            
            self.logger.info(f"✅ Content analyzed for insights: {len(content_metadata_ids)} files")
            
            # Transform for frontend (REST layer)
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Analyze content for insights failed: {e}")
            return {
                "success": False,
                "error": "Analysis Failed",
                "message": str(e)
            }
    
    async def handle_query_insights_analysis_request(
        self,
        query: str,
        analysis_id: str,
        query_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        Handle query analysis request (Frontend API → InsightsOrchestrator).
        Semantic API: NLP query on analysis results.
        
        Args:
            query: Natural language query
            analysis_id: ID of analysis to query
            query_type: Type of query result (table, chart, summary, auto)
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            # Call orchestrator
            result = await self.insights_orchestrator.query_analysis_results(
                query=query,
                analysis_id=analysis_id,
                query_type=query_type
            )
            
            self.logger.info(f"✅ Analysis queried: {query} on {analysis_id}")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Query insights analysis failed: {e}")
            return {
                "success": False,
                "error": "Query Failed",
                "message": str(e)
            }
    
    async def handle_get_available_content_metadata_request(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle get available content metadata request.
        Semantic API: List content available for analysis.
        
        Args:
            user_id: Optional user ID
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            result = await self.insights_orchestrator.get_available_content_metadata(
                user_id=user_id
            )
            
            self.logger.info(f"✅ Available content metadata retrieved")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Get available content metadata failed: {e}")
            return {
                "success": False,
                "error": "Retrieval Failed",
                "message": str(e)
            }
    
    async def handle_validate_content_metadata_for_insights_request(
        self,
        content_metadata_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Handle validate content metadata request.
        Semantic API: Validate content metadata for insights analysis.
        
        Args:
            content_metadata_ids: List of content metadata IDs to validate
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            result = await self.insights_orchestrator.validate_content_metadata(
                content_metadata_ids=content_metadata_ids
            )
            
            self.logger.info(f"✅ Content metadata validated: {len(content_metadata_ids)} items")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Validate content metadata failed: {e}")
            return {
                "success": False,
                "error": "Validation Failed",
                "message": str(e)
            }
    
    async def handle_get_insights_analysis_results_request(
        self,
        analysis_id: str
    ) -> Dict[str, Any]:
        """
        Handle get analysis results request.
        Semantic API: Get complete analysis results.
        
        Args:
            analysis_id: Analysis ID
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            result = await self.insights_orchestrator.get_analysis_results(
                analysis_id=analysis_id
            )
            
            self.logger.info(f"✅ Analysis results retrieved: {analysis_id}")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Get analysis results failed: {e}")
            return {
                "success": False,
                "error": "Retrieval Failed",
                "message": str(e)
            }
    
    async def handle_get_insights_analysis_visualizations_request(
        self,
        analysis_id: str
    ) -> Dict[str, Any]:
        """
        Handle get analysis visualizations request.
        Semantic API: Get visualizations for analysis.
        
        Args:
            analysis_id: Analysis ID
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            result = await self.insights_orchestrator.get_analysis_visualizations(
                analysis_id=analysis_id
            )
            
            self.logger.info(f"✅ Analysis visualizations retrieved: {analysis_id}")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Get analysis visualizations failed: {e}")
            return {
                "success": False,
                "error": "Retrieval Failed",
                "message": str(e)
            }
    
    async def handle_list_user_insights_analyses_request(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle list user analyses request.
        Semantic API: List all analyses for user.
        
        Args:
            user_id: Optional user ID
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            result = await self.insights_orchestrator.list_user_analyses(
                user_id=user_id
            )
            
            self.logger.info(f"✅ User analyses listed")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ List user analyses failed: {e}")
            return {
                "success": False,
                "error": "Listing Failed",
                "message": str(e)
            }
    
    async def handle_get_insights_pillar_summary_request(
        self,
        analysis_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle get pillar summary request.
        Semantic API: Get Insights Pillar summary for Business Outcomes.
        
        Args:
            analysis_id: Optional analysis ID (if None, returns most recent)
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            result = await self.insights_orchestrator.get_pillar_summary(
                analysis_id=analysis_id
            )
            
            self.logger.info(f"✅ Insights pillar summary retrieved")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Get pillar summary failed: {e}")
            return {
                "success": False,
                "error": "Summary Failed",
                "message": str(e)
            }
    
    async def handle_insights_pillar_health_check_request(self) -> Dict[str, Any]:
        """
        Handle insights pillar health check request.
        Semantic API: Check if Insights Pillar is available.
        
        Returns:
            Health status
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "status": "unavailable",
                    "pillar": "insights",
                    "message": "Insights orchestrator not available",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Call orchestrator health check
            result = await self.insights_orchestrator.health_check()
            
            return {
                "status": "healthy",
                "pillar": "insights",
                "orchestrator_status": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Insights health check failed: {e}")
            return {
                "status": "unhealthy",
                "pillar": "insights",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ========================================================================
    # CONTENT PILLAR HANDLERS (Semantic API)
    # ========================================================================
    
    async def handle_upload_file_request(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        user_id: str,
        session_id: Optional[str] = None,
        copybook_data: Optional[bytes] = None,
        copybook_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle file upload request (Content Pillar).
        
        Args:
            file_data: File binary data
            filename: Original filename
            content_type: MIME type
            user_id: User identifier
            session_id: Optional session ID
            copybook_data: Optional copybook file data
            copybook_filename: Optional copybook filename
        
        Returns:
            Upload result with file metadata
        """
        try:
            # Validate required parameters
            if file_data is None:
                self.logger.error("❌ File upload failed: file_data is None")
                return {
                    "success": False,
                    "error": "file_data is required but was not provided"
                }
            
            if not filename:
                self.logger.error("❌ File upload failed: filename is None or empty")
                return {
                    "success": False,
                    "error": "filename is required but was not provided"
                }
            
            self.logger.info(f"📤 Content Pillar: Upload file request: {filename} ({len(file_data)} bytes)")
            
            # Get Content Analysis Orchestrator (try direct attribute first, then dictionary)
            content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentAnalysisOrchestrator")
            
            # If still not available, try to discover orchestrators lazily
            if not content_orchestrator:
                self.logger.warning("⚠️ ContentAnalysisOrchestrator not found, attempting lazy discovery...")
                await self._discover_orchestrators()
                content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentAnalysisOrchestrator")
            
            if not content_orchestrator:
                self.logger.error("❌ ContentAnalysisOrchestrator not available")
                return {
                    "success": False,
                    "error": "Content Analysis Orchestrator not available"
                }
            
            # Call orchestrator's upload method
            result = await content_orchestrator.upload_file(
                file_data=file_data,
                filename=filename,
                file_type=content_type,
                user_id=user_id,
                session_id=session_id
            )
            
            # Handle copybook upload if provided
            if copybook_data and copybook_filename:
                self.logger.info(f"📎 Uploading copybook: {copybook_filename}")
                copybook_result = await content_orchestrator.upload_file(
                    file_data=copybook_data,
                    filename=copybook_filename,
                    file_type="text/plain",
                    user_id=user_id,
                    session_id=session_id
                )
                
                if copybook_result.get("success"):
                    result["copybook_file_id"] = copybook_result.get("file_id")
            
            return result
            
        except Exception as e:
            # Log error without exc_info to avoid LogRecord conflict with TraceContextFormatter
            # The exception details are already in the message
            self.logger.error(f"❌ Upload file request failed: {e}", exc_info=False)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_process_file_request(
        self,
        file_id: str,
        user_id: str,
        copybook_file_id: Optional[str] = None,
        processing_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle file processing request (Content Pillar).
        
        Args:
            file_id: File UUID
            user_id: User identifier
            copybook_file_id: Optional copybook file UUID
            processing_options: Optional processing options
        
        Returns:
            Processing result with parsed data and metadata
        """
        try:
            self.logger.info(f"⚙️ Content Pillar: Process file request: {file_id}")
            
            # Get Content Analysis Orchestrator (try direct attribute first, then dictionary)
            content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentAnalysisOrchestrator")
            
            # If still not available, try to discover orchestrators lazily
            if not content_orchestrator:
                self.logger.warning("⚠️ ContentAnalysisOrchestrator not found, attempting lazy discovery...")
                await self._discover_orchestrators()
                content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentAnalysisOrchestrator")
            
            if not content_orchestrator:
                self.logger.error("❌ ContentAnalysisOrchestrator not available")
                return {
                    "success": False,
                    "error": "Content Analysis Orchestrator not available"
                }
            
            # Call orchestrator's process method
            result = await content_orchestrator.process_file(
                file_id=file_id,
                user_id=user_id,
                copybook_file_id=copybook_file_id,
                processing_options=processing_options or {}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Process file request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_list_uploaded_files_request(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Handle list uploaded files request (Content Pillar).
        
        Args:
            user_id: User identifier
        
        Returns:
            List of uploaded files
        """
        try:
            self.logger.info(f"📋 Content Pillar: List uploaded files request for user: {user_id}")
            
            # Get Content Analysis Orchestrator (try direct attribute first, then dictionary)
            content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentAnalysisOrchestrator")
            
            # If still not available, try to discover orchestrators lazily
            if not content_orchestrator:
                self.logger.warning("⚠️ ContentAnalysisOrchestrator not found, attempting lazy discovery...")
                await self._discover_orchestrators()
                content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentAnalysisOrchestrator")
            
            if not content_orchestrator:
                self.logger.error("❌ ContentAnalysisOrchestrator not available")
                return {
                    "success": False,
                    "files": [],
                    "count": 0,
                    "error": "Content Analysis Orchestrator not available"
                }
            
            # Call orchestrator's list files method
            result = await content_orchestrator.list_uploaded_files(user_id=user_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ List uploaded files request failed: {e}")
            return {
                "success": False,
                "files": [],
                "count": 0,
                "error": str(e)
            }
    
    async def handle_get_file_details_request(
        self,
        file_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Handle get file details request (Content Pillar).
        
        Args:
            file_id: File UUID
            user_id: User identifier
        
        Returns:
            File details
        """
        try:
            self.logger.info(f"🔍 Content Pillar: Get file details request: {file_id}")
            
            # Get Content Analysis Orchestrator (try direct attribute first, then dictionary)
            content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentAnalysisOrchestrator")
            
            # If still not available, try to discover orchestrators lazily
            if not content_orchestrator:
                self.logger.warning("⚠️ ContentAnalysisOrchestrator not found, attempting lazy discovery...")
                await self._discover_orchestrators()
                content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentAnalysisOrchestrator")
            
            if not content_orchestrator:
                self.logger.error("❌ ContentAnalysisOrchestrator not available")
                return {
                    "success": False,
                    "file": None,
                    "error": "Content Analysis Orchestrator not available"
                }
            
            # Call orchestrator's get file details method
            result = await content_orchestrator.get_file_details(
                file_id=file_id,
                user_id=user_id
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Get file details request failed: {e}")
            return {
                "success": False,
                "file": None,
                "error": str(e)
            }
    
    async def _lazy_discover_orchestrators_if_needed(self):
        """Lazy-discover orchestrators if they weren't available during initialization."""
        if not self.orchestrators:
            self.logger.info("🔄 Orchestrators not available, attempting lazy discovery...")
            await self._discover_orchestrators()
    
    async def handle_content_pillar_health_check_request(self) -> Dict[str, Any]:
        """
        Handle content pillar health check request.
        
        Returns:
            Health status
        """
        try:
            self.logger.info("🏥 Content Pillar: Health check request")
            
            # Lazy-discover orchestrators if needed
            await self._lazy_discover_orchestrators_if_needed()
            
            # Get Content Analysis Orchestrator
            content_orchestrator = self.orchestrators.get("ContentAnalysisOrchestrator")
            if not content_orchestrator:
                return {
                    "status": "unhealthy",
                    "pillar": "content",
                    "error": "ContentAnalysisOrchestrator not available",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Call orchestrator's health check
            result = await content_orchestrator.health_check()
            
            return {
                "status": "healthy",
                "pillar": "content",
                "orchestrator_status": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Content health check failed: {e}")
            return {
                "status": "unhealthy",
                "pillar": "content",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ========================================================================
    # OPERATIONS PILLAR HANDLERS (Semantic API)
    # ========================================================================
    
    async def handle_get_session_elements_request(
        self,
        session_token: str
    ) -> Dict[str, Any]:
        """
        Handle get session elements request (Operations Pillar).
        
        Args:
            session_token: Session identifier
        
        Returns:
            Session state with SOP and Workflow elements
        """
        try:
            self.logger.info(f"📋 Operations Pillar: Get session elements request")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "valid": False,
                    "action": "error",
                    "missing": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.get_session_elements(
                session_token=session_token
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Get session elements request failed: {e}")
            return {
                "valid": False,
                "action": "error",
                "missing": str(e)
            }
    
    async def handle_clear_session_elements_request(
        self,
        session_token: str
    ) -> Dict[str, Any]:
        """
        Handle clear session elements request (Operations Pillar).
        
        Args:
            session_token: Session identifier
        
        Returns:
            Success status
        """
        try:
            self.logger.info(f"🗑️ Operations Pillar: Clear session elements request")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "message": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.clear_session_elements(
                session_token=session_token
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Clear session elements request failed: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def handle_generate_workflow_from_sop_request(
        self,
        session_token: str,
        sop_file_uuid: str
    ) -> Dict[str, Any]:
        """
        Handle generate workflow from SOP request (Operations Pillar).
        
        Args:
            session_token: Session identifier
            sop_file_uuid: SOP file UUID
        
        Returns:
            Generated workflow
        """
        try:
            self.logger.info(f"📄➡️📊 Operations Pillar: Generate workflow from SOP: {sop_file_uuid}")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.generate_workflow_from_sop(
                session_token=session_token,
                sop_file_uuid=sop_file_uuid
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Generate workflow from SOP request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_generate_sop_from_workflow_request(
        self,
        session_token: str,
        workflow_file_uuid: str
    ) -> Dict[str, Any]:
        """
        Handle generate SOP from workflow request (Operations Pillar).
        
        Args:
            session_token: Session identifier
            workflow_file_uuid: Workflow file UUID
        
        Returns:
            Generated SOP
        """
        try:
            self.logger.info(f"📊➡️📄 Operations Pillar: Generate SOP from workflow: {workflow_file_uuid}")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.generate_sop_from_workflow(
                session_token=session_token,
                workflow_file_uuid=workflow_file_uuid
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Generate SOP from workflow request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_analyze_file_request(
        self,
        session_token: str,
        input_file_uuid: str,
        output_type: str
    ) -> Dict[str, Any]:
        """
        Handle analyze file request (Operations Pillar).
        
        Args:
            session_token: Session identifier
            input_file_uuid: Input file UUID
            output_type: "workflow" or "sop"
        
        Returns:
            Analysis result
        """
        try:
            self.logger.info(f"🔍 Operations Pillar: Analyze file: {input_file_uuid} → {output_type}")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.analyze_file(
                session_token=session_token,
                input_file_uuid=input_file_uuid,
                output_type=output_type
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Analyze file request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_analyze_coexistence_files_request(
        self,
        session_token: str
    ) -> Dict[str, Any]:
        """
        Handle analyze coexistence (file-based) request (Operations Pillar).
        
        Args:
            session_token: Session identifier (contains SOP and Workflow)
        
        Returns:
            Coexistence analysis
        """
        try:
            self.logger.info(f"🔄 Operations Pillar: Analyze coexistence (files)")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.analyze_coexistence_files(
                session_token=session_token
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Analyze coexistence files request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_analyze_coexistence_content_request(
        self,
        session_token: str,
        sop_content: str,
        workflow_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle analyze coexistence (content-based) request (Operations Pillar).
        
        Args:
            session_token: Session identifier
            sop_content: SOP text content
            workflow_content: Workflow object
        
        Returns:
            Coexistence analysis
        """
        try:
            self.logger.info(f"🔄 Operations Pillar: Analyze coexistence (content)")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.analyze_coexistence_content(
                session_token=session_token,
                sop_content=sop_content,
                workflow_content=workflow_content
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Analyze coexistence content request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_start_wizard_request(self) -> Dict[str, Any]:
        """
        Handle start wizard request (Operations Pillar).
        
        Returns:
            Wizard session info
        """
        try:
            self.logger.info(f"🧙 Operations Pillar: Start wizard")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.start_wizard()
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Start wizard request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_wizard_chat_request(
        self,
        session_token: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Handle wizard chat request (Operations Pillar).
        
        Args:
            session_token: Wizard session token
            user_message: User's message
        
        Returns:
            Wizard response
        """
        try:
            self.logger.info(f"💬 Operations Pillar: Wizard chat")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.wizard_chat(
                session_token=session_token,
                user_message=user_message
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Wizard chat request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_wizard_publish_request(
        self,
        session_token: str
    ) -> Dict[str, Any]:
        """
        Handle wizard publish request (Operations Pillar).
        
        Args:
            session_token: Wizard session token
        
        Returns:
            Published SOP
        """
        try:
            self.logger.info(f"📤 Operations Pillar: Wizard publish")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.wizard_publish(
                session_token=session_token
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Wizard publish request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_save_blueprint_request(
        self,
        blueprint: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Handle save blueprint request (Operations Pillar).
        
        Args:
            blueprint: Blueprint object
            user_id: User identifier
        
        Returns:
            Blueprint ID
        """
        try:
            self.logger.info(f"💾 Operations Pillar: Save blueprint for user: {user_id}")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.save_blueprint(
                blueprint=blueprint,
                user_id=user_id
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Save blueprint request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_process_operations_query_request(
        self,
        session_id: str,
        query: str,
        file_url: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle process operations query request (Operations Pillar).
        
        Args:
            session_id: Session identifier
            query: User query
            file_url: Optional file URL
            context: Optional context
        
        Returns:
            Query response
        """
        try:
            self.logger.info(f"❓ Operations Pillar: Process query: {query}")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.process_query(
                session_id=session_id,
                query=query,
                file_url=file_url,
                context=context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Process operations query request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_process_operations_conversation_request(
        self,
        session_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle process operations conversation request (Operations Pillar).
        
        Args:
            session_id: Session identifier
            message: User message
            context: Optional context
        
        Returns:
            Conversation response
        """
        try:
            self.logger.info(f"💬 Operations Pillar: Process conversation")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.process_conversation(
                session_id=session_id,
                message=message,
                context=context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Process operations conversation request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_get_operations_conversation_context_request(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Handle get operations conversation context request (Operations Pillar).
        
        Args:
            session_id: Session identifier
        
        Returns:
            Conversation context
        """
        try:
            self.logger.info(f"📝 Operations Pillar: Get conversation context: {session_id}")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.get_conversation_context(
                session_id=session_id
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Get conversation context request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_analyze_operations_intent_request(
        self,
        query: str
    ) -> Dict[str, Any]:
        """
        Handle analyze operations intent request (Operations Pillar).
        
        Args:
            query: User query
        
        Returns:
            Intent analysis
        """
        try:
            self.logger.info(f"🔍 Operations Pillar: Analyze intent: {query}")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.analyze_intent(
                query=query
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Analyze operations intent request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # OPERATIONS PILLAR SEMANTIC API HANDLERS (NEW)
    # ========================================================================
    
    async def handle_create_standard_operating_procedure_request(
        self,
        sop_content: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        sop_type: Optional[str] = None,
        file_ids: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous",
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle create standard operating procedure request (Operations Pillar).
        
        Args:
            sop_content: SOP content
            description: SOP description
            sop_type: Type of SOP (process, procedure, checklist)
            file_ids: Optional file IDs to reference
            options: Additional options
            user_id: User identifier
            session_token: Optional session token
        
        Returns:
            SOP creation result
        """
        try:
            self.logger.info(f"📋 Operations Pillar: Create SOP request")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available",
                    "message": "OperationsOrchestrator is not available"
                }
            
            # For now, if we have workflow_content, convert workflow to SOP
            # Otherwise, create a placeholder SOP
            # TODO: Implement proper SOP creation in OperationsOrchestrator
            if sop_content:
                result = {
                    "success": True,
                    "sop_id": str(uuid.uuid4()),
                    "sop": sop_content,
                    "message": "SOP created successfully (placeholder implementation)"
                }
            else:
                result = {
                    "success": True,
                    "sop_id": str(uuid.uuid4()),
                    "sop": {
                        "description": description or "New SOP",
                        "sop_type": sop_type or "process",
                        "content": {}
                    },
                    "message": "SOP created successfully (placeholder implementation)"
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Create SOP request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create SOP: {str(e)}"
            }
    
    async def handle_list_standard_operating_procedures_request(
        self,
        user_id: str = "anonymous",
        sop_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle list standard operating procedures request (Operations Pillar).
        
        Args:
            user_id: User identifier
            sop_type: Optional filter by SOP type
        
        Returns:
            List of SOPs
        """
        try:
            self.logger.info(f"📋 Operations Pillar: List SOPs request")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available",
                    "message": "OperationsOrchestrator is not available"
                }
            
            # TODO: Implement proper SOP listing in OperationsOrchestrator
            # For now, return empty list
            result = {
                "success": True,
                "standard_operating_procedures": [],
                "sops": [],
                "message": "List SOPs endpoint - to be implemented"
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ List SOPs request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list SOPs: {str(e)}"
            }
    
    async def handle_create_workflow_request(
        self,
        workflow_data: Optional[Dict[str, Any]] = None,
        workflow: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        sop_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous",
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle create workflow request (Operations Pillar).
        
        Args:
            workflow_data: Workflow data
            workflow: Workflow definition
            name: Workflow name
            description: Workflow description
            sop_id: Optional SOP ID to convert from
            options: Additional options
            user_id: User identifier
            session_token: Optional session token
        
        Returns:
            Workflow creation result
        """
        try:
            self.logger.info(f"📋 Operations Pillar: Create workflow request")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available",
                    "message": "OperationsOrchestrator is not available"
                }
            
            # If sop_id is provided, convert SOP to workflow
            if sop_id:
                result = await operations_orchestrator.generate_workflow_from_sop(
                    session_token=session_token,
                    sop_file_uuid=sop_id,
                    sop_content=None
                )
                return result
            
            # Otherwise, create a new workflow
            # TODO: Implement proper workflow creation in OperationsOrchestrator
            workflow_content = workflow_data or workflow or {}
            result = {
                "success": True,
                "workflow_id": str(uuid.uuid4()),
                "workflow": workflow_content,
                "message": "Workflow created successfully (placeholder implementation)"
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Create workflow request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create workflow: {str(e)}"
            }
    
    async def handle_list_workflows_request(
        self,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Handle list workflows request (Operations Pillar).
        
        Args:
            user_id: User identifier
        
        Returns:
            List of workflows
        """
        try:
            self.logger.info(f"📋 Operations Pillar: List workflows request")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available",
                    "message": "OperationsOrchestrator is not available"
                }
            
            # TODO: Implement proper workflow listing in OperationsOrchestrator
            # For now, return empty list
            result = {
                "success": True,
                "workflows": [],
                "message": "List workflows endpoint - to be implemented"
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ List workflows request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list workflows: {str(e)}"
            }
    
    async def handle_convert_sop_to_workflow_request(
        self,
        sop_id: Optional[str] = None,
        sop_file_uuid: Optional[str] = None,
        sop_content: Optional[Dict[str, Any]] = None,
        conversion_type: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous",
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle convert SOP to workflow request (Operations Pillar).
        
        Args:
            sop_id: SOP ID
            sop_file_uuid: SOP file UUID
            sop_content: SOP content
            conversion_type: Conversion type
            options: Additional options
            user_id: User identifier
            session_token: Optional session token
        
        Returns:
            Workflow conversion result
        """
        try:
            self.logger.info(f"📋 Operations Pillar: Convert SOP to workflow request")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available",
                    "message": "OperationsOrchestrator is not available"
                }
            
            # Call orchestrator's conversion method
            result = await operations_orchestrator.generate_workflow_from_sop(
                session_token=session_token,
                sop_file_uuid=sop_id or sop_file_uuid,
                sop_content=sop_content
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Convert SOP to workflow request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to convert SOP to workflow: {str(e)}"
            }
    
    async def handle_convert_workflow_to_sop_request(
        self,
        workflow_id: Optional[str] = None,
        workflow_file_uuid: Optional[str] = None,
        workflow: Optional[Dict[str, Any]] = None,
        workflow_content: Optional[Dict[str, Any]] = None,
        conversion_type: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous",
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle convert workflow to SOP request (Operations Pillar).
        
        Args:
            workflow_id: Workflow ID
            workflow_file_uuid: Workflow file UUID
            workflow: Workflow definition
            workflow_content: Workflow content
            conversion_type: Conversion type
            options: Additional options
            user_id: User identifier
            session_token: Optional session token
        
        Returns:
            SOP conversion result
        """
        try:
            self.logger.info(f"📋 Operations Pillar: Convert workflow to SOP request")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available",
                    "message": "OperationsOrchestrator is not available"
                }
            
            # Call orchestrator's conversion method
            result = await operations_orchestrator.generate_sop_from_workflow(
                session_token=session_token,
                workflow_file_uuid=workflow_id or workflow_file_uuid,
                workflow_content=workflow_content or workflow
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Convert workflow to SOP request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to convert workflow to SOP: {str(e)}"
            }
    
    async def handle_operations_pillar_health_check_request(self) -> Dict[str, Any]:
        """
        Handle operations pillar health check request.
        
        Returns:
            Health status
        """
        try:
            self.logger.info("🏥 Operations Pillar: Health check request")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                return {
                    "status": "unhealthy",
                    "pillar": "operations",
                    "error": "OperationsOrchestrator not available",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Call orchestrator's health check
            result = await operations_orchestrator.health_check()
            
            return {
                "status": "healthy",
                "pillar": "operations",
                "orchestrator_status": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Operations health check failed: {e}")
            return {
                "status": "unhealthy",
                "pillar": "operations",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ========================================================================
    # SESSION PILLAR HANDLERS (NEW)
    # ========================================================================
    
    async def handle_create_user_session_request(
        self,
        user_id: str,
        session_type: str = "mvp",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle create user session request (Session Pillar).
        
        Args:
            user_id: User identifier
            session_type: Type of session (mvp, etc.)
            context: Optional context
        
        Returns:
            Session creation result
        """
        try:
            self.logger.info(f"📝 Session Pillar: Create user session request for user {user_id}")
            
            # Try to get SessionManagerService from Experience Foundation
            session_manager = None
            try:
                if self.curator:
                    session_manager = await self.curator.get_service("SessionManagerService")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not get SessionManagerService: {e}")
            
            if session_manager:
                # Use SessionManagerService
                result = await session_manager.create_session(
                    user_id=user_id,
                    context=context
                )
                return {
                    "success": True,
                    "session_id": result.get("session_id"),
                    "session_token": result.get("session_token"),
                    "user_id": user_id,
                    "created_at": result.get("created_at"),
                    "message": "Session created successfully"
                }
            else:
                # Fallback: Create basic session
                session_id = str(uuid.uuid4())
                session_token = str(uuid.uuid4())
                return {
                    "success": True,
                    "session_id": session_id,
                    "session_token": session_token,
                    "user_id": user_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "message": "Session created successfully (basic implementation)"
                }
            
        except Exception as e:
            self.logger.error(f"❌ Create user session request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create session: {str(e)}"
            }
    
    async def handle_get_session_details_request(
        self,
        session_id: str,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Handle get session details request (Session Pillar).
        
        Args:
            session_id: Session identifier
            user_id: User identifier
        
        Returns:
            Session details
        """
        try:
            self.logger.info(f"📝 Session Pillar: Get session details request for session {session_id}")
            
            # Try to get SessionManagerService
            session_manager = None
            try:
                if self.curator:
                    session_manager = await self.curator.get_service("SessionManagerService")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not get SessionManagerService: {e}")
            
            if session_manager and hasattr(session_manager, 'get_session'):
                result = await session_manager.get_session(session_id)
                return {
                    "success": True,
                    "session": result,
                    "message": "Session details retrieved successfully"
                }
            else:
                # Fallback: Return basic session info
                return {
                    "success": True,
                    "session": {
                        "session_id": session_id,
                        "user_id": user_id,
                        "status": "active"
                    },
                    "message": "Session details retrieved (basic implementation)"
                }
            
        except Exception as e:
            self.logger.error(f"❌ Get session details request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get session details: {str(e)}"
            }
    
    async def handle_get_session_state_request(
        self,
        session_id: str,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Handle get session state request (Session Pillar).
        
        Args:
            session_id: Session identifier
            user_id: User identifier
        
        Returns:
            Session state
        """
        try:
            self.logger.info(f"📝 Session Pillar: Get session state request for session {session_id}")
            
            # Try to get SessionManagerService
            session_manager = None
            try:
                if self.curator:
                    session_manager = await self.curator.get_service("SessionManagerService")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not get SessionManagerService: {e}")
            
            if session_manager and hasattr(session_manager, 'get_session'):
                result = await session_manager.get_session(session_id)
                return {
                    "success": True,
                    "session_state": result.get("state", {}),
                    "orchestrator_states": result.get("orchestrator_context", {}),
                    "message": "Session state retrieved successfully"
                }
            else:
                # Fallback: Return basic session state
                return {
                    "success": True,
                    "session_state": {},
                    "orchestrator_states": {},
                    "message": "Session state retrieved (basic implementation)"
                }
            
        except Exception as e:
            self.logger.error(f"❌ Get session state request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get session state: {str(e)}"
            }
    
    async def handle_session_pillar_health_check_request(self) -> Dict[str, Any]:
        """
        Handle session pillar health check request.
        
        Returns:
            Health status
        """
        try:
            self.logger.info("🏥 Session Pillar: Health check request")
            
            return {
                "status": "healthy",
                "pillar": "session",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Session health check failed: {e}")
            return {
                "status": "unhealthy",
                "pillar": "session",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ========================================================================
    # LIAISON AGENTS PILLAR HANDLERS (NEW)
    # ========================================================================
    
    async def handle_send_message_to_pillar_agent_request(
        self,
        message: str,
        pillar: str,
        session_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        user_id: str = "anonymous",
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle send message to pillar agent request (Liaison Agents Pillar).
        
        Args:
            message: User message
            pillar: Pillar name (content, insights, operations, business-outcomes)
            session_id: Optional session identifier
            conversation_id: Optional conversation identifier
            user_id: User identifier
            session_token: Optional session token
        
        Returns:
            Agent response
        """
        try:
            self.logger.info(f"💬 Liaison Agents Pillar: Send message to {pillar} agent")
            
            # Use existing liaison chat handler
            result = await self.handle_liaison_chat_request(
                message=message,
                pillar=pillar,
                conversation_id=conversation_id or f"conv_{pillar}_{session_id or uuid.uuid4()}",
                user_id=user_id
            )
            
            return {
                "success": result.get("success", True),
                "response": result.get("response"),
                "session_id": session_id,
                "pillar": pillar,
                "timestamp": datetime.utcnow().isoformat(),
                "message": result.get("message")
            }
            
        except Exception as e:
            self.logger.error(f"❌ Send message to pillar agent request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to send message: {str(e)}"
            }
    
    async def handle_get_pillar_conversation_history_request(
        self,
        session_id: str,
        pillar: str,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Handle get pillar conversation history request (Liaison Agents Pillar).
        
        Args:
            session_id: Session identifier
            pillar: Pillar name (content, insights, operations, business-outcomes)
            user_id: User identifier
        
        Returns:
            Conversation history
        """
        try:
            self.logger.info(f"💬 Liaison Agents Pillar: Get conversation history for {pillar} agent")
            
            # Try to get SessionManagerService to get conversation history
            session_manager = None
            try:
                if self.curator:
                    session_manager = await self.curator.get_service("SessionManagerService")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not get SessionManagerService: {e}")
            
            if session_manager and hasattr(session_manager, 'get_session'):
                session = await session_manager.get_session(session_id)
                conversations = session.get("conversations", {})
                pillar_key = f"{pillar}_liaison" if not pillar.endswith("_liaison") else pillar
                conversation = conversations.get(pillar_key, {})
                
                return {
                    "success": True,
                    "conversation": conversation,
                    "message": "Conversation history retrieved successfully"
                }
            else:
                # Fallback: Return empty conversation
                return {
                    "success": True,
                    "conversation": {
                        "conversation_id": f"conv_{pillar}_{session_id}",
                        "messages": []
                    },
                    "message": "Conversation history retrieved (basic implementation)"
                }
            
        except Exception as e:
            self.logger.error(f"❌ Get pillar conversation history request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get conversation history: {str(e)}"
            }
    
    async def handle_liaison_agents_pillar_health_check_request(self) -> Dict[str, Any]:
        """
        Handle liaison agents pillar health check request.
        
        Returns:
            Health status
        """
        try:
            self.logger.info("🏥 Liaison Agents Pillar: Health check request")
            
            return {
                "status": "healthy",
                "pillar": "liaison-agents",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Liaison Agents health check failed: {e}")
            return {
                "status": "unhealthy",
                "pillar": "liaison-agents",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ========================================================================
    # BUSINESS OUTCOMES PILLAR REQUEST HANDLERS
    # ========================================================================
    
    async def handle_generate_strategic_roadmap_request(
        self,
        pillar_outputs: Dict[str, Any],
        roadmap_options: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Handle generate strategic roadmap request (Business Outcomes Pillar).
        Semantic API: Generate strategic roadmap from pillar outputs.
        
        Args:
            pillar_outputs: Outputs from all pillars
            roadmap_options: Optional roadmap generation options
            user_id: User identifier
        
        Returns:
            Frontend-ready response
        """
        try:
            self.logger.info(f"🗺️ Business Outcomes Pillar: Generate strategic roadmap for user: {user_id}")
            
            if not self.business_outcomes_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Business Outcomes Orchestrator is not available"
                }
            
            # Call orchestrator's semantic API method
            context_data = {
                "pillar_outputs": pillar_outputs,
                "roadmap_options": roadmap_options or {}
            }
            result = await self.business_outcomes_orchestrator.generate_strategic_roadmap(
                context_data=context_data,
                user_id=user_id
            )
            
            self.logger.info(f"✅ Strategic roadmap generated successfully")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Generate strategic roadmap failed: {e}")
            return {
                "success": False,
                "error": "Generation Failed",
                "message": str(e)
            }
    
    async def handle_generate_poc_proposal_request(
        self,
        pillar_outputs: Dict[str, Any],
        proposal_options: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Handle generate POC proposal request (Business Outcomes Pillar).
        Semantic API: Generate POC proposal from pillar outputs.
        
        Args:
            pillar_outputs: Outputs from all pillars
            proposal_options: Optional proposal generation options
            user_id: User identifier
        
        Returns:
            Frontend-ready response
        """
        try:
            self.logger.info(f"📋 Business Outcomes Pillar: Generate POC proposal for user: {user_id}")
            
            if not self.business_outcomes_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Business Outcomes Orchestrator is not available"
                }
            
            # Call orchestrator's semantic API method
            context_data = {
                "pillar_outputs": pillar_outputs,
                "proposal_options": proposal_options or {}
            }
            result = await self.business_outcomes_orchestrator.generate_poc_proposal(
                context_data=context_data,
                user_id=user_id
            )
            
            self.logger.info(f"✅ POC proposal generated successfully")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Generate POC proposal failed: {e}")
            return {
                "success": False,
                "error": "Generation Failed",
                "message": str(e)
            }
    
    async def handle_get_pillar_summaries_request(
        self,
        session_id: Optional[str] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Handle get pillar summaries request (Business Outcomes Pillar).
        Semantic API: Get summaries from all pillars.
        
        Args:
            session_id: Optional session identifier
            user_id: User identifier
        
        Returns:
            Frontend-ready response
        """
        try:
            self.logger.info(f"📊 Business Outcomes Pillar: Get pillar summaries for session: {session_id}")
            
            if not self.business_outcomes_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Business Outcomes Orchestrator is not available"
                }
            
            # Call orchestrator's semantic API method
            result = await self.business_outcomes_orchestrator.get_pillar_summaries(
                session_id=session_id or "",
                user_id=user_id
            )
            
            self.logger.info(f"✅ Pillar summaries retrieved successfully")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Get pillar summaries failed: {e}")
            return {
                "success": False,
                "error": "Retrieval Failed",
                "message": str(e)
            }
    
    async def handle_get_journey_visualization_request(
        self,
        session_id: Optional[str] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Handle get journey visualization request (Business Outcomes Pillar).
        Semantic API: Get journey visualization across all pillars.
        
        Args:
            session_id: Optional session identifier
            user_id: User identifier
        
        Returns:
            Frontend-ready response
        """
        try:
            self.logger.info(f"📊 Business Outcomes Pillar: Get journey visualization for session: {session_id}")
            
            if not self.business_outcomes_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Business Outcomes Orchestrator is not available"
                }
            
            # Call orchestrator's semantic API method
            result = await self.business_outcomes_orchestrator.get_journey_visualization(
                session_id=session_id or "",
                user_id=user_id
            )
            
            self.logger.info(f"✅ Journey visualization retrieved successfully")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Get journey visualization failed: {e}")
            return {
                "success": False,
                "error": "Retrieval Failed",
                "message": str(e)
            }
    
    async def handle_business_outcomes_health_check_request(self) -> Dict[str, Any]:
        """
        Handle business outcomes pillar health check request.
        
        Returns:
            Health status
        """
        try:
            self.logger.info("🏥 Business Outcomes Pillar: Health check request")
            
            if not self.business_outcomes_orchestrator:
                return {
                    "status": "unhealthy",
                    "pillar": "business_outcomes",
                    "error": "BusinessOutcomesOrchestrator not available",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Call orchestrator's health check
            result = await self.business_outcomes_orchestrator.health_check()
            
            return {
                "status": "healthy",
                "pillar": "business_outcomes",
                "orchestrator_status": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Business Outcomes health check failed: {e}")
            return {
                "status": "unhealthy",
                "pillar": "business_outcomes",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ========================================================================
    # API MANAGEMENT
    # ========================================================================
    
    async def register_api_endpoint(
        self,
        endpoint: str,
        handler: Callable
    ) -> bool:
        """Register an API endpoint with handler (SOA API)."""
        return await self.expose_frontend_api(
            api_name=endpoint.split("/")[-1],
            endpoint=endpoint,
            handler=handler
        )
    
    async def validate_api_request(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate API request (SOA API).
        
        Args:
            request: Request to validate
        
        Returns:
            Validation result
        """
        try:
            # Validate required fields
            required_fields = ["endpoint", "method"]
            missing_fields = [f for f in required_fields if f not in request]
            
            if missing_fields:
                return {
                    "valid": False,
                    "errors": [f"Missing required field: {f}" for f in missing_fields]
                }
            
            # Validate endpoint exists
            if request["endpoint"] not in self.registered_apis:
                return {
                    "valid": False,
                    "errors": [f"Endpoint not found: {request['endpoint']}"]
                }
            
            return {
                "valid": True,
                "endpoint": request["endpoint"]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Validate API request failed: {e}")
            return {
                "valid": False,
                "errors": [str(e)]
            }
    
    async def transform_for_frontend(
        self,
        orchestrator_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transform orchestrator response for frontend consumption (SOA API).
        
        Args:
            orchestrator_response: Response from Business Enablement orchestrator
        
        Returns:
            Frontend-ready response
        """
        try:
            # Add frontend-specific fields
            frontend_response = {
                **orchestrator_response,
                "ui_state": "success" if orchestrator_response.get("success") else "error",
                "timestamp": datetime.utcnow().isoformat(),
                "api_version": "v1"
            }
            
            # Add next actions if success
            if orchestrator_response.get("success"):
                frontend_response["next_actions"] = [
                    "view_results",
                    "export",
                    "share"
                ]
            
            return frontend_response
            
        except Exception as e:
            self.logger.error(f"❌ Transform for frontend failed: {e}")
            return orchestrator_response
    
    # ========================================================================
    # OPERATIONS PILLAR HANDLERS
    # ========================================================================
    
    async def handle_generate_workflow_from_sop_request(
        self,
        session_token: str = None,
        sop_file_uuid: str = None,
        sop_content: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate workflow from SOP."""
        try:
            if not self.operations_orchestrator:
                return {
                    "success": False,
                    "error": "Operations Orchestrator Not Available",
                    "message": "Operations orchestrator is not initialized"
                }
            
            # Delegate to operations orchestrator
            result = await self.operations_orchestrator.generate_workflow_from_sop(
                session_token=session_token,
                sop_file_uuid=sop_file_uuid,
                sop_content=sop_content
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Generate workflow from SOP failed: {e}")
            return {
                "success": False,
                "error": "Internal Server Error",
                "message": str(e)
            }
    
    async def handle_generate_sop_from_workflow_request(
        self,
        session_token: str = None,
        workflow_file_uuid: str = None,
        workflow_content: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate SOP from workflow."""
        try:
            if not self.operations_orchestrator:
                return {
                    "success": False,
                    "error": "Operations Orchestrator Not Available",
                    "message": "Operations orchestrator is not initialized"
                }
            
            # Delegate to operations orchestrator
            result = await self.operations_orchestrator.generate_sop_from_workflow(
                session_token=session_token,
                workflow_file_uuid=workflow_file_uuid,
                workflow_content=workflow_content
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Generate SOP from workflow failed: {e}")
            return {
                "success": False,
                "error": "Internal Server Error",
                "message": str(e)
            }
    
    # ========================================================================
    # BUSINESS OUTCOMES PILLAR HANDLERS
    # ========================================================================
    
    async def handle_generate_strategic_roadmap_request(
        self,
        pillar_outputs: Dict[str, Any] = None,
        roadmap_options: Dict[str, Any] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Generate strategic roadmap from pillar outputs."""
        try:
            if not self.business_outcomes_orchestrator:
                return {
                    "success": False,
                    "error": "Business Outcomes Orchestrator Not Available",
                    "message": "Business outcomes orchestrator is not initialized"
                }
            
            # For MVP: Return a simple roadmap structure
            # In production, this would call the actual orchestrator
            roadmap = {
                "roadmap_id": f"roadmap_{user_id or 'default'}",
                "title": "Strategic Roadmap",
                "pillars_analyzed": list(pillar_outputs.keys()) if pillar_outputs else [],
                "recommendations": [
                    {"priority": "high", "action": "Implement content analysis pipeline"},
                    {"priority": "medium", "action": "Optimize operational workflows"},
                    {"priority": "low", "action": "Enhance data insights"}
                ],
                "timeline": roadmap_options.get("timeline", "12 months") if roadmap_options else "12 months",
                "visualization_type": "summary"
            }
            
            return {
                "success": True,
                "roadmap": roadmap,
                "message": "Strategic roadmap generated successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Generate strategic roadmap failed: {e}")
            return {
                "success": False,
                "error": "Internal Server Error",
                "message": str(e)
            }
    
    async def handle_generate_poc_proposal_request(
        self,
        pillar_outputs: Dict[str, Any] = None,
        proposal_options: Dict[str, Any] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Generate proof-of-concept proposal."""
        try:
            if not self.business_outcomes_orchestrator:
                return {
                    "success": False,
                    "error": "Business Outcomes Orchestrator Not Available",
                    "message": "Business outcomes orchestrator is not initialized"
                }
            
            # For MVP: Return a simple POC proposal
            proposal = {
                "proposal_id": f"poc_{user_id or 'default'}",
                "title": "Proof of Concept Proposal",
                "scope": "MVP implementation",
                "timeline": "3 months",
                "deliverables": ["Working prototype", "Documentation", "Demo"]
            }
            
            return {
                "success": True,
                "proposal": proposal,
                "message": "POC proposal generated successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Generate POC proposal failed: {e}")
            return {
                "success": False,
                "error": "Internal Server Error",
                "message": str(e)
            }
    
    async def handle_get_pillar_summaries_request(
        self,
        session_id: str = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Get summaries from all pillars."""
        try:
            summaries = {
                "content": {"status": "available", "files_processed": 0},
                "insights": {"status": "available", "insights_generated": 0},
                "operations": {"status": "available", "workflows_created": 0}
            }
            
            return {
                "success": True,
                "summaries": summaries,
                "message": "Pillar summaries retrieved successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Get pillar summaries failed: {e}")
            return {
                "success": False,
                "error": "Internal Server Error",
                "message": str(e)
            }
    
    async def handle_get_journey_visualization_request(
        self,
        session_id: str = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Get journey visualization."""
        try:
            visualization = {
                "journey_id": session_id or "default",
                "steps": [],
                "current_step": 0,
                "completion_percentage": 0
            }
            
            return {
                "success": True,
                "visualization": visualization,
                "message": "Journey visualization retrieved successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Get journey visualization failed: {e}")
            return {
                "success": False,
                "error": "Internal Server Error",
                "message": str(e)
            }
    
    async def handle_business_outcomes_health_check_request(self) -> Dict[str, Any]:
        """Health check for business outcomes pillar."""
        return {
            "success": True,
            "status": "healthy" if self.business_outcomes_orchestrator else "unavailable",
            "orchestrator_available": self.business_outcomes_orchestrator is not None
        }
    
    # ========================================================================
    # HEALTH & METADATA
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check (inherited from RealmServiceBase)."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "registered_apis": len(self.registered_apis),
            "orchestrators_available": {
                "content": self.content_orchestrator is not None,
                "insights": self.insights_orchestrator is not None,
                "operations": self.operations_orchestrator is not None,
                "data_operations": self.data_operations_orchestrator is not None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "experience_service",
            "realm": "experience",
            "layer": "ui_gateway",
            "capabilities": ["frontend_api_gateway", "request_routing", "api_transformation"],
            "soa_apis": [
                "expose_frontend_api", "route_frontend_request", "get_frontend_apis",
                "handle_document_analysis_request", "handle_insights_request",
                "handle_operations_request", "handle_data_operations_request",
                "register_api_endpoint", "validate_api_request", "transform_for_frontend"
            ],
            "mcp_tools": [],
            "composes": "business_enablement_orchestrators",
            "supported_types": self.supported_types
        }
    
    # ========================================================================
    # ROUTING METRICS (Phase 4: Monitoring)
    # ========================================================================
    
    async def get_routing_metrics(self) -> Dict[str, Any]:
        """
        Get routing performance metrics for monitoring.
        
        Returns metrics for both old (hardcoded) and new (discovered) routing methods.
        """
        if not self.routing_monitoring_enabled:
            return {
                "monitoring_enabled": False,
                "message": "Routing monitoring is disabled"
            }
        
        # Calculate success rates
        old_success_rate = 0.0
        if self.routing_metrics["old_routing"]["requests"] > 0:
            old_success_rate = (
                self.routing_metrics["old_routing"]["successes"] / 
                self.routing_metrics["old_routing"]["requests"]
            ) * 100
        
        new_success_rate = 0.0
        if self.routing_metrics["new_routing"]["requests"] > 0:
            new_success_rate = (
                self.routing_metrics["new_routing"]["successes"] / 
                self.routing_metrics["new_routing"]["requests"]
            ) * 100
        
        return {
            "monitoring_enabled": True,
            "feature_flag_enabled": self.use_discovered_routing,
            "last_reset": self.routing_metrics["last_reset"],
            "old_routing": {
                "requests": self.routing_metrics["old_routing"]["requests"],
                "successes": self.routing_metrics["old_routing"]["successes"],
                "errors": self.routing_metrics["old_routing"]["errors"],
                "success_rate_percent": round(old_success_rate, 2),
                "total_time_ms": round(self.routing_metrics["old_routing"]["total_time_ms"], 2),
                "avg_time_ms": round(self.routing_metrics["old_routing"]["avg_time_ms"], 2)
            },
            "new_routing": {
                "requests": self.routing_metrics["new_routing"]["requests"],
                "successes": self.routing_metrics["new_routing"]["successes"],
                "errors": self.routing_metrics["new_routing"]["errors"],
                "fallbacks": self.routing_metrics["new_routing"]["fallbacks"],
                "success_rate_percent": round(new_success_rate, 2),
                "total_time_ms": round(self.routing_metrics["new_routing"]["total_time_ms"], 2),
                "avg_time_ms": round(self.routing_metrics["new_routing"]["avg_time_ms"], 2)
            },
            "comparison": {
                "performance_improvement_percent": round(
                    ((self.routing_metrics["old_routing"]["avg_time_ms"] - 
                      self.routing_metrics["new_routing"]["avg_time_ms"]) / 
                     max(self.routing_metrics["old_routing"]["avg_time_ms"], 1)) * 100, 2
                ) if self.routing_metrics["old_routing"]["avg_time_ms"] > 0 else 0,
                "new_routing_usage_percent": round(
                    (self.routing_metrics["new_routing"]["requests"] / 
                     max(self.routing_metrics["old_routing"]["requests"] + 
                         self.routing_metrics["new_routing"]["requests"], 1)) * 100, 2
                )
            }
        }
    
    async def reset_routing_metrics(self) -> Dict[str, Any]:
        """Reset routing metrics (for testing/monitoring)."""
        self.routing_metrics = {
            "old_routing": {
                "requests": 0,
                "successes": 0,
                "errors": 0,
                "total_time_ms": 0.0,
                "avg_time_ms": 0.0
            },
            "new_routing": {
                "requests": 0,
                "successes": 0,
                "errors": 0,
                "total_time_ms": 0.0,
                "avg_time_ms": 0.0,
                "fallbacks": 0
            },
            "last_reset": datetime.utcnow().isoformat()
        }
        return {"success": True, "message": "Routing metrics reset", "timestamp": self.routing_metrics["last_reset"]}


