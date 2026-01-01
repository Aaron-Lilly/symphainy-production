#!/usr/bin/env python3
"""
Librarian Service - Clean Rebuild with Proper Infrastructure

Clean implementation using ONLY our new base and protocol construct
with proper infrastructure abstractions for search, knowledge management, and caching.

WHAT (Smart City Role): I manage knowledge discovery, metadata governance, and semantic search
HOW (Service Implementation): I use SmartCityRoleBase with correct infrastructure abstractions
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# Import ONLY our new base and protocol
from bases.smart_city_role_base import SmartCityRoleBase


class LibrarianServiceProtocol:
    """
    Protocol for Librarian services with proper infrastructure integration.
    Defines the contract for knowledge management, search, and content organization.
    """
    
    # Knowledge Management Methods
    async def store_knowledge(self, knowledge_data: Dict[str, Any]) -> str:
        """Store knowledge item with metadata."""
        ...
    
    async def get_knowledge_item(self, item_id: str) -> Dict[str, Any]:
        """Retrieve knowledge item by ID."""
        ...
    
    async def update_knowledge_item(self, item_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update knowledge item."""
        ...
    
    async def delete_knowledge_item(self, item_id: str) -> bool:
        """Delete knowledge item."""
        ...
    
    # Search Methods
    async def search_knowledge(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search knowledge base using Meilisearch."""
        ...
    
    async def semantic_search(self, concept: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform semantic search using ArangoDB graph."""
        ...
    
    async def get_semantic_relationships(self, concept: str) -> Dict[str, Any]:
        """Get semantic relationships for a concept."""
        ...
    
    # Content Organization Methods
    async def catalog_content(self, content_data: Dict[str, Any]) -> str:
        """Catalog and organize content."""
        ...
    
    async def manage_content_schema(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage content schema and metadata."""
        ...
    
    async def get_content_categories(self) -> Dict[str, Any]:
        """Get available content categories."""
        ...


class LibrarianService(SmartCityRoleBase, LibrarianServiceProtocol):
    """
    Librarian Service - Clean Rebuild with Proper Infrastructure
    
    Clean implementation using ONLY our new base and protocol construct
    with proper infrastructure abstractions for search, knowledge management, and caching.
    
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
        self.search_management_abstraction = None  # Meilisearch
        self.knowledge_management_abstraction = None  # ArangoDB
        self.content_caching_abstraction = None  # Redis
        
        # Service State
        self.is_infrastructure_connected = False
        
        # Week 3 Enhancement: SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # Service-specific state
        self.knowledge_base: Dict[str, Dict[str, Any]] = {}
        self.content_catalog: Dict[str, Dict[str, Any]] = {}
        self.search_index: Dict[str, List[str]] = {}
        self.semantic_relationships: Dict[str, List[str]] = {}
        
        # Logger is initialized by SmartCityRoleBase
        if self.logger:
            self.logger.info("✅ Librarian Service (Clean Rebuild with Proper Infrastructure) initialized")
    
    async def initialize(self) -> bool:
        """Initialize Librarian Service with proper infrastructure connections."""
        try:
            if self.logger:
                self.logger.info("🚀 Initializing Librarian Service with proper infrastructure connections...")
            
            # Initialize infrastructure connections
            await self._initialize_infrastructure_connections()
            
            # Initialize SOA API exposure
            await self._initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self._initialize_mcp_tool_integration()
            
            # Register capabilities with curator
            capabilities = await self._register_librarian_capabilities()
            await self.register_capability("LibrarianService", capabilities)
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            if self.logger:
                self.logger.info("✅ Librarian Service (Proper Infrastructure) initialized successfully")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to initialize Librarian Service: {str(e)}")
            self.service_health = "unhealthy"
            return False
    
    async def _initialize_infrastructure_connections(self):
        """Initialize connections to proper infrastructure abstractions."""
        try:
            if self.logger:
                self.logger.info("🔌 Connecting to proper infrastructure abstractions...")
            
            # Get Public Works Foundation
            public_works_foundation = self.get_public_works_foundation()
            if not public_works_foundation:
                raise Exception("Public Works Foundation not available")
            
            # Get Search Management Abstraction (Meilisearch)
            self.search_management_abstraction = await public_works_foundation.get_abstraction("search_management")
            if not self.search_management_abstraction:
                raise Exception("Search Management Abstraction not available")
            
            # Get Knowledge Management Abstraction (ArangoDB)
            self.knowledge_management_abstraction = await public_works_foundation.get_abstraction("knowledge_management")
            if not self.knowledge_management_abstraction:
                raise Exception("Knowledge Management Abstraction not available")
            
            # Get Content Caching Abstraction (Redis)
            self.content_caching_abstraction = await public_works_foundation.get_abstraction("content_caching")
            if not self.content_caching_abstraction:
                raise Exception("Content Caching Abstraction not available")
            
            self.is_infrastructure_connected = True
            
            if self.logger:
                self.logger.info("✅ Proper infrastructure connections established:")
                self.logger.info("  - Search Management (Meilisearch): ✅")
                self.logger.info("  - Knowledge Management (ArangoDB): ✅")
                self.logger.info("  - Content Caching (Redis): ✅")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to connect to proper infrastructure: {str(e)}")
            raise e
    
    async def _initialize_soa_api_exposure(self):
        """Initialize SOA API exposure for Smart City capabilities."""
        self.soa_apis = {
            "store_knowledge": {
                "endpoint": "/api/librarian/knowledge",
                "method": "POST",
                "description": "Store knowledge item with metadata",
                "parameters": ["knowledge_data"]
            },
            "search_knowledge": {
                "endpoint": "/api/librarian/knowledge/search",
                "method": "GET",
                "description": "Search knowledge base using Meilisearch",
                "parameters": ["query", "filters"]
            },
            "semantic_search": {
                "endpoint": "/api/librarian/semantic/search",
                "method": "GET",
                "description": "Perform semantic search using ArangoDB graph",
                "parameters": ["concept", "context"]
            },
            "get_semantic_relationships": {
                "endpoint": "/api/librarian/semantic/relationships/{concept}",
                "method": "GET",
                "description": "Get semantic relationships for a concept",
                "parameters": ["concept"]
            },
            "catalog_content": {
                "endpoint": "/api/librarian/content/catalog",
                "method": "POST",
                "description": "Catalog and organize content",
                "parameters": ["content_data"]
            },
            "manage_content_schema": {
                "endpoint": "/api/librarian/content/schema",
                "method": "PUT",
                "description": "Manage content schema and metadata",
                "parameters": ["schema_data"]
            },
            "get_content_categories": {
                "endpoint": "/api/librarian/content/categories",
                "method": "GET",
                "description": "Get available content categories",
                "parameters": []
            }
        }
    
    async def _initialize_mcp_tool_integration(self):
        """Initialize MCP tool integration for knowledge management operations."""
        self.mcp_tools = {
            "knowledge_manager": {
                "name": "knowledge_manager",
                "description": "Manage knowledge storage and retrieval",
                "parameters": ["knowledge_data", "operation_type"]
            },
            "search_engine": {
                "name": "search_engine",
                "description": "Perform knowledge searches using Meilisearch",
                "parameters": ["query", "search_options"]
            },
            "semantic_analyzer": {
                "name": "semantic_analyzer",
                "description": "Analyze semantic relationships using ArangoDB",
                "parameters": ["concept", "analysis_context"]
            },
            "content_organizer": {
                "name": "content_organizer",
                "description": "Organize and catalog content",
                "parameters": ["content_data", "organization_rules"]
            }
        }
    
    async def _register_librarian_capabilities(self) -> Dict[str, Any]:
        """Register Librarian Service capabilities with proper infrastructure mapping."""
        return {
            "service_name": "LibrarianService",
            "service_type": "knowledge_manager",
            "realm": "smart_city",
            "capabilities": [
                "knowledge_management",
                "semantic_search",
                "content_organization",
                "metadata_governance",
                "search_indexing",
                "infrastructure_integration"
            ],
            "infrastructure_connections": {
                "search_management": "Meilisearch",
                "knowledge_management": "ArangoDB",
                "content_caching": "Redis"
            },
            "soa_apis": self.soa_apis,
            "mcp_tools": self.mcp_tools,
            "status": "active",
            "infrastructure_connected": self.is_infrastructure_connected,
            "infrastructure_correct_from_start": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ============================================================================
    # KNOWLEDGE MANAGEMENT METHODS WITH PROPER INFRASTRUCTURE INTEGRATION
    # ============================================================================
    
    async def store_knowledge(self, knowledge_data: Dict[str, Any]) -> str:
        """Store knowledge item using ArangoDB + Meilisearch + Redis infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            item_id = str(uuid.uuid4())
            knowledge_item = {
                "item_id": item_id,
                "title": knowledge_data.get("title"),
                "content": knowledge_data.get("content"),
                "category": knowledge_data.get("category"),
                "tags": knowledge_data.get("tags", []),
                "metadata": knowledge_data.get("metadata", {}),
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Store in ArangoDB via Knowledge Management Abstraction
            success = await self.knowledge_management_abstraction.store_knowledge_item(
                item_id=item_id,
                knowledge_item=knowledge_item
            )
            
            if success:
                # Index in Meilisearch via Search Management Abstraction
                await self.search_management_abstraction.index_document(
                    document_id=item_id,
                    document_data=knowledge_item
                )
                
                # Cache in Redis via Content Caching Abstraction
                await self.content_caching_abstraction.cache_content(
                    content_id=item_id,
                    content_data=knowledge_item,
                    ttl=3600  # 1 hour
                )
                
                self.knowledge_base[item_id] = knowledge_item
                
                if self.logger:
                    self.logger.info(f"✅ Knowledge item stored: {item_id}")
                return item_id
            else:
                raise Exception("Failed to store knowledge item in ArangoDB")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error storing knowledge item: {str(e)}")
            raise e
    
    async def get_knowledge_item(self, item_id: str) -> Dict[str, Any]:
        """Retrieve knowledge item using Redis cache + ArangoDB infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Try Redis cache first
            cached_item = await self.content_caching_abstraction.get_cached_content(item_id)
            if cached_item:
                if self.logger:
                    self.logger.info(f"✅ Knowledge item retrieved from cache: {item_id}")
                return {
                    "item_id": item_id,
                    "item": cached_item,
                    "source": "cache",
                    "status": "success"
                }
            
            # Fallback to ArangoDB
            knowledge_item = await self.knowledge_management_abstraction.get_knowledge_item(item_id)
            if knowledge_item:
                # Cache for future requests
                await self.content_caching_abstraction.cache_content(
                    content_id=item_id,
                    content_data=knowledge_item,
                    ttl=3600
                )
                
                if self.logger:
                    self.logger.info(f"✅ Knowledge item retrieved from database: {item_id}")
                return {
                    "item_id": item_id,
                    "item": knowledge_item,
                    "source": "database",
                    "status": "success"
                }
            else:
                return {
                    "item_id": item_id,
                    "item": None,
                    "error": "Knowledge item not found",
                    "status": "error"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error retrieving knowledge item: {str(e)}")
            return {
                "item_id": item_id,
                "item": None,
                "error": str(e),
                "status": "error"
            }
    
    async def update_knowledge_item(self, item_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update knowledge item using ArangoDB + Meilisearch + Redis infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Update in ArangoDB
            success = await self.knowledge_management_abstraction.update_knowledge_item(
                item_id=item_id,
                updates=updates
            )
            
            if success:
                # Update index in Meilisearch
                await self.search_management_abstraction.update_document(
                    document_id=item_id,
                    document_updates=updates
                )
                
                # Invalidate cache in Redis
                await self.content_caching_abstraction.invalidate_content(item_id)
                
                if self.logger:
                    self.logger.info(f"✅ Knowledge item updated: {item_id}")
                return {
                    "item_id": item_id,
                    "updated": True,
                    "updates": updates,
                    "status": "success"
                }
            else:
                return {
                    "item_id": item_id,
                    "updated": False,
                    "error": "Failed to update knowledge item",
                    "status": "error"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error updating knowledge item: {str(e)}")
            return {
                "item_id": item_id,
                "updated": False,
                "error": str(e),
                "status": "error"
            }
    
    async def delete_knowledge_item(self, item_id: str) -> bool:
        """Delete knowledge item using ArangoDB + Meilisearch + Redis infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Delete from ArangoDB
            success = await self.knowledge_management_abstraction.delete_knowledge_item(item_id)
            
            if success:
                # Remove from Meilisearch index
                await self.search_management_abstraction.delete_document(item_id)
                
                # Remove from Redis cache
                await self.content_caching_abstraction.invalidate_content(item_id)
                
                # Remove from local state
                if item_id in self.knowledge_base:
                    del self.knowledge_base[item_id]
                
                if self.logger:
                    self.logger.info(f"✅ Knowledge item deleted: {item_id}")
                return True
            else:
                if self.logger:
                    self.logger.warning(f"⚠️ Failed to delete knowledge item: {item_id}")
                return False
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error deleting knowledge item: {str(e)}")
            return False
    
    # ============================================================================
    # SEARCH METHODS WITH PROPER INFRASTRUCTURE INTEGRATION
    # ============================================================================
    
    async def search_knowledge(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search knowledge base using Meilisearch infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Search using Meilisearch via Search Management Abstraction
            search_results = await self.search_management_abstraction.search_documents(
                query=query,
                filters=filters or {}
            )
            
            if search_results:
                if self.logger:
                    self.logger.info(f"✅ Knowledge search completed: {len(search_results.get('results', []))} results")
                return {
                    "query": query,
                    "filters": filters,
                    "results": search_results.get("results", []),
                    "total_results": search_results.get("total", 0),
                    "search_time": search_results.get("search_time", 0),
                    "status": "success"
                }
            else:
                return {
                    "query": query,
                    "filters": filters,
                    "results": [],
                    "total_results": 0,
                    "status": "success"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error searching knowledge: {str(e)}")
            return {
                "query": query,
                "filters": filters,
                "results": [],
                "total_results": 0,
                "error": str(e),
                "status": "error"
            }
    
    async def semantic_search(self, concept: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform semantic search using ArangoDB graph infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Semantic search using ArangoDB via Knowledge Management Abstraction
            semantic_results = await self.knowledge_management_abstraction.semantic_search(
                concept=concept,
                context=context or {}
            )
            
            if semantic_results:
                if self.logger:
                    self.logger.info(f"✅ Semantic search completed: {len(semantic_results.get('results', []))} results")
                return {
                    "concept": concept,
                    "context": context,
                    "results": semantic_results.get("results", []),
                    "relationships": semantic_results.get("relationships", []),
                    "confidence_scores": semantic_results.get("confidence_scores", []),
                    "status": "success"
                }
            else:
                return {
                    "concept": concept,
                    "context": context,
                    "results": [],
                    "relationships": [],
                    "confidence_scores": [],
                    "status": "success"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error performing semantic search: {str(e)}")
            return {
                "concept": concept,
                "context": context,
                "results": [],
                "relationships": [],
                "confidence_scores": [],
                "error": str(e),
                "status": "error"
            }
    
    async def get_semantic_relationships(self, concept: str) -> Dict[str, Any]:
        """Get semantic relationships using ArangoDB graph infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get relationships using ArangoDB via Knowledge Management Abstraction
            relationships = await self.knowledge_management_abstraction.get_semantic_relationships(concept)
            
            if relationships:
                if self.logger:
                    self.logger.info(f"✅ Semantic relationships retrieved: {len(relationships.get('relationships', []))} relationships")
                return {
                    "concept": concept,
                    "relationships": relationships.get("relationships", []),
                    "relationship_types": relationships.get("relationship_types", []),
                    "confidence_scores": relationships.get("confidence_scores", []),
                    "status": "success"
                }
            else:
                return {
                    "concept": concept,
                    "relationships": [],
                    "relationship_types": [],
                    "confidence_scores": [],
                    "status": "success"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting semantic relationships: {str(e)}")
            return {
                "concept": concept,
                "relationships": [],
                "relationship_types": [],
                "confidence_scores": [],
                "error": str(e),
                "status": "error"
            }
    
    # ============================================================================
    # CONTENT ORGANIZATION METHODS WITH PROPER INFRASTRUCTURE INTEGRATION
    # ============================================================================
    
    async def catalog_content(self, content_data: Dict[str, Any]) -> str:
        """Catalog content using ArangoDB + Redis infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            catalog_id = str(uuid.uuid4())
            catalog_entry = {
                "catalog_id": catalog_id,
                "content_type": content_data.get("content_type"),
                "title": content_data.get("title"),
                "description": content_data.get("description"),
                "category": content_data.get("category"),
                "tags": content_data.get("tags", []),
                "metadata": content_data.get("metadata", {}),
                "created_at": datetime.utcnow().isoformat(),
                "status": "cataloged"
            }
            
            # Store catalog entry in ArangoDB
            success = await self.knowledge_management_abstraction.store_catalog_entry(
                catalog_id=catalog_id,
                catalog_entry=catalog_entry
            )
            
            if success:
                # Cache catalog entry in Redis
                await self.content_caching_abstraction.cache_content(
                    content_id=catalog_id,
                    content_data=catalog_entry,
                    ttl=1800  # 30 minutes
                )
                
                self.content_catalog[catalog_id] = catalog_entry
                
                if self.logger:
                    self.logger.info(f"✅ Content cataloged: {catalog_id}")
                return catalog_id
            else:
                raise Exception("Failed to catalog content in ArangoDB")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error cataloging content: {str(e)}")
            raise e
    
    async def manage_content_schema(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage content schema using ArangoDB infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            schema_id = schema_data.get("schema_id") or str(uuid.uuid4())
            schema_definition = {
                "schema_id": schema_id,
                "schema_name": schema_data.get("schema_name"),
                "schema_version": schema_data.get("schema_version", "1.0"),
                "fields": schema_data.get("fields", []),
                "validation_rules": schema_data.get("validation_rules", {}),
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Store schema in ArangoDB
            success = await self.knowledge_management_abstraction.store_content_schema(
                schema_id=schema_id,
                schema_definition=schema_definition
            )
            
            if success:
                if self.logger:
                    self.logger.info(f"✅ Content schema managed: {schema_id}")
                return {
                    "schema_id": schema_id,
                    "schema_definition": schema_definition,
                    "managed": True,
                    "status": "success"
                }
            else:
                return {
                    "schema_id": schema_id,
                    "managed": False,
                    "error": "Failed to manage content schema",
                    "status": "error"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error managing content schema: {str(e)}")
            return {
                "schema_id": schema_data.get("schema_id"),
                "managed": False,
                "error": str(e),
                "status": "error"
            }
    
    async def get_content_categories(self) -> Dict[str, Any]:
        """Get content categories using Redis cache + ArangoDB infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Try Redis cache first
            cached_categories = await self.content_caching_abstraction.get_cached_content("content_categories")
            if cached_categories:
                if self.logger:
                    self.logger.info("✅ Content categories retrieved from cache")
                return {
                    "categories": cached_categories,
                    "source": "cache",
                    "status": "success"
                }
            
            # Fallback to ArangoDB
            categories = await self.knowledge_management_abstraction.get_content_categories()
            if categories:
                # Cache for future requests
                await self.content_caching_abstraction.cache_content(
                    content_id="content_categories",
                    content_data=categories,
                    ttl=1800  # 30 minutes
                )
                
                if self.logger:
                    self.logger.info("✅ Content categories retrieved from database")
                return {
                    "categories": categories,
                    "source": "database",
                    "status": "success"
                }
            else:
                return {
                    "categories": [],
                    "source": "database",
                    "status": "success"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting content categories: {str(e)}")
            return {
                "categories": [],
                "error": str(e),
                "status": "error"
            }
    
    # ============================================================================
    # INFRASTRUCTURE VALIDATION METHODS
    # ============================================================================
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate that proper infrastructure mapping is working correctly."""
        try:
            validation_results = {
                "search_management_meilisearch": False,
                "knowledge_management_arangodb": False,
                "content_caching_redis": False,
                "overall_status": False
            }
            
            # Test Search Management (Meilisearch)
            try:
                if self.search_management_abstraction:
                    test_result = await self.search_management_abstraction.health_check()
                    validation_results["search_management_meilisearch"] = True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ Search Management (Meilisearch) test failed: {str(e)}")
            
            # Test Knowledge Management (ArangoDB)
            try:
                if self.knowledge_management_abstraction:
                    test_result = await self.knowledge_management_abstraction.health_check()
                    validation_results["knowledge_management_arangodb"] = True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ Knowledge Management (ArangoDB) test failed: {str(e)}")
            
            # Test Content Caching (Redis)
            try:
                if self.content_caching_abstraction:
                    test_result = await self.content_caching_abstraction.health_check()
                    validation_results["content_caching_redis"] = True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ Content Caching (Redis) test failed: {str(e)}")
            
            # Overall status
            validation_results["overall_status"] = all([
                validation_results["search_management_meilisearch"],
                validation_results["knowledge_management_arangodb"],
                validation_results["content_caching_redis"]
            ])
            
            if self.logger:
                self.logger.info("🔍 Proper infrastructure mapping validation completed:")
                self.logger.info(f"  - Search Management (Meilisearch): {'✅' if validation_results['search_management_meilisearch'] else '❌'}")
                self.logger.info(f"  - Knowledge Management (ArangoDB): {'✅' if validation_results['knowledge_management_arangodb'] else '❌'}")
                self.logger.info(f"  - Content Caching (Redis): {'✅' if validation_results['content_caching_redis'] else '❌'}")
                self.logger.info(f"  - Overall Status: {'✅' if validation_results['overall_status'] else '❌'}")
            
            return validation_results
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error validating proper infrastructure mapping: {str(e)}")
            return {
                "search_management_meilisearch": False,
                "knowledge_management_arangodb": False,
                "content_caching_redis": False,
                "overall_status": False,
                "error": str(e)
            }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities with proper infrastructure status."""
        try:
            return {
                "service_name": "LibrarianService",
                "service_type": "knowledge_manager",
                "realm": "smart_city",
                "capabilities": [
                    "knowledge_management",
                    "semantic_search",
                    "content_organization",
                    "metadata_governance",
                    "search_indexing",
                    "infrastructure_integration"
                ],
                "infrastructure_connections": {
                    "search_management": "Meilisearch",
                    "knowledge_management": "ArangoDB",
                    "content_caching": "Redis"
                },
                "infrastructure_status": {
                    "connected": self.is_infrastructure_connected,
                    "search_management_available": self.search_management_abstraction is not None,
                    "knowledge_management_available": self.knowledge_management_abstraction is not None,
                    "content_caching_available": self.content_caching_abstraction is not None
                },
                "infrastructure_correct_from_start": True,
                "soa_apis": self.soa_apis,
                "mcp_tools": self.mcp_tools,
                "status": "active",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting service capabilities: {str(e)}")
            return {
                "service_name": "LibrarianService",
                "error": str(e),
                "status": "error"
            }
