#!/usr/bin/env python3
"""
Content Manager Service - Initialization Module

Micro-module for Content Manager service initialization with proper infrastructure connections.
"""

import logging
from typing import Any


class Initialization:
    """Initialization module for Content Manager service."""
    
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
            
            # Content Steward - Content operations
            self.service.data_steward = await self.service.get_data_steward_api()
            if not self.service.data_steward and hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.warning("⚠️ Content Steward service not available")
            
            # Data Steward - Data operations
            self.service.data_steward = await self.service.get_data_steward_api()
            if not self.service.data_steward and hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.warning("⚠️ Data Steward service not available")
            
            self.service.is_infrastructure_connected = True
            
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("✅ Infrastructure connections established")
            
        except Exception as e:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.error(f"❌ Failed to connect to infrastructure: {str(e)}")
            raise e
    
    async def initialize_content_manager_capabilities(self):
        """Initialize Content Manager-specific capabilities."""
        try:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🎯 Initializing Content Manager capabilities...")
            
            # Create and initialize ContentOrchestrator
            # ContentOrchestrator is a Content realm orchestrator that ContentManagerService manages
            try:
                from backend.content.orchestrators.content_orchestrator.content_analysis_orchestrator import ContentOrchestrator
                
                if hasattr(self.service, 'logger') and self.service.logger:
                    self.service.logger.info("🔧 Creating ContentOrchestrator...")
                
                self.service.content_orchestrator = ContentOrchestrator(
                    content_manager=self.service
                )
                
                # Initialize the orchestrator (registers with Curator)
                await self.service.content_orchestrator.initialize()
                
                if hasattr(self.service, 'logger') and self.service.logger:
                    self.service.logger.info("✅ ContentOrchestrator created and initialized")
            except Exception as orchestrator_error:
                if hasattr(self.service, 'logger') and self.service.logger:
                    self.service.logger.error(f"❌ Failed to create ContentOrchestrator: {str(orchestrator_error)}")
                    import traceback
                    self.service.logger.error(f"Traceback: {traceback.format_exc()}")
                # Set to None so discovery can try later
                self.service.content_orchestrator = None
            
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("✅ Content Manager capabilities initialized")
            
        except Exception as e:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.error(f"❌ Failed to initialize capabilities: {str(e)}")
                import traceback
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")
            raise e
    
    async def discover_content_realm_services(self):
        """Discover Content realm services via Curator."""
        try:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🔍 Discovering Content realm services via Curator...")
            
            # ContentOrchestrator should already be created in initialize_content_manager_capabilities
            # This method is for discovering other Content realm services if needed
            # If ContentOrchestrator wasn't created, try to discover it
            if not self.service.content_orchestrator:
                curator = self.service.get_curator()
                if curator:
                    # Try to discover Content Orchestrator (in case it was created elsewhere)
                    content_orchestrator = await curator.discover_service_by_name("ContentAnalysisOrchestratorService")
                    if content_orchestrator:
                        self.service.content_orchestrator = content_orchestrator
                        if hasattr(self.service, 'logger') and self.service.logger:
                            self.service.logger.info("✅ Content Orchestrator discovered via Curator")
                    else:
                        if hasattr(self.service, 'logger') and self.service.logger:
                            self.service.logger.warning("⚠️ Content Orchestrator not found in Curator - should have been created in initialize_content_manager_capabilities")
                else:
                    if hasattr(self.service, 'logger') and self.service.logger:
                        self.service.logger.warning("⚠️ Curator not available - cannot discover Content realm services")
            else:
                if hasattr(self.service, 'logger') and self.service.logger:
                    self.service.logger.info("✅ ContentOrchestrator already available (created during capability initialization)")
            
        except Exception as e:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.error(f"❌ Failed to discover Content realm services: {str(e)}")
                import traceback
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")
            raise e

