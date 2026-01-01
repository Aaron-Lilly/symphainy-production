#!/usr/bin/env python3
"""
Config Loader Builder - SDK Builder for Config Loader

Creates Config Loader instances for loading tenant-specific configurations.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging


class ConfigLoader:
    """
    Config Loader Instance - Loads tenant-specific configurations.
    
    Supports loading from Git or DB storage.
    """
    
    def __init__(
        self,
        tenant_id: str,
        storage_type: str,
        public_works_foundation: Optional[Any],
        config: Dict[str, Any],
        di_container: Any
    ):
        """Initialize Config Loader instance."""
        self.tenant_id = tenant_id
        self.storage_type = storage_type
        self.public_works_foundation = public_works_foundation
        self.config = config
        self.di_container = di_container
        
        if not di_container:
            raise ValueError("DI Container is required for ConfigLoader initialization")
        self.logger = di_container.get_logger(f"ConfigLoader.{tenant_id}")
        
        # Storage abstractions (from Public Works)
        self.file_management = None
        self.knowledge_discovery = None
        
        # Config cache
        self.config_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = config.get("cache_ttl", 300)  # 5 minutes default
    
    async def initialize(self) -> bool:
        """Initialize Config Loader."""
        try:
            self.logger.info(f"🔧 Initializing Config Loader for tenant: {self.tenant_id}")
            
            # Get storage abstractions from Public Works Foundation
            if self.public_works_foundation:
                try:
                    self.file_management = self.public_works_foundation.get_abstraction("FileManagementAbstraction")
                    self.knowledge_discovery = self.public_works_foundation.get_abstraction("KnowledgeDiscoveryAbstraction")
                    self.logger.info("✅ Storage abstractions initialized")
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not get storage abstractions: {e}")
            
            self.logger.info(f"✅ Config Loader initialized for tenant: {self.tenant_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Config Loader initialization failed: {e}")
            raise
    
    async def load_tenant_config(self, config_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Load tenant configuration.
        
        Args:
            config_type: Optional config type filter (e.g., "domain_models", "workflows")
                        If None, loads all configs
        
        Returns:
            Dict containing tenant configurations
        """
        try:
            self.logger.info(f"📥 Loading config for tenant: {self.tenant_id}, type: {config_type or 'all'}")
            
            # Check cache first
            cache_key = f"{self.tenant_id}_{config_type or 'all'}"
            if cache_key in self.config_cache:
                cached_config = self.config_cache[cache_key]
                # Check if cache is still valid (simple TTL check)
                cache_time = cached_config.get("_cached_at", 0)
                if (datetime.utcnow().timestamp() - cache_time) < self.cache_ttl:
                    self.logger.debug(f"✅ Using cached config for {cache_key}")
                    return cached_config.get("config", {})
            
            # Load from storage
            if self.storage_type == "git" and self.file_management:
                config = await self._load_from_git(config_type)
            elif self.storage_type == "db" and self.knowledge_discovery:
                config = await self._load_from_db(config_type)
            elif self.storage_type == "hybrid":
                config = await self._load_hybrid(config_type)
            else:
                # Fallback: return empty config
                self.logger.warning(f"⚠️ Storage not available, returning empty config")
                config = {}
            
            # Cache the result
            self.config_cache[cache_key] = {
                "config": config,
                "_cached_at": datetime.utcnow().timestamp()
            }
            
            return config
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load tenant config: {e}")
            return {}
    
    async def load_config(self, tenant_id: str, config_type: str) -> Dict[str, Any]:
        """
        Load specific config type for tenant.
        
        Args:
            tenant_id: Tenant identifier
            config_type: Config type (e.g., "domain_models", "workflows", "dashboards")
        
        Returns:
            Dict containing the specific config
        """
        if tenant_id != self.tenant_id:
            raise ValueError(f"Config Loader is for tenant {self.tenant_id}, not {tenant_id}")
        
        all_configs = await self.load_tenant_config(config_type)
        return all_configs.get(config_type, {})
    
    async def _load_from_git(self, config_type: Optional[str]) -> Dict[str, Any]:
        """Load configs from Git storage."""
        try:
            # Git-backed storage via FileManagementAbstraction
            # Configs stored in: configs/{tenant_id}/{config_type}.yaml
            config_path = f"configs/{self.tenant_id}"
            
            if config_type:
                config_path = f"{config_path}/{config_type}.yaml"
            else:
                # Load all configs
                # List files in configs/{tenant_id}/ directory
                pass
            
            # Use FileManagementAbstraction to read from Git
            # This is a placeholder - actual implementation would use Git operations
            self.logger.debug(f"Loading from Git: {config_path}")
            
            # For now, return empty (will be implemented with real Git operations)
            return {}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load from Git: {e}")
            return {}
    
    async def _load_from_db(self, config_type: Optional[str]) -> Dict[str, Any]:
        """Load configs from DB storage."""
        try:
            # DB-backed storage via KnowledgeDiscoveryAbstraction
            # Configs stored in ArangoDB with namespace: client_config_{tenant_id}
            namespace = f"client_config_{self.tenant_id}"
            
            if self.knowledge_discovery:
                # Search for configs in namespace
                filters = {
                    "namespace": namespace,
                    "type": "client_config"
                }
                
                if config_type:
                    filters["config_type"] = config_type
                
                # Search knowledge base
                search_result = await self.knowledge_discovery.search_knowledge(
                    query=f"tenant:{self.tenant_id}",
                    filters=filters,
                    limit=100
                )
                
                # Extract configs from search results
                configs = {}
                if search_result and isinstance(search_result, dict):
                    results = search_result.get("results", search_result.get("hits", []))
                else:
                    results = search_result if isinstance(search_result, list) else []
                
                for result in results:
                    if isinstance(result, dict):
                        config_data = result.get("content", result.get("data", result))
                        config_type_found = config_data.get("config_type", "unknown")
                        configs[config_type_found] = config_data.get("config", {})
                
                return configs
            
            return {}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load from DB: {e}")
            return {}
    
    async def _load_hybrid(self, config_type: Optional[str]) -> Dict[str, Any]:
        """Load configs from hybrid storage (Git for versioned, DB for dynamic)."""
        try:
            # Versioned configs (domain_models, workflows) from Git
            versioned_types = ["domain_models", "workflows"]
            
            # Dynamic configs (dashboards, user_preferences) from DB
            dynamic_types = ["dashboards", "user_preferences", "ingestion_endpoints"]
            
            configs = {}
            
            if not config_type or config_type in versioned_types:
                # Load from Git
                git_configs = await self._load_from_git(config_type)
                configs.update(git_configs)
            
            if not config_type or config_type in dynamic_types:
                # Load from DB
                db_configs = await self._load_from_db(config_type)
                configs.update(db_configs)
            
            return configs
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load hybrid: {e}")
            return {}


class ConfigLoaderBuilder:
    """
    Config Loader Builder - SDK Builder for Config Loader
    
    Creates Config Loader instances for loading tenant-specific configurations.
    """
    
    def __init__(
        self,
        tenant_id: str,
        storage_type: str,
        public_works_foundation: Optional[Any],
        config: Dict[str, Any],
        di_container: Any
    ):
        """
        Initialize Config Loader Builder.
        
        Args:
            tenant_id: Tenant identifier
            storage_type: Storage type ("git", "db", or "hybrid")
            public_works_foundation: Public Works Foundation (for storage abstractions)
            config: Optional loader configuration
                - cache_ttl: Cache TTL in seconds (default: 300)
            di_container: DI Container
        """
        self.tenant_id = tenant_id
        self.storage_type = storage_type
        self.public_works_foundation = public_works_foundation
        self.config = config or {}
        self.di_container = di_container
        
        if not di_container:
            raise ValueError("DI Container is required for ConfigLoaderBuilder initialization")
        self.logger = di_container.get_logger(f"ConfigLoaderBuilder.{tenant_id}")
        
        # Loader instance (will be created in initialize)
        self.loader: Optional[ConfigLoader] = None
    
    async def initialize(self) -> bool:
        """
        Initialize Config Loader instance.
        
        Returns:
            bool: True if initialized successfully
        """
        try:
            self.logger.info(f"🔧 Initializing Config Loader for tenant: {self.tenant_id}")
            
            # Create ConfigLoader instance
            self.loader = ConfigLoader(
                tenant_id=self.tenant_id,
                storage_type=self.storage_type,
                public_works_foundation=self.public_works_foundation,
                config=self.config,
                di_container=self.di_container
            )
            
            # Initialize the loader
            success = await self.loader.initialize()
            
            if success:
                self.logger.info(f"✅ Config Loader initialized for tenant: {self.tenant_id}")
            else:
                self.logger.error(f"❌ Config Loader initialization failed for tenant: {self.tenant_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Config Loader Builder initialization failed: {e}")
            raise
    
    def get_loader(self) -> Optional[ConfigLoader]:
        """Get the initialized Config Loader instance."""
        return self.loader










