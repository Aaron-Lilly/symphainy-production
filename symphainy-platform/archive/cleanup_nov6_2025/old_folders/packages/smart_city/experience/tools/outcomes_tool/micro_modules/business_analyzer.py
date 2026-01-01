"""
Business Analyzer Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class BusinessAnalyzer:
    """
    Business impact analysis following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("BusinessAnalyzer micro-module initialized")
    
    async def analyze_business_impact(
        self, 
        content_data: Dict[str, Any], 
        insights_data: Dict[str, Any], 
        operations_data: Dict[str, Any], 
        context: str
    ) -> Dict[str, Any]:
        """
        Analyze business impact from all pillar data.
        
        Args:
            content_data: Content pillar analysis results
            insights_data: Insights pillar analysis results
            operations_data: Operations pillar analysis results
            context: Additional context for analysis
            
        Returns:
            Business impact analysis results
        """
        try:
            results = {
                "content_quality": {},
                "insights_value": {},
                "operations_efficiency": {},
                "business_impact": {},
                "overall_assessment": {},
                "key_findings": []
            }
            
            # Analyze content quality impact
            content_quality = await self._analyze_content_quality(content_data)
            results["content_quality"] = content_quality
            
            # Analyze insights value impact
            insights_value = await self._analyze_insights_value(insights_data)
            results["insights_value"] = insights_value
            
            # Analyze operations efficiency impact
            operations_efficiency = await self._analyze_operations_efficiency(operations_data)
            results["operations_efficiency"] = operations_efficiency
            
            # Analyze overall business impact
            business_impact = await self._analyze_business_impact_overall(
                content_quality, insights_value, operations_efficiency, context
            )
            results["business_impact"] = business_impact
            
            # Generate overall assessment
            overall_assessment = await self._generate_overall_assessment(
                content_quality, insights_value, operations_efficiency, business_impact
            )
            results["overall_assessment"] = overall_assessment
            
            # Generate key findings
            key_findings = await self._generate_key_findings(
                content_quality, insights_value, operations_efficiency, business_impact
            )
            results["key_findings"] = key_findings
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing business impact: {e}")
            return {
                "content_quality": {"message": f"Error: {str(e)}"},
                "insights_value": {"message": f"Error: {str(e)}"},
                "operations_efficiency": {"message": f"Error: {str(e)}"},
                "business_impact": {"message": f"Error: {str(e)}"},
                "overall_assessment": {"message": f"Error: {str(e)}"},
                "key_findings": ["Error in business impact analysis"]
            }
    
    async def _analyze_content_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content quality impact."""
        try:
            analysis = {
                "overall_score": 0.0,
                "data_quality_score": 0.0,
                "content_relevance_score": 0.0,
                "processing_efficiency_score": 0.0,
                "business_value_score": 0.0,
                "assessment": "unknown"
            }
            
            # Extract quality metrics from content data
            if "data_quality" in content_data:
                data_quality = content_data["data_quality"]
                analysis["data_quality_score"] = data_quality.get("overall_score", 0)
            
            if "tabular_content" in content_data:
                tabular_content = content_data["tabular_content"]
                analysis["content_relevance_score"] = tabular_content.get("relevance_score", 0)
            
            if "visualization" in content_data:
                visualization = content_data["visualization"]
                analysis["processing_efficiency_score"] = visualization.get("efficiency_score", 0)
            
            if "summary" in content_data:
                summary = content_data["summary"]
                analysis["business_value_score"] = summary.get("value_score", 0)
            
            # Calculate overall score
            scores = [
                analysis["data_quality_score"],
                analysis["content_relevance_score"],
                analysis["processing_efficiency_score"],
                analysis["business_value_score"]
            ]
            analysis["overall_score"] = np.mean([s for s in scores if s > 0]) if any(s > 0 for s in scores) else 0
            
            # Assess quality level
            if analysis["overall_score"] >= 80:
                analysis["assessment"] = "excellent"
            elif analysis["overall_score"] >= 70:
                analysis["assessment"] = "good"
            elif analysis["overall_score"] >= 60:
                analysis["assessment"] = "fair"
            else:
                analysis["assessment"] = "needs_improvement"
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing content quality: {e}")
            return {"overall_score": 0, "assessment": "error"}
    
    async def _analyze_insights_value(self, insights_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze insights value impact."""
        try:
            analysis = {
                "overall_score": 0.0,
                "anomaly_detection_score": 0.0,
                "modeling_insights_score": 0.0,
                "predictive_accuracy_score": 0.0,
                "business_relevance_score": 0.0,
                "assessment": "unknown"
            }
            
            # Extract insights metrics
            if "anomaly_detection" in insights_data:
                anomaly_detection = insights_data["anomaly_detection"]
                analysis["anomaly_detection_score"] = anomaly_detection.get("detection_accuracy", 0)
            
            if "modeling_insights" in insights_data:
                modeling_insights = insights_data["modeling_insights"]
                analysis["modeling_insights_score"] = modeling_insights.get("insight_quality", 0)
            
            if "predictive_analysis" in insights_data:
                predictive_analysis = insights_data["predictive_analysis"]
                analysis["predictive_accuracy_score"] = predictive_analysis.get("accuracy", 0)
            
            # Calculate business relevance
            if "business_impact" in insights_data:
                business_impact = insights_data["business_impact"]
                analysis["business_relevance_score"] = business_impact.get("relevance_score", 0)
            
            # Calculate overall score
            scores = [
                analysis["anomaly_detection_score"],
                analysis["modeling_insights_score"],
                analysis["predictive_accuracy_score"],
                analysis["business_relevance_score"]
            ]
            analysis["overall_score"] = np.mean([s for s in scores if s > 0]) if any(s > 0 for s in scores) else 0
            
            # Assess value level
            if analysis["overall_score"] >= 80:
                analysis["assessment"] = "excellent"
            elif analysis["overall_score"] >= 70:
                analysis["assessment"] = "good"
            elif analysis["overall_score"] >= 60:
                analysis["assessment"] = "fair"
            else:
                analysis["assessment"] = "needs_improvement"
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing insights value: {e}")
            return {"overall_score": 0, "assessment": "error"}
    
    async def _analyze_operations_efficiency(self, operations_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze operations efficiency impact."""
        try:
            analysis = {
                "overall_score": 0.0,
                "complexity_score": 0.0,
                "automation_score": 0.0,
                "handoff_efficiency_score": 0.0,
                "workflow_optimization_score": 0.0,
                "assessment": "unknown"
            }
            
            # Extract operations metrics
            if "complexity_assessment" in operations_data:
                complexity = operations_data["complexity_assessment"]
                complexity_level = complexity.get("overall_complexity", "medium")
                if complexity_level == "low":
                    analysis["complexity_score"] = 90
                elif complexity_level == "medium":
                    analysis["complexity_score"] = 70
                else:
                    analysis["complexity_score"] = 50
            
            if "automation_potential" in operations_data:
                automation = operations_data["automation_potential"]
                analysis["automation_score"] = automation.get("overall_score", 0) * 100
            
            if "handoff_points" in operations_data:
                handoff_points = operations_data["handoff_points"]
                if handoff_points:
                    analysis["handoff_efficiency_score"] = 80  # Good handoff identification
                else:
                    analysis["handoff_efficiency_score"] = 60  # No handoffs identified
            
            if "workflow_optimization" in operations_data:
                optimization = operations_data["workflow_optimization"]
                analysis["workflow_optimization_score"] = optimization.get("optimization_percentage", 0)
            
            # Calculate overall score
            scores = [
                analysis["complexity_score"],
                analysis["automation_score"],
                analysis["handoff_efficiency_score"],
                analysis["workflow_optimization_score"]
            ]
            analysis["overall_score"] = np.mean([s for s in scores if s > 0]) if any(s > 0 for s in scores) else 0
            
            # Assess efficiency level
            if analysis["overall_score"] >= 80:
                analysis["assessment"] = "excellent"
            elif analysis["overall_score"] >= 70:
                analysis["assessment"] = "good"
            elif analysis["overall_score"] >= 60:
                analysis["assessment"] = "fair"
            else:
                analysis["assessment"] = "needs_improvement"
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing operations efficiency: {e}")
            return {"overall_score": 0, "assessment": "error"}
    
    async def _analyze_business_impact_overall(
        self, 
        content_quality: Dict[str, Any], 
        insights_value: Dict[str, Any], 
        operations_efficiency: Dict[str, Any], 
        context: str
    ) -> Dict[str, Any]:
        """Analyze overall business impact."""
        try:
            analysis = {
                "overall_score": 0.0,
                "roi_potential": "unknown",
                "time_to_value": "unknown",
                "scalability_potential": "unknown",
                "competitive_advantage": "unknown",
                "assessment": "unknown"
            }
            
            # Calculate overall score
            scores = [
                content_quality.get("overall_score", 0),
                insights_value.get("overall_score", 0),
                operations_efficiency.get("overall_score", 0)
            ]
            analysis["overall_score"] = np.mean(scores)
            
            # Assess ROI potential
            if analysis["overall_score"] >= 80:
                analysis["roi_potential"] = "high"
                analysis["time_to_value"] = "short"
                analysis["scalability_potential"] = "high"
                analysis["competitive_advantage"] = "strong"
            elif analysis["overall_score"] >= 70:
                analysis["roi_potential"] = "medium"
                analysis["time_to_value"] = "medium"
                analysis["scalability_potential"] = "medium"
                analysis["competitive_advantage"] = "moderate"
            elif analysis["overall_score"] >= 60:
                analysis["roi_potential"] = "low"
                analysis["time_to_value"] = "long"
                analysis["scalability_potential"] = "low"
                analysis["competitive_advantage"] = "weak"
            else:
                analysis["roi_potential"] = "very_low"
                analysis["time_to_value"] = "very_long"
                analysis["scalability_potential"] = "very_low"
                analysis["competitive_advantage"] = "minimal"
            
            # Assess overall business impact
            if analysis["overall_score"] >= 80:
                analysis["assessment"] = "excellent"
            elif analysis["overall_score"] >= 70:
                analysis["assessment"] = "good"
            elif analysis["overall_score"] >= 60:
                analysis["assessment"] = "fair"
            else:
                analysis["assessment"] = "needs_improvement"
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing business impact overall: {e}")
            return {"overall_score": 0, "assessment": "error"}
    
    async def _generate_overall_assessment(
        self, 
        content_quality: Dict[str, Any], 
        insights_value: Dict[str, Any], 
        operations_efficiency: Dict[str, Any], 
        business_impact: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate overall assessment."""
        try:
            assessment = {
                "overall_score": 0.0,
                "strengths": [],
                "weaknesses": [],
                "opportunities": [],
                "threats": [],
                "recommendation": "unknown"
            }
            
            # Calculate overall score
            scores = [
                content_quality.get("overall_score", 0),
                insights_value.get("overall_score", 0),
                operations_efficiency.get("overall_score", 0),
                business_impact.get("overall_score", 0)
            ]
            assessment["overall_score"] = np.mean(scores)
            
            # Identify strengths
            if content_quality.get("overall_score", 0) >= 80:
                assessment["strengths"].append("High content quality")
            if insights_value.get("overall_score", 0) >= 80:
                assessment["strengths"].append("Strong insights value")
            if operations_efficiency.get("overall_score", 0) >= 80:
                assessment["strengths"].append("Efficient operations")
            if business_impact.get("overall_score", 0) >= 80:
                assessment["strengths"].append("Strong business impact")
            
            # Identify weaknesses
            if content_quality.get("overall_score", 0) < 60:
                assessment["weaknesses"].append("Low content quality")
            if insights_value.get("overall_score", 0) < 60:
                assessment["weaknesses"].append("Limited insights value")
            if operations_efficiency.get("overall_score", 0) < 60:
                assessment["weaknesses"].append("Inefficient operations")
            if business_impact.get("overall_score", 0) < 60:
                assessment["weaknesses"].append("Weak business impact")
            
            # Identify opportunities
            if content_quality.get("overall_score", 0) >= 70:
                assessment["opportunities"].append("Leverage high-quality content for better insights")
            if insights_value.get("overall_score", 0) >= 70:
                assessment["opportunities"].append("Scale insights capabilities across organization")
            if operations_efficiency.get("overall_score", 0) >= 70:
                assessment["opportunities"].append("Expand efficient operations to other areas")
            
            # Identify threats
            if content_quality.get("overall_score", 0) < 50:
                assessment["threats"].append("Poor content quality may impact decision-making")
            if insights_value.get("overall_score", 0) < 50:
                assessment["threats"].append("Limited insights may reduce competitive advantage")
            if operations_efficiency.get("overall_score", 0) < 50:
                assessment["threats"].append("Inefficient operations may impact scalability")
            
            # Generate recommendation
            if assessment["overall_score"] >= 80:
                assessment["recommendation"] = "Proceed with full implementation"
            elif assessment["overall_score"] >= 70:
                assessment["recommendation"] = "Proceed with implementation, address identified weaknesses"
            elif assessment["overall_score"] >= 60:
                assessment["recommendation"] = "Proceed with pilot implementation, focus on improvements"
            else:
                assessment["recommendation"] = "Address critical issues before implementation"
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error generating overall assessment: {e}")
            return {"overall_score": 0, "recommendation": "error"}
    
    async def _generate_key_findings(
        self, 
        content_quality: Dict[str, Any], 
        insights_value: Dict[str, Any], 
        operations_efficiency: Dict[str, Any], 
        business_impact: Dict[str, Any]
    ) -> List[str]:
        """Generate key findings."""
        try:
            findings = []
            
            # Content quality findings
            content_score = content_quality.get("overall_score", 0)
            if content_score >= 80:
                findings.append("Content quality is excellent and ready for business use")
            elif content_score >= 60:
                findings.append("Content quality is good with room for improvement")
            else:
                findings.append("Content quality needs significant improvement")
            
            # Insights value findings
            insights_score = insights_value.get("overall_score", 0)
            if insights_score >= 80:
                findings.append("Insights provide high business value and actionable intelligence")
            elif insights_score >= 60:
                findings.append("Insights provide moderate business value")
            else:
                findings.append("Insights need enhancement to provide business value")
            
            # Operations efficiency findings
            operations_score = operations_efficiency.get("overall_score", 0)
            if operations_score >= 80:
                findings.append("Operations are highly efficient and well-optimized")
            elif operations_score >= 60:
                findings.append("Operations are reasonably efficient with optimization opportunities")
            else:
                findings.append("Operations need significant efficiency improvements")
            
            # Business impact findings
            business_score = business_impact.get("overall_score", 0)
            if business_score >= 80:
                findings.append("Strong business impact potential with high ROI")
            elif business_score >= 60:
                findings.append("Moderate business impact with good ROI potential")
            else:
                findings.append("Limited business impact, focus on value creation")
            
            # Overall findings
            overall_score = np.mean([content_score, insights_score, operations_score, business_score])
            if overall_score >= 80:
                findings.append("Overall system is ready for full-scale implementation")
            elif overall_score >= 70:
                findings.append("System shows strong potential with minor improvements needed")
            elif overall_score >= 60:
                findings.append("System has good foundation but needs significant improvements")
            else:
                findings.append("System requires major improvements before implementation")
            
            return findings
            
        except Exception as e:
            self.logger.error(f"Error generating key findings: {e}")
            return ["Error in key findings generation"]

