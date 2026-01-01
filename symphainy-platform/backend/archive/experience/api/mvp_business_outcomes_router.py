#!/usr/bin/env python3
"""
MVP Business Outcomes Pillar Router

Handles business outcomes pillar (roadmap, POC proposals).
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mvp/business-outcomes", tags=["MVP Business Outcomes"])

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mvp_content_router import (
    get_mvp_journey_orchestrator,
    get_business_orchestrator
)

@router.post("/roadmap/create")
async def create_roadmap(
    context_data: Dict[str, Any],
    user_id: str = "anonymous"
):
    """Generate strategic roadmap."""
    try:
        logger.info(f"🗺️ Roadmap creation request")
        
        mvp_journey = await get_mvp_journey_orchestrator()
        if mvp_journey:
            try:
                await mvp_journey.navigate_to_pillar("business_outcomes", {"user_id": user_id})
            except: pass
        
        business_orchestrator = await get_business_orchestrator()
        if business_orchestrator and hasattr(business_orchestrator, 'generate_roadmap'):
            result = await business_orchestrator.generate_roadmap(
                context_data=context_data,
                user_id=user_id
            )
        else:
            result = {
                "success": True,
                "roadmap_id": f"roadmap_{datetime.utcnow().timestamp()}",
                "roadmap": "Mock strategic roadmap",
                "message": "Roadmap created (mock mode)"
            }
        
        if mvp_journey:
            try:
                await mvp_journey.update_pillar_progress("business_outcomes", {
                    "roadmap_generated": True
                })
            except: pass
        
        return result
        
    except Exception as e:
        logger.error(f"Roadmap creation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/poc-proposal/create")
async def create_poc_proposal(
    context_data: Dict[str, Any],
    user_id: str = "anonymous"
):
    """Generate POC proposal."""
    try:
        logger.info(f"📋 POC proposal creation request")
        
        business_orchestrator = await get_business_orchestrator()
        if business_orchestrator and hasattr(business_orchestrator, 'generate_poc_proposal'):
            result = await business_orchestrator.generate_poc_proposal(
                context_data=context_data,
                user_id=user_id
            )
        else:
            result = {
                "success": True,
                "proposal_id": f"poc_{datetime.utcnow().timestamp()}",
                "proposal": "Mock POC proposal",
                "message": "POC proposal created (mock mode)"
            }
        
        mvp_journey = await get_mvp_journey_orchestrator()
        if mvp_journey:
            try:
                await mvp_journey.update_pillar_progress("business_outcomes", {
                    "poc_proposal_generated": True
                })
            except: pass
        
        return result
        
    except Exception as e:
        logger.error(f"POC proposal creation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def business_outcomes_health():
    """Business outcomes pillar health check."""
    return {"status": "healthy", "pillar": "business_outcomes"}


