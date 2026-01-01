#!/usr/bin/env python3
"""
Communication Protocol - Unified Communication Interface

Defines the unified communication interface for all realms to use
for inter-realm communication via Communication Foundation.

WHAT (Abstraction Contract): I define the unified communication interface
HOW (Protocol Definition): I specify the contract for all communication operations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum


class CommunicationType(Enum):
    """Communication type enumeration."""
    API_REQUEST = "api_request"
    API_RESPONSE = "api_response"
    MESSAGE = "message"
    EVENT = "event"
    WEBSOCKET = "websocket"
    SOA_API = "soa_api"


class CommunicationPriority(Enum):
    """Communication priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class CommunicationStatus(Enum):
    """Communication status enumeration."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    TIMEOUT = "timeout"


class CommunicationContext:
    """Communication context for tracking communication operations."""
    
    def __init__(self, communication_id: str, communication_type: CommunicationType,
                 source_realm: str, target_realm: str, content: Dict[str, Any],
                 priority: CommunicationPriority = CommunicationPriority.NORMAL,
                 correlation_id: Optional[str] = None, tenant_id: Optional[str] = None):
        """Initialize communication context."""
        self.communication_id = communication_id
        self.communication_type = communication_type
        self.source_realm = source_realm
        self.target_realm = target_realm
        self.content = content
        self.priority = priority
        self.correlation_id = correlation_id
        self.tenant_id = tenant_id
        self.status = CommunicationStatus.PENDING
        self.timestamp = datetime.now()
        self.retry_count = 0
        self.error_message = None


class CommunicationProtocol(ABC):
    """Communication protocol interface for unified communication."""
    
    @abstractmethod
    async def send_api_request(self, target_realm: str, endpoint: str, 
                             request_data: Dict[str, Any], 
                             priority: CommunicationPriority = CommunicationPriority.NORMAL,
                             correlation_id: Optional[str] = None, 
                             tenant_id: Optional[str] = None) -> Optional[CommunicationContext]:
        """Send API request to target realm."""
        pass
    
    @abstractmethod
    async def send_api_response(self, target_realm: str, request_id: str,
                               response_data: Dict[str, Any],
                               status_code: int = 200,
                               correlation_id: Optional[str] = None,
                               tenant_id: Optional[str] = None) -> Optional[CommunicationContext]:
        """Send API response to target realm."""
        pass
    
    @abstractmethod
    async def send_message(self, target_realm: str, message_type: str,
                          message_data: Dict[str, Any],
                          priority: CommunicationPriority = CommunicationPriority.NORMAL,
                          correlation_id: Optional[str] = None,
                          tenant_id: Optional[str] = None) -> Optional[CommunicationContext]:
        """Send message to target realm."""
        pass
    
    @abstractmethod
    async def publish_event(self, event_type: str, event_data: Dict[str, Any],
                           source_realm: str = "system",
                           priority: CommunicationPriority = CommunicationPriority.NORMAL,
                           correlation_id: Optional[str] = None,
                           tenant_id: Optional[str] = None) -> Optional[CommunicationContext]:
        """Publish event to event bus."""
        pass
    
    @abstractmethod
    async def establish_websocket_connection(self, target_realm: str, client_id: str,
                                           connection_data: Dict[str, Any],
                                           correlation_id: Optional[str] = None,
                                           tenant_id: Optional[str] = None) -> Optional[CommunicationContext]:
        """Establish WebSocket connection to target realm."""
        pass
    
    @abstractmethod
    async def send_soa_api_request(self, target_realm: str, service_name: str,
                                  endpoint: str, request_data: Dict[str, Any],
                                  priority: CommunicationPriority = CommunicationPriority.NORMAL,
                                  correlation_id: Optional[str] = None,
                                  tenant_id: Optional[str] = None) -> Optional[CommunicationContext]:
        """Send SOA API request to target realm."""
        pass
    
    @abstractmethod
    async def receive_communication(self, realm: str, communication_id: str) -> Optional[CommunicationContext]:
        """Receive communication for realm."""
        pass
    
    @abstractmethod
    async def get_communication_status(self, communication_id: str) -> Optional[CommunicationStatus]:
        """Get communication status."""
        pass
    
    @abstractmethod
    async def subscribe_to_events(self, realm: str, event_type: str, handler: Callable):
        """Subscribe to events for realm."""
        pass
    
    @abstractmethod
    async def unsubscribe_from_events(self, realm: str, event_type: str, handler: Callable):
        """Unsubscribe from events for realm."""
        pass
    
    @abstractmethod
    async def get_communication_history(self, realm: str, limit: int = 100) -> List[CommunicationContext]:
        """Get communication history for realm."""
        pass
    
    @abstractmethod
    async def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics."""
        pass


class SOAAPIProtocol(ABC):
    """SOA API protocol interface for service-oriented architecture."""
    
    @abstractmethod
    async def register_soa_api(self, realm: str, service_name: str, 
                             endpoints: Dict[str, str], base_url: str,
                             version: str = "1.0.0") -> bool:
        """Register SOA API endpoints for realm."""
        pass
    
    @abstractmethod
    async def discover_soa_api(self, realm: str, service_name: str) -> Optional[Dict[str, Any]]:
        """Discover SOA API endpoints for realm."""
        pass
    
    @abstractmethod
    async def get_soa_api_endpoints(self, realm: str) -> Dict[str, Any]:
        """Get all SOA API endpoints for realm."""
        pass
    
    @abstractmethod
    async def call_soa_api(self, realm: str, service_name: str, endpoint: str,
                          request_data: Dict[str, Any],
                          correlation_id: Optional[str] = None,
                          tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Call SOA API endpoint."""
        pass
    
    @abstractmethod
    async def get_soa_api_health(self, realm: str, service_name: str) -> Dict[str, Any]:
        """Get SOA API health status."""
        pass


class WebSocketProtocol(ABC):
    """WebSocket protocol interface for real-time communication."""
    
    @abstractmethod
    async def connect_websocket(self, realm: str, client_id: str,
                               connection_data: Dict[str, Any]) -> bool:
        """Connect WebSocket to realm."""
        pass
    
    @abstractmethod
    async def disconnect_websocket(self, realm: str, client_id: str) -> bool:
        """Disconnect WebSocket from realm."""
        pass
    
    @abstractmethod
    async def send_websocket_message(self, realm: str, client_id: str,
                                    message: Dict[str, Any]) -> bool:
        """Send WebSocket message to client."""
        pass
    
    @abstractmethod
    async def broadcast_to_realm(self, realm: str, message: Dict[str, Any]) -> int:
        """Broadcast message to all clients in realm."""
        pass
    
    @abstractmethod
    async def get_websocket_connections(self, realm: str) -> List[str]:
        """Get WebSocket connections for realm."""
        pass
    
    @abstractmethod
    async def get_websocket_stats(self) -> Dict[str, Any]:
        """Get WebSocket statistics."""
        pass


class MessagingProtocol(ABC):
    """Messaging protocol interface for asynchronous communication."""
    
    @abstractmethod
    async def send_message(self, target_realm: str, message_type: str,
                          message_data: Dict[str, Any],
                          priority: CommunicationPriority = CommunicationPriority.NORMAL) -> Optional[str]:
        """Send message to target realm."""
        pass
    
    @abstractmethod
    async def receive_message(self, realm: str, message_id: str) -> Optional[Dict[str, Any]]:
        """Receive message for realm."""
        pass
    
    @abstractmethod
    async def get_message_queue(self, realm: str) -> List[Dict[str, Any]]:
        """Get message queue for realm."""
        pass
    
    @abstractmethod
    async def clear_message_queue(self, realm: str) -> bool:
        """Clear message queue for realm."""
        pass
    
    @abstractmethod
    async def get_messaging_stats(self) -> Dict[str, Any]:
        """Get messaging statistics."""
        pass


class EventBusProtocol(ABC):
    """Event bus protocol interface for event-driven communication."""
    
    @abstractmethod
    async def publish_event(self, event_type: str, event_data: Dict[str, Any],
                           source_realm: str = "system") -> Optional[str]:
        """Publish event to event bus."""
        pass
    
    @abstractmethod
    async def subscribe_to_event(self, realm: str, event_type: str, handler: Callable) -> bool:
        """Subscribe to event type for realm."""
        pass
    
    @abstractmethod
    async def unsubscribe_from_event(self, realm: str, event_type: str, handler: Callable) -> bool:
        """Unsubscribe from event type for realm."""
        pass
    
    @abstractmethod
    async def get_event_subscribers(self, event_type: str) -> List[str]:
        """Get event subscribers for event type."""
        pass
    
    @abstractmethod
    async def get_event_bus_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        pass
