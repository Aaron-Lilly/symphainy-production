"""
Workflow Optimizer Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class WorkflowOptimizer:
    """
    Workflow optimization following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("WorkflowOptimizer micro-module initialized")
    
    async def optimize_workflow(
        self, 
        workflow_nodes: List[Dict[str, Any]], 
        workflow_edges: List[Dict[str, Any]], 
        complexity_assessment: Dict[str, Any], 
        automation_potential: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize workflow for human-AI coexistence.
        
        Args:
            workflow_nodes: List of workflow nodes
            workflow_edges: List of workflow edges
            complexity_assessment: Complexity assessment results
            automation_potential: Automation potential assessment results
            
        Returns:
            Workflow optimization results
        """
        try:
            results = {
                "optimization_opportunities": [],
                "optimized_nodes": [],
                "optimized_edges": [],
                "optimization_metrics": {},
                "implementation_plan": [],
                "expected_benefits": []
            }
            
            # Identify optimization opportunities
            opportunities = await self._identify_optimization_opportunities(
                workflow_nodes, workflow_edges, complexity_assessment, automation_potential
            )
            results["optimization_opportunities"] = opportunities
            
            # Generate optimized nodes
            optimized_nodes = await self._optimize_nodes(workflow_nodes, opportunities)
            results["optimized_nodes"] = optimized_nodes
            
            # Generate optimized edges
            optimized_edges = await self._optimize_edges(workflow_edges, opportunities)
            results["optimized_edges"] = optimized_edges
            
            # Calculate optimization metrics
            metrics = await self._calculate_optimization_metrics(
                workflow_nodes, workflow_edges, optimized_nodes, optimized_edges
            )
            results["optimization_metrics"] = metrics
            
            # Generate implementation plan
            implementation_plan = await self._generate_implementation_plan(opportunities, metrics)
            results["implementation_plan"] = implementation_plan
            
            # Generate expected benefits
            expected_benefits = await self._generate_expected_benefits(opportunities, metrics)
            results["expected_benefits"] = expected_benefits
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error optimizing workflow: {e}")
            return {
                "optimization_opportunities": [],
                "optimized_nodes": [],
                "optimized_edges": [],
                "optimization_metrics": {"message": f"Error: {str(e)}"},
                "implementation_plan": [],
                "expected_benefits": []
            }
    
    async def _identify_optimization_opportunities(
        self, 
        workflow_nodes: List[Dict[str, Any]], 
        workflow_edges: List[Dict[str, Any]], 
        complexity_assessment: Dict[str, Any], 
        automation_potential: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify optimization opportunities."""
        try:
            opportunities = []
            
            # Complexity-based opportunities
            complexity_level = complexity_assessment.get("overall_complexity", "medium")
            if complexity_level == "high":
                opportunities.append({
                    "type": "complexity_reduction",
                    "description": "Reduce workflow complexity by breaking down complex nodes",
                    "priority": "high",
                    "impact": "high",
                    "effort": "medium"
                })
            
            # Automation-based opportunities
            automation_score = automation_potential.get("overall_score", 0)
            if automation_score > 0.7:
                opportunities.append({
                    "type": "automation_implementation",
                    "description": "Implement automation for high-potential nodes",
                    "priority": "high",
                    "impact": "high",
                    "effort": "medium"
                })
            elif automation_score < 0.3:
                opportunities.append({
                    "type": "process_improvement",
                    "description": "Improve process efficiency before considering automation",
                    "priority": "medium",
                    "impact": "medium",
                    "effort": "low"
                })
            
            # Node-based opportunities
            for node in workflow_nodes:
                node_opportunities = await self._analyze_node_optimization(node)
                opportunities.extend(node_opportunities)
            
            # Edge-based opportunities
            for edge in workflow_edges:
                edge_opportunities = await self._analyze_edge_optimization(edge)
                opportunities.extend(edge_opportunities)
            
            # Workflow structure opportunities
            structure_opportunities = await self._analyze_workflow_structure(workflow_nodes, workflow_edges)
            opportunities.extend(structure_opportunities)
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error identifying optimization opportunities: {e}")
            return []
    
    async def _analyze_node_optimization(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze optimization opportunities for a single node."""
        try:
            opportunities = []
            node_id = node.get("id", "")
            node_name = node.get("name", "")
            node_type = node.get("type", "").lower()
            
            # Check for redundant nodes
            if "duplicate" in str(node).lower() or "redundant" in str(node).lower():
                opportunities.append({
                    "type": "node_consolidation",
                    "description": f"Consolidate redundant node: {node_name}",
                    "node_id": node_id,
                    "priority": "medium",
                    "impact": "medium",
                    "effort": "low"
                })
            
            # Check for complex nodes that can be simplified
            if "complex" in str(node).lower() or "multiple" in str(node).lower():
                opportunities.append({
                    "type": "node_simplification",
                    "description": f"Simplify complex node: {node_name}",
                    "node_id": node_id,
                    "priority": "medium",
                    "impact": "medium",
                    "effort": "medium"
                })
            
            # Check for manual nodes that can be automated
            if "manual" in str(node).lower() and "automated" not in str(node).lower():
                opportunities.append({
                    "type": "automation_candidate",
                    "description": f"Consider automation for manual node: {node_name}",
                    "node_id": node_id,
                    "priority": "high",
                    "impact": "high",
                    "effort": "medium"
                })
            
            # Check for decision nodes that can be optimized
            if "decision" in node_type or "gateway" in node_type:
                opportunities.append({
                    "type": "decision_optimization",
                    "description": f"Optimize decision logic in node: {node_name}",
                    "node_id": node_id,
                    "priority": "medium",
                    "impact": "medium",
                    "effort": "low"
                })
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error analyzing node optimization: {e}")
            return []
    
    async def _analyze_edge_optimization(self, edge: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze optimization opportunities for a single edge."""
        try:
            opportunities = []
            source = edge.get("source", "")
            target = edge.get("target", "")
            
            # Check for unnecessary edges
            if "unnecessary" in str(edge).lower() or "redundant" in str(edge).lower():
                opportunities.append({
                    "type": "edge_removal",
                    "description": f"Remove unnecessary edge: {source} -> {target}",
                    "source": source,
                    "target": target,
                    "priority": "low",
                    "impact": "low",
                    "effort": "low"
                })
            
            # Check for missing edges
            if "missing" in str(edge).lower() or "gap" in str(edge).lower():
                opportunities.append({
                    "type": "edge_addition",
                    "description": f"Add missing edge: {source} -> {target}",
                    "source": source,
                    "target": target,
                    "priority": "medium",
                    "impact": "medium",
                    "effort": "low"
                })
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error analyzing edge optimization: {e}")
            return []
    
    async def _analyze_workflow_structure(
        self, 
        workflow_nodes: List[Dict[str, Any]], 
        workflow_edges: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze workflow structure optimization opportunities."""
        try:
            opportunities = []
            
            # Check for parallel execution opportunities
            parallel_opportunities = await self._identify_parallel_opportunities(workflow_nodes, workflow_edges)
            opportunities.extend(parallel_opportunities)
            
            # Check for sequential optimization opportunities
            sequential_opportunities = await self._identify_sequential_optimizations(workflow_nodes, workflow_edges)
            opportunities.extend(sequential_opportunities)
            
            # Check for bottleneck identification
            bottleneck_opportunities = await self._identify_bottlenecks(workflow_nodes, workflow_edges)
            opportunities.extend(bottleneck_opportunities)
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error analyzing workflow structure: {e}")
            return []
    
    async def _identify_parallel_opportunities(
        self, 
        workflow_nodes: List[Dict[str, Any]], 
        workflow_edges: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify opportunities for parallel execution."""
        try:
            opportunities = []
            
            # Group nodes by dependencies
            node_dependencies = {}
            for edge in workflow_edges:
                source = edge.get("source", "")
                target = edge.get("target", "")
                if target not in node_dependencies:
                    node_dependencies[target] = []
                node_dependencies[target].append(source)
            
            # Find nodes that could run in parallel
            independent_nodes = [node for node in workflow_nodes 
                               if node.get("id", "") not in node_dependencies]
            
            if len(independent_nodes) > 1:
                opportunities.append({
                    "type": "parallel_execution",
                    "description": f"Execute {len(independent_nodes)} independent nodes in parallel",
                    "nodes": [node.get("id", "") for node in independent_nodes],
                    "priority": "high",
                    "impact": "high",
                    "effort": "medium"
                })
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error identifying parallel opportunities: {e}")
            return []
    
    async def _identify_sequential_optimizations(
        self, 
        workflow_nodes: List[Dict[str, Any]], 
        workflow_edges: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify sequential optimization opportunities."""
        try:
            opportunities = []
            
            # Check for long sequential chains
            chain_lengths = await self._calculate_chain_lengths(workflow_nodes, workflow_edges)
            
            for chain in chain_lengths:
                if len(chain) > 5:  # Long sequential chain
                    opportunities.append({
                        "type": "sequential_optimization",
                        "description": f"Optimize long sequential chain of {len(chain)} nodes",
                        "chain": chain,
                        "priority": "medium",
                        "impact": "medium",
                        "effort": "medium"
                    })
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error identifying sequential optimizations: {e}")
            return []
    
    async def _identify_bottlenecks(
        self, 
        workflow_nodes: List[Dict[str, Any]], 
        workflow_edges: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify potential bottlenecks."""
        try:
            opportunities = []
            
            # Count incoming edges per node
            incoming_edges = {}
            for edge in workflow_edges:
                target = edge.get("target", "")
                incoming_edges[target] = incoming_edges.get(target, 0) + 1
            
            # Find nodes with many incoming edges (potential bottlenecks)
            for node_id, count in incoming_edges.items():
                if count > 3:  # High fan-in
                    opportunities.append({
                        "type": "bottleneck_resolution",
                        "description": f"Resolve bottleneck at node {node_id} ({count} incoming edges)",
                        "node_id": node_id,
                        "incoming_count": count,
                        "priority": "high",
                        "impact": "high",
                        "effort": "medium"
                    })
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error identifying bottlenecks: {e}")
            return []
    
    async def _calculate_chain_lengths(
        self, 
        workflow_nodes: List[Dict[str, Any]], 
        workflow_edges: List[Dict[str, Any]]
    ) -> List[List[str]]:
        """Calculate lengths of sequential chains."""
        try:
            chains = []
            
            # Build adjacency list
            graph = {}
            for edge in workflow_edges:
                source = edge.get("source", "")
                target = edge.get("target", "")
                if source not in graph:
                    graph[source] = []
                graph[source].append(target)
            
            # Find all possible chains
            for node in workflow_nodes:
                node_id = node.get("id", "")
                chain = await self._find_longest_chain(graph, node_id, [])
                if len(chain) > 1:
                    chains.append(chain)
            
            return chains
            
        except Exception as e:
            self.logger.error(f"Error calculating chain lengths: {e}")
            return []
    
    async def _find_longest_chain(self, graph: Dict[str, List[str]], node: str, visited: List[str]) -> List[str]:
        """Find the longest chain starting from a node."""
        try:
            if node in visited:
                return visited
            
            visited = visited + [node]
            longest_chain = visited
            
            for neighbor in graph.get(node, []):
                chain = await self._find_longest_chain(graph, neighbor, visited)
                if len(chain) > len(longest_chain):
                    longest_chain = chain
            
            return longest_chain
            
        except Exception as e:
            self.logger.error(f"Error finding longest chain: {e}")
            return visited
    
    async def _optimize_nodes(
        self, 
        workflow_nodes: List[Dict[str, Any]], 
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate optimized nodes based on opportunities."""
        try:
            optimized_nodes = []
            
            for node in workflow_nodes:
                optimized_node = node.copy()
                
                # Apply node-specific optimizations
                node_opportunities = [opp for opp in opportunities 
                                   if opp.get("node_id") == node.get("id", "")]
                
                for opportunity in node_opportunities:
                    if opportunity["type"] == "node_consolidation":
                        optimized_node["optimized"] = True
                        optimized_node["optimization_type"] = "consolidated"
                    elif opportunity["type"] == "node_simplification":
                        optimized_node["optimized"] = True
                        optimized_node["optimization_type"] = "simplified"
                    elif opportunity["type"] == "automation_candidate":
                        optimized_node["optimized"] = True
                        optimized_node["optimization_type"] = "automated"
                        optimized_node["automation_potential"] = "high"
                
                optimized_nodes.append(optimized_node)
            
            return optimized_nodes
            
        except Exception as e:
            self.logger.error(f"Error optimizing nodes: {e}")
            return workflow_nodes
    
    async def _optimize_edges(
        self, 
        workflow_edges: List[Dict[str, Any]], 
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate optimized edges based on opportunities."""
        try:
            optimized_edges = []
            
            for edge in workflow_edges:
                optimized_edge = edge.copy()
                
                # Apply edge-specific optimizations
                edge_opportunities = [opp for opp in opportunities 
                                    if opp.get("source") == edge.get("source", "") and 
                                       opp.get("target") == edge.get("target", "")]
                
                for opportunity in edge_opportunities:
                    if opportunity["type"] == "edge_removal":
                        continue  # Skip this edge
                    elif opportunity["type"] == "edge_addition":
                        optimized_edge["optimized"] = True
                        optimized_edge["optimization_type"] = "added"
                
                optimized_edges.append(optimized_edge)
            
            return optimized_edges
            
        except Exception as e:
            self.logger.error(f"Error optimizing edges: {e}")
            return workflow_edges
    
    async def _calculate_optimization_metrics(
        self, 
        original_nodes: List[Dict[str, Any]], 
        original_edges: List[Dict[str, Any]], 
        optimized_nodes: List[Dict[str, Any]], 
        optimized_edges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate optimization metrics."""
        try:
            metrics = {
                "original_node_count": len(original_nodes),
                "optimized_node_count": len(optimized_nodes),
                "original_edge_count": len(original_edges),
                "optimized_edge_count": len(optimized_edges),
                "node_reduction": len(original_nodes) - len(optimized_nodes),
                "edge_reduction": len(original_edges) - len(optimized_edges),
                "optimization_percentage": 0.0,
                "complexity_reduction": 0.0
            }
            
            # Calculate optimization percentage
            total_original = len(original_nodes) + len(original_edges)
            total_optimized = len(optimized_nodes) + len(optimized_edges)
            
            if total_original > 0:
                metrics["optimization_percentage"] = ((total_original - total_optimized) / total_original) * 100
            
            # Calculate complexity reduction
            original_complexity = len(original_nodes) * len(original_edges)
            optimized_complexity = len(optimized_nodes) * len(optimized_edges)
            
            if original_complexity > 0:
                metrics["complexity_reduction"] = ((original_complexity - optimized_complexity) / original_complexity) * 100
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating optimization metrics: {e}")
            return {}
    
    async def _generate_implementation_plan(
        self, 
        opportunities: List[Dict[str, Any]], 
        metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate implementation plan for optimizations."""
        try:
            plan = []
            
            # Sort opportunities by priority and effort
            sorted_opportunities = sorted(opportunities, key=lambda x: (
                {"high": 3, "medium": 2, "low": 1}.get(x.get("priority", "medium"), 2),
                {"low": 1, "medium": 2, "high": 3}.get(x.get("effort", "medium"), 2)
            ), reverse=True)
            
            # Phase 1: High priority, low effort
            phase1 = [opp for opp in sorted_opportunities 
                     if opp.get("priority") == "high" and opp.get("effort") == "low"]
            
            if phase1:
                plan.append({
                    "phase": 1,
                    "name": "Quick Wins",
                    "opportunities": phase1,
                    "duration": "1-2 weeks",
                    "description": "Implement high-impact, low-effort optimizations"
                })
            
            # Phase 2: High priority, medium effort
            phase2 = [opp for opp in sorted_opportunities 
                     if opp.get("priority") == "high" and opp.get("effort") == "medium"]
            
            if phase2:
                plan.append({
                    "phase": 2,
                    "name": "High Impact Improvements",
                    "opportunities": phase2,
                    "duration": "2-4 weeks",
                    "description": "Implement high-impact, medium-effort optimizations"
                })
            
            # Phase 3: Medium priority, low effort
            phase3 = [opp for opp in sorted_opportunities 
                     if opp.get("priority") == "medium" and opp.get("effort") == "low"]
            
            if phase3:
                plan.append({
                    "phase": 3,
                    "name": "Process Improvements",
                    "opportunities": phase3,
                    "duration": "1-2 weeks",
                    "description": "Implement medium-impact, low-effort optimizations"
                })
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Error generating implementation plan: {e}")
            return []
    
    async def _generate_expected_benefits(
        self, 
        opportunities: List[Dict[str, Any]], 
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate expected benefits from optimizations."""
        try:
            benefits = []
            
            # Complexity reduction benefits
            complexity_reduction = metrics.get("complexity_reduction", 0)
            if complexity_reduction > 0:
                benefits.append(f"Reduce workflow complexity by {complexity_reduction:.1f}%")
            
            # Node reduction benefits
            node_reduction = metrics.get("node_reduction", 0)
            if node_reduction > 0:
                benefits.append(f"Reduce number of workflow nodes by {node_reduction}")
            
            # Edge reduction benefits
            edge_reduction = metrics.get("edge_reduction", 0)
            if edge_reduction > 0:
                benefits.append(f"Reduce number of workflow edges by {edge_reduction}")
            
            # Opportunity-based benefits
            automation_opportunities = [opp for opp in opportunities if opp.get("type") == "automation_implementation"]
            if automation_opportunities:
                benefits.append(f"Implement automation for {len(automation_opportunities)} high-potential areas")
            
            parallel_opportunities = [opp for opp in opportunities if opp.get("type") == "parallel_execution"]
            if parallel_opportunities:
                benefits.append(f"Enable parallel execution for {len(parallel_opportunities)} workflow sections")
            
            bottleneck_opportunities = [opp for opp in opportunities if opp.get("type") == "bottleneck_resolution"]
            if bottleneck_opportunities:
                benefits.append(f"Resolve {len(bottleneck_opportunities)} workflow bottlenecks")
            
            # General benefits
            benefits.append("Improve overall workflow efficiency and performance")
            benefits.append("Reduce manual effort and human error")
            benefits.append("Enhance scalability and maintainability")
            
            return benefits[:8]  # Limit to 8 benefits
            
        except Exception as e:
            self.logger.error(f"Error generating expected benefits: {e}")
            return ["Improve workflow efficiency and performance"]

