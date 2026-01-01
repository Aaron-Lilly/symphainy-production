#!/usr/bin/env python3
"""
Data Steward Service - Data Governance Module (Expanded)

Micro-module for expanded data governance covering all data types:
- Platform data governance (before semantic layer)
- Client data governance (before semantic layer)
- Parsed data governance (before semantic layer)
- Semantic layer governance (after semantic processing)

WHAT: I provide governance for all data types at all stages
HOW: I use existing governance modules (policy_management, lineage_tracking, quality_compliance)
     and apply them to platform, client, parsed, and semantic data
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime


class DataGovernance:
    """Expanded data governance module for all data types."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def govern_platform_file_metadata(
        self,
        file_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Govern platform file metadata."""
        try:
            # Get file metadata via file management abstraction
            file_management = self.service.file_management_abstraction
            if not file_management:
                raise ValueError("File management abstraction not available")
            
            file_metadata = await file_management.get_file(file_id)
            if not file_metadata:
                return {
                    "success": False,
                    "error": f"File {file_id} not found"
                }
            
            # Apply governance policies
            governance_result = await self._apply_governance_policies(
                data_id=file_id,
                data_type="platform_file_metadata",
                data=file_metadata,
                user_context=user_context
            )
            
            return {
                "success": True,
                "file_id": file_id,
                "governance_result": governance_result
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to govern platform file metadata: {e}")
            raise
    
    async def govern_platform_parsed_data(
        self,
        parsed_data_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Govern platform parsed data."""
        try:
            # Get parsed data (implementation depends on storage location)
            # This would query the parsed data store
            parsed_data = await self._get_parsed_data(parsed_data_id, "platform")
            if not parsed_data:
                return {
                    "success": False,
                    "error": f"Parsed data {parsed_data_id} not found"
                }
            
            # Apply governance policies
            governance_result = await self._apply_governance_policies(
                data_id=parsed_data_id,
                data_type="platform_parsed_data",
                data=parsed_data,
                user_context=user_context
            )
            
            return {
                "success": True,
                "parsed_data_id": parsed_data_id,
                "governance_result": governance_result
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to govern platform parsed data: {e}")
            raise
    
    async def govern_client_file_metadata(
        self,
        file_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Govern client file metadata."""
        try:
            # Validate tenant access
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            # Get file metadata
            file_management = self.service.file_management_abstraction
            if not file_management:
                raise ValueError("File management abstraction not available")
            
            file_metadata = await file_management.get_file(file_id)
            if not file_metadata:
                return {
                    "success": False,
                    "error": f"File {file_id} not found"
                }
            
            # Apply governance policies
            governance_result = await self._apply_governance_policies(
                data_id=file_id,
                data_type="client_file_metadata",
                data=file_metadata,
                user_context=user_context
            )
            
            return {
                "success": True,
                "file_id": file_id,
                "governance_result": governance_result
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to govern client file metadata: {e}")
            raise
    
    async def govern_client_parsed_data(
        self,
        parsed_data_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Govern client parsed data."""
        try:
            # Validate tenant access
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            # Get parsed data
            parsed_data = await self._get_parsed_data(parsed_data_id, "client")
            if not parsed_data:
                return {
                    "success": False,
                    "error": f"Parsed data {parsed_data_id} not found"
                }
            
            # Apply governance policies
            governance_result = await self._apply_governance_policies(
                data_id=parsed_data_id,
                data_type="client_parsed_data",
                data=parsed_data,
                user_context=user_context
            )
            
            return {
                "success": True,
                "parsed_data_id": parsed_data_id,
                "governance_result": governance_result
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to govern client parsed data: {e}")
            raise
    
    async def govern_semantic_data(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Govern semantic layer data."""
        try:
            # Get semantic data via ContentMetadataAbstraction
            content_metadata = self.service.content_metadata_abstraction
            if not content_metadata:
                raise ValueError("Content metadata abstraction not available")
            
            # Get semantic embeddings or graph
            semantic_embeddings = await content_metadata.get_semantic_embeddings(content_id)
            semantic_graph = await content_metadata.get_semantic_graph(content_id)
            
            # Apply governance policies
            governance_result = await self._apply_governance_policies(
                data_id=content_id,
                data_type="semantic_data",
                data={
                    "embeddings": semantic_embeddings,
                    "graph": semantic_graph
                },
                user_context=user_context
            )
            
            return {
                "success": True,
                "content_id": content_id,
                "governance_result": governance_result
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to govern semantic data: {e}")
            raise
    
    async def apply_quality_policy(
        self,
        data_id: str,
        data_type: str,
        policy_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Apply quality policy to any data type."""
        try:
            # Get policy from policy registry
            policy = await self._get_policy(policy_id)
            if not policy:
                return {
                    "success": False,
                    "error": f"Policy {policy_id} not found"
                }
            
            # Get data based on type
            data = await self._get_data_by_type(data_id, data_type, user_context)
            if not data:
                return {
                    "success": False,
                    "error": f"Data {data_id} of type {data_type} not found"
                }
            
            # Apply policy rules using quality compliance module
            policy_result = await self.service.quality_compliance_module.validate_schema(
                schema_data=data,
                user_context=user_context
            )
            
            return {
                "success": True,
                "data_id": data_id,
                "data_type": data_type,
                "policy_id": policy_id,
                "policy_result": {
                    "passed": policy_result,
                    "violations": []
                }
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to apply quality policy: {e}")
            raise
    
    async def track_lineage(
        self,
        lineage_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Track lineage for any data type."""
        try:
            # Use existing lineage tracking module
            lineage_tracking = self.service.lineage_tracking_module
            if not lineage_tracking:
                raise ValueError("Lineage tracking module not available")
            
            # Record lineage
            lineage_id = await lineage_tracking.record_lineage(lineage_data, user_context)
            
            return lineage_id
        except Exception as e:
            self.logger.error(f"❌ Failed to track lineage: {e}")
            raise
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    async def _apply_governance_policies(
        self,
        data_id: str,
        data_type: str,
        data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Apply governance policies to data."""
        try:
            # Get policies for data type
            policy = await self.service.policy_management_module.get_policy_for_content(
                content_type=data_type,
                user_context=user_context
            )
            
            # Apply quality compliance
            quality_result = await self.service.quality_compliance_module.validate_schema(
                schema_data=data,
                user_context=user_context
            )
            
            # Get quality metrics
            quality_metrics = await self.service.quality_compliance_module.get_quality_metrics(
                asset_id=data_id,
                user_context=user_context
            )
            
            return {
                "compliance_status": "compliant" if quality_result else "non_compliant",
                "policies_applied": [policy.get("policy_id")] if policy else [],
                "quality_metrics": quality_metrics,
                "violations": [] if quality_result else ["quality_check_failed"]
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to apply governance policies: {e}")
            return {
                "compliance_status": "error",
                "policies_applied": [],
                "violations": [str(e)]
            }
    
    async def _get_parsed_data(
        self,
        parsed_data_id: str,
        data_scope: str
    ) -> Optional[Dict[str, Any]]:
        """Get parsed data by ID and scope."""
        # Real implementation: Query parsed data store
        # This would use ArangoAdapter to query parsed data collection
        # For now, return None (will be implemented when parsed data storage is defined)
        return None
    
    async def _get_policy(
        self,
        policy_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get policy by ID."""
        try:
            # Use policy management module to get policy
            # Note: This requires policy_id to be mapped to content_type
            # For now, return None (will be enhanced when policy registry is fully implemented)
            return None
        except Exception as e:
            self.logger.error(f"❌ Failed to get policy: {e}")
            return None
    
    async def _get_data_by_type(
        self,
        data_id: str,
        data_type: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get data by ID and type."""
        try:
            # Route to appropriate data store based on type
            if data_type.startswith("platform_file") or data_type.startswith("client_file"):
                file_management = self.service.file_management_abstraction
                if file_management:
                    return await file_management.get_file(data_id)
            elif data_type.startswith("semantic"):
                content_metadata = self.service.content_metadata_abstraction
                if content_metadata:
                    embeddings = await content_metadata.get_semantic_embeddings(data_id)
                    graph = await content_metadata.get_semantic_graph(data_id)
                    return {
                        "embeddings": embeddings,
                        "graph": graph
                    }
            elif data_type.startswith("platform_parsed") or data_type.startswith("client_parsed"):
                return await self._get_parsed_data(data_id, data_type.split("_")[0])
            
            return None
        except Exception as e:
            self.logger.error(f"❌ Failed to get data by type: {e}")
            return None




