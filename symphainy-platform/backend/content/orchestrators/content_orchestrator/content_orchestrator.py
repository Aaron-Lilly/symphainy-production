#!/usr/bin/env python3
"""
Content Analysis Orchestrator for MVP Use Case

WHAT: Orchestrates enabling services for MVP content analysis features
HOW: Delegates to FileParser, DataAnalyzer, MetricsCalculator while preserving UI integration

This orchestrator provides the same API surface as the old ContentPillar to preserve
UI integration, but internally delegates to first-class enabling services.
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

# Try to import pandas and pyarrow for parquet conversion
try:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    PANDAS_AVAILABLE = True
    PYARROW_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    PYARROW_AVAILABLE = False
    pd = None
    pa = None
    pq = None


class ContentOrchestrator(OrchestratorBase):
    """
    Content Orchestrator for MVP use case.
    
    Extends OrchestratorBase for Smart City access and orchestrator capabilities.
    Preserves MVP UI integration while delegating to enabling services.
    
    OLD: ContentPillar did everything internally
    NEW: Delegates to FileParserService, DataAnalyzerService, MetricsCalculatorService
    
    This orchestrator has an MCP Server that exposes use case-level tools for agents.
    """
    
    def __init__(self, delivery_manager):
        """
        Initialize Content Orchestrator.
        
        Args:
            delivery_manager: Reference to DeliveryManagerService for service access
        """
        # Extract parameters from delivery_manager (which extends ManagerServiceBase)
        # ✅ FIXED: Use "content" realm_name (not from delivery_manager which might be "business_enablement")
        super().__init__(
            service_name="ContentOrchestratorService",
            realm_name="content",  # ✅ Content realm (not business_enablement)
            platform_gateway=delivery_manager.platform_gateway,
            di_container=delivery_manager.di_container,
            business_orchestrator=delivery_manager  # Keep for backward compatibility during migration
        )
        self.delivery_manager = delivery_manager
        # Set a shorter orchestrator name for MVP UI compatibility
        self.orchestrator_name = "ContentOrchestrator"
        
        # Enabling services (lazy initialization - created on first use)
        self._file_parser_service = None
        self._data_analyzer_service = None
        
        # NOTE: File storage is handled by FileManagementAbstraction (GCS + Supabase)
        # No in-memory storage needed - files are persisted via infrastructure abstractions
    
    async def _get_file_parser_service(self):
        """
        Lazy initialization of File Parser Service using four-tier access pattern.
        
        Tier 1: Enabling Service (via Curator) - use get_enabling_service()
        Tier 2: Direct import and initialization (fallback)
        Tier 3: N/A (no SOA API or Platform Gateway equivalent)
        Tier 4: Return None (calling code handles None gracefully)
        """
        if self._file_parser_service is None:
            try:
                # Tier 1: Try Enabling Service via Curator (four-tier pattern)
                file_parser = await self.get_enabling_service("FileParserService")
                if file_parser:
                    self._file_parser_service = file_parser
                    self.logger.info("✅ File Parser Service discovered via Curator")
                    return file_parser
                
                # Tier 2: Fallback - Import and initialize directly
                self.logger.warning("⚠️ File Parser Service not found via Curator, initializing directly")
                from backend.business_enablement.enabling_services.file_parser_service import FileParserService
                
                self._file_parser_service = FileParserService(
                    service_name="FileParserService",
                    realm_name="business_enablement",
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await self._file_parser_service.initialize()
                self.logger.info("✅ File Parser Service initialized directly")
                
            except Exception as e:
                self.logger.error(f"❌ File Parser Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                # Tier 4: Return None - calling code handles None gracefully with structured error
                return None
        
        return self._file_parser_service
    
    async def _get_data_analyzer_service(self):
        """
        Lazy initialization of Data Analyzer Service using four-tier access pattern.
        
        Tier 1: Enabling Service (via Curator) - use get_enabling_service()
        Tier 2: Direct import and initialization (fallback)
        Tier 3: N/A (no SOA API or Platform Gateway equivalent)
        Tier 4: Return None (calling code handles None gracefully)
        """
        if self._data_analyzer_service is None:
            try:
                # Tier 1: Try Enabling Service via Curator (four-tier pattern)
                data_analyzer = await self.get_enabling_service("DataAnalyzerService")
                if data_analyzer:
                    self._data_analyzer_service = data_analyzer
                    self.logger.info("✅ Data Analyzer Service discovered via Curator")
                    return data_analyzer
                
                # Tier 2: Fallback - Import and initialize directly
                self.logger.warning("⚠️ Data Analyzer Service not found via Curator, initializing directly")
                from backend.business_enablement.enabling_services.data_analyzer_service import DataAnalyzerService
                
                self._data_analyzer_service = DataAnalyzerService(
                    service_name="DataAnalyzerService",
                    realm_name="business_enablement",
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await self._data_analyzer_service.initialize()
                self.logger.info("✅ Data Analyzer Service initialized directly")
                
            except Exception as e:
                self.logger.error(f"❌ Data Analyzer Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                # Tier 4: Return None - calling code handles None gracefully with structured error
                return None
        
        return self._data_analyzer_service
    
    async def _get_data_solution_orchestrator(self):
        """
        Get Data Solution Orchestrator Service via Curator discovery.
        
        This is the ONLY way to access data operations in the platform.
        Hard fails if Data Solution Orchestrator is not available.
        
        Returns:
            DataSolutionOrchestratorService instance
        
        Raises:
            ValueError: If Data Solution Orchestrator Service is not available
        """
        try:
            # Discover via Curator (Solution realm service)
            curator = await self.get_foundation_service("CuratorFoundationService")
            if not curator:
                raise ValueError("Curator not available - cannot discover Data Solution Orchestrator Service")
            
            data_solution_service = await curator.get_service("DataSolutionOrchestratorService")
            if not data_solution_service:
                raise ValueError("Data Solution Orchestrator Service not available - must be registered in Solution realm")
            
            return data_solution_service
        except Exception as e:
            self.logger.error(f"❌ Failed to get Data Solution Orchestrator Service: {e}")
            raise ValueError(f"Data Solution Orchestrator Service not available: {e}")
    
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
            
            # ⚠️ TEMPORARY: Optional import for SpecialistCapability
            # TODO (Section 1.3): Properly implement business_specialist_agent_protocol when overhauling agents
            # This import is optional to allow orchestrator initialization without the protocol module
            try:
                from backend.business_enablement.protocols.business_specialist_agent_protocol import SpecialistCapability
                specialist_capability = SpecialistCapability.CONTENT_PROCESSING
            except ImportError:
                self.logger.warning("⚠️ business_specialist_agent_protocol not available - skipping specialist_capability (will be fixed in Section 1.3)")
                specialist_capability = None
            
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
                specialist_capability=specialist_capability  # May be None if protocol not available
            )
            
            # Give specialist agent access to orchestrator (for MCP server access)
            if self.processing_agent and hasattr(self.processing_agent, 'set_orchestrator'):
                self.processing_agent.set_orchestrator(self)
            
            # Initialize MCP Server (exposes orchestrator methods as MCP tools)
            from .mcp_server import ContentAnalysisMCPServer
            
            self.mcp_server = ContentAnalysisMCPServer(
                orchestrator=self,
                di_container=self.delivery_manager.di_container
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
                    }
                ],
                soa_apis=["handle_content_upload", "parse_file", "analyze_document", "extract_entities"],
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
        user_context: Optional[Dict[str, Any]] = None  # ✅ NEW: User context with permissions from request
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
            content_info = determine_content_type(
                file_components["file_extension"],
                file_type
            )
            # Result: {
            #   "content_type": "unstructured",
            #   "file_type_category": "document"
            # }
            
            # Track orchestrator workflow if session_id provided
            workflow_id = None
            if session_id and hasattr(self.delivery_manager, 'session_manager') and self.delivery_manager.session_manager:
                workflow_id = f"upload_{file_components['ui_name']}_{datetime.utcnow().timestamp()}"
                # Note: Delivery Manager may not have track_orchestrator_workflow - this is optional
                if hasattr(self.delivery_manager, 'track_orchestrator_workflow'):
                    await self.delivery_manager.track_orchestrator_workflow(
                        session_id=session_id,
                        orchestrator_name="ContentAnalysisOrchestrator",
                        workflow_data={
                            "workflow_id": workflow_id,
                            "status": "processing",
                            "started_at": datetime.utcnow().isoformat(),
                            "enabling_services": ["ContentSteward"],
                            "operation": "file_upload",
                            "filename": filename,
                            "ui_name": file_components["ui_name"]
                        }
                    )
            
            # ========================================================================
            # Call Smart City services directly (Content Steward)
            # ========================================================================
            # ContentOrchestrator is called BY DataSolutionOrchestratorService via ClientDataJourneyOrchestratorService
            # So we should NOT call DataSolutionOrchestratorService here (that would create a circular dependency)
            # Instead, call Smart City services directly
            # ========================================================================
                
            # Use Content Steward for proper file storage (GCS + Supabase)
            # Access via OrchestratorBase (delegates to RealmServiceBase)
            data_steward = await self.get_data_steward_api()
            
            if not data_steward:
                raise Exception("Content Steward service not available - file upload requires infrastructure")
            
            # Prepare metadata for Content Steward with proper field names
            # Check if this is an SOP/Workflow file that should be processed in Operations Pillar
            processing_pillar = None
            if content_info["file_type_category"] == "sop_workflow":
                processing_pillar = "operations_pillar"
                self.logger.info(f"📋 File marked for Operations Pillar processing: {filename}")
            
            metadata = {
                "user_id": user_id,
                "ui_name": file_components["ui_name"],  # ✅ Correct field name
                "file_type": file_components["file_extension_clean"],  # ✅ Extension, not MIME
                "mime_type": file_type,  # ✅ MIME type separately
                "original_filename": file_components["original_filename"],  # ✅ Full original name
                "file_extension": file_components["file_extension"],  # ✅ Extension with dot
                "content_type": content_info["content_type"],  # ✅ For Supabase schema
                "file_type_category": content_info["file_type_category"],  # ✅ For processing logic
                "processing_pillar": processing_pillar,  # ✅ NEW: Mark for Operations Pillar if SOP/Workflow
                "uploaded_at": datetime.utcnow().isoformat(),
                "size_bytes": len(file_data)
            }
                
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
                if session_id and workflow_id and hasattr(self.delivery_manager, 'session_manager') and self.delivery_manager.session_manager:
                    if hasattr(self.delivery_manager, 'track_orchestrator_workflow'):
                        await self.delivery_manager.track_orchestrator_workflow(
                            session_id=session_id,
                            orchestrator_name="ContentAnalysisOrchestrator",
                            workflow_data={
                                "workflow_id": workflow_id,
                                "status": "completed",
                                "completed_at": datetime.utcnow().isoformat(),
                                "file_id": file_uuid
                            }
                        )
                
                # Step 5: Return with proper field names
                # Build return dict - handle both Data Solution Orchestrator and old pattern
                return_dict = {
                    "success": True,
                    "file_id": file_uuid,
                    "uuid": file_uuid,
                    "workflow_id": workflow_id,  # Return workflow_id for frontend
                    "orchestrator": "ContentAnalysisOrchestrator"
                }
                
                # Add metadata fields
                return_dict.update({
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
                })
                
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
        user_context: Optional[Dict[str, Any]] = None  # ✅ NEW: User context with permissions
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
            user_context: Optional user context with permissions from request
        
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
        # ✅ Get user context from request-scoped context
        from utilities.security_authorization.request_context import get_request_user_context
        ctx = get_request_user_context()
        
        if ctx:
            self.logger.debug(f"✅ [process_file] Using user context: user_id={ctx.get('user_id')}, tenant_id={ctx.get('tenant_id')}, permissions={ctx.get('permissions')}")
        else:
            self.logger.warning(f"⚠️ [process_file] No user context available in request context")
        
        """
        Process file (parsing + metadata extraction) - Frontend Gateway API compatibility.
        
        PHASE 1 FIX: Returns only metadata/summary (not full parsed data).
        - Full parsed data (with numpy types) is stored as parquet in GCS
        - API response contains only metadata to avoid numpy serialization errors
        - Frontend will use embeddings + metadata for previews (Phase 4)
        
        Args:
            file_id: File UUID
            user_id: User identifier
            copybook_file_id: Optional copybook file UUID
            processing_options: Optional processing options
        
        Returns:
            Processing result with metadata only (no full parsed data):
            - parse_result: Metadata, structure, counts (no tables/records/data)
            - parsed_file_id: Reference to stored parquet file
            - file_details: File metadata
        """
        try:
            self.logger.info(f"⚙️ Processing file: {file_id}")
            
            # ========================================================================
            # Call Smart City services directly (FileParserService, Content Steward)
            # ========================================================================
            # ContentOrchestrator is called BY DataSolutionOrchestratorService via ClientDataJourneyOrchestratorService
            # So we should NOT call DataSolutionOrchestratorService here (that would create a circular dependency)
            # Instead, call Smart City services directly
            # ========================================================================
            
            # Get FileParserService (enabling service)
            file_parser = await self._get_file_parser_service()
            if not file_parser:
                return {
                    "success": False,
                    "file_id": file_id,
                    "error": "FileParserService not available - parsing requires enabling services"
                }
            
            # Prepare parse options
            parse_options = processing_options or {}
            if copybook_file_id:
                parse_options["copybook_file_id"] = copybook_file_id
            
            # Parse file via FileParserService
            parse_result = await file_parser.parse_file(
                file_id=file_id,
                parse_options=parse_options,
                user_context={"user_id": user_id}  # Minimal user_context for parsing
            )
            
            if not parse_result.get("success"):
                return {
                    "success": False,
                    "file_id": file_id,
                    "error": parse_result.get("error", "File parsing failed"),
                    "parse_result": parse_result
                }
            
            # ========================================================================
            # PHASE 1 FIX: Convert parsed data to parquet and store via Content Steward
            # ========================================================================
            parsed_file_id = None
            content_type = parse_result.get("parsing_type", "structured")  # structured, unstructured, hybrid
            
            # Force debug output to stderr (always visible)
            import sys
            sys.stderr.write(f"\n🔍🔍🔍 [process_file] content_type: {content_type}, parse_result.success: {parse_result.get('success')}\n")
            sys.stderr.write(f"🔍🔍🔍 [process_file] parse_result keys: {list(parse_result.keys())}\n")
            sys.stderr.flush()
            
            self.logger.error(f"🔍🔍🔍 [process_file] content_type: {content_type}, parse_result.success: {parse_result.get('success')}")
            self.logger.error(f"🔍🔍🔍 [process_file] parse_result keys: {list(parse_result.keys())}")
            
            # Only save as parquet for structured data (has tables/records)
            if content_type == "structured" and parse_result.get("success"):
                sys.stderr.write(f"🔍🔍🔍 [process_file] Attempting to convert to parquet and store...\n")
                sys.stderr.flush()
                self.logger.error(f"🔍🔍🔍 [process_file] Attempting to convert to parquet and store...")
                try:
                    # Convert parsed data to parquet bytes
                    sys.stderr.write(f"🔍🔍🔍 [process_file] Calling _convert_to_parquet_bytes()...\n")
                    sys.stderr.flush()
                    parquet_bytes = await self._convert_to_parquet_bytes(parse_result)
                    sys.stderr.write(f"🔍🔍🔍 [process_file] _convert_to_parquet_bytes() returned: {parquet_bytes is not None} (size: {len(parquet_bytes) if parquet_bytes else 0})\n")
                    sys.stderr.flush()
                    
                    # Validate parquet bytes before storing (validation is now in _convert_to_parquet_bytes)
                    if parquet_bytes:
                        # Double-check validation
                        if len(parquet_bytes) >= 4:
                            magic_bytes = parquet_bytes[:4]
                            footer_magic = parquet_bytes[-4:] if len(parquet_bytes) >= 4 else None
                            if magic_bytes == b'PAR1' and footer_magic == b'PAR1':
                                self.logger.info(f"✅ [process_file] Parquet bytes validated before storage: {len(parquet_bytes)} bytes, header={magic_bytes}, footer={footer_magic}")
                            else:
                                self.logger.error(f"❌ [process_file] Invalid parquet bytes: header={magic_bytes}, footer={footer_magic}")
                                parquet_bytes = None
                        else:
                            self.logger.error(f"❌ [process_file] Parquet bytes too short: {len(parquet_bytes)} bytes")
                            parquet_bytes = None
                    
                    if parquet_bytes:
                        # Get Content Steward API
                        data_steward = await self.get_data_steward_api()
                        if data_steward:
                            # ✅ Use request-scoped context (no need to pass user_context)
                            # store_parsed_file will get context from request_context automatically
                            # Store parsed file via Content Steward
                            store_result = await data_steward.store_parsed_file(
                                file_id=file_id,
                                parsed_file_data=parquet_bytes,
                                format_type="parquet",
                                content_type=content_type,
                                parse_result=parse_result,
                                workflow_id=None
                            )
                            
                            if store_result:
                                # store_parsed_file returns parsed_file_id at top level (for backward compatibility)
                                parsed_file_id = (
                                    store_result.get("parsed_file_id") or
                                    store_result.get("data", {}).get("parsed_file_id")  # Fallback to nested format
                                )
                                if parsed_file_id:
                                    self.logger.info(f"✅ Stored parsed file as parquet: parsed_file_id={parsed_file_id}")
                                else:
                                    self.logger.warning(f"⚠️ store_parsed_file did not return parsed_file_id. Result keys: {list(store_result.keys())}")
                                    self.logger.warning(f"   store_result.get('data'): {store_result.get('data')}")
                            else:
                                self.logger.warning(f"⚠️ store_parsed_file returned None")
                        else:
                            self.logger.warning(f"⚠️ Content Steward not available - cannot store parsed file")
                    else:
                        self.logger.warning(f"⚠️ Failed to convert parsed data to parquet bytes")
                except Exception as e:
                    self.logger.error(f"❌ Failed to store parsed file: {e}", exc_info=True)
                    # Continue - don't fail the entire operation if storage fails
            
            # Get file details (includes metadata)
            file_details = await self.get_file_details(file_id, user_id)
            
            # Combine results
            import uuid
            workflow_id = str(uuid.uuid4())  # Generate workflow_id for response
            
            # ========================================================================
            # PHASE 1 FIX: Return only metadata/summary (not full parsed data)
            # ========================================================================
            # The full parsed data (with numpy types) is stored as parquet in GCS.
            # API responses return only metadata to avoid numpy serialization errors.
            # Frontend will use embeddings + metadata for previews (Phase 4).
            # ========================================================================
            
            # Sanitize metadata and structure first to convert any numpy types
            # CRITICAL: Sanitize the entire parse_result first to catch any numpy types
            sanitized_parse_result = self._sanitize_for_json(parse_result)
            sanitized_metadata = sanitized_parse_result.get("metadata", {})
            sanitized_structure = sanitized_parse_result.get("structure", {})
            
            # Calculate counts safely (ensure they're native Python ints, not numpy types)
            # NOTE: We get counts from parse_result, but we DON'T include tables/records in response
            # Use sanitized_parse_result to ensure counts are already converted
            tables = sanitized_parse_result.get("tables", [])
            records = sanitized_parse_result.get("records", [])
            table_count = int(len(tables)) if tables else 0
            record_count = int(len(records)) if records else 0
            
            # Build parse_summary with ONLY metadata (no full data)
            # Explicitly exclude: tables, records, data (full parsed data)
            parse_summary = {
                "success": sanitized_parse_result.get("success", False),
                "parsing_type": sanitized_parse_result.get("parsing_type", "unknown"),
                "file_type": sanitized_parse_result.get("file_type"),
                "metadata": sanitized_metadata,  # Schema, column names, data types, etc.
                "structure": sanitized_structure,  # Structure info (table layout, etc.)
                "table_count": table_count,  # Count only (not full tables)
                "record_count": record_count,  # Count only (not full records)
                "parsed_at": sanitized_parse_result.get("parsed_at")
            }
            
            # Explicitly remove any full data that might have leaked through
            # This ensures we never return tables, records, or data arrays
            parse_summary.pop("tables", None)
            parse_summary.pop("records", None)
            parse_summary.pop("data", None)
            
            # Sanitize the summary itself (in case parsed_at or other fields contain numpy types)
            parse_summary = self._sanitize_for_json(parse_summary)
            
            # Build result - sanitize file_details as well
            sanitized_file_details = self._sanitize_for_json(file_details.get("file", {}))
            
            # Extract parsed_file_id - prioritize the one from store_parsed_file() call above
            # If not set (e.g., storage failed or not structured), try parse_result
            if not parsed_file_id:
                parsed_file_id = (
                    sanitized_parse_result.get("parsed_file_id") or
                    sanitized_parse_result.get("parquet_file_id") or
                    sanitized_parse_result.get("file_id") or
                    sanitized_parse_result.get("uuid") or
                    file_id  # Fallback to original file_id if parsed_file_id not found
                )
            
            # If still None, try to get from file_details
            if not parsed_file_id or parsed_file_id == file_id:
                parsed_file_id = sanitized_file_details.get("parsed_file_id") or file_id
            
            result = {
                "success": True,
                "file_id": file_id,
                "parse_result": parse_summary,  # Only metadata/summary, not full data
                "parsed_file_id": parsed_file_id,  # Reference to stored parquet file
                "file_details": sanitized_file_details,
                "copybook_file_id": copybook_file_id,
                "workflow_id": workflow_id,
                "message": "Parsing completed successfully",
                "note": "Full parsed data (with numpy types) stored as parquet in GCS. Use parsed_file_id to retrieve. Frontend previews will use embeddings + metadata (Phase 4)."
            }
            
            # Final sanitization pass to catch any remaining numpy types
            # This is critical - ensures ALL numpy types are converted before FastAPI's encoder runs
            # Sanitize multiple times to catch nested numpy types
            sanitized_result = self._sanitize_for_json(result)
            sanitized_result = self._sanitize_for_json(sanitized_result, visited=set())  # Second pass with fresh visited set
            sanitized_result = self._sanitize_for_json(sanitized_result, visited=set())  # Third pass to be absolutely sure
            
            # Double-check: verify no numpy types remain
            try:
                import json
                # Try to serialize to verify it's JSON-safe
                json.dumps(sanitized_result)
                self.logger.info("✅ Final sanitization verified - response is JSON-safe")
            except (TypeError, ValueError) as e:
                self.logger.error(f"❌ Sanitized result still contains non-serializable types: {e}")
                self.logger.error(f"   Result keys: {list(sanitized_result.keys()) if isinstance(sanitized_result, dict) else 'not a dict'}")
                # Debug: Try to find where the numpy type is
                try:
                    import numpy as np
                    def find_numpy_types(obj, path=""):
                        """Recursively find numpy types in object."""
                        if isinstance(obj, dict):
                            for k, v in obj.items():
                                find_numpy_types(v, f"{path}.{k}")
                        elif isinstance(obj, (list, tuple)):
                            for i, item in enumerate(obj):
                                find_numpy_types(item, f"{path}[{i}]")
                        elif hasattr(obj, '__class__') and hasattr(obj.__class__, '__module__'):
                            if obj.__class__.__module__ == 'numpy':
                                self.logger.error(f"   Found numpy type at {path}: {type(obj).__name__}")
                    find_numpy_types(sanitized_result)
                except Exception as debug_error:
                    self.logger.error(f"   Debug search failed: {debug_error}")
                
                # Last resort: return minimal safe response
                return {
                    "success": True,
                    "file_id": file_id,
                    "parse_result": {
                        "success": sanitized_parse_result.get("success", False),
                        "parsing_type": sanitized_parse_result.get("parsing_type", "unknown"),
                        "file_type": sanitized_parse_result.get("file_type"),
                        "table_count": table_count,
                        "record_count": record_count,
                        "note": "Full parsed data available via parsed_file_id (contains numpy types for parquet storage)"
                    },
                    "parsed_file_id": sanitized_parse_result.get("parsed_file_id"),
                    "workflow_id": workflow_id,
                    "message": "Parsing completed successfully (response sanitized due to numpy types)",
                    "error": "Response contained non-serializable types - data stored but not returned in JSON"
                }
            
            return sanitized_result
            
        except Exception as e:
            self.logger.error(f"❌ File processing failed: {e}")
            return {
                "success": False,
                "file_id": file_id,
                "error": str(e)
            }
    
    def _sanitize_for_json(self, data: Any, visited: Optional[set] = None) -> Any:
        """
        Sanitize data for JSON serialization by converting numpy types and other non-serializable types.
        
        Args:
            data: Data to sanitize
            visited: Set of visited object IDs to detect circular references
        
        Returns:
            Sanitized data (only JSON-serializable types)
        """
        if visited is None:
            visited = set()
        
        # Handle None
        if data is None:
            return None
        
        # Handle circular references
        obj_id = id(data)
        if obj_id in visited:
            return "<circular_reference>"
        visited.add(obj_id)
        
        try:
            # Handle numpy types FIRST (before simple types, as numpy.int64 might pass isinstance checks)
            try:
                import numpy as np
                # Check for numpy scalar types using isinstance
                if isinstance(data, (np.integer, np.int64, np.int32, np.int16, np.int8, np.uint64, np.uint32, np.uint16, np.uint8)):
                    return int(data)
                if isinstance(data, (np.floating, np.float64, np.float32, np.float16)):
                    return float(data)
                if isinstance(data, np.bool_):
                    return bool(data)
                # Check for numpy types by module name (catches all numpy types)
                if hasattr(data, '__class__') and hasattr(data.__class__, '__module__'):
                    if data.__class__.__module__ == 'numpy':
                        # Try .item() method first (works for scalars)
                        if hasattr(data, 'item'):
                            try:
                                return data.item()
                            except (ValueError, AttributeError):
                                pass
                        # For arrays, convert to list
                        if isinstance(data, np.ndarray):
                            return [self._sanitize_for_json(item, visited) for item in data.tolist()]
                        # Fallback: try to convert to native Python type
                        try:
                            if isinstance(data, (np.integer,)):
                                return int(data)
                            if isinstance(data, (np.floating,)):
                                return float(data)
                            if isinstance(data, (np.bool_,)):
                                return bool(data)
                        except (ValueError, TypeError):
                            return str(data)  # Last resort: convert to string
            except (ImportError, AttributeError, ValueError, TypeError) as e:
                # If numpy conversion fails, continue to other type checks
                pass
            
            # Handle simple types (after numpy check)
            if isinstance(data, (str, int, float, bool)):
                return data
            
            # Handle datetime
            if isinstance(data, datetime):
                return data.isoformat()
            
            # Handle dict
            if isinstance(data, dict):
                # CRITICAL: Sanitize both keys and values (keys might be numpy types)
                sanitized_dict = {}
                for k, v in data.items():
                    # Sanitize key first (in case it's a numpy type)
                    sanitized_key = self._sanitize_for_json(k, visited)
                    # Ensure key is a string (dict keys must be strings for JSON)
                    if not isinstance(sanitized_key, str):
                        sanitized_key = str(sanitized_key)
                    # Sanitize value
                    sanitized_dict[sanitized_key] = self._sanitize_for_json(v, visited)
                return sanitized_dict
            
            # Handle list/tuple
            if isinstance(data, (list, tuple)):
                return [self._sanitize_for_json(item, visited) for item in data]
            
            # Handle objects with __dict__
            if hasattr(data, '__dict__'):
                return self._sanitize_for_json(data.__dict__, visited)
            
            # Try to convert to string for other types
            try:
                return str(data)
            except Exception:
                return "<non_serializable>"
        
        finally:
            visited.discard(obj_id)
    
    async def _convert_to_parquet_bytes(self, parse_result: Dict[str, Any]) -> Optional[bytes]:
        """
        Convert parsed data to parquet bytes (in-memory).
        
        Based on ParquetComposer pattern from business_enablement_old.
        Extracts structured data from parse_result and converts to parquet format.
        
        Args:
            parse_result: Parse result dictionary with tables, records, or data
        
        Returns:
            Parquet file bytes, or None if conversion fails
        """
        try:
            if not PANDAS_AVAILABLE or not PYARROW_AVAILABLE:
                self.logger.warning("⚠️ pandas/pyarrow not available - cannot convert to parquet")
                return None
            
            # Extract structured data from parse_result (based on ParquetComposer._extract_structured_data)
            records = []
            
            # Check for tables (list of tables)
            if "tables" in parse_result and isinstance(parse_result["tables"], list):
                for table in parse_result["tables"]:
                    if isinstance(table, list):
                        records.extend(table)
                    elif isinstance(table, dict):
                        records.append(table)
            
            # Check for records (list of records)
            if "records" in parse_result and isinstance(parse_result["records"], list):
                records.extend(parse_result["records"])
            
            # Check for data (structured data)
            if "data" in parse_result:
                data = parse_result["data"]
                if isinstance(data, list):
                    records.extend(data)
                elif isinstance(data, dict):
                    records.append(data)
            
            if not records:
                self.logger.warning("⚠️ No structured data found in parse_result - cannot convert to parquet")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            if df.empty:
                self.logger.warning("⚠️ DataFrame is empty - cannot convert to parquet")
                return None
            
            # Convert to PyArrow Table
            table = pa.Table.from_pandas(df)
            
            # Write to Parquet in memory (BytesIO)
            parquet_buffer = io.BytesIO()
            pq.write_table(table, parquet_buffer, compression='snappy')
            parquet_bytes = parquet_buffer.getvalue()
            
            # Validate parquet bytes before returning
            if len(parquet_bytes) >= 4:
                magic_bytes = parquet_bytes[:4]
                footer_magic = parquet_bytes[-4:] if len(parquet_bytes) >= 4 else None
                if magic_bytes == b'PAR1' and footer_magic == b'PAR1':
                    self.logger.info(f"✅ Converted to parquet: {len(df)} rows, {len(df.columns)} columns, {len(parquet_bytes)} bytes")
                    self.logger.info(f"   ✅ Parquet validation: header={magic_bytes}, footer={footer_magic}")
                else:
                    self.logger.error(f"❌ Invalid parquet bytes: header={magic_bytes}, footer={footer_magic}")
                    return None
            else:
                self.logger.error(f"❌ Parquet bytes too short: {len(parquet_bytes)} bytes")
                return None
            
            return parquet_bytes
            
        except Exception as e:
            self.logger.error(f"❌ Failed to convert to parquet bytes: {e}", exc_info=True)
            return None
    
    async def embed_content(
        self,
        file_id: str,
        parsed_file_id: str,
        content_metadata: Dict[str, Any],
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create semantic embeddings for parsed content (Frontend API).
        
        Phase 2: Enhanced Embedding Storage
        - Creates representative embeddings (every 10th row)
        - Stores enhanced metadata (data_type, semantic_meaning, sample_values, etc.)
        - Stores via SemanticDataAbstraction (ArangoDB)
        
        Args:
            file_id: File UUID
            parsed_file_id: Parsed file identifier (parquet in GCS)
            content_metadata: Content metadata from parsing (includes schema, columns, etc.)
            user_id: User identifier
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Embedding result with success status, embeddings_count, content_id, workflow_id
        """
        try:
            workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
            self.logger.info(f"🧬 Creating embeddings: file_id={file_id}, parsed_file_id={parsed_file_id} (workflow_id: {workflow_id})")
            
            # Get EmbeddingService (Content realm service)
            try:
                from backend.content.services.embedding_service.embedding_service import EmbeddingService
                
                embedding_service = EmbeddingService(
                    service_name="EmbeddingService",
                    realm_name="content",  # ✅ Content realm service
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await embedding_service.initialize()
                self.logger.info("✅ EmbeddingService initialized (Content realm)")
            except Exception as e:
                self.logger.error(f"❌ EmbeddingService initialization failed: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": f"EmbeddingService not available: {str(e)}",
                    "workflow_id": workflow_id
                }
            
            # Create representative embeddings
            embeddings_result = await embedding_service.create_representative_embeddings(
                parsed_file_id=parsed_file_id,
                content_metadata=content_metadata,
                sampling_strategy="every_nth",
                n=10,  # Every 10th row
                user_context=user_context
            )
            
            if not embeddings_result.get("success"):
                self.logger.error(f"❌ Embedding creation failed: {embeddings_result.get('error')}")
                return {
                    "success": False,
                    "error": embeddings_result.get("error", "Embedding creation failed"),
                    "workflow_id": workflow_id
                }
            
            content_id = embeddings_result.get("content_id") or content_metadata.get("content_id") or content_metadata.get("metadata_id")
            embeddings_count = embeddings_result.get("embeddings_count", 0) or embeddings_result.get("stored_count", 0)
            
            self.logger.info(f"✅ Created {embeddings_count} embeddings for content {content_id} (workflow_id: {workflow_id})")
            
            return {
                "success": True,
                "embeddings_count": embeddings_count,
                "content_id": content_id,  # Ensure content_id is always returned
                "file_id": file_id,
                "parsed_file_id": parsed_file_id,
                "workflow_id": workflow_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ Embed content failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "embed_content")
            workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def list_uploaded_files(self, user_id: str) -> Dict[str, Any]:
        """
        List uploaded files for user (File Dashboard).
        
        Uses FileManagementAbstraction via Platform Gateway to query Supabase for user's files.
        
        Args:
            user_id: User identifier
        
        Returns:
            List of uploaded files with metadata
        """
        try:
            self.logger.info(f"📋 Listing uploaded files for user: {user_id}")
            
            # Get FileManagementAbstraction via Platform Gateway (Tier 3 access pattern)
            file_management = self.get_abstraction("file_management")
            if not file_management:
                return {
                    "success": False,
                    "files": [],
                    "count": 0,
                    "error": "File Management abstraction not available"
                }
            
            # List files for user via FileManagementAbstraction
            try:
                files = await file_management.list_files(
                    user_id=user_id,
                    tenant_id=None,  # Can be added if multi-tenant filtering is needed
                    filters=None,  # Can add filters if needed (e.g., file_type, content_type)
                    limit=None,  # No limit for dashboard
                    offset=None  # No pagination for dashboard
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
    
    async def embed_content(
        self,
        file_id: str,
        parsed_file_id: str,
        content_metadata: Dict[str, Any],
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create embeddings for parsed content.
        
        Args:
            file_id: Original file ID
            parsed_file_id: ID of the parsed (parquet) file
            content_metadata: Metadata extracted during parsing
            user_id: User ID
            user_context: User context for permissions and correlation
        
        Returns:
            Embedding result with counts and IDs
        """
        workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
        self.logger.info(f"🧬 Orchestrating embedding creation for file_id={file_id}, parsed_file_id={parsed_file_id} (workflow_id: {workflow_id})")
        
        try:
            # Get EmbeddingService (Content realm service)
            embedding_service = None
            try:
                # Import and initialize directly (Content realm service)
                from backend.content.services.embedding_service.embedding_service import EmbeddingService
                
                embedding_service = EmbeddingService(
                    service_name="EmbeddingService",
                    realm_name="content",  # ✅ Content realm service
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await embedding_service.initialize()
                self.logger.info("✅ EmbeddingService initialized (Content realm)")
                except Exception as init_error:
                    self.logger.error(f"❌ Failed to initialize EmbeddingService directly: {init_error}", exc_info=True)
                    embedding_service = None
            
            if not embedding_service:
                raise ValueError("EmbeddingService not available")
            
            # Call EmbeddingService to create and store embeddings
            embedding_result = await embedding_service.create_representative_embeddings(
                parsed_file_id=parsed_file_id,
                content_metadata=content_metadata,
                user_context=user_context
            )
            
            self.logger.info(f"✅ Embedding creation complete for file_id={file_id}. Stored {embedding_result.get('stored_count', 0)} embeddings.")
            
            # Debug: Log embedding_result structure
            self.logger.info(f"🔍 [embed_content] embedding_result keys: {list(embedding_result.keys()) if isinstance(embedding_result, dict) else 'NOT_A_DICT'}")
            self.logger.info(f"🔍 [embed_content] embedding_result.get('content_id'): {embedding_result.get('content_id')}")
            self.logger.info(f"🔍 [embed_content] content_metadata.get('content_id'): {content_metadata.get('content_id')}")
            
            # Extract content_id from embedding_result (it may have been generated during embedding creation)
            # embedding_result should contain content_id from embedding_creation_module.create_representative_embeddings()
            content_id = embedding_result.get("content_id")
            if not content_id:
                # Fallback: try to get from content_metadata (should be set during parsing)
                content_id = content_metadata.get("content_id") or content_metadata.get("metadata_id")
                if not content_id:
                    self.logger.warning(f"⚠️ content_id not found in embedding_result or content_metadata - this should not happen")
            
            self.logger.info(f"✅ Extracted content_id: {content_id}")
            
            return {
                "success": True,
                "file_id": file_id,
                "parsed_file_id": parsed_file_id,
                "content_id": content_id,  # Use content_id from embedding_result (may have been generated)
                "embeddings_count": embedding_result.get("stored_count", 0),
                "workflow_id": workflow_id,
                "message": "Embeddings created and stored successfully"
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to create embeddings for file_id={file_id}: {e}", exc_info=True)
            await self._realm_service.handle_error_with_audit(e, "embed_content", user_context)
            return {
                "success": False,
                "file_id": file_id,
                "parsed_file_id": parsed_file_id,
                "error": str(e),
                "workflow_id": workflow_id,
                "message": "Failed to create embeddings"
            }
    
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







