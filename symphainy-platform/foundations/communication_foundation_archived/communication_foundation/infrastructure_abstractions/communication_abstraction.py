#!/usr/bin/env python3
"""
Communication Abstraction - Unified Communication Implementation

Unified communication abstraction that provides a single interface
for all communication types (API, messaging, events, WebSocket).

WHAT (Infrastructure Abstraction): I provide unified communication interface
HOW (Infrastructure Implementation): I orchestrate all communication adapters
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import uuid

# Import abstraction contracts
from ..abstraction_contracts.communication_protocol import (
    CommunicationProtocol, CommunicationContext, CommunicationType, 
    CommunicationPriority, CommunicationStatus
)

# Import foundation services (replacing old adapters)
from ..foundation_services.websocket_foundation_service import WebSocketFoundationService
from ..foundation_services.messaging_foundation_service import MessagingFoundationService
from ..foundation_services.event_bus_foundation_service import EventBusFoundationService

logger = logging.getLogger(__name__)


class CommunicationAbstraction(CommunicationProtocol):
    """
    Communication Abstraction - Unified Communication Implementation
    
    Provides unified communication interface that orchestrates all communication
    adapters to provide a single interface for all communication types.
    
    WHAT (Infrastructure Abstraction): I provide unified communication interface
    HOW (Infrastructure Implementation): I orchestrate all communication adapters
    """
    
    def __init__(self, api_gateway_adapter: Optional[Any] = None,  # Removed - using FastAPIRouterManager instead
                 websocket_foundation: Optional[WebSocketFoundationService] = None,
                 messaging_foundation: Optional[MessagingFoundationService] = None,
                 event_bus_foundation: Optional[EventBusFoundationService] = None):
        """Initialize Communication Abstraction."""
        self.logger = logging.getLogger("CommunicationAbstraction")
        
        # Infrastructure foundation services (api_gateway_adapter is None - we use FastAPIRouterManager now)
        self.api_gateway_adapter = api_gateway_adapter
        self.websocket_foundation = websocket_foundation
        self.messaging_foundation = messaging_foundation
        self.event_bus_foundation = event_bus_foundation
        
        # Backward compatibility aliases (for methods that still reference adapters)
        self.websocket_adapter = websocket_foundation
        self.messaging_adapter = messaging_foundation
        self.event_bus_adapter = event_bus_foundation
        
        # Communication tracking
        self.communication_contexts = {}
        self.communication_history = []
        
        # Service state
        self.is_initialized = False
        self.is_running = False
        
        self.logger.info("🏗️ Communication Abstraction initialized")
    
    async def initialize(self):
        """Initialize Communication Abstraction."""
        self.logger.info("🚀 Initializing Communication Abstraction...")
        
        try:
            # Initialize all adapters (if available)
            if self.api_gateway_adapter:
                await self.api_gateway_adapter.initialize()
            else:
                self.logger.warning("⚠️ API Gateway adapter not available")
            
            if self.websocket_foundation:
                if not self.websocket_foundation.is_initialized:
                    await self.websocket_foundation.initialize()
            else:
                self.logger.warning("⚠️ WebSocket foundation service not available")
            
            if self.messaging_foundation:
                if not self.messaging_foundation.is_initialized:
                    await self.messaging_foundation.initialize()
            else:
                self.logger.warning("⚠️ Messaging foundation service not available")
            
            if self.event_bus_foundation:
                if not self.event_bus_foundation.is_initialized:
                    await self.event_bus_foundation.initialize()
            else:
                self.logger.warning("⚠️ Event bus foundation service not available")
            
            self.is_initialized = True
            self.logger.info("✅ Communication Abstraction initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Communication Abstraction: {e}")
            raise
    
    async def start(self):
        """Start Communication Abstraction."""
        if not self.is_initialized:
            await self.initialize()
        
        self.logger.info("🚀 Starting Communication Abstraction...")
        
        try:
            # Start all adapters (if available)
            if self.api_gateway_adapter:
                await self.api_gateway_adapter.start()
            if self.websocket_adapter:
                await self.websocket_adapter.start()
            if self.messaging_adapter:
                await self.messaging_adapter.start()
            if self.event_bus_adapter:
                await self.event_bus_adapter.start()
            
            self.is_running = True
            self.logger.info("✅ Communication Abstraction started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start Communication Abstraction: {e}")
            raise
    
    async def stop(self):
        """Stop Communication Abstraction."""
        self.logger.info("🛑 Stopping Communication Abstraction...")
        
        try:
            # Stop all adapters (if available)
            if self.event_bus_adapter:
                await self.event_bus_adapter.stop()
            if self.messaging_adapter:
                await self.messaging_adapter.stop()
            if self.websocket_adapter:
                await self.websocket_adapter.stop()
            if self.api_gateway_adapter:
                await self.api_gateway_adapter.stop()
            
            self.is_running = False
            self.logger.info("✅ Communication Abstraction stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop Communication Abstraction: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown Communication Abstraction."""
        await self.stop()
        self.logger.info("🔌 Communication Abstraction shutdown complete")
    
    # Communication Protocol Implementation
    
    async def send_api_request(self, target_realm: str, endpoint: str, 
                             request_data: Dict[str, Any], 
                             priority: CommunicationPriority = CommunicationPriority.NORMAL,
                             correlation_id: Optional[str] = None, 
                             tenant_id: Optional[str] = None) -> Optional[CommunicationContext]:
        """Send API request to target realm."""
        try:
            communication_id = str(uuid.uuid4())
            
            # Create communication context
            context = CommunicationContext(
                communication_id=communication_id,
                communication_type=CommunicationType.API_REQUEST,
                source_realm="system",
                target_realm=target_realm,
                content={
                    "endpoint": endpoint,
                    "request_data": request_data
                },
                priority=priority,
                correlation_id=correlation_id,
                tenant_id=tenant_id
            )
            
            # Route request through API Gateway
            # API Gateway Adapter removed - routing handled by FastAPIRouterManager
            if not self.api_gateway_adapter:
                raise RuntimeError("API routing not available - use realm bridges via FastAPIRouterManager")
            response = await self.api_gateway_adapter.route_request(
                target_realm=target_realm,
                endpoint=endpoint,
                request_data=request_data
            )
            
            if response:
                context.status = CommunicationStatus.SENT
                self.communication_contexts[communication_id] = context
                self.communication_history.append(context)
                
                self.logger.info(f"✅ API request sent to {target_realm}: {endpoint}")
                return context
            else:
                context.status = CommunicationStatus.FAILED
                self.logger.error(f"❌ Failed to send API request to {target_realm}: {endpoint}")
                return context
                
        except Exception as e:
            self.logger.error(f"❌ Failed to send API request: {e}")
            return None
    
    async def send_api_response(self, target_realm: str, request_id: str,
                               response_data: Dict[str, Any],
                               status_code: int = 200,
                               correlation_id: Optional[str] = None,
                               tenant_id: Optional[str] = None) -> Optional[CommunicationContext]:
        """Send API response to target realm."""
        try:
            communication_id = str(uuid.uuid4())
            
            # Create communication context
            context = CommunicationContext(
                communication_id=communication_id,
                communication_type=CommunicationType.API_RESPONSE,
                source_realm="system",
                target_realm=target_realm,
                content={
                    "request_id": request_id,
                    "response_data": response_data,
                    "status_code": status_code
                },
                priority=CommunicationPriority.NORMAL,
                correlation_id=correlation_id,
                tenant_id=tenant_id
            )
            
            # Send response through API Gateway
            # API Gateway Adapter removed - routing handled by FastAPIRouterManager
            if not self.api_gateway_adapter:
                raise RuntimeError("API routing not available - use realm bridges via FastAPIRouterManager")
            success = await self.api_gateway_adapter.send_response(
                target_realm=target_realm,
                request_id=request_id,
                response_data=response_data,
                status_code=status_code
            )
            
            if success:
                context.status = CommunicationStatus.SENT
                self.communication_contexts[communication_id] = context
                self.communication_history.append(context)
                
                self.logger.info(f"✅ API response sent to {target_realm}: {request_id}")
                return context
            else:
                context.status = CommunicationStatus.FAILED
                self.logger.error(f"❌ Failed to send API response to {target_realm}: {request_id}")
                return context
                
        except Exception as e:
            self.logger.error(f"❌ Failed to send API response: {e}")
            return None
    
    async def send_message(self, target_realm: str, message_type: str,
                          message_data: Dict[str, Any],
                          priority: CommunicationPriority = CommunicationPriority.NORMAL,
                          correlation_id: Optional[str] = None,
                          tenant_id: Optional[str] = None) -> Optional[CommunicationContext]:
        """Send message to target realm."""
        try:
            communication_id = str(uuid.uuid4())
            
            # Create communication context
            context = CommunicationContext(
                communication_id=communication_id,
                communication_type=CommunicationType.MESSAGE,
                source_realm="system",
                target_realm=target_realm,
                content={
                    "message_type": message_type,
                    "message_data": message_data
                },
                priority=priority,
                correlation_id=correlation_id,
                tenant_id=tenant_id
            )
            
            # Send message through messaging adapter
            message_id = await self.messaging_adapter.send_message(
                target_realm=target_realm,
                message_type=message_type,
                message_data=message_data,
                sender="system",
                priority=priority.value
            )
            
            if message_id:
                context.status = CommunicationStatus.SENT
                self.communication_contexts[communication_id] = context
                self.communication_history.append(context)
                
                self.logger.info(f"✅ Message sent to {target_realm}: {message_type}")
                return context
            else:
                context.status = CommunicationStatus.FAILED
                self.logger.error(f"❌ Failed to send message to {target_realm}: {message_type}")
                return context
                
        except Exception as e:
            self.logger.error(f"❌ Failed to send message: {e}")
            return None
    
    async def publish_event(self, event_type: str, event_data: Dict[str, Any],
                           source_realm: str = "system",
                           priority: CommunicationPriority = CommunicationPriority.NORMAL,
                           correlation_id: Optional[str] = None,
                           tenant_id: Optional[str] = None) -> Optional[CommunicationContext]:
        """Publish event to event bus."""
        try:
            communication_id = str(uuid.uuid4())
            
            # Create communication context
            context = CommunicationContext(
                communication_id=communication_id,
                communication_type=CommunicationType.EVENT,
                source_realm=source_realm,
                target_realm="*",  # Broadcast to all
                content={
                    "event_type": event_type,
                    "event_data": event_data
                },
                priority=priority,
                correlation_id=correlation_id,
                tenant_id=tenant_id
            )
            
            # Publish event through event bus adapter
            event_id = await self.event_bus_adapter.publish_event(
                event_type=event_type,
                event_data=event_data,
                source_realm=source_realm,
                priority=priority.value
            )
            
            if event_id:
                context.status = CommunicationStatus.SENT
                self.communication_contexts[communication_id] = context
                self.communication_history.append(context)
                
                self.logger.info(f"✅ Event published: {event_type}")
                return context
            else:
                context.status = CommunicationStatus.FAILED
                self.logger.error(f"❌ Failed to publish event: {event_type}")
                return context
                
        except Exception as e:
            self.logger.error(f"❌ Failed to publish event: {e}")
            return None
    
    async def establish_websocket_connection(self, target_realm: str, client_id: str,
                                           connection_data: Dict[str, Any],
                                           correlation_id: Optional[str] = None,
                                           tenant_id: Optional[str] = None) -> Optional[CommunicationContext]:
        """Establish WebSocket connection to target realm."""
        try:
            communication_id = str(uuid.uuid4())
            
            # Create communication context
            context = CommunicationContext(
                communication_id=communication_id,
                communication_type=CommunicationType.WEBSOCKET,
                source_realm="system",
                target_realm=target_realm,
                content={
                    "client_id": client_id,
                    "connection_data": connection_data
                },
                priority=CommunicationPriority.NORMAL,
                correlation_id=correlation_id,
                tenant_id=tenant_id
            )
            
            # Establish WebSocket connection
            connection = await self.websocket_adapter.establish_connection(
                client_id=client_id,
                realm=target_realm
            )
            
            if connection:
                context.status = CommunicationStatus.SENT
                self.communication_contexts[communication_id] = context
                self.communication_history.append(context)
                
                self.logger.info(f"✅ WebSocket connection established: {client_id} -> {target_realm}")
                return context
            else:
                context.status = CommunicationStatus.FAILED
                self.logger.error(f"❌ Failed to establish WebSocket connection: {client_id} -> {target_realm}")
                return context
                
        except Exception as e:
            self.logger.error(f"❌ Failed to establish WebSocket connection: {e}")
            return None
    
    async def send_soa_api_request(self, target_realm: str, service_name: str,
                                  endpoint: str, request_data: Dict[str, Any],
                                  priority: CommunicationPriority = CommunicationPriority.NORMAL,
                                  correlation_id: Optional[str] = None,
                                  tenant_id: Optional[str] = None) -> Optional[CommunicationContext]:
        """Send SOA API request to target realm."""
        try:
            communication_id = str(uuid.uuid4())
            
            # Create communication context
            context = CommunicationContext(
                communication_id=communication_id,
                communication_type=CommunicationType.SOA_API,
                source_realm="system",
                target_realm=target_realm,
                content={
                    "service_name": service_name,
                    "endpoint": endpoint,
                    "request_data": request_data
                },
                priority=priority,
                correlation_id=correlation_id,
                tenant_id=tenant_id
            )
            
            # Route SOA API request through API Gateway
            # API Gateway Adapter removed - SOA routing handled by realm bridges
            if not self.api_gateway_adapter:
                raise RuntimeError("SOA routing not available - use realm bridges via FastAPIRouterManager")
            response = await self.api_gateway_adapter.route_soa_request(
                target_realm=target_realm,
                service_name=service_name,
                endpoint=endpoint,
                request_data=request_data
            )
            
            if response:
                context.status = CommunicationStatus.SENT
                self.communication_contexts[communication_id] = context
                self.communication_history.append(context)
                
                self.logger.info(f"✅ SOA API request sent to {target_realm}: {service_name}/{endpoint}")
                return context
            else:
                context.status = CommunicationStatus.FAILED
                self.logger.error(f"❌ Failed to send SOA API request to {target_realm}: {service_name}/{endpoint}")
                return context
                
        except Exception as e:
            self.logger.error(f"❌ Failed to send SOA API request: {e}")
            return None
    
    async def receive_communication(self, realm: str, communication_id: str) -> Optional[CommunicationContext]:
        """Receive communication for realm."""
        return self.communication_contexts.get(communication_id)
    
    async def get_communication_status(self, communication_id: str) -> Optional[CommunicationStatus]:
        """Get communication status."""
        context = self.communication_contexts.get(communication_id)
        return context.status if context else None
    
    async def subscribe_to_events(self, realm: str, event_type: str, handler: Callable):
        """Subscribe to events for realm."""
        await self.event_bus_adapter.subscribe_to_event(realm, event_type, handler)
    
    async def unsubscribe_from_events(self, realm: str, event_type: str, handler: Callable):
        """Unsubscribe from events for realm."""
        await self.event_bus_adapter.unsubscribe_from_event(realm, event_type, handler)
    
    async def get_communication_history(self, realm: str, limit: int = 100) -> List[CommunicationContext]:
        """Get communication history for realm."""
        realm_history = [
            context for context in self.communication_history
            if context.source_realm == realm or context.target_realm == realm
        ]
        return realm_history[-limit:] if limit > 0 else realm_history
    
    async def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics."""
        return {
            "total_communications": len(self.communication_contexts),
            "communication_history_count": len(self.communication_history),
            "is_running": self.is_running,
            "is_initialized": self.is_initialized,
            "adapter_stats": {
                "api_gateway": await self.api_gateway_adapter.get_stats() if hasattr(self.api_gateway_adapter, 'get_stats') else {},
                "websocket": await self.websocket_adapter.get_websocket_stats() if hasattr(self.websocket_adapter, 'get_websocket_stats') else {},
                "messaging": await self.messaging_adapter.get_messaging_stats() if hasattr(self.messaging_adapter, 'get_messaging_stats') else {},
                "event_bus": await self.event_bus_adapter.get_event_bus_stats() if hasattr(self.event_bus_adapter, 'get_event_bus_stats') else {}
            }
        }
