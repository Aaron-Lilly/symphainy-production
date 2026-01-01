#!/usr/bin/env python3
"""
Cloud-Ready Platform Orchestrator - Parallel Implementation

Simplified startup process for cloud-ready architecture.
Runs in parallel with current main.py.

WHAT (Platform Orchestrator): I orchestrate platform startup with cloud-ready patterns
HOW (Implementation): I use auto-discovery, unified registry, and simplified initialization
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from utilities.configuration.cloud_ready_config import get_cloud_ready_config
from foundations.di_container.di_container_service import DIContainerService
from foundations.di_container.unified_service_registry import UnifiedServiceRegistry, ServiceType, ServiceLifecycleState
from utilities.api_routing.fastapi_router_manager import FastAPIRouterManager

logger = logging.getLogger(__name__)


class CloudReadyPlatformOrchestrator:
    """
    Cloud-Ready Platform Orchestrator - Simplified Startup
    
    Provides a simplified startup process for cloud-ready architecture:
    - Bootstrap phase (minimal required services)
    - Auto-discovery phase (automatic)
    - Dependency resolution phase (automatic)
    - Lazy initialization (on-demand)
    """
    
    def __init__(self):
        """Initialize Cloud-Ready Platform Orchestrator."""
        self.logger = logging.getLogger("CloudReadyPlatformOrchestrator")
        self.di_container: Optional[DIContainerService] = None
        self.router_manager: Optional[FastAPIRouterManager] = None
        self.public_works_foundation = None
        self.curator_foundation = None
        self.agentic_foundation = None
        self.experience_foundation = None
        self.startup_status: Dict[str, Any] = {}
        self.startup_sequence: List[str] = []
        
        self.logger.info("🏗️ Cloud-Ready Platform Orchestrator initialized")
    
    async def orchestrate_platform_startup(self) -> Dict[str, Any]:
        """
        Orchestrate platform startup (cloud-ready mode).
        
        Simplified startup sequence:
        1. Bootstrap phase (minimal required services)
        2. Auto-discovery phase (automatic)
        3. Dependency resolution phase (automatic)
        4. Lazy initialization (on-demand)
        
        Returns:
            Dictionary with startup result
        """
        self.logger.info("🚀 Starting SymphAIny Platform (Cloud-Ready Mode)")
        
        try:
            # Phase 1: Bootstrap (Minimal, Must Start)
            await self._bootstrap_phase()
            
            # Phase 2: Auto-Discovery (Automatic)
            cloud_ready_config = get_cloud_ready_config()
            if cloud_ready_config.should_use_auto_discovery():
                await self._auto_discovery_phase()
            
            # Phase 3: Dependency Resolution (Automatic)
            if cloud_ready_config.should_use_unified_registry():
                await self._dependency_resolution_phase()
            
            # Phase 4: Lazy Initialization (On-Demand)
            self.logger.info("🌀 Services configured for lazy initialization")
            self.startup_status["lazy_initialization"] = "ready"
            self.startup_sequence.append("lazy_initialization")
            
            self.logger.info("🎉 Cloud-Ready Platform orchestration completed successfully!")
            self.logger.info("   ✅ Bootstrap phase completed")
            self.logger.info("   ✅ Auto-discovery completed (if enabled)")
            self.logger.info("   ✅ Dependency resolution completed (if enabled)")
            self.logger.info("   ✅ Lazy initialization ready")
            
            return {
                "success": True,
                "mode": "cloud_ready",
                "startup_sequence": self.startup_sequence,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Cloud-ready startup failed: {e}")
            raise
    
    async def _bootstrap_phase(self):
        """
        Bootstrap phase - minimal required services.
        
        Only initializes services that MUST start for the platform to function.
        """
        self.logger.info("🔧 Phase 1: Bootstrap Phase (Minimal Required Services)")
        
        # 1. DI Container
        self.di_container = DIContainerService("platform_orchestrated")
        self.startup_status["di_container"] = "initialized"
        self.startup_sequence.append("di_container")
        self.logger.info("✅ DI Container initialized")
        
        # 2. FastAPIRouterManager (utility)
        self.router_manager = FastAPIRouterManager()
        await self.router_manager.initialize()
        # Register in DI Container
        if self.di_container.unified_registry:
            self.di_container.unified_registry.register(
                service_name="FastAPIRouterManager",
                service_type=ServiceType.UTILITY,
                instance=self.router_manager,
                dependencies=[],
                metadata={"type": "utility"}
            )
        self.di_container.service_registry["FastAPIRouterManager"] = self.router_manager
        self.startup_status["router_manager"] = "initialized"
        self.startup_sequence.append("router_manager")
        self.logger.info("✅ FastAPI Router Manager initialized")
        
        # 3. Public Works Foundation
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        self.public_works_foundation = PublicWorksFoundationService(di_container=self.di_container)
        await self.public_works_foundation.initialize()
        # Register in DI Container
        if self.di_container.unified_registry:
            self.di_container.unified_registry.register(
                service_name="PublicWorksFoundationService",
                service_type=ServiceType.FOUNDATION,
                instance=self.public_works_foundation,
                dependencies=["DIContainerService"],
                metadata={"type": "foundation"}
            )
        self.di_container.public_works_foundation = self.public_works_foundation
        self.di_container.service_registry["PublicWorksFoundationService"] = self.public_works_foundation
        self.startup_status["public_works_foundation"] = "initialized"
        self.startup_sequence.append("public_works_foundation")
        self.logger.info("✅ Public Works Foundation initialized")
        
        # 4. Curator Foundation
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        self.curator_foundation = CuratorFoundationService(
            foundation_services=self.di_container,
            public_works_foundation=self.public_works_foundation
        )
        await self.curator_foundation.initialize()
        # Register in DI Container
        if self.di_container.unified_registry:
            self.di_container.unified_registry.register(
                service_name="CuratorFoundationService",
                service_type=ServiceType.FOUNDATION,
                instance=self.curator_foundation,
                dependencies=["DIContainerService", "PublicWorksFoundationService"],
                metadata={"type": "foundation"}
            )
        self.di_container.service_registry["CuratorFoundationService"] = self.curator_foundation
        self.startup_status["curator_foundation"] = "initialized"
        self.startup_sequence.append("curator_foundation")
        self.logger.info("✅ Curator Foundation initialized")
        
        # 5. Agentic Foundation
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        self.agentic_foundation = AgenticFoundationService(
            di_container=self.di_container,
            public_works_foundation=self.public_works_foundation,
            curator_foundation=self.curator_foundation
        )
        await self.agentic_foundation.initialize()
        # Register in DI Container
        if self.di_container.unified_registry:
            self.di_container.unified_registry.register(
                service_name="AgenticFoundationService",
                service_type=ServiceType.FOUNDATION,
                instance=self.agentic_foundation,
                dependencies=["DIContainerService", "PublicWorksFoundationService", "CuratorFoundationService"],
                metadata={"type": "foundation"}
            )
        self.di_container.service_registry["AgenticFoundationService"] = self.agentic_foundation
        self.startup_status["agentic_foundation"] = "initialized"
        self.startup_sequence.append("agentic_foundation")
        self.logger.info("✅ Agentic Foundation initialized")
        
        # 6. Experience Foundation
        from foundations.experience_foundation.experience_foundation_service import ExperienceFoundationService
        self.experience_foundation = ExperienceFoundationService(
            di_container=self.di_container,
            public_works_foundation=self.public_works_foundation,
            curator_foundation=self.curator_foundation
        )
        await self.experience_foundation.initialize()
        # Register in DI Container
        if self.di_container.unified_registry:
            self.di_container.unified_registry.register(
                service_name="ExperienceFoundationService",
                service_type=ServiceType.FOUNDATION,
                instance=self.experience_foundation,
                dependencies=["DIContainerService", "PublicWorksFoundationService", "CuratorFoundationService"],
                metadata={"type": "foundation"}
            )
        self.di_container.service_registry["ExperienceFoundationService"] = self.experience_foundation
        self.startup_status["experience_foundation"] = "initialized"
        self.startup_sequence.append("experience_foundation")
        self.logger.info("✅ Experience Foundation initialized")
        
        self.startup_status["bootstrap"] = "completed"
        self.logger.info("✅ Bootstrap phase completed")
    
    async def _auto_discovery_phase(self):
        """
        Auto-discovery phase - discover all services automatically.
        
        Uses Curator Foundation's auto-discovery service to discover and register services.
        """
        self.logger.info("🔍 Phase 2: Auto-Discovery Phase")
        
        if not self.curator_foundation or not self.curator_foundation.auto_discovery:
            self.logger.warning("⚠️ Auto-discovery not available, skipping...")
            return
        
        try:
            # Run auto-discovery
            discovered_services = await self.curator_foundation.auto_discovery.discover_all_services()
            
            if discovered_services:
                # Register discovered services
                registration_results = await self.curator_foundation.auto_discovery.register_discovered_services(discovered_services)
                registered_count = len(registration_results.get("registered", []))
                self.logger.info(f"✅ Auto-discovery completed: {registered_count} services discovered")
                self.startup_status["auto_discovery"] = "completed"
                self.startup_sequence.append("auto_discovery")
            else:
                self.logger.info("ℹ️ No services discovered (may be normal if services are lazy-loaded)")
                self.startup_status["auto_discovery"] = "completed"
                self.startup_sequence.append("auto_discovery")
        
        except Exception as e:
            self.logger.error(f"❌ Auto-discovery phase failed: {e}")
            # Don't fail startup - auto-discovery is optional
            self.startup_status["auto_discovery"] = "failed"
    
    async def _dependency_resolution_phase(self):
        """
        Dependency resolution phase - resolve and initialize services.
        
        Uses unified registry to resolve service dependencies and initialize services in order.
        """
        self.logger.info("🔧 Phase 3: Dependency Resolution Phase")
        
        if not self.di_container or not self.di_container.unified_registry:
            self.logger.warning("⚠️ Unified registry not available, skipping dependency resolution...")
            return
        
        try:
            # Resolve dependency order
            service_order = self.di_container.unified_registry.resolve_dependencies()
            
            self.logger.info(f"✅ Resolved dependency order: {len(service_order)} services")
            self.startup_status["dependency_resolution"] = "completed"
            self.startup_sequence.append("dependency_resolution")
            
            # Note: Services are initialized lazily on-demand
            # This phase just ensures dependencies are resolved
            # Actual initialization happens when services are first accessed
        
        except Exception as e:
            self.logger.error(f"❌ Dependency resolution phase failed: {e}")
            # Don't fail startup - dependency resolution is optional
            self.startup_status["dependency_resolution"] = "failed"
    
    def get_di_container(self) -> Optional[DIContainerService]:
        """Get DI Container instance."""
        return self.di_container
    
    def get_router_manager(self) -> Optional[FastAPIRouterManager]:
        """Get FastAPI Router Manager instance."""
        return self.router_manager
    
    def get_foundation_service(self, service_name: str) -> Optional[Any]:
        """Get foundation service by name."""
        if not self.di_container:
            return None
        return self.di_container.get_foundation_service(service_name)
    
    @property
    def foundation_services(self) -> Dict[str, Any]:
        """Get foundation services dictionary (for compatibility with register_api_routers)."""
        services = {}
        if self.di_container:
            # Get all foundation services from DI Container
            foundation_names = [
                "PublicWorksFoundationService",
                "CuratorFoundationService",
                "AgenticFoundationService",
                "ExperienceFoundationService"
            ]
            for name in foundation_names:
                service = self.di_container.get_foundation_service(name)
                if service:
                    services[name] = service
        return services
    
    @property
    def managers(self) -> Dict[str, Any]:
        """Get managers dictionary (for compatibility - empty in cloud-ready mode)."""
        return {}
    
    async def get_platform_status(self) -> Dict[str, Any]:
        """Get platform status."""
        return {
            "mode": "cloud_ready",
            "startup_status": self.startup_status,
            "startup_sequence": self.startup_sequence,
            "timestamp": datetime.utcnow().isoformat()
        }

