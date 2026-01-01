#!/usr/bin/env python3
"""
Librarian Service - SOA/MCP Module

Micro-module for SOA API exposure and MCP tool integration.
"""

from typing import Any, Dict


class SoaMcp:
    """SOA/MCP module for Librarian service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def initialize_soa_api_exposure(self):
        """Initialize SOA API exposure for Smart City capabilities (Phase 3.2: Librarian Finalization)."""
        self.service.soa_apis = {
            # Content Metadata Storage APIs
            "store_content_metadata": {
                "endpoint": "/api/librarian/content-metadata",
                "method": "POST",
                "description": "Store extracted content metadata (from Business Enablement)",
                "parameters": ["content_id", "file_id", "metadata", "user_context"]
            },
            "get_content_metadata": {
                "endpoint": "/api/librarian/content-metadata/{content_id}",
                "method": "GET",
                "description": "Get content metadata by content_id",
                "parameters": ["content_id", "user_context"]
            },
            "update_content_metadata": {
                "endpoint": "/api/librarian/content-metadata/{content_id}",
                "method": "PUT",
                "description": "Update content metadata",
                "parameters": ["content_id", "metadata_updates", "user_context"]
            },
            "get_content_structure": {
                "endpoint": "/api/librarian/content-structure/{content_id}",
                "method": "GET",
                "description": "Get content structure (schema, columns, data types)",
                "parameters": ["content_id", "user_context"]
            },
            # Semantic Data APIs
            "store_embeddings": {
                "endpoint": "/api/librarian/embeddings",
                "method": "POST",
                "description": "Store semantic embeddings",
                "parameters": ["content_id", "file_id", "embeddings", "user_context"]
            },
            "get_embeddings": {
                "endpoint": "/api/librarian/embeddings/{content_id}",
                "method": "GET",
                "description": "Get semantic embeddings by content_id",
                "parameters": ["content_id", "user_context"]
            },
            "query_by_semantic_id": {
                "endpoint": "/api/librarian/semantic/{semantic_id}",
                "method": "GET",
                "description": "Query by semantic ID",
                "parameters": ["semantic_id", "user_context"]
            },
            "vector_search": {
                "endpoint": "/api/librarian/vector-search",
                "method": "POST",
                "description": "Vector similarity search",
                "parameters": ["query_embedding", "limit", "filters", "user_context"]
            },
            "store_semantic_graph": {
                "endpoint": "/api/librarian/semantic-graph",
                "method": "POST",
                "description": "Store semantic graph",
                "parameters": ["content_id", "file_id", "semantic_graph", "user_context"]
            },
            "get_semantic_graph": {
                "endpoint": "/api/librarian/semantic-graph/{content_id}",
                "method": "GET",
                "description": "Get semantic graph by content_id",
                "parameters": ["content_id", "user_context"]
            },
            "store_correlation_map": {
                "endpoint": "/api/librarian/correlation-map",
                "method": "POST",
                "description": "Store correlation map (for hybrid parsing)",
                "parameters": ["content_id", "file_id", "correlation_map", "user_context"]
            },
            "get_correlation_map": {
                "endpoint": "/api/librarian/correlation-map/{content_id}",
                "method": "GET",
                "description": "Get correlation map by content_id",
                "parameters": ["content_id", "user_context"]
            },
            # Semantic Search APIs
            "search_semantic": {
                "endpoint": "/api/librarian/search/semantic",
                "method": "POST",
                "description": "Unified semantic search",
                "parameters": ["query", "filters", "user_context"]
            },
            "search_metadata": {
                "endpoint": "/api/librarian/search/metadata",
                "method": "POST",
                "description": "Meilisearch for metadata search",
                "parameters": ["query", "filters", "user_context"]
            }
        }
        
        if self.service.logger:
            self.service.logger.info(f"✅ SOA APIs exposed: {len(self.service.soa_apis)} endpoints")
    
    async def initialize_mcp_tool_integration(self):
        """Initialize MCP tool integration for Smart City capabilities."""
        self.service.mcp_tools = {
            "store_knowledge": {
                "name": "store_knowledge",
                "description": "Store knowledge item with metadata",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "string"},
                        "category": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "metadata": {"type": "object"}
                    },
                    "required": ["title", "content"]
                }
            },
            "search_knowledge": {
                "name": "search_knowledge",
                "description": "Search knowledge base",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "filters": {"type": "object"}
                    },
                    "required": ["query"]
                }
            },
            "semantic_search": {
                "name": "semantic_search",
                "description": "Perform semantic search",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "concept": {"type": "string"},
                        "context": {"type": "object"}
                    },
                    "required": ["concept"]
                }
            },
            "catalog_content": {
                "name": "catalog_content",
                "description": "Catalog and organize content",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content_type": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "category": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "metadata": {"type": "object"}
                    },
                    "required": ["content_type", "title"]
                }
            }
        }
        
        if self.service.logger:
            self.service.logger.info(f"✅ MCP tools registered: {len(self.service.mcp_tools)} tools")
    
    async def register_capabilities(self) -> Dict[str, Any]:
        """Register Librarian capabilities with Curator using Phase 2 pattern (simplified for Smart City)."""
        try:
            # Build capabilities list with SOA API and MCP Tool contracts
            capabilities = []
            
            # Group SOA APIs and MCP tools by capability
            # For Smart City services, we create one capability per SOA API/MCP tool pair
            # or combine related ones into a single capability
            
            # Create knowledge_management capability (combines multiple SOA APIs)
            knowledge_apis = ["store_knowledge", "search_knowledge", "semantic_search"]
            knowledge_tools = ["store_knowledge", "search_knowledge"]
            
            capabilities.append({
                "name": "knowledge_management",
                "protocol": "LibrarianServiceProtocol",
                "description": "Knowledge management and semantic search capabilities",
                "contracts": {
                    "soa_api": {
                        "api_name": "store_knowledge",  # Primary SOA API
                        "endpoint": self.service.soa_apis.get("store_knowledge", {}).get("endpoint", "/soa/librarian/store_knowledge"),
                        "method": self.service.soa_apis.get("store_knowledge", {}).get("method", "POST"),
                        "handler": getattr(self.service, "store_knowledge", None),
                        "metadata": {
                            "description": "Store knowledge item with metadata",
                            "apis": knowledge_apis
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "librarian_store_knowledge",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "librarian_store_knowledge",
                            "description": "Store knowledge item with metadata",
                            "input_schema": self.service.mcp_tools.get("store_knowledge", {}).get("input_schema", {})
                        }
                    }
                }
            })
            
            # Create content_organization capability
            content_apis = ["catalog_content", "manage_content_schema"]
            content_tools = ["catalog_content"]
            
            capabilities.append({
                "name": "content_organization",
                "protocol": "LibrarianServiceProtocol",
                "description": "Content cataloging and schema management",
                "contracts": {
                    "soa_api": {
                        "api_name": "catalog_content",
                        "endpoint": self.service.soa_apis.get("catalog_content", {}).get("endpoint", "/soa/librarian/catalog_content"),
                        "method": self.service.soa_apis.get("catalog_content", {}).get("method", "POST"),
                        "handler": getattr(self.service, "catalog_content", None),
                        "metadata": {
                            "description": "Catalog and organize content",
                            "apis": content_apis
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "librarian_catalog_content",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "librarian_catalog_content",
                            "description": "Catalog and organize content",
                            "input_schema": self.service.mcp_tools.get("catalog_content", {}).get("input_schema", {})
                        }
                    }
                }
            })
            
            # Register using register_with_curator (simplified Phase 2 pattern)
            soa_api_names = list(self.service.soa_apis.keys())
            mcp_tool_names = [f"librarian_{tool}" for tool in self.service.mcp_tools.keys()]
            
            success = await self.service.register_with_curator(
                capabilities=capabilities,
                soa_apis=soa_api_names,
                mcp_tools=mcp_tool_names,
                protocols=[{
                    "name": "LibrarianServiceProtocol",
                    "definition": {
                        "methods": {
                            "store_knowledge": {"input_schema": {}, "output_schema": {}},
                            "search_knowledge": {"input_schema": {}, "output_schema": {}},
                            "semantic_search": {"input_schema": {}, "output_schema": {}},
                            "catalog_content": {"input_schema": {}, "output_schema": {}},
                            "manage_content_schema": {"input_schema": {}, "output_schema": {}}
                        }
                    }
                }]
            )
            
            if success:
                if self.service.logger:
                    self.service.logger.info(f"✅ Librarian registered with Curator (Phase 2 pattern - Smart City): {len(capabilities)} capabilities")
            else:
                if self.service.logger:
                    self.service.logger.warning("⚠️ Failed to register Librarian with Curator")
                    
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to register Librarian capabilities: {e}")
                import traceback
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't raise - return capabilities dict anyway
        
        # Return capabilities metadata
        return await self._get_librarian_capabilities_dict()
    
    async def register_librarian_capabilities(self) -> Dict[str, Any]:
        """Register Librarian service capabilities (backward compatibility - calls register_capabilities first)."""
        # Call register_capabilities first to ensure Curator registration happens
        return await self.register_capabilities()
    
    async def _get_librarian_capabilities_dict(self) -> Dict[str, Any]:
        """Get Librarian service capabilities dict."""
        capabilities = {
            "knowledge_management": {
                "store_knowledge": True,
                "get_knowledge_item": True,
                "update_knowledge_item": True,
                "delete_knowledge_item": True
            },
            "search": {
                "search_knowledge": True,
                "semantic_search": True,
                "get_semantic_relationships": True
            },
            "content_organization": {
                "catalog_content": True,
                "manage_content_schema": True,
                "get_content_categories": True
            },
            "infrastructure": {
                "knowledge_discovery": True,
                "knowledge_governance": True,
                "messaging_cache": True
            }
        }
        
        if self.service.logger:
            self.service.logger.info("✅ Librarian capabilities registered")
        
        return capabilities







