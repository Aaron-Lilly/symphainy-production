#!/usr/bin/env python3
"""
API Gateway Adapter - Centralized API Gateway Infrastructure

Centralized API Gateway adapter that routes all API traffic (external and internal)
and provides SOA API routing capabilities.

WHAT (Infrastructure Adapter): I provide centralized API Gateway infrastructure
HOW (Infrastructure Implementation): I route API requests and provide SOA API capabilities
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Import Public Works Foundation for infrastructure abstractions
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService

# Import DI Container for dependency injection
from foundations.di_container.di_container_service import DIContainerService

# Import utilities
from utilities.api_routing.api_routing_utility import APIRoutingUtility

logger = logging.getLogger(__name__)


class APIGatewayAdapter:
    """
    API Gateway Adapter - Centralized API Gateway Infrastructure
    
    Provides centralized API Gateway infrastructure that routes all API traffic
    (external and internal) and provides SOA API routing capabilities.
    
    WHAT (Infrastructure Adapter): I provide centralized API Gateway infrastructure
    HOW (Infrastructure Implementation): I route API requests and provide SOA API capabilities
    """
    
    def __init__(self, di_container: DIContainerService, 
                 public_works_foundation: PublicWorksFoundationService,
                 fastapi_router_manager=None):
        """Initialize API Gateway Adapter."""
        self.logger = logging.getLogger("APIGatewayAdapter")
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        self.fastapi_router_manager = fastapi_router_manager
        
        # FastAPI application
        self.app = None
        
        # API routing utility
        self.api_routing_utility = None
        
        # Service routing configuration (migrated from Experience realm)
        self.service_routes = {
            "insights": "http://localhost:8000",     # Insights pillar (from business_orchestrator_old)
            "content": "http://localhost:8001",      # Content pillar
            "operations": "http://localhost:8002",   # Operations pillar
            "business_outcomes": "http://localhost:8003", # Business outcomes pillar
            "smart_city": "http://localhost:8004",   # Smart City services
            "cross_pillar": "http://localhost:8005", # Cross-pillar coordination
            "global": "http://localhost:8006"        # Global services
        }
        
        # SOA API routing configuration
        self.soa_api_routes = {
            "smart_city": {
                "base_url": "http://localhost:8004",
                "endpoints": {
                    "security_guard": "/api/v1/security",
                    "traffic_cop": "/api/v1/orchestration",
                    "nurse": "/api/v1/health",
                    "conductor": "/api/v1/workflow",
                    "librarian": "/api/v1/knowledge",
                    "data_steward": "/api/v1/data",
                    "post_office": "/api/v1/messaging",
                    "city_manager": "/api/v1/management"
                }
            },
            "business_enablement": {
                "base_url": "http://localhost:8001",
                "endpoints": {
                    "content_pillar": "/api/v1/content",
                    "insights_pillar": "/api/v1/insights",
                    "operations_pillar": "/api/v1/operations",
                    "business_outcomes_pillar": "/api/v1/outcomes"
                }
            },
            "experience": {
                "base_url": "http://localhost:8007",
                "endpoints": {
                    "frontend_integration": "/api/v1/frontend",
                    "session_manager": "/api/v1/session",
                    "ui_state_manager": "/api/v1/state",
                    "real_time_coordinator": "/api/v1/realtime"
                }
            },
            "journey_solution": {
                "base_url": "http://localhost:8008",
                "endpoints": {
                    "journey_orchestrator": "/api/v1/journey",
                    "business_outcome_landing": "/api/v1/outcome",
                    "journey_persistence": "/api/v1/persistence"
                }
            },
            "solution": {
                "base_url": "http://localhost:8009",
                "endpoints": {
                    "solution_orchestration": "/api/v1/solution/orchestrate",
                    "solution_capabilities": "/api/v1/solution/orchestrate/capabilities",
                    "solution_initiators": "/api/v1/solution/orchestrate/initiators",
                    "solution_dashboard": "/api/v1/solution/dashboard",
                    "solution_health": "/api/v1/solution/platform/health"
                }
            }
        }
        
        # Service state
        self.is_initialized = False
        self.is_running = False
        
        self.logger.info("🏗️ API Gateway Adapter initialized")
    
    async def initialize(self):
        """Initialize API Gateway Adapter."""
        self.logger.info("🚀 Initializing API Gateway Adapter...")
        
        try:
            # Create FastAPI application
            self.app = FastAPI(
                title="SymphAIny Platform API Gateway",
                description="Centralized API Gateway for SymphAIny Platform",
                version="1.0.0",
                docs_url="/docs",
                redoc_url="/redoc"
            )
            
            # Add CORS middleware
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],  # Configure based on environment
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            
            # Add trusted host middleware
            self.app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=["*"]  # Configure based on environment
            )
            
            # Initialize API routing utility
            self.api_routing_utility = APIRoutingUtility(
                di_container=self.di_container
            )
            await self.api_routing_utility.initialize()
            
            # Setup API routes
            await self._setup_api_routes()
            
            # Setup SOA API routes
            await self._setup_soa_api_routes()
            
            self.is_initialized = True
            self.logger.info("✅ API Gateway Adapter initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize API Gateway Adapter: {e}")
            raise
    
    async def _setup_api_routes(self):
        """Setup API routes for external and internal traffic."""
        self.logger.info("🔧 Setting up API routes...")
        
        # Add health check endpoint
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        # Add service discovery endpoint
        @self.app.get("/services")
        async def get_services():
            return {
                "service_routes": self.service_routes,
                "soa_api_routes": self.soa_api_routes
            }
        
        # Add unified router from router manager if available
        if self.fastapi_router_manager:
            # Include unified router from router manager
            unified_router = self.fastapi_router_manager.get_unified_router()
            if unified_router:
                self.app.include_router(unified_router)
                self.logger.info("✅ Unified router included from router manager")
            else:
                self.logger.warning("⚠️ No unified router available from router manager")
        elif self.api_routing_utility:
            # Fallback to API routing utility
            router = self.api_routing_utility.get_router()
            if router:
                self.app.include_router(router, prefix="/api/v1")
                self.logger.info("✅ API routing utility router included")
            else:
                self.logger.warning("⚠️ No router available from API routing utility")
        
        self.logger.info("✅ API routes setup complete")
    
    async def _setup_soa_api_routes(self):
        """Setup SOA API routes for inter-realm communication."""
        self.logger.info("🔧 Setting up SOA API routes...")
        
        # Add SOA API discovery endpoint
        @self.app.get("/soa/apis")
        async def get_soa_apis():
            return self.soa_api_routes
        
        # Add SOA API routing endpoint
        @self.app.get("/soa/route/{realm}/{service}")
        async def route_soa_api(realm: str, service: str):
            if realm in self.soa_api_routes:
                realm_config = self.soa_api_routes[realm]
                if service in realm_config["endpoints"]:
                    return {
                        "realm": realm,
                        "service": service,
                        "endpoint": realm_config["endpoints"][service],
                        "base_url": realm_config["base_url"]
                    }
            return {"error": "Service not found"}
        
        self.logger.info("✅ SOA API routes setup complete")
    
    async def start(self):
        """Start API Gateway Adapter."""
        if not self.is_initialized:
            await self.initialize()
        
        self.logger.info("🚀 Starting API Gateway Adapter...")
        
        try:
            # Start API routing utility
            if self.api_routing_utility:
                await self.api_routing_utility.start()
            
            self.is_running = True
            self.logger.info("✅ API Gateway Adapter started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start API Gateway Adapter: {e}")
            raise
    
    async def stop(self):
        """Stop API Gateway Adapter."""
        self.logger.info("🛑 Stopping API Gateway Adapter...")
        
        try:
            # Stop API routing utility
            if self.api_routing_utility:
                await self.api_routing_utility.stop()
            
            self.is_running = False
            self.logger.info("✅ API Gateway Adapter stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop API Gateway Adapter: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown API Gateway Adapter."""
        await self.stop()
        self.logger.info("🔌 API Gateway Adapter shutdown complete")
    
    # Public API methods
    
    def get_app(self) -> FastAPI:
        """Get FastAPI application."""
        return self.app
    
    async def route_request(self, request: Request) -> Response:
        """Route API request to appropriate service."""
        # This would be implemented with actual routing logic
        # For now, return a placeholder response
        return Response(
            content="API Gateway routing not yet implemented",
            status_code=200
        )
    
    async def route_request_to_pillar(self, pillar: str, endpoint: str, method: str, 
                                     data: Optional[Dict[str, Any]] = None,
                                     params: Optional[Dict[str, Any]] = None,
                                     headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Route a request to the appropriate backend service (migrated from Experience realm).
        
        Args:
            pillar: The pillar/service to route to
            endpoint: The API endpoint
            method: The HTTP method
            data: Request body data
            params: Query parameters
            headers: Request headers
            
        Returns:
            Response from the backend service
        """
        self.logger.info(f"Routing request to {pillar}: {method} {endpoint}")
        
        try:
            # Get service URL
            service_url = self.service_routes.get(pillar, self.service_routes["global"])
            full_url = f"{service_url}{endpoint}"
            
            # Make HTTP request (simplified implementation)
            # In a real implementation, this would use httpx or similar
            response = {
                "status": "success",
                "pillar": pillar,
                "endpoint": endpoint,
                "method": method,
                "url": full_url,
                "data": data,
                "params": params,
                "headers": headers,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Request routed successfully to {pillar}")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Failed to route request to {pillar}: {e}")
            return {
                "status": "error",
                "pillar": pillar,
                "endpoint": endpoint,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def register_soa_api(self, realm: str, service: str, endpoint: str, base_url: str):
        """Register SOA API endpoint."""
        if realm not in self.soa_api_routes:
            self.soa_api_routes[realm] = {
                "base_url": base_url,
                "endpoints": {}
            }
        
        self.soa_api_routes[realm]["endpoints"][service] = endpoint
        self.logger.info(f"✅ Registered SOA API: {realm}/{service} -> {endpoint}")
    
    async def discover_soa_api(self, realm: str, service: str) -> Optional[Dict[str, Any]]:
        """Discover SOA API endpoint."""
        if realm in self.soa_api_routes:
            realm_config = self.soa_api_routes[realm]
            if service in realm_config["endpoints"]:
                return {
                    "realm": realm,
                    "service": service,
                    "endpoint": realm_config["endpoints"][service],
                    "base_url": realm_config["base_url"]
                }
        return None
    
    async def get_service_routes(self) -> Dict[str, str]:
        """Get service routing configuration."""
        return self.service_routes
    
    async def get_soa_api_routes(self) -> Dict[str, Any]:
        """Get SOA API routing configuration."""
        return self.soa_api_routes
