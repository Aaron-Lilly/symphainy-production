#!/usr/bin/env python3
"""
Insurance Use Case: Template Integration Helper

Helper functions to integrate Saga Journey and Solution Composer templates
with the platform services during initialization.
"""

from typing import Dict, Any, Optional

from .saga_journey_templates import register_saga_templates
from .solution_composer_templates import register_solution_templates


async def integrate_insurance_templates(
    di_container,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Integrate all Insurance Use Case templates with platform services.
    
    This function should be called during platform initialization to register
    all Insurance Use Case templates with Saga Journey Orchestrator and
    Solution Composer Service.
    
    Args:
        di_container: DI Container for service discovery
        user_context: Optional user context
    
    Returns:
        Integration result with registration status
    """
    results = {
        "saga_templates": {"success": False},
        "solution_templates": {"success": False}
    }
    
    try:
        # 1. Register Saga Journey templates
        try:
            # Get Saga Journey Orchestrator from DI container
            saga_orchestrator = None
            if hasattr(di_container, 'get_foundation_service'):
                saga_orchestrator = await di_container.get_foundation_service("SagaJourneyOrchestratorService")
            elif hasattr(di_container, 'curator'):
                saga_orchestrator = await di_container.curator.discover_service_by_name("SagaJourneyOrchestratorService")
            
            if saga_orchestrator:
                saga_result = await register_saga_templates(
                    saga_orchestrator=saga_orchestrator,
                    user_context=user_context
                )
                results["saga_templates"] = saga_result
            else:
                results["saga_templates"] = {
                    "success": False,
                    "error": "Saga Journey Orchestrator not found"
                }
        except Exception as e:
            results["saga_templates"] = {
                "success": False,
                "error": str(e)
            }
        
        # 2. Register Solution Composer templates
        try:
            # Get Solution Composer Service from DI container
            solution_composer = None
            if hasattr(di_container, 'get_foundation_service'):
                solution_composer = await di_container.get_foundation_service("SolutionComposerService")
            elif hasattr(di_container, 'curator'):
                solution_composer = await di_container.curator.discover_service_by_name("SolutionComposerService")
            
            if solution_composer:
                solution_result = await register_solution_templates(
                    solution_composer=solution_composer,
                    user_context=user_context
                )
                results["solution_templates"] = solution_result
            else:
                results["solution_templates"] = {
                    "success": False,
                    "error": "Solution Composer Service not found"
                }
        except Exception as e:
            results["solution_templates"] = {
                "success": False,
                "error": str(e)
            }
        
        # Overall success if both succeeded
        overall_success = (
            results["saga_templates"].get("success", False) and
            results["solution_templates"].get("success", False)
        )
        
        return {
            "success": overall_success,
            "results": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "results": results
        }











