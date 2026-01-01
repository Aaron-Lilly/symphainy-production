#!/usr/bin/env python3
"""
Content Pillar API Routing Integration Example

This example shows how to integrate the Content Pillar Service with the new API routing utility.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..api_routing_utility import APIRoutingUtility, HTTPMethod, RequestContext, ResponseContext
from ..middleware import (
    AuthenticationMiddleware,
    LoggingMiddleware,
    ValidationMiddleware,
    ErrorHandlingMiddleware
)
from utilities import UserContext


class ContentPillarAPIIntegration:
    """Example integration of Content Pillar with API routing utility."""
    
    def __init__(self, di_container, content_pillar_service):
        """Initialize Content Pillar API integration."""
        self.di_container = di_container
        self.content_pillar_service = content_pillar_service
        self.logger = logging.getLogger("ContentPillarAPIIntegration")
        
        # Get API router
        self.api_router = di_container.get_api_router()
        
        # Initialize middleware
        self._setup_middleware()
        
        # Register routes
        self._register_routes()
    
    def _setup_middleware(self):
        """Setup middleware for Content Pillar API routes."""
        # Register global middleware
        self.api_router.register_middleware(
            LoggingMiddleware(self.di_container),
            scope="global"
        )
        
        self.api_router.register_middleware(
            ErrorHandlingMiddleware(self.di_container),
            scope="global"
        )
        
        # Register realm-specific middleware
        self.api_router.register_middleware(
            AuthenticationMiddleware(self.di_container),
            scope="realm",
            target="business_enablement"
        )
        
        self.api_router.register_middleware(
            ValidationMiddleware(self.di_container),
            scope="realm",
            target="business_enablement"
        )
        
        # Register pillar-specific middleware
        self.api_router.register_middleware(
            ValidationMiddleware(self.di_container),
            scope="pillar",
            target="content_pillar"
        )
    
    def _register_routes(self):
        """Register Content Pillar API routes."""
        # File upload route
        self.api_router.register_route(
            method=HTTPMethod.POST,
            path="/api/content/upload",
            handler=self._handle_file_upload,
            pillar="content_pillar",
            realm="business_enablement",
            description="Upload a file for content processing",
            version="1.0",
            tags=["file", "upload", "content"]
        )
        
        # File parsing route
        self.api_router.register_route(
            method=HTTPMethod.POST,
            path="/api/content/{file_id}/parse",
            handler=self._handle_file_parsing,
            pillar="content_pillar",
            realm="business_enablement",
            description="Parse a file to extract content",
            version="1.0",
            tags=["file", "parse", "content"]
        )
        
        # Metadata extraction route
        self.api_router.register_route(
            method=HTTPMethod.GET,
            path="/api/content/{file_id}/metadata",
            handler=self._handle_metadata_extraction,
            pillar="content_pillar",
            realm="business_enablement",
            description="Extract metadata from a file",
            version="1.0",
            tags=["file", "metadata", "content"]
        )
        
        # File listing route
        self.api_router.register_route(
            method=HTTPMethod.GET,
            path="/api/content/files",
            handler=self._handle_file_listing,
            pillar="content_pillar",
            realm="business_enablement",
            description="List available files",
            version="1.0",
            tags=["file", "list", "content"]
        )
        
        # Health check route
        self.api_router.register_route(
            method=HTTPMethod.GET,
            path="/api/content/health",
            handler=self._handle_health_check,
            pillar="content_pillar",
            realm="business_enablement",
            description="Content Pillar health check",
            version="1.0",
            tags=["health", "status"]
        )
    
    # ROUTE HANDLERS
    
    async def _handle_file_upload(self, request_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Handle file upload request."""
        try:
            # Extract file data from request
            file_data = request_data.get("file_data")
            file_name = request_data.get("file_name")
            file_type = request_data.get("file_type", "auto")
            
            if not file_data or not file_name:
                return {
                    "success": False,
                    "error": "file_data and file_name are required"
                }
            
            # Call Content Pillar Service
            result = await self.content_pillar_service.upload_file(
                file_data=file_data,
                file_name=file_name,
                file_type=file_type,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ File upload failed: {e}")
            raise
    
    async def _handle_file_parsing(self, request_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Handle file parsing request."""
        try:
            # Extract file ID from path parameters (would be set by router)
            file_id = request_data.get("file_id")
            if not file_id:
                return {
                    "success": False,
                    "error": "file_id is required"
                }
            
            # Call Content Pillar Service
            result = await self.content_pillar_service.parse_file(
                file_id=file_id,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ File parsing failed: {e}")
            raise
    
    async def _handle_metadata_extraction(self, request_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Handle metadata extraction request."""
        try:
            # Extract file ID from path parameters
            file_id = request_data.get("file_id")
            if not file_id:
                return {
                    "success": False,
                    "error": "file_id is required"
                }
            
            # Call Content Pillar Service
            result = await self.content_pillar_service.extract_comprehensive_metadata(
                file_id=file_id,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Metadata extraction failed: {e}")
            raise
    
    async def _handle_file_listing(self, request_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Handle file listing request."""
        try:
            # Call Content Pillar Service
            result = await self.content_pillar_service.list_files(
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ File listing failed: {e}")
            raise
    
    async def _handle_health_check(self, request_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Handle health check request."""
        try:
            # Call Content Pillar Service health check
            result = await self.content_pillar_service.health_check()
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            raise
    
    # PUBLIC API METHODS
    
    async def route_request(
        self,
        method: str,
        path: str,
        request_data: Dict[str, Any],
        user_context: UserContext,
        headers: Dict[str, str] = None,
        query_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Route a request through the API router."""
        try:
            # Convert method string to HTTPMethod enum
            http_method = HTTPMethod(method.upper())
            
            # Route the request
            response_context = await self.api_router.route_request(
                method=http_method,
                path=path,
                request_data=request_data,
                user_context=user_context,
                headers=headers,
                query_params=query_params
            )
            
            return response_context.body
            
        except Exception as e:
            self.logger.error(f"❌ Request routing failed: {e}")
            return {
                "success": False,
                "error": {
                    "code": "ROUTING_ERROR",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
    
    async def get_routing_stats(self) -> Dict[str, Any]:
        """Get API routing statistics."""
        return await self.api_router.get_routing_stats()
    
    async def list_registered_routes(self) -> Dict[str, Any]:
        """List all registered routes."""
        routes = await self.api_router.list_routes(pillar="content_pillar")
        return {
            "routes": [
                {
                    "method": route.method.value,
                    "path": route.path,
                    "description": route.description,
                    "version": route.version,
                    "tags": route.tags,
                    "status": route.status.value
                }
                for route in routes
            ],
            "total_routes": len(routes)
        }


