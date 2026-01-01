#!/usr/bin/env python3
"""
Journey Manager Service - Initialization Module

Micro-module for Journey Manager service initialization with proper infrastructure connections.
"""

import logging
from typing import Any


class Initialization:
    """Initialization module for Journey Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def initialize_infrastructure_connections(self):
        """Initialize infrastructure connections using mixin methods."""
        try:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🔌 Connecting to Public Works infrastructure abstractions...")
            
            # Get Public Works Foundation from DI Container
            public_works_foundation = self.service.di_container.get_foundation_service("PublicWorksFoundationService")
            if not public_works_foundation:
                raise Exception("Public Works Foundation not available")
            
            # Journey Manager should use Smart City services (Traffic Cop) for session/state management
            # NOT direct infrastructure abstractions (architectural pattern to prevent spaghetti code)
            # Session and state management will be handled via Traffic Cop SOA API (discovered below)
            # We don't set session_abstraction or state_management_abstraction directly
            if self.service.logger:
                self.service.logger.info("ℹ️ Session and state management will be handled via Traffic Cop service")
            
            # Discover Smart City services via Curator for business-level operations
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🔍 Discovering Smart City services via Curator...")
            
            # Traffic Cop - Session routing, state sync
            self.service.traffic_cop = await self.service.get_traffic_cop_api()
            if not self.service.traffic_cop and hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.warning("⚠️ Traffic Cop service not available")
            
            # Conductor - Workflow orchestration
            self.service.conductor = await self.service.get_conductor_api()
            if not self.service.conductor and hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.warning("⚠️ Conductor service not available")
            
            # Post Office - Structured messaging
            self.service.post_office = await self.service.get_post_office_api()
            if not self.service.post_office and hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.warning("⚠️ Post Office service not available")
            
            self.service.is_infrastructure_connected = True
            
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("✅ Infrastructure connections established")
            
        except Exception as e:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.error(f"❌ Failed to connect to infrastructure: {str(e)}")
            raise e
    
    async def initialize_journey_manager_capabilities(self):
        """Initialize Journey Manager-specific capabilities."""
        try:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🎯 Initializing Journey Manager capabilities...")
            
            # Initialize journey-specific services
            self.service.journey_services = {
                "journey_orchestrator": None,
                "business_outcome_landing_page": None,
                "journey_persistence": None
            }
            
            # Initialize journey templates
            self.service.journey_templates = {}
            self.service.active_journeys = {}
            
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("✅ Journey Manager capabilities initialized")
            
        except Exception as e:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.error(f"❌ Failed to initialize capabilities: {str(e)}")
                import traceback
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")
            raise e


