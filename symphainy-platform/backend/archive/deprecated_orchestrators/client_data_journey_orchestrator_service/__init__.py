"""
Client Data Journey Orchestrator Service

Orchestrates client data journey: Ingest → Parse → Embed → Expose
Composes FrontendGatewayService → routes to ContentOrchestrator
"""

from .client_data_journey_orchestrator_service import ClientDataJourneyOrchestratorService

__all__ = ["ClientDataJourneyOrchestratorService"]


