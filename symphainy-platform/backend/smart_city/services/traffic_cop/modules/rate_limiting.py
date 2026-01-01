#!/usr/bin/env python3
"""
Rate Limiting Module - Traffic Cop Service

Handles rate limiting checks and resets.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from backend.smart_city.protocols.traffic_cop_service_protocol import (
    RateLimitRequest, RateLimitResponse, RateLimitType
)


class RateLimiting:
    """Rate limiting module for Traffic Cop Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def check_rate_limit(self, request: RateLimitRequest, user_context: Optional[Dict[str, Any]] = None) -> RateLimitResponse:
        """Check if request is within rate limits."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "check_rate_limit_start",
            success=True,
            details={"limit_type": request.limit_type.value, "api_endpoint": request.api_endpoint}
        )
        
        try:
            # Generate rate limit key
            if request.limit_type == RateLimitType.PER_USER:
                key = f"rate_limit:user:{request.user_id}"
            elif request.limit_type == RateLimitType.PER_API:
                key = f"rate_limit:api:{request.api_endpoint}"
            elif request.limit_type == RateLimitType.PER_IP:
                key = f"rate_limit:ip:{request.ip_address}"
            else:  # GLOBAL
                key = "rate_limit:global"
            
            # Get current count from Redis
            current_count = await self.service.messaging_abstraction.get_data(key) or 0 if self.service.messaging_abstraction else 0
            
            # Check limits
            if current_count >= request.requests_per_minute:
                await self.service.record_health_metric("rate_limit_exceeded", 1.0, {"limit_type": request.limit_type.value})
                await self.service.log_operation_with_telemetry("check_rate_limit_complete", success=False, details={"limit_type": request.limit_type.value, "reason": "exceeded"})
                return RateLimitResponse(
                    allowed=False,
                    remaining_requests=0,
                    reset_time=(datetime.utcnow() + timedelta(minutes=1)).isoformat(),
                    limit_type=request.limit_type.value
                )
            
            # Increment counter
            if self.service.messaging_abstraction:
                await self.service.messaging_abstraction.increment_counter(key, 60)  # 60 second TTL
            
            # Record health metric
            await self.service.record_health_metric(
                "rate_limit_checked",
                1.0,
                {"limit_type": request.limit_type.value, "remaining": request.requests_per_minute - current_count - 1}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "check_rate_limit_complete",
                success=True,
                details={"limit_type": request.limit_type.value, "remaining": request.requests_per_minute - current_count - 1}
            )
            
            return RateLimitResponse(
                allowed=True,
                remaining_requests=request.requests_per_minute - current_count - 1,
                reset_time=(datetime.utcnow() + timedelta(minutes=1)).isoformat(),
                limit_type=request.limit_type.value
            )
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "check_rate_limit")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "check_rate_limit_complete",
                success=False,
                details={"limit_type": request.limit_type.value, "error": str(e)}
            )
            return RateLimitResponse(
                allowed=True,  # Fail open
                remaining_requests=0,
                error=str(e)
            )
    
    async def reset_rate_limit(self, user_id: str, api_endpoint: Optional[str] = None, user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Reset rate limits for user/API."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "reset_rate_limit_start",
            success=True,
            details={"user_id": user_id, "api_endpoint": api_endpoint}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "rate_limiting", "write"):
                        await self.service.record_health_metric("reset_rate_limit_access_denied", 1.0, {"user_id": user_id})
                        await self.service.log_operation_with_telemetry("reset_rate_limit_complete", success=False)
                        return False
            
            if api_endpoint:
                key = f"rate_limit:api:{api_endpoint}"
            else:
                key = f"rate_limit:user:{user_id}"
            
            if self.service.messaging_abstraction:
                await self.service.messaging_abstraction.delete_data(key)
            
            # Record health metric
            await self.service.record_health_metric(
                "rate_limit_reset",
                1.0,
                {"user_id": user_id, "api_endpoint": api_endpoint}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "reset_rate_limit_complete",
                success=True,
                details={"user_id": user_id, "api_endpoint": api_endpoint}
            )
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "reset_rate_limit")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "reset_rate_limit_complete",
                success=False,
                details={"user_id": user_id, "api_endpoint": api_endpoint, "error": str(e)}
            )
            return False







