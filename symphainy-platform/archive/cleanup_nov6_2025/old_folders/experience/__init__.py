#!/usr/bin/env python3
"""
Experience Dimension

Experience Dimension following Smart City architectural patterns with proper role structure.

WHAT (Experience Dimension): I manage user experience, frontend integration, and journey management
HOW (Smart City Role): I use interfaces, protocols, and roles for experience management
"""

# Import role services
from .roles.frontend_integration.frontend_integration_service import FrontendIntegrationService, create_frontend_integration_service

# Note: Other services will be imported when they are refactored
# from .roles.experience_manager.experience_manager_service import ExperienceManagerService
# from .roles.journey_manager.journey_manager_service import JourneyManagerService

__all__ = [
    # Services
    "FrontendIntegrationService",
    "create_frontend_integration_service",
    
    # Note: Other services will be added when refactored
    # "ExperienceManagerService",
    # "JourneyManagerService"
]