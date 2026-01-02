#!/usr/bin/env python3
"""
Insights Journey Orchestrator - Journey Realm

WHAT: Orchestrates insights operations (data mapping, analysis, quality validation)
HOW: Delegates to Insights realm services while preserving UI integration

This orchestrator is in the Journey realm and orchestrates insights operations.
It extends Smart City capabilities to provide insights and data mapping capabilities.

Architecture:
- Journey Realm: Operations orchestration
- Orchestrates Insights realm services (Field Extraction, Data Quality, Data Transformation)
- Uses Smart City services (ContentSteward, DataSteward) via Curator
- Self-initializing (doesn't require InsightsManager)
"""

import os
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../../'))

from bases.orchestrator_base import OrchestratorBase


class InsightsJourneyOrchestrator(OrchestratorBase):
    """
    Insights Journey Orchestrator - Journey Realm
    
    Orchestrates insights operations:
    - Data mapping (source → target)
    - Data analysis
    - Quality validation
    - Cleanup actions
    
    Extends OrchestratorBase for Smart City access and orchestrator capabilities.
    Preserves MVP UI integration while delegating to Insights realm services.
    
    Key Principles:
    - Journey Realm: Operations orchestration
    - Orchestrates Insights realm services (Field Extraction, Data Quality, Data Transformation)
    - Uses Smart City services (ContentSteward, DataSteward) via Curator
    - Self-initializing (doesn't require InsightsManager)
    """
    
    def __init__(self, platform_gateway, di_container):
        """
        Initialize Insights Journey Orchestrator.
        
        Args:
            platform_gateway: Platform Gateway instance
            di_container: DI Container instance
        """
        # Self-initializing - doesn't require InsightsManager
        super().__init__(
            service_name="InsightsJourneyOrchestratorService",
            realm_name="journey",  # ✅ Journey realm
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        # Set a shorter orchestrator name for MVP UI compatibility
        self.orchestrator_name = "InsightsJourneyOrchestrator"
        
        # Insights realm services (lazy initialization - created on first use)
        self._field_extraction_service = None
        self._data_quality_validation_service = None
        self._data_transformation_service = None
        self._data_analyzer_service = None
        self._visualization_engine_service = None
        self._apg_processor_service = None
        self._insights_generator_service = None
        self._metrics_calculator_service = None
        
        # Agents (lazy initialization - created on first use)
        self._insights_specialist_agent = None
        
        # Workflows
        self._data_mapping_workflow = None
        self._unstructured_analysis_workflow = None
        self._structured_analysis_workflow = None
    
    async def _get_field_extraction_service(self):
        """Lazy initialization of Field Extraction Service (Insights realm service)."""
        if self._field_extraction_service is None:
            try:
                # Import and initialize directly (Insights realm service)
                from backend.insights.services.field_extraction_service.field_extraction_service import FieldExtractionService
                
                self._field_extraction_service = FieldExtractionService(
                    service_name="FieldExtractionService",
                    realm_name="insights",  # ✅ Insights realm service
                    platform_gateway=self.platform_gateway,
                    di_container=self.di_container
                )
                await self._field_extraction_service.initialize()
                self.logger.info("✅ Field Extraction Service initialized (Insights realm)")
                
            except Exception as e:
                self.logger.error(f"❌ Field Extraction Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._field_extraction_service
    
    async def _get_data_quality_validation_service(self):
        """Lazy initialization of Data Quality Validation Service (Insights realm service)."""
        if self._data_quality_validation_service is None:
            try:
                # Import and initialize directly (Insights realm service)
                from backend.insights.services.data_quality_validation_service.data_quality_validation_service import DataQualityValidationService
                
                self._data_quality_validation_service = DataQualityValidationService(
                    service_name="DataQualityValidationService",
                    realm_name="insights",  # ✅ Insights realm service
                    platform_gateway=self.platform_gateway,
                    di_container=self.di_container
                )
                await self._data_quality_validation_service.initialize()
                self.logger.info("✅ Data Quality Validation Service initialized (Insights realm)")
                
            except Exception as e:
                self.logger.error(f"❌ Data Quality Validation Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._data_quality_validation_service
    
    async def _get_data_transformation_service(self):
        """Lazy initialization of Data Transformation Service (Insights realm service)."""
        if self._data_transformation_service is None:
            try:
                # Import and initialize directly (Insights realm service)
                from backend.insights.services.data_transformation_service.data_transformation_service import DataTransformationService
                
                self._data_transformation_service = DataTransformationService(
                    service_name="DataTransformationService",
                    realm_name="insights",  # ✅ Insights realm service
                    platform_gateway=self.platform_gateway,
                    di_container=self.di_container
                )
                await self._data_transformation_service.initialize()
                self.logger.info("✅ Data Transformation Service initialized (Insights realm)")
                
            except Exception as e:
                self.logger.error(f"❌ Data Transformation Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._data_transformation_service
    
    async def _get_data_mapping_workflow(self):
        """Lazy initialization of Data Mapping Workflow."""
        if self._data_mapping_workflow is None:
            try:
                from .workflows.data_mapping_workflow import DataMappingWorkflow
                
                self._data_mapping_workflow = DataMappingWorkflow(self)
                self.logger.info("✅ Data Mapping Workflow initialized")
                
            except Exception as e:
                self.logger.error(f"❌ Data Mapping Workflow initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._data_mapping_workflow
    
    async def _get_unstructured_analysis_workflow(self):
        """Lazy initialization of Unstructured Analysis Workflow."""
        if self._unstructured_analysis_workflow is None:
            try:
                from .workflows.unstructured_analysis_workflow import UnstructuredAnalysisWorkflow
                
                self._unstructured_analysis_workflow = UnstructuredAnalysisWorkflow(self)
                self.logger.info("✅ Unstructured Analysis Workflow initialized")
                
            except Exception as e:
                self.logger.error(f"❌ Unstructured Analysis Workflow initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._unstructured_analysis_workflow
    
    async def _get_structured_analysis_workflow(self):
        """Lazy initialization of Structured Analysis Workflow."""
        if self._structured_analysis_workflow is None:
            try:
                from .workflows.structured_analysis_workflow import StructuredAnalysisWorkflow
                
                self._structured_analysis_workflow = StructuredAnalysisWorkflow(self)
                self.logger.info("✅ Structured Analysis Workflow initialized")
                
            except Exception as e:
                self.logger.error(f"❌ Structured Analysis Workflow initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._structured_analysis_workflow
    
    async def initialize(self) -> bool:
        """
        Initialize Insights Journey Orchestrator.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self._realm_service.log_operation_with_telemetry(
            "insights_journey_orchestrator_initialize_start",
            success=True
        )
        
        # Call parent initialize (sets up RealmServiceBase)
        init_result = await super().initialize()
        if not init_result:
            self.logger.warning("⚠️ Base orchestrator initialization failed, continuing anyway...")
        
        try:
            self.logger.info("🚀 Initializing Insights Journey Orchestrator...")
            
            # Register with Curator for discovery
            await self._register_with_curator()
            
            self.logger.info("✅ Insights Journey Orchestrator initialized successfully")
            
            # Complete telemetry tracking
            await self._realm_service.log_operation_with_telemetry(
                "insights_journey_orchestrator_initialize_complete",
                success=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Insights Journey Orchestrator: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            
            await self._realm_service.log_operation_with_telemetry(
                "insights_journey_orchestrator_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            await self._realm_service.handle_error_with_audit(e, "initialize")
            return False
    
    async def _register_with_curator(self):
        """Register Insights Journey Orchestrator with Curator for discovery."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                service_metadata = {
                    "service_name": self.service_name,
                    "service_type": "insights_journey_orchestration",
                    "realm_name": self.realm_name,
                    "capabilities": ["data_mapping", "data_analysis", "quality_validation"],
                    "description": "Orchestrates insights workflows and composes Insights realm services"
                }
                await curator.register_service(self, service_metadata)
                self.logger.info("✅ Registered Insights Journey Orchestrator with Curator")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to register with Curator: {e}")
    
    async def execute_data_mapping_workflow(
        self,
        source_file_id: str,
        target_file_id: str,
        mapping_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute data mapping workflow with solution context integration and optional Saga guarantees.
        
        Delegates to Data Mapping Workflow which orchestrates:
        - Schema extraction
        - Semantic matching
        - Field extraction (for unstructured sources)
        - Data quality validation (for structured→structured)
        - Data transformation
        - Output generation
        
        Args:
            source_file_id: Source file identifier
            target_file_id: Target file identifier
            mapping_options: Optional mapping configuration
            user_context: Optional user context (includes workflow_id, session_id)
        
        Returns:
            Dict with mapping results, quality report, cleanup actions, and saga_id (if Saga was used)
        """
        # Prepare user context for Saga
        enhanced_user_context = user_context.copy() if user_context else {}
        enhanced_user_context.update({
            "source_file_id": source_file_id,
            "target_file_id": target_file_id
        })
        
        # Define milestones for data mapping operation
        milestones = ["analyze_source", "analyze_target", "generate_mapping", "apply_mapping", "validate"]
        
        # Execute with Saga if enabled
        return await self._execute_with_saga(
            operation="insights_data_mapping",
            workflow_func=lambda: self._execute_data_mapping_workflow_internal(
                source_file_id=source_file_id,
                target_file_id=target_file_id,
                mapping_options=mapping_options,
                user_context=enhanced_user_context
            ),
            milestones=milestones,
            user_context=enhanced_user_context
        )
    
    async def _execute_data_mapping_workflow_internal(
        self,
        source_file_id: str,
        target_file_id: str,
        mapping_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute data mapping workflow (called by Saga or directly).
        
        This is the actual workflow implementation, extracted for reuse.
        
        Args:
            source_file_id: Source file identifier
            target_file_id: Target file identifier
            mapping_options: Optional mapping configuration
            user_context: Optional user context
        
        Returns:
            Dict with mapping results, quality report, cleanup actions, etc.
        """
        try:
            # Get solution context from session if available
            enhanced_user_context = user_context.copy() if user_context else {}
            session_id = enhanced_user_context.get("session_id")
            
            if session_id:
                mvp_orchestrator = await self._get_mvp_journey_orchestrator()
                if mvp_orchestrator:
                    try:
                        solution_context = await mvp_orchestrator.get_solution_context(session_id)
                        if solution_context:
                            # Enhance user_context with solution context
                            enhanced_user_context["solution_context"] = solution_context
                            self.logger.info("✅ Solution context retrieved and added to user_context for data mapping")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to get solution context: {e}")
            
            # Enhance mapping_options with solution context if available
            enhanced_mapping_options = (mapping_options or {}).copy()
            if enhanced_user_context.get("solution_context"):
                solution_context = enhanced_user_context["solution_context"]
                enhanced_mapping_options["user_goals"] = solution_context.get("user_goals", "")
                solution_structure = solution_context.get("solution_structure", {})
                enhanced_mapping_options["strategic_focus"] = solution_structure.get("strategic_focus", "")
                enhanced_mapping_options["solution_context"] = solution_context
            
            # Get Data Mapping Workflow
            workflow = await self._get_data_mapping_workflow()
            if not workflow:
                return {
                    "success": False,
                    "error": "Data Mapping Workflow not available"
                }
            
            # Execute workflow with enhanced context
            result = await workflow.execute(
                source_file_id=source_file_id,
                target_file_id=target_file_id,
                mapping_options=enhanced_mapping_options,
                user_context=enhanced_user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Data mapping workflow execution failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "execute_data_mapping_workflow")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_analysis_workflow(
        self,
        file_id: str,
        analysis_type: str,
        analysis_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute analysis workflow with solution context integration.
        
        Delegates to appropriate workflow based on analysis_type:
        - "eda": EDA analysis (structured data)
        - "vark": VARK analysis (structured data)
        - "business_summary": Business summary (structured data)
        - "unstructured": Unstructured analysis (documents, text)
        
        Args:
            file_id: File identifier
            analysis_type: Type of analysis
            analysis_options: Optional analysis configuration
            user_context: Optional user context (includes workflow_id, session_id)
        
        Returns:
            Dict with analysis results
        """
        try:
            # Get solution context from session if available
            enhanced_user_context = user_context.copy() if user_context else {}
            session_id = enhanced_user_context.get("session_id")
            
            if session_id:
                mvp_orchestrator = await self._get_mvp_journey_orchestrator()
                if mvp_orchestrator:
                    try:
                        solution_context = await mvp_orchestrator.get_solution_context(session_id)
                        if solution_context:
                            # Enhance user_context with solution context
                            enhanced_user_context["solution_context"] = solution_context
                            self.logger.info("✅ Solution context retrieved and added to user_context")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to get solution context: {e}")
            
            # Enhance analysis_options with solution context if available
            enhanced_analysis_options = (analysis_options or {}).copy()
            if enhanced_user_context.get("solution_context"):
                solution_context = enhanced_user_context["solution_context"]
                enhanced_analysis_options["user_goals"] = solution_context.get("user_goals", "")
                solution_structure = solution_context.get("solution_structure", {})
                enhanced_analysis_options["strategic_focus"] = solution_structure.get("strategic_focus", "")
                enhanced_analysis_options["solution_context"] = solution_context
            
            # Determine which workflow to use
            if analysis_type == "unstructured":
                workflow = await self._get_unstructured_analysis_workflow()
                if not workflow:
                    return {
                        "success": False,
                        "error": "Unstructured Analysis Workflow not available"
                    }
                
                # Execute unstructured analysis workflow with enhanced context
                result = await workflow.execute(
                    source_type="file",
                    file_id=file_id,
                    analysis_options=enhanced_analysis_options,
                    user_context=enhanced_user_context
                )
                
            elif analysis_type in ["eda", "vark", "business_summary"]:
                workflow = await self._get_structured_analysis_workflow()
                if not workflow:
                    return {
                        "success": False,
                        "error": "Structured Analysis Workflow not available"
                    }
                
                # Execute structured analysis workflow with enhanced context
                # ✅ Extract content_id from analysis_options if provided (for EDA analysis)
                structured_options = {
                    **enhanced_analysis_options,
                    "analysis_type": analysis_type
                }
                # If content_id is in the request, pass it to the workflow
                if enhanced_analysis_options.get("content_id"):
                    structured_options["content_id"] = enhanced_analysis_options.get("content_id")
                
                result = await workflow.execute(
                    source_type="file",
                    file_id=file_id,
                    analysis_options=structured_options,
                    user_context=enhanced_user_context
                )
            else:
                return {
                    "success": False,
                    "error": f"Unknown analysis type: {analysis_type}"
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Analysis workflow execution failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "execute_analysis_workflow")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_visualization_workflow(
        self,
        content_id: str,
        visualization_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute visualization workflow.
        
        Delegates to Visualization Engine Service to generate visualizations.
        
        Args:
            content_id: Content metadata identifier
            visualization_options: Optional visualization configuration
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Dict with visualization results
        """
        try:
            # Get Visualization Engine Service
            visualization_service = await self._get_visualization_engine_service()
            if not visualization_service:
                return {
                    "success": False,
                    "error": "Visualization Engine Service not available"
                }
            
            # Get visualization options
            options = visualization_options or {}
            visualization_type = options.get("visualization_type", "chart")  # Default to chart
            visualization_spec = options.get("visualization_spec", {})
            
            # If no spec provided, create default spec based on content
            if not visualization_spec:
                # Try to infer from content metadata
                try:
                    # Get content metadata to understand data structure
                    librarian = await self.get_librarian_api()
                    if librarian:
                        content_metadata = await librarian.get_content_metadata(content_id, user_context)
                        if content_metadata and content_metadata.get("parsed_file_id"):
                            # Default to table visualization for structured data
                            visualization_type = "table"
                            visualization_spec = {
                                "columns": content_metadata.get("structure", {}).get("columns", []),
                                "sortable": True,
                                "filterable": True
                            }
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to infer visualization spec from content: {e}")
                    # Default to simple chart
                    visualization_type = "chart"
                    visualization_spec = {
                        "chart_type": "bar",
                        "title": "Data Visualization"
                    }
            
            # Call Visualization Engine Service to create visualization
            visualization_result = await visualization_service.create_agui_visualization(
                content_id=content_id,
                visualization_type=visualization_type,
                visualization_spec=visualization_spec,
                user_context=user_context
            )
            
            if not visualization_result.get("success"):
                return {
                    "success": False,
                    "error": visualization_result.get("error", "Visualization creation failed"),
                    "visualization_id": f"viz_{content_id}"
                }
            
            # Return visualization results
            return {
                "success": True,
                "visualization_id": f"viz_{content_id}_{int(datetime.utcnow().timestamp())}",
                "visualization_type": visualization_type,
                "visualization_data": visualization_result.get("component", {}),
                "agui_schema": visualization_result.get("agui_schema", {}),
                "content_id": content_id,
                "message": "Visualization created successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Visualization workflow execution failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "execute_visualization_workflow")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def query_insights_with_data_mash(
        self,
        insights_query: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query insights across all three data types (client, semantic, platform) using data mash.
        
        This method composes data from:
        - Client Data: Files, parsed data via ContentSteward
        - Semantic Data: Embeddings, metadata via semantic layer
        - Platform Data: Workflow, lineage, telemetry via DataSteward
        
        Phase 4 Implementation:
        - Queries insights based on workflow_ids, file_ids, content_ids
        - Composes client data by querying ContentSteward
        - Composes semantic data by querying semantic layer (embeddings)
        - Composes platform data by querying DataSteward (lineage, telemetry)
        - Correlates results using workflow_id and other correlation IDs
        
        Args:
            insights_query: Query specification (e.g., {
                "mapping_needed": True,
                "quality_issues": True,
                "workflow_ids": ["workflow_123"],
                "file_ids": ["file_456"],
                "content_ids": ["content_789"]
            })
            user_context: User context with correlation IDs (workflow_id, user_id, session_id, etc.)
        
        Returns:
            Dict with query results:
            {
                "success": True,
                "insights": {
                    "mappings": [...],
                    "analyses": [...],
                    "visualizations": [...]
                },
                "workflow_ids": [...],
                "file_ids": [...],
                "content_ids": [...]
            }
        """
        try:
            self.logger.info(f"📊 Querying insights with data mash: {insights_query}")
            
            results = {
                "success": True,
                "insights": {
                    "mappings": [],
                    "analyses": [],
                    "visualizations": []
                },
                "workflow_ids": [],
                "file_ids": [],
                "content_ids": []
            }
            
            # Extract query parameters
            workflow_ids = insights_query.get("workflow_ids", [])
            file_ids = insights_query.get("file_ids", [])
            content_ids = insights_query.get("content_ids", [])
            mapping_needed = insights_query.get("mapping_needed", False)
            quality_issues = insights_query.get("quality_issues", False)
            
            # Step 1: Compose Client Data (via ContentSteward)
            content_steward = await self.get_content_steward_api()
            client_data = []
            if content_steward and file_ids:
                try:
                    self.logger.info(f"📊 Composing client data for {len(file_ids)} files")
                    # Query file metadata for each file_id
                    for file_id in file_ids:
                        try:
                            file_info = await content_steward.get_file(file_id, user_context=user_context)
                            if file_info:
                                results["file_ids"].append(file_id)
                                
                                # Extract file details
                                metadata = file_info.get("metadata") or {}
                                file_data_entry = {
                                    "file_id": file_id,
                                    "ui_name": metadata.get("ui_name") or file_info.get("filename", ""),
                                    "file_type": metadata.get("file_type") or file_info.get("file_type", ""),
                                    "mime_type": metadata.get("mime_type") or file_info.get("mime_type", ""),
                                    "size_bytes": file_info.get("size_bytes", 0),
                                    "uploaded_at": metadata.get("uploaded_at") or file_info.get("uploaded_at"),
                                    "parsed": metadata.get("parsed", False),
                                    "parsed_file_id": metadata.get("parsed_file_id"),
                                    "copybook_file_id": metadata.get("copybook_file_id"),
                                    "metadata": metadata
                                }
                                
                                # If parsed, include parse result summary
                                if file_data_entry["parsed"] and metadata.get("parse_result"):
                                    parse_result = metadata.get("parse_result", {})
                                    file_data_entry["parse_summary"] = {
                                        "record_count": parse_result.get("record_count", 0),
                                        "schema_fields": len(parse_result.get("schema", {}).get("fields", [])),
                                        "parse_status": parse_result.get("status", "unknown")
                                    }
                                
                                client_data.append(file_data_entry)
                        except Exception as e:
                            self.logger.warning(f"⚠️ Failed to get file {file_id}: {e}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Client data composition failed: {e}")
            
            # Add client_data to results
            if client_data:
                results["client_data"] = client_data
            
            # Step 2: Compose Semantic Data (via semantic layer - Future)
            if content_ids:
                self.logger.info(f"📊 Composing semantic data for {len(content_ids)} content items")
                # Future: Query embeddings, metadata from semantic layer
                results["content_ids"].extend(content_ids)
            
            # Step 3: Compose Platform Data (via DataSteward - Future)
            if workflow_ids:
                self.logger.info(f"📊 Composing platform data for {len(workflow_ids)} workflows")
                # Future: Query lineage, telemetry from DataSteward
                results["workflow_ids"].extend(workflow_ids)
            
            # Step 4: Query Insights based on criteria
            # Query actual insights data from Librarian (where insights are stored)
            librarian = await self.get_librarian_api()
            if librarian:
                try:
                    # Query stored insights documents
                    # Insights are stored with metadata containing workflow_id, file_id, content_id
                    insights_query_filters = {}
                    if workflow_ids:
                        insights_query_filters["workflow_id"] = {"$in": workflow_ids}
                    if file_ids:
                        insights_query_filters["file_id"] = {"$in": file_ids}
                    if content_ids:
                        insights_query_filters["content_id"] = {"$in": content_ids}
                    
                    # Query for analysis results
                    if insights_query_filters or mapping_needed or quality_issues:
                        # Query stored analysis documents
                        analysis_documents = await librarian.query_documents(
                            filters={
                                "document_type": "insights_analysis",
                                **insights_query_filters
                            },
                            user_context=user_context
                        )
                        
                        if analysis_documents and isinstance(analysis_documents, list):
                            for doc in analysis_documents:
                                doc_data = doc.get("data", {}) if isinstance(doc, dict) else {}
                                doc_metadata = doc.get("metadata", {}) if isinstance(doc, dict) else {}
                                
                                # Add to analyses
                                results["insights"]["analyses"].append({
                                    "analysis_id": doc_metadata.get("analysis_id") or doc_data.get("analysis_id"),
                                    "workflow_id": doc_metadata.get("workflow_id"),
                                    "file_id": doc_metadata.get("file_id"),
                                    "content_id": doc_metadata.get("content_id"),
                                    "analysis_type": doc_metadata.get("analysis_type", "unknown"),
                                    "summary": doc_data.get("summary", {}),
                                    "insights": doc_data.get("insights", []),
                                    "timestamp": doc_metadata.get("timestamp")
                                })
                    
                    # Query for visualization results
                    if insights_query_filters:
                        visualization_documents = await librarian.query_documents(
                            filters={
                                "document_type": "insights_visualization",
                                **insights_query_filters
                            },
                            user_context=user_context
                        )
                        
                        if visualization_documents and isinstance(visualization_documents, list):
                            for doc in visualization_documents:
                                doc_data = doc.get("data", {}) if isinstance(doc, dict) else {}
                                doc_metadata = doc.get("metadata", {}) if isinstance(doc, dict) else {}
                                
                                # Add to visualizations
                                results["insights"]["visualizations"].append({
                                    "visualization_id": doc_metadata.get("visualization_id") or doc_data.get("visualization_id"),
                                    "workflow_id": doc_metadata.get("workflow_id"),
                                    "content_id": doc_metadata.get("content_id"),
                                    "visualization_type": doc_metadata.get("visualization_type", "unknown"),
                                    "component": doc_data.get("component", {}),
                                    "timestamp": doc_metadata.get("timestamp")
                                })
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to query insights from Librarian: {e}")
                    # Continue with other query logic
            
            if mapping_needed:
                self.logger.info("📊 Querying mappings with mapping_needed=True")
                # Check if any files in client_data need mapping
                files_needing_mapping = [
                    file_data for file_data in client_data
                    if file_data.get("parsed") and not file_data.get("metadata", {}).get("mapped", False)
                ]
                if files_needing_mapping:
                    results["insights"]["mappings"] = [
                        {
                            "file_id": file_data["file_id"],
                            "ui_name": file_data["ui_name"],
                            "file_type": file_data["file_type"],
                            "status": "mapping_needed",
                            "note": "File is parsed but not yet mapped"
                        }
                        for file_data in files_needing_mapping
                    ]
                else:
                    results["insights"]["mappings"].append({
                        "note": "No files found that need mapping. Mapping query results will be fully implemented when insights storage is available"
                    })
            
            if quality_issues:
                self.logger.info("📊 Querying analyses with quality_issues=True")
                # Check if any files have quality issues in parse_result
                files_with_quality_issues = []
                for file_data in client_data:
                    parse_result = file_data.get("metadata", {}).get("parse_result", {})
                    if parse_result.get("quality_issues"):
                        files_with_quality_issues.append({
                            "file_id": file_data["file_id"],
                            "ui_name": file_data["ui_name"],
                            "quality_issues": parse_result.get("quality_issues", [])
                        })
                
                if files_with_quality_issues:
                    results["insights"]["analyses"] = files_with_quality_issues
                else:
                    results["insights"]["analyses"].append({
                        "note": "No quality issues found in parsed files. Analysis query results will be fully implemented when insights storage is available"
                    })
            
            # Deduplicate lists
            results["workflow_ids"] = list(set(results["workflow_ids"]))
            results["file_ids"] = list(set(results["file_ids"]))
            results["content_ids"] = list(set(results["content_ids"]))
            
            self.logger.info(f"✅ Insights query completed: {len(results['workflow_ids'])} workflows, {len(results['file_ids'])} files, {len(results['content_ids'])} content items")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Insights query with data mash failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "query_insights_with_data_mash")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_visualization_engine_service(self):
        """Lazy initialization of Visualization Engine Service (Insights realm service)."""
        if self._visualization_engine_service is None:
            try:
                from backend.insights.services.visualization_engine_service.visualization_engine_service import VisualizationEngineService
                
                self._visualization_engine_service = VisualizationEngineService(
                    service_name="VisualizationEngineService",
                    realm_name="insights",
                    platform_gateway=self.platform_gateway,
                    di_container=self.di_container
                )
                await self._visualization_engine_service.initialize()
                self.logger.info("✅ Visualization Engine Service initialized (Insights realm)")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Visualization Engine Service initialization failed: {e}")
                return None
        
        return self._visualization_engine_service
    
    async def _get_data_analyzer_service(self):
        """Lazy initialization of Data Analyzer Service (Insights realm service)."""
        if self._data_analyzer_service is None:
            try:
                from backend.insights.services.data_analyzer_service.data_analyzer_service import DataAnalyzerService
                
                self._data_analyzer_service = DataAnalyzerService(
                    service_name="DataAnalyzerService",
                    realm_name="insights",
                    platform_gateway=self.platform_gateway,
                    di_container=self.di_container
                )
                await self._data_analyzer_service.initialize()
                self.logger.info("✅ Data Analyzer Service initialized (Insights realm)")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Data Analyzer Service initialization failed: {e}")
                return None
        
        return self._data_analyzer_service
    
    async def _get_apg_processor_service(self):
        """Lazy initialization of APG Processor Service (Business Enablement enabling service)."""
        if self._apg_processor_service is None:
            try:
                # Try via Curator first
                apg_processor = await self.get_enabling_service("APGProcessingService")
                if apg_processor:
                    self._apg_processor_service = apg_processor
                    return apg_processor
                
                # Fallback: Direct import
                from backend.business_enablement.enabling_services.apg_processor_service.apg_processor_service import APGProcessingService
                
                self._apg_processor_service = APGProcessingService(
                    service_name="APGProcessingService",
                    realm_name="business_enablement",
                    platform_gateway=self.platform_gateway,
                    di_container=self.di_container
                )
                await self._apg_processor_service.initialize()
                self.logger.info("✅ APG Processor Service initialized")
                
            except Exception as e:
                self.logger.warning(f"⚠️ APG Processor Service initialization failed: {e}")
                return None
        
        return self._apg_processor_service
    
    async def _get_insights_generator_service(self):
        """Lazy initialization of Insights Generator Service (Business Enablement enabling service)."""
        if self._insights_generator_service is None:
            try:
                # Try via Curator first
                insights_generator = await self.get_enabling_service("InsightsGeneratorService")
                if insights_generator:
                    self._insights_generator_service = insights_generator
                    return insights_generator
                
                # Fallback: Direct import
                from backend.business_enablement.enabling_services.insights_generator_service.insights_generator_service import InsightsGeneratorService
                
                self._insights_generator_service = InsightsGeneratorService(
                    service_name="InsightsGeneratorService",
                    realm_name="business_enablement",
                    platform_gateway=self.platform_gateway,
                    di_container=self.di_container
                )
                await self._insights_generator_service.initialize()
                self.logger.info("✅ Insights Generator Service initialized")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Insights Generator Service initialization failed: {e}")
                return None
        
        return self._insights_generator_service
    
    async def _get_metrics_calculator_service(self):
        """Lazy initialization of Metrics Calculator Service (Business Enablement enabling service)."""
        if self._metrics_calculator_service is None:
            try:
                # Try via Curator first
                metrics_calculator = await self.get_enabling_service("MetricsCalculatorService")
                if metrics_calculator:
                    self._metrics_calculator_service = metrics_calculator
                    return metrics_calculator
                
                # Fallback: Direct import
                from backend.business_enablement.enabling_services.metrics_calculator_service.metrics_calculator_service import MetricsCalculatorService
                
                self._metrics_calculator_service = MetricsCalculatorService(
                    service_name="MetricsCalculatorService",
                    realm_name="business_enablement",
                    platform_gateway=self.platform_gateway,
                    di_container=self.di_container
                )
                await self._metrics_calculator_service.initialize()
                self.logger.info("✅ Metrics Calculator Service initialized")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Metrics Calculator Service initialization failed: {e}")
                return None
        
        return self._metrics_calculator_service
    
    async def _get_insights_specialist_agent(self):
        """Lazy initialization of Insights Specialist Agent."""
        if self._insights_specialist_agent is None:
            try:
                # Try to get via Curator first
                curator = await self.get_foundation_service("CuratorFoundationService")
                if curator:
                    # Try to discover agent via Curator
                    agent = await curator.discover_service_by_name("InsightsSpecialistAgent")
                    if agent:
                        self._insights_specialist_agent = agent
                        self.logger.info("✅ Insights Specialist Agent discovered via Curator")
                        return agent
                
                # Fallback: Initialize using OrchestratorBase helper (via Agentic Foundation factory)
                self.logger.info("🔄 Insights Specialist Agent not found via Curator, initializing via factory")
                from backend.insights.agents.insights_specialist_agent import InsightsSpecialistAgent
                from backend.business_enablement.protocols.business_specialist_agent_protocol import SpecialistCapability
                
                agent = await self.initialize_agent(
                    InsightsSpecialistAgent,
                    "InsightsSpecialistAgent",
                    agent_type="specialist",
                    capabilities=[
                        "data_analysis",
                        "insights_generation",
                        "aar_analysis",
                        "pattern_extraction",
                        "quality_assessment"
                    ],
                    required_roles=[],
                    specialist_capability=SpecialistCapability.DATA_ANALYSIS
                )
                
                if agent:
                    self._insights_specialist_agent = agent
                    # Give specialist agent access to orchestrator (for MCP server access)
                    if hasattr(agent, 'set_orchestrator'):
                        agent.set_orchestrator(self)
                    self.logger.info("✅ Insights Specialist Agent initialized via factory")
                    return agent
                else:
                    self.logger.error("❌ Failed to initialize Insights Specialist Agent via factory")
                    return None
                
            except Exception as e:
                self.logger.error(f"❌ Insights Specialist Agent initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._insights_specialist_agent
    
    # Note: get_content_steward_api(), get_data_steward_api(), and get_librarian_api()
    # are already provided by OrchestratorBase (delegates to RealmServiceBase)
    # No need to override them - they're inherited from OrchestratorBase
    
    async def track_data_lineage(self, lineage_data: Dict[str, Any]):
        """Track data lineage via Data Steward."""
        try:
            data_steward = await self.get_data_steward_api()
            if data_steward:
                await data_steward.track_data_lineage(lineage_data)
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to track lineage: {e}")
    
    async def store_document(self, document_data: Dict[str, Any], metadata: Dict[str, Any]):
        """Store document via Librarian."""
        try:
            librarian = await self.get_librarian_api()
            if librarian:
                return await librarian.store_document(document_data, metadata)
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to store document: {e}")
            return {}
    
    async def _get_mvp_journey_orchestrator(self):
        """Get MVP Journey Orchestrator for solution context retrieval."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                mvp_orchestrator = await curator.discover_service_by_name("MVPJourneyOrchestratorService")
                if mvp_orchestrator:
                    # Verify it's from Journey realm
                    orchestrator_realm = getattr(mvp_orchestrator, 'realm_name', None)
                    if orchestrator_realm == "journey":
                        self.logger.info("✅ Discovered MVPJourneyOrchestratorService via Curator")
                        return mvp_orchestrator
                    else:
                        self.logger.warning(f"⚠️ Found MVPJourneyOrchestratorService but wrong realm: {orchestrator_realm} (expected 'journey')")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to get MVP Journey Orchestrator: {e}")
        return None
    
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
        saga_operations_str = config_adapter.get("SAGA_OPERATIONS", "insights_data_mapping")
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
            "insights_data_mapping": {
                "analyze_source": "revert_source_analysis",
                "analyze_target": "revert_target_analysis",
                "generate_mapping": "delete_mapping_rules",
                "apply_mapping": "revert_transformation",
                "validate": "mark_as_invalid"
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
            operation: Operation name (e.g., "insights_data_mapping")
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
    
    async def execute_data_quality_evaluation_workflow(
        self,
        file_id: str,
        parsed_file_id: Optional[str] = None,
        quality_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute holistic data quality evaluation workflow.
        
        This workflow:
        1. Retrieves parsed file and validation rules (88 codes, level-01 metadata)
        2. Applies validation rules to records
        3. Uses DataQualityValidationService for schema validation
        4. Uses DataAnalyzerService for quality metrics
        5. Uses DataQualityAgent for recommendations
        6. Returns comprehensive quality report
        
        Args:
            file_id: File identifier
            parsed_file_id: Optional parsed file identifier (if not provided, will look up)
            quality_options: Optional quality evaluation options
            user_context: Optional user context
        
        Returns:
        {
            "success": bool,
            "quality_report": {
                "overall_quality_score": float,
                "validation_results": [...],  # From validation rules
                "schema_validation": {...},  # From DataQualityValidationService
                "quality_metrics": {...},  # From DataAnalyzerService
                "recommendations": [...],  # From DataQualityAgent
                "summary": {
                    "total_records": int,
                    "valid_records": int,
                    "invalid_records": int,
                    "issues_by_type": {...},
                    "issues_by_severity": {...}
                }
            }
        }
        """
        try:
            self.logger.info(f"🔍 Starting holistic data quality evaluation: file_id={file_id}, parsed_file_id={parsed_file_id}")
            
            # Get Content Steward to retrieve parsed file
            content_steward = await self.get_content_steward_api()
            if not content_steward:
                return {
                    "success": False,
                    "error": "Content Steward service not available"
                }
            
            # Step 1: Retrieve parsed file and validation rules
            if not parsed_file_id:
                # Get parsed_file_id from file metadata
                file_info = await content_steward.get_file(file_id, user_context=user_context)
                if file_info and file_info.get("metadata"):
                    parsed_file_id = file_info.get("metadata", {}).get("parsed_file_id")
                    if not parsed_file_id:
                        # Try to get first parsed file for this file_id
                        parsed_files = await content_steward.list_parsed_files(file_id=file_id, user_context=user_context)
                        if parsed_files and isinstance(parsed_files, list) and len(parsed_files) > 0:
                            parsed_file_id = parsed_files[0].get("parsed_file_id")
            
            if not parsed_file_id:
                return {
                    "success": False,
                    "error": f"No parsed file found for file_id: {file_id}"
                }
            
            # Get parsed file data
            parsed_file_result = await content_steward.get_parsed_file(parsed_file_id, user_context=user_context)
            if not parsed_file_result:
                return {
                    "success": False,
                    "error": f"Parsed file not found: {parsed_file_id}"
                }
            
            # Extract validation rules and records
            parse_result = parsed_file_result.get("parse_result", {})
            validation_rules = parse_result.get("validation_rules", {})
            records = parsed_file_result.get("file_data", {}).get("records", [])
            
            if not records:
                return {
                    "success": False,
                    "error": "No records found in parsed file"
                }
            
            # Step 2: Apply validation rules (88 codes and level-01 metadata)
            validation_results = await self._apply_validation_rules(records, validation_rules)
            
            # Step 3: Schema validation using DataQualityValidationService
            schema_validation = None
            data_quality_service = await self._get_data_quality_validation_service()
            if data_quality_service and validation_rules:
                # Create target schema from validation rules
                target_schema = self._create_schema_from_validation_rules(validation_rules)
                if target_schema:
                    schema_validation = await data_quality_service.validate_records(
                        records=records,
                        target_schema=target_schema,
                        mapping_rules=[],  # No mapping needed - direct validation
                        user_context=user_context
                    )
            
            # Step 4: Quality metrics using DataAnalyzerService
            quality_metrics = None
            data_analyzer = await self._get_data_analyzer_service()
            if data_analyzer:
                try:
                    # Get quality metrics (missing values, data types, distributions, etc.)
                    quality_metrics = await self._calculate_quality_metrics(records, data_analyzer)
                except Exception as e:
                    self.logger.warning(f"⚠️ Quality metrics calculation failed: {e}")
            
            # Step 5: Generate recommendations using DataQualityAgent
            recommendations = []
            try:
                from backend.insights.agents.data_quality_agent import DataQualityAgent
                quality_agent = DataQualityAgent(self)
                
                quality_summary = {
                    "validation_results": validation_results,
                    "schema_validation": schema_validation,
                    "quality_metrics": quality_metrics
                }
                
                recommendations_result = await quality_agent.analyze_quality_issues(
                    quality_results=quality_summary,
                    source_file_id=file_id
                )
                
                if recommendations_result and recommendations_result.get("recommendations"):
                    recommendations = recommendations_result["recommendations"]
            except Exception as e:
                self.logger.warning(f"⚠️ Recommendations generation failed: {e}")
            
            # Step 6: Compile comprehensive quality report
            quality_report = self._compile_quality_report(
                validation_results=validation_results,
                schema_validation=schema_validation,
                quality_metrics=quality_metrics,
                recommendations=recommendations,
                total_records=len(records)
            )
            
            self.logger.info(f"✅ Data quality evaluation complete: overall_score={quality_report.get('overall_quality_score', 0):.2f}")
            
            return {
                "success": True,
                "file_id": file_id,
                "parsed_file_id": parsed_file_id,
                "quality_report": quality_report,
                "workflow_id": user_context.get("workflow_id") if user_context else None
            }
            
        except Exception as e:
            self.logger.error(f"❌ Data quality evaluation failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _apply_validation_rules(
        self,
        records: List[Dict[str, Any]],
        validation_rules: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply validation rules (88 codes and level-01 metadata) to records.
        
        Returns list of validation results per record.
        """
        validation_results = []
        
        if not validation_rules:
            # No validation rules - all records pass
            return [
                {
                    "record_index": idx,
                    "is_valid": True,
                    "issues": [],
                    "applied_rules": []
                }
                for idx in range(len(records))
            ]
        
        # Extract 88-level field rules
        rules_88 = validation_rules.get("88_level_fields", [])
        # Group by field_name
        rules_by_field = {}
        for rule in rules_88:
            field_name = rule.get("field_name")
            if field_name not in rules_by_field:
                rules_by_field[field_name] = []
            rules_by_field[field_name].append(rule)
        
        # Extract metadata record rules
        metadata_rules = validation_rules.get("metadata_records", [])
        # Group by target_field
        metadata_by_field = {}
        for rule in metadata_rules:
            target_field = rule.get("target_field")
            if target_field:
                if target_field not in metadata_by_field:
                    metadata_by_field[target_field] = []
                metadata_by_field[target_field].append(rule)
        
        # Validate each record
        for idx, record in enumerate(records):
            issues = []
            applied_rules = []
            
            # Apply 88-level field rules
            for field_name, rules in rules_by_field.items():
                if field_name in record:
                    value = record[field_name]
                    # Check if value matches any allowed value
                    allowed_values = [r.get("value") for r in rules]
                    if value not in allowed_values:
                        condition_names = [r.get("condition_name") for r in rules]
                        issues.append({
                            "field": field_name,
                            "issue_type": "invalid_value",
                            "severity": "error",
                            "message": f"Field '{field_name}' has invalid value '{value}'. Allowed values: {allowed_values}",
                            "value": value,
                            "allowed_values": allowed_values,
                            "rule_type": "88_level_field"
                        })
                    else:
                        applied_rules.append({
                            "field": field_name,
                            "rule_type": "88_level_field",
                            "value": value,
                            "matched_rule": next(r for r in rules if r.get("value") == value)
                        })
            
            # Apply metadata record rules
            for target_field, rules in metadata_by_field.items():
                if target_field in record:
                    value = record[target_field]
                    # Check if value matches any allowed value
                    allowed_values = [r.get("value").strip() for r in rules]
                    value_stripped = str(value).strip() if value else ""
                    if value_stripped not in allowed_values:
                        issues.append({
                            "field": target_field,
                            "issue_type": "invalid_value",
                            "severity": "error",
                            "message": f"Field '{target_field}' has invalid value '{value}'. Allowed values: {allowed_values}",
                            "value": value,
                            "allowed_values": allowed_values,
                            "rule_type": "metadata_record"
                        })
                    else:
                        applied_rules.append({
                            "field": target_field,
                            "rule_type": "metadata_record",
                            "value": value,
                            "matched_rule": next(r for r in rules if r.get("value").strip() == value_stripped)
                        })
            
            validation_results.append({
                "record_index": idx,
                "is_valid": len(issues) == 0,
                "issues": issues,
                "applied_rules": applied_rules
            })
        
        return validation_results
    
    def _create_schema_from_validation_rules(
        self,
        validation_rules: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create target schema from validation rules for DataQualityValidationService."""
        if not validation_rules:
            return None
        
        fields = []
        
        # Extract fields from 88-level rules
        rules_88 = validation_rules.get("88_level_fields", [])
        fields_by_name = {}
        for rule in rules_88:
            field_name = rule.get("field_name")
            if field_name not in fields_by_name:
                fields_by_name[field_name] = {
                    "field_name": field_name,
                    "field_type": "string",  # 88-level fields are typically strings
                    "required": True,
                    "allowed_values": []
                }
            fields_by_name[field_name]["allowed_values"].append(rule.get("value"))
        
        # Extract fields from metadata rules
        metadata_rules = validation_rules.get("metadata_records", [])
        for rule in metadata_rules:
            target_field = rule.get("target_field")
            if target_field and target_field not in fields_by_name:
                fields_by_name[target_field] = {
                    "field_name": target_field,
                    "field_type": "string",
                    "required": False,
                    "allowed_values": []
                }
            if target_field:
                fields_by_name[target_field]["allowed_values"].append(rule.get("value"))
        
        if not fields_by_name:
            return None
        
        return {
            "fields": list(fields_by_name.values())
        }
    
    async def _calculate_quality_metrics(
        self,
        records: List[Dict[str, Any]],
        data_analyzer: Any
    ) -> Dict[str, Any]:
        """Calculate quality metrics using DataAnalyzerService."""
        try:
            # Convert records to format expected by DataAnalyzerService
            # For now, return basic metrics
            if not records:
                return {}
            
            # Calculate basic quality metrics
            total_records = len(records)
            total_fields = len(records[0].keys()) if records else 0
            
            # Count missing values
            missing_by_field = {}
            for record in records:
                for field, value in record.items():
                    if not value or (isinstance(value, str) and value.strip() == ""):
                        missing_by_field[field] = missing_by_field.get(field, 0) + 1
            
            # Calculate completeness
            completeness_by_field = {
                field: 1.0 - (count / total_records) if total_records > 0 else 0.0
                for field, count in missing_by_field.items()
            }
            
            overall_completeness = sum(completeness_by_field.values()) / len(completeness_by_field) if completeness_by_field else 1.0
            
            return {
                "total_records": total_records,
                "total_fields": total_fields,
                "completeness": {
                    "overall": overall_completeness,
                    "by_field": completeness_by_field
                },
                "missing_values": {
                    "by_field": missing_by_field,
                    "total_missing": sum(missing_by_field.values())
                }
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Quality metrics calculation failed: {e}")
            return {}
    
    def _compile_quality_report(
        self,
        validation_results: List[Dict[str, Any]],
        schema_validation: Optional[Dict[str, Any]],
        quality_metrics: Optional[Dict[str, Any]],
        recommendations: List[Dict[str, Any]],
        total_records: int
    ) -> Dict[str, Any]:
        """Compile comprehensive quality report from all sources."""
        # Calculate overall quality score
        valid_count = sum(1 for r in validation_results if r.get("is_valid", False))
        validation_score = valid_count / total_records if total_records > 0 else 1.0
        
        schema_score = 1.0
        if schema_validation and schema_validation.get("summary"):
            schema_summary = schema_validation["summary"]
            schema_valid_count = schema_summary.get("valid_records", 0)
            schema_total = schema_summary.get("total_records", total_records)
            schema_score = schema_valid_count / schema_total if schema_total > 0 else 1.0
        
        completeness_score = 1.0
        if quality_metrics and quality_metrics.get("completeness"):
            completeness_score = quality_metrics["completeness"].get("overall", 1.0)
        
        # Weighted overall score
        overall_quality_score = (
            validation_score * 0.4 +  # 40% weight on validation rules
            schema_score * 0.3 +  # 30% weight on schema validation
            completeness_score * 0.3  # 30% weight on completeness
        )
        
        # Aggregate issues
        all_issues = []
        for result in validation_results:
            all_issues.extend(result.get("issues", []))
        
        if schema_validation and schema_validation.get("validation_results"):
            for schema_result in schema_validation["validation_results"]:
                all_issues.extend(schema_result.get("issues", []))
        
        # Group issues by type and severity
        issues_by_type = {}
        issues_by_severity = {"error": 0, "warning": 0, "info": 0}
        
        for issue in all_issues:
            issue_type = issue.get("issue_type", "unknown")
            severity = issue.get("severity", "info")
            
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = 0
            issues_by_type[issue_type] += 1
            
            issues_by_severity[severity] = issues_by_severity.get(severity, 0) + 1
        
        return {
            "overall_quality_score": overall_quality_score,
            "validation_results": validation_results,
            "schema_validation": schema_validation,
            "quality_metrics": quality_metrics,
            "recommendations": recommendations,
            "summary": {
                "total_records": total_records,
                "valid_records": valid_count,
                "invalid_records": total_records - valid_count,
                "issues_by_type": issues_by_type,
                "issues_by_severity": issues_by_severity,
                "total_issues": len(all_issues)
            }
        }
    
    async def orchestrate_summary(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Select the most appropriate and interesting output from available analyses.
        
        ⭐ Priority order (most actionable/interesting first):
        1. Data mappings - Most actionable, shows transformation logic
        2. AAR (After Action Review) - Comprehensive insights, narrative format
        3. Structured insights - Data-driven, charts/trends
        4. Unstructured insights - Narrative summaries, key findings
        
        Args:
            session_id: Session identifier
            user_context: Optional user context (includes user_id, tenant_id)
        
        Returns:
            Dict with success status, selected output type, and output content:
            {
                "success": True,
                "output_type": "data_mapping" | "aar" | "structured_insights" | "unstructured_insights",
                "output": {...},  # The selected output content
                "metadata": {
                    "session_id": "...",
                    "selected_at": "...",
                    "available_types": [...]
                }
            }
        """
        try:
            self.logger.info(f"📊 Orchestrating summary selection for session: {session_id}")
            
            # Get user_id from user_context
            user_id = (user_context or {}).get("user_id", "anonymous")
            
            # Query available outputs for this session
            available_outputs = {
                "data_mapping": None,
                "aar": None,
                "structured_insights": None,
                "unstructured_insights": None
            }
            
            # Try to get Librarian Service to query for stored analyses/mappings
            librarian = await self.get_librarian_api()
            if librarian:
                try:
                    # Query for content associated with this session
                    # This is a placeholder - actual implementation depends on Librarian API
                    if hasattr(librarian, 'query_content_by_session'):
                        content_result = await librarian.query_content_by_session(
                            session_id=session_id,
                            user_context=user_context
                        )
                        if content_result and isinstance(content_result, dict):
                            content_list = content_result.get("content", [])
                            
                            # Categorize content by type
                            for content in content_list:
                                content_type = content.get("content_type") or content.get("type", "")
                                metadata = content.get("metadata", {})
                                
                                # Check for data mapping
                                if "mapping" in content_type.lower() or metadata.get("mapping_rules"):
                                    if not available_outputs["data_mapping"]:
                                        available_outputs["data_mapping"] = content
                                
                                # Check for AAR
                                elif "aar" in content_type.lower() or "after_action" in content_type.lower():
                                    if not available_outputs["aar"]:
                                        available_outputs["aar"] = content
                                
                                # Check for structured insights
                                elif "structured" in content_type.lower() or metadata.get("analysis_type") in ["eda", "vark", "business_summary"]:
                                    if not available_outputs["structured_insights"]:
                                        available_outputs["structured_insights"] = content
                                
                                # Check for unstructured insights
                                elif "unstructured" in content_type.lower() or metadata.get("analysis_type") == "unstructured":
                                    if not available_outputs["unstructured_insights"]:
                                        available_outputs["unstructured_insights"] = content
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to query content from Librarian: {e}")
            
            # Try to get ContentSteward to query for file-based analyses
            content_steward = await self.get_content_steward_api()
            if content_steward:
                try:
                    # Query for files with analysis results
                    # This is a placeholder - actual implementation depends on ContentSteward API
                    if hasattr(content_steward, 'list_files_with_analyses'):
                        files_result = await content_steward.list_files_with_analyses(
                            session_id=session_id,
                            user_context=user_context
                        )
                        if files_result and isinstance(files_result, dict):
                            files = files_result.get("files", [])
                            
                            # Check each file for analysis results
                            for file_info in files:
                                metadata = file_info.get("metadata", {})
                                analysis_results = metadata.get("analysis_results", {})
                                
                                # Check for data mapping (look for mapping-related metadata)
                                if metadata.get("mapping_rules") or analysis_results.get("mapping"):
                                    if not available_outputs["data_mapping"]:
                                        available_outputs["data_mapping"] = {
                                            "type": "data_mapping",
                                            "file_id": file_info.get("file_id"),
                                            "mapping_rules": metadata.get("mapping_rules"),
                                            "analysis_results": analysis_results.get("mapping")
                                        }
                                
                                # Check for AAR
                                if analysis_results.get("aar") or metadata.get("aar_report"):
                                    if not available_outputs["aar"]:
                                        available_outputs["aar"] = {
                                            "type": "aar",
                                            "file_id": file_info.get("file_id"),
                                            "aar_report": analysis_results.get("aar") or metadata.get("aar_report")
                                        }
                                
                                # Check for structured insights
                                structured_analysis = analysis_results.get("structured") or analysis_results.get("eda") or analysis_results.get("vark")
                                if structured_analysis:
                                    if not available_outputs["structured_insights"]:
                                        available_outputs["structured_insights"] = {
                                            "type": "structured_insights",
                                            "file_id": file_info.get("file_id"),
                                            "analysis_results": structured_analysis
                                        }
                                
                                # Check for unstructured insights
                                unstructured_analysis = analysis_results.get("unstructured")
                                if unstructured_analysis:
                                    if not available_outputs["unstructured_insights"]:
                                        available_outputs["unstructured_insights"] = {
                                            "type": "unstructured_insights",
                                            "file_id": file_info.get("file_id"),
                                            "analysis_results": unstructured_analysis
                                        }
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to query files from ContentSteward: {e}")
            
            # Select the best output based on priority
            selected_output = None
            selected_type = None
            
            # Priority: data_mapping > aar > structured_insights > unstructured_insights
            if available_outputs["data_mapping"]:
                selected_output = available_outputs["data_mapping"]
                selected_type = "data_mapping"
            elif available_outputs["aar"]:
                selected_output = available_outputs["aar"]
                selected_type = "aar"
            elif available_outputs["structured_insights"]:
                selected_output = available_outputs["structured_insights"]
                selected_type = "structured_insights"
            elif available_outputs["unstructured_insights"]:
                selected_output = available_outputs["unstructured_insights"]
                selected_type = "unstructured_insights"
            
            # Build metadata
            available_types = [t for t, output in available_outputs.items() if output is not None]
            
            if selected_output:
                self.logger.info(f"✅ Selected {selected_type} as best output (available types: {available_types})")
                
                return {
                    "success": True,
                    "output_type": selected_type,
                    "output": selected_output,
                    "summary": selected_output,  # Alias for compatibility
                    "metadata": {
                        "session_id": session_id,
                        "selected_at": datetime.utcnow().isoformat(),
                        "available_types": available_types,
                        "priority_order": ["data_mapping", "aar", "structured_insights", "unstructured_insights"]
                    }
                }
            else:
                self.logger.warning(f"⚠️ No outputs available for session {session_id}")
                
                return {
                    "success": False,
                    "error": "No analysis outputs available for this session",
                    "output_type": None,
                    "output": None,
                    "summary": {},
                    "metadata": {
                        "session_id": session_id,
                        "selected_at": datetime.utcnow().isoformat(),
                        "available_types": [],
                        "priority_order": ["data_mapping", "aar", "structured_insights", "unstructured_insights"]
                    }
                }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to orchestrate summary: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "output_type": None,
                "output": None,
                "summary": {}
            }

