#!/usr/bin/env python3
"""
Content Steward Service - SOA/MCP Module

Micro-module for SOA API exposure and MCP tool integration.
"""

from typing import Any, Dict


class SoaMcp:
    """SOA/MCP module for Content Steward service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def initialize_soa_api_exposure(self):
        """Initialize SOA API exposure for Smart City capabilities (Phase 3.1: Content Steward Finalization)."""
        self.service.soa_apis = {
            # File Lifecycle APIs
            "upload_file": {
                "endpoint": "/api/content-steward/upload",
                "method": "POST",
                "description": "Upload file (raw data storage)",
                "parameters": ["file_data", "file_name", "file_type", "metadata", "user_context"]
            },
            "get_file": {
                "endpoint": "/api/content-steward/file/{file_id}",
                "method": "GET",
                "description": "Get file by ID",
                "parameters": ["file_id"]
            },
            "delete_file": {
                "endpoint": "/api/content-steward/file/{file_id}",
                "method": "DELETE",
                "description": "Delete file by ID",
                "parameters": ["file_id", "user_context"]
            },
            "list_files": {
                "endpoint": "/api/content-steward/files",
                "method": "GET",
                "description": "List files with optional filters",
                "parameters": ["filters", "user_context"]
            },
            "classify_file": {
                "endpoint": "/api/content-steward/file/{file_id}/classify",
                "method": "POST",
                "description": "Classify file (data_classification: 'client' or 'platform')",
                "parameters": ["file_id", "data_classification", "user_context"]
            },
            # Parsed File Storage APIs
            "store_parsed_file": {
                "endpoint": "/api/content-steward/parsed",
                "method": "POST",
                "description": "Store parsed file in GCS + metadata in Supabase",
                "parameters": ["file_id", "parsed_file_data", "format_type", "content_type", "parse_result", "user_context"]
            },
            "get_parsed_file": {
                "endpoint": "/api/content-steward/parsed/{parsed_file_id}",
                "method": "GET",
                "description": "Retrieve parsed file data",
                "parameters": ["parsed_file_id", "user_context"]
            },
            "list_parsed_files": {
                "endpoint": "/api/content-steward/parsed",
                "method": "GET",
                "description": "List parsed files for a file_id",
                "parameters": ["file_id", "user_context"]
            }
        }
        
        if self.service.logger:
            self.service.logger.info(f"✅ SOA APIs exposed: {len(self.service.soa_apis)} endpoints")
    
    async def initialize_mcp_tool_integration(self):
        """Initialize MCP tool integration for content processing."""
        self.service.mcp_tools = {
            "content_processor": {
                "name": "content_processor",
                "description": "Process and analyze content files",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_data": {"type": "string", "description": "File data (base64 encoded)"},
                        "content_type": {"type": "string", "description": "Content type"},
                        "processing_options": {"type": "object", "description": "Processing options"}
                    },
                    "required": ["file_data", "content_type"]
                }
            },
            "metadata_extractor": {
                "name": "metadata_extractor",
                "description": "Extract metadata from content files",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_data": {"type": "string", "description": "File data (base64 encoded)"},
                        "content_type": {"type": "string", "description": "Content type"}
                    },
                    "required": ["file_data", "content_type"]
                }
            },
            "format_converter": {
                "name": "format_converter",
                "description": "Convert content between different formats",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "File ID"},
                        "source_format": {"type": "string", "description": "Source format"},
                        "target_format": {"type": "string", "description": "Target format"}
                    },
                    "required": ["file_id", "source_format", "target_format"]
                }
            },
            "content_validator": {
                "name": "content_validator",
                "description": "Validate content against policies and standards",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content_data": {"type": "string", "description": "Content data (base64 encoded)"},
                        "content_type": {"type": "string", "description": "Content type"}
                    },
                    "required": ["content_data", "content_type"]
                }
            }
        }
        
        if self.service.logger:
            self.service.logger.info(f"✅ MCP tools registered: {len(self.service.mcp_tools)} tools")
    
    async def register_capabilities(self) -> Dict[str, Any]:
        """Register Content Steward capabilities with Curator using Phase 2 pattern (simplified for Smart City)."""
        try:
            # Build capabilities list with SOA API and MCP Tool contracts
            capabilities = []
            
            # Create content_processing capability
            capabilities.append({
                "name": "content_processing",
                "protocol": "ContentStewardServiceProtocol",
                "description": "Content file processing and analysis",
                "contracts": {
                    "soa_api": {
                        "api_name": "process_upload",
                        "endpoint": self.service.soa_apis.get("process_upload", {}).get("endpoint", "/soa/content-steward/process_upload"),
                        "method": self.service.soa_apis.get("process_upload", {}).get("method", "POST"),
                        "handler": getattr(self.service, "process_upload", None),
                        "metadata": {
                            "description": "Process uploaded file with content analysis"
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "content_steward_content_processor",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "content_steward_content_processor",
                            "description": "Process and analyze content files",
                            "input_schema": self.service.mcp_tools.get("content_processor", {}).get("input_schema", {})
                        }
                    }
                }
            })
            
            # Create metadata_management capability
            capabilities.append({
                "name": "metadata_management",
                "protocol": "ContentStewardServiceProtocol",
                "description": "Content metadata extraction and management",
                "contracts": {
                    "soa_api": {
                        "api_name": "get_file_metadata",
                        "endpoint": self.service.soa_apis.get("get_file_metadata", {}).get("endpoint", "/soa/content-steward/get_file_metadata"),
                        "method": self.service.soa_apis.get("get_file_metadata", {}).get("method", "GET"),
                        "handler": getattr(self.service, "get_file_metadata", None),
                        "metadata": {
                            "description": "Retrieve metadata for specific file"
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "content_steward_metadata_extractor",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "content_steward_metadata_extractor",
                            "description": "Extract metadata from content files",
                            "input_schema": self.service.mcp_tools.get("metadata_extractor", {}).get("input_schema", {})
                        }
                    }
                }
            })
            
            # Create format_conversion capability
            capabilities.append({
                "name": "format_conversion",
                "protocol": "ContentStewardServiceProtocol",
                "description": "File format conversion",
                "contracts": {
                    "soa_api": {
                        "api_name": "convert_file_format",
                        "endpoint": self.service.soa_apis.get("convert_file_format", {}).get("endpoint", "/soa/content-steward/convert_file_format"),
                        "method": self.service.soa_apis.get("convert_file_format", {}).get("method", "POST"),
                        "handler": getattr(self.service, "convert_file_format", None),
                        "metadata": {
                            "description": "Convert file format"
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "content_steward_format_converter",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "content_steward_format_converter",
                            "description": "Convert content between different formats",
                            "input_schema": self.service.mcp_tools.get("format_converter", {}).get("input_schema", {})
                        }
                    }
                }
            })
            
            # Create content_validation capability
            capabilities.append({
                "name": "content_validation",
                "protocol": "ContentStewardServiceProtocol",
                "description": "Content validation and quality metrics",
                "contracts": {
                    "soa_api": {
                        "api_name": "validate_content",
                        "endpoint": self.service.soa_apis.get("validate_content", {}).get("endpoint", "/soa/content-steward/validate_content"),
                        "method": self.service.soa_apis.get("validate_content", {}).get("method", "POST"),
                        "handler": getattr(self.service, "validate_content", None),
                        "metadata": {
                            "description": "Validate content against policies",
                            "apis": ["validate_content", "get_quality_metrics"]
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "content_steward_content_validator",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "content_steward_content_validator",
                            "description": "Validate content against policies and standards",
                            "input_schema": self.service.mcp_tools.get("content_validator", {}).get("input_schema", {})
                        }
                    }
                }
            })
            
            # Register using register_with_curator (simplified Phase 2 pattern)
            soa_api_names = list(self.service.soa_apis.keys())
            mcp_tool_names = [f"content_steward_{tool}" for tool in self.service.mcp_tools.keys()]
            
            success = await self.service.register_with_curator(
                capabilities=capabilities,
                soa_apis=soa_api_names,
                mcp_tools=mcp_tool_names,
                protocols=[{
                    "name": "ContentStewardServiceProtocol",
                    "definition": {
                        "methods": {api: {"input_schema": {}, "output_schema": {}} for api in soa_api_names}
                    }
                }]
            )
            
            if success:
                if self.service.logger:
                    self.service.logger.info(f"✅ Content Steward registered with Curator (Phase 2 pattern - Smart City): {len(capabilities)} capabilities")
            else:
                if self.service.logger:
                    self.service.logger.warning("⚠️ Failed to register Content Steward with Curator")
                    
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to register Content Steward capabilities: {e}")
                import traceback
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return capabilities metadata
        return await self._get_content_steward_capabilities_dict()
    
    async def register_content_steward_capabilities(self) -> Dict[str, Any]:
        """Register Content Steward service capabilities (backward compatibility - calls register_capabilities first)."""
        # Call register_capabilities first to ensure Curator registration happens
        return await self.register_capabilities()
    
    async def _get_content_steward_capabilities_dict(self) -> Dict[str, Any]:
        """Get Content Steward service capabilities dict."""
        capabilities = {
            "content_processing": {
                "process_upload": True,
                "process_file_content": True,
                "get_file_metadata": True,
                "update_file_metadata": True
            },
            "format_conversion": {
                "convert_file_format": True,
                "batch_convert_formats": True
            },
            "data_optimization": {
                "optimize_data": True,
                "compress_data": True,
                "validate_output": True
            },
            "content_validation": {
                "validate_content": True,
                "get_quality_metrics": True
            },
            "metadata_management": {
                "get_asset_metadata": True,
                "get_lineage": True,
                "get_processing_status": True
            },
            "infrastructure": {
                "file_management_gcs_supabase": True,
                "content_metadata_arango": True,
                "messaging_cache_redis": True
            }
        }
        
        if self.service.logger:
            self.service.logger.info("✅ Content Steward capabilities registered")
        
        return capabilities






