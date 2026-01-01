#!/usr/bin/env python3
"""
Journey Solution Interfaces Package

Contains interface definitions for Journey Solution services.
"""

from .journey_manager_interface import IJourneyManager, JourneyServiceType, JourneyAgentType
from .journey_orchestrator_interface import IJourneyOrchestrator, JourneyDimension, JourneyStatus
from .business_outcome_analyzer_interface import IBusinessOutcomeAnalyzer, BusinessOutcomeType, CapabilityType
from .solution_architect_interface import ISolutionArchitect, SolutionType, ArchitecturePattern

__all__ = [
    # Journey Manager Interface
    "IJourneyManager",
    "JourneyServiceType", 
    "JourneyAgentType",
    
    # Journey Orchestrator Interface
    "IJourneyOrchestrator",
    "JourneyDimension",
    "JourneyStatus",
    
    # Business Outcome Analyzer Interface
    "IBusinessOutcomeAnalyzer",
    "BusinessOutcomeType",
    "CapabilityType",
    
    # Solution Architect Interface
    "ISolutionArchitect",
    "SolutionType",
    "ArchitecturePattern"
]





