#!/usr/bin/env python3
"""
FastAPI Router Manager - Platform Infrastructure Utility

WHAT (Infrastructure Utility): I provide unified FastAPI router management
HOW (Infrastructure Implementation): I consolidate all realm routers into a single router

Similar to DI Container - simple, direct, no abstractions needed.
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, FastAPI
from datetime import datetime

logger = logging.getLogger(__name__)


class FastAPIRouterManager:
    """
    FastAPI Router Manager - Platform Infrastructure Utility
    
    Centralized FastAPI router management that consolidates all realm-specific
    routers into a unified communication infrastructure.
    
    Similar to DI Container - simple, direct access, no abstractions.
    
    WHAT (Infrastructure Utility): I provide unified FastAPI router management
    HOW (Infrastructure Implementation): I consolidate all realm routers into a single router
    """
    
    def __init__(self):
        """Initialize FastAPI Router Manager."""
        self.logger = logging.getLogger("FastAPIRouterManager")
        
        # Router registry
        self.realm_routers: Dict[str, APIRouter] = {}
        self.global_router = APIRouter()
        
        # Router metadata
        self.router_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Service state
        self.is_initialized = False
        
        self.logger.info("🏗️ FastAPI Router Manager initialized")
    
    async def initialize(self):
        """Initialize the router manager."""
        self.logger.info("🚀 Initializing FastAPI Router Manager...")
        
        try:
            # Initialize global router
            await self._setup_global_router()
            
            # Register health check endpoint
            await self._register_health_endpoints()
            
            self.is_initialized = True
            self.logger.info("✅ FastAPI Router Manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize FastAPI Router Manager: {e}")
            raise
    
    async def register_realm_router(self, realm: str, router: APIRouter, metadata: Dict[str, Any] = None):
        """Register a realm-specific router."""
        self.logger.info(f"📝 Registering {realm} realm router...")
        
        try:
            # Store router
            self.realm_routers[realm] = router
            
            # Store metadata
            self.router_metadata[realm] = metadata or {}
            self.router_metadata[realm]["registered_at"] = datetime.utcnow().isoformat()
            
            # Include router in global router
            self.global_router.include_router(router)
            
            self.logger.info(f"✅ {realm} realm router registered successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register {realm} realm router: {e}")
            raise
    
    def get_unified_router(self) -> APIRouter:
        """Get the unified router for all realms."""
        if not self.is_initialized:
            raise RuntimeError("FastAPI Router Manager not initialized")
        
        return self.global_router
    
    def get_realm_router(self, realm: str) -> Optional[APIRouter]:
        """Get a specific realm router."""
        return self.realm_routers.get(realm)
    
    def list_registered_realms(self) -> List[str]:
        """List all registered realms."""
        return list(self.realm_routers.keys())
    
    async def get_router_stats(self) -> Dict[str, Any]:
        """Get router statistics and metadata."""
        return {
            "total_realms": len(self.realm_routers),
            "registered_realms": list(self.realm_routers.keys()),
            "router_metadata": self.router_metadata,
            "is_initialized": self.is_initialized,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the router manager."""
        return {
            "status": "healthy" if self.is_initialized else "not_initialized",
            "total_realms": len(self.realm_routers),
            "registered_realms": list(self.realm_routers.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # PRIVATE METHODS
    
    async def _setup_global_router(self):
        """Set up the global router with common endpoints."""
        self.logger.info("🔧 Setting up global router...")
        
        # Add common middleware, CORS, etc.
        # This would be where we add global middleware
        
        self.logger.info("✅ Global router setup completed")
    
    async def _register_health_endpoints(self):
        """Register health check endpoints."""
        self.logger.info("🔧 Registering health check endpoints...")
        
        @self.global_router.get("/health")
        async def health_check():
            """Global health check endpoint."""
            return await self.health_check()
        
        @self.global_router.get("/health/realms")
        async def realms_health_check():
            """Realms health check endpoint."""
            return await self.get_router_stats()
        
        self.logger.info("✅ Health check endpoints registered")
    
    async def shutdown(self):
        """Shutdown the router manager."""
        self.logger.info("🛑 Shutting down FastAPI Router Manager...")
        
        # Clear router registry
        self.realm_routers.clear()
        self.router_metadata.clear()
        
        # Reset state
        self.is_initialized = False
        
        self.logger.info("✅ FastAPI Router Manager shutdown completed")









