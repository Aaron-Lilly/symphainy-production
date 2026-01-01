#!/usr/bin/env python3
"""
Coexistence Analysis Adapter

Lightweight infrastructure adapter for coexistence analysis capabilities.
Wraps specific analysis libraries and provides consistent interface.

WHAT (Infrastructure Adapter Role): I provide lightweight coexistence analysis infrastructure
HOW (Infrastructure Adapter Implementation): I wrap specific analysis libraries
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
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


class CoexistenceAnalysisAdapter:
    """
    Lightweight infrastructure adapter for coexistence analysis.
    
    Wraps specific analysis libraries and provides consistent interface
    for human-AI coexistence analysis, risk assessment, and optimization.
    """
    
    def __init__(self, **kwargs):
        """Initialize coexistence analysis adapter."""
        self.logger = logging.getLogger("CoexistenceAnalysisAdapter")
        self.logger.info("✅ Coexistence Analysis Adapter initialized")
    
    async def analyze_process_complexity(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze process complexity for coexistence.
        
        Args:
            process_data: Process data dictionary
            
        Returns:
            Dict with complexity analysis results
        """
        try:
            steps = process_data.get("steps", [])
            
            # Calculate complexity metrics
            total_steps = len(steps)
            human_steps = len([s for s in steps if s.get("actor") == "human"])
            ai_steps = len([s for s in steps if s.get("actor") == "ai"])
            hybrid_steps = len([s for s in steps if s.get("actor") == "hybrid"])
            
            # Calculate complexity score
            complexity_score = self._calculate_complexity_score(steps)
            complexity_level = self._determine_complexity_level(complexity_score)
            
            return {
                "success": True,
                "complexity_analysis": {
                    "total_steps": total_steps,
                    "human_steps": human_steps,
                    "ai_steps": ai_steps,
                    "hybrid_steps": hybrid_steps,
                    "complexity_score": complexity_score,
                    "complexity_level": complexity_level.value,
                    "analysis_timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Process complexity analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
    
    async def assess_automation_potential(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess automation potential for coexistence.
        
        Args:
            process_data: Process data dictionary
            
        Returns:
            Dict with automation potential assessment
        """
        try:
            steps = process_data.get("steps", [])
            
            # Calculate automation metrics
            automation_scores = []
            for step in steps:
                score = self._calculate_step_automation_score(step)
                automation_scores.append(score)
            
            # Calculate overall automation potential
            avg_automation_score = sum(automation_scores) / len(automation_scores) if automation_scores else 0
            automation_potential = self._determine_automation_potential(avg_automation_score)
            
            return {
                "success": True,
                "automation_assessment": {
                    "average_automation_score": avg_automation_score,
                    "automation_potential": automation_potential.value,
                    "step_scores": automation_scores,
                    "assessment_timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Automation potential assessment failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "assessment_timestamp": datetime.utcnow().isoformat()
            }
    
    async def evaluate_coexistence_risk(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate coexistence risk.
        
        Args:
            process_data: Process data dictionary
            
        Returns:
            Dict with coexistence risk evaluation
        """
        try:
            steps = process_data.get("steps", [])
            
            # Calculate risk factors
            handoff_frequency = self._calculate_handoff_frequency(steps)
            coordination_complexity = self._calculate_coordination_complexity(steps)
            dependency_risk = self._calculate_dependency_risk(steps)
            
            # Calculate overall risk score
            risk_score = (handoff_frequency + coordination_complexity + dependency_risk) / 3
            risk_level = self._determine_risk_level(risk_score)
            
            return {
                "success": True,
                "risk_evaluation": {
                    "handoff_frequency": handoff_frequency,
                    "coordination_complexity": coordination_complexity,
                    "dependency_risk": dependency_risk,
                    "overall_risk_score": risk_score,
                    "risk_level": risk_level.value,
                    "evaluation_timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Coexistence risk evaluation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "evaluation_timestamp": datetime.utcnow().isoformat()
            }
    
    async def calculate_coexistence_metrics(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate coexistence metrics.
        
        Args:
            process_data: Process data dictionary
            
        Returns:
            Dict with coexistence metrics
        """
        try:
            steps = process_data.get("steps", [])
            
            # Calculate metrics
            total_steps = len(steps)
            human_steps = len([s for s in steps if s.get("actor") == "human"])
            ai_steps = len([s for s in steps if s.get("actor") == "ai"])
            hybrid_steps = len([s for s in steps if s.get("actor") == "hybrid"])
            
            human_workload_percentage = (human_steps / total_steps * 100) if total_steps > 0 else 0
            ai_workload_percentage = (ai_steps / total_steps * 100) if total_steps > 0 else 0
            hybrid_workload_percentage = (hybrid_steps / total_steps * 100) if total_steps > 0 else 0
            
            # Calculate handoff frequency
            handoff_frequency = self._calculate_handoff_frequency(steps)
            
            # Calculate coordination complexity
            coordination_complexity = self._calculate_coordination_complexity(steps)
            
            return {
                "success": True,
                "coexistence_metrics": {
                    "total_steps": total_steps,
                    "human_workload_percentage": human_workload_percentage,
                    "ai_workload_percentage": ai_workload_percentage,
                    "hybrid_workload_percentage": hybrid_workload_percentage,
                    "handoff_frequency": handoff_frequency,
                    "coordination_complexity": coordination_complexity,
                    "metrics_timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Coexistence metrics calculation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "metrics_timestamp": datetime.utcnow().isoformat()
            }
    
    def _calculate_complexity_score(self, steps: List[Dict[str, Any]]) -> float:
        """Calculate complexity score for process steps."""
        if not steps:
            return 0.0
        
        complexity_factors = []
        for step in steps:
            # Factor in step complexity
            step_complexity = step.get("complexity", "medium")
            complexity_value = {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(step_complexity, 2)
            complexity_factors.append(complexity_value)
        
        return sum(complexity_factors) / len(complexity_factors)
    
    def _determine_complexity_level(self, complexity_score: float) -> ComplexityLevel:
        """Determine complexity level from score."""
        if complexity_score <= 1.5:
            return ComplexityLevel.LOW
        elif complexity_score <= 2.5:
            return ComplexityLevel.MEDIUM
        elif complexity_score <= 3.5:
            return ComplexityLevel.HIGH
        else:
            return ComplexityLevel.CRITICAL
    
    def _calculate_step_automation_score(self, step: Dict[str, Any]) -> float:
        """Calculate automation score for a single step."""
        # Base score from automation potential
        automation_potential = step.get("automation_potential", "partial")
        base_score = {"minimal": 0.2, "partial": 0.5, "substantial": 0.8, "full": 1.0}.get(automation_potential, 0.5)
        
        # Adjust based on step complexity
        complexity = step.get("complexity", "medium")
        complexity_factor = {"low": 1.0, "medium": 0.8, "high": 0.6, "critical": 0.4}.get(complexity, 0.8)
        
        return base_score * complexity_factor
    
    def _determine_automation_potential(self, avg_score: float) -> AutomationPotential:
        """Determine automation potential from average score."""
        if avg_score <= 0.3:
            return AutomationPotential.MINIMAL
        elif avg_score <= 0.6:
            return AutomationPotential.PARTIAL
        elif avg_score <= 0.8:
            return AutomationPotential.SUBSTANTIAL
        else:
            return AutomationPotential.FULL
    
    def _calculate_handoff_frequency(self, steps: List[Dict[str, Any]]) -> float:
        """Calculate handoff frequency between human and AI."""
        if len(steps) < 2:
            return 0.0
        
        handoffs = 0
        for i in range(len(steps) - 1):
            current_actor = steps[i].get("actor", "human")
            next_actor = steps[i + 1].get("actor", "human")
            if current_actor != next_actor:
                handoffs += 1
        
        return handoffs / (len(steps) - 1) if len(steps) > 1 else 0.0
    
    def _calculate_coordination_complexity(self, steps: List[Dict[str, Any]]) -> float:
        """Calculate coordination complexity."""
        if not steps:
            return 0.0
        
        # Count different actor types
        actors = set(step.get("actor", "human") for step in steps)
        actor_diversity = len(actors)
        
        # Count dependencies
        dependencies = sum(len(step.get("dependencies", [])) for step in steps)
        
        # Calculate complexity
        complexity = (actor_diversity * 0.3) + (dependencies * 0.1)
        return min(complexity, 1.0)  # Cap at 1.0
    
    def _calculate_dependency_risk(self, steps: List[Dict[str, Any]]) -> float:
        """Calculate dependency risk."""
        if not steps:
            return 0.0
        
        # Count steps with dependencies
        steps_with_dependencies = len([s for s in steps if s.get("dependencies")])
        dependency_ratio = steps_with_dependencies / len(steps)
        
        return dependency_ratio
    
    def _determine_risk_level(self, risk_score: float) -> CoexistenceRisk:
        """Determine risk level from score."""
        if risk_score <= 0.3:
            return CoexistenceRisk.LOW
        elif risk_score <= 0.6:
            return CoexistenceRisk.MEDIUM
        elif risk_score <= 0.8:
            return CoexistenceRisk.HIGH
        else:
            return CoexistenceRisk.CRITICAL
    
    async def health_check(self) -> Dict[str, Any]:
        """Check adapter health."""
        try:
            return {
                "healthy": True,
                "adapter": "CoexistenceAnalysisAdapter",
                "capabilities": [
                    "analyze_process_complexity",
                    "assess_automation_potential",
                    "evaluate_coexistence_risk",
                    "calculate_coexistence_metrics"
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


