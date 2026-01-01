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
import inspect
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
from pathlib import Path

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
    HOW: Uses route discovery from Curator via APIRoutingUtility (Phase 5: New Routing Only)
    
    Composes:
    - MVPSolutionOrchestratorService → /api/v1/mvp-solution/* (MVP Solution entry point)
    - ContentOrchestrator → /api/v1/content-pillar/*
    - InsightsSolutionOrchestratorService → /api/v1/insights-solution/*
    - DataSolutionOrchestratorService → /api/v1/data-solution/* (Phase 4: Data Mash)
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
        # REMOVED: self.insights_orchestrator - Use InsightsSolutionOrchestratorService via insights-solution pillar
        self.operations_orchestrator = None
        self.data_operations_orchestrator = None
        self.business_outcomes_orchestrator = None
        
        # Insurance Use Case orchestrators (discovered via Delivery Manager)
        self.insurance_migration_orchestrator = None
        self.wave_orchestrator = None
        self.policy_tracker_orchestrator = None
        
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
        
        # ⭐ Phase 5: New routing only - always use discovered routing
        # Old hardcoded routing has been removed and archived
        try:
            from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager
            from utilities.path_utils import get_project_root
            project_root = get_project_root()
            config = UnifiedConfigurationManager(
                service_name="frontend_gateway",
                config_root=str(project_root)
            )
            # Always use discovered routing (Phase 5)
            self.use_discovered_routing = True
            self.routing_monitoring_enabled = config.get("routing.monitoring.enabled", True)
        except Exception as e:
            # Fallback if config not available - still use new routing
            self.use_discovered_routing = True
            self.routing_monitoring_enabled = False
            self.logger.warning(f"⚠️ Failed to load routing config: {e}, using defaults")
        
        # Route registry for discovered routes
        self.discovered_routes: Dict[str, Dict[str, Any]] = {}
        
        # Traefik routing abstraction (for service discovery and health checking)
        self.traefik_routing = None
        
        # Routing metrics for monitoring (Phase 4)
        self.routing_metrics: Dict[str, Any] = {
            "routing": {
                "requests": 0,
                "successes": 0,
                "errors": 0,
                "total_time_ms": 0.0,
                "avg_time_ms": 0.0
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
            
            # ⭐ Phase 5: Always discover routes from Curator (new routing only)
            await self._discover_routes_from_curator()
            
            # ⭐ NEW: Get Traefik routing abstraction for service discovery
            try:
                public_works = self.di_container.get_public_works()
                if public_works and hasattr(public_works, 'routing_registry'):
                    routing_registry = public_works.routing_registry
                    if routing_registry:
                        self.traefik_routing = routing_registry.get_routing()
                        if self.traefik_routing:
                            self.logger.info("✅ Traefik routing abstraction connected")
                            # Discover routes from Traefik for monitoring
                            try:
                                traefik_routes = await self.traefik_routing.discover_routes()
                                self.logger.info(f"✅ Discovered {len(traefik_routes)} routes from Traefik")
                            except Exception as e:
                                self.logger.warning(f"⚠️ Failed to discover routes from Traefik: {e}")
            except Exception as e:
                self.logger.warning(f"⚠️ Traefik routing not available: {e} - routing will continue without Traefik integration")
            
            # 3. Discover Business Enablement orchestrators via Curator
            await self._discover_orchestrators()
            
            # 4. Register routes via APIRoutingUtility (routes tracked in Curator)
            # ⚠️ REMOVED: _register_orchestrator_routes() - redundant with discovery-based approach
            # Routes are now registered via:
            #   1. _register_routes_with_curator() - registers route metadata with Curator
            #   2. _discover_routes_from_curator() - discovers and registers routes with APIRoutingUtility
            # This eliminates duplicate route registration and ensures we use the discovery-based handler
            # if self.api_router:
            #     await self._register_orchestrator_routes()
            
            # 5. Expose frontend APIs
            await self._expose_frontend_apis()
            
            # 6. NOTE: FrontendGatewayService does NOT register with Curator
            # Foundation Services don't register with Curator (since Curator is itself a foundation).
            # FrontendGatewayService is exposed via Experience Foundation SDK instead.
            # Routes are still registered with Curator for discovery (via _register_routes_with_curator),
            # but the service itself is accessed via Experience Foundation SDK.
            self.logger.info("📝 FrontendGatewayService exposed via Experience Foundation SDK (not Curator)")
            
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
                # Note: key is now "content" (renamed from "content")
                if "content" in delivery_manager.mvp_pillar_orchestrators:
                    self.content_orchestrator = delivery_manager.mvp_pillar_orchestrators["content"]
                    # Also store in orchestrators dictionary for dictionary-style access
                    self.orchestrators["ContentOrchestrator"] = self.content_orchestrator
                    self.logger.info("✅ Discovered ContentOrchestrator from Delivery Manager")
                    # Debug logging to understand orchestrator discovery
                    self.logger.debug(f"🔍 ContentOrchestrator object: {self.content_orchestrator is not None}, type: {type(self.content_orchestrator).__name__}")
                    self.logger.debug(f"🔍 Stored in orchestrators['ContentOrchestrator']: {self.orchestrators.get('ContentOrchestrator') is not None}")
                else:
                    self.logger.warning("⚠️ ContentOrchestrator not in mvp_pillar_orchestrators")
                    self.logger.warning(f"   Available keys: {list(delivery_manager.mvp_pillar_orchestrators.keys())}")
                    # Debug logging for missing orchestrator
                    self.logger.debug(f"🔍 Delivery Manager mvp_pillar_orchestrators keys: {list(delivery_manager.mvp_pillar_orchestrators.keys())}")
                    self.logger.debug(f"🔍 'content' in dict: {'content' in delivery_manager.mvp_pillar_orchestrators}")
                
                # REMOVED: InsightsOrchestrator discovery - Use InsightsSolutionOrchestratorService via insights-solution pillar
                
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
                    self.orchestrators["ContentOrchestrator"] = self.content_orchestrator
                # REMOVED: InsightsOrchestrator - Use InsightsSolutionOrchestratorService via insights-solution pillar
                if self.operations_orchestrator:
                    self.orchestrators["OperationsOrchestrator"] = self.operations_orchestrator
                if self.data_operations_orchestrator:
                    self.orchestrators["DataOperationsOrchestrator"] = self.data_operations_orchestrator
                if self.business_outcomes_orchestrator:
                    self.orchestrators["BusinessOutcomesOrchestrator"] = self.business_outcomes_orchestrator
                
                self.logger.info(f"✅ Orchestrators registered: {list(self.orchestrators.keys())}")
                
                # Discover Insurance Use Case orchestrators via get_orchestrators()
                if hasattr(delivery_manager, 'get_orchestrators'):
                    try:
                        all_orchestrators = delivery_manager.get_orchestrators()
                        for orchestrator in all_orchestrators:
                            if hasattr(orchestrator, 'orchestrator_name'):
                                if orchestrator.orchestrator_name == "InsuranceMigrationOrchestrator":
                                    self.insurance_migration_orchestrator = orchestrator
                                    self.orchestrators["InsuranceMigrationOrchestrator"] = orchestrator
                                    self.logger.info("✅ Discovered InsuranceMigrationOrchestrator")
                                elif orchestrator.orchestrator_name == "WaveOrchestrator":
                                    self.wave_orchestrator = orchestrator
                                    self.orchestrators["WaveOrchestrator"] = orchestrator
                                    self.logger.info("✅ Discovered WaveOrchestrator")
                                elif orchestrator.orchestrator_name == "PolicyTrackerOrchestrator":
                                    self.policy_tracker_orchestrator = orchestrator
                                    self.orchestrators["PolicyTrackerOrchestrator"] = orchestrator
                                    self.logger.info("✅ Discovered PolicyTrackerOrchestrator")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to discover Insurance orchestrators: {e}")
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
            
            # Route mappings for each orchestrator with handler method names
            route_mappings = {
                "content": {
                    "pillar": "content-pillar",
                    "orchestrator": self.content_orchestrator,
                    "routes": [
                        {"path": "/api/v1/content-pillar/list-uploaded-files", "method": "GET", "handler": "handle_list_uploaded_files_request"},
                        {"path": "/api/v1/content-pillar/upload-file", "method": "POST", "handler": "handle_upload_file_request"},
                        {"path": "/api/v1/content-pillar/process-file/{file_id}", "method": "POST", "handler": "handle_process_file_request"},
                        {"path": "/api/v1/content-pillar/list-parsed-files", "method": "GET", "handler": "handle_list_parsed_files_request"},
                        {"path": "/api/v1/content-pillar/preview-parsed-file/{parsed_file_id}", "method": "GET", "handler": "handle_preview_parsed_file_request"},
                        {"path": "/api/v1/content-pillar/create-embeddings", "method": "POST", "handler": "handle_create_embeddings_request"},
                        {"path": "/api/v1/content-pillar/preview-embeddings/{content_id}", "method": "GET", "handler": "handle_preview_embeddings_request"},
                        {"path": "/api/v1/content-pillar/list-embeddings", "method": "GET", "handler": "handle_list_embeddings_request"},
                        {"path": "/api/v1/content-pillar/list-parsed-files-with-embeddings", "method": "GET", "handler": "handle_list_parsed_files_with_embeddings_request"},
                    ]
                },
                # REMOVED: insights-pillar routes - Use insights-solution pillar instead
                # All insights operations now go through InsightsSolutionOrchestratorService
                "operations": {
                    "pillar": "operations-pillar",
                    "orchestrator": self.operations_orchestrator,
                    "routes": [
                        {"path": "/api/v1/operations-pillar/convert-sop-to-workflow", "method": "POST", "handler": "handle_convert_sop_to_workflow_request"},
                        {"path": "/api/v1/operations-pillar/convert-workflow-to-sop", "method": "POST", "handler": "handle_convert_workflow_to_sop_request"},
                    ]
                },
                "business_outcomes": {
                    "pillar": "business-outcomes-pillar",
                    "orchestrator": self.business_outcomes_orchestrator,
                    "routes": [
                        {"path": "/api/v1/business-outcomes-pillar/generate-strategic-roadmap", "method": "POST", "handler": "handle_generate_strategic_roadmap_request"},
                        {"path": "/api/v1/business-outcomes-pillar/generate-proof-of-concept-proposal", "method": "POST", "handler": "handle_generate_proof_of_concept_proposal_request"},
                    ]
                },
                "session": {
                    "pillar": "session",
                    "orchestrator": None,  # Session doesn't use an orchestrator, handled directly by FrontendGatewayService
                    "routes": [
                        {"path": "/api/v1/session/create-user-session", "method": "POST", "handler": "handle_create_user_session_request"},
                        {"path": "/api/v1/session/get-session-details/{session_id}", "method": "GET", "handler": "handle_get_session_details_request"},
                        {"path": "/api/v1/session/get-session-state/{session_id}", "method": "GET", "handler": "handle_get_session_state_request"},
                        {"path": "/api/v1/session/health", "method": "GET", "handler": "handle_session_pillar_health_check_request"},
                    ]
                },
                "liaison-agents": {
                    "pillar": "liaison-agents",
                    "orchestrator": None,  # Liaison agents don't use an orchestrator, handled directly by FrontendGatewayService
                    "routes": [
                        {"path": "/api/v1/liaison-agents/send-message-to-pillar-agent", "method": "POST", "handler": "handle_send_message_to_pillar_agent_request"},
                        {"path": "/api/v1/liaison-agents/get-pillar-conversation-history/{session_id}/{pillar}", "method": "GET", "handler": "handle_get_pillar_conversation_history_request"},
                        {"path": "/api/v1/liaison-agents/health", "method": "GET", "handler": "handle_liaison_agents_pillar_health_check_request"},
                    ]
                },
                "insurance_migration": {
                    "pillar": "insurance-migration",
                    "orchestrator": self.insurance_migration_orchestrator,
                    "routes": [
                        {"path": "/api/v1/insurance-migration/ingest-legacy-data", "method": "POST", "handler": "handle_ingest_legacy_data_request"},
                        {"path": "/api/v1/insurance-migration/map-to-canonical", "method": "POST", "handler": "handle_map_to_canonical_request"},
                        {"path": "/api/v1/insurance-migration/route-policies", "method": "POST", "handler": "handle_route_policies_request"},
                    ]
                },
                "wave_orchestration": {
                    "pillar": "wave-orchestration",
                    "orchestrator": self.wave_orchestrator,
                    "routes": [
                        {"path": "/api/v1/wave-orchestration/create-wave", "method": "POST", "handler": "handle_create_wave_request"},
                        {"path": "/api/v1/wave-orchestration/get-wave-status/{wave_id}", "method": "GET", "handler": "handle_get_wave_status_request"},
                        {"path": "/api/v1/wave-orchestration/execute-wave/{wave_id}", "method": "POST", "handler": "handle_execute_wave_request"},
                    ]
                },
                "policy_tracking": {
                    "pillar": "policy-tracking",
                    "orchestrator": self.policy_tracker_orchestrator,
                    "routes": [
                        {"path": "/api/v1/policy-tracking/register-policy", "method": "POST", "handler": "handle_register_policy_request"},
                        {"path": "/api/v1/policy-tracking/get-policy-location/{policy_id}", "method": "GET", "handler": "handle_get_policy_location_request"},
                        {"path": "/api/v1/policy-tracking/update-policy-location", "method": "PUT", "handler": "handle_update_policy_location_request"},
                    ]
                }
            }
            
            registered_count = 0
            for orchestrator_key, mapping in route_mappings.items():
                orchestrator = mapping["orchestrator"]
                # Allow registration even if orchestrator is None (e.g., session and liaison-agents pillars handled directly by FrontendGatewayService)
                if orchestrator is None and orchestrator_key not in ["session", "liaison-agents"]:
                    self.logger.debug(f"⚠️ {orchestrator_key} orchestrator not available - skipping route registration")
                    continue
                
                # Log session and liaison-agents pillar registration
                if orchestrator_key == "session":
                    self.logger.info(f"📋 Registering {len(mapping['routes'])} session pillar routes (no orchestrator needed)")
                elif orchestrator_key == "liaison-agents":
                    self.logger.info(f"📋 Registering {len(mapping['routes'])} liaison-agents pillar routes (no orchestrator needed)")
                
                for route in mapping["routes"]:
                    try:
                        # Create route handler that delegates to route_frontend_request()
                        # Use closure to capture route_path and route_method
                        route_path = route["path"]
                        route_method = route["method"]
                        
                        async def create_handler(route_path_inner, route_method_inner, handler_method_name):
                            # APIRoutingUtility calls: handler(request_context.body, request_context.user_context)
                            # So we need to accept two arguments: body and user_context
                            # Get the handler method to avoid recursion (call handler directly, not route_frontend_request)
                            handler_method = getattr(self, handler_method_name, None)
                            if not handler_method:
                                self.logger.error(f"❌ Handler method not found: {handler_method_name}")
                                async def error_handler(request_body: Dict[str, Any], user_context: Any):
                                    return {"success": False, "error": f"Handler method {handler_method_name} not found"}
                                return error_handler
                            
                            async def handler(request_body: Dict[str, Any], user_context: Any):
                                # Extract path parameters from route_path_inner if needed
                                # APIRoutingUtility should extract these, but we'll also check here
                                # For routes like /api/v1/content-pillar/process-file/{file_id}
                                # The file_id should be in request_body from _route_via_discovery path extraction
                                # Extract user_id from user_context
                                user_id = None
                                session_token = None
                                if user_context:
                                    if hasattr(user_context, 'user_id'):
                                        user_id = user_context.user_id
                                    if hasattr(user_context, 'session_token'):
                                        session_token = user_context.session_token
                                    elif hasattr(user_context, 'token'):
                                        session_token = user_context.token
                                
                                # Call handler method directly (avoid recursion - don't call route_frontend_request)
                                # Handler methods know how to extract parameters from request_body
                                try:
                                    # Most handlers need file_data, filename, content_type, user_id, etc.
                                    # Extract from request_body based on handler signature
                                    if handler_method_name == "handle_upload_file_request":
                                        return await handler_method(
                                            file_data=request_body.get("file_data"),
                                            filename=request_body.get("filename"),
                                            content_type=request_body.get("content_type"),
                                            user_id=user_id or "anonymous",
                                            session_id=request_body.get("session_id"),
                                            copybook_data=request_body.get("copybook_data"),
                                            copybook_filename=request_body.get("copybook_filename")
                                        )
                                    elif handler_method_name == "handle_list_parsed_files_request":
                                        return await self.handle_list_parsed_files_request(request_body, user_context)
                                    elif handler_method_name == "handle_preview_parsed_file_request":
                                        # Extract parsed_file_id from path parameters (stored in request_body by _route_via_discovery)
                                        parsed_file_id = request_body.get("parsed_file_id") or request_body.get("path_params", {}).get("parsed_file_id")
                                        if not parsed_file_id:
                                            return {"success": False, "error": "parsed_file_id required"}
                                        else:
                                            return await self.handle_preview_parsed_file_request(parsed_file_id, request_body, user_context)
                                    elif handler_method_name == "handle_list_uploaded_files_request":
                                        return await handler_method(user_id=user_id or "anonymous")
                                    elif handler_method_name == "handle_process_file_request":
                                        # Extract file_id from request_body (may come from path params or body)
                                        file_id = request_body.get("file_id") or request_body.get("file_uuid") or request_body.get("id")
                                        # Extract processing options
                                        processing_options = request_body.get("options", {})
                                        if request_body.get("action"):
                                            processing_options["action"] = request_body.get("action")
                                        # Debug logging for copybook passing
                                        self.logger.warning(f"🔍🔍🔍 handle_process_file_request processing_options: {processing_options}")
                                        if processing_options:
                                            has_copybook = "copybook" in processing_options
                                            copybook_length = len(str(processing_options.get("copybook", "")))
                                            self.logger.warning(f"🔍🔍🔍 handle_process_file_request: has_copybook={has_copybook}, copybook_length={copybook_length}, options_keys={list(processing_options.keys())}")
                                        
                                        # ✅ user_context is now from request scope (set in route_frontend_request)
                                        # No need to extract or pass it - handler methods will get it from request context
                                        return await handler_method(
                                            file_id=file_id,
                                            user_id=user_id or "anonymous",
                                            copybook_file_id=request_body.get("copybook_file_id"),
                                            processing_options=processing_options if processing_options else None
                                        )
                                    # REMOVED: handle_analyze_content_for_insights_semantic_request - Use insights-solution pillar
                                    elif handler_method_name == "handle_analyze_content_for_insights_semantic_request":
                                        return {
                                            "success": False,
                                            "error": "Endpoint Removed",
                                            "message": "This endpoint has been removed. Use /api/v1/insights-solution/analyze instead"
                                        }
                                    elif handler_method_name == "handle_convert_sop_to_workflow_request":
                                        return await handler_method(
                                            sop_id=request_body.get("sop_id"),
                                            sop_file_uuid=request_body.get("sop_file_uuid"),
                                            sop_content=request_body.get("sop_content"),
                                            conversion_type=request_body.get("conversion_type"),
                                            options=request_body.get("options", {}),
                                            user_id=user_id or "anonymous",
                                            session_token=session_token
                                        )
                                    elif handler_method_name == "handle_convert_workflow_to_sop_request":
                                        return await handler_method(
                                            workflow_id=request_body.get("workflow_id"),
                                            workflow_file_uuid=request_body.get("workflow_file_uuid"),
                                            workflow=request_body.get("workflow"),
                                            workflow_content=request_body.get("workflow_content"),
                                            conversion_type=request_body.get("conversion_type"),
                                            options=request_body.get("options", {}),
                                            user_id=user_id or "anonymous",
                                            session_token=session_token
                                        )
                                    elif handler_method_name == "handle_generate_strategic_roadmap_request":
                                        return await handler_method(
                                            pillar_outputs=request_body.get("pillar_outputs", {}),
                                            roadmap_options=request_body.get("roadmap_options", {}),
                                            user_id=user_id or "anonymous"
                                        )
                                    elif handler_method_name == "handle_generate_proof_of_concept_proposal_request":
                                        return await handler_method(
                                            pillar_outputs=request_body.get("pillar_outputs", {}),
                                            poc_options=request_body.get("poc_options", {}),
                                            user_id=user_id or "anonymous"
                                        )
                                    elif handler_method_name == "handle_create_user_session_request":
                                        return await handler_method(
                                            user_id=request_body.get("user_id") or user_id or "anonymous",
                                            session_type=request_body.get("session_type", "mvp"),
                                            context=request_body.get("context")
                                        )
                                    elif handler_method_name == "handle_get_session_details_request":
                                        # Extract session_id from path parameters (stored in request_body by _route_via_discovery)
                                        session_id = request_body.get("session_id") or request_body.get("path_params", {}).get("session_id")
                                        return await handler_method(
                                            session_id=session_id,
                                            user_id=user_id or "anonymous"
                                        )
                                    elif handler_method_name == "handle_get_session_state_request":
                                        # Extract session_id from path parameters
                                        session_id = request_body.get("session_id") or request_body.get("path_params", {}).get("session_id")
                                        return await handler_method(
                                            session_id=session_id,
                                            user_id=user_id or "anonymous"
                                        )
                                    elif handler_method_name == "handle_session_pillar_health_check_request":
                                        return await handler_method()
                                    elif handler_method_name == "handle_send_message_to_pillar_agent_request":
                                        return await handler_method(
                                            message=request_body.get("message"),
                                            pillar=request_body.get("pillar"),
                                            session_id=request_body.get("session_id"),
                                            conversation_id=request_body.get("conversation_id"),
                                            user_id=user_id or request_body.get("user_id", "anonymous"),
                                            session_token=request_body.get("session_token")
                                        )
                                    elif handler_method_name == "handle_get_pillar_conversation_history_request":
                                        # Extract session_id and pillar from path parameters
                                        session_id = request_body.get("session_id") or request_body.get("path_params", {}).get("session_id")
                                        pillar = request_body.get("pillar") or request_body.get("path_params", {}).get("pillar")
                                        return await handler_method(
                                            session_id=session_id,
                                            pillar=pillar,
                                            user_id=user_id or "anonymous"
                                        )
                                    elif handler_method_name == "handle_liaison_agents_pillar_health_check_request":
                                        return await handler_method()
                                    else:
                                        # Generic handler call - pass request_body as kwargs with user_id
                                        kwargs = dict(request_body) if isinstance(request_body, dict) else {}
                                        kwargs["user_id"] = user_id or "anonymous"
                                        return await handler_method(**kwargs)
                                except Exception as e:
                                    self.logger.error(f"❌ Handler {handler_method_name} execution failed: {e}", exc_info=True)
                                    return {"success": False, "error": str(e)}
                            return handler
                        
                        handler = await create_handler(route_path, route_method, route.get("handler"))
                        
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
        
        # REMOVED: Legacy insights endpoint - Use /api/v1/insights-solution/* endpoints instead
        
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
            
            # Use Curator's register_route wrapper method instead of accessing route_registry directly
            # This avoids the coroutine issue and ensures proper initialization
            if not hasattr(curator, 'register_route'):
                self.logger.warning("⚠️ Curator does not have register_route method - routes will not be registered")
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
                    "route_id": "content_delete_file",
                    "path": "/api/v1/content-pillar/delete-file/{file_id}",
                    "method": "DELETE",
                    "pillar": "content-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "file_deletion",
                    "handler": "handle_delete_file_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Delete a file",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "content_embed",
                    "path": "/api/v1/content-pillar/embed/{file_id}",
                    "method": "POST",
                    "pillar": "content-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "embedding_creation",
                    "handler": "handle_embed_content_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Create embeddings for parsed content",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "content_get_embeddings",
                    "path": "/api/v1/content-pillar/embeddings/{content_id}",
                    "method": "GET",
                    "pillar": "content-pillar",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "embedding_retrieval",
                    "handler": "handle_get_embeddings_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Get embeddings for content",
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
                # REMOVED: All insights-pillar routes - Use insights-solution pillar instead
                # All insights operations now go through InsightsSolutionOrchestratorService
                # New endpoints:
                # - POST /api/v1/insights-solution/analyze
                # - POST /api/v1/insights-solution/mapping
                # - POST /api/v1/insights-solution/visualize
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
                },
                # Liaison Agents Pillar Routes
                {
                    "route_id": "liaison_agents_send_message",
                    "path": "/api/v1/liaison-agents/send-message-to-pillar-agent",
                    "method": "POST",
                    "pillar": "liaison-agents",
                    "realm": "experience",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "liaison_agent_chat",
                    "handler": "handle_send_message_to_pillar_agent_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Send message to pillar-specific liaison agent",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "liaison_agents_conversation_history",
                    "path": "/api/v1/liaison-agents/get-pillar-conversation-history/{session_id}/{pillar}",
                    "method": "GET",
                    "pillar": "liaison-agents",
                    "realm": "experience",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "liaison_agent_conversation_history",
                    "handler": "handle_get_pillar_conversation_history_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Get conversation history for pillar-specific liaison agent",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "liaison_agents_health",
                    "path": "/api/v1/liaison-agents/health",
                    "method": "GET",
                    "pillar": "liaison-agents",
                    "realm": "experience",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "health_check",
                    "handler": "handle_liaison_agents_pillar_health_check_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Liaison agents pillar health check",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                # Journey/Guide Agent Routes (from JourneyRealmBridge via Experience Foundation SDK)
                {
                    "route_id": "guide_agent_analyze_intent",
                    "path": "/api/v1/journey/guide-agent/analyze-user-intent",
                    "method": "POST",
                    "pillar": "journey",
                    "realm": "journey",
                    "service_name": "JourneyRealmBridge",
                    "capability_name": "intent_analysis",
                    "handler": "route_to_journey_bridge",
                    "handler_service": "FrontendGatewayService",
                    "description": "Analyze user intent for Guide Agent",
                    "version": "v1",
                    "defined_by": "experience_foundation_sdk"
                },
                {
                    "route_id": "guide_agent_get_journey_guidance",
                    "path": "/api/v1/journey/guide-agent/get-journey-guidance",
                    "method": "POST",
                    "pillar": "journey",
                    "realm": "journey",
                    "service_name": "JourneyRealmBridge",
                    "capability_name": "journey_guidance",
                    "handler": "route_to_journey_bridge",
                    "handler_service": "FrontendGatewayService",
                    "description": "Get journey guidance (recommended next pillar) for Guide Agent",
                    "version": "v1",
                    "defined_by": "experience_foundation_sdk"
                },
                {
                    "route_id": "guide_agent_get_conversation_history",
                    "path": "/api/v1/journey/guide-agent/get-conversation-history/{session_id}",
                    "method": "GET",
                    "pillar": "journey",
                    "realm": "journey",
                    "service_name": "JourneyRealmBridge",
                    "capability_name": "conversation_history",
                    "handler": "route_to_journey_bridge",
                    "handler_service": "FrontendGatewayService",
                    "description": "Get conversation history for Guide Agent",
                    "version": "v1",
                    "defined_by": "experience_foundation_sdk"
                },
                # Session Pillar Routes
                {
                    "route_id": "session_create_user_session",
                    "path": "/api/v1/session/create-user-session",
                    "method": "POST",
                    "pillar": "session",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "session_creation",
                    "handler": "handle_create_user_session_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Create user session",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "session_get_session_details",
                    "path": "/api/v1/session/get-session-details/{session_id}",
                    "method": "GET",
                    "pillar": "session",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "session_details",
                    "handler": "handle_get_session_details_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Get session details",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "session_get_session_state",
                    "path": "/api/v1/session/get-session-state/{session_id}",
                    "method": "GET",
                    "pillar": "session",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "session_state",
                    "handler": "handle_get_session_state_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Get session state",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                },
                {
                    "route_id": "session_health",
                    "path": "/api/v1/session/health",
                    "method": "GET",
                    "pillar": "session",
                    "realm": "business_enablement",
                    "service_name": "FrontendGatewayService",
                    "capability_name": "health_check",
                    "handler": "handle_session_pillar_health_check_request",
                    "handler_service": "FrontendGatewayService",
                    "description": "Session pillar health check",
                    "version": "v1",
                    "defined_by": "experience_foundation"
                }
            ]
            
            # Register each route
            routes_registered = 0
            for route_metadata in routes_to_register:
                try:
                    # Skip handler check for Journey routes (handled directly by FastAPI via JourneyRealmBridge)
                    handler_name = route_metadata.get("handler")
                    if route_metadata.get("realm") == "journey":
                        # Journey routes are handled by JourneyRealmBridge, not FrontendGatewayService
                        # We register them in Curator for discovery, but they're executed by FastAPI directly
                        self.logger.debug(f"📋 Registering Journey route (handled by FastAPI): {route_metadata['path']}")
                    elif not hasattr(self, handler_name):
                        self.logger.warning(f"⚠️ Handler method not found: {handler_name}, skipping route {route_metadata.get('path')}")
                        continue
                    
                    # Register route via Curator's register_route wrapper (avoids coroutine issues)
                    self.logger.debug(f"📋 Registering route: {route_metadata['method']} {route_metadata['path']} (handler: {handler_name})")
                    
                    success = await curator.register_route(
                        route_metadata=route_metadata,
                        user_context=None  # System registration, no user context needed
                    )
                    
                    if success:
                        routes_registered += 1
                        self.logger.debug(f"✅ Route registered: {route_metadata['path']}")
                    else:
                        self.logger.warning(f"⚠️ Failed to register route: {route_metadata['path']} (register_route returned False)")
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Error registering route {route_metadata.get('path')}: {e}")
                    import traceback
                    self.logger.debug(f"Traceback: {traceback.format_exc()}")
            
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
            
            # Get RouteRegistryService from Curator - use direct access (most reliable)
            route_registry = None
            try:
                # Direct access to route_registry (CuratorFoundationService has this as an attribute)
                if hasattr(curator, 'route_registry'):
                    route_registry = curator.route_registry
                    self.logger.debug("✅ Got RouteRegistryService via curator.route_registry (discovery)")
                elif hasattr(curator, 'route_registry_service'):
                    route_registry = curator.route_registry_service
                    self.logger.debug("✅ Got RouteRegistryService via curator.route_registry_service (discovery)")
                else:
                    self.logger.warning("⚠️ Curator does not have route_registry or route_registry_service attribute (discovery)")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get RouteRegistryService: {e}")
                import traceback
                self.logger.debug(f"Traceback: {traceback.format_exc()}")
            
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
                                        # ✅ Extract user_context from request_body or user_context parameter
                                        # Priority: 1) request_body.user_context (dict), 2) user_context parameter (UserContext object), 3) None
                                        user_context_dict = request_body.get("user_context")
                                        if user_context_dict and isinstance(user_context_dict, dict):
                                            # If request_body has user_context as dict, use it (from Universal Pillar Router)
                                            user_context = user_context_dict
                                            self.logger.info(f"✅ [ADAPTER] Using user_context from request_body: permissions={user_context.get('permissions')}")
                                        elif user_context and hasattr(user_context, 'permissions'):
                                            # Convert UserContext object to dict format expected by handler
                                            user_context = {
                                                "user_id": user_context.user_id,
                                                "tenant_id": getattr(user_context, 'tenant_id', None),
                                                "permissions": user_context.permissions if hasattr(user_context, 'permissions') else [],
                                                "roles": getattr(user_context, 'roles', []),
                                                "email": getattr(user_context, 'email', None),
                                                "session_id": getattr(user_context, 'session_id', None),
                                                "workflow_id": getattr(user_context, 'workflow_id', None)
                                            }
                                            self.logger.info(f"✅ [ADAPTER] Converted UserContext object to dict: permissions={user_context.get('permissions')}")
                                        else:
                                            # Fallback: try to get from request_body params (Universal Pillar Router might have put it there)
                                            user_context = {
                                                "user_id": user_id,
                                                "permissions": request_body.get("permissions") or [],
                                                "tenant_id": request_body.get("tenant_id"),
                                                "roles": request_body.get("roles") or [],
                                                "email": request_body.get("email"),
                                                "session_id": request_body.get("session_id"),
                                                "workflow_id": request_body.get("workflow_id")
                                            }
                                            self.logger.warning(f"⚠️ [ADAPTER] No user_context found, built from request_body params: permissions={user_context.get('permissions')}")
                                        return await original_handler(
                                            file_data=request_body.get("file_data"),
                                            filename=request_body.get("filename"),
                                            content_type=request_body.get("content_type"),
                                            user_id=user_id,
                                            session_id=request_body.get("session_id"),
                                            copybook_data=request_body.get("copybook_data"),
                                            copybook_filename=request_body.get("copybook_filename"),
                                            user_context=user_context  # ✅ Pass user_context with permissions
                                        )
                                    elif handler_name == "handle_content_pillar_health_check_request":
                                        return await original_handler()
                                    # REMOVED: handle_insights_pillar_health_check_request - Use insights-solution pillar
                                    elif handler_name == "handle_insights_pillar_health_check_request":
                                        return {"success": False, "error": "Endpoint removed - Use insights-solution pillar"}
                                    elif handler_name == "handle_operations_pillar_health_check_request":
                                        return await original_handler()
                                    elif handler_name == "handle_business_outcomes_health_check_request":
                                        return await original_handler()
                                    elif handler_name == "handle_list_parsed_files_request":
                                        return await original_handler(request_body=request_body, user_context=user_context)
                                    elif handler_name == "handle_preview_parsed_file_request":
                                        # Extract parsed_file_id from path params
                                        parsed_file_id = request_body.get("parsed_file_id") or request_body.get("path_params", {}).get("parsed_file_id")
                                        if not parsed_file_id:
                                            return {"success": False, "error": "parsed_file_id required"}
                                        return await original_handler(parsed_file_id=parsed_file_id, request_body=request_body, user_context=user_context)
                                    elif handler_name == "handle_list_uploaded_files_request":
                                        return await original_handler(user_id=user_id)
                                    elif handler_name == "handle_get_file_details_request":
                                        # Extract file_id from path (stored in request_body by _route_via_discovery)
                                        file_id = request_body.get("file_id")
                                        return await original_handler(file_id=file_id, user_id=user_id)
                                    elif handler_name == "handle_delete_file_request":
                                        # Extract file_id from path (stored in request_body by _route_via_discovery)
                                        file_id = request_body.get("file_id") or request_body.get("path_params", {}).get("file_id")
                                        if not file_id:
                                            return {"success": False, "error": "file_id is required"}
                                        return await original_handler(file_id=file_id, user_id=user_id)
                                    elif handler_name == "handle_embed_content_request":
                                        # Extract file_id from path params (should be set by _route_via_discovery)
                                        file_id = request_body.get("file_id") or request_body.get("path_params", {}).get("file_id")
                                        # Debug logging
                                        self.logger.info(f"🔍 [handle_embed_content_request] file_id from request_body: {request_body.get('file_id')}, from path_params: {request_body.get('path_params', {}).get('file_id')}, final: {file_id}")
                                        self.logger.info(f"🔍 [handle_embed_content_request] request_body keys: {list(request_body.keys())}")
                                        
                                        if not file_id:
                                            self.logger.error(f"❌ [handle_embed_content_request] file_id is None - cannot proceed with embedding creation")
                                            return {
                                                "success": False,
                                                "error": "file_id is required for embedding creation",
                                                "message": "file_id not found in request"
                                            }
                                        
                                        return await original_handler(
                                            file_id=file_id,
                                            parsed_file_id=request_body.get("parsed_file_id"),
                                            content_metadata=request_body.get("content_metadata", {}),
                                            user_id=user_id or "anonymous",
                                            user_context=request_body.get("user_context")
                                        )
                                    elif handler_name == "handle_get_embeddings_request":
                                        # Extract content_id from path params
                                        content_id = request_body.get("content_id") or request_body.get("path_params", {}).get("content_id")
                                        # Debug logging
                                        self.logger.info(f"🔍 [handle_get_embeddings_request ADAPTER] request_body keys: {list(request_body.keys()) if isinstance(request_body, dict) else 'NOT_A_DICT'}")
                                        self.logger.info(f"🔍 [handle_get_embeddings_request ADAPTER] request_body.get('content_id'): {request_body.get('content_id')}")
                                        self.logger.info(f"🔍 [handle_get_embeddings_request ADAPTER] request_body.get('path_params'): {request_body.get('path_params')}")
                                        self.logger.info(f"🔍 [handle_get_embeddings_request ADAPTER] Extracted content_id: {content_id}")
                                        # ✅ user_context is now from request scope (set in route_frontend_request)
                                        return await original_handler(
                                            content_id=content_id,
                                            user_id=user_id or "anonymous"
                                        )
                                    elif handler_name == "handle_process_file_request":
                                        file_id = request_body.get("file_id")
                                        
                                        # Extract processing_options from request_body - it might be in "options" or "processing_options"
                                        processing_options = request_body.get("options") or request_body.get("processing_options")
                                        # Also include action if present
                                        if request_body.get("action"):
                                            if not processing_options:
                                                processing_options = {}
                                            processing_options["action"] = request_body.get("action")
                                        
                                        result = await original_handler(
                                            file_id=file_id,
                                            user_id=user_id,
                                            copybook_file_id=request_body.get("copybook_file_id"),
                                            processing_options=processing_options
                                        )
                                        
                                        # Add debug info to result
                                        if isinstance(result, dict):
                                            result["_debug_adapter"] = {
                                                "request_body_keys": list(request_body.keys()) if isinstance(request_body, dict) else "NOT_A_DICT",
                                                "processing_options": processing_options,
                                                "handler_path": "adapter_from_register_routes_with_curator"
                                            }
                                        
                                        return result
                                    # REMOVED: All insights-pillar handlers - Use insights-solution pillar instead
                                    elif handler_name in [
                                        "handle_analyze_content_for_insights_semantic_request",
                                        "handle_query_insights_analysis_request",
                                        "handle_get_available_content_metadata_request",
                                        "handle_validate_content_metadata_for_insights_request",
                                        "handle_get_insights_analysis_results_request",
                                        "handle_get_insights_analysis_visualizations_request",
                                        "handle_list_user_insights_analyses_request"
                                    ]:
                                        return {
                                            "success": False,
                                            "error": "Endpoint Removed",
                                            "message": f"Handler {handler_name} has been removed. Use /api/v1/insights-solution/* endpoints instead"
                                        }
                                    elif handler_name == "handle_send_message_to_pillar_agent_request":
                                        return await original_handler(
                                            message=request_body.get("message"),
                                            pillar=request_body.get("pillar"),
                                            session_id=request_body.get("session_id"),
                                            conversation_id=request_body.get("conversation_id"),
                                            user_id=user_id,
                                            session_token=request_body.get("session_token")
                                        )
                                    elif handler_name == "handle_get_pillar_conversation_history_request":
                                        # Extract session_id and pillar from path parameters
                                        session_id = request_body.get("session_id") or request_body.get("path_params", {}).get("session_id")
                                        pillar = request_body.get("pillar") or request_body.get("path_params", {}).get("pillar")
                                        return await original_handler(
                                            session_id=session_id,
                                            pillar=pillar,
                                            user_id=user_id
                                        )
                                    elif handler_name == "handle_liaison_agents_pillar_health_check_request":
                                        return await original_handler()
                                    elif handler_name == "handle_create_user_session_request":
                                        # Explicit handler to avoid passing workflow_id or other unexpected kwargs
                                        return await original_handler(
                                            user_id=request_body.get("user_id") or user_id or "anonymous",
                                            session_type=request_body.get("session_type", "mvp"),
                                            context=request_body.get("context")
                                        )
                                    elif handler_name == "handle_get_session_details_request":
                                        session_id = request_body.get("session_id") or request_body.get("path_params", {}).get("session_id")
                                        return await original_handler(
                                            session_id=session_id,
                                            user_id=user_id or "anonymous"
                                        )
                                    elif handler_name == "handle_get_session_state_request":
                                        session_id = request_body.get("session_id") or request_body.get("path_params", {}).get("session_id")
                                        return await original_handler(
                                            session_id=session_id,
                                            user_id=user_id or "anonymous"
                                        )
                                    elif handler_name == "handle_session_pillar_health_check_request":
                                        return await original_handler()
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
            # ✅ Phase 0.5: Use user_context from request if available (includes workflow_id)
            request_user_context = request.get("user_context", {})
            user_id = request_user_context.get("user_id") or request.get("user_id") or request.get("params", {}).get("user_id", "anonymous")
            workflow_id = request_user_context.get("workflow_id") or request.get("params", {}).get("workflow_id")
            
            # Debug logging
            self.logger.info(f"🔍 [_route_via_discovery] request_user_context: {request_user_context}")
            self.logger.info(f"🔍 [_route_via_discovery] request_user_context.get('permissions'): {request_user_context.get('permissions') if isinstance(request_user_context, dict) else 'NOT_A_DICT'}")
            request_params = request.get('params', {})
            request_params_permissions = request_params.get('permissions', []) if isinstance(request_params, dict) else []
            self.logger.info(f"🔍 [_route_via_discovery] request.get('params').get('permissions'): {request_params_permissions}")
            
            # Get permissions - prioritize request_user_context (from route_frontend_request)
            # ✅ CRITICAL FIX: Check if permissions key exists, not just if it's truthy (empty list is falsy!)
            permissions = []
            if isinstance(request_user_context, dict) and "permissions" in request_user_context:
                permissions = request_user_context.get("permissions", [])
                self.logger.info(f"🔍 [_route_via_discovery] Got permissions from request_user_context: {permissions}")
            if not permissions and "permissions" in request.get("params", {}):
                permissions = request.get("params", {}).get("permissions", [])
                self.logger.info(f"🔍 [_route_via_discovery] Got permissions from request.params: {permissions}")
            
            self.logger.info(f"🔍 [_route_via_discovery] Final permissions: {permissions}")
            
            user_context = UserContext(
                user_id=user_id,
                email=request_user_context.get("email") or request.get("params", {}).get("email", f"{user_id}@example.com"),
                full_name=request_user_context.get("full_name") or request.get("params", {}).get("full_name", user_id),
                session_id=request_user_context.get("session_id") or request.get("params", {}).get("session_id", ""),
                permissions=permissions if permissions else [],  # Ensure it's always a list
                tenant_id=request_user_context.get("tenant_id") or request.get("params", {}).get("tenant_id"),
                workflow_id=workflow_id  # ✅ Phase 0.5: Add workflow_id to UserContext
            )
            
            self.logger.info(f"🔍 [_route_via_discovery] UserContext created with permissions: {user_context.permissions}")
            
            # Execute route with middleware via APIRoutingUtility
            # route_request() handles route matching internally via _find_matching_route()
            # Note: We need to extract path parameters from endpoint for handlers that need them
            # Initialize request_data first before using it
            request_data = request.get("params", {}).copy()
            
            # ✅ CRITICAL FIX: Extract processing_options from request body (not just params)
            # Test scripts send processing_options in JSON body, which gets put in params by universal_pillar_router
            # But we also check the request directly in case it's at the top level
            if "processing_options" in request_data:
                # Already in params (from universal_pillar_router)
                pass
            elif "processing_options" in request:
                request_data["processing_options"] = request["processing_options"]
            elif "options" in request_data:
                # Also support "options" key
                request_data["processing_options"] = request_data["options"]
            elif "options" in request:
                request_data["options"] = request["options"]
                request_data["processing_options"] = request["options"]
            
            # ✅ Phase 0.5: Store workflow_id in request_data for handlers to access
            if workflow_id:
                request_data["workflow_id"] = workflow_id
            
            # ✅ Add user_context to request_data so it's available in request_body for adapters
            if user_context and hasattr(user_context, 'permissions'):
                # Debug logging
                self.logger.info(f"🔍 [_route_via_discovery] user_context.permissions: {user_context.permissions if hasattr(user_context, 'permissions') else 'NO_PERMISSIONS_ATTR'}")
                self.logger.info(f"🔍 [_route_via_discovery] user_context type: {type(user_context)}")
                
                request_data["user_context"] = {
                    "user_id": user_context.user_id,
                    "tenant_id": getattr(user_context, 'tenant_id', None),
                    "permissions": user_context.permissions if hasattr(user_context, 'permissions') and user_context.permissions else [],
                    "roles": getattr(user_context, 'roles', []),
                    "email": getattr(user_context, 'email', None),
                    "session_id": getattr(user_context, 'session_id', None),
                    "workflow_id": getattr(user_context, 'workflow_id', None)
                }
                
                self.logger.info(f"🔍 [_route_via_discovery] request_data['user_context']['permissions']: {request_data['user_context']['permissions']}")
            
            # Extract path parameters (e.g., /api/v1/content-pillar/process-file/{file_id})
            # Store in request_data so adapter can access them
            path_parts = endpoint.strip("/").split("/")
            if len(path_parts) >= 5:  # /api/v1/pillar/path/{id}
                # Try to extract ID from path (last part after the action)
                action_part = path_parts[-2] if len(path_parts) > 4 else None
                id_part = path_parts[-1] if len(path_parts) > 4 else None
                
                # Map common patterns
                # ✅ Check "embeddings" FIRST (more specific) before "embed" (less specific)
                if "embeddings" in action_part or "embeddings" in endpoint.lower():
                    # Extract content_id from embeddings endpoint: /api/v1/content-pillar/embeddings/{content_id}
                    if id_part and id_part not in ["health"]:
                        request_data["content_id"] = id_part
                        # Also store in path_params for handler access
                        if "path_params" not in request_data:
                            request_data["path_params"] = {}
                        request_data["path_params"]["content_id"] = id_part
                        # Debug logging
                        self.logger.info(f"🔍 [path_param_extraction] Extracted content_id from embeddings endpoint: {id_part}")
                elif "embed" in action_part or "embed" in endpoint.lower():
                    # Extract file_id from embed endpoint: /api/v1/content-pillar/embed/{file_id}
                    if id_part and id_part not in ["health"]:
                        request_data["file_id"] = id_part
                        # Also store in path_params for handler access
                        if "path_params" not in request_data:
                            request_data["path_params"] = {}
                        request_data["path_params"]["file_id"] = id_part
                        # Debug logging
                        self.logger.info(f"🔍 [path_param_extraction] Extracted file_id from embed endpoint: {id_part}")
                elif "preview-parsed-file" in endpoint.lower():
                    # Extract parsed_file_id from preview endpoint: /api/v1/content-pillar/preview-parsed-file/{parsed_file_id}
                    if id_part:
                        request_data["parsed_file_id"] = id_part
                        # Also store in path_params for handler access
                        if "path_params" not in request_data:
                            request_data["path_params"] = {}
                        request_data["path_params"]["parsed_file_id"] = id_part
                        self.logger.info(f"🔍 [path_param_extraction] Extracted parsed_file_id from preview endpoint: {id_part}")
                elif "preview-embeddings" in endpoint.lower():
                    # Extract content_id from preview-embeddings endpoint: /api/v1/content-pillar/preview-embeddings/{content_id}
                    if id_part:
                        request_data["content_id"] = id_part
                        # Also store in path_params for handler access
                        if "path_params" not in request_data:
                            request_data["path_params"] = {}
                        request_data["path_params"]["content_id"] = id_part
                        self.logger.info(f"🔍 [path_param_extraction] Extracted content_id from preview-embeddings endpoint: {id_part}")
                elif "delete-file" in endpoint.lower():
                    # Extract file_id from delete-file endpoint: /api/v1/content-pillar/delete-file/{file_id}
                    if id_part and id_part not in ["health"]:
                        request_data["file_id"] = id_part
                        # Also store in path_params for handler access
                        if "path_params" not in request_data:
                            request_data["path_params"] = {}
                        request_data["path_params"]["file_id"] = id_part
                        self.logger.info(f"🔍 [path_param_extraction] Extracted file_id from delete-file endpoint: {id_part}")
                elif "file" in action_part or "file" in (path_parts[-2] if len(path_parts) > 3 else ""):
                    if id_part and id_part not in ["health", "list-uploaded-files", "upload-file", "list-parsed-files", "preview-parsed-file", "delete-file"]:
                        request_data["file_id"] = id_part
                elif "analysis" in action_part:
                    if id_part and id_part not in ["results", "visualizations"]:
                        request_data["analysis_id"] = id_part
                elif "session" in endpoint.lower():
                    # Extract session_id from session endpoints
                    if id_part and id_part not in ["health", "create-user-session"]:
                        request_data["session_id"] = id_part
                    # Also store in path_params for handler access
                    if "path_params" not in request_data:
                        request_data["path_params"] = {}
                    if id_part and id_part not in ["health", "create-user-session"]:
                        request_data["path_params"]["session_id"] = id_part
                elif "liaison-agents" in endpoint.lower():
                    # Extract session_id and pillar from liaison-agents endpoints
                    # Format: /api/v1/liaison-agents/get-pillar-conversation-history/{session_id}/{pillar}
                    if len(path_parts) >= 7:  # /api/v1/liaison-agents/get-pillar-conversation-history/{session_id}/{pillar}
                        # Second-to-last part is session_id, last part is pillar
                        session_id_part = path_parts[-2] if len(path_parts) >= 7 else None
                        pillar_part = path_parts[-1] if len(path_parts) >= 7 else None
                        if session_id_part and session_id_part not in ["health", "send-message-to-pillar-agent"]:
                            request_data["session_id"] = session_id_part
                        if pillar_part and pillar_part not in ["health", "send-message-to-pillar-agent"]:
                            request_data["pillar"] = pillar_part
                        # Also store in path_params for handler access
                        if "path_params" not in request_data:
                            request_data["path_params"] = {}
                        if session_id_part:
                            request_data["path_params"]["session_id"] = session_id_part
                        if pillar_part:
                            request_data["path_params"]["pillar"] = pillar_part
            
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
    
    async def route_frontend_request(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simplified pillar-based request router.
        
        Routes requests directly to Journey Orchestrators based on pillar name.
        Journey Orchestrators handle internal routing to specific handlers.
        
        This replaces the complex route discovery/matching with simple, direct routing.
        
        Args:
            request: Frontend request data
                - endpoint: "/api/v1/{pillar}/{path}" 
                - method: "GET" | "POST" | "PUT" | "DELETE"
                - params: Request parameters/body
                - headers: Optional headers (may include X-Tenant-Id, X-User-Id from Traefik ForwardAuth)
                - query_params: Optional query parameters
                - user_id: Optional user identifier
                - user_context: Optional user context (from universal_pillar_router)
        
        Returns:
            Frontend-ready response
        """
        try:
            # Start telemetry tracking
            endpoint = request.get("endpoint", "")
            method = request.get("method", "POST")
            await self.log_operation_with_telemetry("route_frontend_request_start", success=True, metadata={"endpoint": endpoint, "method": method})
            
            # Extract tenant context from Traefik ForwardAuth headers (Phase 1: Security Integration)
            headers = request.get("headers", {})
            tenant_id = headers.get("X-Tenant-Id") or request.get("params", {}).get("tenant_id")
            user_id = headers.get("X-User-Id") or request.get("user_id") or request.get("params", {}).get("user_id")
            user_email = headers.get("X-User-Email") or request.get("params", {}).get("email")
            user_roles = headers.get("X-User-Roles", "").split(",") if headers.get("X-User-Roles") else request.get("params", {}).get("roles", [])
            user_permissions = headers.get("X-User-Permissions", "").split(",") if headers.get("X-User-Permissions") else request.get("params", {}).get("permissions", [])
            session_token = headers.get("X-Session-Token") or headers.get("x-session-token") or request.get("params", {}).get("session_token")
            
            # ✅ Phase 0.5: Generate workflow_id at gateway entry point (if not provided)
            # Frontend can send X-Workflow-Id header for multi-step operations
            # If not provided, generate new workflow_id for this request
            # Priority: params (JSON body) > headers > generate new UUID
            # Check params first (request body) since that's where the test passes workflow_id
            workflow_id = (
                request.get("params", {}).get("workflow_id") or  # ✅ Check request body (JSON params) FIRST
                request.get("workflow_id") or 
                headers.get("X-Workflow-Id") or 
                headers.get("x-workflow-id") or
                str(uuid.uuid4())
            )
            
            # ✅ CRITICAL FIX: Preserve permissions from original request.user_context (from universal_pillar_router)
            # universal_pillar_router sets user_context with full permissions from auth validation
            # We MUST preserve these permissions, not overwrite with empty headers
            original_user_context = request.get("user_context", {})
            if isinstance(original_user_context, dict):
                # Prioritize permissions from original user_context (from universal_pillar_router)
                if original_user_context.get("permissions"):
                    user_permissions = original_user_context.get("permissions")
                    self.logger.info(f"✅ [route_frontend_request] Using permissions from original user_context: {user_permissions}")
                # Also preserve other fields from original if they're more complete
                if original_user_context.get("tenant_id") and not tenant_id:
                    tenant_id = original_user_context.get("tenant_id")
                if original_user_context.get("roles") and user_roles == []:
                    user_roles = original_user_context.get("roles", user_roles)
                if original_user_context.get("email") and not user_email:
                    user_email = original_user_context.get("email")
            
            # Debug logging
            self.logger.info(f"🔍 [route_frontend_request] Final user_permissions: {user_permissions}")
            self.logger.info(f"🔍 [route_frontend_request] Final tenant_id: {tenant_id}")
            
            user_context = {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "session_id": session_token,
                "workflow_id": workflow_id,  # ✅ Phase 0.5: Add workflow_id for correlation
                "email": user_email,
                "roles": user_roles,
                "permissions": user_permissions  # ✅ This should now have permissions from original user_context
            }
            
            # ✅ Set request-scoped user context (accessible throughout request lifecycle)
            from utilities.security_authorization.request_context import set_request_user_context
            set_request_user_context(user_context)
            
            # Add user_context and workflow_id to request for propagation
            request["user_context"] = user_context
            if "params" not in request:
                request["params"] = {}
            request["params"]["workflow_id"] = workflow_id
            
            # Add tenant context to request params if not already present
            if tenant_id and "tenant_id" not in request.get("params", {}):
                request["params"]["tenant_id"] = tenant_id
            
            # Validate tenant access if tenant_id is provided
            if tenant_id:
                tenant = self.get_tenant()
                if tenant:
                    try:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("route_frontend_request_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("route_frontend_request_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied",
                                "tenant_id": tenant_id
                            }
                    except Exception as tenant_error:
                        self.logger.warning(f"⚠️ Tenant validation error: {tenant_error}")
            
            # ✅ SIMPLIFIED ROUTING: Pillar-based direct routing
            # Parse endpoint: /api/v1/{pillar}/{path}
            # Example: /api/v1/content-pillar/delete-file/441ab256-...
            parts = endpoint.strip("/").split("/")
            if len(parts) < 4 or parts[0] != "api" or parts[1] != "v1":
                await self.record_health_metric("route_frontend_request_invalid_endpoint", 1.0, {"endpoint": endpoint})
                await self.log_operation_with_telemetry("route_frontend_request_complete", success=False)
                return {
                    "success": False,
                    "error": "Invalid endpoint format. Expected: /api/v1/{pillar}/{path}",
                    "endpoint": endpoint
                }
            
            pillar = parts[2]  # content-pillar, insights-pillar, etc.
            path = "/".join(parts[3:])  # Rest of the path (e.g., "delete-file/441ab256-...")
            
            # Get orchestrator for pillar
            start_time = datetime.utcnow()
            orchestrator = await self._get_orchestrator_for_pillar(pillar)
            if not orchestrator:
                await self.record_health_metric("route_frontend_request_orchestrator_not_found", 1.0, {"pillar": pillar})
                await self.log_operation_with_telemetry("route_frontend_request_complete", success=False)
                return {
                    "success": False,
                    "error": f"Orchestrator not available for pillar: {pillar}",
                    "pillar": pillar,
                    "endpoint": endpoint
                }
            
            # Route to orchestrator's handle_request method
            # Orchestrators handle internal routing to specific handlers
            # Special case: If orchestrator is self (session pillar), use our own handle_request
            if orchestrator is self:
                result = await self.handle_request(
                    method=method,
                    path=path,
                    params=request.get("params", {}),
                    user_context=user_context,
                    headers=headers,
                    query_params=request.get("query_params", {})
                )
            elif not hasattr(orchestrator, 'handle_request'):
                # Debug: Check what methods the orchestrator actually has
                methods = [m for m in dir(orchestrator) if not m.startswith('_') and callable(getattr(orchestrator, m, None))]
                self.logger.error(f"❌ Orchestrator {type(orchestrator).__name__} does not have handle_request method")
                self.logger.error(f"🔍 Orchestrator type: {type(orchestrator)}, methods: {methods[:10]}")
                self.logger.error(f"🔍 Has handle_request on class: {hasattr(type(orchestrator), 'handle_request')}")
                self.logger.error(f"🔍 Has handle_request on instance: {hasattr(orchestrator, 'handle_request')}")
                await self.record_health_metric("route_frontend_request_no_handler_method", 1.0, {"pillar": pillar})
                await self.log_operation_with_telemetry("route_frontend_request_complete", success=False)
                return {
                    "success": False,
                    "error": f"Orchestrator {type(orchestrator).__name__} does not support handle_request",
                    "pillar": pillar
                }
            else:
                # ✅ HYBRID APPROACH: Try direct orchestrator call first (faster, more reliable)
                # If orchestrator has handle_request, use it directly for routes it supports
                # This bypasses route discovery issues and is more reliable
                self.logger.info(f"✅ Using direct orchestrator.handle_request for {method} {path}")
                result = await orchestrator.handle_request(
                    method=method,
                    path=path,
                    params=request.get("params", {}),
                    user_context=user_context,
                    headers=headers,
                    query_params=request.get("query_params", {})
                )
                
                # If orchestrator returns "Route not found", fall back to _route_via_discovery
                if result.get("error") == "Route not found" and self.api_router:
                    self.logger.info(f"⚠️ Orchestrator returned 'Route not found', trying _route_via_discovery (endpoint: {endpoint})")
                    result = await self._route_via_discovery(request)
            elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Track metrics for routing
            if self.routing_monitoring_enabled:
                self.routing_metrics["routing"]["requests"] += 1
                self.routing_metrics["routing"]["total_time_ms"] += elapsed_ms
                if result.get("success") is not False and result.get("error") != "Route not found":
                    self.routing_metrics["routing"]["successes"] += 1
                else:
                    self.routing_metrics["routing"]["errors"] += 1
                # Update average
                if self.routing_metrics["routing"]["requests"] > 0:
                    self.routing_metrics["routing"]["avg_time_ms"] = (
                        self.routing_metrics["routing"]["total_time_ms"] / 
                        self.routing_metrics["routing"]["requests"]
                    )
                self.logger.debug(f"✅ Routing: {endpoint} ({elapsed_ms:.2f}ms)")
            
            # Check if result indicates route not found
            if result and result.get("error") == "Route not found":
                await self.record_health_metric("route_frontend_request_no_handler", 1.0, {"endpoint": endpoint})
                await self.log_operation_with_telemetry("route_frontend_request_complete", success=False)
                return result
            
            # Transform for frontend
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
                            "method": method
                        }
                    )
                except Exception as log_error:
                    self.logger.warning(f"⚠️  Failed to log request: {log_error}")
                
                # Record health metric
                await self.record_health_metric("route_frontend_request_success", 1.0, {"endpoint": endpoint})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("route_frontend_request_complete", success=True)
                
                return frontend_response
            
            # No result - return error
            await self.record_health_metric("route_frontend_request_no_handler", 1.0, {"endpoint": endpoint})
            await self.log_operation_with_telemetry("route_frontend_request_complete", success=False)
            
            return {
                "success": False,
                "error": "Route Not Found",
                "message": f"No route found for: {endpoint}"
            }
            
        except Exception as e:
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
    
    async def _get_orchestrator_for_pillar(self, pillar: str) -> Optional[Any]:
        """
        Get Journey Orchestrator for a pillar using simplified discovery.
        
        Special handling:
        - "session" pillar: Handled directly by FrontendGatewayService (returns self)
        - Other pillars: Discovered via Curator
        
        Args:
            pillar: Pillar name (e.g., "content-pillar", "insights-pillar", "session")
        
        Returns:
            Orchestrator instance (or self for session pillar) or None if not found
        """
        # Special case: session pillar is handled directly by FrontendGatewayService
        if pillar == "session":
            self.logger.info(f"✅ Session pillar - handled directly by FrontendGatewayService")
            return self  # Return self so handle_request can route to session handlers
        
        # Pillar → Orchestrator mapping
        pillar_map = {
            "mvp-solution": "MVPSolutionOrchestratorService",  # NEW: MVP Solution entry point (Solution → Journey → Realm)
            "content-pillar": "ContentJourneyOrchestrator",
            "insights-solution": "InsightsSolutionOrchestratorService",  # New pattern (Solution → Journey → Realm)
            "data-solution": "DataSolutionOrchestratorService",  # Phase 4: Data Mash (Solution → Journey → Realm)
            "operations-solution": "OperationsSolutionOrchestratorService",  # NEW: Operations Solution Orchestrator (Solution → Journey → Realm)
            "operations-pillar": "OperationsOrchestrator",  # Legacy - use operations-solution instead
            "business-outcomes-solution": "BusinessOutcomesSolutionOrchestratorService",  # NEW: Business Outcomes Solution Orchestrator (Solution → Journey → Realm)
            "business-outcomes-pillar": "BusinessOutcomesOrchestrator",  # Legacy - use business-outcomes-solution instead
        }
        
        # Legacy pillar mapping (removed - use insights-solution instead)
        # "insights-pillar": "InsightsOrchestrator" - REMOVED: Use insights-solution
        
        orchestrator_name = pillar_map.get(pillar)
        if not orchestrator_name:
            self.logger.warning(f"⚠️ Unknown pillar: {pillar}")
            return None
        
        # Discover orchestrator via Curator
        try:
            curator = self.di_container.get_foundation_service("CuratorFoundationService")
            if not curator:
                self.logger.error("❌ CuratorFoundationService not available")
                return None
            
            orchestrator = await curator.discover_service_by_name(orchestrator_name)
            if not orchestrator:
                self.logger.warning(f"⚠️ {orchestrator_name} not found via Curator")
                # Fallback: Try direct import for Solution Orchestrators and Journey Orchestrators
                if orchestrator_name == "ContentJourneyOrchestrator":
                    try:
                        # Force reload the module to get the latest code
                        import importlib
                        import backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator as content_module
                        importlib.reload(content_module)
                        ContentJourneyOrchestrator = content_module.ContentJourneyOrchestrator
                        
                        orchestrator = ContentJourneyOrchestrator(
                            platform_gateway=self.platform_gateway,
                            di_container=self.di_container
                        )
                        await orchestrator.initialize()
                        self.logger.info(f"✅ {orchestrator_name} initialized directly as fallback")
                        # Verify the method exists
                        if hasattr(orchestrator, 'handle_request'):
                            self.logger.info(f"✅ Verified: {orchestrator_name} has handle_request method")
                        else:
                            self.logger.warning(f"⚠️ {orchestrator_name} does not have handle_request method")
                    except Exception as e:
                        self.logger.error(f"❌ Failed to initialize {orchestrator_name} as fallback: {e}")
                        import traceback
                        self.logger.error(f"   Traceback: {traceback.format_exc()}")
                        return None
                elif orchestrator_name == "OperationsSolutionOrchestratorService":
                    try:
                        # Force reload the module to get the latest code
                        import importlib
                        import backend.solution.services.operations_solution_orchestrator_service.operations_solution_orchestrator_service as ops_module
                        importlib.reload(ops_module)
                        OperationsSolutionOrchestratorService = ops_module.OperationsSolutionOrchestratorService
                        
                        orchestrator = OperationsSolutionOrchestratorService(
                            service_name="OperationsSolutionOrchestratorService",
                            realm_name="solution",
                            platform_gateway=self.platform_gateway,
                            di_container=self.di_container
                        )
                        await orchestrator.initialize()
                        self.logger.info(f"✅ {orchestrator_name} initialized directly as fallback")
                        # Verify the method exists
                        if hasattr(orchestrator, 'handle_request'):
                            self.logger.info(f"✅ Verified: {orchestrator_name} has handle_request method")
                        else:
                            self.logger.error(f"❌ WARNING: {orchestrator_name} fallback instance does NOT have handle_request method!")
                    except Exception as fallback_error:
                        self.logger.error(f"❌ Fallback initialization failed: {fallback_error}", exc_info=True)
                        return None
                elif orchestrator_name == "InsightsSolutionOrchestratorService":
                    try:
                        # Import and initialize Insights Solution Orchestrator
                        import importlib
                        from backend.solution.services.insights_solution_orchestrator_service.insights_solution_orchestrator_service import InsightsSolutionOrchestratorService
                        
                        orchestrator = InsightsSolutionOrchestratorService(
                            service_name="InsightsSolutionOrchestratorService",
                            realm_name="solution",
                            platform_gateway=self.platform_gateway,
                            di_container=self.di_container
                        )
                        await orchestrator.initialize()
                        self.logger.info(f"✅ {orchestrator_name} initialized directly as fallback")
                        if hasattr(orchestrator, 'handle_request'):
                            self.logger.info(f"✅ Verified: {orchestrator_name} has handle_request method")
                    except Exception as fallback_error:
                        self.logger.error(f"❌ Fallback initialization failed: {fallback_error}", exc_info=True)
                        return None
                elif orchestrator_name == "DataSolutionOrchestratorService":
                    try:
                        # Import and initialize Data Solution Orchestrator
                        import importlib
                        from backend.solution.services.data_solution_orchestrator_service.data_solution_orchestrator_service import DataSolutionOrchestratorService
                        
                        orchestrator = DataSolutionOrchestratorService(
                            service_name="DataSolutionOrchestratorService",
                            realm_name="solution",
                            platform_gateway=self.platform_gateway,
                            di_container=self.di_container
                        )
                        await orchestrator.initialize()
                        self.logger.info(f"✅ {orchestrator_name} initialized directly as fallback")
                        if hasattr(orchestrator, 'handle_request'):
                            self.logger.info(f"✅ Verified: {orchestrator_name} has handle_request method")
                    except Exception as fallback_error:
                        self.logger.error(f"❌ Fallback initialization failed: {fallback_error}", exc_info=True)
                        return None
                elif orchestrator_name == "BusinessOutcomesSolutionOrchestratorService":
                    try:
                        # Import and initialize Business Outcomes Solution Orchestrator
                        import importlib
                        from backend.solution.services.business_outcomes_solution_orchestrator_service.business_outcomes_solution_orchestrator_service import BusinessOutcomesSolutionOrchestratorService
                        
                        orchestrator = BusinessOutcomesSolutionOrchestratorService(
                            service_name="BusinessOutcomesSolutionOrchestratorService",
                            realm_name="solution",
                            platform_gateway=self.platform_gateway,
                            di_container=self.di_container
                        )
                        await orchestrator.initialize()
                        self.logger.info(f"✅ {orchestrator_name} initialized directly as fallback")
                        if hasattr(orchestrator, 'handle_request'):
                            self.logger.info(f"✅ Verified: {orchestrator_name} has handle_request method")
                    except Exception as fallback_error:
                        self.logger.error(f"❌ Fallback initialization failed: {fallback_error}", exc_info=True)
                        return None
                elif orchestrator_name == "MVPSolutionOrchestratorService":
                    try:
                        # Import and initialize MVP Solution Orchestrator
                        import importlib
                        from backend.solution.services.mvp_solution_orchestrator_service.mvp_solution_orchestrator_service import MVPSolutionOrchestratorService
                        
                        orchestrator = MVPSolutionOrchestratorService(
                            service_name="MVPSolutionOrchestratorService",
                            realm_name="solution",
                            platform_gateway=self.platform_gateway,
                            di_container=self.di_container
                        )
                        await orchestrator.initialize()
                        self.logger.info(f"✅ {orchestrator_name} initialized directly as fallback")
                        if hasattr(orchestrator, 'handle_request'):
                            self.logger.info(f"✅ Verified: {orchestrator_name} has handle_request method")
                    except Exception as fallback_error:
                        self.logger.error(f"❌ Fallback initialization failed: {fallback_error}", exc_info=True)
                        return None
                else:
                    return None
            else:
                # Verify the discovered orchestrator has handle_request
                if not hasattr(orchestrator, 'handle_request'):
                    self.logger.warning(f"⚠️ Discovered {orchestrator_name} from Curator does not have handle_request, trying fallback...")
                    # Try fallback initialization
                    if orchestrator_name == "ContentJourneyOrchestrator":
                        try:
                            import importlib
                            import backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator as content_module
                            importlib.reload(content_module)
                            ContentJourneyOrchestrator = content_module.ContentJourneyOrchestrator
                            
                            orchestrator = ContentJourneyOrchestrator(
                                platform_gateway=self.platform_gateway,
                                di_container=self.di_container
                            )
                            await orchestrator.initialize()
                            self.logger.info(f"✅ {orchestrator_name} re-initialized via fallback (Curator instance was stale)")
                        except Exception as fallback_error:
                            self.logger.error(f"❌ Fallback re-initialization failed: {fallback_error}", exc_info=True)
                            # Return the stale one anyway - might still work via old routing
                            pass
            
            self.logger.info(f"✅ Discovered orchestrator: {orchestrator_name} for pillar: {pillar}")
            return orchestrator
            
        except Exception as e:
            self.logger.error(f"❌ Failed to discover orchestrator for {pillar}: {e}", exc_info=True)
            return None
    
    async def handle_document_analysis_request(
        self,
        document_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle document analysis request (Frontend API → ContentOrchestrator).
        
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
    
    # REMOVED: handle_insights_request - Use /api/v1/insights-solution/* endpoints instead
    
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
    # INSURANCE USE CASE HANDLERS (Frontend API → Insurance Orchestrators)
    # ========================================================================
    
    async def handle_ingest_legacy_data_request(
        self,
        request_body: Dict[str, Any],
        user_context: Any
    ) -> Dict[str, Any]:
        """Handle ingest legacy data request."""
        try:
            if not self.insurance_migration_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insurance Migration Orchestrator not available"
                }
            
            # Extract parameters from request body
            file_id = request_body.get("file_id")
            file_data = request_body.get("file_data")
            filename = request_body.get("filename")
            
            # Call orchestrator
            result = await self.insurance_migration_orchestrator.ingest_legacy_data(
                file_id=file_id,
                file_data=file_data,
                filename=filename,
                user_context=user_context
            )
            
            self.logger.info(f"✅ Legacy data ingested: {file_id or filename}")
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Ingest legacy data failed: {e}")
            return {
                "success": False,
                "error": "Ingestion Failed",
                "message": str(e)
            }
    
    async def handle_map_to_canonical_request(
        self,
        request_body: Dict[str, Any],
        user_context: Any
    ) -> Dict[str, Any]:
        """Handle map to canonical request."""
        try:
            if not self.insurance_migration_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insurance Migration Orchestrator not available"
                }
            
            # Extract parameters
            file_id = request_body.get("file_id")
            mapping_strategy = request_body.get("mapping_strategy")
            
            # Call orchestrator
            result = await self.insurance_migration_orchestrator.map_to_canonical(
                file_id=file_id,
                mapping_strategy=mapping_strategy,
                user_context=user_context
            )
            
            self.logger.info(f"✅ Mapped to canonical: {file_id}")
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Map to canonical failed: {e}")
            return {
                "success": False,
                "error": "Mapping Failed",
                "message": str(e)
            }
    
    async def handle_route_policies_request(
        self,
        request_body: Dict[str, Any],
        user_context: Any
    ) -> Dict[str, Any]:
        """Handle route policies request."""
        try:
            if not self.insurance_migration_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insurance Migration Orchestrator not available"
                }
            
            # Extract parameters
            policy_data = request_body.get("policy_data")
            namespace = request_body.get("namespace", "default")
            
            # Call orchestrator
            result = await self.insurance_migration_orchestrator.route_policies(
                policy_data=policy_data,
                namespace=namespace,
                user_context=user_context
            )
            
            self.logger.info(f"✅ Policies routed: {namespace}")
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Route policies failed: {e}")
            return {
                "success": False,
                "error": "Routing Failed",
                "message": str(e)
            }
    
    async def handle_create_wave_request(
        self,
        request_body: Dict[str, Any],
        user_context: Any
    ) -> Dict[str, Any]:
        """Handle create wave request."""
        try:
            if not self.wave_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Wave Orchestrator not available"
                }
            
            # Extract parameters
            wave_config = request_body.get("wave_config")
            
            # Call orchestrator
            result = await self.wave_orchestrator.create_wave(
                wave_config=wave_config,
                user_context=user_context
            )
            
            self.logger.info(f"✅ Wave created: {result.get('wave_id', 'unknown')}")
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Create wave failed: {e}")
            return {
                "success": False,
                "error": "Wave Creation Failed",
                "message": str(e)
            }
    
    async def handle_get_wave_status_request(
        self,
        request_body: Dict[str, Any],
        user_context: Any
    ) -> Dict[str, Any]:
        """Handle get wave status request."""
        try:
            if not self.wave_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Wave Orchestrator not available"
                }
            
            # Extract wave_id from path parameter (should be in request_body from route extraction)
            wave_id = request_body.get("wave_id")
            
            # Call orchestrator
            result = await self.wave_orchestrator.get_wave_status(
                wave_id=wave_id,
                user_context=user_context
            )
            
            self.logger.info(f"✅ Wave status retrieved: {wave_id}")
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Get wave status failed: {e}")
            return {
                "success": False,
                "error": "Status Retrieval Failed",
                "message": str(e)
            }
    
    async def handle_execute_wave_request(
        self,
        request_body: Dict[str, Any],
        user_context: Any
    ) -> Dict[str, Any]:
        """Handle execute wave request."""
        try:
            if not self.wave_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Wave Orchestrator not available"
                }
            
            # Extract wave_id from path parameter
            wave_id = request_body.get("wave_id")
            
            # Call orchestrator
            result = await self.wave_orchestrator.execute_wave(
                wave_id=wave_id,
                user_context=user_context
            )
            
            self.logger.info(f"✅ Wave executed: {wave_id}")
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Execute wave failed: {e}")
            return {
                "success": False,
                "error": "Wave Execution Failed",
                "message": str(e)
            }
    
    async def handle_register_policy_request(
        self,
        request_body: Dict[str, Any],
        user_context: Any
    ) -> Dict[str, Any]:
        """Handle register policy request."""
        try:
            if not self.policy_tracker_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Policy Tracker Orchestrator not available"
                }
            
            # Extract parameters
            policy_id = request_body.get("policy_id")
            location = request_body.get("location")
            metadata = request_body.get("metadata", {})
            
            # Call orchestrator
            result = await self.policy_tracker_orchestrator.register_policy(
                policy_id=policy_id,
                location=location,
                metadata=metadata,
                user_context=user_context
            )
            
            self.logger.info(f"✅ Policy registered: {policy_id}")
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Register policy failed: {e}")
            return {
                "success": False,
                "error": "Policy Registration Failed",
                "message": str(e)
            }
    
    async def handle_get_policy_location_request(
        self,
        request_body: Dict[str, Any],
        user_context: Any
    ) -> Dict[str, Any]:
        """Handle get policy location request."""
        try:
            if not self.policy_tracker_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Policy Tracker Orchestrator not available"
                }
            
            # Extract policy_id from path parameter
            policy_id = request_body.get("policy_id")
            
            # Call orchestrator
            result = await self.policy_tracker_orchestrator.get_policy_location(
                policy_id=policy_id
            )
            
            self.logger.info(f"✅ Policy location retrieved: {policy_id}")
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Get policy location failed: {e}")
            return {
                "success": False,
                "error": "Location Retrieval Failed",
                "message": str(e)
            }
    
    async def handle_update_policy_location_request(
        self,
        request_body: Dict[str, Any],
        user_context: Any
    ) -> Dict[str, Any]:
        """Handle update policy location request."""
        try:
            if not self.policy_tracker_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Policy Tracker Orchestrator not available"
                }
            
            # Extract parameters
            policy_id = request_body.get("policy_id")
            new_location = request_body.get("new_location")
            metadata = request_body.get("metadata", {})
            
            # Call orchestrator
            result = await self.policy_tracker_orchestrator.update_policy_location(
                policy_id=policy_id,
                new_location=new_location,
                metadata=metadata,
                user_context=user_context
            )
            
            self.logger.info(f"✅ Policy location updated: {policy_id}")
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Update policy location failed: {e}")
            return {
                "success": False,
                "error": "Location Update Failed",
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
    # INSIGHTS PILLAR SEMANTIC API HANDLERS - REMOVED
    # ========================================================================
    # All insights-pillar handlers removed - Use insights-solution pillar instead
    # New endpoints:
    # - POST /api/v1/insights-solution/analyze
    # - POST /api/v1/insights-solution/mapping
    # - POST /api/v1/insights-solution/visualize
    
    # REMOVED: handle_analyze_content_for_insights_semantic_request
    # REMOVED: handle_analyze_content_for_insights_request
    # REMOVED: handle_query_insights_analysis_request
    # REMOVED: handle_get_available_content_metadata_request
    # REMOVED: handle_validate_content_metadata_for_insights_request
    # REMOVED: handle_get_insights_analysis_results_request
    # REMOVED: handle_get_insights_analysis_visualizations_request
    # REMOVED: handle_list_user_insights_analyses_request
    # REMOVED: handle_get_insights_pillar_summary_request
    # REMOVED: handle_insights_pillar_health_check_request
    
    # All insights-pillar handler methods removed - Use insights-solution pillar instead
    
    async def handle_get_content_pillar_summary_request(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle get Content pillar summary request.
        Semantic API: Get Content Pillar summary for Business Outcomes.
        
        Args:
            session_id: Optional session identifier
            user_id: Optional user identifier
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.content_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Content Orchestrator is not available"
                }
            
            result = await self.content_orchestrator.get_pillar_summary(
                session_id=session_id,
                user_id=user_id
            )
            
            self.logger.info(f"✅ Content pillar summary retrieved")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Get Content pillar summary failed: {e}")
            return {
                "success": False,
                "error": "Summary Failed",
                "message": str(e)
            }
    
    async def handle_get_operations_pillar_summary_request(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        client_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle get Operations pillar summary request.
        Semantic API: Get Operations Pillar summary for Business Outcomes.
        
        Args:
            session_id: Optional session identifier
            user_id: Optional user identifier
            client_id: Optional client identifier
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.operations_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Operations Orchestrator is not available"
                }
            
            result = await self.operations_orchestrator.get_pillar_summary(
                session_id=session_id,
                user_id=user_id,
                client_id=client_id
            )
            
            self.logger.info(f"✅ Operations pillar summary retrieved")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Get Operations pillar summary failed: {e}")
            return {
                "success": False,
                "error": "Summary Failed",
                "message": str(e)
            }
    
    # REMOVED: handle_insights_pillar_health_check_request - Use insights-solution pillar instead
    
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
        copybook_filename: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None  # ✅ NEW: User context with permissions from request
    ) -> Dict[str, Any]:
        """
        Handle file upload request (Content Pillar).
        
        ✅ UPDATED: Routes through Data Solution Orchestrator for proper platform correlation.
        Flow: Frontend → Data Solution Orchestrator → ContentJourneyOrchestrator (Journey realm) → Content Steward (Content realm)
        
        Args:
            file_data: File binary data
            filename: Original filename
            content_type: MIME type
            user_id: User identifier
            session_id: Optional session ID
            copybook_data: Optional copybook file data
            copybook_filename: Optional copybook filename
            user_context: Optional user context (will be enhanced with workflow_id)
        
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
            
            self.logger.info(f"📤 Content Pillar: Upload file request: {filename} ({len(file_data)} bytes) (routing through Data Solution Orchestrator)")
            
            # ✅ Get user context from request scope
            from utilities.security_authorization.request_context import get_request_user_context
            ctx = get_request_user_context()
            
            # Get Data Solution Orchestrator (Solution realm)
            self.logger.info(f"🔍 [handle_upload_file_request] Starting Data Solution Orchestrator discovery...")
            data_solution_orchestrator = await self._get_data_solution_orchestrator()
            
            if not data_solution_orchestrator:
                self.logger.error("❌ Data Solution Orchestrator not available")
                return {
                    "success": False,
                    "error": "Data Solution Orchestrator not available"
                }
            
            # Prepare user context with workflow_id
            import uuid
            enhanced_user_context = user_context.copy() if user_context else {}
            enhanced_user_context.update({
                "user_id": user_id,
                "workflow_id": str(uuid.uuid4())  # Generate workflow_id for end-to-end tracking
            })
            
            # Add session_id if provided
            if session_id:
                enhanced_user_context["session_id"] = session_id
            
            # Add request context data if available
            if ctx:
                enhanced_user_context.update({
                    "tenant_id": ctx.get("tenant_id"),
                    "permissions": ctx.get("permissions")
                })
                # Use session_id from context if not already set
                if not enhanced_user_context.get("session_id") and ctx.get("session_id"):
                    enhanced_user_context["session_id"] = ctx.get("session_id")
                self.logger.debug(f"✅ [handle_upload_file_request] Using request context: user_id={ctx.get('user_id')}, tenant_id={ctx.get('tenant_id')}, permissions={ctx.get('permissions')}")
            
            # Handle copybook upload FIRST if provided (so we can include copybook_file_id in main file metadata)
            copybook_file_id = None
            if copybook_data and copybook_filename:
                self.logger.info(f"📎 Uploading copybook first: {copybook_filename}")
                copybook_result = await data_solution_orchestrator.orchestrate_data_ingest(
                    file_data=copybook_data,
                    file_name=copybook_filename,
                    file_type="text/plain",
                    user_context=enhanced_user_context
                )
                
                if copybook_result.get("success"):
                    copybook_file_id = copybook_result.get("file_id")
                    self.logger.info(f"✅ Copybook uploaded successfully: {copybook_file_id}")
                    # Add copybook_file_id to user_context so it can be included in main file metadata
                    enhanced_user_context["copybook_file_id"] = copybook_file_id
                else:
                    self.logger.warning(f"⚠️ Copybook upload failed: {copybook_result.get('error')}")
            
            # Route through Data Solution Orchestrator
            # This will: orchestrate platform correlation → ContentJourneyOrchestrator (Journey realm) → Content Steward (Content realm)
            result = await data_solution_orchestrator.orchestrate_data_ingest(
                file_data=file_data,
                file_name=filename,
                file_type=content_type,
                user_context=enhanced_user_context
            )
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": result.get("error", "File upload failed"),
                    "workflow_id": enhanced_user_context.get("workflow_id")
                }
            
            # Add copybook_file_id to result if we uploaded one
            if copybook_file_id:
                result["copybook_file_id"] = copybook_file_id
            
            # Ensure workflow_id is in result
            if "workflow_id" not in result:
                result["workflow_id"] = enhanced_user_context.get("workflow_id")
            
            return result
            
        except Exception as e:
            # Log error without exc_info to avoid LogRecord conflict with TraceContextFormatter
            # The exception details are already in the message
            self.logger.error(f"❌ Upload file request failed: {e}", exc_info=False)
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
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
        
        ✅ UPDATED: Routes through Data Solution Orchestrator for proper platform correlation.
        Flow: Frontend → Data Solution Orchestrator → ContentJourneyOrchestrator (Journey realm) → FileParserService (Content realm)
        
        Args:
            file_id: File UUID
            user_id: User identifier
            copybook_file_id: Optional copybook file UUID
            processing_options: Optional processing options
        
        Returns:
            Processing result with parsed data and metadata
        """
        try:
            self.logger.info(f"⚙️ Content Pillar: Process file request: {file_id} (routing through Data Solution Orchestrator)")
            
            # ✅ Get user context from request scope
            from utilities.security_authorization.request_context import get_request_user_context
            ctx = get_request_user_context()
            
            # Get Data Solution Orchestrator (Solution realm)
            self.logger.info(f"🔍 [handle_process_file_request] Starting Data Solution Orchestrator discovery...")
            data_solution_orchestrator = await self._get_data_solution_orchestrator()
            
            if not data_solution_orchestrator:
                self.logger.error("❌ Data Solution Orchestrator not available")
                return {
                    "success": False,
                    "error": "Data Solution Orchestrator not available"
                }
            
            # Prepare user context with workflow_id
            import uuid
            user_context = {
                "user_id": user_id,
                "workflow_id": str(uuid.uuid4())  # Generate workflow_id for end-to-end tracking
            }
            
            # Add request context data if available
            if ctx:
                user_context.update({
                    "tenant_id": ctx.get("tenant_id"),
                    "session_id": ctx.get("session_id"),
                    "permissions": ctx.get("permissions")
                })
                self.logger.debug(f"✅ [handle_process_file_request] Using request context: user_id={ctx.get('user_id')}, tenant_id={ctx.get('tenant_id')}, permissions={ctx.get('permissions')}")
            
            # Prepare parse options
            parse_options = processing_options or {}
            if copybook_file_id:
                parse_options["copybook_file_id"] = copybook_file_id
            
            # Route through Data Solution Orchestrator
            # This will: orchestrate platform correlation → ContentJourneyOrchestrator (Journey realm) → FileParserService (Content realm)
            result = await data_solution_orchestrator.orchestrate_data_parse(
                file_id=file_id,
                parse_options=parse_options,
                user_context=user_context
            )
            
            if not result.get("success"):
                return {
                    "success": False,
                    "file_id": file_id,
                    "error": result.get("error", "File parsing failed"),
                    "parse_result": result
                }
            
            # Get file details (includes metadata)
            # Note: We still need ContentOrchestrator for get_file_details
            content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentOrchestrator")
            if not content_orchestrator:
                await self._discover_orchestrators()
                content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentOrchestrator")
            
            file_details = {}
            if content_orchestrator:
                try:
                    file_details = await content_orchestrator.get_file_details(file_id, user_id)
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not get file details: {e}")
            
            # Combine results
            return {
                "success": True,
                "file_id": file_id,
                "parse_result": result.get("parse_result", {}),
                "parsed_file_id": result.get("parsed_file_id"),
                "content_metadata": result.get("content_metadata", {}),
                "file_details": file_details.get("file", {}),
                "copybook_file_id": copybook_file_id,
                "workflow_id": result.get("workflow_id") or user_context.get("workflow_id"),
                "message": "Parsing completed successfully via Data Solution Orchestrator"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Process file request failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_data_solution_orchestrator(self):
        """Get Data Solution Orchestrator Service via Curator discovery."""
        try:
            self.logger.info(f"🔍 [_get_data_solution_orchestrator] Getting CuratorFoundationService...")
            # FrontendGatewayService extends RealmServiceBase, not OrchestratorBase, so use di_container directly
            curator = self.di_container.get_foundation_service("CuratorFoundationService")
            
            if curator:
                self.logger.info(f"🔍 [_get_data_solution_orchestrator] Discovering DataSolutionOrchestratorService...")
                data_solution_orchestrator = await curator.discover_service_by_name("DataSolutionOrchestratorService")
                
                if data_solution_orchestrator:
                    self.logger.info("✅ Discovered Data Solution Orchestrator via Curator")
                    return data_solution_orchestrator
            
            self.logger.warning("⚠️ Data Solution Orchestrator not found via Curator")
            return None
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover Data Solution Orchestrator: {e}")
            return None
    
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
            content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentOrchestrator")
            
            # If still not available, try to discover orchestrators lazily
            if not content_orchestrator:
                self.logger.warning("⚠️ ContentOrchestrator not found, attempting lazy discovery...")
                await self._discover_orchestrators()
                content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentOrchestrator")
            
            if not content_orchestrator:
                self.logger.error("❌ ContentOrchestrator not available")
                return {
                    "success": False,
                    "files": [],
                    "count": 0,
                    "error": "Content Orchestrator not available"
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
    
    async def handle_delete_file_request(
        self,
        file_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Handle delete file request (Content Pillar).
        
        Args:
            file_id: File UUID to delete
            user_id: User identifier
        
        Returns:
            Deletion result
        """
        try:
            self.logger.info(f"🗑️ Content Pillar: Delete file request for file: {file_id}, user: {user_id}")
            
            # Get Content Journey Orchestrator
            content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentOrchestrator")
            
            # If still not available, try to discover orchestrators lazily
            if not content_orchestrator:
                self.logger.warning("⚠️ ContentOrchestrator not found, attempting lazy discovery...")
                await self._discover_orchestrators()
                content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentOrchestrator")
            
            if not content_orchestrator:
                self.logger.error("❌ ContentOrchestrator not available")
                return {
                    "success": False,
                    "error": "Content Orchestrator not available"
                }
            
            # Call orchestrator's delete_file method
            result = await content_orchestrator.delete_file(file_id, user_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Delete file request failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_list_parsed_files_request(
        self,
        request_body: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle list parsed files request (Content Pillar).
        
        Lists parsed files for a user (optionally filtered by file_id).
        
        Args:
            request_body: Request body (may contain file_id)
            user_context: User context from request
        
        Returns:
            List of parsed files
        """
        try:
            # Get user_id from context
            user_id = user_context.get("user_id") if user_context else None
            if not user_id:
                return {
                    "success": False,
                    "error": "User ID required",
                    "parsed_files": [],
                    "count": 0
                }
            
            # Get file_id from request_body or query params
            file_id = None
            if request_body:
                file_id = request_body.get("file_id")
            
            self.logger.info(f"📋 Content Pillar: List parsed files request for user: {user_id}" + (f" (file_id: {file_id})" if file_id else ""))
            
            # Get Content Journey Orchestrator
            content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentJourneyOrchestrator") or self.orchestrators.get("ContentOrchestrator")
            if not content_orchestrator:
                await self._discover_orchestrators()
                content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentJourneyOrchestrator") or self.orchestrators.get("ContentOrchestrator")
            
            if not content_orchestrator:
                return {
                    "success": False,
                    "error": "Content Orchestrator not available",
                    "parsed_files": [],
                    "count": 0
                }
            
            # Call orchestrator method
            result = await content_orchestrator.list_parsed_files(user_id=user_id, file_id=file_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ List parsed files request failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "parsed_files": [],
                "count": 0
            }
    
    async def handle_preview_parsed_file_request(
        self,
        parsed_file_id: str,
        request_body: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle preview parsed file request (Content Pillar).
        
        Previews a parsed file by reading first N rows/columns from parquet.
        
        Args:
            parsed_file_id: ID of parsed file to preview
            request_body: Request body (may contain max_rows, max_columns)
            user_context: User context from request
        
        Returns:
            Preview data with columns, rows, and metadata
        """
        try:
            # Get max_rows and max_columns from request_body or query params
            # Convert to int to avoid slice errors (query params come as strings)
            max_rows = 20
            max_columns = 20
            
            # Check both request_body and query_params (query params may be in request_body or separate)
            query_params = request_body.get("query_params", {}) if request_body else {}
            combined_params = {**(request_body or {}), **query_params}
            
            max_rows_raw = combined_params.get("max_rows")
            max_columns_raw = combined_params.get("max_columns")
            
            try:
                max_rows = int(max_rows_raw) if max_rows_raw is not None else 20
            except (ValueError, TypeError):
                max_rows = 20
            try:
                max_columns = int(max_columns_raw) if max_columns_raw is not None else 20
            except (ValueError, TypeError):
                max_columns = 20
            
            self.logger.info(f"👁️ Content Pillar: Preview parsed file request: {parsed_file_id} (max_rows={max_rows}, max_columns={max_columns})")
            
            # Get Content Journey Orchestrator
            content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentJourneyOrchestrator") or self.orchestrators.get("ContentOrchestrator")
            if not content_orchestrator:
                await self._discover_orchestrators()
                content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentJourneyOrchestrator") or self.orchestrators.get("ContentOrchestrator")
            
            if not content_orchestrator:
                return {
                    "success": False,
                    "error": "Content Orchestrator not available",
                    "parsed_file_id": parsed_file_id
                }
            
            # Get user_id from context (optional for preview)
            user_id = user_context.get("user_id") if user_context else None
            
            # Call orchestrator method
            result = await content_orchestrator.preview_parsed_file(
                parsed_file_id=parsed_file_id,
                max_rows=max_rows,
                max_columns=max_columns,
                user_id=user_id
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Preview parsed file request failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "parsed_file_id": parsed_file_id
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
            content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentOrchestrator")
            
            # If still not available, try to discover orchestrators lazily
            if not content_orchestrator:
                self.logger.warning("⚠️ ContentOrchestrator not found, attempting lazy discovery...")
                await self._discover_orchestrators()
                content_orchestrator = self.content_orchestrator or self.orchestrators.get("ContentOrchestrator")
            
            if not content_orchestrator:
                self.logger.error("❌ ContentOrchestrator not available")
                return {
                    "success": False,
                    "file": None,
                    "error": "Content Orchestrator not available"
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
    
    async def handle_embed_content_request(
        self,
        file_id: str,
        parsed_file_id: str,
        content_metadata: Dict[str, Any],
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle embed content request (Frontend API → ContentOrchestrator).
        
        Args:
            file_id: File UUID
            parsed_file_id: Parsed file identifier
            content_metadata: Content metadata from parsing
            user_id: User identifier
            user_context: Optional user context
        
        Returns:
            Embedding creation result
        """
        try:
            if not self.content_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Content orchestrator not available"
                }
            
            # Call ContentOrchestrator.embed_content()
            result = await self.content_orchestrator.embed_content(
                file_id=file_id,
                parsed_file_id=parsed_file_id,
                content_metadata=content_metadata,
                user_id=user_id,
                user_context=user_context
            )
            
            self.logger.info(f"✅ Embedding creation complete: file_id={file_id}, content_id={result.get('content_id')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Embed content request failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": "Embedding Creation Failed",
                "message": str(e)
            }
    
    async def handle_get_embeddings_request(
        self,
        content_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Handle get embeddings request (Frontend API → SemanticDataAbstraction).
        
        Args:
            content_id: Content metadata ID
            user_id: User identifier
        
        Returns:
            Embeddings list
        """
        try:
            # ✅ Get user context from request-scoped context
            from utilities.security_authorization.request_context import get_request_user_context
            ctx = get_request_user_context()
            
            if ctx:
                self.logger.debug(f"✅ [handle_get_embeddings_request] Using request context: user_id={ctx.get('user_id')}, tenant_id={ctx.get('tenant_id')}")
            
            # Get SemanticDataAbstraction
            semantic_data = self.get_abstraction("semantic_data")
            if not semantic_data:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Semantic data abstraction not available"
                }
            
            # Get embeddings (pass request context)
            embeddings = await semantic_data.get_semantic_embeddings(
                content_id=content_id,
                user_context=ctx
            )
            
            self.logger.info(f"✅ Retrieved {len(embeddings)} embeddings for content_id={content_id}")
            
            return {
                "success": True,
                "embeddings": embeddings,
                "count": len(embeddings),
                "content_id": content_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ Get embeddings request failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": "Embedding Retrieval Failed",
                "message": str(e)
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
            content_orchestrator = self.orchestrators.get("ContentOrchestrator")
            if not content_orchestrator:
                return {
                    "status": "unhealthy",
                    "pillar": "content",
                    "error": "ContentOrchestrator not available",
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
    
    async def handle_request(
        self,
        method: str,
        path: str,
        params: Dict[str, Any],
        user_context: Dict[str, Any],
        headers: Dict[str, Any] = None,
        query_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Handle requests for the Session Pillar (when FrontendGatewayService acts as orchestrator).
        
        Routes session pillar requests to appropriate handlers.
        """
        self.logger.info(f"🔀 [FrontendGatewayService.handle_request] Session Pillar: {method} {path}")
        
        user_id = user_context.get("user_id") or params.get("user_id") or "anonymous"
        
        # Route based on path
        if method == "POST" and path == "create-user-session":
            return await self.handle_create_user_session_request(
                user_id=user_id,
                session_type=params.get("session_type", "mvp"),
                context=params.get("context")
            )
        elif method == "GET" and path.startswith("get-session-details/"):
            session_id = path.split("get-session-details/")[-1].split("/")[0]
            return await self.handle_get_session_details_request(
                session_id=session_id,
                user_id=user_id
            )
        elif method == "GET" and path.startswith("get-session-state/"):
            session_id = path.split("get-session-state/")[-1].split("/")[0]
            return await self.handle_get_session_state_request(
                session_id=session_id,
                user_id=user_id
            )
        elif method == "GET" and path == "health":
            return {
                "status": "healthy",
                "pillar": "session",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            self.logger.warning(f"⚠️ No handler found for session pillar: {method} {path}")
            return {
                "success": False,
                "error": f"Route not found for {method} {path}"
            }
    
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
            
            # Call orchestrator's semantic API method (agentic-forward pattern)
            business_context = {
                "pillar_outputs": pillar_outputs,
                "roadmap_options": roadmap_options or {},
                "business_name": roadmap_options.get("business_name") if roadmap_options else None,
                "objectives": roadmap_options.get("objectives", []) if roadmap_options else []
            }
            result = await self.business_outcomes_orchestrator.generate_strategic_roadmap(
                business_context=business_context,
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
            
            # Call orchestrator's semantic API method (agentic-forward pattern)
            business_context = {
                "pillar_outputs": pillar_outputs,
                "proposal_options": proposal_options or {},
                "business_name": proposal_options.get("business_name") if proposal_options else None,
                "objectives": proposal_options.get("objectives", []) if proposal_options else []
            }
            result = await self.business_outcomes_orchestrator.generate_poc_proposal(
                business_context=business_context,
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
                "insights": False,  # REMOVED: insights_orchestrator - Use insights-solution pillar
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
                "handle_document_analysis_request",  # REMOVED: "handle_insights_request" - Use insights-solution pillar
                "handle_operations_request", "handle_data_operations_request",
                "register_api_endpoint", "validate_api_request", "transform_for_frontend"
            ],
            "mcp_tools": [],
            "composes": "business_enablement_orchestrators",
            "supported_types": self.supported_types
        }
    
    # ========================================================================
    # ROUTING METRICS (Phase 5: Monitoring - New Routing Only)
    # ========================================================================
    
    async def get_routing_metrics(self) -> Dict[str, Any]:
        """
        Get routing performance metrics for monitoring.
        
        Returns metrics for discovered routing.
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
            "routing": {
                "requests": 0,
                "successes": 0,
                "errors": 0,
                "total_time_ms": 0.0,
                "avg_time_ms": 0.0
            },
            "last_reset": datetime.utcnow().isoformat()
        }
        return {"success": True, "message": "Routing metrics reset", "timestamp": self.routing_metrics["last_reset"]}


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
                "insights": False,  # REMOVED: insights_orchestrator - Use insights-solution pillar
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
                "handle_document_analysis_request",  # REMOVED: "handle_insights_request" - Use insights-solution pillar
                "handle_operations_request", "handle_data_operations_request",
                "register_api_endpoint", "validate_api_request", "transform_for_frontend"
            ],
            "mcp_tools": [],
            "composes": "business_enablement_orchestrators",
            "supported_types": self.supported_types
        }
    
    # ========================================================================
    # ROUTING METRICS (Phase 5: Monitoring - New Routing Only)
    # ========================================================================
    
    async def get_routing_metrics(self) -> Dict[str, Any]:
        """
        Get routing performance metrics for monitoring.
        
        Returns metrics for discovered routing.
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
            "routing": {
                "requests": 0,
                "successes": 0,
                "errors": 0,
                "total_time_ms": 0.0,
                "avg_time_ms": 0.0
            },
            "last_reset": datetime.utcnow().isoformat()
        }
        return {"success": True, "message": "Routing metrics reset", "timestamp": self.routing_metrics["last_reset"]}


