#!/usr/bin/env python3
"""
Knowledge Discovery Protocol - Abstraction Contract Layer

Protocol defining knowledge discovery and search operations.
This is Layer 2 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I define the contract for knowledge discovery operations
HOW (Infrastructure Implementation): I specify the interface for knowledge search and discovery
"""

from typing import Dict, Any, List, Optional, Protocol, Union
from datetime import datetime
from enum import Enum

class SearchMode(Enum):
    """Search mode enumeration."""
    EXACT = "exact"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"

class KnowledgeType(Enum):
    """Knowledge type enumeration."""
    DOCUMENT = "document"
    CONCEPT = "concept"
    RELATIONSHIP = "relationship"
    METADATA = "metadata"
    ANALYTICS = "analytics"

class DiscoveryScope(Enum):
    """Discovery scope enumeration."""
    LOCAL = "local"
    GLOBAL = "global"
    CONTEXTUAL = "contextual"
    SEMANTIC = "semantic"

class KnowledgeDiscoveryProtocol(Protocol):
    """
    Protocol for knowledge discovery operations.
    
    Defines the interface for knowledge search, discovery, and semantic operations
    across multiple backends (Meilisearch, ArangoDB, Redis Graph).
    """
    
    # ============================================================================
    # SEARCH OPERATIONS
    # ============================================================================
    
    async def search_knowledge(self, 
                              query: str,
                              search_mode: SearchMode = SearchMode.HYBRID,
                              knowledge_types: Optional[List[KnowledgeType]] = None,
                              scope: DiscoveryScope = DiscoveryScope.GLOBAL,
                              filters: Optional[Dict[str, Any]] = None,
                              limit: int = 20,
                              offset: int = 0) -> Dict[str, Any]:
        """
        Search for knowledge assets.
        
        Args:
            query: Search query string
            search_mode: Search mode (exact, fuzzy, semantic, hybrid)
            knowledge_types: Types of knowledge to search
            scope: Discovery scope (local, global, contextual, semantic)
            filters: Additional search filters
            limit: Maximum number of results
            offset: Result offset for pagination
            
        Returns:
            Dict containing search results and metadata
        """
        ...
    
    async def semantic_search(self, 
                             query: str,
                             similarity_threshold: float = 0.7,
                             max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform semantic search for knowledge.
        
        Args:
            query: Semantic search query
            similarity_threshold: Minimum similarity score
            max_results: Maximum number of results
            
        Returns:
            List of semantically similar knowledge assets
        """
        ...
    
    async def faceted_search(self, 
                           query: str,
                           facets: List[str],
                           limit: int = 20) -> Dict[str, Any]:
        """
        Perform faceted search with analytics.
        
        Args:
            query: Search query
            facets: Facets to analyze
            limit: Maximum number of results
            
        Returns:
            Dict containing results and facet distribution
        """
        ...
    
    # ============================================================================
    # DISCOVERY OPERATIONS
    # ============================================================================
    
    async def discover_related_knowledge(self, 
                                       asset_id: str,
                                       relationship_types: Optional[List[str]] = None,
                                       max_depth: int = 2) -> List[Dict[str, Any]]:
        """
        Discover knowledge related to a specific asset.
        
        Args:
            asset_id: ID of the knowledge asset
            relationship_types: Types of relationships to explore
            max_depth: Maximum relationship depth
            
        Returns:
            List of related knowledge assets
        """
        ...
    
    async def find_knowledge_paths(self, 
                                 start_asset_id: str,
                                 end_asset_id: str,
                                 max_paths: int = 5) -> List[Dict[str, Any]]:
        """
        Find paths between knowledge assets.
        
        Args:
            start_asset_id: Starting asset ID
            end_asset_id: Ending asset ID
            max_paths: Maximum number of paths to return
            
        Returns:
            List of knowledge paths
        """
        ...
    
    async def get_knowledge_clusters(self, 
                                   cluster_size: int = 5,
                                   similarity_threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Get knowledge clusters based on similarity.
        
        Args:
            cluster_size: Size of clusters to generate
            similarity_threshold: Minimum similarity for clustering
            
        Returns:
            List of knowledge clusters
        """
        ...
    
    # ============================================================================
    # RECOMMENDATION OPERATIONS
    # ============================================================================
    
    async def get_knowledge_recommendations(self, 
                                          asset_id: str,
                                          recommendation_type: str = "similar",
                                          limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get knowledge recommendations for an asset.
        
        Args:
            asset_id: ID of the knowledge asset
            recommendation_type: Type of recommendations (similar, related, trending)
            limit: Maximum number of recommendations
            
        Returns:
            List of knowledge recommendations
        """
        ...
    
    async def update_recommendations(self, 
                                   asset_id: str,
                                   recommendations: List[Dict[str, Any]]) -> bool:
        """
        Update recommendations for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            recommendations: List of recommendations to store
            
        Returns:
            Success status
        """
        ...
    
    # ============================================================================
    # ANALYTICS OPERATIONS
    # ============================================================================
    
    async def get_search_analytics(self, 
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get search analytics and insights.
        
        Args:
            start_date: Start date for analytics
            end_date: End date for analytics
            
        Returns:
            Dict containing search analytics
        """
        ...
    
    async def track_search_event(self, 
                               query: str,
                               results_count: int,
                               user_id: Optional[str] = None,
                               metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Track a search event for analytics.
        
        Args:
            query: Search query
            results_count: Number of results returned
            user_id: ID of the user performing the search
            metadata: Additional search metadata
            
        Returns:
            Success status
        """
        ...
    
    # ============================================================================
    # KNOWLEDGE GRAPH OPERATIONS
    # ============================================================================
    
    async def create_knowledge_relationship(self, 
                                          source_asset_id: str,
                                          target_asset_id: str,
                                          relationship_type: str,
                                          properties: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a relationship between knowledge assets.
        
        Args:
            source_asset_id: Source asset ID
            target_asset_id: Target asset ID
            relationship_type: Type of relationship
            properties: Relationship properties
            
        Returns:
            Relationship ID
        """
        ...
    
    async def get_knowledge_relationships(self, 
                                        asset_id: str,
                                        relationship_types: Optional[List[str]] = None,
                                        direction: str = "both") -> List[Dict[str, Any]]:
        """
        Get relationships for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            relationship_types: Types of relationships to retrieve
            direction: Relationship direction (incoming, outgoing, both)
            
        Returns:
            List of relationships
        """
        ...
    
    async def traverse_knowledge_graph(self, 
                                     start_asset_id: str,
                                     traversal_rules: Dict[str, Any],
                                     max_depth: int = 3) -> List[Dict[str, Any]]:
        """
        Traverse the knowledge graph from a starting point.
        
        Args:
            start_asset_id: Starting asset ID
            traversal_rules: Rules for graph traversal
            max_depth: Maximum traversal depth
            
        Returns:
            List of traversed knowledge assets
        """
        ...
    
    # ============================================================================
    # METADATA OPERATIONS
    # ============================================================================
    
    async def get_knowledge_metadata(self, 
                                   asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            
        Returns:
            Asset metadata or None
        """
        ...
    
    async def update_knowledge_metadata(self, 
                                      asset_id: str,
                                      metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            metadata: Metadata to update
            
        Returns:
            Success status
        """
        ...
    
    async def add_semantic_tags(self, 
                              asset_id: str,
                              tags: List[str],
                              confidence_scores: Optional[List[float]] = None) -> bool:
        """
        Add semantic tags to a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            tags: List of semantic tags
            confidence_scores: Confidence scores for tags
            
        Returns:
            Success status
        """
        ...
    
    async def search_by_semantic_tags(self, 
                                    tags: List[str],
                                    min_confidence: float = 0.5) -> List[Dict[str, Any]]:
        """
        Search knowledge assets by semantic tags.
        
        Args:
            tags: List of semantic tags to search
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of matching knowledge assets
        """
        ...
    
    # ============================================================================
    # GOVERNANCE OPERATIONS
    # ============================================================================
    
    async def apply_governance_policy(self, 
                                   asset_id: str,
                                   policy_id: str) -> bool:
        """
        Apply a governance policy to a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            policy_id: ID of the governance policy
            
        Returns:
            Success status
        """
        ...
    
    async def get_governance_policies(self, 
                                    policy_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get governance policies.
        
        Args:
            policy_type: Optional policy type filter
            
        Returns:
            List of governance policies
        """
        ...
    
    # ============================================================================
    # UTILITY OPERATIONS
    # ============================================================================
    
    async def get_knowledge_statistics(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics.
        
        Returns:
            Dict containing knowledge base statistics
        """
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on knowledge discovery services.
        
        Returns:
            Dict containing health status
        """
        ...

