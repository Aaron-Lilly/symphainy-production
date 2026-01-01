#!/usr/bin/env python3
"""
Infrastructure Foundation Service - Infrastructure Abstraction Producer

Produces infrastructure abstractions using injected configuration from
Configuration Foundation Service.

WHAT (Infrastructure Role): I need to create infrastructure abstractions from validated configuration
HOW (Infrastructure Service): I use injected config to create real, usable infrastructure abstractions
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from bases.foundation_service_base import FoundationServiceBase
from common.utilities import UserContext
# Import directly from micro-modules for clean architecture
from .abstractions import (
    PostgreSQLAbstraction, SQLiteAbstraction, RedisAbstraction,
    ElasticsearchAbstraction, MeilisearchAbstraction,
    LocalStorageAbstraction, S3Abstraction, TelemetryAbstraction, CeleryAbstraction,
    # Core 4 Raw Infrastructure Abstractions
    GCSStorageAbstraction, S3StorageAbstraction, ArangoDBAbstraction,
    # Advanced Authentication Infrastructure Abstractions
    SupabaseAuthAbstraction,
    # Advanced Event Bus Infrastructure Abstractions
    RedisStreamsAbstraction, EventRoutingAbstraction
)


class InfrastructureFoundationService(FoundationServiceBase):
    """
    Infrastructure Foundation Service - Infrastructure Abstraction Producer
    
    WHAT (Infrastructure Role): I need to create infrastructure abstractions from validated configuration
    HOW (Infrastructure Service): I use injected config to create real, usable infrastructure abstractions
    
    Responsibilities:
    - Receive validated configuration from Configuration Foundation
    - Create infrastructure abstractions using real configuration
    - Provide infrastructure abstractions to other foundation services
    - Manage infrastructure connection pools and resources
    """
    
    def __init__(self, utility_foundation, curator_foundation, configuration_foundation):
        """Initialize Infrastructure Foundation Service."""
        super().__init__("infrastructure_foundation", utility_foundation)
        
        self.utility_foundation = utility_foundation
        self.curator_foundation = curator_foundation
        self.configuration_foundation = configuration_foundation
        
        # Infrastructure abstractions (will be created from injected config)
        self.infrastructure_abstractions = {}
        
        # Configuration (injected from Configuration Foundation)
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
        
        self.logger.info("🏗️ Infrastructure Foundation Service initialized as Abstraction Producer")
    
    async def initialize(self):
        """Initialize infrastructure abstractions using injected configuration."""
        try:
            # Call parent initialize
            await super().initialize()
            
            self.logger.info("🚀 Initializing Infrastructure Foundation Service...")
            
            # Get configuration from Configuration Foundation
            await self.configuration_foundation.inject_infrastructure_config(self)
            
            # Create infrastructure abstractions using injected configuration
            await self._create_infrastructure_abstractions()
            
            self.logger.info("✅ Infrastructure Foundation Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Infrastructure Foundation Service: {e}")
            await self.handle_error_with_audit(e, "infrastructure_initialization")
            raise
    
    # ============================================================================
    # CONFIGURATION INJECTION METHODS (Called by Configuration Foundation)
    
    async def configure_database(self, db_config: Dict[str, Any]):
        """Configure database using injected configuration."""
        try:
            self.db_config = db_config
            self.logger.info("✅ Database configuration injected")
        except Exception as e:
            self.logger.error(f"❌ Failed to configure database: {e}")
            raise
    
    async def configure_redis(self, redis_config: Dict[str, Any]):
        """Configure Redis using injected configuration."""
        try:
            self.redis_config = redis_config
            self.logger.info("✅ Redis configuration injected")
        except Exception as e:
            self.logger.error(f"❌ Failed to configure Redis: {e}")
            raise
    
    async def configure_telemetry(self, telemetry_config: Dict[str, Any]):
        """Configure telemetry using injected configuration."""
        try:
            self.telemetry_config = telemetry_config
            self.logger.info("✅ Telemetry configuration injected")
        except Exception as e:
            self.logger.error(f"❌ Failed to configure telemetry: {e}")
            raise
    
    async def configure_search(self, search_config: Dict[str, Any]):
        """Configure search using injected configuration."""
        try:
            self.search_config = search_config
            self.logger.info("✅ Search configuration injected")
        except Exception as e:
            self.logger.error(f"❌ Failed to configure search: {e}")
            raise
    
    async def configure_file_storage(self, file_storage_config: Dict[str, Any]):
        """Configure file storage using injected configuration."""
        try:
            self.file_storage_config = file_storage_config
            self.logger.info("✅ File storage configuration injected")
        except Exception as e:
            self.logger.error(f"❌ Failed to configure file storage: {e}")
            raise
    
    async def configure_workflow(self, workflow_config: Dict[str, Any]):
        """Configure workflow using injected configuration."""
        try:
            self.workflow_config = workflow_config
            self.logger.info("✅ Workflow configuration injected")
        except Exception as e:
            self.logger.error(f"❌ Failed to configure workflow: {e}")
            raise
    
    async def configure_core4(self, core4_config: Dict[str, Any]):
        """Configure Core 4 using injected configuration."""
        try:
            self.core4_config = core4_config
            self.logger.info("✅ Core 4 configuration injected")
        except Exception as e:
            self.logger.error(f"❌ Failed to configure Core 4: {e}")
            raise
    
    async def configure_authentication(self, authentication_config: Dict[str, Any]):
        """Configure authentication infrastructure using injected configuration."""
        try:
            self.authentication_config = authentication_config
            self.logger.info("✅ Authentication configuration injected")
        except Exception as e:
            self.logger.error(f"❌ Failed to configure authentication: {e}")
            raise
    
    async def configure_event_bus(self, event_bus_config: Dict[str, Any]):
        """Configure event bus infrastructure using injected configuration."""
        try:
            self.event_bus_config = event_bus_config
            self.logger.info("✅ Event bus configuration injected")
        except Exception as e:
            self.logger.error(f"❌ Failed to configure event bus: {e}")
            raise
    
    # ============================================================================
    # INFRASTRUCTURE ABSTRACTION CREATION METHODS
    
    async def _create_infrastructure_abstractions(self):
        """Create infrastructure abstractions using injected configuration."""
        try:
            await self.log_operation_with_telemetry("create_infrastructure_abstractions", success=True)
            self.logger.info("🏗️ Creating infrastructure abstractions...")
            
            # Create database abstractions
            await self._create_database_abstractions()
            
            # Create cache abstractions
            await self._create_cache_abstractions()
            
            # Create search abstractions
            await self._create_search_abstractions()
            
            # Create file storage abstractions
            await self._create_file_storage_abstractions()
            
            # Create telemetry abstractions
            await self._create_telemetry_abstractions()
            
            # Create workflow abstractions
            await self._create_workflow_abstractions()
            
            # Create Core 4 abstractions
            await self._create_core4_abstractions()
            
            # Create authentication abstractions
            await self._create_authentication_abstractions()
            
            # Create event bus abstractions
            await self._create_event_bus_abstractions()
            
            # Track utility usage
            self.track_utility_usage("abstraction_creation")
            await self.record_health_metric("abstractions_created", len(self.infrastructure_abstractions))
            
            self.logger.info("✅ Infrastructure abstractions created successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create infrastructure abstractions: {e}")
            await self.handle_error_with_audit(e, "create_infrastructure_abstractions")
            raise
    
    async def _create_database_abstractions(self):
        """Create database abstractions using injected configuration."""
        try:
            if not self.db_config:
                self.logger.warning("No database configuration available")
                return
            
            self.infrastructure_abstractions["database"] = {}
            
            # Create PostgreSQL abstraction
            if self.db_config.get("postgresql", {}).get("enabled", False):
                postgresql_config = self.db_config["postgresql"]
                self.infrastructure_abstractions["database"]["postgresql"] = PostgreSQLAbstraction(
                    host=postgresql_config["host"],
                    port=postgresql_config["port"],
                    database=postgresql_config["database"],
                    user=postgresql_config["user"],
                    password=postgresql_config["password"],
                    pool_size=postgresql_config.get("pool_size", 10),
                    max_overflow=postgresql_config.get("max_overflow", 20)
                )
                self.logger.info("✅ PostgreSQL abstraction created")
            
            # Create SQLite abstraction
            if self.db_config.get("sqlite", {}).get("enabled", False):
                sqlite_config = self.db_config["sqlite"]
                self.infrastructure_abstractions["database"]["sqlite"] = SQLiteAbstraction(
                    database_path=sqlite_config["database_path"],
                    timeout=sqlite_config.get("timeout", 30)
                )
                self.logger.info("✅ SQLite abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create database abstractions: {e}")
            raise
    
    async def _create_cache_abstractions(self):
        """Create cache abstractions using injected configuration."""
        try:
            if not self.redis_config or not self.redis_config.get("enabled", False):
                self.logger.warning("Redis not enabled or no configuration available")
                return
            
            self.infrastructure_abstractions["cache"] = {}
            
            # Create Redis abstraction
            redis_config = self.redis_config
            self.infrastructure_abstractions["cache"]["redis"] = RedisAbstraction(
                host=redis_config["host"],
                port=redis_config["port"],
                password=redis_config.get("password", ""),
                database=redis_config.get("database", 0),
                pool_size=redis_config.get("pool_size", 10),
                max_connections=redis_config.get("max_connections", 50),
                socket_timeout=redis_config.get("socket_timeout", 5),
                socket_connect_timeout=redis_config.get("socket_connect_timeout", 5)
            )
            self.logger.info("✅ Redis abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create cache abstractions: {e}")
            raise
    
    async def _create_search_abstractions(self):
        """Create search abstractions using injected configuration."""
        try:
            if not self.search_config:
                self.logger.warning("No search configuration available")
                return
            
            self.infrastructure_abstractions["search"] = {}
            
            # Create Meilisearch abstraction (current implementation)
            if self.search_config.get("meilisearch", {}).get("enabled", False):
                meilisearch_config = self.search_config["meilisearch"]
                self.infrastructure_abstractions["search"]["meilisearch"] = MeilisearchAbstraction(
                    host=meilisearch_config["host"],
                    port=meilisearch_config["port"],
                    master_key=meilisearch_config["master_key"]
                )
                self.logger.info("✅ Meilisearch abstraction created")
            
            # Create Elasticsearch abstraction (future roadmap)
            if self.search_config.get("elasticsearch", {}).get("enabled", False):
                elasticsearch_config = self.search_config["elasticsearch"]
                self.infrastructure_abstractions["search"]["elasticsearch"] = ElasticsearchAbstraction(
                    host=elasticsearch_config["host"],
                    port=elasticsearch_config["port"],
                    username=elasticsearch_config.get("username", ""),
                    password=elasticsearch_config.get("password", ""),
                    use_ssl=elasticsearch_config.get("use_ssl", False),
                    verify_certs=elasticsearch_config.get("verify_certs", False)
                )
                self.logger.info("✅ Elasticsearch abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create search abstractions: {e}")
            raise
    
    async def _create_file_storage_abstractions(self):
        """Create file storage abstractions using injected configuration."""
        try:
            if not self.file_storage_config:
                self.logger.warning("No file storage configuration available")
                return
            
            self.infrastructure_abstractions["file_storage"] = {}
            
            # Create local storage abstraction
            if self.file_storage_config.get("local", {}).get("enabled", False):
                local_config = self.file_storage_config["local"]
                self.infrastructure_abstractions["file_storage"]["local"] = LocalStorageAbstraction(
                    base_path=local_config["base_path"],
                    max_file_size=local_config.get("max_file_size", 10485760),
                    allowed_extensions=local_config.get("allowed_extensions", ["txt", "json", "csv", "pdf"])
                )
                self.logger.info("✅ Local storage abstraction created")
            
            # Create S3 abstraction
            if self.file_storage_config.get("s3", {}).get("enabled", False):
                s3_config = self.file_storage_config["s3"]
                self.infrastructure_abstractions["file_storage"]["s3"] = S3Abstraction(
                    bucket_name=s3_config["bucket_name"],
                    region=s3_config["region"],
                    access_key_id=s3_config["access_key_id"],
                    secret_access_key=s3_config["secret_access_key"]
                )
                self.logger.info("✅ S3 abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create file storage abstractions: {e}")
            raise
    
    async def _create_telemetry_abstractions(self):
        """Create telemetry abstractions using injected configuration."""
        try:
            if not self.telemetry_config or not self.telemetry_config.get("enabled", False):
                self.logger.warning("Telemetry not enabled or no configuration available")
                return
            
            self.infrastructure_abstractions["telemetry"] = {}
            
            # Create telemetry abstraction
            telemetry_config = self.telemetry_config
            self.infrastructure_abstractions["telemetry"]["opentelemetry"] = TelemetryAbstraction(
                provider=telemetry_config["provider"],
                endpoint=telemetry_config["endpoint"],
                metrics_port=telemetry_config.get("metrics_port", 8000),
                trace_endpoint=telemetry_config.get("trace_endpoint", ""),
                log_level=telemetry_config.get("log_level", "INFO"),
                sample_rate=telemetry_config.get("sample_rate", 1.0)
            )
            self.logger.info("✅ OpenTelemetry abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create telemetry abstractions: {e}")
            raise
    
    async def _create_workflow_abstractions(self):
        """Create workflow abstractions using injected configuration."""
        try:
            if not self.workflow_config:
                self.logger.warning("No workflow configuration available")
                return
            
            self.infrastructure_abstractions["workflow"] = {}
            
            # Create Celery abstraction
            if self.workflow_config.get("celery", {}).get("enabled", False):
                celery_config = self.workflow_config["celery"]
                self.infrastructure_abstractions["workflow"]["celery"] = CeleryAbstraction(
                    broker_url=celery_config["broker_url"],
                    result_backend=celery_config["result_backend"],
                    task_serializer=celery_config.get("task_serializer", "json"),
                    result_serializer=celery_config.get("result_serializer", "json"),
                    accept_content=celery_config.get("accept_content", ["json"]),
                    timezone=celery_config.get("timezone", "UTC")
                )
                self.logger.info("✅ Celery abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create workflow abstractions: {e}")
            raise
    
    async def _create_core4_abstractions(self):
        """Create Core 4 raw infrastructure abstractions using injected configuration."""
        try:
            if not self.core4_config:
                self.logger.warning("No Core 4 configuration available")
                return
            
            self.infrastructure_abstractions["core4"] = {}
            
            # Create GCS Storage abstraction
            if self.core4_config.get("gcs", {}).get("enabled", False):
                gcs_config = self.core4_config["gcs"]
                self.infrastructure_abstractions["core4"]["gcs"] = GCSStorageAbstraction(
                    project_id=gcs_config["project_id"],
                    credentials_path=gcs_config.get("credentials_path")
                )
                self.logger.info("✅ Core 4 GCS Storage abstraction created")
            
            # Create S3 Storage abstraction
            if self.core4_config.get("s3", {}).get("enabled", False):
                s3_config = self.core4_config["s3"]
                self.infrastructure_abstractions["core4"]["s3"] = S3StorageAbstraction(
                    region=s3_config["region"],
                    access_key_id=s3_config["access_key_id"],
                    secret_access_key=s3_config["secret_access_key"]
                )
                self.logger.info("✅ Core 4 S3 Storage abstraction created")
            
            # Create ArangoDB abstraction
            if self.core4_config.get("arangodb", {}).get("enabled", False):
                arango_config = self.core4_config["arangodb"]
                self.infrastructure_abstractions["core4"]["arangodb"] = ArangoDBAbstraction(
                    host=arango_config["host"],
                    port=arango_config["port"],
                    username=arango_config["username"],
                    password=arango_config["password"],
                    database=arango_config["database"]
                )
                self.logger.info("✅ Core 4 ArangoDB abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create Core 4 raw infrastructure abstractions: {e}")
            raise
    
    async def _create_authentication_abstractions(self):
        """Create authentication infrastructure abstractions using injected configuration."""
        try:
            if not self.authentication_config:
                self.logger.warning("No authentication configuration available")
                return
            
            self.infrastructure_abstractions["authentication"] = {}
            
            # Create Supabase authentication abstraction
            if self.authentication_config.get("supabase", {}).get("enabled", False):
                supabase_config = self.authentication_config["supabase"]
                self.infrastructure_abstractions["authentication"]["supabase"] = SupabaseAuthAbstraction(
                    supabase_url=supabase_config["supabase_url"],
                    supabase_anon_key=supabase_config["supabase_anon_key"],
                    supabase_service_key=supabase_config["supabase_service_key"]
                )
                self.logger.info("✅ Supabase authentication abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create authentication infrastructure abstractions: {e}")
            raise
    
    async def _create_event_bus_abstractions(self):
        """Create event bus infrastructure abstractions using injected configuration."""
        try:
            if not self.event_bus_config:
                self.logger.warning("No event bus configuration available")
                return
            
            self.infrastructure_abstractions["event_bus"] = {}
            
            # Create Redis Streams abstraction
            if self.event_bus_config.get("redis_streams", {}).get("enabled", False):
                redis_streams_config = self.event_bus_config["redis_streams"]
                redis_streams_abstraction = RedisStreamsAbstraction(
                    host=redis_streams_config["host"],
                    port=redis_streams_config["port"],
                    password=redis_streams_config.get("password")
                )
                self.infrastructure_abstractions["event_bus"]["redis_streams"] = redis_streams_abstraction
                self.logger.info("✅ Redis Streams abstraction created")
                
                # Create Event Routing abstraction (depends on Redis Streams)
                if self.event_bus_config.get("event_routing", {}).get("enabled", False):
                    self.infrastructure_abstractions["event_bus"]["event_routing"] = EventRoutingAbstraction(
                        redis_streams_abstraction=redis_streams_abstraction
                    )
                    self.logger.info("✅ Event Routing abstraction created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create event bus infrastructure abstractions: {e}")
            raise
    
    # ============================================================================
    # INFRASTRUCTURE ABSTRACTION ACCESS METHODS
    
    def get_infrastructure_abstraction(self, category: str, type: str):
        """Get infrastructure abstraction by category and type."""
        try:
            if category not in self.infrastructure_abstractions:
                self.logger.warning(f"No infrastructure abstractions found for category: {category}")
                return None
            
            if type not in self.infrastructure_abstractions[category]:
                self.logger.warning(f"No infrastructure abstraction found for {category}/{type}")
                return None
            
            return self.infrastructure_abstractions[category][type]
            
        except Exception as e:
            self.logger.error(f"Failed to get infrastructure abstraction {category}/{type}: {e}")
            return None
    
    def get_database_abstraction(self, db_type: str = "postgresql"):
        """Get database abstraction."""
        return self.get_infrastructure_abstraction("database", db_type)
    
    def get_cache_abstraction(self, cache_type: str = "redis"):
        """Get cache abstraction."""
        return self.get_infrastructure_abstraction("cache", cache_type)
    
    def get_search_abstraction(self, search_type: str = "meilisearch"):
        """Get search abstraction."""
        return self.get_infrastructure_abstraction("search", search_type)
    
    def get_file_storage_abstraction(self, storage_type: str = "local"):
        """Get file storage abstraction."""
        return self.get_infrastructure_abstraction("file_storage", storage_type)
    
    def get_telemetry_abstraction(self, telemetry_type: str = "opentelemetry"):
        """Get telemetry abstraction."""
        return self.get_infrastructure_abstraction("telemetry", telemetry_type)
    
    def get_workflow_abstraction(self, workflow_type: str = "celery"):
        """Get workflow abstraction."""
        return self.get_infrastructure_abstraction("workflow", workflow_type)
    
    # Core 4 Raw Infrastructure Access Methods
    def get_gcs_abstraction(self):
        """Get Core 4 GCS Storage abstraction."""
        return self.get_infrastructure_abstraction("core4", "gcs")
    
    def get_s3_abstraction(self):
        """Get Core 4 S3 Storage abstraction."""
        return self.get_infrastructure_abstraction("core4", "s3")
    
    def get_arangodb_abstraction(self):
        """Get Core 4 ArangoDB abstraction."""
        return self.get_infrastructure_abstraction("core4", "arangodb")
    
    # Authentication Infrastructure Access Methods
    def get_supabase_auth_abstraction(self):
        """Get Supabase authentication abstraction."""
        return self.get_infrastructure_abstraction("authentication", "supabase")
    
    # Event Bus Infrastructure Access Methods
    def get_redis_streams_abstraction(self):
        """Get Redis Streams abstraction."""
        return self.get_infrastructure_abstraction("event_bus", "redis_streams")
    
    def get_event_routing_abstraction(self):
        """Get Event Routing abstraction."""
        return self.get_infrastructure_abstraction("event_bus", "event_routing")
    
    def get_all_abstractions(self) -> Dict[str, Any]:
        """Get all infrastructure abstractions."""
        return self.infrastructure_abstractions
    
    def list_available_abstractions(self) -> Dict[str, list]:
        """List all available infrastructure abstractions."""
        available = {}
        for category, abstractions in self.infrastructure_abstractions.items():
            available[category] = list(abstractions.keys())
        return available
    
    # ============================================================================
    # HEALTH AND STATUS METHODS
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get service health status."""
        try:
            # Get base health status
            base_health = await super().get_service_health()
            
            # Add infrastructure-specific health info
            base_health.update({
                "infrastructure_abstractions_created": len(self.infrastructure_abstractions),
                "available_abstractions": self.list_available_abstractions(),
                "configuration_injected": {
                    "database": self.db_config is not None,
                    "redis": self.redis_config is not None,
                    "telemetry": self.telemetry_config is not None,
                    "search": self.search_config is not None,
                    "file_storage": self.file_storage_config is not None,
                    "workflow": self.workflow_config is not None
                }
            })
            
            return base_health
            
        except Exception as e:
            return {
                "service": "infrastructure_foundation",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }