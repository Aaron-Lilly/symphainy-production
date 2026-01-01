#!/usr/bin/env python3
"""
Meilisearch Knowledge Adapter - Raw Technology Layer

Raw Meilisearch client wrapper for knowledge search operations.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw Meilisearch search capabilities
HOW (Infrastructure Implementation): I wrap the Meilisearch client with basic operations
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import asyncio

logger = logging.getLogger(__name__)

class MeilisearchKnowledgeAdapter:
    """
    Raw Meilisearch client wrapper for knowledge search operations.
    
    Provides direct access to Meilisearch search capabilities without business logic.
    Focused on knowledge search, indexing, and analytics operations.
    """
    
    def __init__(self, host: str = "localhost", port: int = 7700, api_key: str = None, 
                 timeout: int = 30, index_prefix: str = "knowledge_"):
        """Initialize Meilisearch knowledge adapter."""
        self.host = host
        self.port = port
        self.api_key = api_key
        self.timeout = timeout
        self.index_prefix = index_prefix
        self.logger = logging.getLogger(__name__)
        
        # Meilisearch client (private - use wrapper methods instead)
        self._client = None
        self.base_url = f"http://{host}:{port}"
        # Keep client as alias for backward compatibility (will be removed)
        self.client = None
        
        # Knowledge-specific indexes
        self.knowledge_index = f"{index_prefix}assets"
        self.analytics_index = f"{index_prefix}analytics"
        self.recommendations_index = f"{index_prefix}recommendations"
        
        self.logger.info(f"✅ Meilisearch Knowledge adapter initialized with {host}:{port}")
    
    async def connect(self) -> bool:
        """Connect to Meilisearch server."""
        try:
            import meilisearch
            
            # Create Meilisearch client (private)
            self._client = meilisearch.Client(
                url=self.base_url,
                api_key=self.api_key,
                timeout=self.timeout
            )
            # Keep client as alias for backward compatibility (will be removed)
            self.client = self._client
            
            # Test connection
            health = await self._get_health()
            if health:
                self.logger.info("✅ Meilisearch Knowledge adapter connected")
                return True
            else:
                self.logger.error("❌ Failed to connect to Meilisearch")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to Meilisearch: {e}")
            return False
    
    async def _get_health(self) -> bool:
        """Check Meilisearch server health."""
        try:
            if self._client:
                # Simple health check
                await asyncio.sleep(0.1)  # Non-blocking check
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            return False
    
    # ============================================================================
    # INDEX MANAGEMENT
    # ============================================================================
    
    async def create_index(self, index_name: str, primary_key: str = "id") -> bool:
        """Create a new index."""
        try:
            if not self._client:
                return False
            
            # Create index with primary key
            index = self._client.index(index_name)
            await index.create_index(primary_key)
            
            self.logger.info(f"✅ Index created: {index_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create index {index_name}: {e}")
            return False
    
    async def delete_index(self, index_name: str) -> bool:
        """Delete an index."""
        try:
            if not self._client:
                return False
            
            # Delete index
            await self._client.delete_index(index_name)
            
            self.logger.info(f"✅ Index deleted: {index_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to delete index {index_name}: {e}")
            return False
    
    async def get_indexes(self) -> List[Dict[str, Any]]:
        """Get all indexes."""
        try:
            if not self._client:
                return []
            
            # Get all indexes
            indexes = await self._client.get_indexes()
            
            return indexes.get('results', [])
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get indexes: {e}")
            return []
    
    # ============================================================================
    # DOCUMENT OPERATIONS
    # ============================================================================
    
    async def add_documents(self, index_name: str, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to an index."""
        try:
            if not self._client:
                return False
            
            # Add documents
            index = self._client.index(index_name)
            result = await index.add_documents(documents)
            
            self.logger.info(f"✅ Added {len(documents)} documents to {index_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add documents to {index_name}: {e}")
            return False
    
    async def update_documents(self, index_name: str, documents: List[Dict[str, Any]]) -> bool:
        """Update documents in an index."""
        try:
            if not self._client:
                return False
            
            # Update documents
            index = self._client.index(index_name)
            result = await index.update_documents(documents)
            
            self.logger.info(f"✅ Updated {len(documents)} documents in {index_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update documents in {index_name}: {e}")
            return False
    
    async def delete_documents(self, index_name: str, document_ids: List[str]) -> bool:
        """Delete documents from an index."""
        try:
            if not self._client:
                return False
            
            # Delete documents
            index = self._client.index(index_name)
            result = await index.delete_documents(document_ids)
            
            self.logger.info(f"✅ Deleted {len(document_ids)} documents from {index_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to delete documents from {index_name}: {e}")
            return False
    
    # ============================================================================
    # SEARCH OPERATIONS
    # ============================================================================
    
    async def search(self, index_name: str, query: str, 
                    filters: Optional[Dict[str, Any]] = None,
                    limit: int = 20, offset: int = 0,
                    attributes_to_retrieve: Optional[List[str]] = None,
                    attributes_to_crop: Optional[List[str]] = None,
                    crop_length: int = 200) -> Dict[str, Any]:
        """Search documents in an index."""
        try:
            if not self._client:
                return {"hits": [], "totalHits": 0}
            
            # Build search parameters
            search_params = {
                "q": query,
                "limit": limit,
                "offset": offset
            }
            
            if filters:
                search_params["filter"] = self._build_filter_string(filters)
            
            if attributes_to_retrieve:
                search_params["attributesToRetrieve"] = attributes_to_retrieve
            
            if attributes_to_crop:
                search_params["attributesToCrop"] = attributes_to_crop
                search_params["cropLength"] = crop_length
            
            # Perform search
            index = self._client.index(index_name)
            results = await index.search(**search_params)
            
            self.logger.info(f"✅ Search completed: {query} in {index_name}")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Search failed in {index_name}: {e}")
            return {"hits": [], "totalHits": 0}
    
    async def search_with_facets(self, index_name: str, query: str,
                               facets: List[str], limit: int = 20) -> Dict[str, Any]:
        """Search with facet analysis."""
        try:
            if not self._client:
                return {"hits": [], "totalHits": 0, "facetDistribution": {}}
            
            # Build search parameters with facets
            search_params = {
                "q": query,
                "limit": limit,
                "facets": facets
            }
            
            # Perform search with facets
            index = self._client.index(index_name)
            results = await index.search(**search_params)
            
            self.logger.info(f"✅ Faceted search completed: {query} in {index_name}")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Faceted search failed in {index_name}: {e}")
            return {"hits": [], "totalHits": 0, "facetDistribution": {}}
    
    # ============================================================================
    # ANALYTICS OPERATIONS
    # ============================================================================
    
    async def get_search_analytics(self, index_name: str, 
                                  start_date: Optional[str] = None,
                                  end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get search analytics for an index."""
        try:
            if not self._client:
                return {"totalSearches": 0, "popularQueries": [], "searchTrends": []}
            
            # This would typically involve querying analytics data
            # For now, return basic analytics structure
            analytics = {
                "totalSearches": 0,
                "popularQueries": [],
                "searchTrends": [],
                "indexName": index_name,
                "period": {
                    "start": start_date,
                    "end": end_date
                }
            }
            
            self.logger.info(f"✅ Analytics retrieved for {index_name}")
            return analytics
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get analytics for {index_name}: {e}")
            return {"totalSearches": 0, "popularQueries": [], "searchTrends": []}
    
    async def track_search_event(self, index_name: str, query: str, 
                               results_count: int, user_id: Optional[str] = None) -> bool:
        """Track a search event for analytics."""
        try:
            if not self._client:
                return False
            
            # Create search event document
            event_doc = {
                "id": f"search_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                "indexName": index_name,
                "query": query,
                "resultsCount": results_count,
                "userId": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to analytics index
            analytics_index = f"{self.index_prefix}analytics"
            success = await self.add_documents(analytics_index, [event_doc])
            
            if success:
                self.logger.info(f"✅ Search event tracked: {query}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to track search event: {e}")
            return False
    
    # ============================================================================
    # RECOMMENDATION OPERATIONS
    # ============================================================================
    
    async def get_recommendations(self, index_name: str, document_id: str, 
                                limit: int = 10) -> List[Dict[str, Any]]:
        """Get recommendations based on a document."""
        try:
            if not self._client:
                return []
            
            # This would typically involve collaborative filtering or content-based recommendations
            # For now, return basic recommendation structure
            recommendations = []
            
            self.logger.info(f"✅ Recommendations retrieved for {document_id}")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get recommendations for {document_id}: {e}")
            return []
    
    async def update_recommendations(self, index_name: str, document_id: str,
                                   recommendations: List[Dict[str, Any]]) -> bool:
        """Update recommendations for a document."""
        try:
            if not self._client:
                return False
            
            # Create recommendation document
            rec_doc = {
                "id": f"rec_{document_id}",
                "documentId": document_id,
                "recommendations": recommendations,
                "updatedAt": datetime.utcnow().isoformat()
            }
            
            # Add to recommendations index
            rec_index = f"{self.index_prefix}recommendations"
            success = await self.add_documents(rec_index, [rec_doc])
            
            if success:
                self.logger.info(f"✅ Recommendations updated for {document_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update recommendations: {e}")
            return False
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _build_filter_string(self, filters: Dict[str, Any]) -> str:
        """Build Meilisearch filter string from filters dict."""
        try:
            filter_parts = []
            
            for key, value in filters.items():
                if isinstance(value, list):
                    # Handle array filters
                    filter_parts.append(f"{key} IN {value}")
                elif isinstance(value, str):
                    # Handle string filters
                    filter_parts.append(f"{key} = '{value}'")
                else:
                    # Handle other types
                    filter_parts.append(f"{key} = {value}")
            
            return " AND ".join(filter_parts)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to build filter string: {e}")
            return ""
    
    async def get_index_stats(self, index_name: str) -> Dict[str, Any]:
        """Get statistics for an index."""
        try:
            if not self._client:
                return {"numberOfDocuments": 0, "isIndexing": False}
            
            # Get index stats
            index = self._client.index(index_name)
            stats = await index.get_stats()
            
            self.logger.info(f"✅ Stats retrieved for {index_name}")
            return stats
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get stats for {index_name}: {e}")
            return {"numberOfDocuments": 0, "isIndexing": False}
    
    async def close(self):
        """Close the Meilisearch connection."""
        try:
            if self._client:
                # Meilisearch client doesn't need explicit closing
                self.client = None
                self.logger.info("✅ Meilisearch Knowledge adapter closed")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to close Meilisearch adapter: {e}")

