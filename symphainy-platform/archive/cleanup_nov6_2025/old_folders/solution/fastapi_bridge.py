"""
Solution Realm FastAPI Bridge
FastAPI integration for Solution Realm services
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
import logging

from .services.solution_manager.solution_manager_service import SolutionManagerService
from .services.solution_orchestration_hub.solution_orchestration_hub_service import SolutionOrchestrationHubService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.di_container.di_container_service import DIContainerService
from utilities import UserContext

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/solution", tags=["solution"])

# Dependency injection
def get_solution_manager() -> SolutionManagerService:
    """Get Solution Manager Service instance."""
    # This would be injected via dependency injection in real implementation
    # For now, we'll create a mock instance
    try:
        # Get Public Works Foundation (would be injected)
        public_works_foundation = None  # This would be injected
        return SolutionManagerService(public_works_foundation)
    except Exception as e:
        logger.error(f"Failed to create Solution Manager: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize Solution Manager")

def get_solution_orchestration_hub() -> SolutionOrchestrationHubService:
    """Get Solution Orchestration Hub Service instance."""
    try:
        # Get services from DI container (would be injected in real implementation)
        di_container = None  # This would be injected
        public_works_foundation = None  # This would be injected
        curator_foundation = None  # This would be injected
        
        return SolutionOrchestrationHubService(
            di_container=di_container,
            public_works_foundation=public_works_foundation,
            curator_foundation=curator_foundation
        )
    except Exception as e:
        logger.error(f"Failed to create Solution Orchestration Hub: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize Solution Orchestration Hub")

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    solution_manager: SolutionManagerService = Depends(get_solution_manager)
) -> Dict[str, Any]:
    """Get summary dashboard data for all realms."""
    try:
        result = await solution_manager.get_dashboard_summary()
        return result
    except Exception as e:
        logger.error(f"Failed to get dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/realm/{realm_name}")
async def get_realm_dashboard(
    realm_name: str,
    solution_manager: SolutionManagerService = Depends(get_solution_manager)
) -> Dict[str, Any]:
    """Get detailed dashboard data for a specific realm."""
    try:
        result = await solution_manager.get_realm_dashboard(realm_name)
        return result
    except Exception as e:
        logger.error(f"Failed to get realm dashboard for {realm_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/journey/templates")
async def get_journey_templates(
    solution_manager: SolutionManagerService = Depends(get_solution_manager)
) -> Dict[str, Any]:
    """Get all saved journey templates."""
    try:
        result = await solution_manager.get_journey_templates()
        return result
    except Exception as e:
        logger.error(f"Failed to get journey templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/journey/save")
async def save_journey_template(
    template_data: Dict[str, Any],
    solution_manager: SolutionManagerService = Depends(get_solution_manager)
) -> Dict[str, Any]:
    """Save a journey template for reuse."""
    try:
        result = await solution_manager.save_journey_template(template_data)
        return result
    except Exception as e:
        logger.error(f"Failed to save journey template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platform/health")
async def get_platform_health(
    solution_manager: SolutionManagerService = Depends(get_solution_manager)
) -> Dict[str, Any]:
    """Get overall platform health status."""
    try:
        # Get platform summary dashboard
        result = await solution_manager.get_realm_dashboard("platform_summary")
        return result
    except Exception as e:
        logger.error(f"Failed to get platform health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SOLUTION ORCHESTRATION HUB PUBLIC API ENDPOINTS
# ============================================================================

@router.post("/orchestrate")
async def orchestrate_solution(
    request_data: Dict[str, Any],
    solution_orchestration_hub: SolutionOrchestrationHubService = Depends(get_solution_orchestration_hub)
) -> Dict[str, Any]:
    """
    Public API endpoint for solution orchestration.
    
    This endpoint can be called by:
    - Frontend landing pages (MVP use case)
    - External clients (future extensibility)
    - Direct integrations (bypassing landing page service)
    
    Request format:
    {
        "business_outcome": "AI-enabled legacy data integration",
        "solution_intent": "mvp",  # mvp, poc, demo, roadmap, production, integration, custom
        "user_context": {
            "user_id": "user123",
            "tenant_id": "tenant456",
            "session_id": "session789"
        }
    }
    """
    try:
        # Extract request data
        business_outcome = request_data.get("business_outcome", "")
        solution_intent = request_data.get("solution_intent", "mvp")
        user_context_data = request_data.get("user_context", {})
        
        # Create UserContext
        user_context = UserContext(
            user_id=user_context_data.get("user_id", "anonymous"),
            tenant_id=user_context_data.get("tenant_id", "default"),
            session_id=user_context_data.get("session_id", "default")
        )
        
        # Orchestrate solution
        result = await solution_orchestration_hub.orchestrate_solution(
            user_input=business_outcome,
            user_context=user_context
        )
        
        return {
            "success": True,
            "result": result,
            "timestamp": result.get("timestamp", "unknown")
        }
        
    except Exception as e:
        logger.error(f"Failed to orchestrate solution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orchestrate/capabilities")
async def get_orchestration_capabilities(
    solution_orchestration_hub: SolutionOrchestrationHubService = Depends(get_solution_orchestration_hub)
) -> Dict[str, Any]:
    """Get available solution orchestration capabilities."""
    try:
        capabilities = await solution_orchestration_hub.get_realm_capabilities()
        return capabilities
    except Exception as e:
        logger.error(f"Failed to get orchestration capabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orchestrate/initiators")
async def get_available_initiators(
    solution_orchestration_hub: SolutionOrchestrationHubService = Depends(get_solution_orchestration_hub)
) -> Dict[str, Any]:
    """Get available solution initiators."""
    try:
        initiators = await solution_orchestration_hub.get_available_initiators()
        return initiators
    except Exception as e:
        logger.error(f"Failed to get available initiators: {e}")
        raise HTTPException(status_code=500, detail=str(e))




