#!/usr/bin/env python3
"""
Experience Service Interface

Defines the standard interface for Experience Dimension services using pure dependency injection.

WHAT (Service Interface): I define the standard interface for Experience services
HOW (Interface): I provide clear contracts for service implementation and usage
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))


class ExperienceServiceType(Enum):
    """Types of Experience services."""
    FRONTEND_INTEGRATION = "frontend_integration"
    EXPERIENCE_MANAGER = "experience_manager"
    JOURNEY_MANAGER = "journey_manager"
    MULTI_TENANT = "multi_tenant"


class ExperienceOperationType(Enum):
    """Types of operations Experience services can perform."""
    SESSION_MANAGEMENT = "session_management"
    UI_STATE_MANAGEMENT = "ui_state_management"
    REAL_TIME_COORDINATION = "real_time_coordination"
    FRONTEND_ROUTING = "frontend_routing"
    JOURNEY_TRACKING = "journey_tracking"
    FLOW_MANAGEMENT = "flow_management"
    API_GATEWAY = "api_gateway"
    WEBSOCKET_MANAGEMENT = "websocket_management"
    MULTI_TENANT_MANAGEMENT = "multi_tenant_management"
    USER_EXPERIENCE_OPTIMIZATION = "user_experience_optimization"


class IExperienceService(ABC):
    """
    Experience Service Interface
    
    Standard interface for all Experience Dimension services using pure dependency injection.
    """
    
    @abstractmethod
    async def initialize(self, user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize the experience service."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """Shutdown the experience service."""
        pass
    
    @abstractmethod
    async def execute_operation(self, operation_type: ExperienceOperationType, 
                               operation_data: Dict[str, Any], 
                               user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a specific operation."""
        pass
    
    @abstractmethod
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this service."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the service."""
        pass
    
    @abstractmethod
    async def validate_dependencies(self) -> Dict[str, Any]:
        """Validate that all dependencies are properly injected."""
        pass


class IFrontendIntegrationService(IExperienceService):
    """
    Frontend Integration Service Interface
    
    Interface for services that manage frontend-backend communication and API integration.
    """
    
    @abstractmethod
    async def route_api_request(self, endpoint: str, method: str, 
                               user_context: Dict[str, Any], 
                               data: Optional[Dict[str, Any]] = None,
                               params: Optional[Dict[str, Any]] = None,
                               headers: Optional[Dict[str, str]] = None,
                               session_token: Optional[str] = None) -> Dict[str, Any]:
        """Route an API request to the appropriate backend service."""
        pass
    
    @abstractmethod
    async def transform_request_data(self, data: Dict[str, Any], 
                                   source_format: str, target_format: str) -> Dict[str, Any]:
        """Transform request data between different formats."""
        pass
    
    @abstractmethod
    async def transform_response_data(self, data: Dict[str, Any], 
                                    source_format: str, target_format: str) -> Dict[str, Any]:
        """Transform response data between different formats."""
        pass
    
    @abstractmethod
    async def validate_request(self, endpoint: str, method: str, 
                              data: Optional[Dict[str, Any]] = None,
                              params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate an incoming API request."""
        pass
    
    @abstractmethod
    async def handle_error(self, error: Exception, endpoint: str, 
                          user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle and format API errors."""
        pass
    
    @abstractmethod
    async def get_api_documentation(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Get API documentation for endpoints."""
        pass
    
    @abstractmethod
    async def register_webhook(self, endpoint: str, webhook_url: str, 
                              events: List[str]) -> Dict[str, Any]:
        """Register a webhook for an endpoint."""
        pass
    
    @abstractmethod
    async def unregister_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Unregister a webhook."""
        pass
    
    @abstractmethod
    async def create_authenticated_headers(self, user_context: Dict[str, Any], 
                                         session_token: Optional[str] = None,
                                         additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Create standardized authenticated headers for API requests."""
        pass


class IExperienceManagerService(IExperienceService):
    """
    Experience Manager Service Interface
    
    Interface for services that manage overall user experience and coordinate between services.
    """
    
    @abstractmethod
    async def manage_user_session(self, user_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage user session and state."""
        pass
    
    @abstractmethod
    async def coordinate_user_journey(self, user_id: str, journey_data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate user journey across services."""
        pass
    
    @abstractmethod
    async def optimize_user_experience(self, user_id: str, optimization_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize user experience based on data."""
        pass
    
    @abstractmethod
    async def track_user_behavior(self, user_id: str, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track user behavior for analytics."""
        pass
    
    @abstractmethod
    async def personalize_experience(self, user_id: str, personalization_data: Dict[str, Any]) -> Dict[str, Any]:
        """Personalize user experience."""
        pass
    
    @abstractmethod
    async def manage_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Manage user preferences and settings."""
        pass
    
    @abstractmethod
    async def get_user_insights(self, user_id: str, insight_type: str) -> Dict[str, Any]:
        """Get insights about user behavior and preferences."""
        pass


class IJourneyManagerService(IExperienceService):
    """
    Journey Manager Service Interface
    
    Interface for services that manage user journeys and flow orchestration.
    """
    
    @abstractmethod
    async def create_user_journey(self, journey_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user journey."""
        pass
    
    @abstractmethod
    async def update_user_journey(self, journey_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing user journey."""
        pass
    
    @abstractmethod
    async def execute_user_journey(self, journey_id: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a user journey."""
        pass
    
    @abstractmethod
    async def track_journey_progress(self, journey_id: str, user_id: str) -> Dict[str, Any]:
        """Track progress of a user journey."""
        pass
    
    @abstractmethod
    async def optimize_journey_flow(self, journey_id: str, optimization_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize journey flow based on analytics."""
        pass
    
    @abstractmethod
    async def get_journey_analytics(self, journey_id: str, analytics_type: str) -> Dict[str, Any]:
        """Get analytics for a journey."""
        pass
    
    @abstractmethod
    async def manage_journey_milestones(self, journey_id: str, milestones: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Manage journey milestones and checkpoints."""
        pass


class IMultiTenantService(IExperienceService):
    """
    Multi-Tenant Service Interface
    
    Interface for services that manage multi-tenant functionality and tenant isolation.
    """
    
    @abstractmethod
    async def create_tenant(self, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tenant."""
        pass
    
    @abstractmethod
    async def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update tenant information."""
        pass
    
    @abstractmethod
    async def get_tenant_info(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant information."""
        pass
    
    @abstractmethod
    async def validate_tenant_access(self, tenant_id: str, user_id: str) -> bool:
        """Validate user access to tenant."""
        pass
    
    @abstractmethod
    async def isolate_tenant_data(self, tenant_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure tenant data isolation."""
        pass
    
    @abstractmethod
    async def configure_tenant_settings(self, tenant_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Configure tenant-specific settings."""
        pass
    
    @abstractmethod
    async def get_tenant_users(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get users belonging to a tenant."""
        pass
    
    @abstractmethod
    async def audit_tenant_access(self, tenant_id: str, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Audit tenant access and usage."""
        pass


class IWebSocketService(IExperienceService):
    """
    WebSocket Service Interface
    
    Interface for services that manage WebSocket connections and real-time communication.
    """
    
    @abstractmethod
    async def establish_connection(self, user_id: str, connection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Establish WebSocket connection."""
        pass
    
    @abstractmethod
    async def send_message(self, connection_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message via WebSocket."""
        pass
    
    @abstractmethod
    async def broadcast_message(self, message: Dict[str, Any], target_users: List[str]) -> Dict[str, Any]:
        """Broadcast message to multiple users."""
        pass
    
    @abstractmethod
    async def close_connection(self, connection_id: str) -> Dict[str, Any]:
        """Close WebSocket connection."""
        pass
    
    @abstractmethod
    async def get_connection_status(self, connection_id: str) -> Dict[str, Any]:
        """Get WebSocket connection status."""
        pass
    
    @abstractmethod
    async def manage_connection_pool(self, pool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage WebSocket connection pool."""
        pass


class IAPIGatewayService(IExperienceService):
    """
    API Gateway Service Interface
    
    Interface for services that manage API gateway functionality and routing.
    """
    
    @abstractmethod
    async def route_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route incoming API request."""
        pass
    
    @abstractmethod
    async def authenticate_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate incoming API request."""
        pass
    
    @abstractmethod
    async def authorize_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Authorize incoming API request."""
        pass
    
    @abstractmethod
    async def rate_limit_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply rate limiting to request."""
        pass
    
    @abstractmethod
    async def transform_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform request before routing."""
        pass
    
    @abstractmethod
    async def transform_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform response before returning."""
        pass
    
    @abstractmethod
    async def log_request(self, request_data: Dict[str, Any], response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log API request and response."""
        pass


class IErrorHandlingService(IExperienceService):
    """
    Error Handling Service Interface
    
    Interface for services that manage error handling and reporting.
    """
    
    @abstractmethod
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle and process errors."""
        pass
    
    @abstractmethod
    async def report_error(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Report error for monitoring and debugging."""
        pass
    
    @abstractmethod
    async def get_error_logs(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get error logs for debugging."""
        pass
    
    @abstractmethod
    async def create_user_friendly_message(self, error: Exception) -> str:
        """Create user-friendly error message."""
        pass
    
    @abstractmethod
    async def track_error_metrics(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track error metrics for monitoring."""
        pass




























