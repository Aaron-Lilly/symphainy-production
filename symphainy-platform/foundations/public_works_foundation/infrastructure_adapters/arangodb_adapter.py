#!/usr/bin/env python3
"""
ArangoDB Adapter - Raw Technology Client

Raw ArangoDB client wrapper with no business logic.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw ArangoDB operations for complex state persistence
HOW (Infrastructure Implementation): I use real ArangoDB client with no business logic
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import json
import logging

try:
    from arango import ArangoClient
    from arango.database import StandardDatabase
    from arango.collection import StandardCollection
    from arango.exceptions import ArangoError
except ImportError:
    # Mock ArangoDB classes for development
    class ArangoClient:
        def __init__(self, hosts): pass
        def db(self, name, username, password): return None
    class StandardDatabase:
        def __init__(self): pass
    class StandardCollection:
        def __init__(self): pass
    class ArangoError(Exception): pass

logger = logging.getLogger(__name__)

class ArangoDBAdapter:
    """
    Raw ArangoDB client wrapper - no business logic.
    
    This adapter provides direct access to ArangoDB operations without
    any business logic or abstraction. It's the raw technology layer.
    """
    
    def __init__(self, hosts: str, database: str, username: str, password: str):
        """
        Initialize ArangoDB adapter (lightweight - no connection).
        
        CRITICAL: This is now lazy initialization to prevent SSH session crashes.
        Connection happens in async connect() method with timeout.
        """
        self.hosts = hosts
        self.database = database
        self.username = username
        self.password = password
        
        # Create ArangoDB client (private - use wrapper methods instead)
        # Client creation is lightweight and doesn't connect
        self._client = ArangoClient(hosts=hosts)
        
        # Connection state (will be set in connect())
        self._db: Optional[StandardDatabase] = None
        self._is_connected = False
        
        # Keep client and db as aliases for backward compatibility (will be removed)
        self.client = self._client
        self.db = None  # Will be set after connect()
        
        logger.info(f"✅ ArangoDB adapter initialized (lazy) for database: {database}")
    
    # ============================================================================
    # RAW DOCUMENT OPERATIONS
    # ============================================================================
    
    async def _ensure_connected(self):
        """Ensure adapter is connected (lazy connection)."""
        if not self._is_connected or self._db is None:
            await self.connect()
    
    async def create_document(self, collection: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """Raw document creation - no business logic."""
        await self._ensure_connected()
        
        try:
            # Ensure collection exists
            if not self._db.has_collection(collection):
                self._db.create_collection(collection)
                logger.debug(f"✅ Created collection: {collection}")
            
            result = self._db.collection(collection).insert(document)
            logger.debug(f"✅ Document created in {collection}: {result['_key']}")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to create document in {collection}: {e}")
            raise
    
    async def get_document(self, collection: str, key: str) -> Optional[Dict[str, Any]]:
        """Raw document retrieval - no business logic."""
        await self._ensure_connected()
        
        try:
            result = self._db.collection(collection).get(key)
            if result:
                logger.debug(f"✅ Document retrieved from {collection}: {key}")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to get document from {collection}: {e}")
            return None
    
    async def update_document(self, collection: str, key: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """Raw document update - no business logic."""
        await self._ensure_connected()
        
        try:
            # ArangoDB update() expects document with _key, not separate key parameter
            # Merge key into document
            document_with_key = {**document, "_key": key}
            result = self._db.collection(collection).update(document_with_key)
            logger.debug(f"✅ Document updated in {collection}: {key}")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to update document in {collection}: {e}")
            raise
    
    async def delete_document(self, collection: str, key: str) -> bool:
        """Raw document deletion - no business logic."""
        await self._ensure_connected()
        
        try:
            result = self._db.collection(collection).delete(key)
            logger.debug(f"✅ Document deleted from {collection}: {key}")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to delete document from {collection}: {e}")
            return False
    
    # ============================================================================
    # RAW QUERY OPERATIONS
    # ============================================================================
    
    async def execute_aql(self, query: str, bind_vars: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Raw AQL query execution - no business logic."""
        await self._ensure_connected()
        
        try:
            cursor = self._db.aql.execute(query, bind_vars=bind_vars or {})
            results = [doc for doc in cursor]
            logger.debug(f"✅ AQL query executed: {len(results)} results")
            return results
        except ArangoError as e:
            logger.error(f"❌ Failed to execute AQL query: {e}")
            raise
    
    async def find_documents(self, collection: str, filter_conditions: Dict[str, Any] = None, 
                           limit: int = None, offset: int = None) -> List[Dict[str, Any]]:
        """Raw document search - no business logic."""
        await self._ensure_connected()
        
        try:
            # ArangoDB find() doesn't support offset directly - use AQL for offset
            if offset is not None and offset > 0:
                # Use AQL query for offset support
                aql_query = f"""
                FOR doc IN {collection}
                    FILTER doc == doc
                    LIMIT {offset}, {limit if limit else 1000}
                    RETURN doc
                """
                cursor = self._db.aql.execute(aql_query, bind_vars=filter_conditions or {})
                results = [doc for doc in cursor]
            else:
                # Simple find without offset
                cursor = self._db.collection(collection).find(filter_conditions or {}, limit=limit)
                results = [doc for doc in cursor]
            logger.debug(f"✅ Documents found in {collection}: {len(results)} results")
            return results
        except ArangoError as e:
            logger.error(f"❌ Failed to find documents in {collection}: {e}")
            raise
    
    # ============================================================================
    # RAW GRAPH OPERATIONS
    # ============================================================================
    
    async def create_graph(self, name: str, edge_definitions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Raw graph creation - no business logic."""
        await self._ensure_connected()
        
        try:
            result = self._db.create_graph(name, edge_definitions=edge_definitions)
            logger.debug(f"✅ Graph created: {name}")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to create graph {name}: {e}")
            raise
    
    async def get_graph(self, name: str) -> Optional[Dict[str, Any]]:
        """Raw graph retrieval - no business logic."""
        await self._ensure_connected()
        
        try:
            result = self._db.graph(name)
            logger.debug(f"✅ Graph retrieved: {name}")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to get graph {name}: {e}")
            return None
    
    async def create_vertex(self, graph: str, collection: str, vertex: Dict[str, Any]) -> Dict[str, Any]:
        """Raw vertex creation - no business logic."""
        await self._ensure_connected()
        
        try:
            result = self._db.graph(graph).create_vertex(collection, vertex)
            logger.debug(f"✅ Vertex created in graph {graph}: {result['_key']}")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to create vertex in graph {graph}: {e}")
            raise
    
    async def create_edge(self, graph: str, collection: str, edge: Dict[str, Any]) -> Dict[str, Any]:
        """Raw edge creation - no business logic."""
        await self._ensure_connected()
        
        try:
            result = self._db.graph(graph).create_edge(collection, edge)
            logger.debug(f"✅ Edge created in graph {graph}: {result['_key']}")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to create edge in graph {graph}: {e}")
            raise
    
    # ============================================================================
    # RAW COLLECTION OPERATIONS
    # ============================================================================
    
    async def create_collection(self, name: str, collection_type: str = "document") -> Dict[str, Any]:
        """Raw collection creation - no business logic."""
        await self._ensure_connected()
        
        try:
            result = self._db.create_collection(name, type=collection_type)
            logger.debug(f"✅ Collection created: {name}")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to create collection {name}: {e}")
            raise
    
    async def get_collection(self, name: str) -> Optional[StandardCollection]:
        """Raw collection retrieval - no business logic."""
        await self._ensure_connected()
        
        try:
            result = self._db.collection(name)
            logger.debug(f"✅ Collection retrieved: {name}")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to get collection {name}: {e}")
            return None
    
    async def collection_exists(self, name: str) -> bool:
        """Raw collection existence check - no business logic."""
        await self._ensure_connected()
        
        try:
            result = self._db.has_collection(name)
            logger.debug(f"✅ Collection exists check: {name} = {result}")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to check collection existence {name}: {e}")
            return False
    
    # ============================================================================
    # RAW TRANSACTION OPERATIONS
    # ============================================================================
    
    async def begin_transaction(self) -> str:
        """Raw transaction begin - no business logic."""
        await self._ensure_connected()
        
        try:
            result = self._db.begin_transaction()
            logger.debug(f"✅ Transaction begun: {result}")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to begin transaction: {e}")
            raise
    
    async def commit_transaction(self, transaction_id: str) -> bool:
        """Raw transaction commit - no business logic."""
        await self._ensure_connected()
        
        try:
            result = self._db.commit_transaction(transaction_id)
            logger.debug(f"✅ Transaction committed: {transaction_id}")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to commit transaction {transaction_id}: {e}")
            return False
    
    async def abort_transaction(self, transaction_id: str) -> bool:
        """Raw transaction abort - no business logic."""
        await self._ensure_connected()
        
        try:
            result = self._db.abort_transaction(transaction_id)
            logger.debug(f"✅ Transaction aborted: {transaction_id}")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to abort transaction {transaction_id}: {e}")
            return False
    
    # ============================================================================
    # RAW INDEX OPERATIONS
    # ============================================================================
    
    async def create_index(self, collection: str, index_type: str, fields: List[str], 
                         unique: bool = False) -> Dict[str, Any]:
        """Raw index creation - no business logic."""
        await self._ensure_connected()
        
        try:
            result = self._db.collection(collection).add_index({
                "type": index_type,
                "fields": fields,
                "unique": unique
            })
            logger.debug(f"✅ Index created on {collection}: {fields}")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to create index on {collection}: {e}")
            raise
    
    # ============================================================================
    # RAW UTILITY OPERATIONS
    # ============================================================================
    
    async def get_database_info(self) -> Dict[str, Any]:
        """Raw database info retrieval - no business logic."""
        await self._ensure_connected()
        
        try:
            result = self._db.properties()
            logger.debug(f"✅ Database info retrieved")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to get database info: {e}")
            return {}
    
    async def get_collections(self) -> List[Dict[str, Any]]:
        """Raw collections list - no business logic."""
        await self._ensure_connected()
        
        try:
            result = self._db.collections()
            logger.debug(f"✅ Collections list retrieved: {len(result)} collections")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to get collections list: {e}")
            return []
    
    async def get_graphs(self) -> List[Dict[str, Any]]:
        """Raw graphs list - no business logic."""
        await self._ensure_connected()
        
        try:
            result = self._db.graphs()
            logger.debug(f"✅ Graphs list retrieved: {len(result)} graphs")
            return result
        except ArangoError as e:
            logger.error(f"❌ Failed to get graphs list: {e}")
            return []
    
    # ============================================================================
    # RAW CONNECTION OPERATIONS
    # ============================================================================
    
    async def connect(self, timeout: float = 10.0) -> bool:
        """
        Connect to ArangoDB with timeout to prevent hanging.
        
        CRITICAL: This method must be called before using the adapter.
        It ensures database exists and establishes connection with timeout.
        
        Args:
            timeout: Connection timeout in seconds (default 10.0)
            
        Returns:
            bool: True if connection successful
            
        Raises:
            ConnectionError: If ArangoDB is unavailable (with timeout to prevent hanging)
        """
        import asyncio
        
        if self._is_connected and self._db is not None:
            logger.debug("✅ ArangoDB already connected")
            return True
        
        try:
            loop = asyncio.get_event_loop()
            
            # Step 1: Ensure database exists (with timeout)
            try:
                logger.debug(f"🔌 Checking/creating ArangoDB database: {self.database}")
                sys_db_result = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: self._client.db('_system', username=self.username, password=self.password)
                    ),
                    timeout=timeout
                )
                
                # Check if database exists
                databases_result = await asyncio.wait_for(
                    loop.run_in_executor(None, sys_db_result.databases),
                    timeout=timeout
                )
                
                if self.database not in databases_result:
                    logger.info(f"📦 Creating ArangoDB database: {self.database}")
                    await asyncio.wait_for(
                        loop.run_in_executor(None, sys_db_result.create_database, self.database),
                        timeout=timeout
                    )
                    logger.info(f"✅ Created ArangoDB database: {self.database}")
                else:
                    logger.debug(f"✅ ArangoDB database exists: {self.database}")
            except asyncio.TimeoutError:
                error_msg = f"ArangoDB database check/create timed out after {timeout} seconds - ArangoDB is CRITICAL infrastructure"
                logger.error(f"❌ {error_msg}")
                raise ConnectionError(error_msg)
            except Exception as e:
                logger.warning(f"⚠️ Could not check/create database (may not have permissions): {e}")
                # Continue - connection might still work if database exists
            
            # Step 2: Connect to the database (with timeout)
            try:
                logger.debug(f"🔌 Connecting to ArangoDB database: {self.database}")
                self._db = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: self._client.db(self.database, username=self.username, password=self.password)
                    ),
                    timeout=timeout
                )
                
                # Verify connection with a quick test
                await asyncio.wait_for(
                    loop.run_in_executor(None, self._db.properties),
                    timeout=5.0
                )
                
                self._is_connected = True
                self.db = self._db  # Update alias
                logger.info(f"✅ ArangoDB connected successfully ({self.hosts}/{self.database})")
                return True
                
            except asyncio.TimeoutError:
                error_msg = f"ArangoDB connection timed out after {timeout} seconds - ArangoDB is CRITICAL infrastructure and must be available"
                logger.error(f"❌ {error_msg}")
                self._db = None
                self._is_connected = False
                raise ConnectionError(error_msg)
            except Exception as e:
                error_msg = f"ArangoDB connection failed - ArangoDB is CRITICAL infrastructure: {e}"
                logger.error(f"❌ {error_msg}")
                self._db = None
                self._is_connected = False
                raise ConnectionError(error_msg)
                
        except ConnectionError:
            # Re-raise ConnectionError
            raise
        except Exception as e:
            error_msg = f"ArangoDB connection failed unexpectedly: {e}"
            logger.error(f"❌ {error_msg}")
            self._db = None
            self._is_connected = False
            raise ConnectionError(error_msg)
    
    async def test_connection(self) -> bool:
        """
        Test existing connection with timeout - no business logic.
        
        ArangoDB is CRITICAL infrastructure - if unavailable, should fail gracefully.
        
        Returns:
            bool: True if connection successful
            
        Raises:
            ConnectionError: If ArangoDB is unavailable (with timeout to prevent hanging)
        """
        import asyncio
        
        if not self._is_connected or self._db is None:
            # Try to connect if not already connected
            return await self.connect()
        
        try:
            # Use asyncio timeout to prevent hanging on unavailable ArangoDB
            loop = asyncio.get_event_loop()
            try:
                # Run connection test with timeout (5 seconds)
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, self._db.properties),
                    timeout=5.0
                )
                logger.debug(f"✅ ArangoDB connection test successful")
                return True
            except asyncio.TimeoutError:
                error_msg = "ArangoDB connection timeout - ArangoDB is CRITICAL infrastructure and must be available"
                logger.error(f"❌ {error_msg}")
                self._is_connected = False
                raise ConnectionError(error_msg)
        except ConnectionError:
            # Re-raise ConnectionError
            raise
        except Exception as e:
            error_msg = f"ArangoDB connection test failed - ArangoDB is CRITICAL infrastructure: {e}"
            logger.error(f"❌ {error_msg}")
            self._is_connected = False
            raise ConnectionError(error_msg)
    
    async def close_connection(self) -> bool:
        """Raw connection close - no business logic."""
        try:
            # ArangoDB client doesn't have explicit close method
            logger.debug(f"✅ Connection closed")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to close connection: {e}")
            return False

