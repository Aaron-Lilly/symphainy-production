#!/usr/bin/env python3
"""
Metadata Management Abstraction - Business Logic Implementation

Implements metadata management operations using Supabase adapter.
This is Layer 3 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I manage metadata and governance operations
HOW (Infrastructure Implementation): I implement business logic for Data Steward operations
"""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from foundations.public_works_foundation.abstraction_contracts.metadata_management_protocol import MetadataManagementProtocol

logger = logging.getLogger(__name__)

class MetadataManagementAbstraction(MetadataManagementProtocol):
    """
    Metadata management abstraction with business logic.
    
    Implements Data Steward operations for policy management,
    lineage tracking, and compliance enforcement.
    """
    
    def __init__(self, supabase_adapter, config_adapter, di_container=None):
        """Initialize metadata management abstraction."""
        self.supabase_adapter = supabase_adapter
        self.config_adapter = config_adapter
        self.di_container = di_container
        self.service_name = "metadata_management_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        # Metadata table configuration
        self.metadata_table = "metadata"
        self.lineage_table = "data_lineage"
        self.policies_table = "policies"
        
        self.logger.info("✅ Metadata Management Abstraction initialized")
    
    async def create_metadata(self, 
                            metadata_id: str,
                            metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new metadata record.
        
        Creates metadata record in Supabase with business logic.
        """
        try:
            # Add business logic metadata
            enhanced_metadata = {
                "id": metadata_id,
                "type": metadata_type,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active",
                "version": "1.0"
            }
            
            # Merge with provided metadata
            enhanced_metadata.update(metadata)
            
            # Create metadata record
            result = await self.supabase_adapter.create_metadata(
                self.metadata_table, enhanced_metadata
            )
            
            if result:
                self.logger.debug(f"Metadata created: {metadata_id}")
                
                return True
            else:
                self.logger.error(f"Failed to create metadata: {metadata_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to create metadata {metadata_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Retrieve metadata by ID.
        
        Gets metadata from Supabase.
        """
        try:
            metadata = await self.supabase_adapter.get_metadata(
                self.metadata_table, metadata_id
            )
            
            if metadata:
                self.logger.debug(f"Metadata retrieved: {metadata_id}")
                
            else:
                self.logger.warning(f"Metadata not found: {metadata_id}")
            
            return metadata
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get metadata {metadata_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def update_metadata(self,
                            metadata_id: str,
                            metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing metadata.
        
        Updates metadata in Supabase with business logic.
        """
        try:
            # Add update timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            # Update metadata
            result = await self.supabase_adapter.update_metadata(
                self.metadata_table, metadata_id, updates
            )
            
            if result:
                self.logger.debug(f"Metadata updated: {metadata_id}")
                
                return True
            else:
                self.logger.error(f"Failed to update metadata: {metadata_id}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to update metadata {metadata_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Delete metadata record.
        
        Deletes metadata from Supabase.
        """
        try:
            # Soft delete by updating status
            updates = {
                "status": "deleted",
                "deleted_at": datetime.utcnow().isoformat()
            }
            
            result = await self.supabase_adapter.update_metadata(
                self.metadata_table, metadata_id, updates
            )
            
            if result:
                self.logger.debug(f"Metadata deleted: {metadata_id}")
                
                return True
            else:
                self.logger.error(f"Failed to delete metadata: {metadata_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to delete metadata {metadata_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Query metadata with filters.
        
        Queries metadata from Supabase with business logic.
        """
        try:
            # Add type filter if specified
            if metadata_type:
                if not filters:
                    filters = {}
                filters['type'] = metadata_type
            
            # Add status filter to exclude deleted records
            if not filters:
                filters = {}
            filters['status'] = 'active'
            
            # Query metadata
            results = await self.supabase_adapter.query_metadata(
                self.metadata_table, filters, limit=limit, offset=offset
            )
            
            self.logger.debug(f"Queried {len(results)} metadata records")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to query metadata: {e}")
            raise  # Re-raise for service layer to handle
    
    async def search_metadata(self,
                            query: str,
                            limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search metadata using a query string.
        
        Searches metadata in Supabase with business logic.
        """
        try:
            # Add type filter if specified
            filters = {}
            if metadata_type:
                filters['type'] = metadata_type
            
            # Add status filter to exclude deleted records
            filters['status'] = 'active'
            
            # Search metadata
            search_fields = fields or ['name', 'description', 'tags']
            results = []
            
            for field in search_fields:
                field_results = await self.supabase_adapter.search_metadata(
                    self.metadata_table, field, query, limit=limit
                )
                results.extend(field_results)
            
            # Remove duplicates
            unique_results = list({result['id']: result for result in results}.values())
            
            if limit:
                unique_results = unique_results[:limit]
            
            self.logger.debug(f"Found {len(unique_results)} metadata records for query: {query}")
            
            return unique_results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to search metadata: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get all metadata of a specific type.
        
        Gets metadata from Supabase filtered by type.
        """
        try:
            filters = {
                "type": metadata_type,
                "status": "active"
            }
            
            results = await self.supabase_adapter.query_metadata(
                self.metadata_table, filters
            )
            
            self.logger.debug(f"Found {len(results)} metadata records of type: {metadata_type}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get metadata by type {metadata_type}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get all metadata associated with an entity.
        
        Gets metadata from Supabase filtered by entity.
        """
        try:
            filters = {
                "entity_id": entity_id,
                "status": "active"
            }
            
            results = await self.supabase_adapter.query_metadata(
                self.metadata_table, filters
            )
            
            self.logger.debug(f"Found {len(results)} metadata records for entity: {entity_id}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get metadata by entity {entity_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Create a data lineage record.
        
        Creates lineage record in Supabase with business logic.
        """
        try:
            # Generate lineage ID
            lineage_id = str(uuid.uuid4())
            
            # Add business logic metadata
            enhanced_lineage = {
                "id": lineage_id,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active",
                "version": "1.0"
            }
            
            # Merge with provided lineage data
            enhanced_lineage.update(lineage_data)
            
            # Create lineage record
            result = await self.supabase_adapter.create_lineage_record(enhanced_lineage)
            
            if result:
                self.logger.debug(f"Lineage record created: {lineage_id}")
                
                return lineage_id
            else:
                self.logger.error(f"Failed to create lineage record")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to create lineage record: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get lineage records for a specific asset.
        
        Gets lineage records from Supabase.
        """
        try:
            results = await self.supabase_adapter.get_lineage_by_asset(asset_id)
            
            self.logger.debug(f"Found {len(results)} lineage records for asset: {asset_id}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get lineage by asset {asset_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get lineage records for a specific source.
        
        Gets lineage records from Supabase.
        """
        try:
            results = await self.supabase_adapter.get_lineage_by_source(source_id)
            
            self.logger.debug(f"Found {len(results)} lineage records for source: {source_id}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get lineage by source {source_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Create a new policy.
        
        Creates policy in Supabase with business logic.
        """
        try:
            # Generate policy ID
            policy_id = str(uuid.uuid4())
            
            # Add business logic metadata
            enhanced_policy = {
                "id": policy_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active",
                "version": "1.0"
            }
            
            # Merge with provided policy data
            enhanced_policy.update(policy_data)
            
            # Create policy
            result = await self.supabase_adapter.create_policy(enhanced_policy)
            
            if result:
                self.logger.debug(f"Policy created: {policy_id}")
                
                return policy_id
            else:
                self.logger.error(f"Failed to create policy")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to create policy: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get a specific policy.
        
        Gets policy from Supabase.
        """
        try:
            policy = await self.supabase_adapter.get_policy(policy_id)
            
            if policy:
                self.logger.debug(f"Policy retrieved: {policy_id}")
                
            else:
                self.logger.warning(f"Policy not found: {policy_id}")
            
            return policy
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get policy {policy_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get policies of a specific type.
        
        Gets policies from Supabase filtered by type.
        """
        try:
            results = await self.supabase_adapter.get_policies_by_type(policy_type)
            
            self.logger.debug(f"Found {len(results)} policies of type: {policy_type}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get policies by type {policy_type}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def update_policy(self,
                          policy_id: str,
                          policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing policy.
        
        Updates policy in Supabase with business logic.
        """
        try:
            # Add update timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            # Update policy
            result = await self.supabase_adapter.update_metadata(
                self.policies_table, policy_id, updates
            )
            
            if result:
                self.logger.debug(f"Policy updated: {policy_id}")
                
                return True
            else:
                self.logger.error(f"Failed to update policy: {policy_id}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to update policy {policy_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Delete a policy.
        
        Soft deletes policy in Supabase.
        """
        try:
            # Soft delete by updating status
            updates = {
                "status": "deleted",
                "deleted_at": datetime.utcnow().isoformat()
            }
            
            result = await self.supabase_adapter.update_metadata(
                self.policies_table, policy_id, updates
            )
            
            if result:
                self.logger.debug(f"Policy deleted: {policy_id}")
                
                return True
            else:
                self.logger.error(f"Failed to delete policy: {policy_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to delete policy {policy_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get statistics about stored metadata.
        
        Gets statistics from Supabase.
        """
        try:
            # Get all metadata
            all_metadata = await self.query_metadata()
            
            # Calculate statistics
            total_metadata = len(all_metadata)
            
            # Group by type
            types = {}
            for metadata in all_metadata:
                metadata_type = metadata.get('type', 'unknown')
                types[metadata_type] = types.get(metadata_type, 0) + 1
            
            # Group by status
            statuses = {}
            for metadata in all_metadata:
                status = metadata.get('status', 'unknown')
                statuses[status] = statuses.get(status, 0) + 1
            
            statistics = {
                "total_metadata": total_metadata,
                "types": types,
                "statuses": statuses,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.debug(f"Metadata statistics: {total_metadata} records")
            
            return statistics
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get metadata statistics: {e}")
    
            raise  # Re-raise for service layer to handle

        """
        Clean up orphaned metadata records.
        
        This is a simplified implementation - in practice you'd need
        more sophisticated logic to identify truly orphaned metadata.
        """
        try:
            # Get all metadata
            all_metadata = await self.query_metadata()
            
            # Check for orphaned records (simplified logic)
            orphaned_count = 0
            for metadata in all_metadata:
                metadata_id = metadata.get('id')
                if metadata_id:
                    # Check if metadata is orphaned (simplified check)
                    if metadata.get('status') == 'deleted':
                        # Already marked as deleted
                        continue
                    
                    # Check if metadata has no associated entity
                    if not metadata.get('entity_id'):
                        # Mark as orphaned
                        await self.update_metadata(metadata_id, {
                            "status": "orphaned",
                            "orphaned_at": datetime.utcnow().isoformat()
                        })
                        orphaned_count += 1
            
            self.logger.debug(f"Cleaned up {orphaned_count} orphaned metadata records")
            
            return orphaned_count
            
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup orphaned metadata: {e}")
    
            raise  # Re-raise for service layer to handle

        """
        Create a backup of metadata.
        
        Creates backup in Supabase.
        """
        try:
            # Get metadata
            metadata = await self.get_metadata(metadata_id)
            if not metadata:
                raise ValueError(f"Metadata {metadata_id} not found")
            
            # Create backup metadata
            backup_id = f"{metadata_id}_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            backup_metadata = metadata.copy()
            backup_metadata['id'] = backup_id
            backup_metadata['backup_of'] = metadata_id
            backup_metadata['backup_timestamp'] = datetime.utcnow().isoformat()
            backup_metadata['backup_type'] = 'manual'
            
            # Create backup
            result = await self.create_metadata(backup_id, backup_metadata, "backup")
            
            if result:
                self.logger.debug(f"Metadata backup created: {backup_id}")
                
                return True
            else:
                self.logger.error(f"Failed to create metadata backup: {metadata_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to backup metadata {metadata_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Restore metadata from a backup.
        
        Restores metadata from backup in Supabase.
        """
        try:
            # Get backup metadata
            backup_metadata = await self.get_metadata(backup_id)
            if not backup_metadata:
                return False
            
            # Create restore metadata
            restore_metadata = backup_metadata.copy()
            restore_metadata['id'] = metadata_id
            restore_metadata['restored_from'] = backup_id
            restore_metadata['restored_at'] = datetime.utcnow().isoformat()
            
            # Create restored metadata
            result = await self.create_metadata(metadata_id, restore_metadata, "restored")
            
            if result:
                self.logger.debug(f"Metadata restored from backup: {backup_id} -> {metadata_id}")
                
                return True
            else:
                self.logger.error(f"Failed to restore metadata from backup: {backup_id} -> {metadata_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to restore metadata {metadata_id} from backup {backup_id}: {e}")
            raise  # Re-raise for service layer to handle
