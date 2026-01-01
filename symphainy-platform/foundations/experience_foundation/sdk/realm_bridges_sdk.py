#!/usr/bin/env python3
"""
Realm Bridges SDK - Experience Foundation

Provides realm bridge capabilities for exposing Smart City and other realm services via REST.

WHAT (Experience SDK): I provide realm bridges for exposing services via REST
HOW (SDK Implementation): I manage realm bridge routers and register them with FastAPI Router Manager
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter

from utilities.api_routing.fastapi_router_manager import FastAPIRouterManager

logger = logging.getLogger(__name__)


class RealmBridgesSDK:
    """
    Realm Bridges SDK - Experience Foundation
    
    Provides realm bridge capabilities for exposing Smart City and other realm services via REST.
    Manages realm bridge routers and registers them with FastAPI Router Manager.
    
    WHAT (Experience SDK): I provide realm bridges for exposing services via REST
    HOW (SDK Implementation): I manage realm bridge routers and register them with FastAPI Router Manager
    """
    
    def __init__(
        self,
        di_container: Any,
        public_works_foundation: Any,
        curator_foundation: Any,
        router_manager: FastAPIRouterManager
    ):
        """Initialize Realm Bridges SDK."""
        self.logger = logging.getLogger("RealmBridgesSDK")
        
        # Dependencies
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        self.curator_foundation = curator_foundation
        self.router_manager = router_manager
        
        # Realm bridges (will be initialized)
        self.realm_bridges: Dict[str, Any] = {}
        
        # Service state
        self.is_initialized = False
        
        self.logger.info("🏗️ Realm Bridges SDK initialized")
    
    async def initialize(self):
        """Initialize Realm Bridges SDK and create realm bridges."""
        self.logger.info("🚀 Initializing Realm Bridges SDK...")
        
        try:
            # Create realm bridges for each realm
            await self._create_realm_bridges()
            
            # Register all bridge routers with FastAPI Router Manager
            await self._register_bridge_routers()
            
            self.is_initialized = True
            self.logger.info("✅ Realm Bridges SDK initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Realm Bridges SDK: {e}")
            raise
    
    async def get_realm_bridge(self, realm: str) -> Optional[Any]:
        """
        Get a realm bridge by realm name.
        
        Args:
            realm: Realm name (e.g., "smart_city", "journey", "solution")
        
        Returns:
            Realm bridge instance, or None if not found
        """
        return self.realm_bridges.get(realm)
    
    async def list_realm_bridges(self) -> Dict[str, Any]:
        """
        List all initialized realm bridges.
        
        Returns:
            Dict mapping realm names to bridge metadata
        """
        return {
            realm: {
                "realm": realm,
                "initialized": bridge is not None,
                "has_router": hasattr(bridge, "router") if bridge else False
            }
            for realm, bridge in self.realm_bridges.items()
        }
    
    # PRIVATE METHODS
    
    async def _create_realm_bridges(self):
        """Create realm bridges for each realm."""
        self.logger.info("🔧 Creating realm bridges...")
        
        # Create Smart City bridge
        try:
            from foundations.experience_foundation.realm_bridges.smart_city_bridge import SmartCityRealmBridge
            
            self.realm_bridges["smart_city"] = SmartCityRealmBridge(
                di_container=self.di_container,
                public_works_foundation=self.public_works_foundation,
                curator_foundation=self.curator_foundation
            )
            await self.realm_bridges["smart_city"].initialize()
            self.logger.info("✅ Smart City realm bridge created")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to create Smart City realm bridge: {e}")
            self.realm_bridges["smart_city"] = None
        
        # Create Journey bridge
        try:
            from foundations.experience_foundation.realm_bridges.journey_bridge import JourneyRealmBridge
            
            self.realm_bridges["journey"] = JourneyRealmBridge(
                di_container=self.di_container,
                public_works_foundation=self.public_works_foundation,
                curator_foundation=self.curator_foundation
            )
            await self.realm_bridges["journey"].initialize()
            self.logger.info("✅ Journey realm bridge created")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to create Journey realm bridge: {e}")
            self.realm_bridges["journey"] = None
        
        # Create Solution bridge
        try:
            from foundations.experience_foundation.realm_bridges.solution_bridge import SolutionRealmBridge
            
            self.realm_bridges["solution"] = SolutionRealmBridge(
                di_container=self.di_container,
                public_works_foundation=self.public_works_foundation,
                curator_foundation=self.curator_foundation
            )
            await self.realm_bridges["solution"].initialize()
            self.logger.info("✅ Solution realm bridge created")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to create Solution realm bridge: {e}")
            self.realm_bridges["solution"] = None
        
        # Create Business Enablement bridge
        try:
            from foundations.experience_foundation.realm_bridges.business_enablement_bridge import BusinessEnablementRealmBridge
            
            self.realm_bridges["business_enablement"] = BusinessEnablementRealmBridge(
                di_container=self.di_container,
                public_works_foundation=self.public_works_foundation,
                curator_foundation=self.curator_foundation
            )
            await self.realm_bridges["business_enablement"].initialize()
            self.logger.info("✅ Business Enablement realm bridge created")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to create Business Enablement realm bridge: {e}")
            self.realm_bridges["business_enablement"] = None
        
        # Create Experience Foundation bridge
        try:
            from foundations.experience_foundation.realm_bridges.experience_bridge import ExperienceFoundationBridge
            
            self.realm_bridges["experience_foundation"] = ExperienceFoundationBridge(
                di_container=self.di_container,
                public_works_foundation=self.public_works_foundation,
                curator_foundation=self.curator_foundation
            )
            await self.realm_bridges["experience_foundation"].initialize()
            self.logger.info("✅ Experience Foundation bridge created")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to create Experience Foundation bridge: {e}")
            self.realm_bridges["experience_foundation"] = None
    
    async def _register_bridge_routers(self):
        """Register all bridge routers with FastAPI Router Manager."""
        self.logger.info("🔧 Registering realm bridge routers...")
        
        # Register Smart City bridge router
        if self.realm_bridges.get("smart_city"):
            try:
                smart_city_router = await self.realm_bridges["smart_city"].get_router()
                await self.router_manager.register_realm_router(
                    realm="smart_city",
                    router=smart_city_router,
                    metadata={"realm": "smart_city", "version": "1.0"}
                )
                self.logger.info("✅ Smart City realm bridge router registered")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to register Smart City realm bridge router: {e}")
        
        # Register Journey bridge router
        if self.realm_bridges.get("journey"):
            try:
                journey_router = await self.realm_bridges["journey"].get_router()
                await self.router_manager.register_realm_router(
                    realm="journey",
                    router=journey_router,
                    metadata={"realm": "journey", "version": "1.0"}
                )
                self.logger.info("✅ Journey realm bridge router registered")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to register Journey realm bridge router: {e}")
        
        # Register Solution bridge router
        if self.realm_bridges.get("solution"):
            try:
                solution_router = await self.realm_bridges["solution"].get_router()
                await self.router_manager.register_realm_router(
                    realm="solution",
                    router=solution_router,
                    metadata={"realm": "solution", "version": "1.0"}
                )
                self.logger.info("✅ Solution realm bridge router registered")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to register Solution realm bridge router: {e}")
        
        # Register Business Enablement bridge router
        if self.realm_bridges.get("business_enablement"):
            try:
                be_router = await self.realm_bridges["business_enablement"].get_router()
                await self.router_manager.register_realm_router(
                    realm="business_enablement",
                    router=be_router,
                    metadata={"realm": "business_enablement", "version": "1.0"}
                )
                self.logger.info("✅ Business Enablement realm bridge router registered")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to register Business Enablement realm bridge router: {e}")
        
        # Register Experience Foundation bridge router
        if self.realm_bridges.get("experience_foundation"):
            try:
                experience_router = await self.realm_bridges["experience_foundation"].get_router()
                await self.router_manager.register_realm_router(
                    realm="experience_foundation",
                    router=experience_router,
                    metadata={"foundation": "experience", "version": "1.0"}
                )
                self.logger.info("✅ Experience Foundation bridge router registered")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to register Experience Foundation bridge router: {e}")
    
    async def shutdown(self):
        """Shutdown Realm Bridges SDK."""
        self.logger.info("🛑 Shutting down Realm Bridges SDK...")
        
        try:
            # Shutdown all realm bridges
            for realm, bridge in self.realm_bridges.items():
                if bridge and hasattr(bridge, "shutdown"):
                    try:
                        await bridge.shutdown()
                        self.logger.info(f"✅ {realm} realm bridge shutdown")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to shutdown {realm} realm bridge: {e}")
            
            # Clear bridges
            self.realm_bridges.clear()
            
            self.is_initialized = False
            self.logger.info("✅ Realm Bridges SDK shutdown complete")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown Realm Bridges SDK: {e}")
            raise

