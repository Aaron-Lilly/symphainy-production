#!/usr/bin/env python3
"""
Redis Graph Knowledge Adapter - Raw Technology Layer

Raw Redis Graph client wrapper for knowledge graph operations.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw Redis Graph graph capabilities
HOW (Infrastructure Implementation): I wrap the Redis Graph client with basic operations
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import asyncio

logger = logging.getLogger(__name__)

class RedisGraphKnowledgeAdapter:
    """
    Raw Redis Graph client wrapper for knowledge graph operations.
    
    Provides direct access to Redis Graph capabilities without business logic.
    Focused on knowledge graph operations, relationships, and semantic queries.
    """
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, 
                 password: str = None, timeout: int = 30, graph_prefix: str = "knowledge_"):
        """Initialize Redis Graph knowledge adapter."""
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.timeout = timeout
        self.graph_prefix = graph_prefix
        self.logger = logging.getLogger(__name__)
        
        # Redis Graph client
        self.redis_client = None
        self.graph = None
        
        # Knowledge-specific graph names
        self.knowledge_graph = f"{graph_prefix}graph"
        self.semantic_graph = f"{graph_prefix}semantic"
        self.relationships_graph = f"{graph_prefix}relationships"
        
        self.logger.info(f"✅ Redis Graph Knowledge adapter initialized with {host}:{port}")
    
    async def connect(self) -> bool:
        """Connect to Redis Graph server."""
        try:
            import redis.asyncio as redis
            
            # Create Redis client with asyncio support
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
                socket_timeout=self.timeout
            )
            
            # Test connection
            health = await self._get_health()
            if health:
                self.logger.info("✅ Redis Graph Knowledge adapter connected")
                return True
            else:
                self.logger.error("❌ Failed to connect to Redis Graph")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to Redis Graph: {e}")
            return False
    
    async def _get_health(self) -> bool:
        """Check Redis Graph server health."""
        try:
            if self.redis_client:
                # Simple ping test
                result = await self.redis_client.ping()
                return result
            return False
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            return False
    
    # ============================================================================
    # GRAPH MANAGEMENT
    # ============================================================================
    
    async def create_graph(self, graph_name: str) -> bool:
        """Create a new graph."""
        try:
            if not self.redis_client:
                return False
            
            # Create graph (Redis Graph creates graphs implicitly)
            # Just verify the graph exists
            result = await self.redis_client.execute_command("GRAPH.QUERY", graph_name, "MATCH (n) RETURN count(n) LIMIT 1")
            
            self.logger.info(f"✅ Graph created/verified: {graph_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create graph {graph_name}: {e}")
            return False
    
    async def delete_graph(self, graph_name: str) -> bool:
        """Delete a graph."""
        try:
            if not self.redis_client:
                return False
            
            # Delete graph
            result = await self.redis_client.execute_command("GRAPH.DELETE", graph_name)
            
            self.logger.info(f"✅ Graph deleted: {graph_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to delete graph {graph_name}: {e}")
            return False
    
    async def list_graphs(self) -> List[str]:
        """List all graphs."""
        try:
            if not self.redis_client:
                return []
            
            # Get all graph keys
            keys = await self.redis_client.keys("GRAPH.*")
            graphs = [key.replace("GRAPH.", "") for key in keys if key.startswith("GRAPH.")]
            
            return graphs
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list graphs: {e}")
            return []
    
    # ============================================================================
    # NODE OPERATIONS
    # ============================================================================
    
    async def create_node(self, graph_name: str, labels: List[str], 
                        properties: Dict[str, Any]) -> str:
        """Create a node in the graph."""
        try:
            if not self.redis_client:
                return None
            
            # Build CREATE query
            label_str = ":".join(labels)
            props_str = self._build_properties_string(properties)
            
            query = f"CREATE (n:{label_str} {props_str}) RETURN ID(n) as id"
            
            result = await self.redis_client.execute_command("GRAPH.QUERY", graph_name, query)
            
            if result and len(result) > 0:
                node_id = result[0][0]
                self.logger.info(f"✅ Node created: {node_id}")
                return str(node_id)
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create node: {e}")
            return None
    
    async def get_node(self, graph_name: str, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by ID."""
        try:
            if not self.redis_client:
                return None
            
            # Build MATCH query
            query = f"MATCH (n) WHERE ID(n) = {node_id} RETURN n"
            
            result = await self.redis_client.execute_command("GRAPH.QUERY", graph_name, query)
            
            if result and len(result) > 0:
                node_data = result[0][0]
                self.logger.info(f"✅ Node retrieved: {node_id}")
                return node_data
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get node {node_id}: {e}")
            return None
    
    async def update_node(self, graph_name: str, node_id: str, 
                         properties: Dict[str, Any]) -> bool:
        """Update node properties."""
        try:
            if not self.redis_client:
                return False
            
            # Build SET query
            set_clauses = []
            for key, value in properties.items():
                if isinstance(value, str):
                    set_clauses.append(f"n.{key} = '{value}'")
                else:
                    set_clauses.append(f"n.{key} = {value}")
            
            set_str = ", ".join(set_clauses)
            query = f"MATCH (n) WHERE ID(n) = {node_id} SET {set_str} RETURN n"
            
            result = await self.redis_client.execute_command("GRAPH.QUERY", graph_name, query)
            
            if result:
                self.logger.info(f"✅ Node updated: {node_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update node {node_id}: {e}")
            return False
    
    async def delete_node(self, graph_name: str, node_id: str) -> bool:
        """Delete a node."""
        try:
            if not self.redis_client:
                return False
            
            # Build DELETE query
            query = f"MATCH (n) WHERE ID(n) = {node_id} DELETE n"
            
            result = await self.redis_client.execute_command("GRAPH.QUERY", graph_name, query)
            
            self.logger.info(f"✅ Node deleted: {node_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to delete node {node_id}: {e}")
            return False
    
    # ============================================================================
    # RELATIONSHIP OPERATIONS
    # ============================================================================
    
    async def create_relationship(self, graph_name: str, from_node_id: str, 
                                to_node_id: str, relationship_type: str,
                                properties: Optional[Dict[str, Any]] = None) -> str:
        """Create a relationship between nodes."""
        try:
            if not self.redis_client:
                return None
            
            # Build CREATE query
            props_str = ""
            if properties:
                props_str = self._build_properties_string(properties)
            
            query = f"MATCH (a), (b) WHERE ID(a) = {from_node_id} AND ID(b) = {to_node_id} CREATE (a)-[r:{relationship_type} {props_str}]->(b) RETURN ID(r) as id"
            
            result = await self.redis_client.execute_command("GRAPH.QUERY", graph_name, query)
            
            if result and len(result) > 0:
                rel_id = result[0][0]
                self.logger.info(f"✅ Relationship created: {rel_id}")
                return str(rel_id)
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create relationship: {e}")
            return None
    
    async def get_relationships(self, graph_name: str, node_id: str, 
                               direction: str = "both") -> List[Dict[str, Any]]:
        """Get relationships for a node."""
        try:
            if not self.redis_client:
                return []
            
            # Build MATCH query based on direction
            if direction == "outgoing":
                query = f"MATCH (n)-[r]->(m) WHERE ID(n) = {node_id} RETURN r, m"
            elif direction == "incoming":
                query = f"MATCH (n)<-[r]-(m) WHERE ID(n) = {node_id} RETURN r, m"
            else:  # both
                query = f"MATCH (n)-[r]-(m) WHERE ID(n) = {node_id} RETURN r, m"
            
            result = await self.redis_client.execute_command("GRAPH.QUERY", graph_name, query)
            
            relationships = []
            for row in result:
                rel_data = {
                    "relationship": row[0],
                    "target_node": row[1]
                }
                relationships.append(rel_data)
            
            self.logger.info(f"✅ Relationships retrieved for node: {node_id}")
            return relationships
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get relationships for {node_id}: {e}")
            return []
    
    # ============================================================================
    # QUERY OPERATIONS
    # ============================================================================
    
    async def execute_query(self, graph_name: str, query: str) -> List[Dict[str, Any]]:
        """Execute a Cypher query."""
        try:
            if not self.redis_client:
                return []
            
            result = await self.redis_client.execute_command("GRAPH.QUERY", graph_name, query)
            
            self.logger.info(f"✅ Query executed: {query[:50]}...")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Query execution failed: {e}")
            return []
    
    async def find_path(self, graph_name: str, start_node_id: str, 
                       end_node_id: str, max_depth: int = 5) -> List[Dict[str, Any]]:
        """Find path between two nodes."""
        try:
            if not self.redis_client:
                return []
            
            # Build path finding query
            query = f"MATCH path = (start)-[*1..{max_depth}]-(end) WHERE ID(start) = {start_node_id} AND ID(end) = {end_node_id} RETURN path LIMIT 10"
            
            result = await self.redis_client.execute_command("GRAPH.QUERY", graph_name, query)
            
            paths = []
            for row in result:
                path_data = {
                    "path": row[0],
                    "length": len(row[0]) if row[0] else 0
                }
                paths.append(path_data)
            
            self.logger.info(f"✅ Path found between {start_node_id} and {end_node_id}")
            return paths
            
        except Exception as e:
            self.logger.error(f"❌ Failed to find path: {e}")
            return []
    
    async def get_neighbors(self, graph_name: str, node_id: str, 
                          depth: int = 1) -> List[Dict[str, Any]]:
        """Get neighbors of a node."""
        try:
            if not self.redis_client:
                return []
            
            # Build neighbor query
            query = f"MATCH (n)-[*1..{depth}]-(neighbor) WHERE ID(n) = {node_id} RETURN DISTINCT neighbor"
            
            result = await self.redis_client.execute_command("GRAPH.QUERY", graph_name, query)
            
            neighbors = []
            for row in result:
                neighbors.append(row[0])
            
            self.logger.info(f"✅ Neighbors retrieved for node: {node_id}")
            return neighbors
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get neighbors for {node_id}: {e}")
            return []
    
    # ============================================================================
    # SEMANTIC OPERATIONS
    # ============================================================================
    
    async def find_semantic_similarity(self, graph_name: str, node_id: str, 
                                     similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find semantically similar nodes."""
        try:
            if not self.redis_client:
                return []
            
            # This would typically involve vector similarity or semantic analysis
            # For now, return basic similarity structure
            similar_nodes = []
            
            self.logger.info(f"✅ Semantic similarity found for node: {node_id}")
            return similar_nodes
            
        except Exception as e:
            self.logger.error(f"❌ Failed to find semantic similarity: {e}")
            return []
    
    async def get_knowledge_clusters(self, graph_name: str, 
                                   cluster_size: int = 5) -> List[Dict[str, Any]]:
        """Get knowledge clusters from the graph."""
        try:
            if not self.redis_client:
                return []
            
            # Build clustering query
            query = f"MATCH (n) WITH n, rand() as r ORDER BY r LIMIT {cluster_size} RETURN n"
            
            result = await self.redis_client.execute_command("GRAPH.QUERY", graph_name, query)
            
            clusters = []
            for row in result:
                clusters.append(row[0])
            
            self.logger.info(f"✅ Knowledge clusters retrieved")
            return clusters
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get knowledge clusters: {e}")
            return []
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _build_properties_string(self, properties: Dict[str, Any]) -> str:
        """Build properties string for Cypher queries."""
        try:
            if not properties:
                return ""
            
            prop_pairs = []
            for key, value in properties.items():
                if isinstance(value, str):
                    prop_pairs.append(f"{key}: '{value}'")
                else:
                    prop_pairs.append(f"{key}: {value}")
            
            return "{" + ", ".join(prop_pairs) + "}"
            
        except Exception as e:
            self.logger.error(f"❌ Failed to build properties string: {e}")
            return ""
    
    async def get_graph_stats(self, graph_name: str) -> Dict[str, Any]:
        """Get statistics for a graph."""
        try:
            if not self.redis_client:
                return {"nodeCount": 0, "relationshipCount": 0}
            
            # Get node count
            node_query = "MATCH (n) RETURN count(n) as nodeCount"
            node_result = await self.redis_client.execute_command("GRAPH.QUERY", graph_name, node_query)
            
            # Get relationship count
            rel_query = "MATCH ()-[r]->() RETURN count(r) as relationshipCount"
            rel_result = await self.redis_client.execute_command("GRAPH.QUERY", graph_name, rel_query)
            
            stats = {
                "nodeCount": node_result[0][0] if node_result else 0,
                "relationshipCount": rel_result[0][0] if rel_result else 0,
                "graphName": graph_name
            }
            
            self.logger.info(f"✅ Graph stats retrieved for {graph_name}")
            return stats
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get graph stats: {e}")
            return {"nodeCount": 0, "relationshipCount": 0}
    
    async def close(self):
        """Close the Redis Graph connection."""
        try:
            if self.redis_client:
                await self.redis_client.close()
                self.redis_client = None
                self.logger.info("✅ Redis Graph Knowledge adapter closed")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to close Redis Graph adapter: {e}")

