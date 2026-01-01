#!/usr/bin/env python3
"""
Insights Manager Service - Initialization Module

Micro-module for Insights Manager service initialization with proper infrastructure connections.
"""

import logging
from typing import Any


class Initialization:
    """Initialization module for Insights Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def initialize_infrastructure_connections(self):
        """Initialize infrastructure connections via Platform Gateway and Smart City services."""
        try:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🔌 Connecting to infrastructure via Platform Gateway...")
            
            # Verify Platform Gateway is available
            if not hasattr(self.service, 'platform_gateway') or not self.service.platform_gateway:
                if hasattr(self.service, 'logger') and self.service.logger:
                    self.service.logger.warning("⚠️ Platform Gateway not available - operating with limited infrastructure access")
            else:
                if hasattr(self.service, 'logger') and self.service.logger:
                    self.service.logger.info("✅ Platform Gateway available for selective infrastructure access")
            
            # Discover Smart City services via Curator
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🔍 Discovering Smart City services via Curator...")
            
            # Librarian - Content metadata management
            self.service.librarian = await self.service.get_librarian_api()
            if not self.service.librarian and hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.warning("⚠️ Librarian service not available")
            
            # Data Steward - Data operations
            self.service.data_steward = await self.service.get_data_steward_api()
            if not self.service.data_steward and hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.warning("⚠️ Data Steward service not available")
            
            # Content Steward - Content operations
            self.service.content_steward = await self.service.get_content_steward_api()
            if not self.service.content_steward and hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.warning("⚠️ Content Steward service not available")
            
            self.service.is_infrastructure_connected = True
            
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("✅ Infrastructure connections established")
            
        except Exception as e:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.error(f"❌ Failed to connect to infrastructure: {str(e)}")
            raise e
    
    async def initialize_insights_manager_capabilities(self):
        """Initialize Insights Manager-specific capabilities."""
        try:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🎯 Initializing Insights Manager capabilities...")
            
            # Initialize insights orchestrator reference
            self.service.insights_orchestrator = None
            
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("✅ Insights Manager capabilities initialized")
            
        except Exception as e:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.error(f"❌ Failed to initialize capabilities: {str(e)}")
                import traceback
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")
            raise e
    
    async def discover_insights_realm_services(self):
        """Discover Insights realm services via Curator."""
        try:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🔍 Discovering Insights realm services via Curator...")
            
            # Discover Insights Orchestrator
            curator = self.service.get_curator()
            if curator:
                # Try to discover Insights Orchestrator
                insights_orchestrator = await curator.discover_service_by_name("InsightsOrchestrator")
                if insights_orchestrator:
                    self.service.insights_orchestrator = insights_orchestrator
                    if hasattr(self.service, 'logger') and self.service.logger:
                        self.service.logger.info("✅ Insights Orchestrator discovered via Curator")
                else:
                    if hasattr(self.service, 'logger') and self.service.logger:
                        self.service.logger.warning("⚠️ Insights Orchestrator not found in Curator - may need to be initialized")
            else:
                if hasattr(self.service, 'logger') and self.service.logger:
                    self.service.logger.warning("⚠️ Curator not available - cannot discover Insights realm services")
            
        except Exception as e:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.error(f"❌ Failed to discover Insights realm services: {str(e)}")
                import traceback
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")
            raise e

