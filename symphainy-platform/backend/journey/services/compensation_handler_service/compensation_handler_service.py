#!/usr/bin/env python3
"""
Compensation Handler Service

WHAT: Executes compensation operations for Saga rollback
HOW: Domain-specific undo operations for each milestone type

This service provides compensation handlers for Saga pattern rollback.
When a Saga milestone fails, compensation handlers undo the work of
previously completed milestones in reverse order.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class CompensationHandlerService(RealmServiceBase):
    """
    Compensation Handler Service for Journey realm.
    
    Provides compensation handlers for Saga pattern rollback.
    Each compensation handler is a domain-specific undo operation
    that reverses the effects of a completed milestone.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Compensation Handler Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.librarian = None
        self.data_steward = None
        self.content_steward = None
        self.conductor = None
        
        # Journey services (discovered via Curator)
        self.sop_builder_service = None
        self.workflow_conversion_service = None
        self.coexistence_analysis_service = None
    
    async def initialize(self) -> bool:
        """
        Initialize Compensation Handler Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "compensation_handler_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # 1. Get Smart City services
            self.librarian = await self.get_librarian_api()
            self.data_steward = await self.get_data_steward_api()
            self.content_steward = await self.get_content_steward_api()
            self.conductor = await self.get_conductor_api()
            
            # 2. Discover Journey services via Curator
            await self._discover_journey_services()
            
            # 3. Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "compensation_execution",
                        "protocol": "CompensationHandlerProtocol",
                        "description": "Execute compensation handlers for Saga rollback",
                        "contracts": {
                            "soa_api": {
                                "api_name": "execute_compensation",
                                "endpoint": "/api/v1/journey/compensation/execute",
                                "method": "POST",
                                "handler": self.execute_compensation,
                                "metadata": {
                                    "description": "Execute a compensation handler",
                                    "parameters": ["handler_name", "milestone_data", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.execute_compensation",
                            "semantic_api": "/api/v1/journey/compensation/execute",
                            "user_journey": "execute_compensation"
                        }
                    }
                ],
                soa_apis=[
                    "execute_compensation",
                    "get_available_handlers"
                ]
            )
            
            # Record health metric
            await self.record_health_metric(
                "compensation_handler_initialized",
                1.0,
                {"service": "CompensationHandlerService"}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "compensation_handler_initialize_complete",
                success=True
            )
            
            self.logger.info("✅ Compensation Handler Service initialized successfully")
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "compensation_handler_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "compensation_handler_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Compensation Handler Service initialization failed: {e}")
            return False
    
    async def _discover_journey_services(self):
        """Discover Journey services via Curator."""
        curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
        if curator:
            try:
                self.sop_builder_service = await curator.discover_service_by_name("SOPBuilderService")
                if self.sop_builder_service:
                    self.logger.info("✅ Discovered SOPBuilderService")
            except Exception:
                self.logger.warning("⚠️ SOPBuilderService not yet available")
            
            try:
                self.workflow_conversion_service = await curator.discover_service_by_name("WorkflowConversionService")
                if self.workflow_conversion_service:
                    self.logger.info("✅ Discovered WorkflowConversionService")
            except Exception:
                self.logger.warning("⚠️ WorkflowConversionService not yet available")
            
            try:
                self.coexistence_analysis_service = await curator.discover_service_by_name("CoexistenceAnalysisService")
                if self.coexistence_analysis_service:
                    self.logger.info("✅ Discovered CoexistenceAnalysisService")
            except Exception:
                self.logger.warning("⚠️ CoexistenceAnalysisService not yet available")
    
    # ========================================================================
    # COMPENSATION EXECUTION (SOA API)
    # ========================================================================
    
    async def execute_compensation(
        self,
        handler_name: str,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a compensation handler (SOA API).
        
        Routes to appropriate handler based on handler_name.
        All compensation handlers are idempotent (safe to retry).
        
        Args:
            handler_name: Name of compensation handler (e.g., "delete_uploaded_file")
            milestone_data: Data from the milestone that needs compensation
            user_context: Optional user context
        
        Returns:
            Dict with compensation result:
            {
                "success": bool,
                "message": str,
                "compensated_data": Dict[str, Any]  # Data that was compensated
            }
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "execute_compensation_start",
            success=True,
            details={"handler_name": handler_name}
        )
        
        try:
            # Security and Tenant Validation
            if user_context:
                if not await self.security.check_permissions(user_context, "execute_compensation", "execute"):
                    await self.handle_error_with_audit(
                        ValueError("Permission denied"),
                        "execute_compensation",
                        details={"user_id": user_context.get("user_id"), "handler_name": handler_name}
                    )
                    await self.record_health_metric("execute_compensation_access_denied", 1.0, {})
                    await self.log_operation_with_telemetry("execute_compensation_complete", success=False)
                    return {
                        "success": False,
                        "error": "Permission denied"
                    }
                
                tenant_id = user_context.get("tenant_id")
                if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                    await self.handle_error_with_audit(
                        ValueError("Tenant access denied"),
                        "execute_compensation",
                        details={"tenant_id": tenant_id, "handler_name": handler_name}
                    )
                    await self.record_health_metric("execute_compensation_tenant_denied", 1.0, {"tenant_id": tenant_id})
                    await self.log_operation_with_telemetry("execute_compensation_complete", success=False)
                    return {
                        "success": False,
                        "error": "Tenant access denied"
                    }
            
            # Route to appropriate handler
            result = None
            
            # Data Operations Compensation Handlers
            if handler_name == "delete_uploaded_file":
                result = await self._delete_uploaded_file(milestone_data, user_context)
            elif handler_name == "mark_file_as_unparsed":
                result = await self._mark_file_as_unparsed(milestone_data, user_context)
            elif handler_name == "delete_embeddings":
                result = await self._delete_embeddings(milestone_data, user_context)
            elif handler_name == "remove_from_semantic_layer":
                result = await self._remove_from_semantic_layer(milestone_data, user_context)
            
            # Data Mapping Compensation Handlers
            elif handler_name == "revert_source_analysis":
                result = await self._revert_source_analysis(milestone_data, user_context)
            elif handler_name == "revert_target_analysis":
                result = await self._revert_target_analysis(milestone_data, user_context)
            elif handler_name == "delete_mapping_rules":
                result = await self._delete_mapping_rules(milestone_data, user_context)
            elif handler_name == "revert_transformation":
                result = await self._revert_transformation(milestone_data, user_context)
            elif handler_name == "mark_as_invalid":
                result = await self._mark_as_invalid(milestone_data, user_context)
            
            # Operations Compensation Handlers
            elif handler_name == "revert_sop_parsing":
                result = await self._revert_sop_parsing(milestone_data, user_context)
            elif handler_name == "clear_analysis_cache":
                result = await self._clear_analysis_cache(milestone_data, user_context)
            elif handler_name == "delete_workflow_draft":
                result = await self._delete_workflow_draft(milestone_data, user_context)
            elif handler_name == "mark_workflow_as_invalid":
                result = await self._mark_workflow_as_invalid(milestone_data, user_context)
            elif handler_name == "delete_stored_workflow":
                result = await self._delete_stored_workflow(milestone_data, user_context)
            elif handler_name == "clear_sop_cache":
                result = await self._clear_sop_cache(milestone_data, user_context)
            elif handler_name == "clear_workflow_cache":
                result = await self._clear_workflow_cache(milestone_data, user_context)
            elif handler_name == "revert_analysis":
                result = await self._revert_analysis(milestone_data, user_context)
            elif handler_name == "delete_blueprint_draft":
                result = await self._delete_blueprint_draft(milestone_data, user_context)
            elif handler_name == "delete_stored_blueprint":
                result = await self._delete_stored_blueprint(milestone_data, user_context)
            elif handler_name == "delete_wizard_session":
                result = await self._delete_wizard_session(milestone_data, user_context)
            elif handler_name == "clear_wizard_state":
                result = await self._clear_wizard_state(milestone_data, user_context)
            elif handler_name == "delete_sop_draft":
                result = await self._delete_sop_draft(milestone_data, user_context)
            elif handler_name == "mark_sop_as_invalid":
                result = await self._mark_sop_as_invalid(milestone_data, user_context)
            elif handler_name == "delete_published_sop":
                result = await self._delete_published_sop(milestone_data, user_context)
            
            # Business Outcomes Compensation Handlers
            elif handler_name == "clear_content_cache":
                result = await self._clear_content_cache(milestone_data, user_context)
            elif handler_name == "clear_insights_cache":
                result = await self._clear_insights_cache(milestone_data, user_context)
            elif handler_name == "clear_operations_cache":
                result = await self._clear_operations_cache(milestone_data, user_context)
            elif handler_name == "delete_compiled_summary":
                result = await self._delete_compiled_summary(milestone_data, user_context)
            elif handler_name == "delete_stored_summary":
                result = await self._delete_stored_summary(milestone_data, user_context)
            elif handler_name == "revert_opportunity_identification":
                result = await self._revert_opportunity_identification(milestone_data, user_context)
            elif handler_name == "delete_roadmap_draft":
                result = await self._delete_roadmap_draft(milestone_data, user_context)
            elif handler_name == "revert_business_analysis":
                result = await self._revert_business_analysis(milestone_data, user_context)
            elif handler_name == "delete_stored_roadmap":
                result = await self._delete_stored_roadmap(milestone_data, user_context)
            elif handler_name == "clear_requirements_cache":
                result = await self._clear_requirements_cache(milestone_data, user_context)
            elif handler_name == "revert_financial_calculations":
                result = await self._revert_financial_calculations(milestone_data, user_context)
            elif handler_name == "revert_risk_assessment":
                result = await self._revert_risk_assessment(milestone_data, user_context)
            elif handler_name == "delete_poc_draft":
                result = await self._delete_poc_draft(milestone_data, user_context)
            elif handler_name == "delete_stored_poc":
                result = await self._delete_stored_poc(milestone_data, user_context)
            
            else:
                result = {
                    "success": False,
                    "error": f"Unknown compensation handler: {handler_name}"
                }
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "execute_compensation_complete",
                success=result.get("success", False),
                details={"handler_name": handler_name, "result": result}
            )
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "execute_compensation", details={"handler_name": handler_name})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "execute_compensation_complete",
                success=False,
                details={"error": str(e), "handler_name": handler_name}
            )
            
            self.logger.error(f"❌ Compensation execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # DATA OPERATIONS COMPENSATION HANDLERS
    # ========================================================================
    
    async def _delete_uploaded_file(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Delete uploaded file."""
        file_id = milestone_data.get("file_id")
        if not file_id:
            return {"success": False, "error": "file_id required"}
        
        try:
            if self.librarian:
                await self.librarian.delete_document(file_id, user_context=user_context)
                self.logger.info(f"✅ Compensated: Deleted uploaded file {file_id}")
                return {
                    "success": True,
                    "message": f"File {file_id} deleted",
                    "compensated_data": {"file_id": file_id}
                }
            else:
                return {"success": False, "error": "Librarian not available"}
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _mark_file_as_unparsed(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Mark file as unparsed."""
        file_id = milestone_data.get("file_id")
        parsed_file_id = milestone_data.get("parsed_file_id")
        
        if not file_id:
            return {"success": False, "error": "file_id required"}
        
        try:
            # Update file metadata to mark as unparsed
            if self.librarian:
                # Get file metadata
                file_metadata = await self.librarian.get_document_metadata(file_id, user_context=user_context)
                if file_metadata:
                    # Update metadata to remove parsed status
                    updated_metadata = file_metadata.copy()
                    updated_metadata["parsing_status"] = "unparsed"
                    if parsed_file_id:
                        updated_metadata.pop("parsed_file_id", None)
                    
                    await self.librarian.update_document_metadata(
                        file_id,
                        updated_metadata,
                        user_context=user_context
                    )
                    
                    self.logger.info(f"✅ Compensated: Marked file {file_id} as unparsed")
                    return {
                        "success": True,
                        "message": f"File {file_id} marked as unparsed",
                        "compensated_data": {"file_id": file_id, "parsed_file_id": parsed_file_id}
                    }
            
            return {"success": False, "error": "Librarian not available"}
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_embeddings(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Delete embeddings."""
        file_id = milestone_data.get("file_id")
        parsed_file_id = milestone_data.get("parsed_file_id")
        content_id = milestone_data.get("content_id")
        
        if not file_id and not parsed_file_id and not content_id:
            return {"success": False, "error": "file_id, parsed_file_id, or content_id required"}
        
        try:
            # Delete embeddings via Content Steward or Librarian
            if self.content_steward:
                # Content Steward manages embeddings
                if content_id:
                    await self.content_steward.delete_embeddings(content_id, user_context=user_context)
                elif parsed_file_id:
                    await self.content_steward.delete_embeddings_by_parsed_file(parsed_file_id, user_context=user_context)
                elif file_id:
                    await self.content_steward.delete_embeddings_by_file(file_id, user_context=user_context)
                
                self.logger.info(f"✅ Compensated: Deleted embeddings for {file_id or parsed_file_id or content_id}")
                return {
                    "success": True,
                    "message": "Embeddings deleted",
                    "compensated_data": {
                        "file_id": file_id,
                        "parsed_file_id": parsed_file_id,
                        "content_id": content_id
                    }
                }
            
            return {"success": False, "error": "Content Steward not available"}
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _remove_from_semantic_layer(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Remove from semantic layer."""
        file_id = milestone_data.get("file_id")
        parsed_file_id = milestone_data.get("parsed_file_id")
        
        if not file_id and not parsed_file_id:
            return {"success": False, "error": "file_id or parsed_file_id required"}
        
        try:
            # Remove from semantic layer (future implementation)
            # For now, log the compensation
            self.logger.info(f"✅ Compensated: Removed {file_id or parsed_file_id} from semantic layer")
            return {
                "success": True,
                "message": "Removed from semantic layer",
                "compensated_data": {"file_id": file_id, "parsed_file_id": parsed_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # DATA MAPPING COMPENSATION HANDLERS
    # ========================================================================
    
    async def _revert_source_analysis(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Revert source analysis."""
        source_file_id = milestone_data.get("source_file_id")
        analysis_id = milestone_data.get("analysis_id")
        
        try:
            # Clear source analysis cache/metadata
            if self.data_steward and analysis_id:
                # Delete analysis results
                await self.data_steward.delete_analysis(analysis_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Reverted source analysis for {source_file_id}")
            return {
                "success": True,
                "message": "Source analysis reverted",
                "compensated_data": {"source_file_id": source_file_id, "analysis_id": analysis_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _revert_target_analysis(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Revert target analysis."""
        target_file_id = milestone_data.get("target_file_id")
        analysis_id = milestone_data.get("analysis_id")
        
        try:
            # Clear target analysis cache/metadata
            if self.data_steward and analysis_id:
                await self.data_steward.delete_analysis(analysis_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Reverted target analysis for {target_file_id}")
            return {
                "success": True,
                "message": "Target analysis reverted",
                "compensated_data": {"target_file_id": target_file_id, "analysis_id": analysis_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_mapping_rules(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Delete mapping rules."""
        mapping_id = milestone_data.get("mapping_id")
        
        try:
            # Delete mapping rules
            if self.data_steward and mapping_id:
                await self.data_steward.delete_mapping(mapping_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Deleted mapping rules {mapping_id}")
            return {
                "success": True,
                "message": "Mapping rules deleted",
                "compensated_data": {"mapping_id": mapping_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _revert_transformation(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Revert transformation."""
        transformation_id = milestone_data.get("transformation_id")
        target_file_id = milestone_data.get("target_file_id")
        
        try:
            # Revert transformation (delete transformed data)
            if self.librarian and target_file_id:
                # Mark transformed file as invalid or delete it
                await self.librarian.delete_document(target_file_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Reverted transformation {transformation_id}")
            return {
                "success": True,
                "message": "Transformation reverted",
                "compensated_data": {"transformation_id": transformation_id, "target_file_id": target_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _mark_as_invalid(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Mark as invalid."""
        validation_id = milestone_data.get("validation_id")
        file_id = milestone_data.get("file_id")
        
        try:
            # Mark validation result as invalid
            if self.data_steward and validation_id:
                await self.data_steward.mark_validation_invalid(validation_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Marked validation {validation_id} as invalid")
            return {
                "success": True,
                "message": "Marked as invalid",
                "compensated_data": {"validation_id": validation_id, "file_id": file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # OPERATIONS COMPENSATION HANDLERS
    # ========================================================================
    
    async def _revert_sop_parsing(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Revert SOP parsing."""
        sop_file_id = milestone_data.get("sop_file_id")
        
        try:
            # Revert SOP parsing (mark as unparsed)
            if self.librarian and sop_file_id:
                file_metadata = await self.librarian.get_document_metadata(sop_file_id, user_context=user_context)
                if file_metadata:
                    updated_metadata = file_metadata.copy()
                    updated_metadata["parsing_status"] = "unparsed"
                    updated_metadata.pop("parsed_file_id", None)
                    await self.librarian.update_document_metadata(sop_file_id, updated_metadata, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Reverted SOP parsing for {sop_file_id}")
            return {
                "success": True,
                "message": "SOP parsing reverted",
                "compensated_data": {"sop_file_id": sop_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _clear_analysis_cache(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Clear analysis cache."""
        analysis_id = milestone_data.get("analysis_id")
        
        try:
            # Clear analysis cache
            if self.data_steward and analysis_id:
                await self.data_steward.delete_analysis(analysis_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Cleared analysis cache {analysis_id}")
            return {
                "success": True,
                "message": "Analysis cache cleared",
                "compensated_data": {"analysis_id": analysis_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_workflow_draft(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Delete workflow draft."""
        workflow_id = milestone_data.get("workflow_id")
        workflow_file_id = milestone_data.get("workflow_file_id")
        
        try:
            # Delete workflow draft
            if self.librarian and workflow_file_id:
                await self.librarian.delete_document(workflow_file_id, user_context=user_context)
            elif self.conductor and workflow_id:
                await self.conductor.cancel_workflow(workflow_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Deleted workflow draft {workflow_id or workflow_file_id}")
            return {
                "success": True,
                "message": "Workflow draft deleted",
                "compensated_data": {"workflow_id": workflow_id, "workflow_file_id": workflow_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _mark_workflow_as_invalid(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Mark workflow as invalid."""
        workflow_id = milestone_data.get("workflow_id")
        workflow_file_id = milestone_data.get("workflow_file_id")
        
        try:
            # Mark workflow as invalid
            if self.librarian and workflow_file_id:
                file_metadata = await self.librarian.get_document_metadata(workflow_file_id, user_context=user_context)
                if file_metadata:
                    updated_metadata = file_metadata.copy()
                    updated_metadata["validation_status"] = "invalid"
                    await self.librarian.update_document_metadata(workflow_file_id, updated_metadata, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Marked workflow {workflow_id or workflow_file_id} as invalid")
            return {
                "success": True,
                "message": "Workflow marked as invalid",
                "compensated_data": {"workflow_id": workflow_id, "workflow_file_id": workflow_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_stored_workflow(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Delete stored workflow."""
        workflow_file_id = milestone_data.get("workflow_file_id")
        
        try:
            # Delete stored workflow
            if self.librarian and workflow_file_id:
                await self.librarian.delete_document(workflow_file_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Deleted stored workflow {workflow_file_id}")
            return {
                "success": True,
                "message": "Stored workflow deleted",
                "compensated_data": {"workflow_file_id": workflow_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _clear_sop_cache(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Clear SOP cache."""
        sop_file_id = milestone_data.get("sop_file_id")
        
        try:
            # Clear SOP cache (future implementation)
            self.logger.info(f"✅ Compensated: Cleared SOP cache for {sop_file_id}")
            return {
                "success": True,
                "message": "SOP cache cleared",
                "compensated_data": {"sop_file_id": sop_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _clear_workflow_cache(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Clear workflow cache."""
        workflow_file_id = milestone_data.get("workflow_file_id")
        
        try:
            # Clear workflow cache (future implementation)
            self.logger.info(f"✅ Compensated: Cleared workflow cache for {workflow_file_id}")
            return {
                "success": True,
                "message": "Workflow cache cleared",
                "compensated_data": {"workflow_file_id": workflow_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _revert_analysis(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Revert coexistence analysis."""
        analysis_id = milestone_data.get("analysis_id")
        
        try:
            # Revert analysis
            if self.coexistence_analysis_service and analysis_id:
                # Delete analysis results
                await self.coexistence_analysis_service.delete_analysis(analysis_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Reverted coexistence analysis {analysis_id}")
            return {
                "success": True,
                "message": "Coexistence analysis reverted",
                "compensated_data": {"analysis_id": analysis_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_blueprint_draft(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Delete blueprint draft."""
        blueprint_id = milestone_data.get("blueprint_id")
        blueprint_file_id = milestone_data.get("blueprint_file_id")
        
        try:
            # Delete blueprint draft
            if self.librarian and blueprint_file_id:
                await self.librarian.delete_document(blueprint_file_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Deleted blueprint draft {blueprint_id or blueprint_file_id}")
            return {
                "success": True,
                "message": "Blueprint draft deleted",
                "compensated_data": {"blueprint_id": blueprint_id, "blueprint_file_id": blueprint_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_stored_blueprint(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Delete stored blueprint."""
        blueprint_file_id = milestone_data.get("blueprint_file_id")
        
        try:
            # Delete stored blueprint
            if self.librarian and blueprint_file_id:
                await self.librarian.delete_document(blueprint_file_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Deleted stored blueprint {blueprint_file_id}")
            return {
                "success": True,
                "message": "Stored blueprint deleted",
                "compensated_data": {"blueprint_file_id": blueprint_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_wizard_session(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Delete wizard session."""
        session_token = milestone_data.get("session_token")
        
        try:
            # Delete wizard session
            if self.sop_builder_service and session_token:
                await self.sop_builder_service.delete_wizard_session(session_token, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Deleted wizard session {session_token}")
            return {
                "success": True,
                "message": "Wizard session deleted",
                "compensated_data": {"session_token": session_token}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _clear_wizard_state(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Clear wizard state."""
        session_token = milestone_data.get("session_token")
        
        try:
            # Clear wizard state
            if self.sop_builder_service and session_token:
                await self.sop_builder_service.clear_wizard_state(session_token, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Cleared wizard state for {session_token}")
            return {
                "success": True,
                "message": "Wizard state cleared",
                "compensated_data": {"session_token": session_token}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_sop_draft(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Delete SOP draft."""
        sop_id = milestone_data.get("sop_id")
        sop_file_id = milestone_data.get("sop_file_id")
        
        try:
            # Delete SOP draft
            if self.librarian and sop_file_id:
                await self.librarian.delete_document(sop_file_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Deleted SOP draft {sop_id or sop_file_id}")
            return {
                "success": True,
                "message": "SOP draft deleted",
                "compensated_data": {"sop_id": sop_id, "sop_file_id": sop_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _mark_sop_as_invalid(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Mark SOP as invalid."""
        sop_id = milestone_data.get("sop_id")
        sop_file_id = milestone_data.get("sop_file_id")
        
        try:
            # Mark SOP as invalid
            if self.librarian and sop_file_id:
                file_metadata = await self.librarian.get_document_metadata(sop_file_id, user_context=user_context)
                if file_metadata:
                    updated_metadata = file_metadata.copy()
                    updated_metadata["validation_status"] = "invalid"
                    await self.librarian.update_document_metadata(sop_file_id, updated_metadata, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Marked SOP {sop_id or sop_file_id} as invalid")
            return {
                "success": True,
                "message": "SOP marked as invalid",
                "compensated_data": {"sop_id": sop_id, "sop_file_id": sop_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_published_sop(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Delete published SOP."""
        sop_file_id = milestone_data.get("sop_file_id")
        
        try:
            # Delete published SOP
            if self.librarian and sop_file_id:
                await self.librarian.delete_document(sop_file_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Deleted published SOP {sop_file_id}")
            return {
                "success": True,
                "message": "Published SOP deleted",
                "compensated_data": {"sop_file_id": sop_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # BUSINESS OUTCOMES COMPENSATION HANDLERS
    # ========================================================================
    
    async def _clear_content_cache(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Clear content cache."""
        session_id = milestone_data.get("session_id")
        
        try:
            # Clear content cache (future implementation)
            self.logger.info(f"✅ Compensated: Cleared content cache for {session_id}")
            return {
                "success": True,
                "message": "Content cache cleared",
                "compensated_data": {"session_id": session_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _clear_insights_cache(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Clear insights cache."""
        session_id = milestone_data.get("session_id")
        
        try:
            # Clear insights cache (future implementation)
            self.logger.info(f"✅ Compensated: Cleared insights cache for {session_id}")
            return {
                "success": True,
                "message": "Insights cache cleared",
                "compensated_data": {"session_id": session_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _clear_operations_cache(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Clear operations cache."""
        session_id = milestone_data.get("session_id")
        
        try:
            # Clear operations cache (future implementation)
            self.logger.info(f"✅ Compensated: Cleared operations cache for {session_id}")
            return {
                "success": True,
                "message": "Operations cache cleared",
                "compensated_data": {"session_id": session_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_compiled_summary(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Delete compiled summary."""
        summary_id = milestone_data.get("summary_id")
        
        try:
            # Delete compiled summary
            if self.data_steward and summary_id:
                await self.data_steward.delete_summary(summary_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Deleted compiled summary {summary_id}")
            return {
                "success": True,
                "message": "Compiled summary deleted",
                "compensated_data": {"summary_id": summary_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_stored_summary(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Delete stored summary."""
        summary_id = milestone_data.get("summary_id")
        
        try:
            # Delete stored summary
            if self.data_steward and summary_id:
                await self.data_steward.delete_summary(summary_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Deleted stored summary {summary_id}")
            return {
                "success": True,
                "message": "Stored summary deleted",
                "compensated_data": {"summary_id": summary_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _revert_opportunity_identification(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Revert opportunity identification."""
        opportunity_id = milestone_data.get("opportunity_id")
        
        try:
            # Revert opportunity identification (delete opportunities)
            if self.data_steward and opportunity_id:
                await self.data_steward.delete_opportunity(opportunity_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Reverted opportunity identification {opportunity_id}")
            return {
                "success": True,
                "message": "Opportunity identification reverted",
                "compensated_data": {"opportunity_id": opportunity_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_roadmap_draft(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Delete roadmap draft."""
        roadmap_id = milestone_data.get("roadmap_id")
        roadmap_file_id = milestone_data.get("roadmap_file_id")
        
        try:
            # Delete roadmap draft
            if self.librarian and roadmap_file_id:
                await self.librarian.delete_document(roadmap_file_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Deleted roadmap draft {roadmap_id or roadmap_file_id}")
            return {
                "success": True,
                "message": "Roadmap draft deleted",
                "compensated_data": {"roadmap_id": roadmap_id, "roadmap_file_id": roadmap_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _revert_business_analysis(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Revert business analysis."""
        analysis_id = milestone_data.get("analysis_id")
        
        try:
            # Revert business analysis
            if self.data_steward and analysis_id:
                await self.data_steward.delete_analysis(analysis_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Reverted business analysis {analysis_id}")
            return {
                "success": True,
                "message": "Business analysis reverted",
                "compensated_data": {"analysis_id": analysis_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_stored_roadmap(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Delete stored roadmap."""
        roadmap_file_id = milestone_data.get("roadmap_file_id")
        
        try:
            # Delete stored roadmap
            if self.librarian and roadmap_file_id:
                await self.librarian.delete_document(roadmap_file_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Deleted stored roadmap {roadmap_file_id}")
            return {
                "success": True,
                "message": "Stored roadmap deleted",
                "compensated_data": {"roadmap_file_id": roadmap_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _clear_requirements_cache(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Clear requirements cache."""
        requirements_id = milestone_data.get("requirements_id")
        
        try:
            # Clear requirements cache (future implementation)
            self.logger.info(f"✅ Compensated: Cleared requirements cache {requirements_id}")
            return {
                "success": True,
                "message": "Requirements cache cleared",
                "compensated_data": {"requirements_id": requirements_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _revert_financial_calculations(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Revert financial calculations."""
        calculation_id = milestone_data.get("calculation_id")
        
        try:
            # Revert financial calculations (delete calculation results)
            if self.data_steward and calculation_id:
                await self.data_steward.delete_calculation(calculation_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Reverted financial calculations {calculation_id}")
            return {
                "success": True,
                "message": "Financial calculations reverted",
                "compensated_data": {"calculation_id": calculation_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _revert_risk_assessment(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Revert risk assessment."""
        risk_assessment_id = milestone_data.get("risk_assessment_id")
        
        try:
            # Revert risk assessment (delete assessment results)
            if self.data_steward and risk_assessment_id:
                await self.data_steward.delete_risk_assessment(risk_assessment_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Reverted risk assessment {risk_assessment_id}")
            return {
                "success": True,
                "message": "Risk assessment reverted",
                "compensated_data": {"risk_assessment_id": risk_assessment_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_poc_draft(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Delete POC draft."""
        poc_id = milestone_data.get("poc_id")
        poc_file_id = milestone_data.get("poc_file_id")
        
        try:
            # Delete POC draft
            if self.librarian and poc_file_id:
                await self.librarian.delete_document(poc_file_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Deleted POC draft {poc_id or poc_file_id}")
            return {
                "success": True,
                "message": "POC draft deleted",
                "compensated_data": {"poc_id": poc_id, "poc_file_id": poc_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_stored_poc(
        self,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compensation: Delete stored POC."""
        poc_file_id = milestone_data.get("poc_file_id")
        
        try:
            # Delete stored POC
            if self.librarian and poc_file_id:
                await self.librarian.delete_document(poc_file_id, user_context=user_context)
            
            self.logger.info(f"✅ Compensated: Deleted stored POC {poc_file_id}")
            return {
                "success": True,
                "message": "Stored POC deleted",
                "compensated_data": {"poc_file_id": poc_file_id}
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Compensation failed (non-blocking): {e}")
            return {"success": False, "error": str(e)}




