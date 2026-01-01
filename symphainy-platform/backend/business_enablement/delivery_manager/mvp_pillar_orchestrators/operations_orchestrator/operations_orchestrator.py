#!/usr/bin/env python3
"""
Operations Orchestrator for MVP Use Case

WHAT: Orchestrates enabling services for MVP operations features
HOW: Delegates to WorkflowManager, VisualizationEngine while preserving UI integration

This orchestrator provides the same API surface as the old OperationsPillar to preserve
UI integration, but internally delegates to first-class enabling services.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.insert(0, os.path.abspath('../../../../../../../'))

from bases.orchestrator_base import OrchestratorBase


class OperationsOrchestrator(OrchestratorBase):
    """Operations Orchestrator for MVP use case."""
    
    def __init__(self, delivery_manager: Any):
        super().__init__(
            service_name="OperationsOrchestratorService",
            realm_name=delivery_manager.realm_name,
            platform_gateway=delivery_manager.platform_gateway,
            di_container=delivery_manager.di_container,
            business_orchestrator=delivery_manager  # Keep for backward compatibility during migration
        )
        self.delivery_manager = delivery_manager
        
        # Enabling services (lazy initialization)
        self._workflow_conversion_service = None
        self._coexistence_analysis_service = None
        self._sop_builder_service = None
        self.librarian = None
        self.conductor = None
        
        # Journey Orchestrator (for artifact creation - Week 7)
        self._journey_orchestrator = None
    
    async def _get_workflow_conversion_service(self):
        """
        Lazy initialization of Workflow Conversion Service using four-tier access pattern.
        
        Tier 1: Enabling Service (via Curator) - use get_enabling_service()
        Tier 2: Direct import and initialization (fallback)
        Tier 3: N/A (no SOA API or Platform Gateway equivalent)
        Tier 4: Return None (calling code handles None gracefully)
        """
        if self._workflow_conversion_service is None:
            try:
                # Tier 1: Try Enabling Service via Curator (four-tier pattern)
                workflow_conversion = await self.get_enabling_service("WorkflowConversionService")
                if workflow_conversion:
                    self._workflow_conversion_service = workflow_conversion
                    self.logger.info("✅ Workflow Conversion Service discovered via Curator")
                    return workflow_conversion
                
                # Tier 2: Fallback - Import and initialize directly
                self.logger.warning("⚠️ Workflow Conversion Service not found via Curator, initializing directly")
                from backend.journey.services.workflow_conversion_service.workflow_conversion_service import WorkflowConversionService
                
                self._workflow_conversion_service = WorkflowConversionService(
                    service_name="WorkflowConversionService",
                    realm_name="journey",
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await self._workflow_conversion_service.initialize()
                self.logger.info("✅ Workflow Conversion Service initialized directly")
                
            except Exception as e:
                self.logger.error(f"❌ Workflow Conversion Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                # Tier 4: Return None - calling code handles None gracefully with structured error
                return None
        
        return self._workflow_conversion_service
    
    async def _get_coexistence_analysis_service(self):
        """
        Lazy initialization of Coexistence Analysis Service using four-tier access pattern.
        
        Tier 1: Enabling Service (via Curator) - use get_enabling_service()
        Tier 2: Direct import and initialization (fallback)
        Tier 3: N/A (no SOA API or Platform Gateway equivalent)
        Tier 4: Return None (calling code handles None gracefully)
        """
        if self._coexistence_analysis_service is None:
            try:
                # Tier 1: Try Enabling Service via Curator (four-tier pattern)
                coexistence_analysis = await self.get_enabling_service("CoexistenceAnalysisService")
                if coexistence_analysis:
                    self._coexistence_analysis_service = coexistence_analysis
                    self.logger.info("✅ Coexistence Analysis Service discovered via Curator")
                    return coexistence_analysis
                
                # Tier 2: Fallback - Import and initialize directly
                self.logger.warning("⚠️ Coexistence Analysis Service not found via Curator, initializing directly")
                from backend.journey.services.coexistence_analysis_service.coexistence_analysis_service import CoexistenceAnalysisService
                
                self._coexistence_analysis_service = CoexistenceAnalysisService(
                    service_name="CoexistenceAnalysisService",
                    realm_name="journey",
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await self._coexistence_analysis_service.initialize()
                self.logger.info("✅ Coexistence Analysis Service initialized directly")
                
            except Exception as e:
                self.logger.error(f"❌ Coexistence Analysis Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                # Tier 4: Return None - calling code handles None gracefully with structured error
                return None
        
        return self._coexistence_analysis_service
    
    async def _get_sop_builder_service(self):
        """
        Lazy initialization of SOP Builder Service using four-tier access pattern.
        
        Tier 1: Enabling Service (via Curator) - use get_enabling_service()
        Tier 2: Direct import and initialization (fallback)
        Tier 3: N/A (no SOA API or Platform Gateway equivalent)
        Tier 4: Return None (calling code handles None gracefully)
        """
        if self._sop_builder_service is None:
            try:
                # Tier 1: Try Enabling Service via Curator (four-tier pattern)
                sop_builder = await self.get_enabling_service("SOPBuilderService")
                if sop_builder:
                    self._sop_builder_service = sop_builder
                    self.logger.info("✅ SOP Builder Service discovered via Curator")
                    return sop_builder
                
                # Tier 2: Fallback - Import and initialize directly
                self.logger.warning("⚠️ SOP Builder Service not found via Curator, initializing directly")
                from backend.journey.services.sop_builder_service.sop_builder_service import SOPBuilderService
                
                self._sop_builder_service = SOPBuilderService(
                    service_name="SOPBuilderService",
                    realm_name="journey",
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await self._sop_builder_service.initialize()
                self.logger.info("✅ SOP Builder Service initialized directly")
                
            except Exception as e:
                self.logger.error(f"❌ SOP Builder Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                # Tier 4: Return None - calling code handles None gracefully with structured error
                return None
        
        return self._sop_builder_service
    
    async def _get_journey_orchestrator(self):
        """
        Lazy initialization of Journey Orchestrator Service for artifact creation.
        
        Uses Curator discovery to find StructuredJourneyOrchestratorService.
        """
        if self._journey_orchestrator is None:
            try:
                # Try Curator discovery
                curator = await self.get_foundation_service("CuratorFoundationService")
                if curator:
                    journey_orchestrator = await curator.discover_service_by_name("StructuredJourneyOrchestratorService")
                    if journey_orchestrator:
                        self._journey_orchestrator = journey_orchestrator
                        self.logger.info("✅ Journey Orchestrator discovered via Curator")
                        return journey_orchestrator
                
                # Fallback: Direct import
                self.logger.warning("⚠️ Journey Orchestrator not found via Curator, initializing directly")
                from backend.journey.services.structured_journey_orchestrator_service.structured_journey_orchestrator_service import StructuredJourneyOrchestratorService
                
                self._journey_orchestrator = StructuredJourneyOrchestratorService(
                    service_name="StructuredJourneyOrchestratorService",
                    realm_name="journey",
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await self._journey_orchestrator.initialize()
                self.logger.info("✅ Journey Orchestrator initialized directly")
                
            except Exception as e:
                self.logger.error(f"❌ Journey Orchestrator initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._journey_orchestrator
    
    async def initialize(self) -> bool:
        """
        Initialize Operations Orchestrator and its agents.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self._realm_service.log_operation_with_telemetry(
            "operations_orchestrator_initialize_start",
            success=True
        )
        
        # Call parent initialize (sets up OrchestratorBase)
        init_result = await super().initialize()
        if not init_result:
            self.logger.warning("⚠️ Base orchestrator initialization failed, continuing anyway...")
        
        try:
            # Get Smart City services (via OrchestratorBase delegation)
            self.librarian = await self.get_librarian_api()
            self.conductor = await self.get_conductor_api()
            
            # Initialize Liaison Agent using OrchestratorBase helper (via Agentic Foundation factory)
            from .agents import OperationsLiaisonAgent
            self.liaison_agent = await self.initialize_agent(
                OperationsLiaisonAgent,
                "OperationsLiaisonAgent",
                agent_type="liaison",
                capabilities=["conversation", "guidance", "operations_support"],
                required_roles=["liaison_agent"]
            )
            
            # Set pillar for this liaison agent (Phase 4.5)
            if self.liaison_agent:
                self.liaison_agent.pillar = "operations"
                self.logger.info("✅ Set pillar='operations' for OperationsLiaisonAgent")
            
            # Initialize Specialist Agent
            from .agents import OperationsSpecialistAgent
            # ⚠️ TEMPORARY: Optional import for SpecialistCapability
            # TODO (Section 1.3): Properly implement business_specialist_agent_protocol when overhauling agents
            try:
                from backend.business_enablement.protocols.business_specialist_agent_protocol import SpecialistCapability
                specialist_capability = SpecialistCapability.PROCESS_OPTIMIZATION
            except ImportError:
                self.logger.warning("⚠️ business_specialist_agent_protocol not available - skipping specialist_capability (will be fixed in Section 1.3)")
                specialist_capability = None
            
            self.specialist_agent = await self.initialize_agent(
                OperationsSpecialistAgent,
                "OperationsSpecialistAgent",
                agent_type="specialist",
                capabilities=["sop_refinement", "workflow_optimization", "blueprint_enhancement"],
                required_roles=[],
                specialist_capability=specialist_capability  # May be None if protocol not available
            )
            
            # Give specialist agent access to orchestrator (for MCP server access)
            if self.specialist_agent and hasattr(self.specialist_agent, 'set_orchestrator'):
                self.specialist_agent.set_orchestrator(self)
            
            # Initialize MCP Server (exposes orchestrator methods as MCP tools)
            from .mcp_server import OperationsMCPServer
            
            self.mcp_server = OperationsMCPServer(
                orchestrator=self,
                di_container=self.di_container
            )
            # MCP server registers tools in __init__, ready to use
            self.logger.info(f"✅ {self.orchestrator_name} MCP Server initialized")
            
            # Register with Curator (Phase 2 pattern with CapabilityDefinition structure)
            await self._realm_service.register_with_curator(
                capabilities=[
                    {
                        "name": "process_optimization",
                        "protocol": "OperationsOrchestratorProtocol",
                        "description": "Optimize business processes",
                        "contracts": {
                            "soa_api": {
                                "api_name": "optimize_process",
                                "endpoint": "/api/v1/operations-pillar/optimize-process",
                                "method": "POST",
                                "handler": self.analyze_coexistence_content,
                                "metadata": {
                                    "description": "Optimize business process",
                                    "parameters": ["session_token", "sop_content", "workflow_content"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "optimize_process_tool",
                                "tool_definition": {
                                    "name": "optimize_process_tool",
                                    "description": "Optimize business process",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "session_token": {"type": "string"},
                                            "sop_content": {"type": "string"},
                                            "workflow_content": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "operations.optimize_process",
                            "semantic_api": "/api/v1/operations-pillar/optimize-process",
                            "user_journey": "optimize_process"
                        }
                    },
                    {
                        "name": "sop_building",
                        "protocol": "OperationsOrchestratorProtocol",
                        "description": "Build SOPs from descriptions",
                        "contracts": {
                            "soa_api": {
                                "api_name": "build_sop",
                                "endpoint": "/api/v1/operations-pillar/build-sop",
                                "method": "POST",
                                "handler": self.start_wizard,
                                "metadata": {
                                    "description": "Build SOP using wizard",
                                    "parameters": []
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "build_sop_tool",
                                "tool_definition": {
                                    "name": "build_sop_tool",
                                    "description": "Build SOP using wizard",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {}
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "operations.build_sop",
                            "semantic_api": "/api/v1/operations-pillar/build-sop",
                            "user_journey": "build_sop"
                        }
                    },
                    {
                        "name": "workflow_visualization",
                        "protocol": "OperationsOrchestratorProtocol",
                        "description": "Visualize workflows",
                        "contracts": {
                            "soa_api": {
                                "api_name": "visualize_workflow",
                                "endpoint": "/api/v1/operations-pillar/visualize-workflow",
                                "method": "POST",
                                "handler": self.generate_workflow_from_sop,
                                "metadata": {
                                    "description": "Visualize workflow from SOP",
                                    "parameters": ["session_token", "sop_file_uuid", "sop_content"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "visualize_workflow_tool",
                                "tool_definition": {
                                    "name": "visualize_workflow_tool",
                                    "description": "Visualize workflow from SOP",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "session_token": {"type": "string"},
                                            "sop_file_uuid": {"type": "string"},
                                            "sop_content": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "operations.visualize_workflow",
                            "semantic_api": "/api/v1/operations-pillar/visualize-workflow",
                            "user_journey": "visualize_workflow"
                        }
                    },
                    {
                        "name": "sop_conversion",
                        "protocol": "OperationsOrchestratorProtocol",
                        "description": "Convert between SOPs and workflows",
                        "contracts": {
                            "soa_api": {
                                "api_name": "convert_sop_to_workflow",
                                "endpoint": "/api/v1/operations-pillar/convert-sop-to-workflow",
                                "method": "POST",
                                "handler": self.generate_workflow_from_sop,
                                "metadata": {
                                    "description": "Convert SOP to workflow",
                                    "parameters": ["session_token", "sop_file_uuid", "sop_content"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "operations.convert_sop_to_workflow",
                            "semantic_api": "/api/v1/operations-pillar/convert-sop-to-workflow",
                            "user_journey": "convert_sop_to_workflow"
                        }
                    }
                ],
                soa_apis=["optimize_process", "build_sop", "visualize_workflow", "convert_sop_to_workflow"],
                mcp_tools=["optimize_process_tool", "build_sop_tool", "visualize_workflow_tool"]
            )
            
            # Record health metric
            await self._realm_service.record_health_metric(
                "operations_orchestrator_initialized",
                1.0,
                {"orchestrator": self.orchestrator_name}
            )
            
            # End telemetry tracking
            await self._realm_service.log_operation_with_telemetry(
                "operations_orchestrator_initialize_complete",
                success=True
            )
            
            self.logger.info(f"✅ {self.orchestrator_name} initialized successfully")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self._realm_service.handle_error_with_audit(e, "operations_orchestrator_initialize")
            
            # End telemetry tracking with failure
            await self._realm_service.log_operation_with_telemetry(
                "operations_orchestrator_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Failed to initialize {self.orchestrator_name}: {e}")
            return False
    
    # ========================================================================
    # Session Management (2 methods)
    # ========================================================================
    
    async def get_session_elements(self, session_token: str) -> Dict[str, Any]:
        """Get session elements (files/data stored in session)."""
        try:
            self.logger.info(f"📂 Getting session elements for: {session_token}")
            
            # Retrieve session data from Librarian
            if self.librarian:
                session_doc = await self.librarian.get_document(document_id=f"session_{session_token}")
                if session_doc:
                    session_data = session_doc.get("data", {})
                    return {
                        "success": True,
                        "session_token": session_token,
                        "elements": session_data.get("elements", []),
                        "element_count": len(session_data.get("elements", []))
                    }
            
            return {
                "success": True,
                "session_token": session_token,
                "elements": [],
                "element_count": 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get session elements: {e}")
            return {"success": False, "error": str(e)}
    
    async def clear_session_elements(self, session_token: str) -> Dict[str, Any]:
        """Clear session elements."""
        try:
            self.logger.info(f"🗑️ Clearing session elements for: {session_token}")
            
            # Clear session data via Content Steward (using RealmServiceBase helper)
            await self.store_document(
                document_data={"elements": [], "cleared_at": datetime.utcnow().isoformat()},
                metadata={"document_type": "session", "session_token": session_token}
            )
            
            return {
                "success": True,
                "session_token": session_token,
                "message": "Session elements cleared"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to clear session elements: {e}")
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # Process Blueprint (3 methods)
    # ========================================================================
    
    async def generate_workflow_from_sop(
        self,
        session_token: str = None,
        sop_file_uuid: str = None,
        sop_content: Dict[str, Any] = None,
        client_id: Optional[str] = None,  # NEW - Week 7: Client-scoped artifacts
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate workflow from SOP file or content.
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_token: Session token for the request
            sop_file_uuid: UUID of uploaded SOP file (optional)
            sop_content: Direct SOP content (optional)
            user_context: User context for security and tenant validation (optional)
        
        Returns:
            Workflow generation result
        """
        # Start telemetry tracking
        await self._realm_service.log_operation_with_telemetry(
            "generate_workflow_from_sop_start",
            success=True,
            details={"session_token": session_token, "sop_file_uuid": sop_file_uuid}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self._realm_service.security.check_permissions(user_context, "generate_workflow_from_sop", "execute"):
                await self._realm_service.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "generate_workflow_from_sop",
                    details={"user_id": user_context.get("user_id"), "session_token": session_token}
                )
                await self._realm_service.record_health_metric("generate_workflow_from_sop_access_denied", 1.0, {"session_token": session_token})
                await self._realm_service.log_operation_with_telemetry("generate_workflow_from_sop_complete", success=False)
                return {"success": False, "error": "Permission denied"}
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self._realm_service.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self._realm_service.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "generate_workflow_from_sop",
                    details={"tenant_id": tenant_id, "session_token": session_token}
                )
                await self._realm_service.record_health_metric("generate_workflow_from_sop_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self._realm_service.log_operation_with_telemetry("generate_workflow_from_sop_complete", success=False)
                return {"success": False, "error": "Tenant access denied"}
        
        try:
            if sop_file_uuid:
                self.logger.info(f"📄➡️📊 Generating workflow from SOP file: {sop_file_uuid}")
                
                # AGENTIC-FORWARD PATTERN: Agent does critical reasoning FIRST
                workflow_structure = None
                sop_content_data = None
                
                # Step 1: Get SOP content for agent analysis
                if self.librarian:
                    file_doc = await self.librarian.get_document(document_id=sop_file_uuid)
                    if file_doc:
                        sop_content_data = file_doc.get("data", {})
                        if isinstance(sop_content_data, str):
                            import json
                            try:
                                sop_content_data = json.loads(sop_content_data)
                            except:
                                sop_content_data = {"content": sop_content_data}
                
                # Step 2: Invoke Specialist Agent for critical reasoning
                if self.specialist_agent and hasattr(self.specialist_agent, 'analyze_process_for_workflow_structure'):
                    try:
                        self.logger.info("🧠 Invoking Specialist Agent for critical reasoning (workflow structure)...")
                        reasoning_result = await self.specialist_agent.analyze_process_for_workflow_structure(
                            process_content=sop_content_data or {"content": "SOP file"},
                            context={"sop_file_uuid": sop_file_uuid, "session_token": session_token},
                            user_id=user_context.get("user_id", "anonymous") if user_context else "anonymous"
                        )
                        if reasoning_result.get("success"):
                            workflow_structure = reasoning_result.get("workflow_structure", {})
                            self.logger.info("✅ Specialist Agent completed critical reasoning for workflow")
                        else:
                            self.logger.warning("⚠️ Specialist Agent reasoning returned unsuccessful, using fallback")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Specialist Agent reasoning failed: {e}, using fallback")
                
                # Step 3: Use WorkflowConversionService to execute agent's strategic decisions
                if not workflow_structure:
                    return {"success": False, "error": "Agent reasoning failed - workflow structure not available"}
                
                workflow_conversion = await self._get_workflow_conversion_service()
                if workflow_conversion:
                    result = await workflow_conversion.convert_sop_to_workflow(
                        workflow_structure=workflow_structure,
                        sop_content=sop_content_data,
                        sop_file_uuid=sop_file_uuid
                    )
                    
                    # NEW - Week 7: Create Journey artifact if client_id provided
                    artifact_id = None
                    if client_id and result.get("success"):
                        try:
                            journey_orchestrator = await self._get_journey_orchestrator()
                            if journey_orchestrator:
                                workflow = result.get("workflow") or result.get("workflow_content") or result
                                artifact_result = await journey_orchestrator.create_journey_artifact(
                                    artifact_type="workflow",
                                    artifact_data={
                                        "workflow_definition": workflow,
                                        "source": "sop_file",
                                        "sop_file_uuid": sop_file_uuid,
                                        "session_token": session_token
                                    },
                                    client_id=client_id,
                                    status="draft",
                                    user_context=user_context
                                )
                                if artifact_result.get("success"):
                                    artifact_id = artifact_result["artifact"]["artifact_id"]
                                    self.logger.info(f"✅ Created workflow artifact: {artifact_id}")
                        except Exception as e:
                            self.logger.warning(f"⚠️ Failed to create workflow artifact: {e}")
                            # Don't fail the workflow generation if artifact creation fails
                    
                    # Add artifact_id to result if created
                    if artifact_id:
                        result["artifact_id"] = artifact_id
                        result["status"] = "draft"
                    
                    return result
                
                return {"success": False, "error": "Workflow Conversion Service not available"}
            
            elif sop_content:
                self.logger.info(f"📄➡️📊 Generating workflow from SOP content")
                
                # AGENTIC-FORWARD PATTERN: Agent does critical reasoning FIRST
                workflow_structure = None
                
                # Step 1: Invoke Specialist Agent for critical reasoning
                if self.specialist_agent and hasattr(self.specialist_agent, 'analyze_process_for_workflow_structure'):
                    try:
                        self.logger.info("🧠 Invoking Specialist Agent for critical reasoning (workflow structure)...")
                        reasoning_result = await self.specialist_agent.analyze_process_for_workflow_structure(
                            process_content=sop_content,
                            context={"session_token": session_token},
                            user_id=user_context.get("user_id", "anonymous") if user_context else "anonymous"
                        )
                        if reasoning_result.get("success"):
                            workflow_structure = reasoning_result.get("workflow_structure", {})
                            self.logger.info("✅ Specialist Agent completed critical reasoning for workflow")
                        else:
                            self.logger.warning("⚠️ Specialist Agent reasoning returned unsuccessful, using fallback")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Specialist Agent reasoning failed: {e}, using fallback")
                
                # Step 2: Use WorkflowConversionService to execute agent's strategic decisions
                if not workflow_structure:
                    return {"success": False, "error": "Agent reasoning failed - workflow structure not available"}
                
                workflow_conversion = await self._get_workflow_conversion_service()
                if workflow_conversion:
                    result = await workflow_conversion.convert_sop_to_workflow(
                        workflow_structure=workflow_structure,
                        sop_content=sop_content
                    )
                    if result.get("success"):
                        workflow = result.get("workflow", {})
                    else:
                        return result
                else:
                    return {"success": False, "error": "Workflow Conversion Service not available"}
                
                # NEW - Week 7: Create Journey artifact
                artifact_id = None
                if client_id:
                    try:
                        journey_orchestrator = await self._get_journey_orchestrator()
                        if journey_orchestrator:
                            artifact_result = await journey_orchestrator.create_journey_artifact(
                                artifact_type="workflow",
                                artifact_data={
                                    "workflow_definition": workflow,
                                    "source": "sop_content",
                                    "session_token": session_token
                                },
                                client_id=client_id,
                                status="draft",
                                user_context=user_context
                            )
                            if artifact_result.get("success"):
                                artifact_id = artifact_result["artifact"]["artifact_id"]
                                self.logger.info(f"✅ Created workflow artifact: {artifact_id}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to create workflow artifact: {e}")
                        # Don't fail the workflow generation if artifact creation fails
                
                # Record health metric (success)
                await self._realm_service.record_health_metric("generate_workflow_from_sop_success", 1.0, {"session_token": session_token})
                
                # End telemetry tracking
                await self._realm_service.log_operation_with_telemetry("generate_workflow_from_sop_complete", success=True, details={"session_token": session_token, "artifact_id": artifact_id})
                
                result = {
                    "success": True,
                    "workflow": workflow,
                    "workflow_content": workflow,
                    "message": "Workflow generated from SOP content"
                }
                
                # Add artifact_id if created
                if artifact_id:
                    result["artifact_id"] = artifact_id
                    result["status"] = "draft"
                
                return result
            
            else:
                await self._realm_service.record_health_metric("generate_workflow_from_sop_failed", 1.0, {"session_token": session_token, "error": "SOP content not found"})
                await self._realm_service.log_operation_with_telemetry("generate_workflow_from_sop_complete", success=False)
                return {
                    "success": False,
                    "error": "SOP content not found",
                    "message": "Either sop_file_uuid or sop_content must be provided"
                }
            
        except Exception as e:
            # Error handling with audit
            await self._realm_service.handle_error_with_audit(e, "generate_workflow_from_sop", details={"session_token": session_token})
            
            # Record health metric (failure)
            await self._realm_service.record_health_metric("generate_workflow_from_sop_failed", 1.0, {"session_token": session_token, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self._realm_service.log_operation_with_telemetry("generate_workflow_from_sop_complete", success=False, details={"session_token": session_token, "error": str(e)})
            
            self.logger.error(f"❌ Failed to generate workflow from SOP: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_sop_from_workflow(
        self,
        session_token: str = None,
        workflow_file_uuid: str = None,
        workflow_content: Dict[str, Any] = None,
        client_id: Optional[str] = None,  # NEW - Week 7: Client-scoped artifacts
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate SOP from workflow file or content.
        
        Args:
            session_token: Session token for the request
            workflow_file_uuid: UUID of uploaded workflow file (optional)
            workflow_content: Direct workflow content (optional)
        
        Returns:
            SOP generation result
        """
        try:
            if workflow_file_uuid:
                self.logger.info(f"📊➡️📄 Generating SOP from workflow file: {workflow_file_uuid}")
                
                # AGENTIC-FORWARD PATTERN: Agent does critical reasoning FIRST
                sop_structure = None
                workflow_content_data = None
                
                # Step 1: Get workflow content for agent analysis
                if self.librarian:
                    file_doc = await self.librarian.get_document(document_id=workflow_file_uuid)
                    if file_doc:
                        workflow_content_data = file_doc.get("data", {})
                        if isinstance(workflow_content_data, str):
                            import json
                            try:
                                workflow_content_data = json.loads(workflow_content_data)
                            except:
                                workflow_content_data = {"content": workflow_content_data}
                
                # Step 2: Invoke Specialist Agent for critical reasoning
                if self.specialist_agent and hasattr(self.specialist_agent, 'analyze_for_sop_structure'):
                    try:
                        self.logger.info("🧠 Invoking Specialist Agent for critical reasoning (SOP structure)...")
                        reasoning_result = await self.specialist_agent.analyze_for_sop_structure(
                            workflow_content=workflow_content_data or {"content": "Workflow file"},
                            context={"workflow_file_uuid": workflow_file_uuid, "session_token": session_token},
                            user_id=user_context.get("user_id", "anonymous") if user_context else "anonymous"
                        )
                        if reasoning_result.get("success"):
                            sop_structure = reasoning_result.get("sop_structure", {})
                            self.logger.info("✅ Specialist Agent completed critical reasoning for SOP")
                        else:
                            self.logger.warning("⚠️ Specialist Agent reasoning returned unsuccessful, using fallback")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Specialist Agent reasoning failed: {e}, using fallback")
                
                # Step 3: Use WorkflowConversionService to execute agent's strategic decisions
                if not sop_structure:
                    return {"success": False, "error": "Agent reasoning failed - SOP structure not available"}
                
                workflow_conversion = await self._get_workflow_conversion_service()
                if workflow_conversion:
                    result = await workflow_conversion.convert_workflow_to_sop(
                        sop_structure=sop_structure,
                        workflow_content=workflow_content_data,
                        workflow_file_uuid=workflow_file_uuid
                    )
                    
                    # NEW - Week 7: Create Journey artifact if client_id provided
                    artifact_id = None
                    if client_id and result.get("success"):
                        try:
                            journey_orchestrator = await self._get_journey_orchestrator()
                            if journey_orchestrator:
                                sop = result.get("sop") or result.get("sop_content") or result
                                artifact_result = await journey_orchestrator.create_journey_artifact(
                                    artifact_type="sop",
                                    artifact_data={
                                        "sop_definition": sop,
                                        "source": "workflow_file",
                                        "workflow_file_uuid": workflow_file_uuid,
                                        "session_token": session_token
                                    },
                                    client_id=client_id,
                                    status="draft",
                                    user_context=user_context
                                )
                                if artifact_result.get("success"):
                                    artifact_id = artifact_result["artifact"]["artifact_id"]
                                    self.logger.info(f"✅ Created SOP artifact: {artifact_id}")
                        except Exception as e:
                            self.logger.warning(f"⚠️ Failed to create SOP artifact: {e}")
                            # Don't fail the SOP generation if artifact creation fails
                    
                    # Add artifact_id to result if created
                    if artifact_id:
                        result["artifact_id"] = artifact_id
                        result["status"] = "draft"
                    
                    return result
                
                return {"success": False, "error": "Workflow Conversion Service not available"}
            
            elif workflow_content:
                self.logger.info(f"📊➡️📄 Generating SOP from workflow content")
                
                # AGENTIC-FORWARD PATTERN: Agent does critical reasoning FIRST
                sop_structure = None
                
                # Step 1: Invoke Specialist Agent for critical reasoning
                if self.specialist_agent and hasattr(self.specialist_agent, 'analyze_for_sop_structure'):
                    try:
                        self.logger.info("🧠 Invoking Specialist Agent for critical reasoning (SOP structure)...")
                        reasoning_result = await self.specialist_agent.analyze_for_sop_structure(
                            workflow_content=workflow_content,
                            context={"session_token": session_token},
                            user_id=user_context.get("user_id", "anonymous") if user_context else "anonymous"
                        )
                        if reasoning_result.get("success"):
                            sop_structure = reasoning_result.get("sop_structure", {})
                            self.logger.info("✅ Specialist Agent completed critical reasoning for SOP")
                        else:
                            self.logger.warning("⚠️ Specialist Agent reasoning returned unsuccessful, using fallback")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Specialist Agent reasoning failed: {e}, using fallback")
                
                # Step 2: Use WorkflowConversionService to execute agent's strategic decisions
                if not sop_structure:
                    return {"success": False, "error": "Agent reasoning failed - SOP structure not available"}
                
                workflow_conversion = await self._get_workflow_conversion_service()
                if workflow_conversion:
                    result = await workflow_conversion.convert_workflow_to_sop(
                        sop_structure=sop_structure,
                        workflow_content=workflow_content
                    )
                    if result.get("success"):
                        sop = result.get("sop", {})
                    else:
                        return result
                else:
                    return {"success": False, "error": "Workflow Conversion Service not available"}
                
                # NEW - Week 7: Create Journey artifact
                artifact_id = None
                if client_id:
                    try:
                        journey_orchestrator = await self._get_journey_orchestrator()
                        if journey_orchestrator:
                            artifact_result = await journey_orchestrator.create_journey_artifact(
                                artifact_type="sop",
                                artifact_data={
                                    "sop_definition": sop,
                                    "source": "workflow_content",
                                    "session_token": session_token
                                },
                                client_id=client_id,
                                status="draft",
                                user_context=user_context
                            )
                            if artifact_result.get("success"):
                                artifact_id = artifact_result["artifact"]["artifact_id"]
                                self.logger.info(f"✅ Created SOP artifact: {artifact_id}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to create SOP artifact: {e}")
                        # Don't fail the SOP generation if artifact creation fails
                
                result = {
                    "success": True,
                    "sop": sop,
                    "sop_content": sop,
                    "message": "SOP generated from workflow content"
                }
                
                # Add artifact_id if created
                if artifact_id:
                    result["artifact_id"] = artifact_id
                    result["status"] = "draft"
                
                return result
            
            else:
                return {
                    "success": False,
                    "error": "Workflow content not found",
                    "message": "Either workflow_file_uuid or workflow_content must be provided"
                }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate SOP from workflow: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_file(self, session_token: str, input_file_uuid: str, output_type: str) -> Dict[str, Any]:
        """Analyze file and convert to desired output type."""
        try:
            self.logger.info(f"🔍 Analyzing file: {input_file_uuid} → {output_type}")
            
            # Access WorkflowConversionService via BusinessOrchestrator
            workflow_conversion = self.business_orchestrator.workflow_conversion_service
            if workflow_conversion:
                result = await workflow_conversion.analyze_file(input_file_uuid, output_type)
                return result
            
            return {"success": False, "error": "Workflow Conversion Service not available"}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to analyze file: {e}")
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # Coexistence Analysis (2 methods)
    # ========================================================================
    
    async def analyze_coexistence_files(self, session_token: str) -> Dict[str, Any]:
        """Get files available for coexistence analysis."""
        try:
            self.logger.info(f"📋 Getting coexistence analysis files for session: {session_token}")
            
            # Get session elements
            session_result = await self.get_session_elements(session_token)
            
            if session_result.get("success"):
                elements = session_result.get("elements", [])
                
                # Filter for SOP and Workflow files
                sop_files = [e for e in elements if e.get("type") == "sop"]
                workflow_files = [e for e in elements if e.get("type") == "workflow"]
                
                return {
                    "success": True,
                    "sop_files": sop_files,
                    "workflow_files": workflow_files,
                    "can_analyze": len(sop_files) > 0 and len(workflow_files) > 0
                }
            
            return {"success": False, "error": "Failed to get session elements"}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get coexistence files: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_coexistence_content(
        self,
        session_token: str,
        sop_content: str,
        workflow_content: Dict[str, Any],
        client_id: Optional[str] = None,  # NEW - Week 7: Client-scoped artifacts
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze coexistence between SOP and Workflow content.
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self._realm_service.log_operation_with_telemetry(
            "analyze_coexistence_content_start",
            success=True,
            details={"session_token": session_token}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self._realm_service.security.check_permissions(user_context, "analyze_coexistence_content", "execute"):
                await self._realm_service.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "analyze_coexistence_content",
                    details={"user_id": user_context.get("user_id"), "session_token": session_token}
                )
                await self._realm_service.record_health_metric("analyze_coexistence_content_access_denied", 1.0, {"session_token": session_token})
                await self._realm_service.log_operation_with_telemetry("analyze_coexistence_content_complete", success=False)
                return {"success": False, "error": "Permission denied"}
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self._realm_service.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self._realm_service.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "analyze_coexistence_content",
                    details={"tenant_id": tenant_id, "session_token": session_token}
                )
                await self._realm_service.record_health_metric("analyze_coexistence_content_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self._realm_service.log_operation_with_telemetry("analyze_coexistence_content_complete", success=False)
                return {"success": False, "error": "Tenant access denied"}
        
        try:
            self.logger.info(f"🔄 Analyzing coexistence for session: {session_token}")
            
            # AGENTIC-FORWARD PATTERN: Agent does critical reasoning FIRST
            coexistence_structure = None
            
            # Step 1: Normalize content for agent analysis
            sop_data = sop_content
            if isinstance(sop_content, str):
                import json
                try:
                    sop_data = json.loads(sop_content)
                except:
                    sop_data = {"content": sop_content}
            
            # Step 2: Invoke Specialist Agent for critical reasoning
            if self.specialist_agent and hasattr(self.specialist_agent, 'analyze_for_coexistence_structure'):
                try:
                    self.logger.info("🧠 Invoking Specialist Agent for critical reasoning (coexistence structure)...")
                    reasoning_result = await self.specialist_agent.analyze_for_coexistence_structure(
                        sop_content=sop_data,
                        workflow_content=workflow_content,
                        context={"session_token": session_token},
                        user_id=user_context.get("user_id", "anonymous") if user_context else "anonymous"
                    )
                    if reasoning_result.get("success"):
                        coexistence_structure = reasoning_result.get("coexistence_structure", {})
                        self.logger.info("✅ Specialist Agent completed critical reasoning for coexistence")
                    else:
                        self.logger.warning("⚠️ Specialist Agent reasoning returned unsuccessful, using fallback")
                except Exception as e:
                    self.logger.warning(f"⚠️ Specialist Agent reasoning failed: {e}, using fallback")
            
            # Step 3: Use CoexistenceAnalysisService to execute agent's strategic decisions
            if not coexistence_structure:
                return {"success": False, "error": "Agent reasoning failed - coexistence structure not available"}
            
            coexistence_analysis = await self._get_coexistence_analysis_service()
            if coexistence_analysis:
                result = await coexistence_analysis.analyze_coexistence(
                    coexistence_structure=coexistence_structure,
                    sop_content=sop_content,
                    workflow_content=workflow_content
                )
                
                # NEW - Week 7: Create Journey artifact for blueprint
                artifact_id = None
                if client_id and result.get("success"):
                    try:
                        journey_orchestrator = await self._get_journey_orchestrator()
                        if journey_orchestrator:
                            blueprint = result.get("blueprint") or result.get("coexistence_blueprint") or result
                            artifact_result = await journey_orchestrator.create_journey_artifact(
                                artifact_type="coexistence_blueprint",
                                artifact_data={
                                    "blueprint_definition": blueprint,
                                    "sop_content": sop_content,
                                    "workflow_content": workflow_content,
                                    "session_token": session_token
                                },
                                client_id=client_id,
                                status="draft",
                                user_context=user_context
                            )
                            if artifact_result.get("success"):
                                artifact_id = artifact_result["artifact"]["artifact_id"]
                                self.logger.info(f"✅ Created coexistence blueprint artifact: {artifact_id}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to create blueprint artifact: {e}")
                        # Don't fail the analysis if artifact creation fails
                
                # Record health metric (success)
                await self._realm_service.record_health_metric("analyze_coexistence_content_success", 1.0, {"session_token": session_token})
                
                # End telemetry tracking
                await self._realm_service.log_operation_with_telemetry("analyze_coexistence_content_complete", success=True, details={"session_token": session_token, "artifact_id": artifact_id})
                
                # Add artifact_id to result if created
                if artifact_id:
                    result["artifact_id"] = artifact_id
                    result["status"] = "draft"
                
                return result
            
            await self._realm_service.record_health_metric("analyze_coexistence_content_failed", 1.0, {"session_token": session_token, "error": "Coexistence Analysis Service not available"})
            await self._realm_service.log_operation_with_telemetry("analyze_coexistence_content_complete", success=False)
            return {"success": False, "error": "Coexistence Analysis Service not available"}
            
        except Exception as e:
            # Error handling with audit
            await self._realm_service.handle_error_with_audit(e, "analyze_coexistence_content", details={"session_token": session_token})
            
            # Record health metric (failure)
            await self._realm_service.record_health_metric("analyze_coexistence_content_failed", 1.0, {"session_token": session_token, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self._realm_service.log_operation_with_telemetry("analyze_coexistence_content_complete", success=False, details={"session_token": session_token, "error": str(e)})
            
            self.logger.error(f"❌ Failed to analyze coexistence: {e}")
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # Wizard Mode (3 methods)
    # ========================================================================
    
    async def start_wizard(self) -> Dict[str, Any]:
        """Start SOP builder wizard."""
        try:
            self.logger.info("🧙 Starting SOP wizard")
            
            # Access SOPBuilderService via BusinessOrchestrator
            sop_builder = await self._get_sop_builder_service()
            if sop_builder:
                result = await sop_builder.start_wizard_session()
                return result
            
            return {"success": False, "error": "SOP Builder Service not available"}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start wizard: {e}")
            return {"success": False, "error": str(e)}
    
    async def wizard_chat(self, session_token: str, user_message: str) -> Dict[str, Any]:
        """Process wizard chat message."""
        try:
            self.logger.info(f"💬 Processing wizard chat for session: {session_token}")
            
            # Access SOPBuilderService via BusinessOrchestrator
            sop_builder = await self._get_sop_builder_service()
            if sop_builder:
                result = await sop_builder.process_wizard_step(session_token, user_message)
                return result
            
            return {"success": False, "error": "SOP Builder Service not available"}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to process wizard chat: {e}")
            return {"success": False, "error": str(e)}
    
    async def wizard_publish(
        self,
        session_token: str,
        client_id: Optional[str] = None,  # NEW - Week 7: Client-scoped artifacts
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Publish wizard results."""
        try:
            self.logger.info(f"📤 Publishing wizard results for session: {session_token}")
            
            # Access SOPBuilderService via BusinessOrchestrator
            sop_builder = await self._get_sop_builder_service()
            if sop_builder:
                result = await sop_builder.complete_wizard(session_token)
                
                # NEW - Week 7: Create Journey artifact if client_id provided
                artifact_id = None
                if client_id and result.get("success"):
                    try:
                        journey_orchestrator = await self._get_journey_orchestrator()
                        if journey_orchestrator:
                            sop = result.get("sop") or result.get("sop_content") or result
                            artifact_result = await journey_orchestrator.create_journey_artifact(
                                artifact_type="sop",
                                artifact_data={
                                    "sop_definition": sop,
                                    "source": "wizard",
                                    "session_token": session_token
                                },
                                client_id=client_id,
                                status="draft",
                                user_context=user_context
                            )
                            if artifact_result.get("success"):
                                artifact_id = artifact_result["artifact"]["artifact_id"]
                                self.logger.info(f"✅ Created SOP artifact from wizard: {artifact_id}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to create SOP artifact: {e}")
                        # Don't fail the wizard publish if artifact creation fails
                
                # Add artifact_id to result if created
                if artifact_id:
                    result["artifact_id"] = artifact_id
                    result["status"] = "draft"
                
                return result
            
            return {"success": False, "error": "SOP Builder Service not available"}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to publish wizard results: {e}")
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # Blueprint Management (1 method)
    # ========================================================================
    
    async def save_blueprint(
        self,
        session_token: str,
        sop_id: str,
        workflow_id: str,
        client_id: Optional[str] = None,  # NEW - Week 7: Client-scoped artifacts
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Save coexistence blueprint."""
        try:
            self.logger.info(f"💾 Saving blueprint for session: {session_token}")
            
            # Access CoexistenceAnalysisService via BusinessOrchestrator
            coexistence_analysis = await self._get_coexistence_analysis_service()
            if coexistence_analysis:
                result = await coexistence_analysis.create_blueprint(sop_id, workflow_id)
                return result
            
            return {"success": False, "error": "Coexistence Analysis Service not available"}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save blueprint: {e}")
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # Liaison Agent (4 methods)
    # ========================================================================
    
    async def process_query(self, session_token: str, query_text: str) -> Dict[str, Any]:
        """Process operations query via liaison agent."""
        try:
            self.logger.info(f"❓ Processing query for session: {session_token}")
            
            # Use liaison agent for conversational queries
            if self.liaison_agent:
                # Liaison agent processes query and returns response
                agent_response = await self.liaison_agent.process_query(query_text, session_token)
                return {
                    "success": True,
                    "response": agent_response.get("response", "I can help you with operations tasks."),
                    "agent": "OperationsLiaisonAgent"
                }
            
            return {
                "success": False,
                "error": "Liaison agent not available"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to process query: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_conversation(self, session_token: str, message: str) -> Dict[str, Any]:
        """Process conversation message via liaison agent."""
        try:
            self.logger.info(f"💬 Processing conversation for session: {session_token}")
            
            # Use liaison agent for conversation
            if self.liaison_agent:
                agent_response = await self.liaison_agent.process_message(message, session_token)
                return {
                    "success": True,
                    "response": agent_response.get("response", "How can I assist you with operations?"),
                    "agent": "OperationsLiaisonAgent"
                }
            
            return {
                "success": False,
                "error": "Liaison agent not available"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to process conversation: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context for session."""
        try:
            self.logger.info(f"📖 Getting conversation context for session: {session_id}")
            
            # Retrieve conversation history from Librarian
            if self.librarian:
                context_doc = await self.librarian.get_document(document_id=f"conversation_{session_id}")
                if context_doc:
                    return {
                        "success": True,
                        "context": context_doc.get("data", {}),
                        "session_id": session_id
                    }
            
            return {
                "success": True,
                "context": {"messages": [], "session_id": session_id},
                "session_id": session_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get conversation context: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_intent(self, session_token: str, user_input: str) -> Dict[str, Any]:
        """Analyze user intent."""
        try:
            self.logger.info(f"🎯 Analyzing intent for session: {session_token}")
            
            # Simple intent analysis (can be enhanced with NLP)
            intent = "general"
            confidence = 0.7
            
            user_input_lower = user_input.lower()
            
            if any(keyword in user_input_lower for keyword in ["create", "build", "make", "sop"]):
                intent = "create_sop"
                confidence = 0.9
            elif any(keyword in user_input_lower for keyword in ["convert", "transform", "workflow"]):
                intent = "convert_workflow"
                confidence = 0.85
            elif any(keyword in user_input_lower for keyword in ["analyze", "compare", "coexistence"]):
                intent = "analyze_coexistence"
                confidence = 0.85
            elif any(keyword in user_input_lower for keyword in ["wizard", "guide", "help me"]):
                intent = "start_wizard"
                confidence = 0.8
            
            return {
                "success": True,
                "intent": intent,
                "confidence": confidence,
                "user_input": user_input
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to analyze intent: {e}")
            return {"success": False, "error": str(e)}
    
    def _format_for_mvp_ui(self, results: Dict[str, Any], resource_id: str, storage_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = {"status": "success", "resource_id": resource_id, "data": results, "timestamp": datetime.utcnow().isoformat(), "orchestrator": self.orchestrator_name}
        if storage_result:
            response["stored_document_id"] = storage_result.get("document_id")
        return response
    
    # ========================================================================
    # Health Check (1 method)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Check orchestrator health."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "orchestrator_type": "mvp_use_case",
            "semantic_api_methods": 16,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_pillar_summary(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        client_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get Operations Pillar summary for Business Outcomes page (NEW semantic API method).
        
        Returns the 3-way summary (textual, tabular, visualizations) of created artifacts
        (workflows, SOPs, coexistence blueprints) for display in Business Outcomes pillar.
        
        Args:
            session_id: Optional session identifier (for filtering)
            user_id: Optional user identifier (for filtering)
            client_id: Optional client identifier (for filtering)
        
        Returns:
            Dict[str, Any]: Pillar summary with 3-way content
                {
                    "success": bool,
                    "pillar": "operations",
                    "summary": {
                        "textual": str,
                        "tabular": {...},
                        "visualizations": [...]
                    },
                    "artifacts": {...},
                    "source_session_id": str,
                    "generated_at": str
                }
        """
        try:
            self.logger.info(f"📊 Getting Operations pillar summary for session: {session_id}")
            
            # Get Librarian API to query artifacts
            librarian = await self.get_librarian_api()
            if not librarian:
                return {
                    "success": False,
                    "error": "Librarian service not available",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Query journey artifacts from Librarian
            filters = {
                "type": "journey_artifact"
            }
            if client_id:
                filters["client_id"] = client_id
            if user_id:
                filters["user_id"] = user_id
            
            try:
                artifacts_result = await librarian.query_documents(
                    collection="journey_artifacts",
                    filters=filters,
                    sort_by="created_at",
                    sort_order="desc"
                )
                artifacts_list = artifacts_result.get("documents", [])
            except Exception as e:
                # If collection doesn't exist or query fails, try searching documents
                self.logger.warning(f"⚠️ Direct query failed, trying search: {e}")
                try:
                    search_results = await self._realm_service.search_documents(
                        query="journey_artifact",
                        filters=filters
                    )
                    artifacts_list = search_results if isinstance(search_results, list) else []
                except Exception as search_error:
                    self.logger.warning(f"⚠️ Search also failed: {search_error}")
                    artifacts_list = []
            
            # Categorize artifacts
            workflows = [a for a in artifacts_list if a.get("artifact_type") == "workflow"]
            sops = [a for a in artifacts_list if a.get("artifact_type") == "sop"]
            blueprints = [a for a in artifacts_list if a.get("artifact_type") == "coexistence_blueprint"]
            
            # Count by status
            draft_count = len([a for a in artifacts_list if a.get("status") == "draft"])
            review_count = len([a for a in artifacts_list if a.get("status") == "review"])
            approved_count = len([a for a in artifacts_list if a.get("status") == "approved"])
            
            # Generate textual summary
            total_artifacts = len(artifacts_list)
            workflow_count = len(workflows)
            sop_count = len(sops)
            blueprint_count = len(blueprints)
            
            # Get coexistence score from blueprints if available
            coexistence_score = None
            if blueprints:
                blueprint_data = blueprints[0].get("data", {})
                coexistence_score = blueprint_data.get("alignment_score") or blueprint_data.get("coexistence_score")
            
            textual = (
                f"Created {total_artifacts} artifact(s): {workflow_count} workflow(s), "
                f"{sop_count} SOP(s), and {blueprint_count} coexistence blueprint(s). "
                f"Status breakdown: {draft_count} draft, {review_count} in review, {approved_count} approved."
            )
            if coexistence_score:
                textual += f" Latest coexistence analysis shows {coexistence_score * 100:.0f}% alignment."
            
            # Generate tabular summary
            tabular_rows = []
            for artifact in artifacts_list[:10]:  # Limit to first 10 for summary
                artifact_data = artifact.get("data", {})
                title = (
                    artifact_data.get("title") or
                    artifact_data.get("workflow_definition", {}).get("title") or
                    artifact_data.get("sop_definition", {}).get("title") or
                    artifact_data.get("blueprint", {}).get("title") or
                    f"{artifact.get('artifact_type', 'unknown').title()} {artifact.get('artifact_id', '')[:8]}"
                )
                tabular_rows.append([
                    title,
                    artifact.get("artifact_type", "unknown").replace("_", " ").title(),
                    artifact.get("status", "unknown").title(),
                    artifact.get("created_at", "N/A")[:10] if artifact.get("created_at") else "N/A"
                ])
            
            tabular = {
                "columns": ["Artifact Name", "Type", "Status", "Created"],
                "rows": tabular_rows,
                "summary_stats": {
                    "total_rows": total_artifacts,
                    "key_metrics": {
                        "total_artifacts": total_artifacts,
                        "workflows": workflow_count,
                        "sops": sop_count,
                        "blueprints": blueprint_count,
                        "draft": draft_count,
                        "in_review": review_count,
                        "approved": approved_count
                    }
                }
            }
            
            # Generate visualizations
            visualizations = [
                {
                    "visualization_id": "operations_artifacts_by_type",
                    "chart_type": "bar",
                    "library": "recharts",
                    "title": "Operations Artifacts by Type",
                    "rationale": "Shows breakdown of workflows, SOPs, and blueprints created",
                    "chart_data": [
                        {"name": "Workflows", "value": workflow_count},
                        {"name": "SOPs", "value": sop_count},
                        {"name": "Blueprints", "value": blueprint_count}
                    ],
                    "colors": ["#8884d8", "#82ca9d", "#ffc658"]
                },
                {
                    "visualization_id": "operations_artifacts_by_status",
                    "chart_type": "pie",
                    "library": "recharts",
                    "title": "Artifacts Status Distribution",
                    "rationale": "Shows status breakdown of all artifacts",
                    "chart_data": [
                        {"name": "Draft", "value": draft_count},
                        {"name": "In Review", "value": review_count},
                        {"name": "Approved", "value": approved_count}
                    ],
                    "colors": ["#ffc658", "#8884d8", "#82ca9d"]
                }
            ]
            
            # Format artifacts for summary
            artifacts_summary = {
                "workflows": [
                    {
                        "artifact_id": a.get("artifact_id"),
                        "title": a.get("data", {}).get("workflow_definition", {}).get("title") or f"Workflow {a.get('artifact_id', '')[:8]}",
                        "status": a.get("status", "draft"),
                        "created_at": a.get("created_at")
                    }
                    for a in workflows[:5]  # Limit to 5 for summary
                ],
                "sops": [
                    {
                        "artifact_id": a.get("artifact_id"),
                        "title": a.get("data", {}).get("sop_definition", {}).get("title") or f"SOP {a.get('artifact_id', '')[:8]}",
                        "status": a.get("status", "draft"),
                        "created_at": a.get("created_at")
                    }
                    for a in sops[:5]  # Limit to 5 for summary
                ],
                "coexistence_blueprints": [
                    {
                        "artifact_id": a.get("artifact_id"),
                        "title": a.get("data", {}).get("blueprint", {}).get("title") or f"Blueprint {a.get('artifact_id', '')[:8]}",
                        "status": a.get("status", "draft"),
                        "alignment_score": a.get("data", {}).get("alignment_score") or a.get("data", {}).get("coexistence_score"),
                        "gaps_identified": a.get("data", {}).get("gaps_identified", 0),
                        "created_at": a.get("created_at")
                    }
                    for a in blueprints[:5]  # Limit to 5 for summary
                ]
            }
            
            self.logger.info(f"✅ Operations pillar summary generated: {total_artifacts} artifacts")
            
            return {
                "success": True,
                "pillar": "operations",
                "summary": {
                    "textual": textual,
                    "tabular": tabular,
                    "visualizations": visualizations
                },
                "artifacts": artifacts_summary,
                "source_session_id": session_id,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get Operations pillar summary: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": "Failed to get Operations pillar summary",
                "error_details": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get orchestrator capabilities."""
        return {
            "service_name": self.service_name,
            "service_type": "mvp_orchestrator",
            "capabilities": [
                "session_management",
                "workflow_conversion",
                "coexistence_analysis",
                "sop_wizard",
                "blueprint_management",
                "liaison_support"
            ],
            "semantic_apis": [
                "get_session_elements",
                "clear_session_elements",
                "generate_workflow_from_sop",
                "generate_sop_from_workflow",
                "analyze_file",
                "analyze_coexistence_files",
                "analyze_coexistence_content",
                "start_wizard",
                "wizard_chat",
                "wizard_publish",
                "save_blueprint",
                "process_query",
                "process_conversation",
                "get_conversation_context",
                "analyze_intent",
                "health_check"
            ],
            "enabling_services": [
                "SOPBuilderService",
                "CoexistenceAnalysisService",
                "WorkflowConversionService"
            ],
            "legacy_pillar": "OperationsPillar"
        }
