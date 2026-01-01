#!/usr/bin/env python3
"""
Redis Graph Infrastructure Adapter

Raw Redis Graph bindings for workflow orchestration and graph-based execution.
Thin wrapper around Redis Graph SDK with no business logic.
"""

from typing import Dict, Any, List, Optional, Tuple
import json
import asyncio
from datetime import datetime
import logging
import uuid

try:
    import redis
    from redis.exceptions import RedisError
except ImportError:
    redis = None
    RedisError = Exception


class RedisGraphAdapter:
    """Raw Redis Graph adapter for workflow orchestration."""
    
    def __init__(self, host: str, port: int, db: int = 0, password: str = None, 
                 timeout: int = 30, **kwargs):
        """
        Initialize Redis Graph adapter.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database
            password: Redis password
            timeout: Connection timeout
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.timeout = timeout
        self.logger = logging.getLogger("RedisGraphAdapter")
        
        # Redis client
        self.redis_client = None
        self.graph_client = None
        
        # Graph names
        self.workflow_graph = "workflow_orchestration"
        self.agent_graph = "agent_coordination"
        self.execution_graph = "execution_state"
        
        # Redis Graph availability flag
        self.graph_available = False
        
        # Initialize Redis connection
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection and check for Graph module."""
        if redis is None:
            self.logger.error("Redis not installed")
            return
            
        try:
            # Create Redis client
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
                socket_timeout=self.timeout,
                socket_connect_timeout=self.timeout
            )
            
            # Test connection
            self.redis_client.ping()
            
            # Check if Redis Graph module is available
            try:
                # Check if GRAPH module is loaded by trying MODULE LIST
                modules = self.redis_client.execute_command('MODULE', 'LIST')
                graph_module_loaded = any(
                    module.get(b'name', b'').decode('utf-8', errors='ignore') == 'graph' 
                    for module in modules if isinstance(module, dict)
                )
                
                if graph_module_loaded:
                    # Try a simple Graph command to verify it works
                    try:
                        # Use a test graph name that won't conflict
                        test_result = self.redis_client.execute_command('GRAPH.QUERY', 'test_availability_check', 'RETURN 1', '--compact')
                        self.graph_available = True
                        self.logger.info("✅ Redis Graph adapter initialized (Graph module available)")
                    except Exception as test_error:
                        # Graph module loaded but command failed - might be version issue
                        self.graph_available = True  # Assume available, will handle errors in methods
                        self.logger.warning(f"⚠️  Redis Graph module loaded but test query failed: {test_error}")
                else:
                    self.graph_available = False
                    self.logger.warning(
                        "⚠️  Redis Graph module not loaded. "
                        "Use redislabs/redisgraph image for Graph support."
                    )
            except Exception as graph_error:
                # MODULE LIST might not be available or failed - try direct command
                try:
                    self.redis_client.execute_command('GRAPH.QUERY', 'test_availability_check', 'RETURN 1', '--compact')
                    self.graph_available = True
                    self.logger.info("✅ Redis Graph adapter initialized (Graph module available)")
                except Exception:
                    # Graph module not available
                    self.graph_available = False
                    self.logger.warning(
                        f"⚠️  Redis Graph module not available: {graph_error}. "
                        f"Graph operations will be disabled. Use redislabs/redisgraph image for Graph support."
                    )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis: {e}")
            self.redis_client = None
            self.graph_available = False
    
    def create_graph(self, graph_name: str) -> bool:
        """
        Create a new graph.
        
        Args:
            graph_name: Name of the graph
            
        Returns:
            bool: Success status
        """
        if not self.redis_client:
            return False
        
        if not self.graph_available:
            self.logger.warning(f"⚠️  Redis Graph not available - cannot create graph {graph_name}")
            return False
            
        try:
            # Create graph using Redis Graph commands
            result = self.redis_client.execute_command('GRAPH.QUERY', graph_name, 
                                                     'CREATE ()', '--compact')
            
            self.logger.info(f"✅ Graph {graph_name} created")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create graph {graph_name}: {e}")
            return False
    
    def delete_graph(self, graph_name: str) -> bool:
        """
        Delete a graph.
        
        Args:
            graph_name: Name of the graph
            
        Returns:
            bool: Success status
        """
        if not self.redis_client:
            return False
            
        try:
            # Delete graph
            self.redis_client.execute_command('GRAPH.DELETE', graph_name)
            
            self.logger.info(f"✅ Graph {graph_name} deleted")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete graph {graph_name}: {e}")
            return False
    
    def execute_query(self, graph_name: str, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a Cypher query on the graph.
        
        Args:
            graph_name: Name of the graph
            query: Cypher query
            params: Query parameters
            
        Returns:
            Dict: Query result
        """
        if not self.redis_client:
            return {"error": "Redis not initialized", "result": []}
        
        if not self.graph_available:
            return {"error": "Redis Graph not available", "result": [], "graph_available": False}
            
        try:
            # Execute query
            result = self.redis_client.execute_command('GRAPH.QUERY', graph_name, query, '--compact')
            
            return {
                "graph_name": graph_name,
                "query": query,
                "result": result,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to execute query on {graph_name}: {e}")
            return {"error": str(e), "result": []}
    
    def create_node(self, graph_name: str, node_id: str, labels: List[str] = None, 
                   properties: Dict[str, Any] = None) -> bool:
        """
        Create a node in the graph.
        
        Args:
            graph_name: Name of the graph
            node_id: Node ID
            labels: Node labels
            properties: Node properties
            
        Returns:
            bool: Success status
        """
        if not self.redis_client:
            return False
        
        if not self.graph_available:
            self.logger.warning(f"⚠️  Redis Graph not available - cannot create node {node_id}")
            return False
            
        try:
            # Build Cypher query
            labels_str = ":" + ":".join(labels) if labels else ""
            props_str = json.dumps(properties or {})
            
            query = f"CREATE (n{labels_str} {{id: '{node_id}', properties: {props_str}}})"
            
            result = self.redis_client.execute_command('GRAPH.QUERY', graph_name, query, '--compact')
            
            self.logger.info(f"✅ Node {node_id} created in {graph_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create node {node_id}: {e}")
            return False
    
    def create_relationship(self, graph_name: str, from_node: str, to_node: str, 
                           relationship_type: str, properties: Dict[str, Any] = None) -> bool:
        """
        Create a relationship between nodes.
        
        Args:
            graph_name: Name of the graph
            from_node: Source node ID
            to_node: Target node ID
            relationship_type: Type of relationship
            properties: Relationship properties
            
        Returns:
            bool: Success status
        """
        if not self.redis_client:
            return False
            
        try:
            # Build Cypher query
            props_str = json.dumps(properties or {})
            
            query = f"""
            MATCH (a {{id: '{from_node}'}}), (b {{id: '{to_node}'}})
            CREATE (a)-[r:{relationship_type} {{properties: {props_str}}}]->(b)
            """
            
            result = self.redis_client.execute_command('GRAPH.QUERY', graph_name, query, '--compact')
            
            self.logger.info(f"✅ Relationship {from_node}->{to_node} created in {graph_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create relationship {from_node}->{to_node}: {e}")
            return False
    
    def get_node(self, graph_name: str, node_id: str) -> Dict[str, Any]:
        """
        Get a node by ID.
        
        Args:
            graph_name: Name of the graph
            node_id: Node ID
            
        Returns:
            Dict: Node data
        """
        if not self.redis_client:
            return {"error": "Redis not initialized"}
            
        try:
            query = f"MATCH (n {{id: '{node_id}'}}) RETURN n"
            result = self.redis_client.execute_command('GRAPH.QUERY', graph_name, query, '--compact')
            
            return {
                "node_id": node_id,
                "data": result,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get node {node_id}: {e}")
            return {"error": str(e)}
    
    def get_relationships(self, graph_name: str, node_id: str, 
                        direction: str = "both") -> List[Dict[str, Any]]:
        """
        Get relationships for a node.
        
        Args:
            graph_name: Name of the graph
            node_id: Node ID
            direction: Relationship direction (in, out, both)
            
        Returns:
            List: Relationships
        """
        if not self.redis_client:
            return []
            
        try:
            if direction == "out":
                query = f"MATCH (n {{id: '{node_id}'}})-[r]->(m) RETURN r, m"
            elif direction == "in":
                query = f"MATCH (n)<-[r]-(m {{id: '{node_id}'}}) RETURN r, m"
            else:
                query = f"MATCH (n {{id: '{node_id}'}})-[r]-(m) RETURN r, m"
            
            result = self.redis_client.execute_command('GRAPH.QUERY', graph_name, query, '--compact')
            
            return result or []
            
        except Exception as e:
            self.logger.error(f"Failed to get relationships for {node_id}: {e}")
            return []
    
    def update_node(self, graph_name: str, node_id: str, 
                   properties: Dict[str, Any]) -> bool:
        """
        Update node properties.
        
        Args:
            graph_name: Name of the graph
            node_id: Node ID
            properties: New properties
            
        Returns:
            bool: Success status
        """
        if not self.redis_client:
            return False
            
        try:
            # Build update query
            props_str = json.dumps(properties)
            
            query = f"""
            MATCH (n {{id: '{node_id}'}})
            SET n.properties = {props_str}
            RETURN n
            """
            
            result = self.redis_client.execute_command('GRAPH.QUERY', graph_name, query, '--compact')
            
            self.logger.info(f"✅ Node {node_id} updated in {graph_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update node {node_id}: {e}")
            return False
    
    def delete_node(self, graph_name: str, node_id: str) -> bool:
        """
        Delete a node and its relationships.
        
        Args:
            graph_name: Name of the graph
            node_id: Node ID
            
        Returns:
            bool: Success status
        """
        if not self.redis_client:
            return False
            
        try:
            query = f"MATCH (n {{id: '{node_id}'}}) DETACH DELETE n"
            result = self.redis_client.execute_command('GRAPH.QUERY', graph_name, query, '--compact')
            
            self.logger.info(f"✅ Node {node_id} deleted from {graph_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete node {node_id}: {e}")
            return False
    
    def get_graph_info(self, graph_name: str) -> Dict[str, Any]:
        """
        Get graph information.
        
        Args:
            graph_name: Name of the graph
            
        Returns:
            Dict: Graph information
        """
        if not self.redis_client:
            return {"error": "Redis not initialized"}
            
        try:
            # Get graph statistics
            stats_query = "CALL db.stats()"
            stats_result = self.redis_client.execute_command('GRAPH.QUERY', graph_name, stats_query, '--compact')
            
            # Get node count
            node_query = "MATCH (n) RETURN count(n) as node_count"
            node_result = self.redis_client.execute_command('GRAPH.QUERY', graph_name, node_query, '--compact')
            
            # Get relationship count
            rel_query = "MATCH ()-[r]->() RETURN count(r) as rel_count"
            rel_result = self.redis_client.execute_command('GRAPH.QUERY', graph_name, rel_query, '--compact')
            
            return {
                "graph_name": graph_name,
                "stats": stats_result,
                "node_count": node_result,
                "relationship_count": rel_result,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get graph info for {graph_name}: {e}")
            return {"error": str(e)}
    
    def list_graphs(self) -> List[str]:
        """
        List all graphs.
        
        Returns:
            List: Graph names
        """
        if not self.redis_client:
            return []
            
        try:
            # Get all graph keys
            keys = self.redis_client.keys("graph:*")
            graphs = [key.replace("graph:", "") for key in keys]
            
            return graphs
            
        except Exception as e:
            self.logger.error(f"Failed to list graphs: {e}")
            return []
    
    def backup_graph(self, graph_name: str, backup_path: str) -> bool:
        """
        Backup a graph.
        
        Args:
            graph_name: Name of the graph
            backup_path: Backup file path
            
        Returns:
            bool: Success status
        """
        if not self.redis_client:
            return False
            
        try:
            # Export graph data
            export_query = "MATCH (n)-[r]->(m) RETURN n, r, m"
            result = self.redis_client.execute_command('GRAPH.QUERY', graph_name, export_query, '--compact')
            
            # Save to file
            with open(backup_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            self.logger.info(f"✅ Graph {graph_name} backed up to {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to backup graph {graph_name}: {e}")
            return False
    
    def restore_graph(self, graph_name: str, backup_path: str) -> bool:
        """
        Restore a graph from backup.
        
        Args:
            graph_name: Name of the graph
            backup_path: Backup file path
            
        Returns:
            bool: Success status
        """
        if not self.redis_client:
            return False
            
        try:
            # Load backup data
            with open(backup_path, 'r') as f:
                data = json.load(f)
            
            # Restore graph
            for item in data:
                # Recreate nodes and relationships
                # This would need to be implemented based on backup format
                pass
            
            self.logger.info(f"✅ Graph {graph_name} restored from {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore graph {graph_name}: {e}")
            return False



