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
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../../'))

from bases.orchestrator_base import OrchestratorBase


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
        super().__init__(
            service_name="ContentOrchestratorService",
            realm_name=delivery_manager.realm_name,
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
        session_id: Optional[str] = None  # NEW: Session ID for workflow tracking
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
            # ✅ PROPER: Call Content Steward directly (Content realm service)
            # ========================================================================
            # ContentJourneyOrchestrator is called BY DataSolutionOrchestratorService
            # So we should NOT call DataSolutionOrchestratorService here (that would create a circular dependency)
            # Instead, call Content Steward directly
            # ========================================================================
            
            # Get Content Steward for proper file storage (GCS + Supabase)
            # Access via OrchestratorBase (delegates to RealmServiceBase)
            content_steward = await self.get_content_steward_api()
            
            if not content_steward:
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
                "processing_pillar": processing_pillar,  # ✅ Mark for Operations Pillar if SOP/Workflow
                "uploaded_at": datetime.utcnow().isoformat(),
                "size_bytes": len(file_data)
            }
            
            # ✅ Get user context from request-scoped context (preserves permissions from Universal Pillar Router)
            from utilities.security_authorization.request_context import get_request_user_context
            ctx = get_request_user_context()
            
            # Prepare user_context for Content Steward
            # Merge request-scoped context (with permissions) with upload-specific fields
            user_context = {
                "user_id": user_id,
                "session_id": session_id,
                "workflow_id": workflow_id
            }
            
            # Preserve permissions and other fields from request context
            if ctx:
                user_context.update({
                    "tenant_id": ctx.get("tenant_id"),
                    "permissions": ctx.get("permissions", []),
                    "roles": ctx.get("roles", []),
                    "email": ctx.get("email")
                })
                self.logger.debug(f"✅ [handle_content_upload] Using request context: user_id={ctx.get('user_id')}, tenant_id={ctx.get('tenant_id')}, permissions={ctx.get('permissions')}")
            else:
                self.logger.warning(f"⚠️ [handle_content_upload] No user context available in request context - permissions may be missing")
            
            upload_result = await content_steward.process_upload(file_data, file_type, metadata, user_context)
            
            # Extract file_id from result
            file_uuid = upload_result.get("uuid") or upload_result.get("file_id")
            
            if upload_result.get("success") or upload_result.get("status") == "success" or file_uuid:
                self.logger.info(f"✅ File uploaded via Content Steward (GCS + Supabase): {filename}")
                
                # Ensure we have file_uuid
                if not file_uuid:
                    file_uuid = upload_result.get("uuid") or upload_result.get("file_id")
                
                if not file_uuid:
                    raise Exception("File upload failed: no UUID returned")
                
                # Update workflow status to completed
                # Session tracking handled via Traffic Cop (Smart City service)
                # Workflow tracking handled via Conductor (Smart City service)
                # Workflow tracking is handled by DataSolutionOrchestrator via platform correlation
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
                
                # Return with proper field names
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
                    "message": "File uploaded successfully" + (f" (will be processed in {processing_pillar})" if processing_pillar else "")
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
        session_id: Optional[str] = None
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
        
        Returns:
            Upload result with file metadata
        """
        return await self.handle_content_upload(
            file_data=file_data,
            filename=filename,
            file_type=file_type,
            user_id=user_id,
            session_id=session_id
        )
    
    async def process_file(
        self,
        file_id: str,
        user_id: str,
        copybook_file_id: Optional[str] = None,
        processing_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process file (parsing + metadata extraction) - Frontend Gateway API compatibility.
        
        ✅ ContentJourneyOrchestrator is called BY DataSolutionOrchestratorService.
        So we should NOT call DataSolutionOrchestratorService here (that would create a circular dependency).
        Instead, call FileParserService and other Content realm services directly.
        
        Args:
            file_id: File UUID
            user_id: User identifier
            copybook_file_id: Optional copybook file UUID
            processing_options: Optional processing options
        
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
                return {
                    "success": False,
                    "file_id": file_id,
                    "error": parse_result.get("error", "File parsing failed"),
                    "parse_result": parse_result
                }
            
            # Get file details (includes metadata)
            file_details = await self.get_file_details(file_id, user_id)
            
            # Combine results
            result = {
                "success": True,
                "file_id": file_id,
                "parse_result": parse_result,
                "file_details": file_details.get("file", {}),
                "copybook_file_id": copybook_file_id,
                "message": "Parsing completed successfully via FileParserService"
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ File processing failed: {e}")
            return {
                "success": False,
                "file_id": file_id,
                "error": str(e)
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


