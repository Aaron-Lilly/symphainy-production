"""
Data Solution Orchestrator Service Package

WHAT: Orchestrates the complete data solution flow: Ingest → Parse → Embed → Expose
HOW: Direct SOA API calls to Smart City services, delegates to enabling services
"""

from .data_solution_orchestrator_service import DataSolutionOrchestratorService

__all__ = ["DataSolutionOrchestratorService"]



