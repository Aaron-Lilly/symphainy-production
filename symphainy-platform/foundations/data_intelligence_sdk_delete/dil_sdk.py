#!/usr/bin/env python3
"""
Data Intelligence Layer SDK - Client Library for Smart City Services

Provides unified interface for data operations, semantic data management,
and observability through Smart City SOA APIs.

WHAT (DIL SDK Role): I provide unified interface for data operations
HOW (DIL SDK Implementation): I wrap Smart City SOA APIs
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime


class DILSDK:
    """
    Data Intelligence Layer SDK - Client library for Smart City services.
    
    WHAT: I provide unified interface for data operations
    HOW: I wrap Smart City SOA APIs
    
    This SDK provides a clean, unified interface for:
    - File lifecycle operations (via Content Steward)
    - Semantic data operations (via Librarian)
    - Data governance operations (via Data Steward)
    - Observability operations (via Nurse)
    """
    
    def __init__(self, smart_city_services: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        Initialize DIL SDK with Smart City services.
        
        Args:
            smart_city_services: Dictionary of Smart City service instances
                Expected keys: "content_steward", "librarian", "data_steward", "nurse"
            logger: Optional logger instance
        """
        self.content_steward = smart_city_services.get("content_steward")
        self.librarian = smart_city_services.get("librarian")
        self.data_steward = smart_city_services.get("data_steward")
        self.nurse = smart_city_services.get("nurse")
        
        self.logger = logger or logging.getLogger(__name__)
        
        # Validate required services
        missing_services = []
        if not self.content_steward:
            missing_services.append("content_steward")
        if not self.librarian:
            missing_services.append("librarian")
        if not self.data_steward:
            missing_services.append("data_steward")
        if not self.nurse:
            missing_services.append("nurse")
        
        if missing_services:
            self.logger.warning(f"⚠️ DIL SDK initialized with missing services: {missing_services}")
        else:
            self.logger.info("✅ DIL SDK initialized with all Smart City services")
    
    # ============================================================================
    # FILE LIFECYCLE OPERATIONS (via Content Steward)
    # ============================================================================
    
    async def upload_file(
        self,
        file_data: bytes,
        file_name: str,
        file_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload file via Content Steward.
        
        Args:
            file_data: Raw file bytes
            file_name: File name
            file_type: File type/extension
            metadata: Optional file metadata
            user_context: Optional user context for security
            
        Returns:
            Dict with file_id and metadata
        """
        if not self.content_steward:
            raise ValueError("Content Steward service not available")
        
        return await self.content_steward.upload_file(
            file_data=file_data,
            file_name=file_name,
            file_type=file_type,
            metadata=metadata,
            user_context=user_context
        )
    
    async def get_file(
        self,
        file_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get file via Content Steward.
        
        Args:
            file_id: File UUID
            user_context: Optional user context for security
            
        Returns:
            File data with metadata, or None if not found
        """
        if not self.content_steward:
            raise ValueError("Content Steward service not available")
        
        return await self.content_steward.get_file(file_id, user_context)
    
    async def list_files(
        self,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List files via Content Steward.
        
        Args:
            filters: Optional filters (user_id, tenant_id, content_type, etc.)
            user_context: Optional user context for security
            
        Returns:
            List of file records
        """
        if not self.content_steward:
            raise ValueError("Content Steward service not available")
        
        return await self.content_steward.list_files(filters=filters, user_context=user_context)
    
    async def store_parsed_file(
        self,
        file_id: str,
        parsed_file_data: bytes,
        format_type: str,
        content_type: str,
        parse_result: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store parsed file via Content Steward.
        
        Args:
            file_id: Original file UUID
            parsed_file_data: Parsed file bytes
            format_type: Format type ("parquet", "json_structured", "json_chunks")
            content_type: Content type ("structured", "unstructured", "hybrid")
            parse_result: Parse result metadata
            user_context: Optional user context
            
        Returns:
            Dict with parsed_file_id and metadata
        """
        if not self.content_steward:
            raise ValueError("Content Steward service not available")
        
        return await self.content_steward.store_parsed_file(
            file_id=file_id,
            parsed_file_data=parsed_file_data,
            format_type=format_type,
            content_type=content_type,
            parse_result=parse_result,
            user_context=user_context
        )
    
    # ============================================================================
    # SEMANTIC DATA OPERATIONS (via Librarian)
    # ============================================================================
    
    async def store_content_metadata(
        self,
        file_id: str,
        parsed_file_id: str,
        content_metadata: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store content metadata via Librarian.
        
        Args:
            file_id: Original file UUID
            parsed_file_id: Parsed file ID
            content_metadata: Extracted content metadata
            user_context: Optional user context
            
        Returns:
            Dict with content_id and metadata
        """
        if not self.librarian:
            raise ValueError("Librarian service not available")
        
        return await self.librarian.store_content_metadata(
            file_id=file_id,
            parsed_file_id=parsed_file_id,
            content_metadata=content_metadata,
            user_context=user_context
        )
    
    async def get_content_metadata(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get content metadata via Librarian.
        
        Args:
            content_id: Content ID
            user_context: Optional user context
            
        Returns:
            Content metadata dict, or None if not found
        """
        if not self.librarian:
            raise ValueError("Librarian service not available")
        
        return await self.librarian.get_content_metadata(content_id, user_context)
    
    async def store_semantic_embeddings(
        self,
        content_id: str,
        file_id: str,
        embeddings: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store semantic embeddings via Librarian.
        
        Args:
            content_id: Content ID
            file_id: File UUID
            embeddings: List of embedding dicts (with column_name and meaning_embedding/metadata_embedding)
            user_context: Optional user context
            
        Returns:
            Dict with success status and embedding IDs
        """
        if not self.librarian:
            raise ValueError("Librarian service not available")
        
        return await self.librarian.store_embeddings(
            content_id=content_id,
            file_id=file_id,
            embeddings=embeddings,
            user_context=user_context
        )
    
    async def get_semantic_embeddings(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get semantic embeddings via Librarian.
        
        Args:
            content_id: Content ID
            user_context: Optional user context
            
        Returns:
            List of embedding records
        """
        if not self.librarian:
            raise ValueError("Librarian service not available")
        
        return await self.librarian.get_embeddings(content_id, user_context)
    
    async def vector_search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Vector similarity search via Librarian.
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            filters: Optional filters
            user_context: Optional user context
            
        Returns:
            List of similar embeddings with scores
        """
        if not self.librarian:
            raise ValueError("Librarian service not available")
        
        # Use semantic_data_abstraction directly for vector search
        if hasattr(self.librarian, 'semantic_data_abstraction') and self.librarian.semantic_data_abstraction:
            return await self.librarian.semantic_data_abstraction.query_semantic_embeddings(
                query_embedding=query_embedding,
                limit=limit,
                filters=filters,
                user_context=user_context
            )
        else:
            raise ValueError("Semantic data abstraction not available in Librarian")
    
    # ============================================================================
    # DATA GOVERNANCE OPERATIONS (via Data Steward)
    # ============================================================================
    
    async def track_lineage(
        self,
        lineage_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track data lineage via Data Steward.
        
        Args:
            lineage_data: Lineage data (source_id, target_id, operation, etc.)
            user_context: Optional user context
            
        Returns:
            Dict with lineage_id and status
        """
        if not self.data_steward:
            raise ValueError("Data Steward service not available")
        
        return await self.data_steward.track_lineage(lineage_data, user_context)
    
    async def get_lineage(
        self,
        asset_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get lineage for asset via Data Steward.
        
        Args:
            asset_id: Asset ID
            user_context: Optional user context
            
        Returns:
            Dict with lineage information
        """
        if not self.data_steward:
            raise ValueError("Data Steward service not available")
        
        return await self.data_steward.get_lineage(asset_id, user_context)
    
    # ============================================================================
    # OBSERVABILITY OPERATIONS (via Nurse)
    # ============================================================================
    
    async def record_platform_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        trace_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record platform event (log, metric, or trace) via Nurse.
        
        Args:
            event_type: Event type ("log", "metric", "trace")
            event_data: Event data (level, message, metric_name, value, etc.)
            trace_id: Optional trace ID for correlation
            user_context: Optional user context
            
        Returns:
            Dict with event_id and status
        """
        if not self.nurse:
            raise ValueError("Nurse service not available")
        
        return await self.nurse.record_platform_event(
            event_type=event_type,
            event_data=event_data,
            trace_id=trace_id,
            user_context=user_context
        )
    
    async def record_agent_execution(
        self,
        agent_id: str,
        agent_name: str,
        prompt_hash: str,
        response: str,
        trace_id: Optional[str] = None,
        execution_metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record agent execution via Nurse.
        
        Args:
            agent_id: Agent identifier
            agent_name: Agent name
            prompt_hash: Hash of the prompt used
            response: Agent response text
            trace_id: Optional trace ID for correlation
            execution_metadata: Optional execution metadata (tokens, latency, cost, etc.)
            user_context: Optional user context
            
        Returns:
            Dict with execution_id and status
        """
        if not self.nurse:
            raise ValueError("Nurse service not available")
        
        return await self.nurse.record_agent_execution(
            agent_id=agent_id,
            agent_name=agent_name,
            prompt_hash=prompt_hash,
            response=response,
            trace_id=trace_id,
            execution_metadata=execution_metadata,
            user_context=user_context
        )
    
    async def get_observability_data(
        self,
        data_type: str,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query observability data via Nurse.
        
        Args:
            data_type: Data type ("logs", "metrics", "traces", "agent_execution")
            filters: Optional filters
            user_context: Optional user context
            
        Returns:
            List of observability records
        """
        if not self.nurse:
            raise ValueError("Nurse service not available")
        
        return await self.nurse.get_observability_data(
            data_type=data_type,
            filters=filters,
            user_context=user_context
        )


