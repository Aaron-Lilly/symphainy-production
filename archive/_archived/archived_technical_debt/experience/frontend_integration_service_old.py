#!/usr/bin/env python3
"""
Frontend Integration Service - Experience Dimension Role

Manages frontend-backend communication and API integration following
Smart City architectural patterns.

WHAT (Experience Dimension Role): I manage frontend-backend integration and API communication
HOW (Smart City Role): I use micro-modules, MCP server, and agents for integration
"""

import os
import sys
import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from urllib.parse import urlencode

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../'))

from bases.foundation_service_base import FoundationServiceBase
from utilities import UserContext
from config.environment_loader import EnvironmentLoader
from config import Environment

# Import experience dimension protocols
from experience.protocols.experience_soa_service_protocol import ExperienceServiceBase
from experience.protocols.experience_mcp_server_protocol import ExperienceMCPServerBase
from experience.protocols.experience_agent_protocol import ExperienceAgentBase

# Import experience dimension interfaces
from experience.interfaces.frontend_integration_interface import (
    IFrontendIntegration, 
    APIEndpoint, 
    RequestMethod, 
    ResponseStatus, 
    DataFormat
)

# Import micro-modules
from experience.roles.frontend_integration.micro_modules.api_router import APIRouterModule
from experience.roles.frontend_integration.micro_modules.request_transformer import RequestTransformerModule
from experience.roles.frontend_integration.micro_modules.response_transformer import ResponseTransformerModule
from experience.roles.frontend_integration.micro_modules.error_handler import ErrorHandlerModule
from experience.roles.frontend_integration.micro_modules.authentication_manager import AuthenticationManagerModule
from experience.roles.frontend_integration.micro_modules.session_coordinator import SessionCoordinatorModule

# MCP server will be initialized separately to avoid circular imports


class FrontendIntegrationService(ExperienceServiceBase, IFrontendIntegration):
    """
    Frontend Integration Service - Experience Dimension Role
    
    Manages frontend-backend communication and API integration using micro-modules,
    MCP server, and specialist agents following Smart City architectural patterns.
    
    WHAT (Experience Dimension Role): I manage frontend-backend integration and API communication
    HOW (Smart City Role): I use micro-modules, MCP server, and agents for integration
    """
    
    def __init__(self, utility_foundation=None, curator_foundation=None, 
                 environment: Optional[Environment] = None):
        """Initialize Frontend Integration Service."""
        super().__init__("frontend_integration", "frontend_integration", utility_foundation, curator_foundation)
        
        self.utility_foundation = utility_foundation
        self.curator_foundation = curator_foundation
        self.env_loader = EnvironmentLoader(environment)
        
        # Environment-specific configuration
        self.config = self.env_loader.get_all_config()
        self.api_config = self.env_loader.get_api_config()
        self.feature_flags = self.env_loader.get_feature_flags()
        
        # Initialize micro-modules
        self.api_router = APIRouterModule(self.logger, self.env_loader)
        self.request_transformer = RequestTransformerModule(self.logger, self.env_loader)
        self.response_transformer = ResponseTransformerModule(self.logger, self.env_loader)
        self.error_handler = ErrorHandlerModule(self.logger, self.env_loader)
        self.authentication_manager = AuthenticationManagerModule(self.logger, self.env_loader)
        self.session_coordinator = SessionCoordinatorModule(self.logger, self.env_loader)
        
        # MCP server will be initialized separately
        
        # Service state
        self.service_name = "FrontendIntegrationService"
        self.service_version = "1.0.0"
        self.business_domain = "frontend_integration"
        self.capabilities = [
            "api_routing",
            "request_transformation",
            "response_transformation",
            "error_handling",
            "authentication_management",
            "session_coordination",
            "cross_pillar_communication"
        ]
        
        # API routing configuration - Updated with real patterns from business_orchestrator_old
        self.pillar_routes = {
            "insights": "http://localhost:8000",  # Insights pillar runs on port 8000
            "content": "http://localhost:8001",   # Content pillar runs on port 8001
            "operations": "http://localhost:8002", # Operations pillar runs on port 8002
            "business_outcomes": "http://localhost:8003", # Business outcomes runs on port 8003
            "smart_city": "http://localhost:8004", # Smart City runs on port 8004
            "cross_pillar": "http://localhost:8005", # Cross-pillar runs on port 8005
            "global": "http://localhost:8006"      # Global services run on port 8006
        }
        
        # Endpoint to pillar mapping for routing decisions
        self.endpoint_pillar_mapping = {
            # Insights pillar endpoints (from business_orchestrator_old)
            "/health": "insights",
            "/capabilities": "insights", 
            "/analyze": "insights",
            "/visualize": "insights",
            "/insights": "insights",
            "/chat": "insights",
            "/conversation": "insights",
            "/analyze/anomaly": "insights",
            "/analyze/correlation": "insights",
            "/analyze/statistical": "insights",
            "/visualize/histogram": "insights",
            "/visualize/scatter": "insights",
            "/visualize/heatmap": "insights",
            
            # Content pillar endpoints
            "/api/content": "content",
            
            # Operations pillar endpoints
            "/api/operations": "operations",
            
            # Business outcomes endpoints
            "/api/business-outcomes": "business_outcomes",
            
            # Cross-pillar endpoints
            "/api/smart-city": "smart_city",
            "/api/cross-pillar": "cross_pillar",
            
            # Global endpoints
            "/global": "global"
        }
        
        # Error handling configuration
        self.user_friendly_messages = {
            '400': 'Invalid request. Please check your input and try again.',
            '401': 'Authentication required. Please log in again.',
            '403': 'Access denied. You may not have permission for this operation.',
            '404': 'Resource not found. The requested resource may have been moved or deleted.',
            '422': 'Invalid data format. Please ensure your data is in the correct format.',
            '500': 'Server error. Please try again later or contact support.',
            '502': 'Service temporarily unavailable. Please try again later.',
            '503': 'Service temporarily unavailable. Please try again later.',
            '504': 'Request timeout. Please try again with a smaller request.',
        }
        
        self.logger.info(f"🔗 {self.service_name} initialized - Frontend Integration")
    
    async def _initialize_service_components(self):
        """Initialize service-specific components."""
        self.logger.info("🚀 Initializing Frontend Integration components...")
        
        # Initialize micro-modules
        await self.api_router.initialize()
        await self.request_transformer.initialize()
        await self.response_transformer.initialize()
        await self.error_handler.initialize()
        await self.authentication_manager.initialize()
        await self.session_coordinator.initialize()
        
        # MCP server initialization handled separately
        
        self.logger.info("✅ Frontend Integration components initialized")
    
    async def route_api_request(
        self, 
        endpoint: APIEndpoint, 
        method: RequestMethod, 
        user_context: UserContext, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Route an API request to the appropriate backend service."""
        self.logger.info(f"Routing API request: {method.value} {endpoint.value}")
        
        try:
            # Create authenticated headers
            auth_headers = await self.create_authenticated_headers(
                user_context, session_token, headers
            )
            
            # Transform request data if needed
            transformed_data = await self.request_transformer.transform_request(
                data, DataFormat.JSON, DataFormat.JSON
            )
            
            # Route to appropriate pillar service
            pillar = self._determine_pillar_from_endpoint(endpoint)
            route_result = await self.api_router.route_request(
                pillar, endpoint.value, method.value, transformed_data, params, auth_headers
            )
            
            # Transform response data
            response = await self.response_transformer.transform_response(
                route_result, DataFormat.JSON, DataFormat.JSON
            )
            
            return {
                "success": True,
                "data": response,
                "status": ResponseStatus.SUCCESS.value,
                "endpoint": endpoint.value,
                "method": method.value
            }
            
        except Exception as e:
            return await self.handle_api_error(
                e, endpoint, user_context, 
                status_code=getattr(e, 'status_code', 500)
            )
    
    async def transform_request_data(
        self, 
        data: Dict[str, Any], 
        source_format: DataFormat, 
        target_format: DataFormat
    ) -> Dict[str, Any]:
        """Transform request data between different formats."""
        return await self.request_transformer.transform_request(data, source_format, target_format)
    
    async def transform_response_data(
        self, 
        data: Dict[str, Any], 
        source_format: DataFormat, 
        target_format: DataFormat
    ) -> Dict[str, Any]:
        """Transform response data between different formats."""
        return await self.response_transformer.transform_response(data, source_format, target_format)
    
    async def validate_request(
        self, 
        endpoint: APIEndpoint, 
        method: RequestMethod, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate an incoming API request."""
        self.logger.info(f"Validating request: {method.value} {endpoint.value}")
        
        try:
            # Basic validation
            if not endpoint or not method:
                return {
                    "valid": False,
                    "error": "Missing endpoint or method",
                    "status": ResponseStatus.VALIDATION_ERROR.value
                }
            
            # Validate endpoint format
            if not endpoint.value.startswith('/'):
                return {
                    "valid": False,
                    "error": "Invalid endpoint format",
                    "status": ResponseStatus.VALIDATION_ERROR.value
                }
            
            # Validate method
            if method.value not in [m.value for m in RequestMethod]:
                return {
                    "valid": False,
                    "error": "Invalid HTTP method",
                    "status": ResponseStatus.VALIDATION_ERROR.value
                }
            
            # Additional validation based on endpoint
            validation_result = await self._validate_endpoint_specific(endpoint, method, data, params)
            
            return {
                "valid": validation_result.get("valid", True),
                "error": validation_result.get("error"),
                "status": ResponseStatus.SUCCESS.value if validation_result.get("valid", True) else ResponseStatus.VALIDATION_ERROR.value
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}",
                "status": ResponseStatus.VALIDATION_ERROR.value
            }
    
    async def handle_error(
        self, 
        error: Exception, 
        endpoint: APIEndpoint, 
        user_context: UserContext
    ) -> Dict[str, Any]:
        """Handle and format API errors."""
        return await self.error_handler.handle_error(error, endpoint, user_context)
    
    async def get_api_documentation(
        self, 
        endpoint: Optional[APIEndpoint] = None
    ) -> Dict[str, Any]:
        """Get API documentation for endpoints."""
        self.logger.info(f"Getting API documentation for: {endpoint.value if endpoint else 'all'}")
        
        if endpoint:
            return await self._get_endpoint_documentation(endpoint)
        else:
            return await self._get_all_endpoints_documentation()
    
    async def register_webhook(
        self, 
        endpoint: APIEndpoint, 
        webhook_url: str, 
        events: List[str]
    ) -> Dict[str, Any]:
        """Register a webhook for an endpoint."""
        self.logger.info(f"Registering webhook for {endpoint.value}: {webhook_url}")
        
        try:
            webhook_id = f"webhook_{endpoint.value.replace('/', '_')}_{int(datetime.utcnow().timestamp())}"
            
            # Store webhook configuration
            webhook_config = {
                "webhook_id": webhook_id,
                "endpoint": endpoint.value,
                "webhook_url": webhook_url,
                "events": events,
                "created_at": datetime.utcnow().isoformat(),
                "active": True
            }
            
            # In a real implementation, this would be stored in a database
            # For MVP, we'll store in memory
            if not hasattr(self, 'webhooks'):
                self.webhooks = {}
            self.webhooks[webhook_id] = webhook_config
            
            return {
                "success": True,
                "webhook_id": webhook_id,
                "message": "Webhook registered successfully",
                "status": ResponseStatus.SUCCESS.value
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to register webhook: {str(e)}",
                "status": ResponseStatus.ERROR.value
            }
    
    async def unregister_webhook(
        self, 
        webhook_id: str
    ) -> Dict[str, Any]:
        """Unregister a webhook."""
        self.logger.info(f"Unregistering webhook: {webhook_id}")
        
        try:
            if not hasattr(self, 'webhooks'):
                return {
                    "success": False,
                    "error": "No webhooks registered",
                    "status": ResponseStatus.NOT_FOUND.value
                }
            
            if webhook_id not in self.webhooks:
                return {
                    "success": False,
                    "error": "Webhook not found",
                    "status": ResponseStatus.NOT_FOUND.value
                }
            
            # Remove webhook
            del self.webhooks[webhook_id]
            
            return {
                "success": True,
                "message": "Webhook unregistered successfully",
                "status": ResponseStatus.SUCCESS.value
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to unregister webhook: {str(e)}",
                "status": ResponseStatus.ERROR.value
            }
    
    async def create_authenticated_headers(
        self, 
        user_context: UserContext, 
        session_token: Optional[str] = None,
        additional_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Create standardized authenticated headers for API requests."""
        return await self.authentication_manager.create_headers(
            user_context, session_token, additional_headers
        )
    
    async def handle_api_error(
        self, 
        error: Exception, 
        endpoint: APIEndpoint, 
        user_context: UserContext,
        response_text: Optional[str] = None,
        status_code: Optional[int] = None
    ) -> Dict[str, Any]:
        """Handle and format API errors with user-friendly messages."""
        return await self.error_handler.handle_api_error(
            error, endpoint, user_context, response_text, status_code
        )
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get the health status of the frontend integration service."""
        return {
            "service_name": self.service_name,
            "status": "healthy",
            "version": self.service_version,
            "capabilities": self.capabilities,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "api_router": "healthy",
                "request_transformer": "healthy", 
                "response_transformer": "healthy",
                "error_handler": "healthy",
                "authentication_manager": "healthy",
                "session_coordinator": "healthy"
            }
        }
    
    def _determine_pillar_from_endpoint(self, endpoint: APIEndpoint) -> str:
        """Determine which pillar an endpoint belongs to using the extracted patterns."""
        endpoint_str = endpoint.value
        
        # First, try exact matches from the mapping
        for pattern, pillar in self.endpoint_pillar_mapping.items():
            if endpoint_str.startswith(pattern):
                return pillar
        
        # Fallback to prefix matching for API endpoints
        if endpoint_str.startswith("/api/"):
            # Extract the pillar from the API path
            parts = endpoint_str.split("/")
            if len(parts) >= 3:
                api_pillar = parts[2]  # e.g., "/api/content/upload" -> "content"
                if api_pillar in self.pillar_routes:
                    return api_pillar
        
        # Default to global for unmatched endpoints
        return "global"
    
    async def _validate_endpoint_specific(
        self, 
        endpoint: APIEndpoint, 
        method: RequestMethod, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate endpoint-specific requirements."""
        # This would contain specific validation logic for each endpoint
        # For MVP, we'll do basic validation
        return {"valid": True}
    
    async def _get_endpoint_documentation(self, endpoint: APIEndpoint) -> Dict[str, Any]:
        """Get documentation for a specific endpoint."""
        return {
            "endpoint": endpoint.value,
            "description": f"API endpoint for {endpoint.value}",
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "parameters": {},
            "examples": {}
        }
    
    async def _get_all_endpoints_documentation(self) -> Dict[str, Any]:
        """Get documentation for all endpoints."""
        endpoints = {}
        for endpoint in APIEndpoint:
            endpoints[endpoint.value] = await self._get_endpoint_documentation(endpoint)
        
        return {
            "api_version": "1.0.0",
            "endpoints": endpoints,
            "total_endpoints": len(APIEndpoint)
        }


# Create service instance
frontend_integration_service = FrontendIntegrationService()
