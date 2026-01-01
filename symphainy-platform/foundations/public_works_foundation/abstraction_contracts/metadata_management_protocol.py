#!/usr/bin/env python3
"""
Metadata Management Protocol - Abstraction Contract

Defines the contract for metadata management operations across different backends.
This is Layer 2 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I define how metadata should be managed and stored
HOW (Infrastructure Implementation): I provide the interface for metadata management logic
"""

from typing import Protocol
from typing import Dict, Any, Optional, List
from datetime import datetime

class MetadataManagementProtocol(Protocol):
    """
    Protocol for metadata management operations.
    
    This protocol defines how metadata should be stored, retrieved,
    and managed across different backends.
    """
    
    async def create_metadata(self, 
                            metadata_id: str,
                            metadata: Dict[str, Any],
                            metadata_type: str = "generic") -> bool:
        """
        Create new metadata record.
        
        Args:
            metadata_id: Unique identifier for the metadata
            metadata: The metadata to store
            metadata_type: Type of metadata (file, lineage, policy, etc.)
            
        Returns:
            bool: True if creation was successful
        """
        ...
    
    async def get_metadata(self, metadata_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata by ID.
        
        Args:
            metadata_id: Unique identifier for the metadata
            
        Returns:
            Optional[Dict[str, Any]]: Metadata if found, None otherwise
        """
        ...
    
    async def update_metadata(self, 
                            metadata_id: str,
                            updates: Dict[str, Any]) -> bool:
        """
        Update existing metadata.
        
        Args:
            metadata_id: Unique identifier for the metadata
            updates: The updates to apply
            
        Returns:
            bool: True if update was successful
        """
        ...
    
    async def delete_metadata(self, metadata_id: str) -> bool:
        """
        Delete metadata record.
        
        Args:
            metadata_id: Unique identifier for the metadata
            
        Returns:
            bool: True if deletion was successful
        """
        ...
    
    async def query_metadata(self, 
                           filters: Dict[str, Any] = None,
                           metadata_type: str = None,
                           limit: int = None,
                           offset: int = None) -> List[Dict[str, Any]]:
        """
        Query metadata with filters.
        
        Args:
            filters: Optional filters to apply
            metadata_type: Optional metadata type filter
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List[Dict[str, Any]]: List of matching metadata records
        """
        ...
    
    async def search_metadata(self, 
                            query: str,
                            fields: List[str] = None,
                            metadata_type: str = None,
                            limit: int = None) -> List[Dict[str, Any]]:
        """
        Search metadata using a query string.
        
        Args:
            query: Search query string
            fields: Optional fields to search in
            metadata_type: Optional metadata type filter
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: List of matching metadata records
        """
        ...
    
    async def get_metadata_by_type(self, metadata_type: str) -> List[Dict[str, Any]]:
        """
        Get all metadata of a specific type.
        
        Args:
            metadata_type: Type of metadata to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of metadata records
        """
        ...
    
    async def get_metadata_by_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get all metadata associated with an entity.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            List[Dict[str, Any]]: List of metadata records
        """
        ...
    
    async def create_lineage_record(self, 
                                 lineage_data: Dict[str, Any]) -> str:
        """
        Create a data lineage record.
        
        Args:
            lineage_data: Lineage information
            
        Returns:
            str: Lineage record ID
        """
        ...
    
    async def get_lineage_by_asset(self, asset_id: str) -> List[Dict[str, Any]]:
        """
        Get lineage records for a specific asset.
        
        Args:
            asset_id: Asset identifier
            
        Returns:
            List[Dict[str, Any]]: List of lineage records
        """
        ...
    
    async def get_lineage_by_source(self, source_id: str) -> List[Dict[str, Any]]:
        """
        Get lineage records for a specific source.
        
        Args:
            source_id: Source identifier
            
        Returns:
            List[Dict[str, Any]]: List of lineage records
        """
        ...
    
    async def create_policy(self, policy_data: Dict[str, Any]) -> str:
        """
        Create a new policy.
        
        Args:
            policy_data: Policy information
            
        Returns:
            str: Policy ID
        """
        ...
    
    async def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific policy.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            Optional[Dict[str, Any]]: Policy data if found
        """
        ...
    
    async def get_policies_by_type(self, policy_type: str) -> List[Dict[str, Any]]:
        """
        Get policies of a specific type.
        
        Args:
            policy_type: Type of policy to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of policies
        """
        ...
    
    async def update_policy(self, 
                          policy_id: str,
                          updates: Dict[str, Any]) -> bool:
        """
        Update an existing policy.
        
        Args:
            policy_id: Policy identifier
            updates: Policy updates
            
        Returns:
            bool: True if update was successful
        """
        ...
    
    async def delete_policy(self, policy_id: str) -> bool:
        """
        Delete a policy.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            bool: True if deletion was successful
        """
        ...
    
    async def get_metadata_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored metadata.
        
        Returns:
            Dict[str, Any]: Metadata statistics
        """
        ...
    
    async def cleanup_orphaned_metadata(self) -> int:
        """
        Clean up orphaned metadata records.
        
        Returns:
            int: Number of records cleaned up
        """
        ...
    
    async def backup_metadata(self, metadata_id: str) -> bool:
        """
        Create a backup of metadata.
        
        Args:
            metadata_id: Metadata identifier
            
        Returns:
            bool: True if backup was successful
        """
        ...
    
    async def restore_metadata(self, metadata_id: str, backup_id: str) -> bool:
        """
        Restore metadata from a backup.
        
        Args:
            metadata_id: Metadata identifier
            backup_id: Backup identifier
            
        Returns:
            bool: True if restore was successful
        """
        ...

