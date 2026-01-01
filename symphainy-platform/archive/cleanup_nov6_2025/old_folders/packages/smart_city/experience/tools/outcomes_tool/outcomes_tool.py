"""
Experience Outcomes Tool - Smart City MCP Tool
Provides business outcomes analysis for Experience Pillar frontend
"""

from typing import Dict, Any, List, Optional
from backend.bases.smart_city.base_mcp import BaseMCP
from backend.bases.smart_city.base_tool import BaseTool
from backend.smart_city_library import get_logging_service, get_configuration_service
from backend.smart_city_library.infrastructure.infrastructure_services.infrastructure_service_factory import get_infrastructure_service_factory
import pandas as pd
import json

# Import micro-modules
from .micro_modules.business_analyzer import BusinessAnalyzer
from .micro_modules.outcome_predictor import OutcomePredictor
from .micro_modules.recommendation_engine import RecommendationEngine
from .micro_modules.impact_evaluator import ImpactEvaluator


class ExperienceOutcomesTool(BaseMCP):
    """
    Experience Outcomes Tool for Experience Pillar
    Provides business outcomes analysis optimized for frontend display
    """
    
    def __init__(self):
        super().__init__()
        
        # Smart City infrastructure services
        factory = get_infrastructure_service_factory()
        self._logger = factory.get_logging_service("ExperienceOutcomesTool")
        self._config = factory.get_configuration_service()
        self._data_processing = factory.get_data_processing_service()
        self._response_formatter = factory.get_response_formatting_service()
        
        # Initialize micro-modules
        self._initialize_micro_modules()
        
        self._logger.info("ExperienceOutcomesTool initialized with Smart City patterns")
    
    def _initialize_micro_modules(self):
        """Initialize micro-modules following Smart City patterns."""
        try:
            self.business_analyzer = BusinessAnalyzer(self._logger, self._config)
            self.outcome_predictor = OutcomePredictor(self._logger, self._config)
            self.recommendation_engine = RecommendationEngine(self._logger, self._config)
            self.impact_evaluator = ImpactEvaluator(self._logger, self._config)
            
            self._logger.info("ExperienceOutcomesTool micro-modules initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Error initializing ExperienceOutcomesTool micro-modules: {e}")
            raise e
    
    async def analyze_business_outcomes(
        self, 
        content_data: Dict[str, Any], 
        insights_data: Dict[str, Any], 
        operations_data: Dict[str, Any],
        session_token: Optional[str] = None,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze business outcomes from all pillar data.
        
        Args:
            content_data: Content pillar analysis results
            insights_data: Insights pillar analysis results
            operations_data: Operations pillar analysis results
            session_token: Smart City session token
            context: Additional context for analysis
            
        Returns:
            Business outcomes analysis for frontend display
        """
        try:
            # Validate session if provided
            if session_token:
                session_valid = await self._validate_session(session_token)
                if not session_valid:
                    return self._create_error_response("Invalid session token")
            
            # Perform business outcomes analysis
            analysis_results = await self._perform_outcomes_analysis(
                content_data, insights_data, operations_data, context
            )
            
            # Format for frontend display
            formatted_results = self._format_for_frontend(analysis_results)
            
            # Add Smart City metadata
            formatted_results["metadata"] = self._create_metadata(session_token, "business_outcomes_analysis")
            
            self._logger.info("Business outcomes analysis completed successfully")
            return formatted_results
            
        except Exception as e:
            self._logger.error(f"Error in business outcomes analysis: {e}")
            return self._create_error_response(f"Business outcomes analysis failed: {str(e)}")
    
    async def _perform_outcomes_analysis(
        self, 
        content_data: Dict[str, Any], 
        insights_data: Dict[str, Any], 
        operations_data: Dict[str, Any], 
        context: str
    ) -> Dict[str, Any]:
        """Perform business outcomes analysis using micro-modules."""
        results = {
            "business_analysis": {},
            "outcome_predictions": {},
            "recommendations": [],
            "success_metrics": {},
            "risk_assessment": {},
            "implementation_roadmap": {}
        }
        
        try:
            # Analyze business impact
            business_analysis = await self.business_analyzer.analyze_business_impact(
                content_data, insights_data, operations_data, context
            )
            results["business_analysis"] = business_analysis
            
            # Predict outcomes
            outcome_predictions = await self.outcome_predictor.predict_outcomes(
                content_data, insights_data, operations_data, business_analysis
            )
            results["outcome_predictions"] = outcome_predictions
            
            # Generate recommendations
            recommendations = await self.recommendation_engine.generate_recommendations(
                business_analysis, outcome_predictions, context
            )
            results["recommendations"] = recommendations
            
            # Evaluate impact
            impact_evaluation = await self.impact_evaluator.evaluate_impact(
                business_analysis, outcome_predictions, recommendations
            )
            results["impact_evaluation"] = impact_evaluation
            
            # Calculate success metrics
            success_metrics = await self._calculate_success_metrics(
                business_analysis, outcome_predictions
            )
            results["success_metrics"] = success_metrics
            
            # Assess risks
            risk_assessment = await self._assess_risks(
                business_analysis, outcome_predictions, recommendations
            )
            results["risk_assessment"] = risk_assessment
            
            # Generate implementation roadmap
            implementation_roadmap = await self._generate_implementation_roadmap(
                recommendations, success_metrics, risk_assessment
            )
            results["implementation_roadmap"] = implementation_roadmap
            
            return results
            
        except Exception as e:
            self._logger.error(f"Error in outcomes analysis: {e}")
            raise e
    
    async def _calculate_success_metrics(
        self, 
        business_analysis: Dict[str, Any], 
        outcome_predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate success metrics for the analysis."""
        try:
            metrics = {
                "overall_success_score": 0.0,
                "content_quality_score": 0.0,
                "insights_value_score": 0.0,
                "operations_efficiency_score": 0.0,
                "business_impact_score": 0.0,
                "implementation_readiness": "unknown"
            }
            
            # Calculate content quality score
            content_quality = business_analysis.get("content_quality", {})
            metrics["content_quality_score"] = content_quality.get("overall_score", 0)
            
            # Calculate insights value score
            insights_value = business_analysis.get("insights_value", {})
            metrics["insights_value_score"] = insights_value.get("overall_score", 0)
            
            # Calculate operations efficiency score
            operations_efficiency = business_analysis.get("operations_efficiency", {})
            metrics["operations_efficiency_score"] = operations_efficiency.get("overall_score", 0)
            
            # Calculate business impact score
            business_impact = business_analysis.get("business_impact", {})
            metrics["business_impact_score"] = business_impact.get("overall_score", 0)
            
            # Calculate overall success score
            overall_score = (
                metrics["content_quality_score"] * 0.25 +
                metrics["insights_value_score"] * 0.25 +
                metrics["operations_efficiency_score"] * 0.25 +
                metrics["business_impact_score"] * 0.25
            )
            metrics["overall_success_score"] = overall_score
            
            # Determine implementation readiness
            if overall_score >= 80:
                metrics["implementation_readiness"] = "excellent"
            elif overall_score >= 70:
                metrics["implementation_readiness"] = "good"
            elif overall_score >= 60:
                metrics["implementation_readiness"] = "fair"
            else:
                metrics["implementation_readiness"] = "needs_improvement"
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating success metrics: {e}")
            return {
                "overall_success_score": 0.0,
                "content_quality_score": 0.0,
                "insights_value_score": 0.0,
                "operations_efficiency_score": 0.0,
                "business_impact_score": 0.0,
                "implementation_readiness": "unknown"
            }
    
    async def _assess_risks(
        self, 
        business_analysis: Dict[str, Any], 
        outcome_predictions: Dict[str, Any], 
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess risks associated with the analysis."""
        try:
            risks = {
                "overall_risk_level": "medium",
                "risk_factors": [],
                "mitigation_strategies": [],
                "risk_score": 0.0
            }
            
            # Assess content risks
            content_quality = business_analysis.get("content_quality", {})
            if content_quality.get("overall_score", 0) < 60:
                risks["risk_factors"].append("Low content quality may impact business outcomes")
                risks["mitigation_strategies"].append("Improve data quality and validation processes")
            
            # Assess insights risks
            insights_value = business_analysis.get("insights_value", {})
            if insights_value.get("overall_score", 0) < 60:
                risks["risk_factors"].append("Low insights value may limit decision-making effectiveness")
                risks["mitigation_strategies"].append("Enhance analytics capabilities and data processing")
            
            # Assess operations risks
            operations_efficiency = business_analysis.get("operations_efficiency", {})
            if operations_efficiency.get("overall_score", 0) < 60:
                risks["risk_factors"].append("Low operations efficiency may impact implementation success")
                risks["mitigation_strategies"].append("Optimize workflow processes and human-AI coordination")
            
            # Assess business impact risks
            business_impact = business_analysis.get("business_impact", {})
            if business_impact.get("overall_score", 0) < 60:
                risks["risk_factors"].append("Low business impact may limit ROI and stakeholder buy-in")
                risks["mitigation_strategies"].append("Focus on high-impact use cases and clear value propositions")
            
            # Calculate risk score
            risk_score = 0.0
            if len(risks["risk_factors"]) > 3:
                risk_score = 0.8
            elif len(risks["risk_factors"]) > 1:
                risk_score = 0.5
            else:
                risk_score = 0.2
            
            risks["risk_score"] = risk_score
            
            # Determine overall risk level
            if risk_score >= 0.7:
                risks["overall_risk_level"] = "high"
            elif risk_score >= 0.4:
                risks["overall_risk_level"] = "medium"
            else:
                risks["overall_risk_level"] = "low"
            
            return risks
            
        except Exception as e:
            self.logger.error(f"Error assessing risks: {e}")
            return {
                "overall_risk_level": "unknown",
                "risk_factors": ["Error in risk assessment"],
                "mitigation_strategies": ["Review analysis results"],
                "risk_score": 0.0
            }
    
    async def _generate_implementation_roadmap(
        self, 
        recommendations: List[Dict[str, Any]], 
        success_metrics: Dict[str, Any], 
        risk_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate implementation roadmap."""
        try:
            roadmap = {
                "phases": [],
                "timeline": "unknown",
                "resource_requirements": {},
                "success_criteria": [],
                "milestones": []
            }
            
            # Phase 1: Foundation (0-4 weeks)
            phase1 = {
                "phase": 1,
                "name": "Foundation",
                "duration": "4 weeks",
                "description": "Establish foundation and address critical issues",
                "activities": [],
                "success_criteria": []
            }
            
            # Add foundation activities based on recommendations
            for rec in recommendations:
                if rec.get("priority") == "high" and rec.get("effort") == "low":
                    phase1["activities"].append(rec.get("description", ""))
                    phase1["success_criteria"].append(f"Complete: {rec.get('description', '')}")
            
            if phase1["activities"]:
                roadmap["phases"].append(phase1)
            
            # Phase 2: Implementation (4-12 weeks)
            phase2 = {
                "phase": 2,
                "name": "Implementation",
                "duration": "8 weeks",
                "description": "Implement core functionality and optimizations",
                "activities": [],
                "success_criteria": []
            }
            
            for rec in recommendations:
                if rec.get("priority") == "high" and rec.get("effort") == "medium":
                    phase2["activities"].append(rec.get("description", ""))
                    phase2["success_criteria"].append(f"Complete: {rec.get('description', '')}")
            
            if phase2["activities"]:
                roadmap["phases"].append(phase2)
            
            # Phase 3: Optimization (12-20 weeks)
            phase3 = {
                "phase": 3,
                "name": "Optimization",
                "duration": "8 weeks",
                "description": "Optimize and enhance based on feedback",
                "activities": [],
                "success_criteria": []
            }
            
            for rec in recommendations:
                if rec.get("priority") == "medium":
                    phase3["activities"].append(rec.get("description", ""))
                    phase3["success_criteria"].append(f"Complete: {rec.get('description', '')}")
            
            if phase3["activities"]:
                roadmap["phases"].append(phase3)
            
            # Calculate timeline
            total_weeks = sum(int(phase["duration"].split()[0]) for phase in roadmap["phases"])
            roadmap["timeline"] = f"{total_weeks} weeks"
            
            # Resource requirements
            roadmap["resource_requirements"] = {
                "technical_team": "2-3 developers",
                "business_analyst": "1 analyst",
                "project_manager": "1 manager",
                "stakeholders": "Key business stakeholders"
            }
            
            # Success criteria
            roadmap["success_criteria"] = [
                "Achieve overall success score > 80",
                "Complete all high-priority recommendations",
                "Implement risk mitigation strategies",
                "Demonstrate measurable business value"
            ]
            
            # Milestones
            roadmap["milestones"] = [
                {"week": 4, "milestone": "Foundation phase complete"},
                {"week": 12, "milestone": "Core implementation complete"},
                {"week": 20, "milestone": "Full optimization complete"}
            ]
            
            return roadmap
            
        except Exception as e:
            self.logger.error(f"Error generating implementation roadmap: {e}")
            return {
                "phases": [],
                "timeline": "unknown",
                "resource_requirements": {},
                "success_criteria": ["Error in roadmap generation"],
                "milestones": []
            }
    
    def _format_for_frontend(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Format results for frontend display."""
        return {
            "business_analysis": results.get("business_analysis", {}),
            "outcome_predictions": results.get("outcome_predictions", {}),
            "recommendations": results.get("recommendations", []),
            "success_metrics": results.get("success_metrics", {}),
            "risk_assessment": results.get("risk_assessment", {}),
            "implementation_roadmap": results.get("implementation_roadmap", {})
        }
    
    def _create_metadata(self, session_token: Optional[str], operation: str) -> Dict[str, Any]:
        """Create Smart City metadata."""
        return {
            "smart_city_version": self._config.get("version", "1.0.0"),
            "session_token": session_token,
            "operation": operation,
            "tool": "ExperienceOutcomesTool",
            "pillar": "experience",
            "architecture": "micro-module",
            "config_source": "unified_orchestrator"
        }
    
    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "business_analysis": {"message": f"Error: {message}"},
            "outcome_predictions": {"message": f"Error: {message}"},
            "recommendations": ["Please check your data and try again"],
            "success_metrics": {"overall_success_score": 0, "implementation_readiness": "error"},
            "risk_assessment": {"overall_risk_level": "unknown", "risk_factors": [f"Error: {message}"]},
            "implementation_roadmap": {"phases": [], "timeline": "unknown"},
            "metadata": {
                "error": message,
                "tool": "ExperienceOutcomesTool",
                "pillar": "experience"
            }
        }
    
    async def get_tool_capabilities(self) -> Dict[str, Any]:
        """Get tool capabilities information."""
        return {
            "tool_name": "ExperienceOutcomesTool",
            "pillar": "experience",
            "architecture": "micro-module",
            "capabilities": [
                "business_impact_analysis",
                "outcome_prediction",
                "recommendation_generation",
                "success_metrics_calculation",
                "risk_assessment",
                "implementation_roadmap_generation"
            ],
            "input_formats": ["content_data", "insights_data", "operations_data"],
            "output_format": "frontend_business_outcomes",
            "micro_modules": [
                "business_analyzer",
                "outcome_predictor",
                "recommendation_engine"
            ]
        }
