#!/usr/bin/env python3
"""
SOA Composition Service - Service-Oriented Architecture Orchestration

SOA composition service that orchestrates service-oriented architecture
communication patterns for inter-realm service communication.

WHAT (Composition Service): I orchestrate SOA communication patterns
HOW (Composition Implementation): I coordinate SOA client and service discovery
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import infrastructure abstractions
from ..infrastructure_abstractions.soa_client_abstraction import SOAClientAbstraction

# Import Curator Foundation
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService

# Import abstraction contracts
from ..abstraction_contracts.soa_api_protocol import (
    SOAAPIService, SOAAPIRequest, SOAAPIResponse, SOAAPIStatus
)

logger = logging.getLogger(__name__)


class SOACompositionService:
    """
    SOA Composition Service - Service-Oriented Architecture Orchestration
    
    Orchestrates service-oriented architecture communication patterns
    for inter-realm service communication.
    
    WHAT (Composition Service): I orchestrate SOA communication patterns
    HOW (Composition Implementation): I coordinate SOA client and service discovery
    """
    
    def __init__(self, soa_client_abstraction: SOAClientAbstraction,
                 curator_foundation: Optional[CuratorFoundationService]):
        """Initialize SOA Composition Service."""
        self.logger = logging.getLogger("SOACompositionService")
        
        # Infrastructure abstractions
        self.soa_client_abstraction = soa_client_abstraction
        self.curator_foundation = curator_foundation
        
        # SOA orchestration
        self.soa_services = {}
        self.soa_requests = {}
        self.soa_responses = {}
        
        # Service state
        self.is_initialized = False
        self.is_running = False
        
        self.logger.info("🏗️ SOA Composition Service initialized")
    
    async def initialize(self):
        """Initialize SOA Composition Service."""
        try:
            self.logger.info("🚀 Initializing SOA Composition Service...")
            
            # Initialize SOA client abstraction
            await self.soa_client_abstraction.initialize()
            
            # Initialize Curator Foundation if available
            if self.curator_foundation:
                await self.curator_foundation.initialize()
            
            # Discover and register SOA services
            await self._discover_and_register_services()
            
            self.is_initialized = True
            self.logger.info("✅ SOA Composition Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize SOA Composition Service: {e}", exc_info=True)
            raise
    
    async def _discover_and_register_services(self):
        """Discover and register SOA services from Curator Foundation."""
        self.logger.info("🔍 Discovering and registering SOA services...")
        
        if self.curator_foundation:
            try:
                # Get all registered services
                services = await self.curator_foundation.get_all_services()
                
                for service in services:
                    if service.get("type") == "soa_api":
                        await self._register_soa_service(service)
                
                self.logger.info(f"✅ Discovered and registered {len(self.soa_services)} SOA services")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to discover services: {e}")
        else:
            self.logger.warning("⚠️ Curator Foundation not available for service discovery")
    
    async def _register_soa_service(self, service_info: Dict[str, Any]):
        """Register SOA service."""
        try:
            service = SOAAPIService(
                service_name=service_info["name"],
                realm=service_info["realm"],
                base_url=service_info["base_url"],
                version=service_info.get("version", "1.0.0"),
                status=SOAAPIStatus.ACTIVE
            )
            
            # Register with SOA client abstraction
            await self.soa_client_abstraction.register_service(service)
            
            # Store locally
            service_key = f"{service.realm}:{service.service_name}"
            self.soa_services[service_key] = service
            
            self.logger.info(f"✅ SOA service registered: {service_key}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register SOA service: {e}")
    
    async def start(self):
        """Start SOA Composition Service."""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            self.logger.info("🚀 Starting SOA Composition Service...")
            
            # Start SOA client abstraction
            await self.soa_client_abstraction.start()
            
            # Start Curator Foundation if available
            if self.curator_foundation:
                await self.curator_foundation.start()
            
            self.is_running = True
            self.logger.info("✅ SOA Composition Service started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start SOA Composition Service: {e}", exc_info=True)
            raise
    
    async def stop(self):
        """Stop SOA Composition Service."""
        try:
            self.logger.info("🛑 Stopping SOA Composition Service...")
            
            # Stop Curator Foundation if available
            if self.curator_foundation:
                await self.curator_foundation.stop()
            
            # Stop SOA client abstraction
            await self.soa_client_abstraction.stop()
            
            self.is_running = False
            self.logger.info("✅ SOA Composition Service stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop SOA Composition Service: {e}", exc_info=True)
            raise
    
    async def shutdown(self):
        """Shutdown SOA Composition Service."""
        try:
            await self.stop()
            self.logger.info("🔌 SOA Composition Service shutdown complete")
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown SOA Composition Service: {e}", exc_info=True)
            raise
    
    # SOA orchestration methods
    
    async def orchestrate_soa_api_call(self, source_realm: str, target_realm: str,
                                     service_name: str, endpoint: str,
                                     request_data: Dict[str, Any],
                                     correlation_id: Optional[str] = None,
                                     tenant_id: Optional[str] = None) -> Optional[SOAAPIResponse]:
        """Orchestrate SOA API call."""
        try:
            self.logger.info(f"🎭 Orchestrating SOA API call: {source_realm} -> {target_realm}/{service_name}/{endpoint}")
            
            # Create SOA API request
            request = SOAAPIRequest(
                request_id=str(uuid.uuid4()),
                service_name=service_name,
                endpoint=endpoint,
                request_data=request_data,
                source_realm=source_realm,
                correlation_id=correlation_id,
                tenant_id=tenant_id
            )
            
            # Store request
            self.soa_requests[request.request_id] = request
            
            # Execute SOA API call
            response = await self.soa_client_abstraction.call_service(request)
            
            if response:
                # Store response
                self.soa_responses[request.request_id] = response
                
                self.logger.info(f"✅ SOA API call orchestrated successfully: {source_realm} -> {target_realm}/{service_name}")
                return response
            else:
                self.logger.error(f"❌ Failed to orchestrate SOA API call: {source_realm} -> {target_realm}/{service_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Failed to orchestrate SOA API call: {e}")
            return None
    
    async def orchestrate_service_discovery(self, service_name: str, realm: str) -> Optional[SOAAPIService]:
        """Orchestrate service discovery."""
        try:
            self.logger.info(f"🔍 Orchestrating service discovery: {service_name} in {realm}")
            
            # Discover service via SOA client abstraction
            service = await self.soa_client_abstraction.discover_service(service_name, realm)
            
            if service:
                self.logger.info(f"✅ Service discovered: {service_name} in {realm}")
                return service
            else:
                self.logger.warning(f"⚠️ Service not found: {service_name} in {realm}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Failed to orchestrate service discovery: {e}")
            return None
    
    async def orchestrate_service_registration(self, service: SOAAPIService) -> bool:
        """Orchestrate service registration."""
        try:
            self.logger.info(f"📝 Orchestrating service registration: {service.service_name} in {service.realm}")
            
            # Register service via SOA client abstraction
            success = await self.soa_client_abstraction.register_service(service)
            
            if success:
                # Store locally
                service_key = f"{service.realm}:{service.service_name}"
                self.soa_services[service_key] = service
                
                self.logger.info(f"✅ Service registered: {service.service_name} in {service.realm}")
                return True
            else:
                self.logger.error(f"❌ Failed to register service: {service.service_name} in {service.realm}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to orchestrate service registration: {e}")
            return False
    
    async def orchestrate_service_health_check(self, service_name: str, realm: str) -> Dict[str, Any]:
        """Orchestrate service health check."""
        try:
            self.logger.info(f"🏥 Orchestrating service health check: {service_name} in {realm}")
            
            # Get service health via SOA client abstraction
            health_info = await self.soa_client_abstraction.get_service_health(service_name, realm)
            
            self.logger.info(f"✅ Service health check completed: {service_name} in {realm}")
            return health_info
            
        except Exception as e:
            self.logger.error(f"❌ Failed to orchestrate service health check: {e}")
            return {
                "service_name": service_name,
                "realm": realm,
                "status": "error",
                "error": str(e)
            }
    
    async def orchestrate_service_monitoring(self) -> Dict[str, Any]:
        """Orchestrate service monitoring."""
        try:
            self.logger.info("📊 Orchestrating service monitoring...")
            
            monitoring_info = {
                "total_services": len(self.soa_services),
                "total_requests": len(self.soa_requests),
                "total_responses": len(self.soa_responses),
                "services_by_realm": {},
                "service_health": {}
            }
            
            # Group services by realm
            for service in self.soa_services.values():
                realm = service.realm
                if realm not in monitoring_info["services_by_realm"]:
                    monitoring_info["services_by_realm"][realm] = 0
                monitoring_info["services_by_realm"][realm] += 1
            
            # Check health of all services
            for service_key, service in self.soa_services.items():
                health_info = await self.orchestrate_service_health_check(
                    service.service_name, service.realm
                )
                monitoring_info["service_health"][service_key] = health_info
            
            self.logger.info("✅ Service monitoring completed")
            return monitoring_info
            
        except Exception as e:
            self.logger.error(f"❌ Failed to orchestrate service monitoring: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    # Public API methods
    
    async def get_soa_services(self, user_context: Dict[str, Any] = None) -> Dict[str, SOAAPIService]:
        """Get all SOA services."""
        try:
            self.logger.debug("Getting SOA services")
            
            # Note: Composition services don't have utility access yet
            # Security/tenant validation would be added when DI Container access is available
            
            return self.soa_services
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get SOA services: {e}", exc_info=True)
            return {}
    
    async def get_soa_requests(self, user_context: Dict[str, Any] = None) -> Dict[str, SOAAPIRequest]:
        """Get all SOA requests."""
        try:
            self.logger.debug("Getting SOA requests")
            
            # Note: Composition services don't have utility access yet
            # Security/tenant validation would be added when DI Container access is available
            
            return self.soa_requests
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get SOA requests: {e}", exc_info=True)
            return {}
    
    async def get_soa_responses(self, user_context: Dict[str, Any] = None) -> Dict[str, SOAAPIResponse]:
        """Get all SOA responses."""
        try:
            self.logger.debug("Getting SOA responses")
            
            # Note: Composition services don't have utility access yet
            # Security/tenant validation would be added when DI Container access is available
            
            return self.soa_responses
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get SOA responses: {e}", exc_info=True)
            return {}
    
    async def get_soa_service_by_key(self, service_key: str, user_context: Dict[str, Any] = None) -> Optional[SOAAPIService]:
        """Get SOA service by key."""
        try:
            self.logger.debug(f"Getting SOA service by key: {service_key}")
            
            # Note: Composition services don't have utility access yet
            # Security/tenant validation would be added when DI Container access is available
            
            return self.soa_services.get(service_key)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get SOA service by key {service_key}: {e}", exc_info=True)
            return None
    
    async def get_soa_request_by_id(self, request_id: str, user_context: Dict[str, Any] = None) -> Optional[SOAAPIRequest]:
        """Get SOA request by ID."""
        try:
            self.logger.debug(f"Getting SOA request by ID: {request_id}")
            
            # Note: Composition services don't have utility access yet
            # Security/tenant validation would be added when DI Container access is available
            
            return self.soa_requests.get(request_id)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get SOA request by ID {request_id}: {e}", exc_info=True)
            return None
    
    async def get_soa_response_by_id(self, response_id: str, user_context: Dict[str, Any] = None) -> Optional[SOAAPIResponse]:
        """Get SOA response by ID."""
        try:
            self.logger.debug(f"Getting SOA response by ID: {response_id}")
            
            # Note: Composition services don't have utility access yet
            # Security/tenant validation would be added when DI Container access is available
            
            return self.soa_responses.get(response_id)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get SOA response by ID {response_id}: {e}", exc_info=True)
            return None
    
    async def get_composition_stats(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get composition service statistics."""
        try:
            self.logger.debug("Getting composition stats")
            
            # Note: Composition services don't have utility access yet
            # Security/tenant validation would be added when DI Container access is available
            
            return {
                "is_running": self.is_running,
                "is_initialized": self.is_initialized,
                "total_services": len(self.soa_services),
                "total_requests": len(self.soa_requests),
                "total_responses": len(self.soa_responses),
                "services_by_realm": {
                    realm: len([s for s in self.soa_services.values() if s.realm == realm])
                    for realm in set(s.realm for s in self.soa_services.values())
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get composition stats: {e}", exc_info=True)
            return {}
