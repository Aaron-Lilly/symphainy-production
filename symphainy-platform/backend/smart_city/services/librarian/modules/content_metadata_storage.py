#!/usr/bin/env python3
"""
Librarian Service - Content Metadata Storage Module

Micro-module for content metadata storage operations using ContentMetadataAbstraction.
"""

import uuid
from typing import Any, Dict, Optional
from datetime import datetime


class ContentMetadataStorage:
    """Content metadata storage module for Librarian service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def store_content_metadata(
        self,
        file_id: str,
        parsed_file_id: str,
        content_metadata: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store content metadata using ContentMetadataAbstraction.
        
        Args:
            file_id: Original file UUID
            parsed_file_id: Parsed file ID (from parsed_data_files table)
            content_metadata: Extracted content metadata (schema, columns, etc.)
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dict with content_id and metadata
        """
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "store_content_metadata_start",
            success=True,
            details={"file_id": file_id, "parsed_file_id": parsed_file_id}
        )
        
        try:
            # Security validation
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "knowledge_management", "write"):
                        await self.service.record_health_metric("store_content_metadata_access_denied", 1.0, {"file_id": file_id})
                        await self.service.log_operation_with_telemetry("store_content_metadata_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to store content metadata")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            if not self.service.content_metadata_abstraction:
                raise Exception("Content Metadata Abstraction not available")
            
            # Generate content ID if not provided
            content_id = content_metadata.get("content_id", str(uuid.uuid4()))
            
            # Prepare content metadata document
            content_metadata_doc = {
                "content_id": content_id,
                "file_uuid": file_id,
                "file_id": file_id,  # Alias for consistency
                "parsed_file_id": parsed_file_id,
                "content_type": content_metadata.get("content_type", "unstructured"),
                "structure_type": content_metadata.get("structure_type", "unknown"),
                "schema": content_metadata.get("schema", {}),
                "columns": content_metadata.get("columns", []),
                "data_types": content_metadata.get("data_types", {}),
                "row_count": content_metadata.get("row_count"),
                "column_count": content_metadata.get("column_count"),
                "chunk_count": content_metadata.get("chunk_count"),
                "word_count": content_metadata.get("word_count"),
                "parsing_method": content_metadata.get("parsing_method", "unknown"),
                "parsing_confidence": content_metadata.get("parsing_confidence", 1.0),
                "has_embeddings": False,  # Will be updated when embeddings are stored
                "has_semantic_graph": False,  # Will be updated when semantic graph is stored
                "embedding_count": 0,  # Will be updated when embeddings are stored
                "semantic_graph_node_count": 0,  # Will be updated when semantic graph is stored
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Store via ContentMetadataAbstraction
            result = await self.service.content_metadata_abstraction.create_content_metadata(content_metadata_doc)
            
            # Record health metric
            await self.service.record_health_metric(
                "content_metadata_stored",
                1.0,
                {
                    "file_id": file_id,
                    "content_id": content_id,
                    "content_type": content_metadata_doc["content_type"]
                }
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "store_content_metadata_complete",
                success=True,
                details={
                    "file_id": file_id,
                    "content_id": content_id,
                    "content_type": content_metadata_doc["content_type"]
                }
            )
            
            return {
                "success": True,
                "content_id": content_id,
                "file_id": file_id,
                "parsed_file_id": parsed_file_id,
                "metadata": result
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store content metadata: {e}")
            await self.service.log_operation_with_telemetry(
                "store_content_metadata_complete",
                success=False,
                details={"error": str(e)}
            )
            raise
    
    async def get_content_metadata(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get content metadata by content_id.
        
        Args:
            content_id: Content metadata ID
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dict with content metadata, or None if not found
        """
        try:
            # Security validation
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "knowledge_management", "read"):
                        raise PermissionError("Access denied: insufficient permissions to get content metadata")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            if not self.service.content_metadata_abstraction:
                raise Exception("Content Metadata Abstraction not available")
            
            result = await self.service.content_metadata_abstraction.get_content_metadata(content_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get content metadata {content_id}: {e}")
            return None
    
    async def update_content_metadata(
        self,
        content_id: str,
        updates: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update content metadata.
        
        Args:
            content_id: Content metadata ID
            updates: Dictionary of fields to update
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dict with updated content metadata
        """
        try:
            # Security validation
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "knowledge_management", "write"):
                        raise PermissionError("Access denied: insufficient permissions to update content metadata")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            if not self.service.content_metadata_abstraction:
                raise Exception("Content Metadata Abstraction not available")
            
            result = await self.service.content_metadata_abstraction.update_content_metadata(content_id, updates)
            
            self.logger.debug(f"✅ Updated content metadata: {content_id}")
            
            return {
                "success": True,
                "content_id": content_id,
                "metadata": result
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update content metadata {content_id}: {e}")
            raise



