#!/usr/bin/env python3
"""
Insurance Migration Orchestrator for Insurance Use Case

WHAT: Orchestrates enabling services for insurance data migration
HOW: Delegates to CanonicalModelService, RoutingEngineService, FileParserService, etc.

This orchestrator provides insurance-specific migration capabilities while
delegating to first-class enabling services.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../../../'))

from bases.orchestrator_base import OrchestratorBase


class InsuranceMigrationOrchestrator(OrchestratorBase):
    """
    Insurance Migration Orchestrator for Insurance Use Case.
    
    Extends OrchestratorBase for Smart City access and orchestrator capabilities.
    Delegates to enabling services: CanonicalModelService, RoutingEngineService, etc.
    Integrates with Data Steward WAL for audit trail.
    """
    
    def __init__(self, delivery_manager):
        """
        Initialize Insurance Migration Orchestrator.
        
        Args:
            delivery_manager: Reference to DeliveryManagerService for service access
        """
        # Extract parameters from delivery_manager (which extends ManagerServiceBase)
        super().__init__(
            service_name="InsuranceMigrationOrchestratorService",
            realm_name=delivery_manager.realm_name,
            platform_gateway=delivery_manager.platform_gateway,
            di_container=delivery_manager.di_container,
            business_orchestrator=delivery_manager
        )
        self.delivery_manager = delivery_manager
        self.orchestrator_name = "InsuranceMigrationOrchestrator"
        
        # Enabling services (lazy initialization)
        self._canonical_model_service = None
        self._routing_engine_service = None
        self._file_parser_service = None
        self._schema_mapper_service = None
        self._data_steward = None  # For WAL integration
        
        # Specialist agents (lazy initialization)
        self._universal_mapper_agent = None
        self._quality_remediation_agent = None
        self._routing_decision_agent = None
        
        # MCP Server (initialized in initialize())
        self.mcp_server = None
    
    async def _get_canonical_model_service(self):
        """Lazy initialization of Canonical Model Service."""
        if self._canonical_model_service is None:
            try:
                # Tier 1: Try Enabling Service via Curator
                canonical_model = await self.get_enabling_service("CanonicalModelService")
                if canonical_model:
                    self._canonical_model_service = canonical_model
                    self.logger.info("✅ Canonical Model Service discovered via Curator")
                    return canonical_model
                
                # Tier 2: Fallback - Import and initialize directly
                self.logger.warning("⚠️ Canonical Model Service not found via Curator, initializing directly")
                from backend.business_enablement.enabling_services.canonical_model_service import CanonicalModelService
                
                self._canonical_model_service = CanonicalModelService(
                    service_name="CanonicalModelService",
                    realm_name="business_enablement",
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await self._canonical_model_service.initialize()
                self.logger.info("✅ Canonical Model Service initialized directly")
                
            except Exception as e:
                self.logger.error(f"❌ Canonical Model Service initialization failed: {e}")
                return None
        
        return self._canonical_model_service
    
    async def _get_routing_engine_service(self):
        """Lazy initialization of Routing Engine Service."""
        if self._routing_engine_service is None:
            try:
                # Tier 1: Try Enabling Service via Curator
                routing_engine = await self.get_enabling_service("RoutingEngineService")
                if routing_engine:
                    self._routing_engine_service = routing_engine
                    self.logger.info("✅ Routing Engine Service discovered via Curator")
                    return routing_engine
                
                # Tier 2: Fallback
                self.logger.warning("⚠️ Routing Engine Service not found via Curator, initializing directly")
                from backend.business_enablement.enabling_services.routing_engine_service import RoutingEngineService
                
                self._routing_engine_service = RoutingEngineService(
                    service_name="RoutingEngineService",
                    realm_name="business_enablement",
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await self._routing_engine_service.initialize()
                self.logger.info("✅ Routing Engine Service initialized directly")
                
            except Exception as e:
                self.logger.error(f"❌ Routing Engine Service initialization failed: {e}")
                return None
        
        return self._routing_engine_service
    
    async def _get_data_steward(self):
        """Lazy initialization of Data Steward (for WAL)."""
        if self._data_steward is None:
            try:
                self._data_steward = await self.get_data_steward_api()
                if self._data_steward:
                    self.logger.info("✅ Data Steward discovered for WAL integration")
            except Exception as e:
                self.logger.warning(f"⚠️ Data Steward not available: {e}")
        
        return self._data_steward
    
    async def _get_universal_mapper_agent(self):
        """Lazy initialization of Universal Mapper Specialist Agent."""
        if self._universal_mapper_agent is None:
            try:
                self._universal_mapper_agent = await self.get_agent("UniversalMapperSpecialist")
                if self._universal_mapper_agent:
                    self.logger.debug("✅ Universal Mapper Specialist Agent available")
            except Exception as e:
                self.logger.debug(f"Universal Mapper Specialist Agent not available: {e}")
        
        return self._universal_mapper_agent
    
    async def _get_quality_remediation_agent(self):
        """Lazy initialization of Quality Remediation Specialist Agent."""
        if self._quality_remediation_agent is None:
            try:
                self._quality_remediation_agent = await self.get_agent("QualityRemediationSpecialist")
                if self._quality_remediation_agent:
                    self.logger.debug("✅ Quality Remediation Specialist Agent available")
            except Exception as e:
                self.logger.debug(f"Quality Remediation Specialist Agent not available: {e}")
        
        return self._quality_remediation_agent
    
    async def _get_routing_decision_agent(self):
        """Lazy initialization of Routing Decision Specialist Agent."""
        if self._routing_decision_agent is None:
            try:
                self._routing_decision_agent = await self.get_agent("RoutingDecisionSpecialist")
                if self._routing_decision_agent:
                    self.logger.debug("✅ Routing Decision Specialist Agent available")
            except Exception as e:
                self.logger.debug(f"Routing Decision Specialist Agent not available: {e}")
        
        return self._routing_decision_agent
    
    async def _get_change_impact_agent(self):
        """Lazy initialization of Change Impact Assessment Specialist Agent."""
        if self._change_impact_agent is None:
            try:
                self._change_impact_agent = await self.get_agent("ChangeImpactAssessmentSpecialist")
                if self._change_impact_agent:
                    self.logger.debug("✅ Change Impact Assessment Specialist Agent available")
            except Exception as e:
                self.logger.debug(f"Change Impact Assessment Specialist Agent not available: {e}")
        
        return self._change_impact_agent
    
    # ============================================================================
    # INSURANCE MIGRATION OPERATIONS
    # ============================================================================
    
    async def ingest_legacy_data(
        self,
        file_id: Optional[str] = None,
        file_data: Optional[bytes] = None,
        filename: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest legacy insurance data with complete orchestration workflow.
        
        Complete orchestration:
        1. Upload/get file via Content Steward
        2. Parse file via File Parser Service
        3. Profile data via Data Steward
        4. Extract schema via Schema Mapper Service
        5. Store metadata via Librarian
        6. Track lineage via Data Steward
        7. Log all operations to WAL
        
        Compensation handler: delete_ingested_data
        """
        # Step 7: Write to WAL via Data Steward (BEFORE execution)
        data_steward = await self._get_data_steward()
        if data_steward:
            await data_steward.write_to_log(
                namespace="insurance_migration",
                payload={
                    "operation": "ingest_legacy_data",
                    "file_id": file_id,
                    "filename": filename
                },
                target="insurance_migration_queue",
                lifecycle={"retry_count": 3},
                user_context=user_context
            )
        
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "ingest_legacy_data_start",
            success=True,
            details={"file_id": file_id, "filename": filename}
        )
        
        try:
            # Step 1: Upload/get file via Content Steward
            content_steward = await self.get_content_steward_api()
            if not content_steward:
                return {
                    "success": False,
                    "error": "Content Steward not available"
                }
            
            if file_data and filename:
                # Upload new file
                upload_result = await content_steward.upload_file(
                    file_data=file_data,
                    filename=filename,
                    user_context=user_context
                )
                if not upload_result.get("success"):
                    return {
                        "success": False,
                        "error": f"File upload failed: {upload_result.get('error')}"
                    }
                file_id = upload_result.get("file_id")
                self.logger.info(f"✅ File uploaded: {file_id}")
            elif file_id:
                # Get existing file metadata
                file_metadata = await content_steward.get_file_metadata(
                    file_id=file_id,
                    user_context=user_context
                )
                if not file_metadata:
                    return {
                        "success": False,
                        "error": f"File not found: {file_id}"
                    }
                self.logger.info(f"✅ File found: {file_id}")
            else:
                return {
                    "success": False,
                    "error": "Either file_id or file_data+filename must be provided"
                }
            
            # Step 2: Parse file via File Parser Service
            file_parser = await self.get_enabling_service("FileParserService")
            if not file_parser:
                return {
                    "success": False,
                    "error": "File Parser Service not available"
                }
            
            parse_result = await file_parser.parse_file(
                file_id=file_id,
                user_context=user_context
            )
            
            if not parse_result.get("success"):
                return {
                    "success": False,
                    "error": parse_result.get("error", "File parsing failed")
                }
            
            parsed_data = parse_result.get("parsed_data", [])
            self.logger.info(f"✅ File parsed: {len(parsed_data)} records")
            
            # Step 3: Profile data via Data Steward (using available methods)
            if data_steward:
                try:
                    # Try to profile data (method may vary)
                    profile_result = await data_steward.analyze_data_quality(
                        data=parsed_data,
                        user_context=user_context
                    ) if hasattr(data_steward, 'analyze_data_quality') else None
                    quality_metrics = profile_result.get("metrics", {}) if profile_result else {}
                    self.logger.info(f"✅ Data profiled: Quality score = {quality_metrics.get('quality_score', 'N/A')}")
                    
                    # Get Quality Remediation Agent for quality intelligence
                    quality_agent = await self._get_quality_remediation_agent()
                    if quality_agent and quality_metrics:
                        try:
                            # Get AI-powered quality remediation recommendations
                            remediation_result = await quality_agent.recommend_remediation(
                                quality_metrics=quality_metrics,
                                policy_data=parsed_data[0] if parsed_data else None,
                                user_context=user_context
                            )
                            
                            if remediation_result.get("success"):
                                remediation_strategies = remediation_result.get("remediation_strategies", [])
                                if remediation_strategies:
                                    self.logger.info(f"✅ Quality remediation recommendations: {len(remediation_strategies)} strategies")
                                    # Store remediation recommendations in quality_metrics for downstream use
                                    quality_metrics["remediation_recommendations"] = remediation_strategies
                        except Exception as e:
                            self.logger.debug(f"Quality remediation recommendations not available: {e}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Data profiling not available: {e}")
                    quality_metrics = {}
            else:
                quality_metrics = {}
            
            # Step 4: Extract schema via Schema Mapper Service
            schema_mapper = await self.get_enabling_service("SchemaMapperService")
            if schema_mapper:
                schema_result = await schema_mapper.discover_schema(
                    schema_id=file_id,
                    data_sample=parsed_data[:10] if parsed_data else [],
                    user_context=user_context
                )
                source_schema = schema_result.get("schema", {}) if schema_result.get("success") else {}
                self.logger.info(f"✅ Schema extracted: {len(source_schema.get('fields', []))} fields")
            else:
                source_schema = {}
            
            # Step 5: Store metadata via Librarian
            librarian = await self.get_librarian_api()
            if librarian:
                metadata_doc = {
                    "file_id": file_id,
                    "filename": filename,
                    "schema": source_schema,
                    "quality_metrics": quality_metrics,
                    "record_count": len(parsed_data),
                    "ingested_at": datetime.utcnow().isoformat()
                }
                
                storage_result = await librarian.store_document(
                    document_data=metadata_doc,
                    metadata={
                        "type": "ingestion_metadata",
                        "file_id": file_id,
                        "ingested_at": datetime.utcnow().isoformat()
                    },
                    user_context=user_context
                )
                metadata_id = storage_result.get("document_id") if storage_result else None
                self.logger.info(f"✅ Metadata stored: {metadata_id}")
            else:
                metadata_id = None
            
            # Step 6: Track lineage via Data Steward
            if data_steward:
                await data_steward.track_lineage(
                    lineage_data={
                        "source": file_id,
                        "operation": "ingest_legacy_data",
                        "destination": metadata_id,
                        "metadata": {
                            "filename": filename,
                            "record_count": len(parsed_data),
                            "quality_score": quality_metrics.get("quality_score")
                        }
                    },
                    user_context=user_context
                )
                self.logger.info("✅ Lineage tracked")
            
            # Record health metric (success)
            await self.record_health_metric(
                "ingest_legacy_data_success",
                1.0,
                {
                    "file_id": file_id,
                    "record_count": len(parsed_data),
                    "quality_score": quality_metrics.get("quality_score", 0.0)
                }
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "ingest_legacy_data_complete",
                success=True,
                details={
                    "file_id": file_id,
                    "record_count": len(parsed_data),
                    "quality_score": quality_metrics.get("quality_score", 0.0)
                }
            )
            
            self.logger.info(f"✅ Legacy data ingestion complete: {file_id}")
            
            return {
                "success": True,
                "file_id": file_id,
                "parsed_data": parsed_data,
                "schema": source_schema,
                "quality_metrics": quality_metrics,
                "metadata_id": metadata_id,
                "file_ids": [file_id]  # For compensation handler
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "ingest_legacy_data")
            
            # Record health metric (failure)
            await self.record_health_metric(
                "ingest_legacy_data_failed",
                1.0,
                {"file_id": file_id, "error": str(e)}
            )
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "ingest_legacy_data_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Legacy data ingestion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_id": file_id
            }
    
    async def delete_ingested_data(
        self,
        saga_id: str,
        milestone_id: str,
        context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compensation handler: Delete ingested legacy data.
        
        Idempotent: Safe to call multiple times.
        """
        # Write to WAL before compensation
        data_steward = await self._get_data_steward()
        if data_steward:
            await data_steward.write_to_log(
                namespace="saga_compensation",
                payload={
                    "saga_id": saga_id,
                    "milestone_id": milestone_id,
                    "operation": "delete_ingested_data",
                    "context": context
                },
                target="compensation_queue",
                lifecycle={"retry_count": 5, "delay": 60, "backoff": "exponential"},
                user_context=user_context
            )
        
        try:
            # Get file IDs from context
            file_ids = context.get("file_ids", [])
            
            # Get Content Steward for file deletion
            content_steward = await self.get_content_steward_api()
            
            # Delete files (idempotent - safe to retry)
            deleted_files = []
            for file_id in file_ids:
                try:
                    # Check if file exists (idempotent check)
                    if content_steward:
                        file_metadata = await content_steward.get_file_metadata(file_id)
                        if file_metadata:
                            # Delete file (idempotent operation)
                            await content_steward.delete_file(file_id)
                            deleted_files.append(file_id)
                except Exception as e:
                    # Already deleted or doesn't exist (idempotent)
                    self.logger.warning(f"⚠️ File {file_id} already deleted or not found: {e}")
            
            return {
                "success": True,
                "deleted_files": deleted_files,
                "saga_id": saga_id,
                "milestone_id": milestone_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to delete ingested data: {e}")
            return {
                "success": False,
                "error": str(e),
                "saga_id": saga_id,
                "milestone_id": milestone_id
            }
    
    async def map_to_canonical(
        self,
        source_data: Dict[str, Any],
        source_schema_id: Optional[str] = None,
        mapping_rules: Optional[Dict[str, Any]] = None,
        canonical_model_name: str = "policy_v1",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Map source data to canonical model with complete orchestration workflow.
        
        Complete orchestration:
        1. Get source schema from Librarian (if not provided)
        2. Validate source data via Data Steward
        3. Map source → canonical via Schema Mapper Service
        4. Validate canonical data via Canonical Model Service
        5. Store mapping rules via Librarian
        6. Track mapping lineage
        7. Log all operations to WAL
        
        Compensation handler: revert_canonical_mapping
        """
        # Step 7: Write to WAL via Data Steward (BEFORE execution)
        data_steward = await self._get_data_steward()
        if data_steward:
            await data_steward.write_to_log(
                namespace="insurance_migration",
                payload={
                    "operation": "map_to_canonical",
                    "source_schema_id": source_schema_id,
                    "canonical_model": canonical_model_name
                },
                target="canonical_mapping_queue",
                lifecycle={"retry_count": 3},
                user_context=user_context
            )
        
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "map_to_canonical_start",
            success=True,
            details={"canonical_model": canonical_model_name}
        )
        
        try:
            # Step 1: Get source schema from Librarian (if not provided)
            librarian = await self.get_librarian_api()
            source_schema = None
            
            if source_schema_id and librarian:
                schema_doc = await librarian.retrieve_document(source_schema_id)
                if schema_doc:
                    source_schema = schema_doc.get("data") or schema_doc
                    self.logger.info(f"✅ Source schema retrieved: {source_schema_id}")
            
            if not source_schema:
                # Extract schema from source_data
                schema_mapper = await self.get_enabling_service("SchemaMapperService")
                if schema_mapper:
                    schema_result = await schema_mapper.discover_schema(
                        schema_id="extracted",
                        data_sample=[source_data],
                        user_context=user_context
                    )
                    if schema_result.get("success"):
                        source_schema = schema_result.get("schema", {})
                        self.logger.info("✅ Source schema extracted from data")
            
            # Step 2: Validate source data via Data Steward (using available methods)
            if data_steward and source_schema:
                try:
                    # Try to validate data (method may vary)
                    validation_result = await data_steward.validate_data(
                        data=source_data,
                        schema=source_schema,
                        user_context=user_context
                    ) if hasattr(data_steward, 'validate_data') else None
                    if validation_result and not validation_result.get("valid", True):
                        self.logger.warning(f"⚠️ Source data validation issues: {validation_result.get('errors', [])}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Data validation not available: {e}")
            
            # Step 3: Map source → canonical via Schema Mapper Service
            schema_mapper = await self.get_enabling_service("SchemaMapperService")
            if not schema_mapper:
                return {
                    "success": False,
                    "error": "Schema Mapper Service not available"
                }
            
            # Get Universal Mapper Agent for AI-assisted mapping suggestions
            universal_mapper = await self._get_universal_mapper_agent()
            ai_mapping_suggestions = None
            
            if universal_mapper and source_schema:
                try:
                    # Get AI-powered mapping suggestions
                    suggestions_result = await universal_mapper.suggest_mappings(
                        source_schema=source_schema,
                        target_schema_name=canonical_model_name,
                        user_context=user_context
                    )
                    
                    if suggestions_result.get("success"):
                        ai_mapping_suggestions = suggestions_result.get("suggested_mappings", [])
                        self.logger.info(f"✅ AI mapping suggestions: {len(ai_mapping_suggestions)} suggestions")
                except Exception as e:
                    self.logger.debug(f"AI mapping suggestions not available: {e}")
            
            # Perform mapping (with AI suggestions if available)
            # Perform mapping (deterministic service call)
            mapping_result = await schema_mapper.map_to_canonical(
                source_schema=source_schema or source_data,
                canonical_model_name=canonical_model_name,
                mapping_strategy="semantic_match",
                user_context=user_context
            )
            
            # Enhance mapping result with AI suggestions if available
            if ai_mapping_suggestions and mapping_result.get("success"):
                # Add AI suggestions to mapping result for downstream use
                mapping_result["ai_suggestions"] = ai_mapping_suggestions
                mapping_result["enhanced_with_ai"] = True
            
            if not mapping_result.get("success"):
                return {
                    "success": False,
                    "error": mapping_result.get("error", "Mapping failed")
                }
            
            mapping_id = mapping_result.get("mapping_id")
            field_mappings = mapping_result.get("field_mappings", [])
            self.logger.info(f"✅ Mapping created: {mapping_id} ({len(field_mappings)} fields)")
            
            # Learn from mapping (if Universal Mapper Agent is available)
            if universal_mapper and mapping_result.get("mapping_rules"):
                try:
                    await universal_mapper.learn_from_mappings(
                        source_schema=source_schema,
                        target_schema_name=canonical_model_name,
                        mapping_rules=mapping_result.get("mapping_rules", {}),
                        user_context=user_context
                    )
                    self.logger.debug("✅ Mapping patterns learned by Universal Mapper Agent")
                except Exception as e:
                    self.logger.debug(f"Learning from mapping not available: {e}")
            
            # Step 4: Transform source data to canonical format via Canonical Model Service
            canonical_model = await self._get_canonical_model_service()
            canonical_data = None
            canonical_validation = {"success": True, "validated": False}
            
            if canonical_model:
                # Transform source data to canonical format using field mappings
                # Build mapping rules from field_mappings for canonical transformation
                transformation_mapping_rules = {}
                for mapping in field_mappings:
                    source_field = mapping.get("source_field")
                    target_field = mapping.get("target_field")
                    if source_field and target_field:
                        transformation_mapping_rules[source_field] = target_field
                
                # Call Canonical Model Service to transform data
                transformation_result = await canonical_model.map_to_canonical(
                    source_data=source_data,
                    model_name=canonical_model_name,
                    mapping_rules=transformation_mapping_rules if transformation_mapping_rules else mapping_rules,
                    user_context=user_context
                )
                
                if transformation_result.get("success"):
                    canonical_data = transformation_result.get("canonical_data", {})
                    self.logger.info("✅ Source data transformed to canonical format")
                else:
                    self.logger.warning(f"⚠️ Canonical transformation failed: {transformation_result.get('error')}")
                    # Fallback: use source_data structure (graceful degradation)
                    canonical_data = source_data
                
                # Validate transformed canonical data
                canonical_validation = await canonical_model.validate_against_canonical(
                    data=canonical_data,
                    model_name=canonical_model_name,
                    version="1.0.0",
                    user_context=user_context
                )
                
                if canonical_validation.get("success") and canonical_validation.get("valid"):
                    self.logger.info("✅ Canonical data validated")
                else:
                    validation_errors = canonical_validation.get("errors", [])
                    self.logger.warning(f"⚠️ Canonical validation issues: {validation_errors}")
            else:
                self.logger.warning("⚠️ Canonical Model Service not available - using source_data as fallback")
                canonical_data = source_data
            
            # Step 5: Store mapping rules via Librarian
            if librarian:
                mapping_rules_doc = {
                    "mapping_id": mapping_id,
                    "source_schema": source_schema,
                    "canonical_model": canonical_model_name,
                    "field_mappings": field_mappings,
                    "mapping_rules": mapping_rules,
                    "confidence_score": mapping_result.get("confidence_score", 0.0),
                    "created_at": datetime.utcnow().isoformat()
                }
                
                storage_result = await librarian.store_document(
                    document_data=mapping_rules_doc,
                    metadata={
                        "type": "canonical_mapping_rule",
                        "mapping_id": mapping_id,
                        "canonical_model": canonical_model_name,
                        "created_at": datetime.utcnow().isoformat()
                    },
                    user_context=user_context
                )
                mapping_rules_id = storage_result.get("document_id") if storage_result else mapping_id
                self.logger.info(f"✅ Mapping rules stored: {mapping_rules_id}")
            else:
                mapping_rules_id = mapping_id
            
            # Step 6: Track mapping lineage
            if data_steward:
                await data_steward.track_lineage(
                    lineage_data={
                        "source": source_schema_id or "extracted",
                        "operation": "map_to_canonical",
                        "destination": mapping_rules_id,
                        "metadata": {
                            "canonical_model": canonical_model_name,
                            "mapping_id": mapping_id,
                            "confidence_score": mapping_result.get("confidence_score", 0.0)
                        }
                    },
                    user_context=user_context
                )
                self.logger.info("✅ Mapping lineage tracked")
            
            # Record health metric (success)
            await self.record_health_metric(
                "map_to_canonical_success",
                1.0,
                {
                    "mapping_id": mapping_id,
                    "canonical_model": canonical_model_name,
                    "confidence_score": mapping_result.get("confidence_score", 0.0)
                }
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "map_to_canonical_complete",
                success=True,
                details={
                    "mapping_id": mapping_id,
                    "canonical_model": canonical_model_name,
                    "confidence_score": mapping_result.get("confidence_score", 0.0)
                }
            )
            
            self.logger.info(f"✅ Canonical mapping complete: {mapping_id}")
            
            return {
                "success": True,
                "mapping_id": mapping_id,
                "mapping_rules_id": mapping_rules_id,
                "canonical_data": canonical_data if canonical_data else source_data,
                "field_mappings": field_mappings,
                "confidence_score": mapping_result.get("confidence_score", 0.0),
                "validation": canonical_validation
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "map_to_canonical")
            
            # Record health metric (failure)
            await self.record_health_metric(
                "map_to_canonical_failed",
                1.0,
                {"canonical_model": canonical_model_name, "error": str(e)}
            )
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "map_to_canonical_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Canonical mapping failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def route_policies(
        self,
        policy_data: Dict[str, Any],
        namespace: str = "default",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route policies to target systems with complete orchestration workflow.
        
        Complete orchestration:
        1. Get policy status from Policy Tracker
        2. Extract routing key via Routing Engine Service
        3. Evaluate routing rules via Routing Engine Service
        4. Update Policy Tracker with routing decision
        5. Store routing decision in Librarian
        6. Track routing lineage
        7. Log all operations to WAL
        
        Compensation handler: revert_routing
        """
        policy_id = policy_data.get("policy_id")
        
        # Step 7: Write to WAL via Data Steward (BEFORE execution)
        data_steward = await self._get_data_steward()
        if data_steward:
            await data_steward.write_to_log(
                namespace="insurance_migration",
                payload={
                    "operation": "route_policies",
                    "policy_id": policy_id,
                    "namespace": namespace
                },
                target="routing_evaluation_queue",
                lifecycle={"retry_count": 3},
                user_context=user_context
            )
        
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "route_policies_start",
            success=True,
            details={"policy_id": policy_id, "namespace": namespace}
        )
        
        try:
            # Step 1: Get policy status from Policy Tracker
            policy_tracker = None
            try:
                orchestrators = self.delivery_manager.get_orchestrators()
                for orchestrator in orchestrators:
                    if hasattr(orchestrator, 'orchestrator_name') and orchestrator.orchestrator_name == "PolicyTrackerOrchestrator":
                        policy_tracker = orchestrator
                        break
            except Exception as e:
                self.logger.warning(f"⚠️ Policy Tracker not available: {e}")
            
            policy_status = None
            if policy_tracker and policy_id:
                try:
                    location_result = await policy_tracker.get_policy_location(
                        policy_id=policy_id,
                        user_context=user_context
                    )
                    if location_result.get("success"):
                        policy_status = location_result.get("status")
                        self.logger.info(f"✅ Policy status retrieved: {policy_status}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not get policy status: {e}")
            
            # Step 2: Extract routing key via Routing Engine Service
            routing_engine = await self._get_routing_engine_service()
            if not routing_engine:
                return {
                    "success": False,
                    "error": "Routing Engine Service not available"
                }
            
            routing_key_result = await routing_engine.get_routing_key(
                policy_data=policy_data,
                namespace=namespace,
                user_context=user_context
            )
            
            routing_key = routing_key_result.get("routing_key") if routing_key_result.get("success") else policy_data.get("policy_id")
            self.logger.info(f"✅ Routing key extracted: {routing_key}")
            
            # Step 3: Evaluate routing rules via Routing Engine Service (deterministic)
            routing_result = await routing_engine.evaluate_routing(
                policy_data=policy_data,
                namespace=namespace,
                user_context=user_context
            )
            
            # Check if routing is ambiguous or failed - use Routing Decision Agent
            routing_decision_agent = await self._get_routing_decision_agent()
            if routing_decision_agent and (not routing_result.get("success") or routing_result.get("confidence", 1.0) < 0.8):
                try:
                    # Get routing options (if available) or create from result
                    routing_options = []
                    if routing_result.get("success"):
                        routing_options.append({
                            "target_system": routing_result.get("target_system"),
                            "confidence": routing_result.get("confidence", 0.5),
                            "priority": routing_result.get("priority", 99)
                        })
                    
                    # Get AI-powered routing decision
                    agent_decision = await routing_decision_agent.decide_routing(
                        policy_data=policy_data,
                        routing_options=routing_options if routing_options else None,
                        user_context=user_context
                    )
                    
                    if agent_decision.get("success"):
                        # Use agent's decision
                        target_system = agent_decision.get("target_system")
                        routing_key = routing_key_result.get("routing_key")
                        rule_name = "ai_decision"
                        self.logger.info(f"✅ AI routing decision: {policy_id} → {target_system} (confidence: {agent_decision.get('confidence', 0.0):.2f})")
                        
                        # Update routing_result with agent decision
                        routing_result = {
                            "success": True,
                            "target_system": target_system,
                            "routing_key": routing_key,
                            "rule_name": rule_name,
                            "matched_rules": [rule_name],
                            "ai_enhanced": True,
                            "confidence": agent_decision.get("confidence", 0.0),
                            "reasoning": agent_decision.get("reasoning", "")
                        }
                    else:
                        # Agent decision failed, use original result or fail
                        if not routing_result.get("success"):
                            return {
                                "success": False,
                                "error": routing_result.get("error", "Routing evaluation failed")
                            }
                except Exception as e:
                    self.logger.debug(f"Routing Decision Agent not available: {e}")
                    # Fall through to use deterministic result
            
            if not routing_result.get("success"):
                return {
                    "success": False,
                    "error": routing_result.get("error", "Routing evaluation failed")
                }
            
            target_system = routing_result.get("target_system")
            matched_rules = routing_result.get("matched_rules", [])
            self.logger.info(f"✅ Routing evaluated: {target_system} (matched {len(matched_rules)} rules)")
            
            # Step 4: Update Policy Tracker with routing decision
            if policy_tracker and policy_id:
                try:
                    await policy_tracker.update_migration_status(
                        policy_id=policy_id,
                        status="routed",
                        target_system=target_system,
                        metadata={
                            "routing_key": routing_key,
                            "matched_rules": matched_rules
                        },
                        user_context=user_context
                    )
                    self.logger.info("✅ Policy Tracker updated")
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not update Policy Tracker: {e}")
            
            # Step 5: Store routing decision in Librarian
            librarian = await self.get_librarian_api()
            routing_decision_id = None
            if librarian:
                routing_decision_doc = {
                    "policy_id": policy_id,
                    "routing_key": routing_key,
                    "target_system": target_system,
                    "matched_rules": matched_rules,
                    "confidence": routing_result.get("confidence", 0.0),
                    "policy_status": policy_status,
                    "routed_at": datetime.utcnow().isoformat()
                }
                
                storage_result = await librarian.store_document(
                    document_data=routing_decision_doc,
                    metadata={
                        "type": "routing_decision",
                        "policy_id": policy_id,
                        "target_system": target_system,
                        "routed_at": datetime.utcnow().isoformat()
                    },
                    user_context=user_context
                )
                routing_decision_id = storage_result.get("document_id") if storage_result else None
                self.logger.info(f"✅ Routing decision stored: {routing_decision_id}")
            
            # Step 6: Track routing lineage
            if data_steward:
                await data_steward.track_lineage(
                    lineage_data={
                        "source": policy_id,
                        "operation": "route_policies",
                        "destination": target_system,
                        "metadata": {
                            "routing_key": routing_key,
                            "routing_decision_id": routing_decision_id,
                            "matched_rules": matched_rules
                        }
                    },
                    user_context=user_context
                )
                self.logger.info("✅ Routing lineage tracked")
            
            # Record health metric (success)
            await self.record_health_metric(
                "route_policies_success",
                1.0,
                {
                    "policy_id": policy_id,
                    "target_system": target_system,
                    "confidence": routing_result.get("confidence", 0.0)
                }
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "route_policies_complete",
                success=True,
                details={
                    "policy_id": policy_id,
                    "target_system": target_system,
                    "confidence": routing_result.get("confidence", 0.0)
                }
            )
            
            self.logger.info(f"✅ Policy routing complete: {policy_id} → {target_system}")
            
            return {
                "success": True,
                "routing_decision_id": routing_decision_id,
                "target_system": target_system,
                "routing_key": routing_key,
                "matched_rules": matched_rules,
                "confidence": routing_result.get("confidence", 0.0),
                "policy_status": policy_status
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "route_policies")
            
            # Record health metric (failure)
            await self.record_health_metric(
                "route_policies_failed",
                1.0,
                {"policy_id": policy_id, "error": str(e)}
            )
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "route_policies_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Policy routing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "policy_id": policy_id
            }
    
    # ============================================================================
    # INITIALIZATION
    # ============================================================================
    
    async def initialize(self) -> bool:
        """
        Initialize Insurance Migration Orchestrator.
        
        Sets up:
        - Liaison Agent (conversational guidance)
        - MCP Server (exposes orchestrator methods as MCP tools)
        """
        try:
            # Call parent initialize
            await super().initialize()
            
            # Initialize Insurance Liaison Agent
            from backend.business_enablement.agents.insurance_liaison_agent import InsuranceLiaisonAgent
            
            self.liaison_agent = await self.initialize_agent(
                InsuranceLiaisonAgent,
                "InsuranceLiaisonAgent",
                agent_type="liaison",
                capabilities=[
                    "legacy_data_ingestion",
                    "canonical_mapping",
                    "policy_routing",
                    "wave_planning",
                    "policy_tracking",
                    "migration_guidance"
                ],
                required_roles=["liaison_agent"]
            )
            
            if self.liaison_agent:
                self.logger.info("✅ Insurance Liaison Agent initialized")
            
            # Initialize Universal Mapper Specialist Agent (for AI-assisted mapping)
            # Using declarative implementation (configuration-driven, LLM-powered reasoning)
            from backend.business_enablement.agents.universal_mapper_specialist import UniversalMapperSpecialist
            
            self._universal_mapper_agent = await self.initialize_agent(
                UniversalMapperSpecialist,
                "UniversalMapperSpecialist",
                agent_type="specialist",
                capabilities=["pattern_learning", "ai_assisted_mapping", "mapping_validation"]
            )
            
            # Give agent access to orchestrator (for MCP server access)
            if self._universal_mapper_agent and hasattr(self._universal_mapper_agent, 'set_orchestrator'):
                self._universal_mapper_agent.set_orchestrator(self)
                self.logger.info("✅ Universal Mapper Agent orchestrator set for MCP tool access")
            
            if self._universal_mapper_agent:
                self.logger.info("✅ Universal Mapper Specialist Agent initialized")
            
            # Initialize Quality Remediation Specialist Agent (for quality intelligence)
            # Using declarative implementation (configuration-driven, LLM-powered reasoning)
            from backend.business_enablement.agents.quality_remediation_specialist import QualityRemediationSpecialist
            
            self._quality_remediation_agent = await self.initialize_agent(
                QualityRemediationSpecialist,
                "QualityRemediationSpecialist",
                agent_type="specialist",
                capabilities=["anomaly_interpretation", "remediation_strategy", "pattern_detection"]
            )
            
            if self._quality_remediation_agent:
                self.logger.info("✅ Quality Remediation Specialist Agent initialized")
            
            # Initialize Routing Decision Specialist Agent (for complex routing decisions)
            # Using declarative implementation (configuration-driven, LLM-powered reasoning)
            from backend.business_enablement.agents.routing_decision_specialist import RoutingDecisionSpecialist
            
            self._routing_decision_agent = await self.initialize_agent(
                RoutingDecisionSpecialist,
                "RoutingDecisionSpecialist",
                agent_type="specialist",
                capabilities=["complex_routing_decisions", "business_context_analysis", "conflict_resolution"]
            )
            
            if self._routing_decision_agent:
                self.logger.info("✅ Routing Decision Specialist Agent initialized")
            
            # Initialize Change Impact Assessment Specialist Agent (for change impact analysis)
            # Using declarative implementation (configuration-driven, LLM-powered reasoning)
            from backend.business_enablement.agents.change_impact_assessment_specialist import ChangeImpactAssessmentSpecialist
            
            self._change_impact_agent = await self.initialize_agent(
                ChangeImpactAssessmentSpecialist,
                "ChangeImpactAssessmentSpecialist",
                agent_type="specialist",
                capabilities=["mapping_rule_impact", "schema_evolution_impact", "downstream_dependency_analysis"]
            )
            
            if self._change_impact_agent:
                self.logger.info("✅ Change Impact Assessment Specialist Agent initialized")
            
            # Initialize MCP Server (exposes orchestrator methods as MCP tools)
            from .mcp_server import InsuranceMigrationMCPServer
            
            self.mcp_server = InsuranceMigrationMCPServer(
                orchestrator=self,
                di_container=self.di_container
            )
            
            # MCP server registers tools in __init__, ready to use
            self.logger.info(f"✅ {self.orchestrator_name} MCP Server initialized")
            
            # Register with Curator (Phase 2 pattern with CapabilityDefinition structure)
            await self._realm_service.register_with_curator(
                capabilities=[
                    {
                        "name": "legacy_data_ingestion",
                        "protocol": "InsuranceMigrationOrchestratorProtocol",
                        "description": "Ingest legacy insurance data files",
                        "contracts": {
                            "soa_api": {
                                "api_name": "ingest_legacy_data",
                                "endpoint": "/api/v1/insurance-migration/ingest-legacy-data",
                                "method": "POST",
                                "handler": self.ingest_legacy_data,
                                "metadata": {
                                    "description": "Ingest legacy insurance data file",
                                    "parameters": ["file_id", "file_data", "filename", "user_context"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "ingest_legacy_data_tool",
                                "tool_definition": {
                                    "name": "ingest_legacy_data_tool",
                                    "description": "Ingest legacy insurance data file",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "file_id": {"type": "string"},
                                            "file_data": {"type": "string", "format": "base64"},
                                            "filename": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "insurance.ingest_legacy_data",
                            "semantic_api": "/api/v1/insurance-migration/ingest-legacy-data"
                        }
                    },
                    {
                        "name": "canonical_mapping",
                        "protocol": "InsuranceMigrationOrchestratorProtocol",
                        "description": "Map legacy data to canonical model",
                        "contracts": {
                            "soa_api": {
                                "api_name": "map_to_canonical",
                                "endpoint": "/api/v1/insurance-migration/map-to-canonical",
                                "method": "POST",
                                "handler": self.map_to_canonical,
                                "metadata": {
                                    "description": "Map legacy data to canonical model",
                                    "parameters": ["file_id", "mapping_strategy", "user_context"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "map_to_canonical_tool",
                                "tool_definition": {
                                    "name": "map_to_canonical_tool",
                                    "description": "Map legacy data to canonical model",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "file_id": {"type": "string"},
                                            "mapping_strategy": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "insurance.map_to_canonical",
                            "semantic_api": "/api/v1/insurance-migration/map-to-canonical"
                        }
                    },
                    {
                        "name": "policy_routing",
                        "protocol": "InsuranceMigrationOrchestratorProtocol",
                        "description": "Route policies to target systems",
                        "contracts": {
                            "soa_api": {
                                "api_name": "route_policies",
                                "endpoint": "/api/v1/insurance-migration/route-policies",
                                "method": "POST",
                                "handler": self.route_policies,
                                "metadata": {
                                    "description": "Route policies to target systems",
                                    "parameters": ["policy_data", "namespace", "user_context"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "route_policies_tool",
                                "tool_definition": {
                                    "name": "route_policies_tool",
                                    "description": "Route policies to target systems",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "policy_data": {"type": "object"},
                                            "namespace": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "insurance.route_policies",
                            "semantic_api": "/api/v1/insurance-migration/route-policies"
                        }
                    }
                ],
                soa_apis=["ingest_legacy_data", "map_to_canonical", "route_policies"],
                mcp_tools=["ingest_legacy_data_tool", "map_to_canonical_tool", "route_policies_tool"]
            )
            
            self.logger.info(f"✅ {self.orchestrator_name} registered with Curator")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.orchestrator_name}: {e}", exc_info=True)
            return False

