#!/usr/bin/env python3
"""
Data Infrastructure Registry - Service Exposure Layer

Central registry for exposing and managing data infrastructure capabilities.
This is Layer 5 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I expose and manage all data infrastructure capabilities
HOW (Infrastructure Implementation): I provide unified access to all data infrastructure services
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from foundations.public_works_foundation.composition_services.data_infrastructure_composition_service import DataInfrastructureCompositionService

logger = logging.getLogger(__name__)

class DataInfrastructureRegistry:
    """
    Data Infrastructure Registry.
    
    Central registry that exposes and manages all data infrastructure capabilities
    including Traffic Cop state promotion, Data Steward governance, and Content Pillar processing.
    """
    
    def __init__(self, composition_service: DataInfrastructureCompositionService):
        """Initialize data infrastructure registry."""
        self.composition_service = composition_service
        self.logger = logging.getLogger(__name__)
        
        # Registry capabilities
        self.capabilities = {
            "traffic_cop": {
                "state_promotion": True,
                "state_retrieval": True,
                "state_analysis": True
            },
            "data_steward": {
                "policy_management": True,
                "lineage_tracking": True,
                "compliance_enforcement": True
            },
            "content_steward": {
                "file_processing": True,
                "metadata_extraction": True,
                "quality_assessment": True
            },
            "cross_service": {
                "workflow_coordination": True,
                "status_monitoring": True,
                "health_checks": True
            }
        }
        
        self.logger.info("✅ Data Infrastructure Registry initialized")
    
    # ============================================================================
    # TRAFFIC COP CAPABILITIES
    # ============================================================================
    
    async def promote_state(self, 
                           state_data: Dict[str, Any],
                           session_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Promote Traffic Cop state to persistent storage.
        
        Public API for Traffic Cop state promotion workflow.
        """
        try:
            self.logger.info(f"🚦 Registry: Promoting Traffic Cop state: {state_data.get('id', 'unknown')}")
            
            result = await self.composition_service.promote_traffic_cop_state(
                state_data, session_context
            )
            
            self.logger.info(f"✅ Registry: State promotion completed: {result.get('promoted', False)}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Registry: State promotion failed: {e}")
            return {
                "promoted": False,
                "reason": "registry_error",
                "error": str(e)
            }
    
    async def retrieve_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve Traffic Cop state from storage.
        
        Public API for Traffic Cop state retrieval.
        """
        try:
            self.logger.info(f"🔍 Registry: Retrieving Traffic Cop state: {state_id}")
            
            result = await self.composition_service.retrieve_traffic_cop_state(state_id)
            
            if result:
                self.logger.info(f"✅ Registry: State retrieved successfully: {state_id}")
            else:
                self.logger.warning(f"⚠️ Registry: State not found: {state_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Registry: State retrieval failed: {e}")
            return None
    
    # ============================================================================
    # DATA STEWARD CAPABILITIES
    # ============================================================================
    
    async def create_policy(self, 
                           policy_data: Dict[str, Any],
                           policy_type: str = "data_governance") -> str:
        """
        Create Data Steward governance policy.
        
        Public API for Data Steward policy management.
        """
        try:
            self.logger.info(f"🏛️ Registry: Creating Data Steward policy: {policy_data.get('name', 'unknown')}")
            
            policy_id = await self.composition_service.create_governance_policy(
                policy_data, policy_type
            )
            
            if policy_id:
                self.logger.info(f"✅ Registry: Policy created successfully: {policy_id}")
            else:
                self.logger.error(f"❌ Registry: Policy creation failed")
            
            return policy_id
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Policy creation failed: {e}")
            return None
    
    async def track_lineage(self, lineage_data: Dict[str, Any]) -> str:
        """
        Track data lineage for Data Steward.
        
        Public API for Data Steward lineage tracking.
        """
        try:
            self.logger.info(f"📊 Registry: Tracking data lineage: {lineage_data.get('asset_id', 'unknown')}")
            
            lineage_id = await self.composition_service.track_data_lineage(lineage_data)
            
            if lineage_id:
                self.logger.info(f"✅ Registry: Lineage tracked successfully: {lineage_id}")
            else:
                self.logger.error(f"❌ Registry: Lineage tracking failed")
            
            return lineage_id
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Lineage tracking failed: {e}")
            return None
    
    async def enforce_compliance(self, 
                               asset_id: str,
                               compliance_rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce governance compliance for Data Steward.
        
        Public API for Data Steward compliance enforcement.
        """
        try:
            self.logger.info(f"⚖️ Registry: Enforcing governance compliance: {asset_id}")
            
            result = await self.composition_service.enforce_governance_compliance(
                asset_id, compliance_rules
            )
            
            self.logger.info(f"✅ Registry: Compliance enforcement completed: {result.get('compliant', False)}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Compliance enforcement failed: {e}")
            return {
                "asset_id": asset_id,
                "compliant": False,
                "error": str(e)
            }
    
    # ============================================================================
    # CONTENT PILLAR CAPABILITIES
    # ============================================================================
    
    async def process_file(self, 
                          file_data: bytes,
                          file_metadata: Dict[str, Any],
                          data_type: str) -> Dict[str, Any]:
        """
        Process Content Pillar file upload.
        
        Public API for Content Pillar file processing.
        """
        try:
            self.logger.info(f"📁 Registry: Processing Content Pillar file: {file_metadata.get('name', 'unknown')}")
            
            result = await self.composition_service.process_content_upload(
                file_data, file_metadata, data_type
            )
            
            self.logger.info(f"✅ Registry: File processing completed: {result.get('processed', False)}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Registry: File processing failed: {e}")
            return {
                "processed": False,
                "reason": "registry_error",
                "error": str(e)
            }
    
    # ============================================================================
    # CROSS-SERVICE COORDINATION
    # ============================================================================
    
    async def coordinate_workflow(self, 
                                workflow_type: str,
                                workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate cross-service data workflow.
        
        Public API for multi-service workflow coordination.
        """
        try:
            self.logger.info(f"🔄 Registry: Coordinating workflow: {workflow_type}")
            
            result = await self.composition_service.coordinate_data_workflow(
                workflow_type, workflow_data
            )
            
            self.logger.info(f"✅ Registry: Workflow coordination completed: {workflow_type}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Workflow coordination failed: {e}")
            return {
                "coordinated": False,
                "reason": "registry_error",
                "error": str(e)
            }
    
    # ============================================================================
    # REGISTRY MANAGEMENT
    # ============================================================================
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get registry capabilities.
        
        Returns information about available data infrastructure capabilities.
        """
        try:
            self.logger.info("📋 Registry: Getting capabilities")
            
            capabilities = {
                "registry_version": "1.0.0",
                "capabilities": self.capabilities,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "operational"
            }
            
            self.logger.info("✅ Registry: Capabilities retrieved")
            return capabilities
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Failed to get capabilities: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive infrastructure status.
        
        Returns health and status information for all data infrastructure components.
        """
        try:
            self.logger.info("📊 Registry: Getting infrastructure status")
            
            status = await self.composition_service.get_infrastructure_status()
            
            # Add registry-specific status
            status["registry"] = {
                "status": "operational",
                "capabilities": self.capabilities,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.info("✅ Registry: Infrastructure status retrieved")
            return status
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Failed to get infrastructure status: {e}")
            return {
                "registry": {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.
        
        Checks the health of all data infrastructure components.
        """
        try:
            self.logger.info("🏥 Registry: Performing health check")
            
            # Get infrastructure status
            status = await self.get_status()
            
            # Determine overall health
            overall_health = "healthy"
            if status.get("overall_status") != "operational":
                overall_health = "unhealthy"
            
            health_check = {
                "overall_health": overall_health,
                "components": {
                    "traffic_cop": "operational" if self.capabilities["traffic_cop"]["state_promotion"] else "degraded",
                    "data_steward": "operational" if self.capabilities["data_steward"]["policy_management"] else "degraded",
                    "content_steward": "operational" if self.capabilities["content_steward"]["file_processing"] else "degraded",
                    "cross_service": "operational" if self.capabilities["cross_service"]["workflow_coordination"] else "degraded"
                },
                "timestamp": datetime.utcnow().isoformat(),
                "registry_status": "operational"
            }
            
            self.logger.info(f"✅ Registry: Health check completed: {overall_health}")
            return health_check
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Health check failed: {e}")
            return {
                "overall_health": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # SERVICE DISCOVERY
    # ============================================================================
    
    async def discover_services(self) -> Dict[str, Any]:
        """
        Discover available data infrastructure services.
        
        Returns information about available services and their capabilities.
        """
        try:
            self.logger.info("🔍 Registry: Discovering services")
            
            services = {
                "traffic_cop": {
                    "name": "Traffic Cop State Management",
                    "description": "State analysis and persistence for Traffic Cop",
                    "capabilities": self.capabilities["traffic_cop"],
                    "endpoints": [
                        "promote_state",
                        "retrieve_state"
                    ]
                },
                "data_steward": {
                    "name": "Data Steward Governance",
                    "description": "Policy management and compliance enforcement",
                    "capabilities": self.capabilities["data_steward"],
                    "endpoints": [
                        "create_policy",
                        "track_lineage",
                        "enforce_compliance"
                    ]
                },
                "content_steward": {
                    "name": "Content Steward Processing",
                    "description": "File processing and metadata management",
                    "capabilities": self.capabilities["content_steward"],
                    "endpoints": [
                        "process_file"
                    ]
                },
                "cross_service": {
                    "name": "Cross-Service Coordination",
                    "description": "Multi-service workflow orchestration",
                    "capabilities": self.capabilities["cross_service"],
                    "endpoints": [
                        "coordinate_workflow"
                    ]
                }
            }
            
            self.logger.info("✅ Registry: Services discovered")
            return services
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Service discovery failed: {e}")
            return {
                "error": str(e),
                "services": {}
            }
    
    # ============================================================================
    # UNIFIED API
    # ============================================================================
    
    async def execute_data_operation(self, 
                                   operation: str,
                                   parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute data infrastructure operation.
        
        Unified API for all data infrastructure operations.
        """
        try:
            self.logger.info(f"🎯 Registry: Executing data operation: {operation}")
            
            # Route operation to appropriate service
            if operation == "promote_state":
                return await self.promote_state(
                    parameters.get("state_data", {}),
                    parameters.get("session_context", {})
                )
            elif operation == "retrieve_state":
                return await self.retrieve_state(parameters.get("state_id", ""))
            elif operation == "create_policy":
                return await self.create_policy(
                    parameters.get("policy_data", {}),
                    parameters.get("policy_type", "data_governance")
                )
            elif operation == "track_lineage":
                return await self.track_lineage(parameters.get("lineage_data", {}))
            elif operation == "enforce_compliance":
                return await self.enforce_compliance(
                    parameters.get("asset_id", ""),
                    parameters.get("compliance_rules", {})
                )
            elif operation == "process_file":
                return await self.process_file(
                    parameters.get("file_data", b""),
                    parameters.get("file_metadata", {}),
                    parameters.get("data_type", "unknown")
                )
            elif operation == "coordinate_workflow":
                return await self.coordinate_workflow(
                    parameters.get("workflow_type", ""),
                    parameters.get("workflow_data", {})
                )
            else:
                self.logger.warning(f"⚠️ Registry: Unknown operation: {operation}")
                return {
                    "success": False,
                    "reason": "unknown_operation",
                    "operation": operation
                }
                
        except Exception as e:
            self.logger.error(f"❌ Registry: Data operation failed: {e}")
            return {
                "success": False,
                "reason": "operation_error",
                "error": str(e)
            }
