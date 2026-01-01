#!/usr/bin/env python3
"""
ArangoDB Content Metadata Adapter - Raw Technology Client

Raw ArangoDB client wrapper for content metadata operations.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw ArangoDB operations for content metadata
HOW (Infrastructure Implementation): I use real ArangoDB client with no business logic
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

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

class ArangoContentMetadataAdapter:
    """Raw ArangoDB client wrapper for content metadata operations - no business logic."""
    
    def __init__(self, hosts: str, database: str, username: str, password: str):
        """Initialize ArangoDB content metadata adapter with real connection."""
        self.hosts = hosts
        self.database = database
        self.username = username
        self.password = password
        
        # Content-specific collections
        self.CONTENT_METADATA_COLLECTION = "content_metadata"
        self.CONTENT_SCHEMAS_COLLECTION = "content_schemas"
        self.CONTENT_INSIGHTS_COLLECTION = "content_insights"
        self.CONTENT_RELATIONSHIPS_COLLECTION = "content_relationships"
        self.CONTENT_ANALYSIS_COLLECTION = "content_analysis"
        
        # Create ArangoDB client (private - use wrapper methods instead)
        self._client = ArangoClient(hosts=hosts)
        self._db: StandardDatabase = self._client.db(database, username, password)
        # Keep client and db as aliases for backward compatibility (will be removed)
        self.client = self._client
        self.db = self._db
        
        logger.info(f"✅ ArangoDB Content Metadata adapter initialized with database: {database}")
    
    # ============================================================================
    # RAW CONTENT METADATA OPERATIONS
    # ============================================================================
    
    async def create_content_metadata(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Raw content metadata creation - no business logic."""
        try:
            # Prepare document
            document = {
                "_key": content_data.get("content_id", str(uuid.uuid4())),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                **content_data
            }
            
            result = self._db.collection(self.CONTENT_METADATA_COLLECTION).insert(document)
            logger.debug(f"✅ Content metadata created: {result['_key']}")
            return result
            
        except ArangoError as e:
            logger.error(f"❌ Failed to create content metadata: {e}")
            raise
    
    async def get_content_metadata(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Raw content metadata retrieval - no business logic."""
        try:
            result = self._db.collection(self.CONTENT_METADATA_COLLECTION).get(content_id)
            if result:
                logger.debug(f"✅ Content metadata retrieved: {content_id}")
            return result
            
        except ArangoError as e:
            logger.error(f"❌ Failed to get content metadata {content_id}: {e}")
            return None
    
    async def update_content_metadata(self, content_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Raw content metadata update - no business logic."""
        try:
            # Add update timestamp
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            result = self._db.collection(self.CONTENT_METADATA_COLLECTION).update(content_id, updates)
            logger.debug(f"✅ Content metadata updated: {content_id}")
            return result
            
        except ArangoError as e:
            logger.error(f"❌ Failed to update content metadata {content_id}: {e}")
            raise
    
    async def delete_content_metadata(self, content_id: str) -> bool:
        """Raw content metadata deletion - no business logic."""
        try:
            result = self._db.collection(self.CONTENT_METADATA_COLLECTION).delete(content_id)
            logger.debug(f"✅ Content metadata deleted: {content_id}")
            return result
            
        except ArangoError as e:
            logger.error(f"❌ Failed to delete content metadata {content_id}: {e}")
            return False
    
    async def search_content_metadata(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Raw content metadata search - no business logic."""
        try:
            # Build AQL query
            aql = f"FOR doc IN {self.CONTENT_METADATA_COLLECTION}"
            bind_vars = {}
            
            if "content_type" in query:
                aql += " FILTER doc.content_type == @content_type"
                bind_vars["content_type"] = query["content_type"]
            
            if "file_uuid" in query:
                aql += " FILTER doc.file_uuid == @file_uuid"
                bind_vars["file_uuid"] = query["file_uuid"]
            
            if "user_id" in query:
                aql += " FILTER doc.user_id == @user_id"
                bind_vars["user_id"] = query["user_id"]
            
            aql += " RETURN doc"
            
            cursor = self._db.aql.execute(aql, bind_vars=bind_vars)
            results = list(cursor)
            
            logger.debug(f"✅ Content metadata search returned {len(results)} results")
            return results
            
        except ArangoError as e:
            logger.error(f"❌ Failed to search content metadata: {e}")
            return []
    
    # ============================================================================
    # RAW CONTENT SCHEMA OPERATIONS
    # ============================================================================
    
    async def create_content_schema(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """Raw content schema creation - no business logic."""
        try:
            document = {
                "_key": schema_data.get("schema_id", str(uuid.uuid4())),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                **schema_data
            }
            
            result = self._db.collection(self.CONTENT_SCHEMAS_COLLECTION).insert(document)
            logger.debug(f"✅ Content schema created: {result['_key']}")
            return result
            
        except ArangoError as e:
            logger.error(f"❌ Failed to create content schema: {e}")
            raise
    
    async def get_content_schema(self, schema_id: str) -> Optional[Dict[str, Any]]:
        """Raw content schema retrieval - no business logic."""
        try:
            result = self._db.collection(self.CONTENT_SCHEMAS_COLLECTION).get(schema_id)
            if result:
                logger.debug(f"✅ Content schema retrieved: {schema_id}")
            return result
            
        except ArangoError as e:
            logger.error(f"❌ Failed to get content schema {schema_id}: {e}")
            return None
    
    async def search_schemas_by_pattern(self, pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Raw schema pattern search - no business logic."""
        try:
            aql = f"FOR doc IN {self.CONTENT_SCHEMAS_COLLECTION}"
            bind_vars = {}
            
            if "schema_type" in pattern:
                aql += " FILTER doc.schema_type == @schema_type"
                bind_vars["schema_type"] = pattern["schema_type"]
            
            if "content_id" in pattern:
                aql += " FILTER doc.content_id == @content_id"
                bind_vars["content_id"] = pattern["content_id"]
            
            aql += " RETURN doc"
            
            cursor = self._db.aql.execute(aql, bind_vars=bind_vars)
            results = list(cursor)
            
            logger.debug(f"✅ Schema pattern search returned {len(results)} results")
            return results
            
        except ArangoError as e:
            logger.error(f"❌ Failed to search schemas by pattern: {e}")
            return []
    
    # ============================================================================
    # RAW CONTENT INSIGHTS OPERATIONS
    # ============================================================================
    
    async def create_content_insight(self, insight_data: Dict[str, Any]) -> Dict[str, Any]:
        """Raw content insight creation - no business logic."""
        try:
            document = {
                "_key": insight_data.get("insight_id", str(uuid.uuid4())),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                **insight_data
            }
            
            result = self._db.collection(self.CONTENT_INSIGHTS_COLLECTION).insert(document)
            logger.debug(f"✅ Content insight created: {result['_key']}")
            return result
            
        except ArangoError as e:
            logger.error(f"❌ Failed to create content insight: {e}")
            raise
    
    async def get_content_insights(self, content_id: str) -> List[Dict[str, Any]]:
        """Raw content insights retrieval - no business logic."""
        try:
            aql = f"""
            FOR insight IN {self.CONTENT_INSIGHTS_COLLECTION}
            FILTER insight.content_id == @content_id
            RETURN insight
            """
            
            cursor = self._db.aql.execute(aql, bind_vars={"content_id": content_id})
            results = list(cursor)
            
            logger.debug(f"✅ Retrieved {len(results)} insights for content: {content_id}")
            return results
            
        except ArangoError as e:
            logger.error(f"❌ Failed to get content insights {content_id}: {e}")
            return []
    
    async def search_insights_by_type(self, insight_type: str) -> List[Dict[str, Any]]:
        """Raw insights search by type - no business logic."""
        try:
            aql = f"""
            FOR insight IN {self.CONTENT_INSIGHTS_COLLECTION}
            FILTER insight.insight_type == @insight_type
            RETURN insight
            """
            
            cursor = self._db.aql.execute(aql, bind_vars={"insight_type": insight_type})
            results = list(cursor)
            
            logger.debug(f"✅ Retrieved {len(results)} insights of type: {insight_type}")
            return results
            
        except ArangoError as e:
            logger.error(f"❌ Failed to search insights by type {insight_type}: {e}")
            return []
    
    # ============================================================================
    # RAW CONTENT RELATIONSHIP OPERATIONS
    # ============================================================================
    
    async def create_content_relationship(self, parent_id: str, child_id: str, 
                                        relationship_type: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Raw content relationship creation - no business logic."""
        try:
            document = {
                "_key": f"{parent_id}_{child_id}_{relationship_type}",
                "parent_content_id": parent_id,
                "child_content_id": child_id,
                "relationship_type": relationship_type,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            result = self._db.collection(self.CONTENT_RELATIONSHIPS_COLLECTION).insert(document)
            logger.debug(f"✅ Content relationship created: {parent_id} -> {child_id}")
            return result
            
        except ArangoError as e:
            logger.error(f"❌ Failed to create content relationship: {e}")
            raise
    
    async def get_content_relationships(self, content_id: str, direction: str = "both") -> List[Dict[str, Any]]:
        """Raw content relationships retrieval - no business logic."""
        try:
            relationships = []
            
            if direction in ("parent", "both"):
                aql = f"""
                FOR rel IN {self.CONTENT_RELATIONSHIPS_COLLECTION}
                FILTER rel.child_content_id == @content_id
                RETURN rel
                """
                cursor = self._db.aql.execute(aql, bind_vars={"content_id": content_id})
                relationships.extend(list(cursor))
            
            if direction in ("child", "both"):
                aql = f"""
                FOR rel IN {self.CONTENT_RELATIONSHIPS_COLLECTION}
                FILTER rel.parent_content_id == @content_id
                RETURN rel
                """
                cursor = self._db.aql.execute(aql, bind_vars={"content_id": content_id})
                relationships.extend(list(cursor))
            
            logger.debug(f"✅ Retrieved {len(relationships)} relationships for content: {content_id}")
            return relationships
            
        except ArangoError as e:
            logger.error(f"❌ Failed to get content relationships {content_id}: {e}")
            return []
    
    # ============================================================================
    # RAW CONTENT ANALYSIS OPERATIONS
    # ============================================================================
    
    async def create_content_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Raw content analysis creation - no business logic."""
        try:
            document = {
                "_key": analysis_data.get("analysis_id", str(uuid.uuid4())),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                **analysis_data
            }
            
            result = self._db.collection(self.CONTENT_ANALYSIS_COLLECTION).insert(document)
            logger.debug(f"✅ Content analysis created: {result['_key']}")
            return result
            
        except ArangoError as e:
            logger.error(f"❌ Failed to create content analysis: {e}")
            raise
    
    async def get_content_analysis(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Raw content analysis retrieval - no business logic."""
        try:
            aql = f"""
            FOR analysis IN {self.CONTENT_ANALYSIS_COLLECTION}
            FILTER analysis.content_id == @content_id
            RETURN analysis
            """
            
            cursor = self._db.aql.execute(aql, bind_vars={"content_id": content_id})
            results = list(cursor)
            
            if results:
                logger.debug(f"✅ Content analysis retrieved: {content_id}")
                return results[0]  # Return most recent analysis
            
            return None
            
        except ArangoError as e:
            logger.error(f"❌ Failed to get content analysis {content_id}: {e}")
            return None
    
    # ============================================================================
    # RAW AQL QUERY OPERATIONS
    # ============================================================================
    
    async def execute_content_aql(self, query: str, bind_vars: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Raw AQL query execution - no business logic."""
        try:
            cursor = self._db.aql.execute(query, bind_vars=bind_vars or {})
            results = list(cursor)
            
            logger.debug(f"✅ Executed content AQL query, returned {len(results)} results")
            return results
            
        except ArangoError as e:
            logger.error(f"❌ Failed to execute content AQL query: {e}")
            return []
    
    # ============================================================================
    # RAW COLLECTION MANAGEMENT
    # ============================================================================
    
    async def create_content_collections(self) -> bool:
        """Raw collection creation - no business logic."""
        try:
            collections = [
                self.CONTENT_METADATA_COLLECTION,
                self.CONTENT_SCHEMAS_COLLECTION,
                self.CONTENT_INSIGHTS_COLLECTION,
                self.CONTENT_RELATIONSHIPS_COLLECTION,
                self.CONTENT_ANALYSIS_COLLECTION
            ]
            
            for collection_name in collections:
                if not self._db.has_collection(collection_name):
                    self._db.create_collection(collection_name)
                    logger.info(f"✅ Created collection: {collection_name}")
            
            return True
            
        except ArangoError as e:
            logger.error(f"❌ Failed to create content collections: {e}")
            return False
    
    async def create_content_indexes(self) -> bool:
        """Raw index creation - no business logic."""
        try:
            # Content metadata indexes
            if self._db.has_collection(self.CONTENT_METADATA_COLLECTION):
                collection = self._db.collection(self.CONTENT_METADATA_COLLECTION)
                collection.add_index({'type': 'hash', 'fields': ['content_id']})
                collection.add_index({'type': 'hash', 'fields': ['file_uuid']})
                collection.add_index({'type': 'hash', 'fields': ['content_type']})
                collection.add_index({'type': 'hash', 'fields': ['user_id']})
                collection.add_index({'type': 'skiplist', 'fields': ['created_at']})
            
            # Content schemas indexes
            if self._db.has_collection(self.CONTENT_SCHEMAS_COLLECTION):
                collection = self._db.collection(self.CONTENT_SCHEMAS_COLLECTION)
                collection.add_index({'type': 'hash', 'fields': ['schema_id']})
                collection.add_index({'type': 'hash', 'fields': ['content_id']})
                collection.add_index({'type': 'hash', 'fields': ['schema_type']})
            
            # Content insights indexes
            if self._db.has_collection(self.CONTENT_INSIGHTS_COLLECTION):
                collection = self._db.collection(self.CONTENT_INSIGHTS_COLLECTION)
                collection.add_index({'type': 'hash', 'fields': ['insight_id']})
                collection.add_index({'type': 'hash', 'fields': ['content_id']})
                collection.add_index({'type': 'hash', 'fields': ['insight_type']})
                collection.add_index({'type': 'skiplist', 'fields': ['confidence_score']})
            
            # Content relationships indexes
            if self._db.has_collection(self.CONTENT_RELATIONSHIPS_COLLECTION):
                collection = self._db.collection(self.CONTENT_RELATIONSHIPS_COLLECTION)
                collection.add_index({'type': 'hash', 'fields': ['parent_content_id']})
                collection.add_index({'type': 'hash', 'fields': ['child_content_id']})
                collection.add_index({'type': 'hash', 'fields': ['relationship_type']})
            
            logger.info("✅ Created content metadata indexes")
            return True
            
        except ArangoError as e:
            logger.error(f"❌ Failed to create content indexes: {e}")
            return False
    
    # ============================================================================
    # RAW HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Raw health check - no business logic."""
        try:
            # Test basic connection
            version = self._db.version()
            
            return {
                "status": "healthy",
                "message": "ArangoDB Content Metadata adapter is operational",
                "version": version,
                "database": self.database,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"ArangoDB Content Metadata adapter error: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def close(self):
        """Close the ArangoDB connection."""
        try:
            # ArangoDB client doesn't need explicit closing
            logger.info("✅ ArangoDB Content Metadata adapter closed")
        except Exception as e:
            logger.error(f"❌ Error closing ArangoDB Content Metadata adapter: {e}")




