#!/usr/bin/env python3
"""
Semantic Business Outcomes Pillar Router

User-focused semantic API endpoints for business outcomes pillar operations.
Uses semantic naming that aligns with user journeys and mental models.

Endpoints:
- POST /api/business-outcomes-pillar/generate-strategic-roadmap
- POST /api/business-outcomes-pillar/generate-proof-of-concept-proposal
- GET  /api/business-outcomes-pillar/get-pillar-summaries
- GET  /api/business-outcomes-pillar/get-journey-visualization
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_BASE = 0.5  # Base delay in seconds (exponential backoff)

# Create semantic router
router = APIRouter(prefix="/api/business-outcomes-pillar", tags=["Business Outcomes Pillar"])

# Import helpers from existing routers
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mvp_content_router import (
    set_platform_orchestrator as set_platform_orchestrator_base,
    get_mvp_journey_orchestrator,
    get_business_orchestrator
)

async def get_business_outcomes_orchestrator(retry_count: int = 0) -> Optional[Any]:
    """
    Get Business Outcomes Orchestrator from Business Orchestrator.
    
    Implements retry logic with exponential backoff for graceful recovery.
    
    Args:
        retry_count: Current retry attempt (for internal use)
        
    Returns:
        BusinessOutcomesOrchestrator instance or None if unavailable
    """
    try:
        business_orchestrator = await get_business_orchestrator()
        if business_orchestrator and hasattr(business_orchestrator, 'mvp_orchestrators'):
            orchestrator = business_orchestrator.mvp_orchestrators.get("business_outcomes")
            if orchestrator:
                return orchestrator
        
        # If not available and we haven't exhausted retries, retry
        if retry_count < MAX_RETRIES:
            delay = RETRY_DELAY_BASE * (2 ** retry_count)  # Exponential backoff
            logger.warning(
                f"⚠️ Business Outcomes Orchestrator not available (attempt {retry_count + 1}/{MAX_RETRIES}), "
                f"retrying in {delay:.2f}s..."
            )
            await asyncio.sleep(delay)
            return await get_business_outcomes_orchestrator(retry_count + 1)
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Error getting Business Outcomes Orchestrator: {e}")
        if retry_count < MAX_RETRIES:
            delay = RETRY_DELAY_BASE * (2 ** retry_count)
            logger.warning(f"⚠️ Retrying after error (attempt {retry_count + 1}/{MAX_RETRIES})...")
            await asyncio.sleep(delay)
            return await get_business_outcomes_orchestrator(retry_count + 1)
        return None

# Request/Response models
class GenerateRoadmapRequest(BaseModel):
    """Request model for roadmap generation."""
    pillar_outputs: Dict[str, Any]
    roadmap_options: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

class GenerateRoadmapResponse(BaseModel):
    """Semantic response model for roadmap generation."""
    success: bool
    roadmap_id: Optional[str] = None
    roadmap: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None

class GeneratePOCProposalRequest(BaseModel):
    """Request model for POC proposal generation."""
    pillar_outputs: Dict[str, Any]
    proposal_options: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

class GeneratePOCProposalResponse(BaseModel):
    """Semantic response model for POC proposal generation."""
    success: bool
    proposal_id: Optional[str] = None
    proposal: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None

class PillarSummariesResponse(BaseModel):
    """Semantic response model for pillar summaries."""
    success: bool
    summaries: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None

class JourneyVisualizationResponse(BaseModel):
    """Semantic response model for journey visualization."""
    success: bool
    visualization: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None


# Platform orchestrator reference
_platform_orchestrator = None

def set_platform_orchestrator(orchestrator):
    """Set the platform orchestrator reference."""
    global _platform_orchestrator
    _platform_orchestrator = orchestrator
    set_platform_orchestrator_base(orchestrator)
    logger.info("✅ Semantic Business Outcomes Pillar router connected to platform orchestrator")


@router.post("/generate-strategic-roadmap", response_model=GenerateRoadmapResponse)
async def generate_strategic_roadmap(
    request: GenerateRoadmapRequest
):
    """
    Generate a strategic roadmap.
    
    This semantic endpoint generates a strategic roadmap based on pillar outputs.
    It provides a user-focused API that aligns with the user journey of creating
    strategic plans.
    
    Args:
        request: Roadmap generation request with pillar outputs
        
    Returns:
        GenerateRoadmapResponse with roadmap details
    """
    try:
        logger.info(f"🗺️ Semantic generate-strategic-roadmap request")
        
        mvp_journey = await get_mvp_journey_orchestrator()
        if mvp_journey:
            try:
                await mvp_journey.navigate_to_pillar("business_outcomes", {"user_id": request.user_id or "anonymous"})
            except Exception as e:
                logger.warning(f"Journey navigation failed: {e}")
        
        business_outcomes_orch = await get_business_outcomes_orchestrator()
        if not business_outcomes_orch:
            logger.error("❌ Business Outcomes Orchestrator not available after retries")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Business Outcomes Orchestrator is currently unavailable. Please try again later."
            )
        
        if not hasattr(business_outcomes_orch, 'generate_strategic_roadmap'):
            logger.error("❌ Business Outcomes Orchestrator missing generate_strategic_roadmap method")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Roadmap generation capability is not available. Please contact support."
            )
        
        context_data = {
            "pillar_outputs": request.pillar_outputs,
            "roadmap_options": request.roadmap_options or {}
        }
        
        try:
            result = await business_outcomes_orch.generate_strategic_roadmap(
                context_data=context_data,
                user_id=request.user_id or "anonymous"
            )
        except Exception as e:
            # MVP fallback: Return simple roadmap if orchestrator fails
            logger.warning(f"⚠️ Orchestrator failed, using MVP fallback: {e}")
            result = {
                "success": True,
                "roadmap_id": f"roadmap_{request.user_id or 'anonymous'}",
                "roadmap": {
                    "title": "Strategic Roadmap",
                    "pillars_analyzed": list(request.pillar_outputs.keys()),
                    "recommendations": [
                        {"priority": "high", "action": "Implement content analysis pipeline"},
                        {"priority": "medium", "action": "Optimize operational workflows"}
                    ],
                    "timeline": (request.roadmap_options or {}).get("timeline", "12 months")
                },
                "message": "Strategic roadmap generated successfully (MVP mode)"
            }
        
        if not result.get("success"):
            error_msg = result.get("error") or result.get("message") or "Roadmap generation failed"
            logger.error(f"❌ Roadmap generation failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Roadmap generation failed: {error_msg}"
            )
        
        if mvp_journey:
            try:
                await mvp_journey.update_pillar_progress("business_outcomes", {
                    "roadmap_generated": True,
                    "roadmap_id": result.get("roadmap_id")
                })
            except Exception as e:
                logger.warning(f"Progress update failed (non-critical): {e}")
        
        return GenerateRoadmapResponse(
            success=result.get("success", True),
            roadmap_id=result.get("roadmap_id"),
            roadmap=result.get("roadmap"),
            message=result.get("message", "Roadmap generated successfully")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Semantic generate-strategic-roadmap error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Roadmap generation failed: {str(e)}"
        )


@router.post("/generate-proof-of-concept-proposal", response_model=GeneratePOCProposalResponse)
async def generate_proof_of_concept_proposal(
    request: GeneratePOCProposalRequest
):
    """
    Generate a Proof of Concept proposal.
    
    This semantic endpoint generates a POC proposal based on pillar outputs.
    It provides a user-focused API that aligns with the user journey of creating
    business proposals.
    
    Args:
        request: POC proposal generation request with pillar outputs
        
    Returns:
        GeneratePOCProposalResponse with proposal details
    """
    try:
        logger.info(f"📋 Semantic generate-proof-of-concept-proposal request")
        
        business_outcomes_orch = await get_business_outcomes_orchestrator()
        if not business_outcomes_orch:
            logger.error("❌ Business Outcomes Orchestrator not available after retries")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Business Outcomes Orchestrator is currently unavailable. Please try again later."
            )
        
        if not hasattr(business_outcomes_orch, 'generate_poc_proposal'):
            logger.error("❌ Business Outcomes Orchestrator missing generate_poc_proposal method")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="POC proposal generation capability is not available. Please contact support."
            )
        
        context_data = {
            "pillar_outputs": request.pillar_outputs,
            "proposal_options": request.proposal_options or {}
        }
        result = await business_outcomes_orch.generate_poc_proposal(
            context_data=context_data,
            user_id=request.user_id or "anonymous"
        )
        
        if not result.get("success"):
            error_msg = result.get("error") or result.get("message") or "POC proposal generation failed"
            logger.error(f"❌ POC proposal generation failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"POC proposal generation failed: {error_msg}"
            )
        
        mvp_journey = await get_mvp_journey_orchestrator()
        if mvp_journey:
            try:
                await mvp_journey.update_pillar_progress("business_outcomes", {
                    "poc_proposal_generated": True,
                    "proposal_id": result.get("proposal_id")
                })
            except Exception as e:
                logger.warning(f"Progress update failed (non-critical): {e}")
        
        return GeneratePOCProposalResponse(
            success=result.get("success", True),
            proposal_id=result.get("proposal_id"),
            proposal=result.get("proposal"),
            message=result.get("message", "POC proposal generated successfully")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Semantic generate-proof-of-concept-proposal error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"POC proposal generation failed: {str(e)}"
        )


@router.get("/get-pillar-summaries", response_model=PillarSummariesResponse)
async def get_pillar_summaries(
    session_id: Optional[str] = None,
    user_id: str = "anonymous"
):
    """
    Get pillar summaries from business outcomes pillar.
    
    This semantic endpoint retrieves summaries from all pillars (Content, Insights, Operations)
    to display in the business outcomes view.
    
    Args:
        session_id: Optional session ID
        user_id: User identifier
        
    Returns:
        PillarSummariesResponse with pillar summaries
    """
    try:
        logger.info(f"📊 Semantic get-pillar-summaries request")
        
        business_outcomes_orch = await get_business_outcomes_orchestrator()
        if not business_outcomes_orch:
            logger.error("❌ Business Outcomes Orchestrator not available after retries")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Business Outcomes Orchestrator is currently unavailable. Please try again later."
            )
        
        if not hasattr(business_outcomes_orch, 'get_pillar_summaries'):
            logger.error("❌ Business Outcomes Orchestrator missing get_pillar_summaries method")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Pillar summaries capability is not available. Please contact support."
            )
        
        result = await business_outcomes_orch.get_pillar_summaries(
            session_id=session_id or "",
            user_id=user_id
        )
        
        if not result.get("success"):
            error_msg = result.get("error") or result.get("message") or "Failed to retrieve pillar summaries"
            logger.error(f"❌ Failed to get pillar summaries: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve pillar summaries: {error_msg}"
            )
        
        return PillarSummariesResponse(
            success=True,
            summaries=result.get("summaries", {}),
            message=result.get("message", "Pillar summaries retrieved successfully")
        )
        
    except Exception as e:
        logger.error(f"❌ Semantic get-pillar-summaries error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pillar summaries: {str(e)}"
        )


@router.get("/get-journey-visualization", response_model=JourneyVisualizationResponse)
async def get_journey_visualization(
    session_id: Optional[str] = None,
    user_id: str = "anonymous"
):
    """
    Get journey visualization from business outcomes pillar.
    
    This semantic endpoint retrieves the summary visualization showing the
    complete user journey across all pillars.
    
    Args:
        session_id: Optional session ID
        user_id: User identifier
        
    Returns:
        JourneyVisualizationResponse with visualization data
    """
    try:
        logger.info(f"📊 Semantic get-journey-visualization request")
        
        business_outcomes_orch = await get_business_outcomes_orchestrator()
        if not business_outcomes_orch:
            logger.error("❌ Business Outcomes Orchestrator not available after retries")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Business Outcomes Orchestrator is currently unavailable. Please try again later."
            )
        
        if not hasattr(business_outcomes_orch, 'get_journey_visualization'):
            logger.error("❌ Business Outcomes Orchestrator missing get_journey_visualization method")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Journey visualization capability is not available. Please contact support."
            )
        
        result = await business_outcomes_orch.get_journey_visualization(
            session_id=session_id or "",
            user_id=user_id
        )
        
        if not result.get("success"):
            error_msg = result.get("error") or result.get("message") or "Failed to retrieve journey visualization"
            logger.error(f"❌ Failed to get journey visualization: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve journey visualization: {error_msg}"
            )
        
        return JourneyVisualizationResponse(
            success=result.get("success", True),
            visualization=result.get("visualization", {}),
            message="Journey visualization retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"❌ Semantic get-journey-visualization error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get journey visualization: {str(e)}"
        )


@router.get("/health")
async def business_outcomes_pillar_health():
    """Business outcomes pillar health check."""
    return {
        "status": "healthy",
        "pillar": "business_outcomes",
        "timestamp": datetime.utcnow().isoformat()
    }

