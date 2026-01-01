#!/usr/bin/env python3
"""
Analytics Module - Traffic Cop Service

Handles traffic analytics using pandas for analysis.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from backend.smart_city.protocols.traffic_cop_service_protocol import (
    TrafficAnalyticsRequest, TrafficAnalyticsResponse
)


class Analytics:
    """Analytics module for Traffic Cop Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def get_traffic_analytics(self, request: TrafficAnalyticsRequest, user_context: Optional[Dict[str, Any]] = None) -> TrafficAnalyticsResponse:
        """Get traffic analytics data using pandas for analysis."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "get_traffic_analytics_start",
            success=True,
            details={"time_range": request.time_range}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "analytics", "read"):
                        await self.service.record_health_metric("get_traffic_analytics_access_denied", 1.0, {"time_range": request.time_range})
                        await self.service.log_operation_with_telemetry("get_traffic_analytics_complete", success=False)
                        return TrafficAnalyticsResponse(
                            success=False,
                            error="Access denied: insufficient permissions"
                        )
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("get_traffic_analytics_tenant_denied", 1.0, {"time_range": request.time_range, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("get_traffic_analytics_complete", success=False)
                            return TrafficAnalyticsResponse(
                                success=False,
                                error=f"Tenant access denied: {tenant_id}"
                            )
            
            # Get traffic data from Redis
            analytics_key = f"traffic_analytics:{request.time_range}"
            traffic_data = await self.service.messaging_abstraction.get_data(analytics_key) or [] if self.service.messaging_abstraction else []
            
            # Use pandas for analysis if available
            if self.service.pandas and traffic_data:
                df = self.service.pandas.DataFrame(traffic_data)
                
                # Calculate analytics
                analytics_data = {
                    "total_requests": len(df),
                    "unique_users": df["user_id"].nunique() if "user_id" in df.columns else 0,
                    "average_response_time": df["response_time"].mean() if "response_time" in df.columns else 0,
                    "error_rate": (df["status_code"] >= 400).mean() if "status_code" in df.columns else 0,
                    "top_endpoints": df["endpoint"].value_counts().head(10).to_dict() if "endpoint" in df.columns else {},
                    "requests_by_hour": df.groupby(df["timestamp"].dt.hour).size().to_dict() if "timestamp" in df.columns else {}
                }
            else:
                # Fallback to basic metrics
                analytics_data = {
                    "total_requests": self.service.traffic_metrics["total_requests"],
                    "successful_requests": self.service.traffic_metrics["successful_requests"],
                    "failed_requests": self.service.traffic_metrics["failed_requests"],
                    "active_sessions": self.service.traffic_metrics["active_sessions"],
                    "state_sync_operations": self.service.traffic_metrics["state_sync_operations"],
                    "load_balancing_operations": self.service.traffic_metrics["load_balancing_operations"]
                }
            
            # Record health metric
            await self.service.record_health_metric(
                "traffic_analytics_retrieved",
                1.0,
                {"time_range": request.time_range, "total_requests": analytics_data.get("total_requests", 0)}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "get_traffic_analytics_complete",
                success=True,
                details={"time_range": request.time_range, "total_requests": analytics_data.get("total_requests", 0)}
            )
            
            return TrafficAnalyticsResponse(
                success=True,
                analytics_data=analytics_data,
                time_range=request.time_range,
                generated_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "get_traffic_analytics")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "get_traffic_analytics_complete",
                success=False,
                details={"time_range": request.time_range, "error": str(e)}
            )
            
            return TrafficAnalyticsResponse(
                success=False,
                error=str(e)
            )
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get service health information."""
        try:
            instances = self.service.service_instances.get(service_name, [])
            healthy_instances = []
            
            # Get load balancing module for health checks
            load_balancing = self.service.get_module("load_balancing")
            
            for instance in instances:
                health_score = await load_balancing._check_instance_health(instance)
                if health_score > 50:
                    healthy_instances.append(instance.id)
            
            return {
                "service_name": service_name,
                "total_instances": len(instances),
                "healthy_instances": len(healthy_instances),
                "health_percentage": (len(healthy_instances) / len(instances) * 100) if instances else 0,
                "instances": [
                    {
                        "id": inst.id,
                        "host": inst.host,
                        "port": inst.port,
                        "weight": inst.weight
                    }
                    for inst in instances
                ]
            }
            
        except Exception as e:
            self.service._log("error", f"Failed to get service health: {e}")
            return {
                "service_name": service_name,
                "error": str(e)
            }







