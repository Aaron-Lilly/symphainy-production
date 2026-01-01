"""
Impact Evaluator Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class ImpactEvaluator:
    """
    Impact evaluation following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("ImpactEvaluator micro-module initialized")
    
    async def evaluate_impact(
        self, 
        business_analysis: Dict[str, Any], 
        outcome_predictions: Dict[str, Any], 
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate the potential impact of recommendations.
        
        Args:
            business_analysis: Business analysis results
            outcome_predictions: Outcome prediction results
            recommendations: List of recommendations
            
        Returns:
            Impact evaluation results
        """
        try:
            # Calculate overall impact score
            overall_impact = await self._calculate_overall_impact(business_analysis, outcome_predictions)
            
            # Evaluate recommendation impact
            recommendation_impact = await self._evaluate_recommendation_impact(recommendations)
            
            # Calculate ROI potential
            roi_potential = await self._calculate_roi_potential(business_analysis, recommendations)
            
            # Assess implementation feasibility
            feasibility = await self._assess_implementation_feasibility(recommendations)
            
            # Generate impact summary
            impact_summary = await self._generate_impact_summary(
                overall_impact, 
                recommendation_impact, 
                roi_potential, 
                feasibility
            )
            
            return {
                "overall_impact": overall_impact,
                "recommendation_impact": recommendation_impact,
                "roi_potential": roi_potential,
                "feasibility": feasibility,
                "impact_summary": impact_summary
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating impact: {e}")
            return {
                "overall_impact": {"score": 0, "level": "low"},
                "recommendation_impact": {"total_impact": 0, "high_impact_count": 0},
                "roi_potential": {"roi_score": 0, "payback_period": "unknown"},
                "feasibility": {"overall_feasibility": "low", "blockers": ["Error in evaluation"]},
                "impact_summary": "Error occurred during impact evaluation"
            }
    
    async def _calculate_overall_impact(
        self, 
        business_analysis: Dict[str, Any], 
        outcome_predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall impact score."""
        try:
            # Get scores from business analysis
            content_score = business_analysis.get("content_quality", {}).get("overall_score", 0)
            insights_score = business_analysis.get("insights_value", {}).get("overall_score", 0)
            operations_score = business_analysis.get("operations_efficiency", {}).get("overall_score", 0)
            business_score = business_analysis.get("business_impact", {}).get("overall_score", 0)
            
            # Get success probability
            success_probability = outcome_predictions.get("success_probability", 0)
            
            # Calculate weighted average
            weights = {"content": 0.2, "insights": 0.3, "operations": 0.2, "business": 0.3}
            weighted_score = (
                content_score * weights["content"] +
                insights_score * weights["insights"] +
                operations_score * weights["operations"] +
                business_score * weights["business"]
            )
            
            # Adjust for success probability
            adjusted_score = weighted_score * success_probability
            
            # Determine impact level
            if adjusted_score >= 80:
                impact_level = "high"
            elif adjusted_score >= 60:
                impact_level = "medium"
            else:
                impact_level = "low"
            
            return {
                "score": round(adjusted_score, 2),
                "level": impact_level,
                "content_contribution": content_score * weights["content"],
                "insights_contribution": insights_score * weights["insights"],
                "operations_contribution": operations_score * weights["operations"],
                "business_contribution": business_score * weights["business"],
                "success_probability_factor": success_probability
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating overall impact: {e}")
            return {"score": 0, "level": "low"}
    
    async def _evaluate_recommendation_impact(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate the impact of recommendations."""
        try:
            if not recommendations:
                return {"total_impact": 0, "high_impact_count": 0, "impact_breakdown": {}}
            
            # Calculate total impact score
            total_impact = 0
            high_impact_count = 0
            impact_breakdown = {}
            
            for rec in recommendations:
                impact = rec.get("impact", "medium")
                priority = rec.get("priority", "medium")
                rec_type = rec.get("type", "general")
                
                # Calculate impact score
                impact_scores = {"high": 3, "medium": 2, "low": 1}
                priority_scores = {"high": 3, "medium": 2, "low": 1}
                
                rec_impact_score = impact_scores.get(impact, 2) * priority_scores.get(priority, 2)
                total_impact += rec_impact_score
                
                if impact == "high":
                    high_impact_count += 1
                
                # Track by type
                if rec_type not in impact_breakdown:
                    impact_breakdown[rec_type] = {"count": 0, "total_impact": 0}
                
                impact_breakdown[rec_type]["count"] += 1
                impact_breakdown[rec_type]["total_impact"] += rec_impact_score
            
            # Calculate average impact per recommendation
            avg_impact = total_impact / len(recommendations) if recommendations else 0
            
            return {
                "total_impact": round(total_impact, 2),
                "high_impact_count": high_impact_count,
                "average_impact": round(avg_impact, 2),
                "impact_breakdown": impact_breakdown
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating recommendation impact: {e}")
            return {"total_impact": 0, "high_impact_count": 0, "impact_breakdown": {}}
    
    async def _calculate_roi_potential(
        self, 
        business_analysis: Dict[str, Any], 
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate ROI potential."""
        try:
            # Get business impact score
            business_score = business_analysis.get("business_impact", {}).get("overall_score", 0)
            
            # Calculate effort vs impact ratio
            total_effort = 0
            total_impact = 0
            
            for rec in recommendations:
                effort = rec.get("effort", "medium")
                impact = rec.get("impact", "medium")
                
                effort_scores = {"high": 3, "medium": 2, "low": 1}
                impact_scores = {"high": 3, "medium": 2, "low": 1}
                
                total_effort += effort_scores.get(effort, 2)
                total_impact += impact_scores.get(impact, 2)
            
            # Calculate ROI score
            if total_effort > 0:
                roi_score = (total_impact / total_effort) * business_score / 100
            else:
                roi_score = 0
            
            # Determine payback period
            if roi_score >= 2.0:
                payback_period = "1-3 months"
            elif roi_score >= 1.5:
                payback_period = "3-6 months"
            elif roi_score >= 1.0:
                payback_period = "6-12 months"
            else:
                payback_period = "12+ months"
            
            return {
                "roi_score": round(roi_score, 2),
                "payback_period": payback_period,
                "effort_impact_ratio": round(total_impact / total_effort, 2) if total_effort > 0 else 0,
                "business_score_factor": business_score / 100
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating ROI potential: {e}")
            return {"roi_score": 0, "payback_period": "unknown"}
    
    async def _assess_implementation_feasibility(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess implementation feasibility."""
        try:
            if not recommendations:
                return {"overall_feasibility": "low", "blockers": ["No recommendations provided"]}
            
            # Analyze feasibility factors
            high_effort_count = 0
            long_timeline_count = 0
            blockers = []
            
            for rec in recommendations:
                effort = rec.get("effort", "medium")
                timeline = rec.get("timeline", "unknown")
                
                if effort == "high":
                    high_effort_count += 1
                
                if "3+" in timeline or "6+" in timeline:
                    long_timeline_count += 1
                
                # Check for specific blockers
                if "compliance" in rec.get("category", "").lower():
                    blockers.append("Compliance requirements may create implementation challenges")
                
                if "critical" in rec.get("category", "").lower():
                    blockers.append("Critical issues may require immediate attention")
            
            # Calculate overall feasibility
            total_recs = len(recommendations)
            high_effort_ratio = high_effort_count / total_recs
            long_timeline_ratio = long_timeline_count / total_recs
            
            if high_effort_ratio > 0.6 or long_timeline_ratio > 0.6:
                overall_feasibility = "low"
            elif high_effort_ratio > 0.3 or long_timeline_ratio > 0.3:
                overall_feasibility = "medium"
            else:
                overall_feasibility = "high"
            
            # Add general blockers if needed
            if overall_feasibility == "low":
                blockers.append("High effort or long timeline requirements")
            
            return {
                "overall_feasibility": overall_feasibility,
                "high_effort_ratio": round(high_effort_ratio, 2),
                "long_timeline_ratio": round(long_timeline_ratio, 2),
                "blockers": blockers,
                "total_recommendations": total_recs
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing implementation feasibility: {e}")
            return {"overall_feasibility": "low", "blockers": ["Error in feasibility assessment"]}
    
    async def _generate_impact_summary(
        self, 
        overall_impact: Dict[str, Any], 
        recommendation_impact: Dict[str, Any], 
        roi_potential: Dict[str, Any], 
        feasibility: Dict[str, Any]
    ) -> str:
        """Generate impact summary."""
        try:
            impact_level = overall_impact.get("level", "low")
            roi_score = roi_potential.get("roi_score", 0)
            feasibility_level = feasibility.get("overall_feasibility", "low")
            high_impact_count = recommendation_impact.get("high_impact_count", 0)
            
            # Generate summary based on impact level
            if impact_level == "high" and roi_score >= 1.5 and feasibility_level in ["high", "medium"]:
                summary = f"High impact potential with {high_impact_count} high-impact recommendations. Strong ROI potential ({roi_score:.1f}) and good feasibility ({feasibility_level})."
            elif impact_level == "medium" and roi_score >= 1.0:
                summary = f"Medium impact potential with {high_impact_count} high-impact recommendations. Moderate ROI potential ({roi_score:.1f}) and {feasibility_level} feasibility."
            else:
                summary = f"Lower impact potential with {high_impact_count} high-impact recommendations. ROI potential: {roi_score:.1f}, Feasibility: {feasibility_level}."
            
            # Add specific insights
            if roi_score >= 2.0:
                summary += " Excellent ROI potential with quick payback period."
            elif roi_score >= 1.5:
                summary += " Good ROI potential with reasonable payback period."
            else:
                summary += " Consider focusing on high-impact, low-effort recommendations first."
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating impact summary: {e}")
            return "Error occurred during impact summary generation"

