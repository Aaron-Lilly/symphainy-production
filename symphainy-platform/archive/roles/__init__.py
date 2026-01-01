"""
Journey/Solution Dimension Roles

Roles for the Journey/Solution dimension that handle specific journey flows
and intelligent routing for different use cases.
"""

from .mvp_journey_manager.mvp_journey_manager_service import MVPJourneyManagerService, create_mvp_journey_manager_service

__all__ = [
    'MVPJourneyManagerService',
    'create_mvp_journey_manager_service'
]
