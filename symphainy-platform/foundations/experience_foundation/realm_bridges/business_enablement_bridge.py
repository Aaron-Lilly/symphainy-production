#!/usr/bin/env python3
"""
Business Enablement Realm Bridge - Business Enablement API Integration within Communication Foundation

Provides Business Enablement realm API endpoints through the unified Communication Foundation,
exposing all MVP pillar orchestrator endpoints for external consumption.

WHAT (Realm Bridge): I provide Business Enablement realm API endpoints through Communication Foundation
HOW (Bridge Implementation): I create Business Enablement FastAPI router and register with Communication Foundation
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from datetime import datetime

logger = logging.getLogger(__name__)


class BusinessEnablementRealmBridge:
    """
    Business Enablement Realm Bridge - Business Enablement API Integration within Communication Foundation
    
    Provides Business Enablement realm API endpoints through the unified Communication Foundation,
    consolidating all Business Enablement communication infrastructure in one place.
    
    WHAT (Realm Bridge): I provide Business Enablement realm API endpoints through Communication Foundation
    HOW (Bridge Implementation): I create Business Enablement FastAPI router and register with Communication Foundation
    """
    
    def __init__(self, di_container, public_works_foundation, curator_foundation):
        """Initialize Business Enablement Realm Bridge."""
        self.logger = logging.getLogger("BusinessEnablementRealmBridge")
        
        # Dependencies
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        self.curator_foundation = curator_foundation
        
        # Business Enablement services (will be initialized)
        self.delivery_manager = None
        
        # Router
        self.router = APIRouter(prefix="/api/v1/business_enablement", tags=["business_enablement"])
        
        self.logger.info("🏗️ Business Enablement Realm Bridge initialized")
    
    async def initialize(self):
        """Initialize Business Enablement Realm Bridge and create router."""
        try:
            self.logger.info("🚀 Initializing Business Enablement Realm Bridge...")
            
            # Initialize Business Enablement services
            await self._initialize_business_enablement_services()
            
            # Create Business Enablement API router
            await self._create_business_enablement_router()
            
            self.logger.info("✅ Business Enablement Realm Bridge initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Business Enablement Realm Bridge: {e}", exc_info=True)
            raise
    
    async def get_router(self, user_context: Dict[str, Any] = None) -> APIRouter:
        """Get the Business Enablement realm router."""
        try:
            # Note: Realm bridges don't have utility access yet
            # Security/tenant validation would be added when DI Container utilities are available
            return self.router
        except Exception as e:
            self.logger.error(f"❌ Failed to get router: {e}", exc_info=True)
            raise
    
    async def shutdown(self):
        """Shutdown Business Enablement Realm Bridge."""
        try:
            self.logger.info("🛑 Shutting down Business Enablement Realm Bridge...")
            # No cleanup needed for services (they're managed by DI Container)
            self.logger.info("✅ Business Enablement Realm Bridge shutdown completed")
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown Business Enablement Realm Bridge: {e}", exc_info=True)
            raise
    
    # PRIVATE METHODS
    
    async def _initialize_business_enablement_services(self):
        """Initialize Business Enablement services from DI Container."""
        self.logger.info("🔧 Initializing Business Enablement services...")
        
        try:
            # Get Delivery Manager from DI Container
            self.delivery_manager = self.di_container.service_registry.get("DeliveryManagerService")
            if self.delivery_manager:
                self.logger.info("✅ Delivery Manager service found")
                
                # Verify MVP pillar orchestrators are initialized
                if hasattr(self.delivery_manager, 'mvp_pillar_orchestrators'):
                    orchestrator_count = sum(1 for v in self.delivery_manager.mvp_pillar_orchestrators.values() if v is not None)
                    self.logger.info(f"✅ Delivery Manager has {orchestrator_count} MVP pillar orchestrators initialized")
                else:
                    self.logger.warning("⚠️ Delivery Manager missing mvp_pillar_orchestrators")
            else:
                self.logger.warning("⚠️ Delivery Manager not available")
            
            self.logger.info("✅ Business Enablement services initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Business Enablement services: {e}")
            raise
    
    async def _create_business_enablement_router(self):
        """Create Business Enablement realm FastAPI router with all endpoints."""
        self.logger.info("🔧 Creating Business Enablement realm router...")
        
        # Dependency injection functions
        def get_delivery_manager():
            """Get Delivery Manager Service instance."""
            if not self.delivery_manager:
                raise HTTPException(status_code=503, detail="Delivery Manager not available")
            return self.delivery_manager
        
        def get_content_orchestrator():
            """Get Content Analysis Orchestrator."""
            delivery_manager = get_delivery_manager()
            if not hasattr(delivery_manager, 'mvp_pillar_orchestrators'):
                raise HTTPException(status_code=503, detail="MVP pillar orchestrators not initialized")
            orchestrator = delivery_manager.mvp_pillar_orchestrators.get("content_analysis")
            if not orchestrator:
                raise HTTPException(status_code=503, detail="Content Analysis Orchestrator not available")
            return orchestrator
        
        def get_insights_orchestrator():
            """Get Insights Orchestrator."""
            delivery_manager = get_delivery_manager()
            if not hasattr(delivery_manager, 'mvp_pillar_orchestrators'):
                raise HTTPException(status_code=503, detail="MVP pillar orchestrators not initialized")
            orchestrator = delivery_manager.mvp_pillar_orchestrators.get("insights")
            if not orchestrator:
                raise HTTPException(status_code=503, detail="Insights Orchestrator not available")
            return orchestrator
        
        def get_operations_orchestrator():
            """Get Operations Orchestrator."""
            delivery_manager = get_delivery_manager()
            if not hasattr(delivery_manager, 'mvp_pillar_orchestrators'):
                raise HTTPException(status_code=503, detail="MVP pillar orchestrators not initialized")
            orchestrator = delivery_manager.mvp_pillar_orchestrators.get("operations")
            if not orchestrator:
                raise HTTPException(status_code=503, detail="Operations Orchestrator not available")
            return orchestrator
        
        def get_business_outcomes_orchestrator():
            """Get Business Outcomes Orchestrator."""
            delivery_manager = get_delivery_manager()
            if not hasattr(delivery_manager, 'mvp_pillar_orchestrators'):
                raise HTTPException(status_code=503, detail="MVP pillar orchestrators not initialized")
            orchestrator = delivery_manager.mvp_pillar_orchestrators.get("business_outcomes")
            if not orchestrator:
                raise HTTPException(status_code=503, detail="Business Outcomes Orchestrator not available")
            return orchestrator
        
        # ============================================================================
        # CONTENT ANALYSIS ENDPOINTS
        # ============================================================================
        
        @self.router.post("/content/upload-file")
        async def upload_file(
            file: UploadFile = File(...),
            user_id: str = "default_user",
            content_orchestrator = Depends(get_content_orchestrator)
        ) -> Dict[str, Any]:
            """Upload a file for content analysis."""
            try:
                # Read file content
                file_content = await file.read()
                
                result = await content_orchestrator.upload_file(
                    file_data=file_content,
                    filename=file.filename,
                    user_id=user_id
                )
                return result
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to upload file: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/content/list-uploaded-files")
        async def list_uploaded_files(
            user_id: str = "default_user",
            content_orchestrator = Depends(get_content_orchestrator)
        ) -> Dict[str, Any]:
            """List all uploaded files for a user."""
            try:
                result = await content_orchestrator.list_uploaded_files(user_id=user_id)
                return result
            except Exception as e:
                self.logger.error(f"Failed to list uploaded files: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/content/process-file/{file_id}")
        async def process_file(
            file_id: str,
            user_id: str = "default_user",
            content_orchestrator = Depends(get_content_orchestrator)
        ) -> Dict[str, Any]:
            """Process an uploaded file (parse and extract metadata)."""
            try:
                result = await content_orchestrator.process_file(
                    file_id=file_id,
                    user_id=user_id
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to process file: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/content/get-file-details/{file_id}")
        async def get_file_details(
            file_id: str,
            user_id: str = "default_user",
            content_orchestrator = Depends(get_content_orchestrator)
        ) -> Dict[str, Any]:
            """Get detailed information about a specific file."""
            try:
                result = await content_orchestrator.get_file_details(
                    file_id=file_id,
                    user_id=user_id
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to get file details: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/content/get-parsing-preview/{file_id}")
        async def get_parsing_preview(
            file_id: str,
            user_id: str = "default_user",
            content_orchestrator = Depends(get_content_orchestrator)
        ) -> Dict[str, Any]:
            """Get a preview of the parsed content."""
            try:
                result = await content_orchestrator.get_parsing_preview(
                    file_id=file_id,
                    user_id=user_id
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to get parsing preview: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/content/get-metadata-preview/{file_id}")
        async def get_metadata_preview(
            file_id: str,
            user_id: str = "default_user",
            content_orchestrator = Depends(get_content_orchestrator)
        ) -> Dict[str, Any]:
            """Get a preview of the extracted metadata."""
            try:
                result = await content_orchestrator.get_metadata_preview(
                    file_id=file_id,
                    user_id=user_id
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to get metadata preview: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # ============================================================================
        # INSIGHTS ENDPOINTS
        # ============================================================================
        
        @self.router.post("/insights/analyze-content-for-insights")
        async def analyze_content_for_insights(
            request_data: Dict[str, Any],
            insights_orchestrator = Depends(get_insights_orchestrator)
        ) -> Dict[str, Any]:
            """Analyze content for insights."""
            try:
                content_id = request_data.get("content_id")
                user_id = request_data.get("user_id", "default_user")
                
                result = await insights_orchestrator.analyze_content_for_insights(
                    content_id=content_id,
                    user_id=user_id
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to analyze content for insights: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/insights/get-analysis-results/{analysis_id}")
        async def get_analysis_results(
            analysis_id: str,
            user_id: str = "default_user",
            insights_orchestrator = Depends(get_insights_orchestrator)
        ) -> Dict[str, Any]:
            """Get analysis results for a specific analysis."""
            try:
                result = await insights_orchestrator.get_analysis_results(
                    analysis_id=analysis_id,
                    user_id=user_id
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to get analysis results: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/insights/get-visualizations/{analysis_id}")
        async def get_visualizations(
            analysis_id: str,
            user_id: str = "default_user",
            insights_orchestrator = Depends(get_insights_orchestrator)
        ) -> Dict[str, Any]:
            """Get visualizations for a specific analysis."""
            try:
                result = await insights_orchestrator.get_analysis_visualizations(
                    analysis_id=analysis_id,
                    user_id=user_id
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to get visualizations: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/insights/get-available-content-metadata")
        async def get_available_content_metadata(
            user_id: Optional[str] = None,
            insights_orchestrator = Depends(get_insights_orchestrator)
        ) -> Dict[str, Any]:
            """Get available content metadata for insights generation."""
            try:
                result = await insights_orchestrator.get_available_content_metadata(
                    user_id=user_id
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to get available content metadata: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # ============================================================================
        # OPERATIONS ENDPOINTS
        # ============================================================================
        
        @self.router.post("/operations/create-standard-operating-procedure")
        async def create_standard_operating_procedure(
            request_data: Dict[str, Any],
            operations_orchestrator = Depends(get_operations_orchestrator)
        ) -> Dict[str, Any]:
            """Create a Standard Operating Procedure (SOP) from workflow."""
            try:
                session_token = request_data.get("session_token")
                workflow_file_uuid = request_data.get("workflow_file_uuid")
                workflow_content = request_data.get("workflow_content")
                user_id = request_data.get("user_id", "default_user")
                
                result = await operations_orchestrator.generate_sop_from_workflow(
                    session_token=session_token,
                    workflow_file_uuid=workflow_file_uuid,
                    workflow_content=workflow_content,
                    user_id=user_id
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to create SOP: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/operations/create-workflow")
        async def create_workflow(
            request_data: Dict[str, Any],
            operations_orchestrator = Depends(get_operations_orchestrator)
        ) -> Dict[str, Any]:
            """Create a workflow from Standard Operating Procedure (SOP)."""
            try:
                session_token = request_data.get("session_token")
                sop_file_uuid = request_data.get("sop_file_uuid")
                sop_content = request_data.get("sop_content")
                user_id = request_data.get("user_id", "default_user")
                
                result = await operations_orchestrator.generate_workflow_from_sop(
                    session_token=session_token,
                    sop_file_uuid=sop_file_uuid,
                    sop_content=sop_content,
                    user_id=user_id
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to create workflow: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/operations/list-standard-operating-procedures")
        async def list_standard_operating_procedures(
            user_id: str = "default_user",
            operations_orchestrator = Depends(get_operations_orchestrator)
        ) -> Dict[str, Any]:
            """List all Standard Operating Procedures."""
            try:
                # This would need to be implemented in OperationsOrchestrator
                # For now, return placeholder
                return {
                    "success": True,
                    "sops": [],
                    "message": "List SOPs endpoint - to be implemented"
                }
            except Exception as e:
                self.logger.error(f"Failed to list SOPs: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/operations/list-workflows")
        async def list_workflows(
            user_id: str = "default_user",
            operations_orchestrator = Depends(get_operations_orchestrator)
        ) -> Dict[str, Any]:
            """List all workflows."""
            try:
                # This would need to be implemented in OperationsOrchestrator
                # For now, return placeholder
                return {
                    "success": True,
                    "workflows": [],
                    "message": "List workflows endpoint - to be implemented"
                }
            except Exception as e:
                self.logger.error(f"Failed to list workflows: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # ============================================================================
        # BUSINESS OUTCOMES ENDPOINTS
        # ============================================================================
        
        @self.router.post("/outcomes/generate-strategic-roadmap")
        async def generate_strategic_roadmap(
            request_data: Dict[str, Any],
            business_outcomes_orchestrator = Depends(get_business_outcomes_orchestrator)
        ) -> Dict[str, Any]:
            """Generate a strategic roadmap."""
            try:
                strategic_plan = request_data.get("strategic_plan", {})
                user_id = request_data.get("user_id", "default_user")
                
                result = await business_outcomes_orchestrator.generate_strategic_roadmap(
                    strategic_plan=strategic_plan,
                    user_id=user_id
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to generate strategic roadmap: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/outcomes/generate-proof-of-concept-proposal")
        async def generate_proof_of_concept_proposal(
            request_data: Dict[str, Any],
            business_outcomes_orchestrator = Depends(get_business_outcomes_orchestrator)
        ) -> Dict[str, Any]:
            """Generate a Proof of Concept (POC) proposal."""
            try:
                solution_id = request_data.get("solution_id")
                scope = request_data.get("scope", "basic")
                user_id = request_data.get("user_id", "default_user")
                
                result = await business_outcomes_orchestrator.generate_poc_proposal(
                    solution_id=solution_id,
                    scope=scope,
                    user_id=user_id
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to generate POC proposal: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/outcomes/get-pillar-summaries")
        async def get_pillar_summaries(
            user_id: str = "default_user",
            business_outcomes_orchestrator = Depends(get_business_outcomes_orchestrator)
        ) -> Dict[str, Any]:
            """Get summaries of all MVP pillars."""
            try:
                result = await business_outcomes_orchestrator.get_pillar_summaries(
                    user_id=user_id
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to get pillar summaries: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/outcomes/get-journey-visualization/{journey_id}")
        async def get_journey_visualization(
            journey_id: str,
            user_id: str = "default_user",
            business_outcomes_orchestrator = Depends(get_business_outcomes_orchestrator)
        ) -> Dict[str, Any]:
            """Get visualization of a specific user journey's progress and outcomes."""
            try:
                result = await business_outcomes_orchestrator.get_journey_visualization(
                    journey_id=journey_id,
                    user_id=user_id
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to get journey visualization: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        self.logger.info("✅ Business Enablement realm router created")

