#!/usr/bin/env python3
"""
SOA Client Service - Curator Foundation

Provides SOA client capabilities for inter-service communication.

WHAT (Service Role): I provide SOA client for service discovery and communication
HOW (Service Implementation): I use Curator registry for service discovery and make SOA API calls
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import httpx

from bases.foundation_service_base import FoundationServiceBase


class SOAClientService(FoundationServiceBase):
    """
    SOA Client Service - Curator Foundation
    
    Provides SOA client capabilities for inter-service communication.
    Uses Curator registry for service discovery.
    
    WHAT (Service Role): I provide SOA client for service discovery and communication
    HOW (Service Implementation): I use Curator registry for service discovery and make SOA API calls
    """
    
    def __init__(self, di_container, curator_foundation=None):
        """Initialize SOA Client Service."""
        super().__init__("soa_client", di_container)
        
        # Store Curator Foundation reference (self-reference for service discovery)
        self.curator_foundation = curator_foundation
        
        # SOA service registry (cached from Curator)
        self.soa_services: Dict[str, Dict[str, Any]] = {}
        
        # Request/response tracking
        self.soa_requests: Dict[str, Dict[str, Any]] = {}
        self.soa_responses: Dict[str, Dict[str, Any]] = {}
        
        # HTTP client for SOA API calls
        self.http_client: Optional[httpx.AsyncClient] = None
        
        # Service state
        self.is_initialized = False
        
        self.logger.info("🏗️ SOA Client Service initialized")
    
    async def initialize(self):
        """Initialize SOA Client Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("soa_client_initialize_start", success=True)
            
            await super().initialize()
            self.logger.info("🚀 Initializing SOA Client Service...")
            
            # Get Curator Foundation from DI Container if not provided
            if not self.curator_foundation:
                if hasattr(self.di_container, 'get_foundation_service'):
                    self.curator_foundation = self.di_container.get_foundation_service("CuratorFoundationService")
            
            # Initialize HTTP client for SOA API calls
            self.http_client = httpx.AsyncClient(timeout=30.0)
            
            # Discover existing SOA services from Curator
            await self._discover_existing_services()
            
            self.is_initialized = True
            self.logger.info("✅ SOA Client Service initialized successfully")
            
            # Record health metric
            await self.record_health_metric("soa_client_initialized", 1.0, {"service": "soa_client"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("soa_client_initialize_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "soa_client_initialize")
            self.logger.error(f"❌ Failed to initialize SOA Client Service: {e}")
            raise
    
    async def _discover_existing_services(self):
        """Discover existing SOA services from Curator registry."""
        self.logger.info("🔍 Discovering existing SOA services from Curator...")
        
        if not self.curator_foundation:
            self.logger.warning("⚠️ Curator Foundation not available for service discovery")
            return
        
        try:
            # Get all registered services from Curator
            # Note: This depends on Curator's service discovery API
            # For now, we'll discover services as they're needed (lazy discovery)
            self.logger.info("✅ SOA Client Service ready for service discovery")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover services: {e}")
    
    async def discover_service(self, service_name: str, realm: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Discover SOA service from Curator registry.
        
        Args:
            service_name: Name of the service
            realm: Optional realm name (if None, searches all realms)
        
        Returns:
            Service information dict, or None if not found
        """
        try:
            service_key = f"{realm}:{service_name}" if realm else service_name
            
            # Check local cache first
            if service_key in self.soa_services:
                return self.soa_services[service_key]
            
            # Discover from Curator
            if self.curator_foundation:
                # Use Curator's service discovery
                # Note: This depends on Curator's actual API - may need to adjust based on implementation
                if hasattr(self.curator_foundation, 'discover_service'):
                    service_info = await self.curator_foundation.discover_service(service_name, realm)
                    if service_info:
                        self.soa_services[service_key] = service_info
                        return service_info
                elif hasattr(self.curator_foundation, 'get_service'):
                    # Alternative: use get_service method
                    service_info = await self.curator_foundation.get_service(service_name, realm)
                    if service_info:
                        self.soa_services[service_key] = service_info
                        return service_info
            
            self.logger.warning(f"⚠️ SOA service not found: {service_key}")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Failed to discover SOA service: {e}")
            return None
    
    async def call_service(self, service_name: str, endpoint: str, request_data: Dict[str, Any],
                          realm: Optional[str] = None, correlation_id: Optional[str] = None,
                          tenant_id: Optional[str] = None, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Call SOA API service.
        
        Args:
            service_name: Name of the service
            endpoint: API endpoint (e.g., "/api/service/method")
            request_data: Request data
            realm: Optional realm name
            correlation_id: Optional correlation ID for tracing
            tenant_id: Optional tenant ID
        
        Returns:
            Response dict with success status and data
        """
        request_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "soa_client_call_start",
                success=True,
                details={"service_name": service_name, "endpoint": endpoint, "realm": realm}
            )
            
            # Discover service
            service_info = await self.discover_service(service_name, realm)
            if not service_info:
                return {
                    "success": False,
                    "error": f"Service not found: {service_name}",
                    "request_id": request_id
                }
            
            # Get service base URL
            base_url = service_info.get("base_url") or service_info.get("endpoint")
            if not base_url:
                return {
                    "success": False,
                    "error": f"Service base URL not found: {service_name}",
                    "request_id": request_id
                }
            
            # Build full URL
            full_url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            
            # Store request
            self.soa_requests[request_id] = {
                "service_name": service_name,
                "realm": realm,
                "endpoint": endpoint,
                "url": full_url,
                "request_data": request_data,
                "correlation_id": correlation_id,
                "tenant_id": tenant_id,
                "workflow_id": workflow_id,  # ✅ Phase 0.5: Store workflow_id
                "start_time": start_time.isoformat()
            }
            
            # Make HTTP request
            if not self.http_client:
                self.http_client = httpx.AsyncClient(timeout=30.0)
            
            headers = {}
            if correlation_id:
                headers["X-Correlation-ID"] = correlation_id
            if workflow_id:  # ✅ Phase 0.5: Add workflow_id header
                headers["X-Workflow-ID"] = workflow_id
            if tenant_id:
                headers["X-Tenant-ID"] = tenant_id
            
            response = await self.http_client.post(
                full_url,
                json=request_data,
                headers=headers
            )
            
            end_time = datetime.utcnow()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Parse response
            if response.is_success:
                response_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"raw": response.text}
                result = {
                    "success": True,
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "response_data": response_data,
                    "response_time_ms": response_time_ms
                }
            else:
                result = {
                    "success": False,
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "error": response.text,
                    "response_time_ms": response_time_ms
                }
            
            # Store response
            self.soa_responses[request_id] = result
            
            # Record health metric
            await self.record_health_metric(
                "soa_client_call_complete",
                1.0 if result.get("success") else 0.0,
                {
                    "service_name": service_name,
                    "endpoint": endpoint,
                    "realm": realm,
                    "response_time_ms": response_time_ms,
                    "success": result.get("success")
                }
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "soa_client_call_complete",
                success=result.get("success", False),
                details={
                    "service_name": service_name,
                    "endpoint": endpoint,
                    "realm": realm,
                    "response_time_ms": response_time_ms
                }
            )
            
            return result
            
        except httpx.HTTPError as e:
            end_time = datetime.utcnow()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            result = {
                "success": False,
                "request_id": request_id,
                "error": str(e),
                "response_time_ms": response_time_ms
            }
            
            # Store response
            self.soa_responses[request_id] = result
            
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "soa_client_call", details={
                "service_name": service_name,
                "endpoint": endpoint,
                "realm": realm
            })
            
            return result
            
        except Exception as e:
            end_time = datetime.utcnow()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            result = {
                "success": False,
                "request_id": request_id,
                "error": str(e),
                "response_time_ms": response_time_ms
            }
            
            # Store response
            self.soa_responses[request_id] = result
            
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "soa_client_call", details={
                "service_name": service_name,
                "endpoint": endpoint,
                "realm": realm
            })
            
            return result
    
    async def get_service_health(self, service_name: str, realm: Optional[str] = None) -> Dict[str, Any]:
        """
        Get service health status.
        
        Args:
            service_name: Name of the service
            realm: Optional realm name
        
        Returns:
            Health status dict
        """
        try:
            service_info = await self.discover_service(service_name, realm)
            if service_info:
                return {
                    "service_name": service_name,
                    "realm": realm,
                    "status": service_info.get("status", "unknown"),
                    "health_status": service_info.get("health_status", "unknown"),
                    "last_updated": service_info.get("last_updated", datetime.utcnow().isoformat())
                }
            else:
                return {
                    "service_name": service_name,
                    "realm": realm,
                    "status": "not_found",
                    "health_status": "unknown"
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get service health: {e}")
            return {
                "service_name": service_name,
                "realm": realm,
                "status": "error",
                "health_status": "error",
                "error": str(e)
            }
    
    async def list_services(self, realm: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all services or services for specific realm.
        
        Args:
            realm: Optional realm name (if None, returns all services)
        
        Returns:
            List of service information dicts
        """
        try:
            if realm:
                return [
                    service for key, service in self.soa_services.items()
                    if service.get("realm") == realm
                ]
            else:
                return list(self.soa_services.values())
                
        except Exception as e:
            self.logger.error(f"❌ Failed to list services: {e}")
            return []
    
    async def shutdown(self):
        """Shutdown SOA Client Service."""
        self.logger.info("🛑 Shutting down SOA Client Service...")
        
        try:
            # Close HTTP client
            if self.http_client:
                await self.http_client.aclose()
                self.http_client = None
            
            # Clear caches
            self.soa_services.clear()
            self.soa_requests.clear()
            self.soa_responses.clear()
            
            self.is_initialized = False
            self.logger.info("✅ SOA Client Service shutdown complete")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown SOA Client Service: {e}")
            raise







