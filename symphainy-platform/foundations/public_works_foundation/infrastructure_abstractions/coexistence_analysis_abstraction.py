#!/usr/bin/env python3
"""
Coexistence Analysis Abstraction

Infrastructure abstraction for coexistence analysis capabilities.
Implements CoexistenceAnalysisProtocol using CoexistenceAnalysisAdapter.

WHAT (Infrastructure Abstraction Role): I provide unified coexistence analysis infrastructure
HOW (Infrastructure Abstraction Implementation): I coordinate coexistence analysis adapters
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..abstraction_contracts.coexistence_analysis_protocol import (
    CoexistenceAnalysisProtocol, ComplexityLevel, AutomationPotential, 
    CoexistenceRisk, ProcessStep, CoexistenceMetrics, CoexistenceAnalysisResult
)
from ..infrastructure_adapters.coexistence_analysis_adapter import CoexistenceAnalysisAdapter

class CoexistenceAnalysisAbstraction(CoexistenceAnalysisProtocol):
    """Coexistence analysis abstraction using coexistence analysis adapter."""
    
    def __init__(self, coexistence_analysis_adapter: CoexistenceAnalysisAdapter, di_container=None, **kwargs):
        """
        Initialize coexistence analysis abstraction.
        
        Args:
            coexistence_analysis_adapter: Coexistence analysis adapter instance
            di_container: Dependency injection container
        """
        self.coexistence_analysis_adapter = coexistence_analysis_adapter
        self.di_container = di_container
        self.service_name = "coexistence_analysis_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        # Initialize abstraction
        self._initialize_abstraction()
    
    def _initialize_abstraction(self):
        """Initialize the coexistence analysis abstraction."""
        try:
            self.logger.info("✅ Coexistence Analysis Abstraction initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize coexistence analysis abstraction: {e}")
            raise  # Re-raise for service layer to handle
    
    async def analyze_process_complexity(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze process complexity for coexistence.
        
        Args:
            process_data: Process data dictionary
            
        Returns:
            Dict with complexity analysis results
        """
        try:
            # Use adapter to analyze process complexity
            result = await self.coexistence_analysis_adapter.analyze_process_complexity(process_data)
            
            if result.get("success"):
                response = {
                    "success": True,
                    "complexity_analysis": result.get("complexity_analysis", {}),
                    "analyzed_at": datetime.utcnow().isoformat()
                }
                
                return response
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Process complexity analysis failed"),
                    "analyzed_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Process complexity analysis failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def assess_automation_potential(self, coexistence_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess automation potential for coexistence.
        
        Args:
            process_data: Process data dictionary
            
        Returns:
            Dict with automation potential assessment
        """
        try:
            # Use adapter to assess automation potential
            result = await self.coexistence_analysis_adapter.assess_automation_potential(process_data)
            
            if result.get("success"):
                response = {
                    "success": True,
                    "automation_assessment": result.get("automation_assessment", {}),
                    "assessed_at": datetime.utcnow().isoformat()
                }
                
                return response
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Automation potential assessment failed"),
                    "assessed_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Automation potential assessment failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def evaluate_coexistence_risk(self, coexistence_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate coexistence risk.
        
        Args:
            process_data: Process data dictionary
            
        Returns:
            Dict with coexistence risk evaluation
        """
        try:
            # Use adapter to evaluate coexistence risk
            result = await self.coexistence_analysis_adapter.evaluate_coexistence_risk(process_data)
            
            if result.get("success"):
                response = {
                    "success": True,
                    "risk_evaluation": result.get("risk_evaluation", {}),
                    "evaluated_at": datetime.utcnow().isoformat()
                }
                
                return response
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Coexistence risk evaluation failed"),
                    "evaluated_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Coexistence risk evaluation failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Calculate coexistence metrics.
        
        Args:
            process_data: Process data dictionary
            
        Returns:
            CoexistenceMetrics with calculated metrics
        """
        try:
            # Use adapter to calculate coexistence metrics
            result = await self.coexistence_analysis_adapter.calculate_coexistence_metrics(process_data)
            
            if result.get("success"):
                metrics_data = result.get("coexistence_metrics", {})
                
                metrics = CoexistenceMetrics(
                    human_workload_percentage=metrics_data.get("human_workload_percentage", 0.0),
                    ai_workload_percentage=metrics_data.get("ai_workload_percentage", 0.0),
                    hybrid_workload_percentage=metrics_data.get("hybrid_workload_percentage", 0.0),
                    handoff_frequency=metrics_data.get("handoff_frequency", 0.0),
                    coordination_complexity=metrics_data.get("coordination_complexity", 0.0),
                    risk_level=CoexistenceRisk.LOW,  # Default, would be calculated from risk evaluation
                    efficiency_score=0.0,  # Would be calculated from analysis
                    collaboration_score=0.0  # Would be calculated from analysis
                )
                
                return metrics
            else:
                # Return default metrics on failure
                return CoexistenceMetrics(
                    human_workload_percentage=0.0,
                    ai_workload_percentage=0.0,
                    hybrid_workload_percentage=0.0,
                    handoff_frequency=0.0,
                    coordination_complexity=0.0,
                    risk_level=CoexistenceRisk.LOW,
                    efficiency_score=0.0,
                    collaboration_score=0.0
                )
                
        except Exception as e:
            self.logger.error(f"❌ Coexistence metrics calculation failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Generate coexistence optimization recommendations.
        
        Args:
            analysis_result: Coexistence analysis result
            
        Returns:
            List of optimization recommendations
        """
        try:
            recommendations = []
            
            # Generate recommendations based on analysis results
            if analysis_result.complexity_analysis:
                complexity_level = analysis_result.complexity_analysis.get("complexity_level", "medium")
                if complexity_level == "high" or complexity_level == "critical":
                    recommendations.append({
                        "category": "complexity_reduction",
                        "priority": "high",
                        "description": "Consider breaking down complex processes into smaller, manageable steps",
                        "expected_impact": "Reduced coordination complexity and improved human-AI collaboration"
                    })
            
            if analysis_result.automation_assessment:
                automation_potential = analysis_result.automation_assessment.get("automation_potential", "partial")
                if automation_potential == "substantial" or automation_potential == "full":
                    recommendations.append({
                        "category": "automation_optimization",
                        "priority": "medium",
                        "description": "High automation potential detected - consider optimizing human-AI handoffs",
                        "expected_impact": "Improved efficiency and reduced human workload"
                    })
            
            if analysis_result.risk_evaluation:
                risk_level = analysis_result.risk_evaluation.get("risk_level", "low")
                if risk_level == "high" or risk_level == "critical":
                    recommendations.append({
                        "category": "risk_mitigation",
                        "priority": "critical",
                        "description": "High coexistence risk detected - implement monitoring and fallback procedures",
                        "expected_impact": "Reduced risk of process failures and improved reliability"
                    })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"❌ Recommendation generation failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def compare_coexistence_scenarios(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare different coexistence scenarios.
        
        Args:
            scenarios: List of coexistence scenarios to compare
            
        Returns:
            Dict with scenario comparison results
        """
        try:
            comparison_result = {
                "scenario_count": len(scenarios),
                "comparisons": [],
                "best_scenario": None,
                "worst_scenario": None,
                "compared_at": datetime.utcnow().isoformat()
            }
            
            # Compare scenarios based on key metrics
            for i, scenario in enumerate(scenarios):
                scenario_metrics = scenario.get("metrics", {})
                comparison = {
                    "scenario_id": scenario.get("id", f"scenario_{i}"),
                    "name": scenario.get("name", f"Scenario {i}"),
                    "efficiency_score": scenario_metrics.get("efficiency_score", 0.0),
                    "collaboration_score": scenario_metrics.get("collaboration_score", 0.0),
                    "risk_level": scenario_metrics.get("risk_level", "low"),
                    "overall_score": (scenario_metrics.get("efficiency_score", 0.0) + 
                                    scenario_metrics.get("collaboration_score", 0.0)) / 2
                }
                comparison_result["comparisons"].append(comparison)
            
            # Find best and worst scenarios
            if comparison_result["comparisons"]:
                best_scenario = max(comparison_result["comparisons"], key=lambda x: x["overall_score"])
                worst_scenario = min(comparison_result["comparisons"], key=lambda x: x["overall_score"])
                
                comparison_result["best_scenario"] = best_scenario
                comparison_result["worst_scenario"] = worst_scenario
            
            response = {
                "success": True,
                "comparison_result": comparison_result,
                "compared_at": datetime.utcnow().isoformat()
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Scenario comparison failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Perform health check.
        
        Returns:
            Dict: Health check result
        """
        try:
            # Get adapter health
            adapter_health = await self.coexistence_analysis_adapter.health_check()
            
            health_status = {
                "healthy": adapter_health.get("healthy", False),
                "adapter": adapter_health,
                "abstraction": {
                    "name": "CoexistenceAnalysisAbstraction",
                    "status": "active"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")

            raise  # Re-raise for service layer to handle
