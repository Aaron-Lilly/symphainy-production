"""
Journey/Solution Dimension - The Front Door to the Agentic IDP

This dimension serves as the "front door" to the agentic IDP, orchestrating business outcome
journeys across all platform dimensions and giving purpose to the dormant cross-dimensional managers.

WHAT (Journey/Solution Role): I orchestrate business outcome journeys across all dimensions
HOW (Service Implementation): I coordinate City Manager, Delivery Manager, and Experience Manager
"""

from .services.journey_orchestrator_service import JourneyOrchestratorService, create_journey_orchestrator_service
from .services.business_outcome_analyzer_service import BusinessOutcomeAnalyzerService, create_business_outcome_analyzer_service
from .services.solution_architect_service import SolutionArchitectService, create_solution_architect_service
from .services.business_outcome_landing_page_service import BusinessOutcomeLandingPageService, create_business_outcome_landing_page_service

__all__ = [
    'JourneyOrchestratorService',
    'create_journey_orchestrator_service',
    'BusinessOutcomeAnalyzerService', 
    'create_business_outcome_analyzer_service',
    'SolutionArchitectService',
    'create_solution_architect_service',
    'BusinessOutcomeLandingPageService',
    'create_business_outcome_landing_page_service'
]
