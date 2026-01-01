"""
Manager Service Interfaces
Interfaces for domain manager services
"""

from .i_realm_startup_orchestrator import IRealmStartupOrchestrator
from .i_dependency_manager import IDependencyManager
from .i_cross_dimensional_cicd_coordinator import ICrossDimensionalCICDCoordinator
from .i_journey_orchestrator import IJourneyOrchestrator
from .i_agent_governance_provider import IAgentGovernanceProvider
from .i_manager_service import IManagerService

__all__ = [
    "IRealmStartupOrchestrator",
    "IDependencyManager", 
    "ICrossDimensionalCICDCoordinator",
    "IJourneyOrchestrator",
    "IAgentGovernanceProvider",
    "IManagerService"
]




