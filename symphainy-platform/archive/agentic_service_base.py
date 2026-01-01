#!/usr/bin/env python3
"""
Agentic Service Base - Base Class for Agentic Services

Base class for all agentic services that support the Agent SDK.
Provides proper error handling, multi-tenancy, and agentic business abstractions.

WHAT (Agentic Role): I provide base functionality for agentic services
HOW (Agentic Service Base): I use proper DI patterns with agentic-specific utilities
"""

import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from bases.realm_service_base import RealmServiceBase


class AgenticServiceBase(RealmServiceBase):
    """
    Base class for all agentic services that support the Agent SDK.
    
    Provides:
    - Proper error handling using SmartCityErrorHandler
    - Native multi-tenancy support using TenantManagementUtility
    - Agentic business abstractions from Public Works
    - Agent-specific logging and telemetry
    - Health monitoring and status reporting
    """
    
    def __init__(self, service_name: str, di_container,
                 public_works_foundation: PublicWorksFoundationService = None,
                 security_provider=None, authorization_guard=None):
        """
        Initialize agentic service base with ServiceBase foundation.
        
        Args:
            service_name: Name of the agentic service
            di_container: DI Container Service
            public_works_foundation: Public Works Foundation Service for agentic business abstractions
            security_provider: Security provider for zero-trust
            authorization_guard: Authorization guard for zero-trust
        """
        # Initialize ServiceBase (ground zero) with security awareness
        super().__init__(
            service_name=service_name,
            di_container=di_container,
            security_provider=security_provider,
            authorization_guard=authorization_guard
        )
        
        self.public_works_foundation = public_works_foundation
        
        # Multi-tenant context
        self.tenant_context = None
        self.tenant_isolation_enabled = True
        self.tenant_id = None
        self.tenant_user_id = None
        
        # Agentic business abstractions from public works
        self.agentic_abstractions = {}
        
        # Service state
        self.is_initialized = False
        self.initialization_time = None
        
        self.logger.info(f"🤖 Agentic Service {service_name} initialized with proper DI and multi-tenancy support")
    
    async def initialize(self, tenant_context: Dict[str, Any] = None):
        """Initialize the agentic service with tenant context."""
        try:
            self.logger.info(f"🚀 Initializing agentic service {self.service_name}...")
            
            # Set tenant context
            if tenant_context:
                await self.set_tenant_context(tenant_context)
            
            # Load agentic business abstractions from public works
            if self.public_works_foundation:
                await self._load_agentic_abstractions()
            
            # Perform service-specific initialization
            await self._initialize_service()
            
            self.is_initialized = True
            self.initialization_time = datetime.utcnow()
            
            self.logger.info(f"✅ Agentic service {self.service_name} initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize agentic service {self.service_name}: {e}")
            self.error_handler.handle_error(e, f"{self.service_name}_initialization_failed")
            raise
    
    async def set_tenant_context(self, tenant_context: Dict[str, Any]) -> bool:
        """Set tenant context for multi-tenant operations."""
        try:
            if not tenant_context:
                return False
            
            self.tenant_context = tenant_context
            self.tenant_id = tenant_context.get("tenant_id")
            self.tenant_user_id = tenant_context.get("user_id")
            
            # Validate tenant context using tenant utility
            if self.tenant_id:
                tenant_config = self.tenant.get_tenant_config("organization")  # Default to organization
                self.logger.info(f"Tenant context validated for {self.tenant_id}")
            
            self.logger.info(f"Tenant context set for agentic service {self.service_name}: {self.tenant_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set tenant context: {e}")
            self.error_handler.handle_error(e, f"{self.service_name}_set_tenant_context_failed")
            return False
    
    async def _load_agentic_abstractions(self):
        """Load agentic business abstractions from public works foundation."""
        try:
            if self.public_works_foundation:
                # Get agentic abstractions from public works
                self.agentic_abstractions = await self.public_works_foundation.get_agentic_abstractions()
                self.logger.info(f"Loaded {len(self.agentic_abstractions)} agentic business abstractions")
            else:
                self.logger.warning("Public works foundation not available - using limited abstractions")
        except Exception as e:
            self.logger.error(f"Failed to load agentic abstractions: {e}")
            self.error_handler.handle_error(e, f"{self.service_name}_load_agentic_abstractions_failed")
            self.agentic_abstractions = {}
    
    @abstractmethod
    async def _initialize_service(self):
        """Initialize service-specific functionality. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agentic service. Must be implemented by subclasses."""
        pass
    
    async def run_health_check(self) -> Dict[str, Any]:
        """Run health checks for the agentic service."""
        self.logger.info(f"Running health check for agentic service {self.service_name}...")
        
        overall_status = "healthy"
        checks = {}
        
        # Check foundation services
        fs_status = await self.foundation_services.get_container_health()
        checks["foundation_services"] = fs_status
        if fs_status["status"] != "healthy":
            overall_status = "degraded"
        
        # Check public works foundation
        if self.public_works_foundation:
            pwf_status = await self.public_works_foundation.get_status()
            checks["public_works_foundation"] = pwf_status
            if pwf_status["status"] != "healthy":
                overall_status = "degraded"
        
        # Check agentic abstractions
        checks["agentic_abstractions"] = {
            "count": len(self.agentic_abstractions),
            "status": "loaded" if self.agentic_abstractions else "empty"
        }
        
        # Check tenant context
        checks["tenant_context"] = {
            "tenant_id": self.tenant_id,
            "tenant_user_id": self.tenant_user_id,
            "isolation_enabled": self.tenant_isolation_enabled
        }
        
        # Get service-specific status
        service_status = await self.get_status()
        checks["service_status"] = service_status
        
        self.logger.info(f"✅ Health check completed for agentic service {self.service_name}: {overall_status}")
        return {
            "service_name": self.service_name,
            "overall_status": overall_status,
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def shutdown(self):
        """Shutdown the agentic service."""
        self.logger.info(f"Shutting down agentic service {self.service_name}...")
        # Perform cleanup
        self.is_initialized = False
        self.logger.info(f"Agentic service {self.service_name} shut down.")



















