#!/usr/bin/env python3
"""
Agent Base - AI/ML Components

AgentBase inherits from GroundZeroBase and provides specific functionality
for AI/ML agents in the platform.

WHAT (Agent Role): I provide base functionality for AI/ML agents
HOW (Agent Implementation): I inherit from GroundZeroBase with agent-specific capabilities
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

from backend.bases.ground_zero_base import GroundZeroBase


class AgentBase(GroundZeroBase):
    """
    AgentBase - Base Class for AI/ML Agents
    
    Inherits from GroundZeroBase and provides agent-specific functionality
    for AI/ML agents in the platform.
    
    WHAT (Agent Role): I provide base functionality for AI/ML agents
    HOW (Agent Implementation): I inherit from GroundZeroBase with agent-specific capabilities
    """
    
    def __init__(self, agent_name: str, di_container,
                 security_provider=None, authorization_guard=None):
        """Initialize AgentBase with GroundZeroBase foundation."""
        super().__init__(
            service_name=agent_name,
            di_container=di_container,
            security_provider=security_provider,
            authorization_guard=authorization_guard
        )
        
        # Agent-specific properties
        self.agent_type = "ai_ml"
        self.agent_capabilities = []
        self.agent_tools = []
        
        self.logger.info(f"🤖 AgentBase '{agent_name}' initialized with GroundZeroBase foundation")
    
    # ============================================================================
    # AGENT-SPECIFIC CAPABILITIES
    # ============================================================================
    
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities."""
        return {
            "agent_name": self.service_name,
            "agent_type": self.agent_type,
            "capabilities": self.agent_capabilities,
            "tools": self.agent_tools,
            "security_enabled": self.security_provider is not None,
            "authorization_enabled": self.authorization_guard is not None,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Get agent health status."""
        try:
            # Use GroundZeroBase health infrastructure
            base_health = await super().get_service_health()
            
            # Add agent-specific health
            agent_health = {
                "agent_type": self.agent_type,
                "capabilities_count": len(self.agent_capabilities),
                "tools_count": len(self.agent_tools),
                "status": "healthy"
            }
            
            return {**base_health, **agent_health}
            
        except Exception as e:
            return {
                "agent_name": self.service_name,
                "agent_type": self.agent_type,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # ABSTRACT METHODS (to be implemented by concrete agents)
    # ============================================================================
    
    @abstractmethod
    async def initialize(self):
        """Initialize the agent."""
        pass
    
    @abstractmethod
    async def shutdown(self):
        """Shutdown the agent."""
        pass
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an agent request."""
        pass




