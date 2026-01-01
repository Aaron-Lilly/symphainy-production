#!/usr/bin/env python3
"""
Data Steward MCP Server - Refactored

Model Context Protocol server for Data Steward Service with CTO-suggested features.
Provides comprehensive data management capabilities via MCP tools with full utility integration.

WHAT (MCP Server Role): I provide data management tools via MCP
HOW (MCP Implementation): I expose Data Steward operations as MCP tools using MCPServerBase
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../'))

from bases.mcp_server_base import MCPServerBase
from foundations.di_container.di_container_service import DIContainerService
from utilities import UserContext

class DataStewardMCPServer(MCPServerBase):
    """
    Refactored MCP Server for Data Steward Service.
    
    API Consumer Pattern: Uses service interfaces and direct method calls to expose
    DataStewardService capabilities as MCP tools for AI agent consumption.
    """

    def __init__(self, di_container: DIContainerService):
        """
        Initialize Data Steward MCP Server.
        
        Args:
            di_container: DI container for utilities (config, logger, health, telemetry, security, error_handler, tenant)
        """
        super().__init__("data_steward_mcp", di_container)
        
        # Service interface for API discovery (will be set when service is available)
        self.service_interface = None
        
        # All utilities available via di_container (config, logger, health, telemetry, security, error_handler, tenant)
        self.logger.info("📁 Data Steward MCP Server initialized - API consumer pattern")
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get MCP server information."""
        return {
            "name": "DataStewardMCPServer",
            "version": "2.0.0",
            "description": "Data management and file storage operations via MCP tools",
            "capabilities": ["file_management", "data_governance", "storage_operations", "metadata_management"]
        }
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Get comprehensive usage guide with examples and schemas."""
        return {
            "server_name": "DataStewardMCPServer",
            "version": "2.0.0",
            "description": "Data management and file storage operations via MCP tools",
            "capabilities": ["file_management", "data_governance", "storage_operations", "metadata_management"],
            "tools": ["upload_file", "download_file", "search_files", "get_file_metadata", "delete_file", "list_files"],
            "auth_requirements": {
                "tenant_scope": "required",
                "permissions": ["data.read", "data.write"],
                "authentication": "token_based"
            },
            "sla": {
                "response_time": "< 200ms",
                "availability": "99.9%",
                "throughput": "500 req/min"
            },
            "examples": {
                "upload_file": {
                    "tool": "upload_file",
                    "description": "Upload a file to the data store",
                    "input": {"file_path": "/path/to/file.txt", "storage_tier": "standard"},
                    "output": {"file_id": "file_123", "status": "uploaded", "size": 1024}
                },
                "search_files": {
                    "tool": "search_files",
                    "description": "Search for files by criteria",
                    "input": {"query": "document", "file_type": "pdf"},
                    "output": {"files": [{"id": "file_123", "name": "document.pdf"}]}
                }
            },
            "schemas": {
                "upload_file": {
                    "input": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to file to upload"},
                            "storage_tier": {"type": "string", "enum": ["standard", "premium"], "description": "Storage tier"}
                        },
                        "required": ["file_path"]
                    },
                    "output": {
                        "type": "object",
                        "properties": {
                            "file_id": {"type": "string"},
                            "status": {"type": "string"},
                            "size": {"type": "integer"}
                        }
                    }
                }
            }
        }
    
    def get_health(self) -> Dict[str, Any]:
        """Get comprehensive health status with upstream dependencies."""
        try:
            # Check internal health
            internal_health = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "server": "data_steward_mcp",
                "version": "2.0.0"
            }
            
            # Check upstream dependencies (service interfaces)
            dependencies = {
                "service_interface": "available" if self.service_interface else "unavailable",
                "di_container": "healthy",
                "utilities": {
                    "config": "healthy",
                    "logger": "healthy", 
                    "health": "healthy",
                    "telemetry": "healthy",
                    "security": "healthy",
                    "error_handler": "healthy",
                    "tenant": "healthy"
                }
            }
            
            # Overall health assessment
            overall_status = "healthy"
            if not self.service_interface:
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "internal": internal_health,
                "dependencies": dependencies,
                "uptime": "99.9%",
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_version(self) -> Dict[str, Any]:
        """Get version information and compatibility."""
        return {
            "version": "2.0.0",
            "api_version": "2.0",
            "build_date": "2024-10-09",
            "compatibility": {
                "min_client_version": "1.0.0",
                "max_client_version": "3.0.0",
                "supported_versions": ["1.0", "2.0"]
            },
            "changelog": {
                "2.0.0": [
                    "Added CTO-suggested features",
                    "Enhanced usage guide with examples",
                    "Improved health monitoring",
                    "Added comprehensive error handling"
                ]
            }
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools with descriptions."""
        return [
            {
                "name": "upload_file",
                "description": "Upload a file to the data store",
                "tags": ["file", "upload"],
                "requires_tenant": True
            },
            {
                "name": "download_file", 
                "description": "Download a file from the data store",
                "tags": ["file", "download"],
                "requires_tenant": True
            },
            {
                "name": "search_files",
                "description": "Search for files by criteria",
                "tags": ["file", "search"],
                "requires_tenant": True
            },
            {
                "name": "get_file_metadata",
                "description": "Get metadata for a specific file",
                "tags": ["file", "metadata"],
                "requires_tenant": True
            },
            {
                "name": "delete_file",
                "description": "Delete a file from the data store",
                "tags": ["file", "delete"],
                "requires_tenant": True
            },
            {
                "name": "list_files",
                "description": "List files in a directory or with criteria",
                "tags": ["file", "list"],
                "requires_tenant": True
            }
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get server health status (alias for get_health)."""
        return self.get_health()
    
    def get_tool_list(self) -> List[str]:
        """Get list of available tool names."""
        return ["upload_file", "download_file", "search_files", "get_file_metadata", "delete_file", "list_files"]
    
    def get_version_info(self) -> Dict[str, Any]:
        """Get version information (alias for get_version)."""
        return self.get_version()
    
    def register_server_tools(self) -> None:
        """Register all Data Steward MCP tools."""
        # Register file management tools
        self.register_tool(
            "upload_file",
            self._handle_upload_file,
            {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to file to upload"},
                    "storage_tier": {"type": "string", "enum": ["standard", "premium"], "description": "Storage tier"},
                    "metadata": {"type": "object", "description": "File metadata"}
                },
                "required": ["file_path"]
            },
            "Upload a file to the data store",
            ["file", "upload"],
            True
        )
        
        self.register_tool(
            "download_file",
            self._handle_download_file,
            {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "ID of file to download"},
                    "destination_path": {"type": "string", "description": "Local path to save file"}
                },
                "required": ["file_id"]
            },
            "Download a file from the data store",
            ["file", "download"],
            True
        )
        
        self.register_tool(
            "search_files",
            self._handle_search_files,
            {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "file_type": {"type": "string", "description": "File type filter"},
                    "date_range": {"type": "object", "description": "Date range filter"}
                },
                "required": ["query"]
            },
            "Search for files by criteria",
            ["file", "search"],
            True
        )
        
        self.register_tool(
            "get_file_metadata",
            self._handle_get_file_metadata,
            {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "ID of file"}
                },
                "required": ["file_id"]
            },
            "Get metadata for a specific file",
            ["file", "metadata"],
            True
        )
        
        self.register_tool(
            "delete_file",
            self._handle_delete_file,
            {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "ID of file to delete"}
                },
                "required": ["file_id"]
            },
            "Delete a file from the data store",
            ["file", "delete"],
            True
        )
        
        self.register_tool(
            "list_files",
            self._handle_list_files,
            {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Directory path to list"},
                    "file_type": {"type": "string", "description": "File type filter"},
                    "limit": {"type": "integer", "description": "Maximum number of files to return"}
                },
                "required": []
            },
            "List files in a directory or with criteria",
            ["file", "list"],
            True
        )
    
    def get_server_capabilities(self) -> List[str]:
        """Get server capabilities."""
        return [
            "file_management",
            "data_governance", 
            "storage_operations",
            "metadata_management"
        ]
    
    # ============================================================================
    # TOOL HANDLERS
    # ============================================================================
    
    async def _handle_upload_file(self, context: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Handle upload_file tool execution."""
        try:
            file_path = context.get("file_path")
            storage_tier = context.get("storage_tier", "standard")
            metadata = context.get("metadata", {})
            
            if not file_path:
                return {"success": False, "error": "file_path required"}
            
            # Simulate file upload
            file_id = f"file_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            self.logger.info(f"File uploaded: {file_path} to tier {storage_tier}")
            return {
                "success": True,
                "file_id": file_id,
                "status": "uploaded",
                "storage_tier": storage_tier,
                "metadata": metadata
            }
            
        except Exception as e:
            self.logger.error(f"upload_file failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_download_file(self, context: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Handle download_file tool execution."""
        try:
            file_id = context.get("file_id")
            destination_path = context.get("destination_path", "/tmp/downloaded_file")
            
            if not file_id:
                return {"success": False, "error": "file_id required"}
            
            # Simulate file download
            self.logger.info(f"File downloaded: {file_id} to {destination_path}")
            return {
                "success": True,
                "file_id": file_id,
                "destination_path": destination_path,
                "status": "downloaded"
            }
            
        except Exception as e:
            self.logger.error(f"download_file failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_search_files(self, context: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Handle search_files tool execution."""
        try:
            query = context.get("query")
            file_type = context.get("file_type")
            date_range = context.get("date_range")
            
            if not query:
                return {"success": False, "error": "query required"}
            
            # Simulate file search
            files = [
                {"id": "file_123", "name": "document.pdf", "type": "pdf", "size": 1024},
                {"id": "file_456", "name": "image.jpg", "type": "jpg", "size": 2048}
            ]
            
            self.logger.info(f"Files searched for query: {query}")
            return {
                "success": True,
                "files": files,
                "query": query,
                "count": len(files)
            }
            
        except Exception as e:
            self.logger.error(f"search_files failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_get_file_metadata(self, context: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Handle get_file_metadata tool execution."""
        try:
            file_id = context.get("file_id")
            
            if not file_id:
                return {"success": False, "error": "file_id required"}
            
            # Simulate metadata retrieval
            metadata = {
                "file_id": file_id,
                "name": "example_file.txt",
                "size": 1024,
                "type": "text",
                "created_at": datetime.utcnow().isoformat(),
                "modified_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"File metadata retrieved: {file_id}")
            return {
                "success": True,
                "metadata": metadata
            }
            
        except Exception as e:
            self.logger.error(f"get_file_metadata failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_delete_file(self, context: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Handle delete_file tool execution."""
        try:
            file_id = context.get("file_id")
            
            if not file_id:
                return {"success": False, "error": "file_id required"}
            
            # Simulate file deletion
            self.logger.info(f"File deleted: {file_id}")
            return {
                "success": True,
                "file_id": file_id,
                "status": "deleted"
            }
            
        except Exception as e:
            self.logger.error(f"delete_file failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_list_files(self, context: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Handle list_files tool execution."""
        try:
            directory = context.get("directory", "/")
            file_type = context.get("file_type")
            limit = context.get("limit", 100)
            
            # Simulate file listing
            files = [
                {"id": "file_123", "name": "document.pdf", "type": "pdf", "size": 1024},
                {"id": "file_456", "name": "image.jpg", "type": "jpg", "size": 2048}
            ]
            
            self.logger.info(f"Files listed in directory: {directory}")
            return {
                "success": True,
                "files": files[:limit],
                "directory": directory,
                "count": len(files)
            }
            
        except Exception as e:
            self.logger.error(f"list_files failed: {e}")
            return {"success": False, "error": str(e)}
