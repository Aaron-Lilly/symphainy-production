#!/usr/bin/env python3
"""
Librarian MCP Server

MCP server that exposes Librarian service capabilities as MCP tools.
Provides knowledge management, search, metadata extraction, and analytics tools.

WHAT (Smart City Role): I expose my knowledge management capabilities via MCP tools
HOW (MCP Server): I implement the MCP protocol and expose Librarian operations
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../'))

from bases.foundation_service_base import FoundationServiceBase
from foundations.curator_foundation.services import CapabilityRegistryService
from config.environment_loader import EnvironmentLoader
from config import Environment
from utilities import UserContext
from backend.smart_city.protocols.mcp_server_protocol import MCPServerProtocol, MCPTool, MCPServerInfo
from backend.smart_city.interfaces import (
    KnowledgeSearchRequest, KnowledgeSearchResponse, KnowledgeIndexRequest, KnowledgeIndexResponse,
    KnowledgeRecommendationRequest, KnowledgeRecommendationResponse, MetadataExtractionRequest,
    MetadataExtractionResponse, KnowledgeQualityAssessmentRequest, KnowledgeQualityAssessmentResponse,
    SearchMode, KnowledgeType, QualityLevel
)
from backend.smart_city.services.librarian.librarian_service import LibrarianService


class LibrarianMCPServer(MCPServerProtocol):
    """
    Librarian MCP Server
    
    Exposes Librarian service capabilities as MCP tools for external consumption.
    Provides comprehensive knowledge management, search, metadata extraction, and analytics.
    
    WHAT (Smart City Role): I expose my knowledge management capabilities via MCP tools
    HOW (MCP Server): I implement the MCP protocol and expose Librarian operations
    """
    
    def __init__(self, librarian_service: LibrarianService, curator_foundation: CapabilityRegistryService = None):
        """Initialize Librarian MCP Server."""
        super().__init__(
            server_name="librarian_mcp_server",
            interface_class=LibrarianService,  # The service class that implements the interface
            curator_foundation=curator_foundation
        )
        
        self.librarian_service = librarian_service
        
        # Initialize MCP protocol
        self.mcp_protocol = LibrarianMCPProtocol("LibrarianMCPServer", self, curator_foundation)
        
        self.tools = self._create_librarian_tools()
    
    async def initialize(self):
        """Initialize the MCP server."""
        try:
            await super().initialize()
            
            self.logger.info("🚀 Initializing Librarian MCP Server...")
            
            # Initialize MCP protocol
            await self.mcp_protocol.initialize()
            self.logger.info("✅ MCP Protocol initialized")
            
            # Initialize Librarian service
            await self.librarian_service.initialize()
            self.logger.info("✅ Librarian Service initialized")
            
            self.logger.info("✅ Librarian MCP Server initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Librarian MCP Server: {e}")
            raise
        
    def _create_librarian_tools(self) -> List[MCPTool]:
        """Create Librarian specific MCP tools."""
        return self._create_standard_tools() + [
            # Knowledge Search Tools
            MCPTool(
                name="search_knowledge",
                description="Search knowledge assets with advanced capabilities",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "search_mode": {"type": "string", "enum": ["semantic", "exact", "fuzzy"], "description": "Search mode"},
                        "knowledge_type": {"type": "string", "enum": ["document", "image", "video", "audio", "data", "code"], "description": "Filter by knowledge type"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
                        "date_from": {"type": "string", "format": "date", "description": "Filter from date"},
                        "date_to": {"type": "string", "format": "date", "description": "Filter to date"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 1000, "description": "Maximum number of results"}
                    },
                    "required": ["query"]
                },
                handler=self._handle_search_knowledge,
                tags=["knowledge", "search", "discovery"]
            ),
            
            # Knowledge Management Tools
            MCPTool(
                name="index_knowledge",
                description="Index a new knowledge asset",
                input_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Title of the knowledge asset"},
                        "content": {"type": "string", "description": "Content of the knowledge asset"},
                        "knowledge_type": {"type": "string", "enum": ["document", "image", "video", "audio", "data", "code"], "description": "Type of knowledge"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for the knowledge asset"},
                        "content_type": {"type": "string", "description": "MIME type of the content"},
                        "metadata": {"type": "object", "description": "Additional metadata"}
                    },
                    "required": ["title", "content", "knowledge_type"]
                },
                handler=self._handle_index_knowledge,
                tags=["knowledge", "index", "management"]
            ),
            
            MCPTool(
                name="get_knowledge_asset",
                description="Get a knowledge asset by ID",
                input_schema={
                    "type": "object",
                    "properties": {
                        "asset_id": {"type": "string", "description": "ID of the knowledge asset"}
                    },
                    "required": ["asset_id"]
                },
                handler=self._handle_get_knowledge_asset,
                tags=["knowledge", "retrieval", "management"]
            ),
            
            MCPTool(
                name="update_knowledge_asset",
                description="Update a knowledge asset",
                input_schema={
                    "type": "object",
                    "properties": {
                        "asset_id": {"type": "string", "description": "ID of the knowledge asset"},
                        "updates": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "content": {"type": "string"},
                                "tags": {"type": "array", "items": {"type": "string"}},
                                "metadata": {"type": "object"}
                            }
                        }
                    },
                    "required": ["asset_id", "updates"]
                },
                handler=self._handle_update_knowledge_asset,
                tags=["knowledge", "update", "management"]
            ),
            
            MCPTool(
                name="delete_knowledge_asset",
                description="Delete a knowledge asset",
                input_schema={
                    "type": "object",
                    "properties": {
                        "asset_id": {"type": "string", "description": "ID of the knowledge asset"}
                    },
                    "required": ["asset_id"]
                },
                handler=self._handle_delete_knowledge_asset,
                tags=["knowledge", "delete", "management"]
            ),
            
            # Recommendation Tools
            MCPTool(
                name="get_recommendations",
                description="Get knowledge recommendations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "recommendation_type": {"type": "string", "enum": ["content_based", "user_based"], "description": "Type of recommendations"},
                        "asset_id": {"type": "string", "description": "Source asset ID for content-based recommendations"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 100, "description": "Maximum number of recommendations"}
                    },
                    "required": ["recommendation_type"]
                },
                handler=self._handle_get_recommendations,
                tags=["knowledge", "recommendations", "discovery"]
            ),
            
            # Metadata Tools
            MCPTool(
                name="extract_metadata",
                description="Extract metadata from content",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Content to extract metadata from"},
                        "content_type": {"type": "string", "description": "Type of content"},
                        "file_name": {"type": "string", "description": "Name of the file"}
                    },
                    "required": ["content", "content_type"]
                },
                handler=self._handle_extract_metadata,
                tags=["metadata", "extraction", "analysis"]
            ),
            
            MCPTool(
                name="assess_quality",
                description="Assess the quality of knowledge content",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Content to assess"},
                        "title": {"type": "string", "description": "Title of the content"},
                        "metadata": {"type": "object", "description": "Metadata of the content"}
                    },
                    "required": ["content"]
                },
                handler=self._handle_assess_quality,
                tags=["quality", "assessment", "analysis"]
            ),
            
            # Analytics Tools
            MCPTool(
                name="get_analytics",
                description="Get knowledge management analytics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "time_period": {"type": "string", "enum": ["7d", "30d", "90d"], "description": "Time period for analytics"},
                        "user_id": {"type": "string", "description": "User ID for user-specific analytics"}
                    },
                    "required": []
                },
                handler=self._handle_get_analytics,
                tags=["analytics", "metrics", "insights"]
            ),
            
            # Service Management Tools
            MCPTool(
                name="get_service_status",
                description="Get the current status of the Librarian service",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                handler=self._handle_get_service_status,
                tags=["service", "status", "health"]
            ),
            
            MCPTool(
                name="get_search_suggestions",
                description="Get search suggestions based on partial query",
                input_schema={
                    "type": "object",
                    "properties": {
                        "partial_query": {"type": "string", "description": "Partial search query"}
                    },
                    "required": ["partial_query"]
                },
                handler=self._handle_get_search_suggestions,
                tags=["search", "suggestions", "discovery"]
            )
        ]
    
    async def initialize(self, user_context: UserContext = None):
        """Initialize the Librarian MCP Server."""
        try:
            # Ensure the Librarian service is initialized
            if not hasattr(self.librarian_service, 'initialized') or not self.librarian_service.initialized:
                await self.librarian_service.initialize()
            
            # Register with Curator Foundation if available
            if self.curator_foundation:
                await self.register_with_curator(user_context)
            
            self.logger.info("✅ Librarian MCP Server initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Librarian MCP Server: {e}")
            raise
    
    def get_server_info(self) -> MCPServerInfo:
        """Get server information for MCP manifest generation."""
        return MCPServerInfo(
            server_name="librarian_mcp_server",
            version="1.0.0",
            description="Librarian MCP Server - Knowledge management, search, metadata extraction, and analytics",
            interface_name="IKnowledgeManagement",
            tools=[tool.name for tool in self.tools],
            capabilities=[
                "knowledge_search",
                "knowledge_indexing",
                "metadata_extraction",
                "quality_assessment",
                "recommendations",
                "analytics",
                "content_discovery"
            ]
        )
    
    def get_tools(self) -> List[MCPTool]:
        """Get all available MCP tools."""
        return self.tools
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Execute an MCP tool with given parameters."""
        try:
            # Find the tool
            tool = next((t for t in self.tools if t.name == tool_name), None)
            if not tool:
                return self._create_error_response(f"Tool '{tool_name}' not found")
            
            # Execute the tool
            return await tool.handler(parameters, user_context)
            
        except Exception as e:
            return self._create_error_response(f"Tool execution failed: {str(e)}")
    
    async def register_with_curator(self, user_context: UserContext = None) -> Dict[str, Any]:
        """Register this server with Curator Foundation Service."""
        if not self.curator_foundation:
            return {"error": "Curator Foundation Service not available"}
        
        try:
            server_info = self.get_server_info()
            
            capability = {
                "interface": server_info.interface_name,
                "endpoints": [],  # MCP servers don't have HTTP endpoints
                "tools": server_info.tools,
                "description": server_info.description,
                "realm": "smart_city",
                "role": "librarian"
            }
            
            return await self.curator_foundation.register_capability(
                self.server_name,
                capability,
                user_context
            )
            
        except Exception as e:
            return {"error": f"Failed to register with Curator: {str(e)}"}
    
    # Tool Handlers
    
    async def _handle_search_knowledge(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle knowledge search tool execution."""
        try:
            # Create search request
            request = KnowledgeSearchRequest(
                query=parameters["query"],
                search_mode=SearchMode(parameters.get("search_mode", "semantic")),
                knowledge_type=KnowledgeType(parameters["knowledge_type"]) if parameters.get("knowledge_type") else None,
                tags=parameters.get("tags", []),
                date_from=parameters.get("date_from"),
                date_to=parameters.get("date_to"),
                limit=parameters.get("limit", 100)
            )
            
            # Execute search
            response = await self.librarian_service.search_knowledge(request, user_context)
            
            return self._create_success_response({
                "success": response["success"],
                "results": response.get("results", []),
                "total_count": response.get("total_count", 0),
                "search_mode": response.get("search_mode", "semantic"),
                "query": response.get("query", parameters["query"])
            })
            
        except Exception as e:
            return self._create_error_response(f"Knowledge search failed: {str(e)}")
    
    async def _handle_index_knowledge(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle knowledge indexing tool execution."""
        try:
            # Create index request
            request = KnowledgeIndexRequest(
                title=parameters["title"],
                content=parameters["content"],
                knowledge_type=KnowledgeType(parameters["knowledge_type"]),
                tags=parameters.get("tags", []),
                content_type=parameters.get("content_type", "text/plain"),
                metadata=parameters.get("metadata", {})
            )
            
            # Execute indexing
            response = await self.librarian_service.index_knowledge(request, user_context)
            
            return self._create_success_response({
                "success": response["success"],
                "asset_id": response.get("asset_id"),
                "indexed_at": response.get("indexed_at"),
                "metadata": response.get("metadata", {})
            })
            
        except Exception as e:
            return self._create_error_response(f"Knowledge indexing failed: {str(e)}")
    
    async def _handle_get_knowledge_asset(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get knowledge asset tool execution."""
        try:
            # Execute retrieval
            asset = await self.librarian_service.get_knowledge_asset(parameters["asset_id"], user_context)
            
            if asset:
                return self._create_success_response({
                    "success": True,
                    "asset": asset
                })
            else:
                return self._create_success_response({
                    "success": False,
                    "error": "Asset not found"
                })
                
        except Exception as e:
            return self._create_error_response(f"Get knowledge asset failed: {str(e)}")
    
    async def _handle_update_knowledge_asset(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle update knowledge asset tool execution."""
        try:
            # Execute update
            success = await self.librarian_service.update_knowledge_asset(
                parameters["asset_id"], 
                parameters["updates"], 
                user_context
            )
            
            return self._create_success_response({
                "success": success,
                "asset_id": parameters["asset_id"]
            })
            
        except Exception as e:
            return self._create_error_response(f"Update knowledge asset failed: {str(e)}")
    
    async def _handle_delete_knowledge_asset(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle delete knowledge asset tool execution."""
        try:
            # Execute deletion
            success = await self.librarian_service.delete_knowledge_asset(parameters["asset_id"], user_context)
            
            return self._create_success_response({
                "success": success,
                "asset_id": parameters["asset_id"]
            })
            
        except Exception as e:
            return self._create_error_response(f"Delete knowledge asset failed: {str(e)}")
    
    async def _handle_get_recommendations(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get recommendations tool execution."""
        try:
            # Create recommendation request
            request = KnowledgeRecommendationRequest(
                recommendation_type=parameters["recommendation_type"],
                asset_id=parameters.get("asset_id"),
                limit=parameters.get("limit", 10)
            )
            
            # Execute recommendations
            response = await self.librarian_service.get_recommendations(request, user_context)
            
            return self._create_success_response({
                "success": response["success"],
                "recommendations": response.get("recommendations", []),
                "total_count": response.get("total_count", 0),
                "recommendation_type": response.get("recommendation_type", parameters["recommendation_type"])
            })
            
        except Exception as e:
            return self._create_error_response(f"Get recommendations failed: {str(e)}")
    
    async def _handle_extract_metadata(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle extract metadata tool execution."""
        try:
            # Create metadata extraction request
            request = MetadataExtractionRequest(
                content=parameters["content"],
                content_type=parameters["content_type"],
                file_name=parameters.get("file_name", "")
            )
            
            # Execute metadata extraction
            response = await self.librarian_service.extract_metadata(request, user_context)
            
            return self._create_success_response({
                "success": response["success"],
                "metadata": response.get("metadata", {}),
                "error": response.get("error")
            })
            
        except Exception as e:
            return self._create_error_response(f"Metadata extraction failed: {str(e)}")
    
    async def _handle_assess_quality(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle assess quality tool execution."""
        try:
            # Create quality assessment request
            request = KnowledgeQualityAssessmentRequest(
                content=parameters["content"],
                title=parameters.get("title", ""),
                metadata=parameters.get("metadata", {})
            )
            
            # Execute quality assessment
            response = await self.librarian_service.assess_quality(request, user_context)
            
            return self._create_success_response({
                "success": response["success"],
                "quality_score": response.get("quality_score", 0.0),
                "quality_level": response.get("quality_level", "unknown"),
                "quality_factors": response.get("quality_factors", []),
                "recommendations": response.get("recommendations", [])
            })
            
        except Exception as e:
            return self._create_error_response(f"Quality assessment failed: {str(e)}")
    
    async def _handle_get_analytics(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get analytics tool execution."""
        try:
            # Get analytics from the service
            time_period = parameters.get("time_period", "30d")
            user_id = parameters.get("user_id")
            
            if user_id:
                result = await self.librarian_service.knowledge_analytics.get_user_analytics(user_id, time_period)
            else:
                result = await self.librarian_service.knowledge_analytics.get_asset_analytics(time_period)
            
            return self._create_success_response({
                "success": result["success"],
                "analytics": result.get("analytics", {}),
                "time_period": time_period
            })
            
        except Exception as e:
            return self._create_error_response(f"Get analytics failed: {str(e)}")
    
    async def _handle_get_service_status(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get service status tool execution."""
        try:
            # Get service health
            health = await self.librarian_service.get_service_health()
            
            return self._create_success_response({
                "service_status": health["status"],
                "environment": health["environment"],
                "architecture": health["architecture"],
                "micro_modules": health.get("micro_modules", {}),
                "environment_info": health.get("environment_info", {})
            })
            
        except Exception as e:
            return self._create_error_response(f"Get service status failed: {str(e)}")
    
    async def _handle_get_search_suggestions(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get search suggestions tool execution."""
        try:
            # Get search suggestions
            suggestions = await self.librarian_service.search_engine.get_search_suggestions(
                parameters["partial_query"],
                user_context.to_dict() if user_context else None
            )
            
            return self._create_success_response({
                "suggestions": suggestions,
                "partial_query": parameters["partial_query"]
            })
            
        except Exception as e:
            return self._create_error_response(f"Get search suggestions failed: {str(e)}")


class LibrarianMCPProtocol(MCPServerProtocol):
    """MCP Protocol implementation for Librarian MCP Server."""
    
    def __init__(self, server_name: str, server_instance, curator_foundation=None):
        """Initialize Librarian MCP Protocol."""
        super().__init__(server_name, None, curator_foundation)
        self.server_instance = server_instance
        self.server_info = None
        
    async def initialize(self, user_context: UserContext = None):
        """Initialize the MCP server."""
        # Create server info with multi-tenant metadata
        self.server_info = MCPServerInfo(
            server_name="LibrarianMCPServer",
            version="1.0.0",
            description="Librarian MCP Server - Multi-tenant knowledge management and search tools",
            interface_name="ILibrarianMCP",
            tools=self._create_all_tools(),
            capabilities=["knowledge-management", "search", "multi-tenant", "content-discovery"],
            multi_tenant_enabled=True,
            tenant_isolation_level="strict"
        )
    
    def get_server_info(self) -> MCPServerInfo:
        """Get server information for MCP manifest generation."""
        return self.server_info
    
    def get_tools(self) -> List[MCPTool]:
        """Get all available MCP tools."""
        return self.server_info.tools
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Execute an MCP tool with given parameters."""
        # Find the tool
        tool = None
        for t in self.server_info.tools:
            if t.name == tool_name:
                tool = t
                break
        
        if not tool:
            return self._create_error_response(f"Tool '{tool_name}' not found", "TOOL_NOT_FOUND")
        
        # Validate tenant context if required
        if tool.requires_tenant:
            validation = self._validate_tenant_context(user_context, tool)
            if not validation["valid"]:
                return self._create_error_response(validation["error"], "TENANT_CONTEXT_REQUIRED")
        
        try:
            # Execute the tool handler
            result = await tool.handler(parameters, user_context)
            return self._create_success_response(result)
        except Exception as e:
            return self._create_error_response(str(e), "TOOL_EXECUTION_ERROR")
    
    async def register_with_curator(self, user_context: UserContext = None) -> Dict[str, Any]:
        """Register this server with Curator Foundation Service."""
        if self.curator_foundation:
            capability = {
                "interface": self.server_info.interface_name,
                "endpoints": [],  # MCP servers don't have HTTP endpoints
                "tools": [tool.name for tool in self.server_info.tools],
                "description": self.server_info.description,
                "realm": "smart_city",
                "multi_tenant_enabled": self.server_info.multi_tenant_enabled,
                "tenant_isolation_level": self.server_info.tenant_isolation_level
            }
            
            return await self.curator_foundation.register_capability(
                self.server_name,
                capability,
                user_context
            )
        else:
            return {"error": "Curator Foundation Service not available"}
    
    def _create_all_tools(self) -> List[MCPTool]:
        """Create all tools for Librarian MCP Server."""
        tools = []
        
        # Standard tools
        tools.extend(self._create_standard_tools())
        tools.extend(self._create_tenant_aware_tools())
        
        # Librarian specific tools
        tools.extend([
            MCPTool(
                name="create_knowledge_item",
                description="Create a new knowledge item with tenant awareness",
                input_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Knowledge item title"},
                        "content": {"type": "string", "description": "Knowledge item content"},
                        "type": {"type": "string", "description": "Knowledge item type"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Knowledge item tags"},
                        "metadata": {"type": "object", "description": "Additional metadata"}
                    },
                    "required": ["title", "content", "type"]
                },
                handler=self._handle_create_knowledge_item,
                tags=["knowledge", "management"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            MCPTool(
                name="search_knowledge",
                description="Search knowledge items with tenant awareness",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "filters": {"type": "object", "description": "Search filters"},
                        "limit": {"type": "integer", "description": "Maximum results"},
                        "offset": {"type": "integer", "description": "Result offset"}
                    },
                    "required": ["query"]
                },
                handler=self._handle_search_knowledge,
                tags=["search", "knowledge"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            MCPTool(
                name="get_knowledge_item",
                description="Get a specific knowledge item",
                input_schema={
                    "type": "object",
                    "properties": {
                        "knowledge_id": {"type": "string", "description": "Knowledge item ID"}
                    },
                    "required": ["knowledge_id"]
                },
                handler=self._handle_get_knowledge_item,
                tags=["knowledge", "retrieval"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            MCPTool(
                name="list_knowledge_items",
                description="List knowledge items for the current tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "filter": {"type": "object", "description": "Filter criteria"},
                        "limit": {"type": "integer", "description": "Maximum results"}
                    }
                },
                handler=self._handle_list_knowledge_items,
                tags=["knowledge", "management"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            MCPTool(
                name="update_knowledge_item",
                description="Update a knowledge item",
                input_schema={
                    "type": "object",
                    "properties": {
                        "knowledge_id": {"type": "string", "description": "Knowledge item ID"},
                        "title": {"type": "string", "description": "Updated title"},
                        "content": {"type": "string", "description": "Updated content"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Updated tags"},
                        "metadata": {"type": "object", "description": "Updated metadata"}
                    },
                    "required": ["knowledge_id"]
                },
                handler=self._handle_update_knowledge_item,
                tags=["knowledge", "management"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            MCPTool(
                name="get_tenant_knowledge_summary",
                description="Get knowledge summary for a specific tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "description": "Tenant ID"}
                    },
                    "required": ["tenant_id"]
                },
                handler=self._handle_get_tenant_knowledge_summary,
                tags=["tenant", "knowledge"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            MCPTool(
                name="get_tenant_search_analytics",
                description="Get search analytics for a specific tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "description": "Tenant ID"}
                    },
                    "required": ["tenant_id"]
                },
                handler=self._handle_get_tenant_search_analytics,
                tags=["tenant", "analytics"],
                requires_tenant=True,
                tenant_scope="tenant"
            )
        ])
        
        return tools
    
    async def _handle_create_knowledge_item(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle create_knowledge_item tool execution."""
        title = parameters.get("title")
        content = parameters.get("content")
        item_type = parameters.get("type")
        tags = parameters.get("tags", [])
        metadata = parameters.get("metadata", {})
        
        if not all([title, content, item_type]):
            return {"error": "Title, content, and type required"}
        
        result = await self.server_instance.librarian_service.create_knowledge_item(
            title, content, item_type, tags, metadata, user_context
        )
        return result
    
    async def _handle_search_knowledge(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle search_knowledge tool execution."""
        query = parameters.get("query")
        filters = parameters.get("filters", {})
        limit = parameters.get("limit", 10)
        offset = parameters.get("offset", 0)
        
        if not query:
            return {"error": "Query required"}
        
        result = await self.server_instance.librarian_service.search_knowledge(
            query, filters, limit, offset, user_context
        )
        return result
    
    async def _handle_get_knowledge_item(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get_knowledge_item tool execution."""
        knowledge_id = parameters.get("knowledge_id")
        if not knowledge_id:
            return {"error": "Knowledge ID required"}
        
        result = await self.server_instance.librarian_service.get_knowledge_item(
            knowledge_id, user_context
        )
        return result
    
    async def _handle_list_knowledge_items(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle list_knowledge_items tool execution."""
        filter_criteria = parameters.get("filter", {})
        limit = parameters.get("limit", 100)
        
        result = await self.server_instance.librarian_service.list_knowledge_items(
            filter_criteria, limit, user_context
        )
        return result
    
    async def _handle_update_knowledge_item(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle update_knowledge_item tool execution."""
        knowledge_id = parameters.get("knowledge_id")
        title = parameters.get("title")
        content = parameters.get("content")
        tags = parameters.get("tags", [])
        metadata = parameters.get("metadata", {})
        
        if not knowledge_id:
            return {"error": "Knowledge ID required"}
        
        result = await self.server_instance.librarian_service.update_knowledge_item(
            knowledge_id, title, content, tags, metadata, user_context
        )
        return result
    
    async def _handle_get_tenant_knowledge_summary(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get_tenant_knowledge_summary tool execution."""
        tenant_id = parameters.get("tenant_id")
        if not tenant_id:
            return {"error": "Tenant ID required"}
        
        result = await self.server_instance.librarian_service.get_tenant_knowledge_summary(
            tenant_id, user_context
        )
        return result
    
    async def _handle_get_tenant_search_analytics(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get_tenant_search_analytics tool execution."""
        tenant_id = parameters.get("tenant_id")
        if not tenant_id:
            return {"error": "Tenant ID required"}
        
        result = await self.server_instance.librarian_service.get_tenant_search_analytics(
            tenant_id, user_context
        )
        return result
