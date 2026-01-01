#!/usr/bin/env python3
"""
Frontend Gateway Service Protocol - UPDATED for Current Architecture

Defines the contract for frontend gateway services in the Experience realm.
Reflects enabling services + semantic API + orchestrator composition pattern.

WHAT (Frontend Gateway Role): REST API gateway that exposes Business Enablement orchestrators
HOW (Frontend Gateway Service): Discovers orchestrators via Curator, routes requests, transforms responses

Architecture:
    Protocol Adapters (REST, GraphQL, WebSocket, gRPC)
        ↓
    FrontendGatewayService (this protocol)
        ↓ discover_orchestrators() via Curator
    Business Enablement Orchestrators (ContentAnalysis, Insights, Operations, BusinessOutcomes)
        ↓ compose SOA APIs
    Enabling Services (FileParser, DataAnalyzer, MetricsCalculator, etc.)
        ↓
    Smart City Infrastructure (Librarian, DataSteward, SecurityGuard, TrafficCop)
"""

from typing import Dict, Any, Optional, List, Protocol, runtime_checkable, Callable


@runtime_checkable
class FrontendGatewayServiceProtocol(Protocol):
    """
    Protocol for Frontend Gateway Service (Experience Realm).
    
    Responsibilities:
    - Discover Business Enablement orchestrators via Curator
    - Expose orchestrators as REST/GraphQL/WebSocket/gRPC APIs
    - Route protocol requests to orchestrators (universal routing)
    - Validate API requests against schemas
    - Transform orchestrator responses for frontend consumption
    - Support multiple protocol adapters with single implementation
    
    This protocol reflects the ACTUAL architecture (not UI rendering):
    - Orchestrators provide domain capabilities
    - Gateway exposes them as APIs
    - Protocol adapters provide HTTP/GraphQL/WS/gRPC bindings
    - Frontend manages its own state (React)
    """
    
    # ============================================================================
    # SERVICE PROTOCOL METHODS (Required by all services)
    # ============================================================================
    
    async def initialize(self) -> bool:
        """Initialize the service."""
        ...
    
    async def shutdown(self) -> bool:
        """Shutdown the service gracefully."""
        ...
    
    def health_check(self) -> Dict[str, Any]:
        """Get service health status."""
        ...
    
    def get_service_capabilities(self) -> List[str]:
        """Get list of service capabilities."""
        ...
    
    async def send_message(self, message: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message."""
        ...
    
    # ============================================================================
    # ORCHESTRATOR DISCOVERY (Smart City Integration)
    # ============================================================================
    
    async def discover_orchestrators(self) -> Dict[str, Any]:
        """
        Discover Business Enablement orchestrators via Curator.
        Called during initialize() to find available orchestrators.
        
        Discovers:
        - ContentAnalysisOrchestrator
        - InsightsOrchestrator
        - OperationsOrchestrator
        - BusinessOutcomesOrchestrator
        - DataOperationsOrchestrator
        
        Returns:
            Dict of discovered orchestrators {name: instance}
        """
        ...
    
    async def get_orchestrator(self, orchestrator_name: str) -> Optional[Any]:
        """
        Get specific orchestrator by name.
        
        Args:
            orchestrator_name: Name (e.g., "InsightsOrchestrator")
        
        Returns:
            Orchestrator instance or None if not available
        """
        ...
    
    # ============================================================================
    # API ENDPOINT REGISTRATION
    # ============================================================================
    
    async def register_api_endpoint(
        self,
        endpoint: str,
        handler: Callable,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register API endpoint with handler.
        
        Args:
            endpoint: API path (e.g., "/api/insights/analyze-content")
            handler: Handler method (orchestrator method)
            metadata: Optional metadata (orchestrator name, method, etc.)
            
        Returns:
            True if registered successfully
        """
        ...
    
    async def get_registered_endpoints(self) -> Dict[str, Any]:
        """
        Get all registered API endpoints.
        
        Returns:
            Dict of endpoints with metadata
        """
        ...
    
    # ============================================================================
    # REQUEST ROUTING (Core Gateway Capability - MOST IMPORTANT!)
    # ============================================================================
    
    async def route_frontend_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Universal request router - CORE gateway SOA API.
        Called by ALL protocol adapters (REST, GraphQL, WebSocket, gRPC).
        
        This is the PRIMARY method that makes the gateway universal!
        
        Flow:
        1. Validate request against schema
        2. Find orchestrator handler for endpoint
        3. Call orchestrator (domain capability)
        4. Transform response for frontend
        5. Log request via Librarian
        
        Args:
            request: {
                "endpoint": "/api/insights/analyze-content",
                "method": "POST" | "GET" | "PUT" | "DELETE",
                "params": {...},           # Request body/parameters
                "headers": {...},          # HTTP headers (optional)
                "query_params": {...},     # Query parameters (optional)
                "user_id": "...",          # User identifier (optional)
                "session_token": "..."     # Session token (optional)
            }
        
        Returns:
            Frontend-ready response with ui_state, timestamp, next_actions, etc.
            {
                "success": bool,
                "data": {...},           # Domain data from orchestrator
                "ui_state": "success" | "error" | "loading",
                "timestamp": "2025-11-11T...",
                "next_actions": ["action1", "action2"],
                "error": "..." (if failure)
            }
        """
        ...
    
    # ============================================================================
    # REQUEST VALIDATION
    # ============================================================================
    
    async def validate_api_request(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate API request against schemas.
        Reused by all protocol adapters.
        
        Args:
            request: Request to validate
        
        Returns:
            {
                "valid": bool,
                "errors": List[str] if invalid
            }
        """
        ...
    
    def get_endpoint_schema(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """
        Get schema for specific endpoint.
        
        Args:
            endpoint: Endpoint path
        
        Returns:
            Schema dict or None if endpoint not found
        """
        ...
    
    # ============================================================================
    # RESPONSE TRANSFORMATION
    # ============================================================================
    
    async def transform_for_frontend(
        self,
        orchestrator_response: Dict[str, Any],
        request_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Transform orchestrator response for frontend consumption.
        Reused by all protocol adapters.
        
        Adds frontend-specific fields:
        - ui_state: "success" | "error" | "loading"
        - timestamp: ISO format datetime
        - next_actions: Suggested user actions
        - error_hints: User-friendly error messages
        
        Args:
            orchestrator_response: Response from orchestrator (domain layer)
            request_context: Optional context for transformation
        
        Returns:
            Frontend-ready response (REST layer)
        """
        ...
    
    # ============================================================================
    # PROTOCOL ADAPTER SUPPORT
    # ============================================================================
    
    async def register_protocol_adapter(
        self,
        protocol_name: str,
        adapter: Any
    ) -> bool:
        """
        Register protocol adapter (REST, GraphQL, WebSocket, gRPC).
        
        Args:
            protocol_name: "REST" | "GraphQL" | "WebSocket" | "gRPC"
            adapter: Adapter instance
        
        Returns:
            True if registered
        """
        ...
    
    def get_supported_protocols(self) -> List[str]:
        """
        Get list of supported protocol adapters.
        
        Returns:
            List of protocol names (e.g., ["REST", "GraphQL", "WebSocket"])
        """
        ...
