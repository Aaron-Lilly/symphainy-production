#!/usr/bin/env python3
"""
Data Steward MCP Server - Multi-Tenant

MCP server that exposes Data Steward service capabilities as MCP tools
with multi-tenant awareness and proper tenant isolation.

WHAT (Smart City Role): I expose my file storage capabilities via MCP tools with tenant awareness
HOW (MCP Server): I implement the MCP protocol and expose Data Steward operations with tenant context
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../'))

from backend.smart_city.protocols.smart_city_service_base import SmartCityServiceBase
from foundations.di_container.di_container_service import DIContainerService
from foundations.curator_foundation.services import CapabilityRegistryService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from config.environment_loader import EnvironmentLoader
from config import Environment
from utilities import UserContext
from backend.smart_city.protocols.mcp_server_protocol import MCPServerProtocol, MCPTool, MCPServerInfo
from backend.smart_city.interfaces.file_storage_interface import (
    FileUploadRequest, FileUploadResponse, FileDownloadRequest, FileDownloadResponse,
    FileSearchRequest, FileSearchResponse, FileMetadata, StorageTier, FileType
)
from backend.smart_city.services.data_steward.data_steward_service import DataStewardService


class DataStewardMCPServer(SmartCityServiceBase):
    """
    Data Steward MCP Server - Multi-Tenant
    
    Exposes Data Steward service capabilities as MCP tools for external consumption
    with multi-tenant awareness and proper tenant isolation.
    
    WHAT (Smart City Role): I expose my file storage capabilities via MCP tools with tenant awareness
    HOW (MCP Server): I implement the MCP protocol and expose Data Steward operations with tenant context
    """
    
    def __init__(self, data_steward_service: DataStewardService, di_container, 
                 curator_foundation: CapabilityRegistryService = None, public_works_foundation: PublicWorksFoundationService = None):
        """Initialize Data Steward MCP Server with multi-tenant capabilities."""
        super().__init__("DataStewardMCPServer", di_container, public_works_foundation, curator_foundation)
        
        self.data_steward_service = data_steward_service
        self.public_works_foundation = public_works_foundation
        
        # Initialize MCP protocol
        self.mcp_protocol = DataStewardMCPProtocol("DataStewardMCPServer", self, curator_foundation)
        
        # Multi-tenant coordination service
        self.multi_tenant_coordinator = None
        if self.public_works_foundation:
            self.multi_tenant_coordinator = self.public_works_foundation.multi_tenant_coordination_service
        
        # Smart city abstractions from public works
        self.smart_city_abstractions = {}
        
        # MCP tools for multi-tenant operations
        self.mcp_tools = []
        
        self.logger.info("📁 Data Steward MCP Server initialized - Multi-Tenant File Storage Hub")
    
    async def initialize(self):
        """Initialize Data Steward MCP Server with multi-tenant capabilities."""
        try:
            await super().initialize()
            
            self.logger.info("🚀 Initializing Data Steward MCP Server with multi-tenant capabilities...")

            # Initialize MCP protocol
            await self.mcp_protocol.initialize()
            self.logger.info("✅ MCP Protocol initialized")

            # Initialize multi-tenant coordination
            if self.multi_tenant_coordinator:
                await self.multi_tenant_coordinator.initialize()
                self.logger.info("✅ Multi-tenant coordination initialized")
            
            # Load smart city abstractions from public works
            if self.public_works_foundation:
                self.smart_city_abstractions = self.public_works_foundation.get_smart_city_realm_abstractions()
                self.logger.info(f"✅ Loaded {len(self.smart_city_abstractions)} smart city abstractions")

            # Create MCP tools
            self.mcp_tools = self._create_data_steward_tools()
            
            self.logger.info("✅ Data Steward MCP Server initialized with multi-tenant capabilities")
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="data_steward_mcp_initialize")
            raise
        
    def _create_data_steward_tools(self) -> List[MCPTool]:
        """Create Data Steward specific MCP tools."""
        return self._create_standard_tools() + [
            # File Upload Tools
            MCPTool(
                name="upload_file",
                description="Upload a file to storage with metadata",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "Name of the file to upload"},
                        "file_data": {"type": "string", "description": "Base64 encoded file data"},
                        "content_type": {"type": "string", "description": "MIME type of the file"},
                        "storage_tier": {"type": "string", "enum": ["hot", "warm", "cold", "archive"], "description": "Storage tier for the file"},
                        "file_type": {"type": "string", "enum": ["document", "image", "video", "audio", "data", "code", "config", "log"], "description": "Type of file"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for the file"},
                        "description": {"type": "string", "description": "Description of the file"}
                    },
                    "required": ["file_name", "file_data", "content_type"]
                },
                handler=self._handle_upload_file,
                tags=["file", "upload", "storage"]
            ),
            
            # File Download Tools
            MCPTool(
                name="download_file",
                description="Download a file from storage",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the file to download"}
                    },
                    "required": ["file_id"]
                },
                handler=self._handle_download_file,
                tags=["file", "download", "storage"]
            ),
            
            # File Management Tools
            MCPTool(
                name="delete_file",
                description="Delete a file from storage",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the file to delete"}
                    },
                    "required": ["file_id"]
                },
                handler=self._handle_delete_file,
                tags=["file", "delete", "storage"]
            ),
            
            MCPTool(
                name="search_files",
                description="Search for files based on criteria",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "file_type": {"type": "string", "enum": ["document", "image", "video", "audio", "data", "code", "config", "log"], "description": "Filter by file type"},
                        "storage_tier": {"type": "string", "enum": ["hot", "warm", "cold", "archive"], "description": "Filter by storage tier"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
                        "date_from": {"type": "string", "format": "date", "description": "Filter files from this date"},
                        "date_to": {"type": "string", "format": "date", "description": "Filter files to this date"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 1000, "description": "Maximum number of results"},
                        "offset": {"type": "integer", "minimum": 0, "description": "Number of results to skip"}
                    },
                    "required": []
                },
                handler=self._handle_search_files,
                tags=["file", "search", "storage"]
            ),
            
            # Metadata Tools
            MCPTool(
                name="get_file_metadata",
                description="Get metadata for a specific file",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the file"}
                    },
                    "required": ["file_id"]
                },
                handler=self._handle_get_file_metadata,
                tags=["file", "metadata", "storage"]
            ),
            
            MCPTool(
                name="update_file_metadata",
                description="Update metadata for a specific file",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the file"},
                        "metadata": {
                            "type": "object",
                            "properties": {
                                "tags": {"type": "array", "items": {"type": "string"}},
                                "description": {"type": "string"},
                                "storage_tier": {"type": "string", "enum": ["hot", "warm", "cold", "archive"]},
                                "file_type": {"type": "string", "enum": ["document", "image", "video", "audio", "data", "code", "config", "log"]}
                            }
                        }
                    },
                    "required": ["file_id", "metadata"]
                },
                handler=self._handle_update_file_metadata,
                tags=["file", "metadata", "storage"]
            ),
            
            # Service Management Tools
            MCPTool(
                name="get_service_status",
                description="Get the current status of the Data Steward service",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                handler=self._handle_get_service_status,
                tags=["service", "status", "health"]
            ),
            
            MCPTool(
                name="get_storage_stats",
                description="Get storage statistics and usage information",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                handler=self._handle_get_storage_stats,
                tags=["storage", "stats", "analytics"]
            ),
            
            # Multi-Tenant Specific Tools
            MCPTool(
                name="get_tenant_files",
                description="Get all files for a specific tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "description": "ID of the tenant"}
                    },
                    "required": ["tenant_id"]
                },
                handler=self._handle_get_tenant_files,
                tags=["tenant", "files", "multi-tenant"]
            ),
            
            MCPTool(
                name="get_tenant_storage_usage",
                description="Get storage usage metrics for a specific tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "description": "ID of the tenant"}
                    },
                    "required": ["tenant_id"]
                },
                handler=self._handle_get_tenant_storage_usage,
                tags=["tenant", "storage", "usage", "multi-tenant"]
            ),
            
            MCPTool(
                name="get_tenant_data_governance_summary",
                description="Get data governance summary for a specific tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "description": "ID of the tenant"}
                    },
                    "required": ["tenant_id"]
                },
                handler=self._handle_get_tenant_data_governance_summary,
                tags=["tenant", "governance", "multi-tenant"]
            )
        ]
    
    async def initialize(self, user_context: UserContext = None):
        """Initialize the Data Steward MCP Server."""
        try:
            # Ensure the Data Steward service is initialized
            if not hasattr(self.data_steward_service, 'initialized') or not self.data_steward_service.initialized:
                await self.data_steward_service.initialize()
            
            # Register with Curator Foundation if available
            if self.curator_foundation:
                await self.register_with_curator(user_context)
            
            self.logger.info("✅ Data Steward MCP Server initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Data Steward MCP Server: {e}")
            raise
    
    def get_server_info(self) -> MCPServerInfo:
        """Get server information for MCP manifest generation."""
        return MCPServerInfo(
            server_name="data_steward_mcp_server",
            version="1.0.0",
            description="Data Steward MCP Server - File storage, lifecycle management, and metadata governance",
            interface_name="IFileStorage",
            tools=[tool.name for tool in self.tools],
            capabilities=[
                "file_upload",
                "file_download", 
                "file_deletion",
                "file_search",
                "metadata_management",
                "storage_optimization",
                "lifecycle_management"
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
                "role": "data_steward"
            }
            
            return await self.curator_foundation.register_capability(
                self.server_name,
                capability,
                user_context
            )
            
        except Exception as e:
            return {"error": f"Failed to register with Curator: {str(e)}"}
    
    # Tool Handlers
    
    async def _handle_upload_file(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle file upload tool execution."""
        try:
            # Create file upload request
            request = FileUploadRequest(
                file_name=parameters["file_name"],
                file_data=parameters["file_data"].encode() if isinstance(parameters["file_data"], str) else parameters["file_data"],
                content_type=parameters["content_type"],
                storage_tier=StorageTier(parameters.get("storage_tier", "warm")),
                file_type=FileType(parameters.get("file_type", "data")),
                tags=parameters.get("tags", []),
                description=parameters.get("description", "")
            )
            
            # Execute upload
            response = await self.data_steward_service.upload_file(request, user_context)
            
            return self._create_success_response({
                "success": response["success"],
                "file_id": response.get("file_id"),
                "file_name": response.get("file_name"),
                "error": response.get("error")
            })
            
        except Exception as e:
            return self._create_error_response(f"File upload failed: {str(e)}")
    
    async def _handle_download_file(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle file download tool execution."""
        try:
            # Create file download request
            request = FileDownloadRequest(file_id=parameters["file_id"])
            
            # Execute download
            response = await self.data_steward_service.download_file(request, user_context)
            
            return self._create_success_response({
                "success": response["success"],
                "file_data": response.get("file_data"),
                "file_name": response.get("file_name"),
                "content_type": response.get("content_type"),
                "error": response.get("error")
            })
            
        except Exception as e:
            return self._create_error_response(f"File download failed: {str(e)}")
    
    async def _handle_delete_file(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle file deletion tool execution."""
        try:
            # Execute deletion
            success = await self.data_steward_service.delete_file(parameters["file_id"], user_context)
            
            return self._create_success_response({
                "success": success,
                "file_id": parameters["file_id"]
            })
            
        except Exception as e:
            return self._create_error_response(f"File deletion failed: {str(e)}")
    
    async def _handle_search_files(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle file search tool execution."""
        try:
            # Create search request
            request = FileSearchRequest(
                query=parameters.get("query", ""),
                file_type=FileType(parameters["file_type"]) if parameters.get("file_type") else None,
                storage_tier=StorageTier(parameters["storage_tier"]) if parameters.get("storage_tier") else None,
                tags=parameters.get("tags", []),
                date_from=parameters.get("date_from"),
                date_to=parameters.get("date_to"),
                limit=parameters.get("limit", 100),
                offset=parameters.get("offset", 0)
            )
            
            # Execute search
            response = await self.data_steward_service.search_files(request, user_context)
            
            return self._create_success_response({
                "success": response["success"],
                "files": response.get("files", []),
                "total_count": response.get("total_count", 0)
            })
            
        except Exception as e:
            return self._create_error_response(f"File search failed: {str(e)}")
    
    async def _handle_get_file_metadata(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get file metadata tool execution."""
        try:
            # Execute metadata retrieval
            metadata = await self.data_steward_service.get_file_metadata(parameters["file_id"], user_context)
            
            if metadata:
                return self._create_success_response({
                    "success": True,
                    "metadata": {
                        "file_id": metadata.file_id,
                        "file_name": metadata.file_name,
                        "content_type": metadata.content_type,
                        "size": metadata.size,
                        "created_at": metadata.created_at.isoformat() if metadata.created_at else None,
                        "updated_at": metadata.updated_at.isoformat() if metadata.updated_at else None,
                        "storage_tier": metadata.storage_tier.value if metadata.storage_tier else None,
                        "file_type": metadata.file_type.value if metadata.file_type else None,
                        "tags": metadata.tags,
                        "description": metadata.description
                    }
                })
            else:
                return self._create_success_response({
                    "success": False,
                    "error": "File not found"
                })
                
        except Exception as e:
            return self._create_error_response(f"Get file metadata failed: {str(e)}")
    
    async def _handle_update_file_metadata(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle update file metadata tool execution."""
        try:
            # Create metadata object
            metadata_dict = parameters["metadata"]
            metadata = FileMetadata(
                file_id=parameters["file_id"],
                file_name="",  # Will be updated by service
                content_type="",  # Will be updated by service
                size=0,  # Will be updated by service
                created_at=None,  # Will be updated by service
                updated_at=None,  # Will be updated by service
                storage_tier=StorageTier(metadata_dict["storage_tier"]) if metadata_dict.get("storage_tier") else None,
                file_type=FileType(metadata_dict["file_type"]) if metadata_dict.get("file_type") else None,
                tags=metadata_dict.get("tags", []),
                description=metadata_dict.get("description", "")
            )
            
            # Execute metadata update
            success = await self.data_steward_service.update_file_metadata(parameters["file_id"], metadata, user_context)
            
            return self._create_success_response({
                "success": success,
                "file_id": parameters["file_id"]
            })
            
        except Exception as e:
            return self._create_error_response(f"Update file metadata failed: {str(e)}")
    
    async def _handle_get_service_status(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get service status tool execution."""
        try:
            # Get service health
            health = await self.data_steward_service.get_service_health()
            
            return self._create_success_response({
                "service_status": health["status"],
                "environment": health["environment"],
                "architecture": health["architecture"],
                "micro_modules": health.get("micro_modules", {}),
                "environment_info": health.get("environment_info", {})
            })
            
        except Exception as e:
            return self._create_error_response(f"Get service status failed: {str(e)}")
    
    async def _handle_get_storage_stats(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get storage stats tool execution."""
        try:
            # Get storage statistics (this would be implemented in the service)
            # For now, return basic stats
            stats = {
                "total_files": 0,  # Would be calculated from actual storage
                "total_size": 0,   # Would be calculated from actual storage
                "storage_tiers": {
                    "hot": 0,
                    "warm": 0,
                    "cold": 0,
                    "archive": 0
                },
                "file_types": {
                    "document": 0,
                    "image": 0,
                    "video": 0,
                    "audio": 0,
                    "data": 0,
                    "code": 0,
                    "config": 0,
                    "log": 0
                }
            }
            
            return self._create_success_response(stats)
            
        except Exception as e:
            return self._create_error_response(f"Get storage stats failed: {str(e)}")
    
    # ============================================================================
    # MULTI-TENANT TOOL HANDLERS
    # ============================================================================
    
    async def _handle_get_tenant_files(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get tenant files tool execution."""
        try:
            tenant_id = parameters.get("tenant_id")
            if not tenant_id:
                return self._create_error_response("tenant_id is required")
            
            # Convert MCP user context to service user context
            service_user_context = self._convert_mcp_user_context(user_context)
            
            # Call the service method
            result = await self.data_steward_service.get_tenant_files(tenant_id, service_user_context)
            
            if result.get("success"):
                return self._create_success_response({
                    "tenant_id": tenant_id,
                    "files": result.get("files", []),
                    "total_count": len(result.get("files", []))
                })
            else:
                return self._create_error_response(result.get("error", "Failed to get tenant files"))
                
        except Exception as e:
            return self._create_error_response(f"Get tenant files failed: {str(e)}")
    
    async def _handle_get_tenant_storage_usage(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get tenant storage usage tool execution."""
        try:
            tenant_id = parameters.get("tenant_id")
            if not tenant_id:
                return self._create_error_response("tenant_id is required")
            
            # Convert MCP user context to service user context
            service_user_context = self._convert_mcp_user_context(user_context)
            
            # Call the service method
            result = await self.data_steward_service.get_tenant_storage_usage(tenant_id, service_user_context)
            
            if result.get("success"):
                return self._create_success_response(result.get("usage_metrics", {}))
            else:
                return self._create_error_response(result.get("error", "Failed to get tenant storage usage"))
                
        except Exception as e:
            return self._create_error_response(f"Get tenant storage usage failed: {str(e)}")
    
    async def _handle_get_tenant_data_governance_summary(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get tenant data governance summary tool execution."""
        try:
            tenant_id = parameters.get("tenant_id")
            if not tenant_id:
                return self._create_error_response("tenant_id is required")
            
            # Convert MCP user context to service user context
            service_user_context = self._convert_mcp_user_context(user_context)
            
            # Call the service method
            result = await self.data_steward_service.get_tenant_data_governance_summary(tenant_id, service_user_context)
            
            if result.get("success"):
                return self._create_success_response(result.get("governance_summary", {}))
            else:
                return self._create_error_response(result.get("error", "Failed to get tenant data governance summary"))
                
        except Exception as e:
            return self._create_error_response(f"Get tenant data governance summary failed: {str(e)}")
    
    def _convert_mcp_user_context(self, mcp_user_context: UserContext = None) -> Optional[UserContext]:
        """Convert MCP user context to service user context."""
        if not mcp_user_context:
            return None
        
        # MCP user context is already in the correct format
        return mcp_user_context


class DataStewardMCPProtocol(MCPServerProtocol):
    """MCP Protocol implementation for Data Steward MCP Server."""
    
    def __init__(self, server_name: str, server_instance, curator_foundation=None):
        """Initialize Data Steward MCP Protocol."""
        super().__init__(server_name, None, curator_foundation)
        self.server_instance = server_instance
        self.server_info = None
        
    async def initialize(self, user_context: UserContext = None):
        """Initialize the MCP server."""
        # Create server info with multi-tenant metadata
        self.server_info = MCPServerInfo(
            server_name="DataStewardMCPServer",
            version="1.0.0",
            description="Data Steward MCP Server - Multi-tenant data governance and file management tools",
            interface_name="IDataStewardMCP",
            tools=self._create_all_tools(),
            capabilities=["data-governance", "file-management", "multi-tenant", "data-quality"],
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
        """Create all tools for Data Steward MCP Server."""
        tools = []
        
        # Standard tools
        tools.extend(self._create_standard_tools())
        tools.extend(self._create_tenant_aware_tools())
        
        # Data Steward specific tools
        tools.extend([
            MCPTool(
                name="upload_file",
                description="Upload a file with tenant awareness",
                input_schema={
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "File name"},
                        "content_type": {"type": "string", "description": "File content type"},
                        "file_data": {"type": "string", "description": "File data (base64 encoded)"},
                        "metadata": {"type": "object", "description": "File metadata"},
                        "classification": {"type": "string", "description": "File classification"}
                    },
                    "required": ["filename", "content_type", "file_data"]
                },
                handler=self._handle_upload_file,
                tags=["files", "upload"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            MCPTool(
                name="download_file",
                description="Download a file with tenant awareness",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "File ID"}
                    },
                    "required": ["file_id"]
                },
                handler=self._handle_download_file,
                tags=["files", "download"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            MCPTool(
                name="list_files",
                description="List files for the current tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "filter": {"type": "object", "description": "Filter criteria"},
                        "limit": {"type": "integer", "description": "Maximum number of files to return"}
                    }
                },
                handler=self._handle_list_files,
                tags=["files", "management"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            MCPTool(
                name="get_file_metadata",
                description="Get metadata for a specific file",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "File ID"}
                    },
                    "required": ["file_id"]
                },
                handler=self._handle_get_file_metadata,
                tags=["files", "metadata"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            MCPTool(
                name="list_governance_policies",
                description="List data governance policies for the current tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "filter": {"type": "object", "description": "Filter criteria"}
                    }
                },
                handler=self._handle_list_governance_policies,
                tags=["governance", "policies"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            MCPTool(
                name="create_governance_policy",
                description="Create a new data governance policy",
                input_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Policy name"},
                        "description": {"type": "string", "description": "Policy description"},
                        "rules": {"type": "array", "items": {"type": "object"}, "description": "Policy rules"},
                        "classification": {"type": "string", "description": "Policy classification"}
                    },
                    "required": ["name", "description", "rules"]
                },
                handler=self._handle_create_governance_policy,
                tags=["governance", "policies"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            MCPTool(
                name="get_tenant_file_summary",
                description="Get file summary for a specific tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "description": "Tenant ID"}
                    },
                    "required": ["tenant_id"]
                },
                handler=self._handle_get_tenant_file_summary,
                tags=["tenant", "files"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            MCPTool(
                name="get_tenant_governance_summary",
                description="Get data governance summary for a specific tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "description": "Tenant ID"}
                    },
                    "required": ["tenant_id"]
                },
                handler=self._handle_get_tenant_governance_summary,
                tags=["tenant", "governance"],
                requires_tenant=True,
                tenant_scope="tenant"
            )
        ])
        
        return tools
    
    async def _handle_upload_file(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle upload_file tool execution."""
        filename = parameters.get("filename")
        content_type = parameters.get("content_type")
        file_data = parameters.get("file_data")
        metadata = parameters.get("metadata", {})
        classification = parameters.get("classification")
        
        if not all([filename, content_type, file_data]):
            return {"error": "Filename, content type, and file data required"}
        
        result = await self.server_instance.data_steward_service.upload_file(
            filename, content_type, file_data, metadata, classification, user_context
        )
        return result
    
    async def _handle_download_file(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle download_file tool execution."""
        file_id = parameters.get("file_id")
        if not file_id:
            return {"error": "File ID required"}
        
        result = await self.server_instance.data_steward_service.download_file(
            file_id, user_context
        )
        return result
    
    async def _handle_list_files(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle list_files tool execution."""
        filter_criteria = parameters.get("filter", {})
        limit = parameters.get("limit", 100)
        
        result = await self.server_instance.data_steward_service.list_files(
            filter_criteria, limit, user_context
        )
        return result
    
    async def _handle_get_file_metadata(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get_file_metadata tool execution."""
        file_id = parameters.get("file_id")
        if not file_id:
            return {"error": "File ID required"}
        
        result = await self.server_instance.data_steward_service.get_file_metadata(
            file_id, user_context
        )
        return result
    
    async def _handle_list_governance_policies(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle list_governance_policies tool execution."""
        filter_criteria = parameters.get("filter", {})
        
        result = await self.server_instance.data_steward_service.list_governance_policies(
            filter_criteria, user_context
        )
        return result
    
    async def _handle_create_governance_policy(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle create_governance_policy tool execution."""
        name = parameters.get("name")
        description = parameters.get("description")
        rules = parameters.get("rules")
        classification = parameters.get("classification")
        
        if not all([name, description, rules]):
            return {"error": "Name, description, and rules required"}
        
        result = await self.server_instance.data_steward_service.create_governance_policy(
            name, description, rules, classification, user_context
        )
        return result
    
    async def _handle_get_tenant_file_summary(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get_tenant_file_summary tool execution."""
        tenant_id = parameters.get("tenant_id")
        if not tenant_id:
            return {"error": "Tenant ID required"}
        
        result = await self.server_instance.data_steward_service.get_tenant_file_summary(
            tenant_id, user_context
        )
        return result
    
    async def _handle_get_tenant_governance_summary(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get_tenant_governance_summary tool execution."""
        tenant_id = parameters.get("tenant_id")
        if not tenant_id:
            return {"error": "Tenant ID required"}
        
        result = await self.server_instance.data_steward_service.get_tenant_data_governance_summary(
            tenant_id, user_context
        )
        return result
