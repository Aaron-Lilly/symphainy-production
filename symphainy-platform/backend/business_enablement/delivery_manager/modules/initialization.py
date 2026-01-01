#!/usr/bin/env python3
"""
Delivery Manager Service - Initialization Module

Micro-module for Delivery Manager service initialization with proper infrastructure connections.
"""

from typing import Any


class Initialization:
    """Initialization module for Delivery Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def initialize_infrastructure_connections(self):
        """Initialize infrastructure connections via Platform Gateway and Smart City services."""
        try:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🔌 Connecting to infrastructure via Platform Gateway...")
            
            # Verify Platform Gateway is available (passed in __init__)
            if not hasattr(self.service, 'platform_gateway') or not self.service.platform_gateway:
                if hasattr(self.service, 'logger') and self.service.logger:
                    self.service.logger.warning("⚠️ Platform Gateway not available - operating with limited infrastructure access")
            else:
                if hasattr(self.service, 'logger') and self.service.logger:
                    self.service.logger.info("✅ Platform Gateway available for selective infrastructure access")
            
            # Delivery Manager uses Smart City services for platform capabilities
            # This maintains proper architectural separation: Smart City = HOW, Managers = WHAT
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("ℹ️ Session and state management will be handled via Smart City services")
            
            # Discover Smart City services via Curator for business-level operations
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🔍 Discovering Smart City services via Curator...")
            
            # Conductor - Workflow orchestration for pillar delivery
            self.service.conductor = await self.service.get_conductor_api()
            if not self.service.conductor and hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.warning("⚠️ Conductor service not available")
            
            # Post Office - Pillar coordination messaging
            self.service.post_office = await self.service.get_post_office_api()
            if not self.service.post_office and hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.warning("⚠️ Post Office service not available")
            
            self.service.is_infrastructure_connected = True
            
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("✅ Infrastructure connections established")
            
        except Exception as e:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.error(f"❌ Failed to connect to infrastructure: {str(e)}")
                import traceback
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")
            raise e
    
    async def initialize_delivery_manager_capabilities(self):
        """Initialize Delivery Manager-specific capabilities."""
        try:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🎯 Initializing Delivery Manager capabilities...")
            
            # Initialize business enablement pillars
            self.service.business_pillars = {
                "content_pillar": None,
                "insights_pillar": None,
                "operations_pillar": None,
                "business_outcomes_pillar": None,
                "context_pillar": None
            }
            
            # Initialize business orchestrator
            self.service.business_orchestrator = None
            
            # Initialize cross-realm coordination capabilities
            self.service.cross_realm_coordination_enabled = True
            
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("✅ Delivery Manager capabilities initialized")
            
        except Exception as e:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.error(f"❌ Failed to initialize capabilities: {str(e)}")
                import traceback
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")
            raise e


