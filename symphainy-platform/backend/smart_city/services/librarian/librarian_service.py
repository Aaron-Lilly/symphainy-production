#!/usr/bin/env python3
"""
Librarian Service - Clean Micro-Modular Rebuild

Clean micro-modular implementation using base/protocol architecture
with proper infrastructure abstractions for knowledge management.

WHAT (Smart City Role): I manage knowledge discovery, metadata governance, and semantic search
HOW (Service Implementation): I use SmartCityRoleBase with correct infrastructure abstractions
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

# Import base and protocol
from bases.smart_city_role_base import SmartCityRoleBase
from backend.smart_city.protocols.librarian_service_protocol import LibrarianServiceProtocol

# Import micro-modules
from .modules.initialization import Initialization
from .modules.knowledge_management import KnowledgeManagement
from .modules.search import Search
from .modules.content_organization import ContentOrganization
from .modules.content_metadata_storage import ContentMetadataStorage
from .modules.semantic_data_storage import SemanticDataStorage
from .modules.soa_mcp import SoaMcp
from .modules.utilities import Utilities


class LibrarianService(SmartCityRoleBase, LibrarianServiceProtocol):
    """
    Librarian Service - Clean Micro-Modular Rebuild
    
    Clean micro-modular implementation using base/protocol architecture
    with proper infrastructure abstractions for knowledge management.
    
    WHAT (Smart City Role): I manage knowledge discovery, metadata governance, and semantic search
    HOW (Service Implementation): I use SmartCityRoleBase with correct infrastructure abstractions
    """
    
    def __init__(self, di_container: Any):
        """Initialize Librarian Service with proper infrastructure mapping."""
        super().__init__(
            service_name="LibrarianService",
            role_name="librarian",
            di_container=di_container
        )
        
        # Infrastructure Abstractions (will be initialized in initialize())
        self.knowledge_discovery_abstraction = None  # Meilisearch + Redis Graph + ArangoDB
        self.knowledge_governance_abstraction = None  # Metadata + ArangoDB
        self.content_metadata_abstraction = None  # ContentMetadataAbstraction (NEW)
        self.semantic_data_abstraction = None  # SemanticDataAbstraction (NEW)
        self.messaging_abstraction = None  # Redis for caching
        
        # Service State
        self.is_infrastructure_connected = False
        
        # SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # Service-specific state
        self.knowledge_base: Dict[str, Dict[str, Any]] = {}
        self.content_catalog: Dict[str, Dict[str, Any]] = {}
        
        # Initialize micro-modules
        self.initialization_module = Initialization(self)
        self.knowledge_management_module = KnowledgeManagement(self)
        self.search_module = Search(self)
        self.content_organization_module = ContentOrganization(self)
        self.content_metadata_storage_module = ContentMetadataStorage(self)  # NEW
        self.semantic_data_storage_module = SemanticDataStorage(self)  # NEW
        self.soa_mcp_module = SoaMcp(self)
        self.utilities_module = Utilities(self)
        
        # Logger is initialized by SmartCityRoleBase
        if self.logger:
            self.logger.info("✅ Librarian Service (Clean Micro-Modular Rebuild) initialized")
    
    async def initialize(self) -> bool:
        """Initialize Librarian Service with proper infrastructure connections."""
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "librarian_initialize_start",
            success=True
        )
        
        try:
            # Initialize infrastructure connections
            await self.initialization_module.initialize_infrastructure_connections()
            
            # Initialize SOA API exposure
            await self.soa_mcp_module.initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self.soa_mcp_module.initialize_mcp_tool_integration()
            
            # Register capabilities with curator (Phase 2 pattern - simplified for Smart City)
            await self.soa_mcp_module.register_capabilities()
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            # Record health metric
            await self.record_health_metric(
                "librarian_initialized",
                1.0,
                {"service": "LibrarianService"}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "librarian_initialize_complete",
                success=True
            )
            
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(
                e,
                "librarian_initialize",
                {
                    "service": "LibrarianService",
                    "error_type": type(e).__name__
                }
            )
            
            self.service_health = "unhealthy"
            
            # Log failure
            await self.log_operation_with_telemetry(
                "librarian_initialize_complete",
                success=False,
                details={"error": str(e), "error_type": type(e).__name__}
            )
            
            # Record health metric
            await self.record_health_metric(
                "librarian_initialized",
                0.0,
                metadata={"error_type": type(e).__name__}
            )
            
            return False
    
    # ============================================================================
    # KNOWLEDGE MANAGEMENT METHODS
    # ============================================================================
    
    async def store_knowledge(self, knowledge_data: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> str:
        """Store knowledge item with metadata."""
        # Service-level method delegates to module (module handles utilities)
        return await self.knowledge_management_module.store_knowledge(knowledge_data, user_context)
    
    async def get_knowledge_item(self, item_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve knowledge item by ID."""
        # Service-level method delegates to module (module handles utilities)
        return await self.knowledge_management_module.get_knowledge_item(item_id, user_context)
    
    async def retrieve_document(self, document_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve document by ID (alias for get_knowledge_item for backward compatibility).
        
        Args:
            document_id: Document ID to retrieve
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Document data and metadata
        """
        # Service-level method delegates to module (module handles utilities)
        return await self.get_knowledge_item(document_id, user_context)
    
    async def update_knowledge_item(self, item_id: str, updates: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update knowledge item."""
        # Service-level method delegates to module (module handles utilities)
        return await self.knowledge_management_module.update_knowledge_item(item_id, updates, user_context)
    
    async def delete_knowledge_item(self, item_id: str, user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Delete knowledge item."""
        # Service-level method delegates to module (module handles utilities)
        return await self.knowledge_management_module.delete_knowledge_item(item_id, user_context)
    
    # ============================================================================
    # SEARCH METHODS
    # ============================================================================
    
    async def search_knowledge(self, query: str, filters: Optional[Dict[str, Any]] = None, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search knowledge base using Meilisearch."""
        # Service-level method delegates to module (module handles utilities)
        return await self.search_module.search_knowledge(query, filters, user_context)
    
    async def semantic_search(self, concept: str, context: Optional[Dict[str, Any]] = None, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform semantic search using ArangoDB graph."""
        # Service-level method delegates to module (module handles utilities)
        return await self.search_module.semantic_search(concept, context, user_context)
    
    async def get_semantic_relationships(self, concept: str) -> Dict[str, Any]:
        """Get semantic relationships for a concept."""
        return await self.search_module.get_semantic_relationships(concept)
    
    # ============================================================================
    # CONTENT ORGANIZATION METHODS
    # ============================================================================
    
    async def catalog_content(self, content_data: Dict[str, Any]) -> str:
        """Catalog and organize content."""
        return await self.content_organization_module.catalog_content(content_data)
    
    async def manage_content_schema(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage content schema and metadata."""
        return await self.content_organization_module.manage_content_schema(schema_data)
    
    async def get_content_categories(self) -> Dict[str, Any]:
        """Get available content categories."""
        return await self.content_organization_module.get_content_categories()
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate infrastructure mapping."""
        return await self.utilities_module.validate_infrastructure_mapping()
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get Librarian service capabilities."""
        return await self.utilities_module.get_service_capabilities()
    
    # ============================================================================
    # CONTENT METADATA STORAGE METHODS (NEW)
    # ============================================================================
    
    async def store_content_metadata(
        self,
        file_id: str,
        parsed_file_id: str,
        content_metadata: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store content metadata (SOA API).
        
        Args:
            file_id: Original file UUID
            parsed_file_id: Parsed file ID
            content_metadata: Extracted content metadata
            user_context: Optional user context
            
        Returns:
            Dict with content_id and metadata
        """
        return await self.content_metadata_storage_module.store_content_metadata(
            file_id, parsed_file_id, content_metadata, user_context
        )
    
    async def get_content_metadata(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get content metadata by content_id (SOA API).
        
        Args:
            content_id: Content metadata ID
            user_context: Optional user context
            
        Returns:
            Dict with content metadata
        """
        return await self.content_metadata_storage_module.get_content_metadata(content_id, user_context)
    
    async def update_content_metadata(
        self,
        content_id: str,
        updates: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update content metadata (SOA API).
        
        Args:
            content_id: Content metadata ID
            updates: Dictionary of fields to update
            user_context: Optional user context
            
        Returns:
            Dict with updated content metadata
        """
        return await self.content_metadata_storage_module.update_content_metadata(content_id, updates, user_context)
    
    # ============================================================================
    # SEMANTIC DATA STORAGE METHODS (NEW)
    # ============================================================================
    
    async def store_embeddings(
        self,
        content_id: str,
        file_id: str,
        embeddings: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store semantic embeddings (SOA API).
        
        Args:
            content_id: Content metadata ID
            file_id: File UUID
            embeddings: List of embedding dictionaries
            user_context: Optional user context
            
        Returns:
            Dict with storage result
        """
        return await self.semantic_data_storage_module.store_embeddings(
            content_id, file_id, embeddings, user_context
        )
    
    async def get_embeddings(
        self,
        content_id: str,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get semantic embeddings with filtering (SOA API).
        
        Args:
            content_id: Content metadata ID
            filters: Optional filters
            user_context: Optional user context
            
        Returns:
            List of embedding dictionaries
        """
        return await self.semantic_data_storage_module.get_embeddings(content_id, filters, user_context)
    
    async def vector_search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Vector similarity search (SOA API).
        
        Args:
            query_embedding: Query vector
            limit: Maximum number of results
            filters: Optional filters
            user_context: Optional user context
            
        Returns:
            List of matching embedding dictionaries
        """
        return await self.semantic_data_storage_module.vector_search(
            query_embedding, limit, filters, user_context
        )
    
    async def store_semantic_graph(
        self,
        content_id: str,
        file_id: str,
        semantic_graph: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store semantic graph (SOA API).
        
        Args:
            content_id: Content metadata ID
            file_id: File UUID
            semantic_graph: Dictionary with 'nodes' and 'edges' lists
            user_context: Optional user context
            
        Returns:
            Dict with storage result
        """
        return await self.semantic_data_storage_module.store_semantic_graph(
            content_id, file_id, semantic_graph, user_context
        )
    
    async def get_semantic_graph(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get semantic graph (SOA API).
        
        Args:
            content_id: Content metadata ID
            user_context: Optional user context
            
        Returns:
            Dictionary with 'nodes' and 'edges' lists
        """
        return await self.semantic_data_storage_module.get_semantic_graph(content_id, user_context)
