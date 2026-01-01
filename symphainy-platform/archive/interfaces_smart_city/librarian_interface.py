#!/usr/bin/env python3
"""
Librarian Interface

Defines the contracts for Librarian service operations.
This interface matches the existing LibrarianService APIs.

WHAT (Interface Role): I define the contracts for knowledge management and metadata
HOW (Interface Implementation): I provide clear, typed interfaces for consumers
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class KnowledgeType(str, Enum):
    """Knowledge type levels."""
    DOCUMENT = "document"
    DATASET = "dataset"
    CODE = "code"
    CONFIGURATION = "configuration"
    METADATA = "metadata"
    RELATIONSHIP = "relationship"


class SearchMode(str, Enum):
    """Search mode levels."""
    EXACT = "exact"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    KEYWORD = "keyword"


class MetadataStatus(str, Enum):
    """Metadata status levels."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


# Request Models
class StoreKnowledgeRequest(BaseModel):
    """Request to store knowledge item."""
    knowledge_id: str = Field(..., description="Unique identifier for the knowledge item")
    knowledge_type: KnowledgeType = Field(..., description="Type of knowledge being stored")
    title: str = Field(..., description="Title of the knowledge item")
    content: str = Field(..., description="Content of the knowledge item")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Knowledge metadata")
    tags: Optional[List[str]] = Field(default_factory=list, description="Knowledge tags")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant knowledge")
    author: Optional[str] = Field(None, description="Author of the knowledge item")


class SearchKnowledgeRequest(BaseModel):
    """Request to search knowledge base."""
    query: str = Field(..., description="Search query")
    search_mode: Optional[SearchMode] = Field(SearchMode.SEMANTIC, description="Search mode to use")
    knowledge_types: Optional[List[KnowledgeType]] = Field(None, description="Types of knowledge to search")
    tags: Optional[List[str]] = Field(None, description="Tags to filter by")
    limit: Optional[int] = Field(10, description="Maximum number of results")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant search")


class GetMetadataRequest(BaseModel):
    """Request to get metadata for a knowledge item."""
    item_id: str = Field(..., description="ID of the knowledge item")
    include_content: Optional[bool] = Field(False, description="Include content in response")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant access")


class UpdateMetadataRequest(BaseModel):
    """Request to update metadata for a knowledge item."""
    item_id: str = Field(..., description="ID of the knowledge item")
    metadata: Dict[str, Any] = Field(..., description="Updated metadata")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    status: Optional[MetadataStatus] = Field(None, description="Updated status")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant access")


class GetSemanticRelationshipsRequest(BaseModel):
    """Request to get semantic relationships for a concept."""
    concept: str = Field(..., description="Concept to find relationships for")
    relationship_types: Optional[List[str]] = Field(None, description="Types of relationships to find")
    depth: Optional[int] = Field(1, description="Depth of relationship traversal")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant access")


# Response Models
class StoreKnowledgeResponse(BaseModel):
    """Response for knowledge storage."""
    success: bool = Field(..., description="Knowledge storage success status")
    knowledge_id: Optional[str] = Field(None, description="Stored knowledge ID")
    knowledge_type: Optional[KnowledgeType] = Field(None, description="Type of stored knowledge")
    title: Optional[str] = Field(None, description="Title of stored knowledge")
    stored_at: Optional[str] = Field(None, description="Storage timestamp")
    message: str = Field(..., description="Response message")


class SearchKnowledgeResponse(BaseModel):
    """Response for knowledge search."""
    success: bool = Field(..., description="Search success status")
    query: Optional[str] = Field(None, description="Search query")
    search_mode: Optional[SearchMode] = Field(None, description="Search mode used")
    results: Optional[List[Dict[str, Any]]] = Field(None, description="Search results")
    total_results: Optional[int] = Field(None, description="Total number of results found")
    searched_at: Optional[str] = Field(None, description="Search timestamp")
    message: str = Field(..., description="Response message")


class GetMetadataResponse(BaseModel):
    """Response for metadata retrieval."""
    success: bool = Field(..., description="Metadata retrieval success status")
    item_id: Optional[str] = Field(None, description="Knowledge item ID")
    knowledge_type: Optional[KnowledgeType] = Field(None, description="Type of knowledge")
    title: Optional[str] = Field(None, description="Knowledge title")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Knowledge metadata")
    tags: Optional[List[str]] = Field(None, description="Knowledge tags")
    content: Optional[str] = Field(None, description="Knowledge content if requested")
    retrieved_at: Optional[str] = Field(None, description="Retrieval timestamp")
    message: str = Field(..., description="Response message")


class UpdateMetadataResponse(BaseModel):
    """Response for metadata update."""
    success: bool = Field(..., description="Metadata update success status")
    item_id: Optional[str] = Field(None, description="Updated knowledge item ID")
    updated_metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")
    updated_tags: Optional[List[str]] = Field(None, description="Updated tags")
    updated_status: Optional[MetadataStatus] = Field(None, description="Updated status")
    updated_at: Optional[str] = Field(None, description="Update timestamp")
    message: str = Field(..., description="Response message")


class GetSemanticRelationshipsResponse(BaseModel):
    """Response for semantic relationships."""
    success: bool = Field(..., description="Relationship retrieval success status")
    concept: Optional[str] = Field(None, description="Requested concept")
    relationships: Optional[Dict[str, List[str]]] = Field(None, description="Semantic relationships")
    relationship_count: Optional[int] = Field(None, description="Number of relationships found")
    retrieved_at: Optional[str] = Field(None, description="Retrieval timestamp")
    message: str = Field(..., description="Response message")


# Interface Definition
class ILibrarian:
    """
    Librarian Interface

    Defines the contracts for Librarian service operations.
    This interface matches the existing LibrarianService APIs.
    """

    # Knowledge Management
    async def store_knowledge(self, request: StoreKnowledgeRequest) -> StoreKnowledgeResponse:
        """Store knowledge item with metadata."""
        pass

    async def search_knowledge(self, request: SearchKnowledgeRequest) -> SearchKnowledgeResponse:
        """Search knowledge base with semantic capabilities."""
        pass

    # Metadata Management
    async def get_metadata(self, request: GetMetadataRequest) -> GetMetadataResponse:
        """Get metadata for a knowledge item."""
        pass

    async def update_metadata(self, request: UpdateMetadataRequest) -> UpdateMetadataResponse:
        """Update metadata for a knowledge item."""
        pass

    # Semantic Relationships
    async def get_semantic_relationships(self, request: GetSemanticRelationshipsRequest) -> GetSemanticRelationshipsResponse:
        """Get semantic relationships for a concept."""
        pass























