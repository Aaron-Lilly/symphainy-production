#!/usr/bin/env python3
"""
Frontend Integration Interface

Defines the contract for the Frontend Integration service, responsible for
managing frontend-backend communication and API integration.

WHAT (Smart City Role): I manage frontend-backend integration and API communication
HOW (Interface): I define the contract for API routing, data transformation, and frontend coordination
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

from utilities import UserContext


class APIEndpoint(Enum):
    """Defines available API endpoints based on actual backend implementation from business_orchestrator_old."""
    
    # ===== INSIGHTS PILLAR ENDPOINTS (from business_orchestrator_old) =====
    # Health and capabilities
    INSIGHTS_HEALTH = "/health"
    INSIGHTS_CAPABILITIES = "/capabilities"
    
    # Analysis endpoints
    INSIGHTS_ANALYZE = "/analyze"
    INSIGHTS_VISUALIZE = "/visualize"
    INSIGHTS_BUSINESS_INSIGHTS = "/insights"
    
    # Chat endpoints
    INSIGHTS_CHAT = "/chat"
    INSIGHTS_CONVERSATION_HISTORY = "/conversation/{session_id}"
    INSIGHTS_CLEAR_HISTORY = "/conversation/{session_id}"
    
    # Specialized analysis
    INSIGHTS_ANOMALY_DETECTION = "/analyze/anomaly"
    INSIGHTS_CORRELATION_ANALYSIS = "/analyze/correlation"
    INSIGHTS_STATISTICAL_ANALYSIS = "/analyze/statistical"
    
    # Visualization types
    INSIGHTS_HISTOGRAM = "/visualize/histogram"
    INSIGHTS_SCATTER_PLOT = "/visualize/scatter"
    INSIGHTS_HEATMAP = "/visualize/heatmap"
    
    # ===== CONTENT PILLAR ENDPOINTS =====
    CONTENT_FILES = "/api/content/files"
    CONTENT_UPLOAD = "/api/content/upload"
    CONTENT_PARSE = "/api/content/parse"
    CONTENT_ANALYZE = "/api/content/analyze"
    CONTENT_PREVIEW = "/api/content/{file_id}/preview"
    CONTENT_METADATA = "/api/content/{file_id}/metadata"
    
    # ===== OPERATIONS PILLAR ENDPOINTS =====
    OPERATIONS_SESSION_ELEMENTS = "/api/operations/session/elements"
    OPERATIONS_SOP_TO_WORKFLOW = "/api/operations/convert-sop-to-workflow-real"
    OPERATIONS_WORKFLOW_TO_SOP = "/api/operations/convert-workflow-to-sop-real"
    OPERATIONS_COEXISTENCE = "/api/operations/create-coexistence-blueprint-directly"
    OPERATIONS_CONVERSATION = "/api/operations/conversation"
    OPERATIONS_HEALTH = "/api/operations/health"
    
    # ===== BUSINESS OUTCOMES ENDPOINTS =====
    BUSINESS_OUTCOMES_STRATEGIC_PLAN = "/api/business-outcomes/strategic-plan"
    BUSINESS_OUTCOMES_ROI_ANALYSIS = "/api/business-outcomes/roi-analysis"
    BUSINESS_OUTCOMES_METRICS = "/api/business-outcomes/metrics"
    
    # ===== CROSS-PILLAR ENDPOINTS =====
    CROSS_PILLAR_SMART_CITY = "/api/smart-city/sessions/{session_token}"
    CROSS_PILLAR_COMMUNICATION = "/api/cross-pillar/communication"
    CROSS_PILLAR_DATA_SHARING = "/api/cross-pillar/data-sharing"
    
    # ===== GLOBAL ENDPOINTS =====
    GLOBAL_AGENT = "/global/agent"
    HEALTH_CHECK = "/health"
    
    def __str__(self):
        return self.value


class RequestMethod(Enum):
    """Defines HTTP request methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    
    def __str__(self):
        return self.value


class ResponseStatus(Enum):
    """Defines response status states."""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    UNAUTHORIZED = "unauthorized"
    NOT_FOUND = "not_found"
    VALIDATION_ERROR = "validation_error"
    
    def __str__(self):
        return self.value


class DataFormat(Enum):
    """Defines data format types."""
    JSON = "json"
    XML = "xml"
    FORM_DATA = "form_data"
    MULTIPART = "multipart"
    BINARY = "binary"
    
    def __str__(self):
        return self.value


class IFrontendIntegration(ABC):
    """
    Frontend Integration Interface
    
    Defines the contract for frontend-backend integration services.
    """
    
    @abstractmethod
    async def route_api_request(self, endpoint: str, method: str, 
                               request_data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route an API request to the appropriate backend service.
        
        Args:
            endpoint: The API endpoint to route to
            method: The HTTP method
            request_data: Request data
            user_context: User context data
            
        Returns:
            Dict containing the response data and status
        """
        pass

    @abstractmethod
    async def authenticate_user(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate a user.
        
        Args:
            credentials: User credentials
            
        Returns:
            Dict containing authentication result
        """
        pass

    @abstractmethod
    async def establish_websocket_connection(self, session_token: str, agent_type: str) -> Dict[str, Any]:
        """
        Establish a WebSocket connection.
        
        Args:
            session_token: Session token
            agent_type: Type of agent
            
        Returns:
            Dict containing WebSocket connection result
        """
        pass

    @abstractmethod
    async def execute_operation(self, operation_type, operation_data: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a frontend integration operation.
        
        Args:
            operation_type: Type of operation to execute
            operation_data: Operation data
            user_context: User context data
            
        Returns:
            Dict containing operation execution result
        """
        pass

    @abstractmethod
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """
        Get service capabilities.
        
        Returns:
            Dict containing service capabilities
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Dict containing health status
        """
        pass