"""
Session Composition Service - Infrastructure-level business logic for session management

Handles infrastructure-level session workflows, session orchestration,
and coordination between different session management systems.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from foundations.public_works_foundation.abstraction_contracts.session_protocol import (
    SessionContext, Session, SessionToken, SessionAnalytics,
    SessionStatus, SessionType, SecurityLevel
)
from foundations.public_works_foundation.infrastructure_abstractions.session_abstraction import SessionAbstraction


class SessionCompositionService:
    """
    Session Composition Service - Infrastructure-level business logic for session management
    
    Handles infrastructure-level session workflows and orchestration.
    This service coordinates session management across different systems.
    """
    
    def __init__(self, session_abstraction: SessionAbstraction, di_container=None):
        """Initialize Session Composition Service."""
        if not di_container:
            raise ValueError("DI Container is required for SessionCompositionService initialization")
        
        self.session_abstraction = session_abstraction
        self.di_container = di_container
        self.service_name = "session_composition_service"
        
        # Get logger from DI Container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(self.service_name)
        
        # Infrastructure-level session workflows
        self.session_workflows = {
            "user_session": self._user_session_workflow,
            "agent_session": self._agent_session_workflow,
            "api_session": self._api_session_workflow,
            "web_session": self._web_session_workflow,
            "mobile_session": self._mobile_session_workflow,
            "comprehensive_session": self._comprehensive_session_workflow
        }
        
        self.logger.info("Initialized Session Composition Service")
    
    # ============================================================================
    # SECURITY AND MULTI-TENANCY VALIDATION HELPERS
    # ============================================================================
    
    async def _validate_security_and_tenant(self, user_context: Dict[str, Any], 
                                           resource: str, action: str) -> Optional[Dict[str, Any]]:
        """
        Validate security context and tenant access.
        
        Args:
            user_context: User context with user_id, tenant_id, security_context
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            None if validation passes, error dict if validation fails
        """
        try:
            if not user_context:
                return None  # No validation if no context provided
            
            # Get utilities from DI container
            security = self.di_container.get_utility("security") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            tenant = self.di_container.get_utility("tenant") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            
            user_id = user_context.get("user_id")
            tenant_id = user_context.get("tenant_id")
            security_context = user_context.get("security_context")
            
            # Security validation (if security utility available and context provided)
            if security and security_context:
                try:
                    # Validate user permission
                    has_permission = await security.validate_user_permission(
                        user_id, resource, action, 
                        security_context.get("permissions", [])
                    )
                    if not has_permission:
                        return {
                            "success": False,
                            "error": f"Permission denied: {action} on {resource}",
                            "error_code": "PERMISSION_DENIED"
                        }
                except Exception as e:
                    self.logger.warning(f"Security validation failed: {e}")
                    # Don't fail on security validation errors - log and continue
            
            # Multi-tenancy validation (if tenant utility available and tenant_id provided)
            if tenant and tenant_id:
                try:
                    # Check if multi-tenancy is enabled
                    if tenant.is_multi_tenant_enabled():
                        # Validate tenant access (basic check - user can only access their own tenant)
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            return {
                                "success": False,
                                "error": f"Tenant access denied for tenant: {tenant_id}",
                                "error_code": "TENANT_ACCESS_DENIED"
                            }
                except Exception as e:
                    self.logger.warning(f"Tenant validation failed: {e}")
                    # Don't fail on tenant validation errors - log and continue
            
            return None  # Validation passed
            
        except Exception as e:
            self.logger.error(f"Security/tenant validation error: {e}")
            # Don't fail on validation errors - log and continue
            return None
    
    async def orchestrate_session_management(self, 
                                          workflow_type: str,
                                          context: SessionContext,
                                          session_data: Optional[Dict[str, Any]] = None,
                                          user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Orchestrate session management using infrastructure-level workflows."""
        try:
            # Validate security and tenant access
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "session", "orchestrate"
                )
                if validation_error:
                    return validation_error
            
            self.logger.debug(f"Orchestrating {workflow_type} session management")
            
            # Get workflow
            workflow = self.session_workflows.get(workflow_type)
            if not workflow:
                return {
                    "success": False,
                    "error": f"Unknown workflow type: {workflow_type}",
                    "workflow_type": workflow_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Execute workflow
            result = await workflow(context, session_data)
            
            # Add infrastructure-level metadata
            result.update({
                "workflow_type": workflow_type,
                "orchestrated_at": datetime.utcnow().isoformat(),
                "composition_service": self.service_name
            })
            
            # Record platform operation event
            telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("orchestrate_session_management", {
                    "workflow_type": workflow_type,
                    "success": result.get("success", False)
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "orchestrate_session_management",
                    "workflow_type": workflow_type,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Session orchestration failed for {workflow_type}: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "SESSION_ORCHESTRATION_ERROR",
                "workflow_type": workflow_type,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def perform_session_assessment(self, 
                                       session_id: str,
                                       context: SessionContext,
                                       user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform comprehensive session assessment."""
        try:
            # Validate security and tenant access
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "session", "assess"
                )
                if validation_error:
                    return validation_error
            
            self.logger.debug(f"Performing session assessment for {session_id}")
            
            # Get session
            session = await self.session_abstraction.get_session(session_id, context)
            if not session:
                return {
                    "success": False,
                    "error": f"Session {session_id} not found",
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Get session analytics
            analytics = await self.session_abstraction.get_session_analytics(session_id, context)
            
            # Analyze session status
            assessment = self._analyze_session_status(session, analytics)
            
            result = {
                "success": True,
                "session_id": session_id,
                "session_status": session.status.value,
                "session_type": session.session_type.value,
                "security_level": session.security_level.value,
                "analytics": {
                    "total_requests": analytics.total_requests,
                    "successful_requests": analytics.successful_requests,
                    "failed_requests": analytics.failed_requests,
                    "average_response_time": analytics.average_response_time,
                    "security_events": analytics.security_events
                },
                "assessment": assessment,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record platform operation event
            telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("perform_session_assessment", {
                    "session_id": session_id,
                    "session_status": session.status.value,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "perform_session_assessment",
                    "session_id": session_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Session assessment failed for {session_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "SESSION_ASSESSMENT_ERROR",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def create_session_with_security(self, 
                                        context: SessionContext,
                                        session_data: Dict[str, Any],
                                        security_level: SecurityLevel = SecurityLevel.MEDIUM,
                                        user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create session with enhanced security measures."""
        try:
            # Validate security and tenant access
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "session", "create"
                )
                if validation_error:
                    return validation_error
            
            self.logger.debug(f"Creating secure session with {security_level.value} security level")
            
            # Add security metadata
            enhanced_session_data = session_data.copy()
            enhanced_session_data.update({
                "security_level": security_level.value,
                "created_by": self.service_name,
                "security_enhanced": True
            })
            
            # Create session
            session = await self.session_abstraction.create_session(context, enhanced_session_data)
            
            # Create session token
            token = await self.session_abstraction.create_session_token(
                session.session_id,
                "access",
                context
            )
            
            result = {
                "success": True,
                "session_id": session.session_id,
                "session_type": session.session_type.value,
                "security_level": session.security_level.value,
                "token_id": token.token_id,
                "token_value": token.token_value,
                "expires_at": session.expires_at.isoformat() if session.expires_at else None,
                "created_at": session.created_at.isoformat()
            }
            
            # Record platform operation event
            telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("create_session_with_security", {
                    "session_id": session.session_id,
                    "security_level": security_level.value,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "create_session_with_security",
                    "security_level": security_level.value,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Secure session creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "SESSION_CREATION_ERROR",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_session_metrics(self) -> Dict[str, Any]:
        """Get infrastructure-level session metrics."""
        try:
            self.logger.debug("Getting session metrics")
            
            # Get adapter health
            adapter_health = await self.session_abstraction.health_check()
            
            # Get available workflows
            available_workflows = list(self.session_workflows.keys())
            
            return {
                "success": True,
                "adapter_health": adapter_health,
                "available_workflows": available_workflows,
                "workflow_count": len(available_workflows),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_session_metrics",
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"Failed to get session metrics: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "SESSION_METRICS_ERROR",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check session composition service health."""
        try:
            self.logger.debug("Checking session composition service health")
            
            # Check underlying abstraction
            abstraction_health = await self.session_abstraction.health_check()
            
            return {
                "status": "healthy" if abstraction_health.get("status") == "healthy" else "unhealthy",
                "service": self.service_name,
                "abstraction_health": abstraction_health,
                "available_workflows": len(self.session_workflows),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "health_check",
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"Session composition service health check failed: {e}")
            return {
                "status": "unhealthy",
                "service": self.service_name,
                "error": str(e),
                "error_code": "HEALTH_CHECK_ERROR",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # INFRASTRUCTURE-LEVEL SESSION WORKFLOWS
    # ============================================================================
    
    async def _user_session_workflow(self, 
                                   context: SessionContext, 
                                   session_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """User session workflow for infrastructure-level session management."""
        try:
            if not session_data:
                session_data = {
                    "session_type": "user",
                    "security_level": "medium"
                }
            
            # Create user session
            session = await self.session_abstraction.create_session(context, session_data)
            
            # Create access token
            token = await self.session_abstraction.create_session_token(
                session.session_id,
                "access",
                context
            )
            
            return {
                "success": True,
                "workflow": "user_session",
                "session_id": session.session_id,
                "session_type": session.session_type.value,
                "security_level": session.security_level.value,
                "token_id": token.token_id,
                "expires_at": session.expires_at.isoformat() if session.expires_at else None
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_user_session_workflow",
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None)
            return {
                "success": False,
                "workflow": "user_session",
                "error": str(e),
                "error_code": "USER_SESSION_WORKFLOW_ERROR"
            }
    
    async def _agent_session_workflow(self, 
                                    context: SessionContext, 
                                    session_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Agent session workflow for infrastructure-level session management."""
        try:
            if not session_data:
                session_data = {
                    "session_type": "agent",
                    "security_level": "high"
                }
            
            # Create agent session
            session = await self.session_abstraction.create_session(context, session_data)
            
            # Create access token
            token = await self.session_abstraction.create_session_token(
                session.session_id,
                "access",
                context
            )
            
            return {
                "success": True,
                "workflow": "agent_session",
                "session_id": session.session_id,
                "session_type": session.session_type.value,
                "security_level": session.security_level.value,
                "token_id": token.token_id,
                "expires_at": session.expires_at.isoformat() if session.expires_at else None
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_agent_session_workflow",
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None)
            return {
                "success": False,
                "workflow": "agent_session",
                "error": str(e),
                "error_code": "AGENT_SESSION_WORKFLOW_ERROR"
            }
    
    async def _api_session_workflow(self, 
                                   context: SessionContext, 
                                   session_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """API session workflow for infrastructure-level session management."""
        try:
            if not session_data:
                session_data = {
                    "session_type": "api",
                    "security_level": "high"
                }
            
            # Create API session
            session = await self.session_abstraction.create_session(context, session_data)
            
            # Create access token
            token = await self.session_abstraction.create_session_token(
                session.session_id,
                "access",
                context
            )
            
            return {
                "success": True,
                "workflow": "api_session",
                "session_id": session.session_id,
                "session_type": session.session_type.value,
                "security_level": session.security_level.value,
                "token_id": token.token_id,
                "expires_at": session.expires_at.isoformat() if session.expires_at else None
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_api_session_workflow",
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None)
            return {
                "success": False,
                "workflow": "api_session",
                "error": str(e),
                "error_code": "API_SESSION_WORKFLOW_ERROR"
            }
    
    async def _web_session_workflow(self, 
                                   context: SessionContext, 
                                   session_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Web session workflow for infrastructure-level session management."""
        try:
            if not session_data:
                session_data = {
                    "session_type": "web",
                    "security_level": "medium"
                }
            
            # Create web session
            session = await self.session_abstraction.create_session(context, session_data)
            
            # Create access token
            token = await self.session_abstraction.create_session_token(
                session.session_id,
                "access",
                context
            )
            
            return {
                "success": True,
                "workflow": "web_session",
                "session_id": session.session_id,
                "session_type": session.session_type.value,
                "security_level": session.security_level.value,
                "token_id": token.token_id,
                "expires_at": session.expires_at.isoformat() if session.expires_at else None
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_web_session_workflow",
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None)
            return {
                "success": False,
                "workflow": "web_session",
                "error": str(e),
                "error_code": "WEB_SESSION_WORKFLOW_ERROR"
            }
    
    async def _mobile_session_workflow(self, 
                                     context: SessionContext, 
                                     session_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Mobile session workflow for infrastructure-level session management."""
        try:
            if not session_data:
                session_data = {
                    "session_type": "mobile",
                    "security_level": "high"
                }
            
            # Create mobile session
            session = await self.session_abstraction.create_session(context, session_data)
            
            # Create access token
            token = await self.session_abstraction.create_session_token(
                session.session_id,
                "access",
                context
            )
            
            return {
                "success": True,
                "workflow": "mobile_session",
                "session_id": session.session_id,
                "session_type": session.session_type.value,
                "security_level": session.security_level.value,
                "token_id": token.token_id,
                "expires_at": session.expires_at.isoformat() if session.expires_at else None
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_mobile_session_workflow",
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None)
            return {
                "success": False,
                "workflow": "mobile_session",
                "error": str(e),
                "error_code": "MOBILE_SESSION_WORKFLOW_ERROR"
            }
    
    async def _comprehensive_session_workflow(self, 
                                            context: SessionContext, 
                                            session_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Comprehensive session workflow for infrastructure-level session management."""
        try:
            if not session_data:
                session_data = {
                    "session_type": "user",
                    "security_level": "high"
                }
            
            # Create comprehensive session
            session = await self.session_abstraction.create_session(context, session_data)
            
            # Create access token
            token = await self.session_abstraction.create_session_token(
                session.session_id,
                "access",
                context
            )
            
            # Get session analytics
            analytics = await self.session_abstraction.get_session_analytics(session.session_id, context)
            
            return {
                "success": True,
                "workflow": "comprehensive_session",
                "session_id": session.session_id,
                "session_type": session.session_type.value,
                "security_level": session.security_level.value,
                "token_id": token.token_id,
                "expires_at": session.expires_at.isoformat() if session.expires_at else None,
                "analytics": {
                    "total_requests": analytics.total_requests,
                    "successful_requests": analytics.successful_requests,
                    "failed_requests": analytics.failed_requests,
                    "average_response_time": analytics.average_response_time,
                    "security_events": analytics.security_events
                }
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_comprehensive_session_workflow",
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None)
            return {
                "success": False,
                "workflow": "comprehensive_session",
                "error": str(e),
                "error_code": "COMPREHENSIVE_SESSION_WORKFLOW_ERROR"
            }
    
    def _analyze_session_status(self, session: Session, analytics: SessionAnalytics) -> Dict[str, Any]:
        """Analyze session status and provide insights."""
        return {
            "session_health": self._calculate_session_health(session, analytics),
            "security_assessment": self._assess_session_security(session),
            "performance_metrics": {
                "success_rate": (analytics.successful_requests / max(analytics.total_requests, 1)) * 100,
                "average_response_time": analytics.average_response_time,
                "security_events": analytics.security_events
            },
            "recommendations": self._generate_session_recommendations(session, analytics)
        }
    
    def _calculate_session_health(self, session: Session, analytics: SessionAnalytics) -> str:
        """Calculate session health score."""
        if session.status != SessionStatus.ACTIVE:
            return "unhealthy"
        
        success_rate = (analytics.successful_requests / max(analytics.total_requests, 1)) * 100
        if success_rate >= 95 and analytics.security_events == 0:
            return "excellent"
        elif success_rate >= 90 and analytics.security_events <= 1:
            return "good"
        elif success_rate >= 80:
            return "fair"
        else:
            return "poor"
    
    def _assess_session_security(self, session: Session) -> Dict[str, Any]:
        """Assess session security level."""
        return {
            "security_level": session.security_level.value,
            "is_secure": session.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL],
            "recommendations": self._get_security_recommendations(session)
        }
    
    def _generate_session_recommendations(self, session: Session, analytics: SessionAnalytics) -> List[str]:
        """Generate session recommendations."""
        recommendations = []
        
        if session.status != SessionStatus.ACTIVE:
            recommendations.append("Session is not active - consider refreshing or recreating")
        
        if analytics.security_events > 0:
            recommendations.append("Security events detected - review session security")
        
        if analytics.average_response_time > 1000:
            recommendations.append("High response times detected - consider performance optimization")
        
        if not recommendations:
            recommendations.append("Session is operating normally")
        
        return recommendations
    
    def _get_security_recommendations(self, session: Session) -> List[str]:
        """Get security recommendations for session."""
        recommendations = []
        
        if session.security_level == SecurityLevel.LOW:
            recommendations.append("Consider upgrading to higher security level")
        
        if session.security_level == SecurityLevel.MEDIUM:
            recommendations.append("Security level is adequate for most use cases")
        
        if session.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            recommendations.append("High security level is appropriate for sensitive operations")
        
        return recommendations