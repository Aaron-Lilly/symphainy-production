#!/usr/bin/env python3
"""
File Management Protocol - Abstraction Contract

Defines the contract for file management operations.
This is Layer 2 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I define the contract for file management operations
HOW (Infrastructure Implementation): I provide abstract methods for file management
"""

from typing import Protocol, Dict, Any, List, Optional

class FileManagementProtocol(Protocol):
    """Protocol for file management operations."""
    
    # ============================================================================
    # CORE FILE OPERATIONS
    # ============================================================================
    
    async def create_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new file record.
        
        Args:
            file_data: File metadata and information
            
        Returns:
            Dict containing created file information
        """
        ...
    
    async def get_file(self, file_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get file record by UUID.
        
        Args:
            file_uuid: Unique identifier for the file
            
        Returns:
            Dict containing file information or None if not found
        """
        ...
    
    async def update_file(self, file_uuid: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update file record.
        
        Args:
            file_uuid: Unique identifier for the file
            updates: Dictionary of fields to update
            
        Returns:
            Dict containing updated file information
        """
        ...
    
    async def delete_file(self, file_uuid: str) -> bool:
        """
        Delete file record (soft delete).
        
        Args:
            file_uuid: Unique identifier for the file
            
        Returns:
            bool indicating success
        """
        ...
    
    async def list_files(self, user_id: str, tenant_id: Optional[str] = None, 
                        filters: Optional[Dict[str, Any]] = None,
                        limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List files with optional filtering.
        
        Args:
            user_id: User identifier
            tenant_id: Optional tenant identifier
            filters: Optional filters to apply
            limit: Optional limit on number of results
            offset: Optional offset for pagination
            
        Returns:
            List of file records
        """
        ...
    
    # ============================================================================
    # FILE LINKING OPERATIONS
    # ============================================================================
    
    async def create_file_link(self, parent_uuid: str, child_uuid: str, link_type: str) -> Dict[str, Any]:
        """
        Create file relationship link.
        
        Args:
            parent_uuid: UUID of parent file
            child_uuid: UUID of child file
            link_type: Type of relationship
            
        Returns:
            Dict containing link information
        """
        ...
    
    async def get_file_links(self, file_uuid: str, direction: str = "both") -> List[Dict[str, Any]]:
        """
        Get file relationships.
        
        Args:
            file_uuid: UUID of the file
            direction: "parent", "child", or "both"
            
        Returns:
            List of file relationship records
        """
        ...
    
    async def delete_file_link(self, link_id: str) -> bool:
        """
        Delete file relationship link.
        
        Args:
            link_id: Unique identifier for the link
            
        Returns:
            bool indicating success
        """
        ...
    
    # ============================================================================
    # LINEAGE OPERATIONS
    # ============================================================================
    
    async def get_lineage_tree(self, root_uuid: str) -> List[Dict[str, Any]]:
        """
        Get complete file lineage tree.
        
        Args:
            root_uuid: UUID of the root file
            
        Returns:
            List of files in lineage tree with hierarchy information
        """
        ...
    
    async def get_file_descendants(self, root_uuid: str) -> List[Dict[str, Any]]:
        """
        Get all descendants of a file.
        
        Args:
            root_uuid: UUID of the root file
            
        Returns:
            List of descendant files
        """
        ...
    
    # ============================================================================
    # SEARCH OPERATIONS
    # ============================================================================
    
    async def search_files(self, user_id: str, search_term: str, 
                          content_type: Optional[str] = None,
                          file_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search files by various criteria.
        
        Args:
            user_id: User identifier
            search_term: Text to search for
            content_type: Optional content type filter
            file_type: Optional file type filter
            
        Returns:
            List of matching file records
        """
        ...
    
    # ============================================================================
    # STATISTICS OPERATIONS
    # ============================================================================
    
    async def get_file_statistics(self, user_id: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get file statistics for a user.
        
        Args:
            user_id: User identifier
            tenant_id: Optional tenant identifier
            
        Returns:
            Dict containing file statistics
        """
        ...
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of the file management system.
        
        Returns:
            Dict containing health status information
        """
        ...