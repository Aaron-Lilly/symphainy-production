"""
Operations Coexistence Tool - Smart City MCP Tool
Provides human-AI coexistence analysis for Operations Pillar frontend
"""

from typing import Dict, Any, List, Optional
from backend.bases.smart_city.base_mcp import BaseMCP
from backend.bases.smart_city.base_tool import BaseTool
from backend.smart_city_library import get_logging_service, get_configuration_service
from backend.smart_city_library.infrastructure.infrastructure_services.infrastructure_service_factory import get_infrastructure_service_factory
import pandas as pd
import json

# Import micro-modules
from .micro_modules.complexity_assessor import ComplexityAssessor
from .micro_modules.automation_assessor import AutomationAssessor
from .micro_modules.handoff_identifier import HandoffIdentifier
from .micro_modules.workflow_optimizer import WorkflowOptimizer


class OperationsCoexistenceTool(BaseMCP):
    """
    Operations Coexistence Tool for Operations Pillar
    Provides human-AI coexistence analysis optimized for frontend display
    """
    
    def __init__(self):
        super().__init__()
        
        # Smart City infrastructure services
        factory = get_infrastructure_service_factory()
        self._logger = factory.get_logging_service("OperationsCoexistenceTool")
        self._config = factory.get_configuration_service()
        self._data_processing = factory.get_data_processing_service()
        self._response_formatter = factory.get_response_formatting_service()
        
        # Initialize micro-modules
        self._initialize_micro_modules()
        
        self._logger.info("OperationsCoexistenceTool initialized with Smart City patterns")
    
    def _initialize_micro_modules(self):
        """Initialize micro-modules following Smart City patterns."""
        try:
            self.complexity_assessor = ComplexityAssessor(self._logger, self._config)
            self.automation_assessor = AutomationAssessor(self._logger, self._config)
            self.handoff_identifier = HandoffIdentifier(self._logger, self._config)
            self.workflow_optimizer = WorkflowOptimizer(self._logger, self._config)
            
            self._logger.info("OperationsCoexistenceTool micro-modules initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Error initializing OperationsCoexistenceTool micro-modules: {e}")
            raise e
    
    async def analyze_coexistence(
        self, 
        workflow_data: Dict[str, Any], 
        sop_data: Optional[Dict[str, Any]] = None,
        session_token: Optional[str] = None,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze human-AI coexistence for frontend display.
        
        Args:
            workflow_data: Workflow data to analyze
            sop_data: Optional SOP data for comparison
            session_token: Smart City session token
            context: Additional context for analysis
            
        Returns:
            Coexistence analysis results for frontend display
        """
        try:
            # Validate session if provided
            if session_token:
                session_valid = await self._validate_session(session_token)
                if not session_valid:
                    return self._create_error_response("Invalid session token")
            
            # Perform coexistence analysis
            analysis_results = await self._perform_coexistence_analysis(workflow_data, sop_data, context)
            
            # Format for frontend display
            formatted_results = self._format_for_frontend(analysis_results)
            
            # Add Smart City metadata
            formatted_results["metadata"] = self._create_metadata(session_token, "coexistence_analysis")
            
            self._logger.info("Coexistence analysis completed successfully")
            return formatted_results
            
        except Exception as e:
            self._logger.error(f"Error in coexistence analysis: {e}")
            return self._create_error_response(f"Coexistence analysis failed: {str(e)}")
    
    async def _perform_coexistence_analysis(
        self, 
        workflow_data: Dict[str, Any], 
        sop_data: Optional[Dict[str, Any]], 
        context: str
    ) -> Dict[str, Any]:
        """Perform coexistence analysis using micro-modules."""
        results = {
            "complexity_assessment": {},
            "automation_potential": {},
            "handoff_points": [],
            "workflow_optimization": {},
            "coexistence_recommendations": [],
            "analysis_summary": {}
        }
        
        try:
            # Extract workflow components
            workflow_nodes = workflow_data.get("nodes", [])
            workflow_edges = workflow_data.get("edges", [])
            
            # Extract SOP components if available
            sop_steps = sop_data.get("steps", []) if sop_data else []
            
            # Assess complexity
            complexity_assessment = await self.complexity_assessor.assess_complexity(
                workflow_nodes, workflow_edges, sop_steps
            )
            results["complexity_assessment"] = complexity_assessment
            
            # Assess automation potential
            automation_potential = await self.automation_assessor.assess_automation_potential(
                workflow_nodes, workflow_edges, sop_steps
            )
            results["automation_potential"] = automation_potential
            
            # Identify handoff points
            handoff_points = await self.handoff_identifier.identify_handoff_points(
                workflow_nodes, workflow_edges, sop_steps
            )
            results["handoff_points"] = handoff_points
            
            # Optimize workflow
            workflow_optimization = await self.workflow_optimizer.optimize_workflow(
                workflow_nodes, workflow_edges, complexity_assessment, automation_potential
            )
            results["workflow_optimization"] = workflow_optimization
            
            # Generate coexistence recommendations
            recommendations = await self._generate_coexistence_recommendations(
                complexity_assessment, automation_potential, handoff_points, workflow_optimization
            )
            results["coexistence_recommendations"] = recommendations
            
            # Generate analysis summary
            summary = await self._generate_analysis_summary(
                complexity_assessment, automation_potential, handoff_points, workflow_optimization
            )
            results["analysis_summary"] = summary
            
            return results
            
        except Exception as e:
            self._logger.error(f"Error in coexistence analysis: {e}")
            raise e
    
    async def _generate_coexistence_recommendations(
        self, 
        complexity_assessment: Dict[str, Any], 
        automation_potential: Dict[str, Any], 
        handoff_points: List[Dict[str, Any]], 
        workflow_optimization: Dict[str, Any]
    ) -> List[str]:
        """Generate coexistence recommendations."""
        try:
            recommendations = []
            
            # Complexity-based recommendations
            complexity_level = complexity_assessment.get("overall_complexity", "medium")
            if complexity_level == "high":
                recommendations.append("High complexity detected - consider breaking down into smaller, manageable tasks")
            elif complexity_level == "low":
                recommendations.append("Low complexity - good candidate for automation")
            
            # Automation potential recommendations
            automation_score = automation_potential.get("overall_score", 0)
            if automation_score > 80:
                recommendations.append("High automation potential - consider implementing AI solutions")
            elif automation_score < 40:
                recommendations.append("Low automation potential - focus on human expertise and decision-making")
            else:
                recommendations.append("Moderate automation potential - consider hybrid human-AI approach")
            
            # Handoff point recommendations
            if handoff_points:
                recommendations.append(f"Identify {len(handoff_points)} handoff points for human-AI collaboration")
                recommendations.append("Establish clear communication protocols at handoff points")
            else:
                recommendations.append("No clear handoff points identified - review workflow structure")
            
            # Workflow optimization recommendations
            optimization_opportunities = workflow_optimization.get("optimization_opportunities", [])
            if optimization_opportunities:
                recommendations.append(f"Found {len(optimization_opportunities)} optimization opportunities")
                recommendations.append("Implement suggested workflow improvements for better efficiency")
            
            # General coexistence recommendations
            recommendations.append("Establish clear roles and responsibilities for human and AI components")
            recommendations.append("Implement monitoring and feedback mechanisms for continuous improvement")
            
            return recommendations[:8]  # Limit to 8 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating coexistence recommendations: {e}")
            return ["Review workflow structure and human-AI interaction points"]
    
    async def _generate_analysis_summary(
        self, 
        complexity_assessment: Dict[str, Any], 
        automation_potential: Dict[str, Any], 
        handoff_points: List[Dict[str, Any]], 
        workflow_optimization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate analysis summary."""
        try:
            summary = {
                "workflow_complexity": complexity_assessment.get("overall_complexity", "unknown"),
                "automation_score": automation_potential.get("overall_score", 0),
                "handoff_count": len(handoff_points),
                "optimization_opportunities": len(workflow_optimization.get("optimization_opportunities", [])),
                "coexistence_readiness": "unknown",
                "key_findings": []
            }
            
            # Determine coexistence readiness
            complexity_level = complexity_assessment.get("overall_complexity", "medium")
            automation_score = automation_potential.get("overall_score", 0)
            handoff_count = len(handoff_points)
            
            if complexity_level == "low" and automation_score > 70:
                summary["coexistence_readiness"] = "excellent"
            elif complexity_level == "medium" and automation_score > 50 and handoff_count > 0:
                summary["coexistence_readiness"] = "good"
            elif complexity_level == "high" or automation_score < 30:
                summary["coexistence_readiness"] = "needs_improvement"
            else:
                summary["coexistence_readiness"] = "fair"
            
            # Generate key findings
            if complexity_level == "high":
                summary["key_findings"].append("High workflow complexity requires careful human-AI coordination")
            
            if automation_score > 80:
                summary["key_findings"].append("Strong automation potential - AI can handle most tasks")
            elif automation_score < 40:
                summary["key_findings"].append("Low automation potential - human expertise is critical")
            
            if handoff_count > 0:
                summary["key_findings"].append(f"Clear handoff points identified for human-AI collaboration")
            else:
                summary["key_findings"].append("Workflow needs restructuring for effective human-AI coexistence")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating analysis summary: {e}")
            return {
                "workflow_complexity": "unknown",
                "automation_score": 0,
                "handoff_count": 0,
                "optimization_opportunities": 0,
                "coexistence_readiness": "unknown",
                "key_findings": ["Error generating analysis summary"]
            }
    
    def _format_for_frontend(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Format results for frontend display."""
        return {
            "complexity_assessment": results.get("complexity_assessment", {}),
            "automation_potential": results.get("automation_potential", {}),
            "handoff_points": results.get("handoff_points", []),
            "workflow_optimization": results.get("workflow_optimization", {}),
            "coexistence_recommendations": results.get("coexistence_recommendations", []),
            "analysis_summary": results.get("analysis_summary", {})
        }
    
    def _create_metadata(self, session_token: Optional[str], operation: str) -> Dict[str, Any]:
        """Create Smart City metadata."""
        return {
            "smart_city_version": self._config.get("version", "1.0.0"),
            "session_token": session_token,
            "operation": operation,
            "tool": "OperationsCoexistenceTool",
            "pillar": "operations",
            "architecture": "micro-module",
            "config_source": "unified_orchestrator"
        }
    
    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "complexity_assessment": {"message": f"Error: {message}"},
            "automation_potential": {"message": f"Error: {message}"},
            "handoff_points": [],
            "workflow_optimization": {"message": f"Error: {message}"},
            "coexistence_recommendations": ["Please check your data and try again"],
            "analysis_summary": {"message": f"Error: {message}"},
            "metadata": {
                "error": message,
                "tool": "OperationsCoexistenceTool",
                "pillar": "operations"
            }
        }
    
    async def get_tool_capabilities(self) -> Dict[str, Any]:
        """Get tool capabilities information."""
        return {
            "tool_name": "OperationsCoexistenceTool",
            "pillar": "operations",
            "architecture": "micro-module",
            "capabilities": [
                "complexity_assessment",
                "automation_potential_analysis",
                "handoff_point_identification",
                "workflow_optimization",
                "coexistence_recommendations"
            ],
            "input_formats": ["workflow_json", "sop_json", "dict"],
            "output_format": "frontend_coexistence_analysis",
            "micro_modules": [
                "complexity_assessor",
                "automation_assessor",
                "handoff_identifier",
                "workflow_optimizer"
            ]
        }

