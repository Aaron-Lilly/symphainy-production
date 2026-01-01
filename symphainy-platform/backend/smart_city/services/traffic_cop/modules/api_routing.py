#!/usr/bin/env python3
"""
API Routing Module - Traffic Cop Service

Handles API Gateway routing and request processing.
"""

import time
from typing import List, Dict, Any, Optional
from backend.smart_city.protocols.traffic_cop_service_protocol import (
    APIGatewayRequest, APIGatewayResponse,
    LoadBalancingRequest, LoadBalancingStrategy,
    RateLimitRequest, RateLimitType
)


class ApiRouting:
    """API routing module for Traffic Cop Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def route_api_request(self, request: APIGatewayRequest, user_context: Optional[Dict[str, Any]] = None) -> APIGatewayResponse:
        """Route API request to appropriate service."""
        start_time = time.time()
        
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "route_api_request_start",
            success=True,
            details={"path": request.path, "method": request.method}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "api_routing", "read"):
                        await self.service.record_health_metric("route_api_request_access_denied", 1.0, {"path": request.path})
                        await self.service.log_operation_with_telemetry("route_api_request_complete", success=False)
                        return APIGatewayResponse(
                            success=False,
                            status_code=403,
                            error="Access denied: insufficient permissions"
                        )
            
            self.service.traffic_metrics["total_requests"] += 1
            
            # Check rate limits
            rate_limit_request = RateLimitRequest(
                user_id=request.user_id,
                api_endpoint=request.path,
                ip_address=request.headers.get("X-Forwarded-For"),
                limit_type=RateLimitType.PER_USER
            )
            
            # Get rate limiting module
            rate_limiting = self.service.get_module("rate_limiting")
            rate_limit_response = await rate_limiting.check_rate_limit(rate_limit_request)
            if not rate_limit_response.allowed:
                await self.service.record_health_metric("rate_limit_exceeded", 1.0, {"path": request.path})
                await self.service.log_operation_with_telemetry("route_api_request_complete", success=False, details={"path": request.path, "reason": "rate_limit_exceeded"})
                return APIGatewayResponse(
                    success=False,
                    status_code=429,
                    error="Rate limit exceeded"
                )
            
            # Find matching route
            route_config = self.service.api_routes.get(request.path)
            if not route_config:
                await self.service.record_health_metric("route_not_found", 1.0, {"path": request.path})
                await self.service.log_operation_with_telemetry("route_api_request_complete", success=False, details={"path": request.path, "reason": "not_found"})
                return APIGatewayResponse(
                    success=False,
                    status_code=404,
                    error="Route not found"
                )
            
            # Select service instance
            load_balancing_request = LoadBalancingRequest(
                service_name=route_config["service"],
                strategy=LoadBalancingStrategy.ROUND_ROBIN
            )
            
            # Get load balancing module
            load_balancing = self.service.get_module("load_balancing")
            load_balancing_response = await load_balancing.select_service(load_balancing_request, user_context)
            if not load_balancing_response.success:
                await self.service.record_health_metric("no_service_instances_for_route", 1.0, {"path": request.path, "service": route_config["service"]})
                await self.service.log_operation_with_telemetry("route_api_request_complete", success=False, details={"path": request.path, "reason": "no_instances"})
                return APIGatewayResponse(
                    success=False,
                    status_code=503,
                    error="No service instances available"
                )
            
            # Route request to selected service
            processing_time = time.time() - start_time
            
            # Mock response (in real implementation, this would forward the request)
            response_data = {
                "message": "Request processed successfully",
                "service_instance": load_balancing_response.service_instance.id,
                "processing_time": processing_time
            }
            
            self.service.traffic_metrics["successful_requests"] += 1
            
            # Record health metric
            await self.service.record_health_metric(
                "api_request_routed",
                1.0,
                {"path": request.path, "service": route_config["service"], "processing_time": processing_time}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "route_api_request_complete",
                success=True,
                details={"path": request.path, "service": route_config["service"], "processing_time": processing_time}
            )
            
            return APIGatewayResponse(
                success=True,
                status_code=200,
                body=response_data,
                service_instance=load_balancing_response.service_instance,
                processing_time=processing_time
            )
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "route_api_request")
            self.service.traffic_metrics["failed_requests"] += 1
            
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "route_api_request_complete",
                success=False,
                details={"path": request.path, "error": str(e)}
            )
            
            return APIGatewayResponse(
                success=False,
                status_code=500,
                error=str(e)
            )
    
    async def get_api_routes(self) -> List[Dict[str, Any]]:
        """Get available API routes."""
        return [
            {
                "path": path,
                "method": config["method"],
                "service": config["service"]
            }
            for path, config in self.service.api_routes.items()
        ]







