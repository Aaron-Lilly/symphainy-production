#!/usr/bin/env python3
"""
Agent WebSocket SDK

Provides WebSocket connection management for agents using Communication Foundation infrastructure.
This SDK enables agents to use WebSocket for real-time communication while maintaining
proper session management and realm-aware routing.

WHAT (Agent WebSocket SDK Role): I provide WebSocket connection management for agents
HOW (Agent WebSocket SDK Implementation): I use Communication Foundation WebSocket infrastructure
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


class AgentWebSocketSDK:
    """
    Agent WebSocket SDK - WebSocket connection management for agents.
    
    Provides standardized WebSocket connection management for agents using
    Communication Foundation infrastructure. Supports both Guide and Liaison agents
    with pillar-specific routing for Liaison agents.
    
    Architecture:
    - Uses Communication Foundation WebSocket infrastructure
    - Supports agent-specific routing (Guide vs Liaison)
    - Handles session management integration
    - Supports pillar-specific routing for liaison agents (all in same realm, but different instances)
    """
    
    def __init__(self, websocket_foundation: Any, di_container: Any):
        """
        Initialize Agent WebSocket SDK.
        
        Args:
            websocket_foundation: Communication Foundation WebSocket infrastructure
            di_container: DI Container for accessing other services
        """
        self.websocket_foundation = websocket_foundation
        self.di_container = di_container
        self.logger = logging.getLogger(f"{__name__}.AgentWebSocketSDK")
        
        # Connection tracking
        self.connections: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("✅ Agent WebSocket SDK initialized")
    
    async def connect_guide_agent(self, session_token: str) -> str:
        """
        Connect Guide Agent WebSocket.
        
        Args:
            session_token: User session token
        
        Returns:
            connection_id: Unique connection identifier
        """
        try:
            connection_id = str(uuid.uuid4())
            
            # Register connection with Communication Foundation
            if self.websocket_foundation:
                await self.websocket_foundation.register_connection(
                    connection_id=connection_id,
                    realm="journey_solution",  # Guide Agent is in journey_solution realm
                    agent_type="guide",
                    session_token=session_token
                )
            
            # Track connection
            self.connections[connection_id] = {
                "connection_id": connection_id,
                "agent_type": "guide",
                "realm": "journey_solution",
                "session_token": session_token,
                "pillar": None,
                "connected_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"✅ Guide Agent WebSocket connected: {connection_id}")
            return connection_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to connect Guide Agent WebSocket: {e}")
            raise
    
    async def connect_liaison_agent(self, pillar: str, session_token: str) -> str:
        """
        Connect Liaison Agent WebSocket.
        
        Args:
            pillar: Frontend pillar name (content, insights, operations, business_outcomes)
            session_token: User session token
        
        Returns:
            connection_id: Unique connection identifier
        
        Note: All liaison agents are in business_enablement realm, but each
        pillar has its own liaison agent instance. The SDK routes to the
        correct agent based on pillar name.
        """
        try:
            connection_id = str(uuid.uuid4())
            
            # Map pillar to agent name for Communication Foundation
            pillar_to_agent = {
                "content": "ContentLiaisonAgent",
                "insights": "InsightsLiaisonAgent",
                "operations": "OperationsLiaisonAgent",
                "business_outcomes": "BusinessOutcomesLiaisonAgent"
            }
            agent_name = pillar_to_agent.get(pillar, f"{pillar}_liaison")
            
            # Register connection with Communication Foundation
            if self.websocket_foundation:
                await self.websocket_foundation.register_connection(
                    connection_id=connection_id,
                    realm="business_enablement",  # All liaison agents are in business_enablement realm
                    agent_type="liaison",
                    agent_name=agent_name,
                    session_token=session_token
                )
            
            # Track connection
            self.connections[connection_id] = {
                "connection_id": connection_id,
                "agent_type": "liaison",
                "realm": "business_enablement",
                "session_token": session_token,
                "pillar": pillar,
                "agent_name": agent_name,
                "connected_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"✅ Liaison Agent WebSocket connected: {connection_id} (pillar: {pillar})")
            return connection_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to connect Liaison Agent WebSocket (pillar: {pillar}): {e}")
            raise
    
    async def send_agent_message(self, connection_id: str, message: Dict[str, Any]) -> None:
        """
        Send message via WebSocket.
        
        Args:
            connection_id: WebSocket connection ID
            message: Message to send
        """
        try:
            if connection_id not in self.connections:
                raise ValueError(f"Connection {connection_id} not found")
            
            connection = self.connections[connection_id]
            
            # Send via Communication Foundation
            if self.websocket_foundation:
                await self.websocket_foundation.send_message(
                    connection_id=connection_id,
                    message=message
                )
            
            self.logger.debug(f"✅ Message sent via connection {connection_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send message via connection {connection_id}: {e}")
            raise
    
    async def receive_agent_message(self, connection_id: str) -> Dict[str, Any]:
        """
        Receive message via WebSocket.
        
        Args:
            connection_id: WebSocket connection ID
        
        Returns:
            Message received
        """
        try:
            if connection_id not in self.connections:
                raise ValueError(f"Connection {connection_id} not found")
            
            # Receive via Communication Foundation
            if self.websocket_foundation:
                message = await self.websocket_foundation.receive_message(connection_id)
                return message
            
            return {}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to receive message via connection {connection_id}: {e}")
            raise
    
    async def disconnect_agent(self, connection_id: str) -> None:
        """
        Disconnect WebSocket.
        
        Args:
            connection_id: WebSocket connection ID
        """
        try:
            if connection_id not in self.connections:
                self.logger.warning(f"⚠️ Connection {connection_id} not found for disconnect")
                return
            
            connection = self.connections[connection_id]
            
            # Disconnect via Communication Foundation
            if self.websocket_foundation:
                await self.websocket_foundation.disconnect_connection(connection_id)
            
            # Remove from tracking
            del self.connections[connection_id]
            
            self.logger.info(f"✅ Agent WebSocket disconnected: {connection_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to disconnect connection {connection_id}: {e}")
            raise
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection information."""
        return self.connections.get(connection_id)
    
    def list_connections(self, agent_type: Optional[str] = None, pillar: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all connections, optionally filtered by agent_type or pillar."""
        connections = list(self.connections.values())
        
        if agent_type:
            connections = [c for c in connections if c.get("agent_type") == agent_type]
        
        if pillar:
            connections = [c for c in connections if c.get("pillar") == pillar]
        
        return connections

