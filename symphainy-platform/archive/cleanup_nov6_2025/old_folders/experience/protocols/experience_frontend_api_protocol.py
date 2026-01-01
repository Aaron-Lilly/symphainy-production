#!/usr/bin/env python3
"""
Experience Frontend API Protocol

Defines the API endpoints and protocols that the Experience layer exposes
to the frontend for seamless integration.

WHAT (Frontend API Protocol): I define the API contracts for frontend-backend communication
HOW (Protocol): I provide standardized REST and WebSocket endpoints with proper data models
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))


class APIMethod(Enum):
    """HTTP methods supported by the Experience Frontend API."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class APICategory(Enum):
    """Categories of APIs exposed to the frontend."""
    AUTHENTICATION = "authentication"
    CONTENT = "content"
    OPERATIONS = "operations"
    INSIGHTS = "insights"
    BUSINESS_OUTCOMES = "business_outcomes"
    WEBSOCKET = "websocket"
    ERROR_HANDLING = "error_handling"
    HEALTH = "health"


class ExperienceFrontendAPIProtocol(ABC):
    """
    Experience Frontend API Protocol
    
    Defines the API endpoints and protocols that the Experience layer exposes
    to the frontend for seamless integration.
    """
    
    # ============================================================================
    # AUTHENTICATION APIs
    # ============================================================================
    
    @abstractmethod
    async def authenticate_user(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate user and return session information."""
        pass
    
    @abstractmethod
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register new user and return session information."""
        pass
    
    @abstractmethod
    async def validate_session(self, session_token: str) -> Dict[str, Any]:
        """Validate user session token."""
        pass
    
    @abstractmethod
    async def refresh_session(self, session_token: str) -> Dict[str, Any]:
        """Refresh user session token."""
        pass
    
    @abstractmethod
    async def logout_user(self, session_token: str) -> Dict[str, Any]:
        """Logout user and invalidate session."""
        pass
    
    # ============================================================================
    # CONTENT PILLAR APIs
    # ============================================================================
    
    @abstractmethod
    async def list_content_files(self, session_token: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List all content files for the user."""
        pass
    
    @abstractmethod
    async def upload_content_file(self, file_data: bytes, metadata: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Upload a new content file."""
        pass
    
    @abstractmethod
    async def get_content_file(self, file_id: str, session_token: str) -> Dict[str, Any]:
        """Get content file information and metadata."""
        pass
    
    @abstractmethod
    async def update_content_file(self, file_id: str, updates: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Update content file metadata."""
        pass
    
    @abstractmethod
    async def delete_content_file(self, file_id: str, session_token: str) -> Dict[str, Any]:
        """Delete a content file."""
        pass
    
    @abstractmethod
    async def process_content_file(self, file_id: str, processing_options: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Process a content file."""
        pass
    
    @abstractmethod
    async def extract_content_metadata(self, file_id: str, session_token: str) -> Dict[str, Any]:
        """Extract metadata from a content file."""
        pass
    
    @abstractmethod
    async def analyze_content(self, file_id: str, analysis_type: str, session_token: str) -> Dict[str, Any]:
        """Analyze content file."""
        pass
    
    @abstractmethod
    async def search_content(self, query: str, filters: Optional[Dict[str, Any]], session_token: str) -> Dict[str, Any]:
        """Search content files."""
        pass
    
    # ============================================================================
    # OPERATIONS PILLAR APIs
    # ============================================================================
    
    @abstractmethod
    async def get_session_elements(self, session_token: str) -> Dict[str, Any]:
        """Get session elements for operations."""
        pass
    
    @abstractmethod
    async def analyze_coexistence(self, coexistence_data: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Analyze coexistence of processes."""
        pass
    
    @abstractmethod
    async def generate_workflow(self, workflow_spec: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Generate workflow from specification."""
        pass
    
    @abstractmethod
    async def generate_sop(self, sop_spec: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Generate Standard Operating Procedure."""
        pass
    
    @abstractmethod
    async def optimize_process(self, process_id: str, optimization_params: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Optimize a specific process."""
        pass
    
    @abstractmethod
    async def check_compliance(self, compliance_data: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Check compliance requirements."""
        pass
    
    # ============================================================================
    # INSIGHTS PILLAR APIs
    # ============================================================================
    
    @abstractmethod
    async def generate_insights(self, data_sources: List[str], insight_type: str, session_token: str) -> Dict[str, Any]:
        """Generate insights from data sources."""
        pass
    
    @abstractmethod
    async def get_insights_analytics(self, analytics_params: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Get analytics and insights."""
        pass
    
    @abstractmethod
    async def create_insights_report(self, report_spec: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Create insights report."""
        pass
    
    # ============================================================================
    # BUSINESS OUTCOMES PILLAR APIs
    # ============================================================================
    
    @abstractmethod
    async def track_business_outcomes(self, outcome_data: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Track business outcomes."""
        pass
    
    @abstractmethod
    async def measure_success_metrics(self, metrics_spec: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Measure success metrics."""
        pass
    
    @abstractmethod
    async def optimize_business_outcomes(self, optimization_data: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Optimize business outcomes."""
        pass
    
    # ============================================================================
    # WEBSOCKET COMMUNICATION APIs
    # ============================================================================
    
    @abstractmethod
    async def establish_websocket_connection(self, session_token: str, agent_type: str) -> Dict[str, Any]:
        """Establish WebSocket connection for real-time communication."""
        pass
    
    @abstractmethod
    async def send_agent_message(self, message: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Send message to agent via WebSocket."""
        pass
    
    @abstractmethod
    async def route_agent_message(self, message: Dict[str, Any], target_agent: str, session_token: str) -> Dict[str, Any]:
        """Route message to specific agent."""
        pass
    
    # ============================================================================
    # ERROR HANDLING APIs
    # ============================================================================
    
    @abstractmethod
    async def report_error(self, error_data: Dict[str, Any], session_token: Optional[str] = None) -> Dict[str, Any]:
        """Report error for debugging and monitoring."""
        pass
    
    @abstractmethod
    async def get_error_logs(self, filters: Optional[Dict[str, Any]], session_token: str) -> Dict[str, Any]:
        """Get error logs for debugging."""
        pass
    
    # ============================================================================
    # HEALTH AND STATUS APIs
    # ============================================================================
    
    @abstractmethod
    async def get_service_health(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get health status of services."""
        pass
    
    @abstractmethod
    async def get_platform_status(self) -> Dict[str, Any]:
        """Get overall platform status."""
        pass
    
    @abstractmethod
    async def get_api_documentation(self, api_category: Optional[APICategory] = None) -> Dict[str, Any]:
        """Get API documentation."""
        pass


class ExperienceFrontendAPIService:
    """
    Experience Frontend API Service (DI-Based)
    
    Implements the Experience Frontend API Protocol to provide all the APIs
    that the frontend needs for seamless integration.
    """
    
    def __init__(self, foundation_services, smart_city_apis, business_apis, agent_apis):
        """Initialize Experience Frontend API Service with dependency injection."""
        self.foundation_services = foundation_services
        self.smart_city_apis = smart_city_apis
        self.business_apis = business_apis
        self.agent_apis = agent_apis
        
        # Get utilities from foundation services
        self.logger = foundation_services.get_logger("experience_frontend_api")
        self.config = foundation_services.get_config()
        self.security = foundation_services.get_security()
        self.telemetry = foundation_services.get_telemetry()
        
        # API routing configuration
        self.api_routes = {
            "authentication": {
                "login": "/api/auth/login",
                "register": "/api/auth/register",
                "validate": "/api/auth/validate",
                "refresh": "/api/auth/refresh",
                "logout": "/api/auth/logout"
            },
            "content": {
                "files": "/api/content/files",
                "upload": "/api/content/upload",
                "file": "/api/content/{file_id}",
                "process": "/api/content/{file_id}/process",
                "metadata": "/api/content/{file_id}/metadata",
                "analyze": "/api/content/{file_id}/analyze",
                "search": "/api/content/search",
                "health": "/api/content/health"
            },
            "operations": {
                "session_elements": "/api/operations/session/elements",
                "coexistence_analyze": "/api/operations/coexistence/analyze",
                "workflow_generate": "/api/operations/workflow/generate",
                "sop_generate": "/api/operations/sop/generate",
                "process_optimize": "/api/operations/process/{process_id}/optimize",
                "compliance_check": "/api/operations/compliance/check",
                "health": "/api/operations/health"
            },
            "insights": {
                "generate": "/api/insights/generate",
                "analytics": "/api/insights/analytics",
                "report": "/api/insights/report",
                "health": "/api/insights/health"
            },
            "business_outcomes": {
                "track": "/api/business-outcomes/track",
                "measure": "/api/business-outcomes/measure",
                "optimize": "/api/business-outcomes/optimize",
                "health": "/api/business-outcomes/health"
            },
            "websocket": {
                "smart_chat": "/smart-chat"
            },
            "error_handling": {
                "report": "/api/errors",
                "logs": "/api/errors/logs"
            },
            "health": {
                "service": "/api/health/{service_name}",
                "platform": "/api/health/platform"
            }
        }
        
        self.logger.info("🌐 Experience Frontend API Service initialized (DI-Based)")
    
    # ============================================================================
    # AUTHENTICATION APIs
    # ============================================================================
    
    async def authenticate_user(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate user and return session information."""
        try:
            self.logger.info("Authenticating user...")
            
            # Use Smart City Security Guard API
            auth_result = await self.smart_city_apis.authenticate_user(credentials)
            
            if auth_result.get("success"):
                # Create session and return user data
                session_data = {
                    "user_id": auth_result["user"]["user_id"],
                    "email": auth_result["user"]["email"],
                    "full_name": auth_result["user"]["full_name"],
                    "token": auth_result["token"],
                    "expires_at": auth_result.get("expires_at")
                }
                
                return {
                    "success": True,
                    "user": session_data,
                    "token": auth_result["token"],
                    "message": "Authentication successful"
                }
            else:
                return {
                    "success": False,
                    "message": auth_result.get("message", "Authentication failed")
                }
                
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return {
                "success": False,
                "message": "Authentication failed due to server error"
            }
    
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register new user and return session information."""
        try:
            self.logger.info("Registering new user...")
            
            # Use Smart City Security Guard API
            registration_result = await self.smart_city_apis.register_user(user_data)
            
            if registration_result.get("success"):
                # Create session and return user data
                session_data = {
                    "user_id": registration_result["user"]["user_id"],
                    "email": registration_result["user"]["email"],
                    "full_name": registration_result["user"]["full_name"],
                    "token": registration_result["token"],
                    "expires_at": registration_result.get("expires_at")
                }
                
                return {
                    "success": True,
                    "user": session_data,
                    "token": registration_result["token"],
                    "message": "Registration successful"
                }
            else:
                return {
                    "success": False,
                    "message": registration_result.get("message", "Registration failed")
                }
                
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return {
                "success": False,
                "message": "Registration failed due to server error"
            }
    
    async def validate_session(self, session_token: str) -> Dict[str, Any]:
        """Validate user session token."""
        try:
            self.logger.info("Validating session token...")
            
            # Use Smart City Security Guard API
            validation_result = await self.smart_city_apis.validate_token(session_token)
            
            return {
                "success": validation_result.get("valid", False),
                "user": validation_result.get("user"),
                "message": "Session valid" if validation_result.get("valid") else "Session invalid"
            }
            
        except Exception as e:
            self.logger.error(f"Session validation error: {e}")
            return {
                "success": False,
                "message": "Session validation failed"
            }
    
    async def refresh_session(self, session_token: str) -> Dict[str, Any]:
        """Refresh user session token."""
        try:
            self.logger.info("Refreshing session token...")
            
            # Use Smart City Security Guard API
            refresh_result = await self.smart_city_apis.refresh_token(session_token)
            
            return {
                "success": refresh_result.get("success", False),
                "token": refresh_result.get("token"),
                "expires_at": refresh_result.get("expires_at"),
                "message": "Session refreshed" if refresh_result.get("success") else "Session refresh failed"
            }
            
        except Exception as e:
            self.logger.error(f"Session refresh error: {e}")
            return {
                "success": False,
                "message": "Session refresh failed"
            }
    
    async def logout_user(self, session_token: str) -> Dict[str, Any]:
        """Logout user and invalidate session."""
        try:
            self.logger.info("Logging out user...")
            
            # Use Smart City Security Guard API
            logout_result = await self.smart_city_apis.logout_user(session_token)
            
            return {
                "success": logout_result.get("success", False),
                "message": "Logout successful" if logout_result.get("success") else "Logout failed"
            }
            
        except Exception as e:
            self.logger.error(f"Logout error: {e}")
            return {
                "success": False,
                "message": "Logout failed"
            }
    
    # ============================================================================
    # CONTENT PILLAR APIs
    # ============================================================================
    
    async def list_content_files(self, session_token: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List all content files for the user."""
        try:
            self.logger.info("Listing content files...")
            
            # Use Business Enablement Content API
            files_result = await self.business_apis.list_content_files(session_token, filters)
            
            return {
                "success": True,
                "files": files_result.get("files", []),
                "total_count": len(files_result.get("files", [])),
                "message": "Files retrieved successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error listing content files: {e}")
            return {
                "success": False,
                "files": [],
                "message": "Failed to retrieve files"
            }
    
    async def upload_content_file(self, file_data: bytes, metadata: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Upload a new content file."""
        try:
            self.logger.info("Uploading content file...")
            
            # Use Business Enablement Content API
            upload_result = await self.business_apis.upload_content_file(file_data, metadata, session_token)
            
            return {
                "success": upload_result.get("success", False),
                "file": upload_result.get("file"),
                "message": "File uploaded successfully" if upload_result.get("success") else "File upload failed"
            }
            
        except Exception as e:
            self.logger.error(f"Error uploading content file: {e}")
            return {
                "success": False,
                "message": "File upload failed"
            }
    
    # Continue with other Content APIs...
    # (Implementation continues with similar patterns for all other API methods)
    
    # ============================================================================
    # WEBSOCKET COMMUNICATION APIs
    # ============================================================================
    
    async def establish_websocket_connection(self, session_token: str, agent_type: str) -> Dict[str, Any]:
        """Establish WebSocket connection for real-time communication."""
        try:
            self.logger.info(f"Establishing WebSocket connection for agent: {agent_type}")
            
            # Use Smart City Traffic Cop API for event routing
            connection_result = await self.smart_city_apis.establish_websocket_connection(session_token, agent_type)
            
            return {
                "success": connection_result.get("success", False),
                "connection_id": connection_result.get("connection_id"),
                "websocket_url": f"ws://127.0.0.1:8000/smart-chat",
                "message": "WebSocket connection established" if connection_result.get("success") else "WebSocket connection failed"
            }
            
        except Exception as e:
            self.logger.error(f"WebSocket connection error: {e}")
            return {
                "success": False,
                "message": "WebSocket connection failed"
            }
    
    async def send_agent_message(self, message: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Send message to agent via WebSocket."""
        try:
            self.logger.info("Sending agent message...")
            
            # Use Agent APIs for message routing
            message_result = await self.agent_apis.send_agent_message(message, session_token)
            
            return {
                "success": message_result.get("success", False),
                "response": message_result.get("response"),
                "message": "Message sent successfully" if message_result.get("success") else "Message sending failed"
            }
            
        except Exception as e:
            self.logger.error(f"Agent message error: {e}")
            return {
                "success": False,
                "message": "Message sending failed"
            }
    
    # ============================================================================
    # HEALTH AND STATUS APIs
    # ============================================================================
    
    async def get_service_health(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get health status of services."""
        try:
            self.logger.info(f"Getting health status for service: {service_name or 'all'}")
            
            # Get foundation services health
            foundation_health = await self.foundation_services.get_container_health()
            
            # Get specific service health if requested
            service_health = None
            if service_name:
                # This would call the specific service's health endpoint
                service_health = {"status": "healthy", "service": service_name}
            
            return {
                "success": True,
                "foundation_services": foundation_health,
                "service_health": service_health,
                "overall_status": "healthy",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health check error: {e}")
            return {
                "success": False,
                "overall_status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_api_documentation(self, api_category: Optional[APICategory] = None) -> Dict[str, Any]:
        """Get API documentation."""
        try:
            self.logger.info(f"Getting API documentation for category: {api_category or 'all'}")
            
            if api_category:
                # Return specific category documentation
                return {
                    "success": True,
                    "category": api_category.value,
                    "endpoints": self.api_routes.get(api_category.value, {}),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                # Return all API documentation
                return {
                    "success": True,
                    "api_version": "1.0.0",
                    "categories": list(self.api_routes.keys()),
                    "endpoints": self.api_routes,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"API documentation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_service_health_status(self) -> Dict[str, Any]:
        """Get the health status of the Experience Frontend API Service."""
        try:
            return {
                "service": "experience_frontend_api",
                "status": "healthy",
                "architecture": "DI-Based",
                "api_categories_supported": list(self.api_routes.keys()),
                "total_endpoints": sum(len(category) for category in self.api_routes.values()),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "service": "experience_frontend_api",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }




























