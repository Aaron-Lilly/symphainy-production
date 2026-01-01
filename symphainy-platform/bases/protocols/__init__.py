#!/usr/bin/env python3
"""
Base Class Protocols

Clean protocol definitions for base classes - contracts only, no implementations.
Aligned with new architecture (Platform Gateway, Curator, Communication patterns).

WHAT (Protocol Role): I define contracts for all base classes
HOW (Protocol Implementation): I provide type-safe contracts with clear responsibilities
"""

from .foundation_service_protocol import FoundationServiceProtocol
from .platform_gateway_protocol import PlatformGatewayProtocol, RealmCapability
from .realm_service_protocol import RealmServiceProtocol
from .smart_city_role_protocol import SmartCityRoleProtocol
from .manager_service_protocol import ManagerServiceProtocol
from .orchestrator_protocol import OrchestratorProtocol
from .service_protocol import ServiceProtocol
from .solution_manager_service_protocol import SolutionManagerServiceProtocol
from .journey_manager_service_protocol import JourneyManagerServiceProtocol

__all__ = [
    # Base Protocols
    "ServiceProtocol",
    
    # Base Class Protocols
    "FoundationServiceProtocol",
    "PlatformGatewayProtocol", 
    "RealmServiceProtocol",
    "SmartCityRoleProtocol",
    "ManagerServiceProtocol",
    "OrchestratorProtocol",
    
    # Manager Protocols
    "SolutionManagerServiceProtocol",
    "JourneyManagerServiceProtocol",
    
    # Data Classes
    "RealmCapability",
]