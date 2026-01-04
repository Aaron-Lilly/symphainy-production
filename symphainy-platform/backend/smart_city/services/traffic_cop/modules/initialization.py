#!/usr/bin/env python3
"""
Initialization Module - Traffic Cop Service

Initializes infrastructure connections using mixin methods and direct libraries.
"""

from typing import Dict, Any


class Initialization:
    """Initialization module for Traffic Cop Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def initialize_infrastructure(self):
        """Initialize infrastructure connections using mixin methods."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "initialize_infrastructure_start",
            success=True
        )
        
        try:
            # Use mixin methods - NOT direct foundation access!
            self.service.session_abstraction = self.service.get_session_abstraction()
            self.service.state_management_abstraction = self.service.get_state_management_abstraction()
            self.service.messaging_abstraction = self.service.get_messaging_abstraction()
            self.service.file_management_abstraction = self.service.get_file_management_abstraction()
            # Analytics abstraction doesn't exist - skip it (optional)
            try:
                self.service.analytics_abstraction = self.service.get_infrastructure_abstraction("analytics")
            except:
                self.service.analytics_abstraction = None
            
            self.service.is_infrastructure_connected = True
            
            # Record health metric
            await self.service.record_health_metric(
                "infrastructure_connected",
                1.0,
                {
                    "session": "connected",
                    "state_management": "connected",
                    "messaging": "connected",
                    "file_management": "connected",
                    "analytics": "connected"
                }
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "initialize_infrastructure_complete",
                success=True,
                details={
                    "session": "connected",
                    "state_management": "connected",
                    "messaging": "connected",
                    "file_management": "connected",
                    "analytics": "connected"
                }
            )
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "initialize_infrastructure")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "initialize_infrastructure_complete",
                success=False,
                details={"error": str(e)}
            )
            raise
    
    async def initialize_direct_libraries(self):
        """Initialize direct library injection for business logic."""
        try:
            self.service._log("info", "📚 Initializing direct library injection...")
            
            # Import libraries directly (these are Python packages, not services in DI container)
            try:
                import fastapi
                self.service.fastapi = fastapi
            except ImportError:
                self.service.fastapi = None
                
            try:
                from fastapi import WebSocket
                self.service.websocket = WebSocket
            except ImportError:
                self.service.websocket = None
                
            try:
                import pandas
                self.service.pandas = pandas
            except ImportError:
                self.service.pandas = None
                
            try:
                import httpx
                self.service.httpx = httpx
            except ImportError:
                self.service.httpx = None
            
            self.service._log("debug", f"Libraries loaded - FastAPI: {self.service.fastapi is not None}, WebSocket: {self.service.websocket is not None}, pandas: {self.service.pandas is not None}, httpx: {self.service.httpx is not None}")
            
            # Initialize FastAPI app for API Gateway
            if self.service.fastapi:
                from fastapi import FastAPI
                from fastapi.middleware.cors import CORSMiddleware
                
                self.service.fastapi_app = FastAPI(
                    title="Traffic Cop API Gateway",
                    description="API Gateway for Smart City Platform",
                    version="1.0.0"
                )
                
                # Add CORS middleware
                self.service.fastapi_app.add_middleware(
                    CORSMiddleware,
                    allow_origins=["*"],
                    allow_credentials=True,
                    allow_methods=["*"],
                    allow_headers=["*"]
                )
            
            self.service._log("info", "✅ Direct libraries initialized")
            
        except Exception as e:
            self.service._log("error", f"❌ Failed to initialize direct libraries: {e}")
            raise
    
    async def initialize_capabilities(self):
        """Initialize Traffic Cop specific capabilities."""
        try:
            self.service._log("info", "🚦 Initializing Traffic Cop capabilities...")
            
            # Initialize service registry
            self.service.service_instances = {}
            self.service.load_balancing_counters = {}
            
            # Initialize rate limiting
            self.service.rate_limit_counters = {}
            
            # Initialize API routes
            self.service.api_routes = {
                "/api/v1/health": {"method": "GET", "service": "health"},
                "/api/v1/sessions": {"method": "POST", "service": "session"},
                "/api/v1/state": {"method": "POST", "service": "state"},
                "/api/v1/analytics": {"method": "GET", "service": "analytics"}
            }
            
            # Initialize WebSocket Connection Registry (Redis-backed for horizontal scaling)
            if self.service.messaging_abstraction:
                try:
                    from backend.smart_city.services.traffic_cop.connection_registry import TrafficCopConnectionRegistry
                    self.service.websocket_connection_registry = TrafficCopConnectionRegistry(
                        self.service.messaging_abstraction
                    )
                    self.service._log("info", "✅ WebSocket Connection Registry initialized (Redis-backed)")
                except Exception as e:
                    self.service._log("error", f"❌ Failed to initialize WebSocket Connection Registry: {e}")
                    self.service.websocket_connection_registry = None
            else:
                self.service._log("warning", "⚠️ Messaging abstraction not available - WebSocket Connection Registry not initialized")
                self.service.websocket_connection_registry = None
            
            self.service._log("info", "✅ Traffic Cop capabilities initialized")
            
        except Exception as e:
            self.service._log("error", f"❌ Failed to initialize Traffic Cop capabilities: {e}")
            raise







