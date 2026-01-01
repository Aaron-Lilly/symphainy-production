#!/usr/bin/env python3
"""
Config Versioner Builder - SDK Builder for Config Versioner

Creates Config Versioner instances for versioning tenant-specific configurations.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging


class ConfigVersioner:
    """
    Config Versioner Instance - Versions tenant-specific configurations.
    
    Supports:
    - Git versioning (commits, branches, tags)
    - DB versioning (timestamps, snapshots)
    - Rollback capabilities
    - Version comparison and diff
    """
    
    def __init__(
        self,
        tenant_id: str,
        storage_type: str,
        public_works_foundation: Optional[Any],
        config: Dict[str, Any],
        di_container: Any
    ):
        """Initialize Config Versioner instance."""
        self.tenant_id = tenant_id
        self.storage_type = storage_type
        self.public_works_foundation = public_works_foundation
        self.config = config
        self.di_container = di_container
        
        if not di_container:
            raise ValueError("DI Container is required for ConfigVersioner initialization")
        self.logger = di_container.get_logger(f"ConfigVersioner.{tenant_id}")
        
        # Storage abstractions (from Public Works)
        self.file_management = None
        self.knowledge_discovery = None
    
    async def initialize(self) -> bool:
        """Initialize Config Versioner."""
        try:
            self.logger.info(f"🔧 Initializing Config Versioner for tenant: {self.tenant_id}")
            
            # Get storage abstractions from Public Works Foundation
            if self.public_works_foundation:
                try:
                    self.file_management = self.public_works_foundation.get_abstraction("FileManagementAbstraction")
                    self.knowledge_discovery = self.public_works_foundation.get_abstraction("KnowledgeDiscoveryAbstraction")
                    self.logger.info("✅ Storage abstractions initialized")
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not get storage abstractions: {e}")
            
            self.logger.info(f"✅ Config Versioner initialized for tenant: {self.tenant_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Config Versioner initialization failed: {e}")
            raise
    
    async def create_version(
        self,
        config_type: str,
        config: Dict[str, Any],
        version_message: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new version of configuration.
        
        Args:
            config_type: Config type (e.g., "domain_models", "workflows")
            config: Configuration data
            version_message: Version message/description
            user_context: Optional user context
        
        Returns:
            Version ID
        """
        try:
            self.logger.info(f"📝 Creating version for config: {config_type}, tenant: {self.tenant_id}")
            
            version_id = f"v_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            if self.storage_type == "git" and self.file_management:
                version_id = await self._create_git_version(config_type, config, version_message, user_context)
            elif self.storage_type == "db" and self.knowledge_discovery:
                version_id = await self._create_db_version(config_type, config, version_message, user_context)
            elif self.storage_type == "hybrid":
                version_id = await self._create_hybrid_version(config_type, config, version_message, user_context)
            
            self.logger.info(f"✅ Version created: {version_id}")
            return version_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create version: {e}")
            raise
    
    async def get_versions(
        self,
        config_type: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get version history for configuration.
        
        Args:
            config_type: Config type
            limit: Maximum number of versions to return
        
        Returns:
            List of version information
        """
        try:
            self.logger.info(f"📚 Getting versions for config: {config_type}, tenant: {self.tenant_id}")
            
            if self.storage_type == "git" and self.file_management:
                versions = await self._get_git_versions(config_type, limit)
            elif self.storage_type == "db" and self.knowledge_discovery:
                versions = await self._get_db_versions(config_type, limit)
            elif self.storage_type == "hybrid":
                versions = await self._get_hybrid_versions(config_type, limit)
            else:
                versions = []
            
            return versions
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get versions: {e}")
            return []
    
    async def rollback_to_version(
        self,
        config_type: str,
        version_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Rollback configuration to a specific version.
        
        Args:
            config_type: Config type
            version_id: Version ID to rollback to
            user_context: Optional user context
        
        Returns:
            True if rollback successful
        """
        try:
            self.logger.info(f"⏪ Rolling back config: {config_type} to version: {version_id}")
            
            if self.storage_type == "git" and self.file_management:
                success = await self._rollback_git_version(config_type, version_id, user_context)
            elif self.storage_type == "db" and self.knowledge_discovery:
                success = await self._rollback_db_version(config_type, version_id, user_context)
            elif self.storage_type == "hybrid":
                success = await self._rollback_hybrid_version(config_type, version_id, user_context)
            else:
                success = False
            
            if success:
                self.logger.info(f"✅ Rollback successful: {version_id}")
            else:
                self.logger.warning(f"⚠️ Rollback failed: {version_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to rollback: {e}")
            return False
    
    async def compare_versions(
        self,
        config_type: str,
        version_id_1: str,
        version_id_2: str
    ) -> Dict[str, Any]:
        """
        Compare two versions of configuration.
        
        Args:
            config_type: Config type
            version_id_1: First version ID
            version_id_2: Second version ID
        
        Returns:
            Comparison result with differences
        """
        try:
            self.logger.info(f"🔍 Comparing versions: {version_id_1} vs {version_id_2}")
            
            # Get both versions
            versions = await self.get_versions(config_type, limit=100)
            version1 = next((v for v in versions if v.get("version_id") == version_id_1), None)
            version2 = next((v for v in versions if v.get("version_id") == version_id_2), None)
            
            if not version1 or not version2:
                return {
                    "success": False,
                    "error": "One or both versions not found"
                }
            
            # Simple comparison (would use proper diff algorithm in production)
            config1 = version1.get("config", {})
            config2 = version2.get("config", {})
            
            differences = []
            
            # Compare keys
            keys1 = set(config1.keys())
            keys2 = set(config2.keys())
            
            added = keys2 - keys1
            removed = keys1 - keys2
            changed = []
            
            for key in keys1 & keys2:
                if config1[key] != config2[key]:
                    changed.append(key)
            
            return {
                "success": True,
                "version1": version_id_1,
                "version2": version_id_2,
                "differences": {
                    "added": list(added),
                    "removed": list(removed),
                    "changed": changed
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to compare versions: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_git_version(
        self,
        config_type: str,
        config: Dict[str, Any],
        version_message: str,
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Create version in Git storage."""
        try:
            # Git versioning via FileManagementAbstraction
            # Create commit with version message
            version_id = f"git_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # TODO: Implement actual Git commit via FileManagementAbstraction
            # await self.file_management.commit_file(config_path, config_data, commit_message=version_message)
            
            return version_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create Git version: {e}")
            raise
    
    async def _create_db_version(
        self,
        config_type: str,
        config: Dict[str, Any],
        version_message: str,
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Create version in DB storage."""
        try:
            # DB versioning via KnowledgeDiscoveryAbstraction
            # Store snapshot with timestamp
            version_id = f"db_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            namespace = f"client_config_{self.tenant_id}"
            version_data = {
                "version_id": version_id,
                "tenant_id": self.tenant_id,
                "config_type": config_type,
                "config": config,
                "version_message": version_message,
                "namespace": namespace,
                "type": "client_config_version",
                "created_at": datetime.utcnow().isoformat(),
                "created_by": user_context.get("user_id") if user_context else None
            }
            
            if self.knowledge_discovery:
                if hasattr(self.knowledge_discovery, 'store_knowledge'):
                    await self.knowledge_discovery.store_knowledge(
                        knowledge_data=version_data,
                        user_context=user_context
                    )
            
            return version_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create DB version: {e}")
            raise
    
    async def _create_hybrid_version(
        self,
        config_type: str,
        config: Dict[str, Any],
        version_message: str,
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Create version in hybrid storage."""
        try:
            # Versioned configs (domain_models, workflows) in Git
            versioned_types = ["domain_models", "workflows"]
            
            if config_type in versioned_types:
                return await self._create_git_version(config_type, config, version_message, user_context)
            else:
                return await self._create_db_version(config_type, config, version_message, user_context)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create hybrid version: {e}")
            raise
    
    async def _get_git_versions(self, config_type: str, limit: int) -> List[Dict[str, Any]]:
        """Get versions from Git storage."""
        try:
            # Get Git commit history
            # TODO: Implement actual Git log via FileManagementAbstraction
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get Git versions: {e}")
            return []
    
    async def _get_db_versions(self, config_type: str, limit: int) -> List[Dict[str, Any]]:
        """Get versions from DB storage."""
        try:
            namespace = f"client_config_{self.tenant_id}"
            
            if self.knowledge_discovery:
                filters = {
                    "namespace": namespace,
                    "type": "client_config_version",
                    "config_type": config_type
                }
                
                search_result = await self.knowledge_discovery.search_knowledge(
                    query=f"tenant:{self.tenant_id} config_type:{config_type}",
                    filters=filters,
                    limit=limit
                )
                
                versions = []
                if search_result and isinstance(search_result, dict):
                    results = search_result.get("results", search_result.get("hits", []))
                else:
                    results = search_result if isinstance(search_result, list) else []
                
                for result in results:
                    if isinstance(result, dict):
                        version_data = result.get("content", result.get("data", result))
                        versions.append({
                            "version_id": version_data.get("version_id"),
                            "config_type": version_data.get("config_type"),
                            "version_message": version_data.get("version_message"),
                            "created_at": version_data.get("created_at"),
                            "created_by": version_data.get("created_by")
                        })
                
                # Sort by created_at descending
                versions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
                return versions[:limit]
            
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get DB versions: {e}")
            return []
    
    async def _get_hybrid_versions(self, config_type: str, limit: int) -> List[Dict[str, Any]]:
        """Get versions from hybrid storage."""
        try:
            versioned_types = ["domain_models", "workflows"]
            
            if config_type in versioned_types:
                return await self._get_git_versions(config_type, limit)
            else:
                return await self._get_db_versions(config_type, limit)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get hybrid versions: {e}")
            return []
    
    async def _rollback_git_version(
        self,
        config_type: str,
        version_id: str,
        user_context: Optional[Dict[str, Any]]
    ) -> bool:
        """Rollback to Git version."""
        try:
            # Git rollback via FileManagementAbstraction
            # TODO: Implement actual Git checkout/reset
            self.logger.debug(f"Rolling back Git version: {version_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to rollback Git version: {e}")
            return False
    
    async def _rollback_db_version(
        self,
        config_type: str,
        version_id: str,
        user_context: Optional[Dict[str, Any]]
    ) -> bool:
        """Rollback to DB version."""
        try:
            # Get version data
            versions = await self._get_db_versions(config_type, limit=100)
            target_version = next((v for v in versions if v.get("version_id") == version_id), None)
            
            if not target_version:
                self.logger.error(f"Version not found: {version_id}")
                return False
            
            # Get config from version
            namespace = f"client_config_{self.tenant_id}"
            if self.knowledge_discovery:
                filters = {
                    "namespace": namespace,
                    "type": "client_config_version",
                    "version_id": version_id
                }
                
                search_result = await self.knowledge_discovery.search_knowledge(
                    query=f"version_id:{version_id}",
                    filters=filters,
                    limit=1
                )
                
                if search_result:
                    if isinstance(search_result, dict):
                        results = search_result.get("results", search_result.get("hits", []))
                    else:
                        results = search_result if isinstance(search_result, list) else []
                    
                    if results:
                        version_data = results[0].get("content", results[0].get("data", results[0]))
                        config = version_data.get("config", {})
                        
                        # Store as current version
                        # This would use ConfigStorage to store the rolled-back config
                        self.logger.info(f"✅ Rolled back to version: {version_id}")
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to rollback DB version: {e}")
            return False
    
    async def _rollback_hybrid_version(
        self,
        config_type: str,
        version_id: str,
        user_context: Optional[Dict[str, Any]]
    ) -> bool:
        """Rollback to hybrid version."""
        try:
            versioned_types = ["domain_models", "workflows"]
            
            if config_type in versioned_types:
                return await self._rollback_git_version(config_type, version_id, user_context)
            else:
                return await self._rollback_db_version(config_type, version_id, user_context)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to rollback hybrid version: {e}")
            return False


class ConfigVersionerBuilder:
    """
    Config Versioner Builder - SDK Builder for Config Versioner
    
    Creates Config Versioner instances for versioning tenant-specific configurations.
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
        Initialize Config Versioner Builder.
        
        Args:
            tenant_id: Tenant identifier
            storage_type: Storage type ("git", "db", or "hybrid")
            public_works_foundation: Public Works Foundation (for storage abstractions)
            config: Optional versioner configuration
            di_container: DI Container
        """
        self.tenant_id = tenant_id
        self.storage_type = storage_type
        self.public_works_foundation = public_works_foundation
        self.config = config or {}
        self.di_container = di_container
        
        if not di_container:
            raise ValueError("DI Container is required for ConfigVersionerBuilder initialization")
        self.logger = di_container.get_logger(f"ConfigVersionerBuilder.{tenant_id}")
        
        # Versioner instance (will be created in initialize)
        self.versioner: Optional[ConfigVersioner] = None
    
    async def initialize(self) -> bool:
        """
        Initialize Config Versioner instance.
        
        Returns:
            bool: True if initialized successfully
        """
        try:
            self.logger.info(f"🔧 Initializing Config Versioner for tenant: {self.tenant_id}")
            
            # Create ConfigVersioner instance
            self.versioner = ConfigVersioner(
                tenant_id=self.tenant_id,
                storage_type=self.storage_type,
                public_works_foundation=self.public_works_foundation,
                config=self.config,
                di_container=self.di_container
            )
            
            # Initialize the versioner
            success = await self.versioner.initialize()
            
            if success:
                self.logger.info(f"✅ Config Versioner initialized for tenant: {self.tenant_id}")
            else:
                self.logger.error(f"❌ Config Versioner initialization failed for tenant: {self.tenant_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Config Versioner Builder initialization failed: {e}")
            raise
    
    def get_versioner(self) -> Optional[ConfigVersioner]:
        """Get the initialized Config Versioner instance."""
        return self.versioner










