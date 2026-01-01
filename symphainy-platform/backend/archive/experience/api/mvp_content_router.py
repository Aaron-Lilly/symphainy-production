#!/usr/bin/env python3
"""
MVP Content Pillar Router

Handles content pillar operations (file upload, parsing, listing).
Routes through MVP Journey Orchestrator for tracking, executes via Business Orchestrator.
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/mvp/content", tags=["MVP Content"])

# Request/Response models
class FileUploadResponse(BaseModel):
    success: bool
    file_id: Optional[str] = None
    filename: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

class FileListResponse(BaseModel):
    success: bool
    files: List[Dict[str, Any]] = []
    count: int = 0


# Platform orchestrator reference
_platform_orchestrator = None

def set_platform_orchestrator(orchestrator):
    """Set the platform orchestrator reference."""
    global _platform_orchestrator
    _platform_orchestrator = orchestrator
    logger.info("✅ MVP Content router connected to platform orchestrator")


def get_managers():
    """Get all required managers from platform orchestrator."""
    if not _platform_orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Platform not initialized"
        )
    
    city_manager = _platform_orchestrator.managers.get("city_manager")
    if not city_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="City Manager not available"
        )
    
    # Get Journey Manager
    journey_manager = city_manager.manager_hierarchy.get("journey_manager", {}).get("instance")
    
    # Get Delivery Manager  
    delivery_manager = city_manager.manager_hierarchy.get("delivery_manager", {}).get("instance")
    
    return {
        "city": city_manager,
        "journey": journey_manager,
        "delivery": delivery_manager
    }


async def get_mvp_journey_orchestrator():
    """Get MVP Journey Orchestrator from Journey Manager."""
    try:
        managers = get_managers()
        journey_manager = managers.get("journey")
        
        if not journey_manager:
            logger.warning("Journey Manager not available")
            return None
        
        # Try to get MVP Journey Orchestrator
        mvp_orchestrator = getattr(journey_manager, 'mvp_journey_orchestrator', None)
        if mvp_orchestrator:
            logger.info("✅ Retrieved MVP Journey Orchestrator")
            return mvp_orchestrator
        
        # Fallback: Check if it's in discovered services
        di_container = _platform_orchestrator.infrastructure_services.get("di_container")
        if di_container:
            mvp_orchestrator = di_container.service_registry.get("MVPJourneyOrchestratorService")
            if mvp_orchestrator:
                logger.info("✅ Retrieved MVP Journey Orchestrator from DI container")
                return mvp_orchestrator
        
        logger.warning("MVP Journey Orchestrator not available")
        return None
        
    except Exception as e:
        logger.error(f"Error getting MVP Journey Orchestrator: {e}")
        return None


async def get_business_orchestrator():
    """
    Get Business Orchestrator with lazy loading.
    
    Business Orchestrator is registered in DI container during platform startup.
    Falls back to Delivery Manager if not found in DI container.
    """
    try:
        if not _platform_orchestrator:
            logger.warning("Platform Orchestrator not available")
            return None
        
        # FIRST: Check DI container (primary location after main_api.py initialization)
        di_container = _platform_orchestrator.infrastructure_services.get("di_container")
        if di_container:
            business_orchestrator = di_container.service_registry.get("BusinessOrchestratorService")
            if business_orchestrator:
                logger.debug("✅ Retrieved Business Orchestrator from DI container")
                return business_orchestrator
        
        # SECOND: Check if Business Orchestrator is directly stored (legacy pattern)
        business_orchestrator = _platform_orchestrator.managers.get("business_orchestrator")
        if business_orchestrator:
            logger.debug("✅ Retrieved Business Orchestrator from Platform Orchestrator (legacy)")
            return business_orchestrator
        
        # THIRD: Try to get via Delivery Manager (architectural pattern)
        delivery_manager = None
        if di_container:
            delivery_manager = di_container.service_registry.get("DeliveryManagerService")
        
        if delivery_manager and hasattr(delivery_manager, 'get_business_orchestrator'):
            business_orchestrator = await delivery_manager.get_business_orchestrator()
            if business_orchestrator:
                logger.info("✅ Retrieved Business Orchestrator from Delivery Manager (lazy-loaded)")
                logger.info(f"🔍 get_business_orchestrator: mvp_orchestrators keys: {list(business_orchestrator.mvp_orchestrators.keys()) if hasattr(business_orchestrator, 'mvp_orchestrators') else 'N/A'}")
                logger.info(f"🔍 get_business_orchestrator: mvp_orchestrators count: {len(business_orchestrator.mvp_orchestrators) if hasattr(business_orchestrator, 'mvp_orchestrators') else 0}")
                return business_orchestrator
        
        # FOURTH: Check if stored directly in Delivery Manager
        if delivery_manager and hasattr(delivery_manager, 'business_orchestrator') and delivery_manager.business_orchestrator:
            business_orchestrator = delivery_manager.business_orchestrator
            logger.info("✅ Retrieved Business Orchestrator from Delivery Manager (direct)")
            return business_orchestrator
        
        logger.warning("⚠️ Business Orchestrator not available (not initialized yet?)")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error getting Business Orchestrator: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


async def get_session_manager():
    """Get Session Manager service."""
    try:
        if not _platform_orchestrator:
            return None
        
        city_manager = _platform_orchestrator.managers.get("city_manager")
        if not city_manager:
            return None
        
        # Try to get Session Manager from Experience Manager
        experience_manager = city_manager.manager_hierarchy.get("experience_manager", {}).get("instance")
        if experience_manager:
            session_manager = getattr(experience_manager, 'session_manager', None)
            if session_manager:
                logger.info("✅ Retrieved Session Manager from Experience Manager")
                return session_manager
        
        # Fallback: Try DI container
        di_container = _platform_orchestrator.infrastructure_services.get("di_container")
        if di_container:
            session_manager = di_container.service_registry.get("SessionManager")
            if session_manager:
                logger.info("✅ Retrieved Session Manager from DI container")
                return session_manager
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting Session Manager: {e}")
        return None


async def get_session_id_from_token(session_token: Optional[str] = None) -> Optional[str]:
    """
    Get session_id from session_token.
    
    If session_token is None, creates a new session.
    """
    if not session_token:
        # Create new session
        session_manager = await get_session_manager()
        if session_manager:
            result = await session_manager.create_session(
                user_id="anonymous",
                context={}
            )
            if result.get("success"):
                return result.get("session", {}).get("session_id")
        return None
    
    # Try to find session by token
    session_manager = await get_session_manager()
    if session_manager:
        # Try to get session - if it exists, return session_id
        result = await session_manager.get_session(session_token)
        if result.get("success"):
            return session_token
    
    # If not found, create new session
    if session_manager:
        result = await session_manager.create_session(
            user_id="anonymous",
            context={}
        )
        if result.get("success"):
            return result.get("session", {}).get("session_id")
    
    return None


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Form(default="anonymous"),
    session_token: Optional[str] = Header(None, alias="X-Session-Token")  # NEW: Get session from header
):
    """
    Upload a file for content analysis.
    
    Flow:
    1. Navigate to content pillar (journey tracking)
    2. Execute upload via Business Orchestrator
    3. Update pillar progress
    4. Return result
    """
    try:
        logger.info(f"📤 File upload request: {file.filename} from user: {user_id}")
        
        # Read file data
        file_data = await file.read()
        file_size = len(file_data)
        
        logger.info(f"File size: {file_size} bytes, content type: {file.content_type}")
        
        # Step 1: Navigate to content pillar (journey tracking)
        mvp_journey = await get_mvp_journey_orchestrator()
        if mvp_journey and hasattr(mvp_journey, 'navigate_to_pillar'):
            try:
                await mvp_journey.navigate_to_pillar("content", {"user_id": user_id})
                logger.info("✅ Navigated to content pillar")
            except Exception as e:
                logger.warning(f"Journey navigation failed (non-critical): {e}")
        
        # Get session_id from session_token
        session_id = await get_session_id_from_token(session_token)
        
        # Step 2: Execute upload via Business Orchestrator
        business_orchestrator = await get_business_orchestrator()
        
        if business_orchestrator and hasattr(business_orchestrator, 'handle_content_upload'):
            logger.info("Using Business Orchestrator delegation method for file upload")
            
            # Use Business Orchestrator's delegation method (encapsulates orchestrator access)
            result = await business_orchestrator.handle_content_upload(
                file_data=file_data,
                filename=file.filename,
                file_type=file.content_type,
                user_id=user_id,
                session_id=session_id  # Pass session_id for workflow tracking
            )
            
            file_id = result.get("file_id")
            
        else:
            # Fail-fast: Business Orchestrator must be available
            logger.error("❌ Business Orchestrator not available - service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Business Orchestrator not available - service not initialized. Cannot upload files."
            )
        
        # Step 3: Update pillar progress
        if mvp_journey and hasattr(mvp_journey, 'update_pillar_progress'):
            try:
                await mvp_journey.update_pillar_progress("content", {
                    "files_uploaded": True,
                    "last_file_id": file_id,
                    "last_action": "upload",
                    "uploaded_at": datetime.utcnow().isoformat()
                })
                logger.info("✅ Updated content pillar progress")
            except Exception as e:
                logger.warning(f"Progress update failed (non-critical): {e}")
        
        # Step 4: Return result
        return FileUploadResponse(
            success=True,
            file_id=file_id,
            filename=file.filename,
            message=result.get("message", "File uploaded successfully")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ File upload error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/files", response_model=FileListResponse)
async def list_files(user_id: str = "anonymous"):
    """
    List all files for a user.
    
    Returns files uploaded by the user.
    """
    try:
        logger.info(f"📋 List files request for user: {user_id}")
        
        business_orchestrator = await get_business_orchestrator()
        
        if business_orchestrator and hasattr(business_orchestrator, 'list_user_files'):
            logger.info("Using Business Orchestrator for file listing")
            result = await business_orchestrator.list_user_files(user_id=user_id)
            
            files = result.get("files", [])
            
            return FileListResponse(
                success=True,
                files=files,
                count=len(files)
            )
        
        # Fail-fast: Business Orchestrator must be available
        logger.error("❌ Business Orchestrator not available - service not initialized")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Business Orchestrator not available - service not initialized. Cannot list files."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ List files error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"List files failed: {str(e)}"
        )


@router.post("/parse/{file_id}")
async def parse_file(file_id: str, user_id: str = "anonymous"):
    """
    Parse a previously uploaded file.
    
    Flow:
    1. Execute parsing via Business Orchestrator
    2. Update pillar progress
    3. Return result
    """
    try:
        logger.info(f"🔍 Parse file request: {file_id} from user: {user_id}")
        
        business_orchestrator = await get_business_orchestrator()
        
        if business_orchestrator and hasattr(business_orchestrator, 'parse_file'):
            logger.info("Using Business Orchestrator for file parsing")
            result = await business_orchestrator.parse_file(
                file_id=file_id,
                user_id=user_id
            )
        else:
            # Fail-fast: Business Orchestrator must be available
            logger.error("❌ Business Orchestrator not available - service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Business Orchestrator not available - service not initialized. Cannot parse files."
            )
        
        # Update pillar progress
        mvp_journey = await get_mvp_journey_orchestrator()
        if mvp_journey and hasattr(mvp_journey, 'update_pillar_progress'):
            try:
                await mvp_journey.update_pillar_progress("content", {
                    "files_parsed": True,
                    "last_parsed_file_id": file_id,
                    "last_action": "parse",
                    "parsed_at": datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.warning(f"Progress update failed (non-critical): {e}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Parse file error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File parsing failed: {str(e)}"
        )


@router.get("/health")
async def content_health():
    """Content pillar health check."""
    mvp_journey = await get_mvp_journey_orchestrator()
    business_orchestrator = await get_business_orchestrator()
    
    return {
        "status": "healthy",
        "pillar": "content",
        "mvp_journey_available": mvp_journey is not None,
        "business_orchestrator_available": business_orchestrator is not None,
        "mode": "production" if business_orchestrator else "mock"
    }


