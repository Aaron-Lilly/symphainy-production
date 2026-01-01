#!/usr/bin/env python3
"""
Client Collaboration API Router

FastAPI router for client collaboration endpoints (artifact sharing, review, approval).

WHAT: Provides REST API endpoints for client artifact collaboration
HOW: FastAPI router that delegates to ClientCollaborationService
"""

from fastapi import APIRouter, HTTPException, status, Request, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/client-collaboration", tags=["Client Collaboration"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ShareArtifactRequest(BaseModel):
    """Request model for sharing artifact with client."""
    artifact_id: str
    artifact_type: str  # "solution" or "journey"
    client_id: str


class ShareArtifactResponse(BaseModel):
    """Response model for sharing artifact."""
    success: bool
    artifact_id: str
    artifact_type: str
    client_id: str
    status: str
    shared_at: str
    message: Optional[str] = None
    error: Optional[str] = None


class AddCommentRequest(BaseModel):
    """Request model for adding comment to artifact."""
    comment: str
    section: Optional[str] = None
    user: Optional[str] = None
    artifact_type: str  # "solution" or "journey"
    client_id: str


class AddCommentResponse(BaseModel):
    """Response model for adding comment."""
    success: bool
    artifact_id: str
    comment: Dict[str, Any]
    total_comments: int
    message: Optional[str] = None
    error: Optional[str] = None


class ApproveArtifactRequest(BaseModel):
    """Request model for approving artifact."""
    client_id: str
    artifact_type: str  # "solution" or "journey"


class ApproveArtifactResponse(BaseModel):
    """Response model for approving artifact."""
    success: bool
    artifact_id: str
    artifact_type: str
    client_id: str
    status: str
    approved_at: str
    message: Optional[str] = None
    error: Optional[str] = None


class RejectArtifactRequest(BaseModel):
    """Request model for rejecting artifact."""
    client_id: str
    rejection_reason: str
    artifact_type: str  # "solution" or "journey"


class RejectArtifactResponse(BaseModel):
    """Response model for rejecting artifact."""
    success: bool
    artifact_id: str
    artifact_type: str
    client_id: str
    status: str
    rejection_reason: str
    rejected_at: str
    message: Optional[str] = None
    error: Optional[str] = None


class ClientArtifactsResponse(BaseModel):
    """Response model for getting client artifacts."""
    success: bool
    client_id: str
    artifacts: Dict[str, Any]
    count: int
    filters: Dict[str, Optional[str]]
    message: Optional[str] = None
    error: Optional[str] = None


# ============================================================================
# GLOBAL STATE FOR SERVICE ACCESS
# ============================================================================

_client_collaboration_service = None


def set_client_collaboration_service(service: Any):
    """Set ClientCollaborationService (called during router registration)."""
    global _client_collaboration_service
    _client_collaboration_service = service
    logger.info("✅ ClientCollaborationService set in router")


async def get_client_collaboration_service():
    """
    Get ClientCollaborationService instance via service discovery.
    
    Uses Curator Foundation for service discovery.
    """
    global _client_collaboration_service
    
    # Use cached instance if available
    if _client_collaboration_service:
        return _client_collaboration_service
    
    # Try to discover via Curator
    try:
        from utilities.service_discovery.curator import Curator
        curator = Curator()
        service = await curator.get_service("ClientCollaborationService")
        if service:
            _client_collaboration_service = service
            logger.info("✅ ClientCollaborationService retrieved via Curator")
            return service
    except Exception as e:
        logger.warning(f"⚠️ Curator lookup failed: {e}")
    
    logger.error("❌ ClientCollaborationService not available")
    return None


def extract_user_context(request: Request) -> Dict[str, Any]:
    """
    Extract user context from request headers.
    
    Headers set by ForwardAuth:
    - X-User-Id
    - X-Tenant-Id
    - X-User-Email
    - X-User-Roles
    - X-User-Permissions
    """
    return {
        "user_id": request.headers.get("X-User-Id"),
        "tenant_id": request.headers.get("X-Tenant-Id"),
        "email": request.headers.get("X-User-Email"),
        "roles": request.headers.get("X-User-Roles", "").split(",") if request.headers.get("X-User-Roles") else [],
        "permissions": request.headers.get("X-User-Permissions", "").split(",") if request.headers.get("X-User-Permissions") else [],
        "session_id": request.headers.get("X-Session-Id")
    }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/share-artifact", response_model=ShareArtifactResponse, status_code=status.HTTP_200_OK)
async def share_artifact_with_client(request: ShareArtifactRequest, http_request: Request):
    """
    Share artifact with client for review.
    
    Updates artifact status: "draft" → "review"
    """
    try:
        logger.info(f"📤 Sharing artifact {request.artifact_id} with client {request.client_id}")
        
        service = await get_client_collaboration_service()
        if not service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ClientCollaborationService not available"
            )
        
        user_context = extract_user_context(http_request)
        
        result = await service.share_artifact_with_client(
            artifact_id=request.artifact_id,
            artifact_type=request.artifact_type,
            client_id=request.client_id,
            user_context=user_context
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to share artifact")
            )
        
        return ShareArtifactResponse(
            success=True,
            artifact_id=result["artifact_id"],
            artifact_type=result["artifact_type"],
            client_id=result["client_id"],
            status=result["status"],
            shared_at=result["shared_at"],
            message="Artifact shared successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Share artifact error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to share artifact: {str(e)}"
        )


@router.get("/client/{client_id}/artifacts", response_model=ClientArtifactsResponse)
async def get_client_artifacts(
    client_id: str,
    artifact_type: Optional[str] = Query(None, description="Filter by artifact type (solution or journey)"),
    status: Optional[str] = Query(None, description="Filter by status (draft, review, approved, etc.)"),
    http_request: Request = None
):
    """
    Get all artifacts for a client (with optional filters).
    
    Used by client UI to display artifacts for review.
    """
    try:
        logger.info(f"📋 Getting artifacts for client {client_id} (type: {artifact_type}, status: {status})")
        
        service = await get_client_collaboration_service()
        if not service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ClientCollaborationService not available"
            )
        
        user_context = extract_user_context(http_request) if http_request else {}
        
        result = await service.get_client_artifacts(
            client_id=client_id,
            artifact_type=artifact_type,
            status=status,
            user_context=user_context
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to get client artifacts")
            )
        
        return ClientArtifactsResponse(
            success=True,
            client_id=result["client_id"],
            artifacts=result["artifacts"],
            count=result["count"],
            filters=result["filters"],
            message="Artifacts retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get client artifacts error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get client artifacts: {str(e)}"
        )


@router.post("/artifacts/{artifact_id}/comments", response_model=AddCommentResponse, status_code=status.HTTP_201_CREATED)
async def add_client_comment(
    artifact_id: str,
    request: AddCommentRequest,
    http_request: Request = None
):
    """
    Add client comment to artifact.
    
    Comments are stored with artifact and tracked with metadata.
    """
    try:
        logger.info(f"💬 Adding comment to artifact {artifact_id} by client {request.client_id}")
        
        service = await get_client_collaboration_service()
        if not service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ClientCollaborationService not available"
            )
        
        user_context = extract_user_context(http_request) if http_request else {}
        
        comment_data = {
            "comment": request.comment,
            "section": request.section,
            "user": request.user or user_context.get("user_id")
        }
        
        result = await service.add_client_comment(
            artifact_id=artifact_id,
            artifact_type=request.artifact_type,
            comment=comment_data,
            client_id=request.client_id,
            user_context=user_context
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to add comment")
            )
        
        return AddCommentResponse(
            success=True,
            artifact_id=result["artifact_id"],
            comment=result["comment"],
            total_comments=result["total_comments"],
            message="Comment added successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Add comment error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add comment: {str(e)}"
        )


@router.post("/artifacts/{artifact_id}/approve", response_model=ApproveArtifactResponse)
async def approve_artifact(
    artifact_id: str,
    request: ApproveArtifactRequest,
    http_request: Request = None
):
    """
    Client approves artifact.
    
    Updates artifact status: "review" → "approved"
    """
    try:
        logger.info(f"✅ Approving artifact {artifact_id} by client {request.client_id}")
        
        service = await get_client_collaboration_service()
        if not service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ClientCollaborationService not available"
            )
        
        user_context = extract_user_context(http_request) if http_request else {}
        
        result = await service.approve_artifact(
            artifact_id=artifact_id,
            artifact_type=request.artifact_type,
            client_id=request.client_id,
            user_context=user_context
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to approve artifact")
            )
        
        return ApproveArtifactResponse(
            success=True,
            artifact_id=result["artifact_id"],
            artifact_type=result["artifact_type"],
            client_id=result["client_id"],
            status=result["status"],
            approved_at=result["approved_at"],
            message="Artifact approved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Approve artifact error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve artifact: {str(e)}"
        )


@router.post("/artifacts/{artifact_id}/reject", response_model=RejectArtifactResponse)
async def reject_artifact(
    artifact_id: str,
    request: RejectArtifactRequest,
    http_request: Request = None
):
    """
    Client rejects artifact.
    
    Updates artifact status: "review" → "draft"
    Adds rejection reason as comment.
    """
    try:
        logger.info(f"❌ Rejecting artifact {artifact_id} by client {request.client_id}: {request.rejection_reason}")
        
        service = await get_client_collaboration_service()
        if not service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ClientCollaborationService not available"
            )
        
        user_context = extract_user_context(http_request) if http_request else {}
        
        result = await service.reject_artifact(
            artifact_id=artifact_id,
            artifact_type=request.artifact_type,
            rejection_reason=request.rejection_reason,
            client_id=request.client_id,
            user_context=user_context
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to reject artifact")
            )
        
        return RejectArtifactResponse(
            success=True,
            artifact_id=result["artifact_id"],
            artifact_type=result["artifact_type"],
            client_id=result["client_id"],
            status=result["status"],
            rejection_reason=result["rejection_reason"],
            rejected_at=result["rejected_at"],
            message="Artifact rejected successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Reject artifact error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject artifact: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for client collaboration API."""
    service = await get_client_collaboration_service()
    if not service:
        return {
            "status": "unhealthy",
            "service": "ClientCollaborationService",
            "message": "Service not available"
        }
    
    health = await service.health_check()
    return health

