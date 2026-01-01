#!/usr/bin/env python3
"""
Authentication Module - Security Guard Service

Handles authentication and authorization operations.
"""

import uuid
from typing import Dict, Any
from datetime import datetime


class Authentication:
    """Authentication module for Security Guard Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def authenticate_user(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate user credentials with full orchestration.
        
        Enhanced with:
        - Correlation ID tracking (workflow_id)
        - Comprehensive user_context with permissions
        - Traffic Cop integration (session management)
        - Nurse integration (observability)
        - Data Steward integration (lineage tracking)
        
        BOOTSTRAP PATTERN: This method PROVIDES security, so we use direct security abstraction access
        instead of get_security() utility to avoid circular dependency.
        """
        # Generate workflow_id for correlation (Phase 1)
        workflow_id = request.get("workflow_id") or str(uuid.uuid4())
        
        # Bootstrap Pattern: Direct security abstraction access (Security Guard PROVIDES security)
        # ❌ DON'T USE: security = self.service.get_security()
        # ✅ USE: Direct auth abstraction access for self-reporting
        auth_abstraction = self.service.get_auth_abstraction()
        
        try:
            email = request.get("email")
            password = request.get("password")
            
            if not email or not password:
                return {
                    "success": False,
                    "user_id": None,
                    "session_id": None,
                    "access_token": None,
                    "workflow_id": workflow_id,
                    "message": "Email and password are required"
                }
            
            self.service._log("info", f"🔐 Authenticating user: {email} (workflow_id: {workflow_id})")
            
            if not auth_abstraction:
                raise Exception("Auth abstraction not available")
            
            # Get the access token, refresh token, and user info from Supabase adapter directly
            # The auth abstraction doesn't expose the token, so we need to get it from the adapter
            # We call Supabase directly to get both tokens and user info
            access_token = None
            refresh_token = None  # ✅ NEW: Extract refresh_token
            user_data = None
            try:
                # Get Supabase adapter from auth abstraction
                if hasattr(auth_abstraction, 'supabase'):
                    supabase_result = await auth_abstraction.supabase.sign_in_with_password(email, password)
                    if supabase_result.get("success"):
                        access_token = supabase_result.get("access_token")
                        refresh_token = supabase_result.get("refresh_token")  # ✅ NEW: Extract refresh_token
                        user_data = supabase_result.get("user", {})
                        self.service._log("info", f"✅ Retrieved tokens from Supabase: access_token={access_token[:20] if access_token else 'None'}..., refresh_token={'present' if refresh_token else 'None'}")
            except Exception as e:
                self.service._log("warning", f"Could not get tokens from Supabase adapter: {e}")
            
            # AuthAbstraction.authenticate_user expects a dict with email and password
            # This validates the credentials and creates SecurityContext
            # We still call this to get the SecurityContext, even though we already have the token
            security_context = await auth_abstraction.authenticate_user({
                "email": email,
                "password": password
            })
            
            # Phase 2: Create session via Session Abstraction (direct Public Works access)
            # Security Guard uses abstractions directly (like other Smart City services) to avoid circular dependencies
            session_id = None
            session_abstraction = self.service.get_session_abstraction()
            if session_abstraction:
                try:
                    from foundations.public_works_foundation.abstraction_contracts.session_protocol import SessionContext, SessionType, SecurityLevel
                    session_context = SessionContext(
                        user_id=security_context.user_id,
                        tenant_id=security_context.tenant_id,
                        agent_id=None,
                        origin="security_guard"
                    )
                    session_data = {
                        "email": email,
                        "roles": security_context.roles,
                        "permissions": security_context.permissions,
                        "workflow_id": workflow_id
                    }
                    session = await session_abstraction.create_session(
                        context=session_context,
                        session_data=session_data
                    )
                    session_id = session.session_id
                    self.service._log("info", f"✅ Session created via Session Abstraction: {session_id}")
                except Exception as e:
                    self.service._log("warning", f"⚠️ Session Abstraction creation failed (using fallback): {e}")
            
            # Fallback: Internal session storage if Session Abstraction not available
            if not session_id:
                session_id = str(uuid.uuid4())
                self.service.active_sessions[session_id] = {
                    "session_id": session_id,
                    "user_id": security_context.user_id,
                    "email": email,
                    "created_at": datetime.utcnow(),
                    "status": "active",
                    "workflow_id": workflow_id
                }
                self.service._log("info", f"✅ Session created (internal storage): {session_id}")
            
            # Phase 5: Build comprehensive user_context with permissions
            user_context = {
                "user_id": security_context.user_id,
                "session_id": session_id,
                "workflow_id": workflow_id,
                "permissions": security_context.permissions or [],  # ✅ CRITICAL: Include permissions
                "roles": security_context.roles or [],
                "tenant_id": security_context.tenant_id,
                "email": email
            }
            
            # Phase 3: Record observability via Observability Abstraction (direct Public Works access)
            # Security Guard uses abstractions directly (like other Smart City services) to avoid circular dependencies
            # Note: Observability abstraction may not be available - use telemetry utilities as fallback
            try:
                observability_abstraction = self.service.get_infrastructure_abstraction("observability")
                if observability_abstraction:
                    await observability_abstraction.record_platform_log(
                        log_level="info",
                        message=f"User authenticated: {email}",
                        service_name="SecurityGuardService",
                        trace_id=workflow_id,
                        user_context=user_context,
                        metadata={
                            "user_id": security_context.user_id,
                            "session_id": session_id,
                            "workflow_id": workflow_id,
                            "event_type": "user_authenticated"
                        }
                    )
            except Exception as e:
                self.service._log("warning", f"⚠️ Observability Abstraction recording failed (using telemetry utilities): {e}")
            
            # Phase 4: Track lineage via State Management Abstraction (direct Public Works access)
            # Security Guard uses abstractions directly (like other Smart City services) to avoid circular dependencies
            state_management_abstraction = self.service.get_state_management_abstraction()
            if state_management_abstraction:
                try:
                    lineage_state_id = f"lineage:auth:{security_context.user_id}:{session_id}"
                    await state_management_abstraction.store_state(
                        state_id=lineage_state_id,
                        state_data={
                            "source_id": security_context.user_id,
                            "target_id": session_id,
                            "operation": "user_authentication",
                            "operation_type": "security_event",
                            "correlation_ids": {
                                "workflow_id": workflow_id,
                                "user_id": security_context.user_id,
                                "session_id": session_id
                            }
                        },
                        metadata={
                            "workflow_id": workflow_id,
                            "user_id": security_context.user_id,
                            "session_id": session_id,
                            "event_type": "authentication_lineage"
                        }
                    )
                except Exception as e:
                    self.service._log("warning", f"⚠️ State Management Abstraction lineage tracking failed: {e}")
            
            # ✅ CAN USE: Telemetry utilities (Security Guard doesn't provide telemetry)
            await self.service.log_operation_with_telemetry(
                "authenticate_user_complete",
                success=True,
                details={"user_id": security_context.user_id, "email": email, "workflow_id": workflow_id}
            )
            
            # ✅ CAN USE: Health metrics utility
            await self.service.record_health_metric(
                "user_authenticated",
                1.0,
                {"user_id": security_context.user_id, "email": email, "workflow_id": workflow_id}
            )
            
            # Return comprehensive response with user_context
            return {
                "success": True,
                "user_id": security_context.user_id,
                "session_id": session_id,
                "access_token": access_token,  # None if not available - no placeholder
                "refresh_token": refresh_token,  # ✅ NEW: Include refresh_token in response
                "workflow_id": workflow_id,  # ✅ Phase 1: Correlation ID
                "user_context": user_context,  # ✅ Phase 5: Comprehensive context with permissions
                "tenant_id": security_context.tenant_id,
                "roles": security_context.roles,
                "permissions": security_context.permissions,  # ✅ Phase 5: Explicit permissions
                "email": email,
                "message": "User authenticated successfully" + (" (token not available)" if not access_token else "")
            }
            
        except Exception as e:
            # ✅ CAN USE: Error handling utility (Security Guard doesn't provide error handling)
            await self.service.handle_error_with_audit(e, "authenticate_user")
            
            # ✅ CAN USE: Telemetry utilities for failure reporting
            await self.service.log_operation_with_telemetry(
                "authenticate_user_complete",
                success=False,
                details={"email": email, "error": str(e)}
            )
            
            self.service._log("error", f"❌ Failed to authenticate user: {e}")
            return {
                "success": False,
                "user_id": request.get("email"),
                "session_id": None,
                "access_token": None,
                "message": str(e)
            }
    
    async def register_user(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register new user credentials.
        
        BOOTSTRAP PATTERN: This method PROVIDES security, so we use direct security abstraction access
        instead of get_security() utility to avoid circular dependency.
        """
        # Bootstrap Pattern: Direct security abstraction access (Security Guard PROVIDES security)
        auth_abstraction = self.service.get_auth_abstraction()
        
        try:
            email = request.get("email")
            password = request.get("password")
            name = request.get("name")
            user_metadata = request.get("user_metadata", {})
            
            if not email or not password:
                return {
                    "success": False,
                    "user_id": None,
                    "session_id": None,
                    "access_token": None,
                    "message": "Email and password are required"
                }
            
            if name:
                user_metadata["name"] = name
            
            self.service._log("info", f"📝 Registering user: {email}")
            
            if not auth_abstraction:
                raise Exception("Auth abstraction not available")
            
            # Get the access token from Supabase adapter directly
            # The auth abstraction doesn't expose the token, so we need to get it from the adapter
            # We call Supabase directly to get the token, then use auth abstraction for validation
            access_token = None
            try:
                # Get Supabase adapter from auth abstraction
                if hasattr(auth_abstraction, 'supabase'):
                    supabase_result = await auth_abstraction.supabase.sign_up_with_password(email, password, user_metadata)
                    if supabase_result.get("success") and supabase_result.get("access_token"):
                        access_token = supabase_result.get("access_token")
                        self.service._log("info", f"✅ Retrieved access token from Supabase")
            except Exception as e:
                self.service._log("warning", f"Could not get access token from Supabase adapter: {e}")
            
            security_context = await auth_abstraction.register_user({
                "email": email,
                "password": password,
                "user_metadata": user_metadata
            })
            
            # Create session
            session_id = str(uuid.uuid4())
            self.service.active_sessions[session_id] = {
                "session_id": session_id,
                "user_id": security_context.user_id,
                "email": email,
                "created_at": datetime.utcnow(),
                "status": "active"
            }
            
            # ✅ CAN USE: Telemetry utilities (Security Guard doesn't provide telemetry)
            await self.service.log_operation_with_telemetry(
                "register_user_complete",
                success=True,
                details={"user_id": security_context.user_id, "email": email}
            )
            
            # ✅ CAN USE: Health metrics utility
            await self.service.record_health_metric(
                "user_registered",
                1.0,
                {"user_id": security_context.user_id, "email": email}
            )
            
            # Return None for access_token if not available (don't use placeholder)
            # Callers should check for None and handle appropriately
            return {
                "success": True,
                "user_id": security_context.user_id,
                "session_id": session_id,
                "access_token": access_token,  # None if not available - no placeholder
                "tenant_id": security_context.tenant_id,
                "roles": security_context.roles,
                "permissions": security_context.permissions,
                "message": "User registered successfully" + (" (token not available)" if not access_token else "")
            }
            
        except Exception as e:
            # ✅ CAN USE: Error handling utility (Security Guard doesn't provide error handling)
            await self.service.handle_error_with_audit(e, "register_user")
            
            # ✅ CAN USE: Telemetry utilities for failure reporting
            await self.service.log_operation_with_telemetry(
                "register_user_complete",
                success=False,
                details={"email": email, "error": str(e)}
            )
            
            self.service._log("error", f"❌ Failed to register user: {e}")
            return {
                "success": False,
                "user_id": None,
                "session_id": None,
                "access_token": None,
                "message": str(e)
            }
    
    async def authorize_action(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authorize user action on resource.
        
        BOOTSTRAP PATTERN: This method PROVIDES security, so we use direct security abstraction access
        instead of get_security() utility to avoid circular dependency.
        
        Zero-trust authorization: "Secure by design, open by policy"
        """
        # Bootstrap Pattern: Direct security abstraction access (Security Guard PROVIDES security)
        authorization_abstraction = self.service.get_authorization_abstraction()
        
        try:
            user_id = request.get("user_id")
            action = request.get("action")
            resource = request.get("resource") or request.get("resource_id")
            tenant_id = request.get("tenant_id", "default")
            context_data = request.get("context", {})
            
            self.service._log("info", f"🔐 Authorizing action: {action} on {resource}")
            
            # Create security context
            from foundations.public_works_foundation.abstraction_contracts.authentication_protocol import SecurityContext
            security_context = SecurityContext(
                user_id=user_id,
                tenant_id=tenant_id,
                roles=context_data.get("roles", ["user"]),
                permissions=context_data.get("permissions", []),
                origin=context_data.get("origin", "api")
            )
            
            if not authorization_abstraction:
                self.service._log("warning", "⚠️ Authorization abstraction not available - allowing request (MVP mode)")
                # ✅ CAN USE: Telemetry utilities for MVP mode reporting
                await self.service.log_operation_with_telemetry(
                    "authorize_action_complete",
                    success=True,
                    details={"action": action, "resource": resource, "mode": "mvp"}
                )
                return {
                    "success": True,
                    "authorized": True,
                    "policy_decision": "allowed_mvp_mode",
                    "message": "Authorization granted (MVP mode - no policy engine)"
                }
            
            # Call the enforce method (not authorize_action)
            is_authorized = await authorization_abstraction.enforce(
                action=action,
                resource=resource,
                context=security_context
            )
            
            if is_authorized:
                self.service._log("info", f"✅ Authorization granted: {user_id} -> {action} {resource}")
                
                # ✅ CAN USE: Telemetry utilities (Security Guard doesn't provide telemetry)
                await self.service.log_operation_with_telemetry(
                    "authorize_action_complete",
                    success=True,
                    details={"user_id": user_id, "action": action, "resource": resource, "authorized": True}
                )
                
                # ✅ CAN USE: Health metrics utility
                await self.service.record_health_metric(
                    "authorization_granted",
                    1.0,
                    {"user_id": user_id, "action": action, "resource": resource}
                )
                
                return {
                    "success": True,
                    "authorized": True,
                    "policy_decision": "allowed",
                    "message": "Authorization granted"
                }
            else:
                self.service._log("warning", f"❌ Authorization denied: {user_id} -> {action} {resource}")
                
                # ✅ CAN USE: Telemetry utilities for denial reporting
                await self.service.log_operation_with_telemetry(
                    "authorize_action_complete",
                    success=False,
                    details={"user_id": user_id, "action": action, "resource": resource, "authorized": False}
                )
                
                # ✅ CAN USE: Health metrics utility
                await self.service.record_health_metric(
                    "authorization_denied",
                    1.0,
                    {"user_id": user_id, "action": action, "resource": resource}
                )
                
                return {
                    "success": False,
                    "authorized": False,
                    "policy_decision": "denied",
                    "message": "Authorization denied by policy"
                }
            
        except Exception as e:
            # ✅ CAN USE: Error handling utility (Security Guard doesn't provide error handling)
            await self.service.handle_error_with_audit(e, "authorize_action")
            
            # ✅ CAN USE: Telemetry utilities for error reporting
            await self.service.log_operation_with_telemetry(
                "authorize_action_complete",
                success=False,
                details={"action": action, "resource": resource, "error": str(e)}
            )
            
            self.service._log("error", f"❌ Failed to authorize action: {e}")
            # Fail closed for zero-trust
            return {
                "success": False,
                "authorized": False,
                "policy_decision": "error",
                "message": str(e)
            }







