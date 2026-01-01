#!/usr/bin/env python3
"""
MVP Operations Pillar Router

Handles operations pillar (SOP, workflow generation).
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mvp/operations", tags=["MVP Operations"])

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mvp_content_router import (
    get_mvp_journey_orchestrator,
    get_business_orchestrator
)

@router.post("/sop/create")
async def create_sop(
    file_ids: List[str],
    sop_data: Dict[str, Any],
    user_id: str = "anonymous"
):
    """Generate SOP from files."""
    try:
        logger.info(f"📝 SOP creation request")
        
        mvp_journey = await get_mvp_journey_orchestrator()
        if mvp_journey:
            try:
                await mvp_journey.navigate_to_pillar("operations", {"user_id": user_id})
            except: pass
        
        business_orchestrator = await get_business_orchestrator()
        if business_orchestrator and hasattr(business_orchestrator, 'generate_sop'):
            result = await business_orchestrator.generate_sop(
                file_ids=file_ids,
                sop_data=sop_data,
                user_id=user_id
            )
        else:
            result = {
                "success": True,
                "sop_id": f"sop_{datetime.utcnow().timestamp()}",
                "sop_content": "Mock SOP content",
                "message": "SOP created (mock mode)"
            }
        
        if mvp_journey:
            try:
                await mvp_journey.update_pillar_progress("operations", {
                    "sop_generated": True
                })
            except: pass
        
        return result
        
    except Exception as e:
        logger.error(f"SOP creation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/create")
async def create_workflow(
    file_ids: List[str],
    workflow_data: Dict[str, Any],
    user_id: str = "anonymous"
):
    """Generate workflow from files."""
    try:
        logger.info(f"⚙️ Workflow creation request")
        
        business_orchestrator = await get_business_orchestrator()
        if business_orchestrator and hasattr(business_orchestrator, 'generate_workflow'):
            result = await business_orchestrator.generate_workflow(
                file_ids=file_ids,
                workflow_data=workflow_data,
                user_id=user_id
            )
        else:
            result = {
                "success": True,
                "workflow_id": f"workflow_{datetime.utcnow().timestamp()}",
                "workflow_content": "Mock workflow",
                "message": "Workflow created (mock mode)"
            }
        
        mvp_journey = await get_mvp_journey_orchestrator()
        if mvp_journey:
            try:
                await mvp_journey.update_pillar_progress("operations", {
                    "workflow_generated": True
                })
            except: pass
        
        return result
        
    except Exception as e:
        logger.error(f"Workflow creation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def operations_health():
    """Operations pillar health check."""
    return {"status": "healthy", "pillar": "operations"}


