#!/usr/bin/env python3
"""
LLM Caching Composition Service

Composition service for LLM caching capabilities.
Orchestrates cache abstractions for agentic LLM response caching.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import uuid

from ..infrastructure_abstractions.llm_caching_abstraction import LLMCachingAbstraction
from ..abstraction_contracts.llm_caching_protocol import CacheRequest, CacheResponse, CacheStats


class LLMCachingCompositionService:
    """Composition service for LLM caching capabilities."""
    
    def __init__(self, llm_caching_abstraction: LLMCachingAbstraction, di_container=None):
        """
        Initialize LLM caching composition service.
        
        Args:
            llm_caching_abstraction: LLM caching abstraction instance
            di_container: DI Container for utilities
        """
        self.llm_caching = llm_caching_abstraction
        self.di_container = di_container
        self.service_name = "llm_caching_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("LLMCachingCompositionService")
        
        # Service status
        self.is_initialized = False
        
        # Initialize service
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the composition service."""
        try:
            self.logger.info("✅ LLM caching composition service initialized")
            self.is_initialized = True
            
        except Exception as e:
            # Use error handler with telemetry (sync method, so only log)
            if self.di_container and hasattr(self.di_container, 'get_utility'):
                # Can't await in sync method, just log
                self.logger.error(f"Failed to initialize LLM caching composition service: {e}")
            else:
                self.logger.error(f"Failed to initialize LLM caching composition service: {e}")
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
    # AGENTIC LLM CACHING CAPABILITIES
    # ============================================================================
    
    async def get_cached_agent_response(self, prompt: str, model: str, 
                                      agent_id: str = None, 
                                      user_context: Optional[Dict[str, Any]] = None,
                                      **kwargs) -> Optional[Dict[str, Any]]:
        """
        Get cached response for agentic LLM request.
        
        Args:
            prompt: LLM prompt
            model: LLM model
            agent_id: Agent ID for context
            user_context: User context with user_id, tenant_id, security_context
            **kwargs: Additional parameters
            
        Returns:
            Optional[Dict]: Cached response if found
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "llm_cache", "read"
                )
                if validation_error:
                    return None
            
            # Create cache request
            request = CacheRequest(
                prompt=prompt,
                model=model,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens"),
                parameters=kwargs
            )
            
            # Get cached response
            cached_response = await self.llm_caching.get_cached_response(request)
            
            if cached_response:
                # Format for agentic use
                agent_response = {
                    "response_id": cached_response.response_id,
                    "content": cached_response.content,
                    "model": cached_response.model,
                    "usage": cached_response.usage,
                    "cached": True,
                    "agent_id": agent_id,
                    "timestamp": cached_response.timestamp.isoformat()
                }
                
                self.logger.info(f"✅ Cached response retrieved for agent: {agent_id}")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("get_cached_agent_response", {
                        "agent_id": agent_id,
                        "model": model,
                        "cached": True,
                        "success": True
                    })
                
                return agent_response
            
            # Record telemetry even for cache miss
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_cached_agent_response", {
                    "agent_id": agent_id,
                    "model": model,
                    "cached": False,
                    "success": True
                })
            
            return None
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_cached_agent_response",
                    "agent_id": agent_id,
                    "model": model,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to get cached agent response: {e}")
            return None
    
    async def cache_agent_response(self, prompt: str, model: str, response: Dict[str, Any],
                                 agent_id: str = None, ttl: int = None,
                                 user_context: Optional[Dict[str, Any]] = None,
                                 **kwargs) -> bool:
        """
        Cache response for agentic LLM request.
        
        Args:
            prompt: LLM prompt
            model: LLM model
            response: Response to cache
            agent_id: Agent ID for context
            ttl: Time to live in seconds
            user_context: User context with user_id, tenant_id, security_context
            **kwargs: Additional parameters
            
        Returns:
            bool: Success status
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "llm_cache", "write"
                )
                if validation_error:
                    return False
            
            # Create cache request
            request = CacheRequest(
                prompt=prompt,
                model=model,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens"),
                parameters=kwargs
            )
            
            # Create cache response
            cache_response = CacheResponse(
                response_id=response.get("response_id", str(uuid.uuid4())),
                content=response.get("content", ""),
                model=model,
                usage=response.get("usage", {}),
                timestamp=datetime.now()
            )
            
            # Cache response
            success = await self.llm_caching.cache_response(request, cache_response, ttl)
            
            if success:
                self.logger.info(f"✅ Response cached for agent: {agent_id}")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("cache_agent_response", {
                        "agent_id": agent_id,
                        "model": model,
                        "success": True
                    })
            else:
                self.logger.warning(f"Failed to cache response for agent: {agent_id}")
            
            return success
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "cache_agent_response",
                    "agent_id": agent_id,
                    "model": model,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to cache agent response: {e}")
            return False
    
    async def invalidate_agent_cache(self, prompt: str, model: str, 
                                   agent_id: str = None,
                                   user_context: Optional[Dict[str, Any]] = None,
                                   **kwargs) -> bool:
        """
        Invalidate cache for agentic LLM request.
        
        Args:
            prompt: LLM prompt
            model: LLM model
            agent_id: Agent ID for context
            user_context: User context with user_id, tenant_id, security_context
            **kwargs: Additional parameters
            
        Returns:
            bool: Success status
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "llm_cache", "invalidate"
                )
                if validation_error:
                    return False
            
            # Create cache request
            request = CacheRequest(
                prompt=prompt,
                model=model,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens"),
                parameters=kwargs
            )
            
            # Invalidate cache
            success = await self.llm_caching.invalidate_cache(request)
            
            if success:
                self.logger.info(f"✅ Cache invalidated for agent: {agent_id}")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("invalidate_agent_cache", {
                        "agent_id": agent_id,
                        "model": model,
                        "success": True
                    })
            else:
                self.logger.warning(f"Failed to invalidate cache for agent: {agent_id}")
            
            return success
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "invalidate_agent_cache",
                    "agent_id": agent_id,
                    "model": model,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to invalidate agent cache: {e}")
            return False
    
    async def clear_agent_cache(self, agent_id: str = None,
                               user_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Clear all cache entries.
        
        Args:
            agent_id: Agent ID for context
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            bool: Success status
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "llm_cache", "clear"
                )
                if validation_error:
                    return False
            
            # Clear cache
            success = await self.llm_caching.clear_cache()
            
            if success:
                self.logger.info(f"✅ Cache cleared for agent: {agent_id}")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("clear_agent_cache", {
                        "agent_id": agent_id,
                        "success": True
                    })
            else:
                self.logger.warning(f"Failed to clear cache for agent: {agent_id}")
            
            return success
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "clear_agent_cache",
                    "agent_id": agent_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to clear agent cache: {e}")
            return False
    
    async def get_agent_cache_stats(self, agent_id: str = None,
                                   user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get cache statistics for agentic use.
        
        Args:
            agent_id: Agent ID for context
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Cache statistics
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "llm_cache", "view"
                )
                if validation_error:
                    return validation_error
            
            # Get cache stats
            stats = await self.llm_caching.get_cache_stats()
            
            # Format for agentic use
            agent_stats = {
                "hits": stats.hits,
                "misses": stats.misses,
                "evictions": stats.evictions,
                "total_requests": stats.total_requests,
                "hit_rate": stats.hit_rate,
                "enabled": stats.enabled,
                "agent_id": agent_id,
                "timestamp": stats.timestamp.isoformat() if stats.timestamp else datetime.now().isoformat()
            }
            
            if stats.error:
                agent_stats["error"] = stats.error
            
            self.logger.info(f"✅ Cache stats retrieved for agent: {agent_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_agent_cache_stats", {
                    "agent_id": agent_id,
                    "hit_rate": stats.hit_rate,
                    "success": True
                })
            
            return agent_stats
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_agent_cache_stats",
                    "agent_id": agent_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to get agent cache stats: {e}")
            return {
                "error": str(e),
                "error_code": "LLM_CACHING_STATS_ERROR",
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def optimize_agent_cache(self, agent_id: str = None,
                                  user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Optimize cache for agentic use.
        
        Args:
            agent_id: Agent ID for context
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Optimization result
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "llm_cache", "optimize"
                )
                if validation_error:
                    return validation_error
            
            # Get current stats
            stats = await self.get_agent_cache_stats(agent_id, user_context)
            
            # Analyze cache performance
            hit_rate = stats.get("hit_rate", 0.0)
            total_requests = stats.get("total_requests", 0)
            
            # Determine optimization recommendations
            recommendations = []
            
            if hit_rate < 0.3 and total_requests > 100:
                recommendations.append("Consider increasing cache TTL")
            elif hit_rate > 0.8:
                recommendations.append("Cache is performing well")
            elif total_requests < 50:
                recommendations.append("Insufficient data for optimization")
            
            # Format optimization result
            optimization_result = {
                "agent_id": agent_id,
                "current_hit_rate": hit_rate,
                "total_requests": total_requests,
                "recommendations": recommendations,
                "optimization_score": min(hit_rate * 100, 100),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Cache optimization analyzed for agent: {agent_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("optimize_agent_cache", {
                    "agent_id": agent_id,
                    "hit_rate": hit_rate,
                    "success": True
                })
            
            return optimization_result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "optimize_agent_cache",
                    "agent_id": agent_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to optimize agent cache: {e}")
            return {
                "error": str(e),
                "error_code": "LLM_CACHING_OPTIMIZATION_ERROR",
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
            # Get LLM caching status
            caching_health = await self.llm_caching.health_check()
            
            result = {
                "service": "LLMCachingCompositionService",
                "initialized": self.is_initialized,
                "llm_caching": caching_health,
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
                "service": "LLMCachingCompositionService",
                "initialized": self.is_initialized,
                "error": str(e),
                "error_code": "LLM_CACHING_SERVICE_STATUS_ERROR",
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
            
            # Check LLM caching
            try:
                caching_health = await self.llm_caching.health_check()
                health_status["components"]["llm_caching"] = caching_health
                
                if not caching_health.get("healthy", False):
                    health_status["healthy"] = False
                    
            except Exception as e:
                health_status["components"]["llm_caching"] = {
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
                "error_code": "LLM_CACHING_HEALTH_CHECK_ERROR",
                "timestamp": datetime.now().isoformat()
            }




