#!/usr/bin/env python3
"""
SOA API Protocol - Service-Oriented Architecture API Interface

Defines the SOA API protocol for inter-realm service communication
via standardized service-oriented architecture patterns.

WHAT (Abstraction Contract): I define the SOA API interface for inter-realm communication
HOW (Protocol Definition): I specify the contract for SOA API operations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class SOAAPIStatus(Enum):
    """SOA API status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    MAINTENANCE = "maintenance"


class SOAAPIEndpoint:
    """SOA API endpoint definition."""
    
    def __init__(self, endpoint_name: str, endpoint_path: str, http_method: str,
                 description: str = "", version: str = "1.0.0",
                 requires_auth: bool = True, rate_limit: Optional[int] = None):
        """Initialize SOA API endpoint."""
        self.endpoint_name = endpoint_name
        self.endpoint_path = endpoint_path
        self.http_method = http_method
        self.description = description
        self.version = version
        self.requires_auth = requires_auth
        self.rate_limit = rate_limit
        self.created_at = datetime.now()
        self.last_accessed = None
        self.access_count = 0


class SOAAPIService:
    """SOA API service definition."""
    
    def __init__(self, service_name: str, realm: str, base_url: str,
                 version: str = "1.0.0", status: SOAAPIStatus = SOAAPIStatus.ACTIVE):
        """Initialize SOA API service."""
        self.service_name = service_name
        self.realm = realm
        self.base_url = base_url
        self.version = version
        self.status = status
        self.endpoints = {}
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.health_status = "unknown"
        self.response_time_ms = 0


class SOAAPIRequest:
    """SOA API request definition."""
    
    def __init__(self, request_id: str, service_name: str, endpoint: str,
                 request_data: Dict[str, Any], source_realm: str,
                 correlation_id: Optional[str] = None, tenant_id: Optional[str] = None):
        """Initialize SOA API request."""
        self.request_id = request_id
        self.service_name = service_name
        self.endpoint = endpoint
        self.request_data = request_data
        self.source_realm = source_realm
        self.correlation_id = correlation_id
        self.tenant_id = tenant_id
        self.timestamp = datetime.now()
        self.status = "pending"
        self.response_data = None
        self.error_message = None


class SOAAPIResponse:
    """SOA API response definition."""
    
    def __init__(self, request_id: str, status_code: int, response_data: Dict[str, Any],
                   response_time_ms: int, error_message: Optional[str] = None):
        """Initialize SOA API response."""
        self.request_id = request_id
        self.status_code = status_code
        self.response_data = response_data
        self.response_time_ms = response_time_ms
        self.error_message = error_message
        self.timestamp = datetime.now()


class SOAAPIProtocol(ABC):
    """SOA API protocol interface for service-oriented architecture."""
    
    @abstractmethod
    async def register_service(self, service: SOAAPIService) -> bool:
        """Register SOA API service."""
        pass
    
    @abstractmethod
    async def unregister_service(self, service_name: str, realm: str) -> bool:
        """Unregister SOA API service."""
        pass
    
    @abstractmethod
    async def discover_service(self, service_name: str, realm: str) -> Optional[SOAAPIService]:
        """Discover SOA API service."""
        pass
    
    @abstractmethod
    async def get_service_endpoints(self, service_name: str, realm: str) -> Dict[str, SOAAPIEndpoint]:
        """Get service endpoints."""
        pass
    
    @abstractmethod
    async def call_service(self, request: SOAAPIRequest) -> Optional[SOAAPIResponse]:
        """Call SOA API service."""
        pass
    
    @abstractmethod
    async def get_service_health(self, service_name: str, realm: str) -> Dict[str, Any]:
        """Get service health status."""
        pass
    
    @abstractmethod
    async def get_service_stats(self, service_name: str, realm: str) -> Dict[str, Any]:
        """Get service statistics."""
        pass
    
    @abstractmethod
    async def list_services(self, realm: Optional[str] = None) -> List[SOAAPIService]:
        """List all services or services for specific realm."""
        pass
    
    @abstractmethod
    async def update_service_status(self, service_name: str, realm: str, 
                                  status: SOAAPIStatus) -> bool:
        """Update service status."""
        pass


class SOAAPIClientProtocol(ABC):
    """SOA API client protocol interface."""
    
    @abstractmethod
    async def create_request(self, service_name: str, endpoint: str,
                           request_data: Dict[str, Any], source_realm: str,
                           correlation_id: Optional[str] = None,
                           tenant_id: Optional[str] = None) -> SOAAPIRequest:
        """Create SOA API request."""
        pass
    
    @abstractmethod
    async def send_request(self, request: SOAAPIRequest) -> Optional[SOAAPIResponse]:
        """Send SOA API request."""
        pass
    
    @abstractmethod
    async def get_request_status(self, request_id: str) -> Optional[str]:
        """Get request status."""
        pass
    
    @abstractmethod
    async def cancel_request(self, request_id: str) -> bool:
        """Cancel SOA API request."""
        pass
    
    @abstractmethod
    async def get_request_history(self, source_realm: str, limit: int = 100) -> List[SOAAPIRequest]:
        """Get request history for source realm."""
        pass


class SOAAPIRegistryProtocol(ABC):
    """SOA API registry protocol interface."""
    
    @abstractmethod
    async def register_endpoint(self, service_name: str, realm: str, 
                              endpoint: SOAAPIEndpoint) -> bool:
        """Register API endpoint."""
        pass
    
    @abstractmethod
    async def unregister_endpoint(self, service_name: str, realm: str, 
                                endpoint_name: str) -> bool:
        """Unregister API endpoint."""
        pass
    
    @abstractmethod
    async def discover_endpoint(self, service_name: str, realm: str, 
                               endpoint_name: str) -> Optional[SOAAPIEndpoint]:
        """Discover API endpoint."""
        pass
    
    @abstractmethod
    async def list_endpoints(self, service_name: str, realm: str) -> List[SOAAPIEndpoint]:
        """List all endpoints for service."""
        pass
    
    @abstractmethod
    async def update_endpoint(self, service_name: str, realm: str, 
                            endpoint_name: str, endpoint: SOAAPIEndpoint) -> bool:
        """Update API endpoint."""
        pass


class SOAAPIGatewayProtocol(ABC):
    """SOA API gateway protocol interface."""
    
    @abstractmethod
    async def route_request(self, request: SOAAPIRequest) -> Optional[SOAAPIResponse]:
        """Route SOA API request to appropriate service."""
        pass
    
    @abstractmethod
    async def load_balance(self, service_name: str, realm: str) -> Optional[str]:
        """Load balance requests across service instances."""
        pass
    
    @abstractmethod
    async def rate_limit(self, service_name: str, realm: str, 
                        client_id: str) -> bool:
        """Check rate limit for service."""
        pass
    
    @abstractmethod
    async def authenticate_request(self, request: SOAAPIRequest) -> bool:
        """Authenticate SOA API request."""
        pass
    
    @abstractmethod
    async def authorize_request(self, request: SOAAPIRequest) -> bool:
        """Authorize SOA API request."""
        pass
    
    @abstractmethod
    async def get_gateway_stats(self) -> Dict[str, Any]:
        """Get gateway statistics."""
        pass
