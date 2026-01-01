#!/usr/bin/env python3
"""
State Promotion Protocol - Abstraction Contract

Defines the contract for state promotion analysis and persistence strategies.
This is Layer 2 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I define how state data should be analyzed and promoted
HOW (Infrastructure Implementation): I provide the interface for state promotion logic
"""

from typing import Protocol
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime

class PersistenceStrategy(Enum):
    """Enumeration of state persistence strategies."""
    IMMEDIATE_PERSIST = "immediate_persist"
    DELAYED_PERSIST = "delayed_persist"
    CACHE_ONLY = "cache_only"

class PersistenceBackend(Enum):
    """Enumeration of persistence backends."""
    ARANGO_DB = "arango_db"
    REDIS = "redis"
    MEMORY = "memory"

class StatePromotionProtocol(Protocol):
    """
    Protocol for state promotion analysis and persistence decisions.
    
    This protocol defines how state data should be analyzed to determine
    the appropriate persistence strategy and backend.
    """
    
    async def analyze_state_complexity(self, state_data: Dict[str, Any]) -> int:
        """
        Analyze the complexity of state data.
        
        Args:
            state_data: The state data to analyze
            
        Returns:
            int: Complexity score (0-100)
        """
        ...
    
    async def analyze_state_size(self, state_data: Dict[str, Any]) -> int:
        """
        Analyze the size of state data.
        
        Args:
            state_data: The state data to analyze
            
        Returns:
            int: Size estimate in bytes
        """
        ...
    
    async def analyze_state_importance(self, state_data: Dict[str, Any]) -> int:
        """
        Analyze the importance of state data.
        
        Args:
            state_data: The state data to analyze
            
        Returns:
            int: Importance score (0-10)
        """
        ...
    
    async def determine_persistence_strategy(self, 
                                           complexity_score: int,
                                           size_estimate: int,
                                           importance_score: int) -> PersistenceStrategy:
        """
        Determine the persistence strategy based on analysis scores.
        
        Args:
            complexity_score: Complexity analysis result
            size_estimate: Size analysis result
            importance_score: Importance analysis result
            
        Returns:
            PersistenceStrategy: The determined strategy
        """
        ...
    
    async def determine_persistence_backend(self, 
                                        strategy: PersistenceStrategy,
                                        complexity_score: int,
                                        size_estimate: int,
                                        importance_score: int) -> PersistenceBackend:
        """
        Determine the persistence backend based on strategy and scores.
        
        Args:
            strategy: The determined persistence strategy
            complexity_score: Complexity analysis result
            size_estimate: Size analysis result
            importance_score: Importance analysis result
            
        Returns:
            PersistenceBackend: The determined backend
        """
        ...
    
    async def calculate_ttl(self, 
                          strategy: PersistenceStrategy,
                          backend: PersistenceBackend,
                          importance_score: int) -> int:
        """
        Calculate the time-to-live for state data.
        
        Args:
            strategy: The persistence strategy
            backend: The persistence backend
            importance_score: The importance score
            
        Returns:
            int: TTL in seconds
        """
        ...
    
    async def should_promote_state(self, 
                                 state_data: Dict[str, Any],
                                 session_context: Dict[str, Any]) -> bool:
        """
        Determine if state should be promoted to persistent storage.
        
        Args:
            state_data: The state data to evaluate
            session_context: The session context information
            
        Returns:
            bool: True if state should be promoted
        """
        ...
    
    async def get_promotion_metadata(self, 
                                    state_data: Dict[str, Any],
                                    strategy: PersistenceStrategy,
                                    backend: PersistenceBackend) -> Dict[str, Any]:
        """
        Generate metadata for state promotion.
        
        Args:
            state_data: The state data being promoted
            strategy: The persistence strategy
            backend: The persistence backend
            
        Returns:
            Dict[str, Any]: Promotion metadata
        """
        ...

