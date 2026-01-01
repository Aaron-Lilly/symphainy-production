#!/usr/bin/env python3
"""
Knowledge Discovery Abstraction - Infrastructure Abstraction Layer

Business logic implementation for knowledge discovery operations.
This is Layer 3 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I implement knowledge discovery business logic
HOW (Infrastructure Implementation): I coordinate between Meilisearch, Redis Graph, and ArangoDB adapters
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import asyncio
import json

from foundations.public_works_foundation.abstraction_contracts.knowledge_discovery_protocol import (
    KnowledgeDiscoveryProtocol, SearchMode, KnowledgeType, DiscoveryScope
)
from foundations.public_works_foundation.infrastructure_adapters.meilisearch_knowledge_adapter import MeilisearchKnowledgeAdapter
from foundations.public_works_foundation.infrastructure_adapters.redis_graph_knowledge_adapter import RedisGraphKnowledgeAdapter
from foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter import ArangoDBAdapter

logger = logging.getLogger(__name__)

class KnowledgeDiscoveryAbstraction(KnowledgeDiscoveryProtocol):
    """
    Knowledge Discovery Abstraction.
    
    Implements business logic for knowledge discovery operations by coordinating
    between Meilisearch (search), Redis Graph (real-time), and ArangoDB (persistent storage).
    """
    
    def __init__(self, 
                 meilisearch_adapter: MeilisearchKnowledgeAdapter,
                 redis_graph_adapter: RedisGraphKnowledgeAdapter,
                 arango_adapter: ArangoDBAdapter,
                 config_adapter=None,
                 di_container=None):
        """Initialize knowledge discovery abstraction."""
        self.meilisearch_adapter = meilisearch_adapter
        self.redis_graph_adapter = redis_graph_adapter
        self.arango_adapter = arango_adapter
        self.config_adapter = config_adapter
        self.di_container = di_container
        self.service_name = "knowledge_discovery_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        # Knowledge indexes and graphs
        self.knowledge_index = "knowledge_assets"
        self.analytics_index = "knowledge_analytics"
        self.knowledge_graph = "knowledge_graph"
        self.semantic_graph = "semantic_graph"
        
        self.logger.info("✅ Knowledge Discovery Abstraction initialized")
    
    # ============================================================================
    # SEARCH OPERATIONS
    # ============================================================================
    
    async def search_knowledge(self, 
                              query: str,
                              filters: Dict[str, Any] = None,
                              limit: int = 10) -> Dict[str, Any]:
        """
        Search for knowledge assets using hybrid approach.
        
        Coordinates between Meilisearch (search), Redis Graph (real-time), and ArangoDB (persistent).
        """
        try:
            self.logger.info(f"🔍 Searching knowledge: {query} (mode: {search_mode.value})")
            
            # Determine search strategy based on mode and scope
            search_results = await self._execute_hybrid_search(
                query, search_mode, knowledge_types, scope, filters, limit, offset
            )
            
            # Track search analytics
            await self._track_search_analytics(query, len(search_results.get('hits', [])))
            
            self.logger.info(f"✅ Knowledge search completed: {len(search_results.get('hits', []))} results")
            
            return search_results
            
        except Exception as e:
            self.logger.error(f"❌ Knowledge search failed: {e}")
    
            raise  # Re-raise for service layer to handle
    
    async def execute_hybrid_search(self,
                                   query: str,
                                   search_mode: SearchMode,
                                   knowledge_types: Optional[List[KnowledgeType]],
                                   scope: DiscoveryScope,
                                   filters: Optional[Dict[str, Any]],
                                   limit: int) -> Dict[str, Any]:
        """Execute hybrid search across multiple backends."""
        try:
            # Primary search using Meilisearch
            meilisearch_results = await self.meilisearch_adapter.search(
                self.knowledge_index,
                query,
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            # Real-time relationship discovery using Redis Graph
            if scope == DiscoveryScope.SEMANTIC or search_mode == SearchMode.SEMANTIC:
                # Use Redis Graph for semantic relationships
                semantic_results = await self.redis_graph_adapter.find_semantic_similarity(
                    self.semantic_graph, query, 0.7
                )
                meilisearch_results = await self._merge_semantic_results(meilisearch_results, semantic_results)
            
            # Persistent knowledge validation using ArangoDB
            if scope == DiscoveryScope.GLOBAL:
                # Use ArangoDB for persistent knowledge validation
                arango_results = await self.arango_adapter.find_semantic_similarity(query, 0.7, 10)
                meilisearch_results = await self._merge_semantic_results(meilisearch_results, arango_results)
            
            return meilisearch_results
            
        except Exception as e:
            self.logger.error(f"❌ Hybrid search execution failed: {e}")
    
            raise  # Re-raise for service layer to handle
    
    async def perform_semantic_search(self,
                             query: str,
                             filters: Dict[str, Any] = None,
                             limit: int = 10) -> Dict[str, Any]:
        """
        Perform semantic search using Redis Graph and ArangoDB.
        
        Uses Redis Graph for real-time semantic relationships and ArangoDB for persistent knowledge.
        """
        try:
            self.logger.info(f"🧠 Semantic search: {query} (threshold: {similarity_threshold})")
            
            # Get semantic relationships from Redis Graph
            semantic_relationships = await self.redis_graph_adapter.find_semantic_similarity(
                self.semantic_graph, query, similarity_threshold
            )
            
            # Get persistent knowledge from ArangoDB
            arango_semantic = await self.arango_adapter.find_semantic_similarity(
                query, similarity_threshold, max_results
            )
            
            # Merge and rank results
            combined_results = await self._merge_semantic_results(
                semantic_relationships, arango_semantic, similarity_threshold
            )
            
            self.logger.info(f"✅ Semantic search completed: {len(combined_results)} results")
            
            return combined_results
            
        except Exception as e:
            self.logger.error(f"❌ Semantic search failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def perform_faceted_search(self,
                           query: str,
                           facets: List[str],
                           limit: int = 10) -> Dict[str, Any]:
        """
        Perform faceted search with analytics using Meilisearch.
        
        Provides search results with facet distribution for knowledge discovery.
        """
        try:
            self.logger.info(f"📊 Faceted search: {query} (facets: {facets})")
            
            # Execute faceted search using Meilisearch
            faceted_results = await self.meilisearch_adapter.search_with_facets(
                self.knowledge_index,
                query,
                facets,
                limit
            )
            
            # Get additional analytics
            analytics = await self.meilisearch_adapter.get_search_analytics(
                self.knowledge_index
            )
            
            # Combine results with analytics
            combined_results = {
                **faceted_results,
                "analytics": analytics,
                "searchMetadata": {
                    "query": query,
                    "facets": facets,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            self.logger.info(f"✅ Faceted search completed: {len(faceted_results.get('hits', []))} results")
            
            return combined_results
            
        except Exception as e:
            self.logger.error(f"❌ Faceted search failed: {e}")
            raise  # Re-raise for service layer to handle
    
    # ============================================================================
    # DISCOVERY OPERATIONS
    # ============================================================================
    
    async def discover_related_knowledge(self,
                                       asset_id: str,
                                       relationship_types: List[str] = None,
                                       limit: int = 10) -> Dict[str, Any]:
        """
        Discover related knowledge using Redis Graph and ArangoDB.
        
        Uses Redis Graph for real-time traversal and ArangoDB for persistent relationships.
        """
        try:
            self.logger.info(f"🔗 Discovering related knowledge: {asset_id} (depth: {max_depth})")
            
            # Get real-time relationships from Redis Graph
            redis_relationships = await self.redis_graph_adapter.get_neighbors(
                self.knowledge_graph, asset_id, max_depth
            )
            
            # Get persistent relationships from ArangoDB
            arango_relationships = await self.arango_adapter.get_related_documents(
                asset_id, relationship_types, max_depth
            )
            
            # Merge and deduplicate results
            combined_relationships = await self._merge_relationship_results(
                redis_relationships, arango_relationships
            )
            
            self.logger.info(f"✅ Related knowledge discovered: {len(combined_relationships)} assets")
            
            return combined_relationships
            
        except Exception as e:
            self.logger.error(f"❌ Related knowledge discovery failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def find_knowledge_paths(self,
                                 start_asset_id: str,
                                 end_asset_id: str,
                                 max_depth: int = 5) -> List[List[str]]:
        """
        Find paths between knowledge assets using Redis Graph.
        
        Uses Redis Graph for real-time path finding between knowledge assets.
        """
        try:
            self.logger.info(f"🛤️ Finding knowledge paths: {start_asset_id} → {end_asset_id}")
            
            # Find paths using Redis Graph
            paths = await self.redis_graph_adapter.find_path(
                self.knowledge_graph, start_asset_id, end_asset_id, max_paths
            )
            
            self.logger.info(f"✅ Knowledge paths found: {len(paths)} paths")
            
            return paths
            
        except Exception as e:
            self.logger.error(f"❌ Knowledge path finding failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_knowledge_clusters(self,
                                   cluster_size: int = 10,
                                   similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Get knowledge clusters using Redis Graph and ArangoDB.
        
        Uses Redis Graph for real-time clustering and ArangoDB for persistent clusters.
        """
        try:
            self.logger.info(f"🔗 Getting knowledge clusters: size={cluster_size}, threshold={similarity_threshold}")
            
            # Get clusters from Redis Graph
            redis_clusters = await self.redis_graph_adapter.get_knowledge_clusters(
                self.knowledge_graph, cluster_size
            )
            
            # Get persistent clusters from ArangoDB
            arango_clusters = await self.arango_adapter.get_knowledge_clusters(
                cluster_size, similarity_threshold
            )
            
            # Merge clusters
            combined_clusters = await self._merge_cluster_results(
                redis_clusters, arango_clusters, similarity_threshold
            )
            
            self.logger.info(f"✅ Knowledge clusters retrieved: {len(combined_clusters)} clusters")
            
            return combined_clusters
            
        except Exception as e:
            self.logger.error(f"❌ Knowledge clustering failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_knowledge_recommendations(self,
                                          asset_id: str,
                                          recommendation_type: str = "similar",
                                          limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get knowledge recommendations using hybrid approach.
        
        Combines Meilisearch recommendations with Redis Graph relationships.
        """
        try:
            self.logger.info(f"💡 Getting recommendations: {asset_id} (type: {recommendation_type})")
            
            # Get recommendations from Meilisearch
            meilisearch_recs = await self.meilisearch_adapter.get_recommendations(
                self.knowledge_index, asset_id, limit
            )
            
            # Get relationship-based recommendations from Redis Graph
            graph_recs = await self.redis_graph_adapter.get_neighbors(
                self.knowledge_graph, asset_id, 2
            )
            
            # Merge and rank recommendations
            combined_recommendations = await self._merge_recommendation_results(
                meilisearch_recs, graph_recs, recommendation_type
            )
            
            self.logger.info(f"✅ Recommendations retrieved: {len(combined_recommendations)} items")
            
            return combined_recommendations
            
        except Exception as e:
            self.logger.error(f"❌ Knowledge recommendations failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def update_recommendations(self,
                                   asset_id: str,
                                   recommendations: List[Dict[str, Any]]) -> bool:
        """
        Update recommendations using Meilisearch.
        
        Stores recommendations in Meilisearch for fast retrieval.
        """
        try:
            self.logger.info(f"💾 Updating recommendations: {asset_id}")
            
            # Update recommendations in Meilisearch
            success = await self.meilisearch_adapter.update_recommendations(
                self.knowledge_index, asset_id, recommendations
            )
            
            if success:
                self.logger.info(f"✅ Recommendations updated: {asset_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Recommendation update failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_search_analytics(self,
                                 start_date: str = None,
                                 end_date: str = None) -> Dict[str, Any]:
        """
        Get search analytics from Meilisearch and Redis Graph.
        
        Combines analytics from multiple sources for comprehensive insights.
        """
        try:
            self.logger.info("📊 Getting search analytics")
            
            # Get Meilisearch analytics
            meilisearch_analytics = await self.meilisearch_adapter.get_search_analytics(
                self.knowledge_index, start_date, end_date
            )
            
            # Get Redis Graph analytics
            graph_stats = await self.redis_graph_adapter.get_graph_stats(self.knowledge_graph)
            
            # Get ArangoDB analytics
            arango_stats = await self.arango_adapter.get_database_statistics()
            
            # Combine analytics
            combined_analytics = {
                "searchAnalytics": meilisearch_analytics,
                "graphAnalytics": graph_stats,
                "persistentAnalytics": arango_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.info("✅ Search analytics retrieved")
            
            return combined_analytics
            
        except Exception as e:
            self.logger.error(f"❌ Search analytics failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def track_search_event(self,
                               query: str,
                               results_count: int) -> bool:
        """
        Track search event using Meilisearch.
        
        Records search events for analytics and recommendation improvement.
        """
        try:
            self.logger.info(f"📝 Tracking search event: {query}")
            
            # Track in Meilisearch
            user_id = None  # Default if not provided
            success = await self.meilisearch_adapter.track_search_event(
                self.knowledge_index, query, results_count, user_id
            )
            
            if success:
                self.logger.info(f"✅ Search event tracked: {query}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Search event tracking failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _merge_semantic_results(self,
                                    redis_results: List[Dict[str, Any]],
                                    arango_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge semantic search results from Redis Graph and ArangoDB."""
        try:
            # Combine and deduplicate results
            combined_results = []
            seen_ids = set()
            
            # Add Redis results
            for result in redis_results:
                if result.get('id') not in seen_ids:
                    combined_results.append(result)
                    seen_ids.add(result.get('id'))
            
            # Add ArangoDB results
            for result in arango_results:
                if result.get('id') not in seen_ids:
                    combined_results.append(result)
                    seen_ids.add(result.get('id'))
            
            # Sort by similarity score
            combined_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
            
            return combined_results
            
        except Exception as e:
            self.logger.error(f"❌ Semantic results merge failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _merge_relationship_results(self,
                                       redis_results: List[Dict[str, Any]],
                                       arango_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge relationship results from Redis Graph and ArangoDB."""
        try:
            # Combine and deduplicate results
            combined_results = []
            seen_ids = set()
            
            # Add Redis results
            for result in redis_results:
                if result.get('id') not in seen_ids:
                    combined_results.append(result)
                    seen_ids.add(result.get('id'))
            
            # Add ArangoDB results
            for result in arango_results:
                if result.get('id') not in seen_ids:
                    combined_results.append(result)
                    seen_ids.add(result.get('id'))
            
            return combined_results
            
        except Exception as e:
            self.logger.error(f"❌ Relationship results merge failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _merge_recommendation_results(self,
                                          meilisearch_recs: List[Dict[str, Any]],
                                          graph_recs: List[Dict[str, Any]],
                                          recommendation_type: str = "similar") -> List[Dict[str, Any]]:
        """Merge recommendation results from Meilisearch and Redis Graph."""
        try:
            # Combine and deduplicate recommendations
            combined_recs = []
            seen_ids = set()
            
            # Add Meilisearch recommendations
            for rec in meilisearch_recs:
                if rec.get('id') not in seen_ids:
                    combined_recs.append(rec)
                    seen_ids.add(rec.get('id'))
            
            # Add graph-based recommendations
            for rec in graph_recs:
                if rec.get('id') not in seen_ids:
                    combined_recs.append(rec)
                    seen_ids.add(rec.get('id'))
            
            # Sort by relevance score
            combined_recs.sort(key=lambda x: x.get('relevance', 0), reverse=True)
            
            return combined_recs
            
        except Exception as e:
            self.logger.error(f"❌ Recommendation results merge failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _track_search_analytics(self, query: str, results_count: int) -> None:
        """Track search analytics."""
        try:
            await self.track_search_event(query, results_count)
        except Exception as e:
            self.logger.error(f"❌ Search analytics tracking failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on knowledge discovery services."""
        try:
            # Check Meilisearch
            meilisearch_health = await self.meilisearch_adapter._get_health()
            
            # Check Redis Graph
            redis_health = await self.redis_graph_adapter._get_health()
            
            # Check ArangoDB
            arango_health = await self.arango_adapter._get_health()
            
            overall_health = all([meilisearch_health, redis_health, arango_health])
            
            health_status = {
                "overall_health": "healthy" if overall_health else "unhealthy",
                "meilisearch": "healthy" if meilisearch_health else "unhealthy",
                "redis_graph": "healthy" if redis_health else "unhealthy",
                "arango": "healthy" if arango_health else "unhealthy",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")

            raise  # Re-raise for service layer to handle
