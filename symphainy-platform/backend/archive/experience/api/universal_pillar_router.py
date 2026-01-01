#!/usr/bin/env python3
"""
Universal Pillar Router - Lightweight adapter for ALL pillars.

ONE router handles: Content, Insights, Operations, Business Outcomes
Extensible: Add new pillars by just registering them in FrontendGatewayService

Architecture:
    Frontend → Universal Router (50 lines) → FrontendGatewayService (REST translation) 
                                           → Orchestrators (domain capabilities)
                                           → Enabling Services (SOA APIs)

This file: 50 lines (replaces 2,900 lines of pillar-specific routers!)
"""

from fastapi import APIRouter, Request, HTTPException, status, UploadFile, File, Form
from typing import Optional
import logging
import base64

logger = logging.getLogger(__name__)

# ============================================================================
# UNIVERSAL ROUTER (Handles all pillars)
# ============================================================================

router = APIRouter(tags=["Universal Pillar API"])

_frontend_gateway = None


def set_frontend_gateway(gateway):
    """
    Inject FrontendGatewayService (dependency injection).
    
    Args:
        gateway: FrontendGatewayService instance
    """
    global _frontend_gateway
    _frontend_gateway = gateway
    logger.info("✅ Universal Pillar Router connected to Frontend Gateway Service")


def get_frontend_gateway():
    """
    Get FrontendGatewayService instance.
    
    Returns:
        FrontendGatewayService instance
    
    Raises:
        HTTPException: If gateway not initialized
    """
    if not _frontend_gateway:
        logger.error("❌ Frontend Gateway Service not initialized")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Frontend Gateway Service not initialized"
        )
    return _frontend_gateway


# ============================================================================
# FILE UPLOAD ENDPOINT (Special handling for multipart/form-data)
# ============================================================================

@router.post("/api/content/upload", name="content_file_upload")
async def content_file_upload(
    request: Request,
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None)
):
    """
    Handle file upload for Content Pillar (multipart/form-data).
    
    This endpoint specifically handles file uploads with multipart/form-data,
    which the universal handler can't process due to FastAPI limitations.
    """
    try:
        gateway = get_frontend_gateway()
        
        # Read file content and encode as base64
        file_content = await file.read()
        file_b64 = base64.b64encode(file_content).decode('utf-8')
        
        # Prepare request data
        frontend_request = {
            "endpoint": "/api/content/upload-file",
            "method": "POST",
            "params": {
                "filename": file.filename,
                "content": file_b64,
                "content_type": file.content_type,
                "user_id": user_id or "anonymous",
                "file_data": file_b64  # For backward compatibility
            }
        }
        
        # Route through gateway
        result = await gateway.route_frontend_request(frontend_request)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ File upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


# ============================================================================
# UNIVERSAL ENDPOINT (Handles all pillars + all paths)
# ============================================================================

@router.api_route(
    "/api/{pillar}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    name="universal_pillar_handler"
)
async def universal_pillar_handler(
    request: Request,
    pillar: str,
    path: str
):
    """
    Universal handler for ALL pillar requests.
    
    Supported pillars:
    - content            → ContentAnalysisOrchestrator
    - insights           → InsightsOrchestrator  
    - operations         → OperationsOrchestrator
    - business-outcomes  → BusinessOutcomesOrchestrator
    
    Routes:
    - /api/content/*           → Content Pillar endpoints
    - /api/insights/*          → Insights Pillar endpoints
    - /api/operations/*        → Operations Pillar endpoints
    - /api/business-outcomes/* → Business Outcomes Pillar endpoints
    
    All business logic (validation, transformation, orchestration) is in FrontendGatewayService!
    This router is just a thin HTTP adapter (protocol-specific handling only).
    
    Args:
        request: FastAPI request object
        pillar: Pillar name (content, insights, operations, business-outcomes)
        path: Endpoint path within pillar
    
    Returns:
        Response from FrontendGatewayService (already formatted for frontend)
    
    Example:
        POST /api/insights/analyze-content
        → gateway.route_frontend_request({
              "endpoint": "/api/insights/analyze-content",
              "method": "POST",
              "params": {...},
              "headers": {...}
          })
    """
    try:
        # Get Frontend Gateway Service (Frontend Enabler layer)
        gateway = get_frontend_gateway()
        
        # Extract request data (HTTP-specific handling)
        body = {}
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
            except Exception:
                # Empty body is OK for some requests
                body = {}
        
        # Build gateway request (protocol adapter → gateway translation)
        gateway_request = {
            "endpoint": f"/api/{pillar}/{path}",
            "method": request.method,
            "params": body,
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            # Extract common headers
            "user_id": request.headers.get("X-User-ID"),
            "session_token": request.headers.get("X-Session-Token")
        }
        
        # Route to gateway (all logic is there!)
        logger.info(f"📊 Routing {request.method} /api/{pillar}/{path}")
        result = await gateway.route_frontend_request(gateway_request)
        
        logger.info(f"✅ Request completed: /api/{pillar}/{path}")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions (from gateway not initialized, etc.)
        raise
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"❌ Universal router failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Request processing failed: {str(e)}"
        )


# ============================================================================
# HEALTH CHECK (Optional convenience endpoint)
# ============================================================================

@router.get("/api/health", name="universal_health_check")
async def health_check():
    """
    Health check for all pillars.
    
    Returns:
        Health status of gateway + all orchestrators
    """
    try:
        gateway = get_frontend_gateway()
        return await gateway.health_check()
    except HTTPException:
        return {
            "status": "unhealthy",
            "message": "Frontend Gateway Service not available",
            "pillars": {}
        }



