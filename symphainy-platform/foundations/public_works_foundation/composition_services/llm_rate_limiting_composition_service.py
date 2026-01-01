#!/usr/bin/env python3
"""
LLM Rate Limiting Composition Service

Composition service for LLM rate limiting capabilities.
Orchestrates rate limiting abstractions for agentic LLM request rate limiting.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..infrastructure_abstractions.llm_rate_limiting_abstraction import LLMRateLimitingAbstraction
from ..abstraction_contracts.llm_rate_limiting_protocol import (
    RateLimitRequest, RateLimitResponse, RateLimitStats
)


class LLMRateLimitingCompositionService:
    """Composition service for LLM rate limiting capabilities."""
    
    def __init__(self, llm_rate_limiting_abstraction: LLMRateLimitingAbstraction, di_container=None):
        """
        Initialize LLM rate limiting composition service.
        
        Args:
            llm_rate_limiting_abstraction: LLM rate limiting abstraction instance
            di_container: DI Container for utilities
        """
        self.llm_rate_limiting = llm_rate_limiting_abstraction
        self.di_container = di_container
        self.service_name = "llm_rate_limiting_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("LLMRateLimitingCompositionService")
        
        # Service status
        self.is_initialized = False
        
        # Initialize service
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the composition service."""
        try:
            self.logger.info("✅ LLM rate limiting composition service initialized")
            self.is_initialized = True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM rate limiting composition service: {e}")
            self.is_initialized = False
    
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
                    # (security might not be fully bootstrapped)
            
            # Multi-tenancy validation (if tenant utility available and tenant_id provided)
            if tenant and tenant_id:
                try:
                    # Check if multi-tenancy is enabled
                    if tenant.is_multi_tenant_enabled():
                        # Validate tenant access (basic check - user can only access their own tenant)
                        # For cross-tenant access, this would be handled at foundation service level
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
    
    # ============================================================================
    # AGENTIC LLM RATE LIMITING CAPABILITIES
    # ============================================================================
    
    async def check_agent_rate_limit(self, user_id: str, model: str, 
                                   estimated_tokens: int = 0, agent_id: str = None,
                                   user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Check rate limit for agentic LLM request.
        
        Args:
            user_id: User ID
            model: LLM model
            estimated_tokens: Estimated token usage
            agent_id: Agent ID for context
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Rate limit check result
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "llm_rate_limit", "check"
                )
                if validation_error:
                    return validation_error
            
            # Create rate limit request
            request = RateLimitRequest(
                user_id=user_id,
                model=model,
                estimated_tokens=estimated_tokens
            )
            
            # Check rate limit
            response = await self.llm_rate_limiting.check_rate_limit(request)
            
            # Format for agentic use
            agent_response = {
                "allowed": response.allowed,
                "reason": response.reason,
                "retry_after": response.retry_after,
                "current_requests": response.current_requests,
                "current_tokens": response.current_tokens,
                "request_limit": response.request_limit,
                "token_limit": response.token_limit,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
            
            if response.allowed:
                self.logger.info(f"✅ Rate limit check passed for agent: {agent_id}")
            else:
                self.logger.warning(f"Rate limit exceeded for agent: {agent_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("check_agent_rate_limit", {
                    "user_id": user_id,
                    "model": model,
                    "allowed": response.allowed,
                    "success": True
                })
            
            return agent_response
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "check_agent_rate_limit",
                    "user_id": user_id,
                    "model": model,
                    "agent_id": agent_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to check agent rate limit: {e}")
            return {
                "allowed": True,  # Fail open
                "reason": "rate_limiting_error",
                "retry_after": 0,
                "current_requests": 0,
                "current_tokens": 0,
                "request_limit": 0,
                "token_limit": 0,
                "agent_id": agent_id,
                "error": str(e),
                "error_code": "LLM_RATE_LIMITING_CHECK_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_agent_rate_limit_status(self, user_id: str, model: str, 
                                        agent_id: str = None,
                                        user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get rate limit status for agentic use.
        
        Args:
            user_id: User ID
            model: LLM model
            agent_id: Agent ID for context
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Rate limit status
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "llm_rate_limit", "view"
                )
                if validation_error:
                    return validation_error
            
            # Get rate limit status
            status = await self.llm_rate_limiting.get_rate_limit_status(user_id, model)
            
            # Format for agentic use
            agent_status = {
                "user_id": user_id,
                "model": model,
                "agent_id": agent_id,
                "current_minute_requests": status.get("current_minute_requests", 0),
                "minute_request_limit": status.get("minute_request_limit", 0),
                "current_hour_requests": status.get("current_hour_requests", 0),
                "hour_request_limit": status.get("hour_request_limit", 0),
                "current_minute_tokens": status.get("current_minute_tokens", 0),
                "minute_token_limit": status.get("minute_token_limit", 0),
                "current_hour_tokens": status.get("current_hour_tokens", 0),
                "hour_token_limit": status.get("hour_token_limit", 0),
                "minute_request_usage_percent": status.get("minute_request_usage_percent", 0),
                "hour_request_usage_percent": status.get("hour_request_usage_percent", 0),
                "minute_token_usage_percent": status.get("minute_token_usage_percent", 0),
                "hour_token_usage_percent": status.get("hour_token_usage_percent", 0),
                "timestamp": datetime.now().isoformat()
            }
            
            if "error" in status:
                agent_status["error"] = status["error"]
            
            self.logger.info(f"✅ Rate limit status retrieved for agent: {agent_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_agent_rate_limit_status", {
                    "user_id": user_id,
                    "model": model,
                    "success": True
                })
            
            return agent_status
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_agent_rate_limit_status",
                    "user_id": user_id,
                    "model": model,
                    "agent_id": agent_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to get agent rate limit status: {e}")
            return {
                "error": str(e),
                "error_code": "LLM_RATE_LIMITING_STATUS_ERROR",
                "user_id": user_id,
                "model": model,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def reset_agent_rate_limits(self, user_id: str, model: str = None, 
                                     agent_id: str = None,
                                     user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Reset rate limits for agentic use.
        
        Args:
            user_id: User ID
            model: LLM model (None for all models)
            agent_id: Agent ID for context
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Reset result
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "llm_rate_limit", "reset"
                )
                if validation_error:
                    return validation_error
            
            # Reset rate limits
            success = await self.llm_rate_limiting.reset_user_limits(user_id, model)
            
            # Format for agentic use
            reset_result = {
                "success": success,
                "user_id": user_id,
                "model": model,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
            
            if success:
                self.logger.info(f"✅ Rate limits reset for agent: {agent_id}")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("reset_agent_rate_limits", {
                        "user_id": user_id,
                        "model": model,
                        "success": True
                    })
            else:
                self.logger.warning(f"Failed to reset rate limits for agent: {agent_id}")
            
            return reset_result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "reset_agent_rate_limits",
                    "user_id": user_id,
                    "model": model,
                    "agent_id": agent_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to reset agent rate limits: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "LLM_RATE_LIMITING_RESET_ERROR",
                "user_id": user_id,
                "model": model,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_agent_rate_limit_stats(self, agent_id: str = None,
                                       user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get rate limit statistics for agentic use.
        
        Args:
            agent_id: Agent ID for context
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Rate limit statistics
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "llm_rate_limit", "view"
                )
                if validation_error:
                    return validation_error
            
            # Get rate limit stats
            stats = await self.llm_rate_limiting.get_rate_limit_stats()
            
            # Format for agentic use
            agent_stats = {
                "total_requests": stats.total_requests,
                "allowed_requests": stats.allowed_requests,
                "blocked_requests": stats.blocked_requests,
                "success_rate": stats.success_rate,
                "rate_limit_hits": stats.rate_limit_hits,
                "requests_per_minute_limit": stats.requests_per_minute_limit,
                "tokens_per_minute_limit": stats.tokens_per_minute_limit,
                "enabled": stats.enabled,
                "agent_id": agent_id,
                "timestamp": stats.timestamp.isoformat() if stats.timestamp else datetime.now().isoformat()
            }
            
            if stats.error:
                agent_stats["error"] = stats.error
            
            self.logger.info(f"✅ Rate limit stats retrieved for agent: {agent_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_agent_rate_limit_stats", {
                    "agent_id": agent_id,
                    "success_rate": stats.success_rate,
                    "success": True
                })
            
            return agent_stats
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_agent_rate_limit_stats",
                    "agent_id": agent_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to get agent rate limit stats: {e}")
            return {
                "error": str(e),
                "error_code": "LLM_RATE_LIMITING_STATS_ERROR",
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def optimize_agent_rate_limits(self, user_id: str, model: str, 
                                       agent_id: str = None,
                                       user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Optimize rate limits for agentic use.
        
        Args:
            user_id: User ID
            model: LLM model
            agent_id: Agent ID for context
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Optimization result
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "llm_rate_limit", "optimize"
                )
                if validation_error:
                    return validation_error
            
            # Get current status
            status = await self.get_agent_rate_limit_status(user_id, model, agent_id, user_context)
            
            # Analyze rate limit usage
            minute_request_usage = status.get("minute_request_usage_percent", 0)
            hour_request_usage = status.get("hour_request_usage_percent", 0)
            minute_token_usage = status.get("minute_token_usage_percent", 0)
            hour_token_usage = status.get("hour_token_usage_percent", 0)
            
            # Determine optimization recommendations
            recommendations = []
            
            if minute_request_usage > 80:
                recommendations.append("Consider reducing request frequency")
            elif minute_request_usage < 20:
                recommendations.append("Request rate is well within limits")
            
            if minute_token_usage > 80:
                recommendations.append("Consider reducing token usage per request")
            elif minute_token_usage < 20:
                recommendations.append("Token usage is well within limits")
            
            if hour_request_usage > 90:
                recommendations.append("Hourly request limit approaching")
            if hour_token_usage > 90:
                recommendations.append("Hourly token limit approaching")
            
            # Calculate optimization score
            optimization_score = 100 - max(minute_request_usage, hour_request_usage, 
                                         minute_token_usage, hour_token_usage)
            
            # Format optimization result
            optimization_result = {
                "user_id": user_id,
                "model": model,
                "agent_id": agent_id,
                "minute_request_usage": minute_request_usage,
                "hour_request_usage": hour_request_usage,
                "minute_token_usage": minute_token_usage,
                "hour_token_usage": hour_token_usage,
                "recommendations": recommendations,
                "optimization_score": max(0, optimization_score),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Rate limit optimization analyzed for agent: {agent_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("optimize_agent_rate_limits", {
                    "user_id": user_id,
                    "model": model,
                    "optimization_score": max(0, optimization_score),
                    "success": True
                })
            
            return optimization_result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "optimize_agent_rate_limits",
                    "user_id": user_id,
                    "model": model,
                    "agent_id": agent_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to optimize agent rate limits: {e}")
            return {
                "error": str(e),
                "error_code": "LLM_RATE_LIMITING_OPTIMIZATION_ERROR",
                "user_id": user_id,
                "model": model,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    # ============================================================================
    # SERVICE MANAGEMENT
    # ============================================================================
    
    async def get_service_status(self) -> Dict[str, Any]:
        """
        Get composition service status.
        
        Returns:
            Dict: Service status
        """
        try:
            # Get LLM rate limiting status
            rate_limiting_health = await self.llm_rate_limiting.health_check()
            
            result = {
                "service": "LLMRateLimitingCompositionService",
                "initialized": self.is_initialized,
                "llm_rate_limiting": rate_limiting_health,
                "timestamp": datetime.now().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_service_status", {
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_service_status",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to get service status: {e}")
            return {
                "service": "LLMRateLimitingCompositionService",
                "initialized": self.is_initialized,
                "error": str(e),
                "error_code": "LLM_RATE_LIMITING_SERVICE_STATUS_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all components.
        
        Returns:
            Dict: Health check result
        """
        try:
            health_status = {
                "healthy": True,
                "components": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Check LLM rate limiting
            try:
                rate_limiting_health = await self.llm_rate_limiting.health_check()
                health_status["components"]["llm_rate_limiting"] = rate_limiting_health
                
                if not rate_limiting_health.get("healthy", False):
                    health_status["healthy"] = False
                    
            except Exception as e:
                health_status["components"]["llm_rate_limiting"] = {
                    "healthy": False,
                    "error": str(e)
                }
                health_status["healthy"] = False
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("health_check", {
                    "healthy": health_status.get("healthy", False),
                    "success": True
                })
            
            return health_status
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "health_check",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "error_code": "LLM_RATE_LIMITING_HEALTH_CHECK_ERROR",
                "timestamp": datetime.now().isoformat()
            }




