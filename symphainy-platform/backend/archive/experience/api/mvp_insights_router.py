#!/usr/bin/env python3
"""
MVP Insights Pillar Router

Handles insights pillar operations (data analysis, visualizations).
Routes through MVP Journey Orchestrator for tracking, executes via Business Orchestrator.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mvp/insights", tags=["MVP Insights"])

# Import shared helper functions from content router
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mvp_content_router import (
    set_platform_orchestrator,
    get_mvp_journey_orchestrator,
    get_business_orchestrator
)

@router.post("/analyze")
async def analyze_data(
    file_ids: List[str],
    analysis_type: str = "comprehensive",
    user_id: str = "anonymous"
):
    """Analyze data from uploaded files."""
    try:
        logger.info(f"📊 Analysis request for files: {file_ids}")
        
        # Navigate to insights pillar
        mvp_journey = await get_mvp_journey_orchestrator()
        if mvp_journey:
            try:
                await mvp_journey.navigate_to_pillar("insights", {"user_id": user_id})
            except Exception as e:
                logger.warning(f"Journey navigation failed: {e}")
        
        # Execute via Business Orchestrator
        business_orchestrator = await get_business_orchestrator()
        if business_orchestrator and hasattr(business_orchestrator, 'analyze_data'):
            result = await business_orchestrator.analyze_data(
                file_ids=file_ids,
                analysis_type=analysis_type,
                user_id=user_id
            )
        else:
            # Mock fallback
            result = {
                "success": True,
                "analysis_id": f"analysis_{datetime.utcnow().timestamp()}",
                "insights": ["Mock insight 1", "Mock insight 2"],
                "message": "Analysis complete (mock mode)"
            }
        
        # Update progress
        if mvp_journey:
            try:
                await mvp_journey.update_pillar_progress("insights", {
                    "analysis_complete": True,
                    "last_action": "analyze"
                })
            except: pass
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def insights_health():
    """Insights pillar health check."""
    return {"status": "healthy", "pillar": "insights"}


