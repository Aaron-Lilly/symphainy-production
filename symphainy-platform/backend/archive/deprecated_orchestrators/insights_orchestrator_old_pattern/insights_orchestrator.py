#!/usr/bin/env python3
"""
Insights Orchestrator for MVP Use Case

WHAT: Orchestrates enabling services for MVP insights features
HOW: Delegates to DataAnalyzer, MetricsCalculator, VisualizationEngine while preserving UI integration

This orchestrator provides the same API surface as the old InsightsPillar to preserve
UI integration, but internally delegates to first-class enabling services.
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.orchestrator_base import OrchestratorBase

# ⚠️ TEMPORARY: Optional import for SpecialistCapability
# TODO (Section 1.3): Properly implement business_specialist_agent_protocol when overhauling agents
# This import is optional to allow orchestrator initialization without the protocol module
try:
    from backend.business_enablement.protocols.business_specialist_agent_protocol import SpecialistCapability
    SPECIALIST_CAPABILITY_AVAILABLE = True
except ImportError:
    SPECIALIST_CAPABILITY_AVAILABLE = False
    # Create a dummy enum for compatibility
    from enum import Enum
    class SpecialistCapability(Enum):
        DATA_ANALYSIS = "data_analysis"
        CONTENT_PROCESSING = "content_processing"
        OPERATIONS_MANAGEMENT = "operations_management"
        BUSINESS_OUTCOMES = "business_outcomes"


class InsightsOrchestrator(OrchestratorBase):
    """
    Insights Orchestrator for MVP use case.
    
    ⚠️ DEPRECATED: This orchestrator uses the old Manager + Orchestrator pattern.
    New insights operations should use InsightsSolutionOrchestratorService → InsightsJourneyOrchestrator pattern.
    
    This orchestrator is kept for backward compatibility but will be phased out.
    New development should use:
    - InsightsSolutionOrchestratorService (Solution Realm) for platform correlation
    - InsightsJourneyOrchestrator (Journey Realm) for workflow orchestration
    
    Extends OrchestratorBase for Smart City access and orchestrator capabilities.
    Preserves MVP UI integration while delegating to enabling services.
    
    OLD: InsightsPillar did everything internally
    NEW: Delegates to DataAnalyzerService, MetricsCalculatorService, VisualizationEngineService
    
    This orchestrator has an MCP Server that exposes use case-level tools for agents.
    """
    
    def __init__(self, insights_manager: Any):
        """
        Initialize Insights Orchestrator.
        
        Args:
            insights_manager: InsightsManagerService instance (provides service_name, realm_name, platform_gateway, di_container)
        """
        # Extract parameters from insights_manager (which extends ManagerServiceBase)
        super().__init__(
            service_name="InsightsOrchestratorService",
            realm_name="insights",
            platform_gateway=insights_manager.platform_gateway,
            di_container=insights_manager.di_container,
            delivery_manager=insights_manager  # For backward compatibility
        )
        self.insights_manager = insights_manager
        self.delivery_manager = insights_manager  # Keep for backward compatibility
        self.orchestrator_name = "InsightsOrchestrator"
        
        # Will be initialized in initialize()
        self.librarian = None
        self.data_steward = None
        self.content_steward = None
        
        # Data Solution Orchestrator (Phase 6 - same pattern as Content Pillar)
        self._data_solution_orchestrator = None
        
        # Enabling services (lazy initialization)
        self._data_analyzer_service = None
        self._metrics_calculator_service = None
        self._visualization_engine_service = None
        self._apg_processor_service = None
        self._insights_generator_service = None
        self._semantic_enrichment_gateway = None
    
    async def _get_data_solution_orchestrator(self):
        """
        Get Data Solution Orchestrator Service via Curator discovery.
        
        Phase 6: Same pattern as Content Pillar.
        This is the ONLY way to access data operations in the platform.
        Hard fails if Data Solution Orchestrator is not available.
        
        Returns:
            DataSolutionOrchestratorService instance
        
        Raises:
            ValueError: If Data Solution Orchestrator Service is not available
        """
        if self._data_solution_orchestrator is None:
            try:
                # Discover via Curator (Solution realm service)
                curator = await self.get_foundation_service("CuratorFoundationService")
                if not curator:
                    raise ValueError("Curator not available - cannot discover Data Solution Orchestrator Service")
                
                data_solution_service = await curator.get_service("DataSolutionOrchestratorService")
                if not data_solution_service:
                    raise ValueError("Data Solution Orchestrator Service not available - must be registered in Solution realm")
                
                self._data_solution_orchestrator = data_solution_service
                self.logger.info("✅ Data Solution Orchestrator discovered via Curator")
                return data_solution_service
            except Exception as e:
                self.logger.error(f"❌ Failed to get Data Solution Orchestrator Service: {e}")
                raise ValueError(f"Data Solution Orchestrator Service not available: {e}")
        
        return self._data_solution_orchestrator
    
    async def _get_data_analyzer_service(self):
        """
        Lazy initialization of Data Analyzer Service using four-tier access pattern.
        
        Data Analyzer Service is now an Insights realm service (not an enabling service).
        """
        if self._data_analyzer_service is None:
            try:
                # Import and initialize directly (Insights realm service)
                from backend.insights.services.data_analyzer_service.data_analyzer_service import DataAnalyzerService
                
                self._data_analyzer_service = DataAnalyzerService(
                    service_name="DataAnalyzerService",
                    realm_name="insights",  # ✅ Insights realm service
                    platform_gateway=self.insights_manager.platform_gateway,
                    di_container=self.insights_manager.di_container
                )
                await self._data_analyzer_service.initialize()
                self.logger.info("✅ Data Analyzer Service initialized (Insights realm)")
                
            except Exception as e:
                self.logger.error(f"❌ Data Analyzer Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                # Tier 4: Return None - calling code handles None gracefully with structured error
                return None
        
        return self._data_analyzer_service
    
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
                    realm_name="business_enablement",  # Enabling services stay in business_enablement
                    platform_gateway=self.insights_manager.platform_gateway,
                    di_container=self.insights_manager.di_container
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
    
    async def _get_visualization_engine_service(self):
        """
        Lazy initialization of Visualization Engine Service using four-tier access pattern.
        
        Visualization Engine Service is now an Insights realm service (not an enabling service).
        """
        if self._visualization_engine_service is None:
            try:
                # Import and initialize directly (Insights realm service)
                from backend.insights.services.visualization_engine_service.visualization_engine_service import VisualizationEngineService
                
                self._visualization_engine_service = VisualizationEngineService(
                    service_name="VisualizationEngineService",
                    realm_name="insights",  # ✅ Insights realm service
                    platform_gateway=self.insights_manager.platform_gateway,
                    di_container=self.insights_manager.di_container
                )
                await self._visualization_engine_service.initialize()
                self.logger.info("✅ Visualization Engine Service initialized (Insights realm)")
                
            except Exception as e:
                self.logger.error(f"❌ Visualization Engine Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                # Tier 4: Return None - calling code handles None gracefully with structured error
                return None
        
        return self._visualization_engine_service
    
    async def _get_apg_processor_service(self):
        """
        Lazy initialization of APG Processor Service using four-tier access pattern.
        
        Tier 1: Enabling Service (via Curator) - use get_enabling_service()
        Tier 2: Direct import and initialization (fallback)
        Tier 3: N/A (no SOA API or Platform Gateway equivalent)
        Tier 4: Return None (calling code handles None gracefully)
        """
        if self._apg_processor_service is None:
            try:
                # Tier 1: Try Enabling Service via Curator (four-tier pattern)
                apg_processor = await self.get_enabling_service("APGProcessingService")
                if apg_processor:
                    self._apg_processor_service = apg_processor
                    self.logger.info("✅ APG Processor Service discovered via Curator")
                    return apg_processor
                
                # Tier 2: Fallback - Import and initialize directly
                self.logger.warning("⚠️ APG Processor Service not found via Curator, initializing directly")
                from backend.business_enablement.enabling_services.apg_processor_service.apg_processor_service import APGProcessingService
                
                self._apg_processor_service = APGProcessingService(
                    service_name="APGProcessingService",
                    realm_name="business_enablement",  # Enabling services stay in business_enablement
                    platform_gateway=self.insights_manager.platform_gateway,
                    di_container=self.insights_manager.di_container
                )
                await self._apg_processor_service.initialize()
                self.logger.info("✅ APG Processor Service initialized directly")
                
            except Exception as e:
                self.logger.error(f"❌ APG Processor Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                # Tier 4: Return None - calling code handles None gracefully with structured error
                return None
        
        return self._apg_processor_service
    
    async def _get_insights_generator_service(self):
        """
        Lazy initialization of Insights Generator Service using four-tier access pattern.
        
        Tier 1: Enabling Service (via Curator) - use get_enabling_service()
        Tier 2: Direct import and initialization (fallback)
        Tier 3: N/A (no SOA API or Platform Gateway equivalent)
        Tier 4: Return None (calling code handles None gracefully)
        """
        if self._insights_generator_service is None:
            try:
                # Tier 1: Try Enabling Service via Curator (four-tier pattern)
                insights_generator = await self.get_enabling_service("InsightsGeneratorService")
                if insights_generator:
                    self._insights_generator_service = insights_generator
                    self.logger.info("✅ Insights Generator Service discovered via Curator")
                    return insights_generator
                
                # Tier 2: Fallback - Import and initialize directly
                self.logger.warning("⚠️ Insights Generator Service not found via Curator, initializing directly")
                from backend.business_enablement.enabling_services.insights_generator_service.insights_generator_service import InsightsGeneratorService
                
                self._insights_generator_service = InsightsGeneratorService(
                    service_name="InsightsGeneratorService",
                    realm_name="business_enablement",  # Enabling services stay in business_enablement
                    platform_gateway=self.insights_manager.platform_gateway,
                    di_container=self.insights_manager.di_container
                )
                await self._insights_generator_service.initialize()
                self.logger.info("✅ Insights Generator Service initialized directly")
                
            except Exception as e:
                self.logger.error(f"❌ Insights Generator Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                # Tier 4: Return None - calling code handles None gracefully with structured error
                return None
        
        return self._insights_generator_service
    
    async def _get_semantic_enrichment_gateway(self):
        """
        Get Semantic Enrichment Gateway Service via Curator discovery.
        
        Phase 4: Gateway for semantic layer enrichment requests.
        Maintains security boundary while enabling enrichment.
        
        Returns:
            SemanticEnrichmentGatewayService instance or None if not available
        """
        if self._semantic_enrichment_gateway is None:
            try:
                # Try Enabling Service via Curator (four-tier pattern)
                gateway = await self.get_enabling_service("SemanticEnrichmentGatewayService")
                if gateway:
                    self._semantic_enrichment_gateway = gateway
                    self.logger.info("✅ Semantic Enrichment Gateway discovered via Curator")
                    return gateway
                
                # Fallback: Try direct import (Content realm service - other realms use Content for data needs)
                self.logger.debug("⚠️ Semantic Enrichment Gateway not found via Curator, trying direct import")
                from backend.content.services.semantic_enrichment_gateway.semantic_enrichment_gateway import SemanticEnrichmentGateway
                
                gateway = SemanticEnrichmentGateway(
                    service_name="SemanticEnrichmentGatewayService",
                    realm_name="content",  # ✅ Content realm service
                    platform_gateway=self.platform_gateway,
                    di_container=self.di_container
                )
                await gateway.initialize()
                self._semantic_enrichment_gateway = gateway
                self.logger.info("✅ Semantic Enrichment Gateway initialized directly")
                return gateway
                
            except Exception as e:
                self.logger.warning(f"⚠️ Semantic Enrichment Gateway not available: {e}")
                return None
        
        return self._semantic_enrichment_gateway
    
    # ========================================================================
    # PHASE 6: DATA SOLUTION ORCHESTRATOR HELPER METHODS
    # ========================================================================
    
    async def get_semantic_embeddings_via_data_solution(
        self,
        file_id: Optional[str] = None,
        parsed_file_id: Optional[str] = None,
        content_id: Optional[str] = None,
        embedding_type: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get semantic embeddings via Data Solution Orchestrator (Phase 6).
        
        This is the ONLY way agents should access semantic data.
        Maintains security boundary - platform uses semantic data only.
        
        Args:
            file_id: File identifier (if provided directly)
            parsed_file_id: Optional parsed file identifier (if provided directly)
            content_id: Content metadata ID (if file_id not provided, will look up from content_id)
            embedding_type: Optional filter by embedding type (e.g., "schema", "chunk")
            user_context: Optional user context for security and tenant validation
        
        Returns:
            List of semantic embeddings
        """
        try:
            # If content_id provided but file_id not, get file_id from content metadata
            if content_id and not file_id:
                librarian = await self.get_librarian_api()
                if librarian:
                    content_metadata = await librarian.get_content_metadata(content_id, user_context)
                    if content_metadata:
                        file_id = content_metadata.get("file_id")
                        parsed_file_id = parsed_file_id or content_metadata.get("parsed_file_id")
                else:
                    self.logger.warning(f"⚠️ Librarian not available to get file_id from content_id: {content_id}")
                    return []
            
            if not file_id:
                self.logger.warning("⚠️ file_id required but not provided")
                return []
            
            # Get Data Solution Orchestrator
            data_solution = await self._get_data_solution_orchestrator()
            
            # Expose semantic data via Data Solution Orchestrator
            expose_result = await data_solution.orchestrate_data_expose(
                file_id=file_id,
                parsed_file_id=parsed_file_id,
                user_context=user_context
            )
            
            if not expose_result.get("success"):
                self.logger.warning(f"⚠️ Failed to expose semantic data: {expose_result.get('error')}")
                return []
            
            embeddings = expose_result.get("embeddings", [])
            
            # Filter by embedding_type if specified
            if embedding_type:
                embeddings = [emb for emb in embeddings if emb.get("embedding_type") == embedding_type]
            
            return embeddings
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get semantic embeddings via Data Solution Orchestrator: {e}")
            return []
    
    def _determine_data_type(self, embeddings: List[Dict[str, Any]]) -> str:
        """
        Determine data type from embeddings.
        
        Phase 6: Helper method for data type detection.
        
        Args:
            embeddings: List of semantic embeddings
        
        Returns:
            "structured" or "unstructured"
        """
        if not embeddings:
            return "unstructured"
        
        # Check for schema embeddings (indicates structured data)
        schema_embeddings = [emb for emb in embeddings if emb.get("embedding_type") == "schema"]
        if schema_embeddings:
            return "structured"
        
        # Check for chunk embeddings with structured patterns
        chunk_embeddings = [emb for emb in embeddings if emb.get("embedding_type") == "chunk"]
        for chunk in chunk_embeddings:
            # If chunk has structured metadata (columns, rows, etc.), it's structured
            if chunk.get("metadata", {}).get("has_columns") or chunk.get("metadata", {}).get("is_tabular"):
                return "structured"
        
        return "unstructured"
    
    def _needs_enrichment(self, user_query: str, embeddings: List[Dict[str, Any]]) -> bool:
        """
        Determine if enrichment is needed based on query and available embeddings.
        
        Phase 6: Helper method for enrichment detection.
        
        Args:
            user_query: User's natural language query
            embeddings: Available semantic embeddings
        
        Returns:
            True if enrichment is needed, False otherwise
        """
        if not user_query or not embeddings:
            return False
        
        query_lower = user_query.lower()
        
        # Keywords that might require enrichment
        enrichment_keywords = [
            "specific", "exact", "precise", "detailed", "all values",
            "column values", "row data", "cell data", "raw data"
        ]
        
        # Check if query contains enrichment keywords
        needs_enrichment = any(keyword in query_lower for keyword in enrichment_keywords)
        
        # Check if embeddings have schema but query asks for values
        has_schema = any(emb.get("embedding_type") == "schema" for emb in embeddings)
        asks_for_values = any(keyword in query_lower for keyword in ["values", "data", "numbers", "text"])
        
        if has_schema and asks_for_values:
            # Schema exists but query asks for actual values - might need enrichment
            return True
        
        return needs_enrichment
    
    def _build_enrichment_request(self, user_query: str) -> Dict[str, Any]:
        """
        Build enrichment request from user query.
        
        Phase 6: Helper method for enrichment request building.
        
        Args:
            user_query: User's natural language query
        
        Returns:
            Enrichment request dict
        """
        query_lower = user_query.lower()
        
        # Determine enrichment type based on query
        enrichment_type = "column_values"  # Default
        
        if "statistics" in query_lower or "stats" in query_lower:
            enrichment_type = "statistics"
        elif "correlation" in query_lower or "correlate" in query_lower:
            enrichment_type = "correlations"
        elif "distribution" in query_lower or "distribute" in query_lower:
            enrichment_type = "distributions"
        
        return {
            "type": enrichment_type,
            "description": user_query,
            "filters": {}  # Can be enhanced to extract column/row filters from query
        }
    
    def _needs_visualization(self, user_query: str) -> bool:
        """
        Determine if visualization is needed based on query.
        
        Phase 6: Helper method for visualization detection.
        
        Args:
            user_query: User's natural language query
        
        Returns:
            True if visualization is needed, False otherwise
        """
        if not user_query:
            return False
        
        query_lower = user_query.lower()
        viz_keywords = ["show", "display", "chart", "graph", "plot", "visualize", "visualization", "view"]
        return any(keyword in query_lower for keyword in viz_keywords)
    
    async def _validate_tenant_access(self, user_tenant_id: str, resource_tenant_id: str) -> bool:
        """
        Helper method to validate tenant access (handles both async and sync cases).
        
        Args:
            user_tenant_id: User's tenant ID
            resource_tenant_id: Resource's tenant ID
        
        Returns:
            bool: True if access is allowed, False otherwise
        """
        tenant = self._realm_service.get_tenant()
        if not tenant:
            return True  # No tenant validation available, allow access
        
        try:
            # Check if validate_tenant_access is a coroutine function
            if asyncio.iscoroutinefunction(tenant.validate_tenant_access):
                return await tenant.validate_tenant_access(user_tenant_id, resource_tenant_id)
            else:
                # Synchronous call
                return tenant.validate_tenant_access(user_tenant_id, resource_tenant_id)
        except Exception as e:
            self.logger.warning(f"⚠️ Tenant validation failed: {e}")
            return False  # Fail closed
    
    async def initialize(self) -> bool:
        """
        Initialize Insights Orchestrator and its agents.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self._realm_service.log_operation_with_telemetry(
            "insights_orchestrator_initialize_start",
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
            self.content_steward = await self.get_content_steward_api()
            
            # 2. Initialize Liaison Agent using OrchestratorBase helper (via Agentic Foundation factory)
            # Use the main InsightsLiaisonAgent from insights/agents (not the duplicate)
            from backend.insights.agents.insights_liaison_agent import InsightsLiaisonAgent
            liaison_agent = await self.initialize_agent(
                InsightsLiaisonAgent,
                "InsightsLiaisonAgent",
                agent_type="liaison",
                capabilities=["conversation", "guidance", "analysis_support"],
                required_roles=[]  # Liaison agents don't require Smart City roles
            )
            
            # Store in both legacy attribute and _agents dict (for backward compatibility and get_agent() access)
            self.liaison_agent = liaison_agent
            if liaison_agent:
                # Ensure it's in _agents dict for get_agent() to find it
                if "InsightsLiaisonAgent" not in self._agents:
                    self._agents["InsightsLiaisonAgent"] = liaison_agent
                liaison_agent.pillar = "insights"
                self.logger.info("✅ InsightsLiaisonAgent initialized and accessible via get_agent()")
            else:
                self.logger.warning("⚠️ Failed to initialize InsightsLiaisonAgent")
            
            # 2.1. Initialize Query Agent (Phase 5)
            from .agents import InsightsQueryAgent
            query_agent = await self.initialize_agent(
                InsightsQueryAgent,
                "InsightsQueryAgent",
                agent_type="query",
                capabilities=["query_generation", "schema_analysis"],
                required_roles=[]
            )
            if query_agent:
                self.logger.info("✅ InsightsQueryAgent initialized")
            else:
                self.logger.warning("⚠️ Failed to initialize InsightsQueryAgent")
            
            # 2.2. Initialize Business Analysis Agent (Phase 3)
            from .agents import InsightsBusinessAnalysisAgent
            business_analysis_agent = await self.initialize_agent(
                InsightsBusinessAnalysisAgent,
                "InsightsBusinessAnalysisAgent",
                agent_type="analysis",
                capabilities=["structured_analysis", "unstructured_analysis", "business_narrative"],
                required_roles=[]
            )
            if business_analysis_agent:
                # Set orchestrator reference for Data Solution Orchestrator access
                business_analysis_agent.orchestrator = self
                business_analysis_agent.insights_orchestrator = self
                self.logger.info("✅ InsightsBusinessAnalysisAgent initialized")
            else:
                self.logger.warning("⚠️ Failed to initialize InsightsBusinessAnalysisAgent")
            
            # 2.3. Set orchestrator reference on Query Agent for Data Solution Orchestrator access
            if query_agent:
                query_agent.orchestrator = self
                query_agent.insights_orchestrator = self
            
            # 2.5. Initialize Specialist Agent (AI Showcase - Data Science Orchestrator)
            from .agents import InsightsSpecialistAgent
            
            self.specialist_agent = await self.initialize_agent(
                InsightsSpecialistAgent,
                "InsightsSpecialistAgent",
                agent_type="specialist",
                capabilities=[
                    "data_science_orchestration",
                    "grounded_insight_generation",
                    "business_narrative_generation",
                    "double_click_exploration",
                    "insights_summary_generation"
                ],
                required_roles=[],
                specialist_capability=SpecialistCapability.DATA_ANALYSIS
            )
            
            # Give specialist agent access to orchestrator (for MCP server access)
            if self.specialist_agent and hasattr(self.specialist_agent, 'set_orchestrator'):
                self.specialist_agent.set_orchestrator(self)
            
            # 2.6. Initialize MCP Server (exposes orchestrator methods as MCP tools)
            from .mcp_server import InsightsMCPServer
            
            self.mcp_server = InsightsMCPServer(
                orchestrator=self,
                di_container=self.di_container
            )
            # MCP server registers tools in __init__, ready to use
            self.logger.info(f"✅ {self.orchestrator_name} MCP Server initialized")
            
            # 3. Initialize workflows
            from .workflows import (
                StructuredAnalysisWorkflow,
                UnstructuredAnalysisWorkflow,
                HybridAnalysisWorkflow
            )
            self.structured_workflow = StructuredAnalysisWorkflow(self)
            self.unstructured_workflow = UnstructuredAnalysisWorkflow(self)
            self.hybrid_workflow = HybridAnalysisWorkflow(self)
            
            # 4. Initialize DataInsightsQueryService (NLP queries for analytics)
            from backend.business_enablement.enabling_services.data_insights_query_service import DataInsightsQueryService
            self.data_insights_query_service = DataInsightsQueryService(
                service_name="DataInsightsQueryService",
                realm_name=self.realm_name,
                platform_gateway=self.platform_gateway,
                di_container=self.di_container
            )
            await self.data_insights_query_service.initialize()
            self.logger.info("✅ DataInsightsQueryService initialized")
            
            # 5. Initialize analysis cache (for query support)
            self.analysis_cache = {}
            
            # 6. Register with Curator (Phase 2 pattern with CapabilityDefinition structure)
            await self._realm_service.register_with_curator(
                capabilities=[
                    {
                        "name": "metrics_calculation",
                        "protocol": "InsightsOrchestratorProtocol",
                        "description": "Calculate business metrics from data",
                        "contracts": {
                            "soa_api": {
                                "api_name": "calculate_metrics",
                                "endpoint": "/api/v1/insights-pillar/calculate-metrics",
                                "method": "POST",
                                "handler": self.calculate_metrics,
                                "metadata": {
                                    "description": "Calculate business metrics",
                                    "parameters": ["resource_id", "options"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "calculate_metrics_tool",
                                "tool_definition": {
                                    "name": "calculate_metrics_tool",
                                    "description": "Calculate business metrics from data",
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
                            "domain_capability": "insights.calculate_metrics",
                            "semantic_api": "/api/v1/insights-pillar/calculate-metrics",
                            "user_journey": "calculate_metrics"
                        }
                    },
                    {
                        "name": "insight_generation",
                        "protocol": "InsightsOrchestratorProtocol",
                        "description": "Generate insights from data",
                        "contracts": {
                            "soa_api": {
                                "api_name": "generate_insights",
                                "endpoint": "/api/v1/insights-pillar/generate-insights",
                                "method": "POST",
                                "handler": self.generate_insights,
                                "metadata": {
                                    "description": "Generate insights from data",
                                    "parameters": ["resource_id", "options"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "generate_insights_tool",
                                "tool_definition": {
                                    "name": "generate_insights_tool",
                                    "description": "Generate insights from data",
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
                            "domain_capability": "insights.generate_insights",
                            "semantic_api": "/api/v1/insights-pillar/generate-insights",
                            "user_journey": "generate_insights"
                        }
                    },
                    {
                        "name": "visualization_creation",
                        "protocol": "InsightsOrchestratorProtocol",
                        "description": "Create visual dashboards",
                        "contracts": {
                            "soa_api": {
                                "api_name": "create_visualization",
                                "endpoint": "/api/v1/insights-pillar/create-visualization",
                                "method": "POST",
                                "handler": self.create_visualization,
                                "metadata": {
                                    "description": "Create visual dashboards",
                                    "parameters": ["resource_id", "options"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "create_visualization_tool",
                                "tool_definition": {
                                    "name": "create_visualization_tool",
                                    "description": "Create visual dashboards",
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
                            "domain_capability": "insights.create_visualization",
                            "semantic_api": "/api/v1/insights-pillar/create-visualization",
                            "user_journey": "create_visualization"
                        }
                    },
                    {
                        "name": "trend_analysis",
                        "protocol": "InsightsOrchestratorProtocol",
                        "description": "Analyze data trends",
                        "contracts": {
                            "soa_api": {
                                "api_name": "analyze_trends",
                                "endpoint": "/api/v1/insights-pillar/analyze-trends",
                                "method": "POST",
                                "handler": self.analyze_trends,
                                "metadata": {
                                    "description": "Analyze data trends",
                                    "parameters": ["resource_id", "options"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "insights.analyze_trends",
                            "semantic_api": "/api/v1/insights-pillar/analyze-trends",
                            "user_journey": "analyze_trends"
                        }
                    },
                    {
                        "name": "content_analysis",
                        "protocol": "InsightsOrchestratorProtocol",
                        "description": "Analyze content for insights",
                        "contracts": {
                            "soa_api": {
                                "api_name": "analyze_content_for_insights",
                                "endpoint": "/api/v1/insights-pillar/analyze-content",
                                "method": "POST",
                                "handler": self.analyze_content_for_insights,
                                "metadata": {
                                    "description": "Analyze content for insights",
                                    "parameters": ["source_type", "file_id", "content_metadata_id", "content_type", "analysis_options"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "insights.analyze_content",
                            "semantic_api": "/api/v1/insights-pillar/analyze-content",
                            "user_journey": "analyze_content"
                        }
                    },
                    {
                        "name": "nlp_queries",
                        "protocol": "InsightsOrchestratorProtocol",
                        "description": "Query analysis results using natural language",
                        "contracts": {
                            "soa_api": {
                                "api_name": "query_analysis_results",
                                "endpoint": "/api/v1/insights-pillar/query-analysis",
                                "method": "POST",
                                "handler": self.query_analysis_results,
                                "metadata": {
                                    "description": "Query analysis results using natural language",
                                    "parameters": ["query", "analysis_id", "query_type"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "insights.query_analysis",
                            "semantic_api": "/api/v1/insights-pillar/query-analysis",
                            "user_journey": "query_analysis"
                        }
                    }
                ],
                soa_apis=["calculate_metrics", "generate_insights", "create_visualization", "analyze_trends", "analyze_content_for_insights", "query_analysis_results"],
                mcp_tools=["calculate_metrics_tool", "generate_insights_tool", "create_visualization_tool"]
            )
            
            # Record health metric
            await self._realm_service.record_health_metric(
                "insights_orchestrator_initialized",
                1.0,
                {"orchestrator": self.orchestrator_name}
            )
            
            # End telemetry tracking
            await self._realm_service.log_operation_with_telemetry(
                "insights_orchestrator_initialize_complete",
                success=True
            )
            
            self.logger.info(f"✅ {self.orchestrator_name} initialized successfully")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self._realm_service.handle_error_with_audit(e, "insights_orchestrator_initialize")
            
            # End telemetry tracking with failure
            await self._realm_service.log_operation_with_telemetry(
                "insights_orchestrator_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Failed to initialize {self.orchestrator_name}: {e}")
            return False
    
    # ========================================================================
    # MVP USE CASE APIs (Preserve UI Integration)
    # ========================================================================
    
    async def calculate_metrics(
        self,
        resource_id: str,
        options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate business metrics (MVP use case orchestration).
        
        OLD: InsightsPillar.calculate_metrics() - internal micro-modules
        NEW: Delegates to enabling services + Smart City
        
        This method preserves the API surface for the MVP UI.
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self._realm_service.log_operation_with_telemetry(
            "calculate_metrics_start",
            success=True,
            details={"resource_id": resource_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self._realm_service.security.check_permissions(user_context, "calculate_metrics", "execute"):
                await self._realm_service.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "calculate_metrics",
                    details={"user_id": user_context.get("user_id"), "resource_id": resource_id}
                )
                await self._realm_service.record_health_metric("calculate_metrics_access_denied", 1.0, {"resource_id": resource_id})
                await self._realm_service.log_operation_with_telemetry("calculate_metrics_complete", success=False)
                return {"status": "error", "message": "Permission denied"}
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self._validate_tenant_access(tenant_id, tenant_id):
                await self._realm_service.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "calculate_metrics",
                    details={"tenant_id": tenant_id, "resource_id": resource_id}
                )
                await self._realm_service.record_health_metric("calculate_metrics_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self._realm_service.log_operation_with_telemetry("calculate_metrics_complete", success=False)
                return {"status": "error", "message": "Tenant access denied"}
        
        try:
            self.logger.info(f"📊 Calculating metrics: {resource_id}")
            options = options or {}
            results = {}
            
            # Step 1: Analyze data via Data Analyzer
            data_analyzer = await self._get_data_analyzer_service()
            if data_analyzer:
                analysis_type = options.get("analysis_type", "descriptive")
                analysis_result = await data_analyzer.analyze_data(
                    data_id=resource_id,
                    analysis_type=analysis_type,
                    analysis_options=options.get("analysis_options", {})
                )
                if analysis_result.get("success"):
                    results["analysis"] = analysis_result
                else:
                    results["analysis"] = {"error": "Data analysis failed"}
            else:
                results["analysis"] = {"error": "Data Analyzer service not available"}
            
            # Step 2: Calculate metrics via Metrics Calculator
            metrics_calculator = await self._get_metrics_calculator_service()
            if metrics_calculator and results.get("analysis", {}).get("success"):
                # Use calculate_kpi for KPI calculation or calculate_metric for single metric
                kpi_name = options.get("metric_name", "default_kpi")
                metric_params = options.get("metric_params", {})
                kpi_formula = metric_params.get("formula") if isinstance(metric_params, dict) else None
                metrics_result = await metrics_calculator.calculate_kpi(
                    kpi_name=kpi_name,
                    data_sources=resource_id,  # resource_id is the data source
                    kpi_formula=kpi_formula
                )
                if metrics_result.get("success"):
                    results["metrics"] = metrics_result
                else:
                    results["metrics"] = {"error": "Metrics calculation failed"}
            else:
                results["metrics"] = {"error": "Metrics Calculator service not available"}
            
            # Step 3: Track lineage via Data Steward
            await self.track_data_lineage({
                "source": resource_id,
                "destination": f"{resource_id}_metrics",
                "transformation": {
                    "type": "metrics_calculation",
                    "orchestrator": self.orchestrator_name
                }
            })
            
            # Step 4: Store results via Librarian
            storage_result = await self.store_document(
                document_data=results,
                metadata={
                    "resource_id": resource_id,
                    "capability": "calculate_metrics",
                    "orchestrator": self.orchestrator_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            self.logger.info(f"✅ Metrics calculation complete: {resource_id}")
            
            # Record health metric (success)
            await self._realm_service.record_health_metric("calculate_metrics_success", 1.0, {"resource_id": resource_id})
            
            # End telemetry tracking
            await self._realm_service.log_operation_with_telemetry("calculate_metrics_complete", success=True, details={"resource_id": resource_id})
            
            # Format response for MVP UI (preserves contract)
            return self._format_for_mvp_ui(results, resource_id, storage_result)
            
        except Exception as e:
            # Error handling with audit
            await self._realm_service.handle_error_with_audit(e, "calculate_metrics")
            
            # Record health metric (failure)
            await self._realm_service.record_health_metric("calculate_metrics_failed", 1.0, {"resource_id": resource_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self._realm_service.log_operation_with_telemetry("calculate_metrics_complete", success=False, details={"resource_id": resource_id, "error": str(e)})
            
            self.logger.error(f"❌ Metrics calculation failed: {e}")
            return {
                "status": "error",
                "message": f"Metrics calculation failed: {str(e)}",
                "error": str(e)
            }
    
    async def generate_insights(
        self,
        resource_id: str,
        options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate insights from data (MVP use case orchestration).
        
        Orchestrates DataAnalyzer + MetricsCalculator + VisualizationEngine.
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self._realm_service.log_operation_with_telemetry(
            "generate_insights_start",
            success=True,
            details={"resource_id": resource_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self._realm_service.security.check_permissions(user_context, "generate_insights", "execute"):
                await self._realm_service.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "generate_insights",
                    details={"user_id": user_context.get("user_id"), "resource_id": resource_id}
                )
                await self._realm_service.record_health_metric("generate_insights_access_denied", 1.0, {"resource_id": resource_id})
                await self._realm_service.log_operation_with_telemetry("generate_insights_complete", success=False)
                return {"status": "error", "message": "Permission denied"}
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self._validate_tenant_access(tenant_id, tenant_id):
                await self._realm_service.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "generate_insights",
                    details={"tenant_id": tenant_id, "resource_id": resource_id}
                )
                await self._realm_service.record_health_metric("generate_insights_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self._realm_service.log_operation_with_telemetry("generate_insights_complete", success=False)
                return {"status": "error", "message": "Tenant access denied"}
        
        try:
            self.logger.info(f"💡 Generating insights: {resource_id}")
            options = options or {}
            results = {}
            
            # Step 1: Analyze data
            data_analyzer = await self._get_data_analyzer_service()
            if data_analyzer:
                analysis_type = options.get("analysis_type", "descriptive")
                analysis_result = await data_analyzer.analyze_data(
                    data_id=resource_id,
                    analysis_type=analysis_type,
                    analysis_options=options.get("analysis_options", {})
                )
                results["analysis"] = analysis_result if analysis_result.get("success") else {"error": "Analysis failed"}
            else:
                results["analysis"] = {"error": "Data Analyzer not available"}
            
            # Step 2: Calculate metrics
            metrics_calculator = await self._get_metrics_calculator_service()
            if metrics_calculator:
                metrics_result = await metrics_calculator.calculate_kpi(
                    kpi_name="insights_kpi",
                    data_sources=resource_id,  # resource_id is the data source
                    kpi_formula=None
                )
                results["metrics"] = metrics_result if metrics_result.get("success") else {"error": "Metrics failed"}
            else:
                results["metrics"] = {"error": "Metrics Calculator not available"}
            
            # Step 3: Create visualization (if requested)
            if options.get("include_visualization"):
                visualization_engine = await self._get_visualization_engine_service()
                if visualization_engine:
                    viz_result = await visualization_engine.create_visualization(
                        data_id=resource_id,
                        visualization_type="insights_dashboard",
                        options={"data": results}
                    )
                    results["visualization"] = viz_result if viz_result.get("success") else {"error": "Visualization failed"}
            
            # Track lineage
            await self.track_data_lineage({
                "source": resource_id,
                "destination": f"{resource_id}_insights",
                "transformation": {"type": "insight_generation", "orchestrator": self.orchestrator_name}
            })
            
            # Store results
            storage_result = await self.store_document(
                document_data=results,
                metadata={
                    "resource_id": resource_id,
                    "capability": "generate_insights",
                    "orchestrator": self.orchestrator_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            self.logger.info(f"✅ Insights generation complete: {resource_id}")
            
            # Record health metric (success)
            await self._realm_service.record_health_metric("generate_insights_success", 1.0, {"resource_id": resource_id})
            
            # End telemetry tracking
            await self._realm_service.log_operation_with_telemetry("generate_insights_complete", success=True, details={"resource_id": resource_id})
            
            return self._format_for_mvp_ui(results, resource_id, storage_result)
            
        except Exception as e:
            # Error handling with audit
            await self._realm_service.handle_error_with_audit(e, "generate_insights")
            
            # Record health metric (failure)
            await self._realm_service.record_health_metric("generate_insights_failed", 1.0, {"resource_id": resource_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self._realm_service.log_operation_with_telemetry("generate_insights_complete", success=False, details={"resource_id": resource_id, "error": str(e)})
            
            self.logger.error(f"❌ Insights generation failed: {e}")
            return {"status": "error", "message": f"Insights generation failed: {str(e)}", "error": str(e)}
    
    async def create_visualization(
        self,
        resource_id: str,
        options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create visual dashboards (MVP use case orchestration).
        
        Orchestrates MetricsCalculator + VisualizationEngine.
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self._realm_service.log_operation_with_telemetry(
            "create_visualization_start",
            success=True,
            details={"resource_id": resource_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self._realm_service.security.check_permissions(user_context, "create_visualization", "execute"):
                await self._realm_service.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "create_visualization",
                    details={"user_id": user_context.get("user_id"), "resource_id": resource_id}
                )
                await self._realm_service.record_health_metric("create_visualization_access_denied", 1.0, {"resource_id": resource_id})
                await self._realm_service.log_operation_with_telemetry("create_visualization_complete", success=False)
                return {"status": "error", "message": "Permission denied"}
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self._validate_tenant_access(tenant_id, tenant_id):
                await self._realm_service.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "create_visualization",
                    details={"tenant_id": tenant_id, "resource_id": resource_id}
                )
                await self._realm_service.record_health_metric("create_visualization_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self._realm_service.log_operation_with_telemetry("create_visualization_complete", success=False)
                return {"status": "error", "message": "Tenant access denied"}
        
        try:
            self.logger.info(f"📊 Creating visualization: {resource_id}")
            options = options or {}
            
            # Step 1: Get metrics
            metrics_calculator = await self._get_metrics_calculator_service()
            metrics_data = {}
            if metrics_calculator:
                metrics_result = await metrics_calculator.calculate_kpi(
                    kpi_name="visualization_kpi",
                    data_sources=resource_id,  # resource_id is the data source
                    kpi_formula=None
                )
                metrics_data = metrics_result.get("kpi_value", {}) if metrics_result.get("success") else {}
            
            # Step 2: Create visualization
            visualization_engine = await self._get_visualization_engine_service()
            if visualization_engine:
                viz_result = await visualization_engine.create_visualization(
                    data_id=resource_id,
                    visualization_type=options.get("chart_type", "dashboard"),
                    options={"data": metrics_data}
                )
                if viz_result.get("success"):
                    # Store and return
                    storage_result = await self.store_document(
                        document_data=viz_result,
                        metadata={
                            "resource_id": resource_id,
                            "capability": "create_visualization",
                            "orchestrator": self.orchestrator_name,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                    # Record health metric (success)
                    await self._realm_service.record_health_metric("create_visualization_success", 1.0, {"resource_id": resource_id})
                    
                    # End telemetry tracking
                    await self._realm_service.log_operation_with_telemetry("create_visualization_complete", success=True, details={"resource_id": resource_id})
                    
                    return self._format_for_mvp_ui({"visualization": viz_result}, resource_id, storage_result)
                else:
                    await self._realm_service.record_health_metric("create_visualization_failed", 1.0, {"resource_id": resource_id, "error": "Visualization creation failed"})
                    await self._realm_service.log_operation_with_telemetry("create_visualization_complete", success=False)
                    return {"status": "error", "message": "Visualization creation failed"}
            else:
                await self._realm_service.record_health_metric("create_visualization_failed", 1.0, {"resource_id": resource_id, "error": "Visualization Engine not available"})
                await self._realm_service.log_operation_with_telemetry("create_visualization_complete", success=False)
                return {"status": "error", "message": "Visualization Engine not available"}
                
        except Exception as e:
            # Error handling with audit
            await self._realm_service.handle_error_with_audit(e, "create_visualization")
            
            # Record health metric (failure)
            await self._realm_service.record_health_metric("create_visualization_failed", 1.0, {"resource_id": resource_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self._realm_service.log_operation_with_telemetry("create_visualization_complete", success=False, details={"resource_id": resource_id, "error": str(e)})
            
            self.logger.error(f"❌ Visualization creation failed: {e}")
            return {"status": "error", "message": f"Visualization creation failed: {str(e)}", "error": str(e)}
    
    async def analyze_trends(
        self,
        resource_id: str,
        options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze data trends (MVP use case orchestration).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self._realm_service.log_operation_with_telemetry(
            "analyze_trends_start",
            success=True,
            details={"resource_id": resource_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self._realm_service.security.check_permissions(user_context, "analyze_trends", "execute"):
                await self._realm_service.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "analyze_trends",
                    details={"user_id": user_context.get("user_id"), "resource_id": resource_id}
                )
                await self._realm_service.record_health_metric("analyze_trends_access_denied", 1.0, {"resource_id": resource_id})
                await self._realm_service.log_operation_with_telemetry("analyze_trends_complete", success=False)
                return {"status": "error", "message": "Permission denied"}
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self._validate_tenant_access(tenant_id, tenant_id):
                await self._realm_service.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "analyze_trends",
                    details={"tenant_id": tenant_id, "resource_id": resource_id}
                )
                await self._realm_service.record_health_metric("analyze_trends_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self._realm_service.log_operation_with_telemetry("analyze_trends_complete", success=False)
                return {"status": "error", "message": "Tenant access denied"}
        
        try:
            self.logger.info(f"📈 Analyzing trends: {resource_id}")
            options = options or {}
            
            # Use Data Analyzer for trend analysis
            data_analyzer = await self._get_data_analyzer_service()
            if data_analyzer:
                analysis_result = await data_analyzer.analyze_data(
                    data_id=resource_id,
                    analysis_type="trend",
                    analysis_options=options or {}
                )
                if analysis_result.get("success"):
                    storage_result = await self.store_document(
                        document_data=analysis_result,
                        metadata={
                            "resource_id": resource_id,
                            "capability": "analyze_trends",
                            "orchestrator": self.orchestrator_name,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                    # Record health metric (success)
                    await self._realm_service.record_health_metric("analyze_trends_success", 1.0, {"resource_id": resource_id})
                    
                    # End telemetry tracking
                    await self._realm_service.log_operation_with_telemetry("analyze_trends_complete", success=True, details={"resource_id": resource_id})
                    
                    return self._format_for_mvp_ui({"trends": analysis_result}, resource_id, storage_result)
                else:
                    await self._realm_service.record_health_metric("analyze_trends_failed", 1.0, {"resource_id": resource_id, "error": "Trend analysis failed"})
                    await self._realm_service.log_operation_with_telemetry("analyze_trends_complete", success=False)
                    return {"status": "error", "message": "Trend analysis failed"}
            else:
                await self._realm_service.record_health_metric("analyze_trends_failed", 1.0, {"resource_id": resource_id, "error": "Data Analyzer not available"})
                await self._realm_service.log_operation_with_telemetry("analyze_trends_complete", success=False)
                return {"status": "error", "message": "Data Analyzer not available"}
                
        except Exception as e:
            # Error handling with audit
            await self._realm_service.handle_error_with_audit(e, "analyze_trends")
            
            # Record health metric (failure)
            await self._realm_service.record_health_metric("analyze_trends_failed", 1.0, {"resource_id": resource_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self._realm_service.log_operation_with_telemetry("analyze_trends_complete", success=False, details={"resource_id": resource_id, "error": str(e)})
            
            self.logger.error(f"❌ Trend analysis failed: {e}")
            return {"status": "error", "message": f"Trend analysis failed: {str(e)}", "error": str(e)}
    
    # ========================================================================
    # NEW SEMANTIC API METHODS (Align with API Contract)
    # ========================================================================
    
    async def analyze_content_for_insights(
        self,
        source_type: str,
        file_id: Optional[str] = None,
        content_metadata_id: Optional[str] = None,
        content_type: str = "structured",
        analysis_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze content for insights (NEW semantic API method).
        
        This is the primary analysis method that aligns with our API contract.
        Supports both file and content_metadata sources.
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            source_type: 'file' or 'content_metadata'
            file_id: File identifier (if source_type='file')
            content_metadata_id: Content metadata ID from ArangoDB (if source_type='content_metadata')
            content_type: 'structured', 'unstructured', or 'hybrid'
            analysis_options: Optional configuration
                - include_visualizations: bool (default: True)
                - include_tabular_summary: bool (default: True)
                - aar_specific_analysis: bool (default: False)
            user_context: User context for security and tenant validation
        
        Returns:
            Dict[str, Any]: Analysis result with 3-way summary
                {
                    "success": bool,
                    "analysis_id": str,
                    "summary": {
                        "textual": str,
                        "tabular": {...},
                        "visualizations": [...]
                    },
                    "insights": [...],
                    "aar_analysis": {...},  # Optional
                    "metadata": {...}
                }
        """
        # Start telemetry tracking
        await self._realm_service.log_operation_with_telemetry(
            "analyze_content_for_insights_start",
            success=True,
            details={"source_type": source_type, "content_type": content_type}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self._realm_service.security.check_permissions(user_context, "analyze_content_for_insights", "execute"):
                await self._realm_service.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "analyze_content_for_insights",
                    details={"user_id": user_context.get("user_id"), "source_type": source_type}
                )
                await self._realm_service.record_health_metric("analyze_content_for_insights_access_denied", 1.0, {"source_type": source_type})
                await self._realm_service.log_operation_with_telemetry("analyze_content_for_insights_complete", success=False)
                return {"success": False, "error": "Permission denied", "timestamp": datetime.utcnow().isoformat()}
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self._validate_tenant_access(tenant_id, tenant_id):
                await self._realm_service.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "analyze_content_for_insights",
                    details={"tenant_id": tenant_id, "source_type": source_type}
                )
                await self._realm_service.record_health_metric("analyze_content_for_insights_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self._realm_service.log_operation_with_telemetry("analyze_content_for_insights_complete", success=False)
                return {"success": False, "error": "Tenant access denied", "timestamp": datetime.utcnow().isoformat()}
        
        try:
            self.logger.info(f"📊 Analyzing content: source_type={source_type}, content_type={content_type}")
            
            # Route to appropriate workflow
            if content_type == "structured":
                result = await self.structured_workflow.execute(
                    source_type=source_type,
                    file_id=file_id,
                    content_metadata_id=content_metadata_id,
                    analysis_options=analysis_options
                )
            elif content_type == "unstructured":
                result = await self.unstructured_workflow.execute(
                    source_type=source_type,
                    file_id=file_id,
                    content_metadata_id=content_metadata_id,
                    analysis_options=analysis_options
                )
            elif content_type == "hybrid":
                result = await self.hybrid_workflow.execute(
                    source_type=source_type,
                    file_id=file_id,
                    content_metadata_id=content_metadata_id,
                    analysis_options=analysis_options
                )
            else:
                return {
                    "success": False,
                    "error": f"Unknown content_type: {content_type}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Cache result for query support
            if result.get("success") and result.get("analysis_id"):
                self.analysis_cache[result["analysis_id"]] = result
            
            # Record health metric (success)
            await self._realm_service.record_health_metric("analyze_content_for_insights_success", 1.0, {"source_type": source_type, "content_type": content_type})
            
            # End telemetry tracking
            await self._realm_service.log_operation_with_telemetry("analyze_content_for_insights_complete", success=True, details={"source_type": source_type, "content_type": content_type})
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self._realm_service.handle_error_with_audit(e, "analyze_content_for_insights")
            
            # Record health metric (failure)
            await self._realm_service.record_health_metric("analyze_content_for_insights_failed", 1.0, {"source_type": source_type, "content_type": content_type, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self._realm_service.log_operation_with_telemetry("analyze_content_for_insights_complete", success=False, details={"source_type": source_type, "content_type": content_type, "error": str(e)})
            
            self.logger.error(f"❌ Content analysis failed: {e}")
            return {
                "success": False,
                "error": "Content analysis failed",
                "error_details": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def query_analysis(
        self,
        query: str,
        analysis_id: str,
        query_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Alias for query_analysis_results (MCP compatibility)."""
        return await self.query_analysis_results(query, analysis_id, query_type)
    
    async def query_analysis_results(
        self,
        query: str,
        analysis_id: str,
        query_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query analysis results using natural language (NEW semantic API method).
        
        This enables conversational analytics - users can ask questions about their analysis.
        
        Args:
            query: Natural language query (e.g., "Show me accounts over 90 days late")
            analysis_id: Analysis ID to query
            query_type: Optional hint ('table', 'chart', 'summary')
        
        Returns:
            Dict[str, Any]: Query result
                {
                    "success": bool,
                    "query_id": str,
                    "result": {
                        "type": "table" | "chart" | "text",
                        "data": ...,
                        "explanation": str
                    },
                    "follow_up_suggestions": [...]
                }
        """
        try:
            self.logger.info(f"💬 Querying analysis: {analysis_id} - '{query}'")
            
            # Get cached analysis
            analysis = self.analysis_cache.get(analysis_id)
            if not analysis:
                return {
                    "success": False,
                    "error": f"Analysis not found: {analysis_id}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Use DataInsightsQueryService to process the query
            result = await self.data_insights_query_service.process_query(
                query=query,
                analysis_id=analysis_id,
                cached_analysis=analysis,
                query_type=query_type
            )
            
            # Return the result directly from the service
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Query processing failed: {e}")
            return {
                "success": False,
                "error": "Query processing failed",
                "error_details": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_analysis_results(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get cached analysis results by ID (NEW semantic API method).
        
        Args:
            analysis_id: Analysis ID
        
        Returns:
            Dict[str, Any]: Analysis result or error
        """
        try:
            analysis = self.analysis_cache.get(analysis_id)
            if analysis:
                return {
                    "success": True,
                    "analysis": analysis
                }
            else:
                return {
                    "success": False,
                    "error": f"Analysis not found: {analysis_id}"
                }
        except Exception as e:
            self.logger.error(f"❌ Failed to get analysis results: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_pillar_summary(
        self,
        analysis_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get Insights Pillar summary for Business Outcomes page (NEW semantic API method).
        
        Returns the 3-way summary (textual, tabular, visualizations) from the most recent
        or specified analysis for display in Business Outcomes pillar.
        
        Args:
            analysis_id: Optional specific analysis ID (defaults to most recent)
        
        Returns:
            Dict[str, Any]: Pillar summary with 3-way content
                {
                    "success": bool,
                    "pillar": "insights",
                    "summary": {
                        "textual": str,
                        "tabular": {...},
                        "visualizations": [...]
                    },
                    "source_analysis_id": str,
                    "generated_at": str
                }
        """
        try:
            # Get the specified or most recent analysis
            if analysis_id:
                analysis = self.analysis_cache.get(analysis_id)
                if not analysis:
                    return {
                        "success": False,
                        "error": f"Analysis not found: {analysis_id}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
            else:
                # Get most recent analysis from cache
                if not self.analysis_cache:
                    return {
                        "success": False,
                        "error": "No analyses available. Please run an analysis first.",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                
                # Get the most recent (last added to cache)
                analysis_id = list(self.analysis_cache.keys())[-1]
                analysis = self.analysis_cache[analysis_id]
            
            # Extract the 3-way summary
            summary = analysis.get("summary", {})
            
            self.logger.info(f"✅ Pillar summary retrieved for analysis: {analysis_id}")
            
            return {
                "success": True,
                "pillar": "insights",
                "summary": {
                    "textual": summary.get("textual", ""),
                    "tabular": summary.get("tabular", {}),
                    "visualizations": summary.get("visualizations", [])
                },
                "source_analysis_id": analysis_id,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get pillar summary: {e}")
            return {
                "success": False,
                "error": "Failed to get pillar summary",
                "error_details": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def list_user_analyses(
        self,
        limit: int = 20,
        offset: int = 0,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List user's analysis history (NEW semantic API method).
        
        Args:
            limit: Number of results to return
            offset: Offset for pagination
            content_type: Optional filter ('structured' | 'unstructured')
        
        Returns:
            Dict[str, Any]: List of analyses with pagination
        """
        try:
            # Get all analyses from cache
            all_analyses = list(self.analysis_cache.values())
            
            # Filter by content_type if specified
            if content_type:
                all_analyses = [
                    a for a in all_analyses
                    if a.get("metadata", {}).get("content_type") == content_type
                ]
            
            # Sort by timestamp (newest first)
            all_analyses.sort(
                key=lambda a: a.get("metadata", {}).get("analysis_timestamp", ""),
                reverse=True
            )
            
            # Paginate
            paginated = all_analyses[offset:offset + limit]
            
            # Format for API response
            analyses_list = []
            for analysis in paginated:
                analyses_list.append({
                    "analysis_id": analysis.get("analysis_id"),
                    "content_type": analysis.get("metadata", {}).get("content_type"),
                    "source_info": analysis.get("metadata", {}).get("source_info", {}),
                    "analyzed_at": analysis.get("metadata", {}).get("analysis_timestamp"),
                    "summary_preview": analysis.get("summary", {}).get("textual", "")[:200],
                    "insight_count": len(analysis.get("insights", [])),
                    "has_visualizations": bool(analysis.get("summary", {}).get("visualizations"))
                })
            
            return {
                "success": True,
                "analyses": analyses_list,
                "pagination": {
                    "total_count": len(all_analyses),
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + limit) < len(all_analyses)
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list analyses: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_available_content_metadata(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get available content metadata for insights analysis (Frontend Gateway API).
        
        Queries Content Steward/Librarian for available content metadata that can be analyzed.
        
        Args:
            user_id: Optional user identifier to filter by user
        
        Returns:
            List of available content metadata with basic info
        """
        try:
            self.logger.info(f"📋 Getting available content metadata for user: {user_id or 'all'}")
            
            # Get Content Steward or Librarian
            librarian = await self.get_librarian_api()
            if not librarian:
                return {
                    "success": False,
                    "content_metadata": [],
                    "error": "Librarian service not available"
                }
            
            # Query content metadata from Supabase
            try:
                filters = {}
                if user_id:
                    filters["user_id"] = user_id
                
                metadata_result = await librarian.query_documents(
                    collection="content_metadata",
                    filters=filters,
                    sort_by="uploaded_at",
                    sort_order="desc"
                )
                
                metadata_list = metadata_result.get("documents", [])
                
                # Format for frontend
                formatted_metadata = []
                for metadata_doc in metadata_list:
                    formatted_metadata.append({
                        "metadata_id": metadata_doc.get("uuid") or metadata_doc.get("file_id"),
                        "file_id": metadata_doc.get("uuid") or metadata_doc.get("file_id"),
                        "ui_name": metadata_doc.get("ui_name", metadata_doc.get("filename", "")),
                        "file_type": metadata_doc.get("file_type", ""),
                        "content_type": metadata_doc.get("content_type", ""),
                        "uploaded_at": metadata_doc.get("uploaded_at", ""),
                        "parsed": metadata_doc.get("parsed", False),
                        "has_metadata": bool(metadata_doc.get("metadata"))
                    })
                
                self.logger.info(f"✅ Found {len(formatted_metadata)} content metadata items")
                
                return {
                    "success": True,
                    "content_metadata": formatted_metadata,
                    "count": len(formatted_metadata)
                }
                
            except Exception as query_error:
                self.logger.warning(f"⚠️ Query method failed: {query_error}")
                
                # Fallback: Try Content Steward
                content_steward = await self.get_content_steward_api()
                if content_steward:
                    return {
                        "success": False,
                        "content_metadata": [],
                        "error": "Content metadata listing not yet implemented via Content Steward",
                        "note": "Need to implement Content Steward metadata listing API"
                    }
                
                return {
                    "success": False,
                    "content_metadata": [],
                    "error": f"Failed to query content metadata: {str(query_error)}"
                }
            
        except Exception as e:
            self.logger.error(f"❌ Get available content metadata failed: {e}")
            return {
                "success": False,
                "content_metadata": [],
                "error": str(e)
            }
    
    async def validate_content_metadata(
        self,
        content_metadata_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Validate content metadata for insights analysis (Frontend Gateway API).
        
        Validates that the specified content metadata is ready for insights analysis.
        
        Args:
            content_metadata_ids: List of content metadata IDs to validate
        
        Returns:
            Validation result with status for each metadata ID
        """
        try:
            self.logger.info(f"✅ Validating {len(content_metadata_ids)} content metadata items")
            
            # Get Librarian
            librarian = await self.get_librarian_api()
            if not librarian:
                return {
                    "success": False,
                    "validated": [],
                    "error": "Librarian service not available"
                }
            
            validated_items = []
            for metadata_id in content_metadata_ids:
                try:
                    # Get metadata document
                    metadata_doc = await librarian.get_document(document_id=metadata_id)
                    
                    if not metadata_doc:
                        validated_items.append({
                            "metadata_id": metadata_id,
                            "valid": False,
                            "error": "Metadata not found"
                        })
                        continue
                    
                    # Check if metadata is ready for analysis
                    is_valid = (
                        metadata_doc.get("parsed", False) and
                        bool(metadata_doc.get("metadata")) and
                        metadata_doc.get("content_type") in ["structured", "unstructured"]
                    )
                    
                    validated_items.append({
                        "metadata_id": metadata_id,
                        "valid": is_valid,
                        "parsed": metadata_doc.get("parsed", False),
                        "has_metadata": bool(metadata_doc.get("metadata")),
                        "content_type": metadata_doc.get("content_type"),
                        "error": None if is_valid else "Metadata not ready for analysis"
                    })
                    
                except Exception as item_error:
                    validated_items.append({
                        "metadata_id": metadata_id,
                        "valid": False,
                        "error": str(item_error)
                    })
            
            valid_count = sum(1 for item in validated_items if item.get("valid"))
            
            self.logger.info(f"✅ Validated {valid_count}/{len(content_metadata_ids)} content metadata items")
            
            return {
                "success": True,
                "validated": validated_items,
                "valid_count": valid_count,
                "total_count": len(content_metadata_ids)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Validate content metadata failed: {e}")
            return {
                "success": False,
                "validated": [],
                "error": str(e)
            }
    
    async def get_analysis_visualizations(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get analysis visualizations (Frontend Gateway API).
        
        Returns visualization data for a specific analysis.
        
        Args:
            analysis_id: Analysis ID
        
        Returns:
            Visualization data (charts, graphs, etc.)
        """
        try:
            self.logger.info(f"📊 Getting visualizations for analysis: {analysis_id}")
            
            # Get analysis from cache
            analysis = self.analysis_cache.get(analysis_id)
            if not analysis:
                return {
                    "success": False,
                    "visualizations": [],
                    "error": f"Analysis not found: {analysis_id}"
                }
            
            # Extract visualizations from analysis summary
            summary = analysis.get("summary", {})
            visualizations = summary.get("visualizations", [])
            
            # If no visualizations in summary, try to generate from analysis data
            if not visualizations:
                # Try to get visualization from VisualizationEngine if available
                visualization_engine = await self._get_visualization_engine_service()
                if visualization_engine:
                    try:
                        viz_result = await visualization_engine.create_visualization(
                            data_id=analysis_id,
                            visualization_type="auto"
                        )
                        if viz_result.get("success"):
                            visualizations = [viz_result.get("visualization", {})]
                    except Exception as viz_error:
                        self.logger.warning(f"⚠️ Visualization generation failed: {viz_error}")
            
            self.logger.info(f"✅ Found {len(visualizations)} visualizations for analysis: {analysis_id}")
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "visualizations": visualizations,
                "count": len(visualizations)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Get analysis visualizations failed: {e}")
            return {
                "success": False,
                "visualizations": [],
                "error": str(e)
            }
    
    # ========================================================================
    # ORCHESTRATION HELPERS
    # ========================================================================
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestration (called by Business Orchestrator)."""
        try:
            action = request.get("action")
            params = request.get("params", {})
            
            if action == "calculate_metrics":
                return await self.calculate_metrics(**params)
            elif action == "generate_insights":
                return await self.generate_insights(**params)
            elif action == "create_visualization":
                return await self.create_visualization(**params)
            elif action == "analyze_trends":
                return await self.analyze_trends(**params)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown action: {action}"
                }
            
        except Exception as e:
            self.logger.error(f"❌ Orchestration execution failed: {e}")
            return {
                "status": "error",
                "message": f"Orchestration execution failed: {str(e)}",
                "error": str(e)
            }
    
    def _format_for_mvp_ui(
        self,
        results: Dict[str, Any],
        resource_id: str,
        storage_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format results for MVP UI (preserves API contract)."""
        response = {
            "status": "success",
            "resource_id": resource_id,
            "data": results,
            "timestamp": datetime.utcnow().isoformat(),
            "orchestrator": self.orchestrator_name
        }
        
        if storage_result:
            response["stored_document_id"] = storage_result.get("document_id")
        
        return response
    
    # ========================================================================
    # HEALTH & METADATA (Inherited from RealmServiceBase)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check (inherited from RealmServiceBase)."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "orchestrator_type": "mvp_use_case",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "mvp_orchestrator",
            "capabilities": ["metrics_calculation", "insight_generation", "visualization_creation", "trend_analysis"],
            "soa_apis": ["calculate_metrics", "generate_insights", "create_visualization", "analyze_trends"],
            "mcp_tools": ["calculate_metrics_tool", "generate_insights_tool", "create_visualization_tool"],
            "legacy_pillar": "InsightsPillar"
        }

