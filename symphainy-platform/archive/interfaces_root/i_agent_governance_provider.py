"""
IAgentGovernanceProvider Interface
Interface for agent governance
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class IAgentGovernanceProvider(ABC):
    """Interface for agent governance."""
    
    @abstractmethod
    async def govern_agents(self, governance_context: Dict[str, Any]) -> Dict[str, Any]:
        """Govern agents across the platform."""
        pass
    
    @abstractmethod
    async def get_agent_governance_status(self) -> Dict[str, Any]:
        """Get agent governance status."""
        pass
    
    @abstractmethod
    async def coordinate_agent_deployment(self, agent_context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate agent deployment."""
        pass
    
    @abstractmethod
    async def get_agent_deployment_status(self, agent_id: str) -> Dict[str, Any]:
        """Get agent deployment status."""
        pass
    
    @abstractmethod
    async def monitor_agent_performance(self, agent_id: str) -> Dict[str, Any]:
        """Monitor agent performance."""
        pass
    
    @abstractmethod
    async def get_agent_performance_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Get agent performance metrics."""
        pass
    
    @abstractmethod
    async def enforce_agent_policy(self, agent_id: str, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce agent policy."""
        pass




