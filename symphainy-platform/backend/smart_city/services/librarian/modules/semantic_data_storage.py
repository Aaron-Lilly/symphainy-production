#!/usr/bin/env python3
"""
Librarian Service - Semantic Data Storage Module

Micro-module for semantic data storage operations (embeddings, semantic graphs) using SemanticDataAbstraction.
"""

from typing import Any, Dict, Optional, List
from datetime import datetime


class SemanticDataStorage:
    """Semantic data storage module for Librarian service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def store_embeddings(
        self,
        content_id: str,
        file_id: str,
        embeddings: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store semantic embeddings using SemanticDataAbstraction.
        
        Args:
            content_id: Content metadata ID
            file_id: File UUID
            embeddings: List of embedding dictionaries
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dict with storage result
        """
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "store_embeddings_start",
            success=True,
            details={"content_id": content_id, "file_id": file_id, "embedding_count": len(embeddings)}
        )
        
        try:
            # Security validation
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "knowledge_management", "write"):
                        await self.service.record_health_metric("store_embeddings_access_denied", 1.0, {"content_id": content_id})
                        await self.service.log_operation_with_telemetry("store_embeddings_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to store embeddings")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            if not self.service.semantic_data_abstraction:
                raise Exception("Semantic Data Abstraction not available")
            
            # Store embeddings via SemanticDataAbstraction
            result = await self.service.semantic_data_abstraction.store_semantic_embeddings(
                content_id=content_id,
                file_id=file_id,
                embeddings=embeddings,
                user_context=user_context
            )
            
            # Update content metadata flags (has_embeddings = True, embedding_count)
            if self.service.content_metadata_abstraction:
                await self.service.content_metadata_abstraction.update_content_metadata(
                    content_id,
                    {
                        "has_embeddings": True,
                        "embedding_count": len(embeddings),
                        "updated_at": datetime.utcnow().isoformat()
                    }
                )
            
            # Record health metric
            await self.service.record_health_metric(
                "embeddings_stored",
                1.0,
                {
                    "content_id": content_id,
                    "file_id": file_id,
                    "embedding_count": len(embeddings)
                }
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "store_embeddings_complete",
                success=True,
                details={
                    "content_id": content_id,
                    "file_id": file_id,
                    "embedding_count": len(embeddings)
                }
            )
            
            return {
                "success": True,
                "content_id": content_id,
                "file_id": file_id,
                "stored_count": result.get("stored_count", len(embeddings)),
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store embeddings: {e}")
            await self.service.log_operation_with_telemetry(
                "store_embeddings_complete",
                success=False,
                details={"error": str(e)}
            )
            raise
    
    async def get_embeddings(
        self,
        content_id: str,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get semantic embeddings with filtering.
        
        Args:
            content_id: Content metadata ID
            filters: Optional filters (column_name, semantic_id, etc.)
            user_context: Optional user context for security and tenant validation
            
        Returns:
            List of embedding dictionaries
        """
        try:
            # Security validation
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "knowledge_management", "read"):
                        raise PermissionError("Access denied: insufficient permissions to get embeddings")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            if not self.service.semantic_data_abstraction:
                raise Exception("Semantic Data Abstraction not available")
            
            result = await self.service.semantic_data_abstraction.get_semantic_embeddings(
                content_id=content_id,
                filters=filters,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get embeddings for {content_id}: {e}")
            return []
    
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
            user_context: Optional user context for security and tenant validation
            
        Returns:
            List of matching embedding dictionaries with similarity scores
        """
        try:
            # Security validation
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "knowledge_management", "read"):
                        raise PermissionError("Access denied: insufficient permissions to perform vector search")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            if not self.service.semantic_data_abstraction:
                raise Exception("Semantic Data Abstraction not available")
            
            result = await self.service.semantic_data_abstraction.vector_search(
                query_embedding=query_embedding,
                limit=limit,
                filters=filters,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to perform vector search: {e}")
            return []
    
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
            semantic_graph: Dictionary with 'nodes' and 'edges' lists
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dict with storage result
        """
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "store_semantic_graph_start",
            success=True,
            details={"content_id": content_id, "file_id": file_id}
        )
        
        try:
            # Security validation
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "knowledge_management", "write"):
                        await self.service.record_health_metric("store_semantic_graph_access_denied", 1.0, {"content_id": content_id})
                        await self.service.log_operation_with_telemetry("store_semantic_graph_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to store semantic graph")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            if not self.service.semantic_data_abstraction:
                raise Exception("Semantic Data Abstraction not available")
            
            # Store semantic graph via SemanticDataAbstraction
            result = await self.service.semantic_data_abstraction.store_semantic_graph(
                content_id=content_id,
                file_id=file_id,
                semantic_graph=semantic_graph,
                user_context=user_context
            )
            
            # Update content metadata flags (has_semantic_graph = True, semantic_graph_node_count)
            if self.service.content_metadata_abstraction:
                node_count = result.get("stored_nodes", 0)
                await self.service.content_metadata_abstraction.update_content_metadata(
                    content_id,
                    {
                        "has_semantic_graph": True,
                        "semantic_graph_node_count": node_count,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                )
            
            # Record health metric
            await self.service.record_health_metric(
                "semantic_graph_stored",
                1.0,
                {
                    "content_id": content_id,
                    "file_id": file_id,
                    "node_count": result.get("stored_nodes", 0),
                    "edge_count": result.get("stored_edges", 0)
                }
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "store_semantic_graph_complete",
                success=True,
                details={
                    "content_id": content_id,
                    "file_id": file_id,
                    "node_count": result.get("stored_nodes", 0),
                    "edge_count": result.get("stored_edges", 0)
                }
            )
            
            return {
                "success": True,
                "content_id": content_id,
                "file_id": file_id,
                "stored_nodes": result.get("stored_nodes", 0),
                "stored_edges": result.get("stored_edges", 0),
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store semantic graph: {e}")
            await self.service.log_operation_with_telemetry(
                "store_semantic_graph_complete",
                success=False,
                details={"error": str(e)}
            )
            raise
    
    async def get_semantic_graph(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get semantic graph for content.
        
        Args:
            content_id: Content metadata ID
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dictionary with 'nodes' and 'edges' lists
        """
        try:
            # Security validation
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "knowledge_management", "read"):
                        raise PermissionError("Access denied: insufficient permissions to get semantic graph")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            if not self.service.semantic_data_abstraction:
                raise Exception("Semantic Data Abstraction not available")
            
            result = await self.service.semantic_data_abstraction.get_semantic_graph(
                content_id=content_id,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get semantic graph for {content_id}: {e}")
            return {"nodes": [], "edges": []}



