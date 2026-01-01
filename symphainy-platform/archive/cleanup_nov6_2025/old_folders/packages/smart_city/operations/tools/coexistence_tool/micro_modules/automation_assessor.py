"""
Automation Assessor Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class AutomationAssessor:
    """
    Automation potential assessment following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("AutomationAssessor micro-module initialized")
    
    async def assess_automation_potential(
        self, 
        workflow_nodes: List[Dict[str, Any]], 
        workflow_edges: List[Dict[str, Any]], 
        sop_steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess automation potential of workflow and SOP.
        
        Args:
            workflow_nodes: List of workflow nodes
            workflow_edges: List of workflow edges
            sop_steps: List of SOP steps
            
        Returns:
            Automation potential assessment results
        """
        try:
            results = {
                "overall_score": 0.0,
                "automation_level": "medium",
                "workflow_automation": {},
                "sop_automation": {},
                "automation_opportunities": [],
                "automation_barriers": [],
                "recommendations": []
            }
            
            # Assess workflow automation potential
            workflow_automation = await self._assess_workflow_automation(workflow_nodes, workflow_edges)
            results["workflow_automation"] = workflow_automation
            
            # Assess SOP automation potential
            sop_automation = await self._assess_sop_automation(sop_steps)
            results["sop_automation"] = sop_automation
            
            # Calculate overall automation score
            overall_score = await self._calculate_overall_automation_score(workflow_automation, sop_automation)
            results["overall_score"] = overall_score
            results["automation_level"] = self._classify_automation_level(overall_score)
            
            # Identify automation opportunities
            opportunities = await self._identify_automation_opportunities(workflow_automation, sop_automation)
            results["automation_opportunities"] = opportunities
            
            # Identify automation barriers
            barriers = await self._identify_automation_barriers(workflow_automation, sop_automation)
            results["automation_barriers"] = barriers
            
            # Generate recommendations
            recommendations = await self._generate_automation_recommendations(overall_score, opportunities, barriers)
            results["recommendations"] = recommendations
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error assessing automation potential: {e}")
            return {
                "overall_score": 0.0,
                "automation_level": "unknown",
                "workflow_automation": {"message": f"Error: {str(e)}"},
                "sop_automation": {"message": f"Error: {str(e)}"},
                "automation_opportunities": [],
                "automation_barriers": [],
                "recommendations": ["Error in automation assessment"]
            }
    
    async def _assess_workflow_automation(
        self, 
        workflow_nodes: List[Dict[str, Any]], 
        workflow_edges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess automation potential of workflow."""
        try:
            if not workflow_nodes:
                return {"message": "No workflow nodes provided"}
            
            # Analyze each node for automation potential
            node_automation_scores = []
            for node in workflow_nodes:
                score = await self._calculate_node_automation_score(node)
                node_automation_scores.append(score)
            
            # Calculate workflow automation metrics
            metrics = {
                "total_nodes": len(workflow_nodes),
                "automation_scores": node_automation_scores,
                "average_automation_score": np.mean(node_automation_scores) if node_automation_scores else 0,
                "high_automation_nodes": len([s for s in node_automation_scores if s > 0.7]),
                "medium_automation_nodes": len([s for s in node_automation_scores if 0.3 <= s <= 0.7]),
                "low_automation_nodes": len([s for s in node_automation_scores if s < 0.3]),
                "automation_variance": np.var(node_automation_scores) if node_automation_scores else 0
            }
            
            # Calculate overall workflow automation score
            workflow_score = await self._calculate_workflow_automation_score(metrics)
            
            # Classify automation level
            automation_level = self._classify_workflow_automation(workflow_score)
            
            return {
                "metrics": metrics,
                "automation_score": workflow_score,
                "automation_level": automation_level,
                "assessment": self._generate_workflow_automation_assessment(metrics, automation_level)
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing workflow automation: {e}")
            return {"message": f"Error in workflow automation assessment: {str(e)}"}
    
    async def _assess_sop_automation(self, sop_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess automation potential of SOP steps."""
        try:
            if not sop_steps:
                return {"message": "No SOP steps provided"}
            
            # Analyze each step for automation potential
            step_automation_scores = []
            for step in sop_steps:
                score = await self._calculate_step_automation_score(step)
                step_automation_scores.append(score)
            
            # Calculate SOP automation metrics
            metrics = {
                "total_steps": len(sop_steps),
                "automation_scores": step_automation_scores,
                "average_automation_score": np.mean(step_automation_scores) if step_automation_scores else 0,
                "high_automation_steps": len([s for s in step_automation_scores if s > 0.7]),
                "medium_automation_steps": len([s for s in step_automation_scores if 0.3 <= s <= 0.7]),
                "low_automation_steps": len([s for s in step_automation_scores if s < 0.3]),
                "automation_variance": np.var(step_automation_scores) if step_automation_scores else 0
            }
            
            # Calculate overall SOP automation score
            sop_score = await self._calculate_sop_automation_score(metrics)
            
            # Classify automation level
            automation_level = self._classify_sop_automation(sop_score)
            
            return {
                "metrics": metrics,
                "automation_score": sop_score,
                "automation_level": automation_level,
                "assessment": self._generate_sop_automation_assessment(metrics, automation_level)
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing SOP automation: {e}")
            return {"message": f"Error in SOP automation assessment: {str(e)}"}
    
    async def _calculate_node_automation_score(self, node: Dict[str, Any]) -> float:
        """Calculate automation score for a single workflow node."""
        try:
            score = 0.0
            
            # Check node type for automation potential
            node_type = node.get("type", "").lower()
            if node_type in ["task", "activity", "process"]:
                score += 0.3
            elif node_type in ["decision", "gateway", "condition"]:
                score += 0.1  # Decisions are harder to automate
            elif node_type in ["start", "end", "terminate"]:
                score += 0.2
            
            # Check for automation-friendly attributes
            if "automated" in str(node).lower():
                score += 0.4
            if "manual" in str(node).lower():
                score -= 0.3
            
            # Check for repetitive patterns
            if "repeat" in str(node).lower() or "loop" in str(node).lower():
                score += 0.2
            
            # Check for data processing tasks
            if "data" in str(node).lower() or "process" in str(node).lower():
                score += 0.2
            
            # Check for human interaction requirements
            if "human" in str(node).lower() or "user" in str(node).lower():
                score -= 0.3
            if "approval" in str(node).lower() or "review" in str(node).lower():
                score -= 0.2
            
            # Check for external dependencies
            if "external" in str(node).lower() or "api" in str(node).lower():
                score += 0.1  # APIs can be automated
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.error(f"Error calculating node automation score: {e}")
            return 0.0
    
    async def _calculate_step_automation_score(self, step: Dict[str, Any]) -> float:
        """Calculate automation score for a single SOP step."""
        try:
            score = 0.0
            
            # Check step type for automation potential
            step_type = step.get("type", "").lower()
            if step_type in ["action", "task", "process"]:
                score += 0.3
            elif step_type in ["decision", "condition", "check"]:
                score += 0.1
            elif step_type in ["start", "end", "terminate"]:
                score += 0.2
            
            # Check for automation-friendly attributes
            if "automated" in str(step).lower():
                score += 0.4
            if "manual" in str(step).lower():
                score -= 0.3
            
            # Check for repetitive patterns
            if "repeat" in str(step).lower() or "routine" in str(step).lower():
                score += 0.2
            
            # Check for data processing tasks
            if "data" in str(step).lower() or "calculate" in str(step).lower():
                score += 0.2
            
            # Check for human interaction requirements
            if "human" in str(step).lower() or "person" in str(step).lower():
                score -= 0.3
            if "approval" in str(step).lower() or "review" in str(step).lower():
                score -= 0.2
            if "judgment" in str(step).lower() or "decision" in str(step).lower():
                score -= 0.2
            
            # Check for external dependencies
            if "external" in str(step).lower() or "api" in str(step).lower():
                score += 0.1
            
            # Check for clear, unambiguous instructions
            if "clear" in str(step).lower() or "specific" in str(step).lower():
                score += 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.error(f"Error calculating step automation score: {e}")
            return 0.0
    
    async def _calculate_workflow_automation_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall workflow automation score."""
        try:
            score = 0.0
            
            # Average automation score component (0-0.6)
            avg_score = metrics.get("average_automation_score", 0)
            score += avg_score * 0.6
            
            # High automation nodes component (0-0.2)
            high_automation_ratio = metrics.get("high_automation_nodes", 0) / metrics.get("total_nodes", 1)
            score += high_automation_ratio * 0.2
            
            # Low automation nodes penalty (0-0.2)
            low_automation_ratio = metrics.get("low_automation_nodes", 0) / metrics.get("total_nodes", 1)
            score -= low_automation_ratio * 0.2
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.error(f"Error calculating workflow automation score: {e}")
            return 0.0
    
    async def _calculate_sop_automation_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall SOP automation score."""
        try:
            score = 0.0
            
            # Average automation score component (0-0.6)
            avg_score = metrics.get("average_automation_score", 0)
            score += avg_score * 0.6
            
            # High automation steps component (0-0.2)
            high_automation_ratio = metrics.get("high_automation_steps", 0) / metrics.get("total_steps", 1)
            score += high_automation_ratio * 0.2
            
            # Low automation steps penalty (0-0.2)
            low_automation_ratio = metrics.get("low_automation_steps", 0) / metrics.get("total_steps", 1)
            score -= low_automation_ratio * 0.2
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.error(f"Error calculating SOP automation score: {e}")
            return 0.0
    
    async def _calculate_overall_automation_score(
        self, 
        workflow_automation: Dict[str, Any], 
        sop_automation: Dict[str, Any]
    ) -> float:
        """Calculate overall automation score."""
        try:
            workflow_score = workflow_automation.get("automation_score", 0)
            sop_score = sop_automation.get("automation_score", 0)
            
            # Weighted average (workflow 60%, SOP 40%)
            overall_score = (workflow_score * 0.6) + (sop_score * 0.4)
            return float(overall_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating overall automation score: {e}")
            return 0.0
    
    def _classify_automation_level(self, score: float) -> str:
        """Classify automation level based on score."""
        if score >= 0.8:
            return "high"
        elif score >= 0.5:
            return "medium"
        elif score >= 0.2:
            return "low"
        else:
            return "very_low"
    
    def _classify_workflow_automation(self, score: float) -> str:
        """Classify workflow automation level."""
        return self._classify_automation_level(score)
    
    def _classify_sop_automation(self, score: float) -> str:
        """Classify SOP automation level."""
        return self._classify_automation_level(score)
    
    def _generate_workflow_automation_assessment(self, metrics: Dict[str, Any], automation_level: str) -> str:
        """Generate workflow automation assessment."""
        try:
            total_nodes = metrics.get("total_nodes", 0)
            high_automation = metrics.get("high_automation_nodes", 0)
            avg_score = metrics.get("average_automation_score", 0)
            
            assessment_parts = []
            
            if automation_level == "high":
                assessment_parts.append("High automation potential with many automatable nodes")
            elif automation_level == "medium":
                assessment_parts.append("Moderate automation potential with mixed node types")
            else:
                assessment_parts.append("Low automation potential with many manual nodes")
            
            if high_automation > 0:
                assessment_parts.append(f"{high_automation} nodes are highly automatable")
            
            if avg_score > 0.7:
                assessment_parts.append("High average automation score across all nodes")
            elif avg_score < 0.3:
                assessment_parts.append("Low average automation score across all nodes")
            
            return ". ".join(assessment_parts) + "."
            
        except Exception as e:
            self.logger.error(f"Error generating workflow automation assessment: {e}")
            return "Error in workflow automation assessment"
    
    def _generate_sop_automation_assessment(self, metrics: Dict[str, Any], automation_level: str) -> str:
        """Generate SOP automation assessment."""
        try:
            total_steps = metrics.get("total_steps", 0)
            high_automation = metrics.get("high_automation_steps", 0)
            avg_score = metrics.get("average_automation_score", 0)
            
            assessment_parts = []
            
            if automation_level == "high":
                assessment_parts.append("High automation potential with many automatable steps")
            elif automation_level == "medium":
                assessment_parts.append("Moderate automation potential with mixed step types")
            else:
                assessment_parts.append("Low automation potential with many manual steps")
            
            if high_automation > 0:
                assessment_parts.append(f"{high_automation} steps are highly automatable")
            
            if avg_score > 0.7:
                assessment_parts.append("High average automation score across all steps")
            elif avg_score < 0.3:
                assessment_parts.append("Low average automation score across all steps")
            
            return ". ".join(assessment_parts) + "."
            
        except Exception as e:
            self.logger.error(f"Error generating SOP automation assessment: {e}")
            return "Error in SOP automation assessment"
    
    async def _identify_automation_opportunities(
        self, 
        workflow_automation: Dict[str, Any], 
        sop_automation: Dict[str, Any]
    ) -> List[str]:
        """Identify automation opportunities."""
        try:
            opportunities = []
            
            # Workflow opportunities
            workflow_metrics = workflow_automation.get("metrics", {})
            high_automation_nodes = workflow_metrics.get("high_automation_nodes", 0)
            if high_automation_nodes > 0:
                opportunities.append(f"{high_automation_nodes} workflow nodes are highly automatable")
            
            # SOP opportunities
            sop_metrics = sop_automation.get("metrics", {})
            high_automation_steps = sop_metrics.get("high_automation_steps", 0)
            if high_automation_steps > 0:
                opportunities.append(f"{high_automation_steps} SOP steps are highly automatable")
            
            # Overall opportunities
            workflow_score = workflow_automation.get("automation_score", 0)
            sop_score = sop_automation.get("automation_score", 0)
            
            if workflow_score > 0.7:
                opportunities.append("Workflow shows strong automation potential")
            if sop_score > 0.7:
                opportunities.append("SOP shows strong automation potential")
            
            if workflow_score > 0.5 and sop_score > 0.5:
                opportunities.append("Both workflow and SOP are suitable for automation")
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error identifying automation opportunities: {e}")
            return []
    
    async def _identify_automation_barriers(
        self, 
        workflow_automation: Dict[str, Any], 
        sop_automation: Dict[str, Any]
    ) -> List[str]:
        """Identify automation barriers."""
        try:
            barriers = []
            
            # Workflow barriers
            workflow_metrics = workflow_automation.get("metrics", {})
            low_automation_nodes = workflow_metrics.get("low_automation_nodes", 0)
            if low_automation_nodes > 0:
                barriers.append(f"{low_automation_nodes} workflow nodes have low automation potential")
            
            # SOP barriers
            sop_metrics = sop_automation.get("metrics", {})
            low_automation_steps = sop_metrics.get("low_automation_steps", 0)
            if low_automation_steps > 0:
                barriers.append(f"{low_automation_steps} SOP steps have low automation potential")
            
            # Overall barriers
            workflow_score = workflow_automation.get("automation_score", 0)
            sop_score = sop_automation.get("automation_score", 0)
            
            if workflow_score < 0.3:
                barriers.append("Workflow has significant automation barriers")
            if sop_score < 0.3:
                barriers.append("SOP has significant automation barriers")
            
            if workflow_score < 0.5 and sop_score < 0.5:
                barriers.append("Both workflow and SOP face automation challenges")
            
            return barriers
            
        except Exception as e:
            self.logger.error(f"Error identifying automation barriers: {e}")
            return []
    
    async def _generate_automation_recommendations(
        self, 
        overall_score: float, 
        opportunities: List[str], 
        barriers: List[str]
    ) -> List[str]:
        """Generate automation recommendations."""
        try:
            recommendations = []
            
            if overall_score > 0.8:
                recommendations.append("High automation potential - implement comprehensive automation strategy")
                recommendations.append("Focus on high-value, low-risk automation opportunities first")
            elif overall_score > 0.5:
                recommendations.append("Moderate automation potential - implement selective automation")
                recommendations.append("Identify and prioritize high-impact automation opportunities")
            else:
                recommendations.append("Low automation potential - focus on process improvement before automation")
                recommendations.append("Consider hybrid human-AI approaches for complex tasks")
            
            # Opportunity-based recommendations
            if opportunities:
                recommendations.append("Leverage identified automation opportunities for quick wins")
            
            # Barrier-based recommendations
            if barriers:
                recommendations.append("Address automation barriers before implementing automation")
                recommendations.append("Consider process redesign to improve automation potential")
            
            # General recommendations
            recommendations.append("Establish clear automation criteria and success metrics")
            recommendations.append("Implement pilot programs to test automation approaches")
            recommendations.append("Ensure proper training and change management for automation implementation")
            
            return recommendations[:8]  # Limit to 8 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating automation recommendations: {e}")
            return ["Review automation potential and implementation strategy"]

