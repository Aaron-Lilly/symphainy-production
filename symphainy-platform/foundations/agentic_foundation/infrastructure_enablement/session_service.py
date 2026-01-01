"""
Session Service - Agent-specific session management business logic

Handles agent-specific session management, session security,
and session-based decision making for agent operations.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.session_protocol import (
    SessionContext, Session, SessionToken, SessionAnalytics,
    SessionStatus, SessionType, SecurityLevel
)
from foundations.public_works_foundation.infrastructure_abstractions.session_abstraction import SessionAbstraction
from foundations.public_works_foundation.composition_services.session_composition_service import SessionCompositionService

# Import utility mixins (minimal - AgenticFoundationService wraps calls)
from bases.mixins.utility_access_mixin import UtilityAccessMixin
from bases.mixins.performance_monitoring_mixin import PerformanceMonitoringMixin


class SessionService(UtilityAccessMixin, PerformanceMonitoringMixin):
    """
    Session Service - Agent-specific session management business logic
    
    Handles agent-specific session management and session-based decision making.
    This service applies session management to agent operations and behaviors.
    """
    
    def __init__(self, 
                 session_abstraction: SessionAbstraction,
                 session_composition_service: SessionCompositionService,
                 curator_foundation=None,
                 di_container=None):
        """Initialize Session Service."""
        if not di_container:
            raise ValueError("DI Container is required for SessionService initialization")
        
        # Initialize utility mixins (minimal - AgenticFoundationService wraps calls)
        self._init_utility_access(di_container)
        self._init_performance_monitoring(di_container)
        
        self.session_abstraction = session_abstraction
        self.session_composition_service = session_composition_service
        self.curator_foundation = curator_foundation
        self.service_name = "session_service"
        
        # Agent-specific session management
        self.agent_session_management = {
            "llm_session": self._manage_llm_session,
            "mcp_session": self._manage_mcp_session,
            "tool_session": self._manage_tool_session,
            "agent_session": self._manage_agent_session
        }
        
        self.logger.info("Initialized Session Service for agent-specific session management")
    
    async def manage_agent_session(self, 
                                  operation_type: str,
                                  context: SessionContext,
                                  operation_data: Dict[str, Any] = None,
                                  user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage session for agent operations."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("manage_agent_session_start", success=True, details={"operation_type": operation_type})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_session", "write"):
                        await self.record_health_metric("manage_agent_session_access_denied", 1.0, {"operation_type": operation_type})
                        await self.log_operation_with_telemetry("manage_agent_session_complete", success=False)
                        return {"success": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("manage_agent_session_tenant_denied", 1.0, {"operation_type": operation_type})
                            await self.log_operation_with_telemetry("manage_agent_session_complete", success=False)
                            return {"success": False, "error": "Tenant access denied"}
            
            self.logger.debug(f"Managing session for {operation_type} operation")
            
            # Get management function
            management_func = self.agent_session_management.get(operation_type)
            if not management_func:
                await self.record_health_metric("manage_agent_session_unknown_operation", 1.0, {"operation_type": operation_type})
                await self.log_operation_with_telemetry("manage_agent_session_complete", success=False)
                return {
                    "success": False,
                    "error": f"Unknown operation type: {operation_type}",
                    "operation_type": operation_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Manage session
            result = await management_func(context, operation_data)
            
            # Add service metadata
            result.update({
                "operation_type": operation_type,
                "managed_at": datetime.utcnow().isoformat(),
                "session_service": self.service_name
            })
            
            # Record success metric
            await self.record_health_metric("manage_agent_session_success", 1.0, {"operation_type": operation_type, "success": result.get("success", False)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("manage_agent_session_complete", success=True, details={"operation_type": operation_type})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "manage_agent_session", details={"operation_type": operation_type})
            self.logger.error(f"Session management failed for {operation_type}: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation_type": operation_type,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def create_agent_session(self, 
                                 agent_id: str,
                                 context: SessionContext,
                                 session_type: SessionType = SessionType.AGENT,
                                 security_level: SecurityLevel = SecurityLevel.HIGH,
                                 user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create session for agent operations."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("create_agent_session_start", success=True, details={"agent_id": agent_id})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_session", "write"):
                        await self.record_health_metric("create_agent_session_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("create_agent_session_complete", success=False)
                        return {"success": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("create_agent_session_tenant_denied", 1.0, {"agent_id": agent_id})
                            await self.log_operation_with_telemetry("create_agent_session_complete", success=False)
                            return {"success": False, "error": "Tenant access denied"}
            
            self.logger.debug(f"Creating session for agent {agent_id}")
            
            # Create agent-specific context
            agent_context = SessionContext(
                service_id=context.service_id,
                agent_id=agent_id,
                tenant_id=context.tenant_id,
                environment=context.environment,
                region=context.region,
                metadata=context.metadata or {}
            )
            
            # Create session with enhanced security
            session_data = {
                "session_type": session_type.value,
                "security_level": security_level.value,
                "agent_id": agent_id,
                "created_by": self.service_name,
                "metadata": {
                    "agent_session": True,
                    "security_enhanced": True
                }
            }
            
            result = await self.session_composition_service.create_session_with_security(
                agent_context,
                session_data,
                security_level
            )
            
            # Record success metric
            await self.record_health_metric("create_agent_session_success", 1.0, {"agent_id": agent_id, "session_type": session_type.value})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("create_agent_session_complete", success=True, details={"agent_id": agent_id})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "create_agent_session", details={"agent_id": agent_id})
            self.logger.error(f"Agent session creation failed for {agent_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def validate_agent_session(self, 
                                   session_id: str,
                                   agent_id: str,
                                   context: SessionContext,
                                   user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate agent session."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("validate_agent_session_start", success=True, details={"session_id": session_id, "agent_id": agent_id})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_session", "read"):
                        await self.record_health_metric("validate_agent_session_access_denied", 1.0, {"session_id": session_id})
                        await self.log_operation_with_telemetry("validate_agent_session_complete", success=False)
                        return {"success": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("validate_agent_session_tenant_denied", 1.0, {"session_id": session_id})
                            await self.log_operation_with_telemetry("validate_agent_session_complete", success=False)
                            return {"success": False, "error": "Tenant access denied"}
            
            self.logger.debug(f"Validating session {session_id} for agent {agent_id}")
            
            # Create agent-specific context
            agent_context = SessionContext(
                service_id=context.service_id,
                agent_id=agent_id,
                tenant_id=context.tenant_id,
                environment=context.environment,
                region=context.region,
                metadata=context.metadata or {}
            )
            
            # Validate session
            is_valid = await self.session_abstraction.validate_session(session_id, agent_context)
            
            # Record success metric
            await self.record_health_metric("validate_agent_session_success", 1.0, {"session_id": session_id, "is_valid": is_valid})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("validate_agent_session_complete", success=True, details={"session_id": session_id, "is_valid": is_valid})
            
            if is_valid:
                # Get session details
                session = await self.session_abstraction.get_session(session_id, agent_context)
                if session:
                    return {
                        "success": True,
                        "session_id": session_id,
                        "agent_id": agent_id,
                        "session_status": session.status.value,
                        "session_type": session.session_type.value,
                        "security_level": session.security_level.value,
                        "is_active": session.status == SessionStatus.ACTIVE,
                        "expires_at": session.expires_at.isoformat() if session.expires_at else None
                    }
            
            return {
                "success": False,
                "session_id": session_id,
                "agent_id": agent_id,
                "is_valid": False,
                "error": "Session validation failed"
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "validate_agent_session", details={"session_id": session_id, "agent_id": agent_id})
            self.logger.error(f"Agent session validation failed for {session_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_agent_session_analytics(self, 
                                         session_id: str,
                                         agent_id: str,
                                         context: SessionContext) -> Dict[str, Any]:
        """Get session analytics for agent."""
        try:
            self.logger.debug(f"Getting session analytics for agent {agent_id}")
            
            # Create agent-specific context
            agent_context = SessionContext(
                service_id=context.service_id,
                agent_id=agent_id,
                tenant_id=context.tenant_id,
                environment=context.environment,
                region=context.region,
                metadata=context.metadata or {}
            )
            
            # Get session analytics
            analytics = await self.session_abstraction.get_session_analytics(session_id, agent_context)
            
            # Analyze analytics
            analytics_analysis = self._analyze_session_analytics(analytics)
            
            return {
                "success": True,
                "session_id": session_id,
                "agent_id": agent_id,
                "analytics": {
                    "total_requests": analytics.total_requests,
                    "successful_requests": analytics.successful_requests,
                    "failed_requests": analytics.failed_requests,
                    "average_response_time": analytics.average_response_time,
                    "security_events": analytics.security_events,
                    "last_activity": analytics.last_activity.isoformat()
                },
                "analysis": analytics_analysis,
                "collected_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_session_analytics", details={"agent_id": agent_id})
            self.logger.error(f"Failed to get session analytics for agent {agent_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def refresh_agent_session(self, 
                                   session_id: str,
                                   agent_id: str,
                                   context: SessionContext,
                                   user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Refresh agent session."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("refresh_agent_session_start", success=True, details={"session_id": session_id, "agent_id": agent_id})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_session", "write"):
                        await self.record_health_metric("refresh_agent_session_access_denied", 1.0, {"session_id": session_id})
                        await self.log_operation_with_telemetry("refresh_agent_session_complete", success=False)
                        return {"success": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("refresh_agent_session_tenant_denied", 1.0, {"session_id": session_id})
                            await self.log_operation_with_telemetry("refresh_agent_session_complete", success=False)
                            return {"success": False, "error": "Tenant access denied"}
            
            self.logger.debug(f"Refreshing session {session_id} for agent {agent_id}")
            
            # Create agent-specific context
            agent_context = SessionContext(
                service_id=context.service_id,
                agent_id=agent_id,
                tenant_id=context.tenant_id,
                environment=context.environment,
                region=context.region,
                metadata=context.metadata or {}
            )
            
            # Refresh session
            refreshed_session = await self.session_abstraction.refresh_session(session_id, agent_context)
            
            # Record success metric
            await self.record_health_metric("refresh_agent_session_success", 1.0, {"session_id": session_id, "refreshed": refreshed_session is not None})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("refresh_agent_session_complete", success=True, details={"session_id": session_id})
            
            if refreshed_session:
                return {
                    "success": True,
                    "session_id": session_id,
                    "agent_id": agent_id,
                    "session_status": refreshed_session.status.value,
                    "expires_at": refreshed_session.expires_at.isoformat() if refreshed_session.expires_at else None,
                    "refreshed_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "session_id": session_id,
                    "agent_id": agent_id,
                    "error": "Session refresh failed"
                }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "refresh_agent_session", details={"session_id": session_id})
            self.logger.error(f"Agent session refresh failed for {session_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def revoke_agent_session(self, 
                                 session_id: str,
                                 agent_id: str,
                                 context: SessionContext,
                                 user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Revoke agent session."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("revoke_agent_session_start", success=True, details={"session_id": session_id, "agent_id": agent_id})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_session", "write"):
                        await self.record_health_metric("revoke_agent_session_access_denied", 1.0, {"session_id": session_id})
                        await self.log_operation_with_telemetry("revoke_agent_session_complete", success=False)
                        return {"success": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("revoke_agent_session_tenant_denied", 1.0, {"session_id": session_id})
                            await self.log_operation_with_telemetry("revoke_agent_session_complete", success=False)
                            return {"success": False, "error": "Tenant access denied"}
            
            self.logger.debug(f"Revoking session {session_id} for agent {agent_id}")
            
            # Create agent-specific context
            agent_context = SessionContext(
                service_id=context.service_id,
                agent_id=agent_id,
                tenant_id=context.tenant_id,
                environment=context.environment,
                region=context.region,
                metadata=context.metadata or {}
            )
            
            # Revoke session
            revoked = await self.session_abstraction.revoke_session(session_id, agent_context)
            
            # Record success metric
            await self.record_health_metric("revoke_agent_session_success", 1.0, {"session_id": session_id, "revoked": revoked})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("revoke_agent_session_complete", success=True, details={"session_id": session_id, "revoked": revoked})
            
            return {
                "success": revoked,
                "session_id": session_id,
                "agent_id": agent_id,
                "revoked": revoked,
                "revoked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "revoke_agent_session", details={"session_id": session_id})
            self.logger.error(f"Agent session revocation failed for {session_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check session service health."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("health_check_start", success=True)
            
            self.logger.debug("Checking session service health")
            
            # Check underlying services
            abstraction_health = await self.session_abstraction.health_check()
            composition_health = await self.session_composition_service.health_check()
            
            result = {
                "status": "healthy" if all(
                    h.get("status") == "healthy" 
                    for h in [abstraction_health, composition_health]
                ) else "unhealthy",
                "service": self.service_name,
                "abstraction_health": abstraction_health,
                "composition_health": composition_health,
                "management_types": list(self.agent_session_management.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("health_check_success", 1.0, {"status": result["status"]})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("health_check_complete", success=True, details={"status": result["status"]})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "health_check")
            self.logger.error(f"Session service health check failed: {e}")
            return {
                "status": "error",
                "service": self.service_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # AGENT-SPECIFIC SESSION MANAGEMENT
    # ============================================================================
    
    async def _manage_llm_session(self, 
                                context: SessionContext, 
                                operation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage session for LLM operations."""
        try:
            # Create or get LLM session
            session_data = {
                "session_type": "agent",
                "security_level": "high",
                "operation_type": "llm",
                "metadata": operation_data or {}
            }
            
            result = await self.session_composition_service.orchestrate_session_management(
                "agent_session",
                context,
                session_data
            )
            
            return {
                "success": result.get("success", False),
                "session_id": result.get("session_id"),
                "session_type": result.get("session_type"),
                "security_level": result.get("security_level"),
                "token_id": result.get("token_id"),
                "management_type": "llm_session"
            }
            
        except Exception as e:
            # Note: Private helper method - error is logged by calling method
            return {
                "success": False,
                "error": str(e),
                "management_type": "llm_session"
            }
    
    async def _manage_mcp_session(self, 
                                context: SessionContext, 
                                operation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage session for MCP operations."""
        try:
            # Create or get MCP session
            session_data = {
                "session_type": "agent",
                "security_level": "high",
                "operation_type": "mcp",
                "metadata": operation_data or {}
            }
            
            result = await self.session_composition_service.orchestrate_session_management(
                "agent_session",
                context,
                session_data
            )
            
            return {
                "success": result.get("success", False),
                "session_id": result.get("session_id"),
                "session_type": result.get("session_type"),
                "security_level": result.get("security_level"),
                "token_id": result.get("token_id"),
                "management_type": "mcp_session"
            }
            
        except Exception as e:
            # Note: Private helper method - error is logged by calling method
            return {
                "success": False,
                "error": str(e),
                "management_type": "mcp_session"
            }
    
    async def _manage_tool_session(self, 
                                 context: SessionContext, 
                                 operation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage session for Tool operations."""
        try:
            # Create or get Tool session
            session_data = {
                "session_type": "agent",
                "security_level": "high",
                "operation_type": "tool",
                "metadata": operation_data or {}
            }
            
            result = await self.session_composition_service.orchestrate_session_management(
                "agent_session",
                context,
                session_data
            )
            
            return {
                "success": result.get("success", False),
                "session_id": result.get("session_id"),
                "session_type": result.get("session_type"),
                "security_level": result.get("security_level"),
                "token_id": result.get("token_id"),
                "management_type": "tool_session"
            }
            
        except Exception as e:
            # Note: Private helper method - error is logged by calling method
            return {
                "success": False,
                "error": str(e),
                "management_type": "tool_session"
            }
    
    async def _manage_agent_session(self, 
                                  context: SessionContext, 
                                  operation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage session for general agent operations."""
        try:
            # Create or get general agent session
            session_data = {
                "session_type": "agent",
                "security_level": "high",
                "operation_type": "agent",
                "metadata": operation_data or {}
            }
            
            result = await self.session_composition_service.orchestrate_session_management(
                "agent_session",
                context,
                session_data
            )
            
            return {
                "success": result.get("success", False),
                "session_id": result.get("session_id"),
                "session_type": result.get("session_type"),
                "security_level": result.get("security_level"),
                "token_id": result.get("token_id"),
                "management_type": "agent_session"
            }
            
        except Exception as e:
            # Note: Private helper method - error is logged by calling method
            return {
                "success": False,
                "error": str(e),
                "management_type": "agent_session"
            }
    
    def _analyze_session_analytics(self, analytics: SessionAnalytics) -> Dict[str, Any]:
        """Analyze session analytics and provide insights."""
        return {
            "performance_score": self._calculate_performance_score(analytics),
            "security_score": self._calculate_security_score(analytics),
            "reliability_score": self._calculate_reliability_score(analytics),
            "recommendations": self._generate_analytics_recommendations(analytics)
        }
    
    def _calculate_performance_score(self, analytics: SessionAnalytics) -> float:
        """Calculate performance score from analytics."""
        if analytics.total_requests == 0:
            return 0.0
        
        success_rate = (analytics.successful_requests / analytics.total_requests) * 100
        response_time_score = max(0, 100 - (analytics.average_response_time / 10))
        
        return (success_rate + response_time_score) / 2
    
    def _calculate_security_score(self, analytics: SessionAnalytics) -> float:
        """Calculate security score from analytics."""
        if analytics.security_events == 0:
            return 100.0
        elif analytics.security_events <= 2:
            return 80.0
        elif analytics.security_events <= 5:
            return 60.0
        else:
            return 40.0
    
    def _calculate_reliability_score(self, analytics: SessionAnalytics) -> float:
        """Calculate reliability score from analytics."""
        if analytics.total_requests == 0:
            return 0.0
        
        success_rate = (analytics.successful_requests / analytics.total_requests) * 100
        return success_rate
    
    def _generate_analytics_recommendations(self, analytics: SessionAnalytics) -> List[str]:
        """Generate recommendations from analytics."""
        recommendations = []
        
        if analytics.security_events > 0:
            recommendations.append("Security events detected - review session security")
        
        if analytics.average_response_time > 1000:
            recommendations.append("High response times detected - consider performance optimization")
        
        if analytics.failed_requests > analytics.successful_requests:
            recommendations.append("High failure rate detected - review session reliability")
        
        if not recommendations:
            recommendations.append("Session analytics are within normal parameters")
        
        return recommendations
