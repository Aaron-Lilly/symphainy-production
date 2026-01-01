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
            
            # Journey Manager uses Smart City services for platform capabilities
            # This maintains proper architectural separation: Smart City = HOW, Managers = WHAT
            if self.service.logger:
                self.service.logger.info("ℹ️ Session and state management will be handled via Smart City services (Traffic Cop)")
            
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
    
    async def discover_journey_realm_services(self):
        """Discover Journey realm services via Curator."""
        try:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🔍 Discovering Journey realm services via Curator...")
            
            # Get Curator from DI Container
            curator = self.service.di_container.get_foundation_service("CuratorFoundationService")
            
            if not curator:
                if self.service.logger:
                    self.service.logger.warning("⚠️ Curator not available - Journey services will not be discovered")
                return
            
            discovered_services = {}
            service_names = [
                ("StructuredJourneyOrchestratorService", "structured_orchestrator"),
                ("SessionJourneyOrchestratorService", "session_orchestrator"),
                ("MVPJourneyOrchestratorService", "mvp_orchestrator"),
                ("JourneyAnalyticsService", "analytics"),
                ("JourneyMilestoneTrackerService", "milestone_tracker")
            ]
            
            for service_name, key in service_names:
                try:
                    service_info = await curator.discover_service_by_name(service_name)
                    if service_info:
                        discovered_services[key] = service_info
                        if self.service.logger:
                            self.service.logger.info(f"✅ Discovered {service_name}")
                    else:
                        if self.service.logger:
                            self.service.logger.warning(f"⚠️ {service_name} not found")
                except Exception as e:
                    if self.service.logger:
                        self.service.logger.warning(f"⚠️ Failed to discover {service_name}: {str(e)}")
            
            self.service.journey_services = discovered_services
            
            if hasattr(self.service, 'logger') and self.service.logger:
                discovered_count = len(discovered_services)
                self.service.logger.info(f"✅ Journey realm service discovery complete ({discovered_count}/5 services found)")
            
        except Exception as e:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.error(f"❌ Failed to discover Journey services: {str(e)}")
                import traceback
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't raise - discovery failure shouldn't break initialization


