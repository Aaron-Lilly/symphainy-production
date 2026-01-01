#!/usr/bin/env python3
"""
ArangoDB Infrastructure Adapter

Raw ArangoDB bindings for metrics storage and telemetry data.
Thin wrapper around ArangoDB Python driver with no business logic.
"""

import logging
from typing import Dict, Any, List, Optional

try:
    from arango import ArangoClient
    from arango.database import StandardDatabase
    from arango.collection import StandardCollection
except ImportError:
    ArangoClient = None
    StandardDatabase = None
    StandardCollection = None


class ArangoAdapter:
    """Raw ArangoDB adapter - thin wrapper around ArangoDB Python driver."""
    
    def __init__(self, hosts: str, username: str = None, password: str = None, 
                 database: str = "telemetry", **kwargs):
        """
        Initialize ArangoDB adapter.
        
        Args:
            hosts: ArangoDB host URL
            username: Database username
            password: Database password
            database: Database name
        """
        self.hosts = hosts
        self.username = username
        self.password = password
        self.database_name = database
        self.logger = logging.getLogger("ArangoAdapter")
        
        # ArangoDB components (private - use wrapper methods instead)
        self._client = None
        self._db = None
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ArangoDB client."""
        if ArangoClient is None:
            self.logger.warning("ArangoDB driver not installed")
            return
        
        try:
            # Create client (private)
            self._client = ArangoClient(hosts=self.hosts)
            
            # Connect to database (private)
            if self.username and self.password:
                self._db = self._client.db(
                    self.database_name,
                    username=self.username,
                    password=self.password
                )
            else:
                self._db = self._client.db(self.database_name)
            
            # Keep client and db as aliases for backward compatibility (will be removed)
            self.client = self._client
            self.db = self._db
            
            self.logger.info("✅ ArangoDB adapter initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ArangoDB: {e}")
    
    def create_collection(self, name: str, collection_type: str = "document") -> bool:
        """Create a collection."""
        if self._db is None:
            return False
        
        try:
            self._db.create_collection(name, type=collection_type)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create collection {name}: {e}")
            return False
    
    def get_collection(self, name: str) -> Optional[StandardCollection]:
        """Get a collection."""
        if self._db is None:
            return None
        
        try:
            return self._db.collection(name)
        except Exception as e:
            self.logger.error(f"Failed to get collection {name}: {e}")
            return None
    
    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> Optional[str]:
        """Insert a document."""
        collection = self.get_collection(collection_name)
        if collection is None:
            return None
        
        try:
            result = collection.insert(document)
            return result.get("_key")
        except Exception as e:
            self.logger.error(f"Failed to insert document: {e}")
            return None
    
    def update_document(self, collection_name: str, key: str, document: Dict[str, Any]) -> bool:
        """Update a document."""
        collection = self.get_collection(collection_name)
        if collection is None:
            return False
        
        try:
            collection.update({"_key": key, **document})
            return True
        except Exception as e:
            self.logger.error(f"Failed to update document {key}: {e}")
            return False
    
    def delete_document(self, collection_name: str, key: str) -> bool:
        """Delete a document."""
        collection = self.get_collection(collection_name)
        if collection is None:
            return False
        
        try:
            collection.delete({"_key": key})
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete document {key}: {e}")
            return False
    
    def get_document(self, collection_name: str, key: str) -> Optional[Dict[str, Any]]:
        """Get a document by key."""
        collection = self.get_collection(collection_name)
        if collection is None:
            return None
        
        try:
            return collection.get({"_key": key})
        except Exception as e:
            self.logger.error(f"Failed to get document {key}: {e}")
            return None
    
    def query(self, aql: str, bind_vars: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute AQL query."""
        if self._db is None:
            return []
        
        try:
            cursor = self._db.aql.execute(aql, bind_vars=bind_vars or {})
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Failed to execute query: {e}")
            return []
    
    def create_index(self, collection_name: str, fields: List[str], 
                    index_type: str = "persistent") -> bool:
        """Create an index."""
        collection = self.get_collection(collection_name)
        if collection is None:
            return False
        
        try:
            collection.add_index({
                "type": index_type,
                "fields": fields
            })
            return True
        except Exception as e:
            self.logger.error(f"Failed to create index: {e}")
            return False



