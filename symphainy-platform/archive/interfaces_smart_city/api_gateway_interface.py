#!/usr/bin/env python3
"""
API Gateway Interface

Defines the contracts for API Gateway orchestration operations.
This interface extends Traffic Cop capabilities with API Gateway orchestration.

WHAT (Interface Role): I define the contracts for API Gateway orchestration
HOW (Interface Implementation): I provide clear, typed interfaces for API Gateway operations
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class APIGatewayMethod(str, Enum):
    """HTTP methods supported by API Gateway."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class APIGatewayPriority(str, Enum):
    """API Gateway priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class APIGatewayStatus(str, Enum):
    """API Gateway status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"


class FastAPIRoutingStatus(str, Enum):
    """FastAPI routing status levels."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"


# API Gateway Request/Response Models
class APIGatewayRequest(BaseModel):
    """Request for API Gateway orchestration."""
    request_id: str = Field(..., description="Unique request identifier")
    method: APIGatewayMethod = Field(..., description="HTTP method")
    path: str = Field(..., description="API path")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    query_params: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    body: Optional[Dict[str, Any]] = Field(None, description="Request body")
    target_service: str = Field(..., description="Target service name")
    priority: APIGatewayPriority = Field(default=APIGatewayPriority.NORMAL, description="Request priority")
    timeout_seconds: int = Field(default=30, description="Request timeout in seconds")
    tenant_id: str = Field(default="default", description="Tenant identifier")


class APIGatewayResponse(BaseModel):
    """Response from API Gateway orchestration."""
    request_id: str = Field(..., description="Request identifier")
    success: bool = Field(..., description="Whether the request was successful")
    status_code: int = Field(..., description="HTTP status code")
    headers: Dict[str, str] = Field(default_factory=dict, description="Response headers")
    body: Optional[Dict[str, Any]] = Field(None, description="Response body")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    target_service: str = Field(..., description="Target service that handled the request")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    error_message: Optional[str] = Field(None, description="Error message if request failed")


class FastAPIRoutingRequest(BaseModel):
    """Request for FastAPI routing management."""
    route_id: str = Field(..., description="Unique route identifier")
    path: str = Field(..., description="Route path")
    method: APIGatewayMethod = Field(..., description="HTTP method")
    target_service: str = Field(..., description="Target service name")
    middleware: List[str] = Field(default_factory=list, description="Middleware to apply")
    rate_limit: Optional[int] = Field(None, description="Rate limit per minute")
    timeout_seconds: int = Field(default=30, description="Route timeout")
    priority: APIGatewayPriority = Field(default=APIGatewayPriority.NORMAL, description="Route priority")
    tenant_id: str = Field(default="default", description="Tenant identifier")


class FastAPIRoutingResponse(BaseModel):
    """Response from FastAPI routing management."""
    route_id: str = Field(..., description="Route identifier")
    success: bool = Field(..., description="Whether the route was created successfully")
    status: FastAPIRoutingStatus = Field(..., description="Route status")
    path: str = Field(..., description="Route path")
    method: APIGatewayMethod = Field(..., description="HTTP method")
    target_service: str = Field(..., description="Target service")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    error_message: Optional[str] = Field(None, description="Error message if route creation failed")


class APIGatewayMetricsRequest(BaseModel):
    """Request for API Gateway metrics."""
    service_name: Optional[str] = Field(None, description="Specific service to get metrics for")
    time_range_minutes: int = Field(default=60, description="Time range in minutes")
    include_details: bool = Field(default=False, description="Include detailed metrics")


class APIGatewayMetricsResponse(BaseModel):
    """Response with API Gateway metrics."""
    success: bool = Field(..., description="Whether metrics retrieval was successful")
    metrics: Dict[str, Any] = Field(..., description="API Gateway metrics")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metrics timestamp")
    error_message: Optional[str] = Field(None, description="Error message if metrics retrieval failed")


class APIGatewayHealthRequest(BaseModel):
    """Request for API Gateway health check."""
    include_dependencies: bool = Field(default=True, description="Include dependency health checks")


class APIGatewayHealthResponse(BaseModel):
    """Response from API Gateway health check."""
    success: bool = Field(..., description="Whether health check was successful")
    status: APIGatewayStatus = Field(..., description="Overall API Gateway status")
    components: Dict[str, Any] = Field(..., description="Component health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    error_message: Optional[str] = Field(None, description="Error message if health check failed")


# Interface Definition
class IAPIGateway:
    """
    API Gateway Interface

    Defines the contracts for API Gateway orchestration operations.
    This interface extends Traffic Cop capabilities with API Gateway orchestration.
    """

    # API Gateway Orchestration
    async def orchestrate_api_gateway(self, request: APIGatewayRequest) -> APIGatewayResponse:
        """Orchestrate API Gateway routing and request handling."""
        pass

    async def orchestrate_fastapi_routing(self, request: FastAPIRoutingRequest) -> FastAPIRoutingResponse:
        """Orchestrate FastAPI routing management."""
        pass

    async def get_api_gateway_metrics(self, request: APIGatewayMetricsRequest) -> APIGatewayMetricsResponse:
        """Get API Gateway metrics and performance data."""
        pass

    async def health_check_api_gateway(self, request: APIGatewayHealthRequest) -> APIGatewayHealthResponse:
        """Perform health check on API Gateway components."""
        pass

