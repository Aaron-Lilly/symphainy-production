#!/usr/bin/env python3
"""
Universal Pillar Router

Universal handler for ALL pillar requests with versioning support.
Routes: /api/v1/{pillar}/{path:path}

WHAT: Routes all pillar requests to FrontendGatewayService
HOW: FastAPI router that extracts request data and delegates to FrontendGatewayService
"""

from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from starlette.datastructures import UploadFile as StarletteUploadFile
from typing import Dict, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Universal Pillar API"])

_frontend_gateway = None

# FIX: Lazy initialization of route pattern from config
_route_pattern = None
_config_manager = None


def _get_api_prefix() -> str:
    """Get API prefix from configuration (lazy initialization)."""
    global _config_manager, _route_pattern
    
    if _route_pattern:
        return _route_pattern
    
    try:
        # Try to get from UnifiedConfigurationManager
        from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager
        from utilities.path_utils import get_project_root
        
        if not _config_manager:
            try:
                project_root = get_project_root()
            except RuntimeError:
                project_root = None
            
            _config_manager = UnifiedConfigurationManager(
                service_name="universal_router",
                config_root=str(project_root) if project_root else None
            )
        
        # Get API prefix from config (try multiple paths)
        api_prefix = (
            _config_manager.get("api_routing.full_prefix") or
            _config_manager.get("API_ROUTING_FULL_PREFIX") or
            _config_manager.get("api_routing.full_prefix") or
            "/api/v1"  # Fallback default
        )
        
        # Construct route pattern
        _route_pattern = f"{api_prefix}/{{pillar}}/{{path:path}}"
        logger.info(f"✅ API route pattern configured: {_route_pattern}")
        return _route_pattern
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to load API prefix from config: {e}, using default /api/v1")
        _route_pattern = "/api/v1/{pillar}/{path:path}"
        return _route_pattern


def set_frontend_gateway(gateway):
    """Inject FrontendGatewayService (dependency injection)."""
    global _frontend_gateway
    _frontend_gateway = gateway
    logger.info("✅ Universal router connected to Frontend Gateway Service")


def get_frontend_gateway():
    """Get FrontendGatewayService."""
    if not _frontend_gateway:
        raise HTTPException(
            status_code=503,
            detail="Frontend Gateway Service not initialized"
        )
    return _frontend_gateway


# FIX: Route pattern read from config
route_pattern = _get_api_prefix()

@router.api_route(
    route_pattern,  # ✅ From config
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def universal_pillar_handler(request: Request, pillar: str, path: str):
    """
    Universal handler for ALL pillar requests with versioning.
    
    Routes:
    - /api/v1/content-pillar/*           → ContentAnalysisOrchestrator
    - /api/v1/insights-pillar/*          → InsightsOrchestrator  
    - /api/v1/operations-pillar/*         → OperationsOrchestrator
    - /api/v1/business-outcomes-pillar/* → BusinessOutcomesOrchestrator
    
    All business logic is in FrontendGatewayService!
    """
    # CRITICAL: Log immediately to confirm handler is called
    print(f"[UNIVERSAL_ROUTER] Handler called: {request.method} /{pillar}/{path}")
    logger.info(f"[UNIVERSAL_ROUTER] Handler called: {request.method} /{pillar}/{path}")
    
    # ✅ SIMPLIFIED ROUTING: All routing now handled by FrontendGatewayService
    # FrontendGatewayService uses pillar-based direct routing to Journey Orchestrators
    # No need for direct route handlers here - gateway handles everything
    
    # Debug: Log Authorization header
    auth_header = request.headers.get("Authorization", "NOT_PRESENT")
    logger.info(f"[UNIVERSAL_ROUTER] Authorization header: {'PRESENT' if auth_header != 'NOT_PRESENT' else 'MISSING'} (length: {len(auth_header) if auth_header != 'NOT_PRESENT' else 0})")
    print(f"[UNIVERSAL_ROUTER] Authorization header: {'PRESENT' if auth_header != 'NOT_PRESENT' else 'MISSING'}")
    
    gateway = get_frontend_gateway()
    
    # Extract request data
    body = {}
    files = {}
    
    # Handle different content types
    content_type = request.headers.get("content-type", "").lower()
    print(f"[UNIVERSAL_ROUTER] Content-Type: {content_type}")
    logger.info(f"🌐 Request: {request.method} /{pillar}/{path}, Content-Type: {content_type}")
    
    # Debug logging for create-embeddings
    if "create-embeddings" in path:
        logger.info(f"🔍 [UNIVERSAL_ROUTER] create-embeddings request detected: {request.method} /{pillar}/{path}")
        print(f"[UNIVERSAL_ROUTER] 🔍 create-embeddings request detected: {request.method} /{pillar}/{path}")
    
    if request.method in ["POST", "PUT", "PATCH"]:
        if "multipart/form-data" in content_type:
            # Handle file uploads
            try:
                print("[UNIVERSAL_ROUTER] Parsing multipart/form-data...")
                logger.info("📋 Parsing multipart/form-data...")
                form_data = await request.form()
                print(f"[UNIVERSAL_ROUTER] Form data keys: {list(form_data.keys())}")
                logger.info(f"📋 Form data keys: {list(form_data.keys())}")
                # Extract form fields
                for key, value in form_data.items():
                    value_type = type(value)
                    value_type_name = value_type.__name__
                    value_type_module = value_type.__module__
                    logger.info(f"🔍 Processing form field: key='{key}', type={value_type_name}, module={value_type_module}")
                    
                    # Check if value is an UploadFile (either FastAPI or Starlette)
                    # Use duck-typing to be more robust: check for read() method and filename attribute
                    is_fastapi_upload = isinstance(value, UploadFile)
                    is_starlette_upload = isinstance(value, StarletteUploadFile)
                    has_read = hasattr(value, 'read')
                    has_filename = hasattr(value, 'filename')
                    read_callable = callable(getattr(value, 'read', None))
                    is_upload_file = is_fastapi_upload or is_starlette_upload or (has_read and has_filename and read_callable)
                    
                    logger.info(f"   → isinstance(value, UploadFile): {is_fastapi_upload}")
                    logger.info(f"   → isinstance(value, StarletteUploadFile): {is_starlette_upload}")
                    logger.info(f"   → hasattr(value, 'read'): {has_read}, hasattr(value, 'filename'): {has_filename}, callable(read): {read_callable}")
                    logger.info(f"   → is_upload_file: {is_upload_file}")
                    
                    if is_upload_file:
                        # Read file content (can only read once, so store it)
                        filename = getattr(value, 'filename', None) or f"unknown_{key}"
                        logger.info(f"📖 Reading file content for key='{key}', filename='{filename}'")
                        try:
                            file_content = await value.read()
                            logger.info(f"📖 File content read: type={type(file_content).__name__}, size={len(file_content) if file_content else 0} bytes")
                        except Exception as read_error:
                            logger.error(f"❌ Failed to read file content: {read_error}", exc_info=True)
                            file_content = None
                        
                        # Validate file content is not empty
                        if file_content is None:
                            logger.warning(f"⚠️ File '{key}' has no content (None) - filename: {filename}")
                        elif len(file_content) == 0:
                            logger.warning(f"⚠️ File '{key}' has empty content (0 bytes) - filename: {filename}")
                        else:
                            content_type = getattr(value, 'content_type', None) or "application/octet-stream"
                            files[key] = {
                                "filename": filename,
                                "content": file_content,
                                "content_type": content_type
                            }
                            logger.info(f"📎 Extracted file: key='{key}', filename='{filename}', size={len(file_content)} bytes")
                    else:
                        body[key] = value
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse multipart form data: {e}", exc_info=True)
                body = {}
        else:
            # Handle JSON body
            try:
                print(f"[UNIVERSAL_ROUTER] Attempting to read JSON body for {request.method} /{pillar}/{path}...")
                logger.info(f"📋 [UNIVERSAL_ROUTER] Reading JSON body for {request.method} /{pillar}/{path}...")
                
                # Check content-length to see if body is large
                content_length = request.headers.get("content-length")
                if content_length:
                    logger.info(f"📋 [UNIVERSAL_ROUTER] Content-Length: {content_length} bytes")
                    print(f"[UNIVERSAL_ROUTER] Content-Length: {content_length} bytes")
                
                # Add timeout to prevent hanging on large bodies
                import asyncio
                body = await asyncio.wait_for(
                    request.json(),
                    timeout=10.0  # JSON parsing should complete within 10 seconds
                )
                print(f"[UNIVERSAL_ROUTER] JSON body read successfully, keys: {list(body.keys()) if isinstance(body, dict) else 'not a dict'}")
                logger.info(f"📋 [UNIVERSAL_ROUTER] JSON body read: {len(str(body))} chars, keys: {list(body.keys()) if isinstance(body, dict) else 'not a dict'}")
            except asyncio.TimeoutError:
                logger.error(f"❌ [UNIVERSAL_ROUTER] JSON body read timed out after 10 seconds for {request.method} /{pillar}/{path}")
                print(f"[UNIVERSAL_ROUTER] ❌ JSON body read timed out")
                body = {}
            except Exception as e:
                logger.warning(f"⚠️ [UNIVERSAL_ROUTER] Failed to parse JSON body: {e}", exc_info=True)
                print(f"[UNIVERSAL_ROUTER] ⚠️ Failed to parse JSON body: {e}")
                body = {}
    
    # Extract headers
    headers = dict(request.headers)
    
    # Extract query parameters
    query_params = dict(request.query_params)
    
    # Extract user context from headers (from ForwardAuth if available)
    # ForwardAuth validates token and adds these headers:
    # - X-User-Id: Authenticated user ID
    # - X-Tenant-Id: User's tenant ID
    # - X-User-Roles: User's roles (comma-separated)
    # - X-User-Permissions: User's permissions (comma-separated)
    user_id = headers.get("X-User-Id") or headers.get("X-User-ID") or headers.get("x-user-id")
    tenant_id = headers.get("X-Tenant-Id") or headers.get("X-Tenant-ID") or headers.get("x-tenant-id")
    session_token = headers.get("X-Session-Token") or headers.get("x-session-token")
    
    # Extract roles and permissions from ForwardAuth headers
    user_roles_str = headers.get("X-User-Roles") or headers.get("X-User-Roles") or headers.get("x-user-roles") or ""
    user_permissions_str = headers.get("X-User-Permissions") or headers.get("X-User-Permissions") or headers.get("x-user-permissions") or ""
    user_roles = [r.strip() for r in user_roles_str.split(",") if r.strip()] if user_roles_str else []
    user_permissions = [p.strip() for p in user_permissions_str.split(",") if p.strip()] if user_permissions_str else []
    
    # Allow anonymous access for session creation endpoint (used to create sessions for unauthenticated users)
    # Path format: /api/v1/session/create-user-session -> pillar="session", path="create-user-session"
    is_session_creation = (pillar == "session" and path == "create-user-session")
    
    # SECURITY: If ForwardAuth headers are missing, validate token in handler
    # This provides backup authentication if ForwardAuth times out or fails
    # JWKS-based local validation is used for performance
    # EXCEPTION: Session creation endpoint allows anonymous access
    if not user_id and not is_session_creation:
        auth_header = headers.get("Authorization", "") or headers.get("authorization", "")
        logger.info(f"🔐 [AUTH_DEBUG] ForwardAuth headers missing. Checking Authorization header: {'PRESENT' if auth_header else 'MISSING'}")
        print(f"[AUTH_DEBUG] Authorization header: {'PRESENT' if auth_header else 'MISSING'}, length: {len(auth_header)}")
        
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "").strip()
            logger.info(f"🔐 [AUTH_DEBUG] Token extracted (length: {len(token)}). Starting JWKS validation...")
            print(f"[AUTH_DEBUG] Token extracted, length: {len(token)}, first 20 chars: {token[:20]}...")
            
            try:
                # Import here to avoid circular dependencies
                from backend.api.auth_router import get_security_guard
                logger.info("🔐 [AUTH_DEBUG] Getting Security Guard...")
                security_guard = await get_security_guard()
                
                if security_guard and hasattr(security_guard, 'get_auth_abstraction'):
                    logger.info("🔐 [AUTH_DEBUG] Security Guard has get_auth_abstraction method. Calling it...")
                    print("[AUTH_DEBUG] Security Guard has get_auth_abstraction method. Calling it...")
                    auth_abstraction = security_guard.get_auth_abstraction()
                    logger.info(f"🔐 [AUTH_DEBUG] get_auth_abstraction returned: {auth_abstraction is not None} (type: {type(auth_abstraction).__name__ if auth_abstraction else 'None'})")
                    print(f"[AUTH_DEBUG] get_auth_abstraction returned: {auth_abstraction is not None}")
                    if auth_abstraction:
                        logger.info("🔐 [AUTH_DEBUG] Security Guard and AuthAbstraction available. Calling validate_token (JWKS)...")
                        print("[AUTH_DEBUG] Calling AuthAbstraction.validate_token (uses JWKS)...")
                        
                        security_context = await auth_abstraction.validate_token(token)
                        
                        if security_context and security_context.user_id:
                            user_id = security_context.user_id
                            tenant_id = security_context.tenant_id or tenant_id
                            # Extract roles and permissions from security context
                            if security_context.roles:
                                user_roles = security_context.roles
                            if security_context.permissions:
                                user_permissions = security_context.permissions
                            
                            # Log permissions status for debugging
                            if not user_permissions:
                                self.logger.warning(f"⚠️ [AUTH_DEBUG] No permissions in security_context for user_id: {user_id}. This indicates _get_user_tenant_info() may have failed. Check logs for [TENANT_INFO] or [JWKS_DEBUG] messages.")
                            
                            logger.info(f"✅ [AUTH_DEBUG] JWKS validation succeeded: user_id={user_id}, tenant_id={tenant_id}, roles={user_roles}, permissions={user_permissions}")
                            print(f"[AUTH_DEBUG] ✅ JWKS validation succeeded: user_id={user_id}, permissions={user_permissions}")
                        else:
                            logger.error("❌ [AUTH_DEBUG] JWKS validation failed: security_context is None or missing user_id")
                            print("[AUTH_DEBUG] ❌ JWKS validation failed: invalid token or missing user_id")
                            raise HTTPException(status_code=401, detail="Unauthorized: Invalid token")
                    else:
                        logger.error("❌ [AUTH_DEBUG] Auth abstraction not available in Security Guard")
                        print("[AUTH_DEBUG] ❌ Auth abstraction not available")
                        raise HTTPException(status_code=503, detail="Service Unavailable: Authentication service not available")
                else:
                    logger.error("❌ [AUTH_DEBUG] Security Guard not available or missing get_auth_abstraction method")
                    print("[AUTH_DEBUG] ❌ Security Guard not available")
                    raise HTTPException(status_code=503, detail="Service Unavailable: Security Guard not available")
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"❌ [AUTH_DEBUG] Handler-level token validation error: {e}", exc_info=True)
                print(f"[AUTH_DEBUG] ❌ Exception during token validation: {type(e).__name__}: {e}")
                raise HTTPException(status_code=401, detail=f"Unauthorized: Token validation failed - {str(e)}")
        else:
            # No token provided - reject request
            logger.error(f"❌ [AUTH_DEBUG] No authentication provided: Authorization header format invalid (expected 'Bearer <token>', got: '{auth_header[:50]}...' if len(auth_header) > 50 else auth_header)")
            print(f"[AUTH_DEBUG] ❌ No valid Authorization header. Header value: '{auth_header[:50]}...' if len(auth_header) > 50 else auth_header")
            raise HTTPException(status_code=401, detail="Unauthorized: Authentication required")
    
    # Build request payload for FrontendGatewayService
    # ✅ SIMPLIFIED ROUTING: FrontendGatewayService now handles all routing via pillar-based routing
    # No need to extract path parameters here - gateway and orchestrators handle it
    api_prefix = _get_api_prefix().replace("/{pillar}/{path:path}", "")
    base_endpoint = f"{api_prefix}/{pillar}/{path}"
    
    # Path parameters are handled by gateway/orchestrators, so initialize as empty
    path_params = {}
    
    request_payload = {
        "endpoint": base_endpoint,
        "method": request.method,
        "params": {**body, **path_params},  # Merge body and path params
        "headers": headers,
        "user_id": user_id or "anonymous",  # Default to "anonymous" if no user_id (for session creation)
        "session_token": session_token,
        "query_params": query_params,
        # ✅ Add user context with permissions for downstream services
        "user_context": {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "roles": user_roles,
            "permissions": user_permissions,
            "session_id": session_token
        } if user_id else None
    }
    
    # Add file data if present
    if files:
        request_payload["files"] = files
        logger.info(f"📦 Files extracted: {list(files.keys())}")
        # Also add file info to params for backward compatibility
        for key, file_info in files.items():
            if key == "file":
                request_payload["params"]["file_data"] = file_info["content"]
                request_payload["params"]["filename"] = file_info["filename"]
                request_payload["params"]["content_type"] = file_info["content_type"]
                logger.info(f"✅ Main file added to params: filename='{file_info['filename']}', size={len(file_info['content'])} bytes")
            elif key == "copybook":
                request_payload["params"]["copybook_data"] = file_info["content"]
                request_payload["params"]["copybook_filename"] = file_info["filename"]
                logger.info(f"✅ Copybook file added to params: filename='{file_info['filename']}', size={len(file_info['content'])} bytes")
            else:
                logger.warning(f"⚠️ Unknown file key '{key}' - not adding to params (expected 'file' or 'copybook')")
        
        # Validate main file is present
        if "file_data" not in request_payload["params"]:
            logger.error(f"❌ Main file ('file') not found in form data! Available keys: {list(files.keys())}")
            return {
                "success": False,
                "error": "Main file ('file') is required but not found in upload",
                "available_files": list(files.keys())
            }
    
    # Route to gateway (all validation, transformation, orchestration happens there!)
    try:
        result = await gateway.route_frontend_request(request_payload)
        
        # Return result (FrontendGatewayService returns dict, FastAPI will serialize to JSON)
        return result
    except Exception as e:
        logger.error(f"❌ Error routing request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


