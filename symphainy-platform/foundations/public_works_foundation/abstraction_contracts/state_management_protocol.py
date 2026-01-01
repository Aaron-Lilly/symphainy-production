#!/usr/bin/env python3
"""
State Management Protocol - Abstraction Contract

Defines the contract for state management operations across different backends.
This is Layer 2 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I define how state data should be managed and stored
HOW (Infrastructure Implementation): I provide the interface for state management logic
"""

from typing import Protocol, Dict, Any, Optional, List
from datetime import datetime

class StateManagementProtocol(Protocol):
    """
    Protocol for state management operations.
    
    This protocol defines how state data should be stored, retrieved,
    updated, and managed across different persistence backends.
    """
    
    async def store_state(self, 
                         state_id: str,
                         state_data: Dict[str, Any],
                         metadata: Dict[str, Any] = None,
                         ttl: int = None) -> bool:
        """
        Store state data in the appropriate backend.
        
        Args:
            state_id: Unique identifier for the state
            state_data: The state data to store
            metadata: Optional metadata for the state
            ttl: Time-to-live in seconds
            
        Returns:
            bool: True if storage was successful
        """
        ...
    
    async def retrieve_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve state data from the appropriate backend.
        
        Args:
            state_id: Unique identifier for the state
            
        Returns:
            Optional[Dict[str, Any]]: State data if found, None otherwise
        """
        ...
    
    async def update_state(self, 
                          state_id: str,
                          updates: Dict[str, Any],
                          metadata: Dict[str, Any] = None) -> bool:
        """
        Update existing state data.
        
        Args:
            state_id: Unique identifier for the state
            updates: The updates to apply
            metadata: Optional metadata updates
            
        Returns:
            bool: True if update was successful
        """
        ...
    
    async def delete_state(self, state_id: str) -> bool:
        """
        Delete state data from storage.
        
        Args:
            state_id: Unique identifier for the state
            
        Returns:
            bool: True if deletion was successful
        """
        ...
    
    async def list_states(self, 
                         filters: Dict[str, Any] = None,
                         limit: int = None,
                         offset: int = None) -> List[Dict[str, Any]]:
        """
        List states matching the given criteria.
        
        Args:
            filters: Optional filters to apply
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List[Dict[str, Any]]: List of matching states
        """
        ...
    
    async def search_states(self, 
                          query: str,
                          fields: List[str] = None,
                          limit: int = None) -> List[Dict[str, Any]]:
        """
        Search for states using a query string.
        
        Args:
            query: Search query string
            fields: Optional fields to search in
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: List of matching states
        """
        ...
    
    async def get_state_metadata(self, state_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific state.
        
        Args:
            state_id: Unique identifier for the state
            
        Returns:
            Optional[Dict[str, Any]]: State metadata if found
        """
        ...
    
    async def update_state_metadata(self, 
                                   state_id: str,
                                   metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for a specific state.
        
        Args:
            state_id: Unique identifier for the state
            metadata: New metadata to store
            
        Returns:
            bool: True if update was successful
        """
        ...
    
    async def get_state_history(self, state_id: str) -> List[Dict[str, Any]]:
        """
        Get the history of changes for a specific state.
        
        Args:
            state_id: Unique identifier for the state
            
        Returns:
            List[Dict[str, Any]]: List of historical changes
        """
        ...
    
    async def backup_state(self, state_id: str) -> bool:
        """
        Create a backup of state data.
        
        Args:
            state_id: Unique identifier for the state
            
        Returns:
            bool: True if backup was successful
        """
        ...
    
    async def restore_state(self, state_id: str, backup_id: str) -> bool:
        """
        Restore state data from a backup.
        
        Args:
            state_id: Unique identifier for the state
            backup_id: Identifier of the backup to restore
            
        Returns:
            bool: True if restore was successful
        """
        ...
    
    async def get_state_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored states.
        
        Returns:
            Dict[str, Any]: State statistics
        """
        ...
    
    async def cleanup_expired_states(self) -> int:
        """
        Clean up expired state data.
        
        Returns:
            int: Number of states cleaned up
        """
        ...
    
    async def migrate_state(self, 
                          state_id: str,
                          target_backend: str) -> bool:
        """
        Migrate state data to a different backend.
        
        Args:
            state_id: Unique identifier for the state
            target_backend: Target backend for migration
            
        Returns:
            bool: True if migration was successful
        """
        ...