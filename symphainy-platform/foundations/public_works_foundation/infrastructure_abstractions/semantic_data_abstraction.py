#!/usr/bin/env python3
"""
Semantic Data Abstraction - Business Logic Implementation

Implements semantic data operations (embeddings, semantic graphs) with business logic.
This is Layer 3 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I manage semantic data operations with business logic
HOW (Infrastructure Implementation): I implement business rules for semantic data storage and retrieval
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..abstraction_contracts.semantic_data_protocol import SemanticDataProtocol

logger = logging.getLogger(__name__)

class SemanticDataAbstraction(SemanticDataProtocol):
    """
    Semantic data abstraction with business logic.
    
    Implements semantic data operations (embeddings, semantic graphs) with business rules,
    validation, and enhanced functionality for the platform.
    """
    
    def __init__(self, arango_adapter, config_adapter, di_container=None):
        """Initialize semantic data abstraction."""
        self.arango_adapter = arango_adapter
        self.config_adapter = config_adapter
        self.di_container = di_container
        self.service_name = "semantic_data_abstraction"
        
        # Semantic data collections for ArangoDB
        self.structured_embeddings_collection = "structured_embeddings"
        self.semantic_graph_nodes_collection = "semantic_graph_nodes"
        self.semantic_graph_edges_collection = "semantic_graph_edges"
        self.correlation_maps_collection = "correlation_maps"  # NEW: For hybrid parsing
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Semantic Data Abstraction initialized")
    
    # ============================================================================
    # EMBEDDING OPERATIONS WITH BUSINESS LOGIC
    # ============================================================================
    
    async def store_semantic_embeddings(
        self,
        content_id: str,
        file_id: str,
        embeddings: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store semantic embeddings for structured content with business logic validation.
        
        Enhanced storage includes both embedding vectors and metadata for preview reconstruction:
        - Embeddings: metadata_embedding, meaning_embedding, samples_embedding (vectors)
        - Metadata: data_type, semantic_meaning (text), sample_values (text array), 
          row_count, column_position, semantic_model_recommendation
        
        Args:
            content_id: Content metadata ID
            file_id: File UUID
            embeddings: List of embedding dictionaries with:
                - column_name (required)
                - metadata_embedding, meaning_embedding, samples_embedding (at least one required)
                - semantic_id (optional)
                - data_type (optional, NEW: for preview reconstruction)
                - semantic_meaning (optional, NEW: meaning as text, not just embedding)
                - sample_values (optional, NEW: samples as text array, not just embedding)
                - row_count (optional, NEW: total row count)
                - column_position (optional, NEW: column order)
                - semantic_model_recommendation (optional, NEW: recommendation object)
            user_context: Optional user context for tenant_id
        
        Returns:
            Storage result with count of stored embeddings
        """
        try:
            # Validate required fields
            if not content_id or not file_id:
                raise ValueError("content_id and file_id are required")
            
            if not embeddings or len(embeddings) == 0:
                raise ValueError("embeddings list cannot be empty")
            
            # Validate embedding structure
            for emb in embeddings:
                if "column_name" not in emb:
                    raise ValueError("Each embedding must have a column_name")
                if "metadata_embedding" not in emb and "meaning_embedding" not in emb:
                    raise ValueError("Each embedding must have at least one embedding vector")
            
            stored_count = 0
            tenant_id = user_context.get("tenant_id") if user_context else None
            
            for emb in embeddings:
                # Get parsed_file_id and embedding_file_id from embedding document if available
                parsed_file_id = emb.get("parsed_file_id")
                embedding_file_id = emb.get("embedding_file_id")  # ✅ NEW: Get embedding_file_id
                
                embedding_doc = {
                    "_key": f"emb_{file_id}_{emb.get('column_name', emb.get('chunk_index', 'unknown'))}_{uuid.uuid4().hex[:8]}",
                    "content_id": content_id,
                    "file_id": file_id,
                    "parsed_file_id": parsed_file_id,  # ✅ Store parsed_file_id for matching
                    "embedding_file_id": embedding_file_id,  # ✅ NEW: Store embedding_file_id for direct lookup
                    "column_name": emb.get("column_name"),
                    # Embeddings (vectors)
                    "metadata_embedding": emb.get("metadata_embedding"),
                    "meaning_embedding": emb.get("meaning_embedding"),
                    "samples_embedding": emb.get("samples_embedding"),
                    "chunk_embedding": emb.get("chunk_embedding"),  # For document chunks
                    # Metadata (text - for preview reconstruction)
                    "semantic_id": emb.get("semantic_id"),
                    "data_type": emb.get("data_type"),  # ✅ NEW: Store data type (string, int, float, etc.)
                    "semantic_meaning": emb.get("semantic_meaning"),  # ✅ NEW: Store meaning as text (not just embedding)
                    "sample_values": emb.get("sample_values"),  # ✅ NEW: Store samples as text array (not just embedding)
                    "row_count": emb.get("row_count"),  # ✅ NEW: Store row count
                    "column_position": emb.get("column_position"),  # ✅ NEW: Store column order
                    "semantic_model_recommendation": emb.get("semantic_model_recommendation"),  # ✅ NEW: Store recommendation object
                    # Document chunk metadata
                    "chunk_index": emb.get("chunk_index"),
                    "chunk_text": emb.get("chunk_text"),
                    "chunk_metadata": emb.get("chunk_metadata"),
                    "total_chunks": emb.get("total_chunks"),
                    "content_type": emb.get("content_type"),
                    "format_type": emb.get("format_type"),
                    "embedding_type": emb.get("embedding_type"),
                    "tenant_id": tenant_id,
                    "created_at": datetime.utcnow().isoformat()
                }
                await self.arango_adapter.create_document(
                    self.structured_embeddings_collection,
                    embedding_doc
                )
                stored_count += 1
            
            self.logger.info(f"✅ Stored {stored_count} semantic embeddings for content {content_id}")
            
            return {
                "success": True,
                "stored_count": stored_count,
                "content_id": content_id,
                "file_id": file_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store semantic embeddings for {content_id}: {e}")
            raise
    
    async def get_semantic_embeddings(
        self,
        content_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get semantic embeddings with filtering and business logic validation.
        
        Args:
            content_id: Optional content metadata ID (if None, queries all embeddings)
            filters: Optional filters (column_name, semantic_id, file_id, parsed_file_id, etc.)
            user_context: Optional user context for tenant_id
        
        Returns:
            List of embedding dictionaries
        """
        try:
            # Build filter conditions
            # If content_id is None, query all embeddings (don't filter by content_id)
            filter_conditions = {}
            if content_id is not None:
                filter_conditions["content_id"] = content_id
            
            if filters:
                filter_conditions.update(filters)
            
            # Add tenant filtering if provided
            if user_context and user_context.get("tenant_id"):
                filter_conditions["tenant_id"] = user_context.get("tenant_id")
            
            print(f"[SEMANTIC_DATA] 🔍 Querying ArangoDB with filter_conditions: {filter_conditions}")
            self.logger.info(f"🔍 Querying ArangoDB with filter_conditions: {filter_conditions}")
            result = await self.arango_adapter.find_documents(
                self.structured_embeddings_collection,
                filter_conditions=filter_conditions
            )
            
            print(f"[SEMANTIC_DATA] ✅ Retrieved {len(result)} semantic embeddings from ArangoDB")
            if content_id:
                self.logger.info(f"✅ Retrieved {len(result)} semantic embeddings for content {content_id}")
            else:
                self.logger.info(f"✅ Retrieved {len(result)} semantic embeddings (all content)")
            
            # Debug: Log filter conditions and first result if any
            if filter_conditions:
                self.logger.info(f"🔍 Query filter conditions: {filter_conditions}")
            if result and len(result) > 0:
                print(f"[SEMANTIC_DATA] 🔍 First embedding keys: {list(result[0].keys())}")
                print(f"[SEMANTIC_DATA] 🔍 First embedding: file_id={result[0].get('file_id')}, parsed_file_id={result[0].get('parsed_file_id')}, content_id={result[0].get('content_id')}")
                self.logger.info(f"🔍 First embedding keys: {list(result[0].keys())}")
                self.logger.info(f"🔍 First embedding: file_id={result[0].get('file_id')}, parsed_file_id={result[0].get('parsed_file_id')}, content_id={result[0].get('content_id')}")
            else:
                print(f"[SEMANTIC_DATA] ⚠️ No embeddings found in ArangoDB with filters: {filter_conditions}")
                self.logger.warning(f"⚠️ No embeddings found in ArangoDB with filters: {filter_conditions}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get semantic embeddings for {content_id}: {e}")
            raise
    
    async def query_by_semantic_id(
        self,
        semantic_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query embeddings by semantic ID with business logic validation.
        
        Args:
            semantic_id: Semantic ID to query
            user_context: Optional user context for tenant_id
        
        Returns:
            List of matching embedding dictionaries
        """
        try:
            filter_conditions = {"semantic_id": semantic_id}
            
            # Add tenant filtering if provided
            if user_context and user_context.get("tenant_id"):
                filter_conditions["tenant_id"] = user_context.get("tenant_id")
            
            result = await self.arango_adapter.find_documents(
                self.structured_embeddings_collection,
                filter_conditions=filter_conditions
            )
            
            self.logger.debug(f"✅ Retrieved {len(result)} embeddings for semantic_id {semantic_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to query embeddings by semantic_id {semantic_id}: {e}")
            raise
    
    async def vector_search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Vector similarity search with business logic validation.
        
        Args:
            query_embedding: Query vector (embedding)
            limit: Maximum number of results
            filters: Optional filters (content_id, file_id, column_name, etc.)
            user_context: Optional user context for tenant_id
        
        Returns:
            List of matching embedding dictionaries with similarity scores
        """
        try:
            # Validate query embedding
            if not query_embedding or len(query_embedding) == 0:
                raise ValueError("query_embedding cannot be empty")
            
            # Build AQL query for vector similarity search
            # Note: This is a simplified version - actual implementation may use
            # ArangoDB's vector search capabilities or external vector database
            filter_conditions = filters or {}
            
            # Add tenant filtering if provided
            if user_context and user_context.get("tenant_id"):
                filter_conditions["tenant_id"] = user_context.get("tenant_id")
            
            # For now, return filtered results (vector similarity will be implemented
            # when ArangoDB vector search is configured)
            result = await self.arango_adapter.find_documents(
                self.structured_embeddings_collection,
                filter_conditions=filter_conditions,
                limit=limit
            )
            
            self.logger.debug(f"✅ Vector search returned {len(result)} results")
            
            # TODO: Add actual vector similarity calculation when ArangoDB vector search is available
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to perform vector search: {e}")
            raise
    
    # ============================================================================
    # SEMANTIC GRAPH OPERATIONS WITH BUSINESS LOGIC
    # ============================================================================
    
    async def store_semantic_graph(
        self,
        content_id: str,
        file_id: str,
        semantic_graph: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store semantic graph for unstructured content with business logic validation.
        
        Args:
            content_id: Content metadata ID
            file_id: File UUID
            semantic_graph: Dictionary with 'nodes' and 'edges' lists
            user_context: Optional user context for tenant_id
        
        Returns:
            Storage result with counts of stored nodes and edges
        """
        try:
            # Validate required fields
            if not content_id or not file_id:
                raise ValueError("content_id and file_id are required")
            
            if "nodes" not in semantic_graph and "edges" not in semantic_graph:
                raise ValueError("semantic_graph must contain 'nodes' and/or 'edges'")
            
            nodes = semantic_graph.get("nodes", [])
            edges = semantic_graph.get("edges", [])
            tenant_id = user_context.get("tenant_id") if user_context else None
            
            # Store nodes
            stored_nodes = 0
            for node in nodes:
                node_doc = {
                    "_key": f"node_{file_id}_{node.get('entity_id', 'unknown')}_{uuid.uuid4().hex[:8]}",
                    "content_id": content_id,
                    "file_id": file_id,
                    "entity_id": node.get("entity_id"),
                    "entity_name": node.get("entity_name"),
                    "entity_text": node.get("entity_text"),
                    "entity_type": node.get("entity_type"),
                    "semantic_id": node.get("semantic_id"),
                    "embedding": node.get("embedding"),
                    "confidence": node.get("confidence"),
                    "confidence_breakdown": node.get("confidence_breakdown"),
                    "tenant_id": tenant_id,
                    "created_at": datetime.utcnow().isoformat()
                }
                await self.arango_adapter.create_document(
                    self.semantic_graph_nodes_collection,
                    node_doc
                )
                stored_nodes += 1
            
            # Store edges
            stored_edges = 0
            for edge in edges:
                # Get source and target node keys for _from and _to
                source_entity_id = edge.get('source_entity_id', 'unknown')
                target_entity_id = edge.get('target_entity_id', 'unknown')
                source_node_key = f"node_{file_id}_{source_entity_id}"
                target_node_key = f"node_{file_id}_{target_entity_id}"
                
                edge_doc = {
                    "_key": f"edge_{file_id}_{source_entity_id}_{target_entity_id}_{uuid.uuid4().hex[:8]}",
                    "_from": f"{self.semantic_graph_nodes_collection}/{source_node_key}",
                    "_to": f"{self.semantic_graph_nodes_collection}/{target_node_key}",
                    "content_id": content_id,
                    "file_id": file_id,
                    "source_entity_id": source_entity_id,
                    "target_entity_id": target_entity_id,
                    "relationship_type": edge.get("relationship_type"),
                    "confidence": edge.get("confidence"),
                    "tenant_id": tenant_id,
                    "created_at": datetime.utcnow().isoformat()
                }
                await self.arango_adapter.create_document(
                    self.semantic_graph_edges_collection,
                    edge_doc
                )
                stored_edges += 1
            
            self.logger.info(f"✅ Stored semantic graph for content {content_id}: {stored_nodes} nodes, {stored_edges} edges")
            
            return {
                "success": True,
                "stored_nodes": stored_nodes,
                "stored_edges": stored_edges,
                "content_id": content_id,
                "file_id": file_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store semantic graph for {content_id}: {e}")
            raise
    
    async def get_semantic_graph(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get semantic graph for content with business logic validation.
        
        Args:
            content_id: Content metadata ID
            user_context: Optional user context for tenant_id
        
        Returns:
            Dictionary with 'nodes' and 'edges' lists
        """
        try:
            filter_conditions = {"content_id": content_id}
            
            # Add tenant filtering if provided
            if user_context and user_context.get("tenant_id"):
                filter_conditions["tenant_id"] = user_context.get("tenant_id")
            
            # Get nodes
            nodes = await self.arango_adapter.find_documents(
                self.semantic_graph_nodes_collection,
                filter_conditions=filter_conditions
            )
            
            # Get edges
            edges = await self.arango_adapter.find_documents(
                self.semantic_graph_edges_collection,
                filter_conditions=filter_conditions
            )
            
            self.logger.debug(f"✅ Retrieved semantic graph for content {content_id}: {len(nodes)} nodes, {len(edges)} edges")
            
            return {
                "nodes": nodes,
                "edges": edges
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get semantic graph for {content_id}: {e}")
            raise
    
    # ============================================================================
    # CORRELATION MAP OPERATIONS (NEW: For hybrid parsing)
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
        try:
            # Validate required fields
            if not content_id or not file_id:
                raise ValueError("content_id and file_id are required")
            
            tenant_id = user_context.get("tenant_id") if user_context else None
            
            correlation_doc = {
                "_key": f"corr_{file_id}_{uuid.uuid4().hex[:8]}",
                "content_id": content_id,
                "file_id": file_id,
                "correlation_map": correlation_map,
                "tenant_id": tenant_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = await self.arango_adapter.create_document(
                self.correlation_maps_collection,
                correlation_doc
            )
            
            self.logger.info(f"✅ Stored correlation map for content {content_id}")
            
            return {
                "success": True,
                "correlation_map_id": result.get("_key"),
                "content_id": content_id,
                "file_id": file_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store correlation map for {content_id}: {e}")
            raise
    
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
        try:
            filter_conditions = {"content_id": content_id}
            
            # Add tenant filtering if provided
            if user_context and user_context.get("tenant_id"):
                filter_conditions["tenant_id"] = user_context.get("tenant_id")
            
            result = await self.arango_adapter.find_documents(
                self.correlation_maps_collection,
                filter_conditions=filter_conditions,
                limit=1
            )
            
            if result and len(result) > 0:
                correlation_map = result[0]
                self.logger.debug(f"✅ Retrieved correlation map for content {content_id}")
                return correlation_map.get("correlation_map", {})
            else:
                self.logger.warning(f"⚠️ No correlation map found for content {content_id}")
                return {}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get correlation map for {content_id}: {e}")
            raise
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health with business logic validation."""
        try:
            result = await self.arango_adapter.health_check()
            
            # Add business logic health checks
            if result.get("status") == "healthy":
                # Test semantic data operations
                test_embeddings = await self.arango_adapter.find_documents(
                    self.structured_embeddings_collection,
                    filter_conditions={},
                    limit=1
                )
                result["business_logic"] = "operational"
                result["test_results"] = {
                    "embeddings_test": len(test_embeddings),
                    "collections": [
                        self.structured_embeddings_collection,
                        self.semantic_graph_nodes_collection,
                        self.semantic_graph_edges_collection,
                        self.correlation_maps_collection
                    ]
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            raise



