#!/usr/bin/env python3
"""
Content Journey Orchestrator - Journey Realm

WHAT: Orchestrates content operations (parsing, semantic layer creation)
HOW: Delegates to Content realm services (FileParserService, etc.) while preserving UI integration

This orchestrator is in the Journey realm and orchestrates content operations.
It extends Smart City capabilities (ContentSteward) to create the semantic data layer.

Architecture:
- Journey Realm: Operations orchestration
- Orchestrates Content realm services (FileParserService, semantic layer services)
- Uses Smart City services (ContentSteward, DataSteward) via Curator
- Self-initializing (doesn't require ContentManager)
"""

import os
import sys
import asyncio
import uuid
import io
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../../'))

from bases.orchestrator_base import OrchestratorBase
from utilities.security_authorization.request_context import get_request_user_context

# JSONL conversion uses standard library json (no external dependencies needed)
# For analytics, pandas can read JSONL: pd.read_json('file.jsonl', lines=True) or pd.DataFrame(list_of_dicts)


class ContentJourneyOrchestrator(OrchestratorBase):
    """
    Content Journey Orchestrator - Journey Realm
    
    Orchestrates content operations:
    - File parsing
    - Content storage
    - Semantic layer creation
    
    Extends OrchestratorBase for Smart City access and orchestrator capabilities.
    Preserves MVP UI integration while delegating to Content realm services.
    
    Key Principles:
    - Journey Realm: Operations orchestration
    - Orchestrates Content realm services (FileParserService, semantic layer services)
    - Uses Smart City services (ContentSteward, DataSteward) via Curator
    - Self-initializing (doesn't require ContentManager)
    
    This orchestrator has an MCP Server that exposes use case-level tools for agents.
    """
    
    def __init__(self, platform_gateway, di_container):
        """
        Initialize Content Journey Orchestrator.
        
        Args:
            platform_gateway: Platform Gateway instance
            di_container: DI Container instance
        """
        # Self-initializing - doesn't require ContentManager
        super().__init__(
            service_name="ContentJourneyOrchestratorService",
            realm_name="journey",  # ✅ Journey realm
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        # Set a shorter orchestrator name for MVP UI compatibility
        self.orchestrator_name = "ContentJourneyOrchestrator"
        
        # Enabling services (lazy initialization - created on first use)
        self._file_parser_service = None
        self._data_analyzer_service = None
        
        # NOTE: File storage is handled by FileManagementAbstraction (GCS + Supabase)
        # No in-memory storage needed - files are persisted via infrastructure abstractions
    
    async def _get_file_parser_service(self):
        """
        Lazy initialization of File Parser Service (Content realm service).
        
        File Parser Service is a Content realm service that extends Smart City capabilities.
        """
        if self._file_parser_service is None:
            try:
                # Import and initialize directly (Content realm service)
                from backend.content.services.file_parser_service.file_parser_service import FileParserService
                
                self._file_parser_service = FileParserService(
                    service_name="FileParserService",
                    realm_name="content",  # ✅ Content realm service
                    platform_gateway=self.platform_gateway,
                    di_container=self.di_container
                )
                await self._file_parser_service.initialize()
                self.logger.info("✅ File Parser Service initialized (Content realm)")
                
            except Exception as e:
                self.logger.error(f"❌ File Parser Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                # Tier 4: Return None - calling code handles None gracefully with structured error
                return None
        
        return self._file_parser_service
    
    async def _get_mvp_journey_orchestrator(self):
        """Get MVP Journey Orchestrator for solution context retrieval."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                mvp_orchestrator = await curator.discover_service_by_name("MVPJourneyOrchestratorService")
                if mvp_orchestrator:
                    return mvp_orchestrator
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover MVPJourneyOrchestratorService: {e}")
        return None
    
    # ❌ REMOVED: DataAnalyzerService is Insights-specific, not Content-specific
    # Content realm should not use Insights services directly
    
    # REMOVED: _get_data_solution_orchestrator() method
    # This created a circular dependency:
    # Data Solution Orchestrator → Content Journey Orchestrator → Data Solution Orchestrator
    # 
    # ContentJourneyOrchestrator should NOT call Data Solution Orchestrator directly.
    # Instead, it should call Content Steward and other Content realm services directly.
    # Data Solution Orchestrator calls ContentJourneyOrchestrator, not the other way around.
    
    async def initialize(self) -> bool:
        """
        Initialize Content Analysis Orchestrator and its agents.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self._realm_service.log_operation_with_telemetry(
            "content_analysis_orchestrator_initialize_start",
            success=True
        )
        
        # Call parent initialize (sets up RealmServiceBase)
        init_result = await super().initialize()
        if not init_result:
            self.logger.warning("⚠️ Base orchestrator initialization failed, continuing anyway...")
        
        try:
            self.logger.info(f"🚀 Initializing {self.orchestrator_name} agents...")
            
            # Initialize agents using OrchestratorBase helper (via Agentic Foundation factory)
            from .agents.content_liaison_agent import ContentLiaisonAgent
            from .agents.content_processing_agent import ContentProcessingAgent
            
            self.liaison_agent = await self.initialize_agent(
                ContentLiaisonAgent,
                "ContentLiaisonAgent",
                agent_type="liaison",
                capabilities=[
                    "file_upload_guidance",
                    "document_parsing_help",
                    "format_conversion_advice",
                    "content_validation_support",
                    "metadata_extraction_guidance"
                ],
                required_roles=[]
            )
            
            # Set pillar for this liaison agent (Phase 4.5)
            if self.liaison_agent:
                self.liaison_agent.pillar = "content"
                self.logger.info("✅ Set pillar='content' for ContentLiaisonAgent")
            
            from backend.business_enablement.protocols.business_specialist_agent_protocol import SpecialistCapability
            
            self.processing_agent = await self.initialize_agent(
                ContentProcessingAgent,
                "ContentProcessingAgent",
                agent_type="specialist",
                capabilities=[
                    "content_processing",
                    "file_parsing",
                    "format_conversion",
                    "content_optimization"
                ],
                required_roles=[],
                specialist_capability=SpecialistCapability.CONTENT_PROCESSING
            )
            
            # Give specialist agent access to orchestrator (for MCP server access)
            if self.processing_agent and hasattr(self.processing_agent, 'set_orchestrator'):
                self.processing_agent.set_orchestrator(self)
            
            # Initialize MCP Server (exposes orchestrator methods as MCP tools)
            from .mcp_server import ContentAnalysisMCPServer
            
            self.mcp_server = ContentAnalysisMCPServer(
                orchestrator=self,
                di_container=self.di_container
            )
            # MCP server registers tools in __init__, ready to use
            self.logger.info(f"✅ {self.orchestrator_name} MCP Server initialized")
            
            # Register with Curator (Phase 2 pattern with CapabilityDefinition structure)
            await self._realm_service.register_with_curator(
                capabilities=[
                    {
                        "name": "file_upload",
                        "protocol": "ContentAnalysisOrchestratorProtocol",
                        "description": "Upload files for content analysis",
                        "contracts": {
                            "soa_api": {
                                "api_name": "handle_content_upload",
                                "endpoint": "/api/v1/content-pillar/upload-file",
                                "method": "POST",
                                "handler": self.handle_content_upload,
                                "metadata": {
                                    "description": "Upload file for analysis",
                                    "parameters": ["file_data", "filename", "file_type", "user_id", "session_id"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "handle_content_upload_tool",
                                "tool_definition": {
                                    "name": "handle_content_upload_tool",
                                    "description": "Upload file for content analysis",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "file_data": {"type": "string", "format": "base64"},
                                            "filename": {"type": "string"},
                                            "file_type": {"type": "string"},
                                            "user_id": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "content.upload_file",
                            "semantic_api": "/api/v1/content-pillar/upload-file",
                            "user_journey": "upload_document"
                        }
                    },
                    {
                        "name": "file_parsing",
                        "protocol": "ContentAnalysisOrchestratorProtocol",
                        "description": "Parse files into structured formats",
                        "contracts": {
                            "soa_api": {
                                "api_name": "parse_file",
                                "endpoint": "/api/v1/content-pillar/parse-file",
                                "method": "POST",
                                "handler": self.parse_file,
                                "metadata": {
                                    "description": "Parse file into structured format",
                                    "parameters": ["file_id", "parse_options"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "parse_file_tool",
                                "tool_definition": {
                                    "name": "parse_file_tool",
                                    "description": "Parse file into structured format",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "file_id": {"type": "string"},
                                            "parse_options": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "content.parse_file",
                            "semantic_api": "/api/v1/content-pillar/parse-file",
                            "user_journey": "parse_document"
                        }
                    },
                    {
                        "name": "content_analysis",
                        "protocol": "ContentAnalysisOrchestratorProtocol",
                        "description": "Analyze documents (structure, metadata, entities)",
                        "contracts": {
                            "soa_api": {
                                "api_name": "analyze_document",
                                "endpoint": "/api/v1/content-pillar/analyze-document",
                                "method": "POST",
                                "handler": self.analyze_document,
                                "metadata": {
                                    "description": "Analyze document structure, metadata, and entities",
                                    "parameters": ["document_id", "analysis_types"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "analyze_document_tool",
                                "tool_definition": {
                                    "name": "analyze_document_tool",
                                    "description": "Analyze document structure, metadata, and entities",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "document_id": {"type": "string"},
                                            "analysis_types": {"type": "array", "items": {"type": "string"}}
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "content.analyze_document",
                            "semantic_api": "/api/v1/content-pillar/analyze-document",
                            "user_journey": "analyze_document"
                        }
                    },
                    {
                        "name": "entity_extraction",
                        "protocol": "ContentAnalysisOrchestratorProtocol",
                        "description": "Extract entities from documents",
                        "contracts": {
                            "soa_api": {
                                "api_name": "extract_entities",
                                "endpoint": "/api/v1/content-pillar/extract-entities",
                                "method": "POST",
                                "handler": self.extract_entities,
                                "metadata": {
                                    "description": "Extract entities from document",
                                    "parameters": ["document_id"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "content.extract_entities",
                            "semantic_api": "/api/v1/content-pillar/extract-entities",
                            "user_journey": "extract_entities"
                        }
                    },
                    {
                        "name": "file_deletion",
                        "protocol": "ContentAnalysisOrchestratorProtocol",
                        "description": "Delete files",
                        "contracts": {
                            "soa_api": {
                                "api_name": "delete_file",
                                "endpoint": "/api/v1/content-pillar/delete-file/{file_id}",
                                "method": "DELETE",
                                "handler": self._delete_file_handler,
                                "metadata": {
                                    "description": "Delete a file",
                                    "parameters": ["file_id", "user_id"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "content.delete_file",
                            "semantic_api": "/api/v1/content-pillar/delete-file/{file_id}",
                            "user_journey": "delete_file"
                        }
                    }
                ],
                soa_apis=["handle_content_upload", "parse_file", "analyze_document", "extract_entities", "delete_file"],
                mcp_tools=["handle_content_upload_tool", "parse_file_tool", "analyze_document_tool"]
            )
            
            # Record health metric
            await self._realm_service.record_health_metric(
                "content_analysis_orchestrator_initialized",
                1.0,
                {"orchestrator": self.orchestrator_name}
            )
            
            # End telemetry tracking
            await self._realm_service.log_operation_with_telemetry(
                "content_analysis_orchestrator_initialize_complete",
                success=True
            )
            
            self.logger.info(f"✅ {self.orchestrator_name} initialized successfully")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self._realm_service.handle_error_with_audit(e, "content_analysis_orchestrator_initialize")
            
            # End telemetry tracking with failure
            await self._realm_service.log_operation_with_telemetry(
                "content_analysis_orchestrator_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Failed to initialize {self.orchestrator_name}: {e}")
            return False
    
    # ========================================================================
    # MVP USE CASE APIs (Preserve UI Integration)
    # ========================================================================
    
    async def analyze_document(
        self,
        document_id: str,
        analysis_types: List[str],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze document (MVP use case orchestration).
        
        OLD: ContentPillar.analyze_document() - internal micro-modules
        NEW: Delegates to enabling services
        
        This method preserves the API surface for the MVP UI.
        
        Includes full utility usage:
        - Telemetry tracking (start/complete)
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        
        Args:
            document_id: ID of document to analyze
            analysis_types: Types of analysis to perform (["structure", "metadata", "entities"])
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Analysis results in format expected by MVP UI
        """
        # Start telemetry tracking
        await self._realm_service.log_operation_with_telemetry(
            "analyze_document_start",
            success=True,
            details={"document_id": document_id, "analysis_types": analysis_types}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self._realm_service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "content_analysis", "execute"):
                        await self._realm_service.record_health_metric("analyze_document_access_denied", 1.0, {"document_id": document_id})
                        await self._realm_service.log_operation_with_telemetry("analyze_document_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to analyze document")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self._realm_service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        # Check if tenant has async validate_tenant_access method
                        if hasattr(tenant, 'validate_tenant_access'):
                            if asyncio.iscoroutinefunction(tenant.validate_tenant_access):
                                # For analyze_document, use user tenant for both (common case)
                                if not await tenant.validate_tenant_access(tenant_id, tenant_id):
                                    await self._realm_service.record_health_metric("analyze_document_tenant_denied", 1.0, {"document_id": document_id, "tenant_id": tenant_id})
                                    await self._realm_service.log_operation_with_telemetry("analyze_document_complete", success=False)
                                    raise PermissionError(f"Tenant access denied: {tenant_id}")
                            else:
                                # Synchronous method
                                if not tenant.validate_tenant_access(tenant_id, tenant_id):
                                    await self._realm_service.record_health_metric("analyze_document_tenant_denied", 1.0, {"document_id": document_id, "tenant_id": tenant_id})
                                    await self._realm_service.log_operation_with_telemetry("analyze_document_complete", success=False)
                                    raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            self.logger.info(f"📄 Analyzing document: {document_id} ({analysis_types})")
            results = {}
            
            # Delegate to enabling services (not internal micro-modules!)
            
            # 1. Structure analysis via FileParser
            if "structure" in analysis_types:
                file_parser = await self._get_file_parser_service()
                if file_parser:
                    parse_result = await file_parser.parse_file(document_id)
                    if parse_result.get("success"):
                        results["structure"] = {
                            "parsed": True,
                            "file_type": parse_result.get("file_type"),
                            "structure": parse_result.get("structure"),
                            "content_preview": parse_result.get("content", "")[:200]
                        }
                    else:
                        results["structure"] = {"error": "Parsing failed"}
                else:
                    results["structure"] = {"error": "File Parser service not available"}
            
            # 2. Metadata analysis via MetricsCalculator
            if "metadata" in analysis_types:
                file_parser = await self._get_file_parser_service()
                if file_parser:
                    metadata_result = await file_parser.extract_metadata(document_id)
                    if metadata_result.get("success"):
                        results["metadata"] = metadata_result.get("metadata", {})
                    else:
                        results["metadata"] = {"error": "Metadata extraction failed"}
                else:
                    results["metadata"] = {"error": "File Parser service not available"}
            
            # 3. Entity extraction via DataAnalyzer
            if "entities" in analysis_types:
                # Discover DataAnalyzerService via Curator
                data_analyzer = await self._get_data_analyzer_service()
                if data_analyzer:
                    entities_result = await data_analyzer.extract_entities(document_id)
                    if entities_result.get("success"):
                        results["entities"] = entities_result.get("entities", [])
                    else:
                        results["entities"] = {"error": "Entity extraction failed"}
                else:
                    results["entities"] = {"error": "Data Analyzer service not available"}
            
            # 4. Use Smart City services for lineage tracking (via Business Orchestrator's helpers)
            await self.track_data_lineage(
                source=document_id,
                destination=f"{document_id}_analysis",
                metadata={
                    "type": "content_analysis",
                    "analysis_types": analysis_types,
                    "orchestrator": "ContentAnalysisOrchestrator"
                }
            )
            
            self.logger.info(f"✅ Document analysis complete: {document_id}")
            
            # Record health metric (success)
            await self._realm_service.record_health_metric(
                "analyze_document_success",
                1.0,
                {"document_id": document_id, "analysis_types": analysis_types}
            )
            
            # End telemetry tracking
            await self._realm_service.log_operation_with_telemetry(
                "analyze_document_complete",
                success=True,
                details={"document_id": document_id, "analysis_types": analysis_types}
            )
            
            # Format response for MVP UI (preserves contract)
            return self._format_for_mvp_ui(results, document_id)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self._realm_service.handle_error_with_audit(e, "analyze_document")
            
            # Record health metric (failure)
            await self._realm_service.record_health_metric(
                "analyze_document_failed",
                1.0,
                {"document_id": document_id, "error": type(e).__name__}
            )
            
            # End telemetry tracking with failure
            await self._realm_service.log_operation_with_telemetry(
                "analyze_document_complete",
                success=False,
                details={"document_id": document_id, "error": str(e)}
            )
            
            self.logger.error(f"❌ Document analysis failed: {e}")
            return {
                "status": "error",
                "message": f"Document analysis failed: {str(e)}",
                "document_id": document_id,
                "error": str(e)
            }
    
    async def parse_file(
        self,
        file_id: str,
        parse_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parse file (MVP use case orchestration).
        
        OLD: ContentPillar.parse_file() - internal parsing
        NEW: Delegates to FileParserService (lazy initialization)
        
        Includes full utility usage:
        - Telemetry tracking (start/complete)
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        
        Args:
            file_id: ID of file to parse
            parse_options: Optional parsing configuration
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Parse results in format expected by MVP UI
        """
        # Start telemetry tracking
        await self._realm_service.log_operation_with_telemetry(
            "parse_file_start",
            success=True,
            details={"file_id": file_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self._realm_service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "content_parsing", "execute"):
                        await self._realm_service.record_health_metric("parse_file_access_denied", 1.0, {"file_id": file_id})
                        await self._realm_service.log_operation_with_telemetry("parse_file_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to parse file")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self._realm_service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        # Check if tenant has async validate_tenant_access method
                        if hasattr(tenant, 'validate_tenant_access'):
                            if asyncio.iscoroutinefunction(tenant.validate_tenant_access):
                                # For parse_file, use user tenant for both (common case)
                                if not await tenant.validate_tenant_access(tenant_id, tenant_id):
                                    await self._realm_service.record_health_metric("parse_file_tenant_denied", 1.0, {"file_id": file_id, "tenant_id": tenant_id})
                                    await self._realm_service.log_operation_with_telemetry("parse_file_complete", success=False)
                                    raise PermissionError(f"Tenant access denied: {tenant_id}")
                            else:
                                # Synchronous method
                                if not tenant.validate_tenant_access(tenant_id, tenant_id):
                                    await self._realm_service.record_health_metric("parse_file_tenant_denied", 1.0, {"file_id": file_id, "tenant_id": tenant_id})
                                    await self._realm_service.log_operation_with_telemetry("parse_file_complete", success=False)
                                    raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            # Get File Parser Service (lazy initialization)
            file_parser = await self._get_file_parser_service()
            if not file_parser:
                await self._realm_service.record_health_metric("parse_file_service_unavailable", 1.0, {"file_id": file_id})
                await self._realm_service.log_operation_with_telemetry("parse_file_complete", success=False, details={"file_id": file_id, "error": "service_unavailable"})
                return {
                    "status": "error",
                    "message": "File Parser service not available"
                }
            
            # Handle copybook_file_id in parse_options - retrieve copybook data if needed
            if parse_options and "copybook_file_id" in parse_options:
                copybook_file_id = parse_options.pop("copybook_file_id")
                try:
                    # Retrieve copybook file
                    copybook_doc = await self._realm_service.retrieve_document(copybook_file_id)
                    if copybook_doc:
                        copybook_data = copybook_doc.get("file_content") or copybook_doc.get("data")
                        if isinstance(copybook_data, str):
                            copybook_data = copybook_data.encode('utf-8')
                        elif not isinstance(copybook_data, bytes):
                            copybook_data = bytes(copybook_data) if copybook_data else b""
                        
                        # Add copybook data to parse_options
                        parse_options["copybook"] = copybook_data.decode('utf-8') if copybook_data else ""
                        self.logger.info(f"✅ Retrieved copybook data from file: {copybook_file_id}")
                    else:
                        self.logger.warning(f"⚠️ Copybook file not found: {copybook_file_id}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to retrieve copybook file {copybook_file_id}: {e}")
            
            result = await file_parser.parse_file(file_id, parse_options, user_context)
            
            # Record health metric (success)
            await self._realm_service.record_health_metric(
                "parse_file_success",
                1.0,
                {"file_id": file_id}
            )
            
            # End telemetry tracking
            await self._realm_service.log_operation_with_telemetry(
                "parse_file_complete",
                success=True,
                details={"file_id": file_id}
            )
            
            # Format for MVP UI
            return self._format_for_mvp_ui({"parse_result": result}, file_id)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self._realm_service.handle_error_with_audit(e, "parse_file")
            
            # Record health metric (failure)
            await self._realm_service.record_health_metric(
                "parse_file_failed",
                1.0,
                {"file_id": file_id, "error": type(e).__name__}
            )
            
            # End telemetry tracking with failure
            await self._realm_service.log_operation_with_telemetry(
                "parse_file_complete",
                success=False,
                details={"file_id": file_id, "error": str(e)}
            )
            
            self.logger.error(f"❌ File parsing failed: {e}")
            return {
                "status": "error",
                "message": f"File parsing failed: {str(e)}",
                "error": str(e)
            }
    
    async def extract_entities(self, document_id: str) -> Dict[str, Any]:
        """
        Extract entities (MVP use case orchestration).
        
        OLD: ContentPillar.extract_entities() - internal extraction
        NEW: Delegates to DataAnalyzerService
        
        Args:
            document_id: ID of document to extract entities from
        
        Returns:
            Extracted entities in format expected by MVP UI
        """
        try:
            # Delegate to DataAnalyzer (not internal implementation!)
            data_analyzer = await self._get_data_analyzer_service()
            if not data_analyzer:
                return {
                    "status": "error",
                    "message": "Data Analyzer service not available"
                }
            
            result = await data_analyzer.extract_entities(document_id)
            
            # Format for MVP UI
            return self._format_for_mvp_ui({"entities": result.get("entities", [])}, document_id)
            
        except Exception as e:
            self.logger.error(f"❌ Entity extraction failed: {e}")
            return {
                "status": "error",
                "message": f"Entity extraction failed: {str(e)}",
                "error": str(e)
            }
    
    async def handle_content_upload(
        self,
        file_data: bytes,
        filename: str,
        file_type: str,
        user_id: str = "api_user",
        session_id: Optional[str] = None,  # NEW: Session ID for workflow tracking
        user_context: Optional[Dict[str, Any]] = None  # NEW: User context (includes copybook_file_id, workflow_id, etc.)
    ) -> Dict[str, Any]:
        """
        Handle file upload (MVP use case orchestration).
        
        Delegates to Content Steward for file storage (GCS + Supabase).
        Requires Content Steward service to be available.
        
        Args:
            file_data: Binary file data
            filename: Original filename (e.g., "userfile.docx")
            file_type: MIME type (e.g., "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            user_id: User ID for ownership tracking
            session_id: Session ID for workflow tracking
        
        Returns:
            Upload result with file ID (UUID), ui_name, and metadata
        """
        try:
            from utilities.file_utils import (
                parse_filename,
                determine_content_type
            )
            
            # Validate file_data is not None
            if file_data is None:
                raise ValueError("file_data cannot be None - file upload requires binary data")
            
            file_size = len(file_data) if file_data else 0
            self.logger.info(f"📤 Handling content upload: {filename} ({file_size} bytes)")
            
            # Step 1: Parse filename
            file_components = parse_filename(filename)
            # Result: {
            #   "ui_name": "userfile",
            #   "file_extension": ".docx",
            #   "file_extension_clean": "docx",
            #   "original_filename": "userfile.docx"
            # }
            
            # Step 2: Determine content type
            # Check if user_context provides explicit content_type (from frontend selection)
            explicit_content_type = None
            explicit_file_type_category = None
            if user_context:
                explicit_content_type = user_context.get("content_type")
                explicit_file_type_category = user_context.get("file_type_category")
            
            if explicit_content_type and explicit_file_type_category:
                # Use explicit values from frontend
                content_info = {
                    "content_type": explicit_content_type,
                    "file_type_category": explicit_file_type_category
                }
                self.logger.info(f"📋 Using explicit content type from frontend: {explicit_content_type}/{explicit_file_type_category}")
            else:
                # Fallback to automatic detection
                content_info = determine_content_type(
                    file_components["file_extension"],
                    file_type
                )
            # Result: {
            #   "content_type": "unstructured" | "workflow_sop" | etc.,
            #   "file_type_category": "document" | "workflow" | "sop" | etc.
            # }
            
            # Track orchestrator workflow if session_id provided
            workflow_id = None
            # Session tracking handled via Traffic Cop (Smart City service)
            # Workflow tracking handled via Conductor (Smart City service)
            # No need for content_manager.session_manager or track_orchestrator_workflow
            if session_id:
                workflow_id = f"upload_{file_components['ui_name']}_{datetime.utcnow().timestamp()}"
                # Workflow tracking is handled by DataSolutionOrchestrator via platform correlation
                # No need to track here - it's handled upstream
            
            # ========================================================================
            # Use Content Steward directly (Content realm service)
            # ========================================================================
            # ContentJourneyOrchestrator is called BY DataSolutionOrchestratorService.
            # So we should NOT call DataSolutionOrchestratorService here (that would create a circular dependency).
            # Instead, call Content Steward directly for file storage.
            # ========================================================================
            
            # Use Data Steward for proper file storage (GCS + Supabase)
            # Access via OrchestratorBase (delegates to RealmServiceBase)
            # Note: Content Steward consolidated into Data Steward
            data_steward = await self.get_data_steward_api()
            
            if not data_steward:
                raise Exception("Data Steward service not available - file upload requires infrastructure")
            
            # Step 3: Prepare metadata for Content Steward with proper field names
            # Check if this is an SOP/Workflow file that should be processed in Operations Pillar
            processing_pillar = None
            parsing_type = None
            if (content_info["content_type"] == "workflow_sop" or 
                content_info["file_type_category"] in ["sop_workflow", "workflow", "sop"]):
                processing_pillar = "operations_pillar"
                # Determine parsing type based on file extension
                file_ext = file_components["file_extension_clean"].lower()
                if file_ext in ["bpmn", "json", "drawio"]:
                    parsing_type = "workflow"
                elif file_ext in ["docx", "pdf", "txt", "md"]:
                    parsing_type = "sop"
                else:
                    parsing_type = "sop"  # Default to sop for unknown types
                self.logger.info(f"📋 File marked for Operations Pillar processing: {filename} (parsing_type: {parsing_type})")
            
            # Extract copybook_file_id from user_context if provided (uploaded before main file)
            copybook_file_id = None
            if user_context and user_context.get("copybook_file_id"):
                copybook_file_id = user_context.get("copybook_file_id")
                self.logger.info(f"📎 Including copybook_file_id in metadata: {copybook_file_id}")
            
            metadata = {
                "user_id": user_id,
                "ui_name": file_components["ui_name"],  # ✅ Correct field name
                "file_type": file_components["file_extension_clean"],  # ✅ Extension, not MIME
                "mime_type": file_type,  # ✅ MIME type separately
                "original_filename": file_components["original_filename"],  # ✅ Full original name
                "file_extension": file_components["file_extension"],  # ✅ Extension with dot
                "content_type": content_info["content_type"],  # ✅ For Supabase schema
                "file_type_category": content_info["file_type_category"],  # ✅ For processing logic
                "processing_pillar": processing_pillar,  # ✅ Mark for Operations Pillar if SOP/Workflow
                "parsing_type": parsing_type,  # ✅ NEW: workflow or sop (for Operations Pillar)
                "uploaded_at": datetime.utcnow().isoformat(),
                "size_bytes": len(file_data)
            }
            
            # Add copybook_file_id to metadata if provided
            if copybook_file_id:
                metadata["copybook_file_id"] = copybook_file_id
            
            upload_result = await data_steward.process_upload(file_data, file_type, metadata)
            
            # Extract file_id from result
            file_uuid = upload_result.get("uuid") or upload_result.get("file_id")
            
            # Common processing
            if upload_result.get("success") or upload_result.get("status") == "success" or file_uuid:
                self.logger.info(f"✅ File uploaded via Content Steward (GCS + Supabase): {filename}")
                
                # Ensure we have file_uuid (already extracted above, but double-check)
                if not file_uuid:
                    file_uuid = upload_result.get("uuid") or upload_result.get("file_id")
                
                if not file_uuid:
                    raise Exception("File upload failed: no UUID returned")
                
                # Update workflow status to completed
                # Session tracking handled via Traffic Cop (Smart City service)
                # Workflow tracking handled via Conductor (Smart City service)
                # No need for content_manager.session_manager or track_orchestrator_workflow
                # Workflow tracking is handled by DataSolutionOrchestrator via platform correlation
                if session_id and workflow_id:
                    # Workflow completion is tracked upstream by DataSolutionOrchestrator
                    pass
                
                # Step 5: Return with proper field names
                return_dict = {
                    "success": True,
                    "file_id": file_uuid,
                    "uuid": file_uuid,
                    "workflow_id": workflow_id,  # Return workflow_id for frontend
                    "orchestrator": "ContentAnalysisOrchestrator",
                    "ui_name": file_components["ui_name"],
                    "original_filename": file_components["original_filename"],
                    "file_extension": file_components["file_extension"],
                    "file_type": file_components["file_extension_clean"],
                    "mime_type": file_type,
                    "content_type": content_info["content_type"],
                    "file_type_category": content_info["file_type_category"],
                    "processing_pillar": processing_pillar,
                    "size": len(file_data),
                    "message": "File uploaded successfully" + (f" (will be processed in {processing_pillar})" if processing_pillar else ""),
                    "mode": "gcs_supabase"
                }
                
                return return_dict
            else:
                error_msg = upload_result.get("error") or upload_result.get("message") or "Unknown error"
                raise Exception(f"Content Steward upload failed: {error_msg}")
            
        except Exception as e:
            self.logger.error(f"❌ File upload failed: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"File upload failed: {str(e)}",
                "error": str(e)
            }
    
    # ========================================================================
    # FRONTEND GATEWAY API COMPATIBILITY METHODS
    # ========================================================================
    
    async def upload_file(
        self,
        file_data: bytes,
        filename: str,
        file_type: str,
        user_id: str = "api_user",
        session_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload file (Frontend Gateway API compatibility wrapper).
        
        Wraps handle_content_upload() for FrontendGatewayService compatibility.
        
        Args:
            file_data: File binary data
            filename: Original filename
            file_type: MIME type
            user_id: User identifier
            session_id: Optional session ID
            user_context: Optional user context (includes copybook_file_id, workflow_id, etc.)
        
        Returns:
            Upload result with file metadata
        """
        return await self.handle_content_upload(
            file_data=file_data,
            filename=filename,
            file_type=file_type,
            user_id=user_id,
            session_id=session_id,
            user_context=user_context
        )
    
    async def process_file(
        self,
        file_id: str,
        user_id: str,
        copybook_file_id: Optional[str] = None,
        processing_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process file (parsing + metadata extraction) with optional Saga guarantees.
        
        ✅ ContentJourneyOrchestrator is called BY DataSolutionOrchestratorService.
        So we should NOT call DataSolutionOrchestratorService here (that would create a circular dependency).
        Instead, call FileParserService and other Content realm services directly.
        
        Args:
            file_id: File UUID
            user_id: User identifier
            copybook_file_id: Optional copybook file UUID
            processing_options: Optional processing options
        
        Returns:
            Processing result with parsed data, metadata, and saga_id (if Saga was used)
        """
        # ✅ Get user context from request-scoped context
        from utilities.security_authorization.request_context import get_request_user_context
        ctx = get_request_user_context()
        
        if ctx:
            self.logger.debug(f"✅ [process_file] Using user context: user_id={ctx.get('user_id')}, tenant_id={ctx.get('tenant_id')}, permissions={ctx.get('permissions')}")
        else:
            self.logger.warning(f"⚠️ [process_file] No user context available in request context")
        
        # Prepare user context for Saga
        user_context = {
            "user_id": user_id,
            "file_id": file_id,
            "copybook_file_id": copybook_file_id,
            "processing_options": processing_options
        }
        if ctx:
            user_context.update(ctx)
        
        # Define milestones for file processing operation
        milestones = ["parse", "store_parsed", "embed"]
        
        # Execute with Saga if enabled
        return await self._execute_with_saga(
            operation="content_process_file",
            workflow_func=lambda: self._execute_process_file_workflow(
                file_id=file_id,
                user_id=user_id,
                copybook_file_id=copybook_file_id,
                processing_options=processing_options,
                user_context=user_context
            ),
            milestones=milestones,
            user_context=user_context
        )
    
    async def _execute_process_file_workflow(
        self,
        file_id: str,
        user_id: str,
        copybook_file_id: Optional[str] = None,
        processing_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute file processing workflow (called by Saga or directly).
        
        This is the actual workflow implementation, extracted for reuse.
        
        Args:
            file_id: File UUID
            user_id: User identifier
            copybook_file_id: Optional copybook file UUID
            processing_options: Optional processing options
            user_context: Optional user context
        
        Returns:
            Processing result with parsed data and metadata
        """
        try:
            self.logger.info(f"⚙️ Processing file: {file_id}")
            
            # ========================================================================
            # Call FileParserService directly (Content realm service)
            # ========================================================================
            # ContentJourneyOrchestrator is called BY DataSolutionOrchestratorService
            # So we should NOT call DataSolutionOrchestratorService here (that would create a circular dependency)
            # Instead, call FileParserService directly
            # ========================================================================
            
            # Get FileParserService (Content realm service)
            file_parser = await self._get_file_parser_service()
            if not file_parser:
                return {
                    "success": False,
                    "file_id": file_id,
                    "error": "FileParserService not available - parsing requires FileParserService"
                }
            
            # Retrieve copybook_file_id from file metadata if not provided as parameter
            if not copybook_file_id:
                try:
                    data_steward = await self.get_data_steward_api()
                    if data_steward:
                        file_info = await data_steward.get_file(file_id)
                        if file_info:
                            # Check metadata for copybook_file_id
                            metadata = file_info.get("metadata") or file_info.get("service_context") or {}
                            copybook_file_id = metadata.get("copybook_file_id")
                            if copybook_file_id:
                                self.logger.info(f"📎 Retrieved copybook_file_id from file metadata: {copybook_file_id}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to retrieve copybook_file_id from metadata: {e}")
            
            # Prepare parse options
            # FileParserService will handle copybook_file_id loading (best practice: service owns its concerns)
            parse_options = processing_options or {}
            if copybook_file_id:
                parse_options["copybook_file_id"] = copybook_file_id
            
            # Parse file via FileParserService
            # FileParserService will load copybook content from copybook_file_id if present
            parse_result = await file_parser.parse_file(
                file_id=file_id,
                parse_options=parse_options,
                user_context={"user_id": user_id}  # Minimal user_context for parsing
            )
            
            if not parse_result.get("success"):
                # ✅ CRITICAL: Return error immediately if parsing fails - don't set parsed_file_id
                error_msg = parse_result.get("error", "File parsing failed")
                self.logger.error(f"❌ File parsing failed: {error_msg}")
                return {
                    "success": False,
                    "file_id": file_id,
                    "error": error_msg,
                    "parse_result": parse_result,
                    "parsed_file_id": None,  # ✅ Explicitly None when parsing fails
                    "message": f"File parsing failed: {error_msg}. Please check the file format and try again."
                }
            
            # ========================================================================
            # Convert parsed data to JSONL and store via Content Steward
            # ========================================================================
            # ✅ CRITICAL: Only set parsed_file_id if storage actually succeeds
            # This ensures we don't return success when storage fails
            parsed_file_id = None
            storage_error = None
            content_type = parse_result.get("parsing_type", "structured")  # structured, unstructured, hybrid
            
            # Only save as JSONL for structured data (has tables/records)
            if content_type == "structured" and parse_result.get("success"):
                self.logger.info(f"🔍 [process_file] Attempting JSONL conversion for structured data. content_type={content_type}, success={parse_result.get('success')}")
                try:
                    # Convert parsed data to JSONL bytes (simple, flexible, AI-friendly)
                    self.logger.info(f"🔍 [process_file] Calling _convert_to_jsonl_bytes with parse_result keys: {list(parse_result.keys())}")
                    jsonl_bytes = await self._convert_to_jsonl_bytes(parse_result)
                    
                    if not jsonl_bytes:
                        storage_error = "Failed to convert parsed data to JSONL bytes - conversion returned None"
                        self.logger.error(f"❌ {storage_error}")
                        # Return error - don't continue if conversion fails
                        return {
                            "success": False,
                            "file_id": file_id,
                            "error": storage_error,
                            "parse_result": parse_result,
                            "parsed_file_id": None,  # ✅ Explicitly None when storage fails
                            "message": "Parsing succeeded but storage failed. Please try again or contact support if the issue persists."
                        }
                    
                    self.logger.info(f"✅ [process_file] JSONL conversion successful: {len(jsonl_bytes)} bytes")
                    
                    # Get Content Steward API
                    data_steward = await self.get_data_steward_api()
                    if not data_steward:
                        storage_error = "Content Steward service not available - cannot store parsed file"
                        self.logger.error(f"❌ {storage_error}")
                        # Return error - don't continue if Content Steward is unavailable
                        return {
                            "success": False,
                            "file_id": file_id,
                            "error": storage_error,
                            "parse_result": parse_result,
                            "parsed_file_id": None,  # ✅ Explicitly None when storage fails
                            "message": "Parsing succeeded but storage service is unavailable. Please try again or contact support."
                        }
                    
                    self.logger.info(f"✅ [process_file] Content Steward available, storing parsed file...")
                    # Store parsed file via Content Steward
                    store_result = await data_steward.store_parsed_file(
                        file_id=file_id,
                        parsed_file_data=jsonl_bytes,
                        format_type="jsonl",  # JSONL format (was "parquet")
                        content_type=content_type,
                        parse_result=parse_result,
                        workflow_id=None
                    )
                    
                    if not store_result:
                        storage_error = "store_parsed_file returned None - storage failed"
                        self.logger.error(f"❌ {storage_error}")
                        # Return error - don't continue if storage returns None
                        return {
                            "success": False,
                            "file_id": file_id,
                            "error": storage_error,
                            "parse_result": parse_result,
                            "parsed_file_id": None,  # ✅ Explicitly None when storage fails
                            "message": "Parsing succeeded but file storage failed. Please try again or contact support if the issue persists."
                        }
                    
                    # store_parsed_file returns parsed_file_id at top level (for backward compatibility)
                    parsed_file_id = (
                        store_result.get("parsed_file_id") or
                        store_result.get("data", {}).get("parsed_file_id")  # Fallback to nested format
                    )
                    
                    if not parsed_file_id:
                        storage_error = f"store_parsed_file did not return parsed_file_id. Result keys: {list(store_result.keys())}"
                        self.logger.error(f"❌ {storage_error}")
                        # Return error - don't continue if parsed_file_id is missing
                        return {
                            "success": False,
                            "file_id": file_id,
                            "error": storage_error,
                            "parse_result": parse_result,
                            "parsed_file_id": None,  # ✅ Explicitly None when storage fails
                            "message": "Parsing succeeded but storage did not return a file ID. Please try again or contact support."
                        }
                    
                    self.logger.info(f"✅ Stored parsed file as JSONL: parsed_file_id={parsed_file_id}")
                    
                    # Update original file status to "parsed" after successful parsing
                    # Note: This is non-critical - if it fails, we still return success since storage succeeded
                    try:
                        data_steward = await self.get_data_steward_api()
                        if data_steward:
                            # Get user context
                            ctx = get_request_user_context()
                            if not ctx:
                                ctx = {"user_id": user_id}
                            
                            await data_steward.update_file_metadata(
                                file_id=file_id,
                                metadata_updates={"status": "parsed"},
                                user_context=ctx
                            )
                            self.logger.info(f"✅ Updated file status to 'parsed': file_id={file_id}")
                        else:
                            self.logger.warning(f"⚠️ Content Steward not available - cannot update file status (non-critical)")
                    except Exception as status_error:
                        self.logger.warning(f"⚠️ Failed to update file status to 'parsed': {status_error} (non-critical)")
                        # Don't fail the entire operation if status update fails - storage already succeeded
                        
                except Exception as e:
                    storage_error = f"Exception during parsed file storage: {str(e)}"
                    self.logger.error(f"❌ {storage_error}", exc_info=True)
                    # Return error - don't continue if storage exception occurs
                    return {
                        "success": False,
                        "file_id": file_id,
                        "error": storage_error,
                        "parse_result": parse_result,
                        "parsed_file_id": None,  # ✅ Explicitly None when storage fails
                        "message": f"Parsing succeeded but storage failed with exception: {str(e)}. Please try again or contact support."
                    }
            else:
                # For non-structured data or if parsing didn't succeed, we don't store
                # This is expected behavior - return success with parsed_file_id=None
                self.logger.info(f"ℹ️ Skipping JSONL storage: content_type={content_type}, success={parse_result.get('success')}")
                if not parse_result.get("success"):
                    # If parsing itself failed, return error
                    return {
                        "success": False,
                        "file_id": file_id,
                        "error": parse_result.get("error", "File parsing failed"),
                        "parse_result": parse_result,
                        "parsed_file_id": None,  # ✅ Explicitly None when parsing fails
                        "message": "File parsing failed. Please check the file format and try again."
                    }
            
            # Get file details (includes metadata)
            file_details = await self.get_file_details(file_id, user_id)
            
            # Create summary response (exclude full data to avoid huge JSON responses)
            # Full data is stored in parquet/GCS - frontend can retrieve via separate endpoint
            parse_summary = {
                "success": parse_result.get("success", True),
                "parsing_type": parse_result.get("parsing_type"),
                "file_type": parse_result.get("file_type"),
                "structure": parse_result.get("structure", {}),
                "metadata": parse_result.get("metadata", {}),
                "record_count": len(parse_result.get("records", [])) if parse_result.get("records") else 0,
                "table_count": len(parse_result.get("tables", [])) if parse_result.get("tables") else 0,
                "parsed_at": parse_result.get("parsed_at"),
                # Exclude full data/records/tables to keep response size manageable
                "note": "Full parsed data available via separate endpoint. Use parsed_file_id to retrieve."
            }
            
            # Include validation if present (for binary files with 88 codes / ASCII level-01 metadata)
            if "validation" in parse_result:
                parse_summary["validation"] = parse_result["validation"]
            
            # ✅ CRITICAL: Only return success if parsed_file_id is set (storage succeeded)
            # If parsed_file_id is None, we should have already returned an error above
            if not parsed_file_id:
                # This should not happen if error handling above is correct, but add safety check
                self.logger.error(f"❌ CRITICAL: parsed_file_id is None but we reached end of function - this should not happen")
                return {
                    "success": False,
                    "file_id": file_id,
                    "error": "Parsed file storage failed - parsed_file_id is None",
                    "parse_result": parse_summary,
                    "parsed_file_id": None,  # ✅ Explicitly None
                    "message": "Parsing completed but storage failed. Please try again or contact support."
                }
            
            # Combine results - only reached if storage succeeded
            result = {
                "success": True,
                "file_id": file_id,
                "parse_result": parse_summary,  # Summary only, not full data
                "parsed_file_id": parsed_file_id,  # ✅ Only set if storage succeeded
                "file_details": file_details.get("file", {}),
                "copybook_file_id": copybook_file_id,
                "message": "Parsing and storage completed successfully via FileParserService",
                "note": "Full parsed data stored as JSONL in GCS. Use parsed_file_id to retrieve. To create semantic layer (embeddings), use create-embeddings endpoint with parsed_file_id."
            }
            
            self.logger.info(f"✅ File processing completed successfully: file_id={file_id}, parsed_file_id={parsed_file_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ File processing failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "file_id": file_id,
                "error": str(e)
            }
    
    async def create_embeddings(
        self,
        parsed_file_id: str,
        user_id: str,
        file_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create embeddings from parsed file (semantic layer creation).
        
        This implements the Data Mash vision: 3-layer semantic embeddings pattern.
        Users select a parsed file and explicitly trigger embedding creation.
        
        Architecture Pattern:
        - ContentJourneyOrchestrator is called BY DataSolutionOrchestratorService
        - ContentJourneyOrchestrator should NOT call DataSolutionOrchestratorService (avoids circular dependency)
        - ContentJourneyOrchestrator calls Content realm services directly (EmbeddingService)
        
        Args:
            parsed_file_id: Parsed file identifier (JSONL in GCS)
            user_id: User identifier
            file_id: Optional file UUID (for correlation)
            user_context: Optional user context (includes workflow_id, tenant_id, etc.)
        
        Returns:
            Dict with success status, content_id, embeddings_count
        """
        try:
            self.logger.info(f"🧬 Creating embeddings: parsed_file_id={parsed_file_id}, file_id={file_id}")
            
            # Get parsed file metadata to build content_metadata
            # We need to get the parse result to build proper content_metadata
            data_steward = await self.get_data_steward_api()
            if not data_steward:
                return {
                    "success": False,
                    "error": "ContentSteward not available",
                    "content_id": None,
                    "embeddings_count": 0
                }
            
            # Get parsed file (includes metadata with parse_result)
            parsed_file = await data_steward.get_parsed_file(parsed_file_id, user_context)
            if not parsed_file:
                return {
                    "success": False,
                    "error": f"Parsed file not found: {parsed_file_id}",
                    "content_id": None,
                    "embeddings_count": 0
                }
            
            # Extract parse result metadata from stored metadata
            # get_parsed_file() returns: {parsed_file_id, metadata: {parsed_file_metadata}, file_data, ...}
            # parse_result is stored in parsed_file_metadata (from Supabase parsed_data_files table)
            parsed_file_metadata = parsed_file.get("metadata", {})
            parse_result_metadata = parsed_file_metadata.get("parse_result", {}) or {}
            if not parse_result_metadata:
                # Fallback: try to get from top level
                parse_result_metadata = parsed_file.get("parse_result", {}) or {}
            
            # Pre-check: Verify required dependencies are available before initializing EmbeddingService
            self.logger.info("🔧 Checking EmbeddingService dependencies...")
            
            # Get ConfigAdapter from PublicWorksFoundationService (required)
            config_adapter = self._get_config_adapter()
            hf_endpoint = config_adapter.get("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
            hf_api_key = config_adapter.get("HUGGINGFACE_EMBEDDINGS_API_KEY") or config_adapter.get("HUGGINGFACE_API_KEY")
            
            if not hf_endpoint or not hf_api_key:
                self.logger.error("❌ HuggingFace configuration missing - HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL and HUGGINGFACE_EMBEDDINGS_API_KEY required")
                return {
                    "success": False,
                    "error": "HuggingFace embedding service not configured. Please set HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL and HUGGINGFACE_EMBEDDINGS_API_KEY environment variables.",
                    "content_id": None,
                    "embeddings_count": 0
                }
            
            # Check SemanticDataAbstraction availability
            semantic_data = self.get_abstraction("semantic_data")
            if not semantic_data:
                self.logger.error("❌ SemanticDataAbstraction not available - cannot store embeddings")
                return {
                    "success": False,
                    "error": "Semantic data storage not available. Please check Platform Gateway configuration.",
                    "content_id": None,
                    "embeddings_count": 0
                }
            
            # Get EmbeddingService (Content realm service)
            # Note: We call Content realm services directly, not through Data Solution Orchestrator
            self.logger.info("🔧 Initializing EmbeddingService...")
            try:
                from backend.content.services.embedding_service.embedding_service import EmbeddingService
                
                embedding_service = EmbeddingService(
                    service_name="EmbeddingService",
                    realm_name="content",  # ✅ Content realm service
                    platform_gateway=self.platform_gateway,
                    di_container=self.di_container
                )
                
                # Initialize with timeout protection
                import asyncio
                try:
                    # Set a timeout for initialization (30 seconds)
                    init_result = await asyncio.wait_for(
                        embedding_service.initialize(),
                        timeout=30.0
                    )
                    if not init_result:
                        raise Exception("EmbeddingService initialization returned False - check logs for missing dependencies")
                    self.logger.info("✅ EmbeddingService initialized (Content realm)")
                except asyncio.TimeoutError:
                    raise Exception("EmbeddingService initialization timed out after 30 seconds - check HuggingFaceAdapter and SemanticDataAbstraction availability")
            except Exception as init_error:
                self.logger.error(f"❌ EmbeddingService initialization failed: {init_error}", exc_info=True)
                return {
                    "success": False,
                    "error": f"Failed to initialize EmbeddingService: {str(init_error)}",
                    "content_id": None,
                    "embeddings_count": 0
                }
            
            # Prepare content metadata from parsed file metadata
            # Get file_id from parsed_file_metadata (from Supabase)
            file_id_from_metadata = parsed_file_metadata.get("file_id") or parsed_file.get("file_id")
            final_file_id = file_id or file_id_from_metadata
            
            # Determine parsing type from parse result
            parsing_type = parse_result_metadata.get("parsing_type") or parsed_file_metadata.get("content_type", "structured")
            
            # Build content_metadata based on parsing type
            if parsing_type in ["workflow", "sop"]:
                # For workflow/SOP, include structure-specific metadata
                content_metadata = {
                    "file_id": final_file_id,
                    "parsed_file_id": parsed_file_id,
                    "parsing_type": parsing_type,
                    "file_type": parse_result_metadata.get("file_type"),
                    "structure": parse_result_metadata.get("structure", {}),
                    "metadata": parse_result_metadata.get("metadata", {}),
                    # Workflow-specific
                    "node_count": parse_result_metadata.get("structure", {}).get("nodes", []) and len(parse_result_metadata.get("structure", {}).get("nodes", [])) or 0,
                    "edge_count": parse_result_metadata.get("structure", {}).get("edges", []) and len(parse_result_metadata.get("structure", {}).get("edges", [])) or 0,
                    # SOP-specific
                    "section_count": parse_result_metadata.get("structure", {}).get("sections", []) and len(parse_result_metadata.get("structure", {}).get("sections", [])) or 0,
                    "step_count": sum(len(s.get("steps", [])) for s in parse_result_metadata.get("structure", {}).get("sections", [])) if parse_result_metadata.get("structure", {}).get("sections") else 0,
                    "role_count": len(parse_result_metadata.get("structure", {}).get("roles", [])) if parse_result_metadata.get("structure", {}).get("roles") else 0
                }
            else:
                # For structured/unstructured/hybrid, use existing format
                content_metadata = {
                    "file_id": final_file_id,
                    "parsed_file_id": parsed_file_id,
                    "parsing_type": parsing_type,
                    "file_type": parse_result_metadata.get("file_type"),
                    "structure": parse_result_metadata.get("structure", {}),
                    "metadata": parse_result_metadata.get("metadata", {}),
                    "record_count": parse_result_metadata.get("record_count") or parsed_file_metadata.get("row_count", 0),
                    "table_count": parse_result_metadata.get("table_count", 0)
                }
            
            # Prepare user context
            if not user_context:
                user_context = {}
            user_context["user_id"] = user_id
            
            # ⭐ NEW: Get solution context for enhanced embedding creation (Phase 5.2)
            session_id = user_context.get("session_id")
            if session_id:
                try:
                    mvp_orchestrator = await self._get_mvp_journey_orchestrator()
                    if mvp_orchestrator:
                        solution_context = await mvp_orchestrator.get_solution_context(session_id)
                        if solution_context:
                            user_context["solution_context"] = solution_context
                            self.logger.debug(f"✅ Solution context retrieved for embedding creation: {session_id}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to get solution context for embedding creation: {e}")
                    # Continue without solution context - not critical
            
            # Create representative embeddings
            embedding_result = await embedding_service.create_representative_embeddings(
                parsed_file_id=parsed_file_id,
                content_metadata=content_metadata,
                sampling_strategy="every_nth",
                n=10,  # Every 10th row
                user_context=user_context
            )
            
            if not embedding_result.get("success"):
                self.logger.error(f"❌ Embedding creation failed: {embedding_result.get('error')}")
                return {
                    "success": False,
                    "error": embedding_result.get("error", "Embedding creation failed"),
                    "content_id": None,
                    "embeddings_count": 0
                }
            
            content_id = embedding_result.get("content_id")
            embeddings_count = embedding_result.get("embeddings_count", 0) or embedding_result.get("stored_count", 0)
            
            # Validate that we got a content_id and embeddings_count
            if not content_id:
                self.logger.error(f"❌ Embedding creation returned no content_id. Result: {embedding_result}")
                return {
                    "success": False,
                    "error": "Embedding creation did not return a content_id",
                    "content_id": None,
                    "embeddings_count": 0,
                    "file_id": final_file_id,
                    "parsed_file_id": parsed_file_id
                }
            
            if embeddings_count == 0:
                self.logger.warning(f"⚠️ Embedding creation returned 0 embeddings. Result: {embedding_result}")
            
            self.logger.info(f"✅ Created {embeddings_count} embeddings for content {content_id}")
            
            # ✅ Track lineage: file_id → parsed_file_id → content_id
            # This enables end-to-end traceability from upload → parse → embed → expose
            try:
                data_steward = await self.get_data_steward_api()
                if data_steward:
                    workflow_id = user_context.get("workflow_id") if user_context else None
                    lineage_data = {
                        "operation": "create_embeddings",
                        "parent_asset_id": parsed_file_id,
                        "parent_asset_type": "parsed_file",
                        "child_asset_id": content_id,
                        "child_asset_type": "content",
                        "relationship": "parsed_file_to_content",
                        "metadata": {
                            "file_id": final_file_id,
                            "parsed_file_id": parsed_file_id,
                            "content_id": content_id,
                            "embeddings_count": embeddings_count,
                            "parsing_type": parsing_type
                        }
                    }
                    
                    # Track lineage with correlation IDs
                    await data_steward.track_lineage(
                        lineage_data=lineage_data,
                        user_context={
                            **(user_context or {}),
                            "workflow_id": workflow_id,
                            "user_id": user_id,
                            "file_id": final_file_id,
                            "parsed_file_id": parsed_file_id,
                            "content_id": content_id
                        }
                    )
                    self.logger.info(f"✅ Tracked lineage: {parsed_file_id} → {content_id} (workflow_id: {workflow_id})")
                else:
                    self.logger.warning("⚠️ DataSteward not available - lineage tracking skipped (non-critical)")
            except Exception as lineage_error:
                self.logger.warning(f"⚠️ Lineage tracking failed: {lineage_error} (non-critical)")
                # Don't fail the operation if lineage tracking fails
            
            # ✅ Ensure workflow_id is in response for end-to-end correlation
            workflow_id = user_context.get("workflow_id") if user_context else None
            
            return {
                "success": True,
                "content_id": content_id,
                "embeddings_count": embeddings_count,
                "file_id": final_file_id,
                "parsed_file_id": parsed_file_id,
                "workflow_id": workflow_id,  # ✅ Include workflow_id for correlation
                "message": f"Successfully created {embeddings_count} embedding{'s' if embeddings_count != 1 else ''}"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create embeddings: {e}", exc_info=True)
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "content_id": None,
                "embeddings_count": 0
            }
    
    async def list_uploaded_files(self, user_id: str) -> Dict[str, Any]:
        """
        List uploaded files for user (File Dashboard).
        
        Uses ContentStewardService (Smart City service) to query files.
        ContentStewardService has proper realm access to file_management.
        
        Args:
            user_id: User identifier
        
        Returns:
            List of uploaded files with metadata
        """
        try:
            self.logger.info(f"📋 Listing uploaded files for user: {user_id}")
            
            # Get ContentStewardService via Curator (Smart City service - has proper realm access)
            data_steward = await self.get_data_steward_api()
            if not data_steward:
                return {
                    "success": False,
                    "files": [],
                    "count": 0,
                    "error": "Content Steward service not available"
                }
            
            # List files for user via ContentStewardService
            # ContentStewardService.list_files() handles realm permissions properly
            try:
                user_context = {"user_id": user_id}
                files = await data_steward.list_files(
                    filters={"user_id": user_id},
                    user_context=user_context
                )
                
                # Format files for frontend
                formatted_files = []
                for file_doc in files:
                    formatted_files.append({
                        "file_id": file_doc.get("uuid") or file_doc.get("file_id"),
                        "uuid": file_doc.get("uuid") or file_doc.get("file_id"),
                        "ui_name": file_doc.get("ui_name", file_doc.get("filename", "")),
                        "original_filename": file_doc.get("original_filename", file_doc.get("filename", "")),
                        "file_type": file_doc.get("file_type", ""),
                        "mime_type": file_doc.get("mime_type", ""),
                        "content_type": file_doc.get("content_type", ""),
                        "size_bytes": file_doc.get("size_bytes", file_doc.get("file_size", 0)),
                        "uploaded_at": file_doc.get("uploaded_at", file_doc.get("created_at", "")),
                        "parsed": file_doc.get("parsed", False)
                    })
                
                self.logger.info(f"✅ Found {len(formatted_files)} files for user: {user_id}")
                
                return {
                    "success": True,
                    "files": formatted_files,
                    "count": len(formatted_files)
                }
                
            except Exception as query_error:
                self.logger.error(f"❌ File listing failed: {query_error}")
                return {
                    "success": False,
                    "files": [],
                    "count": 0,
                    "error": f"Failed to list files: {str(query_error)}"
                }
            
        except Exception as e:
            self.logger.error(f"❌ List uploaded files failed: {e}")
            return {
                "success": False,
                "files": [],
                "count": 0,
                "error": str(e)
            }
    
    async def get_file_details(self, file_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get file details including metadata (File Details + Metadata Preview).
        
        Uses Content Steward to get file metadata from Supabase.
        
        Args:
            file_id: File UUID
            user_id: User identifier
        
        Returns:
            File details with metadata
        """
        try:
            self.logger.info(f"🔍 Getting file details: {file_id}")
            
            # Use RealmServiceBase.retrieve_document() which uses Content Steward
            file_doc = await self._realm_service.retrieve_document(file_id)
            
            if not file_doc:
                return {
                    "success": False,
                    "file": None,
                    "error": "File not found"
                }
            
            # Format for frontend
            file_details = {
                "file_id": file_id,
                "uuid": file_doc.get("uuid", file_id),
                "ui_name": file_doc.get("ui_name", file_doc.get("filename", "")),
                "original_filename": file_doc.get("original_filename", file_doc.get("filename", "")),
                "file_type": file_doc.get("file_type", ""),
                "mime_type": file_doc.get("mime_type", ""),
                "content_type": file_doc.get("content_type", ""),
                "size_bytes": file_doc.get("size_bytes", 0),
                "uploaded_at": file_doc.get("uploaded_at", ""),
                "metadata": file_doc.get("metadata", {}),
                "parsed": file_doc.get("parsed", False),
                "parse_result": file_doc.get("parse_result", {})
            }
            
            self.logger.info(f"✅ File details retrieved: {file_id}")
            
            return {
                "success": True,
                "file": file_details
            }
            
        except Exception as e:
            self.logger.error(f"❌ Get file details failed: {e}")
            return {
                "success": False,
                "file": None,
                "error": str(e)
            }
    
    async def process_documents(
        self,
        file_ids: List[str],
        user_id: str,
        processing_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Batch process multiple documents (Frontend API).
        
        Processes multiple files in batch: parse, analyze, extract entities.
        
        Args:
            file_ids: List of file IDs to process
            user_id: User identifier
            processing_options: Optional processing configuration
        
        Returns:
            Batch processing results
        """
        try:
            self.logger.info(f"📦 Batch processing {len(file_ids)} documents for user: {user_id}")
            
            processing_options = processing_options or {}
            results = []
            errors = []
            
            # Process each file
            for file_id in file_ids:
                try:
                    # Parse file
                    parse_result = await self.parse_file(
                        file_id=file_id,
                        parse_options=processing_options.get("parse_options")
                    )
                    
                    # Analyze document
                    analysis_result = await self.analyze_document(
                        document_id=file_id,
                        analysis_types=processing_options.get("analysis_types", ["structure", "metadata", "entities"])
                    )
                    
                    # Extract entities
                    entities_result = await self.extract_entities(document_id=file_id)
                    
                    results.append({
                        "file_id": file_id,
                        "success": True,
                        "parse_result": parse_result,
                        "analysis_result": analysis_result,
                        "entities_result": entities_result
                    })
                    
                except Exception as file_error:
                    self.logger.error(f"❌ Failed to process file {file_id}: {file_error}")
                    errors.append({
                        "file_id": file_id,
                        "error": str(file_error)
                    })
            
            self.logger.info(f"✅ Batch processing complete: {len(results)} successful, {len(errors)} errors")
            
            return {
                "success": True,
                "processed_count": len(results),
                "error_count": len(errors),
                "results": results,
                "errors": errors
            }
            
        except Exception as e:
            self.logger.error(f"❌ Batch processing failed: {e}")
            return {
                "success": False,
                "processed_count": 0,
                "error_count": len(file_ids),
                "results": [],
                "errors": [{"file_id": fid, "error": str(e)} for fid in file_ids],
                "error": str(e)
            }
    
    async def convert_format(
        self,
        file_id: str,
        target_format: str,
        user_id: Optional[str] = None,
        conversion_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convert file format using FormatComposerService (Frontend API).
        
        Converts parsed content to target format (parquet, json_structured, json_chunks).
        
        Args:
            file_id: File ID to convert
            target_format: Target format ("parquet", "json_structured", or "json_chunks")
            user_id: Optional user identifier
            conversion_options: Optional conversion configuration
        
        Returns:
            Format conversion result
        """
        try:
            self.logger.info(f"🔄 Converting file {file_id} to {target_format}")
            
            # Get FormatComposerService
            format_composer = await self.get_enabling_service("format_composer_service")
            if not format_composer:
                return {
                    "success": False,
                    "error": "Format Composer Service not available"
                }
            
            # Get parsed data from file
            parse_result = await self.parse_file(file_id=file_id)
            if not parse_result.get("success"):
                return {
                    "success": False,
                    "error": "Failed to parse file for format conversion",
                    "parse_error": parse_result.get("error")
                }
            
            parsed_data = parse_result.get("parsed_content", {})
            
            # Compose format
            composition_result = await format_composer.compose_format(
                parsed_data=parsed_data,
                target_format=target_format,
                file_id=file_id,
                composition_options=conversion_options
            )
            
            if not composition_result.get("success"):
                return {
                    "success": False,
                    "error": "Format composition failed",
                    "composition_error": composition_result.get("error")
                }
            
            self.logger.info(f"✅ Format conversion complete: {file_id} → {target_format}")
            
            return {
                "success": True,
                "file_id": file_id,
                "target_format": target_format,
                "composed_data": composition_result.get("composed_data"),
                "metadata": composition_result.get("metadata", {})
            }
            
        except Exception as e:
            self.logger.error(f"❌ Format conversion failed: {e}")
            return {
                "success": False,
                "file_id": file_id,
                "target_format": target_format,
                "error": str(e)
            }
    
    # ========================================================================
    # SAGA INTEGRATION (Capability by Design, Optional by Policy)
    # ========================================================================
    
    async def _get_policy_configuration_service(self):
        """Lazy initialization of Policy Configuration Service."""
        if not hasattr(self, '_policy_config_service') or self._policy_config_service is None:
            try:
                curator = await self.get_foundation_service("CuratorFoundationService")
                if curator:
                    self._policy_config_service = await curator.discover_service_by_name("PolicyConfigurationService")
                    if self._policy_config_service:
                        self.logger.info("✅ Discovered PolicyConfigurationService")
            except Exception as e:
                self.logger.warning(f"⚠️ PolicyConfigurationService not available: {e}")
                self._policy_config_service = None
        
        return self._policy_config_service
    
    async def _get_saga_policy(self, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get Saga policy from PolicyConfigurationService.
        
        Merges policy from service with orchestrator-specific compensation handlers.
        
        Args:
            user_context: Optional user context
        
        Returns:
            Dict with Saga policy (enable_saga, saga_operations, compensation_handlers)
        """
        # Get Policy Configuration Service
        policy_service = await self._get_policy_configuration_service()
        
        if policy_service:
            try:
                # Get policy from service
                policy_result = await policy_service.get_saga_policy(
                    orchestrator_name=self.service_name,
                    user_context=user_context
                )
                
                if policy_result.get("success"):
                    policy = policy_result.get("policy", {})
                    # Merge compensation handlers from orchestrator
                    policy["compensation_handlers"] = self._get_compensation_handlers()
                    return policy
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get Saga policy from PolicyConfigurationService: {e}")
        
        # Fallback to ConfigAdapter if PolicyConfigurationService not available
        config_adapter = self._get_config_adapter()
        saga_enabled_str = config_adapter.get("SAGA_ENABLED", "false")
        saga_enabled = saga_enabled_str.lower() == "true" if isinstance(saga_enabled_str, str) else bool(saga_enabled_str)
        saga_operations_str = config_adapter.get("SAGA_OPERATIONS", "content_process_file")
        saga_operations = saga_operations_str.split(",") if isinstance(saga_operations_str, str) else []
        
        return {
            "enable_saga": saga_enabled,
            "saga_operations": [op.strip() for op in saga_operations],
            "compensation_handlers": self._get_compensation_handlers()
        }
    
    async def _saga_enabled(self, user_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if Saga is enabled via policy.
        
        ⭐ CAPABILITY BY DESIGN, OPTIONAL BY POLICY:
        - Saga capability is built into the architecture
        - Enabled/disabled via policy configuration
        - Default: disabled (no overhead)
        
        Args:
            user_context: Optional user context for policy retrieval
        
        Returns:
            bool indicating if Saga is enabled
        """
        # Get policy (cached or fresh)
        if not hasattr(self, '_saga_policy') or self._saga_policy is None:
            self._saga_policy = await self._get_saga_policy(user_context)
        
        return self._saga_policy.get("enable_saga", False)
    
    def _get_compensation_handlers(self) -> Dict[str, Dict[str, str]]:
        """
        Get compensation handlers for this orchestrator's operations.
        
        Returns:
            Dict mapping operation -> milestone -> compensation_handler
        """
        return {
            "content_process_file": {
                "parse": "mark_file_as_unparsed",
                "store_parsed": "delete_parsed_file",
                "embed": "delete_embeddings"
            }
        }
    
    async def _get_saga_journey_orchestrator(self):
        """Lazy initialization of Saga Journey Orchestrator."""
        if not hasattr(self, '_saga_orchestrator') or self._saga_orchestrator is None:
            try:
                curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
                if curator:
                    self._saga_orchestrator = await curator.discover_service_by_name("SagaJourneyOrchestratorService")
                    if self._saga_orchestrator:
                        self.logger.info("✅ Discovered SagaJourneyOrchestratorService")
            except Exception as e:
                self.logger.warning(f"⚠️ SagaJourneyOrchestratorService not available: {e}")
                self._saga_orchestrator = None
        
        return self._saga_orchestrator
    
    async def _execute_with_saga(
        self,
        operation: str,
        workflow_func,
        milestones: List[str],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute workflow with Saga guarantees if enabled by policy.
        
        Pattern: "Capability by Design, Optional by Policy"
        
        Args:
            operation: Operation name (e.g., "content_process_file")
            workflow_func: Async function that executes the workflow
            milestones: List of milestone names for this operation
            user_context: Optional user context
        
        Returns:
            Dict with workflow result, including saga_id if Saga was used
        """
        # Get policy if not cached
        if not hasattr(self, '_saga_policy') or self._saga_policy is None:
            self._saga_policy = await self._get_saga_policy(user_context)
        
        if not await self._saga_enabled(user_context):
            # Execute without Saga (normal flow)
            return await workflow_func()
        
        if operation not in self._saga_policy.get("saga_operations", []):
            # Execute without Saga (operation not in policy)
            return await workflow_func()
        
        # Get Saga Journey Orchestrator
        saga_orchestrator = await self._get_saga_journey_orchestrator()
        if not saga_orchestrator:
            self.logger.warning("⚠️ Saga Journey Orchestrator not available, executing without Saga")
            return await workflow_func()
        
        # Get compensation handlers for this operation
        compensation_handlers = self._saga_policy.get("compensation_handlers", {}).get(operation, {})
        
        # Design Saga journey
        saga_journey = await saga_orchestrator.design_saga_journey(
            journey_type=operation,
            requirements={
                "operation": operation,
                "milestones": milestones
            },
            compensation_handlers=compensation_handlers,
            user_context=user_context
        )
        
        if not saga_journey.get("success"):
            self.logger.warning(f"⚠️ Saga journey design failed: {saga_journey.get('error')}, executing without Saga")
            return await workflow_func()
        
        # Execute Saga journey
        saga_execution = await saga_orchestrator.execute_saga_journey(
            journey_id=saga_journey["journey_id"],
            user_id=user_context.get("user_id") if user_context else "anonymous",
            context={"operation": operation},
            user_context=user_context
        )
        
        if not saga_execution.get("success"):
            self.logger.warning(f"⚠️ Saga execution start failed: {saga_execution.get('error')}, executing without Saga")
            return await workflow_func()
        
        saga_id = saga_execution["saga_id"]
        
        # Execute workflow as Saga milestone
        try:
            result = await workflow_func()
            
            # Advance Saga step (success)
            await saga_orchestrator.advance_saga_step(
                saga_id=saga_id,
                journey_id=saga_journey["journey_id"],
                user_id=user_context.get("user_id") if user_context else "anonymous",
                step_result={"status": "complete", **result},
                user_context=user_context
            )
            
            result["saga_id"] = saga_id
            return result
            
        except Exception as e:
            # Advance Saga step (failure) - triggers automatic compensation
            await saga_orchestrator.advance_saga_step(
                saga_id=saga_id,
                journey_id=saga_journey["journey_id"],
                user_id=user_context.get("user_id") if user_context else "anonymous",
                step_result={"status": "failed", "error": str(e)},
                user_context=user_context
            )
            raise
    
    # ========================================================================
    # ORCHESTRATION HELPERS
    # ========================================================================
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute orchestration (called by Business Orchestrator).
        
        Routes to appropriate capability based on request action.
        
        Args:
            request: Request with action and params
        
        Returns:
            Orchestration result
        """
        try:
            action = request.get("action")
            params = request.get("params", {})
            
            if action == "analyze_document":
                return await self.analyze_document(
                    document_id=params.get("document_id"),
                    analysis_types=params.get("analysis_types", [])
                )
            
            elif action == "parse_file":
                return await self.parse_file(
                    file_id=params.get("file_id"),
                    parse_options=params.get("parse_options")
                )
            
            elif action == "extract_entities":
                return await self.extract_entities(
                    document_id=params.get("document_id")
                )
            
            else:
                return {
                    "status": "error",
                    "message": f"Unknown action: {action}",
                    "available_actions": ["analyze_document", "parse_file", "extract_entities"]
                }
            
        except Exception as e:
            self.logger.error(f"❌ Orchestration execution failed: {e}")
            return {
                "status": "error",
                "message": f"Orchestration execution failed: {str(e)}",
                "error": str(e)
            }
    
    def _format_for_mvp_ui(self, results: Dict[str, Any], resource_id: str) -> Dict[str, Any]:
        """
        Format results for MVP UI (preserves API contract).
        
        Ensures UI receives data in expected format.
        
        Args:
            results: Orchestration results
            resource_id: Resource ID (document_id, file_id, etc.)
        
        Returns:
            Formatted response for MVP UI
        """
        # Extract success status from nested results if available
        success = results.get("parse_result", {}).get("success", True) if "parse_result" in results else True
        
        return {
            "status": "success",
            "success": success,  # Add top-level success for test compatibility
            "resource_id": resource_id,
            "data": results,
            "timestamp": datetime.utcnow().isoformat(),
            "orchestrator": self.orchestrator_name
        }
    
    async def _convert_to_jsonl_bytes(self, parse_result: Dict[str, Any]) -> Optional[bytes]:
        """
        Convert parsed data to JSONL (JSON Lines) bytes.
        
        Simple, flexible, AI-friendly format: one JSON object per line.
        No type inference issues, works perfectly with pandas for analytics.
        
        Args:
            parse_result: Parse result dictionary with tables, records, or data
        
        Returns:
            JSONL file bytes, or None if conversion fails
        """
        try:
            import json
            
            # DEBUG: Log parse_result structure to understand what we're receiving
            self.logger.info(f"🔍 [JSONL Conversion] parse_result keys: {list(parse_result.keys())}")
            self.logger.info(f"🔍 [JSONL Conversion] parse_result has 'records': {'records' in parse_result}")
            self.logger.info(f"🔍 [JSONL Conversion] parse_result has 'tables': {'tables' in parse_result}")
            self.logger.info(f"🔍 [JSONL Conversion] parse_result has 'data': {'data' in parse_result}")
            if "records" in parse_result:
                self.logger.info(f"🔍 [JSONL Conversion] records type: {type(parse_result['records'])}, length: {len(parse_result['records']) if isinstance(parse_result['records'], list) else 'N/A'}")
            if "tables" in parse_result:
                self.logger.info(f"🔍 [JSONL Conversion] tables type: {type(parse_result['tables'])}, length: {len(parse_result['tables']) if isinstance(parse_result['tables'], list) else 'N/A'}")
            if "data" in parse_result:
                self.logger.info(f"🔍 [JSONL Conversion] data type: {type(parse_result['data'])}")
                if isinstance(parse_result['data'], dict):
                    self.logger.info(f"🔍 [JSONL Conversion] data keys: {list(parse_result['data'].keys())}")
                    if "records" in parse_result['data']:
                        self.logger.info(f"🔍 [JSONL Conversion] data.records type: {type(parse_result['data']['records'])}, length: {len(parse_result['data']['records']) if isinstance(parse_result['data']['records'], list) else 'N/A'}")
            
            # Extract structured data from parse_result
            records = []
            
            # Check for tables (list of tables)
            if "tables" in parse_result and isinstance(parse_result["tables"], list):
                for table in parse_result["tables"]:
                    if isinstance(table, list):
                        records.extend(table)
                    elif isinstance(table, dict):
                        # Tables might have a "data" key containing the actual records
                        if "data" in table and isinstance(table["data"], list):
                            records.extend(table["data"])
                        else:
                            records.append(table)
            
            # Check for records (list of records)
            if "records" in parse_result and isinstance(parse_result["records"], list):
                records.extend(parse_result["records"])
            
            # Check for data (structured data dict)
            if "data" in parse_result:
                data = parse_result["data"]
                if isinstance(data, list):
                    records.extend(data)
                elif isinstance(data, dict):
                    # data might be a dict with "records" or "tables" inside
                    if "records" in data and isinstance(data["records"], list):
                        records.extend(data["records"])
                    elif "tables" in data and isinstance(data["tables"], list):
                        for table in data["tables"]:
                            if isinstance(table, dict) and "data" in table:
                                records.extend(table["data"])
                    else:
                        records.append(data)
            
            self.logger.info(f"🔍 [JSONL Conversion] Extracted {len(records)} records total")
            
            if not records:
                self.logger.warning("⚠️ No structured data found in parse_result - cannot convert to JSONL")
                return None
            
            # Convert to JSONL: one JSON object per line
            jsonl_lines = []
            for record in records:
                # Convert to native Python types (handles numpy types automatically via default=str)
                json_line = json.dumps(record, default=str)  # default=str handles numpy types
                jsonl_lines.append(json_line)
            
            # Join with newlines and encode to bytes
            jsonl_content = '\n'.join(jsonl_lines)
            jsonl_bytes = jsonl_content.encode('utf-8')
            
            self.logger.info(f"✅ Converted to JSONL: {len(records)} records, {len(jsonl_bytes)} bytes")
            return jsonl_bytes
            
        except Exception as e:
            self.logger.error(f"❌ Failed to convert to JSONL bytes: {e}", exc_info=True)
            return None
    
    async def expose_data(
        self,
        file_id: str,
        parsed_file_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Expose data through semantic layer (for Operations/Business Outcomes access).
        
        This method exposes parsed data, content metadata, and semantic embeddings
        through the semantic layer, enabling Operations and Business Outcomes
        pillars to access parsed files without touching raw client data.
        
        Flow:
        1. Get parsed file from Content Steward
        2. Get content metadata from Librarian
        3. Get semantic embeddings (if available)
        4. Return exposed data (semantic view)
        
        Args:
            file_id: File identifier
            parsed_file_id: Optional parsed file identifier (if not provided, gets first one from file metadata)
            user_context: Optional user context (includes workflow_id, tenant_id, etc.)
        
        Returns:
            Dict with exposed data:
            {
                "success": bool,
                "parsed_data": {...},  # Parsed file data (summary/preview)
                "content_metadata": {...},  # Content metadata from Librarian
                "embeddings_info": {...},  # Embeddings information (if available)
                "exposed_via": "semantic_layer",
                "raw_client_data": False  # Not touching raw client data
            }
        """
        try:
            self.logger.info(f"📤 Exposing data via semantic layer: file_id={file_id}, parsed_file_id={parsed_file_id}")
            
            # Step 1: Get parsed file from Content Steward
            data_steward = await self.get_data_steward_api()
            if not data_steward:
                return {
                    "success": False,
                    "error": "ContentSteward not available",
                    "file_id": file_id
                }
            
            # If parsed_file_id not provided, get it from file metadata
            if not parsed_file_id:
                file_info = await data_steward.get_file(file_id, user_context=user_context)
                if file_info and file_info.get("metadata"):
                    parsed_file_id = file_info.get("metadata", {}).get("parsed_file_id")
                    if not parsed_file_id:
                        # Try to get first parsed file for this file_id
                        # Query parsed files for this file_id
                        parsed_files = await data_steward.list_parsed_files(file_id=file_id, user_context=user_context)
                        if parsed_files and isinstance(parsed_files, list) and len(parsed_files) > 0:
                            parsed_file_id = parsed_files[0].get("parsed_file_id")
            
            if not parsed_file_id:
                return {
                    "success": False,
                    "error": f"No parsed file found for file_id: {file_id}",
                    "file_id": file_id
                }
            
            # Get parsed file (summary/preview, not full data)
            parsed_file = await data_steward.get_parsed_file(parsed_file_id, user_context=user_context)
            if not parsed_file:
                return {
                    "success": False,
                    "error": f"Parsed file not found: {parsed_file_id}",
                    "file_id": file_id,
                    "parsed_file_id": parsed_file_id
                }
            
            # Extract parsed data summary (not full data to keep response size manageable)
            parsed_data_summary = {
                "parsed_file_id": parsed_file_id,
                "parsing_type": parsed_file.get("metadata", {}).get("parse_result", {}).get("parsing_type"),
                "file_type": parsed_file.get("metadata", {}).get("parse_result", {}).get("file_type"),
                "structure": parsed_file.get("metadata", {}).get("parse_result", {}).get("structure", {}),
                "record_count": parsed_file.get("metadata", {}).get("parse_result", {}).get("record_count", 0),
                "table_count": parsed_file.get("metadata", {}).get("parse_result", {}).get("table_count", 0),
                "note": "Full parsed data available via preview_parsed_file() or get_parsed_file()"
            }
            
            # Step 2: Get content metadata from Librarian
            librarian = await self.get_content_steward_api()
            content_metadata = None
            if librarian:
                try:
                    content_metadata = await librarian.get_content_metadata(file_id, user_context=user_context)
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to get content metadata from Librarian: {e}")
            
            # Step 3: Get semantic embeddings info (if available)
            embeddings_info = None
            try:
                # Check if embeddings exist for this parsed_file_id
                # Query semantic layer for embeddings
                semantic_data = self.get_abstraction("semantic_data")
                if semantic_data:
                    # Try to get embeddings info (count, etc.)
                    # Note: This is a lightweight check, not full embedding retrieval
                    embeddings_info = {
                        "embeddings_available": True,
                        "note": "Embeddings can be queried via semantic layer"
                    }
            except Exception as e:
                self.logger.debug(f"Embeddings info not available: {e}")
                embeddings_info = {
                    "embeddings_available": False,
                    "note": "Embeddings not yet created for this file"
                }
            
            # Step 4: Return exposed data (semantic view)
            result = {
                "success": True,
                "file_id": file_id,
                "parsed_file_id": parsed_file_id,
                "parsed_data": parsed_data_summary,
                "content_metadata": content_metadata or {},
                "embeddings_info": embeddings_info or {},
                "exposed_via": "semantic_layer",
                "raw_client_data": False,  # Not touching raw client data
                "message": "Data exposed successfully via semantic layer"
            }
            
            self.logger.info(f"✅ Data exposure complete: file_id={file_id}, parsed_file_id={parsed_file_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Data exposure failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "file_id": file_id,
                "parsed_file_id": parsed_file_id
            }
    
    async def preview_parsed_file(
        self,
        parsed_file_id: str,
        max_rows: int = 20,
        max_columns: int = 20,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Preview parsed file from JSONL storage.
        
        Reads first N lines and extracts first M columns from JSONL file for display.
        
        Args:
            parsed_file_id: ID of parsed file (JSONL in GCS)
            max_rows: Maximum rows to return (default: 20)
            max_columns: Maximum columns to return (default: 20)
            user_id: Optional user identifier
        
        Returns:
            Preview data with columns, rows, and metadata
        """
        try:
            import json
            
            # Ensure max_rows and max_columns are integers (defensive check)
            try:
                max_rows = int(max_rows) if max_rows is not None else 20
            except (ValueError, TypeError):
                max_rows = 20
            try:
                max_columns = int(max_columns) if max_columns is not None else 20
            except (ValueError, TypeError):
                max_columns = 20
            
            self.logger.info(f"👁️ Previewing parsed file: {parsed_file_id} (max_rows={max_rows}, max_columns={max_columns})")
            
            # Get Content Steward API
            data_steward = await self.get_data_steward_api()
            if not data_steward:
                return {
                    "success": False,
                    "error": "Content Steward not available",
                    "parsed_file_id": parsed_file_id
                }
            
            # Get parsed file from Content Steward (retrieves from parsed_data_files table + GCS)
            # With the fix to store_parsed_file(), parsed_file_id is now the actual GCS UUID
            parsed_file = await data_steward.get_parsed_file(parsed_file_id)
            
            if not parsed_file:
                return {
                    "success": False,
                    "error": "Parsed file not found",
                    "parsed_file_id": parsed_file_id
                }
            
            # Extract JSONL data from Content Steward response
            # ContentSteward.get_parsed_file() returns: {parsed_file_id, metadata, file_data, format_type, content_type}
            jsonl_data = parsed_file.get("file_data") or parsed_file.get("file_content") or parsed_file.get("data") or parsed_file.get("content")
            
            if not jsonl_data:
                return {
                    "success": False,
                    "error": "Parsed file has no data",
                    "parsed_file_id": parsed_file_id
                }
            
            # Convert to string if bytes
            if isinstance(jsonl_data, bytes):
                jsonl_data = jsonl_data.decode('utf-8')
            
            # Parse JSONL (one JSON object per line)
            lines = jsonl_data.strip().split('\n')
            records = []
            for line in lines[:max_rows]:
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"⚠️ Skipping invalid JSON line: {e}")
                        continue
            
            if not records:
                return {
                    "success": False,
                    "error": "No valid records found in JSONL file",
                    "parsed_file_id": parsed_file_id
                }
            
            # Extract columns from first record
            all_columns = list(records[0].keys())
            columns = all_columns[:max_columns]
            
            # Build preview grid
            preview_rows = []
            for record in records:
                row = [str(record.get(col, '')) for col in columns]
                preview_rows.append(row)
            
            # Get total line count (for total_rows)
            total_lines = len([line for line in lines if line.strip()])
            
            preview_data = {
                "columns": columns,
                "rows": preview_rows,
                "total_rows": total_lines,
                "total_columns": len(all_columns),
                "preview_rows": len(preview_rows),
                "preview_columns": len(columns)
            }
            
            self.logger.info(f"✅ Preview generated: {preview_data['preview_rows']} rows × {preview_data['preview_columns']} columns (from {preview_data['total_rows']} × {preview_data['total_columns']})")
            
            return {
                "success": True,
                "parsed_file_id": parsed_file_id,
                "preview": preview_data
            }
            
        except Exception as e:
            self.logger.error(f"❌ Preview parsed file failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "parsed_file_id": parsed_file_id
            }
    
    async def list_parsed_files(
        self,
        user_id: str,
        file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List parsed files for a user (or for a specific file).
        
        Args:
            user_id: User identifier
            file_id: Optional file ID to filter parsed files for a specific original file
        
        Returns:
            List of parsed files with metadata
        """
        try:
            self.logger.info(f"📋 Listing parsed files for user: {user_id}" + (f" (file_id: {file_id})" if file_id else ""))
            
            # Get Content Steward API
            data_steward = await self.get_data_steward_api()
            if not data_steward:
                return {
                    "success": False,
                    "parsed_files": [],
                    "count": 0,
                    "error": "Content Steward not available"
                }
            
            # Query parsed files via Content Steward
            # ContentSteward.list_parsed_files() requires file_id, so we need file_id to query
            if file_id:
                # Get parsed files for this specific file
                parsed_files_list = await data_steward.list_parsed_files(file_id)
                
                # Format parsed files for frontend
                formatted_files = []
                for parsed_file in parsed_files_list:
                    parsed_file_id = parsed_file.get("parsed_file_id")
                    
                    # ✅ STANDARDIZED: Get ui_name directly from parsed_data_files table (no JOIN needed!)
                    parsed_file_name = parsed_file.get("ui_name")
                    
                    # Fallback: If ui_name not yet populated (legacy data), construct from format_type
                    if not parsed_file_name:
                        format_type = parsed_file.get("format_type", "jsonl")
                        parsed_file_name = f"Parsed: {format_type}"
                        self.logger.debug(f"⚠️ Using fallback name for parsed_file_id {parsed_file_id} (ui_name not in table yet): {parsed_file_name}")
                    
                    formatted_files.append({
                        "parsed_file_id": parsed_file_id,
                        "id": parsed_file_id,  # For frontend compatibility
                        "file_id": parsed_file.get("file_id"),
                        "name": parsed_file_name,
                        "format_type": parsed_file.get("format_type", "jsonl"),
                        "content_type": parsed_file.get("content_type", "structured"),
                        "row_count": parsed_file.get("row_count", 0),
                        "column_count": parsed_file.get("column_count", 0),
                        "parsed_at": parsed_file.get("parsed_at"),
                        "created_at": parsed_file.get("parsed_at")  # For frontend compatibility
                    })
                
                self.logger.info(f"✅ Found {len(formatted_files)} parsed files for file_id: {file_id}")
                
                return {
                    "success": True,
                    "parsed_files": formatted_files,
                    "count": len(formatted_files)
                }
            else:
                # If no file_id provided, list ALL parsed files for the user
                # Query parsed_data_files directly by user_id (more efficient than iterating through files)
                self.logger.info(f"📋 Listing ALL parsed files for user: {user_id}")
                
                # Get user context
                ctx = get_request_user_context()
                if not ctx:
                    ctx = {"user_id": user_id}
                
                # Query parsed_data_files directly by user_id
                # This is more efficient than iterating through all uploaded files
                all_parsed_files_raw = await data_steward.list_parsed_files(file_id=None, user_id=user_id, user_context=ctx)
                
                # Format parsed files for frontend
                all_parsed_files = []
                parsed_file_ids_seen = set()  # Track parsed file IDs to avoid duplicates
                
                for parsed_file in all_parsed_files_raw:
                    parsed_file_id = parsed_file.get("parsed_file_id")
                    if parsed_file_id and parsed_file_id not in parsed_file_ids_seen:
                        parsed_file_ids_seen.add(parsed_file_id)
                        
                        # ✅ STANDARDIZED: Get ui_name directly from parsed_data_files table (no JOIN needed!)
                        # This matches the unified query pattern across project_files, parsed_data_files, and embedding_files
                        parsed_file_name = parsed_file.get("ui_name")
                        
                        # Get file_id from parsed_file record (from parsed_data_files table)
                        original_file_id = parsed_file.get("file_id")  # ✅ FIXED: Get file_id from parsed_file record
                        
                        # Fallback: If ui_name not yet populated (legacy data), construct from format_type
                        if not parsed_file_name:
                            format_type = parsed_file.get("format_type", "jsonl")
                            parsed_file_name = f"Parsed {format_type} file"
                            self.logger.debug(f"⚠️ Using fallback name for parsed_file_id {parsed_file_id} (ui_name not in table yet): {parsed_file_name}")
                        
                        all_parsed_files.append({
                            "parsed_file_id": parsed_file_id,
                            "id": parsed_file_id,  # For frontend compatibility
                            "file_id": original_file_id,  # ✅ FIXED: Use file_id from parsed_file record
                            "name": parsed_file_name,
                            "ui_name": parsed_file_name,  # ✅ Also include ui_name for frontend
                            "format_type": parsed_file.get("format_type", "jsonl"),
                            "content_type": parsed_file.get("content_type", "structured"),
                            "row_count": parsed_file.get("row_count", 0),
                            "column_count": parsed_file.get("column_count", 0),
                            "parsed_at": parsed_file.get("parsed_at"),
                            "created_at": parsed_file.get("parsed_at")  # For frontend compatibility
                        })
                
                self.logger.info(f"✅ Found {len(all_parsed_files)} total parsed files for user: {user_id}")
                
                return {
                    "success": True,
                    "parsed_files": all_parsed_files,
                    "count": len(all_parsed_files)
                }
            
        except Exception as e:
            self.logger.error(f"❌ List parsed files failed: {e}", exc_info=True)
            return {
                "success": False,
                "parsed_files": [],
                "count": 0,
                "error": str(e)
            }
    
    async def list_parsed_files_with_embeddings(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        List parsed files that have embeddings (for Data Mash UI).
        
        This endpoint filters parsed files to only show those that have embeddings,
        making it easier for users to view semantic layer data.
        
        Args:
            user_id: User identifier
        
        Returns:
            List of parsed files with embeddings, including embedding metadata
        """
        try:
            self.logger.info(f"📋 Listing parsed files with embeddings for user: {user_id}")
            
            # Step 1: Get all embedding files for user (direct query - much simpler!)
            embedding_files_result = await self.list_embedding_files(user_id)
            if not embedding_files_result.get("success"):
                return {
                    "success": False,
                    "parsed_files": [],
                    "count": 0,
                    "error": embedding_files_result.get("error", "Failed to list embedding files")
                }
            
            embedding_files = embedding_files_result.get("embedding_files", [])
            if not embedding_files:
                return {
                    "success": True,
                    "parsed_files": [],
                    "count": 0
                }
            
            self.logger.info(f"🔍 Found {len(embedding_files)} embedding files")
            
            # Step 2: Group embedding files by parsed_file_id
            parsed_file_id_to_embeddings = {}
            for emb_file in embedding_files:
                parsed_file_id = emb_file.get("parsed_file_id")
                if parsed_file_id:
                    if parsed_file_id not in parsed_file_id_to_embeddings:
                        parsed_file_id_to_embeddings[parsed_file_id] = []
                    parsed_file_id_to_embeddings[parsed_file_id].append(emb_file)
            
            # Step 3: Get parsed file metadata for each parsed_file_id that has embeddings
            data_steward = await self.get_data_steward_api()
            if not data_steward:
                return {
                    "success": False,
                    "parsed_files": [],
                    "count": 0,
                    "error": "Content Steward not available"
                }
            
            parsed_files_with_embeddings = []
            for parsed_file_id, emb_files in parsed_file_id_to_embeddings.items():
                try:
                    # Get parsed file metadata (includes ui_name from parsed_data_files table)
                    parsed_file = await data_steward.get_parsed_file(parsed_file_id)
                    if parsed_file:
                        # Calculate total embeddings count
                        total_embeddings = sum(emb_file.get("embeddings_count", 0) for emb_file in emb_files)
                        
                        # ✅ STANDARDIZED: Get ui_name directly from parsed_data_files table
                        # get_parsed_file returns: {"metadata": parsed_file_metadata, ...}
                        # where parsed_file_metadata is the full row from parsed_data_files table (includes ui_name)
                        file_id = emb_files[0].get("file_id")
                        parsed_file_metadata = parsed_file.get("metadata", {}) if isinstance(parsed_file, dict) else {}
                        
                        # Get ui_name directly from parsed_file_metadata (it's a column in parsed_data_files table)
                        parsed_file_ui_name = parsed_file_metadata.get("ui_name")
                        
                        # Fallback: Use embedding file's ui_name or construct from parsed_file_id
                        if not parsed_file_ui_name:
                            parsed_file_ui_name = emb_files[0].get("ui_name", f"Parsed file {parsed_file_id[:8]}")
                            self.logger.debug(f"⚠️ Using fallback ui_name for parsed_file_id {parsed_file_id} (ui_name not in parsed_data_files yet): {parsed_file_ui_name}")
                        
                        # Format parsed file with embedding metadata
                        parsed_files_with_embeddings.append({
                            "parsed_file_id": parsed_file_id,
                            "id": parsed_file_id,  # For frontend compatibility
                            "file_id": file_id,
                            "name": parsed_file_ui_name,  # ✅ Use ui_name directly from parsed_data_files
                            "format_type": parsed_file_metadata.get("format_type", "jsonl"),
                            "content_type": parsed_file_metadata.get("content_type", "structured"),
                            "row_count": parsed_file_metadata.get("row_count", 0),
                            "column_count": parsed_file_metadata.get("column_count", 0),
                            "parsed_at": parsed_file_metadata.get("parsed_at"),
                            "created_at": parsed_file_metadata.get("parsed_at"),
                            "embeddings_count": total_embeddings,
                            "embedding_files": emb_files  # Include embedding file details
                        })
                except Exception as parse_error:
                    self.logger.warning(f"⚠️ Failed to get parsed file {parsed_file_id}: {parse_error}")
                    # Still include it with minimal info from embedding file
                    parsed_files_with_embeddings.append({
                        "parsed_file_id": parsed_file_id,
                        "id": parsed_file_id,
                        "file_id": emb_files[0].get("file_id"),
                        "name": emb_files[0].get("ui_name", f"Parsed file {parsed_file_id[:8]}"),
                        "embeddings_count": sum(emb_file.get("embeddings_count", 0) for emb_file in emb_files),
                        "embedding_files": emb_files
                    })
            
            self.logger.info(f"✅ Found {len(parsed_files_with_embeddings)} parsed files with embeddings")
            
            return {
                "success": True,
                "parsed_files": parsed_files_with_embeddings,
                "count": len(parsed_files_with_embeddings)
            }
            
        except Exception as e:
            self.logger.error(f"❌ List parsed files with embeddings failed: {e}", exc_info=True)
            return {
                "success": False,
                "parsed_files": [],
                "count": 0,
                "error": str(e)
            }
    
    async def get_dashboard_files(
        self,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get unified file list for dashboard from all three tables (OPTIMAL ARCHITECTURE).
        
        This is the optimal architecture: dashboard service queries all three tables
        (project_files, parsed_data_files, embedding_files) and composes a unified view.
        
        Args:
            user_id: User identifier
            user_context: Optional user context
        
        Returns:
            Dict with files list and statistics
        """
        try:
            self.logger.info(f"📋 Getting dashboard files for user: {user_id}")
            
            # Get user context
            from utilities.security_authorization.request_context import get_request_user_context
            ctx = user_context or get_request_user_context()
            
            # Use ContentStewardService
            data_steward = await self.get_data_steward_api()
            if not data_steward:
                return {
                    "success": False,
                    "files": [],
                    "statistics": {"uploaded": 0, "parsed": 0, "embedded": 0, "total": 0},
                    "error": "Content Steward service not available"
                }
            
            # Get dashboard files via ContentStewardService
            result = await data_steward.get_dashboard_files(user_id=user_id, user_context=ctx)
            
            self.logger.info(f"✅ Dashboard files retrieved: {result.get('statistics', {})}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Get dashboard files failed: {e}", exc_info=True)
            return {
                "success": False,
                "files": [],
                "statistics": {"uploaded": 0, "parsed": 0, "embedded": 0, "total": 0},
                "error": str(e)
            }
    
    async def delete_file_by_type(
        self,
        file_uuid: str,
        file_type: str,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delete file directly from its table and storage (OPTIMAL ARCHITECTURE).
        No cascade - users delete what they want to delete.
        
        Args:
            file_uuid: UUID of file to delete
            file_type: "original", "parsed", or "embedded"
            user_id: User identifier
            user_context: Optional user context
        
        Returns:
            Delete result
        """
        try:
            self.logger.info(f"🗑️ Deleting file: {file_uuid} (type: {file_type})")
            
            # Get user context
            from utilities.security_authorization.request_context import get_request_user_context
            ctx = user_context or get_request_user_context()
            
            # Use ContentStewardService
            data_steward = await self.get_data_steward_api()
            if not data_steward:
                return {
                    "success": False,
                    "error": "Content Steward service not available"
                }
            
            # Delete file via ContentStewardService
            result = await data_steward.delete_file_by_type(
                file_uuid=file_uuid,
                file_type=file_type,
                user_context=ctx
            )
            
            self.logger.info(f"✅ File deleted: {file_uuid} (type: {file_type})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Delete file failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_file_statistics(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive file statistics for dashboard.
        
        Queries all three file types separately:
        - Uploaded files (project_files table)
        - Parsed files (parsed_data_files table)
        - Embedding files (embedding_files table)
        
        Args:
            user_id: User identifier
        
        Returns:
            Statistics with counts for each file type
        """
        try:
            self.logger.info(f"📊 Getting file statistics for user: {user_id}")
            
            # Get user context for tenant_id
            from utilities.security_authorization.request_context import get_request_user_context
            ctx = get_request_user_context()
            
            # Use ContentStewardService instead of direct file_management access
            data_steward = await self.get_data_steward_api()
            if not data_steward:
                return {
                    "success": False,
                    "statistics": {"uploaded": 0, "parsed": 0, "embedded": 0, "total": 0},
                    "error": "Content Steward service not available"
                }
            
            # Get statistics via ContentStewardService
            try:
                stats = await data_steward.get_file_statistics(user_id=user_id, user_context=ctx)
                uploaded_count = stats.get("uploaded", 0)
                parsed_count = stats.get("parsed", 0)
                embedded_count = stats.get("embedded", 0)
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get file statistics: {e}")
                uploaded_count = 0
                parsed_count = 0
                embedded_count = 0
            
            statistics = {
                "uploaded": uploaded_count,
                "parsed": parsed_count,
                "embedded": embedded_count,  # ✅ FIXED: Use embedded_count (not embedding_count)
                "total": uploaded_count + parsed_count + embedded_count
            }
            
            self.logger.info(f"✅ File statistics: {statistics}")
            
            return {
                "success": True,
                "statistics": statistics
            }
            
        except Exception as e:
            self.logger.error(f"❌ Get file statistics failed: {e}", exc_info=True)
            return {
                "success": False,
                "statistics": {},
                "error": str(e)
            }
    
    async def list_embedding_files(
        self,
        user_id: str,
        parsed_file_id: Optional[str] = None,
        file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List embedding files for a user (for Data Mash UI).
        
        This endpoint queries the embedding_files table directly, providing
        UI-friendly names and metadata for embeddings.
        
        Args:
            user_id: User identifier
            parsed_file_id: Optional parsed file ID to filter by
            file_id: Optional original file ID to filter by
        
        Returns:
            List of embedding files with metadata
        """
        try:
            self.logger.info(f"📋 Listing embedding files for user: {user_id}" + 
                           (f" (parsed_file_id: {parsed_file_id})" if parsed_file_id else "") +
                           (f" (file_id: {file_id})" if file_id else ""))
            
            # Get user context
            from utilities.security_authorization.request_context import get_request_user_context
            ctx = get_request_user_context()
            
            # Use ContentStewardService instead of direct file_management access
            data_steward = await self.get_data_steward_api()
            if not data_steward:
                return {
                    "success": False,
                    "embedding_files": [],
                    "count": 0,
                    "error": "Content Steward service not available"
                }
            
            # Query embedding_files table via ContentStewardService
            try:
                embedding_files_raw = await data_steward.list_embedding_files(
                    user_id=user_id,
                    parsed_file_id=parsed_file_id,
                    file_id=file_id,
                    user_context=ctx
                )
            except Exception as e:
                self.logger.error(f"❌ Failed to list embedding files: {e}", exc_info=True)
                return {
                    "success": False,
                    "embedding_files": [],
                    "count": 0,
                    "error": str(e)
                }
            
            # Format embedding files for frontend
            formatted_files = []
            for emb_file in embedding_files_raw:
                formatted_files.append({
                    "embedding_file_id": emb_file.get("uuid"),
                    "id": emb_file.get("uuid"),  # For frontend compatibility
                    "file_id": emb_file.get("file_id"),
                    "parsed_file_id": emb_file.get("parsed_file_id"),
                    "name": emb_file.get("ui_name", "Embeddings"),
                    "ui_name": emb_file.get("ui_name", "Embeddings"),
                    "embeddings_count": emb_file.get("embeddings_count", 0),
                    "embedding_type": emb_file.get("embedding_type", "structured"),
                    "content_id": emb_file.get("content_id"),
                    "created_at": emb_file.get("created_at"),
                    "status": emb_file.get("status", "active")
                })
            
            self.logger.info(f"✅ Found {len(formatted_files)} embedding files for user: {user_id}")
            
            return {
                "success": True,
                "embedding_files": formatted_files,
                "count": len(formatted_files)
            }
            
        except Exception as e:
            self.logger.error(f"❌ List embedding files failed: {e}", exc_info=True)
            return {
                "success": False,
                "embedding_files": [],
                "count": 0,
                "error": str(e)
            }
    
    async def list_embeddings(
        self,
        user_id: str,
        file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all embeddings for a file (or all for user).
        
        Similar to list_parsed_files().
        
        Args:
            user_id: User identifier
            file_id: Optional file ID to filter embeddings for a specific file
        
        Returns:
            List of embeddings grouped by content_id with metadata
        """
        try:
            self.logger.info(f"📋 Listing embeddings for user: {user_id}" + (f" (file_id: {file_id})" if file_id else ""))
            
            # Get EmbeddingService (Content realm service that can access semantic_data)
            from backend.content.services.embedding_service.embedding_service import EmbeddingService
            
            embedding_service = EmbeddingService(
                service_name="EmbeddingService",
                realm_name="content",
                platform_gateway=self.platform_gateway,
                di_container=self.di_container
            )
            await embedding_service.initialize()
            self.logger.info("✅ EmbeddingService initialized (Content realm)")
            
            # Get user context
            from utilities.security_authorization.request_context import get_request_user_context
            ctx = get_request_user_context()
            if not ctx:
                ctx = {"user_id": user_id}
            else:
                ctx["user_id"] = user_id  # Ensure user_id is set
            
            # Delegate to EmbeddingService.list_embeddings()
            result = await embedding_service.list_embeddings(
                file_id=file_id,
                user_context=ctx
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ List embeddings failed: {e}", exc_info=True)
            return {
                "success": False,
                "embeddings": [],
                "count": 0,
                "error": str(e)
            }
    
    async def preview_embeddings(
        self,
        content_id: str,
        user_id: str,
        max_columns: int = 20
    ) -> Dict[str, Any]:
        """
        Preview semantic layer (embeddings + metadata).
        
        Similar to preview_parsed_file().
        Reconstructs preview from embeddings + metadata (not raw parsed data).
        
        Args:
            content_id: Content ID (semantic layer ID)
            user_id: User identifier
            max_columns: Maximum columns to return (default: 20)
        
        Returns:
            Preview structure with columns, semantic meanings, sample values
        """
        try:
            self.logger.info(f"👁️ Previewing embeddings: content_id={content_id} (max_columns={max_columns})")
            
            # Get EmbeddingService (Content realm service that can access semantic_data)
            from backend.content.services.embedding_service.embedding_service import EmbeddingService
            
            embedding_service = EmbeddingService(
                service_name="EmbeddingService",
                realm_name="content",
                platform_gateway=self.platform_gateway,
                di_container=self.di_container
            )
            await embedding_service.initialize()
            self.logger.info("✅ EmbeddingService initialized (Content realm)")
            
            # Get user context
            from utilities.security_authorization.request_context import get_request_user_context
            ctx = get_request_user_context()
            if not ctx:
                ctx = {"user_id": user_id}
            else:
                ctx["user_id"] = user_id  # Ensure user_id is set
            
            # Delegate to EmbeddingService.preview_embeddings()
            result = await embedding_service.preview_embeddings(
                content_id=content_id,
                max_columns=max_columns,
                user_context=ctx
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Preview embeddings failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _delete_file_handler(self, request_data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Wrapper handler for delete_file that extracts file_id from the request path.
        
        This is called by FrontendGatewayService when the route is matched.
        The file_id is extracted from the endpoint path: /api/v1/content-pillar/delete-file/{file_id}
        """
        try:
            # FrontendGatewayService passes request_data with endpoint, params, user_context, etc.
            if request_data is None:
                request_data = kwargs
            
            # Extract file_id from endpoint path
            endpoint = request_data.get("endpoint", "")
            file_id = None
            
            # Try to extract from endpoint path: /api/v1/content-pillar/delete-file/{file_id}
            if "/delete-file/" in endpoint:
                parts = endpoint.split("/delete-file/")
                if len(parts) > 1:
                    file_id = parts[1].split("/")[0].strip()
            
            # Fallback: try params
            if not file_id:
                params = request_data.get("params", {})
                file_id = params.get("file_id")
            
            if not file_id:
                self.logger.error(f"❌ Could not extract file_id from request. Endpoint: {endpoint}, Params: {request_data.get('params', {})}")
                return {
                    "success": False,
                    "error": "file_id is required",
                    "endpoint": endpoint
                }
            
            # Get user_id from user_context or request_data
            user_id = "anonymous"
            user_context = request_data.get("user_context") or kwargs.get("user_context")
            if user_context:
                user_id = user_context.get("user_id") or "anonymous"
            elif request_data.get("user_id"):
                user_id = request_data.get("user_id")
            
            self.logger.info(f"🗑️ Delete file handler called: file_id={file_id}, user_id={user_id}")
            
            # Call the actual delete_file method
            return await self.delete_file(file_id, user_id)
            
        except Exception as e:
            self.logger.error(f"❌ Delete file handler failed: {e}", exc_info=True)
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_file(self, file_id: str, user_id: str) -> Dict[str, Any]:
        """
        Delete file (Frontend API).
        
        Uses Content Steward to delete file from GCS and Supabase.
        
        Args:
            file_id: File UUID to delete
            user_id: User identifier
        
        Returns:
            Dict with success status
        """
        try:
            self.logger.info(f"🗑️ Deleting file: {file_id}")
            
            # Get Content Steward API
            data_steward = await self.get_data_steward_api()
            if not data_steward:
                return {
                    "success": False,
                    "error": "Content Steward not available"
                }
            
            # Get user context
            ctx = get_request_user_context()
            if not ctx:
                ctx = {"user_id": user_id}
            
            # Delete file via Content Steward
            success = await data_steward.delete_file(file_id, ctx)
            
            if success:
                self.logger.info(f"✅ File deleted successfully: {file_id}")
                return {
                    "success": True,
                    "file_id": file_id,
                    "message": "File deleted successfully"
                }
            else:
                self.logger.warning(f"⚠️ File deletion returned False: {file_id}")
                return {
                    "success": False,
                    "file_id": file_id,
                    "error": "File deletion failed"
                }
            
        except Exception as e:
            self.logger.error(f"❌ Delete file failed: {e}", exc_info=True)
            return {
                "success": False,
                "file_id": file_id,
                "error": str(e)
            }
    
    async def handle_request(
        self,
        method: str,
        path: str,
        params: Dict[str, Any],
        user_context: Dict[str, Any],
        headers: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # Debug logging for all requests
        self.logger.info(f"🔍 [handle_request] {method} {path}, params keys: {list(params.keys())}")
        
        # Special debug logging for list-parsed-files-with-embeddings
        if method == "GET" and "list-parsed-files-with-embeddings" in path:
            self.logger.info(f"🔍 [handle_request] DETECTED list-parsed-files-with-embeddings: method={method}, path={path}, user_context keys: {list(user_context.keys()) if user_context else 'None'}")
        """
        Route requests to appropriate handler methods.
        
        This is called by FrontendGatewayService after pillar-based routing.
        Handles internal routing within the ContentJourneyOrchestrator.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: Request path (e.g., "delete-file/441ab256-...", "process-file")
            params: Request parameters/body
            user_context: User context (user_id, tenant_id, permissions, etc.)
            headers: Optional HTTP headers
            query_params: Optional query parameters
        
        Returns:
            Response dict with success status and data/error
        """
        try:
            user_id = user_context.get("user_id") or "anonymous"
            self.logger.info(f"🔀 [handle_request] {method} {path} for user: {user_id}")
            
            # Route based on method and path
            # DELETE /delete-file/{file_id}?file_type=original|parsed|embedded (OPTIMAL ARCHITECTURE)
            if method == "DELETE" and path.startswith("delete-file/"):
                file_id = path.replace("delete-file/", "").split("/")[0]
                if not file_id:
                    return {"success": False, "error": "file_id is required"}
                # Get file_type from query params (default to "original" for backward compatibility)
                file_type = query_params.get("file_type", "original") if query_params else "original"
                return await self.delete_file_by_type(file_id, file_type, user_id, user_context)
            
            # POST /process-file or POST /process-file/{file_id}
            elif method == "POST" and (path == "process-file" or path.startswith("process-file/")):
                # Extract file_id from path if present (e.g., "process-file/441ab256-...")
                if path.startswith("process-file/"):
                    file_id = path.replace("process-file/", "").split("/")[0]
                else:
                    file_id = params.get("file_id")
                
                if not file_id:
                    return {"success": False, "error": "file_id is required"}
                copybook_file_id = params.get("copybook_file_id")
                processing_options = params.get("processing_options", {})
                return await self.process_file(file_id, user_id, copybook_file_id, processing_options)
            
            # GET /list-uploaded-files
            elif method == "GET" and path == "list-uploaded-files":
                return await self.list_uploaded_files(user_id)
            
            # GET /get-file-statistics
            elif method == "GET" and path == "get-file-statistics":
                return await self.get_file_statistics(user_id)
            
            # GET /dashboard-files (OPTIMAL ARCHITECTURE: unified file list from all three tables)
            elif method == "GET" and path == "dashboard-files":
                return await self.get_dashboard_files(user_id, user_context)
            
            # GET /list-parsed-files
            elif method == "GET" and path == "list-parsed-files":
                file_id = params.get("file_id")  # Optional
                return await self.list_parsed_files(user_id, file_id)
            
            # GET /list-parsed-files-with-embeddings
            elif method == "GET" and path == "list-parsed-files-with-embeddings":
                return await self.list_parsed_files_with_embeddings(user_id)
            
            # GET /list-embedding-files
            elif method == "GET" and path == "list-embedding-files":
                self.logger.info(f"🔍 [handle_request] DETECTED list-embedding-files for user: {user_id}")
                # Extract optional filters from query_params
                parsed_file_id = query_params.get("parsed_file_id") if query_params else None
                file_id = query_params.get("file_id") if query_params else None
                return await self.list_embedding_files(user_id, parsed_file_id=parsed_file_id, file_id=file_id)
            
            # GET /preview-parsed-file/{parsed_file_id}
            elif method == "GET" and path.startswith("preview-parsed-file/"):
                parsed_file_id = path.replace("preview-parsed-file/", "").split("/")[0]
                if not parsed_file_id:
                    return {"success": False, "error": "parsed_file_id is required"}
                # Extract max_rows and max_columns from query params
                max_rows = query_params.get("max_rows", 20) if query_params else 20
                max_columns = query_params.get("max_columns", 20) if query_params else 20
                try:
                    max_rows = int(max_rows) if max_rows else 20
                except (ValueError, TypeError):
                    max_rows = 20
                try:
                    max_columns = int(max_columns) if max_columns else 20
                except (ValueError, TypeError):
                    max_columns = 20
                return await self.preview_parsed_file(parsed_file_id, max_rows, max_columns, user_id)
            
            # POST /create-embeddings (Data Mash - semantic layer creation)
            elif method == "POST" and path == "create-embeddings":
                parsed_file_id = params.get("parsed_file_id")
                file_id = params.get("file_id")  # Optional
                if not parsed_file_id:
                    return {"success": False, "error": "parsed_file_id is required"}
                
                # ✅ Ensure workflow_id from request params is in user_context
                if not user_context:
                    user_context = {}
                # Extract workflow_id from params (may be in request body) and add to user_context
                workflow_id_from_params = params.get("workflow_id")
                if workflow_id_from_params and not user_context.get("workflow_id"):
                    user_context["workflow_id"] = workflow_id_from_params
                
                return await self.create_embeddings(parsed_file_id, user_id, file_id, user_context)
            
            # GET /list-embeddings (Data Mash - list semantic layer files)
            elif method == "GET" and path == "list-embeddings":
                file_id = params.get("file_id")  # Optional
                return await self.list_embeddings(user_id, file_id)
            
            # GET /preview-embeddings/{content_id} (Data Mash - preview semantic layer)
            elif method == "GET" and path.startswith("preview-embeddings/"):
                content_id = path.replace("preview-embeddings/", "").split("/")[0]
                if not content_id:
                    return {"success": False, "error": "content_id is required"}
                max_columns = params.get("max_columns", 20)
                return await self.preview_embeddings(content_id, user_id, max_columns)
            
            # POST /upload-file (handled by universal_pillar_router with multipart)
            elif method == "POST" and path == "upload-file":
                # This is handled differently (multipart form data)
                # Extract file data and copybook data from params
                file_data = params.get("file_data")
                filename = params.get("filename")
                file_type = params.get("file_type") or params.get("content_type")
                session_id = user_context.get("session_id") if user_context else None
                
                # ⭐ NEW: Extract content_type and file_type_category from params (from frontend FormData)
                explicit_content_type = params.get("content_type")  # From frontend selection
                explicit_file_type_category = params.get("file_type_category")  # From frontend selection
                
                # Add to user_context so handle_content_upload can use them
                if not user_context:
                    user_context = {}
                if explicit_content_type:
                    user_context["content_type"] = explicit_content_type
                if explicit_file_type_category:
                    user_context["file_type_category"] = explicit_file_type_category
                
                # Extract copybook data if present
                copybook_data = params.get("copybook_data")
                copybook_filename = params.get("copybook_filename")
                
                if not file_data or not filename:
                    return {"success": False, "error": "file_data and filename are required"}
                
                # If copybook is provided, upload it first to get copybook_file_id
                copybook_file_id = None
                if copybook_data and copybook_filename:
                    self.logger.info(f"📎 Uploading copybook first: {copybook_filename}")
                    try:
                        # Upload copybook file first
                        copybook_result = await self.upload_file(
                            file_data=copybook_data,
                            filename=copybook_filename,
                            file_type="text/plain",
                            user_id=user_id,
                            session_id=session_id,
                            user_context=user_context
                        )
                        
                        if copybook_result.get("success"):
                            copybook_file_id = copybook_result.get("file_id")
                            self.logger.info(f"✅ Copybook uploaded successfully: {copybook_file_id}")
                            # Add copybook_file_id to user_context for main file upload
                            if not user_context:
                                user_context = {}
                            user_context["copybook_file_id"] = copybook_file_id
                        else:
                            self.logger.warning(f"⚠️ Copybook upload failed: {copybook_result.get('error')}")
                    except Exception as e:
                        self.logger.error(f"❌ Copybook upload failed: {e}", exc_info=True)
                
                # Upload main file (with copybook_file_id in user_context if copybook was uploaded)
                result = await self.upload_file(
                    file_data=file_data,
                    filename=filename,
                    file_type=file_type,
                    user_id=user_id,
                    session_id=session_id,
                    user_context=user_context
                )
                
                # Add copybook_file_id to result if we uploaded one
                if copybook_file_id:
                    result["copybook_file_id"] = copybook_file_id
                
                return result
            
            # Route not found
            else:
                self.logger.warning(f"⚠️ Route not found: {method} {path}")
                return {
                    "success": False,
                    "error": "Route not found",
                    "method": method,
                    "path": path
                }
                
        except Exception as e:
            self.logger.error(f"❌ Error handling request: {e}", exc_info=True)
            return {"success": False, "error": str(e)}


