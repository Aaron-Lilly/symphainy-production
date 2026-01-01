"""
Handoff Identifier Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class HandoffIdentifier:
    """
    Handoff point identification following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("HandoffIdentifier micro-module initialized")
    
    async def identify_handoff_points(
        self, 
        workflow_nodes: List[Dict[str, Any]], 
        workflow_edges: List[Dict[str, Any]], 
        sop_steps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify handoff points between human and AI components.
        
        Args:
            workflow_nodes: List of workflow nodes
            workflow_edges: List of workflow edges
            sop_steps: List of SOP steps
            
        Returns:
            List of identified handoff points
        """
        try:
            handoff_points = []
            
            # Identify workflow handoff points
            workflow_handoffs = await self._identify_workflow_handoffs(workflow_nodes, workflow_edges)
            handoff_points.extend(workflow_handoffs)
            
            # Identify SOP handoff points
            sop_handoffs = await self._identify_sop_handoffs(sop_steps)
            handoff_points.extend(sop_handoffs)
            
            # Identify cross-system handoff points
            cross_system_handoffs = await self._identify_cross_system_handoffs(workflow_nodes, sop_steps)
            handoff_points.extend(cross_system_handoffs)
            
            # Analyze handoff characteristics
            for handoff in handoff_points:
                handoff["characteristics"] = await self._analyze_handoff_characteristics(handoff)
                handoff["recommendations"] = await self._generate_handoff_recommendations(handoff)
            
            return handoff_points
            
        except Exception as e:
            self.logger.error(f"Error identifying handoff points: {e}")
            return []
    
    async def _identify_workflow_handoffs(
        self, 
        workflow_nodes: List[Dict[str, Any]], 
        workflow_edges: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify handoff points in workflow."""
        try:
            handoffs = []
            
            for node in workflow_nodes:
                node_id = node.get("id", "")
                node_type = node.get("type", "").lower()
                node_name = node.get("name", "")
                
                # Check for human-AI handoff indicators
                handoff_indicators = await self._detect_handoff_indicators(node)
                
                if handoff_indicators:
                    handoff = {
                        "id": f"workflow_{node_id}",
                        "type": "workflow",
                        "node_id": node_id,
                        "node_name": node_name,
                        "node_type": node_type,
                        "indicators": handoff_indicators,
                        "handoff_type": await self._classify_handoff_type(handoff_indicators),
                        "priority": await self._assess_handoff_priority(handoff_indicators)
                    }
                    handoffs.append(handoff)
            
            return handoffs
            
        except Exception as e:
            self.logger.error(f"Error identifying workflow handoffs: {e}")
            return []
    
    async def _identify_sop_handoffs(self, sop_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify handoff points in SOP steps."""
        try:
            handoffs = []
            
            for i, step in enumerate(sop_steps):
                step_id = step.get("id", f"step_{i}")
                step_name = step.get("name", f"Step {i+1}")
                step_type = step.get("type", "").lower()
                
                # Check for human-AI handoff indicators
                handoff_indicators = await self._detect_handoff_indicators(step)
                
                if handoff_indicators:
                    handoff = {
                        "id": f"sop_{step_id}",
                        "type": "sop",
                        "step_id": step_id,
                        "step_name": step_name,
                        "step_type": step_type,
                        "step_number": i + 1,
                        "indicators": handoff_indicators,
                        "handoff_type": await self._classify_handoff_type(handoff_indicators),
                        "priority": await self._assess_handoff_priority(handoff_indicators)
                    }
                    handoffs.append(handoff)
            
            return handoffs
            
        except Exception as e:
            self.logger.error(f"Error identifying SOP handoffs: {e}")
            return []
    
    async def _identify_cross_system_handoffs(
        self, 
        workflow_nodes: List[Dict[str, Any]], 
        sop_steps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify cross-system handoff points."""
        try:
            handoffs = []
            
            # Look for connections between workflow and SOP
            for node in workflow_nodes:
                node_id = node.get("id", "")
                node_name = node.get("name", "")
                
                # Check if node references SOP steps
                if "sop" in str(node).lower() or "procedure" in str(node).lower():
                    handoff = {
                        "id": f"cross_system_{node_id}",
                        "type": "cross_system",
                        "source": "workflow",
                        "target": "sop",
                        "node_id": node_id,
                        "node_name": node_name,
                        "indicators": ["sop_reference", "procedure_call"],
                        "handoff_type": "workflow_to_sop",
                        "priority": "medium"
                    }
                    handoffs.append(handoff)
            
            # Look for SOP steps that reference workflow
            for i, step in enumerate(sop_steps):
                step_id = step.get("id", f"step_{i}")
                step_name = step.get("name", f"Step {i+1}")
                
                if "workflow" in str(step).lower() or "process" in str(step).lower():
                    handoff = {
                        "id": f"cross_system_{step_id}",
                        "type": "cross_system",
                        "source": "sop",
                        "target": "workflow",
                        "step_id": step_id,
                        "step_name": step_name,
                        "indicators": ["workflow_reference", "process_call"],
                        "handoff_type": "sop_to_workflow",
                        "priority": "medium"
                    }
                    handoffs.append(handoff)
            
            return handoffs
            
        except Exception as e:
            self.logger.error(f"Error identifying cross-system handoffs: {e}")
            return []
    
    async def _detect_handoff_indicators(self, item: Dict[str, Any]) -> List[str]:
        """Detect handoff indicators in a workflow node or SOP step."""
        try:
            indicators = []
            item_text = str(item).lower()
            
            # Human interaction indicators
            if "human" in item_text or "person" in item_text:
                indicators.append("human_interaction")
            if "user" in item_text or "operator" in item_text:
                indicators.append("user_interaction")
            if "approval" in item_text or "review" in item_text:
                indicators.append("approval_required")
            if "decision" in item_text or "judgment" in item_text:
                indicators.append("human_decision")
            
            # AI/automation indicators
            if "ai" in item_text or "artificial" in item_text:
                indicators.append("ai_processing")
            if "automated" in item_text or "automatic" in item_text:
                indicators.append("automated_processing")
            if "algorithm" in item_text or "model" in item_text:
                indicators.append("algorithmic_processing")
            
            # System integration indicators
            if "api" in item_text or "integration" in item_text:
                indicators.append("system_integration")
            if "external" in item_text or "third_party" in item_text:
                indicators.append("external_system")
            if "database" in item_text or "data" in item_text:
                indicators.append("data_processing")
            
            # Communication indicators
            if "notification" in item_text or "alert" in item_text:
                indicators.append("notification")
            if "message" in item_text or "communication" in item_text:
                indicators.append("communication")
            if "handoff" in item_text or "transfer" in item_text:
                indicators.append("explicit_handoff")
            
            # Quality control indicators
            if "validation" in item_text or "verification" in item_text:
                indicators.append("quality_control")
            if "check" in item_text or "verify" in item_text:
                indicators.append("verification")
            if "error" in item_text or "exception" in item_text:
                indicators.append("error_handling")
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error detecting handoff indicators: {e}")
            return []
    
    async def _classify_handoff_type(self, indicators: List[str]) -> str:
        """Classify handoff type based on indicators."""
        try:
            if "explicit_handoff" in indicators:
                return "explicit"
            elif "human_interaction" in indicators and "ai_processing" in indicators:
                return "human_ai_collaboration"
            elif "human_interaction" in indicators:
                return "human_handoff"
            elif "ai_processing" in indicators or "automated_processing" in indicators:
                return "ai_handoff"
            elif "system_integration" in indicators:
                return "system_integration"
            elif "approval_required" in indicators:
                return "approval_handoff"
            elif "quality_control" in indicators:
                return "quality_control_handoff"
            else:
                return "general"
                
        except Exception as e:
            self.logger.error(f"Error classifying handoff type: {e}")
            return "unknown"
    
    async def _assess_handoff_priority(self, indicators: List[str]) -> str:
        """Assess handoff priority based on indicators."""
        try:
            priority_score = 0
            
            # High priority indicators
            if "explicit_handoff" in indicators:
                priority_score += 3
            if "approval_required" in indicators:
                priority_score += 3
            if "human_decision" in indicators:
                priority_score += 2
            if "quality_control" in indicators:
                priority_score += 2
            
            # Medium priority indicators
            if "human_interaction" in indicators:
                priority_score += 1
            if "ai_processing" in indicators:
                priority_score += 1
            if "system_integration" in indicators:
                priority_score += 1
            if "error_handling" in indicators:
                priority_score += 1
            
            # Low priority indicators
            if "notification" in indicators:
                priority_score += 0.5
            if "communication" in indicators:
                priority_score += 0.5
            
            if priority_score >= 5:
                return "high"
            elif priority_score >= 2:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            self.logger.error(f"Error assessing handoff priority: {e}")
            return "medium"
    
    async def _analyze_handoff_characteristics(self, handoff: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze characteristics of a handoff point."""
        try:
            characteristics = {
                "complexity": "medium",
                "risk_level": "medium",
                "automation_potential": "medium",
                "communication_requirements": [],
                "data_requirements": [],
                "timing_requirements": []
            }
            
            indicators = handoff.get("indicators", [])
            
            # Analyze complexity
            if "human_decision" in indicators or "approval_required" in indicators:
                characteristics["complexity"] = "high"
            elif "system_integration" in indicators or "external_system" in indicators:
                characteristics["complexity"] = "high"
            elif "human_interaction" in indicators or "ai_processing" in indicators:
                characteristics["complexity"] = "medium"
            else:
                characteristics["complexity"] = "low"
            
            # Analyze risk level
            if "error_handling" in indicators or "quality_control" in indicators:
                characteristics["risk_level"] = "high"
            elif "approval_required" in indicators or "human_decision" in indicators:
                characteristics["risk_level"] = "medium"
            else:
                characteristics["risk_level"] = "low"
            
            # Analyze automation potential
            if "ai_processing" in indicators or "automated_processing" in indicators:
                characteristics["automation_potential"] = "high"
            elif "human_interaction" in indicators or "human_decision" in indicators:
                characteristics["automation_potential"] = "low"
            else:
                characteristics["automation_potential"] = "medium"
            
            # Analyze communication requirements
            if "notification" in indicators:
                characteristics["communication_requirements"].append("notification")
            if "approval_required" in indicators:
                characteristics["communication_requirements"].append("approval_request")
            if "human_interaction" in indicators:
                characteristics["communication_requirements"].append("human_interaction")
            
            # Analyze data requirements
            if "data_processing" in indicators:
                characteristics["data_requirements"].append("data_transfer")
            if "validation" in indicators or "verification" in indicators:
                characteristics["data_requirements"].append("data_validation")
            if "database" in indicators:
                characteristics["data_requirements"].append("database_access")
            
            # Analyze timing requirements
            if "real_time" in str(handoff).lower():
                characteristics["timing_requirements"].append("real_time")
            if "scheduled" in str(handoff).lower():
                characteristics["timing_requirements"].append("scheduled")
            if "immediate" in str(handoff).lower():
                characteristics["timing_requirements"].append("immediate")
            
            return characteristics
            
        except Exception as e:
            self.logger.error(f"Error analyzing handoff characteristics: {e}")
            return {
                "complexity": "unknown",
                "risk_level": "unknown",
                "automation_potential": "unknown",
                "communication_requirements": [],
                "data_requirements": [],
                "timing_requirements": []
            }
    
    async def _generate_handoff_recommendations(self, handoff: Dict[str, Any]) -> List[str]:
        """Generate recommendations for a handoff point."""
        try:
            recommendations = []
            
            handoff_type = handoff.get("handoff_type", "")
            priority = handoff.get("priority", "medium")
            characteristics = handoff.get("characteristics", {})
            
            # Type-specific recommendations
            if handoff_type == "human_ai_collaboration":
                recommendations.append("Establish clear roles and responsibilities for human and AI components")
                recommendations.append("Implement feedback mechanisms for continuous improvement")
            elif handoff_type == "approval_handoff":
                recommendations.append("Define clear approval criteria and escalation procedures")
                recommendations.append("Implement audit trails for approval decisions")
            elif handoff_type == "quality_control_handoff":
                recommendations.append("Establish quality metrics and monitoring procedures")
                recommendations.append("Implement automated quality checks where possible")
            
            # Priority-based recommendations
            if priority == "high":
                recommendations.append("Prioritize implementation and testing of this handoff point")
                recommendations.append("Establish monitoring and alerting for handoff failures")
            elif priority == "medium":
                recommendations.append("Include in standard implementation planning")
                recommendations.append("Document handoff procedures and requirements")
            else:
                recommendations.append("Consider for future optimization")
            
            # Characteristic-based recommendations
            complexity = characteristics.get("complexity", "medium")
            if complexity == "high":
                recommendations.append("Break down complex handoff into smaller, manageable components")
                recommendations.append("Provide detailed documentation and training")
            
            risk_level = characteristics.get("risk_level", "medium")
            if risk_level == "high":
                recommendations.append("Implement robust error handling and recovery procedures")
                recommendations.append("Establish backup and contingency plans")
            
            automation_potential = characteristics.get("automation_potential", "medium")
            if automation_potential == "high":
                recommendations.append("Consider automation to reduce manual handoff overhead")
            elif automation_potential == "low":
                recommendations.append("Focus on human expertise and decision-making support")
            
            return recommendations[:5]  # Limit to 5 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating handoff recommendations: {e}")
            return ["Review handoff requirements and implementation strategy"]

