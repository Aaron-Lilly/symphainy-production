#!/usr/bin/env python3
"""
Solution Designer Service Protocol

Defines the contract for solution design services in the Solution realm.
Handles solution design, architecture planning, and solution composition.

WHAT (Solution Designer Role): I design solutions and plan architectures
HOW (Solution Designer Service): I create solution designs, plan architectures, and compose solutions
"""

from typing import Dict, Any, Optional, List, runtime_checkable
from bases.protocols.service_protocol import ServiceProtocol


@runtime_checkable
class SolutionDesignerServiceProtocol(ServiceProtocol):
    """
    Protocol for Solution Designer services in the Solution realm.
    
    Solution Designer services handle:
    - Solution design and architecture planning
    - Component selection and integration
    - Solution composition and optimization
    - Design validation and refinement
    """
    
    # ============================================================================
    # SOLUTION DESIGN & ARCHITECTURE
    # ============================================================================
    
    async def design_solution(self, requirements: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design a solution based on requirements and constraints.
        
        Args:
            requirements: Solution requirements
            constraints: Design constraints and limitations
            
        Returns:
            Dict[str, Any]: Designed solution structure
        """
        ...
    
    async def plan_solution_architecture(self, solution_id: str, architecture_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan the architecture for a solution.
        
        Args:
            solution_id: ID of the solution
            architecture_params: Architecture planning parameters
            
        Returns:
            Dict[str, Any]: Planned architecture
        """
        ...
    
    async def select_solution_components(self, solution_id: str, component_requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Select components for a solution.
        
        Args:
            solution_id: ID of the solution
            component_requirements: Requirements for component selection
            
        Returns:
            List[Dict[str, Any]]: Selected components
        """
        ...
    
    # ============================================================================
    # SOLUTION COMPOSITION & INTEGRATION
    # ============================================================================
    
    async def compose_solution(self, solution_id: str, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compose a solution from selected components.
        
        Args:
            solution_id: ID of the solution
            components: Components to compose into solution
            
        Returns:
            Dict[str, Any]: Composed solution
        """
        ...
    
    async def integrate_solution_components(self, solution_id: str, integration_config: Dict[str, Any]) -> bool:
        """
        Integrate components within a solution.
        
        Args:
            solution_id: ID of the solution
            integration_config: Integration configuration
            
        Returns:
            bool: True if integration successful
        """
        ...
    
    async def optimize_solution_design(self, solution_id: str, optimization_goals: List[str]) -> Dict[str, Any]:
        """
        Optimize solution design based on goals.
        
        Args:
            solution_id: ID of the solution
            optimization_goals: Goals for optimization
            
        Returns:
            Dict[str, Any]: Optimization recommendations
        """
        ...
    
    # ============================================================================
    # DESIGN VALIDATION & REFINEMENT
    # ============================================================================
    
    async def validate_solution_design(self, solution_id: str, validation_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate solution design against criteria.
        
        Args:
            solution_id: ID of the solution
            validation_criteria: Criteria for validation
            
        Returns:
            Dict[str, Any]: Validation results
        """
        ...
    
    async def refine_solution_design(self, solution_id: str, refinement_feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine solution design based on feedback.
        
        Args:
            solution_id: ID of the solution
            refinement_feedback: Feedback for refinement
            
        Returns:
            Dict[str, Any]: Refined solution design
        """
        ...
    
    async def iterate_solution_design(self, solution_id: str, iteration_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an iteration of solution design.
        
        Args:
            solution_id: ID of the solution
            iteration_params: Parameters for iteration
            
        Returns:
            Dict[str, Any]: Iterated solution design
        """
        ...
    
    # ============================================================================
    # SOLUTION DOCUMENTATION & SPECIFICATION
    # ============================================================================
    
    async def generate_solution_specification(self, solution_id: str, spec_format: str) -> Dict[str, Any]:
        """
        Generate solution specification document.
        
        Args:
            solution_id: ID of the solution
            spec_format: Format for specification
            
        Returns:
            Dict[str, Any]: Generated specification
        """
        ...
    
    async def create_solution_documentation(self, solution_id: str, doc_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create documentation for a solution.
        
        Args:
            solution_id: ID of the solution
            doc_requirements: Documentation requirements
            
        Returns:
            Dict[str, Any]: Created documentation
        """
        ...
    
    async def export_solution_artifacts(self, solution_id: str, artifact_types: List[str]) -> Dict[str, Any]:
        """
        Export solution artifacts and deliverables.
        
        Args:
            solution_id: ID of the solution
            artifact_types: Types of artifacts to export
            
        Returns:
            Dict[str, Any]: Exported artifacts
        """
        ...
