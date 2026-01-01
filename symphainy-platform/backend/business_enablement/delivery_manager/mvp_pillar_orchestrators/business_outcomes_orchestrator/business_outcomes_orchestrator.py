#!/usr/bin/env python3
"""
Business Outcomes Orchestrator for MVP Use Case

WHAT: Orchestrates enabling services for MVP business outcomes features
HOW: Delegates to MetricsCalculator, ReportGenerator, WorkflowManager while preserving UI integration

This orchestrator provides the same API surface as the old BusinessOutcomesPillar to preserve
UI integration, but internally delegates to first-class enabling services.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../../'))

from bases.orchestrator_base import OrchestratorBase


class BusinessOutcomesOrchestrator(OrchestratorBase):
    """
    Business Outcomes Orchestrator for MVP use case.
    
    Extends OrchestratorBase for Smart City access and orchestrator capabilities.
    Preserves MVP UI integration while delegating to enabling services.
    
    OLD: BusinessOutcomesPillar did everything internally
    NEW: Delegates to MetricsCalculatorService, ReportGeneratorService, OperationsAnalysisService
    
    This orchestrator has an MCP Server that exposes use case-level tools for agents.
    """
    
    def __init__(self, delivery_manager: Any):
        """
        Initialize Business Outcomes Orchestrator.
        
        Args:
            delivery_manager: DeliveryManagerService instance (provides service_name, realm_name, platform_gateway, di_container)
        """
        # Extract parameters from delivery_manager (which extends ManagerServiceBase)
        super().__init__(
            service_name="BusinessOutcomesOrchestratorService",
            realm_name=delivery_manager.realm_name,
            platform_gateway=delivery_manager.platform_gateway,
            di_container=delivery_manager.di_container,
            business_orchestrator=delivery_manager  # Keep for backward compatibility during migration
        )
        self.delivery_manager = delivery_manager
        
        # Will be initialized in initialize()
        self.librarian = None
        self.data_steward = None
        
        # Enabling services (lazy initialization)
        self._metrics_calculator_service = None
        self._report_generator_service = None
        self._roadmap_generation_service = None
        self._data_analyzer_service = None
        self._visualization_engine_service = None
        self._poc_generation_service = None
    
    async def _get_metrics_calculator_service(self):
        """
        Lazy initialization of Metrics Calculator Service using four-tier access pattern.
        
        Tier 1: Enabling Service (via Curator) - use get_enabling_service()
        Tier 2: Direct import and initialization (fallback)
        Tier 3: N/A (no SOA API or Platform Gateway equivalent)
        Tier 4: Return None (calling code handles None gracefully)
        """
        if self._metrics_calculator_service is None:
            try:
                # Tier 1: Try Enabling Service via Curator (four-tier pattern)
                metrics_calculator = await self.get_enabling_service("MetricsCalculatorService")
                if metrics_calculator:
                    self._metrics_calculator_service = metrics_calculator
                    self.logger.info("✅ Metrics Calculator Service discovered via Curator")
                    return metrics_calculator
                
                # Tier 2: Fallback - Import and initialize directly
                self.logger.warning("⚠️ Metrics Calculator Service not found via Curator, initializing directly")
                from backend.business_enablement.enabling_services.metrics_calculator_service import MetricsCalculatorService
                
                self._metrics_calculator_service = MetricsCalculatorService(
                    service_name="MetricsCalculatorService",
                    realm_name="business_enablement",
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await self._metrics_calculator_service.initialize()
                self.logger.info("✅ Metrics Calculator Service initialized directly")
                
            except Exception as e:
                self.logger.error(f"❌ Metrics Calculator Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                # Tier 4: Return None - calling code handles None gracefully with structured error
                return None
        
        return self._metrics_calculator_service
    
    async def _get_report_generator_service(self):
        """
        Lazy initialization of Report Generator Service using four-tier access pattern.
        
        Tier 1: Enabling Service (via Curator) - use get_enabling_service()
        Tier 2: Direct import and initialization (fallback)
        Tier 3: N/A (no SOA API or Platform Gateway equivalent)
        Tier 4: Return None (calling code handles None gracefully)
        """
        if self._report_generator_service is None:
            try:
                # Tier 1: Try Enabling Service via Curator (four-tier pattern)
                report_generator = await self.get_enabling_service("ReportGeneratorService")
                if report_generator:
                    self._report_generator_service = report_generator
                    self.logger.info("✅ Report Generator Service discovered via Curator")
                    return report_generator
                
                # Tier 2: Fallback - Import and initialize directly
                self.logger.warning("⚠️ Report Generator Service not found via Curator, initializing directly")
                from backend.business_enablement.enabling_services.report_generator_service import ReportGeneratorService
                
                self._report_generator_service = ReportGeneratorService(
                    service_name="ReportGeneratorService",
                    realm_name="business_enablement",
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await self._report_generator_service.initialize()
                self.logger.info("✅ Report Generator Service initialized directly")
                
            except Exception as e:
                self.logger.error(f"❌ Report Generator Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                # Tier 4: Return None - calling code handles None gracefully with structured error
                return None
        
        return self._report_generator_service
    
    async def _get_roadmap_generation_service(self):
        """
        Lazy initialization of Roadmap Generation Service using four-tier access pattern.
        
        Tier 1: Enabling Service (via Curator) - use get_enabling_service()
        Tier 2: Direct import and initialization (fallback)
        Tier 3: N/A (no SOA API or Platform Gateway equivalent)
        Tier 4: Return None (calling code handles None gracefully)
        """
        if self._roadmap_generation_service is None:
            try:
                # Tier 1: Try Enabling Service via Curator (four-tier pattern)
                roadmap_service = await self.get_enabling_service("RoadmapGenerationService")
                if roadmap_service:
                    self._roadmap_generation_service = roadmap_service
                    self.logger.info("✅ Roadmap Generation Service discovered via Curator")
                    return roadmap_service
                
                # Tier 2: Fallback - Import and initialize directly
                self.logger.warning("⚠️ Roadmap Generation Service not found via Curator, initializing directly")
                from backend.solution.services.roadmap_generation_service.roadmap_generation_service import RoadmapGenerationService
                
                self._roadmap_generation_service = RoadmapGenerationService(
                    service_name="RoadmapGenerationService",
                    realm_name="solution",
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await self._roadmap_generation_service.initialize()
                self.logger.info("✅ Roadmap Generation Service initialized directly")
                
            except Exception as e:
                self.logger.error(f"❌ Roadmap Generation Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                # Tier 4: Return None - calling code handles None gracefully with structured error
                return None
        
        return self._roadmap_generation_service
    
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
    
    async def _get_visualization_engine_service(self):
        """
        Lazy initialization of Visualization Engine Service using four-tier access pattern.
        
        Tier 1: Enabling Service (via Curator) - use get_enabling_service()
        Tier 2: Direct import and initialization (fallback)
        Tier 3: N/A (no SOA API or Platform Gateway equivalent)
        Tier 4: Return None (calling code handles None gracefully)
        """
        if self._visualization_engine_service is None:
            try:
                # Tier 1: Try Enabling Service via Curator (four-tier pattern)
                visualization_engine = await self.get_enabling_service("VisualizationEngineService")
                if visualization_engine:
                    self._visualization_engine_service = visualization_engine
                    self.logger.info("✅ Visualization Engine Service discovered via Curator")
                    return visualization_engine
                
                # Tier 2: Fallback - Import and initialize directly
                self.logger.warning("⚠️ Visualization Engine Service not found via Curator, initializing directly")
                from backend.business_enablement.enabling_services.visualization_engine_service import VisualizationEngineService
                
                self._visualization_engine_service = VisualizationEngineService(
                    service_name="VisualizationEngineService",
                    realm_name="business_enablement",
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await self._visualization_engine_service.initialize()
                self.logger.info("✅ Visualization Engine Service initialized directly")
                
            except Exception as e:
                self.logger.error(f"❌ Visualization Engine Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                # Tier 4: Return None - calling code handles None gracefully with structured error
                return None
        
        return self._visualization_engine_service
    
    async def _get_poc_generation_service(self):
        """
        Lazy initialization of POC Generation Service using four-tier access pattern.
        
        Tier 1: Enabling Service (via Curator) - use get_enabling_service()
        Tier 2: Direct import and initialization (fallback)
        Tier 3: N/A (no SOA API or Platform Gateway equivalent)
        Tier 4: Return None (calling code handles None gracefully)
        """
        if self._poc_generation_service is None:
            try:
                # Tier 1: Try Enabling Service via Curator (four-tier pattern)
                poc_service = await self.get_enabling_service("POCGenerationService")
                if poc_service:
                    self._poc_generation_service = poc_service
                    self.logger.info("✅ POC Generation Service discovered via Curator")
                    return poc_service
                
                # Tier 2: Fallback - Import and initialize directly
                self.logger.warning("⚠️ POC Generation Service not found via Curator, initializing directly")
                from backend.solution.services.poc_generation_service.poc_generation_service import POCGenerationService
                
                self._poc_generation_service = POCGenerationService(
                    service_name="POCGenerationService",
                    realm_name="solution",
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await self._poc_generation_service.initialize()
                self.logger.info("✅ POC Generation Service initialized directly")
                
            except Exception as e:
                self.logger.error(f"❌ POC Generation Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                # Tier 4: Return None - calling code handles None gracefully with structured error
                return None
        
        return self._poc_generation_service
    
    async def initialize(self) -> bool:
        """
        Initialize Business Outcomes Orchestrator and its agents.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self._realm_service.log_operation_with_telemetry(
            "business_outcomes_orchestrator_initialize_start",
            success=True
        )
        
        # Call parent initialize (sets up OrchestratorBase)
        init_result = await super().initialize()
        if not init_result:
            self.logger.warning("⚠️ Base orchestrator initialization failed, continuing anyway...")
        
        try:
            # 1. Get Smart City services (via OrchestratorBase delegation)
            self.librarian = await self.get_librarian_api()
            self.data_steward = await self.get_data_steward_api()
            
            # 2. Initialize Agents using OrchestratorBase helper (via Agentic Foundation factory)
            from .agents import BusinessOutcomesLiaisonAgent, BusinessOutcomesSpecialistAgent
            
            self.liaison_agent = await self.initialize_agent(
                BusinessOutcomesLiaisonAgent,
                "BusinessOutcomesLiaisonAgent",
                agent_type="liaison",
                capabilities=["conversation", "guidance", "business_outcomes_support"],
                required_roles=["liaison_agent"]
            )
            
            # Set pillar for this liaison agent (Phase 4.5)
            if self.liaison_agent:
                self.liaison_agent.pillar = "business_outcomes"
                self.logger.info("✅ Set pillar='business_outcomes' for BusinessOutcomesLiaisonAgent")
            
            self.specialist_agent = await self.initialize_agent(
                BusinessOutcomesSpecialistAgent,
                "BusinessOutcomesSpecialistAgent",
                agent_type="specialist",
                capabilities=["poc_refinement", "strategic_planning", "business_analysis"],
                required_roles=["specialist_agent"]
            )
            
            # Give specialist agent access to orchestrator (for MCP server access)
            if self.specialist_agent and hasattr(self.specialist_agent, 'set_orchestrator'):
                self.specialist_agent.set_orchestrator(self)
            
            # 2.5. Initialize MCP Server (exposes orchestrator methods as MCP tools)
            from .mcp_server import BusinessOutcomesMCPServer
            
            self.mcp_server = BusinessOutcomesMCPServer(
                orchestrator=self,
                di_container=self.di_container
            )
            # MCP server registers tools in __init__, ready to use
            self.logger.info(f"✅ {self.orchestrator_name} MCP Server initialized")
            
            # 3. Register with Curator (Phase 2 pattern with CapabilityDefinition structure)
            await self._realm_service.register_with_curator(
                capabilities=[
                    {
                        "name": "outcome_tracking",
                        "protocol": "BusinessOutcomesOrchestratorProtocol",
                        "description": "Track business outcomes",
                        "contracts": {
                            "soa_api": {
                                "api_name": "track_outcomes",
                                "endpoint": "/api/v1/business-outcomes-pillar/track-outcomes",
                                "method": "POST",
                                "handler": self.track_outcomes,
                                "metadata": {
                                    "description": "Track business outcomes",
                                    "parameters": ["resource_id", "outcome_data", "options"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "track_outcomes_tool",
                                "tool_definition": {
                                    "name": "track_outcomes_tool",
                                    "description": "Track business outcomes",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "resource_id": {"type": "string"},
                                            "outcome_data": {"type": "object"},
                                            "options": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "business_outcomes.track_outcomes",
                            "semantic_api": "/api/v1/business-outcomes-pillar/track-outcomes",
                            "user_journey": "track_outcomes"
                        }
                    },
                    {
                        "name": "roadmap_generation",
                        "protocol": "BusinessOutcomesOrchestratorProtocol",
                        "description": "Generate strategic roadmap",
                        "contracts": {
                            "soa_api": {
                                "api_name": "generate_roadmap",
                                "endpoint": "/api/v1/business-outcomes-pillar/generate-roadmap",
                                "method": "POST",
                                "handler": self.generate_roadmap,
                                "metadata": {
                                    "description": "Generate strategic roadmap",
                                    "parameters": ["resource_id", "options"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "generate_roadmap_tool",
                                "tool_definition": {
                                    "name": "generate_roadmap_tool",
                                    "description": "Generate strategic roadmap",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "resource_id": {"type": "string"},
                                            "options": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "business_outcomes.generate_roadmap",
                            "semantic_api": "/api/v1/business-outcomes-pillar/generate-roadmap",
                            "user_journey": "generate_roadmap"
                        }
                    },
                    {
                        "name": "strategic_planning",
                        "protocol": "BusinessOutcomesOrchestratorProtocol",
                        "description": "Create comprehensive strategic plan",
                        "contracts": {
                            "soa_api": {
                                "api_name": "create_comprehensive_strategic_plan",
                                "endpoint": "/api/v1/business-outcomes-pillar/create-strategic-plan",
                                "method": "POST",
                                "handler": self.create_comprehensive_strategic_plan,
                                "metadata": {
                                    "description": "Create comprehensive strategic plan",
                                    "parameters": ["pillar_summaries", "options"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "create_comprehensive_strategic_plan_tool",
                                "tool_definition": {
                                    "name": "create_comprehensive_strategic_plan_tool",
                                    "description": "Create comprehensive strategic plan",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "pillar_summaries": {"type": "object"},
                                            "options": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "business_outcomes.create_strategic_plan",
                            "semantic_api": "/api/v1/business-outcomes-pillar/create-strategic-plan",
                            "user_journey": "create_strategic_plan"
                        }
                    }
                ],
                soa_apis=["track_outcomes", "generate_roadmap", "calculate_kpis", "analyze_outcomes", "generate_strategic_roadmap", "generate_poc_proposal", "create_comprehensive_strategic_plan", "track_strategic_progress", "analyze_strategic_trends"],
                mcp_tools=["track_outcomes_tool", "generate_roadmap_tool", "calculate_kpis_tool", "analyze_outcomes_tool", "generate_strategic_roadmap_tool", "generate_poc_proposal_tool", "create_comprehensive_strategic_plan_tool", "track_strategic_progress_tool", "analyze_strategic_trends_tool"]
            )
            
            # Record health metric
            await self._realm_service.record_health_metric(
                "business_outcomes_orchestrator_initialized",
                1.0,
                {"orchestrator": self.orchestrator_name}
            )
            
            # End telemetry tracking
            await self._realm_service.log_operation_with_telemetry(
                "business_outcomes_orchestrator_initialize_complete",
                success=True
            )
            
            self.logger.info(f"✅ {self.orchestrator_name} initialized successfully")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self._realm_service.handle_error_with_audit(e, "business_outcomes_orchestrator_initialize")
            
            # End telemetry tracking with failure
            await self._realm_service.log_operation_with_telemetry(
                "business_outcomes_orchestrator_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Failed to initialize {self.orchestrator_name}: {e}")
            return False
    
    # ========================================================================
    # MVP USE CASE APIs (Preserve UI Integration)
    # ========================================================================
    
    async def track_outcomes(
        self,
        resource_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track business outcomes and KPIs (MVP use case orchestration).
        
        OLD: BusinessOutcomesPillar.track_outcomes() - internal micro-modules
        NEW: Delegates to enabling services + Smart City
        """
        try:
            self.logger.info(f"📊 Tracking outcomes: {resource_id}")
            options = options or {}
            results = {}
            
            # Step 1: Calculate KPIs via Metrics Calculator
            metrics_calculator = await self._get_metrics_calculator_service()
            if metrics_calculator:
                kpi_name = options.get("metric_name", "outcome_kpi")
                metric_params = options.get("metric_params", {})
                kpi_formula = metric_params.get("formula") if isinstance(metric_params, dict) else None
                kpi_result = await metrics_calculator.calculate_kpi(
                    kpi_name=kpi_name,
                    data_sources=resource_id,  # resource_id is the data source
                    kpi_formula=kpi_formula
                )
                if kpi_result.get("success"):
                    results["kpi"] = kpi_result
                else:
                    results["kpi"] = {"error": "KPI calculation failed"}
            else:
                results["kpi"] = {"error": "Metrics Calculator service not available"}
            
            # Step 2: Generate report via Report Generator
            report_generator = await self._get_report_generator_service()
            if report_generator and results.get("kpi", {}).get("success"):
                report_result = await report_generator.generate_report(
                    template_id=options.get("template_id", "default_outcome_template"),
                    data_id=resource_id,
                    options=options.get("report_options", {})
                )
                if report_result.get("success"):
                    results["report"] = report_result
                else:
                    results["report"] = {"error": "Report generation failed"}
            else:
                results["report"] = {"error": "Report Generator service not available"}
            
            # Step 3: Track lineage via Data Steward
            await self.track_data_lineage(
                source=resource_id,
                destination=f"{resource_id}_outcomes",
                transformation={
                    "type": "outcome_tracking",
                    "orchestrator": self.orchestrator_name
                }
            )
            
            # Step 4: Store results via Librarian
            storage_result = await self.store_document(
                document_data=results,
                metadata={
                    "resource_id": resource_id,
                    "capability": "track_outcomes",
                    "orchestrator": self.orchestrator_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            self.logger.info(f"✅ Outcome tracking complete: {resource_id}")
            
            # Format response for MVP UI (preserves contract)
            return self._format_for_mvp_ui(results, resource_id, storage_result)
            
        except Exception as e:
            self.logger.error(f"❌ Outcome tracking failed: {e}")
            return {
                "status": "error",
                "message": f"Outcome tracking failed: {str(e)}",
                "error": str(e)
            }
    
    async def generate_roadmap(
        self,
        resource_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate business roadmap (MVP use case orchestration).
        
        OLD: BusinessOutcomesPillar.generate_roadmap() - internal micro-modules
        NEW: Delegates to RoadmapGenerationService
        """
        try:
            self.logger.info(f"🗺️ Generating roadmap: {resource_id}")
            options = options or {}
            
            # Get business context from resource
            business_context = options.get("business_context", {})
            if not business_context:
                # Try to retrieve from resource_id
                resource_doc = await self.retrieve_document(resource_id)
                if resource_doc:
                    business_context = resource_doc.get("data", {})
            
            # Use RoadmapGenerationService
            roadmap_service = await self._get_roadmap_generation_service()
            if roadmap_service:
                roadmap_result = await roadmap_service.generate_roadmap(
                    business_context=business_context,
                    options=options
                )
                
                if roadmap_result.get("success"):
                    # Track lineage
                    await self.track_data_lineage(
                        source=resource_id,
                        destination=roadmap_result.get("roadmap_id", f"{resource_id}_roadmap"),
                        transformation={"type": "roadmap_generation", "orchestrator": self.orchestrator_name}
                    )
                    
                    return self._format_for_mvp_ui(
                        {"roadmap": roadmap_result.get("roadmap", {})},
                        resource_id,
                        {"document_id": roadmap_result.get("roadmap_id")}
                    )
                else:
                    return {
                        "status": "error",
                        "message": roadmap_result.get("message", "Roadmap generation failed"),
                        "error": roadmap_result.get("error")
                    }
            else:
                return {
                    "status": "error",
                    "message": "Roadmap Generation Service not available",
                    "error": "Service unavailable"
                }
            
        except Exception as e:
            self.logger.error(f"❌ Roadmap generation failed: {e}")
            return {
                "status": "error",
                "message": f"Roadmap generation failed: {str(e)}",
                "error": str(e)
            }
    
    async def calculate_kpis(
        self,
        resource_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate key performance indicators (MVP use case orchestration).
        
        OLD: BusinessOutcomesPillar.calculate_kpis() - internal micro-modules
        NEW: Delegates to MetricsCalculator
        """
        try:
            self.logger.info(f"📈 Calculating KPIs: {resource_id}")
            options = options or {}
            
            # Calculate KPIs via Metrics Calculator
            metrics_calculator = await self._get_metrics_calculator_service()
            if metrics_calculator:
                kpi_names = options.get("kpi_names", ["default_kpi"])
                kpi_results = {}
                
                for kpi_name in kpi_names:
                    metric_params = options.get("metric_params", {})
                    kpi_formula = metric_params.get("formula") if isinstance(metric_params, dict) else None
                    kpi_result = await metrics_calculator.calculate_kpi(
                        kpi_name=kpi_name,
                        data_sources=resource_id,  # resource_id is the data source
                        kpi_formula=kpi_formula
                    )
                    if kpi_result.get("success"):
                        kpi_results[kpi_name] = kpi_result
                    else:
                        kpi_results[kpi_name] = {"error": "KPI calculation failed"}
                
                # Track lineage
                await self.track_data_lineage(
                    source=resource_id,
                    destination=f"{resource_id}_kpis",
                    transformation={"type": "kpi_calculation", "orchestrator": self.orchestrator_name}
                )
                
                # Store results
                storage_result = await self.store_document(
                    document_data=kpi_results,
                    metadata={
                        "resource_id": resource_id,
                        "capability": "calculate_kpis",
                        "orchestrator": self.orchestrator_name,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                return self._format_for_mvp_ui({"kpis": kpi_results}, resource_id, storage_result)
            else:
                return {
                    "status": "error",
                    "message": "Metrics Calculator service not available",
                    "error": "Service unavailable"
                }
                
        except Exception as e:
            self.logger.error(f"❌ KPI calculation failed: {e}")
            return {
                "status": "error",
                "message": f"KPI calculation failed: {str(e)}",
                "error": str(e)
            }
    
    async def analyze_outcomes(
        self,
        resource_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze business outcome trends (MVP use case orchestration).
        
        OLD: BusinessOutcomesPillar.analyze_outcomes() - internal micro-modules
        NEW: Delegates to MetricsCalculator + DataAnalyzer
        """
        try:
            self.logger.info(f"🔍 Analyzing outcomes: {resource_id}")
            options = options or {}
            results = {}
            
            # Step 1: Calculate KPIs
            metrics_calculator = await self._get_metrics_calculator_service()
            if metrics_calculator:
                kpi_result = await metrics_calculator.calculate_kpi(
                    kpi_name="outcome_analysis_kpi",
                    data_sources=resource_id,  # resource_id is the data source
                    kpi_formula=None
                )
                results["kpis"] = kpi_result if kpi_result.get("success") else {"error": "KPI calculation failed"}
            else:
                results["kpis"] = {"error": "Metrics Calculator not available"}
            
            # Step 2: Analyze trends via Data Analyzer
            data_analyzer = await self._get_data_analyzer_service()
            if data_analyzer:
                analysis_result = await data_analyzer.analyze_data(
                    data_id=resource_id,
                    analysis_type="trend",
                    analysis_options=options.get("analysis_options", {})
                )
                results["analysis"] = analysis_result if analysis_result.get("success") else {"error": "Analysis failed"}
            else:
                results["analysis"] = {"error": "Data Analyzer not available"}
            
            # Track lineage
            await self.track_data_lineage(
                source=resource_id,
                destination=f"{resource_id}_outcome_analysis",
                transformation={"type": "outcome_analysis", "orchestrator": self.orchestrator_name}
            )
            
            # Store results
            storage_result = await self.store_document(
                document_data=results,
                metadata={
                    "resource_id": resource_id,
                    "capability": "analyze_outcomes",
                    "orchestrator": self.orchestrator_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            return self._format_for_mvp_ui(results, resource_id, storage_result)
            
        except Exception as e:
            self.logger.error(f"❌ Outcome analysis failed: {e}")
            return {
                "status": "error",
                "message": f"Outcome analysis failed: {str(e)}",
                "error": str(e)
            }
    
    # ========================================================================
    # SEMANTIC API METHODS (For Experience Layer)
    # ========================================================================
    
    async def generate_strategic_roadmap(
        self,
        business_context: Dict[str, Any],
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Generate strategic roadmap from pillar outputs with agent-assisted planning (semantic API).
        
        Flow:
        1. Get Roadmap Generation Service
        2. Generate comprehensive strategic plan
        3. Invoke Specialist Agent for strategic insights
        4. Return enhanced roadmap
        
        Args:
            business_context: Context with pillar_outputs and roadmap_options
            user_id: User identifier
        
        Returns:
            Strategic roadmap result
        """
        try:
            self.logger.info(f"🗺️ Generating strategic roadmap for user: {user_id}")
            
            pillar_outputs = business_context.get("pillar_outputs", {})
            roadmap_options = business_context.get("roadmap_options", {})
            
            # Prepare business context from pillar outputs
            enhanced_business_context = {
                "pillar_outputs": pillar_outputs,
                "objectives": self._extract_objectives_from_pillars(pillar_outputs),
                "business_name": business_context.get("business_name", "Business Outcomes Project"),
                "budget": business_context.get("budget", 100000),
                "timeline_days": business_context.get("timeline_days", 180),
                "roadmap_type": roadmap_options.get("roadmap_type", "hybrid")
            }
            
            # AGENTIC-FORWARD PATTERN: Agent does critical reasoning FIRST
            # Step 1: Invoke Specialist Agent for critical reasoning
            roadmap_structure = None
            if self.specialist_agent and hasattr(self.specialist_agent, 'analyze_pillar_outputs_for_roadmap'):
                try:
                    self.logger.info("🧠 Invoking Specialist Agent for critical reasoning (roadmap structure)...")
                    reasoning_result = await self.specialist_agent.analyze_pillar_outputs_for_roadmap(
                        pillar_outputs=pillar_outputs,
                        business_context=enhanced_business_context,
                        user_id=user_id
                    )
                    if reasoning_result.get("success"):
                        roadmap_structure = reasoning_result.get("roadmap_structure", {})
                        self.logger.info("✅ Specialist Agent completed critical reasoning for roadmap")
                    else:
                        self.logger.warning("⚠️ Specialist Agent reasoning returned unsuccessful, using fallback")
                except Exception as e:
                    self.logger.warning(f"⚠️ Specialist Agent reasoning failed: {e}, using fallback")
            
            # Require agent reasoning - fail gracefully if not available
            if not roadmap_structure:
                return {
                    "success": False,
                    "error": "Agent reasoning required",
                    "message": "Specialist Agent must analyze pillar outputs before generating roadmap"
                }
            
            # Step 2: Use RoadmapGenerationService to execute agent's strategic decisions
            roadmap_service = await self._get_roadmap_generation_service()
            if not roadmap_service:
                return {
                    "success": False,
                    "message": "Roadmap Generation Service not available",
                    "error": "Service unavailable"
                }
            
            # Generate roadmap from agent-specified structure
            roadmap_result = await roadmap_service.generate_roadmap(
                roadmap_structure=roadmap_structure,
                business_context=enhanced_business_context
            )
            
            if not roadmap_result.get("success"):
                return {
                    "success": False,
                    "message": roadmap_result.get("message", "Roadmap generation failed"),
                    "error": roadmap_result.get("error")
                }
            
            # Extract roadmap
            enhanced_roadmap = roadmap_result.get("roadmap", {})
            base_roadmap = enhanced_roadmap.copy()
            agent_enhanced = False
            
            # Step 3: Optional refinement (if agent wants to enhance further)
            if self.specialist_agent and hasattr(self.specialist_agent, 'enhance_strategic_roadmap'):
                try:
                    self.logger.info("🤖 Invoking Specialist Agent for optional refinement...")
                    refined_result = await self.specialist_agent.enhance_strategic_roadmap(
                        base_roadmap={"success": True, "roadmap": enhanced_roadmap},
                        context=business_context,
                        user_id=user_id
                    )
                    if refined_result.get("success"):
                        enhanced_roadmap = refined_result.get("roadmap", enhanced_roadmap)
                        agent_enhanced = True
                        self.logger.info("✅ Specialist Agent refined roadmap successfully")
                except Exception as e:
                    self.logger.warning(f"⚠️ Specialist Agent refinement failed: {e}, using base roadmap")
            
            return {
                "success": True,
                "roadmap_id": enhanced_roadmap.get("roadmap_id", roadmap_result.get("roadmap_id")),
                "roadmap": enhanced_roadmap,
                "agent_enhanced": agent_enhanced,
                "message": "Strategic roadmap generated successfully"
            }
                
        except Exception as e:
            self.logger.error(f"❌ Strategic roadmap generation failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"Strategic roadmap generation failed: {str(e)}",
                "error": str(e)
            }
    
    async def generate_poc_proposal(
        self,
        business_context: Dict[str, Any],
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Generate POC proposal from pillar outputs with agent-assisted refinement (semantic API).
        
        Flow:
        1. Get POC Generation Service
        2. Generate comprehensive POC proposal (roadmap + financials + metrics)
        3. Invoke Specialist Agent for autonomous refinement
        4. Return final proposal
        
        Args:
            business_context: Context with pillar_outputs and proposal_options
            user_id: User identifier
        
        Returns:
            POC proposal result
        """
        try:
            self.logger.info(f"📋 Generating POC proposal for user: {user_id}")
            
            pillar_outputs = business_context.get("pillar_outputs", {})
            proposal_options = business_context.get("proposal_options", {})
            poc_type = proposal_options.get("poc_type", "hybrid")
            
            # AGENTIC-FORWARD PATTERN: Agent does critical reasoning FIRST
            # Step 1: Invoke Specialist Agent for critical reasoning
            poc_structure = None
            if self.specialist_agent and hasattr(self.specialist_agent, 'analyze_pillar_outputs_for_poc'):
                try:
                    self.logger.info("🧠 Invoking Specialist Agent for critical reasoning (POC structure)...")
                    reasoning_result = await self.specialist_agent.analyze_pillar_outputs_for_poc(
                        pillar_outputs=pillar_outputs,
                        business_context=business_context,
                        poc_type=poc_type,
                        user_id=user_id
                    )
                    if reasoning_result.get("success"):
                        poc_structure = reasoning_result.get("poc_structure", {})
                        self.logger.info("✅ Specialist Agent completed critical reasoning for POC")
                    else:
                        self.logger.warning("⚠️ Specialist Agent reasoning returned unsuccessful, using fallback")
                except Exception as e:
                    self.logger.warning(f"⚠️ Specialist Agent reasoning failed: {e}, using fallback")
            
            # Require agent reasoning - fail gracefully if not available
            if not poc_structure:
                return {
                    "success": False,
                    "error": "Agent reasoning required",
                    "message": "Specialist Agent must analyze pillar outputs before generating POC proposal"
                }
            
            # Step 2: Use POC Generation Service to execute agent's strategic decisions
            poc_service = await self._get_poc_generation_service()
            if not poc_service:
                return {
                    "success": False,
                    "message": "POC Generation Service not available",
                    "error": "Service unavailable"
                }
            
            base_proposal = await poc_service.generate_poc_proposal(
                poc_structure=poc_structure,
                poc_type=poc_type,
                options=proposal_options
            )
            
            if not base_proposal.get("success"):
                return base_proposal
            
            # Step 3: Optional refinement (if agent wants to enhance further)
            refined_proposal = base_proposal
            if self.specialist_agent and hasattr(self.specialist_agent, 'refine_poc_proposal'):
                try:
                    self.logger.info("🤖 Invoking Specialist Agent for optional refinement...")
                    refined_result = await self.specialist_agent.refine_poc_proposal(
                        base_proposal=base_proposal,
                        context=business_context,
                        user_id=user_id
                    )
                    if refined_result.get("success"):
                        refined_proposal = refined_result
                        self.logger.info("✅ Specialist Agent refined POC proposal successfully")
                    else:
                        self.logger.warning("⚠️ Specialist Agent refinement returned unsuccessful, using base proposal")
                except Exception as e:
                    self.logger.warning(f"⚠️ Specialist Agent refinement failed: {e}, using base proposal")
            
            # Step 3: Return refined proposal
            return {
                "success": True,
                "proposal_id": refined_proposal.get("poc_proposal", {}).get("proposal_id"),
                "proposal": refined_proposal.get("poc_proposal", {}),
                "agent_refined": refined_proposal != base_proposal,
                "message": "POC proposal generated successfully"
            }
                
        except Exception as e:
            self.logger.error(f"❌ POC proposal generation failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"POC proposal generation failed: {str(e)}",
                "error": str(e)
            }
    
    async def get_pillar_summaries(
        self,
        session_id: str,
        user_id: str = "anonymous",
        client_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get summaries from all pillars by calling their orchestrators directly (semantic API).
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            client_id: Optional client identifier (for filtering)
        
        Returns:
            Pillar summaries from all three pillars
        """
        try:
            self.logger.info(f"📊 Getting pillar summaries for session: {session_id}, user: {user_id}")
            
            summaries = {
                "content_pillar": {},
                "insights_pillar": {},
                "operations_pillar": {}
            }
            
            # Get Content Pillar summary
            try:
                content_orchestrator = self.delivery_manager.mvp_pillar_orchestrators.get("content")
                if content_orchestrator:
                    content_summary = await content_orchestrator.get_pillar_summary(
                        session_id=session_id,
                        user_id=user_id
                    )
                    if content_summary.get("success"):
                        summaries["content_pillar"] = content_summary
                        self.logger.info("✅ Content pillar summary retrieved")
                    else:
                        self.logger.warning(f"⚠️ Content pillar summary failed: {content_summary.get('error')}")
                else:
                    self.logger.warning("⚠️ ContentOrchestrator not available")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get Content pillar summary: {e}")
            
            # Get Insights Pillar summary
            try:
                insights_orchestrator = self.delivery_manager.mvp_pillar_orchestrators.get("insights")
                if insights_orchestrator:
                    insights_summary = await insights_orchestrator.get_pillar_summary()
                    if insights_summary.get("success"):
                        summaries["insights_pillar"] = insights_summary
                        self.logger.info("✅ Insights pillar summary retrieved")
                    else:
                        self.logger.warning(f"⚠️ Insights pillar summary failed: {insights_summary.get('error')}")
                else:
                    self.logger.warning("⚠️ InsightsOrchestrator not available")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get Insights pillar summary: {e}")
            
            # Get Operations Pillar summary
            try:
                operations_orchestrator = self.delivery_manager.mvp_pillar_orchestrators.get("operations")
                if operations_orchestrator:
                    operations_summary = await operations_orchestrator.get_pillar_summary(
                        session_id=session_id,
                        user_id=user_id,
                        client_id=client_id
                    )
                    if operations_summary.get("success"):
                        summaries["operations_pillar"] = operations_summary
                        self.logger.info("✅ Operations pillar summary retrieved")
                    else:
                        self.logger.warning(f"⚠️ Operations pillar summary failed: {operations_summary.get('error')}")
                else:
                    self.logger.warning("⚠️ OperationsOrchestrator not available")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get Operations pillar summary: {e}")
            
            # Check if we got at least one summary
            has_summaries = any(
                summaries.get("content_pillar", {}).get("success"),
                summaries.get("insights_pillar", {}).get("success"),
                summaries.get("operations_pillar", {}).get("success")
            )
            
            return {
                "success": has_summaries,
                "summaries": summaries,
                "message": "Pillar summaries retrieved successfully" if has_summaries else "Some pillar summaries unavailable",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Get pillar summaries failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"Failed to get pillar summaries: {str(e)}",
                "error": str(e),
                "summaries": {
                    "content_pillar": {},
                    "insights_pillar": {},
                    "operations_pillar": {}
                },
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_journey_visualization(
        self,
        session_id: str,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Get journey visualization (semantic API).
        
        Args:
            session_id: Session identifier
            user_id: User identifier
        
        Returns:
            Journey visualization data
        """
        try:
            self.logger.info(f"📊 Getting journey visualization for session: {session_id}")
            
            # Get pillar summaries
            summaries_result = await self.get_pillar_summaries(session_id, user_id)
            summaries = summaries_result.get("summaries", {})
            
            # Use VisualizationEngineService if available
            visualization_service = await self._get_visualization_engine_service()
            if visualization_service:
                visualization_result = await visualization_service.create_visualization(
                    data_id=session_id,
                    visualization_type="journey",
                    options={"summaries": summaries}
                )
                
                if visualization_result.get("success"):
                    return {
                        "success": True,
                        "visualization": visualization_result.get("visualization", {}),
                        "message": "Journey visualization generated successfully"
                    }
            
            # Fallback: return basic visualization structure
            return {
                "success": True,
                "visualization": {
                    "dashboard": {
                        "content_pillar": summaries.get("content_pillar", {}),
                        "insights_pillar": summaries.get("insights_pillar", {}),
                        "operations_pillar": summaries.get("operations_pillar", {})
                    },
                    "charts": [],
                    "summary_display": summaries
                },
                "message": "Journey visualization retrieved successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Get journey visualization failed: {e}")
            return {
                "success": False,
                "message": f"Failed to get journey visualization: {str(e)}",
                "error": str(e)
            }
    
    async def create_comprehensive_strategic_plan(
        self,
        business_context: Dict[str, Any],
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Create comprehensive strategic plan (semantic API).
        
        Args:
            business_context: Business context with objectives, business_name, budget, timeline
            user_id: User identifier
        
        Returns:
            Comprehensive strategic plan
        """
        try:
            self.logger.info(f"🎯 Creating comprehensive strategic plan for user: {user_id}")
            
            roadmap_service = await self._get_roadmap_generation_service()
            if not roadmap_service:
                return {
                    "success": False,
                    "message": "Roadmap Generation Service not available",
                    "error": "Service unavailable"
                }
            
            strategic_plan = await roadmap_service.create_comprehensive_strategic_plan(
                business_context=business_context
            )
            
            return strategic_plan
            
        except Exception as e:
            self.logger.error(f"❌ Create comprehensive strategic plan failed: {e}")
            return {
                "success": False,
                "message": f"Strategic plan creation failed: {str(e)}",
                "error": str(e)
            }
    
    async def track_strategic_progress(
        self,
        goals: List[Dict[str, Any]],
        performance_data: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Track strategic progress (semantic API).
        
        Args:
            goals: List of strategic goals to track
            performance_data: Optional performance data
            user_id: User identifier
        
        Returns:
            Strategic progress tracking results
        """
        try:
            self.logger.info(f"📊 Tracking strategic progress for user: {user_id}")
            
            roadmap_service = await self._get_roadmap_generation_service()
            if not roadmap_service:
                return {
                    "success": False,
                    "message": "Roadmap Generation Service not available",
                    "error": "Service unavailable"
                }
            
            progress_result = await roadmap_service.track_strategic_progress(
                goals=goals,
                performance_data=performance_data
            )
            
            return progress_result
            
        except Exception as e:
            self.logger.error(f"❌ Track strategic progress failed: {e}")
            return {
                "success": False,
                "message": f"Strategic progress tracking failed: {str(e)}",
                "error": str(e)
            }
    
    async def analyze_strategic_trends(
        self,
        market_data: Dict[str, Any],
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Analyze strategic trends (semantic API).
        
        Args:
            market_data: Market and industry data for trend analysis
            user_id: User identifier
        
        Returns:
            Strategic trend analysis results
        """
        try:
            self.logger.info(f"📈 Analyzing strategic trends for user: {user_id}")
            
            roadmap_service = await self._get_roadmap_generation_service()
            if not roadmap_service:
                return {
                    "success": False,
                    "message": "Roadmap Generation Service not available",
                    "error": "Service unavailable"
                }
            
            trend_result = await roadmap_service.analyze_strategic_trends(
                market_data=market_data
            )
            
            return trend_result
            
        except Exception as e:
            self.logger.error(f"❌ Analyze strategic trends failed: {e}")
            return {
                "success": False,
                "message": f"Strategic trend analysis failed: {str(e)}",
                "error": str(e)
            }
    
    # ========================================================================
    # EXECUTE METHOD (Route to MVP APIs)
    # ========================================================================
    
    async def execute(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute orchestration request (routes to MVP use case APIs).
        
        Args:
            request: {
                "action": "track_outcomes" | "generate_roadmap" | "calculate_kpis" | "analyze_outcomes" | "generate_strategic_roadmap" | "generate_poc_proposal",
                "params": {
                    "resource_id": str,
                    "options": Dict[str, Any]
                }
            }
        
        Returns:
            Orchestration result
        """
        action = request.get("action")
        params = request.get("params", {})
        resource_id = params.get("resource_id", "")
        options = params.get("options", {})
        
        if action == "track_outcomes":
            return await self.track_outcomes(resource_id, options)
        elif action == "generate_roadmap":
            return await self.generate_roadmap(resource_id, options)
        elif action == "calculate_kpis":
            return await self.calculate_kpis(resource_id, options)
        elif action == "analyze_outcomes":
            return await self.analyze_outcomes(resource_id, options)
        elif action == "generate_strategic_roadmap":
            return await self.generate_strategic_roadmap(params.get("business_context", {}), params.get("user_id", "anonymous"))
        elif action == "generate_poc_proposal":
            return await self.generate_poc_proposal(params.get("business_context", {}), params.get("user_id", "anonymous"))
        elif action == "create_comprehensive_strategic_plan":
            return await self.create_comprehensive_strategic_plan(params.get("business_context", {}), params.get("user_id", "anonymous"))
        elif action == "track_strategic_progress":
            return await self.track_strategic_progress(params.get("goals", []), params.get("performance_data"), params.get("user_id", "anonymous"))
        elif action == "analyze_strategic_trends":
            return await self.analyze_strategic_trends(params.get("market_data", {}), params.get("user_id", "anonymous"))
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}",
                "available_actions": [
                    "track_outcomes",
                    "generate_roadmap",
                    "calculate_kpis",
                    "analyze_outcomes",
                    "generate_strategic_roadmap",
                    "generate_poc_proposal",
                    "create_comprehensive_strategic_plan",
                    "track_strategic_progress",
                    "analyze_strategic_trends"
                ]
            }
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _format_for_mvp_ui(
        self,
        data: Dict[str, Any],
        resource_id: str,
        storage_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format response for MVP UI (preserves contract).
        
        Args:
            data: Orchestration results
            resource_id: Resource ID
            storage_result: Optional storage result from Librarian
        
        Returns:
            Formatted response for MVP UI
        """
        return {
            "status": "success",
            "data": data,
            "resource_id": resource_id,
            "document_id": storage_result.get("document_id") if storage_result else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _extract_objectives_from_pillars(self, pillar_outputs: Dict[str, Any]) -> List[str]:
        """Extract objectives from pillar outputs."""
        objectives = []
        
        # Extract from insights
        insights = pillar_outputs.get("insights_pillar", {})
        if insights.get("recommendations"):
            objectives.extend([f"Address: {rec}" for rec in insights.get("recommendations", [])[:3]])
        
        # Extract from operations
        operations = pillar_outputs.get("operations_pillar", {})
        if operations.get("coexistence_blueprint"):
            objectives.append("Implement coexistence blueprint")
        
        # Extract from content
        content = pillar_outputs.get("content_pillar", {})
        if content.get("files"):
            objectives.append("Leverage uploaded content for analysis")
        
        return objectives if objectives else ["Improve business outcomes"]
    
    async def _compose_poc_data(
        self,
        pillar_outputs: Dict[str, Any],
        proposal_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compose POC data from pillar outputs."""
        poc_type = proposal_options.get("poc_type", "hybrid")
        
        # Extract data from pillars
        content_data = pillar_outputs.get("content_pillar", {})
        insights_data = pillar_outputs.get("insights_pillar", {})
        operations_data = pillar_outputs.get("operations_pillar", {})
        
        # Compose POC proposal structure
        poc_data = {
            "poc_type": poc_type,
            "executive_summary": {
                "poc_overview": f"Comprehensive {poc_type} POC proposal",
                "key_benefits": [],
                "business_impact": "medium",
                "risk_assessment": "medium",
                "success_criteria": []
            },
            "objectives": self._extract_objectives_from_pillars(pillar_outputs),
            "scope": {
                "in_scope": [],
                "out_of_scope": []
            },
            "timeline": {
                "duration_weeks": 12,
                "phases": []
            },
            "financial_analysis": {},
            "business_metrics": {},
            "roadmap": {},
            "recommendations": insights_data.get("recommendations", []),
            "next_steps": []
        }
        
        # Add insights data
        if insights_data:
            poc_data["business_metrics"] = {
                "kpis": insights_data.get("kpis", {}),
                "insights": insights_data.get("insights", [])
            }
        
        # Add operations data
        if operations_data:
            poc_data["roadmap"] = {
                "phases": operations_data.get("phases", []),
                "milestones": operations_data.get("milestones", [])
            }
        
        return poc_data

