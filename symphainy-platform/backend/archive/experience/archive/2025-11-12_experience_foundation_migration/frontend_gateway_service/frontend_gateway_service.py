#!/usr/bin/env python3
"""
Frontend Gateway Service

WHAT: Routes frontend requests to Business Enablement orchestrators
HOW: Discovers orchestrators via Curator, exposes frontend APIs, transforms responses for UI

This service provides the API gateway for the frontend, routing requests to
Business Enablement orchestrators and transforming responses for UI consumption.
"""

import os
import sys
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class APIEndpointType(Enum):
    """Types of API endpoints."""
    REST = "rest"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"


class FrontendGatewayService(RealmServiceBase):
    """
    Frontend Gateway Service for Experience realm.
    
    Routes frontend requests to Business Enablement orchestrators and
    manages API exposure for the frontend.
    
    Composes:
    - ContentAnalysisOrchestrator → /api/documents/*
    - InsightsOrchestrator → /api/insights/*
    - OperationsOrchestrator → /api/operations/*
    - DataOperationsOrchestrator → /api/data/*
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Frontend Gateway Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.librarian = None
        self.security_guard = None
        self.traffic_cop = None
        
        # Business Enablement orchestrators (discovered via Curator)
        self.content_orchestrator = None
        self.insights_orchestrator = None
        self.operations_orchestrator = None
        self.data_operations_orchestrator = None
        self.business_outcomes_orchestrator = None
        
        # Orchestrators dictionary (for dictionary-style access)
        self.orchestrators: Dict[str, Any] = {}
        
        # Chat Service (discovered via Curator)
        self.chat_service = None
        
        # API registry
        self.registered_apis: Dict[str, Dict[str, Any]] = {}
        
        # Supported endpoint types
        self.supported_types = [t.value for t in APIEndpointType]
    
    async def initialize(self) -> bool:
        """Initialize Frontend Gateway Service."""
        await super().initialize()
        
        try:
            # 1. Get Smart City services
            self.librarian = await self.get_librarian_api()
            self.security_guard = await self.get_security_guard_api()
            self.traffic_cop = await self.get_traffic_cop_api()
            
            # 2. Discover Business Enablement orchestrators via Curator
            await self._discover_orchestrators()
            
            # 3. Expose frontend APIs
            await self._expose_frontend_apis()
            
            # 4. Register with Curator
            await self.register_with_curator(
                capabilities=["frontend_api_gateway", "request_routing", "api_transformation", "chat_routing"],
                soa_apis=[
                    "expose_frontend_api", "route_frontend_request", "get_frontend_apis",
                    "handle_document_analysis_request", "handle_insights_request",
                    "handle_operations_request", "handle_data_operations_request",
                    "handle_guide_chat_request", "handle_liaison_chat_request",
                    "handle_create_conversation_request", "handle_conversation_history_request",
                    "register_api_endpoint", "validate_api_request", "transform_for_frontend"
                ],
                mcp_tools=[],  # Experience services provide SOA APIs, not MCP tools
                additional_metadata={
                    "layer": "experience",
                    "api_gateway": True,
                    "composes": "business_enablement_orchestrators",
                    "chat_enabled": True
                }
            )
            
            self.logger.info("✅ Frontend Gateway Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Frontend Gateway Service initialization failed: {e}")
            return False
    
    async def _discover_orchestrators(self):
        """Discover Business Enablement orchestrators via BusinessOrchestrator."""
        try:
            # Get BusinessOrchestrator from DI container (it should be registered there now)
            business_orchestrator = self.di_container.service_registry.get("BusinessOrchestratorService")
            
            if business_orchestrator and hasattr(business_orchestrator, 'mvp_orchestrators'):
                self.logger.info("✅ Found BusinessOrchestratorService, discovering MVP orchestrators...")
                
                # Get orchestrators from BusinessOrchestrator's mvp_orchestrators dict
                # Note: keys are "content_analysis", not "content"
                if "content_analysis" in business_orchestrator.mvp_orchestrators:
                    self.content_orchestrator = business_orchestrator.mvp_orchestrators["content_analysis"]
                    self.logger.info("✅ Discovered ContentAnalysisOrchestrator from BusinessOrchestrator")
                else:
                    self.logger.warning("⚠️ ContentAnalysisOrchestrator not in mvp_orchestrators")
                    self.logger.warning(f"   Available keys: {list(business_orchestrator.mvp_orchestrators.keys())}")
                
                if "insights" in business_orchestrator.mvp_orchestrators:
                    self.insights_orchestrator = business_orchestrator.mvp_orchestrators["insights"]
                    self.logger.info("✅ Discovered InsightsOrchestrator from BusinessOrchestrator")
                else:
                    self.logger.warning("⚠️ InsightsOrchestrator not in mvp_orchestrators")
                
                if "operations" in business_orchestrator.mvp_orchestrators:
                    self.operations_orchestrator = business_orchestrator.mvp_orchestrators["operations"]
                    self.logger.info("✅ Discovered OperationsOrchestrator from BusinessOrchestrator")
                else:
                    self.logger.warning("⚠️ OperationsOrchestrator not in mvp_orchestrators")
                
                if "business_outcomes" in business_orchestrator.mvp_orchestrators:
                    self.business_outcomes_orchestrator = business_orchestrator.mvp_orchestrators["business_outcomes"]
                    self.logger.info("✅ Discovered BusinessOutcomesOrchestrator from BusinessOrchestrator")
                else:
                    self.logger.warning("⚠️ BusinessOutcomesOrchestrator not in mvp_orchestrators")
                
                self.logger.info(f"✅ Available MVP orchestrators: {list(business_orchestrator.mvp_orchestrators.keys())}")
                
                # Populate orchestrators dictionary for dictionary-style access
                if self.content_orchestrator:
                    self.orchestrators["ContentAnalysisOrchestrator"] = self.content_orchestrator
                if self.insights_orchestrator:
                    self.orchestrators["InsightsOrchestrator"] = self.insights_orchestrator
                if self.operations_orchestrator:
                    self.orchestrators["OperationsOrchestrator"] = self.operations_orchestrator
                if self.data_operations_orchestrator:
                    self.orchestrators["DataOperationsOrchestrator"] = self.data_operations_orchestrator
                if self.business_outcomes_orchestrator:
                    self.orchestrators["BusinessOutcomesOrchestrator"] = self.business_outcomes_orchestrator
                
                self.logger.info(f"✅ Orchestrators registered: {list(self.orchestrators.keys())}")
            else:
                self.logger.warning("⚠️ BusinessOrchestratorService not available or missing mvp_orchestrators")
                self.logger.warning(f"   DI container has: {list(self.di_container.service_registry.keys())}")
                
                # Discover Chat Service
                try:
                    self.chat_service = await curator.get_service("ChatService")
                    self.logger.info("✅ Discovered ChatService")
                except Exception:
                    self.logger.warning("⚠️ ChatService not yet available")
            
        except Exception as e:
            self.logger.error(f"❌ Orchestrator discovery failed: {e}")
    
    async def _expose_frontend_apis(self):
        """Expose frontend APIs for discovered orchestrators."""
        # Register API endpoints
        if self.content_orchestrator:
            await self.register_api_endpoint("/api/documents/analyze", self.handle_document_analysis_request)
        
        if self.insights_orchestrator:
            await self.register_api_endpoint("/api/insights/generate", self.handle_insights_request)
        
        if self.operations_orchestrator:
            await self.register_api_endpoint("/api/operations/optimize", self.handle_operations_request)
        
        if self.data_operations_orchestrator:
            await self.register_api_endpoint("/api/data/transform", self.handle_data_operations_request)
        
        # Register chat endpoints
        if self.chat_service:
            await self.register_api_endpoint("/api/chat/guide", self.handle_guide_chat_request)
            await self.register_api_endpoint("/api/chat/liaison", self.handle_liaison_chat_request)
            await self.register_api_endpoint("/api/chat/conversation/create", self.handle_create_conversation_request)
            await self.register_api_endpoint("/api/chat/conversation/history", self.handle_conversation_history_request)
    
    # ========================================================================
    # SOA APIs (Frontend Gateway)
    # ========================================================================
    
    async def expose_frontend_api(
        self,
        api_name: str,
        endpoint: str,
        handler: Callable
    ) -> bool:
        """
        Expose a frontend API endpoint (SOA API).
        
        Args:
            api_name: Name of the API
            endpoint: API endpoint path
            handler: Handler function for the API
        
        Returns:
            bool: True if API exposed successfully
        """
        try:
            self.registered_apis[endpoint] = {
                "api_name": api_name,
                "handler": handler,
                "exposed_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"✅ Exposed frontend API: {api_name} at {endpoint}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Expose frontend API failed: {e}")
            return False
    
    async def route_frontend_request(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Universal request router - routes requests to pillar-specific handlers (SOA API).
        
        Called by all protocol adapters (REST, GraphQL, WebSocket, gRPC).
        Parses endpoint to determine pillar and path, then routes to appropriate handler.
        
        Args:
            request: Frontend request data
                - endpoint: "/api/{pillar}/{path}" 
                - method: "GET" | "POST" | "PUT" | "DELETE"
                - params: Request parameters/body
                - headers: Optional headers
                - query_params: Optional query parameters
                - user_id: Optional user identifier
        
        Returns:
            Frontend-ready response
        """
        try:
            endpoint = request.get("endpoint", "")
            method = request.get("method", "POST")
            params = request.get("params", {})
            headers = request.get("headers", {})
            query_params = request.get("query_params", {})
            user_id = request.get("user_id") or params.get("user_id", "anonymous")
            
            self.logger.info(f"🌐 Routing {method} {endpoint}")
            
            # Parse endpoint: /api/{pillar}/{path}
            parts = endpoint.strip("/").split("/")
            if len(parts) < 3 or parts[0] != "api":
                return {
                    "success": False,
                    "error": "Invalid Endpoint",
                    "message": f"Endpoint must be /api/{{pillar}}/{{path}}, got: {endpoint}"
                }
            
            pillar = parts[1]  # content, insights, operations, business-outcomes
            path_parts = parts[2:]  # remaining path
            path = "/".join(path_parts)
            
            self.logger.info(f"📍 Pillar: {pillar}, Path: {path}")
            
            # Zero-Trust Authorization via Security Guard
            # "Secure by design, open by policy" - CTO requirement
            if self.security_guard:
                try:
                    auth_result = await self.security_guard.authorize_action({
                        "user_id": user_id,
                        "action": method,
                        "resource": endpoint,
                        "tenant_id": params.get("tenant_id", "default"),
                        "context": {
                            "pillar": pillar,
                            "path": path,
                            "headers": headers
                        }
                    })
                    
                    if not auth_result.get("success", False):
                        self.logger.warning(f"🛡️ Authorization denied: {user_id} -> {method} {endpoint}")
                        return {
                            "success": False,
                            "error": "Unauthorized",
                            "message": f"Access denied: {auth_result.get('message', 'Insufficient permissions')}"
                        }
                    
                    self.logger.info(f"✅ Authorization granted: {user_id} -> {method} {endpoint}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Authorization check failed: {e}")
                    # Fail closed (deny on error) for zero-trust
                    return {
                        "success": False,
                        "error": "Authorization Error",
                        "message": "Unable to verify authorization"
                    }
            else:
                # Security Guard not available - log warning but allow for MVP
                # TODO: Make Security Guard required for production deployment
                self.logger.warning(f"⚠️ Security Guard not available - request allowed without authorization check")
                self.logger.warning(f"   This is acceptable for MVP but MUST be fixed for production")
            
            # Route to pillar-specific handlers
            result = None
            
            # ================================================================
            # CONTENT PILLAR ROUTING
            # ================================================================
            if pillar == "content":
                if path == "upload-file" and method == "POST":
                    # Extract file data from params (will be added by universal router)
                    result = await self.handle_upload_file_request(
                        file_data=params.get("file_data"),
                        filename=params.get("filename"),
                        content_type=params.get("content_type"),
                        user_id=user_id,
                        session_id=params.get("session_id"),
                        copybook_data=params.get("copybook_data"),
                        copybook_filename=params.get("copybook_filename")
                    )
                
                elif path.startswith("process-file/") and method == "POST":
                    file_id = path.split("/")[1]
                    result = await self.handle_process_file_request(
                        file_id=file_id,
                        user_id=user_id,
                        copybook_file_id=params.get("copybook_file_id"),
                        processing_options=params.get("processing_options")
                    )
                
                elif path == "list-uploaded-files" and method == "GET":
                    result = await self.handle_list_uploaded_files_request(
                        user_id=user_id
                    )
                
                elif path.startswith("get-file-details/") and method == "GET":
                    file_id = path.split("/")[1]
                    result = await self.handle_get_file_details_request(
                        file_id=file_id,
                        user_id=user_id
                    )
                
                elif path == "health" and method == "GET":
                    result = await self.handle_content_pillar_health_check_request()
                
                else:
                    result = {
                        "success": False,
                        "error": "Not Found",
                        "message": f"Content Pillar endpoint not found: {path}"
                    }
            
            # ================================================================
            # INSIGHTS PILLAR ROUTING
            # ================================================================
            elif pillar == "insights":
                if path == "analyze-content" and method == "POST":
                    result = await self.handle_analyze_content_for_insights_semantic_request(
                        content_source=params.get("content_source"),
                        content_id=params.get("content_id"),
                        use_extracted_metadata=params.get("use_extracted_metadata", False),
                        metadata_id=params.get("metadata_id"),
                        analysis_type=params.get("analysis_type", "auto"),
                        user_id=user_id
                    )
                
                elif path == "query-analysis" and method == "POST":
                    result = await self.handle_query_insights_analysis_request(
                        analysis_id=params.get("analysis_id"),
                        query=params.get("query"),
                        user_id=user_id
                    )
                
                elif path == "available-content-metadata" and method == "GET":
                    result = await self.handle_get_available_content_metadata_request(
                        user_id=user_id
                    )
                
                elif path == "validate-content-metadata" and method == "POST":
                    result = await self.handle_validate_content_metadata_for_insights_request(
                        metadata_id=params.get("metadata_id"),
                        user_id=user_id
                    )
                
                elif path.startswith("analysis-results/") and method == "GET":
                    analysis_id = path.split("/")[1]
                    result = await self.handle_get_insights_analysis_results_request(
                        analysis_id=analysis_id,
                        user_id=user_id
                    )
                
                elif path.startswith("analysis-visualizations/") and method == "GET":
                    analysis_id = path.split("/")[1]
                    result = await self.handle_get_insights_analysis_visualizations_request(
                        analysis_id=analysis_id,
                        user_id=user_id
                    )
                
                elif path == "user-analyses" and method == "GET":
                    result = await self.handle_list_user_insights_analyses_request(
                        user_id=user_id
                    )
                
                elif path == "pillar-summary" and method == "GET":
                    result = await self.handle_get_insights_pillar_summary_request(
                        analysis_id=params.get("analysis_id"),
                        user_id=user_id
                    )
                
                elif path == "health" and method == "GET":
                    result = await self.handle_insights_pillar_health_check_request()
                
                else:
                    result = {
                        "success": False,
                        "error": "Not Found",
                        "message": f"Insights Pillar endpoint not found: {path}"
                    }
            
            # ================================================================
            # OPERATIONS PILLAR ROUTING
            # ================================================================
            elif pillar == "operations":
                # Session Management
                if path == "session/elements" and method == "GET":
                    result = await self.handle_get_session_elements_request(
                        session_token=params.get("session_token") or query_params.get("session_token")
                    )
                
                elif path == "session/elements" and method == "DELETE":
                    result = await self.handle_clear_session_elements_request(
                        session_token=params.get("session_token") or query_params.get("session_token")
                    )
                
                # Process Blueprint (support both hyphen and underscore formats)
                elif path in ["generate-workflow-from-sop", "generate_workflow_from_sop"] and method == "POST":
                    # Extract sop_content from either direct params or workflow_data
                    sop_content = params.get("sop_content")
                    if not sop_content and "workflow_data" in params:
                        sop_content = params["workflow_data"].get("sop_content")
                    
                    result = await self.handle_generate_workflow_from_sop_request(
                        session_token=params.get("session_token"),
                        sop_file_uuid=params.get("sop_file_uuid"),
                        sop_content=sop_content
                    )
                
                elif path in ["generate-sop-from-workflow", "generate_sop_from_workflow"] and method == "POST":
                    # Extract workflow_content from multiple possible locations
                    workflow_content = params.get("workflow_content")
                    if not workflow_content and "workflow_data" in params:
                        workflow_content = params["workflow_data"].get("workflow_content")
                    if not workflow_content and "sop_data" in params:
                        workflow_content = params["sop_data"].get("workflow")
                    
                    result = await self.handle_generate_sop_from_workflow_request(
                        session_token=params.get("session_token"),
                        workflow_file_uuid=params.get("workflow_file_uuid"),
                        workflow_content=workflow_content
                    )
                
                elif path == "files/analyze" and method == "GET":
                    result = await self.handle_analyze_file_request(
                        session_token=query_params.get("session_token"),
                        input_file_uuid=query_params.get("input_file_uuid"),
                        output_type=query_params.get("output_type")
                    )
                
                # Coexistence Analysis
                elif path == "files/coexistence" and method == "GET":
                    result = await self.handle_analyze_coexistence_files_request(
                        session_token=query_params.get("session_token")
                    )
                
                elif path == "coexistence/analyze" and method == "POST":
                    result = await self.handle_analyze_coexistence_content_request(
                        session_token=params.get("session_token"),
                        sop_content=params.get("sop_content"),
                        workflow_content=params.get("workflow_content")
                    )
                
                # Wizard Mode
                elif path == "wizard/start" and method == "POST":
                    result = await self.handle_start_wizard_request()
                
                elif path == "wizard/chat" and method == "POST":
                    result = await self.handle_wizard_chat_request(
                        session_token=params.get("session_token"),
                        user_message=params.get("user_message")
                    )
                
                elif path == "wizard/publish" and method == "POST":
                    result = await self.handle_wizard_publish_request(
                        session_token=params.get("session_token")
                    )
                
                # Blueprint Management
                elif path == "blueprint/save" and method == "POST":
                    result = await self.handle_save_blueprint_request(
                        blueprint=params.get("blueprint"),
                        user_id=params.get("user_id")
                    )
                
                # Liaison Agent (Conversational)
                elif path == "query" and method == "POST":
                    result = await self.handle_process_operations_query_request(
                        session_id=params.get("session_id"),
                        query=params.get("query"),
                        file_url=params.get("file_url"),
                        context=params.get("context")
                    )
                
                elif path == "conversation" and method == "POST":
                    result = await self.handle_process_operations_conversation_request(
                        session_id=params.get("session_id"),
                        message=params.get("message"),
                        context=params.get("context")
                    )
                
                elif path.startswith("session/") and path.endswith("/context") and method == "GET":
                    session_id = path.split("/")[1]
                    result = await self.handle_get_operations_conversation_context_request(
                        session_id=session_id
                    )
                
                elif path == "intent/analyze" and method == "POST":
                    result = await self.handle_analyze_operations_intent_request(
                        query=params.get("query")
                    )
                
                # Health Check
                elif path == "health" and method == "GET":
                    result = await self.handle_operations_pillar_health_check_request()
                
                else:
                    result = {
                        "success": False,
                        "error": "Not Found",
                        "message": f"Operations Pillar endpoint not found: {path}"
                    }
            
            # ================================================================
            # BUSINESS OUTCOMES PILLAR ROUTING
            # ================================================================
            elif pillar in ["business-outcomes", "business_outcomes"]:
                # Route to BusinessOutcomesOrchestrator semantic APIs
                if not self.business_outcomes_orchestrator:
                    result = {
                        "success": False,
                        "error": "Service Unavailable",
                        "message": "Business Outcomes Orchestrator is not available. Please try again later."
                    }
                else:
                    # Route to semantic API methods (support both hyphen and underscore formats)
                    if path in ["generate-strategic-roadmap", "generate_strategic_roadmap"] and method == "POST":
                        # Extract pillar_outputs from either direct params or context_data
                        context_data = params.get("context_data", {})
                        pillar_outputs = params.get("pillar_outputs") or context_data.get("pillar_outputs", {})
                        roadmap_options = params.get("roadmap_options") or context_data.get("roadmap_options", {})
                        
                        result = await self.handle_generate_strategic_roadmap_request(
                            pillar_outputs=pillar_outputs,
                            roadmap_options=roadmap_options,
                            user_id=user_id
                        )
                    
                    elif path in ["generate-proof-of-concept-proposal", "generate_proof_of_concept_proposal"] and method == "POST":
                        result = await self.handle_generate_poc_proposal_request(
                            pillar_outputs=params.get("pillar_outputs", {}),
                            proposal_options=params.get("proposal_options", {}),
                            user_id=user_id
                        )
                    
                    elif path in ["get-pillar-summaries", "get_pillar_summaries"] and method == "GET":
                        result = await self.handle_get_pillar_summaries_request(
                            session_id=query_params.get("session_id") or params.get("session_id"),
                            user_id=user_id
                        )
                    
                    elif path in ["get-journey-visualization", "get_journey_visualization"] and method == "GET":
                        result = await self.handle_get_journey_visualization_request(
                            session_id=query_params.get("session_id") or params.get("session_id"),
                            user_id=user_id
                        )
                    
                    elif path == "health" and method == "GET":
                        result = await self.handle_business_outcomes_health_check_request()
                    
                    else:
                        result = {
                            "success": False,
                            "error": "Not Found",
                            "message": f"Business Outcomes Pillar endpoint not found: {path}"
                        }
            
            # ================================================================
            # UNKNOWN PILLAR
            # ================================================================
            else:
                result = {
                    "success": False,
                    "error": "Not Found",
                    "message": f"Unknown pillar: {pillar}"
                }
            
            # Transform for frontend (if result exists)
            if result:
                frontend_response = await self.transform_for_frontend(result)
                
                # Log request via Librarian
                try:
                    await self.store_document(
                        document_data={
                            "request": request,
                            "response": frontend_response,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        metadata={
                            "type": "api_request_log",
                            "endpoint": endpoint,
                            "method": method,
                            "pillar": pillar,
                            "path": path
                        }
                    )
                except Exception as log_error:
                    self.logger.warning(f"⚠️  Failed to log request: {log_error}")
                
                return frontend_response
            
            return {
                "success": False,
                "error": "No Handler",
                "message": f"No handler found for: {endpoint}"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Route frontend request failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": "Internal Server Error",
                "message": str(e)
            }
    
    async def get_frontend_apis(self) -> Dict[str, Any]:
        """
        Get all exposed frontend APIs (SOA API).
        
        Returns:
            Dictionary of exposed APIs
        """
        return {
            "success": True,
            "apis": {
                endpoint: {
                    "api_name": info["api_name"],
                    "exposed_at": info["exposed_at"]
                }
                for endpoint, info in self.registered_apis.items()
            },
            "total_apis": len(self.registered_apis)
        }
    
    # ========================================================================
    # REQUEST HANDLERS (Compose Business Enablement Orchestrators)
    # ========================================================================
    
    async def handle_document_analysis_request(
        self,
        document_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle document analysis request (Frontend API → ContentAnalysisOrchestrator).
        
        Args:
            document_id: ID of document to analyze
            options: Optional analysis options
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.content_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Content analysis service not available"
                }
            
            # Call Business Enablement orchestrator
            result = await self.content_orchestrator.analyze_document(document_id)
            
            self.logger.info(f"✅ Document analysis complete: {document_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Document analysis request failed: {e}")
            return {
                "success": False,
                "error": "Analysis Failed",
                "message": str(e)
            }
    
    async def handle_insights_request(
        self,
        data_id: str,
        insight_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Handle insights generation request (Frontend API → InsightsOrchestrator).
        
        Args:
            data_id: ID of data to analyze
            insight_types: Optional list of insight types to generate
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights service not available"
                }
            
            # Call Business Enablement orchestrator
            result = await self.insights_orchestrator.generate_insights(
                data_id=data_id,
                insight_types=insight_types or []
            )
            
            self.logger.info(f"✅ Insights generated: {data_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Insights request failed: {e}")
            return {
                "success": False,
                "error": "Insights Failed",
                "message": str(e)
            }
    
    async def handle_operations_request(
        self,
        process_id: str,
        operation_type: str
    ) -> Dict[str, Any]:
        """
        Handle operations request (Frontend API → OperationsOrchestrator).
        
        Args:
            process_id: ID of process to optimize
            operation_type: Type of operation (optimize, build_sop, etc.)
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.operations_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Operations service not available"
                }
            
            # Call Business Enablement orchestrator
            result = await self.operations_orchestrator.execute(
                request={
                    "action": operation_type,
                    "params": {"process_id": process_id}
                }
            )
            
            self.logger.info(f"✅ Operation complete: {operation_type} on {process_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Operations request failed: {e}")
            return {
                "success": False,
                "error": "Operation Failed",
                "message": str(e)
            }
    
    async def handle_data_operations_request(
        self,
        data_id: str,
        operation_type: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle data operations request (Frontend API → DataOperationsOrchestrator).
        
        Args:
            data_id: ID of data to process
            operation_type: Type of operation (transform, validate, reconcile)
            options: Optional operation options
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.data_operations_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Data operations service not available"
                }
            
            # Call Business Enablement orchestrator
            result = await self.data_operations_orchestrator.execute(
                request={
                    "action": operation_type,
                    "params": {"data_id": data_id, **( options or {})}
                }
            )
            
            self.logger.info(f"✅ Data operation complete: {operation_type} on {data_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Data operations request failed: {e}")
            return {
                "success": False,
                "error": "Data Operation Failed",
                "message": str(e)
            }
    
    # ========================================================================
    # CHAT HANDLERS (Frontend API → ChatService)
    # ========================================================================
    
    async def handle_guide_chat_request(
        self,
        message: str,
        conversation_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Handle guide chat request (Frontend API → ChatService → GuideAgent).
        
        Implements: MVP requirement for Guide Agent in persistent chat panel.
        
        Args:
            message: User's message
            conversation_id: Conversation ID
            user_id: User ID
        
        Returns:
            Frontend-ready chat response
        """
        try:
            if not self.chat_service:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Chat service not available"
                }
            
            # Send message to Guide Agent via ChatService
            result = await self.chat_service.send_message_to_guide(
                message=message,
                conversation_id=conversation_id,
                user_id=user_id
            )
            
            self.logger.info(f"✅ Guide chat message sent: {conversation_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Guide chat request failed: {e}")
            return {
                "success": False,
                "error": "Chat Failed",
                "message": str(e)
            }
    
    async def handle_liaison_chat_request(
        self,
        message: str,
        pillar: str,
        conversation_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Handle liaison chat request (Frontend API → ChatService → Liaison Agent).
        
        Implements: MVP requirement for pillar-specific liaison agents in chat panel.
        
        Args:
            message: User's message
            pillar: Pillar name (content, insights, operations, business_outcomes)
            conversation_id: Conversation ID
            user_id: User ID
        
        Returns:
            Frontend-ready chat response
        """
        try:
            if not self.chat_service:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Chat service not available"
                }
            
            # Send message to Liaison Agent via ChatService
            result = await self.chat_service.send_message_to_liaison(
                message=message,
                pillar=pillar,
                conversation_id=conversation_id,
                user_id=user_id
            )
            
            self.logger.info(f"✅ Liaison chat message sent: {pillar} - {conversation_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Liaison chat request failed: {e}")
            return {
                "success": False,
                "error": "Chat Failed",
                "message": str(e)
            }
    
    async def handle_create_conversation_request(
        self,
        user_id: str,
        initial_agent: str = "guide"
    ) -> Dict[str, Any]:
        """
        Handle create conversation request (Frontend API → ChatService).
        
        Args:
            user_id: User ID
            initial_agent: Initial agent (guide, content, insights, operations, business_outcomes)
        
        Returns:
            New conversation details
        """
        try:
            if not self.chat_service:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Chat service not available"
                }
            
            result = await self.chat_service.create_conversation(
                user_id=user_id,
                initial_agent=initial_agent
            )
            
            self.logger.info(f"✅ Conversation created: {result.get('conversation_id')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Create conversation request failed: {e}")
            return {
                "success": False,
                "error": "Conversation Creation Failed",
                "message": str(e)
            }
    
    async def handle_conversation_history_request(
        self,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Handle conversation history request (Frontend API → ChatService).
        
        Args:
            conversation_id: Conversation ID
        
        Returns:
            Conversation history
        """
        try:
            if not self.chat_service:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Chat service not available"
                }
            
            result = await self.chat_service.get_conversation_history(
                conversation_id=conversation_id
            )
            
            self.logger.info(f"✅ Conversation history retrieved: {conversation_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Conversation history request failed: {e}")
            return {
                "success": False,
                "error": "History Retrieval Failed",
                "message": str(e)
            }
    
    # ========================================================================
    # INSIGHTS PILLAR SEMANTIC API HANDLERS
    # ========================================================================
    
    async def handle_analyze_content_for_insights_semantic_request(
        self,
        source_type: str,
        file_id: Optional[str] = None,
        content_metadata_id: Optional[str] = None,
        content_type: str = "structured",
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle analyze content for insights request (Frontend API → InsightsOrchestrator).
        Semantic API: Primary analysis endpoint matching semantic router signature.
        
        Args:
            source_type: 'file' or 'content_metadata'
            file_id: File identifier (if source_type='file')
            content_metadata_id: Content metadata ID (if source_type='content_metadata')
            content_type: 'structured', 'unstructured', or 'hybrid'
            analysis_options: Optional configuration
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            # Call Business Enablement orchestrator (domain capability)
            result = await self.insights_orchestrator.analyze_content_for_insights(
                source_type=source_type,
                file_id=file_id,
                content_metadata_id=content_metadata_id,
                content_type=content_type,
                analysis_options=analysis_options
            )
            
            self.logger.info(f"✅ Content analyzed for insights: source_type={source_type}, content_type={content_type}")
            
            # Transform for frontend (REST layer)
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Analyze content for insights failed: {e}")
            return {
                "success": False,
                "error": "Analysis Failed",
                "message": str(e)
            }
    
    async def handle_analyze_content_for_insights_request(
        self,
        content_metadata_ids: List[str],
        analysis_type: str = "auto",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle analyze content request (Frontend API → InsightsOrchestrator).
        Semantic API: Analyze content metadata for insights.
        
        Args:
            content_metadata_ids: List of content metadata IDs to analyze
            analysis_type: Type of analysis (auto, structured, unstructured, hybrid)
            user_id: Optional user ID
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            # Call Business Enablement orchestrator (domain capability)
            result = await self.insights_orchestrator.analyze_content(
                content_metadata_ids=content_metadata_ids,
                analysis_type=analysis_type,
                user_id=user_id
            )
            
            self.logger.info(f"✅ Content analyzed for insights: {len(content_metadata_ids)} files")
            
            # Transform for frontend (REST layer)
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Analyze content for insights failed: {e}")
            return {
                "success": False,
                "error": "Analysis Failed",
                "message": str(e)
            }
    
    async def handle_query_insights_analysis_request(
        self,
        query: str,
        analysis_id: str,
        query_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        Handle query analysis request (Frontend API → InsightsOrchestrator).
        Semantic API: NLP query on analysis results.
        
        Args:
            query: Natural language query
            analysis_id: ID of analysis to query
            query_type: Type of query result (table, chart, summary, auto)
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            # Call orchestrator
            result = await self.insights_orchestrator.query_analysis_results(
                query=query,
                analysis_id=analysis_id,
                query_type=query_type
            )
            
            self.logger.info(f"✅ Analysis queried: {query} on {analysis_id}")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Query insights analysis failed: {e}")
            return {
                "success": False,
                "error": "Query Failed",
                "message": str(e)
            }
    
    async def handle_get_available_content_metadata_request(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle get available content metadata request.
        Semantic API: List content available for analysis.
        
        Args:
            user_id: Optional user ID
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            result = await self.insights_orchestrator.get_available_content_metadata(
                user_id=user_id
            )
            
            self.logger.info(f"✅ Available content metadata retrieved")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Get available content metadata failed: {e}")
            return {
                "success": False,
                "error": "Retrieval Failed",
                "message": str(e)
            }
    
    async def handle_validate_content_metadata_for_insights_request(
        self,
        content_metadata_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Handle validate content metadata request.
        Semantic API: Validate content metadata for insights analysis.
        
        Args:
            content_metadata_ids: List of content metadata IDs to validate
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            result = await self.insights_orchestrator.validate_content_metadata(
                content_metadata_ids=content_metadata_ids
            )
            
            self.logger.info(f"✅ Content metadata validated: {len(content_metadata_ids)} items")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Validate content metadata failed: {e}")
            return {
                "success": False,
                "error": "Validation Failed",
                "message": str(e)
            }
    
    async def handle_get_insights_analysis_results_request(
        self,
        analysis_id: str
    ) -> Dict[str, Any]:
        """
        Handle get analysis results request.
        Semantic API: Get complete analysis results.
        
        Args:
            analysis_id: Analysis ID
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            result = await self.insights_orchestrator.get_analysis_results(
                analysis_id=analysis_id
            )
            
            self.logger.info(f"✅ Analysis results retrieved: {analysis_id}")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Get analysis results failed: {e}")
            return {
                "success": False,
                "error": "Retrieval Failed",
                "message": str(e)
            }
    
    async def handle_get_insights_analysis_visualizations_request(
        self,
        analysis_id: str
    ) -> Dict[str, Any]:
        """
        Handle get analysis visualizations request.
        Semantic API: Get visualizations for analysis.
        
        Args:
            analysis_id: Analysis ID
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            result = await self.insights_orchestrator.get_analysis_visualizations(
                analysis_id=analysis_id
            )
            
            self.logger.info(f"✅ Analysis visualizations retrieved: {analysis_id}")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Get analysis visualizations failed: {e}")
            return {
                "success": False,
                "error": "Retrieval Failed",
                "message": str(e)
            }
    
    async def handle_list_user_insights_analyses_request(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle list user analyses request.
        Semantic API: List all analyses for user.
        
        Args:
            user_id: Optional user ID
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            result = await self.insights_orchestrator.list_user_analyses(
                user_id=user_id
            )
            
            self.logger.info(f"✅ User analyses listed")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ List user analyses failed: {e}")
            return {
                "success": False,
                "error": "Listing Failed",
                "message": str(e)
            }
    
    async def handle_get_insights_pillar_summary_request(
        self,
        analysis_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle get pillar summary request.
        Semantic API: Get Insights Pillar summary for Business Outcomes.
        
        Args:
            analysis_id: Optional analysis ID (if None, returns most recent)
        
        Returns:
            Frontend-ready response
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Insights orchestrator not available"
                }
            
            result = await self.insights_orchestrator.get_pillar_summary(
                analysis_id=analysis_id
            )
            
            self.logger.info(f"✅ Insights pillar summary retrieved")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Get pillar summary failed: {e}")
            return {
                "success": False,
                "error": "Summary Failed",
                "message": str(e)
            }
    
    async def handle_insights_pillar_health_check_request(self) -> Dict[str, Any]:
        """
        Handle insights pillar health check request.
        Semantic API: Check if Insights Pillar is available.
        
        Returns:
            Health status
        """
        try:
            if not self.insights_orchestrator:
                return {
                    "status": "unavailable",
                    "pillar": "insights",
                    "message": "Insights orchestrator not available",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Call orchestrator health check
            result = await self.insights_orchestrator.health_check()
            
            return {
                "status": "healthy",
                "pillar": "insights",
                "orchestrator_status": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Insights health check failed: {e}")
            return {
                "status": "unhealthy",
                "pillar": "insights",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ========================================================================
    # CONTENT PILLAR HANDLERS (Semantic API)
    # ========================================================================
    
    async def handle_upload_file_request(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        user_id: str,
        session_id: Optional[str] = None,
        copybook_data: Optional[bytes] = None,
        copybook_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle file upload request (Content Pillar).
        
        Args:
            file_data: File binary data
            filename: Original filename
            content_type: MIME type
            user_id: User identifier
            session_id: Optional session ID
            copybook_data: Optional copybook file data
            copybook_filename: Optional copybook filename
        
        Returns:
            Upload result with file metadata
        """
        try:
            self.logger.info(f"📤 Content Pillar: Upload file request: {filename}")
            
            # Get Content Analysis Orchestrator
            content_orchestrator = self.orchestrators.get("ContentAnalysisOrchestrator")
            if not content_orchestrator:
                self.logger.error("❌ ContentAnalysisOrchestrator not available")
                return {
                    "success": False,
                    "error": "Content Analysis Orchestrator not available"
                }
            
            # Call orchestrator's upload method
            result = await content_orchestrator.upload_file(
                file_data=file_data,
                filename=filename,
                file_type=content_type,
                user_id=user_id,
                session_id=session_id
            )
            
            # Handle copybook upload if provided
            if copybook_data and copybook_filename:
                self.logger.info(f"📎 Uploading copybook: {copybook_filename}")
                copybook_result = await content_orchestrator.upload_file(
                    file_data=copybook_data,
                    filename=copybook_filename,
                    file_type="text/plain",
                    user_id=user_id,
                    session_id=session_id
                )
                
                if copybook_result.get("success"):
                    result["copybook_file_id"] = copybook_result.get("file_id")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Upload file request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_process_file_request(
        self,
        file_id: str,
        user_id: str,
        copybook_file_id: Optional[str] = None,
        processing_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle file processing request (Content Pillar).
        
        Args:
            file_id: File UUID
            user_id: User identifier
            copybook_file_id: Optional copybook file UUID
            processing_options: Optional processing options
        
        Returns:
            Processing result with parsed data and metadata
        """
        try:
            self.logger.info(f"⚙️ Content Pillar: Process file request: {file_id}")
            
            # Get Content Analysis Orchestrator
            content_orchestrator = self.orchestrators.get("ContentAnalysisOrchestrator")
            if not content_orchestrator:
                self.logger.error("❌ ContentAnalysisOrchestrator not available")
                return {
                    "success": False,
                    "error": "Content Analysis Orchestrator not available"
                }
            
            # Call orchestrator's process method
            result = await content_orchestrator.process_file(
                file_id=file_id,
                user_id=user_id,
                copybook_file_id=copybook_file_id,
                processing_options=processing_options or {}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Process file request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_list_uploaded_files_request(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Handle list uploaded files request (Content Pillar).
        
        Args:
            user_id: User identifier
        
        Returns:
            List of uploaded files
        """
        try:
            self.logger.info(f"📋 Content Pillar: List uploaded files request for user: {user_id}")
            
            # Get Content Analysis Orchestrator
            content_orchestrator = self.orchestrators.get("ContentAnalysisOrchestrator")
            if not content_orchestrator:
                self.logger.error("❌ ContentAnalysisOrchestrator not available")
                return {
                    "success": False,
                    "files": [],
                    "count": 0,
                    "error": "Content Analysis Orchestrator not available"
                }
            
            # Call orchestrator's list files method
            result = await content_orchestrator.list_uploaded_files(user_id=user_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ List uploaded files request failed: {e}")
            return {
                "success": False,
                "files": [],
                "count": 0,
                "error": str(e)
            }
    
    async def handle_get_file_details_request(
        self,
        file_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Handle get file details request (Content Pillar).
        
        Args:
            file_id: File UUID
            user_id: User identifier
        
        Returns:
            File details
        """
        try:
            self.logger.info(f"🔍 Content Pillar: Get file details request: {file_id}")
            
            # Get Content Analysis Orchestrator
            content_orchestrator = self.orchestrators.get("ContentAnalysisOrchestrator")
            if not content_orchestrator:
                self.logger.error("❌ ContentAnalysisOrchestrator not available")
                return {
                    "success": False,
                    "file": None,
                    "error": "Content Analysis Orchestrator not available"
                }
            
            # Call orchestrator's get file details method
            result = await content_orchestrator.get_file_details(
                file_id=file_id,
                user_id=user_id
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Get file details request failed: {e}")
            return {
                "success": False,
                "file": None,
                "error": str(e)
            }
    
    async def _lazy_discover_orchestrators_if_needed(self):
        """Lazy-discover orchestrators if they weren't available during initialization."""
        if not self.orchestrators:
            self.logger.info("🔄 Orchestrators not available, attempting lazy discovery...")
            await self._discover_orchestrators()
    
    async def handle_content_pillar_health_check_request(self) -> Dict[str, Any]:
        """
        Handle content pillar health check request.
        
        Returns:
            Health status
        """
        try:
            self.logger.info("🏥 Content Pillar: Health check request")
            
            # Lazy-discover orchestrators if needed
            await self._lazy_discover_orchestrators_if_needed()
            
            # Get Content Analysis Orchestrator
            content_orchestrator = self.orchestrators.get("ContentAnalysisOrchestrator")
            if not content_orchestrator:
                return {
                    "status": "unhealthy",
                    "pillar": "content",
                    "error": "ContentAnalysisOrchestrator not available",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Call orchestrator's health check
            result = await content_orchestrator.health_check()
            
            return {
                "status": "healthy",
                "pillar": "content",
                "orchestrator_status": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Content health check failed: {e}")
            return {
                "status": "unhealthy",
                "pillar": "content",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ========================================================================
    # OPERATIONS PILLAR HANDLERS (Semantic API)
    # ========================================================================
    
    async def handle_get_session_elements_request(
        self,
        session_token: str
    ) -> Dict[str, Any]:
        """
        Handle get session elements request (Operations Pillar).
        
        Args:
            session_token: Session identifier
        
        Returns:
            Session state with SOP and Workflow elements
        """
        try:
            self.logger.info(f"📋 Operations Pillar: Get session elements request")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "valid": False,
                    "action": "error",
                    "missing": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.get_session_elements(
                session_token=session_token
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Get session elements request failed: {e}")
            return {
                "valid": False,
                "action": "error",
                "missing": str(e)
            }
    
    async def handle_clear_session_elements_request(
        self,
        session_token: str
    ) -> Dict[str, Any]:
        """
        Handle clear session elements request (Operations Pillar).
        
        Args:
            session_token: Session identifier
        
        Returns:
            Success status
        """
        try:
            self.logger.info(f"🗑️ Operations Pillar: Clear session elements request")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "message": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.clear_session_elements(
                session_token=session_token
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Clear session elements request failed: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def handle_generate_workflow_from_sop_request(
        self,
        session_token: str,
        sop_file_uuid: str
    ) -> Dict[str, Any]:
        """
        Handle generate workflow from SOP request (Operations Pillar).
        
        Args:
            session_token: Session identifier
            sop_file_uuid: SOP file UUID
        
        Returns:
            Generated workflow
        """
        try:
            self.logger.info(f"📄➡️📊 Operations Pillar: Generate workflow from SOP: {sop_file_uuid}")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.generate_workflow_from_sop(
                session_token=session_token,
                sop_file_uuid=sop_file_uuid
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Generate workflow from SOP request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_generate_sop_from_workflow_request(
        self,
        session_token: str,
        workflow_file_uuid: str
    ) -> Dict[str, Any]:
        """
        Handle generate SOP from workflow request (Operations Pillar).
        
        Args:
            session_token: Session identifier
            workflow_file_uuid: Workflow file UUID
        
        Returns:
            Generated SOP
        """
        try:
            self.logger.info(f"📊➡️📄 Operations Pillar: Generate SOP from workflow: {workflow_file_uuid}")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.generate_sop_from_workflow(
                session_token=session_token,
                workflow_file_uuid=workflow_file_uuid
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Generate SOP from workflow request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_analyze_file_request(
        self,
        session_token: str,
        input_file_uuid: str,
        output_type: str
    ) -> Dict[str, Any]:
        """
        Handle analyze file request (Operations Pillar).
        
        Args:
            session_token: Session identifier
            input_file_uuid: Input file UUID
            output_type: "workflow" or "sop"
        
        Returns:
            Analysis result
        """
        try:
            self.logger.info(f"🔍 Operations Pillar: Analyze file: {input_file_uuid} → {output_type}")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.analyze_file(
                session_token=session_token,
                input_file_uuid=input_file_uuid,
                output_type=output_type
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Analyze file request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_analyze_coexistence_files_request(
        self,
        session_token: str
    ) -> Dict[str, Any]:
        """
        Handle analyze coexistence (file-based) request (Operations Pillar).
        
        Args:
            session_token: Session identifier (contains SOP and Workflow)
        
        Returns:
            Coexistence analysis
        """
        try:
            self.logger.info(f"🔄 Operations Pillar: Analyze coexistence (files)")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.analyze_coexistence_files(
                session_token=session_token
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Analyze coexistence files request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_analyze_coexistence_content_request(
        self,
        session_token: str,
        sop_content: str,
        workflow_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle analyze coexistence (content-based) request (Operations Pillar).
        
        Args:
            session_token: Session identifier
            sop_content: SOP text content
            workflow_content: Workflow object
        
        Returns:
            Coexistence analysis
        """
        try:
            self.logger.info(f"🔄 Operations Pillar: Analyze coexistence (content)")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.analyze_coexistence_content(
                session_token=session_token,
                sop_content=sop_content,
                workflow_content=workflow_content
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Analyze coexistence content request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_start_wizard_request(self) -> Dict[str, Any]:
        """
        Handle start wizard request (Operations Pillar).
        
        Returns:
            Wizard session info
        """
        try:
            self.logger.info(f"🧙 Operations Pillar: Start wizard")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.start_wizard()
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Start wizard request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_wizard_chat_request(
        self,
        session_token: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Handle wizard chat request (Operations Pillar).
        
        Args:
            session_token: Wizard session token
            user_message: User's message
        
        Returns:
            Wizard response
        """
        try:
            self.logger.info(f"💬 Operations Pillar: Wizard chat")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.wizard_chat(
                session_token=session_token,
                user_message=user_message
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Wizard chat request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_wizard_publish_request(
        self,
        session_token: str
    ) -> Dict[str, Any]:
        """
        Handle wizard publish request (Operations Pillar).
        
        Args:
            session_token: Wizard session token
        
        Returns:
            Published SOP
        """
        try:
            self.logger.info(f"📤 Operations Pillar: Wizard publish")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.wizard_publish(
                session_token=session_token
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Wizard publish request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_save_blueprint_request(
        self,
        blueprint: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Handle save blueprint request (Operations Pillar).
        
        Args:
            blueprint: Blueprint object
            user_id: User identifier
        
        Returns:
            Blueprint ID
        """
        try:
            self.logger.info(f"💾 Operations Pillar: Save blueprint for user: {user_id}")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.save_blueprint(
                blueprint=blueprint,
                user_id=user_id
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Save blueprint request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_process_operations_query_request(
        self,
        session_id: str,
        query: str,
        file_url: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle process operations query request (Operations Pillar).
        
        Args:
            session_id: Session identifier
            query: User query
            file_url: Optional file URL
            context: Optional context
        
        Returns:
            Query response
        """
        try:
            self.logger.info(f"❓ Operations Pillar: Process query: {query}")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.process_query(
                session_id=session_id,
                query=query,
                file_url=file_url,
                context=context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Process operations query request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_process_operations_conversation_request(
        self,
        session_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle process operations conversation request (Operations Pillar).
        
        Args:
            session_id: Session identifier
            message: User message
            context: Optional context
        
        Returns:
            Conversation response
        """
        try:
            self.logger.info(f"💬 Operations Pillar: Process conversation")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.process_conversation(
                session_id=session_id,
                message=message,
                context=context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Process operations conversation request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_get_operations_conversation_context_request(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Handle get operations conversation context request (Operations Pillar).
        
        Args:
            session_id: Session identifier
        
        Returns:
            Conversation context
        """
        try:
            self.logger.info(f"📝 Operations Pillar: Get conversation context: {session_id}")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.get_conversation_context(
                session_id=session_id
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Get conversation context request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_analyze_operations_intent_request(
        self,
        query: str
    ) -> Dict[str, Any]:
        """
        Handle analyze operations intent request (Operations Pillar).
        
        Args:
            query: User query
        
        Returns:
            Intent analysis
        """
        try:
            self.logger.info(f"🔍 Operations Pillar: Analyze intent: {query}")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                self.logger.error("❌ OperationsOrchestrator not available")
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Call orchestrator's method
            result = await operations_orchestrator.analyze_intent(
                query=query
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Analyze operations intent request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_operations_pillar_health_check_request(self) -> Dict[str, Any]:
        """
        Handle operations pillar health check request.
        
        Returns:
            Health status
        """
        try:
            self.logger.info("🏥 Operations Pillar: Health check request")
            
            # Get Operations Orchestrator
            operations_orchestrator = self.orchestrators.get("OperationsOrchestrator")
            if not operations_orchestrator:
                return {
                    "status": "unhealthy",
                    "pillar": "operations",
                    "error": "OperationsOrchestrator not available",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Call orchestrator's health check
            result = await operations_orchestrator.health_check()
            
            return {
                "status": "healthy",
                "pillar": "operations",
                "orchestrator_status": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Operations health check failed: {e}")
            return {
                "status": "unhealthy",
                "pillar": "operations",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ========================================================================
    # BUSINESS OUTCOMES PILLAR REQUEST HANDLERS
    # ========================================================================
    
    async def handle_generate_strategic_roadmap_request(
        self,
        pillar_outputs: Dict[str, Any],
        roadmap_options: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Handle generate strategic roadmap request (Business Outcomes Pillar).
        Semantic API: Generate strategic roadmap from pillar outputs.
        
        Args:
            pillar_outputs: Outputs from all pillars
            roadmap_options: Optional roadmap generation options
            user_id: User identifier
        
        Returns:
            Frontend-ready response
        """
        try:
            self.logger.info(f"🗺️ Business Outcomes Pillar: Generate strategic roadmap for user: {user_id}")
            
            if not self.business_outcomes_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Business Outcomes Orchestrator is not available"
                }
            
            # Call orchestrator's semantic API method
            context_data = {
                "pillar_outputs": pillar_outputs,
                "roadmap_options": roadmap_options or {}
            }
            result = await self.business_outcomes_orchestrator.generate_strategic_roadmap(
                context_data=context_data,
                user_id=user_id
            )
            
            self.logger.info(f"✅ Strategic roadmap generated successfully")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Generate strategic roadmap failed: {e}")
            return {
                "success": False,
                "error": "Generation Failed",
                "message": str(e)
            }
    
    async def handle_generate_poc_proposal_request(
        self,
        pillar_outputs: Dict[str, Any],
        proposal_options: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Handle generate POC proposal request (Business Outcomes Pillar).
        Semantic API: Generate POC proposal from pillar outputs.
        
        Args:
            pillar_outputs: Outputs from all pillars
            proposal_options: Optional proposal generation options
            user_id: User identifier
        
        Returns:
            Frontend-ready response
        """
        try:
            self.logger.info(f"📋 Business Outcomes Pillar: Generate POC proposal for user: {user_id}")
            
            if not self.business_outcomes_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Business Outcomes Orchestrator is not available"
                }
            
            # Call orchestrator's semantic API method
            context_data = {
                "pillar_outputs": pillar_outputs,
                "proposal_options": proposal_options or {}
            }
            result = await self.business_outcomes_orchestrator.generate_poc_proposal(
                context_data=context_data,
                user_id=user_id
            )
            
            self.logger.info(f"✅ POC proposal generated successfully")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Generate POC proposal failed: {e}")
            return {
                "success": False,
                "error": "Generation Failed",
                "message": str(e)
            }
    
    async def handle_get_pillar_summaries_request(
        self,
        session_id: Optional[str] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Handle get pillar summaries request (Business Outcomes Pillar).
        Semantic API: Get summaries from all pillars.
        
        Args:
            session_id: Optional session identifier
            user_id: User identifier
        
        Returns:
            Frontend-ready response
        """
        try:
            self.logger.info(f"📊 Business Outcomes Pillar: Get pillar summaries for session: {session_id}")
            
            if not self.business_outcomes_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Business Outcomes Orchestrator is not available"
                }
            
            # Call orchestrator's semantic API method
            result = await self.business_outcomes_orchestrator.get_pillar_summaries(
                session_id=session_id or "",
                user_id=user_id
            )
            
            self.logger.info(f"✅ Pillar summaries retrieved successfully")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Get pillar summaries failed: {e}")
            return {
                "success": False,
                "error": "Retrieval Failed",
                "message": str(e)
            }
    
    async def handle_get_journey_visualization_request(
        self,
        session_id: Optional[str] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Handle get journey visualization request (Business Outcomes Pillar).
        Semantic API: Get journey visualization across all pillars.
        
        Args:
            session_id: Optional session identifier
            user_id: User identifier
        
        Returns:
            Frontend-ready response
        """
        try:
            self.logger.info(f"📊 Business Outcomes Pillar: Get journey visualization for session: {session_id}")
            
            if not self.business_outcomes_orchestrator:
                return {
                    "success": False,
                    "error": "Service Unavailable",
                    "message": "Business Outcomes Orchestrator is not available"
                }
            
            # Call orchestrator's semantic API method
            result = await self.business_outcomes_orchestrator.get_journey_visualization(
                session_id=session_id or "",
                user_id=user_id
            )
            
            self.logger.info(f"✅ Journey visualization retrieved successfully")
            
            return await self.transform_for_frontend(result)
            
        except Exception as e:
            self.logger.error(f"❌ Get journey visualization failed: {e}")
            return {
                "success": False,
                "error": "Retrieval Failed",
                "message": str(e)
            }
    
    async def handle_business_outcomes_health_check_request(self) -> Dict[str, Any]:
        """
        Handle business outcomes pillar health check request.
        
        Returns:
            Health status
        """
        try:
            self.logger.info("🏥 Business Outcomes Pillar: Health check request")
            
            if not self.business_outcomes_orchestrator:
                return {
                    "status": "unhealthy",
                    "pillar": "business_outcomes",
                    "error": "BusinessOutcomesOrchestrator not available",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Call orchestrator's health check
            result = await self.business_outcomes_orchestrator.health_check()
            
            return {
                "status": "healthy",
                "pillar": "business_outcomes",
                "orchestrator_status": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Business Outcomes health check failed: {e}")
            return {
                "status": "unhealthy",
                "pillar": "business_outcomes",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ========================================================================
    # API MANAGEMENT
    # ========================================================================
    
    async def register_api_endpoint(
        self,
        endpoint: str,
        handler: Callable
    ) -> bool:
        """Register an API endpoint with handler (SOA API)."""
        return await self.expose_frontend_api(
            api_name=endpoint.split("/")[-1],
            endpoint=endpoint,
            handler=handler
        )
    
    async def validate_api_request(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate API request (SOA API).
        
        Args:
            request: Request to validate
        
        Returns:
            Validation result
        """
        try:
            # Validate required fields
            required_fields = ["endpoint", "method"]
            missing_fields = [f for f in required_fields if f not in request]
            
            if missing_fields:
                return {
                    "valid": False,
                    "errors": [f"Missing required field: {f}" for f in missing_fields]
                }
            
            # Validate endpoint exists
            if request["endpoint"] not in self.registered_apis:
                return {
                    "valid": False,
                    "errors": [f"Endpoint not found: {request['endpoint']}"]
                }
            
            return {
                "valid": True,
                "endpoint": request["endpoint"]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Validate API request failed: {e}")
            return {
                "valid": False,
                "errors": [str(e)]
            }
    
    async def transform_for_frontend(
        self,
        orchestrator_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transform orchestrator response for frontend consumption (SOA API).
        
        Args:
            orchestrator_response: Response from Business Enablement orchestrator
        
        Returns:
            Frontend-ready response
        """
        try:
            # Add frontend-specific fields
            frontend_response = {
                **orchestrator_response,
                "ui_state": "success" if orchestrator_response.get("success") else "error",
                "timestamp": datetime.utcnow().isoformat(),
                "api_version": "v1"
            }
            
            # Add next actions if success
            if orchestrator_response.get("success"):
                frontend_response["next_actions"] = [
                    "view_results",
                    "export",
                    "share"
                ]
            
            return frontend_response
            
        except Exception as e:
            self.logger.error(f"❌ Transform for frontend failed: {e}")
            return orchestrator_response
    
    # ========================================================================
    # OPERATIONS PILLAR HANDLERS
    # ========================================================================
    
    async def handle_generate_workflow_from_sop_request(
        self,
        session_token: str = None,
        sop_file_uuid: str = None,
        sop_content: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate workflow from SOP."""
        try:
            if not self.operations_orchestrator:
                return {
                    "success": False,
                    "error": "Operations Orchestrator Not Available",
                    "message": "Operations orchestrator is not initialized"
                }
            
            # Delegate to operations orchestrator
            result = await self.operations_orchestrator.generate_workflow_from_sop(
                session_token=session_token,
                sop_file_uuid=sop_file_uuid,
                sop_content=sop_content
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Generate workflow from SOP failed: {e}")
            return {
                "success": False,
                "error": "Internal Server Error",
                "message": str(e)
            }
    
    async def handle_generate_sop_from_workflow_request(
        self,
        session_token: str = None,
        workflow_file_uuid: str = None,
        workflow_content: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate SOP from workflow."""
        try:
            if not self.operations_orchestrator:
                return {
                    "success": False,
                    "error": "Operations Orchestrator Not Available",
                    "message": "Operations orchestrator is not initialized"
                }
            
            # Delegate to operations orchestrator
            result = await self.operations_orchestrator.generate_sop_from_workflow(
                session_token=session_token,
                workflow_file_uuid=workflow_file_uuid,
                workflow_content=workflow_content
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Generate SOP from workflow failed: {e}")
            return {
                "success": False,
                "error": "Internal Server Error",
                "message": str(e)
            }
    
    # ========================================================================
    # BUSINESS OUTCOMES PILLAR HANDLERS
    # ========================================================================
    
    async def handle_generate_strategic_roadmap_request(
        self,
        pillar_outputs: Dict[str, Any] = None,
        roadmap_options: Dict[str, Any] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Generate strategic roadmap from pillar outputs."""
        try:
            if not self.business_outcomes_orchestrator:
                return {
                    "success": False,
                    "error": "Business Outcomes Orchestrator Not Available",
                    "message": "Business outcomes orchestrator is not initialized"
                }
            
            # For MVP: Return a simple roadmap structure
            # In production, this would call the actual orchestrator
            roadmap = {
                "roadmap_id": f"roadmap_{user_id or 'default'}",
                "title": "Strategic Roadmap",
                "pillars_analyzed": list(pillar_outputs.keys()) if pillar_outputs else [],
                "recommendations": [
                    {"priority": "high", "action": "Implement content analysis pipeline"},
                    {"priority": "medium", "action": "Optimize operational workflows"},
                    {"priority": "low", "action": "Enhance data insights"}
                ],
                "timeline": roadmap_options.get("timeline", "12 months") if roadmap_options else "12 months",
                "visualization_type": "summary"
            }
            
            return {
                "success": True,
                "roadmap": roadmap,
                "message": "Strategic roadmap generated successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Generate strategic roadmap failed: {e}")
            return {
                "success": False,
                "error": "Internal Server Error",
                "message": str(e)
            }
    
    async def handle_generate_poc_proposal_request(
        self,
        pillar_outputs: Dict[str, Any] = None,
        proposal_options: Dict[str, Any] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Generate proof-of-concept proposal."""
        try:
            if not self.business_outcomes_orchestrator:
                return {
                    "success": False,
                    "error": "Business Outcomes Orchestrator Not Available",
                    "message": "Business outcomes orchestrator is not initialized"
                }
            
            # For MVP: Return a simple POC proposal
            proposal = {
                "proposal_id": f"poc_{user_id or 'default'}",
                "title": "Proof of Concept Proposal",
                "scope": "MVP implementation",
                "timeline": "3 months",
                "deliverables": ["Working prototype", "Documentation", "Demo"]
            }
            
            return {
                "success": True,
                "proposal": proposal,
                "message": "POC proposal generated successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Generate POC proposal failed: {e}")
            return {
                "success": False,
                "error": "Internal Server Error",
                "message": str(e)
            }
    
    async def handle_get_pillar_summaries_request(
        self,
        session_id: str = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Get summaries from all pillars."""
        try:
            summaries = {
                "content": {"status": "available", "files_processed": 0},
                "insights": {"status": "available", "insights_generated": 0},
                "operations": {"status": "available", "workflows_created": 0}
            }
            
            return {
                "success": True,
                "summaries": summaries,
                "message": "Pillar summaries retrieved successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Get pillar summaries failed: {e}")
            return {
                "success": False,
                "error": "Internal Server Error",
                "message": str(e)
            }
    
    async def handle_get_journey_visualization_request(
        self,
        session_id: str = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Get journey visualization."""
        try:
            visualization = {
                "journey_id": session_id or "default",
                "steps": [],
                "current_step": 0,
                "completion_percentage": 0
            }
            
            return {
                "success": True,
                "visualization": visualization,
                "message": "Journey visualization retrieved successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Get journey visualization failed: {e}")
            return {
                "success": False,
                "error": "Internal Server Error",
                "message": str(e)
            }
    
    async def handle_business_outcomes_health_check_request(self) -> Dict[str, Any]:
        """Health check for business outcomes pillar."""
        return {
            "success": True,
            "status": "healthy" if self.business_outcomes_orchestrator else "unavailable",
            "orchestrator_available": self.business_outcomes_orchestrator is not None
        }
    
    # ========================================================================
    # HEALTH & METADATA
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check (inherited from RealmServiceBase)."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "registered_apis": len(self.registered_apis),
            "orchestrators_available": {
                "content": self.content_orchestrator is not None,
                "insights": self.insights_orchestrator is not None,
                "operations": self.operations_orchestrator is not None,
                "data_operations": self.data_operations_orchestrator is not None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "experience_service",
            "realm": "experience",
            "layer": "ui_gateway",
            "capabilities": ["frontend_api_gateway", "request_routing", "api_transformation"],
            "soa_apis": [
                "expose_frontend_api", "route_frontend_request", "get_frontend_apis",
                "handle_document_analysis_request", "handle_insights_request",
                "handle_operations_request", "handle_data_operations_request",
                "register_api_endpoint", "validate_api_request", "transform_for_frontend"
            ],
            "mcp_tools": [],
            "composes": "business_enablement_orchestrators",
            "supported_types": self.supported_types
        }


