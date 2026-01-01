#!/usr/bin/env python3
"""
Security Composition Service - 5-Layer Architecture Composition Layer

This service orchestrates multiple infrastructure abstractions to provide
business-facing security capabilities. This is the critical missing piece
from the CTO's 5-layer vision.

WHAT (Composition Role): I orchestrate multiple abstractions for business-facing capabilities
HOW (Composition Implementation): I compose auth, authorization, session, tenant abstractions
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

# Import abstraction contracts
from ..abstraction_contracts.authentication_protocol import AuthenticationProtocol, SecurityContext
from ..abstraction_contracts.authorization_protocol import AuthorizationProtocol
from ..abstraction_contracts.session_protocol import SessionProtocol
from ..abstraction_contracts.tenant_protocol import TenantProtocol
from ..abstraction_contracts.policy_engine_protocol import PolicyEngine


class SecurityCompositionService:
    """
    Security Composition Service - 5-Layer Architecture Composition Layer
    
    This service orchestrates multiple infrastructure abstractions to provide
    business-facing security capabilities. This is the critical missing piece
    from the CTO's 5-layer vision.
    
    WHAT (Composition Role): I orchestrate multiple abstractions for business-facing capabilities
    HOW (Composition Implementation): I compose auth, authorization, session, tenant abstractions
    """
    
    def __init__(self, service_name: str = "security_composition_service", di_container=None):
        """Initialize Security Composition Service."""
        if not di_container:
            raise ValueError("DI Container is required for SecurityCompositionService initialization")
        
        self.service_name = service_name
        self.di_container = di_container
        
        # Get logger from DI Container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(f"SecurityCompositionService-{service_name}")
        
        # Infrastructure abstractions (injected by Infrastructure Registry)
        self.auth_abstraction: Optional[AuthenticationProtocol] = None
        self.authorization_abstraction: Optional[AuthorizationProtocol] = None
        self.session_abstraction: Optional[SessionProtocol] = None
        self.tenant_abstraction: Optional[TenantProtocol] = None
        self.policy_engine: Optional[PolicyEngine] = None
        
        # Composition state
        self.is_initialized = False
        self.composition_metrics = {
            "authentications": 0,
            "authorizations": 0,
            "sessions_created": 0,
            "tenant_checks": 0,
            "composition_errors": 0
        }
        
        self.logger.info(f"✅ Security Composition Service '{service_name}' initialized")
    
    async def initialize(self, 
                        auth_abstraction: AuthenticationProtocol,
                        authorization_abstraction: AuthorizationProtocol,
                        session_abstraction: SessionProtocol,
                        tenant_abstraction: TenantProtocol,
                        policy_engine: PolicyEngine):
        """Initialize composition service with infrastructure abstractions."""
        try:
            self.logger.info(f"🚀 Initializing Security Composition Service '{self.service_name}'...")
            
            # Store infrastructure abstractions
            self.auth_abstraction = auth_abstraction
            self.authorization_abstraction = authorization_abstraction
            self.session_abstraction = session_abstraction
            self.tenant_abstraction = tenant_abstraction
            self.policy_engine = policy_engine
            
            # Test composition capabilities
            await self._test_composition_capabilities()
            
            self.is_initialized = True
            self.logger.info(f"✅ Security Composition Service '{self.service_name}' initialized successfully")
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "initialize",
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Failed to initialize Security Composition Service '{self.service_name}': {e}")
            raise
    
    async def _test_composition_capabilities(self):
        """Test that all composition capabilities work together."""
        try:
            # Test that all abstractions are available
            if not all([self.auth_abstraction, self.authorization_abstraction, 
                       self.session_abstraction, self.tenant_abstraction, self.policy_engine]):
                raise Exception("Not all infrastructure abstractions are available for composition")
            
            self.logger.info("✅ All infrastructure abstractions available for composition")
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_test_composition_capabilities",
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Composition capability testing failed: {e}")
            raise
    
    # ============================================================================
    # BUSINESS-FACING SECURITY CAPABILITIES (Composed from Multiple Abstractions)
    # ============================================================================
    
    async def authenticate_and_authorize(self, credentials: Dict[str, Any], 
                                       action: str, resource: str) -> Dict[str, Any]:
        """
        Compose authentication and authorization for business-facing capability.
        
        This is the key composition - orchestrating multiple abstractions
        to provide a single business-facing capability.
        """
        try:
            self.composition_metrics["authentications"] += 1
            
            # Step 1: Authenticate user
            security_context = await self.auth_abstraction.authenticate_user(credentials)
            
            if not security_context:
                return {
                    "success": False,
                    "message": "Authentication failed",
                    "security_context": None
                }
            
            # Step 2: Authorize action
            is_authorized = await self.authorization_abstraction.enforce(action, resource, security_context)
            
            if not is_authorized:
                return {
                    "success": False,
                    "message": "Authorization denied",
                    "security_context": security_context
                }
            
            self.composition_metrics["authorizations"] += 1
            
            # Record platform operation event
            telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("authenticate_and_authorize", {
                    "action": action,
                    "resource": resource,
                    "user_id": getattr(security_context, "user_id", None),
                    "success": True
                })
            
            return {
                "success": True,
                "message": "Authentication and authorization successful",
                "security_context": security_context,
                "action": action,
                "resource": resource
            }
            
        except Exception as e:
            self.composition_metrics["composition_errors"] += 1
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "authenticate_and_authorize",
                    "action": action,
                    "resource": resource,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Authentication and authorization composition failed: {e}")
            return {
                "success": False,
                "message": f"Composition error: {e}",
                "security_context": None,
                "error_code": "AUTH_COMPOSITION_ERROR"
            }
    
    async def create_secure_session(self, user_id: str, tenant_id: str, 
                                  session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compose session creation with tenant validation for business-facing capability.
        """
        try:
            # Step 1: Validate tenant access
            tenant_config = await self.tenant_abstraction.get_tenant_config(tenant_id)
            if not tenant_config:
                return {
                    "success": False,
                    "message": "Invalid tenant",
                    "session_id": None
                }
            
            # Step 2: Create session with tenant context
            session_id = await self.session_abstraction.create_session(user_id, tenant_id, session_data)
            
            if not session_id:
                return {
                    "success": False,
                    "message": "Session creation failed",
                    "session_id": None
                }
            
            self.composition_metrics["sessions_created"] += 1
            self.composition_metrics["tenant_checks"] += 1
            
            # Record platform operation event
            telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("create_secure_session", {
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "session_id": session_id,
                    "success": True
                })
            
            return {
                "success": True,
                "message": "Secure session created",
                "session_id": session_id,
                "tenant_id": tenant_id,
                "user_id": user_id
            }
            
        except Exception as e:
            self.composition_metrics["composition_errors"] += 1
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "create_secure_session",
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Secure session creation composition failed: {e}")
            return {
                "success": False,
                "message": f"Composition error: {e}",
                "session_id": None,
                "error_code": "SESSION_CREATION_ERROR"
            }
    
    async def validate_session_and_authorize(self, session_id: str, 
                                           action: str, resource: str) -> Dict[str, Any]:
        """
        Compose session validation with authorization for business-facing capability.
        """
        try:
            # Step 1: Validate session
            security_context = await self.session_abstraction.validate_session(session_id)
            
            if not security_context:
                return {
                    "success": False,
                    "message": "Invalid session",
                    "authorized": False
                }
            
            # Step 2: Authorize action
            is_authorized = await self.authorization_abstraction.enforce(action, resource, security_context)
            
            # Record platform operation event
            telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("validate_session_and_authorize", {
                    "session_id": session_id,
                    "action": action,
                    "resource": resource,
                    "authorized": is_authorized,
                    "success": True
                })
            
            return {
                "success": True,
                "message": "Session validation and authorization successful",
                "authorized": is_authorized,
                "security_context": security_context
            }
            
        except Exception as e:
            self.composition_metrics["composition_errors"] += 1
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "validate_session_and_authorize",
                    "session_id": session_id,
                    "action": action,
                    "resource": resource,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Session validation and authorization composition failed: {e}")
            return {
                "success": False,
                "message": f"Composition error: {e}",
                "authorized": False,
                "error_code": "SESSION_VALIDATION_ERROR"
            }
    
    async def enforce_tenant_isolation(self, user_id: str, tenant_id: str, 
                                     resource_tenant: str) -> Dict[str, Any]:
        """
        Compose tenant validation with policy enforcement for business-facing capability.
        """
        try:
            # Step 1: Get user's tenant context
            user_tenant_config = await self.tenant_abstraction.get_tenant_config(tenant_id)
            if not user_tenant_config:
                return {
                    "success": False,
                    "message": "User tenant not found",
                    "isolated": False
                }
            
            # Step 2: Check tenant isolation policy
            if tenant_id != resource_tenant:
                return {
                    "success": False,
                    "message": "Tenant isolation violation",
                    "isolated": False
                }
            
            self.composition_metrics["tenant_checks"] += 1
            
            # Record platform operation event
            telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("enforce_tenant_isolation", {
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "resource_tenant": resource_tenant,
                    "isolated": True,
                    "success": True
                })
            
            return {
                "success": True,
                "message": "Tenant isolation enforced",
                "isolated": True,
                "tenant_id": tenant_id
            }
            
        except Exception as e:
            self.composition_metrics["composition_errors"] += 1
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "enforce_tenant_isolation",
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "resource_tenant": resource_tenant,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Tenant isolation composition failed: {e}")
            return {
                "success": False,
                "message": f"Composition error: {e}",
                "isolated": False,
                "error_code": "TENANT_ISOLATION_ERROR"
            }
    
    async def get_security_context_with_tenant(self, session_id: str) -> Dict[str, Any]:
        """
        Compose session validation with tenant context for business-facing capability.
        """
        try:
            # Step 1: Validate session
            security_context = await self.session_abstraction.validate_session(session_id)
            
            if not security_context:
                return {
                    "success": False,
                    "message": "Invalid session",
                    "security_context": None,
                    "tenant_context": None
                }
            
            # Step 2: Get tenant context
            tenant_config = await self.tenant_abstraction.get_tenant_config(security_context.tenant_id)
            
            # Record platform operation event
            telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_security_context_with_tenant", {
                    "session_id": session_id,
                    "tenant_id": getattr(security_context, "tenant_id", None),
                    "success": True
                })
            
            return {
                "success": True,
                "message": "Security context with tenant retrieved",
                "security_context": security_context,
                "tenant_context": tenant_config
            }
            
        except Exception as e:
            self.composition_metrics["composition_errors"] += 1
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_security_context_with_tenant",
                    "session_id": session_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Security context with tenant composition failed: {e}")
            return {
                "success": False,
                "message": f"Composition error: {e}",
                "security_context": None,
                "tenant_context": None,
                "error_code": "SECURITY_CONTEXT_ERROR"
            }
    
    # ============================================================================
    # COMPOSITION METRICS AND STATUS
    # ============================================================================
    
    async def get_composition_metrics(self) -> Dict[str, Any]:
        """Get composition service metrics."""
        try:
            total_operations = (
                self.composition_metrics["authentications"] +
                self.composition_metrics["authorizations"] +
                self.composition_metrics["sessions_created"] +
                self.composition_metrics["tenant_checks"]
            )
            
            error_rate = (self.composition_metrics["composition_errors"] / total_operations * 100) if total_operations > 0 else 0
            
            return {
                "authentications": self.composition_metrics["authentications"],
                "authorizations": self.composition_metrics["authorizations"],
                "sessions_created": self.composition_metrics["sessions_created"],
                "tenant_checks": self.composition_metrics["tenant_checks"],
                "composition_errors": self.composition_metrics["composition_errors"],
                "error_rate": f"{error_rate:.2f}%"
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_composition_metrics",
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Failed to get composition metrics: {e}")
            return {}
    
    def get_capabilities(self) -> List[str]:
        """Get composition service capabilities."""
        return [
            "authenticate_and_authorize",
            "create_secure_session",
            "validate_session_and_authorize",
            "enforce_tenant_isolation",
            "get_security_context_with_tenant",
            "composition_metrics"
        ]
    
    async def get_status(self) -> Dict[str, Any]:
        """Get composition service status."""
        return {
            "service": "SecurityCompositionService",
            "service_name": self.service_name,
            "status": "active" if self.is_initialized else "not_initialized",
            "is_initialized": self.is_initialized,
            "capabilities": self.get_capabilities(),
            "metrics": await self.get_composition_metrics()
        }



