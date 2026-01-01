#!/usr/bin/env python3
"""
Mock Infrastructure Adapters - Production-Ready Test Infrastructure

Comprehensive mocks for all infrastructure adapters that mirror production behavior
exactly. These mocks implement the same interfaces as real adapters but use in-memory
storage and simulated behavior to enable reliable testing without external dependencies.

WHAT (Test Infrastructure Role): I provide production-realistic mocks for all infrastructure adapters
HOW (Test Infrastructure Implementation): I implement adapter interfaces with in-memory storage and simulated behavior
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from collections import defaultdict

logger = logging.getLogger(__name__)


# ============================================================================
# SUPABASE FILE MANAGEMENT MOCK ADAPTER
# ============================================================================

class MockSupabaseFileManagementAdapter:
    """Mock Supabase File Management Adapter - mirrors production interface exactly."""
    
    def __init__(self, url: str, service_key: str):
        """Initialize mock Supabase adapter."""
        self.url = url
        self.service_key = service_key
        self._files = {}  # In-memory file storage
        self._connected = False
        self.logger = logging.getLogger("MockSupabaseFileManagementAdapter")
        self.logger.info(f"✅ Mock Supabase File Management adapter initialized with URL: {url}")
    
    async def connect(self) -> bool:
        """Connect to mock Supabase (always succeeds)."""
        self._connected = True
        self.logger.info("✅ Mock Supabase File Management adapter connected")
        return True
    
    async def create_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create file in mock storage."""
        file_uuid = file_data.get("uuid") or f"file_{len(self._files) + 1}"
        file_data["uuid"] = file_uuid
        file_data["created_at"] = datetime.utcnow().isoformat()
        file_data["updated_at"] = datetime.utcnow().isoformat()
        file_data["deleted"] = False
        self._files[file_uuid] = file_data
        return file_data
    
    async def get_file(self, file_uuid: str) -> Optional[Dict[str, Any]]:
        """Get file from mock storage."""
        file_data = self._files.get(file_uuid)
        if file_data and not file_data.get("deleted", False):
            return file_data
        return None
    
    async def update_file(self, file_uuid: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update file in mock storage."""
        if file_uuid not in self._files:
            raise ValueError(f"File {file_uuid} not found")
        self._files[file_uuid].update(updates)
        self._files[file_uuid]["updated_at"] = datetime.utcnow().isoformat()
        return self._files[file_uuid]
    
    async def delete_file(self, file_uuid: str) -> bool:
        """Delete file in mock storage (soft delete)."""
        if file_uuid in self._files:
            self._files[file_uuid]["deleted"] = True
            self._files[file_uuid]["updated_at"] = datetime.utcnow().isoformat()
            return True
        return False
    
    async def list_files(self, user_id: str, tenant_id: Optional[str] = None,
                        filters: Optional[Dict[str, Any]] = None,
                        limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """List files from mock storage."""
        files = [f for f in self._files.values() if not f.get("deleted", False)]
        if user_id:
            files = [f for f in files if f.get("user_id") == user_id]
        if tenant_id:
            files = [f for f in files if f.get("tenant_id") == tenant_id]
        if filters:
            for key, value in filters.items():
                files = [f for f in files if f.get(key) == value]
        if offset:
            files = files[offset:]
        if limit:
            files = files[:limit]
        return files
    
    async def get_file_statistics(self, user_id: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Get file statistics from mock storage."""
        files = [f for f in self._files.values() if not f.get("deleted", False) and f.get("user_id") == user_id]
        if tenant_id:
            files = [f for f in files if f.get("tenant_id") == tenant_id]
        
        # Calculate statistics
        content_types = {}
        file_types = {}
        statuses = {}
        total_size = 0
        
        for file in files:
            ct = file.get("content_type", "unknown")
            content_types[ct] = content_types.get(ct, 0) + 1
            ft = file.get("file_type", "unknown")
            file_types[ft] = file_types.get(ft, 0) + 1
            status = file.get("status", "unknown")
            statuses[status] = statuses.get(status, 0) + 1
            total_size += file.get("file_size", 0)
        
        return {
            "total_files": len(files),
            "total_size": total_size,
            "content_types": content_types,
            "file_types": file_types,
            "statuses": statuses
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for mock adapter."""
        return {
            "status": "healthy" if self._connected else "unhealthy",
            "message": "Mock Supabase adapter is operational",
            "connected": self._connected,
            "files_count": len([f for f in self._files.values() if not f.get("deleted", False)])
        }


# ============================================================================
# OPENTELEMETRY HEALTH MOCK ADAPTER
# ============================================================================

class MockOpenTelemetryHealthAdapter:
    """Mock OpenTelemetry Health Adapter - mirrors production interface exactly."""
    
    def __init__(self, service_name: str = "opentelemetry_health_adapter",
                 endpoint: str = "http://localhost:4317", timeout: int = 30):
        """Initialize mock OpenTelemetry Health adapter."""
        self.service_name = service_name
        self.endpoint = endpoint
        self.timeout = timeout
        self.logger = logging.getLogger("MockOpenTelemetryHealthAdapter")
        self.health_status = "healthy"
        self.last_check_time = None
        self.logger.info(f"Initialized Mock OpenTelemetry Health Adapter: {endpoint}")
    
    async def check_health(self, health_type: Any, context: Any) -> Any:
        """Perform mock health check."""
        from foundations.public_works_foundation.abstraction_contracts.health_protocol import (
            HealthCheck, HealthStatus, HealthType
        )
        
        self.last_check_time = datetime.utcnow()
        
        return HealthCheck(
            check_id=f"mock_otel_{health_type.value if hasattr(health_type, 'value') else str(health_type)}",
            check_name=f"Mock OpenTelemetry Health Check",
            health_type=health_type,
            status=HealthStatus.HEALTHY,
            message="Mock OpenTelemetry health check completed",
            timestamp=self.last_check_time,
            response_time_ms=1.0,
            metadata={"adapter": "mock_opentelemetry", "endpoint": self.endpoint}
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for mock adapter."""
        return {
            "status": "healthy",
            "message": "Mock OpenTelemetry Health adapter is operational",
            "endpoint": self.endpoint
        }


# ============================================================================
# OPENTELEMETRY TELEMETRY MOCK ADAPTER
# ============================================================================

class MockTelemetryAdapter:
    """Mock Telemetry Adapter - mirrors production interface exactly."""
    
    def __init__(self, service_name: str, service_version: str = "1.0.0",
                 endpoint: str = None, **kwargs):
        """Initialize mock Telemetry adapter."""
        self.service_name = service_name
        self.service_version = service_version
        self.endpoint = endpoint
        self.logger = logging.getLogger("MockTelemetryAdapter")
        self._metrics = []
        self._traces = []
        self._spans = []
        self.logger.info(f"Initialized Mock Telemetry Adapter for {service_name}")
    
    async def record_metric(self, metric_name: str, value: float, metadata: Dict[str, Any] = None) -> bool:
        """Record metric in mock storage."""
        self._metrics.append({
            "name": metric_name,
            "value": value,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        })
        return True
    
    async def record_event(self, event_name: str, metadata: Dict[str, Any] = None) -> bool:
        """Record event in mock storage."""
        self._traces.append({
            "name": event_name,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        })
        return True
    
    def start_span(self, span_name: str, metadata: Dict[str, Any] = None):
        """Start a span in mock storage."""
        span = {
            "name": span_name,
            "metadata": metadata or {},
            "start_time": datetime.utcnow().isoformat(),
            "end_time": None
        }
        self._spans.append(span)
        return span
    
    def end_span(self, span: Dict[str, Any]):
        """End a span in mock storage."""
        span["end_time"] = datetime.utcnow().isoformat()
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for mock adapter."""
        return {
            "status": "healthy",
            "message": "Mock Telemetry adapter is operational",
            "metrics_count": len(self._metrics),
            "traces_count": len(self._traces),
            "spans_count": len(self._spans)
        }


# ============================================================================
# REDIS MOCK ADAPTER
# ============================================================================

class MockRedisAdapter:
    """Mock Redis Adapter - mirrors production interface exactly."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, password: str = None):
        """Initialize mock Redis adapter."""
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self._store = defaultdict(dict)  # In-memory storage: {db: {key: value}}
        self._connected = False
        self.logger = logging.getLogger("MockRedisAdapter")
        
        # Create a mock client object that other adapters can use
        # This mirrors the real RedisAdapter which has a .client attribute
        self.client = MagicMock()
        self.client.ping = AsyncMock(return_value=True)
        self.client.get = AsyncMock(side_effect=lambda key: self._store[self.db].get(key))
        self.client.set = AsyncMock(side_effect=lambda key, value, **kwargs: self._store[self.db].__setitem__(key, value))
        self.client.delete = AsyncMock(side_effect=lambda key: self._store[self.db].pop(key, None))
        self.client.exists = AsyncMock(side_effect=lambda key: key in self._store[self.db])
        self.client.publish = AsyncMock(return_value=True)
        self.client.subscribe = AsyncMock(return_value=MagicMock())
        
        self.logger.info(f"✅ Mock Redis adapter initialized: {host}:{port}/{db}")
    
    async def connect(self) -> bool:
        """Connect to mock Redis (always succeeds)."""
        self._connected = True
        self.logger.info("✅ Mock Redis adapter connected")
        return True
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from mock storage."""
        return self._store[self.db].get(key)
    
    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set value in mock storage."""
        self._store[self.db][key] = value
        if expire:
            # In real implementation, would schedule expiration
            pass
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete key from mock storage."""
        if key in self._store[self.db]:
            del self._store[self.db][key]
            return True
        return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in mock storage."""
        return key in self._store[self.db]
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for mock adapter."""
        return {
            "status": "healthy" if self._connected else "unhealthy",
            "message": "Mock Redis adapter is operational",
            "connected": self._connected,
            "keys_count": len(self._store[self.db])
        }


# ============================================================================
# ARANGODB MOCK ADAPTER
# ============================================================================

class MockArangoDBAdapter:
    """Mock ArangoDB Adapter - mirrors production interface exactly."""
    
    def __init__(self, hosts: str = None, database: str = None, username: str = None, password: str = None,
                 url: str = None, db_name: str = None):
        """
        Initialize mock ArangoDB adapter.
        
        Supports both constructor signatures:
        - ArangoDBAdapter(hosts, database, username, password)
        - ArangoDBAdapter(url=url, db_name=db_name, username=username, password=password)
        """
        # Handle both constructor signatures
        if hosts is not None:
            self.hosts = hosts
            self.database = database or "test_db"
            self.username = username or "root"
            self.password = password or ""
        else:
            self.hosts = url or "http://localhost:8529"
            self.database = db_name or "test_db"
            self.username = username or "root"
            self.password = password or ""
        
        self.url = self.hosts  # For compatibility
        self.db_name = self.database  # For compatibility
        
        self._collections = defaultdict(dict)  # In-memory storage: {collection: {id: doc}}
        self.db = MagicMock()  # Mock database object
        self._connected = False
        self.logger = logging.getLogger("MockArangoDBAdapter")
        self.logger.info(f"✅ Mock ArangoDB adapter initialized: {self.hosts}/{self.database}")
    
    async def connect(self) -> bool:
        """Connect to mock ArangoDB (always succeeds)."""
        self._connected = True
        self.logger.info("✅ Mock ArangoDB adapter connected")
        return True
    
    async def create_collection(self, collection_name: str) -> bool:
        """Create collection in mock storage."""
        if collection_name not in self._collections:
            self._collections[collection_name] = {}
        return True
    
    async def insert_document(self, collection_name: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """Insert document into mock storage."""
    
    async def create_document(self, collection: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """Create document in mock storage."""
        return await self.insert_document(collection, document)
    
    async def update_document(self, collection: str, key: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """Update document in mock storage."""
        if collection not in self._collections or key not in self._collections[collection]:
            raise ValueError(f"Document {key} not found in collection {collection}")
        self._collections[collection][key].update(document)
        return self._collections[collection][key]
    
    async def delete_document(self, collection: str, key: str) -> bool:
        """Delete document from mock storage."""
        if collection not in self._collections or key not in self._collections[collection]:
            return False
        del self._collections[collection][key]
        return True
    
        if collection_name not in self._collections:
            await self.create_collection(collection_name)
        doc_id = document.get("_key") or document.get("_id") or f"doc_{len(self._collections[collection_name]) + 1}"
        document["_key"] = doc_id
        document["_id"] = f"{collection_name}/{doc_id}"
        self._collections[collection_name][doc_id] = document
        return document
    
    async def get_document(self, collection_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document from mock storage."""
        return self._collections.get(collection_name, {}).get(doc_id)
    
    async def query(self, query: str, bind_vars: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute query on mock storage (simplified)."""
        # Simplified query support - in production, would use AQL parser
        results = []
        for collection_name, docs in self._collections.items():
            results.extend(list(docs.values()))
        return results
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for mock adapter."""
        total_docs = sum(len(docs) for docs in self._collections.values())
        return {
            "status": "healthy" if self._connected else "unhealthy",
            "message": "Mock ArangoDB adapter is operational",
            "connected": self._connected,
            "collections_count": len(self._collections),
            "documents_count": total_docs
        }


# ============================================================================
# MOCK ADAPTER FACTORY
# ============================================================================

class MockAdapterFactory:
    """Factory for creating mock adapters that mirror production interfaces."""
    
    @staticmethod
    def create_supabase_file_management_adapter(url: str, service_key: str):
        """Create mock Supabase File Management adapter."""
        return MockSupabaseFileManagementAdapter(url, service_key)
    
    @staticmethod
    def create_opentelemetry_health_adapter(service_name: str = "opentelemetry_health_adapter",
                                            endpoint: str = "http://localhost:4317",
                                            timeout: int = 30):
        """Create mock OpenTelemetry Health adapter."""
        return MockOpenTelemetryHealthAdapter(service_name, endpoint, timeout)
    
    @staticmethod
    def create_telemetry_adapter(service_name: str, service_version: str = "1.0.0",
                                 endpoint: str = None, **kwargs):
        """Create mock Telemetry adapter."""
        return MockTelemetryAdapter(service_name, service_version, endpoint, **kwargs)
    
    @staticmethod
    def create_redis_adapter(host: str = "localhost", port: int = 6379, db: int = 0, password: str = None):
        """Create mock Redis adapter."""
        return MockRedisAdapter(host, port, db, password)
    
    @staticmethod
    def create_arangodb_adapter(url: str = "http://localhost:8529", db_name: str = "test_db",
                                username: str = "root", password: str = ""):
        """Create mock ArangoDB adapter."""
        return MockArangoDBAdapter(url, db_name, username, password)

