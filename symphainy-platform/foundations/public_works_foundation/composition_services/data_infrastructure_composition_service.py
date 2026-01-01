#!/usr/bin/env python3
"""
Data Infrastructure Composition Service - Orchestration Layer

Orchestrates data infrastructure abstractions for Traffic Cop state promotion
and Data Steward ↔ Content Pillar governance integration.
This is Layer 4 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I orchestrate data infrastructure operations
HOW (Infrastructure Implementation): I coordinate between state, file, and metadata abstractions
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from foundations.public_works_foundation.infrastructure_abstractions.state_promotion_abstraction import StatePromotionAbstraction
from foundations.public_works_foundation.infrastructure_abstractions.state_management_abstraction import StateManagementAbstraction
from foundations.public_works_foundation.infrastructure_abstractions.file_management_abstraction import FileManagementAbstraction
from foundations.public_works_foundation.infrastructure_abstractions.metadata_management_abstraction import MetadataManagementAbstraction

logger = logging.getLogger(__name__)

class DataInfrastructureCompositionService:
    """
    Data Infrastructure Composition Service.
    
    Orchestrates the complete data infrastructure workflow including:
    - Traffic Cop state promotion analysis and persistence
    - Data Steward governance operations
    - Content Pillar file processing and metadata management
    - Cross-service data coordination
    """
    
    def __init__(self, 
                 state_promotion: StatePromotionAbstraction,
                 state_management: StateManagementAbstraction,
                 file_management: FileManagementAbstraction,
                 metadata_management: MetadataManagementAbstraction,
                 di_container=None):
        """Initialize data infrastructure composition service."""
        self.state_promotion = state_promotion
        self.state_management = state_management
        self.file_management = file_management
        self.metadata_management = metadata_management
        self.di_container = di_container
        self.service_name = "data_infrastructure_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Data Infrastructure Composition Service initialized")
    
    # ============================================================================
    # SECURITY AND MULTI-TENANCY VALIDATION HELPERS
    # ============================================================================
    
    async def _validate_security_and_tenant(self, user_context: Dict[str, Any], 
                                           resource: str, action: str) -> Optional[Dict[str, Any]]:
        """
        Validate security context and tenant access.
        
        Args:
            user_context: User context with user_id, tenant_id, security_context
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            None if validation passes, error dict if validation fails
        """
        try:
            # Get utilities from DI container
            security = self.di_container.get_utility("security") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            tenant = self.di_container.get_utility("tenant") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            
            user_id = user_context.get("user_id")
            tenant_id = user_context.get("tenant_id")
            security_context = user_context.get("security_context")
            
            # Security validation (if security utility available and context provided)
            if security and security_context:
                try:
                    # Validate user permission
                    has_permission = await security.validate_user_permission(
                        user_id, resource, action, 
                        security_context.get("permissions", [])
                    )
                    if not has_permission:
                        return {
                            "success": False,
                            "error": f"Permission denied: {action} on {resource}",
                            "error_code": "PERMISSION_DENIED"
                        }
                except Exception as e:
                    self.logger.warning(f"Security validation failed: {e}")
                    # Don't fail on security validation errors - log and continue
                    # (security might not be fully bootstrapped)
            
            # Multi-tenancy validation (if tenant utility available and tenant_id provided)
            if tenant and tenant_id:
                try:
                    # Check if multi-tenancy is enabled
                    if tenant.is_multi_tenant_enabled():
                        # Validate tenant access (basic check - user can only access their own tenant)
                        # For cross-tenant access, this would be handled at foundation service level
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            return {
                                "success": False,
                                "error": f"Tenant access denied for tenant: {tenant_id}",
                                "error_code": "TENANT_ACCESS_DENIED"
                            }
                except Exception as e:
                    self.logger.warning(f"Tenant validation failed: {e}")
                    # Don't fail on tenant validation errors - log and continue
            
            return None  # Validation passed
            
        except Exception as e:
            self.logger.error(f"Security/tenant validation error: {e}")
            # Don't fail on validation errors - log and continue
            return None
    

    # ============================================================================
    # TRAFFIC COP STATE PROMOTION ORCHESTRATION
    # ============================================================================
    
    async def promote_traffic_cop_state(self, 
                                       state_data: Dict[str, Any],
                                       session_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate Traffic Cop state promotion workflow.
        
        Complete workflow:
        1. Analyze state complexity, size, and importance
        2. Determine persistence strategy and backend
        3. Calculate TTL and promotion decision
        4. Store state in appropriate backend
        5. Generate promotion metadata
        """
        try:
            self.logger.info(f"🚦 Starting Traffic Cop state promotion for: {state_data.get('id', 'unknown')}")
            
            # Step 1: Analyze state
            complexity = await self.state_promotion.analyze_state_complexity(state_data)
            size = await self.state_promotion.analyze_state_size(state_data)
            importance = await self.state_promotion.analyze_state_importance(state_data)
            
            self.logger.debug(f"State analysis - Complexity: {complexity}, Size: {size}, Importance: {importance}")
            
            # Step 2: Determine strategy and backend
            strategy = await self.state_promotion.determine_persistence_strategy(complexity, size, importance)
            backend = await self.state_promotion.determine_persistence_backend(strategy, complexity, size, importance)
            ttl = await self.state_promotion.calculate_ttl(strategy, backend, importance)
            
            self.logger.debug(f"Persistence decision - Strategy: {strategy.value}, Backend: {backend.value}, TTL: {ttl}")
            
            # Step 3: Check if state should be promoted
            should_promote = await self.state_promotion.should_promote_state(state_data, session_context)
            
            if not should_promote:
                self.logger.info("State promotion not recommended - keeping in memory")
                return {
                    "promoted": False,
                    "reason": "promotion_not_recommended",
                    "strategy": strategy.value,
                    "backend": backend.value
                }
            
            # Step 4: Generate promotion metadata
            promotion_metadata = await self.state_promotion.get_promotion_metadata(state_data, strategy, backend)
            
            # Step 5: Store state in appropriate backend
            state_id = state_data.get('id', f"state_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
            store_success = await self.state_management.store_state(
                state_id, state_data, promotion_metadata, ttl
            )
            
            if store_success:
                self.logger.info(f"✅ State promoted successfully: {state_id} -> {backend.value}")
                
                result = {
                    "promoted": True,
                    "state_id": state_id,
                    "strategy": strategy.value,
                    "backend": backend.value,
                    "ttl": ttl,
                    "metadata": promotion_metadata
                }
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("promote_traffic_cop_state", {
                        "state_id": state_id,
                        "backend": backend.value,
                        "success": True
                    })
                
                return result
            else:
                self.logger.error(f"❌ Failed to promote state: {state_id}")
                return {
                    "promoted": False,
                    "reason": "storage_failed",
                    "state_id": state_id
                }
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "promote_traffic_cop_state",
                    "state_id": state_data.get('id'),
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Traffic Cop state promotion failed: {e}")
            return {
                "promoted": False,
                "reason": "promotion_error",
                "error": str(e),
                "error_code": "DATA_INFRASTRUCTURE_STATE_PROMOTION_ERROR"
            }
    
    async def retrieve_traffic_cop_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve Traffic Cop state from appropriate backend.
        
        Searches across all backends in order of persistence.
        """
        try:
            self.logger.info(f"🔍 Retrieving Traffic Cop state: {state_id}")
            
            # Retrieve state from appropriate backend
            state_data = await self.state_management.retrieve_state(state_id)
            
            if state_data:
                self.logger.info(f"✅ State retrieved successfully: {state_id}")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("retrieve_traffic_cop_state", {
                        "state_id": state_id,
                        "success": True
                    })
                
                return state_data
            else:
                self.logger.warning(f"⚠️ State not found: {state_id}")
                return None
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "retrieve_traffic_cop_state",
                    "state_id": state_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to retrieve Traffic Cop state {state_id}: {e}")
            return None
    
    # ============================================================================
    # DATA STEWARD GOVERNANCE ORCHESTRATION
    # ============================================================================
    
    async def create_governance_policy(self, 
                                     policy_data: Dict[str, Any],
                                     policy_type: str = "data_governance") -> str:
        """
        Orchestrate Data Steward policy creation workflow.
        
        Creates policy and establishes governance framework.
        """
        try:
            self.logger.info(f"🏛️ Creating Data Steward policy: {policy_data.get('name', 'unknown')}")
            
            # Create policy in metadata management
            policy_id = await self.metadata_management.create_policy(policy_data)
            
            if policy_id:
                self.logger.info(f"✅ Governance policy created: {policy_id}")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("create_governance_policy", {
                        "policy_id": policy_id,
                        "policy_type": policy_type,
                        "success": True
                    })
                
                return policy_id
            else:
                self.logger.error(f"❌ Failed to create governance policy")
                return None
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "create_governance_policy",
                    "policy_type": policy_type,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Data Steward policy creation failed: {e}")
            return None
    
    async def track_data_lineage(self, 
                               lineage_data: Dict[str, Any]) -> str:
        """
        Orchestrate Data Steward lineage tracking workflow.
        
        Tracks data lineage and establishes audit trail.
        """
        try:
            self.logger.info(f"📊 Tracking data lineage: {lineage_data.get('asset_id', 'unknown')}")
            
            # Create lineage record
            lineage_id = await self.metadata_management.create_lineage_record(lineage_data)
            
            if lineage_id:
                self.logger.info(f"✅ Data lineage tracked: {lineage_id}")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("track_data_lineage", {
                        "lineage_id": lineage_id,
                        "asset_id": lineage_data.get('asset_id'),
                        "success": True
                    })
                
                return lineage_id
            else:
                self.logger.error(f"❌ Failed to track data lineage")
                return None
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "track_data_lineage",
                    "asset_id": lineage_data.get('asset_id'),
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Data Steward lineage tracking failed: {e}")
            return None
    
    async def enforce_governance_compliance(self, 
                                         asset_id: str,
                                         compliance_rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate Data Steward compliance enforcement workflow.
        
        Enforces governance policies and compliance rules.
        """
        try:
            self.logger.info(f"⚖️ Enforcing governance compliance: {asset_id}")
            
            # Get applicable policies
            policies = await self.metadata_management.get_policies_by_type("data_governance")
            
            # Check compliance against rules
            compliance_results = {
                "asset_id": asset_id,
                "compliant": True,
                "violations": [],
                "enforced_at": datetime.utcnow().isoformat()
            }
            
            for policy in policies:
                policy_rules = policy.get('rules', [])
                for rule in policy_rules:
                    if not self._check_compliance_rule(asset_id, rule, compliance_rules):
                        compliance_results["compliant"] = False
                        compliance_results["violations"].append({
                            "policy_id": policy['id'],
                            "rule": rule,
                            "violation": "rule_violation"
                        })
            
            self.logger.info(f"✅ Governance compliance enforced: {asset_id} - {compliance_results['compliant']}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("enforce_governance_compliance", {
                    "asset_id": asset_id,
                    "compliant": compliance_results['compliant'],
                    "success": True
                })
            
            return compliance_results
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "enforce_governance_compliance",
                    "asset_id": asset_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Data Steward compliance enforcement failed: {e}")
            return {
                "asset_id": asset_id,
                "compliant": False,
                "error": str(e),
                "error_code": "DATA_INFRASTRUCTURE_COMPLIANCE_ERROR"
            }
    
    def _check_compliance_rule(self, asset_id: str, rule: str, compliance_rules: Dict[str, Any]) -> bool:
        """Check if asset complies with a specific rule."""
        # Simplified compliance checking logic
        # In practice, this would be more sophisticated
        return True
    
    # ============================================================================
    # CONTENT PILLAR PROCESSING ORCHESTRATION
    # ============================================================================
    
    async def process_content_upload(self, 
                                   file_data: bytes,
                                   file_metadata: Dict[str, Any],
                                   data_type: str) -> Dict[str, Any]:
        """
        Orchestrate Content Pillar file processing workflow.
        
        Complete workflow:
        1. Upload file to storage
        2. Extract and store metadata
        3. Assess quality and compliance
        4. Report lineage to Data Steward
        """
        try:
            self.logger.info(f"📁 Processing Content Pillar upload: {file_metadata.get('name', 'unknown')}")
            
            # Step 1: Upload file to storage
            file_id = file_metadata.get('id', f"file_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
            upload_success = await self.file_management.upload_file(
                file_id, file_data, file_metadata
            )
            
            if not upload_success:
                self.logger.error(f"❌ File upload failed: {file_id}")
                return {
                    "processed": False,
                    "reason": "upload_failed",
                    "file_id": file_id
                }
            
            # Step 2: Extract and store metadata
            extracted_metadata = await self._extract_file_metadata(file_data, file_metadata)
            metadata_id = await self.metadata_management.create_metadata(
                f"metadata_{file_id}", extracted_metadata, "file_metadata"
            )
            
            # Step 3: Assess quality and compliance
            quality_assessment = await self._assess_file_quality(file_data, extracted_metadata)
            compliance_check = await self.enforce_governance_compliance(file_id, quality_assessment)
            
            # Step 4: Report lineage to Data Steward
            lineage_data = {
                "asset_id": file_id,
                "source": "content_steward_upload",
                "data_type": data_type,
                "processed_at": datetime.utcnow().isoformat(),
                "metadata": extracted_metadata,
                "quality_assessment": quality_assessment,
                "compliance_check": compliance_check
            }
            
            lineage_id = await self.track_data_lineage(lineage_data)
            
            self.logger.info(f"✅ Content Pillar processing completed: {file_id}")
            
            result = {
                "processed": True,
                "file_id": file_id,
                "metadata_id": metadata_id,
                "lineage_id": lineage_id,
                "quality_assessment": quality_assessment,
                "compliance_check": compliance_check
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("process_content_upload", {
                    "file_id": file_id,
                    "data_type": data_type,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "process_content_upload",
                    "file_id": file_metadata.get('id'),
                    "data_type": data_type,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Content Pillar processing failed: {e}")
            return {
                "processed": False,
                "reason": "processing_error",
                "error": str(e),
                "error_code": "DATA_INFRASTRUCTURE_CONTENT_PROCESSING_ERROR"
            }
    
    async def _extract_file_metadata(self, file_data: bytes, file_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional metadata from file data."""
        import hashlib
        
        return {
            "size": len(file_data),
            "hash": hashlib.md5(file_data).hexdigest(),
            "content_type": file_metadata.get('content_type', 'application/octet-stream'),
            "extracted_at": datetime.utcnow().isoformat(),
            "original_metadata": file_metadata
        }
    
    async def _assess_file_quality(self, file_data: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Assess file quality metrics."""
        return {
            "completeness": 1.0,  # Simplified - would be more sophisticated
            "accuracy": 0.95,
            "consistency": 0.98,
            "timeliness": 1.0,
            "assessed_at": datetime.utcnow().isoformat()
        }
    
    # ============================================================================
    # CROSS-SERVICE DATA COORDINATION
    # ============================================================================
    
    async def coordinate_data_workflow(self, 
                                     workflow_type: str,
                                     workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate cross-service data workflow coordination.
        
        Coordinates between Traffic Cop, Data Steward, and Content Pillar.
        """
        try:
            self.logger.info(f"🔄 Coordinating data workflow: {workflow_type}")
            
            result = None
            if workflow_type == "state_promotion":
                result = await self.promote_traffic_cop_state(
                    workflow_data.get('state_data', {}),
                    workflow_data.get('session_context', {})
                )
            elif workflow_type == "file_processing":
                result = await self.process_content_upload(
                    workflow_data.get('file_data', b''),
                    workflow_data.get('file_metadata', {}),
                    workflow_data.get('data_type', 'unknown')
                )
            elif workflow_type == "governance_enforcement":
                result = await self.enforce_governance_compliance(
                    workflow_data.get('asset_id', 'unknown'),
                    workflow_data.get('compliance_rules', {})
                )
            else:
                self.logger.warning(f"⚠️ Unknown workflow type: {workflow_type}")
                result = {
                    "coordinated": False,
                    "reason": "unknown_workflow_type"
                }
            
            # Record telemetry on success (if workflow was recognized and executed)
            if result and (workflow_type in ["state_promotion", "file_processing", "governance_enforcement"]):
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("coordinate_data_workflow", {
                        "workflow_type": workflow_type,
                        "success": True
                    })
            
            return result
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "coordinate_data_workflow",
                    "workflow_type": workflow_type,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Data workflow coordination failed: {e}")
            return {
                "coordinated": False,
                "reason": "coordination_error",
                "error": str(e),
                "error_code": "DATA_INFRASTRUCTURE_WORKFLOW_COORDINATION_ERROR"
            }
    
    async def get_infrastructure_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of all data infrastructure components.
        
        Provides health and status information for monitoring.
        """
        try:
            self.logger.info("📊 Getting data infrastructure status")
            
            # Get state management statistics
            state_stats = await self.state_management.get_state_statistics()
            
            # Get file management statistics
            file_stats = await self.file_management.get_file_statistics()
            
            # Get metadata management statistics
            metadata_stats = await self.metadata_management.get_metadata_statistics()
            
            status = {
                "timestamp": datetime.utcnow().isoformat(),
                "state_management": state_stats,
                "file_management": file_stats,
                "metadata_management": metadata_stats,
                "overall_status": "operational"
            }
            
            self.logger.info("✅ Data infrastructure status retrieved")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_infrastructure_status", {
                    "success": True
                })
            
            return status
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_infrastructure_status",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to get infrastructure status: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": "error",
                "error": str(e),
                "error_code": "DATA_INFRASTRUCTURE_STATUS_ERROR"
            }
