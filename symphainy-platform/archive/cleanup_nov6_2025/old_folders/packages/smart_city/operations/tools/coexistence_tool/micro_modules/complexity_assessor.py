"""
Complexity Assessor Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class ComplexityAssessor:
    """
    Complexity assessment following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("ComplexityAssessor micro-module initialized")
    
    async def assess_complexity(
        self, 
        workflow_nodes: List[Dict[str, Any]], 
        workflow_edges: List[Dict[str, Any]], 
        sop_steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess complexity of workflow and SOP.
        
        Args:
            workflow_nodes: List of workflow nodes
            workflow_edges: List of workflow edges
            sop_steps: List of SOP steps
            
        Returns:
            Complexity assessment results
        """
        try:
            results = {
                "overall_complexity": "medium",
                "complexity_score": 0.0,
                "workflow_complexity": {},
                "sop_complexity": {},
                "complexity_factors": [],
                "recommendations": []
            }
            
            # Assess workflow complexity
            workflow_complexity = await self._assess_workflow_complexity(workflow_nodes, workflow_edges)
            results["workflow_complexity"] = workflow_complexity
            
            # Assess SOP complexity
            sop_complexity = await self._assess_sop_complexity(sop_steps)
            results["sop_complexity"] = sop_complexity
            
            # Calculate overall complexity
            overall_score = await self._calculate_overall_complexity(workflow_complexity, sop_complexity)
            results["complexity_score"] = overall_score
            results["overall_complexity"] = self._classify_complexity_level(overall_score)
            
            # Identify complexity factors
            complexity_factors = await self._identify_complexity_factors(workflow_complexity, sop_complexity)
            results["complexity_factors"] = complexity_factors
            
            # Generate recommendations
            recommendations = await self._generate_complexity_recommendations(overall_score, complexity_factors)
            results["recommendations"] = recommendations
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error assessing complexity: {e}")
            return {
                "overall_complexity": "unknown",
                "complexity_score": 0.0,
                "workflow_complexity": {"message": f"Error: {str(e)}"},
                "sop_complexity": {"message": f"Error: {str(e)}"},
                "complexity_factors": [],
                "recommendations": ["Error in complexity assessment"]
            }
    
    async def _assess_workflow_complexity(
        self, 
        workflow_nodes: List[Dict[str, Any]], 
        workflow_edges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess complexity of workflow structure."""
        try:
            if not workflow_nodes:
                return {"message": "No workflow nodes provided"}
            
            # Basic metrics
            node_count = len(workflow_nodes)
            edge_count = len(workflow_edges)
            
            # Calculate complexity metrics
            complexity_metrics = {
                "node_count": node_count,
                "edge_count": edge_count,
                "connectivity_ratio": edge_count / node_count if node_count > 0 else 0,
                "branching_factor": await self._calculate_branching_factor(workflow_edges),
                "depth": await self._calculate_workflow_depth(workflow_nodes, workflow_edges),
                "parallel_paths": await self._count_parallel_paths(workflow_edges),
                "decision_points": await self._count_decision_points(workflow_nodes, workflow_edges)
            }
            
            # Calculate complexity score
            complexity_score = await self._calculate_workflow_complexity_score(complexity_metrics)
            
            # Classify complexity level
            complexity_level = self._classify_workflow_complexity(complexity_score)
            
            return {
                "metrics": complexity_metrics,
                "complexity_score": complexity_score,
                "complexity_level": complexity_level,
                "assessment": self._generate_workflow_assessment(complexity_metrics, complexity_level)
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing workflow complexity: {e}")
            return {"message": f"Error in workflow complexity assessment: {str(e)}"}
    
    async def _assess_sop_complexity(self, sop_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess complexity of SOP steps."""
        try:
            if not sop_steps:
                return {"message": "No SOP steps provided"}
            
            # Basic metrics
            step_count = len(sop_steps)
            
            # Analyze step complexity
            step_complexity_scores = []
            for step in sop_steps:
                step_score = await self._calculate_step_complexity(step)
                step_complexity_scores.append(step_score)
            
            # Calculate SOP complexity metrics
            complexity_metrics = {
                "step_count": step_count,
                "average_step_complexity": np.mean(step_complexity_scores) if step_complexity_scores else 0,
                "max_step_complexity": np.max(step_complexity_scores) if step_complexity_scores else 0,
                "complexity_variance": np.var(step_complexity_scores) if step_complexity_scores else 0,
                "high_complexity_steps": len([s for s in step_complexity_scores if s > 0.7]),
                "low_complexity_steps": len([s for s in step_complexity_scores if s < 0.3])
            }
            
            # Calculate overall SOP complexity score
            complexity_score = await self._calculate_sop_complexity_score(complexity_metrics)
            
            # Classify complexity level
            complexity_level = self._classify_sop_complexity(complexity_score)
            
            return {
                "metrics": complexity_metrics,
                "complexity_score": complexity_score,
                "complexity_level": complexity_level,
                "step_scores": step_complexity_scores,
                "assessment": self._generate_sop_assessment(complexity_metrics, complexity_level)
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing SOP complexity: {e}")
            return {"message": f"Error in SOP complexity assessment: {str(e)}"}
    
    async def _calculate_step_complexity(self, step: Dict[str, Any]) -> float:
        """Calculate complexity score for a single step."""
        try:
            score = 0.0
            
            # Check for decision points
            if "decision" in step.get("type", "").lower():
                score += 0.3
            
            # Check for multiple inputs/outputs
            inputs = step.get("inputs", [])
            outputs = step.get("outputs", [])
            if len(inputs) > 3:
                score += 0.2
            if len(outputs) > 3:
                score += 0.2
            
            # Check for conditional logic
            if "conditions" in step or "if" in str(step).lower():
                score += 0.2
            
            # Check for loops or iterations
            if "loop" in str(step).lower() or "iteration" in str(step).lower():
                score += 0.2
            
            # Check for external dependencies
            if "external" in str(step).lower() or "api" in str(step).lower():
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"Error calculating step complexity: {e}")
            return 0.0
    
    async def _calculate_branching_factor(self, workflow_edges: List[Dict[str, Any]]) -> float:
        """Calculate branching factor of workflow."""
        try:
            if not workflow_edges:
                return 0.0
            
            # Count outgoing edges per node
            outgoing_edges = {}
            for edge in workflow_edges:
                source = edge.get("source", "")
                if source not in outgoing_edges:
                    outgoing_edges[source] = 0
                outgoing_edges[source] += 1
            
            if not outgoing_edges:
                return 0.0
            
            # Calculate average branching factor
            avg_branching = np.mean(list(outgoing_edges.values()))
            return float(avg_branching)
            
        except Exception as e:
            self.logger.error(f"Error calculating branching factor: {e}")
            return 0.0
    
    async def _calculate_workflow_depth(self, workflow_nodes: List[Dict[str, Any]], workflow_edges: List[Dict[str, Any]]) -> int:
        """Calculate maximum depth of workflow."""
        try:
            if not workflow_nodes or not workflow_edges:
                return 0
            
            # Build adjacency list
            graph = {}
            for edge in workflow_edges:
                source = edge.get("source", "")
                target = edge.get("target", "")
                if source not in graph:
                    graph[source] = []
                graph[source].append(target)
            
            # Find root nodes (nodes with no incoming edges)
            all_targets = set(edge.get("target", "") for edge in workflow_edges)
            root_nodes = [node.get("id", "") for node in workflow_nodes if node.get("id", "") not in all_targets]
            
            if not root_nodes:
                return 0
            
            # Calculate depth using BFS
            max_depth = 0
            for root in root_nodes:
                depth = await self._bfs_depth(graph, root)
                max_depth = max(max_depth, depth)
            
            return max_depth
            
        except Exception as e:
            self.logger.error(f"Error calculating workflow depth: {e}")
            return 0
    
    async def _bfs_depth(self, graph: Dict[str, List[str]], start: str) -> int:
        """Calculate depth using BFS."""
        try:
            if start not in graph:
                return 0
            
            queue = [(start, 0)]
            visited = set()
            max_depth = 0
            
            while queue:
                node, depth = queue.pop(0)
                if node in visited:
                    continue
                
                visited.add(node)
                max_depth = max(max_depth, depth)
                
                for neighbor in graph.get(node, []):
                    queue.append((neighbor, depth + 1))
            
            return max_depth
            
        except Exception as e:
            self.logger.error(f"Error in BFS depth calculation: {e}")
            return 0
    
    async def _count_parallel_paths(self, workflow_edges: List[Dict[str, Any]]) -> int:
        """Count parallel paths in workflow."""
        try:
            if not workflow_edges:
                return 0
            
            # Group edges by source
            source_edges = {}
            for edge in workflow_edges:
                source = edge.get("source", "")
                if source not in source_edges:
                    source_edges[source] = []
                source_edges[source].append(edge)
            
            # Count sources with multiple outgoing edges (parallel paths)
            parallel_count = 0
            for source, edges in source_edges.items():
                if len(edges) > 1:
                    parallel_count += len(edges) - 1  # -1 because one is the main path
            
            return parallel_count
            
        except Exception as e:
            self.logger.error(f"Error counting parallel paths: {e}")
            return 0
    
    async def _count_decision_points(self, workflow_nodes: List[Dict[str, Any]], workflow_edges: List[Dict[str, Any]]) -> int:
        """Count decision points in workflow."""
        try:
            if not workflow_nodes:
                return 0
            
            decision_count = 0
            for node in workflow_nodes:
                node_type = node.get("type", "").lower()
                if "decision" in node_type or "condition" in node_type or "gateway" in node_type:
                    decision_count += 1
            
            return decision_count
            
        except Exception as e:
            self.logger.error(f"Error counting decision points: {e}")
            return 0
    
    async def _calculate_workflow_complexity_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate workflow complexity score."""
        try:
            score = 0.0
            
            # Node count component (0-0.2)
            node_count = metrics.get("node_count", 0)
            if node_count > 20:
                score += 0.2
            elif node_count > 10:
                score += 0.1
            
            # Connectivity ratio component (0-0.2)
            connectivity_ratio = metrics.get("connectivity_ratio", 0)
            if connectivity_ratio > 2:
                score += 0.2
            elif connectivity_ratio > 1:
                score += 0.1
            
            # Branching factor component (0-0.2)
            branching_factor = metrics.get("branching_factor", 0)
            if branching_factor > 3:
                score += 0.2
            elif branching_factor > 2:
                score += 0.1
            
            # Depth component (0-0.2)
            depth = metrics.get("depth", 0)
            if depth > 10:
                score += 0.2
            elif depth > 5:
                score += 0.1
            
            # Parallel paths component (0-0.1)
            parallel_paths = metrics.get("parallel_paths", 0)
            if parallel_paths > 5:
                score += 0.1
            elif parallel_paths > 2:
                score += 0.05
            
            # Decision points component (0-0.1)
            decision_points = metrics.get("decision_points", 0)
            if decision_points > 5:
                score += 0.1
            elif decision_points > 2:
                score += 0.05
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"Error calculating workflow complexity score: {e}")
            return 0.0
    
    async def _calculate_sop_complexity_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate SOP complexity score."""
        try:
            score = 0.0
            
            # Step count component (0-0.3)
            step_count = metrics.get("step_count", 0)
            if step_count > 20:
                score += 0.3
            elif step_count > 10:
                score += 0.2
            elif step_count > 5:
                score += 0.1
            
            # Average step complexity component (0-0.4)
            avg_complexity = metrics.get("average_step_complexity", 0)
            score += avg_complexity * 0.4
            
            # Complexity variance component (0-0.2)
            complexity_variance = metrics.get("complexity_variance", 0)
            if complexity_variance > 0.1:
                score += 0.2
            elif complexity_variance > 0.05:
                score += 0.1
            
            # High complexity steps component (0-0.1)
            high_complexity_steps = metrics.get("high_complexity_steps", 0)
            if high_complexity_steps > 5:
                score += 0.1
            elif high_complexity_steps > 2:
                score += 0.05
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"Error calculating SOP complexity score: {e}")
            return 0.0
    
    async def _calculate_overall_complexity(self, workflow_complexity: Dict[str, Any], sop_complexity: Dict[str, Any]) -> float:
        """Calculate overall complexity score."""
        try:
            workflow_score = workflow_complexity.get("complexity_score", 0)
            sop_score = sop_complexity.get("complexity_score", 0)
            
            # Weighted average (workflow 60%, SOP 40%)
            overall_score = (workflow_score * 0.6) + (sop_score * 0.4)
            return float(overall_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating overall complexity: {e}")
            return 0.0
    
    def _classify_complexity_level(self, score: float) -> str:
        """Classify complexity level based on score."""
        if score >= 0.8:
            return "high"
        elif score >= 0.5:
            return "medium"
        elif score >= 0.2:
            return "low"
        else:
            return "very_low"
    
    def _classify_workflow_complexity(self, score: float) -> str:
        """Classify workflow complexity level."""
        return self._classify_complexity_level(score)
    
    def _classify_sop_complexity(self, score: float) -> str:
        """Classify SOP complexity level."""
        return self._classify_complexity_level(score)
    
    def _generate_workflow_assessment(self, metrics: Dict[str, Any], complexity_level: str) -> str:
        """Generate workflow complexity assessment."""
        try:
            node_count = metrics.get("node_count", 0)
            connectivity_ratio = metrics.get("connectivity_ratio", 0)
            depth = metrics.get("depth", 0)
            
            assessment_parts = []
            
            if complexity_level == "high":
                assessment_parts.append("High complexity workflow with many interconnected components")
            elif complexity_level == "medium":
                assessment_parts.append("Moderate complexity workflow with balanced structure")
            else:
                assessment_parts.append("Low complexity workflow with simple structure")
            
            if node_count > 15:
                assessment_parts.append(f"Large number of nodes ({node_count})")
            
            if connectivity_ratio > 1.5:
                assessment_parts.append("High connectivity between nodes")
            
            if depth > 8:
                assessment_parts.append(f"Deep workflow structure (depth: {depth})")
            
            return ". ".join(assessment_parts) + "."
            
        except Exception as e:
            self.logger.error(f"Error generating workflow assessment: {e}")
            return "Error in workflow assessment"
    
    def _generate_sop_assessment(self, metrics: Dict[str, Any], complexity_level: str) -> str:
        """Generate SOP complexity assessment."""
        try:
            step_count = metrics.get("step_count", 0)
            avg_complexity = metrics.get("average_step_complexity", 0)
            
            assessment_parts = []
            
            if complexity_level == "high":
                assessment_parts.append("High complexity SOP with intricate procedures")
            elif complexity_level == "medium":
                assessment_parts.append("Moderate complexity SOP with balanced steps")
            else:
                assessment_parts.append("Low complexity SOP with simple procedures")
            
            if step_count > 15:
                assessment_parts.append(f"Many steps ({step_count})")
            
            if avg_complexity > 0.7:
                assessment_parts.append("High average step complexity")
            
            return ". ".join(assessment_parts) + "."
            
        except Exception as e:
            self.logger.error(f"Error generating SOP assessment: {e}")
            return "Error in SOP assessment"
    
    async def _identify_complexity_factors(
        self, 
        workflow_complexity: Dict[str, Any], 
        sop_complexity: Dict[str, Any]
    ) -> List[str]:
        """Identify key complexity factors."""
        try:
            factors = []
            
            # Workflow factors
            workflow_metrics = workflow_complexity.get("metrics", {})
            if workflow_metrics.get("node_count", 0) > 15:
                factors.append("Large number of workflow nodes")
            
            if workflow_metrics.get("connectivity_ratio", 0) > 2:
                factors.append("High connectivity between nodes")
            
            if workflow_metrics.get("depth", 0) > 8:
                factors.append("Deep workflow structure")
            
            if workflow_metrics.get("parallel_paths", 0) > 3:
                factors.append("Multiple parallel execution paths")
            
            if workflow_metrics.get("decision_points", 0) > 5:
                factors.append("Many decision points")
            
            # SOP factors
            sop_metrics = sop_complexity.get("metrics", {})
            if sop_metrics.get("step_count", 0) > 15:
                factors.append("Large number of SOP steps")
            
            if sop_metrics.get("average_step_complexity", 0) > 0.7:
                factors.append("High average step complexity")
            
            if sop_metrics.get("high_complexity_steps", 0) > 3:
                factors.append("Multiple high-complexity steps")
            
            return factors
            
        except Exception as e:
            self.logger.error(f"Error identifying complexity factors: {e}")
            return []
    
    async def _generate_complexity_recommendations(self, overall_score: float, complexity_factors: List[str]) -> List[str]:
        """Generate recommendations based on complexity analysis."""
        try:
            recommendations = []
            
            if overall_score > 0.8:
                recommendations.append("Consider breaking down complex workflows into smaller, manageable components")
                recommendations.append("Implement clear documentation and training for complex procedures")
            elif overall_score > 0.5:
                recommendations.append("Monitor workflow performance and identify optimization opportunities")
                recommendations.append("Consider automation for repetitive or low-complexity tasks")
            else:
                recommendations.append("Workflow complexity is manageable - focus on efficiency improvements")
            
            # Factor-specific recommendations
            if "Large number of workflow nodes" in complexity_factors:
                recommendations.append("Consider modularizing workflow into sub-workflows")
            
            if "High connectivity between nodes" in complexity_factors:
                recommendations.append("Review and optimize node connections to reduce complexity")
            
            if "Deep workflow structure" in complexity_factors:
                recommendations.append("Consider flattening workflow structure where possible")
            
            if "Multiple parallel execution paths" in complexity_factors:
                recommendations.append("Ensure proper synchronization mechanisms for parallel paths")
            
            if "Many decision points" in complexity_factors:
                recommendations.append("Simplify decision logic and provide clear decision criteria")
            
            return recommendations[:6]  # Limit to 6 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating complexity recommendations: {e}")
            return ["Review workflow structure and complexity factors"]

