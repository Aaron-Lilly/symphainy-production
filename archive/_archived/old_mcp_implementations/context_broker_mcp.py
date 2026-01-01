#!/usr/bin/env python3
"""
Context Broker MCP Server - Core Data Infrastructure

This MCP server abstracts knowledge and context management operations, combining:
- context7_server: Intelligent context retrieval and management
- librarian_v2: Advanced knowledge management with semantic search
- Infrastructure mapping: ArangoDB + Meilisearch + Object Storage + Redis

Provides a unified interface for knowledge and context management across the Smart City platform.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import uuid
import hashlib
import re
from collections import defaultdict
from enum import Enum

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import base class
from common.utilities.domain_bases import Core4MCPBase

class ContextType(Enum):
    """Context type enumeration for knowledge classification."""
    KNOWLEDGE = "knowledge"
    DOCUMENT = "document"
    PATTERN = "pattern"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    BEST_PRACTICE = "best_practice"
    SECURITY = "security"
    TELEMETRY = "telemetry"
    CONFIGURATION = "configuration"

class SearchMode(Enum):
    """Search mode enumeration."""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    VECTOR = "vector"

class ContextBrokerMCPServer(Core4MCPBase):
    """
    Context Broker MCP Server - abstracts knowledge and context management
    
    This server provides a unified interface for knowledge and context management across the Smart City platform,
    combining context7 server functionality with librarian_v2 advanced knowledge management.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Context Broker MCP Server."""
        # Initialize base class with service name and domain
        super().__init__("context_broker", "core4")
        
        # Keep existing initialization
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Server metadata
        self.name = "context_broker"
        self.version = "1.0.0"
        self.status = "active"
        
        # Knowledge and context configuration
        self.storage_backends = self.config.get("storage_backends", ["internal", "arangodb", "meilisearch", "vector"])
        self.default_backend = self.config.get("default_backend", "internal")
        self.context_path = self.config.get("context_path", "./data/context")
        
        # Knowledge management configuration
        self.knowledge_categories = {
            "patterns": "Design patterns and architectural knowledge",
            "contracts": "Service contracts and interfaces", 
            "workflows": "Business workflow knowledge",
            "models": "Data models and schemas",
            "integrations": "Integration patterns and examples",
            "best_practices": "Development and operational best practices",
            "security": "Security patterns and guidelines",
            "telemetry": "Monitoring and observability patterns",
            "configuration": "Configuration management patterns"
        }
        
        # Context storage
        self._context_store = {}
        self._knowledge_base = {}
        self._context_index = defaultdict(list)
        self._metadata_store = {}
        self._tag_index = defaultdict(list)
        self._capability_index = defaultdict(list)
        self._category_index = defaultdict(list)
        
        # Performance tracking
        self.operation_count = 0
        self.total_operation_time = 0.0
        self.search_metrics = {}
        
        # Initialize storage
        self._initialize_storage()
        
        # Define MCP tools
        self.tools = [
            "search_knowledge",
            "get_context",
            "add_knowledge",
            "update_knowledge",
            "delete_knowledge",
            "index_document",
            "search_context",
            "get_knowledge_by_category",
            "get_knowledge_by_tags",
            "get_knowledge_by_capabilities",
            "semantic_search",
            "vector_search",
            "hybrid_search",
            "get_knowledge_summary",
            "get_context_stats",
            "list_tools"
        ]
        
        # Define MCP resources
        self.resources = [
            "/context/knowledge_base.json",
            "/context/context_store.json",
            "/context/search_index.json",
            "/context/performance_metrics.json",
            "/context/knowledge_categories.json"
        ]
        
        # Define MCP prompts
        self.prompts = [
            "How to search and retrieve knowledge",
            "Knowledge management best practices",
            "Context-aware search patterns",
            "Semantic search implementation",
            "Knowledge organization and indexing"
        ]
        
        self.logger.info(f"Context Broker MCP Server initialized with context path: {self.context_path}")
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the MCP server."""
        logger = logging.getLogger("context_broker_mcp")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_storage(self):
        """Initialize context storage and create sample data."""
        # Ensure context directory exists
        Path(self.context_path).mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self._load_context_store()
        self._load_knowledge_base()
        self._load_metadata_store()
        
        # Initialize sample data if empty
        if not self._knowledge_base:
            self._create_sample_knowledge()
        
        if not self._context_store:
            self._create_sample_context()
    
    def _load_context_store(self):
        """Load context store from disk."""
        context_path = Path(self.context_path) / "context_store.json"
        if context_path.exists():
            try:
                with open(context_path, 'r') as f:
                    self._context_store = json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load context store: {e}")
                self._context_store = {}
        else:
            self._context_store = {}
    
    def _load_knowledge_base(self):
        """Load knowledge base from disk."""
        knowledge_path = Path(self.context_path) / "knowledge_base.json"
        if knowledge_path.exists():
            try:
                with open(knowledge_path, 'r') as f:
                    self._knowledge_base = json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load knowledge base: {e}")
                self._knowledge_base = {}
        else:
            self._knowledge_base = {}
    
    def _load_metadata_store(self):
        """Load metadata store from disk."""
        metadata_path = Path(self.context_path) / "metadata_store.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    self._metadata_store = json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load metadata store: {e}")
                self._metadata_store = {}
        else:
            self._metadata_store = {}
    
    def _save_context_store(self):
        """Save context store to disk."""
        context_path = Path(self.context_path) / "context_store.json"
        try:
            with open(context_path, 'w') as f:
                json.dump(self._context_store, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save context store: {e}")
    
    def _save_knowledge_base(self):
        """Save knowledge base to disk."""
        knowledge_path = Path(self.context_path) / "knowledge_base.json"
        try:
            with open(knowledge_path, 'w') as f:
                json.dump(self._knowledge_base, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save knowledge base: {e}")
    
    def _save_metadata_store(self):
        """Save metadata store to disk."""
        metadata_path = Path(self.context_path) / "metadata_store.json"
        try:
            with open(metadata_path, 'w') as f:
                json.dump(self._metadata_store, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save metadata store: {e}")
    
    def _create_sample_knowledge(self):
        """Create sample knowledge for testing and demonstration."""
        try:
            # Sample knowledge entries (from librarian_v2)
            sample_knowledge = {
                "smart_city_architecture": {
                    "id": str(uuid.uuid4()),
                    "name": "Smart City Architecture V2",
                    "description": "Enhanced Smart City architecture patterns and principles",
                    "content": {
                        "principle": "Orchestrator = HOW, Roles = WHAT",
                        "architecture": "Micro-module based with role separation and comprehensive integration",
                        "patterns": ["role-based", "micro-module", "orchestration", "security-first", "telemetry-aware"],
                        "integration_pattern": "Hybrid Integration Approach - Direct for internal, Orchestrator for cross-role"
                    },
                    "category": "patterns",
                    "tags": ["architecture", "core", "smart-city", "v2"],
                    "capabilities": ["system-design", "architecture-planning", "integration-patterns"],
                    "context_type": ContextType.KNOWLEDGE.value,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                },
                "knowledge_management_patterns": {
                    "id": str(uuid.uuid4()),
                    "name": "Knowledge Management Patterns",
                    "description": "Patterns for effective knowledge management and organization",
                    "content": {
                        "principle": "Knowledge should be discoverable, relevant, and actionable",
                        "patterns": [
                            "semantic_search", "context_awareness", "role_specific_delivery",
                            "metadata_enrichment", "analytics_driven_optimization"
                        ],
                        "organization": "Multi-dimensional indexing (tags, capabilities, categories, roles)",
                        "delivery": "Context-aware knowledge provision with relevance scoring"
                    },
                    "category": "best_practices",
                    "tags": ["knowledge-management", "patterns", "organization", "delivery"],
                    "capabilities": ["knowledge-design", "search-optimization", "content-organization"],
                    "context_type": ContextType.KNOWLEDGE.value,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                },
                "semantic_search_patterns": {
                    "id": str(uuid.uuid4()),
                    "name": "Semantic Search Patterns",
                    "description": "AI-powered semantic search and discovery patterns",
                    "content": {
                        "principle": "Search should understand intent, not just keywords",
                        "patterns": [
                            "relevance_scoring", "context_awareness", "semantic_understanding",
                            "multi_modal_search", "learning_from_interactions"
                        ],
                        "implementation": "Vector embeddings, relevance algorithms, context injection",
                        "optimization": "Continuous learning from search patterns and user feedback"
                    },
                    "category": "patterns",
                    "tags": ["semantic-search", "ai", "search-patterns", "relevance"],
                    "capabilities": ["search-design", "ai-integration", "relevance-optimization"],
                    "context_type": ContextType.KNOWLEDGE.value,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            }
            
            # Store knowledge and update indexes
            for key, knowledge in sample_knowledge.items():
                self._knowledge_base[key] = knowledge
                self._index_knowledge(knowledge)
            
            self._save_knowledge_base()
            self.logger.info("Sample knowledge created successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to create sample knowledge: {e}")
    
    def _create_sample_context(self):
        """Create sample context for testing and demonstration."""
        try:
            # Sample context entries (from context7_server)
            sample_contexts = [
                {
                    "id": "ctx_001",
                    "type": "project_structure",
                    "content": "SymphAIny platform with Smart Cities domain and MCP integration",
                    "tags": ["architecture", "platform", "smart_cities"],
                    "source": "codebase_analysis",
                    "confidence": 0.95,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "ctx_002", 
                    "type": "development_pattern",
                    "content": "Micro-modular architecture with health-aware routing and event-driven coordination",
                    "tags": ["architecture", "patterns", "micro-modules"],
                    "source": "code_review",
                    "confidence": 0.92,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "ctx_003",
                    "type": "integration_status",
                    "content": "File MCP server operational, Database MCP server operational, Context Broker server in development",
                    "tags": ["integration", "mcp", "status"],
                    "source": "system_monitoring",
                    "confidence": 0.98,
                    "created_at": datetime.now().isoformat()
                }
            ]
            
            # Store context and update indexes
            for context in sample_contexts:
                self._context_store[context["id"]] = context
                self._index_context(context["id"], context)
            
            self._save_context_store()
            self.logger.info("Sample context created successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to create sample context: {e}")
    
    def _index_knowledge(self, knowledge: Dict[str, Any]):
        """Index knowledge for search and retrieval."""
        try:
            knowledge_id = knowledge["id"]
            
            # Index by tags
            for tag in knowledge.get("tags", []):
                self._tag_index[tag].append(knowledge_id)
            
            # Index by capabilities
            for capability in knowledge.get("capabilities", []):
                self._capability_index[capability].append(knowledge_id)
            
            # Index by category
            category = knowledge.get("category", "unknown")
            self._category_index[category].append(knowledge_id)
            
            # Index content for text search
            content_text = self._extract_text_from_content(knowledge.get("content", {}))
            tokens = re.findall(r'\b\w+\b', content_text.lower())
            for token in tokens:
                if len(token) > 2:  # Skip very short tokens
                    self._context_index[token].append(knowledge_id)
            
        except Exception as e:
            self.logger.warning(f"Failed to index knowledge {knowledge.get('id', 'unknown')}: {e}")
    
    def _index_context(self, context_id: str, context: Dict[str, Any]):
        """Index context for search and retrieval."""
        try:
            # Convert content to searchable text
            content_text = str(context.get("content", ""))
            tokens = re.findall(r'\b\w+\b', content_text.lower())
            for token in tokens:
                if len(token) > 2:  # Skip very short tokens
                    self._context_index[token].append(context_id)
            
        except Exception as e:
            self.logger.warning(f"Failed to index context {context_id}: {e}")
    
    def _extract_text_from_content(self, content: Any) -> str:
        """Extract searchable text from content."""
        if isinstance(content, dict):
            return " ".join(str(v) for v in content.values())
        elif isinstance(content, list):
            return " ".join(str(item) for item in content)
        else:
            return str(content)
    
    # ============================================================================
    # MCP TOOLS - Core Knowledge Management
    # ============================================================================
    
    def search_knowledge(self, query: str, search_mode: str = "hybrid", 
                        category: str = None, tags: List[str] = None,
                        capabilities: List[str] = None, limit: int = 10) -> Dict[str, Any]:
        """
        Search knowledge using various search modes.
        
        Args:
            query: Search query
            search_mode: Search mode (semantic, keyword, hybrid, vector)
            category: Filter by category
            tags: Filter by tags
            capabilities: Filter by capabilities
            limit: Maximum number of results
            
        Returns:
            Search results
        """
        start_time = datetime.now()
        self.operation_count += 1
        
        try:
            # Determine search mode
            if search_mode == "semantic":
                results = self._semantic_search(query, category, tags, capabilities, limit)
            elif search_mode == "keyword":
                results = self._keyword_search(query, category, tags, capabilities, limit)
            elif search_mode == "vector":
                results = self._vector_search(query, category, tags, capabilities, limit)
            else:  # hybrid
                results = self._hybrid_search(query, category, tags, capabilities, limit)
            
            # Track performance
            end_time = datetime.now()
            operation_time = (end_time - start_time).total_seconds()
            self.total_operation_time += operation_time
            
            # Update search metrics
            if search_mode not in self.search_metrics:
                self.search_metrics[search_mode] = {"count": 0, "total_time": 0.0}
            self.search_metrics[search_mode]["count"] += 1
            self.search_metrics[search_mode]["total_time"] += operation_time
            
            self.logger.info(f"Knowledge search completed: {search_mode} mode, {len(results)} results")
            
            return {
                "success": True,
                "results": results,
                "count": len(results),
                "search_mode": search_mode,
                "query": query,
                "execution_time": operation_time
            }
            
        except Exception as e:
            self.logger.error(f"Failed to search knowledge: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _semantic_search(self, query: str, category: str = None, tags: List[str] = None,
                        capabilities: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search (mock implementation)."""
        # Mock semantic search - in production, this would use vector embeddings
        results = []
        query_lower = query.lower()
        
        for knowledge in self._knowledge_base.values():
            # Calculate semantic relevance (mock)
            relevance = self._calculate_semantic_relevance(knowledge, query_lower)
            
            if relevance > 0.3:  # Threshold for relevance
                # Apply filters
                if category and knowledge.get("category") != category:
                    continue
                if tags and not any(tag in knowledge.get("tags", []) for tag in tags):
                    continue
                if capabilities and not any(cap in knowledge.get("capabilities", []) for cap in capabilities):
                    continue
                
                result = knowledge.copy()
                result["relevance_score"] = relevance
                results.append(result)
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return results[:limit]
    
    def _keyword_search(self, query: str, category: str = None, tags: List[str] = None,
                       capabilities: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform keyword search."""
        results = []
        query_tokens = re.findall(r'\b\w+\b', query.lower())
        
        for knowledge in self._knowledge_base.values():
            # Calculate keyword relevance
            relevance = self._calculate_keyword_relevance(knowledge, query_tokens)
            
            if relevance > 0:
                # Apply filters
                if category and knowledge.get("category") != category:
                    continue
                if tags and not any(tag in knowledge.get("tags", []) for tag in tags):
                    continue
                if capabilities and not any(cap in knowledge.get("capabilities", []) for cap in capabilities):
                    continue
                
                result = knowledge.copy()
                result["relevance_score"] = relevance
                results.append(result)
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return results[:limit]
    
    def _vector_search(self, query: str, category: str = None, tags: List[str] = None,
                      capabilities: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform vector search (mock implementation)."""
        # Mock vector search - in production, this would use actual vector embeddings
        return self._semantic_search(query, category, tags, capabilities, limit)
    
    def _hybrid_search(self, query: str, category: str = None, tags: List[str] = None,
                      capabilities: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform hybrid search combining multiple methods."""
        # Get results from different search methods
        semantic_results = self._semantic_search(query, category, tags, capabilities, limit * 2)
        keyword_results = self._keyword_search(query, category, tags, capabilities, limit * 2)
        
        # Combine and deduplicate results
        combined_results = {}
        for result in semantic_results + keyword_results:
            knowledge_id = result["id"]
            if knowledge_id not in combined_results:
                combined_results[knowledge_id] = result
            else:
                # Combine relevance scores
                existing_score = combined_results[knowledge_id].get("relevance_score", 0)
                new_score = result.get("relevance_score", 0)
                combined_results[knowledge_id]["relevance_score"] = (existing_score + new_score) / 2
        
        # Sort by combined relevance and limit results
        results = list(combined_results.values())
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return results[:limit]
    
    def _calculate_semantic_relevance(self, knowledge: Dict[str, Any], query: str) -> float:
        """Calculate semantic relevance score (mock implementation)."""
        # Mock semantic relevance calculation
        content_text = self._extract_text_from_content(knowledge.get("content", {}))
        content_lower = content_text.lower()
        
        # Simple word overlap scoring
        query_words = set(query.split())
        content_words = set(content_lower.split())
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words.intersection(content_words))
        return overlap / len(query_words)
    
    def _calculate_keyword_relevance(self, knowledge: Dict[str, Any], query_tokens: List[str]) -> float:
        """Calculate keyword relevance score."""
        content_text = self._extract_text_from_content(knowledge.get("content", {}))
        content_lower = content_text.lower()
        
        matches = 0
        for token in query_tokens:
            if token in content_lower:
                matches += 1
        
        return matches / len(query_tokens) if query_tokens else 0.0
    
    def get_context(self, context_id: str) -> Dict[str, Any]:
        """
        Get specific context by ID.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Context data
        """
        try:
            context = self._context_store.get(context_id)
            if context:
                # Add metadata
                context["retrieved_at"] = datetime.now().isoformat()
                context["source_server"] = "context_broker"
                
                return {
                    "success": True,
                    "context": context
                }
            else:
                return {
                    "success": False,
                    "error": f"Context not found: {context_id}"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get context {context_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_knowledge(self, name: str, description: str, content: Dict[str, Any],
                     category: str, tags: List[str] = None, capabilities: List[str] = None) -> Dict[str, Any]:
        """
        Add new knowledge to the knowledge base.
        
        Args:
            name: Name of the knowledge item
            description: Description of the knowledge
            content: The actual knowledge content
            category: Knowledge category
            tags: Tags for organization and search
            capabilities: Capabilities this knowledge enables
            
        Returns:
            Addition result
        """
        try:
            # Validate inputs
            if not name or not description or not content:
                return {
                    "success": False,
                    "error": "Name, description, and content are required"
                }
            
            if category not in self.knowledge_categories:
                return {
                    "success": False,
                    "error": f"Invalid category. Must be one of: {list(self.knowledge_categories.keys())}"
                }
            
            # Create knowledge item
            knowledge_id = str(uuid.uuid4())
            knowledge_item = {
                "id": knowledge_id,
                "name": name,
                "description": description,
                "content": content,
                "category": category,
                "tags": tags or [],
                "capabilities": capabilities or [],
                "context_type": ContextType.KNOWLEDGE.value,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Store knowledge
            self._knowledge_base[knowledge_id] = knowledge_item
            
            # Update indexes
            self._index_knowledge(knowledge_item)
            
            # Save to disk
            self._save_knowledge_base()
            
            self.logger.info(f"Knowledge added successfully: {knowledge_id}")
            
            return {
                "success": True,
                "knowledge_id": knowledge_id,
                "knowledge_item": knowledge_item
            }
            
        except Exception as e:
            self.logger.error(f"Failed to add knowledge: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_knowledge(self, knowledge_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing knowledge.
        
        Args:
            knowledge_id: Knowledge identifier
            updates: Updates to apply
            
        Returns:
            Update result
        """
        try:
            if knowledge_id not in self._knowledge_base:
                return {
                    "success": False,
                    "error": f"Knowledge not found: {knowledge_id}"
                }
            
            # Update knowledge item
            knowledge_item = self._knowledge_base[knowledge_id]
            knowledge_item.update(updates)
            knowledge_item["updated_at"] = datetime.now().isoformat()
            
            # Re-index if content changed
            if any(key in updates for key in ["content", "tags", "capabilities", "category"]):
                self._index_knowledge(knowledge_item)
            
            # Save to disk
            self._save_knowledge_base()
            
            self.logger.info(f"Knowledge updated successfully: {knowledge_id}")
            
            return {
                "success": True,
                "knowledge_id": knowledge_id,
                "knowledge_item": knowledge_item
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update knowledge: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_knowledge(self, knowledge_id: str) -> Dict[str, Any]:
        """
        Delete knowledge from the knowledge base.
        
        Args:
            knowledge_id: Knowledge identifier
            
        Returns:
            Deletion result
        """
        try:
            if knowledge_id not in self._knowledge_base:
                return {
                    "success": False,
                    "error": f"Knowledge not found: {knowledge_id}"
                }
            
            # Remove from knowledge base
            del self._knowledge_base[knowledge_id]
            
            # Remove from indexes (simplified - in production, would be more efficient)
            self._rebuild_indexes()
            
            # Save to disk
            self._save_knowledge_base()
            
            self.logger.info(f"Knowledge deleted successfully: {knowledge_id}")
            
            return {
                "success": True,
                "knowledge_id": knowledge_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to delete knowledge: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _rebuild_indexes(self):
        """Rebuild all indexes from current knowledge base."""
        try:
            # Clear indexes
            self._tag_index.clear()
            self._capability_index.clear()
            self._category_index.clear()
            self._context_index.clear()
            
            # Rebuild indexes
            for knowledge in self._knowledge_base.values():
                self._index_knowledge(knowledge)
            
            for context in self._context_store.values():
                self._index_context(context["id"], context)
            
        except Exception as e:
            self.logger.error(f"Failed to rebuild indexes: {e}")
    
    # ============================================================================
    # MCP TOOLS - Additional Context Operations
    # ============================================================================
    
    def index_document(self, document_id: str, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Index a document for search.
        
        Args:
            document_id: Document identifier
            content: Document content
            metadata: Document metadata
            
        Returns:
            Indexing result
        """
        try:
            # Create context entry
            context_entry = {
                "id": document_id,
                "type": "document",
                "content": content,
                "tags": metadata.get("tags", []) if metadata else [],
                "source": metadata.get("source", "document_indexing") if metadata else "document_indexing",
                "confidence": 1.0,
                "created_at": datetime.now().isoformat()
            }
            
            # Store context
            self._context_store[document_id] = context_entry
            
            # Index for search
            self._index_context(document_id, context_entry)
            
            # Save to disk
            self._save_context_store()
            
            self.logger.info(f"Document indexed successfully: {document_id}")
            
            return {
                "success": True,
                "document_id": document_id,
                "context_entry": context_entry
            }
            
        except Exception as e:
            self.logger.error(f"Failed to index document: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_context(self, query: str, context_type: str = None, 
                      tags: List[str] = None, limit: int = 10) -> Dict[str, Any]:
        """
        Search context using semantic and keyword matching.
        
        Args:
            query: Search query
            context_type: Filter by context type
            tags: Filter by tags
            limit: Maximum number of results
            
        Returns:
            Search results
        """
        try:
            # Tokenize query
            query_tokens = re.findall(r'\b\w+\b', query.lower())
            
            # Find matching contexts
            matches = []
            seen_ids = set()
            
            for token in query_tokens:
                if token in self._context_index:
                    for context_key in self._context_index[token]:
                        if context_key not in seen_ids:
                            context = self._context_store.get(context_key)
                            if context:
                                # Apply filters
                                if context_type and context.get("type") != context_type:
                                    continue
                                if tags and not any(tag in context.get("tags", []) for tag in tags):
                                    continue
                                
                                # Calculate relevance score
                                relevance = self._calculate_context_relevance(context, query_tokens)
                                if relevance > 0:
                                    context_copy = context.copy()
                                    context_copy["relevance_score"] = relevance
                                    matches.append(context_copy)
                                    seen_ids.add(context_key)
            
            # Sort by relevance and limit results
            matches.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            matches = matches[:limit]
            
            return {
                "success": True,
                "results": matches,
                "count": len(matches),
                "query": query
            }
            
        except Exception as e:
            self.logger.error(f"Failed to search context: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_context_relevance(self, context: Dict[str, Any], query_tokens: List[str]) -> float:
        """Calculate relevance score for context."""
        content_text = str(context.get("content", "")).lower()
        
        matches = 0
        for token in query_tokens:
            if token in content_text:
                matches += 1
        
        return matches / len(query_tokens) if query_tokens else 0.0
    
    def get_knowledge_by_category(self, category: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get knowledge by category.
        
        Args:
            category: Knowledge category
            limit: Maximum number of results
            
        Returns:
            Knowledge items in category
        """
        try:
            knowledge_ids = self._category_index.get(category, [])
            knowledge_items = []
            
            for knowledge_id in knowledge_ids[:limit]:
                if knowledge_id in self._knowledge_base:
                    knowledge_items.append(self._knowledge_base[knowledge_id])
            
            return {
                "success": True,
                "knowledge_items": knowledge_items,
                "count": len(knowledge_items),
                "category": category
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get knowledge by category: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_knowledge_by_tags(self, tags: List[str], limit: int = 100) -> Dict[str, Any]:
        """
        Get knowledge by tags.
        
        Args:
            tags: List of tags
            limit: Maximum number of results
            
        Returns:
            Knowledge items with matching tags
        """
        try:
            knowledge_ids = set()
            
            for tag in tags:
                if tag in self._tag_index:
                    knowledge_ids.update(self._tag_index[tag])
            
            knowledge_items = []
            for knowledge_id in list(knowledge_ids)[:limit]:
                if knowledge_id in self._knowledge_base:
                    knowledge_items.append(self._knowledge_base[knowledge_id])
            
            return {
                "success": True,
                "knowledge_items": knowledge_items,
                "count": len(knowledge_items),
                "tags": tags
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get knowledge by tags: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_knowledge_by_capabilities(self, capabilities: List[str], limit: int = 100) -> Dict[str, Any]:
        """
        Get knowledge by capabilities.
        
        Args:
            capabilities: List of capabilities
            limit: Maximum number of results
            
        Returns:
            Knowledge items with matching capabilities
        """
        try:
            knowledge_ids = set()
            
            for capability in capabilities:
                if capability in self._capability_index:
                    knowledge_ids.update(self._capability_index[capability])
            
            knowledge_items = []
            for knowledge_id in list(knowledge_ids)[:limit]:
                if knowledge_id in self._knowledge_base:
                    knowledge_items.append(self._knowledge_base[knowledge_id])
            
            return {
                "success": True,
                "knowledge_items": knowledge_items,
                "count": len(knowledge_items),
                "capabilities": capabilities
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get knowledge by capabilities: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def semantic_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Perform semantic search.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Semantic search results
        """
        return self.search_knowledge(query, "semantic", limit=limit)
    
    def vector_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Perform vector search.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Vector search results
        """
        return self.search_knowledge(query, "vector", limit=limit)
    
    def hybrid_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Perform hybrid search.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Hybrid search results
        """
        return self.search_knowledge(query, "hybrid", limit=limit)
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all knowledge in the system.
        
        Returns:
            Knowledge summary
        """
        try:
            category_counts = {}
            for category in self.knowledge_categories:
                category_counts[category] = len(self._category_index.get(category, []))
            
            return {
                "success": True,
                "summary": {
                    "total_knowledge_items": len(self._knowledge_base),
                    "total_context_items": len(self._context_store),
                    "categories": category_counts,
                    "total_tags": len(self._tag_index),
                    "total_capabilities": len(self._capability_index),
                    "search_metrics": self.search_metrics,
                    "operation_count": self.operation_count,
                    "total_operation_time": self.total_operation_time
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get knowledge summary: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_context_stats(self) -> Dict[str, Any]:
        """
        Get context statistics.
        
        Returns:
            Context statistics
        """
        try:
            # Calculate context type distribution
            type_dist = {}
            for context in self._context_store.values():
                context_type = context.get("type", "unknown")
                type_dist[context_type] = type_dist.get(context_type, 0) + 1
            
            # Calculate tag distribution
            tag_dist = {}
            for context in self._context_store.values():
                for tag in context.get("tags", []):
                    tag_dist[tag] = tag_dist.get(tag, 0) + 1
            
            stats = {
                "total_context_items": len(self._context_store),
                "type_distribution": type_dist,
                "tag_distribution": tag_dist,
                "index_size": len(self._context_index),
                "operation_count": self.operation_count,
                "total_operation_time": self.total_operation_time
            }
            
            return {
                "success": True,
                "stats": stats
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get context stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_tools(self) -> Dict[str, Any]:
        """
        List available tools and capabilities.
        
        Returns:
            Available tools and metadata
        """
        try:
            return {
                "success": True,
                "tools": self.tools,
                "resources": self.resources,
                "prompts": self.prompts,
                "knowledge_categories": list(self.knowledge_categories.keys()),
                "search_modes": [mode.value for mode in SearchMode],
                "context_types": [context_type.value for context_type in ContextType],
                "total_knowledge_items": len(self._knowledge_base),
                "total_context_items": len(self._context_store)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list tools: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================================================
    # MCP RESOURCES
    # ============================================================================
    
    def get_resource(self, resource_path: str) -> Dict[str, Any]:
        """
        Get MCP resource data.
        
        Args:
            resource_path: Resource path
            
        Returns:
            Resource data
        """
        if resource_path == "/context/knowledge_base.json":
            return {
                "success": True,
                "data": self._knowledge_base
            }
        elif resource_path == "/context/context_store.json":
            return {
                "success": True,
                "data": self._context_store
            }
        elif resource_path == "/context/search_index.json":
            return {
                "success": True,
                "data": {
                    "context_index": dict(self._context_index),
                    "tag_index": dict(self._tag_index),
                    "capability_index": dict(self._capability_index),
                    "category_index": dict(self._category_index)
                }
            }
        elif resource_path == "/context/performance_metrics.json":
            return {
                "success": True,
                "data": {
                    "search_metrics": self.search_metrics,
                    "operation_count": self.operation_count,
                    "total_operation_time": self.total_operation_time
                }
            }
        elif resource_path == "/context/knowledge_categories.json":
            return {
                "success": True,
                "data": self.knowledge_categories
            }
        else:
            return {
                "success": False,
                "error": f"Unknown resource: {resource_path}"
            }
    
    # ============================================================================
    # MCP USAGE GUIDE
    # ============================================================================
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return usage guide for this MCP server."""
        return {
            "server": self.name,
            "version": self.version,
            "status": self.status,
            "purpose": "Knowledge and context management for Smart City platform",
            "tools": self.tools,
            "resources": self.resources,
            "prompts": self.prompts,
            "examples": [
                "context_broker.search_knowledge('smart city architecture', 'hybrid')",
                "context_broker.add_knowledge('New Pattern', 'Description', content, 'patterns')",
                "context_broker.get_knowledge_by_category('patterns')",
                "context_broker.semantic_search('knowledge management')",
                "context_broker.index_document('doc_123', 'document content')"
            ],
            "configuration": {
                "storage_backends": self.storage_backends,
                "default_backend": self.default_backend,
                "context_path": self.context_path,
                "knowledge_categories": list(self.knowledge_categories.keys())
            }
        }
    
    def call_tool(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Call a tool by name.
        
        Args:
            tool_name: Name of the tool to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
        
        try:
            method = getattr(self, tool_name)
            return method(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Failed to call tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
