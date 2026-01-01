#!/usr/bin/env python3
"""
File Management Registry - Service Registration and Discovery

Registers and manages file management services for the platform.
This is Layer 5 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I register and manage file management services
HOW (Infrastructure Implementation): I coordinate service initialization and discovery
"""

import logging
from typing import Dict, Any, Optional

from ..infrastructure_adapters.supabase_file_management_adapter import SupabaseFileManagementAdapter
from ..infrastructure_abstractions.file_management_abstraction import FileManagementAbstraction
from ..composition_services.file_management_composition_service import FileManagementCompositionService

logger = logging.getLogger(__name__)

class FileManagementRegistry:
    """
    Registry for file management services.
    
    Manages the initialization, configuration, and discovery of all
    file management related services in the 5-layer architecture.
    """
    
    def __init__(self, config_adapter):
        """Initialize file management registry."""
        self.config_adapter = config_adapter
        self.logger = logging.getLogger(__name__)
        
        # Service instances
        self.supabase_adapter: Optional[SupabaseFileManagementAdapter] = None
        self.file_management_abstraction: Optional[FileManagementAbstraction] = None
        self.file_management_composition: Optional[FileManagementCompositionService] = None
        
        # Service status
        self.is_initialized = False
        self.initialization_error = None
        
        self.logger.info("✅ File Management Registry initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize all file management services.
        
        Returns:
            bool indicating success
        """
        try:
            self.logger.info("🚀 Initializing File Management Registry...")
            
            # Step 1: Initialize Supabase adapter (Layer 1)
            await self._initialize_supabase_adapter()
            
            # Step 2: Initialize file management abstraction (Layer 3)
            await self._initialize_file_management_abstraction()
            
            # Step 3: Initialize composition service (Layer 4)
            await self._initialize_file_management_composition()
            
            # Step 4: Verify all services are healthy
            await self._verify_services_health()
            
            self.is_initialized = True
            self.initialization_error = None
            
            self.logger.info("✅ File Management Registry initialization completed successfully")
            return True
            
        except Exception as e:
            self.initialization_error = str(e)
            self.logger.error(f"❌ File Management Registry initialization failed: {e}")
            return False
    
    async def _initialize_supabase_adapter(self):
        """Initialize Supabase file management adapter."""
        try:
            self.logger.info("🔧 Initializing Supabase File Management Adapter...")
            
            # Get Supabase configuration
            supabase_url = self.config_adapter.get_supabase_url()
            supabase_key = self.config_adapter.get_supabase_service_key()
            
            if not supabase_url or not supabase_key:
                raise ValueError(
                    "Supabase configuration is required. Set SUPABASE_URL and one of:\n"
                    "  - SUPABASE_SECRET_KEY (new naming, preferred)\n"
                    "  - SUPABASE_SERVICE_KEY (legacy naming)\n"
                    "  - SUPABASE_KEY (generic fallback)"
                )
            
            # Create and connect adapter
            self.supabase_adapter = SupabaseFileManagementAdapter(supabase_url, supabase_key)
            
            # Connect to adapter
            connected = await self.supabase_adapter.connect()
            if not connected:
                raise ConnectionError("Failed to connect to Supabase")
            
            self.logger.info("✅ Supabase File Management Adapter initialized and connected")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Supabase adapter: {e}")
            raise
    
    async def _initialize_file_management_abstraction(self):
        """Initialize file management abstraction."""
        try:
            self.logger.info("🔧 Initializing File Management Abstraction...")
            
            if not self.supabase_adapter:
                raise ValueError("Supabase adapter not initialized")
            
            # Create abstraction with adapter and config
            self.file_management_abstraction = FileManagementAbstraction(
                self.supabase_adapter, 
                self.config_adapter
            )
            
            self.logger.info("✅ File Management Abstraction initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize file management abstraction: {e}")
            raise
    
    async def _initialize_file_management_composition(self):
        """Initialize file management composition service."""
        try:
            self.logger.info("🔧 Initializing File Management Composition Service...")
            
            if not self.file_management_abstraction:
                raise ValueError("File management abstraction not initialized")
            
            # Create composition service
            self.file_management_composition = FileManagementCompositionService(
                self.file_management_abstraction
            )
            
            self.logger.info("✅ File Management Composition Service initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize file management composition: {e}")
            raise
    
    async def _verify_services_health(self):
        """Verify all services are healthy."""
        try:
            self.logger.info("🔍 Verifying services health...")
            
            # Health checks work for both real and mock adapters
            # Check Supabase adapter health
            if self.supabase_adapter:
                health = await self.supabase_adapter.health_check()
                if health.get("status") != "healthy":
                    raise RuntimeError(f"Supabase adapter unhealthy: {health.get('message')}")
            
            # Check file management abstraction health
            if self.file_management_abstraction:
                health = await self.file_management_abstraction.health_check()
                if health.get("status") != "healthy":
                    raise RuntimeError(f"File management abstraction unhealthy: {health.get('message')}")
            
            self.logger.info("✅ All services verified healthy")
            
        except Exception as e:
            self.logger.error(f"❌ Service health verification failed: {e}")
            raise
    
    # ============================================================================
    # SERVICE DISCOVERY METHODS
    # ============================================================================
    
    def get_file_management_abstraction(self) -> Optional[FileManagementAbstraction]:
        """
        Get file management abstraction service.
        
        Returns:
            FileManagementAbstraction instance or None if not initialized
        """
        if not self.is_initialized:
            self.logger.warning("⚠️ File Management Registry not initialized")
            return None
        
        return self.file_management_abstraction
    
    def get_file_management_composition(self) -> Optional[FileManagementCompositionService]:
        """
        Get file management composition service.
        
        Returns:
            FileManagementCompositionService instance or None if not initialized
        """
        if not self.is_initialized:
            self.logger.warning("⚠️ File Management Registry not initialized")
            return None
        
        return self.file_management_composition
    
    def get_supabase_adapter(self) -> Optional[SupabaseFileManagementAdapter]:
        """
        Get Supabase file management adapter.
        
        Returns:
            SupabaseFileManagementAdapter instance or None if not initialized
        """
        if not self.is_initialized:
            self.logger.warning("⚠️ File Management Registry not initialized")
            return None
        
        return self.supabase_adapter
    
    # ============================================================================
    # SERVICE STATUS AND HEALTH
    # ============================================================================
    
    def get_registry_status(self) -> Dict[str, Any]:
        """
        Get registry status information.
        
        Returns:
            Dict containing registry status
        """
        return {
            "is_initialized": self.is_initialized,
            "initialization_error": self.initialization_error,
            "services": {
                "supabase_adapter": self.supabase_adapter is not None,
                "file_management_abstraction": self.file_management_abstraction is not None,
                "file_management_composition": self.file_management_composition is not None
            },
            "timestamp": self._get_current_timestamp()
        }
    
    async def get_services_health(self) -> Dict[str, Any]:
        """
        Get health status of all services.
        
        Returns:
            Dict containing health status of all services
        """
        health_status = {
            "registry_initialized": self.is_initialized,
            "services": {},
            "overall_status": "healthy",
            "timestamp": self._get_current_timestamp()
        }
        
        try:
            # Check Supabase adapter health
            if self.supabase_adapter:
                adapter_health = await self.supabase_adapter.health_check()
                health_status["services"]["supabase_adapter"] = adapter_health
            else:
                health_status["services"]["supabase_adapter"] = {
                    "status": "not_initialized",
                    "message": "Supabase adapter not initialized"
                }
            
            # Check file management abstraction health
            if self.file_management_abstraction:
                abstraction_health = await self.file_management_abstraction.health_check()
                health_status["services"]["file_management_abstraction"] = abstraction_health
            else:
                health_status["services"]["file_management_abstraction"] = {
                    "status": "not_initialized",
                    "message": "File management abstraction not initialized"
                }
            
            # Determine overall status
            service_statuses = [s.get("status", "unknown") for s in health_status["services"].values()]
            if "unhealthy" in service_statuses or "not_initialized" in service_statuses:
                health_status["overall_status"] = "unhealthy"
            
        except Exception as e:
            health_status["overall_status"] = "error"
            health_status["error"] = str(e)
            self.logger.error(f"❌ Error checking services health: {e}")
        
        return health_status
    
    # ============================================================================
    # SERVICE LIFECYCLE MANAGEMENT
    # ============================================================================
    
    async def shutdown(self):
        """Shutdown all services gracefully."""
        try:
            self.logger.info("🛑 Shutting down File Management Registry...")
            
            # Close Supabase adapter
            if self.supabase_adapter:
                await self.supabase_adapter.close()
            
            # Reset service instances
            self.supabase_adapter = None
            self.file_management_abstraction = None
            self.file_management_composition = None
            
            self.is_initialized = False
            
            self.logger.info("✅ File Management Registry shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during registry shutdown: {e}")
    
    async def restart(self) -> bool:
        """
        Restart all services.
        
        Returns:
            bool indicating success
        """
        try:
            self.logger.info("🔄 Restarting File Management Registry...")
            
            # Shutdown first
            await self.shutdown()
            
            # Reinitialize
            success = await self.initialize()
            
            if success:
                self.logger.info("✅ File Management Registry restart completed successfully")
            else:
                self.logger.error("❌ File Management Registry restart failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error during registry restart: {e}")
            return False
    
    # ============================================================================
    # CONFIGURATION AND METADATA
    # ============================================================================
    
    def get_service_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about registered services.
        
        Returns:
            Dict containing service metadata
        """
        return {
            "registry_name": "File Management Registry",
            "architecture_layer": "Layer 5 - Infrastructure Registry",
            "purpose": "Service registration and discovery for file management",
            "services_registered": {
                "supabase_adapter": {
                    "layer": "Layer 1 - Infrastructure Adapter",
                    "purpose": "Raw Supabase client wrapper",
                    "initialized": self.supabase_adapter is not None
                },
                "file_management_abstraction": {
                    "layer": "Layer 3 - Infrastructure Abstraction",
                    "purpose": "File management with business logic",
                    "initialized": self.file_management_abstraction is not None
                },
                "file_management_composition": {
                    "layer": "Layer 4 - Composition Service",
                    "purpose": "Complex workflow orchestration",
                    "initialized": self.file_management_composition is not None
                }
            },
            "initialization_status": self.is_initialized,
            "timestamp": self._get_current_timestamp()
        }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()




