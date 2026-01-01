#!/usr/bin/env python3
"""
Pillar API Handlers

Comprehensive API handlers for all business pillars following the working patterns
extracted from business_orchestrator_old.

WHAT (Experience Dimension Role): I provide real API handlers for all business pillars
HOW (Smart City Role): I use proven patterns from business_orchestrator_old
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from utilities import UserContext

# Import business enablement pillar services
from backend.business_enablement.pillars.content_pillar.content_pillar_service import content_pillar_service
from backend.business_enablement.pillars.insights_pillar.insights_pillar_service import insights_pillar_service
from backend.business_enablement.pillars.operations_pillar.operations_pillar_service import operations_pillar_service
from backend.business_enablement.pillars.business_outcomes_pillar.business_outcomes_pillar_service import business_outcomes_pillar_service

# Import business enablement interfaces
from backend.business_enablement.interfaces.content_management_interface import (
    UploadRequest, UploadResponse, ParseRequest, ParseResponse
)
from backend.business_enablement.interfaces.insights_analysis_interface import (
    AnalysisRequest, AnalysisResponse, VisualizationRequest, VisualizationResponse
)
from backend.business_enablement.interfaces.operations_management_interface import (
    SOPRequest, SOPResponse, WorkflowRequest, WorkflowResponse
)
# Business outcomes interface doesn't have request/response classes yet
# from backend.business_enablement.interfaces.business_outcomes_interface import (
#     StrategicPlanRequest, StrategicPlanResponse, ROIAnalysisRequest, ROIAnalysisResponse
# )


class PillarAPIHandlers:
    """
    Comprehensive API handlers for all business pillars.
    
    Provides real API handlers that call actual service methods following
    the working patterns from business_orchestrator_old.
    """
    
    def __init__(self, logger: logging.Logger):
        """Initialize the API handlers."""
        self.logger = logger
        self.security_service = None  # Will be implemented when needed
        
        # Initialize pillar services
        self.content_service = content_pillar_service
        self.insights_service = insights_pillar_service
        self.operations_service = operations_pillar_service
        self.business_outcomes_service = business_outcomes_pillar_service
        
        self.logger.info("🏗️ PillarAPIHandlers initialized with all pillar services")
    
    async def get_user_context(self, user_id: str = "api_user", session_id: Optional[str] = None) -> UserContext:
        """Get user context for API requests."""
        try:
            return UserContext(
                user_id=user_id,
                email=f"{user_id}@api.symphainy.com",
                full_name=f"API User {user_id}",
                session_id=session_id or f"api_session_{user_id}_{int(datetime.now().timestamp())}",
                permissions=["content:read", "content:write", "insights:read", "insights:analyze", 
                           "operations:read", "operations:write", "business_outcomes:read", "business_outcomes:write"]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to create user context: {str(e)}"
            )
    
    # ===== CONTENT PILLAR HANDLERS =====
    
    async def content_upload_handler(self, file_data: bytes, filename: str, 
                                   file_type: str, user_id: str = "api_user") -> JSONResponse:
        """Handle content pillar file upload requests."""
        try:
            # Get user context
            user_context = await self.get_user_context(user_id)
            
            # Convert string file_type to FileType enum
            from backend.business_enablement.interfaces.content_management_interface import FileType
            try:
                file_type_enum = FileType(file_type.lower()) if file_type else FileType.PDF
            except ValueError:
                # Default to PDF if file_type is not recognized
                file_type_enum = FileType.PDF
            
            # Create upload request
            upload_request = UploadRequest(
                file_data=file_data,
                filename=filename,
                file_type=file_type_enum,
                user_id=user_context.user_id,
                session_id=user_context.session_id
            )
            
            # Process upload
            result = await self.content_service.upload_file(upload_request)
            
            # Convert dataclass objects to dictionaries for JSON serialization
            file_metadata_dict = None
            if result.file_metadata:
                file_metadata_dict = {
                    "file_id": result.file_metadata.file_id,
                    "filename": result.file_metadata.filename,
                    "file_type": result.file_metadata.file_type.value if hasattr(result.file_metadata.file_type, 'value') else str(result.file_metadata.file_type),
                    "file_size": result.file_metadata.file_size,
                    "upload_timestamp": result.file_metadata.upload_timestamp.isoformat() if result.file_metadata.upload_timestamp else None,
                    "user_id": result.file_metadata.user_id,
                    "session_id": result.file_metadata.session_id,
                    "content_hash": result.file_metadata.content_hash,
                    "mime_type": result.file_metadata.mime_type,
                    "encoding": result.file_metadata.encoding,
                    "language": result.file_metadata.language,
                    "metadata": result.file_metadata.metadata,
                    "status": result.file_metadata.status,
                    "processing_status": result.file_metadata.processing_status.value if hasattr(result.file_metadata.processing_status, 'value') else str(result.file_metadata.processing_status)
                }
            
            processing_status_dict = None
            if result.processing_status:
                processing_status_dict = {
                    "status": result.processing_status.value if hasattr(result.processing_status, 'value') else str(result.processing_status),
                    "progress": getattr(result.processing_status, 'progress', None),
                    "message": getattr(result.processing_status, 'message', None)
                }
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": result.success,
                    "file_id": result.file_id,
                    "message": result.message,
                    "data": {
                        "file_metadata": file_metadata_dict,
                        "processing_status": processing_status_dict,
                        "error_details": result.error_details
                    }
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Content upload failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Content upload failed: {str(e)}"
            )
    
    async def content_parse_handler(self, file_id: str, parse_options: Dict[str, Any] = None,
                                  user_id: str = "api_user") -> JSONResponse:
        """Handle content pillar file parsing requests."""
        try:
            # Get user context
            user_context = await self.get_user_context(user_id)
            
            # Create parse request
            parse_request = ParseRequest(
                file_id=file_id,
                parse_options=parse_options or {},
                user_context=user_context
            )
            
            # Process parsing
            result = await self.content_service.parse_file(parse_request)
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "file_id": result.file_id,
                    "parsed_content": result.parsed_content,
                    "extracted_metadata": result.extracted_metadata,
                    "message": "File parsed successfully"
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Content parse failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Content parse failed: {str(e)}"
            )
    
    async def content_list_files_handler(self, user_id: str = "api_user") -> JSONResponse:
        """Handle content pillar file listing requests."""
        try:
            # Get user context
            user_context = await self.get_user_context(user_id)
            
            # Get files from content service
            files_result = await self.content_service.list_user_files(
                user_context.user_id, user_context
            )
            files = files_result.get("files", []) if files_result.get("success") else []
            
            # Convert FileMetadata objects to dictionaries for JSON serialization
            serialized_files = []
            for file_metadata in files:
                if hasattr(file_metadata, '__dict__'):
                    file_dict = file_metadata.__dict__.copy()
                    # Convert datetime objects to ISO strings
                    for key, value in file_dict.items():
                        if hasattr(value, 'isoformat'):
                            file_dict[key] = value.isoformat()
                        elif hasattr(value, 'value'):  # Handle enums
                            file_dict[key] = value.value
                    serialized_files.append(file_dict)
                else:
                    serialized_files.append(file_metadata)
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "files": serialized_files,
                    "message": "Files retrieved successfully"
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Content list files failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Content list files failed: {str(e)}"
            )
    
    # ===== INSIGHTS PILLAR HANDLERS =====
    
    async def insights_analyze_handler(self, dataset: Dict[str, Any], 
                                     analysis_type: str = "comprehensive",
                                     user_id: str = "api_user") -> JSONResponse:
        """Handle insights pillar analysis requests."""
        try:
            # Get user context
            user_context = await self.get_user_context(user_id)
            
            # Create analysis request
            analysis_request = AnalysisRequest(
                dataset=dataset,
                analysis_type=analysis_type,
                user_context=user_context
            )
            
            # Process analysis
            result = await self.insights_service.analyze_data(analysis_request)
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "analysis_results": result.analysis_results,
                    "insights": result.insights,
                    "message": "Analysis completed successfully"
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Insights analysis failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Insights analysis failed: {str(e)}"
            )
    
    async def insights_visualize_handler(self, dataset: Dict[str, Any],
                                       visualization_type: str = "auto",
                                       user_id: str = "api_user") -> JSONResponse:
        """Handle insights pillar visualization requests."""
        try:
            # Get user context
            user_context = await self.get_user_context(user_id)
            
            # Create visualization request
            visualization_request = VisualizationRequest(
                dataset=dataset,
                visualization_type=visualization_type,
                user_context=user_context
            )
            
            # Process visualization
            result = await self.insights_service.create_visualization(visualization_request)
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "visualization": result.visualization,
                    "chart_data": result.chart_data,
                    "message": "Visualization created successfully"
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Insights visualization failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Insights visualization failed: {str(e)}"
            )
    
    # ===== OPERATIONS PILLAR HANDLERS =====
    
    async def operations_sop_builder_handler(self, sop_data: Dict[str, Any],
                                           user_id: str = "api_user") -> JSONResponse:
        """Handle operations pillar SOP builder requests."""
        try:
            # Get user context
            user_context = await self.get_user_context(user_id)
            
            # Create SOP request
            sop_request = SOPRequest(
                sop_data=sop_data,
                user_context=user_context
            )
            
            # Process SOP creation
            result = await self.operations_service.create_sop(sop_request)
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "sop_id": result.sop_id,
                    "sop_content": result.sop_content,
                    "message": "SOP created successfully"
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Operations SOP builder failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Operations SOP builder failed: {str(e)}"
            )
    
    async def operations_workflow_builder_handler(self, workflow_data: Dict[str, Any],
                                                user_id: str = "api_user") -> JSONResponse:
        """Handle operations pillar workflow builder requests."""
        try:
            # Get user context
            user_context = await self.get_user_context(user_id)
            
            # Create workflow request
            workflow_request = WorkflowRequest(
                workflow_data=workflow_data,
                user_context=user_context
            )
            
            # Process workflow creation
            result = await self.operations_service.create_workflow(workflow_request)
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "workflow_id": result.workflow_id,
                    "workflow_content": result.workflow_content,
                    "message": "Workflow created successfully"
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Operations workflow builder failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Operations workflow builder failed: {str(e)}"
            )
    
    # ===== BUSINESS OUTCOMES PILLAR HANDLERS =====
    
    async def business_outcomes_strategic_planning_handler(self, plan_data: Dict[str, Any],
                                                         user_id: str = "api_user") -> JSONResponse:
        """Handle business outcomes pillar strategic planning requests."""
        try:
            # Get user context
            user_context = await self.get_user_context(user_id)
            
            # Process strategic planning using the service method directly
            result = await self.business_outcomes_service.generate_strategic_roadmap(
                business_context=plan_data,
                user_context=user_context
            )
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "plan_id": result.get("plan_id", "generated_plan"),
                    "strategic_plan": result,
                    "message": "Strategic plan created successfully"
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Business outcomes strategic planning failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Business outcomes strategic planning failed: {str(e)}"
            )
    
    async def business_outcomes_metrics_handler(self, user_id: str = "api_user") -> JSONResponse:
        """Handle business outcomes pillar metrics requests."""
        try:
            # Get user context
            user_context = await self.get_user_context(user_id)
            
            # Get metrics from business outcomes service
            metrics = await self.business_outcomes_service.get_metrics(user_context)
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "metrics": metrics,
                    "message": "Metrics retrieved successfully"
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Business outcomes metrics failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Business outcomes metrics failed: {str(e)}"
            )
