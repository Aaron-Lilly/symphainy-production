#!/usr/bin/env python3
"""
Knowledge Governance Abstraction - Infrastructure Abstraction Layer

Business logic implementation for knowledge governance operations.
This is Layer 3 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I implement knowledge governance business logic
HOW (Infrastructure Implementation): I coordinate between metadata adapter and ArangoDB for governance
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import asyncio
import json

from foundations.public_works_foundation.abstraction_contracts.knowledge_governance_protocol import (
    KnowledgeGovernanceProtocol, GovernanceLevel, MetadataStatus, PolicyType
)
from foundations.public_works_foundation.infrastructure_adapters.knowledge_metadata_adapter import KnowledgeMetadataAdapter
from foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter import ArangoDBAdapter

logger = logging.getLogger(__name__)

class KnowledgeGovernanceAbstraction(KnowledgeGovernanceProtocol):
    """
    Knowledge Governance Abstraction.
    
    Implements business logic for knowledge governance operations by coordinating
    between metadata adapter and ArangoDB for comprehensive governance management.
    """
    
    def __init__(self, 
                 metadata_adapter: KnowledgeMetadataAdapter,
                 arango_adapter: ArangoDBAdapter,
                 config_adapter=None,
                 di_container=None):
        """Initialize knowledge governance abstraction."""
        self.metadata_adapter = metadata_adapter
        self.arango_adapter = arango_adapter
        self.config_adapter = config_adapter
        self.di_container = di_container
        self.service_name = "knowledge_governance_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        # Governance collections
        self.policies_collection = "governance_policies"
        self.assets_collection = "knowledge_assets"
        self.metadata_collection = "asset_metadata"
        self.audit_collection = "governance_audit"
        
        self.logger.info("✅ Knowledge Governance Abstraction initialized")
    
    # ============================================================================
    # POLICY MANAGEMENT
    # ============================================================================
    
    async def create_governance_policy(self, 
                                     policy_name: str,
                                     policy_type: PolicyType,
                                     policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a governance policy with comprehensive validation.
        
        Stores policy in both metadata adapter and ArangoDB for redundancy.
        """
        try:
            self.logger.info(f"📋 Creating governance policy: {policy_name} (type: {policy_type.value})")
            
            # Validate policy data
            validation_result = await self._validate_policy_data(policy_data, policy_type)
            if not validation_result["valid"]:
                raise ValueError(f"Policy validation failed: {validation_result['errors']}")
            
            # Create policy in metadata adapter
            policy_id = await self.metadata_adapter.create_governance_policy(
                policy_name, policy_data
            )
            
            if not policy_id:
                raise Exception("Failed to create policy in metadata adapter")
            
            # Store policy in ArangoDB for persistence
            arango_policy = {
                "_key": policy_id,
                "name": policy_name,
                "type": policy_type.value,
                "data": policy_data,
                "description": description,
                "status": "active",
                "created_at": datetime.utcnow().isoformat()
            }
            
            arango_success = await self.arango_adapter.create_document(
                self.policies_collection, arango_policy
            )
            
            if not arango_success:
                self.logger.warning(f"⚠️ Policy created in metadata but failed in ArangoDB: {policy_id}")
            
            self.logger.info(f"✅ Governance policy created: {policy_id}")
            
            return policy_id
            
        except Exception as e:
            self.logger.error(f"❌ Governance policy creation failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def update_governance_policy(self,
                                     policy_id: str,
                                     policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a governance policy with validation.
        
        Updates policy in both metadata adapter and ArangoDB.
        """
        try:
            self.logger.info(f"📝 Updating governance policy: {policy_id}")
            
            # Validate updated policy data
            validation_result = await self._validate_policy_data(policy_data)
            if not validation_result["valid"]:
                raise ValueError(f"Policy validation failed: {validation_result['errors']}")
            
            # Update in metadata adapter
            metadata_success = await self.metadata_adapter.update_asset_metadata(
                policy_id, policy_data
            )
            
            # Update in ArangoDB
            arango_success = await self.arango_adapter.update_document(
                self.policies_collection, policy_id, policy_data
            )
            
            success = metadata_success and arango_success
            
            if success:
                self.logger.info(f"✅ Governance policy updated: {policy_id}")
            else:
                self.logger.warning(f"⚠️ Partial policy update: {policy_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Governance policy update failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Delete a governance policy with cleanup.
        
        Removes policy from both metadata adapter and ArangoDB.
        """
        try:
            self.logger.info(f"🗑️ Deleting governance policy: {policy_id}")
            
            # Delete from metadata adapter
            metadata_success = await self.metadata_adapter.delete_asset_metadata(policy_id)
            
            # Delete from ArangoDB
            arango_success = await self.arango_adapter.delete_document(
                self.policies_collection, policy_id
            )
            
            success = metadata_success and arango_success
            
            if success:
                self.logger.info(f"✅ Governance policy deleted: {policy_id}")
            else:
                self.logger.warning(f"⚠️ Partial policy deletion: {policy_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Governance policy deletion failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get governance policies with filtering.
        
        Retrieves policies from metadata adapter with optional filtering.
        """
        try:
            self.logger.info("📋 Getting governance policies")
            
            # Get policies from metadata adapter
            policies = await self.metadata_adapter.get_governance_policies(
                policy_type.value if policy_type else None
            )
            
            # Apply status filter if specified
            if status:
                policies = [p for p in policies if p.get('status') == status]
            
            self.logger.info(f"✅ Governance policies retrieved: {len(policies)} policies")
            
            return policies
            
        except Exception as e:
            self.logger.error(f"❌ Governance policies retrieval failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def apply_governance_policy(self,
                                  asset_id: str,
                                  policy_id: str) -> Dict[str, Any]:
        """
        Apply a governance policy to a knowledge asset.
        
        Creates policy-asset relationship in both metadata and ArangoDB.
        """
        try:
            self.logger.info(f"🔗 Applying policy to asset: {policy_id} → {asset_id}")
            
            # Get policy details
            policy = await self._get_policy_details(policy_id)
            if not policy:
                raise ValueError(f"Policy not found: {policy_id}")
            
            # Apply policy using metadata adapter
            metadata_success = await self.metadata_adapter.apply_governance_policy(
                asset_id, policy_id
            )
            
            # Create policy-asset relationship in ArangoDB
            relationship = {
                "asset_id": asset_id,
                "policy_id": policy_id,
                "effective_date": (effective_date or datetime.utcnow()).isoformat(),
                "applied_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            arango_success = await self.arango_adapter.create_document(
                "policy_asset_relationships", relationship
            )
            
            success = metadata_success and arango_success
            
            if success:
                self.logger.info(f"✅ Policy applied to asset: {policy_id} → {asset_id}")
            else:
                self.logger.warning(f"⚠️ Partial policy application: {policy_id} → {asset_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Policy application failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def remove_governance_policy(self,
                                     asset_id: str,
                                     policy_id: str) -> Dict[str, Any]:
        """
        Remove a governance policy from a knowledge asset.
        
        Removes policy-asset relationship from both metadata and ArangoDB.
        """
        try:
            self.logger.info(f"🔓 Removing policy from asset: {policy_id} → {asset_id}")
            
            # Remove from metadata adapter
            metadata_success = await self.metadata_adapter.delete_asset_metadata(asset_id)
            
            # Remove relationship from ArangoDB
            arango_success = await self.arango_adapter.delete_document_by_query(
                "policy_asset_relationships",
                {"asset_id": asset_id, "policy_id": policy_id}
            )
            
            success = metadata_success and arango_success
            
            if success:
                self.logger.info(f"✅ Policy removed from asset: {policy_id} → {asset_id}")
            else:
                self.logger.warning(f"⚠️ Partial policy removal: {policy_id} → {asset_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Policy removal failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get policies applied to a knowledge asset.
        
        Retrieves policies from both metadata and ArangoDB relationships.
        """
        try:
            self.logger.info(f"📋 Getting asset policies: {asset_id}")
            
            # Get policies from ArangoDB relationships
            relationships = await self.arango_adapter.query_documents(
                "policy_asset_relationships",
                {"asset_id": asset_id}
            )
            
            # Get policy details for each relationship
            policies = []
            for relationship in relationships:
                policy_id = relationship.get('policy_id')
                policy_details = await self._get_policy_details(policy_id)
                if policy_details:
                    policy_details['relationship'] = relationship
                    policies.append(policy_details)
            
            self.logger.info(f"✅ Asset policies retrieved: {len(policies)} policies")
            
            return policies
            
        except Exception as e:
            self.logger.error(f"❌ Asset policies retrieval failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def create_asset_metadata(self,
                                  asset_id: str,
                                  metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create metadata for a knowledge asset with governance.
        
        Stores metadata in both metadata adapter and ArangoDB.
        """
        try:
            self.logger.info(f"📊 Creating asset metadata: {asset_id} (level: {governance_level.value})")
            
            # Add governance information to metadata
            enhanced_metadata = {
                **metadata,
                "governance_level": governance_level.value,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Create in metadata adapter (optional - may not be connected if using ArangoDB only)
            metadata_success = False
            if hasattr(self.metadata_adapter, '_client') and self.metadata_adapter._client:
                try:
                    metadata_success = await self.metadata_adapter.create_asset_metadata(
                        asset_id, enhanced_metadata
                    )
                except Exception as e:
                    self.logger.error(f"❌ Error: {e}")
                    self.logger.debug(f"Metadata adapter not available (using ArangoDB only): {e}")
                    metadata_success = True  # Don't fail if metadata adapter isn't connected
                # Metadata adapter not connected - use ArangoDB only
                    raise  # Re-raise for service layer to handle

                self.logger.debug("Metadata adapter not connected - using ArangoDB only for metadata storage")
            
            # Store in ArangoDB (primary storage)
            arango_metadata = {
                "_key": asset_id,
                **enhanced_metadata
            }
            
            try:
                arango_result = await self.arango_adapter.create_document(
                    self.metadata_collection, arango_metadata
                )
                # create_document returns a dict with _id, _key, _rev on success
                arango_success = arango_result is not None and isinstance(arango_result, dict) and '_key' in arango_result
            except Exception as e:
                self.logger.error(f"❌ Failed to create metadata in ArangoDB: {e}")
                arango_success = False
            
            # Success if ArangoDB succeeded (metadata adapter is optional)
                raise  # Re-raise for service layer to handle

            
            if success:
                self.logger.info(f"✅ Asset metadata created: {asset_id}")
            else:
                self.logger.warning(f"⚠️ Partial metadata creation: {asset_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Asset metadata creation failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def update_asset_metadata(self,
                                   asset_id: str,
                                   metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update metadata for a knowledge asset.
        
        Updates metadata in both metadata adapter and ArangoDB.
        """
        try:
            self.logger.info(f"📝 Updating asset metadata: {asset_id}")
            
            # Add update timestamp
            enhanced_metadata = {
                **metadata,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Update in metadata adapter
            metadata_success = await self.metadata_adapter.update_asset_metadata(
                asset_id, enhanced_metadata
            )
            
            # Update in ArangoDB
            arango_success = await self.arango_adapter.update_document(
                self.metadata_collection, asset_id, enhanced_metadata
            )
            
            success = metadata_success and arango_success
            
            if success:
                self.logger.info(f"✅ Asset metadata updated: {asset_id}")
            else:
                self.logger.warning(f"⚠️ Partial metadata update: {asset_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Asset metadata update failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get metadata for a knowledge asset.
        
        Retrieves metadata from metadata adapter with ArangoDB fallback.
        """
        try:
            self.logger.info(f"📊 Getting asset metadata: {asset_id}")
            
            # Try ArangoDB first (primary storage)
            metadata = await self.arango_adapter.get_document(
                self.metadata_collection, asset_id
            )
            
            # Fallback to metadata adapter if ArangoDB doesn't have it
            if not metadata and hasattr(self.metadata_adapter, '_client') and self.metadata_adapter._client:
                try:
                    metadata = await self.metadata_adapter.get_asset_metadata(asset_id)
                except Exception as e:
                    self.logger.error(f"❌ Error: {e}")
                    self.logger.debug(f"Metadata adapter not available: {e}")
            
                    raise  # Re-raise for service layer to handle

                self.logger.info(f"✅ Asset metadata retrieved: {asset_id}")
            else:
                self.logger.warning(f"⚠️ Asset metadata not found: {asset_id}")
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"❌ Asset metadata retrieval failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def add_semantic_tags(self,
                              asset_id: str,
                              tags: List[str]) -> Dict[str, Any]:
        """
        Add semantic tags to a knowledge asset.
        
        Stores tags in metadata adapter with ArangoDB backup.
        """
        try:
            self.logger.info(f"🏷️ Adding semantic tags: {asset_id} ({len(tags)} tags)")
            
            # Add semantic tags using metadata adapter
            metadata_success = await self.metadata_adapter.add_semantic_tags(
                asset_id, tags, confidence_scores
            )
            
            # Store tags in ArangoDB for persistence
            if metadata_success:
                tag_documents = []
                for i, tag in enumerate(tags):
                    confidence = confidence_scores[i] if confidence_scores and i < len(confidence_scores) else 1.0
                    tag_doc = {
                        "_key": f"{asset_id}_{tag}_{i}",
                        "asset_id": asset_id,
                        "tag": tag,
                        "confidence": confidence,
                        "source": tag_source or "system",
                        "created_at": datetime.utcnow().isoformat()
                    }
                    tag_documents.append(tag_doc)
                
                arango_success = await self.arango_adapter.create_documents(
                    "semantic_tags", tag_documents
                )
                
                if not arango_success:
                    self.logger.warning(f"⚠️ Tags added to metadata but failed in ArangoDB: {asset_id}")
            
            if metadata_success:
                self.logger.info(f"✅ Semantic tags added: {asset_id}")
            
            return metadata_success
            
        except Exception as e:
            self.logger.error(f"❌ Semantic tags addition failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get semantic tags for a knowledge asset.
        
        Retrieves tags from metadata adapter.
        """
        try:
            self.logger.info(f"🏷️ Getting semantic tags: {asset_id}")
            
            # Get tags from metadata adapter
            tags = await self.metadata_adapter.get_semantic_tags(asset_id)
            
            self.logger.info(f"✅ Semantic tags retrieved: {asset_id} ({len(tags)} tags)")
            
            return tags
            
        except Exception as e:
            self.logger.error(f"❌ Semantic tags retrieval failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def search_by_semantic_tags(self,
                                    tags: List[str],
                                    tag_operator: str = "AND") -> List[Dict[str, Any]]:
        """
        Search knowledge assets by semantic tags.
        
        Uses metadata adapter for tag-based search.
        """
        try:
            self.logger.info(f"🔍 Searching by semantic tags: {tags} (operator: {tag_operator})")
            
            # Search using metadata adapter
            results = await self.metadata_adapter.search_by_tags(tags, min_confidence)
            
            self.logger.info(f"✅ Semantic tag search completed: {len(results)} results")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Semantic tag search failed: {e}")
            raise  # Re-raise for service layer to handle
    
    def _validate_policy_data(self,
                                   policy_data: Dict[str, Any]) -> List[str]:
        """Validate policy data structure."""
        try:
            errors = []
            
            # Basic validation
            if not isinstance(policy_data, dict):
                errors.append("Policy data must be a dictionary")
            
            # Type-specific validation
            if policy_type == PolicyType.ACCESS_CONTROL:
                if "permissions" not in policy_data:
                    errors.append("Access control policy must have permissions")
            
            elif policy_type == PolicyType.DATA_QUALITY:
                if "quality_metrics" not in policy_data:
                    errors.append("Data quality policy must have quality metrics")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _get_policy_from_arango(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get policy details from ArangoDB."""
        try:
            policy = await self.arango_adapter.get_document(
                self.policies_collection, policy_id
            )
            return policy
        except Exception as e:
            self.logger.error(f"❌ Failed to get policy details: {e}")
            raise  # Re-raise for service layer to handle
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on governance services."""
        try:
            # Check metadata adapter
            metadata_health = await self.metadata_adapter._get_health()
            
            # Check ArangoDB
            arango_health = await self.arango_adapter._get_health()
            
            overall_health = metadata_health and arango_health
            
            health_status = {
                "overall_health": "healthy" if overall_health else "unhealthy",
                "metadata_adapter": "healthy" if metadata_health else "unhealthy",
                "arango": "healthy" if arango_health else "unhealthy",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")

            raise  # Re-raise for service layer to handle
