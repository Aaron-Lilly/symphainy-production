#!/usr/bin/env python3
"""
FastAPI Infrastructure Foundation Service - Infrastructure Abstraction Producer with FastAPI DI

Produces infrastructure abstractions using FastAPI DI-injected configuration from
FastAPI Configuration Foundation Service.

WHAT (Infrastructure Role): I need to create infrastructure abstractions from FastAPI DI-injected configuration
HOW (Infrastructure Service): I use FastAPI DI to get validated config and create real, usable infrastructure abstractions
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from fastapi import Depends
from bases.foundation_service_base import FoundationServiceBase
from common.utilities import UserContext
from foundations.configuration_foundation.fastapi_configuration_service import (
    FastAPIConfigurationService,
    get_redis_config,
    get_celery_config,
    get_database_config,
    get_storage_config,
    get_telemetry_config,
    get_search_config,
    get_event_bus_config,
    get_authentication_config
)
# Import directly from micro-modules for clean architecture
from .abstractions import (
    PostgreSQLAbstraction, SQLiteAbstraction, RedisAbstraction,
    ElasticsearchAbstraction, MeilisearchAbstraction,
    LocalStorageAbstraction, S3Abstraction, TelemetryAbstraction, CeleryAbstraction, RedisGraphAbstraction, WebSocketAbstraction,
    # Core 4 Raw Infrastructure Abstractions
    GCSStorageAbstraction, S3StorageAbstraction, ArangoDBAbstraction,
    # Advanced Authentication Infrastructure Abstractions
    SupabaseAuthAbstraction,
    # Advanced Event Bus Infrastructure Abstractions
    RedisStreamsAbstraction, EventRoutingAbstraction
)


class FastAPIInfrastructureFoundationService(FoundationServiceBase):
    """
    FastAPI Infrastructure Foundation Service - Infrastructure Abstraction Producer with FastAPI DI
    
    WHAT (Infrastructure Role): I need to create infrastructure abstractions from FastAPI DI-injected configuration
    HOW (Infrastructure Service): I use FastAPI DI to get validated config and create real, usable infrastructure abstractions
    
    Responsibilities:
    - Receive configuration via FastAPI DI from FastAPI Configuration Foundation
    - Create infrastructure abstractions using real configuration
    - Provide infrastructure abstractions to other foundation services
    - Manage infrastructure connection pools and resources
    """
    
    def __init__(self, utility_foundation, curator_foundation, fastapi_config_service: FastAPIConfigurationService):
        """Initialize FastAPI Infrastructure Foundation Service."""
        super().__init__("fastapi_infrastructure_foundation", utility_foundation)
        
        self.utility_foundation = utility_foundation
        self.curator_foundation = curator_foundation
        self.fastapi_config_service = fastapi_config_service
        
        # Infrastructure abstractions (will be created from injected config)
        self.infrastructure_abstractions = {}
        
        # Configuration (injected via FastAPI DI)
        self.db_config = None
        self.redis_config = None
        self.telemetry_config = None
        self.search_config = None
        self.file_storage_config = None
        self.workflow_config = None
        
        # Core 4 Configuration
        self.core4_config = None
        
        # Authentication configuration
        self.authentication_config = None
        
        # Event bus configuration
        self.event_bus_config = None
        
        self.logger.info("🏗️ FastAPI Infrastructure Foundation Service initialized as Abstraction Producer")
    
    async def initialize_infrastructure_abstractions(self):
        """Initialize all infrastructure abstractions using FastAPI DI configuration."""
        try:
            self.logger.info("🔄 Initializing infrastructure abstractions with FastAPI DI configuration...")
            
            # Load configuration via FastAPI DI
            await self._load_configuration_via_fastapi_di()
            
            # Create infrastructure abstractions
            await self._create_database_abstractions()
            await self._create_redis_abstractions()
            await self._create_telemetry_abstractions()
            await self._create_search_abstractions()
            await self._create_storage_abstractions()
            await self._create_workflow_abstractions()
            await self._create_core4_abstractions()
            await self._create_authentication_abstractions()
            await self._create_event_bus_abstractions()
            
            self.logger.info("✅ All infrastructure abstractions initialized with FastAPI DI configuration")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize infrastructure abstractions: {e}")
            raise
    
    async def _load_configuration_via_fastapi_di(self):
        """Load configuration using FastAPI DI."""
        try:
            # Get configurations via FastAPI DI
            self.redis_config = self.fastapi_config_service.get_redis_config()
            self.db_config = self.fastapi_config_service.get_database_config()
            self.telemetry_config = self.fastapi_config_service.get_telemetry_config()
            self.search_config = self.fastapi_config_service.get_search_config()
            self.file_storage_config = self.fastapi_config_service.get_storage_config()
            self.workflow_config = self.fastapi_config_service.get_celery_config()
            self.authentication_config = self.fastapi_config_service.get_authentication_config()
            self.event_bus_config = self.fastapi_config_service.get_event_bus_config()
            self.agui_config = self.fastapi_config_service.get_agui_config()
            
            self.logger.info("✅ Configuration loaded via FastAPI DI")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load configuration via FastAPI DI: {e}")
            raise
    
    async def _create_database_abstractions(self):
        """Create database infrastructure abstractions."""
        try:
            # PostgreSQL
            if self.db_config.type.value == "postgresql":
                postgresql_abstraction = PostgreSQLAbstraction(
                    host=self.db_config.host,
                    port=self.db_config.port,
                    database=self.db_config.name,
                    user=self.db_config.username,
                    password=self.db_config.password,
                    pool_size=self.db_config.max_connections,
                    max_overflow=self.db_config.max_connections
                )
                await postgresql_abstraction.connect()
                self.infrastructure_abstractions["postgresql"] = postgresql_abstraction
                self.logger.info("✅ PostgreSQL abstraction created")
            
            # SQLite
            elif self.db_config.type.value == "sqlite":
                sqlite_abstraction = SQLiteAbstraction(
                    database_path=self.db_config.name,
                    timeout=self.db_config.connection_timeout
                )
                await sqlite_abstraction.connect()
                self.infrastructure_abstractions["sqlite"] = sqlite_abstraction
                self.logger.info("✅ SQLite abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create database abstractions: {e}")
            raise
    
    async def _create_redis_abstractions(self):
        """Create Redis infrastructure abstractions."""
        try:
            redis_abstraction = RedisAbstraction(
                host=self.redis_config.host,
                port=self.redis_config.port,
                database=self.redis_config.db,
                password=self.redis_config.password,
                max_connections=self.redis_config.max_connections
            )
            await redis_abstraction.connect()
            self.infrastructure_abstractions["redis"] = redis_abstraction
            self.logger.info("✅ Redis abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create Redis abstractions: {e}")
            raise
    
    async def _create_telemetry_abstractions(self):
        """Create telemetry infrastructure abstractions."""
        try:
            telemetry_abstraction = TelemetryAbstraction(
                provider=self.telemetry_config.provider,
                endpoint=self.telemetry_config.endpoint,
                service_name="symphainy_platform",
                environment="development"
            )
            await telemetry_abstraction.connect()
            self.infrastructure_abstractions["telemetry"] = telemetry_abstraction
            self.logger.info("✅ Telemetry abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create telemetry abstractions: {e}")
            raise
    
    async def _create_search_abstractions(self):
        """Create search infrastructure abstractions."""
        try:
            # Meilisearch
            if self.search_config.meilisearch_enabled:
                # Parse host and port from meilisearch_host (format: http://host:port)
                meilisearch_url = self.search_config.meilisearch_host
                if meilisearch_url.startswith("http://"):
                    host_port = meilisearch_url[7:]  # Remove http://
                    if ":" in host_port:
                        host, port = host_port.split(":")
                        port = int(port)
                    else:
                        host = host_port
                        port = 7700  # Default Meilisearch port
                else:
                    host = "localhost"
                    port = 7700
                
                meilisearch_abstraction = MeilisearchAbstraction(
                    host=host,
                    port=port,
                    master_key=self.search_config.meilisearch_master_key or ""
                )
                await meilisearch_abstraction.connect()
                self.infrastructure_abstractions["meilisearch"] = meilisearch_abstraction
                self.logger.info("✅ Meilisearch abstraction created")
            
            # Elasticsearch (Future Phase - Not Available Yet)
            if self.search_config.elasticsearch_enabled:
                self.logger.warning("⚠️  Elasticsearch is not available yet (future phase) - skipping Elasticsearch abstraction creation")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create search abstractions: {e}")
            raise
    
    async def _create_storage_abstractions(self):
        """Create storage infrastructure abstractions."""
        try:
            # Local Storage (always enabled as fallback)
            local_storage_abstraction = LocalStorageAbstraction(
                base_path=self.file_storage_config.local_storage_path,
                max_size_gb=self.file_storage_config.local_storage_max_size_gb,
                enable_compression=self.file_storage_config.enable_local_compression
            )
            await local_storage_abstraction.connect()
            self.infrastructure_abstractions["local_storage"] = local_storage_abstraction
            self.logger.info("✅ Local storage abstraction created")
            
            # S3 Storage
            if self.file_storage_config.enable_s3:
                s3_abstraction = S3Abstraction(
                    bucket_name=self.file_storage_config.s3_bucket_name,
                    region=self.file_storage_config.s3_region,
                    access_key=self.file_storage_config.s3_access_key_id,
                    secret_key=self.file_storage_config.s3_secret_access_key
                )
                await s3_abstraction.connect()
                self.infrastructure_abstractions["s3"] = s3_abstraction
                self.logger.info("✅ S3 storage abstraction created")
            
            # GCS Storage
            if self.file_storage_config.enable_gcs:
                gcs_abstraction = GCSStorageAbstraction(
                    bucket_name=self.file_storage_config.gcs_bucket_name,
                    project_id=self.file_storage_config.gcs_project_id,
                    credentials_path=self.file_storage_config.gcs_credentials_path
                )
                await gcs_abstraction.connect()
                self.infrastructure_abstractions["gcs"] = gcs_abstraction
                self.logger.info("✅ GCS storage abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create storage abstractions: {e}")
            raise
    
    async def _create_workflow_abstractions(self):
        """Create workflow infrastructure abstractions."""
        try:
            celery_abstraction = CeleryAbstraction(
                broker_url=self.workflow_config.broker_url or "redis://localhost:6379/0",
                result_backend=self.workflow_config.result_backend or "redis://localhost:6379/0",
                broker_transport=self.workflow_config.broker_transport,
                worker_concurrency=self.workflow_config.worker_concurrency,
                task_serializer=self.workflow_config.task_serializer,
                result_serializer=self.workflow_config.task_serializer,  # Use same as task serializer
                accept_content=[self.workflow_config.task_serializer],
                timezone="UTC",
                enable_utc=True
            )
            await celery_abstraction.connect()
            self.infrastructure_abstractions["celery"] = celery_abstraction
            self.logger.info("✅ Celery abstraction created")
            
            # Redis Graph
            redis_graph_abstraction = RedisGraphAbstraction(
                host=self.redis_config.host,
                port=self.redis_config.port,
                password=self.redis_config.password,
                graph_name="workflows"
            )
            await redis_graph_abstraction.connect()
            self.infrastructure_abstractions["redisgraph"] = redis_graph_abstraction
            self.logger.info("✅ Redis Graph abstraction created")
            
            # WebSocket for AGUI
            websocket_abstraction = WebSocketAbstraction(
                host=self.agui_config.websocket_host,
                port=self.agui_config.websocket_port,
                path=self.agui_config.websocket_path,
                enable_ssl=self.agui_config.enable_ssl,
                max_connections=self.agui_config.max_connections
            )
            await websocket_abstraction.connect()
            self.infrastructure_abstractions["websocket"] = websocket_abstraction
            self.logger.info("✅ WebSocket abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create workflow abstractions: {e}")
            raise
    
    async def _create_core4_abstractions(self):
        """Create Core 4 infrastructure abstractions."""
        try:
            # ArangoDB
            if hasattr(self, 'arango_config') and self.arango_config:
                arango_abstraction = ArangoDBAbstraction(
                    url=self.arango_config.get("url", "http://localhost:8529"),
                    database=self.arango_config.get("database", "symphainy_metadata"),
                    username=self.arango_config.get("username", "root"),
                    password=self.arango_config.get("password", "")
                )
                await arango_abstraction.connect()
                self.infrastructure_abstractions["arangodb"] = arango_abstraction
                self.logger.info("✅ ArangoDB abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create Core 4 abstractions: {e}")
            raise
    
    async def _create_authentication_abstractions(self):
        """Create authentication infrastructure abstractions."""
        try:
            # Supabase Authentication
            if self.authentication_config.supabase_enabled:
                supabase_auth_abstraction = SupabaseAuthAbstraction(
                    supabase_url=self.authentication_config.supabase_url,
                    supabase_anon_key=self.authentication_config.supabase_anon_key,
                    supabase_service_key=self.authentication_config.supabase_service_key
                )
                await supabase_auth_abstraction.connect()
                self.infrastructure_abstractions["supabase_auth"] = supabase_auth_abstraction
                self.logger.info("✅ Supabase authentication abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create authentication abstractions: {e}")
            raise
    
    async def _create_event_bus_abstractions(self):
        """Create event bus infrastructure abstractions."""
        try:
            # Redis Streams
            if self.event_bus_config.redis_streams_enabled:
                redis_streams_abstraction = RedisStreamsAbstraction(
                    host=self.event_bus_config.redis_streams_host,
                    port=self.event_bus_config.redis_streams_port,
                    password=self.event_bus_config.redis_streams_password
                )
                await redis_streams_abstraction.connect()
                self.infrastructure_abstractions["redis_streams"] = redis_streams_abstraction
                self.logger.info("✅ Redis Streams abstraction created")
            
            # Event Routing
            if self.event_bus_config.event_routing_enabled:
                # Get the Redis Streams abstraction that was created earlier
                redis_streams_abstraction = self.infrastructure_abstractions.get("redis_streams")
                if redis_streams_abstraction:
                    event_routing_abstraction = EventRoutingAbstraction(
                        redis_streams_abstraction=redis_streams_abstraction
                    )
                    await event_routing_abstraction.connect()
                    self.infrastructure_abstractions["event_routing"] = event_routing_abstraction
                    self.logger.info("✅ Event routing abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create event bus abstractions: {e}")
            raise
    
    def get_infrastructure_abstraction(self, abstraction_name: str) -> Optional[Any]:
        """Get a specific infrastructure abstraction."""
        return self.infrastructure_abstractions.get(abstraction_name)
    
    def get_all_infrastructure_abstractions(self) -> Dict[str, Any]:
        """Get all infrastructure abstractions."""
        return self.infrastructure_abstractions.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        """Infrastructure foundation health check."""
        try:
            base_health = {
                "service": "fastapi_infrastructure_foundation",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "abstractions": {}
            }
            
            # Check each abstraction
            for name, abstraction in self.infrastructure_abstractions.items():
                try:
                    if hasattr(abstraction, 'health_check'):
                        health = await abstraction.health_check()
                        base_health["abstractions"][name] = health
                    else:
                        base_health["abstractions"][name] = {
                            "status": "unknown",
                            "message": "No health check method"
                        }
                except Exception as e:
                    base_health["abstractions"][name] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
            
            return base_health
            
        except Exception as e:
            return {
                "service": "fastapi_infrastructure_foundation",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# FastAPI Dependency Functions for Infrastructure Abstractions

def get_redis_abstraction(
    infrastructure_service: FastAPIInfrastructureFoundationService = Depends()
) -> RedisAbstraction:
    """FastAPI dependency for Redis abstraction."""
    return infrastructure_service.get_infrastructure_abstraction("redis")


def get_postgresql_abstraction(
    infrastructure_service: FastAPIInfrastructureFoundationService = Depends()
) -> PostgreSQLAbstraction:
    """FastAPI dependency for PostgreSQL abstraction."""
    return infrastructure_service.get_infrastructure_abstraction("postgresql")


def get_telemetry_abstraction(
    infrastructure_service: FastAPIInfrastructureFoundationService = Depends()
) -> TelemetryAbstraction:
    """FastAPI dependency for Telemetry abstraction."""
    return infrastructure_service.get_infrastructure_abstraction("telemetry")


def get_meilisearch_abstraction(
    infrastructure_service: FastAPIInfrastructureFoundationService = Depends()
) -> MeilisearchAbstraction:
    """FastAPI dependency for Meilisearch abstraction."""
    return infrastructure_service.get_infrastructure_abstraction("meilisearch")


def get_supabase_auth_abstraction(
    infrastructure_service: FastAPIInfrastructureFoundationService = Depends()
) -> SupabaseAuthAbstraction:
    """FastAPI dependency for Supabase Auth abstraction."""
    return infrastructure_service.get_infrastructure_abstraction("supabase_auth")


def get_redis_streams_abstraction(
    infrastructure_service: FastAPIInfrastructureFoundationService = Depends()
) -> RedisStreamsAbstraction:
    """FastAPI dependency for Redis Streams abstraction."""
    return infrastructure_service.get_infrastructure_abstraction("redis_streams")
