#!/usr/bin/env python3
"""
Coexistence Analysis Protocol

Defines the interface contract for coexistence analysis capabilities.
Used by infrastructure abstractions to ensure consistent coexistence analysis.

WHAT (Protocol Role): I define the interface contract for coexistence analysis
HOW (Protocol Implementation): I specify the required methods and data structures
"""

from typing import Protocol
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class ComplexityLevel(Enum):
    """Complexity levels for coexistence analysis."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AutomationPotential(Enum):
    """Automation potential levels."""
    MINIMAL = "minimal"
    PARTIAL = "partial"
    SUBSTANTIAL = "substantial"
    FULL = "full"


class CoexistenceRisk(Enum):
    """Coexistence risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ProcessStep:
    """Represents a single step in a business process."""
    step_id: str
    description: str
    actor: str  # "human", "ai", "hybrid"
    complexity: ComplexityLevel
    automation_potential: AutomationPotential
    dependencies: List[str]
    estimated_duration: Optional[int] = None  # minutes
    success_rate: Optional[float] = None  # 0.0 to 1.0


@dataclass
class CoexistenceMetrics:
    """Metrics for coexistence evaluation."""
    human_workload_percentage: float
    ai_workload_percentage: float
    hybrid_workload_percentage: float
    handoff_frequency: float
    coordination_complexity: float
    risk_level: CoexistenceRisk
    efficiency_score: float
    collaboration_score: float


@dataclass
class CoexistenceAnalysisResult:
    """Result of coexistence analysis."""
    success: bool
    complexity_analysis: Optional[Dict[str, Any]]
    automation_assessment: Optional[Dict[str, Any]]
    risk_evaluation: Optional[Dict[str, Any]]
    coexistence_metrics: Optional[CoexistenceMetrics]
    error: Optional[str]
    analyzed_at: datetime


class CoexistenceAnalysisProtocol(Protocol):
    """
    Protocol for coexistence analysis capabilities.
    
    Defines the interface contract that all coexistence analysis implementations
    must follow to ensure consistent coexistence analysis across the platform.
    """
    
    async def analyze_process_complexity(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze process complexity for coexistence.
        
        Args:
            process_data: Process data dictionary
            
        Returns:
            Dict with complexity analysis results
        """
        ...
    
    async def assess_automation_potential(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess automation potential for coexistence.
        
        Args:
            process_data: Process data dictionary
            
        Returns:
            Dict with automation potential assessment
        """
        ...
    
    async def evaluate_coexistence_risk(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate coexistence risk.
        
        Args:
            process_data: Process data dictionary
            
        Returns:
            Dict with coexistence risk evaluation
        """
        ...
    
    async def calculate_coexistence_metrics(self, process_data: Dict[str, Any]) -> CoexistenceMetrics:
        """
        Calculate coexistence metrics.
        
        Args:
            process_data: Process data dictionary
            
        Returns:
            CoexistenceMetrics with calculated metrics
        """
        ...
    
    async def generate_coexistence_recommendations(self, analysis_result: CoexistenceAnalysisResult) -> List[Dict[str, Any]]:
        """
        Generate coexistence optimization recommendations.
        
        Args:
            analysis_result: Coexistence analysis result
            
        Returns:
            List of optimization recommendations
        """
        ...
    
    async def compare_coexistence_scenarios(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare different coexistence scenarios.
        
        Args:
            scenarios: List of coexistence scenarios to compare
            
        Returns:
            Dict with scenario comparison results
        """
        ...


