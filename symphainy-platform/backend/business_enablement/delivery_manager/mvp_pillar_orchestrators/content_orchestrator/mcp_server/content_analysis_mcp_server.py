#!/usr/bin/env python3
"""
Content Analysis MCP Server

Wraps Content Analysis Orchestrator as MCP Tools for agent consumption.

IMPORTANT: MCP servers are at the ORCHESTRATOR level (not enabling service level).
This provides use case-level tools for agents, not low-level service tools.
"""

import os
import sys
from typing import Dict, Any
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../../../'))

from bases.mcp_server.mcp_server_base import MCPServerBase


class ContentAnalysisMCPServer(MCPServerBase):
    """
    MCP Server for Content Analysis Orchestrator (MVP Use Case).
    
    Provides use case-level tools for agents:
    - analyze_document_tool: Complete document analysis (structure, metadata, entities)
    - parse_file_tool: File parsing
    - extract_entities_tool: Entity extraction
    
    These are HIGH-LEVEL tools that orchestrate multiple enabling services internally.
    Agents don't need to know about FileParser, DataAnalyzer, etc.
    """
    
    def __init__(self, orchestrator, di_container):
        """
        Initialize Content Analysis MCP Server.
        
        Args:
            orchestrator: ContentAnalysisOrchestrator instance
            di_container: DI Container for platform services
        """
        super().__init__(
            service_name="content_analysis_mcp",
            di_container=di_container
        )
        self.orchestrator = orchestrator
    
    def register_server_tools(self) -> None:
        """Register MCP tools (use case-level, not service-level)."""
        
        # Tool 1: Analyze Document (orchestrates multiple services)
        self.register_tool(
            tool_name="analyze_document_tool",
            handler=self._analyze_document_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "ID of document to analyze"
                    },
                    "analysis_types": {
                        "type": "array",
                        "description": "Types of analysis to perform",
                        "items": {
                            "type": "string",
                            "enum": ["structure", "metadata", "entities"]
                        },
                        "default": ["structure", "metadata", "entities"]
                    }
                },
                "required": ["document_id"]
            }
        )
        
        # Tool 2: Parse File
        self.register_tool(
            name="parse_file_tool",
            description="Parse file into structured format. Delegates to FileParserService.",
            handler=self._parse_file_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "ID of file to parse"
                    },
                    "parse_options": {
                        "type": "object",
                        "description": "Optional parsing configuration",
                        "properties": {}
                    }
                },
                "required": ["file_id"]
            }
        )
        
        # Tool 3: Extract Entities
        self.register_tool(
            name="extract_entities_tool",
            description="Extract entities from document. Delegates to DataAnalyzerService.",
            handler=self._extract_entities_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "ID of document to extract entities from"
                    }
                },
                "required": ["document_id"]
            }
        )
        
        # Tool 4: List Files
        self.register_tool(
            name="list_files_tool",
            description="List uploaded files for a user. Uses Librarian/Content Steward.",
            handler=self._list_files_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    }
                },
                "required": ["user_id"]
            }
        )
        
        # Tool 5: Get File Metadata
        self.register_tool(
            name="get_file_metadata_tool",
            description="Get file details including metadata. Uses Librarian/Content Steward.",
            handler=self._get_file_metadata_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "File UUID"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    }
                },
                "required": ["file_id", "user_id"]
            }
        )
        
        # Tool 6: Process Documents (Batch)
        self.register_tool(
            name="process_documents_tool",
            description="Batch process multiple documents: parse, analyze, extract entities.",
            handler=self._process_documents_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "file_ids": {
                        "type": "array",
                        "description": "List of file IDs to process",
                        "items": {"type": "string"}
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    },
                    "processing_options": {
                        "type": "object",
                        "description": "Optional processing configuration"
                    }
                },
                "required": ["file_ids", "user_id"]
            }
        )
        
        # Tool 7: Convert Format
        self.register_tool(
            name="convert_format_tool",
            description="Convert file format using FormatComposerService (parquet, json_structured, json_chunks).",
            handler=self._convert_format_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "File ID to convert"
                    },
                    "target_format": {
                        "type": "string",
                        "description": "Target format",
                        "enum": ["parquet", "json_structured", "json_chunks"]
                    },
                    "user_id": {
                        "type": "string",
                        "description": "Optional user identifier"
                    },
                    "conversion_options": {
                        "type": "object",
                        "description": "Optional conversion configuration"
                    }
                },
                "required": ["file_id", "target_format"]
            }
        )
        
        # Tool 8: Enhance Metadata Extraction (Agent-Assisted)
        self.register_tool(
            name="enhance_metadata_extraction_tool",
            description="Agent-assisted metadata enhancement from parsed results (POST-PARSING ONLY).",
            handler=self._enhance_metadata_extraction_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "parsed_result": {
                        "type": "object",
                        "description": "Parsed content dictionary"
                    },
                    "file_id": {
                        "type": "string",
                        "description": "File identifier"
                    }
                },
                "required": ["parsed_result", "file_id"]
            }
        )
        
        # Tool 9: Enhance Content Insights (Agent-Assisted)
        self.register_tool(
            name="enhance_content_insights_tool",
            description="Agent-assisted insights enhancement from parsed results (POST-PARSING ONLY).",
            handler=self._enhance_content_insights_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "parsed_result": {
                        "type": "object",
                        "description": "Parsed content dictionary"
                    },
                    "file_id": {
                        "type": "string",
                        "description": "File identifier"
                    }
                },
                "required": ["parsed_result", "file_id"]
            }
        )
        
        # Tool 10: Recommend Format Optimization
        self.register_tool(
            name="recommend_format_optimization_tool",
            description="Recommend format optimization based on content structure (POST-PARSING ONLY).",
            handler=self._recommend_format_optimization_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "parsed_result": {
                        "type": "object",
                        "description": "Parsed content dictionary"
                    },
                    "file_id": {
                        "type": "string",
                        "description": "File identifier"
                    }
                },
                "required": ["parsed_result", "file_id"]
            }
        )
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return machine + human readable usage guide."""
        return {
            "server_name": self.service_name,
            "description": "Content Analysis MCP Server - Provides use case-level tools for document analysis",
            "tools": {
                "analyze_document_tool": "Complete document analysis (structure, metadata, entities)",
                "parse_file_tool": "Parse file into structured format",
                "extract_entities_tool": "Extract entities from document",
                "list_files_tool": "List uploaded files for a user",
                "get_file_metadata_tool": "Get file metadata",
                "process_documents_tool": "Process multiple documents",
                "convert_format_tool": "Convert document format",
                "enhance_metadata_extraction_tool": "Enhance metadata extraction",
                "enhance_content_insights_tool": "Enhance content insights",
                "recommend_format_optimization_tool": "Recommend format optimization"
            },
            "usage_pattern": "All tools require user_context for multi-tenancy and security"
        }
    
    def get_tool_list(self) -> list:
        """Return list of available tool names."""
        return [
            "analyze_document_tool",
            "parse_file_tool",
            "extract_entities_tool",
            "list_files_tool",
            "get_file_metadata_tool",
            "process_documents_tool",
            "convert_format_tool",
            "enhance_metadata_extraction_tool",
            "enhance_content_insights_tool",
            "recommend_format_optimization_tool"
        ]
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Return health status with upstream dependency checks."""
        try:
            # Check orchestrator health
            orchestrator_health = "healthy"
            if hasattr(self.orchestrator, 'get_health_status'):
                try:
                    health = await self.orchestrator.get_health_status()
                    orchestrator_health = health.get("status", "unknown")
                except Exception:
                    orchestrator_health = "error"
            
            return {
                "server_name": self.service_name,
                "status": "healthy" if orchestrator_health == "healthy" else "degraded",
                "orchestrator_status": orchestrator_health,
                "tools_registered": len(self.get_tool_list()),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "server_name": self.service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_version_info(self) -> Dict[str, Any]:
        """Return version and compatibility info."""
        return {
            "server_name": self.service_name,
            "version": "1.0.0",
            "api_version": "v1",
            "compatible_with": ["content_analysis_orchestrator"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def execute_tool(self, tool_name: str, parameters: dict, user_context: Dict[str, Any] = None) -> dict:
        """
        Execute tool by routing to orchestrator.
        
        Includes utility usage:
        - Telemetry tracking
        - Error handling
        
        The orchestrator handles the complexity of composing multiple services.
        """
        try:
            # Start telemetry tracking
            if self.utilities.telemetry:
                try:
                    await self.utilities.telemetry.collect_metric({
                        "name": "execute_tool_start",
                        "value": 1.0,
                        "type": "counter",
                        "labels": {"tool_name": tool_name, "mcp_server": self.service_name}
                    })
                except Exception:
                    pass  # Telemetry is optional
            
            tool_handlers = {
                "analyze_document_tool": self._analyze_document_tool,
                "parse_file_tool": self._parse_file_tool,
                "extract_entities_tool": self._extract_entities_tool,
                "list_files_tool": self._list_files_tool,
                "get_file_metadata_tool": self._get_file_metadata_tool,
                "process_documents_tool": self._process_documents_tool,
                "convert_format_tool": self._convert_format_tool,
                "enhance_metadata_extraction_tool": self._enhance_metadata_extraction_tool,
                "enhance_content_insights_tool": self._enhance_content_insights_tool,
                "recommend_format_optimization_tool": self._recommend_format_optimization_tool
            }
            
            handler = tool_handlers.get(tool_name)
            if handler:
                # Add user_context to parameters if not present
                if user_context and "user_context" not in parameters:
                    parameters["user_context"] = user_context
                
                result = await handler(**parameters)
                
                # End telemetry tracking
                if self.utilities.telemetry:
                    try:
                        await self.utilities.telemetry.collect_metric({
                            "name": "execute_tool_complete",
                            "value": 1.0,
                            "type": "counter",
                            "labels": {"tool_name": tool_name, "status": "success" if result.get("success", True) else "failed"}
                        })
                    except Exception:
                        pass
                
                return result
            else:
                # Record health metric (tool not found)
                if self.utilities.health:
                    try:
                        await self.utilities.health.record_metric("execute_tool_not_found", 1.0, {"tool_name": tool_name})
                    except Exception:
                        pass
                
                # End telemetry tracking
                if self.utilities.telemetry:
                    try:
                        await self.utilities.telemetry.collect_metric({
                            "name": "execute_tool_complete",
                            "value": 0.0,
                            "type": "counter",
                            "labels": {"tool_name": tool_name, "status": "not_found"}
                        })
                    except Exception:
                        pass
                
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            # Error handling
            self.utilities.logger.error(f"❌ execute_tool failed for {tool_name}: {e}")
            
            # Audit logging (if security available)
            if self.utilities.security:
                try:
                    await self.utilities.security.audit_log({
                        "action": "execute_tool_failed",
                        "mcp_server": self.service_name,
                        "tool_name": tool_name,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception:
                    pass  # Audit is optional
            
            # Record health metric (failure)
            if self.utilities.health:
                try:
                    await self.utilities.health.record_metric("execute_tool_error", 1.0, {
                        "tool_name": tool_name,
                        "error": type(e).__name__
                    })
                except Exception:
                    pass
            
            # End telemetry tracking with failure
            if self.utilities.telemetry:
                try:
                    await self.utilities.telemetry.collect_metric({
                        "name": "execute_tool_complete",
                        "value": 0.0,
                        "type": "counter",
                        "labels": {"tool_name": tool_name, "status": "error", "error": str(e)}
                    })
                except Exception:
                    pass
            
            return {
                "success": False,
                "error": str(e),
                "message": f"Tool execution failed: {str(e)}"
            }
    
    async def _analyze_document_tool(
        self,
        document_id: str,
        analysis_types: list = None,
        user_context: Dict[str, Any] = None
    ) -> dict:
        """
        MCP Tool: Analyze Document (use case-level).
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        
        This is a HIGH-LEVEL tool that orchestrates:
        - FileParserService.parse_file()
        - FileParserService.extract_metadata()
        - DataAnalyzerService.extract_entities()
        
        Agents use this single tool instead of orchestrating services themselves.
        """
        try:
            # Start telemetry tracking
            if self.utilities.telemetry:
                try:
                    await self.utilities.telemetry.collect_metric({
                        "name": "analyze_document_tool_start",
                        "value": 1.0,
                        "type": "counter",
                        "labels": {"document_id": document_id, "mcp_server": self.service_name}
                    })
                except Exception:
                    pass  # Telemetry is optional
            
            # Security validation (zero-trust: secure by design)
            if user_context and self.utilities.security:
                try:
                    if not await self.utilities.security.check_permissions(user_context, "document_analysis", "execute"):
                        # Record health metric (access denied)
                        if self.utilities.health:
                            try:
                                await self.utilities.health.record_metric("analyze_document_tool_access_denied", 1.0, {"document_id": document_id})
                            except Exception:
                                pass
                        # End telemetry tracking
                        if self.utilities.telemetry:
                            try:
                                await self.utilities.telemetry.collect_metric({
                                    "name": "analyze_document_tool_complete",
                                    "value": 0.0,
                                    "type": "counter",
                                    "labels": {"document_id": document_id, "status": "access_denied"}
                                })
                            except Exception:
                                pass
                        raise PermissionError("Access denied: insufficient permissions to analyze document")
                except PermissionError:
                    raise
                except Exception:
                    pass  # Security check is optional
            
            # Tenant validation (multi-tenant support)
            if user_context and self.utilities.tenant:
                try:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await self.utilities.tenant.validate_tenant_access(tenant_id):
                            # Record health metric (tenant denied)
                            if self.utilities.health:
                                try:
                                    await self.utilities.health.record_metric("analyze_document_tool_tenant_denied", 1.0, {
                                        "document_id": document_id,
                                        "tenant_id": tenant_id
                                    })
                                except Exception:
                                    pass
                            # End telemetry tracking
                            if self.utilities.telemetry:
                                try:
                                    await self.utilities.telemetry.collect_metric({
                                        "name": "analyze_document_tool_complete",
                                        "value": 0.0,
                                        "type": "counter",
                                        "labels": {"document_id": document_id, "status": "tenant_denied"}
                                    })
                                except Exception:
                                    pass
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
                except PermissionError:
                    raise
                except Exception:
                    pass  # Tenant validation is optional
            
            if analysis_types is None:
                analysis_types = ["structure", "metadata", "entities"]
            
            result = await self.orchestrator.analyze_document(
                document_id=document_id,
                analysis_types=analysis_types,
                user_context=user_context
            )
            
            # Record health metric (success)
            if self.utilities.health:
                try:
                    await self.utilities.health.record_metric("analyze_document_tool_success", 1.0, {
                        "document_id": document_id
                    })
                except Exception:
                    pass
            
            # End telemetry tracking
            if self.utilities.telemetry:
                try:
                    await self.utilities.telemetry.collect_metric({
                        "name": "analyze_document_tool_complete",
                        "value": 1.0,
                        "type": "counter",
                        "labels": {"document_id": document_id, "status": "success"}
                    })
                except Exception:
                    pass
            
            return result
            
        except PermissionError:
            raise  # Re-raise permission errors
        except Exception as e:
            # Error handling with audit
            self.utilities.logger.error(f"❌ analyze_document_tool failed: {e}")
            
            # Audit logging (if security available)
            if self.utilities.security:
                try:
                    await self.utilities.security.audit_log({
                        "action": "analyze_document_tool_failed",
                        "mcp_server": self.service_name,
                        "document_id": document_id,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception:
                    pass  # Audit is optional
            
            # Record health metric (failure)
            if self.utilities.health:
                try:
                    await self.utilities.health.record_metric("analyze_document_tool_error", 1.0, {
                        "document_id": document_id,
                        "error": type(e).__name__
                    })
                except Exception:
                    pass
            
            # End telemetry tracking with failure
            if self.utilities.telemetry:
                try:
                    await self.utilities.telemetry.collect_metric({
                        "name": "analyze_document_tool_complete",
                        "value": 0.0,
                        "type": "counter",
                        "labels": {"document_id": document_id, "status": "error", "error": str(e)}
                    })
                except Exception:
                    pass
            
            return {
                "success": False,
                "error": str(e),
                "message": f"Document analysis failed: {str(e)}"
            }
    
    async def _parse_file_tool(self, file_id: str, parse_options: dict = None, user_context: Dict[str, Any] = None) -> dict:
        """
        MCP Tool: Parse File.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        try:
            # Start telemetry tracking
            if self.utilities.telemetry:
                try:
                    await self.utilities.telemetry.collect_metric({
                        "name": "parse_file_tool_start",
                        "value": 1.0,
                        "type": "counter",
                        "labels": {"file_id": file_id, "mcp_server": self.service_name}
                    })
                except Exception:
                    pass  # Telemetry is optional
            
            # Security validation (zero-trust: secure by design)
            if user_context and self.utilities.security:
                try:
                    if not await self.utilities.security.check_permissions(user_context, "file_parsing", "execute"):
                        # Record health metric (access denied)
                        if self.utilities.health:
                            try:
                                await self.utilities.health.record_metric("parse_file_tool_access_denied", 1.0, {"file_id": file_id})
                            except Exception:
                                pass
                        # End telemetry tracking
                        if self.utilities.telemetry:
                            try:
                                await self.utilities.telemetry.collect_metric({
                                    "name": "parse_file_tool_complete",
                                    "value": 0.0,
                                    "type": "counter",
                                    "labels": {"file_id": file_id, "status": "access_denied"}
                                })
                            except Exception:
                                pass
                        raise PermissionError("Access denied: insufficient permissions to parse file")
                except PermissionError:
                    raise
                except Exception:
                    pass  # Security check is optional
            
            # Tenant validation (multi-tenant support)
            if user_context and self.utilities.tenant:
                try:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await self.utilities.tenant.validate_tenant_access(tenant_id):
                            # Record health metric (tenant denied)
                            if self.utilities.health:
                                try:
                                    await self.utilities.health.record_metric("parse_file_tool_tenant_denied", 1.0, {
                                        "file_id": file_id,
                                        "tenant_id": tenant_id
                                    })
                                except Exception:
                                    pass
                            # End telemetry tracking
                            if self.utilities.telemetry:
                                try:
                                    await self.utilities.telemetry.collect_metric({
                                        "name": "parse_file_tool_complete",
                                        "value": 0.0,
                                        "type": "counter",
                                        "labels": {"file_id": file_id, "status": "tenant_denied"}
                                    })
                                except Exception:
                                    pass
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
                except PermissionError:
                    raise
                except Exception:
                    pass  # Tenant validation is optional
            
            result = await self.orchestrator.parse_file(
                file_id=file_id,
                parse_options=parse_options,
                user_context=user_context
            )
            
            # Record health metric (success)
            if self.utilities.health:
                try:
                    await self.utilities.health.record_metric("parse_file_tool_success", 1.0, {
                        "file_id": file_id
                    })
                except Exception:
                    pass
            
            # End telemetry tracking
            if self.utilities.telemetry:
                try:
                    await self.utilities.telemetry.collect_metric({
                        "name": "parse_file_tool_complete",
                        "value": 1.0,
                        "type": "counter",
                        "labels": {"file_id": file_id, "status": "success"}
                    })
                except Exception:
                    pass
            
            return result
            
        except PermissionError:
            raise  # Re-raise permission errors
        except Exception as e:
            # Error handling with audit
            self.utilities.logger.error(f"❌ parse_file_tool failed: {e}")
            
            # Audit logging (if security available)
            if self.utilities.security:
                try:
                    await self.utilities.security.audit_log({
                        "action": "parse_file_tool_failed",
                        "mcp_server": self.service_name,
                        "file_id": file_id,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception:
                    pass  # Audit is optional
            
            # Record health metric (failure)
            if self.utilities.health:
                try:
                    await self.utilities.health.record_metric("parse_file_tool_error", 1.0, {
                        "file_id": file_id,
                        "error": type(e).__name__
                    })
                except Exception:
                    pass
            
            # End telemetry tracking with failure
            if self.utilities.telemetry:
                try:
                    await self.utilities.telemetry.collect_metric({
                        "name": "parse_file_tool_complete",
                        "value": 0.0,
                        "type": "counter",
                        "labels": {"file_id": file_id, "status": "error", "error": str(e)}
                    })
                except Exception:
                    pass
            
            return {
                "success": False,
                "error": str(e),
                "message": f"File parsing failed: {str(e)}"
            }
    
    async def _extract_entities_tool(self, document_id: str) -> dict:
        """MCP Tool: Extract Entities."""
        return await self.orchestrator.extract_entities(document_id=document_id)
    
    async def _list_files_tool(self, user_id: str) -> dict:
        """MCP Tool: List uploaded files."""
        return await self.orchestrator.list_uploaded_files(user_id=user_id)
    
    async def _get_file_metadata_tool(self, file_id: str, user_id: str) -> dict:
        """MCP Tool: Get file metadata."""
        return await self.orchestrator.get_file_details(file_id=file_id, user_id=user_id)
    
    async def _process_documents_tool(
        self,
        file_ids: list,
        user_id: str,
        processing_options: dict = None
    ) -> dict:
        """MCP Tool: Batch process documents."""
        return await self.orchestrator.process_documents(
            file_ids=file_ids,
            user_id=user_id,
            processing_options=processing_options
        )
    
    async def _convert_format_tool(
        self,
        file_id: str,
        target_format: str,
        user_id: str = None,
        conversion_options: dict = None
    ) -> dict:
        """MCP Tool: Convert file format."""
        return await self.orchestrator.convert_format(
            file_id=file_id,
            target_format=target_format,
            user_id=user_id,
            conversion_options=conversion_options
        )
    
    async def _enhance_metadata_extraction_tool(
        self,
        parsed_result: dict,
        file_id: str
    ) -> dict:
        """MCP Tool: Agent-assisted metadata enhancement (POST-PARSING ONLY)."""
        # Get agent from orchestrator
        if hasattr(self.orchestrator, 'processing_agent') and self.orchestrator.processing_agent:
            return await self.orchestrator.processing_agent.enhance_metadata_extraction(
                parsed_result=parsed_result,
                file_id=file_id
            )
        else:
            return {
                "success": False,
                "error": "Content Processing Agent not available"
            }
    
    async def _enhance_content_insights_tool(
        self,
        parsed_result: dict,
        file_id: str
    ) -> dict:
        """MCP Tool: Agent-assisted insights enhancement (POST-PARSING ONLY)."""
        # Get agent from orchestrator
        if hasattr(self.orchestrator, 'processing_agent') and self.orchestrator.processing_agent:
            return await self.orchestrator.processing_agent.enhance_content_insights(
                parsed_result=parsed_result,
                file_id=file_id
            )
        else:
            return {
                "success": False,
                "error": "Content Processing Agent not available"
            }
    
    async def _recommend_format_optimization_tool(
        self,
        parsed_result: dict,
        file_id: str
    ) -> dict:
        """MCP Tool: Format recommendation (POST-PARSING ONLY)."""
        # Get agent from orchestrator
        if hasattr(self.orchestrator, 'processing_agent') and self.orchestrator.processing_agent:
            return await self.orchestrator.processing_agent.recommend_format_optimization(
                parsed_result=parsed_result,
                file_id=file_id
            )
        else:
            return {
                "success": False,
                "error": "Content Processing Agent not available"
            }









