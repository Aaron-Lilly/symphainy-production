#!/usr/bin/env python3
"""
Experience Agent Protocol

Defines the standard protocol for Experience Dimension agents.

WHAT (Agent Protocol): I define the standard structure for Experience agents
HOW (Protocol): I follow agent patterns with capabilities, communication, and autonomy
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from bases.foundation_service_base import FoundationServiceBase
from utilities import UserContext


class ExperienceAgentType(Enum):
    """Defines types of Experience agents."""
    EXPERIENCE_ORCHESTRATOR = "experience_orchestrator"
    JOURNEY_COORDINATOR = "journey_coordinator"
    FRONTEND_LIAISON = "frontend_liaison"
    REAL_TIME_MANAGER = "real_time_manager"
    
    def __str__(self):
        return self.value


class ExperienceCapability(Enum):
    """Defines capabilities of Experience agents."""
    SESSION_ORCHESTRATION = "session_orchestration"
    UI_STATE_MANAGEMENT = "ui_state_management"
    REAL_TIME_COORDINATION = "real_time_coordination"
    JOURNEY_NAVIGATION = "journey_navigation"
    FRONTEND_COMMUNICATION = "frontend_communication"
    CROSS_PILLAR_COORDINATION = "cross_pillar_coordination"
    
    def __str__(self):
        return self.value


class ExperienceAgentProtocol(ABC):
    """
    Experience Agent Protocol
    
    Abstract base class that defines the standard protocol for Experience agents.
    """
    
    def __init__(self, agent_name: str, agent_type: ExperienceAgentType, 
                 capabilities: List[ExperienceCapability], 
                 utility_foundation=None, curator_foundation=None):
        """Initialize experience agent protocol."""
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.utility_foundation = utility_foundation
        self.curator_foundation = curator_foundation
        self.is_initialized = False
        
    @abstractmethod
    async def initialize(self, user_context: UserContext = None):
        """Initialize the experience agent."""
        pass
    
    @abstractmethod
    async def execute_capability(self, capability: ExperienceCapability, 
                                capability_data: Dict[str, Any], 
                                user_context: UserContext) -> Dict[str, Any]:
        """Execute a specific capability."""
        pass
    
    @abstractmethod
    async def communicate_with_other_agents(self, target_agent: str, 
                                           message_data: Dict[str, Any], 
                                           user_context: UserContext) -> Dict[str, Any]:
        """Communicate with other agents."""
        pass
    
    @abstractmethod
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this agent."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the agent."""
        pass


class ExperienceAgentBase(FoundationServiceBase):
    """
    Experience Agent Base Class
    
    Base class for Experience agents, providing common functionality
    and integration with foundation services.
    """
    
    def __init__(self, agent_name: str, agent_type: ExperienceAgentType, 
                 capabilities: List[ExperienceCapability], 
                 utility_foundation=None, curator_foundation=None):
        """Initialize experience agent base."""
        super().__init__(agent_name, utility_foundation)
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.curator_foundation = curator_foundation
        self.is_initialized = False
        
        # Agent state
        self.current_capabilities = []
        self.communication_channels = {}
        
    async def initialize(self):
        """Initialize the experience agent."""
        await super().initialize()
        
        # Initialize agent-specific components
        await self._initialize_agent_components()
        
        self.is_initialized = True
        self.logger.info(f"✅ {self.agent_name} initialized successfully")
        
    async def shutdown(self):
        """Shutdown the experience agent."""
        self.logger.info(f"🛑 Shutting down {self.agent_name}...")
        await self._shutdown_agent_components()
        self.is_initialized = False
        self.logger.info(f"✅ {self.agent_name} shutdown successfully")
        
    async def _initialize_agent_components(self):
        """Initialize agent-specific components."""
        # Override in subclasses
        pass
        
    async def _shutdown_agent_components(self):
        """Shutdown agent-specific components."""
        # Override in subclasses
        pass
        
    async def execute_capability(self, capability: ExperienceCapability, 
                                capability_data: Dict[str, Any], 
                                user_context: UserContext) -> Dict[str, Any]:
        """Execute a specific capability."""
        try:
            if capability not in self.capabilities:
                return {"success": False, "error": f"Capability '{capability.value}' not supported"}
            
            # Execute the capability
            result = await self._execute_capability_implementation(capability, capability_data, user_context)
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Capability execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_capability_implementation(self, capability: ExperienceCapability, 
                                                capability_data: Dict[str, Any], 
                                                user_context: UserContext) -> Dict[str, Any]:
        """Execute the implementation of a specific capability."""
        # Override in subclasses
        return {"success": True, "message": "Capability executed successfully"}
    
    async def communicate_with_other_agents(self, target_agent: str, 
                                           message_data: Dict[str, Any], 
                                           user_context: UserContext) -> Dict[str, Any]:
        """Communicate with other agents."""
        try:
            # This would typically involve using the Curator Foundation Service
            # to find and communicate with other agents
            self.logger.info(f"Communicating with {target_agent}")
            
            # Placeholder for actual communication logic
            return {
                "success": True,
                "target_agent": target_agent,
                "message_sent": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Agent communication failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this agent."""
        return {
            "agent_name": self.agent_name,
            "agent_type": self.agent_type.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "is_initialized": self.is_initialized,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the experience agent."""
        return {
            "agent_name": self.agent_name,
            "agent_type": self.agent_type.value,
            "status": "healthy" if self.is_initialized else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "capabilities": await self.get_agent_capabilities()
        }
