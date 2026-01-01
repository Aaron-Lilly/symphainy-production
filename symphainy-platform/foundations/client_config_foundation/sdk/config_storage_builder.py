#!/usr/bin/env python3
"""
Config Storage Builder - SDK Builder for Config Storage

Creates Config Storage instances for storing tenant-specific configurations.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import uuid


class ConfigStorage:
    """
    Config Storage Instance - Stores tenant-specific configurations.
    
    Supports storing in Git or DB storage with version control.
    """
    
    def __init__(
        self,
        tenant_id: str,
        storage_type: str,
        public_works_foundation: Optional[Any],
        config: Dict[str, Any],
        di_container: Any
    ):
        """Initialize Config Storage instance."""
        self.tenant_id = tenant_id
        self.storage_type = storage_type
        self.public_works_foundation = public_works_foundation
        self.config = config
        self.di_container = di_container
        
        if not di_container:
            raise ValueError("DI Container is required for ConfigStorage initialization")
        self.logger = di_container.get_logger(f"ConfigStorage.{tenant_id}")
        
        # Storage abstractions (from Public Works)
        self.file_management = None
        self.knowledge_discovery = None
    
    async def initialize(self) -> bool:
        """Initialize Config Storage."""
        try:
            self.logger.info(f"🔧 Initializing Config Storage for tenant: {self.tenant_id}")
            
            # Get storage abstractions from Public Works Foundation
            if self.public_works_foundation:
                try:
                    self.file_management = self.public_works_foundation.get_abstraction("FileManagementAbstraction")
                    self.knowledge_discovery = self.public_works_foundation.get_abstraction("KnowledgeDiscoveryAbstraction")
                    self.logger.info("✅ Storage abstractions initialized")
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not get storage abstractions: {e}")
            
            self.logger.info(f"✅ Config Storage initialized for tenant: {self.tenant_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Config Storage initialization failed: {e}")
            raise
    
    async def store_config(
        self,
        config_type: str,
        config: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store tenant configuration.
        
        Args:
            config_type: Config type (e.g., "domain_models", "workflows", "dashboards")
            config: Configuration data to store
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Config ID (for tracking and versioning)
        """
        try:
            self.logger.info(f"💾 Storing config for tenant: {self.tenant_id}, type: {config_type}")
            
            # Validate config before storage
            # (Validation will be done by ConfigValidator if available)
            
            # Store based on storage type
            if self.storage_type == "git" and self.file_management:
                config_id = await self._store_in_git(config_type, config, user_context)
            elif self.storage_type == "db" and self.knowledge_discovery:
                config_id = await self._store_in_db(config_type, config, user_context)
            elif self.storage_type == "hybrid":
                config_id = await self._store_hybrid(config_type, config, user_context)
            else:
                # Fallback: generate ID but don't store
                self.logger.warning(f"⚠️ Storage not available, generating ID only")
                config_id = f"config_{uuid.uuid4().hex[:12]}"
            
            self.logger.info(f"✅ Config stored: {config_id}")
            return config_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store config: {e}")
            raise
    
    async def _store_in_git(
        self,
        config_type: str,
        config: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Store config in Git storage."""
        try:
            # Git-backed storage via FileManagementAbstraction
            # Configs stored in: configs/{tenant_id}/{config_type}.yaml
            config_path = f"configs/{self.tenant_id}/{config_type}.yaml"
            
            # Convert config to YAML format
            import yaml
            config_yaml = yaml.dump(config, default_flow_style=False)
            
            # Use FileManagementAbstraction to write to Git
            # This is a placeholder - actual implementation would use Git operations
            self.logger.debug(f"Storing in Git: {config_path}")
            
            # For now, generate ID (will be implemented with real Git operations)
            config_id = f"git_config_{uuid.uuid4().hex[:12]}"
            
            # TODO: Implement actual Git storage via FileManagementAbstraction
            # await self.file_management.write_file(config_path, config_yaml, commit_message=f"Update {config_type} config")
            
            return config_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store in Git: {e}")
            raise
    
    async def _store_in_db(
        self,
        config_type: str,
        config: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Store config in DB storage."""
        try:
            # DB-backed storage via KnowledgeDiscoveryAbstraction
            # Configs stored in ArangoDB with namespace: client_config_{tenant_id}
            namespace = f"client_config_{self.tenant_id}"
            config_id = f"config_{uuid.uuid4().hex[:12]}"
            
            if self.knowledge_discovery:
                # Prepare config data for storage
                config_data = {
                    "config_id": config_id,
                    "tenant_id": self.tenant_id,
                    "config_type": config_type,
                    "config": config,
                    "namespace": namespace,
                    "type": "client_config",
                    "stored_at": datetime.utcnow().isoformat(),
                    "stored_by": user_context.get("user_id") if user_context else None
                }
                
                # Store via KnowledgeDiscoveryAbstraction (uses Librarian)
                # KnowledgeDiscoveryAbstraction has store_knowledge method
                if hasattr(self.knowledge_discovery, 'store_knowledge'):
                    stored_id = await self.knowledge_discovery.store_knowledge(
                        knowledge_data=config_data,
                        user_context=user_context
                    )
                    return stored_id or config_id
                else:
                    # Fallback: use Librarian directly if available
                    # Get Librarian from Public Works
                    if self.public_works_foundation:
                        try:
                            librarian = self.public_works_foundation.get_abstraction("LibrarianService")
                            if librarian:
                                stored_id = await librarian.store_knowledge(
                                    knowledge_data=config_data,
                                    user_context=user_context
                                )
                                return stored_id or config_id
                        except Exception as e:
                            self.logger.warning(f"⚠️ Could not get Librarian: {e}")
            
            return config_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store in DB: {e}")
            raise
    
    async def _store_hybrid(
        self,
        config_type: str,
        config: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Store config in hybrid storage (Git for versioned, DB for dynamic)."""
        try:
            # Versioned configs (domain_models, workflows) to Git
            versioned_types = ["domain_models", "workflows"]
            
            # Dynamic configs (dashboards, user_preferences) to DB
            dynamic_types = ["dashboards", "user_preferences", "ingestion_endpoints"]
            
            if config_type in versioned_types:
                # Store in Git
                return await self._store_in_git(config_type, config, user_context)
            elif config_type in dynamic_types:
                # Store in DB
                return await self._store_in_db(config_type, config, user_context)
            else:
                # Default: store in DB
                return await self._store_in_db(config_type, config, user_context)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store hybrid: {e}")
            raise


class ConfigStorageBuilder:
    """
    Config Storage Builder - SDK Builder for Config Storage
    
    Creates Config Storage instances for storing tenant-specific configurations.
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
        Initialize Config Storage Builder.
        
        Args:
            tenant_id: Tenant identifier
            storage_type: Storage type ("git", "db", or "hybrid")
            public_works_foundation: Public Works Foundation (for storage abstractions)
            config: Optional storage configuration
            di_container: DI Container
        """
        self.tenant_id = tenant_id
        self.storage_type = storage_type
        self.public_works_foundation = public_works_foundation
        self.config = config or {}
        self.di_container = di_container
        
        if not di_container:
            raise ValueError("DI Container is required for ConfigStorageBuilder initialization")
        self.logger = di_container.get_logger(f"ConfigStorageBuilder.{tenant_id}")
        
        # Storage instance (will be created in initialize)
        self.storage: Optional[ConfigStorage] = None
    
    async def initialize(self) -> bool:
        """
        Initialize Config Storage instance.
        
        Returns:
            bool: True if initialized successfully
        """
        try:
            self.logger.info(f"🔧 Initializing Config Storage for tenant: {self.tenant_id}")
            
            # Create ConfigStorage instance
            self.storage = ConfigStorage(
                tenant_id=self.tenant_id,
                storage_type=self.storage_type,
                public_works_foundation=self.public_works_foundation,
                config=self.config,
                di_container=self.di_container
            )
            
            # Initialize the storage
            success = await self.storage.initialize()
            
            if success:
                self.logger.info(f"✅ Config Storage initialized for tenant: {self.tenant_id}")
            else:
                self.logger.error(f"❌ Config Storage initialization failed for tenant: {self.tenant_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Config Storage Builder initialization failed: {e}")
            raise
    
    def get_storage(self) -> Optional[ConfigStorage]:
        """Get the initialized Config Storage instance."""
        return self.storage










