#!/usr/bin/env python3
"""
Semantic Data Protocol - Abstraction Contract

Defines the contract for semantic data operations (embeddings, semantic graphs).
This is Layer 2 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I define the contract for semantic data operations
HOW (Infrastructure Implementation): I provide abstract methods for semantic data storage and retrieval
"""

from typing import Protocol, Dict, Any, List, Optional

class SemanticDataProtocol(Protocol):
    """Protocol for semantic data operations (embeddings, semantic graphs)."""
    
    # ============================================================================
    # EMBEDDING OPERATIONS
    # ============================================================================
    
    async def store_semantic_embeddings(
        self,
        content_id: str,
        file_id: str,
        embeddings: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store semantic embeddings for structured content.
        
        Args:
            content_id: Content metadata ID
            file_id: File UUID
            embeddings: List of embedding dictionaries with column_name, metadata_embedding, meaning_embedding, samples_embedding
            user_context: Optional user context for tenant_id
        
        Returns:
            Storage result with count of stored embeddings
        """
        ...
    
    async def get_semantic_embeddings(
        self,
        content_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get semantic embeddings with filtering.
        
        Args:
            content_id: Optional content metadata ID (if None, queries all embeddings)
            filters: Optional filters (column_name, semantic_id, file_id, parsed_file_id, etc.)
            user_context: Optional user context for tenant_id
        
        Returns:
            List of embedding dictionaries
        """
        ...
    
    async def query_by_semantic_id(
        self,
        semantic_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query embeddings by semantic ID.
        
        Args:
            semantic_id: Semantic ID to query
            user_context: Optional user context for tenant_id
        
        Returns:
            List of matching embedding dictionaries
        """
        ...
    
    async def vector_search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Vector similarity search.
        
        Args:
            query_embedding: Query vector (embedding)
            limit: Maximum number of results
            filters: Optional filters (content_id, file_id, column_name, etc.)
            user_context: Optional user context for tenant_id
        
        Returns:
            List of matching embedding dictionaries with similarity scores
        """
        ...
    
    # ============================================================================
    # SEMANTIC GRAPH OPERATIONS
    # ============================================================================
    
    async def store_semantic_graph(
        self,
        content_id: str,
        file_id: str,
        semantic_graph: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store semantic graph for unstructured content.
        
        Args:
            content_id: Content metadata ID
            file_id: File UUID
            semantic_graph: Semantic graph data (nodes, edges)
            user_context: Optional user context for tenant_id
        
        Returns:
            Storage result with graph information
        """
        ...
    
    async def get_semantic_graph(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get semantic graph for content.
        
        Args:
            content_id: Content metadata ID
            user_context: Optional user context for tenant_id
        
        Returns:
            Semantic graph data (nodes, edges)
        """
        ...
    
    # ============================================================================
    # CORRELATION MAP OPERATIONS (For hybrid parsing)
    # ============================================================================
    
    async def store_correlation_map(
        self,
        content_id: str,
        file_id: str,
        correlation_map: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store correlation map linking structured and unstructured data.
        
        Args:
            content_id: Content metadata ID
            file_id: File UUID
            correlation_map: Correlation map data
            user_context: Optional user context for tenant_id
        
        Returns:
            Storage result with correlation map information
        """
        ...
    
    async def get_correlation_map(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get correlation map for hybrid content.
        
        Args:
            content_id: Content metadata ID
            user_context: Optional user context for tenant_id
        
        Returns:
            Correlation map data
        """
        ...
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of the semantic data system.
        
        Returns:
            Dict containing health status information
        """
        ...



