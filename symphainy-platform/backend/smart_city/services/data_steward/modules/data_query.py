#!/usr/bin/env python3
"""
Data Steward Service - Data Query Module

Micro-module for querying all data types:
- Platform data queries (before semantic layer)
- Client data queries (before semantic layer)
- Parsed data queries (before semantic layer)
- Semantic layer queries (via ContentMetadataAbstraction)

WHAT: I provide query capabilities for all data types at all stages
HOW: I use file_management_abstraction, content_metadata_abstraction, and ArangoAdapter
     to query platform, client, parsed, and semantic data
"""

import logging
from typing import Any, Dict, Optional, List
from datetime import datetime


class DataQuery:
    """Data query module for all data types."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def query_platform_files(
        self,
        filters: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query platform files."""
        try:
            # Get file management abstraction
            file_management = self.service.file_management_abstraction
            if not file_management:
                raise ValueError("File management abstraction not available")
            
            # Add platform filter (platform files have no tenant_id or tenant_id is null)
            query_filters = {**filters, "tenant_id": None}
            
            # Query files with filters
            files = await file_management.list_files(filters=query_filters)
            
            return {
                "success": True,
                "files": files if isinstance(files, list) else [],
                "count": len(files) if isinstance(files, list) else 0
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to query platform files: {e}")
            raise
    
    async def query_platform_parsed_data(
        self,
        filters: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query platform parsed data."""
        try:
            # Real implementation: Query parsed data store
            # This would use ArangoAdapter to query parsed data collection
            # For now, return empty result (will be implemented when parsed data storage is defined)
            parsed_data = await self._query_parsed_data_store(filters, "platform")
            
            return {
                "success": True,
                "parsed_data": parsed_data,
                "count": len(parsed_data) if isinstance(parsed_data, list) else 0
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to query platform parsed data: {e}")
            raise
    
    async def query_client_files(
        self,
        filters: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query client files."""
        try:
            # Validate tenant access
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
                        # Add tenant filter
                        filters["tenant_id"] = tenant_id
            
            # Get file management abstraction
            file_management = self.service.file_management_abstraction
            if not file_management:
                raise ValueError("File management abstraction not available")
            
            # Query files with filters
            files = await file_management.list_files(filters=filters)
            
            return {
                "success": True,
                "files": files if isinstance(files, list) else [],
                "count": len(files) if isinstance(files, list) else 0
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to query client files: {e}")
            raise
    
    async def query_client_parsed_data(
        self,
        filters: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query client parsed data."""
        try:
            # Validate tenant access
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
                        # Add tenant filter
                        filters["tenant_id"] = tenant_id
            
            # Query parsed data store
            parsed_data = await self._query_parsed_data_store(filters, "client")
            
            return {
                "success": True,
                "parsed_data": parsed_data,
                "count": len(parsed_data) if isinstance(parsed_data, list) else 0
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to query client parsed data: {e}")
            raise
    
    async def query_semantic_embeddings(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query semantic embeddings."""
        try:
            # Get ContentMetadataAbstraction
            content_metadata = self.service.content_metadata_abstraction
            if not content_metadata:
                raise ValueError("Content metadata abstraction not available")
            
            # Query semantic embeddings
            embeddings = await content_metadata.get_semantic_embeddings(content_id)
            
            return {
                "success": True,
                "content_id": content_id,
                "embeddings": embeddings if isinstance(embeddings, list) else [],
                "count": len(embeddings) if isinstance(embeddings, list) else 0
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to query semantic embeddings: {e}")
            raise
    
    async def query_semantic_graph(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query semantic graph."""
        try:
            # Get ContentMetadataAbstraction
            content_metadata = self.service.content_metadata_abstraction
            if not content_metadata:
                raise ValueError("Content metadata abstraction not available")
            
            # Query semantic graph
            graph = await content_metadata.get_semantic_graph(content_id)
            
            nodes = graph.get("nodes", []) if isinstance(graph, dict) else []
            edges = graph.get("edges", []) if isinstance(graph, dict) else []
            
            return {
                "success": True,
                "content_id": content_id,
                "graph": graph,
                "nodes_count": len(nodes),
                "edges_count": len(edges)
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to query semantic graph: {e}")
            raise
    
    async def query_by_semantic_id(
        self,
        semantic_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query files/data by semantic ID."""
        try:
            # Get ContentMetadataAbstraction
            content_metadata = self.service.content_metadata_abstraction
            if not content_metadata:
                raise ValueError("Content metadata abstraction not available")
            
            # Query ArangoDB for embeddings matching semantic_id
            # Real implementation: Query structured_embeddings collection
            arango_adapter = self.service.get_abstraction("ArangoAdapter")
            if not arango_adapter:
                raise ValueError("Arango adapter not available")
            
            # Query embeddings by semantic_id
            embeddings = await arango_adapter.find_documents(
                collection="structured_embeddings",
                filter_conditions={"semantic_id": semantic_id}
            )
            
            # Get associated content_ids
            content_ids = list(set([
                emb.get("content_id")
                for emb in embeddings
                if emb.get("content_id")
            ]))
            
            return {
                "success": True,
                "semantic_id": semantic_id,
                "embeddings": embeddings if isinstance(embeddings, list) else [],
                "content_ids": content_ids,
                "count": len(embeddings) if isinstance(embeddings, list) else 0
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to query by semantic ID: {e}")
            raise
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    async def _query_parsed_data_store(
        self,
        filters: Dict[str, Any],
        data_scope: str
    ) -> List[Dict[str, Any]]:
        """Query parsed data store."""
        # Real implementation: Query ArangoDB or other storage
        # This would use ArangoAdapter to query parsed data collection
        # For now, return empty list (will be implemented when parsed data storage is defined)
        return []




