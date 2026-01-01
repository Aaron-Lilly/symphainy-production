#!/usr/bin/env python3
"""
File Broker MCP Server - Core Data Infrastructure

This MCP server abstracts raw file storage operations, combining functionality from:
- file_server: Basic file operations
- platform_server: Platform file management

Provides a unified interface for file storage across the Smart City platform.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid
import hashlib

# Add the shared pattern reporting module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
from pattern_reporting import Core4PatternReporter

# Add Core 4 utility integration
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'common', 'utilities'))
from core4_utility_integration import create_core4_utility_integration
from domain_bases import Core4MCPBase

class FileBrokerMCPServer(Core4MCPBase):
    """
    File Broker MCP Server - abstracts raw file storage operations
    
    This server provides a unified interface for file storage across the Smart City platform,
    combining basic file operations with platform-specific file management.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the File Broker MCP Server."""
        # Initialize base class with service name and domain
        super().__init__("file_broker", "core4")
        
        # Keep existing initialization
        self.config = config or {}
        
        # Initialize Core 4 utility integration
        self.utils = create_core4_utility_integration("file_broker")
        self.logger = self.utils.logger
        
        # Server metadata
        self.name = "file_broker"
        self.version = "1.0.0"
        self.status = "active"
        
        # File storage configuration
        self.storage_backends = self.config.get("storage_backends", ["local", "gcs"])
        self.default_backend = self.config.get("default_backend", "local")
        self.root_path = Path(self.config.get("root_path", "./data/files"))
        
        # Platform-specific roots (from platform_server)
        self.platform_roots = [
            "./backend/smart_cities",  # Smart City code
            "./backend/integrations",  # Integration code
            "./backend/utilities",     # Utility code
            "./data/platform",         # Platform data
            "./data/business",         # Business data
            "./logs"                   # Log files
        ]
        
        # File registry for tracking files
        self.file_registry = {}
        
        # Initialize storage
        self._initialize_storage()
        
        # Initialize pattern reporter
        self.pattern_reporter = Core4PatternReporter("file_broker")
        
        # Define MCP tools
        self.tools = [
            "upload_file",
            "download_file", 
            "delete_file",
            "list_files",
            "get_file_metadata",
            "search_files",
            "get_file_info",
            "list_directory",
            "create_directory",
            "get_storage_stats",
            "report_core4_patterns",
            "get_core4_patterns",
            "health_check",
            "log_telemetry",
            "log_health_metrics",
            "log_anomaly"
        ]
        
        # Define MCP resources
        self.resources = [
            "/files/registry.json",
            "/files/storage_stats.json",
            "/files/platform_files.json"
        ]
        
        # Define MCP prompts
        self.prompts = [
            "How to store and retrieve files",
            "File storage best practices",
            "Platform file management patterns"
        ]
        
        self.logger.info(f"File Broker MCP Server initialized with root: {self.root_path}")
        
        # Set status to running
        from common.utilities.health import ServiceStatus
        self.utils.set_status(ServiceStatus.RUNNING)
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available File Broker tools."""
        return [
            {
                "name": "upload_file",
                "description": "Upload a file to the file storage system",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to the file to upload"},
                        "destination": {"type": "string", "description": "Destination path in storage"},
                        "metadata": {"type": "object", "description": "File metadata"}
                    },
                    "required": ["file_path", "destination"]
                }
            },
            {
                "name": "download_file",
                "description": "Download a file from the file storage system",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the file to download"},
                        "destination": {"type": "string", "description": "Local destination path"}
                    },
                    "required": ["file_id"]
                }
            },
            {
                "name": "list_files",
                "description": "List files in the storage system",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to list files from"},
                        "recursive": {"type": "boolean", "description": "Whether to list recursively", "default": False}
                    }
                }
            },
            {
                "name": "get_file_metadata",
                "description": "Get metadata for a specific file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the file"}
                    },
                    "required": ["file_id"]
                }
            },
            {
                "name": "search_files",
                "description": "Search for files by name or metadata",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "file_type": {"type": "string", "description": "File type filter"},
                        "limit": {"type": "integer", "description": "Maximum number of results", "default": 100}
                    },
                    "required": ["query"]
                }
            }
        ]
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the MCP server."""
        logger = logging.getLogger("file_broker_mcp")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_storage(self):
        """Initialize storage backends and directories."""
        # Ensure root directory exists
        self.root_path.mkdir(parents=True, exist_ok=True)
        
        # Ensure platform directories exist
        for root in self.platform_roots:
            Path(root).mkdir(parents=True, exist_ok=True)
        
        # Initialize file registry
        self._load_file_registry()
    
    def _load_file_registry(self):
        """Load file registry from disk."""
        registry_path = self.root_path / "file_registry.json"
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    self.file_registry = json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load file registry: {e}")
                self.file_registry = {}
        else:
            self.file_registry = {}
    
    def _save_file_registry(self):
        """Save file registry to disk."""
        registry_path = self.root_path / "file_registry.json"
        try:
            with open(registry_path, 'w') as f:
                json.dump(self.file_registry, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save file registry: {e}")
    
    def _generate_file_id(self, file_path: str) -> str:
        """Generate a unique file ID."""
        return str(uuid.uuid4())
    
    def _calculate_file_hash(self, file_data: bytes) -> str:
        """Calculate SHA-256 hash of file data."""
        return hashlib.sha256(file_data).hexdigest()
    
    # ============================================================================
    # MCP TOOLS - File Operations
    # ============================================================================
    
    def upload_file(self, file_data: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload file with metadata.
        
        Args:
            file_data: File content as bytes
            metadata: File metadata (name, type, etc.)
            
        Returns:
            Upload result with file ID and metadata
        """
        try:
            # Generate file ID and calculate hash
            file_id = self._generate_file_id(metadata.get("name", "unknown"))
            file_hash = self._calculate_file_hash(file_data)
            
            # Determine storage path
            file_name = metadata.get("name", f"file_{file_id}")
            storage_path = self.root_path / file_name
            
            # Save file to storage
            with open(storage_path, 'wb') as f:
                f.write(file_data)
            
            # Update file registry
            file_info = {
                "file_id": file_id,
                "name": file_name,
                "path": str(storage_path),
                "size": len(file_data),
                "hash": file_hash,
                "type": metadata.get("type", "application/octet-stream"),
                "uploaded_at": datetime.now().isoformat(),
                "metadata": metadata
            }
            
            self.file_registry[file_id] = file_info
            self._save_file_registry()
            
            self.logger.info(f"File uploaded successfully: {file_id}")
            
            return {
                "success": True,
                "file_id": file_id,
                "file_info": file_info
            }
            
        except Exception as e:
            self.logger.error(f"Failed to upload file: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def download_file(self, file_id: str) -> Dict[str, Any]:
        """
        Download file by ID.
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            File data and metadata
        """
        try:
            if file_id not in self.file_registry:
                return {
                    "success": False,
                    "error": f"File not found: {file_id}"
                }
            
            file_info = self.file_registry[file_id]
            file_path = Path(file_info["path"])
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"File not found on disk: {file_path}"
                }
            
            # Read file data
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            self.logger.info(f"File downloaded successfully: {file_id}")
            
            return {
                "success": True,
                "file_data": file_data,
                "file_info": file_info
            }
            
        except Exception as e:
            self.logger.error(f"Failed to download file: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """
        Delete file by ID.
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            Deletion result
        """
        try:
            if file_id not in self.file_registry:
                return {
                    "success": False,
                    "error": f"File not found: {file_id}"
                }
            
            file_info = self.file_registry[file_id]
            file_path = Path(file_info["path"])
            
            # Delete file from disk
            if file_path.exists():
                file_path.unlink()
            
            # Remove from registry
            del self.file_registry[file_id]
            self._save_file_registry()
            
            self.logger.info(f"File deleted successfully: {file_id}")
            
            return {
                "success": True,
                "file_id": file_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to delete file: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_files(self, filter_criteria: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        List files with optional filtering.
        
        Args:
            filter_criteria: Optional filtering criteria
            
        Returns:
            List of files matching criteria
        """
        try:
            files = list(self.file_registry.values())
            
            # Apply filters if provided
            if filter_criteria:
                filtered_files = []
                for file_info in files:
                    match = True
                    for key, value in filter_criteria.items():
                        if key in file_info and file_info[key] != value:
                            match = False
                            break
                    if match:
                        filtered_files.append(file_info)
                files = filtered_files
            
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Get file metadata by ID.
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            File metadata
        """
        try:
            if file_id not in self.file_registry:
                return {
                    "success": False,
                    "error": f"File not found: {file_id}"
                }
            
            return {
                "success": True,
                "file_info": self.file_registry[file_id]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get file metadata: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_files(self, query: str, search_fields: List[str] = None) -> Dict[str, Any]:
        """
        Search files by query.
        
        Args:
            query: Search query
            search_fields: Fields to search in
            
        Returns:
            Matching files
        """
        try:
            if search_fields is None:
                search_fields = ["name", "type", "metadata"]
            
            matching_files = []
            query_lower = query.lower()
            
            for file_info in self.file_registry.values():
                match = False
                for field in search_fields:
                    if field in file_info:
                        if isinstance(file_info[field], str):
                            if query_lower in file_info[field].lower():
                                match = True
                                break
                        elif isinstance(file_info[field], dict):
                            # Search in metadata
                            for value in file_info[field].values():
                                if isinstance(value, str) and query_lower in value.lower():
                                    match = True
                                    break
                
                if match:
                    matching_files.append(file_info)
            
            return {
                "success": True,
                "files": matching_files,
                "count": len(matching_files),
                "query": query
            }
            
        except Exception as e:
            self.logger.error(f"Failed to search files: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file information by path.
        
        Args:
            file_path: File path
            
        Returns:
            File information
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            stat = path.stat()
            file_info = {
                "name": path.name,
                "path": str(path),
                "size": stat.st_size,
                "type": "directory" if path.is_dir() else "file",
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
            }
            
            return {
                "success": True,
                "file_info": file_info
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get file info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_directory(self, path: str = ".") -> Dict[str, Any]:
        """
        List contents of a directory.
        
        Args:
            path: Directory path
            
        Returns:
            Directory listing
        """
        try:
            full_path = self.root_path / path
            if not full_path.exists():
                return {
                    "success": False,
                    "error": f"Path does not exist: {path}"
                }
            
            if not full_path.is_dir():
                return {
                    "success": False,
                    "error": f"Path is not a directory: {path}"
                }
            
            items = []
            for item in full_path.iterdir():
                try:
                    stat = item.stat()
                    items.append({
                        "name": item.name,
                        "path": str(item.relative_to(self.root_path)),
                        "type": "directory" if item.is_dir() else "file",
                        "size": stat.st_size if item.is_file() else None,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except Exception as e:
                    self.logger.warning(f"Failed to get info for {item}: {e}")
            
            return {
                "success": True,
                "path": path,
                "items": items,
                "count": len(items)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list directory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_directory(self, path: str) -> Dict[str, Any]:
        """
        Create a directory.
        
        Args:
            path: Directory path to create
            
        Returns:
            Creation result
        """
        try:
            full_path = self.root_path / path
            full_path.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Directory created: {path}")
            
            return {
                "success": True,
                "path": path
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create directory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Storage statistics
        """
        try:
            total_files = len(self.file_registry)
            total_size = sum(file_info["size"] for file_info in self.file_registry.values())
            
            # Get disk usage
            disk_usage = self._get_disk_usage()
            
            stats = {
                "total_files": total_files,
                "total_size": total_size,
                "disk_usage": disk_usage,
                "storage_backends": self.storage_backends,
                "default_backend": self.default_backend,
                "root_path": str(self.root_path)
            }
            
            return {
                "success": True,
                "stats": stats
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get storage stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information."""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.root_path)
            
            return {
                "total": total,
                "used": used,
                "free": free,
                "percent_used": (used / total) * 100
            }
        except Exception as e:
            self.logger.warning(f"Failed to get disk usage: {e}")
            return {}
    
    # ============================================================================
    # MCP RESOURCES
    # ============================================================================
    
    def get_resource(self, resource_path: str) -> Dict[str, Any]:
        """
        Get MCP resource data.
        
        Args:
            resource_path: Resource path
            
        Returns:
            Resource data
        """
        if resource_path == "/files/registry.json":
            return {
                "success": True,
                "data": self.file_registry
            }
        elif resource_path == "/files/storage_stats.json":
            return self.get_storage_stats()
        elif resource_path == "/files/platform_files.json":
            return self._get_platform_files()
        else:
            return {
                "success": False,
                "error": f"Unknown resource: {resource_path}"
            }
    
    # Pattern Reporting Tools
    async def report_core4_patterns(self, pattern_name: str, pattern_type: str, pattern_data: Dict[str, Any]) -> Dict[str, Any]:
        """Report Core 4 atomic patterns to private registry."""
        try:
            result = await self.pattern_reporter.report_core4_pattern(pattern_name, pattern_type, pattern_data)
            self.logger.info(f"Pattern reporting result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error reporting pattern: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_core4_patterns(self, pattern_type: str) -> Dict[str, Any]:
        """Get Core 4 patterns by type."""
        try:
            result = await self.pattern_reporter.get_core4_patterns(pattern_type)
            self.logger.info(f"Pattern retrieval result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error retrieving patterns: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
    
    # Utility Tools
    async def health_check(self, include_metrics: bool = False) -> Dict[str, Any]:
        """Check service health and metrics."""
        try:
            health_status = {
                "status": "healthy",
                "server": "file_broker",
                "version": self.version,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if include_metrics:
                storage_stats = self.get_storage_stats()
                health_status["metrics"] = {
                    "storage_stats": storage_stats,
                    "file_registry_count": len(self.file_registry),
                    "storage_backends": self.storage_backends,
                    "default_backend": self.default_backend
                }
            
            return health_status
        except Exception as e:
            self.logger.error(f"Error in health check: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def log_telemetry(self, telemetry_data: Dict[str, Any], telemetry_type: str = "general") -> Dict[str, Any]:
        """Log telemetry data to Nurse MCP Server."""
        try:
            # For now, just log locally - in production this would call Nurse MCP Server
            self.logger.info(f"Telemetry data ({telemetry_type}): {telemetry_data}")
            return {
                "status": "success",
                "message": "Telemetry data logged",
                "telemetry_type": telemetry_type
            }
        except Exception as e:
            self.logger.error(f"Error logging telemetry: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def log_health_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Log health metrics to Nurse MCP Server."""
        try:
            # For now, just log locally - in production this would call Nurse MCP Server
            self.logger.info(f"Health metrics: {metrics}")
            return {
                "status": "success",
                "message": "Health metrics logged"
            }
        except Exception as e:
            self.logger.error(f"Error logging health metrics: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def log_anomaly(self, anomaly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log anomaly detection to Nurse MCP Server."""
        try:
            # For now, just log locally - in production this would call Nurse MCP Server
            self.logger.warning(f"Anomaly detected: {anomaly_data}")
            return {
                "status": "success",
                "message": "Anomaly logged"
            }
        except Exception as e:
            self.logger.error(f"Error logging anomaly: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _get_platform_files(self) -> Dict[str, Any]:
        """Get platform-specific files."""
        try:
            platform_files = {}
            for root in self.platform_roots:
                root_path = Path(root)
                if root_path.exists():
                    files = []
                    try:
                        for item in root_path.rglob("*"):
                            if item.is_file():
                                try:
                                    files.append({
                                        "name": item.name,
                                        "path": str(item.relative_to(Path.cwd())),
                                        "size": item.stat().st_size,
                                        "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                                    })
                                except Exception as e:
                                    # Skip files that can't be accessed
                                    continue
                    except Exception as e:
                        # Skip directories that can't be accessed
                        continue
                    platform_files[root] = files
                else:
                    platform_files[root] = []
            
            return {
                "success": True,
                "platform_files": platform_files
            }
        except Exception as e:
            return {
                "success": True,  # Return success even if no platform files found
                "platform_files": {},
                "note": f"Platform files not accessible: {str(e)}"
            }
    
    # ============================================================================
    # MCP USAGE GUIDE
    # ============================================================================
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return usage guide for this MCP server."""
        return {
            "server": self.name,
            "version": self.version,
            "status": self.status,
            "purpose": "Raw file storage abstraction for Smart City platform",
            "tools": self.tools,
            "resources": self.resources,
            "prompts": self.prompts,
            "examples": [
                "file_broker.upload_file(file_data, {'name': 'document.pdf', 'type': 'application/pdf'})",
                "file_broker.download_file('file_123')",
                "file_broker.list_files({'type': 'application/pdf'})",
                "file_broker.search_files('document')"
            ],
            "configuration": {
                "storage_backends": self.storage_backends,
                "default_backend": self.default_backend,
                "root_path": str(self.root_path)
            }
        }
    
    def call_tool(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Call a tool by name.
        
        Args:
            tool_name: Name of the tool to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
        
        try:
            method = getattr(self, tool_name)
            return method(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Failed to call tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
