#!/usr/bin/env python3
"""
SOA Client Abstraction - Service-Oriented Architecture Client Implementation

SOA Client abstraction that provides inter-realm communication via
service-oriented architecture patterns using Curator Foundation for service discovery.

WHAT (Infrastructure Abstraction): I provide SOA Client for inter-realm communication
HOW (Infrastructure Implementation): I use Curator Foundation for service discovery and API Gateway for routing
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

# Import abstraction contracts
from ..abstraction_contracts.soa_api_protocol import (
    SOAAPIProtocol, SOAAPIService, SOAAPIRequest, SOAAPIResponse, SOAAPIStatus
)

# Import DI Container and Curator Foundation
from foundations.di_container.di_container_service import DIContainerService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService

# Import communication abstraction
from .communication_abstraction import CommunicationAbstraction

logger = logging.getLogger(__name__)


class SOAClientAbstraction(SOAAPIProtocol):
    """
    SOA Client Abstraction - Service-Oriented Architecture Client Implementation
    
    Provides inter-realm communication via service-oriented architecture patterns
    using Curator Foundation for service discovery and API Gateway for routing.
    
    WHAT (Infrastructure Abstraction): I provide SOA Client for inter-realm communication
    HOW (Infrastructure Implementation): I use Curator Foundation for service discovery and API Gateway for routing
    """
    
    def __init__(self, di_container: DIContainerService,
                 curator_foundation: Optional[CuratorFoundationService],
                 communication_abstraction: CommunicationAbstraction):
        """Initialize SOA Client Abstraction."""
        self.logger = logging.getLogger("SOAClientAbstraction")
        self.di_container = di_container
        self.curator_foundation = curator_foundation
        self.communication_abstraction = communication_abstraction
        
        # SOA service registry
        self.soa_services = {}
        self.soa_requests = {}
        self.soa_responses = {}
        
        # Service state
        self.is_initialized = False
        self.is_running = False
        
        self.logger.info("🏗️ SOA Client Abstraction initialized")
    
    async def initialize(self):
        """Initialize SOA Client Abstraction."""
        self.logger.info("🚀 Initializing SOA Client Abstraction...")
        
        try:
            # Initialize Curator Foundation if available
            if self.curator_foundation:
                await self.curator_foundation.initialize()
            
            # Initialize Communication Abstraction
            await self.communication_abstraction.initialize()
            
            # Discover existing SOA services
            await self._discover_existing_services()
            
            self.is_initialized = True
            self.logger.info("✅ SOA Client Abstraction initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize SOA Client Abstraction: {e}")
            raise
    
    async def _discover_existing_services(self):
        """Discover existing SOA services from Curator Foundation."""
        self.logger.info("🔍 Discovering existing SOA services...")
        
        if self.curator_foundation:
            try:
                # Get all registered services
                services = await self.curator_foundation.get_all_services()
                
                for service in services:
                    if service.get("type") == "soa_api":
                        await self._register_discovered_service(service)
                
                self.logger.info(f"✅ Discovered {len(self.soa_services)} SOA services")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to discover services: {e}")
        else:
            self.logger.warning("⚠️ Curator Foundation not available for service discovery")
    
    async def _register_discovered_service(self, service_info: Dict[str, Any]):
        """Register discovered service."""
        try:
            service = SOAAPIService(
                service_name=service_info["name"],
                realm=service_info["realm"],
                base_url=service_info["base_url"],
                version=service_info.get("version", "1.0.0"),
                status=SOAAPIStatus.ACTIVE
            )
            
            self.soa_services[f"{service.realm}:{service.service_name}"] = service
            self.logger.info(f"✅ Registered discovered service: {service.realm}:{service.service_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register discovered service: {e}")
    
    async def start(self):
        """Start SOA Client Abstraction."""
        if not self.is_initialized:
            await self.initialize()
        
        self.logger.info("🚀 Starting SOA Client Abstraction...")
        
        try:
            # Start Curator Foundation if available
            if self.curator_foundation:
                await self.curator_foundation.start()
            
            # Start Communication Abstraction
            await self.communication_abstraction.start()
            
            self.is_running = True
            self.logger.info("✅ SOA Client Abstraction started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start SOA Client Abstraction: {e}")
            raise
    
    async def stop(self):
        """Stop SOA Client Abstraction."""
        self.logger.info("🛑 Stopping SOA Client Abstraction...")
        
        try:
            # Stop Communication Abstraction
            await self.communication_abstraction.stop()
            
            # Stop Curator Foundation if available
            if self.curator_foundation:
                await self.curator_foundation.stop()
            
            self.is_running = False
            self.logger.info("✅ SOA Client Abstraction stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop SOA Client Abstraction: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown SOA Client Abstraction."""
        await self.stop()
        self.logger.info("🔌 SOA Client Abstraction shutdown complete")
    
    # SOA API Protocol Implementation
    
    async def register_service(self, service: SOAAPIService) -> bool:
        """Register SOA API service."""
        try:
            service_key = f"{service.realm}:{service.service_name}"
            self.soa_services[service_key] = service
            
            # Register with Curator Foundation if available
            if self.curator_foundation:
                await self.curator_foundation.register_soa_api(
                    service_name=service.service_name,
                    api_endpoints=service.endpoints
                )
            
            self.logger.info(f"✅ SOA service registered: {service_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register SOA service: {e}")
            return False
    
    async def unregister_service(self, service_name: str, realm: str) -> bool:
        """Unregister SOA API service."""
        try:
            service_key = f"{realm}:{service_name}"
            
            if service_key in self.soa_services:
                del self.soa_services[service_key]
                
                # Unregister from Curator Foundation if available
                if self.curator_foundation:
                    await self.curator_foundation.unregister_soa_api(service_name, realm)
                
                self.logger.info(f"✅ SOA service unregistered: {service_key}")
                return True
            else:
                self.logger.warning(f"⚠️ SOA service not found: {service_key}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to unregister SOA service: {e}")
            return False
    
    async def discover_service(self, service_name: str, realm: str) -> Optional[SOAAPIService]:
        """Discover SOA API service."""
        try:
            service_key = f"{realm}:{service_name}"
            
            # Check local registry first
            if service_key in self.soa_services:
                return self.soa_services[service_key]
            
            # Try to discover from Curator Foundation
            if self.curator_foundation:
                service_info = await self.curator_foundation.discover_soa_api(service_name, realm)
                if service_info:
                    service = SOAAPIService(
                        service_name=service_info["name"],
                        realm=service_info["realm"],
                        base_url=service_info["base_url"],
                        version=service_info.get("version", "1.0.0"),
                        status=SOAAPIStatus.ACTIVE
                    )
                    self.soa_services[service_key] = service
                    return service
            
            self.logger.warning(f"⚠️ SOA service not found: {service_key}")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Failed to discover SOA service: {e}")
            return None
    
    async def get_service_endpoints(self, service_name: str, realm: str) -> Dict[str, Any]:
        """Get service endpoints."""
        try:
            service = await self.discover_service(service_name, realm)
            if service:
                return service.endpoints
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get service endpoints: {e}")
            return {}
    
    async def call_service(self, request: SOAAPIRequest) -> Optional[SOAAPIResponse]:
        """Call SOA API service."""
        try:
            # Discover service
            service = await self.discover_service(request.service_name, request.source_realm)
            if not service:
                return SOAAPIResponse(
                    request_id=request.request_id,
                    status_code=404,
                    response_data={"error": "Service not found"},
                    response_time_ms=0,
                    error_message="Service not found"
                )
            
            # Create SOA API request via Communication Abstraction
            start_time = datetime.now()
            
            context = await self.communication_abstraction.send_soa_api_request(
                target_realm=service.realm,
                service_name=request.service_name,
                endpoint=request.endpoint,
                request_data=request.request_data,
                correlation_id=request.correlation_id,
                tenant_id=request.tenant_id
            )
            
            end_time = datetime.now()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            if context and context.status.value == "sent":
                response = SOAAPIResponse(
                    request_id=request.request_id,
                    status_code=200,
                    response_data=context.content,
                    response_time_ms=response_time_ms
                )
                
                self.soa_responses[request.request_id] = response
                self.logger.info(f"✅ SOA API call successful: {request.service_name}/{request.endpoint}")
                return response
            else:
                response = SOAAPIResponse(
                    request_id=request.request_id,
                    status_code=500,
                    response_data={"error": "Service call failed"},
                    response_time_ms=response_time_ms,
                    error_message="Service call failed"
                )
                
                self.logger.error(f"❌ SOA API call failed: {request.service_name}/{request.endpoint}")
                return response
                
        except Exception as e:
            self.logger.error(f"❌ Failed to call SOA service: {e}")
            return SOAAPIResponse(
                request_id=request.request_id,
                status_code=500,
                response_data={"error": str(e)},
                response_time_ms=0,
                error_message=str(e)
            )
    
    async def get_service_health(self, service_name: str, realm: str) -> Dict[str, Any]:
        """Get service health status."""
        try:
            service = await self.discover_service(service_name, realm)
            if service:
                return {
                    "service_name": service.service_name,
                    "realm": service.realm,
                    "status": service.status.value,
                    "health_status": service.health_status,
                    "response_time_ms": service.response_time_ms,
                    "last_updated": service.last_updated.isoformat()
                }
            else:
                return {
                    "service_name": service_name,
                    "realm": realm,
                    "status": "not_found",
                    "health_status": "unknown",
                    "response_time_ms": 0
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get service health: {e}")
            return {
                "service_name": service_name,
                "realm": realm,
                "status": "error",
                "health_status": "error",
                "response_time_ms": 0,
                "error": str(e)
            }
    
    async def get_service_stats(self, service_name: str, realm: str) -> Dict[str, Any]:
        """Get service statistics."""
        try:
            service = await self.discover_service(service_name, realm)
            if service:
                return {
                    "service_name": service.service_name,
                    "realm": service.realm,
                    "version": service.version,
                    "status": service.status.value,
                    "endpoint_count": len(service.endpoints),
                    "created_at": service.created_at.isoformat(),
                    "last_updated": service.last_updated.isoformat()
                }
            else:
                return {
                    "service_name": service_name,
                    "realm": realm,
                    "status": "not_found"
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get service stats: {e}")
            return {
                "service_name": service_name,
                "realm": realm,
                "status": "error",
                "error": str(e)
            }
    
    async def list_services(self, realm: Optional[str] = None) -> List[SOAAPIService]:
        """List all services or services for specific realm."""
        try:
            if realm:
                return [
                    service for service in self.soa_services.values()
                    if service.realm == realm
                ]
            else:
                return list(self.soa_services.values())
                
        except Exception as e:
            self.logger.error(f"❌ Failed to list services: {e}")
            return []
    
    async def update_service_status(self, service_name: str, realm: str, 
                                  status: SOAAPIStatus) -> bool:
        """Update service status."""
        try:
            service_key = f"{realm}:{service_name}"
            
            if service_key in self.soa_services:
                self.soa_services[service_key].status = status
                self.soa_services[service_key].last_updated = datetime.now()
                
                self.logger.info(f"✅ Service status updated: {service_key} -> {status.value}")
                return True
            else:
                self.logger.warning(f"⚠️ Service not found: {service_key}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to update service status: {e}")
            return False
